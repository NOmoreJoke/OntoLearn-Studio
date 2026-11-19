"""Shared v2 contract checker; resources are shipped byte-for-byte with the engine.

Same deliberately small JSON Schema vocabulary as the TS/zod adapter.
"""

import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "v2"
DOCUMENT = json.loads((ROOT / "schema.json").read_text(encoding="utf-8"))
DEFINITIONS = DOCUMENT["$defs"]
REGISTRY = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
ERROR_CATALOG = json.loads((ROOT / "errors.json").read_text(encoding="utf-8"))
KEYWORDS = {
    "$ref",
    "const",
    "enum",
    "oneOf",
    "type",
    "properties",
    "required",
    "additionalProperties",
    "propertyNames",
    "minProperties",
    "maxProperties",
    "items",
    "minItems",
    "maxItems",
    "minLength",
    "maxLength",
    "pattern",
    "minimum",
    "maximum",
}


def encoded_size(value):
    # Numeric tokens conservatively cost 32 bytes, shared with the TS adapter.
    if type(value) in {int, float}:
        return 32
    if isinstance(value, list):
        return 2 + max(0, len(value) - 1) + sum(encoded_size(v) for v in value)
    if isinstance(value, dict):
        return (
            2
            + max(0, len(value) - 1)
            + sum(encoded_size(k) + 1 + encoded_size(v) for k, v in value.items())
        )
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode())


def equal(a, b):
    if type(a) in {int, float} and type(b) in {int, float}:
        return math.isfinite(a) and math.isfinite(b) and a == b
    return type(a) is type(b) and a == b


def check(s, value):
    if set(s) - KEYWORDS:
        return False
    if "$ref" in s:
        target = s["$ref"]
        return target.startswith("#/$defs/") and check(DEFINITIONS[target[8:]], value)
    if "const" in s:
        return equal(s["const"], value)
    if "enum" in s:
        return any(equal(v, value) for v in s["enum"])
    if "oneOf" in s:
        return sum(check(v, value) for v in s["oneOf"]) == 1
    kind = s.get("type")
    if kind == "object":
        if not isinstance(value, dict) or not set(s.get("required", [])) <= set(value):
            return False
        if not s.get("minProperties", 0) <= len(value) <= s.get("maxProperties", math.inf):
            return False
        properties = s.get("properties", {})
        for key, v in value.items():
            if not isinstance(key, str):
                return False
            if "propertyNames" in s and not check(s["propertyNames"], key):
                return False
            if key in properties:
                if not check(properties[key], v):
                    return False
            elif s.get("additionalProperties") is False:
                return False
            elif isinstance(s.get("additionalProperties"), dict):
                if not check(s["additionalProperties"], v):
                    return False
        return True
    if kind == "array":
        return (
            isinstance(value, list)
            and s.get("minItems", 0) <= len(value) <= s.get("maxItems", math.inf)
            and all(check(s["items"], v) for v in value)
        )
    if kind == "string":
        return (
            isinstance(value, str)
            and s.get("minLength", 0) <= len(value) <= s.get("maxLength", math.inf)
            and all(not 0xD800 <= ord(c) <= 0xDFFF for c in value)
            and ("pattern" not in s or re.fullmatch(s["pattern"], value) is not None)
        )
    if kind == "boolean":
        return type(value) is bool
    if kind in {"number", "integer"}:
        return (
            type(value) in {int, float}
            and math.isfinite(value)
            and (kind != "integer" or value == int(value))
            and s.get("minimum", -math.inf) <= value <= s.get("maximum", math.inf)
        )
    return False


