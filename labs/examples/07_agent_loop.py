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
