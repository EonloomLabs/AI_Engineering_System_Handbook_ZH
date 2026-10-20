"""可直接运行：python3 verify_concepts.py --test 或 --results。
只依赖Python标准库。小模型参数为教学构造，不声称具备语言能力。
"""
from __future__ import annotations
import argparse, copy, json, math, unittest
from pathlib import Path
from typing import Sequence
Matrix = list[list[float]]
X = [[1.0, 1.0], [1.0, -1.0]]
WQ = [[0.5, 0.5], [-0.5, 0.5]]
WK = [[0.5, 0.5], [0.5, -0.5]]
WV = [[5.0, 10.0], [5.0, -10.0]]

def shape(a: Matrix) -> tuple[int, int]:
    if not a or not a[0] or any(len(r) != len(a[0]) for r in a):
        raise ValueError('矩阵必须非空且各行等长')
    if any(not math.isfinite(x) for r in a for x in r):
        raise ValueError('矩阵输入只接受有限数')
    return len(a), len(a[0])

def mm(a: Matrix, b: Matrix) -> Matrix:
    _, ac = shape(a); br, bc = shape(b)
    if ac != br:
        raise ValueError('矩阵乘法的内侧维度必须相同')
    return [[sum(x*b[k][j] for k,x in enumerate(r)) for j in range(bc)] for r in a]

def transpose(a: Matrix) -> Matrix:
    shape(a)
    return [list(r) for r in zip(*a)]

def softmax(xs: Sequence[float]) -> list[float]:
    if not xs or any(math.isnan(x) or x == math.inf for x in xs) or max(xs) == -math.inf:
        raise ValueError('至少需要一个有限分数，不接受NaN或正无穷')
    m = max(xs); es = [math.exp(x-m) for x in xs]; total = sum(es)
    return [e/total for e in es]

def attention(q: Matrix, k: Matrix, v: Matrix, past: int=0, causal: bool=True) -> dict:
    nq, dk = shape(q); nk, kk = shape(k); nv, _ = shape(v)
    if dk != kk or nk != nv or past < 0 or (causal and past + nq > nk):
        raise ValueError('Q/K宽度、K/V位置数或因果位置不匹配')
    dots = mm(q, transpose(k)); scores = []; weights = []
    for i,r in enumerate(dots):
        s = [x/math.sqrt(dk) if not causal or j<=past+i else -math.inf for j,x in enumerate(r)]
        scores.append(s); weights.append(softmax(s))
    return {'dots':dots,'scores':scores,'weights':weights,'output':mm(weights,v)}

def forward(x: Matrix | None=None, wq: Matrix | None=None, wk: Matrix | None=None, wv: Matrix | None=None) -> dict:
    x = copy.deepcopy(X if x is None else x)
    wq = copy.deepcopy(WQ if wq is None else wq); wk = copy.deepcopy(WK if wk is None else wk); wv = copy.deepcopy(WV if wv is None else wv)
    q,k,v = mm(x,wq), mm(x,wk), mm(x,wv)
    return {'X':x,'Wq':wq,'Wk':wk,'Wv':wv,'Q':q,'K':k,'V':v,**attention(q,k,v)}

def readable(obj):
    if isinstance(obj,float) and not math.isfinite(obj): return '-infinity' if obj<0 else str(obj)
    if isinstance(obj,list): return [readable(v) for v in obj]
    if isinstance(obj,dict): return {k:readable(v) for k,v in obj.items()}
    return obj

def results() -> dict:
    base=forward(); change_q=copy.deepcopy(WQ); change_q[0][0]=1.0
    change_v=copy.deepcopy(WV); change_v[0][0]=6.0
    out={'scope':'固定教学参数下的真实数值计算；未训练，不是商业Agent实验',
         'baseline':base,'change_only_Wq_00_to_1':forward(wq=change_q),'change_only_Wv_00_to_6':forward(wv=change_v)}
    last=attention([base['Q'][1]],base['K'],base['V'],past=1)
    out['cached_last_row']=last
    out['value_width_three']=attention([[1,0]],[[1,0],[0,1]],[[10,0,3],[0,20,7]],past=1)
    return readable(out)

