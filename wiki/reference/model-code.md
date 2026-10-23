---
title: "模型实验源码与原始参数"
description: "AI系统工程：本地教学正文与可追溯图表"
---

# 模型实验源码与原始参数

代码可在本地逐行核对。正文中的实现引用直接定位到这里；本页不是另一套课程。


<span id="tiny_model"></span>


## lab/tiny\_model.py

[原文件：labs/model/lab/tiny\_model.py](../../labs/model/lab/tiny_model.py)

```

<span id="tiny_model-L1"></span>
"""可检查的单层因果语言模型 M。CPU/float64；无外部模型、网络或隐式标签移位。

<span id="tiny_model-L2"></span>
 

<span id="tiny_model-L3"></span>
运行: python tiny_model.py --out ../data

<span id="tiny_model-L4"></span>
不是 Llama/GPT 的逐层复刻；结构约定在 MODEL_SPEC 中固定。

<span id="tiny_model-L5"></span>
"""

<span id="tiny_model-L6"></span>
from __future__ import annotations

<span id="tiny_model-L7"></span>
import argparse, copy, hashlib, json, math, platform, sys

<span id="tiny_model-L8"></span>
from pathlib import Path

<span id="tiny_model-L9"></span>
from typing import Optional

<span id="tiny_model-L10"></span>
import torch

<span id="tiny_model-L11"></span>
from torch import nn

<span id="tiny_model-L12"></span>
from torch.nn import functional as F

<span id="tiny_model-L13"></span>
 

<span id="tiny_model-L14"></span>
VOCAB = ['PAD','我','爱','学习','你','！','BOS','EOS']

<span id="tiny_model-L15"></span>
PAD, BOS, EOS = 0, 6, 7

<span id="tiny_model-L16"></span>
MODEL_SPEC = dict(vocab=VOCAB, vocab_size=8, width=4, ffn_width=8,

<span id="tiny_model-L17"></span>
                  layers=1, heads=1, context=8, norm='RMSNorm', eps=1e-5,

<span id="tiny_model-L18"></span>
                  position='learned absolute position', activation='ReLU',

<span id="tiny_model-L19"></span>
                  bias=False, dropout=0.0, tied_embeddings=False,

<span id="tiny_model-L20"></span>
                  dtype='float64', seed=23)

<span id="tiny_model-L21"></span>
SEQUENCES = torch.tensor([[6,1,2,3,5,7],[6,4,2,3,5,7]], dtype=torch.long)

<span id="tiny_model-L22"></span>
 

<span id="tiny_model-L23"></span>
def jval(x):

<span id="tiny_model-L24"></span>
    if isinstance(x, torch.Tensor): return x.detach().cpu().tolist()

<span id="tiny_model-L25"></span>
    if isinstance(x, dict): return {k:jval(v) for k,v in x.items()}

<span id="tiny_model-L26"></span>
    if isinstance(x, (tuple,list)): return [jval(y) for y in x]

<span id="tiny_model-L27"></span>
    return x

<span id="tiny_model-L28"></span>
 

<span id="tiny_model-L29"></span>
def fingerprint(m):

<span id="tiny_model-L30"></span>
    data={k:jval(v) for k,v in m.state_dict().items()}

<span id="tiny_model-L31"></span>
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()

<span id="tiny_model-L32"></span>
 

<span id="tiny_model-L33"></span>
class TinyLM(nn.Module):

<span id="tiny_model-L34"></span>
    """所有 W 按右乘 [in,out] 保存；没有调用含隐式转置的 nn.Linear。"""

<span id="tiny_model-L35"></span>
    def __init__(self):

<span id="tiny_model-L36"></span>
        super().__init__()

<span id="tiny_model-L37"></span>
        g=torch.Generator().manual_seed(23)

<span id="tiny_model-L38"></span>
        E=torch.tensor([[0,0,0,0],[.2,-.1,.7,.4],[-.3,.8,.1,.5],

<span id="tiny_model-L39"></span>
                        [.6,.2,-.4,.9],[.1,-.5,.9,.3],[-.2,.4,.5,-.6],

<span id="tiny_model-L40"></span>
                        [.4,-.2,.3,.1],[.1,.2,-.3,.4]],dtype=torch.float64)

<span id="tiny_model-L41"></span>
        self.E=nn.Parameter(E)

<span id="tiny_model-L42"></span>
        self.P=nn.Parameter(torch.randint(-2,3,(8,4),generator=g).double()*.05)

<span id="tiny_model-L43"></span>
        for name, shape in [('Wq',(4,4)),('Wk',(4,4)),('Wv',(4,4)),('Wo',(4,4)),

<span id="tiny_model-L44"></span>
                            ('W1',(4,8)),('W2',(8,4)),('U',(4,8))]:

<span id="tiny_model-L45"></span>
            self.register_parameter(name,nn.Parameter(torch.randint(-3,4,shape,generator=g).double()*.1))

<span id="tiny_model-L46"></span>
        for name in ('g1','g2','gf'): self.register_parameter(name,nn.Parameter(torch.ones(4,dtype=torch.float64)))

<span id="tiny_model-L47"></span>
 

<span id="tiny_model-L48"></span>
    @staticmethod

<span id="tiny_model-L49"></span>
    def norm(x,g):

<span id="tiny_model-L50"></span>
        r=torch.sqrt(x.square().mean(dim=-1,keepdim=True)+MODEL_SPEC['eps'])

<span id="tiny_model-L51"></span>
        return x/r*g,r

<span id="tiny_model-L52"></span>
 

<span id="tiny_model-L53"></span>
    def forward(self, ids: torch.Tensor, *, cache=None, key_valid=None,

<span id="tiny_model-L54"></span>
                position_ids=None, causal=True, return_trace=False):

<span id="tiny_model-L55"></span>
        if ids.ndim!=2 or ids.dtype!=torch.long: raise ValueError('ids必须是[B,T] long tensor')

<span id="tiny_model-L56"></span>
        B,T=ids.shape

<span id="tiny_model-L57"></span>
        if T==0 or (ids<0).any() or (ids>=8).any(): raise ValueError('空输入或词表ID越界')

<span id="tiny_model-L58"></span>
        past=0 if cache is None else cache[0].shape[1]

<span id="tiny_model-L59"></span>
        if position_ids is None: position_ids=torch.arange(past,past+T,device=ids.device).expand(B,-1)

<span id="tiny_model-L60"></span>
        if position_ids.shape!=ids.shape or (position_ids<0).any() or (position_ids>=8).any():

<span id="tiny_model-L61"></span>
            raise ValueError('position_ids形状或范围错误')

<span id="tiny_model-L62"></span>
        e=self.E[ids]; pos=self.P[position_ids]; x=e+pos

<span id="tiny_model-L63"></span>
        n1,r1=self.norm(x,self.g1)

<span id="tiny_model-L64"></span>
        q=n1@self.Wq; k_new=n1@self.Wk; v_new=n1@self.Wv

<span id="tiny_model-L65"></span>
        k=k_new if cache is None else torch.cat((cache[0],k_new),dim=1)

<span id="tiny_model-L66"></span>
        v=v_new if cache is None else torch.cat((cache[1],v_new),dim=1)

<span id="tiny_model-L67"></span>
        K=k.shape[1]

<span id="tiny_model-L68"></span>
        allowed=torch.ones(B,T,K,dtype=torch.bool,device=ids.device)

<span id="tiny_model-L69"></span>
        if causal:

<span id="tiny_model-L70"></span>
            allowed &= (torch.arange(K,device=ids.device)[None,:] <=

<span id="tiny_model-L71"></span>
                        (past+torch.arange(T,device=ids.device))[:,None])[None,:,:]

<span id="tiny_model-L72"></span>
        if key_valid is not None:

<span id="tiny_model-L73"></span>
            if key_valid.shape!=(B,K):raise ValueError('key_valid必须覆盖历史与当前全部Key')

<span id="tiny_model-L74"></span>
            allowed &= key_valid[:,None,:].bool()

<span id="tiny_model-L75"></span>
        # 本实现拒绝完全没有可读Key的query。PAD query在工业实现中也可以单独跳过。

<span id="tiny_model-L76"></span>
        if not allowed.any(dim=-1).all(): raise ValueError('出现全遮蔽query行')

<span id="tiny_model-L77"></span>
        dot=q@k.transpose(-1,-2)

<span id="tiny_model-L78"></span>
        scores=dot/math.sqrt(4)

<span id="tiny_model-L79"></span>
        masked=scores.masked_fill(~allowed,float('-inf'))

<span id="tiny_model-L80"></span>
        A=torch.softmax(masked,dim=-1)

<span id="tiny_model-L81"></span>
        mix=A@v

<span id="tiny_model-L82"></span>
        attn_delta=mix@self.Wo

<span id="tiny_model-L83"></span>
        residual=x+attn_delta

<span id="tiny_model-L84"></span>
        n2,r2=self.norm(residual,self.g2)

<span id="tiny_model-L85"></span>
        ff_pre=n2@self.W1

<span id="tiny_model-L86"></span>
        ff_act=F.relu(ff_pre)

<span id="tiny_model-L87"></span>
        ff_delta=ff_act@self.W2

<span id="tiny_model-L88"></span>
        hidden=residual+ff_delta

<span id="tiny_model-L89"></span>
        final,rf=self.norm(hidden,self.gf)

<span id="tiny_model-L90"></span>
        logits=final@self.U

<span id="tiny_model-L91"></span>
        new_cache=(k,v)

<span id="tiny_model-L92"></span>
        if not return_trace:return logits,new_cache

<span id="tiny_model-L93"></span>
        trace=dict(ids=ids,position_ids=position_ids,embedding=e,position=pos,x=x,r1=r1,n1=n1,

<span id="tiny_model-L94"></span>
                   q=q,k=k,v=v,dot=dot,scores=scores,allowed=allowed,A=A,mix=mix,

<span id="tiny_model-L95"></span>
                   attn_delta=attn_delta,residual=residual,r2=r2,n2=n2,

<span id="tiny_model-L96"></span>
                   ff_pre=ff_pre,ff_act=ff_act,ff_delta=ff_delta,hidden=hidden,

<span id="tiny_model-L97"></span>
                   rf=rf,final=final,logits=logits,probabilities=torch.softmax(logits,dim=-1))

<span id="tiny_model-L98"></span>
        return logits,new_cache,trace

<span id="tiny_model-L99"></span>
 

<span id="tiny_model-L100"></span>
 

<span id="tiny_model-L101"></span>
def training_loss(logits,targets):

<span id="tiny_model-L102"></span>
    """已对齐的目标；外部切片一次，本函数绝不再次移动标签。"""

<span id="tiny_model-L103"></span>
    if logits.shape[:-1]!=targets.shape:raise ValueError('logits位置轴必须与targets对应')

<span id="tiny_model-L104"></span>
    valid=targets.ne(-100)

<span id="tiny_model-L105"></span>
    if not valid.any():raise ValueError('没有有效目标，不能取0/0均值')

<span id="tiny_model-L106"></span>
    losses=F.cross_entropy(logits.reshape(-1,8),targets.reshape(-1),ignore_index=-100,reduction='none').reshape_as(targets)

<span id="tiny_model-L107"></span>
    return losses.sum()/valid.sum(),losses

<span id="tiny_model-L108"></span>
 

<span id="tiny_model-L109"></span>
 

<span id="tiny_model-L110"></span>
def rms_backward(x,gamma,r,dy):

<span id="tiny_model-L111"></span>
    g=dy*gamma

<span id="tiny_model-L112"></span>
    dx=g/r - x*(g*x).mean(dim=-1,keepdim=True)/(r**3)

<span id="tiny_model-L113"></span>
    dgamma=(dy*x/r).sum(dim=(0,1))

<span id="tiny_model-L114"></span>
    return dx,dgamma

<span id="tiny_model-L115"></span>
 

<span id="tiny_model-L116"></span>
 

<span id="tiny_model-L117"></span>
def manual_backward(model,trace,targets):

<span id="tiny_model-L118"></span>
    """只用链式法则和矩阵运算重建整层梯度，不调用 autograd。"""

<span id="tiny_model-L119"></span>
    t={k:v.detach() for k,v in trace.items()}

<span id="tiny_model-L120"></span>
    p={k:v.detach() for k,v in model.named_parameters()}

<span id="tiny_model-L121"></span>
    safe=targets.clamp(min=0)

<span id="tiny_model-L122"></span>
    onehot=F.one_hot(safe,8).double()

<span id="tiny_model-L123"></span>
    count=targets.ne(-100).sum()

<span id="tiny_model-L124"></span>
    dz=(t['probabilities']-onehot)*targets.ne(-100)[...,None]/count

<span id="tiny_model-L125"></span>
    def wt(a,b):return a.reshape(-1,a.shape[-1]).T@b.reshape(-1,b.shape[-1])

<span id="tiny_model-L126"></span>
    grads={}; backward={}

<span id="tiny_model-L127"></span>
    grads['U']=wt(t['final'],dz)

<span id="tiny_model-L128"></span>
    dfinal=dz@p['U'].T

<span id="tiny_model-L129"></span>
    dhidden,grads['gf']=rms_backward(t['hidden'],p['gf'],t['rf'],dfinal)

<span id="tiny_model-L130"></span>
    grads['W2']=wt(t['ff_act'],dhidden)

<span id="tiny_model-L131"></span>
    dact=dhidden@p['W2'].T

<span id="tiny_model-L132"></span>
    dpre=dact*t['ff_pre'].gt(0)

<span id="tiny_model-L133"></span>
    grads['W1']=wt(t['n2'],dpre)

<span id="tiny_model-L134"></span>
    dn2=dpre@p['W1'].T

<span id="tiny_model-L135"></span>
    drnorm,grads['g2']=rms_backward(t['residual'],p['g2'],t['r2'],dn2)

<span id="tiny_model-L136"></span>
    dresidual=dhidden+drnorm

<span id="tiny_model-L137"></span>
    grads['Wo']=wt(t['mix'],dresidual)

<span id="tiny_model-L138"></span>
    dmix=dresidual@p['Wo'].T

<span id="tiny_model-L139"></span>
    dA=dmix@t['v'].transpose(-1,-2)

<span id="tiny_model-L140"></span>
    dv=t['A'].transpose(-1,-2)@dmix

<span id="tiny_model-L141"></span>
    ds=t['A']*(dA-(dA*t['A']).sum(dim=-1,keepdim=True))

<span id="tiny_model-L142"></span>
    dq=ds@t['k']/math.sqrt(4)

<span id="tiny_model-L143"></span>
    dk=ds.transpose(-1,-2)@t['q']/math.sqrt(4)

<span id="tiny_model-L144"></span>
    grads['Wq']=wt(t['n1'],dq);grads['Wk']=wt(t['n1'],dk);grads['Wv']=wt(t['n1'],dv)

<span id="tiny_model-L145"></span>
    dn1=dq@p['Wq'].T+dk@p['Wk'].T+dv@p['Wv'].T

<span id="tiny_model-L146"></span>
    dxnorm,grads['g1']=rms_backward(t['x'],p['g1'],t['r1'],dn1)

<span id="tiny_model-L147"></span>
    dx=dresidual+dxnorm

<span id="tiny_model-L148"></span>
    grads['E']=torch.zeros_like(p['E']).index_add_(0,t['ids'].reshape(-1),dx.reshape(-1,4))

<span id="tiny_model-L149"></span>
    grads['P']=torch.zeros_like(p['P']).index_add_(0,t['position_ids'].reshape(-1),dx.reshape(-1,4))

<span id="tiny_model-L150"></span>
    backward.update(dz=dz,dfinal=dfinal,dhidden=dhidden,dact=dact,dpre=dpre,dn2=dn2,

<span id="tiny_model-L151"></span>
                    drnorm=drnorm,dresidual=dresidual,dmix=dmix,dA=dA,dv=dv,ds=ds,

<span id="tiny_model-L152"></span>
                    dq=dq,dk=dk,dn1=dn1,dxnorm=dxnorm,dx=dx)

<span id="tiny_model-L153"></span>
    return grads,backward

<span id="tiny_model-L154"></span>
 

<span id="tiny_model-L155"></span>
 

<span id="tiny_model-L156"></span>
def generate(model,prompt,max_new=5,use_cache=True):

<span id="tiny_model-L157"></span>
    if not prompt:raise ValueError('prompt不能为空')

<span id="tiny_model-L158"></span>
    model.eval();ids=torch.tensor([prompt],dtype=torch.long)

<span id="tiny_model-L159"></span>
    full=ids.clone();cache=None;steps=[];reason='length'

<span id="tiny_model-L160"></span>
    with torch.inference_mode():

<span id="tiny_model-L161"></span>
        for step in range(max_new):

<span id="tiny_model-L162"></span>
            if full.shape[1]>8:reason='context';break

<span id="tiny_model-L163"></span>
            new=ids if use_cache else full

<span id="tiny_model-L164"></span>
            log,c,tr=model(new,cache=cache if use_cache else None,return_trace=True)

<span id="tiny_model-L165"></span>
            selected=int(log[0,-1].argmax())

<span id="tiny_model-L166"></span>
            steps.append(dict(step=step,phase='prefill' if step==0 else 'decode',

<span id="tiny_model-L167"></span>
                              prefix=full[0].tolist(),input=new[0].tolist(),

<span id="tiny_model-L168"></span>
                              cache_before=0 if cache is None else cache[0].shape[1],

<span id="tiny_model-L169"></span>
                              cache_after=c[0].shape[1],selected=selected,selected_text=VOCAB[selected],

<span id="tiny_model-L170"></span>
                              logits=jval(log[0,-1]),probabilities=jval(tr['probabilities'][0,-1]),

<span id="tiny_model-L171"></span>
                              trace=jval(tr)))

<span id="tiny_model-L172"></span>
            full=torch.cat((full,torch.tensor([[selected]])),dim=1)

<span id="tiny_model-L173"></span>
            if selected==EOS:reason='eos';break

<span id="tiny_model-L174"></span>
            ids=torch.tensor([[selected]],dtype=torch.long);cache=c if use_cache else None

<span id="tiny_model-L175"></span>
    return dict(tokens=full[0].tolist(),steps=steps,reason=reason)

<span id="tiny_model-L176"></span>
 

<span id="tiny_model-L177"></span>
 

<span id="tiny_model-L178"></span>
def run(out:Path,steps:int=400):

<span id="tiny_model-L179"></span>
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)

<span id="tiny_model-L180"></span>
    out.mkdir(parents=True,exist_ok=True)

<span id="tiny_model-L181"></span>
    model=TinyLM();initial=copy.deepcopy(model.state_dict())

<span id="tiny_model-L182"></span>
    ids=SEQUENCES[:,:-1]; targets=SEQUENCES[:,1:]

<span id="tiny_model-L183"></span>
    logits,_,trace=model(ids,return_trace=True);loss,per=training_loss(logits,targets)

<span id="tiny_model-L184"></span>
    manual,back=manual_backward(model,trace,targets)

<span id="tiny_model-L185"></span>
    loss.backward()

<span id="tiny_model-L186"></span>
    checks={k:float((v-model.get_parameter(k).grad).abs().max()) for k,v in manual.items()}

<span id="tiny_model-L187"></span>
    if max(checks.values())>1e-10:raise AssertionError(checks)

<span id="tiny_model-L188"></span>
    data=dict(spec=MODEL_SPEC,environment=dict(python=platform.python_version(),torch=torch.__version__,device='cpu',threads=1),

<span id="tiny_model-L189"></span>
              sequences=jval(SEQUENCES),input=jval(ids),target=jval(targets),

<span id="tiny_model-L190"></span>
              parameter_count=sum(p.numel() for p in model.parameters()),

<span id="tiny_model-L191"></span>
              initial_parameters=jval(initial),initial_trace=jval(trace),

<span id="tiny_model-L192"></span>
              initial_loss=float(loss.detach()),initial_position_losses=jval(per),

<span id="tiny_model-L193"></span>
              initial_gradients={k:jval(v.grad) for k,v in model.named_parameters()},

<span id="tiny_model-L194"></span>
              analytic_backward=jval(back),analytic_gradient_errors=checks,

<span id="tiny_model-L195"></span>
              initial_hash=fingerprint(model))

<span id="tiny_model-L196"></span>
    model.zero_grad(set_to_none=True)

<span id="tiny_model-L197"></span>
    opt=torch.optim.AdamW(model.parameters(),lr=.03,betas=(.9,.999),eps=1e-8,weight_decay=.01,foreach=False)

<span id="tiny_model-L198"></span>
    history=[];first_two=[]

<span id="tiny_model-L199"></span>
    for step in range(steps):

<span id="tiny_model-L200"></span>
        model.train();opt.zero_grad(set_to_none=True)

<span id="tiny_model-L201"></span>
        logits,_=model(ids);loss,_=training_loss(logits,targets)

<span id="tiny_model-L202"></span>
        loss.backward()

<span id="tiny_model-L203"></span>
        if step<2:

<span id="tiny_model-L204"></span>
            par=model.Wq;idx=(0,0)

<span id="tiny_model-L205"></span>
            state=opt.state.get(par,{})

<span id="tiny_model-L206"></span>
            item=dict(step=step+1,weight_before=float(par[idx].detach()),gradient=float(par.grad[idx]),

<span id="tiny_model-L207"></span>
                      m_before=float(state.get('exp_avg',torch.zeros_like(par))[idx]),

<span id="tiny_model-L208"></span>
                      v_before=float(state.get('exp_avg_sq',torch.zeros_like(par))[idx]))

<span id="tiny_model-L209"></span>
        opt.step()

<span id="tiny_model-L210"></span>
        if step<2:

<span id="tiny_model-L211"></span>
            item.update(weight_after=float(model.Wq[idx].detach()),

<span id="tiny_model-L212"></span>
                        m_after=float(opt.state[model.Wq]['exp_avg'][idx]),

<span id="tiny_model-L213"></span>
                        v_after=float(opt.state[model.Wq]['exp_avg_sq'][idx]))

<span id="tiny_model-L214"></span>
            first_two.append(item)

<span id="tiny_model-L215"></span>
        if step==0:

<span id="tiny_model-L216"></span>
            data['after_one_parameters']=jval(model.state_dict())

<span id="tiny_model-L217"></span>
            _,_,tr1=model(ids,return_trace=True);data['after_one_trace']=jval(tr1)

<span id="tiny_model-L218"></span>
        if step in {0,1,2,4,9,19,49,99,199,299,steps-1}:

<span id="tiny_model-L219"></span>
            with torch.no_grad():

<span id="tiny_model-L220"></span>
                after,_=model(ids);lossafter,_=training_loss(after,targets)

<span id="tiny_model-L221"></span>
            history.append(dict(updates=step+1,loss_before=float(loss.detach()),loss_after=float(lossafter)))

<span id="tiny_model-L222"></span>
    checkpoint=dict(spec=MODEL_SPEC,parameters=jval(model.state_dict()))

<span id="tiny_model-L223"></span>
    (out/'weights_trained.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2))

<span id="tiny_model-L224"></span>
    (out/'weights_initial.json').write_text(json.dumps(dict(spec=MODEL_SPEC,parameters=jval(initial)),ensure_ascii=False,indent=2))

<span id="tiny_model-L225"></span>
    # JSON不执行任意Python反序列化逻辑，便于教学审查。

<span id="tiny_model-L226"></span>
    loaded=TinyLM()

<span id="tiny_model-L227"></span>
    disk=json.loads((out/'weights_trained.json').read_text())

<span id="tiny_model-L228"></span>
    loaded.load_state_dict({k:torch.tensor(v,dtype=torch.float64) for k,v in disk['parameters'].items()})

<span id="tiny_model-L229"></span>
    loaded.eval()

<span id="tiny_model-L230"></span>
    with torch.no_grad():

<span id="tiny_model-L231"></span>
        l,_,tf=loaded(ids,return_trace=True);lf,pl=training_loss(l,targets)

<span id="tiny_model-L232"></span>
    data.update(training_steps=steps,training_hyperparameters=dict(lr=.03,beta1=.9,beta2=.999,eps=1e-8,weight_decay=.01),

<span id="tiny_model-L233"></span>
                history=history,adam_steps=first_two,trained_parameters=disk['parameters'],

<span id="tiny_model-L234"></span>
                final_loss=float(lf),final_position_losses=jval(pl),final_trace=jval(tf),trained_hash=fingerprint(loaded))

<span id="tiny_model-L235"></span>
    before=fingerprint(loaded)

<span id="tiny_model-L236"></span>
    data['generation']=generate(loaded,[6,1,2],use_cache=True)

<span id="tiny_model-L237"></span>
    data['generation_full']=generate(loaded,[6,1,2],use_cache=False)

<span id="tiny_model-L238"></span>
    data['other_prompt']=generate(loaded,[6,4,2],use_cache=True)

<span id="tiny_model-L239"></span>
    data['limited_generation']=generate(loaded,[6,1,2],max_new=2)

<span id="tiny_model-L240"></span>
    data['inference_hash_after']=fingerprint(loaded)

<span id="tiny_model-L241"></span>
    assert before==data['inference_hash_after']

<span id="tiny_model-L242"></span>
    assert data['generation']['tokens']==[6,1,2,3,5,7],data['generation']['tokens']

<span id="tiny_model-L243"></span>
    assert data['other_prompt']['tokens']==[6,4,2,3,5,7]

<span id="tiny_model-L244"></span>
    errors=[]

<span id="tiny_model-L245"></span>
    for a,b in zip(data['generation']['steps'],data['generation_full']['steps']):

<span id="tiny_model-L246"></span>
        errors.append(max(abs(x-y) for x,y in zip(a['logits'],b['logits'])))

<span id="tiny_model-L247"></span>
    assert max(errors)<1e-10,errors

<span id="tiny_model-L248"></span>
    data['cache_full_max_errors']=errors

<span id="tiny_model-L249"></span>
    (out/'run.json').write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False))

<span id="tiny_model-L250"></span>
    print(json.dumps({k:data[k] for k in ['parameter_count','initial_loss','final_loss','training_steps','analytic_gradient_errors','cache_full_max_errors']},ensure_ascii=False,indent=2))

<span id="tiny_model-L251"></span>
 

<span id="tiny_model-L252"></span>
if __name__=='__main__':

<span id="tiny_model-L253"></span>
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parent.parent/'data');ap.add_argument('--steps',type=int,default=400)

<span id="tiny_model-L254"></span>
    a=ap.parse_args()

<span id="tiny_model-L255"></span>
    if a.steps<2:ap.error('--steps至少为2')

<span id="tiny_model-L256"></span>
    run(a.out,a.steps)
```


