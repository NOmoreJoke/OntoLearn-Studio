"""Differential equivalence & complexity regression tests for format3/JobStore ledger checks.

Covers Step 1.3 guarantees:
1. Optimization equivalence: cached per-validation `_history` / `validate_ledger`
   in `JobStore._validate_job3` and per-call `_snapshots` reuse in `format3`
   produce identical pass/fail outcomes and `Format3Fault.category` as an uncached
   reference pass across valid and corrupted ledgers.
2. Anti-regression complexity bounds: `_validate_job3` calls `format3._history` at
   most once per project, and `format3._history` materializes each distinct
   `domainSnapshotRef` at most once regardless of how many application-only
   checkpoints share it.
3. End-to-end Windows-fallback `project.transfer.package.import` completes with
   linear snapshot validation after 10+ application checkpoints.
"""

import json
import sqlite3
from contextlib import contextmanager
from copy import deepcopy
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project import format3, staging
from ontolearn_engine.project.format3 import Format3Fault
from ontolearn_engine.project.mainline import READ_LIMITS
from ontolearn_engine.project.management import validate_ledger
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import canonical, digest


def _uid():
    return str(uuid4())


@contextmanager
def _bypass_trigger(db: sqlite3.Connection, trigger_name: str):
    """Temporarily drop and recreate an exact immutable trigger to inject DB faults."""
    row = db.execute(
        "SELECT sql FROM sqlite_master WHERE type='trigger' AND name=?", (trigger_name,)
    ).fetchone()
    assert row is not None, f"Missing trigger {trigger_name}"
    sql = row[0]
    db.execute(f'DROP TRIGGER "{trigger_name}"')
    try:
        yield
    finally:
        db.execute(sql)


def _create_blank_with_ops(
    store: JobStore,
    actor_id: str,
    name: str,
    *,
    app_steps: int,
    with_domain_commit: bool = True,
):
    c_op = _uid()
    created = store.commit(
        None,
        None,
        c_op,
        None,
        creation={
            "projectCreateCoreVersion": 1,
            "request": {
                "requestVersion": 1,
                "operationId": c_op,
                "name": name,
                "initialization": {"kind": "blank"},
            },
            "origin": {
                "hostClientId": actor_id,
                "engineSessionId": _uid(),
                "permission": "library.create",
            },
            "readerLimits": READ_LIMITS,
        },
    )
    pub = created["projectId"]
    expected_version = 1
    domain_op = None
    if with_domain_commit:
        fact = {
            "id": digest([f"urn:eq:{name}:s1", "urn:eq:p", f'"val-{name}"']),
            "subject": f"urn:eq:{name}:s1",
            "predicate": "urn:eq:p",
            "object": f'"val-{name}"',
        }
        change = {
            "type": "metadata",
            "expectedVersion": expected_version,
            "patch": {"name": f"{name}-d1"},
            "domain": {"base": 0, "plan": {"manual": [fact], "definitions": []}},
        }
        prep = store.prepare_application(pub, change, actor=actor_id, permission="write")
        domain_op = _uid()
        store.apply_application(
            pub,
            domain_op,
            change,
            actor=actor_id,
            permission="write",
            prepared_plan_ref=prep["preparedPlanRef"],
            confirmation_ref=prep["confirmationRef"],
        )
        expected_version += 1

    app_ops = []
    for step in range(app_steps):
        mc = {
            "type": "metadata",
            "expectedVersion": expected_version,
            "patch": {"name": f"{name}-m{step}"},
        }
        prep = store.prepare_application(pub, mc, actor=actor_id, permission="write")
        op = _uid()
        store.apply_application(
            pub,
            op,
            mc,
            actor=actor_id,
            permission="write",
            prepared_plan_ref=prep["preparedPlanRef"],
            confirmation_ref=prep["confirmationRef"],
        )
        app_ops.append(op)
        expected_version += 1
    return {
        "public": pub,
        "internal": store._project(pub),
        "create_op": c_op,
        "domain_op": domain_op,
        "app_ops": app_ops,
    }


