"""Translate visible JS literals through the book's one translation table.

The source scripts are read-only. ``collect`` records the bounded extraction in
runtime-registry.json; it never edits table.json. table.py may merge
source_counts(ROOT), then ``export`` prints the missing rows in batch.py's
id<TAB>text protocol. ``write --lang=en`` requires that exact current registry
and complete, validated table rows before touching en/assets/.

Template expressions, comments, executable code, model-token literals and HTML
machine fields are immutable. Template text is split at each ${...}, so a
translator cannot change or reorder an expression. The lexer is deliberately
local to these bounded browser scripts, not a general JavaScript compiler.
"""

import argparse
import hashlib
import html
import json
import os
import re
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FILES = (
    'assets/diagrams.js', 'assets/mechanisms.js', 'assets/model-player.js',
    'assets/visual-player.js', 'assets/concept-labs.js',
    'assets/reader-navigation.js', 'assets/app.js', 'assets/atelier.js',
    'assets/i18n.js',
)
BUNDLE = 'assets/i18n-data.js'
REGISTRY = 'i18n/runtime-registry.json'
TABLE = 'i18n/table.json'
VERSION = 1
CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff]')
# The HTML extractor uses this same set. The isolated full-width ! is absent
# deliberately: it is a model-vocabulary entry rather than UI punctuation.
MIXED_PUNCT = re.compile(r'[。；，、：？（）]')
MODEL_TOKENS = frozenset(('我', '爱', '学习', '你', '！'))
VISIBLE_ATTRIBUTES = frozenset(('aria-label', 'title', 'alt', 'placeholder'))
IDENTIFIER = re.compile(r'[A-Za-z_$][A-Za-z0-9_$]*')
NUMBER = re.compile(r'(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?')
ESCAPE = re.compile(r'\\(?:\r\n|[\s\S])')
TAG_START = re.compile(r'</?[A-Za-z][\w:-]*\b')
ATTRIBUTE = re.compile(r'(?P<name>[\w:-]+)\s*=\s*(?P<q>[\'"])(?P<value>.*?)(?P=q)', re.S)
TECH = re.compile(
    r'[A-Za-z_][A-Za-z_0-9]*(?:[./-][A-Za-z_0-9]+)*|'
    r'[−-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|'
    r':=|=>|[!<>+*/-]?={1,3}|[Σ≈√×≥≤∞\[\]]')
TECH_SYMBOL = re.compile(r'(?:[:!<>+*/-]?={1,3}|=>|[Σ≈√×≥≤∞\[\]])$')
# These source terms name concepts in the bounded scripts, rather than code
# variables. They may be lowercase or plural in English prose. This is only a
# classification of source text, never a translation or replacement catalogue.
# Unknown names, acronyms (RoPE/MiB/ID), and code-shaped names remain strict.
PROSE_CONCEPTS = frozenset(('Token', 'Embedding', 'Value', 'One-hot'))
CODE_NAME_CONTEXT = re.compile(
    r'(?:变量|参数|字段|函数|方法|属性|标识符|标识|类|键|'
    r'\bnew|\bclass|\bfunction|\bconst|\blet|\bvar)\s*$')
BUNDLE_ASSIGNMENT = re.compile(r'window\.I18N_STRINGS\s*=\s*')
WINDOW_ASSIGNMENT = re.compile(r'\bwindow\.[A-Za-z_$][\w$]*\s*=\s*(?=[{\[])')
HINT_KEY = 'search.pageHint'


class RuntimeStringError(ValueError):
    """A failed extraction or protection check; no output should be published."""


@dataclass(frozen=True)
class Literal:
    start: int
    end: int
    quote: str
    spans: tuple
    expressions: tuple = ()


