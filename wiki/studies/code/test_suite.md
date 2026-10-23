---
title: "test_suite.py"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# test\_suite.py

49项单元与集成测试。对应第对应各实验章。依赖：标准库；NumPy可选。

明确故障样本和断言；全绿不等于生产认证。[阅读运行说明](../experiments.md) / [查看实测结果](../results.md)

[原始Python文件](../../../studies/labs/test_suite.py) · 178行

```

<span id="L1"></span>
from __future__ import annotations
<span id="L2"></span>
import unittest,tempfile,json,subprocess,sys,math
<span id="L3"></span>
from pathlib import Path
<span id="L4"></span>
from copy import deepcopy
<span id="L5"></span>
from context_memory import Item,pack,Memory,validate_checkpoint
<span id="L6"></span>
from retrieval import Doc,Index,rrf,symbols
<span id="L7"></span>
from journal import Journal
<span id="L8"></span>
from sse_protocol import parse_sse,Calls
<span id="L9"></span>
from statistics_lab import pass_at_k,paired_task_bootstrap,wilson,mcnemar_exact
<span id="L10"></span>
from capstone import run as capstone_run
<span id="L11"></span>
try:
<span id="L12"></span>
 import numpy as np
<span id="L13"></span>
 from numerics import Decoder,softmax,rope,cross_entropy,online_attention,dpo_loss,train_bpe,encode_bpe,speculative_sample
<span id="L14"></span>
except ImportError:np=None
<span id="L15"></span>
 
<span id="L16"></span>
@unittest.skipIf(np is None,'NumPy未安装，数值实验未运行')
<span id="L17"></span>
class NumericsTests(unittest.TestCase):
<span id="L18"></span>
 def test_gradient(self):
<span id="L19"></span>
  x=np.array([.3,-.4,1.1]);l,g=cross_entropy(x,1);eps=1e-6
<span id="L20"></span>
  for i in range(len(x)):
<span id="L21"></span>
   d=np.eye(len(x))[i]*eps
<span id="L22"></span>
   self.assertAlmostEqual(g[i],(cross_entropy(x+d,1)[0]-cross_entropy(x-d,1)[0])/(2*eps),places=7)
<span id="L23"></span>
 def test_gradient_sum_zero(self):self.assertAlmostEqual(float(cross_entropy(np.array([1.,2.,3.]),2)[1].sum()),0.)
<span id="L24"></span>
 def test_cache_token(self):
<span id="L25"></span>
  m=Decoder();ids=np.array([[1,3,5,7,2,8]]);full,_=m.forward(ids);cache=None;ys=[]
<span id="L26"></span>
  for i in range(ids.shape[1]):y,cache=m.forward(ids[:,i:i+1],cache);ys.append(y)
<span id="L27"></span>
  np.testing.assert_allclose(full,np.concatenate(ys,axis=1),atol=1e-10)
<span id="L28"></span>
 def test_cache_chunk(self):
<span id="L29"></span>
  m=Decoder();ids=np.array([[1,3,5,7,2,8]]);full,_=m.forward(ids);a,c=m.forward(ids[:,:3]);b,c=m.forward(ids[:,3:],c)
<span id="L30"></span>
  np.testing.assert_allclose(full,np.concatenate([a,b],axis=1),atol=1e-10)
<span id="L31"></span>
 def test_causal(self):
<span id="L32"></span>
  m=Decoder();a=np.array([[1,3,5,7]]);b=np.array([[1,3,6,8]])
<span id="L33"></span>
  np.testing.assert_allclose(m.forward(a)[0][:,:2],m.forward(b)[0][:,:2],atol=1e-12)
<span id="L34"></span>
 def test_negative_mask_detected(self):
<span id="L35"></span>
  m=Decoder();a=np.array([[1,3,5,7]]);b=np.array([[1,3,6,8]])
<span id="L36"></span>
  self.assertGreater(float(np.max(np.abs(m.forward(a,causal=False)[0][:,:2]-m.forward(b,causal=False)[0][:,:2]))),1e-5)
<span id="L37"></span>
 def test_wrong_offset_detected(self):
<span id="L38"></span>
  m=Decoder();ids=np.array([[1,3,5,7]]);a,c=m.forward(ids[:,:3]);bad,_=m.forward(ids[:,3:],c,wrong_offset=True)
<span id="L39"></span>
  self.assertGreater(float(np.max(np.abs(bad-m.forward(ids)[0][:,3:]))),1e-5)
<span id="L40"></span>
 def test_rope_norm(self):
<span id="L41"></span>
  x=np.random.default_rng(17).normal(size=(2,4,7,8));r=rope(x,np.arange(7));np.testing.assert_allclose(np.sum(x*x,-1),np.sum(r*r,-1),atol=1e-12)
<span id="L42"></span>
 def test_softmax_stable(self):np.testing.assert_allclose(softmax(np.array([10000.,10001.])),softmax(np.array([0.,1.])))
<span id="L43"></span>
 def test_all_masked_rejected(self):
<span id="L44"></span>
  with self.assertRaises(ValueError):softmax(np.array([-np.inf,-np.inf]))
<span id="L45"></span>
 def test_online(self):
<span id="L46"></span>
  rng=np.random.default_rng(17);s=rng.normal(size=17)+1000;v=rng.normal(size=(17,5))
<span id="L47"></span>
  for block in (1,3,8,20):np.testing.assert_allclose(online_attention(s,v,block),softmax(s)@v,atol=1e-12)
<span id="L48"></span>
 def test_bpe_roundtrip(self):
<span id="L49"></span>
  rules=train_bpe(['abc','abc','中文中文'],6);ts=encode_bpe('中文abc🙂',rules)
<span id="L50"></span>
  self.assertEqual(bytes(b for t in ts for b in t).decode(),'中文abc🙂')
<span id="L51"></span>
 def test_bpe_merge_shortens(self):self.assertLess(len(encode_bpe('abcabc',train_bpe(['abcabc']*5,5))),6)
<span id="L52"></span>
 def test_dpo_gradient(self):
<span id="L53"></span>
  x=-2.;eps=1e-6;loss,g=dpo_loss(x,-5,-3,-4)
<span id="L54"></span>
  self.assertAlmostEqual(g,(dpo_loss(x+eps,-5,-3,-4)[0]-dpo_loss(x-eps,-5,-3,-4)[0])/(2*eps),places=7)
<span id="L55"></span>
 def test_speculative_distribution(self):
<span id="L56"></span>
  r=speculative_sample(np.array([.6,.3,.1]),np.array([.2,.5,.3]),n=20000)
<span id="L57"></span>
  self.assertLess(max(abs(a-b) for a,b in zip(r['empirical'],r['target'])),.015)
<span id="L58"></span>
 
<span id="L59"></span>
class RetrievalTests(unittest.TestCase):
<span id="L60"></span>
 def setUp(self):
<span id="L61"></span>
  self.index=Index([Doc('ok','exclude repository relative path','a',2,frozenset({'alice'})),Doc('old','exclude relative path','a',1,frozenset({'alice'})),Doc('other','exclude relative path secret','b',2,frozenset({'alice'})),Doc('denied','exclude path','a',2,frozenset({'bob'}))])
<span id="L62"></span>
 def test_acl(self):self.assertEqual([i for i,s in self.index.search('exclude path',tenant='a',principal='alice',version=2)],['ok'])
<span id="L63"></span>
 def test_principal_cache_isolation(self):
<span id="L64"></span>
  self.index.search('exclude',tenant='a',principal='alice',version=2)
<span id="L65"></span>
  self.assertEqual(self.index.search('exclude',tenant='a',principal='mallory',version=2),[])
<span id="L66"></span>
 def test_version(self):self.assertEqual(self.index.search('exclude',tenant='a',principal='alice',version=1)[0][0],'old')
<span id="L67"></span>
 def test_update_invalidates(self):
<span id="L68"></span>
  self.index.search('exclude',tenant='a',principal='alice',version=2);self.index.replace([])
<span id="L69"></span>
  self.assertEqual(self.index.search('exclude',tenant='a',principal='alice',version=2),[])
<span id="L70"></span>
 def test_rrf_duplicate(self):self.assertEqual(rrf([['a','a']])[0][1],1/61)
<span id="L71"></span>
 def test_ast(self):self.assertEqual(symbols('def f(x):\n return x\n')[0],{'name':'f','kind':'FunctionDef','start':1,'end':2})
<span id="L72"></span>
 def test_empty(self):self.assertEqual(self.index.search('',tenant='a',principal='alice',version=2),[])
<span id="L73"></span>
 
<span id="L74"></span>
class ContextTests(unittest.TestCase):
<span id="L75"></span>
 def test_dependency(self):self.assertEqual(pack([Item('d',20,1),Item('u',20,9,needs=('d',))],45)['selected'],['d','u'])
<span id="L76"></span>
 def test_required_overflow(self):
<span id="L77"></span>
  with self.assertRaises(ValueError):pack([Item('must',30,1,True)],20)
<span id="L78"></span>
 def test_cycle(self):
<span id="L79"></span>
  with self.assertRaises(ValueError):pack([Item('a',1,1,needs=('b',)),Item('b',1,1,needs=('a',))],10)
<span id="L80"></span>
 def test_missing_dependency(self):
<span id="L81"></span>
  with self.assertRaises(ValueError):pack([Item('a',1,1,needs=('missing',))],10)
<span id="L82"></span>
 def test_stale_evidence(self):
<span id="L83"></span>
  s={'goal':'fix','constraints':[],'claims':[{'id':'t','status':'verified','evidence_id':'e'}],'evidence':{'e':{'version':1}},'pending':[],'version':2}
<span id="L84"></span>
  self.assertEqual(validate_checkpoint(s,2),['stale_evidence:t'])
<span id="L85"></span>
 def test_unbacked_claim(self):
<span id="L86"></span>
  s={'goal':'fix','constraints':[],'claims':[{'id':'t','status':'verified','evidence_id':'x'}],'evidence':{},'pending':[],'version':2}
<span id="L87"></span>
  self.assertEqual(validate_checkpoint(s,2),['unbacked_verified_claim:t'])
<span id="L88"></span>
 def test_memory(self):
<span id="L89"></span>
  with tempfile.TemporaryDirectory() as d:
<span id="L90"></span>
   path=Path(d)/'m.db';m=Memory(path);m.add('a','rule','new',start=20,recorded=30,source_version=2,status='active');m.close();m=Memory(path)
<span id="L91"></span>
   self.assertEqual(m.recall('a','rule',at=25,known_at=25,source_version=2)['status'],'not_found')
<span id="L92"></span>
   self.assertEqual(m.recall('a','rule',at=25,known_at=35,source_version=2)['status'],'found')
<span id="L93"></span>
   self.assertEqual(m.recall('b','rule',at=25,known_at=35,source_version=2)['status'],'not_found');m.close()
<span id="L94"></span>
 def test_memory_conflict(self):
<span id="L95"></span>
  with tempfile.TemporaryDirectory() as d:
<span id="L96"></span>
   m=Memory(Path(d)/'m.db')
<span id="L97"></span>
   for claim in ('new','old'):m.add('a','rule',claim,start=20,recorded=30,source_version=2,status='active')
<span id="L98"></span>
   self.assertEqual(m.recall('a','rule',at=25,known_at=35,source_version=2)['status'],'conflict');m.close()
<span id="L99"></span>
 
<span id="L100"></span>
class ProtocolTests(unittest.TestCase):
<span id="L101"></span>
 def test_utf8_sse(self):
<span id="L102"></span>
  raw=('data: '+json.dumps({'text':'中文'},ensure_ascii=False)+'\r\n\r\n').encode()
<span id="L103"></span>
  self.assertEqual(list(parse_sse([raw[i:i+1] for i in range(len(raw))])),[{'text':'中文'}])
<span id="L104"></span>
 def test_truncated_sse(self):
<span id="L105"></span>
  with self.assertRaises(ValueError):list(parse_sse([b'data: {"x":1}']))
<span id="L106"></span>
 def test_not_executed_on_delta(self):
<span id="L107"></span>
  c=Calls();c.consume({'type':'response.function_call_arguments.delta','item_id':'1','delta':'{"x":'})
<span id="L108"></span>
  with self.assertRaises(RuntimeError):c.result()
<span id="L109"></span>
 def test_failed_response(self):
<span id="L110"></span>
  c=Calls();c.consume({'type':'response.completed'});c.consume({'type':'response.failed'})
<span id="L111"></span>
  with self.assertRaises(RuntimeError):c.result()
<span id="L112"></span>
 def test_id_conflict(self):
<span id="L113"></span>
  c=Calls()
<span id="L114"></span>
  for i in [1]:c.consume({'type':'response.output_item.done','item':{'type':'function_call','call_id':'x','name':'read','arguments':'{"a":1}'}})
<span id="L115"></span>
  with self.assertRaises(ValueError):c.consume({'type':'response.output_item.done','item':{'type':'function_call','call_id':'x','name':'read','arguments':'{"a":2}'}})
<span id="L116"></span>
 
<span id="L117"></span>
class RecoveryTests(unittest.TestCase):
<span id="L118"></span>
 def test_real_crash_and_reconcile(self):
<span id="L119"></span>
  with tempfile.TemporaryDirectory() as d:
<span id="L120"></span>
   root=Path(d);(root/'state.txt').write_text('old');db=root/'journal.sqlite'
<span id="L121"></span>
   p=subprocess.run([sys.executable,str(Path(__file__).with_name('journal.py')),str(root),str(db),'--crash'],capture_output=True,text=True,timeout=15)
<span id="L122"></span>
   self.assertEqual(p.returncode,75);self.assertEqual((root/'state.txt').read_text(),'new')
<span id="L123"></span>
   j=Journal(root,db);r=j.replace('demo','op1','state.txt','old','new');self.assertFalse(r['wrote']);self.assertEqual(r['status'],'reconciled');j.close()
<span id="L124"></span>
 def test_outside_root(self):
<span id="L125"></span>
  with tempfile.TemporaryDirectory() as d:
<span id="L126"></span>
   j=Journal(Path(d),Path(d)/'j.db')
<span id="L127"></span>
   with self.assertRaises(PermissionError):j.path('../secret')
<span id="L128"></span>
   j.close()
<span id="L129"></span>
 def test_stale_precondition(self):
<span id="L130"></span>
  with tempfile.TemporaryDirectory() as d:
<span id="L131"></span>
   root=Path(d);(root/'s.txt').write_text('unrelated');j=Journal(root,root/'j.db')
<span id="L132"></span>
   with self.assertRaises(RuntimeError):j.replace('t','o','s.txt','old','new')
<span id="L133"></span>
   j.close()
<span id="L134"></span>
 def test_id_reuse(self):
<span id="L135"></span>
  with tempfile.TemporaryDirectory() as d:
<span id="L136"></span>
   root=Path(d);(root/'s.txt').write_text('old');j=Journal(root,root/'j.db');j.replace('t','o','s.txt','old','new')
<span id="L137"></span>
   with self.assertRaises(ValueError):j.replace('t','o','s.txt','old','different')
<span id="L138"></span>
   j.close()
<span id="L139"></span>
 def test_changed_after_applied(self):
<span id="L140"></span>
  with tempfile.TemporaryDirectory() as d:
<span id="L141"></span>
   root=Path(d);(root/'s.txt').write_text('old');j=Journal(root,root/'j.db');j.replace('t','o','s.txt','old','new');(root/'s.txt').write_text('later')
<span id="L142"></span>
   with self.assertRaises(RuntimeError):j.replace('t','o','s.txt','old','new')
<span id="L143"></span>
   j.close()
<span id="L144"></span>
 def test_capstone_actual_patch(self):
<span id="L145"></span>
  r=capstone_run();self.assertFalse(r['initial_passed']);self.assertTrue(r['after_patch_passed']);self.assertTrue(r['completed']);self.assertTrue(r['stale_completion_rejected'])
<span id="L146"></span>
 
<span id="L147"></span>
class StatisticsTests(unittest.TestCase):
<span id="L148"></span>
 def test_pass_at_k(self):self.assertAlmostEqual(pass_at_k(10,2,3),.5333333333333333)
<span id="L149"></span>
 def test_wilson(self):
<span id="L150"></span>
  low,high=wilson(8,10);self.assertLess(low,.8);self.assertGreater(high,.8)
<span id="L151"></span>
 def test_paired_identity(self):self.assertEqual(paired_task_bootstrap([[1],[0]],[[1],[0]])['interval_95'],[0.,0.])
<span id="L152"></span>
 def test_mcnemar_zero(self):self.assertEqual(mcnemar_exact(0,0),1.)
<span id="L153"></span>
 
<span id="L154"></span>
 
<span id="L155"></span>
@unittest.skipUnless(np is not None, 'NumPy未安装')
<span id="L156"></span>
class AttentionBackwardTests(unittest.TestCase):
<span id="L157"></span>
    def test_all_gradients(self):
<span id="L158"></span>
        import attention_gradients as a
<span id="L159"></span>
        report=a.run()
<span id="L160"></span>
        self.assertLess(max(report['max_absolute_errors'].values()),1e-7)
<span id="L161"></span>
    def test_future_gradient_zero(self):
<span id="L162"></span>
        import attention_gradients as a
<span id="L163"></span>
        q=np.ones((3,2));k=np.ones((3,2));v=np.arange(6.).reshape(3,2)
<span id="L164"></span>
        _,cache=a.forward(q,k,v,np.tril(np.ones((3,3),dtype=bool)))
<span id="L165"></span>
        g=np.zeros((3,2));g[0]=1
<span id="L166"></span>
        dq,dk,dv=a.backward(g,cache)
<span id="L167"></span>
        np.testing.assert_array_equal(dk[1:],0.)
<span id="L168"></span>
        np.testing.assert_array_equal(dv[1:],0.)
<span id="L169"></span>
    def test_mask_validation(self):
<span id="L170"></span>
        import attention_gradients as a
<span id="L171"></span>
        with self.assertRaises(ValueError):a.forward(np.ones((1,2)),np.ones((1,2)),np.ones((1,2)),[[False]])
<span id="L172"></span>
    def test_upstream_shape(self):
<span id="L173"></span>
        import attention_gradients as a
<span id="L174"></span>
        _,cache=a.forward(np.ones((2,2)),np.ones((2,2)),np.ones((2,3)))
<span id="L175"></span>
        with self.assertRaises(ValueError):a.backward(np.ones((2,2)),cache)
<span id="L176"></span>
 
<span id="L177"></span>
if __name__ == '__main__':
<span id="L178"></span>
    unittest.main(verbosity=2)
```

AI系统工程：从基础到内部  
[全书目录](../../contents.md) · [术语与符号](../../glossary.md) · [参考资料](../../sources.md)