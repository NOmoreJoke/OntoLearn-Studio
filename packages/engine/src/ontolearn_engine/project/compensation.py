"""Pure compensation selection/validation, called only inside Store.commit.

No SQL writes. Historical selectors require genuine immutable commit evidence.
"""

import json
from copy import deepcopy

from ontolearn_engine.invalidation import reasons
from ontolearn_engine.storage import Conflict, digest


def _records(state: dict) -> dict[tuple[str, ...], object]:
    return {
        **{("definition", d["layer"], d["id"]): d for d in state["definitions"]},
        **{("fact", f["id"]): f for f in state["facts"]},
        **{("mappingState", k): v for k, v in state["mappingState"].items()},
        **{
            ("retirement", layer, identity): True
            for layer, identity in state.get("retirements", [])
        },
    }


def _changes(before: dict, after: dict) -> set[tuple[str, ...]]:
    old, new = _records(before), _records(after)
    return {key for key in old.keys() | new.keys() if old.get(key) != new.get(key)}


def validate_selector(selector: dict) -> None:
    if not isinstance(selector, dict):
        raise ValueError("Compensation selector required")
    expected = {
        "undo": {"kind", "operation"},
        "restore": {"kind", "snapshotRef"},
    }
    kind = selector.get("kind")
    if not isinstance(kind, str) or kind not in expected or set(selector) != expected[kind]:
        raise ValueError("Unsupported compensation selector")
    key = "operation" if kind == "undo" else "snapshotRef"
    if not isinstance(selector[key], str) or not selector[key]:
        raise ValueError("Compensation identity required")


def trusted_snapshot(store, project: str, identity: str) -> dict:
    snap = store._project_snapshot(identity, project)
    if snap["projectRevision"] > store.revision(project):
        raise Conflict("Future compensation input", category="state")
    current = {
        "project": project,
        "projectRevision": store.revision(project),
        "dependencyVector": store.vector(project),
        "state": store.state(project),
    }
    evidence = store._db.execute(
        "SELECT 1 FROM commits c JOIN commit_evidence e "
        "ON e.project=c.project AND e.operation=c.operation WHERE c.project=? "
        "AND ((e.after_snapshot=? AND c.revision=?) "
        "OR (e.before_snapshot=? AND c.revision=?)) LIMIT 1",
        (project, identity, snap["projectRevision"], identity, snap["projectRevision"] + 1),
    ).fetchone()
    if evidence is None and digest(current) != identity:
        raise Conflict("Snapshot lacks formal evidence", category="state")
    for owner, status in snap["state"]["mappingState"].items():
        expected = reasons(
            {f"mapping:{owner}": status["generatedVersion"]}, snap["dependencyVector"]
        )
        if expected != status["stale"]:
            raise Conflict("Inconsistent mapping snapshot evidence", category="state")
    return snap


def retirement_at(store, project: str, revision: int) -> set[tuple[str, str]]:
    """Reconstruct hidden membership from immutable, complete formal history.

    No new snapshot/schema format. Legacy missing evidence is not guessed.
    Compensation selectors always refer to earlier revisions, making replay acyclic.
    """
    history: dict[int, set[tuple[str, str]]] = {0: set()}
    rows = store._db.execute(
        "SELECT c.*,e.before_snapshot,e.after_snapshot FROM commits c "
        "LEFT JOIN commit_evidence e ON c.project=e.project AND c.operation=e.operation "
        "WHERE c.project=? AND c.revision<=? ORDER BY c.revision",
        # The next operation may be the first exact capture of this older
        # baseline (e.g. a supported v1 project with no earlier commit evidence).
        (project, revision + 1),
    ).fetchall()
    for row in rows:
        previous = history.get(row["revision"] - 1)
        if not row["before_snapshot"] or not row["after_snapshot"]:
            continue  # Keep the gap unknown; a later exact capture may establish a new baseline.
        before = store._project_snapshot(row["before_snapshot"], project)
        after = store._project_snapshot(row["after_snapshot"], project)
        if (
            before["projectRevision"] != row["revision"] - 1
            or after["projectRevision"] != row["revision"]
        ):
            raise Conflict("Retirement history revision mismatch", category="state")
        plan = json.loads(row["plan"])
        if digest(plan) != row["fingerprint"]:
            raise Conflict("Retirement plan integrity mismatch", category="state")
        captured = plan.get("preview_control")
        if captured is not None:
            captured_before = {tuple(key) for key in captured["before"]}
            captured_after = {tuple(key) for key in captured["after"]}
            if previous is not None and previous != captured_before:
                raise Conflict("Retirement capture mismatch", category="state")
            history[row["revision"] - 1] = captured_before
            history[row["revision"]] = captured_after
            continue
        if previous is None:
            continue
        selector = plan.get("compensate")
        if selector is None:
            left = {(d["layer"], d["id"]) for d in before["state"]["definitions"]}
            right = {(d["layer"], d["id"]) for d in after["state"]["definitions"]}
            retired = (previous | (left - right)) - right
        elif selector["kind"] == "restore":
            target = store._project_snapshot(selector["snapshotRef"], project)
            if target["projectRevision"] not in history:
                raise Conflict("Retirement restore history mismatch", category="state")
            retired = set(history[target["projectRevision"]])
        else:
            marker = store.marker(project, selector["operation"])
            if marker is None or marker["revision"] not in history:
                raise Conflict("Retirement undo history mismatch", category="state")
            left = history[marker["revision"] - 1]
            right = history[marker["revision"]]
            retired = (previous - (right - left)) | (left - right)
        history[row["revision"]] = retired
    if revision not in history:
        raise Conflict("Retirement input history unavailable", category="state")
    return set(history[revision])


