"""Regression tests for the reviewed text's worked examples and boundaries."""
import json
import math
import unittest
from pathlib import Path
from fractions import Fraction
from content_contracts import *
ROOT = Path(__file__).resolve().parents[1]
RUN = json.loads((ROOT/'labs/model/data/run.json').read_text(encoding='utf-8'))

class NumericChain(unittest.TestCase):
    def setUp(self):
        self.p=RUN['initial_parameters'];self.t=RUN['initial_trace']
    def row(self,k): return self.t[k][0][2]
    def close(self,a,b):
        self.assertEqual(len(a),len(b))
        for x,y in zip(a,b):self.assertAlmostEqual(x,y,places=10)
    def mm(self,a,b):return [sum(x*y for x,y in zip(a,col)) for col in zip(*b)]
    def test_embedding_plus_position(self): self.close([a+b for a,b in zip(self.p['E'][2],self.p['P'][2])],self.row('x'))
    def test_rms_norm(self):
        x=self.row('x');r=math.sqrt(sum(v*v for v in x)/4+1e-5)
        self.close([v/r*g for v,g in zip(x,self.p['g1'])],self.row('n1'))
    def test_q(self): self.close(self.mm(self.row('n1'),self.p['Wq']),self.row('q'))
    def test_k(self): self.close(self.mm(self.row('n1'),self.p['Wk']),self.row('k'))
    def test_v(self): self.close(self.mm(self.row('n1'),self.p['Wv']),self.row('v'))
    def test_attention_probabilities(self):
        q=self.row('q');ks=self.t['k'][0][:3]
        a=softmax([sum(x*y for x,y in zip(q,k))/2 for k in ks])
        self.close(a,self.row('A')[:3])
    def test_value_mixture(self): self.close(self.mm(self.row('A'),self.t['v'][0]),self.row('mix'))
    def test_output_projection(self): self.close(self.mm(self.row('mix'),self.p['Wo']),self.row('attn_delta'))
    def test_first_residual(self): self.close([x+d for x,d in zip(self.row('x'),self.row('attn_delta'))],self.row('residual'))
    def test_ffn_expansion(self): self.close(self.mm(self.row('n2'),self.p['W1']),self.row('ff_pre'))
    def test_relu(self): self.close([max(0,x) for x in self.row('ff_pre')],self.row('ff_act'))
    def test_ffn_compression(self): self.close(self.mm(self.row('ff_act'),self.p['W2']),self.row('ff_delta'))
    def test_second_residual(self): self.close([x+d for x,d in zip(self.row('residual'),self.row('ff_delta'))],self.row('hidden'))
    def test_output_head(self): self.close(self.mm(self.row('final'),self.p['U']),self.row('logits'))
    def test_vocab_probabilities(self): self.close(softmax(self.row('logits')),self.row('probabilities'))
    def test_three_generations(self):
        for s in RUN['generation_full']['steps']:
            self.close(softmax(s['logits']),s['probabilities'])
            self.assertEqual(max(range(8),key=lambda i:s['logits'][i]),s['selected'])
        self.assertEqual([s['selected'] for s in RUN['generation_full']['steps']],[3,5,7])
    def test_initial_and_trained_are_distinct(self): self.assertNotEqual(RUN['initial_hash'],RUN['trained_hash'])
    def test_inference_does_not_update_parameters(self): self.assertEqual(RUN['trained_hash'],RUN['inference_hash_after'])

