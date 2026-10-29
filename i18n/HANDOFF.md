# 多语言版本：交接说明

本文件记录英文版与日语版的完成状态，以及西班牙语、越南语翻译收尾的做法、工具、已定决策和验收边界。
读完这份文件就能接手，不需要重新推导。

搭配阅读：`i18n/TRANSLATING.md`（发给译者的协议）。

---

## 1. 任务与硬约束

这本中文离线教材的 262 页 HTML 已生成英文 `en/`、日语 `ja/`、西班牙语 `es/` 和越南语 `vi/` 版本，各有同内容的 `complete.html` 连续版。四语译文均齐备，版次已登记，实际代码保真检查通过；状态与证据见第 4 节。后续维护继续复用同一张翻译表与生成管线。

**用户定下的约束，必须遵守：**

- 不要启动任何服务或长时间运行的进程（dev server、npm、python server 都不行）。
  用户自己用 codex 做调试和最终验收，机器不能被占住。
- 不要改动中文原文。翻译中发现的原文问题记录下来交给用户裁决，见第 7 节。
- 不调用本地翻译服务，只使用 Codex 的语言能力适配。
- AGENTS.md 的规则照旧生效，其中对翻译影响最大的三条：
  - 「不要手填看似合理的概率；改变示例须重新运行」
  - 「数值图中的舍入仅用于显示；计算使用原精度」
  - 「正常阅读使用根目录 index.html。complete.html 是同一内容的内联版本」

---

## 2. 核心做法：按字符串去重，不按页

这是整件事的关键，别改回按页翻译。

| | 中文字数 |
|---|---|
| 262 页原始 | 306 万（侧栏目录在每页重复一遍） |
| 按页去重 | 101.8 万 |
| **按字符串去重** | **69.8 万** ← 实际工作量 |

副产品是**同一句中文在全站必然同一个英文**，不靠约定。其中 **486 条字符串占全站 77% 的实例**（侧栏+外壳），所以先翻它们，262 页的导航一次全部英文化。

**译文的唯一存放处是 `i18n/table.json`**，形如：

```json
{"s": {"<中文串>": {"id": 1234, "n": 83, "p": 21, "en": "...", "ja": "..."}},
 "next_id": 31687}
```

`n` 是全站出现次数，`p` 是出现页数，`id` 是永久编号。加语言就是加一个字段，所以日语不需要重做任何基础设施。

---

## 3. 管线

```
中文页面 ──extract.py──> i18n/content/*.json   每个可译片段 + 字节偏移
                │
                └──units.py──> i18n/units/*.json  相邻片段按行内标签合并成翻译单元
                                    │
                                    └──table.py build──> i18n/table.json  按字符串去重
                                                              │
                        batch.py export ──> i18n/work/*.src.txt  发给译者
                        batch.py ingest <──  i18n/work/*.en.txt  译者交回
                                                              │
                                              apply.py ──> en/*.html
```

**按字节偏移反向拼接**，所以单元之外的一切（标签、属性、数值、代码、SVG、锚点、data 键）
逐字节保留。这是整套东西能信任的基础：

```bash
python3 i18n/apply.py --verify     # 必须输出「验证 262 页 | 往返不一致: 0」
```

任何改动抽取或合并逻辑之后都要跑这条。

### 各脚本

| 脚本 | 作用 |
|---|---|
| `extract.py` | 抽取整个文档的可译片段（含 head、侧栏、页眉页脚），记字节偏移 |
| `units.py` | 把仅被行内标签分隔的相邻片段合并成一个翻译单元 |
| `table.py build` | 重建去重表，**保留已有译文和永久 id** |
| `batch.py export shell` | 导出跨页高频字符串（n ≥ 51） |
| `batch.py export tier <lo> <hi> <每批条数>` | 按出现次数分层导出 |
| `batch.py export group <名> <页...>` | 导出若干页独有的字符串（n = 1），一批一文件 |
| `batch.py ingest <文件> [--check]` | 校验并入表；`--check` 只校验不写 |
| `batch.py status [--pages]` | 进度 |
| `apply.py [页...] [--lang=xx]` | 生成 `<lang>/` 页面 |
| `apply.py --verify` | 往返无损校验 |
| `consistency.py [--fix]` | 共用中文模板是否被译成两种说法 |
| `embedded.py [--fix]` | 目录里每个链接的文本，是否与它指向的标题一致 |
| `spelling.py [--fix]` | 统一美式拼写（教材自己的 glossary.html 用 `-ization`） |
| `terms.py [--fix]` | 已定术语，带义项区分 |
| `vocab.py [--fix]` | 算例词表的词元是否仍为中文（见第 6 节） |
| `audit.py [页...]` | 按来源归类统计 `en/` 页面的残留中文 |
| `links.py [--lang=xx]` | 校验生成页面的本地引用是否都能解析 |
| `gen_assets.py --lang=xx` | 从译好的页面重建搜索索引；目录标题与分类译文统一读表 |
| `data_strings.py collect\|write` | `visual-data.js` / `model-data.js` 的散文进出表 |
| `runtime_strings.py collect\|export\|write --lang=xx` | 注册、导出或生成语言版运行文案；collect 不写表 |
| `figure_strings.py collect\|export\|write --lang=xx` | 注册、导出或生成语言版 SVG 与下载镜像；collect 不写表 |
| `complete_strings.py collect\|export\|check --lang=xx` | 连续版外壳来源与译文检查；collect 不写表 |
| `build_complete.py --lang=xx [--check]` | 从当前分页正文组装或只读比对连续版 |

