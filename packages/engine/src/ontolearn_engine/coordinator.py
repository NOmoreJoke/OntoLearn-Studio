"""Single application writer; isolated workers never open the SQLite source of truth."""

import asyncio
import hashlib
import json
import os
import queue
import signal
import sqlite3
import sys
import tempfile
import threading
import time
from collections import deque
from pathlib import Path
from uuid import uuid4

from ontolearn_engine import __version__
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.memory_guard import MEMORY_LIMIT_EXIT, resident_bytes
from ontolearn_engine.process_environment import worker_environment
from ontolearn_engine.protocol import JsonlReader, ProtocolFault
from ontolearn_engine.resources import (
    CONTRACT,
    IMPLEMENTATION,
    LIMITS,
    REGISTRY_HASH,
    safe_error,
    semantic_identity,
)
from ontolearn_engine.storage import Conflict, UnsupportedProjectFormat
from ontolearn_engine.worker import (
    query_decode,
    query_encode,
    query_parts,
    query_transport_limits,
    worker_owner_arguments,
)

TERMINAL = {"succeeded", "failed", "cancelled"}
# The frame-transport semantic worker path serves all three read capabilities;
# worker and Store enforce the same set independently.
_SEMANTIC_CAPABILITIES = frozenset({"query.execute", "reasoning.execute", "validation.execute"})
_JOB_READY = object()
_BOOTSTRAP_JOB_STORE = JobStore


class StartupInitializationFailure(Exception):
    """Internal carrier created only after initialization cleanup was attempted."""

    def __init__(self, cause, cleanup_failures=(), reader_state=None):
        super().__init__("STARTUP_INITIALIZATION_FAILED")
        self.cause = cause
        self.cleanup_failures = tuple(cleanup_failures)
        self.reader_state = dict(reader_state or {})


def startup_code(error):
    from ontolearn_engine.project.format3 import Format3Fault

    if isinstance(error, UnsupportedProjectFormat):
        return "PROJECT_FORMAT_UNSUPPORTED"
    if isinstance(error, Format3Fault):
        if error.category == "leaseBusy":
            return "STORAGE_BUSY"
        if error.category == "structure":
            return "STORAGE_FAILURE"
    if isinstance(error, JobFault) and error.code == "STORAGE_BUSY":
        return "STORAGE_BUSY"
    if isinstance(error, sqlite3.Error):
        primary = getattr(error, "sqlite_errorcode", 0) & 0xFF
        if primary in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED}:
            return "STORAGE_BUSY"
        if primary in {
            sqlite3.SQLITE_IOERR,
            sqlite3.SQLITE_FULL,
            sqlite3.SQLITE_READONLY,
            sqlite3.SQLITE_CORRUPT,
        }:
            return "STORAGE_FAILURE"
    return "INTERNAL_ERROR"


class ServiceFault(Exception):
    def __init__(self, code: str, params: dict | None = None):
        self.code = code
        self.params = params
        self.error = safe_error(code, params)


def classify(
    error: Exception, *, resource: str = "job", field: str = "params", profile="legacy2"
) -> dict:
    formatter = CONTRACT.business3_error if profile == "business3" else safe_error
    if isinstance(error, ServiceFault):
        return formatter(error.code, error.params)
    if isinstance(error, (JobFault, Conflict)):
        return formatter(error.code, error.params)
    if isinstance(error, sqlite3.Error):
        primary = getattr(error, "sqlite_errorcode", 0) & 0xFF
        if primary in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED}:
            return formatter("STORAGE_BUSY", {"retryAfterMs": 250})
        if primary in {
            sqlite3.SQLITE_IOERR,
            sqlite3.SQLITE_FULL,
            sqlite3.SQLITE_READONLY,
            sqlite3.SQLITE_CORRUPT,
        }:
            return formatter("STORAGE_FAILURE")
        return formatter("INTERNAL_ERROR")
    return formatter("INTERNAL_ERROR")


def worker_command() -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--worker"]
    return [sys.executable, "-I", "-m", "ontolearn_engine.worker"]


def _signal_worker(process, *, force: bool) -> None:
    """Signal a worker process on POSIX without invoking Popen.poll() ahead of waitpid."""
    if process.returncode is not None:
        return
    if os.name == "posix":
        pid = process.pid
        if pid is None or pid <= 0:
            return
        sig = signal.SIGKILL if force else signal.SIGTERM
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            pass
        return
    try:
        if force:
            process.kill()
        else:
            process.terminate()
    except ProcessLookupError:
        pass


