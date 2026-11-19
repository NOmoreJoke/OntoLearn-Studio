"""Learning checks use the project ledger and real W4 domain operations."""

import json

import pytest
from ontolearn_engine.behavior import baseline_adapter
from ontolearn_engine.behavior import service as behavior_service
from ontolearn_engine.project import learning_wave4
from ontolearn_engine.scenario import service as scenario_service
from ontolearn_engine.storage import canonical, digest
from test_l1_learning_ledger import ROOT, check_task
from test_w4_a1_mapping import DRAFT, mapping_roundtrip, prepare, preview, run_changeset
from test_w4_a1_transfer import build_exported_package, stage_inbound, stage_outbound
from test_w4_a2_harness import (
    RDF_TYPE,
    before_run,
    create_scenario,
    denied,
    exchange,
    expression_value,
    ok,
    open_blank,
    prepared_project,
    run_behavior,
    runtime,
    sample_draft,
    scenario_configuration,
    uid,
)
from test_w4_a2_scenario import resume_scenario, run_scenario, sid


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


NS = "urn:ontolearn:learning:"
E5_PATH = ROOT / "tests/fixtures/scenario/t09-e5.json"
BASELINES = ROOT / "tests/fixtures/product-baselines"


def seed_case(actor, store, model, facts, *, project_rules=()):
    project = open_blank(actor)
    ontology = {
        "layer": "ontology",
        "id": "learning",
        "value": {
            "triples": model["ontology"],
            "singleValuedPredicates": model["singleValuedPredicates"],
        },
    }
    rules = [{"layer": "rule", "id": rule["id"], "value": rule} for rule in project_rules]
    internal = store._project(project)
    store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        definitions=[ontology, *rules],
        manual=[
            {"id": digest([item["subject"], item["predicate"], item["object"]]), **item}
            for item in facts
        ],
    )
    return project, store.revision(internal), digest(store._snapshot_projection(internal))


def _behavior_case(model, case_id):
    cases = json.loads((BASELINES / "cases.json").read_text())["cases"]
    case = next(item for item in cases if item["id"] == case_id)
    event = case["steps"][0]["events"][0]
    order = NS + "W:{eventId}"
    draft = sample_draft(
        id="B-risk",
        trigger={"eventType": event["type"]},
        conditions=[
            {
                "op": "has",
                "subject": {"kind": "eventField", "field": "alarmId"},
                "property": NS + field,
                "value": expression_value("string", expected),
            }
            for field, expected in (("level", "High"), ("status", "Open"))
        ]
        + [
            {
                "op": "type",
                "subject": {"kind": "eventField", "field": "equipmentId"},
                "classId": NS + "HighRiskEquipment",
            }
        ],
        actions=[
            {
                "kind": "create",
                "object": {"kind": "eventTemplate", "template": order},
                "classId": NS + "WorkOrder",
                "initial": [
                    {
                        "property": NS + "workOrderStatus",
                        "value": expression_value("string", "待处理"),
                    }
                ],
            },
            {
                "kind": "add",
                "subject": {"kind": "eventTemplate", "template": NS + "{eventId}"},
                "property": NS + "eventOrder",
                "value": {"kind": "eventTemplate", "template": order},
            },
        ],
    )
    _, schema, _ = baseline_adapter.model_state(model)
    lowered = baseline_adapter.compile_event(event, 0, NS, schema)
    edits = []
    for edit in lowered["edits"]:
        if "value" in edit:
            kind = "string" if schema[edit["property"]]["kind"] == "literal" else "iri"
            edit = {**edit, "value": {"kind": kind, "value": edit["value"]}}
        edits.append(edit)
    return draft, {**lowered, "edits": edits, "version": 1}


def _run_sample(actor, project, revision, snapshot, draft, event, scope):
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    return ok(
        run_behavior(
            actor,
            project,
            revision,
            snapshot,
            draft=draft,
            events=[event],
            operation=operation,
            scope_id=scope,
        )
    )


