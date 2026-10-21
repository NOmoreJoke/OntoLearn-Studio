"""Actual non-Job CAS/combined transactions; no public3 runtime or learning claims."""

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.project import applications, format3
from ontolearn_engine.storage import Conflict, Store, canonical, digest
from test_job_store import CONTRACT, LIMITS, create, uid
from test_job_store import IMPL as JOB_IMPL

IMPL = {
    "executionSemanticsVersion": "app-test",
    "engineVersion": "test",
    "dependencyLockHash": "synthetic",
}
DOMAIN_TABLES = [
    "projects",
    "versions",
    "definitions",
    "facts",
    "mapping_state",
    "commits",
    "snapshots",
    "results",
    "result_state",
    "current_results",
    "result_pins",
    "runs",
    "rounds",
    "run_terminal",
]


def dump(path):
    con = sqlite3.connect(path)
    result = format3.logical_hash(con)
    con.close()
    return result


def domain_rows(store):
    return {
        name: sorted([tuple(r) for r in store._db.execute(f"SELECT * FROM {name}")], key=repr)
        for name in DOMAIN_TABLES
    }


@pytest.fixture
def store(tmp_path):
    s = JobStore(tmp_path / "p.db", contract=CONTRACT, target_format=3)
    s.create_project("p")
    s.project = s.public_project("p")
    s.actor = uid()
    s.commit(
        "p",
        0,
        uid(),
        "initial-job",
        definitions=[{"layer": "rule", "id": "r", "value": {"enabled": True}}],
    )
    s.probe_result = s.publish("p", s.snapshot("p"), ["rule:r"], "query", ["old"], IMPL)
    yield s
    s.close()


def change(name="renamed", version=0, combined=False):
    value = {
        "type": "metadata",
        "expectedVersion": version,
        "patch": {"name": name, "mode": "assisted"},
    }
    if combined:
        value["domain"] = {
            "base": 1,
            "plan": {"definitions": [{"layer": "rule", "id": "r", "value": {"enabled": False}}]},
        }
    return value


def save(editor="q", generation=0, content=None, bound=1):
    return {
        "type": "draft.save",
        "editor": editor,
        "expectedGeneration": generation,
        "boundDomainRevision": bound,
        "content": content,
    }


def apply(s, value, operation=None, prepared=None, actor=None, **kwargs):
    return s.apply_application(
        s.project,
        operation or uid(),
        value,
        actor=actor or s.actor,
        permission="write",
        **(
            {
                "prepared_plan_ref": prepared["preparedPlanRef"],
                "confirmation_ref": prepared["confirmationRef"],
            }
            if prepared
            else {}
        ),
        **kwargs,
    )


def test_metadata_draft_tombstones_and_mode_preserve_domain_results(store):
    s = store
    baseline = domain_rows(s)
    op = uid()
    request = change()
    first = apply(s, request, op)
    assert first["operationKind"] == "application" and first["domainMarkerRef"] is None
    assert first["domainBeforeRevision"] == first["domainAfterRevision"] == 1
    assert first["applicationBeforeCAS"] == [applications.cas("metadata", "p", 0)]
    assert first["applicationAfterCAS"] == [applications.cas("metadata", "p", 1)]
    assert s.marker("p", op) is None
    assert s._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0
    apply(s, save(content={"draft": "未保存内容"}))
    apply(
        s, save(generation=1, content={"draft": "未保存内容"})
    )  # explicit same content still advances
    apply(s, {"type": "draft.delete", "editor": "absent", "expectedGeneration": 0})
    apply(s, save("absent", 1, None))  # JSON null is present; deletion is not
    apply(s, {"type": "draft.delete", "editor": "absent", "expectedGeneration": 2})
    apply(s, change("mode switch", 1))
    current = s.project_checkpoint("p")
    q = next(r for r in current["application"]["drafts"] if r["editor"] == "q")
    tombstone = next(r for r in current["application"]["drafts"] if r["editor"] == "absent")
    assert q["generation"] == 2 and json.loads(q["payload"])["draft"] == "未保存内容"
    assert (
        tombstone["generation"] == 3 and tombstone["present"] == 0 and tombstone["payload"] is None
    )
    assert domain_rows(s) == baseline and not s.result(s.probe_result)["stale"]
    before = dump(s.path)
    assert apply(s, request, op) == first  # old metadata CAS exact retry after later changes
    assert dump(s.path) == before
    request["patch"]["name"] = "mutated caller"
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        apply(s, request, op)
    first["applicationAfterCAS"][0]["version"] = 999  # returned values are not mutable authority
    assert s.project_receipt("p", op)["applicationAfterCAS"][0]["version"] == 1


