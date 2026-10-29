# 界面多语言

支持 5 个语种：简体中文、English、日本語、Español、Tiếng Việt。

本书正文为简体中文；**只有界面外壳做了多语言**。切换语言不会翻译课程内容，
界面上会常驻一条说明（`lang.bodyNotice`），不让读者误以为正文会跟着切换。

## 结构

```
i18n/source.json      词条源表：key + zh-CN + en + ctx（用途说明）
i18n/locales/*.json   各语种译文，每个文件是 key → 译文 的扁平对象
i18n/build.py         打包成 assets/i18n-data.js，并做完整性校验
assets/i18n.js        运行时：套用译文、设置 lang/dir、渲染切换器
assets/i18n.css       切换器样式与 RTL 版式
i18n/inline_complete.py  把上述三者内联进 complete.html（幂等，带哨兵标记）
```

打包成 JS 而非 JSON，是为了让本书在 `file://` 下直接打开也能工作。

## 改动流程

1. 改词条：编辑 `i18n/source.json`，再到各 `i18n/locales/*.json` 补同名 key。
2. 重新打包：`python3 i18n/build.py`。有缺 key、多余 key、译文与中文原文
   相同等情况会逐条报告并以非零状态退出。
3. 校验是否忘了打包：`python3 i18n/build.py --check`。只比对不写入，
   若 `assets/i18n-data.js` 与 `i18n/locales/` 不一致则报错退出。
   页面加载的是打包产物，改了词条不重新打包，线上看到的仍是旧译文。
4. 同步单文件版：`python3 i18n/inline_complete.py`。complete.html 不引用外部
   资源，词条、运行时与样式都内联在其中，改完必须重新内联，否则单文件版
   会比分页版旧。`--check` 只比对不写入，不一致即非零退出。
5. 新增页面：给外壳元素加 `data-i18n="key"`（替换 textContent）或
   `data-i18n-attr="aria-label:key"`（替换属性）。

## 约定

- **不翻译的内容**：课程正文、算例数字、图解、代码、`visual/Fxx.html` 等
  文件路径，以及 `search.pageHint` 里的检索示例（`张量`、`第39课`、`Q001`
  是针对中文索引的真实查询，翻译后会搜不到）。
- **占位符**：`{n}`、`{shown}` 在运行时替换，各语种必须原样保留。
- **RTL**：`ar`、`he` 会把 `<html dir>` 设为 `rtl`；公式、代码、数表与
  分步图解强制保持 `ltr`，它们不是自然语言。
- **诚实性词条**：`lang.bodyNotice` 必须说明正文仍是中文；
  `settings.note`、`article.readStatus` 等存储说明不得添加原文没有的承诺。

## 范围边界：什么算界面，什么算内容

判定依据是「这段文字描述的是**产品**还是**教材**」：

**界面（翻译）**：顶栏与左侧目录的导航项、按钮、对话框、设置项、
折叠控件的摘要、首页的行动按钮与工具面板、目录分组标题、
搜索结果计数、前后导航的「上一课／下一课」。

**内容（保留简体中文）**：课次标题、单元名、正文、算例数字、
图解内部文字、右侧提纲（它是正文小节标题的镜像）、
摘要里写着具体问题的自检答案、书名「AI 系统工程」。

审计方法：按区域（顶栏／目录／提纲／对话框）扫描未带 `data-i18n`
的中文文本节点，并排除 `rail-name`、`rail-code`、`rail-section-name`、
`curriculum-title` 这些内容类节点。只验证「页面接入了 i18n」是不够的——
曾因此漏掉整个首页与目录顶部的导航项。
