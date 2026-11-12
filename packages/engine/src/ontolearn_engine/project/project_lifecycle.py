"""Internal blank/named-create mechanics, not an authorized host service.

Only Store.commit delegates here. Origin is persisted input, never permission or
physical dispatch proof. No path, connection factory, public capability, scope
factory, resolution, or replay across a host boundary is provided.
"""

import hashlib
import json
import sqlite3
from dataclasses import dataclass
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
    if isinstance(context, dict) and "copyCreateContextVersion" in context:
        from ontolearn_engine.project.management import copy_context

        return copy_context(store, project, operation)
    if isinstance(context, dict) and "exampleCreateContextVersion" in context:
        return example_context(store, project, operation)
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
    if (
        "exampleCreateContextVersion" in expected["context"]
        or "copyCreateContextVersion" in expected["context"]
    ):
        require(op["kind"] == "combined" and op["sequence"] == 1 and op["domain_revision"] == 1)
        require(op["plan_hash"] == expected["receipt"]["planHash"])
        require(tuple(origin) == (project, digest(expected["before"]), 0, 0, "created"))
        require(canonical(before) == canonical(expected["before"]))
        require(canonical(after) == canonical(expected["after"]))
        require(store.marker(project, op["operation"]) == expected["marker"])
        return expected["receipt"]
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
        total
        * (1 + counts.get("app_operations", 0) + counts.get("snapshots", 0))
        * (1 + counts.get("management_receipts", 0))
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
        "domainRevision": candidate["after"]["domainRevision"],
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
            "commits": ("project", "operation"),
            "commit_evidence": ("project", "operation"),
            "versions": ("project", "key"),
            "definitions": ("project", "layer", "id"),
            "facts": ("project", "id"),
        }.get(table)
        for row in rows:
            if keys:
                sql = f"SELECT * FROM {table} WHERE " + " AND ".join(f"{key}=?" for key in keys)
                found = store._db.execute(sql, row[: len(keys)]).fetchone()
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


# Named, fixed T09 resource adapter. Neither this value nor a caller dictionary
# grants write authority. Store.commit owns admission and the enclosing transaction.
EXAMPLE_ID = "equipment-maintenance"
EXAMPLE_VERSION = "prd-v0.6-learning-1.fr003-input-1"
EXAMPLE_INPUT_BYTES = 10930
EXAMPLE_INPUT_SHA256 = "52952b637b02ba283d47a9e0c34a1691c1d850b94bb9b366a9863a55507c435e"
EXAMPLE_QUERY_SHA256 = "8efbacd589c42ac40abbb55475cdd088e407a88a23e0db61dc8375e04e4dd386"


@dataclass(frozen=True)
class ExamplePlan:
    """Immutable prepared input; parsed projections are fresh, never authority.

    Reference materials are retained separately from executable domain definitions.
    In particular they are not inferred facts, current results or mapping ownership.
    """

    request_json: str
    definitions_json: str
    manual_json: str
    reference_materials_json: str
    input_digest: str
    resource_utf8: str
    plan_digest: str

    def domain_plan(self):
        return {
            "definitions": json.loads(self.definitions_json),
            "manual": json.loads(self.manual_json),
        }


def example_request_value(value):
    """Separate internal request: never extends the blank four-field contract.

    Reset is another explicitly requested operation creating a new project; there
    is deliberately no target project or overwrite flag in this adapter.
    """
    require(
        type(value) is dict
        and set(value)
        == {"exampleCreateRequestVersion", "operationId", "name", "exampleId", "inputDigest"},
        "input",
    )
    require(
        type(value["exampleCreateRequestVersion"]) is int
        and value["exampleCreateRequestVersion"] == 1,
        "input",
    )
    blank = request_value(
        {
            "requestVersion": 1,
            "operationId": value["operationId"],
            "name": value["name"],
            "initialization": {"kind": "blank"},
        }
    )
    require(
        type(value["exampleId"]) is str
        and value["exampleId"] == EXAMPLE_ID
        and type(value["inputDigest"]) is str
        and value["inputDigest"] == EXAMPLE_INPUT_SHA256,
        "input",
    )
    return {**json.loads(encoded(value, 16384)), "name": blank["name"]}


