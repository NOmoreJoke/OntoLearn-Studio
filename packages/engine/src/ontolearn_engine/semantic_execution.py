"""Immutable-snapshot semantic execution; Store alone authenticates result selection.

Request construction performs no RDF computation. Worker execution only consumes
memory data and injects the canonical public error documents at its boundary.
"""

import json
import re
from uuid import uuid4

from rdflib import Graph, Literal, URIRef, Variable
from rdflib.plugins.parsers.notation3 import SinkParser

from ontolearn_engine import semantic
from ontolearn_engine.semantic_error_adapter import (
    ErrorContext,
    Origin,
    Producer,
    SemanticErrorAdapter,
    Stage,
)
from ontolearn_engine.semantic_offline import SemanticError, offline
from ontolearn_engine.semantic_scopes import (
    _digest,
    _inputs,
    _LexicalSink,
    _source,
    project_validation_scope,
)

SEMANTIC_CAPABILITIES = frozenset({"query.execute", "reasoning.execute", "validation.execute"})
MAX_OUTPUT_BYTES = 8_388_608
MAX_ROWS = 10_000
MAX_CELL = 8192


class SemanticRequestFault(ValueError):
    """Fixed local classification; never contains source text or an exception."""

    def __init__(self, reason, producer, stage, origin):
        self.reason = reason
        self.producer = producer
        self.context = ErrorContext(stage, origin)
        super().__init__("SEMANTIC_REQUEST_INVALID")


class SemanticExecutionFault(ValueError):
    def __init__(self, error):
        self.error = error
        super().__init__("SEMANTIC_EXECUTION_FAILED")


def _fail(reason="REQUEST_INVALID", *, public=False):
    raise SemanticRequestFault(
        "SCOPE_SELECTION_TYPE_INVALID" if public else reason,
        Producer.PUBLIC_PARAMS if public else Producer.PROJECTION,
        Stage.PARAMS if public else Stage.PROJECTION,
        Origin.VERIFIED_USER_INPUT if public else Origin.TRUSTED_INTERNAL,
    )


