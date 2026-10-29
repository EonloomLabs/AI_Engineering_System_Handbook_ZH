"""Source-bound translation collection for the continuous edition's shell.

Only complete.html outside standalone sections and visible inline-JS literals
are collected. Page articles and window.* JSON datasets retain their own
owners. collect never edits table.json; Main serializes table/build writers.

Run: python3 i18n/complete_strings.py collect
     python3 i18n/complete_strings.py export --lang=en > /tmp/complete.src.txt
"""
import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

import extract
import runtime_strings
import units

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = 'i18n/complete-registry.json'
SOURCE = 'complete.html'
VERSION = 1
CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff]')


class CompleteError(ValueError):
    """A source, translation or offline-output contract failed."""


class CompleteIndex(HTMLParser):
    """Locate complete sections and raw script/style spans without reserializing."""
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.lines = [0] + [m.end() for m in re.finditer('\n', source)]
        self.sections, self.scripts, self.styles = [], [], []
        self._sections, self._raw = [], None
        self.feed(source)
        self.close()
        if self._sections or self._raw:
            raise CompleteError('unclosed section/script/style in complete.html')

    def position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        at = self.position()
        attrs = dict(attrs)
        if tag == 'section':
            self._sections.append(dict(start=at, open_end=at + len(self.get_starttag_text()),
                                       attrs=attrs))
        elif tag in ('script', 'style'):
            if self._raw:
                raise CompleteError('nested script/style')
            self._raw = dict(tag=tag, start=at,
                             open_end=at + len(self.get_starttag_text()), attrs=attrs)

    def handle_endtag(self, tag):
        at = self.position()
        end = self.source.index('>', at) + 1
        if tag == 'section':
            if not self._sections:
                raise CompleteError('unmatched section close')
            item = self._sections.pop()
            item.update(close_start=at, end=end)
            if 'standalone-section' in item['attrs'].get('class', '').split():
                self.sections.append(item)
        elif tag in ('script', 'style') and self._raw:
            item, self._raw = self._raw, None
            item.update(close_start=at, end=end)
            (self.scripts if tag == 'script' else self.styles).append(item)


def sha(source):
    return hashlib.sha256(source.encode('utf-8')).hexdigest()


