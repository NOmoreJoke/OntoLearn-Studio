"""W4-A1 T03 mapping wire services over the real runtime and staging protocol.

Covers the frozen Host<->Engine staging protocol (selection-id validation,
symlink/hash/binding rejection, four CSV encodings with BOM handling, XLSX
sheet detection and re-parse), draft generation CAS + idempotent save, preview
diff/issues/conflicts, trusted preparation, the full ``changeset.preview ->
diff -> confirm -> commit`` mappingPreparation transaction with FR-304
owner/source-row provenance, mutual exclusion with manual facts, stale/drift
rejection, undo of a mapping commit, and seeded property tests for mapping
round-trip/idempotency (the dependency lock pins the toolchain, so the
property harness is a deterministic seeded generator in the Hypothesis
tradition: round-trip, invariants, idempotency).
"""

import hashlib
import json
import os
import random
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project import staging
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import digest

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
IMPL = {
    "engineVersion": "0.1.0",
    "executionSemanticsVersion": "changeset-v1",
    "dependencyLockHash": "a" * 64,
}
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
DRAFT = {
    "identity": "equip-map",
    "version": 1,
    "namespace": "urn:x:equipment/",
    "classIri": "urn:x:Equipment",
    "keys": ["equipment_id"],
    "fields": [
        {
            "column": "equipment_name",
            "predicate": "urn:x:name",
            "kind": "string",
            "trim": True,
            "empty": "omit",
            "referenceNamespace": "",
            "referenceColumns": [],
        }
    ],
}


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
    actor.finish_query_reply(request["id"], emitted=True)
    return response


def ok(response):
    assert response["ok"], response
    return response["result"]


def denied(response, code):
    assert not response["ok"] and response["error"]["code"] == code, response
    return response["error"]


