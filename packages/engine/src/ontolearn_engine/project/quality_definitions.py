"""Quality workspace reads and preparation; never a save or execution issuer.

``project.quality.prepare`` freezes the inputs for the FR-500..503
"检查我的项目" chain (reasoning.execute, then validation.execute) without
creating or running any job. ``project.quality.read`` projects the current
persisted quality state — FR-504/505 definitions, three-tier findings with
click-to-locate targets (FR-503), rule and RDFS derivation provenance
(FR-502) and invalidation reasons (FR-006) — strictly from immutable results
and stored definitions. Nothing here re-executes rules or shapes.
"""

import json

from ontolearn_engine.job_store import fault, payload_from_rows

METHODS = frozenset({"project.quality.read", "project.quality.prepare"})

# Fixed statement text (compile-time folded literals) with one bound `?`
# parameter; no caller text is ever interpolated into the query.
_LATEST_RESULTS_SQL = (
    "SELECT jr.id, r.kind, jr.created FROM job_results jr"
    " JOIN results r ON r.id=jr.id"
    " WHERE r.project=? ORDER BY jr.created DESC, jr.id"
)

_SEVERITY_TIERS = {
    "<http://www.w3.org/ns/shacl#Violation>": "violation",
    "<http://www.w3.org/ns/shacl#Warning>": "warning",
    "<http://www.w3.org/ns/shacl#Info>": "info",
}


def _formal_definitions(state, layer):
    out = []
    for record in state["definitions"]:
        if record["layer"] != layer:
            continue
        try:
            payload = json.loads(record["payload"])
        except ValueError:
            fault("INVALID_STATE")
        if not isinstance(payload, dict):
            fault("INVALID_STATE")
        out.append((record["id"], payload))
    return out


def _rule_summary(identity, payload):
    if payload.get("kind") == "rule":
        return {
            "id": identity,
            "format": "fr505",
            "label": payload.get("label"),
            "enabled": bool(payload.get("enabled")),
            "conditions": payload.get("conditions", []),
            "conclusions": payload.get("conclusions", []),
        }
    return {
        "id": identity,
        "format": "legacy",
        "enabled": bool(payload.get("enabled")),
        "when": payload.get("when", []),
        "then": payload.get("then"),
    }


def _constraint_summary(identity, payload):
    if payload.get("kind") == "constraint":
        return {
            "id": identity,
            "format": "fr504",
            "label": payload.get("label"),
            "enabled": bool(payload.get("enabled")),
            "targetClass": payload.get("targetClass"),
            "path": payload.get("path"),
            "template": payload.get("template"),
            "parameters": payload.get("parameters", {}),
        }
    return {
        "id": identity,
        "format": "turtle",
        "enabled": bool(payload.get("enabled")),
        "turtle": payload.get("turtle"),
    }


def _latest_results(store, internal):
    """Latest persisted reasoning/validation results, newest first, immutable.

    Only the bound internal project identifier reaches the statement; the two
    fixed kind names are filtered in Python from the same ordered rows.
    """
    rows = store._db.execute(_LATEST_RESULTS_SQL, (internal,)).fetchall()
    return [row for row in rows if row["kind"] in ("reasoning", "validation")]


def _finding(row):
    """One FR-503 finding with click-to-locate targets and its tier."""
    return {
        "tier": _SEVERITY_TIERS.get(row.get("severity"), "violation"),
        "focusNode": row.get("focus"),
        "path": row.get("path"),
        "constraint": row.get("constraint"),
        "sourceShape": row.get("sourceShape"),
        "value": row.get("value"),
        "targets": {
            "subject": row.get("focus"),
            "predicate": row.get("path"),
            "object": row.get("value"),
        },
    }


def _plain_triple(triple):
    """Project one N3 key row to the read contract's plain subject/predicate."""
    if not isinstance(triple, list) or len(triple) != 3:
        return triple

    def plain(term):
        return (
            term[1:-1] if isinstance(term, str) and term[:1] == "<" and term[-1:] == ">" else term
        )

    return [plain(triple[0]), plain(triple[1]), triple[2]]


def _derivation(payload):
    """FR-502 provenance: rule outputs with their supporting inputs."""
    reasoning = payload.get("reasoning") if isinstance(payload, dict) else None
    if not isinstance(reasoning, dict):
        return None
    evidence = [
        {
            "rule": item.get("rule"),
            "output": _plain_triple(item.get("result", []))
            if isinstance(item.get("result"), list)
            else item.get("result"),
            "inputs": [
                _plain_triple(triple)
                for triple in item.get("inputs", [])
                if isinstance(triple, list)
            ],
        }
        for item in reasoning.get("evidence", [])
        if isinstance(item, dict)
    ]
    rdfs = [
        {
            "output": _plain_triple(item.get("result")),
            "basis": [
                _plain_triple(triple)
                for triple in item.get("basis", [])
                if isinstance(triple, list)
            ],
        }
        for item in reasoning.get("rdfsEvidence", [])
        if isinstance(item, dict)
    ]
    return {
        "executionSemanticsVersion": reasoning.get("semanticsVersion"),
        "rules": [
            _plain_triple(triple)
            for triple in reasoning.get("rules", [])
            if isinstance(triple, list)
        ],
        "rdfs": [
            _plain_triple(triple)
            for triple in reasoning.get("rdfs", [])
            if isinstance(triple, list)
        ],
        "ruleTraces": evidence,
        "rdfsTraces": rdfs,
        "warnings": reasoning.get("warnings", []),
    }


