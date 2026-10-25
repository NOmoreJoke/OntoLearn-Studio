"""A successful controlled write must leave its same owner able to read."""

import asyncio
import base64
import hashlib
import json
import os
import sys
from contextlib import asynccontextmanager
from types import SimpleNamespace

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.project.mainline import READ_LIMITS, prepare_mainline_store
from ontolearn_engine.project.project_host import HostReadFault, MaterialProfile
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import canonical
from test_mainline_dispatch import (
    confirmed_job,
    create,
    drain_owned_changesets,
    exchange,
    frame,
    uid,
)
from test_mainline_dispatch import owned as owned
from test_mainline_language_input_rejection import database_files
from test_mainline_manual_input_rejection import fact
from test_mainline_read_work_budget import job_request, prepare


@pytest.mark.parametrize("axis", ["rows", "bytes", "work"])
@pytest.mark.parametrize("delta", [-1, 0, 1])
def test_original_admission_boundary_includes_all_terminal_headroom(axis, delta):
    pending, runs, extra = 2, 1, 8192
    rows, scan, decoded, repeats = 1, 100, 100, 1
    if axis == "rows":
        rows = 4096 - runs + delta
    elif axis == "bytes":
        decoded = 1572864 - extra + delta
        scan = decoded
    else:
        repeats = 63
        decoded = 1000000 - extra + delta
        scan = (67108864 + delta - (decoded + extra) * repeats) // 2 - extra
    profile = MaterialProfile(rows, scan, decoded, 0, repeats, 1)
    if delta > 0:
        with pytest.raises(HostReadFault) as caught:
            profile.admit_terminal_growth(READ_LIMITS, pending, runs)
        assert caught.value.reason == "limit"
    else:
        profile.admit_terminal_growth(READ_LIMITS, pending, runs)


def test_terminal_tail_proof_covers_error_marker_progress_and_run_row():
    # Independent pinned wire maxima: error + three 16-digit fields + longest
    # quoted state + largest progress + the complete possible run_terminal row.
    assert 2048 + 3 * 16 + 12 + max(365, 193) + (36 + 9 + 224) == 2742
    assert 2742 < 4096


def test_real_owner_draft_growth_rejects_before_read_admission_is_lost(owned, tmp_path):
    actor, store = owned
    project = create(actor, "postwrite admission fresh controlled fixture")[0]["projectId"]
    host = actor.mainline
    identity = (host.owner_id, host.host, host.session, host.generation, host.selected)
    trace = []
    refused = False
    for index in range(32):
        before = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
        assert before["ok"], before
        operation = uid()
        generation = before["result"]["workspace"]["draft"].get("generation", 0)
        params = {
            "projectId": project,
            "operationId": operation,
            "editor": "ontology",
            "expectedGeneration": generation,
            "boundDomainRevision": 0,
            "contentJson": canonical({"note": str(index) + "x" * 12000}),
        }
        physical_before = database_files(tmp_path / "mainline.sqlite")
        result = exchange(actor, "project.draft.save", params)
        physical_after = database_files(tmp_path / "mainline.sqlite")
        after = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
        trace.append(
            {
                "index": index,
                "before": before,
                "write": result,
                "after": after,
                "held": host.hold,
                "operation": operation,
            }
        )
        (tmp_path / "postwrite-trace.json").write_text(
            json.dumps(trace, ensure_ascii=False), encoding="utf-8"
        )
        # Preserve the actual successful-write/failed-read RED before stopping.
        assert after["ok"], {"write": result, "read": after, "index": index}
        assert actor.mainline is host and not host.hold and host.replies == {}
        assert (host.owner_id, host.host, host.session, host.generation, host.selected) == identity
        if not result["ok"]:
            assert result["error"]["code"] == "RESOURCE_LIMIT", result
            assert after["result"] == before["result"]
            assert not store.has_operation_claim(operation)
            assert physical_after == physical_before
            refused = True
            break
    assert refused, "Bounded fixture must reach a controlled admission refusal"
    # A rejected large growth does not poison the original host. A smaller legal
    # draft is a new real operation, not a HOLD clear, rebind or direct SQL repair.
    params.update(operationId=uid(), contentJson=canonical({"note": "small follow-up"}))
    follow = exchange(actor, "project.draft.save", params)
    assert follow["ok"], follow
    final = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
    assert final["ok"] and final["result"]["domain"] == before["result"]["domain"]
    assert actor.mainline is host and not host.hold
    (tmp_path / "postwrite-follow-up.json").write_text(
        json.dumps({"write": follow, "read": final}), encoding="utf-8"
    )