上述运行文案、图形与连续版工具的 `xx` 当前支持 `en`、`ja`、`es` 或 `vi`。

### 每批英文译文回来的固定流程

```bash
cd /Users/chuhemiao/toyama/AI_Engineering_System_Handbook_ZH
python3 i18n/batch.py ingest pNN.en.txt          # 1 入表
python3 i18n/spelling.py --fix                   # 2 统一拼写
python3 i18n/terms.py --fix                      # 3 已定术语
python3 i18n/vocab.py --fix                      # 4 词元保留中文
python3 i18n/consistency.py --fix                # 5 统一模板
python3 i18n/embedded.py --fix                   # 6 对齐目录与标题
python3 i18n/apply.py --verify && python3 i18n/apply.py
```

上述英文检查发布前必须全部归零。另外两个检查：

```bash
python3 i18n/links.py      # 应解析但失败必须为 0（指向未译页面的不算）
python3 i18n/audit.py      # 残留中文按来源归类，核对是否都属已知豁免
```

`links.py` 存在的理由：`en/` 只镜像 HTML 树，所以指向树外的引用在构建时要多加一层
`../`，而指向已译页面的保持原路径。这个重写是整个构建里唯一会**静默**产出坏页面的
环节 —— `../` 数量错了只是样式表 404，不会报错。

---

## 4. 当前状态（2026-10-30）

英文版与日语版均已生成，静态检查通过。英文原收尾证据见
[validation.en.json](validation.en.json)；日语总汇见
[validation.ja.json](validation.ja.json)，分项证据如下。

- `table.json` 共 31,633 条，英文与日语各 31,633 条齐译，`next_id=31687`。
  日语原共享层 7,130 条，独有层 u01–u54 共 24,499 条，原 31,629 条已全部完成。
  原 54 份源契约保留；逐批校验见 [validation.ja-batches.json](validation.ja-batches.json)。
- 本轮发现目录分类还有 4 条未注册来源。`table.py` 从 `catalog-kinds.json` 注册后分配
  ID 31683–31686，单独通过 `work/catalog-01.ja.src.txt` 与对应译文受控入表。
  现有 7 种目录分类的英日译文均从表读取；`catalog-kinds.json` 旧英文值仅保留为迁移历史。
  见 [work/_ja-catalog-enrollment.json](work/_ja-catalog-enrollment.json)。
- 两版各有 262 页分页正文及 1 份连续版，共 263 份 HTML。日语目录 256 条目，
  搜索 5,602 条，覆盖全部 262 页；10 份局部运行资产、14 份资产 JS 及连续版
  14 段内联 JS 均已通过语法检查。逐页比对原脚本清单，262 页共 2,606 个脚本引用
  全部落在 `ja/assets`，共享根目录脚本引用为 0。
  见 [validation.ja-static.json](validation.ja-static.json)。
- 日语 SVG 777 幅、下载镜像 49 个；全量图形准备结果的 207 份输出与已发布文件逐字节一致。
  文字量宽、日语禁则换行与纵向重排经过静态校验。
  见 [validation.ja-figures.json](validation.ja-figures.json)。
- 42 个模型帧中的 958 个数值、布尔值及 null 叶子保持；原机器键、ASCII 机器字符串、
  算例词元和 `sourceGroup` 均保持。见 [validation.ja-data.json](validation.ja-data.json)。
- 日语连续版含 250 个正文节、253 个独立节、13,563 个唯一 ID、175 份内联资源，
  失效锚点、ID 引用、外部运行依赖及失效搜索落点均为 0。
  见 [validation.ja-complete.json](validation.ja-complete.json)。
- 日语 263 页共 88,058 处实际本地引用，失败 0、待译目标 0；262 页往返不一致 0，
  嵌入标题分歧 0。分页版 183 个、连续版 178 个自检答案，共 361 个，全部默认收起。
