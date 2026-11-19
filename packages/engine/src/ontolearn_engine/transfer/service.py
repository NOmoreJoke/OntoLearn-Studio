"""T10 transfer wire services: project package v1 and HTML report v1.

Six ``business3`` methods over the owned Store and the frozen staging
protocol. Export rebuilds every package byte deterministically from real
state, re-runs the FR-901 credential scan on the actual serialized projection
before any archive/report byte is generated, and publishes through the staged
outbound selection atomically (0o600 temp + fsync + replace). Import validates
the full v1 contract defensively, refuses version/kind/unsafe packages with
the frozen reasons, and materializes a brand-new imported project through the
ordinary single-writer Store path - never touching an existing project id or
ownership. Raw OS paths never appear in any DTO, error or log.
"""

import json
from uuid import uuid4

from ontolearn_engine.project import staging
from ontolearn_engine.project.ontology_turtle import resolve_active
from ontolearn_engine.storage import Conflict, canonical, digest
from ontolearn_engine.transfer import package as transfer_package
from ontolearn_engine.transfer import report as transfer_report
from ontolearn_engine.transfer.credential_scan import CredentialLeak, scan_projection

METHODS = frozenset(
    {
        "project.transfer.package.export.check",
        "project.transfer.package.export",
        "project.transfer.package.import.check",
        "project.transfer.package.import",
        "project.transfer.report.prepare",
        "project.transfer.report.export",
    }
)
HISTORY_LIMIT = 200
TEMPLATE_NAME = "导入模板"


def fault(code, **params):
    from ontolearn_engine.job_store import fault as job_fault

    job_fault(code, **params)


def _staging_fault(error):
    code, params = staging.fault_for(error.code)
    fault(code, **params)


def _credential_fault():
    # FR-901: fixed rejection, never echoing the secret material.
    fault("PERMISSION_DENIED")


def _conflict_policy(kind, options):
    return {
        "version": 1,
        "ownership": "reject",
        "projectIdentity": "new-project-id",
        "fingerprint": digest(
            {
                "conflictPolicyVersion": 1,
                "formatVersion": transfer_package.FORMAT_VERSION,
                "kind": kind,
                "options": options,
            }
        ),
    }


def _portability(kind, options, entries):
    missing = ["raw-source", "scenario-input", "scenario-configuration", "execution-semantics"]
    has_mapping_definition = any(
        record["layer"] == "mapping" for record in entries.get("definitions_records", [])
    )
    if not has_mapping_definition:
        missing.append("mapping-definition")
    if not options.get("history"):
        missing.append("history")
    return {
        "restoreCurrent": kind == "full",
        "rerunMapping": False,  # raw sources are never packaged in v1
        "replayScenario": False,  # scenario payloads are not portable in v1
        "missing": missing,
    }


def _collect_entries(store, project, internal, kind, options):
    """Deterministic canonical member payloads from real current state."""
    state = store.state(internal)
    checkpoint = store.project_checkpoint(internal)
    definitions = [dict(record) for record in state["definitions"]]
    if kind == "template":
        definitions = [record for record in definitions if record["layer"] != "mapping"]
    facts = [dict(record) for record in state["facts"]]
    if kind == "template":
        facts = []
    entries = {
        "definitions": canonical(
            {
                "definitions": [
                    {"layer": record["layer"], "id": record["id"], "payload": record["payload"]}
                    for record in definitions
                ]
            }
        ).encode("utf-8")
    }
    if kind == "full":
        # Only a full package carries instance assertions, mapping ownership
        # and the checkpoint of live state; a template is definitions-only.
        entries["assertions"] = canonical(
            {
                "facts": [
                    {
                        "id": fact["id"],
                        "subject": fact["subject"],
                        "predicate": fact["predicate"],
                        "object": fact["object"],
                        "owner": fact["owner"],
                        "sourceRow": fact["source_row"],
                        "managedValue": fact["managed_value"],
                    }
                    for fact in facts
                ]
            }
        ).encode("utf-8")
        entries["ownership"] = canonical(
            {
                "mappingState": {
                    owner: status for owner, status in sorted(state["mappingState"].items())
                }
            }
        ).encode("utf-8")
        entries["checkpoint"] = canonical(
            {
                "domainRevision": checkpoint["domainRevision"],
                "operationSequence": checkpoint["operationSequence"],
                "metadata": checkpoint["application"]["metadata"],
                "metadataVersion": checkpoint["application"]["metadataVersion"],
            }
        ).encode("utf-8")
        if options.get("agentSessions"):
            entries["agent-session"] = canonical(
                {
                    "learning": [
                        {
                            "attempt": row["attempt"],
                            "recordVersion": row["record_version"],
                            "course": row["course"],
                            "task": row["task"],
                            "payload": row["payload"],
                        }
                        for row in checkpoint["application"]["learningCurrent"]
                    ]
                }
            ).encode("utf-8")
    if kind == "full" and options.get("history"):
        rows = store._db.execute(
            "SELECT sequence,operation,kind FROM app_operations WHERE project=? ORDER BY sequence",
            (internal,),
        ).fetchall()[:HISTORY_LIMIT]
        entries["history"] = canonical(
            {
                "operations": [
                    {"sequence": row[0], "operationId": row[1], "operationKind": row[2]}
                    for row in rows
                ]
            }
        ).encode("utf-8")
    return entries, definitions, facts, checkpoint


