---
title: "动态图解：把每一步看清楚"
description: "AI系统工程：本地教学正文与可追溯图表"
---

图解 · 运行过程 · 工程取舍


<span id="page-title"></span>


# 动态图解：把每一步看清楚

从一条输入开始，沿着数值、消息、证据和执行状态逐步看系统怎样运作。

图解中的输入与条件始终在图前说明。主张“保持结果相同”的优化会说明保持什么、在哪些假设下成立；近似优化则显示它改变了什么。

**推荐先看两条完整链路：** [文字输入 → 首次预测 → 下一轮 → EOS](visual/F15.md)　[用户 → 模型 → 工具 → 结果回填](visual/F22.md)

[优化比较索引](visual/optimizations.md) · [各章图解对应表](visual/coverage.md) · [程序与检查范围](visual/verification.md)


<span id="group-1"></span>


## 数字与输入表示

![一句话经过了哪些不同的对象：用户文字](figures/640c2cc11158fce4.svg)

F01 · 6步
<span id="topic-1"></span>


### [一句话经过了哪些不同的对象](visual/F01.md)

输入框中的文字，什么时候才变成模型能计算的东西？

![新增一个轴，究竟多了什么：先数一排编号](figures/4fc9e0b6758cd925.svg)

F02 · 4步
<span id="topic-2"></span>


### [新增一个轴，究竟多了什么](visual/F02.md)

[2,3]为什么变成[2,3,4]？

![文字、字节、Token、编号是四件事：原文字](figures/dc7e515f78fa535a.svg)

F03 · 6步
<span id="topic-3"></span>


### [文字、字节、Token、编号是四件事](visual/F03.md)

为什么不能把“一个汉字”当成“一次生成”？

![组批没有把两句话混成一句：长度不同](figures/d1ae6e52e7825948.svg)

F04 · 4步
<span id="topic-4"></span>


### [组批没有把两句话混成一句](visual/F04.md)

为了整齐补上的PAD，会不会被模型误当成内容？

![Embedding是查一行，不是把编号转二进制：为“我”取第1行](figures/01d566623232c10e.svg)

F05 · 5步
<span id="topic-5"></span>


### [Embedding是查一行，不是把编号转二进制](visual/F05.md)

一组浮点数怎样替代一个Token编号？

![数据搬到GPU，改变的是位置而不是含义：先数对象](figures/6ed8603f233b7e34.svg)

F06 · 4步
<span id="topic-6"></span>


### [数据搬到GPU，改变的是位置而不是含义](visual/F06.md)

“装得下”和“算得快”为什么不是同一回事？


<span id="group-2"></span>


## 模型计算、生成与结束

![矩阵乘法像逐格填写配方结果：填输出的第0行第0列](figures/3e4f881a20bfe1de.svg)

F07 · 4步
<span id="topic-7"></span>


### [矩阵乘法像逐格填写配方结果](visual/F07.md)

一个输出格子的数，到底从哪些输入格子来？

![改摆法与改数值，分开看：原来的两行](figures/50c387bfced5a748.svg)

F08 · 4步
<span id="topic-8"></span>


### [改摆法与改数值，分开看](visual/F08.md)

reshape、转置、广播为什么不能互换？

![Softmax不是直接把分数除以它们的和：分数不是份额](figures/720b763597016f29.svg)

F09 · 5步
<span id="topic-9"></span>


### [Softmax不是直接把分数除以它们的和](visual/F09.md)

怎样从同一组三个分数，一步不跳走到抽样？

![网络层是在重组数值，不是在生成隐藏句子：固定输入与参数](figures/fc6378d3b89a6982.svg)

F10 · 6步
<span id="topic-10"></span>


### [网络层是在重组数值，不是在生成隐藏句子](visual/F10.md)

为什么多层之间还要放一个非线性函数？

![Q/K/V：先算从哪读，再算读进多少：同一输入，三条参数路径](figures/2d31c44cb733ea5a.svg)

F11 · 5步
<span id="topic-11"></span>


### [Q/K/V：先算从哪读，再算读进多少](visual/F11.md)

Query、Key、Value各自是什么数，为什么分三条路径？

![Mask是可见性表，不是额外语义：处理绝对位置0](figures/a1c8c4cf34c01dbd.svg)

