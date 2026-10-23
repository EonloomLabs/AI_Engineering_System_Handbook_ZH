---
title: "来源、版本与事实边界"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# 来源、版本与事实边界

中文正文由机制说明、独立推导、原创实现和案例组成，不以英文链接代替讲解。下列80项记录用于来源追溯；点击正文N编号会到达本页。外部链接只用于核对，不是离线学习的前置条件。

“相关原文核查”表示核查了本书所用机制及相关部分，不表示逐字校勘全部附录、复现所有实验或持续监控最新版本。N95仅摘要核查。原拓展阅读的194项来源另行保留，不计入本轮80项。


<span id="N01"></span>



<span id="section-1"></span>


## N01 · Codex Agent Loop：模型、上下文与工具循环

官方工程文章 相关原文核查

**本书使用范围：**调用循环与输入边界；不是完整服务端实现

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://openai.com/index/unrolling-the-codex-agent-loop/>

本地相关章节：[01](chapters/01.md) / [06](chapters/06.md) / [07](chapters/07.md) / [08](chapters/08.md) / [09](chapters/09.md)


<span id="N02"></span>



<span id="section-2"></span>


## N02 · Codex project\_doc.rs：项目规则发现与预算

固定提交源码 相关原文核查

**本书使用范围：**规则候选优先级、目录顺序、字节预算；源码阅读，未运行Rust测试

核查日期：2026-10-17｜版本：99f47d6e9a3546c14c43af99c7a58fa6bd130548

外部原始出处（可选）：<https://raw.githubusercontent.com/openai/codex/99f47d6e9a3546c14c43af99c7a58fa6bd130548/codex-rs/core/src/project_doc.rs>

本地相关章节：[09](chapters/09.md)


<span id="N03"></span>



<span id="section-3"></span>


## N03 · Codex codex.rs：初始上下文与run\_turn

固定提交源码 相关原文核查

**本书使用范围：**build\_initial\_context、run\_turn相关路径；未编译或运行Codex

核查日期：2026-10-17｜版本：99f47d6e9a3546c14c43af99c7a58fa6bd130548

外部原始出处（可选）：<https://raw.githubusercontent.com/openai/codex/99f47d6e9a3546c14c43af99c7a58fa6bd130548/codex-rs/core/src/codex.rs>

本地相关章节：[09](chapters/09.md)


<span id="N04"></span>



<span id="section-4"></span>


## N04 · Codex compact.rs：一种本地压缩路径

固定提交源码 相关原文核查

**本书使用范围：**摘要请求、历史重建与用量恢复；不代表全部压缩实现

核查日期：2026-10-17｜版本：99f47d6e9a3546c14c43af99c7a58fa6bd130548

外部原始出处（可选）：<https://raw.githubusercontent.com/openai/codex/99f47d6e9a3546c14c43af99c7a58fa6bd130548/codex-rs/core/src/compact.rs>

本地相关章节：[09](chapters/09.md)


<span id="N05"></span>



<span id="section-5"></span>


## N05 · Codex SSE响应事件转换

固定提交源码 相关原文核查

**本书使用范围：**事件类型、完成与失败；与N02—N04不是同一个快照

核查日期：2026-10-17｜版本：2a68b74b9bf16b64e285495c1b149d7d6ac8bdf4

外部原始出处（可选）：<https://raw.githubusercontent.com/openai/codex/2a68b74b9bf16b64e285495c1b149d7d6ac8bdf4/codex-rs/codex-api/src/sse/responses.rs>

本地相关章节：[07](chapters/07.md) / [09](chapters/09.md)


<span id="N06"></span>



<span id="section-6"></span>


## N06 · OpenAI Compaction：压缩状态与连续会话

官方接口文档 相关原文核查

**本书使用范围：**显式与服务端压缩、压缩项；具体可用性依版本

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://developers.openai.com/api/docs/guides/compaction>

本地相关章节：[07](chapters/07.md) / [09](chapters/09.md) / [12](chapters/12.md)


<span id="N07"></span>



<span id="section-7"></span>


## N07 · Attention Is All You Need

原始论文 相关原文核查

**本书使用范围：**Transformer、注意力与原始encoder-decoder架构；本书梯度推导为独立数学讲解

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/1706.03762>

本地相关章节：[01](chapters/01.md) / [02](chapters/02.md) / [31](chapters/31.md)


<span id="N08"></span>



<span id="section-8"></span>


## N08 · GQA：Grouped-Query Attention

原始论文 相关原文核查

