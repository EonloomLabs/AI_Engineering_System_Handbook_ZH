---
title: "把数字改一下，看每一步怎样变化"
description: "AI系统工程：本地教学正文与可追溯图表"
---


<span id="model-experiments"></span>


## 模型实验与可复核证据

讲解本身位于基础课程和系统机制；本区仅集中保存可运行程序、训练产物和逐步数值，便于在正文中核对。统一输入、初始权重和训练后权重各有明确记录。

| 实验材料 | 用途 | 正文入口 |
| --- | --- | --- |
| [数值查看器](labs/model-viewer.md) | 观察更新前前向、反向、实际更新与加载后生成 | [F14前向](foundations/14.md)／[系统04反向](chapters/04.md) |
| [参数与梯度记录](labs/model-values.md) | 对照每张表与计算状态 | [F16训练](foundations/16.md) |
| [完整程序与运行结果](labs/model-run.md) | 复算和训练后推理 | [F18加载与生成](foundations/18.md) |
| [带行号的实现](reference/model-code.md) | 追踪TinyLM.forward、manual\_backward、generate | [系统02逐算子前向](chapters/02.md) |

阅读指南与附录


<span id="labs-title"></span>


# 把数字改一下，看每一步怎样变化


<span id="model-experiment"></span>


## 同一模型的训练与推理复算

本实验对应基础课程F01—F21与系统机制01—08章。沿正文学习时可直接使用嵌入的数值查看器；这里集中提供原始数据和程序。

[逐步中间值](labs/model-viewer.md) · [参数与梯度记录](labs/model-values.md) · [运行方法与完整代码](labs/model-run.md) · [带行号的源码依据](reference/model-code.md) · [原理与接口来源](reference/model-sources.md)

四个本地交互实验。没有网络请求，不调用商业模型，不需要安装程序；它们检验你是否读懂数值与对象关系，不衡量模型的语言能力。


<span id="lab-shape"></span>


## 1．张量形状与存储大小

修改三个轴的长度。注意编号表只有B和T，查表结果才新增每个位置的宽度d。


<span id="shape-form"></span>


输入条数 B
<span id="batch"></span>
每条位置 T
<span id="tokens"></span>
每位置宽度 d
<span id="width"></span>
每数的字节数
<span id="bytes"></span>



<span id="shape-output"></span>


试一试：把T改128、d改4096、字节改2。这里只估算输出这一份数字，不包含模型参数与缓存。


<span id="lab-embedding"></span>


## 2．选一个编号，看它实际取出哪一行

查找编号 
<span id="embedding-id"></span>
0 · PAD1 · 我2 · 爱3 · 学习4 · 你5 · ！

| 编号 | 片段 | 第0个数 | 第1个数 | 第2个数 | 第3个数 |
| --- | --- | --- | --- | --- | --- |
| 0 | <PAD> | 0.0 | 0.0 | 0.0 | 0.0 |
| 1 | 我 | 0.2 | -0.1 | 0.7 | 0.4 |
| 2 | 爱 | -0.3 | 0.8 | 0.1 | 0.5 |
| 3 | 学习 | 0.6 | 0.2 | -0.4 | 0.9 |
| 4 | 你 | 0.1 | -0.5 | 0.9 | 0.3 |
| 5 | ！ | -0.2 | 0.4 | 0.5 | -0.6 |


<span id="embedding-output"></span>


所有数字是特意设置的小数与负数，并非0/1的二进制编码；没有把每一列固定解释成某种语义。选择编号后，下方同时显示这个编号对应的One-hot标识和真正从参数表查出的浮点向量。


<span id="lab-softmax"></span>


## 3．从分数到概率，四步全部写出来

依次看：减最大值、取指数、求总和、除总和。把所有分数都加1000，概率应保持相同。

分数（逗号分隔） 
<span id="logits-input"></span>

<span id="softmax-output"></span>



<span id="lab-mask"></span>


## 4．有历史缓存后，哪些位置可以被读取

查询位置在行，供读取的位置在列。已有3个位置再处理2个新位置时，表是2行5列，而不是2行2列。


<span id="mask-form"></span>


已有历史位置数
<span id="past"></span>
新位置数
<span id="new"></span>



<span id="mask-output"></span>

<span id="mask-note"></span>


此表只展示因果可见关系。真实接口还需合并填充与其他掩码，并核对真假及偏移约定。

[完整Python代码与运行结果 →](checks.md)[回到输入表示示例](examples/input-representation.md)

AI系统工程：从基础到内部  
[全书目录](contents.md) · [术语与符号](glossary.md) · [参考资料](sources.md)