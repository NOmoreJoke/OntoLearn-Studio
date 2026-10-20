"""Pure fact/ontology views for explicitly selected SHACL input ranges.

This computes real finite inference from this call's copied inputs. It is not a
job/result-ID resolver: I03/I04 must validate persisted input and result identity.
No inferred axiom is smuggled into the validation fact graph or silently dropped.
"""

import hashlib
import json
from dataclasses import dataclass

from rdflib import OWL, RDF, RDFS, Graph
from rdflib.util import from_n3

from ontolearn_engine.semantic import SEMANTICS_VERSION, Rule, _copy, _key, _terms, reason
from ontolearn_engine.semantic_offline import SemanticError, offline


def _axiom(triple):
    _s, predicate, value = triple
    return predicate in {RDFS.subClassOf, RDFS.domain, RDFS.range} or (
        predicate == RDF.type
        and value in {OWL.Class, RDFS.Class, OWL.ObjectProperty, OWL.DatatypeProperty}
    )


def _digest(value):
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class ValidationScope:
    facts: Graph
    ontology: Graph
    provenance: dict
    reasoning_result: dict | None


def prepare_validation_scope(
    asserted: Graph,
    ontology: Graph,
    *,
    include_derived: bool,
    rules: tuple[Rule, ...] = (),
) -> ValidationScope:
    """Separate roles before validation; rules are the explicitly selected plan.

    Asserted-only does no inference. Derived scope computes RDFS then the selected
    one-pass rules and retains every inferred fact and all original assertions.
    Original and derived axioms stay in the separate ontology view with evidence.
    """
    with offline():
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
        original_facts = sorted(_key(t) for t in facts)
        original_axioms = sorted(_key(t) for t in axioms)
        sources = {row: [{"kind": "asserted"}] for row in original_facts}
        derived_axioms = []
        selected_rules = []
        warnings = []
        result = None
        if include_derived:
            combined = _copy(facts)
            for triple in axioms:
                combined.add(triple)
            result = reason(combined, rules)
            warnings = result["warnings"]
            selected_rules = [
                {"id": r.id, "when": [_key(t) for t in r.when], "then": _key(r.then)}
                for r in sorted(rules, key=lambda r: r.id)
            ]
            for evidence in result["rdfsEvidence"]:
                row = evidence["result"]
                triple = tuple(from_n3(t) for t in row)
                record = {"kind": "rdfs", "basis": evidence["basis"]}
                if _axiom(triple):
                    axioms.add(triple)
                    derived_axioms.append({"triple": row, "source": record})
                else:
                    facts.add(triple)
                    sources.setdefault(row, []).append(record)
            for evidence in result["evidence"]:
                row = evidence["result"]
                triple = tuple(from_n3(t) for t in row)
                # reason() already rejects schema rule output. Keep this invariant
                # explicit at the view boundary rather than filtering it silently.
                if _axiom(triple):
                    raise SemanticError("UNSUPPORTED_RULE_OUTPUT")
                facts.add(triple)
                sources.setdefault(row, []).append(
                    {
                        "kind": "rule",
                        "rule": evidence["rule"],
                        "inputs": evidence["inputs"],
                        "basis": evidence["basis"],
                    }
                )
        return ValidationScope(
            facts=facts,
            ontology=axioms,
            reasoning_result=result,
            provenance={
                "scope": "asserted+selected-derived" if include_derived else "asserted",
                "executionSemanticsVersion": SEMANTICS_VERSION,
                "assertedInputSha256": _digest(original_facts),
                "ontologyInputSha256": _digest(original_axioms),
                "selectedRulesSha256": _digest(selected_rules),
                "selectedRuleIds": [r["id"] for r in selected_rules],
                "warnings": warnings,
                "selectedFacts": [
                    {"triple": row, "sources": sources[row]} for row in sorted(sources)
                ],
                "derivedAxioms": derived_axioms,
                "ontologyView": sorted(_key(t) for t in axioms),
                "factViewSha256": _digest(sorted(_key(t) for t in facts)),
                "ontologyViewSha256": _digest(sorted(_key(t) for t in axioms)),
            },
        )
