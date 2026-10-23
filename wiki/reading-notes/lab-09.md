---
title: "从契约到补丁与反例测试"
description: "AI系统工程：本地教学正文与可追溯图表"
---

拓展阅读


<span id="section-0"></span>


# 从契约到补丁与反例测试

定义一个虚构的字面目录前缀匹配契约，展示仅比较顶层目录的基线缺陷，以及规范化后的修复。

状态：自检已实际通过　·　环境：Python标准库　·　性质：合成/模拟教学实验  
[对应讲义 11.9](chapter-11.md#m-11-09)　·　[保存Python脚本](../../reading-notes/experiments/09_exclude_contract.py)


<span id="visual-reading"></span>



<span id="topic-1"></span>


## 沿着对象与状态理解本章

先写出要守住的行为，再用会失败的反例证明确实需要修改。测试通过必须绑定被测代码版本；之后再改文件，旧绿色结果不再证明当前交付。

下方图解的固定输入在“输入与适用条件”中声明。它用于解释本章机制，不与本章其他独立例子的数值暗中接续。


<span id="visual-F34"></span>

<span id="topic-2"></span>

<span id="topic-3"></span>

<span id="topic-4"></span>

<span id="topic-5"></span>

<span id="topic-6"></span>

<span id="topic-7"></span>


相关动态过程：[测试是找反例，不是给代码盖绿章](../visual/F34.md)。本节下文继续展示更具体的计算与工程边界。

继续看相关机制：[F30 · 代码检索不能只靠“语义相近”](../visual/F30.md)[F35 · 读指标，先问它的分母是谁](../visual/F35.md)


<span id="method"></span>


## 怎样观察与验证

明确区分src/generated与src/generated2，保持大小写敏感，拒绝父目录穿越和glob。它不代表任何真实构建系统的匹配语义。


<span id="run"></span>


## 运行命令

```
python3 reading-notes/experiments/09_exclude_contract.py
```


<span id="code"></span>


## 完整教学代码

```
"""虚构exclude契约：相对路径、大小写敏感、字面目录前缀，不支持glob。
不读写真实仓库；目标是演示需求、最小修复和反例测试。
"""
import re


def normalize(path: str) -> str:
    if not isinstance(path,str) or not path:
        raise ValueError("路径必须是非空字符串")
    if any(c in path for c in ['\x00','*','?','[',']']):
        raise ValueError("本教学契约不接受NUL或glob字符")
    text=path.replace('\\','/')
    if text.startswith('/') or re.match(r'^[A-Za-z]:',text):
        raise ValueError("仅接受相对路径")
    parts=text.split('/')
    if '..' in parts:
        raise ValueError("禁止父目录穿越")
    normalized='/'.join(p for p in parts if p and p!='.')
    if not normalized:
        raise ValueError("根目录/空路径不在本契约中")
    return normalized


def excluded(path: str, rules: list[str]) -> bool:
    p=normalize(path)
    normalized=[normalize(r) for r in rules]
    return any(p==r or p.startswith(r+'/') for r in normalized)


def filter_files(files: list[str],rules: list[str]) -> list[str]:
    # 保留调用者原始字符串；仅比较时规范化。
    return [p for p in files if not excluded(p,rules)]


def buggy_excluded(path: str,rules: list[str]) -> bool:
    # 故意的基线缺陷：只比较顶层目录，无法处理嵌套规则。
    return normalize(path).split('/')[0] in [normalize(r) for r in rules]


def self_test() -> None:
    assert excluded('src/generated/a.py',['src/generated'])
    assert not excluded('src/generated2/a.py',['src/generated'])
    assert excluded(r'src\generated\a.py',['./src/generated/'])
    assert excluded('build/a.txt',['build'])
    assert not excluded('Build/a.txt',['build'])  # 明确的大小写契约
    files=['src/a.py','tests/a.py']
    assert filter_files(files,[])==files
    assert not buggy_excluded('src/generated/a.py',['src/generated'])
    for bad in ['../secret','/etc/passwd','C:\\secret','a/../b','*','']:
        try:
            normalize(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"应该拒绝: {bad}")


def run_demo() -> dict:
    files=['src/generated/a.py','src/generated2/keep.py','src/main.py','build/out.txt']
    rules=['src/generated','build']
    return {"性质":"虚构契约，不代表PSBuild或任何真实项目",
            "输入":files,"规则":rules,
            "有缺陷基线保留":[p for p in files if not buggy_excluded(p,rules)],
            "修复后保留":filter_files(files,rules),
            "关键反例":"src/generated2 不能被 src/generated 误排除"}


if __name__ == "__main__":
    import json
    self_test()
    print(json.dumps(run_demo(),ensure_ascii=False,indent=2))
```


<span id="result"></span>


## 运行结果示例

以下结果由随包脚本产生。它们不是LLM或产品性能数据。

```
{
  "性质": "虚构契约，不代表PSBuild或任何真实项目",
  "输入": [
    "src/generated/a.py",
    "src/generated2/keep.py",
    "src/main.py",
    "build/out.txt"
  ],
  "规则": [
    "src/generated",
    "build"
  ],
  "有缺陷基线保留": [
    "src/generated/a.py",
    "src/generated2/keep.py",
    "src/main.py"
  ],
  "修复后保留": [
    "src/generated2/keep.py",
    "src/main.py"
  ],
  "关键反例": "src/generated2 不能被 src/generated 误排除"
}
```

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)