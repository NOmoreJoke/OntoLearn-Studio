"""S1 storage spike, deliberately not a mapping/behavior execution service.

One SQLite transaction owns all mutable truth. Graphs are disposable read models.
Callers supply already validated domain plans; this layer validates storage shape,
ownership, base revision and references, not the full Appendix C semantics.
"""

import hashlib
import json
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from ontolearn_engine.invalidation import CODES, RULES, can_publish_current, family, reasons
from ontolearn_engine.rdf_snapshot import iri, term

FORMAT_VERSION = 2
LAYERS = {"ontology", "mapping", "constraint", "rule", "behavior", "scenario", "query", "model"}
Hook = Callable[[str], None]


def canonical(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class Conflict(ValueError):
    """A plan must be previewed again or its ownership conflict resolved."""


class Store:
    def __init__(self, path: str | Path, migration_hook: Hook = lambda _: None):
        self.path = Path(path)
        self._db = sqlite3.connect(self.path, isolation_level=None, timeout=5)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.execute("PRAGMA synchronous=FULL")
        try:
            self._migrate(migration_hook)
        except BaseException:
            self._db.close()
            raise

    def close(self) -> None:
        self._db.close()

    @contextmanager
    def _transaction(self, hook: Hook = lambda _: None) -> Iterator[None]:
        hook("before")
        self._db.execute("BEGIN IMMEDIATE")
        try:
            yield
            hook("before_commit")
            self._db.execute("COMMIT")
        except BaseException:
            if self._db.in_transaction:
                self._db.execute("ROLLBACK")
            raise
        # If delivery/cancellation fails here, the persistent marker is authoritative.
        hook("after_commit")

    def _migrate(self, hook: Hook) -> None:
        version = self._db.execute("PRAGMA user_version").fetchone()[0]
        if version > FORMAT_VERSION:
            raise ValueError("Unsupported future project format")
        if version == FORMAT_VERSION:
            return  # Opening a current format must not take a writer lock.
        # Re-read under the lock: another opener may have migrated while we waited.
        with self._transaction(hook):
            version = self._db.execute("PRAGMA user_version").fetchone()[0]
            if version > FORMAT_VERSION:
                raise ValueError("Unsupported future project format")
            if version == FORMAT_VERSION:
                return
            if version not in {0, 1}:
                raise ValueError("Unsupported project format")
            if version == 0:
                for statement in SCHEMA:
                    self._db.execute(statement)
                self._db.execute("PRAGMA user_version=1")
                hook("v1_created")
            if version < 2:
                self._db.execute(
                    "CREATE TABLE mapping_state(project TEXT REFERENCES projects(id),owner TEXT,"
                    "generated_version INTEGER,PRIMARY KEY(project,owner))"
                )
                hook("mapping_state_created")
                self._db.execute(
                    "INSERT INTO mapping_state SELECT DISTINCT project,owner,-1 "
                    "FROM facts WHERE owner IS NOT NULL"
                )
                hook("mapping_state_backfilled")
                self._db.execute(
                    "CREATE TABLE commit_evidence(project TEXT,operation TEXT,"
                    "before_snapshot TEXT REFERENCES snapshots(id),"
                    "after_snapshot TEXT REFERENCES snapshots(id),PRIMARY KEY(project,operation),"
                    "FOREIGN KEY(project,operation) REFERENCES commits(project,operation))"
                )
                hook("commit_evidence_created")
                for action in ("UPDATE", "DELETE"):
                    self._db.execute(
                        f"CREATE TRIGGER immutable_commit_evidence_{action} BEFORE {action} "
                        "ON commit_evidence BEGIN SELECT RAISE(ABORT,'immutable evidence'); END"
                    )
                hook("immutable_triggers_created")
                self._db.execute("CREATE TABLE migration_log(version INTEGER PRIMARY KEY)")
                self._db.execute("INSERT INTO migration_log VALUES(2)")
                self._db.execute(
                    "CREATE TABLE current_results_v2(project TEXT REFERENCES projects(id),"
                    "kind TEXT,"
                    "implementation TEXT,result TEXT REFERENCES results(id),"
                    "PRIMARY KEY(project,kind,implementation))"
                )
                self._db.execute(
                    "INSERT INTO current_results_v2 "
                    "SELECT c.project,c.kind,r.implementation,c.result "
                    "FROM current_results c JOIN results r ON r.id=c.result"
                )
                hook("current_results_copied")
                self._db.execute("DROP TABLE current_results")
                self._db.execute("ALTER TABLE current_results_v2 RENAME TO current_results")
                hook("current_results_replaced")
                hook("migration_mid")
                self._db.execute("PRAGMA user_version=2")
                hook("format_version_updated")

    def create_project(self, project: str) -> None:
        if not isinstance(project, str) or not project:
            raise ValueError("Nonempty project identity required")
        with self._transaction():
            self._db.execute("INSERT INTO projects VALUES(?,0)", (project,))

    def revision(self, project: str) -> int:
        row = self._db.execute("SELECT revision FROM projects WHERE id=?", (project,)).fetchone()
        if row is None:
            raise KeyError(project)
        return row[0]

    def vector(self, project: str) -> dict[str, int]:
        self.revision(project)
        return dict(
            self._db.execute("SELECT key,version FROM versions WHERE project=?", (project,))
        )

    @contextmanager
    def _read(self) -> Iterator[None]:
        if self._db.in_transaction:
            yield
        else:
            self._db.execute("BEGIN")
            try:
                yield
            finally:
                self._db.execute("ROLLBACK")

    def state(self, project: str) -> dict:
        with self._read():
            return self._state(project)

    def _state(self, project: str) -> dict:
        self.revision(project)
        return {
            "mappingState": {
                r["owner"]: self.mapping_status(project, r["owner"])
                for r in self._db.execute(
                    "SELECT owner FROM mapping_state WHERE project=? ORDER BY owner", (project,)
                )
            },
            "definitions": [
                dict(r)
                for r in self._db.execute(
                    "SELECT layer,id,payload FROM definitions WHERE project=? ORDER BY layer,id",
                    (project,),
                )
            ],
            "facts": [
                dict(r)
                for r in self._db.execute(
                    "SELECT id,subject,predicate,object,owner,source_row,managed_value "
                    "FROM facts WHERE project=? ORDER BY id",
                    (project,),
                )
            ],
        }

    @staticmethod
    def _fact(fact: dict) -> None:
        if set(fact) != {"id", "subject", "predicate", "object"} or any(
            not isinstance(v, str) or not v for v in fact.values()
        ):
            raise ValueError("Fact requires nonempty id/subject/predicate/object strings")
        iri(fact["subject"])
        iri(fact["predicate"])
        if term(fact["object"]).n3() != fact["object"]:
            raise ValueError("Canonical RDF object required; derive ID from term(value).n3()")
        # A stable storage key cannot be rebound to an unrelated statement slot.
        if fact["id"] != digest([fact["subject"], fact["predicate"], fact["object"]]):
            raise ValueError("Fact identity must be content derived")

    def commit(
        self,
        project: str,
        base: int,
        operation: str,
        job: str,
        *,
        definitions: list[dict] | None = None,
        manual: list[dict] | None = None,
        edits: dict[str, str] | None = None,
        remove: list[str] | None = None,
        mapping: dict | None = None,
        hook: Hook = lambda _: None,
    ) -> dict:
        """Atomic ChangeSet or whole managed-range replacement.

        mapping = {id, rows:[{row, facts:[...]}]}; a prepared storage plan,
        NOT a CSV parser or complete mapping executor. No silent takeover exists.
        """
        if type(base) is not int or base < 0:
            raise ValueError("Nonnegative integer projectRevision required")
        if not isinstance(operation, str) or not operation or not isinstance(job, str) or not job:
            raise ValueError("String operationId and jobId required")
        plan = {
            "base": base,
            "definitions": definitions,
            "manual": manual,
            "edits": edits,
            "remove": remove,
            "mapping": mapping,
        }
        fingerprint = digest(plan)
        with self._transaction(hook):
            previous = self.marker(project, operation)
            if previous:
                if previous["fingerprint"] != fingerprint or previous["job"] != job:
                    raise Conflict("operationId reused with different plan/job")
                return previous
            if self.revision(project) != base:
                raise Conflict("Old projectRevision; re-preview required")
            before_state = self.state(project)
            before_snapshot = self._snapshot(
                {
                    "project": project,
                    "projectRevision": base,
                    "dependencyVector": self.vector(project),
                    "state": before_state,
                }
            )
            changed: set[str] = set()
            for definition in definitions or []:
                if not isinstance(definition, dict) or set(definition) != {"layer", "id", "value"}:
                    raise ValueError("Definition requires layer/id/value")
                layer, identity = definition["layer"], definition["id"]
                if (
                    not isinstance(layer, str)
                    or layer not in LAYERS
                    or not isinstance(identity, str)
                    or not identity
                ):
                    raise ValueError("Invalid definition layer/identity")
                self._definition(definition["value"])
                payload = canonical(definition["value"])
                old = self._db.execute(
                    "SELECT payload FROM definitions WHERE project=? AND layer=? AND id=?",
                    (project, layer, identity),
                ).fetchone()
                if old is None or old[0] != payload:
                    self._db.execute(
                        "INSERT OR REPLACE INTO definitions VALUES(?,?,?,?)",
                        (project, layer, identity, payload),
                    )
                    changed.add(f"{layer}:{identity}")
            for identity in remove or []:
                old = self._db.execute(
                    "SELECT * FROM facts WHERE project=? AND id=?", (project, identity)
                ).fetchone()
                if old:
                    if old["object"] is None:
                        continue  # Repeated deletion of a managed tombstone is a no-op.
                    if old["owner"]:
                        self._db.execute(
                            "UPDATE facts SET object=NULL WHERE project=? AND id=?",
                            (project, identity),
                        )
                    else:
                        self._db.execute(
                            "DELETE FROM facts WHERE project=? AND id=?", (project, identity)
                        )
                    changed.add("facts:asserted")
                    if old["owner"]:
                        changed.add(f"mapping:{old['owner']}")
            for identity, value in (edits or {}).items():
                if not isinstance(value, str) or not value:
                    raise ValueError("Edit requires a nonempty value")
                if term(value).n3() != value:
                    raise ValueError("Canonical RDF object required")
                old = self._db.execute(
                    "SELECT * FROM facts WHERE project=? AND id=?", (project, identity)
                ).fetchone()
                if old is None:
                    raise Conflict("Edited fact no longer exists")
                self._check_slot(project, old["subject"], old["predicate"], value, {identity})
                if value != old["object"]:
                    self._db.execute(
                        "UPDATE facts SET object=? WHERE project=? AND id=?",
                        (value, project, identity),
                    )
                    changed.add("facts:asserted")
                    if old["owner"]:
                        changed.add(f"mapping:{old['owner']}")
            for fact in manual or []:
                self._fact(fact)
                existing = self._db.execute(
                    "SELECT * FROM facts WHERE project=? AND id=?", (project, fact["id"])
                ).fetchone()
                if existing:
                    if existing["owner"] or existing["object"] != fact["object"]:
                        raise Conflict(
                            "Explicit fact edit required; cannot take ownership: "
                            f"slot={existing['subject']} {existing['predicate']}, "
                            f"other={existing['owner'] or 'manual'}, row={existing['source_row']}, "
                            f"id={existing['id']}"
                        )
                    continue
                self._check_slot(project, fact["subject"], fact["predicate"], fact["object"], set())
                self._db.execute(
                    "INSERT INTO facts VALUES(?,?,?,?,?,NULL,NULL,NULL)",
                    (project, fact["id"], fact["subject"], fact["predicate"], fact["object"]),
                )
                changed.add("facts:asserted")
            hook("mid_data")
            if mapping is not None:
                if self._replace_mapping(project, mapping):
                    changed.update({"facts:asserted", f"mapping:{mapping['id']}"})
            self._validate_references(project)
            self._validate_single_slots(project)
            after_state = self.state(project)
            if after_state["facts"] == before_state["facts"]:
                changed.discard("facts:asserted")
            before_definitions = {
                (d["layer"], d["id"]): d["payload"] for d in before_state["definitions"]
            }
            after_definitions = {
                (d["layer"], d["id"]): d["payload"] for d in after_state["definitions"]
            }
            for key in tuple(changed):
                category, identity_key = key.split(":", 1)
                if category == "facts":
                    continue
                if before_definitions.get((category, identity_key)) != after_definitions.get(
                    (category, identity_key)
                ):
                    continue
                if category == "mapping":
                    before_owned = [f for f in before_state["facts"] if f["owner"] == identity_key]
                    after_owned = [f for f in after_state["facts"] if f["owner"] == identity_key]
                    if before_owned != after_owned:
                        continue
                changed.discard(key)
            hook("mid_ownership")
            for key in sorted(changed):
                family(key)
                self._db.execute(
                    "INSERT INTO versions VALUES(?,?,1) ON CONFLICT(project,key) "
                    "DO UPDATE SET version=version+1",
                    (project, key),
                )
            if mapping is not None:
                version = self.vector(project).get(f"mapping:{mapping['id']}", 0)
                self._db.execute(
                    "INSERT OR REPLACE INTO mapping_state VALUES(?,?,?)",
                    (project, mapping["id"], version),
                )
            self._invalidate(project)
            hook("mid_invalidation")
            new_revision = base + 1
            self._db.execute("UPDATE projects SET revision=? WHERE id=?", (new_revision, project))
            self._db.execute(
                "INSERT INTO commits VALUES(?,?,?,?,?,?)",
                (project, operation, job, new_revision, fingerprint, canonical(plan)),
            )
            after_snapshot = self._snapshot(
                {
                    "project": project,
                    "projectRevision": new_revision,
                    "dependencyVector": self.vector(project),
                    "state": self.state(project),
                }
            )
            self._db.execute(
                "INSERT INTO commit_evidence VALUES(?,?,?,?)",
                (project, operation, before_snapshot, after_snapshot),
            )
            hook("mid_marker")
        return self.marker(project, operation)

    def mapping_status(self, project: str, owner: str) -> dict | None:
        row = self._db.execute(
            "SELECT generated_version FROM mapping_state WHERE project=? AND owner=?",
            (project, owner),
        ).fetchone()
        if row is None:
            return None
        vector = {f"mapping:{owner}": row[0]}
        return {"generatedVersion": row[0], "stale": reasons(vector, self.vector(project))}

    @staticmethod
    def _definition(value: object) -> None:
        if not isinstance(value, dict):
            return  # Other definition payloads remain opaque canonical JSON in this spike.
        if "references" in value and not isinstance(value["references"], list):
            raise ValueError("Definition references must be a list")
        if "triples" in value:
            if not isinstance(value["triples"], list):
                raise ValueError("Definition triples must be a list")
            for triple in value["triples"]:
                if not isinstance(triple, dict) or set(triple) != {
                    "subject",
                    "predicate",
                    "object",
                }:
                    raise ValueError("Malformed definition triple")
                iri(triple["subject"])
                iri(triple["predicate"])
                obj = triple["object"]
                if not isinstance(obj, str) or term(obj).n3() != obj:
                    raise ValueError("Canonical RDF object required in definition")
        if "singleValuedPredicates" in value:
            predicates = value["singleValuedPredicates"]
            if not isinstance(predicates, list):
                raise ValueError("singleValuedPredicates must be a list")
            for predicate in predicates:
                iri(predicate)

    def _single_predicates(self, project: str) -> set[str]:
        predicates = set()
        for row in self._db.execute(
            "SELECT payload FROM definitions WHERE project=? AND layer='ontology'", (project,)
        ):
            value = json.loads(row[0])
            if isinstance(value, dict):
                predicates.update(value.get("singleValuedPredicates", []))
        return predicates

    def _validate_single_slots(self, project: str) -> None:
        for predicate in self._single_predicates(project):
            if self._db.execute(
                "SELECT subject FROM facts WHERE project=? AND predicate=? AND object IS NOT NULL "
                "GROUP BY subject HAVING COUNT(*)>1 LIMIT 1",
                (project, predicate),
            ).fetchone():
                raise Conflict("Single-valued declaration conflicts with existing facts")

    def _validate_references(self, project: str) -> None:
        for row in self._db.execute("SELECT payload FROM definitions WHERE project=?", (project,)):
            value = json.loads(row[0])
            self._definition(value)
            if not isinstance(value, dict):
                continue
            for reference in value.get("references", []):
                if not isinstance(reference, dict) or set(reference) != {"layer", "id"}:
                    raise ValueError("Malformed definition reference")
                if not self._db.execute(
                    "SELECT 1 FROM definitions WHERE project=? AND layer=? AND id=?",
                    (project, reference["layer"], reference["id"]),
                ).fetchone():
                    raise Conflict("Unresolved definition reference")

    def _check_slot(
        self,
        project: str,
        subject: str,
        predicate: str,
        value: str,
        excluded: set[str],
        single_predicates: set[str] | None = None,
    ) -> None:
        single = predicate in (
            self._single_predicates(project) if single_predicates is None else single_predicates
        )
        reserved_id = digest([subject, predicate, value])
        for row in self._db.execute(
            "SELECT * FROM facts WHERE project=? AND subject=? AND predicate=?",
            (project, subject, predicate),
        ):
            if row["id"] not in excluded and (
                row["id"] == reserved_id
                or (row["object"] is not None and (single or row["object"] == value))
            ):
                raise Conflict(
                    f"Ownership conflict: slot={subject} {predicate}, "
                    f"other={row['owner'] or 'manual'}, row={row['source_row']}, id={row['id']}"
                )

    def _replace_mapping(self, project: str, mapping: dict) -> bool:
        if (
            not isinstance(mapping, dict)
            or set(mapping) != {"id", "rows"}
            or not isinstance(mapping["id"], str)
            or not mapping["id"]
            or not isinstance(mapping["rows"], list)
        ):
            raise ValueError("Invalid mapping plan")
        owner = mapping["id"]
        old = self._db.execute("SELECT * FROM facts WHERE project=? AND owner=?", (project, owner))
        for fact in old:
            if fact["object"] != fact["managed_value"]:
                raise Conflict(
                    f"Manual drift: mapping={owner}, row={fact['source_row']}, "
                    f"slot={fact['subject']} {fact['predicate']}"
                )
        own_ids = {
            r[0]
            for r in self._db.execute(
                "SELECT id FROM facts WHERE project=? AND owner=?", (project, owner)
            )
        }
        single_predicates = self._single_predicates(project)
        staged_slots = set()
        staged = []
        rows = set()
        identities = set()
        for row in mapping["rows"]:
            if (
                not isinstance(row, dict)
                or set(row) != {"row", "facts"}
                or not isinstance(row["row"], str)
                or not row["row"]
                or row["row"] in rows
                or not isinstance(row["facts"], list)
            ):
                raise ValueError("Empty/duplicate source row")
            rows.add(row["row"])
            for fact in row["facts"]:
                self._fact(fact)
                if fact["id"] in identities:
                    raise Conflict("Multiple source rows support same fact")
                identities.add(fact["id"])
                self._check_slot(
                    project,
                    fact["subject"],
                    fact["predicate"],
                    fact["object"],
                    own_ids,
                    single_predicates,
                )
                slot = (fact["subject"], fact["predicate"])
                if fact["predicate"] in single_predicates and slot in staged_slots:
                    raise Conflict("Single-valued mapping slot has multiple values")
                staged_slots.add(slot)
                staged.append(
                    (
                        project,
                        fact["id"],
                        fact["subject"],
                        fact["predicate"],
                        fact["object"],
                        owner,
                        row["row"],
                        fact["object"],
                    )
                )
        existing = [
            tuple(r)
            for r in self._db.execute(
                "SELECT project,id,subject,predicate,object,owner,source_row,managed_value "
                "FROM facts WHERE project=? AND owner=?",
                (project, owner),
            )
        ]
        if sorted(existing) == sorted(staged):
            return False
        self._db.execute("DELETE FROM facts WHERE project=? AND owner=?", (project, owner))
        self._db.executemany("INSERT INTO facts VALUES(?,?,?,?,?,?,?,?)", staged)
        return True

    def marker(self, project: str, operation: str) -> dict | None:
        row = self._db.execute(
            "SELECT c.*,e.before_snapshot,e.after_snapshot FROM commits c "
            "LEFT JOIN commit_evidence e ON e.project=c.project AND e.operation=c.operation "
            "WHERE c.project=? AND c.operation=?",
            (project, operation),
        ).fetchone()
        return dict(row) if row else None

    def snapshot(self, project: str) -> str:
        with self._transaction():
            payload = {
                "project": project,
                "projectRevision": self.revision(project),
                "dependencyVector": self.vector(project),
                "state": self.state(project),
            }
            return self._snapshot(payload)

    def _snapshot(self, payload: dict) -> str:
        identity = digest(payload)
        self._db.execute(
            "INSERT OR IGNORE INTO snapshots VALUES(?,?)", (identity, canonical(payload))
        )
        return identity

    def load_snapshot(self, identity: str) -> dict:
        row = self._db.execute("SELECT payload FROM snapshots WHERE id=?", (identity,)).fetchone()
        if row is None:
            raise KeyError("Missing replay input snapshot")
        payload = json.loads(row[0])
        if digest(payload) != identity:
            raise ValueError("Snapshot integrity failure")
        return payload

    def _project_snapshot(self, identity: str, project: str) -> dict:
        """Validate storage shape; round evidence is not a formal project input."""
        snap = self.load_snapshot(identity)
        if not isinstance(snap, dict) or not isinstance(snap.get("project"), str):
            raise ValueError("Project state snapshot required")
        if snap["project"] != project:
            raise Conflict("Cross-project snapshot")
        revision = snap.get("projectRevision")
        vector = snap.get("dependencyVector")
        state = snap.get("state")
        if (
            type(revision) is not int
            or revision < 0
            or not isinstance(vector, dict)
            or not isinstance(state, dict)
            or not isinstance(state.get("definitions"), list)
            or not isinstance(state.get("facts"), list)
            or not isinstance(state.get("mappingState"), dict)
        ):
            raise ValueError("Project state snapshot required")
        for key, version in vector.items():
            family(key)
            if type(version) is not int or version < 0:
                raise ValueError("Invalid snapshot dependency version")
        self._snapshot_state(state)
        return snap

    @classmethod
    def _snapshot_state(cls, state: dict) -> None:
        """Check persisted record shapes, not future business execution semantics."""
        identities = set()
        definitions = []
        for record in state["definitions"]:
            if (
                not isinstance(record, dict)
                or set(record) != {"layer", "id", "payload"}
                or not isinstance(record["layer"], str)
                or record["layer"] not in LAYERS
                or not isinstance(record["id"], str)
                or not record["id"]
                or not isinstance(record["payload"], str)
            ):
                raise ValueError("Incomplete snapshot definition record")
            key = (record["layer"], record["id"])
            if key in identities:
                raise ValueError("Duplicate snapshot definition")
            identities.add(key)
            value = json.loads(record["payload"])
            canonical(value)
            cls._definition(value)
            definitions.append(value)
        for value in definitions:
            for reference in value.get("references", []) if isinstance(value, dict) else []:
                if (
                    not isinstance(reference, dict)
                    or set(reference) != {"layer", "id"}
                    or not isinstance(reference["layer"], str)
                    or not isinstance(reference["id"], str)
                    or (reference["layer"], reference["id"]) not in identities
                ):
                    raise ValueError("Incomplete snapshot definition reference")
        identities = set()
        for record in state["facts"]:
            if (
                not isinstance(record, dict)
                or set(record)
                != {"id", "subject", "predicate", "object", "owner", "source_row", "managed_value"}
                or not isinstance(record["id"], str)
                or not record["id"]
                or record["id"] in identities
            ):
                raise ValueError("Incomplete snapshot fact record")
            identities.add(record["id"])
            iri(record["subject"])
            iri(record["predicate"])
            owner = record["owner"]
            if owner is None:
                if any(record[k] is not None for k in ("source_row", "managed_value")):
                    raise ValueError("Invalid snapshot manual ownership")
                values = [record["object"]]
            else:
                if not all(
                    isinstance(record[k], str) and record[k] for k in ("owner", "source_row")
                ):
                    raise ValueError("Incomplete snapshot mapping ownership")
                values = [record["managed_value"]]
                if record["object"] is not None:
                    values.append(record["object"])
            for value in values:
                if not isinstance(value, str) or term(value).n3() != value:
                    raise ValueError("Invalid snapshot RDF object")
            # ID stays bound to the original statement across edits and tombstones.
        for owner, status in state["mappingState"].items():
            if (
                not isinstance(owner, str)
                or not owner
                or not isinstance(status, dict)
                or set(status) != {"generatedVersion", "stale"}
                or type(status["generatedVersion"]) is not int
                or status["generatedVersion"] < -1
                or not isinstance(status["stale"], list)
            ):
                raise ValueError("Incomplete snapshot mapping state")
            for reason in status["stale"]:
                if (
                    not isinstance(reason, dict)
                    or set(reason) != {"code", "dependency", "before", "after"}
                    or reason["code"] != CODES["mapping"]
                    or reason["dependency"] != f"mapping:{owner}"
                    or type(reason["before"]) is not int
                    or reason["before"] < -1
                    or type(reason["after"]) is not int
                    or reason["after"] < 0
                ):
                    raise ValueError("Invalid snapshot mapping stale reason")

    def publish(
        self,
        project: str,
        snapshot: str,
        dependencies: list[str],
        kind: str,
        payload: object,
        implementation: dict[str, str],
    ) -> str:
        """Append result evidence, publish current only after in-transaction revalidation."""
        required = set(RULES["implementationCompatibility"]["identityKeys"])
        if (
            not isinstance(implementation, dict)
            or set(implementation) != required
            or not all(isinstance(value, str) and value for value in implementation.values())
        ):
            raise ValueError("Complete execution provenance required")
        with self._transaction():
            snap = self._project_snapshot(snapshot, project)
            if not isinstance(dependencies, list) or not dependencies:
                raise ValueError("At least one registered dependency required")
            for key in dependencies:
                category = family(key)
                if key == "facts:asserted":
                    continue  # Explicit canonical scope exists even for an empty project.
                _, identity_key = key.split(":", 1)
                registered = any(
                    d["layer"] == category and d["id"] == identity_key
                    for d in snap["state"]["definitions"]
                )
                registered_mapping = (
                    category == "mapping" and identity_key in snap["state"]["mappingState"]
                )
                if (
                    not registered
                    and not registered_mapping
                    and key not in snap["dependencyVector"]
                ):
                    raise ValueError(f"Unresolved snapshot dependency: {key}")
            vector = {key: snap["dependencyVector"].get(key, 0) for key in dependencies}
            stale = reasons(vector, self.vector(project))
            identity = str(uuid4())
            cache_key = digest(
                {
                    "project": project,
                    "kind": kind,
                    "snapshot": snapshot,
                    "dependencies": vector,
                    "implementation": implementation,
                }
            )
            self._db.execute(
                "INSERT INTO results VALUES(?,?,?,?,?,?,?,?)",
                (
                    identity,
                    project,
                    snapshot,
                    kind,
                    canonical(vector),
                    canonical(implementation),
                    cache_key,
                    canonical(payload),
                ),
            )
            self._db.execute("INSERT INTO result_state VALUES(?,?)", (identity, canonical(stale)))
            if can_publish_current(snap["projectRevision"], self.revision(project), stale):
                self._db.execute(
                    "INSERT OR REPLACE INTO current_results VALUES(?,?,?,?)",
                    (project, kind, canonical(implementation), identity),
                )
            return identity

    def _invalidate(self, project: str) -> None:
        now = self.vector(project)
        for row in self._db.execute(
            "SELECT id,dependencies FROM results WHERE project=?", (project,)
        ):
            stale = reasons(json.loads(row["dependencies"]), now)
            self._db.execute(
                "UPDATE result_state SET stale=? WHERE result=?", (canonical(stale), row["id"])
            )
            if stale:
                self._db.execute("DELETE FROM current_results WHERE result=?", (row["id"],))

    def result(self, identity: str) -> dict:
        with self._read():
            return self._result(identity)

    def _result(self, identity: str) -> dict:
        row = self._db.execute(
            "SELECT r.*,s.stale FROM results r JOIN result_state s ON s.result=r.id WHERE r.id=?",
            (identity,),
        ).fetchone()
        if row is None:
            raise KeyError(identity)
        result = dict(row)
        for key in ("payload", "dependencies", "implementation", "stale"):
            result[key] = json.loads(result[key]) if result[key] is not None else None
        is_current = self._db.execute(
            "SELECT 1 FROM current_results WHERE result=?", (identity,)
        ).fetchone()
        result["state"] = (
            "stale" if result["stale"] else ("current" if is_current else "historical")
        )
        return result

    def current(self, project: str, kind: str, implementation: dict[str, str]) -> dict | None:
        with self._read():
            return self._current(project, kind, implementation)

    def _current(self, project: str, kind: str, implementation: dict[str, str]) -> dict | None:
        row = self._db.execute(
            "SELECT result FROM current_results WHERE project=? AND kind=? AND implementation=?",
            (project, kind, canonical(implementation)),
        ).fetchone()
        if not row:
            return None
        result = self.result(row[0])
        # No implicit compatibility across engine, semantics or lock upgrades.
        if (
            result["implementation"] != implementation
            or result["stale"]
            or result["payload"] is None
        ):
            return None
        return result

    def pin_result(self, identity: str, report: str) -> None:
        with self._transaction():
            result = self.result(identity)
            if result["payload"] is None:
                raise ValueError("Cannot save report with evicted payload")
            self._db.execute("INSERT INTO result_pins VALUES(?,?)", (identity, report))

    def collect_cache(self) -> list[str]:
        """Only unpinned result payloads; identities/definitions/snapshots remain."""
        with self._transaction():
            ids = [
                r[0]
                for r in self._db.execute(
                    "SELECT id FROM results WHERE id NOT IN (SELECT result FROM result_pins) "
                    "AND id NOT IN (SELECT result FROM current_results) AND payload IS NOT NULL"
                )
            ]
            for identity in ids:
                self._db.execute("UPDATE results SET payload=NULL WHERE id=?", (identity,))
            return ids

    def start_run(self, project: str, snapshot: str, config: dict, implementation: dict) -> str:
        if not isinstance(config, dict) or not isinstance(implementation, dict):
            raise ValueError("Run config and implementation must be objects")
        with self._transaction():
            self._project_snapshot(snapshot, project)
            identity = str(uuid4())
            self._db.execute(
                "INSERT INTO runs VALUES(?,?,?,?,?)",
                (identity, project, snapshot, canonical(config), canonical(implementation)),
            )
            return identity

    def commit_round(
        self,
        run: str,
        number: int,
        state: dict,
        operation: str,
        job: str,
        hook: Hook = lambda _: None,
    ) -> str:
        """Persist a prepared complete round, not an E.2 executor."""
        if not isinstance(operation, str) or not operation or not isinstance(job, str) or not job:
            raise ValueError("operationId and jobId required")
        if type(number) is not int or not 1 <= number <= 1000:
            raise ValueError("Integer round number must be 1..1000")
        if not isinstance(state, dict):
            raise ValueError("Prepared round state must be an object")
        with self._transaction(hook):
            record = self._run(run)
            round_payload = {
                "project": record["project"],
                "run": run,
                "round": number,
                "state": state,
            }
            previous = self._db.execute(
                "SELECT * FROM rounds WHERE operation=?", (operation,)
            ).fetchone()
            if previous:
                if (
                    previous["run"] != run
                    or previous["number"] != number
                    or previous["job"] != job
                    or previous["snapshot"] != digest(round_payload)
                ):
                    raise Conflict("Round operationId reused with different content/run/job")
                return previous["snapshot"]
            if self._db.execute("SELECT 1 FROM run_terminal WHERE run=?", (run,)).fetchone():
                raise Conflict("Terminal run is immutable")
            last = self.progress(run)
            if number != (last["lastCommittedRound"] if last else 0) + 1:
                raise Conflict("Nonsequential round")
            maximum = json.loads(record["config"]).get("maxRounds")
            if (
                not isinstance(maximum, int)
                or isinstance(maximum, bool)
                or not 1 <= maximum <= 1000
            ):
                raise ValueError("maxRounds must be 1..1000")
            if number > maximum:
                raise Conflict("Round limit")
            identity = self._snapshot(round_payload)
            hook("mid_data")
            self._db.execute(
                "INSERT INTO rounds VALUES(?,?,?,?,?)", (run, number, identity, operation, job)
            )
            hook("mid_marker")
            return identity

    def _run(self, identity: str) -> sqlite3.Row:
        row = self._db.execute("SELECT * FROM runs WHERE id=?", (identity,)).fetchone()
        if row is None:
            raise KeyError(identity)
        return row

    def progress(self, run: str) -> dict | None:
        self._run(run)
        row = self._db.execute(
            "SELECT number,snapshot FROM rounds WHERE run=? ORDER BY number DESC LIMIT 1", (run,)
        ).fetchone()
        return {"runId": run, "lastCommittedRound": row[0], "snapshotRef": row[1]} if row else None

    def finish_run(self, run: str, status: str, evidence: dict) -> None:
        if status not in {"succeeded", "cancelled", "failed"}:
            raise ValueError("Invalid terminal status")
        with self._transaction():
            self._run(run)
            self._db.execute(
                "INSERT INTO run_terminal VALUES(?,?,?)", (run, status, canonical(evidence))
            )

    def history(self, run: str) -> dict:
        with self._read():
            return self._history(run)

    def _history(self, run: str) -> dict:
        record = dict(self._run(run))
        record["rounds"] = [
            dict(r)
            for r in self._db.execute("SELECT * FROM rounds WHERE run=? ORDER BY number", (run,))
        ]
        terminal = self._db.execute(
            "SELECT status,evidence FROM run_terminal WHERE run=?", (run,)
        ).fetchone()
        record["terminal"] = dict(terminal) if terminal else None
        record["committedProgress"] = self.progress(run)
        try:
            self._project_snapshot(record["snapshot"], record["project"])
            for r in record["rounds"]:
                saved = self.load_snapshot(r["snapshot"])
                if (
                    not isinstance(saved, dict)
                    or saved.get("project") != record["project"]
                    or saved.get("run") != run
                    or type(saved.get("round")) is not int
                    or saved.get("round") != r["number"]
                    or not isinstance(saved.get("state"), dict)
                ):
                    raise ValueError("Incomplete round evidence")
            config = json.loads(record["config"])
            impl = json.loads(record["implementation"])
            if not isinstance(config, dict) or not isinstance(impl, dict):
                raise ValueError("Incomplete run configuration or provenance")
            record["replayable"] = (
                isinstance(config.get("parameters"), dict)
                and isinstance(config.get("events"), list)
                and all(
                    isinstance(config.get(key), dict)
                    for key in ("ruleVersions", "behaviorVersions")
                )
                and isinstance(config.get("maxRounds"), int)
                and not isinstance(config.get("maxRounds"), bool)
                and 1 <= config["maxRounds"] <= 1000
                and all(
                    isinstance(impl.get(key), str) and impl[key]
                    for key in ("executionSemanticsVersion", "engineVersion", "dependencyLockHash")
                )
            )
        except (KeyError, ValueError, Conflict):
            record["replayable"] = False
        return record

    def backup(self, destination: str | Path) -> None:
        if Path(destination).exists():
            raise ValueError("Backup target must be new")
        target = sqlite3.connect(destination)
        try:
            self._db.backup(target)
        finally:
            target.close()


SCHEMA = [
    "CREATE TABLE projects(id TEXT PRIMARY KEY,revision INTEGER NOT NULL)",
    "CREATE TABLE versions(project TEXT REFERENCES projects(id),key TEXT,version INTEGER NOT NULL,"
    "PRIMARY KEY(project,key))",
    "CREATE TABLE definitions(project TEXT REFERENCES projects(id),layer TEXT,id TEXT,payload TEXT,"
    "PRIMARY KEY(project,layer,id))",
    "CREATE TABLE facts(project TEXT REFERENCES projects(id),id TEXT,subject TEXT,predicate TEXT,"
    "object TEXT,owner TEXT,source_row TEXT,managed_value TEXT,PRIMARY KEY(project,id))",
    "CREATE TABLE commits(project TEXT REFERENCES projects(id),operation TEXT,job TEXT,"
    "revision INTEGER,"
    "fingerprint TEXT,plan TEXT,PRIMARY KEY(project,operation))",
    "CREATE TABLE snapshots(id TEXT PRIMARY KEY,payload TEXT NOT NULL)",
    "CREATE TABLE results(id TEXT PRIMARY KEY,project TEXT REFERENCES projects(id),"
    "snapshot TEXT REFERENCES snapshots(id),kind TEXT,dependencies TEXT,implementation TEXT,"
    "cache_key TEXT,payload TEXT)",
    "CREATE TABLE result_state(result TEXT PRIMARY KEY REFERENCES results(id),stale TEXT)",
    "CREATE TABLE current_results(project TEXT REFERENCES projects(id),kind TEXT,"
    "result TEXT REFERENCES results(id),PRIMARY KEY(project,kind))",
    "CREATE TABLE result_pins(result TEXT REFERENCES results(id),report TEXT,"
    "PRIMARY KEY(result,report))",
    "CREATE TABLE runs(id TEXT PRIMARY KEY,project TEXT REFERENCES projects(id),"
    "snapshot TEXT REFERENCES snapshots(id),config TEXT,implementation TEXT)",
    "CREATE TABLE rounds(run TEXT REFERENCES runs(id),number INTEGER,snapshot TEXT REFERENCES "
    "snapshots(id),operation TEXT UNIQUE,job TEXT,PRIMARY KEY(run,number))",
    "CREATE TABLE run_terminal(run TEXT PRIMARY KEY REFERENCES runs(id),status TEXT,evidence TEXT)",
]
# SQL-level defenses protect immutable evidence even if a later adapter accidentally updates it.
for _table in ("snapshots", "commits", "runs", "rounds", "run_terminal"):
    for _action in ("UPDATE", "DELETE"):
        SCHEMA.append(
            f"CREATE TRIGGER immutable_{_table}_{_action} BEFORE {_action} ON {_table} "
            "BEGIN SELECT RAISE(ABORT,'immutable evidence'); END"
        )
