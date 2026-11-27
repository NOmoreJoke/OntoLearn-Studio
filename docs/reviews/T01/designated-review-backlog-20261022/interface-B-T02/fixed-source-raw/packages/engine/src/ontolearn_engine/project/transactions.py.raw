"""Private deterministic project transactions over the approved Store.

No protocol registration, authorization grant, schema, secondary store or writer.
The caller is the trusted application service; user confirmation belongs to T00.
Previews execute the actual Store.commit and always roll back, including snapshots.
"""

import json
from dataclasses import dataclass
from uuid import uuid4

from ontolearn_engine.storage import Conflict, Hook, Store, canonical, digest

PLAN_KEYS = {
    "definitions",
    "remove_definitions",
    "manual",
    "edits",
    "remove",
    "mapping",
    "compensate",
}
CHECKPOINT_REASONS = {"before-agent", "before-run", "guided-stage", "manual"}


class ProjectFault(ValueError):
    """Private fixed failure code, never includes original business values."""

    def __init__(self, code: str, resources: tuple[str, ...] = ()):
        super().__init__(code)
        self.code = code
        self.resources = resources


@dataclass(frozen=True)
class ChangePreview:
    """Canonical strings prevent nested caller mutation after preview."""

    project: str
    base: int
    plan_json: str
    before_json: str
    after_json: str
    intent: str = "change"
    target: str | None = None
    overwritten_operations: tuple[str, ...] = ()
    control_before_json: str = "[]"
    control_after_json: str = "[]"

    @property
    def identity(self) -> str:
        return digest(
            {
                "project": self.project,
                "base": self.base,
                "plan": json.loads(self.plan_json),
                "before": json.loads(self.before_json),
                "after": json.loads(self.after_json),
                "intent": self.intent,
                "target": self.target,
                "overwrittenOperations": self.overwritten_operations,
                "controlBefore": json.loads(self.control_before_json),
                "controlAfter": json.loads(self.control_after_json),
            }
        )

    @property
    def diff(self) -> list[dict]:
        changes = state_diff(json.loads(self.before_json), json.loads(self.after_json))
        before = {tuple(key) for key in json.loads(self.control_before_json)}
        after = {tuple(key) for key in json.loads(self.control_after_json)}
        changes.extend(
            {
                "resource": ["definition-status", *key],
                "before": "已撤回" if key in before else None,
                "after": "已撤回" if key in after else None,
            }
            for key in sorted(before ^ after)
        )
        return changes

    @property
    def summary(self) -> str:
        changes = self.diff
        added = sum(item["before"] is None for item in changes)
        removed = sum(item["after"] is None for item in changes)
        return f"新增 {added} 项，修改 {len(changes) - added - removed} 项，移除 {removed} 项"


def _records(state: dict) -> dict[tuple[str, ...], object]:
    return {
        **{("definition", d["layer"], d["id"]): d for d in state["definitions"]},
        **{("fact", f["id"]): f for f in state["facts"]},
        **{("mappingState", key): value for key, value in state["mappingState"].items()},
    }


def state_diff(before: dict, after: dict) -> list[dict]:
    old, new = _records(before), _records(after)
    return [
        {"resource": list(key), "before": old.get(key), "after": new.get(key)}
        for key in sorted(old.keys() | new.keys())
        if old.get(key) != new.get(key)
    ]


class _PreviewRollback(Exception):
    pass


