---
title: "retrieval.py"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# retrieval.py

BM25、权限、缓存与AST。对应第13、14章。依赖：标准库。

真实词项检索；未实现向量编码器或ANN。[阅读运行说明](../experiments.md) / [查看实测结果](../results.md)

[原始Python文件](../../../studies/labs/retrieval.py) · 78行

```

<span id="L1"></span>
"""真实BM25、符号召回与RRF；不把词项匹配冒充Embedding/Reranker。
<span id="L2"></span>
小语料线性扫描用于可读性；生产索引的性能需要另测。
<span id="L3"></span>
"""
<span id="L4"></span>
from __future__ import annotations
<span id="L5"></span>
from dataclasses import dataclass
<span id="L6"></span>
from collections import Counter
<span id="L7"></span>
import ast,math,re
<span id="L8"></span>
 
<span id="L9"></span>
 
<span id="L10"></span>
def tokens(s: str) -> list[str]:
<span id="L11"></span>
    split=re.sub(r'([a-z])([A-Z])',r'\1 \2',s).replace('_',' ')
<span id="L12"></span>
    return re.findall(r'[a-z0-9]+|[\u4e00-\u9fff]',split.lower())
<span id="L13"></span>
 
<span id="L14"></span>
 
<span id="L15"></span>
@dataclass(frozen=True)
<span id="L16"></span>
class Doc:
<span id="L17"></span>
    id: str
<span id="L18"></span>
    text: str
<span id="L19"></span>
    tenant: str
<span id="L20"></span>
    version: int
<span id="L21"></span>
    readers: frozenset[str]
<span id="L22"></span>
    path: str=''
<span id="L23"></span>
 
<span id="L24"></span>
 
<span id="L25"></span>
class Index:
<span id="L26"></span>
    def __init__(self,docs: list[Doc]):
<span id="L27"></span>
        self.docs=list(docs)
<span id="L28"></span>
        if len({d.id for d in docs})!=len(docs):raise ValueError('重复文档ID')
<span id="L29"></span>
        self.cache={}
<span id="L30"></span>
 
<span id="L31"></span>
    def search(self,query: str,*,tenant: str,principal: str,version: int,k: int=5):
<span id="L32"></span>
        if k<1:raise ValueError('k必须为正')
<span id="L33"></span>
        key=(query,tenant,principal,version,k)
<span id="L34"></span>
        if key in self.cache:return list(self.cache[key])
<span id="L35"></span>
        allowed=[d for d in self.docs if d.tenant==tenant and d.version==version and principal in d.readers]
<span id="L36"></span>
        bags=[Counter(tokens(d.text)) for d in allowed];n=len(bags)
<span id="L37"></span>
        if not n:return []
<span id="L38"></span>
        avg=sum(sum(b.values()) for b in bags)/n
<span id="L39"></span>
        if avg==0:return []
<span id="L40"></span>
        q=set(tokens(query));df={t:sum(t in b for b in bags) for t in q};scores=[]
<span id="L41"></span>
        for doc,b in zip(allowed,bags):
<span id="L42"></span>
            score=0.;length=sum(b.values())
<span id="L43"></span>
            for term in q:
<span id="L44"></span>
                f=b[term];idf=math.log(1+(n-df[term]+.5)/(df[term]+.5))
<span id="L45"></span>
                if f:score+=idf*f*2.2/(f+1.2*(.25+.75*length/avg))
<span id="L46"></span>
            if score>0:scores.append((doc.id,score))
<span id="L47"></span>
        scores.sort(key=lambda x:(-x[1],x[0]));result=scores[:k];self.cache[key]=result
<span id="L48"></span>
        return list(result)
<span id="L49"></span>
 
<span id="L50"></span>
    def replace(self,docs):
<span id="L51"></span>
        if len({d.id for d in docs})!=len(docs):raise ValueError('重复文档ID')
<span id="L52"></span>
        self.docs=list(docs);self.cache.clear()
<span id="L53"></span>
 
<span id="L54"></span>
 
<span id="L55"></span>
def rrf(rankings: list[list[str]],c: float=60.):
<span id="L56"></span>
    if c<0:raise ValueError('RRF常数不能为负')
<span id="L57"></span>
    scores={}
<span id="L58"></span>
    for ranking in rankings:
<span id="L59"></span>
        seen=set()
<span id="L60"></span>
        for rank,key in enumerate(ranking,1):
<span id="L61"></span>
            if key in seen:continue
<span id="L62"></span>
            seen.add(key);scores[key]=scores.get(key,0.)+1/(c+rank)
<span id="L63"></span>
    return sorted(scores.items(),key=lambda x:(-x[1],x[0]))
<span id="L64"></span>
 
<span id="L65"></span>
 
<span id="L66"></span>
def symbols(source: str):
<span id="L67"></span>
    """Python AST语法索引，不是完整名称绑定、类型推导或跨语言调用图。"""
<span id="L68"></span>
    tree=ast.parse(source);rows=[]
<span id="L69"></span>
    for node in ast.walk(tree):
<span id="L70"></span>
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
<span id="L71"></span>
            rows.append({'name':node.name,'kind':type(node).__name__,'start':node.lineno,'end':node.end_lineno})
<span id="L72"></span>
    return sorted(rows,key=lambda r:r['start'])
<span id="L73"></span>
 
<span id="L74"></span>
 
<span id="L75"></span>
def run():
<span id="L76"></span>
    docs=[Doc('old','exclude matches basename','a',1,frozenset({'alice'})),Doc('current','exclude matches repository relative path','a',2,frozenset({'alice'})),Doc('secret','exclude repository relative path secret','b',2,frozenset({'bob'})),Doc('denied','exclude top secret','a',2,frozenset({'bob'}))]
<span id="L77"></span>
    idx=Index(docs)
<span id="L78"></span>
    return {'kind':'权限过滤先于评分的真实词项检索','result':idx.search('exclude relative path',tenant='a',principal='alice',version=2),'denied':idx.search('exclude',tenant='a',principal='mallory',version=2),'symbols':symbols('def choose(paths):\n    return paths\n'),'rrf':rrf([['current','old'],['old','current']])}
```

AI系统工程：从基础到内部  
[全书目录](../../contents.md) · [术语与符号](../../glossary.md) · [参考资料](../../sources.md)