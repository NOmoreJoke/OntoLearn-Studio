"""Build isolated G-base SQLite evidence through the actual semantic coordinator/workers.

The only input mutation is the documented missing equipment/003 name. The ten
independent load facts support a real, cancellable COUNT Cartesian query; no test
capability, sleep surrogate or fabricated successful job is used.
"""

import argparse
import asyncio
import json
import time
from pathlib import Path
from uuid import uuid4

from ontolearn_engine.coordinator import Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT, IMPLEMENTATION
from ontolearn_engine.semantic_samples import EX, ONTOLOGY, RISK, SHAPES
from ontolearn_engine.storage import digest
from ontolearn_engine.storage_probe import QUERY, fixture
from rdflib import Graph, URIRef, Variable

SLOW_QUERY = (
    "SELECT (COUNT(*) AS ?count) WHERE { "
    + " . ".join(f"?a{i} <urn:i05:load> ?x{i}" for i in range(9))
    + " }"
)
NETWORK_CANARY = "I05_REMOTE_CANARY_DO_NOT_LEAK"
FORBIDDEN_QUERY = (
    "SELECT ?s WHERE { SERVICE <http://127.0.0.1:9/" + NETWORK_CANARY + "> { ?s ?p ?o } }"
)


def uid():
    return str(uuid4())


def definition(layer, identity, value):
    return {"layer": layer, "id": identity, "value": value}


def request(project, capability, identity, *, derived=None):
    return {
        "projectId": project,
        "operationId": uid(),
        "capability": capability,
        "definitionId": identity,
        "scope": "asserted+derived" if derived else "asserted",
        "inputSelection": "current",
        "inputSnapshotId": None,
        "derivedResultId": derived,
    }


def start(coordinator, params):
    if coordinator.session is None:
        hello = coordinator.request(
            {
                "kind": "request",
                "protocolVersion": 2,
                "id": uid(),
                "engineSessionId": None,
                "method": "hello",
                "params": {"supportedVersions": [2], "clientId": uid()},
            }
        )
        if not hello["ok"]:
            raise RuntimeError("FIXTURE_HANDSHAKE_FAILED")
    response = coordinator.request(
        {
            "kind": "request",
            "protocolVersion": 2,
            "id": uid(),
            "engineSessionId": coordinator.session,
            "method": "semantic.start",
            "params": params,
        }
    )
    if not CONTRACT.validate("response", response) or not response["ok"]:
        raise RuntimeError("FIXTURE_ADMISSION_FAILED", response)
    return response["result"]


async def complete(coordinator, store, project, params):
    job = start(coordinator, params)
    deadline = time.monotonic() + 35
    while time.monotonic() < deadline:
        await coordinator.tick()
        await asyncio.sleep(0.01)
        job = store.get_job(project, job["jobId"])
        if job["state"] in {"succeeded", "failed", "cancelled"}:
            await asyncio.gather(*list(coordinator.tasks))
            if job["state"] != "succeeded":
                raise RuntimeError("FIXTURE_REAL_WORKER_FAILED", job)
            result_id = job["resultRef"]["resultId"]
            metadata, payload = store.semantic_result(project, result_id)
            rows = store.result(result_id)["payload"]
            return {
                "job": job,
                "metadata": metadata,
                "payload": payload,
                "rowsSha256": digest(rows),
            }
    raise RuntimeError("FIXTURE_REAL_WORKER_DEADLINE")


