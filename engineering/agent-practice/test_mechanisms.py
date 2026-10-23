"""Deterministic teaching tests: no model/API calls and no Codex production test claims."""
import unittest,json,math,hashlib,sqlite3,subprocess,sys,tempfile,time,random
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class Version:
    model:str='model-a'; config:str='config-1'; owner:int=1; rewrite:int=0

def install_compaction(prefix,suffix,candidate_version,live_version,original_prefix):
    if candidate_version!=live_version:raise ValueError('stale candidate')
    if prefix!=original_prefix:raise ValueError('prefix mismatch')
    return ['summary('+','.join(prefix)+')']+list(suffix)

def rrf(rankings,k=60):
    scores={}
    for ranking in rankings:
        seen=set()
        for rank,doc in enumerate(ranking,1):
            if doc in seen:continue
            seen.add(doc);scores[doc]=scores.get(doc,0)+1/(k+rank)
    return sorted(scores.items(),key=lambda p:(-p[1],p[0]))

def canonical_action(tool,args,scope):
    return hashlib.sha256(json.dumps([tool,args,scope],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def authorize(approved,tool,args,scope):return approved==canonical_action(tool,args,scope)

class Stream:
    def __init__(self):self.buffers={};self.finished=set();self.effects=[];self.complete=False
    def feed(self,event):
        typ=event['type'];cid=event.get('call_id')
        if typ=='delta':self.buffers[cid]=self.buffers.get(cid,'')+event['text']
        elif typ=='item_done':
            if cid in self.finished:raise ValueError('duplicate item')
            obj=json.loads(self.buffers[cid]);self.finished.add(cid)
            if not isinstance(obj.get('path'),str):raise TypeError('path must be string')
            self.effects.append((cid,obj))
        elif typ=='response_done':self.complete=True
    def eof(self):
        if not self.complete:raise EOFError('incomplete response')

class Tests(unittest.TestCase):
    def test_01_model_final_not_goal(self):
        s={'response_complete':True,'effect_verified':False};self.assertFalse(s['response_complete'] and s['effect_verified'])
    def test_02_schema_not_authorization(self):
        p={'path':'secrets/key'};self.assertIsInstance(p['path'],str);self.assertFalse(p['path'].startswith('src/'))
    def test_03_parameter_mutation_invalidates_approval(self):
        key=canonical_action('write',{'env':'test','timeout':30},'test-only')
        self.assertFalse(authorize(key,'write',{'env':'production','timeout':30},'test-only'))
    def test_04_parameter_order_does_not_change_identity(self):
        self.assertEqual(canonical_action('t',{'a':1,'b':2},'s'),canonical_action('t',{'b':2,'a':1},'s'))
    def test_05_prehook_prevents_effect(self):
        effects=[];allow=False
        if allow:effects.append('write')
        self.assertEqual(effects,[])
    def test_06_posthook_does_not_undo_effect(self):
        effects=['write'];model_visible='blocked';self.assertEqual(len(effects),1);self.assertEqual(model_visible,'blocked')
    def test_07_interleaved_call_buffers(self):
        s=Stream()
        for e in [{'type':'delta','call_id':'c1','text':'{"path":"a'},{'type':'delta','call_id':'c2','text':'{"path":"b.py"}'},{'type':'delta','call_id':'c1','text':'.py"}'},{'type':'item_done','call_id':'c2'},{'type':'item_done','call_id':'c1'}]:s.feed(e)
        self.assertEqual(dict(s.effects),{'c1':{'path':'a.py'},'c2':{'path':'b.py'}})
    def test_08_delta_does_not_execute(self):
        s=Stream();s.feed({'type':'delta','call_id':'c1','text':'{"path":"a.py"}'});self.assertEqual(s.effects,[])
    def test_09_eof_not_response_done(self):
        s=Stream()
        with self.assertRaises(EOFError):s.eof()
    def test_10_duplicate_completion_rejected(self):
        s=Stream();s.feed({'type':'delta','call_id':'c1','text':'{"path":"a"}'});s.feed({'type':'item_done','call_id':'c1'})
        with self.assertRaises(ValueError):s.feed({'type':'item_done','call_id':'c1'})
    def test_11_utf8_incremental(self):
        import codecs
        b='爱'.encode();dec=codecs.getincrementaldecoder('utf-8')();parts=[dec.decode(b[:1]),dec.decode(b[1:2]),dec.decode(b[2:],final=True)]
        self.assertEqual(''.join(parts),'爱');self.assertEqual(parts[:2],['',''])
    def test_12_compaction_preserves_suffix(self):
        self.assertEqual(install_compaction(['e1','e2'],['e3'],Version(),Version(),['e1','e2']),['summary(e1,e2)','e3'])
    def test_13_rewrite_rejects_candidate(self):
        with self.assertRaises(ValueError):install_compaction(['e1'],[],Version(),Version(rewrite=1),['e1'])
    def test_14_auth_owner_rejects_candidate(self):
        with self.assertRaises(ValueError):install_compaction(['e1'],[],Version(),Version(owner=2),['e1'])
    def test_15_model_change_rejects_candidate(self):
        with self.assertRaises(ValueError):install_compaction(['e1'],[],Version(),Version(model='b'),['e1'])
    def test_16_config_change_rejects_candidate(self):
        with self.assertRaises(ValueError):install_compaction(['e1'],[],Version(),Version(config='2'),['e1'])
    def test_17_no_input_overwrite(self):
        prefix=['a'];suffix=['new-user-input'];copy=install_compaction(prefix,suffix,Version(),Version(),prefix);self.assertIn('new-user-input',copy)
    def test_18_naive_compaction_counterexample(self):
        live=['a','b','new'];replacement=['summary'];self.assertNotIn(live[-1],replacement)
    def test_19_rrf_order(self):
        self.assertEqual([d for d,s in rrf([['D1','D2','D3'],['D2','D3','D1']])],['D2','D1','D3'])
    def test_20_rrf_exact_score(self):
        scores=dict(rrf([['D1','D2','D3'],['D2','D3','D1']]));self.assertAlmostEqual(scores['D2'],1/61+1/62)
    def test_21_same_dimension_different_space(self):
        a=[1,0];b=[0,1];self.assertEqual(len(a),len(b));self.assertEqual(sum(x*y for x,y in zip(a,b)),0)
    def test_22_postfilter_candidate_shortage(self):
        candidates=list(range(20));allowed=[d for d in candidates if d==7];self.assertEqual(len(allowed),1)
    def test_23_lease_generation(self):
        db={'owner':'new','gen':2};old={'owner':'old','gen':1};self.assertNotEqual(db,old)
    def test_24_empty_memory_success(self):
        result={'status':'success','memories':[]};self.assertEqual(result['status'],'success');self.assertEqual(len(result['memories']),0)
    def test_25_stale_memory_source(self):
        mem={'source_hash':'r7'};self.assertFalse(mem['source_hash']=='r9')
    def test_26_stale_test_result(self):
        test={'hash':'r7','exit':0};self.assertFalse(test['hash']=='r8' and test['exit']==0)
    def test_27_zero_tests_not_verified(self):
        self.assertFalse(0==0 and 0>0)
    def test_28_paired_eval(self):
        both,fix,regress,neither=12,5,1,2;n=20;self.assertEqual(sum([both,fix,regress,neither]),n);self.assertAlmostEqual((both+fix)/n-(both+regress)/n,0.2)
    def test_29_atleast_vs_all(self):
        p=.8;k=3;self.assertAlmostEqual(1-(1-p)**k,.992);self.assertAlmostEqual(p**k,.512)
    def test_30_critical_path(self):self.assertEqual(2+max(5,3)+1,8)
    def test_31_noncritical_optimization(self):self.assertEqual(2+max(5,1)+1,8)
    def test_32_parallel_overhead(self):self.assertEqual(max(4,6)+2+5,13);self.assertEqual(4+6+2,12)
    def test_33_failure_cost(self):self.assertAlmostEqual(20/7,2.857142857142857)
    def test_34_retry_amplification(self):self.assertEqual(3*3*3,27)
    def test_35_p95_not_average(self):
        def p95(x):return sorted(x)[math.ceil(.95*len(x))-1]
        a=[1]*100;b=[100]*2;self.assertNotEqual((p95(a)+p95(b))/2,p95(a+b))
    def test_36_stale_screenshot(self):self.assertNotEqual('screen-r7','screen-r8')
    def test_37_registered_hidden(self):
        state={'registered':True,'visible':False,'authorized':True};self.assertFalse(all(state.values()))
    def test_38_mutable_worktree(self):self.assertNotEqual(hashlib.sha256(b'a').digest(),hashlib.sha256(b'b').digest())
    def test_39_crash_window_idempotency(self):
        with tempfile.TemporaryDirectory() as d:
            db=str(Path(d)/'effects.db')
            c=sqlite3.connect(db);c.execute('create table effects(k text primary key, value text)');c.commit();c.close()
            code='import sqlite3,sys,os;c=sqlite3.connect(sys.argv[1]);c.execute("insert into effects values (?,?)",("K1","done"));c.commit();os._exit(17)'
            r=subprocess.run([sys.executable,'-c',code,db]);self.assertEqual(r.returncode,17)
            c=sqlite3.connect(db);c.execute('insert or ignore into effects values (?,?)',('K1','done'));c.commit();self.assertEqual(c.execute('select count(*) from effects').fetchone()[0],1);c.close()
    def test_40_new_retry_key_duplicates(self):
        with tempfile.TemporaryDirectory() as d:
            c=sqlite3.connect(str(Path(d)/'x.db'));c.execute('create table effects(k text primary key)')
            c.execute('insert into effects values (?)',('K1',));c.execute('insert into effects values (?)',('K2',));self.assertEqual(c.execute('select count(*) from effects').fetchone()[0],2);c.close()

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    record={'kind':'deterministic teaching mechanisms; not production Codex/Claude tests','tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'python':sys.version,'passed':result.wasSuccessful()}
    Path(__file__).with_name('test-results.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
    sys.exit(not result.wasSuccessful())
