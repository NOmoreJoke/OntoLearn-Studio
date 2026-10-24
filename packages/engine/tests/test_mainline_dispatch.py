"""Real owned-Store/Coordinator definitions; no executed-check claim in SOURCE delivery.

No semantic provider, worker, permission issuer or SQLite read is mocked. The
delivery-failure case explicitly injects only the sender's terminal observation.
"""

import asyncio
import base64
import json
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.project.mainline import HELD_BYTES
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import canonical, digest


def uid():
    return str(uuid4())


def frame(actor, method, params):
    return {
        "kind": "request",
        "id": uid(),
        "protocolVersion": 2 if method == "hello" else 3,
        "engineSessionId": None if method == "hello" else actor.session,
        "method": method,
        "params": params,
    }


def exchange(actor, method, params):
    request = frame(actor, method, params)
    response = actor.request(request)
    # In production serve serializes/emits and drops its response alias before
    # finish. This direct test consumer keeps the returned wire data for asserts.
    actor.finish_query_reply(request["id"], emitted=True)
    return response


@pytest.fixture
def owned(tmp_path):
    store = JobStore(tmp_path / "mainline.sqlite", contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    hello = exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})
    assert hello["ok"], hello
    assert {"project.catalog", "project.create", "project.open", "project.read"} <= set(
        hello["result"]["capabilities"]
    )
    assert "ordinary.library" not in hello["result"]["capabilities"]
    yield actor, store
    actor.mainline.close()
    store.close()


def ownership_fixture(actor, store, *, large=False, managed=False):
    project = create(actor)[0]["projectId"]
    subject = "urn:ownership:" + ("x" * 40000 if large and not managed else "subject")
    record = {
        "id": digest([subject, "urn:ownership:value", '"A"']),
        "subject": subject,
        "predicate": "urn:ownership:value",
        "object": '"A"',
    }
    if managed:
        store.commit(
            store._project(project),
            0,
            uid(),
            uid(),
            definitions=[{"layer": "mapping", "id": "M1", "value": {}}],
            mapping={
                "id": "M1",
                "rows": [{"row": "original-row-" + "x" * 40000, "facts": [record]}],
            },
        )
        base = 1
    else:
        confirmed_job(
            actor,
            project,
            {
                "projectId": project,
                "baseRevision": 0,
                "intent": "change",
                "plan": {"manual": [record]},
            },
        )
        drain_owned_changesets(actor)
        confirmed_job(
            actor,
            project,
            {
                "projectId": project,
                "baseRevision": 1,
                "intent": "change",
                "plan": {"edits": {record["id"]: '"B"'}},
            },
        )
        drain_owned_changesets(actor)
        base = 2
    params = {
        "projectId": project,
        "baseRevision": base,
        "intent": "change",
        "plan": {"manual": [record]},
    }
    return project, record, params


def ownership_pages(actor, project, ref, *, page_size=1):
    import hashlib

    ordinal, expected, pages, parts = 0, None, [], []
    while True:
        response = exchange(
            actor,
            "project.ownership.detail",
            {
                "projectId": project,
                "detailRef": ref,
                "documentHash": expected,
                "startOrdinal": ordinal,
                "pageSize": page_size,
            },
        )
        assert response["ok"], response
        page = response["result"]
        pages.append(page)
        expected = page["manifest"]["documentHash"]
        for segment in page["segments"]:
            raw = base64.b64decode(segment["dataBase64"], validate=True)
            assert hashlib.sha256(raw).hexdigest() == segment["sha256"]
            parts.append(raw)
        if page["complete"]:
            break
        ordinal = page["nextOrdinal"]
    raw = b"".join(parts)
    assert len(raw) == page["manifest"]["totalBytes"]
    assert hashlib.sha256(raw).hexdigest() == expected
    return pages, json.loads(raw)


@pytest.mark.parametrize("managed", [False, True])
def test_ownership_large_locator_is_complete_pure_and_bound(owned, tmp_path, managed):
    actor, store = owned
    project, record, params = ownership_fixture(actor, store, large=True, managed=managed)
    before = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
    refused = exchange(actor, "changeset.preview", params)
    assert refused["error"]["code"] == "OWNERSHIP_CONFLICT", refused
    ref = refused["error"]["params"]["detailRef"]
    database = list(store._db.iterdump())
    pages, document = ownership_pages(actor, project, ref)
    assert len(pages) >= 2 and pages[0]["manifest"]["totalBytes"] > 32768
    assert document["existing"]["id"] == record["id"]
    assert document["existing"]["slot"]["subject"] == record["subject"]
    if managed:
        assert document["existing"]["owner"] == "M1"
        assert document["existing"]["sourceRow"] == "original-row-" + "x" * 40000
    assert list(store._db.iterdump()) == database  # Including no new cursor rows.
    header = pages[0]["manifest"]
    wrong = exchange(
        actor,
        "project.ownership.detail",
        {
            "projectId": project,
            "detailRef": ref,
            "documentHash": "f" * 64,
            "startOrdinal": 1,
            "pageSize": 1,
        },
    )
    assert not wrong["ok"] and wrong["error"]["code"] == "IDENTITY_CONFLICT"
    last = exchange(
        actor,
        "project.ownership.detail",
        {
            "projectId": project,
            "detailRef": ref,
            "documentHash": header["documentHash"],
            "startOrdinal": header["segmentCount"] - 1,
            "pageSize": 1,
        },
    )
    assert last["ok"] and last["result"]["complete"]  # End, not whole-document authority.
    assert not actor.mainline.hold
    after = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
    assert after["result"] == before["result"]
    accepted = confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": params["baseRevision"],
            "intent": "change",
            "plan": {
                "manual": [
                    {
                        **record,
                        "id": digest([record["subject"], record["predicate"], '"C"']),
                        "object": '"C"',
                    }
                ]
            },
        },
    )
    drain_owned_changesets(actor)
    assert store.get_job(project, accepted["jobId"])["state"] == "succeeded"
    marker = exchange(
        actor, "operation.get", {"projectId": project, "operationId": accepted["operationId"]}
    )
    assert marker["ok"] and marker["result"]["jobId"] == accepted["jobId"]
    other = create(actor)[0]["projectId"]
    denied = exchange(
        actor,
        "project.ownership.detail",
        {
            "projectId": other,
            "detailRef": ref,
            "documentHash": None,
            "startOrdinal": 0,
            "pageSize": 1,
        },
    )
    assert not denied["ok"] and denied["error"]["code"] == "NOT_FOUND"
    (tmp_path / "large-ownership-trace.json").write_text(
        json.dumps(
            {
                "managed": managed,
                "refused": refused,
                "pages": pages,
                "document": document,
                "wrongHash": wrong,
                "randomLast": last,
                "accepted": accepted,
                "marker": marker,
                "otherProject": denied,
            }
        )
    )


