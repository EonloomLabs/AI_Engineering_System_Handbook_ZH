---
title: "工程深挖的依据与适用范围"
description: "AI系统工程：本地教学正文与可追溯图表"
---


<span id="eng-source-title"></span>


# 工程深挖的依据与适用范围

每项事实都限定到可追溯的文档、源码或实验；工程建议与事实本身分开。


<span id="evidence-levels"></span>


## 怎样阅读证据

| 证据类型 | 本教材怎样使用 | 不能据此声称 |
| --- | --- | --- |
| 官方接口／产品文档 | 按版本、章节与核对日期说明输入、输出和限制。 | 未公开的内部系统提示、私有策略或服务端实现。 |
| 固定源码／公开修复 | 注明commit、路径、符号和读取范围；旧修复讲历史机制。 | 当前所有版本仍有同样bug，或源码已在本地构建运行。 |
| 原始论文／作者工程报告 | 保留研究目标、前提和局限。 | 论文基准成绩等于用户项目可获得的收益。 |
| 本地算子／文件／进程实验 | 提供完整代码、真实输出、环境和失败反例。 | CPU行为普遍等同GPU融合内核或商业服务。 |
| 教学逻辑模拟与推导 | 明确固定输入，验证不变量和失败路径。 | 部署过MCP服务、向量数据库或生产Agent，或制造过真实事故。 |

核对日期统一为**2026-10-21**。动态地址不等于不可变快照；对动态文档，未来阅读时应按记录的接口章节重新确认。这里记录的是本次已读取依据及其边界，不是对所有旧章事实重新认证。


<span id="source-register"></span>


## 一手来源目录


<span id="src-CHAT"></span>



<span id="topic-1"></span>


### CHAT · Hugging Face · Chat templates

版本／日期
:   main动态文档；核对日期2026-10-21；不将main等同于某个已发布安装版本

核对日期
:   2026-10-21

对应章节
:   Special tokens / add\_generation\_prompt / continue\_final\_message

支持的事实
:   消息模板与tokenizer的特殊标记处理必须一致；模板已插入标记时，再tokenize不应重复添加；开启新助手轮与续写末条消息是不同任务。

适用边界
:   不同模型模板不同；本书未运行商业聊天服务隐藏模板。

