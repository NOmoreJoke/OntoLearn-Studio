"""T02 domain acceptance: exact changes and failures against immutable inputs."""

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
from rdflib import RDF, RDFS, XSD, Graph, Literal

NS = "urn:t02:"
E, A, P, N, DEVICE, J = (
    NS + name for name in ("Equipment", "Alarm", "hasAlarm", "name", "001", "A01")
)


def base():
    return Snapshot(
        "project-a",
        7,
        (
            Entity(E, "class", "Equipment", labels=(("设备", "zh"), ("Equipment", "en"))),
            Entity(A, "class", "Alarm"),
            Entity(P, "objectProperty", "hasAlarm", domain=(E,), range=(A,)),
            Entity(N, "dataProperty", "name", domain=(E,), range=(str(XSD.string),)),
            Entity(DEVICE, "individual", "001", types=(E,)),
            Entity(J, "individual", "A01", types=(A,)),
        ),
    )


def failed(reason, function):
    with pytest.raises(OntologyError) as error:
        function()
    assert error.value.reason == reason


def test_structure_is_not_a_fact_or_required_constraint():
    snapshot = base()
    triples = rdf_triples(snapshot)
    assert Triple(P, str(RDFS.domain), f"<{E}>") in triples
    assert Triple(P, str(RDFS.range), f"<{A}>") in triples
    assert not any(t.subject == DEVICE and t.predicate == P for t in triples)
    fact = Fact(DEVICE, P, f"<{J}>")
    preview = change_preview(snapshot, add_facts=(fact,))
    assert preview.added == (fact.triple(),)
    assert preview.removed == ()
    assert preview.changed_entities == ()
    assert snapshot.facts == ()
    assert preview.candidate.facts == (fact,)


def test_complete_rdf_inspection_is_valid_turtle_with_all_terms():
    snapshot = base()
    text = "\n".join(f"<{t.subject}> <{t.predicate}> {t.object} ." for t in rdf_triples(snapshot))
    # Isolated real-library probe of generated basic RDF, not the pending import product path.
    graph = Graph().parse(data=text, format="turtle")
    expected = {(t.subject, t.predicate, t.object) for t in rdf_triples(snapshot)}
    actual = {(str(s), str(p), o.n3()) for s, p, o in graph}
    assert actual == expected
    assert graph.value(next(s for s in graph.subjects() if str(s) == E), RDFS.label) is not None


def test_edit_metadata_and_multiple_language_literals_do_not_vanish():
    snapshot = base()
    original = snapshot.entities[0]
    changed = replace(
        original, definitions=(('A pump\n"设备"', "en"),), synonyms=("机器",), examples=("泵站A",)
    )
    preview = change_preview(snapshot, (Put(changed, False),))
    assert preview.added == (
        Triple(E, str(RDFS.comment), Literal('A pump\n"设备"', lang="en").n3()),
    )
    assert preview.removed == ()
    assert preview.changed_entities == (E,)
    assert next(e for e in preview.candidate.entities if e.iri == E) == changed
    assert original.labels == (("设备", "zh"), ("Equipment", "en"))
    only_metadata = change_preview(snapshot, (Put(replace(original, synonyms=("机器",)), False),))
    assert only_metadata.added == only_metadata.removed == ()
    assert only_metadata.changed_entities == (E,)
    assert only_metadata.entity_changes[0].before == original
    assert only_metadata.entity_changes[0].after == replace(original, synonyms=("机器",))


def test_copy_definition_keeps_metadata_and_types_but_not_incident_facts():
    snapshot = replace(base(), facts=(Fact(DEVICE, P, f"<{J}>"),))
    preview = change_preview(snapshot, (Copy(DEVICE, NS + "002", "002"),))
    assert preview.candidate.facts == snapshot.facts
    assert preview.added == (Triple(NS + "002", str(RDF.type), f"<{E}>"),)
    assert next(e for e in preview.candidate.entities if e.iri == NS + "002").types == (E,)
    failed("already_exists", lambda: change_preview(snapshot, (Copy(DEVICE, DEVICE, "copy"),)))
    # IRI is identity; equal English display identifiers in distinct namespaces
    # must not reject otherwise valid basic RDF.
    copy = change_preview(snapshot, (Copy(DEVICE, NS + "002", "001"),))
    assert len({e.iri for e in copy.candidate.entities}) == len(snapshot.entities) + 1


