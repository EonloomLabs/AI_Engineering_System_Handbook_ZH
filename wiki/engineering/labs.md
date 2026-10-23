---
title: "故障反例、实际结果与完整代码"
description: "AI系统工程：本地教学正文与可追溯图表"
---


<span id="eng-lab-title"></span>


# 故障反例、实际结果与完整代码

验证目标不是“程序能跑”，而是正确实现满足不变量，故意改坏后的实现能被区别出来。


<span id="lab-scope"></span>


## 本次运行范围

以下结果来自本次实际执行的69项测试：零失败、零错误、零跳过。CPU算子、临时Git／文件／数据库／进程操作和逻辑模拟明确区分。没有调用商业模型API，没有GPU性能或线上可靠性基准。

```
{
  "python": "3.13.5 (main, Jul 15 2026, 20:25:40) [GCC 14.2.0]",
  "platform": "Linux-6.18.55-x86_64-with-glibc2.41",
  "torch": "2.10.0+cpu",
  "cuda_available": false,
  "sqlite": "3.46.1",
  "pytest": "9.0.2",
  "git": "git version 2.47.3",
  "ran_at_utc": "2026-10-21T02:54:49.850270+00:00",
  "claims": "CPU and local temporary resources only; no commercial model/GPU/production service benchmarks."
}
```


<span id="lab-run"></span>


## 怎样复现

阅读本页不需要安装依赖。运行新实验需要Python、PyTorch和pytest；本次精确版本写在运行记录中。安装版本不同，首先读失败输出，不要把断言改松就当修复完成。

```
cd AI_Systems_Engineering_Textbook_ZH/engineering/labs
python run.py
```

程序只在临时目录创建文件、SQLite数据库、symlink和Git仓库。崩溃实验故意退出其子进程，不关闭主进程。Windows的符号链接权限与Git可用性可能不同，本次没有在Windows或macOS上验证。


<span id="lab-results"></span>


## 逐条观察与适用边界


<span id="proof-E01"></span>



<span id="topic-1"></span>


### E01 · 模板已经加了BOS，再分词一次为什么会悄悄改变任务？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E01": {
    "correct": [
      1,
      8,
      9,
      2
    ],
    "wrong": [
      1,
      1,
      8,
      9,
      2,
      2
    ],
    "scope": "teaching token list, not HF tokenizer"
  }
}
```

[回到正文解释与反例 →](../chapters/01.md#engineering-E01)


<span id="proof-E02"></span>



<span id="topic-2"></span>


### E02 · 新增Token、绑定输出头与优化器：为什么“能查到”还不等于“能学会”？

真实PyTorch Embedding扩容教学操作；不是调用完整HF模型resize。

```
{
  "E02": {
    "before": [
      6,
      4
    ],
    "after": [
      7,
      4
    ],
    "new_id": 6
  }
}
```

[回到正文解释与反例 →](../chapters/01.md#engineering-E02)


<span id="proof-E03"></span>



<span id="topic-3"></span>


### E03 · 投影两次、缩放两次、eval仍随机：同名Attention接口的三种陷阱

真实PyTorch CPU Linear与SDPA；不含CUDA内核。

```
{
  "E03-dropout": {
    "eval_without_dropout": [
      [
        [
          [
            1.0
          ]
        ]
      ]
    ],
    "outputs_with_p_half": [
      0.5,
      2.0,
      0.5,
      1.5,
      1.0,
      1.5,
      0.5,
      1.0,
      1.0,
      1.5,
      0.5,
      0.5,
      1.0,
      1.0,
      1.0,
      2.0
    ]
  },
  "E03-linear": {
    "correct": [
      [
        5.0,
        11.0
      ]
    ],
    "wrong": [
      [
        7.0,
        10.0
      ]
    ]
  }
}
```

[回到正文解释与反例 →](../chapters/02.md#engineering-E03)


<span id="proof-E04"></span>



<span id="topic-4"></span>


### E04 · 一整行都被遮住时，减最大值为什么仍救不了softmax？

手动softmax与真实PyTorch2.10 CPU SDPA观察；全mask处理不推广到全部后端。

```
{
  "E04": {
    "finite_fill_result": [
      0.5,
      0.5
    ],
    "manual_minus_inf_nan": true,
    "native_sdpa_observed": [
      [
        [
          [
            0.0
          ]
        ]
      ]
    ],
    "scope": "native result not generalized to all backends"
  }
}
```

[回到正文解释与反例 →](../chapters/02.md#engineering-E04)


<span id="proof-E05"></span>



<span id="topic-5"></span>


### E05 · 布尔mask语义相反，加缓存后is\_causal还可能对齐错边

真实PyTorch MHA与SDPA，固定输入、掩码及投影。

```
{
  "E05-polarity": {
    "correct": [
      [
        [
          1.0,
          0.0
        ],
        [
          0.3302384614944458,
          0.6697615385055542
        ]
      ]
    ],
    "inverted": [
      [
        [
          0.0,
          1.0
        ],
        [
          0.0,
          0.0
        ]
      ]
    ]
  },
  "E05-offset": {
    "mask": [
      [
        true,
        true,
        true,
        true,
        false
      ],
      [
        true,
        true,
        true,
        true,
        true
      ]
    ],
    "correct": [
      2.5,
      3.0
    ],
    "upper_left": [
      1.0,
      1.5
    ]
  }
}
```

[回到正文解释与反例 →](../chapters/03.md#engineering-E05)


<span id="proof-E06"></span>



<span id="topic-6"></span>


### E06 · 位置编号、缓存槽位和RoPE：同叫position却不是同一个数

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E06": {
    "once": [
      6.123233995736766e-17,
      1.0
    ],
    "twice": [
      -1.0,
      1.2246467991473532e-16
    ],
    "cache_slots": [
      0,
      1,
      2,
      3,
      4
    ],
    "valid_positions": [
      0,
      1,
      2
    ]
  }
}
```

[回到正文解释与反例 →](../chapters/03.md#engineering-E06)


<span id="proof-E07"></span>



<span id="topic-7"></span>


### E07 · 给了attention\_mask，为什么右补齐生成仍可能读错logits？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E07": {
    "indices": [
      1,
      2
    ],
    "correct": [
      1,
      1
    ],
    "last_column": [
      0,
      1
    ]
  }
}
```

[回到正文解释与反例 →](../chapters/06.md#engineering-E07)


<span id="proof-E08"></span>



<span id="topic-8"></span>


### E08 · 温度、Top-p、禁词：为什么“参数都一样”也可能不是同一采样算法？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E08": {
    "p_temperature1": [
      0.6652409557748218,
      0.24472847105479764,
      0.09003057317038046
    ],
    "p_temperature2": [
      0.506480391055654,
      0.3071958857184984,
      0.1863237232258476
    ],
    "top_p": 0.6,
    "keep_before_temperature": [
      0
    ],
    "keep_after_temperature": [
      0,
      1
    ]
  }
}
```

[回到正文解释与反例 →](../chapters/06.md#engineering-E08)


<span id="proof-E09"></span>



<span id="topic-9"></span>


### E09 · 梯度累积的隐蔽偏差：平均的是批次，还是有效Token？

真实CPU autograd与cross\_entropy；DDP部分是平均规约的代数模拟，没有启动分布式训练。

```
{
  "E09-xent": {
    "full_gradient": [
      [
        0.33608508110046387,
        -0.33608511090278625
      ],
      [
        -0.21314038336277008,
        0.2131403535604477
      ]
    ],
    "sum_normalized_gradient": [
      [
        0.33608508110046387,
        -0.33608511090278625
      ],
      [
        -0.21314038336277008,
        0.2131403535604477
      ]
    ],
    "mean_of_means_gradient": [
      [
        0.06571647524833679,
        -0.06571649014949799
      ],
      [
        -0.4587741494178772,
        0.4587740898132324
      ]
    ],
    "loss": 0.8043063879013062
  },
  "E09-ddp": {
    "rank_sum_gradients": [
      2.0,
      -6.0
    ],
    "counts": [
      1,
      3
    ],
    "correct": -1.0,
    "wrong": 0.0,
    "scope": "algebra simulation; no distributed process group launched"
  },
  "E09": {
    "token_counts": [
      1,
      3
    ],
    "correct_gradient": -1.0,
    "mean_of_means_gradient": 0.0,
    "scalar_loss_counterexample": {
      "loss_sums": [
        2.0,
        3.0
      ],
      "counts": [
        1,
        3
      ],
      "correct": 1.25,
      "wrong": 1.5
    }
  }
}
```

[回到正文解释与反例 →](../chapters/04.md#engineering-E09)


<span id="proof-E10"></span>



<span id="topic-10"></span>


### E10 · 混合精度与重计算：顺序错误会让优化器悄悄走错一步

checkpoint重算调用为真实PyTorch；AMP顺序示例是数值代数，不是GPU混合精度训练。

```
{
  "E10-checkpoint": {
    "calls": 2,
    "gradient": 0.9182168245315552
  },
  "E10": {
    "correct_unscaled_clipping": 1.0,
    "wrong_clip_then_unscale": 0.01
  }
}
```

[回到正文解释与反例 →](../chapters/04.md#engineering-E10)


<span id="proof-E11"></span>



<span id="topic-11"></span>


### E11 · DPO真正比较的不是“好答案概率”，而是相对参考策略的改变量

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E11": {
    "policy_gap": 2.0,
    "reference_gap": 2.0,
    "margin": 0.0,
    "loss": 0.6931471805599453
  }
}
```

[回到正文解释与反例 →](../chapters/05.md#engineering-E11)


<span id="proof-E12"></span>



<span id="topic-12"></span>


### E12 · LoRA第一步A梯度为零，可能是设计正常，不是反传断了

真实PyTorch autograd低秩支路；未运行PEFT完整模型。

```
{
  "E12": {
    "A_gradient": [
      [
        0.0
      ],
      [
        0.0
      ]
    ],
    "B_gradient": [
      [
        -10.0,
        -10.0
      ]
    ],
    "delta_initial": [
      [
        0.0,
        0.0
      ]
    ]
  }
}
```

[回到正文解释与反例 →](../chapters/05.md#engineering-E12)


<span id="proof-E13"></span>



<span id="topic-13"></span>


### E13 · 缓存共享的两个危险：身份不完整与可变对象别名

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E13": {
    "aliased_b": [
      1,
      2,
      3,
      4
    ],
    "copy_on_write_b": [
      1,
      2,
      3
    ],
    "keys_differ": true
  }
}
```

[回到正文解释与反例 →](../chapters/07.md#engineering-E13)


<span id="proof-E14"></span>



<span id="topic-14"></span>


### E14 · 在线softmax为什么必须重标定旧累积量，而不是平均各块答案？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E14": {
    "correct": [
      1.461030113080697,
      0.5380588357249021
    ],
    "wrong_block_average": [
      0.8655292893150024,
      0.6344707106849976
    ]
  }
}
```

[回到正文解释与反例 →](../chapters/07.md#engineering-E14)


<span id="proof-E15"></span>



<span id="topic-15"></span>


### E15 · 吞吐下降但GPU很忙：可能是KV抢占重算，而不是算力不够

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E15": {
    "capacity_positions": 12,
    "before": 11,
    "after": 14,
    "requests": 3
  }
}
```

