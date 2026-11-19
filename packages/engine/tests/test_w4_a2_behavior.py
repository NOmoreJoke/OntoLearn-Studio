"""T06 ``project.behavior.*`` over the real w4a2_runtime business3 runtime (W4-A2).

Covers all eleven frozen rules: trigger binding, AND conditions with catalog-
verified ``rdf:type`` (B-01/B-02), deterministic ``exists -> unavailable``,
reserved event payload keys, single/multi cardinality against the real frozen
snapshot schema, fail-closed before-run receipt reconciliation (missing /
wrong domain / moved revision), idempotent replay vs conflicting reuse, event
replay fingerprints, dynamic freshness with fixed stale reasons, durable cancel
terminal persistence, the strict public error projection (zero evidence, paths
or stack traces), and zero mutation of formal asserted facts.
"""

import json
import random

import pytest
from ontolearn_engine.behavior import service as behavior_service
from ontolearn_engine.storage import digest
from test_w4_a2_harness import (
    RDF_TYPE,
    before_run,
    binding,
    denied,
    exchange,
    expression_value,
    ok,
    prepared_project,
    run_behavior,
    runtime,
    sample_draft,
    sample_event,
    uid,
)


@pytest.fixture
def w4a2_runtime(tmp_path):
    with runtime(tmp_path) as pair:
        yield pair


def read_behavior(actor, project, operation, run_id, bind):
    return exchange(
        actor,
        "project.behavior.read",
        {
            "projectId": project,
            "operationId": operation,
            "runId": run_id,
            "scope": "sample",
            "binding": bind,
        },
    )


def cancel_behavior(actor, project, operation, run_id, bind):
    return exchange(
        actor,
        "project.behavior.cancel",
        {
            "projectId": project,
            "operationId": operation,
            "runId": run_id,
            "scope": "sample",
            "binding": bind,
        },
    )


def run_sample(w4a2_runtime, *, draft=None, events=None, scope_id=None, behavior_version="bv-1"):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    bind = binding(
        project, revision, snapshot_id, scope_id=scope_id, behavior_version=behavior_version
    )
    response = run_behavior(
        actor,
        project,
        revision,
        snapshot_id,
        draft=draft,
        events=events,
        operation=operation,
        bind=bind,
        behavior_version=behavior_version,
    )
    return actor, store, project, (revision, snapshot_id), operation, bind, response


def test_candidate_run_projects_diff_actions_and_conditions(w4a2_runtime):
    actor, store = w4a2_runtime
    draft = sample_draft(
        actions=[
            {
                "kind": "create",
                "object": {"kind": "instanceId", "prefix": "urn:test:inst"},
                "classId": "urn:test:WorkOrder",
                "initial": [
                    {
                        "property": "urn:test:status",
                        "value": expression_value("string", "已升级"),
                    }
                ],
            },
            {
                "kind": "set",
                "subject": {"kind": "eventField", "field": "equipmentId"},
                "property": "urn:test:level",
                "value": expression_value("number", 5),
            },
            {
                "kind": "add",
                "subject": {"kind": "value", "value": {"kind": "iri", "value": "urn:test:wo2"}},
                "property": "urn:test:equipment",
                "value": {"kind": "eventField", "field": "equipmentId"},
            },
            {
                "kind": "notify",
                "message": {
                    "kind": "eventTemplate",
                    "template": "事件 {eventId} 触发升级",
                },
            },
        ]
    )
    _, store, project, _, operation, bind, response = run_sample(w4a2_runtime, draft=draft)
    result = ok(response)
    assert result["state"] == "candidate" and result["committed"] is False
    assert result["scope"] == "sample" and result["error"] is None
    assert result["freshness"] == "current" and result["staleReason"] is None
    assert [action["state"] for action in result["actions"]] == ["planned"] * 4
    assert [action["kind"] for action in result["actions"]] == [
        "create",
        "set",
        "add",
        "notify",
    ]
    added = result["diff"]["added"]
    assert {"kind": "object", "objectId": "urn:test:eq1"} in added or all(
        item["kind"] in ("object", "fact", "notification") for item in added
    )
    facts = {
        (item["fact"]["subject"], item["fact"]["property"]): item["fact"]["value"]
        for item in added
        if item["kind"] == "fact"
    }
    assert facts[("urn:test:eq1", "urn:test:level")] == {"kind": "number", "value": 5}
    assert facts[("urn:test:wo2", "urn:test:equipment")] == {
        "kind": "iri",
        "value": "urn:test:eq1",
    }
    created = next(
        item
        for item in added
        if item["kind"] == "object" and item["objectId"].startswith("urn:test:inst")
    )
    assert facts[(created["objectId"], "urn:test:status")] == {
        "kind": "string",
        "value": "已升级",
    }
    assert facts[(created["objectId"], RDF_TYPE)] == {
        "kind": "iri",
        "value": "urn:test:WorkOrder",
    }
    notifications = result["notifications"]
    assert notifications and notifications[0]["state"] == "candidate"
    assert notifications[0]["message"] == "事件 urn:test:event:1 触发升级"
    decision = result["conditions"][0]
    assert decision["triggered"] is True and decision["reason"] == "triggered"
    assert decision["conditions"][0]["reason"] == "frozen_snapshot"
    # Formal asserted facts and revision are untouched by the isolated sample.
    internal = store._project(project)
    assert all(
        fact["predicate"] != "urn:test:level" or fact["subject"] != "urn:test:eq1"
        for fact in store.state(internal)["facts"]
    )


