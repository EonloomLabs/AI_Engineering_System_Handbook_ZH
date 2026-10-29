"""Check that every local reference in a generated edition resolves.

en/ mirrors only the HTML tree, so a reference out of it gains one '../' at
build time while a reference to a translated page keeps its path. That rewrite
is the one part of the build that can silently produce a page which loads
nothing - a wrong number of '../' gives a 404 for a stylesheet, not an error -
so it is checked here against the file system rather than by reading the rule.

Run: python3 i18n/links.py [--lang=en]
"""
import re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANG = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--lang=')), 'en')
REF = re.compile(r'\b(?:src|href)="([^"]+)"')


def main():
    base = ROOT / LANG
    if not base.is_dir():
        print('%s/ 不存在' % LANG)
        return 0
    pages = sorted(base.rglob('*.html'))
    # A link to a page not yet translated is not a fault - the edition is
    # built page by page - so it is counted apart from a reference that should
    # resolve now: a stylesheet, a script, a figure, or a page already built.
    done = {f.relative_to(base).as_posix() for f in pages}
    missing, pending, kinds, checked = [], Counter(), Counter(), 0
    for f in pages:
        doc = f.read_text(encoding='utf-8')
        for u in REF.findall(doc):
            if u.startswith(('http://', 'https://', '//', 'mailto:', 'data:', '#')):
                continue
            bare = u.split('#')[0].split('?')[0]
            if not bare:
                continue
            checked += 1
            target = (f.parent / bare).resolve()
            if target.exists():
                continue
            zh = ROOT / bare if bare.startswith('/') else (ROOT / f.parent.relative_to(base) / bare)
            try:
                rel = zh.resolve().relative_to(ROOT.resolve()).as_posix()
            except ValueError:
                rel = None
            if bare.endswith('.html') and rel and rel not in done and (ROOT / rel).exists():
                pending[rel] += 1          # that page exists in Chinese, not yet translated
                continue
            missing.append((f.relative_to(ROOT).as_posix(), u))
            kinds[Path(bare).suffix or '(无后缀)'] += 1
    print('[%s] %d 页 | 本地引用 %s 处 | 应解析但失败 %d 处 | 指向未译页面 %s 处（%d 页）' %
          (LANG, len(pages), format(checked, ','), len(missing),
           format(sum(pending.values()), ','), len(pending)))
    for ext, n in kinds.most_common():
        print('   %-10s %d' % (ext, n))
    seen = set()
    for pg, u in missing:
        if u in seen:
            continue
        seen.add(u)
        print('   %-34s %s' % (pg, u))
        if len(seen) >= 12:
            print('   …')
            break
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
