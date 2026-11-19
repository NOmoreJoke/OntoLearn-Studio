"""T03 mapping wire services over the owned Store and the staging protocol.

Five ``business3`` methods (selected-project authority, named-bridge exposure):
source selection / re-parse, versioned draft persistence through the ordinary
application draft ledger, bounded preview with issues/conflicts/diff, and
trusted ``mappingPreparation`` minting. The lowered ChangeSet plan is resolved
from persisted preparation evidence by :func:`resolve_preparation` and flows
through the existing ``changeset.preview -> diff -> confirm -> commit``
machinery unchanged - there is no second write path. Raw OS file paths never
appear in any DTO, error or log.
"""

import json
from dataclasses import asdict
from uuid import uuid4

from ontolearn_engine.mapping import plan as mapping_plan
from ontolearn_engine.mapping.source import (
    MAX_BYTES,
    SourceError,
    parse_csv,
    parse_xlsx,
    xlsx_sheets,
)
from ontolearn_engine.project import staging
from ontolearn_engine.project.ontology_turtle import resolve_active
from ontolearn_engine.storage import Conflict, canonical, digest

METHODS = frozenset(
    {
        "project.mapping.source.select",
        "project.mapping.preview",
        "project.mapping.prepare",
        "project.mapping.draft.read",
        "project.mapping.draft.save",
    }
)
DRAFT_EDITOR_PREFIX = "mapping/"
CSV_SHEET = "CSV"
# Wire encoding -> parser encoding; UTF-8 BOM is recognized by utf-8-sig.
PARSER_ENCODING = {"utf-8": "utf-8-sig", "gb18030": "gb18030", "big5": "big5", "utf-16": "utf-16"}
SELECT_FAULTS = {
    "SOURCE_LIMIT": ("RESOURCE_LIMIT", {"resource": "frame"}),
    "XLSX_PARSER_UNAVAILABLE": ("UNSUPPORTED_CAPABILITY", {}),
}
PAGE_LIMIT = 100
PREPARATION_KEYS = (
    "mappingPreparationVersion",
    "projectId",
    "engineSessionId",
    "hostClientId",
    "resultId",
    "selectionId",
    "sourceFingerprint",
    "baseRevision",
    "operationId",
    "draft",
    "sheet",
    "encoding",
    "previewHash",
    "payloadHash",
    "plan",
)


def fault(code, **params):
    from ontolearn_engine.job_store import fault as job_fault

    job_fault(code, **params)


def _ownership_fault(store, project, resource):
    """Persist fixed ownership evidence and reject with its bounded detailRef."""
    detail_ref = str(uuid4())
    detail = {
        "category": "ownership",
        "resource": resource,
        "projectId": project,
        "conflictCount": True,
    }
    with store._transaction():
        store._db.execute(
            "INSERT INTO job_details VALUES(?,?,?)", (detail_ref, project, canonical(detail))
        )
    fault("OWNERSHIP_CONFLICT", detailRef=detail_ref)


def _value_invalid(selection_id, issues):
    """Map the first blocking issue onto the frozen MAPPING_VALUE_INVALID shape."""
    issue = sorted(issues, key=lambda item: (item.row, item.column, item.field))[0]
    field = "key" if issue.code in {"EMPTY_KEY", "DUPLICATE_KEY", "DUPLICATE_IDENTITY"} else "value"
    fault(
        "MAPPING_VALUE_INVALID",
        worksheetId=selection_id,
        row=max(1, issue.row),
        column=max(1, issue.column),
        field=field,
    )


def _staging_fault(error):
    code, params = staging.fault_for(error.code)
    fault(code, **params)


def _source_fault(error):
    code, params = SELECT_FAULTS.get(error.issue.code, ("INVALID_REQUEST", {"field": "params"}))
    fault(code, **params)


def _message_keys():
    from ontolearn_engine.resources import CONTRACT

    return CONTRACT.ERROR_CATALOG["wave4"]["mappingIssueMessageKeys"]


