"""Pure offline learning reducer. Actual approved tools are injected by their owner.

This module has no product runtime registration and never accepts model text as
completion. Its private Python adapter surface is not an IPC/public contract.
"""

import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Protocol

from .baselines import file_digest, read_json, verify

ASSISTANCE = ("independent", "partial-hints", "full-demonstration", "agent-full-assistance")

COURSE_VERSION = "offline-course-2"
GLOSSARY_VERSION = "glossary-2"
CHECKS_VERSION = "learning-checks-2"

ONTOLOGY_MODEL_CHECK = "ontology-model"
LX01_CHECK = "LX-01"
LX01_EXTRA_ASSERTED_FEEDBACK = "这样步骤 4 就没有可区分的推导了"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
OWL_CLASS = "<http://www.w3.org/2002/07/owl#Class>"
RDFS_CLASS = "<http://www.w3.org/2000/01/rdf-schema#Class>"
OWL_OBJECT_PROPERTY = "<http://www.w3.org/2002/07/owl#ObjectProperty>"
OWL_DATATYPE_PROPERTY = "<http://www.w3.org/2002/07/owl#DatatypeProperty>"
PERSON_IRI = "urn:ontolearn:learning:Person"
ASSIGNED_TO_IRI = "urn:ontolearn:learning:assignedTo"
PERSON_L01_IRI = "urn:ontolearn:learning:person/L01"
EQUIPMENT_001_IRI = "urn:ontolearn:learning:equipment/001"
ALLOWED_EXTRA_SUBJECTS = (PERSON_IRI, ASSIGNED_TO_IRI, PERSON_L01_IRI)
ALLOWED_EXTRA_PREDICATES = (
    "http://www.w3.org/2000/01/rdf-schema#label",
    "http://www.w3.org/2000/01/rdf-schema#comment",
)
DEVIATION_PERSON_AS_CLASS = "当前练习把具体人员建成了类：类回答‘是哪一类’，个体回答‘是哪一个’。"
DEVIATION_ASSIGNED_TO_DATATYPE = "人员是另一个对象，应使用对象属性。"
REPAIR_GUIDANCE = "请新建修复 ChangeSet 后重新检查；检查只报告偏差，不会自动回滚已提交的修改。"


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


def _triple_key(triple: object) -> tuple[str, str, str] | None:
    if not isinstance(triple, dict):
        return None
    subject = triple.get("subject")
    predicate = triple.get("predicate")
    obj = triple.get("object")
    if not all(isinstance(value, str) and value for value in (subject, predicate, obj)):
        return None
    return (subject, predicate, obj)


def _normalise_query(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().casefold().split())


