"""SSE增量解析与完整工具调用组装；不连接API。"""
from __future__ import annotations
import codecs,json


def parse_sse(chunks):
    decoder=codecs.getincrementaldecoder('utf-8')();buffer='';data=[]
    for raw in list(chunks)+[None]:
        buffer+=decoder.decode(b'' if raw is None else raw,final=raw is None)
        # 只在完整换行出现后处理，支持LF/CRLF，不把半个UTF-8字符当文本。
        while '\n' in buffer:
            line,buffer=buffer.split('\n',1);line=line.removesuffix('\r')
            if not line:
                if data:
                    text='\n'.join(data);data=[]
                    if text!='[DONE]':yield json.loads(text)
            elif line.startswith('data:'):
                data.append(line[5:].removeprefix(' '))
    if buffer.strip() or data:raise ValueError('流在事件边界之前结束；不能视为成功')


class Calls:
    def __init__(self):self.arguments={};self.ready={};self.failed=False;self.completed=False
    def consume(self,event):
        t=event['type'];key=event.get('item_id')
        if t=='response.function_call_arguments.delta':
            if not isinstance(event['delta'],str):raise ValueError('delta必须为字符串')
            self.arguments[key]=self.arguments.get(key,'')+event['delta']
        elif t=='response.output_item.done':
            item=event['item']
            if item.get('type')=='function_call':
                parsed=json.loads(item['arguments'])
                if not isinstance(parsed,dict):raise ValueError('工具参数必须为对象')
                call={'id':item['call_id'],'name':item['name'],'args':parsed}
                prev=self.ready.get(call['id'])
                if prev is not None and prev!=call:raise ValueError('同ID出现冲突调用')
                self.ready[call['id']]=call
        elif t in ('response.failed','response.incomplete'):self.failed=True
        elif t=='response.completed':self.completed=True
    def result(self):
        if self.failed or not self.completed:raise RuntimeError('响应没有完整成功，禁止执行')
        return list(self.ready.values())


def run():
    events=[{'type':'response.function_call_arguments.delta','item_id':'x','delta':'{"path":"中'}, {'type':'response.output_item.done','item':{'type':'function_call','call_id':'c1','name':'read_file','arguments':'{"path":"中文.py"}'}},{'type':'response.completed'}]
    raw=''.join('data: '+json.dumps(x,ensure_ascii=False)+'\r\n\r\n' for x in events).encode()
    collector=Calls()
    for e in parse_sse([raw[i:i+1] for i in range(len(raw))]):collector.consume(e)
    return {'kind':'协议字节分片实验，非真实网络请求','calls':collector.result()}
