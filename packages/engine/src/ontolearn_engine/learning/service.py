"""Pure offline learning reducer. Actual approved tools are injected by their owner.

This module has no product runtime registration and never accepts model text as
completion. Its private Python adapter surface is not an IPC/public contract.
"""

import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Protocol

from .baselines import read_json, verify

ASSISTANCE = ("independent", "partial-hints", "full-demonstration", "agent-full-assistance")


@dataclass(frozen=True)
class Context:
    project_id: str
    task_id: str
    attempt_id: str
    input_version: str

    def __post_init__(self) -> None:
        if any(not isinstance(v, str) or not v.strip() for v in asdict(self).values()):
            raise ValueError("Explicit project/task/attempt/input identities required")


@dataclass(frozen=True)
class Attempt:
    context: Context
    max_hint: int = 0
    assistance: str = "independent"
    operation_complete: bool = False
    independent_transfer_success: bool = False
    check_status: str = "not-checked"
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if type(self.max_hint) is not int or not 0 <= self.max_hint <= 4:
            raise ValueError("Hint level must be 0..4")
        if self.assistance not in ASSISTANCE:
            raise ValueError("Unknown assistance")
        if self.max_hint and self.assistance == "independent":
            raise ValueError("Hint use cannot be independent")
        if self.max_hint == 4 and self.assistance == "partial-hints":
            raise ValueError("Full demonstration cannot be partial")


@dataclass(frozen=True)
class ToolEvidence:
    """Owner supplies persisted current evidence and assistance provenance.

    The owner must derive assistance from the actual T01/T08 operation ledger,
    including prior attempts affecting this task, rather than UI assertions.
    Synthetic evidence in unit tests proves reducer behavior only.
    """

    evidence_id: str
    context: Context
    check_id: str
    status: str
    payload: dict | None
    assistance: str
    provenance: str


class ApprovedTools(Protocol):
    def execute_check(self, check_id: str, context: Context) -> ToolEvidence: ...


@dataclass(frozen=True)
class Feedback:
    status: str
    completed: tuple[str, ...]
    repairs: tuple[str, ...]
    suggestions: tuple[str, ...]
    knowledge_points: tuple[str, ...]
    evidence_ids: tuple[str, ...]


def _canonical(value: object) -> str:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")
    )


def _normalise(value: object, field: str = "") -> object:
    # RDF collections are sets, whereas events, action traces, rows and rounds
    # carry required order. Sorting retains duplicate multiplicity.
    if isinstance(value, dict):
        return {key: _normalise(item, key) for key, item in value.items()}
    if isinstance(value, list):
        items = [_normalise(item) for item in value]
        if field in {"facts", "assertedFacts", "inferred", "addedTriples", "inputs"}:
            return sorted(items, key=_canonical)
        return items
    return value


def _max_assistance(a: str, b: str) -> str:
    if a not in ASSISTANCE or b not in ASSISTANCE:
        raise ValueError("Unknown assistance")
    return ASSISTANCE[max(ASSISTANCE.index(a), ASSISTANCE.index(b))]


