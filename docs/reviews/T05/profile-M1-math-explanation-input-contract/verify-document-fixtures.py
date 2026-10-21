"""Read-only document/JSON/hash checks; never import or execute product code."""

from pathlib import Path
from fractions import Fraction
from math import gcd
import ast
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).parent


def read(name):
    return json.loads((HERE / name).read_text())


checked = []
for path in HERE.glob("*.json"):
    if path.name == "static-check.json":
        continue
    json.loads(path.read_text())
    checked.append(path.name)
for path in HERE.glob("*.py"):
    ast.parse(path.read_text())

fixed = read("fixed-inputs.json")
for row in fixed["inputs"]:
    raw = (Path(row["tree"]) / row["path"]).read_bytes()
    assert len(raw) == row["bytes"]
    assert hashlib.sha256(raw).hexdigest() == row["sha256"], row["path"]
    if row.get("ref"):
        assert subprocess.check_output(
            ["git", "show", row["ref"] + ":" + row["path"]], cwd=row["tree"]
        ) == raw

matrix = read("domain-operator-goldens.json")
assert len(matrix["nineDomainCells"]) == 486
assert len({r["id"] for r in matrix["nineDomainCells"]}) == 486
assert len(matrix["numericPairRelationCells"]) == 648
assert len({r["id"] for r in matrix["numericPairRelationCells"]}) == 648
math_inputs = read("math-operand-inputs.json")
assert len(math_inputs["domainComparisonCases"]) == 486
assert len(math_inputs["numericComparisonCases"]) == 648
assert len(math_inputs["numberDecodeCases"]) == 38
assert len(math_inputs["calendarDecodeCases"]) == 15
assert len(math_inputs["mixedNumericComparisonCases"]) == 30
assert len(math_inputs["signedZeroComparisonCases"]) == 24
for family, rows in math_inputs.items():
    if not isinstance(rows, list):
        continue
    assert len({row["id"] for row in rows}) == len(rows)
    for row in rows:
        assert not {"expected", "expectedBoolean", "Number", "Calendar", "reason"}.intersection(row)


def rational(n):
    a, b = int(n["numerator"]), int(n["denominator"])
    assert b > 0 and gcd(a, b) == 1
    assert type(n["negative_zero"]) is bool
    assert not n["negative_zero"] or a == 0
    return Fraction(a, b)


numeric = read("number-goldens.json")
for row in numeric["vectors"]:
    # Stdlib Fraction only validates authored literal expansion, not rounding.
    assert Fraction(row["input"]["lexical_form"]) == rational(row["exactDecimalInput"])
    if "Number" in row["expected"]:
        rational(row["expected"]["Number"])
calendar = read("calendar-goldens.json")
assert len(calendar["vectors"]) == 15
for row in calendar["vectors"]:
    value = row["expectedCalendar"]
    assert 0 <= rational(value["second"]) < 86400
    assert row["expectedDomain"] == (
        ("T" if value["is_datetime"] else "D") + ("z" if value["explicit_offset"] else "l")
    )

graph = read("supplemental-graph-inputs.json")
assert len(graph["cases"]) == 5
assert all("catalogExpectedFromActualOntology" not in row for row in graph["cases"])
cinputs = read("consumer-C-inputs.json")
cgold = read("consumer-C-goldens.json")
assert {r["id"] for r in cinputs["cases"]} == {r["id"] for r in cgold["cases"]}
assert len(cinputs["cases"]) == 13
for row in cinputs["cases"]:
    if "shapesTurtle" in row:
        assert "sh:targetNode" not in row["shapesTurtle"]
        assert "sh:targetClass ex:Focus" in row["shapesTurtle"]
        assert "sh:property ex:shape" in row["shapesTurtle"]
        assert "ex:s a ex:Focus" in row["dataTurtle"]

windows = read("source-supply-and-windows.json")
assert len(windows["missingOriginalContexts"]) == 5
assert [r["matchId"] for r in windows["missingActualEventMatches"]] == [f"e{i:03}" for i in range(1, 17)]
assert len(read("original-source-gaps.json")["failedOrNotExecuted"]) == 5
for row in windows["futurePathWindows"]:
    if row.get("absentAtBase"):
        assert not (ROOT / row["path"]).exists()
    assert row["authorizedByThisDocument"] is False

print(json.dumps({
    "status": "pass: documentation static checks only",
    "jsonFiles": len(checked), "fixedInputs": len(fixed["inputs"]),
    "nineDomainSlots": 486, "numericRelationInstances": 648,
    "numberVectors": len(numeric["vectors"]), "calendarVectors": 15,
    "supplementalGraphInputs": 5, "consumerCCases": 13,
    "mathInputCases": sum(len(v) for v in math_inputs.values() if isinstance(v, list)),
    "originalContextGaps": 5, "missingEventMatches": 16,
    "notRun": "product imports/parsers/comparators/reasoning/tests/Validator/worker/Store/GUI/build/network-model",
    "scope": "JSON/AST/counts/canonical rationals/stdlib decimal expansion/input hashes and supported fixture shape structure; no product pass counts or rounding implementation test"
}, ensure_ascii=False, indent=2))
