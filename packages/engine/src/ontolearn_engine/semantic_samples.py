"""Versioned real G.2 candidate samples, shared by source and frozen executable.

Only semantic G-base is executed here; mapping, behavior and simulation remain
separate dependencies. S1's 18*scale synthetic input is reused byte-for-byte.
"""

import json

from pyshacl.validator import Validator
from rdflib import RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef, Variable

from ontolearn_engine.semantic import Rule, check_shapes, parse_turtle, query, reason
from ontolearn_engine.semantic_offline import SemanticError, offline
from ontolearn_engine.semantic_scopes import prepare_validation_scope, project_validation_scope
from ontolearn_engine.storage_probe import QUERY, SEED, fixture

EX = Namespace("urn:ontolearn:")
PREFIX = """@prefix : <urn:ontolearn:> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""
ONTOLOGY = """@prefix : <urn:ontolearn:> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
:Equipment a owl:Class . :Alarm a owl:Class . :WorkOrder a owl:Class .
:HighRiskEquipment a owl:Class .
:name a owl:DatatypeProperty . :level a owl:DatatypeProperty .
:status a owl:DatatypeProperty . :alarm a owl:ObjectProperty .
:workOrderStatus a owl:DatatypeProperty . :eventWorkOrder a owl:ObjectProperty .
"""
SHAPES = (
    PREFIX
    + """
