"""R2-F1: only trusted binding mutations; public notification is unchanged."""

import json
from pathlib import Path

import pytest
from ontolearn_engine.resources import CONTRACT

CASES = json.loads((Path(CONTRACT.ROOT) / "binding-regressions.json").read_text(encoding="utf-8"))[
    "cases"
]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["name"])
def test_trusted_binding_safe_rejection(case):
    assert CONTRACT.accepts_job_event(case["value"], case["binding"]) is case["valid"]
