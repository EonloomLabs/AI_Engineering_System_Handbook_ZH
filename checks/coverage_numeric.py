"""Recompute new teaching examples with Python's standard library only.

These are arithmetic witnesses, not GPU/model-training benchmarks.
Run: python checks/coverage_numeric.py
"""
import math,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
rows=[]
def close(a,b):
    if isinstance(a,(list,tuple)):return len(a)==len(b) and all(close(x,y) for x,y in zip(a,b))
    return math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10)
def check(name,actual,expected):
    passed=close(actual,expected);rows.append({'example':name,'actual':actual,'expected':expected,'passed':passed})
def rowmul(x,W):return [sum(x[i]*W[i][j] for i in range(len(x))) for j in range(len(W[0]))]
def colmul(W,x):return [sum(a*b for a,b in zip(row,x)) for row in W]
def softmax(z):
    v=[math.exp(x-max(z)) for x in z];return [x/sum(v) for x in v]
check('GPU vector add',[a+b for a,b in zip(range(1,7),range(10,70,10))],[11,22,33,44,55,66])
check('warps in 256-thread CUDA block',256/32,8)
# Independent loop-based access accounting for the specified 4x4, tile=2 model.
naive=0;tiled=0
for i in range(4):
 for j in range(4):
  for k in range(4):naive+=2
for i in range(0,4,2):
 for j in range(0,4,2):
  for k in range(0,4,2):tiled+=2*2+2*2
check('matrix operand reads',[naive,tiled],[128,64])
check('matrix read/write bytes',[(naive+16)*4,(tiled+16)*4],[576,320])
check('tiled arithmetic intensity',128/320,0.4)
check('fusion bytes and reduction',[5*4,3*4,(5-3)/5],[20,12,0.4])
check('replica route TTFT',[100+(1000-800)/10+30,10+1000/10+10,10+(1000-800)/10+30],[150,120,60])
check('compile break-even',math.floor(2000/(8-5))+1,667)
check('compile total costs',[400*8,2000+400*5,1000*8,2000+1000*5],[3200,4000,8000,7000])
W=[[1,0.01,2,0.02],[0.03,3,0.04,4]];Wp=[[v if abs(v)>=.05 else 0 for v in row] for row in W]
check('pruning original output',rowmul([1,2],W),[1.06,6.01,2.08,8.02])
check('pruning new output',rowmul([1,2],Wp),[1,6,2,8])
check('pruning representations',[8*4,4*4+4*2*4,2*4+4*2,2*3+3*2],[32,48,16,12])
check('edited outputs',[colmul([[1,0],[1,1]],x) for x in [[1,0],[0,1],[1,1]]],[[1,1],[0,1],[1,2]])
check('editing evaluation fractions',[1/1,3/4,9/10,1/2,18/20],[1,.75,.9,.5,.9])
p=[.8,.2];q=[.6,.4];ce=-sum(a*math.log(b) for a,b in zip(p,q));entropy=-sum(a*math.log(a) for a in p)
check('distillation CE entropy KL',[ce,entropy,ce-entropy],[.5919186453876236,.5004024235381879,.09151622184943575])
pt=softmax([math.log(4)/2,0]);qt=softmax([math.log(1.5)/2,0]);kl=sum(a*math.log(a/b) for a,b in zip(pt,qt))
check('distillation temperature 2 teacher',pt,[2/3,1/3])
check('distillation temperature 2 student',qt,[.5505102572168219,.4494897427831781])
check('distillation scaled KL',[kl,4*kl],[.02797304016974847,.11189216067899388])
check('watermark probabilities',softmax([math.log(2),0,math.log(2),0]),[1/3,1/6,1/3,1/6])
check('watermark z-score',(70-100*.5)/math.sqrt(100*.5*.5),4)
P=[[1,0,0,1],[0,1,0,1],[0,0,1,1]]
check('visual connector output',rowmul([1,2,3],P),[1,2,3,6])
check('multimodal positions and width',[4+2,len(P[0])],[6,4])
check('answer CE',-math.log(.2),1.6094379124341003)
xt=math.sqrt(.64)*2+math.sqrt(1-.64)*1
check('diffusion forward',xt,2.2)
check('diffusion x0 estimates',[(xt-math.sqrt(1-.64)*v)/math.sqrt(.64) for v in [1,.5]],[2,2.375])
check('diffusion error',(.5-1)**2,.25)
result={'scope':'new independent teaching examples; no GPU or model training','checks':len(rows),'passed':sum(x['passed'] for x in rows),'results':rows}
(R/'checks/coverage_numeric_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='results'},ensure_ascii=False))
raise SystemExit(any(not x['passed'] for x in rows))
