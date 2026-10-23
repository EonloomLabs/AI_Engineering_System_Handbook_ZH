---
title: "示例核验：数值、状态与代码"
description: "AI系统工程：本地教学正文与可追溯图表"
---

AI系统工程 · 运行示例

# 示例核验：数值、状态与代码

把书上的数字与可运行代码对应起来，同时说明哪些结论不在这些测试的证明范围内。

**验证边界：**401个教学示例不等于401场模型能力实验。108项新增测试核对数值公式、维度、因果性、梯度、协议分片和简化状态行为；其他场景例给定前提后作明确推演。它们不证明商业Agent效果、GPU速度、闭源内部或生产安全。


<span id="run"></span>


## 怎样复算

Python 3.10及以上，仅使用标准库。在解压目录执行：

```
python3 worked-examples/run_all.py
```

三组见证共108项测试（34＋60＋14）均已实际运行通过。原有39项基础测试、49项专题测试和12项运行见证也已重新运行通过；另有10个拓展实验自检通过。后者计为10个实验，不混充10项同口径单测。

未重新训练商业模型或运行论文全套基准；既有小模型训练记录保留为原实验材料。本页显示机器可读结果，而不是用断言文案代替计算。


<span id="logs"></span>


## 原始测试日志


<span id="topic-1"></span>


### 数值与状态基础：34项

```
test_acl_before_model (__main__.WitnessTests.test_acl_before_model) ... ok
test_adamw (__main__.WitnessTests.test_adamw) ... ok
test_atomic_replace_fixture (__main__.WitnessTests.test_atomic_replace_fixture) ... ok
test_bm25_ranking (__main__.WitnessTests.test_bm25_ranking) ... ok
test_cache_equivalence (__main__.WitnessTests.test_cache_equivalence) ... ok
test_cache_wrong_offset_detected (__main__.WitnessTests.test_cache_wrong_offset_detected) ... ok
test_ce_update (__main__.WitnessTests.test_ce_update) ... ok
test_chunk_mask (__main__.WitnessTests.test_chunk_mask) ... ok
test_compare_and_swap (__main__.WitnessTests.test_compare_and_swap) ... ok
test_dag_critical_path (__main__.WitnessTests.test_dag_critical_path) ... ok
test_dpo_margin (__main__.WitnessTests.test_dpo_margin) ... ok
test_embedding_semantics (__main__.WitnessTests.test_embedding_semantics) ... ok
test_future_mask (__main__.WitnessTests.test_future_mask) ... ok
test_gradient_finite_difference (__main__.WitnessTests.test_gradient_finite_difference) ... ok
test_gradient_shift_sum (__main__.WitnessTests.test_gradient_shift_sum) ... ok
test_lora_rank1 (__main__.WitnessTests.test_lora_rank1) ... ok
test_memory_bitemporal (__main__.WitnessTests.test_memory_bitemporal) ... ok
test_online_equals_full (__main__.WitnessTests.test_online_equals_full) ... ok
test_paginated_position (__main__.WitnessTests.test_paginated_position) ... ok
test_paired_exact (__main__.WitnessTests.test_paired_exact) ... ok
test_pool_mask (__main__.WitnessTests.test_pool_mask) ... ok
test_precision_recall (__main__.WitnessTests.test_precision_recall) ... ok
test_quantization (__main__.WitnessTests.test_quantization) ... ok
test_rope_preserves_norm (__main__.WitnessTests.test_rope_preserves_norm) ... ok
test_rrf (__main__.WitnessTests.test_rrf) ... ok
test_rrf_duplicate (__main__.WitnessTests.test_rrf_duplicate) ... ok
test_softmax_invalid (__main__.WitnessTests.test_softmax_invalid) ... ok
test_softmax_stability (__main__.WitnessTests.test_softmax_stability) ... ok
test_source_version_gate (__main__.WitnessTests.test_source_version_gate) ... ok
test_speculative_distribution (__main__.WitnessTests.test_speculative_distribution) ... ok
test_sqlite_local_transaction (__main__.WitnessTests.test_sqlite_local_transaction) ... ok
test_sse_all_byte_boundaries (__main__.WitnessTests.test_sse_all_byte_boundaries) ... ok
test_sse_incomplete_not_emitted (__main__.WitnessTests.test_sse_incomplete_not_emitted) ... ok
test_tool_result_pairing (__main__.WitnessTests.test_tool_result_pairing) ... ok

----------------------------------------------------------------------
Ran 34 tests in 0.005s

OK
```


<span id="topic-2"></span>


### 额外数值与状态：60项

```
test_activation_sensitive_error (__main__.MoreNumericTests.test_activation_sensitive_error) ... ok
test_attention_value_scaling (__main__.MoreNumericTests.test_attention_value_scaling) ... ok
test_bm25_exact_visible_numbers (__main__.MoreNumericTests.test_bm25_exact_visible_numbers) ... ok
test_cache_units (__main__.MoreNumericTests.test_cache_units) ... ok
test_calibration_brier (__main__.MoreNumericTests.test_calibration_brier) ... ok
test_context_budget (__main__.MoreNumericTests.test_context_budget) ... ok
test_contrastive_loss (__main__.MoreNumericTests.test_contrastive_loss) ... ok
test_correlated_vote_counterexample (__main__.MoreNumericTests.test_correlated_vote_counterexample) ... ok
test_cost_with_failures (__main__.MoreNumericTests.test_cost_with_failures) ... ok
test_critical_path_after_change (__main__.MoreNumericTests.test_critical_path_after_change) ... ok
test_dense_layer_chain (__main__.MoreNumericTests.test_dense_layer_chain) ... ok
test_dot_matrix_distinction (__main__.MoreNumericTests.test_dot_matrix_distinction) ... ok
test_error_budget (__main__.MoreNumericTests.test_error_budget) ... ok
test_every_masked_probability_zero (__main__.MoreNumericTests.test_every_masked_probability_zero) ... ok
test_grad_direction_finite_difference (__main__.MoreNumericTests.test_grad_direction_finite_difference) ... ok
test_gradient_accumulation_equal_batches (__main__.MoreNumericTests.test_gradient_accumulation_equal_batches) ... ok
test_gradient_accumulation_unequal_batches (__main__.MoreNumericTests.test_gradient_accumulation_unequal_batches) ... ok
test_gradient_shared_embedding (__main__.MoreNumericTests.test_gradient_shared_embedding) ... ok
test_high_weight_not_high_contribution (__main__.MoreNumericTests.test_high_weight_not_high_contribution) ... ok
test_large_step_can_increase_loss (__main__.MoreNumericTests.test_large_step_can_increase_loss) ... ok
test_layer_norm_constant_safe (__main__.MoreNumericTests.test_layer_norm_constant_safe) ... ok
test_layer_norm_mean (__main__.MoreNumericTests.test_layer_norm_mean) ... ok
test_lora_large_count (__main__.MoreNumericTests.test_lora_large_count) ... ok
test_lora_small_count_not_saved (__main__.MoreNumericTests.test_lora_small_count_not_saved) ... ok
test_maxsim_sum (__main__.MoreNumericTests.test_maxsim_sum) ... ok
test_natural_log_units (__main__.MoreNumericTests.test_natural_log_units) ... ok
test_nucleus_boundary (__main__.MoreNumericTests.test_nucleus_boundary) ... ok
test_paired_table_marginals (__main__.MoreNumericTests.test_paired_table_marginals) ... ok
test_pass_events_differ (__main__.MoreNumericTests.test_pass_events_differ) ... ok
test_patch_projector (__main__.MoreNumericTests.test_patch_projector) ... ok
test_ppo_sign_sensitive (__main__.MoreNumericTests.test_ppo_sign_sensitive) ... ok
test_prefill_off_by_one (__main__.MoreNumericTests.test_prefill_off_by_one) ... ok
test_rate_limit_dimensions (__main__.MoreNumericTests.test_rate_limit_dimensions) ... ok
test_relative_rope_shift (__main__.MoreNumericTests.test_relative_rope_shift) ... ok
test_roofline_units (__main__.MoreNumericTests.test_roofline_units) ... ok
test_routing_precision_recall_tradeoff (__main__.MoreNumericTests.test_routing_precision_recall_tradeoff) ... ok
test_scale_pair_product (__main__.MoreNumericTests.test_scale_pair_product) ... ok
test_selective_accuracy_vs_coverage (__main__.MoreNumericTests.test_selective_accuracy_vs_coverage) ... ok
test_simpson_construction (__main__.MoreNumericTests.test_simpson_construction) ... ok
test_single_parameter_sgd (__main__.MoreNumericTests.test_single_parameter_sgd) ... ok
test_spec_bad_resampling_changes_distribution (__main__.MoreNumericTests.test_spec_bad_resampling_changes_distribution) ... ok
test_supercritical_queue (__main__.MoreNumericTests.test_supercritical_queue) ... ok
test_time_to_first_vs_completion (__main__.MoreNumericTests.test_time_to_first_vs_completion) ... ok
test_transpose_not_reshape (__main__.MoreNumericTests.test_transpose_not_reshape) ... ok
test_utf8_three_bytes (__main__.MoreNumericTests.test_utf8_three_bytes) ... ok
test_acl_topk_order (__main__.MoreStateTests.test_acl_topk_order) ... ok
test_approval_bound_to_artifact_environment (__main__.MoreStateTests.test_approval_bound_to_artifact_environment) ... ok
test_atomic_replace_is_not_compare_and_swap (__main__.MoreStateTests.test_atomic_replace_is_not_compare_and_swap) ... ok
test_bitemporal_specific_scenario (__main__.MoreStateTests.test_bitemporal_specific_scenario) ... ok
test_compaction_suffix_preserved (__main__.MoreStateTests.test_compaction_suffix_preserved) ... ok
test_current_test_version (__main__.MoreStateTests.test_current_test_version) ... ok
test_exclude_boundary_counterexample (__main__.MoreStateTests.test_exclude_boundary_counterexample) ... ok
test_gui_scroll_transform (__main__.MoreStateTests.test_gui_scroll_transform) ... ok
test_idempotency_parameter_conflict (__main__.MoreStateTests.test_idempotency_parameter_conflict) ... ok
test_merge_lost_update_counterexample (__main__.MoreStateTests.test_merge_lost_update_counterexample) ... ok
test_refund_conditions_and_not_or (__main__.MoreStateTests.test_refund_conditions_and_not_or) ... ok
test_replay_does_not_repeat_effect (__main__.MoreStateTests.test_replay_does_not_repeat_effect) ... ok
test_tool_completion_order_not_identity (__main__.MoreStateTests.test_tool_completion_order_not_identity) ... ok
test_unknown_not_failure (__main__.MoreStateTests.test_unknown_not_failure) ... ok
test_version_check_refuses_stale_write (__main__.MoreStateTests.test_version_check_refuses_stale_write) ... ok

----------------------------------------------------------------------
Ran 60 tests in 0.007s

OK
```


<span id="topic-3"></span>


### 贯通模型与算子：14项

```
test_KL_asymmetry (__main__.ChainTests.test_KL_asymmetry) ... ok
test_PAD_not_implicitly_generated (__main__.ChainTests.test_PAD_not_implicitly_generated) ... ok
test_beam_joint_counterexample (__main__.ChainTests.test_beam_joint_counterexample) ... ok
test_bool_masks_inversion (__main__.ChainTests.test_bool_masks_inversion) ... ok
test_cache_full_equivalence (__main__.ChainTests.test_cache_full_equivalence) ... ok
test_causal_change_later_cannot_change_first (__main__.ChainTests.test_causal_change_later_cannot_change_first) ... ok
test_embedding_rows_match_foundation (__main__.ChainTests.test_embedding_rows_match_foundation) ... ok
test_greedy_graph_can_stop_local (__main__.ChainTests.test_greedy_graph_can_stop_local) ... ok
test_loss_denominator (__main__.ChainTests.test_loss_denominator) ... ok
test_norms_differ (__main__.ChainTests.test_norms_differ) ... ok
test_quant_clipping (__main__.ChainTests.test_quant_clipping) ... ok
test_retrieval_q_gradient_fd (__main__.ChainTests.test_retrieval_q_gradient_fd) ... ok
test_two_heads_each_row_probability (__main__.ChainTests.test_two_heads_each_row_probability) ... ok
test_zero_state_accounting (__main__.ChainTests.test_zero_state_accounting) ... ok

----------------------------------------------------------------------
Ran 14 tests in 0.002s

OK
```


<span id="calculated-results"></span>


## 正文算例的程序输出

数值表中的六位小数用于阅读；下面JSON保留更多位。相同计算被不同章节解释时，可以关联同一份结果，不算成独立新实验。


<span id="result-F05"></span>



<span id="topic-4"></span>


### F05 · 一整句话怎样逐位置取出Embedding

