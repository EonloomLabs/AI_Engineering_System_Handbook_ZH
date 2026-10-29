"""Source-bound, offline English adaptation of every published content SVG.

collect writes only figure-registry.json. table.py owns permanent IDs and
translations. export prints the standard id<TAB>source protocol. write reads
that one table and validates every input and output before publishing English
HTML, the SVG fields in visual-data.js and the referenced download mirrors.

No source generator is imported, no experiment is run, and no original input
is written. The current released nodes are authoritative for colors, frame
highlights, matrix values and animation identity. figure_layout.py owns local
word wrapping and geometry reflow; native AP tables own their equivalent SVG.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
from urllib.parse import unquote, urlsplit

try:
    from . import figure_layout as layout
except ImportError:
    import figure_layout as layout

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = 'i18n/figure-registry.json'
TABLE = 'i18n/table.json'
DATA = 'assets/visual-data.js'
VERSION = 1
SVG = re.compile(r'<svg\b[^>]*>.*?</svg\s*>', re.I | re.S)
FIGURE = re.compile(r'<figure\b[^>]*>.*?</figure\s*>', re.I | re.S)
HREF = re.compile(r'\bhref\s*=\s*([\'"])(.*?)\1', re.I | re.S)
JS_ASSIGNMENT = re.compile(r'\A\s*window\.(\w+)\s*=\s*', re.S)
CJK = layout.CJK
NUMERIC = re.compile(r'[-−+]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?')
IDENTIFIER = re.compile(r'[A-Za-z_$][A-Za-z_0-9]*(?:[./-][A-Za-z_0-9]+)*')
PROTECTED_NAMES = frozenset(('Q', 'K', 'V', 'W', 'X', 'Y', 'E', 'P', 'B', 'T', 'ID',
    'PAD', 'BOS', 'EOS', 'GPU', 'CPU', 'API', 'KV', 'QKV', 'RoPE', 'GQA', 'BM25',
    'MCP', 'SSE', 'LoRA', 'FlashAttention', 'PagedAttention', 'RMSNorm', 'ReLU',
    'FFN', 'MoE', 'DPO', 'RLHF', 'JSON', 'SQL', 'UTF-8', 'HTTP', 'HTTPS'))
# Countable prose concepts may take an English plural. Their occurrences in
# calls, subscripts or assignments remain literal code, as do qualified names.
PROSE_CONCEPTS = frozenset(('API', 'CPU', 'GPU', 'ID'))
CODE_FOLLOW = re.compile(r'\s*([\(\[=])')
TOKENS = ('我', '爱', '学习', '你', '！')
OWNERS = {
    'vb': ['visual/labs/figures.py:text,para,card,matrix,pipeline,timeline,swim,graph_nodes',
           'visual/labs/catalog.py:build', 'mechanisms/header_audit.py:render_header'],
    'mx': ['mechanisms/figures.py:Canvas,draw_case', 'mechanisms/walk_cases.py:draw_walk'],
    'd': ['diagrams/renderer.py:Paper'],
    'ap': ['published same-figure .ap-table-equivalent table'],
    'board': ['published .foundation-board SVG'],
    'cover': ['index.html:.cover-diagram [data-cover-node]'],
}


class FigureError(ValueError):
    """Incomplete/stale source or translation; prepare publishes nothing."""


def _root(root=None):
    return (ROOT if root is None else Path(root)).resolve()


def digest(value):
    if isinstance(value, str):
        value = value.encode('utf-8')
    return hashlib.sha256(value).hexdigest()


def safe_relative(value):
    path = PurePosixPath(value)
    if not value or not path.parts or path.is_absolute() or '..' in path.parts or '\\' in value or '\x00' in value:
        raise FigureError('unsafe relative path: %r' % value)
    return path


def _path(root, relative):
    path = root.joinpath(*safe_relative(relative).parts)
    current = root
    for part in safe_relative(relative).parts:
        current = current / part
        if current.is_symlink():
            raise FigureError('symlink is outside this writer contract: %s' % current)
    if path.resolve().is_relative_to(root) is False:
        raise FigureError('path escapes project root: %s' % relative)
    return path


def pages(root):
    result = []
    for path in sorted((root / 'i18n/content').glob('*.json')):
        page = json.loads(path.read_text(encoding='utf-8'))['page']
        safe_relative(page)
        if not page.endswith('.html') or page.startswith(('en/', 'ja/')) or page == 'complete.html':
            raise FigureError('unexpected canonical page: %s' % page)
        result.append(page)
    if not result or len(result) != len(set(result)):
        raise FigureError('canonical page inventory is empty or duplicated')
    return result


def read_data(source):
    match = JS_ASSIGNMENT.match(source)
    if not match:
        raise FigureError('unrecognized visual-data.js assignment')
    decoder = json.JSONDecoder()
    value, end = decoder.raw_decode(source, match.end())
    if source[end:].strip() != ';':
        raise FigureError('visual data has executable trailing content')
    return match.group(1), value


def walk_svgs(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ('svg', 'mobileSvg') and isinstance(child, str) and child:
                if not SVG.fullmatch(child):
                    raise FigureError('non-SVG figure field at %r' % (path + (key,),))
                yield path + (key,), child
            else:
                yield from walk_svgs(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_svgs(child, path + (index,))


def at(value, path):
    for key in path:
        value = value[key]
    return value


def put(value, path, replacement):
    parent = at(value, path[:-1])
    parent[path[-1]] = replacement


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.row = None
        self.cell = None
        self.table_depth = 0

    def handle_starttag(self, name, attrs):
        if name == 'table':
            self.table_depth += 1
        elif name == 'tr' and self.table_depth:
            self.row = []
        elif name in ('td', 'th') and self.row is not None:
            self.cell = []
        elif name == 'br' and self.cell is not None:
            self.cell.append(' ')

    def handle_endtag(self, name):
        if name in ('td', 'th') and self.cell is not None:
            self.row.append(''.join(self.cell).strip());self.cell = None
        elif name == 'tr' and self.row is not None:
            self.rows.append(self.row);self.row = None
        elif name == 'table':
            self.table_depth -= 1

    def handle_data(self, value):
        if self.cell is not None:
            self.cell.append(value)


def ap_rows(page_source, start):
    containing = [match for match in FIGURE.finditer(page_source)
                  if match.start() <= start < match.end()]
    if len(containing) != 1 or 'ap-table-equivalent' not in containing[0].group():
        raise FigureError('AP SVG needs its same-figure native table')
    parser = TableParser();parser.feed(containing[0].group())
    if not parser.rows or any(len(row) != len(parser.rows[0]) for row in parser.rows):
        raise FigureError('AP equivalent table is not rectangular')
    return parser.rows


def classify(root):
    classes = root.get('class', '').split()
    if 'ap-desktop-svg' in classes:
        return 'ap'
    if any(c.startswith('cover-diagram') for c in classes):
        return 'cover'
    for name in ('vb', 'mx', 'd'):
        if name + '-svg' in classes:
            return name
    return 'board'


def _downloads(page, source):
    for match in HREF.finditer(source):
        url = urlsplit(html.unescape(match.group(2)))
        if url.scheme or url.netloc or not url.path.lower().endswith('.svg'):
            continue
        path = unquote(url.path)
        if path.startswith('/'):
            relative = path.lstrip('/')
        else:
            # Resolve ordinary source-page ../ links, then enforce containment.
            relative = os.path.normpath(str(PurePosixPath(page).parent / path))
        safe_relative(relative)
        yield relative


def inventory(root=None):
    """Bounded current-source inventory; never imports/executes a generator."""
    root = _root(root)
    files, figures, items = {}, [], []
    downloads = set()

    def note(file, source, locator, line=1, rows=None):
        svg = layout.parse(source)
        family = classify(svg)
        if not any(CJK.search(s) for _, s in layout.strings(svg)) and not any(
                CJK.search(layout.content(e)) for e in svg.iter() if layout.tag(e) == 'text'):
            return
        if family == 'ap':
            flattened = [layout.content(e) for e in svg.iter() if layout.tag(e) == 'text']
            if rows is None or flattened != [v for row in rows for v in row]:
                raise FigureError('AP SVG/table text correspondence changed: %s %r' % (file, locator))
        index = len(figures)
        figures.append({'file': file, 'locator': locator, 'sha256': digest(source),
                        'family': family, 'owner': OWNERS[family]})
        for kind, value in layout.strings(svg, include_text=family != 'ap'):
            items.append({'file': file, 'line': line, 'figure': index,
                          'kind': kind, 'zh': value})

    for relative in pages(root):
        source = _path(root, relative).read_text(encoding='utf-8')
        present = False
        for index, match in enumerate(SVG.finditer(source)):
            raw = match.group()
            if not CJK.search(raw):
                continue
            rows = ap_rows(source, match.start()) if 'ap-desktop-svg' in raw else None
            note(relative, raw, {'kind': 'html', 'index': index},
                 source.count('\n', 0, match.start()) + 1, rows)
            present = True
        linked_downloads=set(_downloads(relative, source))
        if present or linked_downloads:
            files[relative] = digest(source)
        downloads.update(linked_downloads)
    data_source = _path(root, DATA).read_text(encoding='utf-8')
    _, data = read_data(data_source)
    files[DATA] = digest(data_source)
    for path, raw in walk_svgs(data):
        note(DATA, raw, {'kind': 'js', 'path': list(path)})
    actual_downloads = []
    for relative in sorted(downloads):
        path = _path(root, relative)
        if not path.is_file():
            raise FigureError('missing original SVG download: %s' % relative)
        raw = path.read_text(encoding='utf-8')
        if not SVG.fullmatch(raw.strip()):
            raise FigureError('download is not a standalone SVG: %s' % relative)
        files[relative] = digest(raw)
        note(relative, raw.strip(), {'kind': 'download'})
        actual_downloads.append(relative)
    return {'version': VERSION, 'policy': 'current-published-nodes / measured-word-wrap / immutable-x',
            'files': files, 'figures': figures, 'items': items, 'downloads': actual_downloads}


def source_counts(root=None):
    seen = {}
    for item in inventory(root)['items']:
        entry = seen.setdefault(item['zh'], {'n': 0, 'pages': set()})
        entry['n'] += 1;entry['pages'].add(item['file'])
    return seen


def _atomic_text(path, payload, prefix='.figure-'):
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    fd, name = tempfile.mkstemp(prefix=prefix, dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as handle:
            handle.write(payload);handle.flush();os.fchmod(handle.fileno(), mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def collect(root=None):
    root = _root(root)
    document = inventory(root)
    _atomic_text(_path(root, REGISTRY), json.dumps(document, ensure_ascii=False, indent=2) + '\n')
    unique = {item['zh'] for item in document['items']}
    families = collections.Counter(f['family'] for f in document['figures'])
    print('SVG %d 幅 | %d 处 / %d 条译文来源 | %d 下载镜像 -> %s（未改翻译表）' %
          (len(document['figures']), len(document['items']), len(unique), len(document['downloads']), REGISTRY))
    print('图形来源:', dict(families))
    return 0


def _current_registry(root):
    path = _path(root, REGISTRY)
    if not path.is_file():
        raise FigureError('run figure_strings.py collect first')
    document = json.loads(path.read_text(encoding='utf-8'))
    current = inventory(root)
    if current != document:
        raise FigureError('figure registry is stale; re-run collect and table.py build')
    return document


def _table(root):
    table = json.loads(_path(root, TABLE).read_text(encoding='utf-8')).get('s')
    if not isinstance(table, dict):
        raise FigureError('invalid translation table')
    return table


def export(lang='en', root=None):
    if lang != 'en':
        raise FigureError('this adaptation currently supports --lang=en')
    root = _root(root)
    document, table = _current_registry(root), _table(root)
    seen = set()
    print('# SVG labels — target language: en')
    print('# Keep all numbers, code IDs and model vocabulary 我 爱 学习 你 ！ unchanged.')
    print('# Labels were recovered across source line wrapping. Keep source edge whitespace literal.')
    for item in document['items']:
        source = item['zh']
        if source in seen or table.get(source, {}).get(lang):
            continue
        seen.add(source)
        row = table.get(source)
        if not isinstance(row, dict) or not isinstance(row.get('id'), int):
            raise FigureError('source missing permanent table id; run table.py build')
        if any(c in source for c in '\r\n\t'):
            raise FigureError('physical source control cannot use the standard one-line batch protocol')
        print('# source: %s:%d (%s; figure %d)' %
              (item['file'], item['line'], item['kind'], item['figure']))
        print('%d\t%s' % (row['id'], source))
    return 0


def _identifiers(source):
    result = []
    for match in IDENTIFIER.finditer(source):
        token = match.group()
        # A released paragraph can concatenate a wrapped word and the next
        # single-letter record label: "A: ... Docker" + "C: ...". Its issued
        # translation key must stay intact, but DockerC is not a code name.
        if (re.search(r'[a-z][A-Z]$', token) and
                source[match.end():match.end()+1] in (':', '：') and
                re.search(r'[A-Z][:：]', source[:match.start()])):
            result.extend((token[:-1], token[-1]))
        elif (token in PROTECTED_NAMES or re.search(r'[0-9_./]', token)
              or re.search(r'[a-z][A-Z]', token)
              or CODE_FOLLOW.match(source, match.end())
              or (len(token) == 1 and token.isalpha())):
            result.append(token)
    return result


def identifier_counts(source, value):
    """Count literal identifiers separately from ordinary plural concepts."""
    expected = collections.Counter(_identifiers(source))
    generic = collections.Counter()
    code_contexts = collections.Counter()
    for match in IDENTIFIER.finditer(source):
        token = match.group()
        context = CODE_FOLLOW.match(source, match.end())
        if token in PROSE_CONCEPTS and not context:
            generic[token] += 1
        elif context and token in expected:
            code_contexts[(token, context.group(1))] += 1
    actual, valid = {}, True
    for token, count in expected.items():
        stem = r'(?<![A-Za-z0-9_$])' + re.escape(token)
        exact = len(re.findall(stem + r'(?![A-Za-z0-9_$])', value))
        plural = len(re.findall(stem + r's(?![A-Za-z0-9_$])', value)) if generic[token] else 0
        actual[token] = {'literal': exact, 'prose_plural': plural}
        if exact < count - generic[token] or exact + plural < count:
            valid = False
    for (token, operator), count in code_contexts.items():
        expression = (r'(?<![A-Za-z0-9_$])' + re.escape(token) +
                      r'(?![A-Za-z0-9_$])\s*' + re.escape(operator))
        if len(re.findall(expression, value)) < count:
            valid = False
    return valid, list(expected.elements()), actual


def model_tokens(source):
    if layout.TOKEN_ONLY.fullmatch(source.strip()):
        return [tok for tok in TOKENS for _ in range(source.count(tok))]
    result = []
    for token in TOKENS:
        t = re.escape(token)
        cues = (r'[“"\'「]%s[”"\'」]', r'\[[^\]]*%s[^\]]*\]',
                r'%s\s*[0-9→]', r'(?:片段|位置|ID|t=\d+)\s*[:：·/ ]\s*%s',
                r'(?:位置|键|查询|值|ID|t=|s=)?\s*\d+\s*[·:：/ ]\s*%s',
                r'%s\s*[·/／、，,→+]\s*(?:我|爱|学习|你|！)',
                r'(?:我|爱|学习|你|！)\s*[·/／、，,→+]\s*%s')
        clusters = re.findall(r'[\u4e00-\u9fff]+', source)
        joined = any(token in phrase and phrase in source for phrase in ('我爱学习','我爱','你爱')) or any(token in cluster and re.fullmatch(r'(?:我|爱|学习|你)+', cluster)
                     and len(cluster) > len(token) for cluster in clusters)
        if joined or any(re.search(pattern % t, source) for pattern in cues):
            result.extend([token] * source.count(token))
    return result


def numeric_values(value, normalize_dates=False):
    # English may spell a calendar month, or put a day before that month.
    # This recognizes the same dates; it does not infer a changed date/value.
    if not normalize_dates:
        return collections.Counter(number.replace('−','-') for number in NUMERIC.findall(value))
    months=('January','February','March','April','May','June','July','August',
            'September','October','November','December')
    for number,month in enumerate(months,1):
        value=re.sub(r'\b'+month+r'\s+(\d{1,2})(?!\d)',
                     lambda m:str(number)+'月'+m.group(1)+'日',value)
        value=re.sub(r'(?<!\d)(\d{1,2})\s+'+month+r'\b',
                     lambda m:str(number)+'月'+m.group(1)+'日',value)
        value=re.sub(r'\b'+month+r'\b',str(number)+'月',value)
    return collections.Counter(number.replace('−','-') for number in NUMERIC.findall(value))


def validate_translation(source, value):
    if not isinstance(value, str) or not value.strip():
        raise FigureError('empty translation: %s' % source[:90])
    if any(ord(c) < 32 or 0xd800 <= ord(c) <= 0xdfff for c in value):
        raise FigureError('control character in translation: %s' % source[:90])
    remainder = value
    for token in TOKENS:
        remainder = remainder.replace(token, '')
    if CJK.search(remainder):
        raise FigureError('untranslated SVG prose: %s -> %s' % (source[:80], value[:100]))
    if numeric_values(source) != numeric_values(value, bool(re.search(r'\d+\s*月',source))):
        raise FigureError('changed SVG numeric values: %r -> %r (%s)' %
                          (NUMERIC.findall(source), NUMERIC.findall(value), source[:90]))
    identifiers_valid, expected, actual = identifier_counts(source, value)
    if not identifiers_valid:
        raise FigureError('changed SVG code identifiers: %r -> %r (%s)' % (expected, actual, source[:90]))
    for token in set(model_tokens(source)):
        if value.count(token) < model_tokens(source).count(token):
            raise FigureError('lost model vocabulary %s: %s' % (token, source[:90]))
    return value


def _translations(document, table, lang):
    unique = dict.fromkeys(item['zh'] for item in document['items'])
    missing = [source for source in unique if not table.get(source, {}).get(lang)]
    if missing:
        raise FigureError('missing %d SVG translations; first: %s' % (len(missing), missing[0][:100]))
    return {source: validate_translation(source, table[source][lang]) for source in unique}


def data_without_svg(value):
    if isinstance(value, dict):
        return {k: data_without_svg(v) for k, v in value.items() if k not in ('svg', 'mobileSvg')}
    if isinstance(value, list):
        return [data_without_svg(v) for v in value]
    return value


def _raw_for(root, figure, originals, data):
    relative, locator = figure['file'], figure['locator']
    if locator['kind'] == 'html':
        return list(SVG.finditer(originals[relative]))[locator['index']].group()
    if locator['kind'] == 'js':
        return at(data, locator['path'])
    return _path(root, relative).read_text(encoding='utf-8').strip()


def _download_links(source, page, downloads):
    def replace(match):
        raw = match.group(2)
        u = urlsplit(html.unescape(raw))
        if u.scheme or u.netloc or not u.path.lower().endswith('.svg'):
            return match.group()
        # Both apply.py's original-root rewrite and an already adapted link
        # may occur on a rerun. Match only the exact known download suffix.
        normalized = unquote(u.path)
        candidates = [d for d in downloads if normalized == d or normalized.endswith('/' + d)]
        if len(candidates) != 1:
            return match.group()
        desired = os.path.relpath(candidates[0], str(PurePosixPath(page).parent))
        if u.query:
            desired += '?' + u.query
        if u.fragment:
            desired += '#' + u.fragment
        return 'href=' + match.group(1) + html.escape(desired, quote=True) + match.group(1)
    return HREF.sub(replace, source)


def prepare(lang='en', root=None):
    """Prepare every byte and proof in memory; no directory/file mutation."""
    if lang != 'en':
        raise FigureError('this adaptation currently supports --lang=en')
    root = _root(root)
    document, table = _current_registry(root), _table(root)
    translations = _translations(document, table, lang)

    def translate(source):
        if not layout.translatable(source):
            return source
        if source not in translations:
            raise FigureError('unregistered SVG source text: %r' % source)
        return translations[source]

    originals = {relative: _path(root, relative).read_text(encoding='utf-8')
                 for relative in document['files'] if relative.endswith('.html')}
    targets = {}
    target_matches = {}
    for relative in originals:
        target = _path(root, lang + '/' + relative)
        if not target.is_file():
            raise FigureError('missing translated page: %s' % target)
        targets[relative] = target.read_text(encoding='utf-8')
        target_matches[relative] = list(SVG.finditer(targets[relative]))
        if len(target_matches[relative]) != len(list(SVG.finditer(originals[relative]))):
            raise FigureError('translated page SVG identity/count changed: %s' % relative)
    _, original_data = read_data(_path(root, DATA).read_text(encoding='utf-8'))
    data_target = _path(root, lang + '/' + DATA)
    if not data_target.is_file():
        raise FigureError('run data_strings.py write before figure write')
    global_name, target_data = read_data(data_target.read_text(encoding='utf-8'))
    before_data = data_without_svg(target_data)
    if [p for p, _ in walk_svgs(original_data)] != [p for p, _ in walk_svgs(target_data)]:
        raise FigureError('English visual data frame/field identity changed')
    replacements = collections.defaultdict(list)
    payloads, reports = {}, []
    for figure in document['figures']:
        raw = _raw_for(root, figure, originals, original_data)
        if digest(raw) != figure['sha256']:
            raise FigureError('stale SVG figure hash: %s' % figure['file'])
        report = {'file': figure['file'], 'locator': figure['locator'], 'family': figure['family']}
        locator = figure['locator']
        if figure['family'] == 'ap':
            match = target_matches[figure['file']][locator['index']]
            rows = ap_rows(targets[figure['file']], match.start())
            source_match = list(SVG.finditer(originals[figure['file']]))[locator['index']]
            source_rows = ap_rows(originals[figure['file']], source_match.start())
            if len(rows) != len(source_rows) or any(len(a) != len(b) for a, b in zip(rows, source_rows)):
                raise FigureError('translated AP table shape changed')
            # Its prose already passed the page pipeline, but numerical/model
            # cell identity is still a figure publication obligation.
            for original_row, target_row in zip(source_rows, rows):
                for zh, en in zip(original_row, target_row):
                    if CJK.search(zh) and not layout.TOKEN_ONLY.fullmatch(zh):
                        validate_translation(zh, en)
                    elif zh != en:
                        raise FigureError('AP table changed immutable data cell: %s' % zh)
            output = layout.redraw_table(raw, rows, translate, report)
        else:
            output = layout.reflow(raw, translations, translate, report)
        reports.append(report)
        if locator['kind'] == 'html':
            match = target_matches[figure['file']][locator['index']]
            # The outer SVG's identity remains the same across a rerun.
            source_node, target_node = layout.parse(raw), layout.parse(match.group())
            for attribute in ('class', 'id', 'aria-labelledby'):
                if source_node.get(attribute) != target_node.get(attribute):
                    raise FigureError('SVG identity changed before publication: %s' % figure['file'])
            replacements[figure['file']].append((match.start(), match.end(), output))
        elif locator['kind'] == 'js':
            put(target_data, locator['path'], output)
        else:
            payloads[lang + '/' + figure['file']] = output + '\n'
    for relative, source in targets.items():
        for start, end, value in sorted(replacements[relative], reverse=True):
            source = source[:start] + value + source[end:]
        payloads[lang + '/' + relative] = _download_links(source, relative, document['downloads'])
    if before_data != data_without_svg(target_data):
        raise FigureError('figure adaptation changed JS prose/data outside SVG fields')
    payloads[lang + '/' + DATA] = 'window.%s=%s;\n' % (global_name, json.dumps(target_data, ensure_ascii=False))
    # Include every referenced download, even an already-English original.
    for relative in document['downloads']:
        payloads.setdefault(lang + '/' + relative,
                            _path(root, relative).read_text(encoding='utf-8'))
    for relative in payloads:
        _path(root, relative)  # preflight all paths before write can mkdir
    proof = {'version': VERSION, 'registry_sha256': digest(json.dumps(document, ensure_ascii=False, sort_keys=True)),
             'figures': len(reports), 'downloads': len(document['downloads']),
             'outputs': len(payloads), 'report': reports,
             'proof_limits': ['No browser/service was started.',
                'Vertical shape reflow preserves endpoints and horizontal proportions; original generators/data are read-only.',
                'Per-file replacement is atomic for readers; a crash between files requires rerunning write.']}
    return payloads, proof


def _publish(root, payloads):
    """Stage all bytes first; roll back ordinary in-process commit failures."""
    staged, originals, committed = {}, {}, []
    try:
        for relative, payload in payloads.items():
            path = _path(root, relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            originals[relative] = path.read_bytes() if path.exists() else None
            mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
            fd, temporary = tempfile.mkstemp(prefix='.figure-stage-', dir=path.parent)
            staged[relative] = temporary
            with os.fdopen(fd, 'wb') as handle:
                handle.write(payload.encode('utf-8'));handle.flush();os.fchmod(handle.fileno(), mode)
        # Detect another legitimate builder before replacing any of its work.
        for relative, old in originals.items():
            path = _path(root, relative)
            now = path.read_bytes() if path.exists() else None
            if now != old:
                raise FigureError('destination changed while staging: %s' % relative)
        for relative, temporary in staged.items():
            os.replace(temporary, _path(root, relative));committed.append(relative)
    except BaseException:
        for relative in reversed(committed):
            old = originals[relative];path = _path(root, relative)
            if old is None:
                path.unlink(missing_ok=True)
            else:
                _atomic_text(path, old.decode('utf-8'), '.figure-rollback-')
        raise
    finally:
        for name in staged.values():
            if os.path.exists(name):
                os.unlink(name)


def write(lang='en', root=None):
    root = _root(root)
    payloads, proof = prepare(lang, root)
    _publish(root, payloads)
    print('%s: SVG %d 幅；下载镜像 %d 个；%d 个文件已写出。原始文件、数字、横向比例与帧高亮保持。' %
          (lang, proof['figures'], proof['downloads'], proof['outputs']))
    print('排版验证: 每行测宽均在所属槽内；按词换行；保持可读字号；框与箭头端点随行高增长。')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('collect', 'export', 'write'))
    parser.add_argument('--lang', default='en')
    args = parser.parse_args(argv)
    try:
        return {'collect': lambda: collect(), 'export': lambda: export(args.lang),
                'write': lambda: write(args.lang)}[args.command]()
    except (FigureError, layout.LayoutError) as error:
        print('SVG adaptation refused: %s' % error, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