class Coordinator:
    def __init__(
        self,
        store,
        *,
        test_mode: bool = False,
        allowed_projects: set | None = None,
        limits: dict | None = None,
        emit=None,
        profile="legacy2",
        _ready=None,
        ordinary_authority=None,
        query_dispatch=None,
        example_provider=None,
        _test_schedule=None,
    ):
        if profile not in {"legacy2", "business3"}:
            raise ValueError("INVALID_PROFILE")
        if _test_schedule is not None:
            # Trusted-test-only scheduling hooks: never a job parameter, RPC,
            # environment variable or wire-controllable input. Production
            # construction refuses the object outright instead of ignoring it.
            if not test_mode or not isinstance(_test_schedule, dict):
                raise ValueError("INVALID_TEST_INJECTION")
            if set(_test_schedule) - {"before_worker", "after_round_commit"} or any(
                hook is not None and not callable(hook) for hook in _test_schedule.values()
            ):
                raise ValueError("INVALID_TEST_INJECTION")
        version = 3 if profile == "business3" else 2
        if getattr(store, "actual_format", 2) != version or (
            version == 3 and (_ready is not _JOB_READY or not isinstance(store, JobStore))
        ):
            raise ServiceFault("INVALID_STATE")
        self.profile = profile
        self.version = version
        self.validate = CONTRACT.validate_business3 if version == 3 else CONTRACT.validate
        self.methods = (
            CONTRACT.REGISTRY["foundationProfiles"]["business3"]["methods"]
            if version == 3
            else CONTRACT.REGISTRY["v2Runtime"]
        )
        self.store = store
        self.test_mode = test_mode
        # Scheduling-only test hooks (see __init__ validation): they reorder
        # when existing real work runs and never create or mutate state,
        # rounds, snapshots or notifications.
        self._test_schedule = _test_schedule
        # W4-04 optional runtime callback, bound only by serve() below: drains
        # queued inbox frames at scenario round boundaries so an in-flight
        # project.scenario.cancel is answered while the run still executes.
        # It runs solely on the single serve-loop thread; never a wire input.
        self._poll_cancel = None
        self.allowed_projects = frozenset(allowed_projects or set())
        self.limits = LIMITS | (limits or {})
        if not CONTRACT.validate("limits", self.limits):
            raise ValueError("INVALID_LIMITS")
        self.session = None
        # Attribution of the trusted stdio client, never proof of human consent.
        self.host_client_id = None
        self.seen = set()
        self.subscriptions = {}
        self.queued = deque()
        self.active = {}
        self.closed = False
        self._output = emit or self._emit
        self.emit = self._validated_emit
        self.tasks = set()
        from ontolearn_engine.project.ordinary_library import OrdinaryLibrary

        self.ordinary = OrdinaryLibrary(self, ordinary_authority)
        from ontolearn_engine.project.query_definitions import QueryDispatchAuthority

        self.query_dispatch = (
            query_dispatch if isinstance(query_dispatch, QueryDispatchAuthority) else None
        )
        self._query_project_get = None
        self._query_replies = {}
        self.mainline = None
        if version == 3 and not test_mode and ordinary_authority is None and query_dispatch is None:
            # _JOB_READY and the actual original JobStore were checked above.
            # The named production adapter is never installed from a wire DTO.
            from ontolearn_engine.project.mainline import MainlineHost

            self.mainline = MainlineHost(self, example_provider=example_provider)
            self.ordinary = self.mainline
            self.query_dispatch = self.mainline

    def _validated_emit(self, value):
        if not self.validate("envelope", value):
            raise ProtocolFault()
        self._output(value)

    @staticmethod
    def _emit(value: dict) -> None:
        raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()
        if len(raw) > LIMITS["maxFrameBytes"]:
            raise ProtocolFault()
        sys.stdout.buffer.write(raw + b"\n")
        sys.stdout.buffer.flush()

    def _authorize(self, params: dict) -> str | None:
        if self.mainline is not None:
            return self.mainline.authorize(params)
        project = params.get("projectId", params.get("binding", {}).get("projectId"))
        if project and project not in self.allowed_projects | self.ordinary.projects():
            raise ServiceFault("PERMISSION_DENIED")
        return project

    def _progress(self, job: dict, stage: str, subscription: str | None = None) -> None:
        # Progress is a disposable execution hint, never a persistent job state
        # or a guessed amount of work. Share the subscription sequence with state.
        if job["state"] in TERMINAL:
            return
        for identity, binding in list(self.subscriptions.items()):
            if (
                (subscription is None or identity == subscription)
                and binding["projectId"] == job["projectId"]
                and binding["jobId"] == job["jobId"]
                and binding["stateVersion"] == job["stateVersion"]
            ):
                binding["seq"] += 1
                self.emit(
                    {
                        "kind": "notification",
                        "protocolVersion": self.version,
                        "engineSessionId": self.session,
                        "subscriptionId": identity,
                        "projectId": job["projectId"],
                        "jobId": job["jobId"],
                        "seq": binding["seq"],
                        "event": "job.progress",
                        "data": {
                            "stateVersion": job["stateVersion"],
                            "progress": {"stage": stage, "completed": None, "total": None},
                        },
                    }
                )

    def _stage(self, identity: str, stage: str) -> None:
        active = self.active.get(identity)
        if active is None:
            return
        job = self.store.get_job(active["project"], identity)
        if job["state"] in TERMINAL:
            active.pop("stage", None)
            return
        if job["state"] == "cancelling":
            stage = "reconciling"
        if active.get("stage") != stage:
            active["stage"] = stage
            self._progress(job, stage)

    def _notify(self, job: dict) -> None:
        if job["state"] in TERMINAL:
            self.active.get(job["jobId"], {}).pop("stage", None)
        for identity, binding in list(self.subscriptions.items()):
            if binding["projectId"] == job["projectId"] and binding["jobId"] == job["jobId"]:
                if job["stateVersion"] <= binding["stateVersion"]:
                    continue
                binding["stateVersion"] = job["stateVersion"]
                binding["seq"] += 1
                self.emit(
                    {
                        "kind": "notification",
                        "protocolVersion": self.version,
                        "engineSessionId": self.session,
                        "subscriptionId": identity,
                        "projectId": job["projectId"],
                        "jobId": job["jobId"],
                        "seq": binding["seq"],
                        "event": "job.state",
                        "data": job,
                    }
                )

    def request(self, value: object) -> dict:
        # Unknown envelope/method/id is session-fatal: never reflect unknown wire data.
        if self.version == 3 and self.closed:
            raise ProtocolFault()
        if not isinstance(value, dict) or not CONTRACT.validate("id", value.get("id")):
            raise ProtocolFault()
        method = value.get("method")
        if not isinstance(method, str) or (
            method not in self.methods and not (self.version == 2 and method == "ordinary.library")
        ):
            raise ProtocolFault()
        if value["id"] in self.seen or len(self.seen) >= 65536:
            raise ProtocolFault()
        self.seen.add(value["id"])
        required = {"kind", "id", "protocolVersion", "engineSessionId", "method", "params"}
        if set(value) != required or value["kind"] != "request":
            raise ProtocolFault()
        if self.version == 3 and (
            (method == "hello" and self.session is not None)
            or (
                method != "hello"
                and (
                    self.session is None
                    or value["engineSessionId"] != self.session
                    or type(value["protocolVersion"]) is not int
                    or value["protocolVersion"] != 3
                )
            )
        ):
            self.closed = True
            raise ProtocolFault()
        response = {
            "kind": "response",
            "id": value["id"],
            "method": method,
            "protocolVersion": 2 if method == "hello" else self.version,
            "engineSessionId": self.session,
        }
        try:
            expected = 2 if method == "hello" else self.version
            if type(value["protocolVersion"]) is not int or value["protocolVersion"] != expected:
                raise ServiceFault("VERSION_INCOMPATIBLE", {"supportedVersions": [self.version]})
            if method != "hello" and self.session is None:
                raise ServiceFault("HANDSHAKE_REQUIRED")
            if not self.validate("params_" + method, value["params"]):
                raise ServiceFault("INVALID_REQUEST", {"field": "params"})
            if method == "hello":
                if self.session is not None:
                    raise ServiceFault("INVALID_STATE")
                if value["engineSessionId"] is not None:
                    raise ServiceFault("SESSION_MISMATCH")
                if self.version not in value["params"]["supportedVersions"]:
                    raise ServiceFault(
                        "VERSION_INCOMPATIBLE", {"supportedVersions": [self.version]}
                    )
                if self.version == 3 and not self.validate("request", value):
                    raise ServiceFault("INVALID_REQUEST", {"field": "params"})
                self.session = str(uuid4())
                self.host_client_id = value["params"]["clientId"]
                if self.mainline is not None:
                    self.mainline.bind_handshake()
                response["engineSessionId"] = self.session
                data = {
                    "selectedVersion": self.version,
                    "engineVersion": __version__,
                    "engineSessionId": self.session,
                    "capabilities": [*self.methods]
                    + (
                        ["ordinary.library"]
                        if self.mainline is None and self.ordinary.enabled()
                        else []
                    ),
                    "limits": self.limits,
                    "registryHash": REGISTRY_HASH,
                }
            else:
                if self.session is None:
                    raise ServiceFault("HANDSHAKE_REQUIRED")
                if value["engineSessionId"] != self.session:
                    raise ServiceFault("SESSION_MISMATCH")
                if self.version == 3 and not self.validate("request", value):
                    raise ServiceFault("INVALID_REQUEST", {"field": "params"})
                # Liveness does not read project material or acquire authority.
                # A held/damaged project must not turn heartbeat into a restart
                # loop, or prevent the original owner from reporting its state.
                if method not in {"health", "session.ping"}:
                    if self.mainline is not None:
                        self.mainline.begin(value)
                    self._authorize(value["params"])
                if method == "project.get" and self.query_dispatch is not None:
                    from ontolearn_engine.project.query_definitions import ProjectGetReadTicket

                    # Reserve before the external issuer callback can reenter.
                    # A callback failure with no returned receipt stays UNKNOWN;
                    # the real external issuer retains that request's work/aliases.
                    if len(self._query_replies) >= 16:
                        raise ServiceFault("INVALID_STATE")
                    self._query_replies[value["id"]] = None
                    ticket = self.query_dispatch.take(self, value)
                    if ticket is None:
                        del self._query_replies[value["id"]]  # genuine ordinary dispatch
                    else:
                        if (
                            not isinstance(ticket, ProjectGetReadTicket)
                            or ticket.issuer is not self.query_dispatch
                        ):
                            raise ServiceFault("PERMISSION_DENIED")
                        self._query_replies[value["id"]] = ticket
                        if (
                            ticket.request_id != value["id"]
                            or ticket.read.session != self.session
                            or ticket.project != value["params"]["projectId"]
                        ):
                            raise ServiceFault("PERMISSION_DENIED")
                        self._query_project_get = ticket
                data = self.dispatch(method, value["params"])
                if (
                    method in {"result.page", "job.list"}
                    and CONTRACT.encoded_size(data) > self.limits["maxPageBytes"]
                ):
                    raise ServiceFault("RESOURCE_LIMIT", {"resource": "page"})
            response.update(ok=True, result=data)
        except Exception as error:
            if self.mainline is not None:
                self.mainline.observe_error(value["id"], error)
            response.update(
                ok=False,
                error=classify(
                    error,
                    profile=self.profile,
                    resource="project"
                    if method == "project.get"
                    else "result"
                    if method.startswith("result.")
                    else "job",
                ),
            )
        if not self.validate("response", response):
            raise ProtocolFault()
        if self.version == 3 and method == "hello" and not response["ok"]:
            self.closed = True  # No second hello after a rejected3 bootstrap.
        return response

    def ordinary_project_get(self, book, ticket, project):
        # A stack-local one-use permit, never a temporary allowed-project set.
        if book is not self.ordinary:
            raise ServiceFault("PERMISSION_DENIED")
        book.consume(ticket, self.store, "project.get", project)
        return self.dispatch("project.get", {"projectId": project})

    def finish_query_reply(self, request_id, *, emitted, failure=None):
        ticket = self._query_replies.get(request_id)
        if ticket is not None:
            ticket.finish(emitted=emitted, failure=failure)
            if self._query_replies.get(request_id) is ticket and ticket.finished:
                del self._query_replies[request_id]
        if self.mainline is not None:
            self.mainline.finish_reply(request_id, emitted=emitted, failure=failure)

    def dispatch(self, method: str, p: dict):
        from ontolearn_engine.behavior.service import METHODS as BEHAVIOR_METHODS
        from ontolearn_engine.mapping.service import METHODS as MAPPING_METHODS
        from ontolearn_engine.project.checkpoints import METHODS as CHECKPOINT_METHODS
        from ontolearn_engine.project.learning_agent import METHODS as AGENT_METHODS
        from ontolearn_engine.project.learning_ledger import METHODS as LEARNING_METHODS
        from ontolearn_engine.project.management import METHODS as MANAGEMENT_METHODS
        from ontolearn_engine.project.ontology_import import METHODS as IMPORT_METHODS
        from ontolearn_engine.project.ontology_turtle import METHODS as EXPORT_METHODS
        from ontolearn_engine.project.quality_definitions import METHODS as QUALITY_METHODS
        from ontolearn_engine.project.run_before_commit import METHODS as RUN_METHODS
        from ontolearn_engine.scenario.service import METHODS as SCENARIO_METHODS
        from ontolearn_engine.transfer.service import METHODS as TRANSFER_METHODS

        if (
            method in MANAGEMENT_METHODS
            or method in CHECKPOINT_METHODS
            or method in LEARNING_METHODS
            or method in QUALITY_METHODS
            or method in EXPORT_METHODS
            or method in IMPORT_METHODS
            or method in AGENT_METHODS
            or method in MAPPING_METHODS
            or method in TRANSFER_METHODS
            or method in RUN_METHODS
            or method in BEHAVIOR_METHODS
            or method in SCENARIO_METHODS
            or method
            in {
                "project.catalog",
                "project.create",
                "project.example.create",
                "project.draft.save",
                "project.open",
                "project.read",
                "project.ownership.detail",
            }
        ):
            if self.mainline is None:
                raise ServiceFault("PERMISSION_DENIED")
            return self.mainline.dispatch(method, p)
        if method.startswith("query."):
            from ontolearn_engine.project.query_definitions import METHODS, query_read

            if method not in METHODS:
                raise ServiceFault("METHOD_NOT_ALLOWED")
            with query_read(self, method, p) as ticket:
                if method == "query.definition.load":
                    return self.store.load_query_definition(p, ticket=ticket)
                if method == "query.execution.prepare":
                    return self.store.prepare_query_execution_input(
                        p, semantic_identity(), self.limits, REGISTRY_HASH, ticket=ticket
                    )
                return self.store.query_presentation(method, p, self.limits, ticket=ticket)
        if method == "ordinary.library":
            return self.ordinary.dispatch(p)
        if method == "health":
            return {"status": "ok", "engineVersion": __version__}
        if method == "session.ping":
            return {"nonce": p["nonce"]}
        if method == "project.get":
            ticket, self._query_project_get = self._query_project_get, None
            if ticket is not None:
                return self.store.query_project_get(p["projectId"], actor=self, ticket=ticket)
            return self.store.project_get(p["projectId"])
        if method in {"changeset.preview", "changeset.diff.page", "changeset.confirm"}:
            if self.version != 3 or self.host_client_id is None or self.session is None:
                raise ServiceFault("METHOD_NOT_ALLOWED")
            origin = {
                "host_client_id": self.host_client_id,
                "engine_session_id": self.session,
            }
            if method == "changeset.preview":
                return self.store.preview_changeset(
                    p["projectId"],
                    p["baseRevision"],
                    p,
                    limits=self.limits,
                    ownership_proof=self.mainline.ownership_proof(p, method=method)
                    if self.mainline is not None
                    else None,
                    **origin,
                )
            if method == "changeset.diff.page":
                return self.store.changeset_diff_page(
                    p["projectId"],
                    p["previewHash"],
                    p["documentKind"],
                    p["pageSize"],
                    p["cursor"],
                    limits=self.limits,
                    **origin,
                )
            return self.store.confirm_changeset(
                p["projectId"], p["previewHash"], p["completionCursor"], **origin
            )
        if method == "job.get":
            return self.store.get_job(p["projectId"], p["jobId"])
        if method == "job.create":
            formal = self.version == 3 and p["capability"] == "changeset.commit"
            semantic = p["capability"] in _SEMANTIC_CAPABILITIES
            if (
                not formal
                and not semantic
                and (
                    not self.test_mode
                    or p["capability"]
                    not in {
                        "test.read",
                        "test.atomic",
                        "test.rounds",
                    }
                )
            ):
                raise ServiceFault("UNSUPPORTED_CAPABILITY")
            if len(self.queued) >= self.limits[
                "maxQueuedJobs"
            ] and not self.store.has_operation_claim(p["operationId"]):
                raise ServiceFault("QUEUE_FULL", {"retryAfterMs": 250})
            if formal:
                job = self.store.create_changeset_job(
                    p["projectId"],
                    p["operationId"],
                    p["input"],
                    p["confirmationRef"],
                    IMPLEMENTATION,
                    self.limits,
                    host_client_id=self.host_client_id,
                    engine_session_id=self.session,
                )
            else:
                job = self.store.create_job(
                    p["projectId"],
                    p["operationId"],
                    p["capability"],
                    p["input"],
                    p["confirmationRef"],
                    semantic_identity() if semantic else IMPLEMENTATION,
                    self.limits,
                )
            if (
                job["state"] == "queued"
                and job["jobId"] not in self.queued
                and job["jobId"] not in self.active
            ):
                self.queued.append(job["jobId"])
            return job
        if method == "job.cancel":
            answer = self.store.cancel_job(p["projectId"], p["jobId"])
            job = self.store.get_job(p["projectId"], p["jobId"])
            self._notify(job)
            if job["state"] == "cancelling":
                self._stage(job["jobId"], "reconciling")
            if job["state"] == "cancelled":
                try:
                    self.queued.remove(job["jobId"])
                except ValueError:
                    pass
            return answer  # Preserve exact cancellation linearization snapshot.
        if method == "job.subscribe":
            if len(self.subscriptions) >= 128:
                raise ServiceFault("RESOURCE_LIMIT", {"resource": "memory"})
            job = self.store.get_job(p["projectId"], p["jobId"])
            identity = str(uuid4())
            binding = {
                "subscriptionId": identity,
                "projectId": p["projectId"],
                "jobId": p["jobId"],
                "stateVersion": job["stateVersion"],
                "seq": 0,
            }
            self.subscriptions[identity] = binding
            # The stage snapshot may reach the consumer before this response.
            # Preserve seq=0 in the response; the first buffered hint is seq=1.
            response = dict(binding)
            stage = (
                "queued"
                if job["state"] == "queued"
                else self.active.get(job["jobId"], {}).get("stage")
            )
            if stage:
                self._progress(job, stage, identity)
            return response
        if method == "job.unsubscribe":
            binding = self.subscriptions.get(p["subscriptionId"])
            if binding is None or any(binding[k] != p[k] for k in ("projectId", "jobId")):
                raise ServiceFault("NOT_FOUND", {"resource": "subscription"})
            del self.subscriptions[p["subscriptionId"]]
            return {"subscriptionId": p["subscriptionId"], "unsubscribed": True}
        if method in {"job.list", "result.page"} and p["pageSize"] > self.limits["maxPageItems"]:
            raise ServiceFault("RESOURCE_LIMIT", {"resource": "page"})
        if method == "job.list":
            return self.store.job_list(**self._snake(p))
        if method == "result.get":
            return self.store.result_get(p["projectId"], p["resultId"])
        if method == "result.current":
            return self.store.result_current(**self._snake(p))
        if method == "result.page":
            return self.store.result_page(**self._snake(p))
        if method == "operation.get":
            return self.store.operation_get(p["projectId"], p["operationId"])
        raise ServiceFault("METHOD_NOT_ALLOWED")

    @staticmethod
    def _snake(p: dict) -> dict:
        names = {
            "projectId": "project",
            "resultId": "result_id",
            "pageSize": "page_size",
            "listSnapshotId": "list_snapshot_id",
            "definitionId": "definition_id",
            "parametersHash": "parameters_hash",
        }
        return {names.get(k, k): v for k, v in p.items()}

    async def tick(self) -> None:
        # Global concurrency and project single-writer are enforced before launch.
        occupied = {a["project"] for a in self.active.values() if a.get("writing", True)}
        for identity in list(self.queued):
            if len(self.active) >= self.limits["maxConcurrentJobs"]:
                break
            context = self.store.job_context(identity)
            job = context["job"]
            if int(time.time() * 1000) - job["createdAtMs"] >= job["limits"]["totalMs"]:
                self.queued.remove(identity)
                self._notify(
                    self.store.fail_job(identity, safe_error("TIMEOUT", {"phase": "total"}))
                )
                continue
            writing = CONTRACT.REGISTRY["capabilities"][job["capability"]]["effect"] != "read"
            if writing and job["projectId"] in occupied:
                continue
            self.queued.remove(identity)
            if writing:
                occupied.add(job["projectId"])
            active = {"project": job["projectId"], "process": None, "writing": writing}
            self.active[identity] = active
            task = asyncio.create_task(self.execute(identity, context, active))
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)

    async def execute_changeset(self, identity: str, context: dict, active: dict) -> None:
        """Execute a confirmed deterministic transaction in the sole writer.

        Acceptance is already durable. A normal dispatcher turn precedes the
        commit gate; an input-thread read alone never linearizes cancellation.
        No worker computation, test parameters or fabricated rows are involved.
        """
        try:
            job = self.store.start_job(identity)
            self._notify(job)
            self._stage(identity, "loading")
            deadline = (
                (job["createdAtMs"] + job["limits"]["totalMs"]) / 1000
                - time.time()
                + time.monotonic()
            )
            await asyncio.sleep(0)

            def boundary(_phase):
                current = self.store.get_job(active["project"], identity)
                if current["state"] == "cancelling":
                    raise asyncio.CancelledError()
                if time.monotonic() >= deadline:
                    raise ServiceFault("TIMEOUT", {"phase": "total"})

            boundary("before")
            self._stage(identity, "committing")
            job = self.store.commit_job(identity, hook=boundary)
            self._notify(job)
        except asyncio.CancelledError:
            job = self.store.get_job(active["project"], identity)
            if job["state"] in TERMINAL:
                self._notify(job)
            elif job["state"] == "cancelling":
                self._notify(self.store.cancelled_job(identity))
            else:
                self._notify(
                    self.store.fail_job(
                        identity, classify(ServiceFault("ENGINE_EXITED"), profile=self.profile)
                    )
                )
        except Exception as error:
            # A boundary may fail after COMMIT. Never rewrite persisted success.
            job = self.store.get_job(active["project"], identity)
            if job["state"] in TERMINAL:
                self._notify(job)
            else:
                self._notify(self.store.fail_job(identity, classify(error, profile=self.profile)))
        finally:
            self.active.pop(identity, None)

    async def execute(self, identity: str, context: dict, active: dict) -> None:
        if context["capability"] == "changeset.commit":
            await self.execute_changeset(identity, context, active)
            return
        process = None
        try:
            job = self.store.start_job(identity)
            self._notify(job)
            self._stage(identity, "loading")
            parameters = context["parameters"]
            if job["capability"] == "test.rounds":
                self.store.start_job_run(identity, context["runConfig"])
            deadline = time.monotonic() + max(
                0, (job["createdAtMs"] + job["limits"]["totalMs"] - int(time.time() * 1000)) / 1000
            )

            def commit_boundary(_phase):
                if time.monotonic() >= deadline:
                    raise ServiceFault("TIMEOUT", {"phase": "total"})
                if (
                    job["capability"] in _SEMANTIC_CAPABILITIES
                    and self.store.get_job(active["project"], identity)["state"] == "cancelling"
                ):
                    raise asyncio.CancelledError()
                if (
                    _phase == "before"
                    and job["capability"] == "test.rounds"
                    and self.store.get_job(active["project"], identity)["state"] == "cancelling"
                ):
                    # A durable cancel accepted after the last committed round
                    # linearizes before this next normal write: the before hook
                    # runs inside Store._transaction ahead of the running-only
                    # guard, so without this check the accepted cancel would
                    # misclassify the next same-chunk round as an
                    # INVALID_STATE failure instead of taking the existing
                    # cancellation cleanup. Only a real cancelling state takes
                    # that path; every other state and error classification
                    # is unchanged.
                    raise asyncio.CancelledError()

            async def controlled(work, phase, maximum_ms, on_completed=None):
                pending = asyncio.create_task(work)
                phase_deadline = time.monotonic() + maximum_ms / 1000
                try:
                    while not pending.done():
                        if self.store.get_job(active["project"], identity)["state"] == "cancelling":
                            raise asyncio.CancelledError()
                        commit_boundary("waiting")
                        if time.monotonic() >= phase_deadline:
                            raise ServiceFault("TIMEOUT", {"phase": phase})
                        child = active.get("process")
                        if (
                            job["capability"] in _SEMANTIC_CAPABILITIES
                            and sys.platform == "darwin"
                            and child is not None
                            and child.returncode is None
                        ):
                            try:
                                if (
                                    resident_bytes(child.pid)
                                    > job["limits"]["maxWorkerMemoryBytes"]
                                ):
                                    raise ServiceFault("RESOURCE_LIMIT", {"resource": "memory"})
                            except ProcessLookupError:
                                pass
                        await asyncio.wait({pending}, timeout=0.02)
                    result = pending.result()
                    if on_completed:
                        on_completed(result)  # Take ownership before a deadline can reject it.
                    commit_boundary("completed")
                    return result
                finally:
                    if not pending.done():
                        pending.cancel()
                    await asyncio.gather(pending, return_exceptions=True)

            if (
                job["capability"] == "test.rounds"
                and self._test_schedule is not None
                and (hook := self._test_schedule.get("before_worker")) is not None
            ):
                # Trusted-test scheduling point 1: the job is started and
                # notified, controlled() is available, but the worker has NOT
                # been launched. The hook decides when real work may begin;
                # bounded by the original controlled() total deadline.
                await controlled(hook(self, job), "total", job["limits"]["totalMs"])
            process = await controlled(
                asyncio.create_subprocess_exec(
                    *worker_command(),
                    *worker_owner_arguments(),
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL,
                    env=worker_environment(),
                    limit=self.limits["maxFrameBytes"] + 1,
                ),
                "startup",
                self.limits["startupMs"],
                lambda child: active.update(process=child),
            )
            active["process"] = process
            if job["capability"] in _SEMANTIC_CAPABILITIES:
                frame, maximum = query_transport_limits(job["limits"])
                request = (
                    context["queryRequest"]
                    if job["capability"] == "query.execute"
                    else self.store.worker_semantic_request(job, context)
                )
                encoded = query_encode(request, maximum)
                pieces = query_parts(encoded, frame)
                header = {
                    "capability": job["capability"],
                    "memoryBytes": job["limits"]["maxWorkerMemoryBytes"],
                    "frameBytes": frame,
                    "byteLimit": maximum,
                    "parts": len(pieces),
                    "bytes": len(encoded),
                    "sha256": hashlib.sha256(encoded).hexdigest(),
                }
                for message in [header]:
                    process.stdin.write(query_encode(message, frame) + b"\n")
                    await controlled(process.stdin.drain(), "startup", self.limits["startupMs"])
                for index, text in enumerate(pieces):
                    process.stdin.write(query_encode({"index": index, "text": text}, frame) + b"\n")
                    await controlled(process.stdin.drain(), "startup", self.limits["startupMs"])
                process.stdin.close()
                self._stage(identity, "computing")
                output = await controlled(
                    self._query_output(process, job), "total", job["limits"]["totalMs"]
                )
                self._stage(identity, "reconciling")
                await controlled(process.wait(), "total", job["limits"]["totalMs"])
                if process.returncode == MEMORY_LIMIT_EXIT:
                    raise ServiceFault("RESOURCE_LIMIT", {"resource": "memory"})
                if process.returncode != 0:
                    raise ServiceFault("ENGINE_EXITED")
                if "error" in output:
                    raise ServiceFault(output["error"]["code"], output["error"]["params"])
                commit_boundary("before")
                self._stage(identity, "committing")
                if job["capability"] == "query.execute":
                    self._notify(
                        self.store.finish_query_job(identity, output, hook=commit_boundary)
                    )
                else:
                    self._notify(
                        self.store.finish_semantic_job(identity, output, hook=commit_boundary)
                    )
                return
            raw = json.dumps(
                {
                    "capability": job["capability"],
                    "parameters": parameters,
                    "memoryBytes": self.limits["maxWorkerMemoryBytes"],
                }
            ).encode()
            if len(raw) > self.limits["maxFrameBytes"]:
                raise ServiceFault("RESOURCE_LIMIT", {"resource": "frame"})
            process.stdin.write(raw + b"\n")
            await controlled(process.stdin.drain(), "startup", self.limits["startupMs"])
            process.stdin.close()
            self._stage(identity, "computing")
            reader = JsonlReader(self.limits["maxFrameBytes"])
            complete = False
            rows = None
            state = None
            read_task = asyncio.create_task(process.stdout.read(16384))
            try:
                while not complete:
                    job = self.store.get_job(active["project"], identity)
                    if job["state"] == "cancelling":
                        raise asyncio.CancelledError()
                    if time.monotonic() >= deadline:
                        raise ServiceFault("TIMEOUT", {"phase": "total"})
                    if sys.platform == "darwin" and process.returncode is None:
                        try:
                            if resident_bytes(process.pid) > job["limits"]["maxWorkerMemoryBytes"]:
                                raise ServiceFault("RESOURCE_LIMIT", {"resource": "memory"})
                        except ProcessLookupError:
                            pass  # Child exit is reconciled through its actual exit status.
                    done, _ = await asyncio.wait({read_task}, timeout=0.02)
                    if not done:
                        continue
                    chunk = read_task.result()
                    if not chunk:
                        reader.finish()
                        await controlled(process.wait(), "total", self.limits["totalMs"])
                        if process.returncode == MEMORY_LIMIT_EXIT:
                            raise ServiceFault("RESOURCE_LIMIT", {"resource": "memory"})
                        raise ServiceFault("ENGINE_EXITED")
                    framing_error = None
                    try:
                        messages = reader.feed(chunk)
                    except ProtocolFault as error:
                        messages, framing_error = error.frames, error
                    for message in messages:
                        if not isinstance(message, dict):
                            raise ProtocolFault()
                        if message.get("type") == "failure":
                            raise ServiceFault("INTERNAL_ERROR")
                        if message.get("type") == "round" and job["capability"] == "test.rounds":
                            if (
                                set(message) != {"type", "round", "state"}
                                or type(message["round"]) is not int
                                or not isinstance(message["state"], dict)
                            ):
                                raise ProtocolFault()
                            progress = self.store.get_job(active["project"], identity)[
                                "commitProgress"
                            ]["committedProgress"]
                            if (
                                message["round"]
                                != (progress["lastCommittedRound"] if progress else 0) + 1
                            ):
                                raise ProtocolFault()
                            state = message["state"]
                            self._stage(identity, "committing")
                            self.store.commit_job_round(identity, state, hook=commit_boundary)
                            self._notify(self.store.get_job(active["project"], identity))
                            self._stage(identity, "computing")
                            await asyncio.sleep(
                                0
                            )  # Allow control requests between committed rounds.
                            if (
                                self._test_schedule is not None
                                and (hook := self._test_schedule.get("after_round_commit"))
                                is not None
                            ):
                                # Trusted-test scheduling point 2: the real
                                # commit_job_round, the real notification and
                                # the real stage transition have ALL completed;
                                # the hook runs before the NEXT message in this
                                # same chunk is consumed, so a parked hook makes
                                # the next round structurally uncommittable.
                                # Bounded by the original controlled() total
                                # deadline; cancellation settles the wait.
                                await controlled(
                                    hook(self, job, message["round"]),
                                    "total",
                                    job["limits"]["totalMs"],
                                )
                        elif message.get("type") == "ready" and job["capability"] != "test.rounds":
                            if set(message) != {"type", "rows"} or not isinstance(
                                message["rows"], list
                            ):
                                raise ProtocolFault()
                            rows = message["rows"]
                        elif message == {"type": "complete"}:
                            complete = True
                            break  # No event after a worker terminal frame is applied.
                        else:
                            raise ProtocolFault()
                    if framing_error and not complete:
                        raise framing_error
                    if not complete:
                        read_task = asyncio.create_task(process.stdout.read(16384))
                reader.stop()
            finally:
                if not read_task.done():
                    read_task.cancel()
                await asyncio.gather(read_task, return_exceptions=True)
            self._stage(identity, "reconciling")
            exit_task = asyncio.create_task(process.wait())
            while process.returncode is None:
                if self.store.get_job(active["project"], identity)["state"] == "cancelling":
                    raise asyncio.CancelledError()
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise ServiceFault("TIMEOUT", {"phase": "total"})
                await asyncio.wait({exit_task}, timeout=min(0.02, remaining))
            if process.returncode != 0:
                raise ServiceFault("ENGINE_EXITED")
            if self.store.get_job(active["project"], identity)["state"] == "cancelling":
                raise asyncio.CancelledError()

            commit_boundary("before")
            self._stage(identity, "committing")
            if job["capability"] == "test.atomic":
                job = self.store.commit_job(identity, hook=commit_boundary)
            elif job["capability"] == "test.rounds":
                if state is None:
                    raise ProtocolFault()
                job = self.store.finish_job_run(
                    identity,
                    pending_events=state["pendingEvents"],
                    event_consumption=state["consumedEvents"],
                    hook=commit_boundary,
                )
            else:
                if rows is None:
                    raise ProtocolFault()
                job = self.store.finish_read_job(identity, rows, hook=commit_boundary)
            self._notify(job)
        except asyncio.CancelledError:
            process = process or active["process"]
            if process and process.returncode is None:
                _signal_worker(process, force=False)
                try:
                    await asyncio.wait_for(process.wait(), self.limits["cancelGraceMs"] / 1000)
                except TimeoutError:
                    _signal_worker(process, force=True)
                    await process.wait()
            job = self.store.get_job(active["project"], identity)
            if job["state"] == "cancelling":
                self._notify(self.store.cancelled_job(identity))
            else:
                self._notify(self.store.fail_job(identity, safe_error("ENGINE_EXITED")))
        except Exception as error:
            process = process or active["process"]
            if process and process.returncode is None:
                _signal_worker(process, force=True)
                await process.wait()
            self._notify(self.store.fail_job(identity, classify(error, profile=self.profile)))
        finally:
            self.active.pop(identity, None)

    async def _query_output(self, process, job):
        """Private query stream: complete is evidence only after strict EOF and exit.

        Unlike legacy test streams, every post-terminal byte/frame is rejected.
        The caller separately reconciles the actual child exit and cancel fence.
        """
        frame, maximum = query_transport_limits(job["limits"])
        reader = JsonlReader(frame)
        pieces, size = [], 0
        done = complete = False
        failure = None
        while True:
            raw = await process.stdout.read(min(16384, frame + 1))
            if not raw:
                reader.finish()
                await process.wait()
                if process.returncode == MEMORY_LIMIT_EXIT:
                    raise ServiceFault("RESOURCE_LIMIT", {"resource": "memory"})
                break
            for message in reader.feed(raw):
                if complete or type(message) is not dict:
                    raise ProtocolFault()
                kind = message.get("type")
                if kind == "query.chunk" and not done and failure is None:
                    if (
                        set(message) != {"type", "index", "text"}
                        or type(message["index"]) is not int
                        or message["index"] != len(pieces)
                        or type(message["text"]) is not str
                        or not message["text"]
                        or len(message["text"]) > (frame - 256) // 12
                    ):
                        raise ProtocolFault()
                    text = message["text"].encode("utf-8", errors="strict")
                    if len(text) > maximum - size:
                        raise ProtocolFault()
                    size += len(text)
                    pieces.append(text)
                elif kind == "query.done" and not done and failure is None:
                    if (
                        set(message) != {"type", "parts", "bytes", "sha256"}
                        or type(message["parts"]) is not int
                        or message["parts"] != len(pieces)
                        or not pieces
                        or type(message["bytes"]) is not int
                        or message["bytes"] != size
                        or message["sha256"] != hashlib.sha256(b"".join(pieces)).hexdigest()
                    ):
                        raise ProtocolFault()
                    done = True
                elif kind == "query.error" and not done and failure is None and not pieces:
                    if set(message) != {"type", "error"} or not CONTRACT.validate(
                        "error", message["error"]
                    ):
                        raise ProtocolFault()
                    failure = message["error"]
                elif message == {"type": "complete"} and (done or failure is not None):
                    complete = True
                else:
                    raise ProtocolFault()
        if not complete:
            raise ProtocolFault()
        if failure is not None:
            return {"error": failure}
        output = query_decode(b"".join(pieces), maximum)
        if type(output) is not dict or set(output) != {"payload", "rows"}:
            raise ProtocolFault()
        return output

    async def stop(self) -> None:
        self.closed = True
        if self.mainline is not None:
            self.mainline.close()
        for task in list(self.tasks):
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.subscriptions.clear()