def test_two_read_connections_same_generation_one_owner_cas_wins(store):
    s = store
    readers = [sqlite3.connect(s.path.as_uri() + "?mode=ro", uri=True) for _ in range(2)]
    try:
        observed = []
        for con in readers:
            row = con.execute(
                "SELECT generation FROM app_drafts WHERE project='p' AND editor='q'"
            ).fetchone()
            observed.append(row[0] if row else 0)
        assert observed == [0, 0]
        apply(s, save(generation=observed[0], content="first"))
        before = dump(s.path)
        operation = uid()
        with pytest.raises(Conflict):
            apply(s, save(generation=observed[1], content="late"), operation)
        assert dump(s.path) == before and not s.has_operation_claim(operation)
    finally:
        for con in readers:
            con.close()


def test_draft_restore_uses_current_header_and_full_confirmed_preview(store):
    s = store
    apply(s, save(content="original"))
    target = digest(s.project_checkpoint("p"))
    apply(s, {"type": "draft.delete", "editor": "q", "expectedGeneration": 1})
    request = {
        "type": "draft.restore",
        "editor": "q",
        "expectedGeneration": 2,
        "checkpointRef": target,
    }
    before = dump(s.path)
    with pytest.raises(Conflict):
        apply(s, request)
    assert dump(s.path) == before
    prepared = s.prepare_application(s.project, request, actor=s.actor, permission="write")
    # A different editor changes the whole confirmed preview. Reject, never write
    # the frozen after-state over unrelated content even if q's CAS still matches.
    apply(s, save("other", 0, "keep"))
    before = dump(s.path)
    with pytest.raises(Conflict):
        apply(s, request, prepared=prepared)
    assert dump(s.path) == before
    prepared = s.prepare_application(s.project, request, actor=s.actor, permission="write")
    receipt = apply(s, request, prepared=prepared)
    assert receipt["applicationAfterCAS"] == [applications.cas("draft", "q", 3)]
    rows = s.project_checkpoint("p")["application"]["drafts"]
    assert json.loads(next(r["payload"] for r in rows if r["editor"] == "q")) == "original"
    assert json.loads(next(r["payload"] for r in rows if r["editor"] == "other")) == "keep"
    assert s.revision("p") == 1


def test_combined_one_marker_one_sequence_real_null_job_and_fingerprints(store):
    s = store
    request = change(combined=True)
    operation = uid()
    before = dump(s.path)
    with pytest.raises(Conflict):
        apply(s, request, operation)
    assert dump(s.path) == before
    prepared = s.prepare_application(s.project, request, actor=s.actor, permission="write")
    receipt = apply(s, request, operation, prepared)
    marker = s.marker("p", operation)
    assert marker["job"] is None and marker["revision"] == 2
    assert receipt["operationKind"] == "combined" and receipt["operationSequence"] == 2
    assert receipt["domainBeforeRevision"] == 1 and receipt["domainAfterRevision"] == 2
    context = applications.claim_context(s, "p", operation)
    raw_claim = s._db.execute(
        "SELECT fingerprint FROM operation_claims WHERE operation=?", (operation,)
    ).fetchone()[0]
    assert raw_claim == digest(context)
    assert receipt["planHash"] == digest(context["plan"])
    assert marker["fingerprint"] == digest(json.loads(marker["plan"]))
    assert len({raw_claim, receipt["planHash"], marker["fingerprint"]}) == 3
    assert s.result(s.probe_result)["stale"]
    apply(s, save(content="later", bound=2))
    before = dump(s.path)
    assert apply(s, request, operation, prepared) == receipt
    assert dump(s.path) == before and s.revision("p") == 2
    path = s.path
    s.close()
    s = JobStore(path, contract=CONTRACT, target_format=3)
    try:
        assert s.project_checkpoint("p")["operationSequence"] == 3
        assert s.project_receipt("p", operation) == receipt
    finally:
        s.close()


@pytest.mark.parametrize("mutation", ["actor", "target", "request", "confirmation"])
def test_confirmation_exact_binding(store, mutation):
    s = store
    request = change(combined=True)
    prepared = s.prepare_application(s.project, request, actor=s.actor, permission="write")
    actor = s.actor
    if mutation == "actor":
        actor = uid()
    elif mutation == "target":
        s.create_project("second")
        s.project = s.public_project("second")
    elif mutation == "request":
        request["patch"]["name"] = "different"
    else:
        prepared["confirmationRef"] = uid()
    before = dump(s.path)
    operation = uid()
    with pytest.raises(Conflict):
        apply(s, request, operation, prepared, actor)
    assert dump(s.path) == before and not s.has_operation_claim(operation)


