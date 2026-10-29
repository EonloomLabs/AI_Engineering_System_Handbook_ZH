/* Local figure viewer: user-controlled zoom dialog. No network or auto-play. */
(()=>{'use strict';
const d=document.createElement('dialog');d.className='mx-dialog';
d.setAttribute('aria-labelledby','mx-dialog-title');
d.innerHTML='<header><h2 id="mx-dialog-title">Ilustraciones del texto</h2><button type="button" data-mx-close>Cerrar la ilustración</button></header><div class="mx-art" tabindex="0"></div><p>Arrastrar o desplazar para ver; Esc cierra. Figura y texto usan las mismas entradas.</p>';
document.body.append(d);
let returnFocus=null;
d.querySelector('[data-mx-close]').addEventListener('click',()=>d.close());
// Give the trigger its focus back, otherwise keyboard users land at the top of the page.
d.addEventListener('close',()=>{returnFocus?.focus({preventScroll:true});returnFocus=null;});
d.addEventListener('click',e=>{if(e.target!==d)return;const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();});
document.addEventListener('click',e=>{
 const b=e.target.closest('.mx-zoom');if(!b)return;
 const f=b.closest('.mx-figure');if(!f)return;
 const svg=f.querySelector('.mx-desktop svg')||f.querySelector('svg');if(!svg)return;
 returnFocus=b;
 d.querySelector('h2').textContent=f.querySelector('.mx-figure-head span')?.textContent?.trim()||'Ilustraciones del texto';
 d.querySelector('.mx-art').innerHTML=svg.outerHTML;
 if(typeof d.showModal==='function')d.showModal();
});
})();
