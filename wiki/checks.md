---
title: "代码、数值与验证边界"
description: "AI系统工程：本地教学正文与可追溯图表"
---

阅读指南与附录


<span id="checks-title"></span>


# 代码、数值与验证边界

基础实验程序只依赖Python标准库。它核对数表、矩阵、softmax、注意力、掩码、旋转、梯度、简单偏好与评测算式。所有输入、词表和权重都是明确的教学数据。


<span id="section-1"></span>


### 测试结果与适用范围

**39项unittest测试通过，0失败、0错误、0跳过。**完整结果在下方。它们是确定性程序检查，不是模型通用能力、压缩质量或生产安全通过率。


<span id="run"></span>


## 如何运行

无需网络、GPU或API密钥。Python 3.10及以上，在资料包目录执行：

```
cd labs
python3 foundation_lab.py
python3 -m unittest -v test_foundations
```

不运行代码也可阅读全部推导。JSON保存精确输出，课文使用适当小数位。


<span id="code-foundation"></span>


## 基础手算完整程序

[查看对应本地文件](../labs/foundation_lab.py)

```
"""本教材基础手算的可执行核对。Python 3.10+，仅标准库，无网络或模型下载。
所有词表、权重和输入均为原创教学数据；不是商业模型性能测试。
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from typing import Any, Sequence

E = [[0.0, 0.0, 0.0, 0.0], [0.2, -0.1, 0.7, 0.4], [-0.3, 0.8, 0.1, 0.5], [0.6, 0.2, -0.4, 0.9], [0.1, -0.5, 0.9, 0.3], [-0.2, 0.4, 0.5, -0.6]]
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
```


<span id="code-tests"></span>


## 39项测试完整程序

[查看对应本地文件](../labs/test_foundations.py)