def damage_ownership_fixture(store, table, key, identity, payload):
    assert (table, key) in {("job_details", "id"), ("job_blobs", "ref")}
    name = "immutable_" + table + "_UPDATE"
    trigger = store._db.execute("SELECT sql FROM sqlite_master WHERE name=?", (name,)).fetchone()[0]
    with store._transaction():
        store._db.execute("DROP TRIGGER " + name)
        store._db.execute(f"UPDATE {table} SET payload=? WHERE {key}=?", (payload, identity))
        store._db.execute(trigger)


@pytest.mark.parametrize("damage", ["missing-version", "empty-header", "bad-json", "bad-segment"])
def test_ownership_corruption_is_storage_hold(owned, damage):
    actor, store = owned
    project, _, params = ownership_fixture(actor, store)
    refused = exchange(actor, "changeset.preview", params)
    ref = refused["error"]["params"]["detailRef"]
    header = store.detail_get(project, ref)
    if damage == "bad-segment":
        damage_ownership_fixture(
            store, "job_blobs", "ref", header["segmentBlobRefs"][0], canonical([[]] * 20000)
        )
    else:
        payload = (
            "{"
            if damage == "bad-json"
            else "{}"
            if damage == "empty-header"
            else canonical({k: v for k, v in header.items() if k != "ownershipDetailVersion"})
        )
        damage_ownership_fixture(store, "job_details", "id", ref, payload)
    database = list(store._db.iterdump())
    denied = exchange(
        actor,
        "project.ownership.detail",
        {
            "projectId": project,
            "detailRef": ref,
            "documentHash": None,
            "startOrdinal": 0,
            "pageSize": 1,
        },
    )
    assert not denied["ok"] and denied["error"]["code"] == "STORAGE_FAILURE", denied
    assert actor.mainline.hold and list(store._db.iterdump()) == database


def test_ownership_segment_failure_rolls_back_all_diagnostic_rows(owned, monkeypatch):
    import sqlite3

    actor, store = owned
    project, _, params = ownership_fixture(actor, store, large=True)
    database = list(store._db.iterdump())
    original = store.put_blob
    calls = []

    def fail_second(project, value):
        if "dataBase64" in value:
            calls.append(True)
            if len(calls) == 2:
                raise sqlite3.IntegrityError("owned diagnostic fixture failure")
        return original(project, value)

    monkeypatch.setattr(store, "put_blob", fail_second)
    denied = exchange(actor, "changeset.preview", params)
    assert len(calls) == 2 and not denied["ok"] and denied["error"]["code"] == "INTERNAL_ERROR"
    assert "detailRef" not in denied["error"]["params"]
    assert list(store._db.iterdump()) == database
    assert actor.mainline.hold and len(actor.mainline.replies) == 1


@pytest.mark.parametrize("late", [False, True])
def test_ownership_diagnostic_cannot_poison_an_admitted_full_reader(owned, monkeypatch, late):
    from ontolearn_engine.project.mainline import READ_LIMITS
    from ontolearn_engine.project.project_host import ProjectHostReader
    from test_mainline_read_work_budget import pad_scan_to

    actor, store = owned
    project, _, params = ownership_fixture(actor, store)
    pad_scan_to(store, project, READ_LIMITS.validation_bytes - (3000 if late else 64))
    reader = ProjectHostReader(store, limits=READ_LIMITS)
    before = reader.workspace(project, editor="ontology")
    database = list(store._db.iterdump())
    if late:
        original = store.put_blob
        inserted = []

        def extra_after_projection(project, value):
            result = original(project, value)
            if "dataBase64" in value and not inserted:
                inserted.append(True)
                original(project, {"owned-late-admission-fixture": "x" * 6000})
            return result

        monkeypatch.setattr(store, "put_blob", extra_after_projection)
    refused = exchange(actor, "changeset.preview", params)
    assert not refused["ok"] and refused["error"]["code"] == "RESOURCE_LIMIT", refused
    assert "detailRef" not in refused["error"]["params"] and not actor.mainline.hold
    if late:
        assert inserted
    assert list(store._db.iterdump()) == database
    assert reader.workspace(project, editor="ontology") == before
    assert exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})["ok"]