[回到正文解释与反例 →](../chapters/08.md#engineering-E15)


<span id="proof-E16"></span>



<span id="topic-16"></span>


### E16 · 推测采样拒绝草稿后，为什么不能直接按目标分布再抽一次？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E16": {
    "target": [
      0.8,
      0.2
    ],
    "draft": [
      0.2,
      0.8
    ],
    "accepted_mass": [
      0.2,
      0.2
    ],
    "rejection_mass": 0.6,
    "residual": [
      1.0,
      0.0
    ],
    "correct": [
      0.8,
      0.2
    ],
    "wrong_redraw_p": [
      0.6799999999999999,
      0.32
    ]
  }
}
```

[回到正文解释与反例 →](../chapters/08.md#engineering-E16)


<span id="proof-E17"></span>



<span id="topic-17"></span>


### E17 · 有previous\_response\_id，为什么仍可能丢失规则或工具上下文？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E17": {
    "typed_items": [
      {
        "type": "function_call",
        "call_id": "c7",
        "arguments": "{}"
      },
      {
        "type": "function_call_output",
        "call_id": "c7",
        "output": "ok"
      }
    ],
    "lossy_text_items": []
  }
}
```

[回到正文解释与反例 →](../chapters/09.md#engineering-E17)


<span id="proof-E18"></span>



<span id="topic-18"></span>


### E18 · 模型结束、工具结束、任务完成：三种“完成”不能用同一布尔值

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E18": {
    "current": {
      "epoch": 2,
      "target": "b.py"
    },
    "late": {
      "epoch": 1,
      "target": "a.py",
      "status": "ok"
    },
    "accepted": false
  }
}
```

[回到正文解释与反例 →](../chapters/09.md#engineering-E18)


<span id="proof-E19"></span>



<span id="topic-19"></span>


### E19 · 流式工具调用：UTF-8完整、JSON完整、调用完整是三件事

真实Python增量UTF-8解码与分片组装；未连接商业API流。

```
{
  "E19-status": {
    "item": {
      "arguments": "{\"path\":\"a.py\"}",
      "done": true,
      "response_status": "incomplete"
    },
    "execute": false,
    "scope": "conservative local policy; actual protocol contract still required"
  },
  "E19": {
    "byte_count": 14,
    "unicode_length": 12,
    "assembled": {
      "a": "{\"x\":1}",
      "b": "{\"y\":2}"
    }
  }
}
```

[回到正文解释与反例 →](../chapters/10.md#engineering-E19)


<span id="proof-E20"></span>



<span id="topic-20"></span>


### E20 · 严格JSON为什么仍不能直接驱动数据库写入？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E20": {
    "missing_field_valid": false,
    "null_field_valid": true,
    "unauthorized_path_executable": false
  }
}
```

[回到正文解释与反例 →](../chapters/10.md#engineering-E20)


<span id="proof-E21"></span>



<span id="topic-21"></span>


### E21 · MCP能连接却少了工具：初始化、分页和错误层级怎样逐项查？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E21": {
    "first_page": [
      "read"
    ],
    "all": [
      "read",
      "write"
    ]
  }
}
```

[回到正文解释与反例 →](../chapters/11.md#engineering-E21)


<span id="proof-E22"></span>



<span id="topic-22"></span>


### E22 · 令牌受众、权限范围与会话ID：三种“凭证”不能互相替代

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E22": {
    "audience": "service-A",
    "resource": "service-B",
    "accepted": false
  }
}
```

[回到正文解释与反例 →](../chapters/11.md#engineering-E22)


<span id="proof-E23"></span>



<span id="topic-23"></span>


### E23 · Codex源码追问：注册、可见、可达、获授权为什么要分四步？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E23": {
    "registered": [
      "read",
      "write"
    ],
    "visible": [
      "read"
    ],
    "authorized": [
      "read"
    ],
    "scope": "illustration, not Rust integration test"
  }
}
```

[回到正文解释与反例 →](../chapters/12.md#engineering-E23)


<span id="proof-E24"></span>



<span id="topic-24"></span>


### E24 · 同样叫子Agent，为什么Claude与Copilot的“继承”不能凭感觉？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E24": {
    "omitted": [
      "read",
      "write"
    ],
    "empty": [],
    "unknown": [],
    "scope": "documented Copilot rule modeled locally"
  }
}
```

[回到正文解释与反例 →](../chapters/12.md#engineering-E24)


<span id="proof-E25"></span>



<span id="topic-25"></span>


### E25 · 语义没变却缓存失效：精确前缀、工具规格与动态字段怎样相互影响？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E25": {
    "semantically_equal": true,
    "byte_identical": false
  }
}
```

[回到正文解释与反例 →](../chapters/13.md#engineering-E25)


<span id="proof-E26"></span>



<span id="topic-26"></span>


### E26 · 上下文预算不只算已读文件：工具结果、生成与证据依赖还要预留

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E26": {
    "total": 1000,
    "static": 200,
    "reserved_generation": 200,
    "reserved_tool": 250,
    "evidence_budget": 350,
    "required_pair": 500
  }
}
```

[回到正文解释与反例 →](../chapters/13.md#engineering-E26)


<span id="proof-E27"></span>



<span id="topic-27"></span>


### E27 · 压缩结果为什么不能只留下那个“看起来最浓缩”的项目？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E27": {
    "canonical_types": [
      "message",
      "compaction"
    ],
    "lossy_types": [
      "compaction"
    ]
  }
}
```

[回到正文解释与反例 →](../chapters/14.md#engineering-E27)


<span id="proof-E28"></span>



<span id="topic-28"></span>


### E28 · 压缩期间工具结果刚好回来：一次历史替换如何丢掉真实进展？

真实SQLite双连接条件更新，与内存状态模拟；不连接生产任务。

```
{
  "E28-sql": {
    "stale_revision": 10,
    "changed_rows": 0,
    "preserved": [
      11,
      "c7 succeeded"
    ]
  },
  "E28": {
    "snapshot": 10,
    "current": 11,
    "commit_allowed": false,
    "summary": {
      "version": 10,
      "pending": [
        "c7"
      ]
    }
  }
}
```

[回到正文解释与反例 →](../chapters/14.md#engineering-E28)


<span id="proof-E29"></span>



<span id="topic-29"></span>


### E29 · 向量维度相同，为什么查询和索引仍可能根本不在一个空间？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E29": {
    "old_space_result": "A",
    "mixed_space_result": "B",
    "dimension": 2,
    "scope": "basis counterexample, not e5 inference"
  }
}
```

[回到正文解释与反例 →](../chapters/15.md#engineering-E29)


<span id="proof-E30"></span>



<span id="topic-30"></span>


### E30 · 向量查询带了WHERE，为什么仍可能返回不足k条？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E30": {
    "post_filter_top2": [],
    "eligible_top2": [
      [
        "a",
        "mine"
      ],
      [
        "b",
        "mine"
      ]
    ],
    "scope": "candidate model, not pgvector index execution"
  }
}
```

[回到正文解释与反例 →](../chapters/15.md#engineering-E30)


<span id="proof-E31"></span>



<span id="topic-31"></span>


### E31 · RRF不看原始分数，为什么重复来源仍会把排名带偏？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E31": {
    "two_independent_lists": {
      "A": 0.03252247488101534,
      "B": 0.03252247488101534
    },
    "duplicated_one_source": {
      "A": 0.04891591750396616,
      "B": 0.048651507139079855
    }
  }
}
```

[回到正文解释与反例 →](../chapters/16.md#engineering-E31)


<span id="proof-E32"></span>



<span id="topic-32"></span>


### E32 · 相关、可引用、足以支持结论：证据要过三道不同的门

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E32": {
    "evidence": {
      "tier": "pro",
      "version": 3,
      "limit": 100
    },
    "claim_scope": {
      "tier": "free",
      "version": 3
    },
    "supports": false
  }
}
```

[回到正文解释与反例 →](../chapters/16.md#engineering-E32)


<span id="proof-E33"></span>



<span id="topic-33"></span>


### E33 · 代码位置的单位错一个，编辑就可能改错字符：UTF-8、UTF-16与版本号

真实编码计数；未启动语言服务器或编辑器。

```
{
  "E33": {
    "text": "a😀b",
    "position_of_b_codepoints": 2,
    "utf16_units": 3,
    "utf8_bytes": 5
  }
}
```

[回到正文解释与反例 →](../chapters/17.md#engineering-E33)


<span id="proof-E34"></span>



<span id="topic-34"></span>


### E34 · HEAD没变为什么证据已经过期？工作树、未保存buffer与索引快照

真实临时Git仓库和工作树；未操作用户仓库。

```
{
  "E34-git": {
    "same_head": true,
    "diff": "diff --git a/a.py b/a.py\nindex bafc5d9..7a56633 100644\n--- a/a.py\n+++ b/a.py\n@@ -1 +1 @@\n-x=1\n+x=2",
    "scope": "actual local temporary Git repository"
  },
  "E34": {
    "head": "same-commit",
    "old_hash": "0e587b1d65d6bb203adbe6b9d1d0fbd820d1bba03ea0d54e1bc61585dcbd5458",
    "new_hash": "eb55118f6a7e3d350d3e51189c6d475f85d53e79a4c0f9542b36f48a34ed69e2",
    "scope": "actual file edit; Git HEAD represented by fixed label"
  }
}
```

[回到正文解释与反例 →](../chapters/17.md#engineering-E34)


<span id="proof-E35"></span>



<span id="topic-35"></span>


### E35 · “什么时候是真的”与“什么时候知道的”：记忆时间必须拆开

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E35": {
    "at_day6_known_day6": 10,
    "at_day6_known_day9": 20
  }
}
```

[回到正文解释与反例 →](../chapters/18.md#engineering-E35)


<span id="proof-E36"></span>



<span id="topic-36"></span>


### E36 · 删掉原文不等于遗忘：摘要、缓存与经验条目也有依赖

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E36": {
    "invalidated": [
      "answer_cache",
      "chunk",
      "doc",
      "memory",
      "summary"
    ]
  }
}
```

[回到正文解释与反例 →](../chapters/18.md#engineering-E36)


<span id="proof-E37"></span>



<span id="topic-37"></span>


### E37 · Skill未生效时，为什么反复改description常常改错层？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E37": {
    "exists": true,
    "discovered": true,
    "selected": false,
    "body_loaded": false,
    "used": false
  }
}
```