```
"""基础课手算、边界条件和常见错误的确定性测试。不是LLM质量评测。"""
import math
import unittest
from foundation_lab import (E,shape,pad,lookup,matmul,transpose,reshape_flat,softmax,
                            attention,causal_mask,layernorm,rotate,scalar_training,
                            rrf,finite_difference,build_results)

class FoundationTests(unittest.TestCase):
    def assertVector(self,a,b,places=10):
        self.assertEqual(len(a),len(b))
        for x,y in zip(a,b): self.assertAlmostEqual(x,y,places=places)
    def test_scalar_shape(self): self.assertEqual(shape(7),())
    def test_matrix_shape(self): self.assertEqual(shape([[1,2,3],[4,5,6]]),(2,3))
    def test_ragged_rejected(self):
        with self.assertRaises(ValueError): shape([[1,2],[3]])
    def test_pad_ids(self): self.assertEqual(pad([[1,2,3],[4,2]])[0],[[1,2,3],[4,2,0]])
    def test_pad_valid(self): self.assertEqual(pad([[1,2,3],[4,2]])[1],[[1,1,1],[1,1,0]])
    def test_padding_does_not_truncate(self):
        with self.assertRaises(ValueError): pad([[1,2,3]],2)
    def test_embedding_shape(self): self.assertEqual(shape(lookup([[1,2,3],[4,2,0]])),(2,3,4))
    def test_embedding_exact_row(self): self.assertEqual(lookup(4),[0.1,-0.5,0.9,0.3])
    def test_same_token_same_initial_row(self): self.assertEqual(lookup([[1,2],[4,2]])[0][1],lookup(2))
    def test_invalid_id_rejected(self):
        for v in [-1,6,1.5,True]:
            with self.assertRaises(ValueError): lookup(v)
    def test_lookup_does_not_modify_parameter(self):
        a=lookup(1); a[0]=999; self.assertEqual(E[1][0],0.2)
    def test_independent_batch(self):
        h=lookup([[1,2,3],[4,2,0]]); other=lookup([[5,5,5],[4,2,0]])
        self.assertEqual(h[1],other[1])
    def test_matrix_product(self): self.assertEqual(matmul([[1,2,3],[4,5,6]],[[1,0],[0,1],[1,1]]),[[4,5],[10,11]])
    def test_matrix_bad_dimensions(self):
        with self.assertRaises(ValueError): matmul([[1,2]],[[1,2]])
    def test_transpose_not_reshape(self): self.assertNotEqual(transpose([[1,2,3],[4,5,6]]),reshape_flat([1,2,3,4,5,6],3,2))
    def test_softmax_hand_calculation(self): self.assertVector(softmax([0,math.log(2),math.log(3)]),[1/6,1/3,.5])
    def test_softmax_translation(self): self.assertVector(softmax([1,2,3]),softmax([1001,1002,1003]))
    def test_softmax_sum_one(self): self.assertAlmostEqual(sum(softmax([-1000,0,1000])),1)
    def test_all_masked_rejected(self):
        with self.assertRaises(ValueError): softmax([-math.inf,-math.inf])
    def test_attention_hand_calculation(self):
        d=attention([1,0],[[1,0],[0,1]],[[10,0],[0,20]])
        a=1/(1+math.exp(-1/math.sqrt(2)))
        self.assertVector(d['weights'],[a,1-a]); self.assertVector(d['output'],[10*a,20*(1-a)])
    def test_mask_eliminates_value(self): self.assertVector(attention([1,0],[[1,0],[0,1]],[[10,0],[0,20]],[True,False])['output'],[10,0])
    def test_causal_triangle(self): self.assertEqual(causal_mask(0,3),[[True,False,False],[True,True,False],[True,True,True]])
    def test_cached_non_square_mask(self): self.assertEqual(causal_mask(3,2),[[True]*4+[False],[True]*5])
    def test_cached_wrong_top_left_mask_detected(self): self.assertNotEqual(causal_mask(3,2),[[True,False,False,False,False],[True,True,False,False,False]])
    def test_padding_key_excluded(self): self.assertEqual(causal_mask(0,3,[1,1,0])[-1],[True,True,False])
    def test_rotation_preserves_norm(self):
        r=rotate([2,3],math.pi/2); self.assertVector(r,[-3,2]); self.assertAlmostEqual(sum(x*x for x in r),13)
    def test_layernorm(self): self.assertVector(layernorm([1,3],0),[-1,1])
    def test_layernorm_constant_with_epsilon(self): self.assertVector(layernorm([2,2]),[0,0])
    def test_gradient_finite_difference(self): self.assertAlmostEqual(finite_difference(),-4,places=6)
    def test_training_decreases_loss(self):
        d=scalar_training(); self.assertAlmostEqual(d['new_w'],1.8); self.assertAlmostEqual(d['new_loss'],.08)
    def test_logits_to_token(self): self.assertEqual(build_results()['next_token_greedy'],3)
    def test_large_shape_memory(self): self.assertEqual(build_results()['shape_scale']['output_MiB'],2)
    def test_kv_memory(self): self.assertEqual(build_results()['kv_toy']['bytes'],192)
    def test_dpo(self): self.assertAlmostEqual(build_results()['dpo_example']['sigmoid'],2/3)
    def test_kl(self): self.assertAlmostEqual(build_results()['kl_example'],.14384103622589042)
    def test_rrf(self):
        s=rrf([['A','B','C'],['B','C','A']]); self.assertGreater(s['B'],s['A'])
    def test_pass_distinction(self):
        d=build_results()['pass_independent_p08_k3'];self.assertAlmostEqual(d['at_least_once'],.992);self.assertAlmostEqual(d['all_three'],.512)
    def test_dag_overhead(self):
        d=build_results()['dag']; self.assertGreater(d['parallel_overhead4'],d['serial'])
    def test_image_patch_count(self): self.assertEqual(build_results()['image_patches']['count'],196)

if __name__=='__main__': unittest.main(verbosity=2)
```


<span id="numeric-output"></span>


## 实际数值结果

[查看对应本地文件](../labs/foundation_results.json)

