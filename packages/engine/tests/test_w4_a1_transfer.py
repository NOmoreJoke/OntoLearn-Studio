"""W4-A1 T10 transfer services: project package v1 and HTML report v1.

Covers the frozen ``ontolearn-project-package-v1`` contract over the real
runtime and staging protocol: full/template export with FR-1000 role rules and
option isolation, deterministic publication receipts and idempotent replay,
defensive import validation with every frozen rejection reason, brand-new
imported project ids through the single-writer Store path, the FR-901
credential scan (rejection without echoing, redaction acceptance), the
``ontolearn-report-v1`` projection with the strict independent-transfer rule,
CSP-safe HTML escaping, and seeded property tests for manifest/ZIP
round-trip invariants.
"""

import hashlib
import io
import json
import os
import random
import zipfile
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import digest
from ontolearn_engine.transfer import package as transfer_package
from ontolearn_engine.transfer.credential_scan import CredentialLeak, scan_projection
from ontolearn_engine.transfer.report import learning_attempts

OPTIONS_OFF = {"agentSessions": False, "rawSources": False, "derived": False, "history": False}
NAME_FIELD = {
    "column": "equipment_name",
    "predicate": "urn:x:name",
    "kind": "string",
    "trim": True,
    "empty": "omit",
    "referenceNamespace": "",
    "referenceColumns": [],
}
DRAFT = {
    "identity": "equip-map",
    "version": 1,
    "namespace": "urn:x:equipment/",
    "classIri": "urn:x:Equipment",
    "keys": ["equipment_id"],
    "fields": [NAME_FIELD],
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
    store = JobStore(tmp_path / "t10.sqlite", contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
    yield actor, store
    actor.mainline.close()
    store.close()


def open_blank(actor, name="传输项目"):
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


def stage_outbound(actor, project, purpose, extension, output_file):
    root = actor.store.path.parent / ".ontolearn-host-selections"
    selection = uid()
    target = root / selection
    target.mkdir(parents=True)
    os.chmod(target, 0o700)
    (target / "meta.json").write_text(
        json.dumps(
            {
                "version": 1,
                "selectionId": selection,
                "projectId": project,
                "engineSessionId": actor.session,
                "purpose": purpose,
                "extension": extension,
                "outputFile": output_file,
                "createdAt": "2026-11-20T00:00:00Z",
            }
        )
    )
    return selection


def stage_inbound(actor, project, payload, payload_file, fmt, extension):
    root = actor.store.path.parent / ".ontolearn-host-selections"
    selection = uid()
    target = root / selection
    target.mkdir(parents=True)
    os.chmod(target, 0o700)
    (target / payload_file).write_bytes(payload)
    (target / "meta.json").write_text(
        json.dumps(
            {
                "version": 1,
                "selectionId": selection,
                "projectId": project,
                "engineSessionId": actor.session,
                "purpose": "package-import",
                "format": fmt,
                "extension": extension,
                "payloadFile": payload_file,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "byteLength": len(payload),
                "createdAt": "2026-11-20T00:00:00Z",
            }
        )
    )
    return selection


def commit_manual(actor, store, project, facts, definitions=None, base=None):
    host = {"host_client_id": actor.host_client_id, "engine_session_id": actor.session}
    limits = {
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
    if base is None:
        base = store.revision(store._project(project))
    plan = {"manual": facts}
    if definitions:
        plan["definitions"] = definitions
    ready = store.preview_changeset(
        project,
        base,
        {"projectId": project, "baseRevision": base, "intent": "change", "plan": plan},
        limits=limits,
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
            limits=limits,
            **host,
        )
        token = page["nextCursor"]
        if page["complete"]:
            break
    confirmed = store.confirm_changeset(project, ready["previewHash"], token, **host)
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
        {
            "engineVersion": "0.1.0",
            "executionSemanticsVersion": "changeset-v1",
            "dependencyLockHash": "a" * 64,
        },
        limits,
        **host,
    )
    store.start_job(job["jobId"])
    done = store.commit_job(job["jobId"])
    assert done["state"] == "succeeded", done


def populated_project(actor, store):
    """Ontology + two manual facts + one mapping-owned fact set."""
    project = open_blank(actor, name="完整项目")
    commit_manual(
        actor,
        store,
        project,
        [
            {
                "id": digest(["urn:x:equipment/001", "urn:x:name", '"泵站A"']),
                "subject": "urn:x:equipment/001",
                "predicate": "urn:x:name",
                "object": '"泵站A"',
            },
            {
                "id": digest(["urn:x:equipment/002", "urn:x:name", '"泵站B"']),
                "subject": "urn:x:equipment/002",
                "predicate": "urn:x:name",
                "object": '"泵站B"',
            },
        ],
        definitions=[
            {
                "layer": "ontology",
                "id": "G",
                "value": {
                    "triples": [
                        {
                            "subject": "urn:x:Equipment",
                            "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                            "object": "<http://www.w3.org/2002/07/owl#Class>",
                        }
                    ],
                    "singleValuedPredicates": [],
                    "references": [],
                },
            }
        ],
        base=0,
    )
    # A mapping-owned fact set through the storage plan path.
    from ontolearn_engine.mapping.source import parse_csv

    table = parse_csv(b"equipment_id,equipment_name\n003,C\n")
    from ontolearn_engine.mapping import plan as mapping_plan

    mapping = mapping_plan.Mapping(
        identity="equip-map",
        version=1,
        namespace="urn:x:equipment/",
        class_iri="urn:x:Equipment",
        keys=("equipment_id",),
        bindings=(mapping_plan.Binding("equipment_name", "urn:x:name"),),
    )
    preview = mapping_plan.preview(
        mapping,
        table,
        {
            "project": store._project(project),
            "projectRevision": store.revision(store._project(project)),
            "state": store.state(store._project(project)),
        },
    )
    assert preview.ready, preview.issues
    internal = store._project(project)
    revision = store.revision(internal)
    store.commit(
        internal,
        revision,
        uid(),
        uid(),
        mapping={"id": "equip-map", "rows": preview.rows()},
        definitions=[
            {
                "layer": "mapping",
                "id": "equip-map",
                "value": {
                    "version": 1,
                    "definition": {
                        "identity": "equip-map",
                        "version": 1,
                        "namespace": "urn:x:equipment/",
                        "class_iri": "urn:x:Equipment",
                        "keys": ["equipment_id"],
                        "bindings": [
                            {
                                "column": "equipment_name",
                                "predicate": "urn:x:name",
                                "conversion": {
                                    "kind": "string",
                                    "trim": False,
                                    "empty": "omit",
                                    "true_values": ("true", "1"),
                                    "false_values": ("false", "0"),
                                },
                                "reference_namespace": None,
                                "reference_columns": [],
                            }
                        ],
                    },
                    "sourceHash": preview.source_hash,
                    "sheet": "CSV",
                },
            }
        ],
    )
    return project


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def test_export_check_full_roles_portability_and_conflict_policy(owned):
    actor, store = owned
    project = populated_project(actor, store)
    selection = stage_outbound(
        actor, project, "package-export", ".ontolearn.zip", "output.ontolearn.zip"
    )
    revision = store.revision(store._project(project))
    check = ok(
        exchange(
            actor,
            "project.transfer.package.export.check",
            {
                "projectId": project,
                "selectionId": selection,
                "kind": "full",
                "baseRevision": revision,
                "options": {**OPTIONS_OFF, "history": True},
            },
        )
    )
    roles = {file["role"] for file in check["manifest"]["files"]}
    assert roles == {"definitions", "assertions", "ownership", "checkpoint", "history"}
    assert check["portability"]["restoreCurrent"] is True
    assert check["portability"]["rerunMapping"] is False
    assert "raw-source" in check["portability"]["missing"]
    assert check["conflictPolicy"] == {
        "version": 1,
        "ownership": "reject",
        "projectIdentity": "new-project-id",
        "fingerprint": check["conflictPolicy"]["fingerprint"],
    }
    # The policy fingerprint is deterministic for the same kind/options.
    again = ok(
        exchange(
            actor,
            "project.transfer.package.export.check",
            {
                "projectId": project,
                "selectionId": selection,
                "kind": "full",
                "baseRevision": revision,
                "options": {**OPTIONS_OFF, "history": True},
            },
        )
    )
    assert again["conflictPolicy"]["fingerprint"] == check["conflictPolicy"]["fingerprint"]


def test_export_check_template_excludes_mapping_and_facts(owned):
    actor, store = owned
    project = populated_project(actor, store)
    selection = stage_outbound(
        actor, project, "package-export", ".ontolearn.zip", "output.ontolearn.zip"
    )
    revision = store.revision(store._project(project))
    check = ok(
        exchange(
            actor,
            "project.transfer.package.export.check",
            {
                "projectId": project,
                "selectionId": selection,
                "kind": "template",
                "baseRevision": revision,
                "options": OPTIONS_OFF,
            },
        )
    )
    roles = {file["role"] for file in check["manifest"]["files"]}
    assert roles == {"definitions"}
    assert check["portability"]["restoreCurrent"] is False
    assert "mapping-definition" in check["portability"]["missing"]


def test_export_publishes_receipt_and_replays_idempotently(owned):
    actor, store = owned
    project = populated_project(actor, store)
    selection = stage_outbound(
        actor, project, "package-export", ".ontolearn.zip", "output.ontolearn.zip"
    )
    revision = store.revision(store._project(project))
    check = ok(
        exchange(
            actor,
            "project.transfer.package.export.check",
            {
                "projectId": project,
                "selectionId": selection,
                "kind": "full",
                "baseRevision": revision,
                "options": OPTIONS_OFF,
            },
        )
    )
    exported = ok(
        exchange(
            actor,
            "project.transfer.package.export",
            {
                "projectId": project,
                "selectionId": selection,
                "checkRef": check["checkRef"],
                "operationId": uid(),
            },
        )
    )
    assert exported["publication"]["state"] == "published"
    assert exported["publication"]["cleanup"] == "complete"
    assert exported["publication"]["durability"] == "confirmed"
    archive = (
        actor.store.path.parent / ".ontolearn-host-selections" / selection / "output.ontolearn.zip"
    ).read_bytes()
    assert hashlib.sha256(archive).hexdigest() == exported["publication"]["sha256"]
    assert len(archive) == exported["publication"]["byteLength"]
    # Deterministic bytes: a rebuilt archive is byte-identical.
    again = ok(
        exchange(
            actor,
            "project.transfer.package.export",
            {
                "projectId": project,
                "selectionId": selection,
                "checkRef": check["checkRef"],
                "operationId": exported["operationId"],
            },
        )
    )
    assert again == exported
    # A different operation re-exports identical deterministic bytes.
    fresh = ok(
        exchange(
            actor,
            "project.transfer.package.export",
            {
                "projectId": project,
                "selectionId": selection,
                "checkRef": check["checkRef"],
                "operationId": uid(),
            },
        )
    )
    assert fresh["publication"]["sha256"] == exported["publication"]["sha256"]


def test_export_rejects_moved_revision_and_unknown_check(owned):
    actor, store = owned
    project = populated_project(actor, store)
    selection = stage_outbound(
        actor, project, "package-export", ".ontolearn.zip", "output.ontolearn.zip"
    )
    revision = store.revision(store._project(project))
    check = ok(
        exchange(
            actor,
            "project.transfer.package.export.check",
            {
                "projectId": project,
                "selectionId": selection,
                "kind": "full",
                "baseRevision": revision,
                "options": OPTIONS_OFF,
            },
        )
    )
    commit_manual(
        actor,
        store,
        project,
        [
            {
                "id": digest(["urn:x:later", "urn:x:p", '"v"']),
                "subject": "urn:x:later",
                "predicate": "urn:x:p",
                "object": '"v"',
            }
        ],
    )
    denied(
        exchange(
            actor,
            "project.transfer.package.export",
            {
                "projectId": project,
                "selectionId": selection,
                "checkRef": check["checkRef"],
                "operationId": uid(),
            },
        ),
        "REVISION_CONFLICT",
    )
    denied(
        exchange(
            actor,
            "project.transfer.package.export",
            {
                "projectId": project,
                "selectionId": selection,
                "checkRef": "f" * 64,
                "operationId": uid(),
            },
        ),
        "IDENTITY_CONFLICT",
    )


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------


def build_exported_package(actor, project, kind="full", options=None):
    selection = stage_outbound(
        actor, project, "package-export", ".ontolearn.zip", "output.ontolearn.zip"
    )
    revision = actor.store.revision(actor.store._project(project))
    check = ok(
        exchange(
            actor,
            "project.transfer.package.export.check",
            {
                "projectId": project,
                "selectionId": selection,
                "kind": kind,
                "baseRevision": revision,
                "options": options or OPTIONS_OFF,
            },
        )
    )
    ok(
        exchange(
            actor,
            "project.transfer.package.export",
            {
                "projectId": project,
                "selectionId": selection,
                "checkRef": check["checkRef"],
                "operationId": uid(),
            },
        )
    )
    archive = (
        actor.store.path.parent / ".ontolearn-host-selections" / selection / "output.ontolearn.zip"
    ).read_bytes()
    return archive


def test_import_round_trip_full_restores_state(owned):
    actor, store = owned
    project = populated_project(actor, store)
    archive = build_exported_package(actor, project, "full")
    source_state = store.state(store._project(project))
    selection = stage_inbound(
        actor, project, archive, "payload.ontolearn.zip", "zip", ".ontolearn.zip"
    )
    check = ok(
        exchange(
            actor,
            "project.transfer.package.import.check",
            {"projectId": project, "selectionId": selection, "expectedKind": "full"},
        )
    )
    assert check["status"] == "compatible"
    assert check["packageSha256"] == hashlib.sha256(archive).hexdigest()
    imported = ok(
        exchange(
            actor,
            "project.transfer.package.import",
            {
                "projectId": project,
                "selectionId": selection,
                "checkRef": check["checkRef"],
                "operationId": uid(),
                "expectedKind": "full",
                "packageSha256": check["packageSha256"],
            },
        )
    )
    imported_id = imported["importedProjectId"]
    assert imported_id != project
    imported_state = store.state(store._project(imported_id))
    assert imported_state["facts"] == source_state["facts"]
    assert imported_state["definitions"] == source_state["definitions"]
    assert imported_state["mappingState"].keys() == source_state["mappingState"].keys()
    # Idempotent replay returns the identical result.
    replay = ok(
        exchange(
            actor,
            "project.transfer.package.import",
            {
                "projectId": project,
                "selectionId": selection,
                "checkRef": check["checkRef"],
                "operationId": imported["operationId"],
                "expectedKind": "full",
                "packageSha256": check["packageSha256"],
            },
        )
    )
    assert replay == imported


def test_import_template_creates_blank_named_project(owned):
    actor, store = owned
    project = populated_project(actor, store)
    archive = build_exported_package(actor, project, "template")
    selection = stage_inbound(
        actor, project, archive, "payload.ontolearn.zip", "zip", ".ontolearn.zip"
    )
    check = ok(
        exchange(
            actor,
            "project.transfer.package.import.check",
            {"projectId": project, "selectionId": selection, "expectedKind": "template"},
        )
    )
    assert check["status"] == "compatible"
    imported = ok(
        exchange(
            actor,
            "project.transfer.package.import",
            {
                "projectId": project,
                "selectionId": selection,
                "checkRef": check["checkRef"],
                "operationId": uid(),
                "expectedKind": "template",
                "packageSha256": check["packageSha256"],
            },
        )
    )
    imported_state = store.state(store._project(imported["importedProjectId"]))
    assert imported_state["facts"] == []
    assert any(d["layer"] == "ontology" for d in imported_state["definitions"])
    assert not any(d["layer"] == "mapping" for d in imported_state["definitions"])


def mutate_manifest(archive, mutate):
    """Repack an archive with a mutated canonical manifest, members intact."""
    from ontolearn_engine.storage import canonical as canonical_json

    entries = {}
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        manifest = json.loads(source.read("manifest.json"))
        for name in source.namelist():
            if name != "manifest.json":
                entries[name] = source.read(name)
    mutate(manifest)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as out:
        out.writestr("manifest.json", canonical_json(manifest).encode("utf-8"))
        for name, data in entries.items():
            out.writestr(name, data)
    return stream.getvalue()


@pytest.mark.parametrize(
    "mutation,reason",
    [
        (lambda m: m.update(formatVersion="other-v9"), "format-unsupported"),
        (lambda m: m.update(minReaderVersion=99), "reader-too-old"),
        (lambda m: m.update(minWriterVersion=99), "writer-too-old"),
        (lambda m: m.update(dbFormatVersion=2), "database-unsupported"),
        (lambda m: m.update(checkpointSchemaVersion=99), "checkpoint-unsupported"),
        (lambda m: m.update(applicationStateVersion=99), "application-unsupported"),
    ],
)
def test_import_check_rejects_versions_with_frozen_reasons(owned, mutation, reason):
    actor, store = owned
    project = populated_project(actor, store)
    archive = mutate_manifest(build_exported_package(actor, project, "full"), mutation)
    selection = stage_inbound(
        actor, project, archive, "payload.ontolearn.zip", "zip", ".ontolearn.zip"
    )
    result = ok(
        exchange(
            actor,
            "project.transfer.package.import.check",
            {"projectId": project, "selectionId": selection, "expectedKind": "full"},
        )
    )
    assert result["status"] == "rejected" and result["reason"] == reason


def test_import_check_rejects_kind_mismatch_and_unsafe_members(owned):
    actor, store = owned
    project = populated_project(actor, store)
    mismatch = mutate_manifest(
        build_exported_package(actor, project, "full"), lambda m: m.update(kind="template")
    )
    selection = stage_inbound(
        actor, project, mismatch, "payload.ontolearn.zip", "zip", ".ontolearn.zip"
    )
    result = ok(
        exchange(
            actor,
            "project.transfer.package.import.check",
            {"projectId": project, "selectionId": selection, "expectedKind": "full"},
        )
    )
    assert result == {
        "projectId": project,
        "selectionId": selection,
        "expectedKind": "full",
        "status": "rejected",
        "reason": "kind-mismatch",
    }
    # An extra unlisted member makes the whole package unsafe.
    archive = build_exported_package(actor, project, "full")
    stream = io.BytesIO()
    with (
        zipfile.ZipFile(io.BytesIO(archive)) as source,
        zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as out,
    ):
        for name in source.namelist():
            out.writestr(name, source.read(name))
        out.writestr("data/extra.json", b"{}")
    unsafe = stage_inbound(
        actor, project, stream.getvalue(), "payload.ontolearn.zip", "zip", ".ontolearn.zip"
    )
    result = ok(
        exchange(
            actor,
            "project.transfer.package.import.check",
            {"projectId": project, "selectionId": unsafe, "expectedKind": "full"},
        )
    )
    assert result["status"] == "rejected" and result["reason"] == "unsafe-package"


def test_import_execute_rejects_hash_drift(owned):
    actor, store = owned
    project = populated_project(actor, store)
    archive = build_exported_package(actor, project, "full")
    selection = stage_inbound(
        actor, project, archive, "payload.ontolearn.zip", "zip", ".ontolearn.zip"
    )
    check = ok(
        exchange(
            actor,
            "project.transfer.package.import.check",
            {"projectId": project, "selectionId": selection, "expectedKind": "full"},
        )
    )
    denied(
        exchange(
            actor,
            "project.transfer.package.import",
            {
                "projectId": project,
                "selectionId": selection,
                "checkRef": check["checkRef"],
                "operationId": uid(),
                "expectedKind": "full",
                "packageSha256": "0" * 64,
            },
        ),
        "IDENTITY_CONFLICT",
    )


# ---------------------------------------------------------------------------
# FR-901 credential scan
# ---------------------------------------------------------------------------


def test_credential_scan_patterns_and_redaction():
    assert scan_text("普通文本") == "clear"
    for secret in (
        "AKIAIOSFODNN7EXAMPLE",
        "api_key: abcdEFGH12345678",
        "password = sup3rSecret9",
        "Bearer eyJhbGciOi.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
        "-----BEGIN RSA PRIVATE KEY-----",
        "xoxb-1234567890abcdef",
        "AIzaSyA1234567890abcdefghijklmnopqrstuv",
    ):
        with pytest.raises(CredentialLeak):
            scan_text(f"前置 {secret} 后置")
    assert scan_text("密钥已遮蔽 [REDACTED] 其余安全") == "redacted"
    assert scan_projection({"a": ["x"], "b": {"c": "clear"}, "d": 3, "e": None}) == "clear"
    with pytest.raises(CredentialLeak):
        scan_projection({"title": "AKIAIOSFODNN7EXAMPLE"})


from ontolearn_engine.transfer.credential_scan import scan_text  # noqa: E402


def test_export_rejects_unredacted_secret_without_echoing(owned):
    actor, store = owned
    project = populated_project(actor, store)
    # A credential-shaped value inside a mapped fact's free text.
    secret_value = '"AKIAIOSFODNN7EXAMPLE"'
    internal = store._project(project)
    revision = store.revision(internal)
    store.commit(
        internal,
        revision,
        uid(),
        uid(),
        manual=[
            {
                "id": digest(["urn:x:leak", "urn:x:note", secret_value]),
                "subject": "urn:x:leak",
                "predicate": "urn:x:note",
                "object": secret_value,
            }
        ],
    )
    selection = stage_outbound(
        actor, project, "package-export", ".ontolearn.zip", "output.ontolearn.zip"
    )
    response = exchange(
        actor,
        "project.transfer.package.export.check",
        {
            "projectId": project,
            "selectionId": selection,
            "kind": "full",
            "baseRevision": store.revision(internal),
            "options": OPTIONS_OFF,
        },
    )
    error = denied(response, "PERMISSION_DENIED")
    assert "AKIA" not in json.dumps(error)


def test_report_prepare_rejects_secret_in_learning_text(owned):
    actor, store = owned
    project = open_blank(actor, name="AKIAIOSFODNN7EXAMPLE 泄露项目")
    denied(
        exchange(
            actor,
            "project.transfer.report.prepare",
            {"projectId": project, "baseRevision": store.revision(store._project(project))},
        ),
        "PERMISSION_DENIED",
    )


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def ledger_record(
    task_id,
    attempt,
    *,
    transfer=True,
    complete=True,
    hint_level=0,
    assistance="independent",
    check="passed",
    evidence=("ev-1",),
):
    return {
        "attempt": attempt,
        "withdrawn": False,
        "payload": {
            "taskId": task_id,
            "operationComplete": complete,
            "maxHintLevel": hint_level,
            "assistance": assistance,
            "checkStatus": check,
            "evidenceIds": list(evidence),
            "lastFeedback": None,
            "completedGuidedStages": [],
        },
    }


def transfer_tasks():
    return {
        "transfer-repair": {
            "transfer": True,
            "hints": [
                {"kind": "concept"},
                {"kind": "operation"},
                {"kind": "partial-demonstration"},
                {"kind": "full-demonstration"},
            ],
        },
        "transfer-classify": {"transfer": True, "hints": []},
        "business-ontology": {"transfer": False, "hints": []},
    }


def test_independent_transfer_rule_is_strict():
    tasks = transfer_tasks()
    # The one genuine independent success.
    attempts = learning_attempts([ledger_record("transfer-repair", "a1")], tasks)
    assert attempts[0]["independentTransferSuccess"] is True
    variants = [
        ledger_record("transfer-repair", "a2", complete=False),  # UI-only completion
        ledger_record("transfer-repair", "a4", check="needs-repair"),
        ledger_record("transfer-repair", "a5", evidence=()),  # no persisted evidence
        ledger_record("transfer-repair", "a6", hint_level=4),  # full demonstration
        ledger_record("transfer-repair", "a7", hint_level=3),  # partial hint
        ledger_record("transfer-repair", "a8", assistance="agent-full-assistance"),
        ledger_record("business-ontology", "a9"),  # non-transfer task passing
    ]
    projected = learning_attempts(variants, tasks)
    assert all(not attempt["independentTransferSuccess"] for attempt in projected)
    by_id = {attempt["attemptId"]: attempt for attempt in projected}
    assert by_id["a9"]["transferTask"] is False
    assert by_id["a6"]["hint"] == "full"
    assert by_id["a7"]["hint"] == "partial"
    assert by_id["a8"]["agentAssistance"] == "full"
    assert by_id["a2"]["operationCompleted"] is False


def test_report_prepare_export_and_csp_safe_escaping(owned):
    actor, store = owned
    project = open_blank(actor, name='报告 <script>alert("x")</script>')
    revision = store.revision(store._project(project))
    prepared = ok(
        exchange(
            actor,
            "project.transfer.report.prepare",
            {"projectId": project, "baseRevision": revision},
        )
    )
    assert prepared["state"] == "prepared"
    assert prepared["report"]["projectionVersion"] == "ontolearn-report-v1"
    assert prepared["credentialScan"] == {"version": 1, "status": "clear"}
    selection = stage_outbound(actor, project, "report-html", ".html", "output.html")
    exported = ok(
        exchange(
            actor,
            "project.transfer.report.export",
            {
                "projectId": project,
                "selectionId": selection,
                "reportRef": prepared["reportRef"],
                "baseRevision": revision,
                "operationId": uid(),
            },
        )
    )
    assert exported["format"] == "html"
    assert exported["publication"]["state"] == "published"
    html_text = (
        actor.store.path.parent / ".ontolearn-host-selections" / selection / "output.html"
    ).read_text()
    assert "<script>alert" not in html_text
    assert "&lt;script&gt;" in html_text
    assert "<script" not in html_text.replace("<style>", "").replace("</style>", "")
    # Replay is idempotent.
    replay = ok(
        exchange(
            actor,
            "project.transfer.report.export",
            {
                "projectId": project,
                "selectionId": selection,
                "reportRef": prepared["reportRef"],
                "baseRevision": revision,
                "operationId": exported["operationId"],
            },
        )
    )
    assert replay == exported


def test_report_export_rejects_moved_revision(owned):
    actor, store = owned
    project = open_blank(actor, name="版本报告")
    revision = store.revision(store._project(project))
    prepared = ok(
        exchange(
            actor,
            "project.transfer.report.prepare",
            {"projectId": project, "baseRevision": revision},
        )
    )
    selection = stage_outbound(actor, project, "report-html", ".html", "output.html")
    commit_manual(
        actor,
        store,
        project,
        [
            {
                "id": digest(["urn:x:r", "urn:x:p", '"v"']),
                "subject": "urn:x:r",
                "predicate": "urn:x:p",
                "object": '"v"',
            }
        ],
    )
    denied(
        exchange(
            actor,
            "project.transfer.report.export",
            {
                "projectId": project,
                "selectionId": selection,
                "reportRef": prepared["reportRef"],
                "baseRevision": revision,
                "operationId": uid(),
            },
        ),
        "REVISION_CONFLICT",
    )


# ---------------------------------------------------------------------------
# Seeded property tests (Hypothesis-tradition, deterministic generator)
# ---------------------------------------------------------------------------


def test_property_manifest_zip_round_trip_invariants():
    rng = random.Random(1120)
    for _ in range(10):
        roles = ["definitions"]
        if rng.random() < 0.7:
            roles += ["assertions", "ownership", "checkpoint"]
        kind = "full" if len(roles) == 4 else "template"
        options = {key: rng.random() < 0.3 for key in OPTIONS_OFF}
        entries = {role: json.dumps({role: rng.randint(0, 100)}).encode() for role in roles}
        manifest = transfer_package.build_manifest(kind, options, entries)
        raw = transfer_package.build_archive(manifest, entries)
        inspected = transfer_package.inspect_v1(raw, kind)
        assert inspected.manifest == manifest
        assert set(inspected.entries) == {file["path"] for file in manifest["files"]}
        # Invariant: every member hash matches its content and the archive
        # never contains an unlisted path.
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            assert set(archive.namelist()) == set(inspected.entries) | {"manifest.json"}
        # Mutation of any single byte in a member body invalidates the package.
        body = bytearray(raw)
        index = body.find(b'{"definitions"')
        body[index] ^= 1
        with pytest.raises(transfer_package.PackageError):
            transfer_package.inspect_v1(bytes(body), kind)


def test_property_builder_rejects_role_option_violations():
    rng = random.Random(808)
    for _ in range(10):
        include_optional = rng.random() < 0.5
        options = {**OPTIONS_OFF, "history": include_optional}
        entries = {"definitions": b"{}"}
        if include_optional and rng.random() < 0.8:
            entries["history"] = b"[]"
        manifest = transfer_package.build_manifest("template", options, entries)
        roles = {file["role"] for file in manifest["files"]}
        assert ("history" in roles) <= options["history"]
        # Forcing a forbidden role with its option off is rejected outright.
        if not include_optional:
            with pytest.raises(transfer_package.PackageError):
                transfer_package.build_manifest(
                    "template", options, {"definitions": b"{}", "history": b"[]"}
                )
        with pytest.raises(transfer_package.PackageError):
            transfer_package.build_manifest("template", OPTIONS_OFF, {"vault": b"{}"})