class ConceptTests(unittest.TestCase):
    def close(self,a,b,places=10):
        if isinstance(a,(list,tuple)):
            self.assertEqual(len(a),len(b))
            for x,y in zip(a,b):self.close(x,y,places)
        else:self.assertAlmostEqual(a,b,places=places)
    def test_01_q_projection(self):self.close(mm(X,WQ),[[0,1],[1,0]])
    def test_02_k_projection(self):self.close(mm(X,WK),[[1,0],[0,1]])
    def test_03_v_projection(self):self.close(mm(X,WV),[[10,0],[0,20]])
    def test_04_attention_shares(self):self.close(forward()['weights'][1],[.6697615493266569,.3302384506733431])
    def test_05_output(self):self.close(forward()['output'],[[10,0],[6.697615493266569,6.604769013466862]])
    def test_06_mask(self):self.assertEqual(forward()['weights'][0],[1,0])
    def test_07_no_parameter_mutation(self):
        before=copy.deepcopy((X,WQ,WK,WV));forward();self.assertEqual(before,(X,WQ,WK,WV))
    def test_08_value_change_not_weights(self):
        w=copy.deepcopy(WV);w[0][0]=6;new=forward(wv=w);base=forward()
        self.assertEqual(new['Q'],base['Q']);self.assertEqual(new['K'],base['K']);self.close(new['weights'],base['weights']);self.close(new['output'][1][0],base['output'][1][0]+1)
    def test_09_query_change_not_value(self):
        w=copy.deepcopy(WQ);w[0][0]=1;new=forward(wq=w);base=forward()
        self.assertEqual(new['V'],base['V']);self.assertNotEqual(new['weights'][1],base['weights'][1])
    def test_10_value_scaling(self):
        v=[[2*x for x in r] for r in WV];self.close(forward(wv=v)['output'],[[2*x for x in r] for r in forward()['output']])
    def test_11_shared_weight_multiple_positions(self):
        q=mm(X,WQ);self.assertEqual(q[0],mm([X[0]],WQ)[0]);self.assertEqual(q[1],mm([X[1]],WQ)[0])
    def test_12_fused_projection(self):
        fused=[WQ[i]+WK[i]+WV[i] for i in range(2)];out=mm(X,fused);b=forward()
        self.assertEqual(out,[b['Q'][i]+b['K'][i]+b['V'][i] for i in range(2)])
    def test_13_stored_transpose(self):
        stored=transpose(WQ);self.assertEqual(mm(X,transpose(stored)),forward()['Q'])
    def test_14_variable_value_width(self):
        r=attention([[1,0]],[[1,0],[0,1]],[[10,0,3],[0,20,7]],past=1)
        self.assertEqual(shape(r['output']),(1,3));a=r['weights'][0];self.close(r['output'][0][2],a[0]*3+a[1]*7)
    def test_15_bad_shape(self):
        with self.assertRaises(ValueError):mm([[1,2]],[[1,2]])
    def test_16_bad_kv_length(self):
        with self.assertRaises(ValueError):attention([[1,2]],[[1,2]],[[1],[2]])
    def test_17_stable_softmax(self):self.close(softmax([1002,1001,1000]),softmax([2,1,0]))
    def test_18_all_masked_rejected(self):
        with self.assertRaises(ValueError):softmax([-math.inf,-math.inf])
    def test_19_cache(self):
        b=forward();self.close(attention([b['Q'][1]],b['K'],b['V'],past=1)['output'][0],b['output'][1])
    def test_20_wq_derivative(self):
        # output[1,0]=10*sigmoid(Wq[0,0]+0.5 divided by sqrt(2)); only one coefficient varies.
        b=forward();p=b['weights'][1][0];analytic=10*p*(1-p)/math.sqrt(2);eps=1e-5
        a=copy.deepcopy(WQ);c=copy.deepcopy(WQ);a[0][0]+=eps;c[0][0]-=eps
        finite=(forward(wq=a)['output'][1][0]-forward(wq=c)['output'][1][0])/(2*eps);self.close(analytic,finite,8)
    def test_21_matmul_micro(self):self.assertEqual(mm([[1,2]],[[3,4],[5,6]]),[[13,16]])
    def test_22_identity(self):self.assertEqual(mm([[3,-2]],[[1,0],[0,1]]),[[3,-2]])
    def test_23_silu(self):self.close([x/(1+math.exp(-x)) for x in [1,-1]],[.7310585786300049,-.2689414213699951])
    def test_24_kl(self):self.close(sum(p*math.log(p/q) for p,q in zip([.5,.5],[.25,.75])),.14384103622589042)
    def test_25_rrf(self):self.close(1/11+1/13,.16783216783216784)
    def test_26_adam_first(self):
        g=2; beta=.9;m=(1-beta)*g;self.close(m,.2);self.close(m/(1-beta),2)
    def test_27_pass_metrics(self):self.close(1-(1-.8)**3,.992);self.close(.8**3,.512)
    def test_28_nonsquare_mask(self):
        q=[[1,0],[0,1]];k=[[1,0],[0,1],[1,1]];v=[[1],[2],[3]]
        a=attention(q,k,v,past=1);self.assertEqual(a['weights'][0][-1],0);self.assertGreater(a['weights'][1][-1],0)
    def test_29_role_not_semantics(self):
        # The numerical algorithm sees arrays, not the language labels attached in the book.
        self.assertEqual(forward()['Q'],mm(X,WQ))
    def test_30_nans_rejected(self):
        with self.assertRaises(ValueError):mm([[math.nan]],[[1]])

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--test',action='store_true');ap.add_argument('--results',action='store_true');args=ap.parse_args()
    if args.test:
        r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ConceptTests));raise SystemExit(not r.wasSuccessful())
    print(json.dumps(results(),ensure_ascii=False,indent=2,allow_nan=False))
