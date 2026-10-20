"""合成排名上的 RRF、Precision、Recall、MRR 和 nDCG。"""
import math


def unique(seq):
    return list(dict.fromkeys(seq))


def rrf(rankings: list[list[str]], constant: float = 60.0) -> list[tuple[str, float]]:
    if not math.isfinite(constant) or constant < 0:
        raise ValueError("平滑常数必须非负且有限")
    scores = {}
    for ranking in rankings:
        for rank, doc in enumerate(unique(ranking), 1):
            scores[doc] = scores.get(doc, 0.0) + 1 / (constant + rank)
    return sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))


def metrics(ranking: list[str], relevance: dict[str, int], k: int) -> dict:
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ValueError("k 必须为正整数")
    if any(v < 0 for v in relevance.values()):
        raise ValueError("相关性等级不能为负")
    top = unique(ranking)[:k]
    relevant = {doc for doc, grade in relevance.items() if grade > 0}
    hits = sum(doc in relevant for doc in top)
    # 按请求的 k 作分母；结果不足 k 时空缺算未命中。
    precision = hits / k
    recall = hits / len(relevant) if relevant else None
    reciprocal_rank = next((1/i for i,d in enumerate(top,1) if d in relevant), 0.0)
    dcg = sum((2**relevance.get(doc,0)-1)/math.log2(i+1) for i,doc in enumerate(top,1))
    ideal = sorted(relevance.values(), reverse=True)[:k]
    idcg = sum((2**grade-1)/math.log2(i+1) for i,grade in enumerate(ideal,1))
    return {"precision_at_k": precision, "recall_at_k": recall,
            "reciprocal_rank_at_k": reciprocal_rank,
            "ndcg_at_k": dcg/idcg if idcg else None}


def self_test() -> None:
    m = metrics(["A","X","Y"], {"A":1,"B":1}, 3)
    assert m["precision_at_k"] == 1/3 and m["recall_at_k"] == 1/2
    assert metrics(["B","A"], {"A":1,"B":2},2)["ndcg_at_k"] == 1
    assert rrf([["A","A"],["B"]],0) == [("A",1.0),("B",1.0)]
    assert metrics([], {}, 3)["recall_at_k"] is None


def run_demo() -> dict:
    return {"性质":"人工相关性标签，非真实搜索基准",
            "融合":rrf([["A","B","C"],["B","D","A"]]),
            "缺少必要证据B":metrics(["A","X","Y"],{"A":1,"B":1},3),
            "说明":"单查询倒数排名；MRR需要在多个查询上取平均"}


if __name__ == "__main__":
    import json
    self_test()
    print(json.dumps(run_demo(), ensure_ascii=False, indent=2))
