"""I05 finite semantics candidate. Pure inputs/outputs; no Store or protocol writes.

RDFS subclass/domain/range closure precedes one frozen rule pass. Rule output
never feeds another rule or RDFS. No OWL-RL or SHACL-AF expansion is enabled.
"""

from dataclasses import dataclass
from decimal import Decimal
from functools import cmp_to_key
from math import isfinite

from pyshacl.validator import Validator
from rdflib import OWL, RDF, RDFS, SH, XSD, BNode, Graph, Literal, URIRef, Variable
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.stores.memory import Memory
from rdflib.term import Identifier

from ontolearn_engine.semantic_offline import SemanticError, offline
from ontolearn_engine.semantic_query import prepare_lexical_query
from ontolearn_engine.semantic_turtle import parse_graph

MAX_TEXT_BYTES = 1_048_576
MAX_TRIPLES = 100_000
MAX_RULE_MATCHES = 100_000
MAX_WORK = 1_000_000
SEMANTICS_VERSION = "i05-finite-5"
Triple = tuple[Identifier, Identifier, Identifier]


def _text(text):
    if not isinstance(text, str):
        raise SemanticError("TEXT_TYPE_INVALID")
    try:
        size = len(text.encode("utf-8"))
    except UnicodeEncodeError as error:
        raise SemanticError("INVALID_UNICODE") from error
    if size > MAX_TEXT_BYTES:
        raise SemanticError("TEXT_INPUT_LIMIT")


def _copy(graph):
    # Never accept a URL, persistent/remote Store, Dataset, or plugin subclass.
    if type(graph) is not Graph or type(graph.store) is not Memory:
        raise SemanticError("IN_MEMORY_GRAPH_REQUIRED")
    if len(graph) > MAX_TRIPLES:
        raise SemanticError("GRAPH_INPUT_LIMIT")
    result = Graph()
    for triple in graph:
        result.add(triple)
    return result


def _terms(graph, *, shapes=False):
    allowed_owl = {OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty}
    allowed_rdfs = {
        RDFS.Class,
        RDFS.subClassOf,
        RDFS.domain,
        RDFS.range,
        RDFS.label,
        RDFS.comment,
    }
    if any(graph.triples((None, OWL.imports, None))):
        raise SemanticError("EXTERNAL_ACCESS_DENIED")
    for s, p, o in sorted(graph, key=_key):
        if p == OWL.imports:
            raise SemanticError("EXTERNAL_ACCESS_DENIED")
        if not isinstance(s, URIRef | BNode) or not isinstance(p, URIRef):
            raise SemanticError("RDF_TERM_INVALID")
        for term in (s, p, o):
            if isinstance(term, BNode) and not shapes:
                raise SemanticError("UNSUPPORTED_BLANK_NODE")
            if isinstance(term, URIRef):
                value = str(term)
                if ":" not in value or any(c.isspace() or c in '<>"{}|^`\\' for c in value):
                    raise SemanticError("ABSOLUTE_IRI_REQUIRED")
                if value.startswith(str(OWL)) and term not in allowed_owl:
                    raise SemanticError("UNSUPPORTED_OWL")
                if value.startswith(str(RDFS)) and term not in allowed_rdfs:
                    raise SemanticError("UNSUPPORTED_RDFS")
                if value.startswith(str(SH)) and not shapes:
                    raise SemanticError("UNSUPPORTED_SHACL")
            if isinstance(term, Literal):
                if term.ill_typed:
                    raise SemanticError("INVALID_LITERAL_LEXICAL")
                if term.datatype is not None and term.datatype not in _DATATYPES | {RDF.langString}:
                    raise SemanticError("UNSUPPORTED_LITERAL_DATATYPE")
                value = term.toPython()
                if (isinstance(value, Decimal) and not value.is_finite()) or (
                    isinstance(value, float) and not isfinite(value)
                ):
                    raise SemanticError("UNSUPPORTED_NONFINITE_LITERAL")
        if p in {RDFS.subClassOf, RDFS.domain, RDFS.range} and not isinstance(o, URIRef):
            raise SemanticError("RDFS_TERM_INVALID")
        if p == RDF.type and not isinstance(o, URIRef):
            raise SemanticError("RDF_TYPE_OBJECT_INVALID")