F12 · 5步
<span id="topic-12"></span>


### [Mask是可见性表，不是额外语义](visual/F12.md)

怎样防止读到未来，或者把PAD读成内容？

![位置怎样进入数值计算：位置0旋转到0度](figures/54578cd163e4d047.svg)

F13 · 5步
<span id="topic-13"></span>


### [位置怎样进入数值计算](visual/F13.md)

同一个Token出现在不同位置，为什么还需要额外处理？

![一层Transformer不是只有Attention：进入本层](figures/131ac4028baf06c0.svg)

F14 · 6步
<span id="topic-14"></span>


### [一层Transformer不是只有Attention](visual/F14.md)

读其他位置之后，为什么还要残差、归一化和FFN？

![一次输入如何连着预测，直到结束：输入是“我爱”，还没有输出](figures/70f7453c7d22aa60.svg)

F18 · 10步
<span id="topic-15"></span>


### [一次输入如何连着预测，直到结束](visual/F15.md)

预测到的Token什么时候显示，什么时候成为下一轮输入？

![KV Cache：留下算过的，不省掉该读的：两层分别保存历史](figures/b077930c445b006a.svg)

F19 · 5步
<span id="topic-16"></span>


### [KV Cache：留下算过的，不省掉该读的](visual/F16.md)

为什么少算了很多步骤，下一Token仍能看到历史？


<span id="group-3"></span>


## 训练与计算资源

![梯度像坡度，学习率像迈步大小：预测偏小，但参数还没变](figures/43c9750dd554ff44.svg)

F15 · 4步
<span id="topic-17"></span>


### [梯度像坡度，学习率像迈步大小](visual/F17.md)

为什么“梯度下降”有时让参数增大？

![训练：给每个位置一道“下一项”题：把输入和目标错开一格](figures/aff96cb2ac5ffb2c.svg)

F16 · 5步
<span id="topic-18"></span>


### [训练：给每个位置一道“下一项”题](visual/F18.md)

为什么训练看完整句，生成却只能往前走？

![后训练改变行为，奖励不是事实裁判：同一问题，两份回答](figures/ad736b9a23b439f5.svg)

F17 · 6步
<span id="topic-19"></span>


### [后训练改变行为，奖励不是事实裁判](visual/F19.md)

既然模型会接下一Token，为什么还要SFT、偏好训练？

![省参数、省位数、少激活不是同一种优化：原有大权重](figures/18453a1f2a415eb6.svg)

F20 · 6步
<span id="topic-20"></span>


### [省参数、省位数、少激活不是同一种优化](visual/F20.md)

LoRA、量化、MoE到底各自省了哪一部分？

![算得慢，可能是东西搬得慢：先问算力和搬运谁更慢](figures/8e644a205a94010b.svg)

F21 · 4步
<span id="topic-21"></span>


### [算得慢，可能是东西搬得慢](visual/F21.md)

为什么一块算力更高的GPU，不一定让任务同比变快？


<span id="group-4"></span>


## Agent、协议与上下文

![把一个Agent任务拆成真正发生的几轮：1. 用户任务：读config.txt中的timeout](figures/6d2e7c22f31e56b8.svg)

F22 · 8步
<span id="topic-22"></span>


### [把一个Agent任务拆成真正发生的几轮](visual/F22.md)

同一句用户任务，为什么可能调用模型不止一次？

![字符完整、事件完整、工具参数完整是三道关：收到第一段字节](figures/c5a49436657cdf26.svg)

F23 · 4步
<span id="topic-23"></span>


### [字符完整、事件完整、工具参数完整是三道关](visual/F23.md)

为什么看到半段JSON时绝对不能执行？

![任务状态不是聊天里的一句总结：准备](figures/fe48cd968f31b79d.svg)

F24 · 6步
<span id="topic-24"></span>


### [任务状态不是聊天里的一句总结](visual/F24.md)

“模型知道做过”与“系统能恢复”有什么区别？

![MCP连起接口，不自动交出权限：1. Host建立连接，Client与Server协商能力](figures/86250648adf9454a.svg)

F25 · 7步
<span id="topic-25"></span>


### [MCP连起接口，不自动交出权限](visual/F25.md)

