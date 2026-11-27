"""Synthetic adapter tests validate the reducer only, never product integration."""

from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest
from ontolearn_engine.learning.baselines import file_digest, read_json
from ontolearn_engine.learning.service import (
    DEVIATION_ASSIGNED_TO_DATATYPE,
    DEVIATION_PERSON_AS_CLASS,
    Attempt,
    Context,
    LearningService,
    ToolEvidence,
)

ROOT = Path(__file__).resolve().parents[3]
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
OWL_CLASS = "<http://www.w3.org/2002/07/owl#Class>"
RDFS_CLASS = "<http://www.w3.org/2000/01/rdf-schema#Class>"
OWL_OBJECT_PROPERTY = "<http://www.w3.org/2002/07/owl#ObjectProperty>"
OWL_DATATYPE_PROPERTY = "<http://www.w3.org/2002/07/owl#DatatypeProperty>"
PERSON = "urn:ontolearn:learning:Person"
ASSIGNED_TO = "urn:ontolearn:learning:assignedTo"
PERSON_L01 = "urn:ontolearn:learning:person/L01"
EQUIPMENT_001 = "urn:ontolearn:learning:equipment/001"
LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
COMMENT = "http://www.w3.org/2000/01/rdf-schema#comment"


def triple(subject, predicate, obj):
    return {"subject": subject, "predicate": predicate, "object": obj}


TARGET_TRIPLES = [
    triple(PERSON, RDF_TYPE, OWL_CLASS),
    triple(ASSIGNED_TO, RDF_TYPE, OWL_OBJECT_PROPERTY),
    triple(PERSON_L01, RDF_TYPE, f"<{PERSON}>"),
    triple(EQUIPMENT_001, ASSIGNED_TO, f"<{PERSON_L01}>"),
]


def ontology_payload(added, removed=()):
    return {
        "addedTriples": list(added),
        "removedTriples": list(removed),
        "unsupportedConstructs": [],
    }


class SyntheticTools:
    """Unit-test adapter: deliberately has no product registration."""

    def __init__(self, checks, transform=lambda value: value, assistance="independent"):
        self.checks = checks
        self.transform = transform
        self.assistance = assistance
        self.calls = []

    def execute_check(self, check_id, context):
        self.calls.append((check_id, context))
        evidence = ToolEvidence(
            "unit-only:" + context.attempt_id + ":" + check_id,
            context,
            check_id,
            "succeeded",
            deepcopy(self.checks[check_id]["expected"]),
            self.assistance,
            "persisted-domain-tool",
        )
        return self.transform(evidence)


def service(transform=lambda e: e, assistance="independent"):
    checks = read_json(ROOT / "content/learning/checks.json")["checks"]
    adapter = SyntheticTools(checks, transform, assistance)
    return LearningService(ROOT, adapter), adapter


def context(task="transfer-repair", attempt="attempt-1", version="input-1"):
    return Context("project-1", task, attempt, version)


def test_no_model_or_tools_still_has_complete_course_hints_terms_and_pending_check():
    learning = LearningService(ROOT)
    assert learning.course["modelRequired"] is False
    assert [t["module"] for t in learning.course["tasks"][:6]] == [
        "本体构建",
        "数据映射",
        "本体查询",
        "质量与推理",
        "行为定义",
        "沙盘预测",
    ]
    task = learning.course["firstTask"]
    visited = []
    while task:
        visited.append(task)
        item = learning.tasks[task]
        assert all(
            item[key] for key in ["goal", "instructions", "completionCondition", "commonErrors"]
        )
        state = learning.begin(context(task))
        for level in [1, 2, 3, 4]:
            state, text = learning.hint(state, level)
            assert text
        task = item["next"]
    assert visited == [t["id"] for t in learning.course["tasks"]]
    attempt, feedback = learning.check(learning.begin(context()))
    assert not attempt.operation_complete
    assert not attempt.independent_transfer_success
    assert feedback.status == "pending-dependency"
    assert feedback.completed == ()
    assert feedback.repairs and feedback.suggestions and feedback.knowledge_points
    assert "没记录不等于" in learning.explain_term("开放世界假设")["plain"]
    assert "不是填写校验" in learning.explain_term("定义域")["technical"]
    assert "SHACL" in learning.explain_term("值域")["technical"]
    with pytest.raises(ValueError, match="Unknown glossary"):
        learning.explain_term("不存在术语")


