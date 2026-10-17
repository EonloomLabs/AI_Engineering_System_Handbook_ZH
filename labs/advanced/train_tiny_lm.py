"""可选PyTorch CPU真实训练实验。仅用合成循环序列，无商业LLM/API。
训练下降证明优化链路能工作，不证明自然语言泛化或真实代码能力。
"""
from __future__ import annotations
import json,time,math
from pathlib import Path


def run(steps: int=100):
    import torch
    from torch import nn
    import torch.nn.functional as F
    torch.set_num_threads(1);torch.manual_seed(17)
    vocab,width,heads,length=16,32,4,12
    class Block(nn.Module):
        def __init__(self):
            super().__init__();self.ln1=nn.LayerNorm(width);self.ln2=nn.LayerNorm(width)
            self.qkv=nn.Linear(width,width*3,bias=False);self.proj=nn.Linear(width,width,bias=False)
            self.mlp=nn.Sequential(nn.Linear(width,width*2),nn.GELU(),nn.Linear(width*2,width))
        def forward(self,x):
            b,t,d=x.shape;q,k,v=self.qkv(self.ln1(x)).chunk(3,dim=-1)
            q,k,v=[z.view(b,t,heads,d//heads).transpose(1,2) for z in (q,k,v)]
            score=q@k.transpose(-1,-2)/math.sqrt(d//heads)
            mask=torch.ones(t,t,dtype=torch.bool,device=x.device).tril()
            a=score.masked_fill(~mask,float('-inf')).softmax(-1)@v
            x=x+self.proj(a.transpose(1,2).reshape(b,t,d));return x+self.mlp(self.ln2(x))
    class TinyLM(nn.Module):
        def __init__(self):
            super().__init__();self.emb=nn.Embedding(vocab,width);self.pos=nn.Embedding(length,width)
            self.blocks=nn.Sequential(Block(),Block());self.norm=nn.LayerNorm(width);self.head=nn.Linear(width,vocab)
        def forward(self,ids):
            x=self.emb(ids)+self.pos(torch.arange(ids.size(1),device=ids.device))
            return self.head(self.norm(self.blocks(x)))
    # 同一规律的合成数据：下一个Token=(当前+1) mod 16。
    seq=(torch.arange(length+1)[None,:]+torch.arange(vocab)[:,None])%vocab
    x,y=seq[:,:-1],seq[:,1:];model=TinyLM();opt=torch.optim.AdamW(model.parameters(),lr=.006)
    def loss():return F.cross_entropy(model(x).reshape(-1,vocab),y.reshape(-1))
    before=float(loss().detach());start=time.perf_counter()
    history=[]
    for i in range(steps):
        opt.zero_grad(set_to_none=True);l=loss();l.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.)
        opt.step()
        if i%20==0:history.append({'step':i,'loss':float(l.detach())})
    model.eval()
    with torch.no_grad():
        after=float(loss());acc=float((model(x).argmax(-1)==y).float().mean())
        # 改变未来Token，不得改变位置0的logits。
        changed=x.clone();changed[:,5:]=(changed[:,5:]+3)%vocab
        causal_error=float((model(x)[:,:5]-model(changed)[:,:5]).abs().max())
    assert after<before and causal_error<1e-5
    return {'kind':'真实小型模型CPU训练；合成数据；未运行商业模型或GPU吞吐基准','torch_version':torch.__version__,'parameter_count':sum(p.numel() for p in model.parameters()),'steps':steps,'initial_train_loss':before,'final_train_loss':after,'train_token_accuracy':acc,'causal_prefix_error':causal_error,'elapsed_seconds':time.perf_counter()-start,'history':history,'limitation':'测试集泛化尚未评价；高训练准确率不是通用语言理解'}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);p.add_argument('--steps',type=int,default=100);a=p.parse_args()
    if not 1<=a.steps<=2000:p.error('steps必须在1..2000')
    result=run(a.steps);text=json.dumps(result,ensure_ascii=False,indent=2);print(text)
    if a.output:a.output.write_text(text,encoding='utf-8')
