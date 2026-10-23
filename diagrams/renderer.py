
"""Evidence-driven diagrams for an offline learning wiki. No network/font assets."""
from __future__ import annotations
import math, html, json, re
from PIL import ImageFont
from pathlib import Path
INK="#182632"; MUTED="#536473"; BLUE="#285D96"; TEAL="#16766B"; AMBER="#A05720"; RED="#A13A37"
LINE="#D6DFE6"; PALE="#EFF4F8"; GREENPALE="#EAF4EF"; ORANGEPALE="#FBF0E7"
import os
_font_candidates=[os.environ.get("WIKI_CJK_FONT",""),
 "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
 "/System/Library/Fonts/PingFang.ttc", "C:/Windows/Fonts/msyh.ttc"]
FONT=next((f for f in _font_candidates if f and Path(f).is_file()),None)
_fonts={}
def esc(s): return html.escape(str(s),quote=True)
def width(s,size=17):
    if FONT is None:
        # Conservative metric fallback; use WIKI_CJK_FONT for pixel-exact reproduction.
        return sum(size*(1.0 if ord(c)>255 else 0.64) for c in str(s))
    if size not in _fonts: _fonts[size]=ImageFont.truetype(FONT,size)
    return _fonts[size].getlength(str(s))
def wrap(s,limit,size=17):
    result=[]
    for line in str(s).split("\n"):
        words=re.findall(r"[A-Za-z0-9_.+-]+|.",line)
        buf=""
        for word in words:
            if buf and width(buf+word,size)>limit:result.append(buf);buf=""
            if width(word,size)>limit:
                for char in word:
                    if buf and width(buf+char,size)>limit:result.append(buf);buf=""
                    buf+=char
            else:buf+=word
        result.append(buf)
    return result
def fmt(x,n=4):
    if isinstance(x,bool):return "1" if x else "0"
    if isinstance(x,str):return x
    return str(x) if isinstance(x,int) else f"{x:.{n}f}"
class Paper:
    def __init__(self,title,w=960,h=None):
        self.title=title;self.w=w;self.h=h;self.parts=[];self.bottom=0
    def rect(self,x,y,w,h,fill="white",stroke=LINE,r=0,sw=1):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        self.bottom=max(self.bottom,y+h)
    def text(self,x,y,t,size=17,color=INK,bold=False,anchor="start",limit=None):
        ls=wrap(t,limit,size) if limit else str(t).split("\n")
        for i,l in enumerate(ls):
            yy=y+size*1.55*i
            self.parts.append(f'<text x="{x}" y="{yy}" font-size="{size}" fill="{color}" font-weight="{600 if bold else 400}" text-anchor="{anchor}">{esc(l)}</text>')
        self.bottom=max(self.bottom,y+size*1.55*(len(ls)-1)+8)
        return y+size*1.55*len(ls)
    def line(self,x1,y1,x2,y2,col=LINE,sw=1,dash=None):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
        self.bottom=max(self.bottom,y1,y2)
    def arrow(self,x1,y1,x2,y2,col=BLUE,sw=1.6,dash=None):
        self.line(x1,y1,x2,y2,col,sw,dash)
        a=math.atan2(y2-y1,x2-x1)
        pts=[(x2,y2),(x2-8*math.cos(a)+3.5*math.sin(a),y2-8*math.sin(a)-3.5*math.cos(a)),
             (x2-8*math.cos(a)-3.5*math.sin(a),y2-8*math.sin(a)+3.5*math.cos(a))]
        self.parts.append('<polygon fill="'+col+'" points="'+' '.join(f'{a:.2f},{b:.2f}' for a,b in pts)+'"/>')
    def path(self,d,col=BLUE,sw=1.6,dash=None):
        self.parts.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
    def label(self,x,y,w,t,sub="",h=68,accent=False):
        self.rect(x,y,w,h,PALE if accent else "white",BLUE if accent else LINE,r=3)
        self.text(x+14,y+26,t,17,bold=True,limit=w-28)
        if sub:self.text(x+14,y+51,sub,14,MUTED,limit=w-28)
    def matrix(self,x,y,values,label="",rows=None,cols=None,cw=78,ch=42,selected=None,precision=4):
        if label:self.text(x,y,label,17,bold=True);y+=26
        if cols:
            for j,c in enumerate(cols):self.text(x+(j+.5)*cw,y+16,c,13,MUTED,anchor="middle")
            y+=28
        for i,r in enumerate(values):
            if rows:self.text(x-14,y+i*ch+ch*.63,rows[i],14,MUTED,anchor="end")
            for j,v in enumerate(r):
                on=selected and (i,j) in selected
                self.rect(x+j*cw,y+i*ch,cw,ch,PALE if on else "white",LINE,sw=.65)
                self.text(x+(j+.5)*cw,y+i*ch+ch*.63,fmt(v,precision),15,BLUE if on else INK,bold=bool(on),anchor="middle")
        return y+len(values)*ch
    def footer(self,t):
        y=self.bottom+30
        self.line(26,y-13,self.w-26,y-13)
        self.text(26,y+10,t,14,MUTED,limit=self.w-52)
    def svg(self):
        h=self.h or math.ceil(self.bottom+26)
        return f'<svg xmlns="http://www.w3.org/2000/svg" class="d-svg" style="font-family:Noto Sans CJK SC,PingFang SC,Microsoft YaHei,sans-serif;white-space:pre" viewBox="0 0 {self.w} {h}" role="img" aria-label="{esc(self.title)}"><title>{esc(self.title)}</title><rect width="{self.w}" height="{h}" fill="white"/>'+''.join(self.parts)+'</svg>'

