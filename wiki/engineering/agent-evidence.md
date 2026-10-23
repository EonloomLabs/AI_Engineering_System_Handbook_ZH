---
title: "Agent与工程机制：证据、知识关系与覆盖 · AI系统工程"
description: "固定版本、官方资料与教学推导分开标注。"
---

# Agent与工程机制：已取得的证据、阅读范围与核验

正文仍按基础课程与系统机制阅读。本页用于追溯来源，不是另建一套课程。Codex固定提交：`86e17e98c7f901277aeeb4649cf1b01462b082f2`。

## 资料确实取得了什么

上一轮42项来源的直接下载全部失败，却仍保留带源码口吻的推导。这不能算来源核验。本轮先通过GitHub连接器取得指定源码，通过官方网页文本接口取得工程文章，再修订对应教材。旧失败记录没有被覆盖成成功。

| 资料 | 本轮取得及阅读 | 不作的声明 |
| --- | --- | --- |
| Codex 18个文件 | 4份完整源文件落盘并与Git blob哈希一致；其余按所列行范围阅读，保留可确认的摘录与研读笔记 | 不是完整仓库下载；未执行Rust工程测试 |
| Anthropic 17篇工程文章 | 官方正文通过网页文本工具取得并阅读；保存中文笔记、日期与边界 | 不镜像整篇版权原文；配图、视频及外链不算全读 |
| Claude Code 7份文档 | 与课程主张相关章节取得并核对 | 不是整个文档站或全部Hook事件逐项验证 |

容器直连下载仍因DNS失败；逐文件/官方文本读取则成功，二者在取得记录中分别保留。[机器可读来源清单](agent-practice/verified/manifest.json) · [取得方法与限制](agent-practice/verified/ACQUISITION.md) · [上一轮失败记录](agent-practice/prior-failed-source-retrieval.json)

## 正文入口

所有更新仍嵌入原来的课程位置。

