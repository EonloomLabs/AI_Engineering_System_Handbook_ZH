"""CPU/stdlib counterexamples for the Chinese engineering textbook.

No external model, GPU, cloud API, production filesystem, or vector database is used.
Each test fixes its input, compares a valid implementation with a deliberate mutant,
and records observable results. Run with: python run.py
"""
from __future__ import annotations
import codecs, hashlib, json, math, os, sqlite3, subprocess, sys, tempfile, unittest
from collections import defaultdict
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F

OBS: dict[str, dict] = {}
def record(name: str, **values):
    OBS[name] = values

def softmax(xs):
    if not xs or not any(math.isfinite(x) for x in xs):
        raise ValueError('no finite candidate')
    m = max(xs); ws = [math.exp(x-m) for x in xs]; z = sum(ws)
    return [x/z for x in ws]

def top_p(ps, cutoff):
    total = 0.; kept = []
    for i in sorted(range(len(ps)), key=lambda j: -ps[j]):
        kept.append(i); total += ps[i]
        if total >= cutoff: break
    return kept

def masked_attention(q,k,v,allowed):
    weights = F.softmax((q @ k.transpose(-2,-1))/math.sqrt(q.shape[-1])
                         + torch.where(allowed, 0., -torch.inf), dim=-1)
    return weights @ v

def online_attention(scores, values, block_size):
    # One row, no mask: each block is incorporated using the CURRENT running max.
    m = -math.inf; denominator = 0.; numerator = [0.]*len(values[0])
    for start in range(0, len(scores), block_size):
        ss=scores[start:start+block_size]; vv=values[start:start+block_size]
        next_m=max(m,max(ss)); scale=math.exp(m-next_m)
        ws=[math.exp(s-next_m) for s in ss]
        denominator=denominator*scale+sum(ws)
        numerator=[n*scale+sum(w*v[d] for w,v in zip(ws,vv))
                   for d,n in enumerate(numerator)]
        m=next_m
    return [n/denominator for n in numerator]

def rrf(rankings, k=60):
    out=defaultdict(float)
    for ranking in rankings:
        seen=set()
        for rank, identity in enumerate(ranking,1):
            if identity in seen: continue
            seen.add(identity); out[identity]+=1/(k+rank)
    return dict(out)

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,
                                    separators=(',',':')).encode()).hexdigest()

class ModelTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(12); torch.set_num_threads(1)

    def test_E01_duplicate_template_markers(self):
        # A teaching tokenizer already received the model-specific template markers.
        templated=[1,8,9,2]
        correct=templated[:]; wrong=[1]+templated+[2]
        self.assertEqual(len(correct),4); self.assertNotEqual(correct,wrong)
        self.assertEqual(wrong.count(1),2)
        record('E01',correct=correct,wrong=wrong,scope='teaching token list, not HF tokenizer')

    def test_E02_vocab_resize_is_not_width(self):
        embedding=nn.Embedding(6,4)
        with self.assertRaises(IndexError): embedding(torch.tensor([6]))
        grown=nn.Embedding(7,4)
        with torch.no_grad(): grown.weight[:6].copy_(embedding.weight)
        self.assertEqual(list(grown(torch.tensor([6])).shape),[1,4])
        self.assertTrue(torch.equal(grown.weight[:6],embedding.weight))
        record('E02',before=[6,4],after=[7,4],new_id=6)

    def test_E03_linear_storage_transpose(self):
        x=torch.tensor([[1.,2.]])
        w=torch.tensor([[1.,3.],[2.,4.]]) # teaching [in,out]
        layer=nn.Linear(2,2,bias=False)
        with torch.no_grad(): layer.weight.copy_(w.T)
        self.assertTrue(torch.equal(layer(x),x@w))
        self.assertFalse(torch.equal(layer(x),x@w.T))
        record('E03-linear',correct=layer(x).tolist(),wrong=(x@w.T).tolist())

    def test_E03_functional_dropout_ignores_module_eval(self):
        class Attention(nn.Module):
            def forward(self,q,k,v,p): return F.scaled_dot_product_attention(q,k,v,dropout_p=p)
        m=Attention().eval(); q=torch.zeros(1,1,1,2); k=torch.zeros(1,1,4,2)
        v=torch.ones(1,1,4,1)
        correct=m(q,k,v,0.0)
        torch.manual_seed(3); wrong=m(q,k,v,0.5)
        self.assertTrue(torch.equal(correct,torch.ones_like(correct)))
        # No assumption that every random seed must differ: an ensemble finds differences.
        outputs=[]
        for seed in range(16):
            torch.manual_seed(seed); outputs.append(float(m(q,k,v,0.5).item()))
        self.assertGreater(len(set(outputs)),1)
        record('E03-dropout',eval_without_dropout=correct.tolist(),outputs_with_p_half=outputs)

    def test_E04_all_masked_row_has_no_valid_distribution(self):
        finite=F.softmax(torch.tensor([-1e9,-1e9]),dim=0)
        infinite=F.softmax(torch.tensor([-torch.inf,-torch.inf]),dim=0)
        self.assertEqual(finite.tolist(),[0.5,0.5]); self.assertTrue(torch.isnan(infinite).all())
        with self.assertRaises(ValueError): softmax([-math.inf,-math.inf])
        q=torch.zeros(1,1,1,2); k=torch.zeros(1,1,2,2);v=torch.ones(1,1,2,1)
        native=F.scaled_dot_product_attention(q,k,v,attn_mask=torch.zeros(1,2,dtype=torch.bool))
        record('E04',finite_fill_result=finite.tolist(),manual_minus_inf_nan=True,
               native_sdpa_observed=native.tolist(),scope='native result not generalized to all backends')

    def test_E05_bool_mask_polarity(self):
        x=torch.tensor([[[1.,0.],[0.,1.]]]); n=nn.MultiheadAttention(2,1,batch_first=True,bias=False).eval()
        with torch.no_grad():
            n.in_proj_weight.copy_(torch.cat([torch.eye(2)]*3)); n.out_proj.weight.copy_(torch.eye(2))
        allow=torch.tensor([[True,False],[True,True]])
        mha,_=n(x,x,x,attn_mask=~allow,need_weights=False)
        q=x.unsqueeze(1)
        sdpa=F.scaled_dot_product_attention(q,q,q,attn_mask=allow).squeeze(1)
        wrong=F.scaled_dot_product_attention(q,q,q,attn_mask=~allow).squeeze(1)
        self.assertTrue(torch.allclose(mha,sdpa,atol=1e-7)); self.assertFalse(torch.allclose(sdpa,wrong))
        record('E05-polarity',correct=sdpa.tolist(),inverted=wrong.tolist())

    def test_E05_nonsquare_cache_causal_offset(self):
        # Two NEW queries after three cached positions: absolute q positions 3,4.
        q=torch.zeros(1,1,2,1); k=torch.zeros(1,1,5,1)
        v=torch.arange(1.,6.).reshape(1,1,5,1)
        allow=torch.arange(5)[None,:] <= torch.arange(3,5)[:,None]
        correct=F.scaled_dot_product_attention(q,k,v,attn_mask=allow)
        wrong=F.scaled_dot_product_attention(q,k,v,is_causal=True)
        self.assertEqual(correct.flatten().tolist(),[2.5,3.0])
        self.assertEqual(wrong.flatten().tolist(),[1.,1.5])
        record('E05-offset',mask=allow.tolist(),correct=correct.flatten().tolist(),upper_left=wrong.flatten().tolist())

    def test_E06_rope_double_rotation(self):
        def rot(x,a): return [x[0]*math.cos(a)-x[1]*math.sin(a),x[0]*math.sin(a)+x[1]*math.cos(a)]
        x=[1.,0.]; once=rot(x,math.pi/2); twice=rot(once,math.pi/2)
        self.assertAlmostEqual(once[1],1); self.assertAlmostEqual(twice[0],-1)
        record('E06',once=once,twice=twice,cache_slots=[0,1,2,3,4],valid_positions=[0,1,2])

    def test_E07_padding_last_valid_not_last_column(self):
        logits=torch.tensor([[[4.,0.],[0.,4.],[9.,0.]],[[4.,0.],[4.,0.],[0.,4.]]])
        valid=torch.tensor([[1,1,0],[1,1,1]],dtype=torch.bool)
        indices=torch.arange(3).expand_as(valid).masked_fill(~valid,-1).max(-1).values
        right=logits[torch.arange(2),indices].argmax(-1)
        wrong=logits[:,-1].argmax(-1)
        self.assertEqual(right.tolist(),[1,1]); self.assertEqual(wrong.tolist(),[0,1])
        record('E07',indices=indices.tolist(),correct=right.tolist(),last_column=wrong.tolist())

    def test_E08_top_p_temperature_noncommute(self):
        logits=[2.,1.,0.]; base=softmax(logits); warm=softmax([x/2 for x in logits])
        self.assertEqual(top_p(base,.6),[0]); self.assertEqual(top_p(warm,.6),[0,1])
        record('E08',p_temperature1=base,p_temperature2=warm,top_p=.6,
               keep_before_temperature=top_p(base,.6),keep_after_temperature=top_p(warm,.6))

    def test_E09_token_weighted_gradient_accumulation(self):
        w=torch.tensor(1.,requires_grad=True)
        a=(w*torch.tensor([1.])-torch.tensor([0.]))**2
        b=(w*torch.tensor([1.,1.,1.])-torch.tensor([2.,2.,2.]))**2
        good=(a.sum()+b.sum())/4; good.backward(); gg=w.grad.item()
        w.grad=None; bad=((w-0)**2+((w-2)**2))/2; bad.backward(); bg=w.grad.item()
        self.assertEqual(gg,-1.);self.assertEqual(bg,0.)
        record('E09',token_counts=[1,3],correct_gradient=gg,mean_of_means_gradient=bg,
               scalar_loss_counterexample={'loss_sums':[2.,3.],'counts':[1,3],'correct':1.25,'wrong':1.5})

    def test_E09_ddp_denominator_simulation(self):
        # DDP averages rank gradients: scale local SUM by world_size/global_count.
        sums=[2.,-6.]; counts=[1,3]; world=2
        corrected=sum(world*g/sum(counts) for g in sums)/world
        wrong=sum(g/n for g,n in zip(sums,counts))/world
        self.assertEqual(corrected,-1.);self.assertEqual(wrong,0.)
        record('E09-ddp',rank_sum_gradients=sums,counts=counts,correct=corrected,wrong=wrong,
               scope='algebra simulation; no distributed process group launched')

    def test_E10_clip_scaled_gradient_wrong(self):
        grad=10.;scale=100.;threshold=1.
        correct=min(grad,threshold); wrong=min(grad*scale,threshold)/scale
        self.assertEqual(correct,1.);self.assertEqual(wrong,.01)
        record('E10',correct_unscaled_clipping=correct,wrong_clip_then_unscale=wrong)

    def test_E10_checkpoint_recomputes(self):
        from torch.utils.checkpoint import checkpoint
        calls=[];x=torch.tensor([.5],requires_grad=True)
        def fn(a): calls.append('forward');return a.sin()*a
        y=checkpoint(fn,x,use_reentrant=False);y.sum().backward()
        self.assertGreater(len(calls),1)
        self.assertAlmostEqual(x.grad.item(),math.sin(.5)+.5*math.cos(.5),places=6)
        record('E10-checkpoint',calls=len(calls),gradient=x.grad.item())

    def test_E11_dpo_requires_reference_ratio(self):
        # Chosen/rejected log p each shifted by reference likelihood.
        lp_ch,lp_re=-2.,-4.;lr_ch,lr_re=-1.,-3.;beta=.1
        margin=beta*((lp_ch-lp_re)-(lr_ch-lr_re));loss=math.log1p(math.exp(-margin))
        self.assertEqual(margin,0.);self.assertAlmostEqual(loss,math.log(2))
        record('E11',policy_gap=2.,reference_gap=2.,margin=margin,loss=loss)

    def test_E12_zero_B_zero_A_gradient_first_step(self):
        # row-vector convention: x @ A @ B, zero B, nonzero A.
        x=torch.tensor([[1.,2.]])
        a=torch.tensor([[1.],[2.]],requires_grad=True)
        b=torch.tensor([[0.,0.]],requires_grad=True)
        ((x@a@b-torch.ones(1,2))**2).sum().backward()
        self.assertTrue(torch.equal(a.grad,torch.zeros_like(a)));self.assertTrue((b.grad!=0).any())
        record('E12',A_gradient=a.grad.tolist(),B_gradient=b.grad.tolist(),delta_initial=[[0.,0.]])

    def test_E13_shared_cache_mutation_and_identity(self):
        prefix=[1,2,3];a=prefix;b=prefix;a.append(4)
        self.assertEqual(b,[1,2,3,4])
        clean=[1,2,3]; a=clean.copy(); b=clean.copy();a.append(4)
        self.assertEqual(b,[1,2,3])
        base={'tokens':[1,2,3],'adapter':'a','tenant':'T1'}
        changed={**base,'adapter':'b'}
        self.assertNotEqual(digest(base),digest(changed))
        record('E13',aliased_b=prefix,copy_on_write_b=b,keys_differ=True)

    def test_E14_online_softmax_stability(self):
        scores=[1000.,1001.,1008.,1007.];v=[[1.,0.],[0.,1.],[2.,0.],[0.,2.]]
        reference=[sum(w*x[d] for w,x in zip(softmax(scores),v)) for d in range(2)]
        for size in [1,2,3,4]:
            got=online_attention(scores,v,size)
            self.assertTrue(all(abs(a-b)<1e-12 for a,b in zip(reference,got)))
        # invalid equal average of two independently normalized blocks
        wrong=[(online_attention(scores[:2],v[:2],2)[d]+online_attention(scores[2:],v[2:],2)[d])/2 for d in range(2)]
        self.assertTrue(any(abs(a-b)>.1 for a,b in zip(reference,wrong)))
        record('E14',correct=reference,wrong_block_average=wrong)

    def test_E15_token_capacity_not_request_count(self):
        cap=12;current=[4,4,3];next_lengths=[n+1 for n in current]
        self.assertLessEqual(sum(current),cap);self.assertGreater(sum(next_lengths),cap)
        record('E15',capacity_positions=cap,before=sum(current),after=sum(next_lengths),requests=3)

    def test_E16_speculative_residual_distribution(self):
        p=[.8,.2];q=[.2,.8]
        accepted=[min(a,b) for a,b in zip(p,q)]
        reject=1-sum(accepted); residual=[max(a-b,0) for a,b in zip(p,q)]
        residual=[a/sum(residual) for a in residual]
        correct=[a+reject*r for a,r in zip(accepted,residual)]
        wrong=[a+reject*t for a,t in zip(accepted,p)]
        self.assertTrue(all(abs(a-b)<1e-12 for a,b in zip(correct,p)))
        self.assertAlmostEqual(wrong[0],.68)
        record('E16',target=p,draft=q,accepted_mass=accepted,rejection_mass=reject,
               residual=residual,correct=correct,wrong_redraw_p=wrong)


