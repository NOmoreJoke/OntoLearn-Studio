"""Wave 4 evidence projected from Store records, with no renderer claims."""

import hashlib
import json
from urllib.parse import unquote

from ontolearn_engine.behavior import service as behavior
from ontolearn_engine.learning.baselines import read_json
from ontolearn_engine.learning.service import ToolEvidence
from ontolearn_engine.scenario import service as scenario
from ontolearn_engine.storage import digest
from ontolearn_engine.transfer import report as transfer_report
from ontolearn_engine.transfer.credential_scan import CredentialLeak, scan_projection

_SCAN_LIMIT = 200


def _details(store, project, prefix):
    rows = store._db.execute(
        """SELECT payload FROM job_details
           WHERE project=? AND id>=? AND id<? ORDER BY rowid DESC LIMIT ?""",
        (project, prefix, prefix + "\uffff", _SCAN_LIMIT),
    )
    return (json.loads(row["payload"]) for row in rows)


def _mapping(store, project, internal, root, snapshot_ref):
    state = store.state(internal)
    mapped = [fact for fact in state["facts"] if fact["owner"] == "equipment-csv"]
    definitions = [
        json.loads(item["payload"])
        for item in state["definitions"]
        if item["layer"] == "mapping" and item["id"] == "equipment-csv"
    ]
    if not mapped or len(definitions) != 1 or not isinstance(definitions[0], dict):
        return {}
    definition = definitions[0]
    fixture = read_json(root / "tests/fixtures/product-baselines/manifest.json")["files"]
    source_hash = definition.get("sourceHash")
    draft = definition.get("definition", {})
    file_name = (
        "equipment.csv"
        if source_hash == fixture.get("tests/fixtures/product-baselines/equipment.csv")
        else None
    )
    namespace = draft.get("namespace") if isinstance(draft, dict) else None
    triples, ownership, identities = [], [], set()
    for fact in mapped:
        try:
            row = json.loads(fact["source_row"])
        except (TypeError, ValueError):
            row = None
        if not isinstance(row, dict):
            row = {}
        is_managed = fact.get("managed_value") == fact["object"]
        key = (
            unquote(fact["subject"][len(namespace) :])
            if isinstance(namespace, str) and namespace and fact["subject"].startswith(namespace)
            else None
        )
        triple = {field: fact[field] for field in ("subject", "predicate", "object")}
        triples.append(triple)
        identities.add(key)
        ownership.append(
            {
                "triple": triple,
                "mappingId": fact["owner"],
                "sourceFile": file_name if is_managed and row.get("sheet") == "CSV" else None,
                "sourceRow": row.get("row"),
                "key": key,
            }
        )
    common = {
        "facts": triples,
        "ownership": ownership,
        "identities": list(identities),
    }
    evidence = {"M-01": (snapshot_ref, "succeeded", common)}
    definition_hash = digest(definition)
    revision = store.revision(internal)
    committed = [
        record
        for record in _details(store, project, "mapping-run:")
        if record.get("mappingRunVersion") == 1
        and record.get("mappingId") == "equipment-csv"
        and record.get("definitionHash") == definition_hash
    ]
    recent = next(
        (
            record
            for record in committed
            if record["revision"] == revision and record["afterSnapshotId"] == snapshot_ref
        ),
        None,
    )
    if recent is not None and any(
        record["revision"] + 1 == revision
        and record["afterSnapshotId"] == recent["beforeSnapshotId"]
        and record["resultId"] != recent["resultId"]
        for record in committed
    ):
        evidence["M-02"] = (
            recent["operationId"],
            "succeeded",
            {**common, "secondRunChanges": [] if recent["noChanges"] else None},
        )
    return evidence


