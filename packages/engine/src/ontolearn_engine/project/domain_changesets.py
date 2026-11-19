"""Formal, confirmed ChangeSets over the existing Store and Job ledger.

No independent writer or authority table: immutable plans/blobs/details and bounded
cursor tokens use JobStore's existing connection and outer transaction.
"""

import base64
import hashlib
import json
from copy import deepcopy
from uuid import uuid4

from ontolearn_engine.project import compensation
from ontolearn_engine.project.entity_metadata import (
    MetadataError,
    merge_plan,
    validate_change,
    validate_compensation,
    validate_supported_pair,
)
from ontolearn_engine.project.transactions import (
    ChangePreview,
    ProjectFault,
    ProjectTransactions,
    state_diff,
)
from ontolearn_engine.rdf_snapshot import TermInputError, iri, term
from ontolearn_engine.storage import LAYERS, Conflict, canonical, digest

MAX_DOCUMENT = 16 * 1024 * 1024
SEGMENT_BYTES = 32768
PLAN_VERSION = "preparedChangeSetVersion"
RECEIPT_VERSION = "changesetConfirmationReceiptVersion"
IMPACT_VERSION = "changesetUndoImpactVersion"
CURSOR_KIND = "changeset-document-v1"
FAMILIES = LAYERS


def _lifecycle_version(store, project):
    from ontolearn_engine.project.management import lifecycle

    return lifecycle(store, store._project(project))["version"]


def _current_lifecycle(store, project, envelope):
    # Version 1 predates lifecycle transitions. It remains valid historical
    # evidence, but cannot authorize work after a trash/restore cycle.
    version = envelope.get(PLAN_VERSION, envelope.get(IMPACT_VERSION))
    if (
        type(version) is not int
        or version not in (1, 2)
        or (version == 1 and "lifecycleVersion" in envelope)
        or (
            version == 2
            and (
                type(envelope.get("lifecycleVersion")) is not int
                or envelope["lifecycleVersion"] < 0
            )
        )
    ):
        fail("INVALID_STATE")
    return envelope.get("lifecycleVersion", 0) == _lifecycle_version(store, project)


def fail(code, **params):
    # Import late: JobStore's thin methods import this module in turn.
    from ontolearn_engine.job_store import fault

    fault(code, **params)


def _host(host, session):
    from ontolearn_engine.job_store import UUID

    if any(not isinstance(v, str) or not UUID.fullmatch(v) for v in (host, session)):
        fail("IDENTITY_CONFLICT")


def pack(preview):
    return {
        "project": preview.project,
        "base": preview.base,
        "plan": json.loads(preview.plan_json),
        "before": json.loads(preview.before_json),
        "after": json.loads(preview.after_json),
        "intent": preview.intent,
        "target": preview.target,
        "overwrittenOperations": list(preview.overwritten_operations),
        "controlBefore": json.loads(preview.control_before_json),
        "controlAfter": json.loads(preview.control_after_json),
    }


def unpack(value):
    if not isinstance(value, dict) or set(value) != {
        "project",
        "base",
        "plan",
        "before",
        "after",
        "intent",
        "target",
        "overwrittenOperations",
        "controlBefore",
        "controlAfter",
    }:
        fail("INVALID_STATE")
    return ChangePreview(
        value["project"],
        value["base"],
        canonical(value["plan"]),
        canonical(value["before"]),
        canonical(value["after"]),
        value["intent"],
        value["target"],
        tuple(value["overwrittenOperations"]),
        canonical(value["controlBefore"]),
        canonical(value["controlAfter"]),
    )


def _formal_quality_definition(record):
    """FR-504/505: touched rule/constraint ChangeSets must be formal definitions.

    The strict complete-schema editor language from quality.definitions is the
    only accepted payload shape; ``{"layer": "rule", "id": "x", "value": {}}``
    and any other partial/opaque value stay rejected here. Untouched stored
    opaque definitions are never rewritten (see test_preview_zero_domain_writes).
    """
    from ontolearn_engine.quality.definitions import (
        DefinitionError,
        validate_definition,
    )

    value = json.loads(record["payload"])
    try:
        validated = validate_definition(value)
    except (DefinitionError, ValueError, TypeError, KeyError):
        raise ValueError("Unsupported quality definition payload") from None
    if (
        validated.payload() != value
        or value.get("kind") != record["layer"]
        or value.get("id") != record["id"]
    ):
        raise ValueError("Non-canonical quality definition")


