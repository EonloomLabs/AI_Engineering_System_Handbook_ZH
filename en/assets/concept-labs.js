(()=>{'use strict';
const mm=(a,b)=>a.map(row=>b[0].map((_,j)=>row.reduce((sum,x,k)=>sum+x*b[k][j],0)));
const tr=a=>a[0].map((_,i)=>a.map(row=>row[i]));
const fmt=x=>Number.isFinite(x)?(Math.abs(x)<1e-12?'0':Number(x.toFixed(9)).toString()):'-∞';
const row=x=>'['+x.map(fmt).join(', ')+']';
const mat=x=>'['+x.map(row).join(',\n     ')+']';
document.querySelectorAll('[data-qkv-lab]').forEach(lab=>{
 const q=lab.querySelector('[data-qkv-q]'),v=lab.querySelector('[data-qkv-v]'),pos=lab.querySelector('[data-qkv-position]'),out=lab.querySelector('[data-qkv-output]');
 function run(){
  const qv=Number(q.value),vv=Number(v.value),i=Number(pos.value);
  if(!q.value.trim()||!v.value.trim()||!Number.isFinite(qv)||!Number.isFinite(vv)||Math.abs(qv)>5||Math.abs(vv)>20||![0,1].includes(i)){out.textContent='Use finite numbers: this cell of Wq must be between −5 and 5, and this cell of Wv between −20 and 20.';return;}
  const X=[[1,1],[1,-1]],Wq=[[qv,.5],[-.5,.5]],Wk=[[.5,.5],[.5,-.5]],Wv=[[vv,10],[5,-10]];
  const Q=mm(X,Wq),K=mm(X,Wk),V=mm(X,Wv),dots=mm(Q,tr(K))[i];
  const scores=dots.map((x,j)=>j<=i?x/Math.sqrt(2):-Infinity),m=Math.max(...scores),exp=scores.map(x=>Math.exp(x-m)),sum=exp.reduce((a,b)=>a+b,0),weights=exp.map(x=>x/sum),O=mm([weights],V)[0];
  out.textContent=`Fixed input X = ${mat(X)}\n\nParameter Wq = ${mat(Wq)}\nParameter Wk = ${mat(Wk)}\nParameter Wv = ${mat(Wv)}\n\nQ in this run = XWq = ${mat(Q)}\nK in this run = XWk = ${mat(K)}\nV in this run = XWv = ${mat(V)}\n\nCurrent receiving position: ${i} (${i===0?'我':'爱'})\nCurrent q = ${row(Q[i])}\nRaw dot products with each row of K = ${row(dots)}\nDivide by √2 and mask future positions = ${row(scores)}\nSubtract the maximum score at a readable position ${fmt(m)} and exponentiate = ${row(exp)}\nSum of exponentials = ${fmt(sum)}\nRead shares a = ${row(weights)}\n\nOutput of this row = a × V = ${row(O)}\nFirst cell: ${fmt(weights[0])}×${fmt(V[0][0])} + ${fmt(weights[1])}×${fmt(V[1][0])} = ${fmt(O[0])}\nSecond cell: ${fmt(weights[0])}×${fmt(V[0][1])} + ${fmt(weights[1])}×${fmt(V[1][1])} = ${fmt(O[1])}\n\nThe weight matrix W determines how representations are generated; the shares a determine how much Value is read in this run. These results are numerical representations, not final tokens.`;
  lab.dataset.result=JSON.stringify({Q,K,V,scores:scores.map(x=>Number.isFinite(x)?x:null),weights,output:O});
 }
 [q,v,pos].forEach(el=>{el.addEventListener('input',run);el.addEventListener('change',run)});
 lab.querySelector('[data-qkv-reset]').addEventListener('click',()=>{q.value='.5';v.value='5';pos.value='1';run()});run();
});
})();
