"""Core read accounting over real owned histories, without changing any production cap."""

import asyncio
import json
import os
import sqlite3
import sys
from contextlib import asynccontextmanager

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project.mainline import READ_LIMITS
from ontolearn_engine.project.project_host import HostReadFault, ProjectHostReader
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import canonical, digest
from test_mainline_dispatch import (
    _confirmed_application_claim,
    confirmed_job,
    create,
    drain_owned_changesets,
    exchange,
    uid,
)
from test_mainline_dispatch import owned as owned
from test_mainline_query_changeset import diff_pages

SUBJECT, PREDICATE = "urn:work:subject", "urn:work:value"


def scalar_profile(store):
    """Same full-column byte units as preflight; only this test's owned database."""
    tables = {}
    plan_sizes = None
    for (name,) in store._db.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        quoted = '"' + name.replace('"', '""') + '"'
        columns = store._db.execute(f"PRAGMA table_info({quoted})").fetchall()
        sizes = "+".join(
            'coalesce(length(CAST("' + row[1].replace('"', '""') + '" AS BLOB)),0)'
            for row in columns
        )
        count, size = store._db.execute(
            f"SELECT count(*),coalesce(sum({sizes}),0) FROM {quoted}"
        ).fetchone()
        tables[name] = {"rows": count, "bytes": size}
        if name == "job_plans":
            plan_sizes = sizes
    plans = store._db.execute(
        f"SELECT coalesce(sum({plan_sizes}),0) FROM job_plans WHERE ref IN ("
        "SELECT CASE WHEN json_valid(context) THEN "
        "json_extract(context,'$.request.authorization.preparedPlanRef') END "
        "FROM operation_claims WHERE kind='application')"
    ).fetchone()[0]
    scan = sum(row["bytes"] for row in tables.values())
    decoded = scan - tables["job_blobs"]["bytes"] - tables["job_plans"]["bytes"]
    repeats = tables["app_operations"]["rows"] + tables["snapshots"]["rows"]
    return {"tables": tables, "scan": scan, "decoded": decoded, "plans": plans, "repeats": repeats}


def prepare(actor, project, base, plan):
    response = exchange(
        actor,
        "changeset.preview",
        {"projectId": project, "baseRevision": base, "intent": "change", "plan": plan},
    )
    assert response["ok"] and response["result"]["status"] == "ready", response
    ready = response["result"]
    cursor, _ = diff_pages(actor, project, ready)
    confirmed = exchange(
        actor,
        "changeset.confirm",
        {"projectId": project, "previewHash": ready["previewHash"], "completionCursor": cursor},
    )
    assert confirmed["ok"], confirmed
    return confirmed["result"]


def job_request(project, operation, confirmation):
    return {
        "projectId": project,
        "operationId": operation,
        "capability": "changeset.commit",
        "confirmationRef": confirmation["confirmationRef"],
        "input": {
            "inputSnapshotId": confirmation["inputSnapshotId"],
            "scope": "asserted",
            "definitionId": "changeset",
            "parametersHash": confirmation["parametersHash"],
            "derivedResultIds": [],
            "preparedPlanRef": confirmation["preparedPlanRef"],
        },
    }


def bookmark(actor, project, generation, revision, pending):
    response = exchange(
        actor,
        "project.draft.save",
        {
            "projectId": project,
            "operationId": uid(),
            "editor": "ontology-transaction",
            "expectedGeneration": generation,
            "boundDomainRevision": revision,
            "contentJson": canonical({"pending": pending}),
        },
    )
    assert response["ok"], response


