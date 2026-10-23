
"""Checks for diagram data and editorial invariants; no remote model/GPU claims."""
from pathlib import Path
import unittest, json, math, hashlib
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"diagrams/source"
RUN=json.loads((D/"model-run.json").read_text())
CASES=json.loads((D/"mechanism-cases.json").read_text())
def mm(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def softmax(a):
    e=[math.exp(x-max(a)) for x in a];s=sum(e);return [x/s for x in e]
class DiagramDataTests(unittest.TestCase):
    def close(self,a,b):self.assertLess(max(abs(x-y) for x,y in zip(a,b)),1e-10)
    def test_q_projection_uses_n1_not_embedding(self):
        t=RUN["initial_trace"];p=RUN["initial_parameters"]
        self.close(mm([t["n1"][0][2]],p["Wq"])[0],t["q"][0][2])
    def test_k_projection(self):
        t=RUN["initial_trace"];self.close(mm([t["n1"][0][2]],RUN["initial_parameters"]["Wk"])[0],t["k"][0][2])
    def test_v_projection(self):
        t=RUN["initial_trace"];self.close(mm([t["n1"][0][2]],RUN["initial_parameters"]["Wv"])[0],t["v"][0][2])
    def test_attention_contributions_sum_to_mix(self):
        t=RUN["initial_trace"];a=t["A"][0][2];v=t["v"][0]
        self.close([sum(a[i]*v[i][j] for i in range(5)) for j in range(4)],t["mix"][0][2])
    def test_future_positions_contribute_zero(self):
        self.assertEqual(RUN["initial_trace"]["A"][0][2][3:],[0.,0.])
    def test_residual_forward_has_bypass(self):
        t=RUN["initial_trace"];self.close([x+y for x,y in zip(t["x"][0][2],t["attn_delta"][0][2])],t["residual"][0][2])
    def test_ffn_forward_has_bypass(self):
        t=RUN["initial_trace"];self.close([x+y for x,y in zip(t["residual"][0][2],t["ff_delta"][0][2])],t["hidden"][0][2])
    def test_softmax_stable_and_direct_equal(self):
        e=[math.exp(x) for x in [2,1,0]]
        self.close([x/sum(e) for x in e],softmax([2,1,0]))
    def test_softmax_sampling_interval_is_b(self):
        p=softmax([2,1,0]);self.assertLess(p[0],.7);self.assertGreater(sum(p[:2]),.7)
    def test_rrf_scores_and_order(self):
        a=1/61+1/63;b=1/62+1/61;c=1/63+1/62
        self.assertGreater(b,a);self.assertGreater(a,c)
        self.assertEqual([round(b,6),round(a,6),round(c,6)],[.032522,.032266,.032002])
    def test_absolute_cache_masks(self):
        masks=[[k<=q for k in range(5)] for q in [3,4]]
        self.assertEqual(masks,[[True,True,True,True,False],[True]*5])
        v=[1,2,3,4,5]
        self.close([sum(x for x,ok in zip(v,m) if ok)/sum(m) for m in masks],[2.5,3.])
    def test_local_triangle_counterexample(self):
        masks=[[k<=q for k in range(5)] for q in [0,1]]
        v=[1,2,3,4,5]
        self.close([sum(x for x,ok in zip(v,m) if ok)/sum(m) for m in masks],[1.,1.5])
    def test_generation_uses_actual_run(self):
        s=RUN["generation"]["steps"]
        self.assertEqual([x["cache_after"] for x in s],[3,4,5])
        self.assertEqual(s[0]["selected"],RUN["generation"]["tokens"][3])
        self.assertEqual(s[1]["input"],[s[0]["selected"]])
        self.assertEqual(s[2]["input"],[s[1]["selected"]])
        self.assertEqual(RUN["generation"]["reason"],"eos")
    def test_cache_logits_equal_full_recompute(self):
        for a,b in zip(RUN["generation"]["steps"],RUN["generation_full"]["steps"]):
            self.close(a["logits"],b["logits"])
    def test_embedding_shared_id_not_bits(self):
        e=RUN["initial_parameters"]["E"]
        self.close(e[2],[-.3,.8,.1,.5])
        self.assertEqual(e[2],e[[1,2,3][1]])
        self.assertEqual(e[2],e[[4,2,0][1]])
        self.assertEqual(len(e[2]),4)
    def test_paired_task_counts(self):
        both,old_only,new_only,neither=12,1,3,4
        self.assertEqual(sum([both,old_only,new_only,neither]),20)
        self.assertEqual(both+old_only,13);self.assertEqual(both+new_only,15)
    def test_q006_is_declared_independent(self):
        self.assertIn("独立",CASES["Q006"]["purpose"])
        self.assertIn("X=[[1,0],[0,1]]",CASES["Q006"]["purpose"])
        self.assertEqual(mm([[1,0],[0,1]],[[1,0],[1,1]]),[[1,0],[1,1]])
    def test_bitemporal_order_preserved(self):
        p=CASES["Q071"]["purpose"]
        for t in ["10月3日","10月1日","10月8日","10月5日"]:self.assertIn(t,p)
    def test_diagram_xml_valid(self):
        for p in (ROOT/"diagrams/rendered").glob("*.svg"):
            tree=etree.fromstring(p.read_bytes())
            self.assertTrue(tree.get("viewBox") or tree.get("viewbox"),str(p))
    def test_required_semantic_graphs_exist(self):
        names=json.loads((ROOT/"diagrams/rendered/manifest.json").read_text())
        texts=json.dumps(names,ensure_ascii=False)
        for s in ["trace-forward","Q061","Q071","Q091"]:self.assertIn(s,texts)
if __name__=="__main__":unittest.main(verbosity=2)
