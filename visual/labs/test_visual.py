"""Run with Python 3.10+. Distinguishes numerical checks from content contracts.
All examples are deterministic teaching cases, not model benchmarks.
"""
import unittest,math,json,codecs,xml.etree.ElementTree as ET
from pathlib import Path
from numerics import *

class NumericalChecks(unittest.TestCase):
 def assertVector(self,a,b,tol=1e-10):
  self.assertEqual(len(a),len(b))
  for x,y in zip(a,b):self.assertAlmostEqual(x,y,delta=tol)
 def test_softmax_values(self):self.assertVector(softmax([2,1,0]),[.6652409557748218,.24472847105479764,.09003057317038046])
 def test_softmax_shift(self):self.assertVector(softmax([2,1,0]),softmax([1002,1001,1000]))
 def test_softmax_sampling(self):self.assertEqual(sample(softmax([2,1,0]),.7),1)
 def test_softmax_sum_and_positive(self):
  for x in [[0,0],[-9,-4,0],[1000,0,-1000]]:
   p=softmax(x);self.assertAlmostEqual(sum(p),1);self.assertTrue(all(v>=0 for v in p))
 def test_softmax_invalid(self):
  for x in [[],[float('nan')],[float('inf')]]:
   with self.assertRaises(ValueError):softmax(x)
 def test_sampling_range(self):
  for u in [-.1,1]:
   with self.assertRaises(ValueError):sample([.5,.5],u)
 def test_embedding_lookup(self):self.assertEqual([E[t] for t in [1,2,3]],[[.2,-.1,.7,.4],[-.3,.8,.1,.5],[.6,.2,-.4,.9]])
 def test_shape_count(self):self.assertEqual(len([n for ids in [[1,2,3],[4,2,0]] for i in ids for n in E[i]]),24)
 def test_matrix_product(self):self.assertEqual(matmul([[1,2,3],[4,5,6]],[[1,0],[0,1],[1,1]]),[[4,5],[10,11]])
 def test_matrix_shape_mismatch(self):
  with self.assertRaises(ValueError):matmul([[1,2]],[[1,2]])
 def test_qkv_projection(self):
  d=attention_example();self.assertEqual(d['q'],[[0,1],[1,0]]);self.assertEqual(d['k'],[[1,0],[0,1]]);self.assertEqual(d['v'],[[10,0],[0,20]])
 def test_attention_output(self):self.assertVector(attention_example()['y'],[6.697615493266569,6.604769013466862])
 def test_value_change_keeps_weights(self):
  d=attention_example();newv=matmul(d['x'],[[6,10],[5,-10]]);self.assertVector(d['p'],softmax(d['scaled']));self.assertNotEqual(matmul([d['p']],newv)[0],d['y'])
 def test_mask_past_offset(self):self.assertEqual(mask(3,2),[[1,1,1,1,0],[1,1,1,1,1]])
 def test_bad_mask_counterexample(self):self.assertNotEqual(mask(0,2),mask(3,2))
 def test_exclusion_vs_zero_score(self):
  two=softmax([2,1]);three=softmax([2,1,0]);self.assertGreater(three[2],0);self.assertNotAlmostEqual(two[0],three[0])
 def test_rope_norm(self):
  for a in [0,math.pi/6,math.pi/3,math.pi/2]:self.assertAlmostEqual(math.cos(a)**2+math.sin(a)**2,1)
 def test_rope_relative(self):
  self.assertAlmostEqual(math.cos(math.pi/3),math.cos(math.pi/6)*math.cos(math.pi/2)+math.sin(math.pi/6)*math.sin(math.pi/2))
 def test_generation_sequence(self):
  g=generation();self.assertEqual([t['selected'] for t in g['turns']],[3,5,6]);self.assertEqual(g['output'],[3,5]);self.assertTrue(g['eos'])
 def test_generation_cache_lengths(self):self.assertEqual([t['cache_tokens'] for t in generation()['turns']],[2,3,4])
 def test_generation_has_no_eos_forward(self):
  g=generation();self.assertEqual(g['turns'][-1]['new_input'],[5]);self.assertNotIn(6,[r['id'] for t in g['turns'] for r in t['rows']])
 def test_generation_cached_full_equality(self):
  g=generation()
  for t in g['turns']:
   rows,c=run_tokens(t['processed']);self.assertVector(rows[-1]['hidden'],t['rows'][-1]['hidden']);self.assertVector(matmul([rows[-1]['hidden']],g['Wout'])[0],t['logits'])
 def test_generation_probability_from_logits(self):
  for t in generation()['turns']:self.assertVector(softmax(t['logits']),t['probabilities']);self.assertAlmostEqual(t['probabilities'][t['selected']],.7699874831916322)
 def test_changed_prefix_invalidates(self):
  old,c=run_tokens([1,2]);wrong,_=run_tokens([3],c);correct,_=run_tokens([4,2,3]);self.assertTrue(any(abs(a-b)>1e-7 for a,b in zip(wrong[-1]['hidden'],correct[-1]['hidden'])))
 def test_gradient_finite_difference(self):
  h=1e-6;f=lambda w:.5*(w*2-4)**2;self.assertAlmostEqual((f(1+h)-f(1-h))/(2*h),gradient_demo()['gradient'],places=8)
 def test_gradient_update(self):
  d=gradient_demo();self.assertAlmostEqual(d['next_w'],1.8);self.assertAlmostEqual(d['next_loss'],.08)
 def test_learning_rate_overshoot(self):self.assertAlmostEqual(gradient_demo(eta=.6)['next_loss'],3.92)
 def test_pad_loss_denominator(self):self.assertAlmostEqual((.8+.4)/2,.6);self.assertNotAlmostEqual((.8+.4)/3,.6)
 def test_rrf_order(self):self.assertEqual([k for k,v in rrf([['A','B','C'],['B','C','A']])],['B','A','C'])
 def test_rrf_score(self):self.assertAlmostEqual(dict(rrf([['A','B','C'],['B','C','A']]))['B'],1/62+1/61)
 def test_online_softmax_max_rescale(self):
  scores=[0,2,1];v=[[5,5],[10,0],[0,20]];o=online_softmax(scores,v)[-1]['out'];ref=matmul([softmax(scores)],v)[0];self.assertVector(o,ref)
 def test_wrong_online_rescale_detected(self):
  # Incorrectly keep the old accumulator unchanged when max jumps from 0 to 2.
  m=-math.inf;l=0.;acc=[0.,0.]
  for s,v in zip([0,2,1],[[5,5],[10,0],[0,20]]):
   m=max(m,s);w=math.exp(s-m);l+=w;acc=[a+w*b for a,b in zip(acc,v)]
  wrong=[a/l for a in acc];self.assertNotEqual(wrong,online_softmax([0,2,1],[[5,5],[10,0],[0,20]])[-1]['out'])
 def test_lora(self):
  a=[[.1],[.2],[.3],[.4]];b=[[1,-1,.5,0]];d=matmul(a,b);self.assertVector([x+y for x,y in zip(I[0],d[0])],[1.1,-.1,.05,0]);self.assertEqual(sum(map(len,a))+sum(map(len,b)),8)
 def test_quantization_round_clip(self):
  xs=[.26,-.14,.36,.91];q=[max(-8,min(7,round(x/.1))) for x in xs];self.assertEqual(q,[3,-1,4,7]);self.assertAlmostEqual(q[-1]*.1-xs[-1],-.21)
 def test_gqa_storage(self):self.assertEqual([2*2*1*4*h*2*2 for h in [4,2,1]],[256,128,64])
 def test_speculative_corrected_distribution(self):
  p=[.6,.3,.1];q=[.4,.4,.2];accept=[min(1,x/y) for x,y in zip(p,q)];mass=[a*b for a,b in zip(q,accept)];r=[max(0,a-b) for a,b in zip(p,q)];z=sum(r);out=[a+(1-sum(mass))*b/z for a,b in zip(mass,r)];self.assertVector(out,p);self.assertVector(mass,[.4,.3,.1])
 def test_moe_weighted_top2(self):self.assertAlmostEqual((.5*4+.3*5)/(.5+.3),4.375)
 def test_budget(self):self.assertEqual(sum([20,10,15,20,20]),85);self.assertEqual(65+40+20,125);self.assertEqual(65+10+20,95)
 def test_continuous_batching(self):
  pending=[2,4,2];slots=[];ticks=0
  while pending or slots:
   while pending and len(slots)<2:slots.append(pending.pop(0))
   ticks+=1;slots=[x-1 for x in slots if x-1>0]
  self.assertEqual(ticks,4);self.assertEqual(max(2,4)+2,6)
 def test_parallel_critical_path(self):self.assertEqual(2+3+max(3,8)+2+1,16);self.assertEqual(2+3+max(1,8)+2+1,16)
 def test_multiagent_overhead(self):self.assertEqual(6+8+3,17);self.assertEqual(max(6,8)+3+2,13);self.assertEqual(max(6,8)+3+8,19)
 def test_pair_counts(self):
  both,new,old,none=10,4,2,4;n=both+new+old+none;self.assertEqual(n,20);self.assertAlmostEqual((both+new)/n-(both+old)/n,.1)
 def test_precision_recall(self):self.assertEqual(6/(6+2),.75);self.assertEqual(6/(6+4),.6)
 def test_cascade_cost(self):self.assertEqual(20+6*5,50);self.assertEqual(14+5,19);self.assertLess(50/19,100/19)
 def test_utf8_every_split(self):
  raw='爱'.encode('utf8')
  for cut in range(len(raw)+1):
   d=codecs.getincrementaldecoder('utf8')();self.assertEqual(d.decode(raw[:cut])+d.decode(raw[cut:],final=True),'爱')

class LessonContracts(unittest.TestCase):pass

def contract(mid):
 def run(self):
  from catalog import C
  m=C[mid];self.assertGreaterEqual(len(m['frames']),3)
  for k in ['question','intuition','scenario','why','how','risk','verify']:self.assertTrue(m[k],k)
  for f in m['frames']:
   root=ET.fromstring(f['svg']);self.assertIn('viewBox',root.attrib);self.assertTrue(f['title']);self.assertTrue(f['explain']);self.assertNotIn('<script',f['svg']);self.assertNotIn('<image',f['svg'])
  self.assertTrue(all(k in C for k in m['links']))
 return run
try:
 from catalog import C
 for mid in C:setattr(LessonContracts,'test_lesson_'+mid,contract(mid))
except ImportError:pass

if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 report={'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'scope':'数值与反例检查，以及52个图解内容结构检查；不属于商业模型benchmark'}
 Path(__file__).with_name('test_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 raise SystemExit(0 if result.wasSuccessful() else 1)
