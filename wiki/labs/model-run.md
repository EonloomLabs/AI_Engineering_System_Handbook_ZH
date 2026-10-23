---
title: "模型实验：完整代码与运行结果"
description: "AI系统工程：本地教学正文与可追溯图表"
---

# 模型实验：完整代码与运行结果


<span id="mc-section-1"></span>


## 如何运行

阅读无需安装依赖；重新训练需Python与PyTorch。完整训练、测试在本次CPU环境实际运行，环境版本记录在结果JSON。

```
cd labs/model/lab
python tiny_model.py
python test_model.py
python reference_inference.py
```

第三个程序仅依赖Python标准库，读取已保存的训练权重进行独立前向与生成。


<span id="mc-section-2"></span>


## 实际记录

[run.json](../../labs/model/data/run.json)：本地完整文件。

[weights\_initial.json](../../labs/model/data/weights_initial.json)：本地完整文件。

[weights\_trained.json](../../labs/model/data/weights_trained.json)：本地完整文件。

[tests.json](../../labs/model/data/tests.json)：本地完整文件。

[tests.log](../../labs/model/data/tests.log)：本地完整文件。

[reference\_result.json](../../labs/model/data/reference_result.json)：本地完整文件。

| 核验项 | 本次结果 |
| --- | --- |
| 参数数 | 236 |
| 训练更新 | 400次 |
| 初始loss | 2.244673167946 |
| 最终loss | 0.139478689462 |
| 解析反向 vs autograd最大差 | 5.55111512313e-17 |
| 三轮KV vs全量logits差 | [0.0, 0.0, 0.0] |
| 测试 | { "run": 57, "failures": 0, "errors": 0, "skipped": 0, "python": "3.13.5", "torch": "2.10.0+cpu", "device": "cpu" } |


<span id="tiny-model"></span>


## tiny\_model.py · 完整源码

[本地源码文件](../../labs/model/lab/tiny_model.py)

