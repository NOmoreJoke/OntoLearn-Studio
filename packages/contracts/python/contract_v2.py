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
        if valid and name in {"params_job.create", "params_job.list"}:
            return semantic({"kind": "request", "method": name[7:], "params": value})
        return valid
    except (KeyError, TypeError, ValueError, OverflowError, RecursionError):
        return False


def validate_business3(name, value):
    """Foundation validator; no runtime/session or Store readiness is enabled."""
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
