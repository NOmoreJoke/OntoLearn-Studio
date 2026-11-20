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
import struct
import zipfile
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import digest
from ontolearn_engine.transfer import package as transfer_package
from ontolearn_engine.transfer.credential_scan import (
    CredentialLeak,
    host_path_marker,
    scan_projection,
)
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


def _synthetic_member(role, seed):
    """Structurally valid v1 member payloads for the seeded generator."""
    if role == "definitions":
        return json.dumps(
            {
                "definitions": [
                    {"layer": "ontology", "id": f"G{seed}", "payload": json.dumps({"seed": seed})}
                ]
            }
        ).encode()
    shapes = {
        "assertions": {"facts": []},
        "ownership": {"mappingState": {}},
        "checkpoint": {
            "domainRevision": seed,
            "operationSequence": seed,
            "metadata": {},
            "metadataVersion": seed,
        },
        "agent-session": {"learning": []},
        "history": {"operations": []},
    }
    return json.dumps(shapes[role]).encode()


def test_property_manifest_zip_round_trip_invariants():
    rng = random.Random(1120)
    for seed in range(10):
        roles = ["definitions"]
        if rng.random() < 0.7:
            roles += ["assertions", "ownership", "checkpoint"]
        kind = "full" if len(roles) == 4 else "template"
        options = {key: rng.random() < 0.3 for key in OPTIONS_OFF}
        entries = {role: _synthetic_member(role, seed) for role in roles}
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
        entries = {"definitions": _synthetic_member("definitions", 0)}
        if include_optional and rng.random() < 0.8:
            entries["history"] = _synthetic_member("history", 0)
        manifest = transfer_package.build_manifest("template", options, entries)
        roles = {file["role"] for file in manifest["files"]}
        assert ("history" in roles) <= options["history"]
        # Forcing a forbidden role with its option off is rejected outright.
        if not include_optional:
            with pytest.raises(transfer_package.PackageError):
                transfer_package.build_manifest(
                    "template", options, {**entries, "history": _synthetic_member("history", 0)}
                )
        with pytest.raises(transfer_package.PackageError):
            transfer_package.build_manifest("template", OPTIONS_OFF, {"vault": b"{}"})


# ---------------------------------------------------------------------------
# W4 R2 regression: FD hygiene, atomic import, path hygiene, full fidelity,
# strict version/member inspection, ZIP envelope consistency, SQL caps
# ---------------------------------------------------------------------------


def member_bytes(archive, name):
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        return source.read(name)


def all_member_text(archive):
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        return [source.read(name).decode("utf-8", errors="replace") for name in source.namelist()]


def repack_member(archive, path, payload):
    """Repack with one member's bytes replaced and its manifest entry fixed."""
    from ontolearn_engine.storage import canonical as canonical_json

    entries = {}
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        manifest = json.loads(source.read("manifest.json"))
        for name in source.namelist():
            if name != "manifest.json":
                entries[name] = source.read(name)
    entries[path] = payload
    for record in manifest["files"]:
        if record["path"] == path:
            record["size"] = len(payload)
            record["sha256"] = hashlib.sha256(payload).hexdigest()
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as out:
        out.writestr("manifest.json", canonical_json(manifest).encode("utf-8"))
        for name, data in entries.items():
            out.writestr(name, data)
    return stream.getvalue()


def public_project_count(store):
    return store._db.execute("SELECT count(*) FROM public_projects").fetchone()[0]


def import_receipt_count(store):
    return store._db.execute(
        "SELECT count(*) FROM job_details WHERE id LIKE 'transfer-import:%'"
    ).fetchone()[0]


def job_details_count(store):
    return store._db.execute("SELECT count(*) FROM job_details").fetchone()[0]


def import_full(actor, store, project, archive, operation=None):
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
    imported = ok(
        exchange(
            actor,
            "project.transfer.package.import",
            {
                "projectId": project,
                "selectionId": selection,
                "checkRef": check["checkRef"],
                "operationId": operation or uid(),
                "expectedKind": "full",
                "packageSha256": check["packageSha256"],
            },
        )
    )
    return imported


