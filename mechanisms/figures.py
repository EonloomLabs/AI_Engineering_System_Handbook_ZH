from __future__ import annotations
import math,html,re,unicodedata
from typing import Sequence
INK='#172b42'; MUTED='#4e6175'; BLUE='#245d9b'; PALE='#edf3fa'; LINE='#cad5e1'; WARN='#8c4a26'; WASH='#f7f9fc'; GREEN='#21694c'
def esc(t):return html.escape(str(t),quote=True)
def units(s):return sum(1 if unicodedata.east_asian_width(c) in 'WF' else .56 for c in str(s))
def wrap(s,width,size=17):
 lines=[]
 for part in str(s).split('\n'):
  buf='';v=0
  for c in part:
   u=1 if unicodedata.east_asian_width(c) in 'WF' else .56
   if buf and (v+u)*size>width:lines.append(buf);buf='';v=0
   buf+=c;v+=u
  lines.append(buf)
 return lines
class Canvas:
 def __init__(self,w=940,title=''):self.w=w;self.title=title;self.parts=[];self.maxy=0
 def rect(self,x,y,w,h,fill=WASH,stroke=LINE,r=4):
  self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>');self.maxy=max(self.maxy,y+h)
 def line(self,x1,y1,x2,y2,color=LINE,width=1,dash=''):
  self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>');self.maxy=max(self.maxy,y1,y2)
 def arrow(self,x1,y1,x2,y2,color=BLUE,dash=''):
  self.line(x1,y1,x2,y2,color,2,dash);a=math.atan2(y2-y1,x2-x1);pts=[(x2,y2),(x2-9*math.cos(a)-4*math.sin(a),y2-9*math.sin(a)+4*math.cos(a)),(x2-9*math.cos(a)+4*math.sin(a),y2-9*math.sin(a)-4*math.cos(a))]
  self.parts.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+f'" fill="{color}"/>')
 def text(self,x,y,s,size=17,width=None,color=INK,bold=False,anchor='start'):
  ls=wrap(s,width,size) if width else str(s).split('\n');lh=round(size*1.5,1)
  for i,l in enumerate(ls):
   yy=y+i*lh
   self.parts.append(f'<text x="{x}" y="{yy}" font-size="{size}" fill="{color}" font-weight="{650 if bold else 400}" text-anchor="{anchor}">{esc(l)}</text>')
  self.maxy=max(self.maxy,y+(len(ls)-1)*lh+6)
  return len(ls)*lh
 def badge(self,x,y,s,w=130,fill=PALE,color=BLUE):
  ls=wrap(s,w-20,16);h=18+len(ls)*24;self.rect(x,y,w,h,fill);self.text(x+10,y+26,s,16,w-20,color,True);return h
 def matrix(self,x,y,data,title='',rows=None,cols=None,cw=65,ch=42,highlight=(),formatter=str):
  if title:self.text(x,y,title,17,color=BLUE,bold=True);y+=26
  if cols:
   for j,col in enumerate(cols):self.text(x+j*cw+cw/2,y+18,col,14,anchor='middle',color=MUTED)
   y+=28
  for i,row in enumerate(data):
   if rows:self.text(x-10,y+i*ch+ch*.65,rows[i],14,anchor='end',color=MUTED)
   for j,v in enumerate(row):
    hi=(i,j) in highlight
    self.rect(x+j*cw,y+i*ch,cw,ch,PALE if hi else '#fff',LINE,0)
    self.text(x+j*cw+cw/2,y+i*ch+ch*.65,formatter(v),16,anchor='middle',bold=hi,color=BLUE if hi else INK)
  return y+len(data)*ch
 def finish(self,foot='',h=None):
  if foot:self.text(22,self.maxy+32,foot,14,self.w-44,color=MUTED)
  height=math.ceil(max(self.maxy+22,h or 0))
  return f'<svg xmlns="http://www.w3.org/2000/svg" class="mx-svg" role="img" aria-label="{esc(self.title)}" viewBox="0 0 {self.w} {height}"><title>{esc(self.title)}</title><rect x="0" y="0" width="{self.w}" height="{height}" fill="#fff"/>'+''.join(self.parts)+'</svg>'

