# 教材多语言版本

中文正本位于根目录，英文、日语、西班牙语和越南语版分别位于 `en/`、`ja/`、`es/`、`vi/`。
各版已生成 262 页分页正文及同内容的 `complete.html` 连续版；四语实际代码保真检查通过。
接手前读 [HANDOFF.md](HANDOFF.md)、[TRANSLATING.md](TRANSLATING.md) 和
[SOURCE-ISSUES.md](SOURCE-ISSUES.md)。

本任务不启动服务、浏览器或长时间进程，不改中文原文、原始运行脚本、图形生成器或实验数据。
只使用 Codex 翻译，不调用本地翻译服务。布局、章节定位、滚动与动画交互由用户最终验收。

## 当前状态

`table.json` 共 31,633 条，英文、日语、西班牙语和越南语均已齐译，`next_id=31687`。
日语原共享层 7,130 条与独有层 u01–u54 的 24,499 条均已完成；另将 4 条目录分类来源
正式注册并通过 `catalog-01.ja` 批次入表。7 种分类的英日译文统一从表读取，
`catalog-kinds.json` 旧英文值仅保留为迁移历史。

日语已生成 263 份 HTML、777 幅 SVG、49 个下载镜像和 10 份局部运行资产。
14 份资产 JS 与连续版 14 段内联 JS 语法通过；88,058 处本地引用失败 0、待译目标 0。
逐页比对原脚本清单，262 页共 2,606 个脚本引用全部落在 `ja/assets`，共享根目录脚本引用为 0。
262 页往返不一致 0，嵌入标题分歧 0；分页版与连续版共 361 个自检答案全部默认收起。
连续版含 250 个正文节、253 个独立节、13,563 个唯一 ID、175 份内联资源及 5,602 条搜索索引，
失效锚点、ID 引用、外部运行依赖与搜索落点均为 0。

完整记录见 [validation.ja.json](validation.ja.json)，分项见
[静态检查](validation.ja-static.json)、[图形](validation.ja-figures.json)、
[模型数据](validation.ja-data.json)、[连续版](validation.ja-complete.json)、
[批次](validation.ja-batches.json) 和 [工具测试与独立审查](validation.ja-tooling.json)。
32 项测试通过，含首次生成资产路径的 5 项新增测试；12 个代码与测试文件的独立审查
无阻塞项。三位译者只读交叉 QA 共 88 条，
问题已由主流程修复，见 [交叉核对记录](work/_ja-cross-review.json)。这些证据不等于全文逐句人工审校。

日语登记阶段的保留检查记录：1,371 份受保护源文件中 1,370 份字节相同，唯一派生例外为
`assets/i18n-data.js` 的版次列表加入 `ja`，所有语种界面字典内容均未变。
该阶段英文仅局部 `i18n-data.js` 与 `complete.html` 各增加 5 字节版次元数据；
移除该项后均回到原哈希。见 [保留检查](validation.ja-preservation.json) 和
[版次登记审计](work/_ja-edition-publication.json)。原文问题共 32 项，仍待用户裁决。

### 西班牙语与越南语发布结果

本轮翻译、生成与全部静态验证已完成。最终记录见
[西班牙语总汇](validation.es.json)、[越南语总汇](validation.vi.json) 和
[多语言总汇](validation.multilingual.json)；浏览器与交互验收仍由用户执行。

西班牙语 `es` 与越南语 `vi` 各 31,633 条译文均已齐译，v01–v65 各 65 批已串行入表。
批次校验和数值检查通过，130 份源契约保持不变，`next_id=31687` 保留。
批次与译文哈希见 [续接进度](work/_es-vi-progress.json)，实际覆盖以 `table.json` 为准。

两版各有 326 个发布文件，含 263 份 HTML 与 49 个下载镜像；图形适配覆盖 777 幅 SVG，
207 份图形准备输出与发布文件相符。各有 256 条目录项、5,614 条搜索索引，覆盖全部 262 页。
版次元数据现为 `zh-CN / en / ja / es / vi`，四个非中文版本的运行包与连续版已同步。
见 [版次登记审计](work/_es-vi-edition-publication.json)。日语原有 5,602 条搜索索引保持。

四语最终静态复测均已通过：各 263 份 HTML 的 88,058 处本地引用失败为 0；
14 份资产 JS 与连续版 14 段内联 JS 语法错误为 0；分页与连续版共 361 个自检答案默认收起。
ES/VI 连续版各有 250 个正文节、253 个独立节、13,563 个唯一 ID，
失效锚点、ID 引用和外部运行依赖均为 0。分项记录见
[ES 静态检查](validation.es-static.json)、[VI 静态检查](validation.vi-static.json)、
[ES 连续版](validation.es-complete.json)、[VI 连续版](validation.vi-complete.json)、
[ES 图形](validation.es-figures.json) 和 [VI 图形](validation.vi-figures.json)。
代码接缝修复后的实际代码与最终静态产物均已复核通过。

