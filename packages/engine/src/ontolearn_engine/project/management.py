"""Finite project-management effects inside the original Store.commit transaction.

Historical evidence validation never grants current access. Lifecycle checks are
made at admission; receipts remain readable through the narrow management path.
"""

import json
from copy import deepcopy
from uuid import uuid4

from ontolearn_engine.project import format3
from ontolearn_engine.project.applications import hash_ref, uuid_ref
from ontolearn_engine.storage import LAYERS, Conflict, canonical, digest

KINDS = {"rename", "archive", "set-mode", "copy-current", "trash", "restore-trash"}
METHODS = frozenset(
    "project.management." + name
    for name in ("catalog", "read", "preview", "confirm", "apply", "operation.get")
) | {"project.library.status"}


def require(condition, category="state"):
    if not condition:
        raise Conflict("Invalid project management state", category=category)


def action_value(action):
    require(
        type(action) is dict and type(action.get("kind")) is str and action["kind"] in KINDS,
        "input",
    )
    kind = action["kind"]
    fields = {
        "rename": {"name"},
        "archive": {"archived"},
        "set-mode": {"mode"},
        "copy-current": {"name"},
        "trash": set(),
        "restore-trash": set(),
    }
    require(set(action) == {"kind"} | fields[kind], "input")
    if "name" in action:
        require(
            type(action["name"]) is str
            and bool(action["name"].strip())
            and len(action["name"].encode("utf-8")) <= 4096,
            "input",
        )
    if kind == "archive":
        require(type(action["archived"]) is bool, "input")
    if kind == "set-mode":
        require(action["mode"] in {"guided", "assisted"}, "input")
    return json.loads(canonical(action))


def lifecycle(store, internal):
    # Active/version0 is the existing formal project genesis, not a second
    # mutable baseline. A row exists only after a proven lifecycle transition.
    row = store._db.execute(
        "SELECT state,version FROM project_lifecycle WHERE project=?", (internal,)
    ).fetchone()
    return {"state": row[0], "version": row[1]} if row else {"state": "active", "version": 0}


def active(store, internal):
    require(lifecycle(store, internal)["state"] == "active")


def public_internal(store, public):
    require(uuid_ref(public), "input")
    row = store._db.execute(
        "SELECT internal FROM public_projects WHERE public=?", (public,)
    ).fetchone()
    require(row is not None)
    return row[0]


def active_jobs(store, public=None):
    from ontolearn_engine.job_store import TERMINAL

    if store._db.execute("SELECT 1 FROM sqlite_master WHERE name='jobs'").fetchone() is None:
        return 0
    rows = store._db.execute(
        "SELECT dto FROM jobs" + (" WHERE project=?" if public else ""), (public,) if public else ()
    )
    return sum(json.loads(row[0])["state"] not in TERMINAL for row in rows)


def metadata_after(metadata, action):
    value = deepcopy(metadata)
    if action["kind"] in {"rename", "copy-current"}:
        value["name"] = action["name"]
    elif action["kind"] == "archive":
        value["archived"] = action["archived"]
    elif action["kind"] == "set-mode":
        value["mode"] = action["mode"]
    if action["kind"] == "copy-current":
        value.update(archived=False, origin="created")
    return value


def _drafts(application, revision):
    require(not application["learningCurrent"] and not application["assistanceAudit"])
    rows = deepcopy(application["drafts"])
    for row in rows:
        require(row["editor"] == "query-workspace-v1")
        if row["present"]:
            require(row["bound_revision"] == revision)  # stale drafts need explicit rebasing
            content = json.loads(row["payload"])
            require(
                type(content) is dict
                and set(content) == {"version", "definitionId", "draft"}
                and type(content["version"]) is int
                and content["version"] == 1
            )
            require(type(content["definitionId"]) is str and len(content["definitionId"]) <= 128)
            draft = content["draft"]
            require(
                type(draft) is dict
                and set(draft)
                == {"name", "description", "sparql", "scope", "capabilityQuestion", "source"}
            )
            for key, bound in (
                ("name", 128),
                ("description", 4096),
                ("sparql", 65536),
                ("capabilityQuestion", 4096),
            ):
                require(type(draft[key]) is str and len(draft[key]) <= bound)
                draft[key].encode("utf-8")
            require(
                draft["scope"] in {"asserted", "asserted+derived"}
                and draft["source"] in {"template", "visual", "editor", "model"}
            )
        row.update(generation=1, bound_revision=1)
    return rows


