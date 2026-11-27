"""Actual format3 M commit -> accepted immutable query -> real worker -> reopen.

Reuses existing test-only formal commit and wire/owned-child helpers. No Store,
worker, permission, graph, Job or result double. Not Electron or T02 UI evidence.
"""

import json
from copy import deepcopy

import pytest
from ontolearn_engine.resources import CONTRACT, LIMITS, semantic_identity
from ontolearn_engine.semantic_execution import (
    SemanticExecutionFault,
    build_request,
    execute_request,
)
from ontolearn_engine.storage import canonical, digest
from test_ontology_metadata_changeset import ENTITY, TYPE, Harness, definition, uid, value
from test_project_query_worker import (
    decode_success,
    encoded_messages,
    run_worker,
    wire,
)


@pytest.fixture
def owned(tmp_path):
    instance = Harness(tmp_path / "metadata-query.sqlite")
    try:
        yield instance
    finally:
        instance.store.close()


def test_real_format3_metadata_commit_query_worker_and_result_reopen(owned):
    # The fixture is the existing real format3 Harness; all definitions/facts
    # enter through full Diff, confirmation, accepted changeset Job and commit.
    subject = "urn:equipment:equipment/001"
    text = f"SELECT ?s WHERE {{ ?s a <{ENTITY}> }} ORDER BY ?s"
    ontology = value()
    terminal, _, _, _ = owned.apply(
        {
            "definitions": [
                definition(ontology),
                {
                    "layer": "query",
                    "id": "metadata-query",
                    "value": {
                        "text": text,
                        "references": [],
                        "descriptor": {
                            "version": 1,
                            "name": "有元数据的设备",
                            "description": "Metadata is preserved without adding query facts.",
                            "scope": "asserted",
                            "capabilityQuestion": "Which equipment?",
                            "source": "editor",
                        },
                    },
                },
            ],
            "manual": [
                {
                    "id": digest([subject, TYPE, f"<{ENTITY}>"]),
                    "subject": subject,
                    "predicate": TYPE,
                    "object": f"<{ENTITY}>",
                }
            ],
        }
    )
    assert terminal["state"] == "succeeded"
    store = owned.store
    before = store.state(owned.internal)
    snapshot = store.project_get(owned.project)["inputSnapshotId"]
    original_snapshot = store.load_snapshot(snapshot)
    operation = uid()
    job = store.create_job(
        owned.project,
        operation,
        "query.execute",
        {
            "inputSnapshotId": snapshot,
            "scope": "asserted",
            "definitionId": "metadata-query",
            "parametersHash": store.put_blob(owned.project, {"inputSelection": "current"}),
            "derivedResultIds": [],
            "preparedPlanRef": None,
        },
        None,
        semantic_identity(),
        LIMITS,
    )
    accepted = deepcopy(store.job_context(job["jobId"])["queryRequest"])
    assert accepted["snapshot"] == original_snapshot
    messages, frame, maximum = wire(accepted)
    code, stdout, stderr = run_worker(encoded_messages(messages, frame))
    assert code == 0 and stderr == b""
    output = decode_success(stdout, frame, maximum)
    assert output["payload"]["query"] == {
        "type": "SELECT",
        "variables": ["s"],
        "rows": [[f"<{subject}>"]],
    }
    assert output["payload"]["queryText"] == text
    assert output["payload"]["inputSnapshotId"] == snapshot
    assert output["payload"]["inputSelection"] == "current"
    assert store.job_context(job["jobId"])["queryRequest"] == accepted
    store.start_job(job["jobId"])
    finished = store.finish_query_job(job["jobId"], output)
    assert finished["state"] == "succeeded" and finished["error"] is None
    assert finished["commitProgress"] == {"mode": "none"}
    assert finished["operationId"] == operation
    assert store.state(owned.internal) == before
    assert owned.payload() == ontology
    assert store.load_snapshot(snapshot) == original_snapshot
    owned.reopen()
    assert owned.payload() == ontology
    assert owned.store.state(owned.internal) == before
    assert owned.store.get_job(owned.project, job["jobId"]) == finished
    metadata, payload = owned.store.semantic_result(
        owned.project, finished["resultRef"]["resultId"]
    )
    assert payload == output["payload"]
    assert metadata["jobId"] == job["jobId"] and metadata["inputSnapshotId"] == snapshot


