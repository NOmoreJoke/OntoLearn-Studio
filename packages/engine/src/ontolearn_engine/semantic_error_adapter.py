"""Pure I05 reason classification using the I03 canonical error documents.

I04 supplies canonical documents and verified producer/stage/origin context.
Enums do not prove provenance. No exception inspection, I/O, Store, Job, retry,
protocol registration or runtime resource resolution happens in this module.
"""

import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType


class Producer(Enum):
    TURTLE = "turtle"
    QUERY = "query"
    REASON = "reason"
    SHACL = "shacl"
    PROJECTION = "projection"
    PUBLIC_PARAMS = "public-params"


class Stage(Enum):
    SYNTAX = "syntax"
    QUERY = "query"
    RULE = "rule"
    CONSTRAINT = "constraint"
    PROJECTION = "projection"
    PARAMS = "params"


class Origin(Enum):
    VERIFIED_USER_INPUT = "verified-user-input"
    TRUSTED_INTERNAL = "trusted-internal"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ErrorContext:
    stage: Stage
    origin: Origin


@dataclass(frozen=True)
class _Spec:
    message_key: str
    retryable: bool
    parameter: str | None
    values: frozenset[str]


_STAGES = {
    Producer.TURTLE: frozenset({Stage.SYNTAX, Stage.CONSTRAINT}),
    Producer.QUERY: frozenset({Stage.SYNTAX, Stage.QUERY}),
    Producer.REASON: frozenset({Stage.SYNTAX, Stage.RULE}),
    Producer.SHACL: frozenset({Stage.SYNTAX, Stage.CONSTRAINT}),
    Producer.PROJECTION: frozenset({Stage.PROJECTION}),
    Producer.PUBLIC_PARAMS: frozenset({Stage.PARAMS}),
}
_GRAPH_PRODUCERS = frozenset({Producer.TURTLE, Producer.QUERY, Producer.REASON, Producer.SHACL})
_ENGINE_PRODUCERS = _GRAPH_PRODUCERS | {Producer.PROJECTION}
_GRAPH_INPUTS = frozenset(
    {
        (Producer.TURTLE, Stage.SYNTAX),
        (Producer.TURTLE, Stage.CONSTRAINT),
        (Producer.QUERY, Stage.SYNTAX),
        (Producer.REASON, Stage.SYNTAX),
        (Producer.REASON, Stage.RULE),
        (Producer.SHACL, Stage.SYNTAX),
        (Producer.SHACL, Stage.CONSTRAINT),
    }
)
_PARAMS_REASONS = frozenset(
    {"TEXT_TYPE_INVALID", "SCOPE_SELECTION_TYPE_INVALID", "UNSELECTED_RULES_PRESENT"}
)
# These map actual internal branch pairs to public category identifiers,
# not public messageKey/retryable/parameter-schema data.
_RESOURCES = {
    "TEXT_INPUT_LIMIT": (
        "semanticInput",
        frozenset(
            {
                (Producer.TURTLE, Stage.SYNTAX),
                (Producer.TURTLE, Stage.CONSTRAINT),
                (Producer.QUERY, Stage.QUERY),
            }
        ),
    ),
    "GRAPH_INPUT_LIMIT": (
        "semanticInput",
        frozenset(
            {
                (Producer.TURTLE, Stage.SYNTAX),
                (Producer.TURTLE, Stage.CONSTRAINT),
                (Producer.QUERY, Stage.SYNTAX),
                (Producer.REASON, Stage.SYNTAX),
                (Producer.SHACL, Stage.SYNTAX),
                (Producer.SHACL, Stage.CONSTRAINT),
                (Producer.PROJECTION, Stage.PROJECTION),
            }
        ),
    ),
    "QUERY_RESULT_LIMIT": ("semanticResult", frozenset({(Producer.QUERY, Stage.QUERY)})),
    "RDFS_RESULT_LIMIT": ("semanticResult", frozenset({(Producer.REASON, Stage.RULE)})),
    "RULE_MATCH_WORK_LIMIT": ("semanticWork", frozenset({(Producer.REASON, Stage.RULE)})),
    "RULE_EVIDENCE_RESULT_LIMIT": ("semanticResult", frozenset({(Producer.REASON, Stage.RULE)})),
    "WORK_LIMIT": (
        "semanticWork",
        frozenset(
            {
                (Producer.REASON, Stage.RULE),
                (Producer.REASON, Stage.SYNTAX),
                (Producer.PROJECTION, Stage.PROJECTION),
            }
        ),
    ),
    "PROJECTION_RESULT_LIMIT": (
        "semanticResult",
        frozenset({(Producer.PROJECTION, Stage.PROJECTION)}),
    ),
}
_UNSUPPORTED = {
    "UNSUPPORTED_LITERAL_DATATYPE": ("datatype", _GRAPH_INPUTS),
    "UNSUPPORTED_NONFINITE_LITERAL": ("literalValue", _GRAPH_INPUTS),
    "UNSUPPORTED_DATATYPE": ("datatype", frozenset({(Producer.SHACL, Stage.CONSTRAINT)})),
    "UNSUPPORTED_RDFS": ("rdfsConstruct", _GRAPH_INPUTS),
    "UNSUPPORTED_SHACL_PATH": ("shaclPath", frozenset({(Producer.SHACL, Stage.CONSTRAINT)})),
    "UNSUPPORTED_BLANK_NODE": ("rdfBlankNode", _GRAPH_INPUTS),
    "READ_ONLY_QUERY_REQUIRED": ("sparqlForm", frozenset({(Producer.QUERY, Stage.QUERY)})),
    "QUERY_GRAPH_UNSUPPORTED": ("sparqlForm", frozenset({(Producer.QUERY, Stage.QUERY)})),
    "UNSUPPORTED_OWL": ("owlExpression", _GRAPH_INPUTS),
    "UNSUPPORTED_SHACL": ("shaclAdvanced", _GRAPH_INPUTS),
    "UNSUPPORTED_FORMAT": (
        "rdfFormat",
        frozenset({(Producer.TURTLE, Stage.SYNTAX), (Producer.TURTLE, Stage.CONSTRAINT)}),
    ),
    "UNSUPPORTED_QUERY_FUNCTION": ("queryFunction", frozenset({(Producer.QUERY, Stage.QUERY)})),
    "UNSUPPORTED_QUERY_ORDER": ("queryOrder", frozenset({(Producer.QUERY, Stage.QUERY)})),
    "QUERY_SLICE_UNSUPPORTED": ("querySlice", frozenset({(Producer.QUERY, Stage.QUERY)})),
    "UNSUPPORTED_RULE_OUTPUT": ("ruleOutput", frozenset({(Producer.REASON, Stage.RULE)})),
}
_FIELD_REASONS = frozenset(
    {
        "INVALID_LITERAL_LEXICAL",
        "RDF_TERM_INVALID",
        "RDF_TYPE_OBJECT_INVALID",
        "RDFS_TERM_INVALID",
        "INVALID_UNICODE",
        "ABSOLUTE_IRI_REQUIRED",
    }
)
_FIXED_FIELDS = {
    "INVALID_ONTOLOGY_CATALOG": (frozenset({Producer.REASON}), frozenset({Stage.SYNTAX})),
    "INVALID_TURTLE": (frozenset({Producer.TURTLE}), frozenset({Stage.SYNTAX, Stage.CONSTRAINT})),
    "INVALID_QUERY": (frozenset({Producer.QUERY}), frozenset({Stage.QUERY})),
    "INVALID_RULE": (frozenset({Producer.REASON}), frozenset({Stage.RULE})),
    "UNBOUND_RULE_VARIABLE": (frozenset({Producer.REASON}), frozenset({Stage.RULE})),
    "RULE_COMPARISON_TYPE_MISMATCH": (frozenset({Producer.REASON}), frozenset({Stage.RULE})),
    "INVALID_SHAPE": (frozenset({Producer.SHACL}), frozenset({Stage.CONSTRAINT})),
    "INVALID_SHAPE_LIST": (frozenset({Producer.SHACL}), frozenset({Stage.CONSTRAINT})),
    "SHAPE_TARGET_CLASS_INVALID": (frozenset({Producer.SHACL}), frozenset({Stage.CONSTRAINT})),
    "SHAPE_DATATYPE_INVALID": (frozenset({Producer.SHACL}), frozenset({Stage.CONSTRAINT})),
    "SHAPE_PATH_INVALID": (frozenset({Producer.SHACL}), frozenset({Stage.CONSTRAINT})),
}
_REQUIRED = {
    "INTERNAL_ERROR": (None, frozenset()),
    "UNSUPPORTED_CAPABILITY": (None, frozenset()),
    "NETWORK_FORBIDDEN": (None, frozenset()),
    "INVALID_REQUEST": ("field", frozenset({"params"})),
    "SEMANTIC_INPUT_INVALID": ("field", frozenset({"syntax", "query", "rule", "constraint"})),
    "UNSUPPORTED_CONSTRUCT": ("construct", frozenset(v[0] for v in _UNSUPPORTED.values())),
    "RESOURCE_LIMIT": ("resource", frozenset({"semanticInput", "semanticResult", "semanticWork"})),
}