- 日语适配相关 32 项测试通过，含首次生成资产路径的 5 项新增测试；
  12 个代码与测试文件经独立审查，无阻塞项。
  三位译者只读交叉核对共 88 条，发现的问题由主流程修复。
  见 [validation.ja-tooling.json](validation.ja-tooling.json) 和
  [work/_ja-cross-review.json](work/_ja-cross-review.json)。这些检查不等于全文逐句人工审校。

日语登记阶段的历史保留检查：中文原文、运行脚本、图形生成器、模型参数与训练记录保持。1,371 份受保护源文件中，
1,370 份字节相同；唯一派生例外为 `assets/i18n-data.js` 的 `metadata.editions` 新增 `ja`，
所有语种界面字典内容均未变。英文仅 `en/assets/i18n-data.js` 与 `en/complete.html`
各新增 5 字节版次列表；移除这一项后，两份文件均回到原哈希。
见 [validation.ja-preservation.json](validation.ja-preservation.json) 和
[work/_ja-edition-publication.json](work/_ja-edition-publication.json)。

日语版次登记阶段记录的连续版 SHA-256（本轮维护后须另存最终哈希）：

- `ja/complete.html`：`234830e46a2a82cdef8042c64c9dda639a7658b8a806173d790a13afab946ca7`
  （33,609,036 字节）
- `en/complete.html`：`3f8cfd8ad50d9d08dc6ff73c7dd92e68dbf1b7828a769ddc0d1af94cf1b6a87b`

英文拼写、术语、词元、模板一致性与嵌入标题已只读复测，无分歧；
英文 263 页的 88,058 处本地引用也再次通过。原英文收尾记录的安全代码注释 39 种 / 41 处、
1,533 个可解析代码块 AST 保持结论继续有效。代码数据、等宽对齐算例及原文件名
按约定保留，不把表覆盖率解释为所有汉字已消失。
本轮未启动服务、浏览器或长进程；宽屏布局、章节定位、连续版滚动与动画交互留给用户验收，
不宣称已完成浏览器交互测试。

---

### 西班牙语与越南语发布结果

本轮翻译、生成与全部静态验证已完成，无代码待办。最终记录见
[validation.es.json](validation.es.json)、[validation.vi.json](validation.vi.json) 和
[validation.multilingual.json](validation.multilingual.json)。浏览器与交互验收仍由用户执行。

西班牙语 `es` 与越南语 `vi` 各 31,633 条译文均已齐译，v01–v65 各 65 批已串行入表。
批次校验通过，数值差异为 0；130 份源契约保持不变，`next_id=31687` 保留。
两语种开始时各有 217 条译文、缺 31,416 条。原契约不重发覆盖；批次与目标文件哈希见
[work/_es-vi-progress.json](work/_es-vi-progress.json)。

#### 已生成与已验证的发布内容

- 两版各有 326 个发布文件，含 262 页分页正文、1 份连续版及 49 个下载镜像；
  图形适配覆盖 777 幅 SVG，207 份图形准备输出与发布文件相符。
- 两版各有 256 条目录项、5,614 条搜索索引，覆盖全部 262 页。日语原有 5,602 条搜索索引保持。
- 四语各 263 份 HTML 的 88,058 处实际本地引用全部可解析；14 份资产 JS 与连续版
  14 段内联 JS 语法检查通过；分页 183 个与连续版 178 个自检答案共 361 个，全部默认收起。
- ES/VI 连续版各有 250 个正文节、253 个独立节、13,563 个唯一 ID；失效锚点、ID 引用与
  外部运行依赖为 0。对应记录见 [validation.es-complete.json](validation.es-complete.json) 和
  [validation.vi-complete.json](validation.vi-complete.json)。
- 工具测试共 77 项（原 71 项加代码接缝回归 6 项），实现侧与独立复核均通过，无阻塞项；
  ES 原 14 处图形溢出已归零。见
  [validation.es-vi-tooling.json](validation.es-vi-tooling.json)。静态量宽不等于浏览器视觉验收。

分项记录另见 [ES 静态检查](validation.es-static.json)、[VI 静态检查](validation.vi-static.json)、
[ES 图形](validation.es-figures.json)、[VI 图形](validation.vi-figures.json)、
[ES 模型布局](validation.es-model-layout.json) 和 [VI 模型布局](validation.vi-model-layout.json)。
代码接缝修复后的实际代码与最终静态产物均已全量复核通过。

#### 四语实际代码保真检查

[work/_es-vi-code-proof.json](work/_es-vi-code-proof.json) 保留内存预检、修复前失败记录与修复后的
四语实际发布检查，最终状态为 `published_code_validation_passed`：

- 英日西越各 262 页中的 2,015 处行内代码均逐字保持。
- 各 1,533 个可解析 Python 块（287 个 pre 块、1,246 个行内片段）的 AST 与非注释词元保持。
- 各 492 个 pre 块符合当前注释译文，39 种安全注释的 41 处实例均齐备。
- 英西越代码页各 474 处行号义项正确，日语代码路径保持。

