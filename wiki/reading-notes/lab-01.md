---
title: "教学 BPE：字符怎样合并成 Token"
description: "AI系统工程：本地教学正文与可追溯图表"
---

拓展阅读


<span id="section-0"></span>


# 教学 BPE：字符怎样合并成 Token

观察一组简单语料如何决定字符对合并。训练规则与应用规则分开，保留原文本可逆。例子刻意不实现真实模型的字节编码、特殊Token和预处理。

状态：自检已实际通过　·　环境：Python标准库　·　性质：合成/模拟教学实验  
[对应讲义 1.2](chapter-01.md#m-01-02)　·　[保存Python脚本](../../reading-notes/experiments/01_tokenization.py)


<span id="visual-reading"></span>



<span id="topic-1"></span>


## 沿着对象与状态理解本章

先沿着实际对象追踪：用户文字不是消息包，消息包不是Token数组，编号也不是Embedding。把这四种对象分别认出来，后面的shape和API角色才有落点。下图的词表是独立教学约定；不要把它当成所有Tokenizer的真实结果。

下方图解的固定输入在“输入与适用条件”中声明。它用于解释本章机制，不与本章其他独立例子的数值暗中接续。


<span id="visual-F03"></span>

<span id="topic-2"></span>

<span id="topic-3"></span>

<span id="topic-4"></span>

<span id="topic-5"></span>

<span id="topic-6"></span>

<span id="topic-7"></span>


相关动态过程：[文字、字节、Token、编号是四件事](../visual/F03.md)。本节下文继续展示更具体的计算与工程边界。

继续看相关机制：[F04 · 组批没有把两句话混成一句](../visual/F04.md)[F05 · Embedding是查一行，不是把编号转二进制](../visual/F05.md)[F18 · 一次输入如何连着预测，直到结束](../visual/F15.md)


<span id="method"></span>


## 怎样观察与验证

先运行默认样例，再改变语料或合并次数。相同文本可能得到不同教学Token数，说明计数依赖分词器。不要把结果用于商业模型计费。


<span id="run"></span>


## 运行命令

```
python3 reading-notes/experiments/01_tokenization.py
```


<span id="code"></span>


## 完整教学代码

```
"""教学级字符 BPE：只演示合并与编码，不是商业模型的 Tokenizer。"""
from collections import Counter
from typing import Iterable


def apply_merge(tokens: list[str], pair: tuple[str, str]) -> list[str]:
    out, i = [], 0
    while i < len(tokens):
        if i + 1 < len(tokens) and (tokens[i], tokens[i + 1]) == pair:
            out.append(tokens[i] + tokens[i + 1])
            i += 2
        else:
            out.append(tokens[i])
            i += 1
    return out


def train_bpe(texts: Iterable[str], num_merges: int = 8) -> list[tuple[str, str]]:
    if isinstance(texts, (str, bytes)):
        raise TypeError("texts 必须是字符串集合，不是单个字符串")
    if not isinstance(num_merges, int) or isinstance(num_merges, bool) or num_merges < 0:
        raise ValueError("num_merges 必须是非负整数")
    data = list(texts)
    if any(not isinstance(t, str) for t in data):
        raise TypeError("训练样本必须是字符串")
    corpus = [list(t) for t in data]
    merges = []
    for _ in range(num_merges):
        counts = Counter(pair for seq in corpus for pair in zip(seq, seq[1:]))
        if not counts:
            break
        # 相同频次时固定排序，保证演示可复现。
        pair = min(counts, key=lambda p: (-counts[p], p))
        if counts[pair] < 2:
            break
        merges.append(pair)
        corpus = [apply_merge(seq, pair) for seq in corpus]
    return merges


def encode(text: str, merges: list[tuple[str, str]]) -> list[str]:
    if not isinstance(text, str):
        raise TypeError("text 必须是字符串")
    result = list(text)
    for pair in merges:
        result = apply_merge(result, pair)
    return result


def self_test() -> None:
    merges = train_bpe(["路径路径", "路径过滤", "路径规范"], 5)
    for text in ["路径过滤", "未知字符 x\n", ""]:
        assert "".join(encode(text, merges)) == text
    assert len(encode("路径路径", merges)) < len("路径路径")
    assert train_bpe([], 3) == []
    try:
        train_bpe("错误输入")
    except TypeError:
        pass
    else:
        raise AssertionError("应拒绝单个字符串作为语料集合")


def run_demo() -> dict:
    texts = ["exclude_paths", "exclude_path", "exclude_files", "include_paths"]
    merges = train_bpe(texts, 10)
    sample = "exclude_paths"
    tokens = encode(sample, merges)
    return {"性质": "字符级教学 BPE，非真实模型计费", "合并规则": merges,
            "文本": sample, "字符数": len(sample), "教学Token": tokens,
            "教学Token数": len(tokens), "可逆": "".join(tokens) == sample}


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
  "性质": "字符级教学 BPE，非真实模型计费",
  "合并规则": [
    [
      "c",
      "l"
    ],
    [
      "cl",
      "u"
    ],
    [
      "clu",
      "d"
    ],
    [
      "clud",
      "e"
    ],
    [
      "clude",
      "_"
    ],
    [
      "a",
      "t"
    ],
    [
      "at",
      "h"
    ],
    [
      "clude_",
      "p"
    ],
    [
      "clude_p",
      "ath"
    ],
    [
      "e",
      "x"
    ]
  ],
  "文本": "exclude_paths",
  "字符数": 13,
  "教学Token": [
    "ex",
    "clude_path",
    "s"
  ],
  "教学Token数": 3,
  "可逆": true
}
```

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)