---
title: "train_tiny_lm.py"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# train\_tiny\_lm.py

小型Transformer真实训练。对应第03章。依赖：PyTorch。

合成数据训练；没有通用语言能力或测试集泛化结论。[阅读运行说明](../experiments.md) / [查看实测结果](../results.md)

[原始Python文件](../../../studies/labs/train_tiny_lm.py) · 58行

```

<span id="L1"></span>
"""可选PyTorch CPU真实训练实验。仅用合成循环序列，无商业LLM/API。
<span id="L2"></span>
训练下降证明优化链路能工作，不证明自然语言泛化或真实代码能力。
<span id="L3"></span>
"""
<span id="L4"></span>
from __future__ import annotations
<span id="L5"></span>
import json,time,math
<span id="L6"></span>
from pathlib import Path
<span id="L7"></span>
 
<span id="L8"></span>
 
<span id="L9"></span>
def run(steps: int=100):
<span id="L10"></span>
    import torch
<span id="L11"></span>
    from torch import nn
<span id="L12"></span>
    import torch.nn.functional as F
<span id="L13"></span>
    torch.set_num_threads(1);torch.manual_seed(17)
<span id="L14"></span>
    vocab,width,heads,length=16,32,4,12
<span id="L15"></span>
    class Block(nn.Module):
<span id="L16"></span>
        def __init__(self):
<span id="L17"></span>
            super().__init__();self.ln1=nn.LayerNorm(width);self.ln2=nn.LayerNorm(width)
<span id="L18"></span>
            self.qkv=nn.Linear(width,width*3,bias=False);self.proj=nn.Linear(width,width,bias=False)
<span id="L19"></span>
            self.mlp=nn.Sequential(nn.Linear(width,width*2),nn.GELU(),nn.Linear(width*2,width))
<span id="L20"></span>
        def forward(self,x):
<span id="L21"></span>
            b,t,d=x.shape;q,k,v=self.qkv(self.ln1(x)).chunk(3,dim=-1)
<span id="L22"></span>
            q,k,v=[z.view(b,t,heads,d//heads).transpose(1,2) for z in (q,k,v)]
<span id="L23"></span>
            score=q@k.transpose(-1,-2)/math.sqrt(d//heads)
<span id="L24"></span>
            mask=torch.ones(t,t,dtype=torch.bool,device=x.device).tril()
<span id="L25"></span>
            a=score.masked_fill(~mask,float('-inf')).softmax(-1)@v
<span id="L26"></span>
            x=x+self.proj(a.transpose(1,2).reshape(b,t,d));return x+self.mlp(self.ln2(x))
<span id="L27"></span>
    class TinyLM(nn.Module):
<span id="L28"></span>
        def __init__(self):
<span id="L29"></span>
            super().__init__();self.emb=nn.Embedding(vocab,width);self.pos=nn.Embedding(length,width)
<span id="L30"></span>
            self.blocks=nn.Sequential(Block(),Block());self.norm=nn.LayerNorm(width);self.head=nn.Linear(width,vocab)
<span id="L31"></span>
        def forward(self,ids):
<span id="L32"></span>
            x=self.emb(ids)+self.pos(torch.arange(ids.size(1),device=ids.device))
<span id="L33"></span>
            return self.head(self.norm(self.blocks(x)))
<span id="L34"></span>
    # 同一规律的合成数据：下一个Token=(当前+1) mod 16。
<span id="L35"></span>
    seq=(torch.arange(length+1)[None,:]+torch.arange(vocab)[:,None])%vocab
<span id="L36"></span>
    x,y=seq[:,:-1],seq[:,1:];model=TinyLM();opt=torch.optim.AdamW(model.parameters(),lr=.006)
<span id="L37"></span>
    def loss():return F.cross_entropy(model(x).reshape(-1,vocab),y.reshape(-1))
<span id="L38"></span>
    before=float(loss().detach());start=time.perf_counter()
<span id="L39"></span>
    history=[]
<span id="L40"></span>
    for i in range(steps):
<span id="L41"></span>
        opt.zero_grad(set_to_none=True);l=loss();l.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.)
<span id="L42"></span>
        opt.step()
<span id="L43"></span>
        if i%20==0:history.append({'step':i,'loss':float(l.detach())})
<span id="L44"></span>
    model.eval()
<span id="L45"></span>
    with torch.no_grad():
<span id="L46"></span>
        after=float(loss());acc=float((model(x).argmax(-1)==y).float().mean())
<span id="L47"></span>
        # 改变未来Token，不得改变位置0的logits。
<span id="L48"></span>
        changed=x.clone();changed[:,5:]=(changed[:,5:]+3)%vocab
<span id="L49"></span>
        causal_error=float((model(x)[:,:5]-model(changed)[:,:5]).abs().max())
<span id="L50"></span>
    assert after<before and causal_error<1e-5
<span id="L51"></span>
    return {'kind':'真实小型模型CPU训练；合成数据；未运行商业模型或GPU吞吐基准','torch_version':torch.__version__,'parameter_count':sum(p.numel() for p in model.parameters()),'steps':steps,'initial_train_loss':before,'final_train_loss':after,'train_token_accuracy':acc,'causal_prefix_error':causal_error,'elapsed_seconds':time.perf_counter()-start,'history':history,'limitation':'测试集泛化尚未评价；高训练准确率不是通用语言理解'}
<span id="L52"></span>
 
<span id="L53"></span>
if __name__=='__main__':
<span id="L54"></span>
    import argparse
<span id="L55"></span>
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);p.add_argument('--steps',type=int,default=100);a=p.parse_args()
<span id="L56"></span>
    if not 1<=a.steps<=2000:p.error('steps必须在1..2000')
<span id="L57"></span>
    result=run(a.steps);text=json.dumps(result,ensure_ascii=False,indent=2);print(text)
<span id="L58"></span>
    if a.output:a.output.write_text(text,encoding='utf-8')
```

AI系统工程：从基础到内部  
[全书目录](../../contents.md) · [术语与符号](../../glossary.md) · [参考资料](../../sources.md)