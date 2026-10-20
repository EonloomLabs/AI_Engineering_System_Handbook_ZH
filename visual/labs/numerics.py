"""Deterministic teaching calculations. Python >=3.10, standard library only.
These are small teaching systems, not measured commercial model outputs.
"""
from __future__ import annotations
import math
from typing import Sequence

def softmax(xs):
    if not xs or any(not math.isfinite(x) for x in xs): raise ValueError('finite nonempty scores required')
    m=max(xs);ex=[math.exp(x-m) for x in xs];s=sum(ex)
    return [e/s for e in ex]
def transpose(a): return [list(c) for c in zip(*a)]
def matmul(a,b):
    if not a or not b or any(len(r)!=len(b) for r in a):raise ValueError('shape mismatch')
    if any(len(r)!=len(b[0]) for r in b):raise ValueError('ragged matrix')
    return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def inv(a):
    n=len(a);m=[list(map(float,r))+[float(i==j) for j in range(n)] for i,r in enumerate(a)]
    for c in range(n):
        pivot=max(range(c,n),key=lambda i:abs(m[i][c]));m[c],m[pivot]=m[pivot],m[c]
        if abs(m[c][c])<1e-12:raise ValueError('singular')
        d=m[c][c];m[c]=[x/d for x in m[c]]
        for i in range(n):
            if i!=c:
                f=m[i][c];m[i]=[x-f*y for x,y in zip(m[i],m[c])]
    return [r[n:] for r in m]
E=[[0.,0.,0.,0.],[.2,-.1,.7,.4],[-.3,.8,.1,.5],[.6,.2,-.4,.9],[.1,-.5,.9,.3],[-.2,.4,.5,-.6],[.15,-.2,.05,.1]]
WORDS=['PAD','我','爱','学习','你','！','EOS']
I=[[float(i==j) for j in range(4)] for i in range(4)]
WQ=[[1,.1,0,0],[0,1,.1,0],[0,0,1,.1],[.1,0,0,1]]
WK=I
WV=[[.8,0,.1,0],[0,.8,0,.1],[.1,0,.8,0],[0,.1,0,.8]]
WF=[[.3,0,.1,0],[0,.3,0,.1],[.1,0,.3,0],[0,.1,0,.3]]

def run_tokens(ids,cache=None):
    """Single head, one block; residual+0.1*tanh FFN. No LN/RoPE/dropout.
    cache holds the K/V of *processed* tokens, not yet selected output.
    """
    keys=[list(r) for r in (cache or {}).get('k',[])];values=[list(r) for r in (cache or {}).get('v',[])]
    rows=[]
    for token in ids:
        x=list(E[token]);q=matmul([x],WQ)[0];k=matmul([x],WK)[0];v=matmul([x],WV)[0]
        keys.append(k);values.append(v)
        scores=[sum(a*b for a,b in zip(q,kk))/2 for kk in keys]
        p=softmax(scores);a=[sum(w*vv[j] for w,vv in zip(p,values)) for j in range(4)]
        r=[u+v for u,v in zip(x,a)]
        ff=[.1*math.tanh(z) for z in matmul([r],WF)[0]]
        h=[u+v for u,v in zip(r,ff)]
        rows.append({'id':token,'x':x,'q':q,'k':k,'v':v,'scores':scores,'attention':p,'mixed':a,'residual':r,'ff':ff,'hidden':h})
    return rows,{'k':keys,'v':values}

