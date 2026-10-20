"""I05 real worker/JobStore publication, selection and fault integration (no desktop)."""

import asyncio
import json
import sqlite3
import time
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import Coordinator
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.resources import CONTRACT, IMPLEMENTATION, LIMITS
from ontolearn_engine.storage import canonical, digest

TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
SUBCLASS = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
SHAPES = """@prefix : <urn:> . @prefix sh: <http://www.w3.org/ns/shacl#> .
:BaseShape a sh:NodeShape; sh:targetClass :Parent; sh:property :BaseName .
:BaseName a sh:PropertyShape; sh:path :name; sh:minCount 1 .
:RiskShape a sh:NodeShape; sh:targetClass :Risk; sh:property :RiskName .
:RiskName a sh:PropertyShape; sh:path :name; sh:minCount 1 .
"""


def uid():
    return str(uuid4())


def definition(layer, identity, value):
    return {"layer": layer, "id": identity, "value": value}


def risk(enabled=True):
    return definition(
        "rule",
        "risk",
        {
            "enabled": enabled,
            "when": [["?x", f"<{TYPE}>", "<urn:Parent>"]],
            "then": ["?x", f"<{TYPE}>", "<urn:Risk>"],
        },
    )


def seed(store, *, enabled=True):
    store.create_project("semantic")
    project = store.public_project("semantic")
    store.commit(
        "semantic",
        0,
        uid(),
        uid(),
        definitions=[
            definition(
                "ontology",
                "classes",
                {
                    "triples": [
                        {"subject": "urn:Child", "predicate": SUBCLASS, "object": "<urn:Parent>"},
                    ]
                },
            ),
            risk(enabled),
            definition("query", "types", {"text": "SELECT ?type WHERE { <urn:unit> a ?type }"}),
            definition("constraint", "names", {"enabled": True, "turtle": SHAPES}),
        ],
        manual=[
            {
                "id": digest(["urn:unit", TYPE, "<urn:Child>"]),
                "subject": "urn:unit",
                "predicate": TYPE,
                "object": "<urn:Child>",
            }
        ],
    )
    return project


@pytest.fixture
def runtime(tmp_path):
    store = JobStore(tmp_path / "semantic.sqlite", contract=CONTRACT)
    project = seed(store)
    coordinator = Coordinator(store, allowed_projects={project}, emit=lambda _: None)
    yield store, coordinator, project
    asyncio.run(coordinator.stop())
    store.close()


def start(
    c,
    project,
    capability="reasoning.execute",
    *,
    scope="asserted",
    derived=None,
    selection="current",
    snapshot=None,
    definition_id="all",
    operation=None,
):
    p = {
        "projectId": project,
        "operationId": operation or uid(),
        "capability": capability,
        "scope": scope,
        "definitionId": definition_id,
        "derivedResultId": derived,
        "inputSelection": selection,
        "inputSnapshotId": snapshot,
    }
    if c.session is None:
        hello = c.request(
            {
                "kind": "request",
                "protocolVersion": 2,
                "id": uid(),
                "engineSessionId": None,
                "method": "hello",
                "params": {"supportedVersions": [2], "clientId": uid()},
            }
        )
        assert hello["ok"]
    response = c.request(
        {
            "kind": "request",
            "protocolVersion": 2,
            "id": uid(),
            "engineSessionId": c.session,
            "method": "semantic.start",
            "params": p,
        }
    )
    assert CONTRACT.validate("response", response), response
    return response


def drain(c, store, project, *jobs, on_running=None):
    async def run():
        deadline = time.monotonic() + 15
        called = False
        while time.monotonic() < deadline:
            await c.tick()
            await asyncio.sleep(0.01)
            values = [store.get_job(project, j["jobId"]) for j in jobs]
            if on_running and not called and any(j["state"] == "running" for j in values):
                called = True
                on_running(values)
            if all(j["state"] in {"succeeded", "failed", "cancelled"} for j in values):
                await asyncio.gather(*c.tasks)
                return values
        raise AssertionError("real worker completion deadline")

    return asyncio.run(run())


def completed(c, s, p, **kwargs):
    response = start(c, p, **kwargs)
    assert response["ok"], response
    job = drain(c, s, p, response["result"])[0]
    assert job["state"] == "succeeded", job
    metadata, payload = s.semantic_result(p, job["resultRef"]["resultId"])
    return job, metadata, payload


