---
title: "知识主题索引"
description: "AI系统工程：本地教学正文与可追溯图表"
---

阅读指南与附录


<span id="section-0"></span>


# 知识主题索引

按知识主题查找基础课、系统章节与拓展讲义。下表的206项来自不同类型的论文、课程和公开文档；对应关系表示主题关联，不表示已经复现每篇资料的全部实验与附录。


<span id="prereq"></span>


## 系统篇与预备知识

| 系统章节 | 基础课 |
| --- | --- |
| [01｜输入究竟是什么：从用户的一句话到模型张量](chapters/01.md) | [F01](foundations/01.md) · [F02](foundations/02.md) · [F03](foundations/03.md) · [F04](foundations/04.md) · [F05](foundations/05.md) · [F06](foundations/06.md) · [F09](foundations/09.md) · [F18](foundations/18.md) · [F16](foundations/16.md) · [F22](foundations/22.md) · [F37](foundations/37.md) |
| [02｜一次Transformer前向：逐张量、逐算子讲明白](chapters/02.md) | [F07](foundations/07.md) · [F08](foundations/08.md) · [F09](foundations/09.md) · [F10](foundations/10.md) · [F11](foundations/11.md) · [F14](foundations/14.md) |
| [03｜注意力的深入追问：位置、掩码、多头与反向传播](chapters/03.md) | [F08](foundations/08.md) · [F11](foundations/11.md) · [F12](foundations/12.md) · [F13](foundations/13.md) · [F14](foundations/14.md) · [F15](foundations/15.md) · [F16](foundations/16.md) |
| [06｜推理机制：加载、解码策略与连续生成](chapters/06.md) | [F09](foundations/09.md) · [F14](foundations/14.md) · [F18](foundations/18.md) · [F19](foundations/19.md) · [F21](foundations/21.md) |
| [04｜训练机制：损失、完整反向传播与参数更新](chapters/04.md) | [F06](foundations/06.md) · [F09](foundations/09.md) · [F15](foundations/15.md) · [F16](foundations/16.md) · [F21](foundations/21.md) |
| [05｜后训练与模型定制：目标、结构和参数适配](chapters/05.md) | [F07](foundations/07.md) · [F09](foundations/09.md) · [F16](foundations/16.md) · [F17](foundations/17.md) · [F20](foundations/20.md) |
| [07｜KV Cache、FlashAttention与PagedAttention的内部过程](chapters/07.md) | [F06](foundations/06.md) · [F07](foundations/07.md) · [F08](foundations/08.md) · [F11](foundations/11.md) · [F12](foundations/12.md) · [F13](foundations/13.md) · [F19](foundations/19.md) · [F21](foundations/21.md) |
| [08｜推理服务：调度、吞吐、延迟和并行](chapters/08.md) | [F06](foundations/06.md) · [F09](foundations/09.md) · [F19](foundations/19.md) · [F20](foundations/20.md) · [F21](foundations/21.md) · [F38](foundations/38.md) |
| [09｜Agent一次任务的完整循环：谁在思考，谁在执行](chapters/09.md) | [F01](foundations/01.md) · [F18](foundations/18.md) · [F22](foundations/22.md) · [F23](foundations/23.md) · [F24](foundations/24.md) |
| [10｜模型输出怎样变成真实工具调用：协议与执行边界](chapters/10.md) | [F03](foundations/03.md) · [F22](foundations/22.md) · [F23](foundations/23.md) · [F24](foundations/24.md) · [F33](foundations/33.md) |
| [11｜工具设计与MCP：从连接到可控执行](chapters/11.md) | [F23](foundations/23.md) · [F24](foundations/24.md) · [F25](foundations/25.md) · [F33](foundations/33.md) · [F37](foundations/37.md) |
| [12｜Codex、Claude Code、Copilot：从公开事实到可诊断运行链](chapters/12.md) | [F22](foundations/22.md) · [F23](foundations/23.md) · [F24](foundations/24.md) · [F25](foundations/25.md) · [F26](foundations/26.md) · [F27](foundations/27.md) · [F32](foundations/32.md) · [F37](foundations/37.md) |
| [13｜每一轮Prompt怎样组装：上下文是一条数据管线](chapters/13.md) | [F03](foundations/03.md) · [F24](foundations/24.md) · [F25](foundations/25.md) · [F26](foundations/26.md) · [F27](foundations/27.md) · [F32](foundations/32.md) |
| [14｜上下文压缩：到底压掉什么，丢失后又如何恢复](chapters/14.md) | [F19](foundations/19.md) · [F24](foundations/24.md) · [F26](foundations/26.md) · [F27](foundations/27.md) · [F31](foundations/31.md) · [F33](foundations/33.md) · [F35](foundations/35.md) |
| [15｜检索离线链路：文档怎样变成可查询索引](chapters/15.md) | [F03](foundations/03.md) · [F07](foundations/07.md) · [F09](foundations/09.md) · [F28](foundations/28.md) · [F29](foundations/29.md) · [F37](foundations/37.md) |
| [16｜检索在线链路：召回、融合、重排与证据充足性](chapters/16.md) | [F09](foundations/09.md) · [F28](foundations/28.md) · [F29](foundations/29.md) · [F35](foundations/35.md) |
| [17｜代码智能：从文本搜索到符号、版本与运行证据](chapters/17.md) | [F24](foundations/24.md) · [F28](foundations/28.md) · [F29](foundations/29.md) · [F30](foundations/30.md) · [F34](foundations/34.md) |
| [18｜长期记忆：写入、检索、冲突、失效与遗忘](chapters/18.md) | [F24](foundations/24.md) · [F27](foundations/27.md) · [F28](foundations/28.md) · [F29](foundations/29.md) · [F31](foundations/31.md) · [F35](foundations/35.md) |
| [19｜Skills与路由：怎样加载刚好需要的专业能力](chapters/19.md) | [F22](foundations/22.md) · [F25](foundations/25.md) · [F26](foundations/26.md) · [F30](foundations/30.md) · [F31](foundations/31.md) · [F32](foundations/32.md) · [F35](foundations/35.md) |
| [20｜多Agent：并行的收益与交接的损失](chapters/20.md) | [F24](foundations/24.md) · [F30](foundations/30.md) · [F32](foundations/32.md) · [F33](foundations/33.md) · [F34](foundations/34.md) · [F35](foundations/35.md) |
| [21｜可靠执行：重试、幂等、崩溃与状态恢复](chapters/21.md) | [F23](foundations/23.md) · [F24](foundations/24.md) · [F30](foundations/30.md) · [F33](foundations/33.md) · [F37](foundations/37.md) |
| [22｜工程质量：从需求到测试，再到真正可交付的代码](chapters/22.md) | [F24](foundations/24.md) · [F30](foundations/30.md) · [F33](foundations/33.md) · [F34](foundations/34.md) · [F35](foundations/35.md) |
| [23｜Evaluation：怎样证明一次优化真有收益](chapters/23.md) | [F09](foundations/09.md) · [F28](foundations/28.md) · [F34](foundations/34.md) · [F35](foundations/35.md) · [F36](foundations/36.md) |
| [24｜安全：指令边界、沙箱、权限与记忆污染](chapters/24.md) | [F23](foundations/23.md) · [F25](foundations/25.md) · [F31](foundations/31.md) · [F33](foundations/33.md) · [F37](foundations/37.md) |
| [25｜生产运行：Trace、成本、队列、灰度与回滚](chapters/25.md) | [F21](foundations/21.md) · [F24](foundations/24.md) · [F33](foundations/33.md) · [F35](foundations/35.md) · [F36](foundations/36.md) · [F37](foundations/37.md) · [F38](foundations/38.md) |
| [26｜深度应用：把组件组合成能解释的工作系统](chapters/26.md) | [F22](foundations/22.md) · [F24](foundations/24.md) · [F27](foundations/27.md) · [F29](foundations/29.md) · [F30](foundations/30.md) · [F31](foundations/31.md) · [F33](foundations/33.md) · [F34](foundations/34.md) · [F35](foundations/35.md) · [F37](foundations/37.md) · [F38](foundations/38.md) · [F39](foundations/39.md) |
| [27｜事实可靠性、多模态与可解释性：能力边界在哪里](chapters/27.md) | [F09](foundations/09.md) · [F14](foundations/14.md) · [F15](foundations/15.md) · [F17](foundations/17.md) · [F35](foundations/35.md) · [F36](foundations/36.md) · [F39](foundations/39.md) |
| [28｜研究深水区与系统综合判断](chapters/28.md) | [F07](foundations/07.md) · [F11](foundations/11.md) · [F19](foundations/19.md) · [F16](foundations/16.md) · [F17](foundations/17.md) · [F20](foundations/20.md) · [F21](foundations/21.md) · [F26](foundations/26.md) · [F27](foundations/27.md) · [F35](foundations/35.md) · [F36](foundations/36.md) · [F39](foundations/39.md) · [F40](foundations/40.md) |


