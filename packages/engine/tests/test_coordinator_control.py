"""Protocol control paths do not open projects or run workloads."""

import sqlite3
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import Coordinator, classify
from ontolearn_engine.protocol import ProtocolFault
from ontolearn_engine.resources import CONTRACT, REGISTRY_HASH


def request(method, params=None, session=None, **changes):
    return {
        "kind": "request",
        "id": str(uuid4()),
        "protocolVersion": 2,
        "engineSessionId": session,
        "method": method,
        "params": params or {},
    } | changes


def hello(c):
    return c.request(request("hello", {"supportedVersions": [2], "clientId": str(uuid4())}))


def test_handshake_health_reuse_and_exact_registry_hash():
    c = Coordinator(None)
    assert c.request(request("health"))["error"]["code"] == "HANDSHAKE_REQUIRED"
    answer = hello(c)
    assert answer["ok"] and answer["result"]["registryHash"] == REGISTRY_HASH
    assert all(not s.startswith("test.") for s in answer["result"]["capabilities"])
    session = c.session
    for _ in range(10):
        assert c.request(request("health", session=session))["result"]["status"] == "ok"
    assert c.session == session
    assert hello(c)["error"]["code"] == "INVALID_STATE"
    assert c.request(request("health", session=str(uuid4())))["error"]["code"] == "SESSION_MISMATCH"


def test_no_version_intersection_and_no_implicit_v1_fallback():
    c = Coordinator(None)
    for value in ([1], [3]):
        result = c.request(request("hello", {"supportedVersions": value, "clientId": str(uuid4())}))
        assert result["error"]["code"] == "VERSION_INCOMPATIBLE"
        assert c.session is None
    with pytest.raises(ProtocolFault):
        c.request({"id": "health", "method": "health", "protocolVersion": 1})


def test_fatal_unknown_method_duplicate_id_and_bad_envelope():
    c = Coordinator(None)
    hello(c)
    q = request("health", session=c.session)
    assert c.request(q)["ok"]
    with pytest.raises(ProtocolFault):
        c.request(q)
    with pytest.raises(ProtocolFault):
        c.request(request("run arbitrary text", session=c.session))
    with pytest.raises(ProtocolFault):
        c.request(request("health", session=c.session, path="private"))


def test_permissions_do_not_follow_renderer_supplied_project_uuid():
    c = Coordinator(None)
    hello(c)
    error = c.request(request("project.get", {"projectId": str(uuid4())}, c.session))["error"]
    assert error["code"] == "PERMISSION_DENIED"
    assert CONTRACT.validate("error", error)


@pytest.mark.parametrize(
    "code,expected",
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
def test_sqlite_real_errorcode_classification_not_exception_text(code, expected):
    error = sqlite3.OperationalError("secret /path user cell value credential")
    error.sqlite_errorcode = code
    result = classify(error)
    assert result["code"] == expected
    assert CONTRACT.validate("error", result)
    assert "secret" not in str(result)
    assert classify(sqlite3.OperationalError("database is locked"))["code"] == "INTERNAL_ERROR"


@pytest.mark.parametrize("method,params", [("health", {"unexpected": True}), ("project.get", {})])
def test_prehandshake_gate_precedes_method_params(method, params):
    coordinator = Coordinator(None)
    answer = coordinator.request(request(method, params))
    assert answer["error"]["code"] == "HANDSHAKE_REQUIRED"
    assert answer["engineSessionId"] is None
    assert CONTRACT.validate("response", answer)


def test_unknown_producer_cannot_self_assign_public_error_or_retry_permission():
    class ForeignError(ValueError):
        code = "STORAGE_BUSY"
        params = {"retryAfterMs": 250}

    assert classify(ForeignError("private underlying message"))["code"] == "INTERNAL_ERROR"
    assert classify(ValueError("bad user value"))["code"] == "INTERNAL_ERROR"


@pytest.mark.parametrize("method", [None, {}, [], 42])
def test_malformed_method_is_safe_session_failure(method):
    with pytest.raises(ProtocolFault):
        Coordinator(None).request(request(method))


def test_initialization_import_failure_has_only_fixed_bounded_stderr():
    import subprocess
    import sys

    code = """
import importlib.abc,sys
class Block(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname=='ontolearn_engine.resources':
   raise ValueError('/private/path credential cell-value must not escape')
sys.meta_path.insert(0,Block())
from ontolearn_engine.__main__ import main
main()
"""
    result = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, timeout=5)
    assert result.returncode == 1
    assert result.stdout == b""
    assert result.stderr == b"ENGINE_SESSION_FAILED\n"
