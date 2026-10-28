"""Parallel stage orchestration for the Linux Quality CI job (O098).

Every original Quality step keeps its exact command, environment and
evidence directory; only scheduling changes. Independent stages overlap
(install/toolchain prep during the static gates, engine shards beside the
TypeScript lanes, packaging and recovery lanes inside the main e2e window)
under GitHub-step-equivalent failure semantics: a failed lane stops new
lanes, skips its dependents, drains running lanes for evidence, and fails
the job. No test, assertion, budget, or successor gate is removed.
"""

from __future__ import annotations

import asyncio
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Lane:
    name: str
    phase: int
    command: str
    deps: tuple[str, ...] = ()
    env: dict[str, str] = field(default_factory=dict)


# Lane-local cleanup bounds; they bound per-lane teardown inside the original
# job budget and never extend it.
_REAP_WAIT_S = 5.0
_MEMBER_WAIT_S = 2.0
_DRAIN_BOUND_S = 10.0
_EXIT_POLL_S = 0.2
_LANE_SHELL = ("/bin/bash", "-e", "-c")
# Linux production offers pidfd as the stable process-identity handle: an open
# pidfd prevents the leader pid from being recycled for this lane's lifetime.
_PIDFD_SUPPORTED = hasattr(os, "pidfd_open") and sys.platform == "linux"


