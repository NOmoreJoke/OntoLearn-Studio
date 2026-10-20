"""Pure selection projection, separate from generating a new reasoning result.

I03/I04 own authorization, content-addressed payload integrity, producer identity,
versions and snapshot/current/history binding. Local fingerprints only compare
provided producer context with these input graphs; they do not prove authority.
Projection never reevaluates rules or fills missing selected output/evidence.
"""

import hashlib
import json
from dataclasses import dataclass

from rdflib import OWL, RDF, RDFS, Graph, Literal, URIRef, Variable
from rdflib.plugins.parsers.notation3 import RDFSink, SinkParser

from ontolearn_engine.semantic import (
    MAX_TRIPLES,
    SEMANTICS_VERSION,
    Rule,
    _chain_warnings,
    _copy,
    _key,
    _rule,
    _terms,
    reason,
)
from ontolearn_engine.semantic_offline import SemanticError, offline

MAX_PROJECTION_ITEMS = 1_000_000


def _axiom(triple):
    _s, predicate, value = triple
    return predicate in {RDFS.subClassOf, RDFS.domain, RDFS.range} or (
        predicate == RDF.type
        and value in {OWL.Class, RDFS.Class, OWL.ObjectProperty, OWL.DatatypeProperty}
    )


def _digest(value):
    try:
        data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    except UnicodeEncodeError as error:
        raise SemanticError("INVALID_UNICODE") from error
    return hashlib.sha256(data).hexdigest()


def _inputs(asserted, ontology, include_derived, rules):
    if type(include_derived) is not bool:
        raise SemanticError("SCOPE_SELECTION_TYPE_INVALID")
    if not include_derived and rules != ():
        raise SemanticError("UNSELECTED_RULES_PRESENT")
    facts, axioms = _copy(asserted), _copy(ontology)
    _terms(facts)
    _terms(axioms)
    if any(_axiom(t) for t in facts):
        raise SemanticError("FACT_SCOPE_CONTAINS_AXIOMS")
    if any(not _axiom(t) and t[1] not in {RDFS.label, RDFS.comment} for t in axioms):
        raise SemanticError("ONTOLOGY_SCOPE_CONTAINS_FACTS")
    if type(rules) is not tuple or len(rules) > 100:
        raise SemanticError("INVALID_RULE")
    for rule in rules:
        _rule(rule)
    if len({r.id for r in rules}) != len(rules):
        raise SemanticError("INVALID_RULE")
    return facts, axioms


def _source(facts, axioms, rules):
    return {
        "executionSemanticsVersion": SEMANTICS_VERSION,
        "assertedInputSha256": _digest(sorted(_key(t) for t in facts)),
        "ontologyInputSha256": _digest(sorted(_key(t) for t in axioms)),
        "selectedRulesSha256": _digest(
            [
                {"id": r.id, "when": [_key(t) for t in r.when], "then": _key(r.then)}
                for r in sorted(rules, key=lambda r: r.id)
            ]
        ),
    }


class _LexicalSink(RDFSink):
    def newLiteral(self, text, datatype, language):
        return Literal(text, datatype=datatype, lang=language, normalize=False)