def test_write_outbound_never_leaks_file_descriptors(owned):
    # W4-05: every publish (and every faulting publish) closes its verify FD.
    actor, store = owned
    project = open_blank(actor, "描述符项目")
    revision = store.revision(store._project(project))
    prepared = ok(
        exchange(
            actor,
            "project.transfer.report.prepare",
            {"projectId": project, "baseRevision": revision},
        )
    )
    selection = stage_outbound(actor, project, "report-html", ".html", "output.html")
    export_args = {
        "projectId": project,
        "baseRevision": revision,
        "selectionId": selection,
        "reportRef": prepared["reportRef"],
        "operationId": uid(),
    }
    before = len(os.listdir("/dev/fd"))
    for _ in range(5):
        ok(
            exchange(
                actor,
                "project.transfer.report.export",
                {**export_args, "operationId": uid()},
            )
        )
    # Fault path: an existing non-regular target must fault after the temp
    # verification open, with the verify FD still released every time.
    folder = actor.store.path.parent / ".ontolearn-host-selections" / selection
    (folder / "output.html").unlink()
    (folder / "output.html").mkdir()
    for _ in range(3):
        denied(
            exchange(
                actor,
                "project.transfer.report.export",
                {**export_args, "operationId": uid()},
            ),
            "INVALID_STATE",
        )
    after = len(os.listdir("/dev/fd"))
    assert before == after, (before, after)


