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
from ontolearn_engine.semantic_turtle import canonical_string, parse_graph

MAX_TEXT_BYTES = 1_048_576
MAX_TRIPLES = 100_000
MAX_RULE_MATCHES = 100_000
MAX_WORK = 1_000_000
SEMANTICS_VERSION = "i05-finite-6"
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
        result.add(tuple(canonical_string(term) for term in triple))
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


def _canonical_rule(rule):
    # Validate the original shape before touching any user-provided sequence.
    _rule(rule)
    return Rule(
        rule.id,
        tuple(tuple(canonical_string(term) for term in pattern) for pattern in rule.when),
        tuple(canonical_string(term) for term in rule.then),
    )


class ProfileReasonError(SemanticError):
    """Safe private diagnostic; callers own public classification and authority.

    A rule id identifies an actual one-rule compile/evaluate boundary only. It
    does not authenticate a definition, source, graph, or saved producer.
    """

    def __init__(
        self, reason, *, classification="input", location=None, rule_id=None, context="graph"
    ):
        super().__init__(reason)
        self.reason = reason
        self.classification = classification
        self.location = location
        self.rule_id = rule_id
        self.context = context


PROFILE_SEMANTICS_VERSION = "i05-finite-7"
PROFILE_RESULT_FORMAT = "i05-reasoning-result/2"
PROFILE_GRAPH_BUDGET_VERSION = "i05-profile-graph-budget/1"
_PROFILE_POOLS = {
    "work": 16_777_216,
    "input_bytes": 262_144,
    "output_bytes": 262_144,
    "trace_items": 8_192,
    "firings": 1_024,
    "head_occurrences": 16_384,
    "bindings": 1_024,
}


class _GraphBudget:
    """Deterministic graph work, separate from reserved mechanism children."""

    def __init__(self):
        self.work = 0
        self.input_bytes = 0
        self.keys = {}

    def debit(self, amount=1):
        if type(amount) is not int or amount < 0:
            raise ProfileReasonError("INTERNAL_ERROR", classification="internal")
        if amount > MAX_WORK - self.work:
            raise ProfileReasonError("WORK_LIMIT", classification="resource")
        self.work += amount

    def input_text(self, text):
        if type(text) is not str:
            raise ProfileReasonError("RDF_TERM_INVALID")
        # Check characters before allocating the UTF-8 representation.
        if len(text) > MAX_TEXT_BYTES - self.input_bytes:
            raise ProfileReasonError("GRAPH_INPUT_LIMIT", classification="resource")
        self.debit(len(text))
        try:
            size = len(text.encode("utf-8"))
        except UnicodeEncodeError:
            raise ProfileReasonError("INVALID_UNICODE") from None
        if size > MAX_TEXT_BYTES - self.input_bytes:
            raise ProfileReasonError("GRAPH_INPUT_LIMIT", classification="resource")
        self.input_bytes += size
        return size

    def key(self, triple):
        value = self.keys.get(triple)
        if value is None:
            self.debit(3 + sum(_term_characters(term) for term in triple))
            value = _key(triple)
            self.keys[triple] = value
        return value

    def ordered(self, values, *, key=None):
        result = []
        for value in values:
            self.debit()
            result.append(value)
        # Precharge comparison/key dispatches before allocating the sorted copy.
        self.debit(len(result) * max(1, len(result).bit_length()))
        return sorted(result, key=self.key if key is None else key)

    def union(self, sets):
        self.debit(sum(len(value) for value in sets))
        return set().union(*sets)


def _term_characters(term):
    return len(str(term)) + (
        len(str(term.datatype or "")) + len(term.language or "") if isinstance(term, Literal) else 0
    )


