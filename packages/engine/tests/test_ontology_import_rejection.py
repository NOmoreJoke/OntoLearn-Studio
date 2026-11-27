"""FR-203 import pre-check: every out-of-scope construct rejects the whole batch.

Table-driven coverage of the frozen rejection vocabulary (UNSUPPORTED_FORMAT,
INVALID_TURTLE, UNSUPPORTED_OWL/RDFS/SHACL/SHACL_PATH/BLANK_NODE/
LITERAL_DATATYPE). Every rejection proves a zero-change Store and no plan,
while the accepted control case proves the plan is directly previewable.
"""

from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT

BASE = "urn:ontolearn:import:"
PREFIXES = (
    "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
    "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
    "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
    "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
    "@prefix sh: <http://www.w3.org/ns/shacl#> .\n\n"
)
GOOD_TURTLE = PREFIXES + "<urn:x:a> rdf:type owl:Class .\n"
# (name, format, turtle, expected status, expected code)
CASES = [
    (
        "unsupported-format",
        "n3",
        GOOD_TURTLE,
        "invalid",
        "UNSUPPORTED_FORMAT",
    ),
    (
        "broken-syntax",
        "turtle",
        "this is << not turtle",
        "invalid",
        "INVALID_TURTLE",
    ),
    (
        "unsafe-iri",
        "turtle",
        "<urn:x:a> <urn:x:p> <http://example.org/a|b> .",
        "invalid",
        "INVALID_TURTLE",
    ),
    (
        "relative-iri",
        "turtle",
        "@prefix ex: <http://example.org/> .\nex:a ex:p <relative> .",
        "invalid",
        "INVALID_TURTLE",
    ),
    (
        "owl-equivalent-class",
        "turtle",
        PREFIXES + "<urn:x:a> owl:equivalentClass <urn:x:b> .",
        "rejected",
        "UNSUPPORTED_OWL",
    ),
    (
        "owl-restriction",
        "turtle",
        PREFIXES + "<urn:x:a> owl:onProperty <urn:x:p> .",
        "rejected",
        "UNSUPPORTED_OWL",
    ),
    (
        "owl-cardinality",
        "turtle",
        PREFIXES + '<urn:x:a> owl:cardinality "1"^^xsd:integer .',
        "rejected",
        "UNSUPPORTED_OWL",
    ),
    (
        "swrl-rule",
        "turtle",
        PREFIXES + "<urn:x:r> <http://www.w3.org/2003/11/swrl#body> <urn:x:b> .",
        "rejected",
        "UNSUPPORTED_OWL",
    ),
    (
        "rdfs-sub-property",
        "turtle",
        PREFIXES + "<urn:x:p> rdfs:subPropertyOf <urn:x:q> .",
        "rejected",
        "UNSUPPORTED_RDFS",
    ),
    (
        "rdfs-see-also",
        "turtle",
        PREFIXES + "<urn:x:a> rdfs:seeAlso <urn:x:b> .",
        "rejected",
        "UNSUPPORTED_RDFS",
    ),
    (
        "subclass-literal-object",
        "turtle",
        PREFIXES + '<urn:x:a> rdfs:subClassOf "not-a-class" .',
        "rejected",
        "UNSUPPORTED_RDFS",
    ),
    (
        "shacl-sparql-constraint",
        "turtle",
        PREFIXES + '<urn:x:s> a sh:NodeShape ; sh:sparql [ sh:select "?s" ] .',
        "rejected",
        "UNSUPPORTED_SHACL",
    ),
    (
        "shacl-arbitrary-shape",
        "turtle",
        PREFIXES + "<urn:x:s> a sh:NodeShape ; sh:closed true .",
        "rejected",
        "UNSUPPORTED_SHACL",
    ),
    (
        "shacl-logic-composition",
        "turtle",
        PREFIXES + "<urn:x:s> sh:not <urn:x:t> .",
        "rejected",
        "UNSUPPORTED_SHACL",
    ),
    (
        "shacl-template-with-second-constraint",
        "turtle",
        PREFIXES
        + "<urn:ontolearn:shape:c1> a sh:NodeShape ;\n"
        + "    sh:targetClass <urn:x:c> ;\n"
        + "    sh:property <urn:ontolearn:shape:c1:property> .\n"
        + "<urn:ontolearn:shape:c1:property> a sh:PropertyShape ;\n"
        + "    sh:path <urn:x:p> ;\n"
        + "    sh:minCount 1 ;\n"
        + "    sh:datatype xsd:string .\n",
        "rejected",
        "UNSUPPORTED_SHACL",
    ),
    (
        "shacl-inverse-path",
        "turtle",
        PREFIXES + "<urn:x:s> sh:inversePath <urn:x:p> .",
        "rejected",
        "UNSUPPORTED_SHACL_PATH",
    ),
    (
        "shacl-alternative-path",
        "turtle",
        PREFIXES + "<urn:x:s> sh:alternativePath ( <urn:x:p> ) .",
        "rejected",
        {"UNSUPPORTED_SHACL_PATH", "UNSUPPORTED_BLANK_NODE"},
    ),
    (
        "generic-blank-node",
        "turtle",
        PREFIXES + "<urn:x:a> <urn:x:p> [ <urn:x:q> <urn:x:r> ] .",
        "rejected",
        "UNSUPPORTED_BLANK_NODE",
    ),
    (
        "labeled-blank-node",
        "turtle",
        PREFIXES + "_:b1 <urn:x:p> <urn:x:r> .",
        "rejected",
        "UNSUPPORTED_BLANK_NODE",
    ),
    (
        "generic-rdf-list",
        "turtle",
        PREFIXES + "<urn:x:list> rdf:first <urn:x:a> .",
        "rejected",
        "UNSUPPORTED_BLANK_NODE",
    ),
    (
        "unsupported-datatype",
        "turtle",
        PREFIXES + '<urn:x:a> <urn:x:p> "2024"^^xsd:gYear .',
        "rejected",
        "UNSUPPORTED_LITERAL_DATATYPE",
    ),
]


