---
title: "模型提议与程序执行分离"
description: "AI系统工程：本地教学正文与可追溯图表"
---

拓展阅读


<span id="section-0"></span>


# 模型提议与程序执行分离

用确定性模拟模型依次提出读取、修改、测试。执行器检查工具和作用域，记录幂等操作，最终状态依赖验证。

状态：自检已实际通过　·　环境：Python标准库　·　性质：合成/模拟教学实验  
[对应讲义 5.1](chapter-05.md#m-05-01)　·　[保存Python脚本](../../reading-notes/experiments/07_agent_loop.py)


<span id="visual-reading"></span>



<span id="topic-1"></span>


## 沿着对象与状态理解本章

把模型、宿主、工具画成不同泳道后，问“谁真正改变了文件”就有明确答案。跟踪每条返回消息，再判断需要继续调用模型、执行工具还是结束；不要把模型说完成当成环境已经完成。

下方图解的固定输入在“输入与适用条件”中声明。它用于解释本章机制，不与本章其他独立例子的数值暗中接续。


<span id="visual-F22"></span>

<span id="topic-2"></span>

<span id="topic-3"></span>

<span id="topic-4"></span>

<span id="topic-5"></span>

<span id="topic-6"></span>

<span id="topic-7"></span>


相关动态过程：[把一个Agent任务拆成真正发生的几轮](../visual/F22.md)。本节下文继续展示更具体的计算与工程边界。

继续看相关机制：[F24 · 任务状态不是聊天里的一句总结](../visual/F24.md)[F33 · 超时告诉你没收到，不告诉你没发生](../visual/F33.md)


<span id="method"></span>


## 怎样观察与验证

完整任务只有一次模拟写入，重复同一操作ID不重复写。未授权publish被拒绝。没有调用真实LLM，也不读写真实工程文件。


<span id="run"></span>


## 运行命令

```
python3 reading-notes/experiments/07_agent_loop.py
```


<span id="code"></span>


## 完整教学代码


<span id="concept-intro-1"></span>


先认识这里的对象与符号

[OAuth、scope与授权](../concepts.md#concept-oauth)
:   在授权场景，OAuth使应用能按授权取得访问凭据；scope声明一类访问范围，资源服务仍应检查具体权限。在记忆或任务场景，scope又可只表示适用范围，不能混成登录凭据。获准“读取日历”不等于获准删除所有事件；连接成功也不证明操作被批准。

[Patch、图像通道与视觉投影](../concepts.md#concept-patch)
:   图像中的patch是切分的小块，RGB是红绿蓝3个通道；软件工程中的patch则是代码补丁，两者同名。图像块展开后可通过可学习变换成为向量，不是查文字词表。独立图像例：16×16×3的一块含768个数，投影后可以变成d个特征。d由模型设计决定。

```
"""确定性模拟模型与工具循环；不调用LLM、不读写实际工程文件。"""
from dataclasses import dataclass, field


@dataclass
class State:
    evidence: bool=False
    patched: bool=False
    verified: bool=False
    events: list[dict]=field(default_factory=list)


class Executor:
    def __init__(self, allowed: set[str]):
        self.allowed=allowed
        self.completed: dict[str,tuple[dict,dict]]={}
        self.write_count=0

    def execute(self, call: dict, state: State) -> dict:
        if set(call)!={"id","tool","args"}:
            raise ValueError("调用字段必须为 id/tool/args")
        if not isinstance(call["id"],str) or not call["id"]:
            raise ValueError("调用ID必须是非空字符串")
        if call["tool"] not in self.allowed:
            raise PermissionError("工具未授权")
        if call["args"] != {"scope":"toy-project"}:
            raise PermissionError("作用域越界")
        if call["id"] in self.completed:
            previous,result=self.completed[call["id"]]
            if previous != call:
                raise ValueError("同一幂等ID不能指向不同动作")
            return {**result,"replayed":True}
        name=call["tool"]
        if name=="read":
            state.evidence=True
            result={"status":"ok","evidence":"toy:T1"}
        elif name=="patch":
            if not state.evidence:
                raise RuntimeError("缺少前置证据")
            state.patched=True; self.write_count+=1
            result={"status":"ok","version":"toy:v2"}
        elif name=="test":
            state.verified=state.patched
            result={"status":"passed" if state.verified else "failed"}
        else:
            raise ValueError("未知教学工具")
        self.completed[call["id"]]=(dict(call),dict(result))
        return result


def fake_model(state: State) -> dict:
    if not state.evidence: step,name=1,"read"
    elif not state.patched: step,name=2,"patch"
    elif not state.verified: step,name=3,"test"
    else: return {"kind":"final","status":"completed"}
    return {"kind":"tool","call":{"id":f"op-{step}","tool":name,"args":{"scope":"toy-project"}}}


def run(max_turns: int=6):
    if not isinstance(max_turns,int) or isinstance(max_turns,bool) or max_turns<=0:
        raise ValueError("轮次预算必须为正整数")
    state=State(); executor=Executor({"read","patch","test"})
    status="budget_exhausted"
    for _ in range(max_turns):
        proposal=fake_model(state)
        if proposal["kind"]=="final":
            status="completed" if state.verified else "verification_missing"
            break
        call=proposal["call"]
        result=executor.execute(call,state)
        state.events.append({"call":call,"result":result})
    return state,executor,status


def self_test() -> None:
    state,ex,status=run()
    assert status=="completed" and state.verified and ex.write_count==1
    patch={"id":"op-2","tool":"patch","args":{"scope":"toy-project"}}
    assert ex.execute(patch,state)["replayed"] and ex.write_count==1
    try:
        ex.execute({"id":"x","tool":"publish","args":{"scope":"toy-project"}},state)
    except PermissionError:
        pass
    else:
        raise AssertionError("未授权工具应被拒绝")
    assert run(1)[2]=="budget_exhausted"


def run_demo() -> dict:
    state,ex,status=run()
    return {"性质":"模拟模型与内存工具，不代表真实Agent性能",
            "最终状态":status,"实际模拟写入次数":ex.write_count,"事件":state.events}


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
  "性质": "模拟模型与内存工具，不代表真实Agent性能",
  "最终状态": "completed",
  "实际模拟写入次数": 1,
  "事件": [
    {
      "call": {
        "id": "op-1",
        "tool": "read",
        "args": {
          "scope": "toy-project"
        }
      },
      "result": {
        "status": "ok",
        "evidence": "toy:T1"
      }
    },
    {
      "call": {
        "id": "op-2",
        "tool": "patch",
        "args": {
          "scope": "toy-project"
        }
      },
      "result": {
        "status": "ok",
        "version": "toy:v2"
      }
    },
    {
      "call": {
        "id": "op-3",
        "tool": "test",
        "args": {
          "scope": "toy-project"
        }
      },
      "result": {
        "status": "passed"
      }
    }
  ]
}
```

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)