def _finite_closure(asserted, charge, meter=None, *, _direct_capture=None):
    """One closure implementation and one stable first-witness policy."""
    if _direct_capture is not None:
        from .semantic_profile_directsteps import _DirectStepsCapture

        if type(_direct_capture) is not _DirectStepsCapture:
            raise ProfileReasonError("INTERNAL_ERROR", classification="internal")
    ordered = sorted if meter is None else meter.ordered
    key = _key if meter is None else meter.key
    if meter is not None:
        meter.debit(1 + 4 * len(asserted))
    closure = _copy(asserted)
    proofs = {triple: {triple} for triple in asserted}
    changed = True
    while changed:
        additions = []

        def append(triple, inputs, rule, _additions=additions):
            if meter is not None:
                meter.debit(1 + len(inputs))
            if _direct_capture is None:
                _additions.append((triple, inputs))
            else:
                _direct_capture.candidate(rule)
                # Native candidate, borrowed original sort keys and their slots.
                _direct_capture.ledger.reserve("objects", 8)
                _additions.append([triple, inputs, rule, None])

        for child, _, parent in ordered(closure.triples((None, RDFS.subClassOf, None)), key=key):
            for s, _, _o in ordered(closure.triples((None, RDF.type, child)), key=key):
                charge()
                append(
                    (s, RDF.type, parent),
                    [(s, RDF.type, child), (child, RDFS.subClassOf, parent)],
                    "rdfs9-type-via-subclass",
                )
            for _p, _, ancestor in closure.triples((parent, RDFS.subClassOf, None)):
                charge()
                append(
                    (child, RDFS.subClassOf, ancestor),
                    [(child, RDFS.subClassOf, parent), (parent, RDFS.subClassOf, ancestor)],
                    "rdfs11-subclass-transitive",
                )
        for predicate, relation, target in ordered(closure, key=key):
            if relation in {RDFS.domain, RDFS.range} and predicate not in {
                RDFS.label,
                RDFS.comment,
            }:
                for s, _, o in closure.triples((None, predicate, None)):
                    charge()
                    subject = s if relation == RDFS.domain else o
                    if isinstance(subject, URIRef):
                        append(
                            (subject, RDF.type, target),
                            [(predicate, relation, target), (s, predicate, o)],
                            "rdfs2-domain" if relation == RDFS.domain else "rdfs3-range",
                        )
        changed = False

        def addition_key(item):
            value = (key(item[0]), tuple(key(t) for t in item[1]))
            if _direct_capture is not None:
                item[3] = value
            return value

        for item in ordered(additions, key=addition_key):
            triple, inputs = item[:2] if _direct_capture is not None else item
            if triple not in closure:
                # Profile rejects before insertion/allocation. Legacy keeps its
                # original post-insertion limit and error identity.
                if meter is not None:
                    if len(closure) >= MAX_TRIPLES:
                        raise ProfileReasonError(
                            "RDFS_RESULT_LIMIT", classification="resource", context="closure"
                        )
                    meter.debit()
                    basis = meter.union([proofs[i] for i in inputs])
                else:
                    basis = set().union(*(proofs[i] for i in inputs))
                if _direct_capture is not None:
                    _direct_capture.insert(item[3][0], item[3][1], item[2])
                closure.add(triple)
                proofs[triple] = basis
                changed = True
                if len(closure) > MAX_TRIPLES:
                    raise SemanticError("RDFS_RESULT_LIMIT")
        if _direct_capture is not None:
            count = len(additions)
            additions = item = inputs = triple = basis = append = addition_key = None
            _direct_capture.end_candidates(count)
            _direct_capture.ledger.release("objects", 8 * count)
    return closure, proofs


def _finite_matches(closure, patterns, charge, limit, meter=None):
    """Real ordered graph join, shared by both explicit language modes."""
    ordered = sorted if meter is None else meter.ordered
    key = _key if meter is None else meter.key
    if meter is not None:
        meter.debit()
    matches = [({}, [])]
    for pattern in patterns:
        next_matches = []
        for binding, inputs in matches:
            if meter is not None:
                meter.debit(3)
            lookup = tuple(binding.get(t) if isinstance(t, Variable) else t for t in pattern)
            for triple in ordered(closure.triples(lookup), key=key):
                charge()
                if triple[1] in {RDFS.label, RDFS.comment}:
                    continue
                if meter is not None:
                    meter.debit(len(binding) + 3)
                updated = dict(binding)
                for expected, value in zip(pattern, triple, strict=True):
                    if isinstance(expected, Variable):
                        if expected in updated and updated[expected] != value:
                            break
                        updated[expected] = value
                else:
                    if meter is not None:
                        # Limit before copying inputs or appending the binding.
                        if len(next_matches) >= limit:
                            raise ProfileReasonError(
                                "RULE_INPUT_BUDGET", classification="resource", context="rule"
                            )
                        meter.debit(1 + len(inputs))
                    next_matches.append((updated, [*inputs, triple]))
                    if meter is None and len(next_matches) > limit:
                        raise SemanticError("RULE_MATCH_WORK_LIMIT")
        matches = next_matches
    return matches


