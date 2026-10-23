/* Local numerical record viewer. No network, model execution, or automatic playback. */
(()=>{'use strict';
const frames=window.MODEL_FRAMES||[];const hosts=[...document.querySelectorAll('.mc-player')];
const SHARED=window.__bookPlayers||(window.__bookPlayers=[]);
const stops=[];
document.addEventListener('visibilitychange',()=>{if(document.hidden)stops.forEach(s=>s());});
const watcher='IntersectionObserver'in window
 ?new IntersectionObserver(es=>es.forEach(e=>{if(!e.isIntersecting)e.target.__mcStop?.();}),{threshold:0})
 :null;
const ns='http://www.w3.org/2000/svg';
const fmt=(x,precision=6)=>typeof x==='boolean'?(x?'允许':'禁止'):Number.isInteger(x)?String(x):Number(x).toPrecision(precision).replace(/(\.\d*?[1-9])0+(?=e|$)/,'$1').replace(/\.0+(?=e|$)/,'');
function node(name,attrs={},text){const e=document.createElementNS(ns,name);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;return e;}
for(const host of hosts){let group='',i=0,list=[],timer=null;
 const select=host.querySelector('.mc-group'),range=host.querySelector('.mc-range'),play=host.querySelector('[data-mc=play]');
 const requested=(host.dataset.allowedGroups||'').split(',').filter(Boolean);const available=[...new Set(frames.map(f=>f.group))];const groups=requested.length?available.filter(g=>requested.some(r=>g.includes(r))):available; if(!groups.length)groups.push(...available);
 groups.forEach(g=>{const o=document.createElement('option');o.value=g;o.textContent=g;select.append(o);});
 function stop(){if(timer!==null)clearInterval(timer);timer=null;play.textContent='播放';play.setAttribute('aria-pressed','false');}
 function render(){if(!list.length){host.querySelector('.mc-count').textContent='0 / 0';return;}const f=list[i];host.dataset.frame=String(i);host.dataset.group=group;
  host.querySelector('.mc-count').textContent=`${i+1} / ${list.length}`;range.max=String(list.length-1);range.value=String(i);
  host.querySelector('.mc-run-label').textContent=f.input;
  host.querySelector('.mc-frame-title').textContent=f.title;
  host.querySelector('.mc-frame-note').textContent=f.description;
  host.querySelector('.mc-state').textContent=f.state;
  const rows=f.values.map(r=>Array.isArray(r)?r:[r]);const columns=f.columns||rows[0].map((_,j)=>`特征${j}`);
  const w=Math.max(660,155+rows[0].length*94),h=74+rows.length*46;
  const svg=node('svg',{viewBox:`0 0 ${w} ${h}`,role:'img','aria-label':f.group+'：'+f.title});svg.append(node('title',{},f.title));
  svg.append(node('rect',{x:0,y:0,width:w,height:h,fill:'#ffffff'}));
  columns.forEach((c,j)=>svg.append(node('text',{x:150+j*94+43,y:28,'text-anchor':'middle','font-size':14,fill:'#344963'},c)));
  rows.forEach((r,t)=>{svg.append(node('text',{x:10,y:66+t*46,'font-size':15,fill:'#344963'},f.rows?.[t]||`行${t}`));
   r.forEach((v,j)=>{svg.append(node('rect',{x:150+j*94,y:42+t*46,width:88,height:35,rx:3,fill:typeof v==='boolean'?(v?'#e4f0e9':'#edf0f3'):(Math.abs(v)>0?'#edf3f9':'#f5f6f8')}));svg.append(node('text',{x:150+j*94+44,y:66+t*46,'text-anchor':'middle','font-size':13,fill:'#183a5f'},fmt(v,4)));});});
  const art=host.querySelector('.mc-frame-figure');art.replaceChildren(svg);
  const wrap=document.createElement('div');wrap.className='table-wrap';const table=document.createElement('table'),thead=document.createElement('thead'),tr=document.createElement('tr');
  ['位置',...columns].forEach(c=>{const th=document.createElement('th');th.textContent=c;tr.append(th);});thead.append(tr);table.append(thead);const tbody=document.createElement('tbody');
  rows.forEach((r,t)=>{const tr=document.createElement('tr');const th=document.createElement('th');th.textContent=f.rows?.[t]||`行${t}`;tr.append(th);r.forEach(v=>{const td=document.createElement('td');td.textContent=fmt(v,10);tr.append(td);});tbody.append(tr);});table.append(tbody);wrap.append(table);host.querySelector('.mc-frame-table').replaceChildren(wrap);
  host.querySelector('[data-mc=prev]').disabled=i===0;host.querySelector('[data-mc=next]').disabled=i===list.length-1;
 }
 function choose(g){stop();group=g;list=frames.filter(f=>f.group===g);i=0;render();}
 select.addEventListener('change',()=>choose(select.value));range.addEventListener('input',()=>{stop();i=Number(range.value);render();});
 host.addEventListener('click',e=>{const b=e.target.closest('[data-mc]');if(!b)return;const act=b.dataset.mc;
  if(act==='play'){if(timer!==null){stop();return;}SHARED.forEach(s=>s());if(i===list.length-1)i=0;render();play.textContent='暂停';play.setAttribute('aria-pressed','true');timer=setInterval(()=>{if(i>=list.length-1){stop();return;}i++;render();if(i===list.length-1)stop();},2300);return;}
  stop();if(act==='prev')i=Math.max(0,i-1);if(act==='next')i=Math.min(list.length-1,i+1);if(act==='reset')i=0;render();
 });
 host.addEventListener('keydown',e=>{if(['INPUT','SELECT','BUTTON'].includes(e.target.tagName))return;if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();stop();i=Math.max(0,Math.min(list.length-1,i+(e.key==='ArrowRight'?1:-1)));render();}});
 stops.push(stop);SHARED.push(stop);host.__mcStop=stop;watcher?.observe(host);choose(groups[0]);
}
})();
