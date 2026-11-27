"""Internal blank-create transaction mechanics, not an authorized host service.

Only Store.commit delegates here. Origin is persisted input, never permission or
physical dispatch proof. No path, connection factory, public capability, scope
factory, resolution, or replay across a host boundary is provided.
"""

import json
import sqlite3
from uuid import uuid4

from ontolearn_engine.project import format3
from ontolearn_engine.project.applications import uuid_ref
from ontolearn_engine.project.project_host import HostReadFault, ProjectHostReader, ReadLimits
from ontolearn_engine.storage import canonical, digest


class CreationFault(ValueError):
    def __init__(self, reason):
        if reason not in {"input", "state", "structure", "limit", "identity"}:
            raise ValueError("Invalid creation reason")
        super().__init__(reason)
        self.reason = reason


def require(condition, reason="structure"):
    if not condition:
        raise CreationFault(reason)


def encoded(value, maximum):
    try:
        result = canonical(value).encode("utf-8")
    except (ValueError, TypeError, OverflowError, RecursionError):
        raise CreationFault("input") from None
    require(len(result) <= maximum, "limit")
    return result


def request_value(value):
    require(
        type(value) is dict
        and len(value) == 4
        and set(value)
        == {
            "requestVersion",
            "operationId",
            "initialization",
            "name",
        },
        "input",
    )
    require(type(value["requestVersion"]) is int and value["requestVersion"] == 1, "input")
    require(
        type(value["operationId"]) is str
        and len(value["operationId"]) == 36
        and uuid_ref(value["operationId"]),
        "input",
    )
    require(
        type(value["initialization"]) is dict
        and len(value["initialization"]) == 1
        and set(value["initialization"]) == {"kind"}
        and type(value["initialization"]["kind"]) is str
        and value["initialization"]["kind"] == "blank",
        "input",
    )
    name = value["name"]
    require(
        type(name) is str and 0 < len(name) <= 4096 and bool(name.strip()) and "\0" not in name,
        "input",
    )
    try:
        require(len(name.encode("utf-8")) <= 4096, "limit")
    except UnicodeError:
        raise CreationFault("input") from None
    return json.loads(encoded(value, 16384))


def origin_value(value):
    require(
        type(value) is dict
        and len(value) == 3
        and set(value)
        == {
            "hostClientId",
            "engineSessionId",
            "permission",
        },
        "input",
    )
    require(
        all(
            type(value[k]) is str and len(value[k]) == 36 and uuid_ref(value[k])
            for k in ("hostClientId", "engineSessionId")
        ),
        "input",
    )
    require(type(value["permission"]) is str and value["permission"] == "library.create", "input")
    return json.loads(encoded(value, 1024))


def library_evidence(store):
    row = store._db.execute("SELECT migration_id FROM app_format WHERE singleton=1").fetchone()
    require(row is not None and type(row[0]) is str and bool(row[0]))
    return digest(["ontolearn.library-evidence", 1, row[0]])


