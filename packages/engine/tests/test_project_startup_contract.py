"""Startup mechanisms and injected cleanup faults; not OS-failure evidence."""

import asyncio
import io
import json
import sqlite3
from types import SimpleNamespace

import pytest
from ontolearn_engine import coordinator as runtime
from ontolearn_engine import storage
from ontolearn_engine.__main__ import emit_startup_failure, startup_arguments
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project import format3
from ontolearn_engine.resources import CONTRACT, REGISTRY_HASH
from test_job_store import uid


class Closing:
    def __init__(self, target, name, calls, fail=True):
        self.target, self.name, self.calls, self.fail = target, name, calls, fail

    def __getattr__(self, name):
        return getattr(self.target, name)

    def __setattr__(self, name, value):
        if name == "row_factory":
            self.target.row_factory = value
        else:
            object.__setattr__(self, name, value)

    def close(self):
        self.calls.append(self.name)
        if self.target is not None:
            self.target.close()
        if self.fail:
            raise RuntimeError("injected cleanup failure")


@pytest.mark.parametrize("target", [2, 3])
def test_actual_future_is_typed_and_releases_lease(tmp_path, target):
    path = tmp_path / "future.sqlite"
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA user_version=4")
    for _ in range(2):
        with pytest.raises(storage.UnsupportedProjectFormat):
            JobStore(path, contract=CONTRACT, target_format=target)
    with pytest.raises(ValueError) as bad:
        JobStore(path, contract=CONTRACT, target_format=4)
    assert not isinstance(bad.value, storage.UnsupportedProjectFormat)


@pytest.mark.parametrize(
    "target,job,parent_failure",
    [(2, False, True), (2, True, True), (3, False, True), (3, True, True), (3, True, False)],
)
def test_constructor_primary_survives_each_owned_close(
    tmp_path, monkeypatch, job, parent_failure, target
):
    calls = []
    primary = storage.UnsupportedProjectFormat("primary internal reason")
    connect = sqlite3.connect
    monkeypatch.setattr(
        storage.sqlite3, "connect", lambda *a, **kw: Closing(connect(*a, **kw), "db", calls)
    )
    monkeypatch.setattr(format3, "acquire_lease", lambda path: Closing(None, "format3", calls))
    if job:
        monkeypatch.setattr(
            JobStore,
            "_lock",
            lambda self: setattr(self, "_lease", Closing(self._lease, "legacy", calls)),
        )
    if parent_failure:

        def migrate(*args, **kwargs):
            raise primary

        monkeypatch.setattr(storage.Store, "_migrate", migrate)
    else:

        def migrate_job(*args, **kwargs):
            raise primary

        monkeypatch.setattr(JobStore, "_migrate_job3", migrate_job)
    cls = JobStore if job else storage.Store
    obj = cls.__new__(cls)
    with pytest.raises(storage.UnsupportedProjectFormat) as caught:
        obj.__init__(
            tmp_path / "db", target_format=target, **({"contract": CONTRACT} if job else {})
        )
    assert caught.value is primary
    assert calls == ["db"] + (["format3"] if target == 3 else []) + (
        ["legacy"] if job and target == 2 else []
    )
    assert [name for name, _ in obj._cleanup_failures] == [
        {"db": "database", "format3": "format3Lease", "legacy": "legacyLease"}[name]
        for name in calls
    ]


@pytest.mark.parametrize(
    "code", ["PROJECT_FORMAT_UNSUPPORTED", "STORAGE_BUSY", "STORAGE_FAILURE", "INTERNAL_ERROR"]
)
def test_complete_startup_bytes_and_normal_errors_stay_separate(monkeypatch, code):
    output = io.BytesIO()
    monkeypatch.setattr("sys.stdout", SimpleNamespace(buffer=output))
    emit_startup_failure(CONTRACT, REGISTRY_HASH, code)
    raw = output.getvalue()
    assert raw.endswith(b"\n") and b"\r" not in raw and raw.count(b"\n") == 1
    value = json.loads(raw)
    assert set(value) == {"kind", "diagnosticVersion", "engineSessionId", "registryHash", "error"}
    assert value["error"]["code"] == code
    assert CONTRACT.validate_startup_failure(value, len(raw) - 1, REGISTRY_HASH)
    if code == "PROJECT_FORMAT_UNSUPPORTED":
        assert not CONTRACT.validate("error", value["error"])
        assert not CONTRACT.validate_business3("error", value["error"])


