---
title: "正文图解的来源与适用条件"
description: "AI系统工程：本地教学正文与可追溯图表"
---

# 正文图解的来源与适用条件

以下资料用于核对新增图解中的接口与工程边界。核对日期为2026年10月21日；有版本号的资料按该版本解释。原文档中既有来源仍保留原来日期，不能把它们一律视作本次重新验证。

正文全部为中文独立讲解。图中的数字、候选、状态和路径是已声明的教学输入；原理来源不是商业模型的性能证据。既有故障实验的JSON图只重绘其原始记录，不更改原来的环境与测量范围。


<span id="source-SDPA-213"></span>



<span id="mx-section-1"></span>


## PyTorch SDPA接口

**范围：**固定文档版本2.13

核对掩码允许语义、非方阵因果对齐和dropout参数。本文显式构造位置允许表，数值为教学输入，不是性能实测。

[官方原始资料：https://docs.pytorch.org/docs/2.13/generated/torch.nn.functional.scaled\_dot\_product\_attention.html](https://docs.pytorch.org/docs/2.13/generated/torch.nn.functional.scaled_dot_product_attention.html)


<span id="source-TOOLS-API"></span>



<span id="mx-section-2"></span>


## OpenAI Function calling

**范围：**2026-10-21读取的官方文档

客户端函数调用由应用处理，并以调用标识返回结果。本文消息表是教学宿主，不是闭源系统Prompt。

[官方原始资料：https://developers.openai.com/api/docs/guides/function-calling](https://developers.openai.com/api/docs/guides/function-calling)


<span id="source-CACHE-HF"></span>



<span id="mx-section-3"></span>


## Transformers Cache explanation

**范围：**2026-10-21读取的官方文档

核对各层历史K/V复用、新Token位置和缓存与训练的边界；不据此承诺任意框架接收同一种输入形式。

[官方原始资料：https://huggingface.co/docs/transformers/cache\_explanation](https://huggingface.co/docs/transformers/cache_explanation)


<span id="source-GA-FIX"></span>



<span id="mx-section-4"></span>


## Fixing Gradient Accumulation

**范围：**2024-10-16历史修复；2026-10-21复核

解释按有效Token归一化与平均微批均值的区别。保留其历史语境，不指称当前版本仍有该缺陷。

[官方原始资料：https://huggingface.co/blog/gradient\_accumulation](https://huggingface.co/blog/gradient_accumulation)


<span id="source-MCP-LIFE-JUN"></span>



<span id="mx-section-5"></span>


## MCP Lifecycle

**范围：**固定规范2025-06-18

initialize、版本/能力协商、notifications/initialized之后进入常规通信。本图刻意固定规范版本，不称它为最新版本。

[官方原始资料：https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)


<span id="source-MCP-TOOLS-JUN"></span>



<span id="mx-section-6"></span>


## MCP Tools

**范围：**固定规范2025-06-18

核对工具发现、分页和tools/call对象。工具描述与连接成功都不是额外授权。

[官方原始资料：https://modelcontextprotocol.io/specification/2025-06-18/server/tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)


<span id="source-CONTEXT-ANT"></span>



<span id="mx-section-7"></span>


## Effective context engineering for AI agents

**范围：**2025-09-29文章；2026-10-21复核

用于上下文选择和压缩的机制背景。版本条件更新、证据约束等为本教材工程推导与构造实验，不冒充厂商内部实现。

[官方原始资料：https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)


<span id="source-RESPONSE-STATE"></span>



<span id="mx-section-8"></span>


## OpenAI Conversation state

**范围：**2026-10-21读取的官方文档

区分消息历史管理与会话引用。应用仍应检查每轮所需规则、工具与证据是否可用。

[官方原始资料：https://developers.openai.com/api/docs/guides/conversation-state](https://developers.openai.com/api/docs/guides/conversation-state)


<span id="source-RRF-ELASTIC"></span>



<span id="mx-section-9"></span>


## Elasticsearch Reciprocal rank fusion

**范围：**2026-10-21读取的官方文档

核对按1/(k+rank)累加和排名从1开始；本文候选排名是独立教学设定。

[官方原始资料：https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)


<span id="source-SQLITE-ATOMIC"></span>



<span id="mx-section-10"></span>


## SQLite Atomic Commit

**范围：**2026-10-21读取的官方文档

说明数据库提交边界；跨外部副作用的unknown与幂等设计为工程推导，不能把本地事务扩大为远端恰好一次。

[官方原始资料：https://sqlite.org/atomiccommit.html](https://sqlite.org/atomiccommit.html)


<span id="source-OTEL-TRACE"></span>



<span id="mx-section-11"></span>


## OpenTelemetry Traces

**范围：**2026-10-21读取的官方文档

Span记录操作及因果关联；示例耗时为本书设定，不代表平台实测。

[官方原始资料：https://opentelemetry.io/docs/concepts/signals/traces/](https://opentelemetry.io/docs/concepts/signals/traces/)


<span id="source-PROM-HIST"></span>



<span id="mx-section-12"></span>


## Prometheus Histograms and summaries

**范围：**2026-10-21读取的官方文档

核对分位数聚合边界；不直接平均各组p95。

[官方原始资料：https://prometheus.io/docs/practices/histograms/](https://prometheus.io/docs/practices/histograms/)


<span id="source-SLO-SRE"></span>



<span id="mx-section-13"></span>


## Google SRE Implementing SLOs

**范围：**2026-10-21读取的一手工程资料

区分服务目标、用户体验和错误预算；教材阈值若为示例会显式声明，不是通用标准。

[官方原始资料：https://sre.google/workbook/implementing-slos/](https://sre.google/workbook/implementing-slos/)