class ProjectTransactions:
    def __init__(self, store: Store):
        self.store = store

    def _control(self, project: str) -> str:
        return canonical(self.store.retirement_control(project))

    @staticmethod
    def _plan(plan: dict) -> dict:
        if not isinstance(plan, dict) or set(plan) - PLAN_KEYS:
            raise ValueError("Unsupported project plan")
        # Canonical encode both rejects NaN and disconnects all mutable references.
        return json.loads(canonical(plan))

    @staticmethod
    def _fingerprint(preview: ChangePreview) -> str:
        plan = json.loads(preview.plan_json)
        complete = {
            "base": preview.base,
            **{
                key: plan.get(key)
                for key in ("definitions", "manual", "edits", "remove", "mapping")
            },
        }
        if plan.get("remove_definitions") is not None:
            complete["remove_definitions"] = plan["remove_definitions"]
        if plan.get("compensate") is not None:
            complete["compensate"] = plan["compensate"]
        complete["preview_identity"] = preview.identity
        complete["preview_control"] = {
            "before": json.loads(preview.control_before_json),
            "after": json.loads(preview.control_after_json),
        }
        return digest(complete)

    def preview(
        self,
        project: str,
        base: int,
        plan: dict,
        *,
        intent: str = "change",
        target: str | None = None,
        overwritten_operations: tuple[str, ...] = (),
    ) -> ChangePreview:
        plan = self._plan(plan)
        # Outermost transaction is deliberately rolled back, never committed.
        try:
            with self.store._transaction():
                before = self.store.state(project)
                control_before = self._control(project)
                self.store.commit(project, base, str(uuid4()), str(uuid4()), **plan)
                after = self.store.state(project)
                control_after = self._control(project)
                raise _PreviewRollback
        except _PreviewRollback:
            return ChangePreview(
                project,
                base,
                canonical(plan),
                canonical(before),
                canonical(after),
                intent,
                target,
                overwritten_operations,
                control_before,
                control_after,
            )

    def reconcile(self, preview: ChangePreview, operation: str, job: str) -> dict:
        """Read only. Missing marker never authorizes an unfenced automatic retry."""
        marker = self.store.marker(preview.project, operation)
        if marker is None:
            return {"status": "uncommitted", "marker": None}
        if marker["job"] != job or marker["fingerprint"] != self._fingerprint(preview):
            raise Conflict("Operation identity mismatch", category="identity")
        before = self._snapshot(preview.project, marker["before_snapshot"])
        after = self._snapshot(preview.project, marker["after_snapshot"])
        if (
            canonical(before["state"]) != preview.before_json
            or canonical(after["state"]) != preview.after_json
            or json.loads(marker["plan"]).get("preview_control")
            != {
                "before": json.loads(preview.control_before_json),
                "after": json.loads(preview.control_after_json),
            }
        ):
            raise Conflict("Preview evidence mismatch", category="identity")
        return {"status": "committed", "marker": marker}

    def commit(
        self,
        preview: ChangePreview,
        operation: str,
        job: str,
        *,
        confirmed_preview: str,
        hook: Hook = lambda _: None,
    ) -> dict:
        """Trusted caller supplies the exact confirmed digest, not a new permission."""
        if confirmed_preview != preview.identity:
            raise ProjectFault("CONFIRMATION_MISMATCH")
        with self.store._transaction(hook):
            existing = self.reconcile(preview, operation, job)
            if existing["status"] == "committed":
                return existing["marker"]
            if (
                canonical(self.store.state(preview.project)) != preview.before_json
                or self._control(preview.project) != preview.control_before_json
            ):
                raise Conflict("Preview input changed", category="revision")
            marker = self.store.commit(
                preview.project,
                preview.base,
                operation,
                job,
                hook=hook,
                preview_identity=preview.identity,
                preview_control={
                    "before": json.loads(preview.control_before_json),
                    "after": json.loads(preview.control_after_json),
                },
                **json.loads(preview.plan_json),
            )
            if (
                canonical(self.store.state(preview.project)) != preview.after_json
                or self._control(preview.project) != preview.control_after_json
            ):
                raise ProjectFault("PREVIEW_RESULT_MISMATCH")
        return marker

    def checkpoint(self, project: str, reason: str) -> dict:
        if reason not in CHECKPOINT_REASONS:
            raise ValueError("Unsupported checkpoint reason")
        ref = self.store.snapshot(project)
        snap = self.store.load_snapshot(ref)
        return {"snapshotRef": ref, "projectRevision": snap["projectRevision"], "reason": reason}

    def _snapshot(self, project: str, identity: str) -> dict:
        # Store validates project identity, content hash, shape, RDF and ownership.
        return self.store._project_snapshot(identity, project)

    def preview_undo(self, project: str, operation: str) -> ChangePreview:
        with self.store._transaction():
            marker = self.store.marker(project, operation)
            if marker is None:
                raise KeyError("Missing ChangeSet")
            if not marker["before_snapshot"] or not marker["after_snapshot"]:
                raise ProjectFault("UNDO_EVIDENCE_MISSING")
            before = self._snapshot(project, marker["before_snapshot"])["state"]
            after = self._snapshot(project, marker["after_snapshot"])["state"]
            current = self.store.state(project)
            current_records = _records(current)
            changes = state_diff(before, after)
            conflicts = tuple(
                ":".join(item["resource"])
                for item in changes
                if current_records.get(tuple(item["resource"])) != item["after"]
            )
            if conflicts:
                raise ProjectFault("UNDO_CONFLICT", conflicts)
            try:
                return self.preview(
                    project,
                    self.store.revision(project),
                    {"compensate": {"kind": "undo", "operation": operation}},
                    intent="undo",
                    target=operation,
                )
            except Conflict as error:
                if error.category == "state":
                    raise ProjectFault("UNDO_CONFLICT") from error
                raise

    def preview_restore(self, project: str, snapshot: str) -> ChangePreview:
        with self.store._transaction():
            target = self._snapshot(project, snapshot)
            base = self.store.revision(project)
            if target["projectRevision"] > base:
                raise ProjectFault("RESTORE_FUTURE_SNAPSHOT")
            later = []
            after_revision = target["projectRevision"]
            while True:
                page = self.store.operation_list(
                    project, after_revision=after_revision, through_revision=base
                )
                later.extend(item["operation"] for item in page["operations"])
                if page["nextAfterRevision"] is None:
                    break
                after_revision = page["nextAfterRevision"]
            return self.preview(
                project,
                base,
                {"compensate": {"kind": "restore", "snapshotRef": snapshot}},
                intent="restore",
                target=snapshot,
                overwritten_operations=tuple(later),
            )