@pytest.mark.parametrize(
    "arguments",
    [
        ["--t01-internal-profile=legacy2"],
        ["--t01-internal-profile=business3"] * 2,
        ["--unknown"],
        ["--t01-internal-backup=relative"],
        ["--t01-internal-backup="],
        ["--t01-internal-backup=/absolute"],
        [
            "--t01-internal-profile=business3",
            "--t01-internal-backup=/a",
            "--t01-internal-backup=/b",
        ],
    ],
)
def test_cli_rejects_unknown_conflicting_or_untrusted_arguments(arguments):
    with pytest.raises(ValueError):
        startup_arguments(arguments)


def test_profile_does_not_come_from_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("ONTOLEARN_INTERNAL_PROFILE", "business3")
    monkeypatch.setenv("ONTOLEARN_TARGET_FORMAT", "3")
    assert startup_arguments([]) == ("legacy2", None)
    backup = str(tmp_path / "backup.sqlite")
    assert startup_arguments(
        ["--t01-internal-profile=business3", f"--t01-internal-backup={backup}"]
    ) == (
        "business3",
        backup,
    )


@pytest.mark.parametrize(
    "error,expected",
    [
        (storage.UnsupportedProjectFormat("secret"), "PROJECT_FORMAT_UNSUPPORTED"),
        (format3.Format3Fault("leaseBusy"), "STORAGE_BUSY"),
        (format3.Format3Fault("structure"), "STORAGE_FAILURE"),
        (format3.Format3Fault("format"), "INTERNAL_ERROR"),
        (format3.Format3Fault("backupRequired"), "INTERNAL_ERROR"),
        (format3.Format3Fault("backupExists"), "INTERNAL_ERROR"),
        (format3.Format3Fault("sourceChanged"), "INTERNAL_ERROR"),
        (OSError("secret path"), "INTERNAL_ERROR"),
        (ValueError("Unsupported future project format"), "INTERNAL_ERROR"),
    ],
)
def test_startup_categories_require_real_typed_evidence(error, expected):
    assert runtime.startup_code(error) == expected


@pytest.mark.parametrize(
    "primary,expected",
    [
        (sqlite3.SQLITE_BUSY, "STORAGE_BUSY"),
        (sqlite3.SQLITE_LOCKED, "STORAGE_BUSY"),
        (sqlite3.SQLITE_IOERR, "STORAGE_FAILURE"),
        (sqlite3.SQLITE_FULL, "STORAGE_FAILURE"),
        (sqlite3.SQLITE_READONLY, "STORAGE_FAILURE"),
        (sqlite3.SQLITE_CORRUPT, "STORAGE_FAILURE"),
        (sqlite3.SQLITE_CONSTRAINT, "INTERNAL_ERROR"),
    ],
)
def test_injected_sqlite_codes_are_not_claimed_as_os_faults(primary, expected):
    error = sqlite3.OperationalError("injected only")
    error.sqlite_errorcode = primary | (3 << 8)
    assert runtime.startup_code(error) == expected


def request(method="hello", params=None, session=None, version=2):
    return {
        "kind": "request",
        "id": uid(),
        "protocolVersion": version,
        "engineSessionId": session,
        "method": method,
        "params": {"supportedVersions": [3], "clientId": uid()} if params is None else params,
    }


def test_service_fault_keeps_three_version_before_legacy_projection():
    error = runtime.ServiceFault("VERSION_INCOMPATIBLE", {"supportedVersions": [3]})
    assert error.error["code"] == "INTERNAL_ERROR"  # Original2 formatter remains strict.
    result = runtime.classify(error, profile="business3")
    assert result["code"] == "VERSION_INCOMPATIBLE" and result["params"] == {
        "supportedVersions": [3]
    }


