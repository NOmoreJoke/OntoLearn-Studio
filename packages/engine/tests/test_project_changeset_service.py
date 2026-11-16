"""Formal ChangeSet SQLite service evidence; no workers or desktop runtime."""

import base64
import importlib.util
import json
from pathlib import Path
from uuid import uuid4

import pytest
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.storage import canonical, digest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "changeset_contract", ROOT / "packages/contracts/python/contract_v2.py"
)
CONTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACT)
IMPL = {
    "engineVersion": "0.1.0",
    "executionSemanticsVersion": "changeset-v1",
    "dependencyLockHash": "a" * 64,
}
LIMITS = {
    "startupMs": 10000,
    "handshakeMs": 5000,
    "requestMs": 5000,
    "heartbeatMs": 10000,
    "cancelGraceMs": 5000,
    "totalMs": 120000,
    "maxFrameBytes": 262144,
    "maxQueuedJobs": 32,
    "maxConcurrentJobs": 2,
    "maxPageItems": 100,
    "maxPageBytes": 131072,
    "maxWorkerMemoryBytes": 536870912,
}


def uid():
    return str(uuid4())


@pytest.fixture
def store(tmp_path):
    instance = JobStore(tmp_path / "project.sqlite", contract=CONTRACT, target_format=3)
    instance.create_project("changeset-project")
    instance.project = instance.public_project("changeset-project")
    instance.host, instance.session = uid(), uid()
    yield instance
    instance.close()


def host(store):
    return {"host_client_id": store.host, "engine_session_id": store.session}


def definition(value, identity="onto"):
    return {
        "layer": "ontology",
        "id": identity,
        "value": {
            "triples": [{"subject": "urn:s", "predicate": "urn:p", "object": canonical(value)}]
        },
    }


def preview(store, plan=None, *, target=None, hook=lambda _: None):
    base = store.project_get(store.project)["projectRevision"]
    request = {
        "projectId": store.project,
        "baseRevision": base,
        "intent": "change",
        "plan": plan or {},
    }
    if target is not None:
        request = {
            "projectId": store.project,
            "baseRevision": base,
            "intent": "undo",
            "targetOperationId": target,
        }
    return store.preview_changeset(
        store.project, base, request, **host(store), limits=LIMITS, hook=hook
    )


def pages(store, ready, *, page_size=200):
    token, result, all_pages = None, [], []
    while True:
        page = store.changeset_diff_page(
            store.project,
            ready["previewHash"],
            ready["manifest"]["documentKind"],
            page_size,
            token,
            **host(store),
            limits=LIMITS,
        )
        all_pages.append(page)
        result.extend(page["segments"])
        token = page["nextCursor"]
        if page["complete"]:
            break
    raw = b"".join(base64.b64decode(value["dataBase64"]) for value in result)
    assert digest(json.loads(raw)) == ready["manifest"]["documentHash"]
    return token, json.loads(raw), all_pages


def confirmation(store, ready):
    token, _, _ = pages(store, ready)
    return store.confirm_changeset(store.project, ready["previewHash"], token, **host(store))


def create(store, confirmed, operation=None):
    input_ = {
        "inputSnapshotId": confirmed["inputSnapshotId"],
        "scope": "asserted",
        "definitionId": "changeset",
        "parametersHash": confirmed["parametersHash"],
        "derivedResultIds": [],
        "preparedPlanRef": confirmed["preparedPlanRef"],
    }
    return store.create_changeset_job(
        store.project,
        operation or uid(),
        input_,
        confirmed["confirmationRef"],
        IMPL,
        LIMITS,
        **host(store),
    )


def commit(store, plan=None, *, target=None):
    ready = preview(store, plan, target=target)
    assert ready["status"] == "ready", ready
    confirmed = confirmation(store, ready)
    job = create(store, confirmed)
    store.start_job(job["jobId"])
    return store.commit_job(job["jobId"]), ready, confirmed