def test_independent_success_requires_actual_adapter_call_for_every_check():
    learning, adapter = service()
    state, feedback = learning.check(learning.begin(context("mapping")))
    assert state.operation_complete
    assert not state.independent_transfer_success  # A worked core lesson is not a transfer test.
    assert feedback.completed == ("M-01", "M-02")
    assert [call[0] for call in adapter.calls] == ["M-01", "M-02"]
    state, _ = learning.check(learning.begin(context()))
    assert state.operation_complete and state.independent_transfer_success
    assert state.assistance == "independent"


@pytest.mark.parametrize(
    "level,expected",
    [(1, "partial-hints"), (2, "partial-hints"), (3, "partial-hints"), (4, "full-demonstration")],
)
def test_hint_attribution_never_counts_as_independent_transfer(level, expected):
    learning, _ = service()
    state, _ = learning.hint(learning.begin(context()), level)
    state, _ = learning.check(state)
    assert state.operation_complete
    assert not state.independent_transfer_success
    assert state.assistance == expected
    assert state.max_hint == level
    lower, _ = learning.hint(state, 1)
    again, _ = learning.check(lower)
    assert again.assistance == expected
    assert again.max_hint == level
    assert not again.independent_transfer_success


def test_agent_full_assistance_invalidation_mode_switch_and_new_attempt_ledger():
    learning, _ = service(assistance="agent-full-assistance")
    state = learning.record_agent_full_assistance(learning.begin(context()))
    assert not state.operation_complete and state.check_status == "rerun-required"
    state, _ = learning.check(state)
    assert state.operation_complete and not state.independent_transfer_success
    state, _ = learning.hint(state, 1)
    assert state.assistance == "agent-full-assistance"
    # Owner's provenance follows modified data even when the user begins another attempt.
    fresh, _ = learning.check(learning.begin(context(attempt="attempt-2")))
    assert fresh.operation_complete
    assert not fresh.independent_transfer_success
    record = learning.report_record(fresh)
    assert record == {
        "context": {
            "project_id": "project-1",
            "task_id": "transfer-repair",
            "attempt_id": "attempt-2",
            "input_version": "input-1",
        },
        "maxHintLevel": 0,
        "assistance": "agent-full-assistance",
        "operationComplete": True,
        "independentTransferSuccess": False,
        "checkStatus": "passed",
        "evidenceIds": ["unit-only:attempt-2:transfer-repair"],
        "courseVersion": "offline-course-2",
        "courseExtensionVersion": "ext-1",
        "manifestSha256": file_digest(ROOT / "tests/fixtures/product-baselines/manifest.json"),
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("project_id", "other-project"),
        ("task_id", "transfer-classify"),
        ("attempt_id", "old-attempt"),
        ("input_version", "old-version"),
    ],
)
def test_cross_identity_or_stale_results_cannot_mark_complete(field, value):
    learning, _ = service(lambda e: replace(e, context=replace(e.context, **{field: value})))
    state, feedback = learning.check(learning.begin(context()))
    assert not state.operation_complete and not state.independent_transfer_success
    assert feedback.status == "rerun-required"
    assert not feedback.evidence_ids


@pytest.mark.parametrize(
    "status", ["failed", "cancelled", "stale", "historical", "unavailable", "running"]
)
def test_failed_or_noncurrent_tools_never_pass(status):
    learning, _ = service(lambda e: replace(e, status=status))
    state, _ = learning.check(learning.begin(context()))
    assert not state.operation_complete
    assert state.check_status == "tool-not-successful"


@pytest.mark.parametrize(
    "change",
    [
        lambda e: replace(e, payload=None),
        lambda e: replace(e, provenance="model-text"),
        lambda e: replace(e, evidence_id=""),
        lambda e: replace(e, check_id="wrong"),
    ],
)
def test_missing_model_or_wrong_check_evidence_cannot_pass(change):
    learning, _ = service(change)
    state, feedback = learning.check(learning.begin(context()))
    assert not state.operation_complete and feedback.repairs


