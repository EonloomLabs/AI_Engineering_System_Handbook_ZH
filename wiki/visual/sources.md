---
title: "图解的来源与适用边界"
description: "AI系统工程：本地教学正文与可追溯图表"
---

图解 · 运行过程 · 工程取舍


<span id="page-title"></span>


# 图解的来源与适用边界

图解正文为原创中文解释，教学数字和状态来自本书声明的场景。下列一手资料支持机制；它们不包含本书所有手算数字，也不意味着本书复现了商业系统。

核对日期：2026-10-19。产品接口可能更新；具体模型的缓存、停止、权限与协议要求需按使用时版本再确认。


<span id="s-TOKEN"></span>



<span id="topic-1"></span>


## TOKEN · 分词与编号

Token是分词器的片段单位，字符、字节和Token并不一一对应。图中的中文词表是教学约定。

<https://huggingface.co/docs/transformers/en/tokenizer_summary>


<span id="s-PADDING"></span>



<span id="topic-2"></span>


## PADDING · 组批、补齐与截断

不同长度输入的补齐方式与模型接口有关；图中明确使用右侧补齐，不代表所有生成接口的建议。

<https://huggingface.co/docs/transformers/main/en/pad_truncation>


<span id="s-TENSOR"></span>



<span id="topic-3"></span>


## TENSOR · PyTorch Tensor 与数据表示

形状、数据类型与设备共同决定张量的使用方式。字节计数按本书声明的类型独立计算。

<https://docs.pytorch.org/docs/2.14/tensors.html>


<span id="s-EMBED"></span>



<span id="topic-4"></span>


## EMBED · Embedding 查表

索引选择参数表中的行；输出增加嵌入宽度这一末轴。向量不是编号的二进制转换。

<https://docs.pytorch.org/docs/2.14/generated/torch.nn.Embedding.html>


<span id="s-LINEAR"></span>



<span id="topic-5"></span>


## LINEAR · 线性层

仿射变换改变末轴特征；PyTorch存储权重方向与教材行向量写法要按形状对照。

<https://docs.pytorch.org/docs/2.14/generated/torch.nn.Linear.html>


<span id="s-SOFTMAX"></span>



<span id="topic-6"></span>


## SOFTMAX · Softmax

按指定轴归一化得到非负且总和为1的份额。本书手算包含稳定平移和抽样区间。

<https://docs.pytorch.org/docs/2.14/generated/torch.nn.Softmax.html>


<span id="s-SDPA"></span>



<span id="topic-7"></span>


## SDPA · 缩放点积注意力

注意力的缩放、mask与加权聚合。布尔mask的含义依接口而定，不能照搬另一API约定。

<https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.scaled_dot_product_attention.html>


<span id="s-ATTN"></span>



<span id="topic-8"></span>


## ATTN · Transformer 原始论文

多头注意力和Transformer结构的原始依据。教学单头模型不是原论文完整架构。

<https://arxiv.org/abs/1706.03762>


<span id="s-ROPE"></span>



<span id="topic-9"></span>


## ROPE · RoFormer 与旋转位置表示

旋转Q/K的一对分量使内积能表达相对位置。图中固定角度只是可手算示例。

<https://arxiv.org/abs/2104.09864>


<span id="s-NORM"></span>



<span id="topic-10"></span>


## NORM · LayerNorm

按指定维度归一化并学习仿射参数；不等于整批所有位置共同归一化。

<https://docs.pytorch.org/docs/2.14/generated/torch.nn.LayerNorm.html>


<span id="s-GEN"></span>



<span id="topic-11"></span>


## GEN · 自回归生成策略

区分模型给出的分数、解码选择规则与停止条件。本书三轮生成来自可复算的教学权重。

<https://huggingface.co/docs/transformers/generation_strategies>


<span id="s-CACHE"></span>



<span id="topic-12"></span>


## CACHE · KV缓存运行机制

每层保存历史K/V，继续生成时结合过去与新位置。缓存复用要求模型和前缀等条件一致。

<https://huggingface.co/docs/transformers/cache_explanation>


<span id="s-AUTOGRAD"></span>



<span id="topic-13"></span>


## AUTOGRAD · 自动求导

计算图反向求导与优化器参数更新分开；本书梯度例另用有限差分核对。

<https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html>


<span id="s-CE"></span>



<span id="topic-14"></span>


## CE · 交叉熵损失

目标、有效样本与归约方式影响损失；教学中忽略PAD时同时改变分子与分母。

<https://docs.pytorch.org/docs/2.14/generated/torch.nn.CrossEntropyLoss.html>


<span id="s-DPO"></span>



<span id="topic-15"></span>


## DPO · 直接偏好优化

使用偏好数据构造模型优化目标。偏好不自动等于事实正确性。

<https://arxiv.org/abs/2305.18290>


<span id="s-GQA"></span>



<span id="topic-16"></span>


## GQA · Grouped-Query Attention

多组Query共享较少K/V头以改变缓存和推理成本；并非任意权重都能直接等价换成GQA。

<https://arxiv.org/abs/2305.13245>


<span id="s-FLASH"></span>



<span id="topic-17"></span>


## FLASH · FlashAttention

分块和在线归一化减少中间数据读写；本书推导的是数学关系，不声称GPU加速实测。

<https://arxiv.org/abs/2205.14135>


<span id="s-PAGED"></span>



<span id="topic-18"></span>


## PAGED · PagedAttention

将KV缓存映射到非连续物理块以改善内存管理。图中槽位和步时为教学构造。

<https://arxiv.org/abs/2309.06180>


<span id="s-LORA"></span>



