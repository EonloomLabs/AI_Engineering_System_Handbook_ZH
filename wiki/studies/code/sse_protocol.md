---
title: "sse_protocol.py"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# sse\_protocol.py

SSE与工具参数状态。对应第07章。依赖：标准库。

协议子集；不是全部事件或生产SDK。[阅读运行说明](../experiments.md) / [查看实测结果](../results.md)

[原始Python文件](../../../studies/labs/sse_protocol.py) · 50行

```

<span id="L1"></span>
"""SSE增量解析与完整工具调用组装；不连接API。"""
<span id="L2"></span>
from __future__ import annotations
<span id="L3"></span>
import codecs,json
<span id="L4"></span>
 
<span id="L5"></span>
 
<span id="L6"></span>
def parse_sse(chunks):
<span id="L7"></span>
    decoder=codecs.getincrementaldecoder('utf-8')();buffer='';data=[]
<span id="L8"></span>
    for raw in list(chunks)+[None]:
<span id="L9"></span>
        buffer+=decoder.decode(b'' if raw is None else raw,final=raw is None)
<span id="L10"></span>
        # 只在完整换行出现后处理，支持LF/CRLF，不把半个UTF-8字符当文本。
<span id="L11"></span>
        while '\n' in buffer:
<span id="L12"></span>
            line,buffer=buffer.split('\n',1);line=line.removesuffix('\r')
<span id="L13"></span>
            if not line:
<span id="L14"></span>
                if data:
<span id="L15"></span>
                    text='\n'.join(data);data=[]
<span id="L16"></span>
                    if text!='[DONE]':yield json.loads(text)
<span id="L17"></span>
            elif line.startswith('data:'):
<span id="L18"></span>
                data.append(line[5:].removeprefix(' '))
<span id="L19"></span>
    if buffer.strip() or data:raise ValueError('流在事件边界之前结束；不能视为成功')
<span id="L20"></span>
 
<span id="L21"></span>
 
<span id="L22"></span>
class Calls:
<span id="L23"></span>
    def __init__(self):self.arguments={};self.ready={};self.failed=False;self.completed=False
<span id="L24"></span>
    def consume(self,event):
<span id="L25"></span>
        t=event['type'];key=event.get('item_id')
<span id="L26"></span>
        if t=='response.function_call_arguments.delta':
<span id="L27"></span>
            if not isinstance(event['delta'],str):raise ValueError('delta必须为字符串')
<span id="L28"></span>
            self.arguments[key]=self.arguments.get(key,'')+event['delta']
<span id="L29"></span>
        elif t=='response.output_item.done':
<span id="L30"></span>
            item=event['item']
<span id="L31"></span>
            if item.get('type')=='function_call':
<span id="L32"></span>
                parsed=json.loads(item['arguments'])
<span id="L33"></span>
                if not isinstance(parsed,dict):raise ValueError('工具参数必须为对象')
<span id="L34"></span>
                call={'id':item['call_id'],'name':item['name'],'args':parsed}
<span id="L35"></span>
                prev=self.ready.get(call['id'])
<span id="L36"></span>
                if prev is not None and prev!=call:raise ValueError('同ID出现冲突调用')
<span id="L37"></span>
                self.ready[call['id']]=call
<span id="L38"></span>
        elif t in ('response.failed','response.incomplete'):self.failed=True
<span id="L39"></span>
        elif t=='response.completed':self.completed=True
<span id="L40"></span>
    def result(self):
<span id="L41"></span>
        if self.failed or not self.completed:raise RuntimeError('响应没有完整成功，禁止执行')
<span id="L42"></span>
        return list(self.ready.values())
<span id="L43"></span>
 
<span id="L44"></span>
 
<span id="L45"></span>
def run():
<span id="L46"></span>
    events=[{'type':'response.function_call_arguments.delta','item_id':'x','delta':'{"path":"中'}, {'type':'response.output_item.done','item':{'type':'function_call','call_id':'c1','name':'read_file','arguments':'{"path":"中文.py"}'}},{'type':'response.completed'}]
<span id="L47"></span>
    raw=''.join('data: '+json.dumps(x,ensure_ascii=False)+'\r\n\r\n' for x in events).encode()
<span id="L48"></span>
    collector=Calls()
<span id="L49"></span>
    for e in parse_sse([raw[i:i+1] for i in range(len(raw))]):collector.consume(e)
<span id="L50"></span>
    return {'kind':'协议字节分片实验，非真实网络请求','calls':collector.result()}
```

AI系统工程：从基础到内部  
[全书目录](../../contents.md) · [术语与符号](../../glossary.md) · [参考资料](../../sources.md)