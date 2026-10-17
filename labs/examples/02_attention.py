"""小矩阵注意力、稳定 softmax 与因果掩码；所有数据为人工构造。"""
import math


def softmax(values: list[float], temperature: float = 1.0) -> list[float]:
    if not values or not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("需要非空分数和正有限温度")
    if any(math.isnan(x) or x == math.inf for x in values):
        raise ValueError("分数不可含 NaN 或正无穷")
    m = max(values)
    if m == -math.inf:
        raise ValueError("不能屏蔽全部候选")
    exps = [math.exp((x - m) / temperature) for x in values]
    total = sum(exps)
    return [x / total for x in exps]


def validate_matrix(a: list[list[float]], name: str) -> tuple[int, int]:
    if not a or not a[0] or any(len(row) != len(a[0]) for row in a):
        raise ValueError(f"{name} 必须是非空矩形矩阵")
    if any(not math.isfinite(x) for row in a for x in row):
        raise ValueError(f"{name} 必须全部有限")
    return len(a), len(a[0])


def attention(q, k, v, causal: bool = True):
    nq, dq = validate_matrix(q, "Q")
    nk, dk = validate_matrix(k, "K")
    nv, dv = validate_matrix(v, "V")
    if dq != dk or nk != nv or (causal and nq != nk):
        raise ValueError("维度不匹配；本演示因果模式要求相同序列长度")
    all_weights, outputs = [], []
    for i, query in enumerate(q):
        scores = [sum(a * b for a, b in zip(query, key)) / math.sqrt(dk) for key in k]
        if causal:
            scores = [s if j <= i else -math.inf for j, s in enumerate(scores)]
        weights = softmax(scores)
        all_weights.append(weights)
        outputs.append([sum(weights[j] * v[j][d] for j in range(nk)) for d in range(dv)])
    return all_weights, outputs


def self_test() -> None:
    assert abs(sum(softmax([1000, 1001, 1002])) - 1) < 1e-12
    q = k = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    v1, v2 = [[10.0], [20.0], [30.0]], [[10.0], [20.0], [9999.0]]
    w, a = attention(q, k, v1)
    _, b = attention(q, k, v2)
    assert a[:2] == b[:2], "未来 Value 不应影响前两个位置"
    assert w[0][1:] == [0.0, 0.0]
    assert w[1][2] == 0.0
    assert a[2] != b[2]


def run_demo() -> dict:
    q = k = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    weights, output = attention(q, k, [[10.0], [20.0], [30.0]])
    p = softmax([0, 1, 2])
    return {"性质": "原创小矩阵，无训练模型", "softmax_0_1_2": p,
            "加权10_20_30": sum(a*b for a,b in zip(p,[10,20,30])),
            "因果权重": weights, "输出": output}


if __name__ == "__main__":
    import json
    self_test()
    print(json.dumps(run_demo(), ensure_ascii=False, indent=2))