def embedding():
    p=Paper("编号选行；同一个位置从一个ID变成四个浮点特征")
    p.text(26,32,"两条输入，保持原来的片段顺序",20,bold=True)
    p.text(26,62,"我／爱／学习 → [1, 2, 3]       你／爱／PAD → [4, 2, 0]",17)
    E=[[0,0,0,0],[.2,-.1,.7,.4],[-.3,.8,.1,.5],[.6,.2,-.4,.9],[.1,-.5,.9,.3],[-.2,.4,.5,-.6]]
    labs=['0 · PAD','1 · 我','2 · 爱','3 · 学习','4 · 你','5 · ！']
    p.matrix(122,104,E,"参数表 E [6,4]",rows=labs,cols=["特征0","特征1","特征2","特征3"],cw=69,ch=40,selected={(2,j) for j in range(4)})
    p.text(552,106,"第一条输入的结果 [3,4]",18,bold=True)
    p.matrix(552,130,[E[i] for i in [1,2,3]],rows=['我','爱','学习'],cw=85,ch=46,selected={(1,j) for j in range(4)})
    p.text(552,318,"第二条输入的结果 [3,4]",18,bold=True)
    p.matrix(552,342,[E[i] for i in [4,2,0]],rows=['你','爱','PAD'],cw=85,ch=46,selected={(1,j) for j in range(4)})
    p.path('M400 258 H449 V199 H507');p.arrow(490,199,507,199)
    p.path('M449 258 V411 H507');p.arrow(490,411,507,411)
    p.text(427,284,"ID 2",13,BLUE)
    p.footer("两处“爱”都复制 E[2]。新增的轴是每个位置的4个特征；不是二进制位数。PAD行取零也不能替代掩码。")
    return p.svg()
def softmax():
    p=Paper("同一组分数 [2,1,0]，从计算到抽样")
    p.text(26,32,"每一列始终对应同一候选",20,bold=True)
    rows=[['原始分数',2,1,0],['减最大值2',0,-1,-2],['指数',1,math.exp(-1),math.exp(-2)],
          ['除以总和',*([math.exp(x)/sum(math.exp(z) for z in [2,1,0]) for x in [2,1,0]])]]
    y=98
    for j,t in enumerate(['计算步骤','A','B','C']):p.text([28,350,555,760][j],70,t,15,MUTED,bold=True)
    for i,row in enumerate(rows):
        p.text(28,y+26,row[0],17,bold=i==3)
        for j,x in enumerate(row[1:]):
            p.rect(295+j*205,y,180,42,PALE if i==3 else "white",LINE)
            p.text(385+j*205,y+27,fmt(x,6) if isinstance(x,float) else str(x),17,BLUE if i==3 else INK,anchor='middle')
        y+=58
    p.text(28,y+5,"指数总和 = 1 + 0.367879… + 0.135335… = 1.503215…",16,MUTED)
    prob=[math.exp(x)/sum(math.exp(z) for z in [2,1,0]) for x in [2,1,0]]
    y+=48;x=28;span=875
    for name,v,col in zip('ABC',prob,[PALE,GREENPALE,ORANGEPALE]):
        p.rect(x,y,span*v,48,col,LINE);p.text(x+span*v/2,y+30,f'{name}',18,bold=True,anchor='middle');x+=span*v
    for v in [0,prob[0],prob[0]+prob[1],1]:
        xx=28+span*v;p.line(xx,y+48,xx,y+57,INK);p.text(xx,y+78,f'{v:.6f}' if v not in [0,1] else str(v),13,MUTED,anchor='middle')
    px=28+span*.7;p.arrow(px,y-30,px,y-1,TEAL);p.text(px-6,y-40,'u=0.70 → B',16,TEAL,anchor='middle',bold=True)
    p.footer("条长与概率成比例，分界为未舍入的累计概率。argmax选A；给定抽样数0.70选择B。这不是整句答案正确率。")
    return p.svg()
def qkv(run):
    t=run['initial_trace'];pms=run['initial_parameters'];p=Paper("同一个“爱”的表示，经三张参数表变成 Q/K/V")
    b,ti=0,2;n=t['n1'][b][ti]
    p.text(26,32,"固定初始参数 θ₀ · 第0条训练序列 · t=2「爱」",19,bold=True)
    p.matrix(292,75,[n],"本次输入 n₁[0,2] [1,4]",cw=86,ch=42)
    p.path('M464 143 V179 H166 V196');p.arrow(166,184,166,196)
    p.path('M464 179 H476 V196');p.arrow(476,184,476,196)
    p.path('M464 179 H786 V196');p.arrow(786,184,786,196)
    for j,(w,key,label) in enumerate([('Wq','q','Q：参与匹配'),('Wk','k','K：被匹配'),('Wv','v','V：供混合')]):
        x=28+j*310;y=209
        p.text(x,y,label,18,bold=True,color=BLUE)
        p.matrix(x,y+30,pms[w],f'参数 {w} [4,4]',cw=69,ch=35,precision=1)
        p.arrow(x+138,y+211,x+138,y+242)
        p.matrix(x,y+275,[t[key][b][ti]],f'{key}[0,2] = n₁ @ {w}',cw=69,ch=42)
    p.footer("Q/K/V是本次算出的激活值；Wq/Wk/Wv是参数。这个阶段只混合特征；跨Token混合发生在 A @ V。数表保留4位。")
    return p.svg()