连接、发现、模型可见和实际授权分别发生在哪里？

![每轮上下文像一份有边界的工作资料：加入规则](figures/e7310a6fc818967c.svg)

F26 · 5步
<span id="topic-26"></span>


### [每轮上下文像一份有边界的工作资料](visual/F26.md)

为什么“读得越多”有时反而越容易误解？

![压缩要保留行动所依赖的事实：原历史有很多噪声](figures/2fcb6f31838883b5.svg)

F27 · 5步
<span id="topic-27"></span>


### [压缩要保留行动所依赖的事实](visual/F27.md)

把一百轮历史压成几句话，最容易丢什么？


<span id="group-5"></span>


## 检索、记忆、协作与可靠交付

![检索先找候选，再判断能否回答：先有原文，不是先有向量](figures/a7746942c1770c15.svg)

F28 · 4步
<span id="topic-28"></span>


### [检索先找候选，再判断能否回答](visual/F28.md)

倒排索引和向量索引分别在帮什么忙？

![从两个候选列表，走到可用证据：两种搜索给出不同名次](figures/5b3b1dce213dc0f0.svg)

F29 · 5步
<span id="topic-29"></span>


### [从两个候选列表，走到可用证据](visual/F29.md)

“相关”与“足以回答”中间还差哪几步？

![代码检索不能只靠“语义相近”：文本搜索](figures/4d1e242d1988f43d.svg)

F30 · 6步
<span id="topic-30"></span>


### [代码检索不能只靠“语义相近”](visual/F30.md)

grep、AST、LSP、调用图各自看到什么？

![长期记忆不是永远正确的小纸条：1月1日 生效](figures/3ff3f6dd49814a9c.svg)

F31 · 5步
<span id="topic-31"></span>


### [长期记忆不是永远正确的小纸条](visual/F31.md)

新事实出现后，旧记忆怎样更新而不毁掉历史？

![Skill存在，为什么仍可能完全没用？：磁盘上有Skill](figures/49a68f7bc077e158.svg)

F32 · 6步
<span id="topic-32"></span>


### [Skill存在，为什么仍可能完全没用？](visual/F32.md)

从“安装了技能”到“写出了更好的代码”，中间经过什么？

![超时告诉你没收到，不告诉你没发生：请求 op-1](figures/bc1a581c700282fe.svg)

F33 · 6步
<span id="topic-33"></span>


### [超时告诉你没收到，不告诉你没发生](visual/F33.md)

为什么自动重试有时会把一次工作做两遍？

![测试是找反例，不是给代码盖绿章：明确需求](figures/25d0380d8318de01.svg)

F34 · 6步
<span id="topic-34"></span>


### [测试是找反例，不是给代码盖绿章](visual/F34.md)

为什么“测试都通过”仍可能交付错东西？


<span id="group-6"></span>


## 评测、安全与生产

![读指标，先问它的分母是谁：四种结果先分开](figures/be5b9dae2310e53a.svg)

F35 · 4步
<span id="topic-35"></span>


### [读指标，先问它的分母是谁](visual/F35.md)

为什么精确率高不等于证据找全了？

![涨了10个百分点，为什么还不能急着下结论？：同20题，两版各跑一次](figures/33272741a5370b5a.svg)

F36 · 5步
<span id="topic-36"></span>


### [涨了10个百分点，为什么还不能急着下结论？](visual/F36.md)

一次实验怎样区别真实改进与偶然波动？

![资料能影响模型，不代表获得了权限：收到外部资料](figures/ce4c7947228f6518.svg)

F37 · 6步
<span id="topic-37"></span>


### [资料能影响模型，不代表获得了权限](visual/F37.md)

为什么“模型被劝住”不能作为唯一防线？

![Trace要告诉你因果，不只是时间戳：先看一条完整任务](figures/d09e422a80f09b5b.svg)

F38 · 5步
<span id="topic-38"></span>


### [Trace要告诉你因果，不只是时间戳](visual/F38.md)

为何优化一个最显眼的步骤，整体却没变快？

![图像表示与界面行动，是两层不同问题：图像也是规则数字表](figures/ca28923eb081fb02.svg)

F39 · 4步
<span id="topic-39"></span>


### [图像表示与界面行动，是两层不同问题](visual/F39.md)

