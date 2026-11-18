"""Quality workspace reads and preparation; never a save or execution issuer.

``project.quality.prepare`` freezes the inputs for the FR-500..503
"检查我的项目" chain (reasoning.execute, then validation.execute) without
creating or running any job. ``project.quality.read`` projects the current
persisted quality state — FR-504/505 definitions, three-tier findings with
click-to-locate targets (FR-503), rule and RDFS derivation provenance
(FR-502) and invalidation reasons (FR-006) — strictly from immutable results
and stored definitions. Nothing here re-executes rules or shapes; the only
in-memory evaluation is the FR-505 ``ruleTest`` sample, which runs the real
semantic executor on a synthetic snapshot without any write or persistence.
"""

import json

from ontolearn_engine.job_store import fault, payload_from_rows
from ontolearn_engine.storage import digest

METHODS = frozenset({"project.quality.read", "project.quality.prepare"})

TERMINAL_JOB_STATES = ("succeeded", "failed", "cancelled")

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


def _revision_projection(payload, layer, identity, current_vector):
    """Definition version: the stored revision when well-formed, else the vector."""
    revision = payload.get("revision")
    if type(revision) is int and revision >= 0:
        return revision
    return current_vector.get(f"{layer}:{identity}", 0)


def _rule_summary(identity, payload, layer, current_vector):
    revision = _revision_projection(payload, layer, identity, current_vector)
    if payload.get("kind") == "rule":
        return {
            "id": identity,
            "format": "fr505",
            "label": payload.get("label"),
            "enabled": bool(payload.get("enabled")),
            "revision": revision,
            "conditions": payload.get("conditions", []),
            "conclusions": payload.get("conclusions", []),
        }
    return {
        "id": identity,
        "format": "legacy",
        "enabled": bool(payload.get("enabled")),
        "revision": revision,
        "when": payload.get("when", []),
        "then": payload.get("then"),
    }