def _definition(store, record):
    if record["layer"] in {"rule", "constraint"}:
        _formal_quality_definition(record)
        return
    if record["layer"] not in {"ontology", "query"}:
        raise ValueError("Unsupported touched definition")
    value = json.loads(record["payload"])
    if not isinstance(value, dict):
        raise ValueError("Unsupported touched payload")
    if record["layer"] != "ontology":
        from ontolearn_engine.project.query_definitions import draft, scalar

        if not scalar(value.get("text")):
            raise ValueError("Unsupported query text")
        if "descriptor" not in value:
            # Existing snapshots may predate managed query definitions. The
            # incoming ChangeSet schema still requires a managed descriptor;
            # this branch authenticates the historical side of a real Diff/Undo.
            if set(value) - {"text", "references"}:
                raise ValueError("Unsupported legacy query payload")
        else:
            if set(value) != {"text", "references", "descriptor"}:
                raise ValueError("Unsupported managed query payload")
            descriptor = value["descriptor"]
            if (
                type(descriptor) is not dict
                or set(descriptor)
                != {"version", "name", "description", "scope", "capabilityQuestion", "source"}
                or type(descriptor["version"]) is not int
                or descriptor["version"] != 1
            ):
                raise ValueError("Unsupported query descriptor")
            visible = {key: item for key, item in descriptor.items() if key != "version"}
            visible["sparql"] = value["text"]
            if draft(visible, stored=True) != visible:
                raise ValueError("Noncanonical managed query definition")
    store._definition(value)
    for ref in value.get("references", []):
        if (
            not isinstance(ref, dict)
            or set(ref) != {"layer", "id"}
            or ref["layer"] not in FAMILIES
            or not isinstance(ref["id"], str)
            or not ref["id"]
        ):
            raise ValueError("Unsupported reference")


def supported(store, preview):
    """Historical records have no incoming-frame size limit; only typed shape."""
    before, after = json.loads(preview.before_json), json.loads(preview.after_json)
    restoring = preview.intent == "undo"
    if restoring:
        validate_compensation(before, after)
    else:
        validate_change(before, after)
    for item in state_diff(before, after):
        key = item["resource"][0]
        if key == "definition" and item["resource"][1] == "ontology":
            validate_supported_pair(item["before"], item["after"], compensation=restoring)
        for record in (item["before"], item["after"]):
            if record is None:
                continue
            if key == "definition":
                _definition(store, record)
            elif key == "fact":
                if record["owner"] is not None or record["source_row"] is not None:
                    raise ValueError("Mapped facts are outside formal manual ChangeSets")
                # Edits preserve their original ID: validate RDF through the actual
                # Store preview, not an invented new content-derived identity.
                if record["managed_value"] is not None:
                    raise ValueError("Managed facts are outside formal manual ChangeSets")
            else:
                raise ValueError("Unsupported touched state")