def contribution(run):
    t=run['initial_trace'];i=2;p=Paper("一个注意力行：从三个可见来源汇合为一个位置的输出")
    a=t['A'][0][i];v=t['v'][0];res=t['mix'][0][i]
    p.text(26,32,"接收位置 t=2「爱」；只允许读取 t≤2",20,bold=True)
    cols=['来源','读取份额','V的第0特征','加权贡献']
    xs=[28,250,480,715]
    for x,s in zip(xs,cols):p.text(x,80,s,15,MUTED,bold=True)
    for j,name in enumerate(['BOS','我','爱','学习','！']):
        y=105+j*58
        muted=j>2
        p.rect(26,y,890,46, "#F6F7F8" if muted else "white",LINE,sw=.6)
        for x,s in zip(xs,[f't={j} · {name}',f'{a[j]:.6f}',f'{v[j][0]:.6f}',f'{a[j]*v[j][0]:.6f}']):
            p.text(x+6,y+29,s,17,MUTED if muted else INK,bold=x==715 and not muted)
        if muted:p.text(855,y+29,'禁止',14,RED)
    y=425;p.text(28,y,"前三行的贡献相加",18,bold=True);p.arrow(310,y-5,430,y-5)
    p.text(460,y,f'mix[0,2,0] = {res[0]:.6f}',20,BLUE,bold=True)
    p.matrix(300,475,[res],"同样的份额，也分别用于其余三个特征",cw=115,ch=45)
    p.footer("份额沿“来源位置”轴归一化；V的每一列独立加权求和。不是选中一个词，也不是重新混合Key。")
    return p.svg()
def mask():
    p=Paper("有3个历史位置、2个新Query时，因果关系取决于绝对位置")
    p.text(26,32,"同一输入，对照正确与错误的允许表",20,bold=True)
    p.text(75,81,"正确：第 i 行的绝对位置是 3+i",17,BLUE,bold=True)
    p.text(545,81,"错误：把新Query当作位置0、1",17,RED,bold=True)
    for start,A in [(100,[[1,1,1,1,0],[1,1,1,1,1]]),(570,[[1,0,0,0,0],[1,1,0,0,0]])]:
        for j in range(5):p.text(start+j*60+30,122,f'k={j}',13,MUTED,anchor='middle')
        for i,row in enumerate(A):
            p.text(start-14,160+i*58,f'q={i+3}',15,MUTED,anchor='end')
            for j,val in enumerate(row):
                x,y=start+j*60,134+i*58
                p.rect(x,y,56,52,PALE if val else "#F3F4F5",LINE)
                p.text(x+28,y+33,'✓' if val else '×',21,BLUE if val else MUTED,anchor='middle')
        p.text(start,284,'V = [1,2,3,4,5]；所有可见分数相同',14,MUTED)
    p.text(110,329,'输出：[2.5, 3.0]',22,BLUE,bold=True)
    p.text(580,329,'输出：[1.0, 1.5]',22,RED,bold=True)
    p.footer("两边都能得到合法形状，却计算了不同的平均值。此图的✓表示逻辑允许；API布尔掩码的True语义需另查。")
    return p.svg()
def forward():
    p=Paper("共通前向：参数从侧面进入；残差保留并汇合原表示")
    p.text(26,32,"单层教学模型 · 两个残差汇合点必须保留",20,bold=True)
    # main operations; narrow branch and bypass room
    nodes=[
      (90,94,'E[ids] + P[pos]','X  [B,T,4]'),
      (90,214,'RMSNorm → Q/K/V','每行乘 Wq / Wk / Wv'),
      (90,334,'QKᵀ / 2 → 掩码 → softmax','得到A，再算A @ V；沿来源位置混合'),
      (90,454,'乘 Wo，再加回 X','R = X + Δattention'),
      (90,574,'RMSNorm → W1 → ReLU → W2','4维 → 8维 → 4维'),
      (90,694,'加回 R，再做 RMSNorm','H = R + ΔFFN'),
      (90,814,'乘 U','logits [B,T,8]')]
    for x,y,a,b in nodes:p.label(x,y,490,a,b,h=78)
    for i in range(len(nodes)-1):p.arrow(335,nodes[i][1]+78,335,nodes[i+1][1]-7)
    p.path('M90 133 H43 V493 H82',TEAL,2);p.arrow(60,493,82,493,TEAL)
    p.text(16,310,'X',17,TEAL,bold=True)
    p.path('M580 493 H630 V733 H588',TEAL,2);p.arrow(610,733,588,733,TEAL)
    p.text(644,618,'R',17,TEAL,bold=True)
    for y,tx in [(134,'参数：E、P'),(254,'参数：g1、Wq、Wk、Wv'),(494,'参数：Wo'),(614,'参数：g2、W1、W2'),(734,'参数：gf'),(854,'参数：U')]:
        p.text(692,y,tx,15,MUTED,limit=236)
        p.arrow(676,y+7,590,y+7,LINE)
    p.footer("箭头是数据依赖，不是耗时。训练与推理都调用 forward；损失、反向和更新不属于这个共通前向。")
    return p.svg()
def lifecycle():
    p=Paper("训练与推理共用前向，但只有训练更新参数")
    p.text(26,32,"同一个计算核心，两条不同的运行路径",20,bold=True)
    p.text(38,83,"训练：目标已知",18,bold=True);p.text(535,83,"推理：下一项未知",18,bold=True)
    p.label(38,107,365,'训练批次 + 标签','input=前5项；targets=后5项')
    p.label(535,107,365,'已有前缀','BOS + 我 + 爱')
    p.label(250,227,460,'同一个 forward(ids, cache, …)','Embedding → Attention → FFN → logits',accent=True,h=76)
    p.arrow(220,175,345,220);p.arrow(716,175,614,220)
    p.label(38,358,365,'loss → backward','产生梯度；参数仍未改变')
    p.label(535,358,365,'选择下一个Token','固定参数；不调用backward或step')
    p.arrow(350,303,220,350);p.arrow(610,303,717,350)
    p.label(38,493,365,'AdamW.step','θ₀ → θ₁；下一次重新前向')
    p.label(535,493,365,'追加Token或结束','只有未结束时才进入下一轮')
    p.arrow(220,426,220,485);p.arrow(717,426,717,485)
    p.path('M38 526 H18 V140 H30',BLUE,1.7)
    p.path('M900 526 H928 V140 H908',BLUE,1.7)
    p.arrow(18,140,30,140);p.arrow(928,140,908,140)
    p.text(260,606,'保存训练权重 → 重新加载 → 冻结使用',17,TEAL,bold=True)
    p.footer("图中两条回路分别是参数学习与逐Token生成；没有把一次训练更新画成一次推理输出。")
    return p.svg()
