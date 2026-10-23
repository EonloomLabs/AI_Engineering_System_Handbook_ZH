"""仅用Python标准库，从本课保存的JSON权重重新计算无缓存前向与生成。
这份实现刻意不用PyTorch，作为独立数值对照。不会训练或下载模型。
运行: python reference_inference.py
"""
from __future__ import annotations
import json, math
from pathlib import Path

def matmul(a,b):
    if not a or not b or len(a[0])!=len(b): raise ValueError('矩阵乘内侧尺寸不匹配')
    return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]

def trans(a):return [list(col) for col in zip(*a)]
def add(a,b):return [[x+y for x,y in zip(ra,rb)] for ra,rb in zip(a,b)]
def norm(a,g,eps=1e-5):
    out=[]
    for row in a:
        r=math.sqrt(sum(x*x for x in row)/len(row)+eps)
        out.append([x/r*v for x,v in zip(row,g)])
    return out

def softmax(row):
    m=max(row)
    if not math.isfinite(m):raise ValueError('这一行没有有限的可见分数')
    es=[math.exp(x-m) for x in row];s=sum(es)
    return [x/s for x in es]

def forward(ids,p):
    if not ids or len(ids)>8:raise ValueError('只支持1..8个位置')
    x=add([p['E'][i] for i in ids],[p['P'][i] for i in range(len(ids))])
    n=norm(x,p['g1']);q=matmul(n,p['Wq']);k=matmul(n,p['Wk']);v=matmul(n,p['Wv'])
    scores=matmul(q,trans(k))
    probs=[softmax([z/2 if j<=i else -math.inf for j,z in enumerate(row)]) for i,row in enumerate(scores)]
    r=add(x,matmul(matmul(probs,v),p['Wo']))
    ff=matmul(norm(r,p['g2']),p['W1']);ff=[[max(0,x) for x in row] for row in ff]
    h=add(r,matmul(ff,p['W2']))
    return matmul(norm(h,p['gf']),p['U'])

def generate(ids,p,limit=5):
    ids=list(ids);history=[]
    for _ in range(limit):
        z=forward(ids,p)[-1];prob=softmax(z);chosen=max(range(8),key=lambda i:z[i])
        history.append(dict(input=list(ids),logits=z,probabilities=prob,selected=chosen))
        ids.append(chosen)
        if chosen==7:break
    return ids,history

if __name__=='__main__':
    d=Path(__file__).resolve().parent.parent/'data'
    p=json.loads((d/'weights_trained.json').read_text())['parameters']
    tokens,history=generate([6,1,2],p)
    actual=json.loads((d/'run.json').read_text())
    errors=[max(abs(x-y) for x,y in zip(a['logits'],b['logits'])) for a,b in zip(history,actual['generation']['steps'])]
    assert tokens==[6,1,2,3,5,7]
    assert max(errors)<1e-10
    result=dict(tokens=tokens,max_error=max(errors),device='Python math on CPU; no tensor library')
    (d/'reference_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
