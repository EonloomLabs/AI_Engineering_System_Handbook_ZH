---
title: "实验手册：实现、反例与实测边界"
description: "AI系统工程：本地教学正文与可追溯图表"
---

专题研修


<span id="section-0"></span>


# 实验手册：实现、反例与实测边界


<span id="labs-h1"></span>


## 运行环境

离线阅读HTML无需Python，也不需要联网。执行代码需要Python；配套结果的运行环境为Python 3.13.5 / Linux，NumPy和PyTorch已安装。脚本目标为Python 3.10及以上，但没有在每个Python版本、Windows或macOS上逐一验证。

默认实验不发送网络请求。NumPy用于数值与反向传播，PyTorch仅用于小模型训练。标准库机制测试无需这两项；缺少NumPy时相关测试会明确跳过，不应把“跳过”解读成通过。依赖安装本身可能需要联网，不属于离线教材运行的一部分。

在解压后的根目录执行：

```
cd studies/labs
python3 run_all.py
python3 train_tiny_lm.py --output ../reports/tiny_training.json
```

配套运行记录中49项测试全部通过，没有失败、错误或跳过。测试数量不是生产质量证明；下面逐项说明它们覆盖什么、不覆盖什么。


<span id="labs-h2"></span>


## L01｜编码、前向、缓存与采样

[`numerics.py`](code/numerics.md)实现可逆字节级BPE、小型现代Decoder前向、RoPE/GQA、增量KV缓存、分块在线softmax、DPO损失与推测采样。数值使用NumPy float64，追求透明与可验证，不追求服务吞吐。

缓存正确实现与完整前向最大误差约1.55×10⁻¹⁵；故意使用错误位置偏移后误差约3.17，显示测试确实能区分故障。分块softmax与完整计算误差约3.55×10⁻¹⁵。这些是当前随机种子和小尺寸的数值结果，不是任意精度、长度或硬件的保证。

推测采样以30,000次抽样比较目标分布与经验分布。它验证接受—拒绝机制，不证明真实服务加速。程序没有GPU、并行草稿模型或生产批调度。


<span id="labs-h3"></span>


## L02｜真正的解析反向传播

[`attention_gradients.py`](code/attention_gradients.md)包含单头注意力前向、解析反向和有限差分。Q、K、V的最大绝对梯度误差分别约9.14×10⁻¹¹、1.96×10⁻¹⁰、1.17×10⁻¹⁰。未来位置梯度为零、全遮挡行拒绝、形状错误拒绝也有测试。

有限差分验证的是当前函数的局部导数，不是目标函数是否符合业务；共同的掩码错误仍可能使解析和数值方法一起错误。第31章说明如何用独立语义性质补充。


<span id="labs-h4"></span>


## L03｜真实小型语言模型训练

[`train_tiny_lm.py`](code/train_tiny_lm.md)训练一个18,320参数、两层因果Transformer。PyTorch 2.10.0+cpu，100步AdamW，合成循环Token序列。训练损失从2.846790下降到0.003446，训练Token准确率为1.0，因果前缀误差为0。

这不是打印预设曲线：脚本确实执行了前向、损失、反向与参数更新。但数据集非常简单，没有独立泛化评测，也没有自然语言能力评测。不得把100%训练准确率写成模型已经具备语言理解。

此模型为方便教学使用学习位置向量、MHA与GELU；前向数值实验则使用RoPE、GQA、SwiGLU。两套实现不同，不能合称某一商业模型的复现。


<span id="labs-h5"></span>


## L04｜权限、版本与词项检索

[`retrieval.py`](code/retrieval.md)实现BM25、RRF和Python AST范围提取。权限、租户、版本在评分前过滤；缓存键包含调用身份与版本。测试覆盖未授权文档、旧版本、缓存污染与索引替换。

中文分词只是单字教学策略；没有真实向量编码器、ANN索引或重排模型。它证明权限与索引契约，不证明语义召回达到生产要求。HNSW、IVF/PQ、ColBERT与重排的实现取舍在正文解释，未宣称已在实验中部署。


<span id="labs-h6"></span>


## L05｜上下文依赖和双时间记忆

[`context_memory.py`](code/context_memory.md)提供带依赖闭包的贪心装包、确定性Checkpoint字段检查，以及SQLite事实记忆。预算数值是作者设定的教学成本，不是商业模型Tokenizer实测。