```
"""可检查的单层因果语言模型 M。CPU/float64；无外部模型、网络或隐式标签移位。

运行: python tiny_model.py --out ../data
不是 Llama/GPT 的逐层复刻；结构约定在 MODEL_SPEC 中固定。
"""
from __future__ import annotations
import argparse, copy, hashlib, json, math, platform, sys
from pathlib import Path
from typing import Optional
import torch
from torch import nn
from torch.nn import functional as F

VOCAB = ['PAD','我','爱','学习','你','！','BOS','EOS']
PAD, BOS, EOS = 0, 6, 7
MODEL_SPEC = dict(vocab=VOCAB, vocab_size=8, width=4, ffn_width=8,
                  layers=1, heads=1, context=8, norm='RMSNorm', eps=1e-5,
                  position='learned absolute position', activation='ReLU',
                  bias=False, dropout=0.0, tied_embeddings=False,
                  dtype='float64', seed=23)
SEQUENCES = torch.tensor([[6,1,2,3,5,7],[6,4,2,3,5,7]], dtype=torch.long)

def jval(x):
    if isinstance(x, torch.Tensor): return x.detach().cpu().tolist()
    if isinstance(x, dict): return {k:jval(v) for k,v in x.items()}
    if isinstance(x, (tuple,list)): return [jval(y) for y in x]
    return x

def fingerprint(m):
    data={k:jval(v) for k,v in m.state_dict().items()}
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()

class TinyLM(nn.Module):
    """所有 W 按右乘 [in,out] 保存；没有调用含隐式转置的 nn.Linear。"""
    def __init__(self):
        super().__init__()
        g=torch.Generator().manual_seed(23)
        E=torch.tensor([[0,0,0,0],[.2,-.1,.7,.4],[-.3,.8,.1,.5],
                        [.6,.2,-.4,.9],[.1,-.5,.9,.3],[-.2,.4,.5,-.6],
                        [.4,-.2,.3,.1],[.1,.2,-.3,.4]],dtype=torch.float64)
        self.E=nn.Parameter(E)
        self.P=nn.Parameter(torch.randint(-2,3,(8,4),generator=g).double()*.05)
        for name, shape in [('Wq',(4,4)),('Wk',(4,4)),('Wv',(4,4)),('Wo',(4,4)),
                            ('W1',(4,8)),('W2',(8,4)),('U',(4,8))]:
            self.register_parameter(name,nn.Parameter(torch.randint(-3,4,shape,generator=g).double()*.1))
        for name in ('g1','g2','gf'): self.register_parameter(name,nn.Parameter(torch.ones(4,dtype=torch.float64)))

    @staticmethod
    def norm(x,g):
        r=torch.sqrt(x.square().mean(dim=-1,keepdim=True)+MODEL_SPEC['eps'])
        return x/r*g,r

    def forward(self, ids: torch.Tensor, *, cache=None, key_valid=None,
                position_ids=None, causal=True, return_trace=False):
        if ids.ndim!=2 or ids.dtype!=torch.long: raise ValueError('ids必须是[B,T] long tensor')
        B,T=ids.shape
        if T==0 or (ids<0).any() or (ids>=8).any(): raise ValueError('空输入或词表ID越界')
        past=0 if cache is None else cache[0].shape[1]
        if position_ids is None: position_ids=torch.arange(past,past+T,device=ids.device).expand(B,-1)
        if position_ids.shape!=ids.shape or (position_ids<0).any() or (position_ids>=8).any():
            raise ValueError('position_ids形状或范围错误')
        e=self.E[ids]; pos=self.P[position_ids]; x=e+pos
        n1,r1=self.norm(x,self.g1)
        q=n1@self.Wq; k_new=n1@self.Wk; v_new=n1@self.Wv
        k=k_new if cache is None else torch.cat((cache[0],k_new),dim=1)
        v=v_new if cache is None else torch.cat((cache[1],v_new),dim=1)
        K=k.shape[1]
        allowed=torch.ones(B,T,K,dtype=torch.bool,device=ids.device)
        if causal:
            allowed &= (torch.arange(K,device=ids.device)[None,:] <=
                        (past+torch.arange(T,device=ids.device))[:,None])[None,:,:]
        if key_valid is not None:
            if key_valid.shape!=(B,K):raise ValueError('key_valid必须覆盖历史与当前全部Key')
            allowed &= key_valid[:,None,:].bool()
        # 本实现拒绝完全没有可读Key的query。PAD query在工业实现中也可以单独跳过。
        if not allowed.any(dim=-1).all(): raise ValueError('出现全遮蔽query行')
        dot=q@k.transpose(-1,-2)
        scores=dot/math.sqrt(4)
        masked=scores.masked_fill(~allowed,float('-inf'))
        A=torch.softmax(masked,dim=-1)
        mix=A@v
        attn_delta=mix@self.Wo
        residual=x+attn_delta
        n2,r2=self.norm(residual,self.g2)
        ff_pre=n2@self.W1
        ff_act=F.relu(ff_pre)
        ff_delta=ff_act@self.W2
        hidden=residual+ff_delta
        final,rf=self.norm(hidden,self.gf)
        logits=final@self.U
        new_cache=(k,v)
        if not return_trace:return logits,new_cache
        trace=dict(ids=ids,position_ids=position_ids,embedding=e,position=pos,x=x,r1=r1,n1=n1,
                   q=q,k=k,v=v,dot=dot,scores=scores,allowed=allowed,A=A,mix=mix,
                   attn_delta=attn_delta,residual=residual,r2=r2,n2=n2,
                   ff_pre=ff_pre,ff_act=ff_act,ff_delta=ff_delta,hidden=hidden,
                   rf=rf,final=final,logits=logits,probabilities=torch.softmax(logits,dim=-1))
        return logits,new_cache,trace


def training_loss(logits,targets):
    """已对齐的目标；外部切片一次，本函数绝不再次移动标签。"""
    if logits.shape[:-1]!=targets.shape:raise ValueError('logits位置轴必须与targets对应')
    valid=targets.ne(-100)
    if not valid.any():raise ValueError('没有有效目标，不能取0/0均值')
    losses=F.cross_entropy(logits.reshape(-1,8),targets.reshape(-1),ignore_index=-100,reduction='none').reshape_as(targets)
    return losses.sum()/valid.sum(),losses


def rms_backward(x,gamma,r,dy):
    g=dy*gamma
    dx=g/r - x*(g*x).mean(dim=-1,keepdim=True)/(r**3)
    dgamma=(dy*x/r).sum(dim=(0,1))
    return dx,dgamma


def manual_backward(model,trace,targets):
    """只用链式法则和矩阵运算重建整层梯度，不调用 autograd。"""
    t={k:v.detach() for k,v in trace.items()}
    p={k:v.detach() for k,v in model.named_parameters()}
    safe=targets.clamp(min=0)
    onehot=F.one_hot(safe,8).double()
    count=targets.ne(-100).sum()
    dz=(t['probabilities']-onehot)*targets.ne(-100)[...,None]/count
    def wt(a,b):return a.reshape(-1,a.shape[-1]).T@b.reshape(-1,b.shape[-1])
    grads={}; backward={}
    grads['U']=wt(t['final'],dz)
    dfinal=dz@p['U'].T
    dhidden,grads['gf']=rms_backward(t['hidden'],p['gf'],t['rf'],dfinal)
    grads['W2']=wt(t['ff_act'],dhidden)
    dact=dhidden@p['W2'].T
    dpre=dact*t['ff_pre'].gt(0)
    grads['W1']=wt(t['n2'],dpre)
    dn2=dpre@p['W1'].T
    drnorm,grads['g2']=rms_backward(t['residual'],p['g2'],t['r2'],dn2)
    dresidual=dhidden+drnorm
    grads['Wo']=wt(t['mix'],dresidual)
    dmix=dresidual@p['Wo'].T
    dA=dmix@t['v'].transpose(-1,-2)
    dv=t['A'].transpose(-1,-2)@dmix
    ds=t['A']*(dA-(dA*t['A']).sum(dim=-1,keepdim=True))
    dq=ds@t['k']/math.sqrt(4)
    dk=ds.transpose(-1,-2)@t['q']/math.sqrt(4)
    grads['Wq']=wt(t['n1'],dq);grads['Wk']=wt(t['n1'],dk);grads['Wv']=wt(t['n1'],dv)
    dn1=dq@p['Wq'].T+dk@p['Wk'].T+dv@p['Wv'].T
    dxnorm,grads['g1']=rms_backward(t['x'],p['g1'],t['r1'],dn1)
    dx=dresidual+dxnorm
    grads['E']=torch.zeros_like(p['E']).index_add_(0,t['ids'].reshape(-1),dx.reshape(-1,4))
    grads['P']=torch.zeros_like(p['P']).index_add_(0,t['position_ids'].reshape(-1),dx.reshape(-1,4))
    backward.update(dz=dz,dfinal=dfinal,dhidden=dhidden,dact=dact,dpre=dpre,dn2=dn2,
                    drnorm=drnorm,dresidual=dresidual,dmix=dmix,dA=dA,dv=dv,ds=ds,
                    dq=dq,dk=dk,dn1=dn1,dxnorm=dxnorm,dx=dx)
    return grads,backward


def generate(model,prompt,max_new=5,use_cache=True):
    if not prompt:raise ValueError('prompt不能为空')
    model.eval();ids=torch.tensor([prompt],dtype=torch.long)
    full=ids.clone();cache=None;steps=[];reason='length'
    with torch.inference_mode():
        for step in range(max_new):
            if full.shape[1]>8:reason='context';break
            new=ids if use_cache else full
            log,c,tr=model(new,cache=cache if use_cache else None,return_trace=True)
            selected=int(log[0,-1].argmax())
            steps.append(dict(step=step,phase='prefill' if step==0 else 'decode',
                              prefix=full[0].tolist(),input=new[0].tolist(),
                              cache_before=0 if cache is None else cache[0].shape[1],
                              cache_after=c[0].shape[1],selected=selected,selected_text=VOCAB[selected],
                              logits=jval(log[0,-1]),probabilities=jval(tr['probabilities'][0,-1]),
                              trace=jval(tr)))
            full=torch.cat((full,torch.tensor([[selected]])),dim=1)
            if selected==EOS:reason='eos';break
            ids=torch.tensor([[selected]],dtype=torch.long);cache=c if use_cache else None
    return dict(tokens=full[0].tolist(),steps=steps,reason=reason)


def run(out:Path,steps:int=400):
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    out.mkdir(parents=True,exist_ok=True)
    model=TinyLM();initial=copy.deepcopy(model.state_dict())
    ids=SEQUENCES[:,:-1]; targets=SEQUENCES[:,1:]
    logits,_,trace=model(ids,return_trace=True);loss,per=training_loss(logits,targets)
    manual,back=manual_backward(model,trace,targets)
    loss.backward()
    checks={k:float((v-model.get_parameter(k).grad).abs().max()) for k,v in manual.items()}
    if max(checks.values())>1e-10:raise AssertionError(checks)
    data=dict(spec=MODEL_SPEC,environment=dict(python=platform.python_version(),torch=torch.__version__,device='cpu',threads=1),
              sequences=jval(SEQUENCES),input=jval(ids),target=jval(targets),
              parameter_count=sum(p.numel() for p in model.parameters()),
              initial_parameters=jval(initial),initial_trace=jval(trace),
              initial_loss=float(loss.detach()),initial_position_losses=jval(per),
              initial_gradients={k:jval(v.grad) for k,v in model.named_parameters()},
              analytic_backward=jval(back),analytic_gradient_errors=checks,
              initial_hash=fingerprint(model))
    model.zero_grad(set_to_none=True)
    opt=torch.optim.AdamW(model.parameters(),lr=.03,betas=(.9,.999),eps=1e-8,weight_decay=.01,foreach=False)
    history=[];first_two=[]
    for step in range(steps):
        model.train();opt.zero_grad(set_to_none=True)
        logits,_=model(ids);loss,_=training_loss(logits,targets)
        loss.backward()
        if step<2:
            par=model.Wq;idx=(0,0)
            state=opt.state.get(par,{})
            item=dict(step=step+1,weight_before=float(par[idx].detach()),gradient=float(par.grad[idx]),
                      m_before=float(state.get('exp_avg',torch.zeros_like(par))[idx]),
                      v_before=float(state.get('exp_avg_sq',torch.zeros_like(par))[idx]))
        opt.step()
        if step<2:
            item.update(weight_after=float(model.Wq[idx].detach()),
                        m_after=float(opt.state[model.Wq]['exp_avg'][idx]),
                        v_after=float(opt.state[model.Wq]['exp_avg_sq'][idx]))
            first_two.append(item)
        if step==0:
            data['after_one_parameters']=jval(model.state_dict())
            _,_,tr1=model(ids,return_trace=True);data['after_one_trace']=jval(tr1)
        if step in {0,1,2,4,9,19,49,99,199,299,steps-1}:
            with torch.no_grad():
                after,_=model(ids);lossafter,_=training_loss(after,targets)
            history.append(dict(updates=step+1,loss_before=float(loss.detach()),loss_after=float(lossafter)))
    checkpoint=dict(spec=MODEL_SPEC,parameters=jval(model.state_dict()))
    (out/'weights_trained.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2))
    (out/'weights_initial.json').write_text(json.dumps(dict(spec=MODEL_SPEC,parameters=jval(initial)),ensure_ascii=False,indent=2))
    # JSON不执行任意Python反序列化逻辑，便于教学审查。
    loaded=TinyLM()
    disk=json.loads((out/'weights_trained.json').read_text())
    loaded.load_state_dict({k:torch.tensor(v,dtype=torch.float64) for k,v in disk['parameters'].items()})
    loaded.eval()
    with torch.no_grad():
        l,_,tf=loaded(ids,return_trace=True);lf,pl=training_loss(l,targets)
    data.update(training_steps=steps,training_hyperparameters=dict(lr=.03,beta1=.9,beta2=.999,eps=1e-8,weight_decay=.01),
                history=history,adam_steps=first_two,trained_parameters=disk['parameters'],
                final_loss=float(lf),final_position_losses=jval(pl),final_trace=jval(tf),trained_hash=fingerprint(loaded))
    before=fingerprint(loaded)
    data['generation']=generate(loaded,[6,1,2],use_cache=True)
    data['generation_full']=generate(loaded,[6,1,2],use_cache=False)
    data['other_prompt']=generate(loaded,[6,4,2],use_cache=True)
    data['limited_generation']=generate(loaded,[6,1,2],max_new=2)
    data['inference_hash_after']=fingerprint(loaded)
    assert before==data['inference_hash_after']
    assert data['generation']['tokens']==[6,1,2,3,5,7],data['generation']['tokens']
    assert data['other_prompt']['tokens']==[6,4,2,3,5,7]
    errors=[]
    for a,b in zip(data['generation']['steps'],data['generation_full']['steps']):
        errors.append(max(abs(x-y) for x,y in zip(a['logits'],b['logits'])))
    assert max(errors)<1e-10,errors
    data['cache_full_max_errors']=errors
    (out/'run.json').write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps({k:data[k] for k in ['parameter_count','initial_loss','final_loss','training_steps','analytic_gradient_errors','cache_full_max_errors']},ensure_ascii=False,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parent.parent/'data');ap.add_argument('--steps',type=int,default=400)
    a=ap.parse_args()
    if a.steps<2:ap.error('--steps至少为2')
    run(a.out,a.steps)
```


