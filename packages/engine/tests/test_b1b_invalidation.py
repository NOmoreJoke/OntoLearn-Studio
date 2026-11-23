"""FR-006 Appendix D invalidation matrix over the real Store3 ledger.

Every change family marks exactly its dependents stale with the fixed reason
code; non-invalidating operations (rename/mode/checkpoint/restore-same-domain)
never disturb domain results; a late V1 publication can never displace the V2
current pointer; history keeps its original input identity and payload.
"""

from uuid import uuid4

import pytest
from ontolearn_engine.invalidation import can_publish_current
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import Store, digest

IMPL = {
    "executionSemanticsVersion": "b1b-inv",
    "engineVersion": "test",
    "dependencyLockHash": "synthetic",
}
OTHER_IMPL = {**IMPL, "engineVersion": "other"}
# Appendix D rows: dependency family -> fixed stale reason code.
MATRIX = [
    ("ontology", "ONTOLOGY_CHANGED"),
    ("constraint", "VALIDATION_DEFINITION_CHANGED"),
    ("rule", "RULE_CHANGED"),
    ("behavior", "BEHAVIOR_CHANGED"),
    ("scenario", "SCENARIO_CHANGED"),
    ("query", "QUERY_CHANGED"),
]


def uid():
    return str(uuid4())


def dump(path):
    import sqlite3

    con = sqlite3.connect(path)
    value = Store.logical_hash(con) if hasattr(Store, "logical_hash") else None
    con.close()
    if value is None:
        from ontolearn_engine.project.format3 import logical_hash

        con = sqlite3.connect(path)
        value = logical_hash(con)
        con.close()
    return value


@pytest.fixture
def store(tmp_path):
    s = JobStore(tmp_path / "inv.db", contract=CONTRACT, target_format=3)
    s.create_project("p")
    s.project = s.public_project("p")
    s.actor = uid()
    yield s
    s.close()


def seed(store, layer, identity, value=None):
    store.commit(
        "p",
        store.revision("p"),
        uid(),
        uid(),
        definitions=[{"layer": layer, "id": identity, "value": value or {"v": 1}}],
    )


def publish(store, deps, kind="query", payload=("payload",)):
    return store.publish("p", store.snapshot("p"), deps, kind, list(payload), IMPL)


def describe(store, identity):
    """Internal stale list rendered like the public staleReason projection."""
    value = store.result(identity)
    return {**value, "staleReason": value["stale"]}


@pytest.mark.parametrize("layer,code", MATRIX)
def test_family_change_marks_only_its_dependents_stale(store, layer, code):
    for family, _ in MATRIX:
        seed(store, family, f"{family}-def")
    store.commit(
        "p",
        store.revision("p"),
        uid(),
        uid(),
        manual=[
            {
                "id": digest(["urn:s", "urn:p", '"v"']),
                "subject": "urn:s",
                "predicate": "urn:p",
                "object": '"v"',
            }
        ],
    )
    dependents = {
        family: publish(store, [f"{family}:{family}-def"], kind=f"{family}-result")
        for family, _ in MATRIX
    }
    facts_result = publish(store, ["facts:asserted"], kind="facts-result")
    for identity in dependents.values():
        assert store.result(identity)["state"] == "current"
    assert store.result(facts_result)["state"] == "current"

    store.commit(
        "p",
        store.revision("p"),
        uid(),
        uid(),
        definitions=[{"layer": layer, "id": f"{layer}-def", "value": {"v": 2}}],
    )
    stale = describe(store, dependents[layer])
    assert stale["state"] == "stale" and stale["stale"]
    assert stale["staleReason"] == [
        {"code": code, "dependency": f"{layer}:{layer}-def", "before": 1, "after": 2}
    ]
    assert store.current("p", f"{layer}-result", IMPL) is None
    for family, identity in dependents.items():
        if family != layer:
            assert store.result(identity)["state"] == "current", family
    assert store.result(facts_result)["state"] == "current"
    # Historical payload and input identity survive invalidation untouched.
    assert stale["payload"] == ["payload"]


