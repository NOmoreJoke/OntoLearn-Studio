"""Scheduling and accounting regressions for the multi-process engine runner.

These exercise the real dispatcher logic (partition/account) from
scripts/run-engine-tests.py: whole-file assignment with full-coverage and
no-duplicate guarantees for every worker count, the measured-table balance
bound, case-count fallback for unmeasured files, and per-node settlement
plus failure propagation on synthesized worker folders.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

REPOSITORY = Path(__file__).resolve().parents[3]
_SPEC = importlib.util.spec_from_file_location(
    "run_engine_tests_ci_schedule", REPOSITORY / "scripts" / "run-engine-tests.py"
)
runner = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
# Register before exec: the runner's dataclass resolves its postponed
# annotations through sys.modules[cls.__module__].
sys.modules[_SPEC.name] = runner
_SPEC.loader.exec_module(runner)

IDENTITY = {"rootpath": "/repo", "executable": "/usr/bin/python3"}


def rows_for(counts_per_file):
    rows = []
    for name, count in counts_per_file.items():
        path = f"/repo/packages/engine/tests/{name}"
        for case in range(count):
            rows.append({"nodeid": f"{path}::test_{case}", "file": path})
    return rows


def test_partition_covers_every_file_exactly_once_for_each_worker_count():
    rows = rows_for(
        {
            "test_example_a.py": 7,
            "test_example_b.py": 3,
            "test_example_c.py": 12,
            "test_example_d.py": 1,
            "test_example_e.py": 5,
            "test_example_f.py": 2,
            "test_example_g.py": 9,
        }
    )
    for workers in (2, 3, 4):
        groups, weights = runner.partition(rows, workers)
        flat = [name for group in groups for name in group]
        assert len(flat) == len(weights) == 7
        assert len(set(flat)) == 7
        assert len(groups) == workers
        assert all(group == sorted(group) for group in groups)


def test_measured_partition_keeps_the_longest_processing_time_bound():
    rows = rows_for({name: 1 for name in runner.MEASURED_LINUX_SPANS})
    total = sum(runner.MEASURED_LINUX_SPANS.values())
    heaviest = max(runner.MEASURED_LINUX_SPANS.values())
    for workers in (2, 3, 4):
        groups, _weights = runner.partition(rows, workers, runner.MEASURED_LINUX_SPANS)
        loads = [
            sum(runner.MEASURED_LINUX_SPANS[Path(name).name] for name in group) for group in groups
        ]
        assert len(groups) == workers
        assert max(loads) <= total / workers + heaviest


def test_unmeasured_files_fall_back_to_their_collected_case_count():
    measured = {"test_known.py": 10.0}
    rows = rows_for({"test_known.py": 3, "test_new.py": 4})
    groups, weights = runner.partition(rows, 2, measured)
    known = "/repo/packages/engine/tests/test_known.py"
    fresh = "/repo/packages/engine/tests/test_new.py"
    assert weights[known] == 10.0
    assert weights[fresh] == 4.0
    assert sorted(groups[0] + groups[1]) == sorted([known, fresh])


def write_worker_folder(
    folder,
    expected,
    *,
    exitstatus,
    owner,
    drop_reports_for=(),
    foreign_nodeid=None,
):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "collection.json").write_text(
        json.dumps({"identity": IDENTITY, "items": expected}) + "\n", encoding="utf-8"
    )
    lines = [{"event": "session_start", "pid": 999, "parentPid": 222, "owner": owner}]
    for item in expected:
        nodeid = item["nodeid"]
        lines.append({"event": "start", "nodeid": nodeid})
        if nodeid not in drop_reports_for:
            for phase in ("setup", "call", "teardown"):
                lines.append(
                    {
                        "event": "report",
                        "nodeid": nodeid,
                        "phase": phase,
                        "outcome": "passed",
                        "duration": 0.01,
                        "wasxfail": None,
                        "longrepr": None,
                    }
                )
        lines.append({"event": "finish", "nodeid": nodeid})
    if foreign_nodeid is not None:
        lines.append({"event": "start", "nodeid": foreign_nodeid})
    lines.append({"event": "session_finish", "exitstatus": int(exitstatus), "testsfailed": 0})
    (folder / "events.jsonl").write_text(
        "".join(json.dumps(line) + "\n" for line in lines), encoding="utf-8"
    )


def fake_child(folder, owner, returncode):
    return SimpleNamespace(
        folder=folder,
        owner=owner,
        errors=[],
        process=SimpleNamespace(returncode=returncode, pid=222),
    )


def two_file_items():
    return rows_for({"test_example_a.py": 2, "test_example_b.py": 1})


def test_account_settles_every_node_phase_of_a_complete_session(tmp_path):
    expected = two_file_items()
    folder = tmp_path / "worker"
    write_worker_folder(folder, expected, exitstatus=0, owner="owner-1")
    outcomes, errors = runner.account(fake_child(folder, "owner-1", 0), expected, IDENTITY)
    assert errors == []
    assert set(outcomes) == {item["nodeid"] for item in expected}
    assert all(outcome["status"] == "passed" for outcome in outcomes.values())
    for outcome in outcomes.values():
        assert set(outcome["phases"]) == {"setup", "call", "teardown"}
    assert (folder / "session-identity.json").exists()


def test_account_propagates_a_nonzero_native_exit_as_failure(tmp_path):
    expected = two_file_items()
    folder = tmp_path / "worker"
    write_worker_folder(folder, expected, exitstatus=1, owner="owner-1")
    _outcomes, errors = runner.account(fake_child(folder, "owner-1", 1), expected, IDENTITY)
    assert any("native child exit/output failure" in error for error in errors)


def test_account_marks_nodes_with_missing_phases_unsetted_and_fails(tmp_path):
    expected = two_file_items()
    folder = tmp_path / "worker"
    write_worker_folder(
        folder, expected, exitstatus=0, owner="owner-1", drop_reports_for={expected[0]["nodeid"]}
    )
    outcomes, errors = runner.account(fake_child(folder, "owner-1", 0), expected, IDENTITY)
    assert outcomes[expected[0]["nodeid"]]["status"] == "unsettled"
    assert any("unsettled" in error for error in errors)


def test_account_rejects_events_for_nodes_outside_the_shard_manifest(tmp_path):
    expected = two_file_items()
    folder = tmp_path / "worker"
    write_worker_folder(
        folder, expected, exitstatus=0, owner="owner-1", foreign_nodeid="/other::test_x"
    )
    _outcomes, errors = runner.account(fake_child(folder, "owner-1", 0), expected, IDENTITY)
    assert any("unexpected node/event" in error for error in errors)


def test_account_rejects_a_session_owned_by_another_launcher(tmp_path):
    expected = two_file_items()
    folder = tmp_path / "worker"
    write_worker_folder(folder, expected, exitstatus=0, owner="someone-else")
    _outcomes, errors = runner.account(fake_child(folder, "owner-1", 0), expected, IDENTITY)
    assert any("session boundary" in error for error in errors)


def test_reporting_plugin_survives_stdlib_json_monkeypatch(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "engine_test_reporting_isolated", REPOSITORY / "scripts" / "engine-test-reporting.py"
    )
    assert spec is not None and spec.loader is not None
    plugin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plugin)

    test_file = tmp_path / "sample_test.py"
    test_file.write_text("def test_ok(): pass\n", encoding="utf-8")
    resolved_file = test_file.resolve()
    nodeid = f"{resolved_file}::test_ok"

    class FakeConfig:
        def __init__(self, report_dir, files_path=None):
            self.rootpath = tmp_path
            self.inipath = None
            self._opts = {
                "--engine-ci-report": str(report_dir),
                "--engine-ci-owner": "owner-json-guard",
                "--engine-ci-files": str(files_path) if files_path else None,
            }
            self.hook = SimpleNamespace(pytest_deselected=lambda items: None)

        def getoption(self, name):
            return self._opts[name]

        def getini(self, name):
            return []

    first_dir = tmp_path / "collect-only"
    cfg_collect = FakeConfig(first_dir)
    item = SimpleNamespace(path=test_file, nodeid=nodeid)
    plugin.pytest_configure(cfg_collect)
    plugin.pytest_collection_finish(SimpleNamespace(config=cfg_collect, items=[item]))
    plugin.pytest_unconfigure(cfg_collect)
    manifest = json.loads((first_dir / "collection.json").read_text(encoding="utf-8"))

    files_json = tmp_path / "files.json"
    files_json.write_text(
        json.dumps(
            {
                "files": [str(resolved_file)],
                "items": manifest["items"],
                "identity": manifest["identity"],
            }
        ),
        encoding="utf-8",
    )

    worker_dir = tmp_path / "worker"
    cfg_worker = FakeConfig(worker_dir, files_json)
    other_file = tmp_path / "other_test.py"
    other_file.write_text("def test_skip(): pass\n", encoding="utf-8")
    items = [item, SimpleNamespace(path=other_file, nodeid=f"{other_file}::test_skip")]

    def poisoned(*_args, **_kwargs):
        raise AssertionError("whole json allocation")

    with monkeypatch.context() as mp:
        mp.setattr(json, "dumps", poisoned)
        mp.setattr(json, "loads", poisoned)
        plugin.pytest_configure(cfg_worker)
        plugin.pytest_collection_modifyitems(cfg_worker, items)
        assert [entry.nodeid for entry in items] == [nodeid]
        session = SimpleNamespace(config=cfg_worker, items=items, testsfailed=0)
        plugin.pytest_collection_finish(session)
        plugin.pytest_runtest_logstart(nodeid, (str(test_file), 1, "test_ok"))
        for phase in ("setup", "call", "teardown"):
            plugin.pytest_runtest_logreport(
                SimpleNamespace(
                    nodeid=nodeid,
                    when=phase,
                    outcome="passed",
                    duration=0.01,
                    failed=False,
                    skipped=False,
                    longreprtext="",
                )
            )
        plugin.pytest_runtest_logfinish(nodeid, (str(test_file), 1, "test_ok"))
        plugin.pytest_sessionfinish(session, 0)
        plugin.pytest_unconfigure(cfg_worker)

    events = [
        json.loads(line)
        for line in (worker_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert events[0]["event"] == "session_start"
    assert [e.get("phase") for e in events if e["event"] == "report"] == [
        "setup",
        "call",
        "teardown",
    ]
    assert events[-1] == {"event": "session_finish", "exitstatus": 0, "testsfailed": 0}
    assert json.loads((worker_dir / "collection.json").read_text(encoding="utf-8")) == manifest
