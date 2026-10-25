"""Rebuild derived search, standalone HTML and Markdown from canonical article HTML."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup,Tag
from markdownify import markdownify
import json,copy,base64,mimetypes,os,re
W=Path('/mnt/data/_content_audit_20261024');R=W/'build/AI_Systems_Engineering_Textbook_ZH';O=W/'original/AI_Systems_Engineering_Textbook_ZH'
canonical=json.loads((R/'editorial/canonical-pages.json').read_text());paths={e['path'] for e in canonical};moves=json.loads((W/'audit/moved-anchors.json').read_text())
def sid(p):return p[:-5].replace('/','--')
def norm(page,url):
 u=urlsplit(url)
 if u.scheme or u.netloc or not url:return None
 path=unquote(u.path);target=((R/page).parent/path) if path else R/page
 try:target=target.resolve().relative_to(R.resolve()).as_posix()
 except ValueError:return None
 anchor=unquote(u.fragment)
 if target+'#'+anchor in moves:target,anchor=moves[target+'#'+anchor].split('#',1)
 return target,anchor
cache={e['path']:BeautifulSoup((R/e['path']).read_text(),'lxml') for e in canonical}
search=[]
for e in canonical:
 page=e['path'];a=copy.deepcopy(cache[page].select_one('article.article'))
 for t in a.select('details.quiz-answer,.answer,.mobile-outline,.pager,.progress-row,.lesson-context,.source-note,script,style'):t.decompose()
 for h in a.find_all(['h2','h3']):
  if not h.get('id') or h.find_parent(['table','pre']):continue
  chunks=[h.get_text(' ',strip=True)]
  for x in h.next_siblings:
   if isinstance(x,Tag) and x.name in ['h2','h3']:break
   if isinstance(x,Tag):chunks.append(x.get_text(' ',strip=True))
  text='\n'.join(chunks)
  if len(text)>=30:search.append({'title':e['title']+' · '+h.get_text(' ',strip=True),'id':h['id'],'kind':e['kind'],'path':page+'#'+h['id'],'text':text})
(R/'assets/search-data.js').write_text('window.COURSE_SEARCH='+json.dumps(search,ensure_ascii=False)+';',encoding='utf-8')
old=BeautifulSoup((O/'complete.html').read_text(),'lxml');original=copy.deepcopy(old);main=old.select_one('article.article');main.clear()
idmaps={}
for e in canonical:
 p=e['path'];a=cache[p].select_one('article.article');oldsec=original.find(id=sid(p));olds={t['id'] for t in oldsec.find_all(id=True)} if oldsec else set()
 idmaps[p]={t['id']: (t['id'] if t['id'] in olds and sid(p)+'--'+t['id'] not in olds else sid(p)+'--'+t['id']) for t in a.find_all(id=True)}
def onelink(page,url):
 n=norm(page,url)
 if not n:return url,None
 target,anchor=n
 if target in paths:return '#'+(idmaps[target].get(anchor,sid(target)+'--'+anchor) if anchor else sid(target)),None
 p=R/target
 if p.is_file():return 'data:'+(mimetypes.guess_type(p.name)[0] or 'application/octet-stream')+';base64,'+base64.b64encode(p.read_bytes()).decode(),p.name
 return url,None
for e in canonical:
 p=e['path'];a=copy.deepcopy(cache[p].select_one('article.article'));mp=idmaps[p]
 for t in a.select('.pager,.progress-row,.breadcrumb,.footer'):t.decompose()
 for t in a.find_all(True):
  if t.get('id'):t['id']=mp[t['id']]
  for attr in ['aria-labelledby','aria-describedby','aria-controls','for']:
   if t.get(attr):t[attr]=' '.join(mp.get(x,x) for x in t[attr].split())
  for attr in ['marker-start','marker-mid','marker-end','clip-path','mask','filter','fill','stroke','style']:
   if t.get(attr) and 'url(#' in t[attr]:t[attr]=re.sub(r'url\(#([^)]*)\)',lambda m:'url(#'+mp.get(m[1],m[1])+')',t[attr])
  for attr in ['href','xlink:href']:
   if t.get(attr):
    t[attr],download=onelink(p,t[attr])
    if download:t['download']=download
  for attr in ['src','poster']:
   if t.get(attr) and norm(p,t[attr]):
    asset=R/norm(p,t[attr])[0]
    if asset.is_file():t[attr]='data:'+(mimetypes.guess_type(asset.name)[0] or 'application/octet-stream')+';base64,'+base64.b64encode(asset.read_bytes()).decode()
 sec=old.new_tag('section',attrs={'class':'standalone-section','id':sid(p)})
 for t in list(a.contents):sec.append(t.extract())
 main.append(sec)
for script in old.find_all('script'):
 if script.get_text().lstrip().startswith('window.COURSE_SEARCH='):
  data=[dict(i,path=onelink('index.html',i['path'])[0]) for i in search]
  script.string='window.COURSE_SEARCH='+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+';'
(R/'complete.html').write_text(str(old),encoding='utf-8')
# Markdown keeps details/summary exactly, so self-check answers remain collapsible.
for e in canonical:
 page=e['path'];a=copy.deepcopy(cache[page].select_one('article.article'));out=R/'wiki'/Path(page).with_suffix('.md')
 for t in a.select('.mobile-outline,.pager,.progress-row,.lesson-context,.footer,.breadcrumb,script,style'):t.decompose()
 for t in a.find_all(True):
  if t.get('href'):
   n=norm(page,t['href'])
   if n:
    target,anchor=n
    targetpath=R/'wiki'/Path(target).with_suffix('.md') if target in paths else R/target
    t['href']=os.path.relpath(targetpath,out.parent).replace(os.sep,'/')+('#'+anchor if anchor else '')
  if t.get('src'):
   n=norm(page,t['src'])
   if n:t['src']=os.path.relpath(R/n[0],out.parent).replace(os.sep,'/')
 # Preserve canonical heading/section ids through Markdown conversion using raw placeholders.
 raw={}
 for t in list(a.find_all(id=True)):
  if t.name in ['svg','details'] or t.find_parent(['svg','details']):continue
  token='WIKIRAWBLOCK'+str(len(raw))+'Z';raw[token]='<a id="'+t['id']+'"></a>'
  t.insert_before(token)
 for t in list(a.find_all(['details','svg'])):
  if t.parent is None or t.find_parent(['details','svg']):continue
  token='WIKIRAWBLOCK'+str(len(raw))+'Z';raw[token]=str(t);t.replace_with(token)
 md=markdownify(str(a),heading_style='ATX',bullets='-')
 for k,v in raw.items():md=md.replace(k,v)
 out.write_text('---\ntitle: '+json.dumps(e['title'],ensure_ascii=False)+'\ndescription: "主流程课程的可编辑正文"\n---\n\n'+md,encoding='utf-8')
(R/'editorial/content-review/derived-build.json').write_text(json.dumps({'canonical_articles':len(canonical),'search_items':len(search),'single_sections':len(main.select(':scope > section')),'markdown_pages':len(canonical),'source_of_truth':'canonical article HTML; no new teaching route'},ensure_ascii=False,indent=2))
print('derived built:',len(canonical),'articles;',len(search),'search items')
