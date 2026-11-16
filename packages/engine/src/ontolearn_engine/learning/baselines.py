"""Read immutable versioned input; reset exports data, never writes a project."""

import csv
import hashlib
import io
import json
from copy import deepcopy
from pathlib import Path

VERSION = "prd-v0.6-learning-1"
BASELINES = ("G-base", "G-map-empty", "G-behavior", "E.5")

COURSE_VERSION = "offline-course-2"
GLOSSARY_VERSION = "glossary-2"
CHECKS_VERSION = "learning-checks-2"
TASK_COUNT = 9
# S0 §2: exactly five mounted readings; only the scenario one is optional.
REQUIRED_READINGS = {
    "business-ontology": ("business-question", False),
    "mapping": ("mapping-diff-read", False),
    "query": ("query-scope-read", False),
    "behavior": ("behavior-conflict-read", False),
    "scenario": ("scenario-read", True),
}
# S0 §3.2 / S0 §8: reading text must not disclose the practice answer.
READING_FORBIDDEN_FRAGMENTS = (
    "urn:ontolearn:learning:Person",
    "urn:ontolearn:learning:assignedTo",
    "urn:ontolearn:learning:person/L01",
    "owl:Class",
    "owl:ObjectProperty",
    "rdfs:Class",
)


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    def invalid_constant(_: str) -> None:
        raise ValueError("Non-finite JSON number")

    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_unique_object,
        parse_constant=invalid_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("JSON object required")
    return value


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_file(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("Repository-relative manifest path required")
    path = root / relative
    if ".." in Path(relative).parts or path.is_symlink():
        raise ValueError("Unsafe manifest path")
    if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("Manifest file missing or outside repository")
    return path


def _require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Non-empty text required: " + label)
    return value


def _verify_course(root: Path) -> dict:
    course = read_json(root / "content/learning/course.json")
    if course.get("version") != COURSE_VERSION:
        raise ValueError("Course version must be " + COURSE_VERSION)
    if course.get("firstTask") != "business-ontology":
        raise ValueError("Course first task must stay business-ontology")
    tasks = course.get("tasks")
    if not isinstance(tasks, list) or len(tasks) != TASK_COUNT:
        raise ValueError(f"Course must keep exactly {TASK_COUNT} practical tasks")
    task_ids = [task["id"] for task in tasks]
    if len(set(task_ids)) != TASK_COUNT:
        raise ValueError("Duplicate learning task")
    reading_ids: list[str] = []
    for task in tasks:
        identifier = _require_text(task.get("id"), "task id")
        checks = task.get("checks")
        if (
            not isinstance(checks, list)
            or not checks
            or not all(isinstance(c, str) for c in checks)
        ):
            raise ValueError("Every task needs deterministic result checks: " + identifier)
        hints = task.get("hints")
        if not isinstance(hints, list) or [h.get("level") for h in hints] != [1, 2, 3, 4]:
            raise ValueError("Four offline hint levels required: " + identifier)
        for key in ("goal", "instructions", "completionCondition"):
            _require_text(task.get(key), identifier + "." + key)
        if not isinstance(task.get("commonErrors"), list) or not task["commonErrors"]:
            raise ValueError("Common errors required: " + identifier)
        # Reading material lives in readings[], never inside the task object.
        for forbidden in ("content", "selfAssessment", "reading", "readingsContent"):
            if forbidden in task:
                raise ValueError("Reading material must not be inlined in task: " + identifier)
        for reading in task.get("readings", []):
            if not isinstance(reading, dict):
                raise ValueError("Reading entry must be an object: " + identifier)
            reading_id = _require_text(reading.get("id"), identifier + " reading id")
            for key in ("title", "sourceRef", "summary", "content"):
                _require_text(reading.get(key), reading_id + "." + key)
            if not isinstance(reading.get("optional"), bool):
                raise ValueError("Reading optional flag must be boolean: " + reading_id)
            if reading_id in task_ids:
                raise ValueError("Reading must not masquerade as a task: " + reading_id)
            reading_ids.append(reading_id)
            assessment = reading.get("selfAssessment")
            if assessment is not None:
                if not isinstance(assessment, list) or not assessment:
                    raise ValueError("Self assessment must be a non-empty list: " + reading_id)
                for item in assessment:
                    if not isinstance(item, dict):
                        raise ValueError("Self assessment item must be an object: " + reading_id)
                    _require_text(item.get("question"), reading_id + " question")
                    _require_text(item.get("explanation"), reading_id + " explanation")
                    options = item.get("options")
                    if not isinstance(options, list) or len(options) < 2:
                        raise ValueError("Self assessment needs options: " + reading_id)
                    option_ids = []
                    for option in options:
                        if not isinstance(option, dict):
                            raise ValueError(
                                "Self assessment option must be an object: " + reading_id
                            )
                        option_ids.append(
                            _require_text(option.get("id"), reading_id + " option id")
                        )
                        _require_text(option.get("text"), reading_id + " option text")
                    answer_key = _require_text(item.get("answerKey"), reading_id + " answerKey")
                    if answer_key not in option_ids:
                        raise ValueError(
                            "Self assessment answer key must be a local fixed key: " + reading_id
                        )
    if len(set(reading_ids)) != len(reading_ids):
        raise ValueError("Duplicate reading id")
    for task_id, (reading_id, optional) in REQUIRED_READINGS.items():
        task = next((item for item in tasks if item["id"] == task_id), None)
        if task is None:
            raise ValueError("Missing task for mounted reading: " + task_id)
        mounted = {r["id"]: r for r in task.get("readings", [])}
        if reading_id not in mounted:
            raise ValueError("Missing mounted reading: " + reading_id)
        if mounted[reading_id]["optional"] is not optional:
            raise ValueError("Mounted reading optional flag changed: " + reading_id)
    for task in tasks:
        hint_texts = [h.get("text", "") for h in task.get("hints", []) if h.get("level", 0) >= 2]
        for reading in task.get("readings", []):
            content = reading.get("content", "")
            for fragment in READING_FORBIDDEN_FRAGMENTS:
                if fragment in content:
                    raise ValueError("Reading discloses practice steps: " + reading["id"])
            for text in hint_texts:
                if text and text in content:
                    raise ValueError("Reading repeats a level 2+ hint: " + reading["id"])
    return {"courseVersion": COURSE_VERSION, "tasks": TASK_COUNT, "readings": len(reading_ids)}


def _verify_glossary(root: Path) -> dict:
    glossary = read_json(root / "content/learning/glossary.json")
    if glossary.get("version") != GLOSSARY_VERSION:
        raise ValueError("Glossary version must be " + GLOSSARY_VERSION)
    entries = glossary.get("entries")
    if not isinstance(entries, list) or len(entries) != 27:
        raise ValueError("Glossary must keep 23 upgraded terms plus 4 new ones")
    terms = []
    for entry in entries:
        term = _require_text(entry.get("term"), "glossary term")
        terms.append(term)
        for key in ("plain", "example", "technical"):
            _require_text(entry.get(key), term + "." + key)
        _require_text(entry.get("boundary"), term + ".boundary")
        aliases = entry.get("aliases")
        if (
            not isinstance(aliases, list)
            or not aliases
            or not all(isinstance(alias, str) and alias.strip() for alias in aliases)
        ):
            raise ValueError("Glossary aliases must be a non-empty string list: " + term)
        if "equipmentA" in json.dumps(entry, ensure_ascii=False):
            raise ValueError("Glossary example must not use equipmentA: " + term)
    if len(set(terms)) != len(terms):
        raise ValueError("Duplicate glossary term")
    identity = next((e for e in entries if e["term"] == "IRI / 稳定身份"), None)
    if identity is None:
        raise ValueError("Glossary must define IRI / 稳定身份")
    for alias in ("主键", "Primary Key", "PK"):
        if alias not in identity["aliases"]:
            raise ValueError("Glossary identity aliases incomplete: " + alias)
    if "Palantir 主键 ≠ 本软件 IRI" not in identity["boundary"]:
        raise ValueError("Glossary identity boundary must separate Palantir primary key from IRI")
    return {"glossaryVersion": GLOSSARY_VERSION, "entries": len(entries)}


def _verify_checks(root: Path) -> dict:
    checks = read_json(root / "content/learning/checks.json")
    if checks.get("version") != CHECKS_VERSION:
        raise ValueError("Checks version must be " + CHECKS_VERSION)
    model = checks.get("checks", {}).get("ontology-model")
    if not isinstance(model, dict):
        raise ValueError("ontology-model check required")
    expected = model.get("expected")
    if not isinstance(expected, dict) or expected.get("removedTriples") != []:
        raise ValueError("ontology-model expected must declare an empty removedTriples")
    policy = model.get("comparisonPolicy")
    if not isinstance(policy, dict) or policy.get("mode") != "closed-whitelist":
        raise ValueError("ontology-model must freeze a closed whitelist comparison policy")
    alternatives = policy.get("classDeclarationAlternatives", {}).get("exactlyOneOf")
    if alternatives != [
        "<http://www.w3.org/2002/07/owl#Class>",
        "<http://www.w3.org/2000/01/rdf-schema#Class>",
    ]:
        raise ValueError("Class declaration alternatives must stay owl:Class or rdfs:Class")
    return {"checksVersion": CHECKS_VERSION, "comparisonPolicy": "closed-whitelist"}


def _verify_extensions(root: Path, files: dict) -> dict | None:
    path = root / "content/learning/extensions.json"
    if not path.exists():
        return None  # L1 stage: course extensions do not exist yet.
    if "content/learning/extensions.json" not in files:
        raise ValueError("Course extensions must be covered by the fixture manifest")
    value = read_json(path)
    version = value.get("courseExtensionVersion")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Course extensions need a non-empty courseExtensionVersion")
    return {"courseExtensionVersion": version}


def verify(root: Path) -> dict:
    directory = root / "tests/fixtures/product-baselines"
    manifest = read_json(directory / "manifest.json")
    if manifest.get("version") != VERSION or not isinstance(manifest.get("files"), dict):
        raise ValueError("Unsupported fixture manifest")
    files = manifest["files"]
    actual = {
        str(p.relative_to(root))
        for folder in (directory, root / "content/learning")
        for p in folder.rglob("*")
        if p.is_file() and p != directory / "manifest.json"
    }
    if set(files) != actual:
        raise ValueError("Manifest does not cover complete content/fixture file set")
    for relative, expected in files.items():
        if file_digest(checked_file(root, relative)) != expected:
            raise ValueError("Fixture digest mismatch: " + relative)
    source = manifest["source"]
    if file_digest(checked_file(root, source["path"])) != source["sha256"]:
        raise ValueError("PRD source changed; reconcile fixtures before use")
    coverage = read_json(directory / "coverage.json")
    source_text = checked_file(root, source["path"]).read_text(encoding="utf-8")
    if coverage["sourceSha256"] != source["sha256"]:
        raise ValueError("Coverage source mismatch")
    entries = coverage["entries"]
    ids = [entry["id"] for entry in entries]
    cases = read_json(directory / "cases.json")["cases"]
    if len(ids) != 50 or len(set(ids)) != len(ids) or set(ids) != {c["id"] for c in cases}:
        raise ValueError("Complete unique Appendix G coverage required")
    for entry in entries:
        if entry["source"] not in source_text:
            raise ValueError("Coverage differs from PRD")
    if len(cases) != len(ids):
        raise ValueError("Duplicate case identity")
    for case in cases:
        if case["baseline"] not in BASELINES or not case["steps"] or not case["expected"]:
            raise ValueError("Incomplete input or expectation")
        if case["status"] != "input-and-expectation-prepared-runtime-pending":
            raise ValueError("Fixture preparation cannot claim product execution")
        for field in ("baselineVersion", "inputVersion", "ruleVersion", "behaviorVersion"):
            if not isinstance(case.get(field), str) or not case[field]:
                raise ValueError("Versioned case input required")
    rows = list(csv.DictReader(io.StringIO((directory / "equipment.csv").read_text())))
    if rows != [
        {"equipment_id": "001", "equipment_name": "泵站A"},
        {"equipment_id": "002", "equipment_name": "泵站B"},
    ]:
        raise ValueError("Fixed CSV rows or string identities changed")
    course = _verify_course(root)
    glossary = _verify_glossary(root)
    checks = _verify_checks(root)
    extensions = _verify_extensions(root, files)
    return {
        "version": VERSION,
        "manifestSha256": file_digest(directory / "manifest.json"),
        "filesVerified": len(files),
        "casesPrepared": ids,
        "courseVersion": course["courseVersion"],
        "glossaryVersion": glossary["glossaryVersion"],
        "checksVersion": checks["checksVersion"],
        "courseExtensionVersion": extensions["courseExtensionVersion"] if extensions else None,
        "productRuntime": "not-executed",
    }


def reset_input(root: Path, baseline: str) -> dict:
    """Independent reset entry: fresh model export for an approved Store importer.

    No inferred result is preloaded, no SQLite file is touched and no domain
    method is registered. Caller must use approved Store application API.
    """
    if baseline not in BASELINES:
        raise ValueError("Unknown baseline")
    verify(root)
    return deepcopy(read_json(root / "tests/fixtures/product-baselines" / (baseline + ".json")))


def store_seed_plan(root: Path, baseline: str) -> dict:
    """Translate fixed input into the approved base's internal Store plan.

    This is a test-fixture importer, not a business parser or production reset.
    Domain definitions are preserved, never certified executable by this helper.
    """
    from ontolearn_engine.rdf_snapshot import term
    from ontolearn_engine.storage import digest

    data = reset_input(root, baseline)
    versions = {
        key: data[key]
        for key in (
            "fixtureVersion",
            "inputVersion",
            "ruleVersion",
            "behaviorVersion",
            "semanticsVersion",
        )
    }
    definitions = [
        {
            "layer": "ontology",
            "id": baseline + ".ontology",
            "value": {
                "triples": data["ontology"],
                "singleValuedPredicates": data.get("singleValuedPredicates", []),
                "fixtureVersions": versions,
            },
        }
    ]
    for key, layer in (
        ("constraints", "constraint"),
        ("rules", "rule"),
        ("behaviors", "behavior"),
        ("mappings", "mapping"),
        ("queries", "query"),
    ):
        for value in data.get(key, []):
            payload = deepcopy(value)
            if "file" in payload:
                relative = "tests/fixtures/product-baselines/" + payload["file"]
                source = checked_file(root, relative)
                payload["sourceSha256"] = file_digest(source)
                payload["sourceText"] = source.read_text(encoding="utf-8")
            definitions.append({"layer": layer, "id": payload["id"], "value": payload})
    if baseline == "E.5":
        for capacity in (3, 4):
            definitions.append(
                {
                    "layer": "scenario",
                    "id": "E.5-capacity-" + str(capacity),
                    "value": {
                        "fixtureVersions": versions,
                        "maxRounds": data["maxRounds"],
                        "capacityMode": "direct",
                        "capacity": capacity,
                        "initialBacklog": data["initialBacklog"],
                        "events": data["events"],
                        "initialConsumedEvents": [],
                        "initialTriggeredInstances": [],
                        "queueOrder": data["queueOrder"],
                        "orderIdPolicy": data["orderIdPolicy"],
                        "alarmClosurePolicy": data["alarmClosurePolicy"],
                        "eventInjectionPolicy": data["eventInjectionPolicy"],
                    },
                }
            )
    else:
        definitions.append(
            {
                "layer": "scenario",
                "id": baseline + ".initial",
                "value": data["scenario"]
                | {"initialState": data["initialState"], "fixtureVersions": versions},
            }
        )
    manual = []
    for triple in data.get("facts", data.get("initialFacts", [])):
        canonical = triple | {"object": term(triple["object"]).n3()}
        manual.append(
            {
                "id": digest([canonical["subject"], canonical["predicate"], canonical["object"]]),
                **canonical,
            }
        )
    return {"definitions": definitions, "manual": manual}


def seed_test_project(
    root: Path, baseline: str, store: object, project: str, operation: str, job: str
) -> dict:
    """Seed an explicitly created pristine test project through Store.commit only.

    A reused/nonempty project is rejected, never cleared. Caller owns Store and
    its lifecycle; rollback, versions and evidence remain Store responsibilities.
    This function is private test support, with no worker/IPC registration.
    """
    from ontolearn_engine.storage import Store

    if not isinstance(store, Store):
        raise ValueError("Approved internal Store required")
    if store.revision(project) != 0:
        raise ValueError("Reset requires a pristine new test project")
    state = store.state(project)
    if state["definitions"] or state["facts"] or state["mappingState"]:
        raise ValueError("Reset cannot overwrite existing project state")
    plan = store_seed_plan(root, baseline)
    return store.commit(project, 0, operation, job, **plan)