def parse_turtle(text: str, *, format: str = "turtle", shapes: bool = False) -> Graph:
    """Text only: never pass user-controlled source/location or infer a parser."""
    _text(text)
    if format != "turtle":
        raise SemanticError("UNSUPPORTED_FORMAT")
    with offline():
        try:
            graph = parse_graph(text, base_uri="urn:ontolearn:i05:")
        except Exception as error:
            raise SemanticError("INVALID_TURTLE") from error
        if len(graph) > MAX_TRIPLES:
            raise SemanticError("GRAPH_INPUT_LIMIT")
        _terms(graph, shapes=shapes)
        return graph


def _walk(value):
    if isinstance(value, CompValue):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list | tuple):
        for child in value:
            yield from _walk(child)


def query(graph: Graph, text: str) -> dict:
    _text(text)
    with offline():
        local = _copy(graph)
        _terms(local)
        prepared = prepare_lexical_query(text)
        if prepared.algebra.name not in {"SelectQuery", "AskQuery"}:
            raise SemanticError("READ_ONLY_QUERY_REQUIRED")
        orderings = []
        named_graph = False
        for node in _walk(prepared.algebra):
            if node.name in {"ServiceGraphPattern", "DatasetClause"}:
                raise SemanticError("EXTERNAL_ACCESS_DENIED")
            if node.name == "Graph":
                named_graph = True
            if node.name.startswith("Aggregate_") and node.name != "Aggregate_Count":
                # Floating reductions and equal-valued MIN/MAX terms depend on the
                # library's hash iteration order. Candidate only promises COUNT.
                raise SemanticError("UNSUPPORTED_QUERY_FUNCTION")
            if node.name in {
                "Function",
                "Builtin_RAND",
                "Builtin_NOW",
                "Builtin_UUID",
                "Builtin_STRUUID",
                "Builtin_BNODE",
                "Aggregate_Sample",
                "Aggregate_GroupConcat",
            }:
                raise SemanticError("UNSUPPORTED_QUERY_FUNCTION")
            if node.name == "Slice":
                raise SemanticError("QUERY_SLICE_UNSUPPORTED")
            if node.name == "OrderBy":
                orderings.append(node)
        if named_graph:
            raise SemanticError("QUERY_GRAPH_UNSUPPORTED")
        if len(orderings) > 1 or any(
            not isinstance(c.expr, Variable) or c.expr not in prepared.algebra.PV
            for order in orderings
            for c in order.expr
        ):
            raise SemanticError("UNSUPPORTED_QUERY_ORDER")
        try:
            result = local.query(prepared, use_store_provided=False)
            if result.type == "ASK":
                return {"type": "ASK", "value": bool(result.askAnswer)}
            variables = [str(v) for v in result.vars]
            values = []
            for row in result:
                values.append(tuple(row))
                if len(values) > MAX_TRIPLES:
                    raise SemanticError("QUERY_RESULT_LIMIT")

            def canonical(row):
                return tuple((v is not None, v.n3() if v is not None else "") for v in row)

            def compare(left, right):
                from rdflib.plugins.sparql.evalutils import _val

                for order in orderings:
                    for condition in order.expr:
                        index = variables.index(str(condition.expr))
                        a, b = left[index], right[index]
                        a_key = _val(a) if a is not None else (0, "")
                        b_key = _val(b) if b is not None else (0, "")
                        delta = -1 if a_key < b_key else (1 if b_key < a_key else 0)
                        if delta:
                            return -delta if condition.order == "DESC" else delta
                a, b = canonical(left), canonical(right)
                return -1 if a < b else (1 if a > b else 0)

            values.sort(key=cmp_to_key(compare))
            rows = [[v.n3() if v is not None else None for v in row] for row in values]
            return {"type": "SELECT", "variables": variables, "rows": rows}
        except SemanticError:
            raise
        except Exception as error:
            raise SemanticError("QUERY_FAILED") from error


@dataclass(frozen=True)
class Rule:
    id: str
    when: tuple[Triple, ...]
    then: Triple


def _key(triple):
    return tuple(term.n3() for term in triple)


