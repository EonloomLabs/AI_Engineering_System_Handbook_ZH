"""Hold the English edition to the spelling the book's own glossary uses.

glossary.html prints optimization, Quantization, Normalization, so the edition
is American. Translators came from different habits and the earlier batches
followed a reference file that was itself inconsistent, so this sweeps the
table instead of relying on each batch to get it right.

The -ise/-ize family is matched by pattern rather than by a list of words, so a
form no one thought of (Generalising, Contextualisation) is caught too. KEEP
holds the words where "is" belongs to the stem - raise, rise, precise - and the
-wise suffix, which must never be touched.

Run: python3 i18n/spelling.py [--lang=en] [--fix]
"""
import json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / 'i18n/table.json'
LANG = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--lang=')), 'en')
FIX = '--fix' in sys.argv

KEEP = {
    # "is" is part of the stem, not the British suffix
    'raise', 'raises', 'raised', 'raising', 'rise', 'rises', 'risen', 'rising',
    'arise', 'arises', 'arising', 'praise', 'praises', 'praised', 'cruise',
    'noise', 'noises', 'poise', 'guise', 'disguise', 'disguised', 'revise',
    'revised', 'revises', 'revising', 'devise', 'devised', 'devises',
    'supervise', 'supervised', 'supervising', 'improvise', 'improvised',
    'precise', 'precisely', 'concise', 'concisely', 'promise', 'promises',
    'promised', 'promising', 'surprise', 'surprised', 'surprising',
    'comprise', 'comprises', 'comprised', 'compromise', 'compromised',
    'compromises', 'premise', 'premises', 'exercise', 'exercises', 'exercised',
    'enterprise', 'enterprises', 'expertise', 'franchise', 'merchandise',
    'paradise', 'treatise', 'demise', 'chastise', 'advertise', 'advertised',
    'advertising', 'advise', 'surmise', 'despise', 'reprise', 'appraise',
    'disable', 'disability', 'disabilities',
    'size', 'sizes', 'sized', 'sizing',
    # the -wise suffix
    'wise', 'wisely', 'otherwise', 'likewise', 'clockwise', 'stepwise',
    'pairwise', 'elementwise', 'unwise', 'rowwise', 'columnwise',
}
SUFFIX = [('isabilities', 'izabilities'), ('isability', 'izability'),
          ('isable', 'izable'), ('isably', 'izably'),
          ('isations', 'izations'), ('isation', 'ization'), ('isers', 'izers'),
          ('iser', 'izer'), ('ises', 'izes'), ('ised', 'ized'),
          ('ising', 'izing'), ('ise', 'ize')]
WORD = re.compile(r'\b[A-Za-z]+is(?:e|es|ed|ing|ation|ations|er|ers|able|ably|ability|abilities)\b')
# Other British forms the book does not want, as explicit pairs.
OTHER = [('behaviour', 'behavior'), ('labour', 'labor'), ('colour', 'color'), ('catalogue', 'catalog'),
         ('labelled', 'labeled'), ('labelling', 'labeling'), ('modelling', 'modeling'),
         ('modelled', 'modeled'), ('centre', 'center'), ('defence', 'defense'),
         ('licence', 'license'), ('fulfil', 'fulfill'), ('whilst', 'while'),
         ('artefact', 'artifact'), ('judgement', 'judgment'), ('cancelled', 'canceled'),
         ('cancelling', 'canceling'), ('favour', 'favor'), ('neighbour', 'neighbor'),
         ('neighbouring', 'neighboring'), ('analyse', 'analyze'), ('analysed', 'analyzed'),
         ('analysing', 'analyzing'), ('grey', 'gray'), ('programme', 'program'),
         ('travelling', 'traveling'), ('practise', 'practice')]


# A prefixed derivation of a KEEP word must be kept too: imprecise, unwise,
# oversize. Matching by suffix instead would wrongly spare summarise, which
# ends in "arise", so the prefix has to be stripped explicitly.
PREFIX = ('un', 'im', 'in', 'over', 'under', 're', 'mis', 'non', 'pre', 'dis', 'de')
# Protect inflections of native -ise stems as a family, rather than requiring
# a new exception for supervised, supervising, exercisable, advisable, etc.
NATIVE = KEEP | {stem[:-1] + ending
                 for stem in KEEP if stem.endswith('ise')
                 for ending in ('es', 'ed', 'ing', 'er', 'ers', 'able', 'ably',
                                'ability', 'abilities')}


def keep(word):
    w = word.lower()
    # -wise forms are productive (piecewise, bitwise, lengthwise), rather
    # than British -ise verbs. Protect the suffix, including its adverb form.
    if w in NATIVE or w.endswith(('wise', 'wisely')):
        return True
    return any(w.startswith(p) and w[len(p):] in NATIVE for p in PREFIX)


def american(word):
    if keep(word):
        return word
    for a, b in SUFFIX:
        if word.endswith(a):
            return word[:-len(a)] + b
        if word.endswith(a.capitalize()):
            return word[:-len(a)] + b.capitalize()
    return word


def convert_prose(text):
    def one(m):
        return american(m.group(0))
    out = WORD.sub(one, text)
    # These families keep their suffix when the stem spelling changes:
    # behaviour -> behavioral/behaviorally, labour -> labor/laborers.
    for british, american_stem in [('behaviour', 'behavior'), ('labour', 'labor')]:
        out = re.sub(r'\b' + british + r'([a-z]*)\b',
                     lambda m: american_stem + m.group(1), out)
        out = re.sub(r'\b' + british.capitalize() + r'([a-z]*)\b',
                     lambda m: american_stem.capitalize() + m.group(1), out)
    for a, b in OTHER:
        out = re.sub(r'\b%s\b' % a, b, out)
        out = re.sub(r'\b%s%s\b' % (a[0].upper(), a[1:]), b[0].upper() + b[1:], out)
        out = re.sub(r'\b%ss\b' % a, b + 's', out)
    return out


def convert(text):
    # Tags and their attributes are an immutable part of a translation unit.
    return ''.join(part if part.startswith('<') else convert_prose(part)
                   for part in re.split(r'(<[^>]+>)', text))


def main():
    D = json.loads(TABLE.read_text(encoding='utf-8'))
    t = D['s']
    hits, rows = Counter(), 0
    for k, v in t.items():
        e = v.get(LANG)
        if not e:
            continue
        f = convert(e)
        if f == e:
            continue
        rows += 1
        for w in WORD.findall(e):
            if american(w) != w:
                hits[w] += 1
        for a, _ in OTHER:
            n = len(re.findall(r'\b%s' % a, e, re.I))
            if n:
                hits[a] += n
        if FIX:
            v[LANG] = f
    if FIX:
        TABLE.write_text(json.dumps(D, ensure_ascii=False), encoding='utf-8')
    print('[%s] 非目标拼写: %d 条译文, %d 个词形%s' %
          (LANG, rows, len(hits), '（已统一）' if FIX else ''))
    for w, c in hits.most_common(12):
        print('   %-22s ×%d' % (w, c))
    return 0


if __name__ == '__main__':
    sys.exit(main())