def _behavior(store, project, internal, snapshot_ref):
    evidence = {}
    revision = store.revision(internal)
    for run_id in behavior.indexed_runs(store, project):
        run = behavior.load_run(store, project, run_id)
        if not run:
            continue
        for check_id in ("B-01", "B-02"):
            event_id = "E-" + check_id.replace("-", "")
            if check_id in evidence or event_id not in run.get("eventIds", ()):
                continue
            current = run["binding"]["inputSnapshotId"] == snapshot_ref and (
                run["binding"]["baseRevision"] == revision
            )
            # Stage 1 persists the planned Diff. Its candidate has no isolated
            # commit, committed facts, replay consumption or reasoning evidence.
            state = run["state"]
            status = "stale" if not current else state
            evidence[check_id] = (run_id, status, None)
    return evidence


def _scenario_rounds(run):
    rounds = []
    for entry in run["rounds"]:
        view, checkpoint = entry["round"], entry["checkpoint"]
        rounds.append(
            {
                "round": view["number"],
                "created": view["created"],
                "completed": view["resourceCompleted"],
                "backlog": view["backlog"],
                "backlogCount": view["metrics"]["backlog"],
                "completedCount": view["metrics"]["completed"],
                "unclosedHighAlarmCount": view["metrics"]["openHighAlerts"],
                "consumedEvents": checkpoint["consumed"],
            }
        )
    return rounds


def _same_round_projection(actual, expected):
    return len(actual) == len(expected) and all(
        all(wanted.get(field) == value for field, value in round_.items())
        for round_, wanted in zip(actual, expected, strict=True)
    )


def _scenario(store, project, internal, snapshot_ref, checks):
    by_capacity = {"3": [], "4": []}
    resumed = []
    revision = store.revision(internal)
    for run_id in scenario.indexed_run_ids(store, project):
        run = scenario.load_run(store, project, run_id)
        if not run or run["status"] != "succeeded":
            continue
        identity = run["identity"]
        if identity["projectVersion"] != revision or identity["inputSnapshotId"] != snapshot_ref:
            continue
        direct = str(run["evidence"]["capacity"].get("direct"))
        if direct not in by_capacity:
            continue
        if run.get("sourceRunId") is not None:
            if direct == "3":
                resumed.append(run)
        elif run["lastCommittedRound"] == 4:
            by_capacity[direct].append(run)
    evidence = {}
    cases = checks["G-list-01"]["expected"]
    if all(len(runs) >= 2 for runs in by_capacity.values()):
        actual = {
            key: [_scenario_rounds(run) for run in runs[:2]] for key, runs in by_capacity.items()
        }
        parity = all(
            _same_round_projection(rounds, cases["capacities"][key])
            for key, replays in actual.items()
            for rounds in replays
        )
        # Stage 1's zero-action behavior stage lacks the lesson's complete
        # facts, reasoning and trigger traces even when its queue matches.
        evidence["G-list-01"] = (
            by_capacity["3"][0]["runId"],
            "unavailable" if parity else "succeeded",
            None if parity else {"independentReplays": actual},
        )
    for run in resumed:
        source = scenario.load_run(store, project, run["sourceRunId"])
        if source is None or source["status"] not in ("cancelled", "failed"):
            continue
        checkpoints = [
            entry["checkpoint"]
            for entry in source["rounds"]
            if entry["round"]["checkpointRef"] == run["resumedFrom"]
        ]
        if len(checkpoints) != 1 or checkpoints[0]["round"] != 2:
            continue
        wanted = checks["G-list-06"]["expected"]["resumeFromRound2"]
        actual = _scenario_rounds(run)
        parity = checkpoints[0]["consumed"] == wanted["consumedBefore"] and (
            _same_round_projection(actual, wanted["newCommittedRounds"])
        )
        evidence["G-list-06"] = (
            run["runId"],
            "unavailable" if parity else "succeeded",
            None if parity else {"newCommittedRounds": actual},
        )
        break
    return evidence