@pytest.fixture
def owned(tmp_path):
    store = JobStore(tmp_path / "map.sqlite", contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
    yield actor, store
    actor.mainline.close()
    store.close()


def open_blank(actor, name="映射项目"):
    created = ok(
        exchange(
            actor,
            "project.create",
            {
                "requestVersion": 1,
                "operationId": uid(),
                "name": name,
                "initialization": {"kind": "blank"},
            },
        )
    )
    project = created["projectId"]
    ok(exchange(actor, "project.open", {"projectId": project}))
    return project


def stage_mapping_source(actor, project, payload, *, session=None, project_id=None, name=None):
    """Simulate the trusted main-process staging of one mapping-source file."""
    root = actor.store.path.parent / ".ontolearn-host-selections"
    selection = name or uid()
    target = root / selection
    target.mkdir(parents=True)
    os.chmod(target, 0o700)
    (target / "payload.csv").write_bytes(payload)
    os.chmod(target / "payload.csv", 0o600)
    meta = {
        "version": 1,
        "selectionId": selection,
        "projectId": project_id or project,
        "engineSessionId": session or actor.session,
        "purpose": "mapping-source",
        "format": "csv",
        "extension": ".csv",
        "payloadFile": "payload.csv",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "byteLength": len(payload),
        "createdAt": "2026-11-20T00:00:00Z",
    }
    (target / "meta.json").write_text(json.dumps(meta))
    os.chmod(target / "meta.json", 0o600)
    return selection


def select_source(actor, project, selection, **params):
    return exchange(
        actor,
        "project.mapping.source.select",
        {"projectId": project, "selectionId": selection, **params},
    )


def preview(actor, project, selection, draft, **params):
    return exchange(
        actor,
        "project.mapping.preview",
        {
            "projectId": project,
            "selectionId": selection,
            "sheet": params.pop("sheet", "CSV"),
            "encoding": params.pop("encoding", "utf-8"),
            "draft": draft,
            **params,
        },
    )


def prepare(actor, project, result, operation=None):
    return exchange(
        actor,
        "project.mapping.prepare",
        {
            "projectId": project,
            "resultId": result["resultId"],
            "selectionId": result["selectionId"],
            "sourceFingerprint": result["sourceFingerprint"],
            "baseRevision": result["baseRevision"],
            "operationId": operation or uid(),
        },
    )


def run_changeset(actor, store, project, plan, base, operation=None):
    host = {"host_client_id": actor.host_client_id, "engine_session_id": actor.session}
    ready = store.preview_changeset(
        project,
        base,
        {"projectId": project, "baseRevision": base, "intent": "change", "plan": plan},
        limits=LIMITS,
        **host,
    )
    assert ready["status"] == "ready", ready
    token = None
    while True:
        page = store.changeset_diff_page(
            project,
            ready["previewHash"],
            ready["manifest"]["documentKind"],
            200,
            token,
            limits=LIMITS,
            **host,
        )
        token = page["nextCursor"]
        if page["complete"]:
            break
    confirmed = store.confirm_changeset(project, ready["previewHash"], token, **host)
    job = store.create_changeset_job(
        project,
        operation or uid(),
        {
            "inputSnapshotId": confirmed["inputSnapshotId"],
            "scope": "asserted",
            "definitionId": "changeset",
            "parametersHash": confirmed["parametersHash"],
            "derivedResultIds": [],
            "preparedPlanRef": confirmed["preparedPlanRef"],
        },
        confirmed["confirmationRef"],
        IMPL,
        LIMITS,
        **host,
    )
    store.start_job(job["jobId"])
    done = store.commit_job(job["jobId"])
    assert done["state"] == "succeeded", done
    return ready


def mapping_roundtrip(actor, store, project, payload, draft=DRAFT):
    selection = stage_mapping_source(actor, project, payload)
    ok(select_source(actor, project, selection))
    result = ok(preview(actor, project, selection, draft))
    assert result["issues"] == [] and result["conflicts"] == [], result
    prepared = ok(prepare(actor, project, result))
    plan = prepared["plan"]
    run_changeset(actor, store, project, plan, result["baseRevision"])
    return selection, result, prepared


# ---------------------------------------------------------------------------
# Staging protocol security
# ---------------------------------------------------------------------------


def test_staging_rejects_traversal_and_invalid_selection_ids(owned):
    actor, store = owned
    project = open_blank(actor)
    payload = b"id,name\n1,a\n"
    selection = stage_mapping_source(actor, project, payload)
    ok(select_source(actor, project, selection))
    for bad in ("../escape", "a/b", "a\\b", "..", "", "x" * 200, "-leading", ".dot"):
        with pytest.raises(staging.StagingFault) as error:
            staging.read_inbound(
                store,
                project,
                actor.session,
                bad,
                "mapping-source",
                8 * 1024 * 1024,
            )
        assert error.value.code == "SELECTION_INVALID"
    denied(select_source(actor, project, "../escape"), "INVALID_REQUEST")


def test_staging_rejects_symlinked_payload_and_meta(owned, tmp_path):
    actor, store = owned
    project = open_blank(actor)
    payload = b"id,name\n1,a\n"
    selection = stage_mapping_source(actor, project, payload)
    root = store.path.parent / ".ontolearn-host-selections"
    target = root / selection
    (target / "payload.csv").unlink()
    (target / "real.csv").write_bytes(payload)
    os.symlink("real.csv", target / "payload.csv")
    denied(select_source(actor, project, selection), "PERMISSION_DENIED")
    # meta.json as a symlink is equally rejected.
    (target / "payload.csv").unlink()
    (target / "payload.csv").write_bytes(payload)
    (target / "meta.json").unlink()
    os.symlink("other.json", target / "meta.json")
    (target / "other.json").write_text("{}")
    denied(select_source(actor, project, selection), "PERMISSION_DENIED")


def test_staging_rejects_hash_and_length_mismatch(owned):
    actor, store = owned
    project = open_blank(actor)
    payload = b"id,name\n1,a\n"
    selection = stage_mapping_source(actor, project, payload)
    root = store.path.parent / ".ontolearn-host-selections"
    (root / selection / "payload.csv").write_bytes(b"id,name\n1,TAMPERED\n")
    denied(select_source(actor, project, selection), "IDENTITY_CONFLICT")


def test_staging_rejects_wrong_project_and_session(owned):
    actor, _ = owned
    project = open_blank(actor)
    payload = b"id,name\n1,a\n"
    wrong_project = stage_mapping_source(actor, project, payload, project_id=uid())
    denied(select_source(actor, project, wrong_project), "IDENTITY_CONFLICT")
    stale_session = stage_mapping_source(
        actor, project, payload, session="00000000-0000-4000-8000-000000000000"
    )
    denied(select_source(actor, project, stale_session), "IDENTITY_CONFLICT")


def test_payload_drift_after_select_is_rejected(owned):
    actor, store = owned
    project = open_blank(actor)
    payload = b"id,name\n1,a\n"
    selection = stage_mapping_source(actor, project, payload)
    ok(select_source(actor, project, selection))
    root = store.path.parent / ".ontolearn-host-selections"
    changed = b"id,name\n1,b\n"
    (root / selection / "payload.csv").write_bytes(changed)
    meta = json.loads((root / selection / "meta.json").read_text())
    meta["sha256"] = hashlib.sha256(changed).hexdigest()
    meta["byteLength"] = len(changed)
    (root / selection / "meta.json").write_text(json.dumps(meta))
    # The persisted select() binding binds the original bytes: drift rejects.
    denied(preview(actor, project, selection, DRAFT), "IDENTITY_CONFLICT")


# ---------------------------------------------------------------------------
# Parsing: CSV encodings and XLSX
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "encoding,encoding_name",
    [("utf-8", "utf-8"), ("gb18030", "gb18030"), ("big5", "big5"), ("utf-16", "utf-16")],
)
def test_csv_encodings_roundtrip_to_facts(owned, encoding, encoding_name):
    actor, store = owned
    project = open_blank(actor)
    row = "001,泵站A"
    payload = ("equipment_id,equipment_name\n" + row + "\n").encode(encoding)
    if encoding == "utf-8":
        payload = b"\xef\xbb\xbf" + payload  # UTF-8 BOM is recognized.
    selection = stage_mapping_source(actor, project, payload)
    selected = ok(select_source(actor, project, selection, encoding=encoding))
    assert selected["encoding"] == encoding
    assert selected["totalRows"] == 1
    assert selected["fields"][0]["name"] == "equipment_id"
    result = ok(preview(actor, project, selection, DRAFT, encoding=encoding))
    assert result["totalRows"] == 1
    assert '"泵站A"' in " ".join(result["added"])
    prepared = ok(prepare(actor, project, result))
    run_changeset(actor, store, project, prepared["plan"], result["baseRevision"])
    facts = store.state(store._project(project))["facts"]
    assert any(fact["object"] == '"泵站A"' for fact in facts)


