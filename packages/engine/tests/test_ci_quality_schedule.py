"""Scheduling and failure-propagation regressions for the Quality orchestrator.

These exercise the real plan and pipeline from scripts/ci-quality-schedule.py:
every original Quality stage appears exactly once (nothing dropped or
duplicated), phase two opens only after full phase-one success, dependent
lanes are skipped after a failure while independent lanes drain, the green
path succeeds, and the real spawn boundary settles spawn/IO failures,
cancellation (reaping only the lane's own process group) and overlong
single-line output.
"""

from __future__ import annotations

import asyncio
import importlib.util
import os
import sys
from pathlib import Path

import pytest

REPOSITORY = Path(__file__).resolve().parents[3]
_SPEC = importlib.util.spec_from_file_location(
    "ci_quality_schedule", REPOSITORY / "scripts" / "ci-quality-schedule.py"
)
scheduler = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules[_SPEC.name] = scheduler
_SPEC.loader.exec_module(scheduler)

POSIX_LANE_SPAWN = pytest.mark.skipif(
    sys.platform == "win32", reason="the real lane spawn uses /bin/bash"
)


def test_plan_covers_every_original_quality_stage_exactly_once():
    plan = scheduler.build_plan()
    # Commands plus lane environment values are the full stage surface that
    # mirrors the original Quality job; counting tokens over both proves no
    # stage was dropped or duplicated by the rescheduling.
    joined = "\n".join(lane.command + "\n" + "\n".join(lane.env.values()) for lane in plan)
    exact_counts = {
        "scripts.i04_matrix_evidence": 1,
        "--i04-matrix-evidence build/i04-matrix-ci": 1,
        "npm run lint": 1,
        "npm run format:check": 1,
        "npm run typecheck": 1,
        "npm test": 1,
        "npm run build": 1,
        "npm run engine:build": 1,
        "npm run engine:check": 1,
        "npm run verify:sources": 1,
        "./node_modules/.bin/install-electron": 1,
        "sudo chown root:root node_modules/electron/dist/chrome-sandbox": 1,
        "sudo apt-get install -y openbox xdotool": 1,
        "npm run test:e2e": 1,
        "verify-i04-package.py release build/i04-package-ci": 1,
        "npm run package:dir": 1,
        "find release -type f -name chrome-sandbox": 1,
        "ONTOLEARN_PACKAGED_EXECUTABLE": 1,
        "prepare-i04-fixture.py build/i04-native-ci": 1,
        "build/i04-reload-ci --background-rounds 12": 1,
        "build/i04-packaged-reload-ci --background-rounds 12": 1,
        "prepare-i04-fixture.py build/i04-disconnect-ci": 1,
        "prepare-i04-fixture.py build/i04-packaged-disconnect-ci": 1,
        "prepare-i04-fixture.py build/i04-packaged-native-ci": 1,
        "test-results/main/report.json": 1,
        "test-results/i02-linux-evidence.json": 1,
    }
    minimum_counts = {
        '--grep "native renderer"': 2,
        '--grep "reload re-queries"': 2,
        '--grep "coordinator exit"': 2,
        "xvfb-run -a": 7,
        "I04_NATIVE_ISOLATED=1": 2,
    }
    for token, expected in exact_counts.items():
        assert joined.count(token) == expected, token
    for token, expected in minimum_counts.items():
        assert joined.count(token) >= expected, token


def test_plan_dependencies_and_engine_sharding_shape():
    plan = scheduler.build_plan()
    by_name = {lane.name: lane for lane in plan}
    assert set(by_name) == {
        "apt-display",
        "chromium-sandbox",
        "i04-matrix",
        "verify-sources",
        "static-gates",
        "engine",
        "unit-build",
        "main-e2e",
        "package",
        "verify-package",
        "i04-unpackaged",
        "packaged-recovery",
    }
    assert by_name["engine"].deps == ("static-gates",)
    assert by_name["unit-build"].deps == ("static-gates",)
    assert by_name["engine"].env == {
        "CI_ENGINE_TEST_SHARDS": "4",
        "CI_ENGINE_TEST_WEIGHTS": "linux-ci46",
    }
    assert by_name["verify-package"].deps == ("package",)
    # The unpackaged and packaged native renderer runs share the default
    # Electron profile identity (no per-launch user-data-dir), so their lanes
    # are explicitly ordered; see the ownership note in build_plan.
    assert by_name["packaged-recovery"].deps == ("verify-package", "i04-unpackaged")
    # The desktop build rewrites the shared apps/desktop out/ tree that the
    # unpackaged e2e lanes execute from, so packaging consumes the phase-one
    # build instead of rebuilding it concurrently (see the isolation test).
    assert by_name["package"].deps == ("unit-build",)
    for independent in ("main-e2e", "i04-unpackaged"):
        assert by_name[independent].deps == ()
    for lane in plan:
        if lane.phase == 1 and lane.name not in ("engine", "unit-build"):
            assert lane.deps == ()
    scheduler.validate_plan(plan)