def _quality_state(store, project):
    internal = store._project(project)
    state = store.state(internal)
    rules = [_rule_summary(i, p) for i, p in _formal_definitions(state, "rule")]
    constraints = [_constraint_summary(i, p) for i, p in _formal_definitions(state, "constraint")]
    reasoning_view = None
    # "检查我的项目" runs one validation per enabled constraint; collect the
    # newest available result per definitionId at the latest validation
    # snapshot and aggregate their findings into the single read view.
    validation_snapshot = None
    newest_validation = None
    validation_views = {}
    for row in _latest_results(store, internal):
        try:
            dto = store.result_get(project, row["id"])
        except Exception:
            continue
        if dto["payloadStatus"] != "available":
            continue
        view = {
            "resultId": row["id"],
            "jobId": dto["jobId"],
            "state": dto["state"],
            # Named staleReasons (plural): the singular key is reserved by the
            # shared contract semantic walker for full result DTOs.
            "staleReasons": dto["staleReason"],
            "inputSnapshotId": dto["inputSnapshotId"],
            "scope": dto["scope"],
            "definitionId": dto["definitionId"],
        }
        if dto["kind"] == "reasoning":
            if reasoning_view is None:
                payload = payload_from_rows(store.result(row["id"])["payload"])
                derivation = _derivation(payload)
                if derivation is not None:
                    view["derivation"] = derivation
                reasoning_view = view
        elif dto["kind"] == "validation":
            if validation_snapshot is None:
                validation_snapshot = dto["inputSnapshotId"]
            if dto["inputSnapshotId"] != validation_snapshot:
                continue
            if dto["definitionId"] in validation_views:
                continue
            payload = payload_from_rows(store.result(row["id"])["payload"])
            report = payload.get("report") if isinstance(payload, dict) else None
            findings = (
                [_finding(item) for item in report.get("violations", [])]
                if isinstance(report, dict)
                else []
            )
            view["conforms"] = bool(report.get("conforms")) if isinstance(report, dict) else None
            view["findings"] = findings
            validation_views[dto["definitionId"]] = view
            if newest_validation is None:
                newest_validation = view
    validation_view = None
    if newest_validation is not None:
        ordered = [validation_views[key] for key in sorted(validation_views)]
        conforms = (
            all(view["conforms"] for view in ordered)
            if all(view["conforms"] is not None for view in ordered)
            else None
        )
        validation_view = {
            **newest_validation,
            "conforms": conforms,
            "findings": [finding for view in ordered for finding in view["findings"]],
        }
    return {
        "qualityReadVersion": 1,
        "projectId": project,
        "rules": rules,
        "constraints": constraints,
        "reasoning": reasoning_view,
        "validation": validation_view,
    }


def read(store, params, ticket):
    ticket.check(store)
    store._valid("params_project.quality.read", params)
    if params["projectId"] != ticket.project:
        fault("PERMISSION_DENIED")
    with store._read():
        result = _quality_state(store, params["projectId"])
    if not store.contract.validate("result_project.quality.read", result):
        fault("INVALID_STATE")
    return ticket.deliver(result)


def _job_input(store, project, snapshot_id, scope, definition_id, parameters):
    return {
        "inputSnapshotId": snapshot_id,
        "scope": scope,
        "definitionId": definition_id,
        "parametersHash": store.put_blob(project, parameters),
        "derivedResultIds": [],
        "preparedPlanRef": None,
    }


def prepare(store, params, ticket):
    """Freeze the FR-500 chain inputs; no job is created here.

    One prepared validation JobInput is returned per enabled constraint (FR-504
    template or legacy Turtle). A project with zero enabled constraints still
    prepares cleanly: ``validationInput`` is null and ``validationInputs`` is
    empty. An explicit ``constraintId`` filters to that one constraint and
    faults only when it is missing or disabled. ``derivedResultIds`` stays
    empty here; the caller fills it after ``reasoning.execute`` completes when
    ``validationScope`` is ``asserted+derived``.
    """
    from ontolearn_engine.resources import LIMITS, REGISTRY_HASH, semantic_identity

    ticket.check(store)
    store._valid("params_project.quality.prepare", params)
    project = params["projectId"]
    if project != ticket.project:
        fault("PERMISSION_DENIED")
    selection = params["selection"]
    validation_scope = params.get("validationScope", "asserted+derived")
    constraint_filter = params.get("constraintId")
    internal = store._project(project)
    with store._transaction():
        snapshot_id = store.snapshot(internal)
        if selection["kind"] == "historical":
            snapshot_id = selection["snapshotId"]
            store._project_snapshot(snapshot_id, internal)
        state = store.state(internal)
        enabled = [
            identity
            for identity, payload in _formal_definitions(state, "constraint")
            if payload.get("enabled")
            and (constraint_filter is None or identity == constraint_filter)
        ]
        if constraint_filter is not None and not enabled:
            fault("INVALID_REQUEST", field="dependency")
        validation_inputs = [
            _job_input(
                store,
                project,
                snapshot_id,
                validation_scope,
                identity,
                {"inputSelection": selection["kind"]},
            )
            for identity in enabled
        ]
        result = {
            "projectId": project,
            "operationId": params["operationId"],
            "chain": ["reasoning.execute", "validation.execute"],
            "reasoningInput": _job_input(
                store,
                project,
                snapshot_id,
                "asserted",
                "quality-reasoning",
                {"inputSelection": selection["kind"]},
            ),
            "validationInput": validation_inputs[0] if validation_inputs else None,
            "validationInputs": validation_inputs,
            "executionIdentity": {
                "implementation": semantic_identity(),
                "limits": LIMITS,
                "registryHash": REGISTRY_HASH,
            },
        }
        if not store.contract.validate("result_project.quality.prepare", result):
            fault("INVALID_STATE")
        return ticket.deliver(result)