<span id="reference-inference"></span>


## reference\_inference.py · 完整源码

[本地源码文件](../../labs/model/lab/reference_inference.py)

```
"""仅用Python标准库，从本课保存的JSON权重重新计算无缓存前向与生成。
这份实现刻意不用PyTorch，作为独立数值对照。不会训练或下载模型。
运行: python reference_inference.py
"""
from __future__ import annotations
import json, math
from pathlib import Path

def matmul(a,b):
    if not a or not b or len(a[0])!=len(b): raise ValueError('矩阵乘内侧尺寸不匹配')
    return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]

def trans(a):return [list(col) for col in zip(*a)]
def add(a,b):return [[x+y for x,y in zip(ra,rb)] for ra,rb in zip(a,b)]
def norm(a,g,eps=1e-5):
    out=[]
    for row in a:
        r=math.sqrt(sum(x*x for x in row)/len(row)+eps)
        out.append([x/r*v for x,v in zip(row,g)])
    return out

def softmax(row):
    m=max(row)
    if not math.isfinite(m):raise ValueError('这一行没有有限的可见分数')
    es=[math.exp(x-m) for x in row];s=sum(es)
    return [x/s for x in es]

def forward(ids,p):
    if not ids or len(ids)>8:raise ValueError('只支持1..8个位置')
    x=add([p['E'][i] for i in ids],[p['P'][i] for i in range(len(ids))])
    n=norm(x,p['g1']);q=matmul(n,p['Wq']);k=matmul(n,p['Wk']);v=matmul(n,p['Wv'])
    scores=matmul(q,trans(k))
    probs=[softmax([z/2 if j<=i else -math.inf for j,z in enumerate(row)]) for i,row in enumerate(scores)]
    r=add(x,matmul(matmul(probs,v),p['Wo']))
    ff=matmul(norm(r,p['g2']),p['W1']);ff=[[max(0,x) for x in row] for row in ff]
    h=add(r,matmul(ff,p['W2']))
    return matmul(norm(h,p['gf']),p['U'])

def generate(ids,p,limit=5):
    ids=list(ids);history=[]
    for _ in range(limit):
        z=forward(ids,p)[-1];prob=softmax(z);chosen=max(range(8),key=lambda i:z[i])
        history.append(dict(input=list(ids),logits=z,probabilities=prob,selected=chosen))
        ids.append(chosen)
        if chosen==7:break
    return ids,history

if __name__=='__main__':
    d=Path(__file__).resolve().parent.parent/'data'
    p=json.loads((d/'weights_trained.json').read_text())['parameters']
    tokens,history=generate([6,1,2],p)
    actual=json.loads((d/'run.json').read_text())
    errors=[max(abs(x-y) for x,y in zip(a['logits'],b['logits'])) for a,b in zip(history,actual['generation']['steps'])]
    assert tokens==[6,1,2,3,5,7]
    assert max(errors)<1e-10
    result=dict(tokens=tokens,max_error=max(errors),device='Python math on CPU; no tensor library')
    (d/'reference_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
```


