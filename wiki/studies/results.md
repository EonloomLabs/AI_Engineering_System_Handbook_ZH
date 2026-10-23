---
title: "实际结果 · 记录与轨迹全部展开"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# 实际结果 · 记录与轨迹全部展开

**49项离线测试通过，0失败、0错误、0跳过。**CPU小模型训练另外执行。商业模型、GPU基准、生产安全审计未执行。下面是实际报告，不是预期值。

[原始JSON](../../studies/reports/test_results.json) / [测试日志](../../studies/reports/test_log.txt) / [训练JSON](../../studies/reports/tiny_training.json) / [如何解释这些结果](experiments.md)


<span id="section-1"></span>


## 执行环境与验证范围

```
{
  "python": "3.13.5",
  "platform": "Linux-6.18.55-x86_64-with-glibc2.41",
  "test_count": 49,
  "failures": 0,
  "errors": 0,
  "skipped": 0,
  "seconds": 2.300336534000053,
  "live_llm": "NOT_RUN",
  "gpu_benchmark": "NOT_RUN",
  "production_security_audit": "NOT_RUN",
  "scope": "机制/协议/真实本地文件及子进程；所有任务与数值数据为作者构建"
}
```


<span id="section-2"></span>


## 真实小模型CPU训练

```
{
  "kind": "真实小型模型CPU训练；合成数据；未运行商业模型或GPU吞吐基准",
  "torch_version": "2.10.0+cpu",
  "parameter_count": 18320,
  "steps": 100,
  "initial_train_loss": 2.846790313720703,
  "final_train_loss": 0.003446191782131791,
  "train_token_accuracy": 1.0,
  "causal_prefix_error": 0.0,
  "elapsed_seconds": 0.3893101959999967,
  "history": [
    {
      "step": 0,
      "loss": 2.846790313720703
    },
    {
      "step": 20,
      "loss": 0.1237737238407135
    },
    {
      "step": 40,
      "loss": 0.013883101753890514
    },
    {
      "step": 60,
      "loss": 0.006276607979089022
    },
    {
      "step": 80,
      "loss": 0.004390936344861984
    }
  ],
  "limitation": "测试集泛化尚未评价；高训练准确率不是通用语言理解"
}
```


<span id="section-3"></span>


## 数值前向与采样

```
{
  "kind": "数值机制实验；非商用模型评测",
  "cache_max_error": 1.5543122344752192e-15,
  "wrong_rope_offset_error": 3.1744545678365306,
  "online_softmax_error": 3.552713678800501e-15,
  "speculative": {
    "empirical": [
      0.5978666666666667,
      0.30333333333333334,
      0.0988
    ],
    "target": [
      0.6,
      0.3,
      0.1
    ],
    "acceptance": 0.6037333333333333,
    "trials": 30000
  },
  "byte_bpe_roundtrip": "工程lower"
}
```


<span id="section-4"></span>


## 解析反向与有限差分

```
{
  "kind": "解析反向与有限差分；非训练能力/非GPU性能评测",
  "max_absolute_errors": {
    "dQ": 9.143890158935797e-11,
    "dK": 1.9576201770732382e-10,
    "dV": 1.1711515091050728e-10
  }
}
```


<span id="section-5"></span>


## 权限检索

```
{
  "kind": "权限过滤先于评分的真实词项检索",
  "result": [
    [
      "current",
      0.8630462173553426
    ]
  ],
  "denied": [],
  "symbols": [
    {
      "name": "choose",
      "kind": "FunctionDef",
      "start": 1,
      "end": 2
    }
  ],
  "rrf": [
    [
      "current",
      0.03252247488101534
    ],
    [
      "old",
      0.03252247488101534
    ]
  ]
}
```


<span id="section-6"></span>


## 上下文与记忆

```
{
  "kind": "确定性元数据约束，不证明自然语言语义保真",
  "pack": {
    "selected": [
      "definition",
      "policy",
      "usage"
    ],
    "cost": 70,
    "budget": 75
  },
  "historically_unknown": {
    "status": "not_found",
    "claims": []
  },
  "now_known": {
    "status": "found",
    "claims": [
      "repository-relative"
    ]
  }
}
```


<span id="section-7"></span>


## SSE协议分片

```
{
  "kind": "协议字节分片实验，非真实网络请求",
  "calls": [
    {
      "id": "c1",
      "name": "read_file",
      "args": {
        "path": "中文.py"
      }
    }
  ]
}
```


<span id="section-8"></span>


## 合成统计实验

```
{
  "kind": "合成评测数据",
  "bootstrap": {
    "difference": 0.2222222222222222,
    "interval_95": [
      -1.850371707708594e-17,
      0.3333333333333333
    ],
    "resampling_unit": "task"
  },
  "pass_at_3": 0.5333333333333333,
  "wilson_8_of_10": [
    0.49016247153665027,
    0.943317848545623
  ],
  "mcnemar_b1_c4": 0.375,
  "independent_p08_all3": 0.5120000000000001
}
```


