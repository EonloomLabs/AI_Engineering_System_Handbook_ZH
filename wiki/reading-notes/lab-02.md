---
title: "手算注意力与因果掩码"
description: "AI系统工程：本地教学正文与可追溯图表"
---

拓展阅读


<span id="section-0"></span>


# 手算注意力与因果掩码

计算稳定softmax、缩放点积注意力和Value加权。自检修改未来位置的Value，确认前面位置输出不受影响。

状态：自检已实际通过　·　环境：Python标准库　·　性质：合成/模拟教学实验  
[对应讲义 1.3](chapter-01.md#m-01-03)　·　[保存Python脚本](../../reading-notes/experiments/02_attention.py)


<span id="visual-reading"></span>



<span id="topic-1"></span>


## 沿着对象与状态理解本章

先在可见性表里选一个查询行，决定哪些Key位置允许参与；再看如何缩放和混合。多头改变表示的分组方式，位置旋转改变Q/K的比较，反向传播计算参数的影响，三者不是同一个步骤。

下方图解的固定输入在“输入与适用条件”中声明。它用于解释本章机制，不与本章其他独立例子的数值暗中接续。


<span id="visual-F12"></span>

<span id="topic-2"></span>

<span id="topic-3"></span>

<span id="topic-4"></span>

<span id="topic-5"></span>

<span id="topic-6"></span>

<span id="topic-7"></span>


相关动态过程：[Mask是可见性表，不是额外语义](../visual/F12.md)。本节下文继续展示更具体的计算与工程边界。

继续看相关机制：[F13 · 位置怎样进入数值计算](../visual/F13.md)[O01 · GQA/MQA：减少的是K/V组数](../visual/O01.md)[F15 · 梯度像坡度，学习率像迈步大小](../visual/F17.md)


<span id="method"></span>


## 怎样观察与验证

比较有无因果掩码，并改变分数差距。softmax([0,1,2])约为[0.0900,0.2447,0.6652]；这不是事实置信度。


<span id="run"></span>


## 运行命令

```
python3 reading-notes/experiments/02_attention.py
```


<span id="code"></span>


## 完整教学代码

```
"""小矩阵注意力、稳定 softmax 与因果掩码；所有数据为人工构造。"""
import math


def softmax(values: list[float], temperature: float = 1.0) -> list[float]:
    if not values or not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("需要非空分数和正有限温度")
    if any(math.isnan(x) or x == math.inf for x in values):
        raise ValueError("分数不可含 NaN 或正无穷")
    m = max(values)
    if m == -math.inf:
        raise ValueError("不能屏蔽全部候选")
    exps = [math.exp((x - m) / temperature) for x in values]
    total = sum(exps)
    return [x / total for x in exps]


def validate_matrix(a: list[list[float]], name: str) -> tuple[int, int]:
    if not a or not a[0] or any(len(row) != len(a[0]) for row in a):
        raise ValueError(f"{name} 必须是非空矩形矩阵")
    if any(not math.isfinite(x) for row in a for x in row):
        raise ValueError(f"{name} 必须全部有限")
    return len(a), len(a[0])


def attention(q, k, v, causal: bool = True):
    nq, dq = validate_matrix(q, "Q")
    nk, dk = validate_matrix(k, "K")
    nv, dv = validate_matrix(v, "V")
    if dq != dk or nk != nv or (causal and nq != nk):
        raise ValueError("维度不匹配；本演示因果模式要求相同序列长度")
    all_weights, outputs = [], []
    for i, query in enumerate(q):
        scores = [sum(a * b for a, b in zip(query, key)) / math.sqrt(dk) for key in k]
        if causal:
            scores = [s if j <= i else -math.inf for j, s in enumerate(scores)]
        weights = softmax(scores)
        all_weights.append(weights)
        outputs.append([sum(weights[j] * v[j][d] for j in range(nk)) for d in range(dv)])
    return all_weights, outputs


def self_test() -> None:
    assert abs(sum(softmax([1000, 1001, 1002])) - 1) < 1e-12
    q = k = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    v1, v2 = [[10.0], [20.0], [30.0]], [[10.0], [20.0], [9999.0]]
    w, a = attention(q, k, v1)
    _, b = attention(q, k, v2)
    assert a[:2] == b[:2], "未来 Value 不应影响前两个位置"
    assert w[0][1:] == [0.0, 0.0]
    assert w[1][2] == 0.0
    assert a[2] != b[2]


def run_demo() -> dict:
    q = k = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    weights, output = attention(q, k, [[10.0], [20.0], [30.0]])
    p = softmax([0, 1, 2])
    return {"性质": "原创小矩阵，无训练模型", "softmax_0_1_2": p,
            "加权10_20_30": sum(a*b for a,b in zip(p,[10,20,30])),
            "因果权重": weights, "输出": output}


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
  "性质": "原创小矩阵，无训练模型",
  "softmax_0_1_2": [
    0.09003057317038046,
    0.24472847105479764,
    0.6652409557748218
  ],
  "加权10_20_30": 25.75210382604441,
  "因果权重": [
    [
      1.0,
      0.0,
      0.0
    ],
    [
      0.3302384506733431,
      0.6697615493266569,
      0.0
    ],
    [
      0.2482550782577231,
      0.2482550782577231,
      0.5034898434845538
    ]
  ],
  "输出": [
    [
      10.0
    ],
    [
      16.697615493266568
    ],
    [
      22.55234765226831
    ]
  ]
}
```

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)