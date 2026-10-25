from __future__ import annotations
import json, tempfile, unittest, io, sys
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.error import HTTPError
from core import *
from metrics import *
from server import fixture_server

def tool(cid,name,args):return {'role':'assistant','tool_calls':[{'id':cid,'type':'function','function':{'name':name,'arguments':args if isinstance(args,str) else dump(args)}}]}
class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.w=Workspace(Path(self.tmp.name),Task('x','vendor'))
    def tearDown(self):self.tmp.cleanup()
    def test_initial_fails(self):self.assertFalse(self.w.grade()['success'])
    def test_direct_read_content_and_hash(self):
        r=self.w.execute('read_file',{'path':'rules.json'});self.assertEqual(r['sha256'],digest(r['content'].encode()))
    def test_write_then_grade(self):
        sha=self.w.execute('read_file',{'path':'rules.json'})['sha256'];self.w.execute('set_exclusion',{'dir_name':'vendor','expected_sha256':sha});self.assertTrue(self.w.grade()['success'])
    def test_no_prefix_false_positive(self):
        sha=self.w.execute('read_file',{'path':'rules.json'})['sha256'];self.w.execute('set_exclusion',{'dir_name':'vendor','expected_sha256':sha});self.assertTrue(self.w.included('vendor2/a.txt'))
    def test_nested_is_excluded(self):
        sha=self.w.execute('read_file',{'path':'rules.json'})['sha256'];self.w.execute('set_exclusion',{'dir_name':'vendor','expected_sha256':sha});self.assertFalse(self.w.included('vendor/a/b.txt'))
    def test_path_escape(self):
        with self.assertRaises(ToolError):self.w.execute('read_file',{'path':'../secret'})
    def test_absolute_path(self):
        with self.assertRaises(ToolError):self.w.execute('read_file',{'path':'/etc/passwd'})
    def test_unknown_tool(self):
        with self.assertRaises(ToolError):self.w.execute('shell',{'command':'pwd'})
    def test_wrong_type(self):
        with self.assertRaises(ToolError):self.w.execute('read_file',{'path':3})
    def test_extra_field(self):
        with self.assertRaises(ToolError):self.w.execute('read_file',{'path':'rules.json','extra':True})
    def test_missing_field(self):
        with self.assertRaises(ToolError):self.w.execute('read_file',{})
    def test_argument_array(self):
        with self.assertRaises(ToolError):self.w.execute('read_file',[]) 
    def test_stale_write_refused(self):
        with self.assertRaises(ToolError):self.w.execute('set_exclusion',{'dir_name':'vendor','expected_sha256':'old'})
        self.assertEqual(self.w.writes,0)
    def test_invalid_directory(self):
        sha=self.w.execute('read_file',{'path':'rules.json'})['sha256']
        with self.assertRaises(ToolError):self.w.execute('set_exclusion',{'dir_name':'../outside','expected_sha256':sha})
    def test_same_directory_add_once(self):
        for _ in range(2):
            sha=self.w.execute('read_file',{'path':'rules.json'})['sha256'];self.w.execute('set_exclusion',{'dir_name':'vendor','expected_sha256':sha})
        self.assertEqual(self.w.rules(),['vendor']);self.assertEqual(self.w.writes,1)
    def test_symlink_refused(self):
        p=self.w.root/'README.md';p.unlink();p.symlink_to(self.w.root/'rules.json')
        with self.assertRaises(ToolError):self.w.safe_file('README.md')
    def test_successful_trace(self):
        r=run_episode(Task('x','vendor'));self.assertTrue(r['success']);self.assertEqual(len(r['events']),17);self.assertEqual(r['rounds'],4)
    def test_final_is_not_evidence(self):
        r=run_episode(Task('x','vendor'),SequenceBackend([{'role':'assistant','content':'成功'}]));self.assertFalse(r['success'])
    def test_budget_is_terminal(self):
        r=run_episode(Task('x','vendor'),max_rounds=1);self.assertEqual(r['stop_reason'],'budget_exhausted')
    def test_duplicate_id_not_dispatched_twice(self):
        r=run_episode(Task('x','vendor'),SequenceBackend([tool('x','read_file',{'path':'rules.json'}),tool('x','verify_index',{})]));self.assertEqual(r['stop_reason'],'backend_or_protocol_error')
    def test_unknown_tool_returns_error(self):
        r=run_episode(Task('x','vendor'),SequenceBackend([tool('x','danger',{})]));self.assertFalse(next(e for e in r['events'] if e['event']=='tool_returned')['result']['ok'])
    def test_invalid_json_no_write(self):
        r=run_episode(Task('x','vendor'),SequenceBackend([tool('x','set_exclusion','{') ]));self.assertEqual(r['writes'],0)
    def test_compact_preserves_identity(self):
        m=[{'role':'tool','tool_call_id':'x','content':dump({'ok':True,'result':{'sha256':'abc','diagnostics':'noise'}})}]
        c=prepare_history(m,'trim-diagnostics');self.assertEqual(c[0]['tool_call_id'],'x');self.assertIn('abc',c[0]['content']);self.assertNotIn('diagnostics',c[0]['content']);self.assertIn('diagnostics',m[0]['content'])
    def test_compact_keeps_all_calls(self):
        a=run_episode(Task('x','vendor'));b=run_episode(Task('x','vendor'),policy='trim-diagnostics');self.assertEqual(a['artifact_sha256'],b['artifact_sha256']);self.assertLess(b['request_bytes'],a['request_bytes'])
    def test_usage_unknown_not_zero(self):
        r=run_episode(Task('x','vendor'));self.assertIsNone(r['token_count']);self.assertIsNone(r['financial_cost_usd'])
    def test_events_monotonic(self):
        es=run_episode(Task('x','vendor'))['events'];self.assertEqual([e['seq'] for e in es],list(range(len(es))));self.assertEqual([e['at_ms'] for e in es],sorted(e['at_ms'] for e in es))
    def test_task_splits_explicit(self):self.assertEqual(sum(t.split=='heldout-demo' for t in tasks()),2)
    def test_remote_default_refused(self):
        with self.assertRaises(ValueError):HttpBackend('https://example.com/v1','any')
    def test_remote_http_refused(self):
        with self.assertRaises(ValueError):HttpBackend('http://example.com/v1','any',allow_remote=True)
    def test_url_credentials_refused(self):
        with self.assertRaises(ValueError):HttpBackend('http://user:secret@127.0.0.1/v1','any')
    def test_real_http_contract(self):
        with fixture_server() as url:r=run_episode(Task('x','vendor'),HttpBackend(url,'scripted-protocol-fixture','local-fixture-key'))
        self.assertTrue(r['success']);self.assertIsNone(r['token_count'])
    def test_wrong_key_is_not_retried(self):
        with fixture_server() as url:r=run_episode(Task('x','vendor'),HttpBackend(url,'scripted-protocol-fixture','wrong'))
        self.assertEqual(r['rounds'],1);self.assertEqual(r['writes'],0)
    def test_server_admits_no_real_weights(self):
        with fixture_server() as url:
            h=json.load(urlopen(url.replace('/v1','')+'/health'));self.assertFalse(h['model_weights_loaded'])
