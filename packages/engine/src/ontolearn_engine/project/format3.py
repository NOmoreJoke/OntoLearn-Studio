"""Private Store3 foundation. Used only by Store(target_format=3).

This module extends the same SQLite connection/transaction; it is not a store or
public protocol. Job/application global claims remain the JobStore owner's work.
"""

import hashlib
import json
import os
import sqlite3
from pathlib import Path
from uuid import uuid4

from ontolearn_engine.project.draft_plan import DraftHead
from ontolearn_engine.storage import canonical, digest

APPLICATION_SCHEMA_VERSION = 1
MAX_VERSION = 9007199254740991
COVERAGE = ["metadata", "drafts", "learningCurrent", "assistanceAudit"]


class Format3Fault(ValueError):
    def __init__(self, reason: str, **params):
        messages = {
            "format": "Unsupported future project format",
            "structure": "Invalid project structure",
            "backupRequired": "Migration backup required",
            "backupExists": "Migration backup destination must be new",
            "leaseBusy": "Project writer lease unavailable",
            "sourceChanged": "Migration source changed after backup",
        }
        super().__init__(messages[reason])
        self.category = reason
        self.params = params


TABLES = [
    (
        "app_format",
        "CREATE TABLE app_format(singleton INTEGER PRIMARY KEY CHECK(singleton=1),"
        "schema_version INTEGER NOT NULL CHECK(schema_version=1),schema_hash TEXT NOT NULL,"
        "migration_id TEXT NOT NULL,source_format INTEGER NOT NULL,backup_hash TEXT)",
    ),
    (
        "app_projects",
        "CREATE TABLE app_projects(project TEXT PRIMARY KEY REFERENCES projects(id),"
        "metadata_version INTEGER NOT NULL CHECK(metadata_version>=0),"
        "operation_sequence INTEGER NOT NULL CHECK(operation_sequence>=0),metadata TEXT NOT NULL,"
        "checkpoint TEXT REFERENCES app_checkpoints(id))",
    ),
    (
        "app_drafts",
        "CREATE TABLE app_drafts(project TEXT NOT NULL REFERENCES projects(id),"
        "editor TEXT NOT NULL,"
        "generation INTEGER NOT NULL CHECK(generation>=0),"
        "present INTEGER NOT NULL CHECK(present IN (0,1)),"
        "bound_revision INTEGER NOT NULL CHECK(bound_revision>=0),payload TEXT,content_hash TEXT,"
        "PRIMARY KEY(project,editor),"
        "CHECK((present=0 AND payload IS NULL AND content_hash IS NULL) OR "
        "(present=1 AND payload IS NOT NULL AND content_hash IS NOT NULL)))",
    ),
    (
        "app_learning",
        "CREATE TABLE app_learning(project TEXT NOT NULL REFERENCES projects(id),"
        "attempt TEXT NOT NULL,"
        "record_version INTEGER NOT NULL CHECK(record_version>=0),"
        "course TEXT NOT NULL,task TEXT NOT NULL,"
        "payload TEXT NOT NULL,PRIMARY KEY(project,attempt))",
    ),
    (
        "app_assistance",
        "CREATE TABLE app_assistance(project TEXT NOT NULL,"
        "sequence INTEGER NOT NULL CHECK(sequence>0),"
        "attempt TEXT NOT NULL,event_id TEXT NOT NULL,payload TEXT NOT NULL,"
        "PRIMARY KEY(project,sequence),"
        "UNIQUE(project,event_id),"
        "FOREIGN KEY(project,attempt) REFERENCES app_learning(project,attempt))",
    ),
    (
        "app_operations",
        "CREATE TABLE app_operations(project TEXT NOT NULL REFERENCES projects(id),"
        "sequence INTEGER NOT NULL CHECK(sequence>0),operation TEXT NOT NULL,kind TEXT NOT NULL "
        "CHECK(kind IN ('legacy-domain','domain','application','combined')),"
        "plan_hash TEXT NOT NULL,"
        "domain_revision INTEGER NOT NULL CHECK(domain_revision>=0),"
        "PRIMARY KEY(project,sequence),UNIQUE(project,operation))",
    ),
    (
        "app_checkpoints",
        "CREATE TABLE app_checkpoints(id TEXT PRIMARY KEY,"
        "project TEXT NOT NULL REFERENCES projects(id),"
        "domain_snapshot TEXT NOT NULL REFERENCES snapshots(id),"
        "payload TEXT NOT NULL)",
    ),
    (
        "app_origins",
        "CREATE TABLE app_origins(project TEXT PRIMARY KEY REFERENCES projects(id),"
        "checkpoint TEXT NOT NULL REFERENCES app_checkpoints(id),"
        "domain_revision INTEGER NOT NULL,legacy_operations INTEGER NOT NULL,origin TEXT NOT NULL)",
    ),
    (
        "app_receipts",
        "CREATE TABLE app_receipts(project TEXT NOT NULL,operation TEXT NOT NULL,"
        "payload TEXT NOT NULL,PRIMARY KEY(project,operation),"
        "FOREIGN KEY(project,operation) REFERENCES app_operations(project,operation))",
    ),
]
IMMUTABLE = {
    "app_format",
    "app_assistance",
    "app_operations",
    "app_checkpoints",
    "app_receipts",
    "app_origins",
}
TRIGGERS = [
    (
        f"immutable_{table}_{action}",
        f"CREATE TRIGGER immutable_{table}_{action} BEFORE {action} ON {table} "
        "BEGIN SELECT RAISE(ABORT,'immutable application evidence'); END",
    )
    for table in sorted(IMMUTABLE)
    for action in ("UPDATE", "DELETE")
]
SCHEMA_HASH = digest(TABLES + TRIGGERS)


