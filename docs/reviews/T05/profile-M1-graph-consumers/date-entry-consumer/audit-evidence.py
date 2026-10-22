"""Read fixed Git sources and the small date archive using only stdlib."""

import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path.cwd()


def load(path):
    return json.loads(path.read_bytes())


def identity(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def save(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def git(ref, path):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"])


def triples(raw):
    rows = []
    for line in raw.decode().splitlines():
        if line:
            match = re.fullmatch(r"(_:[^ ]+|<[^>]*>) (<[^>]*>) (.+) \.", line)
            assert match is not None, line
            rows.append(match.groups())
    return rows


controlled = load(HERE / "controlled146.json")
candidate = controlled["candidate"]
assert len(controlled["files"]) == 146
for row in controlled["files"]:
    raw = (ROOT / row["path"]).read_bytes()
    assert identity(raw) == {k: row[k] for k in ("bytes", "sha256")}
    assert raw == git(candidate, row["path"])
    assert raw == git(row["sourceRef"], row["path"])
original = (HERE / "original-test.py.raw").read_bytes()
test = ROOT / "packages/engine/tests/test_profile_M1_graph_consumers.py"
assert len(original) == 58366 and test.read_bytes().startswith(original)
exception = load(HERE / "old-format-exception.json")["exception"]
frozen = load(HERE / "frozen-old474-git.json")
assert len(frozen["files"]) == 474
for row in frozen["files"]:
    blob = subprocess.check_output(["git", "hash-object", row["path"]], text=True).strip()
    assert (
        subprocess.check_output(
            ["git", "rev-parse", f"{frozen['start']}:{row['path']}"], text=True
        ).strip()
        == row["gitBlob"]
    )
    if row["path"] == exception["path"]:
        raw = (ROOT / row["path"]).read_bytes()
        assert identity(raw) == {
            "bytes": exception["expectedLiteralMergedBytes"],
            "sha256": exception["expectedLiteralMergedSHA256"],
        }
    else:
        assert blob == row["gitBlob"], row["path"]
commands = []
for directory in sorted((HERE / "commands").iterdir()):
    invocation, result = load(directory / "invocation.json"), load(directory / "result.json")
    assert invocation["argv"] == result["argv"] and invocation["cwd"] == result["cwd"] == str(ROOT)
    for name, expected in result["streams"].items():
        assert identity((directory / name).read_bytes()) == expected
    commands.append({"tag": directory.name, "result": result})
save("command-ledger.json", {"allRawStreamsVerified": True, "commands": commands})
members = load(HERE / "date-completed-normal-original-members.json")
summary = members["summary"]
assert summary["candidate"] == candidate and summary["caseCount"] == 3
normal = load(HERE / "commands/date-completed-normal/result.json")
assert normal["exit"] == 0
assert "M1_GRAPH_OBSERVATION_DIR" not in normal["environment"]
assert "M1_ILLTYPED_OBSERVATION_DIR" not in normal["environment"]
assert "M1_DATE_OBSERVATION_DIR" in normal["environment"]
assert identity((HERE / summary["archive"]).read_bytes()) == {
    "bytes": summary["archiveBytes"],
    "sha256": summary["archiveSha256"],
}
source_path = (
    ROOT / "docs/reviews/T05/profile-M1-math-explanation-input-contract/consumer-C-inputs.json"
)
base = load(source_path)["cases"][11]
assert base["id"] == "C-inclusive-date-entry"
mapping = {
    "focusNode": "focus",
    "resultPath": "path",
    "value": "value",
    "sourceShape": "sourceShape",
    "sourceConstraintComponent": "constraint",
    "resultSeverity": "severity",
}
sh = "http://www.w3.org/ns/shacl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
observations, reports = [], 0
with zipfile.ZipFile(HERE / summary["archive"]) as bundle:
    assert bundle.testzip() is None
    assert len(set(bundle.namelist())) == summary["memberCount"] == len(members["members"])
    for row in members["members"]:
        raw = bundle.read(row["member"])
        assert identity(raw) == {k: row[k] for k in ("bytes", "sha256")}
        prefix, relative = row["member"].split("/", 1)
        actual_path = (
            HERE / "commands/date-completed-normal" / relative
            if prefix == "command"
            else Path(summary["actualDirectory"]) / relative
        )
        assert raw == actual_path.read_bytes()
        if not row["member"].endswith("/observation.json"):
            continue
        observation = json.loads(raw)
        assert observation["assertion"] == "pass"
        assert observation["testSourceSha256"] == identity(test.read_bytes())["sha256"]
        semantic = ROOT / "packages/engine/src/ontolearn_engine/semantic.py"
        assert observation["semanticSourceSha256"] == identity(semantic.read_bytes())["sha256"]
        assert observation["inputSourceSha256"] == identity(source_path.read_bytes())["sha256"]
        case, binding = observation["input"], observation["sourceBinding"]
        assert binding["pointer"] == "/cases/11"
        assert case["shapesTurtle"] == base["shapesTurtle"]
        lexical = {
            "original": "2000-01-01Z",
            "before": "1999-12-31Z",
            "offset": "2000-01-01+00:00",
        }[observation["variant"]]
        assert case["dataTurtle"] == base["dataTurtle"].replace("2000-01-01Z", lexical, 1)
        for name, text in (("data", case["dataTurtle"]), ("shapes", case["shapesTurtle"])):
            assert binding[name + "Utf8Sha256"] == identity(text.encode())["sha256"]
        stages = observation["actual"]["stages"]
        calls = [s["actual"]["validatorRuns"] for s in stages]
        assert calls == (
            [0, 1, 1, 0, 0]
            if observation["variant"] == "original"
            else [1]
            if observation["variant"] == "before"
            else [0]
        )
        directory = row["member"].rsplit("/", 1)[0]
        for stage in stages:
            actual = stage["actual"]
            state = actual["globalState"]
            assert all(
                state[k]
                for k in (
                    "normalizationUnchanged",
                    "converterKeysUnchanged",
                    "converterIdentitiesUnchanged",
                )
            )
            if not actual["validatorRuns"]:
                assert "result" not in actual and "realValidatorReport" not in actual
                assert actual["reason"] == (
                    "RDF_TERM_INVALID" if observation["variant"] == "offset" else "INVALID_SHAPE"
                )
                continue
            reports += 1
            prefix = directory + "/" + stage["name"] + "/"
            raw_triples = triples(bundle.read(prefix + "report.nt"))
            report = actual["result"]["report"]
            boolean = "true" if report["conforms"] else "false"
            assert [o for _, p, o in raw_triples if p == f"<{sh}conforms>"] == [
                f'"{boolean}"^^<{xsd}boolean>'
            ]
            nodes = [o for _, p, o in raw_triples if p == f"<{sh}result>"]
            assert len(nodes) == len(report["violations"])
            for node, api in zip(nodes, report["violations"], strict=True):
                for name, key in mapping.items():
                    assert [o for s, p, o in raw_triples if s == node and p == f"<{sh}{name}>"] == [
                        api[key]
                    ]
            facts = {
                ("<urn:m1:s>", "<urn:m1:p>", f'"{lexical}"^^<{xsd}date>'),
                (
                    "<urn:m1:s>",
                    "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>",
                    "<urn:m1:Focus>",
                ),
            }
            for name in ("parse-data.nt", "validator-data-before.nt", "validator-data-after.nt"):
                assert set(triples(bundle.read(prefix + name))) == facts
        observations.append(
            {"id": observation["id"], "variant": observation["variant"], "calls": calls}
        )
assert len(observations) == reports == 3
save(
    "audit-result.json",
    {
        "candidate": candidate,
        "controlled": 146,
        "readonly": 145,
        "originalPrefix": 58366,
        "oldFrozenGit": 474,
        "oldCurrentUnchanged": 473,
        "oldCurrentFormatException": exception,
        "cases": observations,
        "realReports": reports,
        "archive": summary,
        "allMemberBytesShaAndCrcVerified": True,
    },
)
print(json.dumps({"candidate": candidate, "cases": observations, "realReports": reports}))
