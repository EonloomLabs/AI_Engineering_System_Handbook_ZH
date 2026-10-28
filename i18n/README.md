# 界面多语言

本书正文为简体中文；**只有界面外壳做了多语言**。切换语言不会翻译课程内容，
界面上会常驻一条说明（`lang.bodyNotice`），不让读者误以为正文会跟着切换。

## 结构

```
i18n/source.json      词条源表：key + zh-CN + en + ctx（用途说明）
i18n/locales/*.json   各语种译文，每个文件是 key → 译文 的扁平对象
i18n/build.py         打包成 assets/i18n-data.js，并做完整性校验
assets/i18n.js        运行时：套用译文、设置 lang/dir、渲染切换器
assets/i18n.css       切换器样式与 RTL 版式
```

打包成 JS 而非 JSON，是为了让本书在 `file://` 下直接打开也能工作。

## 改动流程

1. 改词条：编辑 `i18n/source.json`，再到各 `i18n/locales/*.json` 补同名 key。
2. 重新打包：`python3 i18n/build.py`。有缺 key、多余 key、译文与中文原文
   相同等情况会逐条报告并以非零状态退出。
3. 校验是否忘了打包：`python3 i18n/build.py --check`。只比对不写入，
   若 `assets/i18n-data.js` 与 `i18n/locales/` 不一致则报错退出。
   页面加载的是打包产物，改了词条不重新打包，线上看到的仍是旧译文。
4. 新增页面：给外壳元素加 `data-i18n="key"`（替换 textContent）或
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
