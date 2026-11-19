"""Learning checks use the project ledger and real W4 domain operations."""

import json

import pytest
from ontolearn_engine.project import learning_wave4
from ontolearn_engine.storage import digest
from test_l1_learning_ledger import ROOT, check_task
from test_w4_a1_mapping import DRAFT, mapping_roundtrip, prepare, preview, run_changeset
from test_w4_a1_transfer import build_exported_package, stage_inbound, stage_outbound
from test_w4_a2_harness import (
    before_run,
    create_scenario,
    denied,
    exchange,
    ok,
    open_blank,
    prepared_project,
    run_behavior,
    runtime,
    sample_event,
    scenario_configuration,
    uid,
)
from test_w4_a2_scenario import run_scenario


@pytest.fixture
def owned(tmp_path):
    with runtime(tmp_path) as pair:
        yield pair


def test_mapping_requires_two_distinct_committed_runs(owned):
    actor, store = owned
    project = open_blank(actor)
    source = (ROOT / "tests/fixtures/product-baselines/equipment.csv").read_bytes()
    draft = {
        **DRAFT,
        "identity": "equipment-csv",
        "namespace": "urn:ontolearn:learning:equipment/",
        "classIri": "urn:ontolearn:learning:Equipment",
        "fields": [{**DRAFT["fields"][0], "predicate": "urn:ontolearn:learning:name"}],
    }
    missing = check_task(actor, project, "mapping")
    assert not missing["operationComplete"]
    selection, first, _ = mapping_roundtrip(actor, store, project, source, draft)
    initial = check_task(actor, project, "mapping")
    assert initial["feedback"]["completed"] == ["M-01"]
    assert not initial["operationComplete"]
    second = ok(preview(actor, project, selection, draft))
    assert not check_task(actor, project, "mapping")["operationComplete"]
    assert second["resultId"] != first["resultId"]
    assert second["added"] == second["removed"] == second["modified"] == []
    rerun = ok(prepare(actor, project, second))
    operation = uid()
    before = store.state(store._project(project))["facts"]
    run_changeset(actor, store, project, rerun["plan"], second["baseRevision"], operation)
    assert store.state(store._project(project))["facts"] == before
    done = check_task(actor, project, "mapping")
    assert done["checkStatus"] == "passed", done["feedback"]
    assert done["feedback"]["completed"] == ["M-01", "M-02"]
    assert done["evidenceIds"][1] == operation
    assert done["guidedStageCheckpointRef"] is None
    assert done["independentTransferSuccess"] is False


def test_wrong_mapping_bytes_cannot_impersonate_the_offline_fixture(owned):
    actor, store = owned
    project = open_blank(actor)
    draft = {
        **DRAFT,
        "identity": "equipment-csv",
        "namespace": "urn:ontolearn:learning:equipment/",
        "classIri": "urn:ontolearn:learning:Equipment",
        "fields": [{**DRAFT["fields"][0], "predicate": "urn:ontolearn:learning:name"}],
    }
    payload = (ROOT / "tests/fixtures/product-baselines/equipment.csv").read_bytes()
    selection, _, _ = mapping_roundtrip(actor, store, project, b"\xef\xbb\xbf" + payload, draft)
    second = ok(preview(actor, project, selection, draft))
    rerun = ok(prepare(actor, project, second))
    run_changeset(actor, store, project, rerun["plan"], second["baseRevision"])
    result = check_task(actor, project, "mapping")
    assert result["checkStatus"] == "needs-repair"
    assert result["feedback"]["completed"] == []
    assert "泵站A" not in repr(result["feedback"])


def test_legacy_mapping_provenance_is_reported_as_unverifiable(owned):
    actor, store = owned
    project = open_blank(actor)
    internal = store._project(project)
    triple = {
        "subject": "urn:ontolearn:learning:equipment/001",
        "predicate": "urn:ontolearn:learning:name",
        "object": '"泵站A"',
    }
    triple["id"] = digest(list(triple.values()))
    store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        definitions=[{"layer": "mapping", "id": "equipment-csv", "value": {"version": 1}}],
        mapping={"id": "equipment-csv", "rows": [{"row": "legacy source row", "facts": [triple]}]},
    )
    result = check_task(actor, project, "mapping")
    assert not result["operationComplete"]
    assert result["feedback"]["completed"] == []
    assert "legacy source row" not in repr(result["feedback"])


