"""Real Python coordinator/isolated worker/SQLite integration; no Electron windows."""

import errno
import hashlib
import json
import os
import queue
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path
from uuid import uuid4

import pytest
from ontolearn_engine.process_environment import worker_environment
from ontolearn_engine.resources import CONTRACT


class Session:
    def __init__(self, database, projects, test_mode=True):
        env = os.environ | {
            "ONTOLEARN_DB_PATH": str(database),
            "ONTOLEARN_ALLOWED_PROJECTS": json.dumps(projects),
        }
        if test_mode:
            env["ONTOLEARN_TEST_MODE"] = "1"
        else:
            env.pop("ONTOLEARN_TEST_MODE", None)
        command = (
            [os.environ["ONTOLEARN_TEST_ENGINE"]]
            if os.environ.get("ONTOLEARN_TEST_ENGINE")
            else [sys.executable, "-I", "-m", "ontolearn_engine"]
        )
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        self.inbox = queue.Queue()
        self.notifications = []
        self.session = None

        def read():
            for line in self.process.stdout:
                self.inbox.put(json.loads(line))

        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()
        hello = self.call("hello", {"supportedVersions": [2], "clientId": str(uuid4())})
        self.session = hello["engineSessionId"]

    def call(self, method, params):
        request = {
            "kind": "request",
            "id": str(uuid4()),
            "protocolVersion": 2,
            "engineSessionId": None if method == "hello" else self.session,
            "method": method,
            "params": params,
        }
        self.process.stdin.write(json.dumps(request).encode() + b"\n")
        self.process.stdin.flush()
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            value = self.inbox.get(timeout=max(0.01, deadline - time.monotonic()))
            assert CONTRACT.validate(
                "notification" if value["kind"] == "notification" else "response", value
            )
            if value["kind"] == "notification":
                self.notifications.append(value)
                continue
            assert value["id"] == request["id"] and value["method"] == method
            if not value["ok"]:
                return value["error"]
            return value["result"]
        raise AssertionError("request deadline")

    def job(self, project, identity):
        return self.call("job.get", {"projectId": project, "jobId": identity})

    def terminal(self, project, identity, timeout=8):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            job = self.job(project, identity)
            if job["state"] in {"failed", "cancelled", "succeeded"}:
                return job
            time.sleep(0.02)
        raise AssertionError("job deadline")

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.close()
            self.process.wait(timeout=8)
        assert self.process.stderr.read() == b""
        self.process.stdout.close()
        self.process.stderr.close()


def test_default_handshake_deadline_closes_real_source_or_packaged_transport(tmp_path):
    """Same default-duration stdio case runs in check and verify-i04-package.

    The deterministic busy-inbox tests separately pin the exact deadline edge;
    this case verifies default-budget liveness/clean shutdown in the real binary.
    A fast consumer can empty the finite traffic batch before the deadline.
    """
    command = (
        [os.environ["ONTOLEARN_TEST_ENGINE"]]
        if os.environ.get("ONTOLEARN_TEST_ENGINE")
        else [sys.executable, "-I", "-m", "ontolearn_engine"]
    )
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=worker_environment()
        | {
            "ONTOLEARN_DB_PATH": str(tmp_path / "handshake.sqlite"),
            "ONTOLEARN_ALLOWED_PROJECTS": "[]",
        },
    )
    replies = queue.Queue()
    transport_errors = []
    sent = [0]

    def read():
        try:
            for line in process.stdout:
                replies.put(json.loads(line))
        except Exception as error:
            transport_errors.append(type(error).__name__)

    def frame():
        return {
            "kind": "request",
            "id": str(uuid4()),
            "protocolVersion": 2,
            "engineSessionId": None,
            "method": "health",
            "params": {},
        }

    def write():
        try:
            while sent[0] < 60000 and time.monotonic() < started + 5.8:
                process.stdin.write(json.dumps(frame()).encode() + b"\n")
                sent[0] += 1
            process.stdin.flush()
        except BrokenPipeError:
            pass  # Expected: the server closes while the caller still owns stdin.
        except Exception as error:
            transport_errors.append(type(error).__name__)

    reader = threading.Thread(target=read, daemon=True)
    writer = None
    reader.start()
    try:
        process.stdin.write(json.dumps(frame()).encode() + b"\n")
        process.stdin.flush()
        first = replies.get(timeout=8)
        assert first["error"]["code"] == "HANDSHAKE_REQUIRED"
        started = time.monotonic()
        writer = threading.Thread(target=write, daemon=True)
        writer.start()
        assert process.wait(timeout=7) == 0  # Do not close stdin to trigger EOF.
        elapsed = time.monotonic() - started
        writer.join(timeout=2)
        reader.join(timeout=2)
        assert not writer.is_alive() and not reader.is_alive()
        assert sent[0] > 0 and elapsed < 6
        assert process.stderr.read() == b"" and not transport_errors
        observed = [first]
        while not replies.empty():
            observed.append(replies.get_nowait())
        for value in observed:
            assert CONTRACT.validate("response", value)
            assert value["method"] == "health" and value["engineSessionId"] is None
            assert value["ok"] is False and value["error"] == {
                "code": "HANDSHAKE_REQUIRED",
                "messageKey": "protocol.handshakeRequired",
                "params": {},
                "retryable": False,
            }
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=3)
        if writer:
            writer.join(timeout=2)
        reader.join(timeout=2)
        try:
            process.stdin.close()
        except OSError as error:
            # Windows may report EINVAL when BufferedWriter.close retries the
            # pending flush after the peer has already exited. This is cleanup;
            # the transport and natural-exit assertions above still apply.
            if not isinstance(error, BrokenPipeError) and not (
                sys.platform == "win32"
                and error.errno == errno.EINVAL
                and process.poll() is not None
            ):
                raise
        process.stdout.close()
        process.stderr.close()


