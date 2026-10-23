"""数值、因果性、训练/推理边界和常见错误的独立断言。"""
from __future__ import annotations
import copy,json,math,unittest,io,platform
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F
from tiny_model import TinyLM,training_loss,manual_backward,SEQUENCES,fingerprint,generate
from reference_inference import forward as py_forward,softmax as py_softmax
D=Path(__file__).resolve().parent.parent/'data'
R=json.loads((D/'run.json').read_text())
torch.set_num_threads(1)
DT=torch.float64

def loaded():
    m=TinyLM();m.load_state_dict({k:torch.tensor(v,dtype=DT) for k,v in R['trained_parameters'].items()});return m

class Arithmetic(unittest.TestCase):
    def test_matmul_value(self):
        self.assertEqual((torch.tensor([[1.,2.,3.],[4.,5.,6.]])@torch.tensor([[1.,0.],[0.,1.],[1.,1.]])).tolist(),[[4.,5.],[10.,11.]])
    def test_softmax_shift(self):
        a=torch.tensor([2.,1.,0.],dtype=DT);self.assertTrue(torch.allclose(a.softmax(-1),(a-2).softmax(-1)))
    def test_softmax_not_divide_logits(self):
        a=torch.tensor([2.,1.,0.],dtype=DT);self.assertGreater(float((a.softmax(-1)-a/a.sum()).abs().max()),.05)
    def test_probability_sum(self):
        self.assertAlmostEqual(sum(py_softmax([2,1,0])),1,places=14)
    def test_logsumexp_ce(self):
        z=torch.tensor([[2.,1.,0.]],dtype=DT);y=torch.tensor([1]);self.assertAlmostEqual(float(F.cross_entropy(z,y)),float(z.logsumexp(-1)-z[0,1]),places=14)
    def test_ce_gradient(self):
        z=torch.tensor([[2.,1.,0.]],dtype=DT,requires_grad=True);F.cross_entropy(z,torch.tensor([1])).backward();expected=z.detach().softmax(-1)-torch.tensor([[0.,1.,0.]],dtype=DT);self.assertTrue(torch.allclose(z.grad,expected))
    def test_double_softmax_wrong(self):
        z=torch.tensor([[2.,1.,0.]],dtype=DT);y=torch.tensor([1]);self.assertGreater(abs(float(F.cross_entropy(z,y)-F.cross_entropy(z.softmax(-1),y))),.1)
    def test_ln_rms_different(self):
        x=torch.tensor([1.,3.],dtype=DT);a=F.layer_norm(x,(2,),eps=1e-5);b=x/torch.sqrt(x.square().mean()+1e-5);self.assertLess(float(a[0]),0);self.assertGreater(float(b[0]),0)
    def test_adam_steps(self):
        for rec in R['adam_steps']:
            t=rec['step'];g=rec['gradient'];m=.9*rec['m_before']+.1*g;v=.999*rec['v_before']+.001*g*g
            w=rec['weight_before']*(1-.03*.01)-.03*(m/(1-.9**t))/(math.sqrt(v/(1-.999**t))+1e-8)
            self.assertAlmostEqual(w,rec['weight_after'],places=13)
    def test_training_lower_bound(self):
        self.assertGreaterEqual(R['final_loss'],math.log(2)/5)
        self.assertLess(R['final_loss'],.15)
    def test_quantization(self):
        x=.26;q=round(x/.1);self.assertEqual(q,3);self.assertAlmostEqual(q*.1-x,.04)
    def test_lora_rank(self):
        a=torch.tensor([[1.],[2.]],dtype=DT);b=torch.tensor([[1.,2.,3.]],dtype=DT);self.assertEqual((a@b).tolist(),[[1.,2.,3.],[2.,4.,6.]])
    def test_speculative_identity(self):
        p=[.6,.3,.1];q=[.2,.5,.3];accepted=[min(a,b) for a,b in zip(p,q)];rem=[max(a-b,0) for a,b in zip(p,q)];self.assertTrue(all(abs(a+b-c)<1e-15 for a,b,c in zip(accepted,rem,p)))
    def test_online_softmax(self):
        s=[2.,1.,0.];v=[10.,20.,30.];m=-math.inf;l=0;u=0
        for block in [[0,1],[2]]:
            nm=max([m]+[s[i] for i in block]);a=0 if m==-math.inf else math.exp(m-nm)
            l=a*l+sum(math.exp(s[i]-nm) for i in block);u=a*u+sum(math.exp(s[i]-nm)*v[i] for i in block);m=nm
        self.assertAlmostEqual(u/l,sum(a*b for a,b in zip(py_softmax(s),v)),places=13)
    def test_rope_relative(self):
        def rot(x,t):return [x[0]*math.cos(t)-x[1]*math.sin(t),x[0]*math.sin(t)+x[1]*math.cos(t)]
        q=[1,2];k=[-.5,1]
        dot=lambda a,b:sum(x*y for x,y in zip(a,b))
        self.assertAlmostEqual(dot(rot(q,.3),rot(k,.7)),dot(q,rot(k,.4)),places=14)