def _business_projection(definitions, facts, checkpoint):
    """The FR-901 free-text surface of an outbound package."""
    projection = {
        "definitions": [
            {"layer": record["layer"], "id": record["id"], "payload": json.loads(record["payload"])}
            for record in definitions
        ],
        "facts": [fact["object"] for fact in facts if fact["object"] is not None],
        "name": checkpoint["application"]["metadata"].get("name"),
        "learning": checkpoint["application"]["learningCurrent"],
    }
    return projection


def _export_check(store, params, origin, host):
    project = params["projectId"]
    internal = resolve_active(store, project)
    selection_id = params["selectionId"]
    kind, options = params["kind"], params["options"]
    try:
        staging.verify_outbound(
            store, project, origin["engineSessionId"], selection_id, "package-export"
        )
    except staging.StagingFault as error:
        _staging_fault(error)
    if store.revision(internal) != params["baseRevision"]:
        fault("REVISION_CONFLICT", expected=params["baseRevision"], actual=store.revision(internal))
    entries, definitions, facts, checkpoint = _collect_entries(
        store, project, internal, kind, options
    )
    try:
        scan_projection(_business_projection(definitions, facts, checkpoint))
    except CredentialLeak:
        _credential_fault()
    manifest = transfer_package.build_manifest(kind, options, entries)
    envelope = {
        "transferExportCheckVersion": 1,
        "projectId": project,
        "engineSessionId": origin["engineSessionId"],
        "hostClientId": origin["hostClientId"],
        "selectionId": selection_id,
        "kind": kind,
        "baseRevision": params["baseRevision"],
        "options": options,
        "manifest": manifest,
    }
    check_ref = digest(envelope)
    with store._transaction():
        store._db.execute(
            "INSERT OR IGNORE INTO job_details VALUES(?,?,?)",
            (check_ref, project, canonical({**envelope, "checkRef": check_ref})),
        )
    result = {
        "projectId": project,
        "selectionId": selection_id,
        "kind": kind,
        "baseRevision": params["baseRevision"],
        "options": options,
        "checkRef": check_ref,
        "manifest": manifest,
        "conflictPolicy": _conflict_policy(kind, options),
        "portability": _portability(kind, options, {"definitions_records": definitions}),
    }
    store._valid("result_project.transfer.package.export.check", result)
    return result


def _export_envelope(store, project, check_ref):
    row = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?", (check_ref, project)
    ).fetchone()
    if row is None:
        fault("IDENTITY_CONFLICT")
    envelope = json.loads(row[0])
    if not isinstance(envelope, dict) or envelope.get("transferExportCheckVersion") != 1:
        fault("INVALID_STATE")
    return envelope


