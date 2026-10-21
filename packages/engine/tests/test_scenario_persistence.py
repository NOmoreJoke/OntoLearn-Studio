"""Generated T07 records through approved Store, not a registered scenario adapter.

Inference/behavior remain synthetic. Only real SQLite transaction/isolation evidence
is claimed. All writes below are test wiring under temporary paths, never a second
product write route or a use of unapproved T01/I04 candidates.
"""

import json
import os
import sqlite3
import subprocess
import sys
from dataclasses import asdict, replace
from pathlib import Path

import pytest
from ontolearn_engine.scenario.runner import run
from ontolearn_engine.storage import Store, canonical, digest
from test_scenario_rounds import ProbePorts, definition

PHASES = ("before", "mid_data", "mid_marker", "before_commit", "after_commit")


def payload(record):
    return json.loads(canonical(asdict(record)))


def prepare(path, maximum=4):
    store = Store(path)
    store.create_project("project-1")
    subject, predicate, value = "urn:t07:formal-equipment", "urn:t07:name", '"正式数据哨兵"'
    store.commit(
        "project-1",
        0,
        "formal-seed",
        "formal-job",
        manual=[
            {
                "id": digest([subject, predicate, value]),
                "subject": subject,
                "predicate": predicate,
                "object": value,
            }
        ],
    )
    snapshot = store.snapshot("project-1")
    identity = store.start_run(
        "project-1",
        snapshot,
        {"maxRounds": maximum},
        {
            "engineVersion": "approved-store-test",
            "executionSemanticsVersion": "t07-test-only",
            "dependencyLockHash": "test-lock",
        },
    )
    return store, identity


class PersistentProbe(ProbePorts):
    """Test-only wiring. Reconcile the exact durable receipt before deciding effect."""

    def __init__(self, store, identity, *, phase=None, fault=None, fault_round=1):
        super().__init__()
        self.store, self.identity = store, identity
        self.phase, self.fault, self.fault_round = phase, fault, fault_round
        self.reconciled = []
        self.disk_errors = []

    def commit(self, record, check):
        self.enter("commit", check)
        number = record.checkpoint.round
        operation = f"t07-operation-{number}"
        state = payload(record)

        def hook(stage):
            if stage == self.phase and number == self.fault_round:
                if self.fault == "exit":
                    os._exit(92)
                if self.fault == "cancel":
                    self.stop = True
                    check()
                if self.fault == "disk":
                    # Real SQLite READONLY fault; source bytes are not modified.
                    self.store._db.execute("PRAGMA query_only=ON")
                    self.store._db.execute("UPDATE projects SET revision=revision")
                    raise AssertionError("Readonly injection failed")
                raise RuntimeError("acknowledgment fault")
            if stage != "after_commit":
                check()

        try:
            self.store.commit_round(self.identity, number, state, operation, "t07-job", hook)
        except Exception as error:
            if self.fault == "disk" and number == self.fault_round:
                self.disk_errors.append(
                    (
                        isinstance(error, sqlite3.OperationalError),
                        getattr(error, "sqlite_errorcode", None),
                        getattr(error, "sqlite_errorname", None),
                    )
                )
            # Query public immutable records; do not retry the write or infer no effect.
            history = self.store.history(self.identity)
            matches = [r for r in history["rounds"] if r["operation"] == operation]
            if (
                len(matches) != 1
                or matches[0]["number"] != number
                or matches[0]["job"] != "t07-job"
            ):
                raise
            saved = self.store.load_snapshot(matches[0]["snapshot"])
            if saved != {
                "project": "project-1",
                "run": self.identity,
                "round": number,
                "state": state,
            }:
                raise
            self.reconciled.append(number)
        finally:
            self.store._db.execute("PRAGMA query_only=OFF")
        self.saved.append(record)


@pytest.mark.parametrize("capacity", [3, 4])
def test_generated_e5_rounds_persist_exactly_and_never_modify_formal_project(tmp_path, capacity):
    path = tmp_path / "scenario.sqlite"
    store, identity = prepare(path)
    formal, revision = store.state("project-1"), store.revision("project-1")
    result = run(definition(capacity), PersistentProbe(store, identity))
    assert result.status == "succeeded"
    history = store.history(identity)
    snapshots = [r["snapshot"] for r in history["rounds"]]
    assert [r["number"] for r in history["rounds"]] == [1, 2, 3, 4]
    assert [store.load_snapshot(ref)["state"] for ref in snapshots] == [
        payload(record) for record in result.rounds
    ]
    store.finish_run(identity, "succeeded", {"testOnly": True})
    store.collect_cache()
    assert [store.load_snapshot(ref)["state"] for ref in snapshots] == [
        payload(record) for record in result.rounds
    ]
    assert store.state("project-1") == formal and store.revision("project-1") == revision
    store.close()
    reopened = Store(path)
    try:
        assert reopened.history(identity)["terminal"]["status"] == "succeeded"
        assert [reopened.load_snapshot(ref)["state"] for ref in snapshots] == [
            payload(record) for record in result.rounds
        ]
        assert reopened.state("project-1") == formal
    finally:
        reopened.close()