<span id="reference_inference"></span>


## lab/reference\_inference.py

[原文件：labs/model/lab/reference\_inference.py](../../labs/model/lab/reference_inference.py)

```

<span id="reference_inference-L1"></span>
"""仅用Python标准库，从本课保存的JSON权重重新计算无缓存前向与生成。

<span id="reference_inference-L2"></span>
这份实现刻意不用PyTorch，作为独立数值对照。不会训练或下载模型。

<span id="reference_inference-L3"></span>
运行: python reference_inference.py

<span id="reference_inference-L4"></span>
"""

<span id="reference_inference-L5"></span>
from __future__ import annotations

<span id="reference_inference-L6"></span>
import json, math

<span id="reference_inference-L7"></span>
from pathlib import Path

<span id="reference_inference-L8"></span>
 

<span id="reference_inference-L9"></span>
def matmul(a,b):

<span id="reference_inference-L10"></span>
    if not a or not b or len(a[0])!=len(b): raise ValueError('矩阵乘内侧尺寸不匹配')

<span id="reference_inference-L11"></span>
    return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]

<span id="reference_inference-L12"></span>
 

<span id="reference_inference-L13"></span>
def trans(a):return [list(col) for col in zip(*a)]

<span id="reference_inference-L14"></span>
def add(a,b):return [[x+y for x,y in zip(ra,rb)] for ra,rb in zip(a,b)]

<span id="reference_inference-L15"></span>
def norm(a,g,eps=1e-5):

<span id="reference_inference-L16"></span>
    out=[]

<span id="reference_inference-L17"></span>
    for row in a:

<span id="reference_inference-L18"></span>
        r=math.sqrt(sum(x*x for x in row)/len(row)+eps)

<span id="reference_inference-L19"></span>
        out.append([x/r*v for x,v in zip(row,g)])

<span id="reference_inference-L20"></span>
    return out

<span id="reference_inference-L21"></span>
 

<span id="reference_inference-L22"></span>
def softmax(row):

<span id="reference_inference-L23"></span>
    m=max(row)

<span id="reference_inference-L24"></span>
    if not math.isfinite(m):raise ValueError('这一行没有有限的可见分数')

<span id="reference_inference-L25"></span>
    es=[math.exp(x-m) for x in row];s=sum(es)

<span id="reference_inference-L26"></span>
    return [x/s for x in es]

<span id="reference_inference-L27"></span>
 

<span id="reference_inference-L28"></span>
def forward(ids,p):

<span id="reference_inference-L29"></span>
    if not ids or len(ids)>8:raise ValueError('只支持1..8个位置')

<span id="reference_inference-L30"></span>
    x=add([p['E'][i] for i in ids],[p['P'][i] for i in range(len(ids))])

<span id="reference_inference-L31"></span>
    n=norm(x,p['g1']);q=matmul(n,p['Wq']);k=matmul(n,p['Wk']);v=matmul(n,p['Wv'])

<span id="reference_inference-L32"></span>
    scores=matmul(q,trans(k))

<span id="reference_inference-L33"></span>
    probs=[softmax([z/2 if j<=i else -math.inf for j,z in enumerate(row)]) for i,row in enumerate(scores)]

<span id="reference_inference-L34"></span>
    r=add(x,matmul(matmul(probs,v),p['Wo']))

<span id="reference_inference-L35"></span>
    ff=matmul(norm(r,p['g2']),p['W1']);ff=[[max(0,x) for x in row] for row in ff]

<span id="reference_inference-L36"></span>
    h=add(r,matmul(ff,p['W2']))

<span id="reference_inference-L37"></span>
    return matmul(norm(h,p['gf']),p['U'])

<span id="reference_inference-L38"></span>
 

<span id="reference_inference-L39"></span>
def generate(ids,p,limit=5):

<span id="reference_inference-L40"></span>
    ids=list(ids);history=[]

<span id="reference_inference-L41"></span>
    for _ in range(limit):

<span id="reference_inference-L42"></span>
        z=forward(ids,p)[-1];prob=softmax(z);chosen=max(range(8),key=lambda i:z[i])

<span id="reference_inference-L43"></span>
        history.append(dict(input=list(ids),logits=z,probabilities=prob,selected=chosen))

<span id="reference_inference-L44"></span>
        ids.append(chosen)

<span id="reference_inference-L45"></span>
        if chosen==7:break

<span id="reference_inference-L46"></span>
    return ids,history

<span id="reference_inference-L47"></span>
 

<span id="reference_inference-L48"></span>
if __name__=='__main__':

<span id="reference_inference-L49"></span>
    d=Path(__file__).resolve().parent.parent/'data'

<span id="reference_inference-L50"></span>
    p=json.loads((d/'weights_trained.json').read_text())['parameters']

<span id="reference_inference-L51"></span>
    tokens,history=generate([6,1,2],p)

<span id="reference_inference-L52"></span>
    actual=json.loads((d/'run.json').read_text())

<span id="reference_inference-L53"></span>
    errors=[max(abs(x-y) for x,y in zip(a['logits'],b['logits'])) for a,b in zip(history,actual['generation']['steps'])]

<span id="reference_inference-L54"></span>
    assert tokens==[6,1,2,3,5,7]

<span id="reference_inference-L55"></span>
    assert max(errors)<1e-10

<span id="reference_inference-L56"></span>
    result=dict(tokens=tokens,max_error=max(errors),device='Python math on CPU; no tensor library')

<span id="reference_inference-L57"></span>
    (d/'reference_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))

<span id="reference_inference-L58"></span>
    print(json.dumps(result,ensure_ascii=False,indent=2))
```