def test_behavior_identifies_persisted_candidate_without_crediting_an_isolated_commit(owned):
    actor, store = owned
    project, revision, snapshot = prepared_project(actor, store)
    internal = store._project(project)
    facts = store.state(internal)["facts"]
    evidence = []
    for event_id in ("E-B01", "E-B02"):
        operation = uid()
        ok(before_run(actor, project, operation, revision, domain="behavior"))
        result = ok(
            run_behavior(
                actor,
                project,
                revision,
                snapshot,
                operation=operation,
                events=[sample_event(id=event_id)],
            )
        )
        assert result["state"] == "candidate"
        evidence.append(result["runId"])
    result = check_task(actor, project, "behavior")
    assert result["evidenceIds"] == evidence
    assert result["checkStatus"] == "tool-not-successful"
    assert not result["operationComplete"]
    assert store.state(internal)["facts"] == facts


def test_scenario_links_independent_runs_but_does_not_treat_metrics_as_full_e5_results(owned):
    actor, store = owned
    project, revision, snapshot = prepared_project(actor, store)
    initial = check_task(actor, project, "scenario")
    assert all(ref.startswith("missing:") for ref in initial["evidenceIds"])
    ids = []
    for capacity in (3, 3, 4, 4):
        config = scenario_configuration(
            maxRounds=4, capacity={"mode": "direct", "direct": capacity}
        )
        created = ok(create_scenario(actor, project, revision, snapshot, configuration=config))
        scenario = created["scenario"]["identity"]["scenarioId"]
        _, response = run_scenario(actor, project, revision, snapshot, scenario)
        run = ok(response)["run"]
        assert run["lastCommittedRound"] == 4
        assert all(round["checkpointRef"] for round in run["rounds"])
        ids.append(run["runId"])
    checked = check_task(actor, project, "scenario")
    assert checked["evidenceIds"][0] in ids[:2]
    assert checked["evidenceIds"][1].startswith("missing:")
    assert checked["checkStatus"] == "tool-not-successful"
    assert not checked["operationComplete"]


def test_report_demands_real_export_and_full_package_round_trip(owned):
    actor, store = owned
    project, revision, snapshot = prepared_project(actor, store)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    candidate = ok(run_behavior(actor, project, revision, snapshot, operation=operation))
    assert candidate["state"] == "candidate"
    assert not check_task(actor, project, "report")["operationComplete"]
    prepared = ok(
        exchange(
            actor,
            "project.transfer.report.prepare",
            {
                "projectId": project,
                "baseRevision": revision,
            },
        )
    )
    assert not check_task(actor, project, "report")["operationComplete"]
    destination = stage_outbound(actor, project, "report-html", ".html", "output.html")
    export_args = {
        "projectId": project,
        "baseRevision": revision,
        "selectionId": destination,
        "reportRef": prepared["reportRef"],
        "operationId": uid(),
    }
    exported = ok(exchange(actor, "project.transfer.report.export", export_args))
    assert exported["credentialScan"]["status"] == "clear"
    assert exported["publication"]["state"] == "published"
    assert not check_task(actor, project, "report")["operationComplete"]
    archive = build_exported_package(actor, project)
    selection = stage_inbound(
        actor, project, archive, "payload.ontolearn.zip", "zip", ".ontolearn.zip"
    )
    common = {"projectId": project, "selectionId": selection, "expectedKind": "full"}
    checked = ok(exchange(actor, "project.transfer.package.import.check", common))
    assert checked["status"] == "compatible"
    assert not check_task(actor, project, "report")["operationComplete"]
    ok(
        exchange(
            actor,
            "project.transfer.package.import",
            {
                **common,
                "checkRef": checked["checkRef"],
                "packageSha256": checked["packageSha256"],
                "operationId": uid(),
            },
        )
    )
    assert not check_task(actor, project, "report")["operationComplete"]
    folder = store.path.parent / ".ontolearn-host-selections" / destination
    native = store.path.parent / "published.html"
    native.write_bytes((folder / "output.html").read_bytes())
    publication = exported["publication"]
    receipt = {
        "version": 1,
        "reportRef": prepared["reportRef"],
        "operationId": export_args["operationId"],
        "sha256": publication["sha256"],
        "byteLength": publication["byteLength"],
    }
    ack = folder / "report-published.json"
    ack.write_text(json.dumps({**receipt, "sha256": "0" * 64}))
    denied(exchange(actor, "project.transfer.report.export", export_args), "IDENTITY_CONFLICT")
    assert not check_task(actor, project, "report")["operationComplete"]
    ack.write_text(json.dumps(receipt))
    assert ok(exchange(actor, "project.transfer.report.export", export_args)) == exported
    ack.unlink()
    result = check_task(actor, project, "report")
    assert result["checkStatus"] == "passed", result["feedback"]
    assert result["evidenceIds"] == [prepared["reportRef"]]
    assert result["guidedStageCheckpointRef"] is None
    assert learning_wave4._verified_package(store, project, revision + 1) is False