def history_and_opaque(actor, store):
    created, _ = create(actor, "owned history accounting")
    project = created["projectId"]
    fact_id = digest([SUBJECT, PREDICATE, '"value0"'])
    for index in range(21):
        plan = (
            {
                "manual": [
                    {
                        "id": fact_id,
                        "subject": SUBJECT,
                        "predicate": PREDICATE,
                        "object": '"value0"',
                    }
                ]
            }
            if index == 0
            else {"edits": {fact_id: f'"value{index}"'}}
        )
        accepted = confirmed_job(
            actor,
            project,
            {"projectId": project, "baseRevision": index, "intent": "change", "plan": plan},
        )
        drain_owned_changesets(actor)
        assert store.get_job(project, accepted["jobId"])["state"] == "succeeded"
        bookmark(actor, project, index, index + 1, {"operationId": accepted["operationId"]})
    confirmation = prepare(actor, project, 21, {"remove": [fact_id]})
    bookmark(actor, project, 21, 21, {"operationId": uid(), "confirmation": confirmation})
    # Only fixture setup adds opaque interned data. It grants no new authority,
    # does not replace history, and is never decoded by the core reader.
    for index in range(16):
        profile = scalar_profile(store)
        if profile["scan"] * (1 + profile["repeats"]) > READ_LIMITS.validation_work:
            break
        store.put_blob(project, {"opaque": str(index) + "x" * 200000})
    else:
        pytest.fail("Fixture did not reach the original work boundary")
    profile = scalar_profile(store)
    assert (
        profile["tables"]["app_operations"]["rows"],
        profile["tables"]["snapshots"]["rows"],
    ) == (44, 22)
    assert profile["scan"] * (1 + profile["repeats"]) > 67108864
    assert (
        2 * profile["scan"] + (profile["decoded"] + profile["plans"]) * profile["repeats"]
        < 67108864
    )
    return project, fact_id, confirmation, profile


def test_core_same_host_reads_then_last_remove_job_marker_and_after_read(
    owned, monkeypatch, tmp_path
):
    actor, store = owned
    project, fact_id, confirmation, profile = history_and_opaque(actor, store)
    host = actor.mainline
    identity = (host.owner_id, host.host, host.session, host.generation)
    called = []
    original = host.reader._validate

    def validate():
        called.append(True)
        return original()

    monkeypatch.setattr(host.reader, "_validate", validate)
    before = digest(list(store._db.iterdump()))
    active = exchange(actor, "project.get", {"projectId": project})
    (tmp_path / "initial-read-trace.json").write_text(
        json.dumps({"profile": profile, "active": active})
    )
    assert active["ok"] and active["result"]["projectRevision"] == 21, canonical(active)
    read = exchange(actor, "project.read", {"projectId": project, "editor": "ontology-transaction"})
    assert read["ok"] and read["result"]["workspace"]["draft"]["generation"] == 22, read
    assert called and digest(list(store._db.iterdump())) == before
    assert (host.owner_id, host.host, host.session, host.generation) == identity
    with pytest.raises(HostReadFault) as denied:
        ProjectHostReader(store, limits=READ_LIMITS).workspace(
            project, editor="ontology-transaction"
        )
    assert denied.value.reason == "limit"  # Default keeps its original all-table formula.
    operation = uid()
    accepted = exchange(actor, "job.create", job_request(project, operation, confirmation))
    assert accepted["ok"], accepted
    drain_owned_changesets(actor)
    job = store.get_job(project, accepted["result"]["jobId"])
    assert job["state"] == "succeeded", job
    marker = exchange(actor, "operation.get", {"projectId": project, "operationId": operation})
    assert marker["ok"] and marker["result"]["jobId"] == job["jobId"]
    after = exchange(
        actor, "project.read", {"projectId": project, "editor": "ontology-transaction"}
    )
    assert after["ok"] and after["result"]["domain"]["projectRevision"] == 22, after
    assert after["result"]["domain"]["state"]["facts"] == []
    assert actor.mainline is host and not host.hold and host.replies == {}
    (tmp_path / "history-read-trace.json").write_text(
        json.dumps(
            {
                "profile": profile,
                "active": active,
                "beforeRead": read,
                "job": job,
                "marker": marker,
                "afterRead": after,
                "removedOriginalId": fact_id,
            }
        )
    )