def _legacy_reason(graph, rules):
    asserted = _copy(graph)
    _terms(asserted)
    if not isinstance(rules, tuple) or len(rules) > 100:
        raise SemanticError("INVALID_RULE")
    if any(not isinstance(rule, Rule) for rule in rules):
        raise SemanticError("INVALID_RULE")
    rules = tuple(_canonical_rule(rule) for rule in rules)
    if len({r.id for r in rules}) != len(rules):
        raise SemanticError("INVALID_RULE")
    work = 0

    def charge():
        nonlocal work
        work += 1
        if work > MAX_WORK:
            raise SemanticError("WORK_LIMIT")

    closure, proofs = _finite_closure(asserted, charge)
    derived = Graph()
    evidence = []
    for rule in sorted(rules, key=lambda r: r.id):
        matches = _finite_matches(closure, rule.when, charge, MAX_RULE_MATCHES)
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
                        _key(t) for t in sorted(set().union(*(proofs[t] for t in inputs)), key=_key)
                    ],
                }
            )
    rdfs = set(closure) - set(asserted)
    return {
        "rdfs": sorted(_key(t) for t in rdfs),
        "warnings": _chain_warnings(rules),
        "rules": sorted(_key(t) for t in derived),
        "evidence": evidence,
        "rdfsEvidence": [
            {"result": _key(t), "basis": [_key(i) for i in sorted(proofs[t], key=_key)]}
            for t in sorted(rdfs, key=_key)
        ],
    }


def _profile_failure(error, *, rule_id=None, context="graph"):
    return ProfileReasonError(
        error.reason,
        classification=error.classification,
        location=error.location,
        rule_id=rule_id,
        context=context,
    )


def _profile_semantic_failure(error, *, context="graph", location=None, rule_id=None):
    resource_codes = {
        "GRAPH_INPUT_LIMIT",
        "TEXT_INPUT_LIMIT",
        "RULE_INPUT_BUDGET",
        "WORK_LIMIT",
        "RDFS_RESULT_LIMIT",
        "RULE_MATCH_WORK_LIMIT",
        "RULE_EVIDENCE_RESULT_LIMIT",
    }
    return ProfileReasonError(
        error.code,
        context=context,
        location=location,
        rule_id=rule_id,
        classification=(
            "resource"
            if error.code in resource_codes
            else "internal"
            if error.code == "PROFILE_CONTEXT_INVALID"
            else "input"
        ),
    )


def _profile_iri(text, *, context="graph", location=None, rule_id=None):
    from ontolearn_engine.semantic_turtle import validate_profile_iri

    try:
        validate_profile_iri(text)
    except SemanticError as error:
        raise _profile_semantic_failure(
            error, context=context, location=location, rule_id=rule_id
        ) from None


def _profile_definitions(rules, meter):
    from ontolearn_engine.quality.rule_firing import RuleSpec
    from ontolearn_engine.quality.rule_profile import ProfileLimits

    if type(rules) is not tuple or len(rules) > 100:
        raise ProfileReasonError("INVALID_RULE")
    meter.debit(len(rules))
    ids = set()
    for spec in rules:
        if type(spec) is not RuleSpec or type(spec.rule_id) is not str or not spec.rule_id:
            raise ProfileReasonError("INVALID_RULE")
        if len(spec.rule_id) > ProfileLimits().term_bytes:
            raise ProfileReasonError("RULE_INPUT_BUDGET", classification="resource")
        size = meter.input_text(spec.rule_id)
        if size > ProfileLimits().term_bytes:
            raise ProfileReasonError("RULE_INPUT_BUDGET", classification="resource")
        if spec.rule_id in ids:
            raise ProfileReasonError("INVALID_RULE")
        ids.add(spec.rule_id)
    meter.debit(sum(len(spec.rule_id) for spec in rules) * max(1, len(rules).bit_length()))
    return tuple(sorted(enumerate(rules), key=lambda item: item[1].rule_id)), ids