SUBJECT = "urn:equipment:equipment/001"
TEXT = f"SELECT ?s WHERE {{ ?s a <{ENTITY}> }} ORDER BY ?s"
EXPECTED_QUERY = {"type": "SELECT", "variables": ["s"], "rows": [[f"<{SUBJECT}>"]]}


def _initial_plan(ontology):
    return {
        "definitions": [
            definition(ontology),
            {
                "layer": "query",
                "id": "metadata-query",
                "value": {
                    "text": TEXT,
                    "references": [],
                    "descriptor": {
                        "version": 1,
                        "name": "有元数据的设备",
                        "description": "Metadata is preserved without adding query facts.",
                        "scope": "asserted",
                        "capabilityQuestion": "Which equipment?",
                        "source": "editor",
                    },
                },
            },
        ],
        "manual": [
            {
                "id": digest([SUBJECT, TYPE, f"<{ENTITY}>"]),
                "subject": SUBJECT,
                "predicate": TYPE,
                "object": f"<{ENTITY}>",
            }
        ],
    }


def _accepted_query(owned):
    store = owned.store
    snapshot = store.project_get(owned.project)["inputSnapshotId"]
    original_snapshot = store.load_snapshot(snapshot)
    job = store.create_job(
        owned.project,
        uid(),
        "query.execute",
        {
            "inputSnapshotId": snapshot,
            "scope": "asserted",
            "definitionId": "metadata-query",
            "parametersHash": store.put_blob(owned.project, {"inputSelection": "current"}),
            "derivedResultIds": [],
            "preparedPlanRef": None,
        },
        None,
        semantic_identity(),
        LIMITS,
    )
    assert job["state"] == "queued" and job["capability"] == "query.execute"
    assert job["inputSnapshotId"] == snapshot
    accepted = deepcopy(store.job_context(job["jobId"])["queryRequest"])
    assert accepted["snapshot"] == original_snapshot
    assert digest(accepted["snapshot"]) == accepted["input"]["inputSnapshotId"] == snapshot
    return job, accepted, original_snapshot


def _execute_real_and_reopen(owned, expected_ontology):
    store = owned.store
    before = store.state(owned.internal)
    job, accepted, original_snapshot = _accepted_query(owned)
    snapshot = job["inputSnapshotId"]
    assert (
        next(
            json.loads(record["payload"])
            for record in accepted["snapshot"]["state"]["definitions"]
            if record["layer"] == "ontology" and record["id"] == "Equipment"
        )
        == expected_ontology
    )
    messages, frame, maximum = wire(accepted)
    code, stdout, stderr = run_worker(encoded_messages(messages, frame))
    assert code == 0 and stderr == b""
    output = decode_success(stdout, frame, maximum)
    payload = output["payload"]
    assert payload["query"] == EXPECTED_QUERY
    assert payload["queryText"] == TEXT
    assert payload["inputSnapshotId"] == snapshot
    assert payload["inputProjectRevision"] == original_snapshot["projectRevision"]
    assert payload["scope"] == "asserted" and payload["definitionId"] == "metadata-query"
    assert payload["inputSelection"] == "current" and payload["selectedResultIds"] == []
    assert (
        payload["executionSemanticsVersion"] == job["implementation"]["executionSemanticsVersion"]
    )
    assert store.job_context(job["jobId"])["queryRequest"] == accepted
    # Deliberately the original test's manual-worker sequence, not Coordinator dispatch.
    store.start_job(job["jobId"])
    finished = store.finish_query_job(job["jobId"], output)
    assert finished["state"] == "succeeded" and finished["error"] is None
    assert finished["commitProgress"] == {"mode": "none"}
    assert finished["operationId"] == job["operationId"]
    assert finished["resultRef"]["inputSnapshotId"] == snapshot
    assert store.state(owned.internal) == before
    assert owned.payload() == expected_ontology
    assert store.load_snapshot(snapshot) == original_snapshot
    owned.reopen()
    assert owned.store.state(owned.internal) == before
    assert owned.payload() == expected_ontology
    assert owned.store.load_snapshot(snapshot) == original_snapshot
    assert owned.store.get_job(owned.project, job["jobId"]) == finished
    assert owned.store.job_context(job["jobId"])["queryRequest"] == accepted
    metadata, saved = owned.store.semantic_result(owned.project, finished["resultRef"]["resultId"])
    assert saved == payload
    assert metadata["projectId"] == owned.project and metadata["jobId"] == job["jobId"]
    assert metadata["inputSnapshotId"] == snapshot
    assert metadata["inputProjectRevision"] == original_snapshot["projectRevision"]
    assert metadata["scope"] == "asserted" and metadata["definitionId"] == "metadata-query"
    assert metadata["parametersHash"] == job["parametersHash"]
    assert metadata["implementation"] == job["implementation"]
    return {"job": finished, "snapshot": snapshot, "payload": deepcopy(payload)}


