"""Check the assembled offline book, its visible numbering and derived copies."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from collections import Counter
from lxml import html as LH
import json, re, copy

R=Path(__file__).resolve().parents[2]
canonical=json.loads((R/'editorial/canonical-pages.json').read_text())
curriculum=json.loads((R/'editorial/curriculum.json').read_text())
numbering=json.loads((R/'editorial/numbering-map.json').read_text())
docs={p.relative_to(R).as_posix():LH.fromstring(p.read_bytes()) for p in R.rglob('*.html')}
ids={p:set(d.xpath('//@id')) for p,d in docs.items()}
errors=[];references=0;answer_count=0
for page,doc in docs.items():
    for k,n in Counter(doc.xpath('//@id')).items():
        if n>1:errors.append([page,'duplicate-id',k,n])
    for t in doc.iter():
        for attr in ['href','src','poster']:
            url=t.attrib.get(attr)
            if not url:continue
            u=urlsplit(url)
            if u.scheme or u.netloc:continue
            references+=1
            f=(R/page).parent/unquote(u.path) if u.path else R/page
            try:target=f.resolve().relative_to(R.resolve()).as_posix()
            except ValueError:errors.append([page,'outside-root',url]);continue
            if not (R/target).exists():errors.append([page,'missing-file',url])
            elif u.fragment and target in ids and unquote(u.fragment) not in ids[target]:errors.append([page,'missing-anchor',url])
        for value in t.attrib.values():
            for a in re.findall(r'url\(#([^)]*)\)',value):
                if a not in ids[page]:errors.append([page,'missing-svg-reference',a])

def article(d):return d.xpath('//article[contains(concat(" ",normalize-space(@class)," ")," article ")]')[0]
def norm(t):return re.sub(r'\s+',' ',t.text_content()).strip()
single=docs['complete.html'];synced=0;mdsynced=0
for e in canonical:
    p=e['path'];a=copy.deepcopy(article(docs[p]))
    for t in a.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," pager ") or contains(concat(" ",normalize-space(@class)," ")," progress-row ") or contains(concat(" ",normalize-space(@class)," ")," breadcrumb ") or contains(concat(" ",normalize-space(@class)," ")," footer ")]'):
        if t.getparent() is not None:t.getparent().remove(t)
    sec=single.xpath('//*[@id=$id]',id=p[:-5].replace('/','--'))
    if not sec or norm(a)!=norm(sec[0]):errors.append([p,'standalone-text-mismatch'])
    else:synced+=1
    for t in a.xpath('.//details[contains(concat(" ",normalize-space(@class)," ")," quiz-answer ")]'):
        answer_count+=1
        if 'open' not in t.attrib:errors.append([p,'answer-not-open'])
    md=(R/'wiki'/Path(p).with_suffix('.md')).read_text()
    for t in a.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," mobile-outline ") or contains(concat(" ",normalize-space(@class)," ")," lesson-context ")]'):
        if t.getparent() is not None:t.getparent().remove(t)
    needed=set(a.xpath('.//@id'))
    actual=set(re.findall(r'\bid=["\x27]([^"\x27]+)',md))
    if needed-actual:errors.append([p,'markdown-missing-anchors',sorted(needed-actual)])
    else:mdsynced+=1

for row in numbering['lessons']:
    p=row['path'];h=article(docs[p]).xpath('.//h1')[0]
    if norm(h)!=row['title']:errors.append([p,'wrong-lesson-heading',norm(h)])
    if not norm(h).startswith(f"第{row['lesson']:02d}课｜"):errors.append([p,'wrong-lesson-number'])
for row in numbering['questions']:
    hs=docs[row['path']].xpath('//*[@id=$id]',id=row['stable_id'])
    if not hs or not norm(hs[0]).startswith(row['label']+'｜'):errors.append([row['path'],'wrong-question-number',row])
visible_labels=[r['label'] for r in numbering['questions']]
if visible_labels!=[f'Q{i:03d}' for i in range(1,113)]:errors.append(['questions','not-contiguous'])
ordered_paths=curriculum['sequence']
content_paths=[x for x in article(docs['contents.html']).xpath('.//a/@href') if x in ordered_paths]
if content_paths!=ordered_paths:errors.append(['contents.html','reading-order-mismatch',content_paths])
for e in canonical:
    rail=docs[e['path']].xpath('//*[contains(concat(" ",normalize-space(@class)," ")," rail-scroll ")]')
    if rail:
        seq=[x for x in rail[0].xpath('.//a/@data-target') if x in ordered_paths]
        if seq!=ordered_paths:errors.append([e['path'],'sidebar-reading-order-mismatch'])
data=(R/'assets/search-data.js').read_text();search=json.loads(data.split('=',1)[1].rstrip(';'))
for row in numbering['questions']:
    hit=[x for x in search if x['id']==row['label']]
    if len(hit)!=1 or hit[0]['path']!=row['path']+'#'+row['stable_id']:
        errors.append(['search','visible-question-mismatch',row['label'],len(hit)])

report={'html_pages':len(docs),'canonical_articles':len(canonical),'local_references':references,
        'standalone_matches':synced,'markdown_anchor_matches':mdsynced,'answers_open':answer_count,
        'lessons':len(numbering['lessons']),'questions':len(numbering['questions']),
        'reading_order_pages':len(ordered_paths),'search_entries':len(search),'errors':errors,
        'status':'passed' if not errors else 'failed'}
(R/'editorial/coverage-review/static-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2)[:15000])
raise SystemExit(bool(errors))
