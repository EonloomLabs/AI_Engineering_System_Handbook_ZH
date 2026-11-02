# AI Systems Engineering: from the basics to the internals

[简体中文](README.md) · **English** · [日本語](README.ja.md) · [Español](README.es.md) · [Tiếng Việt](README.vi.md)

Offline textbook · core concepts, internal mechanisms, engineering practice

From the basics to the internals: understand how large language models process input and generate output, how agents use tools and manage context and memory, and how to improve engineering quality by verifiable means.

## Open it

Unpack the archive and open [`en/index.html`](en/index.html). No server, no network, no model API or key.
The language switch in every page header jumps to the same page in another edition.

## How the course is built

The main path is five stages and 68 lessons: observe the system first, then descend layer by layer into the model, then return to full-stack acceptance.

| Stage | Lessons | What it covers |
| --- | --- | --- |
| Observe the system | 01—06 | Turn one task's execution into evidence you can check, before changing anything |
| Build the loop | 07—28 | Tool calls, context, retrieval, memory and failure recovery |
| Optimize the black box | 29—34 | Without opening the model: permissions, a fixed task and complete timing decide whether a change helped |
| Take over the model | 35—63 | From the service interface into tensors, the forward pass, training and inference, down to GPUs and scheduling |
| Full-stack verification | 64—68 | Reconnect multimodality, uncertainty and cross-layer optimization to one set of acceptance criteria |

The 40 foundation lessons carry self-check questions; the 28 systems chapters are built around 112 main questions. Twelve reading topics let you enter from a specific problem once you have the basics.
Body text, figures and formula notes are fully expanded; self-check answers are collapsed by default.

## Where things are

| Path | Contents |
| --- | --- |
| [`en/index.html`](en/index.html) | Reading entry point |
| [`en/complete.html`](en/complete.html) | The same content as one continuous text, standing alone |
| [`en/worked-examples.html`](en/worked-examples.html) | Index of worked examples, searchable by number |
| [`en/worked-model.html`](en/worked-model.html) | The same two sentences carried through every intermediate matrix |
| [`labs/model/`](labs/model/) | The worked model's code, original parameters, trained parameters and numeric records |
| [`worked-examples/`](worked-examples/) | Runnable deterministic numeric and state witnesses |
| [`diagrams/`](diagrams/) | Figure sources, data and checks |
| [`wiki/`](wiki/) | Editable wiki text and table of contents |
| [`editorial/`](editorial/) | How the book was written, and the content migration record |
| [`validation/integration/`](validation/integration/) | This round's checks |
| [`i18n/`](i18n/) | Translation table, tooling and validation records |

## Recompute the numbers

No network, GPU or API key is needed. With Python 3.10 or above, run this in the unpacked directory:

```bash
python3 worked-examples/run_all.py
```

The runnable code and model data sit at the repository root and are shared by every edition; script comments and output are in Chinese.
Changing an example means re-running it and bringing the figures, text, search index and continuous edition along with it — the conventions are in [`AGENTS.md`](AGENTS.md).

## Editions

| Language | Entry point |
| --- | --- |
| 简体中文 (source of record) | [`index.html`](index.html) |
| English | [`en/index.html`](en/index.html) |
| 日本語 | [`ja/index.html`](ja/index.html) |
| Español | [`es/index.html`](es/index.html) |
| Tiếng Việt | [`vi/index.html`](vi/index.html) |

Each edition is 262 paginated pages plus a `complete.html` holding the same content. The Chinese text is the source of record; translation questions and suspected defects in the original are recorded in [`i18n/SOURCE-ISSUES.md`](i18n/SOURCE-ISSUES.md) rather than corrected on the author's behalf.

## Limits of verification

401 teaching examples are not 401 experiments on model capability. Tests check numeric formulas, dimensions, causality, gradients, protocol fragmentation and simplified state behaviour; other scenario examples reason explicitly from stated premises.
They do not prove the effectiveness of a commercial agent, GPU speed, closed-source internals or production safety.
Sources point at actual files, functions and line numbers; engineering derivation, measurement and teaching simulation are labelled separately.
Rounding in numeric figures is for display only; the computation uses full precision.

For the scope of source verification see [`engineering/agent-evidence.html`](engineering/agent-evidence.html), with machine records under `engineering/agent-practice/verified/`.
