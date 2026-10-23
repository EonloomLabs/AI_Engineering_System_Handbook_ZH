---
title: "术语与符号速查"
description: "AI系统工程：本地教学正文与可追溯图表"
---

阅读指南与附录


<span id="glossary-title"></span>


# 术语与符号速查

需要理解符号代表什么、从哪里来时，可阅读[公式、术语与对象来源](concepts.md)。该页区分参数、输入、中间结果、尺寸及执行状态，并提供独立微例和完整课程入口。

这里是速查，不是把基础教学缩成定义。每项都有例子和完整前置课入口；学习时优先读课文，再把此页当随手可查的索引。

[搜索一个术语或题号](search.md)


<span id="g001"></span>



<span id="section-1"></span>


### 模型 / Model

带可学习参数的计算规则，把输入表示变为输出分数或其他结果。

**具体例子：**它不能自行打开你电脑里的文件；外围程序才能执行这种动作。

[回到 F01 的完整讲解 →](foundations/01.md)


<span id="g002"></span>



<span id="section-2"></span>


### 参数 / Parameter

模型长期保存、训练时调整的数字。

**具体例子：**Embedding表和线性层权重都属于参数。

[回到 F01 的完整讲解 →](foundations/01.md)


<span id="g003"></span>



<span id="section-3"></span>


### 训练 / Training

依据样例与目标计算误差，再调整参数的过程。

**具体例子：**本书标量训练把w=1更新为1.8。

[回到 F01 的完整讲解 →](foundations/01.md)


<span id="g004"></span>



<span id="section-4"></span>


### 推理 / Inference

使用已有参数处理输入并产生输出的过程。

**具体例子：**通常不会因为一次聊天就永久修改模型权重。

[回到 F01 的完整讲解 →](foundations/01.md)


<span id="g005"></span>



<span id="section-5"></span>


### 函数 / Function

按规则将输入映射到输出的操作。

**具体例子：**f(x)=2x表示输入3输出6。

[回到 F01 的完整讲解 →](foundations/01.md)


<span id="g006"></span>



<span id="section-6"></span>


### 标量 / Scalar

单个数值。

**具体例子：**7，或者某一个损失值。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g007"></span>



<span id="section-7"></span>


### 向量 / Vector

有固定顺序的一排数。

**具体例子：**[0.2,-0.1,0.7,0.4]有4个分量。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g008"></span>



<span id="section-8"></span>


### 矩阵 / Matrix

有行有列的规则数字表。

**具体例子：**两行三列的表，形状[2,3]。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g009"></span>



<span id="section-9"></span>


### 张量 / Tensor

机器学习程序中用于存放规则排列数值的数据对象。

**具体例子：**[2,3,4]可读成两张三行四列表。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g010"></span>



<span id="section-10"></span>


### 形状 / Shape

各个轴分别有多长，不是数据内容。

**具体例子：**内容[[1,2],[3,4]]的形状是[2,2]。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g011"></span>



<span id="section-11"></span>


### 轴 / Axis

张量中某一个索引方向。

**具体例子：**[B,T,d]的三个轴是样本、位置、特征。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g012"></span>



<span id="section-12"></span>


### 秩 / Rank（轴数）

张量语境常指轴的数量，与矩阵线性代数中的秩不是一回事。

**具体例子：**[2,128,4096]有3个轴；矩阵秩见F20。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g013"></span>



<span id="section-13"></span>


### 索引 / Index

用位置找到数据的方式；本书代码从0计数。

**具体例子：**H[1,0]取第二条输入的第一个位置。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g014"></span>



<span id="section-14"></span>


### 切片 / Slice

按范围或保留某轴的一组位置取出数据。

**具体例子：**H[1,:,2]取第二条输入各位置的第三个分量。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g015"></span>



<span id="section-15"></span>


### B

批大小，一起组织计算的输入条数。

**具体例子：**B=2表示两条输入，不表示两层网络。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g016"></span>



<span id="section-16"></span>


### T

本轮安排的序列位置数；具体公式需核对是否包含缓存。

**具体例子：**补齐后T=128不证明真实输入都有128个Token。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g017"></span>



<span id="section-17"></span>


### d / d\_model

每个位置内部表示的宽度。

**具体例子：**d=4096即一排4096个数。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g018"></span>



<span id="section-18"></span>


### N / V（词表）

词表项数；部分论文写V，注意与Attention的Value区别。

**具体例子：**N=6、d=4的Embedding参数表是[6,4]。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g019"></span>



<span id="section-19"></span>


### L（层数）

串行堆叠的模型层数量。

**具体例子：**缓存公式乘L是因为各层都有自己的K和V。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g020"></span>



<span id="section-20"></span>


### 下标 x\_i

向量x的第i个数，或按定义编号的对象。

**具体例子：**x=[7,2,9]时，0起算的x\_1是2。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g021"></span>



<span id="section-21"></span>


### Σ / 求和

把给定范围内的项逐个相加。

**具体例子：**Σ\_i x\_i可展开为x\_0+x\_1+…。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g022"></span>



<span id="section-22"></span>


### ∈ / R

∈读属于；R表示实数集合。

**具体例子：**X∈R^(2×3)表示X是两行三列的实数表。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g023"></span>



<span id="section-23"></span>


### ≈ / 近似

两边因舍入或近似而接近，并非逐位相等。

**具体例子：**1/3≈0.3333。

[回到 F02 的完整讲解 →](foundations/02.md)


<span id="g024"></span>



<span id="section-24"></span>


### 字符 / Character

文本中的书写单位或编码字符，不能直接等同Token。

**具体例子：**“爱”的UTF-8编码占多个字节。

[回到 F03 的完整讲解 →](foundations/03.md)


<span id="g025"></span>



<span id="section-25"></span>


### 字节 / Byte

8个二进制位构成的存储单位。

**具体例子：**一个float32通常占4字节。

[回到 F03 的完整讲解 →](foundations/03.md)


<span id="g026"></span>



<span id="section-26"></span>


### UTF-8

把Unicode字符编码为变长字节序列的一种规则。

**具体例子：**网络分片可能切在一个汉字的字节中间。

[回到 F03 的完整讲解 →](foundations/03.md)


<span id="g027"></span>



<span id="section-27"></span>


### Token

模型分词器使用的片段单位。

**具体例子：**可能是词、词的一部分、标点或部分字节。

[回到 F03 的完整讲解 →](foundations/03.md)


<span id="g028"></span>



<span id="section-28"></span>


### Token ID / input\_ids

某Token在对应词表中的整数地址。

**具体例子：**[1,2,3]先是编号列表，不是三个语义强度。

[回到 F03 的完整讲解 →](foundations/03.md)


<span id="g029"></span>



<span id="section-29"></span>


### Tokenizer

按模型配套规则把文本与Token编号相互转换的工具。

