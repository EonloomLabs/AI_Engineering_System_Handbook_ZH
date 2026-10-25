---
title: "作业03｜优化：模型仍是黑盒时，改什么才有收益"
description: "主流程课程的可编辑正文"
---

<a id="page-title"></a>

# 作业03｜优化：模型仍是黑盒时，改什么才有收益

**作业范围**

这是本教材的原创累积实验。默认离线路径仅操作生成的临时数据；真实模型、外部账号及GPU路径须自行配置，未运行项明确保留为NOT\_RUN。

沿用构建作业的模型、工具、任务与验收，先写假设，再改一个因素。把接口数据减少与真实模型质量、费用和延迟分别测量。

<a id="hypothesis"></a>

## 可被推翻的假设

本实验的`read_file`返回内容、哈希和120行刻意加入的冗余diagnostics。假设是：只删除diagnostics，可以减少后续请求字节，同时保留这个固定策略做下一步所需的信息。不是假设“所有工具日志都能删”，也不是保证真实LLM等效。

<a id="run"></a>

## 同一任务集，两个策略

```
cd AI_Systems_Engineering_Textbook_ZH/labs/stack
python3 run.py optimize
# 比较 results/a3-baseline.json 与 results/a3-candidate.json
# 汇总见 results/a3-comparison.json
```

`full`复制完整历史作为请求；`trim-diagnostics`复制后移除工具结果中一个指定字段。两者使用同一任务清单、同一脚本后端和同一验收器。因为prepare\_history不修改原始历史，原始证据仍可审计；这不代表所有生产系统都有相同保留机制。

<a id="measure"></a>

## 先核对量纲，再核对收益

| 量 | 本地能否取得 | 正确解释 |
| --- | --- | --- |
| 任务成功数 | 能 | 当前公开合成任务与脚本策略的结果，不是LLM能力分 |
| 累计request\_bytes | 能 | 序列化请求总字节，包含重复发送 |
| 实际Token与缓存命中 | 夹具不提供 | 记录null；真实服务依返回usage或账单核对 |
| 费用 | 夹具不计费 | null不是零价格；需实际价格版本及所有调用账 |
| 墙钟p50/p95 | 能 | 本机短任务计时，含调度噪声；不能当GPU推理基准 |

程序使用最近秩定义的分位数，并在结果中写明方法。八个试验的p95等于接近最大值，样本太少，不适合据此声称尾延迟稳定改善。

<a id="section-193e8e35f909"></a>

### 复算配对结果

令a为双方成功、b为只基线成功、c为只候选成功、d为双方失败。样本数n=a+b+c+d；基线成功率为(a+b)/n，候选为(a+c)/n。净增c−b并不取消b项回归；业务关键任务即使只回归一项，也可能使候选不可接受。

成本每成功试验＝所有运行费用÷成功试验数。费用包含失败、在线重试、路由、压缩和验证；线下策略搜索和评测判分另列。零成功时这个比值未定义，不返回0。不要给同一自建GPU计算同时加上“假想API价格”。

<a id="review-assignment-3-handoff"></a>

### 黑盒对照必须保留未成功的尝试

固定任务ID、模型快照、提示与工具版本、预算和评分器；记录输入/输出用量、等待和重试。脚本夹具的请求字节减少，不能直接换算为真实Token费用或模型成功率改善。

| 最小交接字段 | 含义 |
| --- | --- |
| task\_set\_revision | 任务集合与拆分，不只任务数量 |
| artifact\_before / artifact\_after | 待处理与交付工件的版本 |
| system\_revision | 代码、模型、模板、工具/检索设置 |
| run\_mode | script\_fixture / local\_numeric / live\_model |
| budget / seed / environment | 可控条件；不支持或未测写明 |
| outcome / evidence | 成功、失败、未知、未运行与对应原始记录 |

这些字段用于对照，不要求为小练习搭建数据库或复杂平台。一份JSON和已有日志足够；没有改变的输入用同一版本，新增资料不要悄悄覆盖旧结果。

依据与范围：[[CS2680-A3]](../../sources.md#review-CS2680-A3)；[[CS2680-A4]](../../sources.md#review-CS2680-A4)；[[LOCAL]](../../sources.md#review-LOCAL)。算例条件在本节给定；教学结果不代表商业模型或生产性能。

<a id="experiments"></a>

## 进一步干预，但不要同时改完

可选择减少无用往返、按需检索、固定前缀、工具批处理或模型路由中的一项。先画它省掉的工作，再列新增开销和可能损失的证据。并行需要安全独立的工具；路由需要计入路由器、失败的便宜尝试及恢复成本；摘要需要计入生成和再次检索。

<a id="live"></a>

## 真实模型验证是独立等级

本包的HTTP适配器只覆盖Chat-Completions兼容接口。OpenAI Responses与Anthropic Messages等协议不可仅替换URL；对应工具项、增量事件和结果消息需要单独适配。模型也必须支持实际提供的工具格式，不能以“接口兼容”推导语义兼容。

```
# 只在你已有本地或受控服务并确认资源费用后使用
python3 run.py live --base-url http://127.0.0.1:8000/v1 \
  --model YOUR_MODEL --acknowledge-cost
# 如使用远程HTTPS，还需显式 --allow-remote
# 密钥从 AI_LAB_API_KEY 环境变量读取，不写入教材或结果
```

该命令只运行一个演示任务，不自动完成完整模型基准。要证明优化有效，需要在相同任务上重复运行真实后端、保存usage与配置、检查质量回归，并把策略选择集与最终评测集分开。

<a id="deliver"></a>

## 交付

一份事先填写的假设、一对完整结果、一份配对得失表、一项反例和一个限定范围的结论。可以得出“字节减少但尾延迟没有可信改善”，不能强行把负结果包装成成功。

<details class="quiz-answer" open=""><summary>参考答案：两个方案均8/8，为什么还不能说质量相同？</summary><div class="answer"><p>默认是固定脚本，它不会因语言理解差异而犯错；任务只改变目录名。有限样本都通过只支持这些夹具下的观察。真实模型的分布、随机性、长上下文和异常任务仍需测量。</p></div></details>

方法对照：[黑盒优化作业](../../sources.md#source-set-3e7382dd--harvard-a3)、[评测说明](../../sources.md#source-set-3e7382dd--harvard-eval)。公式与夹具由本教材独立构造。

<a id="local-evidence"></a>

## 本地代码与记录

[带行号的完整实现](../stack/code.md) · [实际运行范围](../../../labs/stack/results/run-report.json) · [本轮机制测试结果](../../../labs/stack/results/tests.json)