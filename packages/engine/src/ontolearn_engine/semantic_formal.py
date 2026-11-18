"""Pure selection projection for formal FR-505 rules; legacy scopes unchanged.

semantic_scopes.project_validation_scope keeps serving every legacy rule/test.
Projects that carry formal FR-505 definitions (alone or mixed with legacy
rules) evaluate through the audited rule-profile engine, whose result shape
(comparison evidence, multi-conclusion heads, typed mechanism records) cannot
flow through the legacy structural re-verification. This module therefore
projects one already-authenticated immutable reasoning payload against the
canonical formal source, without re-running SPARQL, rules or reason().
"""

import hashlib
import json

from rdflib import RDF, RDFS, Graph
from rdflib.plugins.parsers.notation3 import SinkParser

from ontolearn_engine.semantic import (
    MAX_TRIPLES,
    PROFILE_SEMANTICS_VERSION,
    _copy,
    _key,
    _terms,
)
from ontolearn_engine.semantic_offline import SemanticError, offline
from ontolearn_engine.semantic_scopes import ValidationScope, _axiom
from ontolearn_engine.semantic_turtle import LexicalSink

MAX_PROJECTION_ITEMS = 1_000_000


def _digest(value):
    try:
        data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    except UnicodeEncodeError as error:
        raise SemanticError("INVALID_UNICODE") from error
    return hashlib.sha256(data).hexdigest()


def _term_record(term):
    """One canonical JSON record for a profile term; variables stay distinct."""
    from ontolearn_engine.quality.rule_firing import Variable

    if isinstance(term, Variable):
        return {"variable": term.name}
    if term.kind == "iri":
        return {"iri": term.lexical_form}
    record = {"literal": term.lexical_form}
    if term.datatype_iri is not None:
        record = {**record, "datatype": term.datatype_iri}
    if term.language_raw is not None:
        record = {**record, "language": term.language_raw}
    return record


def _pattern_record(pattern):
    return {
        "subject": _term_record(pattern.subject),
        "predicate": _term_record(pattern.predicate),
        "object": _term_record(pattern.object),
    }


def formal_source(facts, ontology, specs):
    """Canonical producer context for a project carrying formal FR-505 rules.

    The rules digest covers the compiled audited specs (conditions, comparisons
    and conclusions), so save order or editor formatting cannot change it.
    """
    return {
        "executionSemanticsVersion": PROFILE_SEMANTICS_VERSION,
        "assertedInputSha256": _digest(sorted(_key(t) for t in facts)),
        "ontologyInputSha256": _digest(sorted(_key(t) for t in ontology)),
        "selectedRulesSha256": _digest(
            [
                {
                    "id": spec.rule_id,
                    "when": [_pattern_record(p) for p in spec.when],
                    "comparisons": [
                        {
                            "left": _term_record(c.left),
                            "operator": c.operator,
                            "right": _term_record(c.right),
                        }
                        for c in spec.comparisons
                    ],
                    "heads": [_pattern_record(p) for p in spec.heads],
                }
                for spec in sorted(specs, key=lambda spec: spec.rule_id)
            ]
        ),
    }