def test_xlsx_sheet_detection_reparse_and_suggestions(owned):
    openpyxl = pytest.importorskip("openpyxl")
    actor, store = owned
    project = open_blank(actor)
    # An ontology property whose local name matches the column exactly.
    ontology_plan = {
        "definitions": [
            {
                "layer": "ontology",
                "id": "G",
                "value": {
                    "triples": [
                        {
                            "subject": "urn:x:equipment_name",
                            "predicate": RDF_TYPE,
                            "object": "<http://www.w3.org/2002/07/owl#DatatypeProperty>",
                        },
                    ],
                    "singleValuedPredicates": [],
                    "references": [],
                },
            }
        ]
    }
    run_changeset(actor, store, project, ontology_plan, 0)
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.title = "设备"
    sheet.append(["equipment_id", "equipment_name"])
    sheet.append(["001", "泵站A"])
    other = book.create_sheet("其他")
    other.append(["equipment_id", "equipment_name"])
    other.append(["002", "泵站B"])
    stream = __import__("io").BytesIO()
    book.save(stream)
    payload = stream.getvalue()
    root = store.path.parent / ".ontolearn-host-selections"
    selection = uid()
    target = root / selection
    target.mkdir(parents=True)
    (target / "payload.xlsx").write_bytes(payload)
    (target / "meta.json").write_text(
        json.dumps(
            {
                "version": 1,
                "selectionId": selection,
                "projectId": project,
                "engineSessionId": actor.session,
                "purpose": "mapping-source",
                "format": "xlsx",
                "extension": ".xlsx",
                "payloadFile": "payload.xlsx",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "byteLength": len(payload),
                "createdAt": "2026-11-20T00:00:00Z",
            }
        )
    )
    selected = ok(select_source(actor, project, selection))
    assert selected["format"] == "xlsx" and selected["encoding"] is None
    assert selected["sheets"] == ["设备", "其他"]
    assert selected["sheet"] == "设备"
    assert selected["suggestions"] == [
        {
            "column": "equipment_name",
            "predicate": "urn:x:equipment_name",
            "basis": "exact-field-name",
            "samples": ["泵站A"],
        }
    ]
    # Re-parse through the same bridge with the other sheet.
    reparsed = ok(select_source(actor, project, selection, sheet="其他"))
    assert reparsed["sheet"] == "其他" and reparsed["totalRows"] == 1
    result = ok(preview(actor, project, selection, DRAFT, sheet="其他", encoding=None))
    assert result["totalRows"] == 1
    prepared = ok(prepare(actor, project, result))
    run_changeset(actor, store, project, prepared["plan"], result["baseRevision"])
    facts = store.state(store._project(project))["facts"]
    assert any(fact["object"] == '"泵站B"' for fact in facts)