def test_ownership_private_admission_preserves_already_core_only_vector(owned):
    from ontolearn_engine.project.mainline import READ_LIMITS
    from ontolearn_engine.project.project_host import HostReadFault, ProjectHostReader
    from test_mainline_read_work_budget import pad_scan_to

    actor, store = owned
    project, _, params = ownership_fixture(actor, store)
    pad_scan_to(store, project, READ_LIMITS.validation_bytes + 64)
    with pytest.raises(HostReadFault) as original_full:
        ProjectHostReader(store, limits=READ_LIMITS).workspace(project, editor="ontology")
    assert original_full.value.reason == "limit"
    # Unit of the actual private issuer/admission, not a claimed wire path:
    # public preview's original full-purpose preflight remains unchanged.
    request = frame(actor, "changeset.preview", params)
    actor.mainline.begin(request)
    proof = actor.mainline.ownership_proof(params, method="changeset.preview")
    assert proof.admissions() == (True, False)
    try:
        with pytest.raises(JobFault) as refused:
            store.preview_changeset(
                project,
                params["baseRevision"],
                params,
                host_client_id=actor.host_client_id,
                engine_session_id=actor.session,
                limits=actor.limits,
                ownership_proof=proof,
            )
        assert refused.value.code == "OWNERSHIP_CONFLICT"
        actor.mainline.observe_error(request["id"], refused.value)
    finally:
        actor.finish_query_reply(request["id"], emitted=True)
    assert not actor.mainline.hold
    assert exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})["ok"]
    with pytest.raises(HostReadFault) as still_full:
        ProjectHostReader(store, limits=READ_LIMITS).workspace(project, editor="ontology")
    assert still_full.value.reason == "limit"


def test_ownership_bad_existing_blob_is_bounded_before_intern_reuse(owned, monkeypatch):
    from ontolearn_engine.project.mainline import _OwnershipProof

    actor, store = owned
    project, _, params = ownership_fixture(actor, store)
    ref = exchange(actor, "changeset.preview", params)["error"]["params"]["detailRef"]
    header = store.detail_get(project, ref)
    blob_ref = header["segmentBlobRefs"][0]
    corrupted = canonical([[]] * 20000)
    damage_ownership_fixture(store, "job_blobs", "ref", blob_ref, corrupted)
    budget, decoded, blob_reads = [], [], []
    original_reserve, original_json, original_blob = (
        _OwnershipProof.reserve,
        store._ownership_json,
        store.blob,
    )

    def reserve(proof, stage, **cost):
        if stage == "ownership segment":
            budget.append(cost)
        return original_reserve(proof, stage, **cost)

    def observe_json(raw):
        if raw == corrupted:
            assert budget and budget[-1]["objects"] >= 8 * len(corrupted.encode()) + 128
            decoded.append(True)
        return original_json(raw)

    def observe_blob(project, identity):
        if identity == blob_ref:
            blob_reads.append(True)
        return original_blob(project, identity)

    monkeypatch.setattr(_OwnershipProof, "reserve", reserve)
    monkeypatch.setattr(store, "_ownership_json", observe_json)
    monkeypatch.setattr(store, "blob", observe_blob)
    changed_request = json.loads(canonical(params))
    changed_request["plan"]["definitions"] = []  # Different request hash, same locator bytes.
    database = list(store._db.iterdump())
    denied = exchange(actor, "changeset.preview", changed_request)
    assert not denied["ok"] and denied["error"]["code"] == "STORAGE_FAILURE", denied
    assert decoded and not blob_reads and actor.mainline.hold
    assert list(store._db.iterdump()) == database


def test_ownership_raw_segment_budget_refusal_happens_before_json_loads(owned, monkeypatch):
    from ontolearn_engine.project.mainline import _OwnershipProof

    actor, store = owned
    project, _, params = ownership_fixture(actor, store)
    ref = exchange(actor, "changeset.preview", params)["error"]["params"]["detailRef"]
    header = store.detail_get(project, ref)
    payload = canonical([[]] * 20000)
    damage_ownership_fixture(store, "job_blobs", "ref", header["segmentBlobRefs"][0], payload)
    original_reserve, original_json = _OwnershipProof.reserve, store._ownership_json
    denied_before_decode, decoded = [], []

    def refuse(proof, stage, **cost):
        if stage == "ownership segment":
            assert cost["objects"] >= 8 * len(payload.encode()) + 128
            denied_before_decode.append(True)
            raise JobFault("RESOURCE_LIMIT", {"resource": "memory"})
        return original_reserve(proof, stage, **cost)

    def observe(raw):
        if raw == payload:
            decoded.append(True)
        return original_json(raw)

    monkeypatch.setattr(_OwnershipProof, "reserve", refuse)
    monkeypatch.setattr(store, "_ownership_json", observe)
    response = exchange(
        actor,
        "project.ownership.detail",
        {
            "projectId": project,
            "detailRef": ref,
            "documentHash": None,
            "startOrdinal": 0,
            "pageSize": 1,
        },
    )
    assert not response["ok"] and response["error"]["code"] == "RESOURCE_LIMIT"
    assert denied_before_decode and not decoded and not actor.mainline.hold


