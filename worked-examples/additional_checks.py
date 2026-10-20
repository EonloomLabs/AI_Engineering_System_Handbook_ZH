"""离线示例核验。Python 3.10+，只使用标准库。
本程序测试算术、矩阵与明确的状态反例；不测商业LLM效果或生产系统安全。
"""
from __future__ import annotations
import math, json, unittest, tempfile, sqlite3, os
from pathlib import Path
import engine as e

def extended_outputs():
    # Keep outputs bound to the exact example that introduces the assumptions.
    return {
      'F07': {'A':[[1,2]], 'B':[[3,4],[5,6]],'product':e.mm([[1,2]],[[3,4],[5,6]])},
      'F17': {'x':2,'target':6,'w_before':1,'loss_before':16,'gradient':-16,'learning_rate':.1,'w_after':2.6,'loss_after':(2.6*2-6)**2},
      'Q006': {'probabilities':e.softmax([1/math.sqrt(2),0]),'output':e.mm([e.softmax([1/math.sqrt(2),0])],[[10,0],[0,20]])[0]},
      'Q010': {'relative_angle_degrees':60,'dot_product':math.cos(math.pi/3)},
      'Q030': {'queue_ms':40,'prefill_ms':60,'first_step_ms':20,'TTFT_ms':120,'TPOT_ms':20,'four_tokens_ms':180},
      'Q038': {'utf8_bytes_of_wo':list('我'.encode()),'events':e.sse_trace([b'data: {"text":"'+bytes([0xe6]),bytes([0x88]),bytes([0x91])+b'"}\n\n'])[0]},
      'Q049': {'input_budget':1000-200-50,'fixed':150+100+150,'evidence_budget':350,'selected_evidence':180+120,'used_input':700},
      'Q059': {'scores':[.8,0],'probabilities':e.softmax([.8,0]),'loss':-math.log(e.softmax([.8,0])[0]),'score_gradient':[e.softmax([.8,0])[0]-1,e.softmax([.8,0])[1]]},
      'Q062': {'query':[[1,0],[0,1]],'document':[[.8,.6],[0,1]],'max_per_query':[.8,1], 'MaxSim_A':1.8,'MaxSim_B':2/math.sqrt(2)},
      'Q071': {'queries':[
        {'valid_day':3,'known_day':11,'value':5},
        {'valid_day':7,'known_day':8,'value':5},
        {'valid_day':7,'known_day':11,'value':7}]},
      'Q076': {'A':{'total_cost':100,'successes':80,'cost_per_success':100/80},'B':{'total_cost':70,'successes':40,'cost_per_success':70/40}},
      'Q078': {'serial_seconds':3+5+2,'parallel_seconds':max(3,5)+2,'parallel_with_4s_overhead':max(3,5)+2+4},
      'Q090': {k:v for k,v in e.compute()['metrics'].items() if k.startswith('pass') or k.startswith('finite')},
      'Q091': {'A_successes':12,'B_successes':16,'tasks':20,'A_rate':.6,'B_rate':.8,'discordant':8,'two_sided_exact_p':2*sum(math.comb(8,k) for k in range(3))/2**8},
      'Q097': {'base':max(3,5)+2,'A_optimized':max(1,5)+2,'B_optimized':max(3,2)+2},
      'Q099': {'slots':10,'mean_service_seconds':2,'capacity_per_second':5,'arrivals_per_second':6,'extra_backlog_after_100s':(6-5)*100,'steady_L_at_lambda4_W3':4*3},
      'Q105': {'probabilities':[.8]*4,'labels':[1,1,0,0],'Brier':e.compute()['metrics']['brier']},
      'Q107': {'image':[list(range(i,i+4)) for i in [1,5,9,13]],'patches':[[1,2,5,6],[3,4,7,8],[9,10,13,14],[11,12,15,16]],'W':[[1,0],[0,1],[1,0],[0,1]],'projected':e.mm([[1,2,5,6],[3,4,7,8],[9,10,13,14],[11,12,15,16]],[[1,0],[0,1],[1,0],[0,1]])},
      'Q108': {'weights':[.9,.1],'values':[.01,10],'contributions':[.009,1],'sum':1.009},
      'Q109': {'C_FLOPs':6*10**9*20*10**9,'N_doubled':2*10**9,'D_halved':10*10**9},
      'S01': {'gradient_occurrences':[[.1,-.2],[.3,.4]],'row_gradient':[.4,.2],'new_row':[.8-.1*.4,.6-.1*.2]},
      'S03': {'microbatch_gradients':[1,2,3,4],'unscaled_sum':10,'correct_equal_size_mean':2.5},
      'S04': {'positive_advantage':{'r':1.5,'A':2,'raw':3,'clipped':2.4,'objective':2.4},'negative_advantage':{'r':.5,'A':-2,'raw':-1,'clipped':-1.6,'objective':-1.6}},
      'S05': {'p':[.5,.3,.15,.05],'top2':[.625,.375],'top_p_09':[x/.95 for x in [.5,.3,.15]]},
      'S06': {'compute_lower_bound_us':1e9/1e14*1e6,'transfer_lower_bound_us':1e8/1e12*1e6,'ideal_overlap_lower_bound_us':100},
      'S16': {'old_recall':8/10,'new_recall':10/10,'old_precision':8/(8+2),'new_precision':10/(10+30)},
      'S19': {'A_easy':9/10,'B_easy':80/100,'A_hard':20/100,'B_hard':1/10,'A_total':29/110,'B_total':81/110},
      'S22': {'A_cost_per_success':1000/990,'B_cost_per_success':800/980},
      'S23': {'weight_errors':[.01,.01],'activations':[100,.1],'output_errors':[1,.001],'ratio':1000},
      'S25': {'A_accuracy':80/100,'B_selective_accuracy':45/50,'A_coverage':1,'B_coverage':.5,'correct_counts':[80,45]},
      'S31': {'direction':[1,-2],'directional_derivative':e.dot(e.grad_demo()['dQ'][0],[1,-2])},
      'R03-12': {'total100':20+99*10,'half_prefill':10+99*10,'total50':20+49*10},
      'R08-16': {'recall_at3_X':1,'recall_at3_Y':1,'reciprocal_rank_X':1,'reciprocal_rank_Y':.5},
      'R13-07': {'false_block_rate':5/100,'false_allow_rate':1/10},
      'R14-05': {'requests':10000,'SLO':.99,'allowed_errors':100,'used':80,'remaining':20},
      'R14-07': {'requests':4,'request_limit':60,'tokens_per_request':2000,'tokens':8000,'token_limit':6000},
      'R15-01': {'A':[[1],[2]],'B':[[.1,.2]],'AB':e.mm([[1],[2]],[[.1,.2]])},
      'R16-01': {'w':1,'z':-8,'loss':64,'dz_dw':2,'dL_dz':-16,'dL_dw':-32},
      'R16-05': {'negative_log_natural':-math.log(.5),'negative_log_base2':-math.log2(.5)},
    }