def semantic(v):
    if isinstance(v, list):
        return all(semantic(x) for x in v)
    if not isinstance(v, dict):
        return True
    if v.get("projectionVersion") == 1 and v.get("projectionPolicy") == "selected-facts-v1":
        derived = v["derived"]
        if derived and (
            derived["projectId"] != v["projectId"]
            or derived["inputSnapshotId"] != v["inputSnapshotId"]
            or derived["implementation"] != v["implementation"]
        ):
            return False
    if "code" in v and "messageKey" in v and encoded_size(v) > ERROR_CATALOG["maxEncodedBytes"]:
        return False
    if isinstance(v.get("completed"), (int, float)) and isinstance(v.get("total"), (int, float)):
        if v["completed"] > v["total"]:
            return False
    if "staleReason" in v:
        reasons = v["staleReason"]
        vector, sets = v["dependencyVector"], v["definitionSetDigests"]
        if "facts:asserted" not in vector or len({r["dependency"] for r in reasons}) != len(
            reasons
        ):
            return False
        for r in reasons:
            if r["dependency"] in vector:
                if vector[r["dependency"]] != r["before"]:
                    return False
            elif r["before"] != 0 or r["after"] < 1 or r["dependency"].split(":")[0] not in sets:
                return False
        if (v["state"] == "stale") != bool(reasons):
            return False
        if any(r["before"] == r["after"] for r in reasons):
            return False
        if v["state"] == "current" and (
            v["payloadStatus"] != "available" or v["historicalSelectionRequired"] is not False
        ):
            return False
        if v["state"] == "historical" and v["historicalSelectionRequired"] is not True:
            return False
        if v["kind"] == "receipt" and v["state"] != "historical":
            return False
    if "createdAtMs" in v and "updatedAtMs" in v and v["updatedAtMs"] < v["createdAtMs"]:
        return False
    if type(v.get("finishedAtMs")) in {int, float}:
        if v["finishedAtMs"] < v["createdAtMs"] or v["finishedAtMs"] != v["updatedAtMs"]:
            return False
    for key in ("supportedVersions", "capabilities"):
        if key in v and len(set(v[key])) != len(v[key]):
            return False
    if "disposition" in v:
        terminal = v["state"] in {"succeeded", "failed", "cancelled"}
        if (v["disposition"] == "alreadyTerminal") != terminal:
            return False
        if v["disposition"] == "alreadyRequested" and v["state"] != "cancelling":
            return False
    if v.get("event") == "job.state":
        if any(v["data"][key] != v[key] for key in ("projectId", "jobId")):
            return False
    if v.get("kind") == "response" and v["method"] == "hello" and v["ok"]:
        if v["engineSessionId"] != v["result"]["engineSessionId"]:
            return False
    if v.get("kind") == "request" and v["method"] == "job.list":
        p = v["params"]
        if (p["cursor"] is None) != (p["listSnapshotId"] is None):
            return False
    if v.get("kind") == "request" and v["method"] == "job.create":
        p = v["params"]
        c = REGISTRY["capabilities"][p["capability"]]
        if p["input"]["scope"] not in c["dataScopes"]:
            return False
        if c["requiresConfirmation"]:
            if p["confirmationRef"] is None or p["input"]["preparedPlanRef"] is None:
                return False
        elif p["confirmationRef"] is not None or p["input"]["preparedPlanRef"] is not None:
            return False
    if "capability" in v and "commitProgress" in v:
        capability = REGISTRY["capabilities"][v["capability"]]
        if v["scope"] not in capability["dataScopes"]:
            return False
        if "facts:asserted" not in v["dependencyVector"]:
            return False
        if any(v[k] != v["input"][k] for k in ("inputSnapshotId", "scope", "parametersHash")):
            return False
        if capability["requiresConfirmation"]:
            if v["confirmationRef"] is None or v["input"]["preparedPlanRef"] is None:
                return False
        elif v["confirmationRef"] is not None or v["input"]["preparedPlanRef"] is not None:
            return False
        boundary = capability["cancelBoundary"]
        mode = {"whole-transaction": "atomic", "uncommitted-round": "rounds"}.get(boundary, "none")
        if v["commitProgress"]["mode"] != mode:
            return False
        commit = v["commitProgress"]
        if mode == "atomic" and commit["operationId"] != v["operationId"]:
            return False
        point = commit.get("marker") if mode == "atomic" else commit.get("committedProgress")
        if v["state"] == "queued" and point is not None:
            return False
        if v["state"] == "succeeded" and mode != "none" and point is None:
            return False
        if v["resultRef"] and v["resultRef"]["inputSnapshotId"] != v["inputSnapshotId"]:
            return False
    if "rows" in v and "binding" in v:
        if encoded_size(v) > 131072:
            return False
        keys = [(r["ordinal"], r["rowId"]) for r in v["rows"]]
        if len({r["rowId"] for r in v["rows"]}) != len(v["rows"]):
            return False
        if any(a >= b for a, b in zip(keys, keys[1:], strict=False)):
            return False
    if "jobs" in v and "binding" in v:
        jobs, binding = v["jobs"], v["binding"]
        if len({j["jobId"] for j in jobs}) != len(jobs):
            return False
        for j in jobs:
            terminal = j["state"] in {"succeeded", "failed", "cancelled"}
            if j["projectId"] != binding["projectId"]:
                return False
            if binding["filter"] == "active" and terminal:
                return False
            if binding["filter"] == "terminal" and not terminal:
                return False
        keys = [(j["createdAtMs"], j["jobId"]) for j in jobs]
        if any(a >= b for a, b in zip(keys, keys[1:], strict=False)):
            return False
    return all(semantic(x) for x in v.values())


def validate(name, value):
    try:
        valid = (
            name in DEFINITIONS
            and check(DEFINITIONS[name], value)
            and semantic(value)
            and encoded_size(value) <= 262144
        )
        if valid and (
            not _changeset_semantics(name, value)
            or not _query_consumer_semantics(name, value)
            or not _checkpoint_semantics(name, value)
        ):
            return False
        if valid and name in {"params_job.create", "params_job.list"}:
            return semantic({"kind": "request", "method": name[7:], "params": value})
        return valid
    except (KeyError, TypeError, ValueError, OverflowError, RecursionError):
        return False


_QUERY_EDGE_SPACE = (
    "\t\n\x0b\x0c\r\x1c\x1d\x1e\x1f \x85\xa0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006"
    "\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff"
)


def _query_consumer_semantics(name, value):
    if name in {"request", "response", "envelope", "request3", "response3", "envelope3"}:
        if value["kind"] == "request" and value["method"].startswith("query."):
            return _query_consumer_semantics("params_" + value["method"], value["params"])
        if value["kind"] == "response" and value["ok"] and value["method"].startswith("query."):
            return _query_consumer_semantics("result_" + value["method"], value["result"])
        return True
    if name == "params_query.execution.prepare":
        return _query_consumer_semantics("query.consumer.draft", value["visibleDraft"])
    if name in {"result_query.definition.load", "query.consumer.definitionLoad"}:
        return value["kind"] != "managed" or _query_consumer_semantics(
            "query.consumer.draft", value["draft"]
        )
    if name == "query.consumer.descriptor":
        for key, maximum in {"name": 128, "description": 4096, "capabilityQuestion": 4096}.items():
            text = value[key]
            if (
                type(text) is not str
                or any(0xD800 <= ord(c) <= 0xDFFF for c in text)
                or sum(2 if ord(c) > 0xFFFF else 1 for c in text) > maximum
            ):
                return False
        return bool(value["name"]) and value["name"] == value["name"].strip(_QUERY_EDGE_SPACE)
    if name != "query.consumer.draft":
        return True
    for key, maximum in {
        "name": 128,
        "description": 4096,
        "sparql": 65536,
        "capabilityQuestion": 4096,
    }.items():
        text = value[key]
        if type(text) is not str or any(0xD800 <= ord(c) <= 0xDFFF for c in text):
            return False
        if sum(2 if ord(c) > 0xFFFF else 1 for c in text) > maximum:
            return False
    return all(value[key].strip(_QUERY_EDGE_SPACE) for key in ("name", "sparql"))