def test_ownership_duplicate_reuses_at_row_cap_new_context_rolls_back(owned):
    from ontolearn_engine.project.mainline import READ_LIMITS
    from test_mainline_read_work_budget import scalar_profile

    actor, store = owned
    project, _, params = ownership_fixture(actor, store)
    original = exchange(actor, "changeset.preview", params)
    ref = original["error"]["params"]["detailRef"]
    count = sum(row["rows"] for row in scalar_profile(store)["tables"].values())
    for index in range(READ_LIMITS.validation_rows - count):
        store.put_blob(project, {"owned-row-cap": index})
    database = list(store._db.iterdump())
    repeated = exchange(actor, "changeset.preview", params)
    assert repeated["error"]["code"] == "OWNERSHIP_CONFLICT", repeated
    assert repeated["error"]["params"]["detailRef"] == ref
    assert list(store._db.iterdump()) == database
    changed = json.loads(canonical(params))
    changed["plan"]["definitions"] = []
    rejected = exchange(actor, "changeset.preview", changed)
    assert rejected["error"]["code"] == "RESOURCE_LIMIT", rejected
    assert "detailRef" not in rejected["error"]["params"]
    assert list(store._db.iterdump()) == database and not actor.mainline.hold
    assert exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})["ok"]


def test_ownership_exact_legacy_detail_does_not_invent_locator(owned):
    actor, store = owned
    project, _, params = ownership_fixture(actor, store)
    # The real pre-existing internal API creates its actual old three fields;
    # it has no stack-owned mainline issuer and cannot mint a new locator.
    with pytest.raises(JobFault) as old:
        store.preview_changeset(
            project,
            params["baseRevision"],
            params,
            host_client_id=actor.host_client_id,
            engine_session_id=actor.session,
            limits=actor.limits,
        )
    assert old.value.code == "OWNERSHIP_CONFLICT"
    ref = old.value.params["detailRef"]
    assert store.detail_get(project, ref) == {
        "category": "ownership",
        "resource": "plan",
        "projectId": project,
    }
    response = exchange(
        actor,
        "project.ownership.detail",
        {
            "projectId": project,
            "detailRef": ref,
            "documentHash": None,
            "startOrdinal": 0,
            "pageSize": 1,
        },
    )
    assert response["error"]["code"] == "INVALID_STATE" and not actor.mainline.hold


