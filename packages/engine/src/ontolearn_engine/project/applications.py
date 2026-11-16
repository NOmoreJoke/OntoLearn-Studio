"""Private application plans over the existing global claim and Store.commit.

No renderer DTO, runtime registration, secondary Store or independent writer.
Only metadata and durable draft changes are accepted here. Learning producer
proof and full application restore must be implemented before accepting them.
"""

import json
from copy import deepcopy

from ontolearn_engine.project.draft_plan import DraftHead, delete_draft, restore_draft, save_draft
from ontolearn_engine.storage import Conflict, canonical, digest

PLAN_KEYS = {
    "applicationPlanVersion",
    "project",
    "change",
    "domain",
    "before",
    "after",
    "beforeCAS",
    "afterCAS",
}
CONTEXT_KEYS = {
    "applicationContextVersion",
    "projectId",
    "project",
    "operationId",
    "request",
    "plan",
}


def require(condition):
    if not condition:
        raise Conflict("Invalid application plan", category="input")


def integer(value):
    from ontolearn_engine.project.format3 import MAX_VERSION

    return type(value) is int and 0 <= value <= MAX_VERSION


def next_version(value):
    from ontolearn_engine.project.format3 import MAX_VERSION

    require(integer(value))
    if value == MAX_VERSION:
        raise Conflict("Application version limit", category="state")
    return value + 1


def stable(value):
    try:
        encoded = canonical(value)
        encoded.encode("utf-8")
        return json.loads(encoded)
    except (TypeError, ValueError):
        raise Conflict("Valid UTF-8 JSON application input required", category="input") from None


def hash_ref(value):
    return (
        isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)
    )


def uuid_ref(value):
    from uuid import UUID

    if not isinstance(value, str):
        return False
    try:
        parsed = UUID(value)
        return parsed.version == 4 and str(parsed) == value
    except ValueError:
        return False


def cas(scope, identity, version):
    return {"scope": scope, "identity": identity, "version": version}


CHECKPOINT_REASONS = ("manual", "before-run", "guided-stage", "before-agent")
RESTORE_WITHDRAWN = "withdrawn-by-project-restore"


def check_change(change):
    require(isinstance(change, dict) and isinstance(change.get("type"), str))
    base = {"type", "domain"} if "domain" in change else {"type"}
    kind = change["type"]
    fields = {
        "metadata": {"expectedVersion", "patch"},
        "draft.save": {"editor", "expectedGeneration", "boundDomainRevision", "content"},
        "draft.delete": {"editor", "expectedGeneration"},
        "draft.restore": {"editor", "expectedGeneration", "checkpointRef"},
        "checkpoint.create": {"reason", "label"},
        "project.restore": {
            "checkpointRef",
            "expectedCheckpointRef",
            "expectedMetadataVersion",
            "expectedOperationSequence",
        },
        "learning.record": {
            "attempt",
            "course",
            "task",
            "expectedRecordVersion",
            "payload",
            "assistanceEvent",
        },
    }
    require(kind in fields and set(change) == base | fields[kind])
    if kind == "checkpoint.create":
        # A checkpoint only freezes evidence; it can never carry a domain plan.
        require("domain" not in change)
        require(change["reason"] in CHECKPOINT_REASONS)
        label = change["label"]
        require(
            label is None
            or (isinstance(label, str) and bool(label) and len(label.encode("utf-8")) <= 256)
        )
        stable(change)
        return
    if kind == "project.restore":
        require(hash_ref(change["checkpointRef"]) and hash_ref(change["expectedCheckpointRef"]))
        require(
            integer(change["expectedMetadataVersion"])
            and integer(change["expectedOperationSequence"])
        )
    if kind == "metadata":
        patch = change["patch"]
        require(integer(change["expectedVersion"]) and isinstance(patch, dict) and bool(patch))
        require(not set(patch) - {"name", "archived", "mode"})
        if "name" in patch:
            require(isinstance(patch["name"], str) and bool(patch["name"].strip()))
        if "archived" in patch:
            require(type(patch["archived"]) is bool)
        if "mode" in patch:
            require(isinstance(patch["mode"], str) and patch["mode"] in {"guided", "assisted"})
    elif kind == "learning.record":
        # The learning ledger is application-only state: a domain plan can never
        # ride along (the exact key set above already rejects "domain").
        require(uuid_ref(change["attempt"]))
        for key in ("course", "task"):
            text = change[key]
            require(
                isinstance(text, str) and bool(text) and len(text.encode("utf-8")) <= 128,
            )
        version = change["expectedRecordVersion"]
        require(version is None or integer(version))
        payload = change["payload"]
        require(
            isinstance(payload, dict) and len(canonical(payload).encode("utf-8")) <= 65536,
        )
        event = change["assistanceEvent"]
        require(
            event is None
            or (
                isinstance(event, dict)
                and set(event) == {"eventId", "payload"}
                and uuid_ref(event["eventId"])
                and isinstance(event["payload"], dict)
                and len(canonical(event["payload"]).encode("utf-8")) <= 16384
            )
        )
    elif kind != "project.restore":
        require(isinstance(change["editor"], str) and bool(change["editor"]))
        require(integer(change["expectedGeneration"]))
        if kind == "draft.save":
            require(integer(change["boundDomainRevision"]))
        elif kind == "draft.restore":
            require(hash_ref(change["checkpointRef"]))
    if "domain" in change:
        value = change["domain"]
        require(isinstance(value, dict) and set(value) == {"base", "plan"})
        require(integer(value["base"]) and isinstance(value["plan"], dict))
        from ontolearn_engine.project.transactions import ProjectTransactions

        ProjectTransactions._plan(value["plan"])
    stable(change)


