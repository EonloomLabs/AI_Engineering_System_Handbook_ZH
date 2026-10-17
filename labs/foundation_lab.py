"""本教材基础手算的可执行核对。Python 3.10+，仅标准库，无网络或模型下载。
所有词表、权重和输入均为原创教学数据；不是商业模型性能测试。
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from typing import Any, Sequence

E = [[0.,0.,0.,0.],[1.,0.,0.,1.],[0.,1.,0.,1.],
     [1.,1.,0.,0.],[0.,1.,1.,0.],[1.,0.,1.,0.]]
VOCAB = ['<PAD>','我','爱','学习','你','！']

def shape(x: Any) -> tuple[int, ...]:
    """检查规则嵌套列表；拒绝参差列表，避免误把不规则数据称为密集张量。"""
    if not isinstance(x, (list, tuple)):
        return ()
    if not x:
        return (0,)
    sub = shape(x[0])
    if any(shape(v) != sub for v in x):
        raise ValueError('各行长度不一致，不能描述为规则密集张量')
    return (len(x),) + sub

def pad(rows: Sequence[Sequence[int]], length: int | None = None):
    if not rows or any(not row for row in rows):
        raise ValueError('本演示要求至少一条非空输入')
    size = max(map(len,rows)) if length is None else length
    if type(size) is not int or size < max(map(len,rows)):
        raise ValueError('补齐长度不能小于已有长度；本函数不做截断')
    ids = [list(row)+[0]*(size-len(row)) for row in rows]
    valid = [[1]*len(row)+[0]*(size-len(row)) for row in rows]
    return ids, valid

def lookup(ids, embedding=E):
    es = shape(embedding)
    if len(es)!=2 or es[0]==0 or es[1]==0:
        raise ValueError('Embedding需要非空二维表')
    if isinstance(ids,(list,tuple)):
        shape(ids)
        return [lookup(i,embedding) for i in ids]
    if type(ids) is not int or not 0 <= ids < len(embedding):
        raise ValueError('编号必须是词表范围内的整数')
    return list(embedding[ids])  # 返回副本，避免教学程序误改参数表

def matmul(a, b):
    sa, sb = shape(a), shape(b)
    if len(sa)!=2 or len(sb)!=2 or not sa[0] or not sb[0] or sa[1]!=sb[0]:
        raise ValueError('矩阵乘法要求[m,n]乘[n,k]')
    return [[sum(a[i][j]*b[j][k] for j in range(sa[1]))
             for k in range(sb[1])] for i in range(sa[0])]

def transpose(a):
    if len(shape(a))!=2:
        raise ValueError('只接受二维表')
    return [list(c) for c in zip(*a)]

def reshape_flat(xs, rows, cols):
    if type(rows) is not int or type(cols) is not int or rows<1 or cols<1 or len(xs)!=rows*cols:
        raise ValueError('元素总数必须相同且尺寸为正整数')
    return [list(xs[i*cols:(i+1)*cols]) for i in range(rows)]

def softmax(xs: Sequence[float]) -> list[float]:
    if not xs or any(math.isnan(x) or x==math.inf for x in xs):
        raise ValueError('要求非空分数，允许屏蔽用−inf但不允许NaN/+inf')
    m=max(xs)
    if m == -math.inf:
        raise ValueError('全部位置被屏蔽，无可归一化候选')
    ex=[math.exp(x-m) for x in xs]
    total=sum(ex)
    return [v/total for v in ex]

def attention(q, keys, values, allowed=None):
    sk,sv=shape(keys),shape(values)
    if len(sk)!=2 or len(sv)!=2 or sk[0]!=sv[0] or len(q)!=sk[1] or not q:
        raise ValueError('Q/K宽度与K/V位置数必须一致')
    if allowed is None: allowed=[True]*sk[0]
    if len(allowed)!=sk[0]: raise ValueError('mask长度不匹配')
    scores=[sum(a*b for a,b in zip(q,k))/math.sqrt(len(q)) if ok else -math.inf
            for k,ok in zip(keys,allowed)]
    weights=softmax(scores)
    output=[sum(weights[i]*values[i][j] for i in range(sk[0])) for j in range(sv[1])]
    return {'scores':scores,'weights':weights,'output':output}

def causal_mask(past: int, new: int, valid=None):
    if type(past) is not int or type(new) is not int or past<0 or new<1:
        raise ValueError('历史长度非负，新长度为正整数')
    if valid is None: valid=[True]*(past+new)
    if len(valid)!=past+new: raise ValueError('有效性表长度不匹配')
    return [[bool(valid[j]) and j<=past+i for j in range(past+new)] for i in range(new)]

def layernorm(x, eps=1e-5):
    if not x or eps<0: raise ValueError('要求非空向量和非负epsilon')
    mean=sum(x)/len(x); variance=sum((v-mean)**2 for v in x)/len(x)
    den=math.sqrt(variance+eps)
    if den==0: raise ValueError('分母为0；常量向量需要正epsilon')
    return [(v-mean)/den for v in x]

def rotate(x, angle):
    if len(x)!=2: raise ValueError('这里只演示二维旋转')
    c,s=math.cos(angle),math.sin(angle)
    return [x[0]*c-x[1]*s,x[0]*s+x[1]*c]

def scalar_training(w=1.0, x=2.0, target=4.0, lr=.2):
    pred=w*x; loss=.5*(pred-target)**2; grad=(pred-target)*x
    new_w=w-lr*grad
    return {'w':w,'x':x,'target':target,'prediction':pred,'loss':loss,
            'gradient':grad,'learning_rate':lr,'new_w':new_w,
            'new_prediction':new_w*x,'new_loss':.5*(new_w*x-target)**2}

def rrf(rankings, c=10):
    if c<0: raise ValueError('c不能为负')
    scores={}
    for rank in rankings:
        if len(set(rank))!=len(rank): raise ValueError('单一路排名不能包含重复项')
        for i,item in enumerate(rank,1): scores[item]=scores.get(item,0)+1/(c+i)
    return scores

def finite_difference():
    h=1e-6
    loss=lambda w:.5*(2*w-4)**2
    return (loss(1+h)-loss(1-h))/(2*h)

def build_results():
    ids, valid=pad([[1,2,3],[4,2]])
    h=lookup(ids)
    attention_demo=attention([1,0],[[1,0],[0,1]],[[10,0],[0,20]])
    logits=matmul([[1,2]],[[0,1,0,1,-1,0],[0,0,1,1,0,-1]])[0]
    dpo_s=math.log(.2/.1)-math.log(.1/.1)
    return {
        'scope':'原创教学数据与CPU标量算术。没有商业LLM调用、真实语义训练或GPU性能测量。',
        'vocabulary':VOCAB,'embedding_table':E,
        'input_ids':ids,'valid_positions':valid,'id_shape':shape(ids),
        'embedding_output':h,'embedding_shape':shape(h),
        'shape_scale':{'B':2,'T':128,'d':4096,'elements':2*128*4096,'bytes_per_element':2,
                       'output_bytes':2*128*4096*2,'output_MiB':2*128*4096*2/2**20,
                       'input_int64_bytes':2*128*8},
        'matrix_product':matmul([[1,2,3],[4,5,6]],[[1,0],[0,1],[1,1]]),
        'transpose':transpose([[1,2,3],[4,5,6]]),'reshape':reshape_flat([1,2,3,4,5,6],3,2),
        'softmax_ln123':softmax([0,math.log(2),math.log(3)]),
        'attention':attention_demo,'mask_without_cache':causal_mask(0,3),
        'mask_3_past_2_new':causal_mask(3,2),'rotation_90':rotate([2,3],math.pi/2),
        'layernorm_no_epsilon':layernorm([1,3],0),
        'rmsnorm_no_epsilon':[1/math.sqrt(5),3/math.sqrt(5)],
        'output_logits':logits,'next_token_greedy':max(range(len(logits)),key=logits.__getitem__),
        'simple_network':{'preactivation':[3,-1],'relu':[3,0],'output':6},
        'kv_toy':{'layers':2,'positions':3,'heads':1,'head_width':4,'bytes_per_element':4,
                  'elements':2*2*3*1*4,'bytes':2*2*3*1*4*4},
        'scalar_training':scalar_training(),'finite_difference_gradient':finite_difference(),
        'dpo_example':{'score':dpo_s,'sigmoid':1/(1+math.exp(-dpo_s)),
                       'loss':math.log1p(math.exp(-dpo_s))},
        'kl_example':.5*math.log(.5/.25)+.5*math.log(.5/.75),
        'rrf':rrf([['A','B','C'],['B','C','A']]),
        'pass_independent_p08_k3':{'at_least_once':1-(1-.8)**3,'all_three':.8**3},
        'dag':{'serial':2+3+4+1,'parallel_ideal':2+max(3,4)+1,'parallel_overhead4':2+max(3,4)+1+4},
        'image_patches':{'height':224,'width':224,'patch_side':16,'count':(224//16)**2,'raw_patch_values':16*16*3}}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=Path(__file__).with_name('foundation_results.json'))
    args=ap.parse_args(); data=build_results()
    rendered=json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)
    args.output.write_text(rendered+'\n',encoding='utf-8'); print(rendered)

if __name__=='__main__': main()
