"""FR-203 import-side Turtle pre-check: whole-batch accept or explicit reject.

Parsing is offline and lexical; every construct is audited against the frozen
Appendix C P0 vocabulary before anything is proposed. A passing check returns a
pure ChangeSet plan (ontology/constraint definitions plus content-derived
manual facts) and never writes the Store; any unsupported construct rejects the
entire document with explicit reasons - partial imports cannot happen.
"""

from rdflib import RDF, SH, XSD, BNode, Literal, URIRef

from ontolearn_engine.project.ontology_turtle import (
    MAX_PLAN_ITEMS,
    MAX_REASONS,
    NAME_PATTERN,
    NODE_SHAPE_PREDICATES,
    PROPERTY_SHAPE_PREDICATES,
    PROPERTY_SHAPE_SUFFIX,
    SH_DEACTIVATED,
    SH_IN,
    SHAPE_PREFIX,
    SUPPORTED_DATATYPES,
    TEMPLATE_PATH_PREDICATES,
    build_plan,
    canonical_object,
    check_content_triples,
    fault,
    literal_collision_reasons,
    literal_datatype,
    reason,
    resolve_active,
)
from ontolearn_engine.storage import digest

METHODS = frozenset({"project.ontology.import.check"})
TURTLE_FORMAT = "turtle"
MAX_LITERAL_CHARS = 16384
LIST_PREDICATES = frozenset({str(RDF.first), str(RDF.rest)})
XSD_INTEGER = "http://www.w3.org/2001/XMLSchema#integer"
NUMERIC_BOUND_DATATYPES = frozenset(
    {
        str(XSD.integer),
        str(XSD.decimal),
        str(XSD.int),
        str(XSD.nonNegativeInteger),
        str(XSD.double),
        str(XSD.float),
    }
)


def _invalid(code, field, detail):
    return {"status": "invalid", "reasons": [{"code": code, "field": field, "detail": detail}]}


def _reject(reasons):
    return {"status": "rejected", "reasons": reasons[:MAX_REASONS]}


def _parse(text, base):
    """Offline lexical parse plus per-IRI safety audit; failures are INVALID_TURTLE."""
    from ontolearn_engine.semantic_offline import SemanticError, offline
    from ontolearn_engine.semantic_turtle import parse_graph, validate_profile_iri

    def safe_iri(value):
        validate_profile_iri(str(value))

    with offline():
        try:
            validate_profile_iri(base)
            graph = parse_graph(text, base_uri=base)
            for subject, predicate, obj in graph:
                for term in (subject, predicate, obj):
                    if isinstance(term, URIRef):
                        safe_iri(term)
                if isinstance(obj, Literal):
                    if len(str(obj)) > MAX_LITERAL_CHARS:
                        raise SemanticError("TEXT_INPUT_LIMIT")
                    if obj.datatype is not None:
                        safe_iri(obj.datatype)
            return graph
        except SemanticError as error:
            raise ValueError(str(error.code)) from error
        except Exception as error:  # any parser defect is a definite syntax rejection
            raise ValueError("INVALID_TURTLE") from error


def _single_object(graph, subject, predicate):
    values = list(graph.objects(subject, predicate))
    return values[0] if len(values) == 1 else None


def _read_list(graph, head):
    """Traverse one rdf:first/rdf:rest chain; returns (values, nodes) or None."""
    values, nodes = [], set()
    current = head
    steps = 0
    while current != RDF.nil:
        if not isinstance(current, BNode) or current in nodes or steps > MAX_PLAN_ITEMS:
            return None
        nodes.add(current)
        if {str(p) for p in graph.predicates(current, None)} != LIST_PREDICATES:
            return None
        first = _single_object(graph, current, RDF.first)
        rest = _single_object(graph, current, RDF.rest)
        if first is None or rest is None:
            return None
        values.append(first)
        current = rest
        steps += 1
    if not values:
        return None
    return values, nodes


def _integer_literal(value):
    if (
        isinstance(value, Literal)
        and value.datatype is not None
        and str(value.datatype) == XSD_INTEGER
    ):
        try:
            return int(str(value))
        except ValueError:
            return None
    return None


