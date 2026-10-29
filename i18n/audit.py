"""Account for every Chinese character left in an en/ page, by cause.

The earlier interface round was reported done while chrome strings were still
Chinese, because the check only proved the wiring existed. This counts what is
actually left and names the reason, so "done" is a number, not an impression.

Run: python3 i18n/audit.py [en/page.html ...]
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CJK = re.compile(r'[一-鿿]')
SKIP = re.compile(r'<(script|style|svg)\b', re.I)


def spans(doc):
    """Yield (kind, text) for every Chinese-bearing region, with its cause."""
    out = []
    i = 0
    n = len(doc)
    while i < n:
        lt = doc.find('<', i)
        if lt < 0:
            lt = n
        if lt > i:
            txt = doc[i:lt]
            if CJK.search(txt):
                out.append(('text', txt.strip()))
        if lt >= n:
            break
        m = SKIP.match(doc, lt)
        if m:
            close = '</%s>' % m.group(1).lower()
            end = doc.lower().find(close, lt)
            end = n if end < 0 else end + len(close)
            body = doc[lt:end]
            if CJK.search(body):
                out.append(('svg' if m.group(1).lower() == 'svg' else m.group(1).lower(), body))
            i = end
            continue
        gt = doc.find('>', lt)
        if gt < 0:
            break
        tag = doc[lt:gt + 1]
        if CJK.search(tag):
            name = (re.match(r'<\s*/?\s*([\w-]+)', tag) or [None, '?'])[1]
            tagged = 'data-i18n' in tag
            for an, av in re.findall(r'([\w:-]+)="([^"]*)"', tag):
                if CJK.search(av):
                    kind = ('i18n-fallback' if tagged and (an == 'data-i18n' or 'data-i18n-attr' in tag)
                            else 'attr:%s' % an)
                    if name == 'meta':
                        kind = 'meta'
                    out.append((kind, av.strip()))
        i = gt + 1
    return out


def main(argv):
    files = argv or sorted(str(p) for p in (ROOT / 'en').rglob('*.html'))
    if not files:
        print('en/ 下没有页面')
        return 0
    agg = {}
    for f in files:
        doc = Path(f).read_text(encoding='utf-8')
        for kind, txt in spans(doc):
            c = len(CJK.findall(txt))
            k = agg.setdefault(kind, [0, 0, []])
            k[0] += c
            k[1] += 1
            if len(k[2]) < 3:
                k[2].append(txt[:62])
    tot = sum(v[0] for v in agg.values())
    print('%d 页 | 残留中文 %s 字\n' % (len(files), format(tot, ',')))
    print('%-16s %8s %7s  %s' % ('来源', '字数', '处数', '样例'))
    for kind, (c, n, ex) in sorted(agg.items(), key=lambda x: -x[1][0]):
        print('%-16s %8s %7d  %s' % (kind, format(c, ','), n, ex[0] if ex else ''))
        for e in ex[1:]:
            print('%-33s %s' % ('', e))
    return 0


sys.exit(main(sys.argv[1:]))
