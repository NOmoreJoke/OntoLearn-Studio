"""Read immutable versioned input; reset exports data, never writes a project."""

import csv
import hashlib
import io
import json
from copy import deepcopy
from pathlib import Path

VERSION = "prd-v0.6-learning-1"
BASELINES = ("G-base", "G-map-empty", "G-behavior", "E.5")


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
    return {
        "version": VERSION,
        "manifestSha256": file_digest(directory / "manifest.json"),
        "filesVerified": len(files),
        "casesPrepared": ids,
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
