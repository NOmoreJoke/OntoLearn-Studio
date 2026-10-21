"""Lexical RDF identity through real Store, isolated worker and stdio publication.

Session uses ONTOLEARN_TEST_ENGINE when supplied, so the same stdio cases run
against the packaged executable. No mock worker or direct pure result substitutes
for an authenticated persisted result, projection resource, or public result page.
"""

import asyncio
import json
import time
from uuid import UUID, uuid4

import pytest
from ontolearn_engine.coordinator import Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT, IMPLEMENTATION
from ontolearn_engine.storage import digest

TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
INTEGER = "http://www.w3.org/2001/XMLSchema#integer"
ONE = f'"1"^^<{INTEGER}>'
ZERO_ONE = f'"01"^^<{INTEGER}>'
CASES = (
    "canonical-validation",
    "canonical-query",
    "selected-derived-validation",
    "selected-derived-query",
    "rule-term-identity",
    "historical-selected-derived",
)


def uid():
    return str(uuid4())


def definition(layer, identity, value):
    return {"layer": layer, "id": identity, "value": value}


def shapes(target, path):
    return f"""@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
<urn:LexicalShape> a sh:NodeShape; sh:targetClass <{target}>;
    sh:property <urn:LexicalProperty> .
<urn:LexicalProperty> sh:path <{path}>; sh:minCount 1; sh:in ("01"^^xsd:integer) .
"""


CONSTRAINTS = {
    "canonical": {"enabled": True, "turtle": shapes("urn:Canonical", "urn:p")},
    "derived": {"enabled": True, "turtle": shapes("urn:Derived", "urn:derived")},
}
FACTS = sorted(
    [
        ["<urn:canonical-unit>", f"<{TYPE}>", "<urn:Canonical>"],
        ["<urn:canonical-unit>", "<urn:p>", ONE],
        ["<urn:derived-unit>", f"<{TYPE}>", "<urn:Derived>"],
    ]
)
DERIVED = sorted(
    [
        ["<urn:canonical-unit>", "<urn:matched>", '"yes"'],
        ["<urn:derived-unit>", "<urn:derived>", ZERO_ONE],
    ]
)


def seed(store):
    store.create_project("lexical")
    project = store.public_project("lexical")
    rules = [
        (
            "emit-lexical",
            ["<urn:derived-unit>", f"<{TYPE}>", "<urn:Derived>"],
            ["<urn:derived-unit>", "<urn:derived>", ZERO_ONE],
        ),
        (
            "match-same-term",
            ["<urn:canonical-unit>", "<urn:p>", ONE],
            ["<urn:canonical-unit>", "<urn:matched>", '"yes"'],
        ),
        (
            "reject-same-value",
            ["<urn:canonical-unit>", "<urn:p>", ZERO_ONE],
            ["<urn:canonical-unit>", "<urn:wrong>", '"must-not-exist"'],
        ),
    ]
    store.commit(
        "lexical",
        0,
        uid(),
        uid(),
        definitions=[
            definition("ontology", "classes", {"triples": []}),
            *[
                definition("rule", identity, {"enabled": True, "when": [when], "then": then})
                for identity, when, then in rules
            ],
            *[definition("constraint", identity, value) for identity, value in CONSTRAINTS.items()],
            definition("query", "canonical", {"text": "ASK { <urn:canonical-unit> <urn:p> 01 }"}),
            definition("query", "derived", {"text": "ASK { <urn:derived-unit> <urn:derived> 01 }"}),
        ],
        manual=[
            {
                "id": digest([subject[1:-1], predicate[1:-1], obj]),
                "subject": subject[1:-1],
                "predicate": predicate[1:-1],
                "object": obj,
            }
            for subject, predicate, obj in FACTS
        ],
    )
    return project


class DirectWorker:
    """The real coordinator starts its normal isolated Python worker process."""

    def __init__(self, database, project):
        self.store = JobStore(database, contract=CONTRACT)
        self.project = project
        self.coordinator = Coordinator(self.store, allowed_projects={project}, emit=lambda _: None)
        hello = self.call("hello", {"supportedVersions": [2], "clientId": uid()})
        assert hello["engineSessionId"] == self.coordinator.session

    def call(self, method, params):
        response = self.coordinator.request(
            {
                "kind": "request",
                "protocolVersion": 2,
                "id": uid(),
                "engineSessionId": None if method == "hello" else self.coordinator.session,
                "method": method,
                "params": params,
            }
        )
        assert CONTRACT.validate("response", response), response
        return response["result"] if response["ok"] else response["error"]

    def terminal(self, project, identity):
        async def finish():
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                await self.coordinator.tick()
                await asyncio.sleep(0.01)
                value = self.store.get_job(project, identity)
                if value["state"] in {"succeeded", "failed", "cancelled"}:
                    await asyncio.gather(*self.coordinator.tasks)
                    return value
            raise AssertionError("real lexical worker completion deadline")

        return asyncio.run(finish())

    def close(self):
        try:
            asyncio.run(self.coordinator.stop())
        finally:
            self.store.close()


