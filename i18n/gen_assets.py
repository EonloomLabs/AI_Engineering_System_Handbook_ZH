"""Rebuild the language-specific JS data files for a translated edition.

catalog.js and search-data.js are derived artefacts: the book's own
rebuild_derivatives.py regenerates them from the canonical article HTML rather
than editing them. An edition follows the same rule, so these are built from
the translated pages and never translated as files. That also means the search
index and the rail can never disagree with the page a reader lands on.

visual-data.js and model-data.js hold figure and model labels; they are not
derived from the pages, so they are translated through the table like any other
string and written by gen_data.py.

Run: python3 i18n/gen_assets.py --lang=en
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANG = 'en'
for a in sys.argv[1:]:
    if a.startswith('--lang='):
        LANG = a.split('=', 1)[1]

CJK = re.compile(r'[一-鿿]')
DROP = re.compile(
    r'<(script|style|svg)\b.*?</\1>'
    r'|<details class="quiz-answer".*?</details>'
    r'|<(nav|footer)\b[^>]*class="(?:pager|footer)"[^>]*>.*?</\2>', re.S | re.I)
TAGS = re.compile(r'<[^>]+>')
ENT = {'&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'", '&nbsp;': ' '}


def text_of(html):
    s = DROP.sub(' ', html)
    s = TAGS.sub(' ', s)
    for k, v in ENT.items():
        s = s.replace(k, v)
    return re.sub(r'\s+', ' ', s).strip()


def article(doc):
    m = re.search(r'<article class="(?:article|home-article)">', doc)
    if not m:
        return ''
    return doc[m.end():doc.rindex('</article>')]


def main():
    out = ROOT / LANG / 'assets'
    kinds = {k: v[LANG] for k, v in
             json.loads((ROOT / 'i18n/catalog-kinds.json').read_text(encoding='utf-8')).items()
             if not k.startswith('_')}
    table = json.loads((ROOT / 'i18n/table.json').read_text(encoding='utf-8'))['s']

    # A page's <title> is stored whole, suffix included ("… — AI系统工程"), while
    # catalog.js holds the bare title. Index the bare forms so one lookup finds
    # either, and the catalogue cannot drift from the page it points at.
    SUFFIX = re.compile(r'\s*(?:—|·|-)\s*AI\s*系统工程\s*$')
    bare = {}
    for zh, v in table.items():
        t = v.get(LANG)
        if not t:
            continue
        stem = SUFFIX.sub('', zh)
        if stem != zh:
            bare.setdefault(stem, re.sub(r'\s*(?:—|·|-)\s*AI Systems Engineering\s*$', '', t))

    def tr(s):
        return (table.get(s) or {}).get(LANG) or bare.get(s) or kinds.get(s) or s

    # --- catalog.js: same records, titles and kinds from the table -----------
    src = (ROOT / 'assets/catalog.js').read_text(encoding='utf-8')
    cat = json.loads(re.search(r'=(\[.*\]);?\s*$', src, re.S).group(1))
    missing = []
    for e in cat:
        if CJK.search(e['title']):
            v = tr(e['title'])
            if v == e['title']:
                missing.append(e['title'])
            e['title'] = v
        e['kind'] = tr(e['kind'])
    out.mkdir(parents=True, exist_ok=True)
    (out / 'catalog.js').write_text(
        'window.BOOK_CATALOG=' + json.dumps(cat, ensure_ascii=False) + ';\n', encoding='utf-8')

    # --- search-data.js: rebuilt from the translated pages -------------------
    index = []
    pages = [json.loads(p.read_text(encoding='utf-8'))['page']
             for p in sorted((ROOT / 'i18n/units').glob('*.json'))]
    by_path = {e['path']: e for e in cat}
    built = 0
    for rel in pages:
        f = ROOT / LANG / rel
        if not f.exists():
            continue
        built += 1
        doc = f.read_text(encoding='utf-8')
        body = article(doc)
        meta = by_path.get(rel, {})
        title = meta.get('title') or text_of(re.search(r'<title>(.*?)</title>', doc, re.S).group(1))
        kind = meta.get('kind', '')
        whole = text_of(body)
        if whole:
            index.append({'id': rel[:-5].replace('/', '--'), 'path': rel,
                          'title': title, 'kind': kind, 'text': whole})
        # one entry per heading, carrying the text up to the next heading
        for m in re.finditer(r'<h([23])\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</h\1>', body, re.S):
            lvl, hid, head = m.group(1), m.group(2), text_of(m.group(3))
            nxt = re.search(r'<h[23]\b', body[m.end():])
            chunk = text_of(body[m.end():m.end() + (nxt.start() if nxt else len(body))])
            if len(chunk) < 30:
                continue
            index.append({'title': '%s · %s' % (title, head), 'id': hid, 'kind': kind,
                          'path': '%s#%s' % (rel, hid), 'text': head + '\n' + chunk})
    (out / 'search-data.js').write_text(
        'window.COURSE_SEARCH=' + json.dumps(index, ensure_ascii=False) + ';\n', encoding='utf-8')

    print('%s/assets/catalog.js     %d 条目（%d 条标题缺译文）' % (LANG, len(cat), len(missing)))
    print('%s/assets/search-data.js %s 条索引，来自 %d 页' % (LANG, format(len(index), ','), built))
    if missing:
        print('缺译文的标题:', ', '.join(missing[:6]))


main()
