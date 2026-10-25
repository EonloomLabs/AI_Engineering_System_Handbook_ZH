---
title: "作业02｜构建：接管循环、工具和验收"
description: "主流程课程的可编辑正文"
---

<a id="page-title"></a>

# 作业02｜构建：接管循环、工具和验收

**作业范围**

这是本教材的原创累积实验。默认离线路径仅操作生成的临时数据；真实模型、外部账号及GPU路径须自行配置，未运行项明确保留为NOT\_RUN。

保留相同索引任务，替换“别人替你控制流程”的部分。本次开始建立后续优化沿用的任务集、执行契约和基线。

<a id="contract"></a>

## 先写循环的契约

一轮接收`messages`和`tools`，后端返回assistant消息。消息可以包含多个函数调用，也可以结束生成。宿主先验证整个调用列表的结构与ID，再逐个执行允许的工具，将结果按`tool_call_id`回填。回填之后，模型才有机会依据真实观察修改下一步。

```
while rounds < budget:
    request_view = prepare_history(history, policy)
    message = backend.complete(request_view, allowed_tools)
    validate_message_and_call_ids(message)
    history.append(message)
    if no_tool_calls(message):
        stop_reason = "model_final"
        break
    for call in message.tool_calls:
        result = execute_with_schema_and_path_checks(call)
        history.append(tool_result(call.id, result))
final_state = independent_host_grader()
success = final_state.correct and stop_reason == "model_final"
```

这是本实验控制结构的教学摘要。实际异常分支、预算计数和字段处理见`core.run_episode`，不要把伪代码当作可直接部署的完整服务。

<a id="objects"></a>

## 为什么是这三个工具

| 工具 | 输入与结果 | 关键错误 |
| --- | --- | --- |
| read\_file | 只允许rules.json、README.md；返回内容、SHA-256与冗余诊断 | 路径越界、符号链接、未知文件 |
| set\_exclusion | 根目录名＋观察到的哈希；只改配置 | 非法目录名、过期观察、额外字段 |
| verify\_index | 无参数；核对当前配置的四项条件 | 当前状态不符；不允许修改判分规则 |

工具窄是为了让接口错误可定位。真实编程Agent可提供更通用的Shell或补丁工具，但那会增加授权、转义、环境和副作用问题，不是把函数名换掉就完成安全升级。

<a id="run"></a>

## 运行与故障注入

```
cd AI_Systems_Engineering_Textbook_ZH/labs/stack
python3 run.py build
python3 -m unittest -v test_stack
```

先阅读`test_stack.py`，逐项核对以下路径：错误JSON、重复call\_id、未知工具、错误参数类型、过期哈希、提前final和预算耗尽。对于可以表达成工具错误的情况，结果必须回填；对于后端或协议错误，应留下清楚的停止原因。不要为了“跑完”把所有异常都吞掉。

<a id="section-c4b8d53f9861"></a>

### 不是形式上“调用过测试”就算通过

验收器在循环结束后再次读取真实配置。代理内部的`verify_index`是可用观察，最后的宿主检查是交付判断；即使代理忘了验证，宿主也不能只采信最后一句话。反过来，产物正确但预算耗尽仍记录为未正常完成，便于区分不同失败路径。

<a id="baseline"></a>

## 建立可比较基线

八个公开合成任务只改变根目录名称。前六个标development，后两个标heldout-demo。这是切分方式的演示，不是秘密测试；它们任务结构相似，也不能证明跨仓库泛化。要做真实Agent能力比较，需要自备不同类型任务、初始状态、可复查答案和固定验收程序。

把基线保存为代码版本、提示词、工具Schema、任务文件、模型版本、解码配置和预算的组合。记录每一次尝试，包括坏环境和失败；排除任务必须说明理由并对所有候选使用相同规则。后续更换模型属于新的实验条件，不能假装只改了上下文。

<a id="review-assignment-2-handoff"></a>

### 循环的输出要能与观察基线直接比较

沿用作业1的任务语义与验收规则，记录宿主版本、工具schema版本、失败/未知状态。加入真实模型适配器时，另标运行方式，不把脚本决策轨迹和LLM能力结果混为一组。

| 最小交接字段 | 含义 |
| --- | --- |
| task\_set\_revision | 任务集合与拆分，不只任务数量 |
| artifact\_before / artifact\_after | 待处理与交付工件的版本 |
| system\_revision | 代码、模型、模板、工具/检索设置 |
| run\_mode | script\_fixture / local\_numeric / live\_model |
| budget / seed / environment | 可控条件；不支持或未测写明 |
| outcome / evidence | 成功、失败、未知、未运行与对应原始记录 |

这些字段用于对照，不要求为小练习搭建数据库或复杂平台。一份JSON和已有日志足够；没有改变的输入用同一版本，新增资料不要悄悄覆盖旧结果。

依据与范围：[[CS2680-A3]](../../sources.md#review-CS2680-A3)；[[CS2680-A4]](../../sources.md#review-CS2680-A4)；[[LOCAL]](../../sources.md#review-LOCAL)。算例条件在本节给定；教学结果不代表商业模型或生产性能。

<a id="exercise"></a>

## 需要自己完成的修改

增加一个“不应修改”的任务；增加一个内容合法但业务参数无效的调用；增加一个在读取后模拟其他写者改动的测试。解释单进程单写者的哈希检查与真正跨进程CAS的区别。不得用修改测试来让错误行为通过。

<a id="deliver"></a>

## 交付与评分依据

交付代码、基线清单、全部运行结果、失败分类和一个从请求到验收的手工追踪。能复现故障比报告一个高通过率更重要。评分维度是契约清楚、错误可观察、边界可测试、结果可重现；不是与Harvard榜单分数对齐。

<details class="quiz-answer" open=""><summary>参考答案：重复call_id为什么不能按数组位置修补？</summary><div class="answer"><p>ID连接模型提议、工具结果和历史恢复。宿主自行改名可能与服务端持久状态不一致。应明确拒绝或按已声明的重放协议处理，而不是把不确定调用默默解释为新调用。</p></div></details>

方法参照[CS2680循环作业](../../sources.md#source-set-3e7382dd--harvard-a2)；这里的任务、后端夹具、评分表及测试均为教材原创，不是其未公开测试或作业答案。

<a id="local-evidence"></a>

## 本地代码与记录

[带行号的完整实现](../stack/code.md) · [实际运行范围](../../../labs/stack/results/run-report.json) · [本轮机制测试结果](../../../labs/stack/results/tests.json)