"""Merge extracted runs into translation units.

A text node split by inline markup ("批次<strong>与</strong>形状") is three runs
but one sentence. Translated piecewise it comes out with Chinese word order, so
adjacent runs separated only by inline tags are merged into a single unit whose
zh carries that markup. The translator may then move the tags; apply.py still
splices by byte offset, so everything outside a unit stays bit-for-bit.

Run: python3 i18n/units.py            (rebuild all)
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Tags that sit inside a sentence. A gap made only of these (and whitespace)
# does not end the sentence, so the runs on either side belong to one unit.
INLINE = re.compile(
    r'^(?:</?(?:strong|b|em|i|code|span|a|sub|sup|abbr|kbd|small|u|mark|br|'
    r'time|cite|q|var|samp|dfn|bdi|wbr)\b[^>]*>|\s)+$')
TAG = re.compile(r'<[^>]+>')
# A run of Chinese punctuation on its own translates deterministically, so it
# stays its own unit instead of being folded into the sentence beside it.
# Merging it would turn an already-translated phrase into a new composite
# string and throw that translation away.
PUNCT_ONLY = re.compile(r'^[\s。；，、：？]+$')


def merge(doc, items):
    units, buf = [], []

    def flush():
        if not buf:
            return
        s, e = buf[0]['start'], buf[-1]['end']
        units.append({'i': len(units), 'start': s, 'end': e,
                      'kind': buf[0]['kind'] if len(buf) == 1 else 'rich',
                      'zh': doc[s:e]})
        buf.clear()

    for it in items:
        if it['kind'] != 'text':
            flush()
            units.append({'i': len(units), 'start': it['start'], 'end': it['end'],
                          'kind': it['kind'], 'zh': it['zh']})
            continue
        if PUNCT_ONLY.match(it['zh']):
            flush()
            units.append({'i': len(units), 'start': it['start'], 'end': it['end'],
                          'kind': 'punct', 'zh': it['zh']})
            continue
        if buf and INLINE.match(doc[buf[-1]['end']:it['start']]):
            buf.append(it)
        else:
            flush()
            buf.append(it)
    flush()
    return units


def main():
    out = ROOT / 'i18n/units'
    out.mkdir(exist_ok=True)
    tot = rich = 0
    for p in sorted((ROOT / 'i18n/content').glob('*.json')):
        d = json.loads(p.read_text(encoding='utf-8'))
        doc = (ROOT / d['page']).read_text(encoding='utf-8')
        u = merge(doc, d['items'])
        # the spliced text must still cover exactly what was extracted
        for it in u:
            assert doc[it['start']:it['end']] == it['zh'], d['page']
        (out / p.name).write_text(json.dumps(
            {'page': d['page'], 'items': u}, ensure_ascii=False), encoding='utf-8')
        tot += len(u)
        rich += sum(1 for x in u if x['kind'] == 'rich')
    print('%s 个翻译单元，其中 %s 个含行内标签' %
          (format(tot, ','), format(rich, ',')))


if __name__ == '__main__':
    main()