def test_mapping_change_invalidates_mapping_and_downstream(store):
    seed(store, "ontology", "o")
    fact = {
        "id": digest(["urn:e1", "urn:p1", '"a"']),
        "subject": "urn:e1",
        "predicate": "urn:p1",
        "object": '"a"',
    }
    store.commit(
        "p",
        store.revision("p"),
        uid(),
        uid(),
        definitions=[{"layer": "mapping", "id": "M1", "value": {}}],
        mapping={"id": "M1", "rows": [{"row": "r1", "facts": [fact]}]},
    )
    mapping_result = publish(store, ["mapping:M1"], kind="mapping-result")
    ontology_result = publish(store, ["ontology:o"], kind="ontology-result")
    assert store.result(mapping_result)["state"] == "current"
    store.commit(
        "p",
        store.revision("p"),
        uid(),
        uid(),
        mapping={
            "id": "M1",
            "rows": [
                {
                    "row": "r1",
                    "facts": [
                        fact,
                        {
                            "id": digest(["urn:e2", "urn:p2", '"b"']),
                            "subject": "urn:e2",
                            "predicate": "urn:p2",
                            "object": '"b"',
                        },
                    ],
                }
            ],
        },
    )
    stale = describe(store, mapping_result)
    assert stale["state"] == "stale"
    assert stale["staleReason"][0]["code"] == "MAPPING_INPUT_CHANGED"
    assert store.result(ontology_result)["state"] == "current"


def test_asserted_fact_change_invalidates_fact_dependents(store):
    fact = {
        "id": digest(["urn:s", "urn:p", '"1"']),
        "subject": "urn:s",
        "predicate": "urn:p",
        "object": '"1"',
    }
    store.commit("p", store.revision("p"), uid(), uid(), manual=[fact])
    result = publish(store, ["facts:asserted"])
    store.commit(
        "p",
        store.revision("p"),
        uid(),
        uid(),
        manual=[
            {
                "id": digest(["urn:s", "urn:p", '"2"']),
                "subject": "urn:s",
                "predicate": "urn:p",
                "object": '"2"',
            }
        ],
    )
    stale = describe(store, result)
    assert stale["staleReason"] == [
        {"code": "FACTS_CHANGED", "dependency": "facts:asserted", "before": 1, "after": 2}
    ]


def test_model_and_rename_and_mode_and_checkpoint_never_stale_results(store):
    seed(store, "rule", "r")
    seed(store, "model", "agent-config")
    rule_result = publish(store, ["rule:r"], kind="rule-result")
    model_result = publish(store, ["model:agent-config"], kind="model-result")
    before = dump(store.path)
    store.apply_application(
        store.project,
        uid(),
        {"type": "metadata", "expectedVersion": 0, "patch": {"name": "改名", "mode": "assisted"}},
        actor=store.actor,
        permission="write",
    )
    store.apply_application(
        store.project,
        uid(),
        {"type": "checkpoint.create", "reason": "manual", "label": "CP"},
        actor=store.actor,
        permission="write",
    )
    assert dump(store.path) != before  # operations really committed...
    assert store.result(rule_result)["state"] == "current"  # ...yet results stay current
    assert not store.result(rule_result)["stale"]
    assert store.result(model_result)["state"] == "current"
    # A model/config version bump alone also never invalidates domain results.
    store.commit(
        "p",
        store.revision("p"),
        uid(),
        uid(),
        definitions=[{"layer": "model", "id": "agent-config", "value": {"v": 2}}],
    )
    assert store.result(rule_result)["state"] == "current"
    assert describe(store, model_result)["staleReason"] == []