def test_delete_impact_includes_external_structural_and_asserted_references():
    snapshot = replace(
        base(),
        facts=(Fact(DEVICE, P, f"<{J}>"),),
        external_references=(ExternalReference("constraint:c1", E),),
    )
    assert [(r.source, r.field) for r in deletion_impact(snapshot, E)] == [
        ("constraint:c1", "external"),
        (DEVICE, "types"),
        (P, "domain"),
        (N, "domain"),
    ]
    assert [(r.source, r.field) for r in deletion_impact(snapshot, P)] == [
        (DEVICE, "fact.predicate")
    ]
    failed("class_reference_required", lambda: change_preview(snapshot, (Delete(E),)))
    failed("property_reference_required", lambda: change_preview(snapshot, (Delete(P),)))
    assert snapshot.entities == base().entities


def test_delete_batch_must_remove_all_references_and_lists_full_impact():
    snapshot = replace(base(), facts=(Fact(DEVICE, P, f"<{J}>"),))
    preview = change_preview(snapshot, (Delete(P),), remove_facts=snapshot.facts)
    assert preview.candidate.facts == ()
    assert P not in {e.iri for e in preview.candidate.entities}
    assert set(preview.removed) == {
        Triple(P, str(RDF.type), "<http://www.w3.org/2002/07/owl#ObjectProperty>"),
        Triple(P, str(RDFS.domain), f"<{E}>"),
        Triple(P, str(RDFS.range), f"<{A}>"),
        Triple(DEVICE, P, f"<{J}>"),
    }
    assert [(r.target, r.source, r.field) for r in preview.deletion_references] == [
        (P, DEVICE, "fact.predicate")
    ]
    # A class referenced solely by an external definition cannot disappear.
    extra = Entity(NS + "extra", "class", "Extra")
    outside = replace(
        snapshot,
        entities=(*snapshot.entities, extra),
        external_references=(ExternalReference("rule:r1", extra.iri),),
    )
    failed("dangling_external_reference", lambda: change_preview(outside, (Delete(extra.iri),)))


def test_preview_is_bound_to_project_revision_and_full_input():
    snapshot = base()
    preview = change_preview(snapshot)
    preview.require_current(snapshot)
    preview.require_current(replace(snapshot, entities=tuple(reversed(snapshot.entities))))
    for other in (
        replace(snapshot, project="project-b"),
        replace(snapshot, revision=8),
        replace(snapshot, facts=(Fact(DEVICE, N, '"new name"'),)),
    ):
        failed("stale_preview", lambda other=other: preview.require_current(other))


@pytest.mark.parametrize(
    "fact,reason",
    [
        (Fact(E, P, f"<{J}>"), "individual_reference_required"),
        (Fact(DEVICE, P, '"alarm"'), "individual_reference_required"),
        (Fact(DEVICE, P, f"<{E}>"), "individual_reference_required"),
        (Fact(DEVICE, N, f"<{J}>"), "literal_required"),
        (Fact(DEVICE, NS + "missing", '"x"'), "property_reference_required"),
        (Fact(DEVICE, str(RDF.type), f"<{P}>"), "entity_field_required"),
        (Fact(DEVICE, N, '"x"^^<urn:unknown:type>'), "unsupported_datatype"),
    ],
)
def test_invalid_facts_are_rejected_without_changing_input(fact, reason):
    snapshot = base()
    failed(reason, lambda: change_preview(snapshot, add_facts=(fact,)))
    assert snapshot == base()


