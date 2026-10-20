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
  if(!q.value.trim()||!v.value.trim()||!Number.isFinite(qv)||!Number.isFinite(vv)||Math.abs(qv)>5||Math.abs(vv)>20||![0,1].includes(i)){out.textContent='请使用有限数：Wq这一格在−5到5之间，Wv这一格在−20到20之间。';return;}
  const X=[[1,1],[1,-1]],Wq=[[qv,.5],[-.5,.5]],Wk=[[.5,.5],[.5,-.5]],Wv=[[vv,10],[5,-10]];
  const Q=mm(X,Wq),K=mm(X,Wk),V=mm(X,Wv),dots=mm(Q,tr(K))[i];
  const scores=dots.map((x,j)=>j<=i?x/Math.sqrt(2):-Infinity),m=Math.max(...scores),exp=scores.map(x=>Math.exp(x-m)),sum=exp.reduce((a,b)=>a+b,0),weights=exp.map(x=>x/sum),O=mm([weights],V)[0];
  out.textContent=`固定输入X = ${mat(X)}\n\n参数Wq = ${mat(Wq)}\n参数Wk = ${mat(Wk)}\n参数Wv = ${mat(Wv)}\n\n本次Q = XWq = ${mat(Q)}\n本次K = XWk = ${mat(K)}\n本次V = XWv = ${mat(V)}\n\n当前接收位置：${i}（${i===0?'我':'爱'}）\n当前q = ${row(Q[i])}\n与每行K的原始点积 = ${row(dots)}\n除以√2并屏蔽未来位置 = ${row(scores)}\n减去可读位置的最大分数 ${fmt(m)} 后取指数 = ${row(exp)}\n指数之和 = ${fmt(sum)}\n读取份额a = ${row(weights)}\n\n该行输出 = a × V = ${row(O)}\n第一格：${fmt(weights[0])}×${fmt(V[0][0])} + ${fmt(weights[1])}×${fmt(V[1][0])} = ${fmt(O[0])}\n第二格：${fmt(weights[0])}×${fmt(V[0][1])} + ${fmt(weights[1])}×${fmt(V[1][1])} = ${fmt(O[1])}\n\n权重矩阵W决定如何生成表示；份额a决定本次读入多少Value。上述结果是数值表示，不是最终Token。`;
  lab.dataset.result=JSON.stringify({Q,K,V,scores:scores.map(x=>Number.isFinite(x)?x:null),weights,output:O});
 }
 [q,v,pos].forEach(el=>{el.addEventListener('input',run);el.addEventListener('change',run)});
 lab.querySelector('[data-qkv-reset]').addEventListener('click',()=>{q.value='.5';v.value='5';pos.value='1';run()});run();
});
})();
