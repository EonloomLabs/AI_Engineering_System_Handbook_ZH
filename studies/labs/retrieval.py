"""真实BM25、符号召回与RRF；不把词项匹配冒充Embedding/Reranker。
小语料线性扫描用于可读性；生产索引的性能需要另测。
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import Counter
import ast,math,re


def tokens(s: str) -> list[str]:
    split=re.sub(r'([a-z])([A-Z])',r'\1 \2',s).replace('_',' ')
    return re.findall(r'[a-z0-9]+|[\u4e00-\u9fff]',split.lower())


@dataclass(frozen=True)
class Doc:
    id: str
    text: str
    tenant: str
    version: int
    readers: frozenset[str]
    path: str=''


class Index:
    def __init__(self,docs: list[Doc]):
        self.docs=list(docs)
        if len({d.id for d in docs})!=len(docs):raise ValueError('重复文档ID')
        self.cache={}

    def search(self,query: str,*,tenant: str,principal: str,version: int,k: int=5):
        if k<1:raise ValueError('k必须为正')
        key=(query,tenant,principal,version,k)
        if key in self.cache:return list(self.cache[key])
        allowed=[d for d in self.docs if d.tenant==tenant and d.version==version and principal in d.readers]
        bags=[Counter(tokens(d.text)) for d in allowed];n=len(bags)
        if not n:return []
        avg=sum(sum(b.values()) for b in bags)/n
        if avg==0:return []
        q=set(tokens(query));df={t:sum(t in b for b in bags) for t in q};scores=[]
        for doc,b in zip(allowed,bags):
            score=0.;length=sum(b.values())
            for term in q:
                f=b[term];idf=math.log(1+(n-df[term]+.5)/(df[term]+.5))
                if f:score+=idf*f*2.2/(f+1.2*(.25+.75*length/avg))
            if score>0:scores.append((doc.id,score))
        scores.sort(key=lambda x:(-x[1],x[0]));result=scores[:k];self.cache[key]=result
        return list(result)

    def replace(self,docs):
        if len({d.id for d in docs})!=len(docs):raise ValueError('重复文档ID')
        self.docs=list(docs);self.cache.clear()


def rrf(rankings: list[list[str]],c: float=60.):
    if c<0:raise ValueError('RRF常数不能为负')
    scores={}
    for ranking in rankings:
        seen=set()
        for rank,key in enumerate(ranking,1):
            if key in seen:continue
            seen.add(key);scores[key]=scores.get(key,0.)+1/(c+rank)
    return sorted(scores.items(),key=lambda x:(-x[1],x[0]))


def symbols(source: str):
    """Python AST语法索引，不是完整名称绑定、类型推导或跨语言调用图。"""
    tree=ast.parse(source);rows=[]
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            rows.append({'name':node.name,'kind':type(node).__name__,'start':node.lineno,'end':node.end_lineno})
    return sorted(rows,key=lambda r:r['start'])


def run():
    docs=[Doc('old','exclude matches basename','a',1,frozenset({'alice'})),Doc('current','exclude matches repository relative path','a',2,frozenset({'alice'})),Doc('secret','exclude repository relative path secret','b',2,frozenset({'bob'})),Doc('denied','exclude top secret','a',2,frozenset({'bob'}))]
    idx=Index(docs)
    return {'kind':'权限过滤先于评分的真实词项检索','result':idx.search('exclude relative path',tenant='a',principal='alice',version=2),'denied':idx.search('exclude',tenant='a',principal='mallory',version=2),'symbols':symbols('def choose(paths):\n    return paths\n'),'rrf':rrf([['current','old'],['old','current']])}
