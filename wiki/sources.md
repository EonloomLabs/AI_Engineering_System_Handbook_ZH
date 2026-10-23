---
title: "参考资料与适用范围"
description: "AI系统工程：本地教学正文与可追溯图表"
---

阅读指南与附录


<span id="section-0"></span>


# 参考资料与适用范围

以下出处支持正文中注明范围内的机制。中文讲解、推导和示例已在本地展开，链接用于追溯，不是必读的外部步骤。


<span id="section-1"></span>


### 如何区分三类材料

研究与官方文档说明公开事实；独立手算与构造案例用于解释机制；程序运行记录对应指定数据和断言。教学数值不代表商业模型参数，确定性测试不代表真实Agent成功率。产品与协议说明应与所列版本对应。


<span id="src-TR"></span>



<span id="section-2"></span>


### [TR] Attention Is All You Need

Transformer原始架构与注意力；现代Decoder变体另作说明。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/html/1706.03762v7)


<span id="src-CHAT"></span>



<span id="section-3"></span>


### [CHAT] Hugging Face：Chat templates

消息序列化与模型模板；不等于闭源产品完整Prompt。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://huggingface.co/docs/transformers/chat_templating)


<span id="src-BPE"></span>



<span id="section-4"></span>


### [BPE] Hugging Face：Byte-Pair Encoding tokenization

BPE训练与编码机制；本书字符串例子为原创教学数据。

官方教程 · 资料记录日期：2026-10-17

[来源出处](https://huggingface.co/learn/llm-course/chapter6/5)


<span id="src-UNIGRAM"></span>



<span id="section-5"></span>


### [UNIGRAM] Subword Regularization

Unigram子词模型与分词方案；不声称所有Tokenizer使用同一算法。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/1804.10959)


<span id="src-ROPE"></span>



<span id="section-6"></span>


### [ROPE] RoFormer: Enhanced Transformer with Rotary Position Embedding

旋转位置表示与相对位置关系。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2104.09864)


<span id="src-GQA"></span>



<span id="section-7"></span>


### [GQA] GQA: Training Generalized Multi-Query Transformer Models

Query分组与KV共享；缓存算例为本书独立计算。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2305.13245)


<span id="src-CACHE"></span>



<span id="section-8"></span>


### [CACHE] Hugging Face：KV cache strategies

缓存类别与使用条件；具体形状和位置须按模型实现。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://huggingface.co/docs/transformers/kv_cache)


<span id="src-FLASH"></span>



<span id="section-9"></span>


### [FLASH] FlashAttention: Fast and Memory-Efficient Exact Attention

分块、IO优化和在线归一化；不移植论文加速倍率。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2205.14135)


<span id="src-PAGED"></span>



<span id="section-10"></span>


### [PAGED] Efficient Memory Management for LLM Serving with PagedAttention

KV分页管理与共享思想；块号示例为教学构造。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2309.06180)


<span id="src-SPECULATIVE"></span>



<span id="section-11"></span>


### [SPECULATIVE] Fast Inference from Transformers via Speculative Decoding

接受与残差采样机制；不保证相同随机种子输出相同文本。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2211.17192)


<span id="src-RLHF"></span>



<span id="section-12"></span>


### [RLHF] Training language models to follow instructions with human feedback

SFT、奖励模型和偏好优化的基础流程。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2203.02155)


<span id="src-DPO"></span>



<span id="section-13"></span>


### [DPO] Direct Preference Optimization

相对参考模型的偏好目标；公式解释不等于复现训练。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2305.18290)


<span id="src-R1"></span>



<span id="section-14"></span>


### [R1] DeepSeek-R1

强化学习与推理训练；不把某一报告结论泛化到全部模型。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2501.12948)


<span id="src-LORA"></span>



<span id="section-15"></span>


### [LORA] LoRA: Low-Rank Adaptation of Large Language Models

低秩增量与参数高效适配。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2106.09685)


<span id="src-V3"></span>



<span id="section-16"></span>


### [V3] DeepSeek-V3 Technical Report v2

MLA、MoE与相关架构；仅解释所用机制，不声称复现报告全部实验。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/html/2412.19437v2)