def _wire_mapping(draft):
    """Frozen wire draft -> the pure planner Mapping (no extra authority)."""
    try:
        bindings = [
            mapping_plan.Binding(
                column=field["column"],
                predicate=field["predicate"],
                conversion=mapping_plan.Conversion(
                    kind=field["kind"], trim=field["trim"], empty=field["empty"]
                ),
                reference_namespace=field["referenceNamespace"] or None,
                reference_columns=tuple(field["referenceColumns"]),
            )
            for field in draft["fields"]
        ]
        return mapping_plan.Mapping(
            identity=draft["identity"],
            version=draft["version"],
            namespace=draft["namespace"],
            class_iri=draft["classIri"],
            keys=tuple(draft["keys"]),
            bindings=tuple(bindings),
        )
    except (KeyError, TypeError, ValueError):
        fault("INVALID_REQUEST", field="params")


def _issue_dto(issue):
    keys = _message_keys()
    code = issue.code
    if code == "EMPTY_REFERENCE_KEY":
        code = "INVALID_REFERENCE"  # frozen vocabulary projection
    if code not in keys:
        code = "UNKNOWN_MAPPING_ISSUE"
    return {
        "code": code,
        "messageKey": keys[code],
        "sheet": issue.sheet,
        "row": issue.row,
        "column": issue.column,
        "field": issue.field,
    }


def _parse_table(payload, fmt, sheet, encoding):
    try:
        if fmt == "csv":
            return parse_csv(payload, encoding=PARSER_ENCODING[encoding])
        return parse_xlsx(payload, sheet=sheet)
    except SourceError as error:
        _source_fault(error)


def _binding_id(project, selection_id):
    return digest(
        {
            "mappingSelectionBindingVersion": 1,
            "projectId": project,
            "selectionId": selection_id,
        }
    )


def _read_selection(store, project, engine_session_id, selection_id):
    """Fresh staging read returning (meta, payload, binding envelope)."""
    try:
        meta, payload = staging.read_inbound(
            store, project, engine_session_id, selection_id, "mapping-source", MAX_BYTES
        )
    except staging.StagingFault as error:
        _staging_fault(error)
    envelope = {
        "mappingSelectionVersion": 1,
        "projectId": project,
        "engineSessionId": engine_session_id,
        "selectionId": selection_id,
        "format": meta["format"],
        "fingerprint": staging.sha256_hex(payload),
        "byteLength": meta["byteLength"],
    }
    return meta, payload, envelope


def _verify_binding(store, envelope):
    """The immutable select() binding for this project/session/selection."""
    row = store._db.execute(
        "SELECT project,payload FROM job_details WHERE id=?",
        (_binding_id(envelope["projectId"], envelope["selectionId"]),),
    ).fetchone()
    if row is None or row[0] != envelope["projectId"] or row[1] != canonical(envelope):
        fault("IDENTITY_CONFLICT")
    return envelope


def _load_selection(store, project, engine_session_id, selection_id):
    """Fresh staging read plus the persisted select() session binding."""
    meta, payload, envelope = _read_selection(store, project, engine_session_id, selection_id)
    _verify_binding(store, envelope)
    return meta, payload, envelope


def _snapshot(store, internal):
    return {
        "project": internal,
        "projectRevision": store.revision(internal),
        "state": store.state(internal),
    }


def _fresh_preview(store, project, internal, table, draft):
    mapping = _wire_mapping(draft)
    try:
        return mapping, mapping_plan.preview(mapping, table, _snapshot(store, internal))
    except ValueError:
        fault("INVALID_REQUEST", field="params")


def _triple_text(subject, predicate, obj):
    return f"{subject} {predicate} {obj}"


def _preview_core(mapping, preview):
    """Deterministic equality core: re-verified at prepare and ChangeSet time."""
    return digest(
        {
            "mapping": asdict(mapping),
            "sourceHash": preview.source_hash,
            "snapshotHash": preview.snapshot_hash,
            "definitionHash": preview.definition_hash,
            "issues": [asdict(issue) for issue in preview.issues],
            "conflicts": [asdict(conflict) for conflict in preview.conflicts],
            "rows": preview.rows_json,
            "added": [list(t) for t in preview.added],
            "removed": [list(t) for t in preview.removed],
            "modified": preview.modified,
            "identitiesAdded": list(preview.identities_added),
            "identitiesRemoved": list(preview.identities_removed),
        }
    )