def test_real_definition_manual_commit_undo_and_reopen(store, tmp_path):
    fact = {"subject": "urn:fact", "predicate": "urn:p", "object": '"original"'}
    fact["id"] = digest([fact["subject"], fact["predicate"], fact["object"]])
    job, ready, confirmed = commit(store, {"definitions": [definition("a")], "manual": [fact]})
    assert job["state"] == "succeeded"
    assert job["resultRef"] is not None
    marker = store.operation_get(store.project, job["operationId"])
    assert marker["projectRevision"] == 1
    row = store._db.execute(
        "SELECT * FROM job_plans WHERE ref=?", (ready["preparedPlanRef"],)
    ).fetchone()
    assert (
        len(
            {
                ready["previewHash"],
                row["plan_hash"],
                ready["preparedPlanRef"],
                store._db.execute(
                    "SELECT fingerprint FROM jobs WHERE id=?", (job["jobId"],)
                ).fetchone()[0],
            }
        )
        == 4
    )
    undo, _, _ = commit(store, target=job["operationId"])
    assert undo["state"] == "succeeded"
    assert store.state("changeset-project")["definitions"] == []
    assert store.state("changeset-project")["facts"] == []
    project, old_host, old_session = store.project, store.host, store.session
    store.close()
    reopened = JobStore(tmp_path / "project.sqlite", contract=CONTRACT, target_format=3)
    try:
        assert (
            reopened.create_changeset_job(
                project,
                job["operationId"],
                job["input"],
                confirmed["confirmationRef"],
                IMPL,
                LIMITS,
                host_client_id=uid(),
                engine_session_id=uid(),
            )
            == job
        )
        with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
            reopened.create_changeset_job(
                project,
                uid(),
                job["input"],
                confirmed["confirmationRef"],
                IMPL,
                LIMITS,
                host_client_id=uid(),
                engine_session_id=uid(),
            )
        assert old_host != old_session
    finally:
        reopened.close()


def dump(store):
    return list(store._db.iterdump())


def test_legacy_v1_plan_receipt_and_job_remain_verifiable(store):
    # Construct a pre-lifecycle envelope using the real immutable row format.
    # Its distinct host keeps the new v2 preview out of legacy selection.
    ready = preview(store, {"definitions": [definition("legacy")]})
    row = store._db.execute(
        "SELECT * FROM job_plans WHERE ref=?", (ready["preparedPlanRef"],)
    ).fetchone()
    value = json.loads(row["payload"])
    value["preparedChangeSetVersion"] = 1
    del value["lifecycleVersion"]
    store.host = uid()
    value["hostClientId"] = store.host
    ref = digest(value)
    store._db.execute(
        "INSERT INTO job_plans VALUES(?,?,?,?,?,?)",
        (ref, row["project"], row["base"], row["plan_hash"], row["diff_hash"], canonical(value)),
    )
    confirmed = confirmation(store, {**ready, "preparedPlanRef": ref})
    assert confirmed["preparedPlanRef"] == ref
    job = create(store, confirmed)
    store.start_job(job["jobId"])
    completed = store.commit_job(job["jobId"])
    assert completed["state"] == "succeeded"
    store._validate_job3()
    store.close()
    reopened = JobStore(store.path, contract=CONTRACT, target_format=3)
    try:
        assert reopened.get_job(store.project, job["jobId"]) == completed
        assert reopened.reconcile_jobs() == []
    finally:
        reopened.close()


def test_preview_zero_domain_writes_and_opaque_untouched(store):
    store.commit(
        "changeset-project",
        0,
        uid(),
        uid(),
        definitions=[{"layer": "rule", "id": "opaque", "value": {"unknown": [1]}}],
    )
    state = store.state("changeset-project")
    counts = {
        table: store._db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        for table in ("commits", "commit_evidence", "app_receipts", "app_checkpoints")
    }
    ready = preview(store, {"definitions": [definition("value")]})
    assert ready["status"] == "ready"
    assert store.state("changeset-project") == state
    assert store.revision("changeset-project") == 1
    assert store._db.execute("SELECT count(*) FROM job_confirmations").fetchone()[0] == 0
    assert counts == {
        table: store._db.execute(f"SELECT count(*) FROM {table}").fetchone()[0] for table in counts
    }
    assert (
        json.loads(store._db.execute("SELECT payload FROM job_plans").fetchone()[0])["preview"][
            "after"
        ]["definitions"][1]
        == state["definitions"][0]
    )


@pytest.mark.parametrize(
    "plan",
    [
        {"definitions": [{"layer": "rule", "id": "x", "value": {}}]},
        {"definitions": [{"layer": "ontology", "id": "x", "value": {"unknown": "x"}}]},
        {"definitions": [{"layer": "ontology", "id": "x", "value": "opaque"}]},
        {"mapping": {"id": "x", "rows": []}},
        {"compensate": {"kind": "undo", "operation": "x"}},
        {"manual": [{"id": "bad", "subject": "urn:s", "predicate": "urn:p", "object": '"x"'}]},
    ],
)
def test_unsupported_typed_input_is_atomic(store, plan):
    before = dump(store)
    with pytest.raises((JobFault, ValueError)):
        preview(store, plan)
    assert dump(store) == before


def test_old_opaque_before_rejected_but_untouched_kept(store):
    store.commit(
        "changeset-project",
        0,
        uid(),
        uid(),
        definitions=[{"layer": "ontology", "id": "onto", "value": "opaque"}],
    )
    before = dump(store)
    with pytest.raises(JobFault, match="INVALID_REQUEST"):
        preview(store, {"definitions": [definition("replacement")]})
    assert dump(store) == before