[回到正文解释与反例 →](../chapters/19.md#engineering-E37)


<span id="proof-E38"></span>



<span id="topic-38"></span>


### E38 · 小模型加回退真的省钱吗？关键在错误能否被发现

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E38": {
    "cheap_cost": 1.0,
    "fallback_cost": 5.0,
    "rate": 0.4,
    "expected_cost": 3.0,
    "synthetic": true
  }
}
```

[回到正文解释与反例 →](../chapters/19.md#engineering-E38)


<span id="proof-E39"></span>



<span id="topic-39"></span>


### E39 · 两个人改不同文件，为什么合并后仍会坏？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E39": {
    "producer_key": "timeout_ms",
    "consumer_key": "timeout_s",
    "text_overlap": false,
    "integration_fails": true
  }
}
```

[回到正文解释与反例 →](../chapters/20.md#engineering-E39)


<span id="proof-E40"></span>



<span id="topic-40"></span>


### E40 · 两个审查Agent都通过，为什么不能把错误率直接相乘？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E40": {
    "observed_joint": 0.2,
    "independence_guess": 0.04000000000000001,
    "synthetic": true
  }
}
```

[回到正文解释与反例 →](../chapters/20.md#engineering-E40)


<span id="proof-E41"></span>



<span id="topic-41"></span>


### E41 · 外部动作成功、日志没来得及确认：为什么本地事务无法保证只执行一次？

真实子进程退出码17、两个SQLite文件与稳定幂等键；下游是本地模拟服务，不是外部支付或业务系统。

```
{
  "E41": {
    "crash_exit": 17,
    "unsafe_effects": 2,
    "keyed_effects": 1,
    "scope": "two local SQLite stores + actual subprocess os._exit; not network service"
  }
}
```

[回到正文解释与反例 →](../chapters/21.md#engineering-E41)


<span id="proof-E42"></span>



<span id="topic-42"></span>


### E42 · 三层各重试三次，为什么最底层会被打27次？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E42": {
    "per_layer_attempts": [
      3,
      3,
      3
    ],
    "max_leaf_calls": 27
  },
  "E42-key": {
    "reuse_allowed": false
  }
}
```

[回到正文解释与反例 →](../chapters/21.md#engineering-E42)


<span id="proof-E43"></span>



<span id="topic-43"></span>


### E43 · 测试命令退出0，为什么仍可能一条有效测试都没做？

真实pytest子进程：未收集测试与全部skip；未执行用户代码。

```
{
  "E43": {
    "no_tests_exit": 5,
    "all_skip_exit": 0,
    "all_skip_output": "s                                                                        [100%]\n1 skipped in 0.00s"
  }
}
```

[回到正文解释与反例 →](../chapters/22.md#engineering-E43)


<span id="proof-E44"></span>



<span id="topic-44"></span>


### E44 · 快照看着没变不等于性质没坏：怎样让测试能杀死错误实现？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E44": {
    "weak_inputs": [
      1,
      2
    ],
    "mutant_survives": true,
    "strong_inputs": [
      -1,
      0,
      1
    ],
    "mutant_killed": true
  }
}
```

[回到正文解释与反例 →](../chapters/22.md#engineering-E44)


<span id="proof-E45"></span>



<span id="topic-45"></span>


### E45 · 成功率涨了几个点，为什么还不能宣布优化有效？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E45-bootstrap": {
    "trials": 10000,
    "seed": 20261021,
    "paired_task_delta": [
      0,
      0,
      -1,
      1,
      1,
      0,
      0,
      0
    ],
    "mean": 0.125,
    "percentile_interval": [
      -0.25,
      0.5
    ],
    "scope": "teaching 8-task dataset, not population certification"
  },
  "E45": {
    "old": [
      1,
      1,
      1,
      0,
      0,
      0,
      1,
      0
    ],
    "new": [
      1,
      1,
      0,
      1,
      1,
      0,
      1,
      0
    ],
    "improvements": 2,
    "regressions": 1,
    "mean_delta": 0.125,
    "synthetic": true
  }
}
```

[回到正文解释与反例 →](../chapters/23.md#engineering-E45)


<span id="proof-E46"></span>



<span id="topic-46"></span>


### E46 · LLM裁判的盲点：换个左右顺序，冠军就变了

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E46": {
    "original_order_winner": "A",
    "swapped_order_winner": "B",
    "synthetic_judge": "always chooses left"
  }
}
```

[回到正文解释与反例 →](../chapters/23.md#engineering-E46)


<span id="proof-E47"></span>



<span id="topic-47"></span>


### E47 · 路径在允许目录下，为什么仍可能越界？symlink与检查后替换

真实临时目录symlink解析；没有执行openat2系统调用压力测试。

```
{
  "E47": {
    "lexical_inside": true,
    "resolved_inside": false,
    "read_observed": "harmless",
    "scope": "harmless temporary symlink, not race-safe sandbox implementation"
  }
}
```

[回到正文解释与反例 →](../chapters/24.md#engineering-E47)


<span id="proof-E48"></span>



<span id="topic-48"></span>


### E48 · 用户确认过一次，模型改了参数还能沿用批准吗？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E48": {
    "unchanged_accepted": true,
    "changed_accepted": false
  }
}
```

[回到正文解释与反例 →](../chapters/24.md#engineering-E48)


<span id="proof-E49"></span>



<span id="topic-49"></span>


### E49 · 墙钟、Span总时长、p95、成功成本：指标名字相似，算错就会选错优化

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E49-cost": {
    "cost_per_success": 6.0,
    "successes_only_wrong": 1.0
  },
  "E49": {
    "wall": 7.0,
    "sum_spans": 10.0,
    "mean_group_p95": 50.5,
    "pooled_p95": 100
  }
}
```

[回到正文解释与反例 →](../chapters/25.md#engineering-E49)


<span id="proof-E50"></span>



<span id="topic-50"></span>


### E50 · 只回滚模型名为什么可能越滚越乱？系统版本是一组向量

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E50-schema": {
    "v1_ms": 5000,
    "v2_ms": 5000,
    "unknown_version_rejected": true
  },
  "E50": {
    "old": {
      "model": "m1",
      "template": "t1",
      "index": "i1",
      "tools": "s1"
    },
    "new": {
      "model": "m1",
      "template": "t1",
      "index": "i2",
      "tools": "s1"
    },
    "same_model": true,
    "same_system": false
  }
}
```

[回到正文解释与反例 →](../chapters/25.md#engineering-E50)


<span id="proof-E51"></span>



<span id="topic-51"></span>


### E51 · “根据材料可退款”与“现在可以执行退款”中间还缺什么？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E51": {
    "planned_version": 7,
    "current_version": 8,
    "execute": false
  }
}
```

[回到正文解释与反例 →](../chapters/26.md#engineering-E51)


<span id="proof-E52"></span>



<span id="topic-52"></span>


### E52 · 截图坐标为什么不能直接拿去点击？缩放、DPR与页面变化

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E52": {
    "screenshot": [
      1600,
      1200
    ],
    "css_viewport": [
      800,
      600
    ],
    "pixel_point": [
      1000,
      600
    ],
    "css_point": [
      500.0,
      300.0
    ],
    "invariant": "coordinate mapping alone does not validate current DOM state"
  }
}
```

[回到正文解释与反例 →](../chapters/26.md#engineering-E52)


<span id="proof-E53"></span>



<span id="topic-53"></span>


### E53 · 只回答有把握的问题，准确率上升为何可能只是覆盖率下降？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E53": {
    "overall_accuracy": 0.5,
    "selective_accuracy": 0.8,
    "coverage": 0.5,
    "synthetic": true
  }
}
```

[回到正文解释与反例 →](../chapters/27.md#engineering-E53)


<span id="proof-E54"></span>



<span id="topic-54"></span>


### E54 · 注意力热图最亮的位置，为什么不一定是答案的主要原因？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E54": {
    "weights": [
      0.9,
      0.1
    ],
    "values": [
      0.0,
      100.0
    ],
    "contributions": [
      0.0,
      10.0
    ],
    "scope": "scalar aggregation counterexample, not real causal interpretability"
  }
}
```

[回到正文解释与反例 →](../chapters/27.md#engineering-E54)


<span id="proof-E55"></span>



<span id="topic-55"></span>


### E55 · 训练计算最优，为什么不一定是产品全生命周期最便宜？

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E55": {
    "extra_training_cost": 1000.0,
    "inference_saving": 0.01,
    "break_even_calls": 100000.0,
    "synthetic": true
  }
}
```

[回到正文解释与反例 →](../chapters/28.md#engineering-E55)


<span id="proof-E56"></span>



<span id="topic-56"></span>


### E56 · 深度排障的终点不是“换更强模型”，而是找出失效的不变量

显式输入的教学代数、数据结构或运行契约模拟；不是对应厂商产品集成或性能实测。

```
{
  "E56-mutants": {
    "killed": [
      "mean-of-means",
      "unconditional-compaction-commit",
      "cache-position-reset"
    ]
  },
  "E56": {
    "factorial": {
      "old_old": 0.6,
      "new_old": 0.6,
      "old_new": 0.6,
      "new_new": 0.9
    },
    "interaction": 0.30000000000000004,
    "synthetic": true
  }
}
```

[回到正文解释与反例 →](../chapters/28.md#engineering-E56)


<span id="delivery-validation"></span>


## 内容与阅读界面检查

新内容包含56个工程问题和8个故障案例。实际运行69项新增测试与323项原有单元测试，均通过；它们验证指定程序和反例，不证明所有模型或业务环境行为相同。

检查覆盖5类页面、390／1440／1920／2560四种视窗，以及答案展开、工程问题搜索、目录定位与原动画入口。浏览器环境禁止file与本地HTTP导航，因此以本地HTML、CSS、脚本和数据内联渲染；文件路径、锚点和单文件资源独立检查。没有声称在用户的Mac或Safari上测试。

完整核验记录保存在包内`engineering/QA.json`与`engineering/results/`。新增实验没有改动原有宽屏样式、导航脚本、数学程序和动画数据。


<span id="lab-code"></span>


## 完整代码

代码与页面结果来自相同的一次构建。这里只展开本次新增的测试程序；原有实验仍在原章节入口。代码不是生产级安全库，不应未经适配直接用于真实副作用。


<span id="code-test_engineering-py"></span>



<span id="topic-57"></span>


### test\_engineering.py

```
"""CPU/stdlib counterexamples for the Chinese engineering textbook.

No external model, GPU, cloud API, production filesystem, or vector database is used.
Each test fixes its input, compares a valid implementation with a deliberate mutant,
and records observable results. Run with: python run.py
"""
from __future__ import annotations
import codecs, hashlib, json, math, os, sqlite3, subprocess, sys, tempfile, unittest
from collections import defaultdict
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F