def test_legacy_without_metadata_uses_real_query_worker_and_reopens(owned):
    legacy = value(include_metadata=False)
    owned.apply(_initial_plan(legacy))
    completed = _execute_real_and_reopen(owned, legacy)
    assert completed["payload"]["query"] == EXPECTED_QUERY
    assert "entityMetadata" not in owned.payload()


def test_metadata_add_undo_redo_and_metadata_only_edit_keep_query_semantics(owned):
    legacy = value(include_metadata=False)
    owned.apply(_initial_plan(legacy))
    baseline = owned.store.state(owned.internal)
    query_record = next(record for record in baseline["definitions"] if record["layer"] == "query")
    completed = [_execute_real_and_reopen(owned, legacy)]

    with_metadata = value()
    added, _, _, _ = owned.apply({"definitions": [definition(with_metadata)]})
    completed.append(_execute_real_and_reopen(owned, with_metadata))

    # Ordinary replacement cannot drop M. Only the original authenticated Undo
    # restores its actual historical absent namespace; no snapshot is stripped.
    removed, _, _, _ = owned.apply(target=added["operationId"])
    completed.append(_execute_real_and_reopen(owned, legacy))
    owned.apply(target=removed["operationId"])
    completed.append(_execute_real_and_reopen(owned, with_metadata))

    edited = deepcopy(with_metadata)
    fields = edited["entityMetadata"]["entities"][ENTITY]
    fields["identifier"] = "MaintainableEquipment"
    fields["synonyms"].append("检修资产")
    fields["examples"].append("备用泵 B")
    owned.apply({"definitions": [definition(edited)]})
    completed.append(_execute_real_and_reopen(owned, edited))

    assert len({item["snapshot"] for item in completed}) == 5
    assert len({item["job"]["jobId"] for item in completed}) == 5
    assert len({item["job"]["resultRef"]["resultId"] for item in completed}) == 5
    for item in completed:
        # Compare semantics, not whole outputs whose snapshot/UUID binding differs.
        assert item["payload"]["query"] == completed[0]["payload"]["query"] == EXPECTED_QUERY
        assert item["payload"]["inputSnapshotId"] == item["snapshot"]
        assert item["job"]["inputSnapshotId"] == item["snapshot"]
        for field in (
            "assertedInputSha256",
            "ontologyInputSha256",
            "factViewSha256",
            "ontologyViewSha256",
        ):
            assert (
                item["payload"]["provenance"][field] == completed[0]["payload"]["provenance"][field]
            )
    after = owned.store.state(owned.internal)
    assert after["facts"] == baseline["facts"] and after["mappingState"] == baseline["mappingState"]
    assert (
        next(record for record in after["definitions"] if record["layer"] == "query")
        == query_record
    )
    assert len(after["definitions"]) == len(baseline["definitions"]) == 2
    for field in ("triples", "references", "singleValuedPredicates"):
        assert edited[field] == with_metadata[field] == legacy[field]
    for item in completed:
        # Each old accepted request and its own stored result remain readable at
        # the final project revision; no re-execution or cross-result row equality.
        assert owned.store.get_job(owned.project, item["job"]["jobId"]) == item["job"]
        metadata, payload = owned.store.semantic_result(
            owned.project, item["job"]["resultRef"]["resultId"]
        )
        assert payload == item["payload"] and metadata["inputSnapshotId"] == item["snapshot"]