<span id="src-CODEX"></span>



<span id="section-17"></span>


### [CODEX] Unrolling the Codex agent loop

模型调用、工具反馈与上下文；历史架构文章与固定源码分开引用。

官方工程文章 · 资料记录日期：2026-10-17

[来源出处](https://openai.com/index/unrolling-the-codex-agent-loop/)


<span id="src-CODEX-SRC"></span>



<span id="section-18"></span>


### [CODEX-SRC] Codex固定源码：工具路由与压缩

读取router.rs 80–220、252–407与compact.rs 270–451；未编译或审计整个Codex。

源码快照 · 资料记录日期：2026-10-17

[来源出处](https://github.com/openai/codex/tree/ce0323f2f2d3b25e82806cd555237da3db4e1897)


<span id="src-TOOLS"></span>



<span id="section-19"></span>


### [TOOLS] OpenAI：Function calling

工具调用与结果回填；教学JSON不是逐字段API参考。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://developers.openai.com/api/docs/guides/function-calling)


<span id="src-COMPACT"></span>



<span id="section-20"></span>


### [COMPACT] OpenAI：Compaction

压缩与不透明状态的接口边界；不推测内部编码。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://developers.openai.com/api/docs/guides/compaction)


<span id="src-PCACHE"></span>



<span id="section-21"></span>


### [PCACHE] OpenAI：Prompt caching

重复前缀复用；规则会变化，正文不固定价格或保留期。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://developers.openai.com/api/docs/guides/prompt-caching)


<span id="src-CLAUDE"></span>



<span id="section-22"></span>


### [CLAUDE] How Claude Code works

公开运行、工具和上下文机制；闭源内部实现不作补造。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://code.claude.com/docs/en/how-claude-code-works)


<span id="src-COPILOT"></span>



<span id="section-23"></span>


### [COPILOT] About custom agents for GitHub Copilot CLI

CLI自定义Agent；不推广到全部IDE和云端形态。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents)


<span id="src-CONTEXT"></span>



<span id="section-24"></span>


### [CONTEXT] Effective context engineering for AI agents

选择、卸载、摘要与长任务；状态结构和例子由本书设计。

官方工程文章 · 资料记录日期：2026-10-17

[来源出处](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)


<span id="src-CTXRETRIEVAL"></span>



<span id="section-25"></span>


### [CTXRETRIEVAL] Introducing Contextual Retrieval

上下文增强检索与组合检索；不声称本书取得论文或文章收益。

官方工程文章 · 资料记录日期：2026-10-17

[来源出处](https://www.anthropic.com/engineering/contextual-retrieval)


<span id="src-MCP"></span>



<span id="section-26"></span>


### [MCP] MCP Architecture overview

Host、Client、Server职责；协议时序使用单独固定版规范。

协议文档 · 资料记录日期：2026-10-17

[来源出处](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)


<span id="src-MCP-LIFE"></span>



<span id="section-27"></span>


### [MCP-LIFE] MCP Lifecycle，2025-11-25

初始化、能力协商、版本与会话生命周期。

固定版本规范 · 资料记录日期：2026-10-17

[来源出处](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)


<span id="src-MCP-TOOLS"></span>



<span id="section-28"></span>


### [MCP-TOOLS] MCP Tools，2025-11-25

工具发现、分页、调用与错误层次。

固定版本规范 · 资料记录日期：2026-10-17

[来源出处](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)


<span id="src-SKILLS"></span>



<span id="section-29"></span>


### [SKILLS] Agent Skills specification

技能文件、元数据与按需资源；格式存在不代表路由效果保证。

规范 · 资料记录日期：2026-10-17

[来源出处](https://agentskills.io/specification)


<span id="src-SUBAGENTS"></span>



<span id="section-30"></span>


### [SUBAGENTS] Claude Code：Subagents

独立上下文与工具配置；权限行为需要按版本确认。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://code.claude.com/docs/en/sub-agents)


<span id="src-CLAUDEMEM"></span>



<span id="section-31"></span>


### [CLAUDEMEM] Claude Code：Memory

项目指引与记忆机制；不等于在线参数更新。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://code.claude.com/docs/en/memory)


<span id="src-COPILOTSKILL"></span>



<span id="section-32"></span>


### [COPILOTSKILL] GitHub Copilot：Agent Skills

Copilot技能概念与加载；不把模型自报当作已执行证明。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)


<span id="src-AGENTS"></span>



<span id="section-33"></span>


### [AGENTS] Building effective agents

工作流、Agent及常见编排模式。

官方工程文章 · 资料记录日期：2026-10-17

[来源出处](https://www.anthropic.com/engineering/building-effective-agents)


<span id="src-LONGHARNESS"></span>



<span id="section-34"></span>


### [LONGHARNESS] Effective harnesses for long-running agents

跨会话长任务、环境与状态连续性。

官方工程文章 · 资料记录日期：2026-10-17

[来源出处](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)


<span id="src-MULTI"></span>



<span id="section-35"></span>


### [MULTI] How we built our multi-agent research system

委派、并行探索与整合；本书DAG数字为教学假设。

官方工程文章 · 资料记录日期：2026-10-17

[来源出处](https://www.anthropic.com/engineering/multi-agent-research-system)


<span id="src-MEMGPT"></span>



<span id="section-36"></span>


### [MEMGPT] MemGPT: Towards LLMs as Operating Systems

分层状态与外部记忆；不是通用最优记忆架构。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2310.08560)


<span id="src-COALA"></span>



<span id="section-37"></span>


### [COALA] Cognitive Architectures for Language Agents

工作、长期、程序性等记忆分类的概念框架。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2309.02427)


<span id="src-LONGMEM"></span>



<span id="section-38"></span>


### [LONGMEM] LongMemEval

长期记忆检索、时间与更新等评测问题；本书未运行该基准。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2410.10813)


<span id="src-DPR"></span>



<span id="section-39"></span>


### [DPR] Dense Passage Retrieval

双编码器与稠密检索训练。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2004.04906)