def _ontology_candidates(state):
    """Exact-field-name candidates from the project's real ontology catalog."""
    import re

    candidates = {}
    for record in state["definitions"]:
        if record["layer"] != "ontology":
            continue
        value = json.loads(record["payload"])
        if not isinstance(value, dict):
            continue
        for triple in value.get("triples", []):
            if triple["predicate"] != "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" or (
                triple["object"]
                not in (
                    "<http://www.w3.org/2002/07/owl#DatatypeProperty>",
                    "<http://www.w3.org/2002/07/owl#ObjectProperty>",
                    "<http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>",
                )
            ):
                continue
            predicate = triple["subject"]
            # The property's own local name (after the last #, / or urn ':'),
            # the only basis the frozen exact-field-name suggestion allows.
            local = re.split(r"[#/:]", predicate)[-1]
            if local:
                candidates.setdefault(local, predicate)
    return candidates


def _select(store, params, origin):
    project = params["projectId"]
    selection_id = params.get("selectionId")
    if selection_id is None:
        # The renderer only holds tokens; without a staged selection there is
        # nothing trusted to read (fail closed, mirroring Stage 0 stubs).
        fault("INVALID_REQUEST", field="params")
    internal = resolve_active(store, project)
    meta, payload, envelope = _read_selection(
        store, project, origin["engineSessionId"], selection_id
    )
    fmt = meta["format"]
    if fmt == "csv":
        sheet = params.get("sheet") or CSV_SHEET
        if sheet != CSV_SHEET:
            fault("INVALID_REQUEST", field="params")
        encoding = params.get("encoding") or "utf-8"
        sheets = [CSV_SHEET]
    else:
        if params.get("encoding") is not None:
            fault("INVALID_REQUEST", field="params")
        encoding = None
        try:
            sheets = list(xlsx_sheets(payload))
        except SourceError as error:
            _source_fault(error)
        sheet = params.get("sheet") or (sheets[0] if sheets else None)
        if sheet is None or sheet not in sheets:
            fault("INVALID_REQUEST", field="params")
    table = _parse_table(payload, fmt, sheet, encoding)
    with store._transaction():
        store._db.execute(
            "INSERT OR IGNORE INTO job_details VALUES(?,?,?)",
            (_binding_id(project, selection_id), project, canonical(envelope)),
        )
    describe = table.describe()
    result = {
        "projectId": project,
        "selectionId": selection_id,
        "fingerprint": envelope["fingerprint"],
        "format": fmt,
        "sheets": sheets,
        "sheet": sheet,
        "encoding": encoding,
        "fields": [
            {
                "name": item["field"],
                "observedTypes": item["types"][:16],
                "samples": item["samples"][:8],
            }
            for item in describe
        ],
        "totalRows": len(table.rows),
        "suggestions": [
            {
                "column": item["column"],
                "predicate": item["predicate"],
                "basis": "exact-field-name",
                "samples": item["samples"][:3],
            }
            for item in mapping_plan.suggest(
                table, _ontology_candidates(_snapshot(store, internal)["state"])
            )
        ],
    }
    store._valid("result_project.mapping.source.select", result)
    return result