```
{
  "scope": "原创教学数据与CPU标量算术。没有商业LLM调用、真实语义训练或GPU性能测量。",
  "vocabulary": [
    "<PAD>",
    "我",
    "爱",
    "学习",
    "你",
    "！"
  ],
  "embedding_table": [
    [
      0.0,
      0.0,
      0.0,
      0.0
    ],
    [
      0.2,
      -0.1,
      0.7,
      0.4
    ],
    [
      -0.3,
      0.8,
      0.1,
      0.5
    ],
    [
      0.6,
      0.2,
      -0.4,
      0.9
    ],
    [
      0.1,
      -0.5,
      0.9,
      0.3
    ],
    [
      -0.2,
      0.4,
      0.5,
      -0.6
    ]
  ],
  "input_ids": [
    [
      1,
      2,
      3
    ],
    [
      4,
      2,
      0
    ]
  ],
  "valid_positions": [
    [
      1,
      1,
      1
    ],
    [
      1,
      1,
      0
    ]
  ],
  "id_shape": [
    2,
    3
  ],
  "embedding_output": [
    [
      [
        0.2,
        -0.1,
        0.7,
        0.4
      ],
      [
        -0.3,
        0.8,
        0.1,
        0.5
      ],
      [
        0.6,
        0.2,
        -0.4,
        0.9
      ]
    ],
    [
      [
        0.1,
        -0.5,
        0.9,
        0.3
      ],
      [
        -0.3,
        0.8,
        0.1,
        0.5
      ],
      [
        0.0,
        0.0,
        0.0,
        0.0
      ]
    ]
  ],
  "embedding_shape": [
    2,
    3,
    4
  ],
  "shape_scale": {
    "B": 2,
    "T": 128,
    "d": 4096,
    "elements": 1048576,
    "bytes_per_element": 2,
    "output_bytes": 2097152,
    "output_MiB": 2.0,
    "input_int64_bytes": 2048
  },
  "matrix_product": [
    [
      4,
      5
    ],
    [
      10,
      11
    ]
  ],
  "transpose": [
    [
      1,
      4
    ],
    [
      2,
      5
    ],
    [
      3,
      6
    ]
  ],
  "reshape": [
    [
      1,
      2
    ],
    [
      3,
      4
    ],
    [
      5,
      6
    ]
  ],
  "softmax_ln123": [
    0.16666666666666666,
    0.3333333333333333,
    0.5
  ],
  "attention": {
    "scores": [
      0.7071067811865475,
      0.0
    ],
    "weights": [
      0.6697615493266569,
      0.3302384506733431
    ],
    "output": [
      6.697615493266569,
      6.604769013466862
    ]
  },
  "mask_without_cache": [
    [
      true,
      false,
      false
    ],
    [
      true,
      true,
      false
    ],
    [
      true,
      true,
      true
    ]
  ],
  "mask_3_past_2_new": [
    [
      true,
      true,
      true,
      true,
      false
    ],
    [
      true,
      true,
      true,
      true,
      true
    ]
  ],
  "rotation_90": [
    -3.0,
    2.0
  ],
  "layernorm_no_epsilon": [
    -1.0,
    1.0
  ],
  "rmsnorm_no_epsilon": [
    0.4472135954999579,
    1.3416407864998738
  ],
  "output_logits": [
    0,
    1,
    2,
    3,
    -1,
    -2
  ],
  "next_token_greedy": 3,
  "simple_network": {
    "preactivation": [
      3,
      -1
    ],
    "relu": [
      3,
      0
    ],
    "output": 6
  },
  "kv_toy": {
    "layers": 2,
    "positions": 3,
    "heads": 1,
    "head_width": 4,
    "bytes_per_element": 4,
    "elements": 48,
    "bytes": 192
  },
  "scalar_training": {
    "w": 1.0,
    "x": 2.0,
    "target": 4.0,
    "prediction": 2.0,
    "loss": 2.0,
    "gradient": -4.0,
    "learning_rate": 0.2,
    "new_w": 1.8,
    "new_prediction": 3.6,
    "new_loss": 0.07999999999999996
  },
  "finite_difference_gradient": -4.000000000226045,
  "dpo_example": {
    "score": 0.6931471805599453,
    "sigmoid": 0.6666666666666666,
    "loss": 0.4054651081081644
  },
  "kl_example": 0.14384103622589042,
  "rrf": {
    "A": 0.16783216783216784,
    "B": 0.17424242424242425,
    "C": 0.16025641025641024
  },
  "pass_independent_p08_k3": {
    "at_least_once": 0.992,
    "all_three": 0.5120000000000001
  },
  "dag": {
    "serial": 10,
    "parallel_ideal": 7,
    "parallel_overhead4": 11
  },
  "image_patches": {
    "height": 224,
    "width": 224,
    "patch_side": 16,
    "count": 196,
    "raw_patch_values": 768
  }
}
```


<span id="test-log"></span>


## 实际测试日志

[查看对应本地文件](../labs/test_results.txt)

