"""W5 Stage 1-A: read-only T10 package to t11-comparison-v3 projection.

Drives the real ``Coordinator`` + ``JobStore`` (facts, definitions, mapping
ownership/managed values, learning ledger rows, operation history), exports
real ``.ontolearn.zip`` archives through the real ``TransferService``, then
exercises ``scripts/release/project-t10-comparison.py``:

* deterministic idempotence - the same ZIP projects to byte-identical JSON;
* unselected/never-carried optional layers stay strictly empty;
* template packages honestly refuse restoration (``restoreCurrent is False``);
* ``g6-conflict`` stays unreachable because v1 never carries queries/results;
* tampered packages fail closed with a fixed reason.

The projector runs in-process (loaded by path exactly like the W4 packaged
runner loads its helper), so no shell boundary is involved. The single child
process is the cross-language leg: a constant ``--eval`` driver where Node
enforces its own 24.3+ runtime gate and every path travels through the
environment, never through the argument vector. Runtimes outside the gate
skip that leg explicitly instead of failing.
"""

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
from pathlib import Path
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import digest

REPO_ROOT = Path(__file__).resolve().parents[3]
PROJECTOR = REPO_ROOT / "scripts" / "release" / "project-t10-comparison.py"
VERIFY_MTS = REPO_ROOT / "scripts" / "release" / "verify.mts"
OPTIONS_OFF = {"agentSessions": False, "rawSources": False, "derived": False, "history": False}
SCHEMA_OK_MARKER = "comparison-schema-ok"
# Constant driver source: Node re-checks the frozen 24.3+ gate itself and
# reads both file locations from the environment, never from argv.
NODE_DRIVER_SOURCE = """
const [major, minor] = process.versions.node.split('.').map(Number)
if (major !== 24 || !Number.isInteger(minor) || minor < 3) {
  console.error('UNSUPPORTED_NODE_RUNTIME')
  process.exit(3)
}
const { readFileSync } = await import('node:fs')
const { comparisonSchema } = await import(process.env.W5_VERIFY_MTS)
comparisonSchema.parse(JSON.parse(readFileSync(process.env.W5_PROJECTION_FILE, 'utf8')))
console.log('comparison-schema-ok')
"""


def uid():
    return str(uuid4())