[原始来源：https://huggingface.co/docs/transformers/main/en/chat\_templating](https://huggingface.co/docs/transformers/main/en/chat_templating)


<span id="src-TOKEN"></span>



<span id="topic-2"></span>


### TOKEN · Hugging Face · Tokenizer

版本／日期
:   查询日文档

核对日期
:   2026-10-21

对应章节
:   add\_tokens / add\_special\_tokens

支持的事实
:   新增词表项后需同步调整模型嵌入容量；resize\_token\_embeddings传入完整词表长度，不是本次新增数量。

适用边界
:   具体模型是否绑定输入输出权重及如何初始化新行，须查相应实现。

[原始来源：https://huggingface.co/docs/transformers/main\_classes/tokenizer](https://huggingface.co/docs/transformers/main_classes/tokenizer)


<span id="src-SDPA"></span>



<span id="topic-3"></span>


### SDPA · PyTorch · scaled\_dot\_product\_attention

版本／日期
:   2.10；与本书本次CPU实验版本一致

核对日期
:   2026-10-21

对应章节
:   attn\_mask / dropout\_p / is\_causal / backend warning

支持的事实
:   布尔True表示可参与；函数按dropout\_p应用dropout；非方阵is\_causal采用左上对齐；融合内核与数学实现存在浮点差异。

适用边界
:   这里描述2.10接口，不把所有Attention库都视为同一契约；CPU实验不能证明GPU速度。

[原始来源：https://docs.pytorch.org/docs/2.10/generated/torch.nn.functional.scaled\_dot\_product\_attention.html](https://docs.pytorch.org/docs/2.10/generated/torch.nn.functional.scaled_dot_product_attention.html)


<span id="src-MHA"></span>



<span id="topic-4"></span>


### MHA · PyTorch · MultiheadAttention

版本／日期
:   查询日stable动态文档；本地实验另记录2.10

核对日期
:   2026-10-21

对应章节
:   attn\_mask / key\_padding\_mask / need\_weights

支持的事实
:   MHA的布尔掩码True表示禁止对应位置，与SDPA语义相反。

适用边界
:   高层MHA包含投影；不能把高层接口参数名当成已投影张量的证明。

[原始来源：https://docs.pytorch.org/docs/stable/generated/torch.nn.modules.activation.MultiheadAttention.html](https://docs.pytorch.org/docs/stable/generated/torch.nn.modules.activation.MultiheadAttention.html)


<span id="src-CACHE"></span>



<span id="topic-5"></span>


### CACHE · Transformers · Cache explanation

版本／日期
:   固定5.0.0文档

核对日期
:   2026-10-21

对应章节
:   Cache position / attention mask

支持的事实
:   增量注意力读取历史和当前K/V；mask覆盖过去与当前长度；文档的cache\_position不受padding内容语义影响。

适用边界
:   缓存实现可能是动态、静态、滑窗；槽位、绝对位置与真实有效Token数不能混为一谈。

[原始来源：https://huggingface.co/docs/transformers/v5.0.0/cache\_explanation](https://huggingface.co/docs/transformers/v5.0.0/cache_explanation)


<span id="src-GENERATE"></span>



<span id="topic-6"></span>


### GENERATE · Transformers · LLM generation tutorial

版本／日期
:   main动态文档

核对日期
:   2026-10-21

对应章节
:   Wrong padding side / Generation configuration

支持的事实
:   常见decoder-only generate需要左补齐；只给attention\_mask并不能替代正确选取最后有效位置的logits。

适用边界
:   这是该生成调用路径的约定，不是右补齐在所有自定义前向中都不合法。

[原始来源：https://huggingface.co/docs/transformers/main/en/llm\_tutorial](https://huggingface.co/docs/transformers/main/en/llm_tutorial)


<span id="src-GRAD"></span>



<span id="topic-7"></span>


### GRAD · Hugging Face · Fixing Gradient Accumulation

版本／日期
:   2024-10-16发布；2026-10-21重新核对

核对日期
:   2026-10-21

对应章节
:   Causal LM loss normalization / fix

支持的事实
:   公开修复案例指出，累计不同有效Token数的小批次时，应按总token损失与总有效Token数归一化，而不是简单平均各批平均损失。

适用边界
:   历史事故不表示当前版本仍有该bug；分布式缩放需另看DDP/Trainer实现。

[原始来源：https://huggingface.co/blog/gradient\_accumulation](https://huggingface.co/blog/gradient_accumulation)


<span id="src-AMP"></span>



<span id="topic-8"></span>


### AMP · PyTorch · Automatic Mixed Precision examples

版本／日期
:   2.10

核对日期
:   2026-10-21

对应章节
:   Gradient clipping / Gradient accumulation

支持的事实
:   裁剪应在unscale之后；一轮累计更新的缩放与unscale时机必须一致。

适用边界
:   本次用CPU数值反例验证缩放代数，不声称执行了CUDA GradScaler训练。

[原始来源：https://docs.pytorch.org/docs/2.10/notes/amp\_examples.html](https://docs.pytorch.org/docs/2.10/notes/amp_examples.html)


<span id="src-CHECKPOINT"></span>



<span id="topic-9"></span>


### CHECKPOINT · PyTorch · torch.utils.checkpoint

版本／日期
:   2.10

核对日期
:   2026-10-21

对应章节
:   use\_reentrant / RNG state / recomputation

支持的事实
:   激活检查点会在反向时重算；随机状态与重算函数一致性影响正确性；重算不是纯省内存开关。

适用边界
:   重入/非重入行为不同；不要依赖函数只执行一次。

[原始来源：https://docs.pytorch.org/docs/2.10/checkpoint.html](https://docs.pytorch.org/docs/2.10/checkpoint.html)


<span id="src-LORA"></span>



<span id="topic-10"></span>


### LORA · PEFT · LoRA conceptual guide

版本／日期
:   main动态文档

核对日期
:   2026-10-21

对应章节
:   Initialization options

支持的事实
:   默认参考初始化使用A的Kaiming-uniform与零B，使增量初始为零。

适用边界
:   文档中的“identity”指不改变基座路径，不表示基座W本身是单位矩阵；其他初始化并不必然B=0。

[原始来源：https://huggingface.co/docs/peft/main/en/conceptual\_guides/lora](https://huggingface.co/docs/peft/main/en/conceptual_guides/lora)


<span id="src-DPO"></span>



<span id="topic-11"></span>


### DPO · Rafailov et al. · Direct Preference Optimization

版本／日期
:   原始论文；v3

核对日期
:   2026-10-21

对应章节
:   Preference objective / reference policy

支持的事实
:   偏好目标比较策略与参考策略对成对回答的相对对数概率。

适用边界
:   本书给出的掩码/缓存/长度反例为独立工程推导，不是复现论文训练成绩。

[原始来源：https://arxiv.org/abs/2305.18290](https://arxiv.org/abs/2305.18290)


<span id="src-SPEC"></span>



<span id="topic-12"></span>


### SPEC · Leviathan et al. · Fast Inference from Transformers via Speculative Decoding

版本／日期
:   原始论文；v2

核对日期
:   2026-10-21

对应章节
:   Exact speculative sampling

支持的事实
:   正确的推测采样通过接受/拒绝校正保持目标分布。

适用边界
:   本书枚举有限分布验证正确性，不复现论文硬件加速比。

[原始来源：https://arxiv.org/abs/2211.17192](https://arxiv.org/abs/2211.17192)


<span id="src-PREFIX"></span>



<span id="topic-13"></span>


### PREFIX · vLLM · Automatic Prefix Caching

版本／日期
:   latest动态文档，描述v1

核对日期
:   2026-10-21

对应章节
:   Block hash / extra hashes / cache\_salt / operations

支持的事实
:   块身份依赖前缀链和附加信息；请求盐支持限制跨信任域复用；共享块需要生命周期管理。

适用边界
:   盐不是用户身份认证；本书只模拟身份和别名，不声称运行vLLM服务。

[原始来源：https://docs.vllm.ai/en/latest/design/prefix\_caching/](https://docs.vllm.ai/en/latest/design/prefix_caching/)


<span id="src-SCHED"></span>



<span id="topic-14"></span>


### SCHED · vLLM · Optimization and Tuning

版本／日期
:   latest动态文档

核对日期
:   2026-10-21

对应章节
:   Preemption / Chunked Prefill

支持的事实
:   KV空间不足可导致抢占和重算；调度和分块prefill影响吞吐、TTFT与token间延迟的取舍。

适用边界
:   默认值随版本变化；本书不提供未经压测的万能配置或加速百分比。

[原始来源：https://docs.vllm.ai/en/latest/configuration/optimization/](https://docs.vllm.ai/en/latest/configuration/optimization/)


<span id="src-RESP"></span>



<span id="topic-15"></span>


### RESP · OpenAI · Migrate to the Responses API

版本／日期
:   查询日公开API指南

核对日期
:   2026-10-21

对应章节
:   Map Messages to Items / Update multi-turn conversations

支持的事实
:   previous\_response\_id不携带上轮顶层instructions；手动管理上下文需处理有类型的output项，不能只保留output\_text。

适用边界
:   没有调用付费API，也没有访问闭源隐藏提示。

[原始来源：https://developers.openai.com/api/docs/guides/migrate-to-responses](https://developers.openai.com/api/docs/guides/migrate-to-responses)


<span id="src-TOOLS"></span>



<span id="topic-16"></span>


### TOOLS · OpenAI · Function calling

版本／日期
:   查询日公开API指南

核对日期
:   2026-10-21

对应章节
:   Streaming / call\_id / tool outputs

支持的事实
:   调用与结果通过call\_id关联；流式参数分片需按项组装；模型提出调用不等于应用已执行。

适用边界
:   不同协议终止事件不同；本书协议实验是本地适配器，不伪装真实API回包。

[原始来源：https://developers.openai.com/api/docs/guides/function-calling](https://developers.openai.com/api/docs/guides/function-calling)


<span id="src-STRUCT"></span>



<span id="topic-17"></span>


### STRUCT · OpenAI · Structured Outputs

版本／日期
:   查询日公开API指南

核对日期
:   2026-10-21

对应章节
:   Refusals / Incomplete responses / Supported schemas

支持的事实
:   Schema约束不等于事实与权限正确；拒绝和不完整响应需要分支处理。

适用边界
:   不能据此声称任意schema、任意模型都支持同一严格输出能力。

[原始来源：https://developers.openai.com/api/docs/guides/structured-outputs](https://developers.openai.com/api/docs/guides/structured-outputs)


<span id="src-COMPACT"></span>



<span id="topic-18"></span>


### COMPACT · OpenAI · Compaction

版本／日期
:   查询日公开API指南

核对日期
:   2026-10-21

对应章节
:   Standalone compaction / canonical output window

支持的事实
:   压缩响应中的完整规范输出窗口应一起传递；其中可能同时有保留内容与不透明压缩项，不能随意只保留一项。

适用边界
:   不解读或编造不透明压缩状态的内部内容；接口支持范围需以实际模型为准。

[原始来源：https://developers.openai.com/api/docs/guides/compaction](https://developers.openai.com/api/docs/guides/compaction)


<span id="src-PCACHE"></span>



<span id="topic-19"></span>


### PCACHE · OpenAI · Prompt caching

版本／日期
:   查询日动态指南

核对日期
:   2026-10-21

对应章节
:   Exact prefix / model-dependent caching controls

支持的事实
:   缓存依赖可复用前缀与服务规则；缓存不是删除输入上下文。

适用边界
:   计费、阈值、保留时间和支持模型是易变参数，教材不写成永久常量。

[原始来源：https://developers.openai.com/api/docs/guides/prompt-caching](https://developers.openai.com/api/docs/guides/prompt-caching)


<span id="src-MCPTOOLS"></span>



<span id="topic-20"></span>


### MCPTOOLS · MCP · Tools

版本／日期
:   明确固定2025-11-25，不声称最新版本

核对日期
:   2026-10-21

对应章节
:   tools/list / pagination / isError

支持的事实
:   工具列表可分页；能力变更需按协商处理；协议错误与工具执行返回isError分属不同层。

适用边界
:   发现能力不等于授权执行；工具注解来自服务，不天然可信。

[原始来源：https://modelcontextprotocol.io/specification/2025-11-25/server/tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)


<span id="src-MCPLIFE"></span>



<span id="topic-21"></span>


### MCPLIFE · MCP · Lifecycle

版本／日期
:   固定2025-11-25

核对日期
:   2026-10-21

对应章节
:   Initialization / capability negotiation / shutdown

支持的事实
:   初始化需要协商协议版本和能力；开始业务调用前应完成生命周期约定。

适用边界
:   超时与取消不自动撤销已完成的外部副作用。

[原始来源：https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)


<span id="src-MCPSEC"></span>



<span id="topic-22"></span>


### MCPSEC · MCP · Security Best Practices

版本／日期
:   固定2025-11-25

核对日期
:   2026-10-21

对应章节
:   Token passthrough / confused deputy / session hijacking

支持的事实
:   必须处理令牌受众、权限范围和代理信任边界，不能用会话标识代替身份验证或透传不合受众的令牌。

适用边界
:   本书不执行真实OAuth服务或安全渗透测试。

[原始来源：https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security\_best\_practices](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices)


<span id="src-CLAUDE"></span>



<span id="topic-23"></span>


### CLAUDE · Claude Code · Subagents

版本／日期
:   查询日产品公开文档

核对日期
:   2026-10-21

对应章节
:   Skills / permission modes / context

支持的事实
:   子Agent的上下文、预加载skills和权限需按实际配置核对；不能仅凭主会话已加载就假设子Agent继承。

适用边界
:   产品可能提供不同的fork/委派模式；未公开内部实现保持未知。

[原始来源：https://code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)


<span id="src-SKILLS"></span>



<span id="topic-24"></span>


### SKILLS · Claude Code · Skills

版本／日期
:   查询日产品公开文档

核对日期
:   2026-10-21

对应章节
:   Discovery / invocation / progressive loading

支持的事实
:   技能描述用于发现与选择，正文和附属资源按运行方式加载，发现并不等于真正执行了建议流程。

适用边界
:   这不是所有CLI都完全相同的规范保证。

[原始来源：https://code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)


<span id="src-COPILOT"></span>



<span id="topic-25"></span>


### COPILOT · GitHub · Custom agents configuration

版本／日期
:   查询日产品公开文档

核对日期
:   2026-10-21

对应章节
:   tools / tool availability

支持的事实
:   tools字段省略、通配符与空数组有不同语义；文档说明不识别的工具名会被忽略。

适用边界
:   工具名、别名和支持面随Copilot入口不同；需检查CLI/IDE/云Agent各自配置。

[原始来源：https://docs.github.com/en/copilot/reference/custom-agents-configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)


<span id="src-CODEX"></span>



<span id="topic-26"></span>


### CODEX · Codex · ToolRouter源码

版本／日期
:   commit d571eaf1f61d0d93a797506335a99a9950ffe37b；提交2026-10-21 02:02:49Z；blob 3c01ab98187227561c3a4220ed8277b7317f21ce

核对日期
:   2026-10-21

对应章节
:   ToolRouter / exposes\_tool / build\_tool\_call / dispatch\_tool\_call\_with\_code\_mode\_result\_inner

支持的事实
:   注册表、模型可见规格与可达分派是不同对象；延迟发现、Code Mode、直接调用有不同路径；分派携带call\_id和运行上下文。

适用边界
:   仅静态阅读该文件指定函数；未构建Rust客户端，不能把可见性函数当成完整授权系统。

[原始来源：https://github.com/openai/codex/blob/d571eaf1f61d0d93a797506335a99a9950ffe37b/codex-rs/core/src/tools/router.rs](https://github.com/openai/codex/blob/d571eaf1f61d0d93a797506335a99a9950ffe37b/codex-rs/core/src/tools/router.rs)


<span id="src-E5"></span>



<span id="topic-27"></span>


### E5 · intfloat · e5-base-v2模型卡

版本／日期
:   查询日作者模型卡

核对日期
:   2026-10-21

对应章节
:   Usage / FAQ

支持的事实
:   检索用途按模型要求添加query:/passage:前缀，并使用配套池化和归一化。

适用边界
:   该模型是英文模型；前缀规则不能推广为所有embedding模型的通用格式。

[原始来源：https://huggingface.co/intfloat/e5-base-v2](https://huggingface.co/intfloat/e5-base-v2)


<span id="src-PGVECTOR"></span>



<span id="topic-28"></span>


### PGVECTOR · pgvector · README

版本／日期
:   master动态文档；迭代索引扫描条目标示0.8.0起

核对日期
:   2026-10-21

对应章节
:   Filtering / Iterative index scans

支持的事实
:   近似索引候选扫描后应用过滤可导致数量不足；支持迭代扫描的版本可扩大扫描以改善该现象。

适用边界
:   本书用小列表演示候选截断，不声称运行了PostgreSQL向量索引或复现性能。

[原始来源：https://github.com/pgvector/pgvector/blob/master/README.md](https://github.com/pgvector/pgvector/blob/master/README.md)


<span id="src-LSP"></span>



<span id="topic-29"></span>


### LSP · Microsoft · Language Server Protocol 3.17

版本／日期
:   固定协议3.17；仓库gh-pages正文

核对日期
:   2026-10-21

对应章节
:   PositionEncodingKind（position.md blob 49f13964bc12c6e65c35a349c33e7e3314245c60）及文档版本

支持的事实
:   位置编码、文档版本和文本编辑范围必须一致；传输内容字节数与文档字符位置是不同计量。

适用边界
:   3.17并非查询日最新协议；本书显式按协商编码解释，不硬编码所有服务器都用UTF-16。

[原始来源：https://github.com/microsoft/language-server-protocol/blob/gh-pages/\_specifications/lsp/3.17/specification.md](https://github.com/microsoft/language-server-protocol/blob/gh-pages/_specifications/lsp/3.17/specification.md)

also\_read：['https://github.com/microsoft/language-server-protocol/blob/gh-pages/\_specifications/lsp/3.17/types/position.md']


<span id="src-GIT"></span>



<span id="topic-30"></span>


### GIT · Git · git-worktree

版本／日期
:   查询日手册

核对日期
:   2026-10-21

对应章节
:   Linked working trees / shared repository data

支持的事实
:   工作树隔离工作目录，但共享部分仓库数据；环境端口、外部数据库与缓存仍需额外隔离。

适用边界
:   后半句是由隔离范围得出的工程推论，不把worktree描述成完整沙箱。

[原始来源：https://git-scm.com/docs/git-worktree](https://git-scm.com/docs/git-worktree)


<span id="src-SQLITE"></span>



<span id="topic-31"></span>


### SQLITE · SQLite · Transactions

版本／日期
:   查询日官方手册

核对日期
:   2026-10-21

对应章节
:   Transactions / BEGIN IMMEDIATE / busy

支持的事实
:   数据库事务控制本数据库的状态；写竞争与事务起点需明确。

适用边界
:   SQLite事务不能回滚外部文件或网络副作用；本书故障实验只用本地临时目录。

[原始来源：https://sqlite.org/lang\_transaction.html](https://sqlite.org/lang_transaction.html)


<span id="src-IDEMP"></span>



<span id="topic-32"></span>


### IDEMP · AWS Builders Library · Making retries safe with idempotent APIs

版本／日期
:   作者工程实践文章；查询日重新阅读

核对日期
:   2026-10-21

对应章节
:   Caller request identifiers / late requests / same token different intent

支持的事实
:   幂等标识要代表同一次调用意图；超时不能证明操作未执行；重复调用的语义与返回必须定义清楚。

适用边界
:   本书未接入AWS业务API；数据库外部副作用实验是自建模型。

[原始来源：https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)


<span id="src-PYTEST"></span>



<span id="topic-33"></span>


### PYTEST · pytest · Exit codes

版本／日期
:   查询日stable文档；本地版本写入结果

核对日期
:   2026-10-21

对应章节
:   Exit codes 0–5

支持的事实
:   退出码5表示没有收集到测试；0不能单独证明测试数量、覆盖度或最终代码版本正确。

适用边界
:   全部skip退出0的行为由本次本地子进程另外验证。

[原始来源：https://docs.pytest.org/en/stable/reference/exit-codes.html](https://docs.pytest.org/en/stable/reference/exit-codes.html)


<span id="src-EVAL"></span>



<span id="topic-34"></span>


### EVAL · Anthropic · Demystifying evals for AI agents

版本／日期
:   2026-01-09发布；查询日阅读

核对日期
:   2026-10-21

对应章节
:   Tasks / trials / graders / transcripts / outcomes

支持的事实
:   需要区分任务、试跑、评分器、执行轨迹与环境中的实际结果。

适用边界
:   本书自建配对数据只用于说明评测错误，不是商业Agent排名。

[原始来源：https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)


<span id="src-NOISE"></span>



<span id="topic-35"></span>


### NOISE · Anthropic · Quantifying infrastructure noise in agentic coding evals

版本／日期
:   2026年公开工程研究；查询日阅读

核对日期
:   2026-10-21

对应章节
:   Infrastructure configuration / resource effects

支持的事实
:   执行基础设施变化可以影响编码Agent评测结果，比较模型时应控制环境与资源。

适用边界
:   不把某实验中的幅度推广到所有Agent，不伪造自身线上观测。

[原始来源：https://www.anthropic.com/engineering/infrastructure-noise](https://www.anthropic.com/engineering/infrastructure-noise)


<span id="src-JUDGE"></span>



<span id="topic-36"></span>


### JUDGE · Zheng et al. · Judging LLM-as-a-Judge

版本／日期
:   原始论文v4

核对日期
:   2026-10-21

对应章节
:   Position / verbosity / self-enhancement bias

支持的事实
:   模型裁判存在位置与篇幅等偏差，不能仅因答案由强模型评分就当成客观真值。

适用边界
:   论文中的具体模型结论不自动适用于当前所有模型。

[原始来源：https://arxiv.org/abs/2306.05685](https://arxiv.org/abs/2306.05685)


<span id="src-OPENAT"></span>



<span id="topic-37"></span>


### OPENAT · Linux man-pages · openat2(2)

版本／日期
:   查询日手册

核对日期
:   2026-10-21

对应章节
:   RESOLVE\_BENEATH / RESOLVE\_IN\_ROOT / symlinks

支持的事实
:   目录句柄与解析约束用于限制路径解析范围；字符串检查不能替代执行时边界。

适用边界
:   这些是Linux接口，不声称同样代码可直接用于Windows/macOS；本地symlink实验仅说明攻击面。

[原始来源：https://man7.org/linux/man-pages/man2/openat2.2.html](https://man7.org/linux/man-pages/man2/openat2.2.html)


<span id="src-SRE"></span>



<span id="topic-38"></span>


### SRE · Google SRE · Handling overload

版本／日期
:   作者工程实践章节

核对日期
:   2026-10-21

对应章节
:   Queue management / overload / load shedding

支持的事实
:   排队和资源限制需以有效工作量和截止时间考虑；堆积请求可使系统进入更差状态。

适用边界
:   本书时间线是明确设定的示例，不是生产压测。

[原始来源：https://sre.google/sre-book/handling-overload/](https://sre.google/sre-book/handling-overload/)


<span id="src-GUI"></span>



<span id="topic-39"></span>


### GUI · Anthropic · Computer use tool

版本／日期
:   查询日工具指南

核对日期
:   2026-10-21

对应章节
:   Screenshots / coordinates / environment / security

支持的事实
:   截图、坐标和执行环境必须对应；动作之后需要重新观察状态并处理不可信界面内容。

适用边界
:   本书坐标实验不启动真实GUI Agent或自动点击外部应用。

[原始来源：https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)


<span id="src-CAL"></span>



<span id="topic-40"></span>


### CAL · scikit-learn · Probability calibration

版本／日期
:   查询日stable指南

核对日期
:   2026-10-21

对应章节
:   Calibration curves / proper scoring / calibration data

支持的事实
:   校准评估需要预测与实际结果的匹配及独立数据；区分可靠性、分辨能力和总体误差。

适用边界
:   本书不把Token softmax当作整段回答正确率，也不从教学表推出真实模型校准程度。

[原始来源：https://scikit-learn.org/stable/modules/calibration.html](https://scikit-learn.org/stable/modules/calibration.html)


<span id="src-CIRCUIT"></span>



<span id="topic-41"></span>


### CIRCUIT · Anthropic · Tracing the thoughts of a large language model

版本／日期
:   2025-03-27；查询日阅读

核对日期
:   2026-10-21

对应章节
:   Circuit tracing / limitations

支持的事实
:   可解释研究通过内部机制和干预探索部分路径；自然语言解释与真实内部因果机制不能直接画等号。

适用边界
:   不声称完整解释模型，也不将本文人工因果图当成真实神经网络发现。

[原始来源：https://www.anthropic.com/research/tracing-thoughts-language-model](https://www.anthropic.com/research/tracing-thoughts-language-model)


<span id="src-SCALE"></span>



<span id="topic-42"></span>


### SCALE · Hoffmann et al. · Training Compute-Optimal Large Language Models

版本／日期
:   2022年原始研究

核对日期
:   2026-10-21

对应章节
:   Compute-optimal training allocation

支持的事实
:   在研究设置中比较参数量、数据量与训练计算预算的分配。

适用边界
:   训练预算最优不等于生命周期成本最优；本书盈亏平衡是原创代数例，不是论文实测。

[原始来源：https://arxiv.org/abs/2203.15556](https://arxiv.org/abs/2203.15556)


<span id="src-RRF"></span>



<span id="topic-43"></span>


### RRF · Elastic · Reciprocal rank fusion

版本／日期
:   查询日官方文档

核对日期
:   2026-10-21

对应章节
:   Formula / rank\_constant / rank\_window\_size

支持的事实
:   RRF按各候选的排名而非原始相关分数融合；窗口截断决定哪些候选能参与。

适用边界
:   相关来源重复计票的反例为本书构造，不是Elastic事故报告。

[原始来源：https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)


<span id="src-MEMEVAL"></span>



<span id="topic-44"></span>


### MEMEVAL · Wu et al. · LongMemEval

版本／日期
:   v2，2025-03-04

核对日期
:   2026-10-21

对应章节
:   Temporal reasoning / knowledge updates / abstention

支持的事实
:   长期记忆评测需要覆盖时序推理、知识更新和拒答，不能只检查内容能否被召回。

适用边界
:   本书双时间表与撤销传播是原创工程方案，不声称原论文规定该数据库结构。

[原始来源：https://arxiv.org/abs/2410.10813v2](https://arxiv.org/abs/2410.10813v2)


<span id="src-TRACE"></span>



<span id="topic-45"></span>


### TRACE · OpenTelemetry · Traces

版本／日期
:   查询日官方概念指南

核对日期
:   2026-10-21

对应章节
:   Spans / context / events / links

支持的事实
:   Trace由相关Span组成，Span包含运行时间与上下文关系；跨并行路径不能把持续时间直接视为总等待。

适用边界
:   p95和成本例为本书数学例；不声称在生产部署了OpenTelemetry。

[原始来源：https://opentelemetry.io/docs/concepts/signals/traces/](https://opentelemetry.io/docs/concepts/signals/traces/)


<span id="src-HFPR"></span>



<span id="topic-46"></span>


### HFPR · Transformers PR #34191 与合并后的损失实现

版本／日期
:   2024-10-17已合并；commit c1c7e89620b43f0924148e267a6da5d38450ce1f

核对日期
:   2026-10-21

对应章节
:   src/transformers/loss/loss\_utils.py；fixed\_cross\_entropy / ForCausalLMLoss；blob efa23d24e360b4dce21121a301e8ba7a6f79230b

支持的事实
:   PR已合并；该提交中提供num\_items\_in\_batch时使用损失总和再除以该数；CausalLM损失先移动logits与labels。

适用边界
:   仅核对固定历史源码，不将其当成当前全部Trainer实现；未重新执行历史完整训练套件。

[原始来源：https://github.com/huggingface/transformers/pull/34191](https://github.com/huggingface/transformers/pull/34191)

also\_read：['https://github.com/huggingface/transformers/blob/c1c7e89620b43f0924148e267a6da5d38450ce1f/src/transformers/loss/loss\_utils.py']


<span id="pinned-code"></span>


## 源码读取的明确边界

Codex读取提交 `d571eaf1f61d0d93a797506335a99a9950ffe37b` 的 `codex-rs/core/src/tools/router.rs`，重点为80—240及245—410行，包括暴露判断、类型化输出映射与分派。它用于说明源码中的分层，不声称已构建或执行该Rust客户端。

Transformers历史修复PR #34191于2024-10-17合并，固定合并提交 `c1c7e89620b43f0924148e267a6da5d38450ce1f`。读取 `src/transformers/loss/loss_utils.py` 第1—85行，核对sum归一化与标签移动。新版Trainer是否重复处理分母，应查使用版本，不能把本教材实验当成所有Trainer的兼容补丁。

LSP的偏移单位依据固定3.17协议的 `types/position.md`（blob `49f13964bc12c6e65c35a349c33e7e3314245c60`）；并未把3.17称为最新协议。


<span id="no-translation"></span>


## 写作与实验约定

中文讲解与实验代码为独立编写的教学内容。来源用于支撑机制与接口约定，不是逐字翻译整篇文章。输入、单位、分母、版本和错误路径须同时明确；有的测试只验证逻辑，不验证生产性能。

AI系统工程：从基础到内部 · [工程深挖目录](index.md) · [依据与版本](sources.md)