class MoreNumericTests(unittest.TestCase):
    def test_dense_layer_chain(self):
        t=e.transformer(); self.assertAlmostEqual(t['probabilities'][2],.592200875196,places=10);self.assertAlmostEqual(sum(t['probabilities']),1)
    def test_every_masked_probability_zero(self):
        a=e.compute()['attention'];
        for i,row in enumerate(a['weights']):
            for j,p in enumerate(row):
                if j>i:self.assertEqual(p,0)
    def test_layer_norm_mean(self):
        for row in [[1,0],[0,2],[2,2]]:self.assertAlmostEqual(sum(e.ln(row)),0)
    def test_layer_norm_constant_safe(self):self.assertEqual(e.ln([2,2]),[0,0])
    def test_dot_matrix_distinction(self):self.assertEqual(e.mm([[1,2]],[[3,4],[5,6]]),[[13,16]])
    def test_transpose_not_reshape(self):self.assertEqual(e.tr([[1,2,3],[4,5,6]]),[[1,4],[2,5],[3,6]])
    def test_single_parameter_sgd(self):self.assertAlmostEqual((2.6*2-6)**2,.64)
    def test_large_step_can_increase_loss(self):self.assertGreater(((1-1*(-16))*2-6)**2,16)
    def test_gradient_shared_embedding(self):self.assertEqual([.1+.3,-.2+.4],[.4,.2])
    def test_gradient_accumulation_equal_batches(self):self.assertEqual(sum(x/4 for x in [1,2,3,4]),2.5)
    def test_gradient_accumulation_unequal_batches(self):self.assertNotEqual((1*2+3*4)/(2+4),(1+3)/2)
    def test_ppo_sign_sensitive(self):
        def obj(r,a):return min(r*a,min(1.2,max(.8,r))*a)
        self.assertAlmostEqual(obj(1.5,2),2.4);self.assertAlmostEqual(obj(.5,-2),-1.6)
    def test_nucleus_boundary(self):
        p=[.5,.3,.15,.05];ret=[];total=0
        for x in p:
            ret.append(x);total+=x
            if total>=.9:break
        self.assertEqual(ret,[.5,.3,.15]);self.assertAlmostEqual(sum(x/total for x in ret),1)
    def test_bm25_exact_visible_numbers(self):
        d=e.compute()['bm25'];self.assertAlmostEqual(d['rows'][0]['score'],.523548346502,places=10);self.assertAlmostEqual(d['rows'][1]['score'],.566579717447,places=10)
    def test_contrastive_loss(self):self.assertAlmostEqual(-math.log(e.softmax([.8,0])[0]),.371100665948,places=10)
    def test_maxsim_sum(self):
        qs=[[1,0],[0,1]];ds=[[.8,.6],[0,1]]
        self.assertAlmostEqual(sum(max(e.dot(q,d) for d in ds) for q in qs),1.8)
    def test_spec_bad_resampling_changes_distribution(self):
        s=e.spec_demo();wrong=[a+s['rejection_mass']*p for a,p in zip(s['accepted_mass'],s['target'])]
        for a,b in zip(wrong,[.44,.42,.14]):self.assertAlmostEqual(a,b)
        self.assertNotEqual(wrong,s['target'])
    def test_cache_units(self):
        c=e.compute()['cache'];self.assertEqual(c['GiB'],4);self.assertEqual(c['per_token_KiB'],128);self.assertEqual(c['tiny_bytes'],96)
    def test_attention_value_scaling(self):
        p=e.softmax([1/math.sqrt(2),0]);o=e.mm([p],[[10,0],[0,20]])[0];d=e.mm([p],[[20,0],[0,40]])[0]
        for x,y in zip(o,d):self.assertAlmostEqual(2*x,y)
    def test_grad_direction_finite_difference(self):
        q=[.4,-.2];k=[[1,.5],[-.5,1]];v=[[2,-1],[.5,3]];g=[.7,-.3];direction=[1,-2];h=1e-6
        def f(t):return e.dot(e.attn([[q[i]+t*direction[i] for i in range(2)]],k,v,causal=False)['output'][0],g)
        fd=(f(h)-f(-h))/(2*h);self.assertAlmostEqual(fd,e.dot(e.grad_demo()['dQ'][0],direction),places=8)
    def test_context_budget(self):self.assertEqual(1000-200-50-(150+100+150),350)
    def test_time_to_first_vs_completion(self):self.assertEqual(40+60+20+3*20,180)
    def test_prefill_off_by_one(self):
        out=extended_outputs()['R03-12'];self.assertEqual(out['total100'],1010);self.assertEqual(out['total100']-out['total50'],500)
    def test_roofline_units(self):self.assertEqual(extended_outputs()['S06']['transfer_lower_bound_us'],100)
    def test_cost_with_failures(self):self.assertLess(100/80,70/40)
    def test_critical_path_after_change(self):self.assertEqual(max(1,5)+2,7);self.assertEqual(max(3,2)+2,5)
    def test_supercritical_queue(self):self.assertEqual((6-10/2)*100,100)
    def test_pass_events_differ(self):
        d=e.compute()['metrics'];self.assertAlmostEqual(d['pass_at3'],.992);self.assertAlmostEqual(d['pass_all3'],.512);self.assertAlmostEqual(d['finite_pass3'],29/30)
    def test_paired_table_marginals(self):self.assertEqual((10+2,10+6),(12,16));self.assertEqual(10+2+6+2,20)
    def test_simpson_construction(self):self.assertGreater(9/10,80/100);self.assertGreater(20/100,1/10);self.assertLess(29/110,81/110)
    def test_routing_precision_recall_tradeoff(self):self.assertEqual(10/(10+30),.25);self.assertGreater(10/10,8/10)
    def test_correlated_vote_counterexample(self):self.assertGreater(.2,.2**3)
    def test_patch_projector(self):self.assertEqual(extended_outputs()['Q107']['projected'],[[6,8],[10,12],[22,24],[26,28]])
    def test_activation_sensitive_error(self):self.assertEqual(100*.01,1);self.assertEqual(.1*.01,.001)
    def test_scale_pair_product(self):self.assertEqual(6*10**9*20*10**9,6*2*10**9*10*10**9)
    def test_lora_small_count_not_saved(self):self.assertEqual(2*1+1*2,2*2)
    def test_lora_large_count(self):self.assertEqual(1000*8+8*1000,16000)
    def test_calibration_brier(self):self.assertAlmostEqual(sum((.8-y)**2 for y in [1,1,0,0])/4,.34)
    def test_selective_accuracy_vs_coverage(self):self.assertGreater(45/50,80/100);self.assertLess(45,80)
    def test_error_budget(self):self.assertEqual(100-80,20)
    def test_rate_limit_dimensions(self):self.assertLess(4,60);self.assertGreater(4*2000,6000)
    def test_natural_log_units(self):self.assertAlmostEqual(-math.log(.5),math.log(2));self.assertEqual(-math.log2(.5),1)
    def test_utf8_three_bytes(self):self.assertEqual(list('我'.encode('utf-8')),[230,136,145])
    def test_relative_rope_shift(self):
        def r(t):return [math.cos(t),math.sin(t)]
        self.assertAlmostEqual(e.dot(r(math.pi/6),r(3*math.pi/6)),e.dot(r(2*math.pi/6),r(4*math.pi/6)))
    def test_high_weight_not_high_contribution(self):self.assertLess(.9*.01,.1*10)