def test_behavior_checks_real_isolated_commit_and_replay(owned):
    actor, store = owned
    model = json.loads((BASELINES / "G-base.json").read_text())
    project, revision, snapshot = seed_case(
        actor, store, model, model["facts"], project_rules=model["rules"]
    )
    internal = store._project(project)
    formal = store.state(internal)
    passing = {}
    for check_id in ("B-01", "B-02"):
        draft, event = _behavior_case(model, check_id)
        scope = uid()
        first = _run_sample(actor, project, revision, snapshot, draft, event, scope)
        assert first["state"] == "completed" and first["committed"] is True
        original = behavior_service.load_run(store, project, first["runId"])["isolated"]
        assert check_task(actor, project, "behavior")["operationComplete"] is False
        expected_actions = 2 if check_id == "B-01" else 0
        assert [action["state"] for action in first["actions"]] == ["applied"] * expected_actions
        assert len(original["orders"]) == expected_actions // 2
        risk = {
            "subject": NS + "equipment/001",
            "predicate": RDF_TYPE,
            "object": f"<{NS}HighRiskEquipment>",
        }
        assert risk in original["behaviorBeforeInference"] and risk in original["facts"]
        assert risk not in original["assertedFacts"]
        repeated = _run_sample(
            actor, project, revision, snapshot, draft, {**event, "sequence": 17}, scope
        )
        assert repeated["state"] == "completed" and repeated["committed"] is True
        assert repeated["diff"] == {"added": [], "removed": []}
        assert [action["state"] for action in repeated["actions"]] == [
            "deduplicated"
        ] * expected_actions
        duplicate = behavior_service.load_run(store, project, repeated["runId"])["isolated"]
        assert duplicate["consumedEvents"] == [event["id"]]
        assert duplicate["orders"] == original["orders"]
        assert duplicate["facts"] == original["facts"]
        again = _run_sample(actor, project, revision, snapshot, draft, event, scope)
        assert again["diff"] == repeated["diff"] and again["actions"] == repeated["actions"]
        passing[check_id] = again["runId"]

    done = check_task(actor, project, "behavior")
    assert done["operationComplete"] and done["checkStatus"] == "passed", done["feedback"]
    assert done["evidenceIds"] == list(passing.values())
    assert store.state(internal) == formal and store.revision(internal) == revision

    draft, event = _behavior_case(model, "B-02")
    scope = uid()
    wrong = {**draft, "enabled": False}
    _run_sample(actor, project, revision, snapshot, wrong, event, scope)
    _run_sample(actor, project, revision, snapshot, wrong, event, scope)
    checked = check_task(actor, project, "behavior")
    assert checked["feedback"]["completed"] == ["B-01"] and not checked["operationComplete"]
    assert "alarm-not-high" not in repr(checked["feedback"])
    conflict = _run_sample(
        actor, project, revision, snapshot, wrong, {**event, "version": 2}, scope
    )
    assert conflict["state"] == "failed" and conflict["committed"] is False
    assert conflict["error"]["code"] == "conflict"
    checked = check_task(actor, project, "behavior")
    assert not checked["operationComplete"] and "HighRiskEquipment" not in repr(checked["feedback"])
    assert store.state(internal) == formal and store.revision(internal) == revision
    draft, event = _behavior_case(model, "B-01")
    always = {**draft, "conditions": [{"op": "always"}]}
    scope = uid()
    full_but_unconditional = _run_sample(actor, project, revision, snapshot, always, event, scope)
    assert len(full_but_unconditional["actions"]) == 2
    _run_sample(actor, project, revision, snapshot, always, event, scope)
    checked = check_task(actor, project, "behavior")
    assert checked["feedback"]["completed"] == [] and not checked["operationComplete"]


def test_behavior_rule_uses_rdfs_closure_after_event_edits(owned):
    actor, store = owned
    model = json.loads((BASELINES / "G-base.json").read_text())
    subject = NS + "equipment/001"
    model["ontology"].extend(
        [
            {
                "subject": NS + "Pump",
                "predicate": RDF_TYPE,
                "object": "<http://www.w3.org/2002/07/owl#Class>",
            },
            {
                "subject": NS + "Pump",
                "predicate": "http://www.w3.org/2000/01/rdf-schema#subClassOf",
                "object": f"<{NS}Equipment>",
            },
        ]
    )
    facts = [
        {**fact, "object": f"<{NS}Pump>"}
        if fact["subject"] == subject and fact["predicate"] == RDF_TYPE
        else fact
        for fact in model["facts"]
        if "alarm/A01" not in fact["subject"] and "alarm/A01" not in fact["object"]
    ]
    project, revision, snapshot = seed_case(
        actor, store, model, facts, project_rules=model["rules"]
    )
    draft, event = _behavior_case(model, "B-01")
    run = _run_sample(actor, project, revision, snapshot, draft, event, uid())
    assert run["state"] == "completed" and run["conditions"][0]["triggered"] is True
    isolated = behavior_service.load_run(store, project, run["runId"])["isolated"]
    for class_id in ("Equipment", "HighRiskEquipment"):
        triple = {"subject": subject, "predicate": RDF_TYPE, "object": f"<{NS}{class_id}>"}
        assert triple in isolated["behaviorBeforeInference"]
        assert triple not in isolated["assertedFacts"]
    assert len(isolated["orders"]) == 1