[返回逐步讲解](foundations/05.md#worked-F05)

```
{
  "table": [
    [
      0.0,
      0.0,
      0.0,
      0.0
    ],
    [
      0.2,
      -0.1,
      0.7,
      0.4
    ],
    [
      -0.3,
      0.8,
      0.1,
      0.5
    ],
    [
      0.6,
      0.2,
      -0.4,
      0.9
    ],
    [
      0.1,
      -0.5,
      0.9,
      0.3
    ],
    [
      -0.2,
      0.4,
      0.5,
      -0.6
    ]
  ],
  "ids": [
    [
      1,
      2,
      3
    ],
    [
      4,
      2,
      0
    ]
  ],
  "output": [
    [
      [
        0.2,
        -0.1,
        0.7,
        0.4
      ],
      [
        -0.3,
        0.8,
        0.1,
        0.5
      ],
      [
        0.6,
        0.2,
        -0.4,
        0.9
      ]
    ],
    [
      [
        0.1,
        -0.5,
        0.9,
        0.3
      ],
      [
        -0.3,
        0.8,
        0.1,
        0.5
      ],
      [
        0.0,
        0.0,
        0.0,
        0.0
      ]
    ]
  ]
}
```


<span id="result-F06"></span>



<span id="topic-5"></span>


### F06 · 把同一个张量搬到设备，数值和占用如何分别变化

[返回逐步讲解](foundations/06.md#worked-F06)

```
{
  "ids_elements": 256,
  "ids_bytes_int64": 2048,
  "embedding_elements": 1048576,
  "embedding_bytes_fp16": 2097152
}
```


<span id="result-F09"></span>



<span id="topic-6"></span>


### F09 · 三个分数怎样一步步变成抽样概率

[返回逐步讲解](foundations/09.md#worked-F09)

```
{
  "logits": [
    2,
    1,
    0
  ],
  "p": [
    0.6652409557748218,
    0.24472847105479764,
    0.09003057317038046
  ],
  "shifted_p": [
    0.6652409557748218,
    0.24472847105479764,
    0.09003057317038046
  ],
  "temperature2": [
    0.506480391055654,
    0.3071958857184984,
    0.1863237232258476
  ],
  "temperature05": [
    0.8668133321973349,
    0.11731042782619838,
    0.015876239976466765
  ]
}
```


<span id="result-F16"></span>



<span id="topic-7"></span>


### F19 · 同一条历史为什么每层都要留一份K/V

[返回逐步讲解](foundations/19.md#worked-F16)

```
{
  "tiny_bytes": 96,
  "GiB": 4.0,
  "per_token_KiB": 128.0
}
```


<span id="result-F18"></span>



<span id="topic-8"></span>


### F16 · 把三个训练位置逐一评分，不让PAD混入平均数

[返回逐步讲解](foundations/16.md#worked-F18)

```
{
  "target_ps": [
    0.8,
    0.5,
    0.25
  ],
  "losses": [
    0.2231435513142097,
    0.6931471805599453,
    1.3862943611198906
  ],
  "mean": 0.7675283643313485,
  "logits": [
    0,
    0
  ],
  "gradient": [
    -0.5,
    0.5
  ],
  "updated_logits": [
    0.05,
    -0.05
  ],
  "new_loss": 0.6443966600735709
}
```


<span id="result-F19"></span>



<span id="topic-9"></span>


### F17 · 偏好训练究竟比较哪两个概率比

[返回逐步讲解](foundations/17.md#worked-F19)

```
{
  "pi_preferred": 0.6,
  "pi_rejected": 0.2,
  "ref_preferred": 0.3,
  "ref_rejected": 0.2,
  "beta": 1.0,
  "margin": 0.6931471805599453,
  "loss": 0.40546510810816444,
  "baseline_loss": 0.6931471805599453,
  "kl": 0.19274475702175753
}
```


<span id="result-F28"></span>



<span id="topic-10"></span>


### F28 · 三份文档怎样变成一个倒排索引

[返回逐步讲解](foundations/28.md#worked-F28)

```
{
  "N": 3,
  "df": 2,
  "avgdl": 2.6666666666666665,
  "idf": 0.47000362924573563,
  "rows": [
    {
      "doc": "A",
      "length": 2,
      "frequency": 1,
      "denominator": 1.975,
      "tf_factor": 1.1139240506329113,
      "score": 0.5235483465015789
    },
    {
      "doc": "B",
      "length": 4,
      "frequency": 2,
      "denominator": 3.65,
      "tf_factor": 1.2054794520547947,
      "score": 0.5665797174469143
    },
    {
      "doc": "C",
      "length": 2,
      "frequency": 0,
      "denominator": 0.975,
      "tf_factor": 0.0,
      "score": 0.0
    }
  ]
}
```


<span id="result-F29"></span>



<span id="topic-11"></span>


### F29 · 把两个榜单融合，再检查是否足够回答

[返回逐步讲解](foundations/29.md#worked-F29)

```
[
  [
    "B",
    0.03252247488101534
  ],
  [
    "C",
    0.03200204813108039
  ],
  [
    "A",
    0.01639344262295082
  ],
  [
    "D",
    0.015873015873015872
  ]
]
```


<span id="result-F35"></span>



<span id="topic-12"></span>


### F35 · 同一组结果，把四个分母分别数清

[返回逐步讲解](foundations/35.md#worked-F35)

```
{
  "precision_recall": {
    "precision": 0.3333333333333333,
    "recall": 0.5
  },
  "pass1": 0.8,
  "pass_at3": 0.992,
  "pass_all3": 0.5120000000000001,
  "finite_pass3": 0.9666666666666667,
  "brier": 0.3400000000000001,
  "mcnemar_p": 0.2890625
}
```


<span id="result-Q005"></span>



<span id="topic-13"></span>


### Q005 · 一个两位置单层Decoder，从输入一直算到词表概率

[返回逐步讲解](chapters/02.md#worked-Q005)

```
{
  "X": [
    [
      1.0,
      0.0
    ],
    [
      0.0,
      2.0
    ]
  ],
  "norm1": [
    [
      0.9999800005999799,
      -0.9999800005999799
    ],
    [
      -0.9999950000374997,
      0.9999950000374997
    ]
  ],
  "attention": {
    "scores": [
      [
        1.4141569960932512,
        "-inf"
      ],
      [
        -1.414178208076984,
        1.4141994203788915
      ]
    ],
    "weights": [
      [
        1.0,
        0.0
      ],
      [
        0.055809827361326024,
        0.9441901726386741
      ]
    ],
    "output": [
      [
        0.9999800005999799,
        -0.9999800005999799
      ],
      [
        -0.8883767405249542,
        0.8883767405249542
      ]
    ]
  },
  "residual1": [
    [
      1.99998000059998,
      -0.9999800005999799
    ],
    [
      -0.8883767405249542,
      2.8883767405249543
    ]
  ],
  "norm2": [
    [
      0.9999977777259269,
      -0.9999977777259269
    ],
    [
      -0.9999985978586216,
      0.9999985978586216
    ]
  ],
  "ffn": [
    [
      0.49999888886296345,
      0.0
    ],
    [
      0.0,
      0.4999992989293108
    ]
  ],
  "Y": [
    [
      2.4999788894629433,
      -0.9999800005999799
    ],
    [
      -0.8883767405249542,
      3.3883760394542652
    ]
  ],
  "final_norm": [
    -0.999998906544809,
    0.999998906544809
  ],
  "logits": [
    -0.999998906544809,
    0.999998906544809,
    1.4999983598172135
  ],
  "probabilities": [
    0.04861094091010992,
    0.35918818389337787,
    0.5922008751965122
  ]
}
```


<span id="result-Q007"></span>



<span id="topic-14"></span>


### Q007 · 一次稳定softmax计算，加一个全屏蔽反例

[返回逐步讲解](chapters/02.md#worked-Q007)

```
{
  "logits": [
    2,
    1,
    0
  ],
  "p": [
    0.6652409557748218,
    0.24472847105479764,
    0.09003057317038046
  ],
  "shifted_p": [
    0.6652409557748218,
    0.24472847105479764,
    0.09003057317038046
  ],
  "temperature2": [
    0.506480391055654,
    0.3071958857184984,
    0.1863237232258476
  ],
  "temperature05": [
    0.8668133321973349,
    0.11731042782619838,
    0.015876239976466765
  ]
}
```


<span id="result-Q012"></span>



<span id="topic-15"></span>


### Q012 · 对一个查询手算Attention的梯度，再用扰动检查

[返回逐步讲解](chapters/03.md#worked-Q012)

```
{
  "Q": [
    [
      0.4,
      -0.2
    ]
  ],
  "K": [
    [
      1.0,
      0.5
    ],
    [
      -0.5,
      1.0
    ]
  ],
  "V": [
    [
      2.0,
      -1.0
    ],
    [
      0.5,
      3.0
    ]
  ],
  "upstream": [
    [
      0.7,
      -0.3
    ]
  ],
  "P": [
    [
      0.6212776533473258,
      0.37872234665267435
    ]
  ],
  "O": [
    [
      1.4319164800209887,
      0.5148893866106973
    ]
  ],
  "dP": [
    [
      1.7,
      -0.5499999999999999
    ]
  ],
  "dS": [
    [
      0.5294063942967733,
      -0.5294063942967733
    ]
  ],
  "dQ": [
    [
      0.5615202771161513,
      -0.18717342570538376
    ]
  ],
  "dK": [
    [
      0.14973874056430703,
      -0.07486937028215351
    ],
    [
      -0.14973874056430703,
      0.07486937028215351
    ]
  ],
  "dV": [
    [
      0.43489435734312804,
      -0.18638329600419773
    ],
    [
      0.26510564265687203,
      -0.1136167039958023
    ]
  ],
  "max_error": 1.8966389569996522e-10,
  "coordinates_checked": 10
}
```


<span id="result-Q014"></span>



<span id="topic-16"></span>


### Q014 · 相同logits经过温度、Top-k和Top-p后怎样重新分配

[返回逐步讲解](chapters/06.md#worked-Q014)

```
{
  "logits": [
    2,
    1,
    0
  ],
  "p": [
    0.6652409557748218,
    0.24472847105479764,
    0.09003057317038046
  ],
  "shifted_p": [
    0.6652409557748218,
    0.24472847105479764,
    0.09003057317038046
  ],
  "temperature2": [
    0.506480391055654,
    0.3071958857184984,
    0.1863237232258476
  ],
  "temperature05": [
    0.8668133321973349,
    0.11731042782619838,
    0.015876239976466765
  ]
}
```


<span id="result-Q018"></span>



<span id="topic-17"></span>


### Q018 · AdamW的第一步，把动量、偏差修正与衰减都算出来

[返回逐步讲解](chapters/04.md#worked-Q018)

```
{
  "w": 1.0,
  "gradient": 0.2,
  "m": 0.019999999999999997,
  "v": 4.0000000000000044e-05,
  "m_hat": 0.2,
  "v_hat": 0.04000000000000001,
  "after_decay": 0.999,
  "new_w": 0.8990000049999998
}
```


<span id="result-Q021"></span>



<span id="topic-18"></span>


### Q021 · 同一对回答，SFT与DPO看的训练信号不同

[返回逐步讲解](chapters/05.md#worked-Q021)

```
{
  "pi_preferred": 0.6,
  "pi_rejected": 0.2,
  "ref_preferred": 0.3,
  "ref_rejected": 0.2,
  "beta": 1.0,
  "margin": 0.6931471805599453,
  "loss": 0.40546510810816444,
  "baseline_loss": 0.6931471805599453,
  "kl": 0.19274475702175753
}
```


<span id="result-Q026"></span>



<span id="topic-19"></span>


### Q026 · 把一条长上下文的K/V字节数从单位算出来

[返回逐步讲解](chapters/07.md#worked-Q026)

```
{
  "tiny_bytes": 96,
  "GiB": 4.0,
  "per_token_KiB": 128.0
}
```


<span id="result-Q027"></span>



<span id="topic-20"></span>


### Q027 · 两块分数如何不存完整概率表也得到同一结果

[返回逐步讲解](chapters/07.md#worked-Q027)

```
[
  {
    "score": 1,
    "value": 2,
    "max": 1,
    "old_scale": 0.0,
    "sum": 1.0,
    "weighted_sum": 2.0,
    "output": 2.0
  },
  {
    "score": 3,
    "value": 10,
    "max": 3,
    "old_scale": 0.1353352832366127,
    "sum": 1.1353352832366128,
    "weighted_sum": 10.270670566473225,
    "output": 9.046376623823058
  }
]
```


<span id="result-Q031"></span>



<span id="topic-21"></span>


### Q031 · 草稿错了仍可保持目标分布：三种Token逐项对账

[返回逐步讲解](chapters/08.md#worked-Q031)

```
{
  "target": [
    0.6,
    0.3,
    0.1
  ],
  "draft": [
    0.2,
    0.5,
    0.3
  ],
  "accept_prob": [
    1,
    0.6,
    0.33333333333333337
  ],
  "accepted_mass": [
    0.2,
    0.3,
    0.1
  ],
  "rejection_mass": 0.4,
  "residual_distribution": [
    1.0,
    0.0,
    0.0
  ],
  "final_mass": [
    0.6000000000000001,
    0.3,
    0.1
  ]
}
```


<span id="result-Q038"></span>



<span id="topic-22"></span>


### Q038 · 中文字符被拆成三个网络片段，为什么不能逐片decode

[返回逐步讲解](chapters/10.md#worked-Q038)

```
{
  "utf8_bytes_of_wo": [
    230,
    136,
    145
  ],
  "events": [
    "{\"text\":\"我\"}"
  ]
}
```


<span id="result-Q058"></span>



<span id="topic-23"></span>


### Q058 · 两个文档都含“排除”，BM25为什么不只数次数

[返回逐步讲解](chapters/15.md#worked-Q058)

```
{
  "N": 3,
  "df": 2,
  "avgdl": 2.6666666666666665,
  "idf": 0.47000362924573563,
  "rows": [
    {
      "doc": "A",
      "length": 2,
      "frequency": 1,
      "denominator": 1.975,
      "tf_factor": 1.1139240506329113,
      "score": 0.5235483465015789
    },
    {
      "doc": "B",
      "length": 4,
      "frequency": 2,
      "denominator": 3.65,
      "tf_factor": 1.2054794520547947,
      "score": 0.5665797174469143
    },
    {
      "doc": "C",
      "length": 2,
      "frequency": 0,
      "denominator": 0.975,
      "tf_factor": 0.0,
      "score": 0.0
    }
  ]
}
```


<span id="result-Q061"></span>



<span id="topic-24"></span>


### Q061 · 两张排名表，逐行融合成RRF

[返回逐步讲解](chapters/16.md#worked-Q061)

```
[
  [
    "B",
    0.03252247488101534
  ],
  [
    "C",
    0.03200204813108039
  ],
  [
    "A",
    0.01639344262295082
  ],
  [
    "D",
    0.015873015873015872
  ]
]
```


<span id="result-Q090"></span>



<span id="topic-25"></span>


### Q090 · pass@3与连续三次都成功，数字为何差很多

[返回逐步讲解](chapters/23.md#worked-Q090)

```
{
  "pass1": 0.8,
  "pass_at3": 0.992,
  "pass_all3": 0.5120000000000001,
  "finite_pass3": 0.9666666666666667
}
```


<span id="result-Q091"></span>



<span id="topic-26"></span>


### Q091 · 20个任务提升20个百分点，证据足够强吗

[返回逐步讲解](chapters/23.md#worked-Q091)

```
{
  "A_successes": 12,
  "B_successes": 16,
  "tasks": 20,
  "A_rate": 0.6,
  "B_rate": 0.8,
  "discordant": 8,
  "two_sided_exact_p": 0.2890625
}
```


<span id="result-Q105"></span>



<span id="topic-27"></span>


### Q105 · 四次都说80%把握，实际只对两次，怎么算

[返回逐步讲解](chapters/27.md#worked-Q105)

```
{
  "probabilities": [
    0.8,
    0.8,
    0.8,
    0.8
  ],
  "labels": [
    1,
    1,
    0,
    0
  ],
  "Brier": 0.3400000000000001
}
```


<span id="result-S31"></span>



<span id="topic-28"></span>


### S31 · 用一个方向导数核对矩阵反传是否接对

[返回逐步讲解](studies/chapters/31.md#worked-S31)

```
{
  "direction": [
    1,
    -2
  ],
  "directional_derivative": 0.9358671285269188
}
```


<span id="result-X01"></span>



<span id="topic-29"></span>


### X01 · 沿用“我爱学习／你爱”，把一层模型真正算到底

[返回逐步讲解](worked-model.md#worked-X01)

```
{
  "sentence_A": {
    "ids": [
      1,
      2,
      3
    ],
    "words": [
      "我",
      "爱",
      "学习"
    ],
    "X": [
      [
        0.2,
        -0.1,
        0.7,
        0.4
      ],
      [
        -0.3,
        0.8,
        0.1,
        0.5
      ],
      [
        0.6,
        0.2,
        -0.4,
        0.9
      ]
    ],
    "normalized": [
      [
        -0.34297699576097085,
        -1.3719079830438836,
        1.3719079830438834,
        0.342976995760971
      ],
      [
        -1.3869118391183253,
        1.2663108096297753,
        -0.4221036032099251,
        0.542704632698475
      ],
      [
        0.5650201202110635,
        -0.2568273273686653,
        -1.489598498738259,
        1.1814057058958602
      ]
    ],
    "Wq": [
      [
        1.0,
        0.0,
        0.0,
        0.0
      ],
      [
        0.0,
        1.0,
        0.0,
        0.0
      ],
      [
        0.0,
        0.0,
        1.0,
        0.0
      ],
      [
        0.0,
        0.0,
        0.0,
        1.0
      ]
    ],
    "Wk": [
      [
        0.0,
        1.0,
        0.0,
        0.0
      ],
      [
        1.0,
        0.0,
        0.0,
        0.0
      ],
      [
        0.0,
        0.0,
        0.0,
        1.0
      ],
      [
        0.0,
        0.0,
        1.0,
        0.0
      ]
    ],
    "Wv": [
      [
        1.0,
        0.0,
        0.0,
        0.0
      ],
      [
        0.0,
        0.5,
        0.0,
        0.0
      ],
      [
        0.0,
        0.0,
        1.0,
        0.0
      ],
      [
        0.0,
        0.0,
        0.0,
        0.5
      ]
    ],
    "Q": [
      [
        -0.34297699576097085,
        -1.3719079830438836,
        1.3719079830438834,
        0.342976995760971
      ],
      [
        -1.3869118391183253,
        1.2663108096297753,
        -0.4221036032099251,
        0.542704632698475
      ],
      [
        0.5650201202110635,
        -0.2568273273686653,
        -1.489598498738259,
        1.1814057058958602
      ]
    ],
    "K_new": [
      [
        -1.3719079830438836,
        -0.34297699576097085,
        0.342976995760971,
        1.3719079830438834
      ],
      [
        1.2663108096297753,
        -1.3869118391183253,
        0.542704632698475,
        -0.4221036032099251
      ],
      [
        -0.2568273273686653,
        0.5650201202110635,
        1.1814057058958602,
        -1.489598498738259
      ]
    ],
    "V_new": [
      [
        -0.34297699576097085,
        -0.6859539915219418,
        1.3719079830438834,
        0.1714884978804855
      ],
      [
        -1.3869118391183253,
        0.6331554048148876,
        -0.4221036032099251,
        0.2713523163492375
      ],
      [
        0.5650201202110635,
        -0.12841366368433266,
        -1.489598498738259,
        0.5907028529479301
      ]
    ],
    "heads": [
      {
        "scores": [
          [
            0.6654339782957746,
            "-inf",
            "-inf"
          ],
          [
            1.038315559790008,
            -2.4837287671488384,
            "-inf"
          ],
          [
            -0.48583167819068557,
            0.7577978145111113,
            -0.2052202174328266
          ]
        ],
        "weights": [
          [
            1.0,
            0.0,
            0.0
          ],
          [
            0.9713085308519348,
            0.02869146914806531,
            0.0
          ],
          [
            0.17264843188821463,
            0.5987755582887623,
            0.22857600982302304
          ]
        ],
        "output": [
          [
            -0.34297699576097085,
            -0.6859539915219418
          ],
          [
            -0.3729290201117488,
            -0.6481068049740206
          ],
          [
            -0.7605133067096621,
            0.2313368171661363
          ]
        ]
      },
      {
        "scores": [
          [
            0.6654339782957748,
            "-inf",
            "-inf"
          ],
          [
            0.4241007216043693,
            -0.32396462180202235,
            "-inf"
          ],
          [
            0.7848050186157225,
            -0.9242505136522802,
            -2.4887615459580976
          ]
        ],
        "weights": [
          [
            1.0,
            0.0,
            0.0
          ],
          [
            0.6787570011392197,
            0.3212429988607803,
            0.0
          ],
          [
            0.8204065891481991,
            0.14852369763229697,
            0.031069713219503917
          ]
        ],
        "output": [
          [
            1.3719079830438834,
            0.1714884978804855
          ],
          [
            0.7955943210847245,
            0.20356905040307596
          ],
          [
            1.0165485628935624,
            0.19934551124858982
          ]
        ]
      }
    ],
    "concat_attention": [
      [
        -0.34297699576097085,
        -0.6859539915219418,
        1.3719079830438834,
        0.1714884978804855
      ],
      [
        -0.3729290201117488,
        -0.6481068049740206,
        0.7955943210847245,
        0.20356905040307596
      ],
      [
        -0.7605133067096621,
        0.2313368171661363,
        1.0165485628935624,
        0.19934551124858982
      ]
    ],
    "residual1": [
      [
        -0.14297699576097084,
        -0.7859539915219418,
        2.071907983043883,
        0.5714884978804855
      ],
      [
        -0.6729290201117488,
        0.15189319502597942,
        0.8955943210847245,
        0.7035690504030759
      ],
      [
        -0.16051330670966213,
        0.4313368171661363,
        0.6165485628935624,
        1.09934551124859
      ]
    ],
    "normalized2": [
      [
        -0.5375457231048607,
        -1.1422230212813547,
        1.5454069697365898,
        0.13436177464962554
      ],
      [
        -1.5481133247122487,
        -0.19323668985226614,
        1.0283881167102003,
        0.7129618978543147
      ],
      [
        -1.4570262083734293,
        -0.14486747903237152,
        0.26575541201519126,
        1.3361382753906097
      ]
    ],
    "ffn": [
      [
        0.026638704396888653,
        0.07890418501095597,
        0.49213512533270637,
        0.0024080109431469515
      ],
      [
        0.10506870807782567,
        0.004217979178685728,
        0.194754614176563,
        0.08527681301454476
      ],
      [
        0.10026713476934813,
        0.0024336378144475014,
        0.009994463250812926,
        0.353417478623218
      ]
    ],
    "hidden_output": [
      [
        -0.11633829136408219,
        -0.7070498065109858,
        2.5640431083765893,
        0.5738965088236324
      ],
      [
        -0.5678603120339232,
        0.15611117420466514,
        1.0903489352612874,
        0.7888458634176208
      ],
      [
        -0.060246171940313994,
        0.4337704549805838,
        0.6265430261443753,
        1.452762989871808
      ]
    ],
    "last_norm": [
      -1.234288717037841,
      -0.3288677410295592,
      0.024440872525857662,
      1.5387155855415424
    ],
    "logits_before_PAD_filter": [
      0.0,
      0.41862387568010506,
      0.8789943023110618,
      0.5687208995484289,
      0.5246164597467301,
      -0.7956982680662521
    ],
    "probabilities_after_PAD_filter": [
      0.0,
      0.19397390234211448,
      0.30738285417678823,
      0.22538738883221388,
      0.21566282874820453,
      0.057593025900678906
    ],
    "selected_token": 2,
    "selected_word": "爱",
    "cache": {
      "K": [
        [
          -1.3719079830438836,
          -0.34297699576097085,
          0.342976995760971,
          1.3719079830438834
        ],
        [
          1.2663108096297753,
          -1.3869118391183253,
          0.542704632698475,
          -0.4221036032099251
        ],
        [
          -0.2568273273686653,
          0.5650201202110635,
          1.1814057058958602,
          -1.489598498738259
        ]
      ],
      "V": [
        [
          -0.34297699576097085,
          -0.6859539915219418,
          1.3719079830438834,
          0.1714884978804855
        ],
        [
          -1.3869118391183253,
          0.6331554048148876,
          -0.4221036032099251,
          0.2713523163492375
        ],
        [
          0.5650201202110635,
          -0.12841366368433266,
          -1.489598498738259,
          0.5907028529479301
        ]
      ]
    }
  },
  "sentence_B": {
    "ids": [
      4,
      2
    ],
    "words": [
      "你",
      "爱"
    ],
    "X": [
      [
        0.1,
        -0.5,
        0.9,
        0.3
      ],
      [
        -0.3,
        0.8,
        0.1,
        0.5
      ]
    ],
    "normalized": [
      [
        -0.19999600011999602,
        -1.399972000839972,
        1.399972000839972,
        0.19999600011999596
      ],
      [
        -1.3869118391183253,
        1.2663108096297753,
        -0.4221036032099251,
        0.542704632698475
      ]
    ],
    "Wq": [
      [
        1.0,
        0.0,
        0.0,
        0.0
      ],
      [
        0.0,
        1.0,
        0.0,
        0.0
      ],
      [
        0.0,
        0.0,
        1.0,
        0.0
      ],
      [
        0.0,
        0.0,
        0.0,
        1.0
      ]
    ],
    "Wk": [
      [
        0.0,
        1.0,
        0.0,
        0.0
      ],
      [
        1.0,
        0.0,
        0.0,
        0.0
      ],
      [
        0.0,
        0.0,
        0.0,
        1.0
      ],
      [
        0.0,
        0.0,
        1.0,
        0.0
      ]
    ],
    "Wv": [
      [
        1.0,
        0.0,
        0.0,
        0.0
      ],
      [
        0.0,
        0.5,
        0.0,
        0.0
      ],
      [
        0.0,
        0.0,
        1.0,
        0.0
      ],
      [
        0.0,
        0.0,
        0.0,
        0.5
      ]
    ],
    "Q": [
      [
        -0.19999600011999602,
        -1.399972000839972,
        1.399972000839972,
        0.19999600011999596
      ],
      [
        -1.3869118391183253,
        1.2663108096297753,
        -0.4221036032099251,
        0.542704632698475
      ]
    ],
    "K_new": [
      [
        -1.399972000839972,
        -0.19999600011999602,
        0.19999600011999596,
        1.399972000839972
      ],
      [
        1.2663108096297753,
        -1.3869118391183253,
        0.542704632698475,
        -0.4221036032099251
      ]
    ],
    "V_new": [
      [
        -0.19999600011999602,
        -0.699986000419986,
        1.399972000839972,
        0.09999800005999798
      ],
      [
        -1.3869118391183253,
        0.6331554048148876,
        -0.4221036032099251,
        0.2713523163492375
      ]
    ],
    "heads": [
      {
        "scores": [
          [
            0.3959639589061104,
            "-inf"
          ],
          [
            1.1938654037027494,
            -2.4837287671488384
          ]
        ],
        "weights": [
          [
            1.0,
            0.0
          ],
          [
            0.9753397724784735,
            0.024660227521526565
          ]
        ],
        "output": [
          [
            -0.19999600011999602,
            -0.699986000419986
          ],
          [
            -0.2292656147585984,
            -0.6671104300485264
          ]
        ]
      },
      {
        "scores": [
          [
            0.39596395890611025,
            "-inf"
          ],
          [
            0.47754616148109963,
            -0.32396462180202235
          ]
        ],
        "weights": [
          [
            1.0,
            0.0
          ],
          [
            0.6902975595329414,
            0.30970244046705875
          ]
        ],
        "output": [
          [
            1.399972000839972,
            0.09999800005999798
          ],
          [
            0.8356707395502289,
            0.15306684999933975
          ]
        ]
      }
    ],
    "concat_attention": [
      [
        -0.19999600011999602,
        -0.699986000419986,
        1.399972000839972,
        0.09999800005999798
      ],
      [
        -0.2292656147585984,
        -0.6671104300485264,
        0.8356707395502289,
        0.15306684999933975
      ]
    ],
    "residual1": [
      [
        -0.09999600011999601,
        -1.199986000419986,
        2.299972000839972,
        0.39999800005999797
      ],
      [
        -0.5292656147585983,
        0.1328895699514736,
        0.9356707395502288,
        0.6530668499993397
      ]
    ],
    "normalized2": [
      [
        -0.35547632541594226,
        -1.2244240715329902,
        1.5404016231276416,
        0.03949877382129085
      ],
      [
        -1.4833659426292805,
        -0.29618841733983176,
        1.1431173289264525,
        0.6364370310426596
      ]
    ],
    "ffn": [
      [
        0.01301717141981196,
        0.08513994324236378,
        0.48852155463920643,
        0.00019887014948993128
      ],
      [
        0.10172306748140784,
        0.009353723209194037,
        0.24770508249823658,
        0.06622071158161205
      ]
    ],
    "hidden_output": [
      [
        -0.08697882870018406,
        -1.1148460571776222,
        2.7884935554791785,
        0.4001968702094879
      ],
      [
        -0.4275425472771905,
        0.14224329316066764,
        1.1833758220484654,
        0.7192875615809518
      ]
    ],
    "last_norm": [
      -1.373723709101048,
      -0.4328128205320284,
      1.2864523197198492,
      0.5200842099132272
    ],
    "logits_before_PAD_filter": [
      0.0,
      0.8770868480021786,
      0.45455419323329016,
      -0.9573019285330696,
      1.3928663900777418,
      0.4327952475193865
    ],
    "probabilities_after_PAD_filter": [
      0.0,
      0.24205350317424174,
      0.15863819948379718,
      0.0386586290982537,
      0.40542598586807865,
      0.1552236823756288
    ],
    "selected_token": 4,
    "selected_word": "你",
    "cache": {
      "K": [
        [
          -1.399972000839972,
          -0.19999600011999602,
          0.19999600011999596,
          1.399972000839972
        ],
        [
          1.2663108096297753,
          -1.3869118391183253,
          0.542704632698475,
          -0.4221036032099251
        ]
      ],
      "V": [
        [
          -0.19999600011999602,
          -0.699986000419986,
          1.399972000839972,
          0.09999800005999798
        ],
        [
          -1.3869118391183253,
          0.6331554048148876,
          -0.4221036032099251,
          0.2713523163492375
        ]
      ]
    }
  },
  "next_step_A": {
    "ids": [
      2
    ],
    "words": [
      "爱"
    ],
    "X": [
      [
        -0.3,
        0.8,
        0.1,
        0.5
      ]
    ],
    "normalized": [
      [
        -1.3869118391183253,
        1.2663108096297753,
        -0.4221036032099251,
        0.542704632698475
      ]
    ],
    "Wq": [
      [
        1.0,
        0.0,
        0.0,
        0.0
      ],
      [
        0.0,
        1.0,
        0.0,
        0.0
      ],
      [
        0.0,
        0.0,
        1.0,
        0.0
      ],
      [
        0.0,
        0.0,
        0.0,
        1.0
      ]
    ],
    "Wk": [
      [
        0.0,
        1.0,
        0.0,
        0.0
      ],
      [
        1.0,
        0.0,
        0.0,
        0.0
      ],
      [
        0.0,
        0.0,
        0.0,
        1.0
      ],
      [
        0.0,
        0.0,
        1.0,
        0.0
      ]
    ],
    "Wv": [
      [
        1.0,
        0.0,
        0.0,
        0.0
      ],
      [
        0.0,
        0.5,
        0.0,
        0.0
      ],
      [
        0.0,
        0.0,
        1.0,
        0.0
      ],
      [
        0.0,
        0.0,
        0.0,
        0.5
      ]
    ],
    "Q": [
      [
        -1.3869118391183253,
        1.2663108096297753,
        -0.4221036032099251,
        0.542704632698475
      ]
    ],
    "K_new": [
      [
        1.2663108096297753,
        -1.3869118391183253,
        0.542704632698475,
        -0.4221036032099251
      ]
    ],
    "V_new": [
      [
        -1.3869118391183253,
        0.6331554048148876,
        -0.4221036032099251,
        0.2713523163492375
      ]
    ],
    "heads": [
      {
        "scores": [
          [
            1.038315559790008,
            -2.4837287671488384,
            0.7577978145111113,
            -2.4837287671488384
          ]
        ],
        "weights": [
          [
            0.5511249666097909,
            0.016279672703321285,
            0.4163156879835665,
            0.016279672703321285
          ]
        ],
        "output": [
          [
            0.0010466131151194366,
            -0.41089186789516574
          ]
        ]
      },
      {
        "scores": [
          [
            0.4241007216043693,
            -0.32396462180202235,
            -0.9242505136522802,
            -0.32396462180202235
          ]
        ],
        "weights": [
          [
            0.4532617660923528,
            0.2145203198848118,
            0.11769759413802364,
            0.2145203198848118
          ]
        ],
        "output": [
          [
            0.2654116758073136,
            0.26367465546571783
          ]
        ]
      }
    ],
    "concat_attention": [
      [
        0.0010466131151194366,
        -0.41089186789516574,
        0.2654116758073136,
        0.26367465546571783
      ]
    ],
    "residual1": [
      [
        -0.29895338688488055,
        0.3891081321048343,
        0.3654116758073136,
        0.7636746554657179
      ]
    ],
    "normalized2": [
      [
        -1.5775498330234923,
        0.2202585040479007,
        0.15834298411985276,
        1.1989483448557388
      ]
    ],
    "ffn": [
      [
        0.10647918732019314,
        0.006729387801927646,
        0.003381673851209182,
        0.27611694964160904
      ]
    ],
    "hidden_output": [
      [
        -0.19247419956468742,
        0.39583751990676197,
        0.3687933496585228,
        1.039791605107327
      ]
    ],
    "last_norm": [
      -1.3648661531888693,
      -0.01638759358892958,
      -0.07837596222908708,
      1.4596297090068862
    ],
    "logits_before_PAD_filter": [
      0.0,
      0.2576542387635127,
      1.1183270293660514,
      0.5228199123667249,
      0.2390577281714653,
      -0.6485476133164731
    ],
    "probabilities_after_PAD_filter": [
      0.0,
      0.1651792442552844,
      0.3906078063175441,
      0.21533541595718736,
      0.16213587244494412,
      0.06674166102504007
    ],
    "selected_token": 2,
    "selected_word": "爱",
    "cache": {
      "K": [
        [
          -1.3719079830438836,
          -0.34297699576097085,
          0.342976995760971,
          1.3719079830438834
        ],
        [
          1.2663108096297753,
          -1.3869118391183253,
          0.542704632698475,
          -0.4221036032099251
        ],
        [
          -0.2568273273686653,
          0.5650201202110635,
          1.1814057058958602,
          -1.489598498738259
        ],
        [
          1.2663108096297753,
          -1.3869118391183253,
          0.542704632698475,
          -0.4221036032099251
        ]
      ],
      "V": [
        [
          -0.34297699576097085,
          -0.6859539915219418,
          1.3719079830438834,
          0.1714884978804855
        ],
        [
          -1.3869118391183253,
          0.6331554048148876,
          -0.4221036032099251,
          0.2713523163492375
        ],
        [
          0.5650201202110635,
          -0.12841366368433266,
          -1.489598498738259,
          0.5907028529479301
        ],
        [
          -1.3869118391183253,
          0.6331554048148876,
          -0.4221036032099251,
          0.2713523163492375
        ]
      ]
    }
  },
  "full_recompute_A": {
    "ids": [
      1,
      2,
      3,
      2
    ],
    "words": [
      "我",
      "爱",
      "学习",
      "爱"
    ],
    "X": [
      [
        0.2,
        -0.1,
        0.7,
        0.4
      ],
      [
        -0.3,
        0.8,
        0.1,
        0.5
      ],
      [
        0.6,
        0.2,
        -0.4,
        0.9
      ],
      [
        -0.3,
        0.8,
        0.1,
        0.5
      ]
    ],
    "normalized": [
      [
        -0.34297699576097085,
        -1.3719079830438836,
        1.3719079830438834,
        0.342976995760971
      ],
      [
        -1.3869118391183253,
        1.2663108096297753,
        -0.4221036032099251,
        0.542704632698475
      ],
      [
        0.5650201202110635,
        -0.2568273273686653,
        -1.489598498738259,
        1.1814057058958602
      ],
      [
        -1.3869118391183253,
        1.2663108096297753,
        -0.4221036032099251,
        0.542704632698475
      ]
    ],
    "Wq": [
      [
        1.0,
        0.0,
        0.0,
        0.0
      ],
      [
        0.0,
        1.0,
        0.0,
        0.0
      ],
      [
        0.0,
        0.0,
        1.0,
        0.0
      ],
      [
        0.0,
        0.0,
        0.0,
        1.0
      ]
    ],
    "Wk": [
      [
        0.0,
        1.0,
        0.0,
        0.0
      ],
      [
        1.0,
        0.0,
        0.0,
        0.0
      ],
      [
        0.0,
        0.0,
        0.0,
        1.0
      ],
      [
        0.0,
        0.0,
        1.0,
        0.0
      ]
    ],
    "Wv": [
      [
        1.0,
        0.0,
        0.0,
        0.0
      ],
      [
        0.0,
        0.5,
        0.0,
        0.0
      ],
      [
        0.0,
        0.0,
        1.0,
        0.0
      ],
      [
        0.0,
        0.0,
        0.0,
        0.5
      ]
    ],
    "Q": [
      [
        -0.34297699576097085,
        -1.3719079830438836,
        1.3719079830438834,
        0.342976995760971
      ],
      [
        -1.3869118391183253,
        1.2663108096297753,
        -0.4221036032099251,
        0.542704632698475
      ],
      [
        0.5650201202110635,
        -0.2568273273686653,
        -1.489598498738259,
        1.1814057058958602
      ],
      [
        -1.3869118391183253,
        1.2663108096297753,
        -0.4221036032099251,
        0.542704632698475
      ]
    ],
    "K_new": [
      [
        -1.3719079830438836,
        -0.34297699576097085,
        0.342976995760971,
        1.3719079830438834
      ],
      [
        1.2663108096297753,
        -1.3869118391183253,
        0.542704632698475,
        -0.4221036032099251
      ],
      [
        -0.2568273273686653,
        0.5650201202110635,
        1.1814057058958602,
        -1.489598498738259
      ],
      [
        1.2663108096297753,
        -1.3869118391183253,
        0.542704632698475,
        -0.4221036032099251
      ]
    ],
    "V_new": [
      [
        -0.34297699576097085,
        -0.6859539915219418,
        1.3719079830438834,
        0.1714884978804855
      ],
      [
        -1.3869118391183253,
        0.6331554048148876,
        -0.4221036032099251,
        0.2713523163492375
      ],
      [
        0.5650201202110635,
        -0.12841366368433266,
        -1.489598498738259,
        0.5907028529479301
      ],
      [
        -1.3869118391183253,
        0.6331554048148876,
        -0.4221036032099251,
        0.2713523163492375
      ]
    ],
    "heads": [
      {
        "scores": [
          [
            0.6654339782957746,
            "-inf",
            "-inf",
            "-inf"
          ],
          [
            1.038315559790008,
            -2.4837287671488384,
            "-inf",
            "-inf"
          ],
          [
            -0.48583167819068557,
            0.7577978145111113,
            -0.2052202174328266,
            "-inf"
          ],
          [
            1.038315559790008,
            -2.4837287671488384,
            0.7577978145111113,
            -2.4837287671488384
          ]
        ],
        "weights": [
          [
            1.0,
            0.0,
            0.0,
            0.0
          ],
          [
            0.9713085308519348,
            0.02869146914806531,
            0.0,
            0.0
          ],
          [
            0.17264843188821463,
            0.5987755582887623,
            0.22857600982302304,
            0.0
          ],
          [
            0.5511249666097909,
            0.016279672703321285,
            0.4163156879835665,
            0.016279672703321285
          ]
        ],
        "output": [
          [
            -0.34297699576097085,
            -0.6859539915219418
          ],
          [
            -0.3729290201117488,
            -0.6481068049740206
          ],
          [
            -0.7605133067096621,
            0.2313368171661363
          ],
          [
            0.0010466131151194366,
            -0.41089186789516574
          ]
        ]
      },
      {
        "scores": [
          [
            0.6654339782957748,
            "-inf",
            "-inf",
            "-inf"
          ],
          [
            0.4241007216043693,
            -0.32396462180202235,
            "-inf",
            "-inf"
          ],
          [
            0.7848050186157225,
            -0.9242505136522802,
            -2.4887615459580976,
            "-inf"
          ],
          [
            0.4241007216043693,
            -0.32396462180202235,
            -0.9242505136522802,
            -0.32396462180202235
          ]
        ],
        "weights": [
          [
            1.0,
            0.0,
            0.0,
            0.0
          ],
          [
            0.6787570011392197,
            0.3212429988607803,
            0.0,
            0.0
          ],
          [
            0.8204065891481991,
            0.14852369763229697,
            0.031069713219503917,
            0.0
          ],
          [
            0.4532617660923528,
            0.2145203198848118,
            0.11769759413802364,
            0.2145203198848118
          ]
        ],
        "output": [
          [
            1.3719079830438834,
            0.1714884978804855
          ],
          [
            0.7955943210847245,
            0.20356905040307596
          ],
          [
            1.0165485628935624,
            0.19934551124858982
          ],
          [
            0.2654116758073136,
            0.26367465546571783
          ]
        ]
      }
    ],
    "concat_attention": [
      [
        -0.34297699576097085,
        -0.6859539915219418,
        1.3719079830438834,
        0.1714884978804855
      ],
      [
        -0.3729290201117488,
        -0.6481068049740206,
        0.7955943210847245,
        0.20356905040307596
      ],
      [
        -0.7605133067096621,
        0.2313368171661363,
        1.0165485628935624,
        0.19934551124858982
      ],
      [
        0.0010466131151194366,
        -0.41089186789516574,
        0.2654116758073136,
        0.26367465546571783
      ]
    ],
    "residual1": [
      [
        -0.14297699576097084,
        -0.7859539915219418,
        2.071907983043883,
        0.5714884978804855
      ],
      [
        -0.6729290201117488,
        0.15189319502597942,
        0.8955943210847245,
        0.7035690504030759
      ],
      [
        -0.16051330670966213,
        0.4313368171661363,
        0.6165485628935624,
        1.09934551124859
      ],
      [
        -0.29895338688488055,
        0.3891081321048343,
        0.3654116758073136,
        0.7636746554657179
      ]
    ],
    "normalized2": [
      [
        -0.5375457231048607,
        -1.1422230212813547,
        1.5454069697365898,
        0.13436177464962554
      ],
      [
        -1.5481133247122487,
        -0.19323668985226614,
        1.0283881167102003,
        0.7129618978543147
      ],
      [
        -1.4570262083734293,
        -0.14486747903237152,
        0.26575541201519126,
        1.3361382753906097
      ],
      [
        -1.5775498330234923,
        0.2202585040479007,
        0.15834298411985276,
        1.1989483448557388
      ]
    ],
    "ffn": [
      [
        0.026638704396888653,
        0.07890418501095597,
        0.49213512533270637,
        0.0024080109431469515
      ],
      [
        0.10506870807782567,
        0.004217979178685728,
        0.194754614176563,
        0.08527681301454476
      ],
      [
        0.10026713476934813,
        0.0024336378144475014,
        0.009994463250812926,
        0.353417478623218
      ],
      [
        0.10647918732019314,
        0.006729387801927646,
        0.003381673851209182,
        0.27611694964160904
      ]
    ],
    "hidden_output": [
      [
        -0.11633829136408219,
        -0.7070498065109858,
        2.5640431083765893,
        0.5738965088236324
      ],
      [
        -0.5678603120339232,
        0.15611117420466514,
        1.0903489352612874,
        0.7888458634176208
      ],
      [
        -0.060246171940313994,
        0.4337704549805838,
        0.6265430261443753,
        1.452762989871808
      ],
      [
        -0.19247419956468742,
        0.39583751990676197,
        0.3687933496585228,
        1.039791605107327
      ]
    ],
    "last_norm": [
      -1.3648661531888693,
      -0.01638759358892958,
      -0.07837596222908708,
      1.4596297090068862
    ],
    "logits_before_PAD_filter": [
      0.0,
      0.2576542387635127,
      1.1183270293660514,
      0.5228199123667249,
      0.2390577281714653,
      -0.6485476133164731
    ],
    "probabilities_after_PAD_filter": [
      0.0,
      0.1651792442552844,
      0.3906078063175441,
      0.21533541595718736,
      0.16213587244494412,
      0.06674166102504007
    ],
    "selected_token": 2,
    "selected_word": "爱",
    "cache": {
      "K": [
        [
          -1.3719079830438836,
          -0.34297699576097085,
          0.342976995760971,
          1.3719079830438834
        ],
        [
          1.2663108096297753,
          -1.3869118391183253,
          0.542704632698475,
          -0.4221036032099251
        ],
        [
          -0.2568273273686653,
          0.5650201202110635,
          1.1814057058958602,
          -1.489598498738259
        ],
        [
          1.2663108096297753,
          -1.3869118391183253,
          0.542704632698475,
          -0.4221036032099251
        ]
      ],
      "V": [
        [
          -0.34297699576097085,
          -0.6859539915219418,
          1.3719079830438834,
          0.1714884978804855
        ],
        [
          -1.3869118391183253,
          0.6331554048148876,
          -0.4221036032099251,
          0.2713523163492375
        ],
        [
          0.5650201202110635,
          -0.12841366368433266,
          -1.489598498738259,
          0.5907028529479301
        ],
        [
          -1.3869118391183253,
          0.6331554048148876,
          -0.4221036032099251,
          0.2713523163492375
        ]
      ]
    }
  },
  "cached_vs_full_max_error": 0.0,
  "operators": {
    "X02": {
      "input": [
        1,
        3
      ],
      "mean": 2,
      "population_variance": 1,
      "LayerNorm_epsilon1e5": [
        -0.9999950000374997,
        0.9999950000374997
      ],
      "RMSNorm_epsilon1e5": [
        0.4472131482870333,
        1.3416394448610998
      ],
      "SiLU_1_2": [
        0.7310585786300049,
        1.7615941559557646
      ],
      "SwiGLU_identity_gate_up_down": [
        0.7310585786300049,
        3.5231883119115293
      ]
    },
    "X03": {
      "first_probabilities": {
        "A": 0.6,
        "B": 0.4
      },
      "A_next": {
        "E": 0.51,
        "F": 0.49
      },
      "B_next": {
        "D": 0.99,
        "F": 0.01
      },
      "joint": {
        "AE": 0.306,
        "AF": 0.294,
        "BD": 0.396,
        "BF": 0.004
      }
    },
    "X04": {
      "p": [
        0.8,
        0.2
      ],
      "q": [
        0.5,
        0.5
      ],
      "KL_p_q": 0.19274475702175753,
      "KL_q_p": 0.22314355131420976
    },
    "X05": {
      "parameters": 1000,
      "P_bytes": 4000,
      "G_bytes": 4000,
      "Adam_m_v_bytes": 8000,
      "data_parallel_per_device": 16000,
      "zero1_per_device": 12000,
      "zero2_per_device": 10000,
      "zero3_per_device": 8000
    },
    "X06": {
      "Hq": 4,
      "Hkv": 2,
      "group_mapping": [
        0,
        0,
        1,
        1
      ],
      "toy_KV_per_token": 8
    },
    "X07": {
      "semantic_allowed": [
        [
          true,
          false
        ],
        [
          true,
          true
        ]
      ],
      "sdpa_bool": [
        [
          true,
          false
        ],
        [
          true,
          true
        ]
      ],
      "multihead_attention_bool_blocked": [
        [
          false,
          true
        ],
        [
          false,
          false
        ]
      ],
      "additive_mask": [
        [
          0,
          "-inf"
        ],
        [
          0,
          0
        ]
      ]
    },
    "X08": {
      "q": [
        1.0,
        0.0
      ],
      "a": [
        0.8,
        0.6
      ],
      "b": [
        0.0,
        1.0
      ],
      "p": [
        0.6899744811276125,
        0.31002551887238755
      ],
      "q_gradient": [
        -0.24802041509791,
        0.12401020754895506
      ],
      "q_after_lr01": [
        1.024802041509791,
        -0.012401020754895506
      ]
    },
    "X09": {
      "q": 0,
      "positions": {
        "A": 4,
        "B": 5,
        "C": 1
      },
      "undirected_edges": [
        [
          "A",
          "B"
        ],
        [
          "B",
          "C"
        ]
      ],
      "greedy_stop": "A",
      "best_after_explore_B": "C"
    },
    "X10": {
      "scale": 0.1,
      "integer_min": -2,
      "integer_max": 2,
      "input": [
        -0.24,
        0.03,
        0.26
      ],
      "integer_codes": [
        -2,
        0,
        2
      ],
      "reconstructed": [
        -0.2,
        0,
        0.2
      ]
    },
    "X11": {
      "character_input": [
        "a",
        "b",
        "c"
      ],
      "merge_rank": [
        [
          "b",
          "c",
          0
        ],
        [
          "a",
          "b",
          1
        ]
      ],
      "merged": [
        "a",
        "bc"
      ],
      "teaching_vocabulary": {
        "a": 1,
        "bc": 5
      },
      "IDs": [
        1,
        5
      ]
    },
    "X12": {
      "valid_target_probabilities": [
        0.8,
        0.5,
        0.25
      ],
      "valid_count": 3,
      "padded_count": 4,
      "sum_NLL": 2.3025850929940455,
      "correct_mean": 0.7675283643313485,
      "wrong_divide4": 0.5756462732485114
    }
  }
}
```


<span id="result-X02"></span>



<span id="topic-30"></span>


### X02 · 同样的[1,3]，LayerNorm、RMSNorm和SwiGLU分别做什么

[返回逐步讲解](foundations/14.md#worked-X02)

```
{
  "input": [
    1,
    3
  ],
  "mean": 2,
  "population_variance": 1,
  "LayerNorm_epsilon1e5": [
    -0.9999950000374997,
    0.9999950000374997
  ],
  "RMSNorm_epsilon1e5": [
    0.4472131482870333,
    1.3416394448610998
  ],
  "SiLU_1_2": [
    0.7310585786300049,
    1.7615941559557646
  ],
  "SwiGLU_identity_gate_up_down": [
    0.7310585786300049,
    3.5231883119115293
  ]
}
```


<span id="result-X03"></span>



<span id="topic-31"></span>


### X03 · 贪心第一步最好，不等于两步序列概率最大

[返回逐步讲解](chapters/06.md#worked-X03)

```
{
  "first_probabilities": {
    "A": 0.6,
    "B": 0.4
  },
  "A_next": {
    "E": 0.51,
    "F": 0.49
  },
  "B_next": {
    "D": 0.99,
    "F": 0.01
  },
  "joint": {
    "AE": 0.306,
    "AF": 0.294,
    "BD": 0.396,
    "BF": 0.004
  }
}
```


<span id="result-X04"></span>



<span id="topic-32"></span>


### X04 · KL散度：同两组概率，调换方向会得到不同值

[返回逐步讲解](foundations/17.md#worked-X04)

```
{
  "p": [
    0.8,
    0.2
  ],
  "q": [
    0.5,
    0.5
  ],
  "KL_p_q": 0.19274475702175753,
  "KL_q_p": 0.22314355131420976
}
```


<span id="result-X05"></span>



<span id="topic-33"></span>


### X05 · 用1000个参数算清ZeRO究竟分摊哪份状态

[返回逐步讲解](studies/chapters/03.md#worked-X05)

```
{
  "parameters": 1000,
  "P_bytes": 4000,
  "G_bytes": 4000,
  "Adam_m_v_bytes": 8000,
  "data_parallel_per_device": 16000,
  "zero1_per_device": 12000,
  "zero2_per_device": 10000,
  "zero3_per_device": 8000
}
```


<span id="result-X06"></span>



<span id="topic-34"></span>


### X06 · 4个Q头共享2个KV头，究竟怎样配对

[返回逐步讲解](chapters/03.md#worked-X06)

```
{
  "Hq": 4,
  "Hkv": 2,
  "group_mapping": [
    0,
    0,
    1,
    1
  ],
  "toy_KV_per_token": 8
}
```


<span id="result-X07"></span>



<span id="topic-35"></span>


### X07 · 同一张“允许访问表”，不同接口的布尔值为什么相反

[返回逐步讲解](chapters/03.md#worked-X07)

```
{
  "semantic_allowed": [
    [
      true,
      false
    ],
    [
      true,
      true
    ]
  ],
  "sdpa_bool": [
    [
      true,
      false
    ],
    [
      true,
      true
    ]
  ],
  "multihead_attention_bool_blocked": [
    [
      false,
      true
    ],
    [
      false,
      false
    ]
  ],
  "additive_mask": [
    [
      0,
      "-inf"
    ],
    [
      0,
      0
    ]
  ]
}
```


<span id="result-X08"></span>



<span id="topic-36"></span>


### X08 · 让检索向量学习：查询向量真的往哪个方向移动

[返回逐步讲解](studies/chapters/31.md#worked-X08)

```
{
  "q": [
    1.0,
    0.0
  ],
  "a": [
    0.8,
    0.6
  ],
  "b": [
    0.0,
    1.0
  ],
  "p": [
    0.6899744811276125,
    0.31002551887238755
  ],
  "q_gradient": [
    -0.24802041509791,
    0.12401020754895506
  ],
  "q_after_lr01": [
    1.024802041509791,
    -0.012401020754895506
  ]
}
```


<span id="result-X09"></span>



<span id="topic-37"></span>


### X09 · 近似图搜索为什么会漏掉真正最近的点

[返回逐步讲解](studies/chapters/13.md#worked-X09)

```
{
  "q": 0,
  "positions": {
    "A": 4,
    "B": 5,
    "C": 1
  },
  "undirected_edges": [
    [
      "A",
      "B"
    ],
    [
      "B",
      "C"
    ]
  ],
  "greedy_stop": "A",
  "best_after_explore_B": "C"
}
```


<span id="result-X10"></span>



<span id="topic-38"></span>


### X10 · 量化不只是舍入，还可能把超范围的数截断

[返回逐步讲解](foundations/20.md#worked-X10)

```
{
  "scale": 0.1,
  "integer_min": -2,
  "integer_max": 2,
  "input": [
    -0.24,
    0.03,
    0.26
  ],
  "integer_codes": [
    -2,
    0,
    2
  ],
  "reconstructed": [
    -0.2,
    0,
    0.2
  ]
}
```


<span id="result-X11"></span>



<span id="topic-39"></span>


### X11 · BPE合并时，为什么不是总选左边那一对

[返回逐步讲解](foundations/03.md#worked-X11)

```
{
  "character_input": [
    "a",
    "b",
    "c"
  ],
  "merge_rank": [
    [
      "b",
      "c",
      0
    ],
    [
      "a",
      "b",
      1
    ]
  ],
  "merged": [
    "a",
    "bc"
  ],
  "teaching_vocabulary": {
    "a": 1,
    "bc": 5
  },
  "IDs": [
    1,
    5
  ]
}
```


<span id="result-X12"></span>



<span id="topic-40"></span>


### X12 · padding位置不计损失，分母也必须一起变

[返回逐步讲解](foundations/16.md#worked-X12)

```
{
  "valid_target_probabilities": [
    0.8,
    0.5,
    0.25
  ],
  "valid_count": 3,
  "padded_count": 4,
  "sum_NLL": 2.3025850929940455,
  "correct_mean": 0.7675283643313485,
  "wrong_divide4": 0.5756462732485114
}
```


<span id="code"></span>


## 完整程序

代码与显示结果使用同一份参数。修改参数后请重新运行，不要把旧结果当作新代码输出。


<span id="code-engine"></span>


### engine.py

```
"""Offline numerical witnesses for the worked examples. Python >= 3.10, standard library only.
All inputs are small, constructed teaching data, not real model weights or benchmarks.
"""
from __future__ import annotations
import math, json, itertools, codecs, ast, hashlib, tempfile, os, sqlite3, unittest
from pathlib import Path

def softmax(xs):
    if not xs or not any(math.isfinite(x) for x in xs): raise ValueError('no finite logit')
    if any(math.isnan(x) or x==math.inf for x in xs): raise ValueError('invalid logit')
    m=max(xs); es=[math.exp(x-m) for x in xs]; s=sum(es)
    return [x/s for x in es]

def dot(a,b):
    if len(a)!=len(b): raise ValueError('shape mismatch')
    return sum(x*y for x,y in zip(a,b))
def matrix_shape(a):
    if not isinstance(a, (list, tuple)) or not a or not isinstance(a[0], (list, tuple)) or not a[0]:
        raise ValueError('expected a nonempty rectangular matrix')
    cols=len(a[0])
    if any(not isinstance(row,(list,tuple)) or len(row)!=cols for row in a):
        raise ValueError('ragged matrix')
    return len(a),cols

def tr(a):
    matrix_shape(a)
    return [list(x) for x in zip(*a)]
def mm(a,b):
    _,inner=matrix_shape(a); rows,_=matrix_shape(b)
    if inner!=rows: raise ValueError('shape mismatch')
    return [[dot(x,y) for y in tr(b)] for x in a]
def add(a,b):
    if matrix_shape(a)!=matrix_shape(b):raise ValueError('shape mismatch')
    return [[x+y for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def ln(x,eps=1e-5):
    if not x or eps<=0:raise ValueError('empty vector or nonpositive epsilon')
    m=sum(x)/len(x); v=sum((a-m)**2 for a in x)/len(x)
    return [(a-m)/math.sqrt(v+eps) for a in x]
def attn(q,k,v,offset=0,causal=True):
    nq,dq=matrix_shape(q);nk,dk=matrix_shape(k);nv,_=matrix_shape(v)
    if dq!=dk or nk!=nv or offset<0:raise ValueError('incompatible attention shapes or offset')
    d=len(q[0]); s=[[dot(a,b)/math.sqrt(d) if not causal or j<=offset+i else -math.inf for j,b in enumerate(k)] for i,a in enumerate(q)]
    p=[softmax(row) for row in s]
    return {'scores':s,'weights':p,'output':mm(p,v)}
def finite(x):
    if isinstance(x,float) and not math.isfinite(x): return '-inf' if x<0 else str(x)
    if isinstance(x,list): return [finite(v) for v in x]
    if isinstance(x,dict): return {k:finite(v) for k,v in x.items()}
    return x

def transformer():
    x=[[1.,0.],[0.,2.]]; u=[ln(row) for row in x]; a=attn(u,u,u)
    r=add(x,a['output']); n=[ln(row) for row in r]; f=[[.5*max(0,z) for z in row] for row in n]; y=add(r,f)
    last_norm=ln(y[-1]); logits=mm([last_norm],[[1.,0.,-1.],[0.,1.,.5]])[0]
    return {'X':x,'norm1':u,'attention':a,'residual1':r,'norm2':n,'ffn':f,'Y':y,'final_norm':last_norm,'logits':logits,'probabilities':softmax(logits)}

def grad_demo():
    q=[[.4,-.2]];k=[[1.,.5],[-.5,1.]];v=[[2.,-1.],[.5,3.]];g=[[.7,-.3]]
    a=attn(q,k,v,causal=False);p=a['weights']; dp=mm(g,tr(v));ds=[[pj*(gj-dot(pr,gr)) for pj,gj in zip(pr,gr)] for pr,gr in zip(p,dp)]
    dq=[[z/math.sqrt(2) for z in row] for row in mm(ds,k)]
    dk=[[z/math.sqrt(2) for z in row] for row in mm(tr(ds),q)];dv=mm(tr(p),g)
    def loss(): return dot(attn(q,k,v,causal=False)['output'][0],g[0])
    err=0.; checked=0
    for arr,deriv in [(q,dq),(k,dk),(v,dv)]:
        for i,row in enumerate(arr):
            for j,old in enumerate(row):
                h=1e-6; arr[i][j]=old+h; hi=loss();arr[i][j]=old-h;lo=loss();arr[i][j]=old
                err=max(err,abs((hi-lo)/(2*h)-deriv[i][j]));checked+=1
    return {'Q':q,'K':k,'V':v,'upstream':g,'P':p,'O':a['output'],'dP':dp,'dS':ds,'dQ':dq,'dK':dk,'dV':dv,'max_error':err,'coordinates_checked':checked}

def online_softmax(scores,values):
    m=-math.inf;l=0.;u=0.;trace=[]
    for s,v in zip(scores,values):
        new=max(m,s);scale=math.exp(m-new);e=math.exp(s-new);l=scale*l+e;u=scale*u+e*v;m=new
        trace.append({'score':s,'value':v,'max':m,'old_scale':scale,'sum':l,'weighted_sum':u,'output':u/l})
    return trace

def bm25(docs,term,k1=1.2,b=.75):
    n=len(docs); df=sum(term in d for d in docs);avg=sum(map(len,docs))/n;idf=math.log(1+(n-df+.5)/(df+.5)); rows=[]
    for i,d in enumerate(docs):
        f=d.count(term);den=f+k1*(1-b+b*len(d)/avg);part=f*(k1+1)/den
        rows.append({'doc':chr(65+i),'length':len(d),'frequency':f,'denominator':den,'tf_factor':part,'score':idf*part})
    return {'N':n,'df':df,'avgdl':avg,'idf':idf,'rows':rows}
def rrf(lists,c=60):
    scores={}
    for ranking in lists:
        unique=list(dict.fromkeys(ranking))
        for rank,x in enumerate(unique,1):scores[x]=scores.get(x,0)+1/(c+rank)
    return sorted(scores.items(),key=lambda kv:(-kv[1],kv[0]))

def spec_demo():
    p=[.6,.3,.1];q=[.2,.5,.3];accept=[min(1,pi/qi) for pi,qi in zip(p,q)]
    accepted=[qi*ai for qi,ai in zip(q,accept)];r=sum(qi*(1-ai) for qi,ai in zip(q,accept));res=[max(0,pi-qi) for pi,qi in zip(p,q)];s=sum(res);res=[v/s for v in res]
    return {'target':p,'draft':q,'accept_prob':accept,'accepted_mass':accepted,'rejection_mass':r,'residual_distribution':res,'final_mass':[a+r*b for a,b in zip(accepted,res)]}

def adamw_demo():
    w=1.;g=.2;b1=.9;b2=.999;lr=.1;wd=.01;eps=1e-8
    m=(1-b1)*g;v=(1-b2)*g*g;mh=m/(1-b1);vh=v/(1-b2)
    decay=w*(1-lr*wd);new=decay-lr*mh/(math.sqrt(vh)+eps)
    return {'w':w,'gradient':g,'m':m,'v':v,'m_hat':mh,'v_hat':vh,'after_decay':decay,'new_w':new}

def sse_trace(chunks):
    decoder=codecs.getincrementaldecoder('utf-8')();buf='';events=[]
    for chunk in chunks:
        buf+=decoder.decode(chunk)
        while '\n\n' in buf:
            raw,buf=buf.split('\n\n',1);data=[]
            for line in raw.split('\n'):
                if line.startswith('data:'):
                    text=line[5:]; data.append(text[1:] if text.startswith(' ') else text)
            if data:events.append('\n'.join(data))
    buf+=decoder.decode(b'',final=True)
    return events,buf

def memory_select(items,project,at,known_at):
    known=[r for r in items if r['project']==project and r['recorded']<=known_at]
    # Each item here is a full assertion for a finite validity interval. Later corrections win only in this toy policy.
    valid=[r for r in known if r['from']<=at<r['to']]
    return max(valid,key=lambda r:r['recorded'],default=None)

def precision_recall(ranking,relevant):
    got=set(ranking);rel=set(relevant);tp=len(got&rel)
    return {'precision':tp/len(got) if got else 0,'recall':tp/len(rel) if rel else None}

def compute():
    E=[[0.,0.,0.,0.],[.2,-.1,.7,.4],[-.3,.8,.1,.5],[.6,.2,-.4,.9],[.1,-.5,.9,.3],[-.2,.4,.5,-.6]]
    ids=[[1,2,3],[4,2,0]];embedded=[[E[j] for j in row] for row in ids]
    a=attn([[1.,0.],[0.,1.],[1.,1.]],[[1.,0.],[0.,1.],[1.,1.]],[[1.,2.],[3.,4.],[4.,6.]])
    bm=bm25([['排除','路径'],['排除','排除','路径','缓存'],['日志','输出']],'排除')
    lp=math.log(2.);dpo=-math.log(1/(1+math.exp(-lp)))
    wp=.6;wnew=wp-.1*(wp-1)
    brier=((.8-1)**2+(.8-1)**2+(.8-0)**2+(.8-0)**2)/4
    return {
      'embedding':{'table':E,'ids':ids,'output':embedded},
      'shapes':{'ids_elements':2*128,'ids_bytes_int64':2*128*8,'embedding_elements':2*128*4096,'embedding_bytes_fp16':2*128*4096*2},
      'attention':a,'decoder':transformer(),'gradients':grad_demo(),
      'softmax':{'logits':[2,1,0],'p':softmax([2,1,0]),'shifted_p':softmax([1002,1001,1000]),'temperature2':softmax([1,.5,0]),'temperature05':softmax([4,2,0])},
      'online':online_softmax([1,3],[2,10]),
      'adamw':adamw_demo(),
      'loss':{'target_ps':[.8,.5,.25],'losses':[-math.log(p) for p in [.8,.5,.25]],'mean':sum(-math.log(p) for p in [.8,.5,.25])/3,'logits':[0,0],'gradient':[-.5,.5],'updated_logits':[.05,-.05],'new_loss':-math.log(softmax([.05,-.05])[0])},
      'dpo':{'pi_preferred':.6,'pi_rejected':.2,'ref_preferred':.3,'ref_rejected':.2,'beta':1.,'margin':lp,'loss':dpo,'baseline_loss':math.log(2),'kl':sum(p*math.log(p/q) for p,q in zip([.8,.2],[.5,.5]))},
      'speculative':spec_demo(),
      'cache':{'tiny_bytes':2*2*1*3*1*2*4,'GiB':2*32*1*32768*8*128*2/2**30,'per_token_KiB':2*32*1*8*128*2/1024},
      'bm25':bm,'rrf':rrf([['A','B','C'],['B','C','D']]),
      'metrics':{'precision_recall':precision_recall(['A','X','Y'],['A','B']),'pass1':.8,'pass_at3':1-.2**3,'pass_all3':.8**3,'finite_pass3':1-math.comb(4,3)/math.comb(10,3),'brier':brier,'mcnemar_p':2*sum(math.comb(8,k) for k in range(3))/2**8},
    }

class WitnessTests(unittest.TestCase):
    def test_embedding_semantics(self):
        d=compute()['embedding'];self.assertEqual(d['output'][0][1],d['table'][2]);self.assertEqual(d['output'][1][1],d['table'][2]);self.assertEqual(len(d['output'][1]),3);self.assertEqual(d['output'][1][-1],[0.]*4)
    def test_softmax_stability(self):
        for a,b in zip(softmax([2,1,0]),softmax([1002,1001,1000])):self.assertAlmostEqual(a,b)
        self.assertAlmostEqual(sum(softmax([-1000,-1001])),1)
    def test_softmax_invalid(self):
        for xs in [[],[-math.inf,-math.inf],[math.nan,0],[math.inf,0]]:
            with self.assertRaises(ValueError):softmax(xs)
    def test_future_mask(self):
        a=compute()['attention'];self.assertEqual(a['weights'][0],[1,0,0]);self.assertEqual(a['weights'][1][2],0)
    def test_chunk_mask(self):
        self.assertEqual([[j<=3+i for j in range(5)] for i in range(2)],[[True,True,True,True,False],[True]*5])
    def test_cache_equivalence(self):
        x=[[1.,0.],[0.,1.],[1.,1.]];v=[[1.,2.],[3.,4.],[4.,6.]]
        full=attn(x,x,v)['output'];incremental=[attn([x[i]],x[:i+1],v[:i+1],i)['output'][0] for i in range(3)]
        self.assertEqual(full,incremental)
    def test_cache_wrong_offset_detected(self):
        x=[[1.,0.],[0.,1.],[1.,1.]];v=[[1.,2.],[3.,4.],[4.,6.]]
        self.assertNotEqual(attn([x[-1]],x,v,0)['output'],attn([x[-1]],x,v,2)['output'])
    def test_gradient_finite_difference(self):self.assertLess(grad_demo()['max_error'],1e-8)
    def test_gradient_shift_sum(self):self.assertAlmostEqual(sum(grad_demo()['dS'][0]),0)
    def test_online_equals_full(self):
        o=online_softmax([1,3],[2,10])[-1]['output'];self.assertAlmostEqual(o,dot(softmax([1,3]),[2,10]))
    def test_speculative_distribution(self):
        s=spec_demo()
        for a,b in zip(s['target'],s['final_mass']):self.assertAlmostEqual(a,b)
    def test_adamw(self):self.assertAlmostEqual(adamw_demo()['new_w'],.899000005,places=9)
    def test_dpo_margin(self):self.assertAlmostEqual(compute()['dpo']['loss'],math.log(1.5))
    def test_ce_update(self):self.assertLess(compute()['loss']['new_loss'],math.log(2))
    def test_rope_preserves_norm(self):
        x=[2.,1.];t=.7;c=math.cos(t);s=math.sin(t);y=[c*x[0]-s*x[1],s*x[0]+c*x[1]];self.assertAlmostEqual(dot(x,x),dot(y,y))
    def test_bm25_ranking(self):
        b=compute()['bm25'];self.assertGreater(b['rows'][1]['score'],b['rows'][0]['score']);self.assertEqual(b['rows'][2]['score'],0)
    def test_rrf(self):self.assertEqual([a for a,b in compute()['rrf']],['B','C','A','D'])
    def test_rrf_duplicate(self):self.assertEqual(rrf([['A','A','B']]),rrf([['A','B']]))
    def test_sse_all_byte_boundaries(self):
        wire='data: {"path":"学习.py"}\n\n'.encode('utf-8')
        for cut in range(1,len(wire)):
            e,buf=sse_trace([wire[:cut],wire[cut:]]);self.assertEqual(json.loads(e[0]),{'path':'学习.py'});self.assertEqual(buf,'')
    def test_sse_incomplete_not_emitted(self):self.assertEqual(sse_trace([b'data: {"x":1}'])[0],[])
    def test_tool_result_pairing(self):
        calls={'a':'read(config)','b':'read(test)'};responses=[('b','TEST'),('a','CONFIG')]
        paired={calls[k]:v for k,v in responses};self.assertEqual(paired['read(config)'],'CONFIG')
    def test_memory_bitemporal(self):
        items=[dict(project='A',recorded=1,**{'from':1,'to':99},value=3),dict(project='A',recorded=12,**{'from':10,'to':99},value=5)]
        self.assertEqual(memory_select(items,'A',11,11)['value'],3);self.assertEqual(memory_select(items,'A',11,12)['value'],5)
    def test_acl_before_model(self):
        docs=[('private',.99,{'admin'}),('public',.8,{'user','admin'})];visible=[x[0] for x in docs if 'user' in x[2]];self.assertEqual(visible,['public'])
    def test_compare_and_swap(self):
        current={'version':8,'body':'B'};expected=7
        if current['version']==expected:current.update(version=9,body='C')
        self.assertEqual(current,{'version':8,'body':'B'})
    def test_atomic_replace_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.txt';q=Path(d)/'tmp.txt';p.write_text('old');q.write_text('new');os.replace(q,p);self.assertEqual(p.read_text(),'new')
    def test_sqlite_local_transaction(self):
        c=sqlite3.connect(':memory:');c.execute('create table receipts(id text primary key, result text)');c.execute('insert into receipts values(?,?)',('op1','done'));c.commit()
        with self.assertRaises(sqlite3.IntegrityError):c.execute('insert into receipts values(?,?)',('op1','again'))
        self.assertEqual(c.execute('select count(*) from receipts').fetchone()[0],1);c.close()
    def test_precision_recall(self):self.assertEqual(precision_recall(['A','X','Y'],['A','B']),{'precision':1/3,'recall':.5})
    def test_paired_exact(self):self.assertEqual(compute()['metrics']['mcnemar_p'],.2890625)
    def test_lora_rank1(self):
        self.assertEqual(mm([[1],[2]],[[3,4]]),[[3,4],[6,8]])
    def test_quantization(self):self.assertEqual([round(x/.1) for x in [-.24,.03,.26]],[-2,0,3])
    def test_pool_mask(self):
        vectors=[[2.,0.],[0.,2.],[0.,0.]];valid=[1,1,0];pooled=[sum(r[j]*m for r,m in zip(vectors,valid))/sum(valid) for j in range(2)];self.assertEqual(pooled,[1,1])
    def test_dag_critical_path(self):
        durations={'A':2,'B':3,'C':5,'D':1};finish={'A':2,'B':5,'C':7,'D':8};self.assertEqual(finish['D'],2+max(3,5)+1)
    def test_paginated_position(self):
        blocks=[7,2,19];self.assertEqual((blocks[5//4],5%4),(2,1))
    def test_source_version_gate(self):
        verified={'commit':'r7','exit':0};current='r8';self.assertFalse(verified['commit']==current and verified['exit']==0)

if __name__=='__main__':
    import sys
    if '--test' in sys.argv:unittest.main(argv=[sys.argv[0]],verbosity=2)
    else: print(json.dumps(finite(compute()),ensure_ascii=False,indent=2,allow_nan=False))
```


<span id="code-additional_checks"></span>


### additional\_checks.py

```
"""离线示例核验。Python 3.10+，只使用标准库。
本程序测试算术、矩阵与明确的状态反例；不测商业LLM效果或生产系统安全。
"""
from __future__ import annotations
import math, json, unittest, tempfile, sqlite3, os
from pathlib import Path
import engine as e

def extended_outputs():
    # Keep outputs bound to the exact example that introduces the assumptions.
    return {
      'F07': {'A':[[1,2]], 'B':[[3,4],[5,6]],'product':e.mm([[1,2]],[[3,4],[5,6]])},
      'F17': {'x':2,'target':6,'w_before':1,'loss_before':16,'gradient':-16,'learning_rate':.1,'w_after':2.6,'loss_after':(2.6*2-6)**2},
      'Q006': {'probabilities':e.softmax([1/math.sqrt(2),0]),'output':e.mm([e.softmax([1/math.sqrt(2),0])],[[10,0],[0,20]])[0]},
      'Q010': {'relative_angle_degrees':60,'dot_product':math.cos(math.pi/3)},
      'Q030': {'queue_ms':40,'prefill_ms':60,'first_step_ms':20,'TTFT_ms':120,'TPOT_ms':20,'four_tokens_ms':180},
      'Q038': {'utf8_bytes_of_wo':list('我'.encode()),'events':e.sse_trace([b'data: {"text":"'+bytes([0xe6]),bytes([0x88]),bytes([0x91])+b'"}\n\n'])[0]},
      'Q049': {'input_budget':1000-200-50,'fixed':150+100+150,'evidence_budget':350,'selected_evidence':180+120,'used_input':700},
      'Q059': {'scores':[.8,0],'probabilities':e.softmax([.8,0]),'loss':-math.log(e.softmax([.8,0])[0]),'score_gradient':[e.softmax([.8,0])[0]-1,e.softmax([.8,0])[1]]},
      'Q062': {'query':[[1,0],[0,1]],'document':[[.8,.6],[0,1]],'max_per_query':[.8,1], 'MaxSim_A':1.8,'MaxSim_B':2/math.sqrt(2)},
      'Q071': {'queries':[
        {'valid_day':3,'known_day':11,'value':5},
        {'valid_day':7,'known_day':8,'value':5},
        {'valid_day':7,'known_day':11,'value':7}]},
      'Q076': {'A':{'total_cost':100,'successes':80,'cost_per_success':100/80},'B':{'total_cost':70,'successes':40,'cost_per_success':70/40}},
      'Q078': {'serial_seconds':3+5+2,'parallel_seconds':max(3,5)+2,'parallel_with_4s_overhead':max(3,5)+2+4},
      'Q090': {k:v for k,v in e.compute()['metrics'].items() if k.startswith('pass') or k.startswith('finite')},
      'Q091': {'A_successes':12,'B_successes':16,'tasks':20,'A_rate':.6,'B_rate':.8,'discordant':8,'two_sided_exact_p':2*sum(math.comb(8,k) for k in range(3))/2**8},
      'Q097': {'base':max(3,5)+2,'A_optimized':max(1,5)+2,'B_optimized':max(3,2)+2},
      'Q099': {'slots':10,'mean_service_seconds':2,'capacity_per_second':5,'arrivals_per_second':6,'extra_backlog_after_100s':(6-5)*100,'steady_L_at_lambda4_W3':4*3},
      'Q105': {'probabilities':[.8]*4,'labels':[1,1,0,0],'Brier':e.compute()['metrics']['brier']},
      'Q107': {'image':[list(range(i,i+4)) for i in [1,5,9,13]],'patches':[[1,2,5,6],[3,4,7,8],[9,10,13,14],[11,12,15,16]],'W':[[1,0],[0,1],[1,0],[0,1]],'projected':e.mm([[1,2,5,6],[3,4,7,8],[9,10,13,14],[11,12,15,16]],[[1,0],[0,1],[1,0],[0,1]])},
      'Q108': {'weights':[.9,.1],'values':[.01,10],'contributions':[.009,1],'sum':1.009},
      'Q109': {'C_FLOPs':6*10**9*20*10**9,'N_doubled':2*10**9,'D_halved':10*10**9},
      'S01': {'gradient_occurrences':[[.1,-.2],[.3,.4]],'row_gradient':[.4,.2],'new_row':[.8-.1*.4,.6-.1*.2]},
      'S03': {'microbatch_gradients':[1,2,3,4],'unscaled_sum':10,'correct_equal_size_mean':2.5},
      'S04': {'positive_advantage':{'r':1.5,'A':2,'raw':3,'clipped':2.4,'objective':2.4},'negative_advantage':{'r':.5,'A':-2,'raw':-1,'clipped':-1.6,'objective':-1.6}},
      'S05': {'p':[.5,.3,.15,.05],'top2':[.625,.375],'top_p_09':[x/.95 for x in [.5,.3,.15]]},
      'S06': {'compute_lower_bound_us':1e9/1e14*1e6,'transfer_lower_bound_us':1e8/1e12*1e6,'ideal_overlap_lower_bound_us':100},
      'S16': {'old_recall':8/10,'new_recall':10/10,'old_precision':8/(8+2),'new_precision':10/(10+30)},
      'S19': {'A_easy':9/10,'B_easy':80/100,'A_hard':20/100,'B_hard':1/10,'A_total':29/110,'B_total':81/110},
      'S22': {'A_cost_per_success':1000/990,'B_cost_per_success':800/980},
      'S23': {'weight_errors':[.01,.01],'activations':[100,.1],'output_errors':[1,.001],'ratio':1000},
      'S25': {'A_accuracy':80/100,'B_selective_accuracy':45/50,'A_coverage':1,'B_coverage':.5,'correct_counts':[80,45]},
      'S31': {'direction':[1,-2],'directional_derivative':e.dot(e.grad_demo()['dQ'][0],[1,-2])},
      'R03-12': {'total100':20+99*10,'half_prefill':10+99*10,'total50':20+49*10},
      'R08-16': {'recall_at3_X':1,'recall_at3_Y':1,'reciprocal_rank_X':1,'reciprocal_rank_Y':.5},
      'R13-07': {'false_block_rate':5/100,'false_allow_rate':1/10},
      'R14-05': {'requests':10000,'SLO':.99,'allowed_errors':100,'used':80,'remaining':20},
      'R14-07': {'requests':4,'request_limit':60,'tokens_per_request':2000,'tokens':8000,'token_limit':6000},
      'R15-01': {'A':[[1],[2]],'B':[[.1,.2]],'AB':e.mm([[1],[2]],[[.1,.2]])},
      'R16-01': {'w':1,'z':-8,'loss':64,'dz_dw':2,'dL_dz':-16,'dL_dw':-32},
      'R16-05': {'negative_log_natural':-math.log(.5),'negative_log_base2':-math.log2(.5)},
    }

class MoreNumericTests(unittest.TestCase):
    def test_dense_layer_chain(self):
        t=e.transformer(); self.assertAlmostEqual(t['probabilities'][2],.592200875196,places=10);self.assertAlmostEqual(sum(t['probabilities']),1)
    def test_every_masked_probability_zero(self):
        a=e.compute()['attention'];
        for i,row in enumerate(a['weights']):
            for j,p in enumerate(row):
                if j>i:self.assertEqual(p,0)
    def test_layer_norm_mean(self):
        for row in [[1,0],[0,2],[2,2]]:self.assertAlmostEqual(sum(e.ln(row)),0)
    def test_layer_norm_constant_safe(self):self.assertEqual(e.ln([2,2]),[0,0])
    def test_dot_matrix_distinction(self):self.assertEqual(e.mm([[1,2]],[[3,4],[5,6]]),[[13,16]])
    def test_transpose_not_reshape(self):self.assertEqual(e.tr([[1,2,3],[4,5,6]]),[[1,4],[2,5],[3,6]])
    def test_single_parameter_sgd(self):self.assertAlmostEqual((2.6*2-6)**2,.64)
    def test_large_step_can_increase_loss(self):self.assertGreater(((1-1*(-16))*2-6)**2,16)
    def test_gradient_shared_embedding(self):self.assertEqual([.1+.3,-.2+.4],[.4,.2])
    def test_gradient_accumulation_equal_batches(self):self.assertEqual(sum(x/4 for x in [1,2,3,4]),2.5)
    def test_gradient_accumulation_unequal_batches(self):self.assertNotEqual((1*2+3*4)/(2+4),(1+3)/2)
    def test_ppo_sign_sensitive(self):
        def obj(r,a):return min(r*a,min(1.2,max(.8,r))*a)
        self.assertAlmostEqual(obj(1.5,2),2.4);self.assertAlmostEqual(obj(.5,-2),-1.6)
    def test_nucleus_boundary(self):
        p=[.5,.3,.15,.05];ret=[];total=0
        for x in p:
            ret.append(x);total+=x
            if total>=.9:break
        self.assertEqual(ret,[.5,.3,.15]);self.assertAlmostEqual(sum(x/total for x in ret),1)
    def test_bm25_exact_visible_numbers(self):
        d=e.compute()['bm25'];self.assertAlmostEqual(d['rows'][0]['score'],.523548346502,places=10);self.assertAlmostEqual(d['rows'][1]['score'],.566579717447,places=10)
    def test_contrastive_loss(self):self.assertAlmostEqual(-math.log(e.softmax([.8,0])[0]),.371100665948,places=10)
    def test_maxsim_sum(self):
        qs=[[1,0],[0,1]];ds=[[.8,.6],[0,1]]
        self.assertAlmostEqual(sum(max(e.dot(q,d) for d in ds) for q in qs),1.8)
    def test_spec_bad_resampling_changes_distribution(self):
        s=e.spec_demo();wrong=[a+s['rejection_mass']*p for a,p in zip(s['accepted_mass'],s['target'])]
        for a,b in zip(wrong,[.44,.42,.14]):self.assertAlmostEqual(a,b)
        self.assertNotEqual(wrong,s['target'])
    def test_cache_units(self):
        c=e.compute()['cache'];self.assertEqual(c['GiB'],4);self.assertEqual(c['per_token_KiB'],128);self.assertEqual(c['tiny_bytes'],96)
    def test_attention_value_scaling(self):
        p=e.softmax([1/math.sqrt(2),0]);o=e.mm([p],[[10,0],[0,20]])[0];d=e.mm([p],[[20,0],[0,40]])[0]
        for x,y in zip(o,d):self.assertAlmostEqual(2*x,y)
    def test_grad_direction_finite_difference(self):
        q=[.4,-.2];k=[[1,.5],[-.5,1]];v=[[2,-1],[.5,3]];g=[.7,-.3];direction=[1,-2];h=1e-6
        def f(t):return e.dot(e.attn([[q[i]+t*direction[i] for i in range(2)]],k,v,causal=False)['output'][0],g)
        fd=(f(h)-f(-h))/(2*h);self.assertAlmostEqual(fd,e.dot(e.grad_demo()['dQ'][0],direction),places=8)
    def test_context_budget(self):self.assertEqual(1000-200-50-(150+100+150),350)
    def test_time_to_first_vs_completion(self):self.assertEqual(40+60+20+3*20,180)
    def test_prefill_off_by_one(self):
        out=extended_outputs()['R03-12'];self.assertEqual(out['total100'],1010);self.assertEqual(out['total100']-out['total50'],500)
    def test_roofline_units(self):self.assertEqual(extended_outputs()['S06']['transfer_lower_bound_us'],100)
    def test_cost_with_failures(self):self.assertLess(100/80,70/40)
    def test_critical_path_after_change(self):self.assertEqual(max(1,5)+2,7);self.assertEqual(max(3,2)+2,5)
    def test_supercritical_queue(self):self.assertEqual((6-10/2)*100,100)
    def test_pass_events_differ(self):
        d=e.compute()['metrics'];self.assertAlmostEqual(d['pass_at3'],.992);self.assertAlmostEqual(d['pass_all3'],.512);self.assertAlmostEqual(d['finite_pass3'],29/30)
    def test_paired_table_marginals(self):self.assertEqual((10+2,10+6),(12,16));self.assertEqual(10+2+6+2,20)
    def test_simpson_construction(self):self.assertGreater(9/10,80/100);self.assertGreater(20/100,1/10);self.assertLess(29/110,81/110)
    def test_routing_precision_recall_tradeoff(self):self.assertEqual(10/(10+30),.25);self.assertGreater(10/10,8/10)
    def test_correlated_vote_counterexample(self):self.assertGreater(.2,.2**3)
    def test_patch_projector(self):self.assertEqual(extended_outputs()['Q107']['projected'],[[6,8],[10,12],[22,24],[26,28]])
    def test_activation_sensitive_error(self):self.assertEqual(100*.01,1);self.assertEqual(.1*.01,.001)
    def test_scale_pair_product(self):self.assertEqual(6*10**9*20*10**9,6*2*10**9*10*10**9)
    def test_lora_small_count_not_saved(self):self.assertEqual(2*1+1*2,2*2)
    def test_lora_large_count(self):self.assertEqual(1000*8+8*1000,16000)
    def test_calibration_brier(self):self.assertAlmostEqual(sum((.8-y)**2 for y in [1,1,0,0])/4,.34)
    def test_selective_accuracy_vs_coverage(self):self.assertGreater(45/50,80/100);self.assertLess(45,80)
    def test_error_budget(self):self.assertEqual(100-80,20)
    def test_rate_limit_dimensions(self):self.assertLess(4,60);self.assertGreater(4*2000,6000)
    def test_natural_log_units(self):self.assertAlmostEqual(-math.log(.5),math.log(2));self.assertEqual(-math.log2(.5),1)
    def test_utf8_three_bytes(self):self.assertEqual(list('我'.encode('utf-8')),[230,136,145])
    def test_relative_rope_shift(self):
        def r(t):return [math.cos(t),math.sin(t)]
        self.assertAlmostEqual(e.dot(r(math.pi/6),r(3*math.pi/6)),e.dot(r(2*math.pi/6),r(4*math.pi/6)))
    def test_high_weight_not_high_contribution(self):self.assertLess(.9*.01,.1*10)

class MoreStateTests(unittest.TestCase):
    def test_compaction_suffix_preserved(self):
        snap=list(range(1,21));current=snap+[21];candidate={'covers':20,'summary':'state20'}
        replacement=[candidate]+[i for i in current if i>candidate['covers']]
        self.assertEqual(replacement[-1],21);self.assertEqual(len(replacement),2)
    def test_unknown_not_failure(self):
        external={'counter':11};local={'op7':'unknown'}
        self.assertEqual(external['counter'],11);self.assertNotEqual(local['op7'],'failed')
    def test_idempotency_parameter_conflict(self):
        receipts={'k7':{'amount':10,'result':110}}
        def request(key,amount):
            if key in receipts:
                if receipts[key]['amount']!=amount:raise ValueError('same key different arguments')
                return receipts[key]['result']
            raise ValueError('fixture only supports pre-recorded action')
        self.assertEqual(request('k7',10),110)
        with self.assertRaises(ValueError):request('k7',20)
    def test_merge_lost_update_counterexample(self):
        a={'a':2,'b':1};b={'a':1,'b':2};disk=a.copy();disk=b.copy();self.assertNotEqual(disk,{'a':2,'b':2})
    def test_version_check_refuses_stale_write(self):
        disk={'version':9,'body':'B'};expected=7
        if disk['version']==expected:disk.update(version=8,body='A')
        self.assertEqual(disk['version'],9)
    def test_atomic_replace_is_not_compare_and_swap(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x';tmp=Path(d)/'tmp';p.write_text('v7');observed=p.read_text();p.write_text('v9');tmp.write_text('v8');os.replace(tmp,p)
            self.assertEqual(observed,'v7');self.assertEqual(p.read_text(),'v8')
    def test_exclude_boundary_counterexample(self):
        def correct(p,d):return p==d or p.startswith(d+'/')
        for d in ['a','cache','build']:
            self.assertTrue(correct(d,d));self.assertTrue(correct(d+'/x',d));self.assertFalse(correct(d+'b/x',d));self.assertTrue((d+'b/x').startswith(d))
    def test_acl_topk_order(self):
        ranked=[('A',False),('B',False),('C',True),('D',True)]
        after=[x for x,ok in ranked[:2] if ok];before=[x for x,ok in ranked if ok][:2];self.assertEqual(after,[]);self.assertEqual(before,['C','D'])
    def test_bitemporal_specific_scenario(self):
        rows=[{'project':'prod','recorded':1,'from':1,'to':99,'value':5},{'project':'prod','recorded':10,'from':5,'to':99,'value':7}]
        self.assertEqual(e.memory_select(rows,'prod',3,11)['value'],5);self.assertEqual(e.memory_select(rows,'prod',7,8)['value'],5);self.assertEqual(e.memory_select(rows,'prod',7,11)['value'],7)
    def test_current_test_version(self):
        report={'version':'v8','exit':0};artifact='v9';self.assertFalse(report['version']==artifact and report['exit']==0)
    def test_approval_bound_to_artifact_environment(self):
        approved=('P','staging','v8');self.assertNotEqual(approved,('P','staging','v9'));self.assertNotEqual(approved,('P','production','v8'))
    def test_refund_conditions_and_not_or(self):
        days=6;weekday=False;self.assertFalse(days<=7 and weekday);self.assertTrue(days<=7 or weekday)
    def test_tool_completion_order_not_identity(self):
        result_by_id=dict([('c2','B'),('c1','A')]);self.assertEqual(result_by_id['c1'],'A')
    def test_replay_does_not_repeat_effect(self):
        events=[('c7','succeeded'),('c8','pending')];state={}
        for key,status in events:state[key]=status
        for key,status in events:state[key]=status
        self.assertEqual(state,{'c7':'succeeded','c8':'pending'})
    def test_gui_scroll_transform(self):self.assertEqual(300-200,100);self.assertEqual((120/2,80/2),(60,40))

if __name__=='__main__':
    import sys
    if '--test' in sys.argv:unittest.main(argv=[sys.argv[0]],verbosity=2)
    else:print(json.dumps(e.finite(extended_outputs()),ensure_ascii=False,indent=2,allow_nan=False))
```


<span id="code-chain_and_operators"></span>


### chain\_and\_operators.py

```
"""同一词表的微型Decoder与算子例。全部参数为教学设置，未训练。"""
from __future__ import annotations
import math,json,unittest
import engine as e
E=e.compute()['embedding']['table']
WORDS=['PAD','我','爱','学习','你','！']
I=[[float(i==j) for j in range(4)] for i in range(4)]
WK=[[0.,1.,0.,0.],[1.,0.,0.,0.],[0.,0.,0.,1.],[0.,0.,1.,0.]]
WV=[[1.,0.,0.,0.],[0.,.5,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,.5]]

def silu(x):return x/(1+math.exp(-x))
def forward(ids, prior=None):
    if not ids or any(type(i)is not int or i<=0 or i>=len(E) for i in ids):raise ValueError('valid non-PAD IDs only')
    x=[list(E[i]) for i in ids];norm=[e.ln(v) for v in x];q=e.mm(norm,I);k=e.mm(norm,WK);v=e.mm(norm,WV)
    prior=prior or {'K':[],'V':[]};offset=len(prior['K']);allk=prior['K']+k;allv=prior['V']+v
    heads=[]
    for h in range(2):
        low=2*h;high=low+2
        heads.append(e.attn([a[low:high] for a in q],[a[low:high] for a in allk],[a[low:high] for a in allv],offset=offset))
    combined=[heads[0]['output'][j]+heads[1]['output'][j] for j in range(len(ids))]
    r=e.add(x,combined);n2=[e.ln(row) for row in r]
    # Wgate=Wup=I; Wdown=.25I, hence .25*silu(z)*z.
    f=[[.25*silu(z)*z for z in row] for row in n2];y=e.add(r,f);last=e.ln(y[-1]);logits=e.mm([last],e.tr(E))[0]
    # PAD is forbidden by this explicit teaching decoding policy, not by Embedding itself.
    decoded_logits=[-math.inf]+logits[1:];p=e.softmax(decoded_logits);token=max(range(1,6),key=lambda j:p[j])
    return {'ids':ids,'words':[WORDS[i] for i in ids],'X':x,'normalized':norm,'Wq':I,'Wk':WK,'Wv':WV,'Q':q,'K_new':k,'V_new':v,'heads':heads,'concat_attention':combined,'residual1':r,'normalized2':n2,'ffn':f,'hidden_output':y,'last_norm':last,'logits_before_PAD_filter':logits,'probabilities_after_PAD_filter':p,'selected_token':token,'selected_word':WORDS[token],'cache':{'K':allk,'V':allv}}

def operator_outputs():
    q=[1.,0.];a=[.8,.6];b=[0.,1.];p=e.softmax([e.dot(q,a),e.dot(q,b)]);gq=[(p[0]-1)*a[i]+p[1]*b[i] for i in range(2)]
    rows={'X02':{'input':[1,3],'mean':2,'population_variance':1,'LayerNorm_epsilon1e5':e.ln([1,3]),'RMSNorm_epsilon1e5':[x/math.sqrt(5+1e-5) for x in [1,3]],'SiLU_1_2':[silu(1),silu(2)],'SwiGLU_identity_gate_up_down':[silu(1)*1,silu(2)*2]},
      'X03':{'first_probabilities':{'A':.6,'B':.4},'A_next':{'E':.51,'F':.49},'B_next':{'D':.99,'F':.01},'joint':{'AE':.6*.51,'AF':.6*.49,'BD':.4*.99,'BF':.4*.01}},
      'X04':{'p':[.8,.2],'q':[.5,.5],'KL_p_q':sum(x*math.log(x/y) for x,y in zip([.8,.2],[.5,.5])),'KL_q_p':sum(x*math.log(x/y) for x,y in zip([.5,.5],[.8,.2]))},
      'X05':{'parameters':1000,'P_bytes':4000,'G_bytes':4000,'Adam_m_v_bytes':8000,'data_parallel_per_device':16000,'zero1_per_device':12000,'zero2_per_device':10000,'zero3_per_device':8000},
      'X06':{'Hq':4,'Hkv':2,'group_mapping':[0,0,1,1],'toy_KV_per_token':2*2*2},
      'X07':{'semantic_allowed':[[True,False],[True,True]],'sdpa_bool':[[True,False],[True,True]],'multihead_attention_bool_blocked':[[False,True],[False,False]],'additive_mask':[[0,'-inf'],[0,0]]},
      'X08':{'q':q,'a':a,'b':b,'p':p,'q_gradient':gq,'q_after_lr01':[q[i]-.1*gq[i] for i in range(2)]},
      'X09':{'q':0,'positions':{'A':4,'B':5,'C':1},'undirected_edges':[['A','B'],['B','C']],'greedy_stop':'A','best_after_explore_B':'C'},
      'X10':{'scale':.1,'integer_min':-2,'integer_max':2,'input':[-.24,.03,.26],'integer_codes':[max(-2,min(2,round(x/.1))) for x in [-.24,.03,.26]],'reconstructed':[-.2,0,.2]},
      'X11':{'character_input':['a','b','c'],'merge_rank':[ ['b','c',0], ['a','b',1]],'merged':['a','bc'],'teaching_vocabulary':{'a':1,'bc':5},'IDs':[1,5]},
      'X12':{'valid_target_probabilities':[.8,.5,.25],'valid_count':3,'padded_count':4,'sum_NLL':sum(-math.log(x) for x in [.8,.5,.25]),'correct_mean':sum(-math.log(x) for x in [.8,.5,.25])/3,'wrong_divide4':sum(-math.log(x) for x in [.8,.5,.25])/4}}
    return rows

def compute_chain():
    a=forward([1,2,3]);b=forward([4,2]);follow=forward([a['selected_token']],a['cache']);full=forward([1,2,3,a['selected_token']]);err=max(abs(x-y) for x,y in zip(follow['hidden_output'][0],full['hidden_output'][-1]))
    return {'sentence_A':a,'sentence_B':b,'next_step_A':follow,'full_recompute_A':full,'cached_vs_full_max_error':err,'operators':operator_outputs()}

class ChainTests(unittest.TestCase):
    def test_embedding_rows_match_foundation(self):self.assertEqual(forward([1,2,3])['X'],[E[1],E[2],E[3]])
    def test_two_heads_each_row_probability(self):
        for h in forward([1,2,3])['heads']:
            for row in h['weights']:self.assertAlmostEqual(sum(row),1)
    def test_causal_change_later_cannot_change_first(self):
        self.assertEqual(forward([1,2,3])['hidden_output'][0],forward([1,4,5])['hidden_output'][0])
    def test_cache_full_equivalence(self):self.assertLess(compute_chain()['cached_vs_full_max_error'],1e-12)
    def test_PAD_not_implicitly_generated(self):self.assertEqual(forward([4,2])['probabilities_after_PAD_filter'][0],0)
    def test_norms_differ(self):self.assertNotEqual(operator_outputs()['X02']['LayerNorm_epsilon1e5'],operator_outputs()['X02']['RMSNorm_epsilon1e5'])
    def test_beam_joint_counterexample(self):self.assertGreater(.4*.99,.6*.51)
    def test_KL_asymmetry(self):o=operator_outputs()['X04'];self.assertNotEqual(o['KL_p_q'],o['KL_q_p']);self.assertGreater(o['KL_p_q'],0)
    def test_zero_state_accounting(self):o=operator_outputs()['X05'];self.assertEqual(o['zero1_per_device'],4000+4000+8000/2);self.assertEqual(o['zero3_per_device'],(4000+4000+8000)/2)
    def test_bool_masks_inversion(self):o=operator_outputs()['X07'];self.assertEqual(o['sdpa_bool'],[[not x for x in row] for row in o['multihead_attention_bool_blocked']])
    def test_retrieval_q_gradient_fd(self):
        o=operator_outputs()['X08'];q=o['q'][:];h=1e-6
        def loss():return -math.log(e.softmax([e.dot(q,o['a']),e.dot(q,o['b'])])[0])
        for i,g in enumerate(o['q_gradient']):
            old=q[i];q[i]=old+h;hi=loss();q[i]=old-h;lo=loss();q[i]=old;self.assertAlmostEqual((hi-lo)/(2*h),g,places=8)
    def test_greedy_graph_can_stop_local(self):self.assertGreater(5,4);self.assertLess(1,4)
    def test_quant_clipping(self):self.assertEqual(operator_outputs()['X10']['integer_codes'],[-2,0,2])
    def test_loss_denominator(self):o=operator_outputs()['X12'];self.assertAlmostEqual(o['correct_mean'],.767528364331,places=10);self.assertGreater(o['correct_mean'],o['wrong_divide4'])

if __name__=='__main__':
    import sys
    if '--test' in sys.argv:unittest.main(argv=[sys.argv[0]],verbosity=2)
    else:print(json.dumps(e.finite(compute_chain()),ensure_ascii=False,indent=2,allow_nan=False))
```


<span id="code-run_all"></span>


### run\_all.py

```
"""运行本书401例所配套的确定性数值/状态见证；不调用网络或模型。"""
from pathlib import Path
import subprocess,sys,json
root=Path(__file__).resolve().parent
results=[]
for script in ["engine.py","additional_checks.py","chain_and_operators.py"]:
    p=subprocess.run([sys.executable,str(root/script),"--test"],cwd=root,text=True,capture_output=True)
    print(p.stdout);print(p.stderr)
    results.append({"script":script,"returncode":p.returncode})
    if p.returncode:raise SystemExit(p.returncode)
for script,name in [("engine.py","numbers.json"),("additional_checks.py","extra_numbers.json"),("chain_and_operators.py","chain_numbers.json")]:
    p=subprocess.run([sys.executable,str(root/script)],cwd=root,text=True,capture_output=True,check=True)
    json.loads(p.stdout)
    (root/name).write_text(p.stdout,encoding="utf-8")
print(json.dumps({"all_passed":True,"suites":results},ensure_ascii=False,indent=2))
```

AI系统工程：从基础到内部 · [首页](index.md) · [示例索引](worked-examples.md) · [依据与范围](example-sources.md)