为什么看得懂截图，也可能点错按钮？

![先找错误发生在哪层，再谈换模型：现象](figures/b48c6776dd0aba49.svg)

F40 · 6步
<span id="topic-40"></span>


### [先找错误发生在哪层，再谈换模型](visual/F40.md)

什么时候该改Prompt、检索、记忆或模型？


<span id="group-7"></span>


## 优化的原因、方法与代价

![GQA/MQA：减少的是K/V组数：MHA：每个查询头有自己的K/V](figures/608bb5e343a9bc34.svg)

O01 · 4步
<span id="topic-41"></span>


### [GQA/MQA：减少的是K/V组数](visual/O01.md)

为什么查询头数没变，缓存却可以变小？

![量化：省存储，也引入近似：原来的四个浮点数](figures/bbe802d625ddb252.svg)

O02 · 4步
<span id="topic-42"></span>


### [量化：省存储，也引入近似](visual/O02.md)

为什么“4bit”不等于所有模型内存都缩到八分之一？

![LoRA：冻结大表，学习小增量：原权重并没有被删除](figures/fc76052df6f04678.svg)

O03 · 4步
<span id="topic-43"></span>


### [LoRA：冻结大表，学习小增量](visual/O03.md)

减少的是整个模型，还是需要更新的参数？

![FlashAttention：一边读一边累计，不攒整张表：普通写法先想象整张分数表](figures/c6c2f32fd6937437.svg)

O04 · 5步
<span id="topic-44"></span>


### [FlashAttention：一边读一边累计，不攒整张表](visual/O04.md)

不把完整注意力表存下来，怎样仍算出同一输出？

![PagedAttention：逻辑连续，物理可以分块：初始：A仅3个位置](figures/2420c81cf0a84b02.svg)

O05 · 4步
<span id="topic-45"></span>


### [PagedAttention：逻辑连续，物理可以分块](visual/O05.md)

缓存为什么不必为每个请求找一大块连续显存？

![连续组批：有座位空出来，就接下一位：普通批次等待整体结束](figures/6472068ab54be6ff.svg)

O06 · 4步
<span id="topic-46"></span>


### [连续组批：有座位空出来，就接下一位](visual/O06.md)

为什么设备更忙，不代表每条请求都更快？

![推测解码：草稿可以快，但必须正确校验：草稿分布与目标分布不同](figures/98c744cb98c7b3d2.svg)

O07 · 5步
<span id="topic-47"></span>


### [推测解码：草稿可以快，但必须正确校验](visual/O07.md)

为什么“让小模型先写，大模型点头”还不够准确？

![MoE：每个Token选部分计算路径：先算路由分数](figures/d26dc7b0a36ee173.svg)

O08 · 4步
<span id="topic-48"></span>


### [MoE：每个Token选部分计算路径](visual/O08.md)

为什么总参数很多，但每Token不用计算所有专家？

![Activation Checkpointing：少存一点，反向时重算：普通保存](figures/3d7f5e5cdc3a17f5.svg)

O09 · 5步
<span id="topic-49"></span>


### [Activation Checkpointing：少存一点，反向时重算](visual/O09.md)

为什么有的优化是用时间换内存，而KV缓存恰好相反？

![压缩、检索与Prompt Cache：三种不同的“省”：不区分内容，全塞进来](figures/f007bcaad4c45ea6.svg)

O10 · 4步
<span id="topic-50"></span>


### [压缩、检索与Prompt Cache：三种不同的“省”](visual/O10.md)

上下文短了、检索准了、缓存命中了，为什么不能混为一谈？

![多Agent：可并行的工作，比Agent数量重要：顺序完成两个独立子任务](figures/e9b42be7d3784179.svg)

O11 · 4步
<span id="topic-51"></span>


### [多Agent：可并行的工作，比Agent数量重要](visual/O11.md)

为什么任务拆得更细，有时完成得更慢、更差？

![模型路由：便宜一次，不一定便宜一项成功任务：先给全部20题用便宜模型](figures/7e43cfc622d08a5c.svg)

O12 · 4步
<span id="topic-52"></span>


### [模型路由：便宜一次，不一定便宜一项成功任务](visual/O12.md)

怎样判断换小模型是优化，还是把成本挪到返工？