内存预检另统计 12,527 个数值常量与 12,735 个字符串常量实例；这些检查未执行示例程序，
不把语法结构保持解释为对中文原例计算正确性的重新证明。

实际检查曾发现每版 6 处代码内容多了尾空格，涉及 `data:`、`query:`、`passage:`、`<PAD>` 与
`<untrusted>`。原因是 `apply.space_seams` 的标点接缝匹配跨过 `</code>`，却将新间隔插入代码内侧。
永久修法跟踪每轮匹配输入中的行内代码内容范围：当匹配跨过闭标签时，将新句间空格放到闭标签外；
不改代码内部标记、实体或原有空白。英文既有同类缺陷也按同一规则修复，日语字节路径保持。
主流程重生成受影响英西越分页及派生产物后，四语行内代码均达到 2,015/2,015 逐字保持。

越南语代码行号已通过 `overrides.json` 的页面覆盖使用 `Dòng N`；第 8–117 行的 110 个精确键
覆盖了 346 处实例，连同前 7 个既有键，实际发布页全部 474 处行号正确。共享表的矩阵义项 `Hàng N` 保持。
[行内语法复核](work/_es-vi-inline-grammar-review.json) 记录 5 页、7 个局部上下文的短串组合问题，
包括「从 X 到 Y」、旋转和加入第二条输入。它是来源与修正建议记录，不代替全文母语审校。

#### 版次登记与原文保留

正式版次已登记为 `zh-CN / en / ja / es / vi`，四个非中文版本的运行包与连续版已同步。
[work/_es-vi-edition-publication.json](work/_es-vi-edition-publication.json) 证明根界面派生包仅变更
`metadata.editions`，125 个界面键与 5 份语言字典保持，132 处运行来源及 104 条来源字符串保持；
登记不改译表。连续版最终哈希以主流程在代码接缝修复后更新的登记与分项记录为准，
不使用前一阶段哈希替代最终结果。

[validation.es-vi-preservation.json](validation.es-vi-preservation.json) 将本轮产物与原 1,371 份
受保护源文件基线对照：1,370 份字节相同，唯一派生例外为 `assets/i18n-data.js` 的版次元数据。
中文正文、原代码、图形、权重与训练记录未改。表中永久 ID 无重复，`next_id=31687` 与顶层元数据保持。
32 项中文原文问题仍待用户裁决。

英文 5 个译文字段已受控修复：819 的 copula、1914/1915 的 teacher-forcing 数据以及
6121/25885 的检索字面量；另保留布尔语境的页面覆盖。见
[work/_legacy-en-repair-plan.json](work/_legacy-en-repair-plan.json)。相关分页、搜索与连续版已按受控范围
重建；代码接缝修复另有四语实际代码证明，不沿用早期「英日全部未改动」结论作为本轮证明。

#### 后续维护与人工验收

