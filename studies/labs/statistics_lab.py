"""合成数据上的统计方法；不是任何产品、模型或技能的实测收益。"""
import math,random


def pass_at_k(n,c,k):
    if not (isinstance(n,int) and isinstance(c,int) and isinstance(k,int) and n>=k>=1 and 0<=c<=n):raise ValueError('n/c/k无效')
    return 1. if n-c<k else 1-math.comb(n-c,k)/math.comb(n,k)


def paired_task_bootstrap(old,new,n_boot=4000,seed=17):
    """每行是同一任务的重复试验；整行抽样，不能把相关重复当成新任务。"""
    if len(old)!=len(new) or len(old)<2:raise ValueError('至少两个配对任务')
    if any(not row or any(x not in (0,1) for x in row) for row in old+new):raise ValueError('仅接受非空0/1任务结果')
    diffs=[sum(b)/len(b)-sum(a)/len(a) for a,b in zip(old,new)];rng=random.Random(seed);n=len(diffs)
    values=sorted(sum(diffs[rng.randrange(n)] for _ in range(n))/n for _ in range(n_boot))
    return {'difference':sum(diffs)/n,'interval_95':[values[int(.025*(n_boot-1))],values[int(.975*(n_boot-1))]],'resampling_unit':'task'}


def mcnemar_exact(b,c):
    if min(b,c)<0:raise ValueError('不一致计数不能为负')
    n=b+c
    return 1. if n==0 else min(1.,2*sum(math.comb(n,k) for k in range(min(b,c)+1))/(2**n))


def wilson(success,n,z=1.95996398454):
    if n<=0 or not 0<=success<=n:raise ValueError('计数无效')
    p=success/n;den=1+z*z/n;center=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [center-half,center+half]


def run():
    old=[[1,1,0],[0,1,0],[1,1,1],[0,0,1],[1,0,1],[0,1,0]]
    new=[[1,1,1],[1,1,0],[1,0,1],[1,0,1],[1,1,1],[0,1,1]]
    return {'kind':'合成评测数据','bootstrap':paired_task_bootstrap(old,new),'pass_at_3':pass_at_k(10,2,3),'wilson_8_of_10':wilson(8,10),'mcnemar_b1_c4':mcnemar_exact(1,4),'independent_p08_all3':.8**3}
