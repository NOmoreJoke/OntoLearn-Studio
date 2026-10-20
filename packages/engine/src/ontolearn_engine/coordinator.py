"""Single application writer; isolated workers never open the SQLite source of truth."""

import asyncio
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
from ontolearn_engine.job_store import JobFault
from ontolearn_engine.memory_guard import MEMORY_LIMIT_EXIT, resident_bytes
from ontolearn_engine.process_environment import worker_environment
from ontolearn_engine.protocol import JsonlReader, ProtocolFault
from ontolearn_engine.resources import CONTRACT, IMPLEMENTATION, LIMITS, REGISTRY_HASH, safe_error
from ontolearn_engine.storage import Conflict

TERMINAL = {"succeeded", "failed", "cancelled"}


class ServiceFault(Exception):
    def __init__(self, code: str, params: dict | None = None):
        self.error = safe_error(code, params)


def classify(error: Exception, *, resource: str = "job", field: str = "params") -> dict:
    if isinstance(error, ServiceFault):
        return error.error
    if isinstance(error, (JobFault, Conflict)):
        return safe_error(error.code, error.params)
    if isinstance(error, sqlite3.Error):
        primary = getattr(error, "sqlite_errorcode", 0) & 0xFF
        if primary in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED}:
            return safe_error("STORAGE_BUSY", {"retryAfterMs": 250})
        if primary in {
            sqlite3.SQLITE_IOERR,
            sqlite3.SQLITE_FULL,
            sqlite3.SQLITE_READONLY,
            sqlite3.SQLITE_CORRUPT,
        }:
            return safe_error("STORAGE_FAILURE")
        return safe_error("INTERNAL_ERROR")
    return safe_error("INTERNAL_ERROR")


def worker_command() -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--worker"]
    return [sys.executable, "-I", "-m", "ontolearn_engine.worker"]


class Coordinator:
    def __init__(
        self,
        store,
        *,
        test_mode: bool = False,
        allowed_projects: set | None = None,
        limits: dict | None = None,
        emit=None,
    ):
        self.store = store
        self.test_mode = test_mode
        self.allowed_projects = allowed_projects or set()
        self.limits = LIMITS | (limits or {})
        if not CONTRACT.validate("limits", self.limits):
            raise ValueError("INVALID_LIMITS")
        self.session = None
        self.seen = set()
        self.subscriptions = {}
        self.queued = deque()
        self.active = {}
        self.closed = False
        self.emit = emit or self._emit
        self.tasks = set()

    @staticmethod
    def _emit(value: dict) -> None:
        raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()
        if len(raw) > LIMITS["maxFrameBytes"]:
            raise ProtocolFault()
        sys.stdout.buffer.write(raw + b"\n")
        sys.stdout.buffer.flush()

    def _authorize(self, params: dict) -> str | None:
        project = params.get("projectId", params.get("binding", {}).get("projectId"))
        if project and project not in self.allowed_projects:
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
                        "protocolVersion": 2,
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
                        "protocolVersion": 2,
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
        if not isinstance(value, dict) or not CONTRACT.validate("id", value.get("id")):
            raise ProtocolFault()
        method = value.get("method")
        if not isinstance(method, str) or method not in CONTRACT.REGISTRY["v2Runtime"]:
            raise ProtocolFault()
        if value["id"] in self.seen or len(self.seen) >= 65536:
            raise ProtocolFault()
        self.seen.add(value["id"])
        required = {"kind", "id", "protocolVersion", "engineSessionId", "method", "params"}
        if set(value) != required or value["kind"] != "request":
            raise ProtocolFault()
        response = {
            "kind": "response",
            "id": value["id"],
            "method": method,
            "protocolVersion": 2,
            "engineSessionId": self.session,
        }
        try:
            if type(value["protocolVersion"]) is not int or value["protocolVersion"] != 2:
                raise ServiceFault("VERSION_INCOMPATIBLE", {"supportedVersions": [2]})
            if method != "hello" and self.session is None:
                raise ServiceFault("HANDSHAKE_REQUIRED")
            if not CONTRACT.validate("params_" + method, value["params"]):
                raise ServiceFault("INVALID_REQUEST", {"field": "params"})
            if method == "hello":
                if self.session is not None:
                    raise ServiceFault("INVALID_STATE")
                if value["engineSessionId"] is not None:
                    raise ServiceFault("SESSION_MISMATCH")
                if 2 not in value["params"]["supportedVersions"]:
                    raise ServiceFault("VERSION_INCOMPATIBLE", {"supportedVersions": [2]})
                self.session = str(uuid4())
                response["engineSessionId"] = self.session
                data = {
                    "selectedVersion": 2,
                    "engineVersion": __version__,
                    "engineSessionId": self.session,
                    "capabilities": CONTRACT.REGISTRY["v2Runtime"],
                    "limits": self.limits,
                    "registryHash": REGISTRY_HASH,
                }
            else:
                if self.session is None:
                    raise ServiceFault("HANDSHAKE_REQUIRED")
                if value["engineSessionId"] != self.session:
                    raise ServiceFault("SESSION_MISMATCH")
                self._authorize(value["params"])
                data = self.dispatch(method, value["params"])
                if (
                    method in {"result.page", "job.list"}
                    and CONTRACT.encoded_size(data) > self.limits["maxPageBytes"]
                ):
                    raise ServiceFault("RESOURCE_LIMIT", {"resource": "page"})
            response.update(ok=True, result=data)
        except Exception as error:
            response.update(
                ok=False,
                error=classify(
                    error,
                    resource="project"
                    if method == "project.get"
                    else "result"
                    if method.startswith("result.")
                    else "job",
                ),
            )
        if not CONTRACT.validate("response", response):
            raise ProtocolFault()
        return response

    def dispatch(self, method: str, p: dict):
        if method == "health":
            return {"status": "ok", "engineVersion": __version__}
        if method == "session.ping":
            return {"nonce": p["nonce"]}
        if method == "project.get":
            return self.store.project_get(p["projectId"])
        if method == "job.get":
            return self.store.get_job(p["projectId"], p["jobId"])
        if method == "job.create":
            if not self.test_mode or p["capability"] not in {
                "test.read",
                "test.atomic",
                "test.rounds",
            }:
                raise ServiceFault("UNSUPPORTED_CAPABILITY")
            if len(self.queued) >= self.limits[
                "maxQueuedJobs"
            ] and not self.store.has_operation_claim(p["operationId"]):
                raise ServiceFault("QUEUE_FULL", {"retryAfterMs": 250})
            job = self.store.create_job(
                p["projectId"],
                p["operationId"],
                p["capability"],
                p["input"],
                p["confirmationRef"],
                IMPLEMENTATION,
                self.limits,
            )
            if job["state"] == "queued" and job["jobId"] not in self.queued:
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

    async def execute(self, identity: str, context: dict, active: dict) -> None:
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

            process = await controlled(
                asyncio.create_subprocess_exec(
                    *worker_command(),
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
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), self.limits["cancelGraceMs"] / 1000)
                except TimeoutError:
                    process.kill()
                    await process.wait()
            job = self.store.get_job(active["project"], identity)
            if job["state"] == "cancelling":
                self._notify(self.store.cancelled_job(identity))
            else:
                self._notify(self.store.fail_job(identity, safe_error("ENGINE_EXITED")))
        except Exception as error:
            process = process or active["process"]
            if process and process.returncode is None:
                process.kill()
                await process.wait()
            self._notify(self.store.fail_job(identity, classify(error)))
        finally:
            self.active.pop(identity, None)

    async def stop(self) -> None:
        self.closed = True
        for task in list(self.tasks):
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.subscriptions.clear()


