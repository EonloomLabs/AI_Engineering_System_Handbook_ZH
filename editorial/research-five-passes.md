# Deep Wiki：模型章节重编的五轮证据记录

## 1. 结构与入口
高置信：`TinyLM.__init__` 定义12组参数，`forward`接收整数ID；`run`使用SEQUENCES构造训练输入；`generate`载入训练权重之后调用forward。依据：labs/model/lab/tiny_model.py:33–98,178–258。

## 2. 数据与状态
高置信：标签在run:182切片一次；loss不再移动标签；backward计算梯度但不更新参数；opt.step才改变权重；generate在inference_mode中保存已处理K/V并选择下一项。图解按实际调用链而非文件名生成。

## 3. 接口与依赖
高置信：PyTorch实现与标准库reference_inference.py使用同一JSON权重。二者的模型构型相同；接口的自动转置、自动shift和非方阵mask不能凭名称假定相同。所有接口陷阱以test_model.py中的实际断言为边界。

## 4. 反例与代价
已阅读的测试包括：移除因果掩码、重复shift、交叉熵前再次softmax、错误位置、权重变化后复用旧缓存、eval与梯度状态混淆。推导只覆盖本模型；量化、RoPE、GQA、DPO、分布式效率不当成本地实现能力。

## 5. 整合决策
基础篇承担词表→前向→训练→推理，系统篇承担源码级回传、算子边界与服务权衡。28篇旧独立课程按180个概念小节分配，删除独立课程页面；参数、代码和运行记录移到实验目录。统一重新编号学习顺序，并逐条重映射原站内链接。读者只有基础与系统两条已有层级，不用在平行教程间拼接。

## 验证边界
新验证记录保存在validation/integration中。未声称调用Copilot插件CLI、重训商业模型、运行GPU性能评测，或验证闭源产品内部逻辑。方法源为Microsoft deep-wiki固定提交，内容源为用户提供的本地教材与程序。