def _export(store, params, origin, host):
    project = params["projectId"]
    internal = resolve_active(store, project)
    selection_id = params["selectionId"]
    check_ref, operation = params["checkRef"], params["operationId"]
    envelope = _export_envelope(store, project, check_ref)
    if (
        envelope["engineSessionId"] != origin["engineSessionId"]
        or envelope["selectionId"] != selection_id
    ):
        fault("IDENTITY_CONFLICT")
    request = {
        "transferExportVersion": 1,
        "projectId": project,
        "selectionId": selection_id,
        "checkRef": check_ref,
        "operationId": operation,
    }
    request_hash = digest(request)
    existing_row = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?",
        ("transfer-export:" + operation, project),
    ).fetchone()
    if existing_row is not None:
        existing = json.loads(existing_row[0])
        if (
            not isinstance(existing, dict)
            or existing.get("requestHash") != request_hash
            or existing.get("kind") != envelope["kind"]
        ):
            fault("IDENTITY_CONFLICT")
        result = existing["result"]
        store._valid("result_project.transfer.package.export", result)
        return result
    try:
        staging.verify_outbound(
            store, project, origin["engineSessionId"], selection_id, "package-export"
        )
    except staging.StagingFault as error:
        _staging_fault(error)
    if store.revision(internal) != envelope["baseRevision"]:
        fault(
            "REVISION_CONFLICT",
            expected=envelope["baseRevision"],
            actual=store.revision(internal),
        )
    # Rebuild from live state and prove it still equals the checked manifest.
    entries, definitions, facts, checkpoint = _collect_entries(
        store, project, internal, envelope["kind"], envelope["options"]
    )
    manifest = transfer_package.build_manifest(envelope["kind"], envelope["options"], entries)
    if manifest != envelope["manifest"]:
        fault("IDENTITY_CONFLICT")
    # FR-901 re-scan on the actual serialized bytes before generating the archive.
    try:
        credential_scan = scan_projection(
            {
                "members": {
                    role: payload.decode("utf-8", errors="replace")
                    for role, payload in entries.items()
                },
                "projection": _business_projection(definitions, facts, checkpoint),
            }
        )
    except CredentialLeak:
        _credential_fault()
    archive = transfer_package.build_archive(manifest, entries)
    try:
        published = staging.write_outbound(store, selection_id, "output.ontolearn.zip", archive)
    except staging.StagingFault as error:
        _staging_fault(error)
    result = {
        "projectId": project,
        "selectionId": selection_id,
        "checkRef": check_ref,
        "operationId": operation,
        "kind": envelope["kind"],
        "publication": {
            "state": "published",
            "sha256": published["sha256"],
            "byteLength": published["byteLength"],
            "cleanup": "complete",
            "durability": "confirmed",
            "postPublicationError": False,
        },
    }
    store._valid("result_project.transfer.package.export", result)
    with store._transaction():
        store._db.execute(
            "INSERT INTO job_details VALUES(?,?,?)",
            (
                "transfer-export:" + operation,
                project,
                canonical(
                    {
                        "transferExportReceiptVersion": 1,
                        "requestHash": request_hash,
                        "kind": envelope["kind"],
                        "credentialScan": {"version": 1, "status": credential_scan},
                        "result": result,
                    }
                ),
            ),
        )
    return result


def _read_package(store, project, engine_session_id, selection_id):
    try:
        _, payload = staging.read_inbound(
            store,
            project,
            engine_session_id,
            selection_id,
            "package-import",
            transfer_package.MAX_ARCHIVE,
        )
    except staging.StagingFault as error:
        _staging_fault(error)
    return payload


def _import_check(store, params, origin):
    project = params["projectId"]
    selection_id, expected_kind = params["selectionId"], params["expectedKind"]
    raw = _read_package(store, project, origin["engineSessionId"], selection_id)
    package_sha = staging.sha256_hex(raw)
    try:
        inspected = transfer_package.inspect_v1(raw, expected_kind)
    except transfer_package.PackageError as error:
        result = {
            "projectId": project,
            "selectionId": selection_id,
            "expectedKind": expected_kind,
            "status": "rejected",
            "reason": transfer_package.rejection_reason(error),
        }
        store._valid("result_project.transfer.package.import.check", result)
        return result
    manifest = inspected.manifest
    entries = inspected.entries
    definitions_records = json.loads(entries["data/definitions.json"])["definitions"]
    envelope = {
        "transferImportCheckVersion": 1,
        "projectId": project,
        "engineSessionId": origin["engineSessionId"],
        "hostClientId": origin["hostClientId"],
        "selectionId": selection_id,
        "expectedKind": expected_kind,
        "packageSha256": package_sha,
        "manifest": manifest,
    }
    check_ref = digest(envelope)
    with store._transaction():
        store._db.execute(
            "INSERT OR IGNORE INTO job_details VALUES(?,?,?)",
            (check_ref, project, canonical({**envelope, "checkRef": check_ref})),
        )
    result = {
        "projectId": project,
        "selectionId": selection_id,
        "expectedKind": expected_kind,
        "status": "compatible",
        "checkRef": check_ref,
        "manifest": manifest,
        "packageSha256": package_sha,
        "conflictPolicy": _conflict_policy(manifest["kind"], manifest["options"]),
        "portability": _portability(
            manifest["kind"], manifest["options"], {"definitions_records": definitions_records}
        ),
    }
    store._valid("result_project.transfer.package.import.check", result)
    return result