OBS: dict[str, dict] = {}
def record(name: str, **values):
    OBS[name] = values

def softmax(xs):
    if not xs or not any(math.isfinite(x) for x in xs):
        raise ValueError('no finite candidate')
    m = max(xs); ws = [math.exp(x-m) for x in xs]; z = sum(ws)
    return [x/z for x in ws]

def top_p(ps, cutoff):
    total = 0.; kept = []
    for i in sorted(range(len(ps)), key=lambda j: -ps[j]):
        kept.append(i); total += ps[i]
        if total >= cutoff: break
    return kept

def masked_attention(q,k,v,allowed):
    weights = F.softmax((q @ k.transpose(-2,-1))/math.sqrt(q.shape[-1])
                         + torch.where(allowed, 0., -torch.inf), dim=-1)
    return weights @ v

def online_attention(scores, values, block_size):
    # One row, no mask: each block is incorporated using the CURRENT running max.
    m = -math.inf; denominator = 0.; numerator = [0.]*len(values[0])
    for start in range(0, len(scores), block_size):
        ss=scores[start:start+block_size]; vv=values[start:start+block_size]
        next_m=max(m,max(ss)); scale=math.exp(m-next_m)
        ws=[math.exp(s-next_m) for s in ss]
        denominator=denominator*scale+sum(ws)
        numerator=[n*scale+sum(w*v[d] for w,v in zip(ws,vv))
                   for d,n in enumerate(numerator)]
        m=next_m
    return [n/denominator for n in numerator]

def rrf(rankings, k=60):
    out=defaultdict(float)
    for ranking in rankings:
        seen=set()
        for rank, identity in enumerate(ranking,1):
            if identity in seen: continue
            seen.add(identity); out[identity]+=1/(k+rank)
    return dict(out)

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,
                                    separators=(',',':')).encode()).hexdigest()

class ModelTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(12); torch.set_num_threads(1)

    def test_E01_duplicate_template_markers(self):
        # A teaching tokenizer already received the model-specific template markers.
        templated=[1,8,9,2]
        correct=templated[:]; wrong=[1]+templated+[2]
        self.assertEqual(len(correct),4); self.assertNotEqual(correct,wrong)
        self.assertEqual(wrong.count(1),2)
        record('E01',correct=correct,wrong=wrong,scope='teaching token list, not HF tokenizer')

    def test_E02_vocab_resize_is_not_width(self):
        embedding=nn.Embedding(6,4)
        with self.assertRaises(IndexError): embedding(torch.tensor([6]))
        grown=nn.Embedding(7,4)
        with torch.no_grad(): grown.weight[:6].copy_(embedding.weight)
        self.assertEqual(list(grown(torch.tensor([6])).shape),[1,4])
        self.assertTrue(torch.equal(grown.weight[:6],embedding.weight))
        record('E02',before=[6,4],after=[7,4],new_id=6)

    def test_E03_linear_storage_transpose(self):
        x=torch.tensor([[1.,2.]])
        w=torch.tensor([[1.,3.],[2.,4.]]) # teaching [in,out]
        layer=nn.Linear(2,2,bias=False)
        with torch.no_grad(): layer.weight.copy_(w.T)
        self.assertTrue(torch.equal(layer(x),x@w))
        self.assertFalse(torch.equal(layer(x),x@w.T))
        record('E03-linear',correct=layer(x).tolist(),wrong=(x@w.T).tolist())

    def test_E03_functional_dropout_ignores_module_eval(self):
        class Attention(nn.Module):
            def forward(self,q,k,v,p): return F.scaled_dot_product_attention(q,k,v,dropout_p=p)
        m=Attention().eval(); q=torch.zeros(1,1,1,2); k=torch.zeros(1,1,4,2)
        v=torch.ones(1,1,4,1)
        correct=m(q,k,v,0.0)
        torch.manual_seed(3); wrong=m(q,k,v,0.5)
        self.assertTrue(torch.equal(correct,torch.ones_like(correct)))
        # No assumption that every random seed must differ: an ensemble finds differences.
        outputs=[]
        for seed in range(16):
            torch.manual_seed(seed); outputs.append(float(m(q,k,v,0.5).item()))
        self.assertGreater(len(set(outputs)),1)
        record('E03-dropout',eval_without_dropout=correct.tolist(),outputs_with_p_half=outputs)

    def test_E04_all_masked_row_has_no_valid_distribution(self):
        finite=F.softmax(torch.tensor([-1e9,-1e9]),dim=0)
        infinite=F.softmax(torch.tensor([-torch.inf,-torch.inf]),dim=0)
        self.assertEqual(finite.tolist(),[0.5,0.5]); self.assertTrue(torch.isnan(infinite).all())
        with self.assertRaises(ValueError): softmax([-math.inf,-math.inf])
        q=torch.zeros(1,1,1,2); k=torch.zeros(1,1,2,2);v=torch.ones(1,1,2,1)
        native=F.scaled_dot_product_attention(q,k,v,attn_mask=torch.zeros(1,2,dtype=torch.bool))
        record('E04',finite_fill_result=finite.tolist(),manual_minus_inf_nan=True,
               native_sdpa_observed=native.tolist(),scope='native result not generalized to all backends')

    def test_E05_bool_mask_polarity(self):
        x=torch.tensor([[[1.,0.],[0.,1.]]]); n=nn.MultiheadAttention(2,1,batch_first=True,bias=False).eval()
        with torch.no_grad():
            n.in_proj_weight.copy_(torch.cat([torch.eye(2)]*3)); n.out_proj.weight.copy_(torch.eye(2))
        allow=torch.tensor([[True,False],[True,True]])
        mha,_=n(x,x,x,attn_mask=~allow,need_weights=False)
        q=x.unsqueeze(1)
        sdpa=F.scaled_dot_product_attention(q,q,q,attn_mask=allow).squeeze(1)
        wrong=F.scaled_dot_product_attention(q,q,q,attn_mask=~allow).squeeze(1)
        self.assertTrue(torch.allclose(mha,sdpa,atol=1e-7)); self.assertFalse(torch.allclose(sdpa,wrong))
        record('E05-polarity',correct=sdpa.tolist(),inverted=wrong.tolist())

    def test_E05_nonsquare_cache_causal_offset(self):
        # Two NEW queries after three cached positions: absolute q positions 3,4.
        q=torch.zeros(1,1,2,1); k=torch.zeros(1,1,5,1)
        v=torch.arange(1.,6.).reshape(1,1,5,1)
        allow=torch.arange(5)[None,:] <= torch.arange(3,5)[:,None]
        correct=F.scaled_dot_product_attention(q,k,v,attn_mask=allow)
        wrong=F.scaled_dot_product_attention(q,k,v,is_causal=True)
        self.assertEqual(correct.flatten().tolist(),[2.5,3.0])
        self.assertEqual(wrong.flatten().tolist(),[1.,1.5])
        record('E05-offset',mask=allow.tolist(),correct=correct.flatten().tolist(),upper_left=wrong.flatten().tolist())

    def test_E06_rope_double_rotation(self):
        def rot(x,a): return [x[0]*math.cos(a)-x[1]*math.sin(a),x[0]*math.sin(a)+x[1]*math.cos(a)]
        x=[1.,0.]; once=rot(x,math.pi/2); twice=rot(once,math.pi/2)
        self.assertAlmostEqual(once[1],1); self.assertAlmostEqual(twice[0],-1)
        record('E06',once=once,twice=twice,cache_slots=[0,1,2,3,4],valid_positions=[0,1,2])

    def test_E07_padding_last_valid_not_last_column(self):
        logits=torch.tensor([[[4.,0.],[0.,4.],[9.,0.]],[[4.,0.],[4.,0.],[0.,4.]]])
        valid=torch.tensor([[1,1,0],[1,1,1]],dtype=torch.bool)
        indices=torch.arange(3).expand_as(valid).masked_fill(~valid,-1).max(-1).values
        right=logits[torch.arange(2),indices].argmax(-1)
        wrong=logits[:,-1].argmax(-1)
        self.assertEqual(right.tolist(),[1,1]); self.assertEqual(wrong.tolist(),[0,1])
        record('E07',indices=indices.tolist(),correct=right.tolist(),last_column=wrong.tolist())

    def test_E08_top_p_temperature_noncommute(self):
        logits=[2.,1.,0.]; base=softmax(logits); warm=softmax([x/2 for x in logits])
        self.assertEqual(top_p(base,.6),[0]); self.assertEqual(top_p(warm,.6),[0,1])
        record('E08',p_temperature1=base,p_temperature2=warm,top_p=.6,
               keep_before_temperature=top_p(base,.6),keep_after_temperature=top_p(warm,.6))

    def test_E09_token_weighted_gradient_accumulation(self):
        w=torch.tensor(1.,requires_grad=True)
        a=(w*torch.tensor([1.])-torch.tensor([0.]))**2
        b=(w*torch.tensor([1.,1.,1.])-torch.tensor([2.,2.,2.]))**2
        good=(a.sum()+b.sum())/4; good.backward(); gg=w.grad.item()
        w.grad=None; bad=((w-0)**2+((w-2)**2))/2; bad.backward(); bg=w.grad.item()
        self.assertEqual(gg,-1.);self.assertEqual(bg,0.)
        record('E09',token_counts=[1,3],correct_gradient=gg,mean_of_means_gradient=bg,
               scalar_loss_counterexample={'loss_sums':[2.,3.],'counts':[1,3],'correct':1.25,'wrong':1.5})

    def test_E09_ddp_denominator_simulation(self):
        # DDP averages rank gradients: scale local SUM by world_size/global_count.
        sums=[2.,-6.]; counts=[1,3]; world=2
        corrected=sum(world*g/sum(counts) for g in sums)/world
        wrong=sum(g/n for g,n in zip(sums,counts))/world
        self.assertEqual(corrected,-1.);self.assertEqual(wrong,0.)
        record('E09-ddp',rank_sum_gradients=sums,counts=counts,correct=corrected,wrong=wrong,
               scope='algebra simulation; no distributed process group launched')

    def test_E10_clip_scaled_gradient_wrong(self):
        grad=10.;scale=100.;threshold=1.
        correct=min(grad,threshold); wrong=min(grad*scale,threshold)/scale
        self.assertEqual(correct,1.);self.assertEqual(wrong,.01)
        record('E10',correct_unscaled_clipping=correct,wrong_clip_then_unscale=wrong)

    def test_E10_checkpoint_recomputes(self):
        from torch.utils.checkpoint import checkpoint
        calls=[];x=torch.tensor([.5],requires_grad=True)
        def fn(a): calls.append('forward');return a.sin()*a
        y=checkpoint(fn,x,use_reentrant=False);y.sum().backward()
        self.assertGreater(len(calls),1)
        self.assertAlmostEqual(x.grad.item(),math.sin(.5)+.5*math.cos(.5),places=6)
        record('E10-checkpoint',calls=len(calls),gradient=x.grad.item())

    def test_E11_dpo_requires_reference_ratio(self):
        # Chosen/rejected log p each shifted by reference likelihood.
        lp_ch,lp_re=-2.,-4.;lr_ch,lr_re=-1.,-3.;beta=.1
        margin=beta*((lp_ch-lp_re)-(lr_ch-lr_re));loss=math.log1p(math.exp(-margin))
        self.assertEqual(margin,0.);self.assertAlmostEqual(loss,math.log(2))
        record('E11',policy_gap=2.,reference_gap=2.,margin=margin,loss=loss)

    def test_E12_zero_B_zero_A_gradient_first_step(self):
        # row-vector convention: x @ A @ B, zero B, nonzero A.
        x=torch.tensor([[1.,2.]])
        a=torch.tensor([[1.],[2.]],requires_grad=True)
        b=torch.tensor([[0.,0.]],requires_grad=True)
        ((x@a@b-torch.ones(1,2))**2).sum().backward()
        self.assertTrue(torch.equal(a.grad,torch.zeros_like(a)));self.assertTrue((b.grad!=0).any())
        record('E12',A_gradient=a.grad.tolist(),B_gradient=b.grad.tolist(),delta_initial=[[0.,0.]])

    def test_E13_shared_cache_mutation_and_identity(self):
        prefix=[1,2,3];a=prefix;b=prefix;a.append(4)
        self.assertEqual(b,[1,2,3,4])
        clean=[1,2,3]; a=clean.copy(); b=clean.copy();a.append(4)
        self.assertEqual(b,[1,2,3])
        base={'tokens':[1,2,3],'adapter':'a','tenant':'T1'}
        changed={**base,'adapter':'b'}
        self.assertNotEqual(digest(base),digest(changed))
        record('E13',aliased_b=prefix,copy_on_write_b=b,keys_differ=True)

    def test_E14_online_softmax_stability(self):
        scores=[1000.,1001.,1008.,1007.];v=[[1.,0.],[0.,1.],[2.,0.],[0.,2.]]
        reference=[sum(w*x[d] for w,x in zip(softmax(scores),v)) for d in range(2)]
        for size in [1,2,3,4]:
            got=online_attention(scores,v,size)
            self.assertTrue(all(abs(a-b)<1e-12 for a,b in zip(reference,got)))
        # invalid equal average of two independently normalized blocks
        wrong=[(online_attention(scores[:2],v[:2],2)[d]+online_attention(scores[2:],v[2:],2)[d])/2 for d in range(2)]
        self.assertTrue(any(abs(a-b)>.1 for a,b in zip(reference,wrong)))
        record('E14',correct=reference,wrong_block_average=wrong)

    def test_E15_token_capacity_not_request_count(self):
        cap=12;current=[4,4,3];next_lengths=[n+1 for n in current]
        self.assertLessEqual(sum(current),cap);self.assertGreater(sum(next_lengths),cap)
        record('E15',capacity_positions=cap,before=sum(current),after=sum(next_lengths),requests=3)

    def test_E16_speculative_residual_distribution(self):
        p=[.8,.2];q=[.2,.8]
        accepted=[min(a,b) for a,b in zip(p,q)]
        reject=1-sum(accepted); residual=[max(a-b,0) for a,b in zip(p,q)]
        residual=[a/sum(residual) for a in residual]
        correct=[a+reject*r for a,r in zip(accepted,residual)]
        wrong=[a+reject*t for a,t in zip(accepted,p)]
        self.assertTrue(all(abs(a-b)<1e-12 for a,b in zip(correct,p)))
        self.assertAlmostEqual(wrong[0],.68)
        record('E16',target=p,draft=q,accepted_mass=accepted,rejection_mass=reject,
               residual=residual,correct=correct,wrong_redraw_p=wrong)