class AlignmentAndData(unittest.TestCase):
    def test_explicit_pairs(self): self.assertEqual(explicit_pairs([6,1,2,3,5,7]),([6,1,2,3,5],[1,2,3,5,7]))
    def test_wrapper_shift(self): self.assertEqual(wrapper_targets([6,1,2,3,5,7]),[1,2,3,5,7,-100])
    def test_double_shift_is_different(self): self.assertNotEqual(wrapper_targets([1,2,3,5,7])[:4],[1,2,3,5])
    def test_pad_and_eos_share_id(self): self.assertEqual(loss_labels([6,1,7,7],[1,1,1,0],[0,0,1,0]),[-100,-100,7,-100])
    def test_mask_mismatch_rejected(self):
        with self.assertRaises(ValueError):loss_labels([1,2],[1],[1,1])
    def test_user_condition_is_not_a_loss(self):
        self.assertEqual(loss_labels([10,11,12,13],[1,1,1,1],[0,0,1,1]),[-100,-100,12,13])
    def test_packing_boundary(self):
        a=packed_allow([0,0,0,1,1]);self.assertEqual(a[3],[False,False,False,True,False]);self.assertFalse(a[4][2])
    def test_cached_chunk_absolute_positions(self):self.assertEqual(absolute_allow([3,4],range(5)),[[True,True,True,True,False],[True]*5])
    def test_split_counts(self):self.assertEqual({k:len(v) for k,v in grouped_split(DATA_FIXTURE).items()},{'train':2,'validation':1,'test':1})
    def test_group_disjoint(self):
        d=grouped_split(DATA_FIXTURE);sets=[{r['source'] for r in d[s]} for s in d]
        for i,a in enumerate(sets):
            for b in sets[i+1:]:self.assertFalse(a&b)
    def test_valid_numeric_forms(self):
        for text,val in [('2',Fraction(2)),('-2',Fraction(-2)),('0.5',Fraction(1,2)),('1/2',Fraction(1,2))]:self.assertEqual(parse_exact_number(text),val)
    def test_invalid_numeric_forms(self):
        for text in ['nan','inf','1/0','1+1','__import__("os")','答案2','²']:
            with self.assertRaises(ValueError):parse_exact_number(text)
    def test_isdigit_filter_bias(self):self.assertEqual([x for x in ['2','-2','0.5','1/2'] if x.isdigit()],['2'])

class MetricsAndRestart(unittest.TestCase):
    def test_first_token_boundary(self):
        m=request_metrics(0,[120,140,160,180]);self.assertEqual(m['ttft_ms'],120);self.assertEqual(m['mean_itl_ms'],20);self.assertEqual(m['end_to_last_token_ms'],180)
    def test_one_token_itl_undefined(self):self.assertIsNone(request_metrics(0,[120])['mean_itl_ms'])
    def test_nonmonotonic_timestamps(self):
        with self.assertRaises(ValueError):request_metrics(0,[120,110])
    def test_all_costs_included(self):self.assertEqual(task_metrics([.4,.6,.5,.5],[1,0,1,0],20)['cost_per_solved'],1.)
    def test_zero_success_not_zero_cost(self):self.assertIsNone(task_metrics([1,2],[0,0],20)['cost_per_solved'])
    def test_host_wallclock_denominator(self):self.assertEqual(task_metrics([1,1],[1,1],20)['host_seconds_per_solved'],10)
    def test_confidence_bin_is_empirical(self):self.assertAlmostEqual(calibrated_fraction([1,1,1,0,0]),.6)
    def test_empty_bin_undefined(self):
        with self.assertRaises(ValueError):calibrated_fraction([])
    def test_watermark_base_rate(self):self.assertAlmostEqual(detection_precision(.01,.9,.01),90/189)
    def test_real_optimizer_checkpoint(self):
        d=checkpoint_demo();self.assertEqual(d['uninterrupted'],d['full_resume']);self.assertGreater(abs(d['uninterrupted']-d['weights_only']),1e-4)
    def test_softmax_shift_invariance(self):
        a=softmax([2,1,0]);b=softmax([1002,1001,1000]);self.assertEqual(a,b)
    def test_dpo_is_relative(self):
        a=math.log(.3/.2)-math.log(.3/.4);self.assertAlmostEqual(-math.log(1/(1+math.exp(-a))),-math.log(2/3))
    def test_equal_group_rewards(self):
        r=[1,1,1,1];adv=[x-sum(r)/len(r) for x in r];self.assertEqual(adv,[0,0,0,0])


class ScopeAndStorage(unittest.TestCase):
    def test_all_five_qkv_rows(self):
        p=RUN['initial_parameters']; t=RUN['initial_trace']
        for pos in range(5):
            for k,w in [('q','Wq'),('k','Wk'),('v','Wv')]:
                got=[sum(a*b for a,b in zip(t['n1'][0][pos],col)) for col in zip(*p[w])]
                self.assertLess(max(abs(a-b) for a,b in zip(got,t[k][0][pos])),1e-12)
    def test_dense_storage_bytes(self): self.assertEqual(2*128*4096*2,2*1024**2)
    def test_transpose_address(self):
        storage=[1,2,3,4,5,6]
        self.assertEqual(storage[1*1+0*3],2)
        self.assertEqual([[storage[i+j*3] for j in range(2)] for i in range(3)],[[1,4],[2,5],[3,6]])
    def test_lora_trainable_vs_total(self):
        d,r=8,2; base=d*d; adapters=d*r+r*d
        self.assertEqual((base,adapters,base+adapters),(64,32,96))

if __name__=='__main__':unittest.main(verbosity=2)