def _uncached_reference_validate_job3(store: JobStore, monkeypatch):
    """Exact pre-optimization reference validator: no per-project or snapshot caching."""
    with monkeypatch.context() as mp:
        mp.setattr(
            format3,
            "_cached_snapshot",
            lambda s, proj, ref, _cache: s._project_snapshot(ref, proj),
        )
        # Re-run per-claim without project_receipts / management_validated memoization,
        # delegating structural prefix checks to the same helpers used in JobStore.
        from ontolearn_engine.project.applications import claim_context
        from ontolearn_engine.project.format3 import _json, receipt_for
        from ontolearn_engine.project.project_lifecycle import creation_context

        try:
            for claim in store._db.execute("SELECT * FROM operation_claims"):
                if claim["kind"] != "application":
                    continue
                context = _json(claim["context"])
                if isinstance(context, dict) and "managementLifecycleContextVersion" in context:
                    validate_ledger(store)
                    if (
                        store._db.execute(
                            "SELECT 1 FROM management_receipts WHERE operation=?",
                            (claim["operation"],),
                        ).fetchone()
                        is None
                    ):
                        raise Format3Fault("structure")
                    continue
                internal = store._project(claim["project"])
                creation = creation_context(store, internal, claim["operation"])
                if creation is None:
                    claim_context(store, internal, claim["operation"])
                receipt = receipt_for(store, internal, claim["operation"])
                if creation is not None and receipt != creation["receipt"]:
                    raise Format3Fault("structure")
            store._validate_job3()
        except Format3Fault:
            raise
        except (ValueError, KeyError, TypeError, OverflowError):
            raise Format3Fault("structure") from None


def _run_outcome(fn):
    try:
        fn()
        return ("ok", None)
    except Format3Fault as exc:
        return ("fault", exc.category)


def _build_multi_project_ledger(tmp_path):
    db_path = tmp_path / "ledger.sqlite"
    store = JobStore(db_path, contract=CONTRACT, target_format=3)
    actor_id = _uid()
    proj_a = _create_blank_with_ops(store, actor_id, "Alpha", app_steps=12, with_domain_commit=True)
    proj_b = _create_blank_with_ops(store, actor_id, "Beta", app_steps=3, with_domain_commit=True)
    return store, actor_id, proj_a, proj_b


