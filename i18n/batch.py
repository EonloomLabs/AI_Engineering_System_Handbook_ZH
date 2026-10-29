"""Export slices of the translation table, and ingest the English back.

Two export modes, because the two halves of the book need different context.

  shell   the strings that recur across pages - rail titles, buttons, labels.
          486 of them carry 78% of all instances, so they come first and are
          worth translating together: they are what a reader sees on every page.

  page    one page's remaining strings, in document order. A lesson's prose is
          unique to it, so the page is the context a translator needs.

Ingest validates before writing: no empty line, no Chinese left, and a string
carrying inline HTML must come back with the same tags - it may reorder them,
not drop, add or alter one. A file that fails is rejected whole, so a bad batch
never half-fills the table.

Run: python3 i18n/batch.py export shell
     python3 i18n/batch.py export page <page.html> [...]
     python3 i18n/batch.py ingest <work/file.en.txt> [...]
     python3 i18n/batch.py status [--pages]
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNITS = ROOT / 'i18n/units'
TABLE = ROOT / 'i18n/table.json'
WORK = ROOT / 'i18n/work'
TAG = re.compile(r'<[^>]+>')
MARK = ' [tags]'
GAP = '\u2423'        # visible stand-in for a space at a fragment's edge


CJK = re.compile(r'[一-鿿]')
# Japanese shares its kanji with Chinese, so 'still Chinese' cannot be detected
# that way. Identical prose and long kanji-only text are review signals;
# source-bound Japanese labels and literal units have explicit exceptions.
# Require a kana letter, not punctuation, a voicing/length/iteration mark.
# Includes full-width, small/archaic and half-width kana letters (Unicode 16).
KANA = re.compile(
    r'[\u3041-\u3096\u309f\u30a1-\u30fa\u30ff\u31f0-\u31ff'
    r'\uff66-\uff6f\uff71-\uff9d\U0001b000-\U0001b122'
    r'\U0001b132\U0001b150-\U0001b152\U0001b155\U0001b164-\U0001b167]')
JA_KANJI_TRANSLATIONS = {
    '旧': '旧',  # The same ordinary adjective in Japanese (shell key 30222).
    '图解 Transformer': '図解Transformer',  # Kanji plus the model name (key 348).
    '中间结果 / 新状态': '中間結果 / 新状態',  # Two state labels (key 578).
}
JA_APPROVED = ROOT / 'i18n/ja-approved.json'


class JapaneseApprovalError(ValueError):
    """An unreadable or malformed review file must stop JA validation."""


def _japanese_approvals():
    """Read reviewed exact pairs for validation only, never for generation."""
    try:
        text = JA_APPROVED.read_text(encoding='utf-8')
    except FileNotFoundError:
        return {}  # Optional file: keep the previous checker behavior.
    except (OSError, UnicodeError) as exc:
        raise JapaneseApprovalError('无法读取 %s: %s' % (JA_APPROVED, exc)) from exc
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise JapaneseApprovalError('%s 不是有效 JSON: %s' % (JA_APPROVED, exc)) from exc
    if not isinstance(document, dict) or not isinstance(document.get('pairs'), dict):
        raise JapaneseApprovalError('%s 必须包含 pairs 对象' % JA_APPROVED)
    pairs = document['pairs']
    for source, target in pairs.items():
        if (not isinstance(source, str) or not source.strip()
                or not isinstance(target, str) or not target.strip()):
            raise JapaneseApprovalError('%s 的 source/target 必须是非空字符串' % JA_APPROVED)
    return pairs


def _approved_japanese(source, target, pairs):
    return (JA_KANJI_TRANSLATIONS.get(source.strip()) == target.strip()
            or pairs.get(source) == target)


def approved_japanese(source, target):
    """Read-only exact-pair predicate, also retaining the three built-in pairs.

    External approval is source-and-target exact; the existing built-in pairs
    retain their whitespace compatibility. Invalid review files raise
    JapaneseApprovalError, including when the requested pair is built in.
    """
    pairs = _japanese_approvals()
    if not isinstance(source, str) or not isinstance(target, str):
        return False
    return _approved_japanese(source, target, pairs)


def vocab():
    """The worked model's vocabulary, which stays Chinese in every edition.

    labs/model declares VOCAB = ['PAD','我','爱','学习','你','！','BOS','EOS'],
    and every trained parameter in labs/model/data is indexed by those rows. A
    figure label reading "t=1 · 我" is therefore data, not prose: translating it
    would make the label disagree with run.json and with the weights, and
    AGENTS.md requires an example to be re-run rather than relabelled. So the
    tokens are exempt from the 'still Chinese' check rather than forced through
    it - the check was making translators render the vocabulary as English.
    """
    import json as _j
    try:
        spec = _j.loads((ROOT / 'labs/model/data/run.json').read_text(encoding='utf-8'))['spec']
        return sorted((v for v in spec['vocab'] if CJK.search(v)), key=len, reverse=True)
    except (OSError, KeyError, ValueError) as e:
        print('警告: 读不到模型词表（%s），词表豁免未启用' % e)
        return []


VOCAB = vocab()
# Literal UTF-8 test data, not prose: studies/labs/sse_protocol.py:46 splits
# this file name across streamed argument fragments. Keep its exact bytes.
PRESERVED_FILES = ('中文.py',)
# foundations/23.html's SSE worked example splits the UTF-8 bytes of 学.
# These two exact extracted sources (IDs 15456/15451) describe that byte data;
# 学 is not a generally permitted untranslated prose character.
SOURCE_LITERALS = {
    '后续字节完成“学”': ('学',),
    '，后接两个换行。网络可能在“学”的UTF-8字节中间切开。': ('学',),
    # chapters/04.html:32,36 teacher-forcing target/prefix data (IDs 1914/1915).
    # This independent example does not expand labs/model's shared VOCAB.
    '编程': ('编程',),
    'BOS,我,爱,编程': ('编程',),
    # chapters/15.html:73 Q058's given-token BM25 inputs (ID 6121), checked
    # against example-verification.html's runnable example. Keep complete
    # array syntax, not generic exemptions for these ordinary Chinese words.
    '输入与条件。</strong>文档A=[排除,路径]，B=[排除,排除,路径,缓存]，C=[日志,输出]。N=3，平均长度8/3，k1=1.2，b=0.75；用非负IDF形式ln(1+(N−df+0.5)/(df+0.5))。': (
        'A=[排除,路径]', 'B=[排除,排除,路径,缓存]', 'C=[日志,输出]'),
    # studies/chapters/20.html:32 S20's raw request payload (ID 25885).
    # Native-language explanations may appear outside this exact call.
    '输入与条件。</strong>用户u7仅有项目P1的读取权限，模型请求query(project="P2",text="部署密钥")。': (
        'query(project="P2",text="部署密钥")',),
}


def residual(s, source=''):
    """Remove model vocabulary and data literals bound to their source text."""
    for v in VOCAB:
        s = s.replace(v, '')
    for name in PRESERVED_FILES:
        if name in source:
            s = s.replace(name, '')
    for literal in SOURCE_LITERALS.get(source, ()):
        s = s.replace(literal, '')
    return s


def data_literal(s):
    """A model token/list or a declared file name may stay identical in ja."""
    plain = TAG.sub('', s).strip()
    if plain in VOCAB or plain in PRESERVED_FILES:
        return True
    if not any(v in plain for v in VOCAB):
        return False
    rest = re.sub(r'\b(?:PAD|BOS|EOS|t)\b', '', residual(plain))
    return bool(re.fullmatch(r'[\s\d\[\],，、/／:：;；.·!！+=()（）\-"\'“”‘’]*', rest))


def japanese_unchanged(s):
    """Reviewed same-form Japanese labels, punctuation and literal data."""
    plain = TAG.sub('', s).strip()
    return (data_literal(s) or not CJK.search(plain)
            or JA_KANJI_TRANSLATIONS.get(s.strip()) == s.strip()
            or bool(re.fullmatch(r'(?:第\d+列|\d+(?:\.\d+)?秒)', plain)))


SHELL_MIN = 51          # appears on this many instances or more
LANGS = ('en', 'ja', 'es', 'vi')
LANG = 'en'             # set from argv by main

HEAD = """# {label} — {n} strings — target language: {lang}
# Translate every line into {lang}. Keep the leading "N<TAB>" exactly; N is a table key, not a count.
# [tags] lines carry inline HTML: keep every tag and its attributes unchanged.
#        You may move tags to suit the target language's word order.
# Keep numbers, code, file names and anchors exactly as they are.
# Terminology: i18n/glossary.json is the book's own bilingual glossary - follow it.
"""


def load():
    return json.loads(TABLE.read_text(encoding='utf-8'))['s']


def order(t):
    """Reading order for a listing: most-used first. Not an identity."""
    return sorted(t, key=lambda k: (-t[k]['n'], k))


def ids(t):
    """id -> string, for numbering an export.

    An id is kept across rebuilds, unlike the sort position it replaced, which
    moved whenever a string was added and silently re-pointed keys already
    given out. But ids were reassigned once, in the rebuild that introduced
    them, so a key in a src file written before that does not resolve here.

    That is why ingest never trusts the key: pair() matches a translation to
    its own .src.txt, which records the Chinese for every key it handed out and
    is therefore the authority. Nothing should look a handed-out key up here.
    """
    return {v['id']: k for k, v in t.items()}


def write(name, label, keys, t, idx):
    WORK.mkdir(exist_ok=True)
    # A src file is the contract for work already handed out: overwriting it
    # destroys the record of which string each key stood for, and a finished
    # translation can then no longer be matched to its source.
    dest = WORK / ('%s.%s.src.txt' % (name, LANG))
    if dest.exists():
        print('%-34s 源文件已存在，跳过（如需重发请先删除 %s）' % (label, dest.name))
        return
    lines = [HEAD.format(label=label, n=len(keys), lang=LANG)]
    for k in keys:
        # The raw string is the ingest identity; visible space markers belong
        # only in target text, never in the immutable source contract.
        lines.append('%d\t%s%s' % (idx[k], k, MARK if TAG.search(k) else ''))
    (WORK / ('%s.%s.src.txt' % (name, LANG))).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    ch = sum(len(CJK.findall(k)) for k in keys)
    print('%-34s %5d strings %7s 字 -> i18n/work/%s.%s.src.txt' % (label, len(keys), format(ch, ','), name, LANG))


def export(args):
    t = load()
    idx = {k: t[k]['id'] for k in t}
    if args and args[0] == 'shell':
        keys = [k for k in order(t) if t[k]['n'] >= SHELL_MIN and not t[k].get(LANG)]
        write('shell', 'shell (recurring strings)', keys, t, idx)
        return 0
    if args and args[0] == 'tier':
        lo, hi, per = int(args[1]), int(args[2]), int(args[3]) if len(args) > 3 else 600
        keys = [k for k in order(t) if lo <= t[k]['n'] <= hi and not t[k].get(LANG)]
        for b, i in enumerate(range(0, len(keys), per), 1):
            write('tier%d-%d_%02d' % (lo, hi, b),
                  'tier %d-%d part %d' % (lo, hi, b), keys[i:i + per], t, idx)
        return 0
    if args and args[0] == 'group':
        # One file for several pages: the strings are unique to their page, so
        # no two groups can contain the same string, and a `# page:` line marks
        # where each page's text begins so a translator keeps the context.
        name, pages = args[1], args[2:]
        lines, keys, total = [], [], 0
        for rel in pages:
            slug = rel.replace('/', '__').replace('.html', '')
            d = json.loads((UNITS / (slug + '.json')).read_text(encoding='utf-8'))
            seen, own = set(), []
            for it in d['items']:
                k = it['zh']
                if k in seen or t[k].get(LANG) or t[k]['n'] > 1:
                    continue
                seen.add(k)
                own.append(k)
            if not own:
                continue
            lines.append((rel, own))
            keys += own
            total += sum(len(CJK.findall(k)) for k in own)
        if not keys:
            print('%-34s 已全部有译文' % name)
            return 0
        dest = WORK / ('%s.%s.src.txt' % (name, LANG))
        if dest.exists():
            print('%-34s 源文件已存在，跳过' % name)
            return 0
        WORK.mkdir(exist_ok=True)
        out = [HEAD.format(label=name, n=len(keys), lang=LANG)]
        for rel, own in lines:
            out.append('# page: %s' % rel)
            for k in own:
                out.append('%d\t%s%s' % (idx[k], k, MARK if TAG.search(k) else ''))
        dest.write_text('\n'.join(out) + '\n', encoding='utf-8')
        print('%-22s %2d 页 %5d 条 %7s 字 -> i18n/work/%s' %
              (name, len(lines), len(keys), format(total, ','), dest.name))
        return 0

    # A page batch may be limited to strings unique to that page (max_n=1).
    # Those cannot appear in another page's batch, so several pages can be
    # handed out at once with no string translated twice.
    max_n = SHELL_MIN - 1
    if args and args[0] == 'unique':
        max_n, args = 1, args[1:]
    pages = args[1:] if args and args[0] == 'page' else args
    group, label, chars = [], None, 0
    for rel in pages:
        slug = rel.replace('/', '__').replace('.html', '')
        d = json.loads((UNITS / (slug + '.json')).read_text(encoding='utf-8'))
        keys, seen = [], set()
        for it in d['items']:
            k = it['zh']
            if k in seen or t[k].get(LANG) or t[k]['n'] > max_n:
                continue
            seen.add(k)
            keys.append(k)
        if not keys:
            print('%-34s %s 已全部有译文' % (rel, LANG))
            continue
        write(slug, rel, keys, t, idx)
    return 0


def pair(src, tgt):
    """Match a translation file to the Chinese it was handed, via the src file.

    The src file is the contract: it records, in order, which string each line
    was for. Matching through it means the table can be rebuilt, and strings
    added, without invalidating work already out with a translator. The key in
    the file is then only a cross-check.
    """
    def rows(p):
        out = []
        for ln in Path(p).read_text(encoding='utf-8').splitlines():
            if not ln.strip() or ln.startswith('#'):
                continue
            k, sep, v = ln.partition('\t')
            if not sep or not k.strip().lstrip('-').isdigit():
                continue
            if v.endswith(MARK):
                v = v[:-len(MARK)]          # exactly the marker, not the space before it
            out.append((int(k), v))
        return out

    a, b = rows(src), rows(tgt)
    if len(a) != len(b):
        return None, '行数不符: 源 %d 条，译文 %d 条' % (len(a), len(b))
    ka = [k for k, _ in a]
    kb = [k for k, _ in b]
    if ka == kb:
        how = '按键对齐'
    elif sorted(ka) == sorted(kb):
        m = {k: v for k, v in b}
        b = [(k, m[k]) for k in ka]
        how = '按键重排对齐'
    else:
        how = '按行位置对齐（键已失效）'
    # Space around a fragment is layout, not language: these runs sit against
    # an inline <code> or <strong>, and the gap belongs to the sentence either
    # way. Carrying the source's own leading and trailing whitespace across
    # keeps it exact in every language, and spares the translator an invisible
    # detail they cannot see in the file.
    out = []
    for i in range(len(a)):
        zh, en = a[i][1], b[i][1]
        # A translator may ask for an edge space the Chinese does not have, or
        # drop one it does, by writing ␣ there: Chinese sets no space before an
        # inline <code>, English usually needs one. Without a ␣ the source's own
        # whitespace is carried across, which is right for most fragments and
        # spares the translator an edge they cannot see in the file.
        if GAP in en:
            core = en.strip()
            lead = ' ' if core.startswith(GAP) else ''
            trail = ' ' if core.endswith(GAP) else ''
            out.append((zh, lead + core.strip(GAP).strip() + trail))
            continue
        core = en.strip()
        lead = zh[:len(zh) - len(zh.lstrip())]
        trail = zh[len(zh.rstrip()):]
        out.append((zh, lead + core + trail))
    return out, how


def check(pairs, p, how, t, dry):
    """Validate a batch whole: nothing is written unless every line passes."""
    approvals = _japanese_approvals() if LANG == 'ja' else None
    errs = []
    for i, (zh, v) in enumerate(pairs):
        if not v.strip():
            errs.append('第%d行 空译文' % (i + 1))
        elif LANG == 'ja':
            reviewed = _approved_japanese(zh, v, approvals)
            if v == zh and not japanese_unchanged(zh) and not reviewed:
                errs.append('第%d行 未翻译（与原文相同）' % (i + 1))
            elif (len(zh) >= 6 and not KANA.search(v) and CJK.search(residual(v, zh))
                  and JA_KANJI_TRANSLATIONS.get(zh.strip()) != v.strip() and not reviewed):
                errs.append('第%d行 无假名，疑未翻译' % (i + 1))
        elif CJK.search(residual(v, zh)):
            errs.append('第%d行 仍含中文' % (i + 1))
        for literal in SOURCE_LITERALS.get(zh, ()):
            if zh.count(literal) != v.count(literal):
                errs.append('第%d行 来源数据字面量未原样保留: %s' % (i + 1, literal))
        for name in PRESERVED_FILES:
            if name in zh and zh.count(name) != v.count(name):
                errs.append('第%d行 文件名未原样保留: %s' % (i + 1, name))
        if sorted(TAG.findall(zh)) != sorted(TAG.findall(v)):
            errs.append('第%d行 标签不符 %r -> %r' % (i + 1, TAG.findall(zh), TAG.findall(v)))
    if errs:
        print('%-34s 拒收 (%d): %s' % (p.name, len(errs), '; '.join(errs[:3])))
        return None, how
    print('%-34s %5d 条%s（%s）' % (p.name, len(pairs), '通过校验' if dry else '入表', how))
    return pairs, how


def ingest(files):
    # --check validates without touching the table, so several translators can
    # verify their own batch at the same time without racing on one file.
    dry = '--check' in files
    files = [f for f in files if not f.startswith('--')]
    document = json.loads(TABLE.read_text(encoding='utf-8'))
    t = document['s']
    bad = 0
    for f in files:
        p = Path(f)
        if not p.is_absolute():
            p = WORK / p.name
        if not p.exists():
            print('%-34s 文件不存在' % f)
            bad += 1
            continue
        raw = [ln for ln in p.read_text(encoding='utf-8').splitlines()
               if ln.strip() and not ln.startswith('#') and '\t' in ln]
        keyed = all(ln.split('\t', 1)[0].strip().lstrip('-').isdigit() for ln in raw) if raw else False
        if not keyed:
            # zh<TAB>translation: self-describing, so no src file is needed and
            # no table rebuild can misalign it.
            pairs, how = [], '按中文串对齐'
            errs = []
            for ln in raw:
                zh, _, v = ln.partition('\t')
                if zh not in t:
                    errs.append('源串不在表中: %s' % zh[:28])
                else:
                    core = v.strip()
                    lead = zh[:len(zh) - len(zh.lstrip())]
                    trail = zh[len(zh.rstrip()):]
                    pairs.append((zh, lead + core + trail))
            if errs:
                print('%-34s 拒收 (%d): %s' % (p.name, len(errs), '; '.join(errs[:3])))
                bad += 1
                continue
            pairs, how = check(pairs, p, how, t, dry)
            if pairs is None:
                bad += 1
            elif not dry:
                for zh, v in pairs:
                    t[zh][LANG] = v
            continue

        src = p.with_suffix('').with_suffix('')
        src = WORK / ('%s.%s.src.txt' % (src.name, LANG))
        if not src.exists():
            print('%-34s 找不到对应源文件 %s' % (p.name, src.name))
            bad += 1
            continue
        pairs, how = pair(src, p)
        if pairs is None:
            print('%-34s 拒收: %s' % (p.name, how))
            bad += 1
            continue

        # A source string can legitimately disappear when extraction changes
        # (a punctuation node that now stands alone, a unit that merged), and
        # its translation is then moot. Skipping those beats rejecting a whole
        # batch of good work; anything still in the table is kept.
        gone = [zh for zh, _ in pairs if zh not in t]
        if gone:
            pairs = [(zh, v) for zh, v in pairs if zh in t]
            print('%-34s %d 行源串已不在表中，跳过' % (p.name, len(gone)))
        pairs, how = check(pairs, p, how, t, dry)
        if pairs is None:
            bad += 1
        elif not dry:
            for zh, v in pairs:
                t[zh][LANG] = v
    if not dry:
        TABLE.write_text(json.dumps(document, ensure_ascii=False), encoding='utf-8')
    return 1 if bad else 0


def status(args):
    t = load()
    ch = sum(len(CJK.findall(k)) for k in t)
    chd = sum(len(CJK.findall(k)) for k, v in t.items() if v.get(LANG))
    inst = sum(v['n'] for v in t.values())
    insd = sum(v['n'] for v in t.values() if v.get(LANG))
    print('[%s] 表: %s / %s 条已译 | %s / %s 字 (%.1f%%) | 全站实例覆盖 %.1f%%' % (
        LANG, format(sum(1 for v in t.values() if v.get(LANG)), ','), format(len(t), ','),
        format(chd, ','), format(ch, ','), 100 * chd / ch if ch else 0,
        100 * insd / inst if inst else 0))
    if '--pages' in args:
        rows = []
        for p in sorted(UNITS.glob('*.json')):
            d = json.loads(p.read_text(encoding='utf-8'))
            ks = {it['zh'] for it in d['items']}
            left = sum(1 for k in ks if not t[k].get(LANG))
            rows.append((left, d['page'], len(ks)))
        full = sum(1 for r in rows if r[0] == 0)
        print('页: %d / %d 可生成' % (full, len(rows)))
        for left, pg, n in sorted(rows, reverse=True)[:10]:
            if left:
                print('   %-36s 还缺 %4d / %4d' % (pg, left, n))
    return 0


if __name__ == '__main__':
    argv = sys.argv[1:]
    for a in list(argv):
        if a.startswith('--lang='):
            LANG = a.split('=', 1)[1]
            argv.remove(a)
    assert LANG in LANGS, 'unknown language %r' % LANG
    cmd = argv[0] if argv else 'status'
    try:
        result = {'export': export, 'ingest': ingest, 'status': status}[cmd](argv[1:]) or 0
    except JapaneseApprovalError as exc:
        print('日语核验文件拒收: %s' % exc, file=sys.stderr)
        result = 1
    sys.exit(result)
