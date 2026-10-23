# 图解与数据表达
本目录记录图解审查与重绘，不是另一个学习专题。阅读请从原课程继续。

- `audit.json`：原静态表达的处理清单。
- `animation-audit.json`：逐步图解的保留、重绘、转换记录。
- `walkthrough-audit.json`：贯通案例的表达调整。
- `renderer.py`：精确数表、关系图、时序与状态图的绘图代码。
- `rendered/`：课程实际使用的SVG；原生数据表不生成图片。
- `source/`：用于复算的原始记录副本，未改变模型参数或实验结果。
- `DESIGN.md`：图形是否有必要、如何选择表达形式的规则。
- Mermaid结构源位于 `wiki/diagrams/`。数值与排名表由原始数据生成，不强制转换为流程图。

中文图形使用本机字体，不随教材分发字体。重绘可安装 Pillow 与 lxml，
并设置环境变量 WIKI_CJK_FONT 指向本机可用的中文字体。没有字体路径时使用保守宽度估计；
文字排版仍应在实际浏览器中复核。

实际模型代码：labs/model/lab/tiny_model.py。
`forward` 第53—98行；`manual_backward` 第117—153行；`generate` 第156—175行。
图中的步骤不代表真实GPU耗时，也不表示商业模型内部实现。

`build_exports.py`重新生成本地搜索、Markdown与完整阅读版。先在自用环境安装requirements.txt；读书本身无需安装这些依赖。
