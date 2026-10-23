---
title: "并行Trace：墙钟与操作总量不同"
description: "AI系统工程：本地教学正文与可追溯图表"
---

拓展阅读


<span id="section-0"></span>


# 并行Trace：墙钟与操作总量不同

在人工构造的叶子Span上计算墙钟时间、操作时长总和及峰值并发。相邻区间按左闭右开处理。

状态：自检已实际通过　·　环境：Python标准库　·　性质：合成/模拟教学实验  
[对应讲义 14.3](chapter-14.md#m-14-03)　·　[保存Python脚本](../../reading-notes/experiments/10_trace_timing.py)


<span id="visual-reading"></span>



<span id="topic-1"></span>


## 沿着对象与状态理解本章

性能图先用实际起止时间画，而不是将所有工具耗时直接相加。下图中缩短非关键路径的A不会缩短总时间；同样，降低单次Token价也未必降低成功任务成本。

下方图解的固定输入在“输入与适用条件”中声明。它用于解释本章机制，不与本章其他独立例子的数值暗中接续。


<span id="visual-F38"></span>

<span id="topic-2"></span>

<span id="topic-3"></span>

<span id="topic-4"></span>

<span id="topic-5"></span>

<span id="topic-6"></span>

<span id="topic-7"></span>


相关动态过程：[Trace要告诉你因果，不只是时间戳](../visual/F38.md)。本节下文继续展示更具体的计算与工程边界。

继续看相关机制：[F24 · 任务状态不是聊天里的一句总结](../visual/F24.md)[O06 · 连续组批：有座位空出来，就接下一位](../visual/O06.md)[O12 · 模型路由：便宜一次，不一定便宜一项成功任务](../visual/O12.md)


<span id="method"></span>


## 怎样观察与验证

默认墙钟9、操作总量12、峰值并发2。不要同时把父Span与子Span重复加总，也不要把合成时间当成实际性能测量。


<span id="run"></span>


## 运行命令

```
python3 reading-notes/experiments/10_trace_timing.py
```


<span id="code"></span>


## 完整教学代码


<span id="concept-intro-1"></span>


先认识这里的对象与符号

[SSE、chunk、delta：不同的分片层](../concepts.md#concept-sse)
:   SSE是服务端发送事件的文本协议；网络chunk是这次收到的一段字节；delta是某个输出项的增量内容。三者边界不保证重合。一个完整事件也未必意味着完整工具参数。参数可能先收到{"path":"a，后收到.py"}；必须组装并等协议规定的完成条件，不能见到片段就执行。

```
"""用合成叶子Span说明并行耗时。没有真实计时或外部遥测。"""
from dataclasses import dataclass,asdict
import math


@dataclass(frozen=True)
class Span:
    name: str
    start: float
    end: float

    def __post_init__(self):
        if not self.name or not all(math.isfinite(x) for x in [self.start,self.end]) or self.end<self.start:
            raise ValueError("Span需有名称、有限时间与非负时长")


def summarize(spans: list[Span]) -> dict:
    if not spans:
        return {"wall_time":0.0,"sum_leaf_durations":0.0,"peak_concurrency":0}
    events=[]
    for s in spans:
        if s.end>s.start:
            events.extend([(s.start,1),(s.end,-1)])
    current=peak=0
    # 同时发生时先处理结束；区间按[start,end)解释。
    for _,delta in sorted(events,key=lambda x:(x[0],x[1])):
        current+=delta; peak=max(peak,current)
    return {"wall_time":max(s.end for s in spans)-min(s.start for s in spans),
            "sum_leaf_durations":sum(s.end-s.start for s in spans),
            "peak_concurrency":peak}


def self_test() -> None:
    s=[Span('prepare',0,1),Span('searchA',1,5),Span('searchB',1,4),Span('verify',5,9)]
    m=summarize(s)
    assert m=={"wall_time":9,"sum_leaf_durations":12,"peak_concurrency":2}
    assert summarize([])["wall_time"]==0
    assert summarize([Span('zero',1,1)])["peak_concurrency"]==0


def run_demo() -> dict:
    spans=[Span('准备',0,1),Span('搜索A',1,5),Span('搜索B',1,4),Span('验证',5,9)]
    return {"性质":"人工时间线，只统计叶子Span，不混入父Span重复计时",
            "时间线":[asdict(s) for s in spans],"统计":summarize(spans),
            "说明":"时间单位任意；墙钟9与操作总量12不是同一指标"}


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
  "性质": "人工时间线，只统计叶子Span，不混入父Span重复计时",
  "时间线": [
    {
      "name": "准备",
      "start": 0,
      "end": 1
    },
    {
      "name": "搜索A",
      "start": 1,
      "end": 5
    },
    {
      "name": "搜索B",
      "start": 1,
      "end": 4
    },
    {
      "name": "验证",
      "start": 5,
      "end": 9
    }
  ],
  "统计": {
    "wall_time": 9,
    "sum_leaf_durations": 12,
    "peak_concurrency": 2
  },
  "说明": "时间单位任意；墙钟9与操作总量12不是同一指标"
}
```

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)