def _preview(store, params, origin):
    project = params["projectId"]
    internal = resolve_active(store, project)
    selection_id = params["selectionId"]
    meta, payload, _ = _load_selection(store, project, origin["engineSessionId"], selection_id)
    sheet, encoding, draft = params["sheet"], params["encoding"], params["draft"]
    if meta["format"] == "csv":
        if sheet != CSV_SHEET or encoding is None:
            fault("INVALID_REQUEST", field="params")
    elif encoding is not None:
        fault("INVALID_REQUEST", field="params")
    table = _parse_table(payload, meta["format"], sheet, encoding)
    mapping, fresh = _fresh_preview(store, project, internal, table, draft)
    result_id = str(uuid4())
    page = params.get("page") or {"offset": 0, "limit": PAGE_LIMIT}
    offset, limit = page["offset"], page["limit"]
    rows_json = fresh.rows()
    core = _preview_core(mapping, fresh)
    envelope = {
        "mappingPreviewVersion": 1,
        "projectId": project,
        "engineSessionId": origin["engineSessionId"],
        "hostClientId": origin["hostClientId"],
        "resultId": result_id,
        "selectionId": selection_id,
        "sourceFingerprint": fresh.source_hash,
        "baseRevision": fresh.base_revision,
        "sheet": sheet,
        "encoding": encoding,
        "draft": draft,
        "previewHash": core,
        "blocked": not fresh.ready,
    }
    with store._transaction():
        store._db.execute(
            "INSERT INTO job_details VALUES(?,?,?)",
            ("mapping-preview:" + result_id, project, canonical(envelope)),
        )
    table_by_number = {row.number: row for row in table.rows}
    window = []
    for row in rows_json[offset : offset + limit]:
        number = json.loads(row["row"])["row"]
        row_cells = table_by_number[number]
        window.append(
            {
                "sourceRow": row["row"],
                "input": [cell.text for cell in row_cells.cells],
                "rdf": [
                    _triple_text(fact["subject"], fact["predicate"], fact["object"])
                    for fact in row["facts"]
                ],
            }
        )
    result = {
        "projectId": project,
        "resultId": result_id,
        "baseRevision": fresh.base_revision,
        "selectionId": selection_id,
        "sheet": sheet,
        "encoding": encoding,
        "sourceFingerprint": fresh.source_hash,
        "rows": window,
        "offset": offset,
        "totalRows": len(table.rows),
        "identitiesAdded": list(fresh.identities_added)[:50000],
        "identitiesRemoved": list(fresh.identities_removed)[:50000],
        "issues": [_issue_dto(issue) for issue in fresh.issues],
        "conflicts": [
            {
                "code": conflict.code,
                "current": conflict.current,
                "source": conflict.source,
                "managed": conflict.managed,
                "owner": conflict.owner,
                "sourceRow": conflict.source_row,
                "subject": conflict.subject,
                "predicate": conflict.predicate,
            }
            for conflict in fresh.conflicts
        ],
        "added": [_triple_text(*t) for t in list(fresh.added)[:5000]],
        "removed": [_triple_text(*t) for t in list(fresh.removed)[:5000]],
        "modified": list(fresh.modified)[:5000],
    }
    store._valid("result_project.mapping.preview", result)
    return result


def _preview_envelope(store, project, result_id):
    row = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?",
        ("mapping-preview:" + result_id, project),
    ).fetchone()
    if row is None:
        fault("IDENTITY_CONFLICT")
    envelope = json.loads(row[0])
    if not isinstance(envelope, dict) or envelope.get("mappingPreviewVersion") != 1:
        fault("INVALID_STATE")
    return envelope


def _effective_plan(mapping, fresh, sheet):
    """The trusted T01 storage plan shape; still CAS-checked inside Store.commit."""
    return {
        "mapping": {"id": mapping.identity, "rows": fresh.rows()},
        "definitions": [
            {
                "layer": "mapping",
                "id": mapping.identity,
                "value": {
                    "version": mapping.version,
                    "definition": asdict(mapping),
                    "sourceHash": fresh.source_hash,
                    "sheet": sheet,
                },
            }
        ],
    }


