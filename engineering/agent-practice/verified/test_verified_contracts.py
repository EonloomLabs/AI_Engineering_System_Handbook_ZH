"""Executable teaching contracts, not production Codex or Claude tests.

Models below deliberately simplify control flow. Tests validate the named
invariant only. No model calls, no remote effects, no Rust execution.
"""
from __future__ import annotations
from dataclasses import dataclass, field, replace
from pathlib import Path
import hashlib,json,unittest,sys

@dataclass(frozen=True)
class Identity:
    rewrite: int = 1
    model: str = 'model-A'
    comp_hash: str = 'v1'
    owner: int = 1

@dataclass
class History:
    events: list[str]
    identity: Identity=field(default_factory=Identity)
    disk: list[str]=field(default_factory=list)

@dataclass(frozen=True)
class Candidate:
    prefix: tuple[str,...]
    identity: Identity
    summary: str='S'

# Our model of an acceptance boundary, not a copied Codex implementation.
def install(h:History,c:Candidate,persist_ok:bool=True)->dict:
    if h.identity!=c.identity or tuple(h.events[:len(c.prefix)])!=c.prefix:
        return {'accepted':False,'persisted':False}
    h.events=[c.summary]+h.events[len(c.prefix):]
    if persist_ok:h.disk=h.events.copy()
    return {'accepted':True,'persisted':persist_ok}

@dataclass
class Worker:
    completed: bool=True
    closed: bool=True
    artifacts_ok: bool=True
    owner: int=1

def publish(w:Worker,current_owner:int,baseline_ok:bool=True,db_ok:bool=True)->dict:
    if not(w.completed and w.closed and w.artifacts_ok and w.owner==current_owner):
        return {'baseline':False,'published':False}
    return {'baseline':baseline_ok,'published':baseline_ok and db_ok}

def tool_path(*,pre_block:bool=False,post_block:bool=False,style:str='codex'):
    effects=[];log=[]
    if pre_block:return effects,log,'blocked-before-execution'
    effects.append('write');log.append('original-output')
    if post_block:
        return effects,log,('rejected-result' if style=='codex' else 'original-output + block reason')
    return effects,log,'original-output'

