"""标准注意力 KV 缓存估算与前缀匹配；不是厂商计费器。"""
from typing import Sequence, TypeVar
T = TypeVar("T")


def kv_bytes(layers: int, batch: int, length: int, kv_heads: int,
             head_dim: int, bytes_per_element: int) -> int:
    args = [layers, batch, length, kv_heads, head_dim, bytes_per_element]
    if any(not isinstance(x, int) or isinstance(x, bool) or x <= 0 for x in args):
        raise ValueError("所有参数必须是正整数")
    return 2 * layers * batch * length * kv_heads * head_dim * bytes_per_element


def common_prefix(a: Sequence[T], b: Sequence[T]) -> int:
    count = 0
    for x, y in zip(a, b):
        if x != y:
            break
        count += 1
    return count


def self_test() -> None:
    assert kv_bytes(32, 1, 8192, 8, 128, 2) == 1024**3
    assert kv_bytes(32, 1, 8192, 32, 128, 2) == 4 * 1024**3
    assert common_prefix([1,2,3], [1,2,4]) == 2
    assert common_prefix([], [1]) == 0
    assert common_prefix([1,2], [9,1,2]) == 0


def run_demo() -> dict:
    base = ["规则", "工具", "任务A"]
    return {"性质": "简化公式，不含分配器和其他状态，不适用所有架构",
            "8个KV头_GiB": kv_bytes(32,1,8192,8,128,2)/1024**3,
            "32个KV头_GiB": kv_bytes(32,1,8192,32,128,2)/1024**3,
            "仅尾部变化_共同前缀项": common_prefix(base,["规则","工具","任务B"]),
            "首部插入变化_共同前缀项": common_prefix(base,["新时间","规则","工具","任务B"]),
            "限制": "共同前缀项不是实际缓存Token；产品还有阈值和其他条件"}


if __name__ == "__main__":
    import json
    self_test()
    print(json.dumps(run_demo(), ensure_ascii=False, indent=2))
