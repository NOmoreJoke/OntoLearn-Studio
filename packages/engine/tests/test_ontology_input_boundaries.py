"""Actual malformed adapter inputs must fail safely before hashing or dereferencing."""

from copy import deepcopy
from dataclasses import replace

import pytest
from ontolearn_engine.ontology import (
    Copy,
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
from rdflib import RDF, RDFS
from test_ontology_editor import DEVICE, E, J, N, P, base


def assert_rejected(reason, location, action):
    with pytest.raises(OntologyError) as error:
        action()
    assert error.value.reason == reason
    assert error.value.location == location
    assert str(error.value) == reason  # no input value, parser text, or stack in the diagnostic


@pytest.mark.parametrize(
    "snapshot,commands,add_facts,reason,location",
    [
        (base(), (), ("notafact",), "invalid_fact", "add_facts"),
        (base(), (), ({"subject": "x"},), "invalid_fact", "add_facts"),
        (base(), (Put(None, True),), (), "invalid_command", "commands"),
        (replace(base(), entities=("notanentity",)), (), (), "invalid_entity", "entities"),
        (replace(base(), facts=("notafact",)), (), (), "invalid_fact", "facts"),
        (
            replace(base(), external_references=("notareference",)),
            (),
            (),
            "invalid_external_reference",
            "external_references",
        ),
    ],
)
def test_six_reported_malformed_inputs_have_fixed_errors_without_mutation(
    snapshot, commands, add_facts, reason, location
):
    original = deepcopy((snapshot, commands, add_facts))
    assert_rejected(
        reason, location, lambda: change_preview(snapshot, commands, add_facts=add_facts)
    )
    assert (snapshot, commands, add_facts) == original


@pytest.mark.parametrize(
    "commands,add_facts,remove_facts,reason,location",
    [
        ((Put({"iri": "urn:private:raw"}, True),), (), (), "invalid_command", "commands"),
        ((Put(base().entities[0], 1),), (), (), "invalid_command", "commands"),
        ((Put(replace(base().entities[0], iri=[]), False),), (), (), "invalid_iri", "commands"),
        ((Delete([]),), (), (), "invalid_iri", "commands"),
        ((Copy([], "urn:copy", "copy"),), (), (), "invalid_command", "commands"),
        ((Copy(E, {}, "copy"),), (), (), "invalid_iri", "commands"),
        ((None,), (), (), "unsupported_command", ""),
        ((), (), ({"subject": DEVICE},), "invalid_fact", "remove_facts"),
        ((), (Fact(DEVICE, N, {}),), (), "invalid_rdf_term", ""),
        ((), (), (Fact([], N, '"value"'),), "invalid_rdf_term", ""),
        ([], (), (), "immutable_tuple_required", ""),
        ((), [], (), "immutable_tuple_required", ""),
        ((), (), [], "immutable_tuple_required", ""),
    ],
)
def test_commands_are_checked_before_lookups_hashing_and_sorting(
    commands, add_facts, remove_facts, reason, location
):
    snapshot = base()
    original = deepcopy((snapshot, commands, add_facts, remove_facts))
    assert_rejected(
        reason,
        location,
        lambda: change_preview(snapshot, commands, add_facts=add_facts, remove_facts=remove_facts),
    )
    assert (snapshot, commands, add_facts, remove_facts) == original


@pytest.mark.parametrize("action", [change_preview, rdf_triples, lambda s: deletion_impact(s, E)])
def test_snapshot_entry_points_reject_foreign_objects(action):
    raw = {"project": "private-value", "revision": 1}
    original = deepcopy(raw)
    assert_rejected("invalid_snapshot", "", lambda: action(raw))
    assert raw == original


@pytest.mark.parametrize(
    "candidate,reason,location",
    [
        (replace(base(), project=""), "project_required", ""),
        (
            replace(base(), entities=(base().entities[0], base().entities[0])),
            "duplicate_value",
            "entities",
        ),
        (
            replace(
                base(), entities=(*base().entities, replace(base().entities[0], identifier="other"))
            ),
            "duplicate_iri",
            "",
        ),
        (
            replace(base(), entities=(replace(base().entities[0], kind="unsupported"),)),
            "unsupported_kind",
            "",
        ),
        (
            replace(base(), entities=(replace(base().entities[0], class_type="invalid"),)),
            "invalid_class_type",
            "",
        ),
        (
            replace(base(), entities=(replace(base().entities[0], identifier="has spaces"),)),
            "invalid_identifier",
            "",
        ),
        (
            replace(base(), entities=(replace(base().entities[0], iri="relative"),)),
            "invalid_iri",
            "",
        ),
        (
            replace(base(), entities=(replace(base().entities[0], labels=(("", "zh"),)),)),
            "invalid_text",
            "labels",
        ),
        (
            replace(base(), entities=(replace(base().entities[0], labels=(("Label", "en-GB"),)),)),
            "invalid_language",
            "labels",
        ),
        (
            replace(base(), entities=(replace(base().entities[0], labels=(["x", "zh"],)),)),
            "invalid_value",
            "entities",
        ),
        (
            replace(base(), external_references=(ExternalReference("", E),)),
            "invalid_external_reference",
            "",
        ),
        (
            replace(
                base(),
                facts=(Fact(DEVICE, N, '"abc"^^<http://www.w3.org/2001/XMLSchema#integer>'),),
            ),
            "invalid_literal",
            "object",
        ),
    ],
)
def test_invalid_metadata_and_literal_inputs_keep_safe_specific_diagnostics(
    candidate, reason, location
):
    original = deepcopy(candidate)
    assert_rejected(reason, location, lambda: change_preview(candidate))
    assert candidate == original


def test_fact_command_conflicts_do_not_mutate_or_coerce_values():
    snapshot = base()
    fact = Fact(DEVICE, P, f"<{J}>")
    assert_rejected(
        "duplicate_fact_command", "", lambda: change_preview(snapshot, add_facts=(fact, fact))
    )
    assert_rejected(
        "contradictory_fact_command",
        "",
        lambda: change_preview(snapshot, add_facts=(fact,), remove_facts=(fact,)),
    )
    assert snapshot == base()


def test_batch_delete_retains_all_original_reference_impacts_after_same_batch_release():
    snapshot = base()
    commands = (
        Delete(E),
        Put(replace(next(e for e in snapshot.entities if e.iri == P), domain=()), False),
        Put(replace(next(e for e in snapshot.entities if e.iri == N), domain=()), False),
        Put(replace(next(e for e in snapshot.entities if e.iri == DEVICE), types=()), False),
    )
    preview = change_preview(snapshot, commands)
    assert {
        (ref.target, ref.source, ref.field, ref.statement) for ref in preview.deletion_references
    } == {
        (E, DEVICE, "types", ()),
        (E, P, "domain", ()),
        (E, N, "domain", ()),
    }
    assert all(e.iri != E for e in preview.candidate.entities)
    assert all(E not in e.domain and E not in e.types for e in preview.candidate.entities)
    assert preview.added == ()
    assert set(preview.removed) == {
        Triple(E, str(RDF.type), f"<{RDFS.Class}>"),
        Triple(E, str(RDFS.label), '"设备"@zh'),
        Triple(E, str(RDFS.label), '"Equipment"@en'),
        Triple(P, str(RDFS.domain), f"<{E}>"),
        Triple(N, str(RDFS.domain), f"<{E}>"),
        Triple(DEVICE, str(RDF.type), f"<{E}>"),
    }
    expected = [
        replace(item, domain=())
        if item.iri in {P, N}
        else replace(item, types=())
        if item.iri == DEVICE
        else item
        for item in snapshot.entities
        if item.iri != E
    ]
    assert preview.candidate == replace(
        snapshot, entities=tuple(sorted(expected, key=lambda item: item.iri))
    )
    assert {change.iri for change in preview.entity_changes} == {E, P, N, DEVICE}
    assert snapshot == base()


def test_unspecified_class_declaration_and_copy_remain_rdfs_without_assertion_cloning():
    entity = Entity("urn:default-class", "class", "Default")
    snapshot = Snapshot("p", 0, (entity,))
    assert rdf_triples(snapshot) == (Triple(entity.iri, str(RDF.type), f"<{RDFS.Class}>"),)
    preview = change_preview(snapshot, (Copy(entity.iri, "urn:copy-class", "Copy"),))
    assert preview.added == (Triple("urn:copy-class", str(RDF.type), f"<{RDFS.Class}>"),)
    assert preview.removed == ()
    assert preview.candidate.facts == ()
    assert entity.class_type is None


def test_readding_an_existing_assertion_is_an_exact_idempotent_empty_diff():
    fact = Fact(DEVICE, P, f"<{J}>")
    snapshot = replace(base(), facts=(fact,))
    preview = change_preview(snapshot, add_facts=(fact,))
    assert preview.added == preview.removed == ()
    assert preview.entity_changes == preview.changed_entities == ()
    assert preview.candidate.facts == (fact,)
    assert rdf_triples(preview.candidate) == rdf_triples(snapshot)
    assert snapshot.facts == (fact,)


def test_bad_deletion_target_is_rejected_before_set_membership():
    assert_rejected("invalid_iri", "target", lambda: deletion_impact(base(), {}))


@pytest.mark.parametrize("bad", [chr(0xD800), chr(0xDFFF)])
@pytest.mark.parametrize(
    "field,reason,location",
    [
        ("project", "invalid_text", "project"),
        ("synonyms", "invalid_text", "synonyms"),
        ("examples", "invalid_text", "examples"),
        ("labels", "invalid_text", "labels"),
        ("definitions", "invalid_text", "definitions"),
        ("iri", "invalid_iri", ""),
        ("external_source", "invalid_external_reference", ""),
    ],
)
def test_json_lone_surrogates_in_base_text_have_fixed_errors_without_replacement(
    bad, field, reason, location
):
    import json

    # This is an ordinary JSON-decoded str, not an object with custom Python methods.
    value = json.loads(json.dumps("raw-" + bad))
    entity = Entity("urn:e", "class", "E")
    snapshot = Snapshot("p", 0, (entity,))
    if field == "project":
        snapshot = replace(snapshot, project=value)
    elif field == "external_source":
        snapshot = replace(snapshot, external_references=(ExternalReference(value, entity.iri),))
    else:
        values = ((value, "zh"),) if field in {"labels", "definitions"} else (value,)
        changed = replace(entity, **{field: "urn:" + value if field == "iri" else values})
        snapshot = replace(snapshot, entities=(changed,))
    original = deepcopy(snapshot)
    assert_rejected(reason, location, lambda: change_preview(snapshot))
    assert snapshot == original


@pytest.mark.parametrize("bad", [chr(0xD800), chr(0xDFFF)])
@pytest.mark.parametrize("field", ["synonyms", "examples", "labels", "definitions", "iri"])
def test_put_lone_surrogates_fail_before_diff_and_leave_base_unchanged(bad, field):
    snapshot = Snapshot("p", 0, (Entity("urn:e", "class", "E"),))
    value = "raw-" + bad
    values = ((value, "zh"),) if field in {"labels", "definitions"} else (value,)
    changed = replace(snapshot.entities[0], **{field: "urn:" + value if field == "iri" else values})
    commands = (Put(changed, field == "iri"),)
    reason, location = ("invalid_iri", "") if field == "iri" else ("invalid_text", field)
    original = deepcopy((snapshot, commands))
    assert_rejected(reason, location, lambda: change_preview(snapshot, commands))
    assert (snapshot, commands) == original


@pytest.mark.parametrize("bad", [chr(0xD800), chr(0xDFFF)])
@pytest.mark.parametrize("field", ["subject", "predicate", "object"])
def test_rdf_terms_reject_unencodable_text_with_fixed_diagnostics(bad, field):
    values = {"subject": "urn:s", "predicate": "urn:p", "object": '"value"'}
    values[field] = f'"{bad}"' if field == "object" else "urn:" + bad
    assert_rejected("invalid_rdf_term", "", lambda: Triple(**values))


def test_valid_unicode_is_preserved_verbatim_in_base_and_put_previews():
    from rdflib import Literal

    text = "泵站🚀 e\u0301"  # deliberately decomposed accent; do not silently normalize it
    entity = Entity(
        "urn:设备:🚀",
        "class",
        "Equipment",
        labels=((text, "zh"),),
        definitions=((text, "zh"),),
        synonyms=(text,),
        examples=(text,),
    )
    snapshot = Snapshot("项目🚀", 0, (entity,))
    unchanged = change_preview(snapshot)
    assert unchanged.added == unchanged.removed == ()
    assert unchanged.candidate.entities == (entity,)
    changed = replace(entity, definitions=((text + "更新", "zh"),))
    preview = change_preview(snapshot, (Put(changed, False),))
    assert preview.added == (
        Triple(entity.iri, str(RDFS.comment), Literal(text + "更新", lang="zh").n3()),
    )
    assert preview.removed == (
        Triple(entity.iri, str(RDFS.comment), Literal(text, lang="zh").n3()),
    )
    assert preview.candidate.entities == (changed,)
    assert snapshot.entities == (entity,)
