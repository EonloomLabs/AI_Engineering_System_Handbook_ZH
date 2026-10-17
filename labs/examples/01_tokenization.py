"""教学级字符 BPE：只演示合并与编码，不是商业模型的 Tokenizer。"""
from collections import Counter
from typing import Iterable


def apply_merge(tokens: list[str], pair: tuple[str, str]) -> list[str]:
    out, i = [], 0
    while i < len(tokens):
        if i + 1 < len(tokens) and (tokens[i], tokens[i + 1]) == pair:
            out.append(tokens[i] + tokens[i + 1])
            i += 2
        else:
            out.append(tokens[i])
            i += 1
    return out


def train_bpe(texts: Iterable[str], num_merges: int = 8) -> list[tuple[str, str]]:
    if isinstance(texts, (str, bytes)):
        raise TypeError("texts 必须是字符串集合，不是单个字符串")
    if not isinstance(num_merges, int) or isinstance(num_merges, bool) or num_merges < 0:
        raise ValueError("num_merges 必须是非负整数")
    data = list(texts)
    if any(not isinstance(t, str) for t in data):
        raise TypeError("训练样本必须是字符串")
    corpus = [list(t) for t in data]
    merges = []
    for _ in range(num_merges):
        counts = Counter(pair for seq in corpus for pair in zip(seq, seq[1:]))
        if not counts:
            break
        # 相同频次时固定排序，保证演示可复现。
        pair = min(counts, key=lambda p: (-counts[p], p))
        if counts[pair] < 2:
            break
        merges.append(pair)
        corpus = [apply_merge(seq, pair) for seq in corpus]
    return merges


def encode(text: str, merges: list[tuple[str, str]]) -> list[str]:
    if not isinstance(text, str):
        raise TypeError("text 必须是字符串")
    result = list(text)
    for pair in merges:
        result = apply_merge(result, pair)
    return result


def self_test() -> None:
    merges = train_bpe(["路径路径", "路径过滤", "路径规范"], 5)
    for text in ["路径过滤", "未知字符 x\n", ""]:
        assert "".join(encode(text, merges)) == text
    assert len(encode("路径路径", merges)) < len("路径路径")
    assert train_bpe([], 3) == []
    try:
        train_bpe("错误输入")
    except TypeError:
        pass
    else:
        raise AssertionError("应拒绝单个字符串作为语料集合")


def run_demo() -> dict:
    texts = ["exclude_paths", "exclude_path", "exclude_files", "include_paths"]
    merges = train_bpe(texts, 10)
    sample = "exclude_paths"
    tokens = encode(sample, merges)
    return {"性质": "字符级教学 BPE，非真实模型计费", "合并规则": merges,
            "文本": sample, "字符数": len(sample), "教学Token": tokens,
            "教学Token数": len(tokens), "可逆": "".join(tokens) == sample}


if __name__ == "__main__":
    import json
    self_test()
    print(json.dumps(run_demo(), ensure_ascii=False, indent=2))
