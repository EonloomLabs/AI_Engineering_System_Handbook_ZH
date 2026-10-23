---
title: "成功率、配对比较与真实成本口径"
description: "AI系统工程：本地教学正文与可追溯图表"
---

拓展阅读


<span id="section-0"></span>


# 成功率、配对比较与真实成本口径

计算pass@k、独立重复假设下的至少一次与全部成功概率，并对合成配对任务做Bootstrap示范。

状态：自检已实际通过　·　环境：Python标准库　·　性质：合成/模拟教学实验  
[对应讲义 12.11](chapter-12.md#m-12-11)　·　[保存Python脚本](../../reading-notes/experiments/08_evaluation.py)


<span id="visual-reading"></span>



<span id="topic-1"></span>


## 沿着对象与状态理解本章

两个平均成功率之间的差值，不能告诉你哪些题退化。先看同题配对表：两边都成功、新版独胜、旧版独胜、两边都失败，再看成本、方差和评分器误差。

下方图解的固定输入在“输入与适用条件”中声明。它用于解释本章机制，不与本章其他独立例子的数值暗中接续。


<span id="visual-F36"></span>

<span id="topic-2"></span>

<span id="topic-3"></span>

<span id="topic-4"></span>

<span id="topic-5"></span>

<span id="topic-6"></span>

<span id="topic-7"></span>


相关动态过程：[涨了10个百分点，为什么还不能急着下结论？](../visual/F36.md)。本节下文继续展示更具体的计算与工程边界。

继续看相关机制：[F35 · 读指标，先问它的分母是谁](../visual/F35.md)[O12 · 模型路由：便宜一次，不一定便宜一项成功任务](../visual/O12.md)


<span id="method"></span>


## 怎样观察与验证

p=0.8、k=3得到0.992与0.512。所有任务结果和费用是虚构的；区间不是对任何产品的统计结论。


<span id="run"></span>


## 运行命令

```
python3 reading-notes/experiments/08_evaluation.py
```


<span id="code"></span>


## 完整教学代码


<span id="concept-intro-1"></span>


先认识这里的对象与符号

[pass@k与pass^k](../concepts.md#concept-passk)
:   pass@k类指标通常关心k次尝试至少一次成功；pass^k类指标强调多次全成功。具体估计口径看基准，不能把一次成功后停止与每次都可靠混为一谈。独立同概率假设p=0.8，3次至少一成=0.992，3次全成=0.512。真实任务相关或难度不同则需另算。

```
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
```


<span id="result"></span>


## 运行结果示例

以下结果由随包脚本产生。它们不是LLM或产品性能数据。

```
{
  "性质": "全部结果为合成数据；费用单位是假想单位",
  "独立p08_k3": {
    "at_least_one": 0.992,
    "all_success": 0.5120000000000001
  },
  "n10_c2_k3": 0.5333333333333333,
  "配对比较": {
    "difference": 0.2,
    "percentile_95_interval": [
      -0.2,
      0.6
    ],
    "assumption": "按任务配对重采样；不是对真实产品的显著性结论"
  },
  "含失败成本的每成功任务成本": 1.25
}
```

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)