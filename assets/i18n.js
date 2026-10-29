/* Localisation. No network: the catalogue ships as i18n-data.js so this works
   from file:// as well as from a static host.

   A language can be present in two ways. Every language in META.locales has a
   translated shell, swapped in place. A language in META.editions also has the
   whole book translated, under its own directory (en/foundations/05.html beside
   foundations/05.html), so choosing it navigates to the twin of the page you
   are on rather than translating the furniture around Chinese text. */
(()=>{'use strict';
const BASE='zh-CN';
const DATA=window.I18N_STRINGS||{};
const META=window.I18N_META||{locales:[BASE],rtl:[],names:{}};
const RTL=new Set(META.rtl||[]);
const EDITIONS=new Set(META.editions||[BASE]);   // languages the whole book exists in
const KEY='ai-systems-textbook:lang';

const store={
 get(){try{return localStorage.getItem(KEY)}catch(_){return null}},
 set(v){try{localStorage.setItem(KEY,v)}catch(_){}}
};

function supported(code){return Object.prototype.hasOwnProperty.call(DATA,code)}

/* Where the twin of this page lives in another edition.

   data-root is the way back to the edition's own root, so its number of '../'
   says how many path segments below that root this page sits. Those segments
   plus the file name are the page's path within its edition; what precedes
   them is the edition root, carrying the current language's directory when we
   are inside one. Swapping that one segment gives the same page in the other
   edition, and keeps working from a subdirectory or from file://. */
function twin(lang){
 const root=(document.body&&document.body.dataset.root)||'';
 const depth=(root.match(/\.\.\//g)||[]).length;
 const parts=decodeURIComponent(location.pathname).split('/');
 let file=parts.pop();
 if(!file)file='index.html';
 const rel=parts.splice(Math.max(0,parts.length-depth),depth).concat(file);
 const last=parts[parts.length-1];
 if(last&&last!==BASE&&EDITIONS.has(last))parts.pop();
 return parts.concat(lang===BASE?[]:[lang],rel).join('/')+location.hash;
}

function pick(){
 const saved=store.get();
 if(saved&&supported(saved))return saved;
 for(const want of (navigator.languages||[navigator.language||''])){
  if(!want)continue;
  if(supported(want))return want;                       // zh-TW, pt-BR
  const short=want.split('-')[0];
  const hit=(META.locales||[]).find(c=>c===short||c.split('-')[0]===short);
  if(hit)return hit;
 }
 return BASE;
}

let current=BASE;
function t(key,fallback){
 const table=DATA[current]||{};
 if(key in table)return table[key];
 const base=DATA[BASE]||{};
 return (key in base)?base[key]:(fallback!==undefined?fallback:key);
}

function apply(code){
 current=supported(code)?code:BASE;
 const html=document.documentElement;
 html.lang=current;
 html.dir=RTL.has(current)?'rtl':'ltr';
 html.dataset.lang=current;
 document.querySelectorAll('[data-i18n]').forEach(el=>{
  let v=t(el.dataset.i18n,null);
  if(v===null||v===undefined)return;
  // Numeric slots carried on the element, e.g. a lesson range.
  for(const k of Object.keys(el.dataset)){
   if(k.length===1)v=v.split('{'+k+'}').join(el.dataset[k]);
  }
  // Write into the element's own text, not over its children: some of these
  // elements hold a decorative arrow or a nested data-i18n note, and
  // textContent would delete both.
  const own=Array.from(el.childNodes).find(n=>n.nodeType===3&&n.textContent.trim());
  if(own)own.textContent=v; else if(el.children.length)el.insertBefore(document.createTextNode(v),el.firstChild); else el.textContent=v;
 });
 document.querySelectorAll('[data-i18n-attr]').forEach(el=>{
  el.dataset.i18nAttr.split(';').forEach(pair=>{
   const [attr,key]=pair.split(':');
   if(!attr||!key)return;
   const v=t(key.trim(),null);
   if(v!==null&&v!==undefined)el.setAttribute(attr.trim(),v);
  });
 });
 notice();
 document.dispatchEvent(new CustomEvent('i18n:change',{detail:{lang:current}}));
}

/* Outside a full edition the body text is not translated. Say so rather than
   letting a reader assume the lesson will follow the interface language. */
function notice(){
 let el=document.querySelector('[data-i18n-notice]');
 if(current===BASE||EDITIONS.has(current)){if(el)el.hidden=true;return;}
 if(!el){
  const main=document.querySelector('.reading-main .article,.home-article,main');
  if(!main)return;
  el=document.createElement('p');
  el.className='i18n-notice';
  el.setAttribute('data-i18n-notice','');
  main.insertBefore(el,main.firstChild);
 }
 el.hidden=false;
 el.textContent=t('lang.bodyNotice','');
}

function switcher(){
 const host=document.querySelector('.site-actions');
 if(!host||host.querySelector('[data-lang-select]'))return;
 const wrap=document.createElement('label');
 wrap.className='lang-switch';
 const sel=document.createElement('select');
 sel.setAttribute('data-lang-select','');
 (META.locales||[]).forEach(code=>{
  const o=document.createElement('option');
  o.value=code;
  o.textContent=(META.names||{})[code]||code;          // endonym, not a translated name
  sel.append(o);
 });
 sel.value=current;
 sel.addEventListener('change',()=>{
  const next=sel.value;
  store.set(next);
  // A full edition is a different set of pages, so go there. Without one,
  // translate the shell in place and let notice() say the text stays Chinese.
  if(EDITIONS.has(next)&&next!==current){location.assign(twin(next));return;}
  apply(next);
 });
 wrap.append(sel);
 host.append(wrap);
 sel.setAttribute('aria-label',t('lang.aria','Language'));
 document.addEventListener('i18n:change',()=>{
  sel.value=current;
  sel.setAttribute('aria-label',t('lang.aria','Language'));
 });
}

window.I18N={t,apply,twin,get lang(){return current},locales:META.locales||[BASE],editions:[...EDITIONS],isRTL:()=>RTL.has(current)};
/* Which edition this page belongs to, read from the path rather than from
   html lang: lang says what the page is written in, and we need to know where
   it sits before deciding whether to move. */
function edition(){
 const root=(document.body&&document.body.dataset.root)||'';
 const depth=(root.match(/\.\.\//g)||[]).length;
 const parts=decodeURIComponent(location.pathname).split('/');
 parts.pop();                                     // the file name, or '' for a directory URL
 parts.splice(Math.max(0,parts.length-depth),depth);
 const last=parts[parts.length-1];
 return last&&last!==BASE&&EDITIONS.has(last)?last:BASE;
}

const start=()=>{
 const want=pick();
 // The choice follows the reader from page to page: arriving at a Chinese page
 // with English chosen should open its English twin, not translate the shell
 // around Chinese prose. Only complete editions are listed, so the twin exists.
 if(EDITIONS.has(want)&&want!==edition()){location.replace(twin(want));return;}
 apply(want);
 switcher();
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);
else start();
})();