class Lexer:
    """Locate string text while skipping comments, regexes and substitutions."""

    REGEX_PREFIX_WORDS = frozenset((
        'return', 'throw', 'case', 'delete', 'void', 'typeof', 'instanceof',
        'in', 'new', 'yield', 'await', 'else', 'do',
    ))

    def __init__(self, source):
        self.source = source
        self.literals = []
        self.opaque = []

    def quoted(self, start):
        s, q, i = self.source, self.source[start], start + 1
        while i < len(s):
            if s[i] == '\\':
                if i + 1 >= len(s):
                    break
                i += 3 if s.startswith('\r\n', i + 1) else 2
            elif s[i] == q:
                return Literal(start, i + 1, q, ((start + 1, i),))
            elif s[i] in '\r\n\u2028\u2029':
                raise RuntimeStringError('newline in quoted string at %d' % start)
            else:
                i += 1
        raise RuntimeStringError('unterminated quoted string at %d' % start)

    def template(self, start):
        s, i, text_start = self.source, start + 1, start + 1
        spans, expressions = [], []
        while i < len(s):
            if s[i] == '\\':
                i += 2
            elif s[i] == '`':
                spans.append((text_start, i))
                return Literal(start, i + 1, '`', tuple(spans), tuple(expressions))
            elif s.startswith('${', i):
                spans.append((text_start, i))
                end = self.code(i + 2, substitution=True, collect=False)
                expressions.append(s[i:end])
                i = text_start = end
            else:
                i += 1
        raise RuntimeStringError('unterminated template at %d' % start)

    def regex(self, start):
        s, i, in_class = self.source, start + 1, False
        while i < len(s):
            c = s[i]
            if c == '\\':
                i += 2
                continue
            if c in '\r\n\u2028\u2029':
                break
            if c == '[':
                in_class = True
            elif c == ']':
                in_class = False
            elif c == '/' and not in_class:
                i += 1
                while i < len(s) and s[i].isalpha():
                    i += 1
                return i
            i += 1
        raise RuntimeStringError('unterminated regex at %d' % start)

    def code(self, start=0, substitution=False, collect=True):
        s, i, braces, regex_allowed = self.source, start, 0, True
        while i < len(s):
            c = s[i]
            if c.isspace():
                i += 1
                continue
            if s.startswith('//', i):
                end = s.find('\n', i + 2)
                end = len(s) if end < 0 else end + 1
                self.opaque.append((i, end))
                i = end
                continue
            if s.startswith('/*', i):
                end = s.find('*/', i + 2)
                if end < 0:
                    raise RuntimeStringError('unterminated comment at %d' % i)
                self.opaque.append((i, end + 2))
                i = end + 2
                continue
            if c in '\'"`':
                literal = self.template(i) if c == '`' else self.quoted(i)
                if collect:
                    self.literals.append(literal)
                self.opaque.append((i, literal.end))
                i, regex_allowed = literal.end, False
                continue
            if c == '/':
                end = self.regex(i) if regex_allowed else i + (2 if s.startswith('/=', i) else 1)
                if regex_allowed:
                    self.opaque.append((i, end))
                i = end
                regex_allowed = not regex_allowed
                continue
            if c == '{':
                braces += 1
                regex_allowed = True
            elif c == '}':
                if not braces:
                    if substitution:
                        return i + 1
                    raise RuntimeStringError('unmatched closing brace at %d' % i)
                braces -= 1
                regex_allowed = False
            else:
                match = IDENTIFIER.match(s, i)
                if match:
                    regex_allowed = match.group() in self.REGEX_PREFIX_WORDS
                    i = match.end()
                    continue
                match = NUMBER.match(s, i)
                if match:
                    i, regex_allowed = match.end(), False
                    continue
                if s.startswith(('++', '--'), i):
                    i, regex_allowed = i + 2, False
                    continue
                regex_allowed = c not in ')] .'
            i += 1
        if substitution or braces:
            raise RuntimeStringError('unclosed substitution or brace at %d' % start)
        return i

    def scan(self):
        self.code()
        return self.literals


