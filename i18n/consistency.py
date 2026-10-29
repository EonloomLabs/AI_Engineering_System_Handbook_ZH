"""Find recurring Chinese phrases that have been translated two different ways.

Translation is keyed by string, so an identical string always comes out
identically. But many strings share a frame - "关键边界：…", "不要混淆：…",
"回到 第NN课 的完整讲解 →" - and those frames were translated by different
people in different batches. A reader meets them side by side in the rail and
in the lesson text, so a frame rendered two ways reads as two different things.

This groups translated strings by their leading Chinese phrase and reports the
frames whose translations disagree, with how often each rendering was used, so
the majority can be applied to the rest.

Run: python3 i18n/consistency.py [--lang=en] [--fix]
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / 'i18n/table.json'
LANG = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--lang=')), 'en')
FIX = '--fix' in sys.argv
# A frame ends at a Chinese colon or full stop: what follows varies, what
# precedes is the phrase shared across pages.
HEAD = re.compile(r'^([^：。]{2,24}[：。])')


def main():
    D = json.loads(TABLE.read_text(encoding='utf-8'))
    t = D['s']
    groups = defaultdict(list)
    for zh, v in t.items():
        e = v.get(LANG)
        if not e:
            continue
        m = HEAD.match(zh.strip())
        if m:
            groups[m.group(1)].append((zh, e))

    split = []
    for zh_head, rows in groups.items():
        if len(rows) < 3:
            continue
        # the translated head is everything up to the first ':' or '.'
        heads = Counter()
        for _, e in rows:
            hm = re.match(r'^(.{2,60}?[:.])', e.strip())
            if hm:
                heads[hm.group(1).strip()] += 1
        if len(heads) > 1:
            split.append((sum(heads.values()), zh_head, heads))

    split.sort(reverse=True)
    print('[%s] 共用中文模板 %d 组，其中 %d 组译法不一致\n' %
          (LANG, len(groups), len(split)))
    changed = 0
    for n, zh_head, heads in split[:25]:
        best, cnt = heads.most_common(1)[0]
        print('%-22s ×%-4d' % (zh_head, n))
        for h, c in heads.most_common():
            print('      %-52s ×%d%s' % (h[:52], c, '  ← 取此' if h == best and FIX else ''))
        if FIX and cnt > 1:
            for zh, e in groups[zh_head]:
                hm = re.match(r'^(.{2,60}?[:.])', e.strip())
                if hm and hm.group(1).strip() != best:
                    t[zh][LANG] = best + e.strip()[len(hm.group(1)):]
                    changed += 1
    if FIX:
        TABLE.write_text(json.dumps(D, ensure_ascii=False), encoding='utf-8')
        print('\n统一 %d 条' % changed)
    return 0


sys.exit(main())