def test_same_count_wrong_object_and_boolean_number_alias_are_rejected():
    def wrong_object(e):
        if e.check_id == "Q-01":
            e.payload["rows"][0]["alarm"] = "<urn:ontolearn:learning:alarm/A02>"
        return e

    learning, _ = service(wrong_object)
    state, feedback = learning.check(learning.begin(context("query")))
    assert not state.operation_complete
    assert feedback.completed == ("Q-02",)
    learning, _ = service(lambda e: replace(e, payload=e.payload | {"exported": 1}))
    state, _ = learning.check(learning.begin(context("report")))
    assert not state.operation_complete  # True and 1 must not compare equal.


def test_set_order_normalised_but_event_and_action_order_preserved():
    def shuffled(e):
        e.payload["facts"].reverse()
        return e

    learning, _ = service(shuffled)
    state, _ = learning.check(learning.begin(context()))
    assert state.operation_complete

    def wrong_round_order(e):
        if e.check_id == "G-list-01":
            e.payload["capacities"]["3"][0]["completed"].reverse()
        return e

    learning, _ = service(wrong_round_order)
    state, _ = learning.check(learning.begin(context("scenario")))
    assert not state.operation_complete


def test_invalid_input_and_unexpected_adapter_failure_do_not_modify_previous_attempt():
    learning, _ = service()
    state = learning.begin(context())
    for level in [0, 5, True, "4"]:
        with pytest.raises(ValueError):
            learning.hint(state, level)
    with pytest.raises(ValueError):
        Context("", "mapping", "attempt-1", "input-1")
    with pytest.raises(ValueError):
        Attempt(context(), max_hint=4, assistance="partial-hints")
    with pytest.raises(ValueError):
        learning.begin(context("unknown"))

    def failure(_):
        raise RuntimeError("Unit adapter crashed")

    failed, _ = service(failure)
    with pytest.raises(RuntimeError):
        failed.check(state)
    assert state == Attempt(context())


def ontology_service(payload):
    """Adapter that returns the caller supplied ontology-model evidence."""

    def transform(evidence):
        if evidence.check_id == "ontology-model":
            return replace(evidence, payload=deepcopy(payload))
        return evidence

    return service(transform)


def check_ontology(payload):
    learning, _ = ontology_service(payload)
    state, feedback = learning.check(learning.begin(context("business-ontology")))
    return state, feedback


def test_ontology_model_accepts_rdfs_class_and_whitelisted_label_comment():
    added = [
        triple(PERSON, RDF_TYPE, RDFS_CLASS),
        triple(ASSIGNED_TO, RDF_TYPE, OWL_OBJECT_PROPERTY),
        triple(PERSON_L01, RDF_TYPE, f"<{PERSON}>"),
        triple(EQUIPMENT_001, ASSIGNED_TO, f"<{PERSON_L01}>"),
        triple(PERSON, LABEL, '"人员"'),
        triple(PERSON_L01, COMMENT, '"示例人员"'),
    ]
    state, feedback = check_ontology(ontology_payload(added))
    assert state.operation_complete
    assert feedback.status == "passed"
    assert feedback.completed == ("ontology-model",)
    assert not feedback.repairs


def test_ontology_model_rejects_both_class_declarations_at_once():
    added = TARGET_TRIPLES + [triple(PERSON, RDF_TYPE, RDFS_CLASS)]
    state, feedback = check_ontology(ontology_payload(added))
    assert not state.operation_complete
    assert state.check_status == "needs-repair"
    assert any("恰好出现其一" in repair for repair in feedback.repairs)


def test_ontology_model_rejects_missing_removed_triples_field():
    payload = ontology_payload(TARGET_TRIPLES)
    del payload["removedTriples"]
    state, feedback = check_ontology(payload)
    assert not state.operation_complete
    assert any("removedTriples" in repair for repair in feedback.repairs)