def test_large_old_value_full_diff_pages_and_exact_receipt_after_gc(store):
    old = "旧😀" * 100000
    store.commit("changeset-project", 0, uid(), uid(), definitions=[definition(old)])
    ready = preview(store, {"definitions": [definition("new")]})
    assert ready["manifest"]["totalBytes"] > 262144
    token, items, delivery = pages(store, ready)
    assert len(delivery) > 1
    assert all(len(canonical(page).encode()) <= LIMITS["maxPageBytes"] for page in delivery)
    assert json.loads(items[0]["before"]["payload"])["triples"][0]["object"] == canonical(old)
    confirmed = store.confirm_changeset(store.project, ready["previewHash"], token, **host(store))
    issued = store._db.execute("SELECT count(*) FROM job_confirmations").fetchone()[0]
    store._db.execute("DELETE FROM job_cursors")
    store.now_ms = lambda: 10**14
    assert (
        store.confirm_changeset(store.project, ready["previewHash"], token, **host(store))
        == confirmed
    )
    assert store._db.execute("SELECT count(*) FROM job_confirmations").fetchone()[0] == issued
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        store.confirm_changeset(store.project, ready["previewHash"], uid(), **host(store))
    job = create(store, confirmed)
    store.start_job(job["jobId"])
    assert store.commit_job(job["jobId"])["state"] == "succeeded"
    assert (
        store.confirm_changeset(store.project, ready["previewHash"], token, **host(store))
        == confirmed
    )
    undo, _, _ = commit(store, target=job["operationId"])
    assert undo["state"] == "succeeded"
    assert json.loads(store.state("changeset-project")["definitions"][0]["payload"])["triples"][0][
        "object"
    ] == canonical(old)


def test_first_confirm_requires_whole_live_chain_and_current_base(store):
    store.commit("changeset-project", 0, uid(), uid(), definitions=[definition("x" * 80000)])
    ready = preview(store, {"definitions": [definition("new")]})
    first = store.changeset_diff_page(
        store.project, ready["previewHash"], "diff", 1, None, **host(store), limits=LIMITS
    )
    assert not first["complete"]
    with pytest.raises(JobFault, match="CURSOR_MISMATCH"):
        store.confirm_changeset(
            store.project, ready["previewHash"], first["nextCursor"], **host(store)
        )
    token, _, _ = pages(store, ready, page_size=1)
    store.commit("changeset-project", 1, uid(), uid(), definitions=[definition("unrelated", "b")])
    with pytest.raises(JobFault, match="REVISION_CONFLICT"):
        store.confirm_changeset(store.project, ready["previewHash"], token, **host(store))
    assert store._db.execute("SELECT count(*) FROM job_confirmations").fetchone()[0] == 0


def test_cursor_expiry_binding_and_session_before_first_confirm(store):
    ready = preview(store, {"definitions": [definition("one")]})
    token, _, _ = pages(store, ready)
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        store.confirm_changeset(
            store.project,
            ready["previewHash"],
            token,
            host_client_id=store.host,
            engine_session_id=uid(),
        )
    with pytest.raises(JobFault, match="CURSOR_MISMATCH"):
        store.changeset_diff_page(
            store.project, ready["previewHash"], "diff", 1, token, **host(store), limits=LIMITS
        )
    now = store.now_ms()
    store.now_ms = lambda: now + 60001
    with pytest.raises(JobFault, match="CURSOR_EXPIRED"):
        store.confirm_changeset(store.project, ready["previewHash"], token, **host(store))
    assert store._db.execute("SELECT count(*) FROM job_confirmations").fetchone()[0] == 0


def test_aba_impact_lists_both_real_later_changes_and_full_values(store):
    a, _, _ = commit(store, {"definitions": [definition("a")]})
    b, _, _ = commit(store, {"definitions": [definition("b")]})
    c, _, _ = commit(store, {"definitions": [definition("a")]})
    conflict = preview(store, target=a["operationId"])
    assert conflict["status"] == "conflict" and conflict["impactComplete"]
    _, items, _ = pages(store, conflict)
    later = [item for item in items if item["reason"] == "later-edit"]
    assert [item["operationId"] for item in later] == [b["operationId"], c["operationId"]]
    assert [json.loads(item["after"]["payload"])["triples"][0]["object"] for item in later] == [
        '"b"',
        '"a"',
    ]
    assert all(item["beforeSnapshotRef"] and item["afterSnapshotRef"] for item in later)
    assert "preparedPlanRef" not in conflict
    with pytest.raises(JobFault):
        store.confirm_changeset(store.project, conflict["previewHash"], uid(), **host(store))