def _rule(rule):
    if (
        not isinstance(rule, Rule)
        or not isinstance(rule.id, str)
        or not 1 <= len(rule.id) <= 128
        or not isinstance(rule.when, tuple)
        or not 1 <= len(rule.when) <= 16
    ):
        raise SemanticError("INVALID_RULE")
    variables = set()
    for pattern in (*rule.when, rule.then):
        if not isinstance(pattern, tuple) or len(pattern) != 3:
            raise SemanticError("INVALID_RULE")
        for term in pattern:
            if not isinstance(term, URIRef | Literal | Variable):
                raise SemanticError("INVALID_RULE")
        if not isinstance(pattern[0], URIRef | Variable) or not isinstance(
            pattern[1], URIRef | Variable
        ):
            raise SemanticError("INVALID_RULE")
        candidate = Graph()
        candidate.add(
            tuple(
                URIRef("urn:ontolearn:rule-variable") if isinstance(t, Variable) else t
                for t in pattern
            )
        )
        _terms(candidate)
    for pattern in rule.when:
        variables.update(t for t in pattern if isinstance(t, Variable))
    if any(isinstance(t, Variable) and t not in variables for t in rule.then):
        raise SemanticError("UNBOUND_RULE_VARIABLE")
    # Output predicate must be fixed; arbitrary schema predicates cannot be bound
    # through a wildcard. Rules produce domain assertions or domain class membership.
    predicate, target = rule.then[1:]
    if predicate == RDF.type and not isinstance(target, URIRef | Variable):
        raise SemanticError("UNSUPPORTED_RULE_OUTPUT")
    if not isinstance(predicate, URIRef) or (
        predicate != RDF.type
        and any(str(predicate).startswith(str(ns)) for ns in (RDF, RDFS, OWL, SH))
    ):
        raise SemanticError("UNSUPPORTED_RULE_OUTPUT")
    if (
        predicate == RDF.type
        and isinstance(target, URIRef)
        and any(str(target).startswith(str(ns)) for ns in (RDF, RDFS, OWL, SH))
    ):
        raise SemanticError("UNSUPPORTED_RULE_OUTPUT")


def _chain_warnings(rules):
    return sorted(
        {
            "RULE_CHAIN_UNSUPPORTED:" + consumer.id
            for producer in rules
            for consumer in rules
            for pattern in consumer.when
            if all(
                isinstance(a, Variable) or isinstance(b, Variable) or a == b
                for a, b in zip(producer.then, pattern, strict=True)
            )
        }
    )


