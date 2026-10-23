---
title: "运行示例：依据、参数与范围"
description: "AI系统工程：本地教学正文与可追溯图表"
---

AI系统工程 · 运行示例

# 运行示例：依据、参数与范围

原始机制与本书教学数据分开记录。中文讲解已经包含学习所需内容，外部资料仅用于追溯。

核对日期：2026年10月18日。数学例按显示的公式、输入和参数计算；产品特征按所列官方文档或固定快照说明。没有把构造的调用记录、性能数字、检索语料或评测样本当成真实产品结果。


<span id="ex-src-DERIVE"></span>



<span id="topic-1"></span>


## DERIVE · 独立教学推导与场景设定

本书明确指定输入、权重、概率或业务状态，展示由这些前提推出的结果。不是论文实验数据，也不代表某个商业模型的实际运行。程序见本地“示例核验”。


<span id="ex-src-EMBED"></span>



<span id="topic-2"></span>


## EMBED · PyTorch Embedding：整数索引与参数表

索引形状保持，输出新增embedding\_dim轴。查表不同于二进制展开。

[原始依据（可选核对）](https://docs.pytorch.org/docs/2.14/generated/torch.nn.Embedding.html)  
https://docs.pytorch.org/docs/2.14/generated/torch.nn.Embedding.html


<span id="ex-src-LN"></span>



<span id="topic-3"></span>


## LN · PyTorch LayerNorm：逐归一化维的均值与方差

数值例明确ε、缩放和偏置；方差采用总体方差口径。RMSNorm对照另按正文公式手算。

[原始依据（可选核对）](https://docs.pytorch.org/docs/2.14/generated/torch.nn.LayerNorm.html)  
https://docs.pytorch.org/docs/2.14/generated/torch.nn.LayerNorm.html


<span id="ex-src-GLU"></span>



<span id="topic-4"></span>


## GLU · GLU Variants Improve Transformer

门控变体的原始研究；正文SiLU与乘法门控均使用明确的人为输入与投影。

[原始依据（可选核对）](https://arxiv.org/abs/2002.05202)  
https://arxiv.org/abs/2002.05202


<span id="ex-src-SDPA"></span>



<span id="topic-5"></span>


## SDPA · PyTorch scaled\_dot\_product\_attention

注意布尔掩码True表示允许参与；与MultiheadAttention接口不能混用。教材不默认非方阵is\_causal一定适合带缓存解码。

[原始依据（可选核对）](https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.scaled_dot_product_attention.html)  
https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.scaled\_dot\_product\_attention.html


<span id="ex-src-MHA"></span>



<span id="topic-6"></span>


## MHA · PyTorch MultiheadAttention

attn\_mask布尔True表示不允许访问。以该版本文档为范围。

[原始依据（可选核对）](https://docs.pytorch.org/docs/2.14/generated/torch.nn.MultiheadAttention.html)  
https://docs.pytorch.org/docs/2.14/generated/torch.nn.MultiheadAttention.html


<span id="ex-src-CE"></span>



<span id="topic-7"></span>


## CE · PyTorch CrossEntropyLoss

标签、ignore\_index、权重及reduction共同决定损失与分母；本书例子明确是否加权。

[原始依据（可选核对）](https://docs.pytorch.org/docs/2.14/generated/torch.nn.CrossEntropyLoss.html)  
https://docs.pytorch.org/docs/2.14/generated/torch.nn.CrossEntropyLoss.html


<span id="ex-src-ADAMW"></span>



<span id="topic-8"></span>


## ADAMW · PyTorch AdamW

一二阶矩、偏差校正与解耦权重衰减的具体算式。

[原始依据（可选核对）](https://docs.pytorch.org/docs/2.14/generated/torch.optim.AdamW.html)  
https://docs.pytorch.org/docs/2.14/generated/torch.optim.AdamW.html


<span id="ex-src-CACHE"></span>



<span id="topic-9"></span>


## CACHE · Transformers：缓存机制

逐层缓存、过去位置与新查询的关系。简化缓存公式不包括分配器和临时张量。

[原始依据（可选核对）](https://huggingface.co/docs/transformers/cache_explanation)  
https://huggingface.co/docs/transformers/cache\_explanation


<span id="ex-src-ZERO"></span>



<span id="topic-10"></span>


## ZERO · ZeRO：分摊模型训练状态

三类状态与阶段划分来自原始研究；1000参数例为教学记账，不引用论文性能数字。

[原始依据（可选核对）](https://arxiv.org/abs/1910.02054)  
https://arxiv.org/abs/1910.02054


<span id="ex-src-TOOLS"></span>



<span id="topic-11"></span>


## TOOLS · OpenAI Function calling

模型提议、宿主执行、调用标识与结果回传。例中伪协议不替代当前API完整schema。

[原始依据（可选核对）](https://developers.openai.com/api/docs/guides/function-calling)  
https://developers.openai.com/api/docs/guides/function-calling


<span id="ex-src-COMPACT"></span>



<span id="topic-12"></span>


## COMPACT · OpenAI Compaction

压缩接口与状态续接；本书可读摘要示例不能被理解为所有服务端压缩都返回同样文本。

[原始依据（可选核对）](https://developers.openai.com/api/docs/guides/compaction)  
https://developers.openai.com/api/docs/guides/compaction


<span id="ex-src-CONTEXT"></span>



<span id="topic-13"></span>


## CONTEXT · Anthropic：上下文工程

上下文选择、裁剪、压缩与长任务。数字预算与保真案例为自编。

[原始依据（可选核对）](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)  
https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents


<span id="ex-src-CLAUDE"></span>



<span id="topic-14"></span>


## CLAUDE · Claude Code公开运行说明

仅讨论公开机制，不推断未公开提示词、阈值或模型内部。

[原始依据（可选核对）](https://code.claude.com/docs/en/how-claude-code-works)  
https://code.claude.com/docs/en/how-claude-code-works


<span id="ex-src-CLAUDE-SUB"></span>



<span id="topic-15"></span>


## CLAUDE-SUB · Claude Code子Agent

上下文、工具和委派边界需按具体配置核查，不能假定无限继承。

[原始依据（可选核对）](https://code.claude.com/docs/en/sub-agents)  
https://code.claude.com/docs/en/sub-agents


<span id="ex-src-COPILOT"></span>



<span id="topic-16"></span>


## COPILOT · GitHub Copilot CLI公开说明

产品行为可能随版本变化；三产品比较示例是验证方法，不伪造实测排名。

[原始依据（可选核对）](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-cli)  
https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-cli


<span id="ex-src-CODEX"></span>



<span id="topic-17"></span>


## CODEX · Codex固定源码快照：工具路由

固定提交ce0323f2f2d3b25e82806cd555237da3db4e1897。注册、模型可见与运行时分派是不同环节。压缩流程还参看同提交compact.rs及本书源码专题。不是对最新main的声明。

[原始依据（可选核对）](https://github.com/openai/codex/blob/ce0323f2f2d3b25e82806cd555237da3db4e1897/codex-rs/core/src/tools/router.rs)  
https://github.com/openai/codex/blob/ce0323f2f2d3b25e82806cd555237da3db4e1897/codex-rs/core/src/tools/router.rs


<span id="ex-src-MCP-LIFE"></span>



<span id="topic-18"></span>


## MCP-LIFE · MCP 2025-06-18：生命周期

initialize、能力协商和initialized；示例遵循固定协议版，兼容性以实际双方声明为准。

[原始依据（可选核对）](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)  
https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle


<span id="ex-src-MCP-TOOLS"></span>



<span id="topic-19"></span>


## MCP-TOOLS · MCP 2025-06-18：工具

工具发现、调用与结果；发现不等于执行权限，也不等于业务批准。

[原始依据（可选核对）](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)  
https://modelcontextprotocol.io/specification/2025-06-18/server/tools


<span id="ex-src-SSE"></span>



<span id="topic-20"></span>


## SSE · WHATWG：Server-sent events

字节、UTF-8、行与事件分别处理。教学解析器声明只覆盖LF子集，不声称是完整标准实现。

[原始依据（可选核对）](https://html.spec.whatwg.org/multipage/server-sent-events.html)  
https://html.spec.whatwg.org/multipage/server-sent-events.html


<span id="ex-src-BM25"></span>



<span id="topic-21"></span>


## BM25 · Stanford信息检索教材：BM25

正文明确采用非负IDF变体ln(1+(N−df+0.5)/(df+0.5))，而非把所有实现的IDF视为相同。

[原始依据（可选核对）](https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html)  
https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html


<span id="ex-src-RRF"></span>



<span id="topic-22"></span>


## RRF · Elasticsearch：RRF

排名融合按位置求和；本书明确排名从1开始、常数60以及每列表去重。

[原始依据（可选核对）](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)  
https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion


<span id="ex-src-HNSW"></span>



<span id="topic-23"></span>


## HNSW · HNSW原始研究

图搜索是近似检索的一种。三个点的贪心反例只解释探索局限，不模拟完整多层图算法。

[原始依据（可选核对）](https://arxiv.org/abs/1603.09320)  
https://arxiv.org/abs/1603.09320


<span id="ex-src-DPO"></span>



<span id="topic-24"></span>


## DPO · Direct Preference Optimization

本书用两候选概率手算目标差，不把候选概率或loss当作实际训练提升。

[原始依据（可选核对）](https://arxiv.org/abs/2305.18290)  
https://arxiv.org/abs/2305.18290


<span id="ex-src-PPO"></span>



<span id="topic-25"></span>


## PPO · Proximal Policy Optimization

正负advantage下的裁剪目标；数字是本书构造的单步例子。

[原始依据（可选核对）](https://arxiv.org/abs/1707.06347)  
https://arxiv.org/abs/1707.06347


<span id="ex-src-SPEC"></span>



<span id="topic-26"></span>


## SPEC · Fast Inference from Transformers via Speculative Decoding

接受概率与拒绝残差分布；单步离散分布用于证明不能拒绝后直接照原分布重抽。

[原始依据（可选核对）](https://arxiv.org/abs/2211.17192)  
https://arxiv.org/abs/2211.17192


<span id="ex-src-FLASH"></span>



<span id="topic-27"></span>


## FLASH · FlashAttention

分块与在线归一化的思想；CPU标准库数值见证不证明GPU性能。

[原始依据（可选核对）](https://arxiv.org/abs/2205.14135)  
https://arxiv.org/abs/2205.14135


<span id="ex-src-PAGED"></span>



<span id="topic-28"></span>


## PAGED · PagedAttention / vLLM

分页与KV缓存的映射；页面编号和token数都是教学设定。

[原始依据（可选核对）](https://arxiv.org/abs/2309.06180)  
https://arxiv.org/abs/2309.06180


<span id="ex-src-SQLITE"></span>



<span id="topic-29"></span>


## SQLITE · SQLite事务

数据库事务不自动包住外部工具和文件副作用。

[原始依据（可选核对）](https://sqlite.org/lang_transaction.html)  
https://sqlite.org/lang\_transaction.html


<span id="ex-src-OS"></span>



<span id="topic-30"></span>


## OS · Python os.replace

同文件系统中成功替换的原子性，不等于跨文件数据库事务、耐久性保证或比较后写入。

[原始依据（可选核对）](https://docs.python.org/3/library/os.html#os.replace)  
https://docs.python.org/3/library/os.html#os.replace


<span id="ex-src-SKILLS"></span>



<span id="topic-31"></span>


## SKILLS · Agent Skills开放规范

元数据、正文、资源及渐进加载；项目路由质量需真实任务检验。

[原始依据（可选核对）](https://agentskills.io/specification)  
https://agentskills.io/specification


<span id="ex-src-EVALS"></span>



<span id="topic-32"></span>


## EVALS · Anthropic：Agent评测

任务、轨迹、判分与可靠性需区分；本书分母和统计数字都是构造例。

[原始依据（可选核对）](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)  
https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents


<span id="ex-src-AWQ"></span>



<span id="topic-33"></span>


## AWQ · Activation-aware Weight Quantization

激活影响权重误差向输出传播的大小；局部误差例不等于论文量化实现或基准成绩。

[原始依据（可选核对）](https://arxiv.org/abs/2306.00978)  
https://arxiv.org/abs/2306.00978

AI系统工程：从基础到内部 · [首页](index.md) · [示例索引](worked-examples.md) · [依据与范围](example-sources.md)