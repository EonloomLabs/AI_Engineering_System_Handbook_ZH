"""Rebuild search, standalone HTML and Markdown from canonical article HTML.

Run from any directory: python editorial/coverage-review/build_course.py
Requires beautifulsoup4, lxml, markdownify. Does not contact external services.
Stable paths/anchors and the existing reading interface are retained.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup, Tag
from markdownify import markdownify
import base64, copy, json, mimetypes, os, re

R=Path(__file__).resolve().parents[2]
canonical=json.loads((R/'editorial/canonical-pages.json').read_text())
paths={e['path'] for e in canonical}
cache={e['path']:BeautifulSoup((R/e['path']).read_text(),'lxml') for e in canonical}
numbering=json.loads((R/'editorial/numbering-map.json').read_text())

def sid(p): return p[:-5].replace('/','--')
def norm(page,url):
    u=urlsplit(url)
    if u.scheme or u.netloc or not url:return None
    target=((R/page).parent/unquote(u.path)) if u.path else R/page
    try:target=target.resolve().relative_to(R.resolve()).as_posix()
    except ValueError:return None
    return target,unquote(u.fragment)

# Keep all actual prose, including the now-expanded answers, searchable.
search=[]
for e in canonical:
    page=e['path'];a=copy.deepcopy(cache[page].select_one('article.article'))
    for t in a.select('.mobile-outline,.pager,.progress-row,.lesson-context,script,style'):t.decompose()
    for h in a.find_all(['h1','h2','h3']):
        if not h.get('id') or h.find_parent(['table','pre']):continue
        chunks=[h.get_text(' ',strip=True)]
        for n in h.next_siblings:
            if isinstance(n,Tag) and n.name in ['h1','h2','h3']:break
            if isinstance(n,Tag):chunks.append(n.get_text(' ',strip=True))
        content='\n'.join(chunks)
        if len(content)<15:continue
        match=re.match(r'(Q\d{3})[｜|]',h.get_text('',strip=True))
        visible=match.group(1) if match else h['id']
        search.append({'title':e['title']+' · '+h.get_text(' ',strip=True),
                       'id':visible,'anchor':h['id'],'kind':e['kind'],
                       'path':page+'#'+h['id'],'text':content})
(R/'assets/search-data.js').write_text('window.COURSE_SEARCH='+json.dumps(search,ensure_ascii=False)+';',encoding='utf-8')

single=BeautifulSoup((R/'complete.html').read_text(),'lxml')
old=copy.deepcopy(single)
main=single.select_one('article.article');main.clear()
idmaps={}
for e in canonical:
    p=e['path'];a=cache[p].select_one('article.article')
    oldsec=old.find(id=sid(p));oldids={t['id'] for t in oldsec.find_all(id=True)} if oldsec else set()
    idmaps[p]={t['id']:(t['id'] if t['id'] in oldids and sid(p)+'--'+t['id'] not in oldids else sid(p)+'--'+t['id']) for t in a.find_all(id=True)}

def onelink(page,url):
    item=norm(page,url)
    if not item:return url,None
    target,anchor=item
    if target in paths:
        return '#'+(idmaps[target].get(anchor,sid(target)+'--'+anchor) if anchor else sid(target)),None
    f=R/target
    if f.is_file():
        mime=mimetypes.guess_type(f.name)[0] or 'application/octet-stream'
        return 'data:'+mime+';base64,'+base64.b64encode(f.read_bytes()).decode(),f.name
    return url,None

for e in canonical:
    p=e['path'];a=copy.deepcopy(cache[p].select_one('article.article'));mp=idmaps[p]
    for t in a.select('.pager,.progress-row,.breadcrumb,.footer'):t.decompose()
    for t in a.find_all(True):
        if t.get('id'):t['id']=mp[t['id']]
        for attr in ['aria-labelledby','aria-describedby','aria-controls','for']:
            if t.get(attr):t[attr]=' '.join(mp.get(x,x) for x in t[attr].split())
        for attr in ['marker-start','marker-mid','marker-end','clip-path','mask','filter','fill','stroke','style']:
            if t.get(attr) and 'url(#' in t[attr]:
                t[attr]=re.sub(r'url\(#([^)]*)\)',lambda m:'url(#'+mp.get(m[1],m[1])+')',t[attr])
        for attr in ['href','xlink:href']:
            if t.get(attr):
                t[attr],download=onelink(p,t[attr])
                if download:t['download']=download
        for attr in ['src','poster']:
            if t.get(attr) and norm(p,t[attr]):
                asset=R/norm(p,t[attr])[0]
                if asset.is_file():
                    t[attr]='data:'+(mimetypes.guess_type(asset.name)[0] or 'application/octet-stream')+';base64,'+base64.b64encode(asset.read_bytes()).decode()
    sec=single.new_tag('section',attrs={'class':'standalone-section','id':sid(p)})
    for t in list(a.contents):sec.append(t.extract())
    main.append(sec)

# Rebuild the shell from updated navigation; the old shell carried stale labels.
for selector in ['.book-rail','.site-header']:
    new=copy.deepcopy(cache['index.html'].select_one(selector))
    for a in new.select('a[href]'):a['href']=onelink('index.html',a['href'])[0]
    single.select_one(selector).replace_with(new)
single.title.string='AI 系统工程｜完整连续阅读版'
for style in single.select('style'):style.decompose()
css='\n'.join((R/t['href']).read_text() for t in cache['index.html'].select('link[rel="stylesheet"][href]'))
style=single.new_tag('style');style.string=css;single.head.append(style)
for script in single.select('script'):script.decompose()
datasets=[
    'window.COURSE_SEARCH='+json.dumps([dict(i,path=onelink('index.html',i['path'])[0]) for i in search],ensure_ascii=False)+';',
    (R/'assets/catalog.js').read_text()
]
for content in datasets+[(R/'assets'/f).read_text() for f in ['app.js','atelier.js','reader-navigation.js','figures.js']]:
    script=single.new_tag('script');script.string=content.replace('</script','<\\/script');single.body.append(script)
(R/'complete.html').write_text(str(single),encoding='utf-8')

# The editable Markdown uses the same text and stable anchors, including answers.
for e in canonical:
    page=e['path'];a=copy.deepcopy(cache[page].select_one('article.article'));out=R/'wiki'/Path(page).with_suffix('.md')
    out.parent.mkdir(parents=True,exist_ok=True)
    for t in a.select('.mobile-outline,.pager,.progress-row,.lesson-context,.footer,.breadcrumb,script,style'):t.decompose()
    for t in a.find_all(True):
        if t.get('href'):
            item=norm(page,t['href'])
            if item:
                target,anchor=item
                targetpath=R/'wiki'/Path(target).with_suffix('.md') if target in paths else R/target
                t['href']=os.path.relpath(targetpath,out.parent).replace(os.sep,'/')+('#'+anchor if anchor else '')
        if t.get('src'):
            item=norm(page,t['src'])
            if item:t['src']=os.path.relpath(R/item[0],out.parent).replace(os.sep,'/')
    raw={}
    for t in list(a.find_all(id=True)):
        if t.name in ['svg','details'] or t.find_parent(['svg','details']):continue
        token='WIKIRAWBLOCK'+str(len(raw))+'Z';raw[token]='<a id="'+t['id']+'"></a>';t.insert_before(token)
    for t in list(a.find_all(['details','svg'])):
        if t.parent is None or t.find_parent(['details','svg']):continue
        token='WIKIRAWBLOCK'+str(len(raw))+'Z';raw[token]=str(t);t.replace_with(token)
    md=markdownify(str(a),heading_style='ATX',bullets='-')
    for k,v in raw.items():md=md.replace(k,v)
    out.write_text('---\ntitle: '+json.dumps(e['title'],ensure_ascii=False)+'\ndescription: "主流程课程的可编辑正文"\n---\n\n'+md,encoding='utf-8')

report={'canonical_articles':len(canonical),'search_items':len(search),
        'single_sections':len(main.select(':scope > section')),'markdown_pages':len(canonical),
        'answers_indexed':True,'visible_question_ids_in_search':True,
        'source_of_truth':'canonical HTML; same curriculum and stable anchors'}
(R/'editorial/coverage-review/derived-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