@pytest.fixture
def prepared(tmp_path):
    from ontolearn_engine.job_store import JobStore

    database = tmp_path / "runtime.sqlite"
    store = JobStore(database, contract=CONTRACT)
    store.create_project("first")
    store.create_project("second")
    projects = [store.public_project(p) for p in ["first", "second"]]
    yield database, store, projects
    if not store._lease.closed:
        store.close()


def prepare(store, project, capability, parameters, plan=None):
    input_ = {
        "inputSnapshotId": store.project_get(project)["inputSnapshotId"],
        "scope": "scenario" if capability == "test.rounds" else "asserted",
        "definitionId": "infrastructure-probe",
        "parametersHash": store.put_blob(project, parameters),
        "derivedResultIds": [],
        "preparedPlanRef": None,
    }
    confirmation = None
    if plan is not None:
        confirmation_record = store.prepare_plan(
            project,
            store.project_get(project)["projectRevision"],
            plan,
            actor=str(uuid4()),
            permission="write",
        )
        input_["preparedPlanRef"] = confirmation_record["preparedPlanRef"]
        confirmation = confirmation_record["confirmationRef"]
    return {
        "projectId": project,
        "operationId": str(uuid4()),
        "capability": capability,
        "input": input_,
        "confirmationRef": confirmation,
    }


def test_real_health_reuses_pid_and_rejects_test_capability_in_product_mode(prepared):
    database, store, projects = prepared
    params = prepare(store, projects[0], "test.read", {})
    store.close()
    session = Session(database, projects, test_mode=False)
    try:
        pid = session.process.pid
        for _ in range(5):
            assert session.call("health", {}) == {"status": "ok", "engineVersion": "0.1.0"}
        assert session.process.pid == pid
        assert session.call("job.create", params)["code"] == "UNSUPPORTED_CAPABILITY"
    finally:
        session.close()


def test_busy_worker_cancel_ping_and_other_worker_crash_isolation(prepared):
    database, store, projects = prepared
    busy = prepare(store, projects[0], "test.read", {"workMs": 2000})
    crash = prepare(store, projects[1], "test.read", {"crashRound": 1})
    store.close()
    session = Session(database, projects)
    try:
        job = session.call("job.create", busy)
        other = session.call("job.create", crash)
        started = time.monotonic()
        nonce = str(uuid4())
        assert session.call("session.ping", {"nonce": nonce}) == {"nonce": nonce}
        assert time.monotonic() - started < 1.5
        decision = session.call("job.cancel", {"projectId": projects[0], "jobId": job["jobId"]})
        assert decision["disposition"] in {"accepted", "alreadyRequested"}
        assert session.terminal(projects[0], job["jobId"])["state"] == "cancelled"
        assert session.terminal(projects[1], other["jobId"])["state"] == "failed"
        assert session.call("health", {})["status"] == "ok"
    finally:
        session.close()


