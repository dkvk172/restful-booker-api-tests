"""按端点/marker 统计用例数，输出 Markdown。

用法（项目根目录）：
    python scripts/stats.py
    python scripts/stats.py --total-endpoints 8 --check
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "reports" / "stats.md"
UNLABELED = "未标注"


def _ini_markers(config) -> set[str]:
    """只取 pytest.ini 的 markers 块里声明的项目 marker 名。

    config.getini("markers") 是合并视图：你的 ini + pytest 内置
    （parametrize/skip/skipif/xfail/usefixtures/...）+ 已装插件
    （allure_*/xdist_group）都会混进来，而且内置项带函数签名。
    所以这里直接解析 ini 文件，而不是用它。
    """
    ini = config.inipath
    if ini is None:                      # 没有 ini 文件（如纯 pyproject.toml）时兜底
        return set()

    names: set[str] = set()
    in_block = False
    for raw in ini.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not in_block:
            # 找到 "markers = " 这一行，进入 markers 块
            if line.startswith("markers") and "=" in line:
                in_block = True
                inline = line.split("=", 1)[1].strip()   # 兼容 markers = smoke: xxx 单行写法
                if inline:
                    names.add(inline.split(":", 1)[0].strip())
            continue

        if not line or line.startswith("#"):
            continue
        if raw[:1] not in (" ", "\t"):   # 不再缩进，说明 markers 块结束
            break

        name = line.split(":", 1)[0].strip()   # "smoke: 核心链路冒烟" → "smoke"
        if name:
            names.add(name)

    return names

class Collector:
    """pytest 插件：收集阶段把每条 item 的 marker/参数 id 抓下来。"""

    def __init__(self) -> None:
        self.items: list[dict] = []
        self.business_markers: set[str] = set()


    def pytest_collection_modifyitems(self, config, items):
        # 只统计 pytest.ini 里声明的业务 marker；内置/插件 marker 不参与
        self.business_markers = _ini_markers(config) - {"endpoint"}

        for item in items:
            ep = item.get_closest_marker("endpoint")
            callspec = getattr(item, "callspec", None)
            self.items.append(
                {
                    "nodeid": item.nodeid,
                    "module": item.module.__name__ if hasattr(item, "module") else "",
                    "name": item.name,
                    "markers": sorted(
                        {m.name for m in item.iter_markers() if m.name in self.business_markers}
                    ),
                    "endpoint": ep.args[0] if ep and ep.args else UNLABELED,
                    "xfail": item.get_closest_marker("xfail") is not None,
                    "param_id": callspec.id if callspec else None,
                }
            )


def render(items: list[dict], markers: set[str], total_endpoints: int | None) -> str:
    endpoints = Counter(i["endpoint"] for i in items)
    xfails = Counter(i["endpoint"] for i in items if i["xfail"])
    covered = len([e for e in endpoints if e != UNLABELED])
    unlabeled = endpoints.get(UNLABELED, 0)

    lines = [
        "# 用例统计",
        "",
        f"- 收集时间：{datetime.now():%Y-%m-%d %H:%M}",
        f"- 用例总数：**{len(items)}**（其中 xfail {sum(xfails.values())}）",
        f"- 端点覆盖：**{covered}** 个"
        + (f" / {total_endpoints}（{covered / total_endpoints:.0%}）" if total_endpoints else ""),
        "",
        "## 按端点",
        "",
        "| 端点 | 用例数 | 其中 xfail |",
        "|---|---:|---:|",
    ]
    for ep, n in endpoints.most_common():
        lines.append(f"| {ep} | {n} | {xfails[ep]} |")

    lines += ["", "## 按 marker", "", "| marker | 用例数 |", "|---|---:|"]
    for name in sorted(markers):
        n = sum(1 for i in items if name in i["markers"])
        lines.append(f"| {name} | {n} |")

    if unlabeled:
        lines += ["", f"> ⚠️ {unlabeled} 条用例未标注 `@pytest.mark.endpoint`"]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="按端点/marker 统计 pytest 用例")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--total-endpoints", type=int, default=None, help="全部端点总数，用于算覆盖率（restful-booker 是 8）")
    parser.add_argument("--check", action="store_true", help="存在未标注用例时退出码 2，可当 CI 门禁")
    args = parser.parse_args(argv)

    os.chdir(ROOT)  # 保证 testpaths/conftest 解析正确，脚本可从任意目录调用
    collector = Collector()
    rc = pytest.main(
        # -o addopts= 跳过 ini 里的 -v/--html，统计不写报告、不需要服务
        ["-o", "addopts=", "--strict-markers", "--collect-only", "-q", "-p", "no:cacheprovider"],
        plugins=[collector],
    )
    if rc != 0:
        print(f"收集失败（pytest 退出码 {rc}）", file=sys.stderr)
        return 1

    text = render(collector.items, collector.business_markers, args.total_endpoints)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    print(f"\n已写入 {args.out}")

    if args.check and any(i["endpoint"] == UNLABELED for i in collector.items):
        print("检查失败：存在缺少 endpoint 标注的用例", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())