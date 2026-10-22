"""Pure supplied-material tests, not source/home/provenance or supplier fixtures."""

from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from itertools import product

import pytest
from ontolearn_engine.project.entity_metadata import (
    DEFAULT_BOUNDS,
    ENTITY_KINDS,
    METADATA_FIELDS,
    MetadataBounds,
    MetadataCheck,
    MetadataFault,
    MetadataFields,
    MetadataHome,
    MetadataMaterial,
    MetadataScope,
    MetadataText,
    check_metadata_materials,
)


def home(index=0, kind="class", *, project="project-A", iri=None, owner=None):
    return MetadataHome(project, iri or f"urn:entity:{index}", kind, owner or f"definition-{index}")


def metadata(identifier="BusinessId", **changes):
    return replace(MetadataFields(identifier, (), (), (), ()), **changes)


def material(index=0, kind="class", *, identifier=None, data=None, **home_changes):
    return MetadataMaterial(
        home(index, kind, **home_changes),
        2,
        data if data is not None else metadata(identifier or f"ID-{index}"),
    )


def scope_for(*materials):
    return MetadataScope("project-A", tuple(item.home for item in materials))


def check(*materials, bounds=DEFAULT_BOUNDS):
    return check_metadata_materials(scope_for(*materials), materials, bounds=bounds)


def encoded_size(value):
    """Independent logical input oracle, using real UTF-8 rather than the counter."""
    if type(value) is str:
        return len(value.encode("utf-8"))
    if type(value) is bytes:
        return len(value)
    if type(value) is tuple:
        return sum(encoded_size(item) for item in value)
    if is_dataclass(value):
        return sum(encoded_size(getattr(value, field.name)) for field in fields(value))
    return 0


def fault(reason, callback):
    with pytest.raises(MetadataFault) as captured:
        callback()
    assert captured.value.reason == reason
    assert type(captured.value.location) is tuple
    return captured.value


def test_five_fields_language_text_order_and_identity_are_preserved():
    labels = (
        MetadataText("中文\n原文\0😀", "zh-Hant"),
        MetadataText("English", "EN"),
        MetadataText("中文\n原文\0😀", "zh-Hant"),
    )
    data = metadata(
        "  Real-Identifier  ",
        labels=labels,
        definitions=(MetadataText("定义", datatype="urn:literal:text"),),
        synonyms=(MetadataText("e\u0301"), MetadataText("é")),
        examples=(MetadataText(""), MetadataText("实例\t1")),
    )
    item = material(data=data)
    scope = scope_for(item)
    supplied = (item,)
    result = check_metadata_materials(scope, supplied)
    assert result.scope is scope
    assert result.materials is supplied
    assert result.materials[0].fields is data
    assert result.materials[0].fields.labels is labels
    assert result.gaps == ()
    assert result.supplied_utf8_bytes == encoded_size(scope) + encoded_size(supplied)
    assert tuple(field.name for field in fields(data)) == METADATA_FIELDS
    assert not hasattr(result, "complete_project")
    assert not hasattr(result, "trusted")


def test_scope_and_result_remain_frozen_nested_immutable_values():
    item = material()
    result = check(item)
    for target, name, value in [
        (item, "profile", 1),
        (item.home, "home_id", "other"),
        (item.fields, "identifier", "other"),
        (MetadataText("x"), "text", "y"),
        (result, "gaps", ()),
        (result.scope, "project", "other"),
    ]:
        with pytest.raises(FrozenInstanceError):
            setattr(target, name, value)


@pytest.mark.parametrize("missing", METADATA_FIELDS)
def test_missing_is_not_an_empty_field_or_a_derived_identifier(missing):
    data = replace(metadata("real"), **{missing: None})
    item = material(data=data)
    result = check(item)
    assert result.materials[0].fields is data
    assert result.gaps[0].reason == "missing-fields"
    assert result.gaps[0].fields == (missing,)
    assert getattr(result.materials[0].fields, missing) is None


def test_explicit_empty_collections_are_known_empty():
    item = material(data=metadata("identifier"))
    assert check(item).gaps == ()
    fault("empty-identifier", lambda: check(replace(item, fields=metadata(""))))
    absent = replace(item, fields=None)
    assert check(absent).gaps[0].fields == METADATA_FIELDS
    assert check(absent).gaps[0].reason == "missing-metadata"


