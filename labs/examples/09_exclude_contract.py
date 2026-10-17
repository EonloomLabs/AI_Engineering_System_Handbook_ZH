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
