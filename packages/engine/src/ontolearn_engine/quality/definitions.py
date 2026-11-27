"""Validate the bounded FR-504/505 editor language without evaluating rules.

This is a private domain payload proposal, not an IPC schema or persistence channel.
No graph, Store, execution status or mutable authority is created here.
"""

import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from rdflib import RDF, XSD, Literal

from ontolearn_engine.rdf_snapshot import iri

from .rdf_terms import private_term

MAX_ITEMS = 128
MAX_TEXT = 4096
VARIABLE = re.compile(r"\?[A-Za-z][A-Za-z0-9_]{0,63}\Z")
# Private editor support, not a claim that a runtime implements these datatypes.
DATATYPES = frozenset(
    [str(RDF.langString)]
    + [
        str(XSD[name])
        for name in (
            "string",
            "boolean",
            "integer",
            "int",
            "nonNegativeInteger",
            "decimal",
            "double",
            "float",
            "date",
            "dateTime",
        )
    ]
)


class DefinitionError(ValueError):
    """Safe local diagnostic; never include a rejected value or raw parser exception."""

    def __init__(self, code: str, path: tuple[str | int, ...]):
        self.code, self.path = code, path
        super().__init__(code)


def fail(code: str, path: tuple) -> None:
    raise DefinitionError(code, path)


def shape(value: object, keys: set[str], path: tuple) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        fail("INVALID_FIELDS", path)
    return value


def text(value: object, path: tuple) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > MAX_TEXT
        or any(0xD800 <= ord(char) <= 0xDFFF for char in value)
    ):
        fail("INVALID_TEXT", path)
    return value


def absolute(value: object, path: tuple) -> str:
    value = text(value, path)
    try:
        iri(value)
    except ValueError:
        fail("INVALID_IRI", path)
    return value


def rdf_value(value: object, path: tuple) -> str:
    value = text(value, path)
    try:
        result = private_term(value)
        if isinstance(result, Literal) and result.ill_typed:
            fail("INVALID_LITERAL", path)
        # Match Store's canonical RDF term gate; aliases must be corrected explicitly.
        if result.n3() != value:
            fail("NON_CANONICAL_TERM", path)
    except DefinitionError:
        raise
    except (ValueError, TypeError):
        fail("INVALID_TERM", path)
    return value


def variable(value: object) -> bool:
    return isinstance(value, str) and VARIABLE.fullmatch(value) is not None


def subject(value: object, path: tuple) -> str:
    return value if variable(value) else absolute(value, path)


def object_term(value: object, path: tuple) -> str:
    return value if variable(value) else rdf_value(value, path)


def items(value: object, path: tuple, *, empty: bool = False) -> list:
    if not isinstance(value, list) or not (0 if empty else 1) <= len(value) <= MAX_ITEMS:
        fail("INVALID_LIST", path)
    return value


def positive(value: object, path: tuple, *, zero: bool = False) -> int:
    if type(value) is not int or not (0 if zero else 1) <= value <= 2**31 - 1:
        fail("INVALID_INTEGER", path)
    return value


def numeric(value: object, path: tuple) -> Decimal:
    value = text(value, path)
    if not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)", value):
        fail("INVALID_NUMBER", path)
    try:
        result = Decimal(value)
    except InvalidOperation:
        fail("INVALID_NUMBER", path)
    return result


@dataclass(frozen=True)
class ValidatedDefinition:
    """Canonical immutable payload; consumers cannot mutate a validated value in place."""

    canonical_json: str

    def payload(self) -> dict:
        return json.loads(self.canonical_json)


def validate_definition(value: object) -> ValidatedDefinition:
    if not isinstance(value, dict):
        fail("INVALID_FIELDS", ())
    kind = value.get("kind")
    common = {"schemaVersion", "kind", "id", "revision", "label", "enabled"}
    if kind == "constraint":
        shape(value, common | {"targetClass", "path", "template", "parameters"}, ())
    elif kind == "rule":
        shape(value, common | {"conditions", "conclusions"}, ())
    else:
        fail("UNSUPPORTED_DEFINITION", ("kind",))
    if type(value["schemaVersion"]) is not int or value["schemaVersion"] != 1:
        fail("UNSUPPORTED_VERSION", ("schemaVersion",))
    text(value["id"], ("id",))
    text(value["label"], ("label",))
    positive(value["revision"], ("revision",))
    if type(value["enabled"]) is not bool:
        fail("INVALID_BOOLEAN", ("enabled",))
    if kind == "constraint":
        _constraint(value)
    else:
        _rule(value)
    return ValidatedDefinition(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )


def _constraint(value: dict) -> None:
    absolute(value["targetClass"], ("targetClass",))
    absolute(value["path"], ("path",))
    template, params = value["template"], value["parameters"]
    if template == "required":
        shape(params, set(), ("parameters",))
    elif template == "datatype":
        shape(params, {"datatype"}, ("parameters",))
        if not isinstance(params["datatype"], str) or params["datatype"] not in DATATYPES:
            fail("UNSUPPORTED_DATATYPE", ("parameters", "datatype"))
    elif template == "maxCount":
        shape(params, {"maxCount"}, ("parameters",))
        positive(params["maxCount"], ("parameters", "maxCount"), zero=True)
    elif template == "allowedValues":
        shape(params, {"values"}, ("parameters",))
        values = items(params["values"], ("parameters", "values"))
        for index, item in enumerate(values):
            rdf_value(item, ("parameters", "values", index))
        if len(set(values)) != len(values):
            fail("DUPLICATE_VALUE", ("parameters", "values"))
    elif template == "numericRange":
        shape(params, {"minInclusive", "maxInclusive"}, ("parameters",))
        low, high = params["minInclusive"], params["maxInclusive"]
        if low is None and high is None:
            fail("EMPTY_RANGE", ("parameters",))
        if low is not None:
            numeric(low, ("parameters", "minInclusive"))
        if high is not None:
            numeric(high, ("parameters", "maxInclusive"))
        if low is not None and high is not None and Decimal(low) > Decimal(high):
            fail("REVERSED_RANGE", ("parameters",))
    else:
        fail("UNSUPPORTED_TEMPLATE", ("template",))