工具测试共 77 项（原 71 项加代码接缝回归 6 项），实现侧与独立复核均通过，无阻塞项；
见 [ES/VI 工具验证](validation.es-vi-tooling.json)。
ES 的 14 处图形溢出已修复，对应检查为 0；静态量宽不等于浏览器视觉验收。

[实际发布代码检查](work/_es-vi-code-proof.json) 已对英日西越四版全量通过：各 262 页中，
2,015 处行内代码逐字相同，1,533 个可解析 Python 块的 AST 与非注释词元保持，
492 个 pre 块符合当前注释译文，39 种安全注释的 41 处实例齐备。
英西越代码页各 474 处行号义项正确；日语代码路径保持。

检查曾发现每版 6 处行内代码尾部多出空格，原因是 `apply.space_seams` 的标点接缝规则
把新间隔插入了 `</code>` 内侧。永久修法按行内代码内容范围定位，将跨闭标签匹配产生的
句间空格放到闭标签外，不改代码内容、实体或原有空白。重生成后四语均为 2,015/2,015 逐字保持。
越南语代码行号使用按页覆盖 `Dòng N`，共享表中的矩阵行仍用 `Hàng N`。
[行内语法复核](work/_es-vi-inline-grammar-review.json) 保留短串组合修正的来源与建议。

本轮对历史基线中的 1,371 份受保护源文件复核，1,370 份字节相同；唯一派生例外是
`assets/i18n-data.js` 的 `metadata.editions`。125 个界面键、5 份语言字典、132 处运行来源和
104 条运行来源字符串保持。中文正文、原代码、图形、权重与训练记录未改。
见 [保留检查](validation.es-vi-preservation.json)。原文 32 项问题仍待用户裁决。

旧英文条目 1914、1915 的 teacher-forcing 数据、6121、25885 的检索字面量及 819 的 copula
义项已受控修复，具体边界见 [英文修复记录](work/_legacy-en-repair-plan.json)。
不沿用早期「英日全部未改动」结论作为本轮证明；受控修复及代码接缝修复均保留独立证据。