def _constraint_summary(identity, payload, layer, current_vector):
    revision = _revision_projection(payload, layer, identity, current_vector)
    if payload.get("kind") == "constraint":
        return {
            "id": identity,
            "format": "fr504",
            "label": payload.get("label"),
            "enabled": bool(payload.get("enabled")),
            "revision": revision,
            "targetClass": payload.get("targetClass"),
            "path": payload.get("path"),
            "template": payload.get("template"),
            "parameters": payload.get("parameters", {}),
        }
    return {
        "id": identity,
        "format": "turtle",
        "enabled": bool(payload.get("enabled")),
        "revision": revision,
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


def _terminal_validation_cohort(store, project):
    """Newest-terminal validation.execute cohort keyed by one frozen queue key.

    jobs.project stores the public project UUID (unlike results.project which
    stores the internal id). The newest terminal validation job anchors the
    cohort: only jobs sharing its exact (snapshot, scope, derived ids) belong
    to it, so asserted and asserted+derived runs — or runs against different
    snapshots / reasoning batches — never mix into one aggregated view.
    """
    cohort = []
    anchor = None
    anchor_key = None
    for row in store._db.execute(
        "SELECT dto FROM jobs WHERE project=? ORDER BY rowid DESC", (project,)
    ).fetchall():
        dto = json.loads(row["dto"])
        if (
            dto.get("capability") != "validation.execute"
            or dto.get("projectId") != project
            or dto.get("state") not in TERMINAL_JOB_STATES
        ):
            continue
        input_ = dto.get("input") if isinstance(dto.get("input"), dict) else {}
        key = (
            input_.get("inputSnapshotId"),
            input_.get("scope"),
            tuple(input_.get("derivedResultIds") or ()),
        )
        if anchor is None:
            anchor, anchor_key = dto, key
        if key == anchor_key and input_.get("definitionId") not in {
            item["definitionId"] for item in cohort
        }:
            cohort.append({"definitionId": input_.get("definitionId"), "job": dto})
    return anchor, cohort


def _validation_view(store, project, internal, state):
    """Aggregate the anchored validation cohort with strict coverage semantics.

    conforms is True only when every enabled constraint (both now and at the
    anchor snapshot) has an available succeeded result in the cohort; any
    missing, failed or evicted constraint forces None — the read projection
    must never display "符合约束" over a partial check.
    """
    anchor, cohort = _terminal_validation_cohort(store, project)
    if anchor is None:
        return None
    anchor_snapshot = anchor["input"]["inputSnapshotId"]
    enabled_now = {
        identity
        for identity, payload in _formal_definitions(state, "constraint")
        if payload.get("enabled")
    }
    anchor_state = store._project_snapshot(anchor_snapshot, internal)["state"]
    enabled_at_anchor = {
        identity
        for identity, payload in _formal_definitions(anchor_state, "constraint")
        if payload.get("enabled")
    }
    required_ids = enabled_now | enabled_at_anchor
    latest_jobs = {item["definitionId"]: item["job"] for item in cohort}
    checked_views = {}
    newest_checked = None
    unverified_ids = set()
    failed_ids = set()
    for cid in sorted(set(required_ids) | set(latest_jobs)):
        job = latest_jobs.get(cid)
        if (
            job is not None
            and job["state"] == "succeeded"
            and isinstance(job.get("resultRef"), dict)
        ):
            dto = store.result_get(project, job["resultRef"]["resultId"])
            if dto["payloadStatus"] == "available":
                payload = payload_from_rows(store.result(job["resultRef"]["resultId"])["payload"])
                report = payload.get("report") if isinstance(payload, dict) else None
                violations = report.get("violations", []) if isinstance(report, dict) else []
                conforms = report.get("conforms") if isinstance(report, dict) else None
                checked_views[cid] = {
                    "state": dto["state"],
                    "staleReasons": dto["staleReason"],
                    "conforms": conforms if isinstance(conforms, bool) else None,
                    "findings": [{**_finding(item), "definitionId": cid} for item in violations],
                }
                if newest_checked is None:
                    newest_checked = cid
                continue
            failed_ids.add(cid)
            if cid in required_ids:
                unverified_ids.add(cid)
            continue
        if job is not None:  # failed or cancelled single-constraint rerun
            failed_ids.add(cid)
            if cid in required_ids:
                unverified_ids.add(cid)
            continue
        if cid in required_ids:
            unverified_ids.add(cid)
    conforms = (
        all(view["conforms"] for view in checked_views.values())
        if (
            not unverified_ids
            and not failed_ids
            and checked_views
            and all(isinstance(view["conforms"], bool) for view in checked_views.values())
        )
        else None
    )
    stale_reasons = []
    seen_reasons = set()
    for cid in sorted(checked_views):
        for reason in checked_views[cid]["staleReasons"]:
            marker = json.dumps(reason, sort_keys=True, ensure_ascii=False)
            if marker not in seen_reasons:
                seen_reasons.add(marker)
                stale_reasons.append(reason)
    if stale_reasons:
        view_state = "stale"
    elif anchor_snapshot != store.snapshot(internal) or any(
        view["state"] == "historical" for view in checked_views.values()
    ):
        view_state = "historical"
    else:
        view_state = "current"
    if not unverified_ids and not failed_ids and checked_views:
        definition_projection = (
            next(iter(sorted(checked_views)))
            if len(checked_views) == 1
            else "all-enabled-constraints"
        )
    else:
        definition_projection = "partial-constraints"
    if newest_checked is not None:
        newest_job = latest_jobs[newest_checked]
        result_id, job_id = (
            newest_job["resultRef"]["resultId"],
            newest_job["jobId"],
        )
    else:
        # Every cohort job failed or was evicted: surface the failure itself
        # (anchor job identity) so failed constraints become visible at once.
        result_id, job_id = anchor["jobId"], anchor["jobId"]
    return {
        "resultId": result_id,
        "jobId": job_id,
        "state": view_state,
        # Named staleReasons (plural): the singular key is reserved by the
        # shared contract semantic walker for full result DTOs.
        "staleReasons": stale_reasons,
        "inputSnapshotId": anchor_snapshot,
        "scope": anchor["input"]["scope"],
        "definitionId": definition_projection,
        "conforms": conforms,
        "findings": [
            finding for cid in sorted(checked_views) for finding in checked_views[cid]["findings"]
        ],
        "inputProjectRevision": store._project_snapshot(anchor_snapshot, internal)[
            "projectRevision"
        ],
        "checkedConstraintIds": sorted(checked_views),
        "unverifiedConstraintIds": sorted(unverified_ids),
        "failedConstraintIds": sorted(failed_ids),
    }


def _quality_state(store, project):
    internal = store._project(project)
    state = store.state(internal)
    current_vector = store.vector(internal)
    rules = [
        _rule_summary(i, p, "rule", current_vector) for i, p in _formal_definitions(state, "rule")
    ]
    constraints = [
        _constraint_summary(i, p, "constraint", current_vector)
        for i, p in _formal_definitions(state, "constraint")
    ]
    reasoning_view = None
    for row in _latest_results(store, internal):
        try:
            dto = store.result_get(project, row["id"])
        except Exception:
            continue
        if dto["payloadStatus"] != "available" or dto["kind"] != "reasoning":
            continue
        payload = payload_from_rows(store.result(row["id"])["payload"])
        derivation = _derivation(payload)
        reasoning_view = {
            "resultId": row["id"],
            "jobId": dto["jobId"],
            "state": dto["state"],
            "staleReasons": dto["staleReason"],
            "inputSnapshotId": dto["inputSnapshotId"],
            "scope": dto["scope"],
            "definitionId": dto["definitionId"],
        }
        if derivation is not None:
            reasoning_view["derivation"] = derivation
        break
    validation_view = _validation_view(store, project, internal, state)
    return {
        "qualityReadVersion": 1,
        "projectId": project,
        "rules": rules,
        "constraints": constraints,
        "reasoning": reasoning_view,
        "validation": validation_view,
        "snapshotsAligned": (
            None
            if reasoning_view is None or validation_view is None
            else reasoning_view["inputSnapshotId"] == validation_view["inputSnapshotId"]
        ),
    }


def _evaluate_rule_sample(store, rule_test):
    """FR-505 in-memory sample evaluation: no write transaction, no job, no rows.

    Statements and rules are validated with the shared editor language, static
    rule chains warn, and a synthetic memory-only snapshot drives the real
    semantic executor exactly once. Every failure converges into structured
    diagnostics; raw exception details never leak out.
    """
    from ontolearn_engine.quality.definitions import DefinitionError, validate_definition
    from ontolearn_engine.quality.planning import _signature, validate_statement

    stages = (
        ("ontology", "ontologyTriples"),
        ("input", "inputTriples"),
        ("expected", "expectedOutputs"),
    )
    diagnostics = []
    static_warnings = []
    triples = {}
    for stage, key in stages:
        rows = []
        for index, triple in enumerate(rule_test.get(key) or []):
            try:
                rows.append(list(validate_statement(triple, ())))
            except DefinitionError as error:
                diagnostics.append(
                    _rule_test_diagnostic(stage, index, None, error.path, error.code)
                )
        triples[key] = rows
    definitions = []
    enabled_rules = []
    for index, rule in enumerate(rule_test.get("rules") or []):
        rule_id = rule.get("id") if isinstance(rule, dict) else None
        candidate = {"schemaVersion": 1, "kind": "rule", "revision": 1}
        if isinstance(rule, dict):
            candidate.update(rule)
        try:
            validate_definition(candidate)
        except DefinitionError as error:
            diagnostics.append(
                _rule_test_diagnostic("rule", index, rule_id, error.path, error.code)
            )
            continue
        definitions.append(candidate)
        if candidate["enabled"]:
            enabled_rules.append(candidate)
    signatures = {
        rule["id"]: {
            "reads": {_signature(c) for c in rule["conditions"] if c["kind"] != "compare"},
            "writes": {_signature(c) for c in rule["conclusions"]},
        }
        for rule in enabled_rules
    }
    for consumer in enabled_rules:
        reads = signatures[consumer["id"]]["reads"]
        type_read = any(kind == "type" for kind, _ in reads)
        if any(
            signatures[producer["id"]]["writes"] & reads
            or (type_read and signatures[producer["id"]]["writes"])
            for producer in enabled_rules
        ):
            static_warnings.append(f"RULE_CHAIN_UNSUPPORTED:{consumer['id']}")
            static_warnings.append(
                f"规则 {consumer['id']} 读取其他启用规则的结论：当前版本不支持规则链"
            )
    result = {
        "valid": not diagnostics,
        "matchesExpected": False,
        "actualOutputs": [],
        "rdfsOutputs": [],
        "expectedOutputs": [],
        "missingOutputs": [],
        "unexpectedOutputs": [],
        "ruleTraces": [],
        "warnings": _merged_warnings(static_warnings, []),
        "diagnostics": diagnostics,
    }
    if diagnostics:
        return result
    snapshot = {
        "projectRevision": 0,
        "state": {
            "facts": [
                {"subject": subject, "predicate": predicate, "object": object_}
                for subject, predicate, object_ in triples["inputTriples"]
            ],
            "definitions": [
                {
                    "layer": "ontology",
                    "id": "sample.ontology",
                    "payload": json.dumps(
                        {
                            "triples": [
                                {"subject": subject, "predicate": predicate, "object": object_}
                                for subject, predicate, object_ in triples["ontologyTriples"]
                            ]
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                }
            ]
            + [
                {"layer": "rule", "id": rule["id"], "payload": json.dumps(rule)}
                for rule in definitions
            ],
        },
    }
    snap_digest = digest(snapshot)
    from ontolearn_engine.semantic_execution import execute_request

    try:
        out = execute_request(
            {
                "snapshot": snapshot,
                "capability": "reasoning.execute",
                "input": {
                    "inputSnapshotId": snap_digest,
                    "scope": "asserted",
                    "definitionId": "rule-sample-test",
                    "parametersHash": snap_digest,
                    "derivedResultIds": [],
                    "preparedPlanRef": None,
                },
                "parameters": {"inputSelection": "current"},
                "selected": None,
            },
            error_catalog=store.contract.ERROR_CATALOG,
            error_schema=store.contract.DOCUMENT,
        )
    except Exception:
        diagnostics.append(_rule_test_diagnostic("input", 0, None, (), "SEMANTIC_EXECUTION_FAILED"))
        result["diagnostics"] = diagnostics
        result["valid"] = False
        return result
    derivation = _derivation(out["payload"]) or {}
    actual = sorted({tuple(triple) for triple in derivation.get("rules", [])})
    rdfs_outputs = sorted({tuple(triple) for triple in derivation.get("rdfs", [])})
    expected = sorted({tuple(triple) for triple in triples["expectedOutputs"]})
    result.update(
        {
            "matchesExpected": not diagnostics and actual == expected,
            "actualOutputs": [list(triple) for triple in actual],
            "rdfsOutputs": [list(triple) for triple in rdfs_outputs],
            "expectedOutputs": [list(triple) for triple in expected],
            "missingOutputs": [list(triple) for triple in sorted(set(expected) - set(actual))],
            "unexpectedOutputs": [list(triple) for triple in sorted(set(actual) - set(expected))],
            "ruleTraces": derivation.get("ruleTraces", []),
            "warnings": _merged_warnings(static_warnings, derivation.get("warnings", [])),
        }
    )
    return result


def _rule_test_diagnostic(stage, index, rule_id, path, code):
    return {
        "stage": stage,
        "index": index,
        "ruleId": rule_id,
        "field": ".".join(str(piece) for piece in path),
        "code": code,
        "message": f"{code}：{stage}[{index}]"
        + ("" if not path else " " + ".".join(str(piece) for piece in path))
        + " 校验失败",
    }


def _merged_warnings(static_warnings, runtime_warnings):
    merged = []
    for warning in [*static_warnings, *runtime_warnings]:
        if warning not in merged:
            merged.append(warning)
    return merged


def read(store, params, ticket):
    ticket.check(store)
    store._valid("params_project.quality.read", params)
    if params["projectId"] != ticket.project:
        fault("PERMISSION_DENIED")
    with store._read():
        result = _quality_state(store, params["projectId"])
        if params.get("ruleTest") is not None:
            result["ruleTestResult"] = _evaluate_rule_sample(store, params["ruleTest"])
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
            state = store._project_snapshot(snapshot_id, internal)["state"]
        else:
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