@pytest.mark.parametrize(
    "opaque",
    [
        b"",
        b"\xff\x00",
        b'{"entityMetadata":{"identifier":"real","labels":[],"definitions":[],"synonyms":[],"examples":[]}}',
    ],
)
def test_profile1_opaque_is_preserved_without_decoding_or_profile2_recognition(opaque):
    item = MetadataMaterial(home(), 1, None, opaque)
    result = check(item)
    assert result.materials[0].opaque is opaque
    assert result.materials[0].fields is None
    assert result.gaps[0].reason == "legacy-opaque"
    assert result.gaps[0].fields == METADATA_FIELDS
    assert result.supplied_utf8_bytes == encoded_size(result.scope) + encoded_size((item,))


def test_profile_materials_are_not_interchangeable():
    item = material()
    fault("invalid-material", lambda: check(replace(item, profile=1)))
    fault("invalid-material", lambda: check(replace(item, opaque=b"opaque")))
    legacy_absent = MetadataMaterial(home(), 1, None, None)
    assert check(legacy_absent).gaps[0].reason == "legacy-opaque"


@pytest.mark.parametrize("profile", [True, False, 0, 3, 2.0, "2", None])
def test_unknown_or_noninteger_profile_does_not_default(profile):
    fault("unsupported-profile", lambda: check(replace(material(), profile=profile)))


@pytest.mark.parametrize("first_kind,second_kind", tuple(product(ENTITY_KINDS, repeat=2)))
def test_identifier_is_unique_across_all_four_kinds_in_declared_project(first_kind, second_kind):
    one = material(0, first_kind, identifier="ExactId")
    two = material(1, second_kind, identifier="ExactId")
    error = fault("identifier-conflict", lambda: check(one, two))
    assert error.location == ("materials", 1, "fields", "identifier")


@pytest.mark.parametrize(
    "first,second", [("Id", "id"), ("id", " id"), ("id", "id "), ("é", "e\u0301"), ("ß", "ss")]
)
def test_no_case_trim_nfc_or_casefold_merge(first, second):
    one, two = material(0, identifier=first), material(1, identifier=second)
    assert check(one, two).gaps == ()
    assert check(one, two).materials == (one, two)


def test_same_identifier_in_separate_declared_projects_is_not_global_conflict():
    one = material(identifier="same")
    two = material(identifier="same", project="project-B")
    assert check(one).gaps == ()
    assert check_metadata_materials(MetadataScope("project-B", (two.home,)), (two,)).gaps == ()


def test_one_iri_cannot_claim_two_homes_inside_supplied_scope():
    one = material(0)
    two = material(1, iri=one.home.entity_iri)
    fault("multiple-homes", lambda: check(one, two))
    fault("duplicate-home", lambda: check(one, one))


def test_home_can_contain_distinct_entities_and_is_not_assumed_one_entity_per_definition():
    one, two = material(0, owner="shared-definition"), material(1, owner="shared-definition")
    assert check(one, two).gaps == ()


def test_scope_is_explicit_finite_and_does_not_certify_project_coverage():
    one, omitted = material(0), material(1)
    result = check(one)
    assert result.scope.homes == (one.home,)
    fault("scope-mismatch", lambda: check_metadata_materials(scope_for(one, omitted), (one,)))
    fault("scope-mismatch", lambda: check_metadata_materials(scope_for(one), (omitted,)))
    fault("duplicate-home", lambda: check_metadata_materials(scope_for(one, omitted), (one, one)))
    foreign = material(project="foreign")
    fault("scope-mismatch", lambda: check(foreign))
    fault(
        "scope-mismatch",
        lambda: check_metadata_materials(
            scope_for(one), (replace(one, home=replace(one.home, entity_kind="individual")),)
        ),
    )
    empty = MetadataScope("project-A", ())
    assert check_metadata_materials(empty, ()).materials == ()


def test_missing_identifier_does_not_stop_other_known_identifier_conflict_checks():
    missing = material(0, data=metadata(None))
    one, two = material(1, identifier="duplicate"), material(2, identifier="duplicate")
    fault("identifier-conflict", lambda: check(missing, one, two))