def uid():
    return str(uuid4())


def frame(actor, method, params):
    return {
        "kind": "request",
        "id": uid(),
        "protocolVersion": 2 if method == "hello" else 3,
        "engineSessionId": None if method == "hello" else actor.session,
        "method": method,
        "params": params,
    }


def exchange(actor, method, params):
    request = frame(actor, method, params)
    response = actor.request(request)
    actor.finish_query_reply(request["id"], emitted=True)
    return response


def ok(response):
    assert response["ok"], response
    return response["result"]


@pytest.fixture
def owned(tmp_path):
    store = JobStore(tmp_path / "import.sqlite", contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
    created = ok(
        exchange(
            actor,
            "project.create",
            {
                "requestVersion": 1,
                "operationId": uid(),
                "name": "导入检查",
                "initialization": {"kind": "blank"},
            },
        )
    )
    project = created["projectId"]
    ok(exchange(actor, "project.open", {"projectId": project}))
    yield actor, store, project
    actor.mainline.close()
    store.close()


def check(actor, project, turtle, fmt="turtle"):
    return ok(
        exchange(
            actor,
            "project.ontology.import.check",
            {
                "projectId": project,
                "baseUri": BASE,
                "turtleText": turtle,
                "format": fmt,
            },
        )
    )


@pytest.mark.parametrize("name,fmt,turtle,status,codes", CASES, ids=[case[0] for case in CASES])
def test_rejection_table(owned, name, fmt, turtle, status, codes):
    actor, store, project = owned
    internal = store._project(project)
    before_revision = store.revision(internal)
    before_state = store.state(internal)
    result = check(actor, project, turtle, fmt)
    assert result["status"] == status, (name, result)
    assert set(result) == {"status", "reasons"}, result
    assert result["reasons"], name
    expected = {codes} if isinstance(codes, str) else set(codes)
    assert {item["code"] for item in result["reasons"]} == expected, result["reasons"]
    for item in result["reasons"]:
        assert set(item) == {"code", "field", "detail"}
        assert item["detail"] and item["field"]
    # Rejections never write: revision and committed state are byte-identical.
    assert store.revision(internal) == before_revision
    assert store.state(internal) == before_state
    # And no plan is ever emitted for a rejection.
    assert "plan" not in result and "summary" not in result


def test_accepted_document_plans_a_previewable_changeset(owned):
    actor, store, project = owned
    turtle = (
        PREFIXES
        + "<urn:x:Equipment> rdf:type owl:Class .\n"
        + "<urn:x:e1> rdf:type <urn:x:Equipment> ;\n"
        + '    <urn:x:name> "泵站" .\n'
    )
    result = check(actor, project, turtle)
    assert result["status"] == "ok", result
    assert result["summary"]["tripleCount"] == 3
    assert result["summary"]["definitionCount"] == 1
    assert result["summary"]["manualFactCount"] == 2
    assert result["summary"]["baseRevision"] == store.revision(store._project(project))
    # The plan is a legal ChangeSet input: the original preview accepts it.
    host = {
        "host_client_id": actor.host_client_id,
        "engine_session_id": actor.session,
    }
    base = store.project_get(project)["projectRevision"]
    ready = store.preview_changeset(
        project,
        base,
        {
            "projectId": project,
            "baseRevision": base,
            "intent": "change",
            "plan": result["plan"],
        },
        limits=None
        or {
            "startupMs": 10000,
            "handshakeMs": 5000,
            "requestMs": 5000,
            "heartbeatMs": 10000,
            "cancelGraceMs": 5000,
            "totalMs": 120000,
            "maxFrameBytes": 262144,
            "maxQueuedJobs": 32,
            "maxConcurrentJobs": 2,
            "maxPageItems": 100,
            "maxPageBytes": 131072,
            "maxWorkerMemoryBytes": 536870912,
        },
        **host,
    )
    assert ready["status"] == "ready", ready


def test_template_shape_round_trip_and_list_values(owned):
    actor, _, project = owned
    turtle = (
        PREFIXES
        + "<urn:ontolearn:shape:level> a sh:NodeShape ;\n"
        + "    sh:targetClass <urn:x:Alarm> ;\n"
        + "    sh:property <urn:ontolearn:shape:level:property> .\n"
        + "<urn:ontolearn:shape:level:property> a sh:PropertyShape ;\n"
        + "    sh:path <urn:x:level> ;\n"
        + '    sh:in ( "High" "Low" ) .\n'
    )
    result = check(actor, project, turtle)
    assert result["status"] == "ok", result
    assert result["summary"]["definitionCount"] == 1
    definition = result["plan"]["definitions"][0]
    assert definition["layer"] == "constraint" and definition["id"] == "level"
    assert definition["value"]["template"] == "allowedValues"
    assert definition["value"]["parameters"]["values"] == ['"High"', '"Low"']
    assert definition["value"]["targetClass"] == "urn:x:Alarm"
    assert definition["value"]["path"] == "urn:x:level"
    assert definition["value"]["enabled"] is True
    assert definition["value"]["schemaVersion"] == 1


def test_rejection_is_repeatable_and_stateless(owned):
    actor, store, project = owned
    bad = PREFIXES + "<urn:x:a> owl:disjointWith <urn:x:b> ."
    for _ in range(2):
        result = check(actor, project, bad)
        assert result["status"] == "rejected", result
        assert {item["code"] for item in result["reasons"]} == {"UNSUPPORTED_OWL"}
    assert store.revision(store._project(project)) == 0


def shape_turtle(constraint_text, shape_id="c1"):
    """One well-formed template node/property shape with a custom constraint."""
    return (
        PREFIXES
        + f"<urn:ontolearn:shape:{shape_id}> a sh:NodeShape ;\n"
        + "    sh:targetClass <urn:x:c> ;\n"
        + f"    sh:property <urn:ontolearn:shape:{shape_id}:property> .\n"
        + f"<urn:ontolearn:shape:{shape_id}:property> a sh:PropertyShape ;\n"
        + "    sh:path <urn:x:p> ;\n"
        + f"    {constraint_text} .\n"
    )


def assert_session_stays_readable(actor, project):
    """A structured rejection must never freeze the business session (B03)."""
    state = ok(exchange(actor, "project.get", {"projectId": project}))
    assert state["projectId"] == project
    exported = ok(exchange(actor, "project.ontology.export", {"projectId": project}))
    assert exported["status"] == "ok", exported


def test_shacl_list_blank_node_element_rejects_and_keeps_session_readable(owned):
    actor, store, project = owned
    internal = store._project(project)
    before = store.state(internal)
    result = check(actor, project, shape_turtle("sh:in ( [ <urn:x:q> <urn:x:r> ] )"))
    assert result["status"] == "rejected", result
    codes = {item["code"] for item in result["reasons"]}
    assert "UNSUPPORTED_BLANK_NODE" in codes, result["reasons"]
    assert store.state(internal) == before
    assert_session_stays_readable(actor, project)


def test_shacl_list_unsupported_datatype_rejects_and_keeps_session_readable(owned):
    actor, _, project = owned
    result = check(actor, project, shape_turtle('sh:in ( "2024"^^xsd:gYear )'))
    assert result["status"] == "rejected", result
    codes = {item["code"] for item in result["reasons"]}
    assert "UNSUPPORTED_LITERAL_DATATYPE" in codes, result["reasons"]
    assert_session_stays_readable(actor, project)


def test_shacl_list_ill_typed_literal_rejects_and_keeps_session_readable(owned):
    actor, _, project = owned
    result = check(actor, project, shape_turtle('sh:in ( "abc"^^xsd:integer )'))
    assert result["status"] == "rejected", result
    codes = {item["code"] for item in result["reasons"]}
    assert "UNSUPPORTED_LITERAL_DATATYPE" in codes, result["reasons"]
    assert_session_stays_readable(actor, project)


def test_property_shape_rejects_node_shape_predicates(owned):
    actor, _, project = owned
    for predicate in ("sh:targetClass <urn:x:c>", "sh:property <urn:x:other>"):
        turtle = (
            PREFIXES
            + "<urn:ontolearn:shape:c1> a sh:NodeShape ;\n"
            + "    sh:targetClass <urn:x:c> ;\n"
            + "    sh:property <urn:ontolearn:shape:c1:property> .\n"
            + "<urn:ontolearn:shape:c1:property> a sh:PropertyShape ;\n"
            + "    sh:path <urn:x:p> ;\n"
            + f"    {predicate} .\n"
        )
        result = check(actor, project, turtle)
        assert result["status"] == "rejected", result
        assert {item["code"] for item in result["reasons"]} == {"UNSUPPORTED_SHACL"}


def test_deactivated_must_be_strict_single_boolean(owned):
    actor, _, project = owned
    cases = [
        # typed-as-string "true" is not a boolean literal
        'sh:deactivated "true"^^xsd:string',
        # integer is not a boolean literal
        "sh:deactivated 1",
    ]
    for extra in cases:
        turtle = (
            PREFIXES
            + "<urn:ontolearn:shape:c1> a sh:NodeShape ;\n"
            + "    sh:targetClass <urn:x:c> ;\n"
            + f"    {extra} ;\n"
            + "    sh:property <urn:ontolearn:shape:c1:property> .\n"
            + "<urn:ontolearn:shape:c1:property> a sh:PropertyShape ;\n"
            + "    sh:path <urn:x:p> ;\n"
            + "    sh:minCount 1 .\n"
        )
        result = check(actor, project, turtle)
        assert result["status"] == "rejected", result
        assert {item["code"] for item in result["reasons"]} == {"UNSUPPORTED_SHACL"}
    # two values on the same node shape are ambiguous and rejected
    turtle = (
        PREFIXES
        + "<urn:ontolearn:shape:c1> a sh:NodeShape ;\n"
        + "    sh:targetClass <urn:x:c> ;\n"
        + "    sh:deactivated true, false ;\n"
        + "    sh:property <urn:ontolearn:shape:c1:property> .\n"
        + "<urn:ontolearn:shape:c1:property> a sh:PropertyShape ;\n"
        + "    sh:path <urn:x:p> ;\n"
        + "    sh:minCount 1 .\n"
    )
    result = check(actor, project, turtle)
    assert result["status"] == "rejected", result
    assert {item["code"] for item in result["reasons"]} == {"UNSUPPORTED_SHACL"}


def test_numeric_range_bounds_are_strictly_validated(owned):
    actor, _, project = owned
    bad_bounds = [
        # multi-value bound must not be silently collapsed
        "sh:minInclusive 1, 2",
        # boolean is not a numeric bound
        "sh:minInclusive true",
        # non-numeric text with a datatype outside the numeric set
        'sh:minInclusive "abc"^^xsd:string',
        # well-typed numeric datatype but non-numeric lexical
        'sh:maxInclusive "abc"^^xsd:integer',
        # one good bound cannot hide a broken second bound
        'sh:minInclusive 0 ;\n    sh:maxInclusive "abc"^^xsd:integer',
    ]
    for constraint in bad_bounds:
        result = check(actor, project, shape_turtle(constraint))
        assert result["status"] == "rejected", (constraint, result)
        assert {item["code"] for item in result["reasons"]} == {"UNSUPPORTED_SHACL"}, constraint
    # Legal integer bounds stay exchangeable.
    result = check(actor, project, shape_turtle("sh:minInclusive 0 ;\n    sh:maxInclusive 10"))
    assert result["status"] == "ok", result
    definition = result["plan"]["definitions"][0]["value"]
    assert definition["template"] == "numericRange"
    assert definition["parameters"] == {"minInclusive": "0", "maxInclusive": "10"}


@pytest.mark.parametrize(
    "turtle, codes",
    [
        # B08: lexically distinct integers that fold onto "1"^^xsd:integer
        (
            PREFIXES + "<urn:x:a> <urn:x:p> 1, +01 .\n",
            {"UNSUPPORTED_LITERAL_DATATYPE"},
        ),
        # boolean lexical fold: "0"^^xsd:boolean and false both store "false"
        (
            PREFIXES + '<urn:x:a> <urn:x:p> "0"^^xsd:boolean, false .\n',
            {"UNSUPPORTED_LITERAL_DATATYPE"},
        ),
        # ill-typed literal content
        (
            PREFIXES + '<urn:x:a> <urn:x:p> "abc"^^xsd:integer .\n',
            {"UNSUPPORTED_LITERAL_DATATYPE"},
        ),
    ],
    ids=["integer-lexical-fold", "boolean-lexical-fold", "ill-typed"],
)
def test_normalizing_literal_collisions_reject_whole_batch(owned, turtle, codes):
    actor, store, project = owned
    internal = store._project(project)
    before = store.state(internal)
    result = check(actor, project, turtle)
    assert result["status"] == "rejected", result
    assert {item["code"] for item in result["reasons"]} == codes
    assert "plan" not in result
    assert store.state(internal) == before
    assert_session_stays_readable(actor, project)


def test_distinct_lexical_forms_that_stay_distinct_are_kept(owned):
    # 1.0/1.00 decimals and boolean-vs-integer pairs do not fold onto one
    # stored value: both literals survive as distinct facts (no silent merge,
    # hence no rejection). Exact duplicate triples - and case-insensitive
    # language tags, one literal under RDF 1.1 - count exactly once.
    actor, _, project = owned
    turtle = (
        PREFIXES
        + '<urn:x:a> <urn:x:p1> "1.0"^^xsd:decimal, "1.00"^^xsd:decimal .\n'
        + "<urn:x:a> <urn:x:p2> true, 1 .\n"
        + "<urn:x:a> <urn:x:p3> 1 .\n"
        + "<urn:x:a> <urn:x:p3> 1 .\n"
        + '<urn:x:a> <urn:x:p4> "foo"@en, "foo"@EN .\n'
    )
    result = check(actor, project, turtle)
    assert result["status"] == "ok", result
    assert result["summary"]["tripleCount"] == 6
    assert result["summary"]["manualFactCount"] == 6
    objects = {fact["predicate"]: fact["object"] for fact in result["plan"]["manual"]}
    assert objects["urn:x:p3"] == '"1"^^<http://www.w3.org/2001/XMLSchema#integer>'
    assert objects["urn:x:p4"] == '"foo"@en'
    assert len({fact["id"] for fact in result["plan"]["manual"]}) == 6


def test_long_and_escaped_literals_round_trip_through_the_plan(owned):
    actor, _, project = owned
    long_text = "长" * 4096
    turtle = (
        PREFIXES
        + f'<urn:x:a> <urn:x:p1> "{long_text}" .\n'
        + '<urn:x:a> <urn:x:p2> "quote \\" backslash \\\\ newline \\n tab \\t" .\n'
    )
    result = check(actor, project, turtle)
    assert result["status"] == "ok", result
    from ontolearn_engine.rdf_snapshot import term

    objects = {fact["predicate"]: fact["object"] for fact in result["plan"]["manual"]}
    assert str(term(objects["urn:x:p1"])) == long_text
    assert str(term(objects["urn:x:p2"])) == 'quote " backslash \\ newline \n tab \t'


def test_deactivated_true_round_trips_enabled_false(owned):
    actor, _, project = owned
    turtle = (
        PREFIXES
        + "<urn:ontolearn:shape:c1> a sh:NodeShape ;\n"
        + "    sh:targetClass <urn:x:c> ;\n"
        + "    sh:deactivated true ;\n"
        + "    sh:property <urn:ontolearn:shape:c1:property> .\n"
        + "<urn:ontolearn:shape:c1:property> a sh:PropertyShape ;\n"
        + "    sh:path <urn:x:p> ;\n"
        + "    sh:minCount 1 .\n"
    )
    result = check(actor, project, turtle)
    assert result["status"] == "ok", result
    definition = result["plan"]["definitions"][0]["value"]
    assert definition["enabled"] is False
    # sh:deactivated false keeps the constraint enabled.
    result = check(actor, project, turtle.replace("sh:deactivated true", "sh:deactivated false"))
    assert result["status"] == "ok", result
    assert result["plan"]["definitions"][0]["value"]["enabled"] is True