@pytest.mark.parametrize("direction", ["application-to-job", "job-to-application"])
def test_prepared_credentials_cannot_cross_namespaces(store, direction):
    s = store
    request = change(combined=True)
    snap = s.project_get(s.project)
    parameters = s.put_blob(s.project, {})
    if direction == "application-to-job":
        prepared = s.prepare_application(s.project, request, actor=s.actor, permission="write")
    else:
        prepared = s.prepare_plan(s.project, 1, {}, actor=s.actor, permission="write")
    operation = uid()
    before = dump(s.path)
    with pytest.raises((JobFault, Conflict)):
        if direction == "application-to-job":
            s.create_job(
                s.project,
                operation,
                "test.atomic",
                {
                    "inputSnapshotId": snap["inputSnapshotId"],
                    "scope": "asserted",
                    "definitionId": "probe",
                    "parametersHash": parameters,
                    "derivedResultIds": [],
                    "preparedPlanRef": prepared["preparedPlanRef"],
                },
                prepared["confirmationRef"],
                JOB_IMPL,
                LIMITS,
            )
        else:
            apply(s, request, operation, prepared)
    assert dump(s.path) == before and not s.has_operation_claim(operation)
    assert s._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0
    s.close()
    reopened = JobStore(s.path, contract=CONTRACT, target_format=3)
    try:
        assert dump(s.path) == before
        assert reopened.project_checkpoint("p")["operationSequence"] == 1
    finally:
        reopened.close()


def test_global_kind_project_identity_and_unclaimed_marker_cannot_be_adopted(store):
    s = store
    job = create(s)
    before = dump(s.path)
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        apply(s, change(), job["operationId"])
    assert dump(s.path) == before
    operation = uid()
    apply(s, change(), operation)
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        create(s, operation=operation)
    s.create_project("second")
    second = s.public_project("second")
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        s.apply_application(second, operation, change(), actor=s.actor, permission="write")
    orphan = uid()
    s.commit("second", 0, orphan, "old-job")
    before = dump(s.path)
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        apply(s, change(version=1), orphan)
    assert dump(s.path) == before


@pytest.mark.parametrize(
    "bad",
    [
        {"type": "metadata", "expectedVersion": 0, "patch": {"mode": "professional"}},
        {"type": "metadata", "expectedVersion": 0, "patch": {"mode": []}},
        {"type": "metadata", "expectedVersion": True, "patch": {"name": "n"}},
        {"type": "metadata", "expectedVersion": 0, "patch": {"origin": "created"}},
        {"type": "metadata", "expectedVersion": 0, "patch": {"templateRef": "invented"}},
        {"type": "learning.record", "passed": True},
        {"type": "application.restore", "checkpointRef": "fake"},
        {
            "type": "draft.save",
            "editor": "q",
            "expectedGeneration": 0,
            "boundDomainRevision": 2,
            "content": "future",
        },
        {
            "type": "draft.save",
            "editor": "q",
            "expectedGeneration": 0,
            "boundDomainRevision": 1,
            "content": "\ud800",
        },
    ],
)
def test_invalid_or_not_yet_supported_changes_have_no_claim_or_effect(store, bad):
    before = dump(store.path)
    operation = uid()
    with pytest.raises((Conflict, ValueError)):
        apply(store, bad, operation)
    assert dump(store.path) == before and not store.has_operation_claim(operation)


@pytest.mark.parametrize("field", ["origin", "draft", "audit"])
def test_forged_resolved_plan_cannot_change_undeclared_resources(store, field):
    s = store
    request = change()
    operation = uid()
    plan = applications.construct_plan(s, "p", request)
    if field == "origin":
        plan["after"]["metadata"]["origin"] = "migration-default"
    elif field == "draft":
        plan["after"]["drafts"] = [
            {
                "editor": "hidden",
                "generation": 1,
                "present": 1,
                "bound_revision": 1,
                "payload": canonical("injected"),
                "content_hash": digest("injected"),
            }
        ]
    else:
        plan["after"]["assistanceAudit"] = [
            {"sequence": 1, "attempt": "a", "event_id": "fake", "payload": "{}"}
        ]
    context = {
        "applicationContextVersion": 1,
        "projectId": s.project,
        "project": "p",
        "operationId": operation,
        "request": {
            "change": request,
            "authorization": {
                "actor": s.actor,
                "permission": "write",
                "preparedPlanRef": None,
                "confirmationRef": None,
            },
        },
        "plan": plan,
    }
    s._db.execute(
        "INSERT INTO operation_claims VALUES(?,?,NULL,?,'application',?)",
        (operation, s.project, digest(context), canonical(context)),
    )
    before = dump(s.path)
    with pytest.raises((Conflict, format3.Format3Fault)):
        Store.commit(s, "p", None, operation, None, application=context)
    assert dump(s.path) == before