def _changeset_semantics(name, value):
    if name in {"request3", "response3", "envelope3"}:
        if value["kind"] == "request" and value["method"] == "changeset.preview":
            return _changeset_semantics("params_changeset.preview", value["params"])
        if value["kind"] == "response" and value["ok"] and value["method"].startswith("changeset."):
            return _changeset_semantics("result_" + value["method"], value["result"])
        return True
    if name == "params_changeset.preview":
        return value["intent"] != "change" or _changeset_semantics("changeSetPlan", value["plan"])
    if name == "changeSetPlan":
        return all(
            _changeset_semantics("changeSetDefinition", item)
            for item in value.get("definitions", [])
        )
    if name in {"changeSetDefinition", "changeSetOntologyDefinition"}:
        return value["layer"] != "ontology" or _changeset_semantics(
            "changeSetOntologyValue", value["value"]
        )
    if name == "changeSetOntologyValue":
        return "entityMetadata" not in value or _entity_metadata_semantics(value["entityMetadata"])
    if name == "changeSetEntityMetadata":
        return _entity_metadata_semantics(value)
    if name == "changeSetManifest":
        parts = value["segments"]
        if len(parts) != value["segmentCount"]:
            return False
        offset = 0
        for ordinal, part in enumerate(parts):
            if part["ordinal"] != ordinal or part["byteOffset"] != offset:
                return False
            offset += part["rawByteLength"]
        return offset == value["totalBytes"]
    if name == "result_changeset.preview":
        manifest = value["manifest"]
        return _changeset_semantics("changeSetManifest", manifest) and (
            manifest["documentKind"] == "undo-impact"
            if value["status"] == "conflict"
            else manifest["documentKind"] == "diff"
            and (
                value["targetOperationId"] is None
                if value["intent"] == "change"
                else value["targetOperationId"] is not None
            )
        )
    if name == "changeSetSegment":
        encoded = value["dataBase64"]
        padding = 2 if encoded.endswith("==") else 1 if encoded.endswith("=") else 0
        return len(encoded) // 4 * 3 - padding == value["rawByteLength"]
    if name in {"changeSetPage", "result_changeset.diff.page"}:
        parts = value["segments"]
        return all(
            _changeset_semantics("changeSetSegment", part)
            and (
                index == 0
                or part["ordinal"] == parts[index - 1]["ordinal"] + 1
                and part["byteOffset"]
                == parts[index - 1]["byteOffset"] + parts[index - 1]["rawByteLength"]
            )
            for index, part in enumerate(parts)
        )
    return True


def _checkpoint_semantics(name, value):
    if name in {"request3", "response3", "envelope3"}:
        if value["kind"] == "request" and value["method"].startswith(
            ("project.checkpoint.", "project.restore.")
        ):
            return _checkpoint_semantics("params_" + value["method"], value["params"])
        if (
            value["kind"] == "response"
            and value["ok"]
            and value["method"].startswith(("project.checkpoint.", "project.restore."))
        ):
            return _checkpoint_semantics("result_" + value["method"], value["result"])
        return True
    if name in {"restore.manifest", "checkpoint.coverage", "checkpoint.preserved"}:
        parts = value["segments"] if name == "restore.manifest" else value
        offset = 0
        for ordinal, part in enumerate(parts):
            if part["ordinal"] != ordinal or part["byteOffset"] != offset:
                return False
            offset += part["rawByteLength"]
        return offset == value["totalBytes"] if name == "restore.manifest" else True
    if name == "restore.segment":
        encoded = value["dataBase64"]
        padding = 2 if encoded.endswith("==") else 1 if encoded.endswith("=") else 0
        return len(encoded) // 4 * 3 - padding == value["rawByteLength"]
    if name in {"result_project.restore.page", "params_project.restore.page"}:
        if name.startswith("params_"):
            return True
        parts = value["segments"]
        return all(
            _checkpoint_semantics("restore.segment", part)
            and (
                index == 0
                or part["ordinal"] == parts[index - 1]["ordinal"] + 1
                and part["byteOffset"]
                == parts[index - 1]["byteOffset"] + parts[index - 1]["rawByteLength"]
            )
            for index, part in enumerate(parts)
        )
    if name == "params_project.restore.confirm":
        return len(value["readSegmentHashes"]) == len(set(value["readSegmentHashes"]))
    return True


def _entity_metadata_semantics(metadata):
    for iri, entity in metadata["entities"].items():
        if not re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", iri) or any(
            c.isspace() or c in '<>"{}|^`\\' for c in iri
        ):
            return False
        for field in ("labels", "definitions"):
            pairs = entity[field]
            if len({tuple(pair) for pair in pairs}) != len(pairs) or any(
                not text.strip()
                or len(text) > 16000
                or re.fullmatch(r"(?:|[a-z]+(?:-[a-z0-9]+)*)", language) is None
                for text, language in pairs
            ):
                return False
        for field in ("synonyms", "examples"):
            values = entity[field]
            if len(set(values)) != len(values) or any(
                not text.strip() or len(text) > 16000 for text in values
            ):
                return False
    return True


def validate_startup_failure(value, payload_byte_length, expected_registry_hash):
    """Original-byte budget only; attempt/profile/provenance are runtime-owned."""
    return (
        type(payload_byte_length) in {int, float}
        and 0 < payload_byte_length <= ERROR_CATALOG["startup"]["maxPayloadBytes"]
        and payload_byte_length == int(payload_byte_length)
        and isinstance(expected_registry_hash, str)
        and re.fullmatch(r"[0-9a-f]{64}", expected_registry_hash) is not None
        and validate("startupFailure", value)
        and value["registryHash"] == expected_registry_hash
    )


def startup_error(code, params=None):
    """Construct only the canonical finite startup projection, or safe internal error."""
    from copy import deepcopy

    spec = ERROR_CATALOG["startup"]["codes"].get(code)
    if spec is not None:
        candidate = {
            "code": code,
            "messageKey": spec["messageKey"],
            "retryable": spec["retryable"],
            "params": {} if params is None else deepcopy(params),
        }
        if validate("error_startup", candidate):
            return candidate
    return startup_error("INTERNAL_ERROR", {})


def business3_error(code, params=None):
    """Normal business3 errors stay in error3; startup-only codes cannot enter it."""
    from copy import deepcopy

    spec = ERROR_CATALOG["codes"].get(code)
    if spec is not None:
        candidate = {
            "code": code,
            "messageKey": spec["messageKey"],
            "retryable": spec["retryable"],
            "params": {} if params is None else deepcopy(params),
        }
        if validate_business3("error", candidate):
            return candidate
    return business3_error("INTERNAL_ERROR", {})


