"""S2 coordinator-owned SQLite application service, composed with S1 transactions.

Workers never open this store. The lifetime lease fences previous coordinators;
SQLite transactions serialize formal project writes and all job evidence.
"""

import json
import os
import re
import time
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from ontolearn_engine.invalidation import reasons
from ontolearn_engine.storage import (
    FORMAT_VERSION,
    Conflict,
    Hook,
    Store,
    _close_resources,
    canonical,
    digest,
)

TERMINAL = {"succeeded", "failed", "cancelled"}
PUBLIC_KINDS = {"query", "reasoning", "validation", "behavior", "scenario", "test", "receipt"}
SET_FAMILIES = {"ontology", "rule", "constraint", "behavior", "scenario", "mapping", "query"}
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z")


class JobFault(ValueError):
    """Structured internal failure; callers map only these fixed fields."""

    def __init__(self, code: str, params: dict | None = None):
        super().__init__(code)
        self.code = code
        self.params = params or {}


def fault(code, **params):
    raise JobFault(code, params)


class JobStore(Store):
    def __init__(
        self,
        path: str | Path,
        *,
        contract,
        now_ms=None,
        cursor_ttl_ms: int = 60000,
        max_cursor_records: int = 256,
        target_format: int = FORMAT_VERSION,
        backup_path: str | Path | None = None,
        migration_hook: Hook = lambda _: None,
        job_migration_hook: Hook = lambda _: None,
    ):
        if type(target_format) is not int or target_format not in {2, 3}:
            raise ValueError("Unsupported target project format")
        if not 1 <= cursor_ttl_ms <= 60000 or not 1 <= max_cursor_records <= 4096:
            raise ValueError("Invalid projection bounds")
        self.contract = contract
        self.now_ms = now_ms or (lambda: int(time.time() * 1000))
        self.cursor_ttl_ms = cursor_ttl_ms
        self.max_cursor_records = max_cursor_records
        self._lease = None
        parent_ready = False
        try:
            # Default2 keeps the approved lease path. Explicit3 delegates its one
            # lifetime lease to Store; never acquire that same inode a second time.
            if target_format == 2:
                self._lease = open(str(path) + ".writer-lock", "a+b")
                self._lock()
            super().__init__(
                path, migration_hook, target_format=target_format, backup_path=backup_path
            )
            parent_ready = True  # Store transfers its resources only after a successful return.
            if target_format == 3:
                self._migrate_job3(job_migration_hook)
            else:
                with self._transaction():
                    for sql in JOB_SCHEMA:
                        self._db.execute(sql)
            self._migrate_query_payloads(job_migration_hook)
        except BaseException:
            # A failed parent already attempted its own closes. Its leftover
            # attributes are not a second transfer of resource ownership.
            owned = [("legacyLease", self._lease)]
            if parent_ready:
                owned = [
                    ("database", self._db),
                    ("format3Lease", self._format3_lease),
                    *owned,
                ]
            failures = _close_resources(owned)
            self._cleanup_failures = getattr(self, "_cleanup_failures", []) + failures
            raise

    def _migrate_query_payloads(self, hook):
        """Add a private catalog without changing either original Job schema hash.

        Old query jobs are explicitly inventoried; they never acquire a fictitious
        complete payload. Partial/unknown extension catalogs are rejected, not repaired.
        """
        from ontolearn_engine.project.format3 import _schema

        names = [_job_object_name(sql) for sql in QUERY_PAYLOAD_SCHEMA]
        present = {
            r[0]: r[1]
            for r in self._db.execute(
                "SELECT name,sql FROM sqlite_master WHERE name IN ("
                + ",".join("?" for _ in names)
                + ")",
                tuple(names),
            )
        }
        if present:
            if set(present) != set(names) or any(
                _schema(present[_job_object_name(sql)]) != _schema(sql)
                for sql in QUERY_PAYLOAD_SCHEMA
            ):
                fault("INVALID_STATE")
            with self._read():
                self._validate_query_catalog()
            return
        with self._transaction(lambda phase: hook("query_payload_" + phase)):
            legacy = []
            for row in self._db.execute("SELECT id,context FROM jobs ORDER BY id"):
                context = json.loads(row["context"])
                if "queryRequest" in context:
                    fault("INVALID_STATE")  # Missing catalog for an already-new producer.
                if context.get("capability") == "query.execute":
                    legacy.append(row["id"])
            for sql in QUERY_PAYLOAD_SCHEMA:
                self._db.execute(sql)
                hook("query_payload_ddl:" + _job_object_name(sql))
            for identity in legacy:
                self._db.execute("INSERT INTO query_legacy_jobs VALUES(?)", (identity,))
            self._db.execute(
                "INSERT INTO query_payload_format VALUES(1,1,?,?)",
                (QUERY_PAYLOAD_HASH, self.actual_format),
            )
            hook("query_payload_catalog")
            self._validate_query_catalog()

    def _validate_query_catalog(self):
        catalog = self._db.execute("SELECT * FROM query_payload_format").fetchall()
        if (
            len(catalog) != 1
            or tuple(catalog[0]) != (1, 1, QUERY_PAYLOAD_HASH, catalog[0]["source_format"])
            or catalog[0]["source_format"] not in {2, 3}
        ):
            fault("INVALID_STATE")
        legacy = {r[0] for r in self._db.execute("SELECT job FROM query_legacy_jobs")}
        known = set()
        for row in self._db.execute("SELECT id,context,dto FROM jobs"):
            context, job = json.loads(row["context"]), json.loads(row["dto"])
            if context.get("capability") != "query.execute":
                continue
            if row["id"] in legacy:
                if "queryRequest" in context:
                    fault("INVALID_STATE")
                known.add(row["id"])
                continue
            if "queryRequest" not in context:
                fault("INVALID_STATE")
            claim = self._db.execute(
                "SELECT * FROM operation_claims WHERE operation=?", (job["operationId"],)
            ).fetchone()
            if claim is None or claim["job"] != row["id"]:
                fault("INVALID_STATE")
            self._accepted_job(
                claim,
                job["projectId"],
                job["capability"],
                job["input"],
                job["confirmationRef"],
                job["implementation"],
                job["limits"],
            )
            records = self._db.execute(
                "SELECT q.result FROM query_payloads q JOIN job_results r ON r.id=q.result "
                "WHERE r.job=?",
                (row["id"],),
            ).fetchall()
            if len(records) != (1 if job["state"] == "succeeded" else 0):
                fault("INVALID_STATE")
            if records and job["resultRef"] != {
                "resultId": records[0][0],
                "inputSnapshotId": job["inputSnapshotId"],
            }:
                fault("INVALID_STATE")
        if (
            known != legacy
            or self._db.execute(
                "SELECT 1 FROM query_payloads q LEFT JOIN job_results r ON r.id=q.result "
                "LEFT JOIN jobs j ON j.id=r.job WHERE j.id IS NULL OR j.id IN "
                "(SELECT job FROM query_legacy_jobs) LIMIT 1"
            ).fetchone()
        ):
            fault("INVALID_STATE")
        for row in self._db.execute(
            "SELECT j.context FROM query_payloads q JOIN job_results r ON r.id=q.result "
            "JOIN jobs j ON j.id=r.job"
        ):
            context = json.loads(row[0])
            if context.get("capability") != "query.execute" or "queryRequest" not in context:
                fault("INVALID_STATE")

    def _lock(self):
        try:
            if os.name == "nt":
                import msvcrt

                self._lease.seek(0)
                if self._lease.read(1) == b"":
                    self._lease.write(b"0")
                    self._lease.flush()
                self._lease.seek(0)
                msvcrt.locking(self._lease.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._lease.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            fault("STORAGE_BUSY", retryAfterMs=250)

    def close(self):
        self._cleanup_failures = _close_resources(
            [
                ("database", self._db),
                ("format3Lease", self._format3_lease),
                ("legacyLease", self._lease),
            ]
        )
        if self._cleanup_failures:
            raise self._cleanup_failures[0][1]

    def _migrate_job3(self, hook):
        from ontolearn_engine.project.format3 import Format3Fault, _schema

        # A durable layer marker is schema evidence, never session/hello authority.
        catalog = self._db.execute("SELECT 1 FROM sqlite_master WHERE name='job_format'").fetchone()
        if catalog:
            with self._read():
                self._validate_job3()
            return
        old_objects = {_job_object_name(sql): sql for sql in JOB_SCHEMA}
        present = {
            r[0]: r[1]
            for r in self._db.execute(
                "SELECT name,sql FROM sqlite_master WHERE name IN ("
                + ",".join("?" for _ in old_objects)
                + ")",
                tuple(old_objects),
            )
        }
        if present and (
            set(present) != set(old_objects)
            or any(_schema(present[name]) != _schema(sql) for name, sql in old_objects.items())
        ):
            raise Format3Fault("structure")
        source = "v2" if present else "new"
        with self._transaction(lambda phase: hook("job3_" + phase)):
            if source == "new":
                for sql in JOB3_SCHEMA:
                    self._db.execute(sql)
                    hook("job3_ddl:" + _job_object_name(sql))
            else:
                # Only the actual global claim table is evolved. Original identity,
                # context fingerprint and job references remain byte-for-byte.
                self._db.execute("ALTER TABLE operation_claims RENAME TO operation_claims_v2")
                hook("job3_claims_renamed")
                self._db.execute(JOB3_CLAIMS)
                hook("job3_claims_created")
                self._db.execute(
                    "INSERT INTO operation_claims(operation,project,job,fingerprint,kind,context) "
                    "SELECT operation,project,job,fingerprint,'job',NULL FROM operation_claims_v2"
                )
                hook("job3_claims_copied")
                self._db.execute("DROP TABLE operation_claims_v2")
                hook("job3_claims_dropped")
                for sql in JOB3_SCHEMA:
                    if _job_object_name(sql).startswith("immutable_operation_claims_"):
                        self._db.execute(sql)
                        hook("job3_claims_trigger:" + _job_object_name(sql))
                hook("job3_claims_swapped")
            for sql in JOB3_CATALOG:
                self._db.execute(sql)
                hook("job3_ddl:" + _job_object_name(sql))
            for row in self._db.execute("SELECT id FROM projects ORDER BY id").fetchall():
                self.public_project(row[0])
                hook("job3_identity")
            self._db.execute("INSERT INTO job_format VALUES(1,3,?,?)", (JOB3_HASH, source))
            hook("job3_catalog")
            self._validate_job3()
            hook("job3_validated")

    def _validate_job3(self):
        from ontolearn_engine.project.format3 import Format3Fault, _json, _schema

        try:
            for sql in JOB3_SCHEMA + JOB3_CATALOG:
                row = self._db.execute(
                    "SELECT sql FROM sqlite_master WHERE name=?", (_job_object_name(sql),)
                ).fetchone()
                if row is None or _schema(row[0]) != _schema(sql):
                    raise Format3Fault("structure")
            catalog = self._db.execute("SELECT * FROM job_format").fetchall()
            if (
                len(catalog) != 1
                or catalog[0]["schema_version"] != 3
                or catalog[0]["schema_hash"] != JOB3_HASH
                or catalog[0]["source_kind"] not in {"new", "v2"}
            ):
                raise Format3Fault("structure")
            if self._db.execute("PRAGMA foreign_key_check").fetchone() is not None:
                raise Format3Fault("structure")
            projects = {r[0] for r in self._db.execute("SELECT id FROM projects")}
            public = self._db.execute("SELECT * FROM public_projects").fetchall()
            if projects != {r["internal"] for r in public} or any(
                not isinstance(r["public"], str) or not UUID.fullmatch(r["public"]) for r in public
            ):
                raise Format3Fault("structure")
            jobs = {r[0] for r in self._db.execute("SELECT id FROM jobs")}
            claimed = set()
            for claim in self._db.execute("SELECT * FROM operation_claims"):
                if not isinstance(claim["operation"], str) or not UUID.fullmatch(
                    claim["operation"]
                ):
                    raise Format3Fault("structure")
                if claim["kind"] == "application":
                    from ontolearn_engine.project.applications import claim_context
                    from ontolearn_engine.project.format3 import receipt_for
                    from ontolearn_engine.project.project_lifecycle import creation_context

                    internal = self._project(claim["project"])
                    creation = creation_context(self, internal, claim["operation"])
                    if creation is None:
                        claim_context(self, internal, claim["operation"])
                    receipt = receipt_for(self, internal, claim["operation"])
                    if creation is not None and receipt != creation["receipt"]:
                        raise Format3Fault("structure")
                    continue
                if claim["kind"] != "job" or claim["context"] is not None:
                    raise Format3Fault("structure")
                row = self._db.execute("SELECT * FROM jobs WHERE id=?", (claim["job"],)).fetchone()
                if row is None:
                    raise Format3Fault("structure")
                context = _json(row["context"])
                dto = _json(row["dto"])
                if not self.contract.validate("job", dto):
                    raise Format3Fault("structure")
                if (
                    dto["jobId"] != row["id"]
                    or dto["projectId"] != claim["project"]
                    or dto["operationId"] != claim["operation"]
                ):
                    raise Format3Fault("structure")
                self._accepted_job(
                    claim,
                    claim["project"],
                    context["capability"],
                    context["input"],
                    context["confirmationRef"],
                    context["implementation"],
                    context["limits"],
                )
                claimed.add(claim["job"])
            if claimed != jobs:
                raise Format3Fault("structure")
        except Format3Fault:
            raise
        except (ValueError, KeyError, TypeError, OverflowError):
            raise Format3Fault("structure") from None

    def _application_input(self, project, change, actor, permission):
        from ontolearn_engine.project.applications import check_change, stable

        if self._target_format != 3:
            fault("INVALID_STATE")
        internal = self._project(project)
        if not isinstance(actor, str) or not UUID.fullmatch(actor) or permission != "write":
            fault("PERMISSION_DENIED")
        change = stable(change)
        check_change(change)
        if len(canonical(change).encode()) > 262144:
            fault("RESOURCE_LIMIT", resource="frame")
        return internal, change

    def _occupied_operation_evidence(self, operation):
        # Claims are global. Never adopt a legacy/unclaimed marker from this or
        # another project, or a round suboperation, into a fresh application/job.
        return any(
            self._db.execute(
                f"SELECT 1 FROM {table} WHERE operation=? LIMIT 1", (operation,)
            ).fetchone()
            for table in ("commits", "rounds", "app_operations", "app_receipts")
        )

    def prepare_application(self, project, change, *, actor, permission):
        """Trusted confirmation service; refs stay in the main application's custody."""
        from ontolearn_engine.project.applications import construct_plan, prepared_payload

        internal, change = self._application_input(project, change, actor, permission)
        with self._application(project, "plan"):
            plan = construct_plan(self, internal, change)
            payload = prepared_payload(project, actor, plan)
            ref = digest(payload)
            base = plan["domain"]["base"] if plan["domain"] else None
            diff = digest(
                {"before": plan["before"], "after": plan["after"], "domain": plan["domain"]}
            )
            self._db.execute(
                "INSERT OR IGNORE INTO job_plans VALUES(?,?,?,?,?,?)",
                (ref, project, base, digest(plan), diff, canonical(payload)),
            )
            confirmation = str(uuid4())
            self._db.execute(
                "INSERT INTO job_confirmations VALUES(?,?,?,?,?,?,?)",
                (confirmation, project, ref, base, digest(plan), actor, permission),
            )
            return {
                "preparedPlanRef": ref,
                "confirmationRef": confirmation,
                "planHash": digest(plan),
                "beforeCAS": plan["beforeCAS"],
                "afterCAS": plan["afterCAS"],
                "applicationBefore": plan["before"],
                "applicationAfter": plan["after"],
                "domain": plan["domain"],
            }

    def apply_application(
        self,
        project,
        operation,
        change,
        *,
        actor,
        permission,
        prepared_plan_ref=None,
        confirmation_ref=None,
        hook: Hook = lambda _: None,
    ):
        """One coordinator-owned non-Job transaction. Never a worker or renderer entry."""
        from ontolearn_engine.project.applications import (
            check_confirmation,
            claim_context,
            construct_plan,
            require,
            stable,
        )
        from ontolearn_engine.project.format3 import receipt_for

        internal, change = self._application_input(project, change, actor, permission)
        if not isinstance(operation, str) or not UUID.fullmatch(operation):
            fault("INVALID_REQUEST", field="identity")
        request = {
            "change": change,
            "authorization": {
                "actor": actor,
                "permission": permission,
                "preparedPlanRef": prepared_plan_ref,
                "confirmationRef": confirmation_ref,
            },
        }
        request = stable(request)
        with self._application(project, "application", hook):
            claim = self._db.execute(
                "SELECT * FROM operation_claims WHERE operation=?", (operation,)
            ).fetchone()
            if claim:
                if claim["kind"] != "application" or claim["project"] != project:
                    fault("IDENTITY_CONFLICT")
                from ontolearn_engine.project.project_lifecycle import creation_context

                if creation_context(self, internal, operation) is not None:
                    fault("IDENTITY_CONFLICT")
                context = claim_context(self, internal, operation)
                if canonical(context["request"]) != canonical(request):
                    fault("IDENTITY_CONFLICT")
                # Original request/CAS succeeds again only by validated immutable
                # evidence. No plan reconstruction or current CAS check on retry.
                return receipt_for(self, internal, operation)
            if self._occupied_operation_evidence(operation):
                fault("IDENTITY_CONFLICT")
            require((prepared_plan_ref is None) == (confirmation_ref is None))
            if prepared_plan_ref is not None:
                from ontolearn_engine.project.applications import hash_ref, uuid_ref

                require(hash_ref(prepared_plan_ref) and uuid_ref(confirmation_ref))
            if prepared_plan_ref is None:
                require("domain" not in change and change["type"] != "draft.restore")
                plan = construct_plan(self, internal, change)
            else:
                row = self._db.execute(
                    "SELECT payload FROM job_plans WHERE ref=? AND project=?",
                    (prepared_plan_ref, project),
                ).fetchone()
                require(row is not None)
                payload = json.loads(row[0])
                require(
                    isinstance(payload, dict)
                    and set(payload) == {"preparedApplicationVersion", "projectId", "actor", "plan"}
                )
                require(
                    type(payload["preparedApplicationVersion"]) is int
                    and payload["preparedApplicationVersion"] == 1
                    and payload["projectId"] == project
                    and payload["actor"] == actor
                )
                plan = payload["plan"]
                require(canonical(plan["change"]) == canonical(change))
            context = {
                "applicationContextVersion": 1,
                "projectId": project,
                "project": internal,
                "operationId": operation,
                "request": request,
                "plan": plan,
            }
            check_confirmation(self, context)
            self._db.execute(
                "INSERT INTO operation_claims(operation,project,job,fingerprint,kind,context) "
                "VALUES(?,?,NULL,?,'application',?)",
                (operation, project, digest(context), canonical(context)),
            )
            hook("application_claim")
            base = plan["domain"]["base"] if plan["domain"] else None
            return super().commit(internal, base, operation, None, application=context, hook=hook)

    def _valid(self, schema, value, field="params"):
        if not self.contract.validate(schema, value):
            fault("INVALID_REQUEST", field=field)

    @contextmanager
    def _application(self, project, resource, hook: Hook = lambda _: None):
        try:
            with self._transaction(hook):
                yield
        except Conflict as error:
            if error.category != "ownership":
                raise
            # Persist only fixed categories and authorized opaque identities,
            # outside the rolled-back write. No exception text/values/paths.
            identity = str(uuid4())
            detail = {"category": "ownership", "resource": resource, "projectId": project}
            with self._transaction():
                self._db.execute(
                    "INSERT INTO job_details VALUES(?,?,?)", (identity, project, canonical(detail))
                )
            fault("OWNERSHIP_CONFLICT", detailRef=identity)

    def detail_get(self, project, identity):
        self._project(project)
        row = self._db.execute(
            "SELECT payload FROM job_details WHERE id=? AND project=?", (identity, project)
        ).fetchone()
        if row is None:
            fault("NOT_FOUND", resource="result")
        return json.loads(row[0])

    def has_operation_claim(self, operation):
        return (
            self._db.execute(
                "SELECT 1 FROM operation_claims WHERE operation=?", (operation,)
            ).fetchone()
            is not None
        )

    def _test_parameters(self, parameters):
        bounds = {
            "workMs": (0, 10000),
            "maxRounds": (1, 1000),
            "consumePerRound": (0, 1000),
            "generatePerRound": (0, 100),
            "crashRound": (1, 1000),
            "failRound": (1, 1000),
            "allocateBytes": (0, 2147483648),
        }
        if not isinstance(parameters, dict) or set(parameters) - (
            bounds.keys() | {"events", "rows"}
        ):
            fault("INVALID_REQUEST", field="config")
        for key, (minimum, maximum) in bounds.items():
            if key in parameters and (
                type(parameters[key]) is not int or not minimum <= parameters[key] <= maximum
            ):
                fault("INVALID_REQUEST", field="config")
        events = parameters.get("events", [])
        if (
            not isinstance(events, list)
            or len(events) > 1000
            or any(not isinstance(e, str) or not 1 <= len(e) <= 128 for e in events)
            or len(set(events)) != len(events)
        ):
            fault("INVALID_REQUEST", field="config")
        if parameters.get("generatePerRound", 0) and any(
            re.fullmatch(r"generated-[0-9]+-[0-9]+", event) for event in events
        ):
            fault("INVALID_REQUEST", field="config")
        rows = parameters.get("rows", [])
        if not isinstance(rows, list) or len(rows) > 10000:
            fault("INVALID_REQUEST", field="config")
        for row in rows:
            self._valid("row", row, "config")

    def create_project(self, project: str) -> None:
        if self._target_format != 3:
            return super().create_project(project)
        # Format3 publishes domain/app genesis and its public identity atomically.
        with self._transaction():
            super().create_project(project)
            self.public_project(project)

    def public_project(self, internal: str) -> str:
        self.revision(internal)
        with self._transaction():
            row = self._db.execute(
                "SELECT public FROM public_projects WHERE internal=?", (internal,)
            ).fetchone()
            if row:
                return row[0]
            public = internal if UUID.fullmatch(internal) else str(uuid4())
            self._db.execute("INSERT INTO public_projects VALUES(?,?)", (public, internal))
            return public

    def _project(self, public):
        if not isinstance(public, str) or not UUID.fullmatch(public):
            fault("INVALID_REQUEST", field="identity")
        row = self._db.execute(
            "SELECT internal FROM public_projects WHERE public=?", (public,)
        ).fetchone()
        if row is None:
            fault("NOT_FOUND", resource="project")
        return row[0]

    def project_get(self, project):
        internal = self._project(project)
        with self._transaction():
            return {
                "projectId": project,
                "projectRevision": self.revision(internal),
                "inputSnapshotId": self.snapshot(internal),
                "dependencyVector": self.vector(internal),
                "formatVersion": self.actual_format,
            }

    def put_blob(self, project, value):
        self._project(project)
        encoded = canonical(value)
        if len(encoded.encode()) > 262144:
            fault("RESOURCE_LIMIT", resource="frame")
        ref = digest(value)
        with self._transaction():
            self._db.execute(
                "INSERT OR IGNORE INTO job_blobs VALUES(?,?,?)", (project, ref, encoded)
            )
        return ref

    def blob(self, project, ref):
        self._project(project)
        row = self._db.execute(
            "SELECT payload FROM job_blobs WHERE project=? AND ref=?", (project, ref)
        ).fetchone()
        if row is None:
            fault("NOT_FOUND", resource="snapshot")
        value = json.loads(row[0])
        if digest(value) != ref:
            fault("INVALID_STATE")
        return value

    @staticmethod
    def _plan(base, plan):
        if not isinstance(plan, dict) or set(plan) - {
            "definitions",
            "remove_definitions",
            "manual",
            "edits",
            "remove",
            "mapping",
        }:
            fault("INVALID_REQUEST", field="params")
        complete = {
            "base": base,
            **{k: plan.get(k) for k in ("definitions", "manual", "edits", "remove", "mapping")},
        }
        if plan.get("remove_definitions") is not None:
            complete["remove_definitions"] = plan["remove_definitions"]
        return complete

    def prepare_plan(self, project, base, plan, *, actor, permission):
        """Trusted confirmation service only; never accepts renderer-issued confirmation IDs.

        Preview applies the actual S1 plan inside a rollback-only savepoint. The
        actor and granted permission must be supplied by the trusted caller.
        """
        internal = self._project(project)
        if not isinstance(actor, str) or not UUID.fullmatch(actor) or permission != "write":
            fault("INVALID_REQUEST", field="identity")
        complete = self._plan(base, plan)
        with self._application(project, "plan"):
            if self.revision(internal) != base:
                fault("REVISION_CONFLICT", expected=base, actual=self.revision(internal))
            before = self.snapshot(internal)
            self._db.execute("SAVEPOINT preview")
            try:
                marker = super().commit(
                    internal,
                    base,
                    str(uuid4()),
                    str(uuid4()),
                    **{k: v for k, v in complete.items() if k != "base"},
                )
                after_state = self.state(internal)
                diff_hash = digest(
                    {"before": self.load_snapshot(before)["state"], "after": after_state}
                )
                if marker["fingerprint"] != digest(complete):
                    fault("INVALID_STATE")
            finally:
                self._db.execute("ROLLBACK TO preview")
                self._db.execute("RELEASE preview")
            ref = digest(
                {"projectId": project, "plan": complete, "before": before, "diffHash": diff_hash}
            )
            confirmation = str(uuid4())
            self._db.execute(
                "INSERT OR IGNORE INTO job_plans VALUES(?,?,?,?,?,?)",
                (ref, project, base, digest(complete), diff_hash, canonical(complete)),
            )
            self._db.execute(
                "INSERT INTO job_confirmations VALUES(?,?,?,?,?,?,?)",
                (confirmation, project, ref, base, digest(complete), actor, permission),
            )
            return {"preparedPlanRef": ref, "confirmationRef": confirmation}

    def preview_changeset(
        self,
        project,
        base,
        request,
        *,
        host_client_id,
        engine_session_id,
        limits,
        hook: Hook = lambda _: None,
    ):
        from ontolearn_engine.project.domain_changesets import preview_changeset

        return preview_changeset(
            self,
            project,
            base,
            request,
            host_client_id=host_client_id,
            engine_session_id=engine_session_id,
            limits=limits,
            hook=hook,
        )

    def changeset_diff_page(
        self,
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
        from ontolearn_engine.project.domain_changesets import diff_page

        return diff_page(
            self,
            project,
            preview_hash,
            document_kind,
            page_size,
            cursor,
            host_client_id=host_client_id,
            engine_session_id=engine_session_id,
            limits=limits,
        )

    def confirm_changeset(
        self,
        project,
        preview_hash,
        completion_cursor,
        *,
        host_client_id,
        engine_session_id,
        hook: Hook = lambda _: None,
    ):
        from ontolearn_engine.project.domain_changesets import confirm

        return confirm(
            self,
            project,
            preview_hash,
            completion_cursor,
            host_client_id=host_client_id,
            engine_session_id=engine_session_id,
            hook=hook,
        )

    def create_changeset_job(
        self,
        project,
        operation,
        input_,
        confirmation_ref,
        implementation,
        limits,
        *,
        host_client_id,
        engine_session_id,
        hook: Hook = lambda _: None,
    ):
        return self.create_job(
            project,
            operation,
            "changeset.commit",
            input_,
            confirmation_ref,
            implementation,
            limits,
            _changeset_host=(host_client_id, engine_session_id),
            _acceptance_hook=hook,
        )

    def _definitions(self, snap):
        output = []
        for d in snap["state"]["definitions"]:
            value = json.loads(d["payload"])
            output.append(
                {
                    "family": d["layer"],
                    "id": d["id"],
                    "version": snap["dependencyVector"].get(f"{d['layer']}:{d['id']}", 0),
                    "references": [
                        f"{r['layer']}:{r['id']}"
                        for r in (value.get("references", []) if isinstance(value, dict) else [])
                    ],
                }
            )
        return output

    def _dependencies(self, capability, input_, snap):
        definitions = self._definitions(snap)
        # Infrastructure probes exercise the conservative ChangeSet dependency
        # policy; they are never registered as product execution capabilities.
        policy = "changeset.commit" if capability.startswith("test.") else capability
        selected = self.contract.derive_dependencies(
            policy,
            input_["definitionId"],
            "asserted" if capability.startswith("test.") else input_["scope"],
            definitions,
        )
        vector = {k: snap["dependencyVector"].get(k, 0) for k in selected["keys"]}
        manifests = {
            family_: [[key, snap["dependencyVector"].get(key, 0)] for key in members]
            for family_, members in selected["sets"].items()
        }
        for identity in input_["derivedResultIds"]:
            result = self.result_get(self.public_project(snap["project"]), identity)
            if (
                result["kind"] != "reasoning"
                or result["inputSnapshotId"] != input_["inputSnapshotId"]
                or result["payloadStatus"] != "available"
            ):
                fault("IDENTITY_CONFLICT")
            vector.update(result["dependencyVector"])
            saved = self._db.execute(
                "SELECT manifests FROM job_results WHERE id=?", (identity,)
            ).fetchone()
            for key, members in json.loads(saved[0]).items():
                if key in manifests and manifests[key] != members:
                    fault("IDENTITY_CONFLICT")
                manifests[key] = members
        return vector, manifests

    def _job_prepared_plan(
        self,
        project,
        input_,
        confirmation_ref,
        snapshot,
        *,
        error="IDENTITY_CONFLICT",
        capability=None,
        changeset_host=None,
    ):
        """Validate the ordinary domain-plan namespace before accepting a Job.

        Application previews share immutable tables, but have a distinct envelope
        and reference derivation. A row's existence is not proof of its type.
        The actor is supplied only by the trusted prepare service; create_job
        has no renderer-issued actor or authority to replace that binding.
        """
        if capability == "changeset.commit":
            from ontolearn_engine.project.domain_changesets import accepted_plan

            try:
                return accepted_plan(
                    self, project, input_, confirmation_ref, snapshot, host=changeset_host
                )
            except JobFault as exc:
                if error == "INVALID_STATE":
                    fault(error)
                raise exc
        row = self._db.execute(
            "SELECT * FROM job_plans WHERE project=? AND ref=?",
            (project, input_["preparedPlanRef"]),
        ).fetchone()
        confirmation = self._db.execute(
            "SELECT * FROM job_confirmations WHERE project=? AND id=?",
            (project, confirmation_ref),
        ).fetchone()
        if row is None or confirmation is None:
            fault(error)
        try:
            plan = json.loads(row["payload"])
            fields = {"base", "definitions", "manual", "edits", "remove", "mapping"}
            if not isinstance(plan, dict) or set(plan) not in (
                fields,
                fields | {"remove_definitions"},
            ):
                fault(error)
            expected = self._plan(
                snapshot["projectRevision"], {k: v for k, v in plan.items() if k != "base"}
            )
            valid = (
                canonical(plan) == canonical(expected)
                and row["plan_hash"] == digest(plan)
                and row["base"] == snapshot["projectRevision"]
                and isinstance(row["diff_hash"], str)
                and re.fullmatch(r"[0-9a-f]{64}", row["diff_hash"]) is not None
                and digest(
                    {
                        "projectId": project,
                        "plan": plan,
                        "before": input_["inputSnapshotId"],
                        "diffHash": row["diff_hash"],
                    }
                )
                == input_["preparedPlanRef"]
                and confirmation["plan_ref"] == row["ref"]
                and confirmation["plan_hash"] == row["plan_hash"]
                and confirmation["base"] == row["base"]
                and isinstance(confirmation["actor"], str)
                and UUID.fullmatch(confirmation["actor"]) is not None
                and confirmation["permission"] == "write"
            )
        except (ValueError, TypeError, KeyError):
            fault(error)
        if not valid:
            fault(error)
        return plan

    def create_job(
        self,
        project,
        operation,
        capability,
        input_,
        confirmation_ref,
        implementation,
        limits,
        *,
        _changeset_host=None,
        _acceptance_hook: Hook = lambda _: None,
    ):
        self._valid(
            "params_job.create",
            {
                "projectId": project,
                "operationId": operation,
                "capability": capability,
                "input": input_,
                "confirmationRef": confirmation_ref,
            },
        )
        self._valid("implementation", implementation)
        self._valid("limits", limits)
        internal = self._project(project)
        with self._transaction(_acceptance_hook):
            claim = self._db.execute(
                "SELECT * FROM operation_claims WHERE operation=?", (operation,)
            ).fetchone()
            if claim:
                return self._accepted_job(
                    claim, project, capability, input_, confirmation_ref, implementation, limits
                )
            if self._target_format == 3 and self._occupied_operation_evidence(operation):
                fault("IDENTITY_CONFLICT")
            snap = self._project_snapshot(input_["inputSnapshotId"], internal)
            parameters = self.blob(project, input_["parametersHash"])
            query_request = None
            if capability == "query.execute":
                query_request = self.prepare_query_request(
                    project, input_, parameters, snap, implementation, confirmation_ref
                )
            if capability.startswith("test."):
                self._test_parameters(parameters)
            vector, manifests = self._dependencies(capability, input_, snap)
            for derived in input_["derivedResultIds"]:
                result = self.result_get(project, derived)
                if result["implementation"] != implementation:
                    fault("IDENTITY_CONFLICT")
            writing = capability in {"test.atomic", "changeset.commit", "mapping.commit"}
            if writing:
                if capability == "changeset.commit" and _changeset_host is None:
                    fault("IDENTITY_CONFLICT")
                plan = self._job_prepared_plan(
                    project,
                    input_,
                    confirmation_ref,
                    snap,
                    capability=capability,
                    changeset_host=_changeset_host,
                )
            else:
                if input_["preparedPlanRef"] is not None or confirmation_ref is not None:
                    fault("INVALID_REQUEST", field="identity")
                plan = None
            context = {
                "input": input_,
                "confirmationRef": confirmation_ref,
                "parameters": parameters,
                "snapshot": snap,
                "plan": plan,
                "projectId": project,
                "capability": capability,
                "implementation": implementation,
                "limits": limits,
                "dependencyVector": vector,
                "manifests": manifests,
            }
            if query_request is not None:
                context["queryRequest"] = query_request
            if capability == "test.rounds":
                events = parameters.get("events", [])
                context["runConfig"] = {
                    "maxRounds": parameters.get("maxRounds", 1),
                    "maxActionsPerRound": 1000,
                    "parameters": parameters,
                    "events": events,
                    "parametersRef": input_["parametersHash"],
                    "eventsRef": self.put_blob(project, events),
                    "initialSnapshotId": input_["inputSnapshotId"],
                    "eventConsumptionRef": self.put_blob(
                        project, {"inputEvents": events, "consumedEvents": []}
                    ),
                    "ruleVersions": {k: v for k, v in vector.items() if k.startswith("rule:")},
                    "behaviorVersions": {
                        k: v for k, v in vector.items() if k.startswith("behavior:")
                    },
                    "semantics": "I04-test-rounds-v1",
                    "roundOrder": "consume-input-queue>generate-next-round-events>commit",
                    "triggerOrder": "input-ordinal:asc",
                }
            fingerprint = digest(context)
            identity = str(uuid4())
            now = self.now_ms()
            mode = (
                "atomic"
                if writing
                else ("rounds" if capability in {"test.rounds", "scenario.run"} else "none")
            )
            progress = {"mode": mode}
            if mode == "atomic":
                progress.update(operationId=operation, marker=None)
            if mode == "rounds":
                progress["committedProgress"] = None
            job = {
                "jobId": identity,
                "projectId": project,
                "operationId": operation,
                "capability": capability,
                "inputSnapshotId": input_["inputSnapshotId"],
                "dependencyVector": vector,
                "definitionSetDigests": {k: digest(v) for k, v in manifests.items()},
                "parametersHash": input_["parametersHash"],
                "scope": input_["scope"],
                "implementation": implementation,
                "state": "queued",
                "stateVersion": 1,
                "limits": limits,
                "commitProgress": progress,
                "resultRef": None,
                "error": None,
                "createdAtMs": now,
                "updatedAtMs": now,
                "finishedAtMs": None,
                "input": input_,
                "confirmationRef": confirmation_ref,
            }
            self._valid("job", job)
            self._db.execute(
                "INSERT INTO jobs VALUES(?,?,?,?,?,?,NULL)",
                (
                    identity,
                    project,
                    operation,
                    canonical(job),
                    canonical(context),
                    fingerprint,
                ),
            )
            if capability == "changeset.commit":
                _acceptance_hook("changeset_queued")
            if self._target_format == 3:
                self._db.execute(
                    "INSERT INTO operation_claims(operation,project,job,fingerprint,kind,context) "
                    "VALUES(?,?,?,?,'job',NULL)",
                    (operation, project, identity, fingerprint),
                )
            else:
                self._db.execute(
                    "INSERT INTO operation_claims(operation,project,job,fingerprint) "
                    "VALUES(?,?,?,?)",
                    (operation, project, identity, fingerprint),
                )
            if capability == "changeset.commit":
                _acceptance_hook("changeset_claim")
            return job

    def _accepted_job(
        self, claim, project, capability, input_, confirmation_ref, implementation, limits
    ):
        """Read an existing acceptance, independent of mutable current/cache state.

        The full frozen context remains content-verified; only the original
        accepted source's present payload availability/currentness is irrelevant.
        New operations still use all normal live-reference validation above.
        """
        if claim["project"] != project or (self._target_format == 3 and claim["kind"] != "job"):
            fault("IDENTITY_CONFLICT")
        row = self._db.execute("SELECT * FROM jobs WHERE id=?", (claim["job"],)).fetchone()
        if row is None:
            fault("INVALID_STATE")
        context = json.loads(row["context"])
        if (
            digest(context) != claim["fingerprint"]
            or row["fingerprint"] != claim["fingerprint"]
            or row["project"] != project
            or row["operation"] != claim["operation"]
        ):
            fault("INVALID_STATE")
        supplied = {
            "projectId": project,
            "capability": capability,
            "input": input_,
            "confirmationRef": confirmation_ref,
            "implementation": implementation,
            "limits": limits,
        }
        if any(canonical(context.get(key)) != canonical(value) for key, value in supplied.items()):
            fault("IDENTITY_CONFLICT")
        snapshot = self._project_snapshot(input_["inputSnapshotId"], self._project(project))
        if snapshot != context["snapshot"]:
            fault("INVALID_STATE")
        parameters = self.blob(project, input_["parametersHash"])
        if parameters != context["parameters"] or digest(parameters) != input_["parametersHash"]:
            fault("INVALID_STATE")
        if "queryRequest" in context:
            expected = self.prepare_query_request(
                project, input_, parameters, snapshot, implementation, confirmation_ref, live=False
            )
            if context["queryRequest"] != expected:
                fault("INVALID_STATE")
        if "runConfig" in context:
            config = context["runConfig"]
            if (
                config["parameters"] != parameters
                or config["parametersRef"] != input_["parametersHash"]
                or config["initialSnapshotId"] != input_["inputSnapshotId"]
                or self.blob(project, config["eventsRef"]) != config["events"]
                or digest(config["events"]) != config["eventsRef"]
                or self.blob(project, config["eventConsumptionRef"])
                != {"inputEvents": config["events"], "consumedEvents": []}
            ):
                fault("INVALID_STATE")
        if input_["preparedPlanRef"] is not None:
            plan = self._job_prepared_plan(
                project,
                input_,
                confirmation_ref,
                snapshot,
                error="INVALID_STATE",
                capability=capability,
            )
            if canonical(plan) != canonical(context["plan"]):
                fault("INVALID_STATE")
        elif context["plan"] is not None or confirmation_ref is not None:
            fault("INVALID_STATE")
        return self.get_job(project, claim["job"])

    def get_job(self, project, identity):
        self._project(project)
        row = self._db.execute("SELECT * FROM jobs WHERE id=?", (identity,)).fetchone()
        if row is None or row["project"] != project:
            fault("NOT_FOUND", resource="job")
        job = json.loads(row["dto"])
        context = json.loads(row["context"])
        if (
            digest(context) != row["fingerprint"]
            or job["jobId"] != identity
            or job["operationId"] != row["operation"]
            or any(
                job[key] != context[key]
                for key in (
                    "projectId",
                    "capability",
                    "input",
                    "confirmationRef",
                    "implementation",
                    "limits",
                    "dependencyVector",
                )
            )
        ):
            fault("INVALID_STATE")
        self._valid("job", job)
        return job

    def job_context(self, identity):
        row = self._db.execute("SELECT context,fingerprint FROM jobs WHERE id=?", (identity,))
        row = row.fetchone()
        if row is None:
            fault("NOT_FOUND", resource="job")
        context = json.loads(row["context"])
        if digest(context) != row["fingerprint"]:
            fault("INVALID_STATE")
        job = self._job(identity)
        context["job"] = job
        return context

    def _job(self, identity):
        row = self._db.execute("SELECT project FROM jobs WHERE id=?", (identity,)).fetchone()
        if row is None:
            fault("NOT_FOUND", resource="job")
        return self.get_job(row[0], identity)

    def _save(self, job):
        self._valid("job", job)
        self._db.execute("UPDATE jobs SET dto=? WHERE id=?", (canonical(job), job["jobId"]))
        return job

    def _transition(self, job, state, *, result=None, error=None):
        if not self.contract.permits_transition(
            job["state"], state, job["stateVersion"], job["stateVersion"] + 1, False
        ):
            fault("INVALID_STATE")
        now = max(self.now_ms(), job["updatedAtMs"])
        job.update(
            state=state,
            stateVersion=job["stateVersion"] + 1,
            updatedAtMs=now,
            finishedAtMs=now if state in TERMINAL else None,
            resultRef=result,
            error=error,
        )
        return self._save(job)

    def start_job(self, identity):
        with self._transaction():
            return self._transition(self._job(identity), "running")

    def cancel_job(self, project, identity):
        with self._transaction():
            job = self.get_job(project, identity)
            state = job["state"]
            decision_version = job["stateVersion"]
            disposition = "accepted"
            if state in TERMINAL:
                disposition = "alreadyTerminal"
            elif state == "cancelling":
                disposition = "alreadyRequested"
            else:
                self._transition(job, "cancelled" if state == "queued" else "cancelling")
            return {
                "jobId": identity,
                "disposition": disposition,
                # Accepted queued cancellation reports the decision snapshot,
                # not a promised terminal outcome. get/subscribe observes the
                # atomically persisted cancelled version. This also preserves
                # the canonical alreadyTerminal iff terminal response rule.
                "state": "queued" if state == "queued" else job["state"],
                "stateVersion": decision_version if state == "queued" else job["stateVersion"],
            }

    def fail_job(self, identity, error):
        self._valid("error", error)
        with self._transaction():
            job = self._job(identity)
            if job["state"] in TERMINAL:
                return job
            return self._finish_unsuccessful(job, "failed", error)

    def cancelled_job(self, identity):
        with self._transaction():
            job = self._job(identity)
            if job["state"] in TERMINAL:
                return job
            return self._finish_unsuccessful(job, "cancelled", None)

    def _finish_unsuccessful(self, job, state, error):
        run = self._db.execute("SELECT run FROM jobs WHERE id=?", (job["jobId"],)).fetchone()[0]
        if run:
            self._finish_run_once(
                run, state, {"jobId": job["jobId"], "committedProgress": self.progress(run)}
            )
            job["commitProgress"]["committedProgress"] = self.progress(run)
        marker = self.marker(self._project(job["projectId"]), job["operationId"])
        if marker and job["commitProgress"]["mode"] == "atomic":
            job["commitProgress"]["marker"] = self._marker_dto(marker)
        return self._transition(job, state, error=error)

    @staticmethod
    def _marker_dto(marker):
        return {
            "projectRevision": marker["revision"],
            "beforeSnapshotId": marker["before_snapshot"],
            "afterSnapshotId": marker["after_snapshot"],
            "planHash": marker["fingerprint"],
        }

    def operation_get(self, project, operation):
        internal = self._project(project)
        claim = self._db.execute(
            "SELECT project FROM operation_claims WHERE operation=?", (operation,)
        ).fetchone()
        if claim and claim[0] != project:
            fault("NOT_FOUND", resource="operation")
        marker = self.marker(internal, operation)
        if marker is None:
            return None
        return {
            "projectId": project,
            "operationId": operation,
            "jobId": marker["job"],
            **self._marker_dto(marker),
        }

    def commit_job(self, identity, hook: Hook = lambda _: None):
        with self._application(self._job(identity)["projectId"], "commit", hook):
            job = self._job(identity)
            if job["state"] in TERMINAL:
                return job
            if job["state"] != "running" or job["commitProgress"]["mode"] != "atomic":
                fault("INVALID_STATE")
            context = self.job_context(identity)
            plan = context["plan"]
            internal = self._project(job["projectId"])
            if job["capability"] == "changeset.commit":
                from ontolearn_engine.project.domain_changesets import commit

                marker = commit(self, job, context, hook)
            elif self.revision(internal) != plan["base"]:
                fault("REVISION_CONFLICT", expected=plan["base"], actual=self.revision(internal))
            else:
                marker = super().commit(
                    internal,
                    plan["base"],
                    job["operationId"],
                    identity,
                    hook=hook,
                    **{k: v for k, v in plan.items() if k != "base"},
                )
            job["commitProgress"]["marker"] = self._marker_dto(marker)
            rows = [
                {
                    "rowId": str(uuid4()),
                    "ordinal": 0,
                    "cells": [
                        "commit.receipt.v1",
                        job["operationId"],
                        marker["revision"],
                        marker["before_snapshot"],
                        marker["after_snapshot"],
                        marker["fingerprint"],
                    ],
                }
            ]
            result = self._publish_job(job, rows, "receipt")
            if job["capability"] == "changeset.commit":
                hook("changeset_result")
            self._transition(job, "succeeded", result=result)
            hook("mid_job_terminal")
        return self._job(identity)

    def finish_read_job(self, identity, rows, kind="test", hook: Hook = lambda _: None):
        with self._transaction(hook):
            job = self._job(identity)
            if job["state"] in TERMINAL:
                return job
            if job["state"] != "running" or job["commitProgress"]["mode"] != "none":
                fault("INVALID_STATE")
            if job["capability"] == "query.execute":
                fault("INVALID_STATE")  # New query success requires the complete private bundle.
            result = self._publish_job(job, rows, kind)
            self._transition(job, "succeeded", result=result)
            hook("mid_job_terminal")
        return self._job(identity)

    def prepare_query_request(
        self, project, input_, parameters, snap, implementation, confirmation_ref, *, live=True
    ):
        from ontolearn_engine.resources import semantic_identity
        from ontolearn_engine.semantic_execution import SemanticExecutionFault, build_request
        from ontolearn_engine.worker import query_encode, query_transport_limits

        if type(parameters) is not dict or set(parameters) != {"inputSelection"}:
            fault("INVALID_REQUEST", field="params")
        if parameters["inputSelection"] not in ("current", "historical"):
            fault("INVALID_REQUEST", field="params")
        if (
            input_["scope"] != "asserted"
            or input_["derivedResultIds"]
            or input_["preparedPlanRef"] is not None
            or confirmation_ref is not None
        ):
            fault("INVALID_REQUEST", field="identity")
        if live and implementation != semantic_identity():
            fault("IDENTITY_CONFLICT")
        if implementation["executionSemanticsVersion"] != "i05-finite-6":
            fault("IDENTITY_CONFLICT")
        if not any(
            d["layer"] == "query" and d["id"] == input_["definitionId"]
            for d in snap["state"]["definitions"]
        ):
            fault("INVALID_REQUEST", field="dependency")
        if (
            live
            and parameters["inputSelection"] == "current"
            and input_["inputSnapshotId"] != self.snapshot(self._project(project))
        ):
            fault("IDENTITY_CONFLICT")
        try:
            request = build_request(
                snap,
                "query.execute",
                input_,
                parameters,
                error_catalog=self.contract.ERROR_CATALOG,
                error_schema=self.contract.DOCUMENT,
            )
            from ontolearn_engine.resources import LIMITS

            _, maximum = query_transport_limits(LIMITS)
            query_encode(request, maximum)
            return request
        except SemanticExecutionFault as error:
            raise JobFault(error.error["code"], error.error["params"]) from None

    def _query_payload_binding(self, job, payload, rows):
        """Authenticate accepted source and complete output, without re-running SPARQL."""
        from ontolearn_engine.semantic_execution import _rows, _term

        context = self.job_context(job["jobId"])
        claim = self._db.execute(
            "SELECT * FROM operation_claims WHERE operation=?", (job["operationId"],)
        ).fetchone()
        if claim is None or claim["job"] != job["jobId"]:
            fault("INVALID_STATE")
        self._accepted_job(
            claim,
            job["projectId"],
            job["capability"],
            job["input"],
            job["confirmationRef"],
            job["implementation"],
            job["limits"],
        )
        request = context.get("queryRequest")
        if request is None:
            fault("UNSUPPORTED_CAPABILITY")  # Explicit legacy no-complete-payload distinction.
        expected = self.prepare_query_request(
            job["projectId"],
            job["input"],
            context["parameters"],
            context["snapshot"],
            job["implementation"],
            job["confirmationRef"],
            live=False,
        )
        if request != expected:
            fault("INVALID_STATE")
        query_text = next(
            json.loads(d["payload"])["text"]
            for d in context["snapshot"]["state"]["definitions"]
            if d["layer"] == "query" and d["id"] == job["input"]["definitionId"]
        )
        common = {
            "kind": "query",
            "inputSnapshotId": job["inputSnapshotId"],
            "inputProjectRevision": context["snapshot"]["projectRevision"],
            "executionSemanticsVersion": job["implementation"]["executionSemanticsVersion"],
            "scope": "asserted",
            "definitionId": job["input"]["definitionId"],
            "inputSelection": context["parameters"]["inputSelection"],
            "selectedResultIds": [],
            "queryText": query_text,
        }
        if type(payload) is not dict or set(payload) != set(common) | {"query", "provenance"}:
            fault("INVALID_STATE")
        if any(payload[k] != v for k, v in common.items()):
            fault("INVALID_STATE")
        query = payload["query"]
        if type(query) is not dict:
            fault("INVALID_STATE")
        if query.get("type") == "ASK":
            if set(query) != {"type", "value"} or type(query["value"]) is not bool:
                fault("INVALID_STATE")
        elif query.get("type") == "SELECT":
            if (
                set(query) != {"type", "variables", "rows"}
                or type(query["variables"]) is not list
                or any(type(v) is not str for v in query["variables"])
                or len(set(query["variables"])) != len(query["variables"])
                or type(query["rows"]) is not list
                or any(
                    type(r) is not list
                    or len(r) != len(query["variables"])
                    or any(v is not None and type(v) is not str for v in r)
                    for r in query["rows"]
                )
            ):
                fault("INVALID_STATE")
        else:
            fault("INVALID_STATE")
        state = context["snapshot"]["state"]

        # Only bounded RDF term canonicalization for binding; never execute the
        # query (or invoke execute_request) again in the Store/coordinator.
        def triple(record):
            return [
                f"<{record['subject']}>",
                f"<{record['predicate']}>",
                _term(record["object"]).n3(),
            ]

        facts = sorted({tuple(triple(r)) for r in state["facts"] if r["object"] is not None})
        ontology = sorted(
            {
                tuple(triple(r))
                for d in state["definitions"]
                if d["layer"] == "ontology"
                for r in json.loads(d["payload"])["triples"]
            }
        )
        facts, ontology = [list(t) for t in facts], [list(t) for t in ontology]
        expected_provenance = {
            "scope": "asserted",
            "executionSemanticsVersion": common["executionSemanticsVersion"],
            "assertedInputSha256": digest(facts),
            "ontologyInputSha256": digest(ontology),
            "selectedRulesSha256": digest([]),
            "reasoningSource": None,
            "selectedRuleIds": [],
            "warnings": [],
            "selectedFacts": [{"triple": t, "sources": [{"kind": "asserted"}]} for t in facts],
            "derivedAxioms": [],
            "ontologyView": ontology,
            "factViewSha256": digest(facts),
            "ontologyViewSha256": digest(ontology),
        }
        if payload["provenance"] != expected_provenance:
            fault("INVALID_STATE")
        # Fixed supplier projection is pure JSON walking, not graph/query execution.
        projected = _rows(payload)
        if (
            type(rows) is not list
            or len(rows) != len(projected)
            or any(
                not self.contract.validate("row", row)
                or row["ordinal"] != expected_row["ordinal"]
                or row["cells"] != expected_row["cells"]
                for row, expected_row in zip(rows, projected, strict=True)
            )
        ):
            fault("INVALID_STATE")

    def finish_query_job(self, identity, output, hook: Hook = lambda _: None):
        from ontolearn_engine.worker import query_encode, query_transport_limits

        with self._transaction(hook):
            job = self._job(identity)
            if job["state"] in TERMINAL:
                return job
            if job["state"] != "running" or job["capability"] != "query.execute":
                fault("INVALID_STATE")
            if type(output) is not dict or set(output) != {"payload", "rows"}:
                fault("INVALID_STATE")
            _, maximum = query_transport_limits(job["limits"])
            query_encode(output, maximum)
            self._query_payload_binding(job, output["payload"], output["rows"])
            result = self._publish_job(job, output["rows"], "query")
            hook("query_rows_published")
            self._db.execute(
                "INSERT INTO query_payloads VALUES(?,?,?,?)",
                (
                    result["resultId"],
                    canonical(output["payload"]),
                    digest(output["payload"]),
                    digest(output["rows"]),
                ),
            )
            hook("query_payload_published")
            self._transition(job, "succeeded", result=result)
            hook("mid_job_terminal")
        return self._job(identity)

    def semantic_result(self, project, identity):
        """Internal full query material; public metadata/page schemas are unchanged."""
        with self._read():
            metadata = self.result_get(project, identity)
            if metadata["kind"] != "query":
                fault("UNSUPPORTED_CAPABILITY")
            if metadata["payloadStatus"] != "available":
                fault("PAYLOAD_EVICTED", resultId=identity)
            job = self.get_job(project, metadata["jobId"])
            if self._db.execute(
                "SELECT 1 FROM query_legacy_jobs WHERE job=?", (job["jobId"],)
            ).fetchone():
                fault("UNSUPPORTED_CAPABILITY")
            record = self._db.execute(
                "SELECT * FROM query_payloads WHERE result=?", (identity,)
            ).fetchone()
            if record is None or record["payload"] is None:
                fault("INVALID_STATE")
            payload = json.loads(record["payload"])
            rows = self.result(identity)["payload"]
            if (
                digest(payload) != record["payload_hash"]
                or digest(rows) != record["rows_hash"]
                or job["state"] != "succeeded"
                or job["capability"] != "query.execute"
                or job["resultRef"]
                != {"resultId": identity, "inputSnapshotId": metadata["inputSnapshotId"]}
                or any(
                    job[k] != metadata[k]
                    for k in (
                        "inputSnapshotId",
                        "implementation",
                        "dependencyVector",
                        "definitionSetDigests",
                        "parametersHash",
                        "scope",
                    )
                )
                or job["input"]["definitionId"] != metadata["definitionId"]
            ):
                fault("INVALID_STATE")
            self._query_payload_binding(job, payload, rows)
            return metadata, payload

    def start_job_run(self, identity, config):
        with self._transaction():
            job = self._job(identity)
            if job["state"] != "running" or job["commitProgress"]["mode"] != "rounds":
                fault("INVALID_STATE")
            prior = self._db.execute("SELECT run FROM jobs WHERE id=?", (identity,)).fetchone()[0]
            if prior:
                if json.loads(self._run(prior)["config"]) != config:
                    fault("IDENTITY_CONFLICT")
                return prior
            if not isinstance(config, dict) or type(config.get("maxRounds")) is not int:
                fault("INVALID_REQUEST", field="config")
            if not 1 <= config["maxRounds"] <= 1000:
                fault("INVALID_REQUEST", field="config")
            if (
                job["capability"] == "test.rounds"
                and config != self.job_context(identity)["runConfig"]
            ):
                fault("IDENTITY_CONFLICT")
            # Config is a frozen, content-addressed trusted infrastructure input.
            # It describes test rounds, not a claimed Appendix E domain executor.
            self.put_blob(job["projectId"], config)
            run = super().start_run(
                self._project(job["projectId"]),
                job["inputSnapshotId"],
                config,
                job["implementation"],
            )
            self._db.execute("UPDATE jobs SET run=? WHERE id=?", (run, identity))
            return run

    def commit_job_round(self, identity, state, hook: Hook = lambda _: None):
        with self._transaction(hook):
            job = self._job(identity)
            if job["state"] != "running" or job["commitProgress"]["mode"] != "rounds":
                fault("INVALID_STATE")
            run = self._db.execute("SELECT run FROM jobs WHERE id=?", (identity,)).fetchone()[0]
            if run is None:
                fault("INVALID_STATE")
            progress = self.progress(run)
            number = progress["lastCommittedRound"] + 1 if progress else 1
            if job["capability"] == "test.rounds":
                parameters = self.job_context(identity)["parameters"]
                initial = parameters.get("events", [])
                previous = (
                    self.load_snapshot(progress["snapshotRef"])["state"]
                    if progress
                    else {"pendingEvents": initial, "consumedEvents": [], "inputEvents": initial}
                )
                pending = previous["pendingEvents"]
                take = min(len(pending), parameters.get("consumePerRound", len(pending)))
                expected = {
                    "pendingEvents": pending[take:]
                    + [
                        f"generated-{number}-{i}"
                        for i in range(parameters.get("generatePerRound", 0))
                    ],
                    "consumedEvents": previous["consumedEvents"] + pending[:take],
                    "inputEvents": initial,
                }
                if state != expected:
                    fault("IDENTITY_CONFLICT")
            snapshot = super().commit_round(run, number, state, str(uuid4()), identity, hook)
            job["commitProgress"]["committedProgress"] = self.progress(run)
            # A durable running-progress version is distinct from a transient
            # percentage notification. Subscribers apply its next exact version.
            # _transition owns state-name edges; the running/rounds guard above
            # permits this evidence revision within the same nonterminal state.
            job["stateVersion"] += 1
            job["updatedAtMs"] = max(self.now_ms(), job["updatedAtMs"])
            self._save(job)
            hook("mid_job_progress")
        return snapshot

    def _finish_run_once(self, run, state, evidence):
        previous = self._db.execute("SELECT * FROM run_terminal WHERE run=?", (run,)).fetchone()
        if previous:
            if previous["status"] != state or previous["evidence"] != canonical(evidence):
                fault("INVALID_STATE")
            return
        super().finish_run(run, state, evidence)

    def finish_job_run(
        self, identity, *, pending_events, event_consumption, hook: Hook = lambda _: None
    ):
        with self._transaction(hook):
            job = self._job(identity)
            if job["state"] in TERMINAL:
                return job
            if job["state"] != "running":
                fault("INVALID_STATE")
            run = self._db.execute("SELECT run FROM jobs WHERE id=?", (identity,)).fetchone()[0]
            if run is None:
                fault("INVALID_STATE")
            progress = self.progress(run)
            config = json.loads(self._run(run)["config"])
            if not progress or progress["lastCommittedRound"] != config["maxRounds"]:
                fault("INVALID_STATE")
            # Never trust an independently supplied count or summary. Both the
            # queue and consumption records must equal the last committed state.
            state = self.load_snapshot(progress["snapshotRef"])["state"]
            if (
                not isinstance(pending_events, list)
                or not isinstance(event_consumption, list)
                or state.get("pendingEvents") != pending_events
                or state.get("consumedEvents") != event_consumption
            ):
                fault("IDENTITY_CONFLICT")
            consumption = self.put_blob(
                job["projectId"],
                {
                    "runId": run,
                    "inputSnapshotId": job["inputSnapshotId"],
                    "parametersHash": job["parametersHash"],
                    "config": config,
                    "eventConsumption": event_consumption,
                },
            )
            evidence = {
                "jobId": identity,
                **progress,
                "reachedMaxRounds": True,
                "pendingEventCount": len(pending_events),
                "eventConsumptionRef": consumption,
            }
            self._finish_run_once(run, "succeeded", evidence)
            rows = [
                {
                    "rowId": str(uuid4()),
                    "ordinal": 0,
                    "cells": [
                        "run.summary.v1",
                        run,
                        progress["lastCommittedRound"],
                        progress["snapshotRef"],
                        True,
                        bool(pending_events),
                        len(pending_events),
                        consumption,
                    ],
                }
            ]
            # The audit is read from the actual immutable round ledger. Its
            # rows make the infrastructure result genuinely pageable without
            # inventing business metrics, work orders, or execution phases.
            for committed in self.history(run)["rounds"]:
                rows.append(
                    {
                        "rowId": str(uuid4()),
                        "ordinal": committed["number"],
                        "cells": self._round_audit_cells(run, identity, committed),
                    }
                )
            result = self._publish_job(job, rows, "scenario")
            self._transition(job, "succeeded", result=result)
            hook("mid_job_terminal")
        return self._job(identity)

    def reconcile_jobs(self):
        """Call only after acquiring this store's lifetime OS writer lease.

        No worker holds the DB. A previous coordinator cannot still commit via
        this application service after this lease is acquired. BEGIN IMMEDIATE
        obtains the SQLite write sequence before inspecting marker evidence.
        """
        recovered = []
        with self._transaction():
            for row in self._db.execute("SELECT id FROM jobs").fetchall():
                job = self._job(row[0])
                if job["state"] in TERMINAL:
                    continue
                # Atomic completion is committed in the same transaction as its
                # receipt and terminal; marker alone can never invent success.
                state = "cancelled" if job["state"] == "cancelling" else "failed"
                if state == "cancelled":
                    self._finish_unsuccessful(job, state, None)
                else:
                    error = {
                        "code": "ENGINE_EXITED",
                        "messageKey": "engine.exited",
                        "params": {},
                        "retryable": True,
                    }
                    self._finish_unsuccessful(job, state, error)
                recovered.append(job)
        return recovered

    def _set_reasons(self, vector, manifests, internal):
        now = self.vector(internal)
        expanded = dict(vector)
        for category, members in manifests.items():
            old = dict(members)
            new = {
                f"{r['layer']}:{r['id']}": now.get(f"{r['layer']}:{r['id']}", 0)
                for r in self.state(internal)["definitions"]
                if r["layer"] == category
            }
            for key in old.keys() | new.keys():
                expanded.setdefault(key, old.get(key, 0))
                # Set membership is authoritative even if old counters/source
                # provenance remain in the history ledger.
                now[key] = new.get(key, 0)
        return reasons(expanded, now)

    def _invalidate(self, project):
        super()._invalidate(project)
        # First S1 initialization predates the S2 tables.
        if not self._db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='job_results'"
        ).fetchone():
            return
        for row in self._db.execute(
            "SELECT jr.id,jr.manifests,r.dependencies,r.kind FROM job_results jr "
            "JOIN results r ON r.id=jr.id WHERE r.project=?",
            (project,),
        ).fetchall():
            stale = (
                []
                if row["kind"] == "receipt"
                else self._set_reasons(
                    json.loads(row["dependencies"]), json.loads(row["manifests"]), project
                )
            )
            self._db.execute(
                "UPDATE result_state SET stale=? WHERE result=?", (canonical(stale), row["id"])
            )
            if stale:
                self._db.execute("DELETE FROM current_results WHERE result=?", (row["id"],))
                self._db.execute("DELETE FROM job_current WHERE result=?", (row["id"],))

    def _publish_job(self, job, rows, kind):
        if kind not in PUBLIC_KINDS:
            fault("INVALID_REQUEST", field="kind")
        expected_kind = {
            "test.read": "test",
            "test.atomic": "receipt",
            "test.rounds": "scenario",
            "query.execute": "query",
            "reasoning.execute": "reasoning",
            "validation.execute": "validation",
            "behavior.test": "behavior",
            "scenario.run": "scenario",
            "mapping.commit": "receipt",
            "changeset.commit": "receipt",
        }.get(job["capability"])
        if kind != expected_kind:
            fault("INVALID_REQUEST", field="kind")
        if (
            not isinstance(rows, list)
            or len(rows) > 10000
            or len(canonical(rows).encode()) > 8388608
        ):
            fault("RESOURCE_LIMIT", resource="memory")
        keys = set()
        ids = set()
        for row in rows:
            self._valid("row", row)
            if row["rowId"] in ids or row["ordinal"] in keys:
                fault("INVALID_REQUEST", field="identity")
            ids.add(row["rowId"])
            keys.add(row["ordinal"])
        rows = sorted(rows, key=lambda r: (r["ordinal"], r["rowId"]))
        context = self.job_context(job["jobId"])
        internal = self._project(job["projectId"])
        identity = super().publish(
            internal,
            job["inputSnapshotId"],
            sorted(job["dependencyVector"]),
            kind,
            rows,
            job["implementation"],
        )
        self._db.execute(
            "INSERT INTO job_results VALUES(?,?,?,?,?)",
            (
                identity,
                job["jobId"],
                canonical(context["manifests"]),
                canonical(
                    {
                        "definitionId": job["input"]["definitionId"],
                        "scope": job["scope"],
                        "parametersHash": job["parametersHash"],
                    }
                ),
                self.now_ms(),
            ),
        )
        stale = (
            []
            if kind == "receipt"
            else self._set_reasons(job["dependencyVector"], context["manifests"], internal)
        )
        self._db.execute(
            "UPDATE result_state SET stale=? WHERE result=?", (canonical(stale), identity)
        )
        # A receipt can never become a domain current result. S1's older coarse
        # pointer is also removed; public current is keyed by the full identity.
        self._db.execute("DELETE FROM current_results WHERE result=?", (identity,))
        if (
            kind != "receipt"
            and not stale
            and context["snapshot"]["projectRevision"] == self.revision(internal)
        ):
            self._db.execute(
                "INSERT OR REPLACE INTO job_current VALUES(?,?)",
                (
                    self._current_key(
                        job["projectId"],
                        kind,
                        job["input"]["definitionId"],
                        job["scope"],
                        job["parametersHash"],
                        job["implementation"],
                    ),
                    identity,
                ),
            )
        return {"resultId": identity, "inputSnapshotId": job["inputSnapshotId"]}

    @staticmethod
    def _current_key(project, kind, definition, scope, parameters, implementation):
        return canonical([project, kind, definition, scope, parameters, implementation])

    def result_get(self, project, identity):
        internal = self._project(project)
        row = self._db.execute("SELECT * FROM job_results WHERE id=?", (identity,)).fetchone()
        if row is None:
            fault("NOT_FOUND", resource="result")
        saved = self.result(identity)
        if saved["project"] != internal or saved["kind"] not in PUBLIC_KINDS:
            fault("NOT_FOUND", resource="result")
        job = self.get_job(project, row["job"])
        projection = json.loads(row["projection"])
        is_current = (
            self._db.execute("SELECT 1 FROM job_current WHERE result=?", (identity,)).fetchone()
            is not None
        )
        state = "stale" if saved["stale"] else ("current" if is_current else "historical")
        dto = {
            "resultId": identity,
            "projectId": project,
            "jobId": job["jobId"],
            "kind": saved["kind"],
            **projection,
            "inputSnapshotId": saved["snapshot"],
            "inputProjectRevision": self._project_snapshot(saved["snapshot"], internal)[
                "projectRevision"
            ],
            "dependencyVector": saved["dependencies"],
            "definitionSetDigests": {k: digest(v) for k, v in json.loads(row["manifests"]).items()},
            "implementation": saved["implementation"],
            "state": state,
            "staleReason": saved["stale"],
            "payloadStatus": "evicted" if saved["payload"] is None else "available",
            "createdAtMs": row["created"],
            "historicalSelectionRequired": state != "current",
        }
        self._valid("result", dto)
        return dto

    def result_current(self, project, kind, definition_id, scope, parameters_hash, implementation):
        definition, parameters = definition_id, parameters_hash
        self._project(project)
        if kind not in PUBLIC_KINDS:
            fault("INVALID_REQUEST", field="kind")
        self._valid(
            "params_result.current",
            {
                "projectId": project,
                "kind": kind,
                "definitionId": definition,
                "scope": scope,
                "parametersHash": parameters,
                "implementation": implementation,
            },
        )
        row = self._db.execute(
            "SELECT result FROM job_current WHERE key=?",
            (self._current_key(project, kind, definition, scope, parameters, implementation),),
        ).fetchone()
        if row is None:
            return None
        result = self.result_get(project, row[0])
        return result if result["payloadStatus"] == "available" else None

    def _projection_room(self):
        # Expired tokens remain identifiable in the bounded store until pressure
        # needs their space; callers can distinguish expiration from mismatch.
        now = self.now_ms()
        count = self._db.execute("SELECT count(*) FROM job_cursors").fetchone()[0]
        if count >= self.max_cursor_records:
            self._db.execute("DELETE FROM job_cursors WHERE expires<=?", (now,))
        self._db.execute("DELETE FROM job_lists WHERE expires<=?", (now,))
        if self._db.execute("SELECT count(*) FROM job_cursors").fetchone()[0] >= (
            self.max_cursor_records
        ):
            fault("RESOURCE_LIMIT", resource="page")

    def _cursor(self, token, kind, binding, size):
        row = self._db.execute("SELECT * FROM job_cursors WHERE id=?", (token,)).fetchone()
        if row is None or row["kind"] != kind or row["binding"] != canonical(binding):
            fault("CURSOR_MISMATCH")
        if row["size"] != size:
            fault("CURSOR_MISMATCH")
        if self.now_ms() >= row["expires"]:
            fault("CURSOR_EXPIRED")
        return json.loads(row["position"])

    def _new_cursor(self, kind, binding, size, position, *, expires=None):
        # Identical cursor requests return exactly the same page and next token.
        previous = self._db.execute(
            "SELECT id FROM job_cursors WHERE kind=? AND binding=? AND size=? "
            "AND position=? AND expires>? ORDER BY created,id LIMIT 1",
            (kind, canonical(binding), size, canonical(position), self.now_ms()),
        ).fetchone()
        if previous:
            return previous[0]
        self._projection_room()
        token = str(uuid4())
        self._db.execute(
            "INSERT INTO job_cursors VALUES(?,?,?,?,?,?,?)",
            (
                token,
                kind,
                canonical(binding),
                size,
                canonical(position),
                expires if expires is not None else self.now_ms() + self.cursor_ttl_ms,
                self.now_ms(),
            ),
        )
        return token

    def _result_rows(self, project, identity):
        result = self.result_get(project, identity)
        payload = self.result(identity)["payload"]
        if payload is None:
            fault("PAYLOAD_EVICTED", resultId=identity)
        if not isinstance(payload, list):
            fault("INVALID_STATE")
        if result["kind"] == "scenario":
            self._check_summary(result, payload)
        if result["kind"] == "query" and "queryRequest" in self.job_context(result["jobId"]):
            self.semantic_result(project, identity)
        return result, payload

    def _check_summary(self, result, payload):
        job = self.get_job(result["projectId"], result["jobId"])
        progress = job["commitProgress"]
        if any(not self.contract.validate("row", row) for row in payload):
            fault("INVALID_STATE")
        if len({row["rowId"] for row in payload}) != len(payload):
            fault("INVALID_STATE")
        if (
            job["state"] != "succeeded"
            or job["resultRef"]
            != {"resultId": result["resultId"], "inputSnapshotId": result["inputSnapshotId"]}
            or progress["mode"] != "rounds"
            or not payload
            or len(payload[0].get("cells", [])) != 8
        ):
            fault("INVALID_STATE")
        c = payload[0]["cells"]
        p = progress["committedProgress"]
        if (
            p is None
            or c[:4] != ["run.summary.v1", p["runId"], p["lastCommittedRound"], p["snapshotRef"]]
            or c[4] is not True
            or type(c[5]) is not bool
            or type(c[6]) is not int
            or c[6] < 0
            or c[5] != (c[6] > 0)
        ):
            fault("INVALID_STATE")
        history = self.history(p["runId"])
        if (
            history["project"] != self._project(result["projectId"])
            or history["committedProgress"] != p
            or not history["terminal"]
            or history["terminal"]["status"] != "succeeded"
        ):
            fault("INVALID_STATE")
        if len(payload) != 1 + len(history["rounds"]):
            fault("INVALID_STATE")
        if (
            payload[0].get("ordinal") != 0
            or sum(r.get("cells", [None])[0] == "run.summary.v1" for r in payload if r.get("cells"))
            != 1
        ):
            fault("INVALID_STATE")
        for row, committed in zip(payload[1:], history["rounds"], strict=True):
            if row.get("ordinal") != committed["number"] or row.get(
                "cells"
            ) != self._round_audit_cells(p["runId"], job["jobId"], committed):
                fault("INVALID_STATE")
        evidence = json.loads(history["terminal"]["evidence"])
        if (
            evidence.get("jobId") != job["jobId"]
            or evidence.get("eventConsumptionRef") != c[7]
            or evidence.get("pendingEventCount") != c[6]
        ):
            fault("INVALID_STATE")

        consumption = self.blob(result["projectId"], c[7])
        state = self.load_snapshot(p["snapshotRef"])["state"]
        if (
            consumption.get("runId") != p["runId"]
            or consumption.get("inputSnapshotId") != result["inputSnapshotId"]
            or consumption.get("eventConsumption") != state.get("consumedEvents")
            or len(state.get("pendingEvents", [])) != c[6]
        ):
            fault("INVALID_STATE")

    def _round_audit_cells(self, run, identity, committed):
        if (
            committed["job"] != identity
            or committed["run"] != run
            or not UUID.fullmatch(committed["operation"])
        ):
            fault("INVALID_STATE")
        snapshot = self.load_snapshot(committed["snapshot"])
        if (
            snapshot.get("run") != run
            or snapshot.get("round") != committed["number"]
            or snapshot.get("project") != self._run(run)["project"]
        ):
            fault("INVALID_STATE")
        return [
            "run.round.v1",
            run,
            committed["number"],
            committed["snapshot"],
            committed["operation"],
            identity,
        ]

    def result_page(self, binding, page_size, cursor):
        self._valid(
            "params_result.page", {"binding": binding, "pageSize": page_size, "cursor": cursor}
        )
        with self._transaction():
            result, payload = self._result_rows(binding["projectId"], binding["resultId"])
            for key in ("inputSnapshotId", "scope", "parametersHash"):
                if binding[key] != result[key]:
                    fault("CURSOR_MISMATCH")
            position = self._cursor(cursor, "result", binding, page_size) if cursor else None
            available = [
                r for r in payload if position is None or [r["ordinal"], r["rowId"]] > position
            ]
            rows = []
            for row in available[:page_size]:
                candidate = {
                    "binding": binding,
                    "rows": [*rows, row],
                    "nextCursor": "00000000-0000-4000-8000-000000000000",
                }
                if self.contract.encoded_size(candidate) > 131072:
                    if not rows:
                        fault("RESOURCE_LIMIT", resource="page")
                    break
                rows.append(row)
            token = None
            if len(available) > len(rows):
                last = rows[-1]
                token = self._new_cursor(
                    "result", binding, page_size, [last["ordinal"], last["rowId"]]
                )
            page = {"binding": binding, "rows": rows, "nextCursor": token}
            self._valid("page", page)
            return page

    def job_list(self, project, filter, page_size, list_snapshot_id, cursor):
        filter_ = filter
        self._valid(
            "params_job.list",
            {
                "projectId": project,
                "filter": filter_,
                "pageSize": page_size,
                "listSnapshotId": list_snapshot_id,
                "cursor": cursor,
            },
        )
        self._project(project)
        with self._transaction():
            if list_snapshot_id is None:
                self._projection_room()
                jobs = [
                    json.loads(row[0])
                    for row in self._db.execute(
                        "SELECT dto FROM jobs WHERE project=? LIMIT 4097", (project,)
                    )
                ]
                jobs = [
                    j
                    for j in jobs
                    if filter_ == "all" or (j["state"] in TERMINAL) == (filter_ == "terminal")
                ]
                if len(jobs) > 4096:
                    fault("RESOURCE_LIMIT", resource="page")
                if len(canonical(jobs).encode()) > 8388608:
                    fault("RESOURCE_LIMIT", resource="memory")
                jobs.sort(key=lambda j: (j["createdAtMs"], j["jobId"]))
                if self._db.execute("SELECT count(*) FROM job_lists").fetchone()[0] >= (
                    self.max_cursor_records
                ):
                    fault("RESOURCE_LIMIT", resource="page")
                list_snapshot_id = str(uuid4())
                binding = {
                    "projectId": project,
                    "listSnapshotId": list_snapshot_id,
                    "filter": filter_,
                    "order": "createdAtMs+jobId:asc",
                }
                expires = self.now_ms() + self.cursor_ttl_ms
                self._db.execute(
                    "INSERT INTO job_lists VALUES(?,?,?,?,?)",
                    (
                        list_snapshot_id,
                        canonical(binding),
                        page_size,
                        canonical(jobs),
                        expires,
                    ),
                )
                position = None
            else:
                binding = {
                    "projectId": project,
                    "listSnapshotId": list_snapshot_id,
                    "filter": filter_,
                    "order": "createdAtMs+jobId:asc",
                }
                row = self._db.execute(
                    "SELECT * FROM job_lists WHERE id=?", (list_snapshot_id,)
                ).fetchone()
                if row is None or row["binding"] != canonical(binding) or row["size"] != page_size:
                    fault("CURSOR_MISMATCH")
                if self.now_ms() >= row["expires"]:
                    fault("CURSOR_EXPIRED")
                expires = row["expires"]
                jobs = json.loads(row["payload"])
                position = self._cursor(cursor, "list", binding, page_size)
            remaining = [
                j for j in jobs if position is None or [j["createdAtMs"], j["jobId"]] > position
            ]
            selected = []
            for job in remaining[:page_size]:
                candidate = {"binding": binding, "jobs": [*selected, job], "nextCursor": None}
                if self.contract.encoded_size(candidate) + 40 > 131072:
                    if not selected:
                        fault("RESOURCE_LIMIT", resource="page")
                    break
                selected.append(job)
            token = None
            if len(remaining) > len(selected):
                last = selected[-1]
                token = self._new_cursor(
                    "list",
                    binding,
                    page_size,
                    [last["createdAtMs"], last["jobId"]],
                    expires=expires,
                )
            page = {"binding": binding, "jobs": selected, "nextCursor": token}
            self._valid("jobList", page)
            return page

    def pin_result(self, identity, report):
        with self._transaction():
            result = self.result(identity)
            if result["payload"] is None:
                fault("PAYLOAD_EVICTED", resultId=identity)
            self._db.execute("INSERT OR IGNORE INTO result_pins VALUES(?,?)", (identity, report))

    def pin_report(self, project, identities, report):
        """Pin the complete explicitly selected immutable manifest atomically."""
        self._project(project)
        if not isinstance(identities, list) or not 1 <= len(identities) <= 32:
            fault("INVALID_REQUEST", field="params")
        manifest = canonical(sorted(set(identities)))
        with self._transaction():
            old = self._db.execute("SELECT manifest FROM job_reports WHERE id=?", (report,))
            old = old.fetchone()
            if old and old[0] != manifest:
                fault("IDENTITY_CONFLICT")
            for identity in identities:
                self.result_get(project, identity)
                self.pin_result(identity, report)
            self._db.execute(
                "INSERT OR IGNORE INTO job_reports VALUES(?,?,?)", (report, project, manifest)
            )

    def collect_cache(self):
        with self._transaction():
            ids = [
                r[0]
                for r in self._db.execute(
                    "SELECT id FROM results WHERE id NOT IN (SELECT result FROM result_pins) "
                    "AND id NOT IN (SELECT result FROM current_results) "
                    "AND id NOT IN (SELECT result FROM job_current) AND payload IS NOT NULL"
                )
            ]
            for identity in ids:
                self._db.execute("UPDATE results SET payload=NULL WHERE id=?", (identity,))
                self._db.execute(
                    "UPDATE query_payloads SET payload=NULL WHERE result=?", (identity,)
                )
            return ids


JOB_SCHEMA = [
    "CREATE TABLE IF NOT EXISTS public_projects(public TEXT PRIMARY KEY,internal TEXT UNIQUE "
    "NOT NULL REFERENCES projects(id))",
    "CREATE TABLE IF NOT EXISTS job_blobs(project TEXT REFERENCES public_projects(public),"
    "ref TEXT,payload TEXT NOT NULL,PRIMARY KEY(project,ref))",
    "CREATE TABLE IF NOT EXISTS job_plans(ref TEXT PRIMARY KEY,project TEXT "
    "REFERENCES public_projects(public),base INTEGER,plan_hash TEXT,diff_hash TEXT,payload TEXT)",
    "CREATE TABLE IF NOT EXISTS job_confirmations(id TEXT PRIMARY KEY,project TEXT "
    "REFERENCES public_projects(public),plan_ref TEXT REFERENCES job_plans(ref),base INTEGER,"
    "plan_hash TEXT,actor TEXT,permission TEXT)",
    "CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,project TEXT "
    "REFERENCES public_projects(public),operation TEXT UNIQUE,dto TEXT NOT NULL,"
    "context TEXT NOT NULL,fingerprint TEXT NOT NULL,run TEXT REFERENCES runs(id))",
    "CREATE TABLE IF NOT EXISTS operation_claims(operation TEXT PRIMARY KEY,project TEXT "
    "REFERENCES public_projects(public),job TEXT UNIQUE REFERENCES jobs(id),fingerprint TEXT)",
    "CREATE TABLE IF NOT EXISTS job_results(id TEXT PRIMARY KEY REFERENCES results(id),"
    "job TEXT REFERENCES jobs(id),manifests TEXT,projection TEXT,created INTEGER)",
    "CREATE TABLE IF NOT EXISTS job_current(key TEXT PRIMARY KEY,"
    "result TEXT REFERENCES results(id))",
    "CREATE TABLE IF NOT EXISTS job_cursors(id TEXT PRIMARY KEY,kind TEXT,binding TEXT,"
    "size INTEGER,position TEXT,expires INTEGER,created INTEGER)",
    "CREATE TABLE IF NOT EXISTS job_lists(id TEXT PRIMARY KEY,binding TEXT,size INTEGER,"
    "payload TEXT,expires INTEGER)",
    "CREATE TABLE IF NOT EXISTS job_reports(id TEXT PRIMARY KEY,project TEXT "
    "REFERENCES public_projects(public),manifest TEXT)",
    "CREATE TABLE IF NOT EXISTS job_details(id TEXT PRIMARY KEY,project TEXT "
    "REFERENCES public_projects(public),payload TEXT)",
]
for _table in (
    "public_projects",
    "job_blobs",
    "job_plans",
    "job_confirmations",
    "operation_claims",
    "job_results",
    "job_reports",
    "job_details",
):
    for _action in ("UPDATE", "DELETE"):
        JOB_SCHEMA.append(
            f"CREATE TRIGGER IF NOT EXISTS immutable_{_table}_{_action} BEFORE {_action} "
            f"ON {_table} BEGIN SELECT RAISE(ABORT,'immutable evidence'); END"
        )
JOB_SCHEMA.append(
    "CREATE TRIGGER IF NOT EXISTS immutable_job_context BEFORE UPDATE ON jobs "
    "WHEN NEW.id != OLD.id OR NEW.project != OLD.project OR NEW.operation != OLD.operation "
    "OR NEW.context != OLD.context OR NEW.fingerprint != OLD.fingerprint "
    "OR (OLD.run IS NOT NULL AND NEW.run IS NOT OLD.run) "
    "BEGIN SELECT RAISE(ABORT,'immutable job input'); END"
)
JOB_SCHEMA.append(
    "CREATE TRIGGER IF NOT EXISTS immutable_jobs_DELETE BEFORE DELETE ON jobs "
    "BEGIN SELECT RAISE(ABORT,'immutable job history'); END"
)


# Explicit3 evolves the one approved schema; default2 retains JOB_SCHEMA unchanged.
def _job_object_name(sql):
    normalized = sql.replace("IF NOT EXISTS ", "")
    return (
        normalized.split()[2]
        if normalized.startswith("CREATE TRIGGER")
        else normalized.partition("(")[0].split()[-1]
    )


JOB3_CLAIMS = (
    "CREATE TABLE operation_claims(operation TEXT PRIMARY KEY NOT NULL,"
    "project TEXT NOT NULL REFERENCES public_projects(public),"
    "job TEXT UNIQUE REFERENCES jobs(id),fingerprint TEXT NOT NULL,"
    "kind TEXT NOT NULL CHECK(kind IN ('job','application')),context TEXT,"
    "CHECK((kind='job' AND job IS NOT NULL AND context IS NULL) OR "
    "(kind='application' AND job IS NULL AND context IS NOT NULL)))"
)
JOB3_SCHEMA = [
    JOB3_CLAIMS
    if _job_object_name(sql) == "operation_claims"
    else sql.replace("IF NOT EXISTS ", "")
    for sql in JOB_SCHEMA
]
JOB3_CATALOG = [
    "CREATE TABLE job_format(singleton INTEGER PRIMARY KEY CHECK(singleton=1),"
    "schema_version INTEGER NOT NULL CHECK(schema_version=3),schema_hash TEXT NOT NULL,"
    "source_kind TEXT NOT NULL CHECK(source_kind IN ('new','v2')))"
] + [
    f"CREATE TRIGGER immutable_job_format_{action} BEFORE {action} ON job_format "
    "BEGIN SELECT RAISE(ABORT,'immutable job schema evidence'); END"
    for action in ("UPDATE", "DELETE")
]
JOB3_HASH = digest(JOB3_SCHEMA + JOB3_CATALOG)

# An additive private extension: never append these to JOB_SCHEMA/JOB3_SCHEMA.
QUERY_PAYLOAD_SCHEMA = [
    "CREATE TABLE query_payloads(result TEXT PRIMARY KEY NOT NULL REFERENCES job_results(id),"
    "payload TEXT,payload_hash TEXT NOT NULL,rows_hash TEXT NOT NULL)",
    "CREATE TABLE query_legacy_jobs(job TEXT PRIMARY KEY NOT NULL REFERENCES jobs(id))",
    "CREATE TABLE query_payload_format(singleton INTEGER PRIMARY KEY CHECK(singleton=1),"
    "version INTEGER NOT NULL CHECK(version=1),schema_hash TEXT NOT NULL,"
    "source_format INTEGER NOT NULL CHECK(source_format IN (2,3)))",
    "CREATE TRIGGER immutable_query_payloads_UPDATE BEFORE UPDATE ON query_payloads "
    "WHEN NEW.result IS NOT OLD.result OR NEW.payload_hash IS NOT OLD.payload_hash "
    "OR NEW.rows_hash IS NOT OLD.rows_hash OR NEW.payload IS NOT NULL "
    "BEGIN SELECT RAISE(ABORT,'immutable query payload'); END",
    "CREATE TRIGGER immutable_query_payloads_DELETE BEFORE DELETE ON query_payloads "
    "BEGIN SELECT RAISE(ABORT,'immutable query evidence'); END",
] + [
    f"CREATE TRIGGER immutable_{table}_{action} BEFORE {action} ON {table} "
    "BEGIN SELECT RAISE(ABORT,'immutable query catalog'); END"
    for table in ("query_legacy_jobs", "query_payload_format")
    for action in ("UPDATE", "DELETE")
]
QUERY_PAYLOAD_HASH = digest(QUERY_PAYLOAD_SCHEMA)