async def serve() -> None:
    from ontolearn_engine.job_store import JobStore

    inbox = queue.Queue(maxsize=64)
    stopped = threading.Event()

    def read() -> None:
        reader = JsonlReader()
        try:
            while not stopped.is_set():
                chunk = sys.stdin.buffer.read1(16384)
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
            reader.stop()
            while not stopped.is_set():
                try:
                    inbox.put(None, timeout=0.05)
                    break
                except queue.Full:
                    continue

    temporary = tempfile.TemporaryDirectory(prefix="ontolearn-session-")
    database = os.environ.get("ONTOLEARN_DB_PATH", str(Path(temporary.name) / "engine.sqlite"))
    Path(database).parent.mkdir(parents=True, exist_ok=True)
    store = JobStore(database, contract=CONTRACT)
    store.reconcile_jobs()  # OS writer lease acquired by constructor, no old worker can commit.
    allowed = json.loads(os.environ.get("ONTOLEARN_ALLOWED_PROJECTS", "[]"))
    if not isinstance(allowed, list) or any(not CONTRACT.validate("id", p) for p in allowed):
        raise ValueError("INVALID_PROJECT_AUTHORIZATION")
    coordinator = Coordinator(
        store, test_mode=os.environ.get("ONTOLEARN_TEST_MODE") == "1", allowed_projects=set(allowed)
    )
    loop = asyncio.get_running_loop()
    previous_signal = signal.signal(
        signal.SIGTERM, lambda *_: loop.call_soon_threadsafe(setattr, coordinator, "closed", True)
    )
    thread = threading.Thread(target=read, daemon=True)
    thread.start()
    handshake_deadline = time.monotonic() + LIMITS["handshakeMs"] / 1000
    try:
        while not coordinator.closed:
            try:
                value = inbox.get_nowait()
            except queue.Empty:
                if coordinator.session is None and time.monotonic() > handshake_deadline:
                    break
                await coordinator.tick()
                await asyncio.sleep(0.005)
                continue
            if value is None:
                break
            coordinator.emit(coordinator.request(value))
            await coordinator.tick()
            await asyncio.sleep(0)  # A continuously nonempty inbox must not starve workers/cancel.
    except (ProtocolFault, BrokenPipeError):
        pass
    finally:
        stopped.set()
        await coordinator.stop()
        store.close()
        signal.signal(signal.SIGTERM, previous_signal)
        temporary.cleanup()
