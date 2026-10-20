"""合成样本评测：pass@k、独立重复假设、配对Bootstrap、成功成本。"""
import math
import random


def pass_at_k(n: int, c: int, k: int) -> float:
    if any(not isinstance(x,int) or isinstance(x,bool) for x in [n,c,k]):
        raise TypeError("n/c/k必须是整数")
    if n<=0 or not 0<=c<=n or not 1<=k<=n:
        raise ValueError("要求 n>0, 0<=c<=n, 1<=k<=n")
    return 1.0 if n-c<k else 1-math.comb(n-c,k)/math.comb(n,k)


def repeated_probabilities(p: float,k: int) -> dict:
    if not math.isfinite(p) or not 0<=p<=1 or not isinstance(k,int) or k<=0:
        raise ValueError("p需在[0,1]，k需为正整数")
    return {"at_least_one":1-(1-p)**k,"all_success":p**k}


def paired_bootstrap(old: list[int], new: list[int], samples: int=2000, seed: int=17) -> dict:
    if not old or len(old)!=len(new) or any(x not in (0,1) for x in old+new):
        raise ValueError("需要等长非空的0/1配对结果")
    if not isinstance(samples,int) or samples<100:
        raise ValueError("演示至少使用100次重采样")
    rng=random.Random(seed); n=len(old)
    diffs=[b-a for a,b in zip(old,new)]
    estimates=sorted(sum(diffs[rng.randrange(n)] for _ in range(n))/n for _ in range(samples))
    return {"difference":sum(diffs)/n,"percentile_95_interval":[estimates[int(.025*(samples-1))],estimates[int(.975*(samples-1))]],
            "assumption":"按任务配对重采样；不是对真实产品的显著性结论"}


def cost_per_success(costs: list[float], successes: list[int]) -> float | None:
    if len(costs)!=len(successes) or any(not math.isfinite(x) or x<0 for x in costs):
        raise ValueError("成本需有限非负且与结果等长")
    if any(x not in (0,1) for x in successes):
        raise ValueError("成功标记需为0/1")
    total=sum(successes)
    return sum(costs)/total if total else None


def self_test() -> None:
    assert abs(pass_at_k(10,2,1)-.2)<1e-12
    assert pass_at_k(10,0,3)==0 and pass_at_k(10,10,3)==1
    p=repeated_probabilities(.8,3)
    assert abs(p["at_least_one"]-.992)<1e-12
    assert abs(p["all_success"]-.512)<1e-12
    assert cost_per_success([1,2,3],[1,0,1])==3
    assert cost_per_success([1],[0]) is None
    assert paired_bootstrap([1,0],[1,0])["percentile_95_interval"]==[0.0,0.0]


def run_demo() -> dict:
    old=[1,1,0,1,0,1,0,1,1,0]
    new=[1,1,1,1,0,1,1,1,0,1]
    return {"性质":"全部结果为合成数据；费用单位是假想单位",
            "独立p08_k3":repeated_probabilities(.8,3),
            "n10_c2_k3":pass_at_k(10,2,3),"配对比较":paired_bootstrap(old,new),
            "含失败成本的每成功任务成本":cost_per_success([1.0]*10,new)}


if __name__ == "__main__":
    import json
    self_test()
    print(json.dumps(run_demo(),ensure_ascii=False,indent=2))