# ---------------------------------------------------------------------------
# Draft persistence
# ---------------------------------------------------------------------------


def test_draft_generation_cas_and_idempotent_save(owned):
    actor, store = owned
    project = open_blank(actor)
    revision = store.revision(store._project(project))
    empty = ok(
        exchange(
            actor, "project.mapping.draft.read", {"projectId": project, "mappingId": "equip-map"}
        )
    )
    assert empty["generation"] == 0 and empty["draft"] is None
    operation = uid()
    saved = ok(
        exchange(
            actor,
            "project.mapping.draft.save",
            {
                "projectId": project,
                "operationId": operation,
                "expectedGeneration": 0,
                "baseRevision": revision,
                "draft": DRAFT,
            },
        )
    )
    assert saved["generation"] == 1
    # Stale expectedGeneration fails deterministically.
    denied(
        exchange(
            actor,
            "project.mapping.draft.save",
            {
                "projectId": project,
                "operationId": uid(),
                "expectedGeneration": 0,
                "baseRevision": revision,
                "draft": DRAFT,
            },
        ),
        "INVALID_STATE",
    )
    # Same operation replays its original receipt.
    replay = ok(
        exchange(
            actor,
            "project.mapping.draft.save",
            {
                "projectId": project,
                "operationId": operation,
                "expectedGeneration": 0,
                "baseRevision": revision,
                "draft": DRAFT,
            },
        )
    )
    assert replay == saved
    reading = ok(
        exchange(
            actor, "project.mapping.draft.read", {"projectId": project, "mappingId": "equip-map"}
        )
    )
    assert reading["generation"] == 1 and reading["draft"] == DRAFT


# ---------------------------------------------------------------------------
# Preview issues/conflicts, prepare rejections
# ---------------------------------------------------------------------------


def test_preview_duplicate_key_blocks_preparation(owned):
    actor, store = owned
    project = open_blank(actor)
    payload = b"equipment_id,equipment_name\n001,A\n001,B\n"
    selection = stage_mapping_source(actor, project, payload)
    ok(select_source(actor, project, selection))
    result = ok(preview(actor, project, selection, DRAFT))
    assert {issue["code"] for issue in result["issues"]} == {"DUPLICATE_KEY"}
    assert all(issue["messageKey"] == "mapping.duplicateKey" for issue in result["issues"])
    denied(prepare(actor, project, result), "MAPPING_VALUE_INVALID")


def test_preview_manual_drift_blocks_preparation_with_ownership_conflict(owned):
    actor, store = owned
    project = open_blank(actor)
    payload = b"equipment_id,equipment_name\n001,A\n"
    selection, _, _ = mapping_roundtrip(actor, store, project, payload)
    # Manually edit the mapped value at the storage level (the formal
    # ChangeSet layer refuses touching mapped facts by design): the object
    # diverges from managed_value, which is exactly MANUAL_DRIFT evidence.
    internal = store._project(project)
    facts = store.state(internal)["facts"]
    edited = next(fact for fact in facts if fact["predicate"] == "urn:x:name")
    revision = store.revision(internal)
    store.commit(internal, revision, uid(), uid(), edits={edited["id"]: '"MANUAL"'})
    result = ok(preview(actor, project, selection, DRAFT))
    assert [conflict["code"] for conflict in result["conflicts"]] == ["MANUAL_DRIFT"]
    conflict = result["conflicts"][0]
    assert conflict["owner"] == "equip-map"
    assert conflict["sourceRow"] == json.dumps(
        {"sheet": "CSV", "row": 2}, ensure_ascii=False, separators=(",", ":")
    )
    denied(prepare(actor, project, result), "OWNERSHIP_CONFLICT")