@pytest.mark.parametrize("outcome", ["commit-limit", "cancel", "fail"])
def test_queued_commit_rechecks_all_final_material_and_keeps_real_failed_job(
    owned, tmp_path, outcome, monkeypatch
):
    actor, store = owned
    project = create(actor, "queued final material")[0]["projectId"]
    confirmation = prepare(actor, project, 0, {"manual": [fact('"' + "q" * 60000 + '"')]})
    request = job_request(project, uid(), confirmation)
    accepted = exchange(actor, "job.create", request)
    assert accepted["ok"], accepted
    identity = accepted["result"]["jobId"]
    host = actor.mainline
    for index in range(32):
        before = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
        assert before["ok"], before
        saved = exchange(
            actor,
            "project.draft.save",
            {
                "projectId": project,
                "operationId": uid(),
                "editor": "ontology",
                "expectedGeneration": before["result"]["workspace"]["draft"].get("generation", 0),
                "boundDomainRevision": 0,
                "contentJson": canonical({"note": str(index) + "x" * 12000}),
            },
        )
        if not saved["ok"]:
            assert saved["error"]["code"] == "RESOURCE_LIMIT", saved
            break
    else:
        pytest.fail("Expected a bounded controlled growth refusal")
    stable = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
    assert stable["ok"]

    def non_job_rows():
        result = {}
        for (name,) in store._db.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            if name != "jobs":
                quoted = '"' + name.replace('"', '""') + '"'
                result[name] = [tuple(row) for row in store._db.execute(f"SELECT * FROM {quoted}")]
        return result

    before_rows = non_job_rows()
    if outcome == "cancel":
        cancelled = exchange(actor, "job.cancel", {"projectId": project, "jobId": identity})
        assert cancelled["ok"], cancelled
    elif outcome == "fail":
        original_commit = store.commit_job

        def fail_original_job(job_id, **kwargs):
            if job_id == identity:
                raise JobFault("TIMEOUT", {"phase": "total"})
            return original_commit(job_id, **kwargs)

        monkeypatch.setattr(store, "commit_job", fail_original_job)
        drain_owned_changesets(actor)
        monkeypatch.setattr(store, "commit_job", original_commit)
    else:
        drain_owned_changesets(actor)
    job = store.get_job(project, identity)
    marker = exchange(
        actor, "operation.get", {"projectId": project, "operationId": request["operationId"]}
    )
    after = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
    (tmp_path / "queued-final-trace.json").write_text(
        json.dumps(
            {
                "accepted": accepted,
                "before": stable,
                "job": job,
                "marker": marker,
                "after": after,
            }
        ),
        encoding="utf-8",
    )
    if outcome == "cancel":
        assert job["state"] == "cancelled" and job["error"] is None, job
    else:
        assert job["state"] == "failed", job
        assert job["error"]["code"] == ("TIMEOUT" if outcome == "fail" else "RESOURCE_LIMIT"), job
    assert marker["ok"] and marker["result"] is None
    assert after["ok"] and after["result"] == stable["result"]
    assert non_job_rows() == before_rows  # Only the authentic original Job DTO changes.
    assert actor.mainline is host and not host.hold and host.replies == {}
    replay = exchange(actor, "job.create", request)
    assert replay["ok"] and replay["result"] == job
    assert non_job_rows() == before_rows
    small = confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": 0,
            "intent": "change",
            "plan": {"manual": [fact('"small legal follow-up"')]},
        },
    )
    drain_owned_changesets(actor)
    assert store.get_job(project, small["jobId"])["state"] == "succeeded"
    final_marker = exchange(
        actor, "operation.get", {"projectId": project, "operationId": small["operationId"]}
    )
    final = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
    assert final_marker["ok"] and final_marker["result"]["jobId"] == small["jobId"]
    assert final["ok"] and final["result"]["domain"]["projectRevision"] == 1
    assert actor.mainline is host and not host.hold


