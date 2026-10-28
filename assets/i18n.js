/* Interface localisation. No network: the catalogue ships as i18n-data.js so
   this works from file:// as well as from a static host.
   Only the shell is translated; lesson text stays in Chinese by design. */
(()=>{'use strict';
const BASE='zh-CN';
const DATA=window.I18N_STRINGS||{};
const META=window.I18N_META||{locales:[BASE],rtl:[],names:{}};
const RTL=new Set(META.rtl||[]);
const KEY='ai-systems-textbook:lang';

const store={
 get(){try{return localStorage.getItem(KEY)}catch(_){return null}},
 set(v){try{localStorage.setItem(KEY,v)}catch(_){}}
};

function supported(code){return Object.prototype.hasOwnProperty.call(DATA,code)}

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
  const v=t(el.dataset.i18n,null);
  if(v!==null&&v!==undefined)el.textContent=v;
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

/* The body text is not translated. Say so rather than letting a reader
   assume the lesson will follow the interface language. */
function notice(){
 let el=document.querySelector('[data-i18n-notice]');
 if(current===BASE){if(el)el.hidden=true;return;}
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
 sel.addEventListener('change',()=>{store.set(sel.value);apply(sel.value);});
 wrap.append(sel);
 host.append(wrap);
 sel.setAttribute('aria-label',t('lang.aria','Language'));
 document.addEventListener('i18n:change',()=>{
  sel.value=current;
  sel.setAttribute('aria-label',t('lang.aria','Language'));
 });
}

window.I18N={t,apply,get lang(){return current},locales:META.locales||[BASE],isRTL:()=>RTL.has(current)};
const start=()=>{apply(pick());switcher();};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);
else start();
})();