def test_real_reason_query_validation_complete_sources_and_stable_pages(runtime):
    s, c, p = runtime
    before = s.state("semantic")
    job, metadata, output = completed(c, s, p)
    assert output["reasoning"]["rules"] == [["<urn:unit>", f"<{TYPE}>", "<urn:Risk>"]]
    assert output["reasoning"]["rdfs"] == [["<urn:unit>", f"<{TYPE}>", "<urn:Parent>"]]
    assert output["reasoning"]["evidence"][0]["rule"] == "risk"
    assert metadata["state"] == "current" and job["implementation"] == IMPLEMENTATION
    assert metadata["definitionSetDigests"]["rule"]
    _, _, asserted = completed(c, s, p, capability="query.execute", definition_id="types")
    assert asserted["query"]["rows"] == [["<urn:Child>"]]
    _, _, selected = completed(
        c,
        s,
        p,
        capability="query.execute",
        definition_id="types",
        scope="asserted+derived",
        derived=metadata["resultId"],
    )
    assert selected["query"]["rows"] == [["<urn:Child>"], ["<urn:Parent>"], ["<urn:Risk>"]]
    validation_job, validation, report = completed(
        c,
        s,
        p,
        capability="validation.execute",
        definition_id="names",
        scope="asserted+derived",
        derived=metadata["resultId"],
    )
    assert {v["sourceShape"] for v in report["report"]["violations"]} == {
        "<urn:BaseName>",
        "<urn:RiskName>",
    }
    assert report["constraintsVersion"] == 1
    assert report["selectedResultIds"] == [metadata["resultId"]]
    binding = {
        "projectId": p,
        "resultId": validation["resultId"],
        "inputSnapshotId": validation["inputSnapshotId"],
        "scope": validation["scope"],
        "parametersHash": validation["parametersHash"],
        "order": "ordinal+rowId:asc",
    }
    page = s.result_page(binding, 10, None)
    assert s.result_page(binding, 10, None) == page
    rows = list(page["rows"])
    while page["nextCursor"]:
        page = s.result_page(binding, 10, page["nextCursor"])
        rows.extend(page["rows"])
    assert rows == s.result(validation["resultId"])["payload"]
    assert all(a["ordinal"] < b["ordinal"] for a, b in zip(rows, rows[1:], strict=False))
    assert s.state("semantic") == before
    assert validation_job["commitProgress"] == {"mode": "none"}


def test_earlier_existing_real_result_is_selected_without_recomputation(tmp_path):
    s = JobStore(tmp_path / "history.sqlite", contract=CONTRACT)
    try:
        p = seed(s, enabled=False)
        c = Coordinator(s, allowed_projects={p}, emit=lambda _: None)
        old, old_meta, old_payload = completed(c, s, p)
        assert old_payload["reasoning"]["rules"] == []
        old_snapshot = old["inputSnapshotId"]
        s.commit("semantic", 1, uid(), uid(), definitions=[risk(True)])
        assert s.result_get(p, old_meta["resultId"])["state"] == "stale"
        _, current, _ = completed(c, s, p)
        _, _, now = completed(
            c,
            s,
            p,
            capability="validation.execute",
            definition_id="names",
            scope="asserted+derived",
            derived=current["resultId"],
        )
        _, history, earlier = completed(
            c,
            s,
            p,
            capability="validation.execute",
            definition_id="names",
            scope="asserted+derived",
            derived=old_meta["resultId"],
            selection="historical",
            snapshot=old_snapshot,
        )
        assert len(now["report"]["violations"]) == 2
        assert len(earlier["report"]["violations"]) == 1
        assert earlier["selectedResultIds"] == [old_meta["resultId"]]
        assert earlier["inputSnapshotId"] == old_snapshot
        assert history["state"] == "stale" and history["historicalSelectionRequired"]
        rejected = start(
            c,
            p,
            capability="validation.execute",
            definition_id="names",
            scope="asserted+derived",
            derived=old_meta["resultId"],
        )
        assert not rejected["ok"] and rejected["error"]["code"] == "IDENTITY_CONFLICT"
    finally:
        s.close()


@pytest.mark.parametrize("change", ["scope", "history", "reasoning-derived"])
def test_public_selection_combinations_are_safe_invalid_request(runtime, change):
    _, c, p = runtime
    kwargs = (
        {"scope": "asserted+derived"}
        if change == "scope"
        else (
            {"selection": "historical"}
            if change == "history"
            else {"scope": "asserted+derived", "derived": uid()}
        )
    )
    result = start(c, p, **kwargs)
    assert result["error"] == {
        "code": "INVALID_REQUEST",
        "messageKey": "protocol.invalidRequest",
        "params": {"field": "params"},
        "retryable": False,
    }


