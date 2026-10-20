"""Read-only, per-call evidence for the existing 96 atomic + 48 round fault cases.

Run from the repository root with a NEW output directory (never reuse an old run):
    python -m pytest -p scripts.i04_matrix_evidence \
      --i04-matrix-evidence build/matrix-evidence/run-1 \
      packages/engine/tests/test_job_store.py::test_atomic_job_fault_reconcile_matrix \
      packages/engine/tests/test_i04_round_faults.py::test_round_job_progress_atomic_fault_matrix_fences_and_preserves_previous_round

An optional --i04-matrix-source-revision REF verifies the actual source bytes
against that committed Git tree. No test, fixture, timeout, assertion or retry is
changed. All SQLite connections use mode=ro, query_only and a read-only authorizer.
Counts/hashes describe observed contents; they are NOT exact expected-value tests.
"""

import hashlib
import inspect
import itertools
import json
import os
import sqlite3
import subprocess
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import pytest

ATOMIC = "test_atomic_job_fault_reconcile_matrix"
ROUNDS = "test_round_job_progress_atomic_fault_matrix_fences_and_preserves_previous_round"
TARGETS = {
    ATOMIC: ("atomic", "store", "test.atomic"),
    ROUNDS: ("round", "db", "test.rounds"),
}
EXPECTED = {
    "atomic": {
        (mode, phase, failure)
        for mode, phase, failure in itertools.product(
            ("changeset", "mapping", "definition-remove"),
            (
                "before",
                "mid_data",
                "mid_ownership",
                "mid_invalidation",
                "mid_marker",
                "mid_job_terminal",
                "before_commit",
                "after_commit",
            ),
            ("exception", "disk", "cancel", "exit"),
        )
    },
    "round": {
        (previous, phase, failure)
        for previous, phase, failure in itertools.product(
            (0, 1),
            (
                "before",
                "mid_data",
                "mid_marker",
                "mid_job_progress",
                "before_commit",
                "after_commit",
            ),
            ("exception", "disk", "cancel", "exit"),
        )
    },
}
PARAMETERS = {"atomic": ("mode", "phase", "failure"), "round": ("previous", "phase", "failure")}
SOURCE_FILES = (
    "packages/engine/tests/test_job_store.py",
    "packages/engine/tests/test_i04_round_faults.py",
    "packages/engine/src/ontolearn_engine/job_store.py",
    "packages/engine/src/ontolearn_engine/storage.py",
    "packages/contracts/python/contract_v2.py",
    "packages/contracts/v2/schema.json",
    "packages/contracts/v2/registry.json",
    "packages/contracts/v2/states.json",
    "packages/contracts/v2/errors.json",
    "packages/contracts/v2/dependencies.json",
    "uv.lock",
)