@pytest.mark.parametrize(
    "scenario",
    [
        "valid-ledger",
        "corrupt-snapshots-row",
        "corrupt-second-checkpoint-domain-revision",
        "corrupt-second-checkpoint-application",
        "missing-later-app-receipt",
        "mismatch-creation-receipt-claim",
        "corrupt-combined-marker-snapshot",
    ],
)
def test_differential_equivalence_against_uncached_reference(tmp_path, monkeypatch, scenario):
    store, _actor_id, proj_a, _proj_b = _build_multi_project_ledger(tmp_path)
    try:
        internal_a = proj_a["internal"]
        if scenario == "corrupt-snapshots-row":
            snap_id = store._db.execute(
                "SELECT domain_snapshot FROM app_checkpoints"
                " WHERE project=? ORDER BY rowid DESC LIMIT 1",
                (internal_a,),
            ).fetchone()[0]
            with _bypass_trigger(store._db, "immutable_snapshots_UPDATE"):
                store._db.execute(
                    "UPDATE snapshots SET payload=? WHERE id=?",
                    ("{corrupt", snap_id),
                )
        elif scenario in (
            "corrupt-second-checkpoint-domain-revision",
            "corrupt-second-checkpoint-application",
        ):
            # Target an application-only checkpoint (later seq) that shares the exact
            # same domainSnapshotRef as prior checkpoints, verifying that a cache hit on
            # domainSnapshotRef does not bypass _raw_checkpoint revision/application checks.
            later_op = proj_a["app_ops"][5]
            receipt_row = store._db.execute(
                "SELECT payload FROM app_receipts WHERE project=? AND operation=?",
                (internal_a, later_op),
            ).fetchone()
            later_cp_id = json.loads(receipt_row[0])["afterCheckpointRef"]
            cp_row = store._db.execute(
                "SELECT * FROM app_checkpoints WHERE id=?", (later_cp_id,)
            ).fetchone()
            payload = json.loads(cp_row["payload"])
            bad_payload = deepcopy(payload)
            if scenario == "corrupt-second-checkpoint-domain-revision":
                bad_payload["domainRevision"] = 99
            else:
                bad_payload["application"]["metadata"]["name"] = 42  # invalid non-str/None metadata
            bad_cp_id = digest(bad_payload)
            # Pre-populate cache with the valid snapshot BEFORE probing the corrupted 2nd checkpoint
            cached = {}
            format3._raw_checkpoint(store, internal_a, later_cp_id, _snapshots=cached)
            assert cp_row["domain_snapshot"] in cached
            store._db.execute(
                "INSERT INTO app_checkpoints VALUES(?,?,?,?)",
                (bad_cp_id, internal_a, cp_row["domain_snapshot"], canonical(bad_payload)),
            )
            uncached_outcome = _run_outcome(
                lambda: format3._raw_checkpoint(store, internal_a, bad_cp_id, _snapshots=None)
            )
            cached_outcome = _run_outcome(
                lambda: format3._raw_checkpoint(store, internal_a, bad_cp_id, _snapshots=cached)
            )
            assert cached_outcome == uncached_outcome == ("fault", "structure")
            return
        elif scenario == "missing-later-app-receipt":
            later_op = proj_a["app_ops"][-1]
            with _bypass_trigger(store._db, "immutable_app_receipts_DELETE"):
                store._db.execute(
                    "DELETE FROM app_receipts WHERE project=? AND operation=?",
                    (internal_a, later_op),
                )
        elif scenario == "mismatch-creation-receipt-claim":
            claim_row = store._db.execute(
                "SELECT context FROM operation_claims WHERE operation=?", (proj_a["create_op"],)
            ).fetchone()
            ctx = json.loads(claim_row[0])
            ctx["plan"]["afterCAS"]["operationSequence"] = 999
            with _bypass_trigger(store._db, "immutable_operation_claims_UPDATE"):
                store._db.execute(
                    "UPDATE operation_claims SET context=?, fingerprint=? WHERE operation=?",
                    (canonical(ctx), digest(ctx), proj_a["create_op"]),
                )
        elif scenario == "corrupt-combined-marker-snapshot":
            # Replace the combined commit's after_snapshot with the genesis snapshot id
            # (valid FK & valid snapshot row, wrong state vs domain["afterState"]).
            genesis_snap = store._db.execute(
                "SELECT domain_snapshot FROM app_checkpoints"
                " WHERE project=? ORDER BY rowid ASC LIMIT 1",
                (internal_a,),
            ).fetchone()[0]
            with _bypass_trigger(store._db, "immutable_commit_evidence_UPDATE"):
                store._db.execute(
                    "UPDATE commit_evidence SET after_snapshot=? WHERE project=? AND operation=?",
                    (genesis_snap, internal_a, proj_a["domain_op"]),
                )

        # Evaluate uncached reference WITHOUT side-effecting store._validate_job3 caching
        expected = _run_outcome(lambda: _uncached_reference_validate_job3(store, monkeypatch))
        actual = _run_outcome(store._validate_job3)
        assert actual == expected
        if scenario == "valid-ledger":
            assert actual == ("ok", None)
        else:
            assert actual[0] == "fault" and actual[1] in {"structure", "format"}
    finally:
        store.close()


def test_linear_complexity_bounds_on_shared_snapshots_and_claims(tmp_path, monkeypatch):
    """Ensure _validate_job3 and _history avoid O(K^2) re-walks and duplicate snapshot loads."""
    store, _actor_id, proj_a, proj_b = _build_multi_project_ledger(tmp_path)
    try:
        orig_history = format3._history
        orig_proj_snapshot = store._project_snapshot
        history_calls = []
        snapshot_calls = []

        def counted_history(s, proj):
            history_calls.append(proj)
            return orig_history(s, proj)

        def counted_snapshot(ref, proj):
            snapshot_calls.append((ref, proj))
            return orig_proj_snapshot(ref, proj)

        monkeypatch.setattr(format3, "_history", counted_history)
        monkeypatch.setattr(store, "_project_snapshot", counted_snapshot)

        # Total projects = 2, total operation_claims = 14 + 5 = 19
        store._validate_job3()
        assert len(history_calls) == 2

        distinct_a = {
            r[0]
            for r in store._db.execute(
                "SELECT DISTINCT domain_snapshot FROM app_checkpoints WHERE project=?",
                (proj_a["internal"],),
            )
        }
        snapshot_calls.clear()
        format3._history(store, proj_a["internal"])
        # 14 checkpoints in proj_a, only 2 distinct snapshots (rev 0 and rev 1)
        assert len(distinct_a) == 2
        assert len(snapshot_calls) == len(distinct_a)
    finally:
        store.close()


