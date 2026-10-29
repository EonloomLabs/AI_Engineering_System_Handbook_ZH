"""Locate safe prose in code without changing source, literals or layout.

Offsets use Python string indices, as extract.py and apply.py do. HTML entities
are decoded only for lexing; every visible character retains its raw span.
"""
import ast
import io
import re
import shlex
import tokenize
from html import unescape
from html.parser import HTMLParser

HAN = re.compile(r'[一-鿿]')
LINE_LABEL = re.compile(r'第([0-9]+)行')
ATTRIBUTE = re.compile(
    r'''([\w:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))''')
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr'}


def line_label_translation(source, lang):
    """Code-line label template; existing table entries may mean matrix rows.

    The caller retains existing translations and handles context overrides.
    """
    match = LINE_LABEL.fullmatch(unescape(source))
    if match is None:
        return None
    if lang == 'en':
        return 'Line ' + match.group(1)
    if lang == 'ja':
        return match.group(1) + '行目'
    return None


class _Text:
    def __init__(self):
        self.parts = []
        self.positions = []

    def add(self, text, positions):
        self.parts.append(text)
        self.positions.extend(positions)

    def value(self):
        return ''.join(self.parts)


class _Code(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=False)
        self.raw = raw
        self.starts = [0] + [m.end() for m in re.finditer('\n', raw)]
        self.stack = []
        self.outside = _Text()
        self.lines = []
        self.line = None
        self.skip_depth = None
        self.attributes = []
        self.languages = set()
        self.managed = False

    def source_offset(self):
        row, col = self.getpos()
        return self.starts[row - 1] + col

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        depth = len(self.stack)
        classes = attrs.get('class', '').split()
        self.managed |= 'data-i18n' in attrs
        if tag in ('pre', 'code'):
            self.languages.update(c[9:] for c in classes if c.startswith('language-'))
        if tag == 'span' and ('data-line' in attrs or
                              {'code-line', 'source-line'} & set(classes)):
            if self.line is not None:
                self.managed = True       # unsupported nested line wrappers
            self.line = (depth, 'source-line' in classes, _Text())
            self.lines.append(self.line)
        if tag == 'a' and 'source-number' in classes:
            self.skip_depth = depth + 1
        governed = {p.partition(':')[0].strip()
                    for p in attrs.get('data-i18n-attr', '').split(',')}
        if 'aria-label' not in governed:
            raw = self.get_starttag_text()
            for match in ATTRIBUTE.finditer(raw):
                if match.group(1).lower() != 'aria-label':
                    continue
                group = next(g for g in (2, 3, 4) if match.group(g) is not None)
                value = match.group(group)
                if LINE_LABEL.fullmatch(unescape(value)):
                    self.attributes.append((self.source_offset() + match.start(group),
                                            self.source_offset() + match.end(group),
                                            'attr:aria-label', value))
        if tag == 'br':
            self.add('\n', [None])
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        depth = len(self.stack) - 1
        if self.skip_depth == len(self.stack):
            self.skip_depth = None
        if self.line is not None and tag == 'span' and depth == self.line[0]:
            self.line = None
        if tag in self.stack:
            while self.stack.pop() != tag:
                pass

    def add(self, text, positions):
        if self.skip_depth is None:
            target = self.line[2] if self.line is not None else self.outside
            target.add(text, positions)

    def handle_data(self, data):
        start = self.source_offset()
        self.add(data, [(start + i, start + i + 1) for i in range(len(data))])

    def entity(self, prefix, name):
        start = self.source_offset()
        raw = prefix + name
        if self.raw[start + len(raw):start + len(raw) + 1] == ';':
            raw += ';'
        text = unescape(raw)
        self.add(text, [(start, start + len(raw))] * len(text))

    def handle_entityref(self, name):
        self.entity('&', name)

    def handle_charref(self, name):
        self.entity('&#', name)

    def visible(self):
        if not self.lines:
            return self.outside.value(), self.outside.positions
        if self.outside.value().strip():
            return '', []
        text, positions = [], []
        # Each wrapper is a source line. Ignore the HTML whitespace between
        # wrappers, so data-line pages do not gain duplicate physical newlines.
        for _, numbered, line in self.lines:
            value, mapping = line.value(), line.positions
            if numbered and value.startswith(' '):
                value, mapping = value[1:], mapping[1:]
            text.append(value + '\n')
            positions.extend(mapping + [None])
        return ''.join(text), positions


