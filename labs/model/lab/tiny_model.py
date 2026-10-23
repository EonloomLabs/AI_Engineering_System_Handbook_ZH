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
