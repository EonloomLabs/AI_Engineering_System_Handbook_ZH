"""运行本书401例所配套的确定性数值/状态见证；不调用网络或模型。"""
from pathlib import Path
import subprocess,sys,json
root=Path(__file__).resolve().parent
results=[]
for script in ["engine.py","additional_checks.py","chain_and_operators.py"]:
    p=subprocess.run([sys.executable,str(root/script),"--test"],cwd=root,text=True,capture_output=True)
    print(p.stdout);print(p.stderr)
    results.append({"script":script,"returncode":p.returncode})
    if p.returncode:raise SystemExit(p.returncode)
for script,name in [("engine.py","numbers.json"),("additional_checks.py","extra_numbers.json"),("chain_and_operators.py","chain_numbers.json")]:
    p=subprocess.run([sys.executable,str(root/script)],cwd=root,text=True,capture_output=True,check=True)
    json.loads(p.stdout)
    (root/name).write_text(p.stdout,encoding="utf-8")
print(json.dumps({"all_passed":True,"suites":results},ensure_ascii=False,indent=2))