@pytest.mark.parametrize("previous", [0, 1])
@pytest.mark.parametrize("phase", PHASES)
@pytest.mark.parametrize("failure", ["exception", "cancel", "disk"])
def test_real_store_round_fault_boundaries_preserve_exact_effect(
    tmp_path, previous, phase, failure
):
    store, identity = prepare(tmp_path / "fault.sqlite", previous + 1)
    formal, revision = store.state("project-1"), store.revision("project-1")
    ports = PersistentProbe(store, identity, phase=phase, fault=failure, fault_round=previous + 1)
    result = run(
        replace(definition(), max_rounds=previous + 1), ports, cancelled=lambda: ports.stop
    )
    if failure == "disk":
        assert_readonly_fault(ports)
    committed = previous + (phase == "after_commit")
    assert result.checkpoint.round == committed
    assert result.status == (
        "cancelled" if failure == "cancel" else "succeeded" if phase == "after_commit" else "failed"
    )
    history = store.history(identity)
    assert len(history["rounds"]) == committed
    assert [store.load_snapshot(row["snapshot"])["state"] for row in history["rounds"]] == [
        payload(record) for record in result.rounds
    ]
    assert ports.reconciled == ([previous + 1] if phase == "after_commit" else [])
    if history["committedProgress"]:
        assert history["committedProgress"]["lastCommittedRound"] == result.checkpoint.round
    else:
        assert result.checkpoint.round == 0
    assert store.state("project-1") == formal and store.revision("project-1") == revision
    store.close()


@pytest.mark.parametrize("previous", [0, 1])
@pytest.mark.parametrize("phase", PHASES)
def test_real_process_exit_recovers_only_committed_generated_rounds(tmp_path, previous, phase):
    path = tmp_path / "crash.sqlite"
    store, identity = prepare(path, previous + 1)
    formal, revision = store.state("project-1"), store.revision("project-1")
    store.close()  # The subprocess is the only writer; reopen only after observed exit.
    script = """
import sys
from dataclasses import replace
sys.path.insert(0, sys.argv[1])
from test_scenario_persistence import Store, PersistentProbe, definition, run
store = Store(sys.argv[2])
previous = int(sys.argv[5])
ports = PersistentProbe(store, sys.argv[3], phase=sys.argv[4], fault='exit', fault_round=previous+1)
run(replace(definition(), max_rounds=previous+1), ports)
raise AssertionError('Crash phase not reached')
"""
    process = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            str(Path(__file__).parent),
            str(path),
            identity,
            phase,
            str(previous),
        ],
        capture_output=True,
        timeout=15,
    )
    assert process.returncode == 92 and process.stderr == b""
    reopened = Store(path)
    try:
        committed = previous + (phase == "after_commit")
        history = reopened.history(identity)
        expected = run(replace(definition(), max_rounds=previous + 1), ProbePorts())
        assert [r["number"] for r in history["rounds"]] == list(range(1, committed + 1))
        assert [reopened.load_snapshot(r["snapshot"])["state"] for r in history["rounds"]] == [
            payload(record) for record in expected.rounds[:committed]
        ]
        assert history["terminal"] is None  # A crash does not prove terminal success/cancel.
        assert reopened.state("project-1") == formal
        assert reopened.revision("project-1") == revision
    finally:
        reopened.close()


def assert_readonly_fault(ports):
    # This assertion lives outside runner's error boundary; a swallowed sentinel fails validation.
    assert ports.disk_errors == [(True, sqlite3.SQLITE_READONLY, "SQLITE_READONLY")]


def test_readonly_evidence_rejects_disabled_injection_negative_control(tmp_path):
    store, identity = prepare(tmp_path / "negative-control.sqlite", 1)
    connection = store._db

    class DisabledReadonly:
        def execute(self, sql, *args):
            if sql == "PRAGMA query_only=ON":
                sql = "PRAGMA query_only=OFF"
            return connection.execute(sql, *args)

        def __getattr__(self, name):
            return getattr(connection, name)

    store._db = DisabledReadonly()
    try:
        ports = PersistentProbe(store, identity, phase="mid_data", fault="disk")
        result = run(replace(definition(), max_rounds=1), ports)
        assert result.status == "failed"  # Alone this is too weak to prove READONLY.
        assert ports.disk_errors == [(False, None, None)]
        with pytest.raises(AssertionError):
            assert_readonly_fault(ports)
        assert store.history(identity)["rounds"] == []
    finally:
        store.close()


def test_owner_handoff_sample_matches_generated_full_round_and_pending_ranges():
    sample = json.loads(
        (
            Path(__file__).parents[3] / "tests/fixtures/scenario/round-projection-handoff.json"
        ).read_text()
    )
    d = definition()
    record = run(d, ProbePorts()).rounds[0]
    assert sample["internalRound"] == payload(record)
    proposal = sample["proposedCoordinatorState"]
    assert proposal["scenarioRound"] == sample["internalRound"]
    assert proposal["consumedEvents"] == list(record.checkpoint.consumed)
    assert proposal["inputEvents"] == [event.id for event in d.events]
    assert proposal["pendingEvents"] == [
        event.id for event in record.checkpoint.events if event.id not in record.checkpoint.consumed
    ]
    assert sample["acknowledgmentIdentityProposal"]["stateDigest"] == digest(proposal)
    assert sample["eventScopeExplanation"]["scheduledFutureEvents"] == proposal["pendingEvents"]
    assert sample["eventScopeExplanation"]["generatedPendingEvents"] == []