def _allowed_value_n3(link, values):
    """Validate one sh:in list element; never raises, never calls the
    normalizing term gate on an unsupported element (B03).

    Returns (n3_texts, reason) - a reason means the whole document is
    rejected and nothing may be written.
    """
    n3_texts = []
    for value in values:
        if isinstance(value, BNode):
            return None, reason(
                "UNSUPPORTED_BLANK_NODE",
                "rdfBlankNode",
                f"sh:in list on <{link}> contains a blank node element; only "
                "IRI and supported literal values are exchangeable",
            )
        if not isinstance(value, URIRef | Literal):
            return None, reason(
                "UNSUPPORTED_SHACL",
                "shaclAdvanced",
                f"sh:in list on <{link}> contains an unsupported RDF term",
            )
        if isinstance(value, Literal):
            if value.ill_typed or literal_datatype(value) not in SUPPORTED_DATATYPES:
                return None, reason(
                    "UNSUPPORTED_LITERAL_DATATYPE",
                    "datatype",
                    f"sh:in list on <{link}> contains a literal outside the P0 "
                    "datatype set (string/langString/boolean/integer/decimal/"
                    "double/date/dateTime)",
                )
            try:
                n3_texts.append(canonical_object(value))
            except (ValueError, TypeError):
                return None, reason(
                    "UNSUPPORTED_SHACL",
                    "shaclAdvanced",
                    f"sh:in list on <{link}> contains a literal that cannot be "
                    "canonicalized into a stored RDF term",
                )
        else:
            n3_texts.append(canonical_object(value))
    return n3_texts, None


def _numeric_bound(link, predicate, values):
    """Validate one numericRange bound: exactly one well-typed finite decimal.

    Returns (lexical_or_None, reason) - a reason rejects the whole document;
    None without a reason means the predicate is absent with cardinality zero.
    """
    if not values:
        return None, None
    if len(values) > 1:
        return None, reason(
            "UNSUPPORTED_SHACL",
            "shaclAdvanced",
            f"<{predicate}> on <{link}> must appear exactly once, not {len(values)} times",
        )
    value = values[0]
    if not isinstance(value, Literal) or value.language is not None:
        return None, reason(
            "UNSUPPORTED_SHACL",
            "shaclAdvanced",
            f"<{predicate}> on <{link}> must be a numeric typed literal",
        )
    if literal_datatype(value) not in NUMERIC_BOUND_DATATYPES or value.ill_typed:
        return None, reason(
            "UNSUPPORTED_SHACL",
            "shaclAdvanced",
            f"<{predicate}> on <{link}> must use one of the numeric datatypes "
            "(xsd:integer/xsd:int/xsd:nonNegativeInteger/xsd:decimal/xsd:double/"
            "xsd:float) with a well-typed value",
        )
    text = str(value)
    if not text or len(text) > 128:
        return None, reason(
            "UNSUPPORTED_SHACL",
            "shaclAdvanced",
            f"<{predicate}> on <{link}> carries an unusable numeric lexical form",
        )
    from ontolearn_engine.quality.definitions import numeric as quality_numeric

    try:
        quality_numeric(text, ())
    except ValueError:
        return None, reason(
            "UNSUPPORTED_SHACL",
            "shaclAdvanced",
            f"<{predicate}> on <{link}> must be a finite decimal number text (got {text!r})",
        )
    return text, None


