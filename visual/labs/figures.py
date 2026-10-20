"""Inspectable SVG primitives for the textbook. No external rendering dependencies."""
from __future__ import annotations
from html import escape as e
import math,textwrap
TEAL='#166c69';INK='#203344';GRAY='#61727d';BORDER='#cbdad7';PALE='#eff7f4';AMBER='#9c5818';RED='#a83536';BLUE='#365f9b'

def fmt(v):
 if isinstance(v,bool):return str(int(v))
 if isinstance(v,(int,float)):
  if abs(v-round(v))<1e-10:return str(round(v))
  return f'{v:.4f}'.rstrip('0').rstrip('.')
 return str(v)

def text(x,y,s,size=17,fill=INK,anchor='start',weight='400'):
 return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{fill}" font-weight="{weight}">{e(str(s))}</text>'

def wrap_lines(s,limit=24):
 # Chinese about two latin character widths. Respect explicit newlines.
 out=[]
 for line in str(s).split('\n'):
  row='';n=0
  for c in line:
   k=2 if ord(c)>127 else 1
   if n+k>limit and row:out.append(row);row='';n=0
   row+=c;n+=k
  out.append(row)
 return out

def para(x,y,s,width=230,size=16,line=25,fill=GRAY,max_lines=8):
 return ''.join(text(x,y+i*line,l,size,fill) for i,l in enumerate(wrap_lines(s,max(8,int(width/(size*.52))))[:max_lines]))

def rect(x,y,w,h,fill=PALE,stroke=BORDER,r=10,sw=1.2):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def card(x,y,w,h,title,detail='',active=False,warning=False):
 col=RED if warning else TEAL
 titlelines=wrap_lines(title,max(8,int((w-28)/(17*.54))))
 ts=''.join(text(x+14,y+27+i*22,t,17,col if active or warning else INK,weight='650') for i,t in enumerate(titlelines[:2]))
 start=49+(min(2,len(titlelines))-1)*22
 return rect(x,y,w,h,'#fff5ed' if warning else PALE,col if active or warning else BORDER,10,2.5 if active else 1.2)+ts+para(x+14,y+start,detail,w-28,15,22,max_lines=max(1,int((h-start+8)/22)))

def line(x1,y1,x2,y2,fill=TEAL,dash='',width=2):
 return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{fill}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'

def arrow(x1,y1,x2,y2,fill=TEAL):
 # Marker-free polygon avoids ID collisions across combined single-file pages.
 a=math.atan2(y2-y1,x2-x1);d=10;w=4
 p=[(x2,y2),(x2-d*math.cos(a)+w*math.sin(a),y2-d*math.sin(a)-w*math.cos(a)),(x2-d*math.cos(a)-w*math.sin(a),y2-d*math.sin(a)+w*math.cos(a))]
 return line(x1,y1,x2,y2,fill)+f'<polygon points="'+ ' '.join(f'{x:.2f},{y:.2f}' for x,y in p)+f'" fill="{fill}"/>'

def svg(body,title='',w=820,h=410):
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{e(title,quote=True)}" class="vb-svg">'+f'<title>{e(title)}</title><rect width="{w}" height="{h}" rx="10" fill="#fcfdfc"/>'+body+'</svg>'

def tokens(labels,x=30,y=60,width=94,active=None,muted=None,sub=None):
 out=''
 for i,s in enumerate(labels):
  xx=x+i*(width+9);out+=rect(xx,y,width,49,'#d9eee7' if i==active else ('#f4f1ef' if i in (muted or []) else '#fff'), TEAL if i==active else BORDER)
  out+=text(xx+width/2,y+30,s,18,TEAL if i==active else INK,'middle','650' if i==active else '400')
  if sub and i<len(sub):out+=text(xx+width/2,y+71,sub[i],13,GRAY,'middle')
 return out

def matrix(a,x=30,y=70,cw=68,ch=40,name='',rowlabels=None,collabels=None,highlight=None,colors=None):
 out=text(x,y-(29 if collabels else 15),name,17,TEAL,weight='650') if name else ''
 if collabels:
  for j,s in enumerate(collabels):out+=text(x+j*cw+cw/2,y-3,s,12,GRAY,'middle')
 for i,row in enumerate(a):
  if rowlabels:out+=text(x-8,y+i*ch+ch*.65,rowlabels[i],14,GRAY,'end')
  for j,v in enumerate(row):
   fill=(colors or {}).get((i,j),'#daf0e8' if (i,j) in (highlight or []) else '#fff')
   out+=rect(x+j*cw,y+i*ch,cw-3,ch-3,fill,TEAL if (i,j) in (highlight or []) else BORDER,5)
   label=fmt(v); units=sum(2 if ord(c)>127 else 1 for c in label)
   size=min(15, max(12,(cw-10)/max(1,units*.55)))
   ls=wrap_lines(label,max(4,int((cw-10)/(size*.55))))
   for li,l in enumerate(ls[:3]):out+=text(x+j*cw+(cw-3)/2,y+i*ch+ch/2+(li-(min(3,len(ls))-1)/2)*17+5,l,size,INK,'middle')
 return out

