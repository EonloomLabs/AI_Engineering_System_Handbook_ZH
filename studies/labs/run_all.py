"""运行离线机制、协议、恢复与仓库集成实验。不发送网络请求。"""
from pathlib import Path
import sys,unittest,json,platform,time
from io import StringIO
import test_suite,capstone,retrieval,context_memory,sse_protocol,statistics_lab

def main():
 out=Path(__file__).resolve().parents[1]/'reports';out.mkdir(exist_ok=True)
 log=StringIO();start=time.perf_counter();suite=unittest.defaultTestLoader.loadTestsFromModule(test_suite)
 result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
 reports={'python':platform.python_version(),'platform':platform.platform(),'test_count':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'seconds':time.perf_counter()-start,'live_llm':'NOT_RUN','gpu_benchmark':'NOT_RUN','production_security_audit':'NOT_RUN','scope':'机制/协议/真实本地文件及子进程；所有任务与数值数据为作者构建','capstone':capstone.run(),'retrieval':retrieval.run(),'context_memory':context_memory.run(),'sse':sse_protocol.run(),'statistics':statistics_lab.run()}
 try:
  import numerics
  reports['numerics']=numerics.run()
  import attention_gradients
  reports['attention_backward']=attention_gradients.run()
 except ImportError:reports['numerics']={'status':'NOT_RUN','reason':'NumPy未安装'}
 (out/'test_results.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
 (out/'test_log.txt').write_text(log.getvalue(),encoding='utf-8');print(log.getvalue());print('报告:',out/'test_results.json')
 return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
