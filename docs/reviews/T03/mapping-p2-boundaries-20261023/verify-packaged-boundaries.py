"""Read-only source/package comparison against the pre-run fixed17 expectation.

No caller-supplied paths or inputs. Raw evidence goes to a fresh build directory.
"""

import hashlib
import json
import marshal
import os
import platform
import stat
import subprocess
import sys
import time
import types
import uuid
from datetime import UTC, datetime
from pathlib import Path

from PyInstaller.archive.readers import CArchiveReader

ROOT = Path(__file__).resolve().parents[4]
DOCS = ROOT / "docs/reviews/T03/mapping-p2-boundaries-20261023"
ENGINE = ROOT / "release/mac-arm64/OntoLearn Studio.app/Contents/Resources/engine/ontolearn-engine"
FLAG = "--mapping-probe"
BOUNDARIES = (
    "external-cached-formula",
    "external-hyperlink",
    "csv-file-limit-located",
    "csv-column-limit-located",
    "csv-cell-limit-located",
    "csv-row-limit-located",
)


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def identity(path):
    raw = path.read_bytes()
    return {"path": str(path), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def no_duplicates(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "DUPLICATE_JSON_KEY")
        value[key] = item
    return value


def json_value(raw):
    require(len(raw) <= 65536, "PROBE_OUTPUT_LIMIT")
    return json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=no_duplicates,
        parse_constant=lambda _value: require(False, "NONFINITE_JSON"),
    )


def code_hash(code):
    require(type(code) is types.CodeType, "ARCHIVE_CODE_UNAVAILABLE")

    def normalize(value):
        if type(value) is not types.CodeType:
            return value
        return value.replace(
            co_filename="<t03-fixed-probe-code>",
            co_consts=tuple(normalize(item) for item in value.co_consts),
        )

    return hashlib.sha256(marshal.dumps(normalize(code), 4)).hexdigest()


