from __future__ import annotations
import unittest,tempfile,json,subprocess,sys,math
from pathlib import Path
from copy import deepcopy
from context_memory import Item,pack,Memory,validate_checkpoint
from retrieval import Doc,Index,rrf,symbols
from journal import Journal
from sse_protocol import parse_sse,Calls
from statistics_lab import pass_at_k,paired_task_bootstrap,wilson,mcnemar_exact
from capstone import run as capstone_run
try:
 import numpy as np
 from numerics import Decoder,softmax,rope,cross_entropy,online_attention,dpo_loss,train_bpe,encode_bpe,speculative_sample
except ImportError:np=None

@unittest.skipIf(np is None,'NumPy未安装，数值实验未运行')
class NumericsTests(unittest.TestCase):
 def test_gradient(self):
  x=np.array([.3,-.4,1.1]);l,g=cross_entropy(x,1);eps=1e-6
  for i in range(len(x)):
   d=np.eye(len(x))[i]*eps
   self.assertAlmostEqual(g[i],(cross_entropy(x+d,1)[0]-cross_entropy(x-d,1)[0])/(2*eps),places=7)
 def test_gradient_sum_zero(self):self.assertAlmostEqual(float(cross_entropy(np.array([1.,2.,3.]),2)[1].sum()),0.)
 def test_cache_token(self):
  m=Decoder();ids=np.array([[1,3,5,7,2,8]]);full,_=m.forward(ids);cache=None;ys=[]
  for i in range(ids.shape[1]):y,cache=m.forward(ids[:,i:i+1],cache);ys.append(y)
  np.testing.assert_allclose(full,np.concatenate(ys,axis=1),atol=1e-10)
 def test_cache_chunk(self):
  m=Decoder();ids=np.array([[1,3,5,7,2,8]]);full,_=m.forward(ids);a,c=m.forward(ids[:,:3]);b,c=m.forward(ids[:,3:],c)
  np.testing.assert_allclose(full,np.concatenate([a,b],axis=1),atol=1e-10)
 def test_causal(self):
  m=Decoder();a=np.array([[1,3,5,7]]);b=np.array([[1,3,6,8]])
  np.testing.assert_allclose(m.forward(a)[0][:,:2],m.forward(b)[0][:,:2],atol=1e-12)
 def test_negative_mask_detected(self):
  m=Decoder();a=np.array([[1,3,5,7]]);b=np.array([[1,3,6,8]])
  self.assertGreater(float(np.max(np.abs(m.forward(a,causal=False)[0][:,:2]-m.forward(b,causal=False)[0][:,:2]))),1e-5)
 def test_wrong_offset_detected(self):
  m=Decoder();ids=np.array([[1,3,5,7]]);a,c=m.forward(ids[:,:3]);bad,_=m.forward(ids[:,3:],c,wrong_offset=True)
  self.assertGreater(float(np.max(np.abs(bad-m.forward(ids)[0][:,3:]))),1e-5)
 def test_rope_norm(self):
  x=np.random.default_rng(17).normal(size=(2,4,7,8));r=rope(x,np.arange(7));np.testing.assert_allclose(np.sum(x*x,-1),np.sum(r*r,-1),atol=1e-12)
 def test_softmax_stable(self):np.testing.assert_allclose(softmax(np.array([10000.,10001.])),softmax(np.array([0.,1.])))
 def test_all_masked_rejected(self):
  with self.assertRaises(ValueError):softmax(np.array([-np.inf,-np.inf]))
 def test_online(self):
  rng=np.random.default_rng(17);s=rng.normal(size=17)+1000;v=rng.normal(size=(17,5))
  for block in (1,3,8,20):np.testing.assert_allclose(online_attention(s,v,block),softmax(s)@v,atol=1e-12)
 def test_bpe_roundtrip(self):
  rules=train_bpe(['abc','abc','中文中文'],6);ts=encode_bpe('中文abc🙂',rules)
  self.assertEqual(bytes(b for t in ts for b in t).decode(),'中文abc🙂')
 def test_bpe_merge_shortens(self):self.assertLess(len(encode_bpe('abcabc',train_bpe(['abcabc']*5,5))),6)
 def test_dpo_gradient(self):
  x=-2.;eps=1e-6;loss,g=dpo_loss(x,-5,-3,-4)
  self.assertAlmostEqual(g,(dpo_loss(x+eps,-5,-3,-4)[0]-dpo_loss(x-eps,-5,-3,-4)[0])/(2*eps),places=7)
 def test_speculative_distribution(self):
  r=speculative_sample(np.array([.6,.3,.1]),np.array([.2,.5,.3]),n=20000)
  self.assertLess(max(abs(a-b) for a,b in zip(r['empirical'],r['target'])),.015)

