"""The exact shared business3 corpus; no supervisor, worker, or GUI is started."""

import copy
import hashlib
import json

import pytest
from test_job_store import CONTRACT

ROOT = CONTRACT.ROOT
PROFILE = json.loads((ROOT / "fixtures.json").read_text())["business3"]
REGRESSIONS = json.loads((ROOT / "binding-regressions.json").read_text())["business3"]
ACTUAL_HASH = hashlib.sha256((ROOT / "registry.json").read_bytes()).hexdigest()


def test_same_build_registry_and_default_v2_remains_strict():
    assert PROFILE["registryHash"] == ACTUAL_HASH
    assert PROFILE["profile"] == "validator-only-runtime-disabled"
    for c in PROFILE["cases"]:
        if c["valid"] and c["value"].get("protocolVersion") == 3:
            assert not CONTRACT.validate("envelope", c["value"])
    assert not CONTRACT.validate_business3("not-registered", {})
    assert not CONTRACT.matches_business3_response(None, {}, ACTUAL_HASH)
    assert CONTRACT.business3_hello_outcome({}, None, ACTUAL_HASH) == "invalid-close"


@pytest.mark.parametrize("case", PROFILE["cases"], ids=lambda c: c["name"])
def test_shared_business3_schema(case):
    assert CONTRACT.validate_business3(case["schema"], case["value"]) is case["valid"]


@pytest.mark.parametrize("case", PROFILE["hello"], ids=lambda c: c["name"])
def test_shared_business3_hello(case):
    before = copy.deepcopy(case)
    assert (
        CONTRACT.business3_hello_outcome(case["request"], case["response"], ACTUAL_HASH)
        == case["outcome"]
    )
    assert case == before


@pytest.mark.parametrize("case", PROFILE["responses"], ids=lambda c: c["name"])
def test_shared_business3_response(case):
    before = copy.deepcopy(case)
    assert (
        CONTRACT.matches_business3_response(case["request"], case["response"], ACTUAL_HASH)
        is case["valid"]
    )
    assert case == before


@pytest.mark.parametrize("case", PROFILE["routing"] + REGRESSIONS, ids=lambda c: c["name"])
def test_shared_business3_event_binding(case):
    assert CONTRACT.accepts_business3_job_event(case["value"], case["binding"]) is case["valid"]
