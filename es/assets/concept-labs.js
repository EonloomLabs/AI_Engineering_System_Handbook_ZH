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
  if(!q.value.trim()||!v.value.trim()||!Number.isFinite(qv)||!Number.isFinite(vv)||Math.abs(qv)>5||Math.abs(vv)>20||![0,1].includes(i)){out.textContent='Utilizar números finitos: esta celda de Wq entre −5 y 5 y esta celda de Wv entre −20 y 20.';return;}
  const X=[[1,1],[1,-1]],Wq=[[qv,.5],[-.5,.5]],Wk=[[.5,.5],[.5,-.5]],Wv=[[vv,10],[5,-10]];
  const Q=mm(X,Wq),K=mm(X,Wk),V=mm(X,Wv),dots=mm(Q,tr(K))[i];
  const scores=dots.map((x,j)=>j<=i?x/Math.sqrt(2):-Infinity),m=Math.max(...scores),exp=scores.map(x=>Math.exp(x-m)),sum=exp.reduce((a,b)=>a+b,0),weights=exp.map(x=>x/sum),O=mm([weights],V)[0];
  out.textContent=`Entrada fija X = ${mat(X)}\n\nParámetro Wq = ${mat(Wq)}\nParámetro Wk = ${mat(Wk)}\nParámetro Wv = ${mat(Wv)}\n\nQ actual = XWq = ${mat(Q)}\nK actual = XWk = ${mat(K)}\nV actual = XWv = ${mat(V)}\n\nPosición receptora actual:${i}(${i===0?'我':'爱'})\nq actual = ${row(Q[i])}\nProductos escalares originales con cada fila de K = ${row(dots)}\nDividir por √2 y enmascarar las posiciones futuras = ${row(scores)}\nRestar la puntuación máxima de las posiciones legibles ${fmt(m)} antes de aplicar la exponencial = ${row(exp)}\nSuma de exponenciales = ${fmt(sum)}\nProporciones de lectura a = ${row(weights)}\n\nSalida de esta fila = a × V = ${row(O)}\nPrimera celda:${fmt(weights[0])}×${fmt(V[0][0])} + ${fmt(weights[1])}×${fmt(V[1][0])} = ${fmt(O[0])}\nSegunda celda:${fmt(weights[0])}×${fmt(V[0][1])} + ${fmt(weights[1])}×${fmt(V[1][1])} = ${fmt(O[1])}\n\nLa matriz de pesos W determina cómo generar la representación; las proporciones a determinan cuánto Value se incorpora esta vez. Los resultados anteriores son representaciones numéricas, no tokens finales.`;
  lab.dataset.result=JSON.stringify({Q,K,V,scores:scores.map(x=>Number.isFinite(x)?x:null),weights,output:O});
 }
 [q,v,pos].forEach(el=>{el.addEventListener('input',run);el.addEventListener('change',run)});
 lab.querySelector('[data-qkv-reset]').addEventListener('click',()=>{q.value='.5';v.value='5';pos.value='1';run()});run();
});
})();