def example_plan(resource, request):
    """Strict supported mapping of one pinned resource, without I/O or SQL.

    No caller supplied path, Turtle parser, arbitrary project input or expectations
    enter the write plan. Check raw identity before parsing. The fixed source hash
    binds all fields, including the complete reference-only material.
    """
    request = example_request_value(request)
    require(type(resource) is bytes and len(resource) == EXAMPLE_INPUT_BYTES, "input")
    require(hashlib.sha256(resource).hexdigest() == EXAMPLE_INPUT_SHA256, "identity")
    try:
        value = json.loads(resource.decode("utf-8"))
    except (UnicodeError, ValueError, RecursionError):
        raise CreationFault("input") from None
    require(
        type(value) is dict
        and set(value)
        == {
            "schema",
            "contractKind",
            "status",
            "exampleId",
            "exampleVersion",
            "baseline",
            "sourceHead",
            "sourceBinding",
            "versions",
            "ontology",
            "assertedFacts",
            "singleValuedPredicates",
            "queries",
            "domainMaterials",
            "currentInferredFacts",
            "currentResults",
            "loadSemantics",
        },
        "input",
    )
    require(
        value["schema"] == "t09.fr003.load-input/v1"
        and value["exampleId"] == EXAMPLE_ID
        and value["exampleVersion"] == EXAMPLE_VERSION
        and value["baseline"] == "G-base"
        and value["currentInferredFacts"] == []
        and value["currentResults"] == [],
        "input",
    )
    ontology, facts, queries = value["ontology"], value["assertedFacts"], value["queries"]
    require(type(ontology) is list and len(ontology) == 10, "input")
    require(type(facts) is list and len(facts) == 18, "input")
    require(type(queries) is list and len(queries) == 1, "input")
    from ontolearn_engine.storage import Store

    definitions, manual = [], []
    for index, triple in enumerate(ontology):
        require(type(triple) is dict and set(triple) == {"subject", "predicate", "object"}, "input")
        definition = {"triples": [triple]}
        if index == 0:
            # Store's existing declaration has project-wide union semantics.
            definition["singleValuedPredicates"] = value["singleValuedPredicates"]
        Store._definition(definition)
        # Definition keys are opaque public names; the RDF subject remains in
        # the unchanged triple. An IRI key cannot cross the strict vector DTO.
        definitions.append(
            {"layer": "ontology", "id": f"equipment-maintenance-{index:02d}", "value": definition}
        )
    require(len({item["id"] for item in definitions}) == 10, "input")
    for triple in facts:
        require(type(triple) is dict and set(triple) == {"subject", "predicate", "object"}, "input")
        fact = {"id": digest([triple["subject"], triple["predicate"], triple["object"]]), **triple}
        Store._fact(fact)
        manual.append(fact)
    require(len({item["id"] for item in manual}) == 18, "input")
    query = queries[0]
    require(
        type(query) is dict
        and set(query) == {"id", "scope", "text", "source"}
        and query["id"] == "unclosed-high"
        and query["scope"] == "current-asserted"
        and type(query["text"]) is str
        and len(query["text"].encode("utf-8")) == 162
        and hashlib.sha256(query["text"].encode("utf-8")).hexdigest() == EXAMPLE_QUERY_SHA256,
        "input",
    )
    definitions.append(
        {
            "layer": "query",
            "id": "unclosed-high",
            # The immutable resource/context retains all 162 source bytes and
            # their SHA. Only the executable definition trims the source's final
            # newline, as required by the canonical saved-query contract.
            "value": {
                "text": query["text"].removesuffix("\n"),
                "references": [],
                "descriptor": {
                    "version": 1,
                    "name": "未关闭的高等级告警",
                    "description": "设备运维示例查询",
                    "scope": "asserted",
                    "capabilityQuestion": "哪些高等级告警尚未关闭？",
                    "source": "template",
                },
            },
        }
    )
    references = {
        key: value[key]
        for key in ("sourceHead", "sourceBinding", "versions", "domainMaterials", "loadSemantics")
    }
    plan = {
        "examplePlanVersion": 1,
        "exampleId": EXAMPLE_ID,
        "exampleVersion": EXAMPLE_VERSION,
        "inputDigest": EXAMPLE_INPUT_SHA256,
        "request": request,
        "definitions": definitions,
        "manual": manual,
        "referenceMaterials": references,
    }
    # The encoded representation is immutable and bounded by the pinned resource.
    encoded(plan, 65536)
    return ExamplePlan(
        canonical(request),
        canonical(definitions),
        canonical(manual),
        canonical(references),
        EXAMPLE_INPUT_SHA256,
        resource.decode("utf-8"),
        digest(plan),
    )


