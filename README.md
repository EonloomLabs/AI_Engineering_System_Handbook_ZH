# AI 系统工程：从基础到内部

**简体中文** · [English](README.en.md) · [日本語](README.ja.md) · [Español](README.es.md) · [Tiếng Việt](README.vi.md)

离线教材 · 基础概念、内部机制、工程实践

从基础到内部：理解大语言模型怎样处理输入与生成输出，掌握智能体如何使用工具、管理上下文与记忆，并以可验证的方法改善工程质量。

## 打开

完整解压后打开 [`index.html`](index.html)。无需服务器、无需联网、无需模型 API 或密钥。
每页页眉的语言开关可直接跳到同一页的其他语种版本。

## 课程结构

主干是五个阶段、68 课：先观察系统，再逐层深入到模型内部，最后回到全栈验收。

| 阶段 | 课次 | 内容 |
| --- | --- | --- |
| 观察系统 | 第 01—06 课 | 先把一次任务的运行过程变成可检查的证据，再谈改动 |
| 构建循环 | 第 07—28 课 | 工具调用、上下文、检索、记忆与失败恢复 |
| 优化黑盒 | 第 29—34 课 | 不打开模型，用权限、固定任务和完整计时判断优化是否有效 |
| 接管模型 | 第 35—63 课 | 从服务接口走进张量、前向、训练、推理，直到 GPU 与调度 |
| 全栈验证 | 第 64—68 课 | 把多模态、不确定性与跨层优化接回同一套验收标准 |

基础篇 40 节配自检题，系统篇 28 章围绕 112 个主问题展开；另有十二个阅读主题，供已有基础时按问题进入。
正文、图解与公式说明完整展开，自检答案默认收起、按需查看。

## 目录位置

| 位置 | 内容 |
| --- | --- |
| [`index.html`](index.html) | 正常阅读入口 |
| [`complete.html`](complete.html) | 同一内容的连续阅读版，不依赖其他文件 |
| [`worked-examples.html`](worked-examples.html) | 运行示例索引，可按编号集中查找 |
| [`worked-model.html`](worked-model.html) | 用相同的两句话把所有中间矩阵算到底 |
| [`labs/model/`](labs/model/) | 模型示例代码、原始参数、训练后参数与数值记录 |
| [`worked-examples/`](worked-examples/) | 可运行的确定性数值与状态见证 |
| [`diagrams/`](diagrams/) | 图解源码、数据与检查 |
| [`wiki/`](wiki/) | 可编辑 Wiki 正文与目录 |
| [`editorial/`](editorial/) | 编写方法与内容迁移记录 |
| [`validation/integration/`](validation/integration/) | 本轮检查记录 |
| [`i18n/`](i18n/) | 多语言翻译表、工具与验证记录 |

## 复算

不需要网络、GPU 或 API 密钥。Python 3.10 及以上，在解压目录执行：

```bash
python3 worked-examples/run_all.py
```

可运行代码与模型数据位于根目录，由各语种版本共用；脚本注释与输出为中文。
改变示例须重新运行，并同步图形、文字、搜索和连续版——约定见 [`AGENTS.md`](AGENTS.md)。

## 语言版本

| 语言 | 入口 |
| --- | --- |
| 简体中文（正本） | [`index.html`](index.html) |
| English | [`en/index.html`](en/index.html) |
| 日本語 | [`ja/index.html`](ja/index.html) |
| Español | [`es/index.html`](es/index.html) |
| Tiếng Việt | [`vi/index.html`](vi/index.html) |

各版均为 262 页分页正文加同内容的 `complete.html`。中文为正本，译文问题与原文疑点记录在 [`i18n/SOURCE-ISSUES.md`](i18n/SOURCE-ISSUES.md)，不代为修改原文。

## 验证边界

401 个教学示例不等于 401 场模型能力实验。数值公式、维度、因果性、梯度、协议分片与简化状态行为由测试核对；其他场景例在给定前提后作明确推演。
它们不证明商业 Agent 效果、GPU 速度、闭源内部或生产安全。
来源定位到实际文件、函数与行号；工程推导、实测与教学模拟分别标明。
数值图中的舍入仅用于显示，计算使用原精度。

来源核验范围见 [`engineering/agent-evidence.html`](engineering/agent-evidence.html)，机器记录位于 `engineering/agent-practice/verified/`。
打包说明另见 [`README.txt`](README.txt) 与 [`开始阅读.txt`](开始阅读.txt)。
