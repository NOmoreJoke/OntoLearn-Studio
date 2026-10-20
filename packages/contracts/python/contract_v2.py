"""I03 pure contract checker; not imported by the production v1 engine.

Same deliberately small JSON Schema vocabulary as the TS/zod adapter.
"""

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
        if valid and name in {"params_job.create", "params_job.list"}:
            return semantic({"kind": "request", "method": name[7:], "params": value})
        return valid
    except (KeyError, TypeError, ValueError, OverflowError, RecursionError):
        return False


def accepts_job_event(value, binding):
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


def matches_response(request, response):
    if not validate("request", request) or not validate("response", response):
        return False
    if any(request[k] != response[k] for k in ("id", "method")):
        return False
    if request["method"] != "hello" and request["engineSessionId"] != response["engineSessionId"]:
        return False
    if not response["ok"]:
        return True
    p, data = request["params"], response["result"]
    method = request["method"]
    if method == "hello":
        return 2 in p["supportedVersions"] and all(
            c in REGISTRY["v2Runtime"] for c in data["capabilities"]
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