def _head(project, row):
    if row is None:
        return None
    return DraftHead(
        project,
        row["editor"],
        row["generation"],
        bool(row["present"]),
        row["bound_revision"],
        row["payload"],
    )


def _draft_row(head):
    return {
        "editor": head.editor,
        "generation": head.generation,
        "present": int(head.exists),
        "bound_revision": head.bound_domain_revision,
        "payload": head.content_json,
        "content_hash": head.content_hash,
    }


def _restore_effects(project, change, before, target, domain_after_revision):
    """Whole-project restore of mutable current state; immutable audit stays put."""
    require(target is not None and target["project"] == project)
    require(change["checkpointRef"] == digest(target))
    require(change["expectedMetadataVersion"] == before["metadataVersion"])
    before_meta, target_meta = before["metadata"], target["application"]["metadata"]
    require(
        before_meta["templateRef"] == target_meta["templateRef"]
        and before_meta["origin"] == target_meta["origin"]
    )
    after = deepcopy(before)
    after["metadataVersion"] = next_version(before["metadataVersion"])
    after["metadata"] = {**deepcopy(target_meta)}
    old_cas = [cas("metadata", project, before["metadataVersion"])]
    new_cas = [cas("metadata", project, after["metadataVersion"])]
    before_rows = {row["editor"]: row for row in before["drafts"]}
    target_rows = {row["editor"]: row for row in target["application"]["drafts"]}
    drafts = []
    for editor in sorted(before_rows.keys() | target_rows.keys()):
        head = _head(project, before_rows.get(editor))
        generation = head.generation if head else 0
        next_version(generation)
        target_row = target_rows.get(editor)
        restored = (
            _head(project, target_row)
            if target_row
            else DraftHead(project, editor, 0, False, target["domainRevision"], None)
        )
        plan = restore_draft(
            project,
            editor,
            head,
            restored,
            expected_generation=generation,
            domain_revision=domain_after_revision,
        )
        drafts.append(_draft_row(plan.after))
        old_cas.append(cas("draft", editor, generation))
        new_cas.append(cas("draft", editor, plan.after.generation))
    after["drafts"] = drafts
    before_learning = {row["attempt"]: row for row in before["learningCurrent"]}
    target_learning = {row["attempt"]: row for row in target["application"]["learningCurrent"]}
    # Rows are append-only: a target-only attempt would mean forged future history.
    require(set(target_learning) <= set(before_learning))
    learning = []
    for attempt in sorted(before_learning.keys() | target_learning.keys()):
        row = dict(before_learning[attempt])
        version = row["record_version"]
        row["record_version"] = next_version(version)
        if attempt in target_learning:
            row.update(
                course=target_learning[attempt]["course"],
                task=target_learning[attempt]["task"],
                payload=target_learning[attempt]["payload"],
            )
        else:
            row["payload"] = canonical(
                {"status": RESTORE_WITHDRAWN, "restoredToCheckpointRef": change["checkpointRef"]}
            )
        learning.append(row)
        old_cas.append(cas("learning", attempt, version))
        new_cas.append(cas("learning", attempt, row["record_version"]))
    after["learningCurrent"] = learning
    return after, old_cas, new_cas


