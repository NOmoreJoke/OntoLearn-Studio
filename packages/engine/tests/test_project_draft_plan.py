"""CAS plans only: these tests do not establish durable Store3 or UI integration."""

from dataclasses import FrozenInstanceError

import pytest
from ontolearn_engine.project.draft_plan import DraftHead, delete_draft, restore_draft, save_draft
from ontolearn_engine.storage import Conflict


def save(head=None, *, expected=0, domain=9, bound=7, content=None):
    return save_draft(
        "p",
        "query",
        head,
        expected_generation=expected,
        domain_revision=domain,
        bound_domain_revision=bound,
        content=content,
    )


def test_save_old_input_is_allowed_but_recorded_exactly_without_domain_mutation():
    content = {"text": "SELECT ?s WHERE { ?s ?p ?o }", "unsaved": ["用户输入"]}
    plan = save(content=content)
    assert plan.before == DraftHead("p", "query", 0, False, 9, None)
    assert plan.after.generation == 1
    assert plan.after.bound_domain_revision == 7
    assert (
        plan.after.content_json == '{"text":"SELECT ?s WHERE { ?s ?p ?o }","unsaved":["用户输入"]}'
    )
    fingerprint = plan.fingerprint
    content["unsaved"].clear()
    plan.diff["after"]["content"]["unsaved"].clear()
    assert plan.fingerprint == fingerprint
    assert "用户输入" in plan.after.content_json
    with pytest.raises(FrozenInstanceError):
        plan.after.generation = 0


def test_delete_recreate_and_restore_always_advance_live_header_generation():
    first = save(content={"text": "第一稿"}).after
    deleted = delete_draft("p", "query", first, expected_generation=1, domain_revision=9).after
    assert deleted == DraftHead("p", "query", 2, False, 7, None)
    recreated = save(deleted, expected=2, content={"text": "重建"}).after
    assert recreated.generation == 3
    restored = restore_draft(
        "p", "query", recreated, first, expected_generation=3, domain_revision=10
    ).after
    assert restored.generation == 4
    assert restored.content_json == first.content_json
    assert restored.content_hash == first.content_hash
    with pytest.raises(Conflict):
        save(restored, expected=first.generation, content={"text": "迟到保存"})


def test_restore_absent_payload_retains_header_and_does_not_reuse_old_cas():
    first = save(content={"text": "草稿"}).after
    absent = DraftHead("p", "query", 0, False, 1, None)
    restored = restore_draft(
        "p", "query", first, absent, expected_generation=1, domain_revision=9
    ).after
    assert restored == DraftHead("p", "query", 2, False, 1, None)
    assert save(restored, expected=2, content={}).after.generation == 3


def test_two_plans_from_same_baseline_require_store_to_cas_in_one_transaction():
    first = save(content={"text": "A"})
    competing = save(content={"text": "B"})
    assert first.fingerprint != competing.fingerprint
    # Once the first head is committed, re-evaluating the competing old CAS fails.
    with pytest.raises(Conflict):
        save(first.after, expected=0, content={"text": "B"})


@pytest.mark.parametrize("invalid", [True, -1, 1.5, None])
def test_invalid_cas_and_source_versions_rejected(invalid):
    with pytest.raises(ValueError):
        save(expected=invalid)
    with pytest.raises(ValueError):
        save(domain=invalid)
    with pytest.raises(ValueError):
        save(bound=invalid)


def test_wrong_project_editor_future_source_and_stale_cas_are_rejected():
    for head in [
        DraftHead("other", "query", 1, False, 1, None),
        DraftHead("p", "ontology", 1, False, 1, None),
    ]:
        with pytest.raises(Conflict):
            save(head, expected=1)
    with pytest.raises(Conflict):
        save(bound=10)
    with pytest.raises(Conflict):
        save(DraftHead("p", "query", 2, False, 10, None), expected=2)
    with pytest.raises(Conflict):
        save(expected=3)


@pytest.mark.parametrize("text", ['{"x":NaN}', '{"x": Infinity}', '{ "x":1}', "not-json"])
def test_noncanonical_or_nonfinite_payload_rejected(text):
    with pytest.raises(ValueError):
        DraftHead("p", "query", 1, True, 1, text)


def test_json_null_draft_and_deleted_draft_are_distinct_and_affect_fingerprint():
    present = save(content=None)
    deleted = delete_draft("p", "query", None, expected_generation=0, domain_revision=9)
    assert present.after.exists and present.after.content_json == "null"
    assert present.after.content_hash is not None
    assert not deleted.after.exists and deleted.after.content_json is None
    assert deleted.after.content_hash is None
    assert present.fingerprint != deleted.fingerprint


@pytest.mark.parametrize("content", ["\ud800", {"nested": ["\udfff"]}, {"\ud800": "value"}])
def test_unencodable_content_is_rejected_before_any_plan_is_returned(content):
    with pytest.raises(ValueError, match="valid UTF-8"):
        save(content=content)


@pytest.mark.parametrize("project,editor", [("\ud800", "query"), ("p", "\udfff")])
def test_unencodable_identity_is_rejected_before_hashing(project, editor):
    with pytest.raises(ValueError, match="valid UTF-8"):
        save_draft(
            project,
            editor,
            None,
            expected_generation=0,
            domain_revision=1,
            bound_domain_revision=1,
            content={},
        )


def test_direct_head_rejects_lone_surrogate_but_preserves_valid_unicode_exactly():
    with pytest.raises(ValueError, match="valid UTF-8"):
        DraftHead("p", "query", 1, True, 1, '"\ud800"')
    plan = save(content={"中文": "泵站A 🌏", "分解字符": "e\u0301"})
    assert plan.after.content_json == '{"中文":"泵站A 🌏","分解字符":"é"}'
    assert len(plan.fingerprint) == 64 and len(plan.after.content_hash) == 64
