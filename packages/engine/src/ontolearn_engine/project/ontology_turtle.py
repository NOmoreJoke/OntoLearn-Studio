"""FR-203 deterministic Turtle export of the committed P0 ontology scope.

The export is a whole-batch contract: the committed snapshot's ontology
definitions plus non-tombstone facts are rebuilt through the existing
``rdf_snapshot.graph_from_snapshot`` reader, and P0 constraint templates are
compiled with the quality editor's own deterministic SHACL compiler. Any
construct outside the frozen Appendix C P0 vocabulary rejects the entire
export with explicit reasons; there is never a partial Turtle document and
never a silent drop of stored structure.
"""

import json
import re

from rdflib import OWL, RDF, RDFS, SH, XSD, BNode, Graph, Literal, URIRef

from ontolearn_engine.rdf_snapshot import graph_from_snapshot
from ontolearn_engine.storage import Conflict, digest

METHODS = frozenset({"project.ontology.export"})
MAX_TURTLE_BYTES = 262144
MAX_PLAN_ITEMS = 4096
MAX_REASONS = 128
SHAPE_PREFIX = "urn:ontolearn:shape:"
PROPERTY_SHAPE_SUFFIX = ":property"
NAME_PATTERN = re.compile(r"[A-Za-z0-9_.-]{1,128}")
LOCAL_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*")
PREFIXES = (
    ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    ("rdfs", "http://www.w3.org/2000/01/rdf-schema#"),
    ("owl", str(OWL)),
    ("xsd", str(XSD)),
    ("sh", str(SH)),
)
SWRL_NAMESPACE = "http://www.w3.org/2003/11/swrl#"
# Appendix C P0 literal support: plain/langString plus the entity metadata
# datatype set. Everything else cannot safely round-trip and is rejected.
SUPPORTED_DATATYPES = frozenset(
    {str(RDF.langString)}
    | {
        str(XSD[name])
        for name in ("string", "boolean", "integer", "decimal", "double", "date", "dateTime")
    }
)
OWL_P0_TERMS = frozenset(
    str(term) for term in (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty)
)
RDFS_P0_TERMS = frozenset(
    str(term)
    for term in (RDFS.Class, RDFS.subClassOf, RDFS.domain, RDFS.range, RDFS.label, RDFS.comment)
)
# Ontology definition payload keys whose meaning is fully carried by the RDF
# graph or by Store bookkeeping that the Turtle contract does not promise.
ONTOLOGY_PAYLOAD_KEYS = frozenset(
    {"triples", "singleValuedPredicates", "references", "entityMetadata"}
)
# Constraint template vocabulary shared with the import-side recognition.
TEMPLATE_PATH_PREDICATES = frozenset(
    str(term)
    for term in (
        SH.inversePath,
        SH.alternativePath,
        SH.zeroOrMorePath,
        SH.oneOrMorePath,
        SH.zeroOrOnePath,
    )
)
SH_IN = "http://www.w3.org/ns/shacl#in"
SH_DEACTIVATED = str(SH.deactivated)
# Template shape vocabulary is validated per node kind: node shapes never carry
# property-shape constraints and property shapes never carry sh:targetClass,
# sh:property or sh:deactivated (B03). SHAPE_PREDICATES keeps the union for
# callers that only need "some P0 template predicate" membership.
NODE_SHAPE_PREDICATES = frozenset(
    [str(term) for term in (RDF.type, SH.targetClass, SH.property)] + [SH_DEACTIVATED]
)
PROPERTY_SHAPE_PREDICATES = frozenset(
    [
        str(term)
        for term in (
            RDF.type,
            SH.path,
            SH.minCount,
            SH.maxCount,
            SH.datatype,
            SH.minInclusive,
            SH.maxInclusive,
        )
    ]
    + [SH_IN]
)
SHAPE_PREDICATES = NODE_SHAPE_PREDICATES | PROPERTY_SHAPE_PREDICATES
STRUCTURAL_TYPES = OWL_P0_TERMS | {str(RDFS.Class)}
STRUCTURAL_N3_TYPES = frozenset(f"<{term}>" for term in STRUCTURAL_TYPES)
STRUCTURAL_PREDICATES = frozenset({str(RDFS.subClassOf), str(RDFS.domain), str(RDFS.range)})
ANNOTATION_PREDICATES = frozenset({str(RDFS.label), str(RDFS.comment)})


def fault(code, **params):
    from ontolearn_engine.job_store import fault as job_fault

    job_fault(code, **params)


def reason(code, field, detail):
    return {"code": code, "field": field, "detail": detail}


def _canonical_literal(value):
    """Plain-string folding mirrors rdf_snapshot.term without re-parsing."""
    if isinstance(value, Literal) and value.datatype == XSD.string and value.language is None:
        return Literal(str(value))
    return value


