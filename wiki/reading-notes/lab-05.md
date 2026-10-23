---
title: "压缩保真：状态与否定不能丢"
description: "AI系统工程：本地教学正文与可追溯图表"
---

拓展阅读


<span id="section-0"></span>


# 压缩保真：状态与否定不能丢

把原始任务标成结构化命题，与故意错误的压缩状态比较，检查缺失、确定性、执行状态和版本差异。

状态：自检已实际通过　·　环境：Python标准库　·　性质：合成/模拟教学实验  
[对应讲义 7.6](chapter-07.md#m-07-06)　·　[保存Python脚本](../../reading-notes/experiments/05_compaction_fidelity.py)


<span id="visual-reading"></span>



<span id="topic-1"></span>


## 沿着对象与状态理解本章

压缩最危险的不是少一句背景，而是把“未执行”写成“已完成”，把“禁止”写成“准备做”。先对照本图保留命题、版本、否定与未决状态，再考虑缩短多少Token。

下方图解的固定输入在“输入与适用条件”中声明。它用于解释本章机制，不与本章其他独立例子的数值暗中接续。


<span id="visual-F27"></span>

<span id="topic-2"></span>

<span id="topic-3"></span>

<span id="topic-4"></span>

<span id="topic-5"></span>

<span id="topic-6"></span>

<span id="topic-7"></span>


相关动态过程：[压缩要保留行动所依赖的事实](../visual/F27.md)。本节下文继续展示更具体的计算与工程边界。

继续看相关机制：[F24 · 任务状态不是聊天里的一句总结](../visual/F24.md)[O10 · 压缩、检索与Prompt Cache：三种不同的“省”](../visual/O10.md)


<span id="method"></span>


## 怎样观察与验证

错误样例会缺少public\_api，并出现4处字段变化。它不是自然语言理解器；真实摘要需先可靠抽取命题，并继续执行任务验证。


<span id="run"></span>


## 运行命令

```
python3 reading-notes/experiments/05_compaction_fidelity.py
```


<span id="code"></span>


## 完整教学代码


<span id="concept-intro-1"></span>


这里的patch指字段更新

本程序对结构化命题记录的字段做局部修改，以制造错误摘要；它不是图像分块，也不是修改源代码的diff。读取函数参数时，以该程序定义为准。

```
"""结构化命题保真检查。不是自然语言理解器，也不是 LLM 压缩实现。"""
from copy import deepcopy

CANONICAL = {
    "public_api": {"value":"unchanged", "certainty":"required", "version":"all"},
    "config_loaded": {"value":True, "certainty":"verified", "evidence":"T1"},
    "path_cause": {"value":"base_mismatch", "certainty":"hypothesis", "evidence":None},
    "patch": {"value":"not_applied", "certainty":"observed", "version":"v3"},
    "tests": {"value":"pending", "certainty":"observed", "version":"v3"},
}


def compare_claims(reference: dict, candidate: dict) -> dict:
    if not isinstance(reference,dict) or not isinstance(candidate,dict):
        raise TypeError("输入必须是结构化命题字典")
    missing = sorted(set(reference)-set(candidate))
    extra = sorted(set(candidate)-set(reference))
    changes=[]
    for key in sorted(set(reference)&set(candidate)):
        if not isinstance(reference[key],dict) or not isinstance(candidate[key],dict):
            raise TypeError("每条命题必须包含字段字典")
        for field in sorted(set(reference[key])|set(candidate[key])):
            if reference[key].get(field) != candidate[key].get(field):
                changes.append({"claim":key,"field":field,
                                "expected":reference[key].get(field),
                                "actual":candidate[key].get(field)})
    return {"preserved": not missing and not extra and not changes,
            "missing":missing,"extra":extra,"changed":changes}


def bad_summary() -> dict:
    wrong=deepcopy(CANONICAL)
    del wrong["public_api"]
    wrong["path_cause"]["certainty"]="verified"
    wrong["patch"]["value"]="applied"
    wrong["tests"]={"value":"passed","certainty":"observed","version":"v2"}
    return wrong


def self_test() -> None:
    assert compare_claims(CANONICAL,deepcopy(CANONICAL))["preserved"]
    result=compare_claims(CANONICAL,bad_summary())
    assert not result["preserved"]
    assert result["missing"] == ["public_api"]
    assert len(result["changed"]) == 4


def run_demo() -> dict:
    return {"性质":"人工标注命题上的确定性校验，不会自动判断自然语言",
            "基准":CANONICAL,"错误压缩":bad_summary(),
            "差异":compare_claims(CANONICAL,bad_summary()),
            "限制":"真实压缩仍需人工/模型抽取校准，以及继续执行任务的测试"}


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
  "性质": "人工标注命题上的确定性校验，不会自动判断自然语言",
  "基准": {
    "public_api": {
      "value": "unchanged",
      "certainty": "required",
      "version": "all"
    },
    "config_loaded": {
      "value": true,
      "certainty": "verified",
      "evidence": "T1"
    },
    "path_cause": {
      "value": "base_mismatch",
      "certainty": "hypothesis",
      "evidence": null
    },
    "patch": {
      "value": "not_applied",
      "certainty": "observed",
      "version": "v3"
    },
    "tests": {
      "value": "pending",
      "certainty": "observed",
      "version": "v3"
    }
  },
  "错误压缩": {
    "config_loaded": {
      "value": true,
      "certainty": "verified",
      "evidence": "T1"
    },
    "path_cause": {
      "value": "base_mismatch",
      "certainty": "verified",
      "evidence": null
    },
    "patch": {
      "value": "applied",
      "certainty": "observed",
      "version": "v3"
    },
    "tests": {
      "value": "passed",
      "certainty": "observed",
      "version": "v2"
    }
  },
  "差异": {
    "preserved": false,
    "missing": [
      "public_api"
    ],
    "extra": [],
    "changed": [
      {
        "claim": "patch",
        "field": "value",
        "expected": "not_applied",
        "actual": "applied"
      },
      {
        "claim": "path_cause",
        "field": "certainty",
        "expected": "hypothesis",
        "actual": "verified"
      },
      {
        "claim": "tests",
        "field": "value",
        "expected": "pending",
        "actual": "passed"
      },
      {
        "claim": "tests",
        "field": "version",
        "expected": "v3",
        "actual": "v2"
      }
    ]
  },
  "限制": "真实压缩仍需人工/模型抽取校准，以及继续执行任务的测试"
}
```

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)