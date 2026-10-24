"""Absolute handshake deadline at a deterministic, continuously nonempty inbox.

The production serve loop, JSONL reader, contract and SQLite are real. Only its
local clock and stdin bytes are controlled; no resource limit is reduced. The
separate default-duration stdio probe records the actual wall-clock regression.
"""

import asyncio
import json
import sys
import time
from types import SimpleNamespace
from uuid import uuid4

import pytest
from ontolearn_engine import coordinator as runtime
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT, LIMITS


def frame(method):
    return {
        "kind": "request",
        "id": str(uuid4()),
        "protocolVersion": 2,
        "engineSessionId": None,
        "method": method,
        "params": {"supportedVersions": [2], "clientId": str(uuid4())} if method == "hello" else {},
    }


def serve_frames(tmp_path, monkeypatch, requests, advance_after_first_reply):
    database = tmp_path / "deadline.sqlite"
    chunks = iter([b"".join(json.dumps(value).encode() + b"\n" for value in requests), b""])
    clock = [0.0]
    emitted = []

    def capture(value):
        assert CONTRACT.validate("response", value)
        emitted.append(value)
        if len(emitted) == 1:
            clock[0] = advance_after_first_reply

    # Replace module references only: asyncio's real scheduling clock, process
    # stdin and the global os/time/sys modules remain untouched.
    monkeypatch.setattr(
        runtime, "time", SimpleNamespace(monotonic=lambda: clock[0], time=time.time)
    )
    monkeypatch.setattr(
        runtime,
        "os",
        SimpleNamespace(
            read=lambda _fd, _size: next(chunks, b""),
            environ={"ONTOLEARN_DB_PATH": str(database), "ONTOLEARN_ALLOWED_PROJECTS": "[]"},
        ),
    )
    monkeypatch.setattr(
        runtime,
        "sys",
        SimpleNamespace(stdin=SimpleNamespace(fileno=lambda: 123), platform=sys.platform),
    )
    monkeypatch.setattr(runtime.Coordinator, "_emit", staticmethod(capture))
    asyncio.run(runtime.serve())
    # Normal finalization must release the actual SQLite writer lease.
    reopened = JobStore(database, contract=CONTRACT)
    try:
        assert reopened._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0
    finally:
        reopened.close()
    return emitted


@pytest.mark.parametrize("extra_seconds", [0.0, 1.0])
def test_busy_inbox_cannot_accept_hello_at_or_after_absolute_deadline(
    tmp_path, monkeypatch, extra_seconds
):
    early, late = frame("health"), frame("hello")
    emitted = serve_frames(
        tmp_path, monkeypatch, [early, late], LIMITS["handshakeMs"] / 1000 + extra_seconds
    )
    assert len(emitted) == 1
    assert emitted[0]["id"] == early["id"]
    assert emitted[0]["engineSessionId"] is None
    assert emitted[0]["error"] == runtime.safe_error("HANDSHAKE_REQUIRED")


def test_timely_hello_disables_only_the_prehandshake_deadline(tmp_path, monkeypatch):
    first, repeated = frame("hello"), frame("hello")
    emitted = serve_frames(
        tmp_path, monkeypatch, [first, repeated], LIMITS["handshakeMs"] / 1000 + 1
    )
    assert len(emitted) == 2
    assert emitted[0]["id"] == first["id"] and emitted[0]["ok"]
    assert emitted[1]["id"] == repeated["id"] and not emitted[1]["ok"]
    assert emitted[1]["engineSessionId"] == emitted[0]["engineSessionId"]
    assert emitted[1]["error"] == runtime.safe_error("INVALID_STATE")