<span id="src-COLBERT"></span>



<span id="section-40"></span>


### [COLBERT] ColBERT

Late interaction与细粒度匹配。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2004.12832)


<span id="src-HNSW"></span>



<span id="section-41"></span>


### [HNSW] Efficient and robust approximate nearest neighbor search using HNSW

近邻图搜索与搜索宽度取舍；不是语义正确性证明。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/1603.09320)


<span id="src-BM25"></span>



<span id="section-42"></span>


### [BM25] Stanford IR Book：Okapi BM25

BM25机制；正文明确采用正值IDF变体与教学参数。

教材 · 资料记录日期：2026-10-17

[来源出处](https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html)


<span id="src-RRF"></span>



<span id="section-43"></span>


### [RRF] Elasticsearch：Reciprocal rank fusion

基于排名融合；融合分数不是概率。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)


<span id="src-TREESITTER"></span>



<span id="section-44"></span>


### [TREESITTER] Tree-sitter：Using parsers

解析树与结构定位；不代替类型和运行时分析。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://tree-sitter.github.io/tree-sitter/using-parsers/)


<span id="src-LSP"></span>



<span id="section-45"></span>


### [LSP] Language Server Protocol 3.17

定义、引用、文档版本与诊断的协议边界。

固定版本规范 · 资料记录日期：2026-10-17

[来源出处](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/)


<span id="src-SWEBENCH"></span>



<span id="section-46"></span>


### [SWEBENCH] SWE-bench

真实仓库问题的测试式评价；未运行基准。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2310.06770)


<span id="src-OTEL"></span>



<span id="section-47"></span>


### [OTEL] OpenTelemetry：GenAI agent and framework spans

GenAI约定已迁移；部分为Development。正文使用概念，不固定全部属性名。

规范文档 · 资料记录日期：2026-10-17

[来源出处](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)


<span id="src-GENERATION"></span>



<span id="section-48"></span>


### [GENERATION] Hugging Face：Generation strategies

生成与解码策略。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://huggingface.co/docs/transformers/generation_strategies)


<span id="src-SPEC"></span>



<span id="section-49"></span>


### [SPEC] OpenAI Model Spec，2025-12-18

用于指令层级与来源边界，不声称是最新完整产品实现。

固定版本说明 · 资料记录日期：2026-10-17

