"""Rebuild the offline continuous edition from current page articles.

The Chinese complete.html owns layout, the 250-page order, adapted scripts,
and resource coverage. Current paged articles own teaching content. English
prose is read from en/ and table.json; this generator never translates it.
All work is prepared and checked before one atomic output replacement.

Run: python3 i18n/build_complete.py --lang=en
     python3 i18n/build_complete.py --lang=en --output /tmp/en-complete.html
     python3 i18n/build_complete.py --diagnose-zh --output /tmp/zh-complete.html \
             --report /tmp/complete-diagnostic.json

Only en/complete.html and explicit temporary outputs may be written. The
Chinese original, source resources, datasets and translation table are read-only.
No server, child process, third-party package, or network access is used.
"""
import argparse
import base64
import difflib
import hashlib
import html
import json
import mimetypes
import re
import sys
import tempfile
from collections import Counter, OrderedDict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import apply
import complete_strings
import runtime_strings

ROOT = Path(__file__).resolve().parent.parent
CompleteError = complete_strings.CompleteError
VOID = frozenset(('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                  'link', 'meta', 'param', 'source', 'track', 'wbr'))
REMOVE_CLASSES = frozenset(('breadcrumb', 'mobile-outline', 'reading-meta', 'anchor-target'))
IDREFS = frozenset(('for', 'list', 'form', 'headers', 'aria-labelledby', 'aria-describedby',
                    'aria-controls', 'aria-owns', 'aria-activedescendant', 'aria-details',
                    'aria-flowto', 'aria-errormessage'))
ATTR = re.compile(r'(?P<name>[\w:-]+)(?P<eq>\s*=\s*)(?P<quote>[\'"])(?P<value>.*?)(?P=quote)', re.S)
URL_ID = re.compile(r'url\(\s*([\'"]?)#([^\s)\'"]+)\1\s*\)', re.I)
EXTERNAL = re.compile(r'^(?:[a-zA-Z][\w+.-]*:|//)')
SUPPLEMENTS = {'engineering--agent-evidence': 'engineering/agent-evidence.html',
               'engineering--agent-validation': 'engineering/agent-validation.html'}
DATA_ASSETS = {'I18N_META': 'assets/i18n-data.js',
               'COURSE_SEARCH': 'assets/search-data.js', 'BOOK_CATALOG': 'assets/catalog.js',
               'VISUAL_LESSONS': 'assets/visual-data.js', 'MODEL_FRAMES': 'assets/model-data.js'}
MIME = {'.svg': 'image/svg+xml', '.html': 'text/html', '.json': 'application/json',
        '.py': 'text/x-python', '.md': 'text/plain', '.mmd': 'text/plain',
        '.txt': 'text/plain', '.log': 'text/plain'}


def splice(source, replacements):
    parts, last = [], 0
    for start, end, value in sorted(replacements):
        if start < last or end < start:
            raise CompleteError('overlapping replacement ranges')
        parts.extend((source[last:start], value))
        last = end
    parts.append(source[last:])
    return ''.join(parts)


class Markup(HTMLParser):
    """Retain exact source ranges; never serialize or repair teaching markup."""
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source, self.nodes, self.stack, self.text = source, [], [], []
        self.lines = [0] + [m.end() for m in re.finditer('\n', source)]
        self.feed(source)
        self.close()

    def position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def start(self, tag, attrs, closed=False):
        at = self.position()
        node = dict(tag=tag, attrs=dict(attrs), start=at,
                    open_end=at + len(self.get_starttag_text()))
        self.nodes.append(node)
        if closed or tag in VOID:
            node.update(close_start=node['open_end'], end=node['open_end'])
        else:
            self.stack.append(node)

    def handle_starttag(self, tag, attrs):
        self.start(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self.start(tag, attrs, True)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]['tag'] == tag:
                node = self.stack[i]
                node.update(close_start=self.position(), end=self.source.index('>', self.position()) + 1)
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.text.append(data)

    def handle_entityref(self, name):
        self.text.append(html.unescape('&' + name + ';'))

    def handle_charref(self, name):
        self.text.append(html.unescape('&#' + name + ';'))


class Inputs:
    def __init__(self, root):
        self.root, self.content = root.resolve(), OrderedDict()

    def read(self, path):
        path = path.resolve()
        if not path.is_relative_to(self.root) or not path.is_file():
            raise CompleteError('missing or out-of-root input: %s' % path)
        if path not in self.content:
            self.content[path] = path.read_bytes()
        return self.content[path]

    def text(self, path):
        return self.read(path).decode('utf-8')

    def current(self):
        changed = [path.relative_to(self.root).as_posix() for path, data in self.content.items()
                   if not path.is_file() or path.read_bytes() != data]
        if changed:
            raise CompleteError('inputs changed while building: %s' % ', '.join(changed[:5]))

    def hashes(self):
        return {path.relative_to(self.root).as_posix(): hashlib.sha256(data).hexdigest()
                for path, data in self.content.items()}


def article(source, page):
    nodes = [node for node in Markup(source).nodes if node['tag'] == 'article']
    if len(nodes) != 1 or 'close_start' not in nodes[0]:
        raise CompleteError('expected one closed article: %s' % page)
    node = nodes[0]
    return source[node['open_end']:node['close_start']]


def strip_page_chrome(source):
    markup, removals, removed_ids = Markup(source), [], set()
    for node in markup.nodes:
        if not REMOVE_CLASSES.intersection(node['attrs'].get('class', '').split()):
            continue
        if 'end' not in node:
            raise CompleteError('unclosed per-page chrome: %s' % node['tag'])
        if any(start <= node['start'] < end for start, end, _ in removals):
            continue
        removals.append((node['start'], node['end'], ''))
    for node in markup.nodes:
        if 'id' in node['attrs'] and any(a <= node['start'] < b for a, b, _ in removals):
            removed_ids.add(node['attrs']['id'])
    return splice(source, removals), removed_ids


def assignments(source):
    """Decode strict window JSON only; executable scripts keep their owner."""
    result = []
    for match in re.finditer(r'\bwindow\.([A-Za-z_$][\w$]*)\s*=\s*(?=[\[{])', source):
        try:
            value, length = json.JSONDecoder().raw_decode(source[match.end():])
        except json.JSONDecodeError:
            continue
        result.append((match.group(1), match.end(), match.end() + length, value))
    return result


def english_scope(template, index_source):
    """Copy the edition-owned scope notice without changing other head markup."""
    source = Markup(index_source)
    heads = [n for n in source.nodes if n['tag'] == 'head' and 'close_start' in n]
    scopes = [n for n in source.nodes if n['tag'] == 'meta' and
              (n['attrs'].get('name') or '').lower() == 'i18n-scope']
    if len(heads) != 1 or len(scopes) != 1:
        raise CompleteError('English index must have one head and one i18n-scope meta')
    scope, head = scopes[0], heads[0]
    content = scope['attrs'].get('content')
    if (not isinstance(content, str) or not content.strip() or
            not head['open_end'] <= scope['start'] < head['close_start']):
        raise CompleteError('English index i18n-scope must have nonempty content in head')
    markup = '<meta name="i18n-scope" content="%s">' % html.escape(content, quote=True)
    destination = Markup(template)
    heads = [n for n in destination.nodes if n['tag'] == 'head' and 'close_start' in n]
    scopes = [n for n in destination.nodes if n['tag'] == 'meta' and
              (n['attrs'].get('name') or '').lower() == 'i18n-scope']
    if len(heads) != 1 or len(scopes) > 1:
        raise CompleteError('continuous template must have one head and at most one i18n-scope meta')
    if scopes:
        scope = scopes[0]
        if not heads[0]['open_end'] <= scope['start'] < heads[0]['close_start']:
            raise CompleteError('continuous template i18n-scope must be in head')
        return splice(template, [(scope['start'], scope['end'], markup)])
    at = heads[0]['close_start']
    return splice(template, [(at, at, markup)])


class Resources:
    def __init__(self, inputs, lang, initial, heading, download, summary):
        self.inputs, self.lang = inputs, lang
        self.paths, self.ids, self.mirrors = OrderedDict(), {}, []
        self.heading, self.download, self.summary = heading, download, summary
        for path in initial:
            self.add(path)

    def add(self, relative):
        relative = Path(relative).as_posix()
        if Path(relative).is_absolute() or '..' in Path(relative).parts:
            raise CompleteError('invalid resource path: %s' % relative)
        identity = 'resource--' + hashlib.sha256(relative.encode()).hexdigest()[:12]
        if identity in self.ids and self.ids[identity] != relative:
            raise CompleteError('resource id collision')
        self.ids[identity], self.paths[relative] = relative, identity
        return '#' + identity

    def source_path(self, relative):
        mirror = self.inputs.root / self.lang / relative
        if self.lang != 'zh-CN' and Path(relative).suffix.lower() in ('.svg', '.html') and mirror.is_file():
            self.mirrors.append(relative)
            return mirror
        return self.inputs.root / relative

    def render(self):
        parts = ['<section class="standalone-section" id="embedded-resources"><h1>',
                 self.heading, '</h1>']
        for relative, identity in self.paths.items():
            data = self.inputs.read(self.source_path(relative))
            suffix = Path(relative).suffix.lower()
            mime = MIME.get(suffix, mimetypes.guess_type(relative)[0] or 'application/octet-stream')
            uri = 'data:%s;base64,%s' % (mime, base64.b64encode(data).decode('ascii'))
            parts.extend(('<section id="', identity, '"><h2>', html.escape(relative),
                          '</h2><a download="', html.escape(Path(relative).name, quote=True),
                          '" href="', uri, '">', self.download, '</a>'))
            if mime.startswith('image/'):
                parts.extend(('<img alt="', html.escape(Path(relative).stem, quote=True),
                              '" src="', uri, '"/>'))
            else:
                try:
                    text = data.decode('utf-8')
                except UnicodeDecodeError:
                    text = None
                if text is not None:
                    parts.extend(('<details><summary data-i18n="disclose.source">', self.summary,
                                  '</summary><pre><code>', html.escape(text, quote=False),
                                  '</code></pre></details>'))
            parts.append('</section>')
        parts.append('</section>')
        return ''.join(parts)


class Builder:
    def __init__(self, root=None, lang='en'):
        if lang not in ('en', 'zh-CN'):
            raise CompleteError('supported languages: en, zh-CN diagnostic')
        self.root, self.lang = Path(root or ROOT).resolve(), lang
        self.inputs = Inputs(self.root)
        self.base = self.root if lang == 'zh-CN' else self.root / lang
        self.original = self.inputs.text(self.root / 'complete.html')
        self.old_index = complete_strings.CompleteIndex(self.original)
        self.canonical = json.loads(self.inputs.text(self.root / 'editorial/canonical-pages.json'))
        expected = [(p['path'], p['id']) for p in self.canonical]
        actual = [(p['attrs']['data-book-page'], p['attrs']['id']) for p in self.old_index.sections
                  if 'data-book-page' in p['attrs']]
        if len(expected) != 250 or actual != expected:
            raise CompleteError('canonical pages and original complete order disagree')
        self.page_ids = dict(expected)
        self.page_ids.update({page: sid for sid, page in SUPPLEMENTS.items()})
        self.clean, self.removed, self.articles, self.proofs = {}, {}, {}, []
        self.current_ids, self.diagnostic_search_repairs = {}, []
        self.bundle, self.mapping = {}, {}
        template = self.original
        if lang != 'zh-CN':
            self.inputs.read(self.root / 'i18n/complete-registry.json')
            self.inputs.read(self.root / 'i18n/table.json')
            registry, self.mapping = complete_strings.translations(self.root, lang)
            template = complete_strings.localize_shell(template, registry, self.mapping)
        i18n_asset = self.inputs.text(self.base / 'assets/i18n-data.js')
        self.bundle = next((value for name, _, _, value in assignments(i18n_asset)
                            if name == 'I18N_STRINGS'), {}).get(lang, {})
        if not self.bundle:
            raise CompleteError('missing interface bundle language: %s' % lang)
        if lang != 'zh-CN':
            template, leftovers = apply.chrome(template, self.bundle)
            if leftovers:
                raise CompleteError('missing interface fallback: %s' % ', '.join(leftovers[:5]))
            template = re.sub(r'(<html\b[^>]*\blang=)[\'"][^\'"]+[\'"]', r'\1"en"', template, count=1)
            template = english_scope(template, self.inputs.text(self.base / 'index.html'))
        self.template = template
        self.index = complete_strings.CompleteIndex(template)
        embedded = next(p for p in self.index.sections if p['attrs'].get('id') == 'embedded-resources')
        old_resource = template[embedded['open_end']:embedded['close_start']]
        initial = [html.unescape(value) for value in re.findall(r'<h2\b[^>]*>([^<]+)</h2>', old_resource)]
        heading = re.search(r'<h1\b[^>]*>([^<]+)</h1>', old_resource).group(1)
        download = re.search(r'<a\b[^>]*\bdownload="[^"]*"[^>]*>([^<]+)</a>', old_resource).group(1)
        self.initial_resources = tuple(initial)
        self.resources = Resources(self.inputs, lang, initial, heading, download,
                                   html.escape(self.bundle['disclose.source']))
        for page in self.page_ids:
            body = article(self.inputs.text(self.base / page), page)
            self.clean[page], self.removed[page] = strip_page_chrome(body)
            self.current_ids[page] = {n['attrs']['id'] for n in Markup(self.clean[page]).nodes
                                      if 'id' in n['attrs']}

    def target(self, url, page, *, source=False):
        if not url or EXTERNAL.match(url):
            return url
        parsed = urlsplit(html.unescape(url))
        fragment = unquote(parsed.fragment)
        if not parsed.path:
            target = page
        else:
            candidate = (self.base / Path(page).parent / unquote(parsed.path)).resolve()
            if candidate.is_relative_to(self.base):
                target = candidate.relative_to(self.base).as_posix()
            elif candidate.is_relative_to(self.root):
                target = candidate.relative_to(self.root).as_posix()
                if target.startswith(self.lang + '/'):
                    target = target[len(self.lang) + 1:]
            else:
                raise CompleteError('local link escapes book root: %s in %s' % (url, page))
        if target == 'complete.html':
            return '#main-content'
        if target in self.page_ids and not source:
            sid = self.page_ids[target]
            if fragment in self.removed.get(target, ()):
                fragment = ''
            return '#' + sid + ('--' + fragment if fragment else '')
        return self.resources.add(target)

    def transform(self, body, page):
        sid = self.page_ids[page]
        before = Markup(body)
        ids = [n['attrs']['id'] for n in before.nodes if 'id' in n['attrs']]
        if len(ids) != len(set(ids)):
            raise CompleteError('duplicate article ids: %s' % page)

        def prefixed(identity):
            return sid if identity in self.removed[page] else sid + '--' + identity

        replacements = []
        for node in before.nodes:
            opening = body[node['start']:node['open_end']]

            def change(match):
                name, value = match.group('name').lower(), html.unescape(match.group('value'))
                updated = value
                if name == 'id':
                    updated = prefixed(value)
                elif name in IDREFS:
                    updated = ' '.join(prefixed(item) for item in value.split())
                elif name in ('href', 'xlink:href'):
                    updated = self.target(value, page)
                elif name in ('src', 'poster') and value and not EXTERNAL.match(value):
                    link = self.target(value, page, source=True)
                    relative = self.resources.ids[link[1:]]
                    path = self.resources.source_path(relative)
                    data = self.inputs.read(path)
                    mime = MIME.get(path.suffix.lower(), mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
                    updated = 'data:%s;base64,%s' % (mime, base64.b64encode(data).decode('ascii'))
                updated = URL_ID.sub(lambda item: 'url(#' + prefixed(item.group(2)) + ')', updated)
                if name in ('begin', 'end'):
                    updated = re.sub(r'(?<![\w-])([A-Za-z_][\w:-]*)\.(?=[A-Za-z])',
                                     lambda item: prefixed(item.group(1)) + '.', updated)
                if updated == value:
                    return match.group()
                quote = match.group('quote')
                encoded = html.escape(updated, quote=True).replace('&#x27;', "'" if quote == '"' else '&#x27;')
                return match.group('name') + match.group('eq') + quote + encoded + quote

            updated = ATTR.sub(change, opening)
            if updated != opening:
                replacements.append((node['start'], node['open_end'], updated))
        result = splice(body, replacements)
        after = Markup(result)
        if before.text != after.text:
            raise CompleteError('article text changed during assembly: %s' % page)
        for tag in ('pre', 'code'):
            # Source listings contain real <span id="...-L123"> wrappers.
            # Those line anchors need the same prefix as prose anchors; the
            # displayed code (including every newline/space) stays exact.
            content = lambda doc: [''.join(Markup(inner).text) for inner in
                                   re.findall(r'<' + tag + r'\b[^>]*>([\s\S]*?)</' + tag + '>', doc, re.I)]
            if content(body) != content(result):
                raise CompleteError('%s content changed: %s' % (tag, page))
        before_details = [(n['attrs'].get('class', ''), 'open' in n['attrs'])
                          for n in before.nodes if n['tag'] == 'details']
        after_details = [(n['attrs'].get('class', ''), 'open' in n['attrs'])
                         for n in after.nodes if n['tag'] == 'details']
        if before_details != after_details:
            raise CompleteError('disclosure state changed: %s' % page)
        if any('quiz-answer' in classes.split() and opened for classes, opened in after_details):
            raise CompleteError('quiz answer is initially open: %s' % page)
        # All non-reference attributes in SVG geometry, shapes and numerical
        # diagrams must be identical; prefixing references is the only change.
        def geometry(markup):
            return [(n['tag'], tuple((k, v) for k, v in sorted(n['attrs'].items())
                                     if k not in IDREFS | {'id', 'href', 'xlink:href'} and
                                     not (isinstance(v, str) and URL_ID.search(v))))
                    for n in markup.nodes if n['tag'] in
                    ('svg', 'path', 'rect', 'circle', 'line', 'polyline', 'polygon', 'text', 'tspan', 'g')]
        if geometry(before) != geometry(after):
            raise CompleteError('SVG numerical geometry changed: %s' % page)
        self.proofs.append(dict(page=page, article_sha256=complete_strings.sha(body),
                                assembled_sha256=complete_strings.sha(result),
                                text_unchanged=True, code_unchanged=True, svg_geometry_unchanged=True,
                                ids=len(ids), svg=sum(n['tag'] == 'svg' for n in before.nodes),
                                quiz=sum('quiz-answer' in c.split() for c, _ in before_details),
                                disclosures=len(before_details)))
        return result

    def scripts(self):
        replacements = []
        for number, node in enumerate(self.index.scripts):
            source = self.template[node['open_end']:node['close_start']]
            data = assignments(source)
            owner = next((DATA_ASSETS[name] for name, _, _, _ in data if name in DATA_ASSETS), None)
            if owner:
                source = self.inputs.text(self.base / owner)
                if owner in ('assets/catalog.js', 'assets/search-data.js'):
                    changes = []
                    for name, start, end, rows in assignments(source):
                        if name not in ('BOOK_CATALOG', 'COURSE_SEARCH') or not isinstance(rows, list):
                            raise CompleteError('invalid catalogue/search assignment')
                        prepared = []
                        for row in rows:
                            target = self.target(row['path'], 'index.html')
                            parsed = urlsplit(row['path'])
                            if (parsed.path in self.page_ids and parsed.fragment and
                                    unquote(parsed.fragment) not in self.current_ids[parsed.path] and
                                    unquote(parsed.fragment) not in self.removed[parsed.path]):
                                if self.lang != 'zh-CN':
                                    raise CompleteError('stale English search anchor; rebuild gen_assets: %s' % row['path'])
                                # The root Chinese search asset predates its
                                # current page ids. This read-only diagnostic
                                # keeps the row reachable at the same page's
                                # root and records every repair explicitly.
                                target = '#' + self.page_ids[parsed.path]
                                self.diagnostic_search_repairs.append(dict(source=row['path'], target=target))
                            # Atelier's initial suggestions filter canonical
                            # page paths before resolve() turns them into hashes.
                            # Keep that contract; excluded pages use resource
                            # hashes, and full-text results always use hashes.
                            if name == 'BOOK_CATALOG' and urlsplit(row['path']).path in self.page_ids:
                                target = row['path']
                            prepared.append(dict(row, path=target))
                        rows = prepared
                        changes.append((start, end, json.dumps(rows, ensure_ascii=False, separators=(',', ':'))))
                    source = splice(source, changes)
            elif 'Interface localisation.' in source:
                # The English runtime uses this edition's scope notice. Its
                # local asset is required; Chinese diagnostics retain the
                # original runtime because self.base is the book root there.
                source = self.inputs.text(self.base / 'assets/i18n.js')
            elif self.lang != 'zh-CN':
                source = runtime_strings.localize_js(source, self.mapping, 'complete.html#script-%d' % number)
            source = re.sub(r'</script', r'<\/script', source, flags=re.I)
            replacements.append((node['open_end'], node['close_start'], source))
        return replacements

    def shell_references(self):
        # The original shell still has five local project links. They are not
        # among the 250 article sections, so retain them as downloadable source
        # resources rather than leaving an offline dependency in the shell.
        shell = splice(self.template, [(n['start'], n['end'], ' ' * (n['end'] - n['start']))
                                       for n in self.index.sections])
        changes = []
        for node in Markup(shell).nodes:
            opening = shell[node['start']:node['open_end']]

            def change(match):
                value = html.unescape(match.group('value'))
                if match.group('name').lower() not in ('href', 'xlink:href') or not value or value.startswith('#') or EXTERNAL.match(value):
                    return match.group()
                value = self.target(value, 'index.html')
                quote = match.group('quote')
                return match.group('name') + match.group('eq') + quote + html.escape(value, quote=True) + quote

            updated = ATTR.sub(change, opening)
            if updated != opening:
                changes.append((node['start'], node['open_end'], updated))
        return changes

    def prepare(self):
        replacements = []
        for node in self.index.sections:
            attrs = node['attrs']
            page = attrs.get('data-book-page') or SUPPLEMENTS.get(attrs.get('id'))
            if page:
                content = self.transform(self.clean[page], page)
                self.articles[page] = content
                replacements.append((node['open_end'], node['close_start'], content))
        replacements.extend(self.scripts())  # Search may add excluded HTML resources.
        replacements.extend(self.shell_references())
        embedded = next(p for p in self.index.sections if p['attrs'].get('id') == 'embedded-resources')
        replacements.append((embedded['start'], embedded['end'], self.resources.render()))
        # Keep the continuous edition's original CSS, including its adapted
        # layout. Only the existing i18n style sentinel follows its owner.
        start = self.template.find('/*i18n-css:begin*/')
        end = self.template.find('/*i18n-css:end*/', start)
        if start < 0 or end < start:
            raise CompleteError('missing continuous i18n CSS sentinel')
        start += len('/*i18n-css:begin*/')
        replacements.append((start, end, self.inputs.text(self.root / 'assets/i18n.css')))
        output = splice(self.template, replacements)
        result = validate_document(output, self.canonical)
        result.update(language=self.lang, bytes=len(output.encode()), sha256=complete_strings.sha(output),
                      original_resources=len(self.initial_resources), resources=len(self.resources.paths),
                      added_resources=[p for p in self.resources.paths if p not in self.initial_resources],
                      localized_resource_mirrors=sorted(set(self.resources.mirrors)),
                      diagnostic_stale_search_targets=len(self.diagnostic_search_repairs),
                      diagnostic_search_repairs=self.diagnostic_search_repairs,
                      article_proofs=self.proofs, input_sha256=self.inputs.hashes())
        self.inputs.current()
        return output, result


def validate_document(source, canonical):
    markup = Markup(source)
    ids = [node['attrs']['id'] for node in markup.nodes if 'id' in node['attrs']]
    duplicates = [identity for identity, n in Counter(ids).items() if n > 1]
    known, missing, idrefs, dependencies = set(ids), [], [], []
    for node in markup.nodes:
        attrs = node['attrs']
        for name, value in attrs.items():
            if not isinstance(value, str):
                continue
            if name in ('href', 'xlink:href') and value.startswith('#') and value[1:] not in known:
                missing.append(value)
            if name in IDREFS:
                idrefs.extend(item for item in value.split() if item not in known)
            idrefs.extend(match.group(2) for match in URL_ID.finditer(value) if match.group(2) not in known)
            if name in ('src', 'poster') and value and not value.startswith('data:'):
                dependencies.append((node['tag'], value))
            if node['tag'] == 'link' and name == 'href' and attrs.get('rel') in ('stylesheet', 'preload', 'modulepreload'):
                dependencies.append(('link', value))
            if name in ('href', 'xlink:href') and value and not value.startswith(('#', 'data:')) and not EXTERNAL.match(value):
                dependencies.append(('local-link', value))
    actual = [(n['attrs'].get('data-book-page'), n['attrs'].get('id')) for n in markup.nodes
              if n['tag'] == 'section' and 'data-book-page' in n['attrs']]
    expected = [(p['path'], p['id']) for p in canonical]
    if actual != expected or len(actual) != 250:
        raise CompleteError('assembled page coverage/order changed')
    standalone = [n for n in markup.nodes if 'standalone-section' in n['attrs'].get('class', '').split()]
    if len(standalone) != 253 or not set(SUPPLEMENTS).issubset(known) or 'embedded-resources' not in known:
        raise CompleteError('supplement/resource section coverage changed')
    if duplicates or missing or idrefs or dependencies:
        raise CompleteError('invalid offline document: duplicate ids=%r; broken anchors=%r; '
                            'IDREFs=%r; dependencies=%r' %
                            (duplicates[:8], list(dict.fromkeys(missing))[:8],
                             list(dict.fromkeys(idrefs))[:8], dependencies[:8]))
    dynamic_paths, search_rows = [], 0
    for node in markup.nodes:
        if node['tag'] == 'style' and 'close_start' in node:
            css = source[node['open_end']:node['close_start']]
            urls = re.findall(r'url\(([^)]*)\)', css, re.I)
            if re.search(r'@import\b', css, re.I) or any(
                    not url.strip().strip('\'"').startswith(('data:', '#')) for url in urls):
                raise CompleteError('external CSS runtime dependency')
        elif node['tag'] == 'script' and 'close_start' in node:
            payload = source[node['open_end']:node['close_start']]
            for name, _, _, rows in assignments(payload):
                if name not in ('COURSE_SEARCH', 'BOOK_CATALOG'):
                    continue
                if not isinstance(rows, list):
                    raise CompleteError('invalid embedded search/catalogue data')
                for row in rows:
                    value = row.get('path', '')
                    if name == 'COURSE_SEARCH':
                        search_rows += 1
                        if not value.startswith('#'):
                            dynamic_paths.append(value)
                            continue
                    # This is Atelier's existing resolve() contract.
                    if not value.startswith('#'):
                        page, _, anchor = value.partition('#')
                        value = '#' + page.removesuffix('.html').replace('/', '--') + ('--' + anchor if anchor else '')
                    if value[1:] not in known:
                        dynamic_paths.append(value)
    if dynamic_paths or not search_rows:
        raise CompleteError('invalid embedded search targets: %r' % dynamic_paths[:8])
    opened_quizzes = sum(n['tag'] == 'details' and 'quiz-answer' in n['attrs'].get('class', '').split()
                         and 'open' in n['attrs'] for n in markup.nodes)
    if opened_quizzes:
        raise CompleteError('quiz answers must be initially collapsed')
    return dict(pages=len(actual), standalone_sections=len(standalone), unique_ids=len(known),
                broken_anchors=0, broken_idrefs=0, runtime_dependencies=0,
                search_rows=search_rows, broken_search_targets=0,
                quiz_answers=sum(n['tag'] == 'details' and 'quiz-answer' in n['attrs'].get('class', '').split()
                                 for n in markup.nodes),
                open_quiz_answers=opened_quizzes)


def normalized(source, *, omit_pager=False):
    if omit_pager:
        nodes = Markup(source).nodes
        source = splice(source, [(n['start'], n['end'], '') for n in nodes
                                 if n['tag'] == 'nav' and 'pager' in n['attrs'].get('class', '').split()
                                 and 'end' in n])
    # Token normalization ignores HTML serializer spelling and formatting only.
    parser = Markup(source)
    text = ' '.join(' '.join(parser.text).split())
    tokens = [(n['tag'], tuple(sorted((k, v or '') for k, v in n['attrs'].items()))) for n in parser.nodes]
    return text, tokens


def diagnose(builder, output):
    rebuilt = complete_strings.CompleteIndex(output)
    current = {p['attrs']['data-book-page']: p for p in rebuilt.sections if 'data-book-page' in p['attrs']}
    differences, matches = [], 0
    for old in builder.old_index.sections:
        page = old['attrs'].get('data-book-page')
        if not page:
            continue
        new = current[page]
        before = builder.original[old['open_end']:old['close_start']]
        after = output[new['open_end']:new['close_start']]
        old_text, old_tags = normalized(before)
        new_text, new_tags = normalized(after)
        if (old_text, old_tags) == (new_text, new_tags):
            matches += 1
            continue
        old_without_pager = normalized(before, omit_pager=True)
        new_without_pager = normalized(after, omit_pager=True)
        same_text_without_pager = old_without_pager[0] == new_without_pager[0]
        changes = []
        for operation, a, b, c, d in difflib.SequenceMatcher(None, old_text.split(), new_text.split(), autojunk=False).get_opcodes():
            if operation != 'equal':
                changes.append(dict(old=' '.join(old_text.split()[max(0, a-5):min(len(old_text.split()), b+5)])[:240],
                                    current=' '.join(new_text.split()[max(0, c-5):min(len(new_text.split()), d+5)])[:240]))
                if len(changes) == 3:
                    break
        differences.append(dict(page=page, text_changed=old_text != new_text,
                                structure_changed=old_tags != new_tags,
                                pager_only=old_text != new_text and same_text_without_pager,
                                nonpager_text_changed=not same_text_without_pager,
                                classification=('current-pager-drift' if old_text != new_text and same_text_without_pager
                                                else 'current-page-text-drift' if old_text != new_text
                                                else 'markup-or-reference-difference'), examples=changes))
    return dict(normalization='HTML start-tag attributes sorted; entities decoded; text whitespace collapsed; '
                              'no teaching text or numeric token removed',
                normalized_matches=matches, normalized_differences=len(differences),
                pager_text_drift=sum(item['pager_only'] for item in differences),
                nonpager_text_drift=sum(item['nonpager_text_changed'] for item in differences),
                markup_or_reference_only=sum(not item['text_changed'] for item in differences),
                known_source_drift=['index.html CTA: old foundations/01, current foundations/22',
                                    'foundations/05.html pager: current lesson numbers and course-order labels'],
                limitation='The original Chinese continuous edition is stale. Differences are diagnostics, '
                           'not a claim of byte reproduction. Per-article transformation proofs independently '
                           'require current text, code, SVG geometry and disclosure states to be unchanged.',
                differences=differences)


def is_temporary(path):
    return any(path.is_relative_to(root) for root in
               {Path(tempfile.gettempdir()).resolve(), Path('/tmp').resolve()})


def output_path(value, *, default=None):
    path = Path(value).expanduser() if value else default
    if path is None:
        raise CompleteError('Chinese diagnostics require an explicit temporary --output')
    # Resolve authorized destinations before atomic_text's symlink checks;
    # macOS /tmp itself is a system symlink to the same temporary filesystem.
    if path.is_symlink():
        raise CompleteError('output file is a symlink')
    resolved = path.resolve()
    if not is_temporary(resolved) and resolved != ROOT / 'en/complete.html':
        raise CompleteError('output must be en/complete.html or inside the temporary directory')
    return resolved


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lang', default='en')
    parser.add_argument('--output')
    parser.add_argument('--report', help='optional JSON proof/diagnostic file in the temporary directory')
    parser.add_argument('--diagnose-zh', action='store_true')
    parser.add_argument('--check', action='store_true', help='prepare and compare without writing')
    args = parser.parse_args(argv)
    try:
        language = 'zh-CN' if args.diagnose_zh else args.lang
        destination = output_path(args.output, default=ROOT / 'en/complete.html' if language == 'en' else None)
        if language != 'en' and destination == ROOT / 'en/complete.html':
            raise CompleteError('Chinese diagnostic output must be temporary')
        report_path = output_path(args.report) if args.report else None
        if report_path and not is_temporary(report_path):
            raise CompleteError('reports must be temporary')
        if report_path == destination:
            raise CompleteError('HTML and report destinations must differ')
        builder = Builder(lang=language)
        output, report = builder.prepare()
        if args.diagnose_zh:
            report['chinese_comparison'] = diagnose(builder, output)
        if args.check:
            if not destination.is_file() or destination.read_text(encoding='utf-8') != output:
                raise CompleteError('continuous output is missing or stale: %s' % destination)
        else:
            complete_strings.atomic_text(destination, output)
        if report_path and not args.check:
            complete_strings.atomic_text(report_path, json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({k: v for k, v in report.items() if k not in
                          ('article_proofs', 'input_sha256', 'chinese_comparison', 'localized_resource_mirrors',
                           'added_resources', 'diagnostic_search_repairs')},
                         ensure_ascii=False))
        if args.diagnose_zh:
            comparison = report['chinese_comparison']
            print('Chinese normalization: %d matched / %d different; see %s' %
                  (comparison['normalized_matches'], comparison['normalized_differences'], report_path or 'API report'))
        return 0
    except (CompleteError, runtime_strings.RuntimeStringError, OSError, ValueError, KeyError) as exc:
        print('complete build: %s' % exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
