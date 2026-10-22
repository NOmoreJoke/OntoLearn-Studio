"""Real approved Store-2 input/provenance checks, not product bridge/confirm tests."""

from copy import deepcopy
from dataclasses import replace

import pytest
from ontolearn_engine.ontology import OntologyError, Put, Triple, change_preview, rdf_triples
from ontolearn_engine.ontology.source_projection import bind_rdf_projection
from ontolearn_engine.storage import Store, digest
from test_ontology_fixed_inputs import NS, editor_projection, fixed_input


def _record(raw):
    return {"id": digest([raw["subject"], raw["predicate"], raw["object"]]), **raw}


@pytest.fixture
def seeded(tmp_path):
    data = fixed_input()
    editor = editor_projection(data)
    store = Store(tmp_path / "source.db")
    store.create_project(editor.project)
    mapped = next(
        t
        for t in data["facts"]
        if t["subject"] == NS + "equipment/001" and t["predicate"] == NS + "name"
    )
    definitions = [
        {"layer": "ontology", "id": "g-base", "value": {"triples": data["ontology"]}},
        {
            "layer": "constraint",
            "id": "name-required",
            "value": {
                **data["constraints"][0],
                "references": [{"layer": "ontology", "id": "g-base"}],
            },
        },
        {"layer": "rule", "id": "R-risk", "value": data["rules"][0]},
        {"layer": "behavior", "id": "B-risk", "value": data["behaviors"][0]},
    ]
    store.commit(
        editor.project,
        0,
        "seed",
        "seed-job",
        definitions=definitions,
        manual=[_record(t) for t in data["facts"] if t != mapped],
        mapping={"id": "M-equipment", "rows": [{"row": "2", "facts": [_record(mapped)]}]},
    )
    yield store, replace(editor, revision=1), _record(mapped)
    store.close()


def _source(store, editor):
    ref = store.snapshot(editor.project)
    return ref, store.load_snapshot(ref)


def _expect(reason, action):
    with pytest.raises(OntologyError) as error:
        action()
    assert error.value.reason == reason
    assert str(error.value) == reason


def test_complete_real_store_graph_binding_retains_every_record_without_writes(seeded):
    store, editor, mapped = seeded
    ref, source = _source(store, editor)
    state, vector, revision = store.state(editor.project), store.vector(editor.project), 1
    writes = store._db.total_changes
    bound = bind_rdf_projection(ref, source, editor)
    assert {o.triple for o in bound.statement_sources} == set(rdf_triples(editor))
    assert {o.record_id for o in bound.facts} == {r["id"] for r in source["state"]["facts"]}
    item = next(record for record in bound.facts if record.record_id == mapped["id"])
    assert (item.current_object, item.owner, item.source_row, item.managed_value) == (
        '"泵站A"',
        "M-equipment",
        "2",
        '"泵站A"',
    )
    assert [
        (r.source_layer, r.source_id, r.target_layer, r.target_id)
        for r in bound.definition_references
    ] == [("constraint", "name-required", "ontology", "g-base")]
    assert [(d.layer, d.record_id) for d in bound.definitions] == [
        ("behavior", "B-risk"),
        ("constraint", "name-required"),
        ("ontology", "g-base"),
        ("rule", "R-risk"),
    ]
    assert store.state(editor.project) == state
    assert store.vector(editor.project) == vector
    assert store.revision(editor.project) == revision
    assert store._db.total_changes == writes
    # Caller mutation of its loaded dict cannot alter bound records or the Store source.
    source["state"]["facts"].clear()
    assert len(bound.facts) == 18
    assert store.load_snapshot(ref)["state"]["facts"] == state["facts"]


def test_manual_override_keeps_original_id_mapping_row_and_baseline(seeded):
    store, editor, mapped = seeded
    store.commit(
        editor.project, 1, "manual-edit", "manual-edit-job", edits={mapped["id"]: '"人工改名"'}
    )
    editor = replace(
        editor,
        revision=2,
        facts=tuple(
            replace(t, object='"人工改名"')
            if t.subject == mapped["subject"] and t.predicate == mapped["predicate"]
            else t
            for t in editor.facts
        ),
    )
    ref, source = _source(store, editor)
    bound = bind_rdf_projection(ref, source, editor)
    row = next(record for record in bound.facts if record.record_id == mapped["id"])
    assert (row.record_id, row.current_object, row.managed_value, row.owner, row.source_row) == (
        mapped["id"],
        '"人工改名"',
        '"泵站A"',
        "M-equipment",
        "2",
    )
    assert row.record_id != digest([row.subject, row.predicate, row.current_object])
    assert store.marker(editor.project, "manual-edit")["revision"] == 2