```
test_all_masked_rejected (test_foundations.FoundationTests.test_all_masked_rejected) ... ok
test_attention_hand_calculation (test_foundations.FoundationTests.test_attention_hand_calculation) ... ok
test_cached_non_square_mask (test_foundations.FoundationTests.test_cached_non_square_mask) ... ok
test_cached_wrong_top_left_mask_detected (test_foundations.FoundationTests.test_cached_wrong_top_left_mask_detected) ... ok
test_causal_triangle (test_foundations.FoundationTests.test_causal_triangle) ... ok
test_dag_overhead (test_foundations.FoundationTests.test_dag_overhead) ... ok
test_dpo (test_foundations.FoundationTests.test_dpo) ... ok
test_embedding_exact_row (test_foundations.FoundationTests.test_embedding_exact_row) ... ok
test_embedding_shape (test_foundations.FoundationTests.test_embedding_shape) ... ok
test_gradient_finite_difference (test_foundations.FoundationTests.test_gradient_finite_difference) ... ok
test_image_patch_count (test_foundations.FoundationTests.test_image_patch_count) ... ok
test_independent_batch (test_foundations.FoundationTests.test_independent_batch) ... ok
test_invalid_id_rejected (test_foundations.FoundationTests.test_invalid_id_rejected) ... ok
test_kl (test_foundations.FoundationTests.test_kl) ... ok
test_kv_memory (test_foundations.FoundationTests.test_kv_memory) ... ok
test_large_shape_memory (test_foundations.FoundationTests.test_large_shape_memory) ... ok
test_layernorm (test_foundations.FoundationTests.test_layernorm) ... ok
test_layernorm_constant_with_epsilon (test_foundations.FoundationTests.test_layernorm_constant_with_epsilon) ... ok
test_logits_to_token (test_foundations.FoundationTests.test_logits_to_token) ... ok
test_lookup_does_not_modify_parameter (test_foundations.FoundationTests.test_lookup_does_not_modify_parameter) ... ok
test_mask_eliminates_value (test_foundations.FoundationTests.test_mask_eliminates_value) ... ok
test_matrix_bad_dimensions (test_foundations.FoundationTests.test_matrix_bad_dimensions) ... ok
test_matrix_product (test_foundations.FoundationTests.test_matrix_product) ... ok
test_matrix_shape (test_foundations.FoundationTests.test_matrix_shape) ... ok
test_pad_ids (test_foundations.FoundationTests.test_pad_ids) ... ok
test_pad_valid (test_foundations.FoundationTests.test_pad_valid) ... ok
test_padding_does_not_truncate (test_foundations.FoundationTests.test_padding_does_not_truncate) ... ok
test_padding_key_excluded (test_foundations.FoundationTests.test_padding_key_excluded) ... ok
test_pass_distinction (test_foundations.FoundationTests.test_pass_distinction) ... ok
test_ragged_rejected (test_foundations.FoundationTests.test_ragged_rejected) ... ok
test_rotation_preserves_norm (test_foundations.FoundationTests.test_rotation_preserves_norm) ... ok
test_rrf (test_foundations.FoundationTests.test_rrf) ... ok
test_same_token_same_initial_row (test_foundations.FoundationTests.test_same_token_same_initial_row) ... ok
test_scalar_shape (test_foundations.FoundationTests.test_scalar_shape) ... ok
test_softmax_hand_calculation (test_foundations.FoundationTests.test_softmax_hand_calculation) ... ok
test_softmax_sum_one (test_foundations.FoundationTests.test_softmax_sum_one) ... ok
test_softmax_translation (test_foundations.FoundationTests.test_softmax_translation) ... ok
test_training_decreases_loss (test_foundations.FoundationTests.test_training_decreases_loss) ... ok
test_transpose_not_reshape (test_foundations.FoundationTests.test_transpose_not_reshape) ... ok

----------------------------------------------------------------------
Ran 39 tests in 0.002s

OK
```


<span id="code-numeric_witnesses-py"></span>


## 进阶数值程序

[查看对应本地文件](../checks/numeric_witnesses.py)