def test_ownership_reference_does_not_cross_actual_successor_session(owned):
    actor, store = owned
    project, _, params = ownership_fixture(actor, store)
    ref = exchange(actor, "changeset.preview", params)["error"]["params"]["detailRef"]
    old_session = actor.session
    actor.mainline.close()
    successor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    try:
        assert exchange(successor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
        assert successor.session != old_session
        assert exchange(successor, "project.open", {"projectId": project})["ok"]
        response = exchange(
            successor,
            "project.ownership.detail",
            {
                "projectId": project,
                "detailRef": ref,
                "documentHash": None,
                "startOrdinal": 0,
                "pageSize": 1,
            },
        )
        assert response["error"]["code"] == "NOT_FOUND" and not successor.mainline.hold
        # Only a new explicit preview in the new actual session can issue a
        # new ref. Reading the old UUID never recreates its source authority.
        fresh = exchange(successor, "changeset.preview", params)
        assert fresh["error"]["code"] == "OWNERSHIP_CONFLICT", fresh
        assert fresh["error"]["params"]["detailRef"] != ref
        ownership_pages(successor, project, fresh["error"]["params"]["detailRef"])
    finally:
        successor.mainline.close()


def create(actor, name="项目A", operation=None):
    params = {
        "requestVersion": 1,
        "operationId": operation or uid(),
        "name": name,
        "initialization": {"kind": "blank"},
    }
    result = exchange(actor, "project.create", params)
    assert result["ok"], result
    return result["result"], params


def test_owned_create_retry_catalog_open_read_and_pure_snapshots(owned):
    actor, store = owned
    first, request = create(actor)
    counts = [
        store._db.execute("SELECT count(*) FROM " + table).fetchone()[0]
        for table in ("projects", "public_projects", "operation_claims", "app_receipts")
    ]
    retry = exchange(actor, "project.create", request)
    assert retry["ok"] and retry["result"] == first
    assert counts == [
        store._db.execute("SELECT count(*) FROM " + table).fetchone()[0]
        for table in ("projects", "public_projects", "operation_claims", "app_receipts")
    ]
    assert first["receipt"]["operationSequence"] == 1
    assert first["receipt"]["operationId"] == request["operationId"]
    trace = []
    store._db.set_trace_callback(trace.append)
    try:
        catalog = exchange(actor, "project.catalog", {"pageSize": 64, "cursor": None})
        assert catalog["ok"] and [r["projectId"] for r in catalog["result"]["items"]] == [
            first["projectId"]
        ]
        opened = exchange(actor, "project.open", {"projectId": first["projectId"]})
        assert opened["ok"] and opened["result"]["projectId"] == first["projectId"]
        read = exchange(
            actor, "project.read", {"projectId": first["projectId"], "editor": "ontology"}
        )
        assert read["ok"], read
        value = read["result"]
        assert value["domain"] == {
            "projectRevision": 0,
            "dependencyVector": {},
            "state": {"definitions": [], "facts": [], "mappingState": {}},
        }
        assert value["inputSnapshotId"] == opened["result"]["inputSnapshotId"]
        assert value["workspace"]["draft"] == {"editor": "ontology", "state": "missing"}
        pure = exchange(actor, "project.get", {"projectId": first["projectId"]})
        assert pure["ok"] and pure["result"] == opened["result"]
    finally:
        store._db.set_trace_callback(None)
    assert not any(
        sql.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE", "REPLACE")) for sql in trace
    )
    assert actor.mainline.replies == {} and actor._query_replies == {}


def test_project_read_preserves_mapping_ownership_without_internal_identity(owned):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    statement = ["urn:asset:1", "urn:name", '"来源值"']
    record = {
        "id": digest(statement),
        "subject": statement[0],
        "predicate": statement[1],
        "object": statement[2],
    }
    internal = store._project(project)
    store.commit(
        internal,
        0,
        uid(),
        uid(),
        definitions=[{"layer": "mapping", "id": "M1", "value": {}}],
        mapping={"id": "M1", "rows": [{"row": "source-row-001", "facts": [record]}]},
    )
    original = store._snapshot_projection(internal)
    response = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
    assert response["ok"], response
    actual = response["result"]
    assert actual["domain"]["state"] == original["state"]
    assert "project" not in actual["domain"]
    assert actual["inputSnapshotId"] == digest(original)
    fact = actual["domain"]["state"]["facts"][0]
    assert (fact["owner"], fact["source_row"], fact["managed_value"]) == (
        "M1",
        "source-row-001",
        statement[2],
    )


def test_real_mainline_query_read_scope_loads_current_without_snapshot_insert(owned):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    store.commit(
        store._project(project),
        0,
        uid(),
        uid(),
        definitions=[
            {"layer": "query", "id": "Q1", "value": {"text": "ASK { }"}},
        ],
    )
    expected = store._snapshot_projection(store._project(project))
    trace = []
    store._db.set_trace_callback(trace.append)
    try:
        loaded = exchange(
            actor,
            "query.definition.load",
            {
                "projectId": project,
                "definitionId": "Q1",
                "selection": {"kind": "current"},
            },
        )
    finally:
        store._db.set_trace_callback(None)
    assert loaded["ok"], loaded
    assert loaded["result"]["kind"] == "legacy" and loaded["result"]["text"] == "ASK { }"
    assert loaded["result"]["inputSnapshotId"] == digest(expected)
    assert not any(
        sql.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE", "REPLACE")) for sql in trace
    )
    assert actor.mainline.replies == {}


def test_selection_and_same_handshake_are_required_before_any_read(owned):
    actor, store = owned
    first, _ = create(actor, "A")
    second, _ = create(actor, "B")
    trace = []
    store._db.set_trace_callback(trace.append)
    try:
        denied = exchange(
            actor, "project.read", {"projectId": first["projectId"], "editor": "ontology"}
        )
        assert not denied["ok"] and denied["error"]["code"] == "PERMISSION_DENIED"
        assert trace == []
        assert actor.mainline.projects() == frozenset([second["projectId"]])
        actor.host_client_id = uid()
        denied = exchange(actor, "project.get", {"projectId": second["projectId"]})
        assert not denied["ok"] and denied["error"]["code"] == "PERMISSION_DENIED"
        assert trace == []
    finally:
        store._db.set_trace_callback(None)


def test_unknown_delivery_keeps_original_book_and_closes_new_authority(owned):
    actor, store = owned
    created, _ = create(actor)
    request = frame(actor, "project.get", {"projectId": created["projectId"]})
    response = actor.request(request)
    assert response["ok"]
    original = actor.mainline.replies[request["id"]]
    reserved = original.scalar
    actor.finish_query_reply(request["id"], emitted=False, failure=BrokenPipeError())
    assert actor.mainline.replies[request["id"]] is original and original.unknown
    assert original.scalar == reserved and not actor.mainline.projects()
    assert not actor.mainline.enabled()
    assert not original.ticket.read.active


def test_budget_rejection_is_before_sql_and_damaged_source_holds(owned):
    actor, store = owned
    created, _ = create(actor)
    request = frame(
        actor, "project.read", {"projectId": created["projectId"], "editor": "ontology"}
    )
    actor.mainline.begin(request)
    reply = actor.mainline.current
    trace = []
    store._db.set_trace_callback(trace.append)
    try:
        reply.scalar = HELD_BYTES
        with pytest.raises(JobFault) as error:
            actor.mainline.dispatch("project.read", request["params"])
        assert error.value.code == "RESOURCE_LIMIT" and trace == []
    finally:
        store._db.set_trace_callback(None)
        actor.mainline.finish_reply(request["id"], emitted=True)
    # Corruption is confined to this fixture's temporary database. No repair or
    # empty-project fallback can turn a failed schema proof into an open grant.
    store._db.execute("DROP TABLE current_results")
    broken = exchange(actor, "project.open", {"projectId": created["projectId"]})
    assert not broken["ok"] and broken["error"]["code"] == "STORAGE_FAILURE"
    assert actor.mainline.hold and not actor.mainline.projects()


def test_legacy2_and_test_injection_keep_original_default_deny(tmp_path):
    store = JobStore(tmp_path / "legacy.sqlite", contract=CONTRACT)
    try:
        actor = Coordinator(store, allowed_projects=set())
        assert actor.mainline is None and actor.ordinary.authority is None
        assert actor.query_dispatch is None
        assert not actor.ordinary.enabled()
    finally:
        store.close()


def test_create_conflict_does_not_change_selected_project(owned):
    actor, _ = owned
    created, params = create(actor)
    changed = dict(params, name="不同请求")
    refused = exchange(actor, "project.create", changed)
    assert not refused["ok"] and refused["error"]["code"] == "IDENTITY_CONFLICT"
    assert actor.mainline.selected == created["projectId"]
    assert canonical(params) != canonical(changed)


def confirmed_job(actor, project, request):
    ready = exchange(actor, "changeset.preview", request)
    assert ready["ok"] and ready["result"]["status"] == "ready", ready
    ready = ready["result"]
    cursor, segments = None, []
    while True:
        page = exchange(
            actor,
            "changeset.diff.page",
            {
                "projectId": project,
                "previewHash": ready["previewHash"],
                "documentKind": "diff",
                "pageSize": 1,
                "cursor": cursor,
            },
        )
        assert page["ok"], page
        material = page["result"]
        segments.extend(material["segments"])
        cursor = material["nextCursor"]
        if material["complete"]:
            break
    original = b"".join(base64.b64decode(s["dataBase64"]) for s in segments)
    assert digest(json.loads(original)) == ready["manifest"]["documentHash"]
    confirmation = exchange(
        actor,
        "changeset.confirm",
        {
            "projectId": project,
            "previewHash": ready["previewHash"],
            "completionCursor": cursor,
        },
    )
    assert confirmation["ok"], confirmation
    confirmation = confirmation["result"]
    operation = uid()
    created = exchange(
        actor,
        "job.create",
        {
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
        },
    )
    assert created["ok"] and created["result"]["state"] == "queued", created
    assert created["result"]["operationId"] == operation
    return created["result"]


def drain_owned_changesets(actor):
    async def drain():
        await actor.tick()
        await asyncio.gather(*tuple(actor.tasks))

    asyncio.run(drain())


def test_real_full_diff_confirmation_job_operation_undo_and_view_change(owned):
    actor, store = owned
    first, _ = create(actor, "A")
    project = first["projectId"]
    triple = ["urn:mainline:1", "urn:name", '"A"']
    fact = {"id": digest(triple), "subject": triple[0], "predicate": triple[1], "object": triple[2]}
    accepted = confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": 0,
            "intent": "change",
            "plan": {"manual": [fact]},
        },
    )
    # A different selected view does not cancel, drain, replace or forge A's Job.
    second, _ = create(actor, "B")
    assert actor.mainline.selected == second["projectId"]
    drain_owned_changesets(actor)
    assert store.get_job(project, accepted["jobId"])["state"] == "succeeded"
    assert exchange(actor, "project.open", {"projectId": project})["ok"]
    operation = exchange(
        actor,
        "operation.get",
        {
            "projectId": project,
            "operationId": accepted["operationId"],
        },
    )
    assert operation["ok"] and operation["result"]["jobId"] == accepted["jobId"]
    undone = confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": 1,
            "intent": "undo",
            "targetOperationId": accepted["operationId"],
        },
    )
    drain_owned_changesets(actor)
    assert store.get_job(project, undone["jobId"])["state"] == "succeeded"
    current = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
    assert current["ok"] and current["result"]["domain"]["state"]["facts"] == []
    assert current["result"]["domain"]["projectRevision"] == 2


