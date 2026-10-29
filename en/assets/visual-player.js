/* No network, no eval, no auto-play. All frames use the same checked dataset. */
(()=>{'use strict';
 const DB=window.VISUAL_LESSONS||{}; const players=[];
 // One auto-advancing player at a time, across every kind of player on the page.
 const SHARED=window.__bookPlayers||(window.__bookPlayers=[]);
 const dialog=document.createElement('dialog');dialog.className='vb-dialog';dialog.innerHTML='<header><h2></h2><button type="button">Close figure</button></header><div class="vb-art"></div><p class="vb-caption"></p>';
 document.body.append(dialog);dialog.querySelector('button').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
 function init(el){if(el.dataset.ready)return;const id=el.dataset.vb, lesson=DB[id];if(!lesson||!lesson.frames?.length)return;el.dataset.ready='true';let i=0,timer=null;const $=s=>el.querySelector(s);
  const art=$('.vb-art'),caption=$('.vb-caption'),title=$('.vb-frame-title'),state=$('.vb-state'),equation=$('.vb-equation'),range=$('.vb-range'),status=$('.vb-status'),play=$('[data-vb-action="play"]'),prev=$('[data-vb-action="prev"]'),next=$('[data-vb-action="next"]'),speed=$('.vb-speed select');
  const stop=()=>{if(timer!==null){clearInterval(timer);timer=null;}play.textContent='Play';play.setAttribute('aria-pressed','false');el.dataset.playing='false';};
  function render(){const f=lesson.frames[i];art.innerHTML=(matchMedia('(max-width:680px)').matches&&f.mobileSvg)?f.mobileSvg:f.svg;title.textContent=`${i+1} / ${lesson.frames.length} · ${f.title}`;caption.textContent=f.explain;state.textContent=f.state||'The figure and the explanation together show the state at this step.';equation.textContent=f.equation||'';equation.hidden=!f.equation;range.value=String(i);range.setAttribute('aria-valuetext',`${i+1} / ${lesson.frames.length}:${f.title}`);status.textContent=`Step ${i+1} of ${lesson.frames.length} steps`;prev.disabled=i===0;next.disabled=i===lesson.frames.length-1;el.dataset.frame=String(i);if(i===lesson.frames.length-1)stop();}
  function go(v){stop();i=Math.max(0,Math.min(lesson.frames.length-1,Number(v)||0));render();}
  function start(){if(timer!==null){stop();return;}SHARED.forEach(s=>s());if(i===lesson.frames.length-1)i=0;render();el.dataset.playing='true';play.textContent='Pause';play.setAttribute('aria-pressed','true');timer=setInterval(()=>{if(document.hidden){stop();return;}i=Math.min(i+1,lesson.frames.length-1);render();},Number(speed.value)||4200);}
  prev.addEventListener('click',()=>go(i-1));next.addEventListener('click',()=>go(i+1));play.addEventListener('click',start);$('[data-vb-action="reset"]').addEventListener('click',()=>go(0));range.addEventListener('input',()=>go(range.value));speed.addEventListener('change',()=>{const active=timer!==null;stop();if(active)start();});
  $('[data-vb-action="zoom"]').addEventListener('click',()=>{stop();dialog.querySelector('h2').textContent=lesson.title+' · '+lesson.frames[i].title;dialog.querySelector('.vb-art').innerHTML=lesson.frames[i].svg;dialog.querySelector('.vb-caption').textContent=lesson.frames[i].explain;if(dialog.showModal)dialog.showModal();else art.classList.toggle('vb-expanded');});
  el.addEventListener('keydown',e=>{if(e.target.matches('input,select,button,a'))return;if(e.key==='ArrowRight'){e.preventDefault();go(i+1);}if(e.key==='ArrowLeft'){e.preventDefault();go(i-1);}if(e.key===' '){e.preventDefault();start();}});
  const container=el.closest('.vb-block')||el.parentElement;container.querySelectorAll('[data-vb-jump]').forEach(b=>b.addEventListener('click',()=>{go(b.dataset.vbJump);el.scrollIntoView({block:'nearest',behavior:'auto'});el.focus({preventScroll:true});}));
  const p={el,stop,go,get index(){return i;}};players.push(p);SHARED.push(stop);render();return p;
 }
 document.querySelectorAll('[data-vb]').forEach(init);document.addEventListener('visibilitychange',()=>{if(document.hidden)players.forEach(p=>p.stop());});
 if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>entries.forEach(en=>{if(!en.isIntersecting)players.find(p=>p.el===en.target)?.stop();}),{threshold:0});players.forEach(p=>observer.observe(p.el));}
 window.VisualBook={players,init};
})();