def model(project, request, origin, library, *, actual_genesis=None):
    """Pure encoded candidate; no candidate is treated as existing evidence."""
    operation = request["operationId"]
    domain = {
        "project": project,
        "projectRevision": 0,
        "dependencyVector": {},
        "state": {"mappingState": {}, "definitions": [], "facts": []},
    }
    snapshot = digest(domain)
    meta = {**format3.metadata("created"), "name": request["name"]}
    before = {
        "checkpointVersion": 1,
        "databaseFormatVersion": 3,
        "applicationStateSchemaVersion": 1,
        "project": project,
        "domainSnapshotRef": snapshot,
        "domainRevision": 0,
        "operationSequence": 0,
        "coverage": list(format3.COVERAGE),
        "historyCoverage": {
            "legacyDomainOperations": 0,
            "legacyDomainRevision": 0,
            "legacyHistory": "complete",
            "applicationHistory": "from-format3",
        },
        "application": {
            "metadataVersion": 0,
            "metadata": format3.metadata("created"),
            "drafts": [],
            "learningCurrent": [],
            "assistanceAudit": [],
        },
    }
    if actual_genesis is not None:
        require(canonical(actual_genesis) == canonical(before))
        before = json.loads(canonical(actual_genesis))
    after = json.loads(canonical(before))
    after["operationSequence"] = 1
    after["application"]["metadataVersion"] = 1
    after["application"]["metadata"] = meta
    before_ref, after_ref = digest(before), digest(after)
    plan = {
        "projectCreatePlanVersion": 1,
        "projectId": project,
        "domainRevision": 0,
        "inputSnapshotId": snapshot,
        "beforeCheckpointRef": before_ref,
        "beforeCAS": {"metadataVersion": 0, "operationSequence": 0},
        "afterCAS": {"metadataVersion": 1, "operationSequence": 1},
        "initialMetadata": meta,
    }
    context = {
        "projectCreateContextVersion": 1,
        "libraryEvidenceRef": library,
        "projectId": project,
        "project": project,
        "operationId": operation,
        "request": request,
        "requestHash": digest(request),
        "origin": origin,
        "plan": plan,
    }
    proof = {
        "projectCreateReceiptVersion": 1,
        "libraryEvidenceRef": library,
        "projectId": project,
        "operationId": operation,
        "requestHash": digest(request),
        "contextHash": digest(context),
        "planHash": digest(plan),
        "operationSequence": 1,
        "domainRevision": 0,
        "metadataVersion": 1,
        "inputSnapshotId": snapshot,
        "beforeCheckpointRef": before_ref,
        "afterCheckpointRef": after_ref,
    }
    result = {
        "createResultVersion": 1,
        "operationId": operation,
        "projectId": project,
        "requestHash": digest(request),
        "receipt": proof,
    }
    rows = {
        "projects": [(project, 0)],
        "snapshots": [(snapshot, canonical(domain))],
        "app_projects": [(project, 1, 1, canonical(meta), after_ref)],
        "app_checkpoints": [
            (before_ref, project, snapshot, canonical(before)),
            (after_ref, project, snapshot, canonical(after)),
        ],
        "app_origins": [(project, before_ref, 0, 0, "created")],
        "public_projects": [(project, project)],
        "operation_claims": [
            (operation, project, None, digest(context), "application", canonical(context))
        ],
        "app_operations": [(project, 1, operation, "application", digest(plan), 0)],
        "app_receipts": [(project, operation, canonical(proof))],
    }
    return {
        "domain": domain,
        "before": before,
        "after": after,
        "context": context,
        "receipt": proof,
        "result": result,
        "rows": rows,
    }


def creation_context(store, project, operation):
    """Bind this namespace to its persisted effect without reentering history."""
    row = store._db.execute(
        "SELECT * FROM operation_claims WHERE operation=?", (operation,)
    ).fetchone()
    if row is None or row["kind"] != "application":
        return None
    context = format3._json(row["context"])
    if not isinstance(context, dict) or "projectCreateContextVersion" not in context:
        return None
    require(
        type(context["projectCreateContextVersion"]) is int
        and context["projectCreateContextVersion"] == 1
    )
    require(row["job"] is None and row["project"] == project and uuid_ref(project))
    require(
        set(context)
        == {
            "projectCreateContextVersion",
            "libraryEvidenceRef",
            "projectId",
            "project",
            "operationId",
            "request",
            "requestHash",
            "origin",
            "plan",
        }
    )
    request, origin = request_value(context["request"]), origin_value(context["origin"])
    require(request["operationId"] == operation)
    expected = model(project, request, origin, library_evidence(store))
    require(canonical(context) == canonical(expected["context"]))
    require(row["fingerprint"] == digest(context))
    mapping = store._db.execute(
        "SELECT internal FROM public_projects WHERE public=?", (project,)
    ).fetchone()
    require(mapping is not None and mapping[0] == project)
    # A self-consistent claim alone cannot prove that creation actually happened.
    # Check the immutable links directly; receipt_for validates their full history.
    for table, predicate, params in (
        ("app_origins", "project=?", (project,)),
        ("app_operations", "project=? AND operation=?", (project, operation)),
        ("app_receipts", "project=? AND operation=?", (project, operation)),
    ):
        actual = store._db.execute(f"SELECT * FROM {table} WHERE {predicate}", params).fetchall()
        require([tuple(item) for item in actual] == expected["rows"][table])
    return expected


def validate_transition(store, project, op, origin, before, after):
    expected = creation_context(store, project, op["operation"])
    require(expected is not None)
    require(op["kind"] == "application" and op["sequence"] == 1 and op["domain_revision"] == 0)
    require(op["plan_hash"] == expected["receipt"]["planHash"])
    require(tuple(origin) == (project, digest(expected["before"]), 0, 0, "created"))
    require(
        canonical(before) == canonical(expected["before"])
        and canonical(after) == canonical(expected["after"])
    )
    require(store.marker(project, op["operation"]) is None)
    return expected["receipt"]


def _totals(db):
    counts, size = {}, 0
    for (table,) in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
        quoted = '"' + table.replace('"', '""') + '"'
        columns = db.execute(f"PRAGMA table_info({quoted})").fetchall()
        terms = "+".join(
            'coalesce(length(CAST("' + c[1].replace('"', '""') + '" AS BLOB)),0)' for c in columns
        )
        count, amount = db.execute(
            f"SELECT count(*),coalesce(sum({terms}),0) FROM {quoted}"
        ).fetchone()
        counts[table] = count
        size += amount
    return counts, size