def test_shared_desktop_output_is_built_once_in_phase_one_and_never_rebuilt_during_e2e():
    plan = scheduler.build_plan()
    by_name = {lane.name: lane for lane in plan}
    # 'npm run build' (the electron-vite build that empties/rewrites
    # apps/desktop/out) appears exactly once, in a phase-one lane.
    build_lanes = [lane for lane in plan if "npm run build" in lane.command]
    assert [lane.name for lane in build_lanes] == ["unit-build"]
    assert build_lanes[0].phase == 1
    # Packaging runs the engine bundle plus electron-builder only: it must
    # not contain another desktop build that would race the e2e readers.
    assert "npm run build" not in by_name["package"].command
    assert "npm run engine:build" in by_name["package"].command
    assert "npm run package:dir" in by_name["package"].command
    # The out/ consumers may not depend on packaging, and packaging may not
    # depend on them: they overlap in time over one stable out/ snapshot.
    for reader in ("main-e2e", "i04-unpackaged"):
        assert "package" not in by_name[reader].deps
        assert reader not in by_name["package"].deps
    started: list[str] = []

    async def spawn(lane):
        started.append(lane.name)
        return 0

    result, _logs = asyncio.run(_drive(scheduler.build_plan(), spawn))
    assert result["ok"] is True
    assert started.index("package") > started.index("unit-build")


def test_validate_plan_rejects_broken_dependency_graphs():
    lane = scheduler.Lane("solo", 1, "true")
    assert scheduler.validate_plan([lane]) is None
    for broken in (
        [scheduler.Lane("a", 1, "true", deps=("ghost",))],
        [scheduler.Lane("a", 1, "true"), scheduler.Lane("a", 1, "true")],
        [scheduler.Lane("later", 1, "true", deps=("future",)), scheduler.Lane("future", 2, "t")],
    ):
        try:
            scheduler.validate_plan(broken)
        except ValueError:
            continue
        raise AssertionError(f"validate_plan accepted {broken!r}")


async def _drive(lanes, spawn):
    logs: list[str] = []
    # Bounded so a future non-convergent scheduling loop fails the test here
    # instead of hanging CI; waiting is never treated as a pass.
    result = await asyncio.wait_for(scheduler.run_pipeline(lanes, spawn, logs.append), timeout=10.0)
    return result, logs


def _wait_for(predicate, timeout=5.0):
    deadline = asyncio.get_event_loop().time() + timeout
    while not predicate():
        assert asyncio.get_event_loop().time() < deadline, "timed out waiting for pipeline"
        yield asyncio.sleep(0)


def test_pipeline_green_path_runs_every_lane_to_success():
    started: list[str] = []

    async def spawn(lane):
        started.append(lane.name)
        return 0

    result, logs = asyncio.run(_drive(scheduler.build_plan(), spawn))
    assert result["ok"] is True
    assert set(result["states"].values()) == {"success"}
    assert len(started) == 12
    assert logs[-1].startswith("[packaged-recovery] exit 0") or any(
        line == "[packaged-recovery] exit 0" for line in logs
    )


def test_pipeline_opens_phase_two_only_after_full_phase_one_success():
    gates = {lane.name: asyncio.Event() for lane in scheduler.build_plan()}
    started: list[str] = []

    async def spawn(lane):
        started.append(lane.name)
        await gates[lane.name].wait()
        return 0

    async def scenario():
        pipeline = asyncio.create_task(_drive(scheduler.build_plan(), spawn))
        root = {"apt-display", "chromium-sandbox", "i04-matrix", "verify-sources", "static-gates"}
        for _ in _wait_for(lambda: root <= set(started)):
            await _
        assert "engine" not in started
        gates["static-gates"].set()
        for _ in _wait_for(lambda: {"engine", "unit-build"} <= set(started)):
            await _
        # Phase two stays closed while i04-matrix is still running even though
        # its own prerequisites (none) would allow an immediate start.
        assert not {"main-e2e", "package", "i04-unpackaged"} & set(started)
        for gate in gates.values():
            gate.set()
        return await asyncio.wait_for(pipeline, timeout=10.0)

    result, _logs = asyncio.run(scenario())
    assert result["ok"] is True
    assert started.index("main-e2e") > started.index("i04-matrix")
    assert started.index("packaged-recovery") > started.index("verify-package")
    assert started.index("verify-package") > started.index("package")


