"""Cross-language I03 design corpus and S1 boundary regression; no GUI or worker."""

import importlib.util
import json
from pathlib import Path

import pytest
from ontolearn_engine.storage import Store

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "contract_v2", ROOT / "packages/contracts/python/contract_v2.py"
)
CONTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACT)
FIXTURES = json.loads((ROOT / "packages/contracts/v2/fixtures.json").read_text(encoding="utf-8"))
IMPL = {
    "executionSemanticsVersion": "test-v1",
    "engineVersion": "0.1.0",
    "dependencyLockHash": "test-lock",
}


@pytest.mark.parametrize("case", FIXTURES["cases"], ids=lambda c: c["name"])
def test_shared_schema(case):
    assert CONTRACT.validate(case["schema"], case["value"]) is case["valid"]


@pytest.mark.parametrize("case", FIXTURES["routing"], ids=lambda c: c["name"])
def test_shared_route(case):
    assert CONTRACT.accepts_job_event(case["value"], case["binding"]) is case["valid"]


@pytest.mark.parametrize("case", FIXTURES["cursors"], ids=lambda c: c["name"])
def test_shared_cursor(case):
    assert CONTRACT.cursor_matches(case["record"], case["request"], case["nowMs"]) is case["valid"]


def test_full_transition_matrix():
    states = ["queued", "running", "cancelling", "succeeded", "failed", "cancelled"]
    allowed = {
        "queued>running",
        "queued>cancelled",
        "queued>failed",
        "running>cancelling",
        "running>succeeded",
        "running>failed",
        "cancelling>cancelled",
        "cancelling>failed",
        "cancelling>succeeded",
    }
    for before in states:
        for after in states:
            assert CONTRACT.permits_transition(before, after, 1, 2, True) is (
                before + ">" + after in allowed
            )
    assert not CONTRACT.permits_transition("cancelling", "succeeded", 1, 2, False)
    assert not CONTRACT.permits_transition("running", "failed", 2, 2, True)


def test_request_response_binding():
    cases = {c["name"]: c["value"] for c in FIXTURES["cases"]}
    q, r = cases["request job.get"], cases["response job.get"]
    assert CONTRACT.matches_response(q, r)
    assert not CONTRACT.matches_response(q, {**r, "id": "00000000-0000-4000-8000-000000000099"})
    assert CONTRACT.matches_response(cases["request hello"], cases["response hello"])
    old = {
        **cases["request hello"],
        "params": {**cases["request hello"]["params"], "supportedVersions": [1]},
    }
    assert not CONTRACT.matches_response(old, cases["response hello"])


def test_dependency_sets_and_reference_closure():
    definitions = [
        {"family": "ontology", "id": "O1", "version": 1, "references": []},
        {"family": "mapping", "id": "M1", "version": 1, "references": []},
        {"family": "query", "id": "Q1", "version": 1, "references": []},
        {"family": "rule", "id": "R1", "version": 1, "references": ["ontology:O1"]},
        {"family": "model", "id": "unused", "version": 1, "references": []},
    ]
    assert CONTRACT.derive_dependencies("query.execute", "Q1", "asserted", definitions) == {
        "keys": ["facts:asserted", "mapping:M1", "ontology:O1", "query:Q1"],
        "sets": {"ontology": ["ontology:O1"], "mapping": ["mapping:M1"]},
    }
    assert CONTRACT.derive_dependencies("query.execute", "Q1", "asserted+derived", definitions)[
        "keys"
    ] == [
        "facts:asserted",
        "mapping:M1",
        "ontology:O1",
        "query:Q1",
        "rule:R1",
    ]
    with pytest.raises(ValueError, match="INVALID_REQUEST"):
        CONTRACT.derive_dependencies("query.execute", "missing", "asserted", definitions)


@pytest.mark.parametrize("kind", [None, "", "   ", 1, False, [], {}])
def test_invalid_result_kind_has_zero_writes(tmp_path, kind):
    with_store = Store(tmp_path / "kind.db")
    try:
        with_store.create_project("p")
        snapshot = with_store.snapshot("p")
        before = list(with_store._db.iterdump())
        with pytest.raises(ValueError, match="kind"):
            with_store.publish("p", snapshot, ["facts:asserted"], kind, [], IMPL)
        with pytest.raises(ValueError, match="kind"):
            with_store.current("p", kind, IMPL)
        assert list(with_store._db.iterdump()) == before
        first = with_store.publish("p", snapshot, ["facts:asserted"], "query", ["first"], IMPL)
        second = with_store.publish("p", snapshot, ["facts:asserted"], "query", ["second"], IMPL)
        assert first != second
        assert with_store.current("p", "query", IMPL)["id"] == second
        assert with_store._db.execute("SELECT count(*) FROM current_results").fetchone()[0] == 1
    finally:
        with_store.close()


@pytest.mark.parametrize("implementation", [None, [], 1, False, {}, {"engineVersion": "x"}])
def test_current_invalid_provenance_is_shape_error_not_absence(tmp_path, implementation):
    store = Store(tmp_path / "current.db")
    try:
        store.create_project("p")
        before = list(store._db.iterdump())
        with pytest.raises(ValueError, match="provenance"):
            store.current("p", "query", implementation)
        assert list(store._db.iterdump()) == before
        assert store.current("p", "query", IMPL) is None
    finally:
        store.close()


