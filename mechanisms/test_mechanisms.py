"""Deterministic checks for the book's declared microexamples. No external API calls.
Run: python test_mechanisms.py
The numeric checks do not prove quality of a commercial model or all natural-language explanations.
"""
import unittest,math,json,copy,sys,xml.etree.ElementTree as ET
from pathlib import Path
from cases import C
from figures import draw_case
from walk_cases import W,draw_walk

def softmax(x):
 m=max(x);e=[math.exp(v-m) for v in x];return [v/sum(e) for v in e]
def mm(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def finite(f,x,i,eps=1e-6):
 p=x.copy();m=x.copy();p[i]+=eps;m[i]-=eps;return (f(p)-f(m))/(2*eps)
def rr(lists,k=60):
 out={}
 for l in lists:
  for rank,d in enumerate(l,1):out[d]=out.get(d,0)+1/(k+rank)
 return out
class NumericChecks(unittest.TestCase):
 def assertVec(self,a,b,tol=1e-6):
  self.assertEqual(len(a),len(b))
  for x,y in zip(a,b):self.assertAlmostEqual(x,y,delta=tol)
 def test_qkv_projection(self):
  x=[[1,0],[0,1]];w=[[1,0],[1,1]];self.assertEqual(mm(x,w),w)
 def test_attention_equal_scores(self):
  q=[1,1];K=[[1,0],[0,1]];p=softmax([dot(q,k)/math.sqrt(2) for k in K]);self.assertVec(p,[.5,.5]);self.assertEqual(mm([p],[[2,0],[0,4]]),[[1,2]])
 def test_value_change_only(self):
  p=[.5,.5];self.assertEqual(mm([p],[[2,0],[0,8]]),[[1,4]])
 def test_softmax_numbers(self):self.assertVec(softmax([2,1,0]),[.6652409557748218,.24472847105479764,.09003057317038046],1e-12)
 def test_softmax_translation(self):self.assertVec(softmax([2,1,0]),softmax([0,-1,-2]),1e-12)
 def test_softmax_sample(self):
  p=softmax([2,1,0]);self.assertTrue(p[0]<=.7<p[0]+p[1])
 def test_layernorm(self):
  x=[2,4];m=sum(x)/2;v=sum((a-m)**2 for a in x)/2;self.assertVec([(a-m)/math.sqrt(v) for a in x],[-1,1])
 def test_mask_offset(self):self.assertEqual([[k<=3+q for k in range(5)] for q in range(2)],[[True,True,True,True,False],[True]*5])
 def test_wrong_mask_changes_result(self):
  v=[1,2,3,4,5];correct=[sum(v[:4])/4,sum(v)/5];wrong=[v[0],sum(v[:2])/2];self.assertEqual(correct,[2.5,3]);self.assertEqual(wrong,[1,1.5]);self.assertNotEqual(correct,wrong)
 def test_rope_relative(self):
  R=lambda x,t:[x[0]*math.cos(t)-x[1]*math.sin(t),x[0]*math.sin(t)+x[1]*math.cos(t)]
  self.assertAlmostEqual(dot(R([1,0],0),R([1,0],math.pi/2)),0,places=12)
  self.assertAlmostEqual(dot(R([1,0],math.pi/2),R([1,0],math.pi)),0,places=12)
 def test_gqa_counts(self):
  self.assertEqual(2*2*3*2,24);self.assertEqual(2*4*3*2,48)
 def test_attention_backward_P(self):
  V=[[2,0],[0,4]];g=[1,1];self.assertVec([dot(g,v) for v in V],[2,4])
 def test_attention_backward_S(self):
  p=[.25,.75];g=[2,4];mean=dot(p,g);d=[p[i]*(g[i]-mean) for i in range(2)];self.assertVec(d,[-.375,.375]);self.assertAlmostEqual(sum(d),0)
 def test_selected_not_cached(self):
  cache=[1,2];selected=3;self.assertNotIn(selected,cache);cache.append(selected);self.assertEqual(len(cache),3)
 def test_temperature_distribution(self):
  self.assertVec(softmax([1,.5,0]),[.506480391055654,.3071958857184984,.1863237232258476],1e-12)
 def test_top_p_boundary_changes(self):
  a=softmax([2,1,0]);b=softmax([1,.5,0]);self.assertGreater(sum(a[:2]),.9);self.assertLess(sum(b[:2]),.9)
 def test_shifted_labels(self):
  seq=['我','爱','学习','EOS'];self.assertEqual(seq[:-1],['我','爱','学习']);self.assertEqual(seq[1:],['爱','学习','EOS'])
 def test_adam_first_step(self):
  g=2.;m=.1*g;v=.001*g*g;self.assertAlmostEqual(m/.1,2);self.assertAlmostEqual(v/.001,4);self.assertAlmostEqual(1-.1*1-.1*.01*1,.899)
 def test_train_memory_bookkeeping(self):self.assertEqual(1000*(2+2+4+4+4),16000)
 def test_dpo_margin(self):
  margin=math.log(.3/.2)-math.log(.1/.1);p=1/(1+math.exp(-margin));self.assertAlmostEqual(p,.6);self.assertAlmostEqual(-math.log(p),.5108256237659907)
 def test_group_reward(self):
  x=[0,1,1];mean=sum(x)/3;self.assertVec([t-mean for t in x],[-2/3,1/3,1/3])
 def test_moe_renormalize(self):
  self.assertVec([.6/.9,.3/.9],[2/3,1/3]);self.assertVec([.6/.8,.2/.8],[.75,.25])
 def test_lora_parameter_counts(self):self.assertEqual(8*8,64);self.assertEqual(8*2+2*8,32)
 def test_cache_size(self):self.assertEqual(1*2*2*2*3*4*2,192);self.assertEqual(1*2*2*2*4*4*2,256)
 def test_online_softmax(self):
  e=[1,2];full=(e[0]*10+e[1]*20)/sum(e);renorm=(.5*10+1*20)/(.5+1);self.assertAlmostEqual(full,renorm);self.assertAlmostEqual(full,50/3)
 def test_paging(self):
  blocks=[6,1,9];positions=[(blocks[p//2],p%2) for p in range(5)];self.assertEqual(positions,[(6,0),(6,1),(1,0),(1,1),(9,0)])
 def test_continuous_batch(self):
  slots=[['A','C','C'],['B','B','B']];self.assertEqual(sum(v=='C' for row in slots for v in row),2);self.assertEqual(len(slots[0]),3)
 def test_latency(self):self.assertAlmostEqual(.2+.3,.5);self.assertAlmostEqual(.2+.3+4*.05,.7)
 def test_speculative_mass(self):
  q=[.8,.2];p=[.5,.5];accept=[min(q[i],p[i]) for i in range(2)];reject=1-sum(accept);r=[max(p[i]-q[i],0) for i in range(2)];r=[v/sum(r) for v in r];self.assertVec([accept[i]+reject*r[i] for i in range(2)],p)
 def test_agent_two_model_requests(self):
  rows=C['Q033']['rows'];requests=[r for r in rows if r[0]=='宿主→模型'];self.assertEqual(len(requests),2);self.assertIn('两轮',C['Q033']['title'])
 def test_utf8_boundary(self):
  b='爱'.encode();self.assertEqual(list(b),[0xe7,0x88,0xb1]);self.assertRaises(UnicodeDecodeError,b[:2].decode);self.assertEqual(b.decode(),'爱')
 def test_budget(self):self.assertEqual(100-20-10-10-20-5,35)
 def test_prefix_contiguous(self):
  A=['R1','R2','T1','U1'];B=['R1','R2','T1','U2'];C_=['R1','new','T1','U2'];
  def prefix(a,b):
   n=0
   for x,y in zip(a,b):
    if x!=y:break
    n+=1
   return n
  self.assertEqual(prefix(A,B),3);self.assertEqual(prefix(B,C_),1)
 def test_cas_stale(self):
  version=11;expected=10;self.assertFalse(version==expected)
 def test_bm25(self):
  f=lambda tf,dl:tf*2.2/(tf+1.2*(1-.75+.75*dl/100));self.assertAlmostEqual(f(2,100),1.375);self.assertAlmostEqual(f(4,1000),8.8/13.3)
 def test_rrf_three(self):
  d=rr([['A','B','C'],['B','C','A']]);self.assertEqual(sorted(d,key=d.get,reverse=True),['B','A','C'])
 def test_rrf_walkthrough(self):
  d=rr([['C4','C3','C1','C2'],['C3','C2','C1','C4']]);self.assertEqual(sorted(d,key=d.get,reverse=True),['C3','C4','C2','C1']);self.assertAlmostEqual(d['C4'],.03201844262295082)
 def test_refund_remaining(self):self.assertEqual(100-40,60);self.assertFalse(70<=100-40)
 def test_dual_time(self):
  actual_expiry=5;known_expiry_at=8;self.assertTrue(6>=actual_expiry);self.assertTrue(6<known_expiry_at)
 def test_dag_critical_path(self):self.assertEqual(2+max(4,3)+1,7);self.assertEqual(2+4+3+1,10)
 def test_pass_metrics(self):
  p=.8;k=3;self.assertAlmostEqual(1-(1-p)**k,.992);self.assertAlmostEqual(p**k,.512)
 def test_finite_pass_estimator(self):self.assertAlmostEqual(1-math.comb(3,2)/math.comb(5,2),.7)
 def test_paired_counts(self):
  both=12;oldonly=1;newonly=3;neither=4;self.assertEqual(both+oldonly+newonly+neither,20);self.assertEqual(both+oldonly,13);self.assertEqual(both+newonly,15)
 def test_wall_vs_work(self):self.assertEqual(2+5+3+3,13);self.assertEqual(2+max(5,3)+3,10)
 def test_success_cost(self):self.assertEqual(100/80,1.25);self.assertEqual(70/50,1.4)
 def test_queued_completion(self):self.assertEqual(sum([1,2,3])/3,2)
 def test_visual_patch_count(self):self.assertEqual((32//16)**2,4);self.assertEqual(16*16*3,768)
 def test_quantization_sensitivity(self):
  w=[1,.26];wq=[1,.3];self.assertAlmostEqual(dot([1,1],wq)-dot([1,1],w),.04);self.assertAlmostEqual(dot([1,100],wq)-dot([1,100],w),4)
 def test_cross_entropy(self):
  z=[2.,1.,0.];p=softmax(z);loss=lambda a:-math.log(softmax(a)[1]);g=[p[0],p[1]-1,p[2]];self.assertAlmostEqual(loss(z),1.40760596444438);self.assertVec([finite(loss,z,i) for i in range(3)],g)
 def test_advanced_gradient_q(self):
  q=[0,math.sqrt(2)*math.log(3)];K=[[1,0],[0,1]];V=[[2,0],[0,4]]
  f=lambda a:sum(mm([softmax([dot(a,k)/math.sqrt(2) for k in K])],V)[0]);g=[-.375/math.sqrt(2),.375/math.sqrt(2)];self.assertVec([finite(f,q,i) for i in range(2)],g)
 def test_advanced_gradient_k(self):
  q=[0,math.sqrt(2)*math.log(3)];k=[1.,0.,0.,1.];V=[[2,0],[0,4]]
  f=lambda a:sum(mm([softmax([dot(q,a[:2])/math.sqrt(2),dot(q,a[2:])/math.sqrt(2)])],V)[0]);g=[0,-.375*math.log(3),0,.375*math.log(3)];self.assertVec([finite(f,k,i) for i in range(4)],g)
 def test_walk_attention(self):
  p=softmax([1/math.sqrt(2),1/math.sqrt(2),2/math.sqrt(2)]);O=mm([p],[[1,2],[3,4],[4,6]])[0];self.assertVec(O,[3.00697968,4.51046952],1e-7)
 def test_walk_paired100(self):self.assertEqual(70+5+10+15,100);self.assertEqual((70+10)-(70+5),5)
 def test_header_network(self):
  z=mm([[1,2]],[[1,-1],[1,1]])[0];z[1]-=2;self.assertEqual(z,[3,-1]);self.assertEqual(dot([max(0,a) for a in z],[2,1]),6);self.assertEqual(dot(z,[2,1]),5)
 def test_geometry_XML(self):
  for c in C.values():
   for mobile in [False,True]:
    s=draw_case(c,mobile);tree=ET.fromstring(s);self.assertIn('viewBox',tree.attrib);self.assertTrue(tree.attrib['viewBox'].startswith('0 0 '))
 def test_data_contracts(self):
  self.assertEqual(sum(k.startswith('Q') for k in C),112)
  for c in C.values():
   self.assertEqual(c['id'],next(k for k,v in C.items() if v is c));self.assertEqual(len(c['cols']),3);self.assertTrue(c['purpose']);self.assertGreaterEqual(len(c['read']),2)
   for row in c['rows']:self.assertEqual(len(row),3)
if __name__=='__main__':unittest.main(verbosity=2)