def _profile_catalog(graph, supplied, meter):
    from ontolearn_engine.quality.rule_firing import Catalog

    groups = []
    for categories in ((OWL.Class, RDFS.Class), (OWL.ObjectProperty,), (OWL.DatatypeProperty,)):
        members = set()
        for category in categories:
            for subject, _, _ in graph.triples((None, RDF.type, category)):
                meter.debit(1 + _term_characters(subject))
                if type(subject) is not URIRef:
                    raise ProfileReasonError("INVALID_RULE")
                _profile_iri(str(subject), context="catalog")
                members.add(str(subject))
        meter.debit(sum(map(len, members)) * max(1, len(members).bit_length()))
        groups.append(tuple(sorted(members)))
    actual = Catalog(*groups)
    meter.debit(sum(map(len, groups)))
    if set(actual.object_properties).intersection(actual.data_properties):
        raise ProfileReasonError("INVALID_ONTOLOGY_CATALOG", context="catalog")
    if supplied is not None:
        if type(supplied) is not Catalog:
            raise ProfileReasonError("INVALID_RULE")
        # Do not sort arbitrary caller collections before exact shape/length gates.
        for proposed, real in zip(
            (supplied.classes, supplied.object_properties, supplied.data_properties),
            groups,
            strict=True,
        ):
            if type(proposed) is not tuple or len(proposed) != len(real):
                raise ProfileReasonError("INVALID_RULE")
            if any(type(value) is not str for value in proposed):
                raise ProfileReasonError("INVALID_RULE")
            for value in proposed:
                meter.input_text(value)
                _profile_iri(value, context="catalog")
            meter.debit(sum(map(len, proposed)) * max(1, len(proposed).bit_length()))
            if len(set(proposed)) != len(proposed) or tuple(sorted(proposed)) != real:
                raise ProfileReasonError("INVALID_RULE")
    return actual


def _profile_graph(graph, context, meter):
    from ontolearn_engine.quality.rule_profile import Budget, ProfileFailure, ProfileLimits
    from ontolearn_engine.quality.rule_terms import parse_value
    from ontolearn_engine.semantic_turtle import (
        ProfileTermContext,
        profile_context_for_graph,
    )

    if type(graph) is not Graph or type(graph.store) is not Memory:
        raise ProfileReasonError("IN_MEMORY_GRAPH_REQUIRED")
    if len(graph) > MAX_TRIPLES:
        raise ProfileReasonError("GRAPH_INPUT_LIMIT", classification="resource")
    # Count actual entry bytes before copying, hashing, sorting or context checks.
    maximum_field_width = 1
    for triple in graph:
        meter.debit(4)
        for term in triple:
            if type(term) not in (URIRef, Literal):
                raise ProfileReasonError(
                    "UNSUPPORTED_BLANK_NODE" if isinstance(term, BNode) else "RDF_TERM_INVALID"
                )
            meter.input_text(str(term))
            maximum_field_width = max(maximum_field_width, 7 + _term_characters(term))
            if type(term) is Literal:
                if term.datatype is not None:
                    meter.input_text(str(term.datatype))
                if term.language is not None:
                    meter.input_text(term.language)
    if context is None:
        occurrences = 3 * len(graph)
        meter.debit(occurrences * max(1, occurrences.bit_length()) * maximum_field_width)
        context = profile_context_for_graph(graph)
    if type(context) is not ProfileTermContext:
        raise ProfileReasonError("PROFILE_CONTEXT_INVALID", classification="internal")
    preparation_work, validation_work, lookup_work = context.work_costs()
    meter.debit(preparation_work + validation_work)
    context.validate_graph(graph)
    seen = set()
    allowed_owl = {OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty}
    allowed_rdfs = {RDFS.Class, RDFS.subClassOf, RDFS.domain, RDFS.range, RDFS.label, RDFS.comment}
    for s, p, o in graph:
        meter.debit(3)
        if type(s) is not URIRef or type(p) is not URIRef:
            raise ProfileReasonError("RDF_TERM_INVALID")
        for term in (s, p, o):
            if term in seen:
                continue
            meter.debit()
            seen.add(term)
            if type(term) is URIRef:
                iri = str(term)
                meter.debit(len(iri))
                _profile_iri(iri)
                if iri.startswith(str(OWL)) and term not in allowed_owl:
                    raise ProfileReasonError(
                        "EXTERNAL_ACCESS_DENIED" if term == OWL.imports else "UNSUPPORTED_OWL"
                    )
                if iri.startswith(str(RDFS)) and term not in allowed_rdfs:
                    raise ProfileReasonError("UNSUPPORTED_RDFS")
                if iri.startswith(str(SH)):
                    raise ProfileReasonError("UNSUPPORTED_SHACL")
        if p in {RDFS.subClassOf, RDFS.domain, RDFS.range} and type(o) is not URIRef:
            raise ProfileReasonError("RDFS_TERM_INVALID")
        if p == RDF.type and type(o) is not URIRef:
            raise ProfileReasonError("RDF_TYPE_OBJECT_INVALID")
    meter.debit(len(seen))
    actual_terms = {canonical_string(term) for term in seen}
    # Preserve and validate all actual spellings/sources of graph terms, including
    # plain/explicit-string aliases. Parser-only prefix metadata is not a fact.
    entry_values = []
    for occurrence in context.occurrences:
        meter.debit()
        if canonical_string(occurrence.term) not in actual_terms:
            continue
        value = occurrence.value
        for iri in (value.lexical_form if value.kind == "iri" else None, value.datatype_iri):
            if iri is not None:
                meter.debit(len(iri))
                _profile_iri(iri)
        meter.debit()
        entry_values.append(value)
    # Finish all graph preflight charges before this continuous parse phase.
    # Its one Budget receives only the graph pool's actual remaining work. No
    # other graph charge interleaves, so both remaining counters stay aligned.
    entry = Budget(ProfileLimits(work=MAX_WORK - meter.work, output_bytes=0))
    for value in entry_values:
        previous = dict(entry.usage)["work"]
        try:
            parse_value(value, None, entry)
        except ProfileFailure as error:
            if error.reason == "INVALID_RULE" and error.classification == "input":
                raise ProfileReasonError("RDF_TERM_INVALID", context="graph") from None
            raise _profile_failure(error) from None
        finally:
            meter.debit(dict(entry.usage)["work"] - previous)
    meter.debit(1 + 3 * len(graph))
    return _copy(graph), context, entry, lookup_work


