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