**本书使用范围：**查询头与共享KV头；不复现论文性能数据

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2305.13245>

本地相关章节：[02](chapters/02.md)


<span id="N09"></span>



<span id="section-9"></span>


## N09 · RoFormer：Rotary Position Embedding

原始论文 相关原文核查

**本书使用范围：**旋转位置表示和相对位置关系

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2104.09864>

本地相关章节：[02](chapters/02.md)


<span id="N10"></span>



<span id="section-10"></span>


## N10 · FlashAttention：IO-Aware Exact Attention

原始论文 相关原文核查

**本书使用范围：**分块与在线softmax、I/O效率；CPU教学实现不是CUDA内核

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2205.14135>

本地相关章节：[06](chapters/06.md)


<span id="N11"></span>



<span id="section-11"></span>


## N11 · PagedAttention与vLLM

原始论文 相关原文核查

**本书使用范围：**KV分页管理、共享与服务吞吐；未执行GPU基准

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2309.06180>

本地相关章节：[06](chapters/06.md)


<span id="N12"></span>



<span id="section-12"></span>


## N12 · Speculative Decoding

原始论文 相关原文核查

**本书使用范围：**接受—拒绝与残差采样；仅验证分布，不宣称服务加速

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2211.17192>

本地相关章节：[05](chapters/05.md)


<span id="N13"></span>



<span id="section-13"></span>


## N13 · Hugging Face Chat Templates

官方实现文档 相关原文核查

**本书使用范围：**开放模型的消息序列化与特殊Token；main文档会变化

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://huggingface.co/docs/transformers/main/en/chat_templating>

本地相关章节：[01](chapters/01.md)


<span id="N14"></span>



<span id="section-14"></span>


## N14 · Hugging Face KV Cache Strategies

官方实现文档 相关原文核查

**本书使用范围：**缓存类型与使用约束；不等同长期记忆

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://huggingface.co/docs/transformers/main/en/kv_cache>

本地相关章节：[06](chapters/06.md)


<span id="N15"></span>



<span id="section-15"></span>


## N15 · Direct Preference Optimization

原始论文 相关原文核查

**本书使用范围：**KL正则偏好优化与log-ratio目标

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2305.18290>

本地相关章节：[04](chapters/04.md)


<span id="N16"></span>



<span id="section-16"></span>


## N16 · DeepSeek-R1

模型技术报告 相关原文核查

**本书使用范围：**强化学习、可验证奖励与推理能力；未复现实验

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2501.12948v1>

本地相关章节：[04](chapters/04.md)


<span id="N17"></span>



<span id="section-17"></span>


## N17 · OpenAI Function Calling

官方接口文档 相关原文核查

**本书使用范围：**工具Schema、调用ID、结果反馈；调用意图不等于执行

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://developers.openai.com/api/docs/guides/function-calling>

本地相关章节：[05](chapters/05.md) / [07](chapters/07.md)


<span id="N18"></span>



<span id="section-18"></span>


## N18 · OpenAI Structured Outputs

官方接口文档 相关原文核查

**本书使用范围：**结构约束；不保证字段事实与业务语义

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://developers.openai.com/api/docs/guides/structured-outputs>

本地相关章节：[05](chapters/05.md) / [07](chapters/07.md)


<span id="N19"></span>



<span id="section-19"></span>


## N19 · OpenAI Streaming Responses

官方接口文档 相关原文核查

**本书使用范围：**语义流事件与增量输出；本书SSE子集为教学实现

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://developers.openai.com/api/docs/guides/streaming-responses>

本地相关章节：[05](chapters/05.md) / [07](chapters/07.md)


<span id="N20"></span>



<span id="section-20"></span>


## N20 · How Claude Code Works

官方产品文档 相关原文核查

**本书使用范围：**公开的工具循环、上下文与压缩；未查看闭源内部

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://code.claude.com/docs/en/how-claude-code-works>

本地相关章节：[10](chapters/10.md) / [16](chapters/16.md)


<span id="N21"></span>



<span id="section-21"></span>


## N21 · Claude Code Subagents

官方产品文档 相关原文核查

**本书使用范围：**子Agent配置、上下文和权限边界；依具体版本

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://code.claude.com/docs/en/sub-agents>

本地相关章节：[10](chapters/10.md) / [17](chapters/17.md)


<span id="N22"></span>



<span id="section-22"></span>


## N22 · Copilot CLI Custom Agents

官方产品文档 相关原文核查