async def serve(
    *,
    profile="legacy2",
    backup_path=None,
    library_file_identity=None,
    library_require_existing=False,
    ordinary_authority=None,
    query_dispatch=None,
    example_provider=None,
    _test_schedule=None,
) -> dict:
    if profile not in {"legacy2", "business3"}:
        raise ValueError("INVALID_PROFILE")
    if example_provider is not None and profile != "business3":
        raise ValueError("INVALID_PROFILE")
    if type(library_require_existing) is not bool or (
        library_require_existing and library_file_identity is None
    ):
        raise ValueError("INVALID_LIBRARY_IDENTITY")
    if library_file_identity is not None and profile != "business3":
        raise ValueError("INVALID_LIBRARY_IDENTITY")
    if backup_path is not None and (profile != "business3" or not Path(backup_path).is_absolute()):
        raise ValueError("INVALID_BACKUP")
    if _test_schedule is not None and os.environ.get("ONTOLEARN_TEST_MODE") != "1":
        # Internal entry for trusted test objects only, mirroring the
        # Coordinator's own refusal; never reachable from the CLI or wire.
        raise ValueError("INVALID_TEST_INJECTION")
    from ontolearn_engine.job_store import JobStore

    inbox = queue.Queue(maxsize=64)
    stopped = threading.Event()
    thread = None
    reader_state = {
        "threadCreated": False,
        "threadStartAttempted": False,
        "threadStarted": False,
        "stopRequested": False,
        "readerCreated": False,
        "readerStopAttempted": False,
        "readerStopped": False,
        "threadFinished": False,
        "threadAlive": False,
        "settled": False,
        "queryCleanupAttempted": False,
        "queryCleanupSettled": False,
    }

    def read() -> None:
        reader = JsonlReader()
        reader_state["readerCreated"] = True
        try:
            while not stopped.is_set():
                # The daemon may still be blocked when a session-fatal request
                # closes the transport. Raw fd reads hold no BufferedReader lock
                # that could abort interpreter shutdown; normal cleanup still runs.
                chunk = os.read(sys.stdin.fileno(), 16384)
                if not chunk:
                    reader.finish()
                    break
                framing_error = None
                try:
                    frames = reader.feed(chunk)
                except ProtocolFault as error:
                    frames, framing_error = error.frames, error
                for frame in frames:
                    while not stopped.is_set():
                        try:
                            inbox.put(frame, timeout=0.05)
                            break
                        except queue.Full:
                            continue
                if framing_error:
                    raise framing_error
        except ProtocolFault:
            pass
        finally:
            # The reading thread exclusively owns parser state. The main thread
            # only requests stop; it cannot clear the buffer during feed().
            reader_state["readerStopAttempted"] = True
            reader.stop()
            reader_state["readerStopped"] = reader.terminal
            while not stopped.is_set():
                try:
                    inbox.put(None, timeout=0.05)
                    break
                except queue.Full:
                    continue
            reader_state["threadFinished"] = True

    temporary = store = coordinator = None
    previous_signal = None
    signal_installed = False
    initialization = True
    failure = None
    cleanup_failures = []
    try:
        temporary = tempfile.TemporaryDirectory(prefix="ontolearn-session-")
        database = os.environ.get("ONTOLEARN_DB_PATH", str(Path(temporary.name) / "engine.sqlite"))
        Path(database).parent.mkdir(parents=True, exist_ok=True)
        store = JobStore(
            database,
            contract=CONTRACT,
            target_format=3 if profile == "business3" else 2,
            backup_path=backup_path,
            **(
                {
                    "file_identity": library_file_identity,
                    "require_existing_format": library_require_existing,
                }
                if library_file_identity is not None
                else {}
            ),
        )
        if (
            profile == "business3"
            and isinstance(store, _BOOTSTRAP_JOB_STORE)
            and os.environ.get("ONTOLEARN_TEST_MODE") != "1"
            and ordinary_authority is None
            and query_dispatch is None
        ):
            from ontolearn_engine.project.mainline import prepare_mainline_store

            # The same original Store/lease restriction already covers startup
            # reconciliation before any MainlineHost or caller reply exists.
            prepare_mainline_store(store)
        store.reconcile_jobs()  # Same lifetime lease; no old worker can commit.
        allowed = json.loads(os.environ.get("ONTOLEARN_ALLOWED_PROJECTS", "[]"))
        if not isinstance(allowed, list) or any(not CONTRACT.validate("id", p) for p in allowed):
            raise ValueError("INVALID_PROJECT_AUTHORIZATION")
        coordinator = Coordinator(
            store,
            test_mode=os.environ.get("ONTOLEARN_TEST_MODE") == "1",
            allowed_projects=set(allowed),
            profile=profile,
            _ready=_JOB_READY,
            ordinary_authority=ordinary_authority,
            query_dispatch=query_dispatch,
            example_provider=example_provider,
            _test_schedule=_test_schedule,
        )
        loop = asyncio.get_running_loop()
        previous_signal = signal.signal(
            signal.SIGTERM,
            lambda *_: loop.call_soon_threadsafe(setattr, coordinator, "closed", True),
        )
        signal_installed = True
        thread = threading.Thread(target=read, daemon=True)
        reader_state["threadCreated"] = True
        reader_state["threadStartAttempted"] = True
        thread.start()
        reader_state["threadStarted"] = True
        initialization = False
        # W4-04 same-thread reentrant cancellation: while a synchronous
        # project.scenario.run occupies the loop, its round-boundary checks
        # drain the inbox here. Non-cancel frames (and the EOF sentinel) are
        # parked FIFO in ``deferred`` and consumed first by the loop below,
        # so no request is ever dropped or reordered; one cancel executes
        # inline at a boundary with no pending write transaction.
        deferred = deque()

        def poll_cancel() -> None:
            while True:
                try:
                    message = inbox.get_nowait()
                except queue.Empty:
                    return
                if message is None:
                    deferred.append(message)
                    return
                if not (
                    isinstance(message, dict) and message.get("method") == "project.scenario.cancel"
                ):
                    deferred.append(message)
                    continue
                response = None
                try:
                    response = coordinator.request(message)
                    coordinator.emit(response)
                    request_id = message.get("id")
                    response = None  # Drop this owner alias before successful finish.
                    coordinator.finish_query_reply(request_id, emitted=True)
                except BaseException as err:
                    # Same ownership cleanup as the serve loop: release the
                    # reply holding on failure BEFORE sealing the loop closed,
                    # and never let the cleanup fault mask the original error.
                    try:
                        coordinator.finish_query_reply(
                            message.get("id"), emitted=False, failure=err
                        )
                    except BaseException as cleanup:
                        cleanup_failures.append(("queryReadHolding", cleanup))
                    coordinator.closed = True
                    return
                return

        coordinator._poll_cancel = poll_cancel
        store._scenario_cancel_poll = poll_cancel
        handshake_deadline = time.monotonic() + LIMITS["handshakeMs"] / 1000
        while not coordinator.closed:
            if coordinator.session is None and time.monotonic() >= handshake_deadline:
                break
            if deferred:
                value = deferred.popleft()
            else:
                try:
                    value = inbox.get_nowait()
                except queue.Empty:
                    await coordinator.tick()
                    await asyncio.sleep(0.005)
                    continue
            if value is None:
                break
            response = None
            try:
                response = coordinator.request(value)
                coordinator.emit(response)
            except BaseException as error:
                try:
                    coordinator.finish_query_reply(value.get("id"), emitted=False, failure=error)
                except BaseException as cleanup:
                    cleanup_failures.append(("queryReadHolding", cleanup))
                raise
            else:
                request_id = value["id"]
                response = None  # Drop this owner alias before successful finish.
                coordinator.finish_query_reply(request_id, emitted=True)
            await coordinator.tick()
            await asyncio.sleep(0)
    except (ProtocolFault, BrokenPipeError) as error:
        if initialization:
            failure = error
    except BaseException as error:
        failure = error
    finally:
        stopped.set()
        reader_state["stopRequested"] = stopped.is_set()
        if coordinator is not None:
            # Unbind the round-boundary cancel drain before any teardown.
            coordinator._poll_cancel = None
        if store is not None:
            store._scenario_cancel_poll = None
        if thread is not None:
            # is_alive is a bounded observation, not a join or permission to
            # close user stdin. An OS read may remain blocked until process exit.
            try:
                reader_state["threadStarted"] |= getattr(thread, "ident", None) is not None
                reader_state["threadAlive"] = thread.is_alive()
            except BaseException as error:
                reader_state["threadAlive"] = None
                cleanup_failures.append(("readerObservation", error))
        reader_state["settled"] = (thread is None and not reader_state["readerCreated"]) or (
            reader_state["threadStarted"]
            and reader_state["threadFinished"]
            and reader_state["readerStopped"]
            and reader_state["threadAlive"] is False
        )
        if coordinator is not None:
            reader_state["queryCleanupAttempted"] = True
            try:
                # Access and finite snapshot creation are cleanup operations too.
                # A missing/damaged holding book cannot replace the primary
                # initialization failure or silently be treated as empty.
                query_replies = coordinator._query_replies
                if type(query_replies) is not dict or len(query_replies) > 16:
                    raise RuntimeError("QUERY_CLEANUP_UNKNOWN")
                query_cleanup_failed = False
                for request_id in list(query_replies):
                    try:
                        coordinator.finish_query_reply(request_id, emitted=False, failure=failure)
                    except BaseException as error:
                        query_cleanup_failed = True
                        cleanup_failures.append(("queryReadHolding", error))
                if query_replies:
                    raise RuntimeError("QUERY_CLEANUP_UNKNOWN")
                reader_state["queryCleanupSettled"] = not query_cleanup_failed
            except BaseException as error:
                cleanup_failures.append(("queryReadHolding", error))
            try:
                await coordinator.stop()
            except BaseException as error:
                cleanup_failures.append(("coordinator", error))
        for name, action in (
            ("store", store.close if store is not None else None),
            (
                "signal",
                (lambda: signal.signal(signal.SIGTERM, previous_signal))
                if signal_installed
                else None,
            ),
            ("temporary", temporary.cleanup if temporary is not None else None),
        ):
            if action is not None:
                try:
                    action()
                except BaseException as error:
                    cleanup_failures.append((name, error))
    if failure is not None:
        if initialization and profile == "business3" and isinstance(failure, Exception):
            raise StartupInitializationFailure(
                failure, [name for name, _ in cleanup_failures], reader_state
            ) from None
        raise failure
    if cleanup_failures:
        raise cleanup_failures[0][1]
    return dict(reader_state)  # Internal observation only; never a wire ready/cleanup receipt.