@pytest.mark.parametrize("field", METADATA_FIELDS[1:])
def test_mutable_field_containers_are_rejected(field):
    item = material(data=metadata(**{field: [MetadataText("x")]}))
    fault("invalid-material", lambda: check(item))


def test_arbitrary_objects_lists_and_subclasses_are_not_accepted_as_immutable_material():
    item = material()
    scope = scope_for(item)
    fault("invalid-material", lambda: check_metadata_materials(scope, [item]))
    fault(
        "invalid-material",
        lambda: check_metadata_materials(replace(scope, homes=[item.home]), (item,)),
    )
    fault("invalid-material", lambda: check_metadata_materials(scope, ({"fields": item.fields},)))

    class PretendText(str):
        def __iter__(self):
            raise AssertionError("caller code must not run")

    fault("invalid-material", lambda: check(replace(item, fields=metadata(PretendText("x")))))
    fault("invalid-material", lambda: check(replace(item, fields=metadata(labels=("plain",)))))
    fault("invalid-material", lambda: check(MetadataMaterial(item.home, 1, None, bytearray(b"x"))))


@pytest.mark.parametrize("bad", ["\ud800", "x\udfff", "😀\ud800"])
def test_invalid_unicode_is_fixed_failure_without_raw_value(bad):
    item = material(data=metadata(labels=(MetadataText(bad),)))
    error = fault("invalid-unicode", lambda: check(item))
    assert bad not in str(error)


@pytest.mark.parametrize(
    "term",
    [
        MetadataText("x", ""),
        MetadataText("x", datatype=""),
        MetadataText("x", "en", "urn:datatype"),
    ],
)
def test_inconsistent_lexical_cell_shape_is_not_normalized(term):
    fault("invalid-material", lambda: check(material(data=metadata(labels=(term,)))))


def test_this_is_not_an_iri_language_or_datatype_authority():
    # Preserve lexical material; downstream canonical/model owners still validate
    # actual RDF terms. No range or domain declaration is an input to this leaf.
    item = material(data=metadata(labels=(MetadataText("01", datatype="supplied datatype"),)))
    result = check(item)
    assert result.materials[0].fields.labels[0].datatype == "supplied datatype"


def test_invalid_kind_and_missing_explicit_home_are_fixed_failures():
    fault("unsupported-kind", lambda: check(material(kind="unknown")))
    fault("invalid-material", lambda: check(replace(material(), home=None)))
    malformed = object.__new__(MetadataHome)
    fault(
        "invalid-material",
        lambda: check_metadata_materials(MetadataScope("project-A", (malformed,)), ()),
    )


def test_limits_are_local_fixed_guards_and_only_allow_stricter_integer_bounds():
    assert MetadataBounds() == DEFAULT_BOUNDS
    item = material()
    for name in (field.name for field in fields(DEFAULT_BOUNDS)):
        for invalid in [True, -1, 1.5, "1", getattr(DEFAULT_BOUNDS, name) + 1]:
            fault(
                "invalid-bounds",
                lambda n=name, v=invalid: check(item, bounds=replace(DEFAULT_BOUNDS, **{n: v})),
            )
    fault("invalid-material", lambda: check(item, bounds={"max_homes": 1}))


def test_home_count_and_field_count_exact_limits_and_one_over():
    one, two = material(0), material(1)
    assert check(one, bounds=replace(DEFAULT_BOUNDS, max_homes=1)).gaps == ()
    fault("resource-limit", lambda: check(one, two, bounds=replace(DEFAULT_BOUNDS, max_homes=1)))
    values = (MetadataText("x"), MetadataText("y"))
    item = material(data=metadata(labels=values))
    assert check(item, bounds=replace(DEFAULT_BOUNDS, max_values_per_field=2)).gaps == ()
    fault(
        "resource-limit",
        lambda: check(item, bounds=replace(DEFAULT_BOUNDS, max_values_per_field=1)),
    )


