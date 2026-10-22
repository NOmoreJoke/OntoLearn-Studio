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


HARNESS_STAGES = (
    "reason", "rule-definition", "scope", "restore", "structured-material-required",
    "parse-data", "parse-shapes", "scope-provenance-gate", "scope-selection-gate",
    "implicit-loader-guard", "check-shapes",
)
COLLECTION_FAILURE_STAGE = "collection-failure"


def safe_harness_stage(value):
    # Exact type check comes before membership: no foreign equality, hash, repr,
    # str, descriptor or attribute is evaluated, including on str subclasses.
    return value if type(value) is str and value in HARNESS_STAGES else COLLECTION_FAILURE_STAGE


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
    return rejection("Unknown", "INTERNAL_ERROR", safe_harness_stage(harness_stage), complete=False)


def safe_projection(diagnostic, harness_stage, schema):
    """Pure detached-record model, never introspection of an exception object.

    A real adapter must first establish exact trusted class identity; this function
    cannot prove that from JSON. It models schema rejection and safe fallback only.
    """
    stage = safe_harness_stage(harness_stage)
    if stage == COLLECTION_FAILURE_STAGE:
        return unknown(COLLECTION_FAILURE_STAGE)
    proposed = {"kind": "rejection", "complete": True, "harnessStage": stage,
                "diagnostic": diagnostic, "partialView": None, "report": None}
    if validate(proposed, schema):
        return proposed
    return unknown(stage)


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
    # Wire validity is a separate per-side predicate BEFORE any set or alpha
    # normalization. A mathematical identity helper alone is not wire acceptance.
    expected = case["expectedProjection"]
    return (validate(expected, schema) and validate(observed, schema)
            and canonical_graph_slots(expected, projection_layout(expected))
            and canonical_graph_slots(observed, projection_layout(observed))
            and projection_identity_equal(expected, observed))


def _wire_term(value):
    """Validate the declared typed term spelling, not datatype value semantics."""
    def text(value):
        if type(value) is not str:
            return False
        try:
            value.encode("utf-8")
            return True
        except UnicodeError:
            return False

    def absolute_iri(value):
        return text(value) and re.fullmatch(
            r'[A-Za-z][A-Za-z0-9+.-]*:[^<>"{}|^`\\\x00-\x20]*', value
        ) is not None

    if type(value) is not dict:
        return False
    if set(value) == {"kind", "value"} and value["kind"] == "iri":
        return absolute_iri(value["value"])
    if set(value) == {"kind", "label"} and value["kind"] == "blank":
        return text(value["label"]) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", value["label"]) is not None
    if set(value) != {"kind", "lexical", "datatype", "language"} or value["kind"] != "literal":
        return False
    if not text(value["lexical"]) or not absolute_iri(value["datatype"]):
        return False
    language = value["language"]
    lang_string = "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString"
    if language is None:
        return value["datatype"] != lang_string
    return (text(language) and re.fullmatch(r"[A-Za-z]+(?:-[A-Za-z0-9]+)*", language) is not None
            and value["datatype"] == lang_string)


def _n3_wire_term(token):
    """Read ONE declared generated N3 token; never parse Turtle or call a library.

    Roundtrip enforces this serializer's double-quoted JSON escape spelling and
    plain xsd:string spelling. Numeric/date lexical values are not interpreted.
    """
    if type(token) is not str:
        return None
    try:
        if token.startswith("<") and token.endswith(">"):
            value = {"kind": "iri", "value": token[1:-1]}
        elif token.startswith("_:"):
            value = {"kind": "blank", "label": token[2:]}
        elif token.startswith('"'):
            lexical, end = json.JSONDecoder().raw_decode(token)
            if type(lexical) is not str:
                return None
            suffix = token[end:]
            datatype = "http://www.w3.org/2001/XMLSchema#string"
            language = None
            if suffix.startswith("@"):
                language = suffix[1:]
                datatype = "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString"
            elif suffix.startswith("^^<") and suffix.endswith(">"):
                datatype = suffix[3:-1]
            elif suffix:
                return None
            value = {"kind": "literal", "lexical": lexical, "datatype": datatype, "language": language}
        else:
            return None
        return value if _wire_term(value) and n3(value) == token else None
    except (ValueError, UnicodeError):
        return None


def canonical_graph_wire(rows, mode):
    """Per-end wire gate: original N3 order AND RDF identity uniqueness.

    Does not reorder or deduplicate the supplied rows. Upper/lower language tags
    may each be valid spelling, but two rows with the same RDF identity are not
    two graph members. Blank labels here remain this end's own original labels.
    """
    if type(rows) is not list or mode not in ("typed-graph", "n3-graph"):
        return False
    keys, identities = [], set()
    for row in rows:
        if type(row) is not list or len(row) != 3:
            return False
        terms = row if mode == "typed-graph" else [_n3_wire_term(t) for t in row]
        if not all(_wire_term(t) for t in terms):
            return False
        if terms[0]["kind"] == "literal" or terms[1]["kind"] != "iri":
            return False
        keys.append(tuple(n3(t) for t in terms))
        identity = canonical([identity_term(t) for t in terms])
        if identity in identities:
            return False
        identities.add(identity)
    return keys == sorted(keys)


def canonical_graph_slots(value, slots):
    """Check every explicitly declared graph slot independently before mapping.

    Sequence/raw slots are deliberately untouched; callers must still do complete
    shared-domain comparison afterwards. This function never makes a repaired view.
    """
    try:
        for path, mode in slots:
            if mode not in ("typed-graph", "n3-graph"):
                continue
            rows = value
            for part in path:
                rows = rows[part]
            if not canonical_graph_wire(rows, mode):
                return False
    except (KeyError, IndexError, TypeError):
        return False
    return True


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
    target = {canonical([identity_term(t) for t in row]) for row in right}
    for order in itertools.permutations(b):
        mapping = dict(zip(a, order))
        rewritten = [[{"kind": "blank", "label": mapping[t["label"]]} if t["kind"] == "blank"
                      else identity_term(t) for t in row] for row in left]
        if {canonical(row) for row in rewritten} == target:
            return True
    return False


