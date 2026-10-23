---
title: "工程深挖：从机制到故障边界"
description: "AI系统工程：本地教学正文与可追溯图表"
---


<span id="eng-index-title"></span>


# 工程深挖：从机制到故障边界

能解释概念，还要能回答：哪种写法会悄悄出错、错误会出现在哪一层，以及怎样用实验把它抓出来。

本组内容嵌在系统篇相应问题之后，并在专题研修中提供跨步骤故障案例。这里是定位入口，不是要求读者把正文跳过。建议沿“机制与已有算例 → 工程深挖 → 本地反例 → 连续追问”的顺序阅读。

新增证据核对日期：**2026年10月21日**。当前文档、固定历史修复、固定源码提交和本地实测分别注明；不把“今天重新读取”说成“今天发布”。原有参考资料仍按其原注版本理解，并未一律更新成最新产品行为。

[来源、版本与证据范围](sources.md) · [完整实验代码与实际结果](labs.md)


<span id="eng-contract"></span>


## 深度学习应能回答的六个问题

首先确定接口收到什么对象，接着明确前提和不变量，再构造会失败的最小反例；修复时解释改动的收益与代价；用独立断言或对照实现验证，最后说明结论在哪些版本或环境下不能直接推广。读完后应能指出具体参数、状态或数据条件，而不是只背“多做测试、提高质量”。


<span id="eng-modules"></span>


## 按正文顺序进入56个工程问题


<span id="chapter-01"></span>