class ForwardAndGradient(unittest.TestCase):
    def setUp(self):self.m=TinyLM();self.x=SEQUENCES[:,:-1];self.y=SEQUENCES[:,1:]
    def test_parameter_count(self):self.assertEqual(sum(p.numel() for p in self.m.parameters()),236)
    def test_shapes(self):
        z,_,t=self.m(self.x,return_trace=True);self.assertEqual(tuple(z.shape),(2,5,8));self.assertEqual(tuple(t['A'].shape),(2,5,5))
    def test_rowsum(self):
        _,_,t=self.m(self.x,return_trace=True);self.assertTrue(torch.allclose(t['A'].sum(-1),torch.ones(2,5,dtype=DT)))
    def test_future_attention_zero(self):
        _,_,t=self.m(self.x,return_trace=True);self.assertEqual(float(t['A'].triu(1).abs().sum()),0)
    def test_future_input_no_effect(self):
        x=self.x.clone();x[0,4]=4;a,_=self.m(self.x);b,_=self.m(x);self.assertTrue(torch.equal(a[0,:4],b[0,:4]))
    def test_missing_causal_mask_detected(self):
        x=self.x.clone();x[0,4]=4;a,_=self.m(self.x,causal=False);b,_=self.m(x,causal=False);self.assertGreater(float((a[0,:4]-b[0,:4]).abs().max()),1e-4)
    def test_batch_matches_individual(self):
        a,_=self.m(self.x);b,_=self.m(self.x[:1]);self.assertTrue(torch.allclose(a[:1],b,atol=1e-14,rtol=1e-14))
    def test_batch_permutation(self):
        a,_=self.m(self.x);b,_=self.m(self.x.flip(0));self.assertTrue(torch.allclose(a,b.flip(0),atol=1e-14,rtol=1e-14))
    def test_entire_analytic_backward(self):
        z,_,t=self.m(self.x,return_trace=True);g,b=manual_backward(self.m,t,self.y);l,_=training_loss(z,self.y);l.backward()
        for k,p in self.m.named_parameters():self.assertTrue(torch.allclose(p.grad,g[k],atol=1e-12,rtol=1e-10),k)
    def test_qkv_input_paths_add(self):
        z,_,t=self.m(self.x,return_trace=True);g,b=manual_backward(self.m,t,self.y)
        expected=b['dq']@self.m.Wq.T+b['dk']@self.m.Wk.T+b['dv']@self.m.Wv.T
        self.assertTrue(torch.allclose(expected,b['dn1']))
    def test_embedding_duplicate_rows_accumulate(self):
        z,_,t=self.m(self.x,return_trace=True);g,b=manual_backward(self.m,t,self.y)
        self.assertTrue(torch.allclose(g['E'][2],b['dx'][0,2]+b['dx'][1,2]))
    def test_score_gradient_rowsum_zero(self):
        z,_,t=self.m(self.x,return_trace=True);g,b=manual_backward(self.m,t,self.y);self.assertLess(float(b['ds'].sum(-1).abs().max()),1e-12)
    def test_finite_difference_selected_coordinates(self):
        z,_=self.m(self.x);l,_=training_loss(z,self.y);l.backward();eps=1e-6
        for name,idx in [('Wq',(0,0)),('Wk',(2,1)),('Wv',(1,0)),('Wo',(2,3)),('W1',(0,3)),('W2',(2,1)),('U',(0,3)),('g1',(2,)),('g2',(2,)),('gf',(2,)),('E',(2,1)),('P',(2,1))]:
            p=self.m.get_parameter(name);old=float(p[idx].detach());g=float(p.grad[idx]);vals=[]
            with torch.no_grad():
                for sign in [1,-1]:
                    p[idx]=old+sign*eps;zz,_=self.m(self.x);ll,_=training_loss(zz,self.y);vals.append(float(ll))
                p[idx]=old
            self.assertAlmostEqual((vals[0]-vals[1])/(2*eps),g,places=7,msg=name)
    def test_sgd_small_step(self):
        z,_=self.m(self.x);l,_=training_loss(z,self.y);before=float(l.detach());l.backward()
        with torch.no_grad():
            for p in self.m.parameters():p-=.001*p.grad
        after,_=training_loss(self.m(self.x)[0],self.y);self.assertLess(float(after),before)
    def test_backward_not_update(self):
        old=fingerprint(self.m);z,_=self.m(self.x);training_loss(z,self.y)[0].backward();self.assertEqual(fingerprint(self.m),old)
    def test_grad_accumulation(self):
        z,_=self.m(self.x);l,_=training_loss(z,self.y);l.backward();first=self.m.U.grad.clone()
        z,_=self.m(self.x);training_loss(z,self.y)[0].backward();self.assertTrue(torch.allclose(self.m.U.grad,2*first))
    def test_ignored_target_gradient(self):
        z=torch.randn(1,3,8,dtype=DT,requires_grad=True);y=torch.tensor([[1,-100,2]]);training_loss(z,y)[0].backward();self.assertEqual(float(z.grad[0,1].abs().sum()),0)
    def test_all_ignored_rejected(self):
        with self.assertRaises(ValueError):training_loss(torch.zeros(1,2,8),torch.full((1,2),-100))
    def test_target_alignment(self):
        self.assertEqual(self.x[0].tolist(),[6,1,2,3,5]);self.assertEqual(self.y[0].tolist(),[1,2,3,5,7])
    def test_no_double_shift(self):
        z,_,t=self.m(self.x,return_trace=True);right,_=training_loss(z,self.y)
        wrong,_=training_loss(z[:,:-1],self.y[:,1:]);self.assertGreater(abs(float(right-wrong)),1e-3)
    def test_ce_without_prior_softmax(self):
        z,_=self.m(self.x);right,_=training_loss(z,self.y);wrong,_=training_loss(z.softmax(-1),self.y);self.assertGreater(abs(float(right-wrong)),.01)
    def test_right_padding_needs_final_valid(self):
        x=torch.tensor([[6,1,2,0]]);mask=torch.tensor([[1,1,1,0]],dtype=torch.bool)
        z,_=self.m(x,key_valid=mask);true,_=self.m(x[:,:3]);self.assertTrue(torch.allclose(z[:,2],true[:,-1]));self.assertGreater(float((z[:,3]-z[:,2]).abs().max()),1e-4)
    def test_padding_key_invisible(self):
        x=torch.tensor([[6,0,1,2]]);mask=torch.tensor([[1,0,1,1]],dtype=torch.bool);_,_,t=self.m(x,key_valid=mask,return_trace=True);self.assertEqual(float(t['A'][:,:,1].sum()),0)
    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):self.m(torch.empty(1,0,dtype=torch.long))
    def test_all_masked_rejected(self):
        with self.assertRaises(ValueError):self.m(self.x,key_valid=torch.zeros(2,5,dtype=torch.bool))

