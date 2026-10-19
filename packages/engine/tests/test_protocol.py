import json
import subprocess
import sys

import pytest
from ontolearn_engine.protocol import MAX_REQUEST_BYTES, handle_request


def request(**changes):
    return json.dumps({"id": "test", "method": "health", "protocolVersion": 1} | changes).encode()


def test_health_reports_only_implemented_capability():
    result = handle_request(request())
    assert result == {
        "id": "test",
        "ok": True,
        "result": {
            "protocolVersion": 1,
            "engineVersion": "0.1.0",
            "status": "ok",
            "capabilities": ["health"],
        },
    }


@pytest.mark.parametrize(
    "raw,code",
    [
        (b"{", "INVALID_JSON"),
        (b"[]", "INVALID_REQUEST"),
        (b"\xff", "INVALID_JSON"),
        (request(id=123), "INVALID_ID"),
        (request(method="query"), "METHOD_NOT_ALLOWED"),
        (request(protocolVersion=2), "UNSUPPORTED_PROTOCOL"),
        (request(protocolVersion=True), "UNSUPPORTED_PROTOCOL"),
        (request(secret="never-echo-this"), "INVALID_REQUEST"),
        (b"x" * (MAX_REQUEST_BYTES + 1), "REQUEST_TOO_LARGE"),
    ],
)
def test_invalid_requests_are_rejected_without_echo(raw, code):
    result = handle_request(raw)
    assert result["ok"] is False
    assert result["error"] == {"code": code}
    assert "never-echo-this" not in json.dumps(result)


def test_stdio_entrypoint_works_without_network_or_model():
    completed = subprocess.run(
        [sys.executable, "-I", "-m", "ontolearn_engine"],
        input=request() + b"\n",
        capture_output=True,
        timeout=5,
        check=True,
    )
    assert completed.stderr == b""
    assert json.loads(completed.stdout)["result"]["status"] == "ok"