**具体例子：**不能随意换分词器而保留不相容的模型参数。

[回到 F03 的完整讲解 →](foundations/03.md)


<span id="g030"></span>



<span id="section-30"></span>


### BPE

通过逐步合并相邻符号来构建子词词表的一类方法。

**具体例子：**训练合并规则在前，使用规则编码新输入在后。

[回到 F03 的完整讲解 →](foundations/03.md)


<span id="g031"></span>



<span id="section-31"></span>


### WordPiece

另一类子词建模方法，常采用词表上的最长匹配编码。

**具体例子：**训练目标和BPE合并过程不同，不能只记成同一种算法。

[回到 F03 的完整讲解 →](foundations/03.md)


<span id="g032"></span>



<span id="section-32"></span>


### Unigram

为候选子词赋概率并选择切分的一类子词模型。

**具体例子：**不等于每次都取词表最长字符串。

[回到 F03 的完整讲解 →](foundations/03.md)


<span id="g033"></span>



<span id="section-33"></span>


### 聊天模板 / Chat template

把带角色消息组织成模型约定的输入形式。

**具体例子：**角色与结束标记可能使用专门Token。

[回到 F03 的完整讲解 →](foundations/03.md)


<span id="g034"></span>



<span id="section-34"></span>


### Batch / 批次

一起组织计算的一组输入。

**具体例子：**普通样本batch不让不同用户相互读取内容。

[回到 F04 的完整讲解 →](foundations/04.md)


<span id="g035"></span>



<span id="section-35"></span>


### Padding / 补齐

给短序列增加占位项，使指定组织方式可用。

**具体例子：**[4,2]右补齐为[4,2,0]。

[回到 F04 的完整讲解 →](foundations/04.md)


<span id="g036"></span>



<span id="section-36"></span>


### PAD

模型配置中的补齐用特殊项。

**具体例子：**本书PAD编号为0，现实编号未必为0。

[回到 F04 的完整讲解 →](foundations/04.md)


<span id="g037"></span>



<span id="section-37"></span>


### Truncation / 截断

删去超长输入的一部分，而不是增加占位。

**具体例子：**可能删掉关键约束，不能与摘要压缩混用。

[回到 F04 的完整讲解 →](foundations/04.md)


<span id="g038"></span>



<span id="section-38"></span>


### Embedding / 嵌入表

按输入编号取出对应可学习向量的参数表及操作。

**具体例子：**E形状[6,4]，编号2取E的第2行。

[回到 F05 的完整讲解 →](foundations/05.md)


<span id="g-one-hot"></span>



<span id="topic-1"></span>


### One-hot / 独热编码

用与词表大小相同的0/1数组指向某个编号：只有被选中的位置为1，其他均为0。这不同于整数的二进制存储，也不同于Embedding表中可训练的浮点向量。

**具体例子：**6项词表的编号2写成`[0,0,1,0,0,0]`；若E形状[6,4]，用这个One-hot乘E在数学上等于取出E[2]，但运行时通常直接查表。

