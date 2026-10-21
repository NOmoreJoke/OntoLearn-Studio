"""Approved T09 bytes as independent RDF oracle; no T09 services or Store helpers."""

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest
from ontolearn_engine.ontology import (
    Delete,
    Entity,
    ExternalReference,
    Fact,
    OntologyError,
    Put,
    Snapshot,
    Triple,
    change_preview,
    deletion_impact,
    rdf_triples,
)
from rdflib import OWL, RDF, RDFS

ROOT = Path(__file__).resolve().parents[3]
FIXED = ROOT / "tests/fixtures/ontology/t09-fixed-inputs"
MANIFEST_SHA = "aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e"
NS = "urn:ontolearn:learning:"


def fixed_input():
    manifest_bytes = (FIXED / "manifest.json").read_bytes()
    assert hashlib.sha256(manifest_bytes).hexdigest() == MANIFEST_SHA
    manifest = json.loads(manifest_bytes)
    data_bytes = (FIXED / "G-base.json").read_bytes()
    assert (
        hashlib.sha256(data_bytes).hexdigest()
        == manifest["files"]["tests/fixtures/product-baselines/G-base.json"]
    )
    data = json.loads(data_bytes)
    assert data["fixtureVersion"] == manifest["version"] == "prd-v0.6-learning-1"
    assert (
        hashlib.sha256((ROOT / manifest["source"]["path"]).read_bytes()).hexdigest()
        == manifest["source"]["sha256"]
    )
    return data


def editor_projection(data):
    # Test-specific explicit projection of approved input only. This is not a
    # product parser, generic importer, source-ownership adapter or reset service.
    definitions = []
    kinds = {
        f"<{OWL.Class}>": "class",
        f"<{OWL.ObjectProperty}>": "objectProperty",
        f"<{OWL.DatatypeProperty}>": "dataProperty",
    }
    for triple in data["ontology"]:
        assert triple["predicate"] == str(RDF.type)
        kind = kinds[triple["object"]]
        definitions.append(
            Entity(
                triple["subject"],
                kind,
                triple["subject"].removeprefix(NS),
                class_type="owl" if kind == "class" else None,
            )
        )
    for fact in data["facts"]:
        if fact["predicate"] == str(RDF.type):
            definitions.append(
                Entity(
                    fact["subject"],
                    "individual",
                    fact["subject"].split("/")[-1],
                    types=(fact["object"][1:-1],),
                )
            )
    facts = tuple(Fact(**f) for f in data["facts"] if f["predicate"] != str(RDF.type))
    return Snapshot(
        "t02-fixed-g-base",
        0,
        tuple(definitions),
        facts,
        (
            ExternalReference("constraint:name-required", NS + "Equipment"),
            ExternalReference("rule:R-risk", NS + "Equipment"),
            ExternalReference("rule:R-risk", NS + "HighRiskEquipment"),
            ExternalReference("behavior:B-risk", NS + "HighRiskEquipment"),
            ExternalReference("behavior:B-risk", NS + "WorkOrder"),
        ),
    )


def test_g_base_full_ontology_and_asserted_set_preserved_without_inferred_prefill():
    data = fixed_input()
    snapshot = editor_projection(data)
    expected = tuple(sorted(Triple(**t) for t in [*data["ontology"], *data["facts"]]))
    assert rdf_triples(snapshot) == expected  # all original values; not count-only
    assert change_preview(snapshot).added == change_preview(snapshot).removed == ()
    assert Triple(NS + "equipment/001", str(RDF.type), f"<{NS}HighRiskEquipment>") not in expected


def test_fixed_class_edit_changes_only_its_original_axiom_and_exact_metadata():
    snapshot = editor_projection(fixed_input())
    original = next(e for e in snapshot.entities if e.iri == NS + "Equipment")
    edited = replace(original, labels=(("设备", "zh"),), definitions=(("第一行\n第二行", "zh"),))
    preview = change_preview(snapshot, (Put(edited, False),))
    assert preview.removed == ()
    assert preview.added == (
        Triple(original.iri, str(RDFS.comment), '"""第一行\n第二行"""@zh'),
        Triple(original.iri, str(RDFS.label), '"设备"@zh'),
    )
    assert Triple(original.iri, str(RDF.type), f"<{OWL.Class}>") in rdf_triples(preview.candidate)
    assert preview.candidate.facts == tuple(sorted(snapshot.facts))
    assert preview.entity_changes[0].before == original
    assert preview.entity_changes[0].after == edited


def test_fixed_behavior_reference_blocks_deleting_an_uninstantiated_class():
    snapshot = editor_projection(fixed_input())
    target = NS + "WorkOrder"
    assert [(r.source, r.field) for r in deletion_impact(snapshot, target)] == [
        ("behavior:B-risk", "external")
    ]
    with pytest.raises(OntologyError, match="dangling_external_reference"):
        change_preview(snapshot, (Delete(target),))
    assert rdf_triples(snapshot) == tuple(
        sorted(Triple(**t) for t in [*fixed_input()["ontology"], *fixed_input()["facts"]])
    )
