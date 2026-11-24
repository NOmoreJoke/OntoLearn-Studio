"""T03 service-level G M-01..06; not IPC/UI or formal product acceptance."""

from dataclasses import replace
from pathlib import Path

import pytest
from ontolearn_engine.mapping.plan import (
    Binding,
    Conversion,
    Mapping,
    PreviewRejected,
    checked_plan,
    convert,
    entity,
    preview,
    suggest,
)
from ontolearn_engine.mapping.source import parse_csv
from ontolearn_engine.storage import Conflict, Store, digest
from rdflib import RDF, XSD, Literal

FIXTURE = Path(__file__).resolve().parents[3] / "tests/fixtures/mapping/equipment.csv"
SPEC = Mapping(
    "equipment-map",
    1,
    "urn:example:equipment/",
    "urn:example:Equipment",
    ("equipment_id",),
    (Binding("equipment_name", "urn:example:name"),),
)


def snapshot(store):
    return store.load_snapshot(store.snapshot("P"))


def apply(store, table, *, operation="mapping-1", spec=SPEC):
    current = snapshot(store)
    prepared = checked_plan(preview(spec, table, current), spec, table, current)
    return store.commit("P", operation=operation, job=operation + "-job", **prepared)


@pytest.fixture
def store(tmp_path):
    instance = Store(tmp_path / "mapping.sqlite")
    instance.create_project("P")
    yield instance
    instance.close()


def test_m01_m02_exact_facts_sources_and_string_identity(store):
    table = parse_csv(FIXTURE.read_bytes())
    p = preview(SPEC, table, snapshot(store))
    expected = {
        ("urn:example:equipment/001", str(RDF.type), "<urn:example:Equipment>"),
        ("urn:example:equipment/001", "urn:example:name", '"泵站A"'),
        ("urn:example:equipment/002", str(RDF.type), "<urn:example:Equipment>"),
        ("urn:example:equipment/002", "urn:example:name", '"泵站B"'),
    }
    assert set(p.added) == expected
    assert p.ready and p.identities_removed == ()
    assert [r["row"] for r in p.rows()] == ['{"sheet":"CSV","row":2}', '{"sheet":"CSV","row":3}']
    apply(store, table)
    before = store.state("P")["facts"]
    assert {(f["subject"], f["predicate"], f["object"]) for f in before} == expected
    assert all(f["owner"] == SPEC.identity and f["managed_value"] == f["object"] for f in before)
    again = preview(SPEC, table, snapshot(store))
    assert again.added == again.removed == again.modified == ()
    assert set(again.unchanged) == expected
    apply(store, table, operation="mapping-2")
    assert store.state("P")["facts"] == before


def test_m03_source_delete_preserves_manual_and_other_mapping(store):
    apply(store, parse_csv(FIXTURE.read_bytes()))
    manual = {
        "subject": "urn:example:equipment/002",
        "predicate": "urn:example:note",
        "object": '"人工保留"',
    }
    manual["id"] = digest([manual[k] for k in ("subject", "predicate", "object")])
    store.commit("P", store.revision("P"), "manual", "job-manual", manual=[manual])
    other = replace(SPEC, identity="other", namespace="urn:other:equipment/")
    apply(store, parse_csv(FIXTURE.read_bytes()), operation="other", spec=other)
    p = preview(
        SPEC, parse_csv("equipment_id,equipment_name\n001,泵站A\n".encode()), snapshot(store)
    )
    assert set(p.removed) == {
        ("urn:example:equipment/002", str(RDF.type), "<urn:example:Equipment>"),
        ("urn:example:equipment/002", "urn:example:name", '"泵站B"'),
    }
    assert p.identities_removed == ("urn:example:equipment/002",)
    apply(
        store, parse_csv("equipment_id,equipment_name\n001,泵站A\n".encode()), operation="deleted"
    )
    remaining = store.state("P")["facts"]
    assert manual["id"] in {f["id"] for f in remaining}
    assert {f["subject"] for f in remaining if f["owner"] == "other"} == {
        "urn:other:equipment/001",
        "urn:other:equipment/002",
    }