时间测试区分事实何时有效与系统何时知道，展示迟到信息不能反写过去的认知状态；冲突返回不确定，而不是强行选最近文本。实现只覆盖本书定义的有限生命周期，不是完整双时间数据库。

Checkpoint检查只能检查字段、版本与引用；它不能自动判断自然语言摘要是否保留所有否定条件。真实模型压缩保真实验必须另外执行。


<span id="labs-h7"></span>


## L06｜流式协议的字节与完成语义

[`sse_protocol.py`](code/sse_protocol.md)处理UTF-8跨分片、SSE数据行、增量参数与完成事件。测试故意切在“中文.py”的字节中间，确认最终JSON仍正确；截断流、失败事件、重复ID冲突不会被当成成功工具调用。

它是协议子集教学实现，不是完整SSE或全部Responses事件SDK。等到完整响应完成才调度工具是本书保守策略，不声称所有Agent都这样做。


<span id="labs-h8"></span>


## L07｜真实崩溃窗口与恢复

[`journal.py`](code/journal.md)在文件替换之后、数据库操作完成之前调用`os._exit(75)`，通过真实子进程退出制造中断。恢复后看到文件已为目标内容，记录reconciled，不重复写入；不满足前置内容或相同ID不同参数会拒绝。

它是单写者本地示例，不提供恶意并发下的原子文件安全，不宣称防御全部符号链接/硬链接竞态，也没有模拟断电和文件系统损坏。SQLite事务不可能自动涵盖外部服务副作用。


<span id="labs-h9"></span>


## L08｜完整仓库补丁与测试

[`capstone.py`](code/capstone.md)创建小型仓库和8项测试。初始5项失败；控制器读文件、提交原创补丁，修改后8项通过；随后改变工件，完成检查拒绝沿用旧绿色结果。

动作序列是脚本控制，不是LLM自主规划。测试、文件、子进程和补丁是真实执行。完整调用轨迹、diff、stdout与退出码在结果页展开，可以逐条复核，而不只看“通过”标签。


<span id="labs-h10"></span>


## L09｜统计与评测

[`statistics_lab.py`](code/statistics_lab.md)实现pass@k、Wilson区间、配对任务bootstrap与McNemar精确检验。所有输入为合成数据，只验证计算。示例中的成功率变化与置信区间不是Codex、Claude或Copilot跑分。

尤其注意按任务重采样，而不是把同一任务的多次运行当成独立样本。p值、区间和效应量各有用途，不能相互替代。


<span id="labs-h11"></span>


## L10｜可选的真实只读LLM实验

[`live_readonly.py`](code/live_readonly.md)保留一个需要显式启用的OpenAI Responses只读适配器，默认不运行。使用前必须自行确认API账户、模型可用性、费用与发送的目录；程序仅允许读取限定后缀、大小与根目录内文件。不能把凭据或敏感源码目录作为试验根。

```
# 以下命令会向外部API发送所选目录中的信息，并可能收费；此可选入口未实测。
# 先设置OPENAI_API_KEY，使用自己账户已确认可用的模型标识。
python3 live_readonly.py --allow-paid-api --model YOUR_MODEL_ID --root ./sandbox_repo
```

它不是完善的生产连接器，也不是评测平台。不自动重试网络写操作，不在包中保存API Key。由于未进行真实API验证，产品接口未来发生变化时需要根据当前官方接口调整。


<span id="labs-h12"></span>


## 结果如何阅读

`reports/test_results.json`和`test_log.txt`是机制测试及贯穿案例的原始记录，`tiny_training.json`是实际训练记录。二者分开，防止把测试通过与模型能力混为一谈。第一次阅读可以先看结果解说；深入时逐行查看代码，再改动故障点复现。

本书不以“测试全绿”结束工程判断。生产项目还需要真实任务集、目标平台测试、权限威胁分析、成本与延迟测量、回归和人工验收。第30章给出迁移这些实验时应补交的证据。

[完整实际结果与调用轨迹](results.md)[12个Python源码文件](source-code.md)[原始测试日志](../../studies/reports/test_log.txt)

AI系统工程：从基础到内部  
[全书目录](../contents.md) · [术语与符号](../glossary.md) · [参考资料](../sources.md)