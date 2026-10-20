"""Offline numerical witnesses for the worked examples. Python >= 3.10, standard library only.
All inputs are small, constructed teaching data, not real model weights or benchmarks.
"""
from __future__ import annotations
import math, json, itertools, codecs, ast, hashlib, tempfile, os, sqlite3, unittest
from pathlib import Path

def softmax(xs):
    if not xs or not any(math.isfinite(x) for x in xs): raise ValueError('no finite logit')
    if any(math.isnan(x) or x==math.inf for x in xs): raise ValueError('invalid logit')
    m=max(xs); es=[math.exp(x-m) for x in xs]; s=sum(es)
    return [x/s for x in es]

def dot(a,b):
    if len(a)!=len(b): raise ValueError('shape mismatch')
    return sum(x*y for x,y in zip(a,b))
def matrix_shape(a):
    if not isinstance(a, (list, tuple)) or not a or not isinstance(a[0], (list, tuple)) or not a[0]:
        raise ValueError('expected a nonempty rectangular matrix')
    cols=len(a[0])
    if any(not isinstance(row,(list,tuple)) or len(row)!=cols for row in a):
        raise ValueError('ragged matrix')
    return len(a),cols

def tr(a):
    matrix_shape(a)
    return [list(x) for x in zip(*a)]
def mm(a,b):
    _,inner=matrix_shape(a); rows,_=matrix_shape(b)
    if inner!=rows: raise ValueError('shape mismatch')
    return [[dot(x,y) for y in tr(b)] for x in a]
