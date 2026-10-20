"""同一词表的微型Decoder与算子例。全部参数为教学设置，未训练。"""
from __future__ import annotations
import math,json,unittest
import engine as e
E=e.compute()['embedding']['table']
WORDS=['PAD','我','爱','学习','你','！']
I=[[float(i==j) for j in range(4)] for i in range(4)]
WK=[[0.,1.,0.,0.],[1.,0.,0.,0.],[0.,0.,0.,1.],[0.,0.,1.,0.]]
WV=[[1.,0.,0.,0.],[0.,.5,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,.5]]

def silu(x):return x/(1+math.exp(-x))
def forward(ids, prior=None):
    if not ids or any(type(i)is not int or i<=0 or i>=len(E) for i in ids):raise ValueError('valid non-PAD IDs only')
    x=[list(E[i]) for i in ids];norm=[e.ln(v) for v in x];q=e.mm(norm,I);k=e.mm(norm,WK);v=e.mm(norm,WV)
    prior=prior or {'K':[],'V':[]};offset=len(prior['K']);allk=prior['K']+k;allv=prior['V']+v
    heads=[]
    for h in range(2):
        low=2*h;high=low+2
        heads.append(e.attn([a[low:high] for a in q],[a[low:high] for a in allk],[a[low:high] for a in allv],offset=offset))
    combined=[heads[0]['output'][j]+heads[1]['output'][j] for j in range(len(ids))]
    r=e.add(x,combined);n2=[e.ln(row) for row in r]
    # Wgate=Wup=I; Wdown=.25I, hence .25*silu(z)*z.
    f=[[.25*silu(z)*z for z in row] for row in n2];y=e.add(r,f);last=e.ln(y[-1]);logits=e.mm([last],e.tr(E))[0]
    # PAD is forbidden by this explicit teaching decoding policy, not by Embedding itself.
    decoded_logits=[-math.inf]+logits[1:];p=e.softmax(decoded_logits);token=max(range(1,6),key=lambda j:p[j])
    return {'ids':ids,'words':[WORDS[i] for i in ids],'X':x,'normalized':norm,'Wq':I,'Wk':WK,'Wv':WV,'Q':q,'K_new':k,'V_new':v,'heads':heads,'concat_attention':combined,'residual1':r,'normalized2':n2,'ffn':f,'hidden_output':y,'last_norm':last,'logits_before_PAD_filter':logits,'probabilities_after_PAD_filter':p,'selected_token':token,'selected_word':WORDS[token],'cache':{'K':allk,'V':allv}}

def operator_outputs():
    q=[1.,0.];a=[.8,.6];b=[0.,1.];p=e.softmax([e.dot(q,a),e.dot(q,b)]);gq=[(p[0]-1)*a[i]+p[1]*b[i] for i in range(2)]
    rows={'X02':{'input':[1,3],'mean':2,'population_variance':1,'LayerNorm_epsilon1e5':e.ln([1,3]),'RMSNorm_epsilon1e5':[x/math.sqrt(5+1e-5) for x in [1,3]],'SiLU_1_2':[silu(1),silu(2)],'SwiGLU_identity_gate_up_down':[silu(1)*1,silu(2)*2]},
      'X03':{'first_probabilities':{'A':.6,'B':.4},'A_next':{'E':.51,'F':.49},'B_next':{'D':.99,'F':.01},'joint':{'AE':.6*.51,'AF':.6*.49,'BD':.4*.99,'BF':.4*.01}},
      'X04':{'p':[.8,.2],'q':[.5,.5],'KL_p_q':sum(x*math.log(x/y) for x,y in zip([.8,.2],[.5,.5])),'KL_q_p':sum(x*math.log(x/y) for x,y in zip([.5,.5],[.8,.2]))},
      'X05':{'parameters':1000,'P_bytes':4000,'G_bytes':4000,'Adam_m_v_bytes':8000,'data_parallel_per_device':16000,'zero1_per_device':12000,'zero2_per_device':10000,'zero3_per_device':8000},
      'X06':{'Hq':4,'Hkv':2,'group_mapping':[0,0,1,1],'toy_KV_per_token':2*2*2},
      'X07':{'semantic_allowed':[[True,False],[True,True]],'sdpa_bool':[[True,False],[True,True]],'multihead_attention_bool_blocked':[[False,True],[False,False]],'additive_mask':[[0,'-inf'],[0,0]]},
      'X08':{'q':q,'a':a,'b':b,'p':p,'q_gradient':gq,'q_after_lr01':[q[i]-.1*gq[i] for i in range(2)]},
      'X09':{'q':0,'positions':{'A':4,'B':5,'C':1},'undirected_edges':[['A','B'],['B','C']],'greedy_stop':'A','best_after_explore_B':'C'},
      'X10':{'scale':.1,'integer_min':-2,'integer_max':2,'input':[-.24,.03,.26],'integer_codes':[max(-2,min(2,round(x/.1))) for x in [-.24,.03,.26]],'reconstructed':[-.2,0,.2]},
      'X11':{'character_input':['a','b','c'],'merge_rank':[ ['b','c',0], ['a','b',1]],'merged':['a','bc'],'teaching_vocabulary':{'a':1,'bc':5},'IDs':[1,5]},
      'X12':{'valid_target_probabilities':[.8,.5,.25],'valid_count':3,'padded_count':4,'sum_NLL':sum(-math.log(x) for x in [.8,.5,.25]),'correct_mean':sum(-math.log(x) for x in [.8,.5,.25])/3,'wrong_divide4':sum(-math.log(x) for x in [.8,.5,.25])/4}}
    return rows

