from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlsplit,unquote
from playwright.sync_api import sync_playwright
import json,base64,mimetypes,re
W=Path('/mnt/data/_content_audit_20261024');R=W/'build/AI_Systems_Engineering_Textbook_ZH';Q=W/'qa';Q.mkdir(exist_ok=True)
def inline(rel):
 p=R/rel;s=BeautifulSoup(p.read_text(),'lxml')
 for t in s.select('link[rel="stylesheet"][href]'):
  local=(p.parent/unquote(urlsplit(t['href']).path)).resolve()
  if local.is_file():
   tag=s.new_tag('style');tag.string=local.read_text();t.replace_with(tag)
 for t in s.select('script[src]'):
  local=(p.parent/unquote(urlsplit(t['src']).path)).resolve()
  if local.is_file(): del t['src'];t.string=local.read_text().replace('</script','<\\/script')
 for t in s.select('img[src]'):
  if not urlsplit(t['src']).scheme:
   local=(p.parent/unquote(urlsplit(t['src']).path)).resolve()
   if local.is_file():t['src']='data:'+(mimetypes.guess_type(local.name)[0] or 'application/octet-stream')+';base64,'+base64.b64encode(local.read_bytes()).decode()

 # Search is normally lazy-loaded by the reader. Preload the identical local data
 # because this test's about:blank environment blocks dynamic external script requests.
 if 'window.COURSE_SEARCH=' not in str(s):
  tag=s.new_tag('script');tag.string=(R/'assets/search-data.js').read_text().replace('</script','<\\/script')
  first=s.find('script')
  if first:first.insert_before(tag)
  else:s.body.append(tag)
 return str(s)
pages=['index.html','foundations/05.html','foundations/11.html','foundations/14.html','foundations/16.html','foundations/17.html','foundations/18.html','chapters/02.html','chapters/04.html','chapters/05.html','chapters/06.html','chapters/08.html','chapters/18.html','chapters/23.html','chapters/27.html','labs/projects/assignment4.html','sources.html']
report={'mode':'Chromium set_content with actual local CSS/JS/images inlined; file:// and test-origin navigation blocked by browser policy','layouts':[],'interactions':[],'errors':[],'screenshots':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width in [1440,390]:
  for rel in pages:
   page=b.new_page(viewport={'width':width,'height':960});errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
   page.set_content(inline(rel),wait_until='load');page.wait_for_timeout(120)
   metrics=page.evaluate('''()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,articleWidth:document.querySelector('article').getBoundingClientRect().width,openAnswers:document.querySelectorAll('details.quiz-answer[open]').length,heading:document.querySelector('h1')?.innerText})''')
   report['layouts'].append({'page':rel,**metrics,'pass':metrics['scrollWidth']<=width+1 and metrics['openAnswers']==0})
   if errs:report['errors'].append({'page':rel,'width':width,'errors':errs})
   if rel in ['index.html','foundations/11.html']:
    if rel=='foundations/11.html':page.locator('#core-qkv-2--mc-section-2').scroll_into_view_if_needed()
    out=Q/(rel.replace('/','-')+f'-{width}.png');page.screenshot(path=str(out));report['screenshots'].append(out.name)
   page.close()
 # Important actual controls on independent page
 page=b.new_page(viewport={'width':1440,'height':960});page.set_content(inline('foundations/16.html'),wait_until='load');page.wait_for_timeout(300)
 quiz=page.locator('details.quiz-answer').first
 report['interactions'].append({'name':'independent answer initially closed','pass':quiz.get_attribute('open') is None})
 quiz.locator('summary').click();report['interactions'].append({'name':'independent answer expands','pass':quiz.get_attribute('open') is not None})
 quiz.locator('summary').click();report['interactions'].append({'name':'independent answer collapses','pass':quiz.get_attribute('open') is None})
 page.locator('[data-search]').first.click();page.locator('#command-input').fill('恢复优化器');page.wait_for_timeout(400)
 report['interactions'].append({'name':'new text available in command search','pass':page.locator('#command-results a').count()>0,'sample':page.locator('#command-results').inner_text()[:180]})
 page.keyboard.press('Escape');report['interactions'].append({'name':'command search closes','pass':not page.locator('#command-search').is_visible()})
 page.locator('[data-settings]').first.click();report['interactions'].append({'name':'reading settings opens','pass':page.locator('#reading-settings').is_visible()});page.keyboard.press('Escape')
 # selected item scroll only on desktop. It is already selected in independent HTML.
 page.locator('[data-locate-current]').click();page.wait_for_timeout(150)
 visible=page.evaluate('''()=>{const a=document.querySelector('.rail-scroll a[aria-current="page"]'),r=document.querySelector('.rail-scroll');if(!a||!r)return false;const x=a.getBoundingClientRect(),y=r.getBoundingClientRect();return x.top>=y.top-1&&x.bottom<=y.bottom+1}''')
 report['interactions'].append({'name':'locate current sidebar item','pass':visible});page.close()
 # Mobile drawer
 page=b.new_page(viewport={'width':390,'height':844});page.set_content(inline('foundations/18.html'),wait_until='load');page.wait_for_timeout(100)
 page.locator('[data-studio-menu]').click();page.wait_for_timeout(200)
 report['interactions'].append({'name':'mobile menu opens','pass':page.locator('body').evaluate("e=>e.classList.contains('nav-open')")})
 page.keyboard.press('Escape');page.close()
 # Whole single-file content: no external dependencies needed
 page=b.new_page(viewport={'width':1920,'height':1080});errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
 page.set_content((R/'complete.html').read_text(),wait_until='load');page.wait_for_timeout(400)
 report['interactions'].append({'name':'standalone contains 94 canonical sections','pass':page.locator('article.article > section.standalone-section').count()==94})
 report['interactions'].append({'name':'standalone has no open exercise answers','pass':page.locator('details.quiz-answer[open]').count()==0})
 page.locator('[data-search]').first.click();page.locator('#command-input').fill('恢复优化器');page.wait_for_timeout(300)
 report['interactions'].append({'name':'standalone new-text search','pass':page.locator('#command-results a').count()>0,'results':page.locator('#command-results a').count()})
 page.keyboard.press('Escape');page.evaluate("document.getElementById('foundations--11--core-qkv-2--mc-section-2').scrollIntoView()")
 page.wait_for_timeout(300);out=Q/'standalone-qkv-1920.png';page.screenshot(path=str(out));report['screenshots'].append(out.name)
 report['layouts'].append({'page':'complete.html','width':1920,'scrollWidth':page.evaluate('document.documentElement.scrollWidth'),'pass':page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')})
 if errs:report['errors'].append({'page':'complete.html','errors':errs})
 page.close();b.close()
(R/'editorial/content-review/browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'layouts':len(report['layouts']),'layout_failed':[x for x in report['layouts'] if not x['pass']],'interactions':report['interactions'],'errors':report['errors']},ensure_ascii=False,indent=2))