def example_model(project, request, origin, library, prepared, *, actual_genesis=None):
    """Predict all named creation rows; existing effects are proved separately.

    The sole domain marker has exactly the old Store canonical plan shape. No
    inferred/result/history/mapping-execution rows are invented from references.
    """
    request = example_request_value(request)
    require(type(prepared) is ExamplePlan and prepared.request_json == canonical(request), "input")
    domain_plan = prepared.domain_plan()
    blank_request = {
        "requestVersion": 1,
        "operationId": request["operationId"],
        "initialization": {"kind": "blank"},
        "name": request["name"],
    }
    blank = model(project, blank_request, origin, library, actual_genesis=actual_genesis)
    before = blank["before"]
    definitions = sorted(domain_plan["definitions"], key=lambda item: (item["layer"], item["id"]))
    facts = sorted(domain_plan["manual"], key=lambda item: item["id"])
    vector = {f"{item['layer']}:{item['id']}": 1 for item in definitions}
    vector["facts:asserted"] = 1
    domain = {
        "project": project,
        "projectRevision": 1,
        "dependencyVector": vector,
        "state": {
            "mappingState": {},
            "definitions": [
                {"layer": item["layer"], "id": item["id"], "payload": canonical(item["value"])}
                for item in definitions
            ],
            "facts": [
                {**item, "owner": None, "source_row": None, "managed_value": None} for item in facts
            ],
        },
    }
    after = json.loads(canonical(blank["after"]))
    after["application"]["metadata"]["templateRef"] = EXAMPLE_ID + "@" + EXAMPLE_INPUT_SHA256
    after["domainRevision"] = 1
    after["domainSnapshotRef"] = digest(domain)
    marker_plan = {
        "base": 0,
        "definitions": domain_plan["definitions"],
        "manual": domain_plan["manual"],
        "edits": None,
        "remove": None,
        "mapping": None,
    }
    plan = {
        "exampleCreatePlanVersion": 1,
        "exampleId": EXAMPLE_ID,
        "inputDigest": prepared.input_digest,
        "preparedPlanHash": prepared.plan_digest,
        "projectId": project,
        "initialMetadata": after["application"]["metadata"],
        "domainPlan": marker_plan,
        "beforeCheckpointRef": digest(before),
        "afterCheckpointRef": digest(after),
    }
    # Original pinned bytes are persisted for independent reopen verification;
    # reopening never needs a mutable filesystem resource or candidate assertion.
    context = {
        "exampleCreateContextVersion": 1,
        "exampleId": EXAMPLE_ID,
        "inputDigest": prepared.input_digest,
        "libraryEvidenceRef": library,
        "projectId": project,
        "project": project,
        "operationId": request["operationId"],
        "request": request,
        "requestHash": digest(request),
        "origin": origin,
        "resourceUtf8": prepared.resource_utf8,
        "plan": plan,
    }
    proof = {
        "exampleCreateReceiptVersion": 1,
        "exampleId": EXAMPLE_ID,
        "inputDigest": prepared.input_digest,
        "libraryEvidenceRef": library,
        "projectId": project,
        "operationId": request["operationId"],
        "requestHash": digest(request),
        "contextHash": digest(context),
        "planHash": digest(plan),
        "operationSequence": 1,
        "domainRevision": 1,
        "metadataVersion": 1,
        "inputSnapshotId": digest(domain),
        "beforeCheckpointRef": digest(before),
        "afterCheckpointRef": digest(after),
    }
    result = {
        "createResultVersion": 1,
        "operationId": request["operationId"],
        "projectId": project,
        "requestHash": digest(request),
        "receipt": proof,
    }
    operation = request["operationId"]
    marker = {
        "project": project,
        "operation": operation,
        "job": None,
        "revision": 1,
        "fingerprint": digest(marker_plan),
        "plan": canonical(marker_plan),
        "before_snapshot": before["domainSnapshotRef"],
        "after_snapshot": digest(domain),
    }
    rows = {
        "projects": [(project, 1)],
        "snapshots": [
            (before["domainSnapshotRef"], canonical(blank["domain"])),
            (digest(domain), canonical(domain)),
        ],
        "app_projects": [
            (project, 1, 1, canonical(after["application"]["metadata"]), digest(after))
        ],
        "app_checkpoints": [
            (digest(before), project, before["domainSnapshotRef"], canonical(before)),
            (digest(after), project, digest(domain), canonical(after)),
        ],
        "app_origins": [(project, digest(before), 0, 0, "created")],
        "public_projects": [(project, project)],
        "operation_claims": [
            (operation, project, None, digest(context), "application", canonical(context))
        ],
        "app_operations": [(project, 1, operation, "combined", digest(plan), 1)],
        "app_receipts": [(project, operation, canonical(proof))],
        "definitions": [
            (project, item["layer"], item["id"], canonical(item["value"])) for item in definitions
        ],
        "facts": [
            (
                project,
                item["id"],
                item["subject"],
                item["predicate"],
                item["object"],
                None,
                None,
                None,
            )
            for item in facts
        ],
        "versions": [(project, key, value) for key, value in sorted(vector.items())],
        "commits": [(project, operation, None, 1, digest(marker_plan), canonical(marker_plan))],
        "commit_evidence": [(project, operation, before["domainSnapshotRef"], digest(domain))],
    }
    return {
        "domain": domain,
        "before": before,
        "after": after,
        "context": context,
        "receipt": proof,
        "result": result,
        "rows": rows,
        "marker": marker,
    }


