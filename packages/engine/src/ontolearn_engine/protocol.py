"""Versioned JSON-lines transport; no sockets, filesystem or model access."""

import json

from ontolearn_engine import __version__

PROTOCOL_VERSION = 1
MAX_REQUEST_BYTES = 16384


def handle_request(raw: bytes) -> dict:
    request_id = None
    try:
        if len(raw) > MAX_REQUEST_BYTES:
            raise ValueError("REQUEST_TOO_LARGE")
        request = json.loads(raw)
        if not isinstance(request, dict):
            raise ValueError("INVALID_REQUEST")
        request_id = request.get("id")
        if not isinstance(request_id, str) or not 1 <= len(request_id) <= 128:
            request_id = None
            raise ValueError("INVALID_ID")
        if set(request) != {"id", "method", "protocolVersion"}:
            raise ValueError("INVALID_REQUEST")
        if type(request["protocolVersion"]) is not int or request["protocolVersion"] != 1:
            raise ValueError("UNSUPPORTED_PROTOCOL")
        if request["method"] != "health":
            raise ValueError("METHOD_NOT_ALLOWED")
    except (ValueError, UnicodeError) as error:
        # 错误只返回固定代码，禁止回显导入内容或异常原文。
        allowed = {
            "REQUEST_TOO_LARGE",
            "INVALID_REQUEST",
            "INVALID_ID",
            "UNSUPPORTED_PROTOCOL",
            "METHOD_NOT_ALLOWED",
        }
        code = str(error) if str(error) in allowed else "INVALID_JSON"
        return {"id": request_id, "ok": False, "error": {"code": code}}
    return {
        "id": request_id,
        "ok": True,
        "result": {
            "protocolVersion": PROTOCOL_VERSION,
            "engineVersion": __version__,
            "status": "ok",
            "capabilities": ["health"],
        },
    }
