from __future__ import annotations

import copy
import pathlib

import yaml

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"


def load_yaml(name: str) -> dict:
    path = DATA_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"数据文件不存在：{path}")
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_cases(name: str) -> list[dict]:
    cases = load_yaml(name).get("cases", [])
    if not cases:
        raise ValueError(f"{name}.yaml 没有 cases")
    ids = [c.get("id") for c in cases]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{name}.yaml 用例 id 重复：{ids}")
    for case in cases:
        if not case.get("id") or "expected" not in case:
            raise ValueError(f"用例缺少 id/expected：{case}")
    return cases


def get_path(obj, path: str):
    for key in path.split("."):
        obj = obj[key]
    return obj


def set_path(obj: dict, path: str, value) -> None:
    keys = path.split(".")
    target = obj
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = copy.deepcopy(value)


def del_path(obj: dict, path: str) -> None:
    keys = path.split(".")
    target = obj
    for key in keys[:-1]:
        target = target[key]
    target.pop(keys[-1], None)


def build_payload(base: dict, case: dict) -> dict:
    """模板 + 变更描述 → 该用例的请求体；永远 deepcopy，避免污染别的用例。"""
    payload = copy.deepcopy(base)
    for path in case.get("remove", []):
        del_path(payload, path)
    for path, value in (case.get("set") or {}).items():
        set_path(payload, path, value)
    return payload