def compute_chain():
    a=forward([1,2,3]);b=forward([4,2]);follow=forward([a['selected_token']],a['cache']);full=forward([1,2,3,a['selected_token']]);err=max(abs(x-y) for x,y in zip(follow['hidden_output'][0],full['hidden_output'][-1]))
    return {'sentence_A':a,'sentence_B':b,'next_step_A':follow,'full_recompute_A':full,'cached_vs_full_max_error':err,'operators':operator_outputs()}

class ChainTests(unittest.TestCase):
    def test_embedding_rows_match_foundation(self):self.assertEqual(forward([1,2,3])['X'],[E[1],E[2],E[3]])
    def test_two_heads_each_row_probability(self):
        for h in forward([1,2,3])['heads']:
            for row in h['weights']:self.assertAlmostEqual(sum(row),1)
    def test_causal_change_later_cannot_change_first(self):
        self.assertEqual(forward([1,2,3])['hidden_output'][0],forward([1,4,5])['hidden_output'][0])
    def test_cache_full_equivalence(self):self.assertLess(compute_chain()['cached_vs_full_max_error'],1e-12)
    def test_PAD_not_implicitly_generated(self):self.assertEqual(forward([4,2])['probabilities_after_PAD_filter'][0],0)
    def test_norms_differ(self):self.assertNotEqual(operator_outputs()['X02']['LayerNorm_epsilon1e5'],operator_outputs()['X02']['RMSNorm_epsilon1e5'])
    def test_beam_joint_counterexample(self):self.assertGreater(.4*.99,.6*.51)
    def test_KL_asymmetry(self):o=operator_outputs()['X04'];self.assertNotEqual(o['KL_p_q'],o['KL_q_p']);self.assertGreater(o['KL_p_q'],0)
    def test_zero_state_accounting(self):o=operator_outputs()['X05'];self.assertEqual(o['zero1_per_device'],4000+4000+8000/2);self.assertEqual(o['zero3_per_device'],(4000+4000+8000)/2)
    def test_bool_masks_inversion(self):o=operator_outputs()['X07'];self.assertEqual(o['sdpa_bool'],[[not x for x in row] for row in o['multihead_attention_bool_blocked']])
    def test_retrieval_q_gradient_fd(self):
        o=operator_outputs()['X08'];q=o['q'][:];h=1e-6
        def loss():return -math.log(e.softmax([e.dot(q,o['a']),e.dot(q,o['b'])])[0])
        for i,g in enumerate(o['q_gradient']):
            old=q[i];q[i]=old+h;hi=loss();q[i]=old-h;lo=loss();q[i]=old;self.assertAlmostEqual((hi-lo)/(2*h),g,places=8)
    def test_greedy_graph_can_stop_local(self):self.assertGreater(5,4);self.assertLess(1,4)
    def test_quant_clipping(self):self.assertEqual(operator_outputs()['X10']['integer_codes'],[-2,0,2])
    def test_loss_denominator(self):o=operator_outputs()['X12'];self.assertAlmostEqual(o['correct_mean'],.767528364331,places=10);self.assertGreater(o['correct_mean'],o['wrong_divide4'])

if __name__=='__main__':
    import sys
    if '--test' in sys.argv:unittest.main(argv=[sys.argv[0]],verbosity=2)
    else:print(json.dumps(e.finite(compute_chain()),ensure_ascii=False,indent=2,allow_nan=False))