**本书使用范围：**CLI自定义Agent、工具配置与委派；不泛化到所有Copilot产品面

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents>

本地相关章节：[10](chapters/10.md) / [16](chapters/16.md) / [17](chapters/17.md)


<span id="N23"></span>



<span id="section-23"></span>


## N23 · Effective Context Engineering for AI Agents

官方工程文章 相关原文核查

**本书使用范围：**上下文选择、外置、摘要与任务状态；本书预算算法为原创示例

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>

本地相关章节：[11](chapters/11.md) / [12](chapters/12.md)


<span id="N24"></span>



<span id="section-24"></span>


## N24 · Contextual Retrieval

官方工程文章 相关原文核查

**本书使用范围：**上下文增强、混合检索与重排；不外推原实验提升比例

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://www.anthropic.com/engineering/contextual-retrieval>

本地相关章节：[13](chapters/13.md) / [28](chapters/28.md)


<span id="N25"></span>



<span id="section-25"></span>


## N25 · Writing Effective Tools for Agents

官方工程文章 相关原文核查

**本书使用范围：**工具语义、输出与评测；工具实现建议需本地验证

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://www.anthropic.com/engineering/writing-tools-for-agents>

本地相关章节：[07](chapters/07.md)


<span id="N26"></span>



<span id="section-26"></span>


## N26 · Multi-Agent Research System

官方工程文章 相关原文核查

**本书使用范围：**并行研究与协调成本；不推导编码任务必然受益

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://www.anthropic.com/engineering/multi-agent-research-system>

本地相关章节：[17](chapters/17.md) / [28](chapters/28.md)


<span id="N27"></span>



<span id="section-27"></span>


## N27 · Agent Skills Specification

开放规范 相关原文核查

**本书使用范围：**技能文件、元数据与渐进披露；具体宿主执行不由格式保证

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://agentskills.io/specification>

本地相关章节：[11](chapters/11.md) / [16](chapters/16.md)


<span id="N28"></span>



<span id="section-28"></span>


## N28 · MCP架构说明，2026-07-28

版本化协议文档 相关原文核查

**本书使用范围：**Host、Client、Server与协议职责

核查日期：2026-10-17｜版本：2026-07-28

外部原始出处（可选）：<https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture>

本地相关章节：[20](chapters/20.md)


<span id="N29"></span>



<span id="section-29"></span>


## N29 · MCP Authorization，2026-07-28

版本化协议规范 相关原文核查

**本书使用范围：**HTTP授权、资源绑定与stdio区别；不是业务ACL的替代

核查日期：2026-10-17｜版本：2026-07-28

外部原始出处（可选）：<https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization>

本地相关章节：[20](chapters/20.md)


<span id="N30"></span>



<span id="section-30"></span>


## N30 · LangGraph Persistence

官方框架文档 相关原文核查

**本书使用范围：**Checkpoint与持久化；框架概念不代替外部副作用幂等性

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://docs.langchain.com/oss/python/langgraph/persistence>

本地相关章节：[08](chapters/08.md)


<span id="N31"></span>



<span id="section-31"></span>


## N31 · SQLite Isolation

官方数据库文档 相关原文核查

**本书使用范围：**事务隔离边界；不覆盖数据库外文件与网络操作

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://www.sqlite.org/isolation.html>

本地相关章节：[08](chapters/08.md)


<span id="N32"></span>



<span id="section-32"></span>


## N32 · Stanford信息检索教材：BM25

学术教材 相关原文核查

**本书使用范围：**词频饱和、长度归一化与检索评分

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html>

本地相关章节：[13](chapters/13.md)


<span id="N33"></span>



<span id="section-33"></span>


## N33 · Faiss索引类型

官方项目文档 相关原文核查

**本书使用范围：**精确检索、HNSW、IVF、PQ的索引选择

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://github.com/facebookresearch/faiss/wiki/Faiss-indexes>

本地相关章节：[13](chapters/13.md)


<span id="N34"></span>



<span id="section-34"></span>


## N34 · LSP 3.17官方元模型

版本化协议定义 相关原文核查

**本书使用范围：**符号、定义、引用等消息与类型；实际能力由语言服务器提供

核查日期：2026-10-17｜版本：3.17

外部原始出处（可选）：<https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/metaModel/metaModel.json>

本地相关章节：[14](chapters/14.md)


<span id="N35"></span>



<span id="section-35"></span>


## N35 · LongMemEval

原始评测论文 相关原文核查

**本书使用范围：**长期交互记忆的测试维度；本书未运行该基准

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2410.10813v1>