@pytest.mark.parametrize("edited", ['"人工值"', None])
def test_m04_manual_edit_or_tombstone_blocks_even_source_deletion(store, edited):
    apply(store, parse_csv(FIXTURE.read_bytes()))
    fact = next(f for f in store.state("P")["facts"] if f["object"] == '"泵站A"')
    kwargs = {"edits": {fact["id"]: edited}} if edited is not None else {"remove": [fact["id"]]}
    store.commit("P", store.revision("P"), "edit", "edit-job", **kwargs)
    before = snapshot(store)
    table = parse_csv("equipment_id,equipment_name\n001,源文件新值\n".encode())
    p = preview(SPEC, table, before)
    assert not p.ready
    conflict = p.conflicts[0]
    assert (
        conflict.code,
        conflict.current,
        conflict.source,
        conflict.managed,
        conflict.owner,
        conflict.source_row,
    ) == (
        "MANUAL_DRIFT",
        edited,
        '"源文件新值"',
        '"泵站A"',
        "equipment-map",
        '{"sheet":"CSV","row":2}',
    )
    with pytest.raises(PreviewRejected, match="MAPPING_BLOCKED"):
        checked_plan(p, SPEC, table, before)
    assert snapshot(store) == before
    deleted = preview(SPEC, parse_csv(b"equipment_id,equipment_name\n"), before)
    assert deleted.conflicts[0].source is None


def test_m05_empty_and_duplicate_keys_locate_every_row_and_no_partial_plan(store):
    table = parse_csv(b"equipment_id,equipment_name\n001,A\n,B\n001,C\n")
    before = snapshot(store)
    p = preview(SPEC, table, before)
    assert {(i.code, i.row, i.column, i.field) for i in p.issues} == {
        ("EMPTY_KEY", 3, 1, "equipment_id"),
        ("DUPLICATE_KEY", 2, 1, "equipment_id"),
        ("DUPLICATE_KEY", 4, 1, "equipment_id"),
    }
    with pytest.raises(PreviewRejected):
        checked_plan(p, SPEC, table, before)
    assert snapshot(store) == before


def test_m06_old_preview_and_actual_store_race_reject(store):
    table = parse_csv(FIXTURE.read_bytes())
    apply(store, table)
    current = snapshot(store)
    old = preview(SPEC, table, current)
    plan = checked_plan(old, SPEC, table, current)
    fact = next(f for f in current["state"]["facts"] if f["object"] == '"泵站A"')
    store.commit("P", store.revision("P"), "edit", "job-edit", edits={fact["id"]: '"修改"'})
    with pytest.raises(PreviewRejected, match="STALE_PREVIEW"):
        checked_plan(old, SPEC, table, snapshot(store))
    with pytest.raises(Conflict, match="Old projectRevision"):
        store.commit("P", operation="late", job="late-job", **plan)
    assert next(f for f in store.state("P")["facts"] if f["id"] == fact["id"])["object"] == '"修改"'


def test_source_or_definition_change_invalidates_preview(store):
    table = parse_csv(FIXTURE.read_bytes())
    old = preview(SPEC, table, snapshot(store))
    with pytest.raises(PreviewRejected, match="STALE_PREVIEW"):
        checked_plan(old, SPEC, parse_csv(b"equipment_id,equipment_name\n001,A\n"), snapshot(store))
    with pytest.raises(PreviewRejected, match="STALE_PREVIEW"):
        checked_plan(old, replace(SPEC, namespace="urn:new/"), table, snapshot(store))


def test_shared_fact_and_reserved_identity_block_ownership(store):
    table = parse_csv(FIXTURE.read_bytes())
    apply(store, table)
    other = replace(SPEC, identity="other-map")
    p = preview(other, table, snapshot(store))
    assert {c.code for c in p.conflicts} == {"OWNERSHIP_CONFLICT"}
    assert {(c.subject, c.predicate, c.source) for c in p.conflicts} == set(
        preview(
            SPEC,
            table,
            {"project": "P", "projectRevision": 0, "state": {"facts": [], "definitions": []}},
        ).added
    )


