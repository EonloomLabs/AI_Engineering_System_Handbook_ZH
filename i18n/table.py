"""The book's one translation table: each distinct Chinese string, translated once.

The same sentence recurs across pages - the book rail repeats all 262 titles on
every page - so translating per page would mean the same string rendered many
times, inconsistently, at several times the work. Keying by the string instead
makes identical Chinese come out as identical English everywhere, by
construction, and cuts the job by two thirds.

Run: python3 i18n/table.py build     rebuild the table, keeping existing en
     python3 i18n/table.py status
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNITS = ROOT / 'i18n/units'
TABLE = ROOT / 'i18n/table.json'
CJK = re.compile(r'[一-鿿]')
TAG = re.compile(r'<[^>]+>')


def build():
    prev = json.loads(TABLE.read_text(encoding='utf-8')) if TABLE.exists() else {}
    old = prev.get('s', {})
    # An id, once given out, must never move: a translator's file is keyed by
    # it. New strings take the next free one, and a string that disappears
    # keeps its id reserved so a later rebuild cannot reuse it.
    next_id = prev.get('next_id', 0)
    seen = {}
    for p in sorted(UNITS.glob('*.json')):
        d = json.loads(p.read_text(encoding='utf-8'))
        for it in d['items']:
            e = seen.setdefault(it['zh'], {'n': 0, 'pages': set()})
            e['n'] += 1
            e['pages'].add(d['page'])
    out = {}
    fresh = 0
    for k, v in seen.items():
        was = old.get(k, {})
        i = was.get('id')
        if i is None:
            i, next_id, fresh = next_id, next_id + 1, fresh + 1
        row = {'id': i, 'n': v['n'], 'p': len(v['pages'])}
        for lang in ('en', 'ja', 'es', 'vi'):
            if was.get(lang):
                row[lang] = was[lang]
        out[k] = row
    TABLE.write_text(json.dumps({'s': out, 'next_id': next_id},
                                ensure_ascii=False), encoding='utf-8')
    print('新增 %d 条字符串（id 自 %d 起）' % (fresh, next_id - fresh))
    status()


def status():
    t = json.loads(TABLE.read_text(encoding='utf-8'))['s']
    done = sum(1 for v in t.values() if v.get('en'))
    ch = sum(len(CJK.findall(k)) for k in t)
    chd = sum(len(CJK.findall(k)) for k, v in t.items() if v.get('en'))
    rich = sum(1 for k in t if TAG.search(k))
    print('去重字符串 %s 条（含行内标签 %s 条）| 中文 %s 字' %
          (format(len(t), ','), format(rich, ','), format(ch, ',')))
    print('已译 %s 条 / %s 字  (%.1f%%)' %
          (format(done, ','), format(chd, ','), 100 * chd / ch if ch else 0))
    # how much page text each tier of the table unlocks
    tiers = [(1, 1), (2, 5), (6, 50), (51, 10 ** 9)]
    print()
    print('%-14s %10s %12s' % ('出现次数', '字符串', '占全站实例'))
    inst = sum(v['n'] for v in t.values())
    for lo, hi in tiers:
        g = [v for v in t.values() if lo <= v['n'] <= hi]
        print('%-14s %10s %11.1f%%' % ('%d–%s 次' % (lo, hi if hi < 10 ** 9 else '∞'),
                                       format(len(g), ','), 100 * sum(v['n'] for v in g) / inst))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    {'build': build, 'status': status}[cmd]()