def test_managed_tombstone_retains_origin_without_becoming_an_assertion(seeded):
    store, editor, mapped = seeded
    store.commit(editor.project, 1, "delete-name", "delete-name-job", remove=[mapped["id"]])
    editor = replace(
        editor,
        revision=2,
        facts=tuple(
            t
            for t in editor.facts
            if not (t.subject == mapped["subject"] and t.predicate == mapped["predicate"])
        ),
    )
    ref, source = _source(store, editor)
    bound = bind_rdf_projection(ref, source, editor)
    deleted = next(record for record in bound.facts if record.record_id == mapped["id"])
    assert (deleted.current_object, deleted.managed_value, deleted.owner, deleted.source_row) == (
        None,
        '"泵站A"',
        "M-equipment",
        "2",
    )
    assert not any(
        o.kind == "fact" and o.record_id == mapped["id"] for o in bound.statement_sources
    )
    assert {o.triple for o in bound.statement_sources} == set(rdf_triples(editor))


def test_missing_replaced_or_fabricated_triple_cannot_bind_even_with_same_count(seeded):
    store, editor, _ = seeded
    ref, source = _source(store, editor)
    first = editor.facts[0]
    for candidate in (
        replace(editor, facts=editor.facts[1:]),
        replace(editor, facts=(replace(first, object='"wrong"'), *editor.facts[1:])),
        replace(
            editor,
            entities=tuple(
                replace(e, identifier=e.identifier + "x", labels=(("made up", "zh"),))
                if e.iri == NS + "Equipment"
                else e
                for e in editor.entities
            ),
        ),
    ):
        _expect(
            "projection_rdf_mismatch",
            lambda candidate=candidate: bind_rdf_projection(ref, source, candidate),
        )
    assert store.state(editor.project) == source["state"]


def test_binding_does_not_claim_metadata_authority_or_invent_an_iri_mapping(seeded):
    store, editor, _ = seeded
    ref, source = _source(store, editor)
    candidate = replace(
        editor,
        entities=tuple(
            replace(e, synonyms=("unverified metadata",)) if e.iri == NS + "Equipment" else e
            for e in editor.entities
        ),
    )
    # RDF coverage is proven; non-RDF metadata authority is explicitly outside this API.
    bound = bind_rdf_projection(ref, source, candidate)
    assert bound.editor == candidate
    assert bound.source_ref == ref
    assert next(d.payload_digest for d in bound.definitions if d.layer == "ontology") == digest(
        {"triples": fixed_input()["ontology"]}
    )


def test_overlapping_definition_supports_keep_both_exact_source_positions(seeded):
    store, editor, _ = seeded
    original = fixed_input()["ontology"][0]
    store.commit(
        editor.project,
        1,
        "overlap",
        "overlap-job",
        definitions=[
            {"layer": "ontology", "id": "second", "value": {"triples": [original, original]}}
        ],
    )
    editor = replace(editor, revision=2)
    ref, source = _source(store, editor)
    bound = bind_rdf_projection(ref, source, editor)
    matches = [o for o in bound.statement_sources if o.triple == Triple(**original)]
    assert [(o.kind, o.record_id, o.index) for o in matches] == [
        ("ontology-definition", "g-base", 0),
        ("ontology-definition", "second", 0),
        ("ontology-definition", "second", 1),
    ]
    obj = next(e for e in editor.entities if e.iri == original["subject"])
    preview = change_preview(editor, (Put(replace(obj, class_type="rdfs"), False),))
    assert bound.removed_sources(preview) == tuple(matches)
    assert store.revision(editor.project) == 2