def _document(items, kind):
    raw = canonical(items).encode("utf-8")
    if len(raw) > MAX_DOCUMENT:
        fail("RESOURCE_LIMIT", resource="page")
    pieces = [raw[i : i + SEGMENT_BYTES] for i in range(0, len(raw), SEGMENT_BYTES)]
    segments, values = [], []
    for index, data in enumerate(pieces):
        descriptor = {
            "ordinal": index,
            "byteOffset": index * SEGMENT_BYTES,
            "rawByteLength": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        segments.append(descriptor)
        values.append({**descriptor, "dataBase64": base64.b64encode(data).decode("ascii")})
    manifest = {
        "documentKind": kind,
        "documentHash": hashlib.sha256(raw).hexdigest(),
        "totalBytes": len(raw),
        "segmentCount": len(segments),
        "segments": segments,
    }
    return manifest, values


def _wire_room(store, result, limits):
    # Reserve the envelope's fixed binding fields as well as the result itself.
    budget = min(262144, limits["maxFrameBytes"])
    if len(canonical(result).encode()) + 1024 > budget:
        fail("RESOURCE_LIMIT", resource="frame")


def _page_room(project, preview_hash, manifest, segments, limits):
    # A persisted preview must have a usable first/individual page under the
    # negotiated limits; never save a document that cannot be fully delivered.
    for segment in segments:
        sample = {
            "projectId": project,
            "previewHash": preview_hash,
            "documentKind": manifest["documentKind"],
            "documentHash": manifest["documentHash"],
            "segments": [segment],
            "nextCursor": "00000000-0000-4000-8000-000000000000",
            "complete": False,
        }
        if len(canonical(sample).encode()) + 1024 > min(
            limits["maxPageBytes"], limits["maxFrameBytes"], 262144
        ):
            fail("RESOURCE_LIMIT", resource="page")


def _persist_segments(store, project, segments, hook):
    refs = []
    for segment in segments:
        refs.append(_intern_blob(store, project, segment))
        hook("changeset_segment")
    return refs


def _intern_blob(store, project, value):
    """INSERT OR IGNORE is not evidence that the immutable old row is valid."""
    ref = store.put_blob(project, value)
    if ref != digest(value) or store.blob(project, ref) != value:
        fail("INVALID_STATE")
    return ref


def _snapshot_id(store, preview):
    snapshot = {
        "project": preview.project,
        "projectRevision": preview.base,
        "dependencyVector": store.vector(preview.project),
        "state": json.loads(preview.before_json),
    }
    return digest(snapshot)


def _ready(store, project, ref, envelope):
    preview = unpack(envelope["preview"])
    return {
        "status": "ready",
        "projectId": project,
        "baseRevision": preview.base,
        "previewHash": preview.identity,
        "preparedPlanRef": ref,
        "inputSnapshotId": envelope["inputSnapshotId"],
        "parametersHash": envelope["parametersHash"],
        "intent": preview.intent,
        "targetOperationId": preview.target,
        "summary": preview.summary,
        "manifest": envelope["manifest"],
    }


def _evidence_state(store, internal, ref):
    snap = compensation.trusted_snapshot(store, internal, ref)
    return {
        **snap["state"],
        "retirements": sorted(compensation.retirement_at(store, internal, snap["projectRevision"])),
    }


def _unsupported_item(target, reason="evidence-unavailable"):
    return {"reason": reason, "resource": ["operation", target], "targetOperationId": target}


def impact(store, internal, target, base):
    """Project actual history and inverse candidate; never infer from error text."""
    marker = store.marker(internal, target)
    if marker is None:
        fail("NOT_FOUND", resource="operation")
    entries = []
    try:
        row = store._db.execute("SELECT context FROM jobs WHERE id=?", (marker["job"],)).fetchone()
        if row is None:
            return [_unsupported_item(target, "unsupported-state")], False
        context = json.loads(row[0])
        if context["capability"] != "changeset.commit" or context["plan"].get(PLAN_VERSION) not in (
            1,
            2,
        ):
            return [_unsupported_item(target, "unsupported-state")], False
        accepted = store._db.execute(
            "SELECT * FROM operation_claims WHERE operation=?", (target,)
        ).fetchone()
        if accepted is None:
            return [_unsupported_item(target)], False
        job = store._accepted_job(
            accepted,
            context["projectId"],
            context["capability"],
            context["input"],
            context["confirmationRef"],
            context["implementation"],
            context["limits"],
        )
        preview = unpack(context["plan"]["preview"])
        if (
            job["state"] != "succeeded"
            or ProjectTransactions(store).reconcile(preview, target, job["jobId"])["status"]
            != "committed"
        ):
            return [_unsupported_item(target)], False
        supported(store, preview)
        before = _evidence_state(store, internal, marker["before_snapshot"])
        after = _evidence_state(store, internal, marker["after_snapshot"])
        current = {**store.state(internal), "retirements": store.retirement_control(internal)}
        old, new, now = map(compensation._records, (before, after, current))
        changed = compensation._changes(before, after)
        for key in sorted(changed):
            if now.get(key) != new.get(key):
                entries.append(
                    {
                        "reason": "value-changed",
                        "resource": list(key),
                        "targetOperationId": target,
                        "targetBeforeSnapshotRef": marker["before_snapshot"],
                        "targetAfterSnapshotRef": marker["after_snapshot"],
                        "targetBefore": old.get(key),
                        "targetAfter": new.get(key),
                        "current": now.get(key),
                    }
                )
        rows = store._db.execute(
            "SELECT operation,revision FROM commits WHERE project=? AND revision>? "
            "AND revision<=? ORDER BY revision",
            (internal, marker["revision"], base),
        ).fetchall()
        expected = marker["revision"] + 1
        for row in rows:
            later = store.marker(internal, row["operation"])
            if (
                row["revision"] != expected
                or digest(json.loads(later["plan"])) != later["fingerprint"]
            ):
                raise ValueError("Incomplete history")
            left = _evidence_state(store, internal, later["before_snapshot"])
            right = _evidence_state(store, internal, later["after_snapshot"])
            left_records, right_records = map(compensation._records, (left, right))
            for key in sorted(changed & compensation._changes(left, right)):
                entries.append(
                    {
                        "reason": "later-edit",
                        "resource": list(key),
                        "targetOperationId": target,
                        "operationId": row["operation"],
                        "revision": row["revision"],
                        "beforeSnapshotRef": later["before_snapshot"],
                        "afterSnapshotRef": later["after_snapshot"],
                        "before": left_records.get(key),
                        "after": right_records.get(key),
                    }
                )
            expected += 1
        if expected != base + 1:
            raise ValueError("Incomplete history")
        candidate = deepcopy(now)
        for key in changed:
            if key in old:
                candidate[key] = deepcopy(old[key])
            else:
                candidate.pop(key, None)
        definitions = {key[1:]: value for key, value in candidate.items() if key[0] == "definition"}
        for key, definition in sorted(definitions.items()):
            value = json.loads(definition["payload"])
            for ref in value.get("references", []) if isinstance(value, dict) else []:
                target_key = (ref["layer"], ref["id"])
                if target_key not in definitions:
                    entries.append(
                        {
                            "reason": "reference-block",
                            "resource": ["definition", *key],
                            "target": ["definition", *target_key],
                            "definition": definition,
                            "targetOperationId": target,
                        }
                    )
        singles = set()
        for key, definition in definitions.items():
            value = json.loads(definition["payload"])
            if key[0] == "ontology" and isinstance(value, dict):
                singles.update(value.get("singleValuedPredicates", []))
        slots = {}
        for key, fact in candidate.items():
            if key[0] == "fact":
                slots.setdefault((fact["subject"], fact["predicate"]), []).append(fact)
        for (subject, predicate), facts in sorted(slots.items()):
            active = [fact for fact in facts if fact["object"] is not None]
            duplicate = len({f["object"] for f in active}) != len(active)
            reserved = any(
                other["id"] == digest([subject, predicate, fact["object"]])
                for fact in active
                for other in facts
                if other["id"] != fact["id"]
            )
            if duplicate or reserved or (predicate in singles and len(active) > 1):
                entries.append(
                    {
                        "reason": "ownership-block"
                        if duplicate or reserved
                        else "single-value-block",
                        "resource": ["slot", subject, predicate],
                        "facts": sorted(facts, key=lambda f: f["id"]),
                        "targetOperationId": target,
                    }
                )
        return entries, True
    except (Conflict, ValueError, KeyError, TypeError):
        return [*entries, _unsupported_item(target)], False


def preview_changeset(
    store,
    project,
    base,
    request,
    *,
    host_client_id,
    engine_session_id,
    limits,
    hook,
    ownership_proof=None,
):
    if store.actual_format != 3:
        fail("INVALID_STATE")
    _host(host_client_id, engine_session_id)
    store._valid("params_changeset.preview", request)
    store._valid("limits", limits)
    _wire_room(store, request, limits)
    if request["projectId"] != project or request["baseRevision"] != base:
        fail("IDENTITY_CONFLICT")
    if ownership_proof is not None:
        store._ownership_proof(ownership_proof, project, "changeset.preview")
        if ownership_proof.request_hash != digest(request) or ownership_proof.base != base:
            fail("PERMISSION_DENIED")
    internal = store._project(project)
    with store._application(project, "plan", hook, ownership_proof=ownership_proof):
        if store.revision(internal) != base:
            fail("REVISION_CONFLICT", expected=base, actual=store.revision(internal))
        transactions = ProjectTransactions(store)
        conflict = None
        if request["intent"] == "change":
            # Only direct caller terms get known syntax/policy rejection.
            # Unknown parser/N3/Store/preview failures retain UNKNOWN/HOLD;
            # edits validate values without deriving or replacing their IDs.
            for fact in request["plan"].get("manual", []):
                try:
                    iri(fact["subject"])
                    iri(fact["predicate"])
                except TermInputError:
                    fail("INVALID_REQUEST", field="params")
            values = [fact["object"] for fact in request["plan"].get("manual", [])]
            values.extend(request["plan"].get("edits", {}).values())
            for value in values:
                try:
                    parsed = term(value)
                except TermInputError:
                    fail("INVALID_REQUEST", field="params")
                if parsed.n3() != value:
                    fail("INVALID_REQUEST", field="params")
            try:
                effective_plan = merge_plan(store.state(internal), request["plan"])
            except (ValueError, KeyError, TypeError):
                fail("INVALID_REQUEST", field="params")
            try:
                preview = transactions.preview(internal, base, effective_plan)
            except MetadataError:
                fail("INVALID_REQUEST", field="params")
            try:
                supported(store, preview)
            except (ValueError, KeyError, TypeError):
                fail("INVALID_REQUEST", field="params")
        else:
            target = request["targetOperationId"]
            entries, complete = impact(store, internal, target, base)
            if entries or not complete:
                conflict = (entries, complete)
            else:
                try:
                    preview = transactions.preview_undo(internal, target)
                    supported(store, preview)
                except (ProjectFault, Conflict, ValueError, KeyError, TypeError):
                    conflict = ([_unsupported_item(target)], False)
        if conflict is not None:
            entries, complete = conflict
            manifest, segments = _document(entries, "undo-impact")
            envelope = {
                IMPACT_VERSION: 2,
                "lifecycleVersion": _lifecycle_version(store, project),
                "projectId": project,
                "hostClientId": host_client_id,
                "engineSessionId": engine_session_id,
                "baseRevision": base,
                "targetOperationId": target,
                "items": entries,
                "impactComplete": complete,
                "manifest": manifest,
                "segmentBlobRefs": [digest(value) for value in segments],
            }
            identity = digest(envelope)
            result = {
                "status": "conflict",
                "projectId": project,
                "baseRevision": base,
                "previewHash": identity,
                "targetOperationId": target,
                "summary": f"撤销暂停：{len(entries)} 项影响",
                "impactComplete": complete,
                "manifest": manifest,
            }
            _wire_room(store, result, limits)
            _page_room(project, identity, manifest, segments, limits)
            _persist_segments(store, project, segments, hook)
            store._db.execute(
                "INSERT OR IGNORE INTO job_details VALUES(?,?,?)",
                (identity, project, canonical(envelope)),
            )
            saved = store._db.execute(
                "SELECT project,payload FROM job_details WHERE id=?", (identity,)
            ).fetchone()
            if saved is None or tuple(saved) != (project, canonical(envelope)):
                fail("INVALID_STATE")
            _verify_document(store, project, envelope, entries)
            hook("changeset_impact")
            store._valid("result_changeset.preview", result)
            return result
        manifest, segments = _document(preview.diff, "diff")
        parameters = {
            "changeSetParametersVersion": 1,
            "previewHash": preview.identity,
            "intent": preview.intent,
            "targetOperationId": preview.target,
        }
        envelope = {
            PLAN_VERSION: 2,
            "lifecycleVersion": _lifecycle_version(store, project),
            "projectId": project,
            "hostClientId": host_client_id,
            "engineSessionId": engine_session_id,
            "preview": pack(preview),
            "inputSnapshotId": _snapshot_id(store, preview),
            "parametersHash": digest(parameters),
            "manifest": manifest,
            "segmentBlobRefs": [digest(value) for value in segments],
        }
        ref = digest(envelope)
        result = _ready(store, project, ref, envelope)
        _wire_room(store, result, limits)
        _page_room(project, preview.identity, manifest, segments, limits)
        # Snapshot/parameters/segments/plan are atomic; no confirmation is signed here.
        if store.snapshot(internal) != envelope["inputSnapshotId"]:
            fail("INVALID_STATE")
        _intern_blob(store, project, parameters)
        _persist_segments(store, project, segments, hook)
        store._db.execute(
            "INSERT OR IGNORE INTO job_plans VALUES(?,?,?,?,?,?)",
            (
                ref,
                project,
                base,
                transactions._fingerprint(preview),
                manifest["documentHash"],
                canonical(envelope),
            ),
        )
        saved = store._db.execute("SELECT * FROM job_plans WHERE ref=?", (ref,)).fetchone()
        if saved is None or saved["project"] != project or saved["payload"] != canonical(envelope):
            fail("INVALID_STATE")
        _verify_plan(store, project, saved, json.loads(saved["payload"]))
        hook("changeset_plan")
        store._valid("result_changeset.preview", result)
        return result


def _envelope(store, project, preview_hash, host, session, kind):
    _host(host, session)
    for row in store._db.execute("SELECT * FROM job_plans WHERE project=?", (project,)):
        value = json.loads(row["payload"])
        if value.get(PLAN_VERSION) in (1, 2) and unpack(value["preview"]).identity == preview_hash:
            if (value["hostClientId"], value["engineSessionId"]) != (host, session):
                continue
            _verify_plan(store, project, row, value)
            if not _current_lifecycle(store, project, value):
                continue
            if kind != "diff":
                fail("CURSOR_MISMATCH")
            return row["ref"], value
    for row in store._db.execute("SELECT * FROM job_details WHERE project=?", (project,)):
        value = json.loads(row["payload"])
        if value.get(IMPACT_VERSION) in (1, 2) and digest(value) == preview_hash:
            if (value["hostClientId"], value["engineSessionId"]) != (host, session):
                continue
            if row["id"] != preview_hash or kind != "undo-impact":
                fail("INVALID_STATE")
            if not _current_lifecycle(store, project, value):
                continue
            _verify_document(store, project, value, value["items"])
            return None, value
    fail("IDENTITY_CONFLICT")


def _verify_document(store, project, envelope, items):
    manifest, expected = _document(items, envelope["manifest"]["documentKind"])
    if (
        manifest != envelope["manifest"]
        or [digest(v) for v in expected] != envelope["segmentBlobRefs"]
    ):
        fail("INVALID_STATE")
    for ref, value in zip(envelope["segmentBlobRefs"], expected, strict=True):
        if store.blob(project, ref) != value:
            fail("INVALID_STATE")


def _verify_plan(store, project, row, envelope):
    fields = {
        PLAN_VERSION,
        "projectId",
        "hostClientId",
        "engineSessionId",
        "preview",
        "inputSnapshotId",
        "parametersHash",
        "manifest",
        "segmentBlobRefs",
    }
    version = envelope.get(PLAN_VERSION)
    if type(version) is not int or version not in (1, 2):
        fail("INVALID_STATE")
    if version == 2:
        fields.add("lifecycleVersion")
        if type(envelope.get("lifecycleVersion")) is not int or envelope["lifecycleVersion"] < 0:
            fail("INVALID_STATE")
    if (
        set(envelope) != fields
        or digest(envelope) != row["ref"]
        or envelope["projectId"] != project
    ):
        fail("INVALID_STATE")
    _host(envelope["hostClientId"], envelope["engineSessionId"])
    preview = unpack(envelope["preview"])
    if (
        preview.project != store._project(project)
        or preview.base != row["base"]
        or row["plan_hash"] != ProjectTransactions._fingerprint(preview)
        or row["diff_hash"] != envelope["manifest"]["documentHash"]
        or envelope["manifest"]["documentKind"] != "diff"
        or preview.intent not in {"change", "undo"}
    ):
        fail("INVALID_STATE")
    snap = store._project_snapshot(envelope["inputSnapshotId"], preview.project)
    if snap["projectRevision"] != preview.base or canonical(snap["state"]) != preview.before_json:
        fail("INVALID_STATE")
    parameters = {
        "changeSetParametersVersion": 1,
        "previewHash": preview.identity,
        "intent": preview.intent,
        "targetOperationId": preview.target,
    }
    if (
        digest(parameters) != envelope["parametersHash"]
        or store.blob(project, envelope["parametersHash"]) != parameters
    ):
        fail("INVALID_STATE")
    supported(store, preview)
    _verify_document(store, project, envelope, preview.diff)
    return preview


def _binding(project, ref, envelope, preview_hash):
    return {
        "projectId": project,
        "hostClientId": envelope["hostClientId"],
        "engineSessionId": envelope["engineSessionId"],
        "previewHash": preview_hash,
        "documentKind": envelope["manifest"]["documentKind"],
        "documentHash": envelope["manifest"]["documentHash"],
        "preparedPlanRef": ref,
        "baseRevision": envelope.get("baseRevision", envelope.get("preview", {}).get("base")),
    }


def diff_page(
    store,
    project,
    preview_hash,
    document_kind,
    page_size,
    cursor,
    *,
    host_client_id,
    engine_session_id,
    limits,
):
    store._valid(
        "params_changeset.diff.page",
        {
            "projectId": project,
            "previewHash": preview_hash,
            "documentKind": document_kind,
            "pageSize": page_size,
            "cursor": cursor,
        },
    )
    store._valid("limits", limits)
    with store._transaction():
        ref, envelope = _envelope(
            store, project, preview_hash, host_client_id, engine_session_id, document_kind
        )
        binding = _binding(project, ref, envelope, preview_hash)
        offset = 0
        if cursor is not None:
            position = store._cursor(cursor, CURSOR_KIND, binding, page_size)
            offset = position["byteOffset"]
            if offset >= envelope["manifest"]["totalBytes"]:
                fail("CURSOR_MISMATCH")
        values = [store.blob(project, value) for value in envelope["segmentBlobRefs"]]
        chosen = []
        for value in values:
            if value["byteOffset"] < offset:
                continue
            candidate = {
                "projectId": project,
                "previewHash": preview_hash,
                "documentKind": document_kind,
                "documentHash": envelope["manifest"]["documentHash"],
                "segments": [*chosen, value],
                "nextCursor": "00000000-0000-4000-8000-000000000000",
                "complete": False,
            }
            if len(canonical(candidate).encode()) + 1024 > min(
                limits["maxPageBytes"], limits["maxFrameBytes"], 262144
            ):
                break
            chosen.append(value)
            if len(chosen) == page_size:
                break
        if not chosen or chosen[0]["byteOffset"] != offset:
            fail("RESOURCE_LIMIT", resource="page")
        end = chosen[-1]["byteOffset"] + chosen[-1]["rawByteLength"]
        token = store._new_cursor(
            CURSOR_KIND,
            binding,
            page_size,
            {
                "startOffset": offset,
                "byteOffset": end,
                "previousCursor": cursor,
            },
        )
        result = {
            "projectId": project,
            "previewHash": preview_hash,
            "documentKind": document_kind,
            "documentHash": envelope["manifest"]["documentHash"],
            "segments": chosen,
            "nextCursor": token,
            "complete": end == envelope["manifest"]["totalBytes"],
        }
        store._valid("result_changeset.diff.page", result)
        return result


def _receipt(store, project, ref, envelope, confirmation, *, request=None):
    row = store._db.execute(
        "SELECT * FROM job_confirmations WHERE project=? AND id=?", (project, confirmation)
    ).fetchone()
    detail = store._db.execute(
        "SELECT * FROM job_details WHERE project=? AND id=?", (project, confirmation)
    ).fetchone()
    if row is None or detail is None:
        fail("IDENTITY_CONFLICT" if request is not None else "INVALID_STATE")
    value = json.loads(detail["payload"])
    preview = unpack(envelope["preview"])
    result = {
        "projectId": project,
        "previewHash": preview.identity,
        "preparedPlanRef": ref,
        "confirmationRef": confirmation,
        "inputSnapshotId": envelope["inputSnapshotId"],
        "parametersHash": envelope["parametersHash"],
    }
    expected_fields = {
        RECEIPT_VERSION,
        "request",
        "requestHash",
        "hostClientId",
        "engineSessionId",
        "result",
    }
    if (
        set(value) != expected_fields
        or value[RECEIPT_VERSION] != 1
        or value["requestHash"] != digest(value["request"])
        or value["request"]["projectId"] != project
        or value["request"]["previewHash"] != preview.identity
        or value["hostClientId"] != envelope["hostClientId"]
        or value["engineSessionId"] != envelope["engineSessionId"]
        or value["result"] != result
        or row["plan_ref"] != ref
        or row["base"] != preview.base
        or row["plan_hash"] != ProjectTransactions._fingerprint(preview)
        or row["actor"] != envelope["hostClientId"]
        or row["permission"] != "write"
    ):
        fail("INVALID_STATE")
    store._valid("params_changeset.confirm", value["request"])
    if request is not None and value["request"] != request:
        fail("IDENTITY_CONFLICT")
    return result


def confirm(
    store, project, preview_hash, completion_cursor, *, host_client_id, engine_session_id, hook
):
    request = {
        "projectId": project,
        "previewHash": preview_hash,
        "completionCursor": completion_cursor,
    }
    store._valid("params_changeset.confirm", request)
    with store._application(project, "plan", hook):
        ref, envelope = _envelope(
            store, project, preview_hash, host_client_id, engine_session_id, "diff"
        )
        existing = store._db.execute(
            "SELECT id FROM job_confirmations WHERE project=? AND plan_ref=?", (project, ref)
        ).fetchall()
        # The signing row and immutable versioned receipt are one indivisible
        # authority. An orphan receipt is corruption, never permission to re-sign.
        receipt_ids = []
        for detail in store._db.execute(
            "SELECT id,payload FROM job_details WHERE project=?", (project,)
        ):
            value = json.loads(detail["payload"])
            if (
                isinstance(value, dict)
                and value.get(RECEIPT_VERSION) == 1
                and value.get("result", {}).get("preparedPlanRef") == ref
            ):
                receipt_ids.append(detail["id"])
        if set(receipt_ids) != {row[0] for row in existing}:
            fail("INVALID_STATE")
        if existing:
            if len(existing) != 1:
                fail("INVALID_STATE")
            return _receipt(store, project, ref, envelope, existing[0][0], request=request)
        preview = unpack(envelope["preview"])
        binding = _binding(project, ref, envelope, preview_hash)
        token, expected_end, seen, size = (
            completion_cursor,
            envelope["manifest"]["totalBytes"],
            set(),
            None,
        )
        boundaries = {s["byteOffset"] for s in envelope["manifest"]["segments"]} | {expected_end}
        while token is not None:
            if token in seen:
                fail("CURSOR_MISMATCH")
            seen.add(token)
            row = store._db.execute("SELECT size FROM job_cursors WHERE id=?", (token,)).fetchone()
            if row is None:
                fail("CURSOR_MISMATCH")
            if size is None:
                size = row[0]
            position = store._cursor(token, CURSOR_KIND, binding, size)
            if (
                set(position) != {"startOffset", "byteOffset", "previousCursor"}
                or position["byteOffset"] != expected_end
                or position["startOffset"] not in boundaries
                or not 0 <= position["startOffset"] < expected_end
            ):
                fail("CURSOR_MISMATCH")
            expected_end = position["startOffset"]
            token = position["previousCursor"]
        if expected_end != 0:
            fail("CURSOR_MISMATCH")
        if store.revision(preview.project) != preview.base:
            fail("REVISION_CONFLICT", expected=preview.base, actual=store.revision(preview.project))
        fresh = ProjectTransactions(store).preview(
            preview.project,
            preview.base,
            json.loads(preview.plan_json),
            intent=preview.intent,
            target=preview.target,
            overwritten_operations=preview.overwritten_operations,
        )
        if fresh != preview:
            fail("IDENTITY_CONFLICT")
        confirmation = str(uuid4())
        result = {
            "projectId": project,
            "previewHash": preview_hash,
            "preparedPlanRef": ref,
            "confirmationRef": confirmation,
            "inputSnapshotId": envelope["inputSnapshotId"],
            "parametersHash": envelope["parametersHash"],
        }
        store._db.execute(
            "INSERT INTO job_confirmations VALUES(?,?,?,?,?,?,?)",
            (
                confirmation,
                project,
                ref,
                preview.base,
                ProjectTransactions._fingerprint(preview),
                host_client_id,
                "write",
            ),
        )
        hook("changeset_confirmation")
        receipt = {
            RECEIPT_VERSION: 1,
            "request": request,
            "requestHash": digest(request),
            "hostClientId": host_client_id,
            "engineSessionId": engine_session_id,
            "result": result,
        }
        store._db.execute(
            "INSERT INTO job_details VALUES(?,?,?)", (confirmation, project, canonical(receipt))
        )
        hook("changeset_confirmation_receipt")
        store._valid("result_changeset.confirm", result)
        return result


def accepted_plan(store, project, input_, confirmation, snapshot, *, host=None):
    row = store._db.execute(
        "SELECT * FROM job_plans WHERE project=? AND ref=?", (project, input_["preparedPlanRef"])
    ).fetchone()
    if row is None:
        fail("IDENTITY_CONFLICT")
    envelope = json.loads(row["payload"])
    if envelope.get(PLAN_VERSION) not in (1, 2):
        fail("IDENTITY_CONFLICT")
    preview = _verify_plan(store, project, row, envelope)
    if (
        input_["definitionId"] != "changeset"
        or input_["scope"] != "asserted"
        or input_["derivedResultIds"] != []
        or input_["inputSnapshotId"] != envelope["inputSnapshotId"]
        or input_["parametersHash"] != envelope["parametersHash"]
        or snapshot["projectRevision"] != preview.base
    ):
        fail("IDENTITY_CONFLICT")
    _receipt(store, project, row["ref"], envelope, confirmation)
    if host is not None:
        if not _current_lifecycle(store, project, envelope):
            fail("IDENTITY_CONFLICT")
        if host != (envelope["hostClientId"], envelope["engineSessionId"]):
            fail("IDENTITY_CONFLICT")
        if store.revision(preview.project) != preview.base:
            fail("REVISION_CONFLICT", expected=preview.base, actual=store.revision(preview.project))
        if (
            canonical(store.state(preview.project)) != preview.before_json
            or canonical(store.retirement_control(preview.project)) != preview.control_before_json
        ):
            fail("IDENTITY_CONFLICT")
    return envelope


def commit(store, job, context, hook):
    envelope = accepted_plan(
        store, job["projectId"], context["input"], context["confirmationRef"], context["snapshot"]
    )
    if envelope != context["plan"]:
        fail("INVALID_STATE")
    preview = unpack(envelope["preview"])
    marker = ProjectTransactions(store).commit(
        preview,
        job["operationId"],
        job["jobId"],
        confirmed_preview=preview.identity,
        hook=hook,
    )
    # Same outer _application transaction as the marker above: the staged
    # agent full-assistance marking for this exact ChangeSet either lands
    # with the committed domain state or rolls back with it (B05).
    from ontolearn_engine.project import learning_agent

    learning_agent.apply_pending_assistance(
        store, job["projectId"], job["operationId"], preview.base
    )
    return marker