def copy_seed(store, public, internal, checkpoint):
    snapshot = store._project_snapshot(checkpoint["domainSnapshotRef"], internal)
    _drafts(checkpoint["application"], checkpoint["domainRevision"])
    return {
        "copySeedVersion": 1,
        "sourceProjectId": public,
        "sourceProject": internal,
        "checkpoint": checkpoint,
        "domain": snapshot,
        "versions": [
            list(r)
            for r in store._db.execute(
                "SELECT key,version FROM versions WHERE project=? ORDER BY key", (internal,)
            )
        ],
        "retirements": store.retirement_control(internal),
    }


def _seed_vector(seed):
    state = seed["domain"]["state"]
    members = {f"{r['layer']}:{r['id']}" for r in state["definitions"]}
    members.update("mapping:" + x for x in state["mappingState"])
    members.update("mapping:" + r["owner"] for r in state["facts"] if r["owner"] is not None)
    vector = {
        k: v for k, v in seed["versions"] if k.partition(":")[0] not in LAYERS or k in members
    }
    for layer, identity in seed["retirements"]:
        vector.pop(f"{layer}:{identity}", None)
    return vector


def validate_seed(seed):
    require(
        type(seed) is dict
        and set(seed)
        == {
            "copySeedVersion",
            "sourceProjectId",
            "sourceProject",
            "checkpoint",
            "domain",
            "versions",
            "retirements",
        }
    )
    require(
        type(seed["copySeedVersion"]) is int
        and seed["copySeedVersion"] == 1
        and uuid_ref(seed["sourceProjectId"])
    )
    cp, domain = seed["checkpoint"], seed["domain"]
    from ontolearn_engine.storage import Store

    require(
        domain["project"] == cp["project"] == seed["sourceProject"]
        and digest(domain) == cp["domainSnapshotRef"]
        and domain["projectRevision"] == cp["domainRevision"]
    )
    Store._snapshot_state(domain["state"])
    format3._application(cp["application"], seed["sourceProject"], cp["domainRevision"])
    require(type(seed["versions"]) is list and seed["versions"] == sorted(seed["versions"]))
    require(
        all(
            type(r) is list
            and len(r) == 2
            and type(r[0]) is str
            and bool(r[0])
            and format3._integer(r[1])
            and r[1] <= format3.MAX_VERSION
            for r in seed["versions"]
        )
    )
    require(len({r[0] for r in seed["versions"]}) == len(seed["versions"]))
    require(
        type(seed["retirements"]) is list and seed["retirements"] == sorted(seed["retirements"])
    )
    require(
        all(
            type(r) is list and len(r) == 2 and r[0] in LAYERS and type(r[1]) is str and bool(r[1])
            for r in seed["retirements"]
        )
    )
    require(len({tuple(r) for r in seed["retirements"]}) == len(seed["retirements"]))
    require(_seed_vector(seed) == domain["dependencyVector"])
    _drafts(cp["application"], cp["domainRevision"])


def document(store, public, action):
    internal = public_internal(store, public)
    life = lifecycle(store, internal)
    require(life["state"] == ("trashed" if action["kind"] == "restore-trash" else "active"))
    cp = store.project_checkpoint(internal)
    seed = copy_seed(store, public, internal, cp) if action["kind"] == "copy-current" else None
    snapshot = store._project_snapshot(cp["domainSnapshotRef"], internal)
    application, state = cp["application"], snapshot["state"]
    value = {
        "projectName": application["metadata"]["name"],
        "checkpointRef": digest(cp),
        "domainRevision": cp["domainRevision"],
        "operationSequence": cp["operationSequence"],
        "metadataVersion": application["metadataVersion"],
        "lifecycleVersion": life["version"],
        "beforeMetadata": application["metadata"],
        "afterMetadata": metadata_after(application["metadata"], action),
        "counts": {
            "definitions": len(state["definitions"]),
            "facts": len(state["facts"]),
            "tombstones": sum(r["object"] is None for r in state["facts"]),
            "drafts": len(application["drafts"]),
            "learning": len(application["learningCurrent"]),
            "historyRuns": store._db.execute(
                "SELECT count(*) FROM runs WHERE project=?", (internal,)
            ).fetchone()[0],
            "activeJobs": active_jobs(store, public),
        },
        "coverage": [
            "definitions",
            "asserted-facts",
            "ownership",
            "mapping-state",
            "version-ledger",
            "retirements",
            "metadata",
            "query-workspace-v1",
        ]
        if seed is not None
        else (["lifecycle"] if action["kind"] in {"trash", "restore-trash"} else ["metadata"]),
        "exclusions": [
            "historical-runs",
            "current-results",
            "derived-cache",
            "runtime-authority",
            "learning",
            "assistance-audit",
        ]
        if seed is not None
        else [],
        "seedHash": digest(seed) if seed is not None else None,
    }
    return value, seed