def train_update():
    p=Paper("参数和梯度是两份状态：只有step才改参数")
    p.text(26,32,"一次更新中，θ何时真正改变？",20,bold=True)
    xs=[28,265,488,720];head=['动作','参数 θ','梯度 .grad','本步产生或使用']
    for x,t in zip(xs,head):p.text(x,83,t,15,MUTED,bold=True)
    rows=[
     ['zero_grad','θ₀','清空/置零','清除旧梯度'],
     ['forward + loss','θ₀','尚未求出','logits、loss、激活'],
     ['backward','θ₀','∂L / ∂θ₀','沿图汇合每条梯度'],
     ['optimizer.step','θ₁','仍是旧前向的梯度','更新θ与Adam状态'],
     ['下一次 forward','使用θ₁','另行清理/累计','新激活、新损失']]
    for i,r in enumerate(rows):
        y=112+i*70;p.rect(24,y,902,59,PALE if i==3 else 'white',LINE,sw=.6)
        for j,(x,t) in enumerate(zip(xs,r)):p.text(x+7,y+34,t,16,BLUE if i==3 else INK,bold=(i==3),limit=[210,198,212,192][j])
    p.footer("有意累积微批梯度与忘记清理旧梯度不同。backward之后还没step，不能声称权重已更新。")
    return p.svg()
def residual():
    p=Paper("残差前向相加，反向在分叉处相加")
    p.text(26,32,"同一条旁路，在前向与反向中承担不同作用",20,bold=True)
    for y,title,back in [(93,'前向：y = x + f(x)',False),(330,'反向：dx = dy + df_path',True)]:
        p.text(28,y,title,18,bold=True)
        p.label(45,y+50,120,'x' if not back else 'dx',h=58)
        p.label(340,y+50,180,'f(x)' if not back else 'f的反向',h=58)
        p.label(785,y+50,120,'y' if not back else 'dy',h=58)
        if not back:
            p.arrow(165,y+79,332,y+79);p.arrow(520,y+79,777,y+79)
            p.path(f'M195 {y+79} V{y+162} H720 V{y+79}',TEAL);p.arrow(720,y+110,720,y+79,TEAL)
            p.text(425,y+153,'不经过 f 的原值旁路',15,TEAL,anchor='middle')
        else:
            p.arrow(785,y+79,528,y+79);p.arrow(340,y+79,173,y+79)
            p.path(f'M720 {y+79} V{y+162} H205 V{y+79}',TEAL);p.arrow(205,y+110,205,y+79,TEAL)
            p.text(425,y+153,'旁路直接贡献 dy，不能漏加',15,TEAL,anchor='middle')
    p.footer("共享输入x有多条到损失的路径，必须把各路径的梯度加起来；不能只沿f这一条支路回传。")
    return p.svg()
def sequence(c):
    actors=[]
    for row in c['rows']:
        if '→' in row[0]:
            for a in row[0].split('→'):
                if a not in actors:actors.append(a)
    if len(actors)<2:return None
    p=Paper(c['title']);w=p.w;xs={a:60+i*(w-120)/max(1,len(actors)-1) for i,a in enumerate(actors)}
    p.text(26,31,"消息沿参与方流转；每条箭头标注同一轮的具体对象",18,bold=True)
    top=90;y=150
    for a,x in xs.items():
        p.text(x,top,a,18,bold=True,anchor='middle')
    hrows=[]
    for i,row in enumerate(c['rows']):
        if '→' not in row[0]:continue
        a,b=row[0].split('→',1)
        note=row[1];state=row[2] if len(row)>2 else ''
        lines=wrap(note,700,16);dt=83+24*(len(lines)-1);hrows.append((i,a,b,note,state,y,dt));y+=dt
    for a,x in xs.items():p.line(x,top+19,x,y-25,LINE,1,'3 5')
    for i,a,b,note,state,yy,dt in hrows:
        x1,x2=xs[a],xs[b];cy=yy+26*(len(wrap(note,700,16))-1)
        p.rect(115,yy-25,730,28*len(wrap(note,700,16)), 'white','none')
        p.text(132,yy-4,f'{i+1:02d}  {note}',16,BLUE,limit=700)
        p.arrow(x1,cy+15,x2,cy+15,BLUE,dash='5 3' if (b in ('宿主','用户') and a in ('模型','工具','LLM','宿主')) else None)
        if state:p.text(132,cy+42,state,13,MUTED,limit=730)
    p.footer("时间自上而下；行距不代表耗时。实线是请求/动作，虚线表示图中明确的返回。来源为本节固定教学消息，不推测闭源内部。")
    return p.svg()