def e5_project(actor, store, capacity=3):
    model = json.loads(E5_PATH.read_text())
    # Apply an actual initial edit via the public config, leaving the formal
    # project's name assertion empty for this fixture.
    initial_facts = [item for item in model["initialFacts"] if item["predicate"] != NS + "name"]
    project, revision, snapshot = seed_case(actor, store, model, initial_facts)
    configuration = scenario_configuration(
        name=model["id"],
        maxRounds=model["maxRounds"],
        capacity={"mode": "direct", "direct": capacity},
        ruleVersion=model["ruleVersion"],
        behaviorVersion=model["behaviorVersion"],
        parameters={"behaviors": canonical(model["behaviors"]), "rules": canonical(model["rules"])},
        initialEdits=[
            {
                "kind": "add",
                "subject": item["subject"],
                "property": item["predicate"],
                "value": {"kind": "string", "value": json.loads(item["object"])},
            }
            for item in model["initialFacts"]
            if item["predicate"] == NS + "name"
        ],
        events=[
            {
                "id": item["id"],
                "round": item["round"],
                "sequence": item["inputSequence"],
                "payload": {
                    **item["payload"],
                    "type": item["type"],
                    "addFacts": canonical(item["payload"]["addFacts"]),
                },
            }
            for item in model["events"]
        ],
    )
    return project, revision, snapshot, configuration


def _scenario_run(actor, project, revision, snapshot, identity):
    run = ok(run_scenario(actor, project, revision, snapshot, identity)[1])["run"]
    assert run["status"] == "succeeded" and run["lastCommittedRound"] == 4, run
    return run


def test_scenario_checks_full_e5_and_resume_from_real_committed_rounds(owned, monkeypatch):
    actor, store = owned
    project, revision, snapshot, config = e5_project(actor, store)
    internal = store._project(project)
    formal = store.state(internal)
    initial = check_task(actor, project, "scenario")
    assert all(ref.startswith("missing:") for ref in initial["evidenceIds"])

    runs = {}
    for capacity in (3, 4):
        configuration = {**config, "capacity": {"mode": "direct", "direct": capacity}}
        scenario_id = sid(
            ok(create_scenario(actor, project, revision, snapshot, configuration=configuration))
        )
        first, second = [
            _scenario_run(actor, project, revision, snapshot, scenario_id) for _ in range(2)
        ]
        assert first["rounds"] == second["rounds"]
        assert all(len(round_["behaviorTrace"]) == 8 for round_ in first["rounds"])
        runs[capacity] = first

    partial = check_task(actor, project, "scenario")
    assert partial["feedback"]["completed"] == ["G-list-01"], partial["feedback"]
    assert not partial["operationComplete"]
    whole = runs[3]
    scenario_id = whole["identity"]["scenarioId"]
    # Interrupt the production runner after the real round-2 checkpoint. The
    # engine publishes its successful prefix and records the failed tail.
    original_commit = scenario_service._WirePorts.commit
    with monkeypatch.context() as patch:

        def stop_at_three(ports, record, check):
            if record.checkpoint.round == 3:
                raise scenario_service.scenario_runner.ScenarioFailure("TEST_INTERRUPTION")
            return original_commit(ports, record, check)

        patch.setattr(scenario_service._WirePorts, "commit", stop_at_three)
        interrupted = ok(run_scenario(actor, project, revision, snapshot, scenario_id)[1])["run"]
        failed_resume = ok(
            resume_scenario(
                actor,
                project,
                revision,
                snapshot,
                scenario_id,
                interrupted["runId"],
                interrupted["checkpointRef"],
            )[1]
        )["run"]
    assert failed_resume["status"] == "failed" and failed_resume["rounds"] == []
    assert failed_resume["lastCommittedRound"] == failed_resume["roundOffset"] == 2
    assert failed_resume["checkpointRef"] == interrupted["checkpointRef"]
    assert failed_resume["resumeAvailable"] is False
    assert interrupted["status"] == "failed" and interrupted["lastCommittedRound"] == 2
    assert interrupted["rounds"] == whole["rounds"][:2]
    resumed = ok(
        resume_scenario(
            actor,
            project,
            revision,
            snapshot,
            scenario_id,
            interrupted["runId"],
            interrupted["checkpointRef"],
        )[1]
    )["run"]
    assert resumed["status"] == "succeeded"
    assert resumed["rounds"] == whole["rounds"][2:]
    resumed_row = scenario_service.load_run(store, project, resumed["runId"])
    whole_row = scenario_service.load_run(store, project, whole["runId"])
    assert [canonical(entry["evidence"]) for entry in resumed_row["rounds"]] == [
        canonical(entry["evidence"]) for entry in whole_row["rounds"][2:]
    ]
    assert all(entry["evidence"]["duplicateOrders"] == [] for entry in resumed_row["rounds"])
    done = check_task(actor, project, "scenario")
    assert done["operationComplete"] and done["checkStatus"] == "passed", done["feedback"]
    assert done["evidenceIds"] == [whole["runId"], resumed["runId"]]
    assert store.state(internal) == formal and store.revision(internal) == revision