@pytest.mark.parametrize("generate,expected", [(0, 0), (1, 3)])
def test_real_rounds_summary_stable_paging_and_no_formal_changes(prepared, generate, expected):
    database, store, projects = prepared
    request = prepare(
        store,
        projects[0],
        "test.rounds",
        {"maxRounds": 3, "consumePerRound": 0, "generatePerRound": generate},
    )
    revision = store.project_get(projects[0])["projectRevision"]
    store.close()
    session = Session(database, projects)
    try:
        job = session.call("job.create", request)
        job = session.terminal(projects[0], job["jobId"])
        assert job["state"] == "succeeded", job
        assert job["commitProgress"]["committedProgress"]["lastCommittedRound"] == 3
        result = session.call(
            "result.get", {"projectId": projects[0], "resultId": job["resultRef"]["resultId"]}
        )
        binding = {
            "projectId": projects[0],
            "resultId": result["resultId"],
            "inputSnapshotId": result["inputSnapshotId"],
            "scope": result["scope"],
            "parametersHash": result["parametersHash"],
            "order": "ordinal+rowId:asc",
        }
        page = session.call("result.page", {"binding": binding, "pageSize": 1, "cursor": None})
        cells = page["rows"][0]["cells"]
        assert cells[0] == "run.summary.v1" and cells[6] == expected and cells[5] is (expected > 0)
        cursor = page["nextCursor"]
        assert cursor is not None
        rows = []
        while cursor:
            next_page = session.call(
                "result.page", {"binding": binding, "pageSize": 1, "cursor": cursor}
            )
            assert (
                session.call("result.page", {"binding": binding, "pageSize": 1, "cursor": cursor})
                == next_page
            )
            rows.extend(next_page["rows"])
            cursor = next_page["nextCursor"]
        progress = job["commitProgress"]["committedProgress"]
        assert [row["ordinal"] for row in rows] == [1, 2, 3]
        assert all(
            row["cells"][0] == "run.round.v1"
            and row["cells"][1] == progress["runId"]
            and row["cells"][5] == job["jobId"]
            for row in rows
        )
        assert len({row["cells"][3] for row in rows}) == 3
        assert (
            session.call("project.get", {"projectId": projects[0]})["projectRevision"] == revision
        )
        newer = session.call("job.create", {**request, "operationId": str(uuid4())})
        assert session.terminal(projects[0], newer["jobId"])["state"] == "succeeded"
    finally:
        session.close()

    from ontolearn_engine.job_store import JobStore

    reopened = JobStore(database, contract=CONTRACT)
    try:
        history_before = reopened.history(progress["runId"])
        assert result["resultId"] in reopened.collect_cache()
        assert reopened.history(progress["runId"]) == history_before
    finally:
        reopened.close()
    restored = Session(database, projects)
    try:
        assert restored.job(projects[0], job["jobId"]) == job
        metadata = restored.call(
            "result.get", {"projectId": projects[0], "resultId": result["resultId"]}
        )
        assert metadata["payloadStatus"] == "evicted"
        for cursor in (None, page["nextCursor"]):
            unavailable = restored.call(
                "result.page", {"binding": binding, "pageSize": 1, "cursor": cursor}
            )
            assert unavailable["code"] == "PAYLOAD_EVICTED"
        assert restored.call("job.create", request)["jobId"] == job["jobId"]
    finally:
        restored.close()


def test_real_atomic_completion_cancel_does_not_rewrite_commit(prepared):
    database, store, projects = prepared
    request = prepare(
        store,
        projects[0],
        "test.atomic",
        {},
        {"definitions": [{"layer": "ontology", "id": "probe", "value": {}}]},
    )
    store.close()
    session = Session(database, projects)
    try:
        job = session.call("job.create", request)
        job = session.terminal(projects[0], job["jobId"])
        assert job["state"] == "succeeded", job
        marker = session.call(
            "operation.get", {"projectId": projects[0], "operationId": request["operationId"]}
        )
        assert marker is not None
        decision = session.call("job.cancel", {"projectId": projects[0], "jobId": job["jobId"]})
        assert decision["disposition"] == "alreadyTerminal" and decision["state"] == "succeeded"
        assert (
            session.call(
                "operation.get", {"projectId": projects[0], "operationId": request["operationId"]}
            )
            == marker
        )
    finally:
        session.close()


@pytest.mark.parametrize("mutation", ["missing", "malformed", "wrong-run", "wrong-snapshot"])
def test_real_worker_summary_corruption_is_safe_at_runtime_read_boundary(prepared, mutation):
    database, store, projects = prepared
    request = prepare(store, projects[0], "test.rounds", {"maxRounds": 2})
    store.close()
    session = Session(database, projects)
    try:
        job = session.call("job.create", request)
        job = session.terminal(projects[0], job["jobId"])
        assert job["state"] == "succeeded"
        result = session.call(
            "result.get", {"projectId": projects[0], "resultId": job["resultRef"]["resultId"]}
        )
        binding = {
            key: result[key]
            for key in ("projectId", "resultId", "inputSnapshotId", "scope", "parametersHash")
        } | {"order": "ordinal+rowId:asc"}
        # Explicit physical fault injection into this synthetic DB only. The workload,
        # terminal and result were produced by the actual worker and Store first.
        with sqlite3.connect(database) as connection:
            payload = json.loads(
                connection.execute(
                    "SELECT payload FROM results WHERE id=?", (result["resultId"],)
                ).fetchone()[0]
            )
            if mutation == "missing":
                payload = []
            elif mutation == "malformed":
                payload[0]["cells"] = ["invalid-summary"]
            else:
                payload[0]["cells"][1 if mutation == "wrong-run" else 3] = "0" * 64
            connection.execute(
                "UPDATE results SET payload=? WHERE id=?",
                (json.dumps(payload), result["resultId"]),
            )
        assert session.call("result.page", {"binding": binding, "pageSize": 1, "cursor": None}) == {
            "code": "INVALID_STATE",
            "messageKey": "protocol.invalidState",
            "params": {},
            "retryable": False,
        }
        assert session.job(projects[0], job["jobId"]) == job
        assert session.call("health", {})["status"] == "ok"
    finally:
        session.close()


SIDECAR_SUFFIXES = ("-journal", "-wal", "-shm")
BOUNDARY_KEYS = (
    "runId",
    "operation",
    "ledger",
    "snapshotPayloads",
    "snapshotHashes",
    "progress",
    "dtoProgress",
    "revision",
    "runs",
    "results",
)


def _reject_links_below_root(candidate, resolved_root):
    """Reject symbolic links in every ORIGINAL path component strictly below
    the allowed root — resolve() alone would silently follow them."""
    for depth in range(1, len(candidate.parts) + 1):
        ancestor = Path(*candidate.parts[:depth])
        if ancestor == resolved_root or resolved_root not in ancestor.parents:
            continue
        if ancestor.is_symlink():
            raise ValueError("rejected: symbolic link in path")