def literal_datatype(value):
    if value.language is not None:
        return str(RDF.langString)
    if value.datatype is None:
        return str(XSD.string)
    return str(value.datatype)


def check_content_triples(graph):
    """Appendix C P0 vocabulary audit over one content graph (no SHACL here).

    Returns the rejection reasons; an empty list means every triple is inside
    the frozen P0 exchange vocabulary.
    """
    reasons = []
    for subject, predicate, obj in graph:
        for term in (subject, predicate, obj):
            if isinstance(term, URIRef):
                text = str(term)
                if text.startswith(SWRL_NAMESPACE):
                    reasons.append(
                        reason(
                            "UNSUPPORTED_OWL",
                            "owlExpression",
                            f"SWRL construct <{text}> is outside the P0 exchange scope",
                        )
                    )
                elif text.startswith(str(OWL)) and text not in OWL_P0_TERMS:
                    reasons.append(
                        reason(
                            "UNSUPPORTED_OWL",
                            "owlExpression",
                            f"OWL construct <{text}> is outside the P0 exchange scope",
                        )
                    )
                elif text.startswith(str(RDFS)) and text not in RDFS_P0_TERMS:
                    reasons.append(
                        reason(
                            "UNSUPPORTED_RDFS",
                            "rdfsConstruct",
                            f"RDFS construct <{text}> is outside the P0 exchange scope",
                        )
                    )
        if predicate in (RDF.first, RDF.rest) or subject == RDF.nil or obj == RDF.nil:
            reasons.append(
                reason(
                    "UNSUPPORTED_BLANK_NODE",
                    "rdfBlankNode",
                    "Generic RDF list constructs (rdf:first/rdf:rest/rdf:nil) are only "
                    "supported inside value template constraint shapes",
                )
            )
        if isinstance(obj, Literal) and literal_datatype(obj) not in SUPPORTED_DATATYPES:
            reasons.append(
                reason(
                    "UNSUPPORTED_LITERAL_DATATYPE",
                    "datatype",
                    f"Literal datatype <{literal_datatype(obj)}> is outside the P0 set "
                    "(string/langString/boolean/integer/decimal/double/date/dateTime)",
                )
            )
        if predicate in (RDFS.subClassOf, RDFS.domain, RDFS.range) and not isinstance(obj, URIRef):
            reasons.append(
                reason(
                    "UNSUPPORTED_RDFS",
                    "rdfsConstruct",
                    f"<{predicate}> must reference a class IRI, not a literal",
                )
            )
    return reasons


def _uri(term):
    text = str(term)
    for prefix, namespace in PREFIXES:
        if text.startswith(namespace) and LOCAL_PATTERN.fullmatch(text[len(namespace) :]):
            return f"{prefix}:{text[len(namespace) :]}"
    return f"<{text}>"


def _term_n3(term):
    if isinstance(term, URIRef):
        return _uri(term)
    return _canonical_literal(term).n3()


def n3_triple_set(graph):
    """Canonical N3 triple set used for isomorphic byte comparisons."""
    return {(str(s), str(p), _canonical_literal(o).n3()) for s, p, o in graph}


def serialize_graph(graph):
    """Deterministic subject-grouped Turtle; output depends only on the triple set."""
    grouped = {}
    for subject, predicate, obj in graph:
        grouped.setdefault(subject, {}).setdefault(predicate, set()).add(obj)
    lines = [f"@prefix {prefix}: <{namespace}> ." for prefix, namespace in PREFIXES]
    for subject in sorted(grouped, key=_term_n3):
        predicates = grouped[subject]
        parts = []
        for predicate in sorted(predicates, key=_term_n3):
            objects = ", ".join(sorted(_term_n3(obj) for obj in predicates[predicate]))
            parts.append(f"{_term_n3(predicate)} {objects}")
        lines.append("")
        lines.append(f"{_term_n3(subject)} " + " ;\n    ".join(parts) + " .")
    return "\n".join(lines) + "\n"


def parse_export_turtle(text, base_uri):
    """Offline lexical Turtle parse; ValueError carries the INVALID_TURTLE verdict."""
    from rdflib.plugins.parsers.notation3 import BadSyntax, Notation3InputError

    from ontolearn_engine.semantic_offline import offline
    from ontolearn_engine.semantic_turtle import parse_graph

    with offline():
        try:
            return parse_graph(text, base_uri=base_uri)
        except (BadSyntax, Notation3InputError) as error:
            raise ValueError("INVALID_TURTLE") from error