<span id="topic-19"></span>


## LORA · 低秩适配 LoRA

冻结基础权重并训练低秩增量。少训练参数不等于基础权重不占空间。

<https://arxiv.org/abs/2106.09685>


<span id="s-QLORA"></span>



<span id="topic-20"></span>


## QLORA · 量化与参数高效微调

QLoRA采用量化基础权重等设计；本书均匀刻度例不冒充NF4格式。

<https://arxiv.org/abs/2305.14314>


<span id="s-MOE"></span>



<span id="topic-21"></span>


## MOE · Switch Transformers

稀疏专家路由可改变每Token激活的计算。教学top-2例用于说明选择和混合，不是Switch的top-1复现。

<https://arxiv.org/abs/2101.03961>


<span id="s-CHECKPOINT"></span>



<span id="topic-22"></span>


## CHECKPOINT · 激活检查点

以重算换部分保存量，须注意随机状态与实现变体；保存量不等于实际峰值显存。

<https://docs.pytorch.org/docs/2.14/checkpoint.html>


<span id="s-SPEC"></span>



<span id="topic-23"></span>


## SPEC · 推测解码

随机版本的接受率与拒绝后修正分布；不能用无条件接受草稿替代验证步骤。

<https://arxiv.org/abs/2211.17192>


<span id="s-AGENT"></span>



<span id="topic-24"></span>


## AGENT · Codex Agent Loop

模型请求工具后由宿主执行并反馈结果。只使用公开机制，不反推闭源模型内部实现。

<https://openai.com/index/unrolling-the-codex-agent-loop/>


<span id="s-TOOLS"></span>



<span id="topic-25"></span>


## TOOLS · 工具设计

工具应让任务边界、输入和结果清楚可用。教学请求不是特定产品的完整协议。

<https://www.anthropic.com/engineering/writing-tools-for-agents>


<span id="s-MCP"></span>



<span id="topic-26"></span>


## MCP · MCP 架构

区分Host、Client和Server；工具发现本身不提供业务授权。采用该日期版本的架构说明。

<https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture>


<span id="s-SSE"></span>



<span id="topic-27"></span>


## SSE · SSE 事件流

传输分片、文本解码、SSE帧与业务完成事件不是同一层。

<https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events>


<span id="s-STATE"></span>



<span id="topic-28"></span>


## STATE · SQLite 原子提交

本地事务能维护数据库状态；不能推出远端副作用与本地提交组成一项跨系统原子事务。

<https://www.sqlite.org/atomiccommit.html>


<span id="s-CONTEXT"></span>



<span id="topic-29"></span>


## CONTEXT · 上下文工程

选择、按需取回和压缩分别处理有限上下文；摘要有损，仍要保留证据和任务状态。

<https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>


<span id="s-PCACHE"></span>



<span id="topic-30"></span>


## PCACHE · Prompt caching

复用计算不同于删除或总结上下文；缓存边界依具体模型与服务接口核对。

<https://developers.openai.com/api/docs/guides/prompt-caching>


<span id="s-RETRIEVAL"></span>



<span id="topic-31"></span>


## RETRIEVAL · 上下文检索

检索可结合稀疏、稠密及重排；本书固定排名与分数是说明融合的算例，不外推测试收益。

<https://www.anthropic.com/engineering/contextual-retrieval>


<span id="s-LSP"></span>



<span id="topic-32"></span>


## LSP · Language Server Protocol

语言工具提供定义、引用等结构线索；动态调用和版本一致性仍须核验。

<https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/>


<span id="s-MEMORY"></span>



<span id="topic-33"></span>


## MEMORY · CoALA 认知架构

以记忆、动作和决策区分Agent组件。双时间与失效表是本书工程示例，不是所有框架的固定实现。

<https://arxiv.org/abs/2309.02427>


<span id="s-SKILLS"></span>



<span id="topic-34"></span>


## SKILLS · Agent Skills 规范

元数据、正文和资源有不同加载角色。技能文件存在不等于当前请求已加载并正确应用。

<https://agentskills.io/specification>


<span id="s-MULTI"></span>



<span id="topic-35"></span>


## MULTI · 多Agent研究系统工程

任务可并行性、委派和整合决定收益；图中的时间不是产品实测。

<https://www.anthropic.com/engineering/multi-agent-research-system>


<span id="s-TEST"></span>



<span id="topic-36"></span>


## TEST · 代码审查标准

审查设计、功能、复杂性与测试。当前版本的实际验证证据不能由叙述替代。

<https://google.github.io/eng-practices/review/reviewer/looking-for.html>


<span id="s-EVAL"></span>



<span id="topic-37"></span>


## EVAL · Agent评测

结果、过程、稳定性和评分方式应区别评估；教学任务计数不代表商业模型胜率。

<https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>


<span id="s-SECURITY"></span>



<span id="topic-38"></span>


## SECURITY · Agent 安全与控制

用隔离与权限约束执行边界。动画仅展示威胁路径，不代表完成生产安全审计。

<https://www.anthropic.com/engineering/claude-code-sandboxing>


<span id="s-TRACE"></span>



<span id="topic-39"></span>


## TRACE · OpenTelemetry Trace

嵌套与并行操作通过Trace观察；Span耗时相加不一定是用户的等待时长。

<https://opentelemetry.io/docs/concepts/signals/traces/>


<span id="s-VISION"></span>



<span id="topic-40"></span>


## VISION · 视觉Transformer

图像块进入数值表示的一种架构；图中小图切块不规定所有多模态产品的视觉Token算法。

<https://arxiv.org/abs/2010.11929>