def test_undo_reference_impact_and_disjoint_b_retained(store):
    a, _, _ = commit(store, {"definitions": [definition("a", "a")]})
    bplan = {
        "layer": "ontology",
        "id": "b",
        "value": {"references": [{"layer": "ontology", "id": "a"}]},
    }
    commit(store, {"definitions": [bplan]})
    conflict = preview(store, target=a["operationId"])
    _, items, _ = pages(store, conflict)
    blocked = [item for item in items if item["reason"] == "reference-block"]
    assert conflict["impactComplete"] and len(blocked) == 1
    assert blocked[0]["definition"] == {
        "layer": "ontology",
        "id": "b",
        "payload": canonical(bplan["value"]),
    }
    assert blocked[0]["target"] == ["definition", "ontology", "a"]
    commit(store, {"definitions": [definition("b", "b")]})
    undo, _, _ = commit(store, target=a["operationId"])
    assert undo["state"] == "succeeded"
    assert [(d["layer"], d["id"]) for d in store.state("changeset-project")["definitions"]] == [
        ("ontology", "b")
    ]


def test_target_legacy_is_incomplete_not_formal_ready(store):
    operation = uid()
    store.commit("changeset-project", 0, operation, uid(), definitions=[definition("a")])
    ready = preview(store, target=operation)
    assert ready["status"] == "conflict" and not ready["impactComplete"]
    _, items, _ = pages(store, ready)
    assert items[0]["reason"] == "unsupported-state"


@pytest.mark.parametrize("kind", ["plan", "confirm", "accept", "commit"])
@pytest.mark.parametrize("error", [RuntimeError, __import__("sqlite3").OperationalError])
def test_each_service_fault_rolls_back_every_persistent_boundary(store, kind, error):
    plan = {"definitions": [definition("new")]}
    ready, confirmed, job = None, None, None
    if kind != "plan":
        ready = preview(store, plan)
        token, _, _ = pages(store, ready)
    if kind in {"accept", "commit"}:
        confirmed = store.confirm_changeset(
            store.project, ready["previewHash"], token, **host(store)
        )
    if kind == "commit":
        job = create(store, confirmed)
        store.start_job(job["jobId"])
    phases = {
        "plan": ["before", "changeset_segment", "changeset_plan", "before_commit"],
        "confirm": [
            "before",
            "changeset_confirmation",
            "changeset_confirmation_receipt",
            "before_commit",
        ],
        "accept": ["before", "changeset_queued", "changeset_claim", "before_commit"],
        "commit": [
            "before",
            "mid_data",
            "mid_ownership",
            "mid_invalidation",
            "mid_marker",
            "format3_sequence",
            "format3_checkpoint",
            "format3_receipt",
            "changeset_result",
            "mid_job_terminal",
            "before_commit",
        ],
    }[kind]
    for phase in phases:
        before = dump(store)
        seen = []

        def hook(actual, selected=phase, calls=seen):
            calls.append(actual)
            if actual == selected:
                raise error("fixed test failure")

        with pytest.raises(error, match="fixed test failure"):
            if kind == "plan":
                preview(store, plan, hook=hook)
            elif kind == "confirm":
                store.confirm_changeset(
                    store.project, ready["previewHash"], token, **host(store), hook=hook
                )
            elif kind == "accept":
                input_ = {
                    "inputSnapshotId": confirmed["inputSnapshotId"],
                    "scope": "asserted",
                    "definitionId": "changeset",
                    "parametersHash": confirmed["parametersHash"],
                    "derivedResultIds": [],
                    "preparedPlanRef": confirmed["preparedPlanRef"],
                }
                store.create_changeset_job(
                    store.project,
                    uid(),
                    input_,
                    confirmed["confirmationRef"],
                    IMPL,
                    LIMITS,
                    **host(store),
                    hook=hook,
                )
            else:
                store.commit_job(job["jobId"], hook=hook)
        assert phase in seen
        assert dump(store) == before, phase


def test_confirmation_orphan_and_other_namespaces_fail_closed(store):
    ready = preview(store, {"definitions": [definition("new")]})
    token, _, _ = pages(store, ready)
    confirmed = store.confirm_changeset(store.project, ready["previewHash"], token, **host(store))
    input_ = {
        "inputSnapshotId": confirmed["inputSnapshotId"],
        "scope": "asserted",
        "definitionId": "changeset",
        "parametersHash": confirmed["parametersHash"],
        "derivedResultIds": [],
        "preparedPlanRef": confirmed["preparedPlanRef"],
    }
    input_["parametersHash"] = store.put_blob(store.project, {})
    before = dump(store)
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        store.create_job(
            store.project, uid(), "test.atomic", input_, confirmed["confirmationRef"], IMPL, LIMITS
        )
    assert dump(store) == before
    # Deliberate offline corruption fixture: a forged signing row or receipt may
    # not be healed. Restore its immutable trigger after deleting the signing row.
    triggers = store._db.execute(
        "SELECT name,sql FROM sqlite_master WHERE type='trigger' AND tbl_name='job_confirmations'"
    ).fetchall()
    for trigger in triggers:
        store._db.execute(f'DROP TRIGGER "{trigger["name"]}"')
    store._db.execute("DELETE FROM job_confirmations WHERE id=?", (confirmed["confirmationRef"],))
    for trigger in triggers:
        store._db.execute(trigger["sql"])
    before = dump(store)
    with pytest.raises(JobFault, match="INVALID_STATE"):
        store.confirm_changeset(store.project, ready["previewHash"], token, **host(store))
    assert dump(store) == before