def test_historical_selection_never_publishes_current_even_when_snapshot_is_latest(runtime):
    s, c, p = runtime
    snapshot = s.project_get(p)["inputSnapshotId"]
    _, meta, _ = completed(c, s, p, selection="historical", snapshot=snapshot)
    assert meta["state"] == "historical" and meta["historicalSelectionRequired"]


def test_semantic_operation_idempotent_after_current_moves_and_cannot_change_meaning(runtime):
    s, c, p = runtime
    operation = uid()
    job, _, _ = completed(c, s, p, operation=operation)
    s.commit("semantic", 1, uid(), uid(), definitions=[risk(False)])
    same = start(c, p, operation=operation)
    assert same["result"] == s.get_job(p, job["jobId"])
    altered = start(c, p, operation=operation, definition_id="different")
    assert altered["error"]["code"] == "IDENTITY_CONFLICT"
    assert s._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 1


def test_real_user_query_error_has_fixed_safe_dto_and_no_unpublished_payload(runtime):
    s, c, p = runtime
    s.commit(
        "semantic",
        1,
        uid(),
        uid(),
        definitions=[
            definition(
                "query",
                "types",
                {
                    "text": (
                        "SELECT * WHERE { SERVICE <http://127.0.0.1:9/CANARY-SECRET> { ?s ?p ?o } }"
                    )
                },
            )
        ],
    )
    job = start(c, p, "query.execute", definition_id="types")["result"]
    terminal = drain(c, s, p, job)[0]
    assert terminal["state"] == "failed"
    assert terminal["error"]["code"] == "NETWORK_FORBIDDEN"
    assert "CANARY" not in canonical(terminal)
    assert terminal["resultRef"] is None
    assert s._db.execute("SELECT count(*) FROM semantic_payloads").fetchone()[0] == 0


def test_queued_and_real_worker_cancel_discard_only_the_selected_result(runtime):
    s, c, p = runtime
    queued = start(c, p)["result"]
    c.dispatch("job.cancel", {"projectId": p, "jobId": queued["jobId"]})
    assert s.get_job(p, queued["jobId"])["state"] == "cancelled"
    cancelled = start(c, p)["result"]
    sibling = start(c, p, "query.execute", definition_id="types")["result"]

    def cancel(_):
        assert c.dispatch("session.ping", {"nonce": uid()})
        c.dispatch("job.cancel", {"projectId": p, "jobId": cancelled["jobId"]})

    values = drain(c, s, p, cancelled, sibling, on_running=cancel)
    assert [j["state"] for j in values] == ["cancelled", "succeeded"]
    assert values[0]["resultRef"] is None
    assert s._db.execute("SELECT count(*) FROM semantic_payloads").fetchone()[0] == 1


@pytest.mark.parametrize("phase", ["mid_job_terminal", "before_commit"])
def test_complete_semantic_payload_and_job_terminal_rollback_together(runtime, phase):
    from ontolearn_engine.semantic_execution import execute_request

    s, c, p = runtime
    job = start(c, p)["result"]
    s.start_job(job["jobId"])
    output = execute_request(
        s.job_context(job["jobId"])["semanticRequest"],
        error_catalog=CONTRACT.ERROR_CATALOG,
        error_schema=CONTRACT.DOCUMENT,
    )

    binding = s.job_context(job["jobId"]).get("validationBinding")
    if binding:
        output["payload"]["validationBinding"] = binding

    def fail(where):
        if where == phase:
            raise OSError("private-path-and-canary")

    with pytest.raises(OSError):
        s.finish_semantic_job(job["jobId"], output, hook=fail)
    assert s.get_job(p, job["jobId"])["state"] == "running"
    for table in ("results", "job_results", "semantic_payloads", "job_current"):
        assert s._db.execute(f"SELECT count(*) FROM {table}").fetchone()[0] == 0