def bars(labels,values,x=35,y=65,width=520,height=36,gap=21,maxval=None,percent=False,selected=None):
 out='';m=maxval or max(max(values),1e-9)
 labelw=min(240,max(90,max(sum(2 if ord(c)>127 else 1 for c in str(l)) for l in labels)*8+10))
 width=min(width,820-x-labelw-90)
 for i,(lab,v) in enumerate(zip(labels,values)):
  yy=y+i*(height+gap);out+=para(x,yy+height*.6,lab,labelw-10,16,19,max_lines=2)
  start=x+labelw
  out+=rect(start,yy,width,height,'#edf1ef','#edf1ef',6)
  out+=rect(start,yy,max(.4,width*max(0,v)/m),height,TEAL if i==selected else '#78afa0','none',6)
  s=f'{v*100:.2f}%' if percent else fmt(v)
  out+=text(start+width+12,yy+height*.65,s,16,TEAL if i==selected else INK)
 return out

def pipeline(nodes,active=0,title='',foot='',warn=None):
 body=''
 n=len(nodes);cols=3;w=238;h=118;x0=26;y0=38
 for i,(t,d) in enumerate(nodes):
  row=i//cols;col=i%cols;xx=x0+col*(w+26);yy=y0+row*160
  body+=card(xx,yy,w,h,t,d,i==active,i==warn)
  if col<cols-1 and i<n-1:body+=arrow(xx+w+2,yy+h/2,xx+w+22,yy+h/2,TEAL if i<active else BORDER)
  if col==cols-1 and i<n-1:
   body+=line(xx+w/2,yy+h+3,xx+w/2,yy+h+21,BORDER)+line(x0+w/2,yy+h+21,xx+w/2,yy+h+21,BORDER)+arrow(x0+w/2,yy+h+21,x0+w/2,yy+160-3,BORDER)
 H=y0+math.ceil(n/cols)*160+38
 if foot:body+=para(30,H-40,foot,750,16,22,max_lines=2)
 return svg(body,title,h=H)

def timeline(rows,title='',active=-1):
 body=line(56,46,56,45+len(rows)*69,BORDER, width=3)
 for i,(label,event) in enumerate(rows):
  yy=47+i*69;col=TEAL if i==active else GRAY
  body+=f'<circle cx="56" cy="{yy}" r="{10 if i==active else 6}" fill="{col}"/>'
  body+=text(78,yy+6,label,17,col,weight='650')+para(280,yy+5,event,490,16,22,max_lines=2)
 return svg(body,title,h=80+len(rows)*69)

def swim(lanes,events,active=0,title=''):
 w=740/len(lanes);body=''
 for i,l in enumerate(lanes):
  xx=40+i*w;body+=rect(xx,18,w-8,40,PALE,BORDER,8)+text(xx+(w-8)/2,44,l,17,TEAL,'middle')+line(xx+w/2,62,xx+w/2,78+len(events)*60,BORDER,'4 4')
 for k,(src,dst,lab) in enumerate(events):
  yy=92+k*60;x1=40+src*w+w/2;x2=40+dst*w+w/2;col=TEAL if k==active else '#97aaa5'
  if src!=dst:body+=arrow(x1,yy,x2,yy,col)
  else:body+=line(x1,yy,x1+42,yy,col)+line(x1+42,yy,x1+42,yy+20,col)+arrow(x1+42,yy+20,x1,yy+20,col)
  body+=text(410,yy-11,lab,15,col,'middle','650' if k==active else '400')
 return svg(body,title,h=115+len(events)*60)

def graph_nodes(nodes,edges,highlight=None,title='',h=390):
 body=''
 for a,b,lab in edges:
  xa,ya,wa,ha,_,_=nodes[a];xb,yb,wb,hb,_,_=nodes[b]
  if abs(ya-yb)<30:body+=arrow(xa+wa,ya+ha/2,xb,yb+hb/2)
  else:body+=arrow(xa+wa/2,ya+ha,xb+wb/2,yb)
  if lab:body+=text((xa+wa+xb)/2,(ya+ha/2+yb+hb/2)/2-8,lab,13,GRAY,'middle')
 for k,(x,y,w,hh,t,d) in enumerate(nodes):body+=card(x,y,w,hh,t,d,k==highlight)
 return svg(body,title,h=h)