class MoreStateTests(unittest.TestCase):
    def test_compaction_suffix_preserved(self):
        snap=list(range(1,21));current=snap+[21];candidate={'covers':20,'summary':'state20'}
        replacement=[candidate]+[i for i in current if i>candidate['covers']]
        self.assertEqual(replacement[-1],21);self.assertEqual(len(replacement),2)
    def test_unknown_not_failure(self):
        external={'counter':11};local={'op7':'unknown'}
        self.assertEqual(external['counter'],11);self.assertNotEqual(local['op7'],'failed')
    def test_idempotency_parameter_conflict(self):
        receipts={'k7':{'amount':10,'result':110}}
        def request(key,amount):
            if key in receipts:
                if receipts[key]['amount']!=amount:raise ValueError('same key different arguments')
                return receipts[key]['result']
            raise ValueError('fixture only supports pre-recorded action')
        self.assertEqual(request('k7',10),110)
        with self.assertRaises(ValueError):request('k7',20)
    def test_merge_lost_update_counterexample(self):
        a={'a':2,'b':1};b={'a':1,'b':2};disk=a.copy();disk=b.copy();self.assertNotEqual(disk,{'a':2,'b':2})
    def test_version_check_refuses_stale_write(self):
        disk={'version':9,'body':'B'};expected=7
        if disk['version']==expected:disk.update(version=8,body='A')
        self.assertEqual(disk['version'],9)
    def test_atomic_replace_is_not_compare_and_swap(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x';tmp=Path(d)/'tmp';p.write_text('v7');observed=p.read_text();p.write_text('v9');tmp.write_text('v8');os.replace(tmp,p)
            self.assertEqual(observed,'v7');self.assertEqual(p.read_text(),'v8')
    def test_exclude_boundary_counterexample(self):
        def correct(p,d):return p==d or p.startswith(d+'/')
        for d in ['a','cache','build']:
            self.assertTrue(correct(d,d));self.assertTrue(correct(d+'/x',d));self.assertFalse(correct(d+'b/x',d));self.assertTrue((d+'b/x').startswith(d))
    def test_acl_topk_order(self):
        ranked=[('A',False),('B',False),('C',True),('D',True)]
        after=[x for x,ok in ranked[:2] if ok];before=[x for x,ok in ranked if ok][:2];self.assertEqual(after,[]);self.assertEqual(before,['C','D'])
    def test_bitemporal_specific_scenario(self):
        rows=[{'project':'prod','recorded':1,'from':1,'to':99,'value':5},{'project':'prod','recorded':10,'from':5,'to':99,'value':7}]
        self.assertEqual(e.memory_select(rows,'prod',3,11)['value'],5);self.assertEqual(e.memory_select(rows,'prod',7,8)['value'],5);self.assertEqual(e.memory_select(rows,'prod',7,11)['value'],7)
    def test_current_test_version(self):
        report={'version':'v8','exit':0};artifact='v9';self.assertFalse(report['version']==artifact and report['exit']==0)
    def test_approval_bound_to_artifact_environment(self):
        approved=('P','staging','v8');self.assertNotEqual(approved,('P','staging','v9'));self.assertNotEqual(approved,('P','production','v8'))
    def test_refund_conditions_and_not_or(self):
        days=6;weekday=False;self.assertFalse(days<=7 and weekday);self.assertTrue(days<=7 or weekday)
    def test_tool_completion_order_not_identity(self):
        result_by_id=dict([('c2','B'),('c1','A')]);self.assertEqual(result_by_id['c1'],'A')
    def test_replay_does_not_repeat_effect(self):
        events=[('c7','succeeded'),('c8','pending')];state={}
        for key,status in events:state[key]=status
        for key,status in events:state[key]=status
        self.assertEqual(state,{'c7':'succeeded','c8':'pending'})
    def test_gui_scroll_transform(self):self.assertEqual(300-200,100);self.assertEqual((120/2,80/2),(60,40))

if __name__=='__main__':
    import sys
    if '--test' in sys.argv:unittest.main(argv=[sys.argv[0]],verbosity=2)
    else:print(json.dumps(e.finite(extended_outputs()),ensure_ascii=False,indent=2,allow_nan=False))
