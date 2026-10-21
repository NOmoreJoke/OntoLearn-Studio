"""Immutable-snapshot semantic execution; Store alone authenticates result selection.

Request construction performs no RDF computation. Worker execution only consumes
memory data and injects the canonical public error documents at its boundary.
"""

import hashlib
import json
import re
from uuid import uuid4

from ontolearn_engine.semantic_error_adapter import (
    ErrorContext,
    Origin,
    Producer,
    SemanticErrorAdapter,
    Stage,
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


class ProfileExecutionFault(SemanticExecutionFault):
    """Private P1 diagnostic, never appended to the public four-field error."""

    def __init__(self, error, diagnostic):
        super().__init__(error)
        self.diagnostic = diagnostic


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


def _digest(value):
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


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
    from rdflib import Graph, Literal, URIRef
    from rdflib.plugins.parsers.notation3 import SinkParser

    from ontolearn_engine import semantic
    from ontolearn_engine.semantic_offline import SemanticError
    from ontolearn_engine.semantic_turtle import LexicalSink, canonical_string

    if type(text) is not str or not (text.startswith("<") or text.startswith('"')):
        raise SemanticError("RDF_TERM_INVALID")
    semantic._text(text)
    graph = Graph()
    try:
        # Validate the exact original N3 first. Abstract string normalization
        # must not reject a previously legal explicit xsd:string spelling.
        SinkParser(
            LexicalSink(graph, canonical_strings=False),
            baseURI="urn:ontolearn:term:",
            turtle=True,
        ).loadBuf("<urn:ontolearn:subject> <urn:ontolearn:predicate> " + text + " .")
        if len(graph) != 1:
            raise ValueError
        s, p, value = next(iter(graph))
        if s != URIRef("urn:ontolearn:subject") or p != URIRef("urn:ontolearn:predicate"):
            raise ValueError
        if not isinstance(value, URIRef | Literal) or value.n3() != text:
            raise ValueError
    except Exception:
        raise SemanticError("RDF_TERM_INVALID") from None
    return canonical_string(value)


def _iri(text):
    from rdflib import URIRef

    from ontolearn_engine.semantic_offline import SemanticError

    if (
        type(text) is not str
        or ":" not in text
        or any(c.isspace() or c in '<>"{}|^`\\' for c in text)
    ):
        raise SemanticError("ABSOLUTE_IRI_REQUIRED")
    return URIRef(text)


def _graph(records):
    from rdflib import Graph

    from ontolearn_engine import semantic
    from ontolearn_engine.semantic_offline import SemanticError

    graph = Graph()
    for record in records:
        if type(record) is not dict or not {"subject", "predicate", "object"} <= set(record):
            _fail()
        if record.get("object") is None:  # Managed tombstones are not assertions.
            continue
        graph.add((_iri(record["subject"]), _iri(record["predicate"]), _term(record["object"])))
        if len(graph) > semantic.MAX_TRIPLES:
            raise SemanticError("GRAPH_INPUT_LIMIT")
    return graph


def _rules(definitions):
    from rdflib import Variable

    from ontolearn_engine import semantic

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
    from ontolearn_engine.semantic_offline import SemanticError

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
    from ontolearn_engine.semantic_offline import SemanticError, offline

    adapter = SemanticErrorAdapter(error_catalog=error_catalog, error_schema=error_schema)
    producer, stage, origin = Producer.PROJECTION, Stage.PROJECTION, Origin.TRUSTED_INTERNAL
    try:
        from ontolearn_engine import semantic
        from ontolearn_engine.semantic_scopes import (
            _inputs,
            _source,
            project_validation_scope,
        )

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
            # These records and term encodings came from a verified immutable
            # Store snapshot. Corrupt structure stays an internal failure. The
            # actual bounded Turtle-term decoder owns lexical byte limits.
            producer, stage = Producer.TURTLE, Stage.SYNTAX
            # Rule terms use the same bounded lexical decoder. Check that
            # branch here too, before switching to actual rule evaluation.
            if capability == "reasoning.execute" or input_["scope"] == "asserted+derived":
                for (layer, _), definition in definitions.items():
                    if layer == "rule" and definition["enabled"]:
                        for triple in [*definition["when"], definition["then"]]:
                            for value in triple:
                                semantic._text(value)
            facts = _graph(snapshot["state"]["facts"])
            ontology = _graph(
                [
                    t
                    for (layer, _), value in sorted(definitions.items())
                    if layer == "ontology"
                    for t in value["triples"]
                ]
            )
            # A valid saved definition can still contain a supported-standard
            # construct outside this candidate's finite semantics. Its content
            # is user input; it must not be mislabeled as an engine defect.
            producer, stage, origin = Producer.REASON, Stage.SYNTAX, Origin.VERIFIED_USER_INPUT
            semantic._terms(facts)
            semantic._terms(ontology)
            origin = Origin.TRUSTED_INTERNAL  # Trusted layer construction follows.
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


class _ProfileProjection:
    """One bounded JSON projection, distinct from T05's private typed encoding."""

    def __init__(self):
        self.nodes = 0
        self.bytes = 0

    def charge(self, nodes=1, size=0):
        from ontolearn_engine.semantic_offline import SemanticError

        if self.nodes + nodes > 1_000_000 or self.bytes + size > MAX_OUTPUT_BYTES:
            raise SemanticError("PROJECTION_RESULT_LIMIT")
        self.nodes += nodes
        self.bytes += size

    def value(self, value, depth=0):
        from dataclasses import fields

        import ontolearn_engine.quality.rule_calendar as rule_calendar
        import ontolearn_engine.quality.rule_firing as rule_firing
        import ontolearn_engine.quality.rule_numbers as rule_numbers
        import ontolearn_engine.quality.rule_profile as rule_profile
        from ontolearn_engine.quality.rule_terms import ProfileValue
        from ontolearn_engine.semantic_offline import SemanticError

        if depth > 32:
            raise SemanticError("PROJECTION_RESULT_LIMIT")
        self.charge()
        kind = type(value)
        if value is None or kind is bool:
            self.charge(size=5)
            return value
        if kind is int:
            if value.bit_length() > 32768:
                raise SemanticError("PROJECTION_RESULT_LIMIT")
            self.charge(size=max(24, value.bit_length() // 4 + 16))
            # All integers have an explicit lossless representation, including
            # calendar days and rational fields outside a host JSON number range.
            return {"integerHex": hex(value)}
        if kind is str:
            if len(value) > MAX_OUTPUT_BYTES // 6:
                raise SemanticError("PROJECTION_RESULT_LIMIT")
            self.charge(size=6 * len(value) + 2)
            value.encode("utf-8", errors="strict")
            return value
        if kind is bytes:
            self.charge(size=2 * len(value) + 48)
            return {"encoding": "hex", "bytes": value.hex()}
        if kind in (tuple, list):
            self.charge(nodes=len(value), size=2 * len(value) + 2)
            return [self.value(item, depth + 1) for item in value]
        if kind is dict:
            self.charge(nodes=len(value), size=4 * len(value) + 2)
            if any(type(key) is not str for key in value):
                raise SemanticError("PROFILE_PROJECTION_INVALID")
            return {
                self.value(key, depth + 1): self.value(item, depth + 1)
                for key, item in value.items()
            }
        approved = (
            rule_profile.TermInput,
            rule_profile.SourceRecord,
            rule_profile.InputLocation,
            rule_profile.ProfileLimits,
            rule_firing.Variable,
            rule_firing.Triple,
            rule_firing.Comparison,
            rule_firing.RuleSpec,
            rule_firing.Catalog,
            rule_firing.BindingMatch,
            rule_firing.ComparisonEvidence,
            rule_firing.HeadEvidence,
            rule_firing.PreparedFiring,
            rule_firing.PreparedFiringBatch,
            rule_numbers.Number,
            rule_calendar.Calendar,
            ProfileValue,
        )
        if kind not in approved:
            raise SemanticError("PROFILE_PROJECTION_INVALID")
        return {
            "recordType": kind.__name__,
            **{
                field.name: self.value(getattr(value, field.name), depth + 1)
                for field in fields(value)
            },
        }


def _profile_json_bytes(value):
    """Stream already bounded safe primitives; precharge before retaining chunks."""
    from ontolearn_engine.semantic_offline import SemanticError

    output = bytearray()
    encoder = json.JSONEncoder(
        ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    for chunk in encoder.iterencode(value):
        data = chunk.encode("utf-8")
        if len(output) + len(data) > MAX_OUTPUT_BYTES:
            raise SemanticError("PROJECTION_RESULT_LIMIT")
        output.extend(data)
    return bytes(output)


def _profile_diagnostic(reason, classification, location=None, rule_id=None):
    """Only safe fields from the actual private execution boundary."""
    return {
        "reason": reason,
        "classification": classification,
        "ruleId": rule_id,
        "location": None
        if location is None
        else {
            "section": location.section,
            "index": location.index,
            "side": location.side,
            "span": location.span,
        },
    }


def _execute_profile(
    text,
    rules=(),
    *,
    disabled_rule_ids=(),
    source_reference=None,
    source_revision=None,
    error_catalog,
    error_schema,
    records=None,
    _capture=None,
):
    """Private P1 text caller; no public snapshot DTO, producer or Store authority.

    The actual parser binds lexical/source provenance. Rule records are explicit
    user syntax for this local computation, not authenticated saved definitions.
    T01 must supply the formal domain boundary before any worker can expose it.
    """
    from ontolearn_engine import semantic
    from ontolearn_engine.quality.rule_profile import PROFILE, ProfileFailure, SourceRecord
    from ontolearn_engine.resources import semantic_identity
    from ontolearn_engine.semantic_offline import SemanticError, offline
    from ontolearn_engine.semantic_profile_directsteps import DirectStepsFailure
    from ontolearn_engine.semantic_profile_input import MaterialFailure
    from ontolearn_engine.semantic_turtle import (
        _disabled_ids,
        bind_profile_disabled_rules,
        parse_profile_graph,
        profile_graph_from_records,
    )

    adapter = SemanticErrorAdapter(error_catalog=error_catalog, error_schema=error_schema)
    producer, stage = Producer.TURTLE, Stage.SYNTAX
    origin = Origin.VERIFIED_USER_INPUT
    try:
        if records is None:
            semantic._text(text)
        for item in (source_reference, source_revision):
            if item is not None:
                if type(item) is not str:
                    raise SemanticError("TEXT_TYPE_INVALID")
                if len(item) > 16384:
                    raise SemanticError("TEXT_INPUT_LIMIT")
                try:
                    encoded_item = item.encode("utf-8")
                except UnicodeEncodeError:
                    raise SemanticError("INVALID_UNICODE") from None
                if len(encoded_item) > 16384:
                    raise SemanticError("TEXT_INPUT_LIMIT")
        with offline():
            producer, stage = Producer.REASON, Stage.RULE
            disabled_rule_ids = _disabled_ids(disabled_rule_ids)
            producer, stage = Producer.TURTLE, Stage.SYNTAX
            if records is None:
                original_bytes = text.encode("utf-8")
                source = SourceRecord(
                    source_reference,
                    hashlib.sha256(original_bytes).hexdigest(),
                    source_revision,
                    text if len(original_bytes) <= 65536 else None,
                )
                graph, context = parse_profile_graph(
                    text, base_uri="urn:ontolearn:i05:", source=source
                )
                input_domain = "utf8-turtle"
            else:
                graph, context = profile_graph_from_records(
                    records, disabled_rule_ids=disabled_rule_ids
                )
                try:
                    original_bytes = _profile_json_bytes(_ProfileProjection().value(records))
                except SemanticError as error:
                    if error.code == "PROJECTION_RESULT_LIMIT":
                        raise SemanticError("GRAPH_INPUT_LIMIT") from None
                    raise
                source = tuple(term.source for triple in records for term in triple)
                input_domain = "profile-structured-records-json/1"
            producer, stage = Producer.REASON, Stage.RULE
            if records is None and disabled_rule_ids:
                context = bind_profile_disabled_rules(context, disabled_rule_ids)
            if _capture is None:
                result = semantic.reason(graph, rules, profile=PROFILE, term_context=context)
            else:
                from ontolearn_engine.semantic_profile_production import _ProductionCapture

                if type(_capture) is not _ProductionCapture:
                    raise MaterialFailure()
                _capture.before_input(original_bytes, source, input_domain)
                result = semantic._reason_profile_production(
                    graph, rules, term_context=context, capture=_capture
                )
        producer, stage, origin = Producer.PROJECTION, Stage.PROJECTION, Origin.TRUSTED_INTERNAL
        if _capture is not None:
            _capture.before_projection(result, source, tuple(rules))
        projection = _ProfileProjection()
        safe_result = projection.value(result)
        if _capture is not None:
            _capture.projected(safe_result)
        source_encoded = _profile_json_bytes(projection.value(source))
        defs_encoded = _profile_json_bytes(projection.value(tuple(rules)))
        explanation = _capture is not None and _capture.direct_ledger is not None
        payload = {
            "format": "i05-reasoning-result/3" if explanation else "i05-reasoning-result/2",
            "implementation": semantic_identity(profile=True, explanation=explanation),
            "reasoning": safe_result,
            "inputDigest": hashlib.sha256(original_bytes).hexdigest(),
            "inputDigestDomain": input_domain,
            "sourceDigest": hashlib.sha256(source_encoded).hexdigest(),
            "definitionsDigest": hashlib.sha256(defs_encoded).hexdigest(),
        }
        encoded = _profile_json_bytes(payload)
        if _capture is not None:
            _capture.before_rows()
        # A single payload stream sliced by characters, with no missing tail.
        # Rows are a private transport projection, never T05 proof/basis IDs.
        serialized = encoded.decode("utf-8")
        count = (len(serialized) + MAX_CELL - 1) // MAX_CELL
        if count > MAX_ROWS:
            raise SemanticError("PROJECTION_RESULT_LIMIT")
        rows = [
            [serialized[index : index + MAX_CELL]] for index in range(0, len(serialized), MAX_CELL)
        ]
        rows_encoded = _profile_json_bytes(rows)
        if len(encoded) + len(rows_encoded) > MAX_OUTPUT_BYTES:
            raise SemanticError("PROJECTION_RESULT_LIMIT")
        wire = {
            "payload": payload,
            "rows": rows,
            "jsonPayloadDigest": hashlib.sha256(encoded).hexdigest(),
            "rowsDigest": hashlib.sha256(rows_encoded).hexdigest(),
        }
        if _capture is not None:
            _capture.completed(result, encoded, rows_encoded, source_encoded, defs_encoded, wire)
        return wire
    except (MaterialFailure, DirectStepsFailure):
        raise
    except semantic.ProfileReasonError as error:
        actual_stage = Stage.RULE if error.context in {"rule", "closure"} else Stage.SYNTAX
        actual_origin = (
            Origin.TRUSTED_INTERNAL
            if error.classification == "internal"
            else Origin.VERIFIED_USER_INPUT
        )
        reason = error.code
        if actual_stage is Stage.SYNTAX and reason == "RULE_INPUT_BUDGET":
            reason = "GRAPH_INPUT_LIMIT"
        raise ProfileExecutionFault(
            adapter.adapt(
                producer=Producer.REASON,
                reason=reason,
                context=ErrorContext(actual_stage, actual_origin),
            ),
            _profile_diagnostic(error.code, error.classification, error.location, error.rule_id),
        ) from None
    except ProfileFailure as error:
        # ProfileFailure cannot confer user provenance on an internal failure.
        actual_origin = origin if error.classification != "internal" else Origin.TRUSTED_INTERNAL
        reason = error.reason
        if stage is Stage.SYNTAX and reason == "RULE_INPUT_BUDGET":
            reason = "GRAPH_INPUT_LIMIT"
        raise ProfileExecutionFault(
            adapter.adapt(
                producer=producer,
                reason=reason,
                context=ErrorContext(stage, actual_origin),
            ),
            _profile_diagnostic(error.reason, error.classification, error.location),
        ) from None
    except SemanticError as error:
        raise ProfileExecutionFault(
            adapter.adapt(
                producer=producer, reason=error.code, context=ErrorContext(stage, origin)
            ),
            _profile_diagnostic(
                error.code,
                "resource"
                if error.code
                in {"TEXT_INPUT_LIMIT", "GRAPH_INPUT_LIMIT", "PROJECTION_RESULT_LIMIT"}
                else "input"
                if origin is Origin.VERIFIED_USER_INPUT
                else "internal",
            ),
        ) from None
    except Exception:
        raise ProfileExecutionFault(
            adapter.adapt(
                producer=Producer.PROJECTION,
                reason="PROFILE_EXECUTION_FAILED",
                context=ErrorContext(Stage.PROJECTION, Origin.TRUSTED_INTERNAL),
            ),
            _profile_diagnostic("INTERNAL_ERROR", "internal"),
        ) from None


def execute_profile(
    text,
    rules=(),
    *,
    disabled_rule_ids=(),
    source_reference=None,
    source_revision=None,
    error_catalog,
    error_schema,
):
    """Private actual-text caller; no public producer or persisted selection."""
    return _execute_profile(
        text,
        rules,
        disabled_rule_ids=disabled_rule_ids,
        source_reference=source_reference,
        source_revision=source_revision,
        error_catalog=error_catalog,
        error_schema=error_schema,
    )


def execute_profile_records(
    records, rules=(), *, disabled_rule_ids=(), error_catalog, error_schema
):
    """Private structured input caller; preserve supplied original N3 sources.

    TermInput records are raw input, not signed values or producer authority.
    The one lexical adapter issues the graph context, and the same reason then
    validates actual graph terms and computes all real matches.
    """
    return _execute_profile(
        None,
        rules,
        records=records,
        disabled_rule_ids=disabled_rule_ids,
        error_catalog=error_catalog,
        error_schema=error_schema,
    )


def _execute_profile_production(material, capture, *, error_catalog, error_schema):
    """Same original execution body; no second parser, matcher or projection."""
    from ontolearn_engine.semantic_profile_input import ProfileMaterial
    from ontolearn_engine.semantic_profile_production import _ProductionCapture

    if type(material) is not ProfileMaterial or type(capture) is not _ProductionCapture:
        raise ValueError("PROFILE_PRODUCTION_INTERNAL")
    return _execute_profile(
        material.text,
        material.rules,
        records=material.records,
        disabled_rule_ids=material.disabled_rule_ids,
        source_reference=material.source.reference if material.records is None else None,
        source_revision=material.source.revision if material.records is None else None,
        error_catalog=error_catalog,
        error_schema=error_schema,
        _capture=capture,
    )
