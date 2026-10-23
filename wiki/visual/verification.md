---
title: "图解的数值与程序"
description: "AI系统工程：本地教学正文与可追溯图表"
---

图解 · 运行过程 · 工程取舍


<span id="page-title"></span>


# 图解的数值与程序


<span id="checks-scope"></span>


**本包验证记录**

随书原始图解程序提供97项检查：45项数值、状态与反例检查，以及52项数据结构检查。这些检查验证计算与记录结构，不代表97个图形或97项真实模型实验。教学数据保留52组、263个步骤；目前45组采用可控图形，7组采用更适合逐项核对的原生说明表。

图形、步骤说明和数值记录按同一示例关联。可控图形默认暂停；静态图不自动播放。手机端为关键数值图提供纵向排布，其他宽图在独立区域滚动，避免为了塞入屏幕而把数值缩得过小。

浏览器检查使用本地内容装载；环境限制直接file/localhost导航，因此不将该导航方式计作已测。教材本身没有外部脚本、字体或图片依赖。实际结果与验证边界见 [完整检查记录](../../visual/labs/validation_report.json)。

本页程序只用Python标准库。数值例是真实计算；教学流程不是商业模型实测。图解生成所用源数据与播放数据共用一份定义。

```
cd visual/labs
python3 test_visual.py
```

逐轮生成模型为明确构造的小模型：单层、单头、宽度4；没有位置旋转、归一化和dropout。通过三个指定前缀拟合输出头，只用于展示缓存与生成循环，不代表自然语言理解能力。


<span id="code-numerics"></span>


## numerics.py

```
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
```


<span id="code-test_visual"></span>


## test\_visual.py

