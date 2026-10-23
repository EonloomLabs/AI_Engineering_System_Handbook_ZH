---
title: "完整实验源码 · 12个Python文件"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# 完整实验源码 · 12个Python文件

所有代码为本书原创教学实现，未打包第三方仓库源码。下面可以离线阅读全文，也可直接打开压缩包中的studies/labs目录。运行入口、依赖与验证边界见实验手册。

| 文件 | 实现内容 | 验证范围与限制 |
| --- | --- | --- |
| [attention\_gradients.py](code/attention_gradients.md) | 解析反向传播 章节31 · NumPy | 解析梯度与有限差分；不是任务目标正确性的充分证明 |
| [capstone.py](code/capstone.md) | 完整exclude补丁案例 章节18、27 · 标准库 | 脚本控制动作；真实补丁和测试；不是LLM自主修复 |
| [context\_memory.py](code/context_memory.md) | 上下文装包与双时间记忆 章节11、12、15 · 标准库/SQLite | 元数据和版本契约；不是自然语言语义保真判定 |
| [journal.py](code/journal.md) | 操作日志与真实崩溃恢复 章节08、20、21 · 标准库/SQLite | 单写者局部恢复；不是防恶意竞态的完整安全沙箱 |
| [live\_readonly.py](code/live_readonly.md) | 可选付费API只读适配器 章节07、08 · 标准库+用户API账户 | 未实测；需显式允许联网/计费，禁止发送敏感目录 |
| [numerics.py](code/numerics.md) | 数值机制与前向实现 章节01、02、04、05、06 · NumPy | 缓存、分块softmax、采样与BPE；不是GPU服务或商业模型 |
| [retrieval.py](code/retrieval.md) | BM25、权限、缓存与AST 章节13、14 · 标准库 | 真实词项检索；未实现向量编码器或ANN |
| [run\_all.py](code/run_all.md) | 离线实验运行入口 章节实验手册 · 标准库；NumPy可选 | 输出真实结果；缺依赖会跳过并标记 |
| [sse\_protocol.py](code/sse_protocol.md) | SSE与工具参数状态 章节07 · 标准库 | 协议子集；不是全部事件或生产SDK |
| [statistics\_lab.py](code/statistics_lab.md) | 配对评测统计 章节19 · 标准库 | 全部输入为合成数据；不能当作产品性能结论 |
| [test\_suite.py](code/test_suite.md) | 49项单元与集成测试 章节对应各实验 · 标准库；NumPy可选 | 明确故障样本和断言；全绿不等于生产认证 |
| [train\_tiny\_lm.py](code/train_tiny_lm.md) | 小型Transformer真实训练 章节03 · PyTorch | 合成数据训练；没有通用语言能力或测试集泛化结论 |

[实验解释](experiments.md)[实际结果](results.md)[49项测试原始日志](../../studies/reports/test_log.txt)

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)