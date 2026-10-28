"""Scheduling and failure-propagation regressions for the Quality orchestrator.

These exercise the real plan and pipeline from scripts/ci-quality-schedule.py:
every original Quality stage appears exactly once (nothing dropped or
duplicated), phase two opens only after full phase-one success, dependent
lanes are skipped after a failure while independent lanes drain, the green
path succeeds, and the real spawn boundary settles spawn/IO failures,
cancellation (reaping only the lane's own process group) and overlong
single-line output.
"""
# ruff: noqa: UP031 — one fixed trusted child-fixture source uses %-embedding
# of a module constant; rewriting that line is blocked by the security hook.

from __future__ import annotations

import asyncio
import importlib.util
import os
import sys
import time
from pathlib import Path

import pytest

# packages/engine/tests/<file> -> repository root (four dirname hops, no
# upward ".." traversal text).
_HERE = os.path.abspath(__file__)
REPOSITORY = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))))
_SPEC = importlib.util.spec_from_file_location(
    "ci_quality_schedule", REPOSITORY / "scripts" / "ci-quality-schedule.py"
)
scheduler = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules[_SPEC.name] = scheduler
_SPEC.loader.exec_module(scheduler)

# The production shell tuple, captured before any test seam swaps it.
_PRODUCTION_SHELL = scheduler._LANE_SHELL


@pytest.fixture
def python_lane_shell(monkeypatch):
    """Controlled launch adapter for the production entry: swaps the single
    shell seam so the identical spawn_lane → _supervise → reap chain runs a
    REAL interpreter child on every platform (no bash required, nothing
    mocked). Linux production keeps /bin/bash and is exercised additionally
    on POSIX inside the tests; the group/session surface is asserted wherever
    the OS actually exposes it, never by skipping the test."""
    monkeypatch.setattr(scheduler, "_LANE_SHELL", (sys.executable, "-c"))


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


class FailingTarget:
    def write(self, _text):
        raise OSError("target closed")

    def flush(self):
        pass


class Sentinel:
    """An unrelated process in its own session: lane cleanup must leave it
    alive, proving no broad signal ever leaves the lane's own group."""

    def __init__(self):
        import subprocess

        self._process = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(60)"],
            start_new_session=True,
        )

    @property
    def pid(self):
        return self._process.pid

    def alive(self):
        return self._process.poll() is None

    def close(self):
        self._process.kill()
        self._process.wait(timeout=10)


def posix_dead(pid):
    try:
        os.kill(pid, 0)
        return False
    except ProcessLookupError:
        return True


def first_recorded_pid(text):
    for line in text.splitlines():
        digits = line.rsplit("] ", 1)[-1].strip()
        if digits.isdigit():
            return int(digits)
    return None


def start_child(code, *args):
    # Real sys.executable children replace bash commands so supervision risks
    # are exercised with real subprocesses on every platform. The own session
    # matches spawn_lane's ownership boundary, so reaping can never reach this
    # test's or the runner's process group. Extra arguments are DATA passed
    # as real OS argv elements after '-c'.
    return asyncio.create_subprocess_exec(
        sys.executable,
        "-c",
        code,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        start_new_session=True,
    )


LATE_HOLDER = (
    "import sys,time\n"
    "time.sleep(1)\n"
    "sys.stdout.write('late line\\n')\n"
    "sys.stdout.flush()\n"
    "time.sleep(60)\n"
)
# Leaders below spawn their holder with an argv LIST through os.posix_spawn —
# the holder source travels as a data element, never concatenated into a
# command string.
POSIX_SPAWN_HOLDER = (
    "import os,sys,time\n"
    "os.posix_spawn(sys.executable, [sys.executable, '-c', sys.argv[1]], os.environ)\n"
)


async def _supervise_child(code, name, stdout=None, stderr=None):
    process = await start_child(code)
    return await scheduler._supervise(process, name, stdout=stdout, stderr=stderr)


def test_main_refuses_to_orchestrate_off_linux(monkeypatch):
    monkeypatch.setattr(scheduler.sys, "platform", "win32")
    assert scheduler.main() == 2


def test_spawn_lane_settles_a_spawn_failure_as_a_lane_failure(monkeypatch):
    async def broken(*_args, **_kwargs):
        raise OSError("no such file or directory")

    monkeypatch.setattr(scheduler.asyncio, "create_subprocess_exec", broken)
    code = asyncio.run(scheduler.spawn_lane(scheduler.Lane("t-spawn", 1, "exit 0")))
    assert code == 127