<span id="test-model"></span>


## test\_model.py · 完整源码

[本地源码文件](../../labs/model/lab/test_model.py)

```
"""数值、因果性、训练/推理边界和常见错误的独立断言。"""
from __future__ import annotations
import copy,json,math,unittest,io,platform
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F
from tiny_model import TinyLM,training_loss,manual_backward,SEQUENCES,fingerprint,generate
from reference_inference import forward as py_forward,softmax as py_softmax
D=Path(__file__).resolve().parent.parent/'data'
R=json.loads((D/'run.json').read_text())
torch.set_num_threads(1)
DT=torch.float64

def loaded():
    m=TinyLM();m.load_state_dict({k:torch.tensor(v,dtype=DT) for k,v in R['trained_parameters'].items()});return m

class Arithmetic(unittest.TestCase):
    def test_matmul_value(self):
        self.assertEqual((torch.tensor([[1.,2.,3.],[4.,5.,6.]])@torch.tensor([[1.,0.],[0.,1.],[1.,1.]])).tolist(),[[4.,5.],[10.,11.]])
    def test_softmax_shift(self):
        a=torch.tensor([2.,1.,0.],dtype=DT);self.assertTrue(torch.allclose(a.softmax(-1),(a-2).softmax(-1)))
    def test_softmax_not_divide_logits(self):
        a=torch.tensor([2.,1.,0.],dtype=DT);self.assertGreater(float((a.softmax(-1)-a/a.sum()).abs().max()),.05)
    def test_probability_sum(self):
        self.assertAlmostEqual(sum(py_softmax([2,1,0])),1,places=14)
    def test_logsumexp_ce(self):
        z=torch.tensor([[2.,1.,0.]],dtype=DT);y=torch.tensor([1]);self.assertAlmostEqual(float(F.cross_entropy(z,y)),float(z.logsumexp(-1)-z[0,1]),places=14)
    def test_ce_gradient(self):
        z=torch.tensor([[2.,1.,0.]],dtype=DT,requires_grad=True);F.cross_entropy(z,torch.tensor([1])).backward();expected=z.detach().softmax(-1)-torch.tensor([[0.,1.,0.]],dtype=DT);self.assertTrue(torch.allclose(z.grad,expected))
    def test_double_softmax_wrong(self):
        z=torch.tensor([[2.,1.,0.]],dtype=DT);y=torch.tensor([1]);self.assertGreater(abs(float(F.cross_entropy(z,y)-F.cross_entropy(z.softmax(-1),y))),.1)
    def test_ln_rms_different(self):
        x=torch.tensor([1.,3.],dtype=DT);a=F.layer_norm(x,(2,),eps=1e-5);b=x/torch.sqrt(x.square().mean()+1e-5);self.assertLess(float(a[0]),0);self.assertGreater(float(b[0]),0)
    def test_adam_steps(self):
        for rec in R['adam_steps']:
            t=rec['step'];g=rec['gradient'];m=.9*rec['m_before']+.1*g;v=.999*rec['v_before']+.001*g*g
            w=rec['weight_before']*(1-.03*.01)-.03*(m/(1-.9**t))/(math.sqrt(v/(1-.999**t))+1e-8)
            self.assertAlmostEqual(w,rec['weight_after'],places=13)
    def test_training_lower_bound(self):
        self.assertGreaterEqual(R['final_loss'],math.log(2)/5)
        self.assertLess(R['final_loss'],.15)
    def test_quantization(self):
        x=.26;q=round(x/.1);self.assertEqual(q,3);self.assertAlmostEqual(q*.1-x,.04)
    def test_lora_rank(self):
        a=torch.tensor([[1.],[2.]],dtype=DT);b=torch.tensor([[1.,2.,3.]],dtype=DT);self.assertEqual((a@b).tolist(),[[1.,2.,3.],[2.,4.,6.]])
    def test_speculative_identity(self):
        p=[.6,.3,.1];q=[.2,.5,.3];accepted=[min(a,b) for a,b in zip(p,q)];rem=[max(a-b,0) for a,b in zip(p,q)];self.assertTrue(all(abs(a+b-c)<1e-15 for a,b,c in zip(accepted,rem,p)))
    def test_online_softmax(self):
        s=[2.,1.,0.];v=[10.,20.,30.];m=-math.inf;l=0;u=0
        for block in [[0,1],[2]]:
            nm=max([m]+[s[i] for i in block]);a=0 if m==-math.inf else math.exp(m-nm)
            l=a*l+sum(math.exp(s[i]-nm) for i in block);u=a*u+sum(math.exp(s[i]-nm)*v[i] for i in block);m=nm
        self.assertAlmostEqual(u/l,sum(a*b for a,b in zip(py_softmax(s),v)),places=13)
    def test_rope_relative(self):
        def rot(x,t):return [x[0]*math.cos(t)-x[1]*math.sin(t),x[0]*math.sin(t)+x[1]*math.cos(t)]
        q=[1,2];k=[-.5,1]
        dot=lambda a,b:sum(x*y for x,y in zip(a,b))
        self.assertAlmostEqual(dot(rot(q,.3),rot(k,.7)),dot(q,rot(k,.4)),places=14)

class ForwardAndGradient(unittest.TestCase):
    def setUp(self):self.m=TinyLM();self.x=SEQUENCES[:,:-1];self.y=SEQUENCES[:,1:]
    def test_parameter_count(self):self.assertEqual(sum(p.numel() for p in self.m.parameters()),236)
    def test_shapes(self):
        z,_,t=self.m(self.x,return_trace=True);self.assertEqual(tuple(z.shape),(2,5,8));self.assertEqual(tuple(t['A'].shape),(2,5,5))
    def test_rowsum(self):
        _,_,t=self.m(self.x,return_trace=True);self.assertTrue(torch.allclose(t['A'].sum(-1),torch.ones(2,5,dtype=DT)))
    def test_future_attention_zero(self):
        _,_,t=self.m(self.x,return_trace=True);self.assertEqual(float(t['A'].triu(1).abs().sum()),0)
    def test_future_input_no_effect(self):
        x=self.x.clone();x[0,4]=4;a,_=self.m(self.x);b,_=self.m(x);self.assertTrue(torch.equal(a[0,:4],b[0,:4]))
    def test_missing_causal_mask_detected(self):
        x=self.x.clone();x[0,4]=4;a,_=self.m(self.x,causal=False);b,_=self.m(x,causal=False);self.assertGreater(float((a[0,:4]-b[0,:4]).abs().max()),1e-4)
    def test_batch_matches_individual(self):
        a,_=self.m(self.x);b,_=self.m(self.x[:1]);self.assertTrue(torch.allclose(a[:1],b,atol=1e-14,rtol=1e-14))
    def test_batch_permutation(self):
        a,_=self.m(self.x);b,_=self.m(self.x.flip(0));self.assertTrue(torch.allclose(a,b.flip(0),atol=1e-14,rtol=1e-14))
    def test_entire_analytic_backward(self):
        z,_,t=self.m(self.x,return_trace=True);g,b=manual_backward(self.m,t,self.y);l,_=training_loss(z,self.y);l.backward()
        for k,p in self.m.named_parameters():self.assertTrue(torch.allclose(p.grad,g[k],atol=1e-12,rtol=1e-10),k)
    def test_qkv_input_paths_add(self):
        z,_,t=self.m(self.x,return_trace=True);g,b=manual_backward(self.m,t,self.y)
        expected=b['dq']@self.m.Wq.T+b['dk']@self.m.Wk.T+b['dv']@self.m.Wv.T
        self.assertTrue(torch.allclose(expected,b['dn1']))
    def test_embedding_duplicate_rows_accumulate(self):
        z,_,t=self.m(self.x,return_trace=True);g,b=manual_backward(self.m,t,self.y)
        self.assertTrue(torch.allclose(g['E'][2],b['dx'][0,2]+b['dx'][1,2]))
    def test_score_gradient_rowsum_zero(self):
        z,_,t=self.m(self.x,return_trace=True);g,b=manual_backward(self.m,t,self.y);self.assertLess(float(b['ds'].sum(-1).abs().max()),1e-12)
    def test_finite_difference_selected_coordinates(self):
        z,_=self.m(self.x);l,_=training_loss(z,self.y);l.backward();eps=1e-6
        for name,idx in [('Wq',(0,0)),('Wk',(2,1)),('Wv',(1,0)),('Wo',(2,3)),('W1',(0,3)),('W2',(2,1)),('U',(0,3)),('g1',(2,)),('g2',(2,)),('gf',(2,)),('E',(2,1)),('P',(2,1))]:
            p=self.m.get_parameter(name);old=float(p[idx].detach());g=float(p.grad[idx]);vals=[]
            with torch.no_grad():
                for sign in [1,-1]:
                    p[idx]=old+sign*eps;zz,_=self.m(self.x);ll,_=training_loss(zz,self.y);vals.append(float(ll))
                p[idx]=old
            self.assertAlmostEqual((vals[0]-vals[1])/(2*eps),g,places=7,msg=name)
    def test_sgd_small_step(self):
        z,_=self.m(self.x);l,_=training_loss(z,self.y);before=float(l.detach());l.backward()
        with torch.no_grad():
            for p in self.m.parameters():p-=.001*p.grad
        after,_=training_loss(self.m(self.x)[0],self.y);self.assertLess(float(after),before)
    def test_backward_not_update(self):
        old=fingerprint(self.m);z,_=self.m(self.x);training_loss(z,self.y)[0].backward();self.assertEqual(fingerprint(self.m),old)
    def test_grad_accumulation(self):
        z,_=self.m(self.x);l,_=training_loss(z,self.y);l.backward();first=self.m.U.grad.clone()
        z,_=self.m(self.x);training_loss(z,self.y)[0].backward();self.assertTrue(torch.allclose(self.m.U.grad,2*first))
    def test_ignored_target_gradient(self):
        z=torch.randn(1,3,8,dtype=DT,requires_grad=True);y=torch.tensor([[1,-100,2]]);training_loss(z,y)[0].backward();self.assertEqual(float(z.grad[0,1].abs().sum()),0)
    def test_all_ignored_rejected(self):
        with self.assertRaises(ValueError):training_loss(torch.zeros(1,2,8),torch.full((1,2),-100))
    def test_target_alignment(self):
        self.assertEqual(self.x[0].tolist(),[6,1,2,3,5]);self.assertEqual(self.y[0].tolist(),[1,2,3,5,7])
    def test_no_double_shift(self):
        z,_,t=self.m(self.x,return_trace=True);right,_=training_loss(z,self.y)
        wrong,_=training_loss(z[:,:-1],self.y[:,1:]);self.assertGreater(abs(float(right-wrong)),1e-3)
    def test_ce_without_prior_softmax(self):
        z,_=self.m(self.x);right,_=training_loss(z,self.y);wrong,_=training_loss(z.softmax(-1),self.y);self.assertGreater(abs(float(right-wrong)),.01)
    def test_right_padding_needs_final_valid(self):
        x=torch.tensor([[6,1,2,0]]);mask=torch.tensor([[1,1,1,0]],dtype=torch.bool)
        z,_=self.m(x,key_valid=mask);true,_=self.m(x[:,:3]);self.assertTrue(torch.allclose(z[:,2],true[:,-1]));self.assertGreater(float((z[:,3]-z[:,2]).abs().max()),1e-4)
    def test_padding_key_invisible(self):
        x=torch.tensor([[6,0,1,2]]);mask=torch.tensor([[1,0,1,1]],dtype=torch.bool);_,_,t=self.m(x,key_valid=mask,return_trace=True);self.assertEqual(float(t['A'][:,:,1].sum()),0)
    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):self.m(torch.empty(1,0,dtype=torch.long))
    def test_all_masked_rejected(self):
        with self.assertRaises(ValueError):self.m(self.x,key_valid=torch.zeros(2,5,dtype=torch.bool))

class InferenceAndInterfaces(unittest.TestCase):
    def test_reload_hash(self):self.assertEqual(fingerprint(loaded()),R['trained_hash'])
    def test_full_cache_outputs(self):
        m=loaded();a=generate(m,[6,1,2],use_cache=True);b=generate(m,[6,1,2],use_cache=False)
        self.assertEqual(a['tokens'],b['tokens'])
        for x,y in zip(a['steps'],b['steps']):self.assertLess(max(abs(i-j) for i,j in zip(x['logits'],y['logits'])),1e-10)
    def test_expected_tokens(self):self.assertEqual(generate(loaded(),[6,1,2])['tokens'],[6,1,2,3,5,7])
    def test_no_parameter_change(self):
        m=loaded();h=fingerprint(m);generate(m,[6,1,2]);self.assertEqual(fingerprint(m),h)
    def test_cache_lag(self):
        a=generate(loaded(),[6,1,2]);self.assertEqual([s['cache_after'] for s in a['steps']],[3,4,5]);self.assertEqual(len(a['tokens']),6)
    def test_limit_not_eos(self):
        a=generate(loaded(),[6,1,2],max_new=2);self.assertEqual(a['reason'],'length');self.assertNotEqual(a['tokens'][-1],7)
    def test_two_new_tokens_cache(self):
        m=loaded();x=SEQUENCES[:1,:-1];allz,_=m(x);_,c=m(x[:,:3]);part,_=m(x[:,3:],cache=c);self.assertTrue(torch.allclose(allz[:,3:],part,atol=1e-12))
    def test_wrong_position_changes_output(self):
        m=loaded();_,c=m(torch.tensor([[6,1,2]]));good,_=m(torch.tensor([[3]]),cache=c);bad,_=m(torch.tensor([[3]]),cache=c,position_ids=torch.zeros(1,1,dtype=torch.long));self.assertGreater(float((good-bad).abs().max()),.01)
    def test_stale_cache_after_weights_change(self):
        m=loaded();x=torch.tensor([[6,1,2,3]]);_,c=m(x[:,:3])
        with torch.no_grad():m.Wv.mul_(.5)
        stale,_=m(x[:,3:],cache=c);fresh,_=m(x);self.assertGreater(float((stale[:,-1]-fresh[:,-1]).abs().max()),1e-4)
    def test_stdlib_reference(self):
        z=py_forward([6,1,2],R['trained_parameters']);expected=R['generation']['steps'][0]['logits'];self.assertLess(max(abs(x-y) for x,y in zip(z[-1],expected)),1e-10)
    def test_eval_does_not_disable_grad(self):
        m=TinyLM().eval();z,_=m(SEQUENCES[:,:-1]);self.assertTrue(z.requires_grad)
    def test_no_grad_does_not_switch_dropout(self):
        d=nn.Dropout(.5).train();x=torch.ones(1000)
        with torch.no_grad():y=d(x)
        self.assertGreater(int(y.eq(0).sum()),0)
    def test_eval_switches_dropout(self):
        d=nn.Dropout(.5).eval();x=torch.ones(100);self.assertTrue(torch.equal(d(x),x))
    def test_sdpa_non_square_alignment(self):
        q=torch.ones(1,1,2,1,dtype=DT);k=torch.ones(1,1,5,1,dtype=DT);v=torch.arange(1,6,dtype=DT).reshape(1,1,5,1)
        good=(torch.arange(5)[None,:]<=torch.tensor([3,4])[:,None])
        a=F.scaled_dot_product_attention(q,k,v,attn_mask=good);b=F.scaled_dot_product_attention(q,k,v,is_causal=True)
        self.assertEqual(a.flatten().tolist(),[2.5,3.]);self.assertEqual(b.flatten().tolist(),[1.,1.5])
    def test_sdpa_scale_once(self):
        q=torch.tensor([[[[1.,2.]]]],dtype=DT);k=torch.tensor([[[[1.,0.],[0.,1.]]]],dtype=DT);v=k
        a=F.scaled_dot_product_attention(q,k,v);manual=(q@k.transpose(-1,-2)/math.sqrt(2)).softmax(-1)@v
        self.assertTrue(torch.allclose(a,manual));b=F.scaled_dot_product_attention(q/math.sqrt(2),k,v);self.assertGreater(float((a-b).abs().max()),.01)
    def test_linear_storage_transpose(self):
        x=torch.tensor([[1.,2.]],dtype=DT);w=torch.tensor([[1.,3.],[2.,4.]],dtype=DT)
        self.assertEqual((x@w).tolist(),[[5.,11.]]);self.assertEqual(F.linear(x,w).tolist(),[[7.,10.]])
    def test_training_loss_drops(self):self.assertLess(R['final_loss'],R['initial_loss']/10)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
    stream=io.StringIO();res=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    log=stream.getvalue();print(log)
    (D/'tests.log').write_text(log)
    (D/'tests.json').write_text(json.dumps(dict(run=res.testsRun,failures=len(res.failures),errors=len(res.errors),skipped=len(res.skipped),python=platform.python_version(),torch=torch.__version__,device='cpu'),indent=2))
    if not res.wasSuccessful():raise SystemExit(1)
```