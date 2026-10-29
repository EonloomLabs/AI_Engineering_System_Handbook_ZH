"""Extract every translatable run in a page, with exact byte offsets.

Covers the whole document - head, header, book rail, article, footer - because
the rail alone carries 60% of the book's Chinese and sits outside <article>.

Two things are deliberately left alone. Code and figures (script, style, pre,
code, kbd, and the inside of svg) must stay exact, per AGENTS.md: numbers,
source refs, anchors, data keys and file paths all live there. And an element
that already draws from the interface catalogue (data-i18n) keeps its key; its
English comes from the reviewed bundle, not from a second translation.

Write-back splices by offset in reverse, so whatever is not extracted is
preserved bit-for-bit.

Run: python3 i18n/extract.py <page.html> [...]  -> i18n/content/<slug>.json
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_ELEMENT = re.compile(r'<(script|style|svg|pre|code|kbd)\b', re.I)
CLOSE = {'script': '</script>', 'style': '</style>', 'svg': '</svg>',
         'pre': '</pre>', 'code': '</code>', 'kbd': '</kbd>'}
HAN = re.compile(r'[一-鿿]')
# Chinese punctuation standing alone between two tags - "。" after a term link,
# "、" between two of them. HAN does not match it, so it used to survive into
# the translated page as full-width Chinese punctuation. Only the marks that
# must change are listed: · and — read correctly in English, and ！ is left out
# because every standalone one is a cell of the worked model's vocabulary.
PUNCT_ONLY = re.compile(r'^[\s。；，、：？]*[。；，、：？][\s。；，、：？]*$')
# A node with no Chinese letters can still carry Chinese punctuation that has
# to change: "（blob ", "call_id、item_id", "Precision=6/8；Recall=6/10". HAN
# misses them and PUNCT_ONLY only matches punctuation on its own, so they used
# to reach the English page with full-width marks in them.
MIXED_PUNCT = re.compile(r'[。；，、：？（）]')
ATTRS = ('title', 'aria-label', 'alt', 'summary', 'placeholder', 'content')
# <meta> prose worth translating; the rest (charset, viewport, keys) is machine data.
META_OK = re.compile(r'name="(description|i18n-scope)"|property="og:(title|description)"'
                     r'|name="twitter:(title|description)"', re.I)
VOID = {'br', 'img', 'input', 'meta', 'link', 'hr', 'source', 'area', 'col', 'wbr'}


def extract(doc):
    """[(start, end, kind, text)] for every translatable run in the document."""
    items, i, n = [], 0, len(doc)
    # Lowercased once: the close-tag search runs thousands of times per page,
    # and lowercasing inside the loop made it quadratic in the document size.
    low = doc.lower()
    stack = []                       # open elements that carry data-i18n
    while i < n:
        lt = doc.find('<', i)
        if lt == -1:
            seg = doc[i:]
            if HAN.search(seg) or PUNCT_ONLY.match(seg) or MIXED_PUNCT.search(seg):
                items.append((i, n, 'text', seg))
            break
        if lt > i:
            seg = doc[i:lt]
            # Text under data-i18n is replaced at load from the catalogue;
            # translating it again would be overwritten, and could disagree.
            if (HAN.search(seg) or PUNCT_ONLY.match(seg)
                    or MIXED_PUNCT.search(seg)) and not stack:
                items.append((i, lt, 'text', seg))
        m = SKIP_ELEMENT.match(doc, lt)
        if m:
            tag = m.group(1).lower()
            # an svg's own aria-label is prose a reader hears; its insides are not
            gt = doc.find('>', lt)
            if tag == 'svg' and gt != -1:
                for am in re.finditer(r'\b(aria-label|title)="([^"]*)"', doc[lt:gt + 1]):
                    if HAN.search(am.group(2)):
                        items.append((lt + am.start(2), lt + am.end(2),
                                      'attr:' + am.group(1), am.group(2)))
            end = low.find(CLOSE[tag], lt)
            i = n if end == -1 else end + len(CLOSE[tag])
            continue
        gt = doc.find('>', lt)
        if gt == -1:
            break
        tag = doc[lt:gt + 1]
        name = (re.match(r'<\s*/?\s*([\w-]+)', tag) or [None, ''])[1].lower()
        if tag.startswith('</'):
            if stack and stack[-1] == name:
                stack.pop()
        else:
            closed = tag.endswith('/>') or name in VOID
            if 'data-i18n=' in tag and not closed:
                stack.append(name)
            # data-i18n governs the element's text only; an attribute is
            # managed solely when data-i18n-attr names it, so the rest still
            # need translating even on a catalogued element.
            for a in ATTRS:
                if a == 'content' and not META_OK.search(tag):
                    continue
                if 'data-i18n-attr' in tag and re.search(r'data-i18n-attr="[^"]*%s:' % a, tag):
                    continue
                for am in re.finditer(r'\b%s="([^"]*)"' % a, tag):
                    if HAN.search(am.group(1)):
                        items.append((lt + am.start(1), lt + am.end(1),
                                      'attr:' + a, am.group(1)))
        i = gt + 1
    # <title> is text, but it sits in head where nothing else is prose
    return sorted(items)


def main(argv):
    out_dir = ROOT / 'i18n/content'
    out_dir.mkdir(parents=True, exist_ok=True)
    total = 0
    for rel in argv:
        doc = (ROOT / rel).read_text(encoding='utf-8')
        items = extract(doc)
        for s, e, k, t in items:
            assert doc[s:e] == t, rel
        payload = {'page': rel, 'items': [
            {'i': m, 'start': s, 'end': e, 'kind': k, 'zh': t}
            for m, (s, e, k, t) in enumerate(items)]}
        slug = rel.replace('/', '__').replace('.html', '.json')
        (out_dir / slug).write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
        total += len(items)
    print('%d 页 | %s runs' % (len(argv), format(total, ',')))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