def test_import_operation_conflict_and_mid_failure_leave_zero_residue(owned):
    # W4-01: reused operationId conflicts and mid-transaction failures both
    # leave public_projects and the import receipts with a zero-row increment.
    actor, store = owned
    project = populated_project(actor, store)
    archive = build_exported_package(actor, project, "full")
    operation = uid()
    first = import_full(actor, store, project, archive, operation=operation)
    projects_before = public_project_count(store)
    receipts_before = import_receipt_count(store)
    # Same operationId with a different request hash is a pure conflict.
    denied(
        exchange(
            actor,
            "project.transfer.package.import",
            {
                "projectId": project,
                "selectionId": first["selectionId"],
                "checkRef": first["checkRef"],
                "operationId": operation,
                "expectedKind": "full",
                "packageSha256": "0" * 64,
            },
        ),
        "IDENTITY_CONFLICT",
    )
    assert public_project_count(store) == projects_before
    assert import_receipt_count(store) == receipts_before
    # A package whose managed rows collide on one fact id fails mid-import
    # (inside the outer transaction, after the project was created).
    facts = json.loads(member_bytes(archive, "data/assertions.json"))["facts"]
    managed = next(fact for fact in facts if fact["owner"] is not None)
    duplicate = {**managed, "sourceRow": "row-collides"}
    facts.append(duplicate)
    broken = repack_member(
        archive, "data/assertions.json", json.dumps({"facts": facts}, ensure_ascii=False).encode()
    )
    selection = stage_inbound(
        actor, project, broken, "payload.ontolearn.zip", "zip", ".ontolearn.zip"
    )
    check = ok(
        exchange(
            actor,
            "project.transfer.package.import.check",
            {"projectId": project, "selectionId": selection, "expectedKind": "full"},
        )
    )
    response = exchange(
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
    assert not response["ok"] and response["error"]["code"] == "INVALID_REQUEST", response
    assert public_project_count(store) == projects_before
    assert import_receipt_count(store) == receipts_before
    # A fresh operationId imports the good package successfully afterwards.
    retry = import_full(actor, store, project, archive)
    assert retry["importedProjectId"] != project
    assert public_project_count(store) == projects_before + 1


def test_export_rejects_raw_sources_and_derived_options(owned):
    # W4-03: the format cannot carry raw sources or derived copies, so the
    # check refuses those options instead of silently omitting their members.
    actor, store = owned
    project = open_blank(actor, "选项项目")
    selection = stage_outbound(
        actor, project, "package-export", ".ontolearn.zip", "output.ontolearn.zip"
    )
    revision = store.revision(store._project(project))
    for key in ("rawSources", "derived"):
        denied(
            exchange(
                actor,
                "project.transfer.package.export.check",
                {
                    "projectId": project,
                    "selectionId": selection,
                    "kind": "full",
                    "baseRevision": revision,
                    "options": {**OPTIONS_OFF, key: True},
                },
            ),
            "INVALID_REQUEST",
        )


def test_export_scrubs_host_absolute_paths_from_package_bytes(owned):
    # W4-02: host absolute paths in free text never reach any archive byte;
    # ordinary Chinese names and urn: IRIs stay byte-identical.
    actor, store = owned
    hostile_names = [
        "/Users/kyle/lib/secret 项目",
        "C:\\Users\\kyle\\secret 项目",
        "共享 .ontolearn-host-selections/sel 拼接",
        "file:///Users/kyle/secret 项目",
    ]
    for name in hostile_names:
        project = open_blank(actor, name)
        archive = build_exported_package(actor, project, "full")
        texts = all_member_text(archive)
        assert not any(host_path_marker(text) for text in texts), name
        checkpoint_text = member_bytes(archive, "data/checkpoint.json").decode("utf-8")
        assert "<local-path>" in checkpoint_text
    # Clean business text survives byte-for-byte.
    clean = populated_project(actor, store)
    archive = build_exported_package(actor, clean, "full")
    texts = all_member_text(archive)
    assert any("完整项目" in text for text in texts)
    assert any("urn:x:equipment/001" in text for text in texts)


def test_report_html_scrubs_host_absolute_paths(owned):
    # W4-02: the report title is sanitized before any HTML byte is staged.
    actor, store = owned
    project = open_blank(actor, "/private/var/db/机密 项目")
    revision = store.revision(store._project(project))
    prepared = ok(
        exchange(
            actor,
            "project.transfer.report.prepare",
            {"projectId": project, "baseRevision": revision},
        )
    )
    assert "<local-path>" in prepared["report"]["title"]
    selection = stage_outbound(actor, project, "report-html", ".html", "output.html")
    ok(
        exchange(
            actor,
            "project.transfer.report.export",
            {
                "projectId": project,
                "baseRevision": revision,
                "selectionId": selection,
                "reportRef": prepared["reportRef"],
                "operationId": uid(),
            },
        )
    )
    html_text = (
        actor.store.path.parent / ".ontolearn-host-selections" / selection / "output.html"
    ).read_text()
    assert "/private/var" not in html_text
    # The placeholder is escaped like every dynamic string in the CSP-safe HTML.
    assert "&lt;local-path&gt;" in html_text


def test_full_round_trip_restores_edited_managed_fact_exactly(owned):
    # W4-03: a managed fact edited in the Store round-trips with its exact
    # owner/source_row/managed_value/object quartet and identical ownership.
    actor, store = owned
    project = populated_project(actor, store)
    internal = store._project(project)
    drift_id = digest(["urn:x:equipment/003", "urn:x:name", '"C"'])
    store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        edits={drift_id: '"泵站C-手改"'},
    )
    source_state = store.state(internal)
    source_fact = next(fact for fact in source_state["facts"] if fact["id"] == drift_id)
    assert source_fact["owner"] == "equip-map"
    assert source_fact["managed_value"] == '"C"'
    assert source_fact["object"] == '"泵站C-手改"'
    archive = build_exported_package(actor, project, "full")
    imported = import_full(actor, store, project, archive)
    imported_state = store.state(store._project(imported["importedProjectId"]))
    assert imported_state["facts"] == source_state["facts"]
    assert imported_state["mappingState"] == source_state["mappingState"]
    # Re-exporting the imported project reproduces the ownership member bytes.
    ok(exchange(actor, "project.open", {"projectId": imported["importedProjectId"]}))
    archive2 = build_exported_package(actor, imported["importedProjectId"], "full")
    assert member_bytes(archive2, "data/ownership.json") == member_bytes(
        archive, "data/ownership.json"
    )


def test_full_round_trip_restores_managed_tombstone_exactly(owned):
    # W4-03: a removed managed fact (tombstone) round-trips as a tombstone.
    actor, store = owned
    project = populated_project(actor, store)
    internal = store._project(project)
    tombstone_id = digest(["urn:x:equipment/003", "urn:x:name", '"C"'])
    store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        remove=[tombstone_id],
    )
    source_state = store.state(internal)
    source_fact = next(fact for fact in source_state["facts"] if fact["id"] == tombstone_id)
    assert source_fact["owner"] == "equip-map" and source_fact["object"] is None
    archive = build_exported_package(actor, project, "full")
    imported = import_full(actor, store, project, archive)
    imported_state = store.state(store._project(imported["importedProjectId"]))
    assert imported_state["facts"] == source_state["facts"]
    assert imported_state["mappingState"] == source_state["mappingState"]


