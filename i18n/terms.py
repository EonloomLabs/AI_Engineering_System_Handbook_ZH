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

# Which strings keep "host" is a list, not a pattern. A pattern for the
# machine sense also caught 宿主机制 ("the harness mechanism"), and excluding
# every string that merely mentions MCP also caught 宿主允许的动作, which is the
# harness. Each entry in the file was checked by reading its context.
EXCEPT = {k: v for k, v in json.loads(
    (ROOT / 'i18n/term-exceptions.json').read_text(encoding='utf-8')).items()
    if not k.startswith('_')}


def harness(en):
    return ''.join(part if part.startswith('<') else harness_prose(part)
                   for part in re.split(r'(<[^>]+>)', en))


def harness_prose(en):
    out = re.sub(r'\bhosts\b', 'harnesses', en)
    out = re.sub(r'\bhost\b', 'harness', out)
    out = re.sub(r'\bHosts\b', 'Harnesses', out)
    out = re.sub(r'\bHost\b', 'Harness', out)
    return out.replace('harness program', 'harness').replace('Harness program', 'Harness')


def main():
    D = json.loads(TABLE.read_text(encoding='utf-8'))
    t = D['s']
    changed, kept = [], []
    subagents = 0
    for k, v in t.items():
        en = v.get(LANG)
        if not en:
            continue
        out = en
        if '宿主' in k:
            if k in EXCEPT:
                if re.search(r'\bharness', en, re.I):
                    kept.append((k, en))      # wrongly converted earlier
            else:
                out = harness(en)
        if LANG == 'en':
            normalized = ''.join(
                part if part.startswith('<') else re.sub(
                    r'\b(sub)(agents?)\b', r'\1-\2', part, flags=re.I)
                for part in re.split(r'(<[^>]+>)', out))
            subagents += normalized != out
            out = normalized
        if out != en:
            changed.append((k, en, out))
            if FIX:
                v[LANG] = out
    if FIX and changed:
        TABLE.write_text(json.dumps(D, ensure_ascii=False), encoding='utf-8')
    print('[%s] 已定术语需统一: %d 条%s' %
          (LANG, len(changed), '（已改）' if FIX else '待改'))
    print('[%s] 其中 subagent → sub-agent: %d 条' % (LANG, subagents))
    if kept:
        print('应保留 host 但已被改成 harness 的: %d 条' % len(kept))
        for k, en in kept[:5]:
            print('   zh: %s' % k[:60])
            print('   en: %s' % en[:80])
    return 0


if __name__ == '__main__':
    sys.exit(main())