def example_context(store, project, operation):
    """Authenticate the named immutable receipt closure without recursive history.

    Current mutable definitions/facts may have advanced after creation. The
    original immutable snapshots and marker, never current state, prove adoption.
    """
    row = store._db.execute(
        "SELECT * FROM operation_claims WHERE operation=?", (operation,)
    ).fetchone()
    if row is None or row["kind"] != "application":
        return None
    context = format3._json(row["context"])
    if not isinstance(context, dict) or "exampleCreateContextVersion" not in context:
        return None
    require(
        set(context)
        == {
            "exampleCreateContextVersion",
            "exampleId",
            "inputDigest",
            "libraryEvidenceRef",
            "projectId",
            "project",
            "operationId",
            "request",
            "requestHash",
            "origin",
            "resourceUtf8",
            "plan",
        }
        and type(context["exampleCreateContextVersion"]) is int
        and context["exampleCreateContextVersion"] == 1
    )
    require(row["job"] is None and row["project"] == project and uuid_ref(project))
    request = example_request_value(context["request"])
    require(request["operationId"] == operation and type(context["resourceUtf8"]) is str)
    try:
        resource = context["resourceUtf8"].encode("utf-8")
    except UnicodeError:
        raise CreationFault("structure") from None
    prepared = example_plan(resource, request)
    expected = example_model(
        project, request, origin_value(context["origin"]), library_evidence(store), prepared
    )
    require(canonical(context) == canonical(expected["context"]))
    require(row["fingerprint"] == digest(context))
    mapping = store._db.execute(
        "SELECT internal FROM public_projects WHERE public=?", (project,)
    ).fetchone()
    require(mapping is not None and mapping[0] == project)
    for table, predicate, params in (
        ("app_origins", "project=?", (project,)),
        ("app_operations", "project=? AND operation=?", (project, operation)),
        ("app_receipts", "project=? AND operation=?", (project, operation)),
        ("commits", "project=? AND operation=?", (project, operation)),
        ("commit_evidence", "project=? AND operation=?", (project, operation)),
    ):
        actual = store._db.execute(f"SELECT * FROM {table} WHERE {predicate}", params).fetchall()
        require([tuple(item) for item in actual] == expected["rows"][table])
    for table in ("snapshots", "app_checkpoints"):
        for expected_row in expected["rows"][table]:
            actual = store._db.execute(
                f"SELECT * FROM {table} WHERE id=?", (expected_row[0],)
            ).fetchone()
            require(actual is not None and tuple(actual) == expected_row)
    return expected