class RetrievalTests(unittest.TestCase):
 def setUp(self):
  self.index=Index([Doc('ok','exclude repository relative path','a',2,frozenset({'alice'})),Doc('old','exclude relative path','a',1,frozenset({'alice'})),Doc('other','exclude relative path secret','b',2,frozenset({'alice'})),Doc('denied','exclude path','a',2,frozenset({'bob'}))])
 def test_acl(self):self.assertEqual([i for i,s in self.index.search('exclude path',tenant='a',principal='alice',version=2)],['ok'])
 def test_principal_cache_isolation(self):
  self.index.search('exclude',tenant='a',principal='alice',version=2)
  self.assertEqual(self.index.search('exclude',tenant='a',principal='mallory',version=2),[])
 def test_version(self):self.assertEqual(self.index.search('exclude',tenant='a',principal='alice',version=1)[0][0],'old')
 def test_update_invalidates(self):
  self.index.search('exclude',tenant='a',principal='alice',version=2);self.index.replace([])
  self.assertEqual(self.index.search('exclude',tenant='a',principal='alice',version=2),[])
 def test_rrf_duplicate(self):self.assertEqual(rrf([['a','a']])[0][1],1/61)
 def test_ast(self):self.assertEqual(symbols('def f(x):\n return x\n')[0],{'name':'f','kind':'FunctionDef','start':1,'end':2})
 def test_empty(self):self.assertEqual(self.index.search('',tenant='a',principal='alice',version=2),[])

