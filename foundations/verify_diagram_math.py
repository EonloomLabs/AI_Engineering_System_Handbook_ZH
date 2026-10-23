"""教材节内图解数值与状态条件的可复现检验。仅使用Python标准库。"""
import json, math, unittest
from pathlib import Path
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parent.parent
class DiagramTests(unittest.TestCase):
    def test_coverage(self):
        # Figures are located by their fdiag anchor, not by a presentational
        # class: the class was renamed during the diagram rework, the anchors
        # are what the atlas and the chapter links actually point at.
        import re
        idx=json.loads((ROOT/'foundations/visual-index.json').read_text('utf8'))
        self.assertEqual(len(idx),201)
        self.assertEqual(set(r['chapter'] for r in idx),set(range(1,41)))
        for c in range(1,41):
            html=(ROOT/f'foundations/{c:02d}.html').read_text('utf8')
            anchors=re.findall(r'id="fdiag-\d\d-\d\d"',html)
            self.assertEqual(len(anchors),len([r for r in idx if r['chapter']==c]),
                             f'foundations/{c:02d}.html figure count')
            self.assertEqual(len(set(anchors)),len(anchors),
                             f'foundations/{c:02d}.html duplicate figure anchor')
    def test_shapes(self):
        assert 2*3*4==24
        assert 2*128*4096==1_048_576
    def test_padding(self):
        assert [[1,2,3],[4,2,0]]==[[1,2,3],[4,2]+[0]]
        assert [[1,1,1],[1,1,0]][1][-1]==0
    def test_embedding(self):
        E={0:[0,0,0,0],1:[.2,-.1,.7,.4],2:[-.3,.8,.1,.5],3:[.6,.2,-.4,.9],4:[.1,-.5,.9,.3],5:[-.2,.4,.5,-.6]}
        self.assertEqual([E[x] for x in [1,2,3]][1],[-.3,.8,.1,.5])
        self.assertEqual([E[x] for x in [4,2,0]][-1],[0,0,0,0])
    def test_matmul(self):
        X=[[1,2,3],[4,5,6]];W=[[1,0],[0,1],[1,1]]
        Y=[[sum(X[i][k]*W[k][j] for k in range(3)) for j in range(2)] for i in range(2)]
        self.assertEqual(Y,[[4,5],[10,11]])
        self.assertEqual(sum(a*b for a,b in zip([1,2,3],[4,5,6])),32)
    def test_softmax(self):
        z=[2,1,0];m=max(z);e=[math.exp(x-m) for x in z];p=[x/sum(e) for x in e]
        for a,b in zip(p,[.665241,.244728,.090031]):self.assertAlmostEqual(a,b,places=6)
        self.assertTrue(p[0]<=.70<p[0]+p[1])
        self.assertAlmostEqual(sum(p),1.0)
    def test_attention(self):
        q=[1,0];keys=[[1,0],[0,1]];v=[[10,0],[0,20]]
        z=[sum(a*b for a,b in zip(q,k))/math.sqrt(2) for k in keys]
        p=[math.exp(x)/sum(math.exp(y) for y in z) for x in z]
        out=[sum(p[i]*v[i][j] for i in range(2)) for j in range(2)]
        self.assertAlmostEqual(out[0],6.6976,places=4)
        self.assertAlmostEqual(out[1],6.6048,places=4)
    def test_mask_non_square(self):
        for r,abs_pos in enumerate([3,4]):
            allowed=[int(k<=abs_pos) for k in range(5)]
            self.assertEqual(allowed,[[1,1,1,1,0],[1,1,1,1,1]][r])
    def test_residual(self):
        a=[1,2];b=[.3,-.1]
        self.assertAlmostEqual(a[0]+b[0],1.3)
        self.assertAlmostEqual(a[1]+b[1],1.9)
    def test_generation_cache(self):
        # 选出 d 不会自动将它的 K/V 写入 cache
        computed=['a','b','c']; cache=len(computed)
        chosen='d'; self.assertEqual(cache,3)
        computed.append(chosen);self.assertEqual(len(computed),4)
    def test_gradient(self):
        x,y,w,lr=2,4,1,.2
        before=.5*(w*x-y)**2; grad=(w*x-y)*x
        w2=w-lr*grad;after=.5*(w2*x-y)**2
        self.assertEqual(before,2.0);self.assertEqual(grad,-4)
        self.assertAlmostEqual(w2,1.8);self.assertAlmostEqual(after,.08)
    def test_shift(self):
        seq=['我','爱','学习','EOS']
        self.assertEqual(list(zip(seq[:-1],seq[1:])),[('我','爱'),('爱','学习'),('学习','EOS')])
    def test_quantize(self):
        x,s=.26,.1
        q=round(x/s)
        self.assertEqual(q,3);self.assertAlmostEqual(q*s-x,.04)
    def test_roofline(self):
        compute=10**9/10**11;memory=2*10**8/(2*10**9)
        self.assertAlmostEqual(compute,.01)
        self.assertAlmostEqual(memory,.1)
        self.assertGreater(memory,compute)
    def test_sse_boundary(self):
        chunks=['data: {"call','_id":"a"}\n','\n']
        event=''.join(chunks)
        self.assertTrue(event.endswith('\n\n'))
        self.assertEqual(json.loads(event[6:].strip()),{'call_id':'a'})
    def test_budget(self):
        self.assertEqual(2000-500-100-200-300-100,800)
        self.assertEqual(500+100+200+300+100+800,2000)
    def test_inverted_index(self):
        docs={'D1':set('目录 排除 规则'.split()),'D2':set('文件 路径 规则'.split()),'D3':set('目录 权限 检查'.split())}
        self.assertEqual({d for d,t in docs.items() if '目录' in t},{'D1','D3'})
        self.assertEqual({d for d,t in docs.items() if '规则' in t},{'D1','D2'})
    def test_precision_recall(self):
        self.assertEqual(3/4,.75)
        self.assertEqual(3/5,.60)
    def test_paired(self):
        both,a_only,b_only,neither=13,2,4,1
        self.assertEqual(both+a_only+b_only+neither,20)
        self.assertEqual(both+a_only,15)
        self.assertEqual(both+b_only,17)
    def test_timing(self):
        self.assertEqual(sum([2,1,5,8,2]),18)
    def test_image_patch(self):
        self.assertEqual(16*16*3,768)
if __name__=='__main__': unittest.main(verbosity=2)