def acquire_lease(path: Path):
    """Same OS lock inode/protocol as approved JobStore; never unlink it."""
    lease = open(str(path) + ".writer-lock", "a+b")
    try:
        if os.name == "nt":
            import msvcrt

            lease.seek(0)
            if lease.read(1) == b"":
                lease.write(b"0")
                lease.flush()
            lease.seek(0)
            msvcrt.locking(lease.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(lease.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lease.close()
        raise Format3Fault("leaseBusy") from None
    except BaseException:
        lease.close()
        raise
    return lease


def logical_hash(db) -> str:
    return hashlib.sha256("\n".join(db.iterdump()).encode()).hexdigest()


def migration_backup(store, destination: str | Path | None, hook) -> tuple[str, str]:
    if destination is None:
        raise Format3Fault("backupRequired")
    target = Path(destination)
    hook("before_backup")
    try:
        with target.open("xb"):
            pass
    except FileExistsError:
        raise Format3Fault("backupExists") from None
    backup = sqlite3.connect(target)
    try:
        store._db.backup(backup)
        if backup.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise Format3Fault("structure")
        source_hash = logical_hash(backup)
    finally:
        backup.close()
    # Backup must be durable before publishing the migration transaction.
    with target.open("r+b" if os.name == "nt" else "rb") as saved:
        os.fsync(saved.fileno())
    if os.name != "nt":
        directory = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    proof = hashlib.sha256(target.read_bytes()).hexdigest()
    hook("after_backup")
    return proof, source_hash


def metadata(origin: str) -> dict:
    # Unknown historical name/template remain explicit, not guessed from paths.
    return {
        "name": None,
        "templateRef": None,
        "archived": False,
        "mode": "guided",
        "origin": origin,
    }


def application_state(store, project: str) -> dict:
    row = store._db.execute("SELECT * FROM app_projects WHERE project=?", (project,)).fetchone()
    if row is None:
        raise Format3Fault("structure")
    return {
        "metadataVersion": row["metadata_version"],
        "metadata": json.loads(row["metadata"]),
        "drafts": [
            dict(r)
            for r in store._db.execute(
                "SELECT editor,generation,present,bound_revision,payload,content_hash "
                "FROM app_drafts WHERE project=? ORDER BY editor",
                (project,),
            )
        ],
        "learningCurrent": [
            dict(r)
            for r in store._db.execute(
                "SELECT attempt,record_version,course,task,payload FROM app_learning "
                "WHERE project=? ORDER BY attempt",
                (project,),
            )
        ],
        "assistanceAudit": [
            dict(r)
            for r in store._db.execute(
                "SELECT sequence,attempt,event_id,payload FROM app_assistance "
                "WHERE project=? ORDER BY sequence",
                (project,),
            )
        ],
    }


def history_coverage(store, project: str) -> dict:
    revisions = [
        r[0]
        for r in store._db.execute(
            "SELECT domain_revision FROM app_operations WHERE project=? AND kind='legacy-domain' "
            "ORDER BY sequence",
            (project,),
        )
    ]
    origin = store._db.execute(
        "SELECT domain_revision FROM app_origins WHERE project=?", (project,)
    ).fetchone()
    revision = origin[0] if origin else store.revision(project)
    complete = len(revisions) == revision and all(r == i for i, r in enumerate(revisions, 1))
    return {
        "legacyDomainOperations": len(revisions),
        "legacyDomainRevision": revision,
        "legacyHistory": "complete" if complete else "partial",
        "applicationHistory": "from-format3",
    }


def checkpoint(store, project: str, domain_ref: str, sequence: int, *, strict=False) -> str:
    domain = store._project_snapshot(domain_ref, project)
    payload = {
        "checkpointVersion": 1,
        "databaseFormatVersion": 3,
        "applicationStateSchemaVersion": 1,
        "project": project,
        "domainSnapshotRef": domain_ref,
        "domainRevision": domain["projectRevision"],
        "operationSequence": sequence,
        "coverage": COVERAGE,
        "historyCoverage": history_coverage(store, project),
        "application": application_state(store, project),
    }
    identity = digest(payload)
    store._db.execute(
        ("INSERT INTO" if strict else "INSERT OR IGNORE INTO") + " app_checkpoints VALUES(?,?,?,?)",
        (identity, project, domain_ref, canonical(payload)),
    )
    return identity


def seed_project(
    store, project: str, *, origin="created", strict=False, hook=lambda _: None
) -> None:
    sequence = 0
    for marker in store._db.execute(
        "SELECT operation,fingerprint,revision FROM commits WHERE project=? ORDER BY revision",
        (project,),
    ).fetchall():
        sequence += 1
        store._db.execute(
            "INSERT INTO app_operations VALUES(?,?,?,?,?,?)",
            (
                project,
                sequence,
                marker["operation"],
                "legacy-domain",
                marker["fingerprint"],
                marker["revision"],
            ),
        )
    store._db.execute(
        "INSERT INTO app_projects VALUES(?,0,?,?,NULL)",
        (project, sequence, canonical(metadata(origin))),
    )
    if strict:
        hook("create_app_project")
        payload = {
            "project": project,
            "projectRevision": store.revision(project),
            "dependencyVector": store.vector(project),
            "state": store.state(project),
        }
        domain = digest(payload)
        store._db.execute("INSERT INTO snapshots VALUES(?,?)", (domain, canonical(payload)))
        hook("create_domain_snapshot")
    else:
        domain = store.snapshot(project)
    reference = checkpoint(store, project, domain, sequence, strict=strict)
    if strict:
        hook("create_genesis_checkpoint")
    store._db.execute("UPDATE app_projects SET checkpoint=? WHERE project=?", (reference, project))
    if strict:
        hook("create_genesis_head")
    store._db.execute(
        "INSERT INTO app_origins VALUES(?,?,?,?,?)",
        (project, reference, store.revision(project), sequence, origin),
    )
    if strict:
        hook("create_origin")


def install(store, source_format: int, backup_hash: str | None, hook) -> None:
    if not store._has_retirements():
        from ontolearn_engine.storage import RETIREMENTS_SCHEMA

        store._db.execute(RETIREMENTS_SCHEMA.replace("IF NOT EXISTS ", ""))
        hook("format3_domain_retirements")
    for name, sql in TABLES + TRIGGERS:
        store._db.execute(sql)
        hook("format3_ddl:" + name)
    store._db.execute(
        "INSERT INTO app_format VALUES(1,1,?,?,?,?)",
        (SCHEMA_HASH, str(uuid4()), source_format, backup_hash),
    )
    hook("format3_catalog")
    for row in store._db.execute("SELECT id FROM projects ORDER BY id").fetchall():
        seed_project(store, row[0], origin="migration-default")
        hook("format3_project")
    _validate(store, catalog_version=1)
    from ontolearn_engine.project.management_schema import install_fresh

    install_fresh(store, hook)
    validate(store)
    hook("format3_validated")
    store._db.execute("PRAGMA user_version=3")
    hook("format3_version")


def _integer(value, minimum=0) -> bool:
    return type(value) is int and minimum <= value <= MAX_VERSION


def _text(value) -> bool:
    return isinstance(value, str) and bool(value) and value.encode("utf-8") is not None


def _json(value: str):
    parsed = json.loads(value)
    if canonical(parsed) != value:
        raise Format3Fault("structure")
    value.encode("utf-8")
    return parsed


def _require(condition):
    if not condition:
        raise Format3Fault("structure")


def _schema(sql: str) -> str:
    # SQLite adds identifier quotes when renaming current_results during v1->2.
    return " ".join(sql.replace('"', "").replace("IF NOT EXISTS ", "").split())


def _domain_schema(store):
    from ontolearn_engine.storage import SCHEMA

    statements = {
        (
            sql.split()[2]
            if sql.startswith("CREATE TRIGGER")
            else sql.partition("(")[0].split()[-1]
        ): sql
        for sql in SCHEMA
        if not sql.startswith("CREATE TABLE current_results(")
    }
    statements.update(
        {
            "mapping_state": "CREATE TABLE mapping_state(project TEXT REFERENCES projects(id),"
            "owner TEXT,generated_version INTEGER,PRIMARY KEY(project,owner))",
            "commit_evidence": "CREATE TABLE commit_evidence(project TEXT,operation TEXT,"
            "before_snapshot TEXT REFERENCES snapshots(id),"
            "after_snapshot TEXT REFERENCES snapshots(id),"
            "PRIMARY KEY(project,operation),FOREIGN KEY(project,operation) "
            "REFERENCES commits(project,operation))",
            "migration_log": "CREATE TABLE migration_log(version INTEGER PRIMARY KEY)",
            "current_results": "CREATE TABLE current_results(project TEXT REFERENCES projects(id),"
            "kind TEXT,implementation TEXT,result TEXT REFERENCES results(id),"
            "PRIMARY KEY(project,kind,implementation))",
        }
    )
    for action in ("UPDATE", "DELETE"):
        statements[f"immutable_commit_evidence_{action}"] = (
            f"CREATE TRIGGER immutable_commit_evidence_{action} BEFORE {action} "
            "ON commit_evidence BEGIN SELECT RAISE(ABORT,'immutable evidence'); END"
        )
    for name, expected in statements.items():
        row = store._db.execute("SELECT sql FROM sqlite_master WHERE name=?", (name,)).fetchone()
        _require(row is not None and _schema(row[0]) == _schema(expected))
    _require([tuple(r) for r in store._db.execute("SELECT * FROM migration_log")] == [(2,)])


def _application(value: dict, project: str, revision: int) -> None:
    _require(
        isinstance(value, dict)
        and set(value)
        == {"metadataVersion", "metadata", "drafts", "learningCurrent", "assistanceAudit"}
    )
    _require(_integer(value["metadataVersion"]))
    meta = value["metadata"]
    _require(
        isinstance(meta, dict)
        and set(meta) == {"name", "templateRef", "archived", "mode", "origin"}
    )
    _require(meta["name"] is None or _text(meta["name"]))
    _require(meta["templateRef"] is None or _text(meta["templateRef"]))
    _require(meta["mode"] in {"guided", "assisted"} and type(meta["archived"]) is bool)
    _require(meta["origin"] in {"created", "migration-default"})
    _require(
        all(
            isinstance(value[key], list) for key in ("drafts", "learningCurrent", "assistanceAudit")
        )
    )
    editors = []
    for draft in value["drafts"]:
        _require(
            isinstance(draft, dict)
            and set(draft)
            == {"editor", "generation", "present", "bound_revision", "payload", "content_hash"}
        )
        _require(type(draft["present"]) is int and draft["present"] in (0, 1))
        _require(_integer(draft["generation"]) and _integer(draft["bound_revision"]))
        _require(draft["bound_revision"] <= revision)
        validated = DraftHead(
            project,
            draft["editor"],
            draft["generation"],
            bool(draft["present"]),
            draft["bound_revision"],
            draft["payload"],
        )
        _require(validated.content_hash == draft["content_hash"])
        editors.append(draft["editor"])
    _require(editors == sorted(set(editors)))
    attempts = []
    for record in value["learningCurrent"]:
        _require(
            isinstance(record, dict)
            and set(record) == {"attempt", "record_version", "course", "task", "payload"}
        )
        _require(all(_text(record[key]) for key in ("attempt", "course", "task")))
        _require(_integer(record["record_version"]))
        _require(isinstance(_json(record["payload"]), dict))
        attempts.append(record["attempt"])
    _require(attempts == sorted(set(attempts)))
    sequences, events = [], []
    for record in value["assistanceAudit"]:
        _require(
            isinstance(record, dict)
            and set(record) == {"sequence", "attempt", "event_id", "payload"}
        )
        _require(_integer(record["sequence"], 1) and record["attempt"] in attempts)
        _require(_text(record["event_id"]) and isinstance(_json(record["payload"]), dict))
        sequences.append(record["sequence"])
        events.append(record["event_id"])
    _require(all(n == i for i, n in enumerate(sequences, 1)) and len(events) == len(set(events)))


def validate(store, *, catalog_version=2) -> None:
    """Read only: reject incomplete/mutated Store3, never repair on open."""
    try:
        _validate(store, catalog_version=catalog_version)
    except Format3Fault:
        raise
    except (ValueError, KeyError, TypeError, OverflowError, sqlite3.DatabaseError):
        raise Format3Fault("structure") from None


def _validate(store, *, catalog_version=2):
    _domain_schema(store)
    _require(
        store._db.execute(
            "SELECT 1 FROM results WHERE typeof(kind) != 'text' OR trim(kind) = '' "
            "UNION ALL SELECT 1 FROM current_results "
            "WHERE typeof(kind) != 'text' OR trim(kind) = '' LIMIT 1"
        ).fetchone()
        is None
    )
    for snapshot in store._db.execute("SELECT id FROM snapshots"):
        store.load_snapshot(snapshot[0])
    if catalog_version == 2:
        from ontolearn_engine.project.management_schema import catalog, schema_hash

        tables, triggers = catalog()
        expected_hash = schema_hash()
    else:
        tables, triggers, expected_hash = TABLES, TRIGGERS, SCHEMA_HASH
    for name, expected in tables + triggers:
        row = store._db.execute("SELECT sql FROM sqlite_master WHERE name=?", (name,)).fetchone()
        _require(row is not None and _schema(row[0]) == _schema(expected))
    rows = store._db.execute("SELECT * FROM app_format").fetchall()
    _require(
        len(rows) == 1
        and rows[0]["schema_version"] == catalog_version
        and rows[0]["schema_hash"] == expected_hash
    )
    _require(rows[0]["source_format"] in (0, 1, 2) and _text(rows[0]["migration_id"]))
    backup = rows[0]["backup_hash"]
    _require(
        backup is None
        or isinstance(backup, str)
        and len(backup) == 64
        and all(c in "0123456789abcdef" for c in backup)
    )
    _require(store._db.execute("PRAGMA integrity_check").fetchone()[0] == "ok")
    _require(store._db.execute("PRAGMA foreign_key_check").fetchone() is None)
    projects = [r[0] for r in store._db.execute("SELECT id FROM projects ORDER BY id")]
    for table in ("app_projects", "app_origins"):
        _require(
            projects
            == [r[0] for r in store._db.execute(f"SELECT project FROM {table} ORDER BY project")]
        )
    for project in projects:
        _history(store, project)
    if catalog_version == 2:
        from ontolearn_engine.project.management_schema import validate as validate_management

        validate_management(store)


def load_checkpoint(store, project: str, identity: str) -> dict:
    try:
        _, checkpoints, _ = _history(store, project)
        _require(identity in checkpoints)
        return checkpoints[identity]
    except Format3Fault:
        raise
    except (ValueError, KeyError, TypeError, OverflowError, sqlite3.DatabaseError):
        raise Format3Fault("structure") from None


def _cached_snapshot(store, project, snap_ref, cache):
    """Per-call snapshot reuse; never persists across ledger validations."""
    if cache is not None and snap_ref in cache:
        return cache[snap_ref]
    domain = store._project_snapshot(snap_ref, project)
    if cache is not None:
        cache[snap_ref] = domain
    return domain


def _raw_checkpoint(store, project, identity, *, _snapshots=None):
    """Structural read only. Authority is established by _history, never by this alone."""
    row = store._db.execute(
        "SELECT * FROM app_checkpoints WHERE id=? AND project=?", (identity, project)
    ).fetchone()
    _require(row is not None)
    value = _json(row["payload"])
    _require(
        isinstance(value, dict)
        and set(value)
        == {
            "checkpointVersion",
            "databaseFormatVersion",
            "applicationStateSchemaVersion",
            "project",
            "domainSnapshotRef",
            "domainRevision",
            "operationSequence",
            "coverage",
            "historyCoverage",
            "application",
        }
    )
    _require(
        digest(value) == identity
        and value["project"] == project
        and value["coverage"] == COVERAGE
        and value["historyCoverage"] == history_coverage(store, project)
    )
    versions = (
        value["checkpointVersion"],
        value["databaseFormatVersion"],
        value["applicationStateSchemaVersion"],
    )
    if any(type(v) is not int for v in versions) or versions != (1, 3, 1):
        raise Format3Fault("format")
    _require(_integer(value["domainRevision"]) and _integer(value["operationSequence"]))
    _require(row["domain_snapshot"] == value["domainSnapshotRef"])
    domain = _cached_snapshot(store, project, value["domainSnapshotRef"], _snapshots)
    _require(domain["projectRevision"] == value["domainRevision"])
    _application(value["application"], project, value["domainRevision"])
    return value


def _history(store, project):
    """Verify one immutable mixed ledger from genesis through the actual current head."""
    snapshots: dict[str, dict] = {}
    revision = store.revision(project)
    _require(_text(project) and _integer(revision))
    store._snapshot_state(store.state(project))
    head = store._db.execute("SELECT * FROM app_projects WHERE project=?", (project,)).fetchone()
    origin = store._db.execute("SELECT * FROM app_origins WHERE project=?", (project,)).fetchone()
    _require(head is not None and origin is not None)
    _require(_integer(head["metadata_version"]) and _integer(head["operation_sequence"]))
    _require(
        origin["origin"] in {"created", "migration-default"}
        and _integer(origin["domain_revision"])
        and _integer(origin["legacy_operations"])
    )
    operations = [
        dict(r)
        for r in store._db.execute(
            "SELECT * FROM app_operations WHERE project=? ORDER BY sequence", (project,)
        )
    ]
    _require(
        all(
            _integer(op["sequence"], 1) and op["sequence"] == i
            for i, op in enumerate(operations, 1)
        )
    )
    _require(head["operation_sequence"] == len(operations))
    legacy = history_coverage(store, project)["legacyDomainOperations"]
    _require(legacy == origin["legacy_operations"] and legacy <= len(operations))
    _require(all(op["kind"] == "legacy-domain" for op in operations[:legacy]))
    old_revisions, domain_operations = [], set()
    for op in operations[:legacy]:
        marker = store.marker(project, op["operation"])
        _require(marker is not None and _integer(marker["revision"], 1) and _text(marker["job"]))
        _require(
            op["domain_revision"] == marker["revision"]
            and op["plan_hash"] == marker["fingerprint"] == digest(_json(marker["plan"]))
        )
        old_revisions.append(marker["revision"])
        domain_operations.add(op["operation"])
    _require(
        old_revisions == sorted(set(old_revisions))
        and all(r <= origin["domain_revision"] for r in old_revisions)
    )
    genesis = _raw_checkpoint(store, project, origin["checkpoint"], _snapshots=snapshots)
    _require(
        genesis["operationSequence"] == legacy
        and genesis["domainRevision"] == origin["domain_revision"]
    )
    _require(
        genesis["application"]
        == {
            "metadataVersion": 0,
            "metadata": metadata(origin["origin"]),
            "drafts": [],
            "learningCurrent": [],
            "assistanceAudit": [],
        }
    )
    checkpoints = {origin["checkpoint"]: genesis}
    receipts = {}
    current_ref, current = origin["checkpoint"], genesis
    for op in operations[legacy:]:
        _require(op["kind"] in {"domain", "application", "combined"})
        raw = store._db.execute(
            "SELECT payload FROM app_receipts WHERE project=? AND operation=?",
            (project, op["operation"]),
        ).fetchone()
        _require(raw is not None)
        proof = _json(raw[0])
        _require(isinstance(proof, dict) and proof.get("beforeCheckpointRef") == current_ref)
        after_ref = proof.get("afterCheckpointRef")
        _require(_text(after_ref))
        after = _raw_checkpoint(store, project, after_ref, _snapshots=snapshots)
        _require(
            after["operationSequence"] == op["sequence"]
            and current["operationSequence"] == op["sequence"] - 1
        )
        _require(op["domain_revision"] == after["domainRevision"])
        marker = store.marker(project, op["operation"])
        creation = None
        if op["kind"] in {"application", "combined"}:
            from ontolearn_engine.project.project_lifecycle import creation_context

            creation = creation_context(store, project, op["operation"])
        if creation is not None:
            from ontolearn_engine.project.project_lifecycle import validate_transition

            expected = validate_transition(store, project, op, origin, current, after)
        elif op["kind"] == "domain":
            _require(marker is not None and _text(marker["job"]))
            _require(op["plan_hash"] == marker["fingerprint"] == digest(_json(marker["plan"])))
            expected = _domain_receipt(project, marker, op["sequence"], current_ref, after_ref)
            _require(current["application"] == after["application"])
        else:
            from ontolearn_engine.project.applications import (
                claim_context,
                validate_plan,
            )
            from ontolearn_engine.project.applications import (
                receipt as app_receipt,
            )

            context = claim_context(store, project, op["operation"])
            plan = context["plan"]
            _require(op["plan_hash"] == digest(plan))
            _require(canonical(plan["before"]) == canonical(current["application"]))
            _require(canonical(plan["after"]) == canonical(after["application"]))
            change = plan["change"]
            target = None
            if change["type"] in {"draft.restore", "project.restore"}:
                # Authority comes from the verified ledger itself: cross-project,
                # future or forged checkpoint refs never enter this map.
                _require(change["checkpointRef"] in checkpoints)
                target = checkpoints[change["checkpointRef"]]
                if change["type"] == "project.restore":
                    _require(change["checkpointRef"] != current_ref)
                    _require(
                        (plan["domain"] is not None)
                        == (target["domainSnapshotRef"] != current["domainSnapshotRef"])
                    )
            validate_plan(store, project, plan, current["domainRevision"], target)
            _require((plan["domain"] is not None) == (op["kind"] == "combined"))
            expected = app_receipt(
                project,
                op["operation"],
                op["kind"],
                op["sequence"],
                plan,
                current_ref,
                after_ref,
                current["domainRevision"],
                after["domainRevision"],
            )
            if op["kind"] == "application":
                _require(
                    marker is None
                    and current["domainSnapshotRef"] == after["domainSnapshotRef"]
                    and current["domainRevision"] == after["domainRevision"]
                )
            else:
                domain = plan["domain"]
                _require(marker is not None and marker["job"] is None)
                _require(
                    marker["fingerprint"] == domain["fingerprint"] == digest(_json(marker["plan"]))
                )
                before_snap = _cached_snapshot(store, project, marker["before_snapshot"], snapshots)
                after_snap = _cached_snapshot(store, project, marker["after_snapshot"], snapshots)
                _require(
                    before_snap["state"] == domain["beforeState"]
                    and after_snap["state"] == domain["afterState"]
                )
        if op["kind"] in {"domain", "combined"}:
            _require(marker["revision"] == after["domainRevision"] == current["domainRevision"] + 1)
            _require(
                marker["before_snapshot"] == current["domainSnapshotRef"]
                and marker["after_snapshot"] == after["domainSnapshotRef"]
            )
            domain_operations.add(op["operation"])
        _require(canonical(proof) == canonical(expected))
        receipts[op["operation"]] = proof
        checkpoints[after_ref] = after
        current_ref, current = after_ref, after
    _require(
        {
            r[0]
            for r in store._db.execute("SELECT operation FROM commits WHERE project=?", (project,))
        }
        == domain_operations
    )
    _require(
        store._db.execute(
            "SELECT count(*) FROM app_receipts WHERE project=?", (project,)
        ).fetchone()[0]
        == len(receipts)
    )
    _require(
        {
            r[0]
            for r in store._db.execute("SELECT id FROM app_checkpoints WHERE project=?", (project,))
        }
        == set(checkpoints)
    )
    _require(head["checkpoint"] == current_ref and current["domainRevision"] == revision)
    _require(canonical(application_state(store, project)) == canonical(current["application"]))
    _require(
        current["domainSnapshotRef"]
        == digest(
            {
                "project": project,
                "projectRevision": revision,
                "dependencyVector": store.vector(project),
                "state": store.state(project),
            }
        )
    )
    return receipts, checkpoints, current


def receipts_for_project(store, project: str) -> dict:
    """Validate project history once and return its operation receipts map."""
    try:
        receipts, _, _ = _history(store, project)
        return receipts
    except Format3Fault:
        raise
    except (ValueError, KeyError, TypeError, OverflowError, sqlite3.DatabaseError):
        raise Format3Fault("structure") from None


def receipt_for(store, project: str, operation: str) -> dict:
    receipts = receipts_for_project(store, project)
    _require(operation in receipts)
    return receipts[operation]


def _domain_receipt(project, marker, sequence, before, after):
    return {
        "receiptVersion": 1,
        "project": project,
        "operationId": marker["operation"],
        "operationKind": "domain",
        "operationSequence": sequence,
        "planHash": marker["fingerprint"],
        "domainBeforeRevision": marker["revision"] - 1,
        "domainAfterRevision": marker["revision"],
        "domainMarkerRef": marker["operation"],
        "applicationBeforeCAS": [],
        "applicationAfterCAS": [],
        "beforeCheckpointRef": before,
        "afterCheckpointRef": after,
        "committed": True,
    }


def record_domain_commit(store, project: str, marker: dict, hook) -> None:
    head = store._db.execute("SELECT * FROM app_projects WHERE project=?", (project,)).fetchone()
    if head is None or head["operation_sequence"] >= MAX_VERSION:
        raise Format3Fault("structure")
    sequence = head["operation_sequence"] + 1
    before = checkpoint(store, project, marker["before_snapshot"], sequence - 1)
    store._db.execute(
        "INSERT INTO app_operations VALUES(?,?,?,?,?,?)",
        (
            project,
            sequence,
            marker["operation"],
            "domain",
            marker["fingerprint"],
            marker["revision"],
        ),
    )
    store._db.execute(
        "UPDATE app_projects SET operation_sequence=? WHERE project=?", (sequence, project)
    )
    hook("format3_sequence")
    after = checkpoint(store, project, marker["after_snapshot"], sequence)
    hook("format3_checkpoint")
    receipt = _domain_receipt(project, marker, sequence, before, after)
    store._db.execute(
        "INSERT INTO app_receipts VALUES(?,?,?)", (project, marker["operation"], canonical(receipt))
    )
    store._db.execute("UPDATE app_projects SET checkpoint=? WHERE project=?", (after, project))
    hook("format3_receipt")