async def prepare(directory):
    directory.mkdir(parents=True, exist_ok=False)
    database = directory / "engine.sqlite"
    store = JobStore(database, contract=CONTRACT)
    coordinator = None
    try:
        internal = "i05-synthetic-native"
        store.create_project(internal)
        project = store.public_project(internal)
        original = Graph().parse(data=fixture(1), format="turtle")
        removed = (URIRef("urn:case:0:equipment/003"), EX.name, None)
        removed_triples = sorted([str(s), str(p), o.n3()] for s, p, o in original.triples(removed))
        original.remove(removed)
        facts = [
            {
                "id": digest([str(s), str(p), o.n3()]),
                "subject": str(s),
                "predicate": str(p),
                "object": o.n3(),
            }
            for s, p, o in sorted(original)
        ]
        for index in range(10):
            triple = [f"urn:i05:load:{index:04d}", "urn:i05:load", f'"{index:04d}"']
            facts.append(
                {
                    "id": digest(triple),
                    "subject": triple[0],
                    "predicate": triple[1],
                    "object": triple[2],
                }
            )
        ontology = Graph().parse(data=ONTOLOGY, format="turtle")

        def pattern(triple):
            return ["?" + str(term) if isinstance(term, Variable) else term.n3() for term in triple]

        definitions = [
            definition(
                "ontology",
                "G-base",
                {
                    "triples": [
                        {"subject": str(s), "predicate": str(p), "object": o.n3()}
                        for s, p, o in sorted(ontology)
                    ]
                },
            ),
            definition(
                "rule",
                RISK.id,
                {
                    "enabled": True,
                    "when": [pattern(t) for t in RISK.when],
                    "then": pattern(RISK.then),
                },
            ),
            definition("query", "Q01", {"text": QUERY}),
            definition("query", "slow-count", {"text": SLOW_QUERY}),
            definition("query", "forbidden-service", {"text": FORBIDDEN_QUERY}),
            definition("constraint", "V01", {"enabled": True, "turtle": SHAPES}),
        ]
        store.commit(internal, 0, uid(), uid(), manual=facts, definitions=definitions)
        snapshot = store.project_get(project)
        state_before = store.state(internal)
        coordinator = Coordinator(store, allowed_projects={project}, emit=lambda _: None)
        reasoning = await complete(
            coordinator, store, project, request(project, "reasoning.execute", "all")
        )
        derived = reasoning["metadata"]["resultId"]
        query = await complete(
            coordinator, store, project, request(project, "query.execute", "Q01", derived=derived)
        )
        validation = await complete(
            coordinator,
            store,
            project,
            request(project, "validation.execute", "V01", derived=derived),
        )
        assert query["payload"]["query"] == {
            "type": "SELECT",
            "variables": ["alarm"],
            "rows": [["<urn:case:0:alarm/A01>"]],
        }
        assert validation["payload"]["report"]["violations"] == [
            {
                "focus": "<urn:case:0:equipment/003>",
                "path": "<urn:ontolearn:name>",
                "constraint": "<http://www.w3.org/ns/shacl#MinCountConstraintComponent>",
                "sourceShape": "<urn:ontolearn:NameProperty>",
                "value": None,
                "severity": "<http://www.w3.org/ns/shacl#Violation>",
            }
        ]
        assert store.state(internal) == state_before
        completed = [reasoning, query, validation]
        trusted_fixture = {
            "projectId": project,
            "jobIds": [item["job"]["jobId"] for item in completed],
            "databasePath": str(database),
            "startRequests": [
                request(project, "query.execute", "slow-count"),
                request(project, "query.execute", "forbidden-service"),
            ],
        }
        metadata = {
            "implementation": IMPLEMENTATION,
            "project": snapshot,
            "originalGBaseFactCount": 18,
            "removedNameTriples": removed_triples,
            "gBaseFactCount": len(original),
            "independentLoadFactCount": 10,
            "assertedFactCount": len(facts),
            "ontologyTripleCount": len(ontology),
            "inputFactsSha256": digest(facts),
            "definitionsSha256": digest(definitions),
            "stateSha256": digest(state_before),
            "completed": completed,
            "networkCanary": NETWORK_CANARY,
            "queryText": QUERY,
            "slowQueryText": SLOW_QUERY,
            "slowCartesianCandidates": 10**9,
            "backgroundOperations": trusted_fixture["startRequests"],
        }
        target = directory / "fixture.json"
        target.write_text(json.dumps(trusted_fixture, ensure_ascii=False, indent=2) + "\n")
        (directory / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
        )
        print(target, flush=True)
    finally:
        if coordinator is not None:
            await coordinator.stop()
        store.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    asyncio.run(prepare(args.directory.resolve()))


if __name__ == "__main__":
    main()