def effects(project, change, before, domain_before_revision, domain_after_revision, target=None):
    """Recompute permitted changes; never accept a supplied whole-state replacement."""
    from ontolearn_engine.project.format3 import _application

    check_change(change)
    _application(before, project, domain_before_revision)
    after = deepcopy(before)
    if change["type"] == "checkpoint.create":
        old_cas, new_cas = [], []
    elif change["type"] == "learning.record":
        attempt = change["attempt"]
        rows = {row["attempt"]: row for row in before["learningCurrent"]}
        expected = change["expectedRecordVersion"]
        if expected is None:
            require(attempt not in rows)
            version = 1
        else:
            current = rows.get(attempt)
            if current is None or current["record_version"] != expected:
                raise Conflict("Learning record version changed", category="state")
            version = next_version(expected)
        rows[attempt] = {
            "attempt": attempt,
            "record_version": version,
            "course": change["course"],
            "task": change["task"],
            "payload": canonical(change["payload"]),
        }
        after["learningCurrent"] = [rows[key] for key in sorted(rows)]
        old_cas = (
            cas("learning:init", attempt, 0)
            if expected is None
            else cas("learning", attempt, expected)
        )
        new_cas = cas("learning", attempt, version)
        event = change["assistanceEvent"]
        if event is not None:
            # app_assistance is append-only and immutable; a replayed eventId is
            # rejected instead of silently deduplicated.
            require(event["eventId"] not in {row["event_id"] for row in before["assistanceAudit"]})
            after["assistanceAudit"] = [
                *before["assistanceAudit"],
                {
                    "sequence": next_version(len(before["assistanceAudit"])),
                    "attempt": attempt,
                    "event_id": event["eventId"],
                    "payload": canonical(event["payload"]),
                },
            ]
    elif change["type"] == "project.restore":
        after, old_cas, new_cas = _restore_effects(
            project, change, before, target, domain_after_revision
        )
    elif change["type"] == "metadata":
        version = before["metadataVersion"]
        if change["expectedVersion"] != version:
            raise Conflict("Metadata version changed", category="state")
        after["metadataVersion"] = next_version(version)
        after["metadata"].update(change["patch"])
        old_cas, new_cas = cas("metadata", project, version), cas("metadata", project, version + 1)
    else:
        editor = change["editor"]
        rows = {row["editor"]: row for row in before["drafts"]}
        head = _head(project, rows.get(editor))
        generation = head.generation if head else 0
        next_version(generation)
        kwargs = {
            "expected_generation": change["expectedGeneration"],
            "domain_revision": domain_after_revision,
        }
        if change["type"] == "draft.save":
            plan = save_draft(
                project,
                editor,
                head,
                content=change["content"],
                bound_domain_revision=change["boundDomainRevision"],
                **kwargs,
            )
        elif change["type"] == "draft.delete":
            plan = delete_draft(project, editor, head, **kwargs)
        else:
            require(target is not None and target["project"] == project)
            target_row = next(
                (r for r in target["application"]["drafts"] if r["editor"] == editor), None
            )
            restored = (
                _head(project, target_row)
                if target_row
                else DraftHead(project, editor, 0, False, target["domainRevision"], None)
            )
            plan = restore_draft(project, editor, head, restored, **kwargs)
        rows[editor] = _draft_row(plan.after)
        after["drafts"] = [rows[key] for key in sorted(rows)]
        old_cas, new_cas = cas("draft", editor, generation), cas("draft", editor, generation + 1)
    _application(after, project, domain_after_revision)
    return after, [old_cas], [new_cas]