```
"""Run with Python 3.10+. Distinguishes numerical checks from content contracts.
All examples are deterministic teaching cases, not model benchmarks.
"""
import unittest,math,json,codecs,xml.etree.ElementTree as ET
from pathlib import Path
from numerics import *

class NumericalChecks(unittest.TestCase):
 def assertVector(self,a,b,tol=1e-10):
  self.assertEqual(len(a),len(b))
  for x,y in zip(a,b):self.assertAlmostEqual(x,y,delta=tol)
 def test_softmax_values(self):self.assertVector(softmax([2,1,0]),[.6652409557748218,.24472847105479764,.09003057317038046])
 def test_softmax_shift(self):self.assertVector(softmax([2,1,0]),softmax([1002,1001,1000]))
 def test_softmax_sampling(self):self.assertEqual(sample(softmax([2,1,0]),.7),1)
 def test_softmax_sum_and_positive(self):
  for x in [[0,0],[-9,-4,0],[1000,0,-1000]]:
   p=softmax(x);self.assertAlmostEqual(sum(p),1);self.assertTrue(all(v>=0 for v in p))
 def test_softmax_invalid(self):
  for x in [[],[float('nan')],[float('inf')]]:
   with self.assertRaises(ValueError):softmax(x)
 def test_sampling_range(self):
  for u in [-.1,1]:
   with self.assertRaises(ValueError):sample([.5,.5],u)
 def test_embedding_lookup(self):self.assertEqual([E[t] for t in [1,2,3]],[[.2,-.1,.7,.4],[-.3,.8,.1,.5],[.6,.2,-.4,.9]])
 def test_shape_count(self):self.assertEqual(len([n for ids in [[1,2,3],[4,2,0]] for i in ids for n in E[i]]),24)
 def test_matrix_product(self):self.assertEqual(matmul([[1,2,3],[4,5,6]],[[1,0],[0,1],[1,1]]),[[4,5],[10,11]])
 def test_matrix_shape_mismatch(self):
  with self.assertRaises(ValueError):matmul([[1,2]],[[1,2]])
 def test_qkv_projection(self):
  d=attention_example();self.assertEqual(d['q'],[[0,1],[1,0]]);self.assertEqual(d['k'],[[1,0],[0,1]]);self.assertEqual(d['v'],[[10,0],[0,20]])
 def test_attention_output(self):self.assertVector(attention_example()['y'],[6.697615493266569,6.604769013466862])
 def test_value_change_keeps_weights(self):
  d=attention_example();newv=matmul(d['x'],[[6,10],[5,-10]]);self.assertVector(d['p'],softmax(d['scaled']));self.assertNotEqual(matmul([d['p']],newv)[0],d['y'])
 def test_mask_past_offset(self):self.assertEqual(mask(3,2),[[1,1,1,1,0],[1,1,1,1,1]])
 def test_bad_mask_counterexample(self):self.assertNotEqual(mask(0,2),mask(3,2))
 def test_exclusion_vs_zero_score(self):
  two=softmax([2,1]);three=softmax([2,1,0]);self.assertGreater(three[2],0);self.assertNotAlmostEqual(two[0],three[0])
 def test_rope_norm(self):
  for a in [0,math.pi/6,math.pi/3,math.pi/2]:self.assertAlmostEqual(math.cos(a)**2+math.sin(a)**2,1)
 def test_rope_relative(self):
  self.assertAlmostEqual(math.cos(math.pi/3),math.cos(math.pi/6)*math.cos(math.pi/2)+math.sin(math.pi/6)*math.sin(math.pi/2))
 def test_generation_sequence(self):
  g=generation();self.assertEqual([t['selected'] for t in g['turns']],[3,5,6]);self.assertEqual(g['output'],[3,5]);self.assertTrue(g['eos'])
 def test_generation_cache_lengths(self):self.assertEqual([t['cache_tokens'] for t in generation()['turns']],[2,3,4])
 def test_generation_has_no_eos_forward(self):
  g=generation();self.assertEqual(g['turns'][-1]['new_input'],[5]);self.assertNotIn(6,[r['id'] for t in g['turns'] for r in t['rows']])
 def test_generation_cached_full_equality(self):
  g=generation()
  for t in g['turns']:
   rows,c=run_tokens(t['processed']);self.assertVector(rows[-1]['hidden'],t['rows'][-1]['hidden']);self.assertVector(matmul([rows[-1]['hidden']],g['Wout'])[0],t['logits'])
 def test_generation_probability_from_logits(self):
  for t in generation()['turns']:self.assertVector(softmax(t['logits']),t['probabilities']);self.assertAlmostEqual(t['probabilities'][t['selected']],.7699874831916322)
 def test_changed_prefix_invalidates(self):
  old,c=run_tokens([1,2]);wrong,_=run_tokens([3],c);correct,_=run_tokens([4,2,3]);self.assertTrue(any(abs(a-b)>1e-7 for a,b in zip(wrong[-1]['hidden'],correct[-1]['hidden'])))
 def test_gradient_finite_difference(self):
  h=1e-6;f=lambda w:.5*(w*2-4)**2;self.assertAlmostEqual((f(1+h)-f(1-h))/(2*h),gradient_demo()['gradient'],places=8)
 def test_gradient_update(self):
  d=gradient_demo();self.assertAlmostEqual(d['next_w'],1.8);self.assertAlmostEqual(d['next_loss'],.08)
 def test_learning_rate_overshoot(self):self.assertAlmostEqual(gradient_demo(eta=.6)['next_loss'],3.92)
 def test_pad_loss_denominator(self):self.assertAlmostEqual((.8+.4)/2,.6);self.assertNotAlmostEqual((.8+.4)/3,.6)
 def test_rrf_order(self):self.assertEqual([k for k,v in rrf([['A','B','C'],['B','C','A']])],['B','A','C'])
 def test_rrf_score(self):self.assertAlmostEqual(dict(rrf([['A','B','C'],['B','C','A']]))['B'],1/62+1/61)
 def test_online_softmax_max_rescale(self):
  scores=[0,2,1];v=[[5,5],[10,0],[0,20]];o=online_softmax(scores,v)[-1]['out'];ref=matmul([softmax(scores)],v)[0];self.assertVector(o,ref)
 def test_wrong_online_rescale_detected(self):
  # Incorrectly keep the old accumulator unchanged when max jumps from 0 to 2.
  m=-math.inf;l=0.;acc=[0.,0.]
  for s,v in zip([0,2,1],[[5,5],[10,0],[0,20]]):
   m=max(m,s);w=math.exp(s-m);l+=w;acc=[a+w*b for a,b in zip(acc,v)]
  wrong=[a/l for a in acc];self.assertNotEqual(wrong,online_softmax([0,2,1],[[5,5],[10,0],[0,20]])[-1]['out'])
 def test_lora(self):
  a=[[.1],[.2],[.3],[.4]];b=[[1,-1,.5,0]];d=matmul(a,b);self.assertVector([x+y for x,y in zip(I[0],d[0])],[1.1,-.1,.05,0]);self.assertEqual(sum(map(len,a))+sum(map(len,b)),8)
 def test_quantization_round_clip(self):
  xs=[.26,-.14,.36,.91];q=[max(-8,min(7,round(x/.1))) for x in xs];self.assertEqual(q,[3,-1,4,7]);self.assertAlmostEqual(q[-1]*.1-xs[-1],-.21)
 def test_gqa_storage(self):self.assertEqual([2*2*1*4*h*2*2 for h in [4,2,1]],[256,128,64])
 def test_speculative_corrected_distribution(self):
  p=[.6,.3,.1];q=[.4,.4,.2];accept=[min(1,x/y) for x,y in zip(p,q)];mass=[a*b for a,b in zip(q,accept)];r=[max(0,a-b) for a,b in zip(p,q)];z=sum(r);out=[a+(1-sum(mass))*b/z for a,b in zip(mass,r)];self.assertVector(out,p);self.assertVector(mass,[.4,.3,.1])
 def test_moe_weighted_top2(self):self.assertAlmostEqual((.5*4+.3*5)/(.5+.3),4.375)
 def test_budget(self):self.assertEqual(sum([20,10,15,20,20]),85);self.assertEqual(65+40+20,125);self.assertEqual(65+10+20,95)
 def test_continuous_batching(self):
  pending=[2,4,2];slots=[];ticks=0
  while pending or slots:
   while pending and len(slots)<2:slots.append(pending.pop(0))
   ticks+=1;slots=[x-1 for x in slots if x-1>0]
  self.assertEqual(ticks,4);self.assertEqual(max(2,4)+2,6)
 def test_parallel_critical_path(self):self.assertEqual(2+3+max(3,8)+2+1,16);self.assertEqual(2+3+max(1,8)+2+1,16)
 def test_multiagent_overhead(self):self.assertEqual(6+8+3,17);self.assertEqual(max(6,8)+3+2,13);self.assertEqual(max(6,8)+3+8,19)
 def test_pair_counts(self):
  both,new,old,none=10,4,2,4;n=both+new+old+none;self.assertEqual(n,20);self.assertAlmostEqual((both+new)/n-(both+old)/n,.1)
 def test_precision_recall(self):self.assertEqual(6/(6+2),.75);self.assertEqual(6/(6+4),.6)
 def test_cascade_cost(self):self.assertEqual(20+6*5,50);self.assertEqual(14+5,19);self.assertLess(50/19,100/19)
 def test_utf8_every_split(self):
  raw='爱'.encode('utf8')
  for cut in range(len(raw)+1):
   d=codecs.getincrementaldecoder('utf8')();self.assertEqual(d.decode(raw[:cut])+d.decode(raw[cut:],final=True),'爱')

class LessonContracts(unittest.TestCase):pass

def contract(mid):
 def run(self):
  from catalog import C
  m=C[mid];self.assertGreaterEqual(len(m['frames']),3)
  for k in ['question','intuition','scenario','why','how','risk','verify']:self.assertTrue(m[k],k)
  for f in m['frames']:
   root=ET.fromstring(f['svg']);self.assertIn('viewBox',root.attrib);self.assertTrue(f['title']);self.assertTrue(f['explain']);self.assertNotIn('<script',f['svg']);self.assertNotIn('<image',f['svg'])
  self.assertTrue(all(k in C for k in m['links']))
 return run
try:
 from catalog import C
 for mid in C:setattr(LessonContracts,'test_lesson_'+mid,contract(mid))
except ImportError:pass

if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 report={'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'scope':'数值与反例检查，以及52个图解内容结构检查；不属于商业模型benchmark'}
 Path(__file__).with_name('test_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 raise SystemExit(0 if result.wasSuccessful() else 1)
```


