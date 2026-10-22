"""Verify MCP snapshots, never parse .pen; run from any working directory."""

import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def read(name):
    return json.loads((BASE / name).read_text())


def shells(data):
    found = []

    def walk(node, root):
        if node.get("type") == "ref" and node.get("ref") == "aLI9i":
            found.append((root, node))
        for child in node.get("children", []):
            walk(child, root)

    for root in data["roots"]:
        walk(root, root)
    return found


def diff(a, b, path=()):
    if a == b:
        return []
    if isinstance(a, dict) and isinstance(b, dict):
        result = []
        for key in sorted(a.keys() | b.keys()):
            result += diff(a.get(key), b.get(key), (*path, key))
        return result
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        result = []
        for i, (left, right) in enumerate(zip(a, b, strict=True)):
            result += diff(left, right, (*path, i))
        return result
    return [{"path": list(path), "before": a, "after": b}]


before, after = read("before-mcp.json"), read("after-mcp.json")
rb, ra = read("before-resolved.json"), read("after-resolved.json")
assert len(before["roots"]) == len(after["roots"]) == 56
assert [n["id"] for n in before["roots"]] == [n["id"] for n in after["roots"]]
assert before["variables"] == after["variables"]
for left, right in zip(before["roots"], after["roots"], strict=True):
    if left["id"] not in {"aLI9i", "Ldm3V", "aoPaR", "k92hzW", "qvmsV", "Pfija"}:
        assert left == right, left["id"]
assert all(before["roots"][i] == after["roots"][i] for i in range(9))

changes = diff(before, after)
assert len(changes) == 14, changes
bt, at = ({n["id"]: n for n in data["texts"]} for data in (rb, ra))
assert len(bt) == len(at) == 2676
assert bt.keys() == at.keys()
all_shells = shells(after)
assert len(all_shells) == 32
expected_changes = {
    "dXifi",
    "SvPUC/lNRb1",
    "VVbfi/FUiuL",
    "bybVu/P5Dnb",
    "bhL4U/LYJoZ",
    "cAPJs/Ctyro",
    "cAPJs/bhL4U/LYJoZ",
    "RwYOd/SvPUC/lNRb1",
    "TZKCb",
    "UF2ck",
}
expected_changes |= {node["id"] + "/dXifi" for _, node in all_shells}
actual_changes = {key for key in bt if bt[key] != at[key]}
assert actual_changes == expected_changes
assert len(actual_changes) == 42
for left, right in zip(shells(before), all_shells, strict=True):
    assert left[1]["id"] == right[1]["id"]
    assert left[1]["descendants"]["bhL4U"] == right[1]["descendants"]["bhL4U"]

rows = []
for root, node in all_shells:
    shell_id = node["id"]

    def text(path, prefix=shell_id):
        return at[prefix + "/" + path]["content"]

    mode = text("VVbfi/FUiuL")
    assert mode == ("项目模式" if root["id"] in {"lEAnC", "aoPaR"} else "导师模式")
    save = text("SvPUC/lNRb1")
    assert save == ("查询待保存" if root["id"] == "Pfija" else "已自动保存")
    action = text("bhL4U/LYJoZ")
    state = text("bybVu/P5Dnb")
    assert action and action != "主动作" and state != "状态"
    assert "原型设计态" in text("dXifi")
    rows.append(
        {
            "screen": root["name"],
            "screenId": root["id"],
            "shellId": shell_id,
            "save": save,
            "mode": mode,
            "state": state,
            "action": action,
            "bottomEnabled": node["descendants"]["bhL4U"]["enabled"],
        }
    )
assert sum(row["bottomEnabled"] for row in rows) == 25
assert sum(row["mode"] == "项目模式" for row in rows) == 2
assert at["cAPJs/bhL4U/LYJoZ"]["content"] == "从快照新建运行"
assert at["AqSZB/bhL4U/LYJoZ"]["content"] == "预览映射"
assert at["nsAvO/bhL4U/LYJoZ"]["content"] == "执行查询"
assert at["pZNzK/bhL4U/LYJoZ"]["content"] == "运行检查"
assert at["i9iso/bhL4U/LYJoZ"]["content"] == "比较场景"
for node_id in ("TZKCb", "UF2ck"):
    assert "原型设计态" in at[node_id]["content"]
prior_problems = {json.dumps(n, sort_keys=True) for n in rb["problems"]}
new_problems = [n for n in ra["problems"] if json.dumps(n, sort_keys=True) not in prior_problems]
assert not new_problems, new_problems
for row in rows:
    assert (BASE / "screens" / (row["screenId"] + ".png")).is_file()

with (BASE / "screen-matrix.csv").open(encoding="utf-8-sig", newline="") as stream:
    saved_rows = list(csv.DictReader(stream))
assert saved_rows == [{k: str(v) for k, v in row.items()} for row in rows]
assert read("structural-diff.json") == changes
text_diff = [
    {"id": key, "before": bt[key]["content"], "after": at[key]["content"]}
    for key in sorted(actual_changes)
]
assert read("resolved-text-diff.json") == text_diff
summary = {
    "topLevelNodes": 56,
    "appShellInstances": 32,
    "resolvedTextNodes": 2676,
    "structuralChanges": len(changes),
    "resolvedTextChanges": len(actual_changes),
    "tutorMode": 30,
    "projectMode": 2,
    "enabledBottomActions": 25,
    "disabledBottomActions": 7,
    "baselineLayoutWarnings": len(rb["problems"]),
    "finalLayoutWarnings": len(ra["problems"]),
    "newLayoutWarnings": len(new_problems),
    "scope": "prototype content and targeted layout; not runtime business acceptance",
}
assert read("summary.json") == summary
print(json.dumps(summary, ensure_ascii=False))