def build_plan() -> list[Lane]:
    return [
        Lane("apt-display", 1, "sudo apt-get update && sudo apt-get install -y openbox xdotool"),
        Lane(
            "chromium-sandbox",
            1,
            "./node_modules/.bin/install-electron "
            "&& sudo chown root:root node_modules/electron/dist/chrome-sandbox "
            "&& sudo chmod 4755 node_modules/electron/dist/chrome-sandbox "
            "&& stat -c '%U:%G %a %n' node_modules/electron/dist/chrome-sandbox",
        ),
        Lane(
            "i04-matrix",
            1,
            "uv run --frozen python -m pytest -p scripts.i04_matrix_evidence "
            "--i04-matrix-evidence build/i04-matrix-ci "
            "--i04-matrix-source-revision HEAD "
            "packages/engine/tests/test_job_store.py::test_atomic_job_fault_reconcile_matrix "
            "packages/engine/tests/test_i04_round_faults.py"
            "::test_round_job_progress_atomic_fault_matrix_fences_and_preserves_previous_round "
            "-q",
        ),
        Lane("verify-sources", 1, "npm run verify:sources"),
        Lane(
            "static-gates",
            1,
            "npm run lint && npm run format:check && npm run typecheck",
        ),
        Lane(
            "engine",
            1,
            "npm run engine:check",
            deps=("static-gates",),
            env={
                "CI_ENGINE_TEST_SHARDS": "4",
                "CI_ENGINE_TEST_WEIGHTS": "linux-ci46",
            },
        ),
        Lane("unit-build", 1, "npm test && npm run build", deps=("static-gates",)),
        Lane(
            "main-e2e",
            2,
            "xvfb-run -a sh -c 'openbox > /tmp/i04-openbox.log 2>&1 & "
            "npm run test:e2e -- --reporter=list,github,json --output=test-results/main'",
            env={
                "DEBUG": "pw:browser",
                "I02_EVIDENCE": "test-results/i02-linux-evidence.json",
                "PLAYWRIGHT_JSON_OUTPUT_FILE": "test-results/main/report.json",
            },
        ),
        # The unpackaged e2e lanes launch apps/desktop from its built out/
        # tree, and the desktop build empties and rewrites that tree; the
        # shared out/ is therefore written exactly once, in phase one. This
        # lane consumes the same-commit phase-one build (engine bundle plus
        # electron-builder only) instead of rebuilding it, so it never writes
        # out/ while e2e lanes read it.
        Lane(
            "package",
            2,
            "npm run engine:build && npm run package:dir --workspace @ontolearn/desktop",
            deps=("unit-build",),
        ),
        Lane(
            "verify-package",
            2,
            "uv run --frozen python scripts/verify-i04-package.py release build/i04-package-ci",
            deps=("package",),
        ),
        Lane(
            "i04-unpackaged",
            2,
            "uv run --frozen python scripts/prepare-i04-fixture.py build/i04-native-ci\n"
            'I04_TEST_FIXTURE="$GITHUB_WORKSPACE/build/i04-native-ci/fixture.json" '
            "I04_NATIVE_ISOLATED=1 "
            "PLAYWRIGHT_JSON_OUTPUT_FILE=test-results/i04-native/report.json "
            "xvfb-run -a sh -c 'openbox > /tmp/i04-native-openbox.log 2>&1 & "
            'npx playwright test tests/e2e/i04-jobs.spec.ts --grep "native renderer" '
            "--output=test-results/i04-native --reporter=list,github,json'\n"
            "uv run --frozen python scripts/prepare-i04-fixture.py "
            "build/i04-reload-ci --background-rounds 12\n"
            'I04_TEST_FIXTURE="$GITHUB_WORKSPACE/build/i04-reload-ci/fixture.json" '
            "PLAYWRIGHT_JSON_OUTPUT_FILE=test-results/i04-reload/report.json "
            "xvfb-run -a sh -c 'openbox > /tmp/i04-reload-openbox.log 2>&1 & "
            'npx playwright test tests/e2e/i04-jobs.spec.ts --grep "reload re-queries" '
            "--output=test-results/i04-reload --reporter=list,github,json'\n"
            "uv run --frozen python scripts/prepare-i04-fixture.py build/i04-disconnect-ci\n"
            'I04_TEST_FIXTURE="$GITHUB_WORKSPACE/build/i04-disconnect-ci/fixture.json" '
            "PLAYWRIGHT_JSON_OUTPUT_FILE=test-results/i04-disconnect/report.json "
            "xvfb-run -a sh -c 'openbox > /tmp/i04-disconnect-openbox.log 2>&1 & "
            'npx playwright test tests/e2e/i04-jobs.spec.ts --grep "coordinator exit" '
            "--output=test-results/i04-disconnect --reporter=list,github,json'",
        ),
        Lane(
            "packaged-recovery",
            2,
            "mapfile -t sandboxes < <(find release -type f -name chrome-sandbox)\n"
            "mapfile -t executables < <(find release -type f -name '@ontolearndesktop')\n"
            'test "${#sandboxes[@]}" -eq 1\n'
            'test "${#executables[@]}" -eq 1\n'
            'sudo chown root:root "${sandboxes[0]}"\n'
            'sudo chmod 4755 "${sandboxes[0]}"\n'
            'export ONTOLEARN_PACKAGED_EXECUTABLE="$GITHUB_WORKSPACE/${executables[0]}"\n'
            "uv run --frozen python scripts/prepare-i04-fixture.py "
            "build/i04-packaged-disconnect-ci\n"
            'PLAYWRIGHT_JSON_OUTPUT_FILE="$GITHUB_WORKSPACE/test-results/'
            'i04-packaged-disconnect/report.json" '
            'I04_TEST_FIXTURE="$GITHUB_WORKSPACE/build/i04-packaged-disconnect-ci/'
            'fixture.json" '
            "xvfb-run -a sh -c 'openbox > /tmp/i04-packaged-disconnect-openbox.log 2>&1 & "
            'npx playwright test tests/e2e/i04-jobs.spec.ts --grep "coordinator exit" '
            "--output=test-results/i04-packaged-disconnect --reporter=list,github,json'\n"
            "uv run --frozen python scripts/prepare-i04-fixture.py "
            "build/i04-packaged-reload-ci --background-rounds 12\n"
            'PLAYWRIGHT_JSON_OUTPUT_FILE="$GITHUB_WORKSPACE/test-results/'
            'i04-packaged-reload/report.json" '
            'I04_TEST_FIXTURE="$GITHUB_WORKSPACE/build/i04-packaged-reload-ci/fixture.json" '
            "xvfb-run -a sh -c 'openbox > /tmp/i04-packaged-reload-openbox.log 2>&1 & "
            'npx playwright test tests/e2e/i04-jobs.spec.ts --grep "reload re-queries" '
            "--output=test-results/i04-packaged-reload --reporter=list,github,json'\n"
            "uv run --frozen python scripts/prepare-i04-fixture.py "
            "build/i04-packaged-native-ci\n"
            'PLAYWRIGHT_JSON_OUTPUT_FILE="$GITHUB_WORKSPACE/test-results/'
            'i04-packaged-native/report.json" '
            'I04_TEST_FIXTURE="$GITHUB_WORKSPACE/build/i04-packaged-native-ci/fixture.json" '
            "I04_NATIVE_ISOLATED=1 "
            "xvfb-run -a sh -c 'openbox > /tmp/i04-packaged-native-openbox.log 2>&1 & "
            'npx playwright test tests/e2e/i04-jobs.spec.ts --grep "native renderer" '
            "--output=test-results/i04-packaged-native --reporter=list,github,json'",
            # The unpackaged and packaged native renderer tests are the only
            # e2e launches without their own user-data-dir: both derive the
            # default Electron profile from the same app package identity, so
            # they must never overlap. Every other launch (including C1's
            # native run) uses an isolated per-launch userData directory.
            deps=("verify-package", "i04-unpackaged"),
        ),
    ]


