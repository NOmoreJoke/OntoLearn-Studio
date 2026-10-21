"""Approved frozen T09 input authoring probes; not I05 runtime or project acceptance."""

import hashlib
import json
from pathlib import Path

import pytest
from ontolearn_engine.query_service import compile_visual
from rdflib import Graph, Literal, URIRef

ROOT = Path(__file__).resolve().parents[3]
INPUTS = ROOT / "tests/fixtures/query/approved-baseline"


def verified_input(name):
    manifest_bytes = (INPUTS / "manifest.json").read_bytes()
    assert hashlib.sha256(manifest_bytes).hexdigest() == (
        "aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e"
    )
    manifest = json.loads(manifest_bytes)
    assert manifest["version"] == "prd-v0.6-learning-1"
    path = "tests/fixtures/product-baselines/" + name
    data = (INPUTS / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == manifest["files"][path]
    return data


def new_graph():
    data = json.loads(verified_input("G-base.json"))
    # Read actual declared ontology/facts only. No expected rows or Store helper.
    triples = [*data["ontology"], *data["facts"]]
    text = "\n".join(
        f"<{row['subject']}> <{row['predicate']}> {row['object']} ." for row in triples
    )
    return Graph().parse(data=text, format="turtle")


def visual():
    namespace = json.loads(verified_input("conventions.json"))["namespace"]
    return {
        "classIri": namespace + "Alarm",
        "fields": [],
        "conditions": [
            {
                "predicate": namespace + "level",
                "operator": "eq",
                "value": {
                    "kind": "literal",
                    "value": "High",
                    "language": None,
                    "datatype": None,
                },
            },
            {
                "predicate": namespace + "status",
                "operator": "eq",
                "value": {
                    "kind": "literal",
                    "value": "Open",
                    "language": None,
                    "datatype": None,
                },
            },
        ],
    }


@pytest.mark.parametrize("closed", [False, True])
def test_approved_q01_q02_inputs_have_complete_expected_authoring_rows(closed):
    original = verified_input("unclosed-high.rq").decode("utf-8")
    generated = compile_visual(visual())
    for sparql in [original, generated]:
        graph = new_graph()  # Independent reset for every query/variant.
        if closed:
            graph.set(
                (
                    URIRef("urn:ontolearn:learning:alarm/A01"),
                    URIRef("urn:ontolearn:learning:status"),
                    Literal("Closed"),
                )
            )
        actual = [[str(value) for value in row] for row in graph.query(sparql)]
        assert actual == ([] if closed else [["urn:ontolearn:learning:alarm/A01"]])


def test_equal_count_wrong_semantics_is_not_the_expected_answer():
    """A valid query for Closed/High yields A02, which must not pass as A01."""
    correct = verified_input("unclosed-high.rq").decode("utf-8")
    wrong = correct.replace('"Open"', '"Closed"')
    correct_rows = [[str(value) for value in row] for row in new_graph().query(correct)]
    wrong_rows = [[str(value) for value in row] for row in new_graph().query(wrong)]
    assert correct_rows == [["urn:ontolearn:learning:alarm/A01"]]
    assert wrong_rows == [["urn:ontolearn:learning:alarm/A02"]]
    assert len(wrong_rows) == len(correct_rows)
    assert wrong_rows != correct_rows  # Fixed full answer comparison, never count-only acceptance.