def test_authentic_payload_hash_producer_and_eviction_boundaries(runtime):
    s, c, p = runtime
    job, meta, _ = completed(c, s, p)
    identity = meta["resultId"]
    with pytest.raises(sqlite3.IntegrityError):
        s._db.execute("UPDATE semantic_payloads SET payload='{}' WHERE result=?", (identity,))
    s.create_project("other")
    other = s.public_project("other")
    with pytest.raises(JobFault, match="NOT_FOUND"):
        s.semantic_result(other, identity)
    completed(c, s, p)  # Make first result historical, while retaining its exact identity.
    assert s.result_get(p, identity)["state"] == "historical"
    rejected = start(
        c, p, "query.execute", scope="asserted+derived", derived=identity, definition_id="types"
    )
    assert rejected["error"]["code"] == "IDENTITY_CONFLICT"
    assert identity in s.collect_cache()
    assert (
        s._db.execute(
            "SELECT payload FROM semantic_payloads WHERE result=?", (identity,)
        ).fetchone()[0]
        is None
    )
    with pytest.raises(JobFault, match="PAYLOAD_EVICTED"):
        s.semantic_result(p, identity)
    assert s.get_job(p, job["jobId"])["state"] == "succeeded"


def test_large_complete_output_is_chunked_not_a_single_frame(runtime):
    s, c, p = runtime
    # Input and result exceed the public 256KiB frame while every individual term
    # and private chunk stay within their independent finite budgets.
    facts = [
        {
            "id": digest([f"urn:item:{i}", "urn:name", json.dumps("x" * 1200)]),
            "subject": f"urn:item:{i}",
            "predicate": "urn:name",
            "object": json.dumps("x" * 1200),
        }
        for i in range(240)
    ]
    s.commit("semantic", 1, uid(), uid(), manual=facts)
    _, meta, payload = completed(c, s, p, capability="query.execute", definition_id="types")
    assert payload["query"]["rows"] == [["<urn:Child>"]]
    # Query projection includes the complete fact provenance, not a truncated subset.
    assert len(canonical(payload).encode()) > 262144
    assert meta["payloadStatus"] == "available"


def test_late_semantic_result_preserves_original_input_and_is_not_current(runtime):
    s, c, p = runtime
    job = start(c, p)["result"]
    old_snapshot = job["inputSnapshotId"]

    def change(_):
        s.commit("semantic", 1, uid(), uid(), definitions=[risk(False)])

    done = drain(c, s, p, job, on_running=change)[0]
    metadata, payload = s.semantic_result(p, done["resultRef"]["resultId"])
    assert metadata["state"] == "stale" and payload["inputSnapshotId"] == old_snapshot
    assert payload["reasoning"]["rules"]
    assert s._db.execute("SELECT count(*) FROM job_current").fetchone()[0] == 0


def test_implementation_identity_is_exact_for_selected_real_result(runtime):
    s, c, p = runtime
    _, meta, _ = completed(c, s, p)
    snapshot = s.project_get(p)
    input_ = {
        "inputSnapshotId": snapshot["inputSnapshotId"],
        "scope": "asserted+derived",
        "definitionId": "types",
        "parametersHash": s.put_blob(p, {}),
        "derivedResultIds": [meta["resultId"]],
        "preparedPlanRef": None,
    }
    for key, value in [
        ("engineVersion", "other"),
        ("executionSemanticsVersion", "other"),
        ("dependencyLockHash", "a" * 64),
    ]:
        implementation = {**IMPLEMENTATION, key: value}
        with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
            s.create_job(p, uid(), "query.execute", input_, None, implementation, LIMITS)
    assert digest(s.blob(p, input_["parametersHash"])) == input_["parametersHash"]


def test_private_semantic_chunks_do_not_use_the_smaller_public_frame_budget(runtime):
    s, _, p = runtime
    # A valid smaller public request budget must not reinterpret the separately
    # bounded private worker chunks as public JSONL frames.
    c = Coordinator(s, allowed_projects={p}, limits={"maxFrameBytes": 1024}, emit=lambda _: None)
    _, _, output = completed(c, s, p)
    assert output["reasoning"]["rules"]
    assert len(canonical(output).encode()) > 1024


