"""Read-only independent byte/code/receipt audit. Never invoke the engine."""

import ast
import hashlib
import json
import marshal
import os
import stat
import subprocess
import types
from datetime import UTC, datetime
from pathlib import Path

from PyInstaller.archive.readers import CArchiveReader

ROOT = Path(__file__).resolve().parents[5]
DOCS = ROOT / "docs/reviews/T03/mapping-p2-boundaries-20261023"
OUT = Path(__file__).parent
BASE = "30319412daf8ae4745987babf7bbed93c53b6b42"
CANDIDATE = "da1795b20c3c0d47ae975fe3371e802092a4b429"
RESULT = {"startedUtc": datetime.now(UTC).isoformat(), "base": BASE, "candidate": CANDIDATE}


def raw_git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def owned(path):
    path = Path(path)
    path = path if path.is_absolute() else ROOT / path
    assert path.resolve().is_relative_to(ROOT)
    assert "T03-native-location-N0-build" not in str(path)
    return path


def check_identity(record):
    path = owned(record["path"])
    raw = path.read_bytes()
    assert (len(raw), sha(raw)) == (record["bytes"], record["sha256"]), str(path)


def canonical_code(code):
    if type(code) is not types.CodeType:
        return code
    return code.replace(
        co_filename="<t03-fixed-probe-code>",
        co_consts=tuple(canonical_code(item) for item in code.co_consts),
    )


def code_sha(code):
    return sha(marshal.dumps(canonical_code(code), 4))