def ranks(c):
    p=Paper("两个排序列表怎样合并：排名贡献逐项相加")
    p.text(26,32,"RRF · k=60 · 文档身份 A/B/C 保持不变",20,bold=True)
    p.text(45,81,'词法排序',17,bold=True);p.text(400,81,'向量排序',17,bold=True);p.text(700,81,'融合分数',17,bold=True)
    left=['A','B','C'];right=['B','C','A'];cols=[BLUE,TEAL,AMBER]
    for i,a in enumerate(left):
        y=118+i*88
        p.text(40,y+22,str(i+1),14,MUTED);p.label(82,y-6,108,a,h=48)
        rank=right.index(a);yy=118+rank*88
        p.path(f'M195 {y+18} C270 {y+18} 295 {yy+18} 380 {yy+18}',cols[i],2)
    for i,a in enumerate(right):
        y=118+i*88;p.text(392,y+22,str(i+1),14,MUTED,anchor='end');p.label(397,y-6,108,a,h=48)
    vals={a:1/(60+left.index(a)+1)+1/(60+right.index(a)+1) for a in left}
    for i,a in enumerate(sorted(vals,key=vals.get,reverse=True)):
        y=118+i*88
        p.text(600,y+13,a,20,cols[left.index(a)],bold=True)
        p.text(645,y+13,f'{vals[a]:.6f}',22,bold=True)
        p.text(645,y+39,f'1/{61+left.index(a)} + 1/{61+right.index(a)}',14,MUTED)
    p.footer("曲线只连接同一文档，不表示语义相似度。B在两路都靠前，因此先于A。融合的是排名，不是混加两种原始分数。")
    return p.svg()
def cache():
    p=Paper("KV缓存按层保存已处理位置；刚选出的Token还没写入")
    p.text(26,32,"处理「学习」之前与之后，新增的只有本Token的K/V",20,bold=True)
    names=['BOS','我','爱','学习']
    for side,(x,label) in enumerate([(110,'处理前：cache_len=3'),(565,'处理后：cache_len=4')]):
        p.text(x,82,label,17,BLUE,bold=True)
        for j,t in enumerate(names):p.text(x+38+j*71,119,t,14,MUTED,anchor='middle')
        for i,t in enumerate(['本层K','本层V']):
            p.text(x-10,163+i*60,t,14,MUTED,anchor='end')
            for j in range(4):
                new=j==3;filled=side==1 or not new
                p.rect(x+j*71,138+i*60,66,49, GREENPALE if side==1 and new else PALE if filled else 'white',TEAL if side==1 and new else LINE)
                p.text(x+j*71+33,168+i*60,'新' if side==1 and new else '旧' if filled else '—',17,TEAL if side==1 and new else INK,anchor='middle')
    p.arrow(426,192,491,192);p.text(455,269,'只追加新K/V',14,BLUE,anchor='middle')
    p.label(142,330,680,'本轮 logits → 选择「！」','「！」只是候选中选出的ID；下轮输入它之后，缓存长度才变成5。',h=80,accent=True)
    p.footer("图中是单层逻辑示意；实际多层各自保留不同的K/V。不能把已输出Token数当成已经计算入缓存的位置数。")
    return p.svg()
def generation(run):
    steps=run['generation']['steps'];p=Paper("同一份已训练权重：逐轮预测、追加、停止")
    p.text(26,32,"每一轮都用 θ*；参数在推理中不改变",20,bold=True)
    cols=['轮次','本轮实际输入','缓存覆盖','新选中的Token']
    xs=[28,170,485,730]
    for x,s in zip(xs,cols):p.text(x,82,s,15,MUTED,bold=True)
    vocab=run['spec']['vocab']
    for i,st in enumerate(steps):
        y=115+i*116;p.rect(24,y,906,92,'white',LINE,sw=.6)
        parts=[('Prefill' if i==0 else f'Decode {i}'), ' / '.join(vocab[t] for t in st['input']),
               f"{st['cache_before']} → {st['cache_after']}",st['selected_text']]
        for j,(x,s) in enumerate(zip(xs,parts)):p.text(x+5,y+33,s,17,BLUE if j==3 else INK,bold=j==3,limit=[120,295,215,184][j])
        p.text(180,y+68,'新选出的项尚未做自己的前向' if st['selected_text']!='EOS' else '选到EOS，宿主结束，不再为EOS追加缓存',14,MUTED,limit=720)
    p.footer("数值与选取来自本包 run.json 的真实CPU教学实验；默认argmax。三次前向的logits与完整重算一致。")
    return p.svg()
def state_machine():
    p=Paper("超时进入unknown，恢复必须先核对副作用")
    p.text(26,32,"状态节点与转移条件分开；未知不是失败",20,bold=True)
    nodes=[(40,92,190,'recorded','操作ID已记录'),(350,92,190,'executing','动作已发出'),(675,92,225,'succeeded','有结果且已持久化'),
           (350,310,190,'unknown','未收到确定回执'),(40,512,240,'confirmed_not_done','核验确认没有发生'),
           (650,512,250,'confirmed_done','核验确认已发生')]
    for x,y,w,a,b in nodes:p.label(x,y,w,a,b,h=74,accent=a=='unknown')
    p.arrow(230,129,342,129);p.text(280,111,'派发',14,MUTED,anchor='middle')
    p.arrow(540,129,667,129);p.text(602,111,'确认结果',14,MUTED,anchor='middle')
    p.arrow(445,166,445,301,AMBER);p.text(458,240,'超时 / 连接中断',15,AMBER)
    p.arrow(391,384,216,503);p.text(165,439,'查询下游状态',14,MUTED,anchor='middle')
    p.arrow(499,384,755,503);p.text(740,439,'按操作ID核验提交证据',14,MUTED,anchor='middle')
    p.path('M40 550 H16 V129 H32');p.arrow(16,129,32,129)
    p.text(38,625,'确认未发生：按策略重试',16,BLUE,bold=True)
    p.path('M900 550 H930 V129 H908',TEAL);p.arrow(930,129,908,129,TEAL)
    p.text(650,625,'确认已发生：补记完成，勿重复执行',16,TEAL,bold=True)
    p.footer("这是教学宿主的恢复设计，不是某一API的保证。查不清时维持unknown并升级处理，不能把没有回执当作没有副作用。")
    return p.svg()
