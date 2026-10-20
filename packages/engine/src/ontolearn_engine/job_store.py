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
from ontolearn_engine.storage import FORMAT_VERSION, Conflict, Hook, Store, canonical, digest

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
    ):
        if not 1 <= cursor_ttl_ms <= 60000 or not 1 <= max_cursor_records <= 4096:
            raise ValueError("Invalid projection bounds")
        self.contract = contract
        self.now_ms = now_ms or (lambda: int(time.time() * 1000))
        self.cursor_ttl_ms = cursor_ttl_ms
        self.max_cursor_records = max_cursor_records
        self._lease = open(str(path) + ".writer-lock", "a+b")
        try:
            self._lock()
            super().__init__(path)
            with self._transaction():
                for sql in JOB_SCHEMA:
                    self._db.execute(sql)
        except BaseException:
            if hasattr(self, "_db"):
                self._db.close()
            self._lease.close()
            raise

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
        try:
            super().close()
        finally:
            self._lease.close()  # OS lock releases on close/crash; never unlink a leased inode.

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

    def accepted_operation_job(self, project, operation):
        self._project(project)
        row = self._db.execute(
            "SELECT project,job FROM operation_claims WHERE operation=?", (operation,)
        ).fetchone()
        if row is None:
            return None
        if row["project"] != project:
            fault("IDENTITY_CONFLICT")
        return self.get_job(project, row["job"])

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
                "formatVersion": FORMAT_VERSION,
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

    def create_job(
        self, project, operation, capability, input_, confirmation_ref, implementation, limits
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
        with self._transaction():
            claim = self._db.execute(
                "SELECT * FROM operation_claims WHERE operation=?", (operation,)
            ).fetchone()
            if claim:
                return self._accepted_job(
                    claim, project, capability, input_, confirmation_ref, implementation, limits
                )
            if (
                capability in {"query.execute", "reasoning.execute", "validation.execute"}
                and not self._db.execute(
                    "SELECT 1 FROM snapshots WHERE id=?", (input_["inputSnapshotId"],)
                ).fetchone()
            ):
                fault("NOT_FOUND", resource="snapshot")
            snap = self._project_snapshot(input_["inputSnapshotId"], internal)
            parameters = self.blob(project, input_["parametersHash"])
            if capability.startswith("test."):
                self._test_parameters(parameters)
            semantic_request = None
            if capability in {"query.execute", "reasoning.execute", "validation.execute"}:
                semantic_request = self.prepare_semantic_request(
                    project, capability, input_, parameters, snap, implementation
                )
            vector, manifests = self._dependencies(capability, input_, snap)
            for derived in input_["derivedResultIds"]:
                result = self.result_get(project, derived)
                if result["implementation"] != implementation:
                    fault("IDENTITY_CONFLICT")
            writing = capability in {"test.atomic", "changeset.commit", "mapping.commit"}
            if writing:
                plan_row = self._db.execute(
                    "SELECT * FROM job_plans WHERE ref=? AND project=?",
                    (input_["preparedPlanRef"], project),
                ).fetchone()
                confirmation = self._db.execute(
                    "SELECT * FROM job_confirmations WHERE id=? AND project=?",
                    (confirmation_ref, project),
                ).fetchone()
                if (
                    not plan_row
                    or not confirmation
                    or confirmation["plan_ref"] != plan_row["ref"]
                    or confirmation["plan_hash"] != plan_row["plan_hash"]
                    or confirmation["base"] != snap["projectRevision"]
                    or plan_row["base"] != snap["projectRevision"]
                    or confirmation["permission"] != "write"
                ):
                    fault("IDENTITY_CONFLICT")
                plan = json.loads(plan_row["payload"])
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
            if semantic_request is not None:
                context["semanticRequest"] = semantic_request
                if capability == "validation.execute":
                    context["validationBinding"] = self.validation_binding(
                        project,
                        input_,
                        snap,
                        implementation,
                        semantic_request["selected"],
                        parameters,
                    )
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
            self._db.execute(
                "INSERT INTO operation_claims VALUES(?,?,?,?)",
                (operation, project, identity, fingerprint),
            )
            return job

    def _accepted_job(
        self, claim, project, capability, input_, confirmation_ref, implementation, limits
    ):
        """Read an existing acceptance, independent of mutable current/cache state.

        The full frozen context remains content-verified; only the original
        accepted source's present payload availability/currentness is irrelevant.
        New operations still use all normal live-reference validation above.
        """
        if claim["project"] != project:
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
            plan = self._db.execute(
                "SELECT * FROM job_plans WHERE project=? AND ref=?",
                (project, input_["preparedPlanRef"]),
            ).fetchone()
            confirmation = self._db.execute(
                "SELECT * FROM job_confirmations WHERE project=? AND id=?",
                (project, confirmation_ref),
            ).fetchone()
            if (
                not plan
                or not confirmation
                or json.loads(plan["payload"]) != context["plan"]
                or plan["plan_hash"] != digest(context["plan"])
                or plan["base"] != snapshot["projectRevision"]
                or digest(
                    {
                        "projectId": project,
                        "plan": context["plan"],
                        "before": input_["inputSnapshotId"],
                        "diffHash": plan["diff_hash"],
                    }
                )
                != input_["preparedPlanRef"]
                or confirmation["plan_ref"] != plan["ref"]
                or confirmation["plan_hash"] != plan["plan_hash"]
                or confirmation["base"] != plan["base"]
                or confirmation["permission"] != "write"
            ):
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
            if self.revision(internal) != plan["base"]:
                fault("REVISION_CONFLICT", expected=plan["base"], actual=self.revision(internal))
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
            result = self._publish_job(job, rows, kind)
            self._transition(job, "succeeded", result=result)
            hook("mid_job_terminal")
        return self._job(identity)

    def prepare_semantic_request(
        self, project, capability, input_, parameters, snap, implementation
    ):
        """Resolve immutable sources in the acceptance transaction, before worker launch."""
        from ontolearn_engine.semantic_execution import (
            SemanticExecutionFault,
            build_request,
        )

        if not isinstance(parameters, dict) or set(parameters) - {"inputSelection"}:
            fault("INVALID_REQUEST", field="params")
        selection = parameters.get("inputSelection", "current")
        if selection not in ("current", "historical"):
            fault("INVALID_REQUEST", field="params")
        family = {"query.execute": "query", "validation.execute": "constraint"}.get(capability)
        if family and not any(
            d["layer"] == family and d["id"] == input_["definitionId"]
            for d in snap["state"]["definitions"]
        ):
            # Unknown public selection differs from corrupt saved definition
            # structure, which the trusted request builder handles internally.
            fault("INVALID_REQUEST", field="dependency")
        if selection == "current" and input_["inputSnapshotId"] != self.snapshot(
            self._project(project)
        ):
            fault("IDENTITY_CONFLICT")
        identities = input_["derivedResultIds"]
        include = input_["scope"] == "asserted+derived"
        if (
            len(identities) != (1 if include else 0)
            or capability == "reasoning.execute"
            and include
        ):
            fault("INVALID_REQUEST", field="params")
        selected = None
        if include:
            metadata, payload = self.semantic_result(project, identities[0])
            if (
                metadata["kind"] != "reasoning"
                or metadata["inputSnapshotId"] != input_["inputSnapshotId"]
                or metadata["implementation"] != implementation
                or selection == "current"
                and metadata["state"] != "current"
            ):
                fault("IDENTITY_CONFLICT")
            selected = {"metadata": metadata, "payload": payload}
        try:
            return build_request(
                snap,
                capability,
                input_,
                parameters,
                selected,
                error_catalog=self.contract.ERROR_CATALOG,
                error_schema=self.contract.DOCUMENT,
            )
        except SemanticExecutionFault as error:
            raise JobFault(error.error["code"], error.error["params"]) from None

    def semantic_result(self, project, identity):
        """Authenticate result, producer, accepted input, byte content and complete identity."""
        metadata = self.result_get(project, identity)
        if metadata["payloadStatus"] != "available":
            fault("PAYLOAD_EVICTED", resultId=identity)
        record = self._db.execute(
            "SELECT * FROM semantic_payloads WHERE result=?", (identity,)
        ).fetchone()
        if record is None or record["payload"] is None:
            fault("INTERNAL_ERROR")
        payload = json.loads(record["payload"])
        producer = self.get_job(project, metadata["jobId"])
        if (
            digest(payload) != record["payload_hash"]
            or digest(self.result(identity)["payload"]) != record["rows_hash"]
            or producer["state"] != "succeeded"
            or producer["capability"] != metadata["kind"] + ".execute"
            or producer["resultRef"]
            != {"resultId": identity, "inputSnapshotId": metadata["inputSnapshotId"]}
            or producer["inputSnapshotId"] != metadata["inputSnapshotId"]
            or producer["implementation"] != metadata["implementation"]
            or producer["dependencyVector"] != metadata["dependencyVector"]
            or producer["definitionSetDigests"] != metadata["definitionSetDigests"]
            or any(
                producer["input"][key] != metadata[key]
                for key in ("definitionId", "scope", "parametersHash")
            )
            or payload.get("kind") != metadata["kind"]
            or payload.get("inputSnapshotId") != metadata["inputSnapshotId"]
            or payload.get("inputProjectRevision") != metadata["inputProjectRevision"]
            or payload.get("executionSemanticsVersion")
            != metadata["implementation"]["executionSemanticsVersion"]
            or any(payload.get(key) != metadata[key] for key in ("definitionId", "scope"))
            or payload.get("inputSelection")
            != self.blob(project, producer["parametersHash"]).get("inputSelection", "current")
        ):
            fault("INTERNAL_ERROR")
        return metadata, payload

    def semantic_resource(self, project, value):
        encoded = canonical(value)
        if len(encoded.encode()) > 8388608:
            fault("RESOURCE_LIMIT", resource="semanticInput")
        reference = digest(value)
        self._db.execute(
            "INSERT OR IGNORE INTO semantic_resources VALUES(?,?,?)",
            (project, reference, encoded),
        )
        stored = self._db.execute(
            "SELECT payload FROM semantic_resources WHERE project=? AND ref=?", (project, reference)
        ).fetchone()
        if stored is None or stored[0] != encoded or digest(json.loads(stored[0])) != reference:
            fault("INVALID_STATE")
        return reference

    def validation_binding(self, project, input_, snap, implementation, selected, parameters):
        """Real content-addressed resources, associated by the single canonical resolver."""
        facts = sorted(
            [
                [f"<{r['subject']}>", f"<{r['predicate']}>", r["object"]]
                for r in snap["state"]["facts"]
                if r["object"] is not None
            ]
        )
        definitions = {
            (d["layer"], d["id"]): json.loads(d["payload"]) for d in snap["state"]["definitions"]
        }
        ontology = sorted(
            [
                [f"<{r['subject']}>", f"<{r['predicate']}>", r["object"]]
                for (layer, _), definition in definitions.items()
                if layer == "ontology"
                for r in definition["triples"]
            ]
        )
        values = {
            "assertedFacts": facts,
            "ontologyAxioms": ontology,
            "constraints": definitions[("constraint", input_["definitionId"])],
        }
        derived = None
        if selected:
            reason = selected["payload"]["reasoning"]
            triples = sorted({tuple(t) for t in reason["rdfs"] + reason["rules"]})
            rdfs = "<http://www.w3.org/2000/01/rdf-schema#"
            owl = "<http://www.w3.org/2002/07/owl#"
            rdf_type = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"

            def axiom(t):
                return t[1] in {rdfs + k + ">" for k in ("subClassOf", "domain", "range")} or (
                    t[1] == rdf_type
                    and t[2]
                    in {
                        rdfs + "Class>",
                        *[owl + k + ">" for k in ("Class", "ObjectProperty", "DatatypeProperty")],
                    }
                )

            values["derivedFacts"] = [list(t) for t in triples if not axiom(t)]
            values["derivedAxioms"] = [list(t) for t in triples if axiom(t)]
        refs = {role: self.semantic_resource(project, value) for role, value in values.items()}
        if selected:
            derived = {
                "projectId": project,
                "inputSnapshotId": input_["inputSnapshotId"],
                "resultId": selected["metadata"]["resultId"],
                "implementation": implementation,
                "factsRef": refs["derivedFacts"],
                "axiomsRef": refs["derivedAxioms"],
            }
        projection = {
            "projectionVersion": 1,
            "projectionPolicy": "selected-facts-v1",
            "projectId": project,
            "inputSnapshotId": input_["inputSnapshotId"],
            "inputProjectRevision": snap["projectRevision"],
            "implementation": implementation,
            "assertedFactsRef": refs["assertedFacts"],
            "ontologyAxiomsRef": refs["ontologyAxioms"],
            "constraintDefinitionId": input_["definitionId"],
            "constraintsRef": refs["constraints"],
            "scope": input_["scope"],
            "derived": derived,
            "inputSelection": parameters.get("inputSelection", "current"),
        }
        resources = []
        for role, reference in refs.items():
            source = selected["metadata"] if role.startswith("derived") else None
            resources.append(
                {
                    "ref": reference,
                    "projectId": project,
                    "inputSnapshotId": input_["inputSnapshotId"],
                    "role": role,
                    "resultId": source["resultId"] if source else None,
                    "implementation": source["implementation"] if source else None,
                    "resultKind": source["kind"] if source else None,
                    "payloadStatus": source["payloadStatus"] if source else None,
                    "resultState": source["state"] if source else None,
                    "constraintDefinitionId": input_["definitionId"]
                    if role == "constraints"
                    else None,
                }
            )
        if not self.contract.validation_projection_matches_resources(projection, resources):
            fault("INVALID_STATE")
        return {"projection": projection, "resources": resources}

    def finish_semantic_job(self, identity, output, hook: Hook = lambda _: None):
        with self._transaction(hook):
            job = self._job(identity)
            if job["state"] in TERMINAL:
                return job
            if job["state"] != "running" or job["capability"] not in {
                "query.execute",
                "reasoning.execute",
                "validation.execute",
            }:
                fault("INVALID_STATE")
            if not isinstance(output, dict) or set(output) != {"payload", "rows"}:
                fault("INVALID_STATE")
            payload = output["payload"]
            kind = job["capability"].split(".")[0]
            if (
                not isinstance(payload, dict)
                or payload.get("kind") != kind
                or payload.get("inputSnapshotId") != job["inputSnapshotId"]
            ):
                fault("INVALID_STATE")
            if len(canonical(output).encode()) > 8388608:
                fault("RESOURCE_LIMIT", resource="semanticResult")
            binding = self.job_context(identity).get("validationBinding")
            if binding and payload.get("validationBinding") != binding:
                fault("INVALID_STATE")
            result = self._publish_job(job, output["rows"], kind)
            self._db.execute(
                "INSERT INTO semantic_payloads VALUES(?,?,?,?)",
                (
                    result["resultId"],
                    canonical(payload),
                    digest(payload),
                    digest(self.result(result["resultId"])["payload"]),
                ),
            )
            self._transition(job, "succeeded", result=result)
            hook("mid_job_terminal")
        return self._job(identity)

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
            and context["parameters"].get("inputSelection") != "historical"
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
        if result["kind"] in {"reasoning", "query", "validation"}:
            self.semantic_result(project, identity)
        if result["kind"] == "scenario":
            self._check_summary(result, payload)
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
                    "UPDATE semantic_payloads SET payload=NULL WHERE result=?", (identity,)
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
    "CREATE TABLE IF NOT EXISTS semantic_resources(project TEXT REFERENCES public_projects(public),"
    "ref TEXT,payload TEXT NOT NULL,PRIMARY KEY(project,ref))",
    "CREATE TABLE IF NOT EXISTS semantic_payloads(result TEXT PRIMARY KEY REFERENCES results(id),"
    "payload TEXT,payload_hash TEXT NOT NULL,rows_hash TEXT NOT NULL)",
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
    "semantic_resources",
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

JOB_SCHEMA.extend(
    [
        "CREATE TRIGGER IF NOT EXISTS immutable_semantic_payloads_UPDATE "
        "BEFORE UPDATE ON semantic_payloads "
        "WHEN NEW.result != OLD.result OR NEW.payload_hash != OLD.payload_hash "
        "OR NEW.rows_hash != OLD.rows_hash "
        "OR OLD.payload IS NULL OR NEW.payload IS NOT NULL "
        "BEGIN SELECT RAISE(ABORT,'immutable semantic evidence'); END",
        "CREATE TRIGGER IF NOT EXISTS immutable_semantic_payloads_DELETE "
        "BEFORE DELETE ON semantic_payloads "
        "BEGIN SELECT RAISE(ABORT,'immutable semantic evidence'); END",
    ]
)
