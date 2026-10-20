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