本地相关章节：[15](chapters/15.md) / [26](chapters/26.md) / [28](chapters/28.md)


<span id="N36"></span>



<span id="section-36"></span>


## N36 · Demystifying Evals for AI Agents

官方工程文章 相关原文核查

**本书使用范围：**任务、轨迹、判分与真实失败样本；本书统计分析独立编写

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>

本地相关章节：[19](chapters/19.md)


<span id="N37"></span>



<span id="section-37"></span>


## N37 · Chinchilla：Compute-Optimal Language Models

原始论文 相关原文核查

**本书使用范围：**固定训练计算下的模型—数据权衡；不直接给出服务最优方案

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2203.15556>

本地相关章节：[03](chapters/03.md)


<span id="N38"></span>



<span id="section-38"></span>


## N38 · LoRA

原始论文 相关原文核查

**本书使用范围：**低秩增量参数及合并；本书未执行模型微调

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2106.09685>

本地相关章节：[23](chapters/23.md)


<span id="N39"></span>



<span id="section-39"></span>


## N39 · QLoRA

原始论文 相关原文核查

**本书使用范围：**量化基础模型与参数高效微调；未复现硬件结果

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2305.14314>

本地相关章节：[23](chapters/23.md)


<span id="N40"></span>



<span id="section-40"></span>


## N40 · DeepSeek-V3 Technical Report

模型技术报告 相关原文核查

**本书使用范围：**MoE、MLA等机制的设计动机；不代表所有商业模型架构

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2412.19437>

本地相关章节：[26](chapters/26.md)


<span id="N41"></span>



<span id="section-41"></span>


## N41 · CoALA：Cognitive Architectures for Language Agents

原始研究论文 相关原文核查

**本书使用范围：**工作记忆、长期记忆与动作空间的框架

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2309.02427>

本地相关章节：[15](chapters/15.md)


<span id="N42"></span>



<span id="section-42"></span>


## N42 · MemGPT

原始研究论文 相关原文核查

**本书使用范围：**有限上下文与外部记忆的管理；类操作系统比喻的边界

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2310.08560>

本地相关章节：[15](chapters/15.md)


<span id="N43"></span>



<span id="section-43"></span>


## N43 · AWQ

原始论文 相关原文核查

**本书使用范围：**激活感知量化误差；非所有层同等敏感

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2306.00978>

本地相关章节：[23](chapters/23.md)


<span id="N44"></span>



<span id="section-44"></span>


## N44 · OSWorld

原始评测论文 相关原文核查

**本书使用范围：**真实桌面任务与环境评测；本书未运行GUI基准

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2404.07972>

本地相关章节：[24](chapters/24.md) / [26](chapters/26.md)


<span id="N45"></span>



<span id="section-45"></span>


## N45 · Language Models (Mostly) Know What They Know

原始研究论文 相关原文核查

**本书使用范围：**置信度、自我评估与校准的条件；不代表自信必然正确

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2207.05221>

本地相关章节：[25](chapters/25.md)


<span id="N46"></span>



<span id="section-46"></span>


## N46 · GraphRAG：From Local to Global

原始研究论文 相关原文核查

**本书使用范围：**全局问题、社区摘要与图组织；不替代精确代码搜索

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2404.16130>

本地相关章节：[26](chapters/26.md) / [28](chapters/28.md)


<span id="N47"></span>



<span id="section-47"></span>


## N47 · Agentless

原始研究论文 相关原文核查

**本书使用范围：**简单的软件修复流程作为反证基线

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2407.01489v1>

本地相关章节：[17](chapters/17.md) / [28](chapters/28.md)


<span id="N48"></span>



<span id="section-48"></span>


## N48 · τ-bench

原始评测论文 相关原文核查

**本书使用范围：**规则与工具环境下的可靠性、pass^k；本书数学示例不是跑分

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2406.12045v1>

本地相关章节：[19](chapters/19.md) / [26](chapters/26.md)


<span id="N49"></span>



<span id="section-49"></span>


## N49 · Judging LLM-as-a-Judge

原始研究论文 相关原文核查

**本书使用范围：**模型判分的偏差与使用条件

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2306.05685>

本地相关章节：[19](chapters/19.md)


<span id="N50"></span>



<span id="section-50"></span>


## N50 · Google Code Review Standard

一手工程实践 相关原文核查

**本书使用范围：**代码健康度、审查标准与完美主义的边界

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://google.github.io/eng-practices/review/reviewer/standard.html>