def ledger(c,mobile=False):
 w=390 if mobile else 940;s=Canvas(w,c['title']);y=24
 # Every row is explicitly a correspondence; no invented chronological arrows across rows.
 if mobile:
  for i,row in enumerate(c['rows']):
   s.text(18,y+14,f'{i+1}. {row[0]}',17,w-36,bold=True,color=BLUE);y=s.maxy+14
   for j,v in enumerate(row[1:],1):
    label=c['cols'][j] if j<len(c['cols']) else '结果'
    s.text(22,y+15,label,13,w-44,color=MUTED);y=s.maxy+5
    s.text(22,y+17,v,17,w-44);y=s.maxy+15
   s.line(18,y,w-18,y);y+=22
 else:
  widths=[180,360,356];x=[22,206,568]
  for xx,lab,ww in zip(x,c['cols'],widths):s.text(xx,30,lab,15,ww-22,color=MUTED,bold=True)
  y=53
  for i,row in enumerate(c['rows']):
   heights=[len(wrap(v,ww-28,17))*25.5 for v,ww in zip(row,widths)];h=max(heights)+26
   s.rect(20,y,900,h,'#fff' if i%2 else WASH,'#fff',0)
   for j,(xx,v,ww) in enumerate(zip(x,row,widths)):
    s.text(xx+8,y+28,v,17,ww-28,color=BLUE if j==0 else INK,bold=j==0)
   s.line(20,y+h,920,y+h,LINE);y+=h
 return s.finish('每行是一组对应关系；独立对照不视为前一行的继续运算。')

def swim(c,mobile=False):
 # Use actual actors from arrows. Protocol messages stay attached to their actors.
 actors=[]
 for row in c['rows']:
  if '→' in row[0]:
   for a in row[0].split('→'):
    if a not in actors:actors.append(a)
 if not actors or mobile:return ledger(c,mobile)
 s=Canvas(940,c['title']);xs=[60+i*820/max(1,len(actors)-1) for i in range(len(actors))]
 for x,a in zip(xs,actors):s.text(x,28,a,16,anchor='middle',color=BLUE,bold=True)
 y=65;events=[]
 for i,row in enumerate(c['rows']):
  h=max(90,len(wrap(row[1],780,17))*26+len(wrap(row[2],780,15))*23+40)
  events.append((y,row,h));y+=h
 for x in xs:s.line(x,45,x,y-18,LINE,1,'5 5')
 for yy,row,h in events:
  if '→' in row[0]:
   a,b=row[0].split('→');x1=xs[actors.index(a)];x2=xs[actors.index(b)]
   s.arrow(x1,yy+24,x2,yy+24)
  s.rect(115,yy-6,710,h-21,'#fff','#fff')
  s.text(125,yy+17,row[1],17,690,bold=True)
  s.text(125,yy+46,row[2],15,690,color=MUTED)
  # actual connecting arrow below message avoids text crossing
  if '→' in row[0]:s.arrow(x1,yy+h-21,x2,yy+h-21)
 return s.finish('纵向为逻辑先后；间隔不表示真实耗时。箭头只连接这条消息的实际参与方。')

def matrix_pair(c,mobile=False):
 return ledger(c,mobile)