def projection_layout(value):
    """All RDF positions in this terminal schema; no substring scan of other text.

    One invocation/terminal artifact owns one BNode identity domain. Raw input,
    source, digests, rule IDs and every undeclared position stay exact.
    """
    slots = []

    def legacy_slots(prefix, data):
        for field in ("rdfs", "rules"):
            slots.append((prefix + (field,), "n3-graph"))
        for i, _ in enumerate(data["rdfsEvidence"]):
            slots.extend([(prefix + ("rdfsEvidence", i, "result"), "n3-sequence"),
                          (prefix + ("rdfsEvidence", i, "basis"), "n3-graph")])
        for i, _ in enumerate(data["evidence"]):
            for field, mode in (("result", "n3-sequence"), ("inputs", "n3-sequence"),
                                ("basis", "n3-graph")):
                slots.append((prefix + ("evidence", i, field), mode))

    if value["kind"] == "legacy":
        legacy_slots(("value",), value["value"])
    elif value["kind"] == "scope":
        data = value["value"]
        for field in ("facts", "ontology"):
            slots.append((("value", field), "typed-graph"))
        if data["reasoning_result"] is not None:
            legacy_slots(("value", "reasoning_result"), data["reasoning_result"])
        provenance = data["provenance"]
        for i, row in enumerate(provenance["selectedFacts"]):
            prefix = ("value", "provenance", "selectedFacts", i)
            slots.append((prefix + ("triple",), "n3-sequence"))
            for j, source in enumerate(row["sources"]):
                slots.append((prefix + ("sources", j, "basis"), "n3-graph"))
                if source["kind"] == "rule":
                    slots.append((prefix + ("sources", j, "inputs"), "n3-sequence"))
        for i, _ in enumerate(provenance["derivedAxioms"]):
            prefix = ("value", "provenance", "derivedAxioms", i)
            slots.extend([(prefix + ("triple",), "n3-sequence"),
                          (prefix + ("source", "basis"), "n3-graph")])
        slots.append((("query", "rows"), "typed-sequence"))
        for i, row in enumerate(value["shacl"]["violations"]):
            for field in row:
                slots.append((("shacl", "violations", i, field), "typed-sequence"))
    return slots


def identity_domain_equal(left, right, slots):
    """Joint finite identity comparison, at most 8 BNodes per entire artifact.

    slots are explicit disjoint (JSON path, mode) pairs. Graph modes compare RDF
    sets; sequence modes retain every ordered position and duplicate. Every slot
    shares ONE bijection. Undeclared fields, including raw occurrences and digest
    strings, compare exactly. This detached JSON model is not an RDF/N3 parser.
    """
    def clone(value):
        if type(value) is dict:
            return {k: clone(v) for k, v in value.items()}
        if type(value) is list:
            return [clone(v) for v in value]
        if type(value) in (str, int, bool, type(None)):
            return value
        raise ValueError("detached JSON required")

    paths = [path for path, _ in slots]
    if any(a == b[:len(a)] for i, a in enumerate(paths) for j, b in enumerate(paths) if i != j):
        return False

    def transform(value, mode, mapping, labels):
        def term(value):
            if type(value) is dict:
                if set(value) == {"kind", "label"} and value["kind"] == "blank":
                    labels.add(value["label"])
                    return {"kind": "blank", "label": mapping.get(value["label"], value["label"])}
                if set(value) == {"kind", "lexical", "datatype", "language"} and value["kind"] == "literal":
                    return identity_term(value)
                return {k: term(v) for k, v in value.items()}
            if type(value) is list:
                return [term(v) for v in value]
            if mode.startswith("n3-") and type(value) is str:
                if re.fullmatch(r"_:[A-Za-z][A-Za-z0-9_-]*", value):
                    label = value[2:]
                    labels.add(label)
                    return "_:" + mapping.get(label, label)
                # Only a complete generated literal token's language suffix is
                # casefolded; never lexical text, datatype, IRI or other fields.
                match = re.fullmatch(r'("(?:[^"\\]|\\.)*")@([A-Za-z]+(?:-[A-Za-z0-9]+)*)', value)
                if match:
                    return match[1] + "@" + match[2].casefold()
            return value

        normalized = term(value)
        if mode in ("typed-graph", "n3-graph"):
            return [json.loads(row) for row in sorted({canonical(row) for row in normalized})]
        if mode not in ("typed-sequence", "n3-sequence"):
            raise ValueError("unknown identity slot mode")
        return normalized

    def rewrite(value, mapping):
        result = clone(value)
        labels = set()
        for path, mode in slots:
            if not path:
                raise ValueError("nonempty identity slot path required")
            target = result
            for part in path[:-1]:
                target = target[part]
            key = path[-1]
            target[key] = transform(target[key], mode, mapping, labels)
        return result, sorted(labels)

    try:
        _, a = rewrite(left, {})
        target, b = rewrite(right, {})
        if len(a) != len(b) or len(a) > 8:
            return False
        for order in itertools.permutations(b):
            rewritten, _ = rewrite(left, dict(zip(a, order)))
            if exact(rewritten, target):
                return True
    except (KeyError, IndexError, TypeError, ValueError):
        return False
    return False


def projection_identity_equal(left, right):
    """Mathematical identity relation only; wire callers MUST use matches()."""
    return identity_domain_equal(left, right, projection_layout(left))