def test_missing_before_run_receipt_fails_closed(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    denied(
        run_behavior(actor, project, revision, snapshot_id),
        "IDENTITY_CONFLICT",
    )


def test_wrong_domain_receipt_rejects(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="scenario"))
    denied(
        run_behavior(actor, project, revision, snapshot_id, operation=operation),
        "IDENTITY_CONFLICT",
    )


def test_moved_revision_rejects_run(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    from test_w4_a2_harness import commit_changeset

    commit_changeset(
        actor,
        store,
        project,
        {
            "manual": [
                {
                    "id": digest(["urn:x:moved", "urn:test:status", '"后续"']),
                    "subject": "urn:x:moved",
                    "predicate": "urn:test:status",
                    "object": '"后续"',
                }
            ]
        },
    )
    assert store.revision(store._project(project)) == revision + 1
    denied(
        run_behavior(actor, project, revision, snapshot_id, operation=operation),
        "REVISION_CONFLICT",
    )


def test_receipt_with_label_rejects_engine_binding(w4a2_runtime):
    """The engine reconciles the frozen host binding label: null exactly."""
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    operation = uid()
    labeled = exchange(
        actor,
        "project.run.before_commit",
        {
            "projectId": project,
            "operationId": operation,
            "domain": "behavior",
            "baseRevision": revision,
            "label": "带标签收据",
        },
    )
    assert labeled["ok"]
    denied(
        run_behavior(actor, project, revision, snapshot_id, operation=operation),
        "IDENTITY_CONFLICT",
    )


@pytest.mark.parametrize("key", ["__proto__", "constructor", "prototype"])
def test_reserved_payload_key_rejects_whole_event(w4a2_runtime, key):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    event = sample_event(payload={"equipmentId": "urn:test:eq1", key: 1})
    denied(
        run_behavior(actor, project, revision, snapshot_id, events=[event], operation=operation),
        "INVALID_REQUEST",
    )


def test_lower_event_defensive_rejection():
    with pytest.raises(behavior_service._PublicBehaviorError) as error:
        behavior_service._lower_event(sample_event(payload={"constructor": 0}))
    assert error.value.code == "invalid_input"


@pytest.mark.parametrize(
    ("kind", "property"),
    [("set", "urn:test:equipment"), ("add", "urn:test:level")],
)
def test_cardinality_mismatch_fails_with_invalid_input(w4a2_runtime, kind, property):
    draft = sample_draft(
        actions=[
            {
                "kind": kind,
                "subject": {"kind": "value", "value": {"kind": "iri", "value": "urn:test:wo1"}},
                "property": property,
                "value": expression_value("string", "值"),
            }
        ]
    )
    *_, response = run_sample(w4a2_runtime, draft=draft)
    result = ok(response)
    assert result["state"] == "failed" and result["committed"] is False
    assert result["error"] == {
        "code": "invalid_input",
        "messageKey": "behavior.invalidInput",
    }
    assert result["diff"] == {"added": [], "removed": []}
    assert result["notifications"] == []


def test_unknown_catalog_class_is_deterministic_unavailable(w4a2_runtime):
    draft = sample_draft(
        conditions=[
            {
                "op": "type",
                "subject": {"kind": "eventField", "field": "equipmentId"},
                "classId": "urn:test:UnknownClass",
            }
        ]
    )
    *_, response = run_sample(w4a2_runtime, draft=draft)
    result = ok(response)
    assert result["state"] == "failed"
    assert result["error"] == {"code": "unavailable", "messageKey": "behavior.unavailable"}


def test_exists_condition_is_deterministic_unavailable(w4a2_runtime):
    draft = sample_draft(
        conditions=[
            {
                "op": "exists",
                "subject": {"kind": "eventField", "field": "equipmentId"},
                "property": "urn:test:status",
            }
        ]
    )
    *_, response = run_sample(w4a2_runtime, draft=draft)
    result = ok(response)
    assert result["error"] == {"code": "unavailable", "messageKey": "behavior.unavailable"}


def test_rdf_type_condition_triggers_only_on_real_assertion(w4a2_runtime):
    """B-01/B-02: the type check matches the exact frozen snapshot assertion."""
    matching = sample_draft()  # equipmentId -> urn:test:eq1 rdf:type Equipment (asserted)
    *_, response = run_sample(w4a2_runtime, draft=matching)
    result = ok(response)
    assert result["conditions"][0]["triggered"] is True
    draft = sample_draft(
        conditions=[
            {
                "op": "type",
                "subject": {"kind": "value", "value": {"kind": "iri", "value": "urn:test:wo1"}},
                "classId": "urn:test:Equipment",  # wo1 is a WorkOrder, not Equipment
            }
        ]
    )
    *_, response = run_sample(w4a2_runtime, draft=draft)
    result = ok(response)
    decision = result["conditions"][0]
    assert decision["triggered"] is False
    assert decision["reason"] == "condition_not_satisfied"
    assert decision["conditions"][0] == {
        "index": 0,
        "satisfied": False,
        "reason": "not_recorded_in_snapshot",
    }


def test_unbound_trigger_event_id_rejects(w4a2_runtime):
    draft = sample_draft(trigger={"eventType": "alarm.raised", "eventId": "urn:test:event:99"})
    *_, response = run_sample(w4a2_runtime, draft=draft)
    result = ok(response)
    assert result["error"]["code"] == "invalid_input"


def test_idempotent_replay_returns_persisted_reply(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    bind = binding(project, revision, snapshot_id)
    args = {
        "projectId": project,
        "operationId": operation,
        "runId": uid(),
        "scope": "sample",
        "binding": bind,
        "draft": sample_draft(),
        "events": [sample_event()],
    }
    first = ok(exchange(actor, "project.behavior.run", args))
    second = ok(exchange(actor, "project.behavior.run", args))
    assert second == first


def test_conflicting_operation_reuse_rejects(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    bind = binding(project, revision, snapshot_id)
    base = {
        "projectId": project,
        "operationId": operation,
        "runId": uid(),
        "scope": "sample",
        "binding": bind,
        "draft": sample_draft(),
    }
    ok(exchange(actor, "project.behavior.run", {**base, "events": [sample_event()]}))
    denied(
        exchange(
            actor,
            "project.behavior.run",
            {**base, "events": [sample_event(id="urn:test:event:2")]},
        ),
        "IDENTITY_CONFLICT",
    )


def test_event_replay_fingerprint_idempotent_and_conflicting(w4a2_runtime):
    same = [sample_event(), sample_event()]
    *_, response = run_sample(w4a2_runtime, events=same)
    result = ok(response)
    assert result["state"] == "candidate"
    conflicting = [sample_event(), sample_event(payload={"equipmentId": "urn:test:wo1"})]
    *_, response = run_sample(w4a2_runtime, events=conflicting)
    result = ok(response)
    assert result["state"] == "failed"
    assert result["error"] == {"code": "conflict", "messageKey": "behavior.conflict"}


def test_freshness_stale_reasons(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    bind = binding(project, revision, snapshot_id)
    run_id = uid()
    args = {
        "projectId": project,
        "operationId": operation,
        "runId": run_id,
        "scope": "sample",
        "binding": bind,
        "draft": sample_draft(),
        "events": [sample_event()],
    }
    ok(exchange(actor, "project.behavior.run", args))
    read = ok(read_behavior(actor, project, operation, run_id, bind))
    assert read["freshness"] == "current" and read["staleReason"] is None
    bumped = dict(bind, behaviorVersion="bv-2")
    read = ok(read_behavior(actor, project, operation, run_id, bumped))
    assert read["freshness"] == "stale"
    assert read["staleReason"] == "behavior-version-changed"
    from test_w4_a2_harness import commit_changeset

    commit_changeset(
        actor,
        store,
        project,
        {
            "manual": [
                {
                    "id": digest(["urn:x:drift", "urn:test:status", '"漂移"']),
                    "subject": "urn:x:drift",
                    "predicate": "urn:test:status",
                    "object": '"漂移"',
                }
            ]
        },
    )
    read = ok(read_behavior(actor, project, operation, run_id, bind))
    assert read["freshness"] == "stale"
    assert read["staleReason"] == "project-revision-changed"


def test_scope_replacement_marks_older_run_stale(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    scope = uid()
    first_operation = uid()
    ok(before_run(actor, project, first_operation, revision, domain="behavior"))
    first_bind = binding(project, revision, snapshot_id, scope_id=scope)
    first = ok(
        run_behavior(
            actor,
            project,
            revision,
            snapshot_id,
            operation=first_operation,
            bind=first_bind,
        )
    )
    second_operation = uid()
    ok(before_run(actor, project, second_operation, revision, domain="behavior"))
    second_bind = binding(project, revision, snapshot_id, scope_id=scope)
    ok(
        run_behavior(
            actor,
            project,
            revision,
            snapshot_id,
            operation=second_operation,
            bind=second_bind,
        )
    )
    read = ok(read_behavior(actor, project, first_operation, first["runId"], first_bind))
    assert read["freshness"] == "stale" and read["staleReason"] == "scope-replaced"


def test_cancel_persists_terminal_state_before_reply(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    bind = binding(project, revision, snapshot_id)
    run_id = uid()
    args = {
        "projectId": project,
        "operationId": operation,
        "runId": run_id,
        "scope": "sample",
        "binding": bind,
        "draft": sample_draft(
            actions=[
                {
                    "kind": "set",
                    "subject": {"kind": "eventField", "field": "equipmentId"},
                    "property": "urn:test:level",
                    "value": expression_value("number", 5),
                },
                {"kind": "notify", "message": {"kind": "eventTemplate", "template": "{eventId}"}},
            ]
        ),
        "events": [sample_event()],
    }
    ok(exchange(actor, "project.behavior.run", args))
    cancelled = ok(cancel_behavior(actor, project, operation, run_id, bind))
    assert cancelled["state"] == "cancelled" and cancelled["committed"] is False
    assert cancelled["error"] is None
    assert cancelled["diff"] == {"added": [], "removed": []}
    assert cancelled["notifications"][0]["state"] == "discarded"
    assert all(action["state"] in ("rolled_back", "skipped") for action in cancelled["actions"])
    persisted = behavior_service.load_run(store, project, run_id)
    assert persisted is not None and persisted["state"] == "cancelled"
    marker = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?",
        (behavior_service.CANCELLED_PREFIX + run_id, project),
    ).fetchone()
    assert marker is not None and json.loads(marker[0])["state"] == "cancelled"
    replay = ok(cancel_behavior(actor, project, operation, run_id, bind))
    assert replay == cancelled
    read = ok(read_behavior(actor, project, operation, run_id, bind))
    assert read["state"] == "cancelled" and read["freshness"] == "historical"


def test_cancel_rejections(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    bind = binding(project, revision, snapshot_id)
    denied(
        cancel_behavior(actor, project, uid(), uid(), bind),
        "NOT_FOUND",
    )
    failed_operation = uid()
    ok(before_run(actor, project, failed_operation, revision, domain="behavior"))
    failed_bind = binding(project, revision, snapshot_id)
    failed = ok(
        run_behavior(
            actor,
            project,
            revision,
            snapshot_id,
            draft=sample_draft(
                actions=[
                    {
                        "kind": "set",
                        "subject": {
                            "kind": "value",
                            "value": {"kind": "iri", "value": "urn:test:wo1"},
                        },
                        "property": "urn:test:equipment",
                        "value": expression_value("string", "基数错误"),
                    }
                ]
            ),
            operation=failed_operation,
            bind=failed_bind,
        )
    )
    assert failed["state"] == "failed"
    denied(
        cancel_behavior(actor, project, failed_operation, failed["runId"], failed_bind),
        "INVALID_STATE",
    )


def test_failed_result_leaks_no_private_evidence(w4a2_runtime):
    draft = sample_draft(
        actions=[
            {
                "kind": "set",
                "subject": {"kind": "value", "value": {"kind": "iri", "value": "urn:test:wo1"}},
                "property": "urn:test:equipment",
                "value": expression_value("string", "x"),
            }
        ]
    )
    *_, response = run_sample(w4a2_runtime, draft=draft)
    result = ok(response)
    text = json.dumps(result, ensure_ascii=False)
    assert "evidence" not in text and ".py" not in text and "Traceback" not in text
    assert result["conditions"] == []


def test_formal_facts_and_revision_never_mutated(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    internal = store._project(project)
    before = store.state(internal)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    ok(run_behavior(actor, project, revision, snapshot_id, operation=operation))
    assert store.state(internal) == before
    assert store.revision(internal) == revision


def test_read_reconciles_binding(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    bind = binding(project, revision, snapshot_id)
    result = ok(run_behavior(actor, project, revision, snapshot_id, operation=operation, bind=bind))
    denied(
        read_behavior(actor, project, operation, result["runId"], dict(bind, requestId=uid())),
        "IDENTITY_CONFLICT",
    )
    denied(read_behavior(actor, project, uid(), result["runId"], bind), "IDENTITY_CONFLICT")


def test_seeded_property_planning_is_deterministic_and_order_stable(w4a2_runtime):
    """Seeded random.Random generations: identical inputs replan identically."""
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    generator = random.Random(20261115)
    drafts = []
    for index in range(6):
        drafts.append(
            sample_draft(
                id=f"urn:test:behavior:{index}",
                priority=generator.randint(-3, 3),
                conditions=[{"op": "always"}]
                if generator.random() < 0.3
                else [
                    {
                        "op": "type",
                        "subject": {"kind": "eventField", "field": "equipmentId"},
                        "classId": "urn:test:Equipment",
                    }
                ],
                actions=[
                    {
                        "kind": "set",
                        "subject": {"kind": "eventField", "field": "equipmentId"},
                        "property": "urn:test:level",
                        "value": expression_value("number", generator.randint(1, 9)),
                    }
                ],
            )
        )
    events = [
        sample_event(
            id=f"urn:test:event:{index}",
            sequence=generator.randint(0, 50),
            payload={"equipmentId": "urn:test:eq1"},
        )
        for index in range(4)
    ]
    for draft in drafts:
        first_operation, replay_operation = uid(), uid()
        ok(before_run(actor, project, first_operation, revision, domain="behavior"))
        first = ok(
            run_behavior(
                actor,
                project,
                revision,
                snapshot_id,
                draft=draft,
                events=list(events),
                operation=first_operation,
            )
        )
        ok(before_run(actor, project, replay_operation, revision, domain="behavior"))
        second = ok(
            run_behavior(
                actor,
                project,
                revision,
                snapshot_id,
                draft=draft,
                events=list(events),
                operation=replay_operation,
            )
        )
        assert second["diff"] == first["diff"]
        assert second["conditions"] == first["conditions"]
        assert first["state"] == "candidate"