def bitemporal(c=None):
    p=Paper("有效时间与记录时间：系统何时知道，不等于事实何时生效")
    p.text(26,32,'同一事实有两条时间轴',20,bold=True)
    days=[1,3,5,6,8];left=165;span=700
    px=lambda d:left+(d-1)/7*span
    for y,lab in [(150,'有效时间'),(330,'记录时间')]:
        p.text(26,y+7,lab,18,bold=True);p.arrow(left,y,915,y,LINE)
        for d in days:
            p.line(px(d),y-6,px(d),y+6,INK)
            p.text(px(d),y+30,f'10/{d}',14,MUTED,anchor='middle')
    p.rect(px(1),106,px(5)-px(1),32,PALE,BLUE)
    p.text((px(1)+px(5))/2,96,'规则在1日至5日有效',17,BLUE,bold=True,anchor='middle')
    for d,t in [(3,'系统录入生效'),(8,'系统录入撤销')]:
        x=px(d);p.line(x,260,x,328,TEAL,2);p.text(x,246,t,16,TEAL,anchor='middle')
    p.path(f'M{px(6)} 192 V390',AMBER,1.4,'4 4')
    p.text(px(6),430,'回放10/6的决策',17,AMBER,bold=True,anchor='middle')
    p.text(80,474,'真实有效期已经结束，但系统要到10/8才知道撤销。',18,bold=True)
    p.footer("回放历史判断时同时固定“被问的时刻”和“当时已获知的资料”。不能把后来得知的信息偷放进过去的输入。")
    return p.svg()
def paired():
    p=Paper("配对评测：20个任务中，改对与改错必须同时计入")
    p.text(26,32,"同一批任务逐题对齐，不比较两个无关样本",20,bold=True)
    p.matrix(205,105,[[12,1],[3,4]],rows=['旧成功','旧失败'],cols=['新成功','新失败'],cw=225,ch=100,selected={(0,1),(1,0)})
    p.text(238,424,'3 个新修复',22,TEAL,bold=True)
    p.text(548,424,'1 个回归',22,RED,bold=True)
    p.text(238,475,'净改善 = (3−1) / 20 = 10 个百分点',21,BLUE,bold=True)
    p.footer("旧成功13/20，新成功15/20。对角线不改变净差；这20题的结果不能单凭百分比证明总体稳定收益。")
    return p.svg()

def qkv_small(c):
    p=Paper("独立二维算例：同一个X的三次投影，与最后一行的混合")
    p.text(26,32,"本图只使用该算例的 X=[[1,0],[0,1]]；不是四维训练模型",18,bold=True)
    p.matrix(364,84,[[1,0],[0,1]],'输入 X [2,2]',cw=100,ch=42)
    vals=[('Wq',[[1,0],[1,1]],'Q',[[1,0],[1,1]]),
          ('Wk',[[1,0],[0,1]],'K',[[1,0],[0,1]]),
          ('Wv',[[2,0],[0,4]],'V',[[2,0],[0,4]])]
    for j,(w,W,lab,R) in enumerate(vals):
        x=54+j*304
        p.matrix(x,259,W,w,cw=114,ch=43)
        p.arrow(x+114,378,x+114,414)
        p.matrix(x,449,R,f'{lab} = X @ {w}',cw=114,ch=43,selected={(1,0),(1,1)} if lab=='Q' else None)
        p.path(f'M464 207 V228 H{x+114} V244')
        p.arrow(x+114,232,x+114,244)
    p.text(27,610,'取 q₁=[1,1] → 点积[1,1] → softmax([1,1]/√2)=[0.5,0.5]',18,bold=True)
    p.text(27,654,'输出 = 0.5×[2,0] + 0.5×[0,4] = [1,2]',21,BLUE,bold=True)
    p.footer("右边的V才是被加权混合的内容。Q与K只用于算份额；输出仍是一排特征。")
    return p.svg()
def cache_invalid():
    p=Paper("前缀中途变化时，变化处及后缀的缓存需要重算")
    p.text(26,32,"只改位置1：我 → 你；模型参数与位置约定均保持相同",19,bold=True)
    xx=185;cw=162
    for j in range(4):p.text(xx+cw*(j+.5),92,f'位置 {j}',15,MUTED,anchor='middle')
    for i,(label,toks) in enumerate([('原输入',['BOS','我','爱','学习']),('新输入',['BOS','你','爱','学习']),('缓存判断',['可复用','重算','重算','重算'])]):
        y=118+i*106
        p.text(32,y+34,label,17,bold=True)
        for j,t in enumerate(toks):
            p.rect(xx+j*cw,y,cw-10,65,GREENPALE if i==2 and j==0 else ORANGEPALE if i==2 else PALE if i==1 and j==1 else 'white',LINE)
            p.text(xx+j*cw+(cw-10)/2,y+40,t,20,TEAL if i==2 and j==0 else AMBER if i==2 else INK,bold=i==2,anchor='middle')
    p.path('M424 290 V424 H824',AMBER,1.7);p.arrow(796,424,824,424,AMBER)
    p.text(340,470,'后面的Token虽然没改，但它们可读到的前缀变了。',18,bold=True)
    p.footer("有效复用还要求模型版本、参数、位置与计算配置匹配。不能只比较当前Token的编号。")
    return p.svg()
