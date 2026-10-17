"""Small, offline correctness witnesses; Python 3.10+, standard library only.
No network, external effects, commercial LLM calls, GPU benchmarks or training.
The tiny decoder uses fixed weights and absolute positions, not a product model.
"""
from __future__ import annotations
import codecs
import json
import math
import unittest
from pathlib import Path


def softmax(xs: list[float]) -> list[float]:
    m = max(xs)
    es = [math.exp(x-m) for x in xs]
    return [x/sum(es) for x in es]


def dot(x: list[float], y: list[float]) -> float:
    if len(x) != len(y):
        raise ValueError('dot dimension mismatch')
    return sum(a*b for a,b in zip(x,y))


def project(x: list[float], w: list[list[float]]) -> list[float]:
    if len(x) != len(w):
        raise ValueError('projection dimension mismatch')
    return [sum(x[i]*w[i][j] for i in range(len(x))) for j in range(len(w[0]))]


def weights(rows: int, cols: int, seed: int) -> list[list[float]]:
    return [[math.sin((i+1)*13+(j+1)*7+seed)*.3 for j in range(cols)] for i in range(rows)]


def norm(x: list[float]) -> list[float]:
    mean = sum(x)/len(x)
    var = sum((a-mean)**2 for a in x)/len(x)
    return [(a-mean)/math.sqrt(var+1e-5) for a in x]


class TinyDecoder:
    """Two causal pre-LN layers, width 4, one head, FFN width 8, vocab 8."""
    def __init__(self):
        self.emb = weights(8,4,1)
        self.lm_head = weights(4,8,2)
        self.layers = [dict(q=weights(4,4,10+l), k=weights(4,4,20+l),
                            v=weights(4,4,30+l), o=weights(4,4,40+l),
                            up=weights(4,8,50+l), down=weights(8,4,60+l)) for l in range(2)]

    def forward(self, ids: list[int], cache=None, position_start: int | None=None):
        if not ids or any(type(t) is not int or not 0 <= t < 8 for t in ids):
            raise ValueError('nonempty token IDs in [0,8) required')
        old = cache if cache is not None else [{'k':[], 'v':[]} for _ in self.layers]
        past = len(old[0]['k'])
        if any(len(c['k']) != past or len(c['v']) != past for c in old):
            raise ValueError('inconsistent cache lengths')
        start = past if position_start is None else position_start
        hs = [[self.emb[t][j]+.1*math.sin((start+i+1)/(j+1)) for j in range(4)] for i,t in enumerate(ids)]
        updated=[]; trace=[]
        for li,p in enumerate(self.layers):
            n=[norm(x) for x in hs]
            qs=[project(x,p['q']) for x in n]
            ks=old[li]['k']+[project(x,p['k']) for x in n]
            vs=old[li]['v']+[project(x,p['v']) for x in n]
            out=[]; atts=[]
            for i,q in enumerate(qs):
                visible=past+i+1
                a=softmax([dot(q,k)/2 for k in ks[:visible]])
                agg=[sum(a[j]*vs[j][d] for j in range(visible)) for d in range(4)]
                att=project(agg,p['o'])
                r=[x+y for x,y in zip(hs[i],att)]
                ff=project([max(x,0) for x in project(norm(r),p['up'])],p['down'])
                out.append([x+y for x,y in zip(r,ff)])
                atts.append(a)
            hs=out; updated.append({'k':ks,'v':vs})
            trace.append({'layer':li,'new_query_shape':[len(ids),4],
                          'key_shape':[len(ks),4], 'visible_counts':[past+i+1 for i in range(len(ids))],
                          'attention_rows':atts})
        logits=[project(norm(x),self.lm_head) for x in hs]
        return logits,updated,trace


def attention_loss(q,ks,vs,grad):
    a=softmax([dot(q,k)/math.sqrt(len(q)) for k in ks])
    out=[sum(a[j]*vs[j][d] for j in range(len(ks))) for d in range(len(vs[0]))]
    return dot(out,grad),a,out


def query_gradient(q,ks,vs,grad):
    _,a,_=attention_loss(q,ks,vs,grad)
    da=[dot(v,grad) for v in vs]
    center=sum(x*y for x,y in zip(a,da))
    ds=[x*(y-center) for x,y in zip(a,da)]
    return [sum(ds[j]*ks[j][d] for j in range(len(ks)))/math.sqrt(len(q)) for d in range(len(q))]


def parse_sse_chunks(chunks: list[bytes]):
    """Minimal LF-delimited teaching parser, not the full EventSource standard."""
    decoder=codecs.getincrementaldecoder('utf-8')()
    buf='';events=[]
    for chunk in chunks:
        buf+=decoder.decode(chunk)
        while '\n\n' in buf:
            event,buf=buf.split('\n\n',1)
            data='\n'.join(line[5:].lstrip(' ') for line in event.split('\n') if line.startswith('data:'))
            if data: events.append(json.loads(data))
    buf+=decoder.decode(b'',final=True)
    if buf.strip(): raise ValueError('incomplete event: do not execute')
    return events


def apply_event(state: str, event: str) -> str:
    transitions={('pending','start'):'running',('running','timeout'):'unknown',
                 ('running','success'):'succeeded',('unknown','verified_applied'):'succeeded',
                 ('unknown','verified_not_applied'):'retryable'}
    if (state,event) not in transitions:
        raise ValueError(f'illegal transition {state}/{event}')
    return transitions[(state,event)]


