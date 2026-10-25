# 内容审查：先审查，后设计

## A01 · 计算缺口
位置：foundations/05.html

Embedding与位置相加只留下文字承诺，E[2]+P[2]数表被移除

证据：输入表示X怎样真正出现：分别取E[2]和P[2]，对应特征相加：

验收：复算E[2]+P[2]==initial_trace.x[0][2]

## A02 · 计算衔接
位置：foundations/10.html

RMSNorm给出分母但未展示四格N1，下一课直接使用N1

证据：r=0.469718001；下一课N1=[-0.425787,...]

验收：四格与run.json一致

## A03 · 内容缺失
位置：foundations/11.html

三张参数表完全展开标题下只有来源，无三张表

证据：core-qkv-2--mc-section-2

验收：矩阵乘法得到原Q/K/V，来源哈希不变

## A04 · 计算缺口
位置：foundations/14.html

残差、FFN激活和最终词表头缺少中间数表，只保留单格结果

证据：core-value-residual-5 / core-ffn-3/4 / core-output-head-2

验收：逐个结果与唯一run.json校验

## A05 · 内容缺失
位置：foundations/18.html

第一轮声称八项实际值是，但八项logits与概率不存在

证据：core-generation-2--mc-section-2

验收：每轮与generation_full一致，不借用初值

## A06 · 内容缺失
位置：foundations/19.html

一次两个新Query的mask以冒号结束，未列允许表

证据：core-cache-5--mc-section-5

验收：允许表s<=t，不用左上三角代替

## A07 · 内容缺失
位置：chapters/02.html

整条链的同一位置视图标题下没有数表

证据：core-forward-trace-3--mc-section-3

验收：完整trace各阶段有行，数值可复算

## A08 · 顺序冲突
位置：foundations/01.html, foundations/11.html, foundations/14.html

外向内改序后仍有F22以后展开、方差F14才解释等旧引用

证据：F01/F11/F14文字与curriculum顺序不一致

验收：针对旧语句的回归扫描

## A09 · 前置缺失
位置：foundations/26.html, foundations/29.html, foundations/36.html

Token、HyDE、Bootstrap在阶段内首次使用/自检前没有足够解释

证据：课程模型阶段在阶段4；上述术语阶段2/3已出现

验收：词义先于自检，基础章节仍简洁

## A10 · 实践衔接
位置：foundations/03.html, chapters/01.html

聊天模板与二次tokenize的重复特殊标记风险未形成可检查过程

证据：HF chat_templating v4.44.2

验收：文本与模板版本记录，测试拒绝重复控制前缀

## A11 · 接口冲突风险
位置：foundations/04.html, foundations/16.html, chapters/04.html

手工移位的tiny_model和库内部移位没有统一对照，容易移位两次

证据：tiny_model.py training_loss；Transformers v4.52.3 ForCausalLMLoss

验收：固定序列目标配对测试

## A12 · 概念衔接
位置：foundations/12.html, foundations/17.html, chapters/04.html

可见位置、监督位置、PAD/EOS、打包边界容易混淆

证据：HF/TRL pinned docs与现有mask章节

验收：masked标签仍可被注意力读；PAD/EOS测试

## A13 · 深度衔接
位置：foundations/16.html, chapters/04.html

数据治理已有原则，但从数据记录到去重簇、划分、训练计数缺少连续可复算例

证据：Q019有原则与多个孤立例；CS336 assignment4

验收：同源和重复簇分区不交叉，过滤计数守恒

## A14 · 工程遗漏
位置：foundations/16.html, chapters/04.html

保存权重与精确继续训练的恢复状态没有足够显式对照

证据：本包weights_trained.json仅spec/parameters

验收：使用真实torch比较恢复AdamW与仅权重续训

## A15 · 外部资料迁移
位置：foundations/17.html, chapters/05.html

蒸馏SFT、PPO、DPO和组内奖励的对象不能只靠方法名区分

证据：Dive ch4/ch11；现有Q021/22

验收：目标计算和参考项反例

## A16 · 数据偏差
位置：chapters/05.html

数学SFT来源用isdigit筛答案，会改变任务分布；labels复制不证明只监督助手

证据：Dive notebook lines240–530

验收：负数小数分数可解析，非数值和恶意表达式拒绝