def backward():
    p=Paper("反向按真实依赖传递：两个残差点都要合并梯度")
    p.text(26,32,"与教学模型 manual_backward 的计算对象逐项对应",19,bold=True)
    nodes=[
      (110,94,'dz = (p − onehot) / N','输出概率与真实标签产生梯度'),
      (110,206,'dU、dfinal → 最后RMSNorm反向','得到 dhidden 与 dgf'),
      (110,318,'FFN反向：W2 → ReLU → W1','得到 dW2、dW1 与 dn2'),
      (110,430,'第二RMSNorm反向并相加','dresidual = dhidden + drnorm'),
      (110,542,'Wo反向 → A @ V 反向','得到 dWo、dA、dV'),
      (110,654,'softmax反向 → Q/K/V投影反向','得到 dWq、dWk、dWv 与 dn1'),
      (110,766,'第一RMSNorm反向并相加','dx = dresidual + dxnorm'),
      (110,878,'按Token与位置ID累计','同一个Embedding行的贡献相加')]
    for x,y,a,b in nodes:p.label(x,y,570,a,b,h=78)
    for i in range(len(nodes)-1):p.arrow(395,nodes[i][1]+78,395,nodes[i+1][1]-7)
    p.path('M680 245 H724 V469 H688',TEAL,2);p.arrow(710,469,688,469,TEAL)
    p.text(740,355,'dhidden',15,TEAL,bold=True)
    p.path('M110 469 H52 V805 H102',TEAL,2);p.arrow(73,805,102,805,TEAL)
    p.text(15,640,'dR',15,TEAL,bold=True)
    p.footer("图的旁路是必须相加的梯度贡献，不是多余装饰。反向算出梯度后，参数仍须由优化器step更新。")
    return p.svg()

def sequence_frame(c,active):
    # Same verified messages as sequence(); highlight only the observed event.
    svg=sequence(c)
    from lxml import etree as ET
    root=ET.fromstring(svg.encode());ns={'s':'http://www.w3.org/2000/svg'}
    for text in root.findall('.//s:text',ns):
        st=''.join(text.itertext())
        if re.match(r'^\d\d  ',st):
            i=int(st[:2])-1
            text.set('fill',BLUE if i==active else MUTED)
            text.set('font-weight','650' if i==active else '400')
            if i==active:
                y=float(text.get('y'))-20
                bg=ET.Element('{http://www.w3.org/2000/svg}rect',x='117',y=str(y),width='725',height='29',fill=PALE,stroke='none')
                root.insert(list(root).index(text),bg)
    return ET.tostring(root,encoding='unicode')
def message_mobile(c,active):
    row=c['rows'][active];a,b=row[0].split('→',1);p=Paper(c['title'],w=420)
    p.text(20,30,f'消息 {active+1} / {len(c["rows"])}',16,MUTED)
    p.label(20,63,150,a,h=54,accent=True);p.label(250,63,150,b,h=54)
    p.arrow(172,90,241,90)
    p.text(20,162,'传递的具体内容',15,MUTED)
    p.text(20,196,row[1],19,bold=True,limit=380)
    y=p.bottom+35;p.text(20,y,'这一步改变了什么',15,MUTED)
    p.text(20,y+34,row[2] if len(row)>2 else '',17,limit=380)
    p.footer('箭头表示本条消息方向，不表示模型直接操作文件。')
    return p.svg()
def recover_frame(index):
    p=Paper("文件已更新与宿主已确认，属于两条不同状态线")
    p.text(26,32,"固定操作 op1；版本 v7 → v8；本图展示回执丢失路径",19,bold=True)
    stages=['planned','recorded','executing','unknown','reconciled','succeeded']
    labels=['计划','记录请求','执行','结果未知','恢复核验','完成记录']
    facts=['文件仍为v7','operation_id=op1','文件已替换为v8','v8存在，但宿主没收到成功回执','按op1与内容确认v8','补记成功，不再次盲写']
    current=stages[index]
    p.text(30,88,'宿主记录',16,MUTED);p.text(490,88,'环境事实',16,MUTED)
    p.label(30,107,390,current,labels[index],h=82,accent=True)
    p.label(490,107,430,'v7' if index<2 else 'v8',facts[index],h=82)
    p.text(30,245,'状态转移：必须具备明确的观察或事件',17,bold=True)
    points=[(30,285),(345,285),(665,285),(345,438),(30,570),(665,570)]
    # recorded/executing has normal success branch; observed path chooses unknown
    pos=[points[0],points[1],points[2],points[3],points[4],points[5]]
    for i,(x,y) in enumerate(pos):
        p.label(x,y,255,stages[i],labels[i],h=64,accent=i==index)
    for i in range(2):p.arrow(pos[i][0]+255,pos[i][1]+32,pos[i+1][0]-8,pos[i+1][1]+32)
    p.path('M793 349 V470 H608',AMBER);p.arrow(645,470,608,470,AMBER)
    p.text(642,411,'连接中断',15,AMBER)
    p.arrow(363,502,224,562,TEAL);p.text(41,516,'核验版本与操作ID',14,TEAL)
    p.arrow(285,602,657,602,TEAL);p.text(472,585,'持久化完成事实',14,TEAL,anchor='middle')
    p.footer("unknown≠failed。文件替换成功与日志确认不是同一次提交；恢复不能把超时等同于“没有改过”。")
    return p.svg()
def compression_frame(index):
    p=Paper("压缩必须保留否定与未完成状态，而不只是主题词")
    p.text(26,32,"同一exclude任务：比较可恢复摘要与错误摘要",20,bold=True)
    headers=['原始约束 / 事实','可恢复摘要','错误摘要（反例）']
    xs=[28,340,650]
    for x,h in zip(xs,headers):p.text(x,86,h,17,bold=True)
    rows=[
     ['修复 exclude 行为','继续修复 exclude','重设计整个接口'],
     ['不得改公开 API','不改公开 API','可以重构 API'],
     ['单元已过；集成未运行','单元已过；集成未跑','已测试通过'],
     ['保留文件与测试证据','回查原文件与当前版本','只留一句“进展顺利”']]
    for i,r in enumerate(rows):
        y=115+i*92
        for j,(x,val) in enumerate(zip(xs,r)):
            hi=(index==1 and i==1) or (index==2 and i==2) or (index==3 and j==2) or (index==4 and i==3)
            p.rect(x-4,y,290,70,ORANGEPALE if hi and j==2 else PALE if hi else 'white',LINE)
            p.text(x+9,y+30,val,16,RED if j==2 else INK,bold=bool(hi),limit=264)
    p.footer("错误列是明确构造的反例，不是下一步执行建议。摘要是恢复入口；环境改变后仍须重新核验证据。")
    return p.svg()