def _confined_existing_file(raw, allowed_root):
    """Resolve one existing source file inside the exclusive pytest tmp_path
    root: any '..' component is rejected outright, symbolic links anywhere
    below the root are rejected, containment is proven with resolve() +
    relative_to (never a string prefix), and the result must be a regular
    file."""
    candidate = Path(raw)
    if any(part == ".." for part in candidate.parts):
        raise ValueError("rejected: '..' path component")
    root = allowed_root.resolve(strict=True)
    _reject_links_below_root(candidate, root)
    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError:
        raise ValueError("rejected: path escapes the allowed root") from None
    if not resolved.is_file():
        raise ValueError("rejected: not a regular file")
    return resolved


def _confined_new_directory(raw, allowed_root, keep_out):
    """Validate and exclusively create the forensic target directory: no '..'
    components, no symlink at the location, inside the allowed root, neither
    the root itself nor the source directory; creation fails on any existing
    directory, and validation happens before anything is written."""
    candidate = Path(raw)
    if any(part == ".." for part in candidate.parts):
        raise ValueError("rejected: '..' path component")
    if candidate.is_symlink():
        raise ValueError("rejected: target location is a symbolic link")
    resolved = candidate.resolve(strict=False)
    root = allowed_root.resolve(strict=True)
    _reject_links_below_root(candidate, root)
    try:
        resolved.relative_to(root)
    except ValueError:
        raise ValueError("rejected: target escapes the allowed root") from None
    if resolved == root or resolved == keep_out:
        raise ValueError("rejected: target must be a fresh independent directory")
    resolved.mkdir()
    return resolved


def _confined_exclusive_output(directory, name):
    """Exclusively create (never truncate) one output file inside an already
    validated target directory; a plain file name only, and any existing
    file or symlink is refused."""
    if Path(name).name != name:
        raise ValueError("rejected: file name is not a plain name")
    target = directory / name
    if target.exists() or target.is_symlink():
        raise FileExistsError(target)
    return open(target, "xb")


def _copy_stream_to(source_stream, output_stream):
    """Copy one already-open readable stream into one already-open writable
    stream; every output stream in this file comes from
    _confined_exclusive_output, so no generic path-taking writer exists."""
    source_stream.seek(0)
    while True:
        chunk = source_stream.read(65536)
        if not chunk:
            break
        output_stream.write(chunk)


def _stream_fingerprint(stream):
    """(size, sha256) of one already-open stream; the caller owns the stream
    and every main-database byte in this file flows through such a stream."""
    stream.seek(0)
    digest = hashlib.sha256()
    size = 0
    while True:
        chunk = stream.read(65536)
        if not chunk:
            break
        size += len(chunk)
        digest.update(chunk)
    return size, digest.hexdigest()


def forensic_database_copy(database, destination, allowed_root, maindb_reader=None):
    """Copy a database plus every existing fixed-suffix SQLite sidecar file
    into a fresh confined target directory; only a later standard-SQLite open
    of the COPY performs native crash recovery. Complete preflight — every
    source validated, the target validated — happens before anything is
    created or written.

    Dead-writer path (maindb_reader omitted): the validated original is
    opened here directly, safe only because the caller proved the sole
    writer dead. Live-writer path (maindb_reader supplied): a quiescent
    SQLite connection may still hold the file and POSIX close() of a second
    same-inode descriptor would drop this process's advisory locks, so the
    caller-owned read-only stream provides every main-database byte; the
    helper verifies the stream's file identity against the validated source
    and never closes it. Sidecar files are distinct inodes: short-lived read
    handles, closed promptly (Windows delete sharing), always before any
    source rollback."""
    root = allowed_root.resolve(strict=True)
    main = _confined_existing_file(database, root)
    sidecars = []
    for suffix in SIDECAR_SUFFIXES:
        candidate = Path(str(database) + suffix)
        if candidate.is_symlink() or candidate.exists():
            sidecars.append(_confined_existing_file(candidate, root))
    # Complete input preflight BEFORE the target directory is created: a
    # rejected borrowed stream (wrong file identity, unreadable) must not
    # leave any directory or file behind.
    if maindb_reader is not None:
        if not maindb_reader.readable():
            raise ValueError("rejected: borrowed stream is not readable")
        borrowed = os.fstat(maindb_reader.fileno())
        actual = os.stat(main)
        if (borrowed.st_dev, borrowed.st_ino) != (actual.st_dev, actual.st_ino):
            raise ValueError("rejected: borrowed stream is not the validated source")
    target = _confined_new_directory(destination, root, main.parent)
    output = _confined_exclusive_output(target, main.name)
    try:
        if maindb_reader is None:
            with open(main, "rb") as source_stream:
                _copy_stream_to(source_stream, output)
        else:
            _copy_stream_to(maindb_reader, output)
    finally:
        output.close()
    copied = [main.name]
    for sidecar in sidecars:
        output = _confined_exclusive_output(target, sidecar.name)
        try:
            with open(sidecar, "rb") as source_stream:
                _copy_stream_to(source_stream, output)
        finally:
            output.close()
        copied.append(sidecar.name)
    return copied


