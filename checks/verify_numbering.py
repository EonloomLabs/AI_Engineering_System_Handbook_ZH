"""Post-renumbering verifier. Run: python checks/verify_numbering.py.
Checks are static and offline; this does not test model or GPU performance.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter,defaultdict
from urllib.parse import urlsplit,unquote
import json, re, os, sys
from lxml import html as LH

R=Path(__file__).resolve().parents[1]
legacy=json.loads((R/'editorial/historical-numbering.json').read_text('utf8'))
current=json.loads((R/'editorial/numbering-map.json').read_text('utf8'))
locs=json.loads((R/'worked-examples/locations.json').read_text('utf8'))
examples=json.loads((R/'worked-examples/examples.json').read_text('utf8'))
visibility=json.loads((R/'worked-examples/visibility.json').read_text('utf8'))

trees={}; ids={}; errors=[]; link_count=0; duplicate_count=0;visible_old=[]
for p in sorted(R.rglob('*.html')):
 rel=p.relative_to(R).as_posix()
 t=LH.fromstring(p.read_bytes());trees[rel]=t
 ctr=Counter(t.xpath('//*[@id]/@id'));ids[rel]=set(ctr)
 duplicates=[(k,n) for k,n in ctr.items() if n>1]
 duplicate_count+=len(duplicates)
 for k,n in duplicates:errors.append(f'duplicate id: {rel}#{k} x{n}')
 # For content verification, ignore hidden anchor IDs, script and metadata.
 for elem in t.xpath('//article|//section[@class="standalone-section"]'):
  clone=LH.fromstring(LH.tostring(elem))
  for n in clone.xpath('.//script|.//style|.//svg'):
   n.drop_tree()
  txt=' '.join(clone.itertext())
  if re.search(r'(?<![\w])F(?:0[1-9]|[1-3]\d|40)(?![\w])',txt):
   visible_old.append(rel)
   break
 for tag in t.xpath('//*[@href or @src]'):
  for attr in ('href','src'):
   u=tag.get(attr)
   if not u:continue
   parsed=urlsplit(u)
   if parsed.scheme or u.startswith('//') or u.startswith('data:'):continue
   dest=os.path.normpath(os.path.join(os.path.dirname(rel),unquote(parsed.path))) if parsed.path else rel
   dest=dest.replace(os.sep,'/')
   anchor=unquote(parsed.fragment)
   link_count+=1
   if not (R/dest).exists():errors.append(f'missing file: {rel}: {u}')
   elif anchor and dest.endswith('.html') and anchor not in ids.get(dest,set()):
    # Two-pass check; ids may not yet have been read when source comes first.
    pass
# Second pass link anchors after all HTML pages indexed.
for rel,t in trees.items():
 for tag in t.xpath('//*[@href or @src]'):
  for attr in ('href','src'):
   u=tag.get(attr)
   if not u:continue
   parsed=urlsplit(u)
   if parsed.scheme or u.startswith('//') or u.startswith('data:'):continue
   dest=os.path.normpath(os.path.join(os.path.dirname(rel),unquote(parsed.path))) if parsed.path else rel
   dest=dest.replace(os.sep,'/')
   anch=unquote(parsed.fragment)
   if anch and dest.endswith('.html') and (R/dest).exists() and anch not in ids.get(dest,set()):
    errors.append(f'missing anchor: {rel} -> {u}')

if visible_old:errors.append(f'Visible legacy Fnn tokens: {visible_old}')
assert len(current['lessons'])==68
assert [x['lesson'] for x in current['lessons']]==list(range(1,69))
assert len(current['questions'])==112
if any('old_title' in x for x in current['lessons']):errors.append('Main course map exposes obsolete titles')
for x in current['lessons']:
 p=x['path']; n=x['lesson']
 h=trees[p].xpath('(//article//h1)[1]')
 if not h or not re.match(fr'第0?{n}课\b|第{n:02}课', ''.join(h[0].itertext())):
  errors.append(f'wrong lesson heading {p}: {"".join(h[0].itertext()) if h else "missing"}')

# Make sure all historical F01..F40 entry points have a real target in both
# distributed modes, without appearing as public lesson identifiers.
for f in legacy['foundation_case_compatibility']:
 oid=f['legacy_id'];p=f['original_page']
 if f'worked-{oid}' not in ids.get(p,set()):errors.append(f'old bookmark missing: {p}#worked-{oid}')
 prefix=p[:-5].replace('/','--')
 if f'{prefix}--worked-{oid}' not in ids.get('complete.html',set()):
  errors.append(f'complete bookmark missing: {oid}')

# The example registry must point to *existing* pages and *existing* element IDs.
if len(locs)!=len(examples)!=401:errors.append('example registry cardinality mismatch')
if len(set(x['id'] for x in examples))!=401:errors.append('duplicate example IDs')
for e in examples:
 c=e['id']
 if re.fullmatch(r'F\d{2}',c):errors.append('Legacy case ID in active registry: '+c)
 if c not in locs:
  errors.append('no example mapping: '+c);continue
 url=locs[c];p,_,anchor=url.partition('#')
 if p not in trees:errors.append(f'example file unavailable: {c} -> {url}')
 elif anchor and anchor not in ids.get(p,set()):errors.append(f'example anchor unavailable: {c} -> {url}')
 if c in visibility['no_standalone_block'] and anchor:
  errors.append(f'missing example incorrectly claims a dedicated anchor: {c}')

# The current location of an actual example must be its rendered location.
rendered=defaultdict(list)
for rel,t in trees.items():
 if rel=='complete.html':continue
 for el in t.xpath('//*[@data-example]'):
  c=el.get('data-example');a=el.get('id')
  rendered[c].append(f'{rel}#{a}')
for c,urls in rendered.items():
 if c in locs and locs[c] not in urls:errors.append(f'stale placement: {c} -> {locs[c]} expected {urls}')

# No duplicate visible 'F' labels remain in the local search index; check that
# search metadata still uses the canonical 68 lesson titles.
search=(R/'assets/search-data.js').read_text('utf8')
if re.search(r'(?<!\w)F(?:0[1-9]|[1-3]\d|40)(?!\w)',search):errors.append('old F-code appears in search records')
cat=(R/'assets/catalog.js').read_text('utf8')
for x in current['lessons']:
 if x['title'] not in cat:errors.append('lesson missing from catalog: '+x['title'])

report={'status':'passed' if not errors else 'failed','html_pages':len(trees),'local_asset_and_href_links':link_count,
 'duplicate_dom_ids':duplicate_count,'legacy_bookmarks_retained':40,'current_lessons':len(current['lessons']),
 'current_questions':len(current['questions']),'example_registry_count':len(examples),
 'example_specific_locations':sum('#' in v for v in locs.values()),
 'historical_example_course_fallbacks':len(visibility['no_standalone_block']),
 'remaining_visible_Fnn':len(visible_old),'issues':errors}
out=R/'validation/numbering-fix-results.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='issues'},ensure_ascii=False,indent=2))
if errors:
 print('ERRORS '+str(len(errors)))
 for s in errors[:30]:print(s)
 sys.exit(1)