def _selected_output(result, original, rules):
    """Validate internal consistency, not authenticity or global completeness."""
    invalid = "REASONING_RESULT_INVALID"
    if type(result) is not dict or set(result) != {
        "rdfs",
        "rules",
        "warnings",
        "evidence",
        "rdfsEvidence",
    }:
        raise SemanticError(invalid)
    if any(type(value) is not list for value in result.values()):
        raise SemanticError(invalid)
    remaining = MAX_PROJECTION_ITEMS
    parsed = {}

    def charge(count=1):
        nonlocal remaining
        remaining -= count
        if remaining < 0:
            raise SemanticError("WORK_LIMIT")

    def row(value):
        charge()
        if (
            type(value) not in {list, tuple}
            or len(value) != 3
            or any(type(term) is not str for term in value)
        ):
            raise SemanticError(invalid)
        key = tuple(value)
        if key not in parsed:
            # Parse only a fixed in-memory Turtle row. The private sink preserves
            # original literal lexical forms; never toggle RDFLib global settings.
            if any(not (s.startswith("<") and s.endswith(">") or s.startswith('"')) for s in key):
                raise SemanticError(invalid)
            try:
                text = " ".join(key) + " ."
                text.encode("utf-8")
                graph = Graph()
                SinkParser(
                    _LexicalSink(graph), baseURI="urn:ontolearn:projection:", turtle=True
                ).loadBuf(text)
                if len(graph) != 1:
                    raise SemanticError(invalid)
                triple = next(iter(graph))
                _terms(graph)
                if _key(triple) != key:
                    raise SemanticError(invalid)
            except Exception as error:
                raise SemanticError(invalid) from error
            parsed[key] = triple
        return key

    def rows(value, *, nonempty=False):
        if type(value) is not list or (nonempty and not value):
            raise SemanticError(invalid)
        charge(len(value))
        return [row(item) for item in value]

    rdfs, derived = rows(result["rdfs"]), rows(result["rules"])
    if len(set(rdfs)) != len(rdfs) or len(set(derived)) != len(derived):
        raise SemanticError(invalid)
    rdfs_set, derived_set = set(rdfs), set(derived)
    original_rows = set(original)
    if rdfs_set & original_rows:
        raise SemanticError(invalid)
    proofs = {key: {key} for key in original_rows}
    rdfs_records = []
    for evidence in result["rdfsEvidence"]:
        charge()
        if type(evidence) is not dict or set(evidence) != {"result", "basis"}:
            raise SemanticError(invalid)
        key = row(evidence["result"])
        basis = rows(evidence["basis"], nonempty=True)
        triple = parsed[key]
        if key not in rdfs_set or key in proofs or len(set(basis)) != len(basis):
            raise SemanticError(invalid)
        if not set(basis) <= original_rows or triple[1] not in {RDF.type, RDFS.subClassOf}:
            raise SemanticError(invalid)
        if not isinstance(triple[0], URIRef) or not isinstance(triple[2], URIRef):
            raise SemanticError(invalid)
        proofs[key] = set(basis)
        rdfs_records.append((key, triple, sorted(basis)))
    if set(proofs) != original_rows | rdfs_set:
        raise SemanticError(invalid)
    selected = {r.id: r for r in rules}
    rule_records = []
    covered = set()
    seen_evidence = set()
    for evidence in result["evidence"]:
        charge()
        if type(evidence) is not dict or set(evidence) != {"rule", "result", "inputs", "basis"}:
            raise SemanticError(invalid)
        if type(evidence["rule"]) is not str or evidence["rule"] not in selected:
            raise SemanticError(invalid)
        rule = selected[evidence["rule"]]
        key = row(evidence["result"])
        inputs = rows(evidence["inputs"], nonempty=True)
        basis = rows(evidence["basis"], nonempty=True)
        if key not in derived_set or len(inputs) != len(rule.when):
            raise SemanticError(invalid)
        binding = {}
        for pattern, input_key in zip(rule.when, inputs, strict=True):
            if input_key not in proofs or parsed.get(input_key, original.get(input_key))[1] in {
                RDFS.label,
                RDFS.comment,
            }:
                raise SemanticError(invalid)
            input_triple = parsed.get(input_key, original.get(input_key))
            for expected, value in zip(pattern, input_triple, strict=True):
                if isinstance(expected, Variable):
                    if expected in binding and binding[expected] != value:
                        raise SemanticError(invalid)
                    binding[expected] = value
                elif expected != value:
                    raise SemanticError(invalid)
        triple = parsed[key]
        if tuple(binding.get(t, t) for t in rule.then) != triple or _axiom(triple):
            raise SemanticError(invalid)
        try:
            _rule(Rule(rule.id, (triple,), triple))
        except SemanticError as error:
            raise SemanticError(invalid) from error
        expected_basis = set().union(*(proofs[input_key] for input_key in inputs))
        if len(set(basis)) != len(basis) or set(basis) != expected_basis:
            raise SemanticError(invalid)
        identity = (rule.id, key, tuple(inputs))
        if identity in seen_evidence:
            raise SemanticError(invalid)
        seen_evidence.add(identity)
        covered.add(key)
        rule_records.append((key, triple, rule.id, inputs, sorted(basis)))
    if covered != derived_set or result["warnings"] != _chain_warnings(rules):
        raise SemanticError(invalid)
    return rdfs_records, rule_records


