"""Independent proposed JSON projection model. Standard library only; no engine imports.

Inputs are separately authored mathematical objects, never product returns. This is
neither a product decoder nor a test runner for the engine. Schema validation is the
explicit finite subset used by schema.json; case matching additionally requires every
exact registered value. No caller identity, allocation or capture is constructed.
"""

import hashlib
import itertools
import json
import re


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def exact(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(exact(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(exact(a, b) for a, b in zip(left, right))
    return left == right


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON member")
            result[key] = value
        return result

    def invalid_constant(_):
        raise ValueError("non-JSON numeric constant")

    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant)


def n3(term):
    """Our proposed total spelling for the approved finite typed RDF domain."""
    if term["kind"] == "iri":
        return "<" + term["value"] + ">"
    if term["kind"] == "blank":
        return "_:" + term["label"]
    value = json.dumps(term["lexical"], ensure_ascii=False)
    if term["language"] is not None:
        return value + "@" + term["language"]
    if term["datatype"] == "http://www.w3.org/2001/XMLSchema#string":
        return value
    return value + "^^<" + term["datatype"] + ">"


def triple(value):
    return [n3(term) for term in value]


def identity_term(term):
    if term["kind"] == "literal" and term["language"] is not None:
        return {**term, "language": term["language"].casefold()}
    return term


def graph(values):
    """A mathematical RDF set; serialization uses lexicographic N3 tuple order."""
    return sorted({tuple(triple([identity_term(t) for t in value])) for value in values})


def graph_json(values):
    return [list(value) for value in graph(values)]


def typed_graph(values):
    normalized = [[identity_term(t) for t in value] for value in values]
    unique = {tuple(triple(value)): value for value in normalized}
    return [unique[key] for key in sorted(unique)]


def legacy(math, warnings):
    witnesses = {tuple(triple(w["result"])): w for w in math["selectedWitnesses"]}
    added = graph_json(math["rdfsAdded"])
    records = []
    for match in math["matches"]:
        if not match["accepted"]:
            continue
        for head in match["heads"]:
            records.append({
                "rule": match["ruleId"],
                "result": triple(head["triple"]),
                "inputs": [triple(t) for t in match["when"]],
                "basis": graph_json(match["leafBasis"]),
            })
    # Evidence is an occurrence sequence. Sorting never deduplicates its members.
    records.sort(key=lambda r: (r["rule"], r["result"], r["inputs"], r["basis"]))
    return {
        "rdfs": added,
        "rules": graph_json(math["customOutput"]),
        "warnings": sorted(set(warnings)),
        "rdfsEvidence": [
            {"result": t, "basis": graph_json(witnesses[tuple(t)]["leafUnion"])}
            for t in added
        ],
        "evidence": records,
    }


def source_context(asserted, ontology, rules):
    return {
        "format": "i05-scope-content-source/1",
        "assertedDigest": digest({"domain": "i05-scope-facts/1", "graph": typed_graph(asserted)}),
        "ontologyDigest": digest({"domain": "i05-scope-ontology/1", "graph": typed_graph(ontology)}),
        "rulesDigest": digest({"domain": "i05-scope-rules/1", "rules": rules}),
    }


def view(facts, ontology):
    return {
        "factsCount": len(facts),
        "ontologyCount": len(ontology),
        "factsDigest": digest({"domain": "i05-scope-facts/1", "graph": typed_graph(facts)}),
        "ontologyDigest": digest({"domain": "i05-scope-ontology/1", "graph": typed_graph(ontology)}),
    }


def scope(expected, asserted_expected, dataset):
    """Construct a proposed mathematical record, not ValidationScope instances."""
    asserted = asserted_expected["facts"]
    ontology = asserted_expected["ontology"]
    derived = bool(expected["selectedRuleIds"])
    witnesses = []
    fact_sources = {tuple(triple(r["triple"])): r for r in expected["factSources"]}
    for result in expected["rdfsAdded"]:
        row = fact_sources.get(tuple(triple(result)))
        # This fixed scope has exactly one new subclass axiom, whose two leaves
        # are the entire separately authored input ontology, not inferred output.
        basis = row["basis"] if row else ontology
        witnesses.append({"result": result, "leafUnion": basis})
    math = {"rdfsAdded": expected["rdfsAdded"], "customOutput": expected["customOutput"],
            "matches": expected["matches"], "selectedWitnesses": witnesses}
    result = legacy(math, expected["warnings"]) if derived else None
    selected = []
    for row in sorted(expected["factSources"], key=lambda r: triple(r["triple"])):
        t = triple(row["triple"])
        if row["role"] == "rule":
            sources = [
                {"kind": "rule", "ruleId": e["rule"], "inputs": e["inputs"], "basis": e["basis"]}
                for e in result["evidence"] if e["result"] == t
            ]
        else:
            sources = [{"kind": row["role"], "basis": graph_json(row["basis"])}]
        selected.append({"triple": t, "sources": sources})
    axioms = [
        {"triple": triple(t), "source": {"kind": "rdfs", "basis": graph_json(ontology)}}
        for t in sorted(expected["derivedAxioms"], key=triple)
    ]
    return {
        "facts": typed_graph(expected["facts"]),
        "ontology": typed_graph(expected["ontology"]),
        "reasoning_result": result,
        "provenance": {
            "format": "i05-scope-observation-provenance/1",
            "selectedFacts": selected,
            "selectedRuleIds": expected["selectedRuleIds"],
            "warnings": expected["warnings"],
            "derivedAxioms": axioms,
            "views": {"asserted": view(asserted, ontology),
                      "selected": view(expected["facts"], expected["ontology"])},
            "reasoningSource": source_context(asserted, ontology, dataset["rules"]) if derived else None,
        },
    }


def rejection(origin, reason, harness_stage, classification=None, stage=None,
              slot=None, domain=None, complete=True):
    return {
        "kind": "rejection", "complete": complete, "harnessStage": harness_stage,
        "diagnostic": {"origin": origin, "reason": reason, "classification": classification,
                       "stage": stage, "slot": slot, "domain": domain,
                       "ruleId": None, "location": None},
        "partialView": None, "report": None,
    }


def unknown(harness_stage):
    return rejection("Unknown", "INTERNAL_ERROR", harness_stage, complete=False)


def safe_projection(diagnostic, harness_stage, schema):
    """Pure detached-record model, never introspection of an exception object.

    A real adapter must first establish exact trusted class identity; this function
    cannot prove that from JSON. It models schema rejection and safe fallback only.
    """
    proposed = {"kind": "rejection", "complete": True, "harnessStage": harness_stage,
                "diagnostic": diagnostic, "partialView": None, "report": None}
    if validate(proposed, schema):
        return proposed
    return unknown(harness_stage)


def validate(value, schema, root=None):
    """Finite JSON Schema 2020-12 subset used in this document's schema."""
    root = schema if root is None else root
    if "$ref" in schema:
        target = root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        return validate(value, target, root)
    if "oneOf" in schema:
        if sum(validate(value, option, root) for option in schema["oneOf"]) != 1:
            return False
    if "anyOf" in schema and not any(validate(value, option, root) for option in schema["anyOf"]):
        return False
    if "const" in schema and not exact(value, schema["const"]):
        return False
    if "enum" in schema and not any(exact(value, item) for item in schema["enum"]):
        return False
    kinds = {"null": type(None), "object": dict, "array": list, "string": str,
             "integer": int, "boolean": bool}
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(type(value) is kinds[kind] for kind in types):
            return False
    if type(value) is dict:
        if not set(schema.get("required", ())).issubset(value):
            return False
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False and not set(value).issubset(props):
            return False
        if any(key in props and not validate(item, props[key], root) for key, item in value.items()):
            return False
    if type(value) is list:
        if not schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", float("inf")):
            return False
        if schema.get("uniqueItems") and len({canonical(x) for x in value}) != len(value):
            return False
        for index, item in enumerate(value):
            prefix = schema.get("prefixItems", [])
            rule = prefix[index] if index < len(prefix) else schema.get("items", {})
            if rule is False or not validate(item, rule, root):
                return False
    if type(value) is str and "pattern" in schema and re.search(schema["pattern"], value) is None:
        return False
    if type(value) is int and not schema.get("minimum", value) <= value <= schema.get("maximum", value):
        return False
    return True


def matches(case, observed, schema):
    # A safe unknown or another known refusal can never pass a normal fixture.
    return validate(observed, schema) and exact(case["expectedProjection"], observed)


def graph_isomorphic(left, right):
    """Finite mathematical shape-list example only; never a product RDF parser.

    Every complete graph edge participates in a global BNode bijection. Caller
    separately preserves raw occurrence sequences; these are not RDF graph sets.
    """
    def blanks(rows):
        return sorted({t["label"] for row in rows for t in row if t["kind"] == "blank"})

    a, b = blanks(left), blanks(right)
    if len(a) != len(b) or len(a) > 8:
        return False
    target = {canonical(row) for row in right}
    for order in itertools.permutations(b):
        mapping = dict(zip(a, order))
        rewritten = [[{"kind": "blank", "label": mapping[t["label"]]} if t["kind"] == "blank"
                      else t for t in row] for row in left]
        if {canonical(row) for row in rewritten} == target:
            return True
    return False