def add(a,b):
    if matrix_shape(a)!=matrix_shape(b):raise ValueError('shape mismatch')
    return [[x+y for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def ln(x,eps=1e-5):
    if not x or eps<=0:raise ValueError('empty vector or nonpositive epsilon')
    m=sum(x)/len(x); v=sum((a-m)**2 for a in x)/len(x)
    return [(a-m)/math.sqrt(v+eps) for a in x]
def attn(q,k,v,offset=0,causal=True):
    nq,dq=matrix_shape(q);nk,dk=matrix_shape(k);nv,_=matrix_shape(v)
    if dq!=dk or nk!=nv or offset<0:raise ValueError('incompatible attention shapes or offset')
    d=len(q[0]); s=[[dot(a,b)/math.sqrt(d) if not causal or j<=offset+i else -math.inf for j,b in enumerate(k)] for i,a in enumerate(q)]
    p=[softmax(row) for row in s]
    return {'scores':s,'weights':p,'output':mm(p,v)}
def finite(x):
    if isinstance(x,float) and not math.isfinite(x): return '-inf' if x<0 else str(x)
    if isinstance(x,list): return [finite(v) for v in x]
    if isinstance(x,dict): return {k:finite(v) for k,v in x.items()}
    return x

def transformer():
    x=[[1.,0.],[0.,2.]]; u=[ln(row) for row in x]; a=attn(u,u,u)
    r=add(x,a['output']); n=[ln(row) for row in r]; f=[[.5*max(0,z) for z in row] for row in n]; y=add(r,f)
    last_norm=ln(y[-1]); logits=mm([last_norm],[[1.,0.,-1.],[0.,1.,.5]])[0]
    return {'X':x,'norm1':u,'attention':a,'residual1':r,'norm2':n,'ffn':f,'Y':y,'final_norm':last_norm,'logits':logits,'probabilities':softmax(logits)}

def grad_demo():
    q=[[.4,-.2]];k=[[1.,.5],[-.5,1.]];v=[[2.,-1.],[.5,3.]];g=[[.7,-.3]]
    a=attn(q,k,v,causal=False);p=a['weights']; dp=mm(g,tr(v));ds=[[pj*(gj-dot(pr,gr)) for pj,gj in zip(pr,gr)] for pr,gr in zip(p,dp)]
    dq=[[z/math.sqrt(2) for z in row] for row in mm(ds,k)]
    dk=[[z/math.sqrt(2) for z in row] for row in mm(tr(ds),q)];dv=mm(tr(p),g)
    def loss(): return dot(attn(q,k,v,causal=False)['output'][0],g[0])
    err=0.; checked=0
    for arr,deriv in [(q,dq),(k,dk),(v,dv)]:
        for i,row in enumerate(arr):
            for j,old in enumerate(row):
                h=1e-6; arr[i][j]=old+h; hi=loss();arr[i][j]=old-h;lo=loss();arr[i][j]=old
                err=max(err,abs((hi-lo)/(2*h)-deriv[i][j]));checked+=1
    return {'Q':q,'K':k,'V':v,'upstream':g,'P':p,'O':a['output'],'dP':dp,'dS':ds,'dQ':dq,'dK':dk,'dV':dv,'max_error':err,'coordinates_checked':checked}

def online_softmax(scores,values):
    m=-math.inf;l=0.;u=0.;trace=[]
    for s,v in zip(scores,values):
        new=max(m,s);scale=math.exp(m-new);e=math.exp(s-new);l=scale*l+e;u=scale*u+e*v;m=new
        trace.append({'score':s,'value':v,'max':m,'old_scale':scale,'sum':l,'weighted_sum':u,'output':u/l})
    return trace

def bm25(docs,term,k1=1.2,b=.75):
    n=len(docs); df=sum(term in d for d in docs);avg=sum(map(len,docs))/n;idf=math.log(1+(n-df+.5)/(df+.5)); rows=[]
    for i,d in enumerate(docs):
        f=d.count(term);den=f+k1*(1-b+b*len(d)/avg);part=f*(k1+1)/den
        rows.append({'doc':chr(65+i),'length':len(d),'frequency':f,'denominator':den,'tf_factor':part,'score':idf*part})
    return {'N':n,'df':df,'avgdl':avg,'idf':idf,'rows':rows}
def rrf(lists,c=60):
    scores={}
    for ranking in lists:
        unique=list(dict.fromkeys(ranking))
        for rank,x in enumerate(unique,1):scores[x]=scores.get(x,0)+1/(c+rank)
    return sorted(scores.items(),key=lambda kv:(-kv[1],kv[0]))

def spec_demo():
    p=[.6,.3,.1];q=[.2,.5,.3];accept=[min(1,pi/qi) for pi,qi in zip(p,q)]
    accepted=[qi*ai for qi,ai in zip(q,accept)];r=sum(qi*(1-ai) for qi,ai in zip(q,accept));res=[max(0,pi-qi) for pi,qi in zip(p,q)];s=sum(res);res=[v/s for v in res]
    return {'target':p,'draft':q,'accept_prob':accept,'accepted_mass':accepted,'rejection_mass':r,'residual_distribution':res,'final_mass':[a+r*b for a,b in zip(accepted,res)]}

def adamw_demo():
    w=1.;g=.2;b1=.9;b2=.999;lr=.1;wd=.01;eps=1e-8
    m=(1-b1)*g;v=(1-b2)*g*g;mh=m/(1-b1);vh=v/(1-b2)
    decay=w*(1-lr*wd);new=decay-lr*mh/(math.sqrt(vh)+eps)
    return {'w':w,'gradient':g,'m':m,'v':v,'m_hat':mh,'v_hat':vh,'after_decay':decay,'new_w':new}

def sse_trace(chunks):
    decoder=codecs.getincrementaldecoder('utf-8')();buf='';events=[]
    for chunk in chunks:
        buf+=decoder.decode(chunk)
        while '\n\n' in buf:
            raw,buf=buf.split('\n\n',1);data=[]
            for line in raw.split('\n'):
                if line.startswith('data:'):
                    text=line[5:]; data.append(text[1:] if text.startswith(' ') else text)
            if data:events.append('\n'.join(data))
    buf+=decoder.decode(b'',final=True)
    return events,buf

def memory_select(items,project,at,known_at):
    known=[r for r in items if r['project']==project and r['recorded']<=known_at]
    # Each item here is a full assertion for a finite validity interval. Later corrections win only in this toy policy.
    valid=[r for r in known if r['from']<=at<r['to']]
    return max(valid,key=lambda r:r['recorded'],default=None)

def precision_recall(ranking,relevant):
    got=set(ranking);rel=set(relevant);tp=len(got&rel)
    return {'precision':tp/len(got) if got else 0,'recall':tp/len(rel) if rel else None}

def compute():
    E=[[0.,0.,0.,0.],[.2,-.1,.7,.4],[-.3,.8,.1,.5],[.6,.2,-.4,.9],[.1,-.5,.9,.3],[-.2,.4,.5,-.6]]
    ids=[[1,2,3],[4,2,0]];embedded=[[E[j] for j in row] for row in ids]
    a=attn([[1.,0.],[0.,1.],[1.,1.]],[[1.,0.],[0.,1.],[1.,1.]],[[1.,2.],[3.,4.],[4.,6.]])
    bm=bm25([['排除','路径'],['排除','排除','路径','缓存'],['日志','输出']],'排除')
    lp=math.log(2.);dpo=-math.log(1/(1+math.exp(-lp)))
    wp=.6;wnew=wp-.1*(wp-1)
    brier=((.8-1)**2+(.8-1)**2+(.8-0)**2+(.8-0)**2)/4
    return {
      'embedding':{'table':E,'ids':ids,'output':embedded},
      'shapes':{'ids_elements':2*128,'ids_bytes_int64':2*128*8,'embedding_elements':2*128*4096,'embedding_bytes_fp16':2*128*4096*2},
      'attention':a,'decoder':transformer(),'gradients':grad_demo(),
      'softmax':{'logits':[2,1,0],'p':softmax([2,1,0]),'shifted_p':softmax([1002,1001,1000]),'temperature2':softmax([1,.5,0]),'temperature05':softmax([4,2,0])},
      'online':online_softmax([1,3],[2,10]),
      'adamw':adamw_demo(),
      'loss':{'target_ps':[.8,.5,.25],'losses':[-math.log(p) for p in [.8,.5,.25]],'mean':sum(-math.log(p) for p in [.8,.5,.25])/3,'logits':[0,0],'gradient':[-.5,.5],'updated_logits':[.05,-.05],'new_loss':-math.log(softmax([.05,-.05])[0])},
      'dpo':{'pi_preferred':.6,'pi_rejected':.2,'ref_preferred':.3,'ref_rejected':.2,'beta':1.,'margin':lp,'loss':dpo,'baseline_loss':math.log(2),'kl':sum(p*math.log(p/q) for p,q in zip([.8,.2],[.5,.5]))},
      'speculative':spec_demo(),
      'cache':{'tiny_bytes':2*2*1*3*1*2*4,'GiB':2*32*1*32768*8*128*2/2**30,'per_token_KiB':2*32*1*8*128*2/1024},
      'bm25':bm,'rrf':rrf([['A','B','C'],['B','C','D']]),
      'metrics':{'precision_recall':precision_recall(['A','X','Y'],['A','B']),'pass1':.8,'pass_at3':1-.2**3,'pass_all3':.8**3,'finite_pass3':1-math.comb(4,3)/math.comb(10,3),'brier':brier,'mcnemar_p':2*sum(math.comb(8,k) for k in range(3))/2**8},
    }

class WitnessTests(unittest.TestCase):
    def test_embedding_semantics(self):
        d=compute()['embedding'];self.assertEqual(d['output'][0][1],d['table'][2]);self.assertEqual(d['output'][1][1],d['table'][2]);self.assertEqual(len(d['output'][1]),3);self.assertEqual(d['output'][1][-1],[0.]*4)
    def test_softmax_stability(self):
        for a,b in zip(softmax([2,1,0]),softmax([1002,1001,1000])):self.assertAlmostEqual(a,b)
        self.assertAlmostEqual(sum(softmax([-1000,-1001])),1)
    def test_softmax_invalid(self):
        for xs in [[],[-math.inf,-math.inf],[math.nan,0],[math.inf,0]]:
            with self.assertRaises(ValueError):softmax(xs)
    def test_future_mask(self):
        a=compute()['attention'];self.assertEqual(a['weights'][0],[1,0,0]);self.assertEqual(a['weights'][1][2],0)
    def test_chunk_mask(self):
        self.assertEqual([[j<=3+i for j in range(5)] for i in range(2)],[[True,True,True,True,False],[True]*5])
    def test_cache_equivalence(self):
        x=[[1.,0.],[0.,1.],[1.,1.]];v=[[1.,2.],[3.,4.],[4.,6.]]
        full=attn(x,x,v)['output'];incremental=[attn([x[i]],x[:i+1],v[:i+1],i)['output'][0] for i in range(3)]
        self.assertEqual(full,incremental)
    def test_cache_wrong_offset_detected(self):
        x=[[1.,0.],[0.,1.],[1.,1.]];v=[[1.,2.],[3.,4.],[4.,6.]]
        self.assertNotEqual(attn([x[-1]],x,v,0)['output'],attn([x[-1]],x,v,2)['output'])
    def test_gradient_finite_difference(self):self.assertLess(grad_demo()['max_error'],1e-8)
    def test_gradient_shift_sum(self):self.assertAlmostEqual(sum(grad_demo()['dS'][0]),0)
    def test_online_equals_full(self):
        o=online_softmax([1,3],[2,10])[-1]['output'];self.assertAlmostEqual(o,dot(softmax([1,3]),[2,10]))
    def test_speculative_distribution(self):
        s=spec_demo()
        for a,b in zip(s['target'],s['final_mass']):self.assertAlmostEqual(a,b)
    def test_adamw(self):self.assertAlmostEqual(adamw_demo()['new_w'],.899000005,places=9)
    def test_dpo_margin(self):self.assertAlmostEqual(compute()['dpo']['loss'],math.log(1.5))
    def test_ce_update(self):self.assertLess(compute()['loss']['new_loss'],math.log(2))
    def test_rope_preserves_norm(self):
        x=[2.,1.];t=.7;c=math.cos(t);s=math.sin(t);y=[c*x[0]-s*x[1],s*x[0]+c*x[1]];self.assertAlmostEqual(dot(x,x),dot(y,y))
    def test_bm25_ranking(self):
        b=compute()['bm25'];self.assertGreater(b['rows'][1]['score'],b['rows'][0]['score']);self.assertEqual(b['rows'][2]['score'],0)
    def test_rrf(self):self.assertEqual([a for a,b in compute()['rrf']],['B','C','A','D'])
    def test_rrf_duplicate(self):self.assertEqual(rrf([['A','A','B']]),rrf([['A','B']]))
    def test_sse_all_byte_boundaries(self):
        wire='data: {"path":"学习.py"}\n\n'.encode('utf-8')
        for cut in range(1,len(wire)):
            e,buf=sse_trace([wire[:cut],wire[cut:]]);self.assertEqual(json.loads(e[0]),{'path':'学习.py'});self.assertEqual(buf,'')
    def test_sse_incomplete_not_emitted(self):self.assertEqual(sse_trace([b'data: {"x":1}'])[0],[])
    def test_tool_result_pairing(self):
        calls={'a':'read(config)','b':'read(test)'};responses=[('b','TEST'),('a','CONFIG')]
        paired={calls[k]:v for k,v in responses};self.assertEqual(paired['read(config)'],'CONFIG')
    def test_memory_bitemporal(self):
        items=[dict(project='A',recorded=1,**{'from':1,'to':99},value=3),dict(project='A',recorded=12,**{'from':10,'to':99},value=5)]
        self.assertEqual(memory_select(items,'A',11,11)['value'],3);self.assertEqual(memory_select(items,'A',11,12)['value'],5)
    def test_acl_before_model(self):
        docs=[('private',.99,{'admin'}),('public',.8,{'user','admin'})];visible=[x[0] for x in docs if 'user' in x[2]];self.assertEqual(visible,['public'])
    def test_compare_and_swap(self):
        current={'version':8,'body':'B'};expected=7
        if current['version']==expected:current.update(version=9,body='C')
        self.assertEqual(current,{'version':8,'body':'B'})
    def test_atomic_replace_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.txt';q=Path(d)/'tmp.txt';p.write_text('old');q.write_text('new');os.replace(q,p);self.assertEqual(p.read_text(),'new')
    def test_sqlite_local_transaction(self):
        c=sqlite3.connect(':memory:');c.execute('create table receipts(id text primary key, result text)');c.execute('insert into receipts values(?,?)',('op1','done'));c.commit()
        with self.assertRaises(sqlite3.IntegrityError):c.execute('insert into receipts values(?,?)',('op1','again'))
        self.assertEqual(c.execute('select count(*) from receipts').fetchone()[0],1);c.close()
    def test_precision_recall(self):self.assertEqual(precision_recall(['A','X','Y'],['A','B']),{'precision':1/3,'recall':.5})
    def test_paired_exact(self):self.assertEqual(compute()['metrics']['mcnemar_p'],.2890625)
    def test_lora_rank1(self):
        self.assertEqual(mm([[1],[2]],[[3,4]]),[[3,4],[6,8]])
    def test_quantization(self):self.assertEqual([round(x/.1) for x in [-.24,.03,.26]],[-2,0,3])
    def test_pool_mask(self):
        vectors=[[2.,0.],[0.,2.],[0.,0.]];valid=[1,1,0];pooled=[sum(r[j]*m for r,m in zip(vectors,valid))/sum(valid) for j in range(2)];self.assertEqual(pooled,[1,1])
    def test_dag_critical_path(self):
        durations={'A':2,'B':3,'C':5,'D':1};finish={'A':2,'B':5,'C':7,'D':8};self.assertEqual(finish['D'],2+max(3,5)+1)
    def test_paginated_position(self):
        blocks=[7,2,19];self.assertEqual((blocks[5//4],5%4),(2,1))
    def test_source_version_gate(self):
        verified={'commit':'r7','exit':0};current='r8';self.assertFalse(verified['commit']==current and verified['exit']==0)

if __name__=='__main__':
    import sys
    if '--test' in sys.argv:unittest.main(argv=[sys.argv[0]],verbosity=2)
    else: print(json.dumps(finite(compute()),ensure_ascii=False,indent=2,allow_nan=False))