@dataclass(frozen=True)
class ValidationScope:
    facts: Graph
    ontology: Graph
    provenance: dict
    reasoning_result: dict | None


def project_validation_scope(
    asserted: Graph,
    ontology: Graph,
    *,
    include_derived: bool,
    reasoning_result: dict | None = None,
    reasoning_source: dict | None = None,
    rules: tuple[Rule, ...] = (),
) -> ValidationScope:
    """Project the explicit existing selection without generating another result.

    reasoning_source is private producer-context metadata, not a new public DTO
    or proof of authorization. I04 must derive it from verified producer inputs
    and definitions; hashes claimed by a caller are insufficient provenance.
    Missing/inconsistent selections stop; no reason() invocation occurs here.
    """
    with offline():
        facts, axioms = _inputs(asserted, ontology, include_derived, rules)
        source = _source(facts, axioms, rules)
        original_facts = sorted(_key(t) for t in facts)
        sources = {key: [{"kind": "asserted"}] for key in original_facts}
        derived_axioms = []
        if not include_derived:
            if reasoning_result is not None or reasoning_source is not None:
                raise SemanticError("UNSELECTED_REASONING_PRESENT")
        else:
            if type(reasoning_source) is not dict or reasoning_source != source:
                raise SemanticError("REASONING_SOURCE_MISMATCH")
            original = {_key(t): t for t in (*facts, *axioms)}
            rdfs_records, rule_records = _selected_output(reasoning_result, original, rules)
            for key, triple, basis in rdfs_records:
                record = {"kind": "rdfs", "basis": basis}
                if _axiom(triple):
                    axioms.add(triple)
                    derived_axioms.append({"triple": key, "source": record})
                else:
                    facts.add(triple)
                    sources.setdefault(key, []).append(record)
            for key, triple, rule_id, inputs, basis in rule_records:
                facts.add(triple)
                sources.setdefault(key, []).append(
                    {"kind": "rule", "rule": rule_id, "inputs": inputs, "basis": basis}
                )
            if len(facts) > MAX_TRIPLES or len(axioms) > MAX_TRIPLES:
                raise SemanticError("PROJECTION_RESULT_LIMIT")
        return ValidationScope(
            facts=facts,
            ontology=axioms,
            reasoning_result=reasoning_result,
            provenance={
                "scope": "asserted+selected-derived" if include_derived else "asserted",
                **source,
                "reasoningSource": dict(source) if include_derived else None,
                "selectedRuleIds": [r.id for r in sorted(rules, key=lambda r: r.id)],
                "warnings": list(reasoning_result["warnings"]) if include_derived else [],
                "selectedFacts": [
                    {"triple": key, "sources": sources[key]} for key in sorted(sources)
                ],
                "derivedAxioms": derived_axioms,
                "ontologyView": sorted(_key(t) for t in axioms),
                "factViewSha256": _digest(sorted(_key(t) for t in facts)),
                "ontologyViewSha256": _digest(sorted(_key(t) for t in axioms)),
            },
        )


def prepare_validation_scope(
    asserted: Graph,
    ontology: Graph,
    *,
    include_derived: bool,
    rules: tuple[Rule, ...] = (),
) -> ValidationScope:
    """Generate a new real result then project it; not an existing-result resolver."""
    with offline():
        facts, axioms = _inputs(asserted, ontology, include_derived, rules)
        source = _source(facts, axioms, rules) if include_derived else None
        result = None
        if include_derived:
            combined = _copy(facts)
            for triple in axioms:
                combined.add(triple)
            result = reason(combined, rules)
        return project_validation_scope(
            facts,
            axioms,
            include_derived=include_derived,
            reasoning_result=result,
            reasoning_source=source,
            rules=rules,
        )
