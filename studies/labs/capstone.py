"""贯穿项目：受限工具修复真实临时仓库中的exclude错误。
默认提供者是确定性脚本，不是LLM。真实文件、补丁、子进程测试和验证新鲜度。
"""
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
import tempfile,subprocess,sys,json,difflib
from journal import Journal,digest
from retrieval import symbols

BUGGY='''from pathlib import PurePosixPath

def should_exclude(path, patterns):
    # 契约：路径相对仓库根；末尾/代表目录及后代；其他项精确匹配。
    # 历史错误：只比较basename，导致nested路径失配，也误排除同名文件。
    path = PurePosixPath(path).name
    return path in patterns
'''
FIXED='''from pathlib import PurePosixPath

def should_exclude(path, patterns):
    if not isinstance(path, str) or not all(isinstance(p, str) for p in patterns):
        raise TypeError("path和patterns必须是字符串")
    normalized = path.replace("\\\\", "/")
    parts = PurePosixPath(normalized).parts
    if PurePosixPath(normalized).is_absolute() or ".." in parts:
        raise ValueError("只支持仓库相对路径，拒绝父级跳转")
    value = str(PurePosixPath(normalized))
    for pattern in patterns:
        rule = pattern.replace("\\\\", "/")
        rule_parts = PurePosixPath(rule).parts
        if PurePosixPath(rule).is_absolute() or ".." in rule_parts:
            raise ValueError("排除规则不能越界")
        if rule.endswith("/"):
            prefix = str(PurePosixPath(rule))
            if value == prefix or value.startswith(prefix + "/"):
                return True
        elif value == str(PurePosixPath(rule)):
            return True
    return False
'''
TESTS='''import unittest
from matcher import should_exclude as f
class MatchingTests(unittest.TestCase):
    def test_top(self): self.assertTrue(f("a.py",["a.py"]))
    def test_nested(self): self.assertTrue(f("src/a.py",["src/a.py"]))
    def test_same_name(self): self.assertFalse(f("src/a.py",["a.py"]))
    def test_directory(self): self.assertTrue(f("vendor/a.py",["vendor/"]))
    def test_directory_boundary(self): self.assertFalse(f("vendor2/a.py",["vendor/"]))
    def test_windows(self): self.assertTrue(f("src\\\\a.py",["src/a.py"]))
    def test_empty(self): self.assertFalse(f("a.py",[]))
    def test_parent(self):
        with self.assertRaises(ValueError): f("../a.py",["a.py"])
if __name__=="__main__": unittest.main()
'''

@dataclass(frozen=True)
class Call:
    id: str
    name: str
    args: dict


class Harness:
    def __init__(self,root: Path):
        self.root=root;self.journal=Journal(root,root/'operations.sqlite');self.trace=[];self.validation=None
    def execute(self,call: Call):
        # 仅示例工作区。生产验证器应独立于模型可写工作区。
        if call.name=='read':
            if set(call.args)!={'path'}:raise ValueError('read参数无效')
            p=self.journal.path(call.args['path'])
            if p.suffix!='.py':raise PermissionError('只读示例源码')
            result={'text':p.read_text(),'version':digest(p.read_text())}
        elif call.name=='replace':
            if set(call.args)!={'expected','new'}:raise ValueError('replace参数无效')
            result=self.journal.replace('exclude',call.id,'matcher.py',call.args['expected'],call.args['new']);self.validation=None
        elif call.name=='test':
            if call.args:raise ValueError('test不接受模型命令')
            before=digest((self.root/'matcher.py').read_text())
            proc=subprocess.run([sys.executable,'-I','-c',"import runpy,sys;sys.path.insert(0,'.');runpy.run_path('test_matcher.py',run_name='__main__')"],cwd=self.root,capture_output=True,text=True,timeout=10)
            after=digest((self.root/'matcher.py').read_text())
            self.validation={'version':before,'passed':proc.returncode==0 and before==after,'exit_code':proc.returncode}
            result={**self.validation,'log':(proc.stdout+proc.stderr)[-5000:]}
        else:raise PermissionError('工具不在白名单')
        self.trace.append({'call':{'id':call.id,'name':call.name,'args':{k:('[源码内容]' if k in ('new','expected') else v) for k,v in call.args.items()}},'result':result})
        return result
    def finish(self):
        current=digest((self.root/'matcher.py').read_text())
        return bool(self.validation and self.validation['passed'] and self.validation['version']==current)
    def close(self):self.journal.close()


def create_fixture(root: Path):
    root.mkdir(parents=True,exist_ok=True)
    (root/'matcher.py').write_text(BUGGY,encoding='utf-8');(root/'test_matcher.py').write_text(TESTS,encoding='utf-8')


def run_at(root: Path):
    create_fixture(root);h=Harness(root)
    try:
        initial=h.execute(Call('t0','test',{}));read=h.execute(Call('r1','read',{'path':'matcher.py'}))
        # 确定性动作脚本，补丁已由作者编写；不声称模型发现或生成了补丁。
        patch=h.execute(Call('p1','replace',{'expected':read['text'],'new':FIXED}))
        verified=h.execute(Call('t1','test',{}));completed=h.finish()
        report={'kind':'脚本动作控制+真实文件与测试；非LLM效果评测','initial_passed':initial['passed'],'after_patch_passed':verified['passed'],'completed':completed,'patch_applied':patch['wrote'],'diff':''.join(difflib.unified_diff(BUGGY.splitlines(True),FIXED.splitlines(True),fromfile='a/matcher.py',tofile='b/matcher.py')),'trace':h.trace,'symbols':symbols(FIXED)}
        (root/'matcher.py').write_text(FIXED+'\n# 新变更使旧验证过期\n');report['stale_completion_rejected']=not h.finish()
        return report
    finally:h.close()


def run():
    with tempfile.TemporaryDirectory(prefix='ai-course-') as d:return run_at(Path(d))

if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False,indent=2))