def validate_plan(lanes: list[Lane]) -> None:
    names = [lane.name for lane in lanes]
    if len(names) != len(set(names)):
        raise ValueError("duplicate lane names")
    by_name = {lane.name: lane for lane in lanes}
    for lane in lanes:
        if lane.phase not in (1, 2):
            raise ValueError(f"{lane.name}: phase must be 1 or 2")
        for dep in lane.deps:
            if dep not in by_name:
                raise ValueError(f"{lane.name}: unknown dependency {dep}")
            if by_name[dep].phase > lane.phase:
                raise ValueError(f"{lane.name}: dependency {dep} is in a later phase")


async def run_pipeline(lanes: list[Lane], spawn, log) -> dict:
    validate_plan(lanes)
    state: dict[str, str] = {lane.name: "pending" for lane in lanes}
    running: dict[str, asyncio.Task] = {}

    async def run_lane(lane: Lane) -> None:
        state[lane.name] = "running"
        log(f"[{lane.name}] start")
        try:
            code = await spawn(lane)
        except asyncio.CancelledError:
            state[lane.name] = "cancelled"
            log(
                f"[{lane.name}] cancelled; bounded cleanup ran (outcome recorded via cleanup notes)"
            )
            raise
        except BaseException as error:
            # Spawn/IO failures settle as this lane's failure instead of
            # escaping the task and abandoning the other running lanes.
            state[lane.name] = "failure"
            log(f"[{lane.name}] lane failure: {type(error).__name__}: {error}")
            return
        state[lane.name] = "success" if code == 0 else "failure"
        log(f"[{lane.name}] exit {code}")

    def failed() -> bool:
        return "failure" in state.values()

    def phase_one_incomplete() -> bool:
        return any(lane.phase == 1 and state[lane.name] != "success" for lane in lanes)

    try:
        while True:
            if failed():
                for lane in lanes:
                    if state[lane.name] == "pending":
                        state[lane.name] = "skipped"
                        log(f"[{lane.name}] skipped after an earlier failure")
            ready = [
                lane
                for lane in lanes
                if state[lane.name] == "pending"
                and all(state[dep] == "success" for dep in lane.deps)
                and (lane.phase == 1 or not phase_one_incomplete())
            ]
            for lane in ready:
                running[lane.name] = asyncio.create_task(run_lane(lane))
            if running:
                done, _pending = await asyncio.wait(
                    set(running.values()), return_when=asyncio.FIRST_COMPLETED
                )
                # Remove finished lanes so the running set converges to empty;
                # keeping stale done tasks here made every later wait return
                # immediately and spun the loop forever after the first exit.
                for name, task in list(running.items()):
                    if task in done:
                        del running[name]
                outcomes = await asyncio.gather(*done, return_exceptions=True)
                for outcome in outcomes:
                    if isinstance(outcome, BaseException):
                        raise outcome from None
                continue
            for lane in lanes:
                if state[lane.name] == "pending":
                    state[lane.name] = "skipped"
                    log(f"[{lane.name}] skipped: dependencies cannot be satisfied")
            break
    except asyncio.CancelledError:
        # Cancelling this pipeline must also settle its own lane tasks, whose
        # spawn_lane cancellation handlers reap each lane's process group.
        for task in running.values():
            task.cancel()
        await asyncio.gather(*running.values(), return_exceptions=True)
        raise
    return {"ok": all(value == "success" for value in state.values()), "states": state}