def _profile_term(term):
    """Convert already-compiled constants; never use host value conversion."""
    from ontolearn_engine.quality.rule_firing import Variable as ProfileVariable

    if type(term) is ProfileVariable:
        return Variable(term.name[1:])
    if term.kind == "iri":
        return URIRef(term.lexical_form)
    if term.language_raw:
        return Literal(term.lexical_form, lang=term.language_raw, normalize=False)
    return canonical_string(
        Literal(
            term.lexical_form,
            datatype=URIRef(term.datatype_iri) if term.datatype_iri is not None else None,
            normalize=False,
        )
    )


def _profile_as_term(term, meter):
    from ontolearn_engine.quality.rule_firing import Variable as ProfileVariable

    if type(term) is ProfileVariable:
        characters = len(term.name)
    else:
        characters = sum(
            len(value)
            for value in (term.lexical_form, term.datatype_iri, term.language_raw)
            if value is not None
        )
    meter.debit(4 + characters)
    return _profile_term(term)


def _profile_patterns(spec, meter):
    meter.debit(3 * len(spec.when))
    return tuple(
        tuple(_profile_as_term(term, meter) for term in (p.subject, p.predicate, p.object))
        for p in spec.when
    )


def _profile_rule_iris(spec, meter):
    from ontolearn_engine.quality.rule_firing import Comparison
    from ontolearn_engine.quality.rule_firing import Triple as ProfileTriple
    from ontolearn_engine.quality.rule_profile import InputLocation, TermInput

    # Structural validation remains the one T05 compiler's responsibility. This
    # extra lexical gate only strengthens actual IRI grammar before that call.
    for section, items, item_type in (
        ("when", spec.when, ProfileTriple),
        ("comparison", spec.comparisons, Comparison),
        ("head", spec.heads, ProfileTriple),
    ):
        limit = {"when": 16, "comparison": 32, "head": 16}[section]
        if type(items) is not tuple or len(items) > limit:
            continue
        for index, item in enumerate(items):
            if type(item) is not item_type:
                continue
            terms = (
                (("left", item.left), ("right", item.right))
                if section == "comparison"
                else (
                    (None, item.subject),
                    (None, item.predicate),
                    (None, item.object),
                )
            )
            for side, term in terms:
                if type(term) is not TermInput:
                    continue
                location = InputLocation(section, index, side)
                for iri in (term.lexical_form if term.kind == "iri" else None, term.datatype_iri):
                    if iri is not None and type(iri) is str:
                        meter.input_text(iri)
                        _profile_iri(iri, context="rule", location=location, rule_id=spec.rule_id)


