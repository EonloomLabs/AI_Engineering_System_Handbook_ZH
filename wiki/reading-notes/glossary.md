---
title: "中英术语表"
description: "AI系统工程：本地教学正文与可追溯图表"
---

拓展阅读


<span id="section-0"></span>


# 中英术语表

94个关键术语：先理解含义，再进入本地讲义。


<span id="term-001"></span>



<span id="section-1"></span>


### 词元Token

模型处理的离散符号，可是词、子词、标点或字节片段；不与单词或汉字固定一一对应。

[进入讲义 1.2 →](chapter-01.md#m-01-02)


<span id="term-002"></span>



<span id="section-2"></span>


### 分词器Tokenizer

把输入转换成Token ID并按规则解码的组件，必须与模型约定配套。

[进入讲义 1.2 →](chapter-01.md#m-01-02)


<span id="term-003"></span>



<span id="section-3"></span>


### 嵌入Embedding

将离散ID映射为连续向量；初始词向量与经过上下文处理的表示不同。

[进入讲义 1.5 →](chapter-01.md#m-01-05)


<span id="term-004"></span>



<span id="section-4"></span>


### 隐藏状态Hidden state

网络某层某位置的内部表示，不是可直接读出的固定事实条目。

[进入讲义 1.1 →](chapter-01.md#m-01-01)


<span id="term-005"></span>



<span id="section-5"></span>


### 注意力Attention

根据查询与键的匹配对值进行加权组合的模型内部运算。

[进入讲义 1.3 →](chapter-01.md#m-01-03)


<span id="term-006"></span>



<span id="section-6"></span>


### 查询、键和值Query / Key / Value

注意力中的不同投影表示，分别用于匹配与内容组合，不是外部数据库的同名对象。

[进入讲义 1.3 →](chapter-01.md#m-01-03)


<span id="term-007"></span>



<span id="section-7"></span>


### 因果掩码Causal mask

限制位置只能读取允许的过去信息，避免生成时访问未来目标。

[进入讲义 1.4 →](chapter-01.md#m-01-04)


<span id="term-008"></span>



<span id="section-8"></span>


### 交叉注意力Cross-attention

查询与被查询表示来自不同序列或来源的注意力形式。

[进入讲义 1.6 →](chapter-01.md#m-01-06)


<span id="term-009"></span>



<span id="section-9"></span>


### 残差连接Residual connection

把输入沿直接路径加回变换结果，帮助信息和梯度传播。

[进入讲义 1.3 →](chapter-01.md#m-01-03)


<span id="term-010"></span>



<span id="section-10"></span>


### 归一化Normalization

控制内部数值尺度的运算；位置和具体形式依模型架构而异。

[进入讲义 1.4 →](chapter-01.md#m-01-04)


<span id="term-011"></span>



<span id="section-11"></span>


### 旋转位置编码RoPE

通过旋转作用让注意力计算包含位置关系，不自动保证任意长度泛化。

[进入讲义 1.7 →](chapter-01.md#m-01-07)


<span id="term-012"></span>



<span id="section-12"></span>


### 多头、单组共享与分组查询注意力MHA / MQA / GQA

区别之一是查询头如何共享Key和Value头，影响缓存和推理权衡。

[进入讲义 1.8 →](chapter-01.md#m-01-08)


<span id="term-013"></span>



<span id="section-13"></span>


### 混合专家MoE

模型内部路由选择部分专家网络的稀疏结构，不是多个聊天Agent开会。

[进入讲义 1.9 →](chapter-01.md#m-01-09)


<span id="term-014"></span>



<span id="section-14"></span>


### 未归一化分数Logits

输出投影产生的候选分数，经过softmax等处理形成分布；不是事实置信度。

[进入讲义 3.1 →](chapter-03.md#m-03-01)


<span id="term-015"></span>



<span id="section-15"></span>


### 归一化指数函数Softmax

把分数变成和为1的正权重；稳定实现通常先减去最大值。

[进入讲义 1.3 →](chapter-01.md#m-01-03)


<span id="term-016"></span>



<span id="section-16"></span>


### 自回归Autoregressive

按已有前缀预测并选择后续Token，再把结果用于下一步。

[进入讲义 0.2 →](chapter-00.md#m-00-02)


<span id="term-017"></span>



<span id="section-17"></span>


### 预训练Pretraining

通过大规模训练目标更新参数，形成可迁移表示和能力。

[进入讲义 2.1 →](chapter-02.md#m-02-01)


<span id="term-018"></span>



<span id="section-18"></span>


### 监督微调SFT

利用输入与目标响应配对数据调整模型行为。

[进入讲义 2.6 →](chapter-02.md#m-02-06)


<span id="term-019"></span>



<span id="section-19"></span>


### 人类反馈强化学习RLHF

把偏好、奖励与策略优化结合的训练路线，不等于普通聊天反馈。

[进入讲义 2.6 →](chapter-02.md#m-02-06)


<span id="term-020"></span>



<span id="section-20"></span>


### 奖励模型Reward model

近似某种评价或偏好的模型，奖励高不一定等于事实或业务正确。

[进入讲义 2.6 →](chapter-02.md#m-02-06)


<span id="term-021"></span>



<span id="section-21"></span>


### 近端策略优化PPO

一种控制策略更新的强化学习方法，不等于整个RLHF系统。

[进入讲义 2.9 →](chapter-02.md#m-02-09)


<span id="term-022"></span>



<span id="section-22"></span>


### 直接偏好优化DPO

利用偏好对直接优化模型的训练方法，仍会更新参数。

[进入讲义 2.7 →](chapter-02.md#m-02-07)


<span id="term-023"></span>



<span id="section-23"></span>


### 上下文学习In-context learning

利用当前输入中的示例适应任务，通常不在该次推理中更新权重。

[进入讲义 1.10 →](chapter-01.md#m-01-10)


<span id="term-024"></span>



<span id="section-24"></span>


### 思维链Chain of thought

中间推理步骤相关的提示或输出形式；长解释不保证正确，也不等于全部内部推理。

[进入讲义 2.11 →](chapter-02.md#m-02-11)


<span id="term-025"></span>



<span id="section-25"></span>


### 推理努力配置Reasoning effort

部分模型接口对推理计算的控制方式，支持与含义依产品而异。

[进入讲义 3.4 →](chapter-03.md#m-03-04)


<span id="term-026"></span>



<span id="section-26"></span>


### 过程监督Process supervision

评价中间步骤的训练信号，与只评价最终结果不同。

[进入讲义 2.13 →](chapter-02.md#m-02-13)


<span id="term-027"></span>



<span id="section-27"></span>


### 自一致性Self-consistency

对多个采样路径的答案进行聚合，不等于独立来源交叉验证。

[进入讲义 2.14 →](chapter-02.md#m-02-14)


<span id="term-028"></span>



<span id="section-28"></span>


### 预填充Prefill

处理已有输入上下文的阶段，与逐步生成的Decode资源特征不同。

[进入讲义 3.6 →](chapter-03.md#m-03-06)


<span id="term-029"></span>



<span id="section-29"></span>


### 解码生成Decode

基于当前状态产生后续Token的阶段，通常有串行依赖。

[进入讲义 3.6 →](chapter-03.md#m-03-06)


<span id="term-030"></span>



<span id="section-30"></span>


### 键值缓存KV Cache

复用过去位置的中间计算，减少重复推理；不是长期知识记忆。

[进入讲义 3.3 →](chapter-03.md#m-03-03)


<span id="term-031"></span>



<span id="section-31"></span>


### 提示前缀缓存Prompt Cache

复用符合条件的相同输入前缀处理结果；不等于内容压缩。

[进入讲义 3.7 →](chapter-03.md#m-03-07)


<span id="term-032"></span>



<span id="section-32"></span>


### 温度Temperature

调整采样分布尖锐程度的参数，不能自动提高事实正确性。

[进入讲义 3.1 →](chapter-03.md#m-03-01)


<span id="term-033"></span>



<span id="section-33"></span>


### 核采样Top-p

保留累计概率达到阈值的候选集合后采样，候选数量可动态变化。

[进入讲义 3.2 →](chapter-03.md#m-03-02)


<span id="term-034"></span>



<span id="section-34"></span>


### IO优化注意力FlashAttention

通过改进分块和数据搬运提高注意力实现效率，不是任意丢弃信息。

[进入讲义 3.9 →](chapter-03.md#m-03-09)


<span id="term-035"></span>



<span id="section-35"></span>


### 分页注意力缓存管理PagedAttention

按块组织KV缓存，主要改善服务端内存管理与吞吐。

[进入讲义 3.8 →](chapter-03.md#m-03-08)


<span id="term-036"></span>



<span id="section-36"></span>


### 推测解码Speculative decoding

草稿提出候选，目标模型验证以加速生成；收益受接受率与开销影响。

[进入讲义 3.10 →](chapter-03.md#m-03-10)


<span id="term-037"></span>



<span id="section-37"></span>


### 结构化输出Structured output

按Schema约束格式和字段，不保证字段中的事实真实。

[进入讲义 4.5 →](chapter-04.md#m-04-05)


<span id="term-038"></span>



<span id="section-38"></span>


### 函数调用Function calling

模型提出工具及参数，外部系统验证执行，再把结果返回。

[进入讲义 4.4 →](chapter-04.md#m-04-04)


<span id="term-039"></span>



<span id="section-39"></span>


### 流式输出Streaming

以增量事件交付内容，需要完整组装并识别完成状态。

[进入讲义 4.6 →](chapter-04.md#m-04-06)


<span id="term-040"></span>



<span id="section-40"></span>


### 运行框架Harness

组织模型输入、工具、状态、权限与执行循环的外围系统。

[进入讲义 6.3 →](chapter-06.md#m-06-03)


<span id="term-041"></span>



<span id="section-41"></span>


### 智能体循环Agent loop

模型决策、工具行动、观察反馈和继续执行的循环。

[进入讲义 5.1 →](chapter-05.md#m-05-01)


<span id="term-042"></span>



<span id="section-42"></span>


### 工作流Workflow

主要路径预先定义的编排，可与动态Agent结合。

[进入讲义 10.8 →](chapter-10.md#m-10-08)


<span id="term-043"></span>



<span id="section-43"></span>


### 工具模式定义Tool schema

描述工具参数与结构，帮助模型调用并支持程序校验。

[进入讲义 4.4 →](chapter-04.md#m-04-04)


<span id="term-044"></span>



<span id="section-44"></span>


### 模型上下文协议MCP

连接Host、Client和Server的工具与数据协议，不自动保证权限或服务可信。

[进入讲义 5.9 →](chapter-05.md#m-05-09)


<span id="term-045"></span>



<span id="section-45"></span>


### Agent间协议A2A

面向Agent发现、任务与消息交互的协议，与MCP关注点不同。

[进入讲义 5.12 →](chapter-05.md#m-05-12)


<span id="term-046"></span>



<span id="section-46"></span>


### 检查点Checkpoint

保存可恢复任务状态，不等于跨任务经验。

[进入讲义 5.11 →](chapter-05.md#m-05-11)


<span id="term-047"></span>



<span id="section-47"></span>


### 幂等性Idempotency

同一操作重复提交不重复产生预期外副作用，需要执行系统支持。

[进入讲义 14.7 →](chapter-14.md#m-14-07)


<span id="term-048"></span>



<span id="section-48"></span>


### 上下文组装Context assembly

决定本轮输入包含什么、来自哪里、以何种结构呈现。

[进入讲义 7.1 →](chapter-07.md#m-07-01)


<span id="term-049"></span>



<span id="section-49"></span>


### 上下文压缩Compaction

用更紧凑表示维持任务连续性，可能有信息损失或不透明状态。

[进入讲义 7.6 →](chapter-07.md#m-07-06)


<span id="term-050"></span>



<span id="section-50"></span>


### 信息外置Offloading

将完整资料放在外部，以引用替代常驻输入，必要时再取回。

[进入讲义 7.1 →](chapter-07.md#m-07-01)


<span id="term-051"></span>



<span id="section-51"></span>


### 检索增强生成RAG

利用外部检索证据辅助生成，检索与生成都有独立失败模式。

[进入讲义 8.1 →](chapter-08.md#m-08-01)


<span id="term-052"></span>



<span id="section-52"></span>


### 词项相关性方法BM25

基于词项统计与长度等因素排序，适合精确词项信息。

[进入讲义 8.2 →](chapter-08.md#m-08-02)


<span id="term-053"></span>



<span id="section-53"></span>


### 稠密检索Dense retrieval

利用向量表示召回语义相关内容，相似度不是正确概率。

[进入讲义 8.4 →](chapter-08.md#m-08-04)


<span id="term-054"></span>



<span id="section-54"></span>


### 混合检索Hybrid search

结合词项、向量等不同召回方式，需要融合与去重。

[进入讲义 8.2 →](chapter-08.md#m-08-02)


<span id="term-055"></span>



<span id="section-55"></span>


### 重排序Reranking

对候选结果进行更细致排序，不能补回未被召回的全部证据。

[进入讲义 8.3 →](chapter-08.md#m-08-03)


<span id="term-056"></span>



<span id="section-56"></span>


### 倒数排名融合RRF

按名次而非原始分数融合多个列表。

[进入讲义 8.3 →](chapter-08.md#m-08-03)


<span id="term-057"></span>



<span id="section-57"></span>


### 内容切分Chunking

将文档或代码分成检索单元，需平衡独立语义、粒度和上下文。

[进入讲义 8.2 →](chapter-08.md#m-08-02)


<span id="term-058"></span>



<span id="section-58"></span>


### 抽象语法树AST

代码语法结构表示，不自动包含全部类型与运行时语义。

[进入讲义 8.10 →](chapter-08.md#m-08-10)


<span id="term-059"></span>



<span id="section-59"></span>


### 语言服务器协议LSP

提供定义、引用、诊断等语言服务的交互约定。

[进入讲义 8.11 →](chapter-08.md#m-08-11)


<span id="term-060"></span>



<span id="section-60"></span>


### 前k项召回率Recall@k

必要相关结果中有多少出现在前k项，依赖相关性标签。

[进入讲义 8.16 →](chapter-08.md#m-08-16)


<span id="term-061"></span>



<span id="section-61"></span>


### 前k项精确率Precision@k

前k项中相关结果的比例，与召回关注点不同。

[进入讲义 8.16 →](chapter-08.md#m-08-16)


<span id="term-062"></span>



<span id="section-62"></span>


### 平均倒数排名MRR

对各查询首个相关结果排名倒数取平均。

[进入讲义 8.16 →](chapter-08.md#m-08-16)


<span id="term-063"></span>



<span id="section-63"></span>


### 归一化折损累计增益nDCG

同时考虑排序位置与相关程度的指标。

[进入讲义 8.16 →](chapter-08.md#m-08-16)


<span id="term-064"></span>



<span id="section-64"></span>


### 工作记忆Working memory

支持当前任务的可见信息与状态。

[进入讲义 9.1 →](chapter-09.md#m-09-01)


<span id="term-065"></span>



<span id="section-65"></span>


### 情景记忆Episodic memory

保存具体经历、事件和结果。

[进入讲义 9.1 →](chapter-09.md#m-09-01)


<span id="term-066"></span>



<span id="section-66"></span>


### 语义记忆Semantic memory

保存带范围与证据的知识或事实。

[进入讲义 9.1 →](chapter-09.md#m-09-01)


<span id="term-067"></span>



<span id="section-67"></span>


### 程序性记忆Procedural memory

保存可复用方法与流程，需避免经验过拟合。

[进入讲义 9.1 →](chapter-09.md#m-09-01)


<span id="term-068"></span>



<span id="section-68"></span>


### 记忆污染Memory pollution

错误或恶意内容被保存并在以后误用，可能形成自我强化。

[进入讲义 9.9 →](chapter-09.md#m-09-09)


<span id="term-069"></span>



<span id="section-69"></span>


### 技能工作包Skill

按需提供专业指导与资源，不是参数训练或确定性权限控制。

[进入讲义 10.1 →](chapter-10.md#m-10-01)


<span id="term-070"></span>



<span id="section-70"></span>


### 渐进披露Progressive disclosure

先提供入口元数据，再按需展开正文与资源。

[进入讲义 10.2 →](chapter-10.md#m-10-02)


<span id="term-071"></span>



<span id="section-71"></span>


### 事件钩子Hook

在明确生命周期节点运行程序化动作。

[进入讲义 6.11 →](chapter-06.md#m-06-11)


<span id="term-072"></span>



<span id="section-72"></span>


### 控制权交接Handoff

将任务控制移交给另一Agent，与工具式调用返回不同。

[进入讲义 10.9 →](chapter-10.md#m-10-09)


<span id="term-073"></span>



<span id="section-73"></span>


### 协调者—工作者Orchestrator-worker

由主角色分解和协调相对独立任务的模式。

[进入讲义 10.7 →](chapter-10.md#m-10-07)


<span id="term-074"></span>



<span id="section-74"></span>


### 架构决策记录ADR

记录重要选择的背景、方案与后果，便于以后重新判断。

[进入讲义 11.11 →](chapter-11.md#m-11-11)


<span id="term-075"></span>



<span id="section-75"></span>


### 评测Eval

用明确任务、条件、评分和证据判断系统能力与回归。

[进入讲义 12.1 →](chapter-12.md#m-12-01)


<span id="term-076"></span>



<span id="section-76"></span>


### 评分器Grader

根据特定标准评价结果或过程，可为程序、模型或人工。

[进入讲义 12.6 →](chapter-12.md#m-12-06)


<span id="term-077"></span>



<span id="section-77"></span>


### 至少一次成功指标pass@k

考虑k次尝试中至少一次成功，需明确采样和筛选口径。

[进入讲义 12.11 →](chapter-12.md#m-12-11)


<span id="term-078"></span>



<span id="section-78"></span>


### 重复全部成功指标pass^k

强调多次都成功的可靠性，不能与pass@k混用。

[进入讲义 12.11 →](chapter-12.md#m-12-11)


<span id="term-079"></span>



<span id="section-79"></span>


### 消融实验Ablation

移除或单独改变某机制，帮助判断其贡献。

[进入讲义 12.2 →](chapter-12.md#m-12-02)


<span id="term-080"></span>



<span id="section-80"></span>


### 概率校准Calibration

预测置信水平与相应样本真实正确频率的一致性。

[进入讲义 15.7 →](chapter-15.md#m-15-07)


<span id="term-081"></span>



<span id="section-81"></span>


### 提示注入Prompt injection

不可信内容诱导系统偏离授权目标，可能经外部材料间接发生。

[进入讲义 13.4 →](chapter-13.md#m-13-04)


<span id="term-082"></span>



<span id="section-82"></span>


### 沙箱Sandbox

限制文件、网络或执行资源影响范围的隔离环境。

[进入讲义 13.6 →](chapter-13.md#m-13-06)


<span id="term-083"></span>



<span id="section-83"></span>


### 最小权限Least privilege

只授予完成任务所必需的资源与操作权限。

[进入讲义 13.10 →](chapter-13.md#m-13-10)


<span id="term-084"></span>



<span id="section-84"></span>


### 轨迹与操作片段Trace / Span

分别描述任务因果结构和其中一次操作，注意并行重叠。

[进入讲义 14.1 →](chapter-14.md#m-14-01)


<span id="term-085"></span>



<span id="section-85"></span>


### 首Token延迟TTFT

到首次输出的等待，不等于任务最终完成时间。

[进入讲义 14.8 →](chapter-14.md#m-14-08)


<span id="term-086"></span>



<span id="section-86"></span>


### 服务目标SLO

对成功、延迟等服务行为的可度量约定。

[进入讲义 14.5 →](chapter-14.md#m-14-05)


<span id="term-087"></span>



<span id="section-87"></span>


### 退避Backoff

失败或限流后延迟重试，需有预算与错误分类。

[进入讲义 14.7 →](chapter-14.md#m-14-07)


<span id="term-088"></span>



<span id="section-88"></span>


### 低秩适配LoRA

冻结基础权重并训练低秩增量的一类参数高效方法。

[进入讲义 15.1 →](chapter-15.md#m-15-01)


<span id="term-089"></span>



<span id="section-89"></span>


### 量化低秩微调QLoRA

结合量化基础模型与低秩适配以降低训练内存。

[进入讲义 15.2 →](chapter-15.md#m-15-02)


<span id="term-090"></span>



<span id="section-90"></span>


### 量化Quantization

以较低精度表示权重或状态，影响误差、存储与执行条件。

[进入讲义 15.3 →](chapter-15.md#m-15-03)


<span id="term-091"></span>



<span id="section-91"></span>


### 知识蒸馏Distillation

通过教师信号训练学生，能力迁移受数据与容量限制。

[进入讲义 15.4 →](chapter-15.md#m-15-04)


<span id="term-092"></span>



<span id="section-92"></span>


### 界面定位GUI grounding

把语言目标与图形界面位置关联，不等于完成整个任务。

[进入讲义 15.13 →](chapter-15.md#m-15-13)


<span id="term-093"></span>



<span id="section-93"></span>


### 机制可解释性Mechanistic interpretability

研究内部表示与计算如何导致行为，需要区别相关与因果。

[进入讲义 15.17 →](chapter-15.md#m-15-17)


<span id="term-094"></span>



<span id="section-94"></span>


### 稀疏自编码器Sparse autoencoder

通过重建与稀疏约束提取表示特征的研究工具。

[进入讲义 15.16 →](chapter-15.md#m-15-16)

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)