```
"""Offline witnesses for worked arithmetic, not model performance benchmarks."""
import math, json
from pathlib import Path

def softmax(xs):
    m=max(xs); ex=[math.exp(x-m) for x in xs];s=sum(ex)
    return [x/s for x in ex]

def main():
    w=softmax([1/math.sqrt(2),1/math.sqrt(2),2/math.sqrt(2)])
    vs=[[1,2],[3,4],[4,6]]
    out=[sum(w[i]*vs[i][j] for i in range(3)) for j in range(2)]
    data={
      'attention':{'scores':[1/math.sqrt(2),1/math.sqrt(2),2/math.sqrt(2)], 'weights':w,'output':out},
      'temperature':{str(t):softmax([2/t,1/t,0/t]) for t in [0.5,1,2]},
      'kv_gib':2*32*32768*8*128*2/(2**30),
      'kv_bytes_per_token':2*32*8*128*2,
      'rrf':{'A':1/61+1/63,'B':1/62+1/61,'C':1/63+1/62},
      'pass_at_2_n10_c3':1-math.comb(7,2)/math.comb(10,2),
      'binomial_100_zero_fail_lower_95_two_sided':0.025**(1/100),
      'softmax_streaming':softmax([1,2,3]),
      'bm25':{},
      'speculative':{}
    }
    N=100;df=10;k1=1.2;b=.75;avg=100
    idf=math.log(1+(N-df+.5)/(df+.5))
    for name,tf,dl in [('D1',2,100),('D2',4,400),('D3',1,50)]:
      data['bm25'][name]=idf*tf*(k1+1)/(tf+k1*(1-b+b*dl/avg))
    data['bm25']['idf']=idf
    p=[.6,.3,.1];q=[.4,.4,.2]
    accepted=[min(a,b) for a,b in zip(p,q)];r=[max(a-b,0) for a,b in zip(p,q)]
    reject=1-sum(accepted)
    data['speculative']={'p':p,'q':q,'accept_rates':[min(1,a/b) for a,b in zip(p,q)],'accepted_mass':accepted,'reject_mass':reject,'residual':[x/reject for x in r]}
    assert abs(sum(w)-1)<1e-12
    assert data['kv_gib']==4
    assert data['rrf']['B']>data['rrf']['A']>data['rrf']['C']
    assert abs(data['pass_at_2_n10_c3']-0.5333333333333333)<1e-12
    for i in range(3): assert abs(accepted[i]+reject*data['speculative']['residual'][i]-p[i])<1e-12
    data['scope']='Author-selected arithmetic verified with Python; no commercial LLM or GPU benchmark run.'
    out=Path(__file__).with_name('numeric_results.json');out.write_text(json.dumps(data,ensure_ascii=False,indent=2)); print(json.dumps(data,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
```


<span id="code-runtime_witnesses-py"></span>


## 运行链路程序

[查看对应本地文件](../checks/runtime_witnesses.py)