本地相关章节：[18](chapters/18.md)


<span id="N51"></span>



<span id="section-51"></span>


## N51 · Google SRE：Implementing SLOs

一手工程教材 相关原文核查

**本书使用范围：**用户目标、服务指标与错误预算

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://sre.google/workbook/implementing-slos/>

本地相关章节：[21](chapters/21.md)


<span id="N55"></span>



<span id="section-52"></span>


## N55 · Reflexion

原始研究论文 相关原文核查

**本书使用范围：**语言反馈与后续任务；反思不自动成为正确记忆

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2303.11366>

本地相关章节：[25](chapters/25.md)


<span id="N56"></span>



<span id="section-53"></span>


## N56 · Self-RAG

原始论文 相关原文核查

**本书使用范围：**检索、生成与反思信号；并非简单多加一个Review提示

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2310.11511>

本地相关章节：[26](chapters/26.md)


<span id="N59"></span>



<span id="section-54"></span>


## N59 · Tree of Thoughts

原始论文 相关原文核查

**本书使用范围：**搜索、候选状态与评估器成本

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2305.10601>

本地相关章节：[26](chapters/26.md)


<span id="N61"></span>



<span id="section-55"></span>


## N61 · InstructGPT：Human Feedback

原始论文 相关原文核查

**本书使用范围：**监督微调、奖励模型与偏好后训练

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2203.02155>

本地相关章节：[04](chapters/04.md)


<span id="N67"></span>



<span id="section-56"></span>


## N67 · ReAct

原始论文 相关原文核查

**本书使用范围：**推理与行动反馈结合的基本机制

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2210.03629>

本地相关章节：[26](chapters/26.md)


<span id="N69"></span>



<span id="section-57"></span>


## N69 · Retrieval-Augmented Generation

原始论文 相关原文核查

**本书使用范围：**参数化模型与非参数化证据相结合

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2005.11401>

本地相关章节：[26](chapters/26.md)


<span id="N70"></span>



<span id="section-58"></span>


## N70 · Dense Passage Retrieval

原始论文 相关原文核查

**本书使用范围：**双编码器与对比训练；本书InfoNCE推导独立展开

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2004.04906>

本地相关章节：[26](chapters/26.md) / [31](chapters/31.md)


<span id="N71"></span>



<span id="section-59"></span>


## N71 · ColBERT

原始论文 相关原文核查

**本书使用范围：**Token级晚交互与检索成本

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2004.12832>

本地相关章节：[13](chapters/13.md) / [26](chapters/26.md)


<span id="N72"></span>



<span id="section-60"></span>


## N72 · HyDE

原始论文 相关原文核查

**本书使用范围：**假设文档用于召回，不是事实证据

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2212.10496>

本地相关章节：[13](chapters/13.md) / [26](chapters/26.md)


<span id="N73"></span>



<span id="section-61"></span>


## N73 · RAPTOR

原始论文 相关原文核查

**本书使用范围：**分层摘要和树状检索的用途与损失

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2401.18059>

本地相关章节：[26](chapters/26.md)


<span id="N74"></span>



<span id="section-62"></span>


## N74 · RepoCoder

原始论文 相关原文核查

**本书使用范围：**仓库级检索与生成迭代；不保证跨项目可迁移比例

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2303.12570>

本地相关章节：[14](chapters/14.md)


<span id="N76"></span>



<span id="section-63"></span>


## N76 · LoCoMo

原始评测论文 相关原文核查

**本书使用范围：**长会话的时间、实体与跨段记忆；未复现基准

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2402.17753>

本地相关章节：[26](chapters/26.md)


<span id="N77"></span>



<span id="section-64"></span>


## N77 · A-MEM

原始论文 相关原文核查

**本书使用范围：**动态链接与记忆组织；方法级解释而非完整实现

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2502.12110>

本地相关章节：[15](chapters/15.md) / [26](chapters/26.md)


<span id="N78"></span>



<span id="section-65"></span>


## N78 · Mem0

原始研究论文 相关原文核查

**本书使用范围：**记忆提取与维护；区分作者报告和独立复现

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2504.19413>

本地相关章节：[15](chapters/15.md) / [26](chapters/26.md)


<span id="N79"></span>



<span id="section-66"></span>


## N79 · SWE-agent

原始论文 相关原文核查

**本书使用范围：**Agent-Computer Interface与软件工程任务

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2405.15793>

本地相关章节：[18](chapters/18.md) / [28](chapters/28.md)


<span id="N80"></span>