class InferenceAndInterfaces(unittest.TestCase):
    def test_reload_hash(self):self.assertEqual(fingerprint(loaded()),R['trained_hash'])
    def test_full_cache_outputs(self):
        m=loaded();a=generate(m,[6,1,2],use_cache=True);b=generate(m,[6,1,2],use_cache=False)
        self.assertEqual(a['tokens'],b['tokens'])
        for x,y in zip(a['steps'],b['steps']):self.assertLess(max(abs(i-j) for i,j in zip(x['logits'],y['logits'])),1e-10)
    def test_expected_tokens(self):self.assertEqual(generate(loaded(),[6,1,2])['tokens'],[6,1,2,3,5,7])
    def test_no_parameter_change(self):
        m=loaded();h=fingerprint(m);generate(m,[6,1,2]);self.assertEqual(fingerprint(m),h)
    def test_cache_lag(self):
        a=generate(loaded(),[6,1,2]);self.assertEqual([s['cache_after'] for s in a['steps']],[3,4,5]);self.assertEqual(len(a['tokens']),6)
    def test_limit_not_eos(self):
        a=generate(loaded(),[6,1,2],max_new=2);self.assertEqual(a['reason'],'length');self.assertNotEqual(a['tokens'][-1],7)
    def test_two_new_tokens_cache(self):
        m=loaded();x=SEQUENCES[:1,:-1];allz,_=m(x);_,c=m(x[:,:3]);part,_=m(x[:,3:],cache=c);self.assertTrue(torch.allclose(allz[:,3:],part,atol=1e-12))
    def test_wrong_position_changes_output(self):
        m=loaded();_,c=m(torch.tensor([[6,1,2]]));good,_=m(torch.tensor([[3]]),cache=c);bad,_=m(torch.tensor([[3]]),cache=c,position_ids=torch.zeros(1,1,dtype=torch.long));self.assertGreater(float((good-bad).abs().max()),.01)
    def test_stale_cache_after_weights_change(self):
        m=loaded();x=torch.tensor([[6,1,2,3]]);_,c=m(x[:,:3])
        with torch.no_grad():m.Wv.mul_(.5)
        stale,_=m(x[:,3:],cache=c);fresh,_=m(x);self.assertGreater(float((stale[:,-1]-fresh[:,-1]).abs().max()),1e-4)
    def test_stdlib_reference(self):
        z=py_forward([6,1,2],R['trained_parameters']);expected=R['generation']['steps'][0]['logits'];self.assertLess(max(abs(x-y) for x,y in zip(z[-1],expected)),1e-10)
    def test_eval_does_not_disable_grad(self):
        m=TinyLM().eval();z,_=m(SEQUENCES[:,:-1]);self.assertTrue(z.requires_grad)
    def test_no_grad_does_not_switch_dropout(self):
        d=nn.Dropout(.5).train();x=torch.ones(1000)
        with torch.no_grad():y=d(x)
        self.assertGreater(int(y.eq(0).sum()),0)
    def test_eval_switches_dropout(self):
        d=nn.Dropout(.5).eval();x=torch.ones(100);self.assertTrue(torch.equal(d(x),x))
    def test_sdpa_non_square_alignment(self):
        q=torch.ones(1,1,2,1,dtype=DT);k=torch.ones(1,1,5,1,dtype=DT);v=torch.arange(1,6,dtype=DT).reshape(1,1,5,1)
        good=(torch.arange(5)[None,:]<=torch.tensor([3,4])[:,None])
        a=F.scaled_dot_product_attention(q,k,v,attn_mask=good);b=F.scaled_dot_product_attention(q,k,v,is_causal=True)
        self.assertEqual(a.flatten().tolist(),[2.5,3.]);self.assertEqual(b.flatten().tolist(),[1.,1.5])
    def test_sdpa_scale_once(self):
        q=torch.tensor([[[[1.,2.]]]],dtype=DT);k=torch.tensor([[[[1.,0.],[0.,1.]]]],dtype=DT);v=k
        a=F.scaled_dot_product_attention(q,k,v);manual=(q@k.transpose(-1,-2)/math.sqrt(2)).softmax(-1)@v
        self.assertTrue(torch.allclose(a,manual));b=F.scaled_dot_product_attention(q/math.sqrt(2),k,v);self.assertGreater(float((a-b).abs().max()),.01)
    def test_linear_storage_transpose(self):
        x=torch.tensor([[1.,2.]],dtype=DT);w=torch.tensor([[1.,3.],[2.,4.]],dtype=DT)
        self.assertEqual((x@w).tolist(),[[5.,11.]]);self.assertEqual(F.linear(x,w).tolist(),[[7.,10.]])
    def test_training_loss_drops(self):self.assertLess(R['final_loss'],R['initial_loss']/10)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
    stream=io.StringIO();res=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    log=stream.getvalue();print(log)
    (D/'tests.log').write_text(log)
    (D/'tests.json').write_text(json.dumps(dict(run=res.testsRun,failures=len(res.failures),errors=len(res.errors),skipped=len(res.skipped),python=platform.python_version(),torch=torch.__version__,device='cpu'),indent=2))
    if not res.wasSuccessful():raise SystemExit(1)
