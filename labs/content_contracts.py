"""Small, explicit teaching contracts. No external model/API/GPU is used.

These examples verify mathematics, labels, grouping, restart state and measurement
semantics. They are not implementations of Transformers, vLLM, or CS2680 grading.
"""
from __future__ import annotations
import copy
import math
import re
from fractions import Fraction
from typing import Any, Sequence


def softmax(values: Sequence[float]) -> list[float]:
    if not values or not all(math.isfinite(v) for v in values):
        raise ValueError('Use finite, nonempty scores in this example.')
    m = max(values)
    e = [math.exp(v - m) for v in values]
    return [x / sum(e) for x in e]


def explicit_pairs(tokens: Sequence[int]) -> tuple[list[int], list[int]]:
    if len(tokens) < 2:
        raise ValueError('At least two tokens are needed.')
    return list(tokens[:-1]), list(tokens[1:])


def wrapper_targets(unshifted_labels: Sequence[int]) -> list[int]:
    """The alignment used in the cited ForCausalLMLoss, not a library call."""
    return list(unshifted_labels[1:]) + [-100]


def loss_labels(ids: Sequence[int], valid: Sequence[bool], supervised: Sequence[bool]) -> list[int]:
    if len(ids) != len(valid) or len(ids) != len(supervised):
        raise ValueError('All masks must have the same length as ids.')
    return [token if v and s else -100 for token, v, s in zip(ids, valid, supervised)]


def packed_allow(segment_ids: Sequence[int]) -> list[list[bool]]:
    return [[j <= i and segment_ids[j] == segment_ids[i]
             for j in range(len(segment_ids))] for i in range(len(segment_ids))]


def absolute_allow(query_positions: Sequence[int], key_positions: Sequence[int]) -> list[list[bool]]:
    return [[k <= q for k in key_positions] for q in query_positions]


DATA_FIXTURE = [
    {'id': 'a1', 'source': 'A', 'text': 'A正文'},
    {'id': 'a2', 'source': 'A', 'text': 'A正文'},
    {'id': 'b1', 'source': 'B', 'text': 'B正文'},
    {'id': 'b2', 'source': 'B', 'text': 'B正文'},
    {'id': 'c1', 'source': 'C', 'text': 'C正文'},
    {'id': 'd1', 'source': 'D', 'text': 'D正文'},
]


def grouped_split(rows: Sequence[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """A fixed, auditable fixture, not a general semantic deduplicator.

Exact copies within one source are removed. Versions share a split. Real
cross-source/near duplicates require clustering before splitting as well.
"""
    kept, seen = [], set()
    for row in rows:
        key = (row['source'], row['text'])
        if key not in seen:
            seen.add(key)
            kept.append(dict(row))
    assignments = {'A': 'train', 'B': 'train', 'C': 'validation', 'D': 'test'}
    output: dict[str, list[dict[str, str]]] = {'train': [], 'validation': [], 'test': []}
    for row in kept:
        output[assignments[row['source']]].append(row)
    return output


def parse_exact_number(text: str) -> Fraction:
    """Restricted numeric answer parser; never executes model text."""
    text = text.strip()
    if len(text) > 80 or not re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]+)?|[0-9]+/[0-9]+)', text):
        raise ValueError('Expected a signed integer, decimal or rational a/b.')
    try:
        return Fraction(text)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError('Invalid finite rational number.') from exc


def request_metrics(start_ms: float, emitted_ms: Sequence[float]) -> dict[str, Any]:
    if not emitted_ms or emitted_ms[0] < start_ms or any(b < a for a, b in zip(emitted_ms, emitted_ms[1:])):
        raise ValueError('Token timestamps must be nonempty and monotonic.')
    gaps = [b - a for a, b in zip(emitted_ms, emitted_ms[1:])]
    return {'output_tokens': len(emitted_ms), 'ttft_ms': emitted_ms[0] - start_ms,
            'mean_itl_ms': sum(gaps) / len(gaps) if gaps else None,
            'end_to_last_token_ms': emitted_ms[-1] - start_ms}


def task_metrics(costs: Sequence[float], solved: Sequence[bool], elapsed_s: float) -> dict[str, Any]:
    if len(costs) != len(solved) or elapsed_s <= 0 or any(c < 0 for c in costs):
        raise ValueError('Invalid task measurement inputs.')
    n = sum(solved)
    return {'solved': n, 'cost_total': sum(costs),
            'cost_per_solved': sum(costs) / n if n else None,
            'host_seconds_per_solved': elapsed_s / n if n else None}


def calibrated_fraction(outcomes: Sequence[bool]) -> float:
    if not outcomes:
        raise ValueError('An empty confidence bin has no measured accuracy.')
    return sum(outcomes) / len(outcomes)


def detection_precision(prevalence: float, tpr: float, fpr: float) -> float:
    if not all(0 <= x <= 1 for x in [prevalence, tpr, fpr]):
        raise ValueError('Rates must be probabilities.')
    positive = prevalence * tpr + (1 - prevalence) * fpr
    if positive == 0:
        raise ValueError('No positive predictions.')
    return prevalence * tpr / positive


def checkpoint_demo() -> dict[str, Any]:
    """Real CPU/autograd/AdamW continuation: full state vs weights only.

Uses one scalar parameter, fixed examples and no stochastic layers. This proves
optimizer-state importance, not whole-cluster bitwise reproducibility.
"""
    import torch
    torch.set_num_threads(1)
    def make():
        w = torch.nn.Parameter(torch.tensor([0.25], dtype=torch.float64))
        opt = torch.optim.AdamW([w], lr=0.08, betas=(0.9, 0.999), weight_decay=0.01)
        return w, opt
    examples = [(1., 1.), (2., -1.), (1., 2.), (3., 0.)]
    def step(w, opt, example):
        x, y = example
        opt.zero_grad(set_to_none=True)
        loss = (w * x - y).square().mean()
        loss.backward()
        opt.step()
        return float(loss.detach())
    w, opt = make()
    for pair in examples[:2]:
        step(w, opt, pair)
    checkpoint = {'w': w.detach().clone(), 'optimizer': copy.deepcopy(opt.state_dict()), 'next_index': 2}
    for pair in examples[2:]:
        step(w, opt, pair)
    expected = float(w.detach()[0])
    resumed, resumed_opt = make()
    with torch.no_grad():
        resumed.copy_(checkpoint['w'])
    resumed_opt.load_state_dict(checkpoint['optimizer'])
    for pair in examples[checkpoint['next_index']:]:
        step(resumed, resumed_opt, pair)
    weights_only, fresh_opt = make()
    with torch.no_grad():
        weights_only.copy_(checkpoint['w'])
    for pair in examples[checkpoint['next_index']:]:
        step(weights_only, fresh_opt, pair)
    return {'uninterrupted': expected, 'full_resume': float(resumed.detach()[0]),
            'weights_only': float(weights_only.detach()[0]), 'device': 'cpu',
            'torch_version': torch.__version__, 'optimizer_steps_before_save': 2,
            'scope': 'one scalar; deterministic examples; no GPU, scheduler, dropout or sampler'}


if __name__ == '__main__':
    import json
    print(json.dumps({'checkpoint': checkpoint_demo(),
                      'request': request_metrics(0, [120, 140, 160, 180]),
                      'tasks': task_metrics([.4,.6,.5,.5], [True,False,True,False], 20),
                      'split': grouped_split(DATA_FIXTURE),
                      'detection_precision': detection_precision(.01,.9,.01)}, ensure_ascii=False, indent=2))