class SystemTests(unittest.TestCase):
    def test_E17_history_preserves_typed_items(self):
        history=[{'type':'function_call','call_id':'c7','arguments':'{}'},
                 {'type':'function_call_output','call_id':'c7','output':'ok'}]
        text_only=[x for x in history if x['type']=='message']
        self.assertEqual(text_only,[]);self.assertEqual(history[0]['call_id'],history[1]['call_id'])
        record('E17',typed_items=history,lossy_text_items=text_only)

    def test_E18_late_result_epoch(self):
        state={'epoch':2,'target':'b.py'};result={'epoch':1,'target':'a.py','status':'ok'}
        accepted=result['epoch']==state['epoch']
        self.assertFalse(accepted);record('E18',current=state,late=result,accepted=accepted)

    def test_E19_utf8_and_interleaved_calls(self):
        payload='{"text":"爱"}'.encode(); decoder=codecs.getincrementaldecoder('utf-8')()
        parts=[decoder.decode(bytes([b])) for b in payload]+[decoder.decode(b'',final=True)]
        self.assertEqual(json.loads(''.join(parts)),{'text':'爱'})
        chunks=[('a','{"x":'),('b','{"y":'),('a','1}'),('b','2}')];buffers=defaultdict(str)
        for key,chunk in chunks: buffers[key]+=chunk
        self.assertEqual(json.loads(buffers['a']),{'x':1});self.assertEqual(json.loads(buffers['b']),{'y':2})
        with self.assertRaises(json.JSONDecodeError): json.loads(''.join(c for _,c in chunks))
        record('E19',byte_count=len(payload),unicode_length=len(payload.decode()),assembled=dict(buffers))

    def test_E19_terminal_status_gates_execution(self):
        item={'arguments':'{"path":"a.py"}','done':True,'response_status':'incomplete'}
        authorized=True
        execute=item['done'] and item['response_status']=='completed' and authorized
        self.assertFalse(execute)
        record('E19-status',item=item,execute=execute,scope='conservative local policy; actual protocol contract still required')

    def test_E20_missing_null_and_permission(self):
        def valid(x): return set(x)=={'path','note'} and isinstance(x['path'],str) and (x['note'] is None or isinstance(x['note'],str))
        self.assertFalse(valid({'path':'a.py'}));self.assertTrue(valid({'path':'secret.txt','note':None}))
        allowed={'a.py'}
        self.assertFalse('secret.txt' in allowed)
        record('E20',missing_field_valid=False,null_field_valid=True,unauthorized_path_executable=False)

    def test_E21_tool_discovery_pagination(self):
        pages={None:{'tools':['read'],'nextCursor':'p2'},'p2':{'tools':['write']}}
        cursor=None; result=[]
        while True:
            page=pages[cursor];result+=page['tools'];cursor=page.get('nextCursor')
            if cursor is None:break
        self.assertEqual(result,['read','write']);self.assertNotEqual(pages[None]['tools'],result)
        record('E21',first_page=pages[None]['tools'],all=result)

    def test_E22_audience_not_session(self):
        # This checks policy on already-verified claims, NOT JWT signature validation.
        claims={'aud':'service-A','scope':['read'],'sub':'u1'}
        accepted=claims['aud']=='service-B' and 'read' in claims['scope']
        self.assertFalse(accepted)
        record('E22',audience=claims['aud'],resource='service-B',accepted=accepted)

    def test_E23_registered_visible_executable_are_separate(self):
        registered={'read','write'};visible={'read'};authorized={'read'}
        self.assertTrue('write' in registered);self.assertFalse('write' in visible and 'write' in authorized)
        record('E23',registered=sorted(registered),visible=sorted(visible),authorized=sorted(authorized),scope='illustration, not Rust integration test')

    def test_E24_omitted_empty_tools(self):
        all_tools=['read','write']
        def resolve(value):return all_tools if value is None or value==['*'] else [x for x in value if x in all_tools]
        self.assertEqual(resolve(None),all_tools);self.assertEqual(resolve([]),[]);self.assertEqual(resolve(['typo']),[])
        record('E24',omitted=resolve(None),empty=resolve([]),unknown=resolve(['typo']),scope='documented Copilot rule modeled locally')

    def test_E25_semantics_not_exact_serialization(self):
        a='{"a":1,"b":2}';b='{"b":2,"a":1}'
        self.assertEqual(json.loads(a),json.loads(b));self.assertNotEqual(a,b)
        self.assertEqual(digest(json.loads(a)),digest(json.loads(b)))
        record('E25',semantically_equal=True,byte_identical=False)

    def test_E26_budget_dependency_closure(self):
        total=1000;static=200;generation=200;tool_future=250;available=total-static-generation-tool_future
        self.assertEqual(available,350)
        candidates={'definition':200,'implementation':300}
        self.assertGreater(sum(candidates.values()),available)
        record('E26',total=total,static=static,reserved_generation=generation,
               reserved_tool=tool_future,evidence_budget=available,required_pair=sum(candidates.values()))

    def test_E27_compacted_window_not_one_item(self):
        output=[{'type':'message','role':'user','text':'do not publish'},
                {'type':'compaction','encrypted_content':'opaque'}]
        lossy=output[-1:]
        self.assertEqual(len(lossy),1);self.assertEqual(len(output),2)
        record('E27',canonical_types=[x['type'] for x in output],lossy_types=[x['type'] for x in lossy])

    def test_E28_compaction_compare_and_swap(self):
        version=10;captured=version;summary={'version':captured,'pending':['c7']}
        version+=1 # tool completion arrived during summary generation
        committed=captured==version
        self.assertFalse(committed)
        record('E28',snapshot=captured,current=version,commit_allowed=committed,summary=summary)

    def test_E29_same_dimension_different_vector_space(self):
        docs={'A':[1.,0.],'B':[0.,1.]};q1=[1.,0.];q2=[0.,1.] # same semantics, a different encoder's basis
        choose=lambda q:max(docs,key=lambda k:sum(x*y for x,y in zip(q,docs[k])))
        self.assertEqual(choose(q1),'A');self.assertEqual(choose(q2),'B')
        record('E29',old_space_result=choose(q1),mixed_space_result=choose(q2),dimension=2,scope='basis counterexample, not e5 inference')

    def test_E30_filter_after_topk_underfills(self):
        hits=[('x1','other'),('x2','other'),('a','mine'),('b','mine')]
        post=[x for x in hits[:2] if x[1]=='mine']
        pre=[x for x in hits if x[1]=='mine'][:2]
        self.assertEqual(post,[]);self.assertEqual(len(pre),2)
        record('E30',post_filter_top2=post,eligible_top2=pre,scope='candidate model, not pgvector index execution')

    def test_E31_rrf_duplicate_evidence(self):
        a=rrf([['A','B'],['B','A']]);wrong=rrf([['A','B'],['A','B'],['B','A']])
        self.assertAlmostEqual(a['A'],a['B']);self.assertGreater(wrong['A'],wrong['B'])
        record('E31',two_independent_lists=a,duplicated_one_source=wrong)

    def test_E32_evidence_time_and_condition(self):
        evidence={'tier':'pro','version':3,'limit':100};query={'tier':'free','version':3}
        support=all(evidence[k]==query[k] for k in query)
        self.assertFalse(support);record('E32',evidence=evidence,claim_scope=query,supports=False)

    def test_E33_utf16_utf8_position(self):
        text='a😀b';before='a😀'
        self.assertEqual(len(before),2);self.assertEqual(len(before.encode('utf-16-le'))//2,3)
        self.assertEqual(len(before.encode('utf-8')),5)
        record('E33',text=text,position_of_b_codepoints=2,utf16_units=3,utf8_bytes=5)

    def test_E34_head_not_worktree(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'a.py';p.write_text('x=1\n');first=digest(p.read_text());head='same-commit'
            p.write_text('x=2\n');second=digest(p.read_text())
            self.assertNotEqual(first,second);self.assertEqual(head,'same-commit')
            record('E34',head=head,old_hash=first,new_hash=second,scope='actual file edit; Git HEAD represented by fixed label')

    def test_E35_bitemporal(self):
        events=[{'valid':1,'recorded':1,'value':10},{'valid':5,'recorded':8,'value':20}]
        def asof(valid_at,known_at):
            candidates=[e for e in events if e['valid']<=valid_at and e['recorded']<=known_at]
            return max(candidates,key=lambda x:(x['valid'],x['recorded']))['value']
        self.assertEqual(asof(6,6),10);self.assertEqual(asof(6,9),20)
        record('E35',at_day6_known_day6=10,at_day6_known_day9=20)

    def test_E36_revocation_invalidates_derived(self):
        deps={'chunk':['doc'],'summary':['chunk'],'answer_cache':['summary'],'memory':['summary']};revoked={'doc'}
        changed=True
        while changed:
            old=len(revoked);revoked|={k for k,v in deps.items() if any(x in revoked for x in v)};changed=len(revoked)!=old
        self.assertEqual(revoked,{'doc','chunk','summary','answer_cache','memory'})
        record('E36',invalidated=sorted(revoked))

    def test_E37_skill_stages(self):
        stages={'exists':True,'discovered':True,'selected':False,'body_loaded':False,'used':False}
        self.assertFalse(all(stages.values()))
        record('E37',**stages)

    def test_E38_fallback_expected_cost(self):
        cheap=1.;expensive=5.;fallback=.4
        total=cheap+fallback*expensive
        self.assertEqual(total,3.);self.assertNotEqual(total,cheap)
        record('E38',cheap_cost=cheap,fallback_cost=expensive,rate=fallback,expected_cost=total,synthetic=True)

    def test_E39_disjoint_files_semantic_conflict(self):
        producer=lambda:{'timeout_ms':5000}; consumer=lambda x:x['timeout_s']
        with self.assertRaises(KeyError):consumer(producer())
        record('E39',producer_key='timeout_ms',consumer_key='timeout_s',text_overlap=False,integration_fails=True)

    def test_E40_correlated_reviewers(self):
        failures1={1,2,3,4};failures2={1,2,3,4};n=20
        joint=len(failures1&failures2)/n;independent=(len(failures1)/n)*(len(failures2)/n)
        self.assertEqual(joint,.2);self.assertAlmostEqual(independent,.04)
        record('E40',observed_joint=joint,independence_guess=independent,synthetic=True)

    def test_E41_external_effect_before_journal_real_process(self):
        script=Path(__file__).with_name('crash_worker.py')
        with tempfile.TemporaryDirectory() as td:
            # unsafe retry: committed effect precedes the separate journal acknowledgement.
            first=subprocess.run([sys.executable,str(script),td,'unsafe','crash'],capture_output=True)
            self.assertEqual(first.returncode,17)
            second=subprocess.run([sys.executable,str(script),td,'unsafe','resume'],capture_output=True)
            self.assertEqual(second.returncode,0)
            con=sqlite3.connect(Path(td)/'external.sqlite');unsafe=con.execute('select count(*) from effects').fetchone()[0];con.close()
            self.assertEqual(unsafe,2)
        with tempfile.TemporaryDirectory() as td:
            first=subprocess.run([sys.executable,str(script),td,'keyed','crash'],capture_output=True)
            self.assertEqual(first.returncode,17)
            second=subprocess.run([sys.executable,str(script),td,'keyed','resume'],capture_output=True)
            self.assertEqual(second.returncode,0)
            con=sqlite3.connect(Path(td)/'external.sqlite');safe=con.execute('select count(*) from effects').fetchone()[0];con.close()
            self.assertEqual(safe,1)
        record('E41',crash_exit=17,unsafe_effects=unsafe,keyed_effects=safe,scope='two local SQLite stores + actual subprocess os._exit; not network service')

    def test_E42_retries_multiply(self):
        attempts=[3,3,3];self.assertEqual(math.prod(attempts),27)
        record('E42',per_layer_attempts=attempts,max_leaf_calls=27)

    def test_E42_same_key_different_intent_rejected(self):
        saved={'key':'op7','hash':digest({'path':'a','value':1})}
        changed=digest({'path':'a','value':2})
        self.assertNotEqual(saved['hash'],changed)
        record('E42-key',reuse_allowed=saved['hash']==changed)

    def test_E43_test_exitcodes(self):
        with tempfile.TemporaryDirectory() as td:
            env=dict(os.environ,PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
            empty=subprocess.run([sys.executable,'-m','pytest','-q',td],capture_output=True,text=True,env=env)
            self.assertEqual(empty.returncode,5)
            Path(td,'test_skip.py').write_text('import pytest\n@pytest.mark.skip(reason="demo")\ndef test_x():\n    assert False\n')
            skipped=subprocess.run([sys.executable,'-m','pytest','-q',td],capture_output=True,text=True,env=env)
            self.assertEqual(skipped.returncode,0);self.assertIn('skipped',skipped.stdout)
            record('E43',no_tests_exit=empty.returncode,all_skip_exit=skipped.returncode,all_skip_output=skipped.stdout.strip())

    def test_E44_mutation_test_oracle(self):
        good=lambda x: x>0;bad=lambda x: x>=0
        weak=[1,2];strong=[-1,0,1]
        self.assertTrue(all(good(x)==bad(x) for x in weak));self.assertFalse(all(good(x)==bad(x) for x in strong))
        record('E44',weak_inputs=weak,mutant_survives=True,strong_inputs=strong,mutant_killed=True)

    def test_E45_paired_deltas(self):
        old=[1,1,1,0,0,0,1,0];new=[1,1,0,1,1,0,1,0]
        improvements=sum(a==0 and b==1 for a,b in zip(old,new));regressions=sum(a==1 and b==0 for a,b in zip(old,new))
        delta=(sum(new)-sum(old))/len(old)
        self.assertEqual(improvements,2);self.assertEqual(regressions,1);self.assertEqual(delta,.125)
        record('E45',old=old,new=new,improvements=improvements,regressions=regressions,mean_delta=delta,synthetic=True)

    def test_E46_order_biased_judge(self):
        judge=lambda left,right:left
        original=judge('A','B');swapped=judge('B','A')
        self.assertNotEqual(original,swapped)
        record('E46',original_order_winner=original,swapped_order_winner=swapped,synthetic_judge='always chooses left')

    def test_E47_symlink_bypasses_lexical_check(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);inside=root/'allowed';inside.mkdir();outside=root/'outside.txt';outside.write_text('harmless')
            link=inside/'link.txt';link.symlink_to(outside)
            lexical=link.is_relative_to(inside)
            resolved=link.resolve().is_relative_to(inside.resolve())
            self.assertTrue(lexical);self.assertFalse(resolved)
            record('E47',lexical_inside=lexical,resolved_inside=resolved,read_observed=link.read_text(),scope='harmless temporary symlink, not race-safe sandbox implementation')

    def test_E48_approval_bound_to_intent(self):
        request={'user':'u','op':'write','path':'a','body':'v1','version':7,'expiry':10}
        approved=digest(request);changed={**request,'body':'v2'}
        self.assertNotEqual(approved,digest(changed));record('E48',unchanged_accepted=True,changed_accepted=False)

    def test_E49_parallel_spans_and_percentiles(self):
        wall=max(3.,5.)+2.;span_sum=3.+5.+2.
        self.assertEqual(wall,7.);self.assertEqual(span_sum,10.)
        # Nearest-rank p95 of 95 zeros and 5 hundreds is zero.
        a=[0]*95+[100]*5;b=[0]*95+[100]*5
        p95=lambda xs:sorted(xs)[math.ceil(.95*len(xs))-1]
        mixture=a+b
        self.assertEqual(p95(mixture),0)
        # Separate tenants of unequal size: averaging quantiles is not pooled quantile.
        fast=[1]*100;slow=[100]*10
        self.assertNotEqual((p95(fast)+p95(slow))/2,p95(fast+slow))
        record('E49',wall=wall,sum_spans=span_sum,mean_group_p95=50.5,pooled_p95=p95(fast+slow))

    def test_E49_cost_includes_failures(self):
        costs=[1,1,5,5];success=[1,1,0,0]
        correct=sum(costs)/sum(success);wrong=sum(c for c,s in zip(costs,success) if s)/sum(success)
        self.assertEqual(correct,6.);self.assertEqual(wrong,1.)
        record('E49-cost',cost_per_success=correct,successes_only_wrong=wrong)

    def test_E50_version_vector(self):
        old={'model':'m1','template':'t1','index':'i1','tools':'s1'};new={**old,'index':'i2'}
        self.assertEqual(old['model'],new['model']);self.assertNotEqual(digest(old),digest(new))
        record('E50',old=old,new=new,same_model=True,same_system=False)

    def test_E51_policy_rechecked_at_commit(self):
        plan_policy=7;current_policy=8;allowed_at_plan=True;allowed_at_commit=False
        execute=allowed_at_plan and plan_policy==current_policy and allowed_at_commit
        self.assertFalse(execute);record('E51',planned_version=plan_policy,current_version=current_policy,execute=execute)

    def test_E52_coordinate_scale_and_staleness(self):
        screenshot=[1600,1200];viewport=[800,600];p=[1000,600]
        css=[p[i]*viewport[i]/screenshot[i] for i in range(2)]
        self.assertEqual(css,[500.,300.]);self.assertNotEqual(css,p)
        record('E52',screenshot=screenshot,css_viewport=viewport,pixel_point=p,css_point=css,
               invariant='coordinate mapping alone does not validate current DOM state')

    def test_E53_selective_accuracy_needs_coverage(self):
        correct=[1,1,1,1,0,1,0,0,0,0];accepted=[1,1,1,1,1,0,0,0,0,0]
        selective=sum(c for c,a in zip(correct,accepted) if a)/sum(accepted)
        coverage=sum(accepted)/len(accepted)
        self.assertEqual(selective,.8);self.assertEqual(coverage,.5)
        record('E53',overall_accuracy=sum(correct)/len(correct),selective_accuracy=selective,coverage=coverage,synthetic=True)

    def test_E54_attention_high_weight_not_high_contribution(self):
        weights=[.9,.1];values=[0.,100.];contributions=[a*b for a,b in zip(weights,values)]
        self.assertEqual(contributions,[0.,10.]);record('E54',weights=weights,values=values,contributions=contributions,scope='scalar aggregation counterexample, not real causal interpretability')

    def test_E55_lifecycle_break_even(self):
        upfront=1000.;per_call_saved=.01;break_even=upfront/per_call_saved
        self.assertEqual(break_even,100000.)
        record('E55',extra_training_cost=upfront,inference_saving=per_call_saved,break_even_calls=break_even,synthetic=True)

    def test_E56_interaction_not_main_effect(self):
        table={'old_old':.6,'new_old':.6,'old_new':.6,'new_new':.9}
        interaction=table['new_new']-table['new_old']-table['old_new']+table['old_old']
        self.assertAlmostEqual(interaction,.3)
        record('E56',factorial=table,interaction=interaction,synthetic=True)

class ExtendedIntegrationTests(unittest.TestCase):
    def test_E09_actual_cross_entropy_accumulation(self):
        torch.manual_seed(9)
        features=[torch.tensor([[1.,2.]]),torch.tensor([[2.,1.],[0.,1.],[1.,0.]])]
        targets=[torch.tensor([0]),torch.tensor([1,0,1])]
        initial=torch.tensor([[.2,-.1],[.3,.4]])
        w=initial.clone().requires_grad_()
        full=F.cross_entropy(torch.cat(features)@w,torch.cat(targets),reduction='mean')
        full.backward();expected=w.grad.clone()
        w=initial.clone().requires_grad_()
        for x,y in zip(features,targets):
            (F.cross_entropy(x@w,y,reduction='sum')/4).backward()
        correct=w.grad.clone()
        w=initial.clone().requires_grad_()
        for x,y in zip(features,targets):
            (F.cross_entropy(x@w,y,reduction='mean')/2).backward()
        wrong=w.grad.clone()
        self.assertTrue(torch.allclose(expected,correct,atol=1e-7))
        self.assertFalse(torch.allclose(expected,wrong,atol=1e-4))
        record('E09-xent',full_gradient=expected.tolist(),sum_normalized_gradient=correct.tolist(),
               mean_of_means_gradient=wrong.tolist(),loss=full.item())

    def test_E28_sqlite_conditional_update_prevents_stale_summary(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'history.sqlite';a=sqlite3.connect(path);b=sqlite3.connect(path)
            a.execute('CREATE TABLE history(id INTEGER PRIMARY KEY, rev INTEGER, text TEXT)')
            a.execute("INSERT INTO history VALUES(1,10,'c7 pending')");a.commit()
            captured=a.execute('SELECT rev FROM history WHERE id=1').fetchone()[0]
            b.execute("UPDATE history SET rev=11,text='c7 succeeded' WHERE id=1");b.commit()
            cur=a.execute("UPDATE history SET rev=rev+1,text='summary: c7 pending' WHERE id=1 AND rev=?",(captured,));a.commit()
            self.assertEqual(cur.rowcount,0)
            state=a.execute('SELECT rev,text FROM history WHERE id=1').fetchone()
            self.assertEqual(state,(11,'c7 succeeded'))
            record('E28-sql',stale_revision=captured,changed_rows=cur.rowcount,preserved=list(state))
            a.close();b.close()

    def test_E34_actual_git_worktree_hash(self):
        import shutil
        if not shutil.which('git'): self.skipTest('git not installed')
        with tempfile.TemporaryDirectory() as td:
            def git(*args):return subprocess.run(['git','-C',td,*args],check=True,capture_output=True,text=True).stdout.strip()
            git('init','-q');git('config','user.name','Local Test');git('config','user.email','test@example.invalid')
            p=Path(td)/'a.py';p.write_text('x=1\n');git('add','a.py');git('commit','-qm','fixture')
            before=git('rev-parse','HEAD');p.write_text('x=2\n');after=git('rev-parse','HEAD')
            dirty=git('diff','--','a.py')
            self.assertEqual(before,after);self.assertIn('+x=2',dirty)
            record('E34-git',same_head=before==after,diff=dirty,scope='actual local temporary Git repository')

    def test_E45_paired_bootstrap_task_unit(self):
        import random
        delta=[0,0,-1,1,1,0,0,0];rng=random.Random(20261021)
        draws=sorted(sum(rng.choice(delta) for _ in delta)/len(delta) for _ in range(10000))
        interval=[draws[249],draws[9749]]
        self.assertLessEqual(interval[0],0);self.assertGreaterEqual(interval[1],0)
        record('E45-bootstrap',trials=10000,seed=20261021,paired_task_delta=delta,
               mean=sum(delta)/len(delta),percentile_interval=interval,scope='teaching 8-task dataset, not population certification')

    def test_E50_schema_rollback_compatibility(self):
        # Explicit dual-reader keeps old and new formats distinguishable, never guesses units.
        def read(v):
            if v['schema']==1:return v['timeout_seconds']*1000
            if v['schema']==2:return v['timeout_ms']
            raise ValueError('unsupported schema')
        self.assertEqual(read({'schema':1,'timeout_seconds':5}),5000)
        self.assertEqual(read({'schema':2,'timeout_ms':5000}),5000)
        with self.assertRaises(ValueError):read({'schema':3,'timeout_ms':5000})
        record('E50-schema',v1_ms=5000,v2_ms=5000,unknown_version_rejected=True)

    def test_E56_regression_mutants_are_detectable(self):
        # These deliberately broken functions must not satisfy the intended invariants.
        good_mean=lambda sums,counts:sum(sums)/sum(counts)
        bad_mean=lambda sums,counts:sum(s/n for s,n in zip(sums,counts))/len(counts)
        self.assertNotEqual(good_mean([2,3],[1,3]),bad_mean([2,3],[1,3]))
        safe_commit=lambda old,current:old==current
        bad_commit=lambda old,current:True
        self.assertNotEqual(safe_commit(10,11),bad_commit(10,11))
        correct_positions=lambda past,n:list(range(past,past+n))
        bad_positions=lambda past,n:list(range(n))
        self.assertNotEqual(correct_positions(3,2),bad_positions(3,2))
        record('E56-mutants',killed=['mean-of-means','unconditional-compaction-commit','cache-position-reset'])
