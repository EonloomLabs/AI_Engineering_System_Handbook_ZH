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


def source_counts(units):
    """Current HTML occurrences, independent of the previous table counts."""
    seen = {}
    for p in sorted(units.glob('*.json')):
        d = json.loads(p.read_text(encoding='utf-8'))
        for it in d['items']:
            e = seen.setdefault(it['zh'], {'n': 0, 'pages': set()})
            e['n'] += 1
            e['pages'].add(d['page'])
    return seen


def reconcile(document, html, data):
    """Keep permanent identity and translations; replace all source counts."""
    old = document.get('s', {})
    next_id = max(document.get('next_id', 0),
                  max((v['id'] for v in old.values() if v.get('id') is not None),
                      default=-1) + 1)
    first_id = next_id
    out = {}
    # Retired entries reserve their ids but have no active occurrences.
    # Legacy data-only entries may lack ids and must be numbered as well.
    for k in dict.fromkeys((*old, *html, *data)):
        row = dict(old.get(k, {}))
        if row.get('id') is None:
            row['id'], next_id = next_id, next_id + 1
        h = html.get(k, {'n': 0, 'pages': set()})
        d = data.get(k, {'n': 0, 'pages': set()})
        row.update(n=h['n'] + d['n'], p=len(h['pages'] | d['pages']),
                   data_n=d['n'])
        out[k] = row
    document.update(s=out, next_id=next_id)
    return len(out) - len(old), first_id


def auxiliary_counts(root):
    """Original JS prose plus explicitly collected localization sources."""
    import importlib
    import data_strings

    counts = data_strings.source_counts(root)
    # The config owns category source labels only. Their translations share
    # the same permanent table identities as HTML and runtime occurrences.
    catalogue = 'i18n/catalog-kinds.json'
    kinds = json.loads((root / catalogue).read_text(encoding='utf-8'))
    for text in kinds:
        if text.startswith('_'):
            continue
        row = counts.setdefault(text, {'n': 0, 'pages': set()})
        row['n'] += 1
        row['pages'].add(catalogue)
    for name, registry in [('runtime_strings', 'runtime-registry.json'),
                           ('figure_strings', 'figure-registry.json'),
                           ('complete_strings', 'complete-registry.json')]:
        if not (root / 'i18n' / registry).is_file():
            continue
        module = importlib.import_module(name)
        for text, contribution in module.source_counts(root).items():
            row = counts.setdefault(text, {'n': 0, 'pages': set()})
            row['n'] += contribution['n']
            row['pages'].update(contribution['pages'])
    return counts


def build():
    prev = json.loads(TABLE.read_text(encoding='utf-8')) if TABLE.exists() else {}
    fresh, first_id = reconcile(prev, source_counts(UNITS),
                                auxiliary_counts(ROOT))
    TABLE.write_text(json.dumps(prev, ensure_ascii=False), encoding='utf-8')
    print('新增 %d 条字符串（id 自 %d 起）' % (fresh, first_id))
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
                                       format(len(g), ','), 100 * sum(v['n'] for v in g) / inst if inst else 0))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    {'build': build, 'status': status}[cmd]()