def _boundary_record(connection, job_id):
    job = connection.execute(
        "SELECT project,operation,run,dto FROM jobs WHERE id=?", (job_id,)
    ).fetchone()
    assert job is not None, "boundary: job row missing"
    dto = json.loads(job["dto"])
    assert "commitProgress" in dto and "committedProgress" in dto["commitProgress"]
    # Public→internal project identity: jobs and dto carry the PUBLIC id
    # while projects/runs/results are keyed internally. The read-only
    # public_projects mapping and the job/run/project ownership chain are
    # verified, never assumed — two mismatched empty sets can never pass.
    assert job["project"] == dto["projectId"], "boundary: job project identity mismatch"
    mapping = connection.execute(
        "SELECT internal FROM public_projects WHERE public=?", (dto["projectId"],)
    ).fetchone()
    assert mapping is not None, "boundary: public project mapping missing"
    run = connection.execute("SELECT project FROM runs WHERE id=?", (job["run"],)).fetchone()
    assert run is not None, "boundary: run row missing"
    assert run[0] == mapping[0], "boundary: run project ownership mismatch"
    ledger = connection.execute(
        "SELECT number,snapshot,operation,job FROM rounds WHERE run=? ORDER BY number",
        (job["run"],),
    ).fetchall()
    snapshots = {}
    for row in ledger:
        snapshots[row["snapshot"]] = connection.execute(
            "SELECT payload FROM snapshots WHERE id=?", (row["snapshot"],)
        ).fetchone()[0]
    progress = None
    if ledger:
        progress = {
            "runId": job["run"],
            "lastCommittedRound": ledger[-1]["number"],
            "snapshotRef": ledger[-1]["snapshot"],
        }
    revision = connection.execute(
        "SELECT revision FROM projects WHERE id=?", (mapping[0],)
    ).fetchone()
    assert revision is not None, "boundary: internal project row missing"
    return {
        "state": dto["state"],
        "resultRef": dto["resultRef"],
        "runId": job["run"],
        "operation": job["operation"],
        "ledger": [(r["number"], r["snapshot"], r["operation"], r["job"]) for r in ledger],
        "snapshotPayloads": snapshots,
        "snapshotHashes": {
            identity: hashlib.sha256(payload.encode()).hexdigest()
            for identity, payload in snapshots.items()
        },
        "progress": progress,
        "dtoProgress": dto["commitProgress"]["committedProgress"],
        "revision": revision[0],
        "runs": sorted(
            row[0]
            for row in connection.execute("SELECT id FROM runs WHERE project=?", (mapping[0],))
        ),
        "results": sorted(
            row[0]
            for row in connection.execute("SELECT id FROM results WHERE project=?", (mapping[0],))
        ),
    }


def dead_boundary_oracle(copy, job_id, allowed_dir):
    """Read the death-time durable boundary from the forensic copy with plain
    SQLite (read-write open of the COPY only — native recovery happens there,
    never on the original): the complete durable evidence recovery must
    neither advance, rewind nor rewrite."""
    resolved = _confined_existing_file(copy, allowed_dir)
    connection = sqlite3.connect(str(resolved))
    try:
        connection.row_factory = sqlite3.Row
        return _boundary_record(connection, job_id)
    finally:
        connection.close()


def live_ledger_snapshot(database, job_id, allowed_root):
    """One consistent logical snapshot of the LIVE original database through
    a read-only connection in a single read transaction — never a raw copy
    while the process runs, never a read-write open, never recovery on the
    original. Same record shape as the death oracle."""
    resolved = _confined_existing_file(database, allowed_root)
    connection = sqlite3.connect(resolved.as_uri() + "?mode=ro", uri=True)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("BEGIN")
        return _boundary_record(connection, job_id)
    finally:
        connection.close()