def canonical(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def sqlite_value(value):
    return {"sqlite_blob_hex": value.hex()} if isinstance(value, bytes) else value


def table_rows(connection, table):
    # Identifiers originate in sqlite_master and are quoted, never executed as SQL.
    cursor = connection.execute('SELECT * FROM "' + table.replace('"', '""') + '"')
    columns = [column[0] for column in cursor.description]
    rows = [
        {key: sqlite_value(value) for key, value in zip(columns, row, strict=True)}
        for row in cursor.fetchall()
    ]
    rows.sort(key=canonical)
    return columns, rows


def read_database(path, capability):
    uri = path.resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=5, isolation_level=None)
    try:
        connection.execute("PRAGMA query_only=ON")
        allowed = {
            sqlite3.SQLITE_SELECT,
            sqlite3.SQLITE_READ,
            sqlite3.SQLITE_FUNCTION,
            sqlite3.SQLITE_TRANSACTION,
        }
        connection.set_authorizer(
            lambda action, *_: sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY
        )
        connection.execute("BEGIN")
        schema = connection.execute(
            "SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name"
        ).fetchall()
        names = [
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT GLOB 'sqlite_*' ORDER BY name"
            )
        ]
        tables, contents = {}, {}
        for name in names:
            columns, rows = table_rows(connection, name)
            contents[name] = rows
            tables[name] = {
                "rows": len(rows),
                "sha256": sha256(canonical({"columns": columns, "rows": rows}).encode()),
            }
        candidates = []
        for row in contents.get("jobs", []):
            dto = json.loads(row["dto"])
            if dto.get("capability") == capability:
                candidates.append((row, dto))
        if len(candidates) != 1:
            raise ValueError("EVIDENCE_MAIN_JOB_NOT_UNIQUE")
        row, job = candidates[0]
        # Only keys are emitted; full input/plan/blob/payload contents contribute
        # to their complete table hashes rather than becoming a large data dump.
        keep = (
            "jobId",
            "projectId",
            "operationId",
            "capability",
            "state",
            "stateVersion",
            "commitProgress",
            "resultRef",
            "error",
            "inputSnapshotId",
            "dependencyVector",
            "definitionSetDigests",
            "parametersHash",
            "scope",
            "implementation",
            "confirmationRef",
            "createdAtMs",
            "updatedAtMs",
            "finishedAtMs",
        )
        main_job = {key: job[key] for key in keep}
        main_job["storedContextFingerprint"] = row["fingerprint"]
        main_job["storedContextBytesSha256"] = sha256(row["context"].encode())
        result_projection = []
        for result in contents.get("results", []):
            stale = next(
                (
                    s["stale"]
                    for s in contents.get("result_state", [])
                    if s["result"] == result["id"]
                ),
                None,
            )
            result_projection.append(
                {
                    "resultId": result["id"],
                    "project": result["project"],
                    "kind": result["kind"],
                    "inputSnapshotId": result["snapshot"],
                    "dependencyVector": json.loads(result["dependencies"]),
                    "staleReason": json.loads(stale) if stale is not None else None,
                    "payloadAvailable": result["payload"] is not None,
                }
            )
        return {
            "readOnly": True,
            "mainJob": main_job,
            "schemaSha256": sha256(canonical(schema).encode()),
            "projects": contents.get("projects", []),
            "versions": contents.get("versions", []),
            "definitionRetirements": contents.get("definition_retirements", []),
            "mappingState": contents.get("mapping_state", []),
            "resultProjection": result_projection,
            "currentPointers": {
                "jobCurrent": contents.get("job_current", []),
                "s1Current": contents.get("current_results", []),
            },
            "tables": tables,
        }
    finally:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        connection.close()


def pytest_addoption(parser):
    group = parser.getgroup("i04-matrix-evidence")
    group.addoption(
        "--i04-matrix-evidence", metavar="DIRECTORY", help="New per-run JSON evidence directory"
    )
    group.addoption(
        "--i04-matrix-source-revision",
        metavar="REF",
        help="Verify source bytes against committed REF",
    )


def pytest_configure(config):
    output = config.getoption("--i04-matrix-evidence")
    if output:
        config.pluginmanager.register(MatrixEvidence(config, Path(output)), "i04-matrix-recorder")