[来源出处](https://model-spec.openai.com/2025-12-18.html)


<span id="src-REASON"></span>



<span id="section-50"></span>


### [REASON] OpenAI：Reasoning models

推理输出、预算和状态接口；不访问或伪造隐藏思维链。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://developers.openai.com/api/docs/guides/reasoning)


<span id="src-STRUCTURED"></span>



<span id="section-51"></span>


### [STRUCTURED] OpenAI：Structured outputs

结构约束、拒绝和不完整结果；结构正确不等于事实正确。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://developers.openai.com/api/docs/guides/structured-outputs)


<span id="src-STREAM"></span>



<span id="section-52"></span>


### [STREAM] OpenAI：Streaming responses

增量事件与响应状态；按当前接口处理。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://developers.openai.com/api/docs/guides/streaming-responses)


<span id="src-SSE"></span>



<span id="section-53"></span>


### [SSE] WHATWG HTML：Server-sent events

事件流与解析边界；包内LF示例解析器不是完整标准实现。

标准 · 资料记录日期：2026-10-17

[来源出处](https://html.spec.whatwg.org/multipage/server-sent-events.html)


<span id="src-ADAMW"></span>



<span id="section-54"></span>


### [ADAMW] Decoupled Weight Decay Regularization

权重衰减与优化器更新的区别。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/1711.05101)


<span id="src-CHINCHILLA"></span>



<span id="section-55"></span>


### [CHINCHILLA] Training Compute-Optimal Large Language Models

计算预算下的规模与数据分配；不固定普适比例。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2203.15556)


<span id="src-QLORA"></span>



<span id="section-56"></span>


### [QLORA] QLoRA

量化基础上的参数高效微调。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2305.14314)


<span id="src-REACT"></span>



<span id="section-57"></span>


### [REACT] ReAct: Synergizing Reasoning and Acting

推理、动作与观察的交替。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2210.03629)


<span id="src-LOST"></span>



<span id="section-58"></span>


### [LOST] Lost in the Middle

特定模型与任务中的长上下文位置效应，不是所有模型恒定规律。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2307.03172)


<span id="src-HYDE"></span>



<span id="section-59"></span>


### [HYDE] Precise Zero-Shot Dense Retrieval without Relevance Labels

用假设文档辅助检索；生成文本不是事实证据。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2212.10496)


<span id="src-RAPTOR"></span>



<span id="section-60"></span>


### [RAPTOR] RAPTOR

分层摘要检索。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2401.18059)


<span id="src-GRAPHRAG"></span>



<span id="section-61"></span>


### [GRAPHRAG] From Local to Global: A Graph RAG Approach

图与社区摘要支持跨文档问题；不是所有代码检索默认选项。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2404.16130)


<span id="src-SELFRAG"></span>



<span id="section-62"></span>


### [SELFRAG] Self-RAG

检索、生成与反思机制及训练；不是简单多写一句自检提示。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2310.11511)


<span id="src-CRAG"></span>



<span id="section-63"></span>


### [CRAG] Corrective Retrieval Augmented Generation

检索质量评估与纠正策略。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2401.15884)


<span id="src-TP"></span>



<span id="section-64"></span>


### [TP] PyTorch：Tensor Parallel tutorial

矩阵分片与通信；收益依赖硬件和并行规模。

官方教程 · 资料记录日期：2026-10-17

[来源出处](https://docs.pytorch.org/tutorials/intermediate/TP_tutorial.html)


<span id="src-ZERO"></span>



<span id="section-65"></span>


### [ZERO] ZeRO: Memory Optimizations Toward Training Trillion Parameter Models

优化器状态、梯度和参数分片。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/1910.02054)


<span id="src-SRE"></span>



<span id="section-66"></span>


### [SRE] Google SRE：Monitoring Distributed Systems

监控、延迟与系统运行指标。

工程教材 · 资料记录日期：2026-10-17

