from pathlib import Path
from lxml import html as LH
from collections import Counter
from urllib.parse import urlsplit,unquote
import zipfile,hashlib,re,json,os
import argparse
parser=argparse.ArgumentParser(description='Validate local links, placement and retained teaching content against a base ZIP')
parser.add_argument('book_root',type=Path);parser.add_argument('base_zip',type=Path)
args=parser.parse_args();R=args.book_root.resolve();Z=args.base_zip.resolve()
# Gather ids, refs and teaching text; lxml only reads, it never rewrites the pages.
ids={};trees={};duplicates=[];links=[];bad=[]
for p in sorted(R.rglob('*.html')):
 rel=p.relative_to(R).as_posix();t=LH.fromstring(p.read_bytes());trees[rel]=t
 count=Counter(t.xpath('//*[@id]/@id'));ids[rel]=set(count)
 duplicates +=[(rel,i,n) for i,n in count.items() if n>1]
 for e in t.xpath('//*[@href or @src]'):
  for attr in ['href','src']:
   if not e.get(attr):continue
   u=e.get(attr);parsed=urlsplit(u)
   if parsed.scheme or u.startswith('//') or u.startswith('data:'):continue
   target=os.path.normpath(os.path.join(os.path.dirname(rel),unquote(parsed.path))) if parsed.path else rel
   target=target.replace(os.sep,'/')
   links.append((rel,target,unquote(parsed.fragment),u))
for src,target,anchor,u in links:
 if not (R/target).exists():bad.append({'from':src,'target':u,'reason':'file'})
 elif anchor and target.endswith('.html') and anchor not in ids.get(target,set()):bad.append({'from':src,'target':u,'reason':'anchor'})

# Check old content remains as a multiset, skipping only shells, navigation and length metadata.
TAGS='p|li|th|td|h1|h2|h3|h4|h5|h6|pre|dt|dd'
def textblocks(tree):
 art=tree.xpath('//article');a=art[0] if art else tree
 out=[]
 for e in a.xpath('.//*'):
  if e.tag not in TAGS.split('|'):continue
  if any('reading-meta' in anc.get('class','').split() or anc.tag in ['nav','script','style'] for anc in [e,*e.iterancestors()]):continue
  text=' '.join(''.join(e.itertext()).split())
  if text:out.append(text)
 return Counter(out)
base_files=[];missing_files=[];immutable_changed=[];text_missing=[];baseline_blocks=0
with zipfile.ZipFile(Z) as z:
 for n in z.namelist():
  if n.endswith('/'):continue
  rel=n.split('/',1)[1];base_files.append(rel)
  p=R/rel
  if not p.exists():missing_files.append(rel);continue
  raw=z.read(n)
  if rel.endswith('.html') and rel!='complete.html':
   old=textblocks(LH.fromstring(raw));new=textblocks(trees[rel]);baseline_blocks+=sum(old.values())
   for text,num in (old-new).items():text_missing.append({'path':rel,'count':num,'text':text[:500]})
  elif not rel.endswith('.html') and rel not in ['assets/search-data.js','assets/catalog.js']:
   if hashlib.sha256(raw).digest()!=hashlib.sha256(p.read_bytes()).digest():immutable_changed.append(rel)
mods=json.loads((R/'engineering/modules.json').read_text());cases=json.loads((R/'engineering/cases.json').read_text())
placement_errors=[]
for m in mods:
 rel=f'chapters/{m["chapter"]:02d}.html';t=trees[rel];node=t.xpath(f'//*[@id="engineering-{m["id"]}"]')
 if len(node)!=1:placement_errors.append([m['id'],'count',len(node)]);continue
 prev=node[0].xpath('preceding::h2[starts-with(@id,"Q")][1]')
 if not prev or prev[0].get('id')!=m['after']:placement_errors.append([m['id'],'placement',prev[0].get('id') if prev else None])
 compid=rel[:-5].replace('/','--')+'--engineering-'+m['id']
 if compid not in ids['complete.html']:placement_errors.append([m['id'],'single missing'])
for c in cases:
 rel=f'studies/chapters/{c["chapter"]:02d}.html';t=trees[rel];node=t.xpath(f'//*[@id="engineering-{c["id"]}"]')
 if len(node)!=1:placement_errors.append([c['id'],'count',len(node)]);continue
 prev=node[0].xpath('preceding::h2[1]')
 if not prev or prev[0].get('id')!=c['after']:placement_errors.append([c['id'],'placement',prev[0].get('id') if prev else None])
 compid=rel[:-5].replace('/','--')+'--engineering-'+c['id']
 if compid not in ids['complete.html']:placement_errors.append([c['id'],'single missing'])
openanswers=[]
for path,t in trees.items():
 for d in t.xpath('//details[contains(concat(" ",normalize-space(@class)," ")," quiz-answer ")][@open]'):openanswers.append(path)
source_ids={s['id'] for s in json.loads((R/'engineering/sources.json').read_text())}
unresolved=[]
for m in mods:
 unresolved.extend((m['id'],x) for x in re.findall(r'\[\[SRC:([^]]+)\]\]',m['body']) if x not in source_ids)
external_assets=trees['complete.html'].xpath('//script[@src]/@src|//link[@rel="stylesheet"]/@href|//img[not(starts-with(@src,"data:"))]/@src')
counts={'html_pages':len(trees),'local_references':len(links),'baseline_files':len(base_files),'baseline_teaching_blocks':baseline_blocks,'new_modules':len(mods),'new_cases':len(cases),'new_module_questions_closed':sum(len(t.xpath('//section[contains(@class,"eng-quiz")]//details[not(@open)]')) for path,t in trees.items() if path!='complete.html')}
report={'counts':counts,'missing_local_targets':bad,'duplicate_ids':duplicates,'missing_original_files':missing_files,'changed_original_immutable_files':immutable_changed,'missing_original_teaching_text':text_missing,'placement_errors':placement_errors,'open_selfcheck_answers':openanswers,'unresolved_sources':unresolved,'single_external_assets':external_assets,'pass':not any([bad,duplicates,missing_files,immutable_changed,text_missing,placement_errors,openanswers,unresolved,external_assets])}
(R/'engineering/results/structure.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='missing_original_teaching_text'},ensure_ascii=False,indent=2));print('MISSING TEXT',len(text_missing));print(json.dumps(text_missing[:5],ensure_ascii=False,indent=2))
