"""Run cumulative, inspectable teaching experiments. Offline is the default.
python run.py all
python run.py live --base-url http://127.0.0.1:8000/v1 --model YOUR_MODEL --acknowledge-cost
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, platform, sys
from pathlib import Path
from core import *
from metrics import *
from server import fixture_server
HERE=Path(__file__).resolve().parent

def save(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def trace_page(receipt,path):
    import html
    rows=[]
    for e in receipt['events']:
        rows.append('<tr><td>'+str(e['seq'])+'</td><td>'+f"{e['at_ms']:.3f}"+'</td><td>'+html.escape(e['event'])+'</td><td><details><summary>查看事件字段</summary><pre>'+html.escape(json.dumps(e,ensure_ascii=False,indent=2))+'</pre></details></td></tr>')
    text='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>索引助手运行记录</title><style>body{font:16px/1.75 system-ui;max-width:1100px;margin:40px auto;padding:0 18px;color:#1b2735}table{width:100%;border-collapse:collapse}td,th{text-align:left;vertical-align:top;padding:10px;border-bottom:1px solid #dde1e5}pre{white-space:pre-wrap;overflow-wrap:anywhere}summary{cursor:pointer}h1{font-size:28px}</style><h1>一次任务的完整事件记录</h1><p>本页来自实际本地运行。后端是脚本化协议夹具，不是LLM；耗时不是GPU或商用模型性能。请按事件号定位提议、动作、回填和最终验收。</p><table><thead><tr><th>序号</th><th>自开始起毫秒</th><th>事件</th><th>数据</th></tr></thead><tbody>'''+''.join(rows)+'</tbody></table></html>'
    path.write_text(text,encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('stage',choices=['all','observe','build','optimize','serve','stack','live']);ap.add_argument('--out',type=Path,default=HERE/'results');ap.add_argument('--base-url');ap.add_argument('--model');ap.add_argument('--acknowledge-cost',action='store_true');ap.add_argument('--allow-remote',action='store_true')
    a=ap.parse_args();out=a.out;out.mkdir(parents=True,exist_ok=True)
    if a.stage=='live':
        if not a.acknowledge_cost or not a.base_url or not a.model:ap.error('live requires base URL, model and explicit --acknowledge-cost')
        backend=HttpBackend(a.base_url,a.model,os.environ.get('AI_LAB_API_KEY',''),allow_remote=a.allow_remote)
        r=run_episode(tasks()[0],backend,policy='trim-diagnostics');save(out/'live-receipt.json',r);print(json.dumps({'success':r['success'],'stop_reason':r['stop_reason'],'elapsed_ms':r['elapsed_ms'],'artifact':r['artifact']},ensure_ascii=False));return
    results={'scope':'local execution and deterministic protocol experiments; no commercial model, GPU, official benchmark or hidden-test performance measured','environment':{'python':sys.version,'platform':platform.platform()},'stages':{}}
    if a.stage in ['all','observe','build']:
        r=run_episode(tasks()[0]);save(out/'a1-receipt.json',r);trace_page(r,out/'trace-viewer.html')
        (out/'a1-events.jsonl').write_text('\n'.join(dump(e) for e in r['events'])+'\n')
        results['stages']['observe']={'events':len(r['events']),'success':r['success'],'backend':r['backend']}
        early=run_episode(tasks()[0],SequenceBackend([{'role':'assistant','content':'done'}]));save(out/'a2-early-final.json',early)
        results['stages']['build']={'early_final_is_not_success':not early['success'],'claim':'host grader is independent of final text'}
    if a.stage in ['all','optimize','stack']:
        baseline=[run_episode(t,policy='full') for t in tasks()]
        candidate=[run_episode(t,policy='trim-diagnostics') for t in tasks()]
        save(out/'a3-baseline.json',baseline);save(out/'a3-candidate.json',candidate)
        compare={'baseline':summary(baseline),'candidate':summary(candidate),'paired':paired(baseline,candidate),'scope':'request-byte reduction on scripted fixtures; NOT evidence of model-quality equivalence or GPU speedup'}
        save(out/'a3-comparison.json',compare);results['stages']['optimize']=compare
    if a.stage in ['all','serve']:
        with fixture_server() as url:
            r=run_episode(tasks()[0],HttpBackend(url,'scripted-protocol-fixture','local-fixture-key'))
        save(out/'a4-http-receipt.json',r)
        # Real weights, but only the previously trained toy continuation model, not a coding model.
        script=HERE.parent/'model/lab/reference_inference.py';spec=importlib.util.spec_from_file_location('toy_reference',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        data=HERE.parent/'model/data/weights_trained.json';p=json.loads(data.read_text())['parameters'];ids,steps=m.generate([6,1,2],p)
        assert ids==[6,1,2,3,5,7]
        toy={'weights_sha256':hashlib.sha256(data.read_bytes()).hexdigest(),'input_ids':[6,1,2],'output_ids':ids,'logits':[s['logits'] for s in steps],'scope':'actual CPU calculation using existing toy model weights; not a general language or tool-use model'}
        save(out/'a4-toy-model.json',toy)
        results['stages']['serve']={'http_contract_success':r['success'],'toy_generation':ids,'real_engine_benchmark':'NOT_RUN','course_assignment_complete':False}
    if a.stage in ['all','stack']:
        numeric={'resource_ledger':resource_ledger(),'critical_path_ms':longest_path_ms([{'id':'m1','ms':40,'deps':[]},{'id':'read','ms':20,'deps':['m1']},{'id':'search','ms':60,'deps':['m1']},{'id':'m2','ms':30,'deps':['read','search']}]),'sum_task_ms':150,'amdahl_speedup_for_60_percent_doubled':1/(.4+.6/2),'scope':'constructed dimensions and durations; analytical examples, not performance measurements'}
        save(out/'a5-ledger.json',numeric);results['stages']['stack']=numeric
    save(out/'run-report.json',results);print(json.dumps(results,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
