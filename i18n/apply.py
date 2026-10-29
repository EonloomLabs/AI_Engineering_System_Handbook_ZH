"""Build en/<page> from the Chinese page plus the translation table.

Splices by the byte offsets recorded at extraction, in reverse order so each
offset stays valid. Everything not covered by a unit is copied bit-for-bit:
tags, attributes, numbers, code, SVG, anchors and data keys all survive
untouched, which is why a page's figures and worked numbers cannot drift.

Three things happen besides the splice:
  - elements carrying data-i18n get their Chinese fallback replaced with the
    reviewed English from the interface bundle, so the page reads English
    before the runtime swaps anything and still does if its script fails;
  - references out of en/ gain one '../', since en/ mirrors only the HTML;
  - lang and the i18n-scope note are corrected for an English page.

Run: python3 i18n/apply.py <page.html> [...]   (omit for every ready page)
     python3 i18n/apply.py --verify            round-trip with zh, must match
"""
import json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNITS = ROOT / 'i18n/units'
VERIFY = '--verify' in sys.argv
LANG = 'en'
TAG = re.compile(r'<[^>]+>')
CJK = re.compile(r'[一-鿿]')

LOCALISED = {'assets/catalog.js', 'assets/search-data.js',
             'assets/visual-data.js', 'assets/model-data.js'}
REF = re.compile(r'(?P<a>\b(?:src|href)=")(?P<u>[^"]+)(?P<b>")')


def bundle():
    d = (ROOT / 'assets/i18n-data.js').read_text(encoding='utf-8')
    s = json.loads(re.search(r'window\.I18N_STRINGS=(\{.*?\});\s*$', d, re.S | re.M).group(1))
    return s[LANG]


def overrides():
    """Per-page exceptions to the one-translation-per-string rule.

    Keyed by page then Chinese string; see i18n/overrides.json for why each
    exists. Everything else stays keyed by string alone, which is what makes
    the same sentence read identically across all 262 pages.
    """
    f = ROOT / 'i18n/overrides.json'
    if not f.exists():
        return {}
    return {k: v for k, v in json.loads(f.read_text(encoding='utf-8')).items()
            if not k.startswith('_')}


def splice(doc, items, table, field=None, over=None):
    out = doc
    for it in sorted(items, key=lambda x: x['start'], reverse=True):
        if field == 'zh':
            val = it['zh']
        else:
            o = (over or {}).get(it['zh'])
            val = (o or {}).get(LANG) if o else (table.get(it['zh'], {}) or {}).get(LANG)
        if val is None:
            continue
        assert doc[it['start']:it['end']] == it['zh'], \
            'offset drift at %d — re-run extract.py' % it['start']
        if it['kind'].startswith('attr:'):
            val = val.replace('"', '&quot;')
        out = out[:it['start']] + val + out[it['end']:]
    return out


# An element's leading text, up to its first child. The runtime writes into
# that text node and leaves the children alone, so the static replacement does
# the same: a decorative arrow or a nested note must survive.
EL = re.compile(r'<(?P<n>[\w-]+)(?P<at>[^>]*\bdata-i18n="(?P<k>[^"]+)"[^>]*)>'
                r'(?P<in>[^<]*)')


def chrome(html, en):
    """Replace the Chinese fallback under data-i18n with the reviewed English."""
    left = []

    def el(m):
        v = en.get(m.group('k'))
        if v is None or not CJK.search(m.group('in')):
            return m.group(0)
        return '<%s%s>%s' % (m.group('n'), m.group('at'), v)

    html = EL.sub(el, html)

    def attrs(m):
        tag = m.group(0)
        for pair in m.group(1).split(','):
            a, _, k = pair.partition(':')
            v = en.get(k.strip())
            if not v:
                continue
            tag = re.sub(r'\b%s="[^"]*"' % re.escape(a.strip()),
                         '%s="%s"' % (a.strip(), v.replace('"', '&quot;')), tag, count=1)
        return tag

    html = re.sub(r'<[\w-]+[^>]*\bdata-i18n-attr="([^"]+)"[^>]*>', attrs, html)
    for m in EL.finditer(html):
        if CJK.search(m.group('in')):
            left.append(m.group('k'))
    return html, left


def relink(html, rel, pages):
    """en/ mirrors only the HTML tree, so references out of it gain one '../'."""
    here = Path(rel).parent

    def fix(m):
        u = m.group('u')
        if u.startswith(('http://', 'https://', '//', 'mailto:', 'data:', '#', '/')):
            return m.group(0)
        bare = u.split('#')[0].split('?')[0]
        if not bare:
            return m.group(0)
        target = os.path.normpath(str(here / bare)).replace(os.sep, '/')
        if target in pages or target in LOCALISED:
            return m.group(0)
        return m.group('a') + '../' + u + m.group('b')

    return REF.sub(fix, html)