class Contracts(unittest.TestCase):
    def setUp(self):
        self.h=History(['e1','e2','e3']);self.c=Candidate(tuple(self.h.events),self.h.identity)
    def test_01_live_suffix_is_kept(self):
        self.h.events+=['e4','e5'];self.assertTrue(install(self.h,self.c)['accepted']);self.assertEqual(self.h.events,['S','e4','e5'])
    def test_02_rewrite_invalidates_candidate(self):
        self.h.identity=replace(self.h.identity,rewrite=2);self.assertFalse(install(self.h,self.c)['accepted'])
    def test_03_owner_change_invalidates_candidate(self):
        self.h.identity=replace(self.h.identity,owner=2);self.assertFalse(install(self.h,self.c)['accepted'])
    def test_04_model_change_invalidates_candidate(self):
        self.h.identity=replace(self.h.identity,model='model-B');self.assertFalse(install(self.h,self.c)['accepted'])
    def test_05_compression_version_change_invalidates(self):
        self.h.identity=replace(self.h.identity,comp_hash='v2');self.assertFalse(install(self.h,self.c)['accepted'])
    def test_06_shortened_history_rejected(self):
        self.h.events.pop();self.assertFalse(install(self.h,self.c)['accepted'])
    def test_07_accepted_is_not_durable(self):
        result=install(self.h,self.c,persist_ok=False);self.assertEqual(result,{'accepted':True,'persisted':False});self.assertEqual(self.h.disk,[])
    def test_08_rejected_candidate_preserves_history(self):
        self.h.events[1]='replaced';old=self.h.events.copy();install(self.h,self.c);self.assertEqual(old,self.h.events)
    def test_09_live_permission_is_not_model_snapshot(self):
        settings={'model':'A','router':'r1'};grant={'src'};snapshot=settings.copy();grant.add('tests');self.assertEqual(snapshot,settings);self.assertIn('tests',grant)
    def test_10_pre_hook_blocks_effect(self):
        e,l,r=tool_path(pre_block=True);self.assertEqual(e,[]);self.assertEqual(l,[]);self.assertEqual(r,'blocked-before-execution')
    def test_11_post_hook_does_not_undo_effect(self):
        e,l,r=tool_path(post_block=True);self.assertEqual(e,['write']);self.assertEqual(r,'rejected-result')
    def test_12_cross_product_post_block_is_different(self):
        a=tool_path(post_block=True,style='codex');b=tool_path(post_block=True,style='claude');self.assertEqual(a[0],b[0]);self.assertNotEqual(a[2],b[2])
    def test_13_model_view_does_not_rewrite_log(self):
        log=['email + order'];view='order';self.assertNotIn('email',view);self.assertIn('email',log[0])
    def test_14_parameter_replacement_not_merge(self):
        old={'path':'a','limit':10};replacement={'path':'b'};effective=dict(replacement);self.assertNotIn('limit',effective);self.assertIn('limit',old)
    def test_15_completed_worker_not_published(self):
        self.assertFalse(publish(Worker(closed=False),1)['published'])
    def test_16_invalid_artifacts_not_published(self):
        self.assertFalse(publish(Worker(artifacts_ok=False),1)['published'])
    def test_17_stale_lease_not_published(self):
        self.assertFalse(publish(Worker(owner=1),2)['published'])
    def test_18_baseline_and_db_have_distinct_boundaries(self):
        self.assertEqual(publish(Worker(),1,db_ok=False),{'baseline':True,'published':False})
    def test_19_publication_requires_all_checks(self):
        self.assertTrue(publish(Worker(),1)['published'])
    def test_20_skill_text_and_grant_have_different_lifetimes(self):
        context=['skill-body'];grant={'read_file'};grant.clear();self.assertIn('skill-body',context);self.assertNotIn('read_file',grant)
    def test_21_file_exists_not_automatically_loaded(self):
        files={'AGENTS.md','CLAUDE.md'};supported={'CLAUDE.md'};self.assertEqual(files&supported,{'CLAUDE.md'})
    def test_22_explicit_import_can_add_rule(self):
        loaded={'CLAUDE.md'};imports={'AGENTS.md'};self.assertIn('AGENTS.md',loaded|imports)
    def test_23_mailbox_receipt_not_execution(self):
        mailbox=[{'id':'m1','payload':'task'}];executed=[];self.assertTrue(mailbox);self.assertFalse(executed)
    def test_24_registration_not_visible(self):
        registered={'A','B'};visible={'A'};self.assertIn('B',registered);self.assertNotIn('B',visible)
    def test_25_deferred_discovery_not_direct_spec(self):
        direct={'search_tools'};deferred={'B'};self.assertNotIn('B',direct);self.assertIn('B',deferred)
    def test_26_done_response_not_verified_goal(self):
        self.assertFalse(all([True,True,False,False]))
    def test_27_failed_and_discarded_attempts_cost(self):
        attempts=[(2,False),(3,False),(5,True)];self.assertEqual(sum(a for a,_ in attempts),10);self.assertEqual(sum(ok for _,ok in attempts),1)
    def test_28_retry_same_error_is_not_new_evidence(self):
        observations=['not-authorized']*5;self.assertEqual(len(set(observations)),1)
    def test_29_full_sources_match_git_blobs(self):
        root=Path(__file__).parent;m=json.loads((root/'manifest.json').read_text());checked=0
        for s in m:
            if not s.get('git_blob_verified'):continue
            data=(root/s['local_file']).read_bytes();git=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            self.assertEqual(git,s['source_blob_sha']);self.assertEqual(hashlib.sha256(data).hexdigest(),s['sha256']);checked+=1
        self.assertEqual(checked,4)
    def test_30_evidence_statuses_are_explicit(self):
        m=json.loads(Path(__file__).with_name('manifest.json').read_text());self.assertEqual(len(m),42)
        self.assertEqual(sum(s['id'].startswith('C')for s in m),18)
        self.assertEqual(sum(s['id'].startswith('A')for s in m),17)
        self.assertEqual(sum(s['id'].startswith('D')for s in m),7)
        self.assertTrue(all(s.get('read_note') for s in m));self.assertTrue(all(not s.get('raw_html_mirrored',False)for s in m if not s['id'].startswith('C')))

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Contracts)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'kind':'original deterministic teaching contracts + local evidence integrity; NOT Codex/Claude production tests',
            'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'passed':result.wasSuccessful(),'python':sys.version}
    Path(__file__).with_name('test-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    sys.exit(not result.wasSuccessful())
