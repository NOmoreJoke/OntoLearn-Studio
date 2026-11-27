"""Real immutable inputs, lexical terms, selected output and safe worker errors."""

import copy
import json
import subprocess
import sys
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from ontolearn_engine import semantic
from ontolearn_engine.semantic_execution import (
    SEMANTIC_CAPABILITIES,
    SemanticExecutionFault,
    SemanticRequestFault,
    _rows,
    build_request,
    execute_request,
)
from ontolearn_engine.semantic_scopes import _digest
from rdflib import RDF, RDFS, XSD

ROOT = Path(__file__).resolve().parents[3]
CANONICAL = ROOT / "packages/contracts/v2"


@pytest.fixture
def errors():
    return {
        "error_catalog": json.loads((CANONICAL / "errors.json").read_text()),
        "error_schema": json.loads((CANONICAL / "schema.json").read_text()),
    }


def definition(layer, identity, payload):
    return {"layer": layer, "id": identity, "payload": json.dumps(payload)}


def triple(s, p, o):
    return {"subject": s, "predicate": p, "object": o}


def fixture():
    return {
        "project": "P1",
        "projectRevision": 1,
        "dependencyVector": {},
        "state": {
            "mappingState": {},
            "facts": [
                {
                    "id": "F1",
                    **triple("urn:s", str(RDF.type), "<urn:Child>"),
                    "owner": None,
                    "source_row": None,
                    "managed_value": None,
                },
                {
                    "id": "F2",
                    **triple("urn:s", "urn:count", '"01"^^<' + str(XSD.integer) + ">"),
                    "owner": None,
                    "source_row": None,
                    "managed_value": None,
                },
                {
                    "id": "F3",
                    **triple("urn:s", "urn:name", None),
                    "owner": "M1",
                    "source_row": "row1",
                    "managed_value": '"deleted"',
                },
            ],
            "definitions": [
                definition(
                    "ontology",
                    "O1",
                    {"triples": [triple("urn:Child", str(RDFS.subClassOf), "<urn:Parent>")]},
                ),
                definition(
                    "rule",
                    "R1",
                    {
                        "enabled": True,
                        "when": [["?s", RDF.type.n3(), "<urn:Parent>"]],
                        "then": ["?s", RDF.type.n3(), "<urn:Risk>"],
                    },
                ),
                definition(
                    "rule",
                    "R2",
                    {
                        "enabled": True,
                        "when": [["?s", RDF.type.n3(), "<urn:Risk>"]],
                        "then": ["?s", RDF.type.n3(), "<urn:Next>"],
                    },
                ),
                definition("query", "Q1", {"text": "SELECT ?s ?p ?o WHERE {?s ?p ?o}"}),
                definition(
                    "constraint",
                    "C1",
                    {
                        "enabled": True,
                        "turtle": """
@prefix sh: <http://www.w3.org/ns/shacl#> .
<urn:Shape> a sh:NodeShape; sh:targetClass <urn:Parent>; sh:property <urn:Property> .
<urn:Property> sh:path <urn:name>; sh:minCount 1 .
""",
                    },
                ),
            ],
        },
    }


def request(snapshot=None, capability="reasoning.execute", *, selected=None, parameters=None):
    snapshot = fixture() if snapshot is None else snapshot
    identity = {"query.execute": "Q1", "reasoning.execute": "all", "validation.execute": "C1"}
    input_ = {
        "inputSnapshotId": _digest(snapshot),
        "scope": "asserted+derived" if selected else "asserted",
        "definitionId": identity[capability],
        "parametersHash": _digest(parameters or {}),
        "derivedResultIds": [selected["metadata"]["resultId"]] if selected else [],
        "preparedPlanRef": None,
    }
    return build_request(snapshot, capability, input_, parameters or {}, selected)


def selected_from(output, req):
    return {
        "metadata": {
            "resultId": str(uuid4()),
            "kind": "reasoning",
            "inputSnapshotId": req["input"]["inputSnapshotId"],
        },
        "payload": output["payload"],
    }


def run(req, errors):
    return execute_request(req, **errors)


def test_capabilities_and_real_rdfs_one_pass_rule_complete_output(errors):
    assert SEMANTIC_CAPABILITIES == {"query.execute", "reasoning.execute", "validation.execute"}
    output = run(request(), errors)
    payload = output["payload"]
    assert payload["executionSemanticsVersion"] == semantic.SEMANTICS_VERSION == "i05-finite-6"
    assert payload["reasoning"]["rdfs"] == [["<urn:s>", RDF.type.n3(), "<urn:Parent>"]]
    assert payload["reasoning"]["rules"] == [["<urn:s>", RDF.type.n3(), "<urn:Risk>"]]
    assert payload["reasoning"]["warnings"] == ["RULE_CHAIN_UNSUPPORTED:R2"]
    assert payload["reasoning"]["evidence"][0]["rule"] == "R1"
    assert payload["assertedFacts"] == [
        ["<urn:s>", RDF.type.n3(), "<urn:Child>"],
        ["<urn:s>", "<urn:count>", '"01"^^<' + str(XSD.integer) + ">"],
    ]
    assert all(UUID(row["rowId"]).version == 4 for row in output["rows"])
    assert [row["ordinal"] for row in output["rows"]] == list(range(len(output["rows"])))
    assert output["rows"][0]["cells"] == ["columns", "path", "value", "part", "parts"]


