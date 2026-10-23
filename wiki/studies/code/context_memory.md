---
title: "context_memory.py"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# context\_memory.py

上下文装包与双时间记忆。对应第11、12、15章。依赖：标准库/SQLite。

元数据和版本契约；不是自然语言语义保真判定。[阅读运行说明](../experiments.md) / [查看实测结果](../results.md)

[原始Python文件](../../../studies/labs/context_memory.py) · 80行

```

<span id="L1"></span>
"""预算选择、版本化证据和持久记忆。不是LLM语义压缩器。"""
<span id="L2"></span>
from __future__ import annotations
<span id="L3"></span>
from dataclasses import dataclass,field
<span id="L4"></span>
from pathlib import Path
<span id="L5"></span>
import sqlite3,json
<span id="L6"></span>
 
<span id="L7"></span>
 
<span id="L8"></span>
@dataclass(frozen=True)
<span id="L9"></span>
class Item:
<span id="L10"></span>
    id: str
<span id="L11"></span>
    cost: int
<span id="L12"></span>
    value: float
<span id="L13"></span>
    required: bool=False
<span id="L14"></span>
    needs: tuple[str,...]=()
<span id="L15"></span>
 
<span id="L16"></span>
 
<span id="L17"></span>
def pack(items: list[Item],budget: int):
<span id="L18"></span>
    """确定性贪心基线。cost由调用方给出，本实验数值不是某产品Token测量。"""
<span id="L19"></span>
    by={i.id:i for i in items}
<span id="L20"></span>
    if len(by)!=len(items) or budget<0 or any(i.cost<=0 for i in items):raise ValueError('ID/预算无效')
<span id="L21"></span>
    selected=set()
<span id="L22"></span>
    def closure(key,visiting=None):
<span id="L23"></span>
        if key not in by:raise ValueError('缺少依赖:'+key)
<span id="L24"></span>
        visiting=set() if visiting is None else visiting
<span id="L25"></span>
        if key in visiting:raise ValueError('循环依赖')
<span id="L26"></span>
        return {key}.union(*(closure(d,visiting|{key}) for d in by[key].needs))
<span id="L27"></span>
    for i in items:
<span id="L28"></span>
        if i.required:selected|=closure(i.id)
<span id="L29"></span>
    def cost(s):return sum(by[k].cost for k in s)
<span id="L30"></span>
    if cost(selected)>budget:raise ValueError('必要项已经超预算，禁止静默丢弃')
<span id="L31"></span>
    # 比值只用于教学选择基线，并非声称真实信息价值可精确给定。
<span id="L32"></span>
    for item in sorted(items,key=lambda i:(-i.value/i.cost,i.id)):
<span id="L33"></span>
        proposed=selected|closure(item.id)
<span id="L34"></span>
        if cost(proposed)<=budget:selected=proposed
<span id="L35"></span>
    return {'selected':sorted(selected),'cost':cost(selected),'budget':budget}
<span id="L36"></span>
 
<span id="L37"></span>
 
<span id="L38"></span>
def validate_checkpoint(state: dict, current_version: int):
<span id="L39"></span>
    problems=[]
<span id="L40"></span>
    required={'goal','constraints','claims','evidence','pending','version'}
<span id="L41"></span>
    if required-set(state):return ['missing_fields:'+','.join(sorted(required-set(state)))]
<span id="L42"></span>
    if state['version']!=current_version:problems.append('stale_checkpoint')
<span id="L43"></span>
    for claim in state['claims']:
<span id="L44"></span>
        if claim['status']=='verified':
<span id="L45"></span>
            ref=state['evidence'].get(claim.get('evidence_id'))
<span id="L46"></span>
            if not ref:problems.append('unbacked_verified_claim:'+claim['id'])
<span id="L47"></span>
            elif ref['version']!=current_version:problems.append('stale_evidence:'+claim['id'])
<span id="L48"></span>
    return problems
<span id="L49"></span>
 
<span id="L50"></span>
 
<span id="L51"></span>
class Memory:
<span id="L52"></span>
    def __init__(self,path: Path):
<span id="L53"></span>
        self.db=sqlite3.connect(path)
<span id="L54"></span>
        self.db.execute('''CREATE TABLE IF NOT EXISTS memory(
<span id="L55"></span>
          id INTEGER PRIMARY KEY, tenant TEXT, subject TEXT, claim TEXT,
<span id="L56"></span>
          valid_from INTEGER, valid_to INTEGER, recorded_at INTEGER,
<span id="L57"></span>
          source_version INTEGER, status TEXT)''')
<span id="L58"></span>
    def add(self,tenant,subject,claim,*,start,end=None,recorded,source_version,status='candidate'):
<span id="L59"></span>
        if end is not None and end<=start:raise ValueError('有效时间区间无效')
<span id="L60"></span>
        if status not in ('candidate','active','retired'):raise ValueError('状态无效')
<span id="L61"></span>
        with self.db:
<span id="L62"></span>
            self.db.execute('INSERT INTO memory(tenant,subject,claim,valid_from,valid_to,recorded_at,source_version,status) VALUES(?,?,?,?,?,?,?,?)',(tenant,subject,claim,start,end,recorded,source_version,status))
<span id="L63"></span>
    def recall(self,tenant,subject,*,at,known_at,source_version):
<span id="L64"></span>
        rows=self.db.execute('''SELECT DISTINCT claim FROM memory WHERE tenant=? AND subject=?
<span id="L65"></span>
          AND valid_from<=? AND (valid_to IS NULL OR valid_to>?)
<span id="L66"></span>
          AND recorded_at<=? AND source_version=? AND status='active' ''',(tenant,subject,at,at,known_at,source_version)).fetchall()
<span id="L67"></span>
        if len(rows)>1:return {'status':'conflict','claims':[r[0] for r in rows]}
<span id="L68"></span>
        if not rows:return {'status':'not_found','claims':[]}
<span id="L69"></span>
        return {'status':'found','claims':[rows[0][0]]}
<span id="L70"></span>
    def close(self):self.db.close()
<span id="L71"></span>
 
<span id="L72"></span>
 
<span id="L73"></span>
def run():
<span id="L74"></span>
    import tempfile
<span id="L75"></span>
    items=[Item('policy',30,1,True),Item('definition',20,3),Item('usage',20,5,needs=('definition',)),Item('noise',50,.1)]
<span id="L76"></span>
    with tempfile.TemporaryDirectory() as d:
<span id="L77"></span>
        m=Memory(Path(d)/'memory.db');m.add('a','exclude','repository-relative',start=20,recorded=30,source_version=2,status='active')
<span id="L78"></span>
        early=m.recall('a','exclude',at=25,known_at=25,source_version=2)
<span id="L79"></span>
        now=m.recall('a','exclude',at=25,known_at=35,source_version=2);m.close()
<span id="L80"></span>
    return {'kind':'确定性元数据约束，不证明自然语言语义保真','pack':pack(items,75),'historically_unknown':early,'now_known':now}
```

AI系统工程：从基础到内部  
[全书目录](../../contents.md) · [术语与符号](../../glossary.md) · [参考资料](../../sources.md)