def _with_retirements(store, project: str, snapshot: dict) -> dict:
    return {
        **snapshot["state"],
        "retirements": sorted(retirement_at(store, project, snapshot["projectRevision"])),
    }


def resolve(store, project: str, selector: dict, current: dict) -> dict:
    """Return full desired state; never mutate current or any persisted record."""
    validate_selector(selector)
    if selector["kind"] == "restore":
        target = trusted_snapshot(store, project, selector["snapshotRef"])
        return deepcopy(_with_retirements(store, project, target))
    marker = store.marker(project, selector["operation"])
    if marker is None:
        raise KeyError("Missing compensation operation")
    if not marker["before_snapshot"] or not marker["after_snapshot"]:
        raise Conflict("Undo evidence unavailable", category="state")
    before = trusted_snapshot(store, project, marker["before_snapshot"])
    after = trusted_snapshot(store, project, marker["after_snapshot"])
    if (
        before["projectRevision"] != marker["revision"] - 1
        or after["projectRevision"] != marker["revision"]
    ):
        raise Conflict("Undo evidence revision mismatch", category="state")
    left_state = _with_retirements(store, project, before)
    right_state = _with_retirements(store, project, after)
    current = {
        **current,
        "retirements": sorted(retirement_at(store, project, store.revision(project))),
    }
    changed = _changes(left_state, right_state)
    old, new, now = _records(left_state), _records(right_state), _records(current)
    conflicts = {key for key in changed if now.get(key) != new.get(key)}
    # Equal values alone do not rule out a later edit and return (ABA).
    later = store._db.execute(
        "SELECT c.operation,e.before_snapshot,e.after_snapshot FROM commits c "
        "LEFT JOIN commit_evidence e ON c.project=e.project AND c.operation=e.operation "
        "WHERE c.project=? AND c.revision>? ORDER BY c.revision",
        (project, marker["revision"]),
    ).fetchall()
    for item in later:
        if not item["before_snapshot"] or not item["after_snapshot"]:
            raise Conflict("Later edit evidence unavailable", category="state")
        left = _with_retirements(
            store, project, trusted_snapshot(store, project, item["before_snapshot"])
        )
        right = _with_retirements(
            store, project, trusted_snapshot(store, project, item["after_snapshot"])
        )
        conflicts.update(changed & _changes(left, right))
    if conflicts:
        raise Conflict("Later edits conflict with undo", category="state")
    for key in changed:
        if key not in old:
            now.pop(key, None)
        else:
            now[key] = deepcopy(old[key])
    return {
        "definitions": [value for key, value in sorted(now.items()) if key[0] == "definition"],
        "facts": [value for key, value in sorted(now.items()) if key[0] == "fact"],
        "retirements": [(key[1], key[2]) for key in sorted(now) if key[0] == "retirement"],
        "mappingState": {
            key[1]: value for key, value in sorted(now.items()) if key[0] == "mappingState"
        },
    }
