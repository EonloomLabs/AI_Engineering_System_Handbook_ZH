"""单头注意力的完整解析反向；NumPy float64；不是GPU算子。"""
from __future__ import annotations
import numpy as np


def forward(q, k, v, allowed=None):
    q, k, v = [np.asarray(x, dtype=np.float64) for x in (q, k, v)]
    if any(x.ndim != 2 for x in (q,k,v)) or q.shape[1] != k.shape[1] or k.shape[0] != v.shape[0]:
        raise ValueError('Q/K/V形状不兼容')
    if min(q.shape + k.shape + v.shape) < 1 or not all(np.isfinite(x).all() for x in (q,k,v)):
        raise ValueError('只支持有限非空张量')
    scores = q @ k.T / np.sqrt(q.shape[1])
    if allowed is None:
        allowed = np.ones_like(scores, dtype=bool)
    allowed = np.asarray(allowed, dtype=bool)
    if allowed.shape != scores.shape or not allowed.any(axis=1).all():
        raise ValueError('掩码形状错误或存在全掩码行')
    scores = np.where(allowed, scores, -np.inf)
    exp = np.exp(scores - scores.max(axis=1, keepdims=True))
    p = exp / exp.sum(axis=1, keepdims=True)
    return p @ v, (q, k, v, p, allowed)


def backward(upstream, cache):
    q, k, v, p, allowed = cache
    upstream = np.asarray(upstream, dtype=np.float64)
    if upstream.shape != (q.shape[0], v.shape[1]) or not np.isfinite(upstream).all():
        raise ValueError('上游梯度形状或数值错误')
    dp = upstream @ v.T
    ds = p * (dp - (dp * p).sum(axis=1, keepdims=True))
    ds = np.where(allowed, ds, 0.0)
    scale = np.sqrt(q.shape[1])
    return ds @ k / scale, ds.T @ q / scale, p.T @ upstream


def finite_difference(q, k, v, upstream, allowed=None, eps=1e-6):
    originals = [np.array(x, dtype=np.float64, copy=True) for x in (q,k,v)]
    grads=[]
    for variable in range(3):
        grad = np.zeros_like(originals[variable])
        for index in np.ndindex(grad.shape):
            plus = [x.copy() for x in originals]
            minus = [x.copy() for x in originals]
            plus[variable][index] += eps
            minus[variable][index] -= eps
            fp = float(np.sum(forward(*plus, allowed)[0] * upstream))
            fm = float(np.sum(forward(*minus, allowed)[0] * upstream))
            grad[index] = (fp - fm) / (2*eps)
        grads.append(grad)
    return tuple(grads)


def run():
    rng=np.random.default_rng(42)
    q,k,v,g=rng.normal(size=(3,3)),rng.normal(size=(4,3)),rng.normal(size=(4,2)),rng.normal(size=(3,2))
    allowed=np.arange(4)[None,:] <= np.arange(3)[:,None]+1
    _, cache=forward(q,k,v,allowed)
    analytic=backward(g,cache)
    numerical=finite_difference(q,k,v,g,allowed)
    return {'kind':'解析反向与有限差分；非训练能力/非GPU性能评测',
            'max_absolute_errors':{name:float(np.max(np.abs(a-n))) for name,a,n in zip(('dQ','dK','dV'),analytic,numerical)}}

if __name__=='__main__':
    import json
    print(json.dumps(run(),ensure_ascii=False,indent=2))
