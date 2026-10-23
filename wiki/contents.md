---
title: "目录与学习路径"
description: "AI系统工程：本地教学正文与可追溯图表"
---

# 目录与学习路径

基础课程建立可复算的完整过程；系统机制解释实现边界、真实调用链与工程取舍。所有章节沿同一目录阅读，不需要在平行教程间拼接。

模型部分的顺序固定为：输入与共通计算 → 训练、验证及保存 → 加载与推理 → 资源优化。案例、代码和数值记录放在实验区，作为正文的证据。


<span id="foundations"></span>


## 基础课程

### 输入与表示

- [F01｜模型的生命周期：对象、参数、训练与推理](foundations/01.md)
- [F02｜一排数、一张表和一叠表：读懂张量与形状](foundations/02.md)
- [F03｜文字怎样成为编号：分词、词表与序列边界](foundations/03.md)
- [F04｜从多句话到训练批次：组批、补齐与标签位置](foundations/04.md)
- [F05｜Embedding与位置：从编号查表到模型输入](foundations/05.md)
- [F06｜“放到设备”是什么：数据类型、内存、CPU与GPU](foundations/06.md)

### 共通计算

- [F07｜模型最常做的算术：加权求和、点积与矩阵乘法](foundations/07.md)
- [F08｜reshape、转轴、广播：形状变了，内容未必算过](foundations/08.md)
- [F09｜概率、指数与softmax：把分数变成比例](foundations/09.md)
- [F10｜参数、前向与归一化：同一输入如何变成可用表示](foundations/10.md)
- [F11｜Attention逐步计算：先算相关分数，再混合内容](foundations/11.md)
- [F12｜Mask不是黑箱：把“谁能看谁”写成一张表](foundations/12.md)
- [F13｜位置编号与RoPE：先懂位置，再懂旋转](foundations/13.md)
- [F14｜完成一次前向：残差、前馈网络与词表分数](foundations/14.md)

### 训练与验证

- [F15｜导数、梯度与链式法则：训练怎样找到调整方向](foundations/15.md)
- [F16｜一次训练从头到尾：标签、损失、更新、验证与保存](foundations/16.md)
- [F17｜后训练：监督微调、偏好、奖励与参数适配](foundations/17.md)

### 推理与资源

- [F18｜加载训练结果：逐个预测、选择与停止](foundations/18.md)
- [F19｜KV缓存：在同一结果下复用历史计算](foundations/19.md)
- [F20｜低秩、量化、专家：先看究竟少算了什么](foundations/20.md)
- [F21｜算得快与装得下：复杂度、带宽、批处理和并行](foundations/21.md)

### Agent与上下文

- [F22｜Agent不是另一个神经网络：用一次读文件讲清循环](foundations/22.md)
- [F23｜API与流式协议：请求如何变成可执行数据](foundations/23.md)
- [F24｜状态、事件与检查点：模型知道和系统记录的区别](foundations/24.md)
- [F25｜工具与MCP：连接、发现、授权、执行四层拆开](foundations/25.md)
- [F26｜上下文组装：每轮到底给模型什么，以及为什么](foundations/26.md)
- [F27｜压缩不是魔法：摘要、原文和执行状态怎样配合](foundations/27.md)

### 知识与可靠交付

- [F28｜检索入门：目录、倒排索引、向量与近似搜索](foundations/28.md)
- [F29｜从搜索结果到可信答案：召回、重排和证据](foundations/29.md)
- [F30｜代码不是普通文档：语法树、调用关系与版本](foundations/30.md)
- [F31｜长期记忆的基础：事实、经历、流程和时间](foundations/31.md)
- [F32｜Skill、路由和多Agent：先理解谁负责什么](foundations/32.md)
- [F33｜重试、幂等和事务：为什么超时不是失败证明](foundations/33.md)
- [F34｜工程质量的基础：需求、反例、测试与审查](foundations/34.md)

### 评价与生产

- [F35｜评测指标的分母：成功率、精确率、召回率和pass](foundations/35.md)
- [F36｜别被几个百分点骗了：随机性、样本与统计判断](foundations/36.md)
- [F37｜安全基础：数据能影响模型，但不能因此获得权限](foundations/37.md)
- [F38｜看懂生产运行：Trace、队列、成本和回滚](foundations/38.md)
- [F39｜多模态与可信度：图片怎样成为输入，解释为什么有限](foundations/39.md)
- [F40｜从基础概念到系统分析：怎样定位问题，而不是再堆技术](foundations/40.md)


