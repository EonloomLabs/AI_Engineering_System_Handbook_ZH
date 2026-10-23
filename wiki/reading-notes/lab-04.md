---
title: "RRF与检索指标"
description: "AI系统工程：本地教学正文与可追溯图表"
---

拓展阅读


<span id="section-0"></span>


# RRF与检索指标

对合成排名融合，并计算Precision、Recall、单查询倒数排名和nDCG。相关性标签由教材人工给定。

状态：自检已实际通过　·　环境：Python标准库　·　性质：合成/模拟教学实验  
[对应讲义 8.16](chapter-08.md#m-08-16)　·　[保存Python脚本](../../reading-notes/experiments/04_retrieval.py)


<span id="visual-reading"></span>



<span id="topic-1"></span>


## 沿着对象与状态理解本章

检索排名只说明候选顺序，不说明事实已经成立。下图固定两份候选排名逐项融合，再加入版本与证据判断；如果答案需要两个条件，只召回其中一个还不够。

下方图解的固定输入在“输入与适用条件”中声明。它用于解释本章机制，不与本章其他独立例子的数值暗中接续。


<span id="visual-F29"></span>

<span id="topic-2"></span>

<span id="topic-3"></span>

<span id="topic-4"></span>

<span id="topic-5"></span>

<span id="topic-6"></span>

<span id="topic-7"></span>


相关动态过程：[从两个候选列表，走到可用证据](../visual/F29.md)。本节下文继续展示更具体的计算与工程边界。

继续看相关机制：[F28 · 检索先找候选，再判断能否回答](../visual/F28.md)[F35 · 读指标，先问它的分母是谁](../visual/F35.md)[F37 · 资料能影响模型，不代表获得了权限](../visual/F37.md)


<span id="method"></span>


## 怎样观察与验证


<span id="concept-intro-2"></span>


先认识这里的对象与符号

[Precision、Recall、MRR与nDCG](../concepts.md#concept-metrics)
:   精确率看返回结果中有多少相关；召回率看应找相关中找到了多少；MRR平均第一个正确项的排名倒数；nDCG考虑相关程度和排序位置并相对理想排序归一化。独立例：应找5篇，返回4篇其中3篇相关，精确率3/4，召回率3/5。不要把这两个分母互换。

需要A、B却只返回A、X、Y时，Precision@3为1/3，Recall@3为1/2。增加噪声或交换排序，观察不同指标反应。


<span id="run"></span>


## 运行命令

```
python3 reading-notes/experiments/04_retrieval.py
```


<span id="code"></span>


## 完整教学代码


<span id="concept-intro-1"></span>


先认识这里的对象与符号

[RRF：按排名融合](../concepts.md#concept-rrf)
:   RRF对某文档在每条召回路径上的排名r贡献1/(c+r)，再相加。c是平滑常数，r通常从1开始；没进入某条路径的候选不凭空获得该路贡献。独立例：c=10，某文档两路排名1、3，得1/11+1/13约0.167832。不是把BM25和余弦的原始分数相加。

```
"""合成排名上的 RRF、Precision、Recall、MRR 和 nDCG。"""
import math


def unique(seq):
    return list(dict.fromkeys(seq))


def rrf(rankings: list[list[str]], constant: float = 60.0) -> list[tuple[str, float]]:
    if not math.isfinite(constant) or constant < 0:
        raise ValueError("平滑常数必须非负且有限")
    scores = {}
    for ranking in rankings:
        for rank, doc in enumerate(unique(ranking), 1):
            scores[doc] = scores.get(doc, 0.0) + 1 / (constant + rank)
    return sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))


def metrics(ranking: list[str], relevance: dict[str, int], k: int) -> dict:
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ValueError("k 必须为正整数")
    if any(v < 0 for v in relevance.values()):
        raise ValueError("相关性等级不能为负")
    top = unique(ranking)[:k]
    relevant = {doc for doc, grade in relevance.items() if grade > 0}
    hits = sum(doc in relevant for doc in top)
    # 按请求的 k 作分母；结果不足 k 时空缺算未命中。
    precision = hits / k
    recall = hits / len(relevant) if relevant else None
    reciprocal_rank = next((1/i for i,d in enumerate(top,1) if d in relevant), 0.0)
    dcg = sum((2**relevance.get(doc,0)-1)/math.log2(i+1) for i,doc in enumerate(top,1))
    ideal = sorted(relevance.values(), reverse=True)[:k]
    idcg = sum((2**grade-1)/math.log2(i+1) for i,grade in enumerate(ideal,1))
    return {"precision_at_k": precision, "recall_at_k": recall,
            "reciprocal_rank_at_k": reciprocal_rank,
            "ndcg_at_k": dcg/idcg if idcg else None}


def self_test() -> None:
    m = metrics(["A","X","Y"], {"A":1,"B":1}, 3)
    assert m["precision_at_k"] == 1/3 and m["recall_at_k"] == 1/2
    assert metrics(["B","A"], {"A":1,"B":2},2)["ndcg_at_k"] == 1
    assert rrf([["A","A"],["B"]],0) == [("A",1.0),("B",1.0)]
    assert metrics([], {}, 3)["recall_at_k"] is None


def run_demo() -> dict:
    return {"性质":"人工相关性标签，非真实搜索基准",
            "融合":rrf([["A","B","C"],["B","D","A"]]),
            "缺少必要证据B":metrics(["A","X","Y"],{"A":1,"B":1},3),
            "说明":"单查询倒数排名；MRR需要在多个查询上取平均"}


if __name__ == "__main__":
    import json
    self_test()
    print(json.dumps(run_demo(), ensure_ascii=False, indent=2))
```


<span id="result"></span>


## 运行结果示例

以下结果由随包脚本产生。它们不是LLM或产品性能数据。

```
{
  "性质": "人工相关性标签，非真实搜索基准",
  "融合": [
    [
      "B",
      0.03252247488101534
    ],
    [
      "A",
      0.032266458495966696
    ],
    [
      "D",
      0.016129032258064516
    ],
    [
      "C",
      0.015873015873015872
    ]
  ],
  "缺少必要证据B": {
    "precision_at_k": 0.3333333333333333,
    "recall_at_k": 0.5,
    "reciprocal_rank_at_k": 1.0,
    "ndcg_at_k": 0.6131471927654584
  },
  "说明": "单查询倒数排名；MRR需要在多个查询上取平均"
}
```

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)