## A17 · 覆盖遗漏
位置：chapters/05.html, chapters/18.html, chapters/28.html

外部记忆、知识编辑、检索、微调缺少可撤回性与验证范围的统一对照

证据：Dive ch3；原记忆与SFT章节

验收：概念矩阵不把删除外部数据等同参数遗忘

## A18 · 计量歧义
位置：chapters/08.html

TTFT例prefill后额外20ms未说明性质，容易与首Token已经产生重复计算

证据：Q030公式M*t_decode与示例120ms

验收：固定事件时间线复算TTFT、TPOT、E2E

## A19 · 优化衔接
位置：foundations/21.html, chapters/07.html, chapters/08.html

前缀缓存与decode缓存收益、吞吐与任务完成仍有跨层解释跳跃

证据：vLLM APC；CS2680 A4

验收：相同输出长度计算，独立任务成功不等于token吞吐

## A20 · 过时建议筛选
位置：foundations/26.html, chapters/13.html, chapters/06.html

旧CoT教程可能被误读为所有模型都应长写思维过程

证据：Dive ch2；OpenAI reasoning best practices

验收：不得将多数票比例当事实概率

## A21 · 执行位置遗漏
位置：chapters/17.html, chapters/22.html

本地夹具与真实多容器任务环境不同，当前路径不等于目标仓库

证据：CS2680 A3 sandbox contract

验收：假运行位置与错误基线负例

## A22 · 评测完整性
位置：chapters/23.html, foundations/36.html

调参集与最终留出、失败费用、零成功分母需在同一记录中连接

证据：CS2680 A3/A4；现有Evals

验收：样例成本和置信指标可复算

## A23 · 安全概念遗漏
位置：chapters/24.html

离线风险识别准确率不能直接证明执行防线

证据：Dive R-Judge章节；现安全章节

验收：高分风险识别仍可执行错误的反例

## A24 · 多模态/校准衔接
位置：foundations/39.html, chapters/27.html

GUI自报1–5分与成功概率、图像块与语义对象需明确区分

证据：Dive ch8/ch9；现Q107

验收：坐标映射和置信分组计数测试

## A25 · 来源覆盖取舍
位置：chapters/27.html

水印/隐写与可信度关系目前缺少明确边界

证据：Dive ch5/ch7

验收：混淆矩阵复算，检测分数非作者身份证据

## A26 · 版本真实性
位置：chapters/28.html, sources.html

外部教程包含旧模型/旧软件环境及条件限定实验成绩

证据：Dive eleven READMEs and selected notebook ranges

验收：来源范围与教材结论逐项映射

## A27 · 实践衔接
位置：labs/projects/assignment1.html, labs/projects/assignment2.html, labs/projects/assignment3.html, labs/projects/assignment4.html, labs/projects/assignment5.html

外向内五个作业需要相同任务ID和不可混用的夹具/模型/服务成绩

证据：CS2680 public assignments；labs/stack

验收：5个作业共享manifest，真实模型未运行明确标注

## A28 · 符号与范围
位置：foundations/02.html, foundations/06.html, foundations/08.html, foundations/20.html

N/V/T/d与逻辑张量/实际存储/低秩节省对象需要跨课一致

证据：固定模型spec；现基础多套局部例

验收：字节数/低秩参数量/shape可复算

## A29 · 连贯性复查
位置：chapters/09.html, chapters/10.html, chapters/11.html, chapters/12.html, chapters/14.html, chapters/19.html, chapters/20.html, chapters/21.html, chapters/25.html, chapters/26.html

产品特定快照与通用教学循环需分开；状态、代价和权限不能靠术语代替证据

证据：既有固定Codex来源；现正文

验收：来源日期沿用而非假标今日，结构与引用检查

## A30 · 静态结构与派生稿
位置：all-core

正文、搜索、单页和Markdown可能在局部修改后不一致

证据：当前目录/单页/搜索依赖

验收：95页引用/旧短语/数值契约/隐藏答案/布局全检查
## 追加的段落顺序检查

A31：前向章包含完整生成/缓存续篇，且A.3在A.4之后。A32：相邻DPO公式重复而输入变化。A33：标签问题中提前出现输出头梯度。分别按原机制内部重排、替换重复推导及移动梯度段落；不新增教学分支。
