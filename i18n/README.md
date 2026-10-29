# 教材多语言版本

中文正本位于根目录，英文分页版位于 en/，英文连续版为 en/complete.html。
日语沿用同一张去重表的 ja 字段。接手前读 [HANDOFF.md](HANDOFF.md)、
[TRANSLATING.md](TRANSLATING.md) 和 [SOURCE-ISSUES.md](SOURCE-ISSUES.md)。

本任务不启动服务或长时间进程，不改中文页面、原始运行脚本、图形生成器或实验数据。
只使用 Codex 翻译，不调用本地翻译服务。

## 正文与派生产物

table.json 是正文译文的唯一来源，按中文原串去重，每条有永久 id。
写表必须保留整个顶层对象，包括 next_id、其他语言及未知元数据。
译者只交付自己的批次文件，只能运行带 --check 的 ingest。

~~~text
extract.py → content/ → units.py → units/ → table.py build → table.json
batch.py export / ingest → apply.py → en/ 分页版
gen_assets.py → 英文目录和搜索索引
data_strings.py → 英文图解散文、模型说明与标签
runtime_strings.py → 英文运行脚本文案
figure_strings.py → SVG 排版与下载镜像
build_complete.py → 英文连续版
~~~

每批英文译文入表后，依次运行：

~~~bash
python3 i18n/batch.py ingest pNN.en.txt --lang=en
python3 i18n/spelling.py --fix
python3 i18n/terms.py --fix
python3 i18n/vocab.py --fix
python3 i18n/consistency.py --fix
python3 i18n/embedded.py --fix
python3 i18n/apply.py --verify
~~~

页面及派生产物的最终生成顺序如下。apply.py 和 data_strings.py 会重新复制原 SVG，
因此必须先于 figure_strings.py；连续版最后内联最终资产。
首次生成或新增局部脚本时，先运行一次 runtime_strings.py write --lang=en，
让 apply.py 能把脚本引用指向已存在的英文资产，再执行下列完整流程。

~~~bash
python3 i18n/apply.py --lang=en
python3 i18n/gen_assets.py --lang=en
python3 i18n/data_strings.py write --lang=en
python3 i18n/runtime_strings.py write --lang=en
python3 i18n/figure_strings.py write --lang=en
python3 i18n/build_complete.py --lang=en
python3 i18n/links.py --lang=en
~~~

figure_strings.py 使用当前发布的 SVG 节点，量宽、折行并调整纵向空间；不重跑训练，
不手填数值。代码标识符、数值、横向比例及帧高亮保持。普通概念词可按英文语法变化，
例如正文中的 API → APIs，代码里的 API() 仍须原样保留。

模型数据的 sourceGroup 是从原始 group 复制的内部键，用于匹配未翻译的
data-allowed-groups。播放器选项仍显示翻译后的 group。
算例词元 我 / 爱 / 学习 / 你 / ！始终保留，以匹配参数行索引。
代码数据、等宽对齐的算例文本及原文件名也保留；安全代码注释单独抽取翻译。

## 连续版验证

连续版从当前分页正文组装，沿用原连续版的 250 节收录顺序，并保留资源节和两个工程附节。
页内 ID、锚点和 ID 引用统一重写，搜索与图形数据取自 en/assets/。
资源以 data URI 内联，正文与分页版共用译文。

中文诊断只写临时文件，不改根目录 complete.html：

~~~bash
python3 i18n/build_complete.py --diagnose-zh --output /tmp/zh-complete-rebuilt.html --report /tmp/zh-complete-proof.json
python3 i18n/build_complete.py --lang=en --check
~~~

旧中文连续版有已记录的同步差异，不能要求与当前分页版逐字相同。
构建器逐节验证正文、代码、SVG 几何与折叠状态，并检查唯一 ID、锚点、搜索落点和资源。
静态验证之外的调试与最终验收由用户进行。

## 界面语言与完整版本

source.json 与 locales/*.json 仍只管理 125 条共享界面词条，支持简体中文、English、
日本語、Español、Tiếng Việt。界面切换不能代表正文已翻译。
build.py 打包 assets/i18n-data.js，I18N_META.editions 只有全部分页齐备后才加入该语种。
当前英文局部资产另行适配英文全文搜索提示；其他界面语种保持各自原有说明。
英文局部 i18n.js 从本页 i18n-scope 读取正文版次提示，避免在切换未完成语种时误称正文为中文。

~~~bash
python3 i18n/build.py --check
~~~

i18n/inline_complete.py 用于根目录中文连续版的界面维护，本次翻译任务不运行它。
英文连续版使用 build_complete.py，避免覆盖中文正本。

## 日语续接

共享层 12 批、6,628 条已完成；独有层 u01–u22、u24–u25、u54 又入表 10,726 条。
日语累计 17,856 / 31,629 条，实例覆盖 93.2%，字数覆盖 56.2%，还缺 13,773 条。
证据见 [validation.ja-shared.json](validation.ja-shared.json) 和
[validation.ja-unique.json](validation.ja-unique.json)。67 页正文单位已齐译，
运行脚本与图形适配尚未完成，暂不生成或发布混合版本。

使用 i18n/work/_reference.ja.txt、glossary.ja.json 与协议中的日语约定。
通过 batch.py export ... --lang=ja 和 ingest ... --lang=ja 复用永久 ID；
源文件保留真实首尾空白，␣ 仅用于译文端的空白控制。

英文拼写、术语和词元修复器含有英文规则，不可直接对日语运行 --fix。
日语同形汉字或纯汉字标签被误判时，由主流程核对具体原串和译文，再记入 ja-approved.json。
许可只匹配这一对文本，不跳过标签、文件名和空译文检查，也不用于生成译文。
假名检测只认实际字母，单独的「・」「ー」或浊点不再算作假名证据。
相关正反例与独立审查见 [validation.ja-kana.json](validation.ja-kana.json)。
每批仍由主流程串行 ingest，运行 embedded.py --lang=ja --fix、apply.py --verify，
并核对数字、标识符、转义和算例词元。日语页面未发布时，英文链接检查只验证既有英文产物。
运行脚本、SVG 和连续版适配器目前只发布英文，日语全量阶段须逐项扩展并验证，
不能仅替换 --lang 就宣称日语版完成。未齐备的页面不会生成，也不加入语言导航。
