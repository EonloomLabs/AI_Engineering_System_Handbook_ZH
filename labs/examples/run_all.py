"""运行全部离线教学实验。Python 3.10+，仅标准库，无网络与API费用。"""
from pathlib import Path
import importlib.util
import json
import sys
import traceback


def main() -> int:
    root=Path(__file__).resolve().parent
    results=[]
    for path in sorted(root.glob('[0-9][0-9]_*.py')):
        name='course_'+path.stem
        try:
            spec=importlib.util.spec_from_file_location(name,path)
            if spec is None or spec.loader is None:
                raise RuntimeError('无法加载实验')
            module=importlib.util.module_from_spec(spec)
            sys.modules[name]=module
            spec.loader.exec_module(module)
            module.self_test()
            results.append({"file":path.name,"tests":"passed","demo":module.run_demo()})
        except Exception as exc:
            results.append({"file":path.name,"tests":"failed","error":str(exc),"trace":traceback.format_exc()})
    print(json.dumps({"all_passed":all(r['tests']=='passed' for r in results),
                      "count":len(results),"results":results},ensure_ascii=False,indent=2))
    return 0 if results and all(r['tests']=='passed' for r in results) else 1


if __name__=='__main__':
    raise SystemExit(main())