def test_preview_ownership_conflict_against_manual_fact(owned):
    actor, store = owned
    project = open_blank(actor)
    # Declare urn:x:name single-valued and assert a manual value first: the
    # mapping proposing a different value for that slot is a frozen
    # OWNERSHIP_CONFLICT with the full 8-field evidence.
    ontology_and_manual = {
        "definitions": [
            {
                "layer": "ontology",
                "id": "single",
                "value": {
                    "triples": [],
                    "singleValuedPredicates": ["urn:x:name"],
                    "references": [],
                },
            }
        ],
        "manual": [
            {
                "id": digest(["urn:x:equipment/001", "urn:x:name", '"用户值"']),
                "subject": "urn:x:equipment/001",
                "predicate": "urn:x:name",
                "object": '"用户值"',
            }
        ],
    }
    run_changeset(actor, store, project, ontology_and_manual, 0)
    payload = b"equipment_id,equipment_name\n001,A\n"
    selection = stage_mapping_source(actor, project, payload)
    ok(select_source(actor, project, selection))
    result = ok(preview(actor, project, selection, DRAFT))
    assert [conflict["code"] for conflict in result["conflicts"]] == ["OWNERSHIP_CONFLICT"]
    conflict = result["conflicts"][0]
    assert conflict["subject"] == "urn:x:equipment/001"
    assert conflict["predicate"] == "urn:x:name"
    assert conflict["source"] == '"A"'
    assert conflict["current"] == '"用户值"'
    denied(prepare(actor, project, result), "OWNERSHIP_CONFLICT")


def test_prepare_rejects_stale_revision_and_bad_binding(owned):
    actor, store = owned
    project = open_blank(actor)
    payload = b"equipment_id,equipment_name\n001,A\n"
    selection = stage_mapping_source(actor, project, payload)
    ok(select_source(actor, project, selection))
    result = ok(preview(actor, project, selection, DRAFT))
    manual = {
        "manual": [
            {
                "id": digest(["urn:x:other", "urn:x:p", '"v"']),
                "subject": "urn:x:other",
                "predicate": "urn:x:p",
                "object": '"v"',
            }
        ]
    }
    run_changeset(actor, store, project, manual, result["baseRevision"])
    denied(prepare(actor, project, result), "REVISION_CONFLICT")
    # Unknown resultId never authorizes a preparation.
    forged = dict(result, resultId=uid())
    denied(prepare(actor, project, forged), "IDENTITY_CONFLICT")


# ---------------------------------------------------------------------------
# ChangeSet integration
# ---------------------------------------------------------------------------


def test_mapping_commits_atomically_with_provenance_and_idempotent_rerun(owned):
    actor, store = owned
    project = open_blank(actor)
    payload = b"equipment_id,equipment_name\n001,A\n002,B\n"
    selection, result, prepared = mapping_roundtrip(actor, store, project, payload)
    state = store.state(store._project(project))
    assert len(state["facts"]) == 4  # 2 rdf:type + 2 names
    assert all(fact["owner"] == "equip-map" for fact in state["facts"])
    assert all(fact["source_row"] for fact in state["facts"])
    assert all(fact["managed_value"] == fact["object"] for fact in state["facts"])
    assert any(
        definition["layer"] == "mapping" and definition["id"] == "equip-map"
        for definition in state["definitions"]
    )
    # Rerunning the same mapping over identical source data is a no-op commit.
    second = ok(preview(actor, project, selection, DRAFT))
    second_prepared = ok(prepare(actor, project, second))
    run_changeset(actor, store, project, second_prepared["plan"], second["baseRevision"])
    assert store.state(store._project(project))["facts"] == state["facts"]