def _row_size(db, row):
    return db.execute(
        "SELECT " + "+".join("coalesce(length(CAST(? AS BLOB)),0)" for _ in row), row
    ).fetchone()[0]


def preflight(store, candidate, limits):
    db = store._db
    reader = ProjectHostReader(store, limits=limits)
    reader._preflight()  # Same policy and bounded schema before any materialization.
    counts, total = _totals(db)
    for table, rows in candidate["rows"].items():
        counts[table] = counts.get(table, 0) + len(rows)
        total += sum(_row_size(db, row) for row in rows)
    require(
        sum(counts.values()) <= limits.validation_rows and total <= limits.validation_bytes, "limit"
    )
    require(
        total * (1 + counts.get("app_operations", 0) + counts.get("snapshots", 0))
        <= limits.validation_work,
        "limit",
    )
    require(counts["projects"] <= limits.projects, "limit")
    for k in ("context",):
        require(
            len(encoded(candidate[k], 65536)) + len(encoded(candidate[k]["plan"], 65536)) <= 65536,
            "limit",
        )
    encoded(candidate["receipt"], 16384)
    encoded(candidate["result"], 32768)
    rows = []
    for row in db.execute(
        "SELECT u.public,u.internal,p.revision,a.metadata_version,a.metadata,"
        "a.operation_sequence,a.checkpoint FROM public_projects u "
        "JOIN projects p ON p.id=u.internal JOIN app_projects a ON a.project=p.id"
    ):
        require(len(row["internal"].encode("utf-8")) <= limits.identity_bytes, "limit")
        rows.append(reader._row(row))
    project = candidate["context"]["project"]
    require(len(project.encode("utf-8")) <= limits.identity_bytes, "limit")
    item = {
        "projectId": project,
        "domainRevision": 0,
        "metadataVersion": 1,
        "metadata": candidate["after"]["application"]["metadata"],
        "operationSequence": 1,
        "checkpointRef": digest(candidate["after"]),
    }
    encoded(item["metadata"], limits.metadata_bytes)
    rows.append(item)
    rows.sort(key=lambda row: row["projectId"])
    items = [encoded(row, limits.catalog_row_bytes) for row in rows]
    require(sum(map(len, items)) + 2 + len(items) <= limits.snapshot_bytes, "limit")
    require(768 + len(items) * (limits.catalog_row_bytes + 64) <= limits.retained_bytes, "limit")
    for size in range(1, limits.page_items + 1):
        for offset in range(0, len(rows), size):
            end = min(offset + size, len(rows))
            page = {
                "catalogVersion": 1,
                "snapshotId": "0" * 36,
                "items": rows[offset:end],
                "total": len(rows),
                "offset": offset,
                "nextCursor": "0" * 93 if end < len(rows) else None,
            }
            encoded(page, limits.page_bytes)
    workspace = {
        "workspaceVersion": 1,
        **item,
        "inputSnapshotId": candidate["receipt"]["inputSnapshotId"],
        "draft": {"editor": "\x01" * limits.identity_bytes, "state": "missing"},
    }
    encoded(workspace, limits.workspace_bytes)
    return counts, total


def _actual_rows(store, candidate):
    result = {}
    for table, rows in candidate["rows"].items():
        values = []
        # Each approved table has a single-column key except these two.
        keys = {
            "app_operations": ("project", "sequence"),
            "app_receipts": ("project", "operation"),
        }.get(table)
        for row in rows:
            if keys:
                sql = f"SELECT * FROM {table} WHERE {keys[0]}=? AND {keys[1]}=?"
                found = store._db.execute(sql, row[:2]).fetchone()
            else:
                name = {
                    "projects": "id",
                    "snapshots": "id",
                    "app_projects": "project",
                    "app_checkpoints": "id",
                    "app_origins": "project",
                    "public_projects": "public",
                    "operation_claims": "operation",
                }[table]
                found = store._db.execute(
                    f"SELECT * FROM {table} WHERE {name}=?", (row[0],)
                ).fetchone()
            require(found is not None)
            values.append(tuple(found))
        result[table] = values
    return result