[进入完整原理与查表例子 →](foundations/05.md#representation-comparison)


<span id="g039"></span>



<span id="section-39"></span>


### Lookup / 查表

根据地址读取完整条目，不用地址大小进行语义运算。

**具体例子：**编号4对应[0.1,-0.5,0.9,0.3]，不是将4乘某个向量。

[回到 F05 的完整讲解 →](foundations/05.md)


<span id="g040"></span>



<span id="section-40"></span>


### 分布式表示

一个含义由多个数及其组合共同表达，而非每列固定对应一个词义标签。

**具体例子：**不能断言第12维永远表示快乐。

[回到 F05 的完整讲解 →](foundations/05.md)


<span id="g041"></span>



<span id="section-41"></span>


### dtype / 数据类型

规定每个元素如何存储与运算。

**具体例子：**整数编号与浮点表示通常不是同一dtype。

[回到 F06 的完整讲解 →](foundations/06.md)


<span id="g042"></span>



<span id="section-42"></span>


### 浮点数 / Floating point

用有限位数近似表示实数的计算机格式。

**具体例子：**0.1不一定能被二进制浮点精确保存。

[回到 F06 的完整讲解 →](foundations/06.md)


<span id="g043"></span>



<span id="section-43"></span>


### FP32 / FP16 / BF16

不同的32位或16位浮点格式，范围与精度不一样。

**具体例子：**FP16和BF16都通常占2字节，但不能视为同一数值格式。

[回到 F06 的完整讲解 →](foundations/06.md)


<span id="g044"></span>



<span id="section-44"></span>


### CPU

通用处理器，适合多种控制和数值任务。

**具体例子：**本包基础实验使用CPU与Python标准库。

[回到 F06 的完整讲解 →](foundations/06.md)


<span id="g045"></span>



<span id="section-45"></span>


### GPU

适合大规模并行数值运算的处理器。

**具体例子：**数据搬到GPU不改变编号语义，但消耗时间和显存。

[回到 F06 的完整讲解 →](foundations/06.md)


<span id="g046"></span>



<span id="section-46"></span>


### Device / 设备

数据或运算所在的处理器环境。

**具体例子：**模型权重与输入必须满足相容的设备约束。

[回到 F06 的完整讲解 →](foundations/06.md)


<span id="g047"></span>



<span id="section-47"></span>


### 显存 / VRAM

GPU用于存放参数、输入和中间结果的存储空间。

**具体例子：**只算Embedding输出大小不等于模型总显存。

[回到 F06 的完整讲解 →](foundations/06.md)


<span id="g048"></span>



<span id="section-48"></span>


### MiB / GiB

二进制存储单位，分别为2^20和2^30字节。

**具体例子：**1,048,576个2字节数占2MiB。

[回到 F06 的完整讲解 →](foundations/06.md)


<span id="g049"></span>



<span id="section-49"></span>


### 权重 / Weight

决定输入数值如何组合的可学习系数。

**具体例子：**[1,2,3]乘系数[2,0,1]后求和得5。

[回到 F07 的完整讲解 →](foundations/07.md)


<span id="g050"></span>



<span id="section-50"></span>


### 点积 / Dot product

两个等长向量逐项相乘再求和。

**具体例子：**[1,2]·[3,4]=11。

[回到 F07 的完整讲解 →](foundations/07.md)


<span id="g051"></span>



<span id="section-51"></span>


### 矩阵乘法 / Matmul

把左表每一行与右表每一列做点积。

**具体例子：**[2,3]乘[3,4]得到[2,4]。

[回到 F07 的完整讲解 →](foundations/07.md)


<span id="g052"></span>



<span id="section-52"></span>


### 转置 / Transpose / ᵀ

交换矩阵的行列方向。

**具体例子：**[[1,2,3],[4,5,6]]转置为[[1,4],[2,5],[3,6]]。

[回到 F07 的完整讲解 →](foundations/07.md)


<span id="g053"></span>



<span id="section-53"></span>


### 范数 / Norm

衡量向量大小的一类函数，L2范数为平方和开根号。

**具体例子：**[3,4]的L2范数为5。

[回到 F07 的完整讲解 →](foundations/07.md)


<span id="g054"></span>



<span id="section-54"></span>


### 余弦相似度 / Cosine

点积除以两个向量的L2范数，比较方向。

**具体例子：**主题方向接近不保证事实或权限一致。

[回到 F07 的完整讲解 →](foundations/07.md)


<span id="g055"></span>



<span id="section-55"></span>


### reshape

在元素总数相同的条件下改变数据视图或组织形状。

**具体例子：**6个数可以摆成[2,3]或[3,2]，但转置另有排列规则。

[回到 F08 的完整讲解 →](foundations/08.md)


<span id="g056"></span>



<span id="section-56"></span>


### permute / 转轴

重排多个轴的次序。

**具体例子：**[B,T,h,d\_h]变为[B,h,T,d\_h]。

[回到 F08 的完整讲解 →](foundations/08.md)


<span id="g057"></span>



<span id="section-57"></span>


### Broadcast / 广播

把兼容的单例维按规则扩展用于组合运算。

**具体例子：**每列偏置可应用到表中每一行，不是真的先学出很多份偏置。

[回到 F08 的完整讲解 →](foundations/08.md)


<span id="g058"></span>



<span id="section-58"></span>


### Stride / 步幅

沿某轴移动一个索引时底层存储要跨过的元素间距。

**具体例子：**转置后的视图可能不连续，后续reshape可能需复制。

[回到 F08 的完整讲解 →](foundations/08.md)


<span id="g059"></span>



<span id="section-59"></span>


### 概率 / Probability

在给定条件和模型下事件所占的可能性份额。

**具体例子：**候选Token概率不是最终答案正确率。

[回到 F09 的完整讲解 →](foundations/09.md)


<span id="g060"></span>



<span id="section-60"></span>


### exp / e^x

指数函数，将数值转换为正数；e约2.71828。

**具体例子：**exp(0)=1，exp(ln2)=2。

[回到 F09 的完整讲解 →](foundations/09.md)


<span id="g061"></span>



<span id="section-61"></span>


### ln / log

指数的反向函数；本书未注明底时通常指自然对数。

**具体例子：**ln(1)=0，ln(2)约0.6931。

[回到 F09 的完整讲解 →](foundations/09.md)


<span id="g062"></span>



<span id="section-62"></span>


### softmax

将各分数取指数，再除以所有指数之和。

**具体例子：**[2,1,0]经Softmax后约为[0.6652,0.2447,0.0900]。

[回到 F09 的完整讲解 →](foundations/09.md)


<span id="g063"></span>



<span id="section-63"></span>


### 归一化 / Normalization

按选定规则调整尺度；不同语境目标不同。

**具体例子：**softmax使和为1，LayerNorm按均值与方差变换，不是一回事。

[回到 F09 的完整讲解 →](foundations/09.md)


<span id="g064"></span>



<span id="section-64"></span>


### 线性层 / Linear layer

常写作XW+b，对输入做加权组合并加偏置。

**具体例子：**输出宽度由W的列数决定。

[回到 F10 的完整讲解 →](foundations/10.md)


<span id="g065"></span>



<span id="section-65"></span>


### 偏置 / Bias（参数）

线性层加上的可学习常数项。

**具体例子：**不同于评测里的统计偏差。

[回到 F10 的完整讲解 →](foundations/10.md)


<span id="g066"></span>



<span id="section-66"></span>


### 激活 / Activation

可指层的中间输出，也可指激活函数，需看语境。

**具体例子：**ReLU把负数变0；激活显存存的是本次中间结果。

[回到 F10 的完整讲解 →](foundations/10.md)


<span id="g067"></span>



<span id="section-67"></span>


### 非线性 / Nonlinearity

不能仅用一次线性变换等价表示的运算。

**具体例子：**ReLU使网络可以表达更复杂的分段行为。

[回到 F10 的完整讲解 →](foundations/10.md)


<span id="g068"></span>



<span id="section-68"></span>


### ReLU / GELU / SiLU

不同的非线性激活函数。

**具体例子：**ReLU(x)=max(0,x)，另外两者有平滑曲线。

[回到 F10 的完整讲解 →](foundations/10.md)


<span id="g069"></span>



<span id="section-69"></span>


### 隐藏状态 / Hidden state

网络内部某层某位置的一排表示数字。

**具体例子：**相同Token在不同上下文的后层表示可能不同。

[回到 F10 的完整讲解 →](foundations/10.md)


<span id="g070"></span>



<span id="section-70"></span>


### 前向 / Forward

按网络定义从输入计算输出。

**具体例子：**训练与推理都会做前向，训练还做反向更新。

[回到 F10 的完整讲解 →](foundations/10.md)


<span id="g071"></span>



<span id="section-71"></span>


### Attention / 注意力

计算查询与可读候选的匹配份额，再加权组合内容。

**具体例子：**先计算分数和权重，再用权重混合V。

[回到 F11 的完整讲解 →](foundations/11.md)


<span id="g072"></span>



<span id="section-72"></span>


### Q / Query

当前位置用于与候选比较的一组数。

**具体例子：**q=[1,0]不是用户原话，而是投影后的表示。

[回到 F11 的完整讲解 →](foundations/11.md)


<span id="g073"></span>



<span id="section-73"></span>


### K / Key

每个可读位置用于被查询比较的一组数。

**具体例子：**与Q点积得到匹配分数。

[回到 F11 的完整讲解 →](foundations/11.md)


<span id="g074"></span>



<span id="section-74"></span>


### V / Value

每个可读位置将被加权汇集的内容表示。

**具体例子：**这里V不是词表大小。

[回到 F11 的完整讲解 →](foundations/11.md)


<span id="g075"></span>



<span id="section-75"></span>


### d\_k / d\_h

Key宽度或每个头的宽度，具体以公式定义为准。

**具体例子：**常见点积缩放除以sqrt(d\_k)。

[回到 F11 的完整讲解 →](foundations/11.md)


<span id="g076"></span>



<span id="section-76"></span>


### Self-attention / 自注意力

查询与可读信息来自同一序列的表示。

**具体例子：**生成模型通常再施加因果限制。

[回到 F11 的完整讲解 →](foundations/11.md)


<span id="g077"></span>



<span id="section-77"></span>


### Attention mask

规定哪些位置间的读取被允许的约束。

**具体例子：**接口可能用布尔值或加性负无穷，真假约定要核对。

[回到 F12 的完整讲解 →](foundations/12.md)


<span id="g078"></span>



<span id="section-78"></span>


### Causal mask / 因果掩码

让当前位置不能读取尚未来到的位置。

**具体例子：**位置1能读0和1，但不能读2。

[回到 F12 的完整讲解 →](foundations/12.md)


<span id="g079"></span>



<span id="section-79"></span>


### Padding mask

排除补齐项作为有效内容的标记。

**具体例子：**PAD向量全0仍不保证其softmax权重自动为0。

[回到 F12 的完整讲解 →](foundations/12.md)


<span id="g080"></span>



<span id="section-80"></span>


### Loss mask

规定哪些位置的预测误差计入训练目标。

**具体例子：**用户文本可被读取，但可不直接计算该段输出损失。

[回到 F12 的完整讲解 →](foundations/12.md)


<span id="g081"></span>



<span id="section-81"></span>


### Position IDs

表示真实逻辑位置的编号，不是Token身份编号。

**具体例子：**同一个“爱”出现在位置1或7，Token ID可相同但位置不同。

[回到 F13 的完整讲解 →](foundations/13.md)


<span id="g082"></span>



<span id="section-82"></span>


### RoPE

通过按位置旋转成对坐标来引入位置信息的方法。

**具体例子：**二维90度旋转把[2,3]变为[-3,2]。

[回到 F13 的完整讲解 →](foundations/13.md)


<span id="g083"></span>



<span id="section-83"></span>


### sin / cos

描述二维单位圆上角度对应的纵横坐标的函数。

**具体例子：**旋转矩阵用它们保持长度并改变方向。

[回到 F13 的完整讲解 →](foundations/13.md)


<span id="g084"></span>



<span id="section-84"></span>


### Residual / 残差连接

把某段变换的输入加回输出。

**具体例子：**y=x+f(x)，要求可相加的形状。

[回到 F14 的完整讲解 →](foundations/14.md)


<span id="g085"></span>



<span id="section-85"></span>


### LayerNorm

通常对每位置的特征计算均值方差并标准化，再用可学习尺度偏移。

**具体例子：**[1,3]忽略epsilon时标准化为[-1,1]。

[回到 F14 的完整讲解 →](foundations/14.md)


<span id="g086"></span>



<span id="section-86"></span>


### RMSNorm

按均方根尺度归一化，通常不减均值。

**具体例子：**[1,3]除以sqrt(5)。

[回到 F14 的完整讲解 →](foundations/14.md)


<span id="g087"></span>



<span id="section-87"></span>


### ε / epsilon

通常是避免除零等数值问题的小正数，具体公式另有定义。

**具体例子：**放在方差加项中时会影响精确数值。

[回到 F14 的完整讲解 →](foundations/14.md)


<span id="g088"></span>



<span id="section-88"></span>


### FFN / MLP

通常在每个位置应用的前馈子网络。

**具体例子：**常把宽度先扩展再缩回，带非线性或门控。

[回到 F14 的完整讲解 →](foundations/14.md)


<span id="g089"></span>



<span id="section-89"></span>


### SwiGLU / 门控

以一个分支产生的值调节另一个分支输出的前馈结构。

**具体例子：**不是“挑一个词通过”，而是逐数值调制。

[回到 F14 的完整讲解 →](foundations/14.md)


<span id="g090"></span>



<span id="section-90"></span>


### Pre-norm / Post-norm

归一化放在子层变换之前或残差之后的结构安排。

**具体例子：**不同结构的梯度与数值行为不能只看模块名称判断。

[回到 F14 的完整讲解 →](foundations/14.md)


<span id="g091"></span>



<span id="section-91"></span>


### Logits

输出投影给各词表候选的未归一化分数。

**具体例子：**可以是负数，还不是概率或Token编号。

[回到 F18 的完整讲解 →](foundations/18.md)


<span id="g092"></span>



<span id="section-92"></span>


### Argmax / 贪心选择

选择分数或概率最大的候选下标。

**具体例子：**不涉及按概率随机抽样。

[回到 F18 的完整讲解 →](foundations/18.md)


<span id="g093"></span>



<span id="section-93"></span>


### Sampling / 采样

依据概率分布抽取候选。

**具体例子：**相同输入可以得到不同输出，不代表参数变了。

[回到 F18 的完整讲解 →](foundations/18.md)


<span id="g094"></span>



<span id="section-94"></span>


### Temperature / 温度

在softmax前调整分数尺度的参数。

**具体例子：**正温度越低分布一般越集中，0需按接口特殊语义处理。

[回到 F18 的完整讲解 →](foundations/18.md)


<span id="g095"></span>



<span id="section-95"></span>


### Top-k / Top-p

分别按候选个数或累计概率保留候选的策略。

**具体例子：**筛选后通常还要重新归一化。

[回到 F18 的完整讲解 →](foundations/18.md)


<span id="g096"></span>



<span id="section-96"></span>


### EOS

模型约定的一种结束序列Token。

**具体例子：**与最大输出长度、用户取消是不同结束原因。

[回到 F18 的完整讲解 →](foundations/18.md)


<span id="g097"></span>



<span id="section-97"></span>


### 自回归 / Autoregressive

根据已有序列逐步预测后续项。

**具体例子：**预测出新Token后，再把它作为后续步骤的条件。

[回到 F18 的完整讲解 →](foundations/18.md)


<span id="g098"></span>



<span id="section-98"></span>


### Prefill

处理当前已经知道的一段输入前缀。

**具体例子：**得到各层表示及可复用的K/V。

[回到 F19 的完整讲解 →](foundations/19.md)


<span id="g099"></span>



<span id="section-99"></span>


### Decode（推理阶段）

继续逐步生成新Token的阶段。

**具体例子：**别与Tokenizer把编号解为文字的decode混淆。

[回到 F19 的完整讲解 →](foundations/19.md)


<span id="g100"></span>



<span id="section-100"></span>


### KV Cache

保存每层已有位置的Key和Value计算结果以复用。

**具体例子：**不是用户长期记忆，也不是Prompt摘要。

[回到 F19 的完整讲解 →](foundations/19.md)


<span id="g101"></span>



<span id="section-101"></span>


### Cache position

用于跟踪缓存中逻辑位置的参数或约定。

**具体例子：**有历史前缀后，新查询不能重新从绝对位置0开始。

[回到 F19 的完整讲解 →](foundations/19.md)


<span id="g102"></span>



<span id="section-102"></span>


### 导数 / Derivative

输入微小变化引起输出变化的局部比率。

**具体例子：**x²在x=3处导数是6。

[回到 F15 的完整讲解 →](foundations/15.md)


<span id="g103"></span>



<span id="section-103"></span>


### 梯度 / Gradient

损失对各个参数的偏导数组成的集合。

**具体例子：**不是模型“思考过程”，是可计算的变化率。

[回到 F15 的完整讲解 →](foundations/15.md)


<span id="g104"></span>



<span id="section-104"></span>


### ∂ / 偏导数

只改变某个变量、其余变量按定义固定时的变化率符号。

**具体例子：**∂L/∂w说明权重w对损失L的局部影响。

[回到 F15 的完整讲解 →](foundations/15.md)


<span id="g105"></span>



<span id="section-105"></span>


### 链式法则 / Chain rule

把复合计算各阶段的变化率相乘并按路径相加。

**具体例子：**输出经中间量依赖w时，沿计算链回传影响。

[回到 F15 的完整讲解 →](foundations/15.md)


<span id="g106"></span>



<span id="section-106"></span>


### 反向传播 / Backprop

利用链式法则高效计算各参数梯度的算法。

**具体例子：**沿已有前向计算图反向计算，不是反着生成文字。

[回到 F15 的完整讲解 →](foundations/15.md)


<span id="g107"></span>



<span id="section-107"></span>


### 有限差分

通过输入小幅加减后的输出差近似导数。

**具体例子：**可用于核对解析梯度，但不是大型模型训练常规替代法。

[回到 F15 的完整讲解 →](foundations/15.md)


<span id="g108"></span>



<span id="section-108"></span>


### 标签 / Label

训练中希望模型预测的目标。

**具体例子：**自回归当前位置的标签通常是下一个Token。

[回到 F16 的完整讲解 →](foundations/16.md)


<span id="g109"></span>



<span id="section-109"></span>


### 交叉熵 / Cross entropy

对目标概率取负对数后求平均等的训练目标。

**具体例子：**目标概率0.8时单项损失−ln0.8约0.2231。

[回到 F16 的完整讲解 →](foundations/16.md)


<span id="g110"></span>



<span id="section-110"></span>


### Learning rate / 学习率η

决定沿梯度更新多大步的系数。

**具体例子：**w\_new=w−η×gradient。

[回到 F16 的完整讲解 →](foundations/16.md)


<span id="g111"></span>



<span id="section-111"></span>


### Adam / AdamW

利用梯度一阶与二阶统计的优化器；AdamW独立处理权重衰减。

**具体例子：**恢复训练时应考虑其状态，不只有模型权重。

[回到 F16 的完整讲解 →](foundations/16.md)


<span id="g112"></span>



<span id="section-112"></span>


### Checkpoint（训练）

保存恢复训练所需状态的持久产物。

**具体例子：**可能含权重、优化器、步数与随机状态。

[回到 F16 的完整讲解 →](foundations/16.md)


<span id="g113"></span>



<span id="section-113"></span>


### 过拟合 / Overfitting

过分适应训练数据而不能很好处理新样本。

**具体例子：**背熟教学循环序列不代表会自然语言推理。

[回到 F16 的完整讲解 →](foundations/16.md)


<span id="g114"></span>



<span id="section-114"></span>


### SFT

用指定目标回答做监督微调。

**具体例子：**属于参数训练，和会话中加载Skill不同。

[回到 F17 的完整讲解 →](foundations/17.md)


<span id="g115"></span>



<span id="section-115"></span>


### RLHF / RLAIF

利用人类或AI反馈进行强化学习式后训练的方法族。

**具体例子：**反馈来源和目标都需核对，不能仅看缩写。

[回到 F17 的完整讲解 →](foundations/17.md)


<span id="g116"></span>



<span id="section-116"></span>


### 策略 / Policy

给定状态时对动作或Token的概率分布。

**具体例子：**π(y|x)表示在输入x条件下产生输出y的概率。

[回到 F17 的完整讲解 →](foundations/17.md)


<span id="g117"></span>



<span id="section-117"></span>


### 奖励 / Reward

用于评价动作或结果并驱动优化的信号。

**具体例子：**高奖励不自动证明符合真实业务目标。

[回到 F17 的完整讲解 →](foundations/17.md)


<span id="g118"></span>



<span id="section-118"></span>


### DPO

以偏好对比较策略相对参考模型概率的训练方法。

**具体例子：**要算完整回答条件概率，不只看最后一个Token。

[回到 F17 的完整讲解 →](foundations/17.md)


<span id="g119"></span>



<span id="section-119"></span>


### KL散度

衡量一个概率分布相对另一个分布的偏离量，通常有方向性。

**具体例子：**KL(p||q)不必等于KL(q||p)。

[回到 F17 的完整讲解 →](foundations/17.md)


<span id="g120"></span>



<span id="section-120"></span>


### PPO / GRPO

不同策略优化方法，使用概率比及估计信号等控制更新。

**具体例子：**先懂策略、奖励、基线和相对变化，再读具体公式。

[回到 F17 的完整讲解 →](foundations/17.md)


<span id="g121"></span>



<span id="section-121"></span>


### 矩阵秩 / Low rank

矩阵中独立方向的数量；低秩可用较小矩阵乘积近似某变换。

**具体例子：**不是张量轴数，rank2更新仍可用于二维权重矩阵。

[回到 F20 的完整讲解 →](foundations/20.md)


<span id="g122"></span>



<span id="section-122"></span>


### LoRA

用低秩参数增量适配原权重的微调方法。

**具体例子：**ΔW=AB，训练A和B而非全部基础权重。

[回到 F20 的完整讲解 →](foundations/20.md)


<span id="g123"></span>



<span id="section-123"></span>


### QLoRA

在量化基础模型上训练低秩适配参数的一类方法。

**具体例子：**不意味着所有计算都在4位整数中完成。

[回到 F20 的完整讲解 →](foundations/20.md)


<span id="g124"></span>



<span id="section-124"></span>


### Quantization / 量化

把数值映射到较少位数的离散表示。

**具体例子：**通常需要尺度等元数据，并引入近似误差。

[回到 F20 的完整讲解 →](foundations/20.md)


<span id="g125"></span>



<span id="section-125"></span>


### Distillation / 蒸馏

利用教师模型输出或中间信号训练学生模型。

**具体例子：**不是把大模型参数简单切走一半。

[回到 F20 的完整讲解 →](foundations/20.md)


<span id="g126"></span>



<span id="section-126"></span>


### MoE / 专家混合

根据输入选择部分专家子网络参与计算的架构。

**具体例子：**总参数与本次激活参数分开统计。

[回到 F20 的完整讲解 →](foundations/20.md)


<span id="g127"></span>



<span id="section-127"></span>


### GQA / MQA / MHA

不同查询头与K/V头共享方式的注意力结构。

**具体例子：**共享更多K/V可减少缓存，但不保证质量完全相同。

[回到 F20 的完整讲解 →](foundations/20.md)


<span id="g128"></span>



<span id="section-128"></span>


### 复杂度 / O记号

描述规模增长时主要计算或存储如何增长，省略常数细节。

**具体例子：**O(T²)不意味着某次实测恰好用T²毫秒。

[回到 F21 的完整讲解 →](foundations/21.md)


<span id="g129"></span>



<span id="section-129"></span>


### FLOPs

浮点运算次数的一种计数指标。

**具体例子：**计算少可能仍因内存搬运而慢。

[回到 F21 的完整讲解 →](foundations/21.md)


<span id="g130"></span>



<span id="section-130"></span>


### Bandwidth / 带宽

单位时间可搬运的数据量。

**具体例子：**显存带宽与网络带宽是不同瓶颈。

[回到 F21 的完整讲解 →](foundations/21.md)


<span id="g131"></span>



<span id="section-131"></span>


### FlashAttention

通过分块和更有效内存访问计算注意力的一类实现。

**具体例子：**不是稀疏注意力，也不是把旧历史摘要掉。

[回到 F21 的完整讲解 →](foundations/21.md)


<span id="g132"></span>



<span id="section-132"></span>


### PagedAttention

按块管理注意力缓存的一类机制。

**具体例子：**逻辑连续不要求物理内存一大块连续。

[回到 F21 的完整讲解 →](foundations/21.md)


<span id="g133"></span>



<span id="section-133"></span>


### TP / PP / DP

张量并行、流水线并行和数据并行的不同拆分方式。

**具体例子：**拆运算、拆层、拆样本的通信要求不同。

[回到 F21 的完整讲解 →](foundations/21.md)


<span id="g134"></span>



<span id="section-134"></span>


### ZeRO / 分片

通过分散保存训练状态减少跨设备重复的一类方法。

**具体例子：**不等于把模型训练目标改变。

[回到 F21 的完整讲解 →](foundations/21.md)


<span id="g135"></span>



<span id="section-135"></span>


### Speculative decoding

草稿提候选，目标模型验证并修正的生成加速方法。

**具体例子：**保持目标分布需要正确的接受与拒绝采样。

[回到 F21 的完整讲解 →](foundations/21.md)


<span id="g136"></span>



<span id="section-136"></span>


### Agent

根据任务与观察调用模型和工具、持续推进的执行系统。

**具体例子：**不只是一次写得很长的Prompt。

[回到 F22 的完整讲解 →](foundations/22.md)


<span id="g137"></span>



<span id="section-137"></span>


### Harness / 宿主执行框架

组织模型输入、工具、状态、权限和反馈的外围程序。

**具体例子：**模型提出读文件，Harness执行并回填结果。

[回到 F22 的完整讲解 →](foundations/22.md)


<span id="g138"></span>



<span id="section-138"></span>


### Workflow / 工作流

由程序预先安排主要步骤和分支的流程。

**具体例子：**不等于每一步都必须由模型临时决策。

[回到 F22 的完整讲解 →](foundations/22.md)


<span id="g139"></span>



<span id="section-139"></span>


### API

程序之间约定输入、输出与行为的接口。

**具体例子：**不是人类界面的按钮本身。

[回到 F23 的完整讲解 →](foundations/23.md)


<span id="g140"></span>



<span id="section-140"></span>


### JSON

表达对象、数组、字符串、数值等结构化数据的文本格式。

**具体例子：**合法JSON不保证字段内容在业务上合法。

[回到 F23 的完整讲解 →](foundations/23.md)


<span id="g141"></span>



<span id="section-141"></span>


### Schema

对数据字段及类型等结构的约束描述。

**具体例子：**path是字符串，不表示可以读取任意路径。

[回到 F23 的完整讲解 →](foundations/23.md)


<span id="g142"></span>



<span id="section-142"></span>


### HTTP

常用于客户端与服务器请求响应的网络协议。

**具体例子：**收到HTTP响应不单独证明业务动作成功。

[回到 F23 的完整讲解 →](foundations/23.md)


<span id="g143"></span>



<span id="section-143"></span>


### SSE

通过事件流逐段发送服务器消息的协议形式。

**具体例子：**传输分片边界不保证等于一个完整事件。

[回到 F23 的完整讲解 →](foundations/23.md)


<span id="g144"></span>



<span id="section-144"></span>


### Tool call / 工具调用

模型提出的工具名称和参数等结构化请求。

**具体例子：**提出调用不是工具已经执行。

[回到 F23 的完整讲解 →](foundations/23.md)


<span id="g145"></span>



<span id="section-145"></span>


### Call ID

用来匹配一次工具调用与结果的标识。

**具体例子：**并行调用不能仅按结果到达顺序配对。

[回到 F23 的完整讲解 →](foundations/23.md)


<span id="g146"></span>



<span id="section-146"></span>


### State / 状态

系统当前有效事实或进展的记录。

**具体例子：**已提交、执行中、成功、失败、结果未知。

[回到 F24 的完整讲解 →](foundations/24.md)


<span id="g147"></span>



<span id="section-147"></span>


### Event / 事件

记录某件事发生的不可混淆描述。

**具体例子：**“写入开始”和“写入确认”不是同一事件。

[回到 F24 的完整讲解 →](foundations/24.md)


<span id="g148"></span>



<span id="section-148"></span>


### Checkpoint（任务）

为了中断后继续而保存的任务状态。

**具体例子：**不等于训练checkpoint，也不等于长期经验。

[回到 F24 的完整讲解 →](foundations/24.md)


<span id="g149"></span>



<span id="section-149"></span>


### Unknown / 未知结果

无法确认外部动作是否已经完成的状态。

**具体例子：**超时可能发生在成功执行之后。

[回到 F24 的完整讲解 →](foundations/24.md)


<span id="g150"></span>



<span id="section-150"></span>


### MCP

宿主与外部工具或资源服务器交互的一套协议。

**具体例子：**不是Agent间全部通信的总称。

[回到 F25 的完整讲解 →](foundations/25.md)


<span id="g151"></span>



<span id="section-151"></span>


### Host / Client / Server

MCP中的应用宿主、协议客户端与提供能力的服务器角色。

**具体例子：**一个宿主可通过多个客户端连接不同服务器。

[回到 F25 的完整讲解 →](foundations/25.md)


<span id="g152"></span>



<span id="section-152"></span>


### OAuth / Scope

授权协议与获准操作的范围。

**具体例子：**获准读日历，不等于获准删除事件。

[回到 F25 的完整讲解 →](foundations/25.md)


<span id="g153"></span>



<span id="section-153"></span>


### Context / 上下文

本轮模型调用可利用的输入信息集合。

**具体例子：**通常不包含整个硬盘的所有内容。

[回到 F26 的完整讲解 →](foundations/26.md)


<span id="g154"></span>



<span id="section-154"></span>


### Prompt caching

复用相同输入前缀的计算。

**具体例子：**不缩短逻辑输入长度，也不等于记忆写入。

[回到 F26 的完整讲解 →](foundations/26.md)


<span id="g155"></span>



<span id="section-155"></span>


### JIT / 按需加载

到了相关任务才读取完整资源。

**具体例子：**先展示Skill名称描述，相关时再读正文。

[回到 F26 的完整讲解 →](foundations/26.md)


<span id="g156"></span>



<span id="section-156"></span>


### Compaction / 压缩

用较紧凑内容或专用状态替代较长历史。

**具体例子：**有损摘要应保留原始证据的可恢复位置。

[回到 F27 的完整讲解 →](foundations/27.md)


<span id="g157"></span>



<span id="section-157"></span>


### Provenance / 来源追溯

记录结论来自哪里以及对应版本和条件。

**具体例子：**“见文件”不如准确路径、范围、版本可核对。

[回到 F27 的完整讲解 →](foundations/27.md)


<span id="g158"></span>



<span id="section-158"></span>


### Index / 索引

为查找建立的辅助数据结构。

**具体例子：**有索引不保证内容新鲜或权限正确。

[回到 F28 的完整讲解 →](foundations/28.md)


<span id="g159"></span>



<span id="section-159"></span>


### 倒排索引

从词项找到包含它的文档记录。

**具体例子：**“超时”→文档1、5、8。

[回到 F28 的完整讲解 →](foundations/28.md)


<span id="g160"></span>



<span id="section-160"></span>


### BM25

基于词频、文档频率及长度校正的一类词项相关性评分。

**具体例子：**不理解所有同义表达，也不直接校验事实。

[回到 F28 的完整讲解 →](foundations/28.md)


<span id="g161"></span>



<span id="section-161"></span>


### Embedding（检索向量）

为查询与文档匹配产生的一组表示数字。

**具体例子：**不应与Token输入Embedding任意互换。

[回到 F28 的完整讲解 →](foundations/28.md)


<span id="g162"></span>



<span id="section-162"></span>


### ANN / HNSW

近似最近邻搜索及其图索引方法之一。

**具体例子：**加速候选查找可能牺牲部分召回。

[回到 F28 的完整讲解 →](foundations/28.md)


<span id="g163"></span>



<span id="section-163"></span>


### RAG

先检索外部材料，再让模型依据材料生成的系统模式。

**具体例子：**有引用或有检索不自动保证回答被证据支持。

[回到 F29 的完整讲解 →](foundations/29.md)


<span id="g164"></span>



<span id="section-164"></span>


### Reranking / 重排

对已召回候选做更细致比较并重新排序。

**具体例子：**若正确材料根本没召回，重排无法凭空找回。

[回到 F29 的完整讲解 →](foundations/29.md)


<span id="g165"></span>



<span id="section-165"></span>


### RRF

把各路排名的倒数形式相加来融合候选的一种方法。

**具体例子：**按rank而非直接相加不同模型的原始分数。

[回到 F29 的完整讲解 →](foundations/29.md)


<span id="g166"></span>



<span id="section-166"></span>


### HyDE / 假设文档

借助生成的假设回答表示来帮助检索的方法。

**具体例子：**假设内容不是可信事实，需要真实证据。

[回到 F29 的完整讲解 →](foundations/29.md)


<span id="g167"></span>



<span id="section-167"></span>


### GraphRAG / RAPTOR

利用图关系或分层摘要组织检索的不同方法。

**具体例子：**结构可帮助跨文档问题，也会产生构建与维护成本。

[回到 F29 的完整讲解 →](foundations/29.md)


<span id="g168"></span>



<span id="section-168"></span>


### AST

抽象语法树，表示程序的语法结构。

**具体例子：**能区分函数定义与普通字符串，但不包含全部运行事实。

[回到 F30 的完整讲解 →](foundations/30.md)


<span id="g169"></span>



<span id="section-169"></span>


### LSP

编辑器与语言服务交互的协议，支持定义、引用和诊断等。

**具体例子：**服务能力取决于语言实现与项目配置。

[回到 F30 的完整讲解 →](foundations/30.md)


<span id="g170"></span>



<span id="section-170"></span>


### Commit / Worktree

Git提交快照与当前工作目录的内容。

**具体例子：**未提交修改意味着二者可能不同。

[回到 F30 的完整讲解 →](foundations/30.md)


<span id="g171"></span>



<span id="section-171"></span>


### 语义 / 情景 / 程序性记忆

分别偏向稳定事实、具体经历与可复用执行方法的记忆分类。

**具体例子：**一次修复经历不应直接升级为通用规则。

[回到 F31 的完整讲解 →](foundations/31.md)


<span id="g172"></span>



<span id="section-172"></span>


### Valid time / Recorded time

事实适用的时间与系统记录或获知它的时间。

**具体例子：**政策1日生效、5日才录入，两个时间不能互换。

[回到 F31 的完整讲解 →](foundations/31.md)


<span id="g173"></span>



<span id="section-173"></span>


### TTL / 失效

按时间或条件不再默认使用一条缓存或记忆。

**具体例子：**过期不等于历史记录必定错误，只是不再作为当前事实。

[回到 F31 的完整讲解 →](foundations/31.md)


<span id="g174"></span>



<span id="section-174"></span>


### Skill

供Agent按需使用的专业指导及关联资源。

**具体例子：**不同于模型新增了一组权重。

[回到 F32 的完整讲解 →](foundations/32.md)


<span id="g175"></span>



<span id="section-175"></span>


### Routing / 路由

根据任务选择模型、工具、技能或执行分支的过程。

**具体例子：**误选与漏选要根据实际任务损失评价。

[回到 F32 的完整讲解 →](foundations/32.md)


<span id="g176"></span>



<span id="section-176"></span>


### Hook

在指定执行节点运行的程序性操作。

**具体例子：**适合必须执行的检查，但也会带来延迟与失败面。

[回到 F32 的完整讲解 →](foundations/32.md)


<span id="g177"></span>



<span id="section-177"></span>


### Subagent / Handoff

子Agent与控制或任务交接机制。

**具体例子：**必须考虑上下文、权限和结果证据如何传递。

[回到 F32 的完整讲解 →](foundations/32.md)


<span id="g178"></span>



<span id="section-178"></span>


### DAG / 关键路径

无环有向依赖图及决定理想完成时间的最长依赖链。

**具体例子：**独立任务并行，依赖任务仍需等待。

[回到 F32 的完整讲解 →](foundations/32.md)


<span id="g179"></span>



<span id="section-179"></span>


### Idempotency / 幂等

同一业务动作重复请求不重复产生额外效果的性质或实现目标。

**具体例子：**稳定业务键比每次重试生成新ID更关键。

[回到 F33 的完整讲解 →](foundations/33.md)


<span id="g180"></span>



<span id="section-180"></span>


### CAS / Compare-and-swap

仅当版本或当前值仍符合预期时才更新。

**具体例子：**避免旧分析覆盖新修改，但不覆盖全部外部副作用。

[回到 F33 的完整讲解 →](foundations/33.md)


<span id="g181"></span>



<span id="section-181"></span>


### Transaction / 事务

让一组操作满足特定原子性、一致性等边界的机制。

**具体例子：**单数据库事务不自动包含远端网络API。

[回到 F33 的完整讲解 →](foundations/33.md)


<span id="g182"></span>



<span id="section-182"></span>


### Atomic / 原子操作

相对指定观察边界，不暴露部分完成的操作。

**具体例子：**文件原子替换与跨文件、跨数据库原子性不同。

[回到 F33 的完整讲解 →](foundations/33.md)


<span id="g183"></span>



<span id="section-183"></span>


### Exactly-once

要求业务效果恰好一次的语义目标。

**具体例子：**至少一次传输加幂等可帮助实现，不是任意系统自动保证。

[回到 F33 的完整讲解 →](foundations/33.md)


<span id="g184"></span>



<span id="section-184"></span>


### 反例 / 性质测试

用失败样例或一般应成立的关系检验行为。

**具体例子：**排除规则修改后，不在排除范围的路径仍应保留。

[回到 F34 的完整讲解 →](foundations/34.md)


<span id="g185"></span>



<span id="section-185"></span>


### 回归测试 / Regression

检查修改未破坏已要求的旧行为。

**具体例子：**旧测试全绿不代表新需求已实现。

[回到 F34 的完整讲解 →](foundations/34.md)


<span id="g186"></span>



<span id="section-186"></span>


### Mutation / 变异测试

故意改坏实现来检查测试能否发现错误。

**具体例子：**总返回成功的实现也全绿，说明测试区分力不足。

[回到 F34 的完整讲解 →](foundations/34.md)


<span id="g187"></span>



<span id="section-187"></span>


### Precision / Recall

返回项中正确的比例，和所有该找到项中实际找到的比例。

**具体例子：**分母不同，必须先定义相关或必需的标签。

[回到 F35 的完整讲解 →](foundations/35.md)


<span id="g188"></span>



<span id="section-188"></span>


### pass@k / pass^k

通常分别指k次至少一次成功的估计与多次全成功等可靠性口径，具体按基准定义。

**具体例子：**p=.8、独立3次，至少一次.992，全成功.512。

[回到 F35 的完整讲解 →](foundations/35.md)


<span id="g189"></span>



<span id="section-189"></span>


### MRR / nDCG

关注首个相关项位置、或多等级相关排序质量的检索指标。

**具体例子：**不能代替最终回答准确与权限检查。

[回到 F35 的完整讲解 →](foundations/35.md)


<span id="g190"></span>



<span id="section-190"></span>


### 配对实验 / Paired test

同一批任务对照两个方案，减少任务难度差异。

**具体例子：**独立随机性和运行条件仍需控制。

[回到 F36 的完整讲解 →](foundations/36.md)


<span id="g191"></span>



<span id="section-191"></span>


### 置信区间 / Bootstrap

表达估计不确定性的区间及一种重采样方法。

**具体例子：**区间依赖抽样假设，不是未来成功保证。

[回到 F36 的完整讲解 →](foundations/36.md)


<span id="g192"></span>



<span id="section-192"></span>


### LLM-as-a-judge

用模型按规则评价输出的方法。

**具体例子：**可能受长度、顺序或风格影响，需校准与可执行证据。

[回到 F36 的完整讲解 →](foundations/36.md)


<span id="g193"></span>



<span id="section-193"></span>


### Prompt injection

不可信内容试图改变Agent行为或越过授权的攻击。

**具体例子：**网页正文“忽略规则”不是新用户指令。

[回到 F37 的完整讲解 →](foundations/37.md)


<span id="g194"></span>



<span id="section-194"></span>


### ACL / 租户隔离

对对象可访问者的限制，以及不同用户组织之间的数据边界。

**具体例子：**检索与缓存都需要避免跨权限泄露。

[回到 F37 的完整讲解 →](foundations/37.md)


<span id="g195"></span>



<span id="section-195"></span>


### Sandbox / 沙箱

限制程序可访问文件、网络或资源的隔离环境。

**具体例子：**隔离边界之外的工具仍需独立授权。

[回到 F37 的完整讲解 →](foundations/37.md)


<span id="g196"></span>



<span id="section-196"></span>


### TOCTOU

检查时与使用时目标发生变化的竞争问题。

**具体例子：**批准文件A之后实际操作不能悄悄变成文件B。

[回到 F37 的完整讲解 →](foundations/37.md)


<span id="g197"></span>



<span id="section-197"></span>


### Trace / Span

一次任务的执行轨迹与其中有开始结束的操作跨度。

**具体例子：**并行跨度的耗时不能直接全加成墙钟时间。

[回到 F38 的完整讲解 →](foundations/38.md)


<span id="g198"></span>



<span id="section-198"></span>


### TTFT / p95

首个Token延迟，以及95%样本不超过的分位数等运行指标。

**具体例子：**平均值正常仍可能尾延迟很差。

[回到 F38 的完整讲解 →](foundations/38.md)


<span id="g199"></span>



<span id="section-199"></span>


### Backpressure / 退避

过载时限制上游继续推送，以及失败重试间隔逐渐增大的机制。

**具体例子：**延迟重试不解决业务重复执行本身。

[回到 F38 的完整讲解 →](foundations/38.md)


<span id="g200"></span>



<span id="section-200"></span>


### Canary / Rollback

小范围验证新版本与出现问题时恢复旧版本。

**具体例子：**提示、模型、索引、工具应作为可追溯版本组合。

[回到 F38 的完整讲解 →](foundations/38.md)


<span id="g201"></span>



<span id="section-201"></span>


### Patch / 多模态编码

把图片分片或用视觉编码器转为数值表示的过程。

**具体例子：**224×224、16×16切片得196片，但不保证最终恰196Token。

[回到 F39 的完整讲解 →](foundations/39.md)


<span id="g202"></span>



<span id="section-202"></span>


### Calibration / 校准

置信表达与长期实际正确频率相符合的性质。

**具体例子：**一组90%信心预测应在可比条件下约90%正确。

[回到 F39 的完整讲解 →](foundations/39.md)


<span id="g203"></span>



<span id="section-203"></span>


### SAE / 可解释性

稀疏自编码器等技术研究内部表示特征。

**具体例子：**能解释部分特征不等于完整读出所有原因。

[回到 F39 的完整讲解 →](foundations/39.md)


<span id="g204"></span>



<span id="section-204"></span>


### Ablation / 消融

去掉或替换某个组件观察影响的对照方法。

**具体例子：**先验证新增Review是否真的减少缺陷，而非只增加步骤。

[回到 F40 的完整讲解 →](foundations/40.md)


<span id="g205"></span>



<span id="section-205"></span>


### Scaling law

特定训练设置下观察到的规模与损失等的经验关系。

**具体例子：**不能不加条件外推到所有任务或所有模型。

[回到 F40 的完整讲解 →](foundations/40.md)

AI系统工程：从基础到内部  
[全书目录](contents.md) · [术语与符号](glossary.md) · [参考资料](sources.md)