"""Offline witnesses for worked arithmetic, not model performance benchmarks."""
import math, json
from pathlib import Path

def softmax(xs):
    m=max(xs); ex=[math.exp(x-m) for x in xs];s=sum(ex)
    return [x/s for x in ex]

def main():
    w=softmax([1/math.sqrt(2),1/math.sqrt(2),2/math.sqrt(2)])
    vs=[[1,2],[3,4],[4,6]]
    out=[sum(w[i]*vs[i][j] for i in range(3)) for j in range(2)]
    data={
      'attention':{'scores':[1/math.sqrt(2),1/math.sqrt(2),2/math.sqrt(2)], 'weights':w,'output':out},
      'temperature':{str(t):softmax([2/t,1/t,0/t]) for t in [0.5,1,2]},
      'kv_gib':2*32*32768*8*128*2/(2**30),
      'kv_bytes_per_token':2*32*8*128*2,
      'rrf':{'A':1/61+1/63,'B':1/62+1/61,'C':1/63+1/62},
      'pass_at_2_n10_c3':1-math.comb(7,2)/math.comb(10,2),
      'binomial_100_zero_fail_lower_95_two_sided':0.025**(1/100),
      'softmax_streaming':softmax([1,2,3]),
      'bm25':{},
      'speculative':{}
    }
    N=100;df=10;k1=1.2;b=.75;avg=100
    idf=math.log(1+(N-df+.5)/(df+.5))
    for name,tf,dl in [('D1',2,100),('D2',4,400),('D3',1,50)]:
      data['bm25'][name]=idf*tf*(k1+1)/(tf+k1*(1-b+b*dl/avg))
    data['bm25']['idf']=idf
    p=[.6,.3,.1];q=[.4,.4,.2]
    accepted=[min(a,b) for a,b in zip(p,q)];r=[max(a-b,0) for a,b in zip(p,q)]
    reject=1-sum(accepted)
    data['speculative']={'p':p,'q':q,'accept_rates':[min(1,a/b) for a,b in zip(p,q)],'accepted_mass':accepted,'reject_mass':reject,'residual':[x/reject for x in r]}
    assert abs(sum(w)-1)<1e-12
    assert data['kv_gib']==4
    assert data['rrf']['B']>data['rrf']['A']>data['rrf']['C']
    assert abs(data['pass_at_2_n10_c3']-0.5333333333333333)<1e-12
    for i in range(3): assert abs(accepted[i]+reject*data['speculative']['residual'][i]-p[i])<1e-12
    data['scope']='Author-selected arithmetic verified with Python; no commercial LLM or GPU benchmark run.'
    out=Path(__file__).with_name('numeric_results.json');out.write_text(json.dumps(data,ensure_ascii=False,indent=2)); print(json.dumps(data,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