# Elements that behave as a word in a sentence. sub and sup are excluded on
# purpose: a subscript must stay attached to what it subscripts (d_k, x₁).
WORDISH = r'code|kbd|samp|var|a|strong|em|b|i|span|abbr|dfn|time|cite|q'
SEAM_OPEN = re.compile(r'(?P<l>[A-Za-z0-9)\]])(?P<t><(?:%s)\b[^>]*>)(?P<r>[A-Za-z0-9(\[])' % WORDISH)
SEAM_CLOSE = re.compile(r'(?P<l>[A-Za-z0-9)\]])(?P<t></(?:%s)>)(?P<r>[A-Za-z0-9(\[])' % WORDISH)
OPAQUE = re.compile(r'<(pre|script|style|svg|textarea)\b.*?</\1>', re.S | re.I)
# English always sets a space after punctuation; Chinese does not, so a comma
# or full stop that butts straight into the next inline element loses it:
# "pin the model,<code>Tokenizer</code>", "Basis:<a>tiny_model.py</a>".
# A block element is skipped - the line break supplies the gap - and so is a
# digit, which keeps版本 numbers and decimals intact.
BLOCK = (r'p|div|li|ul|ol|dl|dt|dd|td|th|tr|table|section|article|aside|nav|'
         r'header|footer|h[1-6]|details|summary|figure|figcaption|blockquote|br')
PUNCT_SEAM = re.compile(
    r'(?P<p>[,;:.!?])(?P<t>(?:<(?!/?(?:%s)\b)[^>]+>)+)(?P<r>[A-Za-z])' % BLOCK)
# The same seam where the punctuation itself follows a tag: "…]</code>,<code>[…".
# A decimal or version number cannot straddle a tag, so here the following
# character may be anything - a bracket, a digit, a minus sign.
PUNCT_AFTER_TAG = re.compile(
    r'(?P<l></[\w-]+>)(?P<p>[,;:.!?])(?P<t>(?:<(?!/?(?:%s)\b)[^>]+>)+)(?P<r>[^\s<])' % BLOCK)


def space_seams(html):
    """Put back the space English needs where Chinese needed none.

    Chinese sets no space around an inline element, so a text node ending a
    word runs straight into the <code> or <a> beside it: translated, that
    renders "improvesANNrecall". The gap belongs to the sentence, not to any
    one string, so it is restored here rather than asked of every translator.

    A translation that deliberately attaches - "-style" after WordPiece, "-s"
    after an identifier - starts with punctuation, so it is left alone, and
    pre/script/style/svg are skipped entirely.
    """
    parts, last = [], 0
    for m in OPAQUE.finditer(html):
        parts.append((html[last:m.start()], True))
        parts.append((m.group(0), False))
        last = m.end()
    parts.append((html[last:], True))

    out = []
    for chunk, editable in parts:
        if editable:
            for _ in range(2):          # a seam can need both sides fixed
                chunk = SEAM_OPEN.sub(r'\g<l> \g<t>\g<r>', chunk)
                chunk = SEAM_CLOSE.sub(r'\g<l>\g<t> \g<r>', chunk)
            chunk = PUNCT_SEAM.sub(r'\g<p> \g<t>\g<r>', chunk)
            chunk = PUNCT_AFTER_TAG.sub(r'\g<l>\g<p> \g<t>\g<r>', chunk)
        out.append(chunk)
    return ''.join(out)


def head(html):
    html = re.sub(r'(<html[^>]*\blang=")[^"]*(")', r'\1en\2', html, count=1)
    return re.sub(r'(<meta content=")[^"]*(" name="i18n-scope"/?>)',
                  r'\1English edition: interface and lesson text are translated '
                  r'from the Simplified Chinese original.\2', html, count=1)


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    table = json.loads((ROOT / 'i18n/table.json').read_text(encoding='utf-8'))['s']
    over_all = overrides()
    en = bundle()
    files = sorted(UNITS.glob('*.json'))
    pages = {json.loads(p.read_text(encoding='utf-8'))['page'] for p in files}
    want = set(args) if args else None
    wrote = skip = 0
    for p in files:
        d = json.loads(p.read_text(encoding='utf-8'))
        rel = d['page']
        if want and rel not in want:
            continue
        doc = (ROOT / rel).read_text(encoding='utf-8')
        if VERIFY:
            if splice(doc, d['items'], table, 'zh') != doc:
                print('%-38s 往返不一致' % rel)
                return 1
            wrote += 1
            continue
        left = [it for it in d['items'] if not (table.get(it['zh']) or {}).get(LANG)]
        if left:
            skip += 1
            continue
        html, pending = chrome(splice(doc, d['items'], table,
                                     over=over_all.get(rel)), en)
        html = head(relink(html, rel, pages))
        if LANG != 'ja':
            html = space_seams(html)
        out = ROOT / LANG / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding='utf-8')
        wrote += 1
    if VERIFY:
        print('验证 %d 页 | 往返不一致: 0' % wrote)
    else:
            print('生成 %d 页 -> %s/ | 因缺译文跳过 %d 页' % (wrote, LANG, skip))
    return 0


if __name__ == '__main__':
    argv = sys.argv[1:]
    for a in list(argv):
        if a.startswith('--lang='):
            LANG = a.split('=', 1)[1]
            argv.remove(a)
    sys.exit(main(argv))