def test_build_request_copies_and_does_not_compute(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("build must not parse or compute")

    monkeypatch.setattr(semantic, "reason", forbidden)
    monkeypatch.setattr(semantic, "query", forbidden)
    monkeypatch.setattr(semantic, "parse_turtle", forbidden)
    snapshot = fixture()
    req = request(snapshot)
    snapshot["state"]["facts"].clear()
    assert len(req["snapshot"]["state"]["facts"]) == 3
    assert json.loads(json.dumps(req)) == req


def test_coordinator_request_construction_never_imports_heavy_libraries(errors):
    req = request()
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import json, sys
from ontolearn_engine.semantic_execution import build_request
data = json.loads(sys.stdin.read())
r = data["request"]
build_request(r["snapshot"], r["capability"], r["input"], r["parameters"], r["selected"],
              **data["errors"])
assert not any(m == "rdflib" or m.startswith("rdflib.") or m == "pyshacl"
               or m.startswith("pyshacl.") for m in sys.modules)
assert "ontolearn_engine.semantic" not in sys.modules
assert "ontolearn_engine.semantic_scopes" not in sys.modules
""",
        ],
        input=json.dumps({"request": req, "errors": errors}),
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_query_preserves_lexical_form_tombstone_and_scope(errors):
    result = run(request(capability="query.execute"), errors)["payload"]
    assert result["query"] == {
        "type": "SELECT",
        "variables": ["s", "p", "o"],
        "rows": [
            ["<urn:s>", RDF.type.n3(), "<urn:Child>"],
            ["<urn:s>", "<urn:count>", '"01"^^<' + str(XSD.integer) + ">"],
        ],
    }
    assert result["provenance"]["ontologyView"] == [
        ["<urn:Child>", RDFS.subClassOf.n3(), "<urn:Parent>"]
    ]


def test_selected_existing_result_no_recompute_and_real_shacl(errors, monkeypatch):
    initial = request()
    selection = selected_from(run(initial, errors), initial)

    def forbidden(*args, **kwargs):
        raise AssertionError("selected reasoning cannot recompute")

    monkeypatch.setattr(semantic, "reason", forbidden)
    asserted = run(request(capability="validation.execute"), errors)["payload"]
    derived = run(request(capability="validation.execute", selected=selection), errors)["payload"]
    assert asserted["report"] == {"conforms": True, "violations": []}
    assert derived["report"] == {
        "conforms": False,
        "violations": [
            {
                "focus": "<urn:s>",
                "path": "<urn:name>",
                "constraint": "<http://www.w3.org/ns/shacl#MinCountConstraintComponent>",
                "sourceShape": "<urn:Property>",
                "value": None,
                "severity": "<http://www.w3.org/ns/shacl#Violation>",
            }
        ],
    }
    assert derived["selectedResultIds"] == [selection["metadata"]["resultId"]]
    assert derived["projection"]["factViewSha256"] == derived["provenance"]["factViewSha256"]
    assert derived["constraintsHash"] != derived["inputSnapshotId"]
    queried = run(request(capability="query.execute", selected=selection), errors)["payload"]
    assert ["<urn:s>", RDF.type.n3(), "<urn:Risk>"] in queried["query"]["rows"]
    assert ["<urn:s>", RDF.type.n3(), "<urn:Next>"] not in queried["query"]["rows"]


@pytest.mark.parametrize(
    "change",
    [
        lambda r: r["selected"]["payload"]["reasoning"]["rules"].clear(),
        lambda r: r["selected"]["payload"]["source"].update(assertedInputSha256="0" * 64),
        lambda r: r["selected"]["metadata"].update(resultId=str(uuid4())),
        lambda r: r["selected"]["payload"].update(inputSnapshotId="0" * 64),
    ],
)
def test_corrupt_existing_selection_is_internal_not_recomputed(errors, change):
    initial = request()
    selection = selected_from(run(initial, errors), initial)
    req = request(capability="validation.execute", selected=selection)
    change(req)
    with pytest.raises(SemanticExecutionFault) as failure:
        run(req, errors)
    assert failure.value.error == {
        "code": "INTERNAL_ERROR",
        "messageKey": "engine.internal",
        "params": {},
        "retryable": False,
    }


@pytest.mark.parametrize(
    "params",
    [
        {"url": "https://canary.invalid/secret"},
        {"inputSelection": True},
        {"inputSelection": "future"},
    ],
)
def test_public_parameter_errors_need_canonical_injection(errors, params):
    req = request()
    with pytest.raises(SemanticRequestFault):
        build_request(req["snapshot"], req["capability"], req["input"], params)
    with pytest.raises(SemanticExecutionFault) as failure:
        build_request(req["snapshot"], req["capability"], req["input"], params, **errors)
    assert failure.value.error == {
        "code": "INVALID_REQUEST",
        "messageKey": "protocol.invalidRequest",
        "params": {"field": "params"},
        "retryable": False,
    }


@pytest.mark.parametrize(
    "text,code,params",
    [
        (
            "SELECT * WHERE { SERVICE <http://127.0.0.1:9/secret> {?s ?p ?o} }",
            "NETWORK_FORBIDDEN",
            {},
        ),
        ("SELECT * FROM <http://127.0.0.1:9/secret> WHERE {?s ?p ?o}", "NETWORK_FORBIDDEN", {}),
        ("SELECT (RAND() AS ?x) WHERE {}", "UNSUPPORTED_CONSTRUCT", {"construct": "queryFunction"}),
        ("not a query secret", "SEMANTIC_INPUT_INVALID", {"field": "query"}),
    ],
)
def test_real_query_producer_error_classification(errors, text, code, params):
    snapshot = fixture()
    snapshot["state"]["definitions"][-2]["payload"] = json.dumps({"text": text})
    with pytest.raises(SemanticExecutionFault) as failure:
        run(request(snapshot, "query.execute"), errors)
    assert failure.value.error["code"] == code
    assert failure.value.error["params"] == params
    assert "secret" not in str(failure.value) + json.dumps(failure.value.error)


def test_unknown_exception_never_infers_reason_from_text(errors, monkeypatch):
    def broken(*args, **kwargs):
        raise ValueError("EXTERNAL_ACCESS_DENIED path=/secret/token")

    monkeypatch.setattr(semantic, "query", broken)
    with pytest.raises(SemanticExecutionFault) as failure:
        run(request(capability="query.execute"), errors)
    assert failure.value.error["code"] == "INTERNAL_ERROR"
    assert "secret" not in str(failure.value) + json.dumps(failure.value.error)


def test_rows_losslessly_split_long_values_and_preserve_every_basis():
    payload = {"evidence": [{"basis": ["x" * 20000, "last input"]}], "empty": []}
    rows = _rows(payload)
    pieces = [row["cells"] for row in rows[1:] if row["cells"][0] == "/evidence/0/basis/0"]
    assert [p[2:] for p in pieces] == [[1, 3], [2, 3], [3, 3]]
    assert json.loads("".join(p[1] for p in pieces)) == "x" * 20000
    assert rows[-1]["cells"][1] == '"last input"'
    assert all(len(cell) <= 8192 for row in rows for cell in row["cells"] if isinstance(cell, str))


def test_output_limit_is_explicit_and_never_truncates(errors, monkeypatch):
    from ontolearn_engine import semantic_execution

    monkeypatch.setattr(semantic_execution, "MAX_ROWS", 3)
    with pytest.raises(SemanticExecutionFault) as failure:
        run(request(), errors)
    assert failure.value.error["code"] == "RESOURCE_LIMIT"
    assert failure.value.error["params"] == {"resource": "semanticResult"}


def test_historical_selection_is_explicit_and_input_immutable(errors):
    req = request(parameters={"inputSelection": "historical"})
    before = copy.deepcopy(req)
    assert run(req, errors)["payload"]["inputSelection"] == "historical"
    assert req == before


@pytest.mark.parametrize(
    "text,code,message,params",
    [
        (
            "ASK { GRAPH <urn:g> { ?s ?p ?o } }",
            "UNSUPPORTED_CONSTRUCT",
            "semantics.unsupportedConstruct",
            {"construct": "sparqlForm"},
        ),
        (
            "SELECT ?s WHERE { GRAPH ?g { ?s ?p ?o } }",
            "UNSUPPORTED_CONSTRUCT",
            "semantics.unsupportedConstruct",
            {"construct": "sparqlForm"},
        ),
        (
            "ASK { GRAPH <urn:g> { SERVICE <https://private.invalid/> { ?s ?p ?o } } }",
            "NETWORK_FORBIDDEN",
            "semantics.networkForbidden",
            {},
        ),
        (
            "ASK FROM <https://private.invalid/> { GRAPH ?g { ?s ?p ?o } }",
            "NETWORK_FORBIDDEN",
            "semantics.networkForbidden",
            {},
        ),
    ],
)
def test_actual_named_graph_reason_and_nested_external_priority(
    errors, text, code, message, params
):
    snapshot = fixture()
    next(d for d in snapshot["state"]["definitions"] if d["layer"] == "query")["payload"] = (
        json.dumps({"text": text})
    )
    with pytest.raises(SemanticExecutionFault) as failure:
        run(request(snapshot, "query.execute"), errors)
    assert failure.value.error == {
        "code": code,
        "messageKey": message,
        "params": params,
        "retryable": False,
    }


def test_local_query_grammar_failure_is_internal_not_bad_user_syntax(errors, monkeypatch):
    from ontolearn_engine import semantic_query

    def incompatible_grammar():
        raise RuntimeError("private implementation details must not escape")

    monkeypatch.setattr(semantic_query, "_clone_grammar", incompatible_grammar)
    with pytest.raises(SemanticExecutionFault) as failure:
        run(request(capability="query.execute"), errors)
    assert failure.value.error == {
        "code": "INTERNAL_ERROR",
        "messageKey": "engine.internal",
        "params": {},
        "retryable": False,
    }


def test_unrelated_opaque_definitions_do_not_expand_asserted_query_dependencies(errors):
    snapshot = fixture()
    snapshot["state"]["definitions"].extend(
        [
            {"layer": "model", "id": "opaque", "payload": '"opaque legacy config"'},
            definition("rule", "futureRule", {"notThisCandidatesRuleFormat": True}),
            definition("constraint", "futureConstraint", {"unrelated": True}),
        ]
    )
    assert run(request(snapshot, "query.execute"), errors)["payload"]["query"]["rows"] == [
        ["<urn:s>", RDF.type.n3(), "<urn:Child>"],
        ["<urn:s>", "<urn:count>", '"01"^^<' + str(XSD.integer) + ">"],
    ]


def test_changed_scope_and_disabled_constraint_do_not_report_pass(errors):
    snapshot = fixture()
    snapshot["state"]["definitions"][-1]["payload"] = json.dumps({"enabled": False, "turtle": ""})
    with pytest.raises(SemanticExecutionFault) as failure:
        run(request(snapshot, "validation.execute"), errors)
    assert failure.value.error["code"] == "SEMANTIC_INPUT_INVALID"
    assert failure.value.error["params"] == {"field": "constraint"}


def test_two_selected_results_and_scenario_are_rejected_before_compute(errors):
    req = request()
    for scope, ids in [("scenario", []), ("asserted+derived", [str(uuid4()), str(uuid4())])]:
        input_ = {**req["input"], "scope": scope, "derivedResultIds": ids}
        with pytest.raises(SemanticExecutionFault):
            build_request(req["snapshot"], req["capability"], input_, {}, **errors)


def test_exact_rows_and_total_byte_boundaries(monkeypatch):
    from ontolearn_engine import semantic_execution
    from ontolearn_engine.semantic_offline import SemanticError

    monkeypatch.setattr(semantic_execution, "MAX_ROWS", 3)
    assert len(_rows({"a": 1, "b": 2})) == 3
    with pytest.raises(SemanticError, match="PROJECTION_RESULT_LIMIT"):
        _rows({"a": 1, "b": 2, "c": 3})
    monkeypatch.setattr(semantic_execution, "MAX_ROWS", 10000)
    monkeypatch.setattr(semantic_execution, "MAX_OUTPUT_BYTES", 200)
    with pytest.raises(SemanticError, match="PROJECTION_RESULT_LIMIT"):
        _rows({"value": "中文" * 100})


@pytest.mark.parametrize(
    "mutation",
    [
        lambda s: s["state"]["facts"][0].update(subject="file:///tmp/local"),
        lambda s: s["state"]["facts"][0].update(object='"x" . <urn:evil> <urn:p> "y"'),
        lambda s: s["state"]["definitions"][0].update(payload='{"triples": false}'),
    ],
)
def test_bad_trusted_snapshot_is_safe_internal(errors, mutation):
    snapshot = fixture()
    mutation(snapshot)
    # file: is an absolute inert IRI and must not be interpreted as a file path.
    if snapshot["state"]["facts"][0]["subject"] == "file:///tmp/local":
        assert run(request(snapshot), errors)["payload"]["reasoning"]["rdfs"][0][0] == (
            "<file:///tmp/local>"
        )
        return
    with pytest.raises((SemanticRequestFault, SemanticExecutionFault)) as failure:
        run(request(snapshot), errors)
    if isinstance(failure.value, SemanticExecutionFault):
        assert failure.value.error["code"] == "INTERNAL_ERROR"
