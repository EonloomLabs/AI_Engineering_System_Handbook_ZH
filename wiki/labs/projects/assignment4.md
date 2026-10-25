---
title: "作业04｜服务：从接口合同下探模型与引擎"
description: "主流程课程的可编辑正文"
---

<a id="page-title"></a>

# 作业04｜服务：从接口合同下探模型与引擎

**作业范围**

这是本教材的原创累积实验。默认离线路径仅操作生成的临时数据；真实模型、外部账号及GPU路径须自行配置，未运行项明确保留为NOT\_RUN。

把已有Agent接到自己负责的模型服务上。不要同时把“HTTP能连接”“权重能计算”和“真实服务达到性能目标”认作同一项成功。

<a id="levels"></a>

## 三个验收等级

| 等级 | 本包提供什么 | 是否已实际运行 | 还不能证明什么 |
| --- | --- | --- | --- |
| 协议接通 | localhost上的脚本化Chat接口，真实HTTP传输 | 是 | 不是神经网络服务，没有GPU计算 |
| 模型计算 | 加载既有小模型权重，CPU逐轮生成 | 是 | 不是通用编码模型，也不能完成工具任务 |
| 引擎与工作负载 | 真实模型接入说明、测量模板和验收规则 | NOT\_RUN | 没有官方GPU、商用API或正式任务基准成绩 |

<a id="offline"></a>

## 先检查接口与模型，再追性能

```
cd AI_Systems_Engineering_Textbook_ZH/labs/stack
python3 run.py serve
```

程序启动仅绑定回环地址的临时HTTP服务，用同一run\_episode完成索引任务，然后关闭服务。另行加载`labs/model/data/weights_trained.json`，用`reference_inference.generate`进行真实CPU计算。二者结果分开保存，前者不冒充后者。

小模型的输入编号为`[6,1,2]`，完整结果为`[6,1,2,3,5,7]`。它使用已训练权重；末尾7为该教学词表中的EOS。它的词表与参数结构仅适用于这条模型主线，不能把编号直接送到外部大模型。

<a id="real"></a>

## 准备真实引擎的最小清单

先确定模型许可和权重来源、模型与Tokenizer版本、引擎版本、GPU型号／显存／驱动、精度、并行方式、上下文上限、聊天模板以及工具解析器。模型能够输出普通文本，不保证它能按本课程工具协议调用。验证时先做普通请求，再做一个只读工具调用，最后运行相同任务集。

Harvard分配的账号、GPU与私有评测环境不随本教材提供。课程公开作业可能更新硬件和模型规格，本教材不把旧版设备写成通用要求。你自己的引擎应保留完整启动命令和版本；这里不假装已经在那台硬件上运行。

<a id="section-2c6c66fa6c90"></a>

### 接入时容易漏掉的边界

默认只接受localhost端点。远程模式需HTTPS和显式确认。令牌不要放URL或提交进仓库。服务的API key未必覆盖所有路由，监控端点、管理端点和其他兼容接口还需网关或防火墙；不要把监听0.0.0.0后设置一个key等同于完整访问控制。TLS、认证和任务工具授权是不同层。

<a id="metrics"></a>

## 运行时测量，不只在结束后看日志

先记录冷启动与模型加载，随后以固定请求长度、并发和生成上限执行微基准。再运行同一个多轮Agent：持续采集队列、prefill/decode、KV占用、缓存命中、请求时间与运行期`/metrics`（若引擎提供），用请求ID关联。静态QPS微基准和真实Agent的工具间隙不可混算。

| 问题 | 观察对象 | 先试的一种干预 | 必须核对的代价 |
| --- | --- | --- | --- |
| 长输入阻塞短请求 | 队列等待与prefill区间 | 分块或调度策略 | 吞吐、尾延迟、实现约束 |
| 并发装不下 | 参数、激活、KV与保留内存 | 长度/并发上限或合适精度 | 拒绝率、质量和重算 |
| 工具回来需要重做前缀 | 前缀复用与缓存保留时间 | 缓存策略或请求稳定前缀 | 容量机会成本、过期状态 |
| Token变快但任务没变快 | 完整依赖时间线 | 工具或控制流 | 额外工作和任务正确率 |

<a id="review-assignment-4-handoff"></a>

### 从黑盒换成自建服务，先验接口再谈加速

首先核对模板、停止原因、工具调用结构和错误响应，再使用相同任务测质量及端到端耗时。CPU微型模型只是数值与协议验证；真实GPU引擎未运行的字段写NOT\_RUN，不填估算值。

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

<a id="resource"></a>

## 先用账本排除不可能的解释

给定常见KV布局，缓存字节数为`2×L×B×Hkv×T×dh×s`。例如16层、8条序列、4个KV头、每头64维、1024位置、2字节精度，得到134,217,728字节＝128MiB。这里不含参数、激活、对齐与引擎预留，也不适用于任意压缩注意力结构。

矩阵`[m,k]×[k,n]`的主要前向计算约2mkn FLOPs；训练再计算输入梯度与权重梯度，粗略合计6mkn。把多层权重相乘的数量概括为每Token约2N推理、约6N训练时，必须说明忽略了Attention长度项、归一化、优化器、重计算及通信；不是GPU时间公式。

<a id="deliver"></a>

## 验收

交付实际引擎配置、任务结果、原始metrics、请求轨迹、单变量对照及限制。未运行真实引擎时，保留`real_engine_benchmark=NOT_RUN`与`course_assignment_complete=false`。完成前两级是有价值的准备，但不能代替第三级。

<details class="quiz-answer" open=""><summary>参考答案：为什么不把本地HTTP夹具的p95作为服务基准？</summary><div class="answer"><p>它执行的是固定Python策略，没有加载大模型、没有prefill/decode GPU算子、没有真实KV容量压力。它能证明HTTP合同和Agent接入路径工作，不能证明模型或GPU的性能。</p></div></details>

课程方法参照[CS2680服务作业](../../sources.md#source-set-3e7382dd--harvard-a4)；实际适配边界参见[接口来源](../../sources.md#source-set-3e7382dd--live-apis)。

<a id="local-evidence"></a>

## 本地代码与记录

[带行号的完整实现](../stack/code.md) · [实际运行范围](../../../labs/stack/results/run-report.json) · [本轮机制测试结果](../../../labs/stack/results/tests.json)