def copy_model(project, request, action, seed, origin, library):
    from ontolearn_engine.project.project_lifecycle import model

    validate_seed(seed)
    blank = model(
        project,
        {
            "requestVersion": 1,
            "operationId": request["operationId"],
            "name": action["name"],
            "initialization": {"kind": "blank"},
        },
        origin,
        library,
    )
    before = blank["before"]
    domain = {
        "project": project,
        "projectRevision": 1,
        "dependencyVector": _seed_vector(seed),
        "state": deepcopy(seed["domain"]["state"]),
    }
    after = deepcopy(blank["after"])
    after.update(domainRevision=1, domainSnapshotRef=digest(domain))
    after["application"]["metadata"] = metadata_after(
        seed["checkpoint"]["application"]["metadata"], action
    )
    after["application"]["drafts"] = _drafts(
        seed["checkpoint"]["application"], seed["checkpoint"]["domainRevision"]
    )
    marker_plan = {"copyInitializationVersion": 1, "base": 0, "seedHash": digest(seed)}
    plan = {
        "copyCreatePlanVersion": 1,
        "projectId": project,
        "seedHash": digest(seed),
        "beforeCheckpointRef": digest(before),
        "afterCheckpointRef": digest(after),
        "domainPlan": marker_plan,
    }
    context = {
        "copyCreateContextVersion": 1,
        "libraryEvidenceRef": library,
        "projectId": project,
        "project": project,
        "operationId": request["operationId"],
        "request": request,
        "requestHash": digest(request),
        "action": action,
        "origin": origin,
        "seed": seed,
        "plan": plan,
    }
    proof = {
        "copyCreateReceiptVersion": 1,
        "libraryEvidenceRef": library,
        "projectId": project,
        "operationId": request["operationId"],
        "requestHash": digest(request),
        "contextHash": digest(context),
        "planHash": digest(plan),
        "operationSequence": 1,
        "domainRevision": 1,
        "metadataVersion": 1,
        "inputSnapshotId": digest(domain),
        "beforeCheckpointRef": digest(before),
        "afterCheckpointRef": digest(after),
    }
    op = request["operationId"]
    marker = {
        "project": project,
        "operation": op,
        "job": None,
        "revision": 1,
        "fingerprint": digest(marker_plan),
        "plan": canonical(marker_plan),
        "before_snapshot": before["domainSnapshotRef"],
        "after_snapshot": digest(domain),
    }
    rows = {
        "projects": [(project, 1)],
        "snapshots": [
            (before["domainSnapshotRef"], canonical(blank["domain"])),
            (digest(domain), canonical(domain)),
        ],
        "app_projects": [
            (project, 1, 1, canonical(after["application"]["metadata"]), digest(after))
        ],
        "app_checkpoints": [
            (digest(before), project, before["domainSnapshotRef"], canonical(before)),
            (digest(after), project, digest(domain), canonical(after)),
        ],
        "app_origins": [(project, digest(before), 0, 0, "created")],
        "public_projects": [(project, project)],
        "operation_claims": [
            (op, project, None, digest(context), "application", canonical(context))
        ],
        "app_operations": [(project, 1, op, "combined", digest(plan), 1)],
        "app_receipts": [(project, op, canonical(proof))],
        "definitions": [
            (project, r["layer"], r["id"], r["payload"]) for r in domain["state"]["definitions"]
        ],
        "facts": [
            (
                project,
                *(
                    r[k]
                    for k in (
                        "id",
                        "subject",
                        "predicate",
                        "object",
                        "owner",
                        "source_row",
                        "managed_value",
                    )
                ),
            )
            for r in domain["state"]["facts"]
        ],
        "mapping_state": [
            (project, k, v["generatedVersion"])
            for k, v in sorted(domain["state"]["mappingState"].items())
        ],
        "versions": [(project, k, v) for k, v in seed["versions"]],
        "definition_retirements": [(project, *r) for r in seed["retirements"]],
        "app_drafts": [
            (
                project,
                *(
                    r[k]
                    for k in (
                        "editor",
                        "generation",
                        "present",
                        "bound_revision",
                        "payload",
                        "content_hash",
                    )
                ),
            )
            for r in after["application"]["drafts"]
        ],
        "commits": [(project, op, None, 1, digest(marker_plan), canonical(marker_plan))],
        "commit_evidence": [(project, op, before["domainSnapshotRef"], digest(domain))],
    }
    return {
        "domain": domain,
        "before": before,
        "after": after,
        "context": context,
        "receipt": proof,
        "result": proof,
        "rows": rows,
        "marker": marker,
    }