def compare_ontology_model(payload: object, policy: dict) -> list[str]:
    """Compare the course target against the frozen closed whitelist.

    Triple by triple, never by count. Returns deviation reasons; an empty list
    means the result satisfies the frozen comparison policy.
    """
    reasons: list[str] = []
    if not isinstance(payload, dict):
        return ["实际结果结构不合法：需要包含新增三元组与 removedTriples 的对象"]
    if "removedTriples" not in payload:
        # Strict by contract: a missing field is not an empty removal set.
        return [
            "实际结果缺少 removedTriples 字段：课程契约要求显式传入 removedTriples: []，"
            "缺字段不能判为通过"
        ]
    removed = payload.get("removedTriples")
    if not isinstance(removed, list):
        reasons.append("removedTriples 必须是列表")
    elif removed:
        reasons.append("不能删除既有三元组：本次结果报告了被移除的三元组，删除集合必须为空")
    added = payload.get("addedTriples")
    if not isinstance(added, list):
        reasons.append("实际结果缺少新增三元组列表")
        return reasons
    keys: list[tuple[str, str, str]] = []
    for triple in added:
        key = _triple_key(triple)
        if key is None:
            reasons.append("新增三元组结构不合法：需要 subject、predicate 与 object")
        else:
            keys.append(key)
    present = set(keys)
    # Fixed deviation diagnostics first: they explain the actual mistake.
    if (PERSON_L01_IRI, RDF_TYPE, OWL_CLASS) in present or (
        PERSON_L01_IRI,
        RDF_TYPE,
        RDFS_CLASS,
    ) in present:
        reasons.append(DEVIATION_PERSON_AS_CLASS)
    if (ASSIGNED_TO_IRI, RDF_TYPE, OWL_DATATYPE_PROPERTY) in present:
        reasons.append(DEVIATION_ASSIGNED_TO_DATATYPE)
    alternatives = policy.get("classDeclarationAlternatives", {})
    alternative_subject = alternatives.get("subject", PERSON_IRI)
    alternative_predicate = alternatives.get("predicate", RDF_TYPE)
    alternative_objects = tuple(alternatives.get("exactlyOneOf", (OWL_CLASS, RDFS_CLASS)))
    declared = [
        key
        for key in present
        if key[0] == alternative_subject
        and key[1] == alternative_predicate
        and key[2] in alternative_objects
    ]
    if not declared:
        reasons.append("缺少 Person 的类声明：需要 owl:Class 或 rdfs:Class，二者恰好出现其一")
    elif len(declared) > 1:
        reasons.append(
            "Person 同时声明了 owl:Class 与 rdfs:Class：二者必须恰好出现其一，不能同时出现"
        )
    for required in policy.get("requiredTriples", []):
        key = _triple_key(required)
        if key is None:
            reasons.append("比较政策中的目标三元组结构不合法")
            continue
        if key[0] == alternative_subject and key[1] == alternative_predicate:
            continue  # Covered by the exactly-one class declaration rule above.
        if key not in present:
            reasons.append(f"缺少目标三元组：{key[0]} {key[1]} {key[2]}")
    allowed_subjects = tuple(policy.get("allowedExtraTriples", {}).get("subjects", ()))
    allowed_predicates = tuple(policy.get("allowedExtraTriples", {}).get("predicates", ()))
    for key in sorted(present):
        if key in declared:
            continue
        if any(
            key[0] == required[0] and key[1] == required[1] and key[2] == required[2]
            for required in (
                _triple_key(item)
                for item in policy.get("requiredTriples", [])
                if _triple_key(item) is not None
            )
        ):
            continue
        if key[0] in allowed_subjects and key[1] in allowed_predicates:
            continue
        reasons.append(
            f"白名单之外的新增：{key[0]} {key[1]} {key[2]}"
            "（只允许对 Person、assignedTo、person/L01 额外新增 rdfs:label 或 rdfs:comment）"
        )
    if reasons:
        reasons.append(REPAIR_GUIDANCE)
    return reasons


def compare_lx01(payload: object, expected: dict) -> list[str]:
    """Compare the LX-01 course-extension answer against the frozen expectation.

    The owner evidence carries the learner's selectedOrigins together with the
    origins actually derivable from the current persisted project state and any
    person-type assertion that destroys the distinguishable derivation. The
    four real-run step flags (pre-repair reasoning, SHACL before/after, the
    repaired run) come from the persisted learning host only; a payload
    missing any of them is structurally invalid rather than silently passing.
    The answer never travels through learningObservation.
    """
    if not isinstance(payload, dict) or not {
        "selectedOrigins",
        "actualOrigins",
        "extraAssertedPersons",
    } <= set(payload):
        return [
            "LX-01 实际结果结构不合法：需要 selectedOrigins、actualOrigins 与 extraAssertedPersons"
        ]
    if payload["extraAssertedPersons"]:
        return [LX01_EXTRA_ASSERTED_FEEDBACK + "；请撤销该 ChangeSet 或新建 attempt 后重做步骤 3–4"]
    wanted = expected.get("selectedOrigins")
    if not isinstance(wanted, dict):
        return ["LX-01 固定预期缺少 selectedOrigins"]
    if set(payload) != {
        "selectedOrigins",
        "actualOrigins",
        "extraAssertedPersons",
        "repairAssertionsMatch",
        "step1DerivedMatch",
        "shaclStepsVerified",
        "step4DerivedMatch",
    }:
        return [
            "LX-01 实际结果结构不合法：需要 selectedOrigins、actualOrigins、"
            "extraAssertedPersons、repairAssertionsMatch、step1DerivedMatch、"
            "shaclStepsVerified 与 step4DerivedMatch"
        ]
    if not payload["repairAssertionsMatch"]:
        return [
            "需要修复：修复集合必须恰好是 002 assignedTo person/L02 与 003 assignedTo person/L01"
        ]
    if not (
        payload["step1DerivedMatch"]
        and payload["shaclStepsVerified"]
        and payload["step4DerivedMatch"]
    ):
        return [
            "请完整完成 LX-01 步骤 1–4：前置推理、assignedTo 独立必填"
            " SHACL 修复前后校验及修复后推理"
        ]
    reasons: list[str] = []
    if payload["actualOrigins"] != wanted:
        reasons.append(
            "当前项目推导/断言来源与 LX-01 完成状态不一致："
            "请确认步骤 3 的修复断言恰好为两条固定三元组后重跑推理"
        )
    if payload["selectedOrigins"] != wanted:
        reasons.append("selectedOrigins 与固定预期不同，且必须与真实工具给出的依据一致")
    return reasons