def generation():
    """Fit only a tiny output head to THREE prescribed prefixes, then run
    autoregressive decoding. Exact fit is a teaching construction, not training
    a general language model. Output head and all intermediate values are saved.
    """
    prefixes=[[1,2],[1,2,3],[1,2,3,5]];targets=[3,5,6]
    H=[run_tokens(x)[0][-1]['hidden'] for x in prefixes]
    desired=[[3. if j==t else 0. for j in range(7)] for t in targets]
    Wout=matmul(matmul(transpose(H),inv(matmul(H,transpose(H)))),desired)
    cache=None;pending=[1,2];all_ids=pending[:];out=[];turns=[]
    for _ in range(6):
        rows,cache=run_tokens(pending,cache);h=rows[-1]['hidden'];logits=matmul([h],Wout)[0];p=softmax(logits);t=max(range(7),key=lambda j:logits[j])
        turns.append({'processed':all_ids[:],'new_input':pending[:],'cache_tokens':len(cache['k']),'rows':rows,'logits':logits,'probabilities':p,'selected':t,'cache':cache})
        if t==6:break
        out.append(t);all_ids.append(t);pending=[t]
    return {'architecture':'1 block / 1 head / width 4 / no position encoding or normalization; output head fitted to 3 prefixes','embedding':E,'Wq':WQ,'Wk':WK,'Wv':WV,'Wff':WF,'Wout':Wout,'targets':targets,'turns':turns,'output':out,'eos':turns[-1]['selected']==6}

def attention_example():
    x=[[1,1],[1,-1]];wq=[[.5,.5],[-.5,.5]];wk=[[.5,.5],[.5,-.5]];wv=[[5,10],[5,-10]]
    q=matmul(x,wq);k=matmul(x,wk);v=matmul(x,wv)
    raw=[sum(a*b for a,b in zip(q[1],kk)) for kk in k];scaled=[r/math.sqrt(2) for r in raw];p=softmax(scaled);y=matmul([p],v)[0]
    return {'x':x,'wq':wq,'wk':wk,'wv':wv,'q':q,'k':k,'v':v,'raw':raw,'scaled':scaled,'p':p,'y':y}

def online_softmax(scores, values):
    """Online normalized weighted sum with rescaling when maximum changes."""
    m=-math.inf;l=0.;acc=[0.]*len(values[0]);steps=[]
    for s,v in zip(scores,values):
        new=max(m,s);a=math.exp(m-new) if m!=-math.inf else 0.;b=math.exp(s-new)
        l=a*l+b;acc=[a*x+b*y for x,y in zip(acc,v)];m=new
        steps.append({'max':m,'sum':l,'weighted_sum':acc[:],'out':[x/l for x in acc]})
    return steps

def sample(p,u):
    if not 0<=u<1:raise ValueError('u in [0,1)')
    acc=0
    for i,x in enumerate(p):
        acc+=x
        if u<acc:return i
    return len(p)-1

def gradient_demo(w=1.,eta=.2,x=2.,target=4.):
    prediction=w*x;loss=.5*(prediction-target)**2;g=(prediction-target)*x;nw=w-eta*g
    return {'w':w,'x':x,'target':target,'prediction':prediction,'loss':loss,'gradient':g,'eta':eta,'next_w':nw,'next_prediction':nw*x,'next_loss':.5*(nw*x-target)**2}

def rrf(rankings,k=60):
    out={}
    for ranking in rankings:
        for i,d in enumerate(ranking,1):out[d]=out.get(d,0.)+1/(k+i)
    return sorted(out.items(),key=lambda x:(-x[1],x[0]))

def mask(past,new):return [[int(j<=past+i) for j in range(past+new)] for i in range(new)]

def checks():
    a=attention_example();g=generation();ps=softmax([2,1,0]);gr=gradient_demo()
    return {'softmax':{'scores':[2,1,0],'shifted':[0,-1,-2],'exp':[1.,math.exp(-1),math.exp(-2)],'p':ps,'u':.7,'choice':sample(ps,.7)},'attention':a,'generation':g,'gradient':gr,'online':online_softmax([2,1,0],[[10,0],[0,20],[5,5]]),'rrf':rrf([['A','B','C'],['B','C','A']]),'mask':mask(3,2)}
if __name__=='__main__':
    import json
    print(json.dumps(checks(),ensure_ascii=False,indent=2))