<span id="numeric-results"></span>


## 完整教学数值记录

```
{
  "softmax": {
    "scores": [
      2,
      1,
      0
    ],
    "shifted": [
      0,
      -1,
      -2
    ],
    "exp": [
      1.0,
      0.36787944117144233,
      0.1353352832366127
    ],
    "p": [
      0.6652409557748218,
      0.24472847105479764,
      0.09003057317038046
    ],
    "u": 0.7,
    "choice": 1
  },
  "attention": {
    "x": [
      [
        1,
        1
      ],
      [
        1,
        -1
      ]
    ],
    "wq": [
      [
        0.5,
        0.5
      ],
      [
        -0.5,
        0.5
      ]
    ],
    "wk": [
      [
        0.5,
        0.5
      ],
      [
        0.5,
        -0.5
      ]
    ],
    "wv": [
      [
        5,
        10
      ],
      [
        5,
        -10
      ]
    ],
    "q": [
      [
        0.0,
        1.0
      ],
      [
        1.0,
        0.0
      ]
    ],
    "k": [
      [
        1.0,
        0.0
      ],
      [
        0.0,
        1.0
      ]
    ],
    "v": [
      [
        10,
        0
      ],
      [
        0,
        20
      ]
    ],
    "raw": [
      1.0,
      0.0
    ],
    "scaled": [
      0.7071067811865475,
      0.0
    ],
    "p": [
      0.6697615493266569,
      0.3302384506733431
    ],
    "y": [
      6.697615493266569,
      6.604769013466862
    ]
  },
  "generation": {
    "architecture": "1 block / 1 head / width 4 / no position encoding or normalization; output head fitted to 3 prefixes",
    "embedding": [
      [
        0.0,
        0.0,
        0.0,
        0.0
      ],
      [
        0.2,
        -0.1,
        0.7,
        0.4
      ],
      [
        -0.3,
        0.8,
        0.1,
        0.5
      ],
      [
        0.6,
        0.2,
        -0.4,
        0.9
      ],
      [
        0.1,
        -0.5,
        0.9,
        0.3
      ],
      [
        -0.2,
        0.4,
        0.5,
        -0.6
      ],
      [
        0.15,
        -0.2,
        0.05,
        0.1
      ]
    ],
    "Wq": [
      [
        1,
        0.1,
        0,
        0
      ],
      [
        0,
        1,
        0.1,
        0
      ],
      [
        0,
        0,
        1,
        0.1
      ],
      [
        0.1,
        0,
        0,
        1
      ]
    ],
    "Wk": [
      [
        1.0,
        0.0,
        0.0,
        0.0
      ],
      [
        0.0,
        1.0,
        0.0,
        0.0
      ],
      [
        0.0,
        0.0,
        1.0,
        0.0
      ],
      [
        0.0,
        0.0,
        0.0,
        1.0
      ]
    ],
    "Wv": [
      [
        0.8,
        0,
        0.1,
        0
      ],
      [
        0,
        0.8,
        0,
        0.1
      ],
      [
        0.1,
        0,
        0.8,
        0
      ],
      [
        0,
        0.1,
        0,
        0.8
      ]
    ],
    "Wff": [
      [
        0.3,
        0,
        0.1,
        0
      ],
      [
        0,
        0.3,
        0,
        0.1
      ],
      [
        0.1,
        0,
        0.3,
        0
      ],
      [
        0,
        0.1,
        0,
        0.3
      ]
    ],
    "Wout": [
      [
        0.0,
        0.0,
        0.0,
        -3.1369512045789385,
        0.0,
        2.955672290012137,
        3.1080560358745872
      ],
      [
        0.0,
        0.0,
        0.0,
        0.6602494116706786,
        0.0,
        0.45983993695429126,
        1.4653385279247557
      ],
      [
        0.0,
        0.0,
        0.0,
        -0.5199910894187953,
        0.0,
        0.4190172089893097,
        2.2799301281822117
      ],
      [
        0.0,
        0.0,
        0.0,
        1.3501098041819612,
        0.0,
        0.32657210654192936,
        -1.6587482723025757
      ]
    ],
    "targets": [
      3,
      5,
      6
    ],
    "turns": [
      {
        "processed": [
          1,
          2
        ],
        "new_input": [
          1,
          2
        ],
        "cache_tokens": 2,
        "rows": [
          {
            "id": 1,
            "x": [
              0.2,
              -0.1,
              0.7,
              0.4
            ],
            "q": [
              0.24000000000000002,
              -0.08,
              0.69,
              0.47000000000000003
            ],
            "k": [
              0.2,
              -0.1,
              0.7,
              0.4
            ],
            "v": [
              0.23000000000000004,
              -0.04000000000000001,
              0.58,
              0.31000000000000005
            ],
            "scores": [
              0.3635
            ],
            "attention": [
              1.0
            ],
            "mixed": [
              0.23000000000000004,
              -0.04000000000000001,
              0.58,
              0.31000000000000005
            ],
            "residual": [
              0.43000000000000005,
              -0.14,
              1.2799999999999998,
              0.7100000000000001
            ],
            "ff": [
              0.025148739741581584,
              0.002899187306722258,
              0.0402811120010977,
              0.019641408783879863
            ],
            "hidden": [
              0.45514873974158165,
              -0.13710081269327776,
              1.3202811120010975,
              0.72964140878388
            ]
          },
          {
            "id": 2,
            "x": [
              -0.3,
              0.8,
              0.1,
              0.5
            ],
            "q": [
              -0.25,
              0.77,
              0.18000000000000002,
              0.51
            ],
            "k": [
              -0.3,
              0.8,
              0.1,
              0.5
            ],
            "v": [
              -0.22999999999999998,
              0.6900000000000002,
              0.05000000000000002,
              0.48000000000000004
            ],
            "scores": [
              0.1015,
              0.48200000000000004
            ],
            "attention": [
              0.40600630880809374,
              0.5939936911919063
            ],
            "mixed": [
              -0.043237097948276834,
              0.3936153945700917,
              0.26518334366828966,
              0.4109789275026241
            ],
            "residual": [
              -0.34323709794827684,
              1.1936153945700918,
              0.36518334366828964,
              0.9109789275026241
            ],
            "ff": [
              -0.00663551495563727,
              0.042122679669324044,
              0.007508968384532306,
              0.03736470084721627
            ],
            "hidden": [
              -0.3498726129039141,
              1.235738074239416,
              0.37269231205282194,
              0.9483436283498403
            ]
          }
        ],
        "logits": [
          0.0,
          0.0,
          0.0,
          3.0000000000000027,
          0.0,
          -9.71445146547012e-16,
          -3.219646771412954e-15
        ],
        "probabilities": [
          0.03833541946806122,
          0.03833541946806122,
          0.03833541946806122,
          0.7699874831916329,
          0.03833541946806122,
          0.038335419468061176,
          0.03833541946806109
        ],
        "selected": 3,
        "cache": {
          "k": [
            [
              0.2,
              -0.1,
              0.7,
              0.4
            ],
            [
              -0.3,
              0.8,
              0.1,
              0.5
            ]
          ],
          "v": [
            [
              0.23000000000000004,
              -0.04000000000000001,
              0.58,
              0.31000000000000005
            ],
            [
              -0.22999999999999998,
              0.6900000000000002,
              0.05000000000000002,
              0.48000000000000004
            ]
          ]
        }
      },
      {
        "processed": [
          1,
          2,
          3
        ],
        "new_input": [
          3
        ],
        "cache_tokens": 3,
        "rows": [
          {
            "id": 3,
            "x": [
              0.6,
              0.2,
              -0.4,
              0.9
            ],
            "q": [
              0.69,
              0.26,
              -0.38,
              0.86
            ],
            "k": [
              0.6,
              0.2,
              -0.4,
              0.9
            ],
            "v": [
              0.43999999999999995,
              0.25000000000000006,
              -0.26000000000000006,
              0.7400000000000001
            ],
            "scores": [
              0.09500000000000003,
              0.1965,
              0.6960000000000001
            ],
            "attention": [
              0.25440296813676383,
              0.2815808164614805,
              0.46401621540175575
            ],
            "mixed": [
              0.1979162296620877,
              0.30011869848339,
              0.040988546337940496,
              0.5573957114212067
            ],
            "residual": [
              0.7979162296620876,
              0.5001186984833901,
              -0.35901145366205955,
              1.4573957114212068
            ],
            "ff": [
              0.020071141711280643,
              0.02874415829297143,
              -0.0027904566978148885,
              0.045201561862303646
            ],
            "hidden": [
              0.8179873713733683,
              0.5288628567763615,
              -0.36180191035987447,
              1.5025972732835104
            ]
          }
        ],
        "logits": [
          0.0,
          0.0,
          0.0,
          1.0547118733938987e-15,
          0.0,
          3.0,
          -2.6645352591003757e-15
        ],
        "probabilities": [
          0.038335419468061294,
          0.038335419468061294,
          0.038335419468061294,
          0.03833541946806132,
          0.038335419468061294,
          0.7699874831916323,
          0.03833541946806119
        ],
        "selected": 5,
        "cache": {
          "k": [
            [
              0.2,
              -0.1,
              0.7,
              0.4
            ],
            [
              -0.3,
              0.8,
              0.1,
              0.5
            ],
            [
              0.6,
              0.2,
              -0.4,
              0.9
            ]
          ],
          "v": [
            [
              0.23000000000000004,
              -0.04000000000000001,
              0.58,
              0.31000000000000005
            ],
            [
              -0.22999999999999998,
              0.6900000000000002,
              0.05000000000000002,
              0.48000000000000004
            ],
            [
              0.43999999999999995,
              0.25000000000000006,
              -0.26000000000000006,
              0.7400000000000001
            ]
          ]
        }
      },
      {
        "processed": [
          1,
          2,
          3,
          5
        ],
        "new_input": [
          5
        ],
        "cache_tokens": 4,
        "rows": [
          {
            "id": 5,
            "x": [
              -0.2,
              0.4,
              0.5,
              -0.6
            ],
            "q": [
              -0.26,
              0.38,
              0.54,
              -0.5499999999999999
            ],
            "k": [
              -0.2,
              0.4,
              0.5,
              -0.6
            ],
            "v": [
              -0.11000000000000003,
              0.26000000000000006,
              0.38,
              -0.43999999999999995
            ],
            "scores": [
              0.03400000000000001,
              0.08050000000000004,
              -0.39549999999999996,
              0.402
            ],
            "attention": [
              0.24135499307623112,
              0.252843027120259,
              0.15708213949072153,
              0.3487198403127883
            ],
            "mixed": [
              0.028114711111384347,
              0.2947451823439349,
              0.24430023039149895,
              0.1589887543568631
            ],
            "residual": [
              -0.17188528888861565,
              0.6947451823439349,
              0.744300230391499,
              -0.4410112456431369
            ],
            "ff": [
              0.00228604528302138,
              0.016285922797339265,
              0.020323203676215595,
              -0.00627463142166235
            ],
            "hidden": [
              -0.16959924360559428,
              0.7110311051412742,
              0.7646234340677145,
              -0.4472858770647992
            ]
          }
        ],
        "logits": [
          0.0,
          0.0,
          0.0,
          3.3306690738754696e-16,
          0.0,
          -2.498001805406602e-16,
          3.0000000000000004
        ],
        "probabilities": [
          0.03833541946806127,
          0.03833541946806127,
          0.03833541946806127,
          0.038335419468061294,
          0.03833541946806127,
          0.03833541946806125,
          0.7699874831916323
        ],
        "selected": 6,
        "cache": {
          "k": [
            [
              0.2,
              -0.1,
              0.7,
              0.4
            ],
            [
              -0.3,
              0.8,
              0.1,
              0.5
            ],
            [
              0.6,
              0.2,
              -0.4,
              0.9
            ],
            [
              -0.2,
              0.4,
              0.5,
              -0.6
            ]
          ],
          "v": [
            [
              0.23000000000000004,
              -0.04000000000000001,
              0.58,
              0.31000000000000005
            ],
            [
              -0.22999999999999998,
              0.6900000000000002,
              0.05000000000000002,
              0.48000000000000004
            ],
            [
              0.43999999999999995,
              0.25000000000000006,
              -0.26000000000000006,
              0.7400000000000001
            ],
            [
              -0.11000000000000003,
              0.26000000000000006,
              0.38,
              -0.43999999999999995
            ]
          ]
        }
      }
    ],
    "output": [
      3,
      5
    ],
    "eos": true
  },
  "gradient": {
    "w": 1.0,
    "x": 2.0,
    "target": 4.0,
    "prediction": 2.0,
    "loss": 2.0,
    "gradient": -4.0,
    "eta": 0.2,
    "next_w": 1.8,
    "next_prediction": 3.6,
    "next_loss": 0.07999999999999996
  },
  "online": [
    {
      "max": 2,
      "sum": 1.0,
      "weighted_sum": [
        10.0,
        0.0
      ],
      "out": [
        10.0,
        0.0
      ]
    },
    {
      "max": 2,
      "sum": 1.3678794411714423,
      "weighted_sum": [
        10.0,
        7.357588823428847
      ],
      "out": [
        7.310585786300049,
        5.3788284273999025
      ]
    },
    {
      "max": 2,
      "sum": 1.5032147244080551,
      "weighted_sum": [
        10.676676416183064,
        8.03426523961191
      ],
      "out": [
        7.102562423600121,
        5.344722286947855
      ]
    }
  ],
  "rrf": [
    [
      "B",
      0.03252247488101534
    ],
    [
      "A",
      0.032266458495966696
    ],
    [
      "C",
      0.03200204813108039
    ]
  ],
  "mask": [
    [
      1,
      1,
      1,
      1,
      0
    ],
    [
      1,
      1,
      1,
      1,
      1
    ]
  ]
}
```