def compile_constraint_turtle(defn: dict) -> str:
    """Deterministic valid SHACL Turtle for one validated FR-504 template.

    The emitted document stays inside the engine's finite SHACL subset: one
    named node shape targeting the class plus exactly one named property shape
    carrying the compiled template constraint. Output depends only on the
    canonical validated payload, never on save order or caller state.
    """
    payload = validate_definition(defn).payload()
    if payload["kind"] != "constraint":
        fail("UNSUPPORTED_DEFINITION", ("kind",))
    # The definition id becomes part of the shape IRIs; unsafe characters must
    # be rejected cleanly instead of leaking into generated Turtle.
    try:
        iri("urn:ontolearn:shape:" + payload["id"])
    except ValueError:
        fail("INVALID_IRI", ("id",))
    template, parameters = payload["template"], payload["parameters"]
    if template == "required":
        constraint = "sh:minCount 1"
    elif template == "datatype":
        constraint = f"sh:datatype <{parameters['datatype']}>"
    elif template == "maxCount":
        constraint = f"sh:maxCount {parameters['maxCount']}"
    elif template == "allowedValues":
        # Values are already exact canonical N3 terms (validated rdf_value).
        constraint = "sh:in ( " + " ".join(parameters["values"]) + " )"
    else:
        # numericRange: at least one bound exists; exact Decimal lexical forms
        # as xsd:decimal literals match both pySHACL and the shape whitelist.
        bounds = []
        if parameters["minInclusive"] is not None:
            bounds.append(f'sh:minInclusive "{parameters["minInclusive"]}"^^xsd:decimal')
        if parameters["maxInclusive"] is not None:
            bounds.append(f'sh:maxInclusive "{parameters["maxInclusive"]}"^^xsd:decimal')
        constraint = " ;\n    ".join(bounds)
    shape = f"<urn:ontolearn:shape:{payload['id']}>"
    property_shape = f"<urn:ontolearn:shape:{payload['id']}:property>"
    # SHACL 1.0 sh:deactivated preserves the enabled=False state through a
    # Turtle round-trip; enabled=True output stays byte-identical (B04).
    deactivated = "" if payload["enabled"] else "    sh:deactivated true ;\n"
    return (
        "@prefix sh: <http://www.w3.org/ns/shacl#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n"
        f"{shape} a sh:NodeShape ;\n"
        f"    sh:targetClass <{payload['targetClass']}> ;\n"
        f"{deactivated}"
        f"    sh:property {property_shape} .\n\n"
        f"{property_shape} a sh:PropertyShape ;\n"
        f"    sh:path <{payload['path']}> ;\n"
        f"    {constraint} .\n"
    )


def _pattern(value: object, path: tuple) -> set[str]:
    if not isinstance(value, dict):
        fail("INVALID_FIELDS", path)
    if value.get("kind") == "type":
        shape(value, {"kind", "subject", "class"}, path)
        subject(value["subject"], (*path, "subject"))
        absolute(value["class"], (*path, "class"))
        candidates = [value["subject"]]
    elif value.get("kind") == "property":
        shape(value, {"kind", "subject", "path", "object"}, path)
        subject(value["subject"], (*path, "subject"))
        absolute(value["path"], (*path, "path"))
        object_term(value["object"], (*path, "object"))
        candidates = [value["subject"], value["object"]]
    else:
        fail("UNSUPPORTED_PATTERN", (*path, "kind"))
    return {item for item in candidates if variable(item)}


def _rule(value: dict) -> None:
    bound: set[str] = set()
    comparisons = []
    for index, condition in enumerate(items(value["conditions"], ("conditions",))):
        path = ("conditions", index)
        if isinstance(condition, dict) and condition.get("kind") == "compare":
            shape(condition, {"kind", "left", "operator", "right"}, path)
            if not isinstance(condition["operator"], str) or condition["operator"] not in {
                "eq",
                "ne",
                "lt",
                "le",
                "gt",
                "ge",
            }:
                fail("UNSUPPORTED_COMPARISON", (*path, "operator"))
            object_term(condition["left"], (*path, "left"))
            object_term(condition["right"], (*path, "right"))
            comparisons.append((path, condition))
        else:
            bound |= _pattern(condition, path)
    for path, condition in comparisons:
        for key in ("left", "right"):
            if variable(condition[key]) and condition[key] not in bound:
                fail("UNBOUND_VARIABLE", (*path, key))
    for index, conclusion in enumerate(items(value["conclusions"], ("conclusions",))):
        used = _pattern(conclusion, ("conclusions", index))
        if not used <= bound:
            fail("UNBOUND_VARIABLE", ("conclusions", index))
    if len(comparisons) == len(value["conditions"]):
        fail("MISSING_INPUT_PATTERN", ("conditions",))