def _template_constraints(graph):
    """Recognize exactly the six exported P0 SHACL template shapes.

    Returns (definitions, recognized_triples, list_nodes, reasons). Anything
    SHACL-shaped that is not one of these templates becomes an explicit
    UNSUPPORTED_SHACL / UNSUPPORTED_SHACL_PATH rejection.
    """
    reasons = []
    node_shapes = {s for s in graph.subjects(RDF.type, SH.NodeShape) if isinstance(s, URIRef)}
    property_shapes = {
        s for s in graph.subjects(RDF.type, SH.PropertyShape) if isinstance(s, URIRef)
    }
    recognized, list_nodes = set(), set()
    definitions = []
    used_property_shapes = set()
    for shape in sorted(node_shapes, key=str):
        predicates = {str(p) for p in graph.predicates(shape, None)}
        if predicates - NODE_SHAPE_PREDICATES:
            reasons.append(
                reason(
                    "UNSUPPORTED_SHACL",
                    "shaclAdvanced",
                    f"Node shape <{shape}> carries predicates outside the P0 template "
                    "(sh:targetClass/sh:property/sh:deactivated)",
                )
            )
            continue
        types = {o for o in graph.objects(shape, RDF.type)}
        target = _single_object(graph, shape, SH.targetClass)
        link = _single_object(graph, shape, SH.property)
        deactivated = list(graph.objects(shape, URIRef(SH_DEACTIVATED)))
        enabled = True
        if len(deactivated) > 1:
            reasons.append(
                reason(
                    "UNSUPPORTED_SHACL",
                    "shaclAdvanced",
                    f"sh:deactivated on <{shape}> must appear at most once",
                )
            )
            continue
        if deactivated:
            flag = deactivated[0]
            if (
                not isinstance(flag, Literal)
                or flag.language is not None
                or flag.datatype is None
                or str(flag.datatype) != str(XSD.boolean)
                or str(flag) not in ("true", "false")
            ):
                reasons.append(
                    reason(
                        "UNSUPPORTED_SHACL",
                        "shaclAdvanced",
                        f"sh:deactivated on <{shape}> must be a strict xsd:boolean "
                        "literal 'true' or 'false'",
                    )
                )
                continue
            enabled = str(flag) != "true"
        if (
            types != {SH.NodeShape}
            or not isinstance(target, URIRef)
            or not isinstance(link, URIRef)
            or link not in property_shapes
            or link in used_property_shapes
        ):
            reasons.append(
                reason(
                    "UNSUPPORTED_SHACL",
                    "shaclAdvanced",
                    f"Node shape <{shape}> is not the single-target single-property P0 template",
                )
            )
            continue
        identity = str(shape)[len(SHAPE_PREFIX) :] if str(shape).startswith(SHAPE_PREFIX) else None
        if (
            not str(shape).startswith(SHAPE_PREFIX)
            or identity is None
            or NAME_PATTERN.fullmatch(identity) is None
            or str(link) != SHAPE_PREFIX + identity + PROPERTY_SHAPE_SUFFIX
        ):
            reasons.append(
                reason(
                    "UNSUPPORTED_SHACL",
                    "shaclAdvanced",
                    f"Shape <{shape}> does not use the exported template shape IRIs",
                )
            )
            continue
        used_property_shapes.add(link)
        shape_triples = {
            (s, p, o) for s, p, o in graph.triples((shape, None, None)) if p != RDF.type
        } | {(shape, RDF.type, SH.NodeShape)}
        path = _single_object(graph, link, SH.path)
        path_ok = isinstance(path, URIRef) and {o for o in graph.objects(link, RDF.type)} == {
            SH.PropertyShape
        }
        present = {str(p) for p in graph.predicates(link, None)}
        if not path_ok or present - PROPERTY_SHAPE_PREDICATES or str(SH.path) not in present:
            reasons.append(
                reason(
                    "UNSUPPORTED_SHACL",
                    "shaclAdvanced",
                    f"Property shape <{link}> is not the direct-path P0 property template "
                    "(sh:targetClass/sh:property/sh:deactivated belong to the node shape)",
                )
            )
            continue
        groups = {
            "required": str(SH.minCount) in present,
            "datatype": str(SH.datatype) in present,
            "maxCount": str(SH.maxCount) in present,
            "allowedValues": SH_IN in present,
            "numericRange": str(SH.minInclusive) in present or str(SH.maxInclusive) in present,
        }
        chosen = [name for name, on in groups.items() if on]
        template, parameters = None, None
        if len(chosen) == 1:
            template = chosen[0]
            if template == "required":
                minimum = _integer_literal(_single_object(graph, link, SH.minCount))
                parameters = {} if minimum == 1 else None
            elif template == "datatype":
                datatype = _single_object(graph, link, SH.datatype)
                parameters = {"datatype": str(datatype)} if isinstance(datatype, URIRef) else None
            elif template == "maxCount":
                maximum = _integer_literal(_single_object(graph, link, SH.maxCount))
                parameters = {"maxCount": maximum} if maximum is not None and maximum >= 0 else None
            elif template == "allowedValues":
                head = _single_object(graph, link, URIRef(SH_IN))
                walked = _read_list(graph, head) if head is not None else None
                if walked is not None:
                    values, nodes = walked
                    n3_texts, value_reason = _allowed_value_n3(link, values)
                    if value_reason is not None:
                        reasons.append(value_reason)
                        parameters = None
                    else:
                        parameters = {"values": n3_texts}
                        list_nodes |= nodes
                        shape_triples |= {
                            triple for node in nodes for triple in graph.triples((node, None, None))
                        } | {(link, URIRef(SH_IN), head)}
                else:
                    reasons.append(
                        reason(
                            "UNSUPPORTED_BLANK_NODE",
                            "rdfBlankNode",
                            f"sh:in on <{link}> is not a non-empty flat value template list",
                        )
                    )
            else:
                low, low_reason = _numeric_bound(
                    link, SH.minInclusive, list(graph.objects(link, SH.minInclusive))
                )
                high, high_reason = None, None
                if low_reason is None:
                    high, high_reason = _numeric_bound(
                        link, SH.maxInclusive, list(graph.objects(link, SH.maxInclusive))
                    )
                if low_reason is not None:
                    reasons.append(low_reason)
                elif high_reason is not None:
                    reasons.append(high_reason)
                elif low is not None or high is not None:
                    parameters = {"minInclusive": low, "maxInclusive": high}
        if template is None or parameters is None:
            reasons.append(
                reason(
                    "UNSUPPORTED_SHACL",
                    "shaclAdvanced",
                    f"Property shape <{link}> does not carry exactly one of the six P0 "
                    "template constraints",
                )
            )
            continue
        definition = {
            "schemaVersion": 1,
            "kind": "constraint",
            "id": identity,
            "revision": 1,
            "label": identity,
            "enabled": enabled,
            "targetClass": str(target),
            "path": str(path),
            "template": template,
            "parameters": parameters,
        }
        try:
            from ontolearn_engine.quality.definitions import (
                DefinitionError,
                validate_definition,
            )

            validate_definition(definition)
        except (DefinitionError, ValueError, TypeError, KeyError):
            reasons.append(
                reason(
                    "UNSUPPORTED_SHACL",
                    "shaclAdvanced",
                    f"Constraint template for <{link}> is not a valid P0 constraint definition",
                )
            )
            continue
        definitions.append({"layer": "constraint", "id": identity, "value": definition})
        recognized |= shape_triples | set(graph.triples((link, None, None)))
    # Unused property shapes and any other SHACL residue are explicit rejects.
    for shape in sorted(property_shapes - used_property_shapes, key=str):
        reasons.append(
            reason(
                "UNSUPPORTED_SHACL",
                "shaclAdvanced",
                f"Property shape <{shape}> is not referenced by an exported template node shape",
            )
        )
    return definitions, recognized, list_nodes, reasons