def test_two_projects_pending_keep_global_terminal_headroom(owned, monkeypatch, tmp_path):
    actor, store = owned
    host = actor.mainline
    projects, jobs = [], []
    for name in ("first pending project", "second pending project"):
        project = create(actor, name)[0]["projectId"]
        projects.append(project)
        confirmation = prepare(actor, project, 0, {"manual": [fact('"' + "q" * 60000 + '"')]})
        accepted = exchange(actor, "job.create", job_request(project, uid(), confirmation))
        assert accepted["ok"] and accepted["result"]["state"] == "queued", accepted
        jobs.append(accepted["result"])
    assert (
        sum(
            store.get_job(p, j["jobId"])["state"] == "queued"
            for p, j in zip(projects, jobs, strict=True)
        )
        == 2
    )
    project = projects[0]
    assert exchange(actor, "project.open", {"projectId": project})["ok"]
    for index in range(32):
        before = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
        assert before["ok"], before
        saved = exchange(
            actor,
            "project.draft.save",
            {
                "projectId": project,
                "operationId": uid(),
                "editor": "ontology",
                "expectedGeneration": before["result"]["workspace"]["draft"].get("generation", 0),
                "boundDomainRevision": 0,
                "contentJson": canonical({"note": str(index) + "x" * 12000}),
            },
        )
        after = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
        assert after["ok"], after
        if not saved["ok"]:
            assert saved["error"] == {
                "code": "RESOURCE_LIMIT",
                "messageKey": "resource.limitExceeded",
                "params": {"resource": "page"},
                "retryable": False,
            }
            assert after["result"] == before["result"]
            break
    else:
        pytest.fail("Expected original-cap growth refusal with two accepted Jobs")
    # Only the original Job DTO rows change; this is a logical row comparison.
    non_jobs = {}
    for (name,) in store._db.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        if name != "jobs":
            quoted = '"' + name.replace('"', '""') + '"'
            non_jobs[name] = list(store._db.execute(f"SELECT * FROM {quoted}"))
    cancelled = exchange(actor, "job.cancel", {"projectId": project, "jobId": jobs[0]["jobId"]})
    assert cancelled["ok"], cancelled
    original_commit = store.commit_job

    def fail_second_job(identity, **kwargs):
        if identity == jobs[1]["jobId"]:
            raise JobFault("TIMEOUT", {"phase": "total"})
        return original_commit(identity, **kwargs)

    monkeypatch.setattr(store, "commit_job", fail_second_job)
    drain_owned_changesets(actor)
    monkeypatch.setattr(store, "commit_job", original_commit)
    terminal = [store.get_job(p, j["jobId"]) for p, j in zip(projects, jobs, strict=True)]
    assert [job["state"] for job in terminal] == ["cancelled", "failed"]
    assert terminal[1]["error"]["code"] == "TIMEOUT"
    for name, rows in non_jobs.items():
        quoted = '"' + name.replace('"', '""') + '"'
        assert list(store._db.execute(f"SELECT * FROM {quoted}")) == rows
    results = []
    for p, job in zip(projects, jobs, strict=True):
        assert exchange(actor, "project.open", {"projectId": p})["ok"]
        read = exchange(actor, "project.read", {"projectId": p, "editor": "ontology"})
        marker = exchange(
            actor, "operation.get", {"projectId": p, "operationId": job["operationId"]}
        )
        assert read["ok"] and read["result"]["domain"]["projectRevision"] == 0
        assert marker["ok"] and marker["result"] is None
        results.append({"read": read, "marker": marker})
    assert actor.mainline is host and not host.hold and host.replies == {}
    (tmp_path / "two-project-terminal.json").write_text(
        json.dumps({"jobs": terminal, "results": results})
    )


@pytest.mark.parametrize("change", ["unknown", "replacement"])
def test_original_foreground_scope_cannot_borrow_successor_or_background(owned, change):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    host, admission = actor.mainline, store._read_admission
    original = frame(actor, "project.read", {"projectId": project, "editor": "ontology"})
    host.begin(original)
    reply = host.current
    successor = frame(actor, "project.read", {"projectId": project, "editor": "ontology"})
    work = reply.work

    def hook(phase):
        if phase == "before_commit":
            if change == "unknown":
                reply.unknown = True
            else:
                host.current = None
                host.begin(successor)

    with pytest.raises(JobFault) as denied:
        with store._transaction(hook):
            assert admission.transaction.reply is reply
    assert denied.value.code == "PERMISSION_DENIED"
    assert reply.work == work and admission.retained == [] and admission.active is None
    if change == "replacement":
        assert host.current.request_id == successor["id"] and host.current.work == work
        host.finish_reply(successor["id"], emitted=True)
    host.finish_reply(original["id"], emitted=True)
    assert (original["id"] in host.replies) is (change == "unknown")