def test_coordinator_requires_actual_ready_and_strict_three(tmp_path):
    store = JobStore(tmp_path / "db", target_format=3, contract=CONTRACT)
    try:
        with pytest.raises(runtime.ServiceFault):
            runtime.Coordinator(store)
        with pytest.raises(runtime.ServiceFault):
            runtime.Coordinator(store, profile="business3")
        store.reconcile_jobs()
        coordinator = runtime.Coordinator(store, profile="business3", _ready=runtime._JOB_READY)
        hello = coordinator.request(request())
        assert hello["protocolVersion"] == 2 and hello["result"]["selectedVersion"] == 3
        assert CONTRACT.validate_business3("response", hello)
        session = hello["engineSessionId"]
        ping = coordinator.request(request("session.ping", {"nonce": uid()}, session, 3))
        assert ping["protocolVersion"] == 3 and ping["ok"]
        with pytest.raises(runtime.ProtocolFault):
            coordinator.request(request("session.ping", {"nonce": uid()}, session, 2))
        with pytest.raises(runtime.ProtocolFault):
            coordinator.request(request())
    finally:
        store.close()


@pytest.mark.parametrize("mode", ["incompatible", "params", "session"])
def test_rejected_three_bootstrap_closes_with_finite_error(tmp_path, mode):
    store = JobStore(tmp_path / "db", target_format=3, contract=CONTRACT)
    try:
        coordinator = runtime.Coordinator(store, profile="business3", _ready=runtime._JOB_READY)
        q = request()
        if mode == "incompatible":
            q["params"]["supportedVersions"] = [2]
        elif mode == "params":
            q["params"] = {}
        else:
            q["engineSessionId"] = uid()
        response = coordinator.request(q)
        assert not response["ok"] and coordinator.closed and coordinator.session is None
        assert CONTRACT.validate_business3("response", response)
        assert (
            response["error"]["code"]
            == {
                "incompatible": "VERSION_INCOMPATIBLE",
                "params": "INVALID_REQUEST",
                "session": "SESSION_MISMATCH",
            }[mode]
        )
    finally:
        store.close()


@pytest.mark.parametrize(
    "failed_phase",
    ["temporary", "store", "reconcile", "allowed", "coordinator", "signal", "thread"],
)
def test_serve_initialization_and_secondary_cleanup_preserve_first(
    tmp_path, monkeypatch, failed_phase
):
    calls = []
    primary = storage.UnsupportedProjectFormat("first")

    def at(phase):
        calls.append(phase)
        if failed_phase == phase:
            raise primary

    class Temporary:
        def __init__(self, **kwargs):
            at("temporary")
            self.name = str(tmp_path)

        def cleanup(self):
            calls.append("cleanup-temp")
            raise RuntimeError("secondary")

    class FakeStore:
        def __init__(self, *a, **kw):
            at("store")

        def reconcile_jobs(self):
            at("reconcile")

        def close(self):
            calls.append("cleanup-store")
            raise RuntimeError("secondary")

    class FakeCoordinator:
        def __init__(self, *a, **kw):
            at("coordinator")
            self.closed = False

        async def stop(self):
            calls.append("cleanup-coordinator")
            raise RuntimeError("secondary")

    class Thread:
        ident = None

        def is_alive(self):
            return False

        def __init__(self, **kw):
            pass

        def start(self):
            at("thread")

    real_signal = runtime.signal.signal

    def signal(*args):
        if args[0] != runtime.signal.SIGTERM:
            return real_signal(*args)
        if "signal" in calls:
            calls.append("cleanup-signal")
            raise RuntimeError("secondary")
        at("signal")
        return object()

    monkeypatch.setattr(runtime.tempfile, "TemporaryDirectory", Temporary)
    monkeypatch.setattr("ontolearn_engine.job_store.JobStore", FakeStore)
    monkeypatch.setattr(runtime, "Coordinator", FakeCoordinator)
    monkeypatch.setattr(runtime.signal, "signal", signal)
    monkeypatch.setattr(runtime.threading, "Thread", Thread)
    monkeypatch.setenv(
        "ONTOLEARN_ALLOWED_PROJECTS", "invalid-json" if failed_phase == "allowed" else "[]"
    )
    with pytest.raises(runtime.StartupInitializationFailure) as caught:
        asyncio.run(runtime.serve(profile="business3"))
    if failed_phase == "allowed":
        assert isinstance(caught.value.cause, json.JSONDecodeError)
    else:
        assert caught.value.cause is primary
    acquired_store = failed_phase not in {"temporary", "store"}
    assert ("cleanup-store" in calls) == acquired_store
    assert ("cleanup-temp" in calls) == (failed_phase != "temporary")
    assert ("cleanup-coordinator" in calls) == (failed_phase in {"signal", "thread"})
    assert ("cleanup-signal" in calls) == (failed_phase == "thread")
    state = caught.value.reader_state
    assert state["stopRequested"]
    assert state["threadStartAttempted"] == (failed_phase == "thread")
    assert not state["threadStarted"] and not state["readerCreated"]
    assert not state["readerStopped"] and not state["readerStopAttempted"]
    assert state["threadAlive"] is False