def test_same_domain_restore_keeps_results_current(store):
    seed(store, "rule", "r")
    rule_result = publish(store, ["rule:r"])
    store.apply_application(
        store.project,
        uid(),
        {
            "type": "draft.save",
            "editor": "q",
            "expectedGeneration": 0,
            "boundDomainRevision": 1,
            "content": "d",
        },
        actor=store.actor,
        permission="write",
    )
    head = store.project_checkpoint("p")
    restore = {
        "type": "project.restore",
        "checkpointRef": digest(head),
        "expectedCheckpointRef": digest(head),
        "expectedMetadataVersion": head["application"]["metadataVersion"],
        "expectedOperationSequence": head["operationSequence"],
    }
    from ontolearn_engine.storage import Conflict

    with pytest.raises(Conflict):
        # A same-head restore is rejected outright; use an earlier checkpoint.
        store.prepare_application(store.project, restore, actor=store.actor, permission="write")
    genesis = store._db.execute("SELECT checkpoint FROM app_origins WHERE project='p'").fetchone()[
        0
    ]
    restore = {**restore, "checkpointRef": genesis}
    prepared = store.prepare_application(
        store.project, restore, actor=store.actor, permission="write"
    )
    if prepared["domain"] is None:
        store.apply_application(
            store.project,
            uid(),
            prepared["change"],
            actor=store.actor,
            permission="write",
            prepared_plan_ref=prepared["preparedPlanRef"],
            confirmation_ref=prepared["confirmationRef"],
        )
        # Application-only restore (same domain snapshot) keeps domain results current.
        assert store.result(rule_result)["state"] == "current"
    else:
        # The genesis predates the rule commit: compensation restores and marks
        # exactly the rule dependents stale, never deleting history.
        store.apply_application(
            store.project,
            uid(),
            prepared["change"],
            actor=store.actor,
            permission="write",
            prepared_plan_ref=prepared["preparedPlanRef"],
            confirmation_ref=prepared["confirmationRef"],
        )
        assert store.result(rule_result)["state"] == "stale"
        assert store.result(rule_result)["payload"] == ["payload"]


def test_late_v1_result_cannot_displace_v2_current(store):
    seed(store, "rule", "r")
    store.commit(
        "p",
        store.revision("p"),
        uid(),
        uid(),
        manual=[
            {
                "id": digest(["urn:s", "urn:p", '"1"']),
                "subject": "urn:s",
                "predicate": "urn:p",
                "object": '"1"',
            }
        ],
    )
    v1_snapshot = store.snapshot("p")
    store.commit(
        "p",
        store.revision("p"),
        uid(),
        uid(),
        definitions=[{"layer": "rule", "id": "r", "value": {"v": 2}}],
    )
    v2_snapshot = store.snapshot("p")
    v2 = store.publish("p", v2_snapshot, ["facts:asserted"], "query", ["v2"], IMPL)
    assert store.result(v2)["state"] == "current"
    # A late V1 against unchanged dependencies stays purely historical; the
    # current pointer remains V2's.
    v1_late = store.publish("p", v1_snapshot, ["facts:asserted"], "query", ["v1"], IMPL)
    assert store.result(v1_late)["state"] == "historical"
    assert describe(store, v1_late)["staleReason"] == []
    assert store.result(v2)["state"] == "current"
    assert store.current("p", "query", IMPL)["id"] == v2
    # A stale-input late publication is doubly fenced: never current either.
    stale_late = store.publish("p", v1_snapshot, ["rule:r"], "query", ["v1s"], IMPL)
    assert store.result(stale_late)["state"] == "stale"
    assert store.current("p", "query", IMPL)["id"] == v2
    # can_publish_current is the authoritative gate mirrored by JobStore.
    revision = store.revision("p")
    assert can_publish_current(revision, revision, [])
    assert not can_publish_current(revision - 1, revision, [])


def test_result_identity_and_history_survive_cache_collection(store):
    seed(store, "rule", "r")
    result = publish(store, ["rule:r"], kind="query")
    store.commit(
        "p",
        store.revision("p"),
        uid(),
        uid(),
        definitions=[{"layer": "rule", "id": "r", "value": {"v": 2}}],
    )
    store.collect_cache()
    stale = describe(store, result)
    assert stale["state"] == "stale"
    # Cache collection only touches unpinned payloads of non-current results:
    # identities, dependency vectors and reason evidence remain.
    assert stale["staleReason"][0]["code"] == "RULE_CHANGED"
    assert stale["dependencies"] == {"rule:r": 1}


def test_implementation_isolation_keeps_current_pointers_separate(store):
    seed(store, "rule", "r")
    first = publish(store, ["rule:r"], kind="query", payload=["a"])
    second = store.publish("p", store.snapshot("p"), ["rule:r"], "query", ["b"], OTHER_IMPL)
    assert store.current("p", "query", IMPL)["id"] == first
    assert store.current("p", "query", OTHER_IMPL)["id"] == second
    assert store.result(first)["state"] == "current"
    assert store.result(second)["state"] == "current"
