# 多语言版本：交接说明

本文件记录英文版（后续日语版）的做法、工具、已定决策和剩余工作。
读完这份文件就能接手，不需要重新推导。

搭配阅读：`i18n/TRANSLATING.md`（发给译者的协议）。

---

## 1. 任务与硬约束

把这本中文离线教材（262 页 HTML）做成完整的英文版，放在 `en/` 下，之后做日语版。

**用户定下的约束，必须遵守：**

- 不要启动任何服务或长时间运行的进程（dev server、npm、python server 都不行）。
  用户自己用 codex 做调试和最终验收，机器不能被占住。
- 不要改动中文原文。翻译中发现的原文问题记录下来交给用户裁决，见第 7 节。
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
 "next_id": 28957}
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
| `gen_assets.py --lang=xx` | 从译好的页面重新生成 `catalog.js` 和 `search-data.js` |
| `data_strings.py collect\|write` | `visual-data.js` / `model-data.js` 的散文进出表 |

### 每批回来的固定四步

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

三个检查发布前必须全部归零。另外两个检查：

```bash
python3 i18n/links.py      # 应解析但失败必须为 0（指向未译页面的不算）
python3 i18n/audit.py      # 残留中文按来源归类，核对是否都属已知豁免
```

`links.py` 存在的理由：`en/` 只镜像 HTML 树，所以指向树外的引用在构建时要多加一层
`../`，而指向已译页面的保持原路径。这个重写是整个构建里唯一会**静默**产出坏页面的
环节 —— `../` 数量错了只是样式表 404，不会报错。

---

## 4. 当前状态

- 表：**17,013 / 29,168 条已译，40.2 万 / 69.8 万字（57.6%），全站实例覆盖 93.7%**
- 已生成 **65 页** `en/`（页面要全部字符串齐备才生成，不出半中半英的页）
- `en/assets/` 已生成：catalog.js（256 条目，0 条缺译文）、search-data.js（2,207 条索引）、
  visual-data.js、model-data.js
- 共享层 11 批全部完成（486 条外壳 + 跨页字符串）
- 按页批次 **24 / 48 完成**（p01–p24）

全部门禁当前归零：

```
apply.py --verify   262/262 往返无损
consistency.py      3,637 组模板，0 组分歧
embedded.py         0 处目录／标题不一致
spelling.py         0 条非目标拼写
terms.py            两个方向均 0
links.py            应解析但失败 0 处
```

**未完成：p25–p48 共 24 批**，源文件已导出在 `i18n/work/pNN.en.src.txt`，
约 12,100 条 / 29.5 万字。

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
> 表里已有 12,000+ 条译文，所以你的字符串中嵌入的复用标题、模板、课程名多数
> 已有定译 —— 查出来逐字复用。`i18n/work/_reference.en.txt` 有最高频的 900 条，
> 其余可直接查 `i18n/table.json`。这一点要紧，因为 `i18n/embedded.py` 会检查
> 每个链接的文本是否与它指向的标题一致。
>
> 回报：写了多少行、校验器最终输出、以及任何你无法从上下文确定含义的字符串。

**同时跑 6 个左右**。之前同时跑 12–13 个两次触到额度上限，所有 agent 中途死掉、
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

**一条都没有擅自改动中文。** 完整清单见 `i18n/SOURCE-ISSUES.md`，共 8 项：

1. **`index.html`「从F01开始 →」指向第35课。** 它链 `foundations/01.html`，
   而那页标题是第35课；第01课是 `foundations/22.html`。阅读顺序走课号
   （pager：`chapters/25` → `foundations/01` → `foundations/02` 即 34→35→36）。
   同页上方 `data-i18n` 的 CTA 指向正确。
2. **`chapters/07.html` 裸字母 `M`**（`已经训练好的M权重`、`本M`，全书仅此页 3 处）。
   该页符号表把 `M` 定义为掩码不是模型。两个译者独立判断它指贯通模型，但都保留
   裸字母未作断言。
3. **`chapters/17.html`「会降低延迟且可能阻塞不必要的任务」。** 整段论证不要等
   全量索引，但「降低延迟」是收益，与并列的「阻塞不必要的任务」方向相反，疑为
   「增加延迟」之误。英文按原文直译为 lowers latency，未代为修正。
4. **`chapters/18.html` E35**：正文说「第8天」，实验记录字段是 `at_day6_known_day9`。
5. **`chapters/24.html`「版本包V1={贯通模型1,提示P1,工具T1,索引I1}」**：
   其余三项是 P1/T1/I1，V2 的是 M2/P2/T2/I2，首项疑应为「模型M1」。
6. **`元` 作货币共 3 处**（20元 / 100元 / 每次1元），但邻近声明称数字是「虚构的
   统一单位」。现译 "yuan"；若改为抽象 "units"，三处应一并处理。
7. **`<code>` 内中文会直接出现在英文页上**（四处影响阅读）：
   `chapters/25.html` 的 `max(3,5)+2=7秒`、`chapters/28.html` 的 Mermaid 图源
   `模型提议 --必须经校验--> 执行器`、`chapters/16.html` 的
   `[query,document]→联合模型→相关性分数`、`chapters/26.html` 的 `平均(pᵢ−yᵢ)²`。
