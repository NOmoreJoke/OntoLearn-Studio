"""Private deterministic project transactions over the approved Store.

No protocol registration, authorization grant, schema, secondary store or writer.
The caller is the trusted application service; user confirmation belongs to T00.
Previews execute the actual Store.commit and always roll back, including snapshots.
"""

import json
from dataclasses import dataclass
from uuid import uuid4

from ontolearn_engine.storage import Conflict, Hook, Store, canonical, digest

PLAN_KEYS = {"definitions", "remove_definitions", "manual", "edits", "remove", "mapping"}
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
            }
        )

    @property
    def diff(self) -> list[dict]:
        return state_diff(json.loads(self.before_json), json.loads(self.after_json))

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
        complete["preview_identity"] = preview.identity
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
                self.store.commit(project, base, str(uuid4()), str(uuid4()), **plan)
                after = self.store.state(project)
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
            if canonical(self.store.state(preview.project)) != preview.before_json:
                raise Conflict("Preview input changed", category="revision")
            marker = self.store.commit(
                preview.project,
                preview.base,
                operation,
                job,
                hook=hook,
                preview_identity=preview.identity,
                **json.loads(preview.plan_json),
            )
            if canonical(self.store.state(preview.project)) != preview.after_json:
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
            # Restore only this operation's changed records; unrelated later edits survive.
            desired_records = _records(current)
            for item in changes:
                key = tuple(item["resource"])
                if item["before"] is None:
                    desired_records.pop(key, None)
                else:
                    desired_records[key] = item["before"]
            desired = {
                "definitions": [
                    v for k, v in sorted(desired_records.items()) if k[0] == "definition"
                ],
                "facts": [v for k, v in sorted(desired_records.items()) if k[0] == "fact"],
                "mappingState": {
                    k[1]: v for k, v in sorted(desired_records.items()) if k[0] == "mappingState"
                },
            }
            plan = _restore_plan(current, desired)
            return self.preview(
                project, self.store.revision(project), plan, intent="undo", target=operation
            )

    def preview_restore(self, project: str, snapshot: str) -> ChangePreview:
        with self.store._transaction():
            target = self._snapshot(project, snapshot)
            base = self.store.revision(project)
            if target["projectRevision"] > base:
                raise ProjectFault("RESTORE_FUTURE_SNAPSHOT")
            # Read immutable existing evidence only. A public listing API is a T00 handoff.
            later = tuple(
                row[0]
                for row in self.store._db.execute(
                    "SELECT operation FROM commits WHERE project=? AND revision>? "
                    "ORDER BY revision",
                    (project, target["projectRevision"]),
                )
            )
            plan = _restore_plan(self.store.state(project), target["state"])
            return self.preview(
                project, base, plan, intent="restore", target=snapshot, overwritten_operations=later
            )


def _restore_plan(current: dict, desired: dict) -> dict:
    """Exact inverse if expressible in the approved commit API; otherwise stop."""
    definitions, withdrawn, manual, edits, remove = [], [], [], {}, []
    unsupported = []
    for item in state_diff(current, desired):
        key, old, new = item["resource"], item["before"], item["after"]
        if key[0] == "definition":
            if new is None:
                withdrawn.append({"layer": key[1], "id": key[2]})
            else:
                definitions.append(
                    {"layer": key[1], "id": key[2], "value": json.loads(new["payload"])}
                )
        elif key[0] == "mappingState":
            unsupported.append(":".join(key))
        elif old is not None and new is not None:
            if {k: v for k, v in old.items() if k != "object"} != {
                k: v for k, v in new.items() if k != "object"
            } or new["object"] is None:
                unsupported.append(":".join(key))
            else:
                edits[key[1]] = new["object"]
        elif new is None:
            if old["owner"] is not None:
                unsupported.append(":".join(key))
            else:
                remove.append(key[1])
        elif new["owner"] is not None or new["id"] != digest(
            [new["subject"], new["predicate"], new["object"]]
        ):
            unsupported.append(":".join(key))
        else:
            manual.append({k: new[k] for k in ("id", "subject", "predicate", "object")})
    if unsupported:
        raise ProjectFault("RESTORE_REQUIRES_STORE_SUPPORT", tuple(unsupported))
    return {
        "definitions": definitions,
        "remove_definitions": withdrawn,
        "manual": manual,
        "edits": edits,
        "remove": remove,
    }