def _prepare(store, params, origin):
    project = params["projectId"]
    internal = resolve_active(store, project)
    result_id = params["resultId"]
    operation = params["operationId"]
    request = {
        "mappingPrepareVersion": 1,
        "projectId": project,
        "resultId": result_id,
        "selectionId": params["selectionId"],
        "sourceFingerprint": params["sourceFingerprint"],
        "baseRevision": params["baseRevision"],
        "operationId": operation,
    }
    request_hash = digest(request)
    existing_row = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?",
        ("mapping-prepare:" + operation, project),
    ).fetchone()
    if existing_row is not None:
        # Exact-evidence replay precedes any CAS: an acknowledged preparation
        # replays its original receipt even after the domain head moved.
        existing = json.loads(existing_row[0])
        if (
            not isinstance(existing, dict)
            or existing.get("mappingPreparationVersion") != 1
            or existing.get("requestHash") != request_hash
        ):
            fault("IDENTITY_CONFLICT")
        preparation_ref = existing["preparationRef"]
        result = {
            "projectId": project,
            "resultId": result_id,
            "selectionId": params["selectionId"],
            "sourceFingerprint": params["sourceFingerprint"],
            "baseRevision": params["baseRevision"],
            "operationId": operation,
            "plan": {
                "mappingPreparation": {"resultId": result_id, "preparationRef": preparation_ref}
            },
        }
        store._valid("result_project.mapping.prepare", result)
        return result
    envelope = _preview_envelope(store, project, result_id)
    if envelope["engineSessionId"] != origin["engineSessionId"]:
        fault("IDENTITY_CONFLICT")
    for key in ("selectionId", "sourceFingerprint", "baseRevision"):
        if envelope[key] != params[key]:
            fault("IDENTITY_CONFLICT")
    if store.revision(internal) != params["baseRevision"]:
        fault("REVISION_CONFLICT", expected=params["baseRevision"], actual=store.revision(internal))
    # Trusted recomputation: staged source, stored draft and current snapshot
    # must reproduce the exact preview the caller saw.
    meta, payload, _ = _load_selection(
        store, project, origin["engineSessionId"], envelope["selectionId"]
    )
    if staging.sha256_hex(payload) != envelope["sourceFingerprint"]:
        fault("IDENTITY_CONFLICT")
    table = _parse_table(payload, meta["format"], envelope["sheet"], envelope["encoding"])
    mapping, fresh = _fresh_preview(store, project, internal, table, envelope["draft"])
    if _preview_core(mapping, fresh) != envelope["previewHash"]:
        fault("IDENTITY_CONFLICT")
    if fresh.conflicts:
        _ownership_fault(store, project, "mapping.prepare")
    if fresh.issues:
        _value_invalid(params["selectionId"], fresh.issues)
    if True:
        plan = _effective_plan(mapping, fresh, envelope["sheet"])
        preparation = {
            "mappingPreparationVersion": 1,
            "projectId": project,
            "engineSessionId": origin["engineSessionId"],
            "hostClientId": origin["hostClientId"],
            "resultId": result_id,
            "selectionId": params["selectionId"],
            "sourceFingerprint": params["sourceFingerprint"],
            "baseRevision": params["baseRevision"],
            "operationId": operation,
            "draft": envelope["draft"],
            "sheet": envelope["sheet"],
            "encoding": envelope["encoding"],
            "previewHash": envelope["previewHash"],
            "payloadHash": digest(plan),
            "plan": plan,
        }
        preparation_ref = digest(preparation)
        record = {**preparation, "preparationRef": preparation_ref, "requestHash": request_hash}
        with store._transaction():
            store._db.execute(
                "INSERT INTO job_details VALUES(?,?,?)",
                ("mapping-prepare:" + operation, project, canonical(record)),
            )
            store._db.execute(
                "INSERT INTO job_details VALUES(?,?,?)",
                (preparation_ref, project, canonical(record)),
            )
    result = {
        "projectId": project,
        "resultId": result_id,
        "selectionId": params["selectionId"],
        "sourceFingerprint": params["sourceFingerprint"],
        "baseRevision": params["baseRevision"],
        "operationId": operation,
        "plan": {"mappingPreparation": {"resultId": result_id, "preparationRef": preparation_ref}},
    }
    store._valid("result_project.mapping.prepare", result)
    return result


def _draft_editor(mapping_id):
    return DRAFT_EDITOR_PREFIX + mapping_id


def _draft_head(store, internal, mapping_id):
    checkpoint = store.project_checkpoint(internal)
    return next(
        (
            item
            for item in checkpoint["application"]["drafts"]
            if item["editor"] == _draft_editor(mapping_id)
        ),
        None,
    )