[来源出处](https://sre.google/sre-book/monitoring-distributed-systems/)


<span id="src-SLO"></span>



<span id="section-67"></span>


### [SLO] Google SRE Workbook：Implementing SLOs

面向用户目标的可靠性设计。

工程教材 · 资料记录日期：2026-10-17

[来源出处](https://sre.google/workbook/implementing-slos/)


<span id="src-IDEMPOTENT"></span>



<span id="section-68"></span>


### [IDEMPOTENT] AWS Builders Library：Making retries safe with idempotent APIs

幂等键、重试与意图边界；不推导本地表等于分布式原子性。

官方工程文章 · 资料记录日期：2026-10-17

[来源出处](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)


<span id="src-SQLITE"></span>



<span id="section-69"></span>


### [SQLITE] SQLite：Isolation

数据库事务与隔离；不扩展为数据库外副作用事务。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://www.sqlite.org/isolation.html)


<span id="src-LATENCY"></span>



<span id="section-70"></span>


### [LATENCY] OpenAI：Latency optimization

调用数量、Token和并行的延迟取舍。

官方文档 · 资料记录日期：2026-10-17

[来源出处](https://developers.openai.com/api/docs/guides/latency-optimization)


<span id="src-SANDBOX"></span>



<span id="section-71"></span>


### [SANDBOX] Beyond permission prompts: Claude Code sandboxing

文件系统和网络边界；本书不宣称完成安全审计。

官方工程文章 · 资料记录日期：2026-10-17

[来源出处](https://www.anthropic.com/engineering/claude-code-sandboxing)


<span id="src-A2A"></span>



<span id="section-72"></span>


### [A2A] Agent2Agent Protocol specification

跨Agent任务与通信；不自动赋予权限或业务一致性。

协议文档 · 资料记录日期：2026-10-17

[来源出处](https://a2a-protocol.org/latest/specification/)


<span id="src-JUDGE"></span>



<span id="section-73"></span>


### [JUDGE] Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena

模型评分的偏差与评价问题。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2306.05685)


<span id="src-HUMANEVAL"></span>



<span id="section-74"></span>


### [HUMANEVAL] Evaluating Large Language Models Trained on Code

代码评价与pass@k估计；数值由本书独立计算。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2107.03374)


<span id="src-TAU"></span>



<span id="section-75"></span>


### [TAU] τ-bench

多次运行可靠性和工具任务评价。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2406.12045)


<span id="src-EVALS"></span>



<span id="section-76"></span>


### [EVALS] Demystifying evals for AI agents

任务、试验、轨迹、评分和回归；本书不声称运行商业模型评测。

官方工程文章 · 资料记录日期：2026-10-17

[来源出处](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)


<span id="src-REVIEW"></span>



<span id="section-77"></span>


### [REVIEW] Google Engineering Practices：The Standard of Code Review

代码健康、适度审查和改进标准。

工程规范 · 资料记录日期：2026-10-17

[来源出处](https://google.github.io/eng-practices/review/reviewer/standard.html)


<span id="src-OWASP"></span>



<span id="section-78"></span>


### [OWASP] OWASP LLM01：Prompt Injection

不可信内容、间接注入与边界；不是安全认证。

安全资料 · 资料记录日期：2026-10-17

[来源出处](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)


<span id="src-HIERARCHY"></span>



<span id="section-79"></span>


### [HIERARCHY] The Instruction Hierarchy

训练模型区分不同权威级别；模型行为不能替代执行权限。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2404.13208)


<span id="src-SCALING"></span>



<span id="section-80"></span>


### [SCALING] Scaling Laws for Neural Language Models

规模、数据和计算关系；数学例子标明假设。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2001.08361)


<span id="src-GPT3"></span>



<span id="section-81"></span>


### [GPT3] Language Models are Few-Shot Learners

上下文任务适应，与梯度更新区分。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2005.14165)


<span id="src-CALIBRATION"></span>



<span id="section-82"></span>


### [CALIBRATION] Language Models (Mostly) Know What They Know

特定条件下自评与校准；不能推广为通用可靠置信度。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2207.05221)


<span id="src-TRUTHQA"></span>



<span id="section-83"></span>


### [TRUTHQA] TruthfulQA

真实性与模仿错误信念的评测问题。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2109.07958)


<span id="src-CLIP"></span>



<span id="section-84"></span>


### [CLIP] Learning Transferable Visual Models From Natural Language Supervision