def reason(graph: Graph, rules: tuple[Rule, ...] = ()) -> dict:
    with offline():
        asserted = _copy(graph)
        _terms(asserted)
        if not isinstance(rules, tuple) or len(rules) > 100:
            raise SemanticError("INVALID_RULE")
        if any(not isinstance(rule, Rule) for rule in rules):
            raise SemanticError("INVALID_RULE")
        for rule in rules:
            _rule(rule)
        if len({r.id for r in rules}) != len(rules):
            raise SemanticError("INVALID_RULE")
        closure = _copy(asserted)
        proofs = {triple: {triple} for triple in asserted}
        changed = True
        work = 0

        def charge():
            nonlocal work
            work += 1
            if work > MAX_WORK:
                raise SemanticError("WORK_LIMIT")

        while changed:
            additions = []
            for child, _, parent in sorted(
                closure.triples((None, RDFS.subClassOf, None)), key=_key
            ):
                for s, _, _o in sorted(closure.triples((None, RDF.type, child)), key=_key):
                    charge()
                    additions.append(
                        (
                            (s, RDF.type, parent),
                            [(s, RDF.type, child), (child, RDFS.subClassOf, parent)],
                        )
                    )
                for _p, _, ancestor in closure.triples((parent, RDFS.subClassOf, None)):
                    charge()
                    additions.append(
                        (
                            (child, RDFS.subClassOf, ancestor),
                            [(child, RDFS.subClassOf, parent), (parent, RDFS.subClassOf, ancestor)],
                        )
                    )
            for predicate, relation, target in sorted(closure, key=_key):
                if relation in {RDFS.domain, RDFS.range} and predicate not in {
                    RDFS.label,
                    RDFS.comment,
                }:
                    for s, _, o in closure.triples((None, predicate, None)):
                        charge()
                        subject = s if relation == RDFS.domain else o
                        if isinstance(subject, URIRef):
                            additions.append(
                                (
                                    (subject, RDF.type, target),
                                    [(predicate, relation, target), (s, predicate, o)],
                                )
                            )
            changed = False
            # Keep one valid first witness, with a stable tie-break across all
            # direct input paths. Graph enumeration must not choose the basis.
            # This is neither all proofs nor a minimum-size proof search.
            for triple, inputs in sorted(
                additions, key=lambda item: (_key(item[0]), tuple(_key(t) for t in item[1]))
            ):
                if triple not in closure:
                    closure.add(triple)
                    proofs[triple] = set().union(*(proofs[i] for i in inputs))
                    changed = True
                    if len(closure) > MAX_TRIPLES:
                        raise SemanticError("RDFS_RESULT_LIMIT")
        # Freeze all rule inputs before applying any conclusion.
        derived = Graph()
        evidence = []
        for rule in sorted(rules, key=lambda r: r.id):
            matches = [({}, [])]
            for pattern in rule.when:
                next_matches = []
                for binding, inputs in matches:
                    lookup = tuple(
                        binding.get(t) if isinstance(t, Variable) else t for t in pattern
                    )
                    for triple in sorted(closure.triples(lookup), key=_key):
                        charge()
                        if triple[1] in {RDFS.label, RDFS.comment}:
                            continue
                        updated = dict(binding)
                        for expected, value in zip(pattern, triple, strict=True):
                            if isinstance(expected, Variable):
                                if expected in updated and updated[expected] != value:
                                    break
                                updated[expected] = value
                        else:
                            next_matches.append((updated, [*inputs, triple]))
                            if len(next_matches) > MAX_RULE_MATCHES:
                                raise SemanticError("RULE_MATCH_WORK_LIMIT")
                matches = next_matches
            for binding, inputs in matches:
                output = tuple(binding.get(t, t) for t in rule.then)
                _rule(Rule(rule.id, (output,), output))
                candidate = Graph()
                candidate.add(output)
                _terms(candidate)
                derived.add(output)
                if len(derived) + len(evidence) >= MAX_RULE_MATCHES:
                    raise SemanticError("RULE_EVIDENCE_RESULT_LIMIT")
                evidence.append(
                    {
                        "rule": rule.id,
                        "result": _key(output),
                        "inputs": [_key(t) for t in inputs],
                        "basis": [
                            _key(t)
                            for t in sorted(set().union(*(proofs[t] for t in inputs)), key=_key)
                        ],
                    }
                )
        rdfs = set(closure) - set(asserted)
        # Advisory only: a rule can still match a fact explicitly present in its input.
        warnings = _chain_warnings(rules)
        return {
            "rdfs": sorted(_key(t) for t in rdfs),
            "warnings": warnings,
            "rules": sorted(_key(t) for t in derived),
            "evidence": evidence,
            "rdfsEvidence": [
                {"result": _key(t), "basis": [_key(i) for i in sorted(proofs[t], key=_key)]}
                for t in sorted(rdfs, key=_key)
            ],
        }


_SH_PREDICATES = {
    SH.targetClass,
    SH.property,
    SH.path,
    SH.minCount,
    SH.maxCount,
    SH.datatype,
    SH["in"],
    SH.minInclusive,
    SH.maxInclusive,
}
_DATATYPES = {
    XSD.string,
    XSD.boolean,
    XSD.integer,
    XSD.decimal,
    XSD.double,
    XSD.float,
    XSD.date,
    XSD.dateTime,
    XSD.int,
    XSD.nonNegativeInteger,
}


