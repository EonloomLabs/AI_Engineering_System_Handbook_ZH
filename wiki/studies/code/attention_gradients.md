---
title: "attention_gradients.py"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# attention\_gradients.py

解析反向传播。对应第31章。依赖：NumPy。

解析梯度与有限差分；不是任务目标正确性的充分证明。[阅读运行说明](../experiments.md) / [查看实测结果](../results.md)

[原始Python文件](../../../studies/labs/attention_gradients.py) · 65行

```

<span id="L1"></span>
"""单头注意力的完整解析反向；NumPy float64；不是GPU算子。"""
<span id="L2"></span>
from __future__ import annotations
<span id="L3"></span>
import numpy as np
<span id="L4"></span>
 
<span id="L5"></span>
 
<span id="L6"></span>
def forward(q, k, v, allowed=None):
<span id="L7"></span>
    q, k, v = [np.asarray(x, dtype=np.float64) for x in (q, k, v)]
<span id="L8"></span>
    if any(x.ndim != 2 for x in (q,k,v)) or q.shape[1] != k.shape[1] or k.shape[0] != v.shape[0]:
<span id="L9"></span>
        raise ValueError('Q/K/V形状不兼容')
<span id="L10"></span>
    if min(q.shape + k.shape + v.shape) < 1 or not all(np.isfinite(x).all() for x in (q,k,v)):
<span id="L11"></span>
        raise ValueError('只支持有限非空张量')
<span id="L12"></span>
    scores = q @ k.T / np.sqrt(q.shape[1])
<span id="L13"></span>
    if allowed is None:
<span id="L14"></span>
        allowed = np.ones_like(scores, dtype=bool)
<span id="L15"></span>
    allowed = np.asarray(allowed, dtype=bool)
<span id="L16"></span>
    if allowed.shape != scores.shape or not allowed.any(axis=1).all():
<span id="L17"></span>
        raise ValueError('掩码形状错误或存在全掩码行')
<span id="L18"></span>
    scores = np.where(allowed, scores, -np.inf)
<span id="L19"></span>
    exp = np.exp(scores - scores.max(axis=1, keepdims=True))
<span id="L20"></span>
    p = exp / exp.sum(axis=1, keepdims=True)
<span id="L21"></span>
    return p @ v, (q, k, v, p, allowed)
<span id="L22"></span>
 
<span id="L23"></span>
 
<span id="L24"></span>
def backward(upstream, cache):
<span id="L25"></span>
    q, k, v, p, allowed = cache
<span id="L26"></span>
    upstream = np.asarray(upstream, dtype=np.float64)
<span id="L27"></span>
    if upstream.shape != (q.shape[0], v.shape[1]) or not np.isfinite(upstream).all():
<span id="L28"></span>
        raise ValueError('上游梯度形状或数值错误')
<span id="L29"></span>
    dp = upstream @ v.T
<span id="L30"></span>
    ds = p * (dp - (dp * p).sum(axis=1, keepdims=True))
<span id="L31"></span>
    ds = np.where(allowed, ds, 0.0)
<span id="L32"></span>
    scale = np.sqrt(q.shape[1])
<span id="L33"></span>
    return ds @ k / scale, ds.T @ q / scale, p.T @ upstream
<span id="L34"></span>
 
<span id="L35"></span>
 
<span id="L36"></span>
def finite_difference(q, k, v, upstream, allowed=None, eps=1e-6):
<span id="L37"></span>
    originals = [np.array(x, dtype=np.float64, copy=True) for x in (q,k,v)]
<span id="L38"></span>
    grads=[]
<span id="L39"></span>
    for variable in range(3):
<span id="L40"></span>
        grad = np.zeros_like(originals[variable])
<span id="L41"></span>
        for index in np.ndindex(grad.shape):
<span id="L42"></span>
            plus = [x.copy() for x in originals]
<span id="L43"></span>
            minus = [x.copy() for x in originals]
<span id="L44"></span>
            plus[variable][index] += eps
<span id="L45"></span>
            minus[variable][index] -= eps
<span id="L46"></span>
            fp = float(np.sum(forward(*plus, allowed)[0] * upstream))
<span id="L47"></span>
            fm = float(np.sum(forward(*minus, allowed)[0] * upstream))
<span id="L48"></span>
            grad[index] = (fp - fm) / (2*eps)
<span id="L49"></span>
        grads.append(grad)
<span id="L50"></span>
    return tuple(grads)
<span id="L51"></span>
 
<span id="L52"></span>
 
<span id="L53"></span>
def run():
<span id="L54"></span>
    rng=np.random.default_rng(42)
<span id="L55"></span>
    q,k,v,g=rng.normal(size=(3,3)),rng.normal(size=(4,3)),rng.normal(size=(4,2)),rng.normal(size=(3,2))
<span id="L56"></span>
    allowed=np.arange(4)[None,:] <= np.arange(3)[:,None]+1
<span id="L57"></span>
    _, cache=forward(q,k,v,allowed)
<span id="L58"></span>
    analytic=backward(g,cache)
<span id="L59"></span>
    numerical=finite_difference(q,k,v,g,allowed)
<span id="L60"></span>
    return {'kind':'解析反向与有限差分；非训练能力/非GPU性能评测',
<span id="L61"></span>
            'max_absolute_errors':{name:float(np.max(np.abs(a-n))) for name,a,n in zip(('dQ','dK','dV'),analytic,numerical)}}
<span id="L62"></span>
 
<span id="L63"></span>
if __name__=='__main__':
<span id="L64"></span>
    import json
<span id="L65"></span>
    print(json.dumps(run(),ensure_ascii=False,indent=2))
```

AI系统工程：从基础到内部  
[全书目录](../../contents.md) · [术语与符号](../../glossary.md) · [参考资料](../../sources.md)