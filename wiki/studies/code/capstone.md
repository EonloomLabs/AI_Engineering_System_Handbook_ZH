---
title: "capstone.py"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# capstone.py

完整exclude补丁案例。对应第18、27章。依赖：标准库。

脚本控制动作；真实补丁和测试；不是LLM自主修复。[阅读运行说明](../experiments.md) / [查看实测结果](../results.md)

[原始Python文件](../../../studies/labs/capstone.py) · 114行

```

<span id="L1"></span>
"""贯穿项目：受限工具修复真实临时仓库中的exclude错误。
<span id="L2"></span>
默认提供者是确定性脚本，不是LLM。真实文件、补丁、子进程测试和验证新鲜度。
<span id="L3"></span>
"""
<span id="L4"></span>
from __future__ import annotations
<span id="L5"></span>
from pathlib import Path
<span id="L6"></span>
from dataclasses import dataclass
<span id="L7"></span>
import tempfile,subprocess,sys,json,difflib
<span id="L8"></span>
from journal import Journal,digest
<span id="L9"></span>
from retrieval import symbols
<span id="L10"></span>
 
<span id="L11"></span>
BUGGY='''from pathlib import PurePosixPath
<span id="L12"></span>
 
<span id="L13"></span>
def should_exclude(path, patterns):
<span id="L14"></span>
    # 契约：路径相对仓库根；末尾/代表目录及后代；其他项精确匹配。
<span id="L15"></span>
    # 历史错误：只比较basename，导致nested路径失配，也误排除同名文件。
<span id="L16"></span>
    path = PurePosixPath(path).name
<span id="L17"></span>
    return path in patterns
<span id="L18"></span>
'''
<span id="L19"></span>
FIXED='''from pathlib import PurePosixPath
<span id="L20"></span>
 
<span id="L21"></span>
def should_exclude(path, patterns):
<span id="L22"></span>
    if not isinstance(path, str) or not all(isinstance(p, str) for p in patterns):
<span id="L23"></span>
        raise TypeError("path和patterns必须是字符串")
<span id="L24"></span>
    normalized = path.replace("\\\\", "/")
<span id="L25"></span>
    parts = PurePosixPath(normalized).parts
<span id="L26"></span>
    if PurePosixPath(normalized).is_absolute() or ".." in parts:
<span id="L27"></span>
        raise ValueError("只支持仓库相对路径，拒绝父级跳转")
<span id="L28"></span>
    value = str(PurePosixPath(normalized))
<span id="L29"></span>
    for pattern in patterns:
<span id="L30"></span>
        rule = pattern.replace("\\\\", "/")
<span id="L31"></span>
        rule_parts = PurePosixPath(rule).parts
<span id="L32"></span>
        if PurePosixPath(rule).is_absolute() or ".." in rule_parts:
<span id="L33"></span>
            raise ValueError("排除规则不能越界")
<span id="L34"></span>
        if rule.endswith("/"):
<span id="L35"></span>
            prefix = str(PurePosixPath(rule))
<span id="L36"></span>
            if value == prefix or value.startswith(prefix + "/"):
<span id="L37"></span>
                return True
<span id="L38"></span>
        elif value == str(PurePosixPath(rule)):
<span id="L39"></span>
            return True
<span id="L40"></span>
    return False
<span id="L41"></span>
'''
<span id="L42"></span>
TESTS='''import unittest
<span id="L43"></span>
from matcher import should_exclude as f
<span id="L44"></span>
class MatchingTests(unittest.TestCase):
<span id="L45"></span>
    def test_top(self): self.assertTrue(f("a.py",["a.py"]))
<span id="L46"></span>
    def test_nested(self): self.assertTrue(f("src/a.py",["src/a.py"]))
<span id="L47"></span>
    def test_same_name(self): self.assertFalse(f("src/a.py",["a.py"]))
<span id="L48"></span>
    def test_directory(self): self.assertTrue(f("vendor/a.py",["vendor/"]))
<span id="L49"></span>
    def test_directory_boundary(self): self.assertFalse(f("vendor2/a.py",["vendor/"]))
<span id="L50"></span>
    def test_windows(self): self.assertTrue(f("src\\\\a.py",["src/a.py"]))
<span id="L51"></span>
    def test_empty(self): self.assertFalse(f("a.py",[]))
<span id="L52"></span>
    def test_parent(self):
<span id="L53"></span>
        with self.assertRaises(ValueError): f("../a.py",["a.py"])
<span id="L54"></span>
if __name__=="__main__": unittest.main()
<span id="L55"></span>
'''
<span id="L56"></span>
 
<span id="L57"></span>
@dataclass(frozen=True)
<span id="L58"></span>
class Call:
<span id="L59"></span>
    id: str
<span id="L60"></span>
    name: str
<span id="L61"></span>
    args: dict
<span id="L62"></span>
 
<span id="L63"></span>
 
<span id="L64"></span>
class Harness:
<span id="L65"></span>
    def __init__(self,root: Path):
<span id="L66"></span>
        self.root=root;self.journal=Journal(root,root/'operations.sqlite');self.trace=[];self.validation=None
<span id="L67"></span>
    def execute(self,call: Call):
<span id="L68"></span>
        # 仅示例工作区。生产验证器应独立于模型可写工作区。
<span id="L69"></span>
        if call.name=='read':
<span id="L70"></span>
            if set(call.args)!={'path'}:raise ValueError('read参数无效')
<span id="L71"></span>
            p=self.journal.path(call.args['path'])
<span id="L72"></span>
            if p.suffix!='.py':raise PermissionError('只读示例源码')
<span id="L73"></span>
            result={'text':p.read_text(),'version':digest(p.read_text())}
<span id="L74"></span>
        elif call.name=='replace':
<span id="L75"></span>
            if set(call.args)!={'expected','new'}:raise ValueError('replace参数无效')
<span id="L76"></span>
            result=self.journal.replace('exclude',call.id,'matcher.py',call.args['expected'],call.args['new']);self.validation=None
<span id="L77"></span>
        elif call.name=='test':
<span id="L78"></span>
            if call.args:raise ValueError('test不接受模型命令')
<span id="L79"></span>
            before=digest((self.root/'matcher.py').read_text())
<span id="L80"></span>
            proc=subprocess.run([sys.executable,'-I','-c',"import runpy,sys;sys.path.insert(0,'.');runpy.run_path('test_matcher.py',run_name='__main__')"],cwd=self.root,capture_output=True,text=True,timeout=10)
<span id="L81"></span>
            after=digest((self.root/'matcher.py').read_text())
<span id="L82"></span>
            self.validation={'version':before,'passed':proc.returncode==0 and before==after,'exit_code':proc.returncode}
<span id="L83"></span>
            result={**self.validation,'log':(proc.stdout+proc.stderr)[-5000:]}
<span id="L84"></span>
        else:raise PermissionError('工具不在白名单')
<span id="L85"></span>
        self.trace.append({'call':{'id':call.id,'name':call.name,'args':{k:('[源码内容]' if k in ('new','expected') else v) for k,v in call.args.items()}},'result':result})
<span id="L86"></span>
        return result
<span id="L87"></span>
    def finish(self):
<span id="L88"></span>
        current=digest((self.root/'matcher.py').read_text())
<span id="L89"></span>
        return bool(self.validation and self.validation['passed'] and self.validation['version']==current)
<span id="L90"></span>
    def close(self):self.journal.close()
<span id="L91"></span>
 
<span id="L92"></span>
 
<span id="L93"></span>
def create_fixture(root: Path):
<span id="L94"></span>
    root.mkdir(parents=True,exist_ok=True)
<span id="L95"></span>
    (root/'matcher.py').write_text(BUGGY,encoding='utf-8');(root/'test_matcher.py').write_text(TESTS,encoding='utf-8')
<span id="L96"></span>
 
<span id="L97"></span>
 
<span id="L98"></span>
def run_at(root: Path):
<span id="L99"></span>
    create_fixture(root);h=Harness(root)
<span id="L100"></span>
    try:
<span id="L101"></span>
        initial=h.execute(Call('t0','test',{}));read=h.execute(Call('r1','read',{'path':'matcher.py'}))
<span id="L102"></span>
        # 确定性动作脚本，补丁已由作者编写；不声称模型发现或生成了补丁。
<span id="L103"></span>
        patch=h.execute(Call('p1','replace',{'expected':read['text'],'new':FIXED}))
<span id="L104"></span>
        verified=h.execute(Call('t1','test',{}));completed=h.finish()
<span id="L105"></span>
        report={'kind':'脚本动作控制+真实文件与测试；非LLM效果评测','initial_passed':initial['passed'],'after_patch_passed':verified['passed'],'completed':completed,'patch_applied':patch['wrote'],'diff':''.join(difflib.unified_diff(BUGGY.splitlines(True),FIXED.splitlines(True),fromfile='a/matcher.py',tofile='b/matcher.py')),'trace':h.trace,'symbols':symbols(FIXED)}
<span id="L106"></span>
        (root/'matcher.py').write_text(FIXED+'\n# 新变更使旧验证过期\n');report['stale_completion_rejected']=not h.finish()
<span id="L107"></span>
        return report
<span id="L108"></span>
    finally:h.close()
<span id="L109"></span>
 
<span id="L110"></span>
 
<span id="L111"></span>
def run():
<span id="L112"></span>
    with tempfile.TemporaryDirectory(prefix='ai-course-') as d:return run_at(Path(d))
<span id="L113"></span>
 
<span id="L114"></span>
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False,indent=2))
```

AI系统工程：从基础到内部  
[全书目录](../../contents.md) · [术语与符号](../../glossary.md) · [参考资料](../../sources.md)