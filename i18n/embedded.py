"""Check a link's text against the heading it points at.

A chapter's table of contents is one string holding every heading on the page,
each as its own <a> text. Those headings are table entries in their own right,
so each has a canonical translation - and a reader sees both: the TOC entry and
the heading it links to. Translated independently, they disagree, which reads
as two different headings.

Comparison is positional, not by substring: both the Chinese and the English
are split on their tags, which the tag check already guarantees are the same,
so segment i of one lines up with segment i of the other. That makes this
exact, unlike looking for the piece inside the host - English has to reword a
fragment it absorbs into a sentence, but a link's text stands on its own.

Run: python3 i18n/embedded.py [--lang=en] [--fix]
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / 'i18n/table.json'
LANG = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--lang=')), 'en')
FIX = '--fix' in sys.argv
TAG = re.compile(r'<[^>]+>')


def segs(s):
    return [x.strip() for x in TAG.split(s)]


def main():
    D = json.loads(TABLE.read_text(encoding='utf-8'))
    t = D['s']
    done = {k: v[LANG] for k, v in t.items() if v.get(LANG)}

    bad = []
    for host, host_en in done.items():
        if '<' not in host:
            continue
        a, b = segs(host), segs(host_en)
        if len(a) != len(b):
            continue                       # tags reordered; not comparable
        for i, zh in enumerate(a):
            if len(zh) < 6 or zh not in done or zh == host:
                continue
            want = done[zh].strip()
            if b[i] and b[i] != want:
                bad.append((host, i, zh, want, b[i]))

    print('[%s] 链接文本与其指向的条目不一致: %d 处\n' % (LANG, len(bad)))
    for host, i, zh, want, got in bad[:14]:
        print('  片段 zh : %s' % zh[:66])
        print('  条目 en : %s' % want[:66])
        print('  链接 en : %s' % got[:66])
        print()
    if FIX:
        n = 0
        for host, i, zh, want, got in bad:
            cur = t[host][LANG]
            a, b = segs(host), segs(cur)
            if len(a) != len(b) or b[i] != got:
                continue
            # rebuild the host, replacing only segment i
            parts = TAG.split(cur)
            tags = TAG.findall(cur)
            lead = parts[i][:len(parts[i]) - len(parts[i].lstrip())]
            trail = parts[i][len(parts[i].rstrip()):]
            parts[i] = lead + want + trail
            out = parts[0]
            for j, tg in enumerate(tags):
                out += tg + parts[j + 1]
            t[host][LANG] = out
            n += 1
        TABLE.write_text(json.dumps(D, ensure_ascii=False), encoding='utf-8')
        print('统一 %d 处' % n)
    return 0


if __name__ == '__main__':
    sys.exit(main())