def test_original_background_scope_never_borrows_new_foreground(owned):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    host, admission = actor.mainline, store._read_admission
    successor = frame(actor, "project.read", {"projectId": project, "editor": "ontology"})
    original_work = []

    def hook(phase):
        if phase == "before_commit":
            host.begin(successor)
            original_work.append(host.current.work)

    with store._transaction(hook):
        admission.mark_controlled()
        token = admission.transaction
        assert token.reply is None
    assert host.current.work == original_work[0]
    assert token.holding.scalar > 0 and token.charged is None
    assert admission.active is None and admission.retained == []
    host.finish_reply(successor["id"], emitted=True)


def test_after_commit_reentry_cannot_refund_unknown_outer_writer(owned):
    actor, store = owned
    create(actor)
    admission = store._read_admission

    def hook(phase):
        if phase == "after_commit":
            with pytest.raises(JobFault) as denied:
                with store._transaction():
                    pass
            assert denied.value.code == "INVALID_STATE"
            raise RuntimeError("unknown after-commit fixture")

    with pytest.raises(RuntimeError, match="unknown after-commit fixture"):
        with store._transaction(hook):
            admission.mark_controlled()
    assert actor.mainline.hold and len(admission.retained) == 1
    assert admission.retained[0].scalar > 0 and admission.transaction is None


def test_cleanup_failure_preserves_original_cause_and_holding(owned, monkeypatch):
    actor, store = owned
    create(actor)
    admission = store._read_admission
    original = RuntimeError("original unknown")

    def hook(phase):
        if phase == "after_commit":
            raise original

    def broken_cleanup(*args):
        raise JobFault("INVALID_STATE")

    monkeypatch.setattr(admission, "completed", broken_cleanup)
    with pytest.raises(RuntimeError) as caught:
        with store._transaction(hook):
            admission.mark_controlled()
    assert caught.value is original and admission.transaction.holding is admission.retained[0]
    assert actor.mainline.hold and store._cleanup_failures[-1][0] == "writeAdmission"


@pytest.mark.parametrize("primary", ["known", "success"])
def test_settlement_failure_keeps_exact_foreground_reply_unknown(owned, monkeypatch, primary):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    admission = store._read_admission
    completed = admission.completed
    operation = uid()

    def broken_after_completion(token, error):
        completed(token, error)
        raise RuntimeError("unknown settlement after shared fields cleared")

    monkeypatch.setattr(admission, "completed", broken_after_completion)
    if primary == "known":

        def refuse_application(*args, **kwargs):
            raise JobFault("RESOURCE_LIMIT", {"resource": "page"})

        monkeypatch.setattr(store, "apply_application", refuse_application)
    result = exchange(
        actor,
        "project.draft.save",
        {
            "projectId": project,
            "operationId": operation,
            "editor": "ontology",
            "expectedGeneration": 0,
            "boundDomainRevision": 0,
            "contentJson": canonical({"note": "settlement fixture"}),
        },
    )
    assert not result["ok"]
    assert result["error"]["code"] == ("RESOURCE_LIMIT" if primary == "known" else "INTERNAL_ERROR")
    assert actor.mainline.hold and len(actor.mainline.replies) == 1
    held = next(iter(actor.mainline.replies.values()))
    assert held.unknown and admission.transaction.reply is held
    assert admission.transaction is not None
    # Unknown cleanup after COMMIT does not imply rollback. Inspect this same
    # Store directly; HOLD must not be cleared to obtain a new RPC authority.
    assert store.has_operation_claim(operation) is (primary == "success")


def test_same_store_dto_cannot_bind_or_supply_budget(tmp_path):
    store = JobStore(tmp_path / "binding.sqlite", contract=CONTRACT, target_format=3)
    try:
        admission = prepare_mainline_store(store)
        with pytest.raises(JobFault) as denied:
            admission.bind(SimpleNamespace(store=store, reserve=lambda *args: None))
        assert denied.value.code == "PERMISSION_DENIED" and admission.owner is None
    finally:
        store.close()