<span id="systems"></span>

<span id="chapters"></span>


## 系统机制

### 模型输入与前向

- [01｜输入究竟是什么：从用户的一句话到模型张量](chapters/01.md)
- [02｜一次Transformer前向：逐张量、逐算子讲明白](chapters/02.md)
- [03｜注意力的深入追问：位置、掩码、多头与反向传播](chapters/03.md)

### 训练与适配

- [04｜训练机制：损失、完整反向传播与参数更新](chapters/04.md)
- [05｜后训练与模型定制：目标、结构和参数适配](chapters/05.md)

### 推理与服务

- [06｜推理机制：加载、解码策略与连续生成](chapters/06.md)
- [07｜KV Cache、FlashAttention与PagedAttention的内部过程](chapters/07.md)
- [08｜推理服务：调度、吞吐、延迟和并行](chapters/08.md)

### Agent与工具

- [09｜Agent一次任务的完整循环：谁在思考，谁在执行](chapters/09.md)
- [10｜模型输出怎样变成真实工具调用：协议与执行边界](chapters/10.md)
- [11｜工具设计与MCP：从连接到可控执行](chapters/11.md)
- [12｜Codex、Claude Code、Copilot：从公开事实到可诊断运行链](chapters/12.md)

### 上下文与知识

- [13｜每一轮Prompt怎样组装：上下文是一条数据管线](chapters/13.md)
- [14｜上下文压缩：到底压掉什么，丢失后又如何恢复](chapters/14.md)
- [15｜检索离线链路：文档怎样变成可查询索引](chapters/15.md)
- [16｜检索在线链路：召回、融合、重排与证据充足性](chapters/16.md)
- [17｜代码智能：从文本搜索到符号、版本与运行证据](chapters/17.md)
- [18｜长期记忆：写入、检索、冲突、失效与遗忘](chapters/18.md)
- [19｜Skills与路由：怎样加载刚好需要的专业能力](chapters/19.md)

### 协作与交付

- [20｜多Agent：并行的收益与交接的损失](chapters/20.md)
- [21｜可靠执行：重试、幂等、崩溃与状态恢复](chapters/21.md)
- [22｜工程质量：从需求到测试，再到真正可交付的代码](chapters/22.md)

### 评价、安全与应用

- [23｜Evaluation：怎样证明一次优化真有收益](chapters/23.md)
- [24｜安全：指令边界、沙箱、权限与记忆污染](chapters/24.md)
- [25｜生产运行：Trace、成本、队列、灰度与回滚](chapters/25.md)
- [26｜深度应用：把组件组合成能解释的工作系统](chapters/26.md)
- [27｜事实可靠性、多模态与可解释性：能力边界在哪里](chapters/27.md)
- [28｜研究深水区与系统综合判断](chapters/28.md)


<span id="cases"></span>


## 贯通案例

[全程拆解A｜一次输入怎样变成三个输出Token](walkthroughs/a.md)

[全程拆解B｜一次仓库修复的每轮输入、输出、工具和恢复](walkthroughs/b.md)

[全程拆解C｜从文档入库到检索、回答、记忆更新和遗忘](walkthroughs/c.md)

[全程拆解D｜一次“变慢且变差”的Agent回归怎样查到根因](walkthroughs/d.md)


<span id="practice"></span>


## 实验与复算

[把数字改一下，看每一步怎样变化](labs.md)

[模型实验：逐步查看训练与推理的中间值](labs/model-viewer.md)

[模型实验：参数、前向与梯度记录](labs/model-values.md)

[模型实验：完整代码与运行结果](labs/model-run.md)

[模型实验源码与原始参数](reference/model-code.md)

[模型机制：原理来源与接口版本](reference/model-sources.md)


<span id="appendices"></span>

<span id="engineering-reading"></span>


## 研修与索引

[专题研修：实现、验证与应用](studies/index.md)

[拓展阅读：研究主题与中文讲义](reading-notes/index.md)

[工程深挖：从机制到故障边界](engineering/index.md)

[正文图解与细算索引](mechanisms/index.md)

[公式与术语：先认识对象，再理解运算](concepts.md)

[术语与符号速查](glossary.md)

[参考资料与适用范围](sources.md)