@pytest.mark.parametrize(
    "table,kind",
    [
        ("job_blobs", "plan"),
        ("job_plans", "plan"),
        ("job_confirmations", "confirm"),
        ("job_details", "confirm"),
        ("jobs", "accept"),
        ("operation_claims", "accept"),
        ("definitions", "commit"),
        ("commits", "commit"),
        ("app_operations", "commit"),
        ("app_checkpoints", "commit"),
        ("app_receipts", "commit"),
        ("results", "commit"),
        ("job_results", "commit"),
    ],
)
def test_sqlite_actual_write_denial_has_no_partial_batch(store, table, kind):
    import sqlite3

    ready = confirmed = job = None
    if kind != "plan":
        ready = preview(store, {"definitions": [definition("new")]})
        token, _, _ = pages(store, ready)
    if kind in {"accept", "commit"}:
        confirmed = store.confirm_changeset(
            store.project, ready["previewHash"], token, **host(store)
        )
    if kind == "commit":
        job = create(store, confirmed)
        store.start_job(job["jobId"])
    before = dump(store)
    denied = []

    def authorize(action, name, column, database, cause):
        if (
            action in {sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE}
            and name == table
        ):
            denied.append((action, name))
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    store._db.set_authorizer(authorize)
    try:
        with pytest.raises(sqlite3.DatabaseError):
            if kind == "plan":
                preview(store, {"definitions": [definition("new")]})
            elif kind == "confirm":
                store.confirm_changeset(store.project, ready["previewHash"], token, **host(store))
            elif kind == "accept":
                create(store, confirmed)
            else:
                store.commit_job(job["jobId"])
    finally:
        store._db.set_authorizer(None)
    assert denied
    assert dump(store) == before


EXIT_PHASES = {
    "plan": ["before", "changeset_segment", "changeset_plan", "before_commit", "after_commit"],
    "confirm": [
        "before",
        "changeset_confirmation",
        "changeset_confirmation_receipt",
        "before_commit",
        "after_commit",
    ],
    "accept": ["before", "changeset_queued", "changeset_claim", "before_commit", "after_commit"],
    "commit": [
        "before",
        "mid_data",
        "mid_ownership",
        "mid_invalidation",
        "mid_marker",
        "format3_sequence",
        "format3_checkpoint",
        "format3_receipt",
        "changeset_result",
        "mid_job_terminal",
        "before_commit",
        "after_commit",
    ],
}


