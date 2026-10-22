"""Four approved SHACL entry repairs through the actual parser and Validator."""

import hashlib
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from ontolearn_engine import semantic
from ontolearn_engine.semantic_offline import SemanticError

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "docs/reviews/T05/profile-M1-math-explanation-input-contract"
INPUTS = json.loads((FIXTURES / "consumer-C-inputs.json").read_bytes())["cases"]
GOLDENS = json.loads((FIXTURES / "consumer-C-goldens.json").read_bytes())["cases"]
FIXED_IDS = (
    "C-langString",
    "C-inclusive-nni",
    "C-inclusive-dateTime-equal",
    "C-inclusive-dateTime-before",
)
PREFIX = """@prefix ex: <urn:shape-entry:> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
"""


def observe(data, shapes, identity):
    """Record actual constructor-independent run, without supplying a report."""
    original_run = semantic.Validator.run
    calls = []
    record = {"id": identity, "validatorCalls": 0, "report": None, "error": None}

    def run(self, *args, **kwargs):
        calls.append(1)
        return original_run(self, *args, **kwargs)

    try:
        with patch.object(semantic.Validator, "run", run):
            actual_data = semantic.parse_turtle(data)
            actual_shapes = semantic.parse_turtle(shapes, shapes=True)
            result = semantic.check_shapes(actual_data, actual_shapes)
        record["report"] = result
        return result, len(calls)
    except SemanticError as error:
        record["error"] = error.code
        assert not calls, "entry rejection occurred after real Validator execution"
        raise
    finally:
        record["validatorCalls"] = len(calls)
        directory = os.environ.get("I05_SHAPE_EVIDENCE_DIR")
        if directory:
            dest = Path(directory)
            dest.mkdir(parents=True, exist_ok=True)
            name = hashlib.sha256(identity.encode()).hexdigest() + ".json"
            (dest / name).write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")


def fixture_case(identity):
    return next(case for case in INPUTS if case["id"] == identity)


def complete_rows(rows):
    return [
        {
            "focusNode": row["focus"],
            "resultPath": row["path"],
            "sourceShape": row["sourceShape"],
            "sourceConstraintComponent": row["constraint"],
            "resultSeverity": row["severity"],
            "value": row["value"],
        }
        for row in rows
    ]


@pytest.mark.parametrize("identity", FIXED_IDS)
def test_original_four_inputs_reach_actual_validator_and_full_normative_report(identity):
    case = fixture_case(identity)
    # Only pure input reaches production. Golden is read after the real call.
    report, calls = observe(case["dataTurtle"], case["shapesTurtle"], identity)
    expected = next(case["expected"] for case in GOLDENS if case["id"] == identity)
    assert calls == 1
    assert report["conforms"] is expected["conforms"]
    assert complete_rows(report["violations"]) == [
        {name: value for name, value in row.items() if name != "valueExpectation"}
        for row in expected.get("requiredResultRows", [])
    ]


@pytest.mark.parametrize(
    "identity", ["C-datatype-exact", "C-inclusive-numeric", "C-inclusive-type-error"]
)
def test_original_neighboring_datatype_and_range_cells_keep_full_reports(identity):
    case = fixture_case(identity)
    actual, calls = observe(case["dataTurtle"], case["shapesTurtle"], identity)
    expected = next(case["expected"] for case in GOLDENS if case["id"] == identity)
    assert calls == 1 and actual["conforms"] is expected["conforms"]
    assert complete_rows(actual["violations"]) == [
        {name: value for name, value in row.items() if name != "valueExpectation"}
        for row in expected.get("requiredResultRows", [])
    ]


def shape(parameter):
    return PREFIX + (
        "ex:node a sh:NodeShape; sh:targetClass ex:Focus; sh:property ex:shape .\n"
        "ex:shape a sh:PropertyShape; sh:path ex:p; " + parameter + " ."
    )


def data(value='"2"^^xsd:nonNegativeInteger'):
    return PREFIX + "ex:s a ex:Focus; ex:p " + value + " ."


@pytest.mark.parametrize(
    ("parameter", "error"),
    [
        ('sh:minInclusive "-1"^^xsd:nonNegativeInteger', "INVALID_LITERAL_LEXICAL"),
        ('sh:maxInclusive "bad"^^xsd:nonNegativeInteger', "INVALID_LITERAL_LEXICAL"),
        ('sh:minInclusive "2000-99-01T00:00:00Z"^^xsd:dateTime', "INVALID_LITERAL_LEXICAL"),
        ('sh:maxInclusive "not-a-date"^^xsd:dateTime', "INVALID_LITERAL_LEXICAL"),
        ('sh:minInclusive "2"', "INVALID_SHAPE"),
        ('sh:minInclusive "2000-01-01Z"^^xsd:date', "INVALID_SHAPE"),
        ("sh:datatype <urn:unknown-datatype>", "UNSUPPORTED_DATATYPE"),
        ('sh:datatype "not-an-iri"', "SHAPE_DATATYPE_INVALID"),
        ("sh:minCount -1", "INVALID_SHAPE"),
        ("sh:maxCount true", "INVALID_SHAPE"),
        ("sh:minInclusive <urn:not-a-literal>", "INVALID_SHAPE"),
    ],
)
def test_independent_invalid_parameters_rejected_before_validator(parameter, error):
    with pytest.raises(SemanticError) as caught:
        observe(data(), shape(parameter), "independent-invalid:" + parameter)
    assert caught.value.code == error


@pytest.mark.parametrize(
    "change",
    [
        lambda text: text.replace("sh:path ex:p", "sh:path ex:p, ex:q"),
        lambda text: text.replace("sh:targetClass ex:Focus", "sh:targetClass ex:Focus, ex:Other"),
        lambda text: text.replace("sh:minInclusive", "sh:arbitraryConstraint"),
    ],
)
def test_independent_structural_rejection_keeps_validator_unexecuted(change):
    with pytest.raises(SemanticError):
        observe(
            data(),
            change(shape('sh:minInclusive "0"^^xsd:nonNegativeInteger')),
            "structure:" + change.__name__ + change(shape("sh:minCount 1")),
        )


@pytest.mark.parametrize(
    "parameter",
    ['sh:minInclusive "0"^^xsd:nonNegativeInteger', 'sh:maxInclusive "2"^^xsd:nonNegativeInteger'],
)
def test_independent_nni_zero_and_closed_upper_bound(parameter):
    report, calls = observe(data(), shape(parameter), "nni-boundary:" + parameter)
    assert calls == 1 and report == {"conforms": True, "violations": []}


@pytest.mark.parametrize("side", ["data", "shape"])
def test_external_import_is_denied_before_validator(side):
    source, constraints = data(), shape("sh:datatype rdf:langString")
    imports = "\n<urn:x> <http://www.w3.org/2002/07/owl#imports> <https://example.invalid/x> ."
    if side == "data":
        source += imports
    else:
        constraints += imports
    with pytest.raises(SemanticError) as caught:
        observe(source, constraints, "external-import:" + side)
    assert caught.value.code == "EXTERNAL_ACCESS_DENIED"


def test_illtyped_data_entry_stays_rejected_before_validator():
    case = fixture_case("C-illtyped-entry")
    with pytest.raises(SemanticError) as caught:
        observe(case["dataTurtle"], case["shapesTurtle"], case["id"])
    assert caught.value.code == "INVALID_LITERAL_LEXICAL"