async def _drain(stream, target, name: str) -> None:
    # Byte-chunk draining with no readline length limit: a child emitting one
    # enormous line still flows through (chunked at the cap below) instead of
    # raising and wedging the pipe while the parent only awaits process.wait.
    pending = b""
    while True:
        chunk = await stream.read(65536)
        if not chunk:
            break
        pending += chunk
        *lines, pending = pending.split(b"\n")
        if len(pending) > 262144:
            lines.append(pending)
            pending = b""
        for line in lines:
            target.write(f"[{name}] {line.decode('utf-8', 'replace')}\n")
        target.flush()
    if pending:
        target.write(f"[{name}] {pending.decode('utf-8', 'replace')}\n")
        target.flush()


async def _drain_guarded(stream, target, name: str):
    """Drain one pipe, reporting failures as values so supervision reacts
    immediately instead of discovering them only after process.wait (the
    R14-02 gap). Never raises except cancellation: the diagnostic print is
    itself guarded so a broken diagnostic channel cannot mask the original
    failure or turn the task into an unobserved exception (R14 feedback 3)."""
    try:
        await _drain(stream, target, name)
        return None
    except asyncio.CancelledError:
        raise
    except Exception as error:
        try:
            print(
                f"[{name}] output drain failure: {type(error).__name__}: {error}",
                file=sys.stderr,
            )
        except Exception:
            pass  # the diagnostic channel itself failed; the failure is still returned
        return error


def _proc_stat(pid: int) -> str | None:
    try:
        with open(f"/proc/{pid}/stat", "rb") as stream:
            return stream.read().decode("ascii", "replace")
    except OSError:
        return None