def test_coordinator_kill_reconciles_partial_round_without_replay(prepared, tmp_path):
    database, store, projects = prepared
    request = prepare(store, projects[0], "test.rounds", {"maxRounds": 20, "workMs": 150})
    store.close()
    first = Session(database, projects)
    job = first.call("job.create", request)
    deadline = time.monotonic() + 6
    while time.monotonic() < deadline:
        value = first.job(projects[0], job["jobId"])
        if value["commitProgress"]["committedProgress"]:
            break
        time.sleep(0.02)
    else:
        raise AssertionError("no real round committed")
    first.process.kill()
    first.process.wait(timeout=5)
    first.process.stdin.close()
    first.close()
    # The last poll value is only a possibly-stale COPY: on a slow runner the
    # durable boundary may already be one round further when the kill lands.
    # After the only writer is provably dead, the confined forensic copy is
    # taken once and plain SQLite recovers and reads it. Whatever is durable
    # at death — including the job progress persisted with the last committed
    # round — is the exact boundary recovery must preserve, and the polled
    # full identity (runId/round/snapshot) must be a committed ledger prefix.
    forensic = tmp_path / "forensic-dead"
    copied = forensic_database_copy(database, forensic, tmp_path)
    assert copied[0] == "runtime.sqlite"
    oracle = dead_boundary_oracle(forensic / "runtime.sqlite", job["jobId"], forensic)
    assert oracle["state"] not in ("succeeded", "failed", "cancelled"), "job finished naturally"
    assert oracle["resultRef"] is None
    assert 1 <= len(oracle["ledger"]) < 20
    assert oracle["dtoProgress"] == oracle["progress"], "durable job progress diverged"
    poll = value["commitProgress"]["committedProgress"]
    assert (poll["runId"], poll["lastCommittedRound"], poll["snapshotRef"]) in [
        (oracle["runId"], number, snapshot)
        for number, snapshot, _operation, _job in oracle["ledger"]
    ]
    restored = Session(database, projects)
    try:
        after = restored.job(projects[0], job["jobId"])
        assert after["state"] == "failed" and after["resultRef"] is None
        assert after["error"]["code"] == "ENGINE_EXITED"
        assert after["commitProgress"]["committedProgress"] == oracle["progress"]
        # While the restored process is alive the original is never copied
        # raw: two read-only consistent snapshots — right after recovery and
        # again after the idempotent duplicate create — must each equal the
        # complete death-time evidence, except the failed terminal state.
        recovered = live_ledger_snapshot(database, job["jobId"], tmp_path)
        assert recovered["state"] == "failed" and recovered["resultRef"] is None
        assert recovered["dtoProgress"] == recovered["progress"]
        for key in BOUNDARY_KEYS:
            assert recovered[key] == oracle[key], key
        assert restored.call("job.create", request)["jobId"] == job["jobId"]
        assert restored.job(projects[0], job["jobId"])["state"] == "failed"
        repeated = live_ledger_snapshot(database, job["jobId"], tmp_path)
        assert repeated["state"] == "failed" and repeated["resultRef"] is None
        assert repeated["dtoProgress"] == repeated["progress"]
        for key in BOUNDARY_KEYS:
            assert repeated[key] == oracle[key], key
    finally:
        restored.close()


def test_synthetic_hot_journal_copy_recovery_from_a_quiescent_uncommitted_transaction(
    tmp_path,
):
    # Quiescent-uncommitted-transaction synthetic hot-journal copy recovery:
    # NO new process, command, script or forced exit. One exclusive small
    # synthetic database inside the pytest root holds an open uncommitted
    # transaction whose dirty pages have provably spilled into the main file;
    # the confined forensic helper — fed the caller-owned main-DB stream —
    # copies DB and journal to fresh independent files, and standard SQLite
    # natively recovers the copy back to the committed baseline. This covers
    # the oracle's file-recovery risk only; the resident test above owns the
    # real kill/restart acceptance.
    database = tmp_path / "synthetic.sqlite"
    marker = "UNCOMMITTED-B-MARKER-7f3ac9"
    baseline_rows = [(index, f"committed-A-row-{index:03d}") for index in range(40)]
    spill_rows = [(1000 + index, f"{marker}-{index:04d}-" + "x" * 1536) for index in range(500)]
    source = sqlite3.connect(database)
    stream = None
    try:
        assert source.execute("PRAGMA journal_mode=DELETE").fetchone()[0] == "delete"
        source.execute("PRAGMA cache_size=2")
        page_size = source.execute("PRAGMA page_size").fetchone()[0]
        assert source.execute("PRAGMA cache_size").fetchone()[0] == 2
        source.execute("CREATE TABLE t(id INTEGER PRIMARY KEY,value TEXT)")
        source.executemany("INSERT INTO t VALUES (?,?)", baseline_rows)
        source.commit()
        # Caller-owned long-held read-only stream: from here every
        # main-database byte, hash and copy in this test flows through it.
        stream = open(database, "rb")
        baseline = _stream_fingerprint(stream)
        # The quiescent uncommitted transaction: all SQL returns, then the
        # source connection stays untouched until the final rollback.
        source.execute("BEGIN IMMEDIATE")
        cursor = source.cursor()
        cursor.executemany("INSERT INTO t VALUES (?,?)", spill_rows)
        cursor.close()
        spilled = _stream_fingerprint(stream)
        stream.seek(0)
        spilled_bytes = stream.read()
        assert spilled != baseline, "fixture: uncommitted writes never reached the main file"
        assert marker.encode("ascii") in spilled_bytes, "fixture: no spilled unique marker"
        journal = _confined_existing_file(Path(str(database) + "-journal"), tmp_path)
        with open(journal, "rb") as handle:
            journal_bytes = handle.read()
        assert len(journal_bytes) > 512, "fixture: journal too small to be hot"
        assert journal_bytes[:8] == b"\xd9\xd5\x05\xf9\x20\xa1\x63\xd7", "journal magic"
        # Copy through the real confined helper with the borrowed stream;
        # afterwards the source set must be byte-for-byte unchanged.
        forensic = tmp_path / "forensic"
        assert forensic_database_copy(database, forensic, tmp_path, maindb_reader=stream) == [
            "synthetic.sqlite",
            "synthetic.sqlite-journal",
        ]
        assert _stream_fingerprint(stream) == spilled
        with open(journal, "rb") as handle:
            journal_digest = hashlib.sha256(handle.read()).hexdigest()
        assert journal_digest == hashlib.sha256(journal_bytes).hexdigest()
        assert (forensic / "synthetic.sqlite").read_bytes() == spilled_bytes
        assert (forensic / "synthetic.sqlite-journal").read_bytes() == journal_bytes
        # Standard SQLite natively recovers the independent copy: the exact
        # committed baseline returns, every uncommitted row is gone, and the
        # copied journal is consumed (DELETE mode removes it).
        recovered = sqlite3.connect(forensic / "synthetic.sqlite")
        try:
            rows = recovered.execute("SELECT id,value FROM t ORDER BY id").fetchall()
            assert rows == baseline_rows
            assert recovered.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        finally:
            recovered.close()
        assert not (forensic / "synthetic.sqlite-journal").exists(), "journal not consumed"
        record = {"sqlite": sqlite3.sqlite_version, "page_size": page_size}
        assert record["sqlite"] and record["page_size"] > 0
        # Second immutability check AFTER the copy's native recovery and
        # BEFORE the source rollback: the full source set, sizes and hashes
        # are unchanged; the main-DB hash still flows through the borrowed
        # stream.
        assert _stream_fingerprint(stream) == spilled
        with open(journal, "rb") as handle:
            reread = handle.read()
        assert len(reread) == len(journal_bytes)
        assert hashlib.sha256(reread).hexdigest() == hashlib.sha256(journal_bytes).hexdigest()
        assert {suffix: Path(str(database) + suffix).exists() for suffix in SIDECAR_SUFFIXES} == {
            "-journal": True,
            "-wal": False,
            "-shm": False,
        }
    finally:
        # Ordered cleanup with nested finally blocks: the source rollback is
        # attempted first, but a failing rollback still reaches the SQLite
        # close, and the caller-owned main-DB stream closes only after the
        # SQLite connection. Cleanup failures propagate, never masked.
        try:
            source.rollback()
        finally:
            try:
                source.close()
            finally:
                if stream is not None:
                    stream.close()
    assert not Path(str(database) + "-journal").exists(), "source journal not cleaned"
    verification = sqlite3.connect(database)
    try:
        assert verification.execute("SELECT id,value FROM t ORDER BY id").fetchall() == (
            baseline_rows
        )
    finally:
        verification.close()