def parameters(project, capability, definition_id, *, derived=None, snapshot=None):
    return {
        "projectId": project,
        "operationId": uid(),
        "capability": capability,
        "definitionId": definition_id,
        "scope": "asserted+derived" if derived else "asserted",
        "derivedResultId": derived,
        "inputSelection": "historical" if snapshot else "current",
        "inputSnapshotId": snapshot,
    }


def completed(backend, request):
    project = request["projectId"]
    created = backend.call("semantic.start", request)
    assert "jobId" in created, created
    job = backend.terminal(project, created["jobId"])
    assert job["state"] == "succeeded", job
    assert job["commitProgress"] == {"mode": "none"}
    result = backend.call(
        "result.get", {"projectId": project, "resultId": job["resultRef"]["resultId"]}
    )
    assert CONTRACT.validate("result", result), result
    assert result["jobId"] == job["jobId"]
    assert result["projectId"] == project
    assert result["implementation"] == job["implementation"] == IMPLEMENTATION
    assert result["kind"] == request["capability"].split(".")[0]
    assert result["definitionId"] == request["definitionId"]
    assert result["scope"] == request["scope"]
    assert result["inputSnapshotId"] == job["inputSnapshotId"]
    assert result["payloadStatus"] == "available"
    assert result["state"] == (
        "historical" if request["inputSelection"] == "historical" else "current"
    )
    assert result["historicalSelectionRequired"] is (request["inputSelection"] == "historical")
    binding = {
        "projectId": project,
        "resultId": result["resultId"],
        "inputSnapshotId": result["inputSnapshotId"],
        "scope": result["scope"],
        "parametersHash": result["parametersHash"],
        "order": "ordinal+rowId:asc",
    }
    rows = []
    cursor = None
    while True:
        page_request = {"binding": binding, "pageSize": 17, "cursor": cursor}
        page = backend.call("result.page", page_request)
        assert page == backend.call("result.page", page_request)
        assert page["binding"] == binding
        rows.extend(page["rows"])
        cursor = page["nextCursor"]
        if cursor is None:
            break
    assert [row["ordinal"] for row in rows] == list(range(len(rows)))
    assert len({row["rowId"] for row in rows}) == len(rows)
    assert all(UUID(row["rowId"]).version == 4 for row in rows)
    return {"job": job, "metadata": result, "rows": rows, "request": request}


def expected_reasoning():
    source_type = ["<urn:derived-unit>", f"<{TYPE}>", "<urn:Derived>"]
    source_one = ["<urn:canonical-unit>", "<urn:p>", ONE]
    return {
        "rdfs": [],
        "rules": DERIVED,
        "warnings": [],
        "rdfsEvidence": [],
        "evidence": [
            {
                "rule": "emit-lexical",
                "result": DERIVED[1],
                "inputs": [source_type],
                "basis": [source_type],
            },
            {
                "rule": "match-same-term",
                "result": DERIVED[0],
                "inputs": [source_one],
                "basis": [source_one],
            },
        ],
    }


def assert_binding(store, project, payload, selected):
    binding = payload["validationBinding"]
    projection = binding["projection"]
    resources = binding["resources"]
    assert CONTRACT.validation_projection_matches_resources(projection, resources)
    assert projection["projectId"] == project
    assert projection["inputSnapshotId"] == payload["inputSnapshotId"]
    assert projection["inputProjectRevision"] == payload["inputProjectRevision"] == 1
    assert projection["implementation"] == IMPLEMENTATION
    assert projection["scope"] == payload["scope"]
    assert projection["inputSelection"] == payload["inputSelection"]
    assert projection["constraintDefinitionId"] == payload["definitionId"]
    expected = {
        "assertedFacts": FACTS,
        "ontologyAxioms": [],
        "constraints": CONSTRAINTS[payload["definitionId"]],
    }
    if selected:
        assert projection["derived"]["resultId"] == selected
        assert payload["selectedResultIds"] == [selected]
        expected.update(derivedFacts=DERIVED, derivedAxioms=[])
    else:
        assert projection["derived"] is None
        assert payload["selectedResultIds"] == []
    assert {row["role"] for row in resources} == set(expected)
    for resource in resources:
        encoded = store._db.execute(
            "SELECT payload FROM semantic_resources WHERE project=? AND ref=?",
            (project, resource["ref"]),
        ).fetchone()
        assert encoded is not None
        value = json.loads(encoded[0])
        assert value == expected[resource["role"]]
        assert digest(value) == resource["ref"]
        assert resource["resultId"] == (
            selected if resource["role"].startswith("derived") else None
        )
        if resource["role"].startswith("derived"):
            assert resource["implementation"] == IMPLEMENTATION
            assert resource["resultKind"] == "reasoning"
            assert resource["payloadStatus"] == "available"
            assert resource["resultState"] == (
                "historical" if payload["inputSelection"] == "historical" else "current"
            )