def _import_plan(entries):
    """Materialize the package members into Store plan fragments."""
    definitions = []
    for record in json.loads(entries["data/definitions.json"])["definitions"]:
        if set(record) != {"layer", "id", "payload"}:
            fault("INVALID_STATE")
        try:
            value = json.loads(record["payload"])
        except (ValueError, TypeError):
            fault("INVALID_STATE")
        definitions.append({"layer": record["layer"], "id": record["id"], "value": value})
    manual, grouped = [], {}
    if "data/assertions.json" in entries:
        for fact in json.loads(entries["data/assertions.json"])["facts"]:
            if set(fact) != {
                "id",
                "subject",
                "predicate",
                "object",
                "owner",
                "sourceRow",
                "managedValue",
            }:
                fault("INVALID_STATE")
            if fact["owner"] is None:
                if fact["managedValue"] is not None or fact["sourceRow"] is not None:
                    fault("INVALID_STATE")
                manual.append(
                    {
                        "id": fact["id"],
                        "subject": fact["subject"],
                        "predicate": fact["predicate"],
                        "object": fact["object"],
                    }
                )
                continue
            if fact["managedValue"] != fact["object"]:
                fault("INVALID_STATE")
            # Facts sharing one source row land in that single row's entry,
            # exactly like the exporter grouped them per parsed record.
            grouped.setdefault(fact["owner"], {}).setdefault(fact["sourceRow"], []).append(
                {
                    "id": fact["id"],
                    "subject": fact["subject"],
                    "predicate": fact["predicate"],
                    "object": fact["object"],
                }
            )
    mapping_rows = {
        owner: [{"row": source_row, "facts": facts} for source_row, facts in sorted(rows.items())]
        for owner, rows in sorted(grouped.items())
    }
    return definitions, manual, mapping_rows


