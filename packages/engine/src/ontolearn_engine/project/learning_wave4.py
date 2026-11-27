"""Wave 4 evidence projected from Store records, with no renderer claims."""

import hashlib
import json
from urllib.parse import unquote

from ontolearn_engine.behavior import service as behavior
from ontolearn_engine.learning.baselines import read_json
from ontolearn_engine.learning.service import ToolEvidence, _normalise
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


def _behavior_evidence(store, project, replay, event_id):
    prior_id = replay["isolated"].get("eventOrigins", {}).get(event_id)
    if not prior_id or replay["eventTrace"] != [
        {"event_id": event_id, "reason": "duplicate_event"}
    ]:
        return None
    first = behavior.load_run(store, project, prior_id)
    if (
        first is None
        or first.get("committed") is not True
        or first["state"] != "completed"
        or first["eventTrace"] != [{"event_id": event_id, "reason": "event_applied"}]
        or behavior._scope_prefix(first["binding"]) != behavior._scope_prefix(replay["binding"])
        or first["draft"] != replay["draft"]
    ):
        return None
    for run in (first, replay):
        saved = behavior.scope_commit(store, project, run)
        if (
            saved is None
            or saved["isolated"] != run["isolated"]
            or saved["binding"] != run["binding"]
        ):
            return None
    original, repeated = first["isolated"], replay["isolated"]
    if (
        replay["diff"] != {"added": [], "removed": []}
        or repeated["actionTrace"]
        or any(action["effect"] != "unchanged" for action in replay["actions"])
        or any(
            original[key] != repeated[key]
            for key in (
                "assertedFacts",
                "facts",
                "objects",
                "orders",
                "notifications",
                "consumption",
                "eventOrigins",
                "consumedEvents",
                "triggeredInstances",
                "executedActions",
            )
        )
    ):
        return None
    if set(map(digest, original["assertedFacts"] + original["behaviorBeforeInference"])) != set(
        map(digest, original["facts"])
    ):
        return None
    return first


def _risk_condition_used(first):
    if len(first["conditions"]) != 1:
        return False
    decision = first["conditions"][0]
    if decision["triggered"] is not True:
        return False
    class_id = "urn:ontolearn:learning:HighRiskEquipment"
    for entry in decision["conditions"]:
        condition = first["draft"]["conditions"][entry["index"]]
        if (
            entry["satisfied"] is True
            and condition.get("subject") == {"kind": "eventField", "field": "equipmentId"}
            and (
                (condition["op"] == "type" and condition["classId"] == class_id)
                or (
                    condition.get("property") == behavior.RDF_TYPE
                    and condition["value"]
                    == {"kind": "value", "value": {"kind": "iri", "value": class_id}}
                )
            )
        ):
            return True
    return False


def _alarm_not_high(first):
    """Derive the course reason from the actual failed condition and event facts."""
    if len(first["conditions"]) != 1:
        return []
    decision = first["conditions"][0]
    if decision["reason"] != "condition_not_satisfied":
        return []
    level = "urn:ontolearn:learning:level"
    event = first["events"][0]
    for entry in decision["conditions"]:
        condition = first["draft"]["conditions"][entry["index"]]
        if (
            entry["satisfied"] is False
            and condition.get("property") == level
            and condition.get("subject") == {"kind": "eventField", "field": "alarmId"}
            and condition["value"]
            == {"kind": "value", "value": {"kind": "string", "value": "High"}}
            and {
                "subject": event["payload"].get("alarmId"),
                "predicate": level,
                "object": '"Low"',
            }
            in first["isolated"]["assertedFacts"]
        ):
            return [
                {
                    "eventId": decision["eventId"],
                    "behaviorId": decision["behaviorId"],
                    "reason": "alarm-not-high",
                },
            ]
    return []


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
            binding = run["binding"]
            if binding["inputSnapshotId"] != snapshot_ref or binding["baseRevision"] != revision:
                continue
            if run["state"] != "completed" or run.get("committed") is not True:
                evidence[check_id] = (run_id, run["state"], None)
                continue
            first = _behavior_evidence(store, project, run, event_id)
            if first is None or (check_id == "B-01" and not _risk_condition_used(first)):
                evidence[check_id] = (run_id, "succeeded", None)
                continue
            actual = first["isolated"]
            payload = {
                "committed": first["committed"],
                "facts": actual["assertedFacts"],
                **{
                    key: actual[key]
                    for key in (
                        "orders",
                        "notifications",
                        "actionTrace",
                        "consumedEvents",
                        "triggeredInstances",
                    )
                },
            }
            if check_id == "B-01":
                payload["behaviorBeforeInference"] = actual["behaviorBeforeInference"]
                payload["repeatChanges"] = run["diff"]["added"] + run["diff"]["removed"]
            else:
                payload["notTriggered"] = _alarm_not_high(first)
            evidence[check_id] = (run_id, "succeeded", payload)
    return evidence