def test_mapping_plan_is_mutually_exclusive_with_manual_facts(owned):
    actor, store = owned
    project = open_blank(actor)
    payload = b"equipment_id,equipment_name\n001,A\n"
    selection, result, prepared = mapping_roundtrip(actor, store, project, payload)
    assert set(prepared["plan"]) == {"mappingPreparation"}
    host = {"host_client_id": actor.host_client_id, "engine_session_id": actor.session}
    base = store.revision(store._project(project))
    # The wire schema rejects mixing the branches engine-side as well.
    mixed = {
        "projectId": project,
        "baseRevision": base,
        "intent": "change",
        "plan": {
            "mappingPreparation": prepared["plan"]["mappingPreparation"],
            "manual": [],
        },
    }
    response = exchange(actor, "changeset.preview", mixed)
    denied(response, "INVALID_REQUEST")
    from ontolearn_engine.job_store import JobFault
    from ontolearn_engine.project.domain_changesets import preview_changeset

    with pytest.raises(JobFault):
        preview_changeset(store, project, base, mixed, limits=LIMITS, hook=lambda _: None, **host)


def test_mapping_update_commit_and_undo(owned):
    actor, store = owned
    project = open_blank(actor)
    payload = b"equipment_id,equipment_name\n001,A\n"
    selection, first, _ = mapping_roundtrip(actor, store, project, payload)
    payload2 = b"equipment_id,equipment_name\n001,B\n"
    selection2 = stage_mapping_source(actor, project, payload2)
    ok(select_source(actor, project, selection2))
    second = ok(preview(actor, project, selection2, DRAFT))
    assert second["modified"] == [
        {
            "subject": "urn:x:equipment/001",
            "predicate": "urn:x:name",
            "before": ['"A"'],
            "after": ['"B"'],
        }
    ]
    prepared = ok(prepare(actor, project, second))
    host = {"host_client_id": actor.host_client_id, "engine_session_id": actor.session}
    run_changeset(actor, store, project, prepared["plan"], second["baseRevision"])
    facts = {
        (fact["subject"], fact["predicate"]): fact["object"]
        for fact in store.state(store._project(project))["facts"]
    }
    assert facts[("urn:x:equipment/001", "urn:x:name")] == '"B"'
    # Undo the mapping update through the ordinary undo machinery.
    operation = store._db.execute(
        "SELECT operation FROM commits WHERE project=? AND revision=?",
        (store._project(project), second["baseRevision"] + 1),
    ).fetchone()[0]
    undo_ready = store.preview_changeset(
        project,
        store.revision(store._project(project)),
        {
            "projectId": project,
            "baseRevision": store.revision(store._project(project)),
            "intent": "undo",
            "targetOperationId": operation,
        },
        limits=LIMITS,
        **host,
    )
    assert undo_ready["status"] == "ready", undo_ready
    token = None
    while True:
        page = store.changeset_diff_page(
            project,
            undo_ready["previewHash"],
            undo_ready["manifest"]["documentKind"],
            200,
            token,
            limits=LIMITS,
            **host,
        )
        token = page["nextCursor"]
        if page["complete"]:
            break
    confirmed = store.confirm_changeset(project, undo_ready["previewHash"], token, **host)
    job = store.create_changeset_job(
        project,
        uid(),
        {
            "inputSnapshotId": confirmed["inputSnapshotId"],
            "scope": "asserted",
            "definitionId": "changeset",
            "parametersHash": confirmed["parametersHash"],
            "derivedResultIds": [],
            "preparedPlanRef": confirmed["preparedPlanRef"],
        },
        confirmed["confirmationRef"],
        IMPL,
        LIMITS,
        **host,
    )
    store.start_job(job["jobId"])
    assert store.commit_job(job["jobId"])["state"] == "succeeded"
    facts = {
        (fact["subject"], fact["predicate"]): fact["object"]
        for fact in store.state(store._project(project))["facts"]
    }
    assert facts[("urn:x:equipment/001", "urn:x:name")] == '"A"'


# ---------------------------------------------------------------------------
# Seeded property tests (Hypothesis-tradition, deterministic generator)
# ---------------------------------------------------------------------------