<span id="test_model"></span>


## lab/test\_model.py

[原文件：labs/model/lab/test\_model.py](../../labs/model/lab/test_model.py)

```

<span id="test_model-L1"></span>
"""数值、因果性、训练/推理边界和常见错误的独立断言。"""

<span id="test_model-L2"></span>
from __future__ import annotations

<span id="test_model-L3"></span>
import copy,json,math,unittest,io,platform

<span id="test_model-L4"></span>
from pathlib import Path

<span id="test_model-L5"></span>
import torch

<span id="test_model-L6"></span>
from torch import nn

<span id="test_model-L7"></span>
from torch.nn import functional as F

<span id="test_model-L8"></span>
from tiny_model import TinyLM,training_loss,manual_backward,SEQUENCES,fingerprint,generate

<span id="test_model-L9"></span>
from reference_inference import forward as py_forward,softmax as py_softmax

<span id="test_model-L10"></span>
D=Path(__file__).resolve().parent.parent/'data'

<span id="test_model-L11"></span>
R=json.loads((D/'run.json').read_text())

<span id="test_model-L12"></span>
torch.set_num_threads(1)

<span id="test_model-L13"></span>
DT=torch.float64

<span id="test_model-L14"></span>
 

<span id="test_model-L15"></span>
def loaded():

<span id="test_model-L16"></span>
    m=TinyLM();m.load_state_dict({k:torch.tensor(v,dtype=DT) for k,v in R['trained_parameters'].items()});return m

<span id="test_model-L17"></span>
 

<span id="test_model-L18"></span>
class Arithmetic(unittest.TestCase):

<span id="test_model-L19"></span>
    def test_matmul_value(self):

<span id="test_model-L20"></span>
        self.assertEqual((torch.tensor([[1.,2.,3.],[4.,5.,6.]])@torch.tensor([[1.,0.],[0.,1.],[1.,1.]])).tolist(),[[4.,5.],[10.,11.]])

<span id="test_model-L21"></span>
    def test_softmax_shift(self):

<span id="test_model-L22"></span>
        a=torch.tensor([2.,1.,0.],dtype=DT);self.assertTrue(torch.allclose(a.softmax(-1),(a-2).softmax(-1)))

<span id="test_model-L23"></span>
    def test_softmax_not_divide_logits(self):

<span id="test_model-L24"></span>
        a=torch.tensor([2.,1.,0.],dtype=DT);self.assertGreater(float((a.softmax(-1)-a/a.sum()).abs().max()),.05)

<span id="test_model-L25"></span>
    def test_probability_sum(self):

<span id="test_model-L26"></span>
        self.assertAlmostEqual(sum(py_softmax([2,1,0])),1,places=14)

<span id="test_model-L27"></span>
    def test_logsumexp_ce(self):

<span id="test_model-L28"></span>
        z=torch.tensor([[2.,1.,0.]],dtype=DT);y=torch.tensor([1]);self.assertAlmostEqual(float(F.cross_entropy(z,y)),float(z.logsumexp(-1)-z[0,1]),places=14)

<span id="test_model-L29"></span>
    def test_ce_gradient(self):

<span id="test_model-L30"></span>
        z=torch.tensor([[2.,1.,0.]],dtype=DT,requires_grad=True);F.cross_entropy(z,torch.tensor([1])).backward();expected=z.detach().softmax(-1)-torch.tensor([[0.,1.,0.]],dtype=DT);self.assertTrue(torch.allclose(z.grad,expected))

<span id="test_model-L31"></span>
    def test_double_softmax_wrong(self):

<span id="test_model-L32"></span>
        z=torch.tensor([[2.,1.,0.]],dtype=DT);y=torch.tensor([1]);self.assertGreater(abs(float(F.cross_entropy(z,y)-F.cross_entropy(z.softmax(-1),y))),.1)

<span id="test_model-L33"></span>
    def test_ln_rms_different(self):

<span id="test_model-L34"></span>
        x=torch.tensor([1.,3.],dtype=DT);a=F.layer_norm(x,(2,),eps=1e-5);b=x/torch.sqrt(x.square().mean()+1e-5);self.assertLess(float(a[0]),0);self.assertGreater(float(b[0]),0)

<span id="test_model-L35"></span>
    def test_adam_steps(self):

<span id="test_model-L36"></span>
        for rec in R['adam_steps']:

<span id="test_model-L37"></span>
            t=rec['step'];g=rec['gradient'];m=.9*rec['m_before']+.1*g;v=.999*rec['v_before']+.001*g*g

<span id="test_model-L38"></span>
            w=rec['weight_before']*(1-.03*.01)-.03*(m/(1-.9**t))/(math.sqrt(v/(1-.999**t))+1e-8)

<span id="test_model-L39"></span>
            self.assertAlmostEqual(w,rec['weight_after'],places=13)

<span id="test_model-L40"></span>
    def test_training_lower_bound(self):

<span id="test_model-L41"></span>
        self.assertGreaterEqual(R['final_loss'],math.log(2)/5)

<span id="test_model-L42"></span>
        self.assertLess(R['final_loss'],.15)

<span id="test_model-L43"></span>
    def test_quantization(self):

<span id="test_model-L44"></span>
        x=.26;q=round(x/.1);self.assertEqual(q,3);self.assertAlmostEqual(q*.1-x,.04)

<span id="test_model-L45"></span>
    def test_lora_rank(self):

<span id="test_model-L46"></span>
        a=torch.tensor([[1.],[2.]],dtype=DT);b=torch.tensor([[1.,2.,3.]],dtype=DT);self.assertEqual((a@b).tolist(),[[1.,2.,3.],[2.,4.,6.]])

<span id="test_model-L47"></span>
    def test_speculative_identity(self):

<span id="test_model-L48"></span>
        p=[.6,.3,.1];q=[.2,.5,.3];accepted=[min(a,b) for a,b in zip(p,q)];rem=[max(a-b,0) for a,b in zip(p,q)];self.assertTrue(all(abs(a+b-c)<1e-15 for a,b,c in zip(accepted,rem,p)))

<span id="test_model-L49"></span>
    def test_online_softmax(self):

<span id="test_model-L50"></span>
        s=[2.,1.,0.];v=[10.,20.,30.];m=-math.inf;l=0;u=0

<span id="test_model-L51"></span>
        for block in [[0,1],[2]]:

<span id="test_model-L52"></span>
            nm=max([m]+[s[i] for i in block]);a=0 if m==-math.inf else math.exp(m-nm)

<span id="test_model-L53"></span>
            l=a*l+sum(math.exp(s[i]-nm) for i in block);u=a*u+sum(math.exp(s[i]-nm)*v[i] for i in block);m=nm

<span id="test_model-L54"></span>
        self.assertAlmostEqual(u/l,sum(a*b for a,b in zip(py_softmax(s),v)),places=13)

<span id="test_model-L55"></span>
    def test_rope_relative(self):

<span id="test_model-L56"></span>
        def rot(x,t):return [x[0]*math.cos(t)-x[1]*math.sin(t),x[0]*math.sin(t)+x[1]*math.cos(t)]

<span id="test_model-L57"></span>
        q=[1,2];k=[-.5,1]

<span id="test_model-L58"></span>
        dot=lambda a,b:sum(x*y for x,y in zip(a,b))

<span id="test_model-L59"></span>
        self.assertAlmostEqual(dot(rot(q,.3),rot(k,.7)),dot(q,rot(k,.4)),places=14)

<span id="test_model-L60"></span>
 

<span id="test_model-L61"></span>
class ForwardAndGradient(unittest.TestCase):

<span id="test_model-L62"></span>
    def setUp(self):self.m=TinyLM();self.x=SEQUENCES[:,:-1];self.y=SEQUENCES[:,1:]

<span id="test_model-L63"></span>
    def test_parameter_count(self):self.assertEqual(sum(p.numel() for p in self.m.parameters()),236)

<span id="test_model-L64"></span>
    def test_shapes(self):

<span id="test_model-L65"></span>
        z,_,t=self.m(self.x,return_trace=True);self.assertEqual(tuple(z.shape),(2,5,8));self.assertEqual(tuple(t['A'].shape),(2,5,5))

<span id="test_model-L66"></span>
    def test_rowsum(self):

<span id="test_model-L67"></span>
        _,_,t=self.m(self.x,return_trace=True);self.assertTrue(torch.allclose(t['A'].sum(-1),torch.ones(2,5,dtype=DT)))

<span id="test_model-L68"></span>
    def test_future_attention_zero(self):

<span id="test_model-L69"></span>
        _,_,t=self.m(self.x,return_trace=True);self.assertEqual(float(t['A'].triu(1).abs().sum()),0)

<span id="test_model-L70"></span>
    def test_future_input_no_effect(self):

<span id="test_model-L71"></span>
        x=self.x.clone();x[0,4]=4;a,_=self.m(self.x);b,_=self.m(x);self.assertTrue(torch.equal(a[0,:4],b[0,:4]))

<span id="test_model-L72"></span>
    def test_missing_causal_mask_detected(self):

<span id="test_model-L73"></span>
        x=self.x.clone();x[0,4]=4;a,_=self.m(self.x,causal=False);b,_=self.m(x,causal=False);self.assertGreater(float((a[0,:4]-b[0,:4]).abs().max()),1e-4)

<span id="test_model-L74"></span>
    def test_batch_matches_individual(self):

<span id="test_model-L75"></span>
        a,_=self.m(self.x);b,_=self.m(self.x[:1]);self.assertTrue(torch.allclose(a[:1],b,atol=1e-14,rtol=1e-14))

<span id="test_model-L76"></span>
    def test_batch_permutation(self):

<span id="test_model-L77"></span>
        a,_=self.m(self.x);b,_=self.m(self.x.flip(0));self.assertTrue(torch.allclose(a,b.flip(0),atol=1e-14,rtol=1e-14))

<span id="test_model-L78"></span>
    def test_entire_analytic_backward(self):

<span id="test_model-L79"></span>
        z,_,t=self.m(self.x,return_trace=True);g,b=manual_backward(self.m,t,self.y);l,_=training_loss(z,self.y);l.backward()

<span id="test_model-L80"></span>
        for k,p in self.m.named_parameters():self.assertTrue(torch.allclose(p.grad,g[k],atol=1e-12,rtol=1e-10),k)

<span id="test_model-L81"></span>
    def test_qkv_input_paths_add(self):

<span id="test_model-L82"></span>
        z,_,t=self.m(self.x,return_trace=True);g,b=manual_backward(self.m,t,self.y)

<span id="test_model-L83"></span>
        expected=b['dq']@self.m.Wq.T+b['dk']@self.m.Wk.T+b['dv']@self.m.Wv.T

<span id="test_model-L84"></span>
        self.assertTrue(torch.allclose(expected,b['dn1']))

<span id="test_model-L85"></span>
    def test_embedding_duplicate_rows_accumulate(self):

<span id="test_model-L86"></span>
        z,_,t=self.m(self.x,return_trace=True);g,b=manual_backward(self.m,t,self.y)

<span id="test_model-L87"></span>
        self.assertTrue(torch.allclose(g['E'][2],b['dx'][0,2]+b['dx'][1,2]))

<span id="test_model-L88"></span>
    def test_score_gradient_rowsum_zero(self):

<span id="test_model-L89"></span>
        z,_,t=self.m(self.x,return_trace=True);g,b=manual_backward(self.m,t,self.y);self.assertLess(float(b['ds'].sum(-1).abs().max()),1e-12)

<span id="test_model-L90"></span>
    def test_finite_difference_selected_coordinates(self):

<span id="test_model-L91"></span>
        z,_=self.m(self.x);l,_=training_loss(z,self.y);l.backward();eps=1e-6

<span id="test_model-L92"></span>
        for name,idx in [('Wq',(0,0)),('Wk',(2,1)),('Wv',(1,0)),('Wo',(2,3)),('W1',(0,3)),('W2',(2,1)),('U',(0,3)),('g1',(2,)),('g2',(2,)),('gf',(2,)),('E',(2,1)),('P',(2,1))]:

<span id="test_model-L93"></span>
            p=self.m.get_parameter(name);old=float(p[idx].detach());g=float(p.grad[idx]);vals=[]

<span id="test_model-L94"></span>
            with torch.no_grad():

<span id="test_model-L95"></span>
                for sign in [1,-1]:

<span id="test_model-L96"></span>
                    p[idx]=old+sign*eps;zz,_=self.m(self.x);ll,_=training_loss(zz,self.y);vals.append(float(ll))

<span id="test_model-L97"></span>
                p[idx]=old

<span id="test_model-L98"></span>
            self.assertAlmostEqual((vals[0]-vals[1])/(2*eps),g,places=7,msg=name)

<span id="test_model-L99"></span>
    def test_sgd_small_step(self):

<span id="test_model-L100"></span>
        z,_=self.m(self.x);l,_=training_loss(z,self.y);before=float(l.detach());l.backward()

<span id="test_model-L101"></span>
        with torch.no_grad():

<span id="test_model-L102"></span>
            for p in self.m.parameters():p-=.001*p.grad

<span id="test_model-L103"></span>
        after,_=training_loss(self.m(self.x)[0],self.y);self.assertLess(float(after),before)

<span id="test_model-L104"></span>
    def test_backward_not_update(self):

<span id="test_model-L105"></span>
        old=fingerprint(self.m);z,_=self.m(self.x);training_loss(z,self.y)[0].backward();self.assertEqual(fingerprint(self.m),old)

<span id="test_model-L106"></span>
    def test_grad_accumulation(self):

<span id="test_model-L107"></span>
        z,_=self.m(self.x);l,_=training_loss(z,self.y);l.backward();first=self.m.U.grad.clone()

<span id="test_model-L108"></span>
        z,_=self.m(self.x);training_loss(z,self.y)[0].backward();self.assertTrue(torch.allclose(self.m.U.grad,2*first))

<span id="test_model-L109"></span>
    def test_ignored_target_gradient(self):

<span id="test_model-L110"></span>
        z=torch.randn(1,3,8,dtype=DT,requires_grad=True);y=torch.tensor([[1,-100,2]]);training_loss(z,y)[0].backward();self.assertEqual(float(z.grad[0,1].abs().sum()),0)

<span id="test_model-L111"></span>
    def test_all_ignored_rejected(self):

<span id="test_model-L112"></span>
        with self.assertRaises(ValueError):training_loss(torch.zeros(1,2,8),torch.full((1,2),-100))

<span id="test_model-L113"></span>
    def test_target_alignment(self):

<span id="test_model-L114"></span>
        self.assertEqual(self.x[0].tolist(),[6,1,2,3,5]);self.assertEqual(self.y[0].tolist(),[1,2,3,5,7])

<span id="test_model-L115"></span>
    def test_no_double_shift(self):

<span id="test_model-L116"></span>
        z,_,t=self.m(self.x,return_trace=True);right,_=training_loss(z,self.y)

<span id="test_model-L117"></span>
        wrong,_=training_loss(z[:,:-1],self.y[:,1:]);self.assertGreater(abs(float(right-wrong)),1e-3)

<span id="test_model-L118"></span>
    def test_ce_without_prior_softmax(self):

<span id="test_model-L119"></span>
        z,_=self.m(self.x);right,_=training_loss(z,self.y);wrong,_=training_loss(z.softmax(-1),self.y);self.assertGreater(abs(float(right-wrong)),.01)

<span id="test_model-L120"></span>
    def test_right_padding_needs_final_valid(self):

<span id="test_model-L121"></span>
        x=torch.tensor([[6,1,2,0]]);mask=torch.tensor([[1,1,1,0]],dtype=torch.bool)

<span id="test_model-L122"></span>
        z,_=self.m(x,key_valid=mask);true,_=self.m(x[:,:3]);self.assertTrue(torch.allclose(z[:,2],true[:,-1]));self.assertGreater(float((z[:,3]-z[:,2]).abs().max()),1e-4)

<span id="test_model-L123"></span>
    def test_padding_key_invisible(self):

<span id="test_model-L124"></span>
        x=torch.tensor([[6,0,1,2]]);mask=torch.tensor([[1,0,1,1]],dtype=torch.bool);_,_,t=self.m(x,key_valid=mask,return_trace=True);self.assertEqual(float(t['A'][:,:,1].sum()),0)

<span id="test_model-L125"></span>
    def test_empty_input_rejected(self):

<span id="test_model-L126"></span>
        with self.assertRaises(ValueError):self.m(torch.empty(1,0,dtype=torch.long))

<span id="test_model-L127"></span>
    def test_all_masked_rejected(self):

<span id="test_model-L128"></span>
        with self.assertRaises(ValueError):self.m(self.x,key_valid=torch.zeros(2,5,dtype=torch.bool))

<span id="test_model-L129"></span>
 

<span id="test_model-L130"></span>
class InferenceAndInterfaces(unittest.TestCase):

<span id="test_model-L131"></span>
    def test_reload_hash(self):self.assertEqual(fingerprint(loaded()),R['trained_hash'])

<span id="test_model-L132"></span>
    def test_full_cache_outputs(self):

<span id="test_model-L133"></span>
        m=loaded();a=generate(m,[6,1,2],use_cache=True);b=generate(m,[6,1,2],use_cache=False)

<span id="test_model-L134"></span>
        self.assertEqual(a['tokens'],b['tokens'])

<span id="test_model-L135"></span>
        for x,y in zip(a['steps'],b['steps']):self.assertLess(max(abs(i-j) for i,j in zip(x['logits'],y['logits'])),1e-10)

<span id="test_model-L136"></span>
    def test_expected_tokens(self):self.assertEqual(generate(loaded(),[6,1,2])['tokens'],[6,1,2,3,5,7])

<span id="test_model-L137"></span>
    def test_no_parameter_change(self):

<span id="test_model-L138"></span>
        m=loaded();h=fingerprint(m);generate(m,[6,1,2]);self.assertEqual(fingerprint(m),h)

<span id="test_model-L139"></span>
    def test_cache_lag(self):

<span id="test_model-L140"></span>
        a=generate(loaded(),[6,1,2]);self.assertEqual([s['cache_after'] for s in a['steps']],[3,4,5]);self.assertEqual(len(a['tokens']),6)

<span id="test_model-L141"></span>
    def test_limit_not_eos(self):

<span id="test_model-L142"></span>
        a=generate(loaded(),[6,1,2],max_new=2);self.assertEqual(a['reason'],'length');self.assertNotEqual(a['tokens'][-1],7)

<span id="test_model-L143"></span>
    def test_two_new_tokens_cache(self):

<span id="test_model-L144"></span>
        m=loaded();x=SEQUENCES[:1,:-1];allz,_=m(x);_,c=m(x[:,:3]);part,_=m(x[:,3:],cache=c);self.assertTrue(torch.allclose(allz[:,3:],part,atol=1e-12))

<span id="test_model-L145"></span>
    def test_wrong_position_changes_output(self):

<span id="test_model-L146"></span>
        m=loaded();_,c=m(torch.tensor([[6,1,2]]));good,_=m(torch.tensor([[3]]),cache=c);bad,_=m(torch.tensor([[3]]),cache=c,position_ids=torch.zeros(1,1,dtype=torch.long));self.assertGreater(float((good-bad).abs().max()),.01)

<span id="test_model-L147"></span>
    def test_stale_cache_after_weights_change(self):

<span id="test_model-L148"></span>
        m=loaded();x=torch.tensor([[6,1,2,3]]);_,c=m(x[:,:3])

<span id="test_model-L149"></span>
        with torch.no_grad():m.Wv.mul_(.5)

<span id="test_model-L150"></span>
        stale,_=m(x[:,3:],cache=c);fresh,_=m(x);self.assertGreater(float((stale[:,-1]-fresh[:,-1]).abs().max()),1e-4)

<span id="test_model-L151"></span>
    def test_stdlib_reference(self):

<span id="test_model-L152"></span>
        z=py_forward([6,1,2],R['trained_parameters']);expected=R['generation']['steps'][0]['logits'];self.assertLess(max(abs(x-y) for x,y in zip(z[-1],expected)),1e-10)

<span id="test_model-L153"></span>
    def test_eval_does_not_disable_grad(self):

<span id="test_model-L154"></span>
        m=TinyLM().eval();z,_=m(SEQUENCES[:,:-1]);self.assertTrue(z.requires_grad)

<span id="test_model-L155"></span>
    def test_no_grad_does_not_switch_dropout(self):

<span id="test_model-L156"></span>
        d=nn.Dropout(.5).train();x=torch.ones(1000)

<span id="test_model-L157"></span>
        with torch.no_grad():y=d(x)

<span id="test_model-L158"></span>
        self.assertGreater(int(y.eq(0).sum()),0)

<span id="test_model-L159"></span>
    def test_eval_switches_dropout(self):

<span id="test_model-L160"></span>
        d=nn.Dropout(.5).eval();x=torch.ones(100);self.assertTrue(torch.equal(d(x),x))

<span id="test_model-L161"></span>
    def test_sdpa_non_square_alignment(self):

<span id="test_model-L162"></span>
        q=torch.ones(1,1,2,1,dtype=DT);k=torch.ones(1,1,5,1,dtype=DT);v=torch.arange(1,6,dtype=DT).reshape(1,1,5,1)

<span id="test_model-L163"></span>
        good=(torch.arange(5)[None,:]<=torch.tensor([3,4])[:,None])

<span id="test_model-L164"></span>
        a=F.scaled_dot_product_attention(q,k,v,attn_mask=good);b=F.scaled_dot_product_attention(q,k,v,is_causal=True)

<span id="test_model-L165"></span>
        self.assertEqual(a.flatten().tolist(),[2.5,3.]);self.assertEqual(b.flatten().tolist(),[1.,1.5])

<span id="test_model-L166"></span>
    def test_sdpa_scale_once(self):

<span id="test_model-L167"></span>
        q=torch.tensor([[[[1.,2.]]]],dtype=DT);k=torch.tensor([[[[1.,0.],[0.,1.]]]],dtype=DT);v=k

<span id="test_model-L168"></span>
        a=F.scaled_dot_product_attention(q,k,v);manual=(q@k.transpose(-1,-2)/math.sqrt(2)).softmax(-1)@v

<span id="test_model-L169"></span>
        self.assertTrue(torch.allclose(a,manual));b=F.scaled_dot_product_attention(q/math.sqrt(2),k,v);self.assertGreater(float((a-b).abs().max()),.01)

<span id="test_model-L170"></span>
    def test_linear_storage_transpose(self):

<span id="test_model-L171"></span>
        x=torch.tensor([[1.,2.]],dtype=DT);w=torch.tensor([[1.,3.],[2.,4.]],dtype=DT)

<span id="test_model-L172"></span>
        self.assertEqual((x@w).tolist(),[[5.,11.]]);self.assertEqual(F.linear(x,w).tolist(),[[7.,10.]])

<span id="test_model-L173"></span>
    def test_training_loss_drops(self):self.assertLess(R['final_loss'],R['initial_loss']/10)

<span id="test_model-L174"></span>
 

<span id="test_model-L175"></span>
if __name__=='__main__':

<span id="test_model-L176"></span>
    suite=unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))

<span id="test_model-L177"></span>
    stream=io.StringIO();res=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)

<span id="test_model-L178"></span>
    log=stream.getvalue();print(log)

<span id="test_model-L179"></span>
    (D/'tests.log').write_text(log)

<span id="test_model-L180"></span>
    (D/'tests.json').write_text(json.dumps(dict(run=res.testsRun,failures=len(res.failures),errors=len(res.errors),skipped=len(res.skipped),python=platform.python_version(),torch=torch.__version__,device='cpu'),indent=2))

<span id="test_model-L181"></span>
    if not res.wasSuccessful():raise SystemExit(1)
```


