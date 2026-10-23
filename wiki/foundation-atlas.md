---
title: "基础篇逐节图解索引"
description: "AI系统工程：本地教学正文与可追溯图表"
---

# 基础篇逐节图解索引

从第一节到第四十节，每张图都放在对应解释的附近。点击下面的小节可直接跳到具体的“输入、操作、结果”图解，避免只在章首看一张总览。

本索引包含201张节内图解与23张逐格计算图。正文的例题、自检、程序和参考资料仍在原位置。


<span id="topic-1"></span>


### F01 · 本节图解

[从信息对象认识AI系统](foundations/01.md#fdiag-01-01)[模型不是一位住在电脑里、直接看见所有文件的人](foundations/01.md#fdiag-01-02)[用三个容易混淆的句子检查边界](foundations/01.md#fdiag-01-03)[本书的数字是怎么来的](foundations/01.md#fdiag-01-04)[阅读准备](foundations/01.md#fdiag-01-05)


<span id="topic-2"></span>


### F02 · 本节图解

[先不背“张量是多维数组”](foundations/02.md#fdiag-02-01)[从两张表理解三个轴](foundations/02.md#fdiag-02-02)[方括号中的数字不是同一种“维度”](foundations/02.md#fdiag-02-03)[怎么找到里面的一个数](foundations/02.md#fdiag-02-04)[符号不认识时怎样读公式](foundations/02.md#fdiag-02-05)


<span id="topic-3"></span>


### F03 · 本节图解

[字符、字节和Token先分开](foundations/03.md#fdiag-03-01)[一张教学词表和两条输入](foundations/03.md#fdiag-03-02)[BPE的“学习词表”和“编码输入”不是同一阶段](foundations/03.md#fdiag-03-03)[聊天角色怎样成为输入的一部分](foundations/03.md#fdiag-03-04)[编码后还没发生什么](foundations/03.md#fdiag-03-05)


<span id="topic-4"></span>


### F04 · 本节图解

[“组批”就是让若干条输入一起处理](foundations/04.md#fdiag-04-01)[真实长度与安排长度不是一回事](foundations/04.md#fdiag-04-02)[补左边和补右边有什么区别](foundations/04.md#fdiag-04-03)[补齐不等于截断，更不等于上下文压缩](foundations/04.md#fdiag-04-04)[为什么组批可能快，也可能让一个人等更久](foundations/04.md#fdiag-04-05)


<span id="topic-5"></span>


### F05 · 本节图解

[为什么不能直接拿“编号大小”理解文字](foundations/05.md#fdiag-05-01)[用6行4列的表，表示“我爱学习”和“你爱”](foundations/05.md#fdiag-05-02)[为什么从两个轴变成三个轴](foundations/05.md#fdiag-05-03)[隐藏维度到底“隐藏”了什么](foundations/05.md#fdiag-05-04)[PAD行是零，就能不用mask吗](foundations/05.md#fdiag-05-05)


<span id="topic-6"></span>


### F06 · 本节图解

[同一个数有三种不同的问题](foundations/06.md#fdiag-06-01)[整数编号与浮点特征为何类型不同](foundations/06.md#fdiag-06-02)[对较大规模的表示算一遍存储](foundations/06.md#fdiag-06-03)[一次常见执行的实际顺序](foundations/06.md#fdiag-06-04)[为什么小任务放GPU有时不快](foundations/06.md#fdiag-06-05)


<span id="topic-7"></span>


### F07 · 本节图解

[从你已经会的平均数开始](foundations/07.md#fdiag-07-01)[点积是怎样把两排数变成一个数](foundations/07.md#fdiag-07-02)[矩阵乘法是“一次做很多个点积”](foundations/07.md#fdiag-07-03)[一个Token从4096个数变成另外4096个数，究竟是什么动作](foundations/07.md#fdiag-07-04)[转置怎样帮助“一排数分别与多行比较”](foundations/07.md#fdiag-07-05)


<span id="topic-8"></span>


### F08 · 本节图解

[为什么深度学习代码里反复改变形状](foundations/08.md#fdiag-08-01)[reshape是重新分组，不是交换行列](foundations/08.md#fdiag-08-02)[多头只是把特征轴分组吗](foundations/08.md#fdiag-08-03)[广播：用一个小对象作用到许多位置](foundations/08.md#fdiag-08-04)[内存布局与视图只需先懂一个原则](foundations/08.md#fdiag-08-05)


<span id="topic-9"></span>


### F09 · 本节图解

[分数不是概率](foundations/09.md#fdiag-09-01)[先学指数和对数需要的那一点](foundations/09.md#fdiag-09-02)[softmax一步不跳地算](foundations/09.md#fdiag-09-03)[为什么要减最大值](foundations/09.md#fdiag-09-04)[取最大与按概率抽样不是一回事](foundations/09.md#fdiag-09-05)


<span id="topic-10"></span>


### F10 · 本节图解

[从一条可调的规则认识“模型”](foundations/10.md#fdiag-10-01)[从一个系数w到一张参数表W](foundations/10.md#fdiag-10-02)[一个有两层的完整数值例子](foundations/10.md#fdiag-10-03)[为什么中间需要非线性函数](foundations/10.md#fdiag-10-04)[隐藏状态不是隐藏的中文草稿](foundations/10.md#fdiag-10-05)


<span id="topic-11"></span>


### F11 · 本节图解

[它想解决什么问题](foundations/11.md#fdiag-11-01)[进入注意力之前，X到底是什么](foundations/11.md#fdiag-11-02)[W是什么：先认识“乘法系数表”，再认识三个名字](foundations/11.md#fdiag-11-03)[Query、Key、Value各做哪一件事](foundations/11.md#fdiag-11-04)[用同一份X，把三张参数表完整乘一次](foundations/11.md#fdiag-11-05)[对“爱”这个位置，从打分一直算到新表示](foundations/11.md#fdiag-11-06)


<span id="topic-12"></span>


### F12 · 本节图解

[先给掩码一个不神秘的定义](foundations/12.md#fdiag-12-01)[因果限制怎样防止读未来](foundations/12.md#fdiag-12-02)[填充限制与因果限制怎样合在一起](foundations/12.md#fdiag-12-03)[“禁止”具体怎样改变softmax](foundations/12.md#fdiag-12-04)[已有缓存时，表为什么不再是小正方形](foundations/12.md#fdiag-12-05)


<span id="topic-13"></span>


### F13 · 本节图解

[Token是谁，和它出现在第几位，是两个问题](foundations/13.md#fdiag-13-01)[为什么不能只靠查Embedding](foundations/13.md#fdiag-13-02)[只用平面上的点认识sin与cos](foundations/13.md#fdiag-13-03)[RoPE怎样用位置改变匹配](foundations/13.md#fdiag-13-04)[为什么缓存位置不能每次从0开始](foundations/13.md#fdiag-13-05)


<span id="topic-14"></span>


### F14 · 本节图解

[先把一层写成两段，而不是一大堆缩写](foundations/14.md#fdiag-14-01)[残差连接：保留一条直接通路](foundations/14.md#fdiag-14-02)[均值、方差和标准差从两个数算起](foundations/14.md#fdiag-14-03)[LayerNorm实际规范化哪一排数](foundations/14.md#fdiag-14-04)[FFN到底做了什么](foundations/14.md#fdiag-14-05)


<span id="topic-15"></span>


### F18 · 本节图解

[最后一层还不是文字](foundations/18.md#fdiag-15-01)[为什么看最后一个有效位置](foundations/18.md#fdiag-15-02)[Prefill和Decode只是两种运行阶段](foundations/18.md#fdiag-15-03)[选出来不等于已经处理过](foundations/18.md#fdiag-15-04)[生成Token与界面显示字符的关系](foundations/18.md#fdiag-15-05)


<span id="topic-16"></span>


### F19 · 本节图解

[先从普通缓存的含义说起](foundations/19.md#fdiag-16-01)[为什么追加Token通常不改变旧K/V](foundations/19.md#fdiag-16-02)[用两层、三个历史位置数清缓存](foundations/19.md#fdiag-16-03)[为什么通常不保存历史Q来做后续注意力](foundations/19.md#fdiag-16-04)[有缓存为什么仍然不是常数时间](foundations/19.md#fdiag-16-05)


<span id="topic-17"></span>


### F15 · 本节图解

[导数是在问：稍微改一下输入，结果怎样变](foundations/15.md#fdiag-17-01)[参数训练为什么需要变化率](foundations/15.md#fdiag-17-02)[用一个参数手算一次完整更新](foundations/15.md#fdiag-17-03)[反向传播与优化器不是同一个步骤](foundations/15.md#fdiag-17-04)[有限差分怎样核对解析梯度](foundations/15.md#fdiag-17-05)


<span id="topic-18"></span>


### F16 · 本节图解

[先把“要预测什么”对齐](foundations/16.md#fdiag-18-01)[交叉熵从一个正确候选开始](foundations/16.md#fdiag-18-02)[多位置与填充怎样评分](foundations/16.md#fdiag-18-03)[把一个优化步写完整](foundations/16.md#fdiag-18-04)[Adam为什么会保存额外状态](foundations/16.md#fdiag-18-05)


<span id="topic-19"></span>


### F17 · 本节图解

[同一个“更好”，至少有三种含义](foundations/17.md#fdiag-19-01)[奖励、策略、轨迹不要一起背缩写](foundations/17.md#fdiag-19-02)[概率比到底比较什么](foundations/17.md#fdiag-19-03)[KL散度为什么像一个“不离原来太远”的约束](foundations/17.md#fdiag-19-04)[DPO的式子先用两份答案解释](foundations/17.md#fdiag-19-05)


<span id="topic-20"></span>


### F20 · 本节图解

[“低秩”先用一张重复结构的表理解](foundations/20.md#fdiag-20-01)[LoRA改的不是整个基础模型](foundations/20.md#fdiag-20-02)[量化是在有限刻度上表示数字](foundations/20.md#fdiag-20-03)[MoE为什么很多参数但只调用部分](foundations/20.md#fdiag-20-04)[蒸馏与微调究竟在干什么](foundations/20.md#fdiag-20-05)


<span id="topic-21"></span>


### F21 · 本节图解

[先区分三本账](foundations/21.md#fdiag-21-01)[O(T²)到底是什么意思](foundations/21.md#fdiag-21-02)[为什么存储足够也可能算不快](foundations/21.md#fdiag-21-03)[FlashAttention省的是什么](foundations/21.md#fdiag-21-04)[PagedAttention与连续组批](foundations/21.md#fdiag-21-05)


<span id="topic-22"></span>


### F22 · 本节图解

[先还原成普通程序](foundations/22.md#fdiag-22-01)[一个三次模型调用的完整例子](foundations/22.md#fdiag-22-02)[一轮、一回合和一个任务为什么要区分](foundations/22.md#fdiag-22-03)[工作流与自由Agent的区别](foundations/22.md#fdiag-22-04)[什么叫工具，什么叫副作用](foundations/22.md#fdiag-22-05)


<span id="topic-23"></span>


### F23 · 本节图解

[API只是程序间约定，不是智能本身](foundations/23.md#fdiag-23-01)[Schema在检查什么](foundations/23.md#fdiag-23-02)[为什么网络一次读到的不是一个完整回答](foundations/23.md#fdiag-23-03)[SSE的事件边界](foundations/23.md#fdiag-23-04)[call\_id为什么比工具名称重要](foundations/23.md#fdiag-23-05)


<span id="topic-24"></span>


### F24 · 本节图解

[“做到哪了”必须有具体对象](foundations/24.md#fdiag-24-01)[状态机从最小表开始](foundations/24.md#fdiag-24-02)[事件与快照分别保存什么](foundations/24.md#fdiag-24-03)[版本号为什么重要](foundations/24.md#fdiag-24-04)[检查点保存恢复所需信息](foundations/24.md#fdiag-24-05)


<span id="topic-25"></span>


### F25 · 本节图解

[先别把MCP理解成“给模型装了一个新大脑”](foundations/25.md#fdiag-25-01)[一次从连接到工具结果的逻辑次序](foundations/25.md#fdiag-25-02)[Tools、Resources、Prompts各是什么](foundations/25.md#fdiag-25-03)[工具Schema不应替代业务判断](foundations/25.md#fdiag-25-04)[stdio、HTTP与JSON-RPC先只懂职责](foundations/25.md#fdiag-25-05)


<span id="topic-26"></span>


### F26 · 本节图解

[上下文不是“整台电脑都在模型脑里”](foundations/26.md#fdiag-26-01)[先算一本简化Token账](foundations/26.md#fdiag-26-02)[怎样选证据，不是越多越好](foundations/26.md#fdiag-26-03)[顺序、角色、来源是三种不同标签](foundations/26.md#fdiag-26-04)[Prompt Cache为什么需要稳定前缀](foundations/26.md#fdiag-26-05)


<span id="topic-27"></span>


### F27 · 本节图解

[先区分四种动作](foundations/27.md#fdiag-27-01)[一个不能再被缩短成“任务快完成”的状态](foundations/27.md#fdiag-27-02)[一次压缩应该怎样进行](foundations/27.md#fdiag-27-03)[原文如何重新找回](foundations/27.md#fdiag-27-04)[为什么不透明压缩块不能当普通摘要](foundations/27.md#fdiag-27-05)


<span id="topic-28"></span>


### F28 · 本节图解

[检索先解决“从哪里找到候选”](foundations/28.md#fdiag-28-01)[倒排索引为什么叫“倒排”](foundations/28.md#fdiag-28-02)[TF、IDF与BM25先认识职责](foundations/28.md#fdiag-28-03)[向量检索为什么能找同义表达](foundations/28.md#fdiag-28-04)[精确最近邻与近似最近邻](foundations/28.md#fdiag-28-05)


<span id="topic-29"></span>


### F29 · 本节图解

[召回和重排为什么分两步](foundations/29.md#fdiag-29-01)[关键词和向量怎样一起用](foundations/29.md#fdiag-29-02)[Cross-encoder为什么更细也更贵](foundations/29.md#fdiag-29-03)[相关不等于足够回答](foundations/29.md#fdiag-29-04)[查询改写和假设文档的边界](foundations/29.md#fdiag-29-05)


<span id="topic-30"></span>


### F30 · 本节图解

[先从一行代码看不同观察层](foundations/30.md#fdiag-30-01)[LSP不是自动懂业务的模型](foundations/30.md#fdiag-30-02)[图、节点和边怎样读](foundations/30.md#fdiag-30-03)[Git的几种状态为什么都重要](foundations/30.md#fdiag-30-04)[一次Bug定位的具体顺序](foundations/30.md#fdiag-30-05)


<span id="topic-31"></span>


### F31 · 本节图解

[先说什么值得跨会话保存](foundations/31.md#fdiag-31-01)[四种记忆不只是一组名称](foundations/31.md#fdiag-31-02)[一条可用记忆至少问哪些问题](foundations/31.md#fdiag-31-03)[Valid time与Recorded time为什么不同](foundations/31.md#fdiag-31-04)[更新不是只追加一条新向量](foundations/31.md#fdiag-31-05)


<span id="topic-32"></span>


### F32 · 本节图解

[五种扩展能力不要混成一个大Prompt](foundations/32.md#fdiag-32-01)[路由是在作选择](foundations/32.md#fdiag-32-02)[漏加载与过度加载为何都不好](foundations/32.md#fdiag-32-03)[子Agent不是主Agent的一份完全复制](foundations/32.md#fdiag-32-04)[用一个DAG算并行是否值得](foundations/32.md#fdiag-32-05)


<span id="topic-33"></span>


### F33 · 本节图解

[先看最危险的一条时间线](foundations/33.md#fdiag-33-01)[幂等不是“重试时最好别出错”](foundations/33.md#fdiag-33-02)[数据库事务保证到哪里](foundations/33.md#fdiag-33-03)[CAS怎样避免覆盖新版本](foundations/33.md#fdiag-33-04)[原子替换能做什么，不能做什么](foundations/33.md#fdiag-33-05)


<span id="topic-34"></span>


### F34 · 本节图解

[正确性首先相对于什么](foundations/34.md#fdiag-34-01)[一条测试包含什么](foundations/34.md#fdiag-34-02)[单元、集成和端到端测试各看哪层](foundations/34.md#fdiag-34-03)[用反例识别弱测试](foundations/34.md#fdiag-34-04)[测试通过也必须绑定版本](foundations/34.md#fdiag-34-05)


<span id="topic-35"></span>


### F35 · 本节图解

[先给评测单位起清楚名字](foundations/35.md#fdiag-35-01)[成功率先用真实次数算](foundations/35.md#fdiag-35-02)[精确率和召回率用集合手算](foundations/35.md#fdiag-35-03)[排得靠前也有区别](foundations/35.md#fdiag-35-04)[pass@1、pass@k、pass^k的区别](foundations/35.md#fdiag-35-05)


<span id="topic-36"></span>


### F36 · 本节图解

[概率与一次观察不是同一个数](foundations/36.md#fdiag-36-01)[为什么重复同一题也会不同](foundations/36.md#fdiag-36-02)[配对比较比只看两列总分更有信息](foundations/36.md#fdiag-36-03)[标准误差怎样理解](foundations/36.md#fdiag-36-04)[置信区间不是“模型有95%自信”](foundations/36.md#fdiag-36-05)


<span id="topic-37"></span>


### F37 · 本节图解

[先区分指令来源](foundations/37.md#fdiag-37-01)[可信边界具体是什么](foundations/37.md#fdiag-37-02)[沙箱不是一个神奇开关](foundations/37.md#fdiag-37-03)[最小权限与审批到底批准什么](foundations/37.md#fdiag-37-04)[记忆污染如何让风险跨会话传播](foundations/37.md#fdiag-37-05)


<span id="topic-38"></span>


### F38 · 本节图解

[一次任务到底慢在哪里](foundations/38.md#fdiag-38-01)[用一条教学轨迹分账](foundations/38.md#fdiag-38-02)[TTFT、TPOT与端到端延迟](foundations/38.md#fdiag-38-03)[吞吐与延迟不是一对同义词](foundations/38.md#fdiag-38-04)[成本应算整个任务](foundations/38.md#fdiag-38-05)


<span id="topic-39"></span>


### F39 · 本节图解

[图片在计算机里也是有形状的数据](foundations/39.md#fdiag-39-01)[图像Patch怎样变成一串向量](foundations/39.md#fdiag-39-02)[视觉表示怎样交给语言模型](foundations/39.md#fdiag-39-03)[GUI Agent为什么要反复观察](foundations/39.md#fdiag-39-04)[模型自信、概率与校准](foundations/39.md#fdiag-39-05)


<span id="topic-40"></span>


### F40 · 本节图解

[先问失败发生在哪一层](foundations/40.md#fdiag-40-01)[一个完整但不过度复杂的调查](foundations/40.md#fdiag-40-02)[Prompt、RAG、Memory、Skill和Fine-tuning怎样选](foundations/40.md#fdiag-40-03)[为什么读完基础还需要高级追问](foundations/40.md#fdiag-40-04)[面试式回答怎样不变成背口诀](foundations/40.md#fdiag-40-05)

[返回全书目录](contents.md)