def test_domain_range_are_rdfs_axioms_not_closed_world_validation():
    # Alarm as subject is legal RDF even though hasAlarm has Equipment domain.
    snapshot = base()
    preview = change_preview(snapshot, add_facts=(Fact(J, P, f"<{DEVICE}>"),))
    assert preview.added == (Triple(J, P, f"<{DEVICE}>"),)
    assert not any(t.subject == J and t.object == f"<{E}>" for t in preview.added)


def test_cycles_in_rdfs_are_preserved_and_not_misrepresented_as_invalid_rdf():
    snapshot = base()
    classes = (
        replace(snapshot.entities[0], parents=(A,)),
        replace(snapshot.entities[1], parents=(E,)),
        *snapshot.entities[2:],
    )
    preview = change_preview(snapshot, tuple(Put(e, False) for e in classes[:2]))
    assert set(preview.added) == {
        Triple(E, str(RDFS.subClassOf), f"<{A}>"),
        Triple(A, str(RDFS.subClassOf), f"<{E}>"),
    }


def test_command_errors_are_atomic_and_do_not_silently_create_or_coerce():
    snapshot = base()
    failed("already_exists", lambda: change_preview(snapshot, (Put(snapshot.entities[0], True),)))
    missing = Entity(NS + "new", "class", "New")
    failed("not_found", lambda: change_preview(snapshot, (Put(missing, False),)))
    failed("duplicate_command", lambda: change_preview(snapshot, (Delete(DEVICE), Delete(DEVICE))))
    failed(
        "kind_change_requires_new_entity",
        lambda: change_preview(
            snapshot, (Put(replace(snapshot.entities[0], kind="individual"), False),)
        ),
    )
    failed(
        "fact_not_found", lambda: change_preview(snapshot, remove_facts=(Fact(DEVICE, N, '"x"'),))
    )
    failed("invalid_revision", lambda: change_preview(replace(snapshot, revision=True)))
    failed("immutable_tuple_required", lambda: change_preview(replace(snapshot, facts=[])))
    failed(
        "field_not_applicable",
        lambda: change_preview(snapshot, (Put(replace(snapshot.entities[0], domain=(A,)), False),)),
    )
    failed(
        "class_reference_required",
        lambda: change_preview(
            snapshot, (Put(replace(snapshot.entities[0], parents=(NS + "missing",)), False),)
        ),
    )
    assert snapshot == base()


@pytest.mark.parametrize(
    "value", ["[]", "<relative>", '"x" . <urn:x> <urn:p> "injection"', '"unterminated']
)
def test_invalid_or_injected_terms_are_safely_rejected(value):
    failed("invalid_rdf_term", lambda: Triple(DEVICE, N, value))


def test_type_label_and_comment_have_one_editable_representation():
    snapshot = base()
    for predicate, value in (
        (RDF.type, f"<{E}>"),
        (RDFS.label, '"名称"@zh'),
        (RDFS.comment, '"说明"'),
    ):
        failed(
            "entity_field_required",
            lambda predicate=predicate, value=value: change_preview(
                snapshot, add_facts=(Fact(DEVICE, str(predicate), value),)
            ),
        )
    for predicate in (RDFS.label, RDFS.comment):
        failed(
            "unsupported_datatype",
            lambda predicate=predicate: change_preview(
                snapshot, add_facts=(Fact(DEVICE, str(predicate), '"x"^^<urn:unknown:type>'),)
            ),
        )
    individual = next(e for e in snapshot.entities if e.iri == DEVICE)
    removed = change_preview(snapshot, (Put(replace(individual, types=()), False),))
    assert removed.removed == (Triple(DEVICE, str(RDF.type), f"<{E}>"),)


def test_deletion_impact_distinguishes_all_incident_statements():
    snapshot = replace(base(), facts=(Fact(DEVICE, N, '"a"'), Fact(DEVICE, N, '"b"')))
    impact = deletion_impact(snapshot, DEVICE)
    assert {ref.statement for ref in impact if ref.field == "fact.subject"} == {
        (DEVICE, N, '"a"'),
        (DEVICE, N, '"b"'),
    }
