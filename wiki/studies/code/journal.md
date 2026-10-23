---
title: "journal.py"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# journal.py

操作日志与真实崩溃恢复。对应第08、20、21章。依赖：标准库/SQLite。

单写者局部恢复；不是防恶意竞态的完整安全沙箱。[阅读运行说明](../experiments.md) / [查看实测结果](../results.md)

[原始Python文件](../../../studies/labs/journal.py) · 64行

```

<span id="L1"></span>
"""单写者本地文件CAS与SQLite操作日志。用于解释恢复边界，不是安全沙箱。
<span id="L2"></span>
不提供分布式exactly-once保证，不防有权限的恶意进程竞态。
<span id="L3"></span>
"""
<span id="L4"></span>
from __future__ import annotations
<span id="L5"></span>
from pathlib import Path
<span id="L6"></span>
import hashlib,json,os,sqlite3,tempfile
<span id="L7"></span>
 
<span id="L8"></span>
 
<span id="L9"></span>
def digest(text: str):return hashlib.sha256(text.encode('utf-8')).hexdigest()
<span id="L10"></span>
 
<span id="L11"></span>
 
<span id="L12"></span>
class Journal:
<span id="L13"></span>
    def __init__(self,root: Path,db_path: Path):
<span id="L14"></span>
        self.root=root.resolve();self.db=sqlite3.connect(db_path,timeout=5)
<span id="L15"></span>
        self.db.execute('''CREATE TABLE IF NOT EXISTS operations(
<span id="L16"></span>
            task TEXT, op TEXT, path TEXT, before_hash TEXT, after_hash TEXT,
<span id="L17"></span>
            status TEXT, PRIMARY KEY(task,op))''')
<span id="L18"></span>
        self.db.commit()
<span id="L19"></span>
 
<span id="L20"></span>
    def path(self,relative: str):
<span id="L21"></span>
        p=Path(relative)
<span id="L22"></span>
        if p.is_absolute() or '..' in p.parts:raise PermissionError('只允许工作区相对路径')
<span id="L23"></span>
        candidate=self.root/p
<span id="L24"></span>
        for part in [candidate,*list(candidate.parents)]:
<span id="L25"></span>
            if part==self.root:break
<span id="L26"></span>
            if part.is_symlink():raise PermissionError('教学实现拒绝符号链接路径')
<span id="L27"></span>
        resolved=candidate.resolve()
<span id="L28"></span>
        if not resolved.is_relative_to(self.root):raise PermissionError('工作区越界')
<span id="L29"></span>
        return resolved
<span id="L30"></span>
 
<span id="L31"></span>
    def replace(self,task: str,op: str,relative: str,expected: str,new: str,*,crash=False):
<span id="L32"></span>
        if not task or not op:raise ValueError('任务与操作ID不能为空')
<span id="L33"></span>
        target=self.path(relative);bh,ah=digest(expected),digest(new)
<span id="L34"></span>
        row=self.db.execute('SELECT path,before_hash,after_hash,status FROM operations WHERE task=? AND op=?',(task,op)).fetchone()
<span id="L35"></span>
        current=target.read_text(encoding='utf-8');ch=digest(current)
<span id="L36"></span>
        if row:
<span id="L37"></span>
            if tuple(row[:3])!=(relative,bh,ah):raise ValueError('幂等ID复用为不同动作')
<span id="L38"></span>
            if ch==ah:
<span id="L39"></span>
                with self.db:self.db.execute("UPDATE operations SET status='reconciled' WHERE task=? AND op=?",(task,op))
<span id="L40"></span>
                return {'status':'reconciled','wrote':False,'version':ah}
<span id="L41"></span>
            if row[3] in ('applied','reconciled'):
<span id="L42"></span>
                raise RuntimeError('操作曾完成，但文件后来变化；不能重写覆盖')
<span id="L43"></span>
            if ch!=bh:raise RuntimeError('中断后状态不确定，需要人工或领域核对')
<span id="L44"></span>
        else:
<span id="L45"></span>
            if ch!=bh:raise RuntimeError('CAS前置版本已过期')
<span id="L46"></span>
            with self.db:self.db.execute('INSERT INTO operations VALUES(?,?,?,?,?,?)',(task,op,relative,bh,ah,'started'))
<span id="L47"></span>
        fd,name=tempfile.mkstemp(prefix='.edit-',dir=target.parent)
<span id="L48"></span>
        try:
<span id="L49"></span>
            with os.fdopen(fd,'w',encoding='utf-8') as f:f.write(new);f.flush();os.fsync(f.fileno())
<span id="L50"></span>
            os.replace(name,target)
<span id="L51"></span>
            if crash:os._exit(75)  # 故意真实终止子进程：文件已替换，但日志还没有applied。
<span id="L52"></span>
            with self.db:self.db.execute("UPDATE operations SET status='applied' WHERE task=? AND op=?",(task,op))
<span id="L53"></span>
            return {'status':'applied','wrote':True,'version':ah}
<span id="L54"></span>
        finally:
<span id="L55"></span>
            if os.path.exists(name):os.unlink(name)
<span id="L56"></span>
    def close(self):self.db.close()
<span id="L57"></span>
 
<span id="L58"></span>
 
<span id="L59"></span>
if __name__=='__main__':
<span id="L60"></span>
    import argparse
<span id="L61"></span>
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('db',type=Path);p.add_argument('--crash',action='store_true');a=p.parse_args()
<span id="L62"></span>
    j=Journal(a.root,a.db)
<span id="L63"></span>
    try:print(json.dumps(j.replace('demo','op1','state.txt','old','new',crash=a.crash)))
<span id="L64"></span>
    finally:j.close()
```

AI系统工程：从基础到内部  
[全书目录](../../contents.md) · [术语与符号](../../glossary.md) · [参考资料](../../sources.md)