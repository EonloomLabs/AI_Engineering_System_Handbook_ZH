/* Navigation owns its scroll position. It never scrolls the document to reveal a menu item. */
(()=>{
'use strict';
const body=document.body,rail=document.querySelector('.book-rail'),viewport=rail?.querySelector('.rail-scroll');
if(!rail||!viewport)return;
const page=body.dataset.page||'index.html',single=body.classList.contains('is-complete');
const entries=[...rail.querySelectorAll('a[data-target]')];
const byPage=new Map(entries.map(a=>[a.dataset.target,a]));
const groups=[...rail.querySelectorAll('details[data-group]')];
const memory=new Map(),prefix='ai-systems-textbook:reference-nav:1:';
const storage={read(k){try{return JSON.parse(localStorage.getItem(prefix+k)||'null')}catch(_){return memory.get(k)??null}},write(k,v){memory.set(k,v);try{localStorage.setItem(prefix+k,JSON.stringify(v))}catch(_){}}};
let current=single?'index.html':page,saveTimer=0,manualUntil=0,frame=0,restoring=false,ready=false;
function kind(p){return p.includes('/')?p.split('/')[0]:'reference'}
function active(){return byPage.get(current)||byPage.get(page)||byPage.get('index.html')}
function openAncestors(a){for(let n=a?.parentElement;n&&n!==rail;n=n.parentElement){if(n.tagName==='DETAILS')n.open=true}}
function selectedPathForHash(hash){let h;try{h=decodeURIComponent((hash||'').replace(/^#/,''))}catch(_){h=(hash||'').replace(/^#/,'')}
 if(!h)return null;
 return entries.filter(a=>{const s=a.dataset.section;return s&&(h===s||h.startsWith(s+'--'))}).sort((a,b)=>b.dataset.section.length-a.dataset.section.length)[0]?.dataset.target||null;
}
function mark(path){if(!byPage.has(path))return false;current=path;for(const a of entries){const yes=a.dataset.target===path;a.classList.toggle('active',yes);if(yes)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')}
 const a=active();openAncestors(a);const n=rail.querySelector('[data-nav-current-label]');if(n)n.textContent=a?.querySelector('.rail-code')?.textContent.trim()||a?.textContent.trim().slice(0,16)||'';return true;
}
function reveal({center=false,force=false}={}){const a=active();if(!a)return false;openAncestors(a);
 if(viewport.clientHeight<5)return false;
 if(!force&&Date.now()<manualUntil)return false;
 const v=viewport.getBoundingClientRect(),r=a.getBoundingClientRect(),pad=12;
 if(center||r.top<v.top+pad||r.bottom>v.bottom-pad){const y=viewport.scrollTop+(r.top-v.top)-Math.max(pad,(viewport.clientHeight-r.height)*.42);viewport.scrollTo({top:Math.max(0,Math.min(y,viewport.scrollHeight-viewport.clientHeight)),behavior:'instant'});}
 return true;
}
function save(){if(!ready||restoring)return;const gs={};groups.forEach(d=>gs[d.dataset.group]=d.open);storage.write('groups',gs);storage.write('pos:'+page,viewport.scrollTop);storage.write('module:'+kind(current),viewport.scrollTop);}
function saveSoon(){clearTimeout(saveTimer);saveTimer=setTimeout(save,90)}
function restore(){restoring=true;const gs=storage.read('groups');if(gs&&typeof gs==='object')groups.forEach(d=>{if(Object.hasOwn(gs,d.dataset.group))d.open=Boolean(gs[d.dataset.group])});
 if(single)mark(selectedPathForHash(location.hash)||current||'index.html');else mark(page);
 let y=storage.read('pos:'+page);if(!Number.isFinite(y))y=storage.read('module:'+kind(current));
 if(Number.isFinite(y))viewport.scrollTop=Math.max(0,y);
 reveal({force:true});restoring=false;ready=true;}
function onHash(){if(!single)return;const p=selectedPathForHash(location.hash);if(p){mark(p);requestAnimationFrame(()=>reveal({force:true}))}}
const sectionMap=single?new Map(entries.map(a=>[a.dataset.section,a.dataset.target])):null;
function updateFromDocument(){frame=0;if(!single)return;const sections=[...document.querySelectorAll('.complete-main section.standalone-section[id]')].filter(s=>sectionMap.has(s.id));let chosen=null;
 const edge=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--bar'))+52;
 for(const s of sections){if(s.getBoundingClientRect().top<=edge)chosen=s;else break;}
 const path=chosen?sectionMap.get(chosen.id):'index.html';if(path&&path!==current){mark(path);reveal();}}
viewport.addEventListener('scroll',saveSoon,{passive:true});
viewport.addEventListener('wheel',()=>manualUntil=Date.now()+1800,{passive:true});
viewport.addEventListener('pointerdown',()=>manualUntil=Date.now()+1800,{passive:true});
groups.forEach(d=>d.addEventListener('toggle',saveSoon));
entries.forEach(a=>a.addEventListener('click',()=>{save();if(single){mark(a.dataset.target);requestAnimationFrame(()=>reveal({force:true}))}}));
rail.querySelector('[data-locate-current]')?.addEventListener('click',()=>{manualUntil=0;reveal({center:true,force:true});save();const b=rail.querySelector('[data-locate-current]');b?.setAttribute('title','Capítulo actual localizado')});
addEventListener('pagehide',save);addEventListener('beforeunload',save);addEventListener('pageshow',()=>requestAnimationFrame(restore));
addEventListener('hashchange',onHash);addEventListener('popstate',()=>{onHash();requestAnimationFrame(()=>reveal({force:true}))});
addEventListener('resize',()=>requestAnimationFrame(()=>reveal()));
if(single)addEventListener('scroll',()=>{if(!frame)frame=requestAnimationFrame(updateFromDocument)},{passive:true});
const mo=new MutationObserver(()=>{if(body.classList.contains('nav-open'))requestAnimationFrame(()=>reveal({force:true}));});mo.observe(body,{attributes:true,attributeFilter:['class']});
requestAnimationFrame(()=>{restore();document.fonts?.ready.then(()=>requestAnimationFrame(()=>reveal()));});
window.ReaderNavigation={reveal,save,restore,activate(path){if(mark(path))reveal({force:true})},current(){return current},selectedPathForHash,diagnostics(){const a=active(),v=viewport.getBoundingClientRect(),r=a?.getBoundingClientRect();return {page,current,scrollTop:viewport.scrollTop,height:viewport.clientHeight,total:viewport.scrollHeight,selected:entries.filter(a=>a.getAttribute('aria-current')==='page').length,visible:!!r&&r.top>=Math.max(v.top,rail.getBoundingClientRect().top,0)&&r.bottom<=Math.min(v.bottom,rail.getBoundingClientRect().bottom,innerHeight)&&r.left>=0&&r.right<=innerWidth,documentY:scrollY}}};
})();
