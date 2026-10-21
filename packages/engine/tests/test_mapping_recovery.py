"""Real parsed mapping cancellation/crash boundaries on the approved Store API.

These are private service/storage evidence, not the unavailable public job/UI flow.
"""

import asyncio
import hashlib
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import pytest
from ontolearn_engine.mapping.plan import Binding, Mapping, checked_plan, preview
from ontolearn_engine.mapping.source import parse_csv
from ontolearn_engine.storage import Store

SOURCE = Path(__file__).resolve().parents[3] / "tests/fixtures/mapping/equipment.csv"
SPEC = Mapping(
    "equipment-map",
    1,
    "urn:example:equipment/",
    "urn:example:Equipment",
    ("equipment_id",),
    (Binding("equipment_name", "urn:example:name"),),
)
CHANGED = "equipment_id,equipment_name\n001,更新名称\n".encode()

EXPECTED_CHANGED_FACTS = {
    (
        "urn:example:equipment/001",
        "urn:example:name",
        '"更新名称"',
        "equipment-map",
        '{"sheet":"CSV","row":2}',
        '"更新名称"',
    ),
    (
        "urn:example:equipment/001",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
        "<urn:example:Equipment>",
        "equipment-map",
        '{"sheet":"CSV","row":2}',
        "<urn:example:Equipment>",
    ),
}


def assert_changed_metadata(state):
    assert {
        (f["subject"], f["predicate"], f["object"], f["owner"], f["source_row"], f["managed_value"])
        for f in state["facts"]
    } == EXPECTED_CHANGED_FACTS
    assert [
        {"layer": d["layer"], "id": d["id"], "value": json.loads(d["payload"])}
        for d in state["definitions"]
    ] == [
        {
            "layer": "mapping",
            "id": "equipment-map",
            "value": {
                "version": 1,
                "definition": json.loads(json.dumps(asdict(SPEC))),
                "sourceHash": hashlib.sha256(CHANGED).hexdigest(),
                "sheet": "CSV",
            },
        }
    ]
    assert state["mappingState"] == {"equipment-map": {"generatedVersion": 2, "stale": []}}


def prepare(store, data):
    snapshot = store.load_snapshot(store.snapshot("P"))
    table = parse_csv(data)
    return checked_plan(preview(SPEC, table, snapshot), SPEC, table, snapshot)


def baseline(path):
    store = Store(path)
    store.create_project("P")
    store.commit("P", operation="initial", job="initial-job", **prepare(store, SOURCE.read_bytes()))
    return store


@pytest.mark.parametrize(
    "stage", ["before", "mid_data", "mid_invalidation", "mid_marker", "before_commit"]
)
def test_cancel_before_commit_preserves_last_committed_mapping(tmp_path, stage):
    store = baseline(tmp_path / "cancel.sqlite")
    try:
        before = store.state("P")
        revision = store.revision("P")
        plan = prepare(store, CHANGED)

        def cancel(current):
            if current == stage:
                raise asyncio.CancelledError()

        with pytest.raises(asyncio.CancelledError):
            store.commit("P", operation="cancelled", job="cancel-job", hook=cancel, **plan)
        assert store.revision("P") == revision
        assert store.state("P") == before
        assert store.marker("P", "cancelled") is None
        assert store.marker("P", "initial") is not None
    finally:
        store.close()


def test_cancel_after_commit_is_reconciled_from_marker_and_not_reported_as_zero_commit(tmp_path):
    store = baseline(tmp_path / "late-cancel.sqlite")
    try:
        revision = store.revision("P")
        initial_marker = store.marker("P", "initial")
        initial_history = store.load_snapshot(initial_marker["after_snapshot"])
        plan = prepare(store, CHANGED)

        def cancel(stage):
            if stage == "after_commit":
                raise asyncio.CancelledError()

        with pytest.raises(asyncio.CancelledError):
            store.commit("P", operation="committed", job="late-cancel-job", hook=cancel, **plan)
        marker = store.marker("P", "committed")
        assert marker is not None
        assert store.revision("P") == revision + 1
        assert store.load_snapshot(marker["after_snapshot"])["state"] == store.state("P")
        assert store.load_snapshot(initial_marker["after_snapshot"]) == initial_history
        assert_changed_metadata(store.state("P"))
    finally:
        store.close()


CHILD = """
import os, sys
from pathlib import Path
from dataclasses import asdict
from ontolearn_engine.mapping.plan import Binding, Mapping, checked_plan, preview
from ontolearn_engine.mapping.source import parse_csv
from ontolearn_engine.storage import Store
store = Store(sys.argv[1])
spec = Mapping('equipment-map', 1, 'urn:example:equipment/', 'urn:example:Equipment',
               ('equipment_id',), (Binding('equipment_name', 'urn:example:name'),))
table = parse_csv(Path(sys.argv[2]).read_bytes())
snapshot = store.load_snapshot(store.snapshot('P'))
plan = checked_plan(preview(spec, table, snapshot), spec, table, snapshot)
def crash(stage):
    if stage == sys.argv[3]:
        os._exit(71)
store.commit('P', operation='crash-boundary', job='crash-job', hook=crash, **plan)
raise SystemExit('crash hook did not execute')
"""


@pytest.mark.parametrize(
    ("stage", "committed"),
    [("mid_invalidation", False), ("before_commit", False), ("after_commit", True)],
)
def test_actual_process_exit_reopens_only_explicit_committed_state(tmp_path, stage, committed):
    database = tmp_path / "crash.sqlite"
    source = tmp_path / "changed.csv"
    source.write_bytes(CHANGED)
    store = baseline(database)
    before = store.state("P")
    initial_marker = store.marker("P", "initial")
    initial_history = store.load_snapshot(initial_marker["after_snapshot"])
    revision = store.revision("P")
    store.close()
    result = subprocess.run(
        [sys.executable, "-c", CHILD, str(database), str(source), stage],
        capture_output=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 71, result.stderr.decode(errors="replace")
    reopened = Store(database)
    try:
        marker = reopened.marker("P", "crash-boundary")
        assert (marker is not None) is committed
        assert reopened.revision("P") == revision + int(committed)
        assert reopened.marker("P", "initial") == initial_marker
        assert reopened.load_snapshot(initial_marker["after_snapshot"]) == initial_history
        if committed:
            assert reopened.state("P") == reopened.load_snapshot(marker["after_snapshot"])["state"]
            assert_changed_metadata(reopened.state("P"))
        else:
            assert reopened.state("P") == before
    finally:
        reopened.close()