译者继续读取 `glossary.es.json` / `glossary.vi.json`、`work/_reference.<lang>.txt` 和
[ES/VI 协议](TRANSLATING.md#spanish-and-vietnamese-editions)。译者只交目标批次、运行 `ingest --check`；
主流程串行入表，再运行对应语言的 embedded 对齐与往返校验。英文 spelling / terms / vocab /
consistency 修复器不可对 `es` 或 `vi` 运行 `--fix`。中文算例词元、UTF-8 流数据及字面量保持原样。

浏览器布局、章节定位、滚动、帧播放、分组筛选、动画交互及全文母语审校仍由用户验收。
本轮未启动服务、浏览器或长进程；静态检查不写成交互已测。

---

## 5. 发批次给译者

每批一个 agent，提示词模板：

> 工作目录：/Users/chuhemiao/toyama/AI_Engineering_System_Handbook_ZH
>
> 完整阅读并严格遵守 `i18n/TRANSLATING.md`，包括其中的「Settled house terms」表、
> 算例词表规则（我 爱 学习 你 在标签和词元列表中保留中文）、以及拼接空格由构建
> 集中处理这一点 —— 写自然的英文，完全不用管行内标签旁的空格，也不要为了让
> 接合处读通而扭曲措辞。拼写也不用花精力，`i18n/spelling.py` 会统一。
>
> 你的批次：`i18n/work/pNN.en.src.txt`
> 目标语言：en
> 写出：`i18n/work/pNN.en.txt`
> 自检：`python3 i18n/batch.py ingest pNN.en.txt --check`
>
> `# page:` 行标明每段字符串来自哪一页 —— 短标签含义不明时去读那一页的 HTML。
> 这些注释行不要出现在你的输出里。
>
> 表里已有 31,633 条英文译文，所以你的字符串中嵌入的复用标题、模板、课程名多数
> 已有定译 —— 查出来逐字复用。`i18n/work/_reference.en.txt` 有最高频的 900 条，
> 其余可直接查 `i18n/table.json`。这一点要紧，因为 `i18n/embedded.py` 会检查
> 每个链接的文本是否与它指向的标题一致。
>
> 回报：写了多少行、校验器最终输出、以及任何你无法从上下文确定含义的字符串。

**按当前可用并发槽分批，最多约 6 个译者**。本轮最多 3 个子代理并行，留根代理串行入表。之前同时跑 12–13 个两次触到额度上限，所有 agent 中途死掉、
一个文件都没落盘。6 个一波能保证每波都有产出。

译者绝不能跑不带 `--check` 的 `ingest` —— 那会写共享的表，并发时互相覆盖。

---

## 6. 已定决策，不要重新讨论

| 中文 | 英文 | 依据 |
|---|---|---|
| 宿主 | harness | 教材自己的 glossary.html 印的是 `Harness / 宿主执行框架` |
| 宿主（MCP 语境） | host | `Host` 是该协议里的角色，不是 harness |
| 宿主（机器／内核义） | host | `宿主内核`、`限制宿主影响` 指宿主机 |
| 追问： | Follow-up: | 211 处里的多数 |
| 预备知识： | Prerequisite: | 每处只引一节课，单数正确 |
| 子Agent | sub-agent | 多数 |
| 压缩 | compaction / compress | 上下文压缩 vs 张量压缩，按义项分 |
| 显存 | VRAM | glossary |
| 推理 | inference / reasoning | 模型执行 vs 推理模型 |
| 产物 | artifact | 美式 |
| 拼写 | 美式 `-ize` | glossary.html 印的是 `optimization`/`Quantization`/`Normalization` |

### 算例词表必须保留中文

`labs/model` 声明 `VOCAB = ['PAD','我','爱','学习','你','！','BOS','EOS']`，
`labs/model/data` 里每个训练后参数都按这张表的行索引算出。所以 `t=1 · 我`、
`位置1 · 爱`、`[我,爱,学习,EOS]`、`PAD0、我1、爱2…` 这些是**数据不是文案**，
翻掉就与 `run.json` 和训练后权重脱节，也违反 AGENTS.md 的「改变示例须重新运行」。

规则：**译外框、留词元**（`位置2 · 学习` → `position 2 · 学习`）。散文中可以
一次性加注（`我爱学习 ("I love study")`），但标签保留原字。`batch.py` 的校验器
对这四个字做了豁免 —— 它以前不豁免，结果**逼着三个译者产生了错误**。

**这条规则由 `i18n/vocab.py` 强制，必须进固定流程。** 我最初是手改表，结果重新
ingest 源文件时被 agent 的原始译法整批覆盖回去（回归 24 条）。对表的一次性手改
不持久，只有常驻脚本才持久。

`vocab.py` 的判别要**按词元各自的线索**，不能看整串：`Q111｜In-Context Learning
到底是不是"学习"？` 里引号中的 `学习` 是在质疑「这算不算学习」，是普通词；而那个
引号一旦被当成线索，同句里的 `你` 也会被误报。这类「引号里是普通词」的例外写在
脚本的 `ALLOW` 里，按子串匹配（因为目录复合串会嵌入同一段话）。

独立 `！` 的 10 处全是词表单元格（`<td>5</td><td>！</td>`），也要保留。

### 一串两义：`i18n/overrides.json`

按字符串去重的固有代价是同一短串在不同位置可能需要不同英文。实测问题全集是
347 种片段 / 624 处 / 共 1,090 字，其中真正需要分化的只有 3 处，按「页 + 中文串」
记在 `i18n/overrides.json`，每条写了证据。

结构性修法（把 `<code>` 当行内元素、整句合并）量过代价：**多译 24 万字（+34%）**，
因为合并后句子带上各自的代码就不再重复，去重收益被摧毁。不划算，已否决。

### `terms.py` 的 `宿主` 判别已改为显式清单

曾经用正则判义项，两个方向都出错过：机器义的模式 `宿主机` 命中了 `宿主机制`
（harness 机制），而「句中出现 MCP 就排除」又把 `宿主允许的动作`、
`宿主仍负责模型输入、授权和任务执行组织` 这些 harness 义排除掉了。

现在例外写在 `i18n/term-exceptions.json`，**按中文串为键**（id 曾被重分配过，
不能用作键），19 条逐一读上下文核验过：17 条是 MCP 的 Host 角色，2 条是容器的
宿主机／内核。其余全部为 harness。`terms.py` 可反复运行，当前两个方向都归零。

---

## 7. 待用户裁决的中文原文问题

完整清单见 [SOURCE-ISSUES.md](SOURCE-ISSUES.md)，目前 32 项。所有问题只记录，未改中文，
不由翻译流程代为裁决。

问题包括课程入口与旧课号、旧中文连续版同步差异、40 个中文搜索图解锚点，以及公式条件、
概率与对数概率、缓存形状、链接释义、预备说明错位和目标右移方向等。
英文与日语均保留原文事实和限定。两版连续版取当前分页正文，搜索从当前语言页面重建；
这些派生步骤不修改中文来源，也不修正原文中的事实或措辞。

---

## 8. 各语言版再生成

### 共同生成顺序

正文、代码注释、JS 散文、运行文案、SVG 标签、目录分类与连续版外壳共用 `table.json`。
当前 runtime / figure / complete 适配器均显式支持 `en`、`ja`、`es` 与 `vi`。
维护者串行写表与生成；译者仍只交付自己的批次文件、运行 `ingest --check`。

修改英文译文后，先按第 3 节运行英文修复器和往返验证。
修改日语译文后，运行批次检查、`embedded.py --lang=ja` 与往返验证；
不得对日语运行英文 spelling / terms / vocab / consistency 修复器的 `--fix`。

首次生成和普通译文更新均按以下顺序执行。`apply.relink` 为 `en` / `ja` / `es` / `vi` 声明的
14 份局部 JS 预留语言版路径，即使生成文件尚不存在也保持该路径；
未声明且无语言镜像的资源（包括共享 CSS）仍按原规则指向共享根目录。
无需先运行 runtime write。以下以日语为例；其他语种替换对应的 `--lang`。
ES/VI 全部必需译文齐备后才执行最终生成；同样不得运行英文修复器：

~~~bash
python3 i18n/apply.py --verify
python3 i18n/apply.py --lang=ja
python3 i18n/gen_assets.py --lang=ja
python3 i18n/data_strings.py write --lang=ja
python3 i18n/runtime_strings.py write --lang=ja
python3 i18n/figure_strings.py write --lang=ja
python3 i18n/build_complete.py --lang=ja
python3 i18n/links.py --lang=ja
~~~

`apply.py` 会复制原页面 SVG，`data_strings.py` 会复制原 SVG 字段，必须在图形适配前运行。
SVG 适配后再运行二者，须重跑 `figure_strings.py write` 和连续版构建。
不要运行会写中文连续版的 `inline_complete.py`。

### 来源注册与目录分类

`runtime_strings.py`、`figure_strings.py` 和 `complete_strings.py` 的 `collect`
只写各自 registry，不写翻译表。`table.py build` 合并来源计数并分配永久 ID，
保留整个顶层对象、旧 ID、其他语言及退役条目。源码或注册表漂移时，适配器拒绝生成；
应先核对来源变化，再 collect、重建表、导出新契约并补译，不能绕过检查。

`catalog-kinds.json` 管理 7 种分类的中文来源键，`table.py` 注册这些来源；
`gen_assets.py` 从表读取所选语言译文，缺译或遇到未注册分类时拒绝生成。
配置中的旧英文值仅作迁移历史，不再充当另一个译文来源。

### 新完整语种的版次登记

普通译文更新不需重登记 `editions`。新增完整语种时，先完成分页、数据、运行脚本、
图形、下载及连续版的静态校验，再执行本段。`build.py` 的自动判断只检查全部分页是否存在；
运行脚本和图形是否齐备仍由维护流程核验。

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

`build.py` 更新共享派生包 `assets/i18n-data.js` 中的 `I18N_META.editions`；
本轮结果为 `zh-CN / en / ja / es / vi`，所有语种界面字典逐字内容保持。
随后 `runtime_strings.py collect` 刷新这一输入的指纹，不写表。
本轮核对 132 处来源、104 条字符串及全部 items 精确不变，因此无需重建表。
对本次登记后所有已发布语种重写运行包和连续版，使版次列表同步；本轮英日西越四版均已同步。
任一命令失败时停止登记后的流程并处理失败，不把部分成功视为登记完成。
这个阶段不要重跑 apply / data，以免覆盖已经适配的 SVG。

### 图形、播放器与链接的已定规则

- `figure_strings.py` / `figure_layout.py` 使用当前已发布 SVG，不导入旧生成器、不重跑实验。
  保留原数值、横向比例、标识符、颜色与帧高亮；英文按词量宽折行，日语按禁则换行，
  并调整纵向空间。静态量宽证明不能代替浏览器视觉验收。
- 普通概念词允许自然语法变化，如英文 API → APIs；代码形式 API() / API[] / API= 严格保留。
- `data_strings.py` 在语言版 MODEL_FRAMES 中保留 `sourceGroup` 原键，
  `runtime_strings.py` 用它匹配原 `data-allowed-groups`；可见选项显示译后的 `group`。
  不得翻译机器字段后再靠无匹配回退显示所有阶段。
- `links.py` 解析实际 HTML 属性。连续版源码面板中的 `&lt;a href=...&gt;` 是展示文本，
  不能用全文正则将其当作真实链接；真实缺失文件仍以非零状态拒绝。

### 连续版与人工验收

`build_complete.py` 从当前语言分页正文组装，沿用原有 250 节顺序，另有资源节和两个工程附节。
ID、锚点、SVG 引用和无障碍 ID 引用统一加前缀；资源内联，搜索与数据使用最终 `<lang>/assets`。

先前要求「重建中文与旧连续版逐字相同」已由完整诊断修正：250 节中 108 节规范化相同，
142 节反映旧版同步差异，详情见 `SOURCE-ISSUES.md`。中文诊断仅允许临时输出，不写中文正本；
`/tmp` 不是永久交接脚本或证据来源。当前构建逐节检查文字、代码、SVG 几何、披露状态及资源。
可用正式 CLI 只读核对现有语言连续版：

~~~bash
python3 i18n/complete_strings.py check --lang=ja
python3 i18n/build_complete.py --lang=ja --check
python3 i18n/complete_strings.py check --lang=en
python3 i18n/build_complete.py --lang=en --check
~~~

静态证据存于第 4 节链接的正式验证文件。浏览器布局、章节定位、滚动、帧播放、分组筛选
与动画操作留给用户验收；本轮未启动浏览器或服务，不把静态验证写成交互已测。

### 日语维护约定

1. 遵守 `TRANSLATING.md` 的 Japanese edition、`work/_reference.ja.txt` 和 `glossary.ja.json`。
   中英词表有些是关联概念，不能把 Bootstrap 当成「置信区间」的日语译名。
2. 原共享层与 u01–u54 已全部完成，另有 `catalog-01.ja` 的 4 条来源。原源契约不得重发覆盖。
   `work/_ja-unique-corrections.json` 记录接缝修正与目录规范化，不能用早期快照恢复掉已核验修正。
   后续新批次仍通过 `batch.py export ... --lang=ja` 与串行 ingest 保留永久 ID 和其他语言。
   新 src 保留真实首尾空白，不得覆盖已交译源契约。
3. 不跑英文修复器。`embedded.py --lang=ja` 按来源结构对齐目录与侧栏，完整标题是同题侧栏的定译。
   合法纯汉字标签经主流程核对后写入 `ja-approved.json`，只匹配具体 source / target；
   不绕过标签、文件名或空值检查，英文不读取此文件。假名判定只认实际字母，
   中点、长音符、浊点等单独出现不抵消纯汉字复核。正反例见 `validation.ja-kana.json`。
4. `overrides.json` 继续处理具体页面的短串义项；「是」作布尔值的两页使用 `ja=はい`：
   `chapters/11.html` 三格、assignment4 两格；交叉 QA 的局部句接缝也保留页面覆盖。
5. `apply.py` 支持日语 lang、空格和语言缺省回退，正文单位须齐译才生成。
   界面提示跟随本页 `i18n-scope`，不能把共享中文页面的「正文仍为中文」说明带入日语版。
6. 保留算例数据与文案的区别。`foundations/28.html:36` 的 A/B/C 倒排例中，code 内
   「排除、路径、缓存、日志、输出」是实际匹配词项；条目 15924、15926、15929 的索引与查询
   保留相同中文词项，只译外框。`chapters/04.html` 的 `[BOS, 我, 爱, 编程, EOS]` 同理：
   条目 1914、1915 的「编程」与输入代码、监督标签一致，不译成概念词。
   README 错字正误对照、字节流文件名也按原始数据处理；普通说明仍须翻译。
7. 相同短题名嵌在不同链接组时，也复用定译。`work/_ja-short-titles.json` 记录
   「KV Cache从零解释」统一为「KVキャッシュをゼロから解説する」。
   不能因独立裸串未抽取而让同题短名随批次变化；不为此增造表键或 ID。

### 工具事实定位

- 首次生成的局部 JS 路径：`apply.py:38` 的 `EDITION_ASSETS`、`:127` 的 `relink`；
  来源由 runtime / data 资产常量和目录、搜索生成器的声明输出确定。
- 来源注册与永久编号：`table.py:34` 的 `reconcile`、`:57` 的 `auxiliary_counts`；
  目录分类消费方为 `gen_assets.py:48` 的 `main`。
- 版次元数据：`build.py:20` 的 `editions`、`:49` 的 `main`；
  运行包消费方为 `runtime_strings.py` 的 `prepare` 与 `collect` 仅刷新 registry。
- 图形写出与先后依赖：`figure_strings.py:535` 的 `prepare`；
  连续版语言资产消费方为 `build_complete.py:260` 的 `Builder`。

---

## 9. 我踩过的坑，别重复

1. **表的 key 一定要用永久 `id`，不能用排序位置。** 我最初用 `sorted(-n, key)` 的
   位置做 key，往表里加字符串后排序一变，已发给译者的 key 全部指向别的字符串 ——
   旧的 ingest 会把 600 条译文**静默写到错误的条目上**，而当时的校验只比标签和中文，
   能通过。有 4 个 agent 独立测出了这件事。
   现在 `ingest` 以 `.src.txt`（发出去的契约）为准配对，`id` 只作交叉校验。

2. **`.src.txt` 不可覆盖。** 我重新导出时覆盖了一个已发出的源文件，等于销毁了那批
   549 条译文的对应记录。`write()` 现在遇到已存在的源文件会跳过。真要重发先手动删。

3. **`table.py build` 必须保留 `id` 和各语言字段。** 它曾经把 `id` 清掉，导致全部
   重新分配，并连带丢了一批译文（已从交付文件重新 ingest 恢复）。

4. **所有脚本都要有 `if __name__ == '__main__':`。** `apply.py` 曾在模块层调用
   `main()`，一个 agent 为验证空格处理 import 了它，意外重写了整个 `en/` 输出树。

5. **拼写统一不要用枚举词表。** 枚举会漏词形（`optimiser`、`stabilises`、
   `Contextualisation`）。`spelling.py` 改用模式扫描 + 白名单，白名单还要**前缀感知**
   （`im-precise`、`un-wise`、`over-size` 都要挡住）—— 我的第一版把 `imprecise`
   改坏成了 `imprecize`，工具自己引入了错误。

6. **拼接空格要集中处理，不要让译者扭曲措辞。** 中文在 `<code>` 旁不留空格，英文
   需要，否则渲染成 `improvesANNrecall`、`Xhas shape`。`apply.py` 的 `space_seams`
   处理两种情况：两侧都是单词字符，以及标点紧跟在闭标签之后。保护：`<sub>/<sup>`
   不动（下标必须紧贴），以 `-` 开头的译文不动（刻意紧贴的 `-style`、`-dimensional`）。
   有几个译者在这个机制建好之前为规避问题把接合点挪到了标点上，那些措辞可以回头优化。

7. **中文全角标点会漏抽。** `。`、`、`、`；` 的纯标点文本节点不含汉字，正则抓不到。
   已纳入抽取并自动填译法。注意 `·` 和 `—` 在英文里本就通用、保留；`！` 是词表项、保留。
   另外：标点单元**不能参与合并**，否则会把已译的短语变成新的复合串、架空旧译文
   （我犯过，返工了一轮）。

8. **`consistency.py` 有盲区，`embedded.py` 补上。** 前者按中文前缀分组，抓不到嵌在
   长串中间的模板 —— 目录里写 "Pressing further:" 而它链接到的标题写 "Follow-up:"。
   后者按标签切分后**逐段位置**比对（标签多重集已有校验保证一致，所以中英第 i 段
   必然对应）。不要用「中文包含则英文也应包含」—— 试过，215 处里绝大多数是假阳性，
   因为英文把片段吸收进句子时本来就要改写。

9. **`en/` 的路径重写不能用「加一个 `../`」。** 要按目标相对站点根的路径重算。
   我最初加一个 `../`，抽样测了三个深度都对 —— 因为它们引用的都是 `../assets/x.css`
   这种已带 `../` 的。直到 `links.py` 全量跑才发现 `engineering/agent-evidence.html`
   里的 `agent-practice/verified/manifest.json`（同级目录、无前缀）被指到了
   `en/agent-practice/...`，50 处引用失效。`links.py` 的存在就是为了抓这个 ——
   `../` 数量错了只是 404，不报错。

10. **同时跑 6 个 agent 左右。** 12–13 个两次触到额度上限，所有 agent 中途死掉、
   一个文件都没落盘。额度恢复后用 SendMessage 续跑（保留它们已读的上下文），
   不要重开新 agent。

11. **写表要保存整个顶层 dict。** 只写 {'s': t} 会丢 next_id，使新条目与旧永久 ID 撞号。
    table.py 的安全高水位也不能成为丢元数据的理由。重建必须保留旧 ID、各语言和退役条目。

12. **源契约使用真实空白。** 曾把首尾空格换为 ␣ 导出，ingest 便找不到原中文 key，
    还可能把有效译文当“源已消失”静默跳过。新导出已修复，旧已发出 src 不可覆盖。

13. **英文修复器不是日语修复器。** --lang 只选择表字段，不会自动把英文模板改成日语。
    日语生成链中不受支持的阶段应显式扩展和验证，不能借参数化掩盖缺口。