def _profile_chain_warnings(plans, meter):
    # Potential chaining is advisory. Neither head facts nor warnings feed join.
    producers = []
    consumers = []
    for spec in plans:
        for head in spec.heads:
            meter.debit(3)
            producers.append(
                tuple(
                    _profile_as_term(t, meter) for t in (head.subject, head.predicate, head.object)
                )
            )
        for pattern in spec.when:
            meter.debit(3)
            consumers.append(
                (
                    spec.rule_id,
                    tuple(
                        _profile_as_term(t, meter)
                        for t in (pattern.subject, pattern.predicate, pattern.object)
                    ),
                )
            )
    warnings = set()
    for head in producers:
        for rule_id, pattern in consumers:
            meter.debit(3 + sum(_term_characters(t) for t in head + pattern))
            if all(
                isinstance(a, Variable) or isinstance(b, Variable) or a == b
                for a, b in zip(head, pattern, strict=True)
            ):
                warnings.add("RULE_CHAIN_UNSUPPORTED:" + rule_id)
    return meter.ordered(warnings, key=lambda value: value)


def _profile_reason(graph, rules, catalog, term_context, *, _capture=None):
    from dataclasses import asdict
    from hashlib import sha256

    from ontolearn_engine.quality.rule_firing import (
        BindingMatch,
        compile_rules,
        evaluate_bound_batch,
    )
    from ontolearn_engine.quality.rule_firing import (
        Triple as ProfileTriple,
    )
    from ontolearn_engine.quality.rule_profile import PROFILE, Budget, ProfileFailure, ProfileLimits

    if _capture is not None:
        from ontolearn_engine.semantic_profile_production import _ProductionCapture

        if type(_capture) is not _ProductionCapture:
            raise ProfileReasonError("INTERNAL_ERROR", classification="internal")

    meter = _GraphBudget()
    try:
        ordered_specs, ids = _profile_definitions(rules, meter)
    except ProfileReasonError as error:
        if error.reason != "WORK_LIMIT":
            error.context = "rule"
        raise
    if _capture is not None:
        _capture.definitions(ordered_specs, rules)
    asserted, context, entry, lookup_work = _profile_graph(graph, term_context, meter)

    def actual_term(term):
        meter.debit(lookup_work + 32 + 8 * _term_characters(term))
        return context.term_input(term)

    disabled = context.disabled_rule_ids
    if type(disabled) is not tuple or len(disabled) > len(rules):
        raise ProfileReasonError("INVALID_RULE", context="rule")
    disabled_set = set()
    for rule_id in disabled:
        if type(rule_id) is not str or rule_id not in ids or rule_id in disabled_set:
            raise ProfileReasonError("INVALID_RULE", context="rule")
        meter.debit(1 + len(rule_id))
        disabled_set.add(rule_id)
    if _capture is not None:
        _capture.context(disabled)
    try:
        actual_catalog = _profile_catalog(asserted, catalog, meter)
    except ProfileReasonError as error:
        error.context = "catalog"
        raise
    except ProfileFailure as error:
        raise _profile_failure(error, context="catalog") from None
    except SemanticError as error:
        raise _profile_semantic_failure(error, context="catalog") from None
    if _capture is not None:
        _capture.catalog(actual_catalog)
    plans = []
    count = max(1, len(ordered_specs))
    for position, (ordinal, spec) in enumerate(ordered_specs or ((None, None),)):
        limits = ProfileLimits(
            **{
                name: divmod(total, count)[0] + (position < divmod(total, count)[1])
                for name, total in _PROFILE_POOLS.items()
            }
        )
        if _capture is not None:
            _capture.allocation(spec, ordinal, limits)
        budget = Budget(limits)
        meter.debit(2)
        child_definitions = () if spec is None else (spec,)
        if spec is not None:
            _profile_rule_iris(spec, meter)
        try:
            plan = compile_rules(child_definitions, actual_catalog, budget)
        except ProfileFailure as error:
            raise _profile_failure(
                error,
                rule_id=(
                    spec.rule_id
                    if spec is not None
                    and (error.location is not None or error.classification != "resource")
                    else None
                ),
                context="rule",
            ) from None
        meter.debit()
        plans.append((ordinal, spec, plan, budget, child_definitions))
    # All definitions (including disabled/zero-match) compiled before closure/join.
    direct = None if _capture is None else _capture.direct_capture
    closure, proofs = _finite_closure(asserted, meter.debit, meter, _direct_capture=direct)
    leaf_ids = {}
    leaf_records = []
    for triple in meter.ordered(asserted):
        key = meter.key(triple)
        meter.debit(1 + sum(map(len, key)))
        raw = ("i05-profile-proof-leaf/1\0" + "\0".join(key)).encode("utf-8")
        meter.debit(len(raw))
        reference = "i05-proof:" + sha256(raw).hexdigest()
        meter.debit(2)
        leaf_ids[triple] = reference
        leaf_records.append({"reference": reference, "triple": key})
        if direct is not None:
            direct.link_seed(key, reference)
    mechanism_batches = []
    firings = []
    derived = set()
    evidence = []
    for ordinal, spec, plan, budget, child_definitions in plans:
        inactive = spec is not None and spec.rule_id in disabled_set
        batch = None
        original_matches = None
        if not inactive:
            matches = (
                []
                if spec is None
                else _finite_matches(
                    closure,
                    _profile_patterns(spec, meter),
                    meter.debit,
                    budget.limits.bindings,
                    meter,
                )
            )
            controlled = []
            for binding, inputs in matches:
                meter.debit(1 + len(binding) + 4 * len(inputs))
                proof_refs = []
                actual_when = []
                for triple in inputs:
                    meter.debit(1 + len(proofs[triple]))
                    proof_refs.append(
                        tuple(
                            meter.ordered(
                                (leaf_ids[leaf] for leaf in proofs[triple]), key=lambda value: value
                            )
                        )
                    )
                    actual_when.append(ProfileTriple(*(actual_term(t) for t in triple)))
                meter.debit(len(binding) * max(1, len(binding).bit_length()))
                controlled.append(
                    BindingMatch(
                        spec.rule_id,
                        tuple(
                            ("?" + str(var), actual_term(value))
                            for var, value in sorted(binding.items(), key=lambda pair: str(pair[0]))
                        ),
                        tuple(actual_when),
                        tuple(proof_refs),
                    )
                )
            try:
                meter.debit(1 + len(controlled))
                original_matches = tuple(controlled)
                batch = evaluate_bound_batch(plan, original_matches, budget)
            except ProfileFailure as error:
                raise _profile_failure(
                    error, rule_id=None if spec is None else spec.rule_id, context="rule"
                ) from None
            meter.debit(len(batch.firings) + len(batch.facts))
            for firing in batch.firings:
                firing_index = len(firings)
                meter.debit(1 + len(firing.when) + len(firing.basis))
                firings.append(firing)
                for head in firing.heads:
                    triple = tuple(
                        _profile_as_term(term, meter)
                        for term in (head.triple.subject, head.triple.predicate, head.triple.object)
                    )
                    meter.debit(1 + len(firing.when) + len(firing.basis))
                    derived.add(triple)
                    evidence.append(
                        {
                            "rule": firing.rule_id,
                            "firingIndex": firing_index,
                            "headIndex": head.index,
                            "result": meter.key(triple),
                            "inputs": [
                                meter.key(
                                    tuple(
                                        _profile_as_term(term, meter)
                                        for term in (t.subject, t.predicate, t.object)
                                    )
                                )
                                for t in firing.when
                            ],
                            "basis": firing.basis,
                        }
                    )
        meter.debit(6 + len(child_definitions))
        mechanism_batches.append(
            {
                "ruleId": None if spec is None else spec.rule_id,
                "definitionOrdinal": ordinal,
                "disabled": inactive,
                "planDigest": plan.digest,
                "batch": batch,
                "originalMatches": original_matches,
                "definitions": child_definitions,
                "catalog": actual_catalog,
                "limits": budget.limits,
                "budgetLimits": asdict(budget.limits),
                "budgetUsage": dict(budget.usage),
            }
        )
    meter.debit(len(closure) + len(asserted))
    rdfs = set(closure) - set(asserted)
    rdfs_evidence = []
    for triple in meter.ordered(rdfs):
        meter.debit(1 + len(proofs[triple]))
        rdfs_evidence.append(
            {
                "result": meter.key(triple),
                "basis": [meter.key(leaf) for leaf in meter.ordered(proofs[triple])],
                "proofLeaves": tuple(
                    meter.ordered(
                        (leaf_ids[leaf] for leaf in proofs[triple]), key=lambda value: value
                    )
                ),
            }
        )
    warnings = _profile_chain_warnings(
        tuple(spec for _, spec in ordered_specs if spec.rule_id not in disabled_set), meter
    )
    term_sources = []
    for occurrence in context.occurrences:
        meter.debit(1 + _term_characters(occurrence.term))
        term_sources.append(
            {
                "term": occurrence.term.n3(),
                "value": occurrence.value,
                "ordinal": occurrence.ordinal,
                "span": occurrence.span,
            }
        )
    # No public/JSON projection here. Typed batches/bytes and every occurrence
    # remain intact for the caller's one bounded serializer. No partial result
    # escapes if any later rule, graph projection or caller serialization fails.
    result = {
        "formatVersion": PROFILE_RESULT_FORMAT,
        "semanticsVersion": PROFILE_SEMANTICS_VERSION,
        "profile": PROFILE,
        "rdfs": [meter.key(t) for t in meter.ordered(rdfs)],
        "rules": [meter.key(t) for t in meter.ordered(derived)],
        "warnings": warnings,
        "evidence": evidence,
        "rdfsEvidence": rdfs_evidence,
        "firingGroups": tuple(firings),
        "mechanismBatches": tuple(mechanism_batches),
        "definitions": rules,
        "catalog": actual_catalog,
        "proofLeaves": tuple(leaf_records),
        "termSources": tuple(term_sources),
        "graphBudget": {
            "version": PROFILE_GRAPH_BUDGET_VERSION,
            "limits": {
                "work": MAX_WORK,
                "triples": MAX_TRIPLES,
                "inputTermBytes": MAX_TEXT_BYTES,
                "sidecarScalarBytes": 16_384,
                "sidecarTermBytes": 262_144,
            },
            "entryLimits": asdict(entry.limits),
            "entryUsage": dict(entry.usage),
        },
    }
    if direct is not None:
        result["directSteps"] = direct.finish()
        result["formatVersion"] = "i05-reasoning-result/3"
        result["semanticsVersion"] = "i05-finite-8"
    result["graphBudget"]["usage"] = {"work": meter.work, "inputTermBytes": meter.input_bytes}
    return result