def test_confined_copy_rejects_escape_and_existing_targets(tmp_path):
    # Deterministic refusals: a '..' component, an absolute path outside the
    # allowed root, a pre-existing target directory, and a pre-existing
    # target file are each rejected before anything uninvolved changes.
    sample = tmp_path / "sample.bin"
    sample.write_bytes(b"source-main-bytes")
    sidecar = tmp_path / "sample.bin-journal"
    sidecar.write_bytes(b"source-journal-bytes")

    escaping = tmp_path / "sub" / ".." / "sample.bin"
    with pytest.raises(ValueError, match="path component"):
        forensic_database_copy(escaping, tmp_path / "forensic-escape", tmp_path)
    assert not (tmp_path / "forensic-escape").exists()

    outside = Path(__file__)
    outside_digest = hashlib.sha256(outside.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="allowed root"):
        forensic_database_copy(outside, tmp_path / "forensic-outside", tmp_path)
    assert not (tmp_path / "forensic-outside").exists()
    assert hashlib.sha256(outside.read_bytes()).hexdigest() == outside_digest

    existing = tmp_path / "forensic-existing"
    existing.mkdir()
    (existing / "keep.txt").write_bytes(b"keep-existing-bytes")
    with pytest.raises(FileExistsError):
        forensic_database_copy(sample, existing, tmp_path)
    assert (existing / "keep.txt").read_bytes() == b"keep-existing-bytes"
    assert sorted(path.name for path in existing.iterdir()) == ["keep.txt"]

    occupied = tmp_path / "forensic-occupied"
    occupied.mkdir()
    (occupied / "sample.bin").write_bytes(b"occupied-target-bytes")
    with pytest.raises(FileExistsError):
        forensic_database_copy(sample, occupied, tmp_path)
    assert (occupied / "sample.bin").read_bytes() == b"occupied-target-bytes"
    assert sorted(path.name for path in occupied.iterdir()) == ["sample.bin"]
    assert sample.read_bytes() == b"source-main-bytes"
    assert sidecar.read_bytes() == b"source-journal-bytes"


def test_confined_copy_rejects_symlinked_source(tmp_path):
    # The symlink rejection branch, exercised only where the platform lets
    # the test create a symlink at all (the main acceptance never skips).
    real = tmp_path / "real.sqlite"
    real.write_bytes(b"real-bytes")
    linked = tmp_path / "linked.sqlite"
    try:
        linked.symlink_to(real)
    except (NotImplementedError, PermissionError) as error:
        # Only the explicit platform-unsupported / no-privilege conditions
        # skip THIS negative case; other OSErrors (ENOSPC, EIO, ...) fail.
        pytest.skip(f"symlink creation unsupported on this platform: {error!r}")
    with pytest.raises(ValueError, match="symbolic link"):
        forensic_database_copy(linked, tmp_path / "forensic-link", tmp_path)
    assert not (tmp_path / "forensic-link").exists()
    assert real.read_bytes() == b"real-bytes"