:EquipmentName a sh:NodeShape; sh:targetClass :Equipment; sh:property :NameProperty .
:NameProperty a sh:PropertyShape; sh:path :name; sh:minCount 1 .
"""
)
e, a = Variable("equipment"), Variable("alarm")
RISK = Rule(
    "R-risk",
    (
        (e, RDF.type, EX.Equipment),
        (e, EX.alarm, a),
        (a, EX.level, Literal("High")),
        (a, EX.status, Literal("Open")),
    ),
    (e, RDF.type, EX.HighRiskEquipment),
)
NEXT = Rule("R-next", ((e, RDF.type, EX.HighRiskEquipment),), (e, RDF.type, EX.NeedsInspection))


def suite() -> dict:
    """Assert complete identities and evidence, never counts alone."""
    graph = parse_turtle(fixture(1))
    schema = parse_turtle(ONTOLOGY)
    for triple in schema:
        graph.add(triple)
    shapes = parse_turtle(SHAPES, shapes=True)
    q1 = query(graph, QUERY)
    assert q1 == {"type": "SELECT", "variables": ["alarm"], "rows": [["<urn:case:0:alarm/A01>"]]}
    assert query(graph, "ASK { <urn:case:0:alarm/A01> ?p ?o }") == {"type": "ASK", "value": True}
    assert query(graph, 'SELECT ?x WHERE { BIND("SERVICE FROM" AS ?x) }')["rows"] == [
        ['"SERVICE FROM"']
    ]
    q2graph = parse_turtle(fixture(1))
    a01 = URIRef("urn:case:0:alarm/A01")
    equipment = URIRef("urn:case:0:equipment/001")
    q2graph.set((a01, EX.status, Literal("Closed")))
    assert query(q2graph, QUERY)["rows"] == []
    before = check_shapes(graph, shapes)
    assert before == {"conforms": True, "violations": []}
    missing = URIRef("urn:case:0:equipment/003")
    graph.remove((missing, EX.name, None))
    v1 = check_shapes(graph, shapes)
    assert v1 == {
        "conforms": False,
        "violations": [
            {
                "focus": missing.n3(),
                "path": EX.name.n3(),
                "constraint": "<http://www.w3.org/ns/shacl#MinCountConstraintComponent>",
                "sourceShape": EX.NameProperty.n3(),
                "value": None,
                "severity": "<http://www.w3.org/ns/shacl#Violation>",
            }
        ],
    }
    graph.add((missing, EX.name, Literal("备用泵C")))
    assert check_shapes(graph, shapes) == before
    r1 = reason(graph, (RISK,))
    risk_triple = (equipment.n3(), RDF.type.n3(), EX.HighRiskEquipment.n3())
    assert r1["rules"] == [risk_triple]
    assert r1["evidence"] == [
        {
            "rule": "R-risk",
            "result": risk_triple,
            "inputs": [
                (equipment.n3(), RDF.type.n3(), EX.Equipment.n3()),
                (equipment.n3(), EX.alarm.n3(), a01.n3()),
                (a01.n3(), EX.level.n3(), '"High"'),
                (a01.n3(), EX.status.n3(), '"Open"'),
            ],
            "basis": sorted(
                [
                    (equipment.n3(), RDF.type.n3(), EX.Equipment.n3()),
                    (equipment.n3(), EX.alarm.n3(), a01.n3()),
                    (a01.n3(), EX.level.n3(), '"High"'),
                    (a01.n3(), EX.status.n3(), '"Open"'),
                ]
            ),
        }
    ]
    graph.remove((a01, None, None))
    graph.remove((None, EX.alarm, a01))
    assert reason(graph, (RISK,))["rules"] == []
    a04 = URIRef("urn:case:0:alarm/A04")
    for triple in (
        (equipment, EX.alarm, a04),
        (a04, EX.level, Literal("High")),
        (a04, EX.status, Literal("Open")),
    ):
        graph.add(triple)
    r3 = reason(graph, (RISK,))
    assert r3["rules"] == [risk_triple]
    assert all(
        a01.n3() not in term for row in r3["evidence"] for triple in row["basis"] for term in triple
    )
    assert (equipment.n3(), EX.alarm.n3(), a04.n3()) in r3["evidence"][0]["inputs"]
    critical, pump, alert = EX.CriticalPump, EX.P001, EX.A04
    for triple in (
        (critical, RDFS.subClassOf, EX.Equipment),
        (pump, RDF.type, critical),
        (pump, EX.alarm, alert),
        (alert, EX.level, Literal("High")),
        (alert, EX.status, Literal("Open")),
    ):
        graph.add(triple)
    r4 = reason(graph, (RISK,))
    expected = sorted([risk_triple, (pump.n3(), RDF.type.n3(), EX.HighRiskEquipment.n3())])
    assert r4["rules"] == expected
    assert (pump.n3(), RDF.type.n3(), EX.Equipment.n3()) in r4["rdfs"]
    r5 = reason(graph, (RISK, NEXT))
    assert r5 == reason(graph, (NEXT, RISK))
    assert r5["rules"] == expected
    assert "RULE_CHAIN_UNSUPPORTED:R-next" in r5["warnings"]
    # Absence is not a negative fact. No alarm does not entail an OWL complement.
    a03 = URIRef("urn:case:0:alarm/A03")
    graph.remove((missing, EX.alarm, a03))
    graph.remove((a03, None, None))
    assert query(graph, f"SELECT ?a WHERE {{ {missing.n3()} <{EX.alarm}> ?a }}")["rows"] == []
    return {
        "baseline": "I05-G2-v1",
        "seed": SEED,
        "Q-01": q1,
        "Q-02": [],
        "V-01": v1,
        "R-01": r1,
        "R-02": [],
        "R-03": r3,
        "R-04": r4,
        "R-05-06": r5,
        "O-01": "no recorded alarm; no closed-world negative assertion",
        "finiteTemplates": template_suite(),
        "validationScopes": scope_suite(),
        "literalIdentity": lexical_suite(),
        "stringIdentity": string_identity_suite(),
        "rdfsWitness": rdfs_witness_suite(),
        "scope": "pure G.2 semantics; no storage/task/UI integration",
    }


def string_identity_suite():
    """One RDF string term across parsing, matching, expressions and selection."""
    plain, explicit = Literal("x"), Literal("x", datatype=XSD.string, normalize=False)
    subjects = (EX.bothString, EX.plainString, EX.typedString)
    graph = Graph()
    for subject in subjects:
        graph.add((subject, EX.value, explicit if subject == EX.typedString else plain))
    graph.add((subjects[0], EX.value, explicit))
    graph.add((subjects[0], RDF.type, EX.StringThing))
    original = set(graph)
    variable = Variable("s")
    rules = tuple(
        Rule(identity, ((variable, EX.value, token),), (variable, predicate, EX.yes))
        for identity, token, predicate in (
            ("match-plain", plain, EX.plainMatched),
            ("match-typed", explicit, EX.typedMatched),
        )
    ) + tuple(
        Rule(identity, ((subjects[0], EX.value, plain),), (subjects[0], EX.emitted, token))
        for identity, token in (("emit-plain", plain), ("emit-typed", explicit))
    )

    def row(*terms):
        return tuple(term.n3() for term in terms)

    evidence = []
    for rule in sorted(rules, key=lambda rule: rule.id):
        for subject in (subjects[0],) if rule.id.startswith("emit") else subjects:
            fact = row(subject, EX.value, plain)
            result = (
                row(subject, EX.emitted, plain)
                if rule.id.startswith("emit")
                else row(subject, rule.then[1], EX.yes)
            )
            evidence.append({"rule": rule.id, "result": result, "inputs": [fact], "basis": [fact]})
    expected = {
        "rdfs": [],
        "rdfsEvidence": [],
        "warnings": [],
        "rules": sorted({record["result"] for record in evidence}),
        "evidence": evidence,
    }
    reasoning = reason(graph, rules)
    assert reasoning == expected
    assert len(reasoning["rules"]) == 7 and len(reasoning["evidence"]) == 8
    lexical = []
    for text in ("", "x", 'quote" slash\\', "line\nnext", "你好"):
        a, b = Literal(text, normalize=False), Literal(text, datatype=XSD.string, normalize=False)
        parsed = parse_turtle(f"<{EX.unit}> <{EX.value}> {a.n3()}, {b.n3()} .")
        assert set(parsed) == {(EX.unit, EX.value, a)}
        lexical.append({"lexical": text, "term": parsed.value(EX.unit, EX.value).n3()})
    expressions = [
        f'STRDT("x", <{XSD.string}>)',
        f"STR({explicit.n3()})",
        f'CONCAT("", {explicit.n3()})',
        f'SUBSTR(STRDT("xy", <{XSD.string}>), 1, 1)',
        f'REPLACE(STRDT("a", <{XSD.string}>), "a", "x")',
        f'LCASE(STRDT("X", <{XSD.string}>))',
    ]
    queries = {}
    for expression in expressions:
        text = (
            f"SELECT ?s WHERE {{ BIND({expression} AS ?v) ?s <{EX.value}> ?v "
            'FILTER(sameTerm(?v, "x")) }'
        )
        actual = query(graph, text)
        assert actual == {
            "type": "SELECT",
            "variables": ["s"],
            "rows": [[subject.n3()] for subject in subjects],
        }
        queries[expression] = actual
    values = f'VALUES ?v {{ "x" {explicit.n3()} }}'
    count = query(Graph(), f"SELECT (COUNT(DISTINCT ?v) AS ?n) WHERE {{ {values} }}")
    assert count == {"type": "SELECT", "variables": ["n"], "rows": [[Literal(1).n3()]]}
    distinct = query(Graph(), f"SELECT DISTINCT ?v WHERE {{ {values} }}")
    assert distinct == {"type": "SELECT", "variables": ["v"], "rows": [['"x"']]}
    generated = prepare_validation_scope(graph, Graph(), include_derived=True, rules=rules)
    payload = json.loads(json.dumps(generated.reasoning_result))
    selected = project_validation_scope(
        graph,
        Graph(),
        include_derived=True,
        rules=rules,
        reasoning_result=payload,
        reasoning_source=generated.provenance["reasoningSource"],
    )
    assert selected.reasoning_result is payload
    assert json.loads(json.dumps(reasoning)) == payload
    validations = {}
    for name, clause, conforms in (
        ("inPlain", 'sh:in ("x")', True),
        ("inTyped", f"sh:in ({explicit.n3()})", True),
        ("datatype", f"sh:datatype <{XSD.string}>", True),
        ("maxOne", "sh:maxCount 1", True),
        ("minTwo", "sh:minCount 2", False),
    ):
        shape = parse_turtle(
            PREFIX + ":StringShape a sh:NodeShape; sh:targetClass :StringThing; "
            f"sh:property :StringProperty . :StringProperty sh:path :emitted; {clause} .",
            shapes=True,
        )
        actual = check_shapes(selected.facts, shape)
        expected_report = {"conforms": conforms, "violations": []}
        if not conforms:
            expected_report["violations"] = [
                {
                    "focus": subjects[0].n3(),
                    "path": EX.emitted.n3(),
                    "constraint": "<http://www.w3.org/ns/shacl#MinCountConstraintComponent>",
                    "sourceShape": EX.StringProperty.n3(),
                    "value": None,
                    "severity": "<http://www.w3.org/ns/shacl#Violation>",
                }
            ]
        assert actual == expected_report
        validations[name] = actual
    assert set(graph) == original
    return {
        "lexical": lexical,
        "reasoning": reasoning,
        "runtimeExpressions": queries,
        "distinct": distinct,
        "count": count,
        "selectedProvenance": selected.provenance,
        "validation": validations,
    }


def lexical_suite():
    """C1 counterexamples: exact RDF terms, never numeric-value equality."""
    cases = [
        ("01", "1", XSD.integer),
        ("+01", "+1", XSD.integer),
        ("-01", "-1", XSD.integer),
        ("-00", "0", XSD.integer),
        ("01.00", "1.0", XSD.decimal),
        ("+01.00", "+1.0", XSD.decimal),
        ("-01.00", "-1.0", XSD.decimal),
        ("01e+00", "1e+00", XSD.double),
        ("+01e+00", "+1e+00", XSD.double),
        ("-01e+00", "-1e+00", XSD.double),
    ]
    observations = []
    for token, other, datatype in cases:
        term = Literal(token, datatype=datatype, normalize=False)
        different = Literal(other, datatype=datatype, normalize=False)
        assert term != different and term.eq(different)
        graph = Graph()
        graph.add((EX.unit, RDF.type, EX.Equipment))
        graph.add((EX.unit, EX.value, term))
        assert set(parse_turtle(f"<{EX.unit}> <{EX.value}> {token} .")) == {
            (EX.unit, EX.value, term)
        }
        shapes = parse_turtle(
            PREFIX
            + f"""
            :LexicalShape a sh:NodeShape; sh:targetClass :Equipment;
                sh:property :LexicalProperty .
            :LexicalProperty sh:path :value; sh:in ({term.n3()}) .
            """,
            shapes=True,
        )
        good = check_shapes(graph, shapes)
        assert good == {"conforms": True, "violations": []}
        graph.set((EX.unit, EX.value, different))
        bad = check_shapes(graph, shapes)
        assert bad == {
            "conforms": False,
            "violations": [
                {
                    "focus": EX.unit.n3(),
                    "path": EX.value.n3(),
                    "constraint": "<http://www.w3.org/ns/shacl#InConstraintComponent>",
                    "sourceShape": EX.LexicalProperty.n3(),
                    "value": different.n3(),
                    "severity": "<http://www.w3.org/ns/shacl#Violation>",
                }
            ],
        }
        ask = f"ASK {{ <{EX.unit}> <{EX.value}> {token} }}"
        assert query(graph, ask) == {"type": "ASK", "value": False}
        graph.set((EX.unit, EX.value, term))
        matched = query(graph, ask)
        assert matched == {"type": "ASK", "value": True}
        values = query(Graph(), f"SELECT ?v WHERE {{ VALUES ?v {{ {token} }} }}")
        assert values == {"type": "SELECT", "variables": ["v"], "rows": [[term.n3()]]}
        expression = query(Graph(), f"SELECT ?v WHERE {{ BIND({token} AS ?v) }}")
        assert expression == values
        spelling = query(Graph(), f"SELECT (STR({token}) AS ?v) WHERE {{}}")
        assert spelling == {"type": "SELECT", "variables": ["v"], "rows": [[f'"{token}"']]}
        variable = Variable("s")
        exact = Rule("lexical", ((variable, EX.value, term),), (variable, RDF.type, EX.Exact))
        unequal = Rule(
            "different", ((variable, EX.value, different),), (variable, RDF.type, EX.Different)
        )
        derived = reason(graph, (exact, unequal))
        assert derived["rules"] == [(EX.unit.n3(), RDF.type.n3(), EX.Exact.n3())]
        observations.append(
            {
                "token": token,
                "term": term.n3(),
                "differentTerm": different.n3(),
                "same": good,
                "different": bad,
                "query": matched,
                "values": values,
                "expression": expression,
                "spelling": spelling,
                "rules": derived,
            }
        )
    rejected = []
    for text in (
        "<urn:s> <urn:p> 1.2.3 .",
        "<urn:orphan> .",
        "([<urn:p> <urn:o>]) .",
        "<urn:s> <urn:p> 01 . true .",
    ):
        try:
            parse_turtle(text, shapes=True)
        except SemanticError as error:
            assert error.code == "INVALID_TURTLE"
            rejected.append({"text": text, "reason": error.code})
        else:
            raise AssertionError("orphan Turtle term was silently discarded")
    return {"numbers": observations, "rejectedSyntax": rejected}


def rdfs_witness_suite():
    """Same-output RDFS paths choose a stable valid witness, not all proofs."""
    w = Namespace("urn:i05:witness:")
    subject = Variable("subject")
    rule = Rule(
        "observe-basis",
        ((subject, RDF.type, w.C),),
        (subject, w.observed, w.yes),
    )

    def row(*terms):
        return tuple(term.n3() for term in terms)

    inferred = row(w.u, RDF.type, w.C)
    output = row(w.u, w.observed, w.yes)
    cases = {
        "domain": (
            [(w.u, w.p, w.b), (w.u, w.p, w.a), (w.p, RDFS.domain, w.C)],
            sorted([row(w.p, RDFS.domain, w.C), row(w.u, w.p, w.a)]),
        ),
        "range": (
            [(w.b, w.p, w.u), (w.a, w.p, w.u), (w.p, RDFS.range, w.C)],
            sorted([row(w.a, w.p, w.u), row(w.p, RDFS.range, w.C)]),
        ),
    }
    observations = {}
    for name, (triples, basis) in cases.items():
        expected = {
            "rdfs": [inferred],
            "rules": [output],
            "warnings": [],
            "rdfsEvidence": [{"result": inferred, "basis": basis}],
            "evidence": [{"rule": rule.id, "result": output, "inputs": [inferred], "basis": basis}],
        }
        graph = Graph()
        for triple in triples:
            graph.add(triple)
        result = reason(graph, (rule,))
        assert result == expected
        # Irrelevant inputs and reverse insertion do not become evidence.
        reverse = Graph()
        for triple in reversed([*triples, (w.unrelated, w.q, w.other)]):
            reverse.add(triple)
        assert reason(reverse, (rule,)) == expected
        observations[name] = result
    return observations


def scope_suite():
    """Real asserted / asserted+selected-derived ranges; never a mocked result."""
    ontology = parse_turtle(
        PREFIX
        + """
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        :CriticalPump rdfs:subClassOf :Pump . :Pump rdfs:subClassOf :Equipment .
    """
    )
    asserted = parse_turtle(
        PREFIX
        + """
        :unit a :CriticalPump; :alarm :alert . :alert :level "High"; :status "Open" .
        :explicit a :Equipment; :name "Explicit" .
    """
    )
    shapes = parse_turtle(
        SHAPES
        + """
        :RiskShape a sh:NodeShape; sh:targetClass :HighRiskEquipment; sh:property :RiskName .
        :RiskName a sh:PropertyShape; sh:path :name; sh:minCount 1 .
    """,
        shapes=True,
    )
    original_asserted, original_ontology = set(asserted), set(ontology)
    direct = prepare_validation_scope(asserted, ontology, include_derived=False)
    inferred = prepare_validation_scope(asserted, ontology, include_derived=True, rules=(RISK,))
    direct_result = check_shapes(direct.facts, shapes)
    derived_result = check_shapes(inferred.facts, shapes)

    def targets(data):
        with offline():
            local_data, local_shapes = Graph(), Graph()
            for triple in data:
                local_data.add(triple)
            for triple in shapes:
                local_shapes.add(triple)
            validator = Validator(
                local_data,
                shacl_graph=local_shapes,
                options={
                    "inference": "none",
                    "advanced": False,
                    "use_js": False,
                    "inplace": False,
                    "sparql_mode": False,
                },
            )
            return {
                shape.node.n3(): sorted(node.n3() for node in shape.focus_nodes(local_data))
                for shape in validator.shacl_graph.shapes
            }

    direct_targets, derived_targets = targets(direct.facts), targets(inferred.facts)
    assert direct_targets == {
        EX.EquipmentName.n3(): [EX.explicit.n3()],
        EX.RiskShape.n3(): [],
        EX.NameProperty.n3(): [],
        EX.RiskName.n3(): [],
    }
    assert derived_targets == {
        EX.EquipmentName.n3(): [EX.explicit.n3(), EX.unit.n3()],
        EX.RiskShape.n3(): [EX.unit.n3()],
        EX.NameProperty.n3(): [],
        EX.RiskName.n3(): [],
    }
    assert direct_result == {"conforms": True, "violations": []}
    expected = [
        {
            "focus": EX.unit.n3(),
            "path": EX.name.n3(),
            "constraint": "<http://www.w3.org/ns/shacl#MinCountConstraintComponent>",
            "sourceShape": shape.n3(),
            "value": None,
            "severity": "<http://www.w3.org/ns/shacl#Violation>",
        }
        for shape in (EX.NameProperty, EX.RiskName)
    ]
    assert derived_result == {"conforms": False, "violations": expected}
    type_rows = {
        (EX.unit, RDF.type, cls)
        for cls in (EX.CriticalPump, EX.Pump, EX.Equipment, EX.HighRiskEquipment)
    }
    assert set(direct.facts) == original_asserted
    assert set(inferred.facts) == original_asserted | type_rows
    transitive_axiom = (EX.CriticalPump, RDFS.subClassOf, EX.Equipment)
    assert set(inferred.ontology) == original_ontology | {transitive_axiom}
    assert transitive_axiom not in inferred.facts
    assert set(asserted) == original_asserted and set(ontology) == original_ontology
    sources = {row["triple"]: row["sources"] for row in inferred.provenance["selectedFacts"]}
    expected_rdfs_basis = sorted(
        [
            tuple(t.n3() for t in triple)
            for triple in (
                (EX.unit, RDF.type, EX.CriticalPump),
                (EX.CriticalPump, RDFS.subClassOf, EX.Pump),
                (EX.Pump, RDFS.subClassOf, EX.Equipment),
            )
        ]
    )
    assert sources[(EX.unit.n3(), RDF.type.n3(), EX.Equipment.n3())] == [
        {"kind": "rdfs", "basis": expected_rdfs_basis}
    ]
    risk_sources = sources[(EX.unit.n3(), RDF.type.n3(), EX.HighRiskEquipment.n3())]
    assert risk_sources == [
        {
            "kind": "rule",
            "rule": "R-risk",
            "inputs": [
                (EX.unit.n3(), RDF.type.n3(), EX.Equipment.n3()),
                (EX.unit.n3(), EX.alarm.n3(), EX.alert.n3()),
                (EX.alert.n3(), EX.level.n3(), '"High"'),
                (EX.alert.n3(), EX.status.n3(), '"Open"'),
            ],
            "basis": sorted(
                [
                    *expected_rdfs_basis,
                    (EX.unit.n3(), EX.alarm.n3(), EX.alert.n3()),
                    (EX.alert.n3(), EX.level.n3(), '"High"'),
                    (EX.alert.n3(), EX.status.n3(), '"Open"'),
                ]
            ),
        }
    ]
    assert inferred.provenance["derivedAxioms"] == [
        {
            "triple": tuple(t.n3() for t in transitive_axiom),
            "source": {
                "kind": "rdfs",
                "basis": sorted([tuple(t.n3() for t in row) for row in original_ontology]),
            },
        }
    ]
    assert direct.provenance["assertedInputSha256"] == inferred.provenance["assertedInputSha256"]
    assert direct.provenance["ontologyInputSha256"] == inferred.provenance["ontologyInputSha256"]
    combined = Graph()
    for triple in (*inferred.facts, *inferred.ontology):
        combined.add(triple)
    try:
        check_shapes(combined, shapes)
    except SemanticError as error:
        assert error.code == "FACT_SCOPE_CONTAINS_AXIOMS"
    else:
        raise AssertionError("mixed inferred axioms were accepted as validation facts")
    # A real earlier computation with a different producer plan remains selected.
    # JSON round-trip is a payload boundary, not a simulated Store/Job/history API.
    earlier = prepare_validation_scope(asserted, ontology, include_derived=True)
    selected_bytes = json.dumps(earlier.reasoning_result, ensure_ascii=False, sort_keys=True)
    selected_payload = json.loads(selected_bytes)
    selected = project_validation_scope(
        asserted,
        ontology,
        include_derived=True,
        reasoning_result=selected_payload,
        reasoning_source=earlier.provenance["reasoningSource"],
        rules=(),
    )
    selected_validation, selected_targets = (
        check_shapes(selected.facts, shapes),
        targets(selected.facts),
    )
    assert selected.reasoning_result is selected_payload
    assert json.dumps(selected_payload, ensure_ascii=False, sort_keys=True) == selected_bytes
    assert selected_validation == {"conforms": False, "violations": expected[:1]}
    assert selected_targets == {**derived_targets, EX.RiskShape.n3(): []}
    assert (EX.unit, RDF.type, EX.HighRiskEquipment) not in selected.facts
    assert (EX.unit, RDF.type, EX.HighRiskEquipment) in inferred.facts
    assert set(selected.facts) == set(earlier.facts)
    corrupt = json.loads(selected_bytes)
    corrupt["rdfsEvidence"].pop()
    extra_facts = Graph()
    for triple in asserted:
        extra_facts.add(triple)
    extra_facts.add((EX.unused, EX.name, Literal("unrelated changed input")))
    rejected_selection = {}
    for case, data, payload, source, selected_rules, expected_code in (
        (
            "missingPayload",
            asserted,
            None,
            earlier.provenance["reasoningSource"],
            (),
            "REASONING_RESULT_INVALID",
        ),
        (
            "missingEvidence",
            asserted,
            corrupt,
            earlier.provenance["reasoningSource"],
            (),
            "REASONING_RESULT_INVALID",
        ),
        (
            "changedInput",
            extra_facts,
            selected_payload,
            earlier.provenance["reasoningSource"],
            (),
            "REASONING_SOURCE_MISMATCH",
        ),
        (
            "changedRulePlan",
            asserted,
            selected_payload,
            earlier.provenance["reasoningSource"],
            (RISK,),
            "REASONING_SOURCE_MISMATCH",
        ),
    ):
        try:
            project_validation_scope(
                data,
                ontology,
                include_derived=True,
                reasoning_result=payload,
                reasoning_source=source,
                rules=selected_rules,
            )
        except SemanticError as error:
            assert error.code == expected_code
            rejected_selection[case] = error.code
        else:
            raise AssertionError("invalid selected payload/context accepted")
    assert set(asserted) == original_asserted and set(ontology) == original_ontology
    lexical_value = Literal("01", datatype=XSD.integer, normalize=False)
    lexical_rule = Rule(
        "R-lexical", ((EX.unit, RDF.type, EX.CriticalPump),), (EX.unit, EX.name, lexical_value)
    )
    lexical_generated = prepare_validation_scope(
        asserted, ontology, include_derived=True, rules=(lexical_rule,)
    )
    lexical_payload = json.loads(json.dumps(lexical_generated.reasoning_result))
    lexical_selected = project_validation_scope(
        asserted,
        ontology,
        include_derived=True,
        reasoning_result=lexical_payload,
        reasoning_source=lexical_generated.provenance["reasoningSource"],
        rules=(lexical_rule,),
    )
    assert (EX.unit, EX.name, lexical_value) in lexical_selected.facts
    assert lexical_selected.reasoning_result is lexical_payload
    assert lexical_payload["rules"][0][2] == lexical_value.n3()
    asserted.add((EX.unit, EX.name, Literal("Pump")))
    repaired = prepare_validation_scope(asserted, ontology, include_derived=True, rules=(RISK,))
    assert check_shapes(repaired.facts, shapes) == {"conforms": True, "violations": []}
    chain = prepare_validation_scope(asserted, ontology, include_derived=True, rules=(RISK, NEXT))
    assert chain.provenance["warnings"] == ["RULE_CHAIN_UNSUPPORTED:R-next"]
    assert (EX.unit, RDF.type, EX.NeedsInspection) not in chain.facts
    return {
        "asserted": {
            "validation": direct_result,
            "provenance": direct.provenance,
            "targets": direct_targets,
            "reasoningResult": direct.reasoning_result,
        },
        "assertedWithSelectedDerived": {
            "validation": derived_result,
            "provenance": inferred.provenance,
            "targets": derived_targets,
            "reasoningResult": inferred.reasoning_result,
        },
        "selectedEarlierComputation": {
            "validation": selected_validation,
            "targets": selected_targets,
            "provenance": selected.provenance,
            "reasoningResult": selected_payload,
            "rejectedSelections": rejected_selection,
        },
        "lexicalSelection": {
            "literal": lexical_value.n3(),
            "reasoningResult": lexical_payload,
            "provenance": lexical_selected.provenance,
        },
        "mixedAxiomsRejected": "FACT_SCOPE_CONTAINS_AXIOMS",
        "repaired": {"conforms": True, "violations": []},
        "chainWarnings": chain.provenance["warnings"],
    }


def template_suite():
    """All advertised finite SHACL templates, executed in both runtimes."""
    results = {}
    for name, constraint, values, component in (
        ("datatype", "sh:datatype xsd:integer", '"wrong"', "Datatype"),
        ("maximum", "sh:maxCount 1", '"a", "b"', "MaxCount"),
        ("allowed", 'sh:in ("good" "ok")', '"bad"', "In"),
        ("minimum", "sh:minInclusive 2", "1", "MinInclusive"),
        ("upper", "sh:maxInclusive 2", "3", "MaxInclusive"),
    ):
        data = parse_turtle(PREFIX + f":x a :Equipment; :name {values} .")
        shapes = parse_turtle(
            PREFIX
            + f"""
            :S a sh:NodeShape; sh:targetClass :Equipment; sh:property :P .
            :P a sh:PropertyShape; sh:path :name; {constraint} .""",
            shapes=True,
        )
        result = check_shapes(data, shapes)
        assert result == {
            "conforms": False,
            "violations": [
                {
                    "focus": EX.x.n3(),
                    "path": EX.name.n3(),
                    "sourceShape": EX.P.n3(),
                    "constraint": f"<http://www.w3.org/ns/shacl#{component}ConstraintComponent>",
                    "value": None
                    if component == "MaxCount"
                    else next(data.objects(EX.x, EX.name)).n3(),
                    "severity": "<http://www.w3.org/ns/shacl#Violation>",
                }
            ],
        }
        results[name] = result
    return results


def rejection_cases(endpoint: str) -> list[tuple[str, str, dict]]:
    """Same explicit inputs for source, unit tests, and real packaged executable."""
    cases = []
    for name, text in {
        "service": f"SELECT * WHERE {{ SERVICE <{endpoint}> {{ ?s ?p ?o }} }}",
        "service-silent": f"ASK {{ SERVICE SILENT <{endpoint}> {{ ?s ?p ?o }} }}",
        "service-variable": (
            f"SELECT * WHERE {{ VALUES ?e {{ <{endpoint}> }} SERVICE ?e {{ ?s ?p ?o }} }}"
        ),
        "service-nested": (
            f"SELECT * WHERE {{ {{ SELECT * WHERE {{ SeRvIcE <{endpoint}> {{ ?s ?p ?o }} }} }} }}"
        ),
        "from": f"SELECT * FROM <{endpoint}> WHERE {{ ?s ?p ?o }}",
        "from-named": f"SELECT * FROM NAMED <{endpoint}> WHERE {{ GRAPH ?g {{ ?s ?p ?o }} }}",
        "base-from": f"BASE <{endpoint}> SELECT * FROM <relative> WHERE {{ ?s ?p ?o }}",
        "file-from": "SELECT * FROM <file:///must-not-read.ttl> WHERE { ?s ?p ?o }",
    }.items():
        cases.append((name, "EXTERNAL_ACCESS_DENIED", {"kind": "query", "text": text}))
    for name, format, text in (
        ("jsonld-context", "json-ld", '{"@context":"' + endpoint + '"}'),
        ("jsonld-import", "json-ld", '{"@context":{"@import":"' + endpoint + '"}}'),
        ("xml-entity", "xml", '<!DOCTYPE x [<!ENTITY e SYSTEM "' + endpoint + '">]><x>&e;</x>'),
        ("n3-formula", "n3", "{ <urn:s> <urn:p> <urn:o> } <urn:p> <urn:o> ."),
    ):
        cases.append(
            (name, "UNSUPPORTED_FORMAT", {"kind": "parse", "text": text, "format": format})
        )
    for role in ("data", "ontology", "shapes"):
        for scheme in (endpoint, "file:///must-not-read.ttl"):
            cases.append(
                (
                    f"imports-{role}-{scheme.split(':')[0]}",
                    "EXTERNAL_ACCESS_DENIED",
                    {
                        "kind": "parse",
                        "shapes": role == "shapes",
                        "text": (
                            f"<urn:ontology> <http://www.w3.org/2002/07/owl#imports> <{scheme}> ."
                        ),
                    },
                )
            )
    for name, predicate, value in (
        ("sparql", "sparql", ":Remote"),
        ("js", "js", ":Remote"),
        ("js-library", "jsLibrary", f"<{endpoint}>"),
        ("rule", "rule", ":Remote"),
        ("target", "target", ":Remote"),
        ("validator", "validator", ":Remote"),
        ("function", "select", '"SELECT * {}"'),
        ("logical", "or", "(:Remote)"),
        ("inverse", "inversePath", ":name"),
    ):
        cases.append(
            (
                "shacl-" + name,
                "UNSUPPORTED_SHACL",
                {"kind": "validate", "text": SHAPES + f"\n:Remote sh:{predicate} {value} ."},
            )
        )
    return cases


def execute_case(request: dict):
    if request["kind"] == "query":
        return query(parse_turtle(fixture(1)), request["text"])
    if request["kind"] == "parse":
        return parse_turtle(
            request["text"],
            format=request.get("format", "turtle"),
            shapes=request.get("shapes", False),
        )
    if request["kind"] == "validate":
        return check_shapes(parse_turtle(fixture(1)), parse_turtle(request["text"], shapes=True))
    raise SemanticError("INVALID_PROBE_CASE")