def run():
    require(len(sys.argv) == 1, "FIXED_VERIFIER_NO_ARGUMENTS")
    expected_path = DOCS / "fixed-probe-v2-expected.json"
    expected_identity = identity(expected_path)
    freeze = json.loads((DOCS / "oracle-before-run.json").read_text())
    require(expected_identity["sha256"] == freeze["expected"]["sha256"], "ORACLE_CHANGED")
    expected = json_value(expected_path.read_bytes())
    require(len(expected["cases"]) == 17, "FIXED_CASE_SET_INVALID")
    require(set(expected["boundaryEvidence"]) == set(BOUNDARIES), "FIXED_BOUNDARY_SET_INVALID")
    output = (
        ROOT
        / "build/mapping-p2-boundaries-20261023"
        / (
            "verification-"
            + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
            + "-"
            + uuid.uuid4().hex[:8]
        )
    )
    output.mkdir(parents=True, exist_ok=False)
    (output / "tmp").mkdir()
    before = identity(ENGINE)
    archive = CArchiveReader(str(ENGINE))
    pyz = archive.open_embedded_archive("PYZ.pyz")
    code_bindings = []
    for module, relative in (
        ("ontolearn_engine.mapping.probe", "mapping/probe.py"),
        ("ontolearn_engine.mapping.source", "mapping/source.py"),
        ("ontolearn_engine.mapping.plan", "mapping/plan.py"),
    ):
        path = ROOT / "packages/engine/src/ontolearn_engine" / relative
        source_code = compile(path.read_bytes(), str(path), "exec", dont_inherit=True, optimize=0)
        actual_code = pyz.extract(module)
        source_fingerprint = code_hash(source_code)
        packaged_fingerprint = code_hash(actual_code)
        require(source_fingerprint == packaged_fingerprint, "ACTUAL_PACKAGE_CODE_MISMATCH")
        code_bindings.append(
            {
                "module": module,
                "source": identity(path),
                "sourceCodeSha256": source_fingerprint,
                "actualPackageCodeSha256": packaged_fingerprint,
                "normalization": "only recursive co_filename; marshal4; optimize0",
            }
        )
    internal = ENGINE.parent / "_internal"
    lock = identity(ROOT / "uv.lock")
    packaged_lock = identity(internal / "provenance/uv.lock")
    require(lock["sha256"] == packaged_lock["sha256"], "PACKAGED_LOCK_MISMATCH")
    license_manifest = json.loads(
        (ROOT / "docs/reviews/T03/project-dependency-verification.json").read_text()
    )
    licenses = []
    for record in license_manifest["licenseFiles"].values():
        for relative, expected_sha in record["files"].items():
            actual = identity(internal / relative)
            require(actual["sha256"] == expected_sha, "PACKAGED_LICENSE_MISMATCH")
            licenses.append(actual)
    inventory = []
    for path in sorted(ENGINE.parent.rglob("*")):
        relative = path.relative_to(ENGINE.parent).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            require(
                path.resolve().is_relative_to(ENGINE.parent.resolve()), "PACKAGE_SYMLINK_ESCAPE"
            )
            inventory.append({"path": relative, "kind": "symlink", "target": os.readlink(path)})
        elif path.is_file():
            inventory.append({**identity(path), "path": relative, "kind": "file"})
        elif path.is_dir():
            inventory.append({"path": relative, "kind": "directory"})
        else:
            raise RuntimeError("PACKAGE_SPECIAL_FILE")
    inventory_path = output / "engine-inventory.json"
    inventory_path.write_text(json.dumps(inventory, ensure_ascii=False, sort_keys=True) + "\n")
    environment = os.environ.copy()
    environment["TMPDIR"] = str(output / "tmp")
    environment.pop("I02_HMR", None)
    runs = []
    parsed = {}
    commands = [
        ("source", [str(ROOT / ".venv/bin/python"), "packages/engine/entrypoint.py", FLAG], 0),
        ("package", [str(ENGINE), FLAG], 0),
        ("reject-path", [str(ENGINE), FLAG, "untrusted-input.xlsx"], 2),
        ("reject-script", [str(ENGINE), FLAG, "--script"], 2),
        ("reject-url", [str(ENGINE), FLAG, "https://example.invalid/"], 2),
    ]
    for name, argv, expected_exit in commands:
        start = datetime.now(UTC).isoformat()
        clock = time.monotonic()
        result = subprocess.run(
            argv, cwd=ROOT, env=environment, input=b"", capture_output=True, timeout=30, check=False
        )
        stdout = output / (name + "-stdout.bin")
        stderr = output / (name + "-stderr.bin")
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        item = {
            "name": name,
            "argv": argv,
            "cwd": str(ROOT),
            "startUtc": start,
            "endUtc": datetime.now(UTC).isoformat(),
            "launcherElapsedSeconds": time.monotonic() - clock,
            "exitCode": result.returncode,
            "stdout": identity(stdout),
            "stderr": identity(stderr),
        }
        runs.append(item)
        (output / (name + "-receipt.json")).write_text(
            json.dumps(item, ensure_ascii=False, indent=2) + "\n"
        )
        require(result.returncode == expected_exit, "PROBE_EXIT_MISMATCH")
        if expected_exit == 0:
            require(result.stderr == b"", "PROBE_UNEXPECTED_STDERR")
            parsed[name] = json_value(result.stdout)
            require(parsed[name] == expected, "PREAUTHORED_EXPECTATION_MISMATCH")
        else:
            require(result.stdout == b"", "REJECT_UNEXPECTED_STDOUT")
            require(result.stderr == b"MAPPING_PROBE_INVALID_ARGUMENTS\n", "REJECT_ERROR_MISMATCH")
    require(parsed["source"] == parsed["package"], "SOURCE_PACKAGE_RESULT_MISMATCH")
    require(identity(ENGINE) == before, "PACKAGE_CHANGED_DURING_VERIFICATION")
    cases = []
    for name, observed in parsed["package"]["boundaryEvidence"].items():
        cases.append(
            {
                "id": name,
                "observed": observed,
                "expected": expected["boundaryEvidence"][name],
                "assertionMatched": observed == expected["boundaryEvidence"][name],
                "sourceInvocationExit": 0,
                "packageInvocationExit": 0,
                "independentPerCaseProcessExit": None,
                "executionDomain": "one mandatory17case invocation, not17independent processes",
            }
        )
    all_cases = []
    cumulative_zero = parsed["package"]["boundaryEvidence"]["csv-row-limit-located"]["socketCalls"]
    for name, value in parsed["package"]["cases"].items():
        detail = parsed["package"]["boundaryEvidence"].get(name)
        all_cases.append(
            {
                "id": name,
                "observedResult": value,
                "expectedResult": expected["cases"][name],
                "assertionMatched": value == expected["cases"][name],
                "boundaryObservation": detail,
                "locationEvidence": (
                    "exact code/sheet/row/column emitted by fixed boundary case"
                    if detail is not None
                    else "legacy11 preserves its existing result; no new location claim"
                ),
                "guardCallsAtEndOfSameInvocation": cumulative_zero,
                "guardEvidenceScope": "cumulative across all17; not isolated per-case counters",
                "sourceInvocationExit": runs[0]["exitCode"],
                "packageInvocationExit": runs[1]["exitCode"],
                "independentPerCaseProcessExit": None,
            }
        )
    receipt = {
        "format": "T03-P2-source-package-fixed17/1",
        "recordedAtUtc": datetime.now(UTC).isoformat(),
        "expected": expected_identity,
        "oracleFreeze": identity(DOCS / "oracle-before-run.json"),
        "runtimeHead": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT)
        .decode()
        .strip(),
        "actualPackageExecutable": before,
        "codeBindings": code_bindings,
        "engineInventory": identity(inventory_path),
        "sourceLock": lock,
        "packagedLock": packaged_lock,
        "licenses": licenses,
        "runs": runs,
        "caseCount": 17,
        "newBoundaryCases": cases,
        "allCaseRecords": all_cases,
        "allExactExpected": True,
        "platform": platform.platform(),
        "python": sys.version,
        "guiStarted": False,
        "businessCapabilityEnabled": False,
        "targetPlatformAcceptance": False,
        "limits": expected["limits"],
        "noScopeExpansion": (
            "fixed synthetic17; no caller path, SDK, nativecaller, DB, GUI or I05 semantic CLI"
        ),
        "socketMeasurementDomain": (
            "fixed input construction/parsing; dependency import happens before guard; "
            "counters do not certify every OS-network primitive"
        ),
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {"receipt": identity(receipt_path), "actualNewBoundaryCases": len(cases)},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    run()