def test_pipeline_skips_phase_two_and_fails_after_a_phase_one_failure():
    started: list[str] = []

    async def spawn(lane):
        started.append(lane.name)
        return 1 if lane.name == "engine" else 0

    result, logs = asyncio.run(_drive(scheduler.build_plan(), spawn))
    assert result["ok"] is False
    assert result["states"]["engine"] == "failure"
    for lane in ("main-e2e", "package", "verify-package", "packaged-recovery", "i04-unpackaged"):
        assert result["states"][lane] == "skipped"
        assert lane not in started
    # Independent phase-one lanes still drained to their own terminal states.
    assert result["states"]["i04-matrix"] == "success"
    assert any("skipped after an earlier failure" in line for line in logs)


def test_pipeline_skips_only_dependents_of_a_failed_phase_two_lane():
    started: list[str] = []

    async def spawn(lane):
        started.append(lane.name)
        return 1 if lane.name == "package" else 0

    result, _logs = asyncio.run(_drive(scheduler.build_plan(), spawn))
    assert result["ok"] is False
    assert result["states"]["package"] == "failure"
    assert result["states"]["verify-package"] == "skipped"
    assert result["states"]["packaged-recovery"] == "skipped"
    assert "verify-package" not in started
    assert "packaged-recovery" not in started
    # Unrelated phase-two lanes completed; a partial recovery picture still
    # fails the job rather than reporting success.
    assert result["states"]["main-e2e"] == "success"
    assert result["states"]["i04-unpackaged"] == "success"


def test_pipeline_settles_a_lane_whose_spawn_raises_instead_of_escaping():
    async def spawn(lane):
        if lane.name == "static-gates":
            raise RuntimeError("spawn exploded")
        return 0

    result, logs = asyncio.run(_drive(scheduler.build_plan(), spawn))
    assert result["ok"] is False
    assert result["states"]["static-gates"] == "failure"
    assert result["states"]["main-e2e"] == "skipped"
    assert result["states"]["i04-matrix"] == "success"
    assert any("lane failure: RuntimeError: spawn exploded" in line for line in logs)


def test_pipeline_cancellation_settles_every_running_lane_task():
    started: list[str] = []

    async def spawn(lane):
        started.append(lane.name)
        await asyncio.Event().wait()

    async def scenario():
        task = asyncio.create_task(
            scheduler.run_pipeline(scheduler.build_plan(), spawn, lambda _message: None)
        )
        for _ in range(500):
            if len(started) >= 5:
                break
            await asyncio.sleep(0.01)
        task.cancel()
        try:
            await asyncio.wait_for(task, 10)
        except asyncio.CancelledError:
            pass
        # Every lane task the pipeline created has been settled; only the
        # scenario coroutine itself remains as a running task.
        assert len(asyncio.all_tasks() - {asyncio.current_task()}) == 0

    asyncio.run(scenario())
    assert len(started) == 5


@POSIX_LANE_SPAWN
def test_spawn_lane_returns_the_exact_child_exit_code():
    ok = asyncio.run(scheduler.spawn_lane(scheduler.Lane("t-ok", 1, "exit 0")))
    bad = asyncio.run(scheduler.spawn_lane(scheduler.Lane("t-bad", 1, "exit 3")))
    assert (ok, bad) == (0, 3)


@POSIX_LANE_SPAWN
def test_spawn_lane_settles_a_spawn_failure_as_a_lane_failure(monkeypatch):
    async def broken(*_args, **_kwargs):
        raise OSError("no such file or directory")

    monkeypatch.setattr(scheduler.asyncio, "create_subprocess_exec", broken)
    code = asyncio.run(scheduler.spawn_lane(scheduler.Lane("t-spawn", 1, "exit 0")))
    assert code == 127


@POSIX_LANE_SPAWN
def test_spawn_lane_drains_one_very_long_line_without_wedging(capsys):
    lane = scheduler.Lane("t-long", 1, "head -c 300000 /dev/zero | tr '\\0' 'A'")
    code = asyncio.run(asyncio.wait_for(scheduler.spawn_lane(lane), 20.0))
    assert code == 0
    assert capsys.readouterr().out.count("A") >= 300000


@POSIX_LANE_SPAWN
def test_spawn_lane_cancellation_reaps_only_its_own_process_group(tmp_path):
    pidfile = tmp_path / "lane.pid"
    lane = scheduler.Lane("t-kill", 1, f"echo $$ > {pidfile}; sleep 30")

    async def scenario():
        task = asyncio.create_task(scheduler.spawn_lane(lane))
        for _ in range(500):
            if pidfile.exists():
                break
            await asyncio.sleep(0.01)
        child = int(pidfile.read_text(encoding="ascii").strip())
        # The lane bash runs in its own session, not the test's session, so
        # reaping can only ever touch this lane's own descendants.
        assert os.getsid(child) != os.getsid(os.getpid())
        task.cancel()
        try:
            await asyncio.wait_for(task, 15.0)
        except asyncio.CancelledError:
            pass
        return child

    child = asyncio.run(scenario())
    with pytest.raises(ProcessLookupError):
        os.kill(child, 0)
