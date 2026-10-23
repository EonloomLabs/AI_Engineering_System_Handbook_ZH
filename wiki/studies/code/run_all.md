---
title: "run_all.py"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# run\_all.py

离线实验运行入口。对应第实验手册章。依赖：标准库；NumPy可选。

输出真实结果；缺依赖会跳过并标记。[阅读运行说明](../experiments.md) / [查看实测结果](../results.md)

[原始Python文件](../../../studies/labs/run_all.py) · 21行

```

<span id="L1"></span>
"""运行离线机制、协议、恢复与仓库集成实验。不发送网络请求。"""
<span id="L2"></span>
from pathlib import Path
<span id="L3"></span>
import sys,unittest,json,platform,time
<span id="L4"></span>
from io import StringIO
<span id="L5"></span>
import test_suite,capstone,retrieval,context_memory,sse_protocol,statistics_lab
<span id="L6"></span>
 
<span id="L7"></span>
def main():
<span id="L8"></span>
 out=Path(__file__).resolve().parents[1]/'reports';out.mkdir(exist_ok=True)
<span id="L9"></span>
 log=StringIO();start=time.perf_counter();suite=unittest.defaultTestLoader.loadTestsFromModule(test_suite)
<span id="L10"></span>
 result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
<span id="L11"></span>
 reports={'python':platform.python_version(),'platform':platform.platform(),'test_count':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'seconds':time.perf_counter()-start,'live_llm':'NOT_RUN','gpu_benchmark':'NOT_RUN','production_security_audit':'NOT_RUN','scope':'机制/协议/真实本地文件及子进程；所有任务与数值数据为作者构建','capstone':capstone.run(),'retrieval':retrieval.run(),'context_memory':context_memory.run(),'sse':sse_protocol.run(),'statistics':statistics_lab.run()}
<span id="L12"></span>
 try:
<span id="L13"></span>
  import numerics
<span id="L14"></span>
  reports['numerics']=numerics.run()
<span id="L15"></span>
  import attention_gradients
<span id="L16"></span>
  reports['attention_backward']=attention_gradients.run()
<span id="L17"></span>
 except ImportError:reports['numerics']={'status':'NOT_RUN','reason':'NumPy未安装'}
<span id="L18"></span>
 (out/'test_results.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
<span id="L19"></span>
 (out/'test_log.txt').write_text(log.getvalue(),encoding='utf-8');print(log.getvalue());print('报告:',out/'test_results.json')
<span id="L20"></span>
 return 0 if result.wasSuccessful() else 1
<span id="L21"></span>
if __name__=='__main__':raise SystemExit(main())
```

AI系统工程：从基础到内部  
[全书目录](../../contents.md) · [术语与符号](../../glossary.md) · [参考资料](../../sources.md)