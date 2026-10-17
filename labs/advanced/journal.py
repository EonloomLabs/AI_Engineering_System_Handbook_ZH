"""单写者本地文件CAS与SQLite操作日志。用于解释恢复边界，不是安全沙箱。
不提供分布式exactly-once保证，不防有权限的恶意进程竞态。
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,os,sqlite3,tempfile


def digest(text: str):return hashlib.sha256(text.encode('utf-8')).hexdigest()


class Journal:
    def __init__(self,root: Path,db_path: Path):
        self.root=root.resolve();self.db=sqlite3.connect(db_path,timeout=5)
        self.db.execute('''CREATE TABLE IF NOT EXISTS operations(
            task TEXT, op TEXT, path TEXT, before_hash TEXT, after_hash TEXT,
            status TEXT, PRIMARY KEY(task,op))''')
        self.db.commit()

    def path(self,relative: str):
        p=Path(relative)
        if p.is_absolute() or '..' in p.parts:raise PermissionError('只允许工作区相对路径')
        candidate=self.root/p
        for part in [candidate,*list(candidate.parents)]:
            if part==self.root:break
            if part.is_symlink():raise PermissionError('教学实现拒绝符号链接路径')
        resolved=candidate.resolve()
        if not resolved.is_relative_to(self.root):raise PermissionError('工作区越界')
        return resolved

    def replace(self,task: str,op: str,relative: str,expected: str,new: str,*,crash=False):
        if not task or not op:raise ValueError('任务与操作ID不能为空')
        target=self.path(relative);bh,ah=digest(expected),digest(new)
        row=self.db.execute('SELECT path,before_hash,after_hash,status FROM operations WHERE task=? AND op=?',(task,op)).fetchone()
        current=target.read_text(encoding='utf-8');ch=digest(current)
        if row:
            if tuple(row[:3])!=(relative,bh,ah):raise ValueError('幂等ID复用为不同动作')
            if ch==ah:
                with self.db:self.db.execute("UPDATE operations SET status='reconciled' WHERE task=? AND op=?",(task,op))
                return {'status':'reconciled','wrote':False,'version':ah}
            if row[3] in ('applied','reconciled'):
                raise RuntimeError('操作曾完成，但文件后来变化；不能重写覆盖')
            if ch!=bh:raise RuntimeError('中断后状态不确定，需要人工或领域核对')
        else:
            if ch!=bh:raise RuntimeError('CAS前置版本已过期')
            with self.db:self.db.execute('INSERT INTO operations VALUES(?,?,?,?,?,?)',(task,op,relative,bh,ah,'started'))
        fd,name=tempfile.mkstemp(prefix='.edit-',dir=target.parent)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as f:f.write(new);f.flush();os.fsync(f.fileno())
            os.replace(name,target)
            if crash:os._exit(75)  # 故意真实终止子进程：文件已替换，但日志还没有applied。
            with self.db:self.db.execute("UPDATE operations SET status='applied' WHERE task=? AND op=?",(task,op))
            return {'status':'applied','wrote':True,'version':ah}
        finally:
            if os.path.exists(name):os.unlink(name)
    def close(self):self.db.close()


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('db',type=Path);p.add_argument('--crash',action='store_true');a=p.parse_args()
    j=Journal(a.root,a.db)
    try:print(json.dumps(j.replace('demo','op1','state.txt','old','new',crash=a.crash)))
    finally:j.close()