<span id="reading-topics"></span>


## 206项拓展主题

| 编号 | 主题与中文讲义 | 相关系统章节 |
| --- | --- | --- |

<span id="topic-0-1"></span>
| 0.1 | [LLM课程：概念与工具全景](reading-notes/chapter-00.md#m-00-01) | [01](chapters/01.md) · [09](chapters/09.md) · [12](chapters/12.md) |

<span id="topic-0-2"></span>
| 0.2 | [图解GPT-2：自回归模型](reading-notes/chapter-00.md#m-00-02) | [01](chapters/01.md) · [09](chapters/09.md) · [12](chapters/12.md) |

<span id="topic-0-3"></span>
| 0.3 | [构建有效的智能体](reading-notes/chapter-00.md#m-00-03) | [01](chapters/01.md) · [09](chapters/09.md) · [12](chapters/12.md) |

<span id="topic-0-4"></span>
| 0.4 | [展开Codex智能体循环](reading-notes/chapter-00.md#m-00-04) | [01](chapters/01.md) · [09](chapters/09.md) · [12](chapters/12.md) |

<span id="topic-0-5"></span>
| 0.5 | [从零构建语言模型的知识版图](reading-notes/chapter-00.md#m-00-05) | [01](chapters/01.md) · [09](chapters/09.md) · [12](chapters/12.md) |

<span id="topic-1-1"></span>
| 1.1 | [图解Transformer](reading-notes/chapter-01.md#m-01-01) | [01](chapters/01.md) · [02](chapters/02.md) · [03](chapters/03.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-1-2"></span>
| 1.2 | [分词流水线](reading-notes/chapter-01.md#m-01-02) | [01](chapters/01.md) · [02](chapters/02.md) · [03](chapters/03.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-1-3"></span>
| 1.3 | [注意力与Transformer原始架构](reading-notes/chapter-01.md#m-01-03) | [01](chapters/01.md) · [02](chapters/02.md) · [03](chapters/03.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-1-4"></span>
| 1.4 | [带代码注解的Transformer](reading-notes/chapter-01.md#m-01-04) | [01](chapters/01.md) · [02](chapters/02.md) · [03](chapters/03.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-1-5"></span>
| 1.5 | [图解词向量](reading-notes/chapter-01.md#m-01-05) | [01](chapters/01.md) · [02](chapters/02.md) · [03](chapters/03.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-1-6"></span>
| 1.6 | [注意力机制的不同形式](reading-notes/chapter-01.md#m-01-06) | [01](chapters/01.md) · [02](chapters/02.md) · [03](chapters/03.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-1-7"></span>
| 1.7 | [旋转位置编码RoPE](reading-notes/chapter-01.md#m-01-07) | [01](chapters/01.md) · [02](chapters/02.md) · [03](chapters/03.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-1-8"></span>
| 1.8 | [分组查询注意力](reading-notes/chapter-01.md#m-01-08) | [01](chapters/01.md) · [02](chapters/02.md) · [03](chapters/03.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-1-9"></span>
| 1.9 | [稀疏专家与路由](reading-notes/chapter-01.md#m-01-09) | [01](chapters/01.md) · [02](chapters/02.md) · [03](chapters/03.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-1-10"></span>
| 1.10 | [少样本与上下文学习](reading-notes/chapter-01.md#m-01-10) | [01](chapters/01.md) · [02](chapters/02.md) · [03](chapters/03.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-1-11"></span>
| 1.11 | [Llama3：完整模型系统案例](reading-notes/chapter-01.md#m-01-11) | [01](chapters/01.md) · [02](chapters/02.md) · [03](chapters/03.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-1-12"></span>
| 1.12 | [DeepSeek-V3：稀疏模型工程](reading-notes/chapter-01.md#m-01-12) | [01](chapters/01.md) · [02](chapters/02.md) · [03](chapters/03.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-1-13"></span>
| 1.13 | [Qwen3：推理与非推理模式](reading-notes/chapter-01.md#m-01-13) | [01](chapters/01.md) · [02](chapters/02.md) · [03](chapters/03.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-1-14"></span>
| 1.14 | [LLM技术研究全景](reading-notes/chapter-01.md#m-01-14) | [01](chapters/01.md) · [02](chapters/02.md) · [03](chapters/03.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-1"></span>
| 2.1 | [语言模型缩放规律](reading-notes/chapter-02.md#m-02-01) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-2"></span>
| 2.2 | [计算最优训练与Chinchilla](reading-notes/chapter-02.md#m-02-02) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-3"></span>
| 2.3 | [训练语料的来源与构成](reading-notes/chapter-02.md#m-02-03) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-4"></span>
| 2.4 | [训练数据去重](reading-notes/chapter-02.md#m-02-04) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-5"></span>
| 2.5 | [数据、缩放与训练评估](reading-notes/chapter-02.md#m-02-05) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-6"></span>
| 2.6 | [SFT与RLHF](reading-notes/chapter-02.md#m-02-06) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-7"></span>
| 2.7 | [直接偏好优化DPO](reading-notes/chapter-02.md#m-02-07) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-8"></span>
| 2.8 | [基于原则的AI反馈](reading-notes/chapter-02.md#m-02-08) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-9"></span>
| 2.9 | [近端策略优化PPO](reading-notes/chapter-02.md#m-02-09) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-10"></span>
| 2.10 | [模型行为规范与指令层级](reading-notes/chapter-02.md#m-02-10) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-11"></span>
| 2.11 | [思维链提示与多步骤推理](reading-notes/chapter-02.md#m-02-11) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-12"></span>
| 2.12 | [通过强化学习形成推理能力](reading-notes/chapter-02.md#m-02-12) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-13"></span>
| 2.13 | [过程监督与结果监督](reading-notes/chapter-02.md#m-02-13) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-14"></span>
| 2.14 | [多路径采样与自一致性](reading-notes/chapter-02.md#m-02-14) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-2-15"></span>
| 2.15 | [思维树与外部搜索](reading-notes/chapter-02.md#m-02-15) | [05](chapters/04.md) · [06](chapters/05.md) · [28](chapters/28.md) |

<span id="topic-3-1"></span>
| 3.1 | [文本生成与解码策略](reading-notes/chapter-03.md#m-03-01) | [04](chapters/06.md) · [07](chapters/07.md) · [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-3-2"></span>
| 3.2 | [退化文本与核采样](reading-notes/chapter-03.md#m-03-02) | [04](chapters/06.md) · [07](chapters/07.md) · [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-3-3"></span>
| 3.3 | [KV缓存策略](reading-notes/chapter-03.md#m-03-03) | [04](chapters/06.md) · [07](chapters/07.md) · [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-3-4"></span>
| 3.4 | [推理模型的API使用](reading-notes/chapter-03.md#m-03-04) | [04](chapters/06.md) · [07](chapters/07.md) · [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-3-5"></span>
| 3.5 | [推理模型的使用边界](reading-notes/chapter-03.md#m-03-05) | [04](chapters/06.md) · [07](chapters/07.md) · [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-3-6"></span>
| 3.6 | [Prefill与Decode](reading-notes/chapter-03.md#m-03-06) | [04](chapters/06.md) · [07](chapters/07.md) · [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-3-7"></span>
| 3.7 | [提示前缀缓存](reading-notes/chapter-03.md#m-03-07) | [04](chapters/06.md) · [07](chapters/07.md) · [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-3-8"></span>
| 3.8 | [分页管理KV缓存](reading-notes/chapter-03.md#m-03-08) | [04](chapters/06.md) · [07](chapters/07.md) · [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-3-9"></span>
| 3.9 | [注意力的IO优化](reading-notes/chapter-03.md#m-03-09) | [04](chapters/06.md) · [07](chapters/07.md) · [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-3-10"></span>
| 3.10 | [推测解码](reading-notes/chapter-03.md#m-03-10) | [04](chapters/06.md) · [07](chapters/07.md) · [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-3-11"></span>
| 3.11 | [推理服务架构](reading-notes/chapter-03.md#m-03-11) | [04](chapters/06.md) · [07](chapters/07.md) · [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-3-12"></span>
| 3.12 | [端到端延迟优化](reading-notes/chapter-03.md#m-03-12) | [04](chapters/06.md) · [07](chapters/07.md) · [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-4-1"></span>
| 4.1 | [提示工程基础](reading-notes/chapter-04.md#m-04-01) | [01](chapters/01.md) · [10](chapters/10.md) · [13](chapters/13.md) |

<span id="topic-4-2"></span>
| 4.2 | [提示组织与版本管理](reading-notes/chapter-04.md#m-04-02) | [01](chapters/01.md) · [10](chapters/10.md) · [13](chapters/13.md) |

<span id="topic-4-3"></span>
| 4.3 | [输入可信度与指令冲突](reading-notes/chapter-04.md#m-04-03) | [01](chapters/01.md) · [10](chapters/10.md) · [13](chapters/13.md) |

<span id="topic-4-4"></span>
| 4.4 | [函数调用协议](reading-notes/chapter-04.md#m-04-04) | [01](chapters/01.md) · [10](chapters/10.md) · [13](chapters/13.md) |

<span id="topic-4-5"></span>
| 4.5 | [结构化输出与约束](reading-notes/chapter-04.md#m-04-05) | [01](chapters/01.md) · [10](chapters/10.md) · [13](chapters/13.md) |

<span id="topic-4-6"></span>
| 4.6 | [流式响应与事件组装](reading-notes/chapter-04.md#m-04-06) | [01](chapters/01.md) · [10](chapters/10.md) · [13](chapters/13.md) |

<span id="topic-4-7"></span>
| 4.7 | [Claude提示设计](reading-notes/chapter-04.md#m-04-07) | [01](chapters/01.md) · [10](chapters/10.md) · [13](chapters/13.md) |

<span id="topic-4-8"></span>
| 4.8 | [扩展推理与状态连续性](reading-notes/chapter-04.md#m-04-08) | [01](chapters/01.md) · [10](chapters/10.md) · [13](chapters/13.md) |

<span id="topic-5-1"></span>
| 5.1 | [推理、行动与观察](reading-notes/chapter-05.md#m-05-01) | [09](chapters/09.md) · [10](chapters/10.md) · [11](chapters/11.md) · [21](chapters/21.md) |

<span id="topic-5-2"></span>
| 5.2 | [构建Agent的实践方法](reading-notes/chapter-05.md#m-05-02) | [09](chapters/09.md) · [10](chapters/10.md) · [11](chapters/11.md) · [21](chapters/21.md) |

<span id="topic-5-3"></span>
| 5.3 | [Agent组件与工作流](reading-notes/chapter-05.md#m-05-03) | [09](chapters/09.md) · [10](chapters/10.md) · [11](chapters/11.md) · [21](chapters/21.md) |

<span id="topic-5-4"></span>
| 5.4 | [运行器、会话与追踪](reading-notes/chapter-05.md#m-05-04) | [09](chapters/09.md) · [10](chapters/10.md) · [11](chapters/11.md) · [21](chapters/21.md) |

<span id="topic-5-5"></span>
| 5.5 | [在训练中学习工具使用](reading-notes/chapter-05.md#m-05-05) | [09](chapters/09.md) · [10](chapters/10.md) · [11](chapters/11.md) · [21](chapters/21.md) |

<span id="topic-5-6"></span>
| 5.6 | [语言反馈与任务反思](reading-notes/chapter-05.md#m-05-06) | [09](chapters/09.md) · [10](chapters/10.md) · [11](chapters/11.md) · [21](chapters/21.md) |

<span id="topic-5-7"></span>
| 5.7 | [面向Agent设计工具](reading-notes/chapter-05.md#m-05-07) | [09](chapters/09.md) · [10](chapters/10.md) · [11](chapters/11.md) · [21](chapters/21.md) |

<span id="topic-5-8"></span>
| 5.8 | [MCP的作用与边界](reading-notes/chapter-05.md#m-05-08) | [09](chapters/09.md) · [10](chapters/10.md) · [11](chapters/11.md) · [21](chapters/21.md) |

<span id="topic-5-9"></span>
| 5.9 | [MCP主机、客户端与服务器](reading-notes/chapter-05.md#m-05-09) | [09](chapters/09.md) · [10](chapters/10.md) · [11](chapters/11.md) · [21](chapters/21.md) |

<span id="topic-5-10"></span>
| 5.10 | [通过代码组合工具](reading-notes/chapter-05.md#m-05-10) | [09](chapters/09.md) · [10](chapters/10.md) · [11](chapters/11.md) · [21](chapters/21.md) |

<span id="topic-5-11"></span>
| 5.11 | [检查点、恢复与状态持久化](reading-notes/chapter-05.md#m-05-11) | [09](chapters/09.md) · [10](chapters/10.md) · [11](chapters/11.md) · [21](chapters/21.md) |

<span id="topic-5-12"></span>
| 5.12 | [跨Agent通信协议](reading-notes/chapter-05.md#m-05-12) | [09](chapters/09.md) · [10](chapters/10.md) · [11](chapters/11.md) · [21](chapters/21.md) |

<span id="topic-6-1"></span>
| 6.1 | [Codex输入组装与执行循环](reading-notes/chapter-06.md#m-06-01) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-2"></span>
| 6.2 | [Codex App Server与会话原语](reading-notes/chapter-06.md#m-06-02) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-3"></span>
| 6.3 | [面向Agent的工程环境](reading-notes/chapter-06.md#m-06-03) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-4"></span>
| 6.4 | [如何阅读Codex的公开实现](reading-notes/chapter-06.md#m-06-04) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-5"></span>
| 6.5 | [托管Harness的职责边界](reading-notes/chapter-06.md#m-06-05) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-6"></span>
| 6.6 | [Claude Code工作机制](reading-notes/chapter-06.md#m-06-06) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-7"></span>
| 6.7 | [Claude Code的上下文组成](reading-notes/chapter-06.md#m-06-07) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-8"></span>
| 6.8 | [项目指令与自动记忆](reading-notes/chapter-06.md#m-06-08) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-9"></span>
| 6.9 | [子Agent的隔离与权限](reading-notes/chapter-06.md#m-06-09) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-10"></span>
| 6.10 | [Claude Code技能扩展](reading-notes/chapter-06.md#m-06-10) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-11"></span>
| 6.11 | [执行节点与Hooks](reading-notes/chapter-06.md#m-06-11) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-12"></span>
| 6.12 | [Claude Code权限控制](reading-notes/chapter-06.md#m-06-12) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-13"></span>
| 6.13 | [有效的编码任务组织](reading-notes/chapter-06.md#m-06-13) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-14"></span>
| 6.14 | [Copilot CLI的执行环境](reading-notes/chapter-06.md#m-06-14) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-15"></span>
| 6.15 | [Copilot自定义Agent](reading-notes/chapter-06.md#m-06-15) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-16"></span>
| 6.16 | [Copilot CLI的任务流程](reading-notes/chapter-06.md#m-06-16) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-17"></span>
| 6.17 | [区分五种定制机制](reading-notes/chapter-06.md#m-06-17) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-18"></span>
| 6.18 | [Copilot技能加载](reading-notes/chapter-06.md#m-06-18) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-19"></span>
| 6.19 | [Copilot记忆与证据](reading-notes/chapter-06.md#m-06-19) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-20"></span>
| 6.20 | [插件的组合与分发](reading-notes/chapter-06.md#m-06-20) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-6-21"></span>
| 6.21 | [程序化调用与工具访问](reading-notes/chapter-06.md#m-06-21) | [12](chapters/12.md) · [13](chapters/13.md) · [14](chapters/14.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-7-1"></span>
| 7.1 | [有效的上下文工程](reading-notes/chapter-07.md#m-07-01) | [07](chapters/07.md) · [13](chapters/13.md) · [14](chapters/14.md) |

<span id="topic-7-2"></span>
| 7.2 | [长上下文中的位置效应](reading-notes/chapter-07.md#m-07-02) | [07](chapters/07.md) · [13](chapters/13.md) · [14](chapters/14.md) |

<span id="topic-7-3"></span>
| 7.3 | [上下文容量与状态](reading-notes/chapter-07.md#m-07-03) | [07](chapters/07.md) · [13](chapters/13.md) · [14](chapters/14.md) |

<span id="topic-7-4"></span>
| 7.4 | [长上下文多任务评测](reading-notes/chapter-07.md#m-07-04) | [07](chapters/07.md) · [13](chapters/13.md) · [14](chapters/14.md) |

<span id="topic-7-5"></span>
| 7.5 | [标称窗口与有效能力](reading-notes/chapter-07.md#m-07-05) | [07](chapters/07.md) · [13](chapters/13.md) · [14](chapters/14.md) |

<span id="topic-7-6"></span>
| 7.6 | [不透明压缩状态与连续执行](reading-notes/chapter-07.md#m-07-06) | [07](chapters/07.md) · [13](chapters/13.md) · [14](chapters/14.md) |

<span id="topic-7-7"></span>
| 7.7 | [摘要型压缩概览](reading-notes/chapter-07.md#m-07-07) | [07](chapters/07.md) · [13](chapters/13.md) · [14](chapters/14.md) |

<span id="topic-7-8"></span>
| 7.8 | [主动压缩与阶段边界](reading-notes/chapter-07.md#m-07-08) | [07](chapters/07.md) · [13](chapters/13.md) · [14](chapters/14.md) |

<span id="topic-7-9"></span>
| 7.9 | [工具结果清理](reading-notes/chapter-07.md#m-07-09) | [07](chapters/07.md) · [13](chapters/13.md) · [14](chapters/14.md) |

<span id="topic-7-10"></span>
| 7.10 | [按阈值触发压缩](reading-notes/chapter-07.md#m-07-10) | [07](chapters/07.md) · [13](chapters/13.md) · [14](chapters/14.md) |

<span id="topic-7-11"></span>
| 7.11 | [缓存与压缩的相互作用](reading-notes/chapter-07.md#m-07-11) | [07](chapters/07.md) · [13](chapters/13.md) · [14](chapters/14.md) |

<span id="topic-8-1"></span>
| 8.1 | [检索增强生成的基础](reading-notes/chapter-08.md#m-08-01) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-2"></span>
| 8.2 | [上下文增强的混合检索](reading-notes/chapter-08.md#m-08-02) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-3"></span>
| 8.3 | [倒数排名融合RRF](reading-notes/chapter-08.md#m-08-03) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-4"></span>
| 8.4 | [稠密段落检索DPR](reading-notes/chapter-08.md#m-08-04) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-5"></span>
| 8.5 | [晚交互与多向量检索](reading-notes/chapter-08.md#m-08-05) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-6"></span>
| 8.6 | [假设文档辅助检索](reading-notes/chapter-08.md#m-08-06) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-7"></span>
| 8.7 | [树状摘要索引](reading-notes/chapter-08.md#m-08-07) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-8"></span>
| 8.8 | [代码搜索语法](reading-notes/chapter-08.md#m-08-08) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-9"></span>
| 8.9 | [精确搜索与范围控制](reading-notes/chapter-08.md#m-08-09) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-10"></span>
| 8.10 | [语法树与增量解析](reading-notes/chapter-08.md#m-08-10) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-11"></span>
| 8.11 | [定义、引用与语言服务](reading-notes/chapter-08.md#m-08-11) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-12"></span>
| 8.12 | [仓库级迭代检索与生成](reading-notes/chapter-08.md#m-08-12) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-13"></span>
| 8.13 | [仓库级补全评测](reading-notes/chapter-08.md#m-08-13) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-14"></span>
| 8.14 | [代码语义搜索数据集](reading-notes/chapter-08.md#m-08-14) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-15"></span>
| 8.15 | [异构检索评测](reading-notes/chapter-08.md#m-08-15) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-8-16"></span>
| 8.16 | [排序检索指标](reading-notes/chapter-08.md#m-08-16) | [15](chapters/15.md) · [16](chapters/16.md) · [17](chapters/17.md) |

<span id="topic-9-1"></span>
| 9.1 | [语言Agent的认知架构](reading-notes/chapter-09.md#m-09-01) | [14](chapters/14.md) · [18](chapters/18.md) |

<span id="topic-9-2"></span>
| 9.2 | [分层记忆与上下文换入换出](reading-notes/chapter-09.md#m-09-02) | [14](chapters/14.md) · [18](chapters/18.md) |

<span id="topic-9-3"></span>
| 9.3 | [长期记忆的类型与命名空间](reading-notes/chapter-09.md#m-09-03) | [14](chapters/14.md) · [18](chapters/18.md) |

<span id="topic-9-4"></span>
| 9.4 | [会话状态与长期Store](reading-notes/chapter-09.md#m-09-04) | [14](chapters/14.md) · [18](chapters/18.md) |

<span id="topic-9-5"></span>
| 9.5 | [记忆流、反思与计划](reading-notes/chapter-09.md#m-09-05) | [14](chapters/14.md) · [18](chapters/18.md) |

<span id="topic-9-6"></span>
| 9.6 | [长期互动记忆评测](reading-notes/chapter-09.md#m-09-06) | [14](chapters/14.md) · [18](chapters/18.md) |

<span id="topic-9-7"></span>
| 9.7 | [超长会话中的记忆能力](reading-notes/chapter-09.md#m-09-07) | [14](chapters/14.md) · [18](chapters/18.md) |

<span id="topic-9-8"></span>
| 9.8 | [动态关联的记忆组织](reading-notes/chapter-09.md#m-09-08) | [14](chapters/14.md) · [18](chapters/18.md) |

<span id="topic-9-9"></span>
| 9.9 | [记忆提取与更新流水线](reading-notes/chapter-09.md#m-09-09) | [14](chapters/14.md) · [18](chapters/18.md) |

<span id="topic-9-10"></span>
| 9.10 | [图结构与全局问题检索](reading-notes/chapter-09.md#m-09-10) | [14](chapters/14.md) · [18](chapters/18.md) |

<span id="topic-10-1"></span>
| 10.1 | [渐进式技能加载](reading-notes/chapter-10.md#m-10-01) | [11](chapters/11.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-10-2"></span>
| 10.2 | [技能规范与资源组织](reading-notes/chapter-10.md#m-10-02) | [11](chapters/11.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-10-3"></span>
| 10.3 | [技能选择与执行上下文](reading-notes/chapter-10.md#m-10-03) | [11](chapters/11.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-10-4"></span>
| 10.4 | [Copilot技能的适用范围](reading-notes/chapter-10.md#m-10-04) | [11](chapters/11.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-10-5"></span>
| 10.5 | [Codex技能加载与使用](reading-notes/chapter-10.md#m-10-05) | [11](chapters/11.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-10-6"></span>
| 10.6 | [选择正确的扩展层](reading-notes/chapter-10.md#m-10-06) | [11](chapters/11.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-10-7"></span>
| 10.7 | [主Agent与并行研究者](reading-notes/chapter-10.md#m-10-07) | [11](chapters/11.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-10-8"></span>
| 10.8 | [工作流、并行与动态编排](reading-notes/chapter-10.md#m-10-08) | [11](chapters/11.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-10-9"></span>
| 10.9 | [控制权交接](reading-notes/chapter-10.md#m-10-09) | [11](chapters/11.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-10-10"></span>
| 10.10 | [Agent配置与作为工具调用](reading-notes/chapter-10.md#m-10-10) | [11](chapters/11.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-10-11"></span>
| 10.11 | [简单流程作为强基线](reading-notes/chapter-10.md#m-10-11) | [11](chapters/11.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-10-12"></span>
| 10.12 | [多Agent对话框架](reading-notes/chapter-10.md#m-10-12) | [11](chapters/11.md) · [19](chapters/19.md) · [20](chapters/20.md) |

<span id="topic-11-1"></span>
| 11.1 | [跨上下文持续开发](reading-notes/chapter-11.md#m-11-01) | [21](chapters/21.md) · [22](chapters/22.md) · [26](chapters/26.md) |

<span id="topic-11-2"></span>
| 11.2 | [长应用开发的反馈结构](reading-notes/chapter-11.md#m-11-02) | [21](chapters/21.md) · [22](chapters/22.md) · [26](chapters/26.md) |

<span id="topic-11-3"></span>
| 11.3 | [面向Agent的计算机接口](reading-notes/chapter-11.md#m-11-03) | [21](chapters/21.md) · [22](chapters/22.md) · [26](chapters/26.md) |

<span id="topic-11-4"></span>
| 11.4 | [代码审查的目的与流程](reading-notes/chapter-11.md#m-11-04) | [21](chapters/21.md) · [22](chapters/22.md) · [26](chapters/26.md) |

<span id="topic-11-5"></span>
| 11.5 | [并行Agent构建编译器案例](reading-notes/chapter-11.md#m-11-05) | [21](chapters/21.md) · [22](chapters/22.md) · [26](chapters/26.md) |

<span id="topic-11-6"></span>
| 11.6 | [使用Agent进行代码审查](reading-notes/chapter-11.md#m-11-06) | [21](chapters/21.md) · [22](chapters/22.md) · [26](chapters/26.md) |

<span id="topic-11-7"></span>
| 11.7 | [审查标准与非完美交付](reading-notes/chapter-11.md#m-11-07) | [21](chapters/21.md) · [22](chapters/22.md) · [26](chapters/26.md) |

<span id="topic-11-8"></span>
| 11.8 | [设计、功能、复杂度与测试](reading-notes/chapter-11.md#m-11-08) | [21](chapters/21.md) · [22](chapters/22.md) · [26](chapters/26.md) |

<span id="topic-11-9"></span>
| 11.9 | [测试金字塔](reading-notes/chapter-11.md#m-11-09) | [21](chapters/21.md) · [22](chapters/22.md) · [26](chapters/26.md) |

<span id="topic-11-10"></span>
| 11.10 | [持续集成与反馈速度](reading-notes/chapter-11.md#m-11-10) | [21](chapters/21.md) · [22](chapters/22.md) · [26](chapters/26.md) |

<span id="topic-11-11"></span>
| 11.11 | [记录架构决策及其条件](reading-notes/chapter-11.md#m-11-11) | [21](chapters/21.md) · [22](chapters/22.md) · [26](chapters/26.md) |

<span id="topic-11-12"></span>
| 11.12 | [编码Agent质量回退复盘](reading-notes/chapter-11.md#m-11-12) | [21](chapters/21.md) · [22](chapters/22.md) · [26](chapters/26.md) |

<span id="topic-11-13"></span>
| 11.13 | [推理与执行环境解耦](reading-notes/chapter-11.md#m-11-13) | [21](chapters/21.md) · [22](chapters/22.md) · [26](chapters/26.md) |

<span id="topic-12-1"></span>
| 12.1 | [Agent评测的完整方法](reading-notes/chapter-12.md#m-12-01) | [23](chapters/23.md) · [27](chapters/27.md) |

<span id="topic-12-2"></span>
| 12.2 | [工作流评测](reading-notes/chapter-12.md#m-12-02) | [23](chapters/23.md) · [27](chapters/27.md) |

<span id="topic-12-3"></span>
| 12.3 | [执行轨迹评分](reading-notes/chapter-12.md#m-12-03) | [23](chapters/23.md) · [27](chapters/27.md) |

<span id="topic-12-4"></span>
| 12.4 | [持续评测学习框架](reading-notes/chapter-12.md#m-12-04) | [23](chapters/23.md) · [27](chapters/27.md) |

<span id="topic-12-5"></span>
| 12.5 | [数据集与评分标准](reading-notes/chapter-12.md#m-12-05) | [23](chapters/23.md) · [27](chapters/27.md) |

<span id="topic-12-6"></span>
| 12.6 | [模型评委与评分偏差](reading-notes/chapter-12.md#m-12-06) | [23](chapters/23.md) · [27](chapters/27.md) |

<span id="topic-12-7"></span>
| 12.7 | [真实Issue修复基准](reading-notes/chapter-12.md#m-12-07) | [23](chapters/23.md) · [27](chapters/27.md) |

<span id="topic-12-8"></span>
| 12.8 | [评测环境与任务变体](reading-notes/chapter-12.md#m-12-08) | [23](chapters/23.md) · [27](chapters/27.md) |

<span id="topic-12-9"></span>
| 12.9 | [基础设施噪声与比较偏差](reading-notes/chapter-12.md#m-12-09) | [23](chapters/23.md) · [27](chapters/27.md) |

<span id="topic-12-10"></span>
| 12.10 | [跨环境Agent评测](reading-notes/chapter-12.md#m-12-10) | [23](chapters/23.md) · [27](chapters/27.md) |

<span id="topic-12-11"></span>
| 12.11 | [规则、工具和重复成功率](reading-notes/chapter-12.md#m-12-11) | [23](chapters/23.md) · [27](chapters/27.md) |

<span id="topic-12-12"></span>
| 12.12 | [时间更新与污染控制](reading-notes/chapter-12.md#m-12-12) | [23](chapters/23.md) · [27](chapters/27.md) |

<span id="topic-12-13"></span>
| 12.13 | [通用助手的综合任务](reading-notes/chapter-12.md#m-12-13) | [23](chapters/23.md) · [27](chapters/27.md) |

<span id="topic-13-1"></span>
| 13.1 | [LLM应用风险类别](reading-notes/chapter-13.md#m-13-01) | [11](chapters/11.md) · [21](chapters/21.md) · [24](chapters/24.md) |

<span id="topic-13-2"></span>
| 13.2 | [Agent应用风险类别](reading-notes/chapter-13.md#m-13-02) | [11](chapters/11.md) · [21](chapters/21.md) · [24](chapters/24.md) |

<span id="topic-13-3"></span>
| 13.3 | [特权指令与不可信内容](reading-notes/chapter-13.md#m-13-03) | [11](chapters/11.md) · [21](chapters/21.md) · [24](chapters/24.md) |

<span id="topic-13-4"></span>
| 13.4 | [提示注入攻击模型](reading-notes/chapter-13.md#m-13-04) | [11](chapters/11.md) · [21](chapters/21.md) · [24](chapters/24.md) |

<span id="topic-13-5"></span>
| 13.5 | [通过外部内容间接注入](reading-notes/chapter-13.md#m-13-05) | [11](chapters/11.md) · [21](chapters/21.md) · [24](chapters/24.md) |

<span id="topic-13-6"></span>
| 13.6 | [文件系统与网络隔离](reading-notes/chapter-13.md#m-13-06) | [11](chapters/11.md) · [21](chapters/21.md) · [24](chapters/24.md) |

<span id="topic-13-7"></span>
| 13.7 | [自动批准的误拦与漏拦](reading-notes/chapter-13.md#m-13-07) | [11](chapters/11.md) · [21](chapters/21.md) · [24](chapters/24.md) |

<span id="topic-13-8"></span>
| 13.8 | [不同产品中的隔离边界](reading-notes/chapter-13.md#m-13-08) | [11](chapters/11.md) · [21](chapters/21.md) · [24](chapters/24.md) |

<span id="topic-13-9"></span>
| 13.9 | [安全治理与威胁建模](reading-notes/chapter-13.md#m-13-09) | [11](chapters/11.md) · [21](chapters/21.md) · [24](chapters/24.md) |

<span id="topic-13-10"></span>
| 13.10 | [权限规则和任务风险](reading-notes/chapter-13.md#m-13-10) | [11](chapters/11.md) · [21](chapters/21.md) · [24](chapters/24.md) |

<span id="topic-14-1"></span>
| 14.1 | [模型、工具和交接追踪](reading-notes/chapter-14.md#m-14-01) | [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-14-2"></span>
| 14.2 | [生成式AI的语义约定](reading-notes/chapter-14.md#m-14-02) | [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-14-3"></span>
| 14.3 | [模型与Agent的Span](reading-notes/chapter-14.md#m-14-03) | [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-14-4"></span>
| 14.4 | [监控系统的信号选择](reading-notes/chapter-14.md#m-14-04) | [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-14-5"></span>
| 14.5 | [服务目标与错误预算](reading-notes/chapter-14.md#m-14-05) | [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-14-6"></span>
| 14.6 | [部署前的工程检查](reading-notes/chapter-14.md#m-14-06) | [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-14-7"></span>
| 14.7 | [限流、退避与预算](reading-notes/chapter-14.md#m-14-07) | [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-14-8"></span>
| 14.8 | [端到端任务延迟](reading-notes/chapter-14.md#m-14-08) | [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-14-9"></span>
| 14.9 | [执行状态与模型运行的解耦](reading-notes/chapter-14.md#m-14-09) | [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-14-10"></span>
| 14.10 | [提示、评测与模型优化](reading-notes/chapter-14.md#m-14-10) | [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-14-11"></span>
| 14.11 | [工具组合与成本边界](reading-notes/chapter-14.md#m-14-11) | [08](chapters/08.md) · [25](chapters/25.md) |

<span id="topic-15-1"></span>
| 15.1 | [低秩参数适配](reading-notes/chapter-15.md#m-15-01) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-2"></span>
| 15.2 | [量化模型上的高效微调](reading-notes/chapter-15.md#m-15-02) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-3"></span>
| 15.3 | [激活感知权重量化](reading-notes/chapter-15.md#m-15-03) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-4"></span>
| 15.4 | [知识蒸馏](reading-notes/chapter-15.md#m-15-04) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-5"></span>
| 15.5 | [参数高效微调的工程组织](reading-notes/chapter-15.md#m-15-05) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-6"></span>
| 15.6 | [事实性与模仿错误观念](reading-notes/chapter-15.md#m-15-06) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-7"></span>
| 15.7 | [置信度与校准](reading-notes/chapter-15.md#m-15-07) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-8"></span>
| 15.8 | [按需检索与自我评价](reading-notes/chapter-15.md#m-15-08) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-9"></span>
| 15.9 | [检索证据不足时的纠正](reading-notes/chapter-15.md#m-15-09) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-10"></span>
| 15.10 | [计算机操作的观察行动循环](reading-notes/chapter-15.md#m-15-10) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-11"></span>
| 15.11 | [截图、坐标和操作反馈](reading-notes/chapter-15.md#m-15-11) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-12"></span>
| 15.12 | [真实桌面任务评测](reading-notes/chapter-15.md#m-15-12) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-13"></span>
| 15.13 | [图形界面定位](reading-notes/chapter-15.md#m-15-13) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-14"></span>
| 15.14 | [浏览器与桌面执行环境集成](reading-notes/chapter-15.md#m-15-14) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-15"></span>
| 15.15 | [单义特征与稀疏分解](reading-notes/chapter-15.md#m-15-15) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-16"></span>
| 15.16 | [稀疏自编码器的规模与评价](reading-notes/chapter-15.md#m-15-16) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-15-17"></span>
| 15.17 | [机制可解释性的研究方法](reading-notes/chapter-15.md#m-15-17) | [06](chapters/05.md) · [26](chapters/26.md) · [27](chapters/27.md) · [28](chapters/28.md) |

<span id="topic-16-1"></span>
| 16.1 | [从自动求导到语言模型](reading-notes/chapter-16.md#m-16-01) | [01](chapters/01.md) · [28](chapters/28.md) |

<span id="topic-16-2"></span>
| 16.2 | [最小GPT训练系统](reading-notes/chapter-16.md#m-16-02) | [01](chapters/01.md) · [28](chapters/28.md) |

<span id="topic-16-3"></span>
| 16.3 | [从零训练的实践路线](reading-notes/chapter-16.md#m-16-03) | [01](chapters/01.md) · [28](chapters/28.md) |

<span id="topic-16-4"></span>
| 16.4 | [模型生态的实际使用](reading-notes/chapter-16.md#m-16-04) | [01](chapters/01.md) · [28](chapters/28.md) |

<span id="topic-16-5"></span>
| 16.5 | [数学、概率与优化基础](reading-notes/chapter-16.md#m-16-05) | [01](chapters/01.md) · [28](chapters/28.md) |

<span id="topic-16-6"></span>
| 16.6 | [张量、自动求导与模型训练](reading-notes/chapter-16.md#m-16-06) | [01](chapters/01.md) · [28](chapters/28.md) |

**阅读辅助：** [运行示例索引](worked-examples.md) · [两句话穿过模型的完整数表](worked-model.md) · [数值与状态核验](example-verification.md)

AI系统工程：从基础到内部  
[全书目录](contents.md) · [术语与符号](glossary.md) · [参考资料](sources.md)