@asynccontextmanager
async def stdio(database, trace_path):
    env = {**os.environ, "ONTOLEARN_DB_PATH": str(database)}
    env.pop("ONTOLEARN_TEST_MODE", None)
    env.pop("ONTOLEARN_ALLOWED_PROJECTS", None)
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "ontolearn_engine",
        "--t01-internal-profile=business3",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    wire, session = [], None

    async def call(method, params):
        nonlocal session
        request = {
            "kind": "request",
            "id": uid(),
            "protocolVersion": 2 if method == "hello" else 3,
            "engineSessionId": session,
            "method": method,
            "params": params,
        }
        wire.append({"sent": request})
        process.stdin.write((json.dumps(request) + "\n").encode())
        await process.stdin.drain()
        while True:
            raw = await asyncio.wait_for(process.stdout.readline(), 10)
            assert raw, f"stdio EOF: {process.returncode}"
            response = json.loads(raw)
            wire.append({"received": response})
            if response.get("id") == request["id"]:
                if session is not None:
                    assert response["engineSessionId"] == session
                assert response["ok"], canonical(response)
                if method == "hello":
                    session = response["result"]["engineSessionId"]
                return response["result"]

    try:
        await call("hello", {"supportedVersions": [3], "clientId": uid()})
        yield call
    finally:
        process.stdin.close()
        try:
            await asyncio.wait_for(process.wait(), 10)
        finally:
            if process.returncode is None:
                process.kill()
                await process.wait()
            trace_path.write_text(json.dumps(wire, ensure_ascii=False))
    assert process.returncode == 0, (await process.stderr.read()).decode()