def test_input_identity_and_integrity_are_not_interchangeable(seeded):
    store, editor, _ = seeded
    ref, source = _source(store, editor)
    _expect(
        "projection_identity_mismatch",
        lambda: bind_rdf_projection(ref, source, replace(editor, project="other-project")),
    )
    _expect(
        "projection_identity_mismatch",
        lambda: bind_rdf_projection(ref, source, replace(editor, revision=2)),
    )
    changed = deepcopy(source)
    changed["state"]["facts"][0]["object"] = '"tampered"'
    _expect("source_integrity_mismatch", lambda: bind_rdf_projection(ref, changed, editor))
    bound = bind_rdf_projection(ref, source, editor)
    bound.require_source(ref, source)
    store.commit(
        editor.project,
        1,
        "metadata",
        "metadata-job",
        definitions=[{"layer": "model", "id": "display", "value": {"displayName": "new name"}}],
    )
    current_ref, current = _source(store, editor)
    _expect("stale_source_projection", lambda: bound.require_source(current_ref, current))
    _expect(
        "stale_preview", lambda: bound.removed_sources(change_preview(replace(editor, revision=2)))
    )


@pytest.mark.parametrize(
    "change",
    [
        lambda x: x.update(projectRevision=True),
        lambda x: x.update(state={"facts": [], "definitions": []}),
        lambda x: x["state"]["facts"][0].update(source_row="leaked raw path"),
        lambda x: x["state"]["definitions"][0].update(payload="not json"),
        lambda x: x["dependencyVector"].update({"not valid": 1}),
    ],
)
def test_bad_source_records_fail_with_fixed_diagnostics_and_no_store_changes(seeded, change):
    store, editor, _ = seeded
    _, source = _source(store, editor)
    original = deepcopy(source)
    change(source)
    _expect("invalid_source_snapshot", lambda: bind_rdf_projection(digest(source), source, editor))
    assert store.state(editor.project) == original["state"]


def test_entity_field_edit_keeps_original_asserted_type_and_label_record_origins(seeded):
    store, editor, _ = seeded
    from rdflib import RDF, RDFS

    label = {"subject": NS + "equipment/001", "predicate": str(RDFS.label), "object": '"设备一"@zh'}
    store.commit(editor.project, 1, "annotate", "annotate-job", manual=[_record(label)])
    editor = replace(
        editor,
        revision=2,
        entities=tuple(
            replace(e, labels=(("设备一", "zh"),)) if e.iri == label["subject"] else e
            for e in editor.entities
        ),
    )
    ref, source = _source(store, editor)
    bound = bind_rdf_projection(ref, source, editor)
    individual = next(e for e in editor.entities if e.iri == label["subject"])
    preview = change_preview(editor, (Put(replace(individual, labels=(), types=()), False),))
    type_triple = {
        "subject": label["subject"],
        "predicate": str(RDF.type),
        "object": f"<{NS}Equipment>",
    }
    assert set(preview.removed) == {Triple(**type_triple), Triple(**label)}
    assert {(item.kind, item.record_id, item.index) for item in bound.removed_sources(preview)} == {
        ("fact", _record(label)["id"], None),
        ("fact", _record(type_triple)["id"], None),
    }
    assert store.revision(editor.project) == 2
    assert store.marker(editor.project, "annotate")["revision"] == 2


@pytest.mark.parametrize("editor_input", [None, {"project": "private-untrusted-value"}])
def test_projection_rejects_foreign_editor_before_identity_access(seeded, editor_input):
    store, editor, _ = seeded
    ref, source = _source(store, editor)
    state, writes = store.state(editor.project), store._db.total_changes
    _expect("invalid_snapshot", lambda: bind_rdf_projection(ref, source, editor_input))
    assert store.state(editor.project) == state
    assert store._db.total_changes == writes


def test_removed_sources_rejects_untyped_preview_and_unknown_origin_without_writes(seeded):
    store, editor, _ = seeded
    ref, source = _source(store, editor)
    bound = bind_rdf_projection(ref, source, editor)
    writes = store._db.total_changes
    preview = change_preview(editor)
    _expect("invalid_preview", lambda: bound.removed_sources({"removed": []}))
    _expect(
        "invalid_preview",
        lambda: bound.removed_sources(replace(preview, removed=({"object": "x"},))),
    )
    missing = Triple("urn:unknown:subject", "urn:unknown:predicate", '"unknown origin"')
    _expect(
        "projection_origin_missing",
        lambda: bound.removed_sources(replace(preview, removed=(missing,))),
    )
    assert store.state(editor.project) == source["state"]
    assert store._db.total_changes == writes