def test_actual_stdio_source_or_packaged_jobs_persist_all_three_semantic_outputs(tmp_path):
    from test_resident_runtime import Session

    database = tmp_path / "stdio-semantic.sqlite"
    s = JobStore(database, contract=CONTRACT)
    p = seed(s)
    snapshot = s.project_get(p)["inputSnapshotId"]
    before = s.state("semantic")
    s.close()
    session = Session(database, [p], test_mode=False)
    saved = []
    try:
        for capability, definition_id in [
            ("reasoning.execute", "all"),
            ("query.execute", "types"),
            ("validation.execute", "names"),
        ]:
            request = {
                "projectId": p,
                "operationId": uid(),
                "capability": capability,
                "definitionId": definition_id,
                "scope": "asserted" if not saved else "asserted+derived",
                "derivedResultId": saved[0]["resultRef"]["resultId"] if saved else None,
                "inputSelection": "current",
                "inputSnapshotId": None,
            }
            job = session.call("semantic.start", request)
            assert "jobId" in job, job
            terminal = session.terminal(p, job["jobId"])
            assert terminal["state"] == "succeeded", terminal
            result = session.call(
                "result.get", {"projectId": p, "resultId": terminal["resultRef"]["resultId"]}
            )
            assert (
                result["kind"] == capability.split(".")[0] and result["inputSnapshotId"] == snapshot
            )
            assert result["implementation"] == IMPLEMENTATION
            saved.append(terminal)
        error = session.call(
            "semantic.start", {**request, "projectId": uid(), "operationId": uid()}
        )
        assert error["code"] == "PERMISSION_DENIED"
    finally:
        session.close()
    s = JobStore(database, contract=CONTRACT)
    try:
        payloads = [s.semantic_result(p, job["resultRef"]["resultId"])[1] for job in saved]
        assert payloads[0]["reasoning"]["rules"] == [["<urn:unit>", f"<{TYPE}>", "<urn:Risk>"]]
        assert payloads[1]["query"]["rows"] == [["<urn:Child>"], ["<urn:Parent>"], ["<urn:Risk>"]]
        assert len(payloads[2]["report"]["violations"]) == 2
        binding = payloads[2]["validationBinding"]
        assert CONTRACT.validation_projection_matches_resources(
            binding["projection"], binding["resources"]
        )
        assert binding["projection"]["derived"]["resultId"] == saved[0]["resultRef"]["resultId"]
        assert all(
            s._db.execute(
                "SELECT payload FROM semantic_resources WHERE project=? AND ref=?", (p, r["ref"])
            ).fetchone()
            for r in binding["resources"]
        )
        assert s.state("semantic") == before
    finally:
        s.close()


@pytest.mark.parametrize("tamper", ["bytes", "rehash-wrong-input-version", "producer-ref"])
def test_corrupt_selected_immutable_evidence_is_internal_not_user_input(runtime, tamper):
    s, c, p = runtime
    job, meta, payload = completed(c, s, p)
    identity = meta["resultId"]
    if tamper == "producer-ref":
        job["resultRef"]["resultId"] = uid()
        s._db.execute("UPDATE jobs SET dto=? WHERE id=?", (canonical(job), job["jobId"]))
    else:
        # Deliberately bypass an already-tested immutable trigger to model disk
        # corruption. This is never a product API or accepted renderer option.
        s._db.execute("DROP TRIGGER immutable_semantic_payloads_UPDATE")
        payload["inputProjectRevision"] += 1
        if tamper == "bytes":
            s._db.execute(
                "UPDATE semantic_payloads SET payload=? WHERE result=?",
                (canonical(payload), identity),
            )
        else:
            s._db.execute(
                "UPDATE semantic_payloads SET payload=?,payload_hash=? WHERE result=?",
                (canonical(payload), digest(payload), identity),
            )
    rejected = start(
        c,
        p,
        "validation.execute",
        definition_id="names",
        scope="asserted+derived",
        derived=identity,
    )
    assert rejected["error"] == {
        "code": "INTERNAL_ERROR",
        "messageKey": "engine.internal",
        "params": {},
        "retryable": False,
    }


def test_real_validation_binding_rejects_wrong_role_ref_constraint_and_result_identity(runtime):
    s, c, p = runtime
    _, reason, _ = completed(c, s, p)
    _, _, payload = completed(
        c,
        s,
        p,
        capability="validation.execute",
        definition_id="names",
        scope="asserted+derived",
        derived=reason["resultId"],
    )
    original = payload["validationBinding"]
    import copy

    for field, value in [
        ("ref", "a" * 64),
        ("role", "constraints"),
        ("resultId", uid()),
        ("projectId", uid()),
        ("inputSnapshotId", "b" * 64),
        ("resultState", "historical"),
        ("constraintDefinitionId", "other"),
    ]:
        changed = copy.deepcopy(original)
        row = next(r for r in changed["resources"] if r["role"] == "derivedFacts")
        row[field] = value
        assert not CONTRACT.validation_projection_matches_resources(
            changed["projection"], changed["resources"]
        )


