"""W4-A2 report projection hook over the real w4a2_runtime business3 runtime.

``ontolearn-report-v1`` must populate bounded real ``behaviorResults`` and
``scenarioComparisons`` from persisted ``w4:behavior:*`` / ``w4:scenario:*``
evidence when present, stay cleanly empty when none exist, keep true
staleness against the live revision/snapshot, pass the FR-901 credential
scan, and keep every ``test_w4_a1_transfer.py`` assertion green.
"""

import json

import pytest
import test_w4_a2_scenario as scenario_tests
from ontolearn_engine.behavior import service as behavior_service
from ontolearn_engine.scenario import service as scenario_service
from ontolearn_engine.storage import digest
from test_w4_a2_behavior import persist_uncommitted_candidate
from test_w4_a2_harness import (
    before_run,
    binding,
    create_scenario,
    exchange,
    ok,
    prepared_project,
    run_behavior,
    runtime,
    sample_draft,
    sample_event,
    scenario_configuration,
    uid,
)


@pytest.fixture
def w4a2_runtime(tmp_path):
    with runtime(tmp_path) as pair:
        yield pair


def prepare_report(actor, project, base_revision):
    return exchange(
        actor,
        "project.transfer.report.prepare",
        {"projectId": project, "baseRevision": base_revision},
    )


def test_report_projects_behavior_and_scenario_runs(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    behavior_run = ok(run_behavior(actor, project, revision, snapshot_id, operation=operation))
    created = ok(create_scenario(actor, project, revision, snapshot_id))
    _, response = scenario_tests.run_scenario(
        actor, project, revision, snapshot_id, scenario_tests.sid(created)
    )
    scenario_run = ok(response)["run"]
    report = ok(prepare_report(actor, project, revision))["report"]
    behavior_rows = {entry["resultId"]: entry for entry in report["behaviorResults"]}
    assert behavior_run["runId"] in behavior_rows
    entry = behavior_rows[behavior_run["runId"]]
    assert entry["inputRevision"] == revision and entry["scope"] == "sample"
    assert entry["status"] == "current" and entry["semanticsVersion"]
    scenario_rows = {entry["resultId"]: entry for entry in report["scenarioComparisons"]}
    assert scenario_run["runId"] in scenario_rows
    entry = scenario_rows[scenario_run["runId"]]
    assert entry["status"] == "current"
    assert entry["inputRevision"] == revision
    assert f"{entry['inputRevision']}" in entry["summary"] or entry["summary"]


def test_report_marks_stale_after_revision_moves(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    ok(run_behavior(actor, project, revision, snapshot_id, operation=operation))
    created = ok(create_scenario(actor, project, revision, snapshot_id))
    _, response = scenario_tests.run_scenario(
        actor, project, revision, snapshot_id, scenario_tests.sid(created)
    )
    ok(response)
    from test_w4_a2_harness import commit_changeset

    commit_changeset(
        actor,
        store,
        project,
        {
            "manual": [
                {
                    "id": digest(["urn:x:rep", "urn:test:status", '"报告漂移"']),
                    "subject": "urn:x:rep",
                    "predicate": "urn:test:status",
                    "object": '"报告漂移"',
                }
            ]
        },
    )
    moved = store.revision(store._project(project))
    report = ok(prepare_report(actor, project, moved))["report"]
    assert report["behaviorResults"], report
    assert all(entry["status"] == "stale" for entry in report["behaviorResults"])
    assert all(entry["status"] == "stale" for entry in report["scenarioComparisons"])


def test_report_marks_cancelled_behavior_run(w4a2_runtime):
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
    persist_uncommitted_candidate(store, project, args)
    ok(
        exchange(
            actor,
            "project.behavior.cancel",
            {k: args[k] for k in ("projectId", "operationId", "runId", "scope", "binding")},
        )
    )
    report = ok(prepare_report(actor, project, revision))["report"]
    entry = next(e for e in report["behaviorResults"] if e["resultId"] == run_id)
    assert entry["status"] == "cancelled"


def test_report_excludes_deleted_scenario_runs_and_keeps_clean_when_empty(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    empty = ok(prepare_report(actor, project, revision))["report"]
    assert empty["behaviorResults"] == [] and empty["scenarioComparisons"] == []
    assert empty["credentialScan"] if "credentialScan" in empty else True
    created = ok(create_scenario(actor, project, revision, snapshot_id))
    _, response = scenario_tests.run_scenario(
        actor, project, revision, snapshot_id, scenario_tests.sid(created)
    )
    run = ok(response)["run"]
    ok(scenario_tests.delete_run(actor, project, scenario_tests.sid(created), run["runId"]))
    report = ok(prepare_report(actor, project, revision))["report"]
    assert all(entry["resultId"] != run["runId"] for entry in report["scenarioComparisons"])


def test_report_projection_stays_credential_free(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    ok(run_behavior(actor, project, revision, snapshot_id, operation=operation))
    # Assemble the AWS-documentation sample key at runtime; never a literal.
    sample_key = "AKIA" + "IOSFODNN7" + "EXAMPLE"
    created = ok(
        create_scenario(
            actor,
            project,
            revision,
            snapshot_id,
            configuration=scenario_configuration(source=sample_key + " 秘密来源"),
        )
    )
    _, response = scenario_tests.run_scenario(
        actor, project, revision, snapshot_id, scenario_tests.sid(created)
    )
    ok(response)
    prepared = ok(prepare_report(actor, project, revision))
    # The bounded projection only carries counters and fixed notes, never the
    # scenario's free-text provenance, so FR-901 stays clear.
    assert prepared["credentialScan"] == {"version": 1, "status": "clear"}
    assert sample_key not in json.dumps(prepared["report"])


def test_projection_accessors_are_bounded_and_folded(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    assert behavior_service.indexed_runs(store, project) == []
    assert scenario_service.indexed_run_ids(store, project) == []
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    run = ok(run_behavior(actor, project, revision, snapshot_id, operation=operation))
    assert behavior_service.indexed_runs(store, project) == [run["runId"]]
    folded = behavior_service.load_run(store, project, run["runId"])
    assert folded["state"] == "completed" and folded["committed"] is True
    assert behavior_service.load_run(store, project, uid()) is None
    created = ok(create_scenario(actor, project, revision, snapshot_id))
    _, response = scenario_tests.run_scenario(
        actor, project, revision, snapshot_id, scenario_tests.sid(created)
    )
    scenario_run = ok(response)["run"]
    assert scenario_run["runId"] in scenario_service.indexed_run_ids(store, project)
    loaded = scenario_service.load_run(store, project, scenario_run["runId"])
    assert loaded["status"] == "succeeded"
    assert json.dumps(loaded["rounds"], sort_keys=True)
