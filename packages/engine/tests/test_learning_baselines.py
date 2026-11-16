"""Fixture integrity and reset probes, not product-domain acceptance."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from ontolearn_engine.learning.baselines import file_digest, read_json, reset_input, verify
from ontolearn_engine.rdf_snapshot import term
from rdflib import Graph, URIRef

ROOT = Path(__file__).resolve().parents[3]
DIRECTORY = ROOT / "tests/fixtures/product-baselines"
NS = "urn:ontolearn:learning:"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"


def load(name):
    return read_json(DIRECTORY / (name + ".json"))


def test_reset_is_complete_independent_and_no_project_write():
    result = verify(ROOT)
    assert result["productRuntime"] == "not-executed"
    assert set(result["casesPrepared"]) == {
        *[f"M-{n:02}" for n in range(1, 7)],
        "Q-01",
        "Q-02",
        "V-01",
        "O-01",
        *[f"R-{n:02}" for n in range(1, 7)],
        *[f"B-{n:02}" for n in range(1, 12)],
        *[f"A-{n:02}" for n in range(1, 11)],
        *[f"G-list-{n:02}" for n in range(1, 14)],
    }
    first = reset_input(ROOT, "G-base")
    first["facts"].clear()
    assert reset_input(ROOT, "G-base")["facts"] == load("G-base")["facts"]
    assert reset_input(ROOT, "G-map-empty")["facts"] == []
    assert reset_input(ROOT, "G-map-empty")["behaviors"] == []
    with pytest.raises(ValueError, match="Unknown baseline"):
        reset_input(ROOT, "../../storage")


def test_complete_literal_gbase_and_query_file_on_real_rdf_parser():
    base = load("G-base")
    graph = Graph()
    for triple in base["facts"] + base["ontology"]:
        graph.add((URIRef(triple["subject"]), URIRef(triple["predicate"]), term(triple["object"])))
    expected = {
        ("equipment/001", "泵站A"),
        ("equipment/002", "泵站B"),
        ("equipment/003", "备用泵C"),
    }
    assert {
        (str(s).removeprefix(NS), str(o)) for s, o in graph.subject_objects(URIRef(NS + "name"))
    } == expected
    assert {
        (str(s).removeprefix(NS), str(o).removeprefix(NS))
        for s, o in graph.subject_objects(URIRef(NS + "alarm"))
    } == {
        ("equipment/001", "alarm/A01"),
        ("equipment/002", "alarm/A02"),
        ("equipment/003", "alarm/A03"),
    }
    assert {
        (str(s).removeprefix(NS), str(o)) for s, o in graph.subject_objects(URIRef(NS + "level"))
    } == {("alarm/A01", "High"), ("alarm/A02", "High"), ("alarm/A03", "Low")}
    assert {
        (str(s).removeprefix(NS), str(o)) for s, o in graph.subject_objects(URIRef(NS + "status"))
    } == {("alarm/A01", "Open"), ("alarm/A02", "Closed"), ("alarm/A03", "Open")}
    assert len(base["facts"]) == 18  # Above assertions cover all concrete content, not only size.
    assert list(graph.query((DIRECTORY / "unclosed-high.rq").read_text())) == [
        (URIRef(NS + "alarm/A01"),)
    ]
    assert not list(graph.triples((None, URIRef(RDF_TYPE), URIRef(NS + "HighRiskEquipment"))))
    assert base["initialState"] == {
        "orders": [],
        "pendingEvents": [],
        "consumedEvents": [],
        "triggeredInstances": [],
    }


def test_behavior_baseline_extends_all_base_content_and_preserves_false():
    base, behavior = load("G-base"), load("G-behavior")
    assert behavior["facts"][: len(base["facts"])] == base["facts"]
    assert behavior["rules"] == base["rules"]
    assert behavior["constraints"] == base["constraints"]
    assert behavior["scenario"] == {"maxRounds": 1, "capacityMode": "direct", "capacity": 0}
    assert behavior["initialState"]["pendingEvents"] == []
    assert behavior["initialState"]["orders"] == [
        {"id": "W-test", "status": "待处理"},
        {"id": "W-other", "status": "待处理"},
    ]
    p = next(f for f in behavior["facts"] if f["predicate"] == NS + "P")
    assert term(p["object"]).toPython() is False
    assert {b["id"] for b in behavior["behaviors"]} == {
        "B-risk",
        "B-a",
        "B-b",
        "B-multi",
        "X",
        "Y",
        "B-probe",
    }
    rules = {b["id"]: b for b in behavior["behaviors"]}
    assert rules["X"]["priority"] == rules["Y"]["priority"] == 0
    assert rules["Y"]["conditions"] == [{"target": "T1", "property": "P", "equals": False}]
    cases = {c["id"]: c for c in load("cases")["cases"]}
    assert [e["id"] for e in cases["B-10"]["steps"][0]["events"]] == ["E-M4", "E-M3"]
    assert cases["B-10"]["expected"]["actionTrace"] == [
        {"eventId": "E-M4", "behaviorId": "B-multi", "actionIndex": 1},
        {"eventId": "E-M4", "behaviorId": "B-multi", "actionIndex": 2},
        {"eventId": "E-M3", "behaviorId": "B-multi", "actionIndex": 1},
        {"eventId": "E-M3", "behaviorId": "B-multi", "actionIndex": 2},
    ]
    assert cases["B-11"]["expected"]["notifications"] == [
        {"id": "N:E-M5:B-multi", "eventId": "E-M5", "behaviorId": "B-multi"},
        {"id": "N:E-M6:B-multi", "eventId": "E-M6", "behaviorId": "B-multi"},
    ]
    assert cases["B-04"]["expected"]["behaviorBeforeInference"] == []
    assert (
        cases["B-05"]["expected"]["reason"]
        == cases["B-09"]["expected"]["reason"]
        == "competing-write"
    )


def test_e5_literal_sets_from_prd_and_complete_order_history():
    fixture = load("E.5")
    assert [
        (r["created"], r["completed"], r["backlog"], r["backlogCount"], r["completedCount"])
        for r in fixture["expected"]["3"]
    ] == [
        (["W001", "W002", "W003", "W004"], ["W001", "W002", "W003"], ["W004"], 1, 3),
        (["W005", "W006", "W007", "W008"], ["W004", "W005", "W006"], ["W007", "W008"], 2, 6),
        (
            ["W009", "W010", "W011", "W012"],
            ["W007", "W008", "W009"],
            ["W010", "W011", "W012"],
            3,
            9,
        ),
        (
            ["W013", "W014", "W015", "W016"],
            ["W010", "W011", "W012"],
            ["W013", "W014", "W015", "W016"],
            4,
            12,
        ),
    ]
    assert [r["completed"] for r in fixture["expected"]["4"]] == [
        ["W001", "W002", "W003", "W004"],
        ["W005", "W006", "W007", "W008"],
        ["W009", "W010", "W011", "W012"],
        ["W013", "W014", "W015", "W016"],
    ]
    assert [r["backlog"] for r in fixture["expected"]["4"]] == [[], [], [], []]
    assert [r["completedCount"] for r in fixture["expected"]["4"]] == [4, 8, 12, 16]
    for rounds in fixture["expected"].values():
        for result in rounds:
            assert [o["id"] for o in result["orders"]] == [
                f"W{n:03}" for n in range(1, result["round"] * 4 + 1)
            ]
            assert [o["id"] for o in result["orders"] if o["status"] != "已完成"] == result[
                "backlog"
            ]
            assert result["consumedEvents"] == [
                f"E{n:03}" for n in range(1, result["round"] * 4 + 1)
            ]
            current_events = [
                f"E{n:03}" for n in range((result["round"] - 1) * 4 + 1, result["round"] * 4 + 1)
            ]
            assert result["actionTrace"] == [
                {"eventId": event, "behaviorId": "B-risk", "actionIndex": action}
                for event in current_events
                for action in (1, 2)
            ]
            assert result["scheduledFutureEvents"] == [
                f"E{n:03}" for n in range(result["round"] * 4 + 1, 17)
            ]
            for f in result["facts"]:
                term(f["object"])


def test_manifest_rejects_tampering_untracked_missing_and_duplicate_json(tmp_path):
    for relative in ["content/learning", "tests/fixtures/product-baselines", "docs/prd"]:
        shutil.copytree(ROOT / relative, tmp_path / relative)
    assert verify(tmp_path)["productRuntime"] == "not-executed"
    csv_path = tmp_path / "tests/fixtures/product-baselines/equipment.csv"
    saved = csv_path.read_bytes()
    csv_path.write_text("equipment_id,equipment_name\n1,泵站A\n")
    with pytest.raises(ValueError, match="digest mismatch"):
        verify(tmp_path)
    csv_path.write_bytes(saved)
    unknown = csv_path.with_name("unknown.json")
    unknown.write_text("{}")
    with pytest.raises(ValueError, match="complete content"):
        verify(tmp_path)
    unknown.unlink()
    csv_path.unlink()
    with pytest.raises(ValueError, match="complete content"):
        verify(tmp_path)
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"x": 1, "x": 2}')
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        read_json(duplicate)


def test_cli_reset_exports_exact_baseline_and_failure_exits_nonzero():
    command = [sys.executable, str(ROOT / "scripts/verify-product-baselines.py")]
    output = subprocess.run(
        command + ["--reset", "G-map-empty"], capture_output=True, text=True, check=True
    )
    assert json.loads(output.stdout) == load("G-map-empty")
    wrong = subprocess.run(command + ["--reset", "unknown"], capture_output=True, text=True)
    assert wrong.returncode != 0
    assert not wrong.stdout


@pytest.mark.parametrize("baseline", ["G-base", "G-map-empty", "G-behavior", "E.5"])
def test_real_approved_store_rebuild_retains_full_plan_and_rejects_overwrite(tmp_path, baseline):
    from ontolearn_engine.learning.baselines import seed_test_project, store_seed_plan
    from ontolearn_engine.storage import Store, canonical

    store = Store(tmp_path / "test.sqlite")
    try:
        store.create_project("fixture-project")
        plan = store_seed_plan(ROOT, baseline)
        seed_test_project(ROOT, baseline, store, "fixture-project", "reset-1", "reset-job-1")
        state = store.state("fixture-project")
        assert state["definitions"] == sorted(
            [
                {"layer": d["layer"], "id": d["id"], "payload": canonical(d["value"])}
                for d in plan["definitions"]
            ],
            key=lambda d: (d["layer"], d["id"]),
        )
        assert state["facts"] == sorted(
            [
                f | {"owner": None, "source_row": None, "managed_value": None}
                for f in plan["manual"]
            ],
            key=lambda f: f["id"],
        )
        assert store.revision("fixture-project") == 1
        assert all("expected" not in d["payload"] for d in state["definitions"])
        assert state["mappingState"] == {}  # G-map-empty has no fabricated mapping execution.
        with pytest.raises(ValueError, match="pristine"):
            seed_test_project(ROOT, baseline, store, "fixture-project", "reset-2", "reset-job-2")
        assert store.state("fixture-project") == state
    finally:
        store.close()


def test_retracted_mapping_object_keeps_manual_fact_and_transfer_has_no_answer_in_body():
    cases = {c["id"]: c for c in load("cases")["cases"]}
    manual = {"subject": NS + "equipment/002", "predicate": NS + "note", "object": '"手工备注"'}
    assert cases["M-03"]["steps"][1]["facts"] == [manual]
    assert cases["M-03"]["expected"]["manualFacts"] == [manual]
    assert manual in cases["M-03"]["expected"]["facts"]
    assert not any(
        f["subject"] == NS + "equipment/002" and f["predicate"] != NS + "note"
        for f in cases["M-03"]["expected"]["facts"]
    )
    for c in cases.values():
        if c["baseline"] == "E.5":
            assert c["behaviorVersion"] == load("E.5")["behaviorVersion"]
    course = read_json(ROOT / "content/learning/course.json")
    tasks = {t["id"]: t for t in course["tasks"]}
    assert "供水泵" not in tasks["transfer-repair"]["instructions"]
    assert "102" not in tasks["transfer-repair"]["instructions"]
    assert "名称为断言" not in tasks["transfer-classify"]["instructions"]
    assert "201" not in tasks["transfer-repair"]["hints"][3]["text"]
    assert "102" not in tasks["transfer-classify"]["hints"][3]["text"]


def _copy_tree(tmp_path):
    for relative in ["content/learning", "tests/fixtures/product-baselines", "docs/prd"]:
        shutil.copytree(ROOT / relative, tmp_path / relative)


def _write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _refresh_digest(root, relative):
    manifest_path = root / "tests/fixtures/product-baselines/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"][relative] = file_digest(root / relative)
    _write_json(manifest_path, manifest)


def test_learning_content_versions_are_frozen_without_touching_appendix_g():
    result = verify(ROOT)
    assert result["version"] == "prd-v0.6-learning-1"  # Appendix G identity is unchanged.
    assert result["courseVersion"] == "offline-course-2"
    assert result["glossaryVersion"] == "glossary-2"
    assert result["checksVersion"] == "learning-checks-2"
    assert result["courseExtensionVersion"] is None
    assert len(result["casesPrepared"]) == 50


def test_course_readings_and_task_contract_are_verified(tmp_path):
    _copy_tree(tmp_path)
    course_path = tmp_path / "content/learning/course.json"
    course = json.loads(course_path.read_text(encoding="utf-8"))
    assert len(course["tasks"]) == 9
    assert course["firstTask"] == "business-ontology"
    mounted = {
        task["id"]: [reading["id"] for reading in task.get("readings", [])]
        for task in course["tasks"]
    }
    assert mounted["business-ontology"] == ["business-question"]
    assert mounted["mapping"] == ["mapping-diff-read"]
    assert mounted["query"] == ["query-scope-read"]
    assert mounted["behavior"] == ["behavior-conflict-read"]
    assert mounted["scenario"] == ["scenario-read"]
    for task in course["tasks"]:
        assert [hint["level"] for hint in task["hints"]] == [1, 2, 3, 4]
        assert task["checks"]
        for reading in task.get("readings", []):
            assert reading["content"]
            assert reading["sourceRef"]
            assert isinstance(reading["optional"], bool)
    business = next(task for task in course["tasks"] if task["id"] == "business-ontology")
    assert business["steps"][0]["scored"] is False
    assert business["steps"][0]["readingRef"] == "business-question"
    assert "类回答是哪一类，个体回答是哪一个" in business["hints"][0]["text"]
    # A reading may never disclose the practice answer of its task.
    for task in course["tasks"]:
        for reading in task.get("readings", []):
            for fragment in ("urn:ontolearn:learning:", "owl:Class", "owl:ObjectProperty"):
                assert fragment not in reading["content"]

    course["version"] = "offline-course-1"
    _write_json(course_path, course)
    _refresh_digest(tmp_path, "content/learning/course.json")
    with pytest.raises(ValueError, match="Course version"):
        verify(tmp_path)


def test_missing_or_duplicate_readings_are_rejected(tmp_path):
    _copy_tree(tmp_path)
    course_path = tmp_path / "content/learning/course.json"
    course = json.loads(course_path.read_text(encoding="utf-8"))
    for task in course["tasks"]:
        if task["id"] == "business-ontology":
            task["readings"] = []
    _write_json(course_path, course)
    _refresh_digest(tmp_path, "content/learning/course.json")
    with pytest.raises(ValueError, match="Missing mounted reading"):
        verify(tmp_path)

    duplicate_root = tmp_path / "duplicate"
    _copy_tree(duplicate_root)
    course_path = duplicate_root / "content/learning/course.json"
    course = json.loads(course_path.read_text(encoding="utf-8"))
    for task in course["tasks"]:
        if task["id"] == "mapping":
            task["readings"][0]["id"] = "business-question"
    _write_json(course_path, course)
    _refresh_digest(duplicate_root, "content/learning/course.json")
    with pytest.raises(ValueError, match="Duplicate reading id"):
        verify(duplicate_root)


def test_reading_material_may_not_be_inlined_into_a_task(tmp_path):
    _copy_tree(tmp_path)
    course_path = tmp_path / "content/learning/course.json"
    course = json.loads(course_path.read_text(encoding="utf-8"))
    for task in course["tasks"]:
        if task["id"] == "query":
            task["content"] = "阅读正文"
    _write_json(course_path, course)
    _refresh_digest(tmp_path, "content/learning/course.json")
    with pytest.raises(ValueError, match="must not be inlined"):
        verify(tmp_path)


def test_glossary_boundary_alias_and_example_rules_are_enforced(tmp_path):
    _copy_tree(tmp_path)
    glossary_path = tmp_path / "content/learning/glossary.json"
    glossary = json.loads(glossary_path.read_text(encoding="utf-8"))
    assert glossary["version"] == "glossary-2"
    assert len(glossary["entries"]) == 27
    identity = next(e for e in glossary["entries"] if e["term"] == "IRI / 稳定身份")
    assert identity["aliases"] == ["主键", "Primary Key", "PK"]
    assert "Palantir 主键 ≠ 本软件 IRI" in identity["boundary"]
    for entry in glossary["entries"]:
        assert entry["boundary"].strip()
        assert isinstance(entry["aliases"], list) and entry["aliases"]
        assert "equipmentA" not in json.dumps(entry, ensure_ascii=False)

    glossary["entries"][0]["boundary"] = ""
    _write_json(glossary_path, glossary)
    _refresh_digest(tmp_path, "content/learning/glossary.json")
    with pytest.raises(ValueError, match="boundary"):
        verify(tmp_path)

    glossary = json.loads(glossary_path.read_text(encoding="utf-8"))
    glossary["entries"][0]["boundary"] = "边界"
    glossary["entries"][0]["example"] = "equipmentA 是一个设备类。"
    _write_json(glossary_path, glossary)
    _refresh_digest(tmp_path, "content/learning/glossary.json")
    with pytest.raises(ValueError, match="equipmentA"):
        verify(tmp_path)


def test_checks_version_and_closed_whitelist_policy_are_enforced(tmp_path):
    _copy_tree(tmp_path)
    checks_path = tmp_path / "content/learning/checks.json"
    checks = json.loads(checks_path.read_text(encoding="utf-8"))
    assert checks["version"] == "learning-checks-2"
    model = checks["checks"]["ontology-model"]
    assert model["expected"]["removedTriples"] == []
    assert model["comparisonPolicy"]["mode"] == "closed-whitelist"
    assert model["comparisonPolicy"]["classDeclarationAlternatives"]["exactlyOneOf"] == [
        "<http://www.w3.org/2002/07/owl#Class>",
        "<http://www.w3.org/2000/01/rdf-schema#Class>",
    ]
    assert model["comparisonPolicy"]["allowedExtraTriples"]["subjects"] == [
        "urn:ontolearn:learning:Person",
        "urn:ontolearn:learning:assignedTo",
        "urn:ontolearn:learning:person/L01",
    ]
    assert "LX-01" not in checks["checks"]

    checks["checks"]["ontology-model"]["expected"]["removedTriples"] = [
        {
            "subject": "urn:ontolearn:learning:person/L01",
            "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
            "object": "<urn:ontolearn:learning:Person>",
        }
    ]
    _write_json(checks_path, checks)
    _refresh_digest(tmp_path, "content/learning/checks.json")
    with pytest.raises(ValueError, match="removedTriples"):
        verify(tmp_path)


def test_course_extensions_are_optional_but_must_carry_a_version(tmp_path):
    _copy_tree(tmp_path)
    assert not (tmp_path / "content/learning/extensions.json").exists()
    assert verify(tmp_path)["courseExtensionVersion"] is None
    extensions_path = tmp_path / "content/learning/extensions.json"
    extensions_path.write_text(json.dumps({"cases": []}), encoding="utf-8")
    _refresh_digest(tmp_path, "content/learning/extensions.json")
    with pytest.raises(ValueError, match="courseExtensionVersion"):
        verify(tmp_path)
    extensions_path.write_text(
        json.dumps({"courseExtensionVersion": "ext-1", "cases": []}), encoding="utf-8"
    )
    _refresh_digest(tmp_path, "content/learning/extensions.json")
    assert verify(tmp_path)["courseExtensionVersion"] == "ext-1"


def test_appendix_g_fixtures_and_csv_are_not_modified_by_the_course_revision():
    manifest = read_json(ROOT / "tests/fixtures/product-baselines/manifest.json")
    assert manifest["version"] == "prd-v0.6-learning-1"
    for relative, digest in manifest["files"].items():
        if relative.startswith("tests/fixtures/product-baselines/"):
            assert file_digest(ROOT / relative) == digest
    coverage = read_json(ROOT / "tests/fixtures/product-baselines/coverage.json")
    assert len(coverage["entries"]) == 50
    cases = read_json(ROOT / "tests/fixtures/product-baselines/cases.json")["cases"]
    assert len(cases) == 50
    assert not (ROOT / "content/learning/extensions.json").exists()