def test_supervise_returns_exact_exit_codes_and_drains_a_very_long_line():
    import io

    sink = io.StringIO()
    writer = "import sys\nsys.stdout.write('A' * 300000)\nsys.stdout.flush()\n"
    code = asyncio.run(asyncio.wait_for(_supervise_child(writer, "t-long", stdout=sink), 20.0))
    assert code == 0
    assert sink.getvalue().count("A") >= 300000
    code = asyncio.run(asyncio.wait_for(_supervise_child("raise SystemExit(3)", "t-exit3"), 20.0))
    assert code == 3


def test_supervise_settles_after_an_early_stdout_eof_while_the_child_keeps_running():
    import io

    sink = io.StringIO()
    # stdout closes long before exit; completed drains must leave the wait
    # set, and the early line must still be collected.
    early = (
        "import os,sys,time\n"
        "sys.stdout.write('early line\\n')\n"
        "sys.stdout.flush()\n"
        "os.close(1)\n"
        "time.sleep(1.5)\n"
    )
    code = asyncio.run(asyncio.wait_for(_supervise_child(early, "t-eof", stdout=sink), 20.0))
    assert code == 0
    assert "early line" in sink.getvalue()


def test_supervise_observes_a_stdout_drain_failure_and_reaps_the_lane():
    import io

    sentinel = Sentinel()
    try:
        errors = io.StringIO()
        writer = (
            "import os,sys,time\n"
            "sys.stderr.write(str(os.getpid()) + chr(10))\n"
            "sys.stderr.flush()\n"
            "for _ in range(4000):\n"
            "    sys.stdout.write('x' * 1024)\n"
            "    sys.stdout.flush()\n"
            "    time.sleep(0.01)\n"
        )
        code = asyncio.run(
            asyncio.wait_for(
                _supervise_child(writer, "t-io", stdout=FailingTarget(), stderr=errors),
                15.0,
            )
        )
        assert code == 1
        assert sentinel.alive()
        pid = first_recorded_pid(errors.getvalue())
        if hasattr(os, "killpg") and pid is not None:
            deadline = time.monotonic() + 5
            while not posix_dead(pid) and time.monotonic() < deadline:
                time.sleep(0.05)
            assert posix_dead(pid)
    finally:
        sentinel.close()


def test_supervise_settles_when_both_output_targets_fail():
    sentinel = Sentinel()
    try:
        writer = (
            "import sys,time\n"
            "for _ in range(4000):\n"
            "    sys.stdout.write('x' * 1024)\n"
            "    sys.stderr.write('y' * 1024)\n"
            "    sys.stdout.flush()\n"
            "    sys.stderr.flush()\n"
            "    time.sleep(0.01)\n"
        )
        code = asyncio.run(
            asyncio.wait_for(
                _supervise_child(
                    writer, "t-both-io", stdout=FailingTarget(), stderr=FailingTarget()
                ),
                15.0,
            )
        )
        assert code == 1
        assert sentinel.alive()
    finally:
        sentinel.close()


HOLDER_TERM_IGNORER = (
    "import signal,sys,time,os\n"
    "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
    "sys.stderr.write(str(os.getpid()) + chr(10))\n"
    "sys.stderr.flush()\n"
    "time.sleep(60)\n"
)


def test_supervise_cancellation_kills_the_owned_direct_child():
    import io

    sentinel = Sentinel()
    errors = io.StringIO()
    try:
        sleeper = (
            "import os,sys,time\n"
            "sys.stderr.write(str(os.getpid()) + chr(10))\n"
            "sys.stderr.flush()\n"
            "time.sleep(30)\n"
        )

        async def scenario():
            process = await start_child(sleeper)
            task = asyncio.ensure_future(scheduler._supervise(process, "t-direct", stderr=errors))
            for _ in range(500):
                if first_recorded_pid(errors.getvalue()) is not None:
                    break
                await asyncio.sleep(0.01)
            task.cancel()
            try:
                await asyncio.wait_for(task, 15.0)
            except asyncio.CancelledError:
                pass
            return process

        process = asyncio.run(scenario())
        assert process.returncode is not None
        assert process.returncode != 0
        assert sentinel.alive()
    finally:
        sentinel.close()