```
"""Small, offline correctness witnesses; Python 3.10+, standard library only.
No network, external effects, commercial LLM calls, GPU benchmarks or training.
The tiny decoder uses fixed weights and absolute positions, not a product model.
"""
from __future__ import annotations
import codecs
import json
import math
import unittest
from pathlib import Path


def softmax(xs: list[float]) -> list[float]:
    m = max(xs)
    es = [math.exp(x-m) for x in xs]
    return [x/sum(es) for x in es]


def dot(x: list[float], y: list[float]) -> float:
    if len(x) != len(y):
        raise ValueError('dot dimension mismatch')
    return sum(a*b for a,b in zip(x,y))


def project(x: list[float], w: list[list[float]]) -> list[float]:
    if len(x) != len(w):
        raise ValueError('projection dimension mismatch')
    return [sum(x[i]*w[i][j] for i in range(len(x))) for j in range(len(w[0]))]


def weights(rows: int, cols: int, seed: int) -> list[list[float]]:
    return [[math.sin((i+1)*13+(j+1)*7+seed)*.3 for j in range(cols)] for i in range(rows)]


def norm(x: list[float]) -> list[float]:
    mean = sum(x)/len(x)
    var = sum((a-mean)**2 for a in x)/len(x)
    return [(a-mean)/math.sqrt(var+1e-5) for a in x]


class TinyDecoder:
    """Two causal pre-LN layers, width 4, one head, FFN width 8, vocab 8."""
    def __init__(self):
        self.emb = weights(8,4,1)
        self.lm_head = weights(4,8,2)
        self.layers = [dict(q=weights(4,4,10+l), k=weights(4,4,20+l),
                            v=weights(4,4,30+l), o=weights(4,4,40+l),
                            up=weights(4,8,50+l), down=weights(8,4,60+l)) for l in range(2)]

    def forward(self, ids: list[int], cache=None, position_start: int | None=None):
        if not ids or any(type(t) is not int or not 0 <= t < 8 for t in ids):
            raise ValueError('nonempty token IDs in [0,8) required')
        old = cache if cache is not None else [{'k':[], 'v':[]} for _ in self.layers]
        past = len(old[0]['k'])
        if any(len(c['k']) != past or len(c['v']) != past for c in old):
            raise ValueError('inconsistent cache lengths')
        start = past if position_start is None else position_start
        hs = [[self.emb[t][j]+.1*math.sin((start+i+1)/(j+1)) for j in range(4)] for i,t in enumerate(ids)]
        updated=[]; trace=[]
        for li,p in enumerate(self.layers):
            n=[norm(x) for x in hs]
            qs=[project(x,p['q']) for x in n]
            ks=old[li]['k']+[project(x,p['k']) for x in n]
            vs=old[li]['v']+[project(x,p['v']) for x in n]
            out=[]; atts=[]
            for i,q in enumerate(qs):
                visible=past+i+1
                a=softmax([dot(q,k)/2 for k in ks[:visible]])
                agg=[sum(a[j]*vs[j][d] for j in range(visible)) for d in range(4)]
                att=project(agg,p['o'])
                r=[x+y for x,y in zip(hs[i],att)]
                ff=project([max(x,0) for x in project(norm(r),p['up'])],p['down'])
                out.append([x+y for x,y in zip(r,ff)])
                atts.append(a)
            hs=out; updated.append({'k':ks,'v':vs})
            trace.append({'layer':li,'new_query_shape':[len(ids),4],
                          'key_shape':[len(ks),4], 'visible_counts':[past+i+1 for i in range(len(ids))],
                          'attention_rows':atts})
        logits=[project(norm(x),self.lm_head) for x in hs]
        return logits,updated,trace


def attention_loss(q,ks,vs,grad):
    a=softmax([dot(q,k)/math.sqrt(len(q)) for k in ks])
    out=[sum(a[j]*vs[j][d] for j in range(len(ks))) for d in range(len(vs[0]))]
    return dot(out,grad),a,out


def query_gradient(q,ks,vs,grad):
    _,a,_=attention_loss(q,ks,vs,grad)
    da=[dot(v,grad) for v in vs]
    center=sum(x*y for x,y in zip(a,da))
    ds=[x*(y-center) for x,y in zip(a,da)]
    return [sum(ds[j]*ks[j][d] for j in range(len(ks)))/math.sqrt(len(q)) for d in range(len(q))]


def parse_sse_chunks(chunks: list[bytes]):
    """Minimal LF-delimited teaching parser, not the full EventSource standard."""
    decoder=codecs.getincrementaldecoder('utf-8')()
    buf='';events=[]
    for chunk in chunks:
        buf+=decoder.decode(chunk)
        while '\n\n' in buf:
            event,buf=buf.split('\n\n',1)
            data='\n'.join(line[5:].lstrip(' ') for line in event.split('\n') if line.startswith('data:'))
            if data: events.append(json.loads(data))
    buf+=decoder.decode(b'',final=True)
    if buf.strip(): raise ValueError('incomplete event: do not execute')
    return events


def apply_event(state: str, event: str) -> str:
    transitions={('pending','start'):'running',('running','timeout'):'unknown',
                 ('running','success'):'succeeded',('unknown','verified_applied'):'succeeded',
                 ('unknown','verified_not_applied'):'retryable'}
    if (state,event) not in transitions:
        raise ValueError(f'illegal transition {state}/{event}')
    return transitions[(state,event)]


class WitnessTests(unittest.TestCase):
    def test_attention_hand_calculation(self):
        _,a,out=attention_loss([1,1],[[1,0],[0,1],[1,1]],[[1,2],[3,4],[4,6]],[1,1])
        self.assertAlmostEqual(out[0],3.00697969,places=6)
        self.assertAlmostEqual(sum(a),1)

    def test_query_gradient_finite_difference(self):
        q=[.4,-.7];ks=[[1,0],[0,1],[1,1]];vs=[[1,2],[3,4],[4,6]];g=[.3,-.2]
        analytic=query_gradient(q,ks,vs,g);eps=1e-6
        for i in range(2):
            plus=q.copy();minus=q.copy();plus[i]+=eps;minus[i]-=eps
            numeric=(attention_loss(plus,ks,vs,g)[0]-attention_loss(minus,ks,vs,g)[0])/(2*eps)
            self.assertAlmostEqual(analytic[i],numeric,places=8)

    def test_prefill_decode_equivalence(self):
        m=TinyDecoder();ids=[1,2,3,4,5]
        full,_,_=m.forward(ids)
        _,cache,_=m.forward(ids[:3])
        for i in range(3,len(ids)):
            got,cache,_=m.forward([ids[i]],cache)
            for a,b in zip(got[0],full[i]):self.assertAlmostEqual(a,b,places=12)

    def test_chunk_decode_equivalence(self):
        m=TinyDecoder();full,_,_=m.forward([1,2,3,4,5])
        _,cache,_=m.forward([1,2,3]);got,_,trace=m.forward([4,5],cache)
        self.assertEqual(trace[0]['visible_counts'],[4,5])
        for i in range(2):
            for a,b in zip(got[i],full[i+3]):self.assertAlmostEqual(a,b,places=12)

    def test_wrong_position_is_detectable(self):
        m=TinyDecoder();_,cache,_=m.forward([1,2,3])
        good,_,_=m.forward([4],cache);bad,_,_=m.forward([4],cache,position_start=0)
        self.assertGreater(max(abs(a-b) for a,b in zip(good[0],bad[0])),1e-5)

    def test_prefix_edit_invalidates_suffix(self):
        m=TinyDecoder();_,old,_=m.forward([1,2,3]);right,_,_=m.forward([1,6,3,4])
        wrong,_,_=m.forward([4],old)
        self.assertGreater(max(abs(a-b) for a,b in zip(right[-1],wrong[0])),1e-5)

    def test_causal_mask_is_offset(self):
        past=3;new=2
        correct=[[j<=past+i for j in range(past+new)] for i in range(new)]
        naive=[[j<=i for j in range(past+new)] for i in range(new)]
        self.assertEqual(correct,[[True,True,True,True,False],[True]*5]);self.assertNotEqual(correct,naive)

    def test_sse_every_two_piece_byte_split(self):
        event={'kind':'arguments_done','call_id':'c19','path':'中文.py'}
        raw=('data: '+json.dumps(event,ensure_ascii=False)+'\n\n').encode()
        for i in range(len(raw)+1):self.assertEqual(parse_sse_chunks([raw[:i],raw[i:]]),[event])

    def test_sse_one_byte_chunks(self):
        event={'text':'完成'};raw=('data: '+json.dumps(event,ensure_ascii=False)+'\n\n').encode()
        self.assertEqual(parse_sse_chunks([bytes([b]) for b in raw]),[event])

    def test_sse_partial_is_not_complete(self):
        with self.assertRaises(ValueError):parse_sse_chunks([b'data: {"x":1}'])

    def test_unknown_is_not_failed(self):
        state=apply_event(apply_event('pending','start'),'timeout')
        self.assertEqual(state,'unknown')
        with self.assertRaises(ValueError):apply_event(state,'start')
        self.assertEqual(apply_event(state,'verified_applied'),'succeeded')

    def test_online_softmax_merge(self):
        m=1;l=1;u=2;new_m=3;alpha=math.exp(m-new_m)
        got=(alpha*u+10)/(alpha*l+1)
        a=softmax([1,3]);self.assertAlmostEqual(got,a[0]*2+a[1]*10)


def main():
    import io
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(WitnessTests))
    model=TinyDecoder();p,c,tr=model.forward([1,2,3]);first=max(range(8),key=lambda i:p[-1][i])
    nxt,nc,ntr=model.forward([first],c)
    report={'scope':'Deterministic teaching calculations and state/parser tests; not model capability, autonomous coding or security benchmarks.',
            'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
            'prefill_tokens':[1,2,3], 'prefill_last_logits':p[-1], 'first_greedy_token':first,
            'prefill_cache_lengths':[len(x['k']) for x in c], 'next_decode_logits':nxt[-1],
            'decode_cache_lengths':[len(x['k']) for x in nc], 'prefill_trace':tr,'decode_trace':ntr,
            'test_output':stream.getvalue()}
    Path(__file__).with_name('runtime_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(stream.getvalue());print(json.dumps({k:v for k,v in report.items() if k not in ['test_output','prefill_trace','decode_trace']},ensure_ascii=False,indent=2))
    if not result.wasSuccessful():raise SystemExit(1)
if __name__=='__main__':main()
```


