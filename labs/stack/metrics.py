"""Explicit units and denominators. All numeric worked examples are constructed, not GPU measurements."""
from __future__ import annotations
import math

def mean(values):
    if not values:return None
    return sum(values)/len(values)

def nearest_rank(values,p):
    if not 0<p<=1:raise ValueError('p must lie in (0,1]')
    if not values:return None
    return sorted(values)[max(0,math.ceil(p*len(values))-1)]

def summary(receipts):
    n=len(receipts);ok=sum(bool(r['success']) for r in receipts)
    known=all(r.get('financial_cost_usd') is not None for r in receipts)
    cost=sum(r['financial_cost_usd'] for r in receipts) if known and n else None
    return {'trials':n,'successes':ok,'success_rate':ok/n if n else None,
            'total_request_bytes':sum(r['request_bytes'] for r in receipts),
            'cost_usd':cost,'cost_per_success_usd':cost/ok if cost is not None and ok else None,
            'p50_ms_nearest_rank':nearest_rank([r['elapsed_ms'] for r in receipts],.5),
            'p95_ms_nearest_rank':nearest_rank([r['elapsed_ms'] for r in receipts],.95)}

def paired(a,b):
    da={r['task_id']:r for r in a};db={r['task_id']:r for r in b}
    if len(da)!=len(a) or len(db)!=len(b) or da.keys()!=db.keys():raise ValueError('paired task IDs must match uniquely')
    counts={'both_pass':0,'gain':0,'regression':0,'both_fail':0}
    for k in da:
        x,y=da[k]['success'],db[k]['success']
        counts['both_pass' if x and y else 'gain' if y else 'regression' if x else 'both_fail']+=1
    return counts

def pareto_dominates(a,b):
    # Maximize success count; minimize cost and latency. All measures must be supplied.
    for x in (a,b):
        if any(x.get(k) is None for k in ('successes','cost','latency')):raise ValueError('missing measurement')
    weak=a['successes']>=b['successes'] and a['cost']<=b['cost'] and a['latency']<=b['latency']
    strict=a['successes']>b['successes'] or a['cost']<b['cost'] or a['latency']<b['latency']
    return weak and strict

def longest_path_ms(nodes):
    finish={}
    for node in nodes:
        deps=node['deps']
        if any(d not in finish for d in deps):raise ValueError('nodes must be a topological order')
        if node['ms']<0:raise ValueError('negative duration')
        finish[node['id']]=max((finish[d] for d in deps),default=0)+node['ms']
    return max(finish.values(),default=0)

def resource_ledger(n=1_000_000_000,layers=16,kv_heads=4,head_dim=64,positions=1024,batch=8,element_bytes=2):
    if min(n,layers,kv_heads,head_dim,positions,batch,element_bytes)<=0:raise ValueError('positive dimensions required')
    kv=2*layers*kv_heads*head_dim*positions*batch*element_bytes
    return {'parameters':n,'weight_bytes_fp16':2*n,'training_state_bytes_explicit_recipe':18*n,
            'training_recipe':'FP16 weights 2 + FP32 gradients 4 + FP32 master weights 4 + Adam moments 8 bytes/parameter; activations excluded',
            'kv_bytes':kv,'kv_MiB':kv/2**20,'dense_parameter_matmul_forward_FLOPs_per_token_approx':2*n,
            'caveat':'Dense parameter-bearing matmul estimate only; attention, recomputation, routing and actual utilization require separate accounting.'}
