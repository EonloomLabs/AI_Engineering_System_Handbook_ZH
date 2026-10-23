---
title: "KV缓存估算与前缀复用"
description: "AI系统工程：本地教学正文与可追溯图表"
---

拓展阅读


<span id="section-0"></span>


# KV缓存估算与前缀复用

使用注明条件的标准注意力估算式，比较8与32个KV头。另用离散列表演示共同前缀，不模拟厂商缓存服务器。

状态：自检已实际通过　·　环境：Python标准库　·　性质：合成/模拟教学实验  
[对应讲义 3.3](chapter-03.md#m-03-03)　·　[保存Python脚本](../../reading-notes/experiments/03_cache_budget.py)


<span id="visual-reading"></span>



<span id="topic-1"></span>


## 沿着对象与状态理解本章

这里有三个不同的存储问题：KV缓存跨轮保留历史；FlashAttention安排单次注意力的中间读写；PagedAttention管理物理缓存块。动画分别给出具体数据，避免将三种节约误认为都减少了相同计算。

下方图解的固定输入在“输入与适用条件”中声明。它用于解释本章机制，不与本章其他独立例子的数值暗中接续。


<span id="visual-O04"></span>

<span id="topic-2"></span>

<span id="topic-3"></span>

<span id="topic-4"></span>

<span id="topic-5"></span>

<span id="topic-6"></span>

<span id="topic-7"></span>


相关动态过程：[FlashAttention：一边读一边累计，不攒整张表](../visual/O04.md)。本节下文继续展示更具体的计算与工程边界。

继续看相关机制：[F19 · KV Cache：留下算过的，不省掉该读的](../visual/F16.md)[O01 · GQA/MQA：减少的是K/V组数](../visual/O01.md)[O05 · PagedAttention：逻辑连续，物理可以分块](../visual/O05.md)


<span id="method"></span>


## 怎样观察与验证

默认例子分别得到1与4 GiB。加入批大小后观察线性项；真实内存还含权重、分配器与其他状态，特殊架构可能不适用。


<span id="run"></span>


## 运行命令

```
python3 reading-notes/experiments/03_cache_budget.py
```


<span id="code"></span>


## 完整教学代码

```
"""标准注意力 KV 缓存估算与前缀匹配；不是厂商计费器。"""
from typing import Sequence, TypeVar
T = TypeVar("T")


def kv_bytes(layers: int, batch: int, length: int, kv_heads: int,
             head_dim: int, bytes_per_element: int) -> int:
    args = [layers, batch, length, kv_heads, head_dim, bytes_per_element]
    if any(not isinstance(x, int) or isinstance(x, bool) or x <= 0 for x in args):
        raise ValueError("所有参数必须是正整数")
    return 2 * layers * batch * length * kv_heads * head_dim * bytes_per_element


def common_prefix(a: Sequence[T], b: Sequence[T]) -> int:
    count = 0
    for x, y in zip(a, b):
        if x != y:
            break
        count += 1
    return count


def self_test() -> None:
    assert kv_bytes(32, 1, 8192, 8, 128, 2) == 1024**3
    assert kv_bytes(32, 1, 8192, 32, 128, 2) == 4 * 1024**3
    assert common_prefix([1,2,3], [1,2,4]) == 2
    assert common_prefix([], [1]) == 0
    assert common_prefix([1,2], [9,1,2]) == 0


def run_demo() -> dict:
    base = ["规则", "工具", "任务A"]
    return {"性质": "简化公式，不含分配器和其他状态，不适用所有架构",
            "8个KV头_GiB": kv_bytes(32,1,8192,8,128,2)/1024**3,
            "32个KV头_GiB": kv_bytes(32,1,8192,32,128,2)/1024**3,
            "仅尾部变化_共同前缀项": common_prefix(base,["规则","工具","任务B"]),
            "首部插入变化_共同前缀项": common_prefix(base,["新时间","规则","工具","任务B"]),
            "限制": "共同前缀项不是实际缓存Token；产品还有阈值和其他条件"}


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
  "性质": "简化公式，不含分配器和其他状态，不适用所有架构",
  "8个KV头_GiB": 1.0,
  "32个KV头_GiB": 4.0,
  "仅尾部变化_共同前缀项": 2,
  "首部插入变化_共同前缀项": 0,
  "限制": "共同前缀项不是实际缓存Token；产品还有阈值和其他条件"
}
```

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)