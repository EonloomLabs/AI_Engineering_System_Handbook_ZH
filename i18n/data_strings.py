"""The JS data files' prose, in and out of the one translation table.

visual-data.js and model-data.js are not derived from the pages - they hold the
figure lessons' own explanations, the step captions, the term definitions and
the why/how/risk/verify notes a reader actually reads. So they are translated
through the same table as the HTML, which is what keeps a figure's caption and
the lesson text around it using the same words.

Their svg and mobileSvg fields are figure markup, not prose: the labels inside
them are handled by figure_strings after this script. This script leaves them
alone. Localized MODEL_FRAMES also retain sourceGroup as an internal selector
key, since the original HTML's data-allowed-groups values are machine data.

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


def read(rel, root=None):
    s = ((ROOT if root is None else root) / rel).read_text(encoding='utf-8')
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


def source_counts(root=None):
    """Current JS prose occurrences and source files, excluding SVG markup."""
    seen = {}

    def note(s):
        e = seen.setdefault(s, {'n': 0, 'pages': set()})
        e['n'] += 1
        e['pages'].add(rel)
        return s

    for rel in FILES:
        _, d = read(rel, root)
        walk(d, None, note)
    return seen


def collect():
    import table

    document = json.loads(TABLE.read_text(encoding='utf-8'))
    seen = source_counts()
    added = sum(s not in document['s'] for s in seen)
    table.reconcile(document, table.source_counts(ROOT / 'i18n/units'),
                    table.auxiliary_counts(ROOT))
    TABLE.write_text(json.dumps(document, ensure_ascii=False), encoding='utf-8')
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

    prepared = []
    for rel in FILES:
        g, d = read(rel)
        translated = walk(d, None, tr)
        if g == 'MODEL_FRAMES':
            for original, frame in zip(d, translated):
                frame['sourceGroup'] = original['group']
        prepared.append((Path(rel).name,
                         'window.%s=%s;\n' % (g, json.dumps(translated, ensure_ascii=False))))
    if miss:
        print('缺译文 %s 条，例: %s' % (format(len(set(miss)), ','), list(dict.fromkeys(miss))[0][:50]))
        return 1
    out = ROOT / lang / 'assets'
    out.mkdir(parents=True, exist_ok=True)
    for name, payload in prepared:
        (out / name).write_text(payload, encoding='utf-8')
    print('%s/assets/visual-data.js 与 model-data.js 已写出' % lang)
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'collect'
    lang = next((a.split('=', 1)[1] for a in sys.argv[2:] if a.startswith('--lang=')), 'en')
    sys.exit({'collect': collect, 'write': lambda: write(lang)}[cmd]() or 0)