BASE_PHASES = [
    "before",
    "application_claim",
    "application_state",
    "application_sequence",
    "application_checkpoint",
    "application_receipt",
    "before_commit",
    "after_commit",
]
CASES = [
    (kind, phase)
    for kind in ("application", "combined")
    for phase in (
        BASE_PHASES
        + (
            ["mid_data", "mid_ownership", "mid_invalidation", "mid_marker", "application_domain"]
            if kind == "combined"
            else []
        )
    )
]


@pytest.mark.parametrize("kind,phase", CASES)
@pytest.mark.parametrize("failure", ["exception", "cancel", "disk", "exit"])
def test_application_combined_atomic_faults(store, kind, phase, failure):
    s = store
    request = change(combined=kind == "combined")
    operation = uid()
    prepared = (
        s.prepare_application(s.project, request, actor=s.actor, permission="write")
        if kind == "combined"
        else None
    )
    before = dump(s.path)
    path = s.path
    project = s.project
    actor = s.actor
    if failure == "exit":
        s.close()
        script = """import os,sys,json
from ontolearn_engine.job_store import JobStore
from test_job_store import CONTRACT
s=JobStore(sys.argv[1],contract=CONTRACT,target_format=3)
prepared=json.loads(sys.argv[7])
def hook(p):
    if p==sys.argv[6]: os._exit(79)
s.apply_application(sys.argv[2],sys.argv[3],json.loads(sys.argv[5]),actor=sys.argv[4],permission='write',
prepared_plan_ref=prepared['preparedPlanRef'] if prepared else None,
confirmation_ref=prepared['confirmationRef'] if prepared else None,hook=hook)
"""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                script,
                str(path),
                project,
                operation,
                actor,
                canonical(request),
                phase,
                canonical(prepared),
            ],
            env={**os.environ, "PYTHONPATH": str(Path(__file__).parent)},
            capture_output=True,
            timeout=15,
        )
        assert result.returncode == 79, result.stderr.decode()
    else:
        error = {"exception": RuntimeError, "cancel": KeyboardInterrupt, "disk": OSError}[failure]

        def hook(p):
            if p == phase:
                raise error("injected")

        with pytest.raises(error):
            apply(s, request, operation, prepared, hook=hook)
        s.close()
    s = JobStore(path, contract=CONTRACT, target_format=3)
    s.project = project
    s.actor = actor
    try:
        if phase == "after_commit":
            receipt = s.project_receipt("p", operation)
            assert receipt["operationKind"] == kind and receipt["operationSequence"] == 2
            committed = dump(path)
            assert apply(s, request, operation, prepared) == receipt
            assert dump(path) == committed and s.revision("p") == (2 if kind == "combined" else 1)
        else:
            assert dump(path) == before and not s.has_operation_claim(operation)
            assert s.revision("p") == 1
        s._validate_job3()
    finally:
        s.close()


def test_mixed_sequence_pages_hold_bound_while_appending(store):
    s = store
    first = apply(s, change())
    apply(s, save(content="one"))
    page = s.project_operations("p", limit=1)
    assert page["throughSequence"] == 3 and page["nextSequence"] == 1
    apply(s, save(generation=1, content="two"))
    items = page["items"]
    while page["nextSequence"] is not None:
        page = s.project_operations(
            "p", after_sequence=page["nextSequence"], through_sequence=3, limit=1
        )
        items += page["items"]
    assert [item["sequence"] for item in items] == [1, 2, 3]
    assert [item["operationKind"] for item in items] == ["domain", "application", "application"]
    assert items[1]["receipt"] == first and all(item["domainRevision"] == 1 for item in items)
    assert s.project_checkpoint("p")["operationSequence"] == 4


@pytest.mark.parametrize("field", ["metadata", "draft"])
def test_application_version_limit_rejects_before_effect(field, tmp_path):
    # Pure effects validate trusted headers before a write; no corrupt live DB
    # or forged history is needed to exercise the exact CAS overflow boundary.
    state = {
        "metadataVersion": format3.MAX_VERSION,
        "metadata": format3.metadata("created"),
        "drafts": [],
        "learningCurrent": [],
        "assistanceAudit": [],
    }
    if field == "metadata":
        request = change(version=format3.MAX_VERSION)
    else:
        state["metadataVersion"] = 0
        state["drafts"] = [
            {
                "editor": "q",
                "generation": format3.MAX_VERSION,
                "present": 0,
                "bound_revision": 1,
                "payload": None,
                "content_hash": None,
            }
        ]
        request = save(generation=format3.MAX_VERSION, content="over")
    with pytest.raises(Conflict):
        applications.effects("p", request, state, 1, 1)