def _reason_profile_core(graph, rules, catalog, term_context, capture):
    from ontolearn_engine.quality.rule_profile import ProfileFailure
    from ontolearn_engine.semantic_profile_directsteps import DirectStepsFailure
    from ontolearn_engine.semantic_profile_input import MaterialFailure

    try:
        return _profile_reason(graph, rules, catalog, term_context, _capture=capture)
    except (ProfileReasonError, DirectStepsFailure):
        raise
    except ProfileFailure as error:
        raise _profile_failure(error) from None
    except SemanticError as error:
        raise _profile_semantic_failure(error) from None
    except MaterialFailure:
        if capture is not None:
            raise
        raise ProfileReasonError("INTERNAL_ERROR", classification="internal") from None
    except Exception:
        # Unknown exception strings are never evidence for an error code.
        raise ProfileReasonError("INTERNAL_ERROR", classification="internal") from None


def _reason_profile_production(graph, rules, *, term_context, capture):
    from ontolearn_engine.semantic_profile_production import _ProductionCapture

    if type(capture) is not _ProductionCapture:
        raise ProfileReasonError("INTERNAL_ERROR", classification="internal")
    with offline():
        return _reason_profile_core(graph, rules, None, term_context, capture)


def reason(graph: Graph, rules=(), *, profile=None, catalog=None, term_context=None) -> dict:
    """Explicit legacy or fixed-profile reasoning over one frozen finite closure."""
    with offline():
        if profile is None:
            if catalog is not None or term_context is not None:
                raise SemanticError("INVALID_RULE")
            return _legacy_reason(graph, rules)
        from ontolearn_engine.quality.rule_profile import PROFILE

        if type(profile) is not str or profile != PROFILE:
            raise ProfileReasonError("RULE_POLICY_UNSUPPORTED", context="rule")
        return _reason_profile_core(graph, rules, catalog, term_context, None)


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