def copy_context(store, project, operation):
    from ontolearn_engine.project.project_lifecycle import library_evidence, origin_value

    row = store._db.execute(
        "SELECT * FROM operation_claims WHERE operation=?", (operation,)
    ).fetchone()
    if row is None or row["kind"] != "application":
        return None
    context = format3._json(row["context"])
    if type(context) is not dict or "copyCreateContextVersion" not in context:
        return None
    require(row["project"] == project and row["job"] is None and uuid_ref(project))
    expected = copy_model(
        project,
        context["request"],
        action_value(context["action"]),
        context["seed"],
        origin_value(context["origin"]),
        library_evidence(store),
    )
    require(context == expected["context"] and row["fingerprint"] == digest(context))
    require(
        context["operationId"] == operation
        and context["request"]["projectId"] == context["seed"]["sourceProjectId"]
    )
    for table in ("app_origins", "app_operations", "app_receipts", "commits", "commit_evidence"):
        predicate = "project=?" if table == "app_origins" else "project=? AND operation=?"
        params = (project,) if table == "app_origins" else (project, operation)
        require(
            [
                tuple(r)
                for r in store._db.execute(f"SELECT * FROM {table} WHERE {predicate}", params)
            ]
            == expected["rows"][table]
        )
    for table in ("snapshots", "app_checkpoints"):
        for item in expected["rows"][table]:
            actual = store._db.execute(f"SELECT * FROM {table} WHERE id=?", (item[0],)).fetchone()
            require(actual is not None and tuple(actual) == item)
    require(public_internal(store, project) == project)
    management_row = store._db.execute(
        "SELECT project,target,payload FROM management_receipts WHERE operation=?", (operation,)
    ).fetchone()
    require(management_row is not None and management_row["target"] == project)
    adopted = format3._json(management_row["payload"])
    require(
        adopted["request"] == context["request"]
        and adopted["underlyingReceipt"] == expected["receipt"]
        and adopted["beforeCheckpoint"] == context["seed"]["checkpoint"]
        and adopted["afterCheckpoint"] == expected["after"]
    )
    require(management_row["project"] == context["seed"]["sourceProject"])
    return expected


def _result(proof):
    cp = proof["afterCheckpoint"]
    return {
        "managementResultVersion": 1,
        "kind": proof["action"]["kind"],
        "projectId": proof["request"]["projectId"],
        "operationId": proof["request"]["operationId"],
        "targetProjectId": proof["targetProjectId"],
        "requestHash": digest(proof["request"]),
        "receiptHash": digest(proof),
        "checkpointRef": digest(cp),
        "domainRevision": cp["domainRevision"],
        "metadataVersion": cp["application"]["metadataVersion"],
        "operationSequence": cp["operationSequence"],
        "lifecycleVersion": proof["afterLifecycle"]["version"],
        "lifecycleState": proof["afterLifecycle"]["state"],
    }