def _same_json(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return set(a) == set(b) and all(_same_json(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(_same_json(x, y) for x, y in zip(a, b, strict=True))
    return a == b


def _encoded(value):
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


class SemanticErrorAdapter:
    """Bind trusted canonical data once; adapt only finite trusted call context.

    Catalog configuration errors stop construction with a fixed local ValueError.
    A caller must not replace the catalog with user data or infer context from an
    exception message. Packaged catalog resource location remains I04's concern.
    """

    __slots__ = ("_specs", "_max_bytes")

    def __init__(self, *, error_catalog: dict, error_schema: dict):
        try:
            self._configure(error_catalog, error_schema)
        except Exception:
            raise ValueError("SEMANTIC_ERROR_CATALOG_INVALID") from None

    def _configure(self, catalog, schema):
        if type(catalog) is not dict or type(schema) is not dict:
            raise ValueError
        if type(catalog["schemaVersion"]) is not int or catalog["schemaVersion"] != 2:
            raise ValueError
        budget = catalog["maxEncodedBytes"]
        if type(budget) is not int or budget <= 0:
            raise ValueError
        error_node = schema["$defs"]["error"]
        if type(error_node) is not dict or set(error_node) != {"oneOf"}:
            raise ValueError
        branches = error_node["oneOf"]
        codes = catalog["codes"]
        if type(branches) is not list or type(codes) is not dict:
            raise ValueError
        dispatch = set()
        for branch in branches:
            code_node = branch["properties"]["code"]
            if type(code_node) is not dict or set(code_node) != {"const"}:
                raise ValueError
            code = code_node["const"]
            if type(code) is not str or code not in codes or code in dispatch:
                raise ValueError
            dispatch.add(code)
            item = codes[code]
            if type(item) is not dict or set(item) != {"messageKey", "retryable", "paramsSchema"}:
                raise ValueError
            if (
                type(item["messageKey"]) is not str
                or not item["messageKey"]
                or type(item["retryable"]) is not bool
            ):
                raise ValueError
            expected = {
                "type": "object",
                "properties": {
                    "code": {"const": code},
                    "messageKey": {"const": item["messageKey"]},
                    "retryable": {"const": item["retryable"]},
                    "params": item["paramsSchema"],
                },
                "required": ["code", "messageKey", "retryable", "params"],
                "additionalProperties": False,
            }
            if not _same_json(branch, expected):
                raise ValueError
        if dispatch != set(codes) or type(catalog["parameterMeanings"]) is not dict:
            raise ValueError
        specs = {}
        for code, (parameter, needed) in _REQUIRED.items():
            item = codes[code]
            key, retryable, params = item["messageKey"], item["retryable"], item["paramsSchema"]
            values = frozenset()
            properties = params["properties"]
            required = [] if parameter is None else [parameter]
            if type(params) is not dict or set(params) != {
                "type",
                "properties",
                "required",
                "additionalProperties",
            }:
                raise ValueError
            if (
                params["type"] != "object"
                or type(properties) is not dict
                or not _same_json(params["required"], required)
                or params["additionalProperties"] is not False
            ):
                raise ValueError
            if set(properties) != set(required):
                raise ValueError
            if parameter is not None:
                definition = properties[parameter]
                if type(definition) is not dict or set(definition) != {"enum"}:
                    raise ValueError
                items = definition["enum"]
                if type(items) is not list or not items or any(type(v) is not str for v in items):
                    raise ValueError
                values = frozenset(items)
                if len(values) != len(items) or not needed <= values:
                    raise ValueError
                meanings = catalog["parameterMeanings"][code]
                if (
                    type(meanings) is not dict
                    or set(meanings) != values
                    or any(type(v) is not str or not v for v in meanings.values())
                ):
                    raise ValueError
            spec = _Spec(key, retryable, parameter, values)
            for value in values or {None}:
                dto = {
                    "code": code,
                    "messageKey": key,
                    "params": {} if parameter is None else {parameter: value},
                    "retryable": retryable,
                }
                if _encoded(dto) > budget:
                    raise ValueError
            specs[code] = spec
        self._specs = MappingProxyType(specs)
        self._max_bytes = budget

    def _emit(self, code, value=None):
        spec = self._specs[code]
        if spec.parameter is None:
            params = {}
        elif value in spec.values:
            params = {spec.parameter: value}
        else:
            return self._emit("INTERNAL_ERROR")
        dto = {
            "code": code,
            "messageKey": spec.message_key,
            "params": params,
            "retryable": spec.retryable,
        }
        return dto if _encoded(dto) <= self._max_bytes else self._emit("INTERNAL_ERROR")

    def adapt(self, *, producer: Producer, reason: str, context: ErrorContext) -> dict:
        if (
            type(producer) is not Producer
            or type(reason) is not str
            or not 1 <= len(reason) <= 64
            or type(context) is not ErrorContext
            or type(context.stage) is not Stage
            or type(context.origin) is not Origin
            or context.origin is Origin.UNKNOWN
            or context.stage not in _STAGES[producer]
        ):
            return self._emit("INTERNAL_ERROR")
        if producer is Producer.PUBLIC_PARAMS:
            if reason in _PARAMS_REASONS and context.origin is Origin.VERIFIED_USER_INPUT:
                return self._emit("INVALID_REQUEST", "params")
            return self._emit("INTERNAL_ERROR")
        if reason in _RESOURCES:
            resource, branches = _RESOURCES[reason]
            if (producer, context.stage) in branches:
                return self._emit("RESOURCE_LIMIT", resource)
        if reason == "EXTERNAL_ACCESS_DENIED" and producer in _ENGINE_PRODUCERS:
            return self._emit("NETWORK_FORBIDDEN")
        if context.origin is not Origin.VERIFIED_USER_INPUT:
            return self._emit("INTERNAL_ERROR")
        if producer is Producer.REASON and context.stage is Stage.RULE:
            if reason == "RULE_INPUT_BUDGET":
                return self._emit("RESOURCE_LIMIT", "semanticInput")
            if reason == "RULE_POLICY_UNSUPPORTED":
                return self._emit("UNSUPPORTED_CAPABILITY")
        if reason in _UNSUPPORTED:
            construct, branches = _UNSUPPORTED[reason]
            if (producer, context.stage) in branches:
                return self._emit("UNSUPPORTED_CONSTRUCT", construct)
        if (
            reason == "INVALID_UNICODE"
            and producer is Producer.QUERY
            and context.stage is Stage.QUERY
        ):
            return self._emit("SEMANTIC_INPUT_INVALID", "query")
        if reason in _FIELD_REASONS and (producer, context.stage) in _GRAPH_INPUTS:
            return self._emit("SEMANTIC_INPUT_INVALID", context.stage.value)
        if reason in _FIXED_FIELDS:
            producers, phases = _FIXED_FIELDS[reason]
            if producer in producers and context.stage in phases:
                field = "syntax" if reason == "INVALID_TURTLE" else context.stage.value
                return self._emit("SEMANTIC_INPUT_INVALID", field)
        # Includes unknown reasons, deprecated ambiguous codes, selected-result
        # corruption and warnings. No value, exception or raw params are copied.
        return self._emit("INTERNAL_ERROR")
