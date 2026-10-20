"""可选对照：需要已安装PyTorch。python3 check_pytorch.py
对照真实框架算子与标准库手算，不下载模型、不调用API。
"""
import json
import torch
from verify_concepts import X,WQ,WK,WV,forward
D=torch.float64
x=torch.tensor(X,dtype=D)
b=forward()
checks={}
for name,w in [('Q',WQ),('K',WK),('V',WV)]:
    layer=torch.nn.Linear(2,2,bias=False,dtype=D)
    with torch.no_grad(): layer.weight.copy_(torch.tensor(w,dtype=D).T)
    y=layer(x)
    torch.testing.assert_close(y,torch.tensor(b[name],dtype=D),rtol=1e-12,atol=1e-12)
    checks['linear_'+name]='passed'
q,k,v=[torch.tensor(b[n],dtype=D)[None,None] for n in ['Q','K','V']]
out=torch.nn.functional.scaled_dot_product_attention(q,k,v,dropout_p=0.0,is_causal=True)
torch.testing.assert_close(out[0,0],torch.tensor(b['output'],dtype=D),rtol=1e-12,atol=1e-12)
checks['low_level_sdpa']='passed'
mha=torch.nn.MultiheadAttention(2,1,bias=False,batch_first=True,dtype=D)
with torch.no_grad():
    mha.in_proj_weight.copy_(torch.cat([torch.tensor(w,dtype=D).T for w in [WQ,WK,WV]],dim=0))
    mha.out_proj.weight.copy_(torch.eye(2,dtype=D))
blocked=torch.triu(torch.ones((2,2),dtype=torch.bool),diagonal=1)
y,a=mha(x[None],x[None],x[None],attn_mask=blocked,need_weights=True)
torch.testing.assert_close(y[0],torch.tensor(b['output'],dtype=D),rtol=1e-12,atol=1e-12)
torch.testing.assert_close(a[0],torch.tensor(b['weights'],dtype=D),rtol=1e-12,atol=1e-12)
checks['high_level_mha_same_input']='passed'
print(json.dumps({'torch_version':str(torch.__version__),'device':'CPU','dtype':'float64','checks':checks,'note':'高层MHA收到同一X，内部投影；底层SDPA收到投影后的Q/K/V。'},ensure_ascii=False,indent=2))