def operation_get(store, public, operation, request_hash):
    require(uuid_ref(operation) and hash_ref(request_hash), "input")
    internal = public_internal(store, public)
    with store._read():
        format3.validate(store)
        row = store._db.execute(
            "SELECT * FROM management_receipts WHERE operation=?", (operation,)
        ).fetchone()
        if row is None:
            occupied = store._db.execute(
                "SELECT 1 FROM operation_claims WHERE operation=?", (operation,)
            ).fetchone()
            require(occupied is None, "identity")
            return {"state": "not-found", "result": None}
        proof = format3._json(row["payload"])
        require(
            row["project"] == internal
            and proof["request"]["projectId"] == public
            and digest(proof["request"]) == request_hash,
            "identity",
        )
        return {"state": "applied", "result": _result(proof)}


def validate_ledger(store):
    # Full immutable chain plus actual app/domain evidence, not a receipt hash
    # checked against itself. This path deliberately ignores current access.
    from ontolearn_engine.project.project_lifecycle import library_evidence, origin_value

    rows = store._db.execute("SELECT * FROM management_receipts ORDER BY sequence").fetchall()
    previous = None
    life_heads = {}
    for sequence, row in enumerate(rows, 1):
        proof = format3._json(row["payload"])
        require(
            type(proof) is dict
            and set(proof)
            == {
                "managementReceiptVersion",
                "sequence",
                "previousReceiptHash",
                "libraryEvidenceRef",
                "request",
                "action",
                "document",
                "documentHash",
                "sourceProject",
                "targetProjectId",
                "beforeCheckpoint",
                "afterCheckpoint",
                "beforeLifecycle",
                "afterLifecycle",
                "underlyingReceipt",
                "origin",
                "blockedConfirmations",
            }
        )
        require(
            type(proof["managementReceiptVersion"]) is int
            and proof["managementReceiptVersion"] == 1
        )
        origin_value(proof["origin"])
        require(type(proof["sequence"]) is int)
        require(
            row["sequence"] == proof["sequence"] == sequence
            and proof["previousReceiptHash"] == previous
            and proof["libraryEvidenceRef"] == library_evidence(store)
        )
        request = proof["request"]
        require(
            type(request) is dict
            and set(request) == {"projectId", "operationId", "confirmationRef", "documentHash"}
        )
        require(
            uuid_ref(request["projectId"])
            and uuid_ref(request["operationId"])
            and uuid_ref(request["confirmationRef"])
            and hash_ref(request["documentHash"])
        )
        require(
            row["operation"] == request["operationId"]
            and row["project"]
            == proof["sourceProject"]
            == public_internal(store, request["projectId"])
            and row["target"] == public_internal(store, proof["targetProjectId"])
        )
        action = action_value(proof["action"])
        require(
            proof["documentHash"]
            == request["documentHash"]
            == digest({"action": action, "document": proof["document"]})
        )
        before = proof["beforeCheckpoint"]
        after = proof["afterCheckpoint"]
        require(
            format3._raw_checkpoint(store, row["project"], digest(before)) == before
            and format3._raw_checkpoint(store, row["target"], digest(after)) == after
        )
        beforelife = life_heads.get(row["project"], {"state": "active", "version": 0})
        require(proof["beforeLifecycle"] == beforelife)
        require(
            beforelife["state"] == ("trashed" if action["kind"] == "restore-trash" else "active")
        )
        doc = proof["document"]
        require(
            type(doc) is dict
            and set(doc)
            == {
                "projectName",
                "checkpointRef",
                "domainRevision",
                "operationSequence",
                "metadataVersion",
                "lifecycleVersion",
                "beforeMetadata",
                "afterMetadata",
                "counts",
                "coverage",
                "exclusions",
                "seedHash",
            }
        )
        require(
            all(
                format3._integer(doc[key]) and doc[key] <= format3.MAX_VERSION
                for key in (
                    "domainRevision",
                    "operationSequence",
                    "metadataVersion",
                    "lifecycleVersion",
                )
            )
        )
        require(doc["projectName"] == before["application"]["metadata"]["name"])
        for life in (proof["beforeLifecycle"], proof["afterLifecycle"]):
            require(
                type(life) is dict
                and set(life) == {"state", "version"}
                and life["state"] in {"active", "trashed"}
                and format3._integer(life["version"])
                and life["version"] <= format3.MAX_VERSION
            )
        source_domain = store._project_snapshot(before["domainSnapshotRef"], row["project"])
        counts = doc["counts"]
        require(
            type(counts) is dict
            and set(counts)
            == {
                "definitions",
                "facts",
                "tombstones",
                "drafts",
                "learning",
                "historyRuns",
                "activeJobs",
            }
            and all(
                format3._integer(value) and value <= format3.MAX_VERSION
                for value in counts.values()
            )
        )
        expected_counts = {
            "definitions": len(source_domain["state"]["definitions"]),
            "facts": len(source_domain["state"]["facts"]),
            "tombstones": sum(fact["object"] is None for fact in source_domain["state"]["facts"]),
            "drafts": len(before["application"]["drafts"]),
            "learning": len(before["application"]["learningCurrent"]),
        }
        require(all(counts[key] == value for key, value in expected_counts.items()))
        require(
            counts["historyRuns"]
            <= store._db.execute(
                "SELECT count(*) FROM runs WHERE project=?", (row["project"],)
            ).fetchone()[0]
        )
        require(
            counts["activeJobs"]
            <= store._db.execute(
                "SELECT count(*) FROM jobs WHERE project=?", (request["projectId"],)
            ).fetchone()[0]
        )
        if action["kind"] in {"trash", "restore-trash"}:
            require(counts["activeJobs"] == 0)
        expected_coverage = (
            [
                "definitions",
                "asserted-facts",
                "ownership",
                "mapping-state",
                "version-ledger",
                "retirements",
                "metadata",
                "query-workspace-v1",
            ]
            if action["kind"] == "copy-current"
            else (["lifecycle"] if action["kind"] in {"trash", "restore-trash"} else ["metadata"])
        )
        expected_exclusions = (
            [
                "historical-runs",
                "current-results",
                "derived-cache",
                "runtime-authority",
                "learning",
                "assistance-audit",
            ]
            if action["kind"] == "copy-current"
            else []
        )
        require(doc["coverage"] == expected_coverage and doc["exclusions"] == expected_exclusions)
        require(
            hash_ref(doc["seedHash"])
            if action["kind"] == "copy-current"
            else doc["seedHash"] is None
        )
        require(
            doc["checkpointRef"] == digest(before)
            and doc["lifecycleVersion"] == beforelife["version"]
            and doc["domainRevision"] == before["domainRevision"]
            and doc["operationSequence"] == before["operationSequence"]
            and doc["metadataVersion"] == before["application"]["metadataVersion"]
        )
        require(
            doc["beforeMetadata"] == before["application"]["metadata"]
            and doc["afterMetadata"] == metadata_after(doc["beforeMetadata"], action)
        )
        if action["kind"] == "copy-current":
            require(row["target"] != row["project"])
            created = copy_context(store, row["target"], row["operation"])
            require(
                created is not None
                and created["context"]["seed"]["checkpoint"] == before
                and created["context"]["request"] == request
                and created["context"]["action"] == action
            )
            require(
                created["after"] == after
                and created["receipt"] == proof["underlyingReceipt"]
                and doc["seedHash"] == digest(created["context"]["seed"])
            )
            require(proof["afterLifecycle"] == {"state": "active", "version": 0})
        elif action["kind"] in {"trash", "restore-trash"}:
            require(
                row["target"] == row["project"]
                and before == after
                and proof["underlyingReceipt"] is None
            )
            nextlife = {
                "state": "trashed" if action["kind"] == "trash" else "active",
                "version": beforelife["version"] + 1,
            }
            require(proof["afterLifecycle"] == nextlife)
            life_heads[row["project"]] = nextlife
            claim = store._db.execute(
                "SELECT * FROM operation_claims WHERE operation=?", (row["operation"],)
            ).fetchone()
            expected = {
                "managementLifecycleContextVersion": 1,
                "projectId": request["projectId"],
                "operationId": row["operation"],
                "receiptHash": digest(proof),
            }
            require(
                claim is not None
                and claim["kind"] == "application"
                and claim["project"] == request["projectId"]
                and claim["job"] is None
                and claim["fingerprint"] == digest(expected)
                and format3._json(claim["context"]) == expected
            )
        else:
            require(row["target"] == row["project"] and proof["afterLifecycle"] == beforelife)
            receipt = format3.receipt_for(store, row["project"], row["operation"])
            require(
                receipt == proof["underlyingReceipt"]
                and receipt["beforeCheckpointRef"] == digest(before)
                and receipt["afterCheckpointRef"] == digest(after)
            )
            require(after["application"]["metadata"] == doc["afterMetadata"])
            from ontolearn_engine.project.applications import claim_context

            app_context = claim_context(store, row["project"], row["operation"])
            require(
                app_context["request"]["authorization"]["actor"] == proof["origin"]["hostClientId"]
            )
            patch = {
                "rename": {"name": action.get("name")},
                "archive": {"archived": action.get("archived")},
                "set-mode": {"mode": action.get("mode")},
            }[action["kind"]]
            require(
                app_context["request"]["change"]
                == {
                    "type": "metadata",
                    "expectedVersion": before["application"]["metadataVersion"],
                    "patch": patch,
                }
            )
        blocked = proof["blockedConfirmations"]
        require(type(blocked) is list and blocked == sorted(set(blocked)))
        require(action["kind"] == "trash" or not blocked)
        for ref in blocked:
            require(
                store._db.execute(
                    "SELECT 1 FROM job_confirmations WHERE id=? AND project=?",
                    (ref, request["projectId"]),
                ).fetchone()
                is not None
            )
        previous = digest(proof)
    actual = {
        r["project"]: {"state": r["state"], "version": r["version"]}
        for r in store._db.execute("SELECT * FROM project_lifecycle")
    }
    require(actual == life_heads)
    for row in store._db.execute("SELECT * FROM project_lifecycle"):
        record = store._db.execute(
            "SELECT payload FROM management_receipts WHERE operation=?", (row["operation"],)
        ).fetchone()
        require(
            record is not None
            and format3._json(record[0])["afterLifecycle"] == actual[row["project"]]
            and format3._json(record[0])["sourceProject"] == row["project"]
        )