def _selected_formal_output(result, original, specs):
    """Structurally bind one projected profile result; never re-evaluate it.

    Triples re-parse through the same bounded Turtle sink as the legacy
    projection. Rule evidence must name a compiled spec, match its triple
    patterns by input count, read only asserted-or-RDFS inputs and cite only
    asserted basis leaves. Comparison truth stays with the audited engine.
    """
    invalid = "REASONING_RESULT_INVALID"
    if type(result) is not dict or not {
        "rdfs",
        "rules",
        "warnings",
        "evidence",
        "rdfsEvidence",
    } <= set(result):
        raise SemanticError(invalid)
    if any(
        type(result[key]) is not list
        for key in ("rdfs", "rules", "warnings", "evidence", "rdfsEvidence")
    ):
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
                    LexicalSink(graph), baseURI="urn:ontolearn:formal:", turtle=True
                ).loadBuf(text)
                if len(graph) != 1:
                    raise SemanticError(invalid)
                triple = next(iter(graph))
                _terms(graph)
                if _key(triple) != key:
                    raise SemanticError(invalid)
            except SemanticError:
                raise
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
    if rdfs_set & original_rows or derived_set & original_rows or rdfs_set & derived_set:
        raise SemanticError(invalid)
    for warning in result["warnings"]:
        charge()
        if type(warning) is not str:
            raise SemanticError(invalid)

    rdfs_records = []
    rdfs_seen = set()
    for evidence in result["rdfsEvidence"]:
        charge()
        if type(evidence) is not dict or not {"result", "basis"} <= set(evidence):
            raise SemanticError(invalid)
        key = row(evidence["result"])
        basis = rows(evidence["basis"], nonempty=True)
        triple = parsed[key]
        if key not in rdfs_set or key in rdfs_seen or len(set(basis)) != len(basis):
            raise SemanticError(invalid)
        # Basis leaves must be asserted rows; predicate scoping mirrors the
        # legacy projection (rdf:type / rdfs:subClassOf derivations only).
        if not set(basis) <= original_rows or triple[1] not in {RDF.type, RDFS.subClassOf}:
            raise SemanticError(invalid)
        rdfs_seen.add(key)
        rdfs_records.append((key, triple, sorted(basis)))
    if rdfs_seen != rdfs_set:
        raise SemanticError(invalid)

    selected = {spec.rule_id: spec for spec in specs}
    rule_records = []
    covered = set()
    seen_evidence = set()
    for evidence in result["evidence"]:
        charge()
        if type(evidence) is not dict or not {"rule", "result", "inputs", "basis"} <= set(evidence):
            raise SemanticError(invalid)
        rule_id = evidence["rule"]
        if type(rule_id) is not str or rule_id not in selected:
            raise SemanticError(invalid)
        spec = selected[rule_id]
        key = row(evidence["result"])
        inputs = rows(evidence["inputs"], nonempty=True)
        basis = rows(evidence["basis"], nonempty=True)
        if key not in derived_set or len(inputs) != len(spec.when):
            raise SemanticError(invalid)
        if any(
            input_key not in original_rows and input_key not in rdfs_set for input_key in inputs
        ):
            raise SemanticError(invalid)
        if len(set(basis)) != len(basis) or not set(basis) <= original_rows:
            raise SemanticError(invalid)
        identity = (rule_id, key, tuple(inputs))
        if identity in seen_evidence:
            raise SemanticError(invalid)
        seen_evidence.add(identity)
        covered.add(key)
        rule_records.append((key, parsed[key], rule_id, inputs, sorted(basis)))
    if covered != derived_set:
        raise SemanticError(invalid)
    return rdfs_records, rule_records


def project_formal_validation_scope(asserted, ontology, *, specs, selected):
    """Project the explicit formal selection; no second rule evaluation occurs.

    selected is Store-authenticated producer material ({"metadata", "payload"}).
    Its payload must carry the exact canonical formal source computed from
    these graphs and compiled specs; the projected scope then merges asserted
    facts with the selected rdfs/rule outputs for downstream SPARQL/SHACL.
    """
    with offline():
        facts, axioms = _copy(asserted), _copy(ontology)
        _terms(facts)
        _terms(axioms)
        if any(_axiom(t) for t in facts):
            raise SemanticError("FACT_SCOPE_CONTAINS_AXIOMS")
        if any(not _axiom(t) and t[1] not in {RDFS.label, RDFS.comment} for t in axioms):
            raise SemanticError("ONTOLOGY_SCOPE_CONTAINS_FACTS")
        if type(specs) is not tuple or len(specs) > 100:
            raise SemanticError("INVALID_RULE")
        if len({spec.rule_id for spec in specs}) != len(specs):
            raise SemanticError("INVALID_RULE")
        source = formal_source(facts, axioms, specs)
        if (
            type(selected) is not dict
            or set(selected) != {"metadata", "payload"}
            or type(selected["payload"]) is not dict
            or selected["payload"].get("kind") != "reasoning"
            or selected["payload"].get("source") != source
        ):
            raise SemanticError("REASONING_SOURCE_MISMATCH")
        result = selected["payload"].get("reasoning")
        original = {_key(t): t for t in (*facts, *axioms)}
        rdfs_records, rule_records = _selected_formal_output(result, original, specs)
        original_facts = sorted(_key(t) for t in facts)
        sources = {key: [{"kind": "asserted"}] for key in original_facts}
        derived_axioms = []
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
            reasoning_result=result,
            provenance={
                "scope": "asserted+selected-derived",
                **source,
                "reasoningSource": dict(source),
                "selectedRuleIds": [
                    spec.rule_id for spec in sorted(specs, key=lambda s: s.rule_id)
                ],
                "warnings": list(result["warnings"]),
                "selectedFacts": [
                    {"triple": key, "sources": sources[key]} for key in sorted(sources)
                ],
                "derivedAxioms": derived_axioms,
                "ontologyView": sorted(_key(t) for t in axioms),
                "factViewSha256": _digest(sorted(_key(t) for t in facts)),
                "ontologyViewSha256": _digest(sorted(_key(t) for t in axioms)),
            },
        )