def test_atomic_store_failure_leaves_no_batch_and_prior_history_unchanged(store):
    table = parse_csv(FIXTURE.read_bytes())
    apply(store, table)
    before = snapshot(store)
    changed = parse_csv("equipment_id,equipment_name\n001,新值\n003,新设备\n".encode())
    prepared = checked_plan(preview(SPEC, changed, before), SPEC, changed, before)

    def failure(stage):
        if stage == "mid_invalidation":
            raise OSError("test-only write failure")

    with pytest.raises(OSError):
        store.commit("P", operation="fail", job="job-fail", hook=failure, **prepared)
    assert snapshot(store) == before
    assert store.marker("P", "fail") is None
    assert store.marker("P", "mapping-1") is not None


def test_identity_composite_encoding_and_cross_table_reference(store):
    assert entity("urn:e/", ("001",)) != entity("urn:e/", ("1",))
    assert entity("urn:e/", ("a/b",)) == "urn:e/a%2Fb"
    assert entity("urn:e/", ("a", "b/c")) != entity("urn:e/", ("a/b", "c"))
    spec = Mapping(
        "alarms",
        1,
        "urn:alarm/",
        "urn:Alarm",
        ("id",),
        (
            Binding(
                "equipment_id",
                "urn:equipment",
                reference_namespace=SPEC.namespace,
                reference_columns=SPEC.keys,
            ),
        ),
    )
    p = preview(spec, parse_csv(b"id,equipment_id\nA01,001\n"), snapshot(store))
    assert ("urn:alarm/A01", "urn:equipment", "<urn:example:equipment/001>") in p.added
    assert suggest(parse_csv(FIXTURE.read_bytes()), {"equipment_name": "urn:name"}) == (
        {
            "column": "equipment_name",
            "predicate": "urn:name",
            "basis": "exact-field-name",
            "samples": ["泵站A", "泵站B"],
        },
    )


@pytest.mark.parametrize(
    ("value", "kind", "expected"),
    [
        ("001", "string", '"001"'),
        ("001", "integer", Literal(1, datatype=XSD.integer).n3()),
        ("false", "boolean", Literal(False).n3()),
        ("2026-10-21", "date", Literal("2026-10-21", datatype=XSD.date).n3()),
        ("1.20", "decimal", Literal("1.20", datatype=XSD.decimal).n3()),
    ],
)
def test_explicit_conversions(value, kind, expected):
    assert convert(value, Conversion(kind)) == expected


@pytest.mark.parametrize(
    ("value", "kind"),
    [
        ("yes", "boolean"),
        ("NaN", "decimal"),
        ("1.0", "integer"),
        ("2026-02-30", "date"),
        ("20261021", "date"),
    ],
)
def test_bad_conversions(value, kind):
    with pytest.raises(ValueError):
        convert(value, Conversion(kind))


def test_conversion_error_reports_source_cell_and_blocks_entire_batch(store):
    spec = replace(
        SPEC, bindings=(Binding("equipment_name", "urn:example:name", Conversion("integer")),)
    )
    p = preview(spec, parse_csv(FIXTURE.read_bytes()), snapshot(store))
    assert [(i.sheet, i.row, i.column, i.field) for i in p.issues] == [
        ("CSV", 2, 2, "equipment_name"),
        ("CSV", 3, 2, "equipment_name"),
    ]
    assert not p.ready


def test_composite_reference_error_names_actual_empty_field(store):
    spec = Mapping(
        "alarms",
        1,
        "urn:alarm/",
        "urn:Alarm",
        ("id",),
        (
            Binding(
                "equip_a",
                "urn:equipment",
                reference_namespace=SPEC.namespace,
                reference_columns=("equip_a", "equip_b"),
            ),
        ),
    )
    p = preview(spec, parse_csv(b"id,equip_a,equip_b\n1,001,\n"), snapshot(store))
    assert [(i.code, i.row, i.column, i.field) for i in p.issues] == [
        ("EMPTY_REFERENCE_KEY", 2, 3, "equip_b")
    ]