def test_full_package_restores_agent_sessions_and_preserves_history(owned):
    # W4-03: agentSessions genuinely restores the learning ledger; history is
    # preserved verbatim in the durable import receipt and portability no
    # longer claims it is missing.
    actor, store = owned
    project = populated_project(actor, store)
    attempt = uid()
    payload = {
        "taskId": "transfer-repair",
        "operationComplete": True,
        "maxHintLevel": 0,
        "assistance": "independent",
        "checkStatus": "passed",
        "evidenceIds": ["ev-1"],
        "lastFeedback": None,
        "completedGuidedStages": [],
    }
    change = {
        "type": "learning.record",
        "attempt": attempt,
        "course": "检修",
        "task": "transfer-repair",
        "expectedRecordVersion": None,
        "payload": payload,
        "assistanceEvent": None,
    }
    writer = uid()
    prepared = store.prepare_application(project, change, actor=writer, permission="write")
    store.apply_application(
        project,
        uid(),
        change,
        actor=writer,
        permission="write",
        prepared_plan_ref=prepared["preparedPlanRef"],
        confirmation_ref=prepared["confirmationRef"],
    )
    options = {**OPTIONS_OFF, "agentSessions": True, "history": True}
    archive = build_exported_package(actor, project, "full", options)
    learning_member = json.loads(member_bytes(archive, "data/agent-session.json"))
    assert [row["attempt"] for row in learning_member["learning"]] == [attempt]
    history_member = json.loads(member_bytes(archive, "data/history.json"))
    assert history_member["operations"]
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
    assert "history" not in check["portability"]["missing"]
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
    checkpoint = store.project_checkpoint(store._project(imported["importedProjectId"]))
    rows = {row["attempt"]: row for row in checkpoint["application"]["learningCurrent"]}
    assert attempt in rows
    assert json.loads(rows[attempt]["payload"]) == payload
    receipt = json.loads(
        store._db.execute(
            "SELECT payload FROM job_details WHERE id=?",
            ("transfer-import:" + imported["operationId"],),
        ).fetchone()[0]
    )
    assert receipt["history"] == history_member["operations"]


@pytest.mark.parametrize(
    "mutation,reason",
    [
        (lambda m: m.update(checkpointSchemaVersion=0), "checkpoint-unsupported"),
        (lambda m: m.update(checkpointSchemaVersion=True), "checkpoint-unsupported"),
        (lambda m: m.update(applicationStateVersion="bad"), "application-unsupported"),
        (lambda m: m.update(checkpointSchemaVersion=-1), "checkpoint-unsupported"),
    ],
)
def test_import_check_rejects_mistyped_versions_without_writing(owned, mutation, reason):
    # W4-07: 0/True/negative/string version fields are rejected structurally
    # (never INTERNAL_ERROR) and never write a check receipt.
    actor, store = owned
    project = populated_project(actor, store)
    archive = mutate_manifest(build_exported_package(actor, project, "full"), mutation)
    selection = stage_inbound(
        actor, project, archive, "payload.ontolearn.zip", "zip", ".ontolearn.zip"
    )
    before = job_details_count(store)
    result = ok(
        exchange(
            actor,
            "project.transfer.package.import.check",
            {"projectId": project, "selectionId": selection, "expectedKind": "full"},
        )
    )
    assert result["status"] == "rejected" and result["reason"] == reason
    assert job_details_count(store) == before


def test_import_check_rejects_malformed_member_payload_without_writing(owned):
    # W4-07: a structurally invalid member payload is rejected up front and
    # leaves job_details untouched.
    actor, store = owned
    project = populated_project(actor, store)
    archive = build_exported_package(actor, project, "full")
    broken = repack_member(archive, "data/definitions.json", b'{"definitions": 42}')
    selection = stage_inbound(
        actor, project, broken, "payload.ontolearn.zip", "zip", ".ontolearn.zip"
    )
    before = job_details_count(store)
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
        "reason": "unsafe-package",
    }
    assert job_details_count(store) == before