def constraint_sections(state):
    """Compile every committed constraint template into deterministic SHACL Turtle.

    Returns (sections, triple_counts, reasons); a reason means the stored
    constraint layer cannot be represented in the P0 export and the whole
    export must be rejected.
    """
    from ontolearn_engine.quality.definitions import (
        DefinitionError,
        compile_constraint_turtle,
        validate_definition,
    )

    sections, counts, reasons = [], [], []
    for record in state["definitions"]:
        if record["layer"] != "constraint":
            continue
        try:
            payload = json.loads(record["payload"])
            if isinstance(payload, dict):
                validate_definition(payload)
        except (DefinitionError, ValueError, TypeError, KeyError):
            reasons.append(
                reason(
                    "UNSUPPORTED_SHACL",
                    "shaclAdvanced",
                    f"Constraint definition {record['id']!r} is outside the six P0 "
                    "template constraints (required/datatype/maxCount/allowedValues/numericRange)",
                )
            )
            continue
        if (
            not isinstance(payload, dict)
            or payload.get("kind") != "constraint"
            or payload.get("id") != record["id"]
        ):
            reasons.append(
                reason(
                    "UNSUPPORTED_SHACL",
                    "shaclAdvanced",
                    f"Constraint definition {record['id']!r} is not a canonical P0 template shape",
                )
            )
            continue
        try:
            text = compile_constraint_turtle(payload)
            count = len(parse_export_turtle(text, "urn:ontolearn:export:"))
        except ValueError:
            fault("INVALID_STATE")
        sections.append((record["id"], text))
        counts.append(count)
    return sections, counts, reasons


def resolve_active(store, public):
    from ontolearn_engine.project.applications import uuid_ref
    from ontolearn_engine.project.management import active, public_internal

    if not uuid_ref(public):
        fault("INVALID_REQUEST", field="params")
    internal = public_internal(store, public)
    try:
        active(store, internal)
    except Conflict:
        fault("INVALID_STATE")
    return internal


def _grounded_triple_set(graph):
    """Canonical set of the blank-node-free triples for strict comparison."""
    return {
        (str(s), str(p), _canonical_literal(o).n3())
        for s, p, o in graph
        if not isinstance(s, BNode) and not isinstance(o, BNode)
    }


def _merged_export_graph(graph, sections):
    """Content graph plus every compiled section, blank nodes de-conflicted.

    Each section's blank nodes are renamed into a per-section namespace before
    merging, so two sections can never collide on a generated node label.
    """
    merged = Graph()
    for triple in graph:
        merged.add(triple)
    for index, (_, text) in enumerate(sections):
        section = parse_export_turtle(text, "urn:ontolearn:export:")
        renaming = {}
        for subject, predicate, obj in section:
            if isinstance(subject, BNode):
                subject = renaming.setdefault(subject, BNode(f"section{index}-{subject}"))
            if isinstance(obj, BNode):
                obj = renaming.setdefault(obj, BNode(f"section{index}-{obj}"))
            merged.add((subject, predicate, obj))
    return merged


def export_ontology(store, public):
    """Serialize the committed P0 scope; never touches drafts and never writes."""
    internal = resolve_active(store, public)
    snapshot = store._snapshot_projection(internal)
    state = snapshot["state"]
    graph = graph_from_snapshot(snapshot)
    reasons = check_content_triples(graph)
    for record in state["definitions"]:
        if record["layer"] != "ontology":
            continue
        try:
            payload = json.loads(record["payload"])
        except (ValueError, TypeError):
            payload = None
        if not isinstance(payload, dict) or set(payload) - ONTOLOGY_PAYLOAD_KEYS:
            reasons.append(
                reason(
                    "UNSUPPORTED_RDFS",
                    "rdfsConstruct",
                    f"Ontology definition {record['id']!r} carries payload structure that "
                    "cannot be represented in the P0 Turtle exchange",
                )
            )
    sections, counts, section_reasons = constraint_sections(state)
    reasons += section_reasons
    if reasons:
        return {"status": "rejected", "reasons": reasons[:MAX_REASONS]}
    turtle = serialize_graph(graph)
    for _, text in sorted(sections):
        turtle += "\n" + text
    if len(turtle.encode("utf-8")) > MAX_TURTLE_BYTES:
        fault("RESOURCE_LIMIT", resource="frame")
    triple_count = len(graph) + sum(counts)
    # Self-check before returning: the emitted document must re-parse into
    # exactly the same triples (zero surplus, zero loss). Grounded triples
    # (no blank nodes) keep the strict canonical set comparison; the whole
    # document is additionally checked for graph isomorphism against the
    # merged content-plus-sections graph, because sh:in value lists serialize
    # as fresh blank nodes on every independent parse and their identities can
    # never be compared as bare strings across two parses (B02).
    verification = parse_export_turtle(turtle, "urn:ontolearn:export:")
    merged = _merged_export_graph(graph, sections)
    if (
        len(verification) != triple_count
        or len(merged) != triple_count
        or _grounded_triple_set(verification) != _grounded_triple_set(merged)
    ):
        fault("INVALID_STATE")
    from rdflib.compare import isomorphic

    if not isomorphic(verification, merged):
        fault("INVALID_STATE")
    result = {
        "status": "ok",
        "turtle": turtle,
        "tripleCount": triple_count,
        "inputSnapshotId": digest(snapshot),
        "projectRevision": snapshot["projectRevision"],
    }
    store._valid("result_project.ontology.export", result)
    return result


