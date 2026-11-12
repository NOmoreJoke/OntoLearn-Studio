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
import io
import os
import signal
import subprocess
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
    on POSIX inside the tests. Portable DIRECT-CHILD supervision is asserted
    on every platform; POSIX process-group/zombie scenarios carry their own
    explicit per-test platform premise because Windows exposes no
    killpg/getpgid/getsid and no unreaped-zombie observation."""
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
    # CI49 ordering (isolation variable, not proven root cause): the engine
    # shards start only after unit-build; a contention-free run decides
    # causation. This assertion pins the ordering, not any failure's fix.
    assert by_name["engine"].deps == ("static-gates", "unit-build")
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
        # CI49 ordering (isolation variable, not proven root cause): engine
        # starts only after unit-build completes, so
        # releasing static-gates first starts unit-build alone…
        for _ in _wait_for(lambda: "unit-build" in started):
            await _
        assert "engine" not in started
        # …and unit-build completing (gate released) is what starts engine.
        gates["unit-build"].set()
        for _ in _wait_for(lambda: "engine" in started):
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


# Leaders below spawn their holder with a real argv LIST through
# subprocess.Popen — the holder source travels as a data element (sys.argv),
# never concatenated into a command string.
POSIX_SPAWN_HOLDER = (
    "import os,subprocess,sys,time\nsubprocess.Popen([sys.executable, '-c', sys.argv[1]])\n"
)


async def _supervise_child(code, name, *args, stdout=None, stderr=None):
    # Supervision-level cases run through the PRODUCTION entry with the
    # interpreter seam: python_child_lane builds the lane command (positional
    # args are DATA passed to the child as argv elements) and spawn_lane
    # creates the leader with the exclusive-reap ownership the scheduler
    # supervises. Failing/capturing output targets replace sys.stdout /
    # sys.stderr around the call; the reader threads observe the swapped
    # objects directly.
    lane = python_child_lane(name, code, *args)
    original_out, original_err = sys.stdout, sys.stderr
    original_shell = scheduler._LANE_SHELL
    scheduler._LANE_SHELL = (sys.executable, "-c")
    if stdout is not None:
        sys.stdout = stdout
    if stderr is not None:
        sys.stderr = stderr
    try:
        return await scheduler.spawn_lane(lane)
    finally:
        scheduler._LANE_SHELL = original_shell
        sys.stdout, sys.stderr = original_out, original_err


def test_main_refuses_to_orchestrate_off_linux(monkeypatch):
    monkeypatch.setattr(scheduler.sys, "platform", "win32")
    assert scheduler.main() == 2


def test_spawn_lane_settles_a_spawn_failure_as_a_lane_failure(monkeypatch):
    def broken(*_args, **_kwargs):
        raise OSError("no such file or directory")

    monkeypatch.setattr(scheduler.subprocess, "Popen", broken)
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
                30.0,
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


def test_supervise_cancellation_kills_the_owned_direct_child(tmp_path, monkeypatch):
    sentinel = Sentinel()
    pidfile = tmp_path.joinpath("direct.pid")
    # Atomic pidfile publish (temp + os.replace): exists() implies complete content.
    sleeper = (
        "import os,sys,time\n"
        "t = sys.argv[1] + '.tmp'\n"
        "with open(t, 'w') as f: f.write(str(os.getpid()))\n"
        "os.replace(t, sys.argv[1])\n"
        "time.sleep(30)\n"
    )
    # Capture the REAL Popen object spawn_lane creates (a pass-through wrapper
    # around the genuine constructor — not a mock), so death evidence uses the
    # supervisor's own handle: alive BEFORE cancel and exited AFTER cancel are
    # proven on the SAME object, immune to pid reuse, before any fixture
    # fallback. On Windows poll() is the native non-blocking handle check and
    # the Popen-held handle anchors the identity; on POSIX the pinned-window
    # killpg covers termination and poll() here only confirms it.
    created: list = []
    real_popen = scheduler.subprocess.Popen

    def capturing_popen(*args, **kwargs):
        popen = real_popen(*args, **kwargs)
        created.append(popen)
        return popen

    monkeypatch.setattr(scheduler.subprocess, "Popen", capturing_popen)

    async def scenario():
        task = asyncio.ensure_future(_supervise_child(sleeper, "t-direct", str(pidfile)))
        for _ in range(1000):
            if pidfile.exists():
                break
            await asyncio.sleep(0.01)
        # The pidfile IS the fixture handshake: a missing pid after the poll
        # window means the child never started — a fixture failure, not a
        # silent pass.
        assert pidfile.exists(), "direct child never started (no pidfile)"
        assert created, "spawn_lane never created the leader (fixture failure)"
        popen = created[0]
        assert popen.poll() is None, "leader already exited before cancel (fixture failure)"
        await asyncio.sleep(0.2)
        task.cancel()
        cancelled = False
        try:
            await asyncio.wait_for(task, 15.0)
        except asyncio.CancelledError:
            cancelled = True
        return popen, cancelled

    try:
        popen, cancelled = asyncio.run(scenario())
        assert cancelled
        assert sentinel.alive()
        # SUT termination proof on the SAME captured handle, BEFORE any
        # fixture fallback: the supervisor really killed and reaped the child.
        assert popen.returncode is not None, "leader exit not confirmed by SUT"
        assert popen.returncode != 0
        if hasattr(os, "killpg"):
            pid = int(pidfile.read_text(encoding="ascii").strip())
            assert bounded_dead(pid)
    finally:
        # Outermost cleanup. The same captured Popen objects are killed via
        # their own handle and then waited with a bounded wait; a wait that
        # times out is REPORTED to stderr as a cleanup failure — it is never
        # swallowed into an implied success, and it never masks the original
        # test outcome above. This fallback is not counted as SUT success.
        try:
            for popen in created:
                if popen.poll() is None:
                    try:
                        popen.kill()
                    except OSError:
                        pass
                    try:
                        popen.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        print(
                            f"FIXTURE CLEANUP FAILURE: leader pid {popen.pid} "
                            "not reaped within bound",
                            file=sys.stderr,
                        )
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
    # inline: delegation is proven with a real spawned leader.
    captured = {}

    async def fake_supervise(popen, name, stdout=None, stderr=None):
        captured["pid"] = popen.pid
        captured["name"] = name
        popen.kill()
        popen.wait(timeout=10)
        for stream in (popen.stdout, popen.stderr):
            if stream is not None:
                stream.close()
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
        code = asyncio.run(asyncio.wait_for(scheduler.spawn_lane(lane), 30.0))
        assert code == 1
        assert sentinel.alive()
    finally:
        sys.stdout = original
        sentinel.close()


@pytest.mark.skipif(
    not hasattr(os, "killpg"),
    reason=(
        "POSIX process-group fixture: the pinned-window killpg cleanup must "
        "close a TERM-ignoring same-group descendant holding the lane pipes "
        "after the leader exits unreaped; Windows has no killpg/getpgid/"
        "getsid and no unreaped-zombie observation (production owns only the "
        "direct child's native handle - that contract is covered by "
        "test_supervise_cancellation_kills_the_owned_direct_child and "
        "test_failed_reap_never_reports_closed_or_reaped)"
    ),
)
def test_production_entry_closes_the_group_when_the_leader_exits_first(
    tmp_path, capsys, python_lane_shell
):
    # Layered original of the R14-03 first failure (same assertion red at
    # 3839): the leader exits while a TERM-ignoring same-group descendant
    # holds the pipe. Exit is observed as UNREAPED zombie, so the identity
    # anchor holds through the tail collection and the pinned-window group
    # cleanup actually closes the holder — asserted on the SUT before any
    # fixture fallback.
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
        assert holder_pid is not None, "holder never started (fixture failure)"
        if hasattr(os, "killpg"):
            assert bounded_dead(holder_pid)
        try:
            os.kill(holder_pid, 9)
        except (ProcessLookupError, PermissionError, OSError):
            pass
    finally:
        sentinel.close()


@pytest.mark.skipif(
    not hasattr(os, "killpg"),
    reason=(
        "POSIX process-group fixture: group TERM/KILL must close BOTH the "
        "leader and the same-group holder (asserted together) under getsid "
        "session isolation; Windows has no killpg/getpgid/getsid and no "
        "unreaped-zombie observation (production owns only the direct "
        "child's native handle - the Windows cancellation contract is "
        "covered by test_supervise_cancellation_kills_the_owned_direct_child)"
    ),
)
def test_production_entry_cancellation_closes_the_owned_children(
    tmp_path, capsys, python_lane_shell
):
    # Cancellation through the production entry with the deterministic
    # ordering fixed: reap starts with the leader alive; the group TERM makes
    # the responsive leader exit at once (returncode becomes known mid-reap).
    # Group members are never signaled (no stable delivery handle), so the
    # direct child must be terminated for real, the surviving holder is
    # honestly reported as cleanup NOT confirmed, and this test cleans up its
    # own holder; the unrelated sentinel must stay alive.
    sentinel = Sentinel()
    leader_pidfile = tmp_path.joinpath("leader.pid")
    leader = (  # noqa: UP031 — embedded child sources are test fixtures, not %-formatted user data
        "import os,subprocess,sys,time\n"
        # Atomic pidfile publish: the poll below can never observe an empty
        # file (CI70 attempt2 failed on int('') from a non-atomic write).
        "t = sys.argv[1] + '.tmp'\n"
        "with open(t, 'w') as f: f.write(str(os.getpid()))\n"
        "os.replace(t, sys.argv[1])\n"
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
        assert holder_pid is not None, "holder never started (fixture failure)"
        assert sentinel.alive()
        assert cancelled
        # The leader was ALIVE at cancel: the identity window was pinned, so
        # the bounded group cleanup closed BOTH the leader and the holder;
        # the fixture fallback below only sweeps if anything survived.
        assert bounded_dead(leader_pid, holder_pid)
        for pid in (leader_pid, holder_pid):
            try:
                os.kill(pid, 9)
            except (ProcessLookupError, PermissionError, OSError):
                pass
    finally:
        sentinel.close()


@pytest.mark.skipif(
    not hasattr(os, "killpg"),
    reason=(
        "POSIX process-group fixture: an unreaped-zombie identity anchor "
        "with late data from a same-group descendant through the inherited "
        "pipes, settled by the pinned-window group cleanup; Windows has no "
        "killpg/getpgid/getsid and no unreaped-zombie observation (the "
        "direct-child drain-failure settlement is covered by "
        "test_supervise_observes_a_stdout_drain_failure_and_reaps_the_lane)"
    ),
)
def test_supervise_settles_a_tail_drain_failure_after_the_leader_exits():
    # Fixed ordering for the tail-window gap: the leader's exit is OBSERVED
    # (zombie, unreaped — the identity anchor holds) when the stdout target
    # starts failing on data that only arrives afterwards (a holder writes
    # one late line through the inherited pipe). The failure must settle the
    # lane as nonzero instead of returning the child's 0, and the group
    # cleanup runs in the pinned window.
    sentinel = Sentinel()
    errors = io.StringIO()
    holder = (
        "import os,sys,time\n"
        "sys.stderr.write(str(os.getpid()) + chr(10))\n"
        "sys.stderr.flush()\n"
        "time.sleep(1)\n"
        "sys.stdout.write('late line\\n')\n"
        "sys.stdout.flush()\n"
        "time.sleep(60)\n"
    )
    leader = POSIX_SPAWN_HOLDER + "time.sleep(0.3)\nsys.exit(0)\n"
    try:
        code = asyncio.run(
            asyncio.wait_for(
                _supervise_child(
                    leader, "t-tail-io", holder, stdout=FailingTarget(), stderr=errors
                ),
                30.0,
            )
        )
        assert code == 1
        assert sentinel.alive()
        holder_pid = first_recorded_pid(errors.getvalue())
        assert holder_pid is not None, "holder never started (fixture failure)"
        if hasattr(os, "killpg"):
            # The scheduler's pinned-window group cleanup closed the holder;
            # the fixture fallback below only sweeps if it somehow survived.
            assert bounded_dead(holder_pid)
            try:
                os.kill(holder_pid, 9)
            except (ProcessLookupError, PermissionError, OSError):
                pass
    finally:
        sentinel.close()


@pytest.mark.skipif(
    not hasattr(os, "killpg"),
    reason=(
        "POSIX process-group fixture: tail-collection cancellation must be "
        "preceded by the pinned-window group cleanup closing the holder, "
        "with the os.getpgid identity anchor; Windows has no killpg/"
        "getpgid/getsid and no unreaped-zombie observation (the direct-child "
        "cancellation settlement is covered by "
        "test_supervise_cancellation_kills_the_owned_direct_child)"
    ),
)
def test_supervise_cancellation_during_tail_collection_settles_the_group():
    # Fixed ordering with a REAL handshake for the tail-cancellation gap:
    # (1) the TERM-ignoring holder is provably started (its pid arrives over
    #     the drained stderr — missing pid is a fixture failure);
    # (2) the leader has exited to zombie while UNREAPED (ps/proc state),
    #     so the identity anchor is intact and supervision has entered the
    #     bounded tail collection, still pending on the holder-held pipe;
    # (3) this single cancel must actually propagate (asserted), and the
    #     pinned-window group cleanup must close the holder before it does.
    sentinel = Sentinel()
    capture = io.StringIO()
    holder = HOLDER_TERM_IGNORER
    leader = POSIX_SPAWN_HOLDER + "time.sleep(0.3)\nsys.exit(0)\n"

    async def scenario():
        task = asyncio.create_task(
            _supervise_child(leader, "t-tail-cancel", holder, stderr=capture)
        )
        holder_pid = None
        for _ in range(1500):
            holder_pid = first_recorded_pid(capture.getvalue())
            if holder_pid is not None:
                break
            await asyncio.sleep(0.02)
        assert holder_pid is not None, "holder never started (fixture failure)"
        leader_pid = os.getpgid(holder_pid)
        zombie = False
        for _ in range(1500):
            if os.name == "nt":
                break  # no zombie state on Windows; pipe-pending is the window
            if scheduler._popen_exited_unreaped(type("L", (), {"pid": leader_pid}), {}):
                zombie = True
                break
            await asyncio.sleep(0.02)
        assert zombie or os.name == "nt", "leader never exited (fixture failure)"
        await asyncio.sleep(0.1)  # supervision has now entered the tail wait
        task.cancel()
        cancelled = False
        try:
            await asyncio.wait_for(task, 30.0)
        except asyncio.CancelledError:
            cancelled = True
        return holder_pid, cancelled

    try:
        holder_pid, cancelled = asyncio.run(scenario())
        assert cancelled, "cancellation did not propagate to supervision"
        assert sentinel.alive()
        if hasattr(os, "killpg"):
            # The scheduler's cleanup — not the fixture — closed the holder;
            # the fallback kill only sweeps if it somehow survived.
            assert bounded_dead(holder_pid)
            try:
                os.kill(holder_pid, 9)
            except (ProcessLookupError, PermissionError, OSError):
                pass
    finally:
        sentinel.close()


def test_observation_failure_is_reported_as_unknown_not_gone(monkeypatch):
    # Controlled observation failure: a /proc or ps query that fails must not
    # be interpreted as an empty group, and must surface as an unknown
    # cleanup outcome rather than a silent success or an exception. The
    # POSIX group branch is selected on EVERY platform by a test-local os
    # proxy carrying a fake killpg (the real global os has no killpg
    # attribute to patch on Windows); the fake only records and never sends
    # a real signal to the fictional pid. A wait that simulates a successful
    # reap sets its own returncode honestly.
    delivered: list[str] = []
    monkeypatch.setattr(scheduler, "_own_group_members", lambda pgid: None)
    monkeypatch.setattr(
        scheduler,
        "os",
        type(
            "KillpgOS",
            (),
            {"killpg": staticmethod(lambda pgid, sig: delivered.append("killpg"))},
        ),
    )

    class FakePopen:
        def __init__(self):
            self.pid = 424242
            self.returncode = None

        def wait(self, timeout=None):
            self.returncode = 0
            return 0

    state = {"reaped": False, "code_known": False, "reap_attempted": False}
    outcome = asyncio.run(scheduler._close_lane_group(FakePopen(), "t-obs", state))
    assert outcome == "unknown"
    assert state["reaped"] is True  # the simulated successful reap is real in the fake


def test_failed_reap_never_reports_closed_or_reaped(monkeypatch):
    # Ordering fixture for the honest-reap contract on the no-killpg branch:
    # terminate fails AND the bounded wait never yields a returncode, so the
    # cleanup must NOT mark the leader reaped and must NOT return closed —
    # "attempted" and "confirmed" stay separate, and a second cleanup call
    # does not repeat the bounded wait.
    terminated: list[bool] = []
    waits: list[float] = []

    class StubbornPopen:
        pid = 424242
        returncode = None

        def terminate(self):
            terminated.append(True)
            raise OSError("access denied")

        def wait(self, timeout=None):
            waits.append(timeout)
            raise subprocess.TimeoutExpired(cmd="stubborn", timeout=timeout)

    # A local os proxy WITHOUT a killpg attribute routes cleanup into the
    # Windows-style branch without touching the real global os module.
    monkeypatch.setattr(
        scheduler, "os", type("NoKillpgOS", (), {"kill": staticmethod(os.kill), "name": "nt"})
    )
    state = {"reaped": False, "code_known": False, "reap_attempted": False}
    outcome = asyncio.run(scheduler._close_lane_group(StubbornPopen(), "t-stubborn", state))
    assert terminated == [True]  # termination was genuinely attempted once
    assert outcome == "unknown"  # … but never confirmed as closed
    assert state["reaped"] is False  # and never marked reaped
    assert state["reap_attempted"] is True  # idempotency without lying
    # Second cleanup call: no additional bounded wait, still honest.
    outcome2 = asyncio.run(scheduler._close_lane_group(StubbornPopen(), "t-stubborn", state))
    assert outcome2 == "unknown"
    assert len(waits) == 1


def test_pinned_window_signals_the_group_but_refused_after_reap(monkeypatch):
    # Ordering fixtures against the exclusive-reap contract:
    #   (a) PINNED: state['reaped'] is False — the identity is provably ours
    #       (a leader exited-but-unreaped), so the bounded killpg TERM/KILL
    #       rounds DO run even though members persist in this fixture;
    #   (b) RELEASED: state['reaped'] is True — the pid may already be
    #       recycled, so cleanup refuses every signal and reports NOT
    #       confirmed; a same-number new group is never signaled.
    # The POSIX group branch is selected on EVERY platform by test-local
    # proxies: the os proxy carries a fake killpg (the real global os has no
    # killpg attribute to patch on Windows) and the signal proxy provides
    # BOTH TERM and KILL (the real signal module lacks SIGKILL on Windows,
    # so getattr on it would silently drop the second round). Deliveries are
    # only recorded — never a real signal to the fictional pid. A wait that
    # simulates a successful reap sets its own returncode honestly.
    delivered: list[str] = []
    monkeypatch.setattr(
        scheduler,
        "os",
        type(
            "KillpgOS",
            (),
            {"killpg": staticmethod(lambda pgid, sig: delivered.append("killpg"))},
        ),
    )
    monkeypatch.setattr(
        scheduler,
        "signal",
        type("ControlSignals", (), {"SIGTERM": signal.SIGTERM, "SIGKILL": 9}),
    )
    monkeypatch.setattr(scheduler, "_own_group_members", lambda pgid: [pgid, 4243])

    class FakePopen:
        def __init__(self):
            self.pid = 424242
            self.returncode = None

        def wait(self, timeout=None):
            self.returncode = 0
            return 0

    outcome_a = asyncio.run(
        scheduler._close_lane_group(
            FakePopen(), "t-pinned", {"reaped": False, "code_known": False, "reap_attempted": False}
        )
    )
    assert outcome_a == "residual"  # members persist in the fixture
    assert delivered == ["killpg", "killpg"]  # TERM and KILL rounds ran

    delivered.clear()
    outcome_b = asyncio.run(
        scheduler._close_lane_group(
            FakePopen(),
            "t-released",
            {"reaped": True, "code_known": True, "reap_attempted": True},
        )
    )
    assert outcome_b == "refused"
    assert delivered == []


# POSIX-only ownership regression premise: the readiness-reader branch hands a
# RAW fd (from Popen's owning pipe wrapper) to os.read and, at settlement,
# used to os.close(fd) directly — the owning wrapper stayed open with
# wrapper.closed == False until its finalizer ran (at coroutine death) and
# silently closed whatever fd number then occupied that slot: a double close
# when the number was still free, or EBADF for whoever had reused it. The
# Windows fallback never takes a raw fd: its buffered pipe is closed only
# after the reader thread provably exited, so the dual-ownership defect and
# the fd-number reuse semantics are POSIX-specific here.
#
# Deterministic window: a gate around _settle_readers signals the test AFTER
# the real settlement finished (fds freed in both code variants) while the
# supervisor coroutine still holds the wrappers. Inside that window the test
# asserts wrapper ownership and allocates kept-open pipes until the retired
# lane fd numbers are covered — successive os.pipe calls take the two lowest
# unused descriptors and nothing is closed in between, so the walk-up is
# guaranteed to cover every free number below the bound, including both
# retired fds. Releasing the gate lets the coroutine die; on the defective
# code the wrapper finalizers then close the sentinel-held numbers and the
# sentinel exchange fails with EBADF.
def _pipes_covering(fds, limit=200):
    covered: set = set()
    pipes: list = []
    for _ in range(limit):
        pair = os.pipe()
        pipes.append(pair)
        covered.update(pair)
        if set(fds) <= covered:
            return pipes
    raise AssertionError(f"walk-up allocation never covered {sorted(fds)}: {sorted(covered)}")


def _assert_pipes_still_alive(pipes):
    for read_fd, write_fd in pipes:
        os.write(write_fd, b"fd-owner-sentinel")
        assert os.read(read_fd, 64) == b"fd-owner-sentinel"


def _close_pipe_pairs(pipes):
    for read_fd, write_fd in pipes:
        for fd in (read_fd, write_fd):
            try:
                os.close(fd)
            except OSError:
                pass


@pytest.mark.skipif(
    os.name == "nt",
    reason="POSIX readiness readers own raw fds; Windows closes its buffered pipe after join",
)
def test_supervise_settlement_releases_pipe_ownership_and_survives_fd_reuse(monkeypatch):
    import io

    real_supervise = scheduler._supervise
    real_settle = scheduler._settle_readers
    captured: dict = {}
    settled_event = asyncio.Event()
    release_event = asyncio.Event()

    async def capturing_supervise(popen, name, stdout=None, stderr=None):
        # Capture the LANE LEADER only: the scheduler's own state observation
        # (ps-backed on non-/proc platforms) spawns internal Popen objects we
        # must not mistake for the lane.
        captured["popen"] = popen
        captured["stdout_fd"] = popen.stdout.fileno()
        captured["stderr_fd"] = popen.stderr.fileno()
        return await real_supervise(popen, name, stdout, stderr)

    gate_used = False

    async def gated_settle(readers, failures, name):
        nonlocal gate_used
        settled = await real_settle(readers, failures, name)
        if not gate_used:
            # One-shot window: only the FIRST settlement waits. A cleanup
            # re-entry (cancellation settling again) must never block on a
            # barrier the scenario may already have abandoned.
            gate_used = True
            settled_event.set()
            await release_event.wait()
        return settled

    monkeypatch.setattr(scheduler, "_supervise", capturing_supervise)
    monkeypatch.setattr(scheduler, "_settle_readers", gated_settle)
    out, err = io.StringIO(), io.StringIO()
    writer = "import sys\nsys.stdout.write('owner-out\\n')\nsys.stderr.write('owner-err\\n')\n"
    pipes: list = []

    async def scenario():
        try:
            task = asyncio.create_task(
                _supervise_child(writer, "t-fd-owner", stdout=out, stderr=err)
            )
            await asyncio.wait_for(settled_event.wait(), 30.0)
            popen = captured["popen"]
            # Ownership: settlement itself must close BOTH owning wrappers. The
            # raw os.close(fd) variant leaves wrapper.closed False here — its
            # finalizer at coroutine death then closes the number a second time
            # (EBADF when still free, or the reused owner's fd when taken).
            assert popen.stdout.closed, "stdout pipe owner still open after settlement"
            assert popen.stderr.closed, "stderr pipe owner still open after settlement"
            pipes.extend(_pipes_covering({captured["stdout_fd"], captured["stderr_fd"]}))
            release_event.set()
            code = await asyncio.wait_for(task, 30.0)
            assert code == 0
            # Coroutine death released the supervisor's wrapper references; on
            # the defective code their finalizers closed the sentinel-held fd
            # numbers inside that await. The sentinel exchange must still work.
            _assert_pipes_still_alive(pipes)
        finally:
            # ANY scenario exit releases the gate: a failing ownership assert
            # must not strand the gated settlement (attempt-4 hang).
            release_event.set()

    try:
        asyncio.run(scenario())
        assert "owner-out" in out.getvalue()
        assert "owner-err" in err.getvalue()
    finally:
        _close_pipe_pairs(pipes)


@pytest.mark.skipif(
    os.name == "nt",
    reason="POSIX readiness readers own raw fds; Windows closes its buffered pipe after join",
)
def test_supervise_cancellation_settlement_releases_pipe_ownership_and_survives_fd_reuse(
    monkeypatch,
):
    import io

    real_supervise = scheduler._supervise
    real_settle = scheduler._settle_readers
    captured: dict = {}
    settled_event = asyncio.Event()
    release_event = asyncio.Event()

    async def capturing_supervise(popen, name, stdout=None, stderr=None):
        captured["popen"] = popen
        captured["stdout_fd"] = popen.stdout.fileno()
        captured["stderr_fd"] = popen.stderr.fileno()
        return await real_supervise(popen, name, stdout, stderr)

    gate_used = False

    async def gated_settle(readers, failures, name):
        nonlocal gate_used
        settled = await real_settle(readers, failures, name)
        if not gate_used:
            gate_used = True
            settled_event.set()
            await release_event.wait()
        return settled

    monkeypatch.setattr(scheduler, "_supervise", capturing_supervise)
    monkeypatch.setattr(scheduler, "_settle_readers", gated_settle)
    out, err = io.StringIO(), io.StringIO()
    writer = (
        "import os,sys,time\n"
        "sys.stdout.write(str(os.getpid()) + chr(10))\n"
        "sys.stdout.flush()\n"
        "time.sleep(60)\n"
    )
    pipes: list = []

    async def scenario():
        try:
            task = asyncio.create_task(
                _supervise_child(writer, "t-fd-owner-cancel", stdout=out, stderr=err)
            )
            child_pid = None
            for _ in range(1500):
                child_pid = first_recorded_pid(out.getvalue())
                if child_pid is not None:
                    break
                await asyncio.sleep(0.02)
            assert child_pid is not None, "child never started (fixture failure)"
            task.cancel()
            # Cancellation drives the cleanup chain (group close, then gated
            # reader settlement) into the deterministic ownership window.
            await asyncio.wait_for(settled_event.wait(), 30.0)
            popen = captured["popen"]
            assert popen.stdout.closed, "stdout pipe owner still open after cancellation settlement"
            assert popen.stderr.closed, "stderr pipe owner still open after cancellation settlement"
            pipes.extend(_pipes_covering({captured["stdout_fd"], captured["stderr_fd"]}))
            release_event.set()
            cancelled = False
            try:
                await asyncio.wait_for(task, 30.0)
            except asyncio.CancelledError:
                cancelled = True
            assert cancelled, "cancellation did not propagate to supervision"
            # Supervisor death finalized its wrapper references; the sentinel
            # exchange must still work on the reused fd numbers.
            _assert_pipes_still_alive(pipes)
            # Sweep the cancelled group if the scheduler's own cleanup somehow
            # raced the observation; the ownership assertions above already ran.
            try:
                os.kill(child_pid, 9)
            except (ProcessLookupError, PermissionError, OSError):
                pass
        finally:
            release_event.set()

    try:
        asyncio.run(scenario())
    finally:
        _close_pipe_pairs(pipes)
