# Translating this book

This is an offline Chinese textbook on AI systems engineering. We are building
full translations of it. Translation is keyed by **string**, not by page: the
same Chinese sentence recurs across pages (the book rail repeats all 262 titles
on every page), so each distinct string is translated once and applied
everywhere. That is what keeps the wording consistent across 262 pages.

## Before you start

Read both, every time:

- `i18n/work/_reference.<lang>.txt` — strings already translated, most-used
  first, plus the book's own bilingual glossary. Follow their terminology,
  register and punctuation. They set the house style. Do not re-translate them.
- `i18n/glossary.json` — the 104 term pairs from the book's own `glossary.html`.

## The file protocol

Your batch is `i18n/work/<name>.<lang>.src.txt`. Each line is

    N<TAB>Chinese text

`N` is a **table key**, not a line counter. Lines ending in ` [tags]` contain
inline HTML; that marker is not part of the text and must not be reproduced.

Write `i18n/work/<name>.<lang>.txt`: one line per input line, `N<TAB>translation`,
same `N` values, same order, nothing else but optional `#` comments.

## Rules

- Every HTML tag and attribute stays byte-identical — `href`, `class`, `data-*`.
  You may **move** a tag to suit the target word order; you may not drop, add or
  alter one.
- Unchanged: digits and numeric values, code identifiers, file names, anchors,
  commit hashes, dates, units, math symbols (Σ, ≈, d_k), and names such as
  Q/K/V, RoPE, GQA, BM25, MCP, SSE, LoRA, FlashAttention, PagedAttention.
- `第NN课` → lesson NN, `单元NN` → unit NN, `作业NN` → assignment NN, in the
  target language's own form. Keep the `｜` and `·` separators where they are.
- Register: plain, precise, unhurried technical prose. Explanatory, never
  promotional. Prefer the concrete verb.
- **The book is careful about the status of its evidence, and that must survive
  with the same force.** 教学示例 / 独立例 / 独立微例 / 不是产品实测 /
  不代表商业模型 / 不能据此声称 / 示意图 are deliberate hedges separating a
  teaching construction from a measured result. Translate them as hedges of
  equal strength. Never strengthen a claim, never drop a disclaimer, never add
  one. Likewise keep 工程推导 (engineering derivation), 实测 (measured) and
  教学模拟 (teaching simulation) distinguishable, as the book distinguishes them.
- **The worked model's vocabulary stays in Chinese.** `labs/model` declares
  `VOCAB = ['PAD','我','爱','学习','你','！','BOS','EOS']`, and every trained
  parameter under `labs/model/data` is indexed by those rows. A label like
  `t=1 · 我` or `位置1 · 爱` is therefore **data**, not prose: rendering it as
  `t=1 · I` makes the figure disagree with `run.json` and with the weights, and
  AGENTS.md requires an example to be re-run rather than relabelled. Translate
  the frame around the token (`位置1 · 爱` → `position 1 · 爱`) and leave the
  token itself. The checker exempts these four characters, so they pass.
  Sentences *about* the example may gloss a token once for the reader, e.g.
  "the teaching text is 我爱 (I love)", but the labels keep the glyphs.
- **Spelling follows the book's own glossary**, which prints `optimization`,
  `Quantization`, `Normalization` - so American `-ize/-ization`, and
  `behavior`, `color`, `catalog`, `labeled`. (Earlier batches used British
  forms; those have been normalized, and `_reference.en.txt` is now correct.)
- Very short fragments (与, 和, 得到, 通过, 无, 时间) are pieces of one sentence
  split by inline markup. Translate each as the connective that sentence needs.
- Chinese full-width punctuation becomes the target language's equivalent. A
  fragment that begins with 。 begins with the target's sentence-final mark plus
  a space.
- Spacing at an inline-element seam is **handled for you**, in two steps.
  Ingest carries the source fragment's own surrounding whitespace onto your
  line, and the build then inserts the space English needs wherever a word
  runs into a `<code>`, `<a>` or `<strong>` that Chinese set without one. So
  write the natural English and ignore edge spaces: `improves`+`<code>ANN</code>`
  +`recall` comes out as "improves ANN recall" on its own. Do not contort the
  wording to make a seam read, and do not add edge spaces yourself.
  Two things the build deliberately leaves alone, so they still work: a
  translation that starts with punctuation stays attached (`-style` after
  `WordPiece`, `-dimensional` after `d`), and `<sub>`/`<sup>` never gain a
  space. If you do need an edge space the source lacks, write `␣` there.

## Settled house terms

These were split across batches and have been normalized; follow them.

| Chinese | English | why |
|---|---|---|
| 宿主 | harness | the book's own glossary prints `Harness / 宿主执行框架` |
| 宿主 (in MCP) | host | `Host` is a role in that protocol, not the harness |
| 追问： | Follow-up: | majority of 211 |
| 预备知识： | Prerequisite: | each one introduces a single lesson |
| 子Agent | sub-agent | majority |
| 压缩 | compaction | glossary |
| 显存 | VRAM | glossary |
| 推理 | inference / reasoning | model execution vs reasoning models |
| 产物 | artifact | American spelling |

`python3 i18n/spelling.py` sweeps the -ize family and the other American forms,
so do not spend effort on spelling; write what comes naturally and it is fixed.

## When one string needs two translations

Because translation is keyed by the string, one Chinese string gets one
translation on every page. A few one-character function words break that: 是 is
a copula inside a sentence (`Embedding矩阵 E 是 [V,d]`) and a yes/no value inside
a table cell (`read_file | 是 | 直接可见`). Translate for the reading that fits
most places, then **say so in your report**: name the string, the page, and the
other reading. `i18n/overrides.json` records the per-page exceptions, and the
maintainer adds them there rather than you compromising the common case.

## Scratch files

Several translators work at once in one scratchpad. Give any scratch file a
name unique to your batch (`<batch>_notes.txt`), or a sibling will overwrite it.

## Self-check

    python3 i18n/batch.py ingest <name>.<lang>.txt --check --lang=<lang>

It must print `条通过校验`. It catches missing or extra keys, empty lines,
untranslated text and inline-tag mismatches. Fix and re-run until clean.

## Two checks the maintainer runs over everything

    python3 i18n/consistency.py        a shared Chinese frame rendered two ways
    python3 i18n/embedded.py           a link's text against the heading it points at
    python3 i18n/vocab.py              the worked model's tokens still in Chinese

The second is why reusing canonical wording matters: a chapter's table of
contents is one string holding every heading on the page, so if you translate a
heading differently from the TOC entry that links to it, a reader sees two
different headings. Both checks must come back at zero before a release.

## Hard constraints

- **Never** run `ingest` without `--check`: it writes a shared table and would
  race with the other translators working at the same time.
- **Never** start a server, dev service or any long-running process. The user
  debugs and accepts this project themselves; nothing here may load the machine.
- Edit no file other than your own `i18n/work/<name>.<lang>.txt`.