@pytest.mark.parametrize("repeats,accepted", [(60000, True), (110000, False)])
def test_large_typed_history_open_and_get_respect_exact_validation_byte_boundary(
    tmp_path, repeats, accepted
):
    from ontolearn_engine.project.mainline import (
        HELD_OBJECTS,
        MAX_REPLIES,
        READ_LIMITS,
        READ_WORK,
    )

    assert READ_LIMITS.validation_bytes == 1572864
    assert READ_LIMITS.validation_rows == 4096
    assert READ_LIMITS.validation_work == 67108864
    assert (HELD_BYTES, HELD_OBJECTS, READ_WORK, MAX_REPLIES) == (134217728, 1048576, 536870912, 16)
    store = JobStore(tmp_path / "large-typed-history.sqlite", contract=CONTRACT, target_format=3)
    actor = None
    try:
        # Match the real historical typed baseline from the stdio runtime
        # fixture. This existing writer is setup, not an invented new T02 API.
        project = uid()
        store.create_project(project)
        internal = store._project(project)
        value = '"' + ("界😀" * repeats) + '"'
        assert len(value.encode("utf-8")) == repeats * 7 + 2
        payload = {
            "triples": [{"subject": "urn:Asset", "predicate": "urn:label", "object": value}],
            "references": [],
            "singleValuedPredicates": [],
        }
        store.commit(
            internal,
            0,
            uid(),
            uid(),
            definitions=[{"layer": "ontology", "id": "Asset", "value": payload}],
        )
        # The definition, real commit plan and after-snapshot each retain the
        # full value. These actual SQLite aggregates are only a lower bound on
        # the reader's whole-library admission total, not a Python text-length
        # substitute for the production preflight.
        copies = [
            store._db.execute(
                f"SELECT coalesce(sum(length(CAST({column} AS BLOB))),0) FROM {table}"
            ).fetchone()[0]
            for table, column in (
                ("definitions", "payload"),
                ("commits", "plan"),
                ("snapshots", "payload"),
            )
        ]
        assert all(size >= len(value.encode("utf-8")) for size in copies)
        assert sum(copies) > 1048576
        assert (sum(copies) < READ_LIMITS.validation_bytes) is accepted
        before = digest(list(store._db.iterdump()))
        actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
        assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
        assert actor.mainline.selected is None
        trace = []
        # A successful open/get must work on a genuinely read-only connection;
        # the negative case must also reject without repairing or minting rows.
        store._db.execute("PRAGMA query_only=ON")
        store._db.set_trace_callback(trace.append)
        try:
            opened = exchange(actor, "project.open", {"projectId": project})
            if accepted:
                assert opened["ok"], opened
                assert opened["result"]["projectRevision"] == 1
                got = exchange(actor, "project.get", {"projectId": project})
                assert got["ok"] and got["result"] == opened["result"], got
                assert actor.mainline.selected == project
            else:
                assert not opened["ok"] and opened["error"]["code"] == "RESOURCE_LIMIT", opened
                assert opened["error"]["params"] == {"resource": "page"}
                assert actor.mainline.selected is None
                # A bounded size rejection is repeatable, not a corruption HOLD.
                retried = exchange(actor, "project.open", {"projectId": project})
                assert not retried["ok"] and retried["error"] == opened["error"]
            assert exchange(actor, "health", {})["ok"]
        finally:
            store._db.set_trace_callback(None)
        assert not actor.mainline.hold and not actor.mainline.closed
        assert actor.mainline.enabled()
        assert actor.mainline.replies == {} and actor._query_replies == {}
        assert not any(
            sql.lstrip()
            .upper()
            .startswith(("INSERT", "UPDATE", "DELETE", "REPLACE", "CREATE", "DROP"))
            for sql in trace
        )
        assert digest(list(store._db.iterdump())) == before
        assert store.state(internal)["definitions"][0]["payload"] == canonical(payload)
    finally:
        if actor is not None:
            actor.mainline.close()
        store.close()