<span id="old-labs"></span>


## 进阶实验

基础计算实验位于labs目录；数值与运行链路实验位于checks目录；训练、检索及故障恢复专题位于studies/labs目录。各组实验独立说明依赖、输入数据与结果范围，测试通过不代表已验证商业模型能力或生产安全。

[查看专题实验 →](studies/experiments.md)

**阅读辅助：** [运行示例索引](worked-examples.md) · [两句话穿过模型的完整数表](worked-model.md) · [数值与状态核验](example-verification.md)


<span id="concept-verification"></span>



<span id="topic-1"></span>


## 参数、表示与符号的可复算检查

F11使用完整指定的X、Wq、Wk、Wv，先做投影，再计算缩放点积和因果读取份额。所有展示值来自未舍入值的连续计算。以下代码与结果可在离线环境复核。

[标准库验证程序](../concepts/verify_concepts.py) · [完整中间结果](../concepts/results.json) · [可选PyTorch对照程序](../concepts/check_pytorch.py) · [实际框架对照结果](../validation/pytorch-comparison.json)

标准库程序有30项确定性检查；另用已安装的PyTorch 2.10.0+cpu、CPU和float64对照3个Linear投影、低层SDPA与高层MultiheadAttention，共5组对照通过。高层MHA收到同一X，底层SDPA收到已投影的Q/K/V；这验证接口层次差别，不是模型质量或GPU性能评测。