def test_scalar_utf8_byte_limit_includes_non_ascii_and_exact_boundary():
    item = material(data=metadata(labels=(MetadataText("😀" * 16),)))
    assert check(item, bounds=replace(DEFAULT_BOUNDS, max_scalar_bytes=64)).gaps == ()
    fault(
        "resource-limit", lambda: check(item, bounds=replace(DEFAULT_BOUNDS, max_scalar_bytes=63))
    )
    long = material(
        data=metadata(labels=(MetadataText("x" * (DEFAULT_BOUNDS.max_scalar_bytes + 1)),))
    )
    fault("resource-limit", lambda: check(long))


def test_total_supplied_bytes_independent_oracle_exact_and_one_less():
    item = material(data=metadata(labels=(MetadataText("中文😀", "zh"),)))
    scope = scope_for(item)
    expected = encoded_size(scope) + encoded_size((item,))
    result = check_metadata_materials(
        scope, (item,), bounds=replace(DEFAULT_BOUNDS, max_total_bytes=expected)
    )
    assert result.supplied_utf8_bytes == expected
    fault(
        "resource-limit",
        lambda: check_metadata_materials(
            scope, (item,), bounds=replace(DEFAULT_BOUNDS, max_total_bytes=expected - 1)
        ),
    )
    legacy = MetadataMaterial(home(), 1, None, b"\xff" * 32)
    exact = encoded_size(scope_for(legacy)) + encoded_size((legacy,))
    assert (
        check(legacy, bounds=replace(DEFAULT_BOUNDS, max_total_bytes=exact)).supplied_utf8_bytes
        == exact
    )
    fault(
        "resource-limit",
        lambda: check(legacy, bounds=replace(DEFAULT_BOUNDS, max_total_bytes=exact - 1)),
    )


def test_supplied_gap_material_and_missing_scope_are_not_editable_or_authorized():
    item = replace(material(), fields=None)
    result = check(item)
    assert type(result) is MetadataCheck
    assert result.materials[0].fields is None
    assert result.gaps
    for absent in ["proof", "cost_session", "authorized", "editable", "complete_project"]:
        assert not hasattr(result, absent)


@pytest.mark.parametrize("identifier", [True, 1, b"identifier", ("identifier",)])
def test_identifier_must_be_a_supplied_exact_string(identifier):
    fault("invalid-material", lambda: check(material(data=metadata(identifier))))


def test_profile2_fields_are_not_coerced_from_dictionary_or_other_schema():
    item = replace(material(), fields={"identifier": "looks-valid"})
    fault("invalid-material", lambda: check(item))


def test_hard_home_and_collection_ceilings_have_actual_exact_and_plus_one_cases():
    supplied = tuple(material(index) for index in range(DEFAULT_BOUNDS.max_homes))
    assert check(*supplied).materials == supplied
    fault("resource-limit", lambda: check(*supplied, material(DEFAULT_BOUNDS.max_homes)))
    values = (MetadataText("same"),) * DEFAULT_BOUNDS.max_values_per_field
    item = material(data=metadata(labels=values))
    assert check(item).materials[0].fields.labels is values
    fault(
        "resource-limit", lambda: check(replace(item, fields=metadata(labels=(*values, values[0]))))
    )


def test_actual_hard_total_utf8_ceiling_with_independent_encoded_size_oracle():
    base = material(data=metadata("actual"))
    overhead = encoded_size(scope_for(base)) + encoded_size((base,))
    full, remainder = divmod(
        DEFAULT_BOUNDS.max_total_bytes - overhead, DEFAULT_BOUNDS.max_scalar_bytes
    )
    labels = (MetadataText("x" * DEFAULT_BOUNDS.max_scalar_bytes),) * full
    if remainder:
        labels = (*labels, MetadataText("中" * (remainder // 3) + "x" * (remainder % 3)))
    item = replace(base, fields=replace(base.fields, labels=labels))
    expected = encoded_size(scope_for(item)) + encoded_size((item,))
    assert expected == DEFAULT_BOUNDS.max_total_bytes
    assert check(item).supplied_utf8_bytes == expected
    over = replace(item, fields=replace(item.fields, examples=(MetadataText("x"),)))
    assert encoded_size(scope_for(over)) + encoded_size((over,)) == expected + 1
    fault("resource-limit", lambda: check(over))