def specialized(c,mobile=False):
 k=c['id'];w=390 if mobile else 940;s=Canvas(w,c['title'])
 if k=='Q002':
  stages=[(['a','b','c'],'规则①：合并相邻 a、b'),(['ab','c'],'规则②：合并新形成的 ab、c'),(['abc'],'查固定词表'),(['ID 7'],'只剩一项；原文仍是 abc')]
  y=32
  for i,(tokens,note) in enumerate(stages):
   s.text(20,y,f'时刻 {i}',14,color=MUTED);y+=16
   for j,t in enumerate(tokens):s.badge(24+j*90,y,t,76)
   y+=70;s.text(24,y,note,16,w-48);y=s.maxy+36
   if i<3:s.arrow(52,y-22,52,y-5)
  return s.finish('方格代表当前符号项；一个格子不一定等于一个字符。')
 if k=='Q006':
  blocks=[('输入 X',[[1,0],[0,1]]),('参数 Wq',[[1,0],[1,1]]),('结果 Q',[[1,0],[1,1]]),('参数 Wk',[[1,0],[0,1]]),('结果 K',[[1,0],[0,1]]),('参数 Wv',[[2,0],[0,4]]),('结果 V',[[2,0],[0,4]])]
  if mobile:
   y=30
   for title,a in blocks:y=s.matrix(75,y,a,title,cw=110,ch=42)+35
  else:
   s.matrix(40,35,blocks[0][1],blocks[0][0],cw=70)
   for i,(pi,ri) in enumerate([(1,2),(3,4),(5,6)]):
    y=35+i*155;s.matrix(330,y,blocks[pi][1],blocks[pi][0],cw=70);s.matrix(670,y,blocks[ri][1],blocks[ri][0],cw=70)
    s.arrow(190,90,300,y+65);s.arrow(490,y+65,640,y+65)
  y=s.maxy+35;s.text(24,y,'取 Q 的第1行 [1,1]：与两个 Key 点积都为1。',17,w-48);y=s.maxy+30
  s.text(24,y,'softmax([1/√2,1/√2]) = [0.5,0.5]',18,w-48,color=BLUE,bold=True);y=s.maxy+30
  s.text(24,y,'0.5 × [2,0] + 0.5 × [0,4] = [1,2]',18,w-48,bold=True)
  return s.finish('三张W是固定参数；Q/K/V是本次输入的计算结果。输出仍是位置1的一排特征。')
 if k=='Q007':
  xs=[2,1,0];exp=[math.exp(x-2) for x in xs];p=[x/sum(exp) for x in exp]
  y=30;s.text(22,y,'候选顺序固定：A / B / C',18,bold=True);y+=28
  for title,a in [('原始logits',[xs]),('减最大值2',[[0,-1,-2]]),('取指数',[exp]),('除以指数总和1.503215',[p])]:
   y=s.matrix(28,y,a,title,cw=(w-56)/3,ch=48,formatter=lambda x:f'{x:.6f}' if isinstance(x,float) else str(x))+35
  s.text(24,y,'直接计算 exp([2,1,0]) 再归一化，得到相同概率。',17,w-48)
  return s.finish('分母是全部指数的和；不是原始分数的和。展示舍入到6位，计算用未舍入值。')
 if k=='Q009':
  s.text(20,30,'列 = Key绝对位置；行 = Query绝对位置',17,w-40,bold=True)
  cw=(w-115)/5;y=s.matrix(88,95,[[1,1,1,1,0],[1,1,1,1,1]],'正确允许表',rows=['q=3','q=4'],cols=['0','1','2','3','4'],cw=cw,ch=48,highlight=[(i,j) for i in range(2) for j in range(5) if j<=i+3])
  y=s.matrix(88,y+58,[[1,0,0,0,0],[1,1,0,0,0]],'错误的局部左上三角',rows=['q=3','q=4'],cols=['0','1','2','3','4'],cw=cw,ch=48)+35
  s.text(24,y,'当所有分数相同、V=[1,2,3,4,5]时：',16,w-48);y=s.maxy+27
  s.text(24,y,'正确平均 = [2.5, 3.0]',18,w-48,bold=True,color=BLUE);s.text(24,s.maxy+27,'错误平均 = [1.0, 1.5]',18,w-48,bold=True,color=WARN)
  return s.finish('1为逻辑允许、0为禁止；转换成布尔API掩码时，必须核对True的定义。')
 if k=='Q010':
  panels=[('位置差1：点积0',(1,0),(0,1)),('双方加1：仍点积0',(0,1),(-1,0)),('新q误归零：点积1',(1,0),(1,0))]
  for i,(lab,kp,qp) in enumerate(panels):
   cx=w/2 if mobile else 155+i*310;cy=170+i*260 if mobile else 180
   s.line(cx-90,cy,cx+100,cy,LINE);s.line(cx,cy-90,cx,cy+90,LINE)
   s.arrow(cx,cy,cx+kp[0]*72,cy-kp[1]*72,BLUE)
   s.arrow(cx+4,cy+4,cx+4+qp[0]*60,cy+4-qp[1]*60,WARN)
   s.text(cx,cy+122,lab,16,anchor='middle',bold=True)
  return s.finish('蓝色=Key，棕色=Query；二维长度不变，匹配随相对角度变化。频率90°为教学设定。')
 if k=='Q011':
  y=70
  if mobile:
   for q,g in [(0,0),(1,0),(2,1),(3,1)]:
    s.badge(20,y,f'Q{q}',80);s.arrow(100,y+24,220,y+24);s.badge(230,y,f'K{g} / V{g}',130);y+=75
  else:
   for q,g in [(0,0),(1,0),(2,1),(3,1)]:
    yy=45+q*85;s.badge(65,yy,f'Query头 {q}',150);s.arrow(220,yy+25,660,100+g*175)
   for g in range(2):s.badge(670,75+g*175,f'共享 K{g} / V{g}',205)
  return s.finish('四条Query仍分别计算份额和输出；箭头汇合代表读取同一KV组，不代表结果相同。')
 if k=='Q012':
  rows=[['上游 dO','[1,1]'],['对V0 / V1','[0.25,0.25] / [0.75,0.75]'],['对P','[2,4]'],['P加权的dP基线','0.25×2+0.75×4=3.5'],['对分数S','[-0.375,+0.375]']]
  y=26
  for label,v in rows:
   s.text(24,y+20,label,16,color=MUTED);y+=42;s.rect(24,y,w-48,55,PALE);s.text(38,y+33,v,18,w-76,bold=True);y+=90
  return s.finish('dS之和为0，反映统一平移两个分数不改变softmax。此图计算的是损失对中间量的影响。')
 if k=='Q013':
  rows=[['输入/已处理','[我,爱]','cache_len=2','选择 学习'],['下一轮处理','[学习]','cache_len=3','选择 ！'],['再下一轮处理','[！]','cache_len=4','选择 EOS'],['停止','不再处理EOS','cache_len=4','结束']]
  y=25
  for a,b,d,e in rows:
   s.text(22,y+18,a,15,color=MUTED);y+=40
   s.badge(22,y,b,w=130 if mobile else 250)
   s.arrow(160 if mobile else 290,y+22,205 if mobile else 530,y+22)
   s.badge(215 if mobile else 550,y,d,w=150 if mobile else 300)
   y+=76;s.text(24,y,e+'：新选中项尚未做自己的前向。' if e!='结束' else '宿主看到结束标记，终止后续模型计算。',16,w-48);y=s.maxy+36
  return s.finish('示意以逐Token因果解码为前提；没有把输出编号数误当成缓存已处理数。')
 if k=='Q017':
  tokens=['我','爱','学习'];targets=['爱','学习','EOS'];cw=(w-90)/3
  s.text(20,30,'输入位置与下一项标签',19,bold=True)
  y=s.matrix(65,80,[tokens,targets],rows=['输入','标签'],cw=cw,ch=58,highlight=[(1,0),(1,1),(1,2)])
  y=s.matrix(65,y+62,[[1,0,0],[1,1,0],[1,1,1]],'本次可见关系',rows=['我','爱','学习'],cols=tokens,cw=cw,ch=45,highlight=[(i,j) for i in range(3) for j in range(3) if j<=i])
  return s.finish('标签错开一项；每行只看对应前缀。图中1/0表示允许关系，不是Token编号。')
 if k in ['Q020','Q026','Q049']:
  if k=='Q020':vals=[('低精度权重',2000),('梯度',2000),('FP32主权重',4000),('Adam m/v',8000)];unit='B';den=16000
  elif k=='Q026':vals=[('第1层 K',48),('第1层 V',48),('第2层 K',48),('第2层 V',48)];unit='B';den=192
  else:vals=[('规则',20),('工具',10),('任务',10),('输出预留',20),('余量',5),('证据可用',35)];unit='单位';den=100
  y=35
  for label,v in vals:
   s.text(24,y,label,16,bold=True);y+=17
   s.rect(24,y,w-48,30,WASH);s.rect(24,y,(w-48)*v/den,30,PALE,BLUE,0)
   s.text(32,y+22,f'{v} {unit}',15);y+=65
  s.text(24,y,f'合计：{den} {unit}',20,bold=True,color=BLUE)
  return s.finish('横条长度使用共同总量作分母；没有把字节、参数个数与计算量混为同一单位。')
 if k in ['Q021','Q027']:
  return ledger(c,mobile)
 if k=='Q023':
  for i,(tok,probs) in enumerate([('A',[.6,.3,.1,0]),('B',[.1,.1,.2,.6])]):
   base=55+i*230;s.text(22,base-20,f'Token {tok} 的路由概率',18,bold=True)
   for j,v in enumerate(probs):
    x=45+j*(w-70)/4;maxh=110
    s.rect(x,base+120-v*maxh,(w-95)/4,v*maxh if v else 1,PALE,BLUE)
    s.text(x+(w-95)/8,base+148,f'E{j}: {v}',14,anchor='middle')
  return s.finish('A选E0/E1，B选E3/E2。柱高是本图给定的路由概率，不是专家输出质量。')
 if k=='Q025':
  labels=['a','b','c','d'];cw=(w-92)/4;y=70
  for layer in [1,2]:
   s.text(22,y-25,f'第{layer}层的独立缓存',18,bold=True)
   s.matrix(65,y,[['旧','旧','旧','新'],['旧','旧','旧','新']],rows=['K','V'],cols=labels,cw=cw,ch=45,highlight=[(0,3),(1,3)])
   y=s.maxy+75
  return s.finish('浅色高亮只表示本轮d新增的两组数据；每层的旧数彼此不同，不能只保留最顶层。')
 if k=='Q028':
  y=36
  for logical,physical,toks in [(0,6,'位置0、1'),(1,1,'位置2、3'),(2,9,'位置4、空位')]:
   s.badge(20,y,f'逻辑块{logical}\n{toks}',140 if mobile else 245)
   s.arrow(160 if mobile else 280,y+38,210 if mobile else 570,y+38)
   s.badge(220 if mobile else 600,y,f'物理块{physical}\n由映射表定位',150 if mobile else 260)
   y+=115
  return s.finish('物理块号不表示Token的先后。实际数据按逻辑位置恢复，不能按物理编号排序。')
 if k=='Q029':
  s.text(20,30,'两个解码槽的每步分配',19,bold=True)
  cw=(w-90)/3;s.matrix(65,95,[['A结束','C 1/2','C结束'],['B 1/3','B 2/3','B结束']],rows=['槽0','槽1'],cols=['步1','步2','步3'],cw=cw,ch=65,highlight=[(0,1),(0,2)])
  return s.finish('C已就绪，未计prefill。等宽列仅表示调度步，不表示每步实际耗时相同。')
 if k in ['Q030','Q097','Q099']:
  if k=='Q030':jobs=[('排队',0,.2),('Prefill',.2,.5),('4次Decode',.5,.7)];end=.7;unit='秒'
  elif k=='Q097':jobs=[('计划',0,2),('工具A',2,7),('工具B',2,5),('整合',7,10)];end=10;unit='秒'
  else:jobs=[('R1服务',0,1),('R2服务',1,2),('R3服务',2,3)];end=3;unit='秒'
  left=80;right=w-35;span=right-left;s.text(22,30,f'横轴：时间（{unit}）',18,bold=True)
  for i,(lab,a,b) in enumerate(jobs):
   y=85+i*87;s.text(20,y+25,lab,14,width=58)
   s.line(left,y+45,right,y+45);x=left+a/end*span;ww=(b-a)/end*span
   s.rect(x,y,ww,43,PALE,BLUE,1);s.text(x+ww/2,y+27,f'{a:g}—{b:g}',14,anchor='middle')
  s.line(left,s.maxy+28,right,s.maxy+28,INK)
  return s.finish('横条按本例给定时长等比例绘制。并行重叠区不能重复计入墙钟时间。')
 if k=='Q031':
  s.text(22,30,'从草稿分布到目标分布的概率质量',18,w-44,bold=True)
  y=80;tot=w-48
  for title,p in [('草稿 q',[.8,.2]),('直接接受质量',[.5,.2]),('拒绝补偿',[0,.3]),('最终目标 p',[.5,.5])]:
   s.text(24,y,title,17,bold=True);y+=16;x=24
   for i,v in enumerate(p):
    if v:s.rect(x,y,tot*v,42,PALE if i==0 else '#e6f1ed',BLUE if i==0 else GREEN,0);s.text(x+tot*v/2,y+27,f'{"A" if i==0 else "B"}:{v}',15,anchor='middle')
    x+=tot*v
   y+=85
  return s.finish('所有条使用同一个概率刻度0—1；中间接受总质量0.7，剩余0.3由拒绝补偿填回B。')
 if k in ['Q033','Q037','Q042'] and not mobile:return swim(c,mobile)
 if k=='Q038':
  y=35
  blocks=[('网络片段1',['E7','88'],'只够“爱”的前两个UTF-8字节'),('网络片段2',['B1'],'拼接 E7 88 B1 才解出“爱”'),('已完成一条事件',['arguments += {"path":'],'不是完整JSON对象'),('调用参数完成',['{"path":"a.py"}'],'才开始解析、类型校验与授权')]
  for lab,arr,note in blocks:
   s.text(22,y,lab,17,bold=True);y+=17
   x=24
   for t in arr:
    bw=min(w-48,max(65,units(t)*15+22));s.badge(x,y,t,bw);x+=bw+10
   y=s.maxy+25;s.text(24,y,note,16,w-48,color=MUTED);y=s.maxy+46
  return s.finish('三个边界各有缓冲规则。接收到网络chunk不构成执行授权。')
 if k=='Q051':
  cw=(w-90)/4;s.text(22,30,'每行一份完整请求，从最左侧开始比',18,w-44,bold=True)
  s.matrix(65,85,[['R1','R2','T1','U1'],['R1','R2','T1','U2'],['R1','new','T1','U2']],rows=['A','B','C'],cw=cw,ch=55,highlight=[(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0)])
  return s.finish('A/B共有连续前3项；B/C只有连续前1项。后面相同的T1不能跨过不同的new拼接前缀。')
 if k=='Q058':
  vals=[('A：长度100 / 词频2',1.375),('B：长度1000 / 词频4',8.8/13.3)];y=70
  s.text(22,30,'相同IDF下的词频—长度因子',18,w-44,bold=True)
  for lab,v in vals:
   s.text(22,y,lab,16,w-44);y=s.maxy+15
   ww=(w-48)*v/1.5;s.rect(24,y,ww,42,PALE,BLUE);s.text(34,y+28,f'{v:.6f}',17,bold=True);y+=95
  return s.finish('两条共用0—1.5刻度。图中B词频更高却因文档很长得分更低；不是BM25的全量实测。')
 if k=='Q059':
  cx=w/2;cy=190;scale=115;s.text(22,30,'同样二维，坐标意义可以不同',18,w-44,bold=True)
  s.line(cx-145,cy,cx+145,cy);s.line(cx,cy-145,cx,cy+80)
  for name,xy,col in [('q',[1,0],INK),('配套d',[.9,.1],BLUE),('换模型d',[-.1,.9],WARN)]:
   xx,yy=cx+xy[0]*scale,cy-xy[1]*scale;s.arrow(cx,cy,xx,yy,col);s.text(xx,yy+(25 if name=='q' else -18),name,15,color=col,anchor='middle')
  return s.finish('仅文档向量旋转后，查询没有同步改变。距离公式仍能运行，但原先的相关性不再由该配对保证。')
 if k=='Q061':
  if mobile:return ledger(c,mobile)
  left=['A','B','C'];right=['B','C','A'];order=['B','A','C'];score={'A':1/61+1/63,'B':1/62+1/61,'C':1/63+1/62}
  for x,title in [(30,'词法列表'),(340,'向量列表'),(650,'融合后')]:s.text(x,35,title,19,bold=True)
  for j,d in enumerate(left):s.badge(30,70+j*85,f'{j+1}. {d}',180)
  for j,d in enumerate(right):s.badge(340,70+j*85,f'{j+1}. {d}',180)
  for j,d in enumerate(order):s.badge(650,70+j*85,f'{j+1}. {d}   {score[d]:.6f}',250)
  for d in left:
   s.arrow(220,95+left.index(d)*85,325,95+right.index(d)*85,LINE)
   s.arrow(530,95+right.index(d)*85,638,95+order.index(d)*85,BLUE)
  return s.finish('连线追踪同一文档ID；融合按每路倒数排名累加，不把两个原始分数当同一尺度。')
 if k=='Q071':
  s.text(22,30,'两条时间轴，回答两类不同问题',18,w-44,bold=True)
  left=75;span=w-110
  for y,lab in [(100,'有效'),(235,'获知')]:
   s.text(18,y,lab,15,bold=True);s.line(left,y,left+span,y,INK,2)
   for d in [1,3,5,6,8]:
    x=left+(d-1)/7*span;s.line(x,y-5,x,y+5,INK);s.text(x,y+25,f'10/{d}',12,anchor='middle')
  x1=left;x5=left+4/7*span;s.rect(x1,60,x5-x1,27,PALE,BLUE);s.text(x1+4,80,'有效：1日至5日',14,color=BLUE)
  for d,t in [(3,'录入生效'),(8,'录入撤销')]:
   x=left+(d-1)/7*span;s.line(x,180,x,228,BLUE,2);s.text(x,170,t,13,anchor='middle')
  return s.finish('10/6的实际规则已失效；但系统直到10/8才得知。回放当时决策不能使用未来才取得的消息。')
 if k=='Q078':
  if mobile:
   pts={'A':(100,45),'B':(35,185),'C':(220,185),'D':(100,325)};ww=140
  else:pts={'A':(60,150),'B':(350,45),'C':(350,250),'D':(690,150)};ww=180
  labs={'A':'A 定位 · 2分钟','B':'B 实现 · 4分钟','C':'C 测试 · 3分钟','D':'D 集成 · 1分钟'}
  for a,b in [('A','B'),('A','C'),('B','D'),('C','D')]:
   x,y=pts[a];xx,yy=pts[b];s.arrow(x+ww/2,y+58,xx+ww/2,yy,BLUE if b!='C' and a!='C' else LINE) if mobile else s.arrow(x+ww,y+24,xx-10,yy+24,BLUE if b!='C' and a!='C' else LINE)
  for k,(x,y) in pts.items():s.badge(x,y,labs[k],ww)
  s.text(24,s.maxy+44,'关键路径：A → B → D = 2+4+1 = 7分钟',18,w-48,bold=True,color=BLUE)
  return s.finish('总工作量10分钟。把非关键分支C缩短，不一定改变交付完成时间；通信和集成开销尚未计入。')
 if k=='Q091':
  s.text(22,30,'20个任务，逐题对齐的二维计数',18,w-44,bold=True)
  cw=(w-120)/2;s.matrix(95,110,[[12,1],[3,4]],rows=['旧成功','旧失败'],cols=['新成功','新失败'],cw=cw,ch=75,highlight=[(0,1),(1,0)])
  s.text(24,s.maxy+40,'新改对3题，同时改错1题：净增加2/20=10个百分点。',18,w-48,bold=True)
  return s.finish('对角线两项不改变净差异；高亮的不一致对才区分两个版本。小样本不能仅凭百分比断言稳定收益。')
 if k=='Q096':
  if mobile:return ledger(c,mobile)
  pos={'D1':(30,155),'C1':(290,50),'S1':(290,250),'M1':(550,250),'缓存':(770,155)}
  for a,b in [('D1','C1'),('D1','S1'),('S1','M1'),('M1','缓存')]:
   x,y=pos[a];xx,yy=pos[b];s.arrow(x+115,y+24,xx-10,yy+24)
  for k,(x,y) in pos.items():s.badge(x,y,k+'\n撤回后核验',120,PALE if k!='D1' else '#faf1e9',BLUE if k!='D1' else WARN)
  return s.finish('箭头表示来源依赖，不是多个独立来源。D1撤回后，要沿链使受影响对象失效或重新验证。')
 if k=='Q098':
  vals=[('A：每成功任务',1.25),('B：每成功任务',1.4)];y=72
  s.text(22,30,'统一分母：完成一个成功任务',18,w-44,bold=True)
  for lab,v in vals:
   s.text(24,y,lab,17);y+=20;s.rect(24,y,(w-48)*v/1.5,43,PALE,BLUE);s.text(36,y+28,str(v),18,bold=True);y+=95
  return s.finish('A总费用100/成功80=1.25；B总费用70/成功50=1.40。失败运行的费用没有从分子删除。')
 if k=='Q105':
  y=70
  for title,v in [('自评正确率',.8),('实际核验正确率',.6)]:
   s.text(24,y,title,17,bold=True);y+=20;s.rect(24,y,w-48,43,WASH);s.rect(24,y,(w-48)*v,43,PALE,BLUE);s.text(35,y+29,f'{v*100:.0f}%',18,bold=True);y+=100
  return s.finish('同一组100条答案：声称约80%把握，实际60条正确。仅为教学样本，不是商业模型实测。')
 if k=='Q107':
  s.text(22,30,'32×32 RGB图像 → 四个16×16块',18,w-44,bold=True)
  sz=125 if mobile else 150;x=45;y=80
  for i in range(2):
   for j in range(2):
    s.rect(x+j*sz,y+i*sz,sz,sz,PALE,BLUE,0);s.text(x+j*sz+sz/2,y+i*sz+sz/2,f'Patch {i*2+j}',16,anchor='middle')
  yy=s.maxy+35;s.text(24,yy,'每块 16×16×3 = 768 个像素通道数值',18,w-48,bold=True);yy=s.maxy+35
  s.text(24,yy,'[4,768] × [768,8] → [4,8]',20,w-48,color=BLUE,bold=True)
  return s.finish('768是每块展平后的宽度；4是块数；8是教学投影宽度。图像不是靠文字Token ID查表进入模型。')
 return None