def _json(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def _copy(value):
    return json.loads(_json(value))


def _definitions(snapshot):
    definitions = {}
    state = snapshot.get("state")
    if type(state) is not dict or type(state.get("facts")) is not list:
        _fail()
    if type(state.get("definitions")) is not list:
        _fail()
    for record in state["definitions"]:
        if type(record) is not dict or set(record) != {"layer", "id", "payload"}:
            _fail()
        layer, identity, encoded = record["layer"], record["id"], record["payload"]
        if not all(type(x) is str and x for x in (layer, identity, encoded)):
            _fail()
        key = (layer, identity)
        if key in definitions:
            _fail()
        value = json.loads(encoded)
        definitions[key] = value
    return definitions


def _shape(value, required, optional=()):
    if type(value) is not dict or not set(required) <= set(value) <= set(required) | set(optional):
        _fail()
    if "references" in value and type(value["references"]) is not list:
        _fail()


def _request(snapshot, capability, input_, parameters, selected):
    if capability not in SEMANTIC_CAPABILITIES:
        _fail(public=True)
    if type(parameters) is not dict or set(parameters) - {"inputSelection"}:
        _fail(public=True)
    selection = parameters.get("inputSelection", "current")
    if type(selection) is not str or selection not in {"current", "historical"}:
        _fail(public=True)
    if type(snapshot) is not dict or type(input_) is not dict:
        _fail()
    if _digest(snapshot) != input_.get("inputSnapshotId"):
        _fail()
    scope, ids = input_.get("scope"), input_.get("derivedResultIds")
    if scope not in {"asserted", "asserted+derived"} or type(ids) is not list:
        _fail(public=True)
    if capability == "reasoning.execute" and scope != "asserted":
        _fail(public=True)
    if scope == "asserted":
        if ids or selected is not None:
            _fail(public=True)
    else:
        if (
            len(ids) != 1
            or type(selected) is not dict
            or set(selected) != {"metadata", "payload"}
            or type(selected["metadata"]) is not dict
            or selected["metadata"].get("resultId") != ids[0]
            or selected["metadata"].get("kind") != "reasoning"
            or selected["metadata"].get("inputSnapshotId") != input_["inputSnapshotId"]
            or type(selected["payload"]) is not dict
            or selected["payload"].get("kind") != "reasoning"
            or selected["payload"].get("inputSnapshotId") != input_["inputSnapshotId"]
        ):
            _fail()
    definitions = _definitions(snapshot)
    for (layer, _identity), value in definitions.items():
        if layer == "ontology":
            _shape(value, {"triples"}, {"singleValuedPredicates", "references"})
            if type(value["triples"]) is not list:
                _fail()
            for triple in value["triples"]:
                _shape(triple, {"subject", "predicate", "object"})
                if any(type(term) is not str for term in triple.values()):
                    _fail()
        if layer == "rule" and (capability == "reasoning.execute" or scope == "asserted+derived"):
            _shape(value, {"enabled", "when", "then"}, {"references"})
            if type(value["enabled"]) is not bool or type(value["when"]) is not list:
                _fail()
            for triple in [*value["when"], value["then"]]:
                if type(triple) is not list or len(triple) != 3:
                    _fail()
                if any(type(term) is not str for term in triple):
                    _fail()
    layer = {"query.execute": "query", "validation.execute": "constraint"}.get(capability)
    if layer:
        definition = definitions.get((layer, input_.get("definitionId")))
        if layer == "query":
            _shape(definition, {"text"}, {"references"})
            if type(definition["text"]) is not str:
                _fail()
        else:
            _shape(definition, {"turtle", "enabled"}, {"references"})
            if type(definition["turtle"]) is not str or type(definition["enabled"]) is not bool:
                _fail()
    return _copy(
        {
            "snapshot": snapshot,
            "capability": capability,
            "input": input_,
            "parameters": parameters,
            "selected": selected,
        }
    )


def build_request(
    snapshot,
    capability,
    input_,
    parameters,
    selected=None,
    *,
    error_catalog=None,
    error_schema=None,
):
    """Copy Store-authenticated immutable inputs; no graph parsing or evaluation."""
    adapter = (
        SemanticErrorAdapter(error_catalog=error_catalog, error_schema=error_schema)
        if error_catalog is not None or error_schema is not None
        else None
    )
    try:
        return _request(snapshot, capability, input_, parameters, selected)
    except SemanticRequestFault as error:
        if adapter is None:
            raise
        raise SemanticExecutionFault(
            adapter.adapt(producer=error.producer, reason=error.reason, context=error.context)
        ) from None
    except Exception:
        if adapter is None:
            _fail()
        raise SemanticExecutionFault(
            adapter.adapt(
                producer=Producer.PROJECTION,
                reason="REQUEST_INVALID",
                context=ErrorContext(Stage.PROJECTION, Origin.TRUSTED_INTERNAL),
            )
        ) from None


def _term(text):
    if type(text) is not str or not (text.startswith("<") or text.startswith('"')):
        raise SemanticError("RDF_TERM_INVALID")
    semantic._text(text)
    graph = Graph()
    try:
        SinkParser(_LexicalSink(graph), baseURI="urn:ontolearn:term:", turtle=True).loadBuf(
            "<urn:ontolearn:subject> <urn:ontolearn:predicate> " + text + " ."
        )
        if len(graph) != 1:
            raise ValueError
        s, p, value = next(iter(graph))
        if s != URIRef("urn:ontolearn:subject") or p != URIRef("urn:ontolearn:predicate"):
            raise ValueError
        if not isinstance(value, URIRef | Literal) or value.n3() != text:
            raise ValueError
    except Exception:
        raise SemanticError("RDF_TERM_INVALID") from None
    return value


def _iri(text):
    if (
        type(text) is not str
        or ":" not in text
        or any(c.isspace() or c in '<>"{}|^`\\' for c in text)
    ):
        raise SemanticError("ABSOLUTE_IRI_REQUIRED")
    return URIRef(text)


def _graph(records):
    graph = Graph()
    for record in records:
        if type(record) is not dict or not {"subject", "predicate", "object"} <= set(record):
            _fail()
        if record.get("object") is None:  # Managed tombstones are not assertions.
            continue
        graph.add((_iri(record["subject"]), _iri(record["predicate"]), _term(record["object"])))
        if len(graph) > semantic.MAX_TRIPLES:
            raise SemanticError("GRAPH_INPUT_LIMIT")
    semantic._terms(graph)
    return graph


def _rules(definitions):
    def pattern(values):
        return tuple(
            Variable(value[1:])
            if re.fullmatch(r"\?[A-Za-z_][A-Za-z_0-9]*", value)
            else _term(value)
            for value in values
        )

    output = tuple(
        semantic.Rule(identity, tuple(pattern(p) for p in value["when"]), pattern(value["then"]))
        for (layer, identity), value in sorted(definitions.items())
        if layer == "rule" and value["enabled"]
    )
    for rule in output:
        semantic._rule(rule)
    return output


def _rows(payload):
    """Lossless, stable JSON-pointer display, including every evidence leaf."""
    rows = []

    def add(cells):
        if len(rows) >= MAX_ROWS or any(type(c) is str and len(c) > MAX_CELL for c in cells):
            raise SemanticError("PROJECTION_RESULT_LIMIT")
        rows.append({"rowId": str(uuid4()), "ordinal": len(rows), "cells": cells})

    add(["columns", "path", "value", "part", "parts"])

    def walk(value, path):
        if type(value) is dict and value:
            for key in sorted(value):
                walk(value[key], path + "/" + key.replace("~", "~0").replace("/", "~1"))
        elif type(value) is list and value:
            for index, child in enumerate(value):
                walk(child, path + "/" + str(index))
        else:
            encoded = _json(value)
            pieces = [encoded[i : i + MAX_CELL] for i in range(0, len(encoded), MAX_CELL)] or [""]
            for index, piece in enumerate(pieces):
                add([path, piece, index + 1, len(pieces)])

    walk(payload, "")
    if len(_json({"payload": payload, "rows": rows}).encode("utf-8")) > MAX_OUTPUT_BYTES:
        raise SemanticError("PROJECTION_RESULT_LIMIT")
    return rows


def execute_request(request, *, error_catalog, error_schema):
    """Execute real pinned libraries and return only canonical safe failures."""
    adapter = SemanticErrorAdapter(error_catalog=error_catalog, error_schema=error_schema)
    producer, stage, origin = Producer.PROJECTION, Stage.PROJECTION, Origin.TRUSTED_INTERNAL
    try:
        if type(request) is not dict or set(request) != {
            "snapshot",
            "capability",
            "input",
            "parameters",
            "selected",
        }:
            _fail()
        request = _request(
            request["snapshot"],
            request["capability"],
            request["input"],
            request["parameters"],
            request["selected"],
        )
        with offline():
            snapshot, input_ = request["snapshot"], request["input"]
            capability = request["capability"]
            definitions = _definitions(snapshot)
            producer, stage = Producer.REASON, Stage.SYNTAX
            facts = _graph(snapshot["state"]["facts"])
            ontology = _graph(
                [
                    t
                    for (layer, _), value in sorted(definitions.items())
                    if layer == "ontology"
                    for t in value["triples"]
                ]
            )
            _inputs(facts, ontology, False, ())
            producer, stage, origin = Producer.REASON, Stage.RULE, Origin.VERIFIED_USER_INPUT
            rules = (
                _rules(definitions)
                if (capability == "reasoning.execute" or input_["scope"] == "asserted+derived")
                else ()
            )
            common = {
                "inputSnapshotId": input_["inputSnapshotId"],
                "inputProjectRevision": snapshot["projectRevision"],
                "executionSemanticsVersion": semantic.SEMANTICS_VERSION,
                "scope": input_["scope"],
                "definitionId": input_["definitionId"],
                "inputSelection": request["parameters"].get("inputSelection", "current"),
                "selectedResultIds": list(input_["derivedResultIds"]),
            }
            if capability == "reasoning.execute":
                result = semantic.reason(facts + ontology, rules)
                payload = {
                    **common,
                    "kind": "reasoning",
                    "reasoning": result,
                    "source": _source(facts, ontology, rules),
                    "assertedFacts": sorted(semantic._key(t) for t in facts),
                    "ontology": sorted(semantic._key(t) for t in ontology),
                }
            else:
                producer, stage, origin = (
                    Producer.PROJECTION,
                    Stage.PROJECTION,
                    Origin.TRUSTED_INTERNAL,
                )
                selected = request["selected"]
                view = project_validation_scope(
                    facts,
                    ontology,
                    include_derived=input_["scope"] == "asserted+derived",
                    reasoning_result=selected["payload"]["reasoning"] if selected else None,
                    reasoning_source=selected["payload"]["source"] if selected else None,
                    rules=rules,
                )
                if capability == "query.execute":
                    producer, stage, origin = (
                        Producer.QUERY,
                        Stage.QUERY,
                        Origin.VERIFIED_USER_INPUT,
                    )
                    definition = definitions[("query", input_["definitionId"])]
                    payload = {
                        **common,
                        "kind": "query",
                        "query": semantic.query(view.facts, definition["text"]),
                        "provenance": view.provenance,
                        "queryText": definition["text"],
                    }
                else:
                    definition = definitions[("constraint", input_["definitionId"])]
                    producer, stage, origin = (
                        Producer.SHACL,
                        Stage.CONSTRAINT,
                        Origin.VERIFIED_USER_INPUT,
                    )
                    if not definition["enabled"]:
                        raise SemanticError("INVALID_SHAPE")
                    producer = Producer.TURTLE
                    shapes = semantic.parse_turtle(definition["turtle"], shapes=True)
                    producer = Producer.SHACL
                    payload = {
                        **common,
                        "kind": "validation",
                        "report": semantic.check_shapes(view.facts, shapes),
                        "constraintsHash": _digest(definition),
                        "constraintsVersion": snapshot["dependencyVector"].get(
                            "constraint:" + input_["definitionId"], 0
                        ),
                        "provenance": view.provenance,
                        "projection": {
                            "scope": input_["scope"],
                            "factViewSha256": view.provenance["factViewSha256"],
                            "ontologyViewSha256": view.provenance["ontologyViewSha256"],
                            "selectedResultIds": list(input_["derivedResultIds"]),
                        },
                    }
            producer, stage, origin = Producer.PROJECTION, Stage.PROJECTION, Origin.TRUSTED_INTERNAL
            payload = _copy(payload)
            return {"payload": payload, "rows": _rows(payload)}
    except SemanticRequestFault as error:
        raise SemanticExecutionFault(
            adapter.adapt(
                producer=error.producer,
                reason=error.reason,
                context=error.context,
            )
        ) from None
    except SemanticError as error:
        raise SemanticExecutionFault(
            adapter.adapt(
                producer=producer,
                reason=error.code,
                context=ErrorContext(stage, origin),
            )
        ) from None
    except Exception:
        raise SemanticExecutionFault(
            adapter.adapt(
                producer=Producer.PROJECTION,
                reason="EXECUTION_FAILED",
                context=ErrorContext(Stage.PROJECTION, Origin.TRUSTED_INTERNAL),
            )
        ) from None