def _verified_package(store, project, revision):
    exports = set()
    for record in _details(store, project, "transfer-export:"):
        result = record.get("result", {})
        publication = result.get("publication", {})
        if record.get("transferExportReceiptVersion") != 1 or result.get("kind") != "full":
            continue
        row = store._db.execute(
            "SELECT payload FROM job_details WHERE id=? AND project=?",
            (result["checkRef"], project),
        ).fetchone()
        if row is not None and json.loads(row[0]).get("baseRevision") == revision:
            exports.add(publication.get("sha256"))
    return any(
        receipt.get("transferImportReceiptVersion") == 1
        and receipt["result"]["kind"] == "full"
        and receipt["result"]["packageSha256"] in exports
        for receipt in _details(store, project, "transfer-import:")
    )


def _report(store, project, internal):
    revision = store.revision(internal)
    for receipt in _details(store, project, "transfer-report:"):
        result = receipt.get("result", {})
        if (
            receipt.get("transferReportReceiptVersion") != 1
            or result.get("baseRevision") != revision
        ):
            continue
        publication = result.get("publication", {})
        if publication.get("state") != "published":
            continue
        ref = result["reportRef"]
        recorded = store._db.execute(
            "SELECT payload FROM job_details WHERE id=? AND project=?",
            ("transfer-report-published:" + result["operationId"], project),
        ).fetchone()
        if recorded is None or json.loads(recorded[0]) != {
            "version": 1,
            "operationId": result["operationId"],
            "reportRef": ref,
            "sha256": publication.get("sha256"),
            "byteLength": publication.get("byteLength"),
        }:
            continue
        row = store._db.execute(
            "SELECT payload FROM job_details WHERE id=? AND project=?", (ref, project)
        ).fetchone()
        if row is None:
            continue
        prepared = json.loads(row[0])
        report = prepared.get("report", {})
        if (
            prepared.get("transferReportVersion") != 1
            or prepared.get("baseRevision") != revision
            or report.get("projectionVersion") != transfer_report.PROJECTION_VERSION
            or report.get("projectId") != project
        ):
            continue
        html = transfer_report.render_html(report)
        if hashlib.sha256(html.encode("utf-8")).hexdigest() != publication.get("sha256"):
            continue
        try:
            scan_projection(report)
            scan_projection({"html": html})
        except CredentialLeak:
            continue
        results = [
            result
            for section in (
                "queryResults",
                "validationResults",
                "behaviorResults",
                "scenarioComparisons",
            )
            for result in report[section]
        ]
        return {
            "learning-report": (
                ref,
                "succeeded",
                {
                    "exported": True,
                    "dataVersionIncluded": report["projectRevision"] == revision,
                    "staleStateIncluded": bool(results)
                    and all("status" in result and "statusNote" in result for result in results),
                    "assistanceIncluded": bool(report["learning"])
                    and all(
                        "hint" in item and "agentAssistance" in item for item in report["learning"]
                    ),
                    "credentialsIncluded": False,
                    "htmlSafe": "Content-Security-Policy" in html,
                    "projectPackageVerified": _verified_package(store, project, revision),
                },
            )
        }
    return {}


def persisted_evidences(
    store,
    project,
    internal,
    root,
    service,
    context,
    snapshot_ref,
    assistance,
):
    if context.task_id == "mapping":
        found = _mapping(store, project, internal, root, snapshot_ref)
    elif context.task_id == "behavior":
        found = _behavior(store, project, internal, snapshot_ref)
    elif context.task_id == "scenario":
        found = _scenario(store, project, internal, snapshot_ref, service.checks)
    else:
        found = _report(store, project, internal)
    evidences = {}
    for check_id in service.tasks[context.task_id]["checks"]:
        missing = (f"missing:{context.attempt_id}:{check_id}", "unavailable", None)
        reference, status, payload = found.get(check_id, missing)
        evidences[check_id] = ToolEvidence(
            reference, context, check_id, status, payload, assistance, "persisted-domain-tool"
        )
    return evidences