def validate_business3(name, value):
    """Strict explicit profile validation, not runtime/session or Store readiness."""
    profiles = {
        "request": "request3",
        "response": "response3",
        "notification": "notification3",
        "envelope": "envelope3",
        "error": "error3",
        "bootstrapError": "error_bootstrap3",
        "project": "project3",
        "result_project.get": "result_project.get3",
        "result_hello": "result_hello3",
    }
    return validate(profiles.get(name, name), value)


def ownership_detail_matches(params, value):
    import base64
    import binascii
    import hashlib

    if not (
        validate("params_project.ownership.detail", params)
        and validate("result_project.ownership.detail", value)
    ):
        return False
    manifest, start, segments = value["manifest"], params["startOrdinal"], value["segments"]
    count = (manifest["totalBytes"] + 32767) // 32768
    end = start + len(segments)
    if (
        value["projectId"] != params["projectId"]
        or value["detailRef"] != params["detailRef"]
        or value["startOrdinal"] != start
        or count != manifest["segmentCount"]
        or len(segments) > params["pageSize"]
        or not start < end <= count
        or (
            params["documentHash"] is not None
            and params["documentHash"] != manifest["documentHash"]
        )
        or value["nextOrdinal"] != (None if end == count else end)
        or value["complete"] != (end == count)
    ):
        return False
    for ordinal, segment in enumerate(segments, start):
        length = min(32768, manifest["totalBytes"] - ordinal * 32768)
        if (
            segment["ordinal"] != ordinal
            or segment["byteOffset"] != ordinal * 32768
            or segment["rawByteLength"] != length
        ):
            return False
        try:
            raw = base64.b64decode(segment["dataBase64"], validate=True)
        except (ValueError, binascii.Error):
            return False
        if len(raw) != length or hashlib.sha256(raw).hexdigest() != segment["sha256"]:
            return False
    return True