def test_ontology_model_rejects_any_removed_triple():
    state, feedback = check_ontology(
        ontology_payload(TARGET_TRIPLES, removed=[triple(PERSON, LABEL, '"人员"')])
    )
    assert not state.operation_complete
    assert any("不能删除既有三元组" in repair for repair in feedback.repairs)


@pytest.mark.parametrize(
    "added",
    [
        TARGET_TRIPLES + [triple(PERSON_L01, RDF_TYPE, "<urn:ontolearn:learning:Equipment>")],
        TARGET_TRIPLES
        + [
            triple(
                "urn:ontolearn:learning:equipment/002",
                ASSIGNED_TO,
                f"<{PERSON_L01}>",
            )
        ],
        TARGET_TRIPLES + [triple("urn:ontolearn:learning:equipment/003", RDF_TYPE, OWL_CLASS)],
        TARGET_TRIPLES + [triple(PERSON, RDF_TYPE, OWL_DATATYPE_PROPERTY)],
        TARGET_TRIPLES + [triple(EQUIPMENT_001, LABEL, '"泵站A"')],
    ],
)
def test_ontology_model_rejects_everything_outside_the_closed_whitelist(added):
    state, feedback = check_ontology(ontology_payload(added))
    assert not state.operation_complete
    assert state.check_status == "needs-repair"
    assert feedback.repairs


def test_ontology_model_reports_person_built_as_class_and_datatype_property():
    state, feedback = check_ontology(
        ontology_payload(
            TARGET_TRIPLES
            + [
                triple(PERSON_L01, RDF_TYPE, OWL_CLASS),
                triple(ASSIGNED_TO, RDF_TYPE, OWL_DATATYPE_PROPERTY),
            ]
        )
    )
    assert not state.operation_complete
    repairs = " ".join(feedback.repairs)
    assert DEVIATION_PERSON_AS_CLASS in repairs
    assert DEVIATION_ASSIGNED_TO_DATATYPE in repairs
    assert "新建修复 ChangeSet" in repairs


def test_ontology_model_missing_target_triple_is_reported():
    state, feedback = check_ontology(ontology_payload(TARGET_TRIPLES[:3]))
    assert not state.operation_complete
    assert any("缺少目标三元组" in repair for repair in feedback.repairs)


def test_mounted_readings_are_read_only_and_never_score():
    learning, _ = service()
    assert learning.course_version == "offline-course-2"
    assert learning.glossary_version == "glossary-2"
    assert learning.checks_version == "learning-checks-2"
    assert learning.course_extension_version == "ext-1"
    assert learning.manifest_sha256 == file_digest(
        ROOT / "tests/fixtures/product-baselines/manifest.json"
    )
    readings = learning.readings_for("business-ontology")
    assert [reading["id"] for reading in readings] == ["business-question"]
    assert readings[0]["optional"] is False
    assert learning.readings_for("scenario")[0]["optional"] is True
    assert learning.readings_for("mapping")[0]["id"] == "mapping-diff-read"
    assert learning.readings_for("query")[0]["id"] == "query-scope-read"
    assert learning.readings_for("behavior")[0]["id"] == "behavior-conflict-read"
    # Reading and self assessment never touch a score or the assistance record.
    state = learning.begin(context("business-ontology"))
    assert state == Attempt(context("business-ontology"))
    for reading in learning.readings_for("business-ontology"):
        for item in reading.get("selfAssessment", []):
            assert item["answerKey"] in [option["id"] for option in item["options"]]
    assert learning.readings_for("business-ontology")[0]["content"]
    with pytest.raises(ValueError, match="Unknown task"):
        learning.readings_for("unknown")


@pytest.mark.parametrize("query", ["主键", "Primary Key", "PK", " primary  key ", "主键 "])
def test_glossary_alias_search_reaches_identity_boundary(query):
    learning = LearningService(ROOT)
    matches = learning.search_glossary(query)
    assert matches
    assert matches[0]["term"] == "IRI / 稳定身份"
    assert "Palantir 主键 ≠ 本软件 IRI" in matches[0]["boundary"]
    assert "主键" in matches[0]["aliases"]
    assert learning.search_glossary("") == ()
    assert learning.search_glossary("这个词不存在于术语表") == ()