def _draft_read(store, params, origin):
    project = params["projectId"]
    internal = resolve_active(store, project)
    mapping_id = params["mappingId"]
    row = _draft_head(store, internal, mapping_id)
    if row is None or not row["present"]:
        result = {
            "projectId": project,
            "mappingId": mapping_id,
            "generation": row["generation"] if row is not None else 0,
            "baseRevision": store.revision(internal),
            "draft": None,
        }
    else:
        result = {
            "projectId": project,
            "mappingId": mapping_id,
            "generation": row["generation"],
            "baseRevision": row["bound_revision"],
            "draft": json.loads(row["payload"]),
        }
    store._valid("result_project.mapping.draft.read", result)
    return result


def _draft_save(store, params, origin):
    project = params["projectId"]
    internal = resolve_active(store, project)
    operation = params["operationId"]
    mapping_id = params["draft"]["identity"]
    editor = _draft_editor(mapping_id)
    change = {
        "type": "draft.save",
        "editor": editor,
        "expectedGeneration": params["expectedGeneration"],
        "boundDomainRevision": params["baseRevision"],
        "content": params["draft"],
    }
    request = {
        "mappingDraftSaveVersion": 1,
        "projectId": project,
        "operationId": operation,
        "editor": editor,
        "expectedGeneration": params["expectedGeneration"],
        "boundDomainRevision": params["baseRevision"],
        "draft": params["draft"],
    }
    request_hash = digest(request)
    existing_row = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?",
        ("mapping-draft:" + operation, project),
    ).fetchone()
    if existing_row is not None:
        existing = json.loads(existing_row[0])
        if (
            not isinstance(existing, dict)
            or existing.get("mappingDraftReceiptVersion") != 1
            or existing.get("requestHash") != request_hash
        ):
            fault("IDENTITY_CONFLICT")
        result = existing["result"]
        store._valid("result_project.mapping.draft.save", result)
        return result
    generation_conflict = False
    try:
        with store._transaction():
            if not store.has_operation_claim(operation):
                head = _draft_head(store, internal, mapping_id)
                actual = head["generation"] if head is not None else 0
                generation_conflict = actual != params["expectedGeneration"]
                revision = store.revision(internal)
                if revision != params["baseRevision"]:
                    fault(
                        "REVISION_CONFLICT",
                        expected=params["baseRevision"],
                        actual=revision,
                    )
            receipt = store.apply_application(
                project,
                operation,
                change,
                actor=origin["hostClientId"],
                permission="write",
            )
            checkpoint = store.project_checkpoint(internal, receipt["afterCheckpointRef"])
            row = next(
                (item for item in checkpoint["application"]["drafts"] if item["editor"] == editor),
                None,
            )
            if row is None or row["present"] != 1 or json.loads(row["payload"]) != params["draft"]:
                fault("INVALID_STATE")
            result = {
                "projectId": project,
                "operationId": operation,
                "generation": row["generation"],
                "baseRevision": row["bound_revision"],
                "draft": params["draft"],
            }
            store._valid("result_project.mapping.draft.save", result)
            store._db.execute(
                "INSERT INTO job_details VALUES(?,?,?)",
                (
                    "mapping-draft:" + operation,
                    project,
                    canonical(
                        {
                            "mappingDraftReceiptVersion": 1,
                            "requestHash": request_hash,
                            "result": result,
                        }
                    ),
                ),
            )
    except Conflict as error:
        if generation_conflict and error.category == "state":
            fault("INVALID_STATE")
        raise
    return result