def test_unconsumed_real_preview_material_does_not_poison_core_pure_reads(owned):
    from ontolearn_engine.project.mainline import READ_LIMITS
    from ontolearn_engine.project.project_host import HostReadFault, ProjectHostReader

    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    internal = store._project(project)
    literal = '"' + "界😀" * 60000 + '"'
    store.commit(
        internal,
        0,
        uid(),
        uid(),
        definitions=[
            {
                "layer": "ontology",
                "id": "Asset",
                "value": {
                    "triples": [
                        {"subject": "urn:Asset", "predicate": "urn:label", "object": literal}
                    ],
                    "references": [],
                    "singleValuedPredicates": [],
                },
            }
        ],
    )
    ready = exchange(
        actor,
        "changeset.preview",
        {
            "projectId": project,
            "baseRevision": 1,
            "intent": "change",
            "plan": {
                "definitions": [
                    {
                        "layer": "ontology",
                        "id": "Asset",
                        "value": {
                            "triples": [],
                            "references": [],
                            "singleValuedPredicates": [],
                        },
                    }
                ]
            },
        },
    )
    assert ready["ok"] and ready["result"]["status"] == "ready", ready
    assert store._db.execute("SELECT count(*) FROM job_confirmations").fetchone()[0] == 0
    assert (
        store._db.execute("SELECT max(length(CAST(payload AS BLOB))) FROM job_plans").fetchone()[0]
        > 262144
    )
    assert (
        store._db.execute("SELECT sum(length(CAST(payload AS BLOB))) FROM job_blobs").fetchone()[0]
        > 262144
    )
    before = digest(list(store._db.iterdump()))
    trace = []
    store._db.execute("PRAGMA query_only=ON")
    store._db.set_trace_callback(trace.append)
    try:
        # The legacy/default reader must still use its original full-table bound.
        with pytest.raises(HostReadFault) as rejected:
            ProjectHostReader(store, limits=READ_LIMITS).catalog_start()
        assert rejected.value.reason == "limit"
        opened = exchange(actor, "project.open", {"projectId": project})
        assert opened["ok"] and opened["result"]["projectRevision"] == 1, opened
        got = exchange(actor, "project.get", {"projectId": project})
        assert got["ok"] and got["result"] == opened["result"], got
    finally:
        store._db.set_trace_callback(None)
    assert not actor.mainline.hold
    assert not any(
        sql.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE", "REPLACE")) for sql in trace
    )
    assert digest(list(store._db.iterdump())) == before
    assert actor.mainline.replies == {} and actor._query_replies == {}


def _confirmed_application_claim(actor, store, project):
    version = store._db.execute(
        "SELECT metadata_version FROM app_projects WHERE project=?", (store._project(project),)
    ).fetchone()[0]
    change = {"type": "metadata", "expectedVersion": version, "patch": {"name": "confirmed"}}
    prepared = store.prepare_application(
        project, change, actor=actor.host_client_id, permission="write"
    )
    operation = uid()
    store.apply_application(
        project,
        operation,
        change,
        actor=actor.host_client_id,
        permission="write",
        prepared_plan_ref=prepared["preparedPlanRef"],
        confirmation_ref=prepared["confirmationRef"],
    )
    claim = json.loads(
        store._db.execute(
            "SELECT context FROM operation_claims WHERE operation=?", (operation,)
        ).fetchone()[0]
    )
    assert claim["request"]["authorization"]["preparedPlanRef"] == prepared["preparedPlanRef"]
    assert claim["request"]["authorization"]["confirmationRef"] == prepared["confirmationRef"]
    assert exchange(actor, "project.open", {"projectId": project})["ok"]
    return operation, prepared