def main():
    assert raw_git("rev-parse", "HEAD").decode().strip() == CANDIDATE
    changes = raw_git("diff", "--name-only", BASE, CANDIDATE).decode().splitlines()
    products = [p for p in changes if not p.startswith("docs/")]
    assert products == [
        "packages/engine/src/ontolearn_engine/mapping/probe.py",
        "packages/engine/tests/test_mapping_entrypoint.py",
    ]
    RESULT["committedProducts"] = products
    for name in ("manifest.json", "raw-evidence-manifest.json"):
        records = json.loads((DOCS / name).read_text())["files"]
        for record in records:
            check_identity(record)
        RESULT[name] = {"verifiedFiles": len(records), "allBytesAndHashesMatch": True}

    binding = json.loads((DOCS / "candidate-binding.json").read_text())
    for record in binding["sourceIdentities"]:
        check_identity(record)
        if record["path"] != "AGENTS.md":
            current = owned(record["path"]).read_bytes()
            assert current == raw_git("show", f"{CANDIDATE}:{record['path']}")
            if record["path"] not in products:
                assert current == raw_git("show", f"{BASE}:{record['path']}")
    RESULT["candidateBinding"] = {"sourceIdentitiesVerified": len(binding["sourceIdentities"]),
                                  "protectedRecordedPathsEqualBase": True,
                                  "runtimeDirtyProductsEqualCommit": True}

    expected = json.loads((DOCS / "fixed-probe-v2-expected.json").read_text())
    oldraw = raw_git("show", f"{BASE}:docs/reviews/T03/project-probe-first.json")
    old = json.loads(oldraw)
    assert sha(oldraw) == "5124b647c29d60bd1e4483ca6caf7d68c3a2f02eaff0241b06112ce902944203"
    projected = {k: expected[k] for k in old}
    projected["cases"] = {k: expected["cases"][k] for k in old["cases"]}
    assert projected == old
    probe_path = owned(products[0])
    before_ast = ast.parse(raw_git("show", f"{BASE}:{products[0]}"))
    after_ast = ast.parse(probe_path.read_bytes())
    oldrun = next(n for n in before_ast.body if isinstance(n, ast.FunctionDef) and n.name == "run")
    newrun = next(n for n in after_ast.body if isinstance(n, ast.FunctionDef) and n.name == "_legacy_cases")
    assert [ast.dump(n) for n in oldrun.body] == [ast.dump(n) for n in newrun.body]
    assert len(expected["cases"]) == 17 and len(expected["boundaryEvidence"]) == 6
    RESULT["legacyPreserved"] = {"oracleOld11ProjectionEqualsBase": True,
                                 "legacyFunctionBodyASTEqualsBase": True}

    receipt = json.loads((DOCS / "actual-receipt.json").read_text())
    check_identity(binding["actualVerifierRawReceipt"])
    assert owned(binding["actualVerifierRawReceipt"]["path"]).read_bytes() == (DOCS / "actual-receipt.json").read_bytes()
    check_identity(receipt["actualPackageExecutable"])
    for record in (receipt["expected"], receipt["oracleFreeze"], receipt["engineInventory"],
                   receipt["sourceLock"], receipt["packagedLock"], *receipt["licenses"]):
        check_identity(record)
    engine = owned(receipt["actualPackageExecutable"]["path"])
    inventory = json.loads((DOCS / "actual-engine-inventory.json").read_text())
    assert inventory == json.loads(owned(receipt["engineInventory"]["path"]).read_text())
    actual = []
    for path in sorted(engine.parent.rglob("*")):
        row = {"path": path.relative_to(engine.parent).as_posix()}
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            assert path.resolve().is_relative_to(engine.parent.resolve())
            row.update(kind="symlink", target=os.readlink(path))
        elif stat.S_ISREG(mode):
            raw = path.read_bytes()
            row.update(kind="file", bytes=len(raw), sha256=sha(raw))
        elif stat.S_ISDIR(mode):
            row.update(kind="directory")
        else:
            raise AssertionError("special artifact file")
        actual.append(row)
    assert inventory == actual
    RESULT["actualEngineInventory"] = {"entries": len(actual), "currentFullTreeEqualsArchivedInventory": True}
    archive = CArchiveReader(str(engine)).open_embedded_archive("PYZ.pyz")
    codes = []
    for row in receipt["codeBindings"]:
        check_identity(row["source"])
        path = owned(row["source"]["path"])
        source = compile(path.read_bytes(), str(path), "exec", flags=0, dont_inherit=True, optimize=0)
        computed = code_sha(source)
        assert computed == code_sha(archive.extract(row["module"]))
        assert computed == row["sourceCodeSha256"] == row["actualPackageCodeSha256"]
        codes.append({"module": row["module"], "codeSha256": computed})
    RESULT["independentlyRecomputedCodeBindings"] = codes

    for row in receipt["runs"]:
        check_identity(row["stdout"])
        check_identity(row["stderr"])
        stdout, stderr = (owned(row[x]["path"]).read_bytes() for x in ("stdout", "stderr"))
        if row["name"] in ("source", "package"):
            assert row["exitCode"] == 0 and not stderr and json.loads(stdout) == expected
        else:
            assert row["exitCode"] == 2 and not stdout and stderr == b"MAPPING_PROBE_INVALID_ARGUMENTS\n"
    assert len(receipt["allCaseRecords"]) == 17
    for row in receipt["allCaseRecords"]:
        assert row["independentPerCaseProcessExit"] is None
        assert row["sourceInvocationExit"] == row["packageInvocationExit"] == 0
        assert row["assertionMatched"] and row["observedResult"] == expected["cases"][row["id"]]
    optimized = owned(binding["optimizedSource"]["path"]).read_bytes()
    check_identity(binding["optimizedSource"])
    assert json.loads(optimized) == expected
    RESULT["recordedRunsReadback"] = {"runs": len(receipt["runs"]), "allFullOutputChecksMatch": True,
                                      "caseRecords": 17, "independentPerCaseExits": None,
                                      "optimizedSourceExactOracle": True}

    records = json.loads((DOCS / "command-records.json").read_text())["records"]
    summaries = []
    for row in records:
        check_identity(row["receipt"])
        assert json.loads(owned(row["receipt"]["path"]).read_text()) == row["record"]
        record = row["record"]
        for stream in ("stdout", "stderr"):
            check_identity(record[stream])
        if record["action"] in ("check", "package", "sources", "verify-package", "source-probe-optimized"):
            assert record["exitCode"] == 0
            for product in record["productAtStart"][:2]:
                check_identity(product)
        summaries.append({"action": record["action"], "startUtc": record["startUtc"],
                          "exitCode": record["exitCode"]})
    RESULT["commandReadback"] = summaries
    RESULT["completeUtc"] = datetime.now(UTC).isoformat()
    RESULT["scope"] = "read-only independent byte/code/receipt review; no source/package execution or fullcheck rerun"
    (OUT / "audit-result.json").write_text(json.dumps(RESULT, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(RESULT, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
