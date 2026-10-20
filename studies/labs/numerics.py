"""真实数值算法；随机小模型只验证机制，不代表商业LLM能力或GPU性能。
依赖 NumPy。所有计算默认float64，便于检查误差。
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
import math
import numpy as np


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    m = np.max(x, axis=axis, keepdims=True)
    if not np.all(np.isfinite(m)):
        raise ValueError('每个softmax切片至少需要一个有限分数，且不允许+inf/NaN')
    z = np.exp(x - m)
    return z / z.sum(axis=axis, keepdims=True)


def cross_entropy(logits: np.ndarray, target: int) -> tuple[float, np.ndarray]:
    x = np.asarray(logits, dtype=np.float64)
    if x.ndim != 1 or not 0 <= target < len(x) or not np.all(np.isfinite(x)):
        raise ValueError('需要有限一维logits与有效标签')
    m = x.max()
    loss = float(m + np.log(np.exp(x-m).sum()) - x[target])
    grad = softmax(x); grad[target] -= 1
    return loss, grad


def rope(x: np.ndarray, positions: np.ndarray, base: float = 10000.0) -> np.ndarray:
    """x:[B,H,T,Dh]，成对维度旋转。生产实现可能采用不同的维度排列。"""
    if x.ndim != 4 or x.shape[-1] % 2 or len(positions) != x.shape[-2]:
        raise ValueError('RoPE要求偶数头维与匹配的位置长度')
    freq = base ** (-np.arange(0, x.shape[-1], 2) / x.shape[-1])
    angle = np.asarray(positions)[:, None] * freq[None, :]
    c, s = np.cos(angle)[None,None,:,:], np.sin(angle)[None,None,:,:]
    out = np.empty_like(x)
    out[...,0::2] = x[...,0::2]*c - x[...,1::2]*s
    out[...,1::2] = x[...,0::2]*s + x[...,1::2]*c
    return out


@dataclass(frozen=True)
class Config:
    vocab: int = 32
    width: int = 16
    heads: int = 4
    kv_heads: int = 2
    hidden: int = 32
    layers: int = 2


class Decoder:
    """Pre-RMSNorm + GQA + RoPE + SwiGLU的最小完整前向。
    未实现padding/训练/量化/并行服务；不接受不同长度的批内序列。
    """
    def __init__(self, config: Config = Config(), seed: int = 17):
        c = config
        if min(c.vocab,c.width,c.heads,c.kv_heads,c.hidden,c.layers) <= 0:
            raise ValueError('维度必须为正')
        if c.width % c.heads or c.heads % c.kv_heads or (c.width//c.heads)%2:
            raise ValueError('头维与GQA分组不兼容')
        self.c = c; rng=np.random.default_rng(seed); d=c.width; k=c.kv_heads*(d//c.heads)
        def w(i,j): return rng.normal(size=(i,j))/math.sqrt(i)
        self.emb=w(c.vocab,d)
        self.blocks=[dict(q=w(d,d),k=w(d,k),v=w(d,k),o=w(d,d),gate=w(d,c.hidden),up=w(d,c.hidden),down=w(c.hidden,d)) for _ in range(c.layers)]
        self.lm=w(d,c.vocab)

    @staticmethod
    def norm(x): return x/np.sqrt(np.mean(x*x,axis=-1,keepdims=True)+1e-6)

    def forward(self, ids: np.ndarray, cache=None, *, causal=True, wrong_offset=False):
        ids=np.asarray(ids)
        if ids.ndim != 2 or ids.shape[1] < 1 or not np.issubdtype(ids.dtype,np.integer):
            raise ValueError('Token ID形状必须[B,T]且非空')
        c=self.c; b,t=ids.shape; h=c.heads; hk=c.kv_heads; dh=c.width//h
        if ids.min()<0 or ids.max()>=c.vocab:raise ValueError('Token超出词表')
        if cache is None: cache=[None]*c.layers
        if len(cache)!=c.layers:raise ValueError('缓存层数不匹配')
        lengths=[0 if kv is None else kv[0].shape[-2] for kv in cache]
        if len(set(lengths))!=1:raise ValueError('各层缓存长度不一致')
        past=lengths[0]; x=self.emb[ids]; new=[]
        pos=np.arange(t)+(0 if wrong_offset else past)
        for w,old in zip(self.blocks,cache):
            z=self.norm(x)
            q=(z@w['q']).reshape(b,t,h,dh).transpose(0,2,1,3)
            k=(z@w['k']).reshape(b,t,hk,dh).transpose(0,2,1,3)
            v=(z@w['v']).reshape(b,t,hk,dh).transpose(0,2,1,3)
            q=rope(q,pos); k=rope(k,pos)
            if old is not None:
                if old[0].shape[:2]!=(b,hk) or old[0].shape[-1]!=dh or old[0].shape!=old[1].shape:
                    raise ValueError('缓存形状不兼容')
                k=np.concatenate([old[0],k],axis=-2);v=np.concatenate([old[1],v],axis=-2)
            new.append((k.copy(),v.copy()))
            kk=np.repeat(k,h//hk,axis=1);vv=np.repeat(v,h//hk,axis=1)
            scores=q@kk.swapaxes(-1,-2)/math.sqrt(dh)
            if causal:
                allowed=np.arange(k.shape[-2])[None,:] <= (past+np.arange(t))[:,None]
                scores=np.where(allowed[None,None,:,:],scores,-np.inf)
            y=(softmax(scores)@vv).transpose(0,2,1,3).reshape(b,t,c.width)
            x=x+y@w['o'];z=self.norm(x)
            gate=z@w['gate'];silu=gate/(1+np.exp(-np.clip(gate,-700,700)))
            x=x+(silu*(z@w['up']))@w['down']
        return self.norm(x)@self.lm,new


def online_attention(scores: np.ndarray, values: np.ndarray, block: int=3) -> np.ndarray:
    """一行注意力的在线softmax归并，验证分块恒等式；不是CUDA FlashAttention。"""
    scores=np.asarray(scores,dtype=float);values=np.asarray(values,dtype=float)
    if scores.ndim!=1 or values.ndim!=2 or len(scores)!=len(values) or len(scores)==0 or block<1:
        raise ValueError('形状或块大小无效')
    if not np.isfinite(scores).all() or not np.isfinite(values).all():raise ValueError('本实验要求有限输入')
    m=-np.inf;l=0.;a=np.zeros(values.shape[1])
    for start in range(0,len(scores),block):
        s=scores[start:start+block];v=values[start:start+block]
        new_m=max(m,float(s.max()));alpha=np.exp(m-new_m)
        p=np.exp(s-new_m);a=a*alpha+p@v;l=l*alpha+p.sum();m=new_m
    return a/l


def speculative_sample(p: np.ndarray,q: np.ndarray,n: int=30000,seed=17):
    """单步草稿接受/残差采样。p为目标分布，q为草稿分布。"""
    p=np.asarray(p,dtype=float);q=np.asarray(q,dtype=float)
    if p.shape!=q.shape or p.ndim!=1 or np.any(p<0) or np.any(q<0) or not np.isclose(p.sum(),1) or not np.isclose(q.sum(),1):
        raise ValueError('需要同维归一化非负分布')
    rng=np.random.default_rng(seed);counts=np.zeros(len(p));accepted=0
    residual=np.maximum(p-q,0);mass=residual.sum()
    for _ in range(n):
        x=int(rng.choice(len(q),p=q))
        if rng.random() < min(1.,p[x]/q[x]):accepted+=1;y=x
        else:
            if mass<=0:raise AssertionError('相同分布不会拒绝')
            y=int(rng.choice(len(p),p=residual/mass))
        counts[y]+=1
    return {'empirical':(counts/n).tolist(),'target':p.tolist(),'acceptance':accepted/n,'trials':n}


def dpo_loss(policy_w,policy_l,ref_w,ref_l,beta=.1):
    """输入均为回答序列的log probability，不是Token概率。"""
    if beta<=0:raise ValueError('beta必须为正')
    z=beta*((policy_w-ref_w)-(policy_l-ref_l))
    loss=float(np.logaddexp(0.,-z));grad=-beta/(1+math.exp(max(-700,min(700,z))))
    return loss,grad


def train_bpe(words: list[str], merges: int=5):
    """教学字节BPE；无预分词、特殊Token协议或真实产品词表。"""
    corpus=[[(b,) for b in w.encode('utf-8')] for w in words];rules=[]
    for _ in range(merges):
        counts=Counter((s[i],s[i+1]) for s in corpus for i in range(len(s)-1))
        if not counts:break
        pair=min(counts,key=lambda p:(-counts[p],p));rules.append(pair)
        corpus=[merge_pair(s,pair) for s in corpus]
    return rules


def merge_pair(seq,pair):
    out=[];i=0
    while i<len(seq):
        if i+1<len(seq) and (seq[i],seq[i+1])==pair:out.append(seq[i]+seq[i+1]);i+=2
        else:out.append(seq[i]);i+=1
    return out


def encode_bpe(text,rules):
    seq=[(b,) for b in text.encode('utf-8')]
    for pair in rules:seq=merge_pair(seq,pair)
    return seq


def run():
    model=Decoder();ids=np.array([[1,5,2,9,3,4,8,1,2]])
    full,_=model.forward(ids);cache=None;outs=[]
    for i in range(ids.shape[1]):
        y,cache=model.forward(ids[:,i:i+1],cache);outs.append(y)
    err=float(np.max(np.abs(full-np.concatenate(outs,axis=1))))
    wrong_cache=None;wrong=[]
    for i in range(ids.shape[1]):
        y,wrong_cache=model.forward(ids[:,i:i+1],wrong_cache,wrong_offset=True);wrong.append(y)
    bad=float(np.max(np.abs(full-np.concatenate(wrong,axis=1))))
    scores=np.array([1000,999,997,1001,998,996,1002.]);v=np.arange(21.).reshape(7,3)
    tiled=float(np.max(np.abs(online_attention(scores,v)-softmax(scores)@v)))
    rules=train_bpe(['lower','lower','lowest','low','工程']);encoded=encode_bpe('工程lower',rules)
    return {'kind':'数值机制实验；非商用模型评测','cache_max_error':err,'wrong_rope_offset_error':bad,'online_softmax_error':tiled,'speculative':speculative_sample(np.array([.6,.3,.1]),np.array([.2,.5,.3])),'byte_bpe_roundtrip':bytes(x for t in encoded for x in t).decode('utf-8')}

if __name__=='__main__':
    import json
    print(json.dumps(run(),ensure_ascii=False,indent=2))