<span id="concept-baseline"></span>


### 同一算例的完整中间结果

```
{
  "X": [
    [
      1.0,
      1.0
    ],
    [
      1.0,
      -1.0
    ]
  ],
  "Wq": [
    [
      0.5,
      0.5
    ],
    [
      -0.5,
      0.5
    ]
  ],
  "Wk": [
    [
      0.5,
      0.5
    ],
    [
      0.5,
      -0.5
    ]
  ],
  "Wv": [
    [
      5.0,
      10.0
    ],
    [
      5.0,
      -10.0
    ]
  ],
  "Q": [
    [
      0.0,
      1.0
    ],
    [
      1.0,
      0.0
    ]
  ],
  "K": [
    [
      1.0,
      0.0
    ],
    [
      0.0,
      1.0
    ]
  ],
  "V": [
    [
      10.0,
      0.0
    ],
    [
      0.0,
      20.0
    ]
  ],
  "dots": [
    [
      0.0,
      1.0
    ],
    [
      1.0,
      0.0
    ]
  ],
  "scores": [
    [
      0.0,
      "-infinity"
    ],
    [
      0.7071067811865475,
      0.0
    ]
  ],
  "weights": [
    [
      1.0,
      0.0
    ],
    [
      0.6697615493266569,
      0.3302384506733431
    ]
  ],
  "output": [
    [
      10.0,
      0.0
    ],
    [
      6.697615493266569,
      6.604769013466862
    ]
  ]
}
```


<span id="concept-regression"></span>


### 配套程序检查记录

| 程序组 | 检查规模 | 执行结果 |
| --- | --- | --- |
| foundations | 39 | 通过 |
| numeric\_witnesses | 独立数值见证 | 通过 |
| runtime\_witnesses | 12 | 通过 |
| examples\_engine | 34 | 通过 |
| examples\_extra | 60 | 通过 |
| examples\_chain | 14 | 通过 |
| studies | 49 | 通过 |
| reading\_notes | 10个实验 | 通过 |
| new\_concepts | 30 | 通过 |

[运行汇总](../validation/current-tests/summary.json) · [术语使用位置清单](../validation/first-use-coverage.json) · [概念定义数据](../concepts/definitions.json)

术语清单包含120项定义，按指定模式扫描143个阅读页，针对首次语义使用安排514项就地说明；F11另按完整依赖链编写。扫描不包含目录文字与练习答案，也不能证明已经穷尽所有术语或所有可能的阅读歧义。数值和状态测试验证所列对象，不代表运行了真实商业Agent。

AI系统工程：从基础到内部  
[全书目录](contents.md) · [术语与符号](glossary.md) · [参考资料](sources.md)