<span id="section-67"></span>


## N80 · SWE-bench

原始评测论文 相关原文核查

**本书使用范围：**真实Issue、补丁与测试环境；本书小仓库不是SWE-bench

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2310.06770>

本地相关章节：[26](chapters/26.md)


<span id="N81"></span>



<span id="section-68"></span>


## N81 · Claude Computer Use Tool

官方接口文档 相关原文核查

**本书使用范围：**截图、动作与环境反馈；未执行外部GUI任务

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool>

本地相关章节：[24](chapters/24.md)


<span id="N82"></span>



<span id="section-69"></span>


## N82 · OpenTelemetry GenAI语义约定

官方项目文档 相关原文核查

**本书使用范围：**已迁移的GenAI约定入口；本书不硬编码未稳定字段

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/README.md>

本地相关章节：[21](chapters/21.md)


<span id="N83"></span>



<span id="section-70"></span>


## N83 · OWASP Agentic Applications 2026

官方安全资料 相关原文核查

**本书使用范围：**Agent权限、工具、记忆与自主执行风险；不是产品安全认证

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/>

本地相关章节：[20](chapters/20.md) / [28](chapters/28.md)


<span id="N85"></span>



<span id="section-71"></span>


## N85 · OpenAI Latency Optimization

官方工程指南 相关原文核查

**本书使用范围：**延迟的输入、输出、请求与工具组成；本书没有服务端跑分

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://developers.openai.com/api/docs/guides/latency-optimization>

本地相关章节：[22](chapters/22.md)


<span id="N86"></span>



<span id="section-72"></span>


## N86 · OpenAI Harness Engineering

官方工程文章 相关原文核查

**本书使用范围：**环境、知识组织、验证反馈与工程边界

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://openai.com/index/harness-engineering/>

本地相关章节：[18](chapters/18.md)


<span id="N87"></span>



<span id="section-73"></span>


## N87 · Building Effective Agents

官方工程文章 相关原文核查

**本书使用范围：**预设工作流与动态Agent、从简单方案出发

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://www.anthropic.com/engineering/building-effective-agents>

本地相关章节：[08](chapters/08.md)


<span id="N88"></span>



<span id="section-74"></span>


## N88 · Scaling and Evaluating Sparse Autoencoders

原始研究论文 相关原文核查

**本书使用范围：**稀疏特征、重构与解释评估；未训练SAE

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2406.04093>

本地相关章节：[25](chapters/25.md)


<span id="N95"></span>



<span id="section-75"></span>


## N95 · HNSW原始论文摘要与元数据

原始论文摘要 摘要核查

**本书使用范围：**来源使用范围仅限摘要级机制；实现选型结合N33，不声称全文复现

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/abs/1603.09320>

本地相关章节：[13](chapters/13.md)


<span id="N96"></span>



<span id="section-76"></span>


## N96 · Tree-sitter Query Syntax

官方工具文档 相关原文核查

**本书使用范围：**语法节点与结构查询；不等于完整语义绑定

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://tree-sitter.github.io/tree-sitter/using-parsers/queries/1-syntax.html>

本地相关章节：[14](chapters/14.md)


<span id="N97"></span>



<span id="section-77"></span>


## N97 · Vision Transformer

原始论文 相关原文核查

**本书使用范围：**图像patch与Transformer表示；不作为闭源多模态架构证据

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2010.11929>

本地相关章节：[24](chapters/24.md)


<span id="N98"></span>



<span id="section-78"></span>


## N98 · LLaVA：Visual Instruction Tuning

原始论文 相关原文核查

**本书使用范围：**视觉—语言连接与指令训练；典型公开方案，不是统一架构

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2304.08485>

本地相关章节：[24](chapters/24.md)


<span id="N99"></span>



<span id="section-79"></span>


## N99 · Whisper：Robust Speech Recognition

原始论文 相关原文核查

**本书使用范围：**语音表示、转录与模型训练范围；本书不做语音实验

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://arxiv.org/html/2212.04356>

本地相关章节：[24](chapters/24.md)


<span id="N100"></span>



<span id="section-80"></span>


## N100 · OpenAI Working with Evals：弃用提示

官方接口文档 相关原文核查

**本书使用范围：**2026-10-17核查：旧平台计划10月31日只读、11月30日关闭；未来时间可能更新

核查日期：2026-10-17｜版本：见固定URL或核查日期；动态网页不等于本地版本

外部原始出处（可选）：<https://developers.openai.com/api/docs/guides/evals>

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)