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

The rail splits a full heading at one fixed HTML marker instead of its ｜
separator. That exact source mirror is checked as a whole in every language;
it cannot be found by comparing the two separate text segments.

Run: python3 i18n/embedded.py [--lang=en] [--fix]
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / 'i18n/table.json'
LANG = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--lang=')), 'en')
FIX = '--fix' in sys.argv
TAG = re.compile(r'<[^>]+>')
RAIL_MARKER = '</span><span class="rail-name">'
NUMBER_ID = re.compile(r'[A-Za-z_][A-Za-z_0-9]*(?:[./-][A-Za-z_0-9]+)*|[−+-]?\d+(?:\.\d+)?')


def segs(s):
    return [x.strip() for x in TAG.split(s)]


def _number_ids(text):
    return [token for token in NUMBER_ID.findall(TAG.sub('', text))
            if any(c.isdigit() for c in token)]


def rail_mirror_fixes(translations):
    """Return safe rail replacements from a source -> target mapping, purely.

    A source must contain exactly one RAIL_MARKER, and replacing only that
    marker with ｜ must resolve to an existing translated canonical heading.
    Missing canonical translations/separators are skipped, never guessed.
    Canonical targets with changed tags or numeric identifiers raise ValueError
    before any caller writes. The input mapping and its values are not changed.
    """
    fixes = {}
    for host, got in translations.items():
        if host.count(RAIL_MARKER) != 1:
            continue
        canonical = host.replace(RAIL_MARKER, '｜', 1)
        target = translations.get(canonical)
        if not isinstance(target, str) or not target or '｜' not in target:
            continue
        prefix, body = target.split('｜', 1)
        source_prefix, source_body = host.split(RAIL_MARKER, 1)
        want = prefix + RAIL_MARKER + body
        if sorted(TAG.findall(want)) != sorted(TAG.findall(host)):
            raise ValueError('rail mirror changes source tags: %s' % host[:90])
        if (_number_ids(prefix) != _number_ids(source_prefix)
                or _number_ids(body) != _number_ids(source_body)):
            raise ValueError('rail mirror changes source numeric identifiers: %s' % host[:90])
        if got != want:
            fixes[host] = want
    return fixes


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

    mirrors = rail_mirror_fixes(done)
    print('[%s] 链接文本与其指向的条目不一致: %d 处\n' % (LANG, len(bad) + len(mirrors)))
    for host, i, zh, want, got in bad[:14]:
        print('  片段 zh : %s' % zh[:66])
        print('  条目 %s : %s' % (LANG, want[:66]))
        print('  链接 %s : %s' % (LANG, got[:66]))
        print()
    for host, want in list(mirrors.items())[:max(0, 14 - len(bad))]:
        print('  侧栏 zh : %s' % host[:66])
        print('  条目 %s : %s' % (LANG, want[:66]))
        print('  侧栏 %s : %s' % (LANG, done[host][:66]))
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
        # Segment repairs may have updated a canonical heading; derive the
        # exact mirror again from the current language before committing D.
        mirrors = rail_mirror_fixes({k: v[LANG] for k, v in t.items() if v.get(LANG)})
        for host, want in mirrors.items():
            t[host][LANG] = want
            n += 1
        TABLE.write_text(json.dumps(D, ensure_ascii=False), encoding='utf-8')
        print('统一 %d 处' % n)
    return 0


if __name__ == '__main__':
    sys.exit(main())