译者遵循 [ES/VI 协议](TRANSLATING.md#spanish-and-vietnamese-editions) 和语言词表；
主流程串行入表、运行对应语言的 embedded 对齐与往返校验。
英文 spelling / terms / vocab / consistency 修复器不得对新语种运行 `--fix`。
本轮未启动服务、浏览器或长进程；布局、章节定位、滚动、动画及全文母语审校仍留给用户验收。

## 正文与派生产物

`table.json` 是译文的唯一来源，按中文原串去重，每条有永久 ID。
写表必须保留整个顶层对象，包括 `next_id`、其他语言及未知元数据。
译者只交付自己的批次文件，只能运行带 `--check` 的 ingest；维护者串行入表与生成。

~~~text
extract.py → content/ → units.py → units/ → table.py build → table.json
batch.py export / ingest → apply.py → <lang>/ 分页版
catalog-kinds.json → table.py build → table.json → gen_assets.py 目录分类
页面与表 → gen_assets.py → 目录和搜索索引
data_strings.py → 图解散文、模型说明与标签
runtime_strings.py → 运行脚本文案
figure_strings.py → SVG 排版与下载镜像
build_complete.py → 连续版
~~~

runtime / figure / complete 适配器均显式支持 `en`、`ja`、`es` 与 `vi`。
三个适配器的 `collect` 只写各自 registry；`table.py build` 负责合并计数与永久编号。
来源有变化时，先核对变化，再 collect、重建表并补译；不得绕过来源指纹或缺译检查。
目录分类在 `table.py:57` 的 `auxiliary_counts` 注册，由 `gen_assets.py:48` 的 `main` 消费。

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

日语沿用 [协议中的日语约定](TRANSLATING.md#japanese-edition)、
`work/_reference.ja.txt` 与 `glossary.ja.json`。批次使用 `--lang=ja`，
维护者入表后运行 `embedded.py --lang=ja --fix` 与 `apply.py --verify`，核对数字、
标识符、转义和算例词元。英文 spelling / terms / vocab / consistency 修复器含英文模板，
不可对日语运行 `--fix`。

纯汉字标签经主流程核对具体原串和译文后，才能记入 `ja-approved.json`。
许可仅匹配具体 source / target，不跳过标签、文件名或空译文检查。
假名检测只认实际字母；单独的「・」「ー」或浊点不算假名证据。
见 [假名检测验证](validation.ja-kana.json)。页面短串义项继续由 `overrides.json` 管理。
新源文件保留真实首尾空白，`␣` 仅用于译文端的空白控制；不得覆盖已交译 `.src.txt`。

## 最终生成顺序

以下以日语为例；其他语种替换对应的 `--lang`。ES/VI 全部必需译文齐备后再执行最终生成。
首次生成与普通译文更新均按此顺序执行。`apply.py:127` 的 `relink` 对 `en` / `ja` / `es` / `vi`
声明的 14 份局部 JS 保留语言版路径，即使文件尚未生成也不依赖预生成步骤。
未声明且无语言镜像的资源（包括共享 CSS）仍指向共享根目录：

~~~bash
python3 i18n/apply.py --lang=ja
python3 i18n/gen_assets.py --lang=ja
python3 i18n/data_strings.py write --lang=ja
python3 i18n/runtime_strings.py write --lang=ja
python3 i18n/figure_strings.py write --lang=ja
python3 i18n/build_complete.py --lang=ja
python3 i18n/links.py --lang=ja
~~~

`apply.py` 和 `data_strings.py` 会重新复制原 SVG，必须先于 `figure_strings.py`。
图形适配后重跑前两者，须重跑图形和连续版。图形适配使用当前发布 SVG，量宽、折行并
调整纵向空间；日语使用禁则换行。原代码标识符、数值、横向比例与帧高亮保持，不重跑训练，
不手填数值。静态排版校验不证明浏览器内的视觉效果。

模型数据的 `sourceGroup` 从原始 `group` 复制，用于匹配未翻译的 `data-allowed-groups`；
可见选项显示译后的 `group`。算例词元 `我 / 爱 / 学习 / 你 / ！` 保留，以匹配参数行索引。
代码数据、等宽对齐算例、倒排索引实际匹配词和原文件名也保留；安全代码注释单独抽取翻译。
具体例外与证据见 [HANDOFF.md](HANDOFF.md#8-各语言版再生成)。

## 连续版验证

连续版从当前语言分页正文组装，沿用原连续版的 250 节收录顺序，保留资源节和两个工程附节。
页内 ID、锚点和 ID 引用统一重写，搜索与图形数据取自最终 `<lang>/assets/`；
资源以 data URI 内联。正式只读检查命令为：

~~~bash
python3 i18n/complete_strings.py check --lang=ja
python3 i18n/build_complete.py --lang=ja --check
python3 i18n/complete_strings.py check --lang=en
python3 i18n/build_complete.py --lang=en --check
~~~

旧中文连续版有已记录的同步差异，不能要求与当前分页版逐字相同。
中文诊断只允许临时输出，不改根目录 `complete.html`；`/tmp` 不作为永久交接脚本或证据来源。
构建器逐节验证正文、代码、SVG 几何与折叠状态，并检查唯一 ID、锚点、搜索落点和资源。
本轮未启动浏览器或服务，宽屏布局、章节定位、滚动和动画交互留给用户验收。

## 界面语言与完整版本

`source.json` 与 `locales/*.json` 管理 125 条共享界面词条，支持简体中文、English、
日本語、Español、Tiếng Việt。界面切换与完整正文版本分别管理。
`build.py:20` 的 `editions` 根据全部分页是否存在决定版次列表；当前为 `zh-CN / en / ja / es / vi`。
维护者还须核对数据、运行脚本、图形、下载及连续版齐备后，才登记新完整语种。
局部 `i18n.js` 读取本页 `i18n-scope`，提示须符合当前正文版次；语言版搜索提示使用自身索引示例。

普通译文更新不需重登记版次。新增完整语种并完成静态校验后，运行：

~~~bash
# 列出本次登记后全部已完成验收的非中文完整版本。
# ES/VI 均已齐备时如下；只新增其中一种时移除尚未齐备的语种。
(
set -e
published_languages=(en ja es vi)
python3 i18n/build.py
python3 i18n/runtime_strings.py collect
for lang in "${published_languages[@]}"; do
  python3 i18n/runtime_strings.py write --lang="$lang"
  python3 i18n/build_complete.py --lang="$lang"
done
python3 i18n/build.py --check
for lang in "${published_languages[@]}"; do
  python3 i18n/links.py --lang="$lang"
done
)
~~~

`build.py` 更新共享派生包的版次元数据后，runtime collect 刷新输入指纹，不写表。
本轮 132 处来源、104 条字符串及全部 items 不变，无需重建表。
再写出本次登记后所有已发布语种的运行包和连续版，使语言导航同步；本轮已同步英日西越四版。
任一命令失败时停止后续步骤并处理失败，不把部分成功视为登记完成。
此阶段不重跑 apply / data，以免覆盖 SVG。
`inline_complete.py` 用于根目录中文连续版的界面维护，本次翻译任务不运行它。