def commit(store, project, base, operation, job, supplied, hook):
    from ontolearn_engine.job_store import JobStore

    require(isinstance(store, JobStore) and store._target_format == 3, "state")
    require(not store._db.in_transaction, "state")
    require(project is None and base is None and job is None, "input")
    require(
        type(supplied) is dict
        and len(supplied) == 4
        and set(supplied) == {"projectCreateCoreVersion", "request", "origin", "readerLimits"},
        "input",
    )
    require(
        type(supplied["projectCreateCoreVersion"]) is int
        and supplied["projectCreateCoreVersion"] == 1,
        "input",
    )
    limits = supplied["readerLimits"]
    require(type(limits) is ReadLimits, "input")
    request, origin = request_value(supplied["request"]), origin_value(supplied["origin"])
    require(request["operationId"] == operation, "identity")
    try:
        with store._transaction(hook):
            require(store._db.execute("PRAGMA user_version").fetchone()[0] == 3, "state")
            # Existing acceptance is checked before the prospective caller's
            # creation policy. Its immutable receipt does not acquire a new CAS
            # or budget identity on retry. The fixed hard read guards still bound
            # validation of existing history; tightened policy applies to new work.
            reader = ProjectHostReader(store)
            reader._preflight()
            reader._validate()
            store._validate_job3()
            claim = store._db.execute(
                "SELECT * FROM operation_claims WHERE operation=?", (operation,)
            ).fetchone()
            if claim is not None:
                require(claim["kind"] == "application", "identity")
                old = creation_context(store, claim["project"], operation)
                require(old is not None, "identity")
                require(
                    old["context"]["request"] == request and old["context"]["origin"] == origin,
                    "identity",
                )
                require(format3.receipt_for(store, claim["project"], operation) == old["receipt"])
                return old["result"]
            require(not store._occupied_operation_evidence(operation), "identity")
            project = str(uuid4())
            require(uuid_ref(project), "state")
            require(
                all(
                    store._db.execute(
                        f"SELECT 1 FROM {table} WHERE {column}=?", (project,)
                    ).fetchone()
                    is None
                    for table, column in (
                        ("projects", "id"),
                        ("public_projects", "public"),
                        ("public_projects", "internal"),
                    )
                ),
                "identity",
            )
            candidate = model(project, request, origin, library_evidence(store))
            for table in ("snapshots", "app_checkpoints"):
                require(
                    all(
                        store._db.execute(f"SELECT 1 FROM {table} WHERE id=?", (r[0],)).fetchone()
                        is None
                        for r in candidate["rows"][table]
                    ),
                    "identity",
                )
            projected = preflight(store, candidate, limits)
            hook("create_preflight")
            store._db.execute("INSERT INTO projects VALUES(?,0)", (project,))
            hook("create_project")
            format3.seed_project(store, project, strict=True, hook=hook)
            genesis = store.project_checkpoint(project)
            require(genesis == candidate["before"])
            hook("create_genesis_verified")
            store._db.execute("INSERT INTO public_projects VALUES(?,?)", (project, project))
            hook("create_public")
            # Candidate hashes were only budget predictions. Construct again
            # from the now verified actual genesis before persisting the claim.
            actual = model(
                project, request, origin, library_evidence(store), actual_genesis=genesis
            )
            require(actual == candidate)
            store._db.execute(
                "INSERT INTO operation_claims VALUES(?,?,?,?,?,?)",
                actual["rows"]["operation_claims"][0],
            )
            hook("create_claim")
            store._db.execute(
                "UPDATE app_projects SET metadata_version=1,operation_sequence=1,metadata=? "
                "WHERE project=?",
                (canonical(actual["after"]["application"]["metadata"]), project),
            )
            hook("create_metadata")
            after = format3.checkpoint(
                store, project, actual["receipt"]["inputSnapshotId"], 1, strict=True
            )
            require(after == actual["receipt"]["afterCheckpointRef"])
            hook("create_after_checkpoint")
            store._db.execute(
                "INSERT INTO app_operations VALUES(?,?,?,?,?,?)",
                actual["rows"]["app_operations"][0],
            )
            hook("create_operation")
            store._db.execute(
                "INSERT INTO app_receipts VALUES(?,?,?)", actual["rows"]["app_receipts"][0]
            )
            hook("create_receipt")
            store._db.execute(
                "UPDATE app_projects SET checkpoint=? WHERE project=?", (after, project)
            )
            hook("create_head")
            require(_actual_rows(store, actual) == actual["rows"])
            counts, total = _totals(store._db)
            require((counts, total) == projected)
            reader._preflight()
            reader._validate()
            store._validate_job3()
            hook("create_validated")
            return actual["result"]
    except CreationFault:
        raise
    except HostReadFault as error:
        raise CreationFault("limit" if error.reason == "limit" else "structure") from None
    except (ValueError, KeyError, TypeError, OverflowError, RecursionError, sqlite3.Error):
        raise CreationFault("structure") from None