def draw_case(c,mobile=False):
 out=specialized(c,mobile)
 if out:return out
 if c['kind']=='swim':return swim(c,mobile)
 return ledger(c,mobile)

def example_relations(example,mobile=False):
 """Pure rendering of authored pre-existing table: no invented chaining or numbers."""
 w=390 if mobile else 940;s=Canvas(w,example['title']+'：操作与结果对应图')
 rows=example['rows'];selected=[]
 if not rows:return s.finish('该例未提供可绘制的状态表。')
 # select up to three meaningful correspondences without implying the rows form a linear process.
 idxs=[0]
 if len(rows)>2:
  scores=[sum(word in ' '.join(row) for word in ['错误','反例','拒绝','未知','不等','版本','改变','失败','不能','恢复','分母']) for row in rows]
  j=max(range(1,len(rows)-1),key=lambda i:scores[i]);idxs.append(j)
 if len(rows)>1:idxs.append(len(rows)-1)
 y=30
 for no,ix in enumerate(dict.fromkeys(idxs)):
  row=rows[ix];lab=row[0];action=row[1] if len(row)>1 else '';result=row[2] if len(row)>2 else ''
  s.text(22,y,lab,16,w-44,color=BLUE,bold=True);y=s.maxy+20
  if mobile:
   s.text(28,y,'操作 / 条件',13,color=MUTED);y+=26
   h=len(wrap(action,w-64,16))*24+22;s.rect(22,y-5,w-44,h,WASH);s.text(32,y+18,action,16,w-64);y+=h+22
   s.arrow(46,y-15,46,y+3);y+=28;s.text(28,y,'对应结果 / 边界',13,color=MUTED);y+=27
   h=len(wrap(result,w-64,16))*24+22;s.rect(22,y-5,w-44,h,PALE);s.text(32,y+18,result,16,w-64);y+=h+32
  else:
   h=max(len(wrap(action,370,16)),len(wrap(result,370,16)))*24+62
   s.rect(22,y,402,h,WASH);s.rect(515,y,402,h,PALE)
   s.text(36,y+24,'操作 / 条件',13,color=MUTED);s.text(529,y+24,'对应结果 / 边界',13,color=MUTED)
   s.text(36,y+53,action,16,374);s.text(529,y+53,result,16,374)
   s.arrow(440,y+h/2,498,y+h/2);y+=h+37
 return s.finish('每条横向关系只采用原算例这一行的条件与结果；上下行不暗示输入自动接续。完整表格保留在下方。')
