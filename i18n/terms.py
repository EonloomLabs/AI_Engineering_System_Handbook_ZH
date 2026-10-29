"""Apply the settled house terms, with the sense distinctions they need.

A term ruling is not a blind substitution. 宿主 is the book's own Harness - its
glossary prints "Harness / 宿主执行框架" and defines it as the surrounding
program that organises input, tools, state, permissions and feedback - but the
same two characters carry two other senses the book also uses:

  - MCP's Host, a role in that protocol alongside Client and Server;
  - the machine or kernel a container runs on (宿主内核, 限制宿主影响).

Rendering either of those as "harness" would be wrong, so they are excluded by
the context they appear in rather than fixed up afterwards. This runs safely
any number of times, which a one-off sweep did not.

Run: python3 i18n/terms.py [--lang=en] [--fix]
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / 'i18n/table.json'
LANG = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--lang=')), 'en')
FIX = '--fix' in sys.argv

# The machine/OS sense: a container's kernel, what it can reach.
MACHINE = re.compile(r'宿主(?:内核|机|影响|系统|操作系统|进程空间|环境变量)|限制宿主|隔离宿主|影响宿主')
# MCP names Host, Client and Server as protocol roles.
PROTOCOL = re.compile(r'MCP|Host、|、Host|Host\s*/\s*Client')


def harness(en):
    out = re.sub(r'\bhosts\b', 'harnesses', en)
    out = re.sub(r'\bhost\b', 'harness', out)
    out = re.sub(r'\bHosts\b', 'Harnesses', out)
    out = re.sub(r'\bHost\b', 'Harness', out)
    return out.replace('harness program', 'harness').replace('Harness program', 'Harness')


def main():
    D = json.loads(TABLE.read_text(encoding='utf-8'))
    t = D['s']
    changed, kept = [], []
    for k, v in t.items():
        en = v.get(LANG)
        if not en or '宿主' not in k:
            continue
        if MACHINE.search(k) or PROTOCOL.search(k) or PROTOCOL.search(en):
            if re.search(r'\bharness', en, re.I):
                kept.append((k, en))      # wrongly converted earlier
            continue
        out = harness(en)
        if out != en:
            changed.append((k, en, out))
            if FIX:
                v[LANG] = out
    if FIX and changed:
        TABLE.write_text(json.dumps(D, ensure_ascii=False), encoding='utf-8')
    print('[%s] 宿主 → harness: %d 条%s' %
          (LANG, len(changed), '（已改）' if FIX else '待改'))
    if kept:
        print('应保留 host 但已被改成 harness 的: %d 条' % len(kept))
        for k, en in kept[:5]:
            print('   zh: %s' % k[:60])
            print('   en: %s' % en[:80])
    return 0


if __name__ == '__main__':
    sys.exit(main())