def trust_frame(index):
    p=Paper("外部资料可以提供证据，但不能签发工具权限")
    p.text(26,32,"授权边界与模型阅读路径分开画",20,bold=True)
    p.rect(26,86,900,180,'#F7F9FB',LINE)
    p.text(44,114,'信息路径：外部内容进入模型',16,MUTED,bold=True)
    p.label(46,145,250,'网页 / 源码 / 工具输出','含“忽略原任务”等引用文字',h=83,accent=index<=1)
    p.label(373,145,220,'模型生成提议','可能受到内容影响',h=83,accent=index==2)
    p.arrow(296,186,365,186)
    p.label(676,145,230,'待执行动作','仍不是执行授权',h=83)
    p.arrow(593,186,668,186)
    p.rect(26,328,900,217,'white',BLUE)
    p.text(44,359,'执行边界：由宿主与工具端强制检查',16,BLUE,bold=True)
    p.label(50,390,230,'真实身份与授权','来自可信会话/配置',h=82)
    p.label(350,390,240,'检查目标、范围与批准','不接受外部文字自授权限',h=82,accent=index==3)
    p.label(690,390,212,'允许才执行','越界则拒绝',h=82,accent=index>=4)
    p.arrow(280,430,342,430);p.arrow(590,430,682,430)
    p.arrow(790,228,790,381,AMBER)
    p.text(808,306,'校验',14,AMBER)
    p.footer("提示词可降低风险，却不能替代路径、网络、身份与副作用控制。拒绝越界动作后仍可在原授权内继续任务。")
    return p.svg()

def qkv_mobile(run):
    p=Paper("Q/K/V逐路计算：同一输入，三张参数表",w=420)
    t=run['initial_trace'];pm=run['initial_parameters'];x=t['n1'][0][2]
    p.text(20,30,"θ₀ · 位置2「爱」",19,bold=True)
    y=p.matrix(32,65,[x],"共用输入 n₁[0,2]",cw=88,ch=42)
    for key,w,role in [('q','Wq','Q · 参与匹配'),('k','Wk','K · 被匹配'),('v','Wv','V · 提供内容')]:
        y+=50;p.text(20,y,role,19,BLUE,bold=True)
        y=p.matrix(32,y+33,pm[w],f"参数 {w} [4,4]",cw=88,ch=38,precision=1)
        p.arrow(208,y+12,208,y+38)
        y=p.matrix(32,y+72,[t[key][0][2]],f"n₁ @ {w} → {key}[0,2]",cw=88,ch=44)
    p.footer("三路都使用顶部同一行 n₁；参数不相同，结果也不同。这里还没有跨Token混合。")
    return p.svg().replace('font-size="15"','font-size="17"')
def embedding_mobile():
    p=Paper("沿两个句子查同一张Embedding表",w=420)
    E=[[0,0,0,0],[.2,-.1,.7,.4],[-.3,.8,.1,.5],[.6,.2,-.4,.9],[.1,-.5,.9,.3],[-.2,.4,.5,-.6]]
    p.text(20,30,"每个ID选一整行",20,bold=True)
    labs=['0 PAD','1 我','2 爱','3 学习','4 你','5 ！']
    y=p.matrix(73,67,E,"同一参数表 E [6,4]",rows=labs,cw=79,ch=40,selected={(2,j) for j in range(4)})
    y+=50;p.text(20,y,"我／爱／学习 → [1,2,3]",18,bold=True)
    y=p.matrix(73,y+30,[E[i] for i in [1,2,3]],rows=['我','爱','学习'],cw=79,ch=42,selected={(1,j) for j in range(4)})
    y+=50;p.text(20,y,"你／爱／PAD → [4,2,0]",18,bold=True)
    y=p.matrix(73,y+30,[E[i] for i in [4,2,0]],rows=['你','爱','PAD'],cw=79,ch=42,selected={(1,j) for j in range(4)})
    p.footer("两处“爱”都取E[2]，编号没有变成二进制。得到两张3×4表，整体形状[2,3,4]。")
    return p.svg().replace('font-size="15"','font-size="17"')
def softmax_mobile():
    p=Paper("Softmax与累计抽样区间",w=420)
    p.text(20,30,"固定 A/B/C 的分数 [2,1,0]",18,bold=True)
    probs=[math.exp(i)/sum(math.exp(j) for j in [2,1,0]) for i in [2,1,0]]
    labels=['分数','减2','指数','概率']
    vals=[[2,1,0],[0,-1,-2],[1,math.exp(-1),math.exp(-2)],probs]
    y=78
    for label,val in zip(labels,vals):
        p.text(18,y+26,label,17,bold=label=='概率')
        for j,n in enumerate(val):
            p.rect(76+j*107,y,103,42,PALE if label=='概率' else "white",LINE)
            p.text(127+j*107,y+27,str(n) if isinstance(n,int) else f'{n:.5f}',16,anchor='middle')
        y+=64
    p.text(20,y+15,"指数总和：1.503214…",17)
    y+=62
    cuts=[0,probs[0],sum(probs[:2]),1]
    p.text(20,y,"按累计范围定位 u=0.70",18,bold=True)
    y+=24
    for i,n in enumerate('ABC'):
        p.rect(20,y,380,51,GREENPALE if i==1 else 'white',LINE)
        p.text(32,y+32,f'{n}  [{cuts[i]:.6f}, {cuts[i+1]:.6f})',16,TEAL if i==1 else INK,bold=i==1)
        y+=60
    p.footer("0.70位于B区间；最大概率仍是A。计算用未舍入值，显示小数仅用于阅读。")
    return p.svg().replace('font-size="15"','font-size="17"')