@pytest.mark.parametrize("write_mode", ["raise", "partial", "flush"])
def test_diagnostic_write_failure_never_claims_delivery(monkeypatch, write_mode):
    class Output:
        def write(self, raw):
            if write_mode == "raise":
                raise BrokenPipeError()
            return len(raw) - 1 if write_mode == "partial" else len(raw)

        def flush(self):
            if write_mode == "flush":
                raise BrokenPipeError()

    monkeypatch.setattr("sys.stdout", SimpleNamespace(buffer=Output()))
    with pytest.raises(BrokenPipeError):
        emit_startup_failure(CONTRACT, REGISTRY_HASH, "INTERNAL_ERROR")


def test_bare_store_three_cannot_be_job_ready_even_with_private_sentinel(tmp_path):
    store = storage.Store(tmp_path / "db", target_format=3)
    try:
        with pytest.raises(runtime.ServiceFault):
            runtime.Coordinator(store, profile="business3", _ready=runtime._JOB_READY)
    finally:
        store.close()


def test_started_blocked_reader_is_requested_not_falsely_settled(tmp_path, monkeypatch):
    import threading

    entered, release = threading.Event(), threading.Event()
    threads, stop_threads = [], []
    actual_thread, actual_read = threading.Thread, runtime.os.read
    actual_reader = runtime.JsonlReader
    sentinel = 987654

    class Reader(actual_reader):
        def stop(self):
            stop_threads.append(threading.get_ident())
            super().stop()

    def thread(*args, **kwargs):
        result = actual_thread(*args, **kwargs)
        threads.append(result)
        return result

    def read(fd, size):
        if fd != sentinel:
            return actual_read(fd, size)
        entered.set()
        assert release.wait(5)
        return b""

    async def tick(self):
        if entered.is_set():
            self.closed = True
        else:
            await asyncio.sleep(0.001)

    monkeypatch.setattr(runtime, "JsonlReader", Reader)
    monkeypatch.setattr(runtime.threading, "Thread", thread)
    monkeypatch.setattr(runtime.os, "read", read)
    monkeypatch.setattr(runtime.sys, "stdin", SimpleNamespace(fileno=lambda: sentinel))
    monkeypatch.setattr(runtime.Coordinator, "tick", tick)
    monkeypatch.setenv("ONTOLEARN_DB_PATH", str(tmp_path / "db"))
    monkeypatch.setenv("ONTOLEARN_ALLOWED_PROJECTS", "[]")
    try:
        observed = asyncio.run(runtime.serve(profile="business3"))
        assert observed["threadCreated"] and observed["threadStartAttempted"]
        assert observed["threadStarted"] and observed["stopRequested"]
        assert observed["readerCreated"] and observed["threadAlive"]
        assert not observed["readerStopAttempted"] and not observed["readerStopped"]
        assert not observed["threadFinished"] and not observed["settled"]
        assert stop_threads == []  # Main never mutates the reader during an OS read/feed.
        reopened = JobStore(tmp_path / "db", contract=CONTRACT, target_format=3)
        reopened.close()
    finally:
        release.set()  # Test-controlled fake read release, never close real user stdin.
        for owned in threads:
            owned.join(timeout=1)
            assert not owned.is_alive()
    assert stop_threads == [threads[0].ident, threads[0].ident]  # EOF finish, then owner finally.
    assert not observed["readerStopped"]  # Returned snapshot remains an honest earlier observation.
