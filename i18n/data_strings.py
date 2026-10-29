"""The JS data files' prose, in and out of the one translation table.

visual-data.js and model-data.js are not derived from the pages - they hold the
figure lessons' own explanations, the step captions, the term definitions and
the why/how/risk/verify notes a reader actually reads. So they are translated
through the same table as the HTML, which is what keeps a figure's caption and
the lesson text around it using the same words.

Their svg and mobileSvg fields are figure markup, not prose: the labels inside
them are laid out by the figure generators, which measure text width, so they
are regenerated rather than translated in place. This script leaves them alone.

Run: python3 i18n/data_strings.py collect          add their strings to the table
     python3 i18n/data_strings.py write --lang=en  write <lang>/assets/*.js
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / 'i18n/table.json'
CJK = re.compile(r'[一-鿿]')
FILES = ('assets/visual-data.js', 'assets/model-data.js')
# Figure markup: laid out by the generators, so never spliced as text.
SKIP = ('svg', 'mobileSvg')


def read(rel):
    s = (ROOT / rel).read_text(encoding='utf-8')
    g = re.findall(r'window\.(\w+)=', s)[0]
    return g, json.loads(re.search(r'window\.' + g + r'=(.*?);\s*$', s, re.S).group(1))


def walk(o, key=None, fn=None):
    """Visit every translatable string, skipping figure markup."""
    if isinstance(o, str):
        return fn(o) if key not in SKIP and CJK.search(o) else o
    if isinstance(o, dict):
        return {k: walk(v, k, fn) for k, v in o.items()}
    if isinstance(o, list):
        return [walk(v, key, fn) for v in o]
    return o


def collect():
    t = json.loads(TABLE.read_text(encoding='utf-8'))['s']
    seen = {}

    def note(s):
        seen[s] = seen.get(s, 0) + 1
        return s

    for rel in FILES:
        _, d = read(rel)
        walk(d, None, note)
    added = 0
    for s, n in seen.items():
        if s in t:
            t[s]['n'] += n
        else:
            t[s] = {'en': None, 'n': n, 'p': 1}
            added += 1
    TABLE.write_text(json.dumps({'s': t}, ensure_ascii=False), encoding='utf-8')
    print('数据文件散文 %s 条（新增 %s 条到表）| %s 字' %
          (format(len(seen), ','), format(added, ','),
           format(sum(len(CJK.findall(s)) for s in seen), ',')))


def write(lang):
    t = json.loads(TABLE.read_text(encoding='utf-8'))['s']
    miss = []

    def tr(s):
        v = (t.get(s) or {}).get(lang)
        if not v:
            miss.append(s)
            return s
        return v

    out = ROOT / lang / 'assets'
    out.mkdir(parents=True, exist_ok=True)
    for rel in FILES:
        g, d = read(rel)
        (out / Path(rel).name).write_text(
            'window.%s=%s;\n' % (g, json.dumps(walk(d, None, tr), ensure_ascii=False)),
            encoding='utf-8')
    print('%s/assets/visual-data.js 与 model-data.js 已写出' % lang)
    if miss:
        print('缺译文 %s 条，例: %s' % (format(len(set(miss)), ','), list(dict.fromkeys(miss))[0][:50]))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'collect'
    lang = next((a.split('=', 1)[1] for a in sys.argv[2:] if a.startswith('--lang=')), 'en')
    {'collect': collect, 'write': lambda: write(lang)}[cmd]()