class LearningService:
    def __init__(self, root: Path, tools: ApprovedTools | None = None):
        verify(root)
        self.course = read_json(root / "content/learning/course.json")
        self.glossary = read_json(root / "content/learning/glossary.json")
        self.checks = read_json(root / "content/learning/checks.json")["checks"]
        self.tasks = {task["id"]: task for task in self.course["tasks"]}
        if len(self.tasks) != len(self.course["tasks"]):
            raise ValueError("Duplicate learning task")
        for task in self.tasks.values():
            if task["next"] is not None and task["next"] not in self.tasks:
                raise ValueError("Unknown next task")
            if [hint["level"] for hint in task["hints"]] != [1, 2, 3, 4]:
                raise ValueError("Four offline hint levels required")
            if not task["checks"] or any(c not in self.checks for c in task["checks"]):
                raise ValueError("Every task needs deterministic result checks")
        self.tools = tools

    def explain_term(self, term: str) -> dict:
        from copy import deepcopy

        for entry in self.glossary["entries"]:
            if entry["term"] == term:
                return deepcopy(entry)
        raise ValueError("Unknown glossary term")

    def begin(self, context: Context) -> Attempt:
        if context.task_id not in self.tasks:
            raise ValueError("Unknown task")
        return Attempt(context)

    def hint(self, attempt: Attempt, level: int = 1) -> tuple[Attempt, str]:
        if type(level) is not int or not 1 <= level <= 4:
            raise ValueError("Hint level must be 1..4")
        task = self.tasks[attempt.context.task_id]
        assistance = "full-demonstration" if level == 4 else "partial-hints"
        updated = replace(
            attempt,
            max_hint=max(level, attempt.max_hint),
            assistance=_max_assistance(attempt.assistance, assistance),
            independent_transfer_success=False,
        )
        return updated, task["hints"][level - 1]["text"]

    @staticmethod
    def record_agent_full_assistance(attempt: Attempt) -> Attempt:
        """Owner calls only after accepted actual Agent changes, not on suggestions."""
        return replace(
            attempt,
            assistance="agent-full-assistance",
            operation_complete=False,
            independent_transfer_success=False,
            check_status="rerun-required",
            evidence_ids=(),
        )

    def check(self, attempt: Attempt) -> tuple[Attempt, Feedback]:
        task = self.tasks[attempt.context.task_id]
        completed, repairs, evidence_ids = [], [], []
        assistance = attempt.assistance
        status = "passed"
        for check_id in task["checks"]:
            if self.tools is None:
                repairs.append(check_id + ": 等待批准的实际工具接入")
                status = "pending-dependency"
                continue
            # No blanket exception handler: unexpected owner/programming failures
            # propagate; callers must not overwrite the previous persisted attempt.
            evidence = self.tools.execute_check(check_id, attempt.context)
            if not isinstance(evidence, ToolEvidence):
                raise ValueError("Actual typed tool evidence required")
            if evidence.context != attempt.context or evidence.check_id != check_id:
                repairs.append(check_id + ": 项目、任务、尝试或输入版本不匹配，请重跑")
                status = "rerun-required"
                continue
            if (
                not isinstance(evidence.evidence_id, str)
                or not evidence.evidence_id
                or evidence.provenance != "persisted-domain-tool"
            ):
                repairs.append(check_id + ": 缺少真实工具依据")
                status = "missing-evidence"
                continue
            assistance = _max_assistance(assistance, evidence.assistance)
            evidence_ids.append(evidence.evidence_id)
            if evidence.status != "succeeded":
                repairs.append(check_id + ": 工具未成功或结果已过期，请查看实际记录并重跑")
                status = "tool-not-successful"
                continue
            expected = self.checks[check_id]["expected"]
            if evidence.payload is None or _canonical(_normalise(evidence.payload)) != _canonical(
                _normalise(expected)
            ):
                repairs.append(
                    check_id + ": 实际完整结果与固定预期不同，请核对对象、事实、顺序及依据"
                )
                status = "needs-repair"
                continue
            completed.append(check_id)
        success = len(completed) == len(task["checks"])
        updated = replace(
            attempt,
            assistance=assistance,
            operation_complete=success,
            independent_transfer_success=bool(
                success and task["transfer"] and assistance == "independent"
            ),
            check_status="passed" if success else status,
            evidence_ids=tuple(evidence_ids),
        )
        feedback = Feedback(
            updated.check_status,
            tuple(completed),
            tuple(repairs),
            ("按当前输入版本查看完整实际结果；需要帮助时从概念提示开始。",),
            tuple(task["knowledgePoints"]),
            tuple(evidence_ids),
        )
        return updated, feedback

    @staticmethod
    def report_record(attempt: Attempt) -> dict:
        """Whitelisted projection for T10; caller persists it through T01 only."""
        return {
            "context": asdict(attempt.context),
            "maxHintLevel": attempt.max_hint,
            "assistance": attempt.assistance,
            "operationComplete": attempt.operation_complete,
            "independentTransferSuccess": attempt.independent_transfer_success,
            "checkStatus": attempt.check_status,
            "evidenceIds": list(attempt.evidence_ids),
        }
