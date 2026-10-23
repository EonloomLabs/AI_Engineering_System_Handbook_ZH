
/* Local diagram viewer: user-controlled zoom. No network or auto-play. */
(()=>{"use strict";
const dlg=document.createElement("dialog");dlg.className="d-dialog";
dlg.innerHTML='<div class="d-tools"><h2>图解</h2><button type="button" data-dzoom="-25" aria-label="缩小图形">−</button><button type="button" data-dzoom="reset">适合窗口</button><button type="button" data-dzoom="25" aria-label="放大图形">＋</button><button type="button" data-dclose>关闭</button></div><div class="d-art" tabindex="0"></div><p class="d-source-note">图形与正文采用同一组输入。可滚动查看；Esc关闭。</p>';
document.body.append(dlg);let z=100,returnFocus=null;
const setZoom=()=>dlg.querySelector('.d-art').style.setProperty('--diagram-zoom',z+'%');
dlg.querySelector('[data-dclose]').onclick=()=>dlg.close();
dlg.querySelectorAll('[data-dzoom]').forEach(b=>b.onclick=()=>{z=b.dataset.dzoom==='reset'?100:Math.max(50,Math.min(300,z+Number(b.dataset.dzoom)));setZoom()});
dlg.addEventListener('close',()=>returnFocus?.focus({preventScroll:true}));
document.addEventListener('click',e=>{
 const b=e.target.closest('.d-zoom');if(!b)return;
 const f=b.closest('.d-figure');const svg=f?.querySelector('.d-desktop svg')||f?.querySelector('svg');if(!svg)return;
 returnFocus=b;dlg.querySelector('h2').textContent=f.querySelector('.d-head strong')?.textContent||'图解';
 dlg.querySelector('.d-art').innerHTML=svg.outerHTML;z=100;setZoom();
 if(typeof dlg.showModal==='function')dlg.showModal();
});
dlg.addEventListener('click',e=>{if(e.target!==dlg)return;const r=dlg.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dlg.close()});
})();