def test_real_stdio_core_history_bookmark_current_remove_and_after_read(tmp_path):
    database = tmp_path / "owned-stdio.sqlite"
    store = JobStore(database, contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
    try:
        project, fact_id, _, _ = history_and_opaque(actor, store)
    finally:
        actor.mainline.close()
        store.close()

    # The sole stdio host starts from a fully valid fixture. No host is replaced
    # after a refusal, and old confirmations are not replayed into this session.
    async def run():
        async with stdio(database, tmp_path / "stdio-wire.json") as call:
            await call("project.open", {"projectId": project})
            await call("project.get", {"projectId": project})
            ready = await call(
                "changeset.preview",
                {
                    "projectId": project,
                    "baseRevision": 21,
                    "intent": "change",
                    "plan": {"remove": [fact_id]},
                },
            )
            cursor = None
            while True:
                page = await call(
                    "changeset.diff.page",
                    {
                        "projectId": project,
                        "previewHash": ready["previewHash"],
                        "documentKind": "diff",
                        "pageSize": 1,
                        "cursor": cursor,
                    },
                )
                cursor = page["nextCursor"]
                if page["complete"]:
                    break
            confirmation = await call(
                "changeset.confirm",
                {
                    "projectId": project,
                    "previewHash": ready["previewHash"],
                    "completionCursor": cursor,
                },
            )
            operation = uid()
            await call(
                "project.draft.save",
                {
                    "projectId": project,
                    "operationId": uid(),
                    "editor": "ontology-transaction",
                    "expectedGeneration": 22,
                    "boundDomainRevision": 21,
                    "contentJson": canonical(
                        {"pending": {"operationId": operation, "confirmation": confirmation}}
                    ),
                },
            )
            await call("project.get", {"projectId": project})  # Actual post-bookmark current sync.
            job = await call("job.create", job_request(project, operation, confirmation))
            deadline = asyncio.get_running_loop().time() + 10
            while job["state"] in {"queued", "running", "cancelling"}:
                assert asyncio.get_running_loop().time() < deadline, job
                await asyncio.sleep(0.01)
                job = await call("job.get", {"projectId": project, "jobId": job["jobId"]})
            assert job["state"] == "succeeded", job
            marker = await call("operation.get", {"projectId": project, "operationId": operation})
            assert marker["jobId"] == job["jobId"]
            after = await call(
                "project.read", {"projectId": project, "editor": "ontology-transaction"}
            )
            assert (
                after["domain"]["projectRevision"] == 22 and after["domain"]["state"]["facts"] == []
            )

    asyncio.run(run())


def pad_scan_to(store, project, target):
    """Fixture-only opaque bytes, measured whole-row; no production limit override."""
    scan = scalar_profile(store)["scan"]
    index = 0
    while scan < target:
        value = {"padding": str(index) + ":"}
        overhead = len(project.encode()) + 64 + len(canonical(value).encode())
        value["padding"] += "x" * min(240000, max(0, target - scan - overhead))
        ref = store.put_blob(project, value)
        row = store._db.execute(
            "SELECT length(CAST(project AS BLOB))+length(CAST(ref AS BLOB))"
            "+length(CAST(payload AS BLOB)) FROM job_blobs WHERE project=? AND ref=?",
            (project, ref),
        ).fetchone()
        scan += row[0]
        index += 1
    result = scalar_profile(store)
    assert result["scan"] == scan
    return result


@pytest.mark.parametrize("stage", ["lower", "authorized-plan"])
def test_original_64mib_work_limit_rejects_before_validation_at_both_stages(
    owned, monkeypatch, stage, tmp_path
):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    _confirmed_application_claim(actor, store, project)
    initial = scalar_profile(store)
    assert initial["plans"] > 0 and initial["repeats"] > 0
    # At most two bytes below the cap for the final-plan case; adding P*H must
    # cross the original cap. The lower-bound case crosses before querying P.
    target = (67108864 - initial["decoded"] * initial["repeats"]) // 2
    profile = pad_scan_to(store, project, target + (1 if stage == "lower" else 0))
    lower = 2 * profile["scan"] + profile["decoded"] * profile["repeats"]
    assert (lower > 67108864) == (stage == "lower")
    assert lower + profile["plans"] * profile["repeats"] > 67108864
    assert profile["decoded"] + profile["plans"] < 1572864
    trace, validations = [], []
    original = actor.mainline.reader._validate

    def validate():
        validations.append(True)
        return original()

    monkeypatch.setattr(actor.mainline.reader, "_validate", validate)
    store._db.set_trace_callback(trace.append)
    try:
        refused = exchange(actor, "project.get", {"projectId": project})
    finally:
        store._db.set_trace_callback(None)
    assert not refused["ok"] and refused["error"]["code"] == "RESOURCE_LIMIT", refused
    assert refused["error"]["params"] == {"resource": "page"}
    assert any("json_extract" in sql.lower() for sql in trace) == (stage == "authorized-plan")
    assert not validations and not actor.mainline.hold and actor.mainline.replies == {}
    (tmp_path / "work-limit-trace.json").write_text(
        json.dumps({"profile": profile, "lower": lower, "response": refused, "sql": trace})
    )


def damage_row(store, table, key, identity, column, payload):
    assert (table, key, column) in {
        ("job_plans", "ref", "payload"),
        ("operation_claims", "operation", "context"),
        ("snapshots", "id", "payload"),
        ("app_checkpoints", "id", "payload"),
    }
    name = "immutable_" + table + "_UPDATE"
    trigger = store._db.execute("SELECT sql FROM sqlite_master WHERE name=?", (name,)).fetchone()[0]
    with store._transaction():
        store._db.execute("DROP TRIGGER " + name)
        store._db.execute(f"UPDATE {table} SET {column}=? WHERE {key}=?", (payload, identity))
        store._db.execute(trigger)


def test_real_repeated_decoded_history_remains_bounded_before_plan_selector(owned, tmp_path):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    # Build valid private-fixture history with the real Store transition/CAS
    # path, without passing a core read that would refuse the final bound.
    first_version = store._db.execute(
        "SELECT metadata_version FROM app_projects WHERE project=?", (store._project(project),)
    ).fetchone()[0]
    for version in range(128):
        store.apply_application(
            project,
            uid(),
            {
                "type": "metadata",
                "expectedVersion": first_version + version,
                "patch": {"name": str(version) + "x" * 3000},
            },
            actor=actor.host_client_id,
            permission="write",
        )
        profile = scalar_profile(store)
        if profile["decoded"] * profile["repeats"] > 67108864:
            break
    else:
        pytest.fail("Real decoded history did not cross the original work cap")
    assert profile["decoded"] < 1572864 and profile["plans"] == 0
    trace = []
    store._db.set_trace_callback(trace.append)
    try:
        refused = exchange(actor, "project.get", {"projectId": project})
    finally:
        store._db.set_trace_callback(None)
    assert not refused["ok"] and refused["error"]["code"] == "RESOURCE_LIMIT", refused
    assert refused["error"]["params"] == {"resource": "page"}
    assert not any("json_extract" in sql.lower() for sql in trace)
    assert not actor.mainline.hold
    (tmp_path / "decoded-limit-trace.json").write_text(
        json.dumps({"profile": profile, "response": refused})
    )


@pytest.mark.parametrize(
    "damaged", ["context", "plan", "snapshot", "checkpoint", "repeated-ref", "cross-project"]
)
def test_core_admission_still_runs_full_authentication_and_holds_corruption(
    owned, monkeypatch, damaged, tmp_path
):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    operation, prepared = _confirmed_application_claim(actor, store, project)
    if damaged in {"context", "plan"}:
        table, key, identity, column, payload = (
            ("operation_claims", "operation", operation, "context", "{")
            if damaged == "context"
            else ("job_plans", "ref", prepared["preparedPlanRef"], "payload", "{}")
        )
    elif damaged in {"snapshot", "checkpoint"}:
        table = "snapshots" if damaged == "snapshot" else "app_checkpoints"
        identity = store._db.execute(f"SELECT id FROM {table} LIMIT 1").fetchone()[0]
        key, column, payload = "id", "payload", "{}"
    else:
        other = project if damaged == "repeated-ref" else create(actor)[0]["projectId"]
        second, _ = _confirmed_application_claim(actor, store, other)
        context = json.loads(
            store._db.execute(
                "SELECT context FROM operation_claims WHERE operation=?", (second,)
            ).fetchone()[0]
        )
        context["request"]["authorization"] = {
            "preparedPlanRef": prepared["preparedPlanRef"],
            "confirmationRef": prepared["confirmationRef"],
        }
        table, key, identity, column, payload = (
            "operation_claims",
            "operation",
            second,
            "context",
            canonical(context),
        )
        assert exchange(actor, "project.open", {"projectId": project})["ok"]
    damage_row(store, table, key, identity, column, payload)
    profile = scalar_profile(store)
    if damaged in {"repeated-ref", "cross-project"}:
        # IN deduplicates the repeated reference even across project claims;
        # selector membership is never accepted as authorization proof.
        assert profile["plans"] > 0
        assert profile["tables"]["job_plans"]["bytes"] > profile["plans"]
    before = digest(list(store._db.iterdump()))
    validations = []
    original = actor.mainline.reader._validate

    def validate():
        validations.append(True)
        return original()

    monkeypatch.setattr(actor.mainline.reader, "_validate", validate)
    refused = exchange(actor, "project.get", {"projectId": project})
    assert not refused["ok"] and refused["error"]["code"] == "STORAGE_FAILURE", refused
    assert validations and actor.mainline.hold and not actor.mainline.enabled()
    assert digest(list(store._db.iterdump())) == before
    assert exchange(actor, "health", {})["ok"]
    (tmp_path / "corruption-trace.json").write_text(
        json.dumps({"damaged": damaged, "response": refused, "held": actor.mainline.hold})
    )


def test_authorized_plan_sql_failure_has_no_zero_fallback_and_holds(owned):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    _confirmed_application_claim(actor, store, project)

    def deny_selector(action, first, second, database, source):
        if action == sqlite3.SQLITE_FUNCTION and second == "json_extract":
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    store._db.set_authorizer(deny_selector)
    try:
        refused = exchange(actor, "project.get", {"projectId": project})
    finally:
        store._db.set_authorizer(None)
    assert not refused["ok"] and refused["error"]["code"] == "STORAGE_FAILURE", refused
    assert actor.mainline.hold and not actor.mainline.enabled()