def prepend_unindexed(raw, prefix):
    # Make an otherwise valid central directory point past arbitrary bytes.
    changed = bytearray(prefix + raw)
    central = struct.unpack_from("<I", raw, len(raw) - 6)[0]
    position = len(prefix) + central
    while changed[position : position + 4] == b"PK\x01\x02":
        old = struct.unpack_from("<I", changed, position + 42)[0]
        struct.pack_into("<I", changed, position + 42, old + len(prefix))
        name, extra, comment = struct.unpack_from("<3H", changed, position + 28)
        position += 46 + name + extra + comment
    struct.pack_into("<I", changed, len(changed) - 6, central + len(prefix))
    return bytes(changed)


def test_inspect_rejects_local_header_tampering_and_unindexed_bytes(owned):
    # W4-11: local headers must agree with the central directory, and members
    # must cover the archive contiguously from offset 0 to the central start.
    actor, store = owned
    project = populated_project(actor, store)
    archive = build_exported_package(actor, project, "full")
    # Tamper only the first local header's general-purpose flags.
    tampered = bytearray(archive)
    local = tampered.find(b"PK\x03\x04")
    struct.pack_into("<H", tampered, local + 6, 1)
    with pytest.raises(transfer_package.PackageError):
        transfer_package.inspect_v1(bytes(tampered), "full")
    # Unindexed padding bytes before the first member break the layout.
    with pytest.raises(transfer_package.PackageError):
        transfer_package.inspect_v1(prepend_unindexed(archive, b"unindexed-private-bytes"), "full")


def test_history_and_result_scan_caps_live_in_ordered_sql(owned):
    # W4-13: caps and ordering are enforced inside the SQL statement, never by
    # a Python slice after fetchall.
    actor, store = owned
    from ontolearn_engine.transfer import report as transfer_report
    from ontolearn_engine.transfer import service as transfer_service

    project = open_blank(actor, "上限项目")
    internal = store._project(project)

    class _Rollback(Exception):
        pass

    try:
        with store._transaction():
            # Seed a plain ledger slice larger than the cap; the pure SQL
            # accessor must return exactly the cap, in ascending sequence order.
            for sequence in range(2, 252):
                store._db.execute(
                    "INSERT INTO app_operations VALUES(?,?,?,?,?,?)",
                    (internal, sequence, f"seed-{sequence}", "application", "0" * 64, 0),
                )
            rows = transfer_service._history_operations(store, internal)
            assert len(rows) == transfer_service.HISTORY_LIMIT
            sequences = [row[0] for row in rows]
            assert sequences == sorted(sequences)
            # The result scan keeps the same discipline over the results join.
            snapshot = store.snapshot(internal)
            dto = json.dumps(
                {
                    "capability": "query.execute",
                    "state": "succeeded",
                    "input": {"scope": "asserted"},
                    "implementation": {"executionSemanticsVersion": "changeset-v1"},
                }
            )
            projection = json.dumps({"inputProjectRevision": 1, "summary": "s"})
            for index in range(transfer_report.RESULT_SCAN_CAP + 50):
                store._db.execute(
                    "INSERT INTO results VALUES(?,?,?,?,?,?,?,?)",
                    (f"seed-result-{index}", internal, snapshot, "query", "[]", "{}", "k", "{}"),
                )
                store._db.execute(
                    "INSERT INTO jobs VALUES(?,?,?,?,?,?,?)",
                    (f"seed-job-{index}", project, f"seed-op-{index}", dto, "{}", "f", None),
                )
                store._db.execute(
                    "INSERT INTO job_results VALUES(?,?,?,?,?)",
                    (f"seed-result-{index}", f"seed-job-{index}", None, projection, 0),
                )
            query_rows, validation_rows = transfer_report._semantic_results(store, internal)
            assert len(query_rows) == transfer_report.RESULT_SCAN_CAP
            assert validation_rows == []
            raise _Rollback
    except _Rollback:
        pass
    # The seeding transaction rolled back; nothing persisted.
    assert (
        store._db.execute("SELECT count(*) FROM results WHERE id LIKE 'seed-result-%'").fetchone()[
            0
        ]
        == 0
    )