def commit_example(store, project, base, operation, job, supplied, hook):
    """Sole Store.commit named branch: one atomic independent user project.

    The existing blank entry and its no-external-transaction gate remain intact.
    Origin is identity input, not permission. The mainline caller must hold its
    actual library.create authority before dispatching this private method.
    """
    from ontolearn_engine.job_store import JobStore

    require(isinstance(store, JobStore) and store._target_format == 3, "state")
    require(not store._db.in_transaction, "state")
    require(project is None and base is None and job is None, "input")
    require(
        type(supplied) is dict
        and set(supplied)
        == {"exampleCreateCoreVersion", "request", "origin", "readerLimits", "resource"}
        and type(supplied["exampleCreateCoreVersion"]) is int
        and supplied["exampleCreateCoreVersion"] == 1,
        "input",
    )
    require(type(supplied["readerLimits"]) is ReadLimits, "input")
    limits = supplied["readerLimits"]
    request, origin = example_request_value(supplied["request"]), origin_value(supplied["origin"])
    require(request["operationId"] == operation, "identity")
    prepared = example_plan(supplied["resource"], request)
    try:
        with store._transaction(hook):
            require(store._db.execute("PRAGMA user_version").fetchone()[0] == 3, "state")
            reader = ProjectHostReader(store)
            reader._preflight()
            reader._validate()
            store._validate_job3()
            claim = store._db.execute(
                "SELECT * FROM operation_claims WHERE operation=?", (operation,)
            ).fetchone()
            if claim is not None:
                require(claim["kind"] == "application", "identity")
                old = example_context(store, claim["project"], operation)
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
            candidate = example_model(project, request, origin, library_evidence(store), prepared)
            for table in ("snapshots", "app_checkpoints"):
                require(
                    all(
                        store._db.execute(f"SELECT 1 FROM {table} WHERE id=?", (row[0],)).fetchone()
                        is None
                        for row in candidate["rows"][table]
                    ),
                    "identity",
                )
            projected = preflight(store, candidate, limits)
            hook("example_preflight")
            store._db.execute("INSERT INTO projects VALUES(?,0)", (project,))
            hook("example_project")
            format3.seed_project(store, project, strict=True, hook=hook)
            genesis = store.project_checkpoint(project)
            require(genesis == candidate["before"])
            hook("example_genesis_verified")
            store._db.execute("INSERT INTO public_projects VALUES(?,?)", (project, project))
            actual = example_model(
                project, request, origin, library_evidence(store), prepared, actual_genesis=genesis
            )
            require(actual == candidate)
            store._db.execute(
                "INSERT INTO operation_claims VALUES(?,?,?,?,?,?)",
                actual["rows"]["operation_claims"][0],
            )
            hook("example_claim")
            for table in ("definitions", "facts", "versions"):
                for row in actual["rows"][table]:
                    marks = ",".join("?" for _ in row)
                    store._db.execute(f"INSERT INTO {table} VALUES({marks})", row)
                    hook("example_" + table)
            store._validate_references(project)
            store._validate_single_slots(project)
            store._db.execute("UPDATE projects SET revision=1 WHERE id=?", (project,))
            require(store.state(project) == actual["domain"]["state"])
            require(store.vector(project) == actual["domain"]["dependencyVector"])
            store._db.execute("INSERT INTO snapshots VALUES(?,?)", actual["rows"]["snapshots"][1])
            store._db.execute(
                "INSERT INTO commits VALUES(?,?,?,?,?,?)", actual["rows"]["commits"][0]
            )
            store._db.execute(
                "INSERT INTO commit_evidence VALUES(?,?,?,?)", actual["rows"]["commit_evidence"][0]
            )
            hook("example_domain_marker")
            store._db.execute(
                "UPDATE app_projects SET metadata_version=1,operation_sequence=1,metadata=? "
                "WHERE project=?",
                (canonical(actual["after"]["application"]["metadata"]), project),
            )
            after = format3.checkpoint(
                store, project, actual["receipt"]["inputSnapshotId"], 1, strict=True
            )
            require(after == actual["receipt"]["afterCheckpointRef"])
            hook("example_checkpoint")
            store._db.execute(
                "INSERT INTO app_operations VALUES(?,?,?,?,?,?)",
                actual["rows"]["app_operations"][0],
            )
            store._db.execute(
                "INSERT INTO app_receipts VALUES(?,?,?)", actual["rows"]["app_receipts"][0]
            )
            store._db.execute(
                "UPDATE app_projects SET checkpoint=? WHERE project=?", (after, project)
            )
            hook("example_receipt")
            require(_actual_rows(store, actual) == actual["rows"])
            require(_totals(store._db) == projected)
            reader._preflight()
            reader._validate()
            store._validate_job3()
            hook("example_validated")
            return actual["result"]
    except CreationFault:
        raise
    except HostReadFault as error:
        raise CreationFault("limit" if error.reason == "limit" else "structure") from None
    except (ValueError, KeyError, TypeError, OverflowError, RecursionError, sqlite3.Error):
        raise CreationFault("structure") from None