def _directory_comments(text):
    """Only trailing annotations in a complete one-column directory listing."""
    lines = text.splitlines(keepends=True)
    if len(lines) < 2 or not re.fullmatch(r'[\w.-]+/\s*', lines[0]):
        return None
    comments, offset = [], len(lines[0])
    for line in lines[1:]:
        match = re.fullmatch(r'[ \t]+[\w./-]+(?:[ \t]+(?P<c>#[^\r\n]*))?\s*', line)
        if match is None:
            return None
        if match.group('c'):
            comments.append((offset + match.start('c'), offset + match.end('c')))
        offset += len(line)
    return comments


def _shell_comments(text):
    """The book's cd/python command blocks; reject richer shell syntax whole."""
    comments, pending, offset = [], '', 0
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip(' \t')
        if not pending and stripped.startswith('#'):
            start = offset + len(line) - len(stripped)
            comments.append((start, offset + len(line.rstrip('\r\n'))))
        else:
            pending += line
            if pending.rstrip('\r\n').endswith('\\'):
                offset += len(line)
                continue
            try:
                words = shlex.split(pending)
            except ValueError:
                return []
            if words and (words[0] not in ('cd', 'python', 'python3') or
                          any(re.search(r'[;&|<>`]|\$\(', word) for word in words)):
                return []
            pending = ''
        offset += len(line)
    return [] if pending else comments


def _comments(text, languages):
    if languages - {'python', 'bash', 'sh', 'shell'}:
        return []
    if languages & {'bash', 'sh', 'shell'}:
        return _shell_comments(text)
    directory = _directory_comments(text)
    if directory is not None and not languages:
        return directory
    try:
        ast.parse(text)
    except (SyntaxError, ValueError):
        return [] if languages else _shell_comments(text)
    starts = [0] + [m.end() for m in re.finditer('\n', text)]
    return [(starts[t.start[0] - 1] + t.start[1],
             starts[t.end[0] - 1] + t.end[1])
            for t in tokenize.generate_tokens(io.StringIO(text).readline)
            if t.type == tokenize.COMMENT]


def extract_code_units(raw, base=0):
    """Return raw-span comment bodies and accessible line-number attributes."""
    code = _Code(raw)
    code.feed(raw)
    code.close()
    items = list(code.attributes)
    text, mapping = code.visible()
    if not code.managed and '#' in text:
        for start, end in _comments(text, code.languages):
            comment = text[start:end]
            # Encoding, shebang and tool directives can affect copied code.
            if re.match(r'#(?:!|.*coding[:=]|\s*(?:type:|noqa\b|fmt:|ruff:|pylint:))', comment):
                continue
            start += len(comment) - len(comment.lstrip('# \t'))
            end -= len(comment) - len(comment.rstrip())
            if start >= end or not HAN.search(text[start:end]):
                continue
            spans = mapping[start:end]
            if None in spans:
                continue
            left, right = spans[0][0], spans[-1][1]
            # A token crossing real markup or half of a multi-character entity
            # has no single editable raw span; leave it unchanged.
            if unescape(raw[left:right]) == text[start:end]:
                items.append((left, right, 'code-comment', raw[left:right]))
    return sorted((base + start, base + end, kind, value)
                  for start, end, kind, value in items)


if __name__ == '__main__':
    raise SystemExit('Import extract_code_units or line_label_translation; no files are written.')