def exercise(tmp_path, mode, case):
    from test_resident_runtime import Session

    database = tmp_path / "lexical.sqlite"
    store = JobStore(database, contract=CONTRACT)
    project = seed(store)
    original = store.state("lexical")
    snapshot = store.project_get(project)["inputSnapshotId"]
    store.close()
    backend = (
        DirectWorker(database, project)
        if mode == "worker"
        else Session(database, [project], test_mode=False)
    )
    saved = []
    try:
        reasoning = completed(backend, parameters(project, "reasoning.execute", "all"))
        saved.append(reasoning)
        selected = reasoning["metadata"]["resultId"]
        if case == "historical-selected-derived":
            current = completed(backend, parameters(project, "reasoning.execute", "all"))
            saved.append(current)
            assert current["metadata"]["resultId"] != selected
            old = backend.call("result.get", {"projectId": project, "resultId": selected})
            assert old["state"] == "historical" and old["historicalSelectionRequired"]
            rejected = backend.call(
                "semantic.start",
                parameters(project, "validation.execute", "derived", derived=selected),
            )
            assert CONTRACT.validate("error", rejected)
            assert rejected["code"] == "IDENTITY_CONFLICT"
            for capability in ("validation.execute", "query.execute"):
                saved.append(
                    completed(
                        backend,
                        parameters(
                            project, capability, "derived", derived=selected, snapshot=snapshot
                        ),
                    )
                )
        elif case != "rule-term-identity":
            capability = "validation.execute" if case.endswith("validation") else "query.execute"
            definition_id = "canonical" if case.startswith("canonical") else "derived"
            saved.append(
                completed(
                    backend,
                    parameters(
                        project,
                        capability,
                        definition_id,
                        derived=selected if case.startswith("selected") else None,
                    ),
                )
            )
    finally:
        backend.close()

    store = JobStore(database, contract=CONTRACT)
    try:
        for record in saved:
            metadata, payload = store.semantic_result(project, record["metadata"]["resultId"])
            assert metadata["inputSnapshotId"] == payload["inputSnapshotId"] == snapshot
            assert metadata["implementation"] == IMPLEMENTATION
            assert (
                payload["executionSemanticsVersion"] == IMPLEMENTATION["executionSemanticsVersion"]
            )
            assert metadata["parametersHash"] == record["job"]["parametersHash"]
            assert store.get_job(project, record["job"]["jobId"]) == record["job"]
            assert store.result(metadata["resultId"])["payload"] == record["rows"]
            if payload["kind"] == "reasoning":
                assert payload["reasoning"] == expected_reasoning()
                assert payload["assertedFacts"] == FACTS
                assert payload["ontology"] == []
                continue
            historical = record["request"]["inputSelection"] == "historical"
            assert metadata["state"] == ("historical" if historical else "current")
            assert metadata["historicalSelectionRequired"] is historical
            assert payload["inputSelection"] == ("historical" if historical else "current")
            if payload["kind"] == "query":
                assert payload["query"] == {
                    "type": "ASK",
                    "value": payload["definitionId"] == "derived",
                }
            else:
                assert payload["constraintsVersion"] == 1
                assert payload["constraintsHash"] == digest(CONSTRAINTS[payload["definitionId"]])
                derived = selected if payload["definitionId"] == "derived" else None
                assert_binding(store, project, payload, derived)
                expected = {"conforms": True, "violations": []}
                if payload["definitionId"] == "canonical":
                    expected = {
                        "conforms": False,
                        "violations": [
                            {
                                "focus": "<urn:canonical-unit>",
                                "path": "<urn:p>",
                                "constraint": "<http://www.w3.org/ns/shacl#InConstraintComponent>",
                                "sourceShape": "<urn:LexicalProperty>",
                                "value": ONE,
                                "severity": "<http://www.w3.org/ns/shacl#Violation>",
                            }
                        ],
                    }
                assert payload["report"] == expected
        assert store.state("lexical") == original
    finally:
        store.close()


@pytest.mark.parametrize("case", CASES)
def test_real_store_coordinator_worker_lexical_identity(tmp_path, case):
    exercise(tmp_path, "worker", case)


@pytest.mark.parametrize("case", CASES)
def test_actual_stdio_source_or_packaged_lexical_identity(tmp_path, case):
    exercise(tmp_path, "stdio", case)
