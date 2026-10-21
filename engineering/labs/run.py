"""Run offline tests and persist machine-readable, versioned observations."""
from __future__ import annotations
import contextlib, datetime, hashlib, io, json, platform, sqlite3, sys, unittest
from pathlib import Path
import torch
import importlib.metadata, subprocess
import test_engineering as test

def main():
    out=Path(__file__).resolve().parents[1]/'results';out.mkdir(exist_ok=True)
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test))
    env={'python':sys.version,'platform':platform.platform(),'torch':torch.__version__,
         'cuda_available':torch.cuda.is_available(),'sqlite':sqlite3.sqlite_version,
         'pytest':importlib.metadata.version('pytest'),
         'git':subprocess.run(['git','--version'],capture_output=True,text=True,check=True).stdout.strip(),
         'ran_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'claims':'CPU and local temporary resources only; no commercial model/GPU/production service benchmarks.'}
    data={'environment':env,'tests':result.testsRun,'failures':len(result.failures),
          'errors':len(result.errors),'skipped':len(result.skipped),'observations':test.OBS,
          'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}}
    (out/'run.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    (out/'test.log').write_text(stream.getvalue())
    print(stream.getvalue());print(json.dumps({k:v for k,v in data.items() if k!='observations'},ensure_ascii=False,indent=2))
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__':sys.exit(main())
