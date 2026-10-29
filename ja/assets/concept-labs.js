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
  if(!q.value.trim()||!v.value.trim()||!Number.isFinite(qv)||!Number.isFinite(vv)||Math.abs(qv)>5||Math.abs(vv)>20||![0,1].includes(i)){out.textContent='有限の数を使ってください。Wqのこのマスは−5から5、Wvのこのマスは−20から20の範囲です。';return;}
  const X=[[1,1],[1,-1]],Wq=[[qv,.5],[-.5,.5]],Wk=[[.5,.5],[.5,-.5]],Wv=[[vv,10],[5,-10]];
  const Q=mm(X,Wq),K=mm(X,Wk),V=mm(X,Wv),dots=mm(Q,tr(K))[i];
  const scores=dots.map((x,j)=>j<=i?x/Math.sqrt(2):-Infinity),m=Math.max(...scores),exp=scores.map(x=>Math.exp(x-m)),sum=exp.reduce((a,b)=>a+b,0),weights=exp.map(x=>x/sum),O=mm([weights],V)[0];
  out.textContent=`固定入力X = ${mat(X)}\n\nパラメーターWq = ${mat(Wq)}\nパラメーターWk = ${mat(Wk)}\nパラメーターWv = ${mat(Wv)}\n\n今回のQ = XWq = ${mat(Q)}\n今回のK = XWk = ${mat(K)}\n今回のV = XWv = ${mat(V)}\n\n現在の受け手の位置：${i}（${i===0?'我':'爱'}）\n現在のq = ${row(Q[i])}\n各行のKとの元の内積 = ${row(dots)}\n√2で割り、未来の位置を遮断 = ${row(scores)}\n参照可能な位置の最大スコア ${fmt(m)} を引いてから指数関数を適用 = ${row(exp)}\n指数の和 = ${fmt(sum)}\n読み取りの割合a = ${row(weights)}\n\nこの行の出力 = a × V = ${row(O)}\n一つ目のセル：${fmt(weights[0])}×${fmt(V[0][0])} + ${fmt(weights[1])}×${fmt(V[1][0])} = ${fmt(O[0])}\n二つ目のセル：${fmt(weights[0])}×${fmt(V[0][1])} + ${fmt(weights[1])}×${fmt(V[1][1])} = ${fmt(O[1])}\n\n重み行列Wは表現の生成方法を決め、割合aは今回読み込むValueの量を決めます。これらの結果は数値表現であり、最終的なトークンではありません。`;
  lab.dataset.result=JSON.stringify({Q,K,V,scores:scores.map(x=>Number.isFinite(x)?x:null),weights,output:O});
 }
 [q,v,pos].forEach(el=>{el.addEventListener('input',run);el.addEventListener('change',run)});
 lab.querySelector('[data-qkv-reset]').addEventListener('click',()=>{q.value='.5';v.value='5';pos.value='1';run()});run();
});
})();