def _import(store, params, origin, host):
    project = params["projectId"]
    selection_id, check_ref = params["selectionId"], params["checkRef"]
    operation, expected_kind, package_sha = (
        params["operationId"],
        params["expectedKind"],
        params["packageSha256"],
    )
    request = {
        "transferImportVersion": 1,
        "projectId": project,
        "selectionId": selection_id,
        "checkRef": check_ref,
        "operationId": operation,
        "expectedKind": expected_kind,
        "packageSha256": package_sha,
    }
    request_hash = digest(request)
    existing_row = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?",
        ("transfer-import:" + operation, project),
    ).fetchone()
    if existing_row is not None:
        existing = json.loads(existing_row[0])
        if existing.get("requestHash") != request_hash:
            fault("IDENTITY_CONFLICT")
        result = existing["result"]
        store._valid("result_project.transfer.package.import", result)
        return result
    row = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?", (check_ref, project)
    ).fetchone()
    if row is None:
        fault("IDENTITY_CONFLICT")
    check = json.loads(row[0])
    if (
        not isinstance(check, dict)
        or check.get("transferImportCheckVersion") != 1
        or check.get("engineSessionId") != origin["engineSessionId"]
        or check.get("selectionId") != selection_id
        or check.get("expectedKind") != expected_kind
        or check.get("packageSha256") != package_sha
    ):
        fault("IDENTITY_CONFLICT")
    raw = _read_package(store, project, origin["engineSessionId"], selection_id)
    if staging.sha256_hex(raw) != package_sha:
        fault("IDENTITY_CONFLICT")
    try:
        inspected = transfer_package.inspect_v1(raw, expected_kind)
    except transfer_package.PackageError:
        fault("INVALID_STATE")
    if inspected.manifest != check["manifest"]:
        fault("IDENTITY_CONFLICT")
    definitions, manual, mapping_rows = _import_plan(inspected.entries)
    # FR-901: scan the imported business text before any project is created.
    try:
        credential_scan = scan_projection(
            {"definitions": definitions, "manual": manual, "mappingRows": mapping_rows}
        )
    except CredentialLeak:
        _credential_fault()
    checkpoint_meta = json.loads(inspected.entries.get("data/checkpoint.json", b"{}"))
    name = (
        (checkpoint_meta.get("metadata") or {}).get("name") if expected_kind == "full" else None
    ) or TEMPLATE_NAME
    from ontolearn_engine.project.mainline import READ_LIMITS

    create_operation = str(uuid4())
    created = store.commit(
        None,
        None,
        create_operation,
        None,
        creation={
            "projectCreateCoreVersion": 1,
            "request": {
                "requestVersion": 1,
                "operationId": create_operation,
                "name": name,
                "initialization": {"kind": "blank"},
            },
            "origin": {
                "hostClientId": origin["hostClientId"],
                "engineSessionId": origin["engineSessionId"],
                "permission": "library.create",
            },
            "readerLimits": READ_LIMITS,
        },
    )
    imported_id = created["projectId"]
    imported_internal = store._project(imported_id)
    plans = []
    first = {"definitions": definitions, "manual": manual}
    if mapping_rows:
        owner = sorted(mapping_rows)[0]
        first["mapping"] = {"id": owner, "rows": mapping_rows[owner]}
    plans.append(first)
    for owner in sorted(mapping_rows)[1:]:
        plans.append({"mapping": {"id": owner, "rows": mapping_rows[owner]}})
    # One outer transaction: every domain fragment lands or none does, and the
    # durable import receipt is written inside that same boundary. Each
    # fragment flows through the ordinary single-writer application ledger
    # (prepared plan + confirmation, exactly like every other domain change).
    result = {
        "projectId": project,
        "selectionId": selection_id,
        "checkRef": check_ref,
        "operationId": operation,
        "kind": inspected.manifest["kind"],
        "packageSha256": package_sha,
        "importedProjectId": imported_id,
        "conflictPolicy": _conflict_policy(
            inspected.manifest["kind"], inspected.manifest["options"]
        ),
    }
    store._valid("result_project.transfer.package.import", result)
    try:
        with store._transaction():
            base = store.revision(imported_internal)
            for index, plan in enumerate(plans):
                change = {
                    "type": "metadata",
                    "expectedVersion": 1 + index,
                    "patch": {"name": name},
                    "domain": {"base": base, "plan": plan},
                }
                prepared = store.prepare_application(
                    imported_id, change, actor=origin["hostClientId"], permission="write"
                )
                store.apply_application(
                    imported_id,
                    operation if index == 0 else f"{operation}:import-{index + 1}",
                    change,
                    actor=origin["hostClientId"],
                    permission="write",
                    prepared_plan_ref=prepared["preparedPlanRef"],
                    confirmation_ref=prepared["confirmationRef"],
                )
                base += 1
            store._db.execute(
                "INSERT INTO job_details VALUES(?,?,?)",
                (
                    "transfer-import:" + operation,
                    project,
                    canonical(
                        {
                            "transferImportReceiptVersion": 1,
                            "requestHash": request_hash,
                            "credentialScan": {"version": 1, "status": credential_scan},
                            "result": result,
                        }
                    ),
                ),
            )
    except Conflict as error:
        code = {
            "identity": "IDENTITY_CONFLICT",
            "input": "INVALID_REQUEST",
            "revision": "REVISION_CONFLICT",
        }.get(error.category, "INVALID_STATE")
        if code == "INVALID_REQUEST":
            fault(code, field="params")
        fault(code)
    return result


def _report_prepare(store, params, origin, host):
    project = params["projectId"]
    internal = resolve_active(store, project)
    if store.revision(internal) != params["baseRevision"]:
        fault("REVISION_CONFLICT", expected=params["baseRevision"], actual=store.revision(internal))
    report = transfer_report.collect(store, project, internal, host)
    try:
        credential_scan = scan_projection(report)
    except CredentialLeak:
        _credential_fault()
    envelope = {
        "transferReportVersion": 1,
        "projectId": project,
        "engineSessionId": origin["engineSessionId"],
        "hostClientId": origin["hostClientId"],
        "baseRevision": params["baseRevision"],
        "report": report,
    }
    report_ref = digest(envelope)
    with store._transaction():
        store._db.execute(
            "INSERT OR IGNORE INTO job_details VALUES(?,?,?)",
            (report_ref, project, canonical({**envelope, "reportRef": report_ref})),
        )
    result = {
        "projectId": project,
        "baseRevision": params["baseRevision"],
        "state": "prepared",
        "reportRef": report_ref,
        "report": report,
        "credentialScan": {"version": 1, "status": credential_scan},
    }
    store._valid("result_project.transfer.report.prepare", result)
    return result


