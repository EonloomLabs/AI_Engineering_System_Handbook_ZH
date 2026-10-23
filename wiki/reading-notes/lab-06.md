---
title: "记忆范围、版本、过期与冲突"
description: "AI系统工程：本地教学正文与可追溯图表"
---

拓展阅读


<span id="section-0"></span>


# 记忆范围、版本、过期与冲突

在进程内保存带证据的记忆，按项目与版本查询，排除过期内容，遇到相反结论返回冲突而非擅自择一。

状态：自检已实际通过　·　环境：Python标准库　·　性质：合成/模拟教学实验  
[对应讲义 9.1](chapter-09.md#m-09-01)　·　[保存Python脚本](../../reading-notes/experiments/06_memory_lifecycle.py)


<span id="visual-reading"></span>



<span id="topic-1"></span>


## 沿着对象与状态理解本章

记忆必须回答两个时间问题：事实什么时候生效，系统什么时候知道。下图用超时配置30秒变20秒追踪来源、有效时间和过期，避免把旧知识以熟悉的口吻重复出来。

下方图解的固定输入在“输入与适用条件”中声明。它用于解释本章机制，不与本章其他独立例子的数值暗中接续。


<span id="visual-F31"></span>

<span id="topic-2"></span>

<span id="topic-3"></span>

<span id="topic-4"></span>

<span id="topic-5"></span>

<span id="topic-6"></span>

<span id="topic-7"></span>


相关动态过程：[长期记忆不是永远正确的小纸条](../visual/F31.md)。本节下文继续展示更具体的计算与工程边界。

继续看相关机制：[F27 · 压缩要保留行动所依赖的事实](../visual/F27.md)[F29 · 从两个候选列表，走到可用证据](../visual/F29.md)


<span id="method"></span>


## 怎样观察与验证

固定教学日期为2026-10-17。修改项目或版本观察隔离；新增冲突证据后应返回conflict。此脚本不访问真实用户记忆。


<span id="run"></span>


## 运行命令

```
python3 reading-notes/experiments/06_memory_lifecycle.py
```


<span id="code"></span>


## 完整教学代码


<span id="concept-intro-1"></span>


先认识这里的对象与符号

[OAuth、scope与授权](../concepts.md#concept-oauth)
:   在授权场景，OAuth使应用能按授权取得访问凭据；scope声明一类访问范围，资源服务仍应检查具体权限。在记忆或任务场景，scope又可只表示适用范围，不能混成登录凭据。获准“读取日历”不等于获准删除所有事件；连接成功也不证明操作被批准。

```
"""作用域、版本、证据、到期与冲突演示；所有记忆仅在本进程内。"""
from dataclasses import dataclass, asdict
from datetime import date


@dataclass(frozen=True)
class Memory:
    key: str
    scope: str
    version: str
    value: str
    evidence: tuple[str, ...]
    status: str = "verified"
    expires: date | None = None

    def __post_init__(self):
        if not all([self.key,self.scope,self.version,self.value]):
            raise ValueError("key/scope/version/value 不能为空")
        if self.status not in {"candidate","verified","retired"}:
            raise ValueError("未知状态")
        if self.status == "verified" and not self.evidence:
            raise ValueError("已验证记忆必须带证据引用")


class Store:
    def __init__(self):
        self.items: list[Memory] = []

    def add(self, memory: Memory) -> None:
        if memory not in self.items:
            self.items.append(memory)

    def query(self, key: str, scope: str, version: str, now: date) -> dict:
        matches=[m for m in self.items if m.key==key and m.scope==scope
                 and m.version==version and m.status=="verified"
                 and (m.expires is None or now < m.expires)]
        values=sorted({m.value for m in matches})
        if not matches:
            return {"status":"not_found","value":None,"evidence":[]}
        if len(values)>1:
            return {"status":"conflict","value":None,"candidates":values}
        return {"status":"usable","value":values[0],
                "evidence":sorted({e for m in matches for e in m.evidence})}


def make_store() -> Store:
    s=Store()
    s.add(Memory("path_base","projectA","v2","config_dir",("D1",)))
    s.add(Memory("path_base","projectA","v3","repo_root",("D2","T2")))
    s.add(Memory("path_base","projectB","v3","workspace",("B1",)))
    s.add(Memory("temporary","projectA","v3","old",("T0",),expires=date(2026,10,1)))
    return s


def self_test() -> None:
    s=make_store(); now=date(2026,10,17)
    assert s.query("path_base","projectA","v3",now)["value"]=="repo_root"
    assert s.query("path_base","projectB","v3",now)["value"]=="workspace"
    assert s.query("temporary","projectA","v3",now)["status"]=="not_found"
    s.add(Memory("path_base","projectA","v3","config_dir",("D3",)))
    assert s.query("path_base","projectA","v3",now)["status"]=="conflict"
    try:
        Memory("x","s","v","y",())
    except ValueError:
        pass
    else:
        raise AssertionError("无证据记录不能标为verified")


def run_demo() -> dict:
    s=make_store(); now=date(2026,10,17)
    before=s.query("path_base","projectA","v3",now)
    s.add(Memory("path_base","projectA","v3","config_dir",("D3",)))
    return {"性质":"固定教学日期；进程内存储；未连接真实用户记忆",
            "正常检索":before,"加入冲突后":s.query("path_base","projectA","v3",now),
            "过期条目":s.query("temporary","projectA","v3",now)}


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
  "性质": "固定教学日期；进程内存储；未连接真实用户记忆",
  "正常检索": {
    "status": "usable",
    "value": "repo_root",
    "evidence": [
      "D2",
      "T2"
    ]
  },
  "加入冲突后": {
    "status": "conflict",
    "value": null,
    "candidates": [
      "config_dir",
      "repo_root"
    ]
  },
  "过期条目": {
    "status": "not_found",
    "value": null,
    "evidence": []
  }
}
```

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)