8. 另有若干措辞判断，各批次报告里都标了，不影响正确性。

---

## 8. 剩余工作，按优先级

### 一、把 p19–p48 跑完（主线）

30 批，约 16,200 条 / 39 万字。按第 5 节发批次、第 3 节的四步收。

### 二、`en/` 的派生产物

页面全齐之后：

```bash
python3 i18n/gen_assets.py --lang=en     # catalog.js + search-data.js
python3 i18n/data_strings.py write --lang=en   # visual-data.js + model-data.js
python3 i18n/build.py                    # 重算 I18N_META.editions
```

`gen_assets.py` 是**从译好的页面重新生成**，不是翻译文件 —— 教材自己的
`rebuild_derivatives.py` 就是这个路子（derived 产物重新生成，不手改）。
这样搜索索引和侧栏永远不会和读者落地的页面说法不一致。

`build.py` 算出的 `I18N_META.editions` 只列出**完整**的版本。262 页全齐时 `en`
才会自动加入，切换器才会跳转 —— 所以不会把读者送到不存在的页。

### 三、代码注释（2,103 字 / 47 行）

`<code>`/`<pre>` 内共 5.8 万字中文，按性质拆开：

| | 字数 | 能否翻译 |
|---|---|---|
| 版面内（等宽对齐） | 56,411 | 需逐块重排 |
| 代码注释 | 2,103 | **安全，改动不影响任何对齐** |

注释那部分可译：注释左边和其它行都不会位移。做法是扩展 `extract.py`，在跳过
元素内部只抽取注释文本。

版面那部分不行：验证过 `第一句查表后：       第二句查表后：` 是双栏布局，
用空格垫到第二个矩阵的起始列，译成英文（38 字符 vs 7 字）右栏会被推开。

### 四、SVG 图内标签（3,180 处 / 2 万字 / 157 页）

**可以正确做，但是独立工程。** 三个生成器（`diagrams/renderer.py`、
`mechanisms/figures.py`、`visual/labs/figures.py`）都会量文字宽度并自动折行，
`mechanisms/figures.py` 甚至已经把拉丁字符建模成 0.56 宽 —— 换英文标签版面会
自己重排。

障碍是另外两件：标签写死在这三个 Python 脚本里（共 4,618 字），而生成器→页面的
内联脚本 `diagrams/build_exports.py` 依赖仓库里不存在的 `source/` 目录和 bs4，
在这里跑不起来。

另有 **101 处 / 112 字是算例词表，必须保留中文**（见第 6 节）。

### 五、`en/complete.html`

内容与 262 页相同，但切分边界不同（80.7% 重合）—— 单独翻会白做 10.4 万字重复
内容。正解是从 `en/` 页面重新内联。

**已查明的变换规则**（对比 `foundations/05.html` / `chapters/02.html` /
`index.html` 的 article 与它们在 `complete.html` 里的 section 得出）：

每页的 `<article>` 内容包进

```html
<section class="standalone-section" data-book-page="foundations/05.html" id="foundations--05">
```

`id` 由路径去掉 `.html`、`/` 换成 `--` 得到。页内所有 `id` 加 `<sid>--` 前缀，
页内链接改写为对应的 `#<sid>--<anchor>`。

**剥掉的元素**（三页一致）：

- `<div class="breadcrumb">`
- `<span class="anchor-target">`（如 `id="legacy-F05"`）
- `<details class="mobile-outline">`（内含 `<nav class="toc">` 和 `<summary>`）
- pager 的 `<nav>`

**收录范围：250 个 section，不是 262 页。** 未收录的 12 页是
`about.html`、`advanced-labs.html`、`coverage.html`、`guide.html`、
`engineering/agent-evidence.html`、`engineering/agent-validation.html`、
`labs/projects/assignment1–5.html`、`labs/stack/code.html`。
`en/complete.html` 应保持同样的收录范围。

**正确性可以验证**：先用同一套代码从**中文**页面重新生成一份 `complete.html`，
与现有的 34MB 文件对比。能复现就说明变换对，再跑 `en/`。这是唯一不靠猜的做法 ——
上面的规则是从三页归纳的，剩下 247 页可能有我没见到的边界情况。

bs4 不可用，所以要用纯标准库重写（`i18n/inline_complete.py` 已经是这个路子）。
另外 `complete.html` 里内联了 3 个 `<style>` 和 16 个 `<script>`，英文版要内联
`en/assets/` 的那几个语言相关文件而不是根目录的。

### 六、日语全量

工具已参数化，`--lang=ja` 即可。同一张表加 `ja` 字段，486 条外壳的杠杆照样复用。

日语的校验不能用「含中文字符」判定（汉字重叠），`batch.py` 已改为**必须含假名
且不与原文相同**。

还需要：
- `i18n/work/_reference.ja.txt`（从 125 条界面日语词条起步）
- 日语术语表（教材的 `glossary.html` 只有中英对照）
- `apply.py` 的拼接空格处理对 `ja` 已自动跳过（日语不用词间空格）

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