<span id="weights_initial"></span>


## data/weights\_initial.json

[原文件：labs/model/data/weights\_initial.json](../../labs/model/data/weights_initial.json)

```

<span id="weights_initial-L1"></span>
{

<span id="weights_initial-L2"></span>
  "spec": {

<span id="weights_initial-L3"></span>
    "vocab": [

<span id="weights_initial-L4"></span>
      "PAD",

<span id="weights_initial-L5"></span>
      "我",

<span id="weights_initial-L6"></span>
      "爱",

<span id="weights_initial-L7"></span>
      "学习",

<span id="weights_initial-L8"></span>
      "你",

<span id="weights_initial-L9"></span>
      "！",

<span id="weights_initial-L10"></span>
      "BOS",

<span id="weights_initial-L11"></span>
      "EOS"

<span id="weights_initial-L12"></span>
    ],

<span id="weights_initial-L13"></span>
    "vocab_size": 8,

<span id="weights_initial-L14"></span>
    "width": 4,

<span id="weights_initial-L15"></span>
    "ffn_width": 8,

<span id="weights_initial-L16"></span>
    "layers": 1,

<span id="weights_initial-L17"></span>
    "heads": 1,

<span id="weights_initial-L18"></span>
    "context": 8,

<span id="weights_initial-L19"></span>
    "norm": "RMSNorm",

<span id="weights_initial-L20"></span>
    "eps": 1e-05,

<span id="weights_initial-L21"></span>
    "position": "learned absolute position",

<span id="weights_initial-L22"></span>
    "activation": "ReLU",

<span id="weights_initial-L23"></span>
    "bias": false,

<span id="weights_initial-L24"></span>
    "dropout": 0.0,

<span id="weights_initial-L25"></span>
    "tied_embeddings": false,

<span id="weights_initial-L26"></span>
    "dtype": "float64",

<span id="weights_initial-L27"></span>
    "seed": 23

<span id="weights_initial-L28"></span>
  },

<span id="weights_initial-L29"></span>
  "parameters": {

<span id="weights_initial-L30"></span>
    "E": [

<span id="weights_initial-L31"></span>
      [

<span id="weights_initial-L32"></span>
        0.0,

<span id="weights_initial-L33"></span>
        0.0,

<span id="weights_initial-L34"></span>
        0.0,

<span id="weights_initial-L35"></span>
        0.0

<span id="weights_initial-L36"></span>
      ],

<span id="weights_initial-L37"></span>
      [

<span id="weights_initial-L38"></span>
        0.2,

<span id="weights_initial-L39"></span>
        -0.1,

<span id="weights_initial-L40"></span>
        0.7,

<span id="weights_initial-L41"></span>
        0.4

<span id="weights_initial-L42"></span>
      ],

<span id="weights_initial-L43"></span>
      [

<span id="weights_initial-L44"></span>
        -0.3,

<span id="weights_initial-L45"></span>
        0.8,

<span id="weights_initial-L46"></span>
        0.1,

<span id="weights_initial-L47"></span>
        0.5

<span id="weights_initial-L48"></span>
      ],

<span id="weights_initial-L49"></span>
      [

<span id="weights_initial-L50"></span>
        0.6,

<span id="weights_initial-L51"></span>
        0.2,

<span id="weights_initial-L52"></span>
        -0.4,

<span id="weights_initial-L53"></span>
        0.9

<span id="weights_initial-L54"></span>
      ],

<span id="weights_initial-L55"></span>
      [

<span id="weights_initial-L56"></span>
        0.1,

<span id="weights_initial-L57"></span>
        -0.5,

<span id="weights_initial-L58"></span>
        0.9,

<span id="weights_initial-L59"></span>
        0.3

<span id="weights_initial-L60"></span>
      ],

<span id="weights_initial-L61"></span>
      [

<span id="weights_initial-L62"></span>
        -0.2,

<span id="weights_initial-L63"></span>
        0.4,

<span id="weights_initial-L64"></span>
        0.5,

<span id="weights_initial-L65"></span>
        -0.6

<span id="weights_initial-L66"></span>
      ],

<span id="weights_initial-L67"></span>
      [

<span id="weights_initial-L68"></span>
        0.4,

<span id="weights_initial-L69"></span>
        -0.2,

<span id="weights_initial-L70"></span>
        0.3,

<span id="weights_initial-L71"></span>
        0.1

<span id="weights_initial-L72"></span>
      ],

<span id="weights_initial-L73"></span>
      [

<span id="weights_initial-L74"></span>
        0.1,

<span id="weights_initial-L75"></span>
        0.2,

<span id="weights_initial-L76"></span>
        -0.3,

<span id="weights_initial-L77"></span>
        0.4

<span id="weights_initial-L78"></span>
      ]

<span id="weights_initial-L79"></span>
    ],

<span id="weights_initial-L80"></span>
    "P": [

<span id="weights_initial-L81"></span>
      [

<span id="weights_initial-L82"></span>
        -0.05,

<span id="weights_initial-L83"></span>
        -0.05,

<span id="weights_initial-L84"></span>
        -0.05,

<span id="weights_initial-L85"></span>
        0.0

<span id="weights_initial-L86"></span>
      ],

<span id="weights_initial-L87"></span>
      [

<span id="weights_initial-L88"></span>
        -0.1,

<span id="weights_initial-L89"></span>
        0.0,

<span id="weights_initial-L90"></span>
        0.0,

<span id="weights_initial-L91"></span>
        -0.05

<span id="weights_initial-L92"></span>
      ],

<span id="weights_initial-L93"></span>
      [

<span id="weights_initial-L94"></span>
        0.1,

<span id="weights_initial-L95"></span>
        0.0,

<span id="weights_initial-L96"></span>
        -0.1,

<span id="weights_initial-L97"></span>
        -0.05

<span id="weights_initial-L98"></span>
      ],

<span id="weights_initial-L99"></span>
      [

<span id="weights_initial-L100"></span>
        0.05,

<span id="weights_initial-L101"></span>
        0.0,

<span id="weights_initial-L102"></span>
        0.05,

<span id="weights_initial-L103"></span>
        0.0

<span id="weights_initial-L104"></span>
      ],

<span id="weights_initial-L105"></span>
      [

<span id="weights_initial-L106"></span>
        -0.1,

<span id="weights_initial-L107"></span>
        0.0,

<span id="weights_initial-L108"></span>
        0.1,

<span id="weights_initial-L109"></span>
        0.05

<span id="weights_initial-L110"></span>
      ],

<span id="weights_initial-L111"></span>
      [

<span id="weights_initial-L112"></span>
        -0.05,

<span id="weights_initial-L113"></span>
        0.1,

<span id="weights_initial-L114"></span>
        -0.1,

<span id="weights_initial-L115"></span>
        -0.1

<span id="weights_initial-L116"></span>
      ],

<span id="weights_initial-L117"></span>
      [

<span id="weights_initial-L118"></span>
        0.05,

<span id="weights_initial-L119"></span>
        -0.1,

<span id="weights_initial-L120"></span>
        -0.05,

<span id="weights_initial-L121"></span>
        -0.05

<span id="weights_initial-L122"></span>
      ],

<span id="weights_initial-L123"></span>
      [

<span id="weights_initial-L124"></span>
        -0.05,

<span id="weights_initial-L125"></span>
        0.0,

<span id="weights_initial-L126"></span>
        0.1,

<span id="weights_initial-L127"></span>
        0.05

<span id="weights_initial-L128"></span>
      ]

<span id="weights_initial-L129"></span>
    ],

<span id="weights_initial-L130"></span>
    "Wq": [

<span id="weights_initial-L131"></span>
      [

<span id="weights_initial-L132"></span>
        0.2,

<span id="weights_initial-L133"></span>
        -0.2,

<span id="weights_initial-L134"></span>
        -0.1,

<span id="weights_initial-L135"></span>
        -0.1

<span id="weights_initial-L136"></span>
      ],

<span id="weights_initial-L137"></span>
      [

<span id="weights_initial-L138"></span>
        0.1,

<span id="weights_initial-L139"></span>
        0.1,

<span id="weights_initial-L140"></span>
        -0.30000000000000004,

<span id="weights_initial-L141"></span>
        -0.2

<span id="weights_initial-L142"></span>
      ],

<span id="weights_initial-L143"></span>
      [

<span id="weights_initial-L144"></span>
        -0.2,

<span id="weights_initial-L145"></span>
        0.1,

<span id="weights_initial-L146"></span>
        0.2,

<span id="weights_initial-L147"></span>
        -0.2

<span id="weights_initial-L148"></span>
      ],

<span id="weights_initial-L149"></span>
      [

<span id="weights_initial-L150"></span>
        -0.2,

<span id="weights_initial-L151"></span>
        -0.1,

<span id="weights_initial-L152"></span>
        -0.2,

<span id="weights_initial-L153"></span>
        -0.1

<span id="weights_initial-L154"></span>
      ]

<span id="weights_initial-L155"></span>
    ],

<span id="weights_initial-L156"></span>
    "Wk": [

<span id="weights_initial-L157"></span>
      [

<span id="weights_initial-L158"></span>
        -0.30000000000000004,

<span id="weights_initial-L159"></span>
        -0.1,

<span id="weights_initial-L160"></span>
        -0.1,

<span id="weights_initial-L161"></span>
        -0.2

<span id="weights_initial-L162"></span>
      ],

<span id="weights_initial-L163"></span>
      [

<span id="weights_initial-L164"></span>
        0.30000000000000004,

<span id="weights_initial-L165"></span>
        0.2,

<span id="weights_initial-L166"></span>
        0.0,

<span id="weights_initial-L167"></span>
        0.2

<span id="weights_initial-L168"></span>
      ],

<span id="weights_initial-L169"></span>
      [

<span id="weights_initial-L170"></span>
        0.1,

<span id="weights_initial-L171"></span>
        -0.2,

<span id="weights_initial-L172"></span>
        0.2,

<span id="weights_initial-L173"></span>
        0.2

<span id="weights_initial-L174"></span>
      ],

<span id="weights_initial-L175"></span>
      [

<span id="weights_initial-L176"></span>
        0.2,

<span id="weights_initial-L177"></span>
        0.2,

<span id="weights_initial-L178"></span>
        0.30000000000000004,

<span id="weights_initial-L179"></span>
        -0.30000000000000004

<span id="weights_initial-L180"></span>
      ]

<span id="weights_initial-L181"></span>
    ],

<span id="weights_initial-L182"></span>
    "Wv": [

<span id="weights_initial-L183"></span>
      [

<span id="weights_initial-L184"></span>
        -0.30000000000000004,

<span id="weights_initial-L185"></span>
        0.0,

<span id="weights_initial-L186"></span>
        -0.1,

<span id="weights_initial-L187"></span>
        -0.30000000000000004

<span id="weights_initial-L188"></span>
      ],

<span id="weights_initial-L189"></span>
      [

<span id="weights_initial-L190"></span>
        0.30000000000000004,

<span id="weights_initial-L191"></span>
        0.30000000000000004,

<span id="weights_initial-L192"></span>
        -0.1,

<span id="weights_initial-L193"></span>
        0.1

<span id="weights_initial-L194"></span>
      ],

<span id="weights_initial-L195"></span>
      [

<span id="weights_initial-L196"></span>
        -0.30000000000000004,

<span id="weights_initial-L197"></span>
        0.1,

<span id="weights_initial-L198"></span>
        0.1,

<span id="weights_initial-L199"></span>
        -0.30000000000000004

<span id="weights_initial-L200"></span>
      ],

<span id="weights_initial-L201"></span>
      [

<span id="weights_initial-L202"></span>
        -0.1,

<span id="weights_initial-L203"></span>
        0.30000000000000004,

<span id="weights_initial-L204"></span>
        -0.30000000000000004,

<span id="weights_initial-L205"></span>
        0.0

<span id="weights_initial-L206"></span>
      ]

<span id="weights_initial-L207"></span>
    ],

<span id="weights_initial-L208"></span>
    "Wo": [

<span id="weights_initial-L209"></span>
      [

<span id="weights_initial-L210"></span>
        0.30000000000000004,

<span id="weights_initial-L211"></span>
        0.1,

<span id="weights_initial-L212"></span>
        -0.2,

<span id="weights_initial-L213"></span>
        0.30000000000000004

<span id="weights_initial-L214"></span>
      ],

<span id="weights_initial-L215"></span>
      [

<span id="weights_initial-L216"></span>
        -0.30000000000000004,

<span id="weights_initial-L217"></span>
        -0.1,

<span id="weights_initial-L218"></span>
        -0.1,

<span id="weights_initial-L219"></span>
        0.30000000000000004

<span id="weights_initial-L220"></span>
      ],

<span id="weights_initial-L221"></span>
      [

<span id="weights_initial-L222"></span>
        0.30000000000000004,

<span id="weights_initial-L223"></span>
        0.30000000000000004,

<span id="weights_initial-L224"></span>
        -0.1,

<span id="weights_initial-L225"></span>
        -0.30000000000000004

<span id="weights_initial-L226"></span>
      ],

<span id="weights_initial-L227"></span>
      [

<span id="weights_initial-L228"></span>
        -0.2,

<span id="weights_initial-L229"></span>
        0.0,

<span id="weights_initial-L230"></span>
        0.30000000000000004,

<span id="weights_initial-L231"></span>
        0.1

<span id="weights_initial-L232"></span>
      ]

<span id="weights_initial-L233"></span>
    ],

<span id="weights_initial-L234"></span>
    "W1": [

<span id="weights_initial-L235"></span>
      [

<span id="weights_initial-L236"></span>
        0.2,

<span id="weights_initial-L237"></span>
        -0.1,

<span id="weights_initial-L238"></span>
        -0.1,

<span id="weights_initial-L239"></span>
        0.2,

<span id="weights_initial-L240"></span>
        -0.2,

<span id="weights_initial-L241"></span>
        -0.30000000000000004,

<span id="weights_initial-L242"></span>
        0.30000000000000004,

<span id="weights_initial-L243"></span>
        0.1

<span id="weights_initial-L244"></span>
      ],

<span id="weights_initial-L245"></span>
      [

<span id="weights_initial-L246"></span>
        -0.1,

<span id="weights_initial-L247"></span>
        0.0,

<span id="weights_initial-L248"></span>
        0.30000000000000004,

<span id="weights_initial-L249"></span>
        0.30000000000000004,

<span id="weights_initial-L250"></span>
        -0.30000000000000004,

<span id="weights_initial-L251"></span>
        -0.2,

<span id="weights_initial-L252"></span>
        -0.30000000000000004,

<span id="weights_initial-L253"></span>
        -0.30000000000000004

<span id="weights_initial-L254"></span>
      ],

<span id="weights_initial-L255"></span>
      [

<span id="weights_initial-L256"></span>
        0.1,

<span id="weights_initial-L257"></span>
        0.2,

<span id="weights_initial-L258"></span>
        -0.2,

<span id="weights_initial-L259"></span>
        0.0,

<span id="weights_initial-L260"></span>
        0.0,

<span id="weights_initial-L261"></span>
        0.0,

<span id="weights_initial-L262"></span>
        -0.30000000000000004,

<span id="weights_initial-L263"></span>
        -0.30000000000000004

<span id="weights_initial-L264"></span>
      ],

<span id="weights_initial-L265"></span>
      [

<span id="weights_initial-L266"></span>
        0.2,

<span id="weights_initial-L267"></span>
        -0.1,

<span id="weights_initial-L268"></span>
        0.30000000000000004,

<span id="weights_initial-L269"></span>
        -0.1,

<span id="weights_initial-L270"></span>
        -0.2,

<span id="weights_initial-L271"></span>
        0.0,

<span id="weights_initial-L272"></span>
        0.1,

<span id="weights_initial-L273"></span>
        -0.2

<span id="weights_initial-L274"></span>
      ]

<span id="weights_initial-L275"></span>
    ],

<span id="weights_initial-L276"></span>
    "W2": [

<span id="weights_initial-L277"></span>
      [

<span id="weights_initial-L278"></span>
        -0.30000000000000004,

<span id="weights_initial-L279"></span>
        -0.30000000000000004,

<span id="weights_initial-L280"></span>
        -0.30000000000000004,

<span id="weights_initial-L281"></span>
        0.0

<span id="weights_initial-L282"></span>
      ],

<span id="weights_initial-L283"></span>
      [

<span id="weights_initial-L284"></span>
        0.1,

<span id="weights_initial-L285"></span>
        0.1,

<span id="weights_initial-L286"></span>
        0.0,

<span id="weights_initial-L287"></span>
        0.30000000000000004

<span id="weights_initial-L288"></span>
      ],

<span id="weights_initial-L289"></span>
      [

<span id="weights_initial-L290"></span>
        0.30000000000000004,

<span id="weights_initial-L291"></span>
        0.1,

<span id="weights_initial-L292"></span>
        -0.2,

<span id="weights_initial-L293"></span>
        0.30000000000000004

<span id="weights_initial-L294"></span>
      ],

<span id="weights_initial-L295"></span>
      [

<span id="weights_initial-L296"></span>
        0.1,

<span id="weights_initial-L297"></span>
        -0.2,

<span id="weights_initial-L298"></span>
        -0.30000000000000004,

<span id="weights_initial-L299"></span>
        0.2

<span id="weights_initial-L300"></span>
      ],

<span id="weights_initial-L301"></span>
      [

<span id="weights_initial-L302"></span>
        -0.2,

<span id="weights_initial-L303"></span>
        0.1,

<span id="weights_initial-L304"></span>
        -0.1,

<span id="weights_initial-L305"></span>
        0.1

<span id="weights_initial-L306"></span>
      ],

<span id="weights_initial-L307"></span>
      [

<span id="weights_initial-L308"></span>
        0.0,

<span id="weights_initial-L309"></span>
        0.2,

<span id="weights_initial-L310"></span>
        0.1,

<span id="weights_initial-L311"></span>
        -0.1

<span id="weights_initial-L312"></span>
      ],

<span id="weights_initial-L313"></span>
      [

<span id="weights_initial-L314"></span>
        -0.2,

<span id="weights_initial-L315"></span>
        0.2,

<span id="weights_initial-L316"></span>
        -0.1,

<span id="weights_initial-L317"></span>
        0.1

<span id="weights_initial-L318"></span>
      ],

<span id="weights_initial-L319"></span>
      [

<span id="weights_initial-L320"></span>
        -0.30000000000000004,

<span id="weights_initial-L321"></span>
        0.1,

<span id="weights_initial-L322"></span>
        0.2,

<span id="weights_initial-L323"></span>
        0.0

<span id="weights_initial-L324"></span>
      ]

<span id="weights_initial-L325"></span>
    ],

<span id="weights_initial-L326"></span>
    "U": [

<span id="weights_initial-L327"></span>
      [

<span id="weights_initial-L328"></span>
        0.1,

<span id="weights_initial-L329"></span>
        0.0,

<span id="weights_initial-L330"></span>
        0.30000000000000004,

<span id="weights_initial-L331"></span>
        0.1,

<span id="weights_initial-L332"></span>
        -0.2,

<span id="weights_initial-L333"></span>
        -0.2,

<span id="weights_initial-L334"></span>
        -0.30000000000000004,

<span id="weights_initial-L335"></span>
        0.30000000000000004

<span id="weights_initial-L336"></span>
      ],

<span id="weights_initial-L337"></span>
      [

<span id="weights_initial-L338"></span>
        0.1,

<span id="weights_initial-L339"></span>
        -0.2,

<span id="weights_initial-L340"></span>
        0.1,

<span id="weights_initial-L341"></span>
        0.30000000000000004,

<span id="weights_initial-L342"></span>
        0.30000000000000004,

<span id="weights_initial-L343"></span>
        -0.30000000000000004,

<span id="weights_initial-L344"></span>
        -0.1,

<span id="weights_initial-L345"></span>
        0.1

<span id="weights_initial-L346"></span>
      ],

<span id="weights_initial-L347"></span>
      [

<span id="weights_initial-L348"></span>
        -0.1,

<span id="weights_initial-L349"></span>
        -0.30000000000000004,

<span id="weights_initial-L350"></span>
        0.2,

<span id="weights_initial-L351"></span>
        -0.30000000000000004,

<span id="weights_initial-L352"></span>
        0.30000000000000004,

<span id="weights_initial-L353"></span>
        -0.1,

<span id="weights_initial-L354"></span>
        0.2,

<span id="weights_initial-L355"></span>
        -0.30000000000000004

<span id="weights_initial-L356"></span>
      ],

<span id="weights_initial-L357"></span>
      [

<span id="weights_initial-L358"></span>
        0.0,

<span id="weights_initial-L359"></span>
        -0.1,

<span id="weights_initial-L360"></span>
        -0.2,

<span id="weights_initial-L361"></span>
        0.1,

<span id="weights_initial-L362"></span>
        0.1,

<span id="weights_initial-L363"></span>
        -0.30000000000000004,

<span id="weights_initial-L364"></span>
        0.30000000000000004,

<span id="weights_initial-L365"></span>
        0.1

<span id="weights_initial-L366"></span>
      ]

<span id="weights_initial-L367"></span>
    ],

<span id="weights_initial-L368"></span>
    "g1": [

<span id="weights_initial-L369"></span>
      1.0,

<span id="weights_initial-L370"></span>
      1.0,

<span id="weights_initial-L371"></span>
      1.0,

<span id="weights_initial-L372"></span>
      1.0

<span id="weights_initial-L373"></span>
    ],

<span id="weights_initial-L374"></span>
    "g2": [

<span id="weights_initial-L375"></span>
      1.0,

<span id="weights_initial-L376"></span>
      1.0,

<span id="weights_initial-L377"></span>
      1.0,

<span id="weights_initial-L378"></span>
      1.0

<span id="weights_initial-L379"></span>
    ],

<span id="weights_initial-L380"></span>
    "gf": [

<span id="weights_initial-L381"></span>
      1.0,

<span id="weights_initial-L382"></span>
      1.0,

<span id="weights_initial-L383"></span>
      1.0,

<span id="weights_initial-L384"></span>
      1.0

<span id="weights_initial-L385"></span>
    ]

<span id="weights_initial-L386"></span>
  }

<span id="weights_initial-L387"></span>
}
```


