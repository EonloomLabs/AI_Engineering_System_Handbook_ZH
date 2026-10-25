"""Loopback-only protocol fixture. It performs NO neural-model inference.
Use this to debug HTTP integration; supply a real local engine for the model-serving assignment.
"""
from __future__ import annotations
from contextlib import contextmanager
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import json,threading
from core import ScriptedBackend,dump

@contextmanager
def fixture_server():
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def respond(self,status,data):
            raw=dump(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            if self.path=='/health':self.respond(200,{'backend':'scripted-protocol-fixture','model_weights_loaded':False})
            else:self.respond(404,{'error':'unknown_route'})
        def do_POST(self):
            if self.path!='/v1/chat/completions':self.respond(404,{'error':'unknown_route'});return
            if self.headers.get('Authorization')!='Bearer local-fixture-key':self.respond(401,{'error':'unauthorized'});return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=1_000_000:raise ValueError('request_size')
                obj=json.loads(self.rfile.read(length))
                if obj.get('model')!='scripted-protocol-fixture':self.respond(400,{'error':'unknown_fixture_model'});return
                r=ScriptedBackend().complete(obj['messages'],obj.get('tools',[]))
                self.respond(200,{'id':'local-fixture','object':'chat.completion','model':'scripted-protocol-fixture','choices':[{'index':0,'message':r['message'],'finish_reason':'tool_calls' if r['message'].get('tool_calls') else 'stop'}], 'usage':None, 'fixture':True})
            except Exception as e:self.respond(400,{'error':type(e).__name__})
    srv=ThreadingHTTPServer(('127.0.0.1',0),Handler);srv.daemon_threads=True
    worker=threading.Thread(target=srv.serve_forever,daemon=True);worker.start()
    try:yield f'http://127.0.0.1:{srv.server_port}/v1'
    finally:srv.shutdown();srv.server_close();worker.join(timeout=2)