class LearningService:
    def __init__(self, root: Path, tools: ApprovedTools | None = None):
        verify(root)
        self.root = root
        self.course = read_json(root / "content/learning/course.json")
        self.glossary = read_json(root / "content/learning/glossary.json")
        self.checks = read_json(root / "content/learning/checks.json")["checks"]
        self.tasks = {task["id"]: task for task in self.course["tasks"]}
        if len(self.tasks) != len(self.course["tasks"]):
            raise ValueError("Duplicate learning task")
        self.readings: dict[str, dict] = {}
        self.task_readings: dict[str, tuple[str, ...]] = {}
        for task in self.tasks.values():
            if task["next"] is not None and task["next"] not in self.tasks:
                raise ValueError("Unknown next task")
            if [hint["level"] for hint in task["hints"]] != [1, 2, 3, 4]:
                raise ValueError("Four offline hint levels required")
            if not task["checks"] or any(c not in self.checks for c in task["checks"]):
                raise ValueError("Every task needs deterministic result checks")
            mounted = []
            for reading in task.get("readings", []):
                for key in ("id", "title", "sourceRef", "summary", "content"):
                    if not isinstance(reading.get(key), str) or not reading[key].strip():
                        raise ValueError("Mounted reading needs a valid " + key)
                if not isinstance(reading.get("optional"), bool):
                    raise ValueError("Mounted reading needs a boolean optional flag")
                if reading["id"] in self.readings:
                    raise ValueError("Duplicate mounted reading id")
                assessment = reading.get("selfAssessment")
                if assessment is not None:
                    if not isinstance(assessment, list) or not assessment:
                        raise ValueError("Self assessment must be a non-empty list")
                    for item in assessment:
                        option_ids = [option.get("id") for option in item.get("options", [])]
                        if item.get("answerKey") not in option_ids:
                            raise ValueError("Self assessment needs a local fixed answer key")
                self.readings[reading["id"]] = reading
                mounted.append(reading["id"])
            self.task_readings[task["id"]] = tuple(mounted)
        self.manifest_sha256 = file_digest(root / "tests/fixtures/product-baselines/manifest.json")
        self.course_version = self.course.get("version")
        self.glossary_version = self.glossary.get("version")
        self.checks_version = read_json(root / "content/learning/checks.json").get("version")
        if self.course_version != COURSE_VERSION:
            raise ValueError("Course version must be " + COURSE_VERSION)
        if self.glossary_version != GLOSSARY_VERSION:
            raise ValueError("Glossary version must be " + GLOSSARY_VERSION)
        if self.checks_version != CHECKS_VERSION:
            raise ValueError("Checks version must be " + CHECKS_VERSION)
        extensions_path = root / "content/learning/extensions.json"
        self.course_extension_version = None
        self.extensions: dict[str, dict] = {}
        if extensions_path.exists():
            extensions = read_json(extensions_path)
            version = extensions.get("courseExtensionVersion")
            if not isinstance(version, str) or not version.strip():
                raise ValueError("Course extensions need a non-empty courseExtensionVersion")
            self.course_extension_version = version
            cases = extensions.get("extensions", [])
            if not isinstance(cases, list):
                raise ValueError("Course extensions must be a list of extension cases")
            for case in cases:
                if not isinstance(case, dict) or not isinstance(case.get("id"), str):
                    raise ValueError("Course extension case needs an id")
                if "learningObservation" in case:
                    raise ValueError("Course extension case must not carry learningObservation")
                self.extensions[case["id"]] = case
        self.tools = tools

    def explain_term(self, term: str) -> dict:
        from copy import deepcopy

        for entry in self.glossary["entries"]:
            if entry["term"] == term:
                return deepcopy(entry)
        raise ValueError("Unknown glossary term")

    def search_glossary(self, query: str) -> tuple[dict, ...]:
        """Local normalisation and alias matching only; no network and no model.

        Case and whitespace are normalised locally, so "主键", "Primary Key" and
        "PK" all reach the IRI / 稳定身份 card with its boundary text.
        """
        from copy import deepcopy

        text = _normalise_query(query)
        if not text:
            return ()
        scored: list[tuple[int, str, dict]] = []
        for entry in self.glossary["entries"]:
            names = [entry["term"], *entry.get("aliases", [])]
            normalised = [_normalise_query(name) for name in names]
            if any(name == text for name in normalised):
                rank = 0
            elif any(text in name for name in normalised):
                rank = 1
            elif text in _normalise_query(entry.get("plain", "")) or text in _normalise_query(
                entry.get("boundary", "")
            ):
                rank = 2
            else:
                continue
            scored.append((rank, entry["term"], entry))
        scored.sort(key=lambda item: (item[0], item[1]))
        return tuple(deepcopy(entry) for _, _, entry in scored)

    def readings_for(self, task_id: str) -> tuple[dict, ...]:
        """Mounted readings are read-only material: they never affect a score.

        Reading and self-assessment events are recorded by the owner as
        observations; they cannot change operationComplete, assistance or
        independentTransferSuccess.
        """
        from copy import deepcopy

        if task_id not in self.tasks:
            raise ValueError("Unknown task")
        return tuple(deepcopy(self.readings[rid]) for rid in self.task_readings[task_id])

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
            if check_id == ONTOLOGY_MODEL_CHECK:
                policy = self.checks[check_id].get("comparisonPolicy")
                if not isinstance(policy, dict):
                    raise ValueError("ontology-model requires a frozen comparison policy")
                reasons = compare_ontology_model(evidence.payload, policy)
                if reasons:
                    repairs.append(check_id + ": " + "；".join(reasons))
                    status = "needs-repair"
                    continue
                completed.append(check_id)
                continue
            if check_id == LX01_CHECK:
                if check_id not in self.extensions:
                    raise ValueError("LX-01 requires the registered course extension case")
                reasons = compare_lx01(evidence.payload, expected)
                if reasons:
                    repairs.append(check_id + ": " + "；".join(reasons))
                    status = "needs-repair"
                    continue
                completed.append(check_id)
                continue
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

    def report_record(self, attempt: Attempt) -> dict:
        """Whitelisted projection for T10; caller persists it through T01 only.

        The existing projection keys stay unchanged; the bound content versions
        are added so a report can be tied to manifest SHA + courseVersion +
        courseExtensionVersion instead of the unchanged fixture version string.
        """
        return {
            "context": asdict(attempt.context),
            "maxHintLevel": attempt.max_hint,
            "assistance": attempt.assistance,
            "operationComplete": attempt.operation_complete,
            "independentTransferSuccess": attempt.independent_transfer_success,
            "checkStatus": attempt.check_status,
            "evidenceIds": list(attempt.evidence_ids),
            "courseVersion": self.course_version,
            "courseExtensionVersion": self.course_extension_version,
            "manifestSha256": self.manifest_sha256,
        }
