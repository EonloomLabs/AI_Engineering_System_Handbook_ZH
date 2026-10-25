from pathlib import Path
from urllib.parse import urlsplit,unquote
from lxml import html as LH
from collections import Counter
import json,re,hashlib,os
W=Path('/mnt/data/_content_audit_20261024');R=W/'build/AI_Systems_Engineering_Textbook_ZH';O=W/'original/AI_Systems_Engineering_Textbook_ZH'
report={};cache={};ids={};duplicates=[];broken=[];references=0;svg_refs=[];answers=[]
for p in sorted(R.rglob('*.html')):
 rel=p.relative_to(R).as_posix();doc=LH.fromstring(p.read_bytes());cache[rel]=doc
 c=Counter(doc.xpath('//@id'));ids[rel]=set(c)
 duplicates.extend((rel,x,n) for x,n in c.items() if n>1)
 answers.extend((rel,t.attrib.get('id','')) for t in doc.xpath('//details[contains(concat(" ",normalize-space(@class)," ")," quiz-answer ")][@open]'))
for rel,doc in cache.items():
 for t in doc.iter():
  for attr in ['href','src','poster']:
   url=t.attrib.get(attr)
   if not url:continue
   u=urlsplit(url)
   if u.scheme or u.netloc:continue
   references+=1
   target=(R/rel).parent/unquote(u.path) if u.path else R/rel
   try:target=target.resolve().relative_to(R.resolve()).as_posix()
   except ValueError:broken.append((rel,url,'outside-root'));continue
   if not (R/target).exists():broken.append((rel,url,'file-missing'))
   elif u.fragment and target in ids and unquote(u.fragment) not in ids[target]:broken.append((rel,url,'anchor-missing'))
  for value in t.attrib.values():
   for anchor in re.findall(r'url\(#([^)]*)\)',value):
    if anchor not in ids[rel]:svg_refs.append((rel,anchor))
canonical=json.loads((R/'editorial/canonical-pages.json').read_text());single=cache['complete.html'];sync=[]
for e in canonical:
 p=e['path'];doc=cache[p];a=doc.xpath('//article[contains(concat(" ",normalize-space(@class)," ")," article ")]')[0]
 for t in a.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," pager ") or contains(concat(" ",normalize-space(@class)," ")," progress-row ") or contains(concat(" ",normalize-space(@class)," ")," breadcrumb ") or contains(concat(" ",normalize-space(@class)," ")," footer ")]'):
  if t.getparent() is not None:t.getparent().remove(t)
 sid=p[:-5].replace('/','--');secs=single.xpath('//*[@id=$id]',id=sid)
 if not secs:sync.append((p,'section-missing'));continue
 norm=lambda t:re.sub(r'\s+',' ',t.text_content()).strip()
 if norm(a)!=norm(secs[0]):sync.append((p,'text-different',len(norm(a)),len(norm(secs[0]))))
# Compare file manifests and unmodified code/data/visual assets separately.
original_files=[p for p in O.rglob('*') if p.is_file()]
missing=[p.relative_to(O).as_posix() for p in original_files if not (R/p.relative_to(O)).is_file()]
changed=[];unchanged=[];immutable_changed=[]
for p in original_files:
 rel=p.relative_to(O).as_posix();q=R/rel
 if not q.exists():continue
 if p.read_bytes()!=q.read_bytes():
  changed.append(rel)
  if p.suffix=='.py' or rel.startswith('assets/figures/') or rel.startswith('labs/model/data/') or rel in ['assets/atelier.css','assets/style.css','assets/progressive.css','assets/reader-navigation.js','assets/atelier.js']:immutable_changed.append(rel)
 else:unchanged.append(rel)
qcounts=Counter()
for rel,doc in cache.items():
 if re.fullmatch(r'chapters/\d{2}\.html',rel):qcounts.update(doc.xpath('//@data-question'))
qbad={q:qcounts[q] for q in [f'Q{i:03}' for i in range(1,113)] if qcounts[q]!=1}
# Exact reused examples and parameters can move, not silently vanish.
changestext=[];oldblocks=Counter();newblocks=Counter()
for rel in [e['path'] for e in canonical if e['path'].startswith(('foundations/','chapters/'))]:
 for root,counter in [(O,oldblocks),(R,newblocks)]:
  d=LH.fromstring((root/rel).read_bytes());a=d.xpath('//article[contains(concat(" ",normalize-space(@class)," ")," article ")]')[0]
  for t in a.xpath('.//p|.//pre|.//td|.//th|.//li'):
   if t.xpath('ancestor::nav|ancestor::aside'):continue
   text=re.sub(r'\s+',' ',t.text_content()).strip()
   if len(text)>30:counter[text]+=1
losses=oldblocks-newblocks
# Preserve legitimate scope: not every removed text = mistake; replacements logged for human review.
report.update(html_pages=len(cache),local_references=references,broken=broken,duplicate_ids=duplicates,svg_reference_errors=svg_refs,answers_open=answers,single_page_text_mismatches=sync,question_home_errors=qbad,original_files=len(original_files),missing_original_paths=missing,unchanged_original_files=len(unchanged),changed_original_files=len(changed),immutable_changed=immutable_changed,removed_or_reworded_text_blocks=sum(losses.values()),rewritten_core_pages=len([p for p in changed if p.startswith(('foundations/','chapters/'))]),new_files=len([p for p in R.rglob('*') if p.is_file()])-len(original_files))
out=R/'editorial/content-review';(out/'static-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(out/'changed-files.json').write_text(json.dumps(changed,ensure_ascii=False,indent=2));(out/'rewritten-blocks.json').write_text(json.dumps([{'count':v,'text':k} for k,v in losses.items()],ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2)[:10000])