@pytest.mark.parametrize("unfinished", [False, True])
def test_bootstrap_unsettled_writer_cannot_be_adopted_as_clean(tmp_path, unfinished):
    store = JobStore(tmp_path / "bootstrap-unsettled.sqlite", contract=CONTRACT, target_format=3)
    admission = prepare_mainline_store(store)
    transaction = None
    try:
        if unfinished:
            transaction = store._transaction()
            transaction.__enter__()
        else:

            def fail_after_commit(phase):
                if phase == "after_commit":
                    raise RuntimeError("original bootstrap uncertainty")

            with pytest.raises(RuntimeError, match="original bootstrap uncertainty"):
                with store._transaction(fail_after_commit):
                    pass
            assert admission.retained
        original = (tuple(admission.retained), admission.transaction, admission.active)
        with pytest.raises(JobFault) as denied:
            Coordinator(store, profile="business3", _ready=_JOB_READY)
        assert denied.value.code == "PERMISSION_DENIED"
        assert store._read_admission is admission and admission.owner is None
        assert (tuple(admission.retained), admission.transaction, admission.active) == original
    finally:
        if transaction is not None:
            transaction.__exit__(None, None, None)
        store.close()


def test_clean_close_hands_original_restriction_to_real_successor(owned):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    previous, admission = actor.mainline, store._read_admission
    params = {"projectId": project, "baseRevision": 0, "intent": "change", "plan": {}}
    request = frame(actor, "changeset.preview", params)
    previous.begin(request)
    proof = previous.ownership_proof(params, method="changeset.preview")
    actor.finish_query_reply(request["id"], emitted=True)
    identity = (previous.owner_id, previous.host, previous.session)
    connection, lease = store._db, store._format3_lease
    previous.close()
    successor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    try:
        host = successor.mainline
        assert store._read_admission is admission and admission.owner is host
        assert store._db is connection and store._format3_lease is lease
        assert host is not previous and host.owner_id != identity[0]
        assert host.host is None and host.session is None and host.selected is None
        assert host.generation == 0 and not host.replies and not admission.retained
        assert exchange(successor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
        assert host.host != identity[1] and host.session != identity[2]
        with pytest.raises(JobFault) as denied:
            proof.check(store, project)
        assert denied.value.code == "PERMISSION_DENIED"
        assert exchange(successor, "project.open", {"projectId": project})["ok"]
        saved = exchange(
            successor,
            "project.draft.save",
            {
                "projectId": project,
                "operationId": uid(),
                "editor": "ontology",
                "expectedGeneration": 0,
                "boundDomainRevision": 0,
                "contentJson": canonical({"note": "real successor"}),
            },
        )
        assert saved["ok"], saved
        assert exchange(successor, "project.read", {"projectId": project, "editor": "ontology"})[
            "ok"
        ]
        assert admission.owner is host and not host.hold
    finally:
        successor.mainline.close()


@pytest.mark.parametrize(
    "state",
    [
        "live",
        "current",
        "unknown",
        "hold",
        "retained",
        "unfinished",
        "close-failure",
        "query-reply",
    ],
)
def test_successor_never_discards_unsettled_predecessor(owned, monkeypatch, state):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    host, admission = actor.mainline, store._read_admission
    transaction = None
    if state in {"current", "unknown"}:
        request = frame(actor, "project.read", {"projectId": project, "editor": "ontology"})
        host.begin(request)
        if state == "unknown":
            actor.finish_query_reply(request["id"], emitted=False)
    elif state == "query-reply":
        request = frame(actor, "project.get", {"projectId": project})
        assert actor.request(request)["ok"]
        assert actor._query_replies and host.replies
    elif state == "hold":
        with pytest.raises(JobFault):
            host._host_fault(HostReadFault("structure"))
    elif state == "retained":

        def fail_after_commit(phase):
            if phase == "after_commit":
                raise RuntimeError("original background uncertainty")

        with pytest.raises(RuntimeError, match="original background uncertainty"):
            with store._transaction(fail_after_commit):
                admission.mark_controlled()
        assert host.hold and admission.retained
    elif state == "unfinished":
        transaction = store._transaction()
        transaction.__enter__()
        admission.mark_controlled()
    elif state == "close-failure":
        original_close = host.reader.close

        def broken_close():
            raise RuntimeError("original reader close failure")

        monkeypatch.setattr(host.reader, "close", broken_close)
        with pytest.raises(RuntimeError, match="original reader close failure"):
            host.close()
        assert not host._clean_close
        monkeypatch.setattr(host.reader, "close", original_close)
    if state not in {"live", "close-failure"}:
        host.close()
    original = (
        tuple(host.replies.items()),
        tuple(admission.retained),
        admission.transaction,
        host.hold,
    )
    try:
        with pytest.raises(JobFault) as denied:
            Coordinator(store, profile="business3", _ready=_JOB_READY)
        assert denied.value.code == "PERMISSION_DENIED"
        assert store._read_admission is admission and admission.owner is host
        assert (
            tuple(host.replies.items()),
            tuple(admission.retained),
            admission.transaction,
            host.hold,
        ) == original
    finally:
        if transaction is not None:
            transaction.__exit__(None, None, None)


@pytest.mark.parametrize("launched", [False, True])
def test_successor_cannot_take_original_queued_or_active_job(owned, launched):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    accepted = confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": 0,
            "intent": "change",
            "plan": {"manual": [fact('"original queued responsibility"')]},
        },
    )
    host, admission = actor.mainline, store._read_admission

    async def check():
        if launched:
            await actor.tick()
            assert actor.tasks and actor.active and not actor.queued
        else:
            assert actor.queued and not actor.tasks
        host.close()
        with pytest.raises(JobFault) as denied:
            Coordinator(store, profile="business3", _ready=_JOB_READY)
        assert denied.value.code == "PERMISSION_DENIED"
        assert admission.owner is host and store._read_admission is admission
        if not launched:
            await actor.tick()
        await asyncio.gather(*tuple(actor.tasks))

    asyncio.run(check())
    assert store.get_job(project, accepted["jobId"])["state"] == "succeeded"


