"""预算选择、版本化证据和持久记忆。不是LLM语义压缩器。"""
from __future__ import annotations
from dataclasses import dataclass,field
from pathlib import Path
import sqlite3,json


@dataclass(frozen=True)
class Item:
    id: str
    cost: int
    value: float
    required: bool=False
    needs: tuple[str,...]=()


def pack(items: list[Item],budget: int):
    """确定性贪心基线。cost由调用方给出，本实验数值不是某产品Token测量。"""
    by={i.id:i for i in items}
    if len(by)!=len(items) or budget<0 or any(i.cost<=0 for i in items):raise ValueError('ID/预算无效')
    selected=set()
    def closure(key,visiting=None):
        if key not in by:raise ValueError('缺少依赖:'+key)
        visiting=set() if visiting is None else visiting
        if key in visiting:raise ValueError('循环依赖')
        return {key}.union(*(closure(d,visiting|{key}) for d in by[key].needs))
    for i in items:
        if i.required:selected|=closure(i.id)
    def cost(s):return sum(by[k].cost for k in s)
    if cost(selected)>budget:raise ValueError('必要项已经超预算，禁止静默丢弃')
    # 比值只用于教学选择基线，并非声称真实信息价值可精确给定。
    for item in sorted(items,key=lambda i:(-i.value/i.cost,i.id)):
        proposed=selected|closure(item.id)
        if cost(proposed)<=budget:selected=proposed
    return {'selected':sorted(selected),'cost':cost(selected),'budget':budget}


def validate_checkpoint(state: dict, current_version: int):
    problems=[]
    required={'goal','constraints','claims','evidence','pending','version'}
    if required-set(state):return ['missing_fields:'+','.join(sorted(required-set(state)))]
    if state['version']!=current_version:problems.append('stale_checkpoint')
    for claim in state['claims']:
        if claim['status']=='verified':
            ref=state['evidence'].get(claim.get('evidence_id'))
            if not ref:problems.append('unbacked_verified_claim:'+claim['id'])
            elif ref['version']!=current_version:problems.append('stale_evidence:'+claim['id'])
    return problems


class Memory:
    def __init__(self,path: Path):
        self.db=sqlite3.connect(path)
        self.db.execute('''CREATE TABLE IF NOT EXISTS memory(
          id INTEGER PRIMARY KEY, tenant TEXT, subject TEXT, claim TEXT,
          valid_from INTEGER, valid_to INTEGER, recorded_at INTEGER,
          source_version INTEGER, status TEXT)''')
    def add(self,tenant,subject,claim,*,start,end=None,recorded,source_version,status='candidate'):
        if end is not None and end<=start:raise ValueError('有效时间区间无效')
        if status not in ('candidate','active','retired'):raise ValueError('状态无效')
        with self.db:
            self.db.execute('INSERT INTO memory(tenant,subject,claim,valid_from,valid_to,recorded_at,source_version,status) VALUES(?,?,?,?,?,?,?,?)',(tenant,subject,claim,start,end,recorded,source_version,status))
    def recall(self,tenant,subject,*,at,known_at,source_version):
        rows=self.db.execute('''SELECT DISTINCT claim FROM memory WHERE tenant=? AND subject=?
          AND valid_from<=? AND (valid_to IS NULL OR valid_to>?)
          AND recorded_at<=? AND source_version=? AND status='active' ''',(tenant,subject,at,at,known_at,source_version)).fetchall()
        if len(rows)>1:return {'status':'conflict','claims':[r[0] for r in rows]}
        if not rows:return {'status':'not_found','claims':[]}
        return {'status':'found','claims':[rows[0][0]]}
    def close(self):self.db.close()


def run():
    import tempfile
    items=[Item('policy',30,1,True),Item('definition',20,3),Item('usage',20,5,needs=('definition',)),Item('noise',50,.1)]
    with tempfile.TemporaryDirectory() as d:
        m=Memory(Path(d)/'memory.db');m.add('a','exclude','repository-relative',start=20,recorded=30,source_version=2,status='active')
        early=m.recall('a','exclude',at=25,known_at=25,source_version=2)
        now=m.recall('a','exclude',at=25,known_at=35,source_version=2);m.close()
    return {'kind':'确定性元数据约束，不证明自然语言语义保真','pack':pack(items,75),'historically_unknown':early,'now_known':now}