def atomic_text(path, payload):
    """Same-directory atomic visibility, without a power-loss durability claim."""
    path = Path(path)
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise CompleteError('output path contains a symlink: %s' % path)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    descriptor, temporary = tempfile.mkstemp(prefix='.complete-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8', newline='') as handle:
            handle.write(payload)
            handle.flush()
            os.fchmod(handle.fileno(), mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def inventory(root=None):
    root = Path(root or ROOT).resolve()
    source = (root / SOURCE).read_text(encoding='utf-8')
    index = CompleteIndex(source)
    # Keep character offsets stable while excluding the entire 250-page body,
    # resources and supplementary articles from duplicate translation.
    masked, last = [], 0
    for section in sorted(index.sections, key=lambda item: item['start']):
        masked.extend((source[last:section['start']], ' ' * (section['end'] - section['start'])))
        last = section['end']
    masked.append(source[last:])
    shell = ''.join(masked)
    runs = [dict(start=a, end=b, kind=kind, zh=text)
            for a, b, kind, text in extract.extract(shell)]
    # Adjacent navigation links are separate labels, even though <a> is an
    # inline tag. Merging the entire rail would duplicate 250 page titles in
    # one new translation instead of reusing the table's existing labels.
    items, group = [], []
    for run in runs:
        gap = shell[group[-1]['end']:run['start']] if group else ''
        if group and re.search(r'</a>\s*<a\b', gap, re.I):
            items.extend(units.merge(shell, group))
            group = []
        group.append(run)
    items.extend(units.merge(shell, group))
    # The resource payloads stay source data. Their shared heading and download
    # labels are interface prose, and must pass through the same table too.
    resource = next((section for section in index.sections
                     if section['attrs'].get('id') == 'embedded-resources'), None)
    if resource:
        body = source[resource['open_end']:resource['close_start']]
        for match in re.finditer(r'<h1\b[^>]*>(?P<title>[^<]+)</h1>|'
                                 r'<a\b[^>]*\bdownload="[^"]*"[^>]*>(?P<label>[^<]+)</a>', body):
            group_name = 'title' if match.group('title') is not None else 'label'
            start = resource['open_end'] + match.start(group_name)
            text = match.group(group_name)
            if CJK.search(text):
                items.append(dict(start=start, end=start + len(text), kind='text', zh=text))
    for item in items:
        item.update(file=SOURCE, line=source.count('\n', 0, item['start']) + 1,
                    owner='shell')
    for number, script in enumerate(index.scripts):
        text = source[script['open_end']:script['close_start']]
        for found in runtime_strings.scan_js(text, SOURCE + '#script-%d' % number):
            item = dict(found)
            item['start'] += script['open_end']
            item['end'] += script['open_end']
            item.update(file=SOURCE, line=source.count('\n', 0, item['start']) + 1,
                        owner='script', script=number)
            items.append(item)
    items.sort(key=lambda item: item['start'])
    for item in items:
        if source[item['start']:item['end']] != item['zh']:
            raise CompleteError('source offset mismatch')
    return dict(version=VERSION, file=SOURCE, sha256=sha(source), items=items)


def current_registry(root=None):
    root = Path(root or ROOT).resolve()
    path = root / REGISTRY
    if not path.is_file():
        raise CompleteError('run complete_strings.py collect first')
    document = json.loads(path.read_text(encoding='utf-8'))
    current = inventory(root)
    if document != current:
        raise CompleteError('complete registry is stale; collect and reconcile table first')
    return document


def source_counts(root=None):
    seen = {}
    for item in inventory(root)['items']:
        row = seen.setdefault(item['zh'], {'n': 0, 'pages': set()})
        row['n'] += 1
        row['pages'].add(SOURCE)
    return seen


def translations(root=None, lang='en'):
    if lang != 'en':
        raise CompleteError('the bounded complete builder currently supports --lang=en')
    root = Path(root or ROOT).resolve()
    registry = current_registry(root)
    table = json.loads((root / 'i18n/table.json').read_text(encoding='utf-8'))['s']
    missing = [text for text in dict.fromkeys(it['zh'] for it in registry['items'])
               if not table.get(text, {}).get(lang)]
    if missing:
        raise CompleteError('missing complete translations: %d; example: %s' %
                            (len(missing), missing[0][:80]))
    return registry, {it['zh']: table[it['zh']][lang] for it in registry['items']}


def localize_shell(source, registry, mapping):
    """Translate only recorded shell offsets; JS has its own protected renderer."""
    if sha(source) != registry.get('sha256'):
        raise CompleteError('shell source offset drift')
    changes = []
    for item in registry['items']:
        if item['owner'] != 'shell':
            continue
        value = mapping.get(item['zh'])
        if not isinstance(value, str) or not value.strip() or CJK.search(value):
            raise CompleteError('invalid complete shell translation: %s' % item['zh'][:70])
        if sorted(units.TAG.findall(value)) != sorted(units.TAG.findall(item['zh'])):
            raise CompleteError('changed inline markup in complete shell translation')
        if item['kind'].startswith('attr:'):
            value = value.replace('"', '&quot;')
        changes.append((item['start'], item['end'], value))
    parts, last = [], 0
    for start, end, value in changes:
        if start < last:
            raise CompleteError('overlapping shell source offsets')
        parts.extend((source[last:start], value))
        last = end
    parts.append(source[last:])
    return ''.join(parts)


def export(lang='en', root=None):
    root = Path(root or ROOT).resolve()
    registry = current_registry(root)
    table = json.loads((root / 'i18n/table.json').read_text(encoding='utf-8'))['s']
    pending = []
    for item in registry['items']:
        if item['zh'] in {it['zh'] for it, _ in pending}:
            continue
        row = table.get(item['zh'])
        if not row or row.get('id') is None:
            raise CompleteError('run i18n/table.py build before export')
        if not row.get(lang):
            pending.append((item, row['id']))
    print('# Complete edition shell and inline UI — %d strings — target language: %s' %
          (len(pending), lang))
    print('# Keep leading id<TAB>, inline tags, numbers, code, and literal edge spaces.')
    print('# Template expressions are excluded. Keep every fragment on its current side.')
    print('# Use literal backslash-n for JS escapes; do not introduce physical newlines.')
    for item, identity in pending:
        print('# source: %s:%d (%s/%s)' %
              (SOURCE, item['line'], item['owner'], item['kind']))
        print('%d\t%s' % (identity, item['zh']))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('collect', 'export', 'check'))
    parser.add_argument('--lang', default='en')
    args = parser.parse_args(argv)
    try:
        if args.command == 'collect':
            document = inventory()
            atomic_text(ROOT / REGISTRY, json.dumps(document, ensure_ascii=False, indent=2) + '\n')
            print('complete shell: %d occurrences / %d distinct strings' %
                  (len(document['items']), len({it['zh'] for it in document['items']})))
        elif args.command == 'export':
            export(args.lang)
        else:
            document, _ = translations(lang=args.lang)
            print('complete registry and translations current: %d occurrences' % len(document['items']))
        return 0
    except (CompleteError, runtime_strings.RuntimeStringError, OSError, ValueError) as exc:
        print('complete strings: %s' % exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