@asynccontextmanager
async def wire_host(database, directory):
    env = {**os.environ, "ONTOLEARN_DB_PATH": str(database)}
    env.pop("ONTOLEARN_TEST_MODE", None)
    env.pop("ONTOLEARN_ALLOWED_PROJECTS", None)
    child = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "ontolearn_engine",
        "--t01-internal-profile=business3",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    session, wire = None, []

    async def call(method, params):
        nonlocal session
        request = {
            "kind": "request",
            "id": uid(),
            "method": method,
            "params": params,
            "protocolVersion": 2 if method == "hello" else 3,
            "engineSessionId": session,
        }
        wire.append({"sent": request, "pid": child.pid})
        child.stdin.write((json.dumps(request) + "\n").encode())
        await child.stdin.drain()
        while True:
            raw = await asyncio.wait_for(child.stdout.readline(), 10)
            assert raw, child.returncode
            reply = json.loads(raw)
            wire.append({"received": reply, "pid": child.pid})
            if reply.get("id") == request["id"]:
                if session is not None:
                    assert reply["engineSessionId"] == session
                if method == "hello":
                    assert reply["ok"], reply
                    session = reply["result"]["engineSessionId"]
                assert child.returncode is None
                return reply

    try:
        await call("hello", {"supportedVersions": [3], "clientId": uid()})
        yield call
    finally:
        child.stdin.close()
        forced = False
        try:
            await asyncio.wait_for(child.wait(), 10)
        finally:
            if child.returncode is None:
                forced = True
                child.kill()
                await child.wait()
            (directory / "postwrite-wire.json").write_text(json.dumps(wire), encoding="utf-8")
            (directory / "postwrite-exit.json").write_text(
                json.dumps({"pid": child.pid, "returnCode": child.returncode, "forced": forced}),
                encoding="utf-8",
            )
            (directory / "postwrite-stderr.txt").write_bytes(await child.stderr.read())
        assert child.returncode == 0 and not forced


