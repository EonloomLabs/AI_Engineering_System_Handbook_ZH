"""结构化命题保真检查。不是自然语言理解器，也不是 LLM 压缩实现。"""
from copy import deepcopy

CANONICAL = {
    "public_api": {"value":"unchanged", "certainty":"required", "version":"all"},
    "config_loaded": {"value":True, "certainty":"verified", "evidence":"T1"},
    "path_cause": {"value":"base_mismatch", "certainty":"hypothesis", "evidence":None},
    "patch": {"value":"not_applied", "certainty":"observed", "version":"v3"},
    "tests": {"value":"pending", "certainty":"observed", "version":"v3"},
}


def compare_claims(reference: dict, candidate: dict) -> dict:
    if not isinstance(reference,dict) or not isinstance(candidate,dict):
        raise TypeError("输入必须是结构化命题字典")
    missing = sorted(set(reference)-set(candidate))
    extra = sorted(set(candidate)-set(reference))
    changes=[]
    for key in sorted(set(reference)&set(candidate)):
        if not isinstance(reference[key],dict) or not isinstance(candidate[key],dict):
            raise TypeError("每条命题必须包含字段字典")
        for field in sorted(set(reference[key])|set(candidate[key])):
            if reference[key].get(field) != candidate[key].get(field):
                changes.append({"claim":key,"field":field,
                                "expected":reference[key].get(field),
                                "actual":candidate[key].get(field)})
    return {"preserved": not missing and not extra and not changes,
            "missing":missing,"extra":extra,"changed":changes}


def bad_summary() -> dict:
    wrong=deepcopy(CANONICAL)
    del wrong["public_api"]
    wrong["path_cause"]["certainty"]="verified"
    wrong["patch"]["value"]="applied"
    wrong["tests"]={"value":"passed","certainty":"observed","version":"v2"}
    return wrong


def self_test() -> None:
    assert compare_claims(CANONICAL,deepcopy(CANONICAL))["preserved"]
    result=compare_claims(CANONICAL,bad_summary())
    assert not result["preserved"]
    assert result["missing"] == ["public_api"]
    assert len(result["changed"]) == 4


def run_demo() -> dict:
    return {"性质":"人工标注命题上的确定性校验，不会自动判断自然语言",
            "基准":CANONICAL,"错误压缩":bad_summary(),
            "差异":compare_claims(CANONICAL,bad_summary()),
            "限制":"真实压缩仍需人工/模型抽取校准，以及继续执行任务的测试"}


if __name__ == "__main__":
    import json
    self_test()
    print(json.dumps(run_demo(),ensure_ascii=False,indent=2))