<span id="section-9"></span>


## 贯穿案例：实际差异

```
--- a/matcher.py
+++ b/matcher.py
@@ -1,7 +1,22 @@
 from pathlib import PurePosixPath
 
 def should_exclude(path, patterns):
-    # 契约：路径相对仓库根；末尾/代表目录及后代；其他项精确匹配。
-    # 历史错误：只比较basename，导致nested路径失配，也误排除同名文件。
-    path = PurePosixPath(path).name
-    return path in patterns
+    if not isinstance(path, str) or not all(isinstance(p, str) for p in patterns):
+        raise TypeError("path和patterns必须是字符串")
+    normalized = path.replace("\\", "/")
+    parts = PurePosixPath(normalized).parts
+    if PurePosixPath(normalized).is_absolute() or ".." in parts:
+        raise ValueError("只支持仓库相对路径，拒绝父级跳转")
+    value = str(PurePosixPath(normalized))
+    for pattern in patterns:
+        rule = pattern.replace("\\", "/")
+        rule_parts = PurePosixPath(rule).parts
+        if PurePosixPath(rule).is_absolute() or ".." in rule_parts:
+            raise ValueError("排除规则不能越界")
+        if rule.endswith("/"):
+            prefix = str(PurePosixPath(rule))
+            if value == prefix or value.startswith(prefix + "/"):
+                return True
+        elif value == str(PurePosixPath(rule)):
+            return True
+    return False
```


<span id="section-10"></span>


## 贯穿案例：实际调用、stdout与退出码


<span id="section-11"></span>


### 步骤1

```
{
  "call": {
    "id": "t0",
    "name": "test",
    "args": {}
  },
  "result": {
    "version": "9889901cd19183eb5a6fcdb45fd82538ad8e85ed15c768678af5dfe7ea1a6b4d",
    "passed": false,
    "exit_code": 1,
    "log": "F..FFF.F\n======================================================================\nFAIL: test_directory (__main__.MatchingTests.test_directory)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"test_matcher.py\", line 7, in test_directory\n    def test_directory(self): self.assertTrue(f(\"vendor/a.py\",[\"vendor/\"]))\n                              ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: False is not true\n\n======================================================================\nFAIL: test_nested (__main__.MatchingTests.test_nested)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"test_matcher.py\", line 5, in test_nested\n    def test_nested(self): self.assertTrue(f(\"src/a.py\",[\"src/a.py\"]))\n                           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: False is not true\n\n======================================================================\nFAIL: test_parent (__main__.MatchingTests.test_parent)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"test_matcher.py\", line 12, in test_parent\n    with self.assertRaises(ValueError): f(\"../a.py\",[\"a.py\"])\n         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^\nAssertionError: ValueError not raised\n\n======================================================================\nFAIL: test_same_name (__main__.MatchingTests.test_same_name)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"test_matcher.py\", line 6, in test_same_name\n    def test_same_name(self): self.assertFalse(f(\"src/a.py\",[\"a.py\"]))\n                              ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: True is not false\n\n======================================================================\nFAIL: test_windows (__main__.MatchingTests.test_windows)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"test_matcher.py\", line 9, in test_windows\n    def test_windows(self): self.assertTrue(f(\"src\\\\a.py\",[\"src/a.py\"]))\n                            ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: False is not true\n\n----------------------------------------------------------------------\nRan 8 tests in 0.001s\n\nFAILED (failures=5)\n"
  }
}
```


<span id="section-12"></span>


### 步骤2

```
{
  "call": {
    "id": "r1",
    "name": "read",
    "args": {
      "path": "matcher.py"
    }
  },
  "result": {
    "text": "from pathlib import PurePosixPath\n\ndef should_exclude(path, patterns):\n    # 契约：路径相对仓库根；末尾/代表目录及后代；其他项精确匹配。\n    # 历史错误：只比较basename，导致nested路径失配，也误排除同名文件。\n    path = PurePosixPath(path).name\n    return path in patterns\n",
    "version": "9889901cd19183eb5a6fcdb45fd82538ad8e85ed15c768678af5dfe7ea1a6b4d"
  }
}
```


<span id="section-13"></span>


### 步骤3

```
{
  "call": {
    "id": "p1",
    "name": "replace",
    "args": {
      "expected": "[源码内容]",
      "new": "[源码内容]"
    }
  },
  "result": {
    "status": "applied",
    "wrote": true,
    "version": "383da239221fd2a5d1d19cfc232ebe6403e3730c9ed9ae15f1f58322a9e8b769"
  }
}
```


<span id="section-14"></span>


### 步骤4