def _generated_cases(count, seed=20261120):
    """Seeded pseudo-random small CSV corpora: integers, unicode, blanks."""
    rng = random.Random(seed)
    cases = []
    for _ in range(count):
        rows = rng.randint(1, 6)
        names = [f"值{rng.randint(0, 99)}-{rng.choice('ABC')}" for _ in range(rows)]
        ids = [str(rng.randint(1, 999)).zfill(rng.choice([1, 3])) for _ in range(rows)]
        if len(set(ids)) != len(ids):
            ids = [str(index + 1) for index in range(rows)]
        body = "equipment_id,equipment_name\n" + "".join(
            f"{key},{value}\n" for key, value in zip(ids, names, strict=True)
        )
        cases.append((ids, body.encode("utf-8")))
    return cases


def test_property_mapping_roundtrip_and_idempotency(owned):
    actor, store = owned
    project = open_blank(actor)
    for ids, payload in _generated_cases(8):
        selection, result, prepared = mapping_roundtrip(actor, store, project, payload)
        state = store.state(store._project(project))
        expected_names = {f"urn:x:equipment/{key}" for key in ids}
        owned_subjects = {fact["subject"] for fact in state["facts"]}
        assert expected_names <= owned_subjects
        # Idempotency: same operationId replay returns the same ref even
        # after the domain head moved past the prepared revision.
        replay = ok(prepare(actor, project, result, operation=prepared["operationId"]))
        assert (
            replay["plan"]["mappingPreparation"]["preparationRef"]
            == prepared["plan"]["mappingPreparation"]["preparationRef"]
        )
        # Every persisted fact carries FR-304 provenance.
        assert all(fact["owner"] == "equip-map" for fact in state["facts"])
        assert all(
            fact["source_row"] and fact["managed_value"] == fact["object"]
            for fact in state["facts"]
        )


def test_property_preview_rows_paginate_within_bounds(owned):
    actor, store = owned
    project = open_blank(actor)
    rng = random.Random(4242)
    rows = rng.randint(4, 10)
    body = "equipment_id,equipment_name\n" + "".join(
        f"{index:03d},v{index}\n" for index in range(1, rows + 1)
    )
    selection = stage_mapping_source(actor, project, body.encode())
    ok(select_source(actor, project, selection))
    seen = 0
    offset = 0
    while True:
        page = ok(preview(actor, project, selection, DRAFT, page={"offset": offset, "limit": 3}))
        seen += len(page["rows"])
        offset += len(page["rows"])
        if offset >= page["totalRows"] or not page["rows"]:
            break
    assert seen == rows


# ---------------------------------------------------------------------------
# W4-09: bounded preview response with exact summary and zero orphan evidence
# ---------------------------------------------------------------------------


def preview_evidence_count(store):
    return store._db.execute(
        "SELECT count(*) FROM job_details WHERE id LIKE 'mapping-preview:%'"
    ).fetchone()[0]


def test_legal_5500_row_csv_previews_within_budget_and_prepares(owned):
    from ontolearn_engine.storage import canonical as storage_canonical

    actor, store = owned
    project = open_blank(actor)
    rows = 5500
    payload = (
        "equipment_id,equipment_name\n"
        + "".join(f"{index:04d},设备{index}\n" for index in range(1, rows + 1))
    ).encode()
    selection = stage_mapping_source(actor, project, payload)
    ok(select_source(actor, project, selection))
    result = ok(preview(actor, project, selection, DRAFT, page={"offset": 0, "limit": 1}))
    assert len(storage_canonical(result).encode("utf-8")) <= 220_000
    # The requested page window always survives.
    assert len(result["rows"]) == 1 and result["offset"] == 0
    assert result["rows"][0]["input"] == ["0001", "设备1"]
    assert result["totalRows"] == rows
    # Exact full totals; the large diff arrays were deterministically reduced.
    assert result["summary"] == {
        "totalIdentitiesAdded": rows,
        "totalIdentitiesRemoved": 0,
        "totalIssues": 0,
        "totalConflicts": 0,
        "totalAdded": rows * 2,
        "totalRemoved": 0,
        "totalModified": 0,
        "truncated": True,
    }
    assert 0 < len(result["identitiesAdded"]) < rows
    assert result["identitiesAdded"][0] == "urn:x:equipment/0001"
    assert 0 < len(result["added"]) < rows * 2
    assert preview_evidence_count(store) == 1
    # previewHash still covers the FULL computation: the preparation replays
    # the whole 5,500-row source and lands its digest-bound evidence inside
    # the locked MainlineHost write admission (the per-row bulk is stored as
    # a rowCount reference, not duplicated material).
    prepared = ok(prepare(actor, project, result))
    reference = prepared["plan"]["mappingPreparation"]
    record = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?",
        (reference["preparationRef"], project),
    ).fetchone()
    assert record is not None
    evidence = json.loads(record[0])
    assert evidence["plan"]["mapping"]["rowCount"] == rows
    assert evidence["plan"]["mapping"]["rows"] is None
    assert preview_evidence_count(store) == 1