class WitnessTests(unittest.TestCase):
    def test_attention_hand_calculation(self):
        _,a,out=attention_loss([1,1],[[1,0],[0,1],[1,1]],[[1,2],[3,4],[4,6]],[1,1])
        self.assertAlmostEqual(out[0],3.00697969,places=6)
        self.assertAlmostEqual(sum(a),1)

    def test_query_gradient_finite_difference(self):
        q=[.4,-.7];ks=[[1,0],[0,1],[1,1]];vs=[[1,2],[3,4],[4,6]];g=[.3,-.2]
        analytic=query_gradient(q,ks,vs,g);eps=1e-6
        for i in range(2):
            plus=q.copy();minus=q.copy();plus[i]+=eps;minus[i]-=eps
            numeric=(attention_loss(plus,ks,vs,g)[0]-attention_loss(minus,ks,vs,g)[0])/(2*eps)
            self.assertAlmostEqual(analytic[i],numeric,places=8)

    def test_prefill_decode_equivalence(self):
        m=TinyDecoder();ids=[1,2,3,4,5]
        full,_,_=m.forward(ids)
        _,cache,_=m.forward(ids[:3])
        for i in range(3,len(ids)):
            got,cache,_=m.forward([ids[i]],cache)
            for a,b in zip(got[0],full[i]):self.assertAlmostEqual(a,b,places=12)

    def test_chunk_decode_equivalence(self):
        m=TinyDecoder();full,_,_=m.forward([1,2,3,4,5])
        _,cache,_=m.forward([1,2,3]);got,_,trace=m.forward([4,5],cache)
        self.assertEqual(trace[0]['visible_counts'],[4,5])
        for i in range(2):
            for a,b in zip(got[i],full[i+3]):self.assertAlmostEqual(a,b,places=12)

    def test_wrong_position_is_detectable(self):
        m=TinyDecoder();_,cache,_=m.forward([1,2,3])
        good,_,_=m.forward([4],cache);bad,_,_=m.forward([4],cache,position_start=0)
        self.assertGreater(max(abs(a-b) for a,b in zip(good[0],bad[0])),1e-5)

    def test_prefix_edit_invalidates_suffix(self):
        m=TinyDecoder();_,old,_=m.forward([1,2,3]);right,_,_=m.forward([1,6,3,4])
        wrong,_,_=m.forward([4],old)
        self.assertGreater(max(abs(a-b) for a,b in zip(right[-1],wrong[0])),1e-5)

    def test_causal_mask_is_offset(self):
        past=3;new=2
        correct=[[j<=past+i for j in range(past+new)] for i in range(new)]
        naive=[[j<=i for j in range(past+new)] for i in range(new)]
        self.assertEqual(correct,[[True,True,True,True,False],[True]*5]);self.assertNotEqual(correct,naive)

    def test_sse_every_two_piece_byte_split(self):
        event={'kind':'arguments_done','call_id':'c19','path':'中文.py'}
        raw=('data: '+json.dumps(event,ensure_ascii=False)+'\n\n').encode()
        for i in range(len(raw)+1):self.assertEqual(parse_sse_chunks([raw[:i],raw[i:]]),[event])

    def test_sse_one_byte_chunks(self):
        event={'text':'完成'};raw=('data: '+json.dumps(event,ensure_ascii=False)+'\n\n').encode()
        self.assertEqual(parse_sse_chunks([bytes([b]) for b in raw]),[event])

    def test_sse_partial_is_not_complete(self):
        with self.assertRaises(ValueError):parse_sse_chunks([b'data: {"x":1}'])

    def test_unknown_is_not_failed(self):
        state=apply_event(apply_event('pending','start'),'timeout')
        self.assertEqual(state,'unknown')
        with self.assertRaises(ValueError):apply_event(state,'start')
        self.assertEqual(apply_event(state,'verified_applied'),'succeeded')

    def test_online_softmax_merge(self):
        m=1;l=1;u=2;new_m=3;alpha=math.exp(m-new_m)
        got=(alpha*u+10)/(alpha*l+1)
        a=softmax([1,3]);self.assertAlmostEqual(got,a[0]*2+a[1]*10)


def main():
    import io
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(WitnessTests))
    model=TinyDecoder();p,c,tr=model.forward([1,2,3]);first=max(range(8),key=lambda i:p[-1][i])
    nxt,nc,ntr=model.forward([first],c)
    report={'scope':'Deterministic teaching calculations and state/parser tests; not model capability, autonomous coding or security benchmarks.',
            'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
            'prefill_tokens':[1,2,3], 'prefill_last_logits':p[-1], 'first_greedy_token':first,
            'prefill_cache_lengths':[len(x['k']) for x in c], 'next_decode_logits':nxt[-1],
            'decode_cache_lengths':[len(x['k']) for x in nc], 'prefill_trace':tr,'decode_trace':ntr,
            'test_output':stream.getvalue()}
    Path(__file__).with_name('runtime_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(stream.getvalue());print(json.dumps({k:v for k,v in report.items() if k not in ['test_output','prefill_trace','decode_trace']},ensure_ascii=False,indent=2))
    if not result.wasSuccessful():raise SystemExit(1)
if __name__=='__main__':main()