### 01｜输入究竟是什么：从用户的一句话到模型张量

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E01 | [模板已经加了BOS，再分词一次为什么会悄悄改变任务？](../chapters/01.md#engineering-E01) | 接续Q002 |
| E02 | [新增Token、绑定输出头与优化器：为什么“能查到”还不等于“能学会”？](../chapters/01.md#engineering-E02) | 接续Q004 |


<span id="chapter-02"></span>


### 02｜一次Transformer前向：逐张量、逐算子讲明白

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E03 | [投影两次、缩放两次、eval仍随机：同名Attention接口的三种陷阱](../chapters/02.md#engineering-E03) | 接续Q006 |
| E04 | [一整行都被遮住时，减最大值为什么仍救不了softmax？](../chapters/02.md#engineering-E04) | 接续Q007 |


<span id="chapter-03"></span>


### 03｜注意力的深入追问：位置、掩码、多头与反向传播

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E05 | [布尔mask语义相反，加缓存后is\_causal还可能对齐错边](../chapters/03.md#engineering-E05) | 接续Q009 |
| E06 | [位置编号、缓存槽位和RoPE：同叫position却不是同一个数](../chapters/03.md#engineering-E06) | 接续Q010 |


<span id="chapter-04"></span>


### 04｜输出是怎样一个Token一个Token生成的

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E07 | [给了attention\_mask，为什么右补齐生成仍可能读错logits？](../chapters/06.md#engineering-E07) | 接续Q013 |
| E08 | [温度、Top-p、禁词：为什么“参数都一样”也可能不是同一采样算法？](../chapters/06.md#engineering-E08) | 接续Q014 |


<span id="chapter-05"></span>


### 05｜训练的一步：从正确标签到参数真正改变

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E10 | [混合精度与重计算：顺序错误会让优化器悄悄走错一步](../chapters/04.md#engineering-E10) | 接续Q018 |
| E09 | [梯度累积的隐蔽偏差：平均的是批次，还是有效Token？](../chapters/04.md#engineering-E09) | 接续Q020 |


<span id="chapter-06"></span>


### 06｜后训练、MoE与模型定制：能力和行为如何改变

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E11 | [DPO真正比较的不是“好答案概率”，而是相对参考策略的改变量](../chapters/05.md#engineering-E11) | 接续Q021 |
| E12 | [LoRA第一步A梯度为零，可能是设计正常，不是反传断了](../chapters/05.md#engineering-E12) | 接续Q024 |


<span id="chapter-07"></span>


### 07｜KV Cache、FlashAttention与PagedAttention的内部过程

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E13 | [缓存共享的两个危险：身份不完整与可变对象别名](../chapters/07.md#engineering-E13) | 接续Q025 |
| E14 | [在线softmax为什么必须重标定旧累积量，而不是平均各块答案？](../chapters/07.md#engineering-E14) | 接续Q027 |


<span id="chapter-08"></span>


### 08｜推理服务：调度、吞吐、延迟和并行

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E15 | [吞吐下降但GPU很忙：可能是KV抢占重算，而不是算力不够](../chapters/08.md#engineering-E15) | 接续Q029 |
| E16 | [推测采样拒绝草稿后，为什么不能直接按目标分布再抽一次？](../chapters/08.md#engineering-E16) | 接续Q031 |


<span id="chapter-09"></span>


### 09｜Agent一次任务的完整循环：谁在思考，谁在执行

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E17 | [有previous\_response\_id，为什么仍可能丢失规则或工具上下文？](../chapters/09.md#engineering-E17) | 接续Q035 |
| E18 | [模型结束、工具结束、任务完成：三种“完成”不能用同一布尔值](../chapters/09.md#engineering-E18) | 接续Q036 |


<span id="chapter-10"></span>


### 10｜模型输出怎样变成真实工具调用：协议与执行边界

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E19 | [流式工具调用：UTF-8完整、JSON完整、调用完整是三件事](../chapters/10.md#engineering-E19) | 接续Q038 |
| E20 | [严格JSON为什么仍不能直接驱动数据库写入？](../chapters/10.md#engineering-E20) | 接续Q040 |


<span id="chapter-11"></span>


### 11｜工具设计与MCP：从连接到可控执行

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E21 | [MCP能连接却少了工具：初始化、分页和错误层级怎样逐项查？](../chapters/11.md#engineering-E21) | 接续Q042 |
| E22 | [令牌受众、权限范围与会话ID：三种“凭证”不能互相替代](../chapters/11.md#engineering-E22) | 接续Q044 |


<span id="chapter-12"></span>


### 12｜Codex、Claude Code、Copilot：从公开事实到可诊断运行链

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E23 | [Codex源码追问：注册、可见、可达、获授权为什么要分四步？](../chapters/12.md#engineering-E23) | 接续Q045 |
| E24 | [同样叫子Agent，为什么Claude与Copilot的“继承”不能凭感觉？](../chapters/12.md#engineering-E24) | 接续Q046 |


<span id="chapter-13"></span>


### 13｜每一轮Prompt怎样组装：上下文是一条数据管线

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E26 | [上下文预算不只算已读文件：工具结果、生成与证据依赖还要预留](../chapters/13.md#engineering-E26) | 接续Q050 |
| E25 | [语义没变却缓存失效：精确前缀、工具规格与动态字段怎样相互影响？](../chapters/13.md#engineering-E25) | 接续Q051 |


<span id="chapter-14"></span>


### 14｜上下文压缩：到底压掉什么，丢失后又如何恢复

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E27 | [压缩结果为什么不能只留下那个“看起来最浓缩”的项目？](../chapters/14.md#engineering-E27) | 接续Q053 |
| E28 | [压缩期间工具结果刚好回来：一次历史替换如何丢掉真实进展？](../chapters/14.md#engineering-E28) | 接续Q054 |


<span id="chapter-15"></span>


### 15｜检索离线链路：文档怎样变成可查询索引

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E29 | [向量维度相同，为什么查询和索引仍可能根本不在一个空间？](../chapters/15.md#engineering-E29) | 接续Q059 |
| E30 | [向量查询带了WHERE，为什么仍可能返回不足k条？](../chapters/15.md#engineering-E30) | 接续Q060 |


<span id="chapter-16"></span>


### 16｜检索在线链路：召回、融合、重排与证据充足性

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E31 | [RRF不看原始分数，为什么重复来源仍会把排名带偏？](../chapters/16.md#engineering-E31) | 接续Q061 |
| E32 | [相关、可引用、足以支持结论：证据要过三道不同的门](../chapters/16.md#engineering-E32) | 接续Q063 |


<span id="chapter-17"></span>


### 17｜代码智能：从文本搜索到符号、版本与运行证据

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E33 | [代码位置的单位错一个，编辑就可能改错字符：UTF-8、UTF-16与版本号](../chapters/17.md#engineering-E33) | 接续Q065 |
| E34 | [HEAD没变为什么证据已经过期？工作树、未保存buffer与索引快照](../chapters/17.md#engineering-E34) | 接续Q066 |


<span id="chapter-18"></span>


### 18｜长期记忆：写入、检索、冲突、失效与遗忘

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E35 | [“什么时候是真的”与“什么时候知道的”：记忆时间必须拆开](../chapters/18.md#engineering-E35) | 接续Q071 |
| E36 | [删掉原文不等于遗忘：摘要、缓存与经验条目也有依赖](../chapters/18.md#engineering-E36) | 接续Q072 |


<span id="chapter-19"></span>


### 19｜Skills与路由：怎样加载刚好需要的专业能力

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E37 | [Skill未生效时，为什么反复改description常常改错层？](../chapters/19.md#engineering-E37) | 接续Q073 |
| E38 | [小模型加回退真的省钱吗？关键在错误能否被发现](../chapters/19.md#engineering-E38) | 接续Q076 |


<span id="chapter-20"></span>


### 20｜多Agent：并行的收益与交接的损失

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E39 | [两个人改不同文件，为什么合并后仍会坏？](../chapters/20.md#engineering-E39) | 接续Q079 |
| E40 | [两个审查Agent都通过，为什么不能把错误率直接相乘？](../chapters/20.md#engineering-E40) | 接续Q080 |


<span id="chapter-21"></span>


### 21｜可靠执行：重试、幂等、崩溃与状态恢复

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E41 | [外部动作成功、日志没来得及确认：为什么本地事务无法保证只执行一次？](../chapters/21.md#engineering-E41) | 接续Q082 |
| E42 | [三层各重试三次，为什么最底层会被打27次？](../chapters/21.md#engineering-E42) | 接续Q084 |


<span id="chapter-22"></span>


### 22｜工程质量：从需求到测试，再到真正可交付的代码

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E43 | [测试命令退出0，为什么仍可能一条有效测试都没做？](../chapters/22.md#engineering-E43) | 接续Q086 |
| E44 | [快照看着没变不等于性质没坏：怎样让测试能杀死错误实现？](../chapters/22.md#engineering-E44) | 接续Q088 |


<span id="chapter-23"></span>


### 23｜Evaluation：怎样证明一次优化真有收益

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E45 | [成功率涨了几个点，为什么还不能宣布优化有效？](../chapters/23.md#engineering-E45) | 接续Q091 |
| E46 | [LLM裁判的盲点：换个左右顺序，冠军就变了](../chapters/23.md#engineering-E46) | 接续Q092 |


<span id="chapter-24"></span>


### 24｜安全：指令边界、沙箱、权限与记忆污染

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E47 | [路径在允许目录下，为什么仍可能越界？symlink与检查后替换](../chapters/24.md#engineering-E47) | 接续Q094 |
| E48 | [用户确认过一次，模型改了参数还能沿用批准吗？](../chapters/24.md#engineering-E48) | 接续Q095 |


<span id="chapter-25"></span>


### 25｜生产运行：Trace、成本、队列、灰度与回滚

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E49 | [墙钟、Span总时长、p95、成功成本：指标名字相似，算错就会选错优化](../chapters/25.md#engineering-E49) | 接续Q098 |
| E50 | [只回滚模型名为什么可能越滚越乱？系统版本是一组向量](../chapters/25.md#engineering-E50) | 接续Q100 |


<span id="chapter-26"></span>


### 26｜深度应用：把组件组合成能解释的工作系统

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E51 | [“根据材料可退款”与“现在可以执行退款”中间还缺什么？](../chapters/26.md#engineering-E51) | 接续Q101 |
| E52 | [截图坐标为什么不能直接拿去点击？缩放、DPR与页面变化](../chapters/26.md#engineering-E52) | 接续Q104 |


<span id="chapter-27"></span>


### 27｜事实可靠性、多模态与可解释性：能力边界在哪里

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E53 | [只回答有把握的问题，准确率上升为何可能只是覆盖率下降？](../chapters/27.md#engineering-E53) | 接续Q105 |
| E54 | [注意力热图最亮的位置，为什么不一定是答案的主要原因？](../chapters/27.md#engineering-E54) | 接续Q108 |


<span id="chapter-28"></span>


### 28｜研究深水区与系统综合判断

| 编号 | 核心问题 | 正文位置 |
| --- | --- | --- |
| E55 | [训练计算最优，为什么不一定是产品全生命周期最便宜？](../chapters/28.md#engineering-E55) | 接续Q109 |
| E56 | [深度排障的终点不是“换更强模型”，而是找出失效的不变量](../chapters/28.md#engineering-E56) | 接续Q112 |


<span id="eng-dossiers"></span>


## 跨步骤故障案例

这些案例连接多个接口和持久状态，明确“哪个检查先做、为何有辨别力、哪些实验没做”。案例中的自造输入不冒充真实线上事故；公开历史修复另有明确来源。

[D01 · 故障实验：为什么无缓存前向正确、增量前向却失真？](../studies/chapters/02.md#engineering-D01)[D02 · 真实修复阅读：从梯度累积事故到一份可区分错误目标的测试](../studies/chapters/03.md#engineering-D02)[D03 · 故障注入：在副作用提交之后立刻杀掉执行进程](../studies/chapters/08.md#engineering-D03)[D04 · 故障实验：用两条数据库连接抓住压缩覆盖新事件](../studies/chapters/12.md#engineering-D04)[D05 · 检索诊断：先查表示空间，再查授权候选，最后查融合排序](../studies/chapters/13.md#engineering-D05)[D06 · 记忆诊断：错误不在“没搜到”，而在拿错时间、拿到已撤销结论](../studies/chapters/15.md#engineering-D06)[D07 · 评测诊断：净增一题、一次Bootstrap与一个永远选左边的裁判](../studies/chapters/19.md#engineering-D07)[D08 · 运行诊断：关键路径、重试放大与回滚后的状态兼容](../studies/chapters/21.md#engineering-D08)

AI系统工程：从基础到内部 · [工程深挖目录](index.md) · [依据与版本](sources.md)