@pytest.mark.parametrize(
    "predicate,obj,code,params",
    [
        (
            TYPE,
            "<http://www.w3.org/2002/07/owl#Restriction>",
            "UNSUPPORTED_CONSTRUCT",
            {"construct": "owlExpression"},
        ),
        (
            "http://www.w3.org/2000/01/rdf-schema#subPropertyOf",
            "<urn:p>",
            "UNSUPPORTED_CONSTRUCT",
            {"construct": "rdfsConstruct"},
        ),
        (
            "urn:p",
            '"value"^^<urn:customDatatype>',
            "UNSUPPORTED_CONSTRUCT",
            {"construct": "datatype"},
        ),
        ("urn:p", json.dumps("x" * 1048577), "RESOURCE_LIMIT", {"resource": "semanticInput"}),
    ],
)
def test_saved_user_ontology_content_has_real_safe_semantic_classification(
    runtime, predicate, obj, code, params
):
    s, c, p = runtime
    s.commit(
        "semantic",
        1,
        uid(),
        uid(),
        definitions=[
            definition(
                "ontology",
                "outside",
                {
                    "triples": [
                        {"subject": "urn:Unsupported", "predicate": predicate, "object": obj}
                    ]
                },
            )
        ],
    )
    job = start(c, p)["result"]
    done = drain(c, s, p, job)[0]
    assert done["state"] == "failed" and done["resultRef"] is None
    assert done["error"]["code"] == code and done["error"]["params"] == params
    assert CONTRACT.validate("error", done["error"])


def test_rule_term_lexical_budget_is_not_misclassified_as_internal(runtime):
    s, c, p = runtime
    rule = risk(True)
    rule["value"]["then"] = ["?x", "<urn:long>", json.dumps("x" * 1048577)]
    s.commit("semantic", 1, uid(), uid(), definitions=[rule])
    job = start(c, p)["result"]
    done = drain(c, s, p, job)[0]
    assert done["state"] == "failed" and done["error"]["code"] == "RESOURCE_LIMIT"
    assert done["error"]["params"] == {"resource": "semanticInput"}


def test_disabled_rule_lexical_content_is_not_executed_or_charged(runtime):
    s, c, p = runtime
    rule = risk(False)
    rule["id"] = "disabled-large"
    rule["value"]["then"] = ["?x", "<urn:long>", json.dumps("x" * 1048577)]
    s.commit("semantic", 1, uid(), uid(), definitions=[rule])
    _, _, payload = completed(c, s, p)
    assert payload["reasoning"]["rules"] == [["<urn:unit>", f"<{TYPE}>", "<urn:Risk>"]]


def test_unknown_user_definition_or_historical_snapshot_is_a_safe_selection_error(runtime):
    s, c, p = runtime
    missing_definition = start(c, p, "query.execute", definition_id="not-saved")
    assert missing_definition["error"]["code"] == "INVALID_REQUEST"
    assert missing_definition["error"]["params"] == {"field": "dependency"}
    missing_snapshot = start(
        c, p, "query.execute", definition_id="types", selection="historical", snapshot="a" * 64
    )
    assert missing_snapshot["error"]["code"] == "NOT_FOUND"
    assert missing_snapshot["error"]["params"] == {"resource": "snapshot"}
    assert s._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0


def test_final_authenticated_binding_row_budget_has_safe_result_error(runtime):
    from ontolearn_engine.semantic_execution import execute_request

    s, c, p = runtime
    facts = [
        {
            "id": digest([f"urn:many{i}", TYPE, "<urn:Parent>"]),
            "subject": f"urn:many{i}",
            "predicate": TYPE,
            "object": "<urn:Parent>",
        }
        for i in range(994)
    ]
    s.commit("semantic", 1, uid(), uid(), manual=facts)
    job = start(c, p, "validation.execute", definition_id="names")["result"]
    request = s.job_context(job["jobId"])["semanticRequest"]
    raw = execute_request(
        request, error_catalog=CONTRACT.ERROR_CATALOG, error_schema=CONTRACT.DOCUMENT
    )
    assert len(raw["rows"]) <= 10000  # Pure result fits; authenticated binding is additional.
    done = drain(c, s, p, job)[0]
    assert done["state"] == "failed" and done["resultRef"] is None
    assert done["error"]["code"] == "RESOURCE_LIMIT"
    assert done["error"]["params"] == {"resource": "semanticResult"}
    assert s._db.execute("SELECT count(*) FROM semantic_payloads").fetchone()[0] == 0