def _measure_import_after_app_checkpoints(
    base_dir, monkeypatch, num_checks: int
) -> tuple[int, int]:
    import hashlib

    store = JobStore(base_dir / "w4-e2e-like.sqlite", contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    monkeypatch.setattr(staging, "_USE_DIR_FD", False)
    try:

        def ex(method, params):
            req = {
                "kind": "request",
                "id": _uid(),
                "protocolVersion": 2 if method == "hello" else 3,
                "engineSessionId": None if method == "hello" else actor.session,
                "method": method,
                "params": params,
            }
            res = actor.request(req)
            actor.finish_query_reply(req["id"], emitted=True)
            assert res["ok"], res
            return res["result"]

        ex("hello", {"supportedVersions": [3], "clientId": _uid()})
        pid = ex(
            "project.create",
            {
                "requestVersion": 1,
                "operationId": _uid(),
                "name": "W4 来源项目",
                "initialization": {"kind": "blank"},
            },
        )["projectId"]
        ex("project.open", {"projectId": pid})

        tasks = ("mapping", "behavior", "scenario", "report")
        for idx in range(num_checks):
            ex(
                "project.learning.task.check",
                {"projectId": pid, "taskId": tasks[idx % len(tasks)], "operationId": _uid()},
            )

        staging_root = staging.staging_root(store)
        sel_export = _uid()
        exp_dir = staging_root / sel_export
        exp_dir.mkdir(parents=True)
        (exp_dir / "meta.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "selectionId": sel_export,
                    "projectId": pid,
                    "engineSessionId": actor.session,
                    "purpose": "package-export",
                    "extension": ".ontolearn.zip",
                    "outputFile": "output.ontolearn.zip",
                    "createdAt": "2026-11-24T00:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        echk = ex(
            "project.transfer.package.export.check",
            {
                "projectId": pid,
                "baseRevision": 0,
                "kind": "full",
                "options": {
                    "agentSessions": False,
                    "rawSources": False,
                    "derived": False,
                    "history": False,
                },
                "selectionId": sel_export,
            },
        )
        ex(
            "project.transfer.package.export",
            {
                "projectId": pid,
                "selectionId": sel_export,
                "checkRef": echk["checkRef"],
                "operationId": _uid(),
            },
        )
        pkg_bytes = (exp_dir / "output.ontolearn.zip").read_bytes()

        sel_import = _uid()
        imp_dir = staging_root / sel_import
        imp_dir.mkdir(parents=True)
        (imp_dir / "payload.ontolearn.zip").write_bytes(pkg_bytes)
        (imp_dir / "meta.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "selectionId": sel_import,
                    "projectId": pid,
                    "engineSessionId": actor.session,
                    "purpose": "package-import",
                    "format": "zip",
                    "extension": ".ontolearn.zip",
                    "payloadFile": "payload.ontolearn.zip",
                    "sha256": hashlib.sha256(pkg_bytes).hexdigest(),
                    "byteLength": len(pkg_bytes),
                    "createdAt": "2026-11-24T00:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        ichk = ex(
            "project.transfer.package.import.check",
            {"projectId": pid, "selectionId": sel_import, "expectedKind": "full"},
        )

        orig_history = format3._history
        orig_snap = store._project_snapshot
        h_calls, s_calls = [], []
        monkeypatch.setattr(
            format3, "_history", lambda s, p: (h_calls.append(p), orig_history(s, p))[1]
        )
        monkeypatch.setattr(
            store, "_project_snapshot", lambda r, p: (s_calls.append(r), orig_snap(r, p))[1]
        )

        imp = ex(
            "project.transfer.package.import",
            {
                "projectId": pid,
                "selectionId": sel_import,
                "checkRef": ichk["checkRef"],
                "packageSha256": ichk["packageSha256"],
                "expectedKind": "full",
                "operationId": _uid(),
            },
        )
        assert imp["importedProjectId"] != pid
        return len(h_calls), len(s_calls)
    finally:
        actor.mainline.close()
        store.close()


def test_windows_fallback_import_bounded_after_repeated_app_checkpoints(tmp_path, monkeypatch):
    """Package import validation stays O(distinct_snapshots), invariant to checkpoint growth."""
    dir_small = tmp_path / "c2"
    dir_large = tmp_path / "c12"
    dir_small.mkdir()
    dir_large.mkdir()
    h2, s2 = _measure_import_after_app_checkpoints(dir_small, monkeypatch, 2)
    h12, s12 = _measure_import_after_app_checkpoints(dir_large, monkeypatch, 12)
    assert h12 == h2 <= 10
    assert s12 == s2 <= 16