def canonical_object(obj):
    """Canonical N3 text for one parsed RDF object term (Store fact format)."""
    from ontolearn_engine.rdf_snapshot import term

    return term(_canonical_literal(obj).n3()).n3()


def literal_collision_reasons(content):
    """B08: reject lexically distinct literals the Store would silently fold.

    The exchange parser preserves exact lexical forms (``+01`` vs ``1``), but
    ``canonical_object`` re-parses through the normalizing Store term gate and
    can collapse several distinct RDF literals onto one stored N3 value - which
    would merge two input triples into one fact with a shared id. Ill-typed
    literals (``"abc"^^xsd:integer``) are rejected the same way. Exact RDF
    triple duplicates stay legal set semantics and never reach this collision
    path as two distinct terms.
    """
    reasons = []
    seen = {}
    for subject, predicate, obj in content:
        if not isinstance(obj, Literal):
            continue
        if obj.ill_typed:
            reasons.append(
                reason(
                    "UNSUPPORTED_LITERAL_DATATYPE",
                    "datatype",
                    f"Literal {obj.n3()} is ill-typed for its datatype and cannot "
                    "be stored losslessly in the P0 exchange",
                )
            )
            continue
        try:
            key = (str(subject), str(predicate), canonical_object(obj))
        except (ValueError, TypeError):
            reasons.append(
                reason(
                    "UNSUPPORTED_LITERAL_DATATYPE",
                    "datatype",
                    f"Literal {obj.n3()} cannot be represented as a canonical "
                    "stored RDF term in the P0 exchange",
                )
            )
            continue
        # Pre-normalization identity: raw lexical form plus datatype and
        # language as parsed (language tags keep their original case here).
        identity = (str(obj), literal_datatype(obj), obj.language)
        first = seen.setdefault(key, identity)
        if first != identity:
            reasons.append(
                reason(
                    "UNSUPPORTED_LITERAL_DATATYPE",
                    "datatype",
                    f"Triples of <{subject}> <{predicate}> carry lexically different "
                    "literals (for example differing numeric spellings or language "
                    "tag case) that normalize to one identical stored value; the "
                    "Store cannot keep both without silent loss",
                )
            )
    return reasons


def manual_fact(subject, predicate, obj):
    return {
        "id": digest([subject, predicate, obj]),
        "subject": subject,
        "predicate": predicate,
        "object": obj,
    }


def build_plan(content):
    """Partition checked content triples into a ChangeSet plan (pure, no Store).

    Structural schema triples (class/property typing, hierarchy and domain/range
    axioms, plus their annotations) collapse into one deterministic ontology
    definition; every remaining assertion becomes a content-derived manual fact.
    """
    n3_triples = sorted(
        (str(subject), str(predicate), canonical_object(obj)) for subject, predicate, obj in content
    )
    # A structural axiom (rdfs:subClassOf / rdfs:domain / rdfs:range) is a
    # schema statement on its own: it joins the definition layer even without
    # a same-batch rdf:type declaration, and its subject (like every typed
    # structural subject) drags its rdfs:label / rdfs:comment annotations into
    # the definition layer too (B11).
    structural_subjects = {
        subject
        for subject, predicate, obj in n3_triples
        if (predicate == str(RDF.type) and obj in STRUCTURAL_N3_TYPES)
        or predicate in STRUCTURAL_PREDICATES
    }
    definition_triples, manual = [], []
    for subject, predicate, obj in n3_triples:
        structural = subject in structural_subjects and (
            (predicate == str(RDF.type) and obj in STRUCTURAL_N3_TYPES)
            or predicate in STRUCTURAL_PREDICATES
            or predicate in ANNOTATION_PREDICATES
        )
        if structural:
            definition_triples.append({"subject": subject, "predicate": predicate, "object": obj})
        else:
            manual.append(manual_fact(subject, predicate, obj))
    definitions = []
    if definition_triples:
        identity = "ontology-import-" + digest(definition_triples)[:24]
        definitions.append(
            {
                "layer": "ontology",
                "id": identity,
                "value": {
                    "triples": definition_triples,
                    "singleValuedPredicates": [],
                    "references": [],
                },
            }
        )
    return definitions, manual


def dispatch(store, method, params):
    store._valid("params_project.ontology.export", params)
    return export_ontology(store, params["projectId"])