def test_truncated_preview_within_admission_commits_full_changeset(owned):
    actor, store = owned
    project = open_blank(actor)
    rows, name_length = 240, 450
    # 240 two-column rows of 450-char ASCII names (~105 KB source) stay fully
    # inside the locked 4,096-row / 1.5 MiB MainlineHost database admission
    # (measured: the two admitted plan copies -- jobs context plus the
    # authorized job_plans payload -- total ~1.11 MiB), yet their untruncated
    # preview JSON exceeds the 220,000-byte response budget: the arrays are
    # truly reduced while the committed changeset still lands every fact.
    payload = (
        "equipment_id,equipment_name\n"
        + "".join(
            f"{index:04d},{chr(97 + index % 26) * name_length}\n" for index in range(1, rows + 1)
        )
    ).encode()
    assert len(payload) < 400_000
    selection = stage_mapping_source(actor, project, payload)
    ok(select_source(actor, project, selection))
    result = ok(preview(actor, project, selection, DRAFT))
    assert result["totalRows"] == rows
    assert result["summary"]["totalIdentitiesAdded"] == rows
    assert result["summary"]["totalAdded"] == rows * 2
    assert result["summary"]["truncated"] is True
    assert 0 < len(result["identitiesAdded"]) < rows
    assert 0 < len(result["added"]) < rows * 2
    prepared = ok(prepare(actor, project, result))
    run_changeset(actor, store, project, prepared["plan"], result["baseRevision"])
    facts = store.state(store._project(project))["facts"]
    assert len(facts) == rows * 2
    assert all(fact["owner"] == "equip-map" for fact in facts)


def test_preview_rejection_writes_no_evidence_row(owned):
    actor, store = owned
    project = open_blank(actor)
    payload = b"equipment_id,equipment_name\n001,A\n"
    selection = stage_mapping_source(actor, project, payload)
    ok(select_source(actor, project, selection))
    before = preview_evidence_count(store)
    # Wrong sheet for a CSV source: rejected before any evidence write.
    denied(preview(actor, project, selection, DRAFT, sheet="其他"), "INVALID_REQUEST")
    assert preview_evidence_count(store) == before
    # A malformed draft (unknown key column) rejects without evidence too.
    broken = {
        **DRAFT,
        "keys": ["missing_column"],
        "fields": [
            {**DRAFT["fields"][0], "column": "also_missing"},
        ],
    }
    denied(preview(actor, project, selection, broken), "INVALID_REQUEST")
    assert preview_evidence_count(store) == before


def test_preview_caps_issue_lists_at_contract_maximum_without_orphan_evidence(owned):
    actor, store = owned
    project = open_blank(actor)
    # 5001 duplicate-key rows: more issues than the frozen contract's 5000
    # maxItems. The response keeps a deterministic prefix plus the exact
    # summary total instead of failing validation after writing evidence.
    payload = ("equipment_id,equipment_name\n" + "001,A\n" * 5001).encode()
    selection = stage_mapping_source(actor, project, payload)
    ok(select_source(actor, project, selection))
    result = ok(preview(actor, project, selection, DRAFT))
    # The contract cap (5000) and then the byte budget reduce the carried
    # list; the exact full total stays in summary and no orphan row remains.
    assert 0 < len(result["issues"]) < 5001
    assert all(issue["code"] == "DUPLICATE_KEY" for issue in result["issues"])
    assert result["summary"]["totalIssues"] == 5001
    assert result["summary"]["truncated"] is True
    assert preview_evidence_count(store) == 1