@pytest.mark.parametrize("config", [None, [], 42, "legacy", False])
def test_legacy_nonobject_config_round_is_safe_shape_error_zero_side_effects(tmp_path, config):
    store = Store(tmp_path / "legacy.db")
    try:
        store.create_project("p")
        run = store.start_run("p", store.snapshot("p"), {"maxRounds": 4}, IMPL)
        # Simulate an imported legacy row before its immutable triggers existed.
        store._db.execute("DROP TRIGGER immutable_runs_update")
        store._db.execute("UPDATE runs SET config=? WHERE id=?", (json.dumps(config), run))
        before = list(store._db.iterdump())
        with pytest.raises(ValueError, match="config"):
            store.commit_round(run, 1, {}, "op", "job")
        assert list(store._db.iterdump()) == before
        assert store.progress(run) is None
        assert store.history(run)["replayable"] is False
    finally:
        store.close()


@pytest.mark.parametrize("case", FIXTURES["responses"], ids=lambda c: c["name"])
def test_shared_response_binding(case):
    assert CONTRACT.matches_response(case["request"], case["response"]) is case["valid"]


@pytest.mark.parametrize("case", FIXTURES["jobListCursors"], ids=lambda c: c["name"])
def test_shared_job_list_cursor(case):
    assert (
        CONTRACT.job_list_cursor_matches(case["record"], case["request"], case["nowMs"])
        is case["valid"]
    )


def test_numeric_json_equality_does_not_reject_integral_float():
    value = next(c["value"] for c in FIXTURES["cases"] if c["name"] == "request health")
    assert CONTRACT.validate("envelope", {**value, "protocolVersion": 2.0})


def test_frozen_input_hashes_are_self_contained():
    import hashlib

    folder = ROOT / "docs/reviews/I03/inputs"
    manifest = json.loads((folder / "sources.json").read_text(encoding="utf-8"))
    for entry in manifest:
        assert hashlib.sha256((folder / entry["copy"]).read_bytes()).hexdigest() == entry["sha256"]


@pytest.mark.parametrize("table", ["results", "current_results"])
def test_existing_null_kind_is_rejected_without_silent_cleanup(tmp_path, table):
    import sqlite3

    path = tmp_path / "old-null.db"
    store = Store(path)
    store.create_project("p")
    snapshot = store.snapshot("p")
    result = store.publish("p", snapshot, ["facts:asserted"], "query", [], IMPL)
    if table == "results":
        store._db.execute("UPDATE results SET kind=NULL WHERE id=?", (result,))
    else:
        store._db.execute("INSERT INTO current_results VALUES(?,?,?,?)", ("p", None, "{}", result))
    before = list(store._db.iterdump())
    store.close()
    with pytest.raises(ValueError, match="legacy result kind"):
        Store(path)
    raw = sqlite3.connect(path)
    try:
        assert list(raw.iterdump()) == before
    finally:
        raw.close()


@pytest.mark.parametrize("case", FIXTURES["unicodeMutations"], ids=lambda c: c["name"])
def test_shared_invalid_unicode(case):
    assert CONTRACT.validate(case["schema"], chr(case["codeUnit"])) is case["valid"]


@pytest.mark.parametrize("case", FIXTURES["transitions"], ids=lambda c: c["name"])
def test_shared_numeric_transitions(case):
    assert (
        CONTRACT.permits_transition(
            case["from"],
            case["to"],
            float(case["beforeVersion"]),
            float(case["afterVersion"]),
            case["finalBeforeCancel"],
        )
        is case["valid"]
    )


@pytest.mark.parametrize("case", FIXTURES["dependencyChains"], ids=lambda c: c["name"])
def test_shared_long_dependency_chains(case):
    definitions = [
        {
            "family": "query",
            "id": f"Q{i}",
            "version": 1,
            "references": [f"query:Q{i + 1}"] if i + 1 < case["length"] else [],
        }
        for i in range(case["length"])
    ]
    if case["valid"]:
        assert CONTRACT.derive_dependencies("query.execute", "Q0", "asserted", definitions)[
            "keys"
        ] == sorted(["facts:asserted"] + [f"query:Q{i}" for i in range(case["length"])])
    else:
        with pytest.raises(ValueError, match="INVALID_REQUEST"):
            CONTRACT.derive_dependencies("query.execute", "Q0", "asserted", definitions)


@pytest.mark.parametrize("case", FIXTURES["validationBindings"], ids=lambda c: c["name"])
def test_shared_validation_projection_resources(case):
    assert (
        CONTRACT.validation_projection_matches_resources(case["projection"], case["resources"])
        is case["valid"]
    )


def test_semantic_error_category_descriptions_are_complete():
    errors = json.loads((ROOT / "packages/contracts/v2/errors.json").read_text(encoding="utf-8"))
    for code, parameter in [("UNSUPPORTED_CONSTRUCT", "construct"), ("RESOURCE_LIMIT", "resource")]:
        assert (
            list(errors["parameterMeanings"][code])
            == errors["codes"][code]["paramsSchema"]["properties"][parameter]["enum"]
        )


def test_i05_handoff_source_hash_is_preserved():
    import hashlib

    handoff = ROOT / "docs/reviews/I03/handoffs/I05-contract-source.json"
    record = json.loads(handoff.read_text(encoding="utf-8"))
    for snapshot in (record, record["typedReasonsV3"]):
        assert (
            hashlib.sha256((ROOT / snapshot["copy"]).read_bytes()).hexdigest() == snapshot["sha256"]
        )