图文对比学习；不等同完整生成式多模态聊天系统。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2103.00020)


<span id="src-OSWORLD"></span>



<span id="section-85"></span>


### [OSWORLD] OSWorld

真实桌面环境中的多模态Agent评价；本书未运行基准。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2404.07972)


<span id="src-SAE"></span>



<span id="section-86"></span>


### [SAE] Scaling and evaluating sparse autoencoders

稀疏特征、重构与解释局限。

论文 · 资料记录日期：2026-10-17

[来源出处](https://arxiv.org/abs/2406.04093)


<span id="src-HARNESS"></span>



<span id="section-87"></span>


### [HARNESS] Harness engineering: leveraging Codex in an agent-first world

仓库知识、环境反馈与工程约束；本文蓝图为独立教学设计。

官方工程文章 · 资料记录日期：2026-10-17

[来源出处](https://openai.com/index/harness-engineering/)


<span id="src-F-TENSOR"></span>



<span id="section-88"></span>


### [F-TENSOR] PyTorch：Tensors

张量的shape、dtype、device与基本运算；本书二维三维数表为原创教学例。

一手教材／官方文档 · 资料记录日期：2026-10-17

[来源出处](https://docs.pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html)


<span id="src-F-EMBED"></span>



<span id="section-89"></span>


### [F-EMBED] PyTorch：Embedding

按整数索引取参数表行；输入形状后追加embedding\_dim。教学表不来自预训练模型。

一手教材／官方文档 · 资料记录日期：2026-10-17

[来源出处](https://docs.pytorch.org/docs/2.14/generated/torch.nn.modules.sparse.Embedding.html)


<span id="src-F-PADDING"></span>



<span id="section-90"></span>


### [F-PADDING] Hugging Face：Padding and truncation

批输入补齐、截断及模型相关配置；本书右补齐演示需取末个有效位置。

一手教材／官方文档 · 资料记录日期：2026-10-17

[来源出处](https://huggingface.co/docs/transformers/main/en/pad_truncation)


<span id="src-F-CACHE"></span>



<span id="section-91"></span>


### [F-CACHE] Hugging Face：How caching works

因果条件下逐层K/V复用与历史加新Token的长度关系。具体mask按实际实现核对。

一手教材／官方文档 · 资料记录日期：2026-10-17

[来源出处](https://huggingface.co/docs/transformers/cache_explanation)


<span id="src-F-LINALG"></span>



<span id="section-92"></span>


### [F-LINALG] 动手学深度学习：Linear Algebra

向量矩阵、点积、矩阵乘法及相关基础；数字推导独立编写。

一手教材／官方文档 · 资料记录日期：2026-10-17

[来源出处](https://d2l.ai/chapter_preliminaries/linear-algebra.html)


<span id="src-F-PROB"></span>



<span id="section-93"></span>


### [F-PROB] 动手学深度学习：Probability and Statistics

概率、随机变量、期望等基础；不照搬原文教学例。

一手教材／官方文档 · 资料记录日期：2026-10-17

[来源出处](https://d2l.ai/chapter_preliminaries/probability.html)


<span id="src-F-CALC"></span>



<span id="section-94"></span>


### [F-CALC] 动手学深度学习：Calculus

导数、偏导与链式法则；本书标量训练手算独立构造。

一手教材／官方文档 · 资料记录日期：2026-10-17

[来源出处](https://d2l.ai/chapter_preliminaries/calculus.html)


<span id="src-F-AUTOGRAD"></span>



<span id="section-95"></span>


### [F-AUTOGRAD] PyTorch：Automatic Differentiation

前向计算图、梯度和反向传播；标准库实验不调用autograd。

一手教材／官方文档 · 资料记录日期：2026-10-17

[来源出处](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)


<span id="src-F-IR"></span>



<span id="section-96"></span>


### [F-IR] Stanford IR Book：Evaluation of Ranked Retrieval Results

排序检索评价、Precision/Recall及指标边界；不要将其替代回答正确性。

一手教材／官方文档 · 资料记录日期：2026-10-17

[来源出处](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)

AI系统工程：从基础到内部  
[全书目录](contents.md) · [术语与符号](glossary.md) · [参考资料](sources.md)