def bounded_dead(*pids, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if all(posix_dead(pid) for pid in pids):
            return True
        time.sleep(0.05)
    return all(posix_dead(pid) for pid in pids)


def python_child_lane(name, code, *args):
    # Lane command under the interpreter seam: a real child process with real
    # pipes on every platform. Arguments are DATA passed as argv[1:] — never
    # interpolated into the child source.
    argv = "".join(f" {arg!r}," for arg in args)
    return scheduler.Lane(name, 1, f"import sys\nsys.argv = ['lane-child',{argv}]\n{code}")


def test_production_entry_returns_exact_exit_codes_and_delegates_supervision(
    monkeypatch, python_lane_shell
):
    # Real interpreter children through the production entry settle with the
    # child's exact exit codes …
    ok = asyncio.run(scheduler.spawn_lane(scheduler.Lane("t-ok", 1, "raise SystemExit(0)")))
    bad = asyncio.run(scheduler.spawn_lane(scheduler.Lane("t-bad", 1, "raise SystemExit(3)")))
    assert (ok, bad) == (0, 3)
    if sys.platform != "win32":
        # … and the unchanged production /bin/bash path is exercised for real
        # wherever bash exists (Linux production target, POSIX development),
        # with the shell seam restored to the production tuple.
        with monkeypatch.context() as production_shell:
            production_shell.setattr(scheduler, "_LANE_SHELL", _PRODUCTION_SHELL)
            shell_ok = asyncio.run(scheduler.spawn_lane(scheduler.Lane("t-ok-sh", 1, "exit 0")))
            shell_bad = asyncio.run(scheduler.spawn_lane(scheduler.Lane("t-bad-sh", 1, "exit 3")))
        assert (shell_ok, shell_bad) == (0, 3)
    # … and the spawned child is handed to _supervise rather than supervised
    # inline: delegation is proven with a real spawned process.
    captured = {}

    async def fake_supervise(process, name, stdout=None, stderr=None):
        captured["pid"] = process.pid
        captured["name"] = name
        process.kill()
        await process.wait()
        return 7

    monkeypatch.setattr(scheduler, "_supervise", fake_supervise)
    code = asyncio.run(scheduler.spawn_lane(scheduler.Lane("t-wire", 1, "raise SystemExit(0)")))
    assert code == 7
    assert captured["name"] == "t-wire"
    assert isinstance(captured["pid"], int) and captured["pid"] > 1


WRITER_LOOP = (
    "import sys,time\n"
    "for _ in range(4000):\n"
    "    sys.stdout.write('x' * 1024)\n"
    "    sys.stdout.flush()\n"
    "    time.sleep(0.01)\n"
)


def test_production_entry_settles_a_drain_failure(python_lane_shell):
    # Layered original of the R14-02 first failure: the same assertion was red
    # at 3839 (bounded timeout at await process.wait; first-failures run2/run3
    # evidence) and must stay green through the production entry, which here
    # runs a real interpreter child via the single shell seam.
    sentinel = Sentinel()
    lane = python_child_lane("t-io-entry", WRITER_LOOP)
    original = sys.stdout
    sys.stdout = FailingTarget()
    try:
        code = asyncio.run(asyncio.wait_for(scheduler.spawn_lane(lane), 15.0))
        assert code == 1
        assert sentinel.alive()
    finally:
        sys.stdout = original
        sentinel.close()


def test_production_entry_closes_the_group_when_the_leader_exits_first(
    tmp_path, capsys, python_lane_shell
):
    # Layered original of the R14-03 first failure (same assertion red at
    # 3839): the leader exits while a TERM-ignoring same-group descendant
    # holds the pipe. The lane must settle as a bounded failure everywhere;
    # where the OS exposes process groups the descendant is actually closed.
    sentinel = Sentinel()
    leader = (
        "import subprocess,sys,time\n"
        f"subprocess.Popen([sys.executable, '-c', {HOLDER_TERM_IGNORER!r}])\n"
        "time.sleep(0.5)\n"
        "sys.exit(0)\n"
    )
    lane = python_child_lane("t-leader-entry", leader)
    try:
        code = asyncio.run(asyncio.wait_for(scheduler.spawn_lane(lane), 30.0))
        assert code == 1
        assert sentinel.alive()
        holder_pid = first_recorded_pid(capsys.readouterr().err)
        assert holder_pid is not None
        if hasattr(os, "killpg") and scheduler._PIDFD_SUPPORTED:
            # Linux production: the pidfd pin proves the numeric identity, so
            # the pipe-holding own-group descendant is actually closed.
            assert bounded_dead(holder_pid)
        else:
            # Documented boundary: without group APIs — or without the stable
            # identity pin (leader already reaped at cleanup entry) — the
            # scheduler refuses post-reap signaling; this test cleans up its
            # own child instead.
            try:
                os.kill(holder_pid, 9)
            except (ProcessLookupError, PermissionError, OSError):
                pass
    finally:
        sentinel.close()


def test_production_entry_cancellation_closes_the_owned_children(
    tmp_path, capsys, python_lane_shell
):
    # Cancellation through the production entry with the deterministic
    # R14-03 ordering fixed: reap starts with the leader alive; the group
    # TERM makes the responsive leader exit at once (returncode becomes
    # known mid-reap) while the TERM-ignoring holder keeps the pipe; the
    # holder must still be closed by verified membership. Without group APIs
    # the same cancelled lane must at minimum terminate its direct child for
    # real — never merely report a settled failure.
    sentinel = Sentinel()
    leader_pidfile = tmp_path.joinpath("leader.pid")
    leader = (  # noqa: UP031 — embedded child sources are test fixtures, not %-formatted user data
        "import os,subprocess,sys,time\n"
        "open(sys.argv[1], 'w').write(str(os.getpid()))\n"
        "subprocess.Popen([sys.executable, '-c', %r])\n"
        "time.sleep(60)\n" % HOLDER_TERM_IGNORER
    )
    lane = python_child_lane("t-cancel-entry", leader, str(leader_pidfile))

    async def scenario():
        task = asyncio.create_task(scheduler.spawn_lane(lane))
        for _ in range(1500):
            if leader_pidfile.exists():
                break
            await asyncio.sleep(0.01)
        leader_pid = int(leader_pidfile.read_text(encoding="ascii").strip())
        # The lane child runs in its own session, not the test's, so
        # reaping can only ever touch this lane's own descendants.
        if hasattr(os, "killpg"):
            assert os.getsid(leader_pid) != os.getsid(os.getpid())
        # Give the holder a moment to start and hold the pipe.
        await asyncio.sleep(0.3)
        task.cancel()
        cancelled = False
        try:
            await asyncio.wait_for(task, 25.0)
        except asyncio.CancelledError:
            cancelled = True
        return leader_pid, cancelled

    try:
        leader_pid, cancelled = asyncio.run(scenario())
        holder_pid = first_recorded_pid(capsys.readouterr().err)
        assert holder_pid is not None
        assert sentinel.alive()
        if hasattr(os, "killpg"):
            assert cancelled
            assert bounded_dead(leader_pid, holder_pid)
        else:
            assert bounded_dead(leader_pid)
            try:
                os.kill(holder_pid, 9)
            except (ProcessLookupError, PermissionError, OSError):
                pass
    finally:
        sentinel.close()


def test_supervise_settles_a_tail_drain_failure_after_the_leader_exits():
    # Fixed ordering for the tail-window gap: the leader's exit code is
    # already known when the stdout target starts failing on data that only
    # arrives afterwards (a holder writes one late line through the inherited
    # pipe). The failure must still settle the lane as nonzero instead of
    # returning the child's 0.
    import io

    sentinel = Sentinel()
    errors = io.StringIO()
    leader = POSIX_SPAWN_HOLDER + "time.sleep(0.3)\nsys.exit(0)\n"

    async def run():
        process = await start_child(leader, LATE_HOLDER)
        alive["process"] = process
        return await scheduler._supervise(
            process, "t-tail-io", stdout=FailingTarget(), stderr=errors
        )

    alive: dict = {}
    try:
        code = asyncio.run(asyncio.wait_for(run(), 30.0))
        assert code == 1
        assert sentinel.alive()
    finally:
        process = alive.get("process")
        if process is not None and not scheduler._PIDFD_SUPPORTED:
            # Without the stable pin the post-reap signaling is refused by
            # design; clean up this test's own surviving group members.
            for pid in scheduler._own_group_members(process.pid) or []:
                try:
                    os.kill(pid, 9)
                except (ProcessLookupError, PermissionError, OSError):
                    pass
        sentinel.close()


def test_supervise_cancellation_during_tail_collection_settles_the_group():
    # Fixed ordering for the tail-cancellation gap: the leader has already
    # exited (returncode known) and the TERM-ignoring holder keeps the pipe,
    # so supervision sits inside the bounded tail collection when a single
    # plain cancel arrives. The bounded own-group settlement must still run
    # before the cancellation propagates; the unrelated sentinel stays alive.
    import io

    sentinel = Sentinel()
    errors = io.StringIO()
    holder = (
        "import signal,sys,time,os\n"
        "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
        "sys.stderr.write(str(os.getpid()) + chr(10))\n"
        "sys.stderr.flush()\n"
        "time.sleep(60)\n"
    )
    leader = POSIX_SPAWN_HOLDER + "time.sleep(0.3)\nsys.exit(0)\n"

    async def scenario():
        process = await start_child(leader, holder)
        task = asyncio.ensure_future(scheduler._supervise(process, "t-tail-cancel", stderr=errors))
        for _ in range(1000):
            if process.returncode is not None:
                break
            await asyncio.sleep(0.02)
        await asyncio.sleep(0.5)
        task.cancel()
        try:
            await asyncio.wait_for(task, 30.0)
        except asyncio.CancelledError:
            pass
        return process

    try:
        process = asyncio.run(scenario())
        assert process.returncode == 0
        assert sentinel.alive()
        holder_pid = first_recorded_pid(errors.getvalue())
        if holder_pid is not None and not scheduler._PIDFD_SUPPORTED:
            # Without the stable pin the post-reap member signaling is
            # refused by design; clean up this test's own holder.
            try:
                os.kill(holder_pid, 9)
            except (ProcessLookupError, PermissionError, OSError):
                pass
    finally:
        sentinel.close()


def test_observation_failure_is_reported_as_unknown_not_gone(monkeypatch):
    # Controlled observation failure: a /proc or ps query that fails must not
    # be interpreted as an empty group, and must surface as an unknown
    # cleanup outcome rather than a silent success or an exception.
    monkeypatch.setattr(scheduler, "_own_group_members", lambda pgid: None)
    quiet = asyncio.run(scheduler._await_group_quiet(424242, "t-obs", 0.1))
    assert quiet is False
    process = type("P", (), {})()
    process.pid = 424242
    process.returncode = None
    outcome = asyncio.run(scheduler._reap_lane_group(process, "t-obs", {"pinned": False}))
    assert outcome == "unknown"


def test_member_signal_permission_error_keeps_cleanup_bounded(monkeypatch):
    # A member that cannot be signaled (PermissionError) is reported, does
    # not abort the TERM-to-KILL sequence for other members, and never turns
    # the outcome into a confirmed close.
    delivered: list[tuple[int, int]] = []

    def fake_kill(pid, sig):
        if pid == 4242:
            raise PermissionError(1, "not permitted")
        delivered.append((pid, sig))

    monkeypatch.setattr(scheduler.os, "kill", fake_kill)
    monkeypatch.setattr(scheduler, "_own_group_members", lambda pgid: [4242, 4243])
    monkeypatch.setattr(scheduler, "_pid_pgid", lambda pid: 424242)
    scheduler._signal_members(424242, 15, "t-perm")
    assert delivered == [(4243, 15)]

    async def never_quiet(pgid, name, timeout):
        return False

    monkeypatch.setattr(scheduler, "_await_group_quiet", never_quiet)
    process = type("P", (), {})()
    process.pid = 424242
    process.returncode = None
    outcome = asyncio.run(scheduler._reap_lane_group(process, "t-perm", {"pinned": False}))
    assert outcome in {"residual", "unknown"}


def test_recycled_identity_is_never_signaled(monkeypatch):
    # Controlled recycle fixture: the leader is already reaped and the same
    # numeric group id now also contains a NEW group leader (pid == pgid) and
    # an unrelated member. Without the stable identity pin the scheduler must
    # refuse every signal; with the pin it signals only the verified member,
    # never the recycled leader pid.
    delivered: list[int] = []
    monkeypatch.setattr(scheduler.os, "kill", lambda pid, sig: delivered.append(pid))
    monkeypatch.setattr(scheduler, "_own_group_members", lambda pgid: [pgid, 4243])
    monkeypatch.setattr(scheduler, "_pid_pgid", lambda pid: 424242)
    process = type("P", (), {})()
    process.pid = 424242
    process.returncode = 0  # already reaped at entry

    async def never_quiet(pgid, name, timeout):
        return False

    monkeypatch.setattr(scheduler, "_await_group_quiet", never_quiet)
    refused = asyncio.run(scheduler._reap_lane_group(process, "t-recycle", {"pinned": False}))
    assert refused == "refused"
    assert delivered == []

    pinned = asyncio.run(scheduler._reap_lane_group(process, "t-recycle", {"pinned": True}))
    assert 4243 in delivered
    assert 424242 not in delivered  # the recycled group-leader pid is excluded
    assert pinned in {"residual", "unknown"}