def resolve_preparation(store, project, host_client_id, engine_session_id, plan):
    """Lower a ``mappingPreparation`` plan to the trusted T01 Store plan.

    Called from the ordinary ``changeset.preview`` flow. Re-verifies the
    persisted preparation evidence, the current project revision, and that the
    staged source, stored draft and snapshot still reproduce the exact
    previewed bytes. Never accepts renderer-owned preview instances.
    """
    if not isinstance(plan, dict) or set(plan) != {"mappingPreparation"}:
        fault("INVALID_REQUEST", field="params")
    preparation_ref = plan["mappingPreparation"]["preparationRef"]
    result_id = plan["mappingPreparation"]["resultId"]
    row = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?", (preparation_ref, project)
    ).fetchone()
    if row is None:
        fault("IDENTITY_CONFLICT")
    record = json.loads(row[0])
    if (
        not isinstance(record, dict)
        or set(record) != set(PREPARATION_KEYS) | {"preparationRef", "requestHash"}
        or record.get("mappingPreparationVersion") != 1
        or record.get("resultId") != result_id
        or record.get("engineSessionId") != engine_session_id
        or record.get("hostClientId") != host_client_id
        or record.get("preparationRef") != preparation_ref
        or digest({key: record[key] for key in PREPARATION_KEYS}) != preparation_ref
    ):
        fault("IDENTITY_CONFLICT")
    internal = store._project(project)
    if store.revision(internal) != record["baseRevision"]:
        fault(
            "REVISION_CONFLICT",
            expected=record["baseRevision"],
            actual=store.revision(internal),
        )
    meta, payload, _ = _load_selection(store, project, engine_session_id, record["selectionId"])
    if staging.sha256_hex(payload) != record["sourceFingerprint"]:
        fault("IDENTITY_CONFLICT")
    table = _parse_table(payload, meta["format"], record["sheet"], record["encoding"])
    mapping, fresh = _fresh_preview(store, project, internal, table, record["draft"])
    if _preview_core(mapping, fresh) != record["previewHash"]:
        fault("IDENTITY_CONFLICT")
    effective = _effective_plan(mapping, fresh, record["sheet"])
    if digest(effective) != record["payloadHash"]:
        fault("IDENTITY_CONFLICT")
    if fresh.conflicts:
        _ownership_fault(store, project, "changeset.mappingPreparation")
    if fresh.issues:
        _value_invalid(record["selectionId"], fresh.issues)
    return effective


def bind_changeset_plan(store, project, plan_ref, preparation):
    """Keep the verified mapping preparation beside its immutable formal plan."""
    store._db.execute(
        "INSERT OR IGNORE INTO job_details VALUES(?,?,?)",
        ("mapping-plan:" + plan_ref, project, canonical(preparation)),
    )


def record_changeset_execution(store, job, preview, marker):
    """Store evidence atomically with the successful formal ChangeSet Job."""
    project = job["projectId"]
    binding = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?",
        ("mapping-plan:" + job["input"]["preparedPlanRef"], project),
    ).fetchone()
    if binding is None:
        return
    preparation = json.loads(binding[0])
    record = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?",
        (preparation["preparationRef"], project),
    ).fetchone()
    if record is None:
        fault("INVALID_STATE")
    prepared = json.loads(record[0])
    if prepared["resultId"] != preparation["resultId"] or prepared["baseRevision"] != preview.base:
        fault("INVALID_STATE")
    operation_id = job["operationId"]
    definition = prepared["plan"]["definitions"][0]
    store._db.execute(
        "INSERT INTO job_details VALUES(?,?,?)",
        (
            "mapping-run:" + operation_id,
            project,
            canonical(
                {
                    "mappingRunVersion": 1,
                    "operationId": operation_id,
                    "resultId": preparation["resultId"],
                    "mappingId": definition["id"],
                    "definitionHash": digest(definition["value"]),
                    "beforeSnapshotId": marker["before_snapshot"],
                    "afterSnapshotId": marker["after_snapshot"],
                    "revision": marker["revision"],
                    "noChanges": not preview.diff,
                }
            ),
        ),
    )


def dispatch(store, method, params, origin):
    store._valid("params_" + method, params)
    if method == "project.mapping.source.select":
        return _select(store, params, origin)
    if method == "project.mapping.preview":
        return _preview(store, params, origin)
    if method == "project.mapping.prepare":
        return _prepare(store, params, origin)
    if method == "project.mapping.draft.read":
        return _draft_read(store, params, origin)
    return _draft_save(store, params, origin)