<span id="weights_trained"></span>


## data/weights\_trained.json

[原文件：labs/model/data/weights\_trained.json](../../labs/model/data/weights_trained.json)

```

<span id="weights_trained-L1"></span>
{

<span id="weights_trained-L2"></span>
  "spec": {

<span id="weights_trained-L3"></span>
    "vocab": [

<span id="weights_trained-L4"></span>
      "PAD",

<span id="weights_trained-L5"></span>
      "我",

<span id="weights_trained-L6"></span>
      "爱",

<span id="weights_trained-L7"></span>
      "学习",

<span id="weights_trained-L8"></span>
      "你",

<span id="weights_trained-L9"></span>
      "！",

<span id="weights_trained-L10"></span>
      "BOS",

<span id="weights_trained-L11"></span>
      "EOS"

<span id="weights_trained-L12"></span>
    ],

<span id="weights_trained-L13"></span>
    "vocab_size": 8,

<span id="weights_trained-L14"></span>
    "width": 4,

<span id="weights_trained-L15"></span>
    "ffn_width": 8,

<span id="weights_trained-L16"></span>
    "layers": 1,

<span id="weights_trained-L17"></span>
    "heads": 1,

<span id="weights_trained-L18"></span>
    "context": 8,

<span id="weights_trained-L19"></span>
    "norm": "RMSNorm",

<span id="weights_trained-L20"></span>
    "eps": 1e-05,

<span id="weights_trained-L21"></span>
    "position": "learned absolute position",

<span id="weights_trained-L22"></span>
    "activation": "ReLU",

<span id="weights_trained-L23"></span>
    "bias": false,

<span id="weights_trained-L24"></span>
    "dropout": 0.0,

<span id="weights_trained-L25"></span>
    "tied_embeddings": false,

<span id="weights_trained-L26"></span>
    "dtype": "float64",

<span id="weights_trained-L27"></span>
    "seed": 23

<span id="weights_trained-L28"></span>
  },

<span id="weights_trained-L29"></span>
  "parameters": {

<span id="weights_trained-L30"></span>
    "E": [

<span id="weights_trained-L31"></span>
      [

<span id="weights_trained-L32"></span>
        0.0,

<span id="weights_trained-L33"></span>
        0.0,

<span id="weights_trained-L34"></span>
        0.0,

<span id="weights_trained-L35"></span>
        0.0

<span id="weights_trained-L36"></span>
      ],

<span id="weights_trained-L37"></span>
      [

<span id="weights_trained-L38"></span>
        0.4052665704509908,

<span id="weights_trained-L39"></span>
        -0.13645826723147694,

<span id="weights_trained-L40"></span>
        0.880672324789573,

<span id="weights_trained-L41"></span>
        0.2146078974441324

<span id="weights_trained-L42"></span>
      ],

<span id="weights_trained-L43"></span>
      [

<span id="weights_trained-L44"></span>
        -0.41402480776723555,

<span id="weights_trained-L45"></span>
        0.8976377021170958,

<span id="weights_trained-L46"></span>
        -0.20475984694716162,

<span id="weights_trained-L47"></span>
        0.5363922214217095

<span id="weights_trained-L48"></span>
      ],

<span id="weights_trained-L49"></span>
      [

<span id="weights_trained-L50"></span>
        0.522332368093881,

<span id="weights_trained-L51"></span>
        -0.1627163251385308,

<span id="weights_trained-L52"></span>
        -0.44183553727956254,

<span id="weights_trained-L53"></span>
        0.6930100887813707

<span id="weights_trained-L54"></span>
      ],

<span id="weights_trained-L55"></span>
      [

<span id="weights_trained-L56"></span>
        0.5642765126898115,

<span id="weights_trained-L57"></span>
        -0.17829019233412394,

<span id="weights_trained-L58"></span>
        1.0052418508273846,

<span id="weights_trained-L59"></span>
        0.2302511866468691

<span id="weights_trained-L60"></span>
      ],

<span id="weights_trained-L61"></span>
      [

<span id="weights_trained-L62"></span>
        0.24866447668057495,

<span id="weights_trained-L63"></span>
        0.6780220920160707,

<span id="weights_trained-L64"></span>
        0.22053460562650315,

<span id="weights_trained-L65"></span>
        -0.7765776956913002

<span id="weights_trained-L66"></span>
      ],

<span id="weights_trained-L67"></span>
      [

<span id="weights_trained-L68"></span>
        0.04498881876426931,

<span id="weights_trained-L69"></span>
        -0.44910340538948257,

<span id="weights_trained-L70"></span>
        0.07049946858335403,

<span id="weights_trained-L71"></span>
        0.013794423406222472

<span id="weights_trained-L72"></span>
      ],

<span id="weights_trained-L73"></span>
      [

<span id="weights_trained-L74"></span>
        0.08869044690994136,

<span id="weights_trained-L75"></span>
        0.17738089381988273,

<span id="weights_trained-L76"></span>
        -0.26607134072982386,

<span id="weights_trained-L77"></span>
        0.35476178763976546

<span id="weights_trained-L78"></span>
      ]

<span id="weights_trained-L79"></span>
    ],

<span id="weights_trained-L80"></span>
    "P": [

<span id="weights_trained-L81"></span>
      [

<span id="weights_trained-L82"></span>
        -0.35411819233046726,

<span id="weights_trained-L83"></span>
        -0.31606773502456975,

<span id="weights_trained-L84"></span>
        -0.2399170956014412,

<span id="weights_trained-L85"></span>
        -0.074896023503719

<span id="weights_trained-L86"></span>
      ],

<span id="weights_trained-L87"></span>
      [

<span id="weights_trained-L88"></span>
        0.2724124617391578,

<span id="weights_trained-L89"></span>
        0.18635818470800816,

<span id="weights_trained-L90"></span>
        0.26048613856626973,

<span id="weights_trained-L91"></span>
        -0.14095483867358694

<span id="weights_trained-L92"></span>
      ],

<span id="weights_trained-L93"></span>
      [

<span id="weights_trained-L94"></span>
        -0.059263020127469423,

<span id="weights_trained-L95"></span>
        0.18811412683756437,

<span id="weights_trained-L96"></span>
        -0.3821407407670451,

<span id="weights_trained-L97"></span>
        0.04859476341703128

<span id="weights_trained-L98"></span>
      ],

<span id="weights_trained-L99"></span>
      [

<span id="weights_trained-L100"></span>
        0.03453491008920237,

<span id="weights_trained-L101"></span>
        -0.3400972189584134,

<span id="weights_trained-L102"></span>
        -0.04272852618482567,

<span id="weights_trained-L103"></span>
        -0.10520393340810176

<span id="weights_trained-L104"></span>
      ],

<span id="weights_trained-L105"></span>
      [

<span id="weights_trained-L106"></span>
        0.3373549235905165,

<span id="weights_trained-L107"></span>
        0.32326030437630504,

<span id="weights_trained-L108"></span>
        -0.13422718201326223,

<span id="weights_trained-L109"></span>
        -0.20008979077668104

<span id="weights_trained-L110"></span>
      ],

<span id="weights_trained-L111"></span>
      [

<span id="weights_trained-L112"></span>
        -0.04434522345497068,

<span id="weights_trained-L113"></span>
        0.08869044690994136,

<span id="weights_trained-L114"></span>
        -0.08869044690994136,

<span id="weights_trained-L115"></span>
        -0.08869044690994136

<span id="weights_trained-L116"></span>
      ],

<span id="weights_trained-L117"></span>
      [

<span id="weights_trained-L118"></span>
        0.04434522345497068,

<span id="weights_trained-L119"></span>
        -0.08869044690994136,

<span id="weights_trained-L120"></span>
        -0.04434522345497068,

<span id="weights_trained-L121"></span>
        -0.04434522345497068

<span id="weights_trained-L122"></span>
      ],

<span id="weights_trained-L123"></span>
      [

<span id="weights_trained-L124"></span>
        -0.04434522345497068,

<span id="weights_trained-L125"></span>
        0.0,

<span id="weights_trained-L126"></span>
        0.08869044690994136,

<span id="weights_trained-L127"></span>
        0.04434522345497068

<span id="weights_trained-L128"></span>
      ]

<span id="weights_trained-L129"></span>
    ],

<span id="weights_trained-L130"></span>
    "Wq": [

<span id="weights_trained-L131"></span>
      [

<span id="weights_trained-L132"></span>
        0.12901819214113494,

<span id="weights_trained-L133"></span>
        0.10018194346631253,

<span id="weights_trained-L134"></span>
        -0.07676758359219502,

<span id="weights_trained-L135"></span>
        -0.23410226462910147

<span id="weights_trained-L136"></span>
      ],

<span id="weights_trained-L137"></span>
      [

<span id="weights_trained-L138"></span>
        -0.14199319291176252,

<span id="weights_trained-L139"></span>
        -0.19638590009989923,

<span id="weights_trained-L140"></span>
        -0.5053521160865082,

<span id="weights_trained-L141"></span>
        -0.217821629359178

<span id="weights_trained-L142"></span>
      ],

<span id="weights_trained-L143"></span>
      [

<span id="weights_trained-L144"></span>
        -0.29828838008954023,

<span id="weights_trained-L145"></span>
        -0.23753852184672697,

<span id="weights_trained-L146"></span>
        0.04572017172329083,

<span id="weights_trained-L147"></span>
        -0.10748150272504867

<span id="weights_trained-L148"></span>
      ],

<span id="weights_trained-L149"></span>
      [

<span id="weights_trained-L150"></span>
        -0.2137456044653996,

<span id="weights_trained-L151"></span>
        0.30526990802780746,

<span id="weights_trained-L152"></span>
        -0.1962986205984683,

<span id="weights_trained-L153"></span>
        -0.1110553073336788

<span id="weights_trained-L154"></span>
      ]

<span id="weights_trained-L155"></span>
    ],

<span id="weights_trained-L156"></span>
    "Wk": [

<span id="weights_trained-L157"></span>
      [

<span id="weights_trained-L158"></span>
        -0.16471598616965574,

<span id="weights_trained-L159"></span>
        -0.49600578606092294,

<span id="weights_trained-L160"></span>
        -0.1407311404709995,

<span id="weights_trained-L161"></span>
        -0.015111991294880311

<span id="weights_trained-L162"></span>
      ],

<span id="weights_trained-L163"></span>
      [

<span id="weights_trained-L164"></span>
        0.037844152863870856,

<span id="weights_trained-L165"></span>
        0.10388911362853988,

<span id="weights_trained-L166"></span>
        0.008304300651785165,

<span id="weights_trained-L167"></span>
        0.15278269613010464

<span id="weights_trained-L168"></span>
      ],

<span id="weights_trained-L169"></span>
      [

<span id="weights_trained-L170"></span>
        0.17728364851894093,

<span id="weights_trained-L171"></span>
        -0.10710726152395218,

<span id="weights_trained-L172"></span>
        0.45708888477971765,

<span id="weights_trained-L173"></span>
        0.06371481273508782

<span id="weights_trained-L174"></span>
      ],

<span id="weights_trained-L175"></span>
      [

<span id="weights_trained-L176"></span>
        0.583954943849413,

<span id="weights_trained-L177"></span>
        -0.0552760550869857,

<span id="weights_trained-L178"></span>
        -0.08718302159177573,

<span id="weights_trained-L179"></span>
        0.10321747025562987

<span id="weights_trained-L180"></span>
      ]

<span id="weights_trained-L181"></span>
    ],

<span id="weights_trained-L182"></span>
    "Wv": [

<span id="weights_trained-L183"></span>
      [

<span id="weights_trained-L184"></span>
        -0.1661979024664514,

<span id="weights_trained-L185"></span>
        -0.09760614382746562,

<span id="weights_trained-L186"></span>
        -0.024523795325299438,

<span id="weights_trained-L187"></span>
        -0.5097903198037397

<span id="weights_trained-L188"></span>
      ],

<span id="weights_trained-L189"></span>
      [

<span id="weights_trained-L190"></span>
        0.24106504283779193,

<span id="weights_trained-L191"></span>
        0.23597985056730156,

<span id="weights_trained-L192"></span>
        -0.027017122253964024,

<span id="weights_trained-L193"></span>
        -0.05770683656485458

<span id="weights_trained-L194"></span>
      ],

<span id="weights_trained-L195"></span>
      [

<span id="weights_trained-L196"></span>
        0.03810175702924752,

<span id="weights_trained-L197"></span>
        -0.12171722760788875,

<span id="weights_trained-L198"></span>
        0.2979115911673585,

<span id="weights_trained-L199"></span>
        -0.4813512704399146

<span id="weights_trained-L200"></span>
      ],

<span id="weights_trained-L201"></span>
      [

<span id="weights_trained-L202"></span>
        0.11002371234763587,

<span id="weights_trained-L203"></span>
        0.07441640646561325,

<span id="weights_trained-L204"></span>
        -0.13079117324607692,

<span id="weights_trained-L205"></span>
        -0.21717425754208874

<span id="weights_trained-L206"></span>
      ]

<span id="weights_trained-L207"></span>
    ],

<span id="weights_trained-L208"></span>
    "Wo": [

<span id="weights_trained-L209"></span>
      [

<span id="weights_trained-L210"></span>
        -0.10051174909605023,

<span id="weights_trained-L211"></span>
        0.146567514684471,

<span id="weights_trained-L212"></span>
        0.001355887411496713,

<span id="weights_trained-L213"></span>
        0.30323168182859395

<span id="weights_trained-L214"></span>
      ],

<span id="weights_trained-L215"></span>
      [

<span id="weights_trained-L216"></span>
        -0.08803392347933432,

<span id="weights_trained-L217"></span>
        0.07801132101175781,

<span id="weights_trained-L218"></span>
        -0.2681511753621345,

<span id="weights_trained-L219"></span>
        -0.13974658063479029

<span id="weights_trained-L220"></span>
      ],

<span id="weights_trained-L221"></span>
      [

<span id="weights_trained-L222"></span>
        0.17681444560426157,

<span id="weights_trained-L223"></span>
        0.4886310674820848,

<span id="weights_trained-L224"></span>
        0.17080799482272205,

<span id="weights_trained-L225"></span>
        0.12478537865131792

<span id="weights_trained-L226"></span>
      ],

<span id="weights_trained-L227"></span>
      [

<span id="weights_trained-L228"></span>
        -0.5492654791035682,

<span id="weights_trained-L229"></span>
        0.07304797778675899,

<span id="weights_trained-L230"></span>
        0.4369527468224175,

<span id="weights_trained-L231"></span>
        0.1366195863912654

<span id="weights_trained-L232"></span>
      ]

<span id="weights_trained-L233"></span>
    ],

<span id="weights_trained-L234"></span>
    "W1": [

<span id="weights_trained-L235"></span>
      [

<span id="weights_trained-L236"></span>
        0.5951426698638274,

<span id="weights_trained-L237"></span>
        -0.26544520489076334,

<span id="weights_trained-L238"></span>
        -0.45222946443048656,

<span id="weights_trained-L239"></span>
        0.25027303130409817,

<span id="weights_trained-L240"></span>
        -0.13106752573481484,

<span id="weights_trained-L241"></span>
        -0.5360738577038495,

<span id="weights_trained-L242"></span>
        0.27908927386211285,

<span id="weights_trained-L243"></span>
        -0.2894186884228373

<span id="weights_trained-L244"></span>
      ],

<span id="weights_trained-L245"></span>
      [

<span id="weights_trained-L246"></span>
        -0.0846092483253801,

<span id="weights_trained-L247"></span>
        0.23310034471907004,

<span id="weights_trained-L248"></span>
        0.30921994573767775,

<span id="weights_trained-L249"></span>
        0.31398452903625895,

<span id="weights_trained-L250"></span>
        -0.15841584354623056,

<span id="weights_trained-L251"></span>
        -0.30877464123069054,

<span id="weights_trained-L252"></span>
        -0.3234964068172794,

<span id="weights_trained-L253"></span>
        -0.27658395249135376

<span id="weights_trained-L254"></span>
      ],

<span id="weights_trained-L255"></span>
      [

<span id="weights_trained-L256"></span>
        -0.21898615750849917,

<span id="weights_trained-L257"></span>
        0.36914665333735475,

<span id="weights_trained-L258"></span>
        0.11107552181042529,

<span id="weights_trained-L259"></span>
        0.19557527950958822,

<span id="weights_trained-L260"></span>
        -0.23102667570984356,

<span id="weights_trained-L261"></span>
        0.23579609414078465,

<span id="weights_trained-L262"></span>
        -0.28690132204926355,

<span id="weights_trained-L263"></span>
        0.01800718860998905

<span id="weights_trained-L264"></span>
      ],

<span id="weights_trained-L265"></span>
      [

<span id="weights_trained-L266"></span>
        0.5708099659963267,

<span id="weights_trained-L267"></span>
        -0.3131090599310812,

<span id="weights_trained-L268"></span>
        0.14056178897711857,

<span id="weights_trained-L269"></span>
        0.021318112563615703,

<span id="weights_trained-L270"></span>
        -0.39554942482874306,

<span id="weights_trained-L271"></span>
        -0.20913947036137473,

<span id="weights_trained-L272"></span>
        -0.12586037788522791,

<span id="weights_trained-L273"></span>
        -0.49954284350267636

<span id="weights_trained-L274"></span>
      ]

<span id="weights_trained-L275"></span>
    ],

<span id="weights_trained-L276"></span>
    "W2": [

<span id="weights_trained-L277"></span>
      [

<span id="weights_trained-L278"></span>
        -0.37393827764725274,

<span id="weights_trained-L279"></span>
        -0.6995703125650319,

<span id="weights_trained-L280"></span>
        -0.5838104346189115,

<span id="weights_trained-L281"></span>
        -0.37716754856659324

<span id="weights_trained-L282"></span>
      ],

<span id="weights_trained-L283"></span>
      [

<span id="weights_trained-L284"></span>
        0.4328712557247543,

<span id="weights_trained-L285"></span>
        0.3145770791056371,

<span id="weights_trained-L286"></span>
        -0.04813244766737684,

<span id="weights_trained-L287"></span>
        0.03451033414575454

<span id="weights_trained-L288"></span>
      ],

<span id="weights_trained-L289"></span>
      [

<span id="weights_trained-L290"></span>
        -0.08782339292405175,

<span id="weights_trained-L291"></span>
        -0.14500468980523987,

<span id="weights_trained-L292"></span>
        -0.3156320692426011,

<span id="weights_trained-L293"></span>
        0.23045040898830776

<span id="weights_trained-L294"></span>
      ],

<span id="weights_trained-L295"></span>
      [

<span id="weights_trained-L296"></span>
        0.044943500081096904,

<span id="weights_trained-L297"></span>
        -0.1701151669880897,

<span id="weights_trained-L298"></span>
        -0.3098381002852733,

<span id="weights_trained-L299"></span>
        0.027523849621446973

<span id="weights_trained-L300"></span>
      ],

<span id="weights_trained-L301"></span>
      [

<span id="weights_trained-L302"></span>
        -0.06639234862124987,

<span id="weights_trained-L303"></span>
        0.3204323241752668,

<span id="weights_trained-L304"></span>
        0.009857538582702769,

<span id="weights_trained-L305"></span>
        -0.1767642898322145

<span id="weights_trained-L306"></span>
      ],

<span id="weights_trained-L307"></span>
      [

<span id="weights_trained-L308"></span>
        0.052454066052005935,

<span id="weights_trained-L309"></span>
        0.473205483546291,

<span id="weights_trained-L310"></span>
        0.2803020769159998,

<span id="weights_trained-L311"></span>
        -0.3120454506307641

<span id="weights_trained-L312"></span>
      ],

<span id="weights_trained-L313"></span>
      [

<span id="weights_trained-L314"></span>
        -0.33810736039362654,

<span id="weights_trained-L315"></span>
        -0.22276930186292088,

<span id="weights_trained-L316"></span>
        -0.45467945672294335,

<span id="weights_trained-L317"></span>
        -0.19897167185812908

<span id="weights_trained-L318"></span>
      ],

<span id="weights_trained-L319"></span>
      [

<span id="weights_trained-L320"></span>
        -0.4169712925576273,

<span id="weights_trained-L321"></span>
        0.056932474914360195,

<span id="weights_trained-L322"></span>
        0.1515049129100647,

<span id="weights_trained-L323"></span>
        -0.03658887231023298

<span id="weights_trained-L324"></span>
      ]

<span id="weights_trained-L325"></span>
    ],

<span id="weights_trained-L326"></span>
    "U": [

<span id="weights_trained-L327"></span>
      [

<span id="weights_trained-L328"></span>
        0.23159767479751747,

<span id="weights_trained-L329"></span>
        -1.2033863705883912,

<span id="weights_trained-L330"></span>
        1.3661768603925686,

<span id="weights_trained-L331"></span>
        -0.6526826095161274,

<span id="weights_trained-L332"></span>
        -1.1245086622257228,

<span id="weights_trained-L333"></span>
        -0.20234191971768323,

<span id="weights_trained-L334"></span>
        0.20988593631195954,

<span id="weights_trained-L335"></span>
        0.873423035382752

<span id="weights_trained-L336"></span>
      ],

<span id="weights_trained-L337"></span>
      [

<span id="weights_trained-L338"></span>
        0.05918561900176784,

<span id="weights_trained-L339"></span>
        -0.1906891875722753,

<span id="weights_trained-L340"></span>
        -1.0934387153207679,

<span id="weights_trained-L341"></span>
        1.0743612165020355,

<span id="weights_trained-L342"></span>
        -0.2586528266277411,

<span id="weights_trained-L343"></span>
        -1.327446155300007,

<span id="weights_trained-L344"></span>
        0.05972726377507129,

<span id="weights_trained-L345"></span>
        1.2277697804175587

<span id="weights_trained-L346"></span>
      ],

<span id="weights_trained-L347"></span>
      [

<span id="weights_trained-L348"></span>
        0.3000281521189067,

<span id="weights_trained-L349"></span>
        0.8021715972663168,

<span id="weights_trained-L350"></span>
        1.1121622866814025,

<span id="weights_trained-L351"></span>
        -1.2092777006061424,

<span id="weights_trained-L352"></span>
        1.168320975663797,

<span id="weights_trained-L353"></span>
        -1.1091133248193976,

<span id="weights_trained-L354"></span>
        0.35104960747678415,

<span id="weights_trained-L355"></span>
        -0.13910417247374068

<span id="weights_trained-L356"></span>
      ],

<span id="weights_trained-L357"></span>
      [

<span id="weights_trained-L358"></span>
        0.8124216132521279,

<span id="weights_trained-L359"></span>
        -0.6967202042146631,

<span id="weights_trained-L360"></span>
        -0.28592686466808004,

<span id="weights_trained-L361"></span>
        1.3282719890323578,

<span id="weights_trained-L362"></span>
        -0.38496093333016784,

<span id="weights_trained-L363"></span>
        0.11537519484207422,

<span id="weights_trained-L364"></span>
        0.9204017868185256,

<span id="weights_trained-L365"></span>
        -0.9496749149352876

<span id="weights_trained-L366"></span>
      ]

<span id="weights_trained-L367"></span>
    ],

<span id="weights_trained-L368"></span>
    "g1": [

<span id="weights_trained-L369"></span>
      0.8833610761666376,

<span id="weights_trained-L370"></span>
      0.7049167265305969,

<span id="weights_trained-L371"></span>
      0.9471476805097483,

<span id="weights_trained-L372"></span>
      0.6120434754247834

<span id="weights_trained-L373"></span>
    ],

<span id="weights_trained-L374"></span>
    "g2": [

<span id="weights_trained-L375"></span>
      1.1507837929300662,

<span id="weights_trained-L376"></span>
      0.8746811057503767,

<span id="weights_trained-L377"></span>
      0.6864572816868669,

<span id="weights_trained-L378"></span>
      1.2693203635085186

<span id="weights_trained-L379"></span>
    ],

<span id="weights_trained-L380"></span>
    "gf": [

<span id="weights_trained-L381"></span>
      2.098956853000513,

<span id="weights_trained-L382"></span>
      2.3455107933702246,

<span id="weights_trained-L383"></span>
      2.1185102336010564,

<span id="weights_trained-L384"></span>
      1.9326554118256944

<span id="weights_trained-L385"></span>
    ]

<span id="weights_trained-L386"></span>
  }

<span id="weights_trained-L387"></span>
}
```