class MatrixEvidence:
    def __init__(self, config, output):
        self.config = config
        self.output = output.resolve()
        self.output.mkdir(parents=True, exist_ok=True)
        if any((self.output / name).exists() for name in ("summary.json", "cases.jsonl")):
            raise pytest.UsageError(
                "I04 evidence requires a NEW output directory; old runs are preserved"
            )
        self.started = time.monotonic()
        self.started_at = datetime.now(UTC).isoformat()
        self.cases = {}
        self.errors = []
        self.unexpected = []
        self.sources = {}
        self.root = None
        self.complete_calls = 0
        self.recorded = 0
        self.stream = (self.output / "cases.jsonl").open("w", encoding="utf-8", newline="\n")
        self._write_summary({"status": "running", "startedAtUtc": self.started_at})

    def _write_summary(self, summary):
        temporary = self.output / "summary.json.tmp"
        temporary.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        os.replace(temporary, self.output / "summary.json")

    def pytest_collection_finish(self, session):
        if getattr(self.config.option, "numprocesses", 0):
            self.errors.append("PARALLEL_SCHEDULING_NOT_SUPPORTED")
        for item in session.items:
            original = getattr(item, "originalname", None)
            if original not in TARGETS:
                self.unexpected.append(item.nodeid)
                continue
            matrix, fixture, capability = TARGETS[original]
            params = dict(item.callspec.params) if hasattr(item, "callspec") else {}
            self.cases[item.nodeid] = {
                "matrix": matrix,
                "fixture": fixture,
                "capability": capability,
                "params": params,
                "outcomes": {},
                "snapshotSha256": None,
            }
            file = Path(str(item.path)).resolve()
            root = file.parents[3]
            if self.root is not None and self.root != root:
                self.errors.append("TEST_SOURCE_ROOT_MISMATCH")
            self.root = root
        if self.root is not None:
            for relative in SOURCE_FILES:
                path = self.root / relative
                try:
                    raw = path.read_bytes()
                    self.sources[relative] = {"sha256": sha256(raw)}
                except OSError:
                    self.errors.append("SOURCE_UNREADABLE:" + relative)
            for name, (matrix, _, _) in TARGETS.items():
                matching = [
                    item for item in session.items if getattr(item, "originalname", None) == name
                ]
                if matching:
                    lines, start = inspect.getsourcelines(matching[0].function)
                    self.sources[
                        str(Path(str(matching[0].path)).resolve().relative_to(self.root))
                    ].update(
                        {
                            "function": name,
                            "functionStartLine": start,
                            "functionSha256": sha256("".join(lines).encode()),
                            "matrix": matrix,
                        }
                    )
        # Verify imported implementation paths, not just whichever source checkout
        # happened to contain tests. A foreign editable install must not be hidden.
        for module, relative in (
            ("ontolearn_engine.job_store", "packages/engine/src/ontolearn_engine/job_store.py"),
            ("ontolearn_engine.storage", "packages/engine/src/ontolearn_engine/storage.py"),
        ):
            actual = Path(sys.modules[module].__file__).resolve() if module in sys.modules else None
            if self.root is None or actual != (self.root / relative).resolve():
                self.errors.append("IMPORTED_IMPLEMENTATION_MISMATCH:" + module)
        ref = self.config.getoption("--i04-matrix-source-revision")
        if ref and self.root is not None:
            for relative, source in self.sources.items():
                try:
                    result = subprocess.run(
                        ["git", "show", f"{ref}:{relative}"],
                        cwd=self.root,
                        capture_output=True,
                        timeout=10,
                    )
                    if result.returncode or sha256(result.stdout) != source["sha256"]:
                        self.errors.append("REVISION_SOURCE_MISMATCH:" + relative)
                except (OSError, subprocess.TimeoutExpired):
                    self.errors.append("REVISION_SOURCE_UNVERIFIABLE:" + relative)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        result = yield
        report = result.get_result()
        record = self.cases.get(item.nodeid)
        if record is None:
            return
        record["outcomes"][report.when] = report.outcome
        if report.when != "call":
            return
        self.complete_calls += 1
        evidence = {
            "nodeid": item.nodeid,
            "matrix": record["matrix"],
            "params": record["params"],
            "pytestCallOutcome": report.outcome,
            "assertionsCompleted": report.passed,
            "source": {
                "file": str(Path(str(item.path)).resolve().relative_to(self.root)),
                "sha256": self.sources.get(
                    str(Path(str(item.path)).resolve().relative_to(self.root)), {}
                ).get("sha256"),
            },
        }
        try:
            fixture = item.funcargs[record["fixture"]]
            database = Path(fixture.path)
            evidence["database"] = read_database(database, record["capability"])
            evidence["databaseFixture"] = record["fixture"]
            evidence["databasePathSha256"] = sha256(str(database.resolve()).encode())
            self.recorded += 1
        except Exception as error:
            # Never replace a test assertion outcome or expose an exception/body.
            evidence["captureError"] = {
                "type": type(error).__name__,
                "sqliteCode": getattr(error, "sqlite_errorcode", None),
            }
            self.errors.append("DATABASE_CAPTURE_FAILED:" + item.nodeid)
        encoded = canonical(evidence)
        record["snapshotSha256"] = sha256(encoded.encode())
        self.stream.write(encoded + "\n")
        self.stream.flush()
        os.fsync(self.stream.fileno())

    def pytest_sessionfinish(self, session, exitstatus):
        self.stream.close()
        matrices = {}
        for matrix, expected in EXPECTED.items():
            selected = [case for case in self.cases.values() if case["matrix"] == matrix]
            keys = []
            for case in selected:
                params = case["params"]
                if set(params) != set(PARAMETERS[matrix]):
                    self.errors.append("PARAMETER_FIELDS_MISMATCH:" + matrix)
                else:
                    keys.append(tuple(params[name] for name in PARAMETERS[matrix]))
            if len(keys) != len(set(keys)) or set(keys) != expected:
                self.errors.append("INCOMPLETE_OR_DUPLICATE_MATRIX:" + matrix)
            passed = sum(
                case["outcomes"] == {"setup": "passed", "call": "passed", "teardown": "passed"}
                and case["snapshotSha256"] is not None
                for case in selected
            )
            matrices[matrix] = {
                "expected": len(expected),
                "collected": len(selected),
                "passed": passed,
            }
            if passed != len(expected):
                self.errors.append("NONPASS_MATRIX_CASE:" + matrix)
        for relative, original in self.sources.items():
            try:
                if sha256((self.root / relative).read_bytes()) != original["sha256"]:
                    self.errors.append("SOURCE_CHANGED_DURING_RUN:" + relative)
            except OSError:
                self.errors.append("SOURCE_LOST_DURING_RUN:" + relative)
        if self.unexpected:
            self.errors.append("UNEXPECTED_TEST_SELECTION")
        if int(exitstatus) != 0:
            self.errors.append("PYTEST_NONZERO_EXIT")
        if self.complete_calls != 144 or self.recorded != 144:
            self.errors.append("INCOMPLETE_DATABASE_EVIDENCE")
        failed = bool(self.errors)
        if failed and int(session.exitstatus) == 0:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED
        cases_file = self.output / "cases.jsonl"
        observed = Counter()
        for line in cases_file.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if "database" in row:
                observed[row["database"]["mainJob"]["state"]] += 1
        plugin_file = Path(__file__).resolve()
        summary = {
            "format": "i04-matrix-evidence-v1",
            "status": "failed" if failed else "passed",
            "startedAtUtc": self.started_at,
            "elapsedSeconds": round(time.monotonic() - self.started, 3),
            "sourceRevisionRequested": self.config.getoption("--i04-matrix-source-revision"),
            "sources": self.sources,
            "pluginSha256": sha256(plugin_file.read_bytes()),
            "matrices": matrices,
            "completedCalls": self.complete_calls,
            "capturedDatabases": self.recorded,
            "observedMainJobStates": dict(observed),
            "pytestExitStatus": int(session.exitstatus),
            "errors": sorted(set(self.errors)),
            "unexpectedTests": self.unexpected,
            "casesFile": "cases.jsonl",
            "casesFileSha256": sha256(cases_file.read_bytes()),
            "cases": [
                {
                    "nodeid": key,
                    "matrix": value["matrix"],
                    "params": value["params"],
                    "pytestOutcomes": value["outcomes"],
                    "snapshotSha256": value["snapshotSha256"],
                }
                for key, value in sorted(self.cases.items())
            ],
            "boundaries": [
                "Snapshots are captured after each pytest call; "
                "assertionsCompleted only means the original call passed.",
                "Table hashes cover every row, sorted by canonical JSON, including columns; "
                "they are execution fingerprints, not expected-value assertions.",
                "Exact expected assertions remain in the linked test sources; "
                "observed state/count/hash does not replace them.",
                "SQLite reads use mode=ro, query_only and an authorizer allowing only "
                "SELECT/READ/FUNCTION/TRANSACTION; no database is written or copied.",
                "Only full unique 96 atomic + 48 round cases with setup/call/teardown passed "
                "and captured evidence permit passed status.",
                "No test assertion, budget, retry, fixture or implementation is modified "
                "by this plugin.",
            ],
        }
        self._write_summary(summary)

    def pytest_terminal_summary(self, terminalreporter):
        path = self.output / "summary.json"
        terminalreporter.write_line(
            "I04_MATRIX_EVIDENCE "
            + canonical({"summary": str(path), "sha256": sha256(path.read_bytes())})
        )
