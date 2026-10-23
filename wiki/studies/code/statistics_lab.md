---
title: "statistics_lab.py"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# statistics\_lab.py

配对评测统计。对应第19章。依赖：标准库。

全部输入为合成数据；不能当作产品性能结论。[阅读运行说明](../experiments.md) / [查看实测结果](../results.md)

[原始Python文件](../../../studies/labs/statistics_lab.py) · 35行

```

<span id="L1"></span>
"""合成数据上的统计方法；不是任何产品、模型或技能的实测收益。"""
<span id="L2"></span>
import math,random
<span id="L3"></span>
 
<span id="L4"></span>
 
<span id="L5"></span>
def pass_at_k(n,c,k):
<span id="L6"></span>
    if not (isinstance(n,int) and isinstance(c,int) and isinstance(k,int) and n>=k>=1 and 0<=c<=n):raise ValueError('n/c/k无效')
<span id="L7"></span>
    return 1. if n-c<k else 1-math.comb(n-c,k)/math.comb(n,k)
<span id="L8"></span>
 
<span id="L9"></span>
 
<span id="L10"></span>
def paired_task_bootstrap(old,new,n_boot=4000,seed=17):
<span id="L11"></span>
    """每行是同一任务的重复试验；整行抽样，不能把相关重复当成新任务。"""
<span id="L12"></span>
    if len(old)!=len(new) or len(old)<2:raise ValueError('至少两个配对任务')
<span id="L13"></span>
    if any(not row or any(x not in (0,1) for x in row) for row in old+new):raise ValueError('仅接受非空0/1任务结果')
<span id="L14"></span>
    diffs=[sum(b)/len(b)-sum(a)/len(a) for a,b in zip(old,new)];rng=random.Random(seed);n=len(diffs)
<span id="L15"></span>
    values=sorted(sum(diffs[rng.randrange(n)] for _ in range(n))/n for _ in range(n_boot))
<span id="L16"></span>
    return {'difference':sum(diffs)/n,'interval_95':[values[int(.025*(n_boot-1))],values[int(.975*(n_boot-1))]],'resampling_unit':'task'}
<span id="L17"></span>
 
<span id="L18"></span>
 
<span id="L19"></span>
def mcnemar_exact(b,c):
<span id="L20"></span>
    if min(b,c)<0:raise ValueError('不一致计数不能为负')
<span id="L21"></span>
    n=b+c
<span id="L22"></span>
    return 1. if n==0 else min(1.,2*sum(math.comb(n,k) for k in range(min(b,c)+1))/(2**n))
<span id="L23"></span>
 
<span id="L24"></span>
 
<span id="L25"></span>
def wilson(success,n,z=1.95996398454):
<span id="L26"></span>
    if n<=0 or not 0<=success<=n:raise ValueError('计数无效')
<span id="L27"></span>
    p=success/n;den=1+z*z/n;center=(p+z*z/(2*n))/den
<span id="L28"></span>
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
<span id="L29"></span>
    return [center-half,center+half]
<span id="L30"></span>
 
<span id="L31"></span>
 
<span id="L32"></span>
def run():
<span id="L33"></span>
    old=[[1,1,0],[0,1,0],[1,1,1],[0,0,1],[1,0,1],[0,1,0]]
<span id="L34"></span>
    new=[[1,1,1],[1,1,0],[1,0,1],[1,0,1],[1,1,1],[0,1,1]]
<span id="L35"></span>
    return {'kind':'合成评测数据','bootstrap':paired_task_bootstrap(old,new),'pass_at_3':pass_at_k(10,2,3),'wilson_8_of_10':wilson(8,10),'mcnemar_b1_c4':mcnemar_exact(1,4),'independent_p08_all3':.8**3}
```

AI系统工程：从基础到内部  
[全书目录](../../contents.md) · [术语与符号](../../glossary.md) · [参考资料](../../sources.md)