```
{
  "call": {
    "id": "t1",
    "name": "test",
    "args": {}
  },
  "result": {
    "version": "383da239221fd2a5d1d19cfc232ebe6403e3730c9ed9ae15f1f58322a9e8b769",
    "passed": true,
    "exit_code": 0,
    "log": "........\n----------------------------------------------------------------------\nRan 8 tests in 0.000s\n\nOK\n"
  }
}
```


<span id="section-15"></span>


## 全部测试名称与结果

```
test_all_gradients (test_suite.AttentionBackwardTests.test_all_gradients) ... ok
test_future_gradient_zero (test_suite.AttentionBackwardTests.test_future_gradient_zero) ... ok
test_mask_validation (test_suite.AttentionBackwardTests.test_mask_validation) ... ok
test_upstream_shape (test_suite.AttentionBackwardTests.test_upstream_shape) ... ok
test_cycle (test_suite.ContextTests.test_cycle) ... ok
test_dependency (test_suite.ContextTests.test_dependency) ... ok
test_memory (test_suite.ContextTests.test_memory) ... ok
test_memory_conflict (test_suite.ContextTests.test_memory_conflict) ... ok
test_missing_dependency (test_suite.ContextTests.test_missing_dependency) ... ok
test_required_overflow (test_suite.ContextTests.test_required_overflow) ... ok
test_stale_evidence (test_suite.ContextTests.test_stale_evidence) ... ok
test_unbacked_claim (test_suite.ContextTests.test_unbacked_claim) ... ok
test_all_masked_rejected (test_suite.NumericsTests.test_all_masked_rejected) ... ok
test_bpe_merge_shortens (test_suite.NumericsTests.test_bpe_merge_shortens) ... ok
test_bpe_roundtrip (test_suite.NumericsTests.test_bpe_roundtrip) ... ok
test_cache_chunk (test_suite.NumericsTests.test_cache_chunk) ... ok
test_cache_token (test_suite.NumericsTests.test_cache_token) ... ok
test_causal (test_suite.NumericsTests.test_causal) ... ok
test_dpo_gradient (test_suite.NumericsTests.test_dpo_gradient) ... ok
test_gradient (test_suite.NumericsTests.test_gradient) ... ok
test_gradient_sum_zero (test_suite.NumericsTests.test_gradient_sum_zero) ... ok
test_negative_mask_detected (test_suite.NumericsTests.test_negative_mask_detected) ... ok
test_online (test_suite.NumericsTests.test_online) ... ok
test_rope_norm (test_suite.NumericsTests.test_rope_norm) ... ok
test_softmax_stable (test_suite.NumericsTests.test_softmax_stable) ... ok
test_speculative_distribution (test_suite.NumericsTests.test_speculative_distribution) ... ok
test_wrong_offset_detected (test_suite.NumericsTests.test_wrong_offset_detected) ... ok
test_failed_response (test_suite.ProtocolTests.test_failed_response) ... ok
test_id_conflict (test_suite.ProtocolTests.test_id_conflict) ... ok
test_not_executed_on_delta (test_suite.ProtocolTests.test_not_executed_on_delta) ... ok
test_truncated_sse (test_suite.ProtocolTests.test_truncated_sse) ... ok
test_utf8_sse (test_suite.ProtocolTests.test_utf8_sse) ... ok
test_capstone_actual_patch (test_suite.RecoveryTests.test_capstone_actual_patch) ... ok
test_changed_after_applied (test_suite.RecoveryTests.test_changed_after_applied) ... ok
test_id_reuse (test_suite.RecoveryTests.test_id_reuse) ... ok
test_outside_root (test_suite.RecoveryTests.test_outside_root) ... ok
test_real_crash_and_reconcile (test_suite.RecoveryTests.test_real_crash_and_reconcile) ... ok
test_stale_precondition (test_suite.RecoveryTests.test_stale_precondition) ... ok
test_acl (test_suite.RetrievalTests.test_acl) ... ok
test_ast (test_suite.RetrievalTests.test_ast) ... ok
test_empty (test_suite.RetrievalTests.test_empty) ... ok
test_principal_cache_isolation (test_suite.RetrievalTests.test_principal_cache_isolation) ... ok
test_rrf_duplicate (test_suite.RetrievalTests.test_rrf_duplicate) ... ok
test_update_invalidates (test_suite.RetrievalTests.test_update_invalidates) ... ok
test_version (test_suite.RetrievalTests.test_version) ... ok
test_mcnemar_zero (test_suite.StatisticsTests.test_mcnemar_zero) ... ok
test_paired_identity (test_suite.StatisticsTests.test_paired_identity) ... ok
test_pass_at_k (test_suite.StatisticsTests.test_pass_at_k) ... ok
test_wilson (test_suite.StatisticsTests.test_wilson) ... ok

----------------------------------------------------------------------
Ran 49 tests in 2.298s

OK
```

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)