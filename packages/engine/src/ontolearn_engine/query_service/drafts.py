"""Bounded offline authoring. No graph execution, database access or network calls.

Values are structured RDF terms, never free-form code fragments. Saved queries
are proposals for the owning project service, not a second persistence channel.
Editor/model text remains untrusted until the real executor applies its policy.
"""

import copy
import hashlib
import json
import re


class DraftError(ValueError):
    """Safe private validation error with no user value or filesystem detail."""


def _object(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise DraftError("query.invalidDraft")


def _text(value, maximum, minimum=0):
    if (
        not isinstance(value, str)
        or not minimum <= len(value) <= maximum
        or any(0xD800 <= ord(c) <= 0xDFFF for c in value)
    ):
        raise DraftError("query.invalidDraft")
    return value


def _iri(value):
    _text(value, 2048, 1)
    if not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value) or any(
        c.isspace() or ord(c) <= 32 or ord(c) == 127 or c in '<>"{}|^`\\' for c in value
    ):
        raise DraftError("query.invalidIri")
    return value


def serialize_term(term):
    if not isinstance(term, dict):
        raise DraftError("query.invalidTerm")
    if term.get("kind") == "iri":
        _object(term, ("kind", "value"))
        return f"<{_iri(term['value'])}>"
    _object(term, ("kind", "value", "language", "datatype"))
    if term["kind"] != "literal":
        raise DraftError("query.invalidTerm")
    value = _text(term["value"], 8192)
    language, datatype = term["language"], term["datatype"]
    if language is not None:
        _text(language, 64, 1)
        if not re.fullmatch(r"[A-Za-z]+(?:-[A-Za-z0-9]+)*", language) or datatype is not None:
            raise DraftError("query.invalidTerm")
    if datatype is not None:
        _iri(datatype)
    quoted = json.dumps(value, ensure_ascii=False).replace("\x7f", r"\u007F")
    if language is not None:
        return quoted + "@" + language.lower()
    return quoted + (f"^^<{datatype}>" if datatype is not None else "")


def compile_visual(query):
    _object(query, ("classIri", "fields", "conditions"))
    class_iri = _iri(query["classIri"])
    fields, conditions = query["fields"], query["conditions"]
    if (
        not isinstance(fields, list)
        or len(fields) > 16
        or not isinstance(conditions, list)
        or len(conditions) > 32
    ):
        raise DraftError("query.invalidDraft")
    selected = ["?item", *[f"?field{i}" for i in range(len(fields))]]
    lines = [f"  ?item a <{class_iri}> ."]
    operators = {"eq": "=", "ne": "!=", "lt": "<", "le": "<=", "gt": ">", "ge": ">="}
    for i, condition in enumerate(conditions):
        if not isinstance(condition, dict):
            raise DraftError("query.invalidDraft")
        operator = condition.get("operator")
        if not isinstance(operator, str):
            raise DraftError("query.invalidDraft")
        exists = operator in ("exists", "not-exists")
        _object(
            condition, ("predicate", "operator") if exists else ("predicate", "operator", "value")
        )
        predicate = _iri(condition["predicate"])
        triple = f"?item <{predicate}> ?condition{i} ."
        if exists:
            negation = "NOT " if operator == "not-exists" else ""
            lines.append(f"  FILTER {negation}EXISTS {{ {triple} }}")
        elif operator in operators:
            value = serialize_term(condition["value"])
            lines.extend([f"  {triple}", f"  FILTER (?condition{i} {operators[operator]} {value})"])
        else:
            raise DraftError("query.invalidDraft")
    for i, field in enumerate(fields):
        _object(field, ("predicate", "label"))
        predicate = _iri(field["predicate"])
        _text(field["label"], 128, 1)
        lines.append(f"  OPTIONAL {{ ?item <{predicate}> ?field{i} . }}")
    return (
        "SELECT DISTINCT "
        + " ".join(selected)
        + " WHERE {\n"
        + "\n".join(lines)
        + ("\n}\nORDER BY " + " ".join(selected))
    )


def validate_draft(draft):
    _object(draft, ("name", "description", "sparql", "scope", "capabilityQuestion", "source"))
    normalized = copy.deepcopy(draft)
    normalized["name"] = _text(draft["name"], 128).strip()
    normalized["sparql"] = _text(draft["sparql"], 65536).strip()
    if not normalized["name"] or not normalized["sparql"]:
        raise DraftError("query.invalidDraft")
    _text(draft["description"], 4096)
    _text(draft["capabilityQuestion"], 4096)
    if draft["scope"] not in ("asserted", "asserted+derived") or draft["source"] not in (
        "template",
        "visual",
        "editor",
        "model",
    ):
        raise DraftError("query.invalidDraft")
    return normalized


def save_intent(draft, *, definition_id, expected_revision):
    """Build immutable-value definition intent for T01 preview/confirm; never commit.

    Returned digest identifies this draft only. It is not an execution input hash,
    current-result identity, commit marker or authorization proof.
    """
    if not isinstance(definition_id, str) or not re.fullmatch(
        r"[A-Za-z0-9_.-]{1,128}", definition_id
    ):
        raise DraftError("query.invalidIdentity")
    if type(expected_revision) is not int or not 0 <= expected_revision <= 9007199254740991:
        raise DraftError("query.invalidRevision")
    payload = validate_draft(draft)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "family": "query",
        "id": definition_id,
        "expectedProjectRevision": expected_revision,
        "draftDigest": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
        "value": payload,
    }