def _pid_pgid(pid: int) -> int | None:
    if os.path.isdir("/proc"):
        stat = _proc_stat(pid)
        if stat is None:
            return None
        # comm may contain spaces and parens; fields restart after the last ')'.
        fields = stat.rpartition(")")[2].split()
        try:
            return int(fields[2])
        except (IndexError, ValueError):
            return None
    if sys.platform == "darwin":
        try:
            listing = subprocess.run(
                ["ps", "-o", "pgid=", "-p", str(pid)],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        parts = listing.stdout.split()
        return int(parts[0]) if parts else None
    return None


def _own_group_members(pgid: int) -> list[int] | None:
    """Verifiable own-group anchor: pids whose CURRENT process-group id equals
    this lane's pgid. Returns None when the observation itself FAILED (unreadable
    /proc entry, ps error/timeout/nonzero) — an unknown observation is never
    reported as an empty group, because "could not read" and "does not exist"
    have different cleanup consequences. Linux reads /proc; macOS shells out
    to ps once; other platforms are unknown (never empty)."""
    if os.path.isdir("/proc"):
        try:
            entries = os.listdir("/proc")
        except OSError as error:
            _note(f"own group observation failed (/proc): {error!r}")
            return None
        members = []
        for entry in entries:
            if not entry.isdigit():
                continue
            stat = _proc_stat(int(entry))
            if stat is None:
                # A member we cannot read makes the whole observation
                # unreliable; guessing "gone" from a partial read is forbidden.
                _note("own group observation failed (unreadable member stat)")
                return None
            fields = stat.rpartition(")")[2].split()
            if len(fields) < 4 or fields[2] != str(pgid) or fields[0] == "Z":
                continue
            members.append(int(entry))
        return members
    if sys.platform == "darwin":
        try:
            listing = subprocess.run(
                ["ps", "-axo", "pid=,pgid="],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            _note(f"own group observation failed (ps): {error!r}")
            return None
        if listing.returncode != 0:
            _note(f"own group observation failed (ps exit {listing.returncode})")
            return None
        members = []
        for line in listing.stdout.splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1] == str(pgid):
                members.append(int(parts[0]))
        return members
    return None


def _note(message: str) -> None:
    """Cleanup diagnostics must never raise: a broken diagnostic channel
    cannot be allowed to interrupt the TERM-to-KILL closure sequence."""
    try:
        print(message, file=sys.stderr)
    except Exception:
        pass


def _signal_members(pgid: int, deliver, name: str) -> None:
    # Re-verify membership immediately before each signal so a pid recycled
    # between enumeration and delivery is still excluded. A member whose pid
    # equals the pgid would be a GROUP LEADER: our original leader is gone in
    # the post-reap branch, so such a member can only be a recycled identity
    # and is never signaled.
    for pid in _own_group_members(pgid) or []:
        if pid == pgid:
            continue
        if _pid_pgid(pid) == pgid and hasattr(os, "kill"):
            try:
                os.kill(pid, deliver)
            except ProcessLookupError:
                continue
            except (PermissionError, OSError) as error:
                _note(f"[{name}] own group member {pid} not signaled: {error!r}")


async def _await_group_quiet(pgid: int, name: str, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    observation = _own_group_members(pgid)
    while time.monotonic() < deadline:
        observation = _own_group_members(pgid)
        if observation is not None and not observation:
            return True
        await asyncio.sleep(0.05)
    observation = _own_group_members(pgid)
    if observation is None:
        _note(
            f"[{name}] own process group state UNKNOWN (observation failed); cleanup NOT confirmed"
        )
        return False
    if observation:
        _note(f"[{name}] own process group still present: {observation}")
        return False
    return True


async def _collect_drains_bounded(drains, name: str) -> bool:
    """Finish or bound output collection. Descendants that survive the group
    cleanup can keep pipes open; bounding keeps the lane settled-and-failed
    instead of wedged. Returns True when collection was cut short."""
    try:
        await asyncio.wait_for(asyncio.gather(*drains), timeout=_DRAIN_BOUND_S)
        return False
    except TimeoutError:
        _note(f"[{name}] output collection not complete within {_DRAIN_BOUND_S}s")
        for task in drains:
            task.cancel()
        await asyncio.gather(*drains, return_exceptions=True)
        return True


async def _reap_lane_group(process, name: str, identity=None) -> str:
    # Close exactly this lane's own process group, created with
    # start_new_session; never signal other lanes, the runner, or unrelated
    # user processes. Returns an honest outcome string:
    #   "closed"   — reliably observed empty after bounded TERM→KILL
    #   "residual" — members provably remain after the bounded sequence
    #   "unknown"  — membership observation itself failed; nothing claimed
    #   "refused"  — signaling refused because the original group identity is
    #                no longer provable (leader reaped, no stable handle)
    # While the leader is unreaped, killpg and verified member signaling are
    # provably ours. After the leader was reaped the numeric pgid alone is NOT
    # a lifecycle proof (the number can be recycled into a new group): member
    # signaling then requires the stable identity pin (pidfd) held by
    # _supervise, which prevents the pid from being recycled at all. Without
    # that pin the scheduler refuses to signal and reports the cleanup as not
    # confirmed — it never widens the signal scope to compensate.
    pinned = bool(identity and identity.get("pinned"))
    # Eligibility is decided ONCE at entry: a leader that was still alive when
    # cleanup began keeps full member-closure rights even if it exits (and is
    # reaped) mid-cleanup — the deterministic mid-reap branch. Only a leader
    # already reaped at entry needs the identity pin for post-reap signaling.
    entry_reaped = process.returncode is not None
    pgid = process.pid
    if hasattr(os, "killpg") and not entry_reaped:
        try:
            os.killpg(pgid, signal.SIGTERM)
        except ProcessLookupError:
            pass  # group already fully gone; the quiet check below confirms
        except (PermissionError, OSError) as error:
            _note(f"[{name}] own process group not signaled: {error!r}")
    if hasattr(os, "killpg"):
        if entry_reaped and not pinned:
            _note(
                f"[{name}] leader already reaped and no stable identity pin; "
                "refusing member signals — own process group cleanup NOT confirmed"
            )
            return "refused"
        term = getattr(signal, "SIGTERM", None)
        kill = getattr(signal, "SIGKILL", None)
        for deliver in [sig for sig in (term, kill) if sig is not None]:
            _signal_members(pgid, deliver, name)
            quiet = await _await_group_quiet(pgid, name, _MEMBER_WAIT_S)
            if quiet:
                return "closed"
            if _own_group_members(pgid) is None:
                pass
            else:
                pass
        final = _own_group_members(pgid)
        if final is None:
            _note(f"[{name}] own process group state UNKNOWN; cleanup NOT confirmed")
            return "unknown"
        if final:
            _note(f"[{name}] own process group exit not confirmed; members remain: {final}")
        return "residual" if final else "closed"
    if hasattr(os, "kill") and process.returncode is None:
        # No process-group API (non-POSIX boundary): bound and close the
        # direct child only; group descendants are not provable there.
        try:
            process.kill()
        except OSError as error:
            _note(f"[{name}] own process not killed: {error!r}")
        try:
            await asyncio.wait_for(asyncio.shield(process.wait()), timeout=_REAP_WAIT_S)
            return "closed"
        except TimeoutError:
            _note(f"[{name}] own process exit not confirmed (no group API)")
            return "residual"
    return "unknown"


def _drain_outcome(task) -> Exception | None:
    """Final result of a drain task in either failure shape: the value
    returned by _drain_guarded, or an exception it could not swallow."""
    if task.cancelled():
        return None
    error = task.exception()
    if error is None:
        error = task.result()
    return error


async def _supervise(process, name: str, stdout=None, stderr=None) -> int:
    """Watch the child and both output drains concurrently for the WHOLE
    supervision lifecycle.

    A failing drain — either pipe, including failures of the diagnostic
    channel, at any time INCLUDING the tail collection — settles the lane as
    a failure with the own group closed (R14-02). The child's returncode
    (set by the reaper independently of the pipes) ends the main wait even
    when a long-lived wait() waiter would stay pending on a pipe held by a
    same-group descendant (R14-03). Cancellation protection covers the main
    loop AND the tail collection: a single plain cancel during either phase
    still runs the bounded own-group settlement before propagating. On Linux
    a pidfd opened for the leader pins the numeric identity for the lane's
    lifetime, making post-reap member signaling provably safe; without that
    stable handle the reap refuses post-reap signaling and reports the
    cleanup as not confirmed."""
    # Best-effort stable identity pin: while a pidfd is open the kernel
    # cannot recycle the leader pid, so the numeric pgid can never name a
    # different group during this lane's lifetime.
    identity = {"pinned": False, "handle": None}
    if _PIDFD_SUPPORTED:
        try:
            identity["handle"] = os.pidfd_open(process.pid)
            identity["pinned"] = True
        except OSError as error:
            _note(f"[{name}] identity pin unavailable: {error!r}")
    drains: list[asyncio.Task] | None = None
    waiter: asyncio.Future | None = None
    try:
        drains = [
            asyncio.ensure_future(_drain_guarded(process.stdout, stdout or sys.stdout, name)),
            asyncio.ensure_future(_drain_guarded(process.stderr, stderr or sys.stderr, name)),
        ]
        waiter = asyncio.ensure_future(process.wait())
        drain_failure: Exception | None = None

        def absorb(task) -> None:
            nonlocal drain_failure
            if drain_failure is None:
                drain_failure = _drain_outcome(task)

        unfinished = set(drains)
        # --- main watch loop -------------------------------------------
        while process.returncode is None and drain_failure is None:
            for task in list(unfinished):
                if task.done():
                    unfinished.discard(task)
                    absorb(task)
            if drain_failure is not None:
                break
            await asyncio.wait(
                {waiter, *unfinished},
                timeout=_EXIT_POLL_S,
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in list(unfinished):
                if task.done():
                    unfinished.discard(task)
                    absorb(task)
        if not waiter.done():
            waiter.cancel()
            await asyncio.gather(waiter, return_exceptions=True)
        # --- tail collection -------------------------------------------
        bounded_short = await _collect_drains_bounded(drains, name)
        for task in drains:
            absorb(task)
        if drain_failure is not None or bounded_short:
            # Failure or unconfirmable output closes the lane's own group
            # (leader may already be reaped: the verified member path, gated
            # by the identity pin) instead of leaving pipe-holding
            # descendants behind.
            await _reap_lane_group(process, name, identity)
            return 1
        code = process.returncode
        return 0 if code == 0 else (code if code is not None else 1)
    except asyncio.CancelledError:
        # One bounded settlement for the whole lifecycle: main loop, tail
        # collection, every intermediate await.
        try:
            await _reap_lane_group(process, name, identity)
        except asyncio.CancelledError:
            _note(f"[{name}] cleanup interrupted by repeated cancellation; NOT confirmed")
            raise
        try:
            if drains:
                for task in drains:
                    task.cancel()
                await asyncio.gather(*drains, return_exceptions=True)
            if waiter is not None and not waiter.done():
                waiter.cancel()
                await asyncio.gather(waiter, return_exceptions=True)
        except asyncio.CancelledError:
            pass
        raise
    finally:
        handle = identity.get("handle")
        if handle is not None:
            try:
                os.close(handle)
            except OSError:
                pass


async def spawn_lane(lane: Lane) -> int:
    # Production launches every lane through /bin/bash -e -c. The shell tuple
    # is a single test seam: the regression suite swaps it for a real
    # interpreter so the identical spawn → supervise → reap chain exercises
    # real child processes on platforms without bash; Linux production bytes
    # and behavior are unchanged.
    try:
        process = await asyncio.create_subprocess_exec(
            *_LANE_SHELL,
            lane.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, **lane.env},
            start_new_session=True,
        )
    except OSError as error:
        print(f"[{lane.name}] spawn failed: {error}", file=sys.stderr)
        return 127
    return await _supervise(process, lane.name)


async def _run_orchestrator() -> dict:
    main_task = asyncio.current_task()

    def receive_signal(number, frame):
        # SIGINT/SIGTERM cancel the pipeline itself; run_pipeline then
        # cancels its lane tasks, and each lane reaps its own process group.
        if main_task is not None:
            main_task.cancel()

    for name in (signal.SIGINT, signal.SIGTERM):
        signal.signal(name, receive_signal)
    return await run_pipeline(build_plan(), spawn_lane, print)


def main() -> int:
    if sys.platform != "linux":
        print("ci-quality-schedule orchestrates the Linux Quality job only", file=sys.stderr)
        return 2
    try:
        result = asyncio.run(_run_orchestrator())
    except asyncio.CancelledError:
        print("quality pipeline cancelled; lanes settled (cleanup outcomes recorded via notes)")
        return 130
    for name, value in result["states"].items():
        print(f"quality lane {name}: {value}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