def _shapes(graph):
    _terms(graph, shapes=True)
    nodes = set(graph.subjects(RDF.type, SH.NodeShape))
    properties = set(graph.objects(None, SH.property))
    if any(not isinstance(n, URIRef) for n in nodes | properties) or nodes & properties:
        raise SemanticError("UNSUPPORTED_BLANK_NODE")
    # Diagnose the actual template field before the generic whole-graph whitelist.
    # A non-IRI target/datatype is not a complex path. Only the structurally proven
    # inverse form is classified here; unclassified anonymous paths fail safely.
    for value in graph.objects(None, SH.targetClass):
        if not isinstance(value, URIRef):
            raise SemanticError("SHAPE_TARGET_CLASS_INVALID")
    for value in graph.objects(None, SH.datatype):
        if not isinstance(value, URIRef):
            raise SemanticError("SHAPE_DATATYPE_INVALID")
    for value in graph.objects(None, SH.path):
        if isinstance(value, URIRef):
            continue
        if isinstance(value, Literal):
            raise SemanticError("SHAPE_PATH_INVALID")
        triples = list(graph.triples((value, None, None)))
        if (
            len(triples) == 1
            and triples[0][1] == SH.inversePath
            and isinstance(triples[0][2], URIRef)
        ):
            raise SemanticError("UNSUPPORTED_SHACL_PATH")
        raise SemanticError("SHAPE_PATH_UNCLASSIFIED")
    lists = set()
    for head in graph.objects(None, SH["in"]):
        visited = set()
        while head != RDF.nil:
            if not isinstance(head, BNode) or head in visited:
                raise SemanticError("INVALID_SHAPE_LIST")
            visited.add(head)
            lists.add(head)
            first = list(graph.objects(head, RDF.first))
            rest = list(graph.objects(head, RDF.rest))
            if len(first) != 1 or len(rest) != 1 or not isinstance(first[0], URIRef | Literal):
                raise SemanticError("INVALID_SHAPE_LIST")
            head = rest[0]
    for s, p, o in graph:
        if s in lists and p in {RDF.first, RDF.rest}:
            continue
        if p == RDF.type and (
            (s in nodes and o == SH.NodeShape) or (s in properties and o == SH.PropertyShape)
        ):
            continue
        if p not in _SH_PREDICATES:
            raise SemanticError("UNSUPPORTED_SHACL")
        if p in {SH.targetClass, SH.property}:
            if s not in nodes or not isinstance(o, URIRef | BNode):
                raise SemanticError("INVALID_SHAPE")
        elif s not in properties:
            raise SemanticError("INVALID_SHAPE")
        if p == SH.datatype and o not in _DATATYPES:
            raise SemanticError("UNSUPPORTED_DATATYPE")
        if p in {SH.minCount, SH.maxCount} and (
            not isinstance(o, Literal)
            or o.datatype not in {XSD.integer, XSD.int}
            or type(o.toPython()) is not int
            or o.toPython() < 0
        ):
            raise SemanticError("INVALID_SHAPE")
        if p in {SH.minInclusive, SH.maxInclusive} and (
            not isinstance(o, Literal)
            or o.datatype not in {XSD.integer, XSD.int, XSD.decimal, XSD.float, XSD.double}
            or o.ill_typed
        ):
            raise SemanticError("INVALID_SHAPE")
    for node in nodes:
        if len(list(graph.objects(node, SH.targetClass))) != 1:
            raise SemanticError("INVALID_SHAPE")
    for node in properties:
        if len(list(graph.objects(node, SH.path))) != 1:
            raise SemanticError("INVALID_SHAPE")
        for p in _SH_PREDICATES - {SH.property}:
            if len(list(graph.objects(node, p))) > 1:
                raise SemanticError("INVALID_SHAPE")
    if not nodes:
        raise SemanticError("INVALID_SHAPE")


def check_shapes(data: Graph, shapes: Graph) -> dict:
    """Validate exactly the supplied asserted scope; return real pySHACL details."""
    with offline():
        local, constraints = _copy(data), _copy(shapes)
        _terms(local)
        _shapes(constraints)
        if any(p in {RDFS.subClassOf, RDFS.domain, RDFS.range} for _s, p, _o in local):
            # Even without inference pySHACL follows targetClass subclass paths.
            # Require an explicit asserted/derived fact scope, never mixed ontology.
            raise SemanticError("FACT_SCOPE_CONTAINS_AXIOMS")
        # Pin the real Validator API, bypassing validate()'s Graph/URL loader and
        # process-global temporary RDFLib boolean conversion monkeypatch.
        # No ontology loader, imports, metaSHACL, AF, JS or remote store path exists.
        conforms, report, _text_report = Validator(
            local,
            shacl_graph=constraints,
            ont_graph=None,
            options={
                "inference": "none",
                "advanced": False,
                "use_js": False,
                "iterate_rules": False,
                "inplace": False,
                "sparql_mode": False,
            },
        ).run()
        if not isinstance(report, Graph):
            raise SemanticError("VALIDATION_FAILED")
        violations = []
        for result in report.subjects(RDF.type, SH.ValidationResult):
            violations.append(
                {
                    "focus": report.value(result, SH.focusNode).n3(),
                    "path": report.value(result, SH.resultPath).n3(),
                    "constraint": report.value(result, SH.sourceConstraintComponent).n3(),
                    "sourceShape": report.value(result, SH.sourceShape).n3(),
                    "value": (
                        value.n3()
                        if (value := report.value(result, SH.value)) is not None
                        else None
                    ),
                    "severity": report.value(result, SH.resultSeverity).n3(),
                }
            )
        violations.sort(key=lambda row: tuple(str(v) for v in row.values()))
        return {"conforms": bool(conforms), "violations": violations}