def matches_business3_response(request, response, expected_registry_hash):
    """Pending-request binding only; actual ready gates remain runtime-owned."""
    from copy import deepcopy

    if not (
        validate("hash", expected_registry_hash)
        and validate_business3("request", request)
        and validate_business3("response", response)
    ):
        return False
    if any(request[k] != response[k] for k in ("id", "method")):
        return False
    if request["method"] in {"project.ontology.export", "project.ontology.import.check"}:
        return request["engineSessionId"] == response["engineSessionId"]
    if request["method"] == "project.agent.before_commit":
        if request["engineSessionId"] != response["engineSessionId"]:
            return False
        if not response["ok"]:
            return True
        params, result = request["params"], response["result"]
        return (
            result["projectId"] == params["projectId"]
            and result["operationId"] == params["operationId"]
        )
    if request["method"] == "project.ownership.detail":
        return request["engineSessionId"] == response["engineSessionId"] and (
            not response["ok"] or ownership_detail_matches(request["params"], response["result"])
        )
    if request["method"] == "project.draft.save":
        if request["engineSessionId"] != response["engineSessionId"]:
            return False
        if not response["ok"]:
            return True
        import hashlib

        p, value = request["params"], response["result"]
        return (
            value["projectId"] == p["projectId"]
            and value["operationId"] == p["operationId"]
            and value["editor"] == p["editor"]
            and value["generation"] == p["expectedGeneration"] + 1
            and value["boundDomainRevision"] == p["boundDomainRevision"]
            and value["contentHash"] == hashlib.sha256(p["contentJson"].encode()).hexdigest()
        )
    if request["method"] in {
        "project.catalog",
        "project.create",
        "project.example.create",
        "project.open",
        "project.read",
    }:
        if request["engineSessionId"] != response["engineSessionId"]:
            return False
        if not response["ok"]:
            return True
        method, p, value = request["method"], request["params"], response["result"]
        if method == "project.catalog":
            end = value["offset"] + len(value["items"])
            return (
                len(value["items"]) <= p["pageSize"]
                and end <= value["total"]
                and (
                    end == value["total"]
                    if value["nextCursor"] is None
                    else bool(value["items"]) and end < value["total"]
                )
            )
        if method in {"project.create", "project.example.create"}:
            import hashlib

            request_hash = hashlib.sha256(
                json.dumps(p, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            receipt = value["receipt"]
            return (
                value["operationId"] == p["operationId"] == receipt["operationId"]
                and value["projectId"] == receipt["projectId"]
                and value["requestHash"] == receipt["requestHash"] == request_hash
            )
        if value["projectId"] != p["projectId"]:
            return False
        if method == "project.open":
            return True
        workspace, domain = value["workspace"], value["domain"]
        draft = workspace["draft"]
        return (
            workspace["projectId"] == p["projectId"]
            and workspace["inputSnapshotId"] == value["inputSnapshotId"]
            and domain["projectRevision"] == workspace["domainRevision"]
            and draft["editor"] == p["editor"]
            and (
                draft["state"] == "missing"
                or (
                    draft["present"] is True
                    and type(draft["contentJson"]) is str
                    and type(draft["contentHash"]) is str
                    if draft["state"] == "present"
                    else draft["present"] is False
                    and draft["contentJson"] is None
                    and draft["contentHash"] is None
                )
            )
        )
    if request["method"].startswith(("project.checkpoint.", "project.restore.")):
        if request["engineSessionId"] != response["engineSessionId"]:
            return False
        if not response["ok"]:
            return True
        method, p, value = request["method"], request["params"], response["result"]
        if value["projectId"] != p["projectId"]:
            return False
        if method == "project.checkpoint.list":
            items = value["items"]
            end = value["offset"] + len(items)
            current = [item for item in items if item["isCurrent"]]
            return (
                len(items) <= p["pageSize"]
                and end <= value["total"]
                and (
                    end == value["total"]
                    if value["nextCursor"] is None
                    else bool(items) and end < value["total"]
                )
                and len({item["checkpointRef"] for item in items}) == len(items)
                and len(current) <= 1
            )
        if method == "project.checkpoint.create":
            return value["operationId"] == p["operationId"] and value["reason"] == "manual"
        if method == "project.restore.preview":
            return (
                value["targetCheckpointRef"] == p["targetCheckpointRef"]
                and value["currentCheckpointRef"] == p["expectedCheckpointRef"]
                and value["documentHash"] == value["manifest"]["documentHash"]
            )
        if method == "project.restore.page":
            return value["previewRef"] == p["previewRef"]
        if method == "project.restore.confirm":
            return (
                value["previewRef"] == p["previewRef"]
                and value["documentHash"] == p["documentHash"]
            )
        if method == "project.restore.apply":
            return value["operationId"] == p["operationId"]
        if method != "project.restore.operation.get":
            return False
        if value["state"] == "not-found":
            return value["result"] is None
        return (
            value["result"] is not None
            and value["result"]["operationId"] == p["operationId"]
            and value["result"]["requestHash"] == p["requestHash"]
        )
    if request["method"].startswith("project.learning."):
        if request["engineSessionId"] != response["engineSessionId"]:
            return False
        if not response["ok"]:
            return True
        method, p, value = request["method"], request["params"], response["result"]
        if value["projectId"] != p["projectId"]:
            return False
        if method == "project.learning.read":
            return True
        if value["operationId"] != p["operationId"] or value["taskId"] != p["taskId"]:
            return False
        if method == "project.learning.hint.record":
            return value["level"] == p["level"]
        if method == "project.learning.observation.record":
            return value["observation"] == p["observation"]
        return method in {"project.learning.attempt.start", "project.learning.task.check"}
    if request["method"].startswith("project.quality."):
        if request["engineSessionId"] != response["engineSessionId"]:
            return False
        if not response["ok"]:
            return True
        p, value = request["params"], response["result"]
        if value["projectId"] != p["projectId"]:
            return False
        if request["method"] == "project.quality.read":
            return True
        return value["operationId"] == p["operationId"]
    if request["method"].startswith("changeset."):
        if request["engineSessionId"] != response["engineSessionId"]:
            return False
        if not response["ok"]:
            return True
        p, data = request["params"], response["result"]
        if p["projectId"] != data["projectId"]:
            return False
        if request["method"] == "changeset.preview":
            return p["baseRevision"] == data["baseRevision"] and (
                data["status"] == "ready"
                and data["intent"] == "change"
                and data["targetOperationId"] is None
                if p["intent"] == "change"
                else data["targetOperationId"] == p["targetOperationId"]
                and (data["status"] == "conflict" or data["intent"] == "undo")
            )
        if p["previewHash"] != data["previewHash"]:
            return False
        if request["method"] == "changeset.diff.page":
            return (
                p["documentKind"] == data["documentKind"] and len(data["segments"]) <= p["pageSize"]
            )
        return request["method"] == "changeset.confirm"
    if request["method"] == "hello" and response["ok"]:
        result = response["result"]
        if (
            3 not in request["params"]["supportedVersions"]
            or result["registryHash"] != expected_registry_hash
            or any(
                c not in REGISTRY["foundationProfiles"]["business3"]["methods"]
                for c in result["capabilities"]
            )
        ):
            return False
        # Strict3-only advertised methods must not be checked against legacy2.
        return True
    # Validate v3 first; projecting only known literals reuses the existing
    # strict resource/operation/page bindings without any runtime downgrade.
    q, r = deepcopy(request), deepcopy(response)
    q["protocolVersion"] = r["protocolVersion"] = 2
    if q["method"] == "hello":
        q["params"]["supportedVersions"] = [2]
        if r["ok"]:
            r["result"]["selectedVersion"] = 2
    if q["method"] == "project.get" and r["ok"]:
        r["result"]["formatVersion"] = 2
    if not r["ok"] and r["error"]["code"] == "VERSION_INCOMPATIBLE":
        r["error"]["params"] = {"supportedVersions": [2]}
    return matches_response(q, r)


def business3_hello_outcome(request, response, expected_registry_hash):
    if not matches_business3_response(request, response, expected_registry_hash):
        return "invalid-close"
    if request["method"] != "hello":
        return "invalid-close"
    if response["ok"]:
        return "success"
    if response["error"]["code"] == "VERSION_INCOMPATIBLE":
        return "incompatible-close"
    return "rejected-close"


def accepts_business3_job_event(value, binding):
    if not validate_business3("notification", value):
        return False
    return accepts_job_event({**value, "protocolVersion": 2}, binding)


def source_table_material(table, options, implementation, expected_source_hash, max_encoded_bytes):
    """Owner-internal bounded data-only capture, not a host-object sandbox."""
    try:
        return _capture_source_table(
            table, options, implementation, expected_source_hash, max_encoded_bytes
        )
    except Exception:
        raise ValueError("INVALID_REQUEST") from None


def _capture_source_table(table, options, implementation, expected_source_hash, max_encoded_bytes):
    def invalid():
        raise ValueError("INVALID_REQUEST")

    if (
        type(max_encoded_bytes) not in {int, float}
        or not 1 <= max_encoded_bytes <= 2**53 - 1
        or max_encoded_bytes != int(max_encoded_bytes)
        or type(expected_source_hash) is not str
        or not validate("hash", expected_source_hash)
    ):
        invalid()
    max_encoded_bytes = int(max_encoded_bytes)

    def record(value, names):
        if type(value) is not dict or len(value) != len(names):
            invalid()
        for key in value:
            if type(key) is not str or key not in names:
                invalid()
        return {key: dict.__getitem__(value, key) for key in names}

    def array(value, maximum):
        if type(value) is not list or len(value) > min(maximum, max_encoded_bytes):
            invalid()
        return value

    t = record(table, ("source_hash", "sheet", "fields", "rows"))
    o = record(options, ("format", "encoding", "sheet"))
    impl = record(
        implementation, ("executionSemanticsVersion", "engineVersion", "dependencyLockHash")
    )
    if (
        type(t["source_hash"]) is not str
        or t["source_hash"] != expected_source_hash
        or type(t["sheet"]) is not str
        or type(o["format"]) is not str
        or (o["encoding"] is not None and type(o["encoding"]) is not str)
        or (o["sheet"] is not None and type(o["sheet"]) is not str)
        or any(type(value) is not str for value in impl.values())
        or not validate("implementation", impl)
    ):
        invalid()
    if o["format"] == "csv":
        if (
            o["encoding"] not in {"utf-8", "utf-8-sig", "gb18030", "big5", "utf-16"}
            or o["sheet"] is not None
            or t["sheet"] != "CSV"
        ):
            invalid()
    elif (
        o["format"] != "xlsx"
        or o["encoding"] is not None
        or not t["sheet"]
        or o["sheet"] != t["sheet"]
    ):
        invalid()
    fields, rows = array(t["fields"], 256), array(t["rows"], 50000)
    if not fields:
        invalid()
    chunks = []
    total = 0

    def reserve(size):
        nonlocal total
        if size > max_encoded_bytes - total:
            invalid()
        total += size

    def token(text):
        reserve(len(text))
        chunks.append(text.encode("ascii"))

    def string(value, maximum=None, field=False, no_nul=False):
        if type(value) is not str:
            invalid()
        size = 2
        if size > max_encoded_bytes - total:
            invalid()
        for count, char in enumerate(value, 1):
            cp = ord(char)
            if 0xD800 <= cp <= 0xDFFF or (no_nul and cp == 0):
                invalid()
            if maximum is not None and count > maximum:
                invalid()
            size += (
                2
                if char in '\\"\b\f\n\r\t'
                else 6
                if cp < 32
                else 1
                if cp < 128
                else 2
                if cp < 2048
                else 3
                if cp < 65536
                else 4
            )
            if size > max_encoded_bytes - total:
                invalid()
        if field and (not value or value.isspace()):
            invalid()
        reserve(size)
        # Only the captured immutable primitive reaches json.dumps. Charge first;
        # never deepcopy/stringify caller objects or return a partial material.
        encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if len(encoded) != size:
            invalid()
        chunks.append(encoded)

    token("[")
    string("ontolearn.source-table")
    token(",1,")
    string(t["source_hash"])
    token(",[")
    string(o["format"])
    token(",")
    token("null") if o["encoding"] is None else string(o["encoding"])
    token(",")
    token("null") if o["sheet"] is None else string(o["sheet"])
    token("],[")
    for i, key in enumerate(("executionSemanticsVersion", "engineVersion", "dependencyLockHash")):
        if i:
            token(",")
        string(impl[key])
    token("],")
    string(t["sheet"])
    token(",[")
    seen = set()
    for i in range(len(fields)):
        value = list.__getitem__(fields, i)
        if i:
            token(",")
        string(value, 32768, True, True)
        if value in seen:
            invalid()
        seen.add(value)
    token("],[")
    previous = 1
    kinds = {"string", "empty", "boolean", "datetime", "date", "number"}
    for i in range(len(rows)):
        row = record(list.__getitem__(rows, i), ("number", "cells"))
        number = row["number"]
        if (
            type(number) not in {int, float}
            or not 2 <= number <= 50001
            or number != int(number)
            or number <= previous
        ):
            invalid()
        previous = number
        cells = array(row["cells"], 256)
        if len(cells) != len(fields):
            invalid()
        if i:
            token(",")
        token(f"[{int(number)},[")
        for j in range(len(cells)):
            cell = record(list.__getitem__(cells, j), ("text", "kind"))
            text, kind = cell["text"], cell["kind"]
            if (
                type(text) is not str
                or type(kind) is not str
                or kind not in kinds
                or (o["format"] == "csv" and kind != "string")
                or (kind == "empty" and text != "")
                or (kind == "boolean" and text not in ("true", "false"))
            ):
                invalid()
            if j:
                token(",")
            token("[")
            string(text, 32768, False, True)
            token(",")
            string(kind)
            token("]")
        token("]]")
    token("]]")
    output = b"".join(chunks)
    if len(output) != total:
        invalid()
    return output


def source_table_digest(table, options, implementation, expected_source_hash, max_encoded_bytes):
    material = source_table_material(
        table, options, implementation, expected_source_hash, max_encoded_bytes
    )
    return {"sha256": hashlib.sha256(material).hexdigest(), "encodedBytes": len(material)}


def accepts_job_event(value, binding):
    # The binding is a trusted-side projection, but never assume its shape. Reject
    # corruption before arithmetic/indexing; never silently default sequence/state.
    fields = {
        "engineSessionId",
        "projectId",
        "jobId",
        "subscriptionId",
        "lastSeq",
        "stateVersion",
        "state",
    }
    if not isinstance(binding, dict) or set(binding) != fields:
        return False
    if any(
        not validate("id", binding[k])
        for k in ("engineSessionId", "projectId", "jobId", "subscriptionId")
    ):
        return False
    if any(
        type(binding[k]) is not int or not low <= binding[k] <= 9007199254740991
        for k, low in (("lastSeq", 0), ("stateVersion", 1))
    ):
        return False
    if not isinstance(binding["state"], str) or binding["state"] not in {
        "queued",
        "running",
        "cancelling",
        "succeeded",
        "failed",
        "cancelled",
    }:
        return False
    if not validate("notification", value) or value["event"] == "session.status":
        return False
    if not (
        all(
            value[k] == binding[k]
            for k in ("engineSessionId", "projectId", "jobId", "subscriptionId")
        )
        and value["seq"] == binding["lastSeq"] + 1
        and binding["state"] not in {"succeeded", "failed", "cancelled"}
    ):
        return False
    data = value["data"]
    if value["event"] == "job.progress":
        return data["stateVersion"] == binding["stateVersion"]
    if data["stateVersion"] != binding["stateVersion"] + 1:
        return False
    return data["state"] == binding["state"] or permits_transition(
        binding["state"], data["state"], binding["stateVersion"], data["stateVersion"], False
    )


def cursor_matches(record, request, now_ms):
    return (
        validate("cursorRecord", record)
        and validate("params_result.page", request)
        and record["token"] == request["cursor"]
        and record["binding"] == request["binding"]
        and record["pageSize"] == request["pageSize"]
        and record["expiresAtMs"] > now_ms
    )


def derive_dependencies(capability, definition_id, scope, definitions):
    policies = json.loads((ROOT / "dependencies.json").read_text(encoding="utf-8"))["policies"]
    if capability not in policies or scope not in {"asserted", "asserted+derived", "scenario"}:
        raise ValueError("INVALID_REQUEST")
    if scope not in REGISTRY["capabilities"][capability]["dataScopes"]:
        raise ValueError("INVALID_REQUEST")
    policy = policies[capability]
    if len(definitions) > 4096 or any(not validate("definitionIdentity", d) for d in definitions):
        raise ValueError("INVALID_REQUEST")
    by_key = {d["family"] + ":" + d["id"]: d for d in definitions}
    if len(by_key) != len(definitions):
        raise ValueError("INVALID_REQUEST")
    sets = {}
    selected = {"facts:asserted"}
    families = policy["sets"] + (policy["withDerived"] if scope == "asserted+derived" else [])
    for family in families:
        sets[family] = sorted(k for k in by_key if k.startswith(family + ":"))
        selected.update(sets[family])
    if policy["selectedFamily"]:
        selected.add(policy["selectedFamily"] + ":" + definition_id)

    pending = [key for key in selected if key != "facts:asserted"]
    visited = set()
    while pending:
        key = pending.pop()
        if key in visited:
            continue
        visited.add(key)
        if key not in by_key:
            raise ValueError("INVALID_REQUEST")
        for reference in by_key[key]["references"]:
            selected.add(reference)
            if len(selected) > 4096:
                raise ValueError("INVALID_REQUEST")
            if reference != "facts:asserted" and reference not in visited:
                pending.append(reference)
    if len(selected) > 4096:
        raise ValueError("INVALID_REQUEST")
    return {"keys": sorted(selected), "sets": sets}


def matches_ordinary_response(request, response, binding=None):
    """Private association requires the original issued choice/verified lease binding."""
    if not validate("request", request) or not validate("response", response):
        return False
    if request["method"] != "ordinary.library" or any(
        request[k] != response[k] for k in ("id", "method", "engineSessionId")
    ):
        return False
    if not response["ok"]:
        return True
    p, data = request["params"], response["result"]
    if any(p[k] != data[k] for k in ("op", "ownerId")):
        return False
    if p["op"] == "choices":
        rows = data["choices"]
        return (
            p["menuSeq"] == data["menuSeq"]
            and len({r["choiceRef"] for r in rows}) == len(rows)
            and len({r["projectId"] for r in rows}) == len(rows)
        )
    if any(p[k] != data[k] for k in ("actionId", "actionSeq")):
        return False
    if p["op"] == "release":
        return True
    if p["op"] == "commit" and p["leaseRef"] != data["leaseRef"]:
        return False
    if not isinstance(binding, dict) or binding.get("projectId") != data["project"]["projectId"]:
        return False
    if "project" in binding and not validate("result_project.get", binding["project"]):
        return False
    if p["op"] == "commit" and "project" not in binding:
        return False
    return "project" not in binding or binding["project"] == data["project"]


def matches_response(request, response):
    if not validate("request", request) or not validate("response", response):
        return False
    if any(request[k] != response[k] for k in ("id", "method")):
        return False
    if request["method"] != "hello" and request["engineSessionId"] != response["engineSessionId"]:
        return False
    if request["method"] == "ordinary.library":
        return matches_ordinary_response(request, response)
    if request["method"].startswith("query."):
        return matches_query_consumer_response(request, response)
    if not response["ok"]:
        return True
    p, data = request["params"], response["result"]
    method = request["method"]
    if method == "hello":
        return 2 in p["supportedVersions"] and all(
            c in REGISTRY["v2Runtime"] or c == REGISTRY["ordinaryLibrary"]["method"]
            for c in data["capabilities"]
        )
    if data is None:
        return True
    for key in ("projectId", "jobId", "resultId"):
        if key in p and key in data and p[key] != data[key]:
            return False
    if method == "operation.get" and p["operationId"] != data["operationId"]:
        return False
    if method == "job.unsubscribe" and p["subscriptionId"] != data["subscriptionId"]:
        return False
    if method == "job.create":
        if p["input"] != data["input"] or p["confirmationRef"] != data["confirmationRef"]:
            return False
        if p["operationId"] != data["operationId"] or p["capability"] != data["capability"]:
            return False
        if any(p["input"][k] != data[k] for k in ("inputSnapshotId", "scope", "parametersHash")):
            return False
    if method == "result.current":
        if data["state"] != "current" or p["implementation"] != data["implementation"]:
            return False
        if any(p[k] != data[k] for k in ("kind", "definitionId", "scope", "parametersHash")):
            return False
    if method == "session.ping" and p["nonce"] != data["nonce"]:
        return False
    if method == "result.page":
        return p["binding"] == data["binding"] and len(data["rows"]) <= p["pageSize"]
    if method == "job.list":
        b = data["binding"]
        if len(data["jobs"]) > p["pageSize"]:
            return False
        if b["projectId"] != p["projectId"] or b["filter"] != p["filter"]:
            return False
        if p["listSnapshotId"] and p["listSnapshotId"] != b["listSnapshotId"]:
            return False
        if any(j["projectId"] != p["projectId"] for j in data["jobs"]):
            return False
    return True


def permits_transition(before, after, before_version, after_version, final_before_cancel):
    states = json.loads((ROOT / "states.json").read_text(encoding="utf-8"))["transitions"]
    return (
        after in states.get(before, [])
        and type(before_version) in {int, float}
        and type(after_version) in {int, float}
        and math.isfinite(before_version)
        and math.isfinite(after_version)
        and before_version == int(before_version)
        and after_version == int(after_version)
        and 1 <= before_version < after_version <= 9007199254740991
        and not (before == "cancelling" and after == "succeeded" and not final_before_cancel)
    )


def job_list_cursor_matches(record, request, now_ms):
    return (
        validate("jobListCursorRecord", record)
        and validate("params_job.list", request)
        and record["token"] == request["cursor"]
        and record["binding"]["projectId"] == request["projectId"]
        and record["binding"]["listSnapshotId"] == request["listSnapshotId"]
        and record["binding"]["filter"] == request["filter"]
        and record["pageSize"] == request["pageSize"]
        and record["expiresAtMs"] > now_ms
    )


def validation_projection_matches_resources(projection, resources):
    """Association only: trusted lookup/hash verification and real projection are caller duties."""
    if not validate("validationProjection", projection) or not validate(
        "validationResources", resources
    ):
        return False
    derived = projection["derived"]
    expected = {
        role: projection[role + "Ref"]
        for role in ("assertedFacts", "ontologyAxioms", "constraints")
    }
    if derived:
        expected.update(derivedFacts=derived["factsRef"], derivedAxioms=derived["axiomsRef"])
    if len(resources) != len(expected):
        return False
    if (
        derived
        and len(
            {
                row["resultState"]
                for row in resources
                if row["role"] in {"derivedFacts", "derivedAxioms"}
            }
        )
        != 1
    ):
        return False
    for role, reference in expected.items():
        matches = [row for row in resources if row["role"] == role]
        if len(matches) != 1:
            return False
        row = matches[0]
        if row["constraintDefinitionId"] != (
            projection["constraintDefinitionId"] if role == "constraints" else None
        ):
            return False
        if row["ref"] != reference or any(
            row[k] != projection[k] for k in ("projectId", "inputSnapshotId")
        ):
            return False
        if role in {"derivedFacts", "derivedAxioms"}:
            if (
                not derived
                or row["resultId"] != derived["resultId"]
                or row["resultKind"] != "reasoning"
                or row["payloadStatus"] != "available"
                or row["resultState"] not in {"current", "stale", "historical"}
                or row["implementation"] != derived["implementation"]
                or (projection["inputSelection"] == "current" and row["resultState"] != "current")
            ):
                return False
        elif any(
            row[k] is not None
            for k in ("resultId", "implementation", "resultKind", "payloadStatus", "resultState")
        ):
            return False
    return True


def matches_query_consumer_response(request, response, expected=None):
    """Authenticate successful query DTOs; correct error envelopes still match."""
    if not validate("request", request) or not validate("response", response):
        return False
    if any(request[k] != response[k] for k in ("id", "method", "engineSessionId")):
        return False
    if not response["ok"]:
        return True
    method, p, v = request["method"], request["params"], response["result"]
    if method == "query.definition.load":
        valid = (
            v["projectId"] == p["projectId"]
            and v["definitionId"] == p["definitionId"]
            and (
                p["selection"]["kind"] != "historical"
                or v["inputSnapshotId"] == p["selection"]["snapshotId"]
            )
        )
        return valid and (expected is None or all(v.get(k) == x for k, x in expected.items()))
    if method == "query.execution.prepare":
        input_ = v["input"]
        valid = (
            v["projectId"] == p["projectId"]
            and v["operationId"] == p["operationId"]
            and v["definitionBinding"] == p["definitionBinding"]
            and input_["definitionId"] == p["definitionBinding"]["definitionId"]
            and input_["scope"] == p["visibleDraft"]["scope"]
            and len(input_["derivedResultIds"])
            == (1 if input_["scope"] == "asserted+derived" else 0)
            and input_["preparedPlanRef"] is None
            and (
                p["selection"]["kind"] != "historical"
                or input_["inputSnapshotId"] == p["selection"]["snapshotId"]
            )
        )
        return valid and (expected is None or all(v.get(k) == x for k, x in expected.items()))
    if method == "query.result.describe":
        identity, metadata = v["identity"], v["metadata"]
        if (
            identity["projectId"] != p["projectId"]
            or identity["resultId"] != p["resultId"]
            or metadata["kind"] != "query"
            or any(
                identity[k] != metadata[k]
                for k in (
                    "projectId",
                    "resultId",
                    "jobId",
                    "inputSnapshotId",
                    "definitionId",
                    "parametersHash",
                    "scope",
                    "implementation",
                    "inputProjectRevision",
                )
            )
        ):
            return False
        text, query = v["executedText"], v["query"]
        if not (
            text["unicodeScalars"] <= text["utf8Bytes"] <= 4 * text["unicodeScalars"]
            and text["unicodeScalars"] <= text["utf16Units"] <= 2 * text["unicodeScalars"]
        ):
            return False
        if query["kind"] == "SELECT":
            columns = query["columns"]
            if any(c["index"] != i for i, c in enumerate(columns)) or len(
                {c["name"] for c in columns}
            ) != len(columns):
                return False
        return expected is None or all(v.get(k) == x for k, x in expected.items())
    if method in {"query.result.textPage", "query.result.rowsPage"}:
        if p["binding"] != v["identity"]:
            return False
        if method.endswith("textPage"):
            length = len(v["text"].encode("utf-8"))
            if v["utf8Length"] != length or length > p["maxUtf8Bytes"]:
                return False
            if expected is not None:
                end = v["startUtf8Byte"] + length
                if (
                    ("nextUtf8Byte" in expected and v["startUtf8Byte"] != expected["nextUtf8Byte"])
                    or end > expected["executedText"]["utf8Bytes"]
                    or (v["nextCursor"] is None and end != expected["executedText"]["utf8Bytes"])
                ):
                    return False
        else:
            rows = v["rows"]
            if len(rows) > p["pageSize"] or any(
                b["index"] != a["index"] + 1 for a, b in zip(rows, rows[1:], strict=False)
            ):
                return False
            if expected is not None:
                query = expected["query"]
                start = expected.get(
                    "nextIndex", rows[0]["index"] if rows else query.get("rowCount", 0)
                )
                if query["kind"] != "SELECT":
                    return False
                if (
                    any(
                        row["index"] != start + i or len(row["cells"]) != len(query["columns"])
                        for i, row in enumerate(rows)
                    )
                    or start + len(rows) > query["rowCount"]
                    or (v["nextCursor"] is None and start + len(rows) != query["rowCount"])
                ):
                    return False
        return encoded_size(v) <= 131072
    return False