class ContextTests(unittest.TestCase):
 def test_dependency(self):self.assertEqual(pack([Item('d',20,1),Item('u',20,9,needs=('d',))],45)['selected'],['d','u'])
 def test_required_overflow(self):
  with self.assertRaises(ValueError):pack([Item('must',30,1,True)],20)
 def test_cycle(self):
  with self.assertRaises(ValueError):pack([Item('a',1,1,needs=('b',)),Item('b',1,1,needs=('a',))],10)
 def test_missing_dependency(self):
  with self.assertRaises(ValueError):pack([Item('a',1,1,needs=('missing',))],10)
 def test_stale_evidence(self):
  s={'goal':'fix','constraints':[],'claims':[{'id':'t','status':'verified','evidence_id':'e'}],'evidence':{'e':{'version':1}},'pending':[],'version':2}
  self.assertEqual(validate_checkpoint(s,2),['stale_evidence:t'])
 def test_unbacked_claim(self):
  s={'goal':'fix','constraints':[],'claims':[{'id':'t','status':'verified','evidence_id':'x'}],'evidence':{},'pending':[],'version':2}
  self.assertEqual(validate_checkpoint(s,2),['unbacked_verified_claim:t'])
 def test_memory(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'m.db';m=Memory(path);m.add('a','rule','new',start=20,recorded=30,source_version=2,status='active');m.close();m=Memory(path)
   self.assertEqual(m.recall('a','rule',at=25,known_at=25,source_version=2)['status'],'not_found')
   self.assertEqual(m.recall('a','rule',at=25,known_at=35,source_version=2)['status'],'found')
   self.assertEqual(m.recall('b','rule',at=25,known_at=35,source_version=2)['status'],'not_found');m.close()
 def test_memory_conflict(self):
  with tempfile.TemporaryDirectory() as d:
   m=Memory(Path(d)/'m.db')
   for claim in ('new','old'):m.add('a','rule',claim,start=20,recorded=30,source_version=2,status='active')
   self.assertEqual(m.recall('a','rule',at=25,known_at=35,source_version=2)['status'],'conflict');m.close()

class ProtocolTests(unittest.TestCase):
 def test_utf8_sse(self):
  raw=('data: '+json.dumps({'text':'中文'},ensure_ascii=False)+'\r\n\r\n').encode()
  self.assertEqual(list(parse_sse([raw[i:i+1] for i in range(len(raw))])),[{'text':'中文'}])
 def test_truncated_sse(self):
  with self.assertRaises(ValueError):list(parse_sse([b'data: {"x":1}']))
 def test_not_executed_on_delta(self):
  c=Calls();c.consume({'type':'response.function_call_arguments.delta','item_id':'1','delta':'{"x":'})
  with self.assertRaises(RuntimeError):c.result()
 def test_failed_response(self):
  c=Calls();c.consume({'type':'response.completed'});c.consume({'type':'response.failed'})
  with self.assertRaises(RuntimeError):c.result()
 def test_id_conflict(self):
  c=Calls()
  for i in [1]:c.consume({'type':'response.output_item.done','item':{'type':'function_call','call_id':'x','name':'read','arguments':'{"a":1}'}})
  with self.assertRaises(ValueError):c.consume({'type':'response.output_item.done','item':{'type':'function_call','call_id':'x','name':'read','arguments':'{"a":2}'}})

class RecoveryTests(unittest.TestCase):
 def test_real_crash_and_reconcile(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'state.txt').write_text('old');db=root/'journal.sqlite'
   p=subprocess.run([sys.executable,str(Path(__file__).with_name('journal.py')),str(root),str(db),'--crash'],capture_output=True,text=True,timeout=15)
   self.assertEqual(p.returncode,75);self.assertEqual((root/'state.txt').read_text(),'new')
   j=Journal(root,db);r=j.replace('demo','op1','state.txt','old','new');self.assertFalse(r['wrote']);self.assertEqual(r['status'],'reconciled');j.close()
 def test_outside_root(self):
  with tempfile.TemporaryDirectory() as d:
   j=Journal(Path(d),Path(d)/'j.db')
   with self.assertRaises(PermissionError):j.path('../secret')
   j.close()
 def test_stale_precondition(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'s.txt').write_text('unrelated');j=Journal(root,root/'j.db')
   with self.assertRaises(RuntimeError):j.replace('t','o','s.txt','old','new')
   j.close()
 def test_id_reuse(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'s.txt').write_text('old');j=Journal(root,root/'j.db');j.replace('t','o','s.txt','old','new')
   with self.assertRaises(ValueError):j.replace('t','o','s.txt','old','different')
   j.close()
 def test_changed_after_applied(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'s.txt').write_text('old');j=Journal(root,root/'j.db');j.replace('t','o','s.txt','old','new');(root/'s.txt').write_text('later')
   with self.assertRaises(RuntimeError):j.replace('t','o','s.txt','old','new')
   j.close()
 def test_capstone_actual_patch(self):
  r=capstone_run();self.assertFalse(r['initial_passed']);self.assertTrue(r['after_patch_passed']);self.assertTrue(r['completed']);self.assertTrue(r['stale_completion_rejected'])

class StatisticsTests(unittest.TestCase):
 def test_pass_at_k(self):self.assertAlmostEqual(pass_at_k(10,2,3),.5333333333333333)
 def test_wilson(self):
  low,high=wilson(8,10);self.assertLess(low,.8);self.assertGreater(high,.8)
 def test_paired_identity(self):self.assertEqual(paired_task_bootstrap([[1],[0]],[[1],[0]])['interval_95'],[0.,0.])
 def test_mcnemar_zero(self):self.assertEqual(mcnemar_exact(0,0),1.)


@unittest.skipUnless(np is not None, 'NumPy未安装')
class AttentionBackwardTests(unittest.TestCase):
    def test_all_gradients(self):
        import attention_gradients as a
        report=a.run()
        self.assertLess(max(report['max_absolute_errors'].values()),1e-7)
    def test_future_gradient_zero(self):
        import attention_gradients as a
        q=np.ones((3,2));k=np.ones((3,2));v=np.arange(6.).reshape(3,2)
        _,cache=a.forward(q,k,v,np.tril(np.ones((3,3),dtype=bool)))
        g=np.zeros((3,2));g[0]=1
        dq,dk,dv=a.backward(g,cache)
        np.testing.assert_array_equal(dk[1:],0.)
        np.testing.assert_array_equal(dv[1:],0.)
    def test_mask_validation(self):
        import attention_gradients as a
        with self.assertRaises(ValueError):a.forward(np.ones((1,2)),np.ones((1,2)),np.ones((1,2)),[[False]])
    def test_upstream_shape(self):
        import attention_gradients as a
        _,cache=a.forward(np.ones((2,2)),np.ones((2,2)),np.ones((2,3)))
        with self.assertRaises(ValueError):a.backward(np.ones((2,2)),cache)

if __name__ == '__main__':
    unittest.main(verbosity=2)