@pytest.mark.parametrize("entry", ["build", "execute"])
@pytest.mark.parametrize(
    "damage", ["bool-version", "missing-field", "unknown-namespace-key", "unknown-ontology-key"]
)
def test_metadata_shape_and_unknown_keys_refuse_rehashed_request_without_db_mutation(
    owned, entry, damage
):
    owned.apply(_initial_plan(value()))
    job, accepted, _ = _accepted_query(owned)
    accepted_before = deepcopy(accepted)
    database_before = owned.dump()
    options = {"error_catalog": CONTRACT.ERROR_CATALOG, "error_schema": CONTRACT.DOCUMENT}
    # A valid control proves real decoding/imports are available, so the expected
    # INTERNAL_ERROR cannot be a false green caused by an unavailable executor.
    assert (
        build_request(
            accepted["snapshot"],
            accepted["capability"],
            accepted["input"],
            accepted["parameters"],
            accepted["selected"],
            **options,
        )
        == accepted
    )
    if entry == "execute":
        assert execute_request(accepted, **options)["payload"]["query"] == EXPECTED_QUERY

    bad = deepcopy(accepted)
    record = next(
        record
        for record in bad["snapshot"]["state"]["definitions"]
        if record["layer"] == "ontology" and record["id"] == "Equipment"
    )
    ontology = json.loads(record["payload"])
    if damage == "bool-version":
        ontology["entityMetadata"]["entityMetadataVersion"] = True
    elif damage == "missing-field":
        del ontology["entityMetadata"]["entities"][ENTITY]["examples"]
    elif damage == "unknown-namespace-key":
        ontology["entityMetadata"]["private_canary_namespace"] = "not-a-public-error-param"
    else:
        assert damage == "unknown-ontology-key"
        ontology["private_canary_ontology"] = {"not": "a public error param"}
    record["payload"] = canonical(ontology)
    bad["input"]["inputSnapshotId"] = digest(bad["snapshot"])
    assert digest(bad["snapshot"]) == bad["input"]["inputSnapshotId"]
    assert bad["input"]["inputSnapshotId"] != accepted["input"]["inputSnapshotId"]
    assert bad["snapshot"]["state"]["facts"] == accepted["snapshot"]["state"]["facts"]
    assert "entityMetadata" in json.loads(record["payload"])
    with pytest.raises(SemanticExecutionFault) as rejected:
        if entry == "build":
            build_request(
                bad["snapshot"],
                bad["capability"],
                bad["input"],
                bad["parameters"],
                bad["selected"],
                **options,
            )
        else:
            execute_request(bad, **options)
    assert rejected.value.error == {
        "code": "INTERNAL_ERROR",
        "messageKey": "engine.internal",
        "params": {},
        "retryable": False,
    }
    assert str(rejected.value) == "SEMANTIC_EXECUTION_FAILED"
    assert "private_canary" not in json.dumps(rejected.value.error)
    assert accepted == accepted_before
    assert owned.store.job_context(job["jobId"])["queryRequest"] == accepted_before
    assert owned.dump() == database_before
