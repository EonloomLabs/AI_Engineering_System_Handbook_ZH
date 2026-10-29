"""Keep the worked model's vocabulary in Chinese wherever it names a token.

labs/model declares VOCAB = ['PAD','我','爱','学习','你','！','BOS','EOS'] and
every trained parameter under labs/model/data is indexed by those rows. So a
label like "t=1 · 我", a token list like "[我,爱,学习,EOS]", or a vocabulary
mapping like "PAD0、我1、爱2" is data, not prose: rendering it in English makes
the figure disagree with run.json and with the weights, and AGENTS.md requires
an example to be re-run rather than relabelled.

The same four characters are ordinary words elsewhere - 超时告诉你没收到 is
"tells you", 怎样学习一套系统 is "study" - so this does not look for the
character but for the structural cues that mark a token: quoted on its own,
inside a bracketed list, next to an ID, or joined by 、／/ to another token.

This runs as part of the per-batch pass, not as a one-off edit, because a
re-ingest of a translator's file restores whatever that file said. A manual fix
to the table does not survive; this does.

Run: python3 i18n/vocab.py [--lang=en] [--fix]
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / 'i18n/table.json'
LANG = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--lang=')), 'en')
FIX = '--fix' in sys.argv
CJK = re.compile(r'[一-鿿]')


def tokens():
    spec = json.loads((ROOT / 'labs/model/data/run.json').read_text(encoding='utf-8'))['spec']
    return [v for v in spec['vocab'] if CJK.search(v)]


TOK = tokens()
ALT = '|'.join(sorted(map(re.escape, TOK), key=len, reverse=True))
# A token stands for itself, rather than meaning its ordinary word, when it is
# quoted alone, listed in brackets, paired with an ID, or joined to another.
CUE_SHAPES = (
    r'[“"\'「]%s[”"\'」]',
    r'\[[^\]]*%s[^\]]*\]',
    r'%s\s*\d',
    r'%s\s*→',
    r'%s\s*[、／/，]\s*(?:' + ALT + r')',
    r'(?:' + ALT + r')\s*[、／/，]\s*%s',
)


def cued(zh, tok):
    """Whether this token, specifically, is used as a token in this string.

    Asking only whether the string has any cue was wrong: "Q111｜…到底是不是
    “学习”？" quotes 学习 as an ordinary word, and that quote then made the
    checker flag 你 elsewhere in the same sentence.
    """
    t = re.escape(tok)
    return any(re.search(shape % t, zh) for shape in CUE_SHAPES)


# Where a quoted token is the ordinary word, not the model's token. Matched as
# a substring, because a chapter's table of contents embeds the same phrase and
# would otherwise still be flagged. Each was read in context; no cue separates
# the two cases.
ALLOW = {
    'In-Context Learning到底是不是“学习”': ('学习',
        'the quotes question whether in-context learning is learning at all'),
    '你看到的“爱”是一个字符': ('你',
        '你 is the ordinary pronoun here; the 爱 glyph is kept'),
}
# What an English rendering of each token looks like, so a lost glyph is found.
ENGLISH = {
    '我': r'\bI\b',
    '爱': r'\blov(?:e|es|ed|ing)\b',
    '学习': r'\bstud(?:y|ies|ied|ying)\b|\blearning\b',
    '你': r'\byou\b',
}
# Whole frames whose correct rendering is fixed: the frame is translated, the
# token kept. Anything else is reported for a human to word.
FRAMES = [
    (r'^t=(\d+)\s*·\s*(%s)$', 't={0} · {1}'),
    (r'^位置(\d+)\s*·\s*(%s)$', 'position {0} · {1}'),
    (r'^位置(\d+)\s*[:：]\s*(%s)$', 'position {0}: {1}'),
    (r'^键(\d+)\s*·\s*(%s)$', 'key {0} · {1}'),
    (r'^查询(\d+)\s*·\s*(%s)$', 'query {0} · {1}'),
    (r'^值(\d+)\s*·\s*(%s)$', 'value {0} · {1}'),
    (r'^s=(\d+)\s*·\s*(%s)$', 's={0} · {1}'),
    (r'^(\d+)\s*·\s*(%s)$', '{0} · {1}'),
    (r'^(\d+)\s+(%s)$', '{0} {1}'),
    (r'^(%s)$', '{0}'),
]
# Substitutions that restore a glyph the translator replaced. Each was read in
# context; a blind English-word-to-glyph swap would hit ordinary prose.
RESTORE = [
    ('[I, love, studying, EOS]', '[我, 爱, 学习, EOS]'),
    ('[I, love, study, EOS]', '[我, 爱, 学习, EOS]'),
    ('[I, love] as input first', '[我, 爱] as input first'),
    ('[studying, !, EOS]', '[学习, ！, EOS]'),
    ('[study, !, EOS]', '[学习, ！, EOS]'),
    ('ID 2 for "love" in the teaching vocabulary', 'ID 2 for 爱 in the teaching vocabulary'),
    ('"say love whenever it sees love"', '"say 爱 whenever it sees 爱"'),
    ('the probability of "learning" after the prefix "I love"',
     'the probability of 学习 after the prefix 我爱'),
    ('showing "learning"', 'showing 学习'),
    ('holds only "I, love"', 'holds only 我、爱'),
    ('the Chinese character for "love" takes the three bytes', 'the character 爱 takes the three bytes'),
    ('the three UTF-8 bytes of the character for "love"', 'the three UTF-8 bytes of 爱'),
    ('Decodes to "love"', 'Decodes to 爱'),
    ('four-dimensional vector for "love"', 'four-dimensional vector for 爱'),
    ('PAD 0, I 1, love 2, learning 3, you 4, ! 5', 'PAD 0, 我 1, 爱 2, 学习 3, 你 4, ！5'),
    ('PAD 0, I 1, love 2, study 3, you 4, ! 5', 'PAD 0, 我 1, 爱 2, 学习 3, 你 4, ！5'),
    ('demonstrate "study → ! → EOS"', 'demonstrate 学习→！→EOS'),
    ('demonstrate "studying → ! → EOS"', 'demonstrate 学习→！→EOS'),
    ('stand for "I" and "love"', 'stand for 我 and 爱'),
    ('Working the row for "love" through once in full', 'Working the row for 爱 through once in full'),
    ('The same "love", with the first three results all computed',
     'The same 爱, with the first three results all computed'),
    ('Working out one score with the "studying" column', 'Working out one score with the 学习 column'),
    ('Working out one score with the "study" column', 'Working out one score with the 学习 column'),
    ('Turn 1: only BOS, I and love are processed', 'Turn 1: only BOS, 我 and 爱 are processed'),
    ('Turn 2: "study" appears in the input for the first time',
     'Turn 2: 学习 appears in the input for the first time'),
    ('Turn 2: "studying" appears in the input for the first time',
     'Turn 2: 学习 appears in the input for the first time'),
    ('I / love / study', '我／爱／学习'),
    ('I / love / learning', '我／爱／学习'),
    ('I / love', '我／爱'),
    ('I, love', '我、爱'),
    ('The representation of that same "love", turned into Q/K/V',
     'The representation of that same 爱, turned into Q/K/V'),
]


def main():
    D = json.loads(TABLE.read_text(encoding='utf-8'))
    t = D['s']
    framed = restored = 0
    left = []
    for k, v in t.items():
        en = v.get(LANG)
        if not en:
            continue
        s = k.strip()
        # a label whose whole shape is known: rebuild it, do not patch it
        hit = False
        for pat, tpl in FRAMES:
            m = re.match(pat % ALT, s)
            if m:
                want = tpl.format(*m.groups())
                if en != want:
                    framed += 1
                    if FIX:
                        v[LANG] = want
                hit = True
                break
        if hit:
            continue
        excused = {tok for phrase, (tok, _) in ALLOW.items() if phrase in k}
        out = en
        for a, b in RESTORE:
            out = out.replace(a, b)
        if out != en:
            restored += 1
            if FIX:
                v[LANG] = out
            en = out
        lost = [z for z in TOK
                if z not in excused and z in k and z not in en and cued(k, z)
                and ENGLISH.get(z) and re.search(ENGLISH[z], en, re.I)]
        if lost:
            left.append((v['id'], k, en, lost))

    if FIX:
        TABLE.write_text(json.dumps(D, ensure_ascii=False), encoding='utf-8')
    print('[%s] 词表标签重建 %d 条 | 词元恢复 %d 条 | 仍需人工 %d 条%s' %
          (LANG, framed, restored, len(left), '（已改）' if FIX else ''))
    for i, k, en, lost in left[:10]:
        print('   id=%-6d 丢失 %s' % (i, '/'.join(lost)))
        print('      zh: %s' % k[:76])
        print('      %s: %s' % (LANG, en[:76]))
    return 1 if left else 0


if __name__ == '__main__':
    sys.exit(main())
