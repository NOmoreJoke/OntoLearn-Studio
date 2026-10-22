"""Authoring probes only; I05 runtime, job limits, cancellation and G-base stay pending."""

import copy
import json
from pathlib import Path

import pytest
from ontolearn_engine.query_service import (
    compile_visual,
    save_intent,
    serialize_term,
    validate_draft,
)
from ontolearn_engine.query_service.drafts import DraftError
from rdflib import Graph, Literal, URIRef

FIXTURE = json.loads(
    (Path(__file__).resolve().parents[3] / "tests/fixtures/query/authoring-case.json").read_text()
)
BOUNDARIES = json.loads(
    (Path(__file__).resolve().parents[3] / "tests/fixtures/query/draft-boundaries.json").read_text()
)


def literal(value, **kwargs):
    return {"kind": "literal", "value": value, "language": None, "datatype": None, **kwargs}


def draft():
    return {
        "name": "高危未闭环告警",
        "description": "检查 High 与 Open 的交集",
        "sparql": FIXTURE["sparql"],
        "scope": "asserted",
        "capabilityQuestion": "哪些告警待处理？",
        "source": "template",
    }


@pytest.mark.parametrize("entry", BOUNDARIES["cases"], ids=lambda entry: entry["label"])
def test_draft_raw_utf16_boundaries_before_normalization(entry):
    core = entry["unit"] * entry["count"]
    value = {**draft(), entry["field"]: entry["prefix"] + core + entry["suffix"]}
    if entry["valid"]:
        assert validate_draft(value)[entry["field"]] == core
    else:
        with pytest.raises(DraftError):
            validate_draft(value)


@pytest.mark.parametrize("cp", BOUNDARIES["trimEdgeCodePoints"])
@pytest.mark.parametrize("field", ["name", "sparql"])
def test_draft_shared_edge_whitespace(cp, field):
    edge = chr(cp)
    assert validate_draft({**draft(), field: edge + "q" + edge})[field] == "q"
    with pytest.raises(DraftError):
        validate_draft({**draft(), field: edge})


@pytest.mark.parametrize("field", ["name", "sparql"])
@pytest.mark.parametrize("value", ["\ud800", "\udfff"])
def test_draft_lone_surrogates_still_rejected(field, value):
    with pytest.raises(DraftError):
        validate_draft({**draft(), field: value})


def test_complete_rows_and_empty_variant_in_local_standard_engine():
    query = compile_visual(FIXTURE["visual"])
    assert query == FIXTURE["sparql"]
    graph = Graph().parse(data=FIXTURE["turtle"], format="turtle")
    assert [[str(c) for c in row] for row in graph.query(query)] == FIXTURE["expectedRows"]
    graph.set((URIRef("urn:t04:A01"), URIRef("urn:t04:status"), Literal("Closed")))
    assert [[str(c) for c in row] for row in graph.query(query)] == FIXTURE["closedExpectedRows"]


@pytest.mark.parametrize(
    "value",
    [
        '" . } SERVICE <https://invalid.example> { ?s ?p ?o } #',
        'line\nnew\tcolumn\\quote"',
        "泵站🙂",
        "\x00\x1f\x7f",
    ],
)
def test_literal_injection_roundtrip_is_one_term(value):
    text = serialize_term(literal(value))
    graph = Graph().parse(data=f"<urn:s> <urn:p> {text} .", format="turtle")
    assert list(graph) == [(URIRef("urn:s"), URIRef("urn:p"), Literal(value))]


@pytest.mark.parametrize(
    "iri",
    [
        "relative",
        "urn:bad> . SERVICE <https://invalid.example>",
        "urn:bad\\u003E",
        "urn:a b",
        "urn:a\x00",
        "urn:a\x7f",
        "urn:\ud800",
    ],
)
def test_iri_fragments_rejected(iri):
    with pytest.raises(DraftError):
        serialize_term({"kind": "iri", "value": iri})


def test_languages_datatypes_and_exact_shapes():
    assert serialize_term(literal("泵站", language="ZH-cn")) == '"泵站"@zh-cn'
    assert serialize_term(literal("001", datatype="http://www.w3.org/2001/XMLSchema#string")) == (
        '"001"^^<http://www.w3.org/2001/XMLSchema#string>'
    )
    for term in [
        literal("x", language="en", datatype="urn:type"),
        literal("x", language=""),
        literal("x", language="en; DROP"),
        literal("x", extra=True),
        {"kind": "iri", "value": "urn:x", "language": None},
        literal("\ud800"),
    ]:
        with pytest.raises(DraftError):
            serialize_term(term)


def test_exists_missing_and_no_return_fields():
    query = {
        "classIri": "urn:t04:Alarm",
        "fields": [],
        "conditions": [
            {"predicate": "urn:t04:status", "operator": "exists"},
            {"predicate": "urn:t04:unknown", "operator": "not-exists"},
        ],
    }
    rows = Graph().parse(data=FIXTURE["turtle"], format="turtle").query(compile_visual(query))
    assert [str(row[0]) for row in rows] == ["urn:t04:A01", "urn:t04:A02", "urn:t04:A03"]


@pytest.mark.parametrize(
    "change",
    [
        {"fields": [{}]},
        {"conditions": [{"predicate": "urn:p", "operator": "raw"}]},
        {"conditions": [{"predicate": "urn:p", "operator": {}}]},
        {"classIri": "?injected"},
        {"fields": [{"predicate": "urn:p", "label": "x"}] * 17},
        {"conditions": [{"predicate": "urn:p", "operator": "exists"}] * 33},
        {"arbitrarySparql": "SERVICE"},
    ],
)
def test_visual_unknown_and_over_limit_rejected(change):
    with pytest.raises(DraftError):
        compile_visual({**FIXTURE["visual"], **change})


def test_save_preserves_all_fields_no_alias_and_does_not_execute():
    source = draft()
    intent = save_intent(source, definition_id="Q-01", expected_revision=4)
    assert intent["value"] == source
    assert intent["family"] == "query" and intent["expectedProjectRevision"] == 4
    assert len(intent["draftDigest"]) == 64
    source["name"] = "changed"
    assert intent["value"]["name"] == "高危未闭环告警"
    assert intent == save_intent(draft(), definition_id="Q-01", expected_revision=4)
    model = {**draft(), "source": "model", "sparql": "SERVICE is untrusted draft text"}
    assert validate_draft(model) == model  # authoring does not grant execution permission


@pytest.mark.parametrize("revision", [True, -1, 1.5, 9007199254740992, "4"])
def test_save_invalid_revision(revision):
    with pytest.raises(DraftError):
        save_intent(draft(), definition_id="Q-01", expected_revision=revision)


def test_draft_fields_scope_and_identity():
    for patch in [
        {"scope": "scenario"},
        {"name": " "},
        {"source": "trusted"},
        {"sparql": ""},
        {"description": "a" * 4097},
        {"extra": "no"},
    ]:
        with pytest.raises(DraftError):
            validate_draft({**copy.deepcopy(draft()), **patch})
    with pytest.raises(DraftError):
        save_intent(draft(), definition_id="../Q1", expected_revision=0)