def test_boundary_oracle_detects_added_rounds_and_rewritten_snapshots(tmp_path):
    # Minimal independent sample with the real table shapes the oracle reads;
    # proves an inserted round or a rewritten snapshot payload can never
    # falsely pass the equality assertions of the kill/restart test.
    database = tmp_path / "oracle.sqlite"
    connection = sqlite3.connect(database)
    connection.execute("CREATE TABLE projects(id TEXT PRIMARY KEY,revision INTEGER NOT NULL)")
    connection.execute(
        "CREATE TABLE public_projects(public TEXT PRIMARY KEY,internal TEXT UNIQUE NOT NULL)"
    )
    connection.execute("CREATE TABLE snapshots(id TEXT PRIMARY KEY,payload TEXT NOT NULL)")
    connection.execute("CREATE TABLE runs(id TEXT PRIMARY KEY,project TEXT)")
    connection.execute(
        "CREATE TABLE rounds(run TEXT,number INTEGER,snapshot TEXT,operation TEXT,job TEXT)"
    )
    connection.execute(
        "CREATE TABLE jobs(id TEXT PRIMARY KEY,project TEXT,operation TEXT,dto TEXT,run TEXT)"
    )
    connection.execute("CREATE TABLE results(id TEXT PRIMARY KEY,project TEXT)")
    # The public id deliberately differs from the internal id: the oracle
    # must prove the real public→internal mapping, not reuse one value.
    connection.execute("INSERT INTO projects VALUES (?,?)", ("internal-one", 0))
    connection.execute("INSERT INTO public_projects VALUES (?,?)", ("public-1", "internal-one"))
    connection.execute("INSERT INTO snapshots VALUES (?,?)", ("s1", "payload-one"))
    connection.execute("INSERT INTO runs VALUES (?,?)", ("r1", "internal-one"))
    connection.execute("INSERT INTO rounds VALUES (?,?,?,?,?)", ("r1", 1, "s1", "op1", "j1"))
    dto = json.dumps(
        {
            "projectId": "public-1",
            "state": "running",
            "resultRef": None,
            "commitProgress": {
                "committedProgress": {
                    "runId": "r1",
                    "lastCommittedRound": 1,
                    "snapshotRef": "s1",
                }
            },
        }
    )
    connection.execute("INSERT INTO jobs VALUES (?,?,?,?,?)", ("j1", "public-1", "op-x", dto, "r1"))
    connection.commit()
    connection.close()
    baseline = dead_boundary_oracle(database, "j1", tmp_path)
    assert baseline["ledger"] == [(1, "s1", "op1", "j1")]
    assert baseline["progress"] == {"runId": "r1", "lastCommittedRound": 1, "snapshotRef": "s1"}
    assert baseline["dtoProgress"] == baseline["progress"]
    assert baseline["runs"] == ["r1"] and baseline["results"] == []
    connection = sqlite3.connect(database)
    connection.execute("INSERT INTO rounds VALUES (?,?,?,?,?)", ("r1", 2, "s1", "op2", "j1"))
    connection.execute("UPDATE snapshots SET payload=? WHERE id=?", ("payload-two", "s1"))
    connection.commit()
    connection.close()
    tampered = dead_boundary_oracle(database, "j1", tmp_path)
    assert tampered["ledger"] != baseline["ledger"]
    assert tampered["snapshotPayloads"] != baseline["snapshotPayloads"]
    assert tampered["snapshotHashes"] != baseline["snapshotHashes"]
    assert tampered["progress"] != baseline["progress"]


@pytest.mark.parametrize("wait_for_round", [False, True])
def test_real_round_cancel_preserves_exact_last_committed_boundary(prepared, wait_for_round):
    database, store, projects = prepared
    request = prepare(store, projects[0], "test.rounds", {"maxRounds": 20, "workMs": 500})
    store.close()
    session = Session(database, projects)
    try:
        job = session.call("job.create", request)
        if wait_for_round:
            deadline = time.monotonic() + 6
            while time.monotonic() < deadline:
                previous = session.job(projects[0], job["jobId"])
                if previous["commitProgress"]["committedProgress"]:
                    break
                time.sleep(0.02)
            else:
                raise AssertionError("no actual committed round before cancellation")
        decision = session.call("job.cancel", {"projectId": projects[0], "jobId": job["jobId"]})
        assert decision["disposition"] == "accepted"
        assert decision["state"] in {"queued", "cancelling"}
        final = session.terminal(projects[0], job["jobId"])
        assert final["state"] == "cancelled" and final["resultRef"] is None
        progress = final["commitProgress"]["committedProgress"]
        if wait_for_round:
            assert progress is not None
            assert (
                progress["lastCommittedRound"]
                >= previous["commitProgress"]["committedProgress"]["lastCommittedRound"]
            )
            assert progress["lastCommittedRound"] < 20
        else:
            assert progress is None
        assert session.call("project.get", {"projectId": projects[0]})["projectRevision"] == 0
        assert decision["state"] in {"queued", "cancelling"}  # Original response remains immutable.
    finally:
        session.close()