def _damage_immutable_payload(store, table, key, identity, column, payload):
    # Only fixture-local corruption; restore the exact original trigger so the
    # subsequent failure concerns payload/reference proof, not missing schema.
    assert (table, key, column) in {
        ("job_plans", "ref", "payload"),
        ("operation_claims", "operation", "context"),
    }
    name = "immutable_" + table + "_UPDATE"
    sql = store._db.execute("SELECT sql FROM sqlite_master WHERE name=?", (name,)).fetchone()[0]
    with store._transaction():
        store._db.execute("DROP TRIGGER " + name)
        store._db.execute(f"UPDATE {table} SET {column}=? WHERE {key}=?", (payload, identity))
        store._db.execute(sql)


@pytest.mark.parametrize("missing_confirmation", [False, True])
def test_referenced_application_plan_is_bounded_even_without_confirmation(
    owned, missing_confirmation
):
    from ontolearn_engine.project.mainline import READ_LIMITS

    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    _, prepared = _confirmed_application_claim(actor, store, project)
    _damage_immutable_payload(
        store,
        "job_plans",
        "ref",
        prepared["preparedPlanRef"],
        "payload",
        canonical({"oversized": "x" * READ_LIMITS.validation_bytes}),
    )
    if missing_confirmation:
        name = "immutable_job_confirmations_DELETE"
        sql = store._db.execute("SELECT sql FROM sqlite_master WHERE name=?", (name,)).fetchone()[0]
        with store._transaction():
            store._db.execute("DROP TRIGGER " + name)
            store._db.execute(
                "DELETE FROM job_confirmations WHERE id=?", (prepared["confirmationRef"],)
            )
            store._db.execute(sql)
    before = digest(list(store._db.iterdump()))
    response = exchange(actor, "project.get", {"projectId": project})
    assert not response["ok"] and response["error"]["code"] == "RESOURCE_LIMIT", response
    assert response["error"]["params"] == {"resource": "page"}
    # The oversized referenced row must fail admission before its corrupt body
    # or absent confirmation is fetched by the strict history authenticator.
    assert not actor.mainline.hold
    assert digest(list(store._db.iterdump())) == before


@pytest.mark.parametrize("damaged", ["context", "plan"])
def test_core_material_selector_preserves_actual_application_corruption_hold(owned, damaged):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    operation, prepared = _confirmed_application_claim(actor, store, project)
    if damaged == "context":
        _damage_immutable_payload(store, "operation_claims", "operation", operation, "context", "{")
    else:
        _damage_immutable_payload(
            store, "job_plans", "ref", prepared["preparedPlanRef"], "payload", "{}"
        )
    before = digest(list(store._db.iterdump()))
    response = exchange(actor, "project.get", {"projectId": project})
    assert not response["ok"] and response["error"]["code"] == "STORAGE_FAILURE", response
    assert actor.mainline.hold and not actor.mainline.enabled()
    assert digest(list(store._db.iterdump())) == before
    assert exchange(actor, "health", {})["ok"]


def test_large_claim_context_is_rejected_before_sql_json_selector(owned):
    from ontolearn_engine.project.mainline import READ_LIMITS

    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    operation, _ = _confirmed_application_claim(actor, store, project)
    _damage_immutable_payload(
        store,
        "operation_claims",
        "operation",
        operation,
        "context",
        canonical({"padding": "x" * READ_LIMITS.validation_bytes}),
    )
    trace = []
    store._db.set_trace_callback(trace.append)
    try:
        response = exchange(actor, "project.get", {"projectId": project})
    finally:
        store._db.set_trace_callback(None)
    assert not response["ok"] and response["error"]["code"] == "RESOURCE_LIMIT", response
    assert response["error"]["params"] == {"resource": "page"}
    assert not any("json_extract" in sql.lower() for sql in trace)
    assert not actor.mainline.hold


@pytest.mark.parametrize("purpose", ["query.definition.load", "query.result.describe"])
def test_query_purposes_keep_full_blob_material_admission(owned, purpose):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    store.commit(
        store._project(project),
        0,
        uid(),
        uid(),
        definitions=[{"layer": "query", "id": "Q1", "value": {"text": "ASK { }"}}],
    )
    for index in range(7):
        store.put_blob(project, {"padding": str(index) + "x" * 240000})
    before = digest(list(store._db.iterdump()))
    opened = exchange(actor, "project.open", {"projectId": project})
    assert opened["ok"], opened
    got = exchange(actor, "project.get", {"projectId": project})
    assert got["ok"] and got["result"] == opened["result"], got
    params = (
        {"projectId": project, "definitionId": "Q1", "selection": {"kind": "current"}}
        if purpose == "query.definition.load"
        else {"projectId": project, "resultId": uid()}
    )
    refused = exchange(actor, purpose, params)
    assert not refused["ok"] and refused["error"]["code"] == "RESOURCE_LIMIT", refused
    assert refused["error"]["params"] == {"resource": "page"}
    assert not actor.mainline.hold
    assert digest(list(store._db.iterdump())) == before