def run_projector(package, output, case="current-state", argv=None):
    """Load the projector module by path and run main() in-process."""
    spec = importlib.util.spec_from_file_location("w5_project_t10_comparison", PROJECTOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    buffer = io.StringIO()
    arguments = (
        argv
        if argv is not None
        else [
            "--package",
            str(package),
            "--case",
            case,
            "--output",
            str(output),
        ]
    )
    try:
        with contextlib.redirect_stderr(buffer):
            code = module.main(arguments)
    except SystemExit as exit_error:  # argparse usage failures exit 2
        code = exit_error.code
    return code, buffer.getvalue()


def assert_node_schema_accepts(projection_path):
    if shutil.which("node") is None:
        pytest.skip("comparisonSchema cross-language validation needs a node runtime on PATH")
    environment = dict(os.environ)
    environment["W5_PROJECTION_FILE"] = str(projection_path)
    environment["W5_VERIFY_MTS"] = VERIFY_MTS.as_uri()
    result = subprocess.run(
        ["node", "--input-type=module", "--eval", NODE_DRIVER_SOURCE],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
        shell=False,
        check=False,
    )
    if result.returncode == 3 and "UNSUPPORTED_NODE_RUNTIME" in result.stderr:
        pytest.skip(
            f"comparisonSchema cross-language validation needs Node 24.3+ ({result.stderr.strip()})"
        )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == SCHEMA_OK_MARKER


def frame(actor, method, params):
    return {
        "kind": "request",
        "id": uid(),
        "protocolVersion": 2 if method == "hello" else 3,
        "engineSessionId": None if method == "hello" else actor.session,
        "method": method,
        "params": params,
    }


def exchange(actor, method, params):
    request = frame(actor, method, params)
    response = actor.request(request)
    actor.finish_query_reply(request["id"], emitted=True)
    return response


def ok(response):
    assert response["ok"], response
    return response["result"]


@pytest.fixture
def owned(tmp_path):
    store = JobStore(tmp_path / "w5.sqlite", contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
    yield actor, store
    actor.mainline.close()
    store.close()


def open_blank(actor, name="投影项目"):
    created = ok(
        exchange(
            actor,
            "project.create",
            {
                "requestVersion": 1,
                "operationId": uid(),
                "name": name,
                "initialization": {"kind": "blank"},
            },
        )
    )
    project = created["projectId"]
    ok(exchange(actor, "project.open", {"projectId": project}))
    return project


def stage_outbound(actor, project, purpose, extension, output_file):
    root = actor.store.path.parent / ".ontolearn-host-selections"
    selection = uid()
    target = root / selection
    target.mkdir(parents=True)
    os.chmod(target, 0o700)
    (target / "meta.json").write_text(
        json.dumps(
            {
                "version": 1,
                "selectionId": selection,
                "projectId": project,
                "engineSessionId": actor.session,
                "purpose": purpose,
                "extension": extension,
                "outputFile": output_file,
                "createdAt": "2026-11-21T00:00:00Z",
            }
        )
    )
    return selection


def commit_manual(actor, store, project, facts, definitions=None, base=None):
    host = {"host_client_id": actor.host_client_id, "engine_session_id": actor.session}
    limits = {
        "startupMs": 10000,
        "handshakeMs": 5000,
        "requestMs": 5000,
        "heartbeatMs": 10000,
        "cancelGraceMs": 5000,
        "totalMs": 120000,
        "maxFrameBytes": 262144,
        "maxQueuedJobs": 32,
        "maxConcurrentJobs": 2,
        "maxPageItems": 100,
        "maxPageBytes": 131072,
        "maxWorkerMemoryBytes": 536870912,
    }
    if base is None:
        base = store.revision(store._project(project))
    plan = {"manual": facts}
    if definitions:
        plan["definitions"] = definitions
    ready = store.preview_changeset(
        project,
        base,
        {"projectId": project, "baseRevision": base, "intent": "change", "plan": plan},
        limits=limits,
        **host,
    )
    assert ready["status"] == "ready", ready
    token = None
    while True:
        page = store.changeset_diff_page(
            project,
            ready["previewHash"],
            ready["manifest"]["documentKind"],
            200,
            token,
            limits=limits,
            **host,
        )
        token = page["nextCursor"]
        if page["complete"]:
            break
    confirmed = store.confirm_changeset(project, ready["previewHash"], token, **host)
    job = store.create_changeset_job(
        project,
        uid(),
        {
            "inputSnapshotId": confirmed["inputSnapshotId"],
            "scope": "asserted",
            "definitionId": "changeset",
            "parametersHash": confirmed["parametersHash"],
            "derivedResultIds": [],
            "preparedPlanRef": confirmed["preparedPlanRef"],
        },
        confirmed["confirmationRef"],
        {
            "engineVersion": "0.1.0",
            "executionSemanticsVersion": "changeset-v1",
            "dependencyLockHash": "a" * 64,
        },
        limits,
        **host,
    )
    store.start_job(job["jobId"])
    done = store.commit_job(job["jobId"])
    assert done["state"] == "succeeded", done


def populated_project(actor, store):
    """Ontology + manual facts + a mapping-owned fact set + a learning row."""
    project = open_blank(actor, name="投影完整项目")
    commit_manual(
        actor,
        store,
        project,
        [
            {
                "id": digest(["urn:x:equipment/001", "urn:x:name", '"泵站A"']),
                "subject": "urn:x:equipment/001",
                "predicate": "urn:x:name",
                "object": '"泵站A"',
            },
            {
                "id": digest(["urn:x:equipment/002", "urn:x:name", '"泵站B"']),
                "subject": "urn:x:equipment/002",
                "predicate": "urn:x:name",
                "object": '"泵站B"',
            },
        ],
        definitions=[
            {
                "layer": "ontology",
                "id": "G",
                "value": {
                    "triples": [
                        {
                            "subject": "urn:x:Equipment",
                            "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                            "object": "<http://www.w3.org/2002/07/owl#Class>",
                        }
                    ],
                    "singleValuedPredicates": [],
                    "references": [],
                },
            }
        ],
        base=0,
    )
    from ontolearn_engine.mapping import plan as mapping_plan
    from ontolearn_engine.mapping.source import parse_csv

    table = parse_csv(b"equipment_id,equipment_name\n003,C\n")
    mapping = mapping_plan.Mapping(
        identity="equip-map",
        version=1,
        namespace="urn:x:equipment/",
        class_iri="urn:x:Equipment",
        keys=("equipment_id",),
        bindings=(mapping_plan.Binding("equipment_name", "urn:x:name"),),
    )
    preview = mapping_plan.preview(
        mapping,
        table,
        {
            "project": store._project(project),
            "projectRevision": store.revision(store._project(project)),
            "state": store.state(store._project(project)),
        },
    )
    assert preview.ready, preview.issues
    internal = store._project(project)
    store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        mapping={"id": "equip-map", "rows": preview.rows()},
        definitions=[
            {
                "layer": "mapping",
                "id": "equip-map",
                "value": {
                    "version": 1,
                    "definition": {
                        "identity": "equip-map",
                        "version": 1,
                        "namespace": "urn:x:equipment/",
                        "class_iri": "urn:x:Equipment",
                        "keys": ["equipment_id"],
                        "bindings": [
                            {
                                "column": "equipment_name",
                                "predicate": "urn:x:name",
                                "conversion": {
                                    "kind": "string",
                                    "trim": False,
                                    "empty": "omit",
                                    "true_values": ("true", "1"),
                                    "false_values": ("false", "0"),
                                },
                                "reference_namespace": None,
                                "reference_columns": [],
                            }
                        ],
                    },
                    "sourceHash": preview.source_hash,
                    "sheet": "CSV",
                },
            }
        ],
    )
    attempt = uid()
    payload = {
        "taskId": "transfer-repair",
        "operationComplete": True,
        "maxHintLevel": 0,
        "assistance": "independent",
        "checkStatus": "passed",
        "evidenceIds": ["ev-1"],
        "lastFeedback": None,
        "completedGuidedStages": [],
    }
    change = {
        "type": "learning.record",
        "attempt": attempt,
        "course": "检修",
        "task": "transfer-repair",
        "expectedRecordVersion": None,
        "payload": payload,
        "assistanceEvent": None,
    }
    writer = uid()
    prepared = store.prepare_application(project, change, actor=writer, permission="write")
    store.apply_application(
        project,
        uid(),
        change,
        actor=writer,
        permission="write",
        prepared_plan_ref=prepared["preparedPlanRef"],
        confirmation_ref=prepared["confirmationRef"],
    )
    return project, attempt


def build_exported_package(actor, project, kind="full", options=None):
    selection = stage_outbound(
        actor, project, "package-export", ".ontolearn.zip", "output.ontolearn.zip"
    )
    revision = actor.store.revision(actor.store._project(project))
    check = ok(
        exchange(
            actor,
            "project.transfer.package.export.check",
            {
                "projectId": project,
                "selectionId": selection,
                "kind": kind,
                "baseRevision": revision,
                "options": options or OPTIONS_OFF,
            },
        )
    )
    ok(
        exchange(
            actor,
            "project.transfer.package.export",
            {
                "projectId": project,
                "selectionId": selection,
                "checkRef": check["checkRef"],
                "operationId": uid(),
            },
        )
    )
    return (
        actor.store.path.parent / ".ontolearn-host-selections" / selection / "output.ontolearn.zip"
    ).read_bytes()


def test_full_package_projection_is_deterministic_and_honest(owned, tmp_path):
    actor, store = owned
    project, attempt = populated_project(actor, store)
    archive_bytes = build_exported_package(
        actor, project, "full", {**OPTIONS_OFF, "agentSessions": True, "history": True}
    )
    package = tmp_path / "full.ontolearn.zip"
    package.write_bytes(archive_bytes)
    first = tmp_path / "p1.json"
    second = tmp_path / "p2.json"
    code_one, stderr_one = run_projector(package, first)
    code_two, _stderr_two = run_projector(package, second)
    assert code_one == 0, stderr_one
    assert code_two == 0
    assert stderr_one == ""
    assert first.read_bytes() == second.read_bytes()
    projection = json.loads(first.read_text(encoding="utf-8"))
    assert projection["format"] == "t11-comparison-v3"
    assert projection["comparisonCase"] == "current-state"
    assert projection["sourceSnapshotId"] == hashlib.sha256(archive_bytes).hexdigest()
    assert projection["selection"] == {
        "currentDerived": False,
        "historicalRuns": True,
        "rawSources": False,
        "agentSessions": True,
        "priorUndo": False,
    }
    assert projection["capabilities"] == {
        "restoreCurrent": True,
        "rerunOriginalMapping": False,
        "replaySandbox": False,
    }
    assert projection["dependencies"] == {
        "mappingSources": "missing",
        "replayInputs": False,
        "replayConfiguration": False,
        "replaySemantics": "missing",
    }
    for layer in ("facts", "definitions", "ownership", "mappingState", "history", "agentSessions"):
        assert projection[layer], layer
    # Layers the v1 format never carries stay honestly empty even though the
    # live project has real query results and scenario rounds in its Store.
    for layer in ("queries", "results", "derivedResults", "rounds", "rawSources", "undo"):
        assert projection[layer] == [], layer
    assert [row["id"] for row in projection["agentSessions"]] == [attempt]
    assert {row["payload"]["mapping"] for row in projection["mappingState"]} == {"equip-map"}
    managed = [row for row in projection["ownership"] if row["payload"]["owner"] == "equip-map"]
    assert managed and managed[0]["payload"]["managedValue"] == '"C"'
    facts = {row["payload"]["subject"]: row["payload"]["object"] for row in projection["facts"]}
    assert facts["urn:x:equipment/001"] == '"泵站A"'
    assert_node_schema_accepts(first)


def test_minimal_full_package_keeps_unselected_layers_empty(owned, tmp_path):
    actor, store = owned
    project, _attempt = populated_project(actor, store)
    package = tmp_path / "minimal.ontolearn.zip"
    package.write_bytes(build_exported_package(actor, project, "full", OPTIONS_OFF))
    output = tmp_path / "minimal.json"
    code, stderr = run_projector(package, output)
    assert code == 0, stderr
    projection = json.loads(output.read_text(encoding="utf-8"))
    assert projection["selection"]["historicalRuns"] is False
    assert projection["selection"]["agentSessions"] is False
    assert projection["history"] == []
    assert projection["agentSessions"] == []
    assert projection["capabilities"]["restoreCurrent"] is True
    assert projection["capabilities"]["rerunOriginalMapping"] is False
    assert projection["capabilities"]["replaySandbox"] is False
    assert projection["dependencies"]["mappingSources"] == "missing"
    assert projection["dependencies"]["replaySemantics"] == "missing"
    assert projection["facts"] and projection["ownership"]
    assert_node_schema_accepts(output)


def test_template_package_is_not_restorable(owned, tmp_path):
    actor, store = owned
    project, _attempt = populated_project(actor, store)
    package = tmp_path / "template.ontolearn.zip"
    package.write_bytes(build_exported_package(actor, project, "template"))
    output = tmp_path / "template.json"
    code, stderr = run_projector(package, output)
    assert code == 1
    assert stderr.strip() == "TEMPLATE_NOT_RESTORABLE"
    projection = json.loads(output.read_text(encoding="utf-8"))
    assert projection["capabilities"]["restoreCurrent"] is False
    assert projection["facts"] == []
    assert projection["ownership"] == []
    assert projection["definitions"]  # template definitions-only payload is still carried


def test_g6_conflict_case_is_refused_for_v1_packages(owned, tmp_path):
    actor, store = owned
    project, _attempt = populated_project(actor, store)
    package = tmp_path / "g6.ontolearn.zip"
    package.write_bytes(build_exported_package(actor, project, "full"))
    output = tmp_path / "g6.json"
    code, stderr = run_projector(package, output, case="g6-conflict")
    assert code == 1
    assert stderr.strip() == "G6_REQUIRED_LAYER"
    projection = json.loads(output.read_text(encoding="utf-8"))
    # v1 never carries queries/results, so the six-layer conflict shape is unreachable.
    assert projection["queries"] == [] and projection["results"] == []


def test_tampered_package_is_rejected_without_output(owned, tmp_path):
    actor, store = owned
    project, _attempt = populated_project(actor, store)
    archive_bytes = bytearray(build_exported_package(actor, project, "full"))
    index = archive_bytes.find(b'{"facts"')
    assert index != -1
    archive_bytes[index] ^= 1
    package = tmp_path / "broken.ontolearn.zip"
    package.write_bytes(bytes(archive_bytes))
    output = tmp_path / "broken.json"
    code, stderr = run_projector(package, output)
    assert code == 2
    assert stderr.strip() in {
        "HASH_MISMATCH",
        "SIZE_MISMATCH",
        "MANIFEST_SHAPE",
        "PACKAGE_SHAPE",
        "ARCHIVE_INVALID",
    }
    assert not output.exists()


def test_projector_requires_arguments():
    code, stderr = run_projector(None, None, argv=[])
    assert code == 2
    assert "usage:" in stderr.lower()