def check_confirmation_current(store, public, confirmation):
    if store._target_format != 3 or confirmation is None:
        return
    active(store, public_internal(store, public))
    for row in store._db.execute(
        "SELECT payload FROM management_receipts WHERE project=?", (public_internal(store, public),)
    ):
        proof = format3._json(row[0])
        require(confirmation not in proof["blockedConfirmations"])


def commit(store, project, base, operation, job, supplied, hook):
    from ontolearn_engine.job_store import JobStore
    from ontolearn_engine.project.project_host import ProjectHostReader, ReadLimits
    from ontolearn_engine.project.project_lifecycle import library_evidence, origin_value, preflight

    require(
        isinstance(store, JobStore)
        and store._target_format == 3
        and project is None
        and base is None
        and job is None
    )
    require(
        type(supplied) is dict
        and set(supplied) == {"request", "action", "document", "seed", "origin", "readerLimits"},
        "input",
    )
    request = supplied["request"]
    require(
        type(request) is dict
        and set(request) == {"projectId", "operationId", "confirmationRef", "documentHash"}
        and request["operationId"] == operation,
        "input",
    )
    require(
        uuid_ref(operation)
        and uuid_ref(request["confirmationRef"])
        and hash_ref(request["documentHash"]),
        "input",
    )
    action = action_value(supplied["action"])
    origin = origin_value(supplied["origin"])
    require(type(supplied["readerLimits"]) is ReadLimits, "input")
    with store._transaction(hook):
        reader = ProjectHostReader(store, limits=supplied["readerLimits"])
        reader._preflight()
        reader._validate()
        store._validate_job3()
        existing = operation_get(store, request["projectId"], operation, digest(request))
        if existing["state"] == "applied":
            return existing["result"]
        internal = public_internal(store, request["projectId"])
        current, seed = document(store, request["projectId"], action)
        require(current == supplied["document"] and seed == supplied["seed"], "revision")
        require(
            digest({"action": action, "document": current}) == request["documentHash"], "identity"
        )
        require(
            action["kind"] not in {"trash", "restore-trash"} or current["counts"]["activeJobs"] == 0
        )
        before = store.project_checkpoint(internal)
        beforelife = lifecycle(store, internal)
        require(beforelife["version"] < format3.MAX_VERSION)
        target = request["projectId"]
        targetinternal = internal
        underlying = None
        if action["kind"] == "copy-current":
            target = str(uuid4())
            targetinternal = target
            candidate = copy_model(target, request, action, seed, origin, library_evidence(store))
            preflight(store, candidate, supplied["readerLimits"])
            hook("management_copy_preflight")
            # Defer FKs only within this one atomic transaction; all actual rows
            # and links are validated before commit. No alternate connection.
            store._db.execute("PRAGMA defer_foreign_keys=ON")
            for table, rows in candidate["rows"].items():
                for row in rows:
                    store._db.execute(
                        f"INSERT INTO {table} VALUES({','.join('?' for _ in row)})", row
                    )
                hook("management_copy:" + table)
            store._validate_references(target)
            store._validate_single_slots(target)
            require(
                store.state(target) == candidate["domain"]["state"]
                and store.vector(target) == candidate["domain"]["dependencyVector"]
            )
            underlying = candidate["receipt"]
        elif action["kind"] not in {"trash", "restore-trash"}:
            patch = {
                "rename": {"name": action.get("name")},
                "archive": {"archived": action.get("archived")},
                "set-mode": {"mode": action.get("mode")},
            }[action["kind"]]
            change = {
                "type": "metadata",
                "expectedVersion": before["application"]["metadataVersion"],
                "patch": patch,
            }
            underlying = store.apply_application(
                request["projectId"],
                operation,
                change,
                actor=origin["hostClientId"],
                permission="write",
                hook=hook,
            )
        after = (
            candidate["after"]
            if action["kind"] == "copy-current"
            else store.project_checkpoint(targetinternal)
        )
        afterlife = (
            {
                "state": "trashed" if action["kind"] == "trash" else "active",
                "version": beforelife["version"] + 1,
            }
            if action["kind"] in {"trash", "restore-trash"}
            else lifecycle(store, targetinternal)
        )
        last = store._db.execute(
            "SELECT sequence,payload FROM management_receipts ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        blocked = (
            sorted(
                r[0]
                for r in store._db.execute(
                    "SELECT id FROM job_confirmations WHERE project=?", (request["projectId"],)
                )
            )
            if action["kind"] == "trash"
            else []
        )
        proof = {
            "managementReceiptVersion": 1,
            "sequence": last[0] + 1 if last else 1,
            "previousReceiptHash": digest(format3._json(last[1])) if last else None,
            "libraryEvidenceRef": library_evidence(store),
            "request": request,
            "action": action,
            "document": current,
            "documentHash": request["documentHash"],
            "sourceProject": internal,
            "targetProjectId": target,
            "beforeCheckpoint": before,
            "afterCheckpoint": after,
            "beforeLifecycle": beforelife,
            "afterLifecycle": afterlife,
            "underlyingReceipt": underlying,
            "origin": origin,
            "blockedConfirmations": blocked,
        }
        store._db.execute(
            "INSERT INTO management_receipts VALUES(?,?,?,?,?)",
            (operation, proof["sequence"], internal, targetinternal, canonical(proof)),
        )
        if action["kind"] in {"trash", "restore-trash"}:
            if action["kind"] == "trash":
                # Pagination tokens are transient authority. Keep immutable
                # plans, receipts, Jobs and result history, but revoke tokens.
                for table in ("job_cursors", "job_lists"):
                    for token in store._db.execute(f"SELECT id,binding FROM {table}").fetchall():
                        if json.loads(token["binding"]).get("projectId") == request["projectId"]:
                            store._db.execute(f"DELETE FROM {table} WHERE id=?", (token["id"],))
            context = {
                "managementLifecycleContextVersion": 1,
                "projectId": request["projectId"],
                "operationId": operation,
                "receiptHash": digest(proof),
            }
            store._db.execute(
                "INSERT INTO operation_claims VALUES(?,?,NULL,?,'application',?)",
                (operation, request["projectId"], digest(context), canonical(context)),
            )
            store._db.execute(
                "INSERT INTO project_lifecycle VALUES(?,?,?,?) ON CONFLICT(project) DO UPDATE "
                "SET state=excluded.state,version=excluded.version,operation=excluded.operation",
                (internal, afterlife["state"], afterlife["version"], operation),
            )
        hook("management_receipt")
        reader._preflight()
        reader._validate()
        store._validate_job3()
        hook("management_validated")
        return _result(proof)