@pytest.mark.parametrize("source", ["event-edit", "behavior-edit", "delete"])
def test_scenario_rdf_edits_update_existing_queue_without_resource_capacity(owned, source):
    actor, store = owned
    project, revision, snapshot, config = e5_project(actor, store, capacity=0)
    internal = store._project(project)
    formal = store.state(internal)
    order = NS + "W001"
    status = NS + "workOrderStatus"
    complete = {
        "kind": "set",
        "subject": order,
        "property": status,
        "value": {"kind": "string", "value": "已完成"},
    }
    payload = {"type": "order-updated"}
    if source == "delete":
        payload["edits"] = canonical([{"kind": "delete_object", "object": order}])
    elif source == "event-edit":
        payload["edits"] = canonical([complete])
    else:
        payload["target"] = order
        behaviors = json.loads(config["parameters"]["behaviors"])
        behaviors.append(
            sample_draft(
                id="finish-order",
                trigger={"eventType": "order-updated"},
                conditions=[{"op": "always"}],
                actions=[
                    {
                        **complete,
                        "subject": {"kind": "eventField", "field": "target"},
                        "value": expression_value("string", "已完成"),
                    }
                ],
            )
        )
        config["parameters"]["behaviors"] = canonical(behaviors)
    config["maxRounds"] = 2
    config["events"] = [
        config["events"][0],
        {"id": "E002", "round": 2, "sequence": 0, "payload": payload},
    ]
    scenario_id = sid(ok(create_scenario(actor, project, revision, snapshot, configuration=config)))
    run = ok(run_scenario(actor, project, revision, snapshot, scenario_id)[1])["run"]
    assert run["status"] == "succeeded" and run["lastCommittedRound"] == 2, run
    first, second = run["rounds"]
    assert first["backlog"] == ["W001"] and second["backlog"] == []
    assert second["resourceCompleted"] == []
    row = scenario_service.load_run(store, project, run["runId"])
    evidence = row["rounds"][1]["evidence"]
    order_status = [
        fact["object"]
        for fact in evidence["facts"]
        if (fact["subject"], fact["predicate"]) == (order, status)
    ]
    if source == "delete":
        assert evidence["orders"] == [] and order_status == []
        assert second["metrics"]["completed"] == 0
    else:
        assert [item["status"] for item in evidence["orders"]] == ["已完成"]
        assert order_status == ['"已完成"']
        assert second["metrics"]["completed"] == 1
    assert len(second["behaviorTrace"]) == (1 if source == "behavior-edit" else 0)
    assert store.state(internal) == formal and store.revision(internal) == revision


@pytest.mark.parametrize("missing", ["actions", "inferred", "facts"])
def test_scenario_rejects_real_runs_with_incomplete_e5_evidence(owned, missing):
    actor, store = owned
    project, revision, snapshot, config = e5_project(actor, store)
    if missing == "actions":
        config["parameters"] = {}  # Legacy E.3 can match the queue with zero actions.
    elif missing == "inferred":
        behaviors = json.loads(config["parameters"]["behaviors"])
        behaviors[0]["conditions"] = []
        config["parameters"] = {"behaviors": canonical(behaviors), "rules": "[]"}
    else:
        config["initialEdits"] = []
    for capacity in (3, 4):
        configuration = {**config, "capacity": {"mode": "direct", "direct": capacity}}
        scenario_id = sid(
            ok(create_scenario(actor, project, revision, snapshot, configuration=configuration))
        )
        for _ in range(2):
            run = _scenario_run(actor, project, revision, snapshot, scenario_id)
            assert [item["metrics"]["completed"] for item in run["rounds"]] == [
                capacity * number for number in range(1, 5)
            ]
    checked = check_task(actor, project, "scenario")
    assert checked["feedback"]["completed"] == [] and not checked["operationComplete"]
    assert "E001" not in repr(checked["feedback"]) and "HighRiskEquipment" not in repr(
        checked["feedback"]
    )


def test_report_demands_real_export_and_full_package_round_trip(owned):
    actor, store = owned
    project, revision, snapshot = prepared_project(actor, store)
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="behavior"))
    completed = ok(run_behavior(actor, project, revision, snapshot, operation=operation))
    assert completed["state"] == "completed" and completed["committed"] is True
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