@pytest.mark.parametrize(
    "kind,phase", [(kind, phase) for kind, phases in EXIT_PHASES.items() for phase in phases]
)
def test_real_process_exit_each_boundary_and_reopen(tmp_path, kind, phase):
    import subprocess
    import sys

    path = tmp_path / "exit.sqlite"
    source = r"""
import json,os,runpy,sys
m=runpy.run_path(sys.argv[1]); path,kind,phase=sys.argv[2:]
s=m['JobStore'](path,contract=m['CONTRACT'],target_format=3)
s.create_project('changeset-project'); s.project=s.public_project('changeset-project')
s.host=m['uid'](); s.session=m['uid']()
plan={'definitions':[m['definition']('new')]}
if kind!='plan':
    ready=m['preview'](s,plan); token,_,_=m['pages'](s,ready)
if kind in {'accept','commit'}:
    confirmed=s.confirm_changeset(s.project,ready['previewHash'],token,**m['host'](s))
if kind=='commit':
    job=m['create'](s,confirmed); s.start_job(job['jobId'])
def hook(actual):
    print(json.dumps({'kind':kind,'wanted':phase,'actual':actual}),flush=True)
    if actual==phase: os._exit(73)
if kind=='plan': m['preview'](s,plan,hook=hook)
elif kind=='confirm':
    s.confirm_changeset(s.project,ready['previewHash'],token,**m['host'](s),hook=hook)
elif kind=='accept':
    input_={k:confirmed[k] for k in ['inputSnapshotId','parametersHash','preparedPlanRef']}
    input_.update(scope='asserted',definitionId='changeset',derivedResultIds=[])
    s.create_changeset_job(s.project,m['uid'](),input_,confirmed['confirmationRef'],m['IMPL'],m['LIMITS'],**m['host'](s),hook=hook)
else: s.commit_job(job['jobId'],hook=hook)
raise AssertionError('exit hook not reached')
"""
    process = subprocess.run(
        [sys.executable, "-c", source, __file__, str(path), kind, phase],
        capture_output=True,
        timeout=30,
    )
    log = tmp_path / f"t01-changeset-realexit-{kind}-{phase}.json"
    log.write_text(
        json.dumps(
            {
                "returncode": process.returncode,
                "stdout": process.stdout.decode(),
                "stderr": process.stderr.decode(),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    assert process.returncode == 73, log.read_text()
    assert json.loads(process.stdout.splitlines()[-1])["actual"] == phase
    reopened = JobStore(path, contract=CONTRACT, target_format=3)
    try:
        committed = kind == "commit" and phase == "after_commit"
        assert reopened.revision("changeset-project") == int(committed)
        assert reopened._db.execute("SELECT count(*) FROM commits").fetchone()[0] == int(committed)
        if kind in {"accept", "commit"}:
            accepted = kind == "commit" or phase == "after_commit"
            assert reopened._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == int(accepted)
            assert reopened._db.execute("SELECT count(*) FROM operation_claims").fetchone()[
                0
            ] == int(accepted)
        if kind == "plan":
            assert reopened._db.execute("SELECT count(*) FROM job_plans").fetchone()[0] == int(
                phase == "after_commit"
            )
            assert reopened._db.execute("SELECT count(*) FROM job_blobs").fetchone()[0] == (
                2 if phase == "after_commit" else 0
            )
        if kind == "confirm":
            assert reopened._db.execute("SELECT count(*) FROM job_confirmations").fetchone()[
                0
            ] == int(phase == "after_commit")
            assert reopened._db.execute("SELECT count(*) FROM job_details").fetchone()[0] == int(
                phase == "after_commit"
            )
        if kind == "commit":
            public = reopened.public_project("changeset-project")
            identity = reopened._db.execute("SELECT id FROM jobs").fetchone()[0]
            assert reopened.get_job(public, identity)["state"] == (
                "succeeded" if committed else "running"
            )
            if committed:
                terminal = reopened.get_job(public, identity)
                assert reopened.commit_job(identity) == terminal
                assert terminal["resultRef"]
                assert reopened._db.execute("SELECT count(*) FROM job_results").fetchone()[0] == 1
            else:
                reopened.reconcile_jobs()
                assert reopened.get_job(public, identity)["state"] == "failed"
                assert reopened._db.execute("SELECT count(*) FROM results").fetchone()[0] == 0
    finally:
        reopened.close()


def test_diff_budget_exact_raw_and_preflight_no_partial(store):
    from ontolearn_engine.project.domain_changesets import MAX_DOCUMENT, _document

    # Mechanism boundary uses the same canonical raw encoding, not a giant
    # incoming wire plan. Real >frame historical values are exercised above.
    material = ["x" * (MAX_DOCUMENT - 4)]
    manifest, values = _document(material, "diff")
    assert manifest["totalBytes"] == MAX_DOCUMENT
    assert len(values) == 512 and values[-1]["rawByteLength"] == 32768
    with pytest.raises(JobFault, match="RESOURCE_LIMIT"):
        _document(["x" * (MAX_DOCUMENT - 3)], "diff")
    store.commit("changeset-project", 0, uid(), uid(), definitions=[definition("old" * 30000)])
    before = dump(store)
    small = LIMITS | {"maxPageBytes": 2000}
    request = {
        "projectId": store.project,
        "baseRevision": 1,
        "intent": "change",
        "plan": {"definitions": [definition("new")]},
    }
    with pytest.raises(JobFault, match="RESOURCE_LIMIT"):
        store.preview_changeset(store.project, 1, request, **host(store), limits=small)
    assert dump(store) == before


def test_real_invalidation_and_disjoint_result_remains_current(store):
    from ontolearn_engine.storage import Store

    commit(store, {"definitions": [definition("a", "a"), definition("b", "b")]})
    snap = store.snapshot("changeset-project")
    affected = Store.publish(
        store, "changeset-project", snap, ["ontology:a"], "reasoning", [], IMPL
    )
    separate_impl = IMPL | {"executionSemanticsVersion": "independent-v1"}
    untouched = Store.publish(
        store, "changeset-project", snap, ["ontology:b"], "reasoning", [], separate_impl
    )
    commit(store, {"definitions": [definition("changed", "a")]})
    assert store.result(affected)["stale"]
    assert store.result(untouched)["stale"] == []
    assert (
        store._db.execute(
            "SELECT result FROM current_results WHERE result=?", (affected,)
        ).fetchone()
        is None
    )
    assert (
        store._db.execute(
            "SELECT result FROM current_results WHERE result=?", (untouched,)
        ).fetchone()[0]
        == untouched
    )


def manual(value='"A"', subject="urn:slot", predicate="urn:p"):
    return {
        "id": digest([subject, predicate, value]),
        "subject": subject,
        "predicate": predicate,
        "object": value,
    }


@pytest.mark.parametrize("mode", ["duplicate", "reserved-active", "reserved-tombstone", "single"])
def test_undo_full_owner_slot_projection_from_real_store_records(store, mode):
    initial = manual()
    store.commit("changeset-project", 0, uid(), uid(), manual=[initial])
    if mode == "single":
        store.commit(
            "changeset-project",
            1,
            uid(),
            uid(),
            definitions=[
                {
                    "layer": "ontology",
                    "id": "single",
                    "value": {"singleValuedPredicates": ["urn:p"]},
                }
            ],
        )
    commit(store, {"edits": {initial["id"]: '"B"'}})
    deleted, _, _ = commit(store, {"remove": [initial["id"]]})
    if mode == "duplicate":
        commit(store, {"manual": [manual('"B"')]})
    elif mode == "single":
        commit(store, {"manual": [manual('"C"')]})
    elif mode == "reserved-active":
        other = manual('"C"')
        commit(store, {"manual": [other]})
        commit(store, {"edits": {other["id"]: '"A"'}})
    else:
        # Private Store fixture is an actual mapping owner, outside public plan.
        reserved = manual('"B"')
        base = store.revision("changeset-project")
        store.commit(
            "changeset-project",
            base,
            uid(),
            uid(),
            mapping={"id": "M", "rows": [{"row": "001", "facts": [reserved]}]},
        )
        store.commit("changeset-project", base + 1, uid(), uid(), remove=[reserved["id"]])
    state, revision = store.state("changeset-project"), store.revision("changeset-project")
    conflict = preview(store, target=deleted["operationId"])
    assert conflict["status"] == "conflict" and conflict["impactComplete"]
    _, items, _ = pages(store, conflict)
    blockers = [
        item for item in items if item["reason"] in {"ownership-block", "single-value-block"}
    ]
    assert len(blockers) == 1
    blocker = blockers[0]
    assert blocker["resource"] == ["slot", "urn:slot", "urn:p"]
    assert blocker["reason"] == ("single-value-block" if mode == "single" else "ownership-block")
    facts = blocker["facts"]
    assert next(f for f in facts if f["id"] == initial["id"])["object"] == '"B"'
    if mode == "reserved-tombstone":
        tombstone = next(f for f in facts if f["id"] == reserved["id"])
        assert tombstone == next(f for f in state["facts"] if f["id"] == reserved["id"])
        assert tombstone["owner"] == "M" and tombstone["object"] is None
    assert store.state("changeset-project") == state
    assert store.revision("changeset-project") == revision


def test_retirement_aba_and_restore_are_forward_only(store):
    first, _, _ = commit(store, {"definitions": [definition("A")]})
    removed, _, _ = commit(store, {"remove_definitions": [{"layer": "ontology", "id": "onto"}]})
    assert store.retirement_control("changeset-project") == [["ontology", "onto"]]
    before_history = [
        tuple(row) for row in store._db.execute("SELECT * FROM commits ORDER BY revision")
    ]
    undo, _, _ = commit(store, target=removed["operationId"])
    assert undo["state"] == "succeeded"
    assert store.retirement_control("changeset-project") == []
    assert store.vector("changeset-project")["ontology:onto"] == 3
    assert [
        tuple(row)
        for row in store._db.execute("SELECT * FROM commits WHERE revision<=2 ORDER BY revision")
    ] == before_history
    conflict = preview(store, target=first["operationId"])
    assert conflict["status"] == "conflict" and conflict["impactComplete"]
    _, items, _ = pages(store, conflict)
    assert [
        i["operationId"]
        for i in items
        if i["reason"] == "later-edit" and i["resource"] == ["definition", "ontology", "onto"]
    ] == [removed["operationId"], undo["operationId"]]


def test_manual_batch_failure_leaves_no_first_item_or_history(store):
    item = manual()
    store.commit("changeset-project", 0, uid(), uid(), manual=[item])
    store.commit("changeset-project", 1, uid(), uid(), edits={item["id"]: '"B"'})
    old = dump(store)
    valid = manual(subject="urn:unrelated")
    # First item would be inserted; second item collides with the existing slot.
    with pytest.raises(JobFault, match="OWNERSHIP_CONFLICT"):
        preview(store, {"manual": [valid, manual('"B"')]})
    assert store.state("changeset-project")["facts"] == [
        {**item, "object": '"B"', "owner": None, "source_row": None, "managed_value": None}
    ]
    assert store.revision("changeset-project") == 2
    # Approved ownership detail is the sole auxiliary diagnostic; domain/history,
    # blobs, preparations and confirmation are unchanged.
    current = dump(store)
    assert [line for line in current if not line.startswith('INSERT INTO "job_details"')] == old


def test_missing_later_evidence_is_explicit_incomplete(store):
    first, _, _ = commit(store, {"definitions": [definition("A")]})
    other, _, _ = commit(store, {"definitions": [definition("B", "other")]})
    triggers = store._db.execute(
        "SELECT name,sql FROM sqlite_master WHERE type='trigger' AND tbl_name='commit_evidence'"
    ).fetchall()
    for trigger in triggers:
        store._db.execute(f'DROP TRIGGER "{trigger["name"]}"')
    store._db.execute("DELETE FROM commit_evidence WHERE operation=?", (other["operationId"],))
    for trigger in triggers:
        store._db.execute(trigger["sql"])
    ready = preview(store, target=first["operationId"])
    assert ready["status"] == "conflict" and ready["impactComplete"] is False
    _, items, _ = pages(store, ready)
    assert any(item["reason"] == "evidence-unavailable" for item in items)
    assert "preparedPlanRef" not in ready


def test_changed_original_operation_identity_never_allocates_second_claim(store):
    confirmed = confirmation(store, preview(store, {"definitions": [definition("A")]}))
    original = create(store, confirmed)
    before = dump(store)
    for key, value in [
        ("definitionId", "other"),
        ("scope", "scenario"),
        ("parametersHash", "0" * 64),
    ]:
        changed = original["input"] | {key: value}
        expected = "INVALID_REQUEST" if key == "scope" else "IDENTITY_CONFLICT"
        with pytest.raises(JobFault, match=expected):
            store.create_changeset_job(
                store.project,
                original["operationId"],
                changed,
                confirmed["confirmationRef"],
                IMPL,
                LIMITS,
                **host(store),
            )
        assert dump(store) == before
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        store.create_changeset_job(
            store.project,
            original["operationId"],
            original["input"],
            confirmed["confirmationRef"],
            IMPL | {"engineVersion": "other"},
            LIMITS,
            **host(store),
        )
    assert dump(store) == before


def test_noop_advances_domain_once_and_preserves_original_marker(store):
    job, _, _ = commit(store, {})
    original = store.operation_get(store.project, job["operationId"])
    assert original["projectRevision"] == 1
    assert store.commit_job(job["jobId"]) == job
    assert store.revision("changeset-project") == 1
    assert store.operation_get(store.project, job["operationId"]) == original


@pytest.mark.parametrize("record", ["segment", "parameters", "prepared"])
def test_preview_rejects_preexisting_corrupt_intern_record_without_healing(store, record):
    from ontolearn_engine.project.domain_changesets import (
        PLAN_VERSION,
        _document,
        _snapshot_id,
        pack,
    )
    from ontolearn_engine.project.transactions import ProjectTransactions

    plan = {"definitions": [definition("actual")]}
    actual = ProjectTransactions(store).preview("changeset-project", 0, plan)
    manifest, segments = _document(actual.diff, "diff")
    parameters = {
        "changeSetParametersVersion": 1,
        "previewHash": actual.identity,
        "intent": "change",
        "targetOperationId": None,
    }
    envelope = {
        PLAN_VERSION: 2,
        "lifecycleVersion": 0,
        "projectId": store.project,
        "hostClientId": store.host,
        "engineSessionId": store.session,
        "preview": pack(actual),
        "inputSnapshotId": _snapshot_id(store, actual),
        "parametersHash": digest(parameters),
        "manifest": manifest,
        "segmentBlobRefs": [digest(value) for value in segments],
    }
    bad = canonical({"corrupt": True})
    if record == "prepared":
        store._db.execute(
            "INSERT INTO job_plans VALUES(?,?,?,?,?,?)",
            (
                digest(envelope),
                store.project,
                0,
                ProjectTransactions._fingerprint(actual),
                manifest["documentHash"],
                bad,
            ),
        )
    else:
        expected = segments[0] if record == "segment" else parameters
        store._db.execute(
            "INSERT INTO job_blobs VALUES(?,?,?)", (store.project, digest(expected), bad)
        )
    before = dump(store)
    with pytest.raises(JobFault, match="INVALID_STATE"):
        preview(store, plan)
    assert dump(store) == before
    assert store.revision("changeset-project") == 0
    assert store._db.execute("SELECT count(*) FROM job_confirmations").fetchone()[0] == 0