def _sha(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def _root(root):
    return (ROOT if root is None else Path(root)).resolve()


def _read(root, rel):
    # These names are code-owned constants, never CLI paths or registry paths.
    path = root / rel
    if path.is_symlink():
        raise RuntimeStringError('source is a symlink: %s' % rel)
    return path.read_text(encoding='utf-8')


def _tag_end(s, start):
    """Find a markup delimiter without treating a quoted > as its end."""
    quote, i = None, start + 1
    while i < len(s):
        if quote:
            if s[i] == quote:
                quote = None
        elif s[i] in '\'"':
            quote = s[i]
        elif s[i] == '>':
            return i + 1
        elif s[i] == '<':
            break
        i += 1
    raise RuntimeStringError('malformed HTML literal at %d' % start)


def _items_for_span(source, rel, literal, start, end):
    raw = source[start:end]
    if not (CJK.search(raw) or MIXED_PUNCT.search(raw)):
        return []
    items = []

    def add(a, b, kind, attr_quote=None):
        value = source[a:b]
        if not (CJK.search(value) or MIXED_PUNCT.search(value)) or value in MODEL_TOKENS:
            return
        if any(c in value for c in '\r\n\u2028\u2029'):
            raise RuntimeStringError('multi-line translation fragment in %s' % rel)
        item = dict(file=rel, start=a, end=b,
                    line=source.count('\n', 0, a) + 1, kind=kind,
                    quote=literal.quote, zh=value)
        if attr_quote:
            item['attribute_quote'] = attr_quote
        items.append(item)

    # All markup in the bounded scripts is in ordinary, self-contained
    # literals. A tag split by a substitution is rejected, rather than guessed.
    if TAG_START.search(raw):
        if literal.quote == '`' and literal.expressions:
            raise RuntimeStringError('HTML template with expressions needs explicit ownership: %s' % rel)
        i, text_start = start, start
        while i < end:
            if source[i] != '<' or not TAG_START.match(source, i):
                i += 1
                continue
            add(text_start, i, 'html-text')
            tag_end = _tag_end(source, i)
            if tag_end > end:
                raise RuntimeStringError('HTML tag crosses literal boundary in %s' % rel)
            tag = source[i:tag_end]
            for match in ATTRIBUTE.finditer(tag):
                if match.group('name').lower() in VISIBLE_ATTRIBUTES:
                    a, b = match.span('value')
                    add(i + a, i + b, 'html-attribute', match.group('q'))
            i = text_start = tag_end
        add(text_start, end, 'html-text')
    else:
        add(start, end, 'template-text' if literal.quote == '`' else 'text')
    return items


def _window_data_ranges(source, lexer):
    """Strict JSON assignments are data owners, not inline UI implementations."""
    decoder, ranges = json.JSONDecoder(), []
    for match in WINDOW_ASSIGNMENT.finditer(source):
        if any(a <= match.start() < b for a, b in lexer.opaque):
            continue
        try:
            value, size = decoder.raw_decode(source[match.end():])
        except json.JSONDecodeError:
            continue  # Executable object literals stay in the UI scanner.
        finish = match.end() + size
        tail = re.match(r'\s*(?:;|$)', source[finish:])
        if isinstance(value, (dict, list)) and tail:
            ranges.append((match.start(), finish + tail.end()))
    return ranges


def extract_script(source, rel, *, skip_window_data=False):
    """Return visible spans; offsets are Python character offsets, not bytes."""
    lexer, items = Lexer(source), []
    literals = lexer.scan()
    ranges = _window_data_ranges(source, lexer) if skip_window_data else ()
    for literal in literals:
        if any(a <= literal.start and literal.end <= b for a, b in ranges):
            continue
        for start, end in literal.spans:
            items.extend(_items_for_span(source, rel, literal, start, end))
    return sorted(items, key=lambda it: it['start'])


def scan_js(source, rel='<inline>'):
    """Pure inline-JS API: visible spans, excluding window.* strict JSON data.

    Each item has file/start/end/line/kind/quote/zh. Offsets index the supplied
    Python string. No registry or table access and no writes occur. Non-JSON
    object literals are executable source and remain eligible for scanning.
    """
    return extract_script(source, rel, skip_window_data=True)


def localize_js(source, translations, rel='<inline>'):
    """Pure inline-JS API; translations is a {source: target-string} mapping.

    Missing or invalid rows raise RuntimeStringError. Callers retain ownership
    of collection, table lookup, HTML escaping and output publication. Existing
    window.* JSON data blocks, comments, code and expressions remain untouched.
    Recognized model/edition controllers also receive their bounded runtime
    adaptations, for parity with the separate asset outputs.
    """
    items = scan_js(source, rel)
    missing = [item['zh'] for item in items if not translations.get(item['zh'])]
    if missing:
        raise RuntimeStringError('missing inline-JS translation: %s' % missing[0][:70])
    return adapt_edition_notice(adapt_model_player(render_script(source, items, translations)))


def _bundle(source):
    match = BUNDLE_ASSIGNMENT.search(source)
    if not match:
        raise RuntimeStringError('I18N_STRINGS assignment not found')
    try:
        document, size = json.JSONDecoder().raw_decode(source[match.end():])
    except json.JSONDecodeError as exc:
        raise RuntimeStringError('invalid interface bundle JSON') from exc
    tail = source[match.end() + size:]
    if not re.fullmatch(r';\s*', tail):
        raise RuntimeStringError('unexpected content after I18N_STRINGS')
    if not isinstance(document, dict):
        raise RuntimeStringError('I18N_STRINGS must be an object')
    return document, match.end(), match.end() + size


def inventory(root=None):
    """Deterministic source-bound registry; does not read or write the table."""
    root = _root(root)
    files, items = [], []
    for rel in FILES:
        source = _read(root, rel)
        own = extract_script(source, rel)
        files.append(dict(path=rel, sha256=_sha(source), items=len(own)))
        items.extend(own)
    source = _read(root, BUNDLE)
    bundle, _, _ = _bundle(source)
    try:
        hint = bundle['zh-CN'][HINT_KEY]
        bundle['en'][HINT_KEY]
    except (KeyError, TypeError) as exc:
        raise RuntimeStringError('page-search hint missing from interface bundle') from exc
    if not isinstance(hint, str) or not CJK.search(hint):
        raise RuntimeStringError('Chinese page-search hint is not a source string')
    files.append(dict(path=BUNDLE, sha256=_sha(source), items=1))
    items.append(dict(file=BUNDLE, line=source.count('\n', 0, source.index(HINT_KEY)) + 1,
                      kind='edition-hint', key=HINT_KEY, zh=hint))
    return dict(version=VERSION, files=files, items=items)


def source_counts(root=None):
    """Current runtime occurrences, suitable for table.py's source merging."""
    seen = {}
    for item in inventory(root)['items']:
        row = seen.setdefault(item['zh'], {'n': 0, 'pages': set()})
        row['n'] += 1
        row['pages'].add(item['file'])
    return seen


def _safe_output(root, relative):
    path = root / relative
    # Inputs are a code-owned allowlist; output ancestors must not redirect it.
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink():
            raise RuntimeStringError('output path is a symlink: %s' % relative)
    return path


def _atomic_text(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    fd, temporary = tempfile.mkstemp(prefix='.runtime-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as handle:
            handle.write(payload)
            handle.flush()
            os.fchmod(handle.fileno(), mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def collect(root=None):
    """Write only our registry; table identity remains owned by table.py."""
    root = _root(root)
    document = inventory(root)
    _atomic_text(_safe_output(root, REGISTRY),
                 json.dumps(document, ensure_ascii=False, indent=2) + '\n')
    counts = source_counts(root)
    print('运行时可见文本 %d 处 / %d 条 -> %s（未改翻译表）' %
          (len(document['items']), len(counts), REGISTRY))
    return 0


def _current_registry(root):
    path = root / REGISTRY
    if not path.is_file() or path.is_symlink():
        raise RuntimeStringError('run runtime_strings.py collect first')
    document = json.loads(path.read_text(encoding='utf-8'))
    current = inventory(root)
    if document != current:
        raise RuntimeStringError('runtime registry is stale; re-run collect and table.py build')
    return document


def _table(root):
    table = json.loads((root / TABLE).read_text(encoding='utf-8')).get('s')
    if not isinstance(table, dict):
        raise RuntimeStringError('invalid translation table')
    return table


def export(lang='en', root=None):
    """Print a batch source file; redirect stdout to a new runtime-*.src.txt."""
    if lang != 'en':
        raise RuntimeStringError('this bounded runtime adaptation supports --lang=en')
    root = _root(root)
    document, table = _current_registry(root), _table(root)
    seen, groups = set(), []
    for item in document['items']:
        source = item['zh']
        if source in seen or table.get(source, {}).get(lang):
            continue
        row = table.get(source)
        if not isinstance(row, dict) or not isinstance(row.get('id'), int):
            raise RuntimeStringError('source missing a permanent table id; run table.py build')
        seen.add(source)
        groups.append((item, row['id']))
    print('# Runtime visible strings — target language: en')
    print('# Keep numeric values, technical identifiers, symbols and literal \\n escapes unchanged and in order.')
    print('# Template expressions are absent: fragments stay on their original side of every substitution.')
    print('# The page-search hint must use English-index examples: tensor, Lesson 39, Q001.')
    print('# Source edge spaces are literal. Use ␣ in a translation only to add/change an edge space.')
    for item, identity in groups:
        print('# source: %s:%d (%s)' % (item['file'], item['line'], item['kind']))
        # pair() uses the exact handed-out source as its table key; adding GAP
        # markers here would create a different key. Only the target may use
        # that convention. Literal backslash-n remains one physical line.
        print('%d\t%s' % (identity, item['zh']))
    return 0


def _escapes(value):
    return [match.group() for match in ESCAPE.finditer(value)]


def _prose_concept(match, text):
    """A known prose name loses its exemption in an actual code context."""
    if match.group() not in PROSE_CONCEPTS:
        return False
    before, after = text[:match.start()], text[match.end():]
    if (CODE_NAME_CONTEXT.search(before) or before.rstrip().endswith('`')
            or after.lstrip().startswith('`')
            or re.match(r'\s*(?:[.(\[]|[:!<>+*/-]?=|=>)', after)):
        return False
    return True


def validate_translation(source, value):
    """Reject changed numbers/code/control escapes before JS or HTML encoding."""
    if not isinstance(value, str) or not value.strip():
        raise RuntimeStringError('empty or non-string translation: %s' % source[:70])
    if any(c in value for c in '\r\n\u2028\u2029'):
        raise RuntimeStringError('translation introduces a physical newline: %s' % source[:70])
    if any(ord(c) < 32 or 0xd800 <= ord(c) <= 0xdfff for c in value):
        raise RuntimeStringError('translation introduces a raw control or surrogate: %s' % source[:70])
    if CJK.search(value):
        raise RuntimeStringError('untranslated Chinese in runtime text: %s' % source[:70])
    if MIXED_PUNCT.search(value):
        raise RuntimeStringError('untranslated full-width punctuation: %s' % source[:70])
    if _escapes(source) != _escapes(value):
        raise RuntimeStringError('changed JavaScript control escapes: %s' % source[:70])
    unescaped_source = ESCAPE.sub('', source)
    protected = [match.group() for match in TECH.finditer(unescaped_source)
                 if not _prose_concept(match, unescaped_source)]
    # Only source tokens are protected; English prose introduces other words.
    # Count/order must still match, including short variables such as a or W.
    tokens = TECH.findall(ESCAPE.sub('', value))
    source_set = set(protected)
    actual = [token for token in tokens if token in source_set or token[:1].isdigit()
              or (token[:1] in '−-' and token[1:2].isdigit())
              or TECH_SYMBOL.fullmatch(token)]
    if protected != actual:
        raise RuntimeStringError('changed numeric/code tokens %r -> %r: %s' %
                                 (protected, actual, source[:70]))
    return value


def _encode(value, item):
    if item['kind'] == 'html-text':
        value = html.escape(value, quote=False)
    elif item['kind'] == 'html-attribute':
        value = html.escape(value, quote=True)
    quote = item['quote']
    parts, last = [], 0

    def text(s):
        s = s.replace('\\', '\\\\').replace(quote, '\\' + quote)
        return s.replace('${', '\\${') if quote == '`' else s

    for match in ESCAPE.finditer(value):
        parts.append(text(value[last:match.start()]))
        parts.append(match.group())  # exact source control escape, already validated
        last = match.end()
    parts.append(text(value[last:]))
    return ''.join(parts)


def code_signature(source):
    """Executable bytes, comments, regexes and template expressions, in order."""
    parts, last = [], 0
    for literal in Lexer(source).scan():
        parts.append(source[last:literal.start])
        parts.append(literal.quote + '<text>')
        for expression in literal.expressions:
            parts.append(expression + '<text>')
        parts.append(literal.quote)
        last = literal.end
    parts.append(source[last:])
    return ''.join(parts)


def render_script(source, items, translations):
    """Prepare one script and prove its executable/template skeleton unchanged."""
    parts, last = [], 0
    for item in sorted(items, key=lambda it: it['start']):
        start, end = item['start'], item['end']
        if start < last or source[start:end] != item['zh']:
            raise RuntimeStringError('overlapping or stale runtime text offsets')
        value = validate_translation(item['zh'], translations[item['zh']])
        # Chinese labels need no separator before/after an interpolation;
        # English labels do. This is spacing, as with apply.py's HTML seams,
        # rather than a second translation of shared terms such as Feature.
        if item['kind'] == 'template-text':
            if (source[start - 1:start] == '}' and CJK.match(item['zh'])
                    and re.match(r'[A-Za-z0-9]', value)):
                value = ' ' + value
            if (source[end:end + 2] == '${' and CJK.search(item['zh'][-1:])
                    and re.search(r'[A-Za-z0-9]$', value)):
                value += ' '
        parts.extend((source[last:start], _encode(value, item)))
        last = end
    parts.append(source[last:])
    output = ''.join(parts)
    if code_signature(source) != code_signature(output):
        raise RuntimeStringError('translation changed executable code or a template expression')
    return output


def adapt_model_player(source):
    """Adapt the recognized viewer's group keys and English row-label gutter.

    HTML data-allowed-groups keeps the original Chinese keys. Translated frame
    groups must also match each same-group frame's immutable sourceGroup; the
    existing g.includes(r) path supports original/legacy datasets unchanged.

    Measured 2026-10-29 on the current en/assets/model-data.js (42 frames),
    Pillow 12.3.0, macOS SFNS regular (width 100, optical size 17, weight 400),
    measured at 16x then divided for fractional 15px advances: the longest row
    is 175.125px (The same parameter cell); Candidate probabilities is 163.938px.
    The original x=10..150 gutter is 140px. x=190 leaves 180px, including 4.875px
    after the widest label. Columns (max 69.438px at 14px), actual formatted
    numeric/boolean cells (max 85.688px at 13px), and Arial fallbacks all fit the
    existing 88px cells, so neither column spacing nor cell width changes.
    No dataset, numerical calculation, event handler or original file changes.

    Exact replacements are idempotent and reject a changed selector/layout.
    Non-model inline scripts pass through unchanged.
    """
    if 'const frames=window.MODEL_FRAMES||[];' not in source:
        return source
    if "host.querySelector('.mc-frame-figure')" not in source:
        raise RuntimeStringError('unrecognized model-player layout owner')
    selector = 'available.filter(g=>requested.some(r=>g.includes(r)))'
    source_selector = (
        "available.filter(g=>requested.some(r=>g.includes(r)||frames.some("
        "f=>f.group===g&&typeof f.sourceGroup==='string'&&f.sourceGroup.includes(r))))"
    )
    changes = (
        (selector, source_selector, 1,
         'model-player group selector changed; update the sourceGroup adapter before writing'),
        ('Math.max(660,155+rows[0].length*94)', 'Math.max(660,195+rows[0].length*94)', 1,
         'model-player layout changed; remeasure labels before writing'),
        ('x:150+j*94', 'x:190+j*94', 3,
         'model-player layout changed; remeasure labels before writing'),
    )
    for old, new, count, error in changes:
        if source.count(old) == 0 and source.count(new) == count:
            continue  # Also supports upgrading an output with only the old gutter adapter.
        if source.count(old) != count or new in source:
            raise RuntimeStringError(error)
        source = source.replace(old, new)
    return source


def adapt_edition_notice(source, *, require_owner=False):
    """Use this page's translated scope for an incomplete interface language.

    Only the current localisation controller owns this adaptation. Other
    scripts, including literals/comments quoting its export, pass through.
    A recognized controller with changed guards or notice assignment is refused.
    require_owner binds the explicit assets/i18n.js input; pure inline callers
    can also encounter historical controllers owned by the complete builder.
    Page meta content is already translated through table.json; no language or
    body-language claim is added here. Complete-edition hiding and navigation
    remain the original code.
    """
    banner = '/* Localisation. No network: the catalogue ships as i18n-data.js so this works'
    export = 'window.I18N={t,apply,twin,get lang(){return current}'
    has_banner = source.lstrip().startswith(banner)
    assignment = re.compile(r'\bwindow\.I18N\s*=')
    if not assignment.search(source):
        if require_owner or has_banner:
            raise RuntimeStringError('edition-notice controller export missing; refusing to write')
        return source
    lexer = Lexer(source)
    lexer.scan()
    exports = [match for match in assignment.finditer(source)
               if not any(a <= match.start() < b for a, b in lexer.opaque)]
    if not exports:
        if require_owner or has_banner:
            raise RuntimeStringError('edition-notice controller export is not executable; refusing to write')
        return source
    has_current_export = any(source.startswith(export, match.start()) for match in exports)
    if not has_banner and not has_current_export:
        if require_owner:
            raise RuntimeStringError('unrecognized edition-notice controller; refusing to write')
        return source
    notice, switcher = 'function notice(){', 'function switcher(){'
    if (len(exports) != 1 or not source.lstrip().startswith(banner)
            or source.count(export) != 1 or source.count(notice) != 1
            or source.count(switcher) != 1):
        raise RuntimeStringError('edition-notice controller changed; update its exact adapter before writing')
    old = "el.textContent=t('lang.bodyNotice','');"
    new = ("el.textContent=(document.querySelector('meta[name=\"i18n-scope\"]')?.content||'').trim()"
           "||t('lang.bodyNotice','');")
    if source.count(old) == 0 and source.count(new) == 1:
        selected = new
    elif source.count(old) == 1 and source.count(new) == 0:
        selected = old
    else:
        raise RuntimeStringError('edition-notice assignment changed or duplicated; refusing to write')
    if not source.index(notice) < source.index(selected) < source.index(switcher):
        raise RuntimeStringError('edition-notice assignment moved outside its owner')
    return source.replace(old, new, 1) if selected == old else source


def render_bundle(source, translated_hint):
    """Replace one en JSON string; every other bundle byte remains untouched."""
    document, begin, end = _bundle(source)
    original = document['zh-CN'][HINT_KEY]
    validate_translation(original, translated_hint)
    if not all(example in translated_hint for example in ('tensor', 'Lesson 39', 'Q001')):
        raise RuntimeStringError('English page-search hint needs tensor, Lesson 39 and Q001')
    # Locate the selected object's JSON tokens using a recursive decoder. This
    # retains zh-CN, all other locales and I18N_META byte-for-byte.
    decoder = json.JSONDecoder()
    objects = []

    def object_spans(position, path=()):
        if source[position] != '{':
            raise RuntimeStringError('expected bundle object')
        position += 1
        while True:
            while source[position].isspace():
                position += 1
            if source[position] == '}':
                return position + 1
            key, size = decoder.raw_decode(source[position:])
            position += size
            while source[position].isspace():
                position += 1
            if not isinstance(key, str) or source[position] != ':':
                raise RuntimeStringError('invalid interface object entry')
            position += 1
            while source[position].isspace():
                position += 1
            value_start = position
            value, size = decoder.raw_decode(source[position:])
            if path + (key,) == ('en', HINT_KEY):
                objects.append((value_start, value_start + size))
            if isinstance(value, dict):
                object_spans(position, path + (key,))
            position += size
            while source[position].isspace():
                position += 1
            if source[position] == '}':
                return position + 1
            if source[position] != ',':
                raise RuntimeStringError('invalid interface object delimiter')
            position += 1

    if object_spans(begin) != end or len(objects) != 1:
        raise RuntimeStringError('page-search hint JSON location is ambiguous')
    start, finish = objects[0]
    output = source[:start] + json.dumps(translated_hint, ensure_ascii=False) + source[finish:]
    actual, _, _ = _bundle(output)
    expected = document.copy()
    expected['en'] = dict(document['en'], **{HINT_KEY: translated_hint})
    if actual != expected:
        raise RuntimeStringError('interface bundle changed outside the English hint')
    return output


def prepare(lang='en', root=None):
    """Validate every row and return outputs in memory; no filesystem writes."""
    if lang != 'en':
        raise RuntimeStringError('this bounded runtime adaptation supports --lang=en')
    root = _root(root)
    document, table = _current_registry(root), _table(root)
    missing = [source for source in dict.fromkeys(it['zh'] for it in document['items'])
               if not isinstance(table.get(source), dict) or not table[source].get(lang)]
    if missing:
        raise RuntimeStringError('缺运行时译文 %d 条，例: %s' % (len(missing), missing[0][:70]))
    translations = {item['zh']: table[item['zh']][lang] for item in document['items']}
    prepared = {}
    for rel in FILES:
        own = [item for item in document['items'] if item['file'] == rel]
        output = render_script(_read(root, rel), own, translations)
        if rel == 'assets/model-player.js':
            output = adapt_model_player(output)
        elif rel == 'assets/i18n.js':
            output = adapt_edition_notice(output, require_owner=True)
        prepared[lang + '/' + rel] = output
    hint = next(item for item in document['items'] if item['kind'] == 'edition-hint')
    prepared[lang + '/' + BUNDLE] = render_bundle(_read(root, BUNDLE), translations[hint['zh']])
    return prepared


def write(lang='en', root=None):
    """Publish only fully prepared outputs, with per-file atomic replacement.

    A missing/invalid row cannot create a directory or alter any output. Main
    serializes writers. An I/O commit failure restores already replaced files
    from memory where possible and reports any recovery failure; this does not
    promise a multi-file atomic view or power-loss durability.
    """
    root = _root(root)
    prepared = prepare(lang, root)
    paths = {rel: _safe_output(root, rel) for rel in prepared}
    previous = {rel: path.read_text(encoding='utf-8') if path.exists() else None
                for rel, path in paths.items()}
    committed = []
    try:
        for rel, payload in prepared.items():
            _atomic_text(paths[rel], payload)
            committed.append(rel)
    except OSError as exc:
        failures = []
        for rel in reversed(committed):
            try:
                if previous[rel] is None:
                    paths[rel].unlink()
                else:
                    _atomic_text(paths[rel], previous[rel])
            except OSError as recovery:
                failures.append('%s: %s' % (rel, recovery))
        if failures:
            raise RuntimeStringError('commit failed: %s; recovery failed: %s' %
                                     (exc, '; '.join(failures))) from exc
        raise
    print('%s/assets 运行时脚本已写出（%d 个文件，翻译表只读）' % (lang, len(prepared)))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('collect', 'export', 'write'))
    parser.add_argument('--lang', default='en')
    args = parser.parse_args(argv)
    try:
        if args.command == 'collect':
            return collect()
        return {'export': export, 'write': write}[args.command](args.lang)
    except (RuntimeStringError, OSError, json.JSONDecodeError) as exc:
        print('runtime_strings: %s' % exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