def _confirm_report_publication(store, project, origin, result):
    try:
        receipt = staging.read_report_publication(
            store, project, origin["engineSessionId"], result["selectionId"]
        )
    except staging.StagingFault as error:
        _staging_fault(error)
    if receipt is None:
        return
    expected = {
        "version": 1,
        "operationId": result["operationId"],
        "reportRef": result["reportRef"],
        "sha256": result["publication"]["sha256"],
        "byteLength": result["publication"]["byteLength"],
    }
    if receipt != expected:
        fault("IDENTITY_CONFLICT")
    with store._transaction():
        store._db.execute(
            "INSERT OR IGNORE INTO job_details VALUES(?,?,?)",
            ("transfer-report-published:" + result["operationId"], project, canonical(expected)),
        )


def _report_export(store, params, origin, host):
    project = params["projectId"]
    internal = resolve_active(store, project)
    selection_id, report_ref = params["selectionId"], params["reportRef"]
    operation, base_revision = params["operationId"], params["baseRevision"]
    request = {
        "transferReportExportVersion": 1,
        "projectId": project,
        "selectionId": selection_id,
        "reportRef": report_ref,
        "baseRevision": base_revision,
        "operationId": operation,
    }
    request_hash = digest(request)
    existing_row = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?",
        ("transfer-report:" + operation, project),
    ).fetchone()
    if existing_row is not None:
        existing = json.loads(existing_row[0])
        if existing.get("requestHash") != request_hash:
            fault("IDENTITY_CONFLICT")
        result = existing["result"]
        store._valid("result_project.transfer.report.export", result)
        if existing.get("publicationOrigin") == [
            origin["engineSessionId"],
            origin["hostClientId"],
        ]:
            _confirm_report_publication(store, project, origin, result)
        return result
    row = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?", (report_ref, project)
    ).fetchone()
    if row is None:
        fault("IDENTITY_CONFLICT")
    envelope = json.loads(row[0])
    if (
        not isinstance(envelope, dict)
        or envelope.get("transferReportVersion") != 1
        or envelope.get("engineSessionId") != origin["engineSessionId"]
        or envelope.get("baseRevision") != base_revision
    ):
        fault("IDENTITY_CONFLICT")
    if store.revision(internal) != base_revision:
        fault("REVISION_CONFLICT", expected=base_revision, actual=store.revision(internal))
    try:
        staging.verify_outbound(
            store, project, origin["engineSessionId"], selection_id, "report-html"
        )
    except staging.StagingFault as error:
        _staging_fault(error)
    report = envelope["report"]
    # FR-901 re-scan on the actual rendered serialization before writing bytes.
    html_text = transfer_report.render_html(report)
    try:
        report_scan = scan_projection(report)
        html_scan = scan_projection({"html": html_text})
    except CredentialLeak:
        _credential_fault()
    status = "redacted" if "redacted" in (report_scan, html_scan) else "clear"
    try:
        published = staging.write_outbound(
            store, selection_id, "output.html", html_text.encode("utf-8")
        )
    except staging.StagingFault as error:
        _staging_fault(error)
    result = {
        "projectId": project,
        "selectionId": selection_id,
        "reportRef": report_ref,
        "baseRevision": base_revision,
        "operationId": operation,
        "format": "html",
        "credentialScan": {"version": 1, "status": status},
        "publication": {
            "state": "published",
            "sha256": published["sha256"],
            "byteLength": published["byteLength"],
            "cleanup": "complete",
            "durability": "confirmed",
            "postPublicationError": False,
        },
    }
    store._valid("result_project.transfer.report.export", result)
    with store._transaction():
        store._db.execute(
            "INSERT INTO job_details VALUES(?,?,?)",
            (
                "transfer-report:" + operation,
                project,
                canonical(
                    {
                        "transferReportReceiptVersion": 1,
                        "publicationOrigin": [origin["engineSessionId"], origin["hostClientId"]],
                        "requestHash": request_hash,
                        "result": result,
                    }
                ),
            ),
        )
    return result


def dispatch(store, method, params, host, origin):
    store._valid("params_" + method, params)
    if method == "project.transfer.package.export.check":
        return _export_check(store, params, origin, host)
    if method == "project.transfer.package.export":
        return _export(store, params, origin, host)
    if method == "project.transfer.package.import.check":
        return _import_check(store, params, origin)
    if method == "project.transfer.package.import":
        return _import(store, params, origin, host)
    if method == "project.transfer.report.prepare":
        return _report_prepare(store, params, origin, host)
    return _report_export(store, params, origin, host)