async def wire_commit(call, project, value):
    async def ok(method, params):
        reply = await call(method, params)
        assert reply["ok"], reply
        return reply["result"]

    preview = await ok(
        "changeset.preview",
        {
            "projectId": project,
            "baseRevision": 0,
            "intent": "change",
            "plan": {"manual": [fact(value)]},
        },
    )
    cursor, raw = None, b""
    for _ in range(512):
        page = await ok(
            "changeset.diff.page",
            {
                "projectId": project,
                "previewHash": preview["previewHash"],
                "documentKind": "diff",
                "pageSize": 1,
                "cursor": cursor,
            },
        )
        for part in page["segments"]:
            chunk = base64.b64decode(part["dataBase64"], validate=True)
            assert hashlib.sha256(chunk).hexdigest() == part["sha256"]
            assert part["byteOffset"] == len(raw) and len(chunk) == part["rawByteLength"]
            raw += chunk
        cursor = page["nextCursor"]
        if page["complete"]:
            break
    assert page["complete"] and len(raw) == preview["manifest"]["totalBytes"]
    assert hashlib.sha256(raw).hexdigest() == preview["manifest"]["documentHash"]
    assert json.loads(raw)[0]["after"]["object"] == value
    confirmation = await ok(
        "changeset.confirm",
        {"projectId": project, "previewHash": preview["previewHash"], "completionCursor": cursor},
    )
    request = job_request(project, uid(), confirmation)
    job = await ok("job.create", request)
    end = asyncio.get_running_loop().time() + 10
    while job["state"] in {"queued", "running", "cancelling"}:
        assert asyncio.get_running_loop().time() < end
        await asyncio.sleep(0.01)
        job = await ok("job.get", {"projectId": project, "jobId": job["jobId"]})
    assert job["state"] == "succeeded", job
    marker = await ok("operation.get", {"projectId": project, "operationId": job["operationId"]})
    assert marker["jobId"] == job["jobId"]


def test_real_stdio_growth_refusal_and_same_host_full_commit(tmp_path):
    async def run():
        async with wire_host(tmp_path / "stdio.sqlite", tmp_path) as call:
            created = await call(
                "project.create",
                {
                    "requestVersion": 1,
                    "operationId": uid(),
                    "name": "stdio postwrite guard",
                    "initialization": {"kind": "blank"},
                },
            )
            assert created["ok"], created
            project = created["result"]["projectId"]
            for index in range(32):
                before = await call("project.read", {"projectId": project, "editor": "ontology"})
                assert before["ok"], before
                saved = await call(
                    "project.draft.save",
                    {
                        "projectId": project,
                        "operationId": uid(),
                        "editor": "ontology",
                        "expectedGeneration": before["result"]["workspace"]["draft"].get(
                            "generation", 0
                        ),
                        "boundDomainRevision": 0,
                        "contentJson": canonical({"note": str(index) + "x" * 12000}),
                    },
                )
                after = await call("project.read", {"projectId": project, "editor": "ontology"})
                assert after["ok"], after
                if not saved["ok"]:
                    assert saved["error"]["code"] == "RESOURCE_LIMIT", saved
                    assert after["result"] == before["result"]
                    break
            else:
                pytest.fail("Expected controlled bounded growth refusal")
            await wire_commit(call, project, '"stdio legal follow-up"')
            final = await call("project.read", {"projectId": project, "editor": "ontology"})
            assert final["ok"] and final["result"]["domain"]["projectRevision"] == 1

    asyncio.run(run())


def test_real_stdio_bootstrap_reconciles_original_accepted_job_with_guard(tmp_path):
    database = tmp_path / "bootstrap.sqlite"
    store = JobStore(database, contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    try:
        assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
        project = create(actor)[0]["projectId"]
        accepted = confirmed_job(
            actor,
            project,
            {
                "projectId": project,
                "baseRevision": 0,
                "intent": "change",
                "plan": {"manual": [fact('"not executed before restart"')]},
            },
        )
    finally:
        actor.mainline.close()
        store.close()

    async def run():
        async with wire_host(database, tmp_path) as call:
            assert (await call("project.open", {"projectId": project}))["ok"]
            reply = await call("job.get", {"projectId": project, "jobId": accepted["jobId"]})
            assert reply["ok"] and reply["result"]["state"] == "failed", reply
            assert reply["result"]["error"]["code"] == "ENGINE_EXITED"
            marker = await call(
                "operation.get", {"projectId": project, "operationId": accepted["operationId"]}
            )
            assert marker["ok"] and marker["result"] is None
            assert (await call("project.read", {"projectId": project, "editor": "ontology"}))["ok"]

    asyncio.run(run())