class AccountingTests(unittest.TestCase):
    def test_zero_success_ratio_undefined(self):
        r={'task_id':'x','success':False,'elapsed_ms':1,'request_bytes':1,'financial_cost_usd':1};self.assertIsNone(summary([r])['cost_per_success_usd'])
    def test_failure_cost_included(self):
        rs=[{'task_id':str(i),'success':bool(i),'elapsed_ms':i+1,'request_bytes':1,'financial_cost_usd':1} for i in range(2)];self.assertEqual(summary(rs)['cost_per_success_usd'],2)
    def test_paired_gains_regressions(self):
        a=[{'task_id':'a','success':True},{'task_id':'b','success':False}];b=[{'task_id':'a','success':False},{'task_id':'b','success':True}];self.assertEqual(paired(a,b),dict(both_pass=0,gain=1,regression=1,both_fail=0))
    def test_unmatched_tasks_rejected(self):
        with self.assertRaises(ValueError):paired([{'task_id':'a'}],[{'task_id':'b'}])
    def test_duplicate_tasks_rejected(self):
        with self.assertRaises(ValueError):paired([{'task_id':'a'},{'task_id':'a'}],[{'task_id':'a'}])
    def test_pareto(self):self.assertTrue(pareto_dominates(dict(successes=8,cost=1,latency=1),dict(successes=8,cost=2,latency=1)))
    def test_tradeoff_is_not_dominance(self):self.assertFalse(pareto_dominates(dict(successes=7,cost=1,latency=1),dict(successes=8,cost=2,latency=1)))
    def test_equal_is_not_strict_dominance(self):
        a=dict(successes=8,cost=1,latency=1);self.assertFalse(pareto_dominates(a,a))
    def test_missing_metrics_fail(self):
        with self.assertRaises(ValueError):pareto_dominates(dict(successes=1,cost=None,latency=1),dict(successes=1,cost=2,latency=2))
    def test_kv_bytes(self):self.assertEqual(resource_ledger()['kv_bytes'],134217728)
    def test_training_bytes_explicit(self):self.assertEqual(resource_ledger()['training_state_bytes_explicit_recipe'],18_000_000_000)
    def test_critical_path_not_sum(self):
        n=[{'id':'a','ms':40,'deps':[]},{'id':'b','ms':20,'deps':['a']},{'id':'c','ms':60,'deps':['a']},{'id':'d','ms':30,'deps':['b','c']}];self.assertEqual(longest_path_ms(n),130)
    def test_bad_dag(self):
        with self.assertRaises(ValueError):longest_path_ms([{'id':'a','ms':1,'deps':['b']}])
    def test_percentile_named(self):self.assertEqual(nearest_rank(list(range(1,21)),.95),19)
    def test_empty(self):self.assertIsNone(summary([])['success_rate']);self.assertIsNone(nearest_rank([],.95))

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]);buf=io.StringIO();r=unittest.TextTestRunner(stream=buf,verbosity=2).run(suite)
    out=Path(__file__).resolve().parent/'results';out.mkdir(exist_ok=True)
    (out/'tests.log').write_text(buf.getvalue());(out/'tests.json').write_text(json.dumps({'tests_run':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'skipped':len(r.skipped),'passed':r.wasSuccessful()},indent=2));print(buf.getvalue());sys.exit(not r.wasSuccessful())