* [一次回答结束，为什么任务仍未完成？](../chapters/09.html#agent-practice-loop)
* [为什么每次模型调用都需要一致的上下文快照？](../chapters/09.html#agent-practice-snapshot)
* [流式返回：什么时候参数真的可以执行？](../chapters/10.html#agent-practice-stream)
* [工具存在、模型看见、能调用、获授权：四层检查](../chapters/11.html#agent-practice-tools)
* [前置检查、后置检查为什么不能互相替代？](../chapters/10.html#agent-practice-hooks)
* [并行工具为什么可能先执行完、后显示结果？](../chapters/20.html#agent-practice-parallel)
* [成功写入但没有确认：重试怎样变成重复副作用](../chapters/21.html#agent-practice-recovery)
* [上下文组装为什么不能只做“取前N条”？](../chapters/13.html#agent-practice-context)
* [异步摘要生成期间又来了工具结果，怎样不丢数据？](../chapters/14.html#agent-practice-compaction)
* [规则文件加载与子Agent继承，为什么不能只说“自动继承”？](../chapters/12.html#agent-practice-rules)
* [渐进加载的Skill怎样从“文件”变成实际能力？](../chapters/19.html#agent-practice-skills)
* [记忆写入为什么是一条带租约与验收的流水线？](../chapters/18.html#agent-practice-memory)
* [相关不等于可用：从召回到证据闭合](../chapters/16.html#agent-practice-retrieval)
* [代码证据为什么需要工作树版本，而不只是commit？](../chapters/17.html#agent-practice-code)
* [多Agent怎样并行，又怎样避免交接损失？](../chapters/20.html#agent-practice-delegation)
* [长期任务如何避免每次重新开始或虚假完成？](../chapters/22.html#agent-practice-quality)
* [pass@k、pass^k和一次成功率为什么不能混用？](../chapters/23.html#agent-practice-eval)
* [读到一条“指令”，为什么不代表它有权限？](../chapters/24.html#agent-practice-security)
* [用一条Trace算清等待、用量和失败成本](../chapters/25.html#agent-practice-production)
* [优化先定位瓶颈，不能只追求更少Token](../chapters/26.html#agent-practice-optimization)
* [开源Codex与Claude工程文章怎样对照，才不制造冲突？](../chapters/12.html#agent-practice-products)
* [界面看对了，为什么动作仍然可能点错？](../chapters/27.html#agent-practice-multimodal)
* [研究型Agent怎样避免“搜了很多，却没有形成结论”？](../chapters/26.html#agent-practice-research)
* [索引构建时，哪些元数据一旦丢失就很难补回来？](../chapters/15.html#agent-practice-indexing)
* [怎样把知识图谱变成工程判断，而不是概念大全？](../chapters/28.html#agent-practice-synthesis)

## 带证据等级的知识关系

| 起点 | 关系 | 终点 | 等级与依据 |
| --- | --- | --- | --- |
| 用户目标 | 约束并提供任务 | 模型请求 | source\_observation [[C01]](#source-C01) [[A01]](#source-A01) |
| 请求快照 | 绑定本次声明与分派 | 工具路由器 | source\_observation [[C02]](#source-C02) [[C03]](#source-C03) |
| 工具注册 | 不等价 | 模型可见性 | source\_observation [[C03]](#source-C03) |
| 模型可见性 | 不等价 | 执行授权 | source\_observation [[C09]](#source-C09) [[D05]](#source-D05) |
| 完成工具项 | 先记录 | 会话历史 | source\_observation [[C05]](#source-C05) |
| 完成工具项 | 校验后准入 | 工具执行 | source\_observation [[C05]](#source-C05) [[C09]](#source-C09) |
| 工具执行 | 可能改变 | 外部副作用 | source\_observation [[C09]](#source-C09) |
| 后置钩子 | 不能自动回滚 | 外部副作用 | source\_observation [[C09]](#source-C09) |
| 并行任务 | 执行与结果消费属于不同阶段 | 有序收集 | source\_observation [[C04]](#source-C04) [[C01]](#source-C01) |
| 取消请求 | 不证明从未发生 | 外部副作用 | source\_observation [[C04]](#source-C04) |
| 摘要候选 | 依赖版本 | 历史快照 | source\_observation [[C06]](#source-C06) [[C08]](#source-C08) |
| 摘要安装 | 需要保留或拒绝候选 | 实时后缀 | source\_observation [[C07]](#source-C07) [[C16]](#source-C16) |
| 授权代际 | 变化可使候选失效 | 摘要候选 | source\_observation [[C06]](#source-C06) |
| 记忆候选 | 经筛选进入 | 整合工作者 | source\_observation [[C14]](#source-C14) [[C15]](#source-C15) |
| 租约所有者 | 条件验证 | 记忆发布 | source\_observation [[C15]](#source-C15) |
| 工作者完成 | 并不等价 | 记忆发布 | source\_observation [[C15]](#source-C15) |
| 子Agent消息提交 | 并不等价 | 子任务完成 | source\_observation [[C11]](#source-C11) |
| 技能文件 | 需要发现选择加载与执行 | 实际应用 | source\_observation [[C01]](#source-C01) [[A05]](#source-A05) |
| 文档块 | 需版本条件与覆盖核验 | 回答主张 | engineering\_inference [[A08]](#source-A08) [[A02]](#source-A02) |
| 工作树版本 | 决定验证对象 | 测试结果 | engineering\_inference [[A06]](#source-A06) [[D07]](#source-D07) |
| 任务结果 | 依赖判分口径 | 评测指标 | engineering\_inference [[A07]](#source-A07) |
| 环境噪声 | 可能造成混淆 | 评测差异 | engineering\_inference [[A12]](#source-A12) |
| 失败与废弃工作 | 仍应计入 | 任务成本 | source\_observation [[C06]](#source-C06) [[A14]](#source-A14) |
| Trace | 定位关键路径 | 优化决策 | source\_observation [[C04]](#source-C04) [[A07]](#source-A07) |
| StepContext | 快照访问器仍组合当前授权 | 实时授权 | source\_observation [[C02]](#source-C02) |
| 摘要安装接受 | 不等价 | 持久化成功 | source\_observation [[C16]](#source-C16) |
| Claude后置block | 仍可提供原结果并添加原因 | 原工具结果 | official\_documentation [[D04]](#source-D04) |
| 后置结果替换 | 不自动改写先前记录 | 原始日志 | official\_documentation [[D04]](#source-D04) |
| 技能正文保留 | 寿命不同 | 临时工具许可 | official\_documentation [[D06]](#source-D06) |
| 整合工作者终态 | 还需关停、产物校验及租约确认 | 产物发布 | source\_observation [[C15]](#source-C15) |
| 历史think工具建议 | 2025-12-15更新多数场景改荐后者 | 扩展思考 | dated\_article\_update [[A17]](#source-A17) |
| 增加编排机制 | 须经单项对照，不能假定单调改善 | 任务质量 | engineering\_inference [[A13]](#source-A13) |

## 现有目录中的插入与修订位置

| 页面 | 机制 | 处理 |
| --- | --- | --- |
| [foundations/22.html](../foundations/22.html#agent-foundation-loop) | 一次回答结束，为什么任务仍未完成？ | 保留原例并补证据边界 |
| [foundations/23.html](../foundations/23.html#agent-foundation-stream) | 流式返回：什么时候参数真的可以执行？ | 保留原例并补证据边界 |
| [foundations/24.html](../foundations/24.html#agent-foundation-loop) | 一次回答结束，为什么任务仍未完成？ | 保留原例并补证据边界 |
| [foundations/25.html](../foundations/25.html#agent-foundation-tools) | 工具存在、模型看见、能调用、获授权：四层检查 | 保留原例并补证据边界 |
| [foundations/26.html](../foundations/26.html#agent-foundation-context) | 上下文组装为什么不能只做“取前N条”？ | 保留原例并补证据边界 |
| [foundations/27.html](../foundations/27.html#agent-foundation-compaction) | 异步摘要生成期间又来了工具结果，怎样不丢数据？ | 保留原例并补证据边界 |
| [foundations/28.html](../foundations/28.html#agent-foundation-retrieval) | 相关不等于可用：从召回到证据闭合 | 保留原例并补证据边界 |
| [foundations/29.html](../foundations/29.html#agent-foundation-retrieval) | 相关不等于可用：从召回到证据闭合 | 保留原例并补证据边界 |
| [foundations/30.html](../foundations/30.html#agent-foundation-code) | 代码证据为什么需要工作树版本，而不只是commit？ | 保留原例并补证据边界 |
| [foundations/31.html](../foundations/31.html#agent-foundation-memory) | 记忆写入为什么是一条带租约与验收的流水线？ | 保留原例并补证据边界 |
| [foundations/32.html](../foundations/32.html#agent-foundation-skills) | 渐进加载的Skill怎样从“文件”变成实际能力？ | 保留原例并补证据边界 |
| [foundations/33.html](../foundations/33.html#agent-foundation-recovery) | 成功写入但没有确认：重试怎样变成重复副作用 | 保留原例并补证据边界 |
| [foundations/34.html](../foundations/34.html#agent-foundation-quality) | 长期任务如何避免每次重新开始或虚假完成？ | 保留原例并补证据边界 |
| [foundations/35.html](../foundations/35.html#agent-foundation-eval) | pass@k、pass^k和一次成功率为什么不能混用？ | 保留原例并补证据边界 |
| [foundations/36.html](../foundations/36.html#agent-foundation-eval) | pass@k、pass^k和一次成功率为什么不能混用？ | 保留原例并补证据边界 |
| [foundations/37.html](../foundations/37.html#agent-foundation-security) | 读到一条“指令”，为什么不代表它有权限？ | 保留原例并补证据边界 |
| [foundations/38.html](../foundations/38.html#agent-foundation-production) | 用一条Trace算清等待、用量和失败成本 | 保留原例并补证据边界 |
| [foundations/39.html](../foundations/39.html#agent-foundation-multimodal) | 界面看对了，为什么动作仍然可能点错？ | 保留原例并补证据边界 |
| [foundations/40.html](../foundations/40.html#agent-foundation-research) | 研究型Agent怎样避免“搜了很多，却没有形成结论”？ | 保留原例并补证据边界 |
| [chapters/09.html](../chapters/09.html#agent-practice-loop) | 一次回答结束，为什么任务仍未完成？ | 核验后更新完整机制 |
| [chapters/09.html](../chapters/09.html#agent-practice-snapshot) | 为什么每次模型调用都需要一致的上下文快照？ | 核验后更新完整机制 |
| [chapters/10.html](../chapters/10.html#agent-practice-stream) | 流式返回：什么时候参数真的可以执行？ | 核验后更新完整机制 |
| [chapters/11.html](../chapters/11.html#agent-practice-tools) | 工具存在、模型看见、能调用、获授权：四层检查 | 核验后更新完整机制 |
| [chapters/10.html](../chapters/10.html#agent-practice-hooks) | 前置检查、后置检查为什么不能互相替代？ | 核验后更新完整机制 |
| [chapters/20.html](../chapters/20.html#agent-practice-parallel) | 并行工具为什么可能先执行完、后显示结果？ | 核验后更新完整机制 |
| [chapters/21.html](../chapters/21.html#agent-practice-recovery) | 成功写入但没有确认：重试怎样变成重复副作用 | 核验后更新完整机制 |
| [chapters/13.html](../chapters/13.html#agent-practice-context) | 上下文组装为什么不能只做“取前N条”？ | 核验后更新完整机制 |
| [chapters/14.html](../chapters/14.html#agent-practice-compaction) | 异步摘要生成期间又来了工具结果，怎样不丢数据？ | 核验后更新完整机制 |
| [chapters/12.html](../chapters/12.html#agent-practice-rules) | 规则文件加载与子Agent继承，为什么不能只说“自动继承”？ | 核验后更新完整机制 |
| [chapters/19.html](../chapters/19.html#agent-practice-skills) | 渐进加载的Skill怎样从“文件”变成实际能力？ | 核验后更新完整机制 |
| [chapters/18.html](../chapters/18.html#agent-practice-memory) | 记忆写入为什么是一条带租约与验收的流水线？ | 核验后更新完整机制 |
| [chapters/16.html](../chapters/16.html#agent-practice-retrieval) | 相关不等于可用：从召回到证据闭合 | 核验后更新完整机制 |
| [chapters/15.html](../chapters/15.html#agent-practice-indexing) | 索引构建时，哪些元数据一旦丢失就很难补回来？ | 核验后更新完整机制 |
| [chapters/17.html](../chapters/17.html#agent-practice-code) | 代码证据为什么需要工作树版本，而不只是commit？ | 核验后更新完整机制 |
| [chapters/20.html](../chapters/20.html#agent-practice-delegation) | 多Agent怎样并行，又怎样避免交接损失？ | 核验后更新完整机制 |
| [chapters/22.html](../chapters/22.html#agent-practice-quality) | 长期任务如何避免每次重新开始或虚假完成？ | 核验后更新完整机制 |
| [chapters/23.html](../chapters/23.html#agent-practice-eval) | pass@k、pass^k和一次成功率为什么不能混用？ | 核验后更新完整机制 |
| [chapters/24.html](../chapters/24.html#agent-practice-security) | 读到一条“指令”，为什么不代表它有权限？ | 核验后更新完整机制 |
| [chapters/25.html](../chapters/25.html#agent-practice-production) | 用一条Trace算清等待、用量和失败成本 | 核验后更新完整机制 |
| [chapters/26.html](../chapters/26.html#agent-practice-optimization) | 优化先定位瓶颈，不能只追求更少Token | 核验后更新完整机制 |
| [chapters/12.html](../chapters/12.html#agent-practice-products) | 开源Codex与Claude工程文章怎样对照，才不制造冲突？ | 核验后更新完整机制 |
| [chapters/27.html](../chapters/27.html#agent-practice-multimodal) | 界面看对了，为什么动作仍然可能点错？ | 核验后更新完整机制 |
| [chapters/26.html](../chapters/26.html#agent-practice-research) | 研究型Agent怎样避免“搜了很多，却没有形成结论”？ | 核验后更新完整机制 |
| [chapters/28.html](../chapters/28.html#agent-practice-synthesis) | 怎样把知识图谱变成工程判断，而不是概念大全？ | 核验后更新完整机制 |
| [studies/chapters/07.html](../studies/chapters/07.html#agent-study-stream) | 流式返回：什么时候参数真的可以执行？ | 保留原例并补证据边界 |
| [studies/chapters/08.html](../studies/chapters/08.html#agent-study-recovery) | 成功写入但没有确认：重试怎样变成重复副作用 | 保留原例并补证据边界 |
| [studies/chapters/08.html](../studies/chapters/08.html#agent-study-hooks) | 前置检查、后置检查为什么不能互相替代？ | 保留原例并补证据边界 |
| [studies/chapters/09.html](../studies/chapters/09.html#agent-study-snapshot) | 为什么每次模型调用都需要一致的上下文快照？ | 保留原例并补证据边界 |
| [studies/chapters/09.html](../studies/chapters/09.html#agent-study-compaction) | 异步摘要生成期间又来了工具结果，怎样不丢数据？ | 保留原例并补证据边界 |
| [studies/chapters/10.html](../studies/chapters/10.html#agent-study-products) | 开源Codex与Claude工程文章怎样对照，才不制造冲突？ | 保留原例并补证据边界 |
| [studies/chapters/10.html](../studies/chapters/10.html#agent-study-rules) | 规则文件加载与子Agent继承，为什么不能只说“自动继承”？ | 保留原例并补证据边界 |
| [studies/chapters/11.html](../studies/chapters/11.html#agent-study-context) | 上下文组装为什么不能只做“取前N条”？ | 保留原例并补证据边界 |
| [studies/chapters/12.html](../studies/chapters/12.html#agent-study-compaction) | 异步摘要生成期间又来了工具结果，怎样不丢数据？ | 保留原例并补证据边界 |
| [studies/chapters/13.html](../studies/chapters/13.html#agent-study-retrieval) | 相关不等于可用：从召回到证据闭合 | 保留原例并补证据边界 |
| [studies/chapters/13.html](../studies/chapters/13.html#agent-study-indexing) | 索引构建时，哪些元数据一旦丢失就很难补回来？ | 保留原例并补证据边界 |
| [studies/chapters/14.html](../studies/chapters/14.html#agent-study-code) | 代码证据为什么需要工作树版本，而不只是commit？ | 保留原例并补证据边界 |
| [studies/chapters/15.html](../studies/chapters/15.html#agent-study-memory) | 记忆写入为什么是一条带租约与验收的流水线？ | 保留原例并补证据边界 |
| [studies/chapters/16.html](../studies/chapters/16.html#agent-study-skills) | 渐进加载的Skill怎样从“文件”变成实际能力？ | 保留原例并补证据边界 |
| [studies/chapters/16.html](../studies/chapters/16.html#agent-study-tools) | 工具存在、模型看见、能调用、获授权：四层检查 | 保留原例并补证据边界 |
| [studies/chapters/17.html](../studies/chapters/17.html#agent-study-delegation) | 多Agent怎样并行，又怎样避免交接损失？ | 保留原例并补证据边界 |
| [studies/chapters/17.html](../studies/chapters/17.html#agent-study-parallel) | 并行工具为什么可能先执行完、后显示结果？ | 保留原例并补证据边界 |
| [studies/chapters/18.html](../studies/chapters/18.html#agent-study-quality) | 长期任务如何避免每次重新开始或虚假完成？ | 保留原例并补证据边界 |
| [studies/chapters/19.html](../studies/chapters/19.html#agent-study-eval) | pass@k、pass^k和一次成功率为什么不能混用？ | 保留原例并补证据边界 |
| [studies/chapters/20.html](../studies/chapters/20.html#agent-study-security) | 读到一条“指令”，为什么不代表它有权限？ | 保留原例并补证据边界 |
| [studies/chapters/21.html](../studies/chapters/21.html#agent-study-production) | 用一条Trace算清等待、用量和失败成本 | 保留原例并补证据边界 |
| [studies/chapters/22.html](../studies/chapters/22.html#agent-study-optimization) | 优化先定位瓶颈，不能只追求更少Token | 保留原例并补证据边界 |
| [studies/chapters/24.html](../studies/chapters/24.html#agent-study-multimodal) | 界面看对了，为什么动作仍然可能点错？ | 保留原例并补证据边界 |
| [studies/chapters/25.html](../studies/chapters/25.html#agent-study-research) | 研究型Agent怎样避免“搜了很多，却没有形成结论”？ | 保留原例并补证据边界 |
| [studies/chapters/26.html](../studies/chapters/26.html#agent-study-synthesis) | 怎样把知识图谱变成工程判断，而不是概念大全？ | 保留原例并补证据边界 |
| [studies/chapters/27.html](../studies/chapters/27.html#agent-study-code) | 代码证据为什么需要工作树版本，而不只是commit？ | 保留原例并补证据边界 |
| [studies/chapters/27.html](../studies/chapters/27.html#agent-study-recovery) | 成功写入但没有确认：重试怎样变成重复副作用 | 保留原例并补证据边界 |
| [studies/chapters/28.html](../studies/chapters/28.html#agent-study-quality) | 长期任务如何避免每次重新开始或虚假完成？ | 保留原例并补证据边界 |
| [studies/chapters/29.html](../studies/chapters/29.html#agent-study-recovery) | 成功写入但没有确认：重试怎样变成重复副作用 | 保留原例并补证据边界 |
| [studies/chapters/29.html](../studies/chapters/29.html#agent-study-snapshot) | 为什么每次模型调用都需要一致的上下文快照？ | 保留原例并补证据边界 |
| [studies/chapters/30.html](../studies/chapters/30.html#agent-study-eval) | pass@k、pass^k和一次成功率为什么不能混用？ | 保留原例并补证据边界 |
| [studies/chapters/30.html](../studies/chapters/30.html#agent-study-synthesis) | 怎样把知识图谱变成工程判断，而不是概念大全？ | 保留原例并补证据边界 |
| [reading-notes/chapter-00.html](../reading-notes/chapter-00.html#agent-reading-loop) | 一次回答结束，为什么任务仍未完成？ | 保留原例并补证据边界 |
| [reading-notes/chapter-04.html](../reading-notes/chapter-04.html#agent-reading-stream) | 流式返回：什么时候参数真的可以执行？ | 保留原例并补证据边界 |
| [reading-notes/chapter-04.html](../reading-notes/chapter-04.html#agent-reading-tools) | 工具存在、模型看见、能调用、获授权：四层检查 | 保留原例并补证据边界 |
| [reading-notes/chapter-05.html](../reading-notes/chapter-05.html#agent-reading-loop) | 一次回答结束，为什么任务仍未完成？ | 保留原例并补证据边界 |
| [reading-notes/chapter-05.html](../reading-notes/chapter-05.html#agent-reading-recovery) | 成功写入但没有确认：重试怎样变成重复副作用 | 保留原例并补证据边界 |
| [reading-notes/chapter-06.html](../reading-notes/chapter-06.html#agent-reading-products) | 开源Codex与Claude工程文章怎样对照，才不制造冲突？ | 保留原例并补证据边界 |
| [reading-notes/chapter-06.html](../reading-notes/chapter-06.html#agent-reading-rules) | 规则文件加载与子Agent继承，为什么不能只说“自动继承”？ | 保留原例并补证据边界 |
| [reading-notes/chapter-07.html](../reading-notes/chapter-07.html#agent-reading-context) | 上下文组装为什么不能只做“取前N条”？ | 保留原例并补证据边界 |
| [reading-notes/chapter-07.html](../reading-notes/chapter-07.html#agent-reading-compaction) | 异步摘要生成期间又来了工具结果，怎样不丢数据？ | 保留原例并补证据边界 |
| [reading-notes/chapter-08.html](../reading-notes/chapter-08.html#agent-reading-indexing) | 索引构建时，哪些元数据一旦丢失就很难补回来？ | 保留原例并补证据边界 |
| [reading-notes/chapter-08.html](../reading-notes/chapter-08.html#agent-reading-retrieval) | 相关不等于可用：从召回到证据闭合 | 保留原例并补证据边界 |
| [reading-notes/chapter-08.html](../reading-notes/chapter-08.html#agent-reading-code) | 代码证据为什么需要工作树版本，而不只是commit？ | 保留原例并补证据边界 |
| [reading-notes/chapter-09.html](../reading-notes/chapter-09.html#agent-reading-memory) | 记忆写入为什么是一条带租约与验收的流水线？ | 保留原例并补证据边界 |
| [reading-notes/chapter-10.html](../reading-notes/chapter-10.html#agent-reading-skills) | 渐进加载的Skill怎样从“文件”变成实际能力？ | 保留原例并补证据边界 |
| [reading-notes/chapter-10.html](../reading-notes/chapter-10.html#agent-reading-delegation) | 多Agent怎样并行，又怎样避免交接损失？ | 保留原例并补证据边界 |
| [reading-notes/chapter-11.html](../reading-notes/chapter-11.html#agent-reading-quality) | 长期任务如何避免每次重新开始或虚假完成？ | 保留原例并补证据边界 |
| [reading-notes/chapter-12.html](../reading-notes/chapter-12.html#agent-reading-eval) | pass@k、pass^k和一次成功率为什么不能混用？ | 保留原例并补证据边界 |
| [reading-notes/chapter-13.html](../reading-notes/chapter-13.html#agent-reading-security) | 读到一条“指令”，为什么不代表它有权限？ | 保留原例并补证据边界 |
| [reading-notes/chapter-14.html](../reading-notes/chapter-14.html#agent-reading-production) | 用一条Trace算清等待、用量和失败成本 | 保留原例并补证据边界 |
| [reading-notes/chapter-14.html](../reading-notes/chapter-14.html#agent-reading-optimization) | 优化先定位瓶颈，不能只追求更少Token | 保留原例并补证据边界 |
| [reading-notes/chapter-15.html](../reading-notes/chapter-15.html#agent-reading-multimodal) | 界面看对了，为什么动作仍然可能点错？ | 保留原例并补证据边界 |
| [reading-notes/chapter-15.html](../reading-notes/chapter-15.html#agent-reading-synthesis) | 怎样把知识图谱变成工程判断，而不是概念大全？ | 保留原例并补证据边界 |
| [reading-notes/guide-04.html](../reading-notes/guide-04.html#agent-guide-loop) | 一次回答结束，为什么任务仍未完成？ | 保留原例并补证据边界 |
| [reading-notes/guide-05.html](../reading-notes/guide-05.html#agent-guide-snapshot) | 为什么每次模型调用都需要一致的上下文快照？ | 保留原例并补证据边界 |
| [reading-notes/guide-06.html](../reading-notes/guide-06.html#agent-guide-products) | 开源Codex与Claude工程文章怎样对照，才不制造冲突？ | 保留原例并补证据边界 |
| [reading-notes/guide-07.html](../reading-notes/guide-07.html#agent-guide-context) | 上下文组装为什么不能只做“取前N条”？ | 保留原例并补证据边界 |
| [reading-notes/guide-08.html](../reading-notes/guide-08.html#agent-guide-compaction) | 异步摘要生成期间又来了工具结果，怎样不丢数据？ | 保留原例并补证据边界 |
| [reading-notes/guide-09.html](../reading-notes/guide-09.html#agent-guide-retrieval) | 相关不等于可用：从召回到证据闭合 | 保留原例并补证据边界 |
| [reading-notes/guide-10.html](../reading-notes/guide-10.html#agent-guide-memory) | 记忆写入为什么是一条带租约与验收的流水线？ | 保留原例并补证据边界 |
| [reading-notes/guide-11.html](../reading-notes/guide-11.html#agent-guide-quality) | 长期任务如何避免每次重新开始或虚假完成？ | 保留原例并补证据边界 |
| [reading-notes/guide-12.html](../reading-notes/guide-12.html#agent-guide-eval) | pass@k、pass^k和一次成功率为什么不能混用？ | 保留原例并补证据边界 |
| [walkthroughs/b.html](../walkthroughs/b.html#agent-walkthrough-stream) | 流式返回：什么时候参数真的可以执行？ | 保留原例并补证据边界 |
| [walkthroughs/b.html](../walkthroughs/b.html#agent-walkthrough-hooks) | 前置检查、后置检查为什么不能互相替代？ | 保留原例并补证据边界 |
| [walkthroughs/b.html](../walkthroughs/b.html#agent-walkthrough-recovery) | 成功写入但没有确认：重试怎样变成重复副作用 | 保留原例并补证据边界 |
| [walkthroughs/b.html](../walkthroughs/b.html#agent-walkthrough-code) | 代码证据为什么需要工作树版本，而不只是commit？ | 保留原例并补证据边界 |
| [walkthroughs/c.html](../walkthroughs/c.html#agent-walkthrough-indexing) | 索引构建时，哪些元数据一旦丢失就很难补回来？ | 保留原例并补证据边界 |
| [walkthroughs/c.html](../walkthroughs/c.html#agent-walkthrough-retrieval) | 相关不等于可用：从召回到证据闭合 | 保留原例并补证据边界 |
| [walkthroughs/c.html](../walkthroughs/c.html#agent-walkthrough-memory) | 记忆写入为什么是一条带租约与验收的流水线？ | 保留原例并补证据边界 |
| [walkthroughs/d.html](../walkthroughs/d.html#agent-walkthrough-snapshot) | 为什么每次模型调用都需要一致的上下文快照？ | 保留原例并补证据边界 |
| [walkthroughs/d.html](../walkthroughs/d.html#agent-walkthrough-eval) | pass@k、pass^k和一次成功率为什么不能混用？ | 保留原例并补证据边界 |
| [walkthroughs/d.html](../walkthroughs/d.html#agent-walkthrough-production) | 用一条Trace算清等待、用量和失败成本 | 保留原例并补证据边界 |

## 逐项来源与阅读结果

### C01 · 采样循环、请求组装、工具收集与停止

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/session/turn.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C01.md)

**已取得范围：**`[[1, 250], [400, 1000], [1000, 1350], [1600, 1900]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`32fdf7bd27d02e3b04b26174034f5210fe94c9ce`。

先沿run\_turn识别接收输入、构造StepContext、请求模型、回填工具和停止钩子的边界，再读build\_prompt与显式Skills加载。增量工具模式会让本次tools/base\_instructions字段为空，不能仅看该字段就断言规则未提供。停止钩子没有继续输入时会警告而非无限续跑；内部记忆整合另有拒绝路径。

**选取的原码摘录：**不是完整文件，不具备独立可编译性；全文blob值仅用于标识来源，不冒称已对摘录完成整文件哈希验证。

```
pub(crate) fn build_prompt(
    input: Vec<ResponseItem>,
    step_context: &StepContext,
    base_instructions: BaseInstructions,
    incremental_tools: bool,
) -> Prompt {
    let turn_context = &step_context.turn;
    Prompt {
        input,
        tools: if incremental_tools {
            Arc::default()
        } else {
            step_context.tool_router.model_visible_specs()
        },
        parallel_tool_calls: true,
        base_instructions: if incremental_tools {
            BaseInstructions {
                text: String::new(),
                provenance: None,
            }
        } else {
            base_instructions
        },
        output_schema: turn_context.final_output_json_schema.clone(),
        output_schema_strict: !crate::guardian::is_basic_session_source(
            &turn_context.session_source,
        ),
        cyber_access_program: turn_context.cyber_access_program,
    }
}
```

### C02 · 请求级设置、环境、规则与工具快照

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/session/step_context.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C02.md)

**已取得范围：**`[[1, 90]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`ac96683d40352cf7ac96595a7e057aa5a0184077`。

StepContext绑定发出本次请求所用的模型设置、MCP、环境和工具路由；文件系统访问器仍结合实时会话/本轮授权。快照一致性不等于所有权限永久冻结。

**完整文件已保存，Git blob校验一致。**以下原代码可离线核对，未作为独立模块执行。

```
//! Request-scoped settings and capabilities, with live grants bound to the originating turn.

use std::sync::Arc;

use crate::agents_md::LoadedAgentsMd;
use crate::config::TokenBudgetConfig;
use crate::environment_selection::TurnEnvironmentSnapshot;
use crate::realtime_conversation::RealtimeConversationSnapshot;
use crate::session::step_settings::ResolvedStepSettings;
use crate::session::turn_context::TurnContext;
use crate::session::turn_context::TurnEnvironment;
use crate::tools::router::ToolRouter;
use codex_extension_api::ExtensionData;
use codex_file_system::EnvironmentAccess;
use codex_mcp::McpBinding;
use codex_otel::SessionTelemetry;
use codex_plugin::ExecutorPluginHookSource;
use codex_protocol::items::ModelInvocationContext;
use codex_protocol::protocol::TurnContextItem;
use tokio_util::sync::CancellationToken;

/// Request-scoped state that may change between model sampling requests.
pub(crate) struct StepContext {
    pub(crate) turn: Arc<TurnContext>,
    /// Preempts this request and yields its code-mode observations when user input arrives.
    pub(crate) preempt: Option<CancellationToken>,
    /// Realtime call activity and instructions captured for this sampling request.
    pub(crate) realtime: RealtimeConversationSnapshot,
    /// One immutable settings version captured before request preparation.
    pub(crate) settings: Arc<ResolvedStepSettings>,
    /// Frozen turn preferences resolved against this step's captured model.
    pub(crate) token_budget: Option<TokenBudgetConfig>,
    /// Telemetry context tagged with this sampling request's model.
    pub(crate) session_telemetry: SessionTelemetry,
    pub(crate) environments: TurnEnvironmentSnapshot,
    /// Child bindings captured with this step; configured-only when opted in.
    pub(crate) inherited_environments: TurnEnvironmentSnapshot,
    /// Admitted executor hooks bound to this step's discovery, plugin policy, and MCP routing.
    pub(crate) executor_hook_sources: Vec<ExecutorPluginHookSource>,
    /// Keeps the extension inputs used to build this step's tools for its World State as well.
    pub(crate) extension_data: ExtensionData,
    /// The exact MCP connections, configuration, and catalog captured for this step.
    pub(crate) mcp: Arc<McpBinding>,
    /// The finalized tool plan advertised and executed for this exact sampling request.
    pub(crate) tool_router: Arc<ToolRouter>,
    /// The canonical AGENTS.md value observed with this environment snapshot.
    pub(crate) loaded_agents_md: Option<Arc<LoadedAgentsMd>>,
}

impl StepContext {
    /// Whether new context windows should record tool declarations in history.
    pub(crate) fn incremental_tools_enabled(&self) -> bool {
        self.settings.model_info.use_responses_lite
            && self
                .turn
                .config
                .features
                .enabled(codex_features::Feature::IncrementalTools)
    }

    /// Pairs the step's environments with access using current session and originating-turn grants.
    pub(crate) fn environments(&self) -> Vec<(&TurnEnvironment, impl EnvironmentAccess + '_)> {
        self.environments
            .turn_environments()
            .map(|environment| {
                let grants = self
                    .turn
                    .granted_permissions(&environment.selection.environment_id);
                (environment, environment.fs_accessor(grants))
            })
            .collect()
    }

    /// Persist the context captured for this request, even after a live update.
    pub(crate) fn to_turn_context_item(&self) -> TurnContextItem {
        let mut item = self.turn.to_turn_context_item();
        item.realtime_active = Some(self.realtime.active);
        item
    }

    pub(crate) fn model_context(&self) -> ModelInvocationContext {
        ModelInvocationContext {
            model_slug: self.settings.model_info.slug.clone(),
            reasoning_effort: self
                .settings
                .effective_reasoning_effort()
                .map(|effort| effort.to_string()),
        }
    }
}
```

### C03 · 工具可见性、调用转换与路由

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/tools/router.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C03.md)

**已取得范围：**`[[1, 449]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`3c01ab98187227561c3a4220ed8277b7317f21ce`。

工具注册、直接暴露、延迟发现与Code Mode是不同表面。exposes\_tool覆盖多条路径；build\_tool\_call区分本地与托管搜索，分派携带call\_id和原StepContext。注册指标不证明可见或可执行。

**完整文件已保存，Git blob校验一致。**以下原代码可离线核对，未作为独立模块执行。

```
use crate::function_tool::FunctionCallError;
use crate::responses_metadata::TurnToolNamespacesInfo;
use crate::session::session::Session;
use crate::session::step_context::StepContext;
#[cfg(test)]
use crate::session::turn_context::TurnContext;
use crate::tools::context::SharedTurnDiffTracker;
use crate::tools::context::ToolCallState;
use crate::tools::context::ToolInvocation;
use crate::tools::context::ToolPayload;
#[cfg(test)]
use crate::tools::handlers::ToolSearchHandlerCache;
use crate::tools::registry::AnyToolResult;
use crate::tools::registry::RegisteredTool;
use crate::tools::registry::ToolArgumentDiffConsumer;
use crate::tools::registry::ToolExposure;
use crate::tools::registry::ToolRegistry;
#[cfg(test)]
use crate::tools::spec_plan::finalize_tool_router;
use codex_otel::SessionTelemetry;
use codex_otel::TOOL_REGISTRATIONS_METRIC;
use codex_otel::TOOL_REGISTRATIONS_METRIC_BUCKETS;
use codex_protocol::models::ResponseItem;
use codex_protocol::models::SearchToolCallParams;
#[cfg(test)]
use codex_protocol::openai_models::ModelInfo;
use codex_protocol::openai_models::ToolMode;
use codex_tools::DiscoverableTool;
use codex_tools::ResponsesApiNamespaceTool;
use codex_tools::ToolName;
use codex_tools::ToolSpec;
use std::borrow::Cow;
use std::collections::BTreeMap;
use std::sync::Arc;
use tokio_util::sync::CancellationToken;
use tracing::instrument;

pub use crate::tools::context::ToolCallSource;

const EXPOSURE_DIRECT: &str = "direct";
const EXPOSURE_DIRECT_MODEL_ONLY: &str = "direct_model_only";
const EXPOSURE_DEFERRED: &str = "deferred";
const EXPOSURE_DEFERRED_MODEL_ONLY: &str = "deferred_model_only";
const EXPOSURE_CODE_MODE_ONLY: &str = "code_mode_only";
const EXPOSURE_HIDDEN: &str = "hidden";

#[derive(Clone, Debug, PartialEq)]
pub struct ToolCall {
    pub tool_name: ToolName,
    pub call_id: String,
    pub payload: ToolPayload,
    pub encrypted_function_args: Option<Vec<String>>,
}

impl ToolCall {
    pub(crate) fn direct_source(&self) -> ToolCallSource {
        if self.tool_name.namespace.as_deref() == Some("collaboration")
            && matches!(
                self.tool_name.name.as_str(),
                "spawn_agent" | "send_message" | "followup_task"
            )
            && self
                .encrypted_function_args
                .as_ref()
                .is_some_and(Vec::is_empty)
        {
            ToolCallSource::DirectPlaintextMessage
        } else {
            ToolCallSource::Direct
        }
    }
}

pub(crate) fn tool_log_payload<'a>(
    payload: &'a ToolPayload,
    source: &ToolCallSource,
) -> Cow<'a, str> {
    if matches!(source, ToolCallSource::DirectPlaintextMessage) {
        return Cow::Borrowed("[plaintext arguments]");
    }
    payload.log_payload()
}

/// One finalized tool plan: its advertised surfaces and matching executable runtimes.
pub struct ToolRouter {
    registry: ToolRegistry,
    model_visible_specs: Arc<[ToolSpec]>,
    tool_mode: ToolMode,
    code_mode_tool_names: BTreeMap<String, ToolName>,
    tool_namespaces_info: Option<TurnToolNamespacesInfo>,
    can_manage_children: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum ToolSuggestPresentation {
    ListTool,
    RecommendationContext,
}

#[derive(Clone, Debug)]
pub(crate) struct ToolSuggestCandidates {
    pub(crate) tools: Vec<DiscoverableTool>,
    pub(crate) presentation: ToolSuggestPresentation,
}

impl ToolRouter {
    #[cfg(test)]
    pub(crate) fn from_registry(
        turn_context: &TurnContext,
        model_info: &ModelInfo,
        registry: ToolRegistry,
        hosted_specs: Vec<ToolSpec>,
        tool_search_handler_cache: &ToolSearchHandlerCache,
    ) -> Self {
        finalize_tool_router(
            turn_context,
            model_info,
            registry,
            hosted_specs,
            tool_search_handler_cache,
        )
        .expect("test tool registry should not contain duplicate tools")
    }

    pub(crate) fn from_parts(
        registry: ToolRegistry,
        model_visible_specs: Vec<ToolSpec>,
        tool_mode: ToolMode,
        code_mode_tool_names: BTreeMap<String, ToolName>,
        tool_namespaces_info: Option<TurnToolNamespacesInfo>,
        child_management_tools: &[ToolName],
    ) -> Self {
        let mut router = Self {
            registry,
            model_visible_specs: model_visible_specs.into(),
            tool_mode,
            code_mode_tool_names,
            tool_namespaces_info,
            can_manage_children: false,
        };
        router.can_manage_children = !child_management_tools.is_empty()
            && child_management_tools
                .iter()
                .all(|name| router.exposes_tool(name));
        router
    }

    pub(crate) fn model_visible_specs(&self) -> Arc<[ToolSpec]> {
        Arc::clone(&self.model_visible_specs)
    }

    pub(crate) fn tool_mode(&self) -> ToolMode {
        self.tool_mode
    }

    /// Code Mode still needs its dispatcher when the nested tool set is empty.
    pub(crate) fn requires_code_mode_worker(&self) -> bool {
        matches!(self.tool_mode, ToolMode::CodeMode | ToolMode::CodeModeOnly)
    }

    /// The normalized nested identities chosen after exclusions and collisions.
    pub(crate) fn code_mode_tool_names(&self) -> &BTreeMap<String, ToolName> {
        &self.code_mode_tool_names
    }

    /// Optional request inventory for this exact plan, without publishing it to turn state.
    pub(crate) fn tool_namespaces_info(&self) -> Option<&TurnToolNamespacesInfo> {
        self.tool_namespaces_info.as_ref()
    }

    /// Whether the model can both start and interact with a terminal process.
    #[cfg_attr(not(test), allow(dead_code))]
    pub(crate) fn has_terminal_controls(&self) -> bool {
        self.exposes_tool(&ToolName::plain("exec_command"))
            && self.exposes_tool(&ToolName::plain("write_stdin"))
    }

    /// Whether the configured collaboration backend's child-management tools remain exposed.
    #[cfg_attr(not(test), allow(dead_code))]
    pub(crate) fn can_manage_children(&self) -> bool {
        self.can_manage_children
    }

    // Answers if the tool plan lets the model invoke the tool directly, through code mode, or deferred tool search.
    pub(crate) fn exposes_tool(&self, name: &ToolName) -> bool {
        let name = name.clone().with_default_namespace();
        if self
            .code_mode_tool_names
            .values()
            .any(|nested| nested.clone().with_default_namespace() == name)
            || self.model_visible_specs.iter().any(|spec| match spec {
                ToolSpec::Function(_) | ToolSpec::Freeform(_) => {
                    name.is_default_namespace() && spec.name() == name.name
                }
                ToolSpec::Namespace(namespace) => {
                    name.namespace.as_deref() == Some(namespace.name.as_str())
                        && namespace.tools.iter().any(|tool| match tool {
                            ResponsesApiNamespaceTool::Function(tool) => tool.name == name.name,
                            ResponsesApiNamespaceTool::Custom(tool) => tool.name == name.name,
                        })
                }
                ToolSpec::ToolSearch { .. } | ToolSpec::WebSearch { .. } => false,
            })
        {
            return true;
        }
        self.model_visible_specs
            .iter()
            .any(|spec| matches!(spec, ToolSpec::ToolSearch { .. }))
            && self.registry.entries().any(|tool| {
                tool.exposure.is_deferred()
                    && tool.runtime.tool_name().with_default_namespace() == name
                    && (tool.runtime.immutable_spec().is_some()
                        || tool.runtime.search_info().is_some())
            })
    }

    pub(crate) fn deferred_tool_namespaces(&self) -> BTreeMap<String, String> {
        self.registry.deferred_tool_namespaces()
    }

    pub(crate) fn mcp_namespaces(&self) -> impl Iterator<Item = (&str, &str)> {
        self.registry.mcp_namespaces()
    }

    #[cfg(test)]
    pub(crate) fn registered_tool_names_for_test(&self) -> Vec<ToolName> {
        self.registry.tool_names_for_test()
    }

    #[cfg(test)]
    pub(crate) fn tool_exposure_for_test(
        &self,
        name: &ToolName,
    ) -> Option<crate::tools::registry::ToolExposure> {
        self.registry.tool_exposure(name)
    }

    pub(crate) fn create_diff_consumer(
        &self,
        tool_name: &ToolName,
    ) -> Option<Box<dyn ToolArgumentDiffConsumer>> {
        self.registry.create_diff_consumer(tool_name)
    }

    pub fn tool_supports_parallel(&self, call: &ToolCall) -> bool {
        self.registry
            .supports_parallel_tool_calls(&call.tool_name)
            .unwrap_or(false)
    }

    pub(crate) fn registered_tool(&self, tool_name: &ToolName) -> Option<&RegisteredTool> {
        self.registry.registered_tool(tool_name)
    }

    #[instrument(level = "trace", skip_all, err)]
    pub fn build_tool_call(item: ResponseItem) -> Result<Option<ToolCall>, FunctionCallError> {
        match item {
            ResponseItem::FunctionCall {
                name,
                namespace,
                arguments,
                encrypted_function_args,
                call_id,
                ..
            } => {
                let tool_name = ToolName::new(namespace, name).with_default_namespace();
                Ok(Some(ToolCall {
                    tool_name,
                    call_id,
                    payload: ToolPayload::Function { arguments },
                    encrypted_function_args,
                }))
            }
            ResponseItem::ToolSearchCall {
                call_id: Some(call_id),
                execution,
                arguments,
                ..
            } if execution == "client" => {
                let arguments: SearchToolCallParams =
                    serde_json::from_value(arguments).map_err(|err| {
                        FunctionCallError::RespondToModel(format!(
                            "failed to parse tool_search arguments: {err}"
                        ))
                    })?;
                Ok(Some(ToolCall {
                    tool_name: ToolName::plain("tool_search"),
                    call_id,
                    payload: ToolPayload::ToolSearch { arguments },
                    encrypted_function_args: None,
                }))
            }
            ResponseItem::ToolSearchCall { .. } => Ok(None),
            ResponseItem::CustomToolCall {
                name,
                namespace,
                input,
                call_id,
                ..
            } => Ok(Some(ToolCall {
                tool_name: ToolName::new(namespace, name).with_default_namespace(),
                call_id,
                payload: ToolPayload::Custom { input },
                encrypted_function_args: None,
            })),
            _ => Ok(None),
        }
    }

    #[allow(dead_code)]
    #[instrument(level = "trace", skip_all, err)]
    pub async fn dispatch_tool_call_with_code_mode_result(
        &self,
        session: Arc<Session>,
        step_context: Arc<StepContext>,
        cancellation_token: CancellationToken,
        tracker: SharedTurnDiffTracker,
        call: ToolCall,
        source: ToolCallSource,
    ) -> Result<AnyToolResult, FunctionCallError> {
        self.dispatch_tool_call_with_code_mode_result_inner(
            session,
            step_context,
            cancellation_token,
            tracker,
            call,
            source,
            /*call_state*/ None,
        )
        .await
    }

    #[instrument(level = "trace", skip_all, err)]
    #[allow(clippy::too_many_arguments)]
    pub(crate) async fn dispatch_tool_call_with_state(
        &self,
        session: Arc<Session>,
        step_context: Arc<StepContext>,
        cancellation_token: CancellationToken,
        tracker: SharedTurnDiffTracker,
        call: ToolCall,
        source: ToolCallSource,
        call_state: Arc<ToolCallState>,
    ) -> Result<AnyToolResult, FunctionCallError> {
        self.dispatch_tool_call_with_code_mode_result_inner(
            session,
            step_context,
            cancellation_token,
            tracker,
            call,
            source,
            Some(call_state),
        )
        .await
    }

    #[allow(clippy::too_many_arguments)]
    async fn dispatch_tool_call_with_code_mode_result_inner(
        &self,
        session: Arc<Session>,
        step_context: Arc<StepContext>,
        cancellation_token: CancellationToken,
        tracker: SharedTurnDiffTracker,
        call: ToolCall,
        source: ToolCallSource,
        call_state: Option<Arc<ToolCallState>>,
    ) -> Result<AnyToolResult, FunctionCallError> {
        let ToolCall {
            tool_name,
            call_id,
            payload,
            ..
        } = call;

        // Keep the legacy ToolInvocation.turn field tied to the same request state until handlers migrate.
        let turn = Arc::clone(&step_context.turn);
        let invocation = ToolInvocation {
            session,
            turn,
            step_context,
            cancellation_token,
            tracker,
            call_id,
            tool_name,
            source,
            payload,
        };

        self.registry
            .dispatch_any_with_state(invocation, call_state)
            .await
    }
}

/// Records the registered inventory once per sampling request, before transport retries.
/// Registrations do not imply model visibility or reachability; hosted tools are excluded.
pub(crate) fn record_registration_metrics(
    router: &ToolRouter,
    telemetry: &SessionTelemetry,
    incremental_tools: bool,
) {
    let mut direct = 0usize;
    let mut direct_model_only = 0usize;
    let mut deferred = 0usize;
    let mut deferred_model_only = 0usize;
    let mut code_mode_only = 0usize;
    let mut hidden = 0usize;
    for tool in router.registry.entries() {
        match tool.exposure {
            ToolExposure::Direct => direct += 1,
            ToolExposure::DirectModelOnly => direct_model_only += 1,
            ToolExposure::Deferred => deferred += 1,
            ToolExposure::DeferredModelOnly => deferred_model_only += 1,
            ToolExposure::CodeModeOnly => code_mode_only += 1,
            ToolExposure::Hidden => hidden += 1,
        }
    }

    let tool_mode = match router.tool_mode {
        ToolMode::Direct => "direct",
        ToolMode::CodeMode => "code_mode",
        ToolMode::CodeModeOnly => "code_mode_only",
    };
    let incremental_tools = if incremental_tools { "true" } else { "false" };
    for (exposure, count) in [
        (EXPOSURE_DIRECT, direct),
        (EXPOSURE_DIRECT_MODEL_ONLY, direct_model_only),
        (EXPOSURE_DEFERRED, deferred),
        (EXPOSURE_DEFERRED_MODEL_ONLY, deferred_model_only),
        (EXPOSURE_CODE_MODE_ONLY, code_mode_only),
        (EXPOSURE_HIDDEN, hidden),
    ] {
        telemetry.histogram_with_boundaries(
            TOOL_REGISTRATIONS_METRIC,
            i64::try_from(count).unwrap_or(i64::MAX),
            TOOL_REGISTRATIONS_METRIC_BUCKETS,
            &[
                ("exposure", exposure),
                ("tool_mode", tool_mode),
                ("incremental_tools", incremental_tools),
            ],
        );
    }
}

#[cfg(test)]
#[path = "router_tests.rs"]
mod tests;
```

### C04 · 并行准入、执行、取消与结果

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/tools/parallel.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C04.md)

**已取得范围：**`[[1, 310]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`cc8beb4e3091eaaa0460eead9b05186af71f5513`。

阅读ToolCallRuntime的创建、准入、执行与取消；调用可以立即启动，消费结果的future不代表实际开始时间。并行允许标志只决定调度方式，不证明读写目标彼此独立。

该文件按列出的范围取得并阅读，包内保留原始定位与中文笔记，没有伪造或拼凑全文副本。

### C05 · 输出项记录、分派与回填

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/stream_events_utils.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C05.md)

**已取得范围：**`[[1, 280], [310, 580]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`1b668ea4bb56e5dd22e99e1827bab085b494bc51`。

完整输出项到达后先记录调用，再选择即时或延期分派。已记入历史但还未执行就取消的调用仍需对应中止结果，避免恢复后的孤立调用。工具项完成不等于整次响应或业务任务完成。

**选取的原码摘录：**不是完整文件，不具备独立可编译性；全文blob值仅用于标识来源，不冒称已对摘录完成整文件哈希验证。

```
fn response_item_may_include_external_context(item: &ResponseItem) -> bool {
    matches!(
        item,
        ResponseItem::ToolSearchCall { .. }
            | ResponseItem::ToolSearchOutput { .. }
            | ResponseItem::WebSearchCall { .. }
            | ResponseItem::FunctionCallOutput { call_id: None, .. }
    )
}

pub(crate) async fn mark_thread_memory_mode_polluted_if_external_context(
    sess: &Session,
    turn_context: &TurnContext,
    item: &ResponseItem,
) {
    if !turn_context.config.memories.disable_on_external_context
        || !response_item_may_include_external_context(item)
    {
        return;
    }
    state_db::mark_thread_memory_mode_polluted(
        sess.services.state_db.as_deref(),
        sess.thread_id,
        "record_completed_response_item",
    )
    .await;
}
```

### C06 · 异步压缩生命周期与候选验证

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/session/async_compaction.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C06.md)

**已取得范围：**`[[1, 222]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`a9bba346d829ce0881240a7279a58af3a2d569e6`。

后台压缩受功能标记、TokenBudget禁用和远端V2支持共同约束。启动身份包括历史重写代际、模型与压缩版本、授权代际。取消本轮仅拦新工作，已有工作由会话管理；丢弃结果并不抹掉费用。

**完整文件已保存，Git blob校验一致。**以下原代码可离线核对，未作为独立模块执行。

```
//! Holds the current speculative request, polled at checkpoints or awaited when compaction is due.
//! Discarded requests still charge completed usage; session shutdown cancels remaining network work.

use std::sync::Arc;

use crate::compact_remote_v2::BackgroundCompactionCandidate;
use crate::compact_remote_v2::capture_background_input;
use crate::compact_remote_v2::run_background_compaction;
use crate::context::world_state::WorldState;
use crate::session::context_window::ContextWindowTokenStatus;
use crate::session::session::Session;
use crate::session::step_context::StepContext;
use crate::session::turn_context::TurnContext;
use codex_analytics::CompactionPhase;
use codex_features::Feature;
use codex_model_provider::RemoteCompactionSupport;
use codex_otel::auth_storage::AuthStorageOriginator;
use tokio::sync::oneshot;
use tokio_util::sync::CancellationToken;
use tokio_util::task::TaskTracker;
use tracing::debug;

#[derive(PartialEq, Eq)]
struct CompactionAttempt {
    history_version: u64,
    model_slug: String,
    compaction_hash: Option<String>,
    auth_owner_generation: Option<u64>,
}

#[derive(Default)]
pub(crate) struct AsyncCompactionState {
    last_attempt: Option<CompactionAttempt>,
    // Keep prepared request state off the turn stack while checkpoints await adoption.
    result: Option<oneshot::Receiver<Box<BackgroundCompactionCandidate>>>,
    tasks: TaskTracker,
    shutdown_cancellation: CancellationToken,
}

pub(super) fn enabled(turn_context: &TurnContext) -> bool {
    turn_context
        .config
        .features
        .enabled(Feature::AsyncCompaction)
        && !turn_context.config.features.enabled(Feature::TokenBudget)
        && matches!(
            turn_context.provider.capabilities().remote_compaction,
            RemoteCompactionSupport::V2
        )
}

pub(super) async fn maybe_start(
    sess: &Arc<Session>,
    step_context: &Arc<StepContext>,
    world_state: &Arc<WorldState>,
    phase: CompactionPhase,
    turn_cancellation: &CancellationToken,
    token_status: &ContextWindowTokenStatus,
    (turn_state, auth_owner_generation): (Option<String>, Option<u64>),
) {
    let turn_context = &step_context.turn;
    // Let the foreground establish the backend's model pin before starting a parallel request.
    if matches!(phase, CompactionPhase::PreTurn) && turn_state.is_none() {
        return;
    }
    if !enabled(turn_context)
        || token_status.token_limit_reached
        || (matches!(phase, CompactionPhase::PostTurn)
            && token_status.turn_end_compaction_threshold_reached)
        || step_context
            .settings
            .model_info
            .resolved_context_window()
            .is_none_or(|limit| {
                i128::from(token_status.active_context_tokens) * 100
                    < i128::from(limit)
                        * i128::from(turn_context.config.async_compaction_threshold_percent)
            })
    {
        return;
    }

    let base_instructions = sess.get_prompt_base_instructions().await;
    let mut state = sess.state.lock().await;
    let model_info = &step_context.settings.model_info;
    let attempt = CompactionAttempt {
        history_version: state.history.history_version(),
        model_slug: model_info.slug.clone(),
        compaction_hash: model_info.comp_hash.clone(),
        auth_owner_generation,
    };
    // Stop blocks new launches; already-running compaction remains session-owned.
    if turn_cancellation.is_cancelled()
        || state.shutting_down
        || state.async_compaction.last_attempt.as_ref() == Some(&attempt)
        || state.history.annotated_items().is_empty()
        || sess.services.model_client.auth_owner_generation() != auth_owner_generation
    {
        return;
    }

    // Capture and register without yielding, so shutdown or history replacement cannot
    // overtake this request. Tool attribution still belongs to the foreground's current step.
    let prepared_input = capture_background_input(
        sess,
        step_context,
        state.history.clone(),
        base_instructions,
        turn_state,
        auth_owner_generation,
        sess.current_window_from_state(&state),
    );
    let task_session = Arc::clone(sess);
    let task_step = Arc::clone(step_context);
    let cutoff_world_state = Arc::clone(world_state);
    let storage_originator = AuthStorageOriginator::from_client_name(&turn_context.originator);
    state.async_compaction.last_attempt = Some(attempt);
    let (send, result) = oneshot::channel();
    state.async_compaction.result = Some(result);
    let task = async move {
        match run_background_compaction(
            &task_session,
            task_step,
            cutoff_world_state,
            phase,
            prepared_input,
        )
        .await
        {
            Ok(candidate) => {
                let _ = send.send(Box::new(candidate));
            }
            Err(error) => {
                debug!(%error, "discarding unsuccessful background compaction");
            }
        }
    };
    state
        .async_compaction
        .tasks
        .spawn(storage_originator.scope(task));
}

pub(super) async fn take_ready(
    sess: &Session,
    turn_context: &TurnContext,
) -> Option<Box<BackgroundCompactionCandidate>> {
    if !enabled(turn_context) {
        return None;
    }
    let mut state = sess.state.lock().await;
    let mut result = state.async_compaction.result.take()?;
    let candidate = match result.try_recv() {
        Ok(candidate) => candidate,
        Err(oneshot::error::TryRecvError::Empty) => {
            state.async_compaction.result = Some(result);
            return None;
        }
        // try_recv consumes a closed receiver; awaiting it later would panic.
        Err(oneshot::error::TryRecvError::Closed) => return None,
    };
    (candidate.prefix.generation == state.history.history_version()).then_some(candidate)
}

pub(crate) async fn wait_for_pending(
    sess: &Session,
    step_context: &StepContext,
) -> Option<Box<BackgroundCompactionCandidate>> {
    if !enabled(&step_context.turn) {
        return None;
    }
    let result = {
        let mut state = sess.state.lock().await;
        let result = state.async_compaction.result.take()?;
        let model = &step_context.settings.model_info;
        let attempt = state.async_compaction.last_attempt.as_ref()?;
        if attempt.history_version != state.history.history_version()
            || attempt.model_slug != model.slug
            || attempt.compaction_hash != model.comp_hash
            || attempt.auth_owner_generation != sess.services.model_client.auth_owner_generation()
        {
            return None;
        }
        result
    };
    // Release session state while the request finishes and charges its usage.
    result.await.ok()
}

pub(crate) async fn shutdown_cancellation(sess: &Session) -> CancellationToken {
    sess.state
        .lock()
        .await
        .async_compaction
        .shutdown_cancellation
        .clone()
}

pub(super) async fn shutdown(sess: &Session) {
    let tasks = {
        let mut state = sess.state.lock().await;
        let async_compaction = &mut state.async_compaction;
        async_compaction.result = None;
        async_compaction.tasks.close();
        async_compaction.shutdown_cancellation.cancel();
        async_compaction.tasks.clone()
    };
    // Drain completed usage charging before shutdown finishes.
    tasks.wait().await;
}

/// Test barrier: callers must gate foreground work so it cannot launch another attempt.
pub(crate) async fn wait_for_background_compaction_for_test(sess: &Session) {
    let tasks = sess.state.lock().await.async_compaction.tasks.clone();
    // Closing only enables waiting; it neither cancels tasks nor prevents future launches.
    tasks.close();
    tasks.wait().await;
}

#[cfg(test)]
#[path = "async_compaction_tests.rs"]
mod tests;
```

### C07 · 压缩候选安装及回退

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/compact_remote_v2_installation.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C07.md)

**已取得范围：**`[[1, 320]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`a13b18ba448680976c0ce047aeb296e5c2c9d1ee`。

安装先核对模型与压缩哈希，经共同路径转换候选，再交给历史替换原语。候选安装后实时后缀可能令窗口仍超预算，允许一次前台回退；这不是无限重试。

该文件按列出的范围取得并阅读，包内保留原始定位与中文笔记，没有伪造或拼凑全文副本。

### C08 · 历史版本、重写与基线

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/context_manager/history.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C08.md)

**已取得范围：**`[[1, 300]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`f39be3fb41fee1371036f393d5d1f62057225b60`。

history\_version记录重写；reset\_version用于破坏性重置；user\_message\_revision独立。模型历史、保留事实和审查上下文还分别存在。不能把消息条数或一个版本号当作全部状态身份。

该文件按列出的范围取得并阅读，包内保留原始定位与中文笔记，没有伪造或拼凑全文副本。

### C09 · 注册冲突、准入、钩子及结果

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/tools/registry.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C09.md)

**已取得范围：**`[[1, 180], [430, 1030]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`ebde5a7bdc449a11dc9c1fc1d8475c8e4432010f`。

前置钩子可阻止handler或重建入参；handler执行后才有后置检查。固定源码明确后置阻止拒绝结果、不撤销执行；on\_tool\_result\_accepted在后置接受之后调用。

**选取的原码摘录：**不是完整文件，不具备独立可编译性；全文blob值仅用于标识来源，不冒称已对摘录完成整文件哈希验证。

```
        let post_tool_use_payload = if success {
            result
                .as_ref()
                .ok()
                .and_then(|result| result.post_tool_use_payload.clone())
        } else {
            None
        };
```

### C10 · 规则刷新、缓存与子线程共享

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/agents_md_manager.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C10.md)

**已取得范围：**`[[1, 320]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`ee80cebce50a98248f4503c3861797e86c54d882`。

规则刷新串行化但外部provider调用不占状态锁。环境或信任变化先失效旧缓存，避免刷新失败继续暴露旧规则。子Agent继承已应用文本，动态thread provider需要显式允许共享。

该文件按列出的范围取得并阅读，包内保留原始定位与中文笔记，没有伪造或拼凑全文副本。

### C11 · 子Agent输入与消息提交

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/agent/control.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C11.md)

**已取得范围：**`[[1, 480]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`765725df7b278acd308fbcf9a544b8963c63e941`。

提交或邮箱排队只返回接受标识。未装载接收者且trigger\_turn=false时可仅排队，不意味着启动，更不意味着子任务完成。会话身份与树运行时分开。

**选取的原码摘录：**不是完整文件，不具备独立可编译性；全文blob值仅用于标识来源，不冒称已对摘录完成整文件哈希验证。

```
            // Keep unloaded delivery atomic with publication of a reloaded session.
            let threads = state.threads.read().await;
            if !communication.trigger_turn && !threads.contains_key(&agent_id) {
                let _membership = self.runtime.admit_start()?;
                self.runtime.ensure_agent_known(agent_id)?;
                let submission_id = uuid::Uuid::now_v7().to_string();
                self.runtime.mailboxes.enqueue(
                    agent_id,
                    Some(submission_id.clone()),
                    vec![crate::PendingAgentMessage::new(communication, delivery)],
                )?;
```

### C12 · 子线程创建及历史过滤

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/agent/control/spawn.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C12.md)

**已取得范围：**`[[1, 280]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`22cd725605272a5e4e3b475c8ad2fb2835df0203`。

所读fork过滤函数对不同消息类型有不同保留规则，并移除父线程累计用量。某一路径能复制历史，不代表每种子Agent都完整复制父上下文、工具、权限和缓存。

**选取的原码摘录：**不是完整文件，不具备独立可编译性；全文blob值仅用于标识来源，不冒称已对摘录完成整文件哈希验证。

```
        // Full-history forks preserve the cached prompt prefix and can keep diffing
        // from the parent's durable baseline unless legacy compaction requires rebuilding it.
        RolloutItem::TurnContext(_) | RolloutItem::WorldState(_) => preserve_context_baselines,
        // Child threads inherit model context, not the parent's cumulative usage state.
        RolloutItem::TokenUsageRecord(_) => false,
```

### C13 · 记忆流水线启动条件

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/memories/write/src/start.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C13.md)

**已取得范围：**`[[1, 95]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`102881cf6fde44782cc0779920a3f75d37f93b92`。

启动记忆有根线程、非临时会话、功能标记、数据库和目录等条件；清理与阶段任务顺序可追踪。不能写成每次对话都会永久学习。

**完整文件已保存，Git blob校验一致。**以下原代码可离线核对，未作为独立模块执行。

```
use crate::ensure_layout;
use crate::extensions::seed_extension_instructions;
use crate::guard;
use crate::metrics::MEMORY_STARTUP;
use crate::phase1;
use crate::phase2;
use crate::runtime::MemoryStartupContext;
use codex_core::CodexThread;
use codex_core::ThreadManager;
use codex_core::config::Config;
use codex_features::Feature;
use codex_login::AuthManager;
use codex_protocol::MemoryVersion;
use codex_protocol::ThreadId;
use codex_protocol::models::PermissionProfile;
use codex_protocol::protocol::SessionSource;
use std::sync::Arc;
use tracing::warn;

/// Starts the asynchronous startup memory pipeline for an eligible root session.
///
/// The pipeline is skipped for ephemeral sessions, disabled feature flags, and
/// subagent sessions.
pub fn start_memories_startup_task(
    thread_manager: Arc<ThreadManager>,
    auth_manager: Arc<AuthManager>,
    thread_id: ThreadId,
    thread: Arc<CodexThread>,
    config: Arc<Config>,
    parent_permission_profile: PermissionProfile,
    source: &SessionSource,
) {
    if config.ephemeral
        || !config.features.enabled(Feature::MemoryTool)
        || source.is_non_root_agent()
    {
        return;
    }

    // Dual-write warms v2 while v1 is selected; it is no longer needed after cutover.
    let versions = if config.memories.dual_write && config.memories.version == MemoryVersion::V1 {
        vec![MemoryVersion::V1, MemoryVersion::V2]
    } else {
        vec![config.memories.version]
    };
    for version in versions {
        let mut pipeline_config = config.as_ref().clone();
        pipeline_config.memories.version = version;
        let config = Arc::new(pipeline_config);
        let auth_manager = Arc::clone(&auth_manager);
        let parent_permission_profile = parent_permission_profile.clone();
        let context = Arc::new(MemoryStartupContext::new(
            Arc::clone(&thread_manager),
            Arc::clone(&auth_manager),
            thread_id,
            Arc::clone(&thread),
            config.as_ref(),
            source.clone(),
        ));
        tokio::spawn(async move {
            if context.memory_store().await.is_none() {
                warn!("state db unavailable for memories startup pipeline; skipping");
                return;
            }
            let root = config
                .codex_home
                .join(config.memories.version.directory_name());
            if let Err(err) = ensure_layout(&root).await {
                warn!("failed preparing memories root: {err}");
                return;
            }
            if let Err(err) = seed_extension_instructions(&root).await {
                warn!("failed seeding memory extension instructions: {err}");
            }

            // Clean memories to make preserve DB size. This does not consume tokens so can be
            // done before the quota check.
            phase1::prune(context.as_ref(), &config).await;

            if !guard::rate_limits_ok(&auth_manager, &config).await {
                context.counter(
                    MEMORY_STARTUP,
                    /*inc*/ 1,
                    &[("status", "skipped_rate_limit")],
                );
                return;
            }

            // Run phase 1.
            phase1::run(Arc::clone(&context), Arc::clone(&config)).await;
            // Run phase 2.
            phase2::run(context, config, parent_permission_profile).await;
        });
    }
}
```

### C14 · 记忆抽取与候选状态

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/memories/write/src/phase1.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C14.md)

**已取得范围：**`[[1, 280]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`cddb20dadcc62eac3896666b585fa851c7f00cfb`。

实际run先创建stage-one请求上下文再领取候选，不能盲从注释步骤。候选受来源、年龄、空闲时间、上限和租约约束；并发提取含“成功但无产出”结果，不应当成异常重试。

该文件按列出的范围取得并阅读，包内保留原始定位与中文笔记，没有伪造或拼凑全文副本。

### C15 · 记忆整合、租约与产物核验

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/memories/write/src/phase2.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C15.md)

**已取得范围：**`[[1, 660]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`d6d245f5917da5ad610119400df92efa2ac41a42`。

阶段二先取全局租约并准备Git基线，必要时才启动整合Agent；完成后先关停，检查产物，重新确认租约，再重置基线、登记成功。文件基线和数据库完成登记不是同一原子事务；关闭失败会保留租约等待过期。

**选取的原码摘录：**不是完整文件，不具备独立可编译性；全文blob值仅用于标识来源，不冒称已对摘录完成整文件哈希验证。

```
                if still_owns_lock {
                    if let Err(err) = reset_memory_workspace_baseline(&memory_root).await {
                        tracing::error!("failed resetting memory workspace baseline: {err}");
                        job::failed(context.as_ref(), &db, &claim, "failed_workspace_commit").await;
                    } else if !job::succeed(
                        context.as_ref(),
                        &db,
                        &claim,
                        new_watermark,
                        &selected_outputs,
                        "succeeded",
                    )
                    .await
                    {
                        tracing::error!(
                            "failed marking global memory consolidation job succeeded after resetting workspace baseline"
                        );
                    } else {
                        drop(phase_two_e2e_timer);
                        context.record_storage_size(&memory_root).await;
                    }
                }
```

### C16 · 会话历史替换与持久化入口

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/session/mod.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C16.md)

**已取得范围：**`[[1, 210], [800, 1150], [1450, 2300], [2300, 4530], [4600, 5200], [5350, 5750]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`96cfaa19707c13ed0bd5e7c7d3ab9f7c908226ca`。

捕获模型/环境时有锁顺序，耗时准备移到锁外。前缀安装在状态锁内核验代际、长度、授权并保留实时后缀；随后才持久化。返回true表示该路径接受了内存替换，不能单独当作断电恢复成功的证据。

**选取的原码摘录：**不是完整文件，不具备独立可编译性；全文blob值仅用于标识来源，不冒称已对摘录完成整文件哈希验证。

```
                    // Validate immediately before slicing and replacing the captured prefix.
                    if state.history.history_version() != prefix.generation
                        || state.history.annotated_items().len() < prefix.len
                        || self.services.model_client.auth_owner_generation()
                            != prefix.auth_owner_generation
                    {
                        return false;
                    }
                    let current = state.history.annotated_items();
                    let suffix = &current[prefix.len..];
```

### C17 · 远程压缩参数、钩子与回退

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/compact_remote_v2.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C17.md)

**已取得范围：**`[[1, 220]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`bacf8c3a5c5453051a20c57df1c3275c57ac27c3`。

区分前台、后台候选、是否前台回退与前置钩子。常量2是此快照中压缩传输重试上限，不是通用Agent重试标准。

**选取的原码摘录：**不是完整文件，不具备独立可编译性；全文blob值仅用于标识来源，不冒称已对摘录完成整文件哈希验证。

```
// Compact attempts can run much longer than normal turns, so keep the per-transport
// retry budget smaller than the general Responses stream retry budget.
const MAX_REMOTE_COMPACTION_V2_STREAM_RETRIES: u64 = 2;
```

### C18 · 取消与复用的固定测试案例

[官方出处／固定提交定位](https://github.com/openai/codex/blob/86e17e98c7f901277aeeb4649cf1b01462b082f2/codex-rs/core/src/session/async_compaction_tests.rs) · [本地中文研读笔记](agent-practice/verified/reading-notes/C18.md)

**已取得范围：**`[[1, 210]]`（1-based请求范围；文件较短时到实际末行）。**源码Git blob：**`e4a048124b83f15ab2c5d23c33e39cfff556d70e`。

已读取参数化Rust测试，检查取消前不发请求、已启动请求在轮次取消后仍可复用，并断言只收到一次请求。没有在本环境执行该Rust测试。

**选取的原码摘录：**不是完整文件，不具备独立可编译性；全文blob值仅用于标识来源，不冒称已对摘录完成整文件哈希验证。

```
    assert_eq!(summaries, ["prepared-summary"]);
    assert_eq!(request.requests().len(), 1);
    shutdown(&sess).await;
```

### A01 · Building effective agents

[官方出处／固定提交定位](https://www.anthropic.com/engineering/building-effective-agents) · [本地中文研读笔记](agent-practice/verified/reading-notes/A01.md)

**日期／版本：**2024-12-19。**实际范围：**完整正文的架构、工具设计与何时使用Agent部分。

流程预定与动态行动需要分开。先用满足目标的简单方案，出现真实的不确定步骤后再增加动态编排；原文列出的是可组合模式，不是所有任务必走的审批链。

**边界：**不要推成“复杂任务必用多Agent”或固定角色数量。

### A02 · Effective context engineering

[官方出处／固定提交定位](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) · [本地中文研读笔记](agent-practice/verified/reading-notes/A02.md)

**日期／版本：**2025-09-29。**实际范围：**上下文管理、按需取证、压缩和长任务部分。

信息选择既可提前组织，也可按需检索。压缩优先保留后续判断要用的事实和约束，再减少冗余；原始证据应能重读。

**边界：**压缩保真是需要测量的能力，不是摘要长度达标就成立。

### A03 · Writing tools for agents

[官方出处／固定提交定位](https://www.anthropic.com/engineering/writing-tools-for-agents) · [本地中文研读笔记](agent-practice/verified/reading-notes/A03.md)

**日期／版本：**2025-09-11。**实际范围：**工具原型、评测、命名、响应格式与有效描述部分。

工具接口应减少猜测与无用返回，按任务选择简明或详细结果，同时保留后续调用必需的标识。工具改进要在代表性任务上验证。

**边界：**简短响应不等于可以删除来源、版本或机器所需ID。

### A04 · Multi-agent research system

[官方出处／固定提交定位](https://www.anthropic.com/engineering/multi-agent-research-system) · [本地中文研读笔记](agent-practice/verified/reading-notes/A04.md)

**日期／版本：**2025-06-13。**实际范围：**多Agent架构、委派、工具、评测和生产经验部分。

并行研究需要明确子任务范围、资源预算和产物要求，用可追溯产物减少层层转述。协调和整合也有成本，适用性取决于问题能否分开。

**边界：**研究系统的测量结果不直接证明代码修改任务同样获益。

### A05 · Agent Skills

[官方出处／固定提交定位](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) · [本地中文研读笔记](agent-practice/verified/reading-notes/A05.md)

**日期／版本：**2025-10-16；原文注明2025-12-18更新。**实际范围：**技能结构、渐进发现、资源和安全部分。

技能先暴露概述，再按需读取正文及附属资源；可复用程序能降低重复生成的不稳定性。执行第三方脚本前仍要核实来源和权限。

**边界：**技能描述不等于已经读取正文；技能文件不自动取得外部权限。

### A06 · Long-running agent harnesses

[官方出处／固定提交定位](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) · [本地中文研读笔记](agent-practice/verified/reading-notes/A06.md)

**日期／版本：**2025-11-26。**实际范围：**初始化、增量工作、交接、测试和剩余挑战部分。

长任务需要可恢复的功能状态、工作记录和实际验收；每轮开始重建当前情况，结束留下可检查产物。进度声明不应代替测试。

**边界：**初始化/编码角色是该案例设计，不是强制每个简单修改都分两Agent。

### A07 · Agent evals

[官方出处／固定提交定位](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) · [本地中文研读笔记](agent-practice/verified/reading-notes/A07.md)

**日期／版本：**2026-01-09。**实际范围：**全文正文：任务/试验/判分定义、判分器、实施步骤与边界。

评测对象包括模型和Harness，最终环境结果与输出文本要区分。任务可有多个判分维度，样本应包含不该行动的反例，并用人工核对裁判。

**边界：**不能把调用轨迹必须一模一样当成通用成功标准；关键安全顺序可单独检查。

### A08 · Contextual Retrieval

[官方出处／固定提交定位](https://www.anthropic.com/engineering/contextual-retrieval) · [本地中文研读笔记](agent-practice/verified/reading-notes/A08.md)

**日期／版本：**2024-09-19。**实际范围：**上下文增强、检索组合、重排和实验限制部分。

为块补充上下文再建立关键词及向量索引，可缓解块失去背景的问题；混合检索与重排各解决不同阶段。生成的上下文仍应与原文分开。

**边界：**原文检索实验不是任意知识库的保证收益，也不是最终回答事实准确率。

### A09 · Code execution with MCP

[官方出处／固定提交定位](https://www.anthropic.com/engineering/code-execution-with-mcp) · [本地中文研读笔记](agent-practice/verified/reading-notes/A09.md)

**日期／版本：**2025-11-04。**实际范围：**工具发现、代码执行、数据处理与基础设施部分。

由代码组合工具并在执行环境过滤中间数据，可以少让模型阅读大批结果。工具网络请求不一定减少；执行环境仍需隔离、权限和资源限制。

**边界：**减少模型可见内容不自动保证日志、工具服务器或外部服务不接触敏感数据。

### A10 · Advanced tool use

[官方出处／固定提交定位](https://www.anthropic.com/engineering/advanced-tool-use) · [本地中文研读笔记](agent-practice/verified/reading-notes/A10.md)

**日期／版本：**2025-11-24。**实际范围：**工具搜索、程序化调用、调用示例、取舍与上手部分。

工具搜索应对大量定义，程序化调用应对数据中转，示例应对复杂参数约定。应根据实际瓶颈分别评估，不把三个功能捆成默认流程。

**边界：**旧文章中的Beta参数和模型支持不能直接复制为当前可运行接口。

### A11 · Claude Code sandboxing

[官方出处／固定提交定位](https://www.anthropic.com/engineering/claude-code-sandboxing) · [本地中文研读笔记](agent-practice/verified/reading-notes/A11.md)

**日期／版本：**2025-10-20。**实际范围：**文件系统/网络隔离、许可交互及实现说明部分。

文件系统与网络限制约束工具执行的破坏范围；批准对话和运行时隔离承担不同职责。模型指令无法替代系统边界。

**边界：**有沙箱不等于所有远端工具和授权内的数据都安全，不能宣称彻底消除注入。

### A12 · Infrastructure noise in coding evals

[官方出处／固定提交定位](https://www.anthropic.com/engineering/infrastructure-noise) · [本地中文研读笔记](agent-practice/verified/reading-notes/A12.md)

**日期／版本：**2026-02-05。**实际范围：**资源上限、评测噪声及实验建议部分。

执行资源上限改变会改变任务可完成性。比较模型/Harness前，应固定或记录资源、超时与环境；失败分类要保留在统计口径里。

**边界：**文章中的特定资源倍数不是所有任务的最优配置。

### A13 · Harness design for long-running apps

[官方出处／固定提交定位](https://www.anthropic.com/engineering/harness-design-long-running-apps) · [本地中文研读笔记](agent-practice/verified/reading-notes/A13.md)

**日期／版本：**2026-03-24。**实际范围：**规划/生成/评价、模型升级后简化、实验及附录正文。

独立评价可减少自评偏宽，但仍需要标准与校准。文章也展示随着模型变化移除重置和阶段编排；因此流程必须跟随任务与模型重新验证。

**边界：**角色分离不是统计独立保证，也不证明更多Agent总是更优。

### A14 · Managed agents

[官方出处／固定提交定位](https://www.anthropic.com/engineering/managed-agents) · [本地中文研读笔记](agent-practice/verified/reading-notes/A14.md)

**日期／版本：**2026-04-08。**实际范围：**模型、Harness、会话和执行环境分离部分。

将可持久会话记录、推理控制和执行环境分开，可以分别处理故障和资源调度。日志仍需转成有用的模型上下文。

**边界：**产品案例的首Token延迟改善不是本教材实测，也不是普遍性能结论。

### A15 · Building a C compiler

[官方出处／固定提交定位](https://www.anthropic.com/engineering/building-c-compiler) · [本地中文研读笔记](agent-practice/verified/reading-notes/A15.md)

**日期／版本：**2026-02-05。**实际范围：**并行编译器案例的任务划分、验证、瓶颈与局限部分。

多个工作者需要共享可检查任务、稳定测试和合并纪律。当全部工作者被同一问题阻塞时，调整测试与任务划分比继续增加并发更有意义。

**边界：**实验产物的能力和缺点均需保留，不能写成生产级编译器已经被普遍替代。

### A16 · Claude Code quality postmortem

[官方出处／固定提交定位](https://www.anthropic.com/engineering/april-23-postmortem) · [本地中文研读笔记](agent-practice/verified/reading-notes/A16.md)

**日期／版本：**2026-04-23。**实际范围：**质量事件说明、三个原因、修复时间与后续措施。

这份复盘将具体质量变化关联到推理设置、上下文管理和产品提示变更。教材据此要求记录产品配置和版本，避免仅依据感受归因模型。

**边界：**这是已披露的历史事件，不表示现在相同缺陷仍存在，也不适用于所有API用户。

### A17 · Historical think-tool design

[官方出处／固定提交定位](https://www.anthropic.com/engineering/claude-think-tool) · [本地中文研读笔记](agent-practice/verified/reading-notes/A17.md)

**日期／版本：**2025-03-20；2025-12-15更新。**实际范围：**历史think工具设计、评测与文首更新声明。

历史上独立think工具用于复杂工具任务的中间整理。作者后来说明多数场景优先使用改进后的扩展思考，故教材保留历史方法而不列为必备步骤。

**边界：**不把隐藏推理全文当交付证据；更长思考或更多调用本身不是正确性保证。

### D01 · How Claude Code works

[官方出处／固定提交定位](https://code.claude.com/docs/en/how-claude-code-works) · [本地中文研读笔记](agent-practice/verified/reading-notes/D01.md)

**日期／版本：**2026-10-22检索快照。**实际范围：**Agent循环、上下文管理、工具与检查点相关小节。

会话历史、自动整理、工具和文件检查点是不同机制。检查点可恢复哪些文件应查具体产品文档，不能把它扩大成对任意远端副作用的事务回滚。

**边界：**未读取该网站所有页面；公开产品说明不等于闭源服务源码。

### D02 · Claude Code memory

[官方出处／固定提交定位](https://code.claude.com/docs/en/memory) · [本地中文研读笔记](agent-practice/verified/reading-notes/D02.md)

**日期／版本：**2026-10-22检索快照。**实际范围：**CLAUDE.md、AGENTS.md、导入、目录与记忆相关小节。

Claude Code文档明确CLAUDE.md与自动记忆的用途；AGENTS.md不是同等自动发现文件，需要显式引入等配置。目录被授权访问，也不意味着相关规则都已加载。

**边界：**不把Codex的AGENTS规则自动套到Claude。

### D03 · Claude Code subagents

[官方出处／固定提交定位](https://code.claude.com/docs/en/sub-agents) · [本地中文研读笔记](agent-practice/verified/reading-notes/D03.md)

**日期／版本：**2026-10-22检索快照。**实际范围：**上下文隔离、tools/skills、权限与内置Agent相关小节。

非fork子Agent从独立上下文开始；工具、预加载技能和权限有各自配置。所读文档注明Explore/Plan的精简规则行为，不能承诺自动继承主Agent所有已读内容。

**边界：**fork/普通子Agent、不同版本及内置角色不可混为一谈。

### D04 · Claude Code hooks

[官方出处／固定提交定位](https://code.claude.com/docs/en/hooks) · [本地中文研读笔记](agent-practice/verified/reading-notes/D04.md)

**日期／版本：**2026-10-22检索快照。**实际范围：**PreToolUse、PostToolUse、PostToolUseFailure及输出/日志相关小节。

前置改写与后置结果处理是不同时间点；Claude后置block追加原因并保留原结果，替换使用单独字段。原始结果可能在后置修改前已经记录。

**边界：**文档有3271行，本轮核验上述相关小节，不声称逐项审查全部Hook事件。

### D05 · Claude Code permissions

[官方出处／固定提交定位](https://code.claude.com/docs/en/permissions) · [本地中文研读笔记](agent-practice/verified/reading-notes/D05.md)

**日期／版本：**2026-10-22检索快照。**实际范围：**规则顺序、工具与运行时权限匹配小节。

读取的文档给出deny/ask/allow等规则评估顺序；工具是否出现在模型上下文与参数级执行时检查不能混同。最终行动仍受授权边界限制。

**边界：**具体模式和配置属于检索时版本，不当成不可变标准。

### D06 · Claude Code Skills

[官方出处／固定提交定位](https://code.claude.com/docs/en/skills) · [本地中文研读笔记](agent-practice/verified/reading-notes/D06.md)

**日期／版本：**2026-10-22检索快照。**实际范围：**技能发现、invocation控制、allowed-tools与子Agent预载小节。

菜单可见、允许模型调用、正文已加载和工具使用许可是不同状态；文档还区分正文保留与临时工具许可的生命周期。

**边界：**按具体版本检查allowed-tools和禁用规则，不能只说“技能永远不能影响权限”。

### D07 · Claude Code best practices

[官方出处／固定提交定位](https://code.claude.com/docs/en/best-practices) · [本地中文研读笔记](agent-practice/verified/reading-notes/D07.md)

**日期／版本：**2026-10-22检索快照。**实际范围：**可验证标准、探索/计划/实现与上下文管理小节。

先给可检查的完成标准，再根据问题是否不明、是否跨模块选择规划和验证深度。简单明确修改不应为了形式重复计划/评审。

**边界：**这些是工程实践建议，不是产品对每次任务的强制控制流程。

## 可重复检查与未覆盖范围

新增Python程序检查的是教学状态与资料清单，不是Codex Rust测试，也没有调用付费LLM或生产服务。旧测试记录标为历史；本次实际重跑结果另存。[新增完整代码](agent-practice/verified/test_verified_contracts.py) · [本轮结果](agent-practice/verified/test-results.json) · [包内完整性检查](agent-practice/verified/QA.json)

[Codex摘录Apache 2.0许可证](agent-practice/verified/LICENSE-CODEX-APACHE-2.0.txt) · [署名与编辑说明](agent-practice/verified/ATTRIBUTION.txt)。本文是原创中文讲解，不是厂商原文的逐字翻译。