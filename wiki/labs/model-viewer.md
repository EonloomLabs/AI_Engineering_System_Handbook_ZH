---
title: "模型实验：逐步查看训练与推理的中间值"
description: "AI系统工程：本地教学正文与可追溯图表"
---

# 模型实验：逐步查看训练与推理的中间值


<span id="mc-section-1"></span>


## 一条记录贯穿四种状态

下面的所有帧直接读取随包实跑记录。前向和反向都使用更新前θ₀；参数更新帧记录真实AdamW；生成帧使用保存后重新加载的θ\*。切换分组会明确改变阶段，不将不同权重的数字混在同一次前向。

查看阶段 
<span id="mc-section-2"></span>


### 

默认暂停，最后一步自动停止。图上显示舍入值，记录保留完整精度。图形窄屏可在自身区域滚动；所有数值另有完整可访问表格。


<span id="mc-section-3"></span>


## 完整解释入口

[前向总账](../chapters/02.md#core-forward-trace-1) · [完整反向](../chapters/04.md#core-backward-1) · [参数更新](../foundations/16.md#core-optimizer-1) · [训练后全量生成](../foundations/18.md#core-generation-1) · [缓存对照](../foundations/19.md#core-cache-1)

未启用JavaScript；请打开以下静态记录页，每一张表和步骤仍可阅读。

[完整静态数表](model-values.md) · [程序与原始记录](model-run.md)