def _scenario_rounds(run):
    rounds = []
    for entry in run["rounds"]:
        actual = entry.get("evidence", {})
        view, checkpoint = entry["round"], entry["checkpoint"]
        if (
            "duplicateOrders" not in actual
            or actual["duplicateOrders"] != []
            or actual.get("actionTrace") != view["behaviorTrace"]
        ):
            return []
        rounds.append(
            {
                **{key: value for key, value in actual.items() if key != "duplicateOrders"},
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


def _same_rounds(actual, expected):
    return _normalise(actual) == _normalise(expected)


def _scenario(store, project, internal, snapshot_ref, checks):
    by_capacity = {"3": [], "4": []}
    first_seen = {}
    resumed = []
    revision = store.revision(internal)
    cases = checks["G-list-01"]["expected"]
    for run_id in scenario.indexed_run_ids(store, project):
        run = scenario.load_run(store, project, run_id)
        if not run or run["status"] != "succeeded":
            continue
        identity = run["identity"]
        if identity["projectVersion"] != revision or identity["inputSnapshotId"] != snapshot_ref:
            continue
        capacity = str(run["evidence"]["capacity"].get("direct"))
        if capacity not in by_capacity:
            continue
        if run.get("sourceRunId") is not None:
            if capacity == "3":
                resumed.append(run)
        elif run["lastCommittedRound"] == 4:
            first_seen.setdefault(capacity, run_id)
            rounds = _scenario_rounds(run)
            if len(by_capacity[capacity]) < 2 and _same_rounds(
                rounds, cases["capacities"][capacity]
            ):
                by_capacity[capacity].append((run_id, rounds))
    evidence = {}
    capacity_3 = [rounds for _, rounds in by_capacity["3"]]
    if all(len(runs) == 2 for runs in by_capacity.values()):
        evidence["G-list-01"] = (
            by_capacity["3"][0][0],
            "succeeded",
            {
                "capacities": {key: runs[0][1] for key, runs in by_capacity.items()},
                "independentReplays": {
                    key: [rounds for _, rounds in runs] for key, runs in by_capacity.items()
                },
            },
        )
    elif "3" in first_seen and "4" in first_seen:
        evidence["G-list-01"] = (first_seen["3"], "succeeded", None)
    wanted = checks["G-list-06"]["expected"]["resumeFromRound2"]
    for run in resumed:
        evidence["G-list-06"] = (run["runId"], "succeeded", None)
        source = scenario.load_run(store, project, run["sourceRunId"])
        if source is None or source["status"] not in ("cancelled", "failed"):
            continue
        source_prefix = [entry for entry in source["rounds"] if entry["round"]["number"] <= 2]
        if (
            len(source_prefix) != 2
            or source_prefix[-1]["round"]["checkpointRef"] != run["resumedFrom"]
            or not _same_rounds(
                _scenario_rounds({"rounds": source_prefix}), cases["capacities"]["3"][:2]
            )
        ):
            continue
        consumed = source_prefix[-1]["checkpoint"]["consumed"]
        actual = _scenario_rounds(run)
        if consumed == wanted["consumedBefore"] and _same_rounds(
            actual, wanted["newCommittedRounds"]
        ):
            evidence["G-list-06"] = (
                run["runId"],
                "succeeded",
                {
                    "independentReplays": capacity_3,
                    "resumeFromRound2": {
                        "consumedBefore": consumed,
                        "newCommittedRounds": actual,
                        "duplicateOrders": [
                            order
                            for entry in run["rounds"]
                            for order in entry["evidence"]["duplicateOrders"]
                        ],
                    },
                },
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
