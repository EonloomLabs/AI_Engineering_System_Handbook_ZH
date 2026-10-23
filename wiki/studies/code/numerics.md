---
title: "numerics.py"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# numerics.py

数值机制与前向实现。对应第01、02、04、05、06章。依赖：NumPy。

缓存、分块softmax、采样与BPE；不是GPU服务或商业模型。[阅读运行说明](../experiments.md) / [查看实测结果](../results.md)

[原始Python文件](../../../studies/labs/numerics.py) · 188行

```

<span id="L1"></span>
"""真实数值算法；随机小模型只验证机制，不代表商业LLM能力或GPU性能。
<span id="L2"></span>
依赖 NumPy。所有计算默认float64，便于检查误差。
<span id="L3"></span>
"""
<span id="L4"></span>
from __future__ import annotations
<span id="L5"></span>
from collections import Counter
<span id="L6"></span>
from dataclasses import dataclass
<span id="L7"></span>
import math
<span id="L8"></span>
import numpy as np
<span id="L9"></span>
 
<span id="L10"></span>
 
<span id="L11"></span>
def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
<span id="L12"></span>
    x = np.asarray(x, dtype=np.float64)
<span id="L13"></span>
    m = np.max(x, axis=axis, keepdims=True)
<span id="L14"></span>
    if not np.all(np.isfinite(m)):
<span id="L15"></span>
        raise ValueError('每个softmax切片至少需要一个有限分数，且不允许+inf/NaN')
<span id="L16"></span>
    z = np.exp(x - m)
<span id="L17"></span>
    return z / z.sum(axis=axis, keepdims=True)
<span id="L18"></span>
 
<span id="L19"></span>
 
<span id="L20"></span>
def cross_entropy(logits: np.ndarray, target: int) -> tuple[float, np.ndarray]:
<span id="L21"></span>
    x = np.asarray(logits, dtype=np.float64)
<span id="L22"></span>
    if x.ndim != 1 or not 0 <= target < len(x) or not np.all(np.isfinite(x)):
<span id="L23"></span>
        raise ValueError('需要有限一维logits与有效标签')
<span id="L24"></span>
    m = x.max()
<span id="L25"></span>
    loss = float(m + np.log(np.exp(x-m).sum()) - x[target])
<span id="L26"></span>
    grad = softmax(x); grad[target] -= 1
<span id="L27"></span>
    return loss, grad
<span id="L28"></span>
 
<span id="L29"></span>
 
<span id="L30"></span>
def rope(x: np.ndarray, positions: np.ndarray, base: float = 10000.0) -> np.ndarray:
<span id="L31"></span>
    """x:[B,H,T,Dh]，成对维度旋转。生产实现可能采用不同的维度排列。"""
<span id="L32"></span>
    if x.ndim != 4 or x.shape[-1] % 2 or len(positions) != x.shape[-2]:
<span id="L33"></span>
        raise ValueError('RoPE要求偶数头维与匹配的位置长度')
<span id="L34"></span>
    freq = base ** (-np.arange(0, x.shape[-1], 2) / x.shape[-1])
<span id="L35"></span>
    angle = np.asarray(positions)[:, None] * freq[None, :]
<span id="L36"></span>
    c, s = np.cos(angle)[None,None,:,:], np.sin(angle)[None,None,:,:]
<span id="L37"></span>
    out = np.empty_like(x)
<span id="L38"></span>
    out[...,0::2] = x[...,0::2]*c - x[...,1::2]*s
<span id="L39"></span>
    out[...,1::2] = x[...,0::2]*s + x[...,1::2]*c
<span id="L40"></span>
    return out
<span id="L41"></span>
 
<span id="L42"></span>
 
<span id="L43"></span>
@dataclass(frozen=True)
<span id="L44"></span>
class Config:
<span id="L45"></span>
    vocab: int = 32
<span id="L46"></span>
    width: int = 16
<span id="L47"></span>
    heads: int = 4
<span id="L48"></span>
    kv_heads: int = 2
<span id="L49"></span>
    hidden: int = 32
<span id="L50"></span>
    layers: int = 2
<span id="L51"></span>
 
<span id="L52"></span>
 
<span id="L53"></span>
class Decoder:
<span id="L54"></span>
    """Pre-RMSNorm + GQA + RoPE + SwiGLU的最小完整前向。
<span id="L55"></span>
    未实现padding/训练/量化/并行服务；不接受不同长度的批内序列。
<span id="L56"></span>
    """
<span id="L57"></span>
    def __init__(self, config: Config = Config(), seed: int = 17):
<span id="L58"></span>
        c = config
<span id="L59"></span>
        if min(c.vocab,c.width,c.heads,c.kv_heads,c.hidden,c.layers) <= 0:
<span id="L60"></span>
            raise ValueError('维度必须为正')
<span id="L61"></span>
        if c.width % c.heads or c.heads % c.kv_heads or (c.width//c.heads)%2:
<span id="L62"></span>
            raise ValueError('头维与GQA分组不兼容')
<span id="L63"></span>
        self.c = c; rng=np.random.default_rng(seed); d=c.width; k=c.kv_heads*(d//c.heads)
<span id="L64"></span>
        def w(i,j): return rng.normal(size=(i,j))/math.sqrt(i)
<span id="L65"></span>
        self.emb=w(c.vocab,d)
<span id="L66"></span>
        self.blocks=[dict(q=w(d,d),k=w(d,k),v=w(d,k),o=w(d,d),gate=w(d,c.hidden),up=w(d,c.hidden),down=w(c.hidden,d)) for _ in range(c.layers)]
<span id="L67"></span>
        self.lm=w(d,c.vocab)
<span id="L68"></span>
 
<span id="L69"></span>
    @staticmethod
<span id="L70"></span>
    def norm(x): return x/np.sqrt(np.mean(x*x,axis=-1,keepdims=True)+1e-6)
<span id="L71"></span>
 
<span id="L72"></span>
    def forward(self, ids: np.ndarray, cache=None, *, causal=True, wrong_offset=False):
<span id="L73"></span>
        ids=np.asarray(ids)
<span id="L74"></span>
        if ids.ndim != 2 or ids.shape[1] < 1 or not np.issubdtype(ids.dtype,np.integer):
<span id="L75"></span>
            raise ValueError('Token ID形状必须[B,T]且非空')
<span id="L76"></span>
        c=self.c; b,t=ids.shape; h=c.heads; hk=c.kv_heads; dh=c.width//h
<span id="L77"></span>
        if ids.min()<0 or ids.max()>=c.vocab:raise ValueError('Token超出词表')
<span id="L78"></span>
        if cache is None: cache=[None]*c.layers
<span id="L79"></span>
        if len(cache)!=c.layers:raise ValueError('缓存层数不匹配')
<span id="L80"></span>
        lengths=[0 if kv is None else kv[0].shape[-2] for kv in cache]
<span id="L81"></span>
        if len(set(lengths))!=1:raise ValueError('各层缓存长度不一致')
<span id="L82"></span>
        past=lengths[0]; x=self.emb[ids]; new=[]
<span id="L83"></span>
        pos=np.arange(t)+(0 if wrong_offset else past)
<span id="L84"></span>
        for w,old in zip(self.blocks,cache):
<span id="L85"></span>
            z=self.norm(x)
<span id="L86"></span>
            q=(z@w['q']).reshape(b,t,h,dh).transpose(0,2,1,3)
<span id="L87"></span>
            k=(z@w['k']).reshape(b,t,hk,dh).transpose(0,2,1,3)
<span id="L88"></span>
            v=(z@w['v']).reshape(b,t,hk,dh).transpose(0,2,1,3)
<span id="L89"></span>
            q=rope(q,pos); k=rope(k,pos)
<span id="L90"></span>
            if old is not None:
<span id="L91"></span>
                if old[0].shape[:2]!=(b,hk) or old[0].shape[-1]!=dh or old[0].shape!=old[1].shape:
<span id="L92"></span>
                    raise ValueError('缓存形状不兼容')
<span id="L93"></span>
                k=np.concatenate([old[0],k],axis=-2);v=np.concatenate([old[1],v],axis=-2)
<span id="L94"></span>
            new.append((k.copy(),v.copy()))
<span id="L95"></span>
            kk=np.repeat(k,h//hk,axis=1);vv=np.repeat(v,h//hk,axis=1)
<span id="L96"></span>
            scores=q@kk.swapaxes(-1,-2)/math.sqrt(dh)
<span id="L97"></span>
            if causal:
<span id="L98"></span>
                allowed=np.arange(k.shape[-2])[None,:] <= (past+np.arange(t))[:,None]
<span id="L99"></span>
                scores=np.where(allowed[None,None,:,:],scores,-np.inf)
<span id="L100"></span>
            y=(softmax(scores)@vv).transpose(0,2,1,3).reshape(b,t,c.width)
<span id="L101"></span>
            x=x+y@w['o'];z=self.norm(x)
<span id="L102"></span>
            gate=z@w['gate'];silu=gate/(1+np.exp(-np.clip(gate,-700,700)))
<span id="L103"></span>
            x=x+(silu*(z@w['up']))@w['down']
<span id="L104"></span>
        return self.norm(x)@self.lm,new
<span id="L105"></span>
 
<span id="L106"></span>
 
<span id="L107"></span>
def online_attention(scores: np.ndarray, values: np.ndarray, block: int=3) -> np.ndarray:
<span id="L108"></span>
    """一行注意力的在线softmax归并，验证分块恒等式；不是CUDA FlashAttention。"""
<span id="L109"></span>
    scores=np.asarray(scores,dtype=float);values=np.asarray(values,dtype=float)
<span id="L110"></span>
    if scores.ndim!=1 or values.ndim!=2 or len(scores)!=len(values) or len(scores)==0 or block<1:
<span id="L111"></span>
        raise ValueError('形状或块大小无效')
<span id="L112"></span>
    if not np.isfinite(scores).all() or not np.isfinite(values).all():raise ValueError('本实验要求有限输入')
<span id="L113"></span>
    m=-np.inf;l=0.;a=np.zeros(values.shape[1])
<span id="L114"></span>
    for start in range(0,len(scores),block):
<span id="L115"></span>
        s=scores[start:start+block];v=values[start:start+block]
<span id="L116"></span>
        new_m=max(m,float(s.max()));alpha=np.exp(m-new_m)
<span id="L117"></span>
        p=np.exp(s-new_m);a=a*alpha+p@v;l=l*alpha+p.sum();m=new_m
<span id="L118"></span>
    return a/l
<span id="L119"></span>
 
<span id="L120"></span>
 
<span id="L121"></span>
def speculative_sample(p: np.ndarray,q: np.ndarray,n: int=30000,seed=17):
<span id="L122"></span>
    """单步草稿接受/残差采样。p为目标分布，q为草稿分布。"""
<span id="L123"></span>
    p=np.asarray(p,dtype=float);q=np.asarray(q,dtype=float)
<span id="L124"></span>
    if p.shape!=q.shape or p.ndim!=1 or np.any(p<0) or np.any(q<0) or not np.isclose(p.sum(),1) or not np.isclose(q.sum(),1):
<span id="L125"></span>
        raise ValueError('需要同维归一化非负分布')
<span id="L126"></span>
    rng=np.random.default_rng(seed);counts=np.zeros(len(p));accepted=0
<span id="L127"></span>
    residual=np.maximum(p-q,0);mass=residual.sum()
<span id="L128"></span>
    for _ in range(n):
<span id="L129"></span>
        x=int(rng.choice(len(q),p=q))
<span id="L130"></span>
        if rng.random() < min(1.,p[x]/q[x]):accepted+=1;y=x
<span id="L131"></span>
        else:
<span id="L132"></span>
            if mass<=0:raise AssertionError('相同分布不会拒绝')
<span id="L133"></span>
            y=int(rng.choice(len(p),p=residual/mass))
<span id="L134"></span>
        counts[y]+=1
<span id="L135"></span>
    return {'empirical':(counts/n).tolist(),'target':p.tolist(),'acceptance':accepted/n,'trials':n}
<span id="L136"></span>
 
<span id="L137"></span>
 
<span id="L138"></span>
def dpo_loss(policy_w,policy_l,ref_w,ref_l,beta=.1):
<span id="L139"></span>
    """输入均为回答序列的log probability，不是Token概率。"""
<span id="L140"></span>
    if beta<=0:raise ValueError('beta必须为正')
<span id="L141"></span>
    z=beta*((policy_w-ref_w)-(policy_l-ref_l))
<span id="L142"></span>
    loss=float(np.logaddexp(0.,-z));grad=-beta/(1+math.exp(max(-700,min(700,z))))
<span id="L143"></span>
    return loss,grad
<span id="L144"></span>
 
<span id="L145"></span>
 
<span id="L146"></span>
def train_bpe(words: list[str], merges: int=5):
<span id="L147"></span>
    """教学字节BPE；无预分词、特殊Token协议或真实产品词表。"""
<span id="L148"></span>
    corpus=[[(b,) for b in w.encode('utf-8')] for w in words];rules=[]
<span id="L149"></span>
    for _ in range(merges):
<span id="L150"></span>
        counts=Counter((s[i],s[i+1]) for s in corpus for i in range(len(s)-1))
<span id="L151"></span>
        if not counts:break
<span id="L152"></span>
        pair=min(counts,key=lambda p:(-counts[p],p));rules.append(pair)
<span id="L153"></span>
        corpus=[merge_pair(s,pair) for s in corpus]
<span id="L154"></span>
    return rules
<span id="L155"></span>
 
<span id="L156"></span>
 
<span id="L157"></span>
def merge_pair(seq,pair):
<span id="L158"></span>
    out=[];i=0
<span id="L159"></span>
    while i<len(seq):
<span id="L160"></span>
        if i+1<len(seq) and (seq[i],seq[i+1])==pair:out.append(seq[i]+seq[i+1]);i+=2
<span id="L161"></span>
        else:out.append(seq[i]);i+=1
<span id="L162"></span>
    return out
<span id="L163"></span>
 
<span id="L164"></span>
 
<span id="L165"></span>
def encode_bpe(text,rules):
<span id="L166"></span>
    seq=[(b,) for b in text.encode('utf-8')]
<span id="L167"></span>
    for pair in rules:seq=merge_pair(seq,pair)
<span id="L168"></span>
    return seq
<span id="L169"></span>
 
<span id="L170"></span>
 
<span id="L171"></span>
def run():
<span id="L172"></span>
    model=Decoder();ids=np.array([[1,5,2,9,3,4,8,1,2]])
<span id="L173"></span>
    full,_=model.forward(ids);cache=None;outs=[]
<span id="L174"></span>
    for i in range(ids.shape[1]):
<span id="L175"></span>
        y,cache=model.forward(ids[:,i:i+1],cache);outs.append(y)
<span id="L176"></span>
    err=float(np.max(np.abs(full-np.concatenate(outs,axis=1))))
<span id="L177"></span>
    wrong_cache=None;wrong=[]
<span id="L178"></span>
    for i in range(ids.shape[1]):
<span id="L179"></span>
        y,wrong_cache=model.forward(ids[:,i:i+1],wrong_cache,wrong_offset=True);wrong.append(y)
<span id="L180"></span>
    bad=float(np.max(np.abs(full-np.concatenate(wrong,axis=1))))
<span id="L181"></span>
    scores=np.array([1000,999,997,1001,998,996,1002.]);v=np.arange(21.).reshape(7,3)
<span id="L182"></span>
    tiled=float(np.max(np.abs(online_attention(scores,v)-softmax(scores)@v)))
<span id="L183"></span>
    rules=train_bpe(['lower','lower','lowest','low','工程']);encoded=encode_bpe('工程lower',rules)
<span id="L184"></span>
    return {'kind':'数值机制实验；非商用模型评测','cache_max_error':err,'wrong_rope_offset_error':bad,'online_softmax_error':tiled,'speculative':speculative_sample(np.array([.6,.3,.1]),np.array([.2,.5,.3])),'byte_bpe_roundtrip':bytes(x for t in encoded for x in t).decode('utf-8')}
<span id="L185"></span>
 
<span id="L186"></span>
if __name__=='__main__':
<span id="L187"></span>
    import json
<span id="L188"></span>
    print(json.dumps(run(),ensure_ascii=False,indent=2))
```

AI系统工程：从基础到内部  
[全书目录](../../contents.md) · [术语与符号](../../glossary.md) · [参考资料](../../sources.md)