class SystemTests(unittest.TestCase):
    def test_E17_history_preserves_typed_items(self):
        history=[{'type':'function_call','call_id':'c7','arguments':'{}'},
                 {'type':'function_call_output','call_id':'c7','output':'ok'}]
        text_only=[x for x in history if x['type']=='message']
        self.assertEqual(text_only,[]);self.assertEqual(history[0]['call_id'],history[1]['call_id'])
        record('E17',typed_items=history,lossy_text_items=text_only)

    def test_E18_late_result_epoch(self):
        state={'epoch':2,'target':'b.py'};result={'epoch':1,'target':'a.py','status':'ok'}
        accepted=result['epoch']==state['epoch']
        self.assertFalse(accepted);record('E18',current=state,late=result,accepted=accepted)

    def test_E19_utf8_and_interleaved_calls(self):
        payload='{"text":"爱"}'.encode(); decoder=codecs.getincrementaldecoder('utf-8')()
        parts=[decoder.decode(bytes([b])) for b in payload]+[decoder.decode(b'',final=True)]
        self.assertEqual(json.loads(''.join(parts)),{'text':'爱'})
        chunks=[('a','{"x":'),('b','{"y":'),('a','1}'),('b','2}')];buffers=defaultdict(str)
        for key,chunk in chunks: buffers[key]+=chunk
        self.assertEqual(json.loads(buffers['a']),{'x':1});self.assertEqual(json.loads(buffers['b']),{'y':2})
        with self.assertRaises(json.JSONDecodeError): json.loads(''.join(c for _,c in chunks))
        record('E19',byte_count=len(payload),unicode_length=len(payload.decode()),assembled=dict(buffers))

    def test_E19_terminal_status_gates_execution(self):
        item={'arguments':'{"path":"a.py"}','done':True,'response_status':'incomplete'}
        authorized=True
        execute=item['done'] and item['response_status']=='completed' and authorized
        self.assertFalse(execute)
        record('E19-status',item=item,execute=execute,scope='conservative local policy; actual protocol contract still required')

    def test_E20_missing_null_and_permission(self):
        def valid(x): return set(x)=={'path','note'} and isinstance(x['path'],str) and (x['note'] is None or isinstance(x['note'],str))
        self.assertFalse(valid({'path':'a.py'}));self.assertTrue(valid({'path':'secret.txt','note':None}))
        allowed={'a.py'}
        self.assertFalse('secret.txt' in allowed)
        record('E20',missing_field_valid=False,null_field_valid=True,unauthorized_path_executable=False)

    def test_E21_tool_discovery_pagination(self):
        pages={None:{'tools':['read'],'nextCursor':'p2'},'p2':{'tools':['write']}}
        cursor=None; result=[]
        while True:
            page=pages[cursor];result+=page['tools'];cursor=page.get('nextCursor')
            if cursor is None:break
        self.assertEqual(result,['read','write']);self.assertNotEqual(pages[None]['tools'],result)
        record('E21',first_page=pages[None]['tools'],all=result)

    def test_E22_audience_not_session(self):
        # This checks policy on already-verified claims, NOT JWT signature validation.
        claims={'aud':'service-A','scope':['read'],'sub':'u1'}
        accepted=claims['aud']=='service-B' and 'read' in claims['scope']
        self.assertFalse(accepted)
        record('E22',audience=claims['aud'],resource='service-B',accepted=accepted)

    def test_E23_registered_visible_executable_are_separate(self):
        registered={'read','write'};visible={'read'};authorized={'read'}
        self.assertTrue('write' in registered);self.assertFalse('write' in visible and 'write' in authorized)
        record('E23',registered=sorted(registered),visible=sorted(visible),authorized=sorted(authorized),scope='illustration, not Rust integration test')

    def test_E24_omitted_empty_tools(self):
        all_tools=['read','write']
        def resolve(value):return all_tools if value is None or value==['*'] else [x for x in value if x in all_tools]
        self.assertEqual(resolve(None),all_tools);self.assertEqual(resolve([]),[]);self.assertEqual(resolve(['typo']),[])
        record('E24',omitted=resolve(None),empty=resolve([]),unknown=resolve(['typo']),scope='documented Copilot rule modeled locally')

    def test_E25_semantics_not_exact_serialization(self):
        a='{"a":1,"b":2}';b='{"b":2,"a":1}'
        self.assertEqual(json.loads(a),json.loads(b));self.assertNotEqual(a,b)
        self.assertEqual(digest(json.loads(a)),digest(json.loads(b)))
        record('E25',semantically_equal=True,byte_identical=False)

    def test_E26_budget_dependency_closure(self):
        total=1000;static=200;generation=200;tool_future=250;available=total-static-generation-tool_future
        self.assertEqual(available,350)
        candidates={'definition':200,'implementation':300}
        self.assertGreater(sum(candidates.values()),available)
        record('E26',total=total,static=static,reserved_generation=generation,
               reserved_tool=tool_future,evidence_budget=available,required_pair=sum(candidates.values()))

    def test_E27_compacted_window_not_one_item(self):
        output=[{'type':'message','role':'user','text':'do not publish'},
                {'type':'compaction','encrypted_content':'opaque'}]
        lossy=output[-1:]
        self.assertEqual(len(lossy),1);self.assertEqual(len(output),2)
        record('E27',canonical_types=[x['type'] for x in output],lossy_types=[x['type'] for x in lossy])

    def test_E28_compaction_compare_and_swap(self):
        version=10;captured=version;summary={'version':captured,'pending':['c7']}
        version+=1 # tool completion arrived during summary generation
        committed=captured==version
        self.assertFalse(committed)
        record('E28',snapshot=captured,current=version,commit_allowed=committed,summary=summary)

    def test_E29_same_dimension_different_vector_space(self):
        docs={'A':[1.,0.],'B':[0.,1.]};q1=[1.,0.];q2=[0.,1.] # same semantics, a different encoder's basis
        choose=lambda q:max(docs,key=lambda k:sum(x*y for x,y in zip(q,docs[k])))
        self.assertEqual(choose(q1),'A');self.assertEqual(choose(q2),'B')
        record('E29',old_space_result=choose(q1),mixed_space_result=choose(q2),dimension=2,scope='basis counterexample, not e5 inference')

    def test_E30_filter_after_topk_underfills(self):
        hits=[('x1','other'),('x2','other'),('a','mine'),('b','mine')]
        post=[x for x in hits[:2] if x[1]=='mine']
        pre=[x for x in hits if x[1]=='mine'][:2]
        self.assertEqual(post,[]);self.assertEqual(len(pre),2)
        record('E30',post_filter_top2=post,eligible_top2=pre,scope='candidate model, not pgvector index execution')

    def test_E31_rrf_duplicate_evidence(self):
        a=rrf([['A','B'],['B','A']]);wrong=rrf([['A','B'],['A','B'],['B','A']])
        self.assertAlmostEqual(a['A'],a['B']);self.assertGreater(wrong['A'],wrong['B'])
        record('E31',two_independent_lists=a,duplicated_one_source=wrong)

    def test_E32_evidence_time_and_condition(self):
        evidence={'tier':'pro','version':3,'limit':100};query={'tier':'free','version':3}
        support=all(evidence[k]==query[k] for k in query)
        self.assertFalse(support);record('E32',evidence=evidence,claim_scope=query,supports=False)

    def test_E33_utf16_utf8_position(self):
        text='a😀b';before='a😀'
        self.assertEqual(len(before),2);self.assertEqual(len(before.encode('utf-16-le'))//2,3)
        self.assertEqual(len(before.encode('utf-8')),5)
        record('E33',text=text,position_of_b_codepoints=2,utf16_units=3,utf8_bytes=5)

    def test_E34_head_not_worktree(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'a.py';p.write_text('x=1\n');first=digest(p.read_text());head='same-commit'
            p.write_text('x=2\n');second=digest(p.read_text())
            self.assertNotEqual(first,second);self.assertEqual(head,'same-commit')
            record('E34',head=head,old_hash=first,new_hash=second,scope='actual file edit; Git HEAD represented by fixed label')

    def test_E35_bitemporal(self):
        events=[{'valid':1,'recorded':1,'value':10},{'valid':5,'recorded':8,'value':20}]
        def asof(valid_at,known_at):
            candidates=[e for e in events if e['valid']<=valid_at and e['recorded']<=known_at]
            return max(candidates,key=lambda x:(x['valid'],x['recorded']))['value']
        self.assertEqual(asof(6,6),10);self.assertEqual(asof(6,9),20)
        record('E35',at_day6_known_day6=10,at_day6_known_day9=20)

    def test_E36_revocation_invalidates_derived(self):
        deps={'chunk':['doc'],'summary':['chunk'],'answer_cache':['summary'],'memory':['summary']};revoked={'doc'}
        changed=True
        while changed:
            old=len(revoked);revoked|={k for k,v in deps.items() if any(x in revoked for x in v)};changed=len(revoked)!=old
        self.assertEqual(revoked,{'doc','chunk','summary','answer_cache','memory'})
        record('E36',invalidated=sorted(revoked))

    def test_E37_skill_stages(self):
        stages={'exists':True,'discovered':True,'selected':False,'body_loaded':False,'used':False}
        self.assertFalse(all(stages.values()))
        record('E37',**stages)

    def test_E38_fallback_expected_cost(self):
        cheap=1.;expensive=5.;fallback=.4
        total=cheap+fallback*expensive
        self.assertEqual(total,3.);self.assertNotEqual(total,cheap)
        record('E38',cheap_cost=cheap,fallback_cost=expensive,rate=fallback,expected_cost=total,synthetic=True)

    def test_E39_disjoint_files_semantic_conflict(self):
        producer=lambda:{'timeout_ms':5000}; consumer=lambda x:x['timeout_s']
        with self.assertRaises(KeyError):consumer(producer())
        record('E39',producer_key='timeout_ms',consumer_key='timeout_s',text_overlap=False,integration_fails=True)

    def test_E40_correlated_reviewers(self):
        failures1={1,2,3,4};failures2={1,2,3,4};n=20
        joint=len(failures1&failures2)/n;independent=(len(failures1)/n)*(len(failures2)/n)
        self.assertEqual(joint,.2);self.assertAlmostEqual(independent,.04)
        record('E40',observed_joint=joint,independence_guess=independent,synthetic=True)

    def test_E41_external_effect_before_journal_real_process(self):
        script=Path(__file__).with_name('crash_worker.py')
        with tempfile.TemporaryDirectory() as td:
            # unsafe retry: committed effect precedes the separate journal acknowledgement.
            first=subprocess.run([sys.executable,str(script),td,'unsafe','crash'],capture_output=True)
            self.assertEqual(first.returncode,17)
            second=subprocess.run([sys.executable,str(script),td,'unsafe','resume'],capture_output=True)
            self.assertEqual(second.returncode,0)
            con=sqlite3.connect(Path(td)/'external.sqlite');unsafe=con.execute('select count(*) from effects').fetchone()[0];con.close()
            self.assertEqual(unsafe,2)
        with tempfile.TemporaryDirectory() as td:
            first=subprocess.run([sys.executable,str(script),td,'keyed','crash'],capture_output=True)
            self.assertEqual(first.returncode,17)
            second=subprocess.run([sys.executable,str(script),td,'keyed','resume'],capture_output=True)
            self.assertEqual(second.returncode,0)
            con=sqlite3.connect(Path(td)/'external.sqlite');safe=con.execute('select count(*) from effects').fetchone()[0];con.close()
            self.assertEqual(safe,1)
        record('E41',crash_exit=17,unsafe_effects=unsafe,keyed_effects=safe,scope='two local SQLite stores + actual subprocess os._exit; not network service')

    def test_E42_retries_multiply(self):
        attempts=[3,3,3];self.assertEqual(math.prod(attempts),27)
        record('E42',per_layer_attempts=attempts,max_leaf_calls=27)

    def test_E42_same_key_different_intent_rejected(self):
        saved={'key':'op7','hash':digest({'path':'a','value':1})}
        changed=digest({'path':'a','value':2})
        self.assertNotEqual(saved['hash'],changed)
        record('E42-key',reuse_allowed=saved['hash']==changed)

    def test_E43_test_exitcodes(self):
        with tempfile.TemporaryDirectory() as td:
            env=dict(os.environ,PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
            empty=subprocess.run([sys.executable,'-m','pytest','-q',td],capture_output=True,text=True,env=env)
            self.assertEqual(empty.returncode,5)
            Path(td,'test_skip.py').write_text('import pytest\n@pytest.mark.skip(reason="demo")\ndef test_x():\n    assert False\n')
            skipped=subprocess.run([sys.executable,'-m','pytest','-q',td],capture_output=True,text=True,env=env)
            self.assertEqual(skipped.returncode,0);self.assertIn('skipped',skipped.stdout)
            record('E43',no_tests_exit=empty.returncode,all_skip_exit=skipped.returncode,all_skip_output=skipped.stdout.strip())

    def test_E44_mutation_test_oracle(self):
        good=lambda x: x>0;bad=lambda x: x>=0
        weak=[1,2];strong=[-1,0,1]
        self.assertTrue(all(good(x)==bad(x) for x in weak));self.assertFalse(all(good(x)==bad(x) for x in strong))
        record('E44',weak_inputs=weak,mutant_survives=True,strong_inputs=strong,mutant_killed=True)

    def test_E45_paired_deltas(self):
        old=[1,1,1,0,0,0,1,0];new=[1,1,0,1,1,0,1,0]
        improvements=sum(a==0 and b==1 for a,b in zip(old,new));regressions=sum(a==1 and b==0 for a,b in zip(old,new))
        delta=(sum(new)-sum(old))/len(old)
        self.assertEqual(improvements,2);self.assertEqual(regressions,1);self.assertEqual(delta,.125)
        record('E45',old=old,new=new,improvements=improvements,regressions=regressions,mean_delta=delta,synthetic=True)

    def test_E46_order_biased_judge(self):
        judge=lambda left,right:left
        original=judge('A','B');swapped=judge('B','A')
        self.assertNotEqual(original,swapped)
        record('E46',original_order_winner=original,swapped_order_winner=swapped,synthetic_judge='always chooses left')

    def test_E47_symlink_bypasses_lexical_check(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);inside=root/'allowed';inside.mkdir();outside=root/'outside.txt';outside.write_text('harmless')
            link=inside/'link.txt';link.symlink_to(outside)
            lexical=link.is_relative_to(inside)
            resolved=link.resolve().is_relative_to(inside.resolve())
            self.assertTrue(lexical);self.assertFalse(resolved)
            record('E47',lexical_inside=lexical,resolved_inside=resolved,read_observed=link.read_text(),scope='harmless temporary symlink, not race-safe sandbox implementation')

    def test_E48_approval_bound_to_intent(self):
        request={'user':'u','op':'write','path':'a','body':'v1','version':7,'expiry':10}
        approved=digest(request);changed={**request,'body':'v2'}
        self.assertNotEqual(approved,digest(changed));record('E48',unchanged_accepted=True,changed_accepted=False)

    def test_E49_parallel_spans_and_percentiles(self):
        wall=max(3.,5.)+2.;span_sum=3.+5.+2.
        self.assertEqual(wall,7.);self.assertEqual(span_sum,10.)
        # Nearest-rank p95 of 95 zeros and 5 hundreds is zero.
        a=[0]*95+[100]*5;b=[0]*95+[100]*5
        p95=lambda xs:sorted(xs)[math.ceil(.95*len(xs))-1]
        mixture=a+b
        self.assertEqual(p95(mixture),0)
        # Separate tenants of unequal size: averaging quantiles is not pooled quantile.
        fast=[1]*100;slow=[100]*10
        self.assertNotEqual((p95(fast)+p95(slow))/2,p95(fast+slow))
        record('E49',wall=wall,sum_spans=span_sum,mean_group_p95=50.5,pooled_p95=p95(fast+slow))

    def test_E49_cost_includes_failures(self):
        costs=[1,1,5,5];success=[1,1,0,0]
        correct=sum(costs)/sum(success);wrong=sum(c for c,s in zip(costs,success) if s)/sum(success)
        self.assertEqual(correct,6.);self.assertEqual(wrong,1.)
        record('E49-cost',cost_per_success=correct,successes_only_wrong=wrong)

    def test_E50_version_vector(self):
        old={'model':'m1','template':'t1','index':'i1','tools':'s1'};new={**old,'index':'i2'}
        self.assertEqual(old['model'],new['model']);self.assertNotEqual(digest(old),digest(new))
        record('E50',old=old,new=new,same_model=True,same_system=False)

    def test_E51_policy_rechecked_at_commit(self):
        plan_policy=7;current_policy=8;allowed_at_plan=True;allowed_at_commit=False
        execute=allowed_at_plan and plan_policy==current_policy and allowed_at_commit
        self.assertFalse(execute);record('E51',planned_version=plan_policy,current_version=current_policy,execute=execute)

    def test_E52_coordinate_scale_and_staleness(self):
        screenshot=[1600,1200];viewport=[800,600];p=[1000,600]
        css=[p[i]*viewport[i]/screenshot[i] for i in range(2)]
        self.assertEqual(css,[500.,300.]);self.assertNotEqual(css,p)
        record('E52',screenshot=screenshot,css_viewport=viewport,pixel_point=p,css_point=css,
               invariant='coordinate mapping alone does not validate current DOM state')

    def test_E53_selective_accuracy_needs_coverage(self):
        correct=[1,1,1,1,0,1,0,0,0,0];accepted=[1,1,1,1,1,0,0,0,0,0]
        selective=sum(c for c,a in zip(correct,accepted) if a)/sum(accepted)
        coverage=sum(accepted)/len(accepted)
        self.assertEqual(selective,.8);self.assertEqual(coverage,.5)
        record('E53',overall_accuracy=sum(correct)/len(correct),selective_accuracy=selective,coverage=coverage,synthetic=True)

    def test_E54_attention_high_weight_not_high_contribution(self):
        weights=[.9,.1];values=[0.,100.];contributions=[a*b for a,b in zip(weights,values)]
        self.assertEqual(contributions,[0.,10.]);record('E54',weights=weights,values=values,contributions=contributions,scope='scalar aggregation counterexample, not real causal interpretability')

    def test_E55_lifecycle_break_even(self):
        upfront=1000.;per_call_saved=.01;break_even=upfront/per_call_saved
        self.assertEqual(break_even,100000.)
        record('E55',extra_training_cost=upfront,inference_saving=per_call_saved,break_even_calls=break_even,synthetic=True)

    def test_E56_interaction_not_main_effect(self):
        table={'old_old':.6,'new_old':.6,'old_new':.6,'new_new':.9}
        interaction=table['new_new']-table['new_old']-table['old_new']+table['old_old']
        self.assertAlmostEqual(interaction,.3)
        record('E56',factorial=table,interaction=interaction,synthetic=True)

class ExtendedIntegrationTests(unittest.TestCase):
    def test_E09_actual_cross_entropy_accumulation(self):
        torch.manual_seed(9)
        features=[torch.tensor([[1.,2.]]),torch.tensor([[2.,1.],[0.,1.],[1.,0.]])]
        targets=[torch.tensor([0]),torch.tensor([1,0,1])]
        initial=torch.tensor([[.2,-.1],[.3,.4]])
        w=initial.clone().requires_grad_()
        full=F.cross_entropy(torch.cat(features)@w,torch.cat(targets),reduction='mean')
        full.backward();expected=w.grad.clone()
        w=initial.clone().requires_grad_()
        for x,y in zip(features,targets):
            (F.cross_entropy(x@w,y,reduction='sum')/4).backward()
        correct=w.grad.clone()
        w=initial.clone().requires_grad_()
        for x,y in zip(features,targets):
            (F.cross_entropy(x@w,y,reduction='mean')/2).backward()
        wrong=w.grad.clone()
        self.assertTrue(torch.allclose(expected,correct,atol=1e-7))
        self.assertFalse(torch.allclose(expected,wrong,atol=1e-4))
        record('E09-xent',full_gradient=expected.tolist(),sum_normalized_gradient=correct.tolist(),
               mean_of_means_gradient=wrong.tolist(),loss=full.item())

    def test_E28_sqlite_conditional_update_prevents_stale_summary(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'history.sqlite';a=sqlite3.connect(path);b=sqlite3.connect(path)
            a.execute('CREATE TABLE history(id INTEGER PRIMARY KEY, rev INTEGER, text TEXT)')
            a.execute("INSERT INTO history VALUES(1,10,'c7 pending')");a.commit()
            captured=a.execute('SELECT rev FROM history WHERE id=1').fetchone()[0]
            b.execute("UPDATE history SET rev=11,text='c7 succeeded' WHERE id=1");b.commit()
            cur=a.execute("UPDATE history SET rev=rev+1,text='summary: c7 pending' WHERE id=1 AND rev=?",(captured,));a.commit()
            self.assertEqual(cur.rowcount,0)
            state=a.execute('SELECT rev,text FROM history WHERE id=1').fetchone()
            self.assertEqual(state,(11,'c7 succeeded'))
            record('E28-sql',stale_revision=captured,changed_rows=cur.rowcount,preserved=list(state))
            a.close();b.close()

    def test_E34_actual_git_worktree_hash(self):
        import shutil
        if not shutil.which('git'): self.skipTest('git not installed')
        with tempfile.TemporaryDirectory() as td:
            def git(*args):return subprocess.run(['git','-C',td,*args],check=True,capture_output=True,text=True).stdout.strip()
            git('init','-q');git('config','user.name','Local Test');git('config','user.email','test@example.invalid')
            p=Path(td)/'a.py';p.write_text('x=1\n');git('add','a.py');git('commit','-qm','fixture')
            before=git('rev-parse','HEAD');p.write_text('x=2\n');after=git('rev-parse','HEAD')
            dirty=git('diff','--','a.py')
            self.assertEqual(before,after);self.assertIn('+x=2',dirty)
            record('E34-git',same_head=before==after,diff=dirty,scope='actual local temporary Git repository')

    def test_E45_paired_bootstrap_task_unit(self):
        import random
        delta=[0,0,-1,1,1,0,0,0];rng=random.Random(20261021)
        draws=sorted(sum(rng.choice(delta) for _ in delta)/len(delta) for _ in range(10000))
        interval=[draws[249],draws[9749]]
        self.assertLessEqual(interval[0],0);self.assertGreaterEqual(interval[1],0)
        record('E45-bootstrap',trials=10000,seed=20261021,paired_task_delta=delta,
               mean=sum(delta)/len(delta),percentile_interval=interval,scope='teaching 8-task dataset, not population certification')

    def test_E50_schema_rollback_compatibility(self):
        # Explicit dual-reader keeps old and new formats distinguishable, never guesses units.
        def read(v):
            if v['schema']==1:return v['timeout_seconds']*1000
            if v['schema']==2:return v['timeout_ms']
            raise ValueError('unsupported schema')
        self.assertEqual(read({'schema':1,'timeout_seconds':5}),5000)
        self.assertEqual(read({'schema':2,'timeout_ms':5000}),5000)
        with self.assertRaises(ValueError):read({'schema':3,'timeout_ms':5000})
        record('E50-schema',v1_ms=5000,v2_ms=5000,unknown_version_rejected=True)

    def test_E56_regression_mutants_are_detectable(self):
        # These deliberately broken functions must not satisfy the intended invariants.
        good_mean=lambda sums,counts:sum(sums)/sum(counts)
        bad_mean=lambda sums,counts:sum(s/n for s,n in zip(sums,counts))/len(counts)
        self.assertNotEqual(good_mean([2,3],[1,3]),bad_mean([2,3],[1,3]))
        safe_commit=lambda old,current:old==current
        bad_commit=lambda old,current:True
        self.assertNotEqual(safe_commit(10,11),bad_commit(10,11))
        correct_positions=lambda past,n:list(range(past,past+n))
        bad_positions=lambda past,n:list(range(n))
        self.assertNotEqual(correct_positions(3,2),bad_positions(3,2))
        record('E56-mutants',killed=['mean-of-means','unconditional-compaction-commit','cache-position-reset'])
```


<span id="code-crash_worker-py"></span>



<span id="topic-58"></span>


### crash\_worker.py

```
"""Two independent databases model an executor and a downstream effect store.
A deliberate os._exit occurs ONLY inside the supplied temporary directory.
"""
import json, os, sqlite3, sys
from pathlib import Path

def main():
    root=Path(sys.argv[1]).resolve(); mode=sys.argv[2]; phase=sys.argv[3]
    if mode not in {'unsafe','keyed'} or phase not in {'crash','resume'}:
        raise ValueError('invalid mode')
    external=sqlite3.connect(root/'external.sqlite')
    external.execute('CREATE TABLE IF NOT EXISTS effects(id INTEGER PRIMARY KEY, intent TEXT UNIQUE, value TEXT)')
    journal=sqlite3.connect(root/'journal.sqlite')
    journal.execute('CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, status TEXT)')
    journal.execute("INSERT OR IGNORE INTO jobs VALUES('job7','pending')");journal.commit()
    done=journal.execute("SELECT status FROM jobs WHERE id='job7'").fetchone()[0]=='done'
    if not done:
        intent=None if mode=='unsafe' else 'stable-operation-7'
        external.execute('INSERT OR IGNORE INTO effects(intent,value) VALUES(?,?)',(intent,'effect'))
        external.commit()
        if phase=='crash': os._exit(17)  # downstream committed; journal NOT acknowledged
        journal.execute("UPDATE jobs SET status='done' WHERE id='job7'");journal.commit()
    print(json.dumps({'status':'done'}))
    external.close();journal.close()
if __name__=='__main__': main()
```


<span id="code-run-py"></span>



<span id="topic-59"></span>


### run.py

```
"""Run offline tests and persist machine-readable, versioned observations."""
from __future__ import annotations
import contextlib, datetime, hashlib, io, json, platform, sqlite3, sys, unittest
from pathlib import Path
import torch
import importlib.metadata, subprocess
import test_engineering as test

def main():
    out=Path(__file__).resolve().parents[1]/'results';out.mkdir(exist_ok=True)
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test))
    env={'python':sys.version,'platform':platform.platform(),'torch':torch.__version__,
         'cuda_available':torch.cuda.is_available(),'sqlite':sqlite3.sqlite_version,
         'pytest':importlib.metadata.version('pytest'),
         'git':subprocess.run(['git','--version'],capture_output=True,text=True,check=True).stdout.strip(),
         'ran_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'claims':'CPU and local temporary resources only; no commercial model/GPU/production service benchmarks.'}
    data={'environment':env,'tests':result.testsRun,'failures':len(result.failures),
          'errors':len(result.errors),'skipped':len(result.skipped),'observations':test.OBS,
          'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}}
    (out/'run.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    (out/'test.log').write_text(stream.getvalue())
    print(stream.getvalue());print(json.dumps({k:v for k,v in data.items() if k!='observations'},ensure_ascii=False,indent=2))
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__':sys.exit(main())
```


<span id="raw-log"></span>


## 实际测试日志

```
test_E09_actual_cross_entropy_accumulation (test_engineering.ExtendedIntegrationTests.test_E09_actual_cross_entropy_accumulation) ... ok
test_E28_sqlite_conditional_update_prevents_stale_summary (test_engineering.ExtendedIntegrationTests.test_E28_sqlite_conditional_update_prevents_stale_summary) ... ok
test_E34_actual_git_worktree_hash (test_engineering.ExtendedIntegrationTests.test_E34_actual_git_worktree_hash) ... ok
test_E45_paired_bootstrap_task_unit (test_engineering.ExtendedIntegrationTests.test_E45_paired_bootstrap_task_unit) ... ok
test_E50_schema_rollback_compatibility (test_engineering.ExtendedIntegrationTests.test_E50_schema_rollback_compatibility) ... ok
test_E56_regression_mutants_are_detectable (test_engineering.ExtendedIntegrationTests.test_E56_regression_mutants_are_detectable) ... ok
test_E01_duplicate_template_markers (test_engineering.ModelTests.test_E01_duplicate_template_markers) ... ok
test_E02_vocab_resize_is_not_width (test_engineering.ModelTests.test_E02_vocab_resize_is_not_width) ... ok
test_E03_functional_dropout_ignores_module_eval (test_engineering.ModelTests.test_E03_functional_dropout_ignores_module_eval) ... ok
test_E03_linear_storage_transpose (test_engineering.ModelTests.test_E03_linear_storage_transpose) ... ok
test_E04_all_masked_row_has_no_valid_distribution (test_engineering.ModelTests.test_E04_all_masked_row_has_no_valid_distribution) ... ok
test_E05_bool_mask_polarity (test_engineering.ModelTests.test_E05_bool_mask_polarity) ... ok
test_E05_nonsquare_cache_causal_offset (test_engineering.ModelTests.test_E05_nonsquare_cache_causal_offset) ... ok
test_E06_rope_double_rotation (test_engineering.ModelTests.test_E06_rope_double_rotation) ... ok
test_E07_padding_last_valid_not_last_column (test_engineering.ModelTests.test_E07_padding_last_valid_not_last_column) ... ok
test_E08_top_p_temperature_noncommute (test_engineering.ModelTests.test_E08_top_p_temperature_noncommute) ... ok
test_E09_ddp_denominator_simulation (test_engineering.ModelTests.test_E09_ddp_denominator_simulation) ... ok
test_E09_token_weighted_gradient_accumulation (test_engineering.ModelTests.test_E09_token_weighted_gradient_accumulation) ... ok
test_E10_checkpoint_recomputes (test_engineering.ModelTests.test_E10_checkpoint_recomputes) ... ok
test_E10_clip_scaled_gradient_wrong (test_engineering.ModelTests.test_E10_clip_scaled_gradient_wrong) ... ok
test_E11_dpo_requires_reference_ratio (test_engineering.ModelTests.test_E11_dpo_requires_reference_ratio) ... ok
test_E12_zero_B_zero_A_gradient_first_step (test_engineering.ModelTests.test_E12_zero_B_zero_A_gradient_first_step) ... ok
test_E13_shared_cache_mutation_and_identity (test_engineering.ModelTests.test_E13_shared_cache_mutation_and_identity) ... ok
test_E14_online_softmax_stability (test_engineering.ModelTests.test_E14_online_softmax_stability) ... ok
test_E15_token_capacity_not_request_count (test_engineering.ModelTests.test_E15_token_capacity_not_request_count) ... ok
test_E16_speculative_residual_distribution (test_engineering.ModelTests.test_E16_speculative_residual_distribution) ... ok
test_E17_history_preserves_typed_items (test_engineering.SystemTests.test_E17_history_preserves_typed_items) ... ok
test_E18_late_result_epoch (test_engineering.SystemTests.test_E18_late_result_epoch) ... ok
test_E19_terminal_status_gates_execution (test_engineering.SystemTests.test_E19_terminal_status_gates_execution) ... ok
test_E19_utf8_and_interleaved_calls (test_engineering.SystemTests.test_E19_utf8_and_interleaved_calls) ... ok
test_E20_missing_null_and_permission (test_engineering.SystemTests.test_E20_missing_null_and_permission) ... ok
test_E21_tool_discovery_pagination (test_engineering.SystemTests.test_E21_tool_discovery_pagination) ... ok
test_E22_audience_not_session (test_engineering.SystemTests.test_E22_audience_not_session) ... ok
test_E23_registered_visible_executable_are_separate (test_engineering.SystemTests.test_E23_registered_visible_executable_are_separate) ... ok
test_E24_omitted_empty_tools (test_engineering.SystemTests.test_E24_omitted_empty_tools) ... ok
test_E25_semantics_not_exact_serialization (test_engineering.SystemTests.test_E25_semantics_not_exact_serialization) ... ok
test_E26_budget_dependency_closure (test_engineering.SystemTests.test_E26_budget_dependency_closure) ... ok
test_E27_compacted_window_not_one_item (test_engineering.SystemTests.test_E27_compacted_window_not_one_item) ... ok
test_E28_compaction_compare_and_swap (test_engineering.SystemTests.test_E28_compaction_compare_and_swap) ... ok
test_E29_same_dimension_different_vector_space (test_engineering.SystemTests.test_E29_same_dimension_different_vector_space) ... ok
test_E30_filter_after_topk_underfills (test_engineering.SystemTests.test_E30_filter_after_topk_underfills) ... ok
test_E31_rrf_duplicate_evidence (test_engineering.SystemTests.test_E31_rrf_duplicate_evidence) ... ok
test_E32_evidence_time_and_condition (test_engineering.SystemTests.test_E32_evidence_time_and_condition) ... ok
test_E33_utf16_utf8_position (test_engineering.SystemTests.test_E33_utf16_utf8_position) ... ok
test_E34_head_not_worktree (test_engineering.SystemTests.test_E34_head_not_worktree) ... ok
test_E35_bitemporal (test_engineering.SystemTests.test_E35_bitemporal) ... ok
test_E36_revocation_invalidates_derived (test_engineering.SystemTests.test_E36_revocation_invalidates_derived) ... ok
test_E37_skill_stages (test_engineering.SystemTests.test_E37_skill_stages) ... ok
test_E38_fallback_expected_cost (test_engineering.SystemTests.test_E38_fallback_expected_cost) ... ok
test_E39_disjoint_files_semantic_conflict (test_engineering.SystemTests.test_E39_disjoint_files_semantic_conflict) ... ok
test_E40_correlated_reviewers (test_engineering.SystemTests.test_E40_correlated_reviewers) ... ok
test_E41_external_effect_before_journal_real_process (test_engineering.SystemTests.test_E41_external_effect_before_journal_real_process) ... ok
test_E42_retries_multiply (test_engineering.SystemTests.test_E42_retries_multiply) ... ok
test_E42_same_key_different_intent_rejected (test_engineering.SystemTests.test_E42_same_key_different_intent_rejected) ... ok
test_E43_test_exitcodes (test_engineering.SystemTests.test_E43_test_exitcodes) ... ok
test_E44_mutation_test_oracle (test_engineering.SystemTests.test_E44_mutation_test_oracle) ... ok
test_E45_paired_deltas (test_engineering.SystemTests.test_E45_paired_deltas) ... ok
test_E46_order_biased_judge (test_engineering.SystemTests.test_E46_order_biased_judge) ... ok
test_E47_symlink_bypasses_lexical_check (test_engineering.SystemTests.test_E47_symlink_bypasses_lexical_check) ... ok
test_E48_approval_bound_to_intent (test_engineering.SystemTests.test_E48_approval_bound_to_intent) ... ok
test_E49_cost_includes_failures (test_engineering.SystemTests.test_E49_cost_includes_failures) ... ok
test_E49_parallel_spans_and_percentiles (test_engineering.SystemTests.test_E49_parallel_spans_and_percentiles) ... ok
test_E50_version_vector (test_engineering.SystemTests.test_E50_version_vector) ... ok
test_E51_policy_rechecked_at_commit (test_engineering.SystemTests.test_E51_policy_rechecked_at_commit) ... ok
test_E52_coordinate_scale_and_staleness (test_engineering.SystemTests.test_E52_coordinate_scale_and_staleness) ... ok
test_E53_selective_accuracy_needs_coverage (test_engineering.SystemTests.test_E53_selective_accuracy_needs_coverage) ... ok
test_E54_attention_high_weight_not_high_contribution (test_engineering.SystemTests.test_E54_attention_high_weight_not_high_contribution) ... ok
test_E55_lifecycle_break_even (test_engineering.SystemTests.test_E55_lifecycle_break_even) ... ok
test_E56_interaction_not_main_effect (test_engineering.SystemTests.test_E56_interaction_not_main_effect) ... ok

----------------------------------------------------------------------
Ran 69 tests in 5.371s

OK
```


<span id="regression-run"></span>


## 原有程序的本次回归

原有7组单元测试本次重新运行共323项，全部通过。它们验证相应教学程序，不构成全书事实或产品行为的零错误证明。原程序文件未修改。

```
[
  {
    "suite": "foundations",
    "command": "python -m unittest test_foundations",
    "cwd": "labs",
    "exit": 0,
    "count": 39,
    "tail": ".......................................\n----------------------------------------------------------------------\nRan 39 tests in 0.002s\n\nOK\n"
  },
  {
    "suite": "advanced",
    "command": "python -m unittest test_suite",
    "cwd": "studies/labs",
    "exit": 0,
    "count": 49,
    "tail": ".................................................\n----------------------------------------------------------------------\nRan 49 tests in 2.869s\n\nOK\n"
  },
  {
    "suite": "concepts",
    "command": "python -m unittest verify_concepts",
    "cwd": "concepts",
    "exit": 0,
    "count": 30,
    "tail": "..............................\n----------------------------------------------------------------------\nRan 30 tests in 0.001s\n\nOK\n"
  },
  {
    "suite": "visuals",
    "command": "python -m unittest test_visual",
    "cwd": "visual/labs",
    "exit": 0,
    "count": 97,
    "tail": ".................................................................................................\n----------------------------------------------------------------------\nRan 97 tests in 0.018s\n\nOK\n"
  },
  {
    "suite": "worked",
    "command": "python -m unittest engine",
    "cwd": "worked-examples",
    "exit": 0,
    "count": 34,
    "tail": "..................................\n----------------------------------------------------------------------\nRan 34 tests in 0.007s\n\nOK\n"
  },
  {
    "suite": "operators",
    "command": "python -m unittest chain_and_operators",
    "cwd": "worked-examples",
    "exit": 0,
    "count": 14,
    "tail": "..............\n----------------------------------------------------------------------\nRan 14 tests in 0.002s\n\nOK\n"
  },
  {
    "suite": "additional",
    "command": "python -m unittest additional_checks",
    "cwd": "worked-examples",
    "exit": 0,
    "count": 60,
    "tail": "............................................................\n----------------------------------------------------------------------\nRan 60 tests in 0.008s\n\nOK\n"
  }
]
```


<span id="source-digests"></span>


## 实验源文件指纹

```
{
  "test_engineering.py": "9ee81e26a2ef4e75301ecd8dc001814e148e0a8475f08e908816e1bfd2013094",
  "run.py": "c01e6983ee6a9028f0c4c203b2454cb676e25187c44102431a0236bc547b59d0",
  "crash_worker.py": "4bbe19ed20b08909c6226e0fc3a5faca980bb18f8037c2cf4400a4e455c85639"
}
```

AI系统工程：从基础到内部 · [工程深挖目录](index.md) · [依据与版本](sources.md)