def construct_plan(store, project, change):
    from ontolearn_engine.project.format3 import application_state
    from ontolearn_engine.project.transactions import ProjectTransactions

    change = stable(change)
    check_change(change)
    revision = store.revision(project)
    before = application_state(store, project)
    domain = None
    if "domain" in change:
        request = change["domain"]
        preview = ProjectTransactions(store).preview(project, request["base"], request["plan"])
        kwargs = json.loads(preview.plan_json)
        kwargs.update(
            preview_identity=preview.identity,
            preview_control={
                "before": json.loads(preview.control_before_json),
                "after": json.loads(preview.control_after_json),
            },
        )
        domain = {
            "base": preview.base,
            "kwargs": kwargs,
            "fingerprint": ProjectTransactions._fingerprint(preview),
            "beforeState": json.loads(preview.before_json),
            "afterState": json.loads(preview.after_json),
            "beforeControl": json.loads(preview.control_before_json),
            "afterControl": json.loads(preview.control_after_json),
        }
    target = None
    if change["type"] in {"draft.restore", "project.restore"}:
        target = store.project_checkpoint(project, change["checkpointRef"])
    if change["type"] == "project.restore":
        # The wire change must never smuggle a domain plan: attachment is derived
        # here from the two authoritative checkpoints, nothing else.
        require("domain" not in change)
        current = store.project_checkpoint(project)
        require(change["checkpointRef"] != digest(current))
        require(digest(current) == change["expectedCheckpointRef"])
        require(current["operationSequence"] == change["expectedOperationSequence"])
        require(current["application"]["metadataVersion"] == change["expectedMetadataVersion"])
        if target["domainSnapshotRef"] != current["domainSnapshotRef"]:
            preview = ProjectTransactions(store).preview(
                project,
                current["domainRevision"],
                {"compensate": {"kind": "restore", "snapshotRef": target["domainSnapshotRef"]}},
            )
            kwargs = json.loads(preview.plan_json)
            kwargs.update(
                preview_identity=preview.identity,
                preview_control={
                    "before": json.loads(preview.control_before_json),
                    "after": json.loads(preview.control_after_json),
                },
            )
            domain = {
                "base": preview.base,
                "kwargs": kwargs,
                "fingerprint": ProjectTransactions._fingerprint(preview),
                "beforeState": json.loads(preview.before_json),
                "afterState": json.loads(preview.after_json),
                "beforeControl": json.loads(preview.control_before_json),
                "afterControl": json.loads(preview.control_after_json),
            }
            change = stable(
                {**change, "domain": {"base": preview.base, "plan": json.loads(preview.plan_json)}}
            )
            check_change(change)
    after, old_cas, new_cas = effects(
        project, change, before, revision, revision + int(domain is not None), target
    )
    return {
        "applicationPlanVersion": 1,
        "project": project,
        "change": change,
        "domain": domain,
        "before": before,
        "after": after,
        "beforeCAS": old_cas,
        "afterCAS": new_cas,
    }


def validate_plan(store, project, plan, domain_before_revision, target=None):
    from ontolearn_engine.project.transactions import ChangePreview, ProjectTransactions

    require(isinstance(plan, dict) and set(plan) == PLAN_KEYS)
    require(type(plan["applicationPlanVersion"]) is int and plan["applicationPlanVersion"] == 1)
    require(plan["project"] == project)
    check_change(plan["change"])
    domain = plan["domain"]
    require((domain is not None) == ("domain" in plan["change"]))
    if domain is not None:
        require(
            isinstance(domain, dict)
            and set(domain)
            == {
                "base",
                "kwargs",
                "fingerprint",
                "beforeState",
                "afterState",
                "beforeControl",
                "afterControl",
            }
        )
        request = plan["change"]["domain"]
        require(
            integer(domain["base"]) and domain["base"] == request["base"] == domain_before_revision
        )
        preview = ChangePreview(
            project,
            domain["base"],
            canonical(request["plan"]),
            canonical(domain["beforeState"]),
            canonical(domain["afterState"]),
            control_before_json=canonical(domain["beforeControl"]),
            control_after_json=canonical(domain["afterControl"]),
        )
        expected = stable(request["plan"])
        expected.update(
            preview_identity=preview.identity,
            preview_control={"before": domain["beforeControl"], "after": domain["afterControl"]},
        )
        require(
            domain["kwargs"] == expected
            and domain["fingerprint"] == ProjectTransactions._fingerprint(preview)
        )
    after, old_cas, new_cas = effects(
        project,
        plan["change"],
        plan["before"],
        domain_before_revision,
        domain_before_revision + int(domain is not None),
        target,
    )
    require(canonical(after) == canonical(plan["after"]))
    require(
        canonical(old_cas) == canonical(plan["beforeCAS"])
        and canonical(new_cas) == canonical(plan["afterCAS"])
    )


def prepared_payload(project_id, actor, plan):
    return {"preparedApplicationVersion": 1, "projectId": project_id, "actor": actor, "plan": plan}


def check_confirmation(store, context):
    """Full binding, including actor, scope/CAS, restore target and domain base."""
    request = context["request"]
    auth = request["authorization"]
    plan = context["plan"]
    required = plan["domain"] is not None or plan["change"]["type"] in {
        "draft.restore",
        "project.restore",
    }
    plan_ref, confirmation_ref = auth["preparedPlanRef"], auth["confirmationRef"]
    require((plan_ref is None) == (confirmation_ref is None))
    if plan_ref is None:
        require(not required)
        return
    require(hash_ref(plan_ref) and uuid_ref(confirmation_ref))
    expected = prepared_payload(context["projectId"], auth["actor"], plan)
    row = store._db.execute(
        "SELECT * FROM job_plans WHERE ref=? AND project=?", (plan_ref, context["projectId"])
    ).fetchone()
    confirmation = store._db.execute(
        "SELECT * FROM job_confirmations WHERE id=? AND project=?",
        (confirmation_ref, context["projectId"]),
    ).fetchone()
    require(row is not None and confirmation is not None)
    base = plan["domain"]["base"] if plan["domain"] else None
    require(row["payload"] == canonical(expected) and digest(expected) == plan_ref)
    require(row["plan_hash"] == digest(plan) and row["base"] == base)
    require(
        row["diff_hash"]
        == digest({"before": plan["before"], "after": plan["after"], "domain": plan["domain"]})
    )
    require(
        confirmation["plan_ref"] == plan_ref
        and confirmation["base"] == base
        and confirmation["plan_hash"] == digest(plan)
        and confirmation["permission"] == "write"
        and confirmation["actor"] == auth["actor"]
    )


def claim_context(store, project, operation):
    from ontolearn_engine.project.format3 import _json

    require(
        store._db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='operation_claims'"
        ).fetchone()
        is not None
    )
    row = store._db.execute(
        "SELECT * FROM operation_claims WHERE operation=?", (operation,)
    ).fetchone()
    require(row is not None and row["kind"] == "application" and row["job"] is None)
    context = _json(row["context"])
    require(isinstance(context, dict) and set(context) == CONTEXT_KEYS)
    require(
        type(context["applicationContextVersion"]) is int
        and context["applicationContextVersion"] == 1
    )
    require(context["project"] == project and context["operationId"] == operation)
    require(context["projectId"] == row["project"] and digest(context) == row["fingerprint"])
    mapping = store._db.execute(
        "SELECT internal FROM public_projects WHERE public=?", (context["projectId"],)
    ).fetchone()
    require(mapping is not None and mapping[0] == project)
    request = context["request"]
    require(isinstance(request, dict) and set(request) == {"change", "authorization"})
    auth = request["authorization"]
    require(
        isinstance(auth, dict)
        and set(auth) == {"actor", "permission", "preparedPlanRef", "confirmationRef"}
    )
    require(uuid_ref(auth["actor"]) and auth["permission"] == "write")
    require(uuid_ref(context["operationId"]) and uuid_ref(context["projectId"]))
    require(canonical(request["change"]) == canonical(context["plan"]["change"]))
    check_confirmation(store, context)
    return context


def allow_domain_marker(store, project, operation, fingerprint):
    context = claim_context(store, project, operation)
    domain = context["plan"]["domain"]
    require(domain is not None and domain["fingerprint"] == fingerprint)
    return context


def receipt(project, operation, kind, sequence, plan, before_ref, after_ref, before_rev, after_rev):
    return {
        "receiptVersion": 1,
        "project": project,
        "operationId": operation,
        "operationKind": kind,
        "operationSequence": sequence,
        "planHash": digest(plan),
        "domainBeforeRevision": before_rev,
        "domainAfterRevision": after_rev,
        "domainMarkerRef": operation if kind == "combined" else None,
        "applicationBeforeCAS": plan["beforeCAS"],
        "applicationAfterCAS": plan["afterCAS"],
        "beforeCheckpointRef": before_ref,
        "afterCheckpointRef": after_ref,
        "committed": True,
    }


def commit(store, project, base, operation, job, supplied, hook):
    """Called only from Store.commit; all state/evidence share its outer transaction."""
    from ontolearn_engine.project.format3 import (
        MAX_VERSION,
        application_state,
        checkpoint,
        receipt_for,
    )

    require(store._target_format == 3 and job is None)
    with store._transaction(hook):
        context = claim_context(store, project, operation)
        require(canonical(supplied) == canonical(context))
        plan = context["plan"]
        previous = store._db.execute(
            "SELECT 1 FROM app_operations WHERE project=? AND operation=?", (project, operation)
        ).fetchone()
        if previous:
            return receipt_for(store, project, operation)
        current = store.project_checkpoint(project)
        domain = plan["domain"]
        require(base == (domain["base"] if domain else None))
        if domain is not None and domain["base"] != current["domainRevision"]:
            raise Conflict(
                "Old projectRevision; re-preview required",
                category="revision",
                params={"expected": domain["base"], "actual": current["domainRevision"]},
            )
        target = (
            store.project_checkpoint(project, plan["change"]["checkpointRef"])
            if (plan["change"]["type"] in {"draft.restore", "project.restore"})
            else None
        )
        validate_plan(store, project, plan, current["domainRevision"], target)
        if canonical(application_state(store, project)) != canonical(plan["before"]):
            raise Conflict("Application preview changed", category="state")
        if plan["change"]["type"] == "project.restore":
            change = plan["change"]
            if (
                digest(current) != change["expectedCheckpointRef"]
                or current["operationSequence"] != change["expectedOperationSequence"]
            ):
                raise Conflict(
                    "Restore head changed; re-preview required",
                    category="revision",
                    params={
                        "expected": change["expectedOperationSequence"],
                        "actual": current["operationSequence"],
                    },
                )
        if current["operationSequence"] >= MAX_VERSION:
            raise Conflict("Application sequence limit", category="state")
        before_ref = digest(current)
        domain_ref = current["domainSnapshotRef"]
        if domain is not None:
            if (
                store.state(project) != domain["beforeState"]
                or store.retirement_control(project) != domain["beforeControl"]
            ):
                raise Conflict("Domain preview changed", category="state")
            marker = store.commit(
                project, domain["base"], operation, None, hook=hook, **domain["kwargs"]
            )
            require(
                store.state(project) == domain["afterState"]
                and store.retirement_control(project) == domain["afterControl"]
            )
            domain_ref = marker["after_snapshot"]
            hook("application_domain")
        kind = plan["change"]["type"]
        if kind == "metadata":
            store._db.execute(
                "UPDATE app_projects SET metadata_version=?,metadata=? WHERE project=?",
                (plan["after"]["metadataVersion"], canonical(plan["after"]["metadata"]), project),
            )
        elif kind == "checkpoint.create":
            pass  # Evidence-only operation: the whole application state is frozen as-is.
        elif kind == "learning.record":
            row = next(
                r
                for r in plan["after"]["learningCurrent"]
                if r["attempt"] == plan["change"]["attempt"]
            )
            store._db.execute(
                "INSERT INTO app_learning VALUES(?,?,?,?,?,?) ON CONFLICT(project,attempt) "
                "DO UPDATE SET record_version=excluded.record_version,course=excluded.course,"
                "task=excluded.task,payload=excluded.payload",
                (
                    project,
                    row["attempt"],
                    row["record_version"],
                    row["course"],
                    row["task"],
                    row["payload"],
                ),
            )
            hook("application_learning_record")
            if plan["change"]["assistanceEvent"] is not None:
                event = next(
                    r
                    for r in plan["after"]["assistanceAudit"]
                    if r["event_id"] == plan["change"]["assistanceEvent"]["eventId"]
                )
                # The FK needs its app_learning row first; app_assistance itself
                # is immutable, so the insert is the one and only appearance.
                store._db.execute(
                    "INSERT INTO app_assistance VALUES(?,?,?,?,?)",
                    (
                        project,
                        event["sequence"],
                        event["attempt"],
                        event["event_id"],
                        event["payload"],
                    ),
                )
                hook("application_learning_assistance")
        elif kind == "project.restore":
            store._db.execute(
                "UPDATE app_projects SET metadata_version=?,metadata=? WHERE project=?",
                (plan["after"]["metadataVersion"], canonical(plan["after"]["metadata"]), project),
            )
            upsert_draft = (
                "INSERT INTO app_drafts VALUES(?,?,?,?,?,?,?) "
                "ON CONFLICT(project,editor) DO UPDATE SET "
                "generation=excluded.generation,present=excluded.present,"
                "bound_revision=excluded.bound_revision,payload=excluded.payload,"
                "content_hash=excluded.content_hash"
            )
            for row in plan["after"]["drafts"]:
                store._db.execute(
                    upsert_draft,
                    (
                        project,
                        row["editor"],
                        row["generation"],
                        row["present"],
                        row["bound_revision"],
                        row["payload"],
                        row["content_hash"],
                    ),
                )
            hook("application_restore_drafts")
            upsert_learning = (
                "INSERT INTO app_learning VALUES(?,?,?,?,?,?) "
                "ON CONFLICT(project,attempt) DO UPDATE SET "
                "record_version=excluded.record_version,course=excluded.course,"
                "task=excluded.task,payload=excluded.payload"
            )
            for row in plan["after"]["learningCurrent"]:
                store._db.execute(
                    upsert_learning,
                    (
                        project,
                        row["attempt"],
                        row["record_version"],
                        row["course"],
                        row["task"],
                        row["payload"],
                    ),
                )
            hook("application_restore_learning")
            # assistanceAudit stays byte-identical: app_assistance is immutable.
        else:
            row = next(
                r for r in plan["after"]["drafts"] if r["editor"] == plan["change"]["editor"]
            )
            store._db.execute(
                "INSERT INTO app_drafts VALUES(?,?,?,?,?,?,?) ON CONFLICT(project,editor) "
                "DO UPDATE SET generation=excluded.generation,present=excluded.present,"
                "bound_revision=excluded.bound_revision,payload=excluded.payload,"
                "content_hash=excluded.content_hash",
                (
                    project,
                    row["editor"],
                    row["generation"],
                    row["present"],
                    row["bound_revision"],
                    row["payload"],
                    row["content_hash"],
                ),
            )
        require(canonical(application_state(store, project)) == canonical(plan["after"]))
        hook("application_state")
        sequence = current["operationSequence"] + 1
        kind = "combined" if domain else "application"
        store._db.execute(
            "INSERT INTO app_operations VALUES(?,?,?,?,?,?)",
            (project, sequence, operation, kind, digest(plan), store.revision(project)),
        )
        store._db.execute(
            "UPDATE app_projects SET operation_sequence=? WHERE project=?", (sequence, project)
        )
        hook("application_sequence")
        after_ref = checkpoint(store, project, domain_ref, sequence)
        hook("application_checkpoint")
        proof = receipt(
            project,
            operation,
            kind,
            sequence,
            plan,
            before_ref,
            after_ref,
            current["domainRevision"],
            store.revision(project),
        )
        store._db.execute(
            "INSERT INTO app_receipts VALUES(?,?,?)", (project, operation, canonical(proof))
        )
        store._db.execute(
            "UPDATE app_projects SET checkpoint=? WHERE project=?", (after_ref, project)
        )
        hook("application_receipt")
        return proof