def check_import(store, public, params):
    """Three-branch result: ok (plan), rejected (constructs), invalid (format/syntax)."""
    if params["format"] != TURTLE_FORMAT:
        return _invalid(
            "UNSUPPORTED_FORMAT",
            "rdfFormat",
            f"Format {params['format']!r} is not supported; only 'turtle' is exchangeable",
        )
    try:
        graph = _parse(params["turtleText"], params["baseUri"])
    except ValueError as error:
        return _invalid(
            "INVALID_TURTLE",
            "rdfSyntax",
            f"Turtle text could not be parsed safely offline ({error.args[0]})",
        )
    constraint_defs, recognized, list_nodes, reasons = _template_constraints(graph)
    content = []
    shacl_namespace = str(SH)
    for subject, predicate, obj in graph:
        triple = (subject, predicate, obj)
        if triple in recognized:
            continue
        if str(predicate) in TEMPLATE_PATH_PREDICATES or str(obj) in TEMPLATE_PATH_PREDICATES:
            reasons.append(
                reason(
                    "UNSUPPORTED_SHACL_PATH",
                    "shaclPath",
                    f"SHACL path component <{predicate}> uses inverse/alternative/multi-step "
                    "paths outside the P0 direct template path",
                )
            )
            continue
        if any(
            isinstance(term, URIRef) and str(term).startswith(shacl_namespace) for term in triple
        ):
            reasons.append(
                reason(
                    "UNSUPPORTED_SHACL",
                    "shaclAdvanced",
                    f"SHACL construct <{predicate}> is not one of the P0 template constraints",
                )
            )
            continue
        if isinstance(subject, BNode) or isinstance(obj, BNode):
            reasons.append(
                reason(
                    "UNSUPPORTED_BLANK_NODE",
                    "rdfBlankNode",
                    "Blank nodes are only supported inside value template constraint lists",
                )
            )
            continue
        content.append(triple)
    reasons += check_content_triples(iter(content))
    # B08: reject lexically distinct literals that would fold onto one stored
    # value (for example 1 and +01), and ill-typed literals, before any plan.
    reasons += literal_collision_reasons(iter(content))
    if reasons:
        return _reject(reasons)
    definitions, manual = build_plan(iter(content))
    definitions += constraint_defs
    if (
        len(definitions) > MAX_PLAN_ITEMS
        or len(manual) > MAX_PLAN_ITEMS
        or any(
            len(item["value"].get("triples", ())) > MAX_PLAN_ITEMS
            for item in definitions
            if item["layer"] == "ontology"
        )
    ):
        fault("RESOURCE_LIMIT", resource="frame")
    internal = resolve_active(store, public)
    snapshot = store._snapshot_projection(internal)
    result = {
        "status": "ok",
        "summary": {
            "baseRevision": snapshot["projectRevision"],
            "inputSnapshotId": digest(snapshot),
            "tripleCount": len(graph),
            "definitionCount": len(definitions),
            "manualFactCount": len(manual),
        },
        "plan": {"definitions": definitions, "manual": manual},
    }
    store._valid("result_project.ontology.import.check", result)
    return result


def dispatch(store, method, params):
    store._valid("params_project.ontology.import.check", params)
    return check_import(store, params["projectId"], params)
