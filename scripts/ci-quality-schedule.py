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
import threading
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
# Set by the SIGINT/SIGTERM handlers in _run_orchestrator; lanes observe it
# between poll ticks so a runner signal ends supervision promptly.
_signal = 0


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
            # CI49 observation: the engine shards running concurrently with
            # vitest (unit-build) are the leading SUSPECTED scheduling
            # variable pending isolation — NOT proven as the root cause of
            # the four failures. This ordering removes the variable so a
            # contention-free run can decide causation; it is not itself
            # evidence any failure is fixed. Phase gating, commands, sets,
            # assertions, successors and the 15-minute budget are unchanged
            # — this is ordering, not parallelism removal.
            deps=("static-gates", "unit-build"),
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
            "--output=test-results/i04-packaged-native --reporter=list,github,json'\n"
            'LINUX_C1_EVIDENCE="$GITHUB_WORKSPACE/test-results/'
            'i02-linux-packaged-evidence.json"\n'
            'PLAYWRIGHT_JSON_OUTPUT_FILE="$GITHUB_WORKSPACE/test-results/'
            'i02-packaged-c1/report.json" '
            'I02_EVIDENCE="$LINUX_C1_EVIDENCE" '
            "xvfb-run -a sh -c 'openbox > /tmp/i02-packaged-c1-openbox.log 2>&1 & "
            "npx playwright test tests/e2e/csp-lifecycle.spec.ts --workers=1 "
            "--output=test-results/i02-packaged-c1 --reporter=list,github,json'\n"
            'LINUX_C1_EVIDENCE="$LINUX_C1_EVIDENCE" node -e "'
            "const fs=require('node:fs');"
            "const d=JSON.parse(fs.readFileSync(process.env.LINUX_C1_EVIDENCE,'utf8'));"
            "const ev=d.nativeRecovery?.events||[];"
            "if(!d.nativeRecovery?.packaged||d.result!=='PASS'||!d.foreignSenderRejected"
            "||!ev.includes('crashed')||!ev.includes('unresponsive')){"
            "console.error('LINUX_PACKAGED_C1_FAILED',d);process.exit(1);}"
            "console.log('LINUX_PACKAGED_C1_OK',JSON.stringify(ev));\"\n"
            "xvfb-run -a sh -c 'openbox > /tmp/q3-packaged-graph-openbox.log 2>&1 & "
            "uv run --frozen python scripts/run-q3-packaged-graph.py "
            "release test-results/q3-packaged-graph'\n"
            "B1A_NATIVE_ISOLATED=1 "
            "xvfb-run -a sh -c 'openbox > /tmp/b1a-packaged-openbox.log 2>&1 & "
            "uv run --frozen python scripts/run-b1a-packaged-lifecycle.py "
            "release test-results/b1a-packaged-lifecycle'",
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
        fields = stat.rpartition(")")[2].split()
        try:
            return int(fields[2])
        except (IndexError, ValueError):
            return None
    if sys.platform == "darwin":
        output = _ps_query("pgid", pid)
        if output is None:
            return None
        parts = output.split()
        return int(parts[0]) if parts else None
    return None


def _own_group_members(pgid: int) -> list[int] | None:
    """Pids whose CURRENT pgid equals this lane's pgid. None = the
    observation itself failed (unreadable /proc entry, ps error/timeout/
    nonzero) — unknown is never reported as an empty group."""
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
                _note("own group observation failed (unreadable member stat)")
                return None
            fields = stat.rpartition(")")[2].split()
            if len(fields) < 4 or fields[2] != str(pgid) or fields[0] == "Z":
                continue
            members.append(int(entry))
        return members
    if sys.platform == "darwin":
        output = _ps_query("members")
        if output is None:
            return None
        members = []
        for line in output.splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1] == str(pgid):
                members.append(int(parts[0]))
        return members
    return None


def _note(message: str) -> None:
    """Cleanup diagnostics must never raise: a broken diagnostic channel
    cannot be allowed to interrupt the closure sequence."""
    try:
        print(message, file=sys.stderr)
    except Exception:
        pass


def _ps_query(kind: str, pid: int = 0) -> str | None:
    """The single darwin ps invocation point, restricted to the three fixed
    read-only queries this supervisor uses: 'pgid' and 'stat' take one pid;
    'members' lists (pid, pgid) pairs process-wide. The argv is built here
    from fixed literals plus a validated pid — callers never pass through
    arbitrary arguments or shell text. None means the observation failed
    (error/timeout/nonzero exit); callers treat that as UNKNOWN, never as an
    empty result."""
    if kind == "members":
        argv = ["ps", "-axo", "pid=,pgid="]
    elif kind == "pgid":
        if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 1:
            return None
        argv = ["ps", "-o", "pgid=", "-p", str(pid)]
    elif kind == "stat":
        if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 1:
            return None
        argv = ["ps", "-o", "stat=", "-p", str(pid)]
    else:
        return None
    try:
        listing = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        _note(f"ps observation failed: {error!r}")
        return None
    if listing.returncode != 0:
        _note(f"ps observation failed (exit {listing.returncode})")
        return None
    return listing.stdout


def _pipe_reader_thread(pipe, target, name: str, failures: list) -> None:
    # Windows-fallback reader thread: byte chunks, no readline limit; a
    # failing target or read error is recorded and the thread exits. POSIX
    # uses the readiness-based async reader instead — this thread exists only
    # where loop.add_reader is unavailable.
    prefix = f"[{name}] "
    try:
        while True:
            chunk = pipe.read(65536)
            if not chunk:
                break
            target.write(prefix + chunk.decode("utf-8", "replace"))
            target.flush()
    except Exception as error:  # noqa: BLE001 — recorded, never escapes
        failures.append((name, error))


async def _read_pipe_ready(fd, target, name: str, failures: list) -> None:
    """POSIX pipe reader on the raw fd: non-blocking os.read driven by the
    event loop's readiness notifications. It never blocks the loop, is fully
    cancellable, and — because it owns no buffered wrapper — its END (this
    coroutine returning) is real proof nobody holds the object's lock before
    the fd is closed. EOF, read errors and target failures all terminate it."""
    loop = asyncio.get_running_loop()
    prefix = f"[{name}] "
    try:
        while True:
            waiter = loop.create_future()
            loop.add_reader(fd, waiter.set_result, None)
            try:
                await waiter
            finally:
                loop.remove_reader(fd)
            while True:
                try:
                    chunk = os.read(fd, 65536)
                except BlockingIOError:
                    break  # drained for now; wait for the next readiness
                except OSError as error:
                    failures.append((name, error))
                    return
                if not chunk:
                    return  # EOF
                target.write(prefix + chunk.decode("utf-8", "replace"))
                target.flush()
    except asyncio.CancelledError:
        raise
    except Exception as error:  # noqa: BLE001 — recorded, never escapes
        failures.append((name, error))


def _popen_exited_unreaped(popen, state: dict) -> bool:
    """True when the leader has EXITED while WE still hold the reap right.

    Linux reads /proc state 'Z' and macOS uses ps — neither call touches
    poll()/wait(), so observing exit never releases the pid. Windows has no
    zombie state; there poll() IS the native non-blocking handle check
    (WaitForSingleObject(0)) and the Popen-held process handle keeps the
    identity anchored regardless, so polling there is both safe and the only
    real terminal observation (no POSIX groups exist to protect)."""
    if os.name == "nt":
        exited = popen.poll() is not None
        if exited:
            state["code_known"] = True
        return exited
    pid = popen.pid
    if os.path.isdir("/proc"):
        stat = _proc_stat(pid)
        if stat is None:
            return False  # unreadable is NOT proof of exit
        fields = stat.rpartition(")")[2].split()
        return bool(fields) and fields[0] == "Z"
    if sys.platform == "darwin":
        output = _ps_query("stat", pid)
        if output is None:
            return False  # failed observation is NOT proof of exit
        return output.strip().startswith("Z")
    return False


async def _reap_leader(popen, name: str, state: dict) -> None:
    """The SINGLE reap point. The blocking wait runs in a worker with its own
    timeout — the worker thread always ends within that bound even if the
    outer await is cancelled — and the result is actually collected.
    reap_attempted makes a second call a no-op WITHOUT claiming success."""
    if state["reaped"] or state.get("reap_attempted"):
        return
    loop = asyncio.get_running_loop()

    def bounded_wait():
        try:
            popen.wait(timeout=_REAP_WAIT_S)
        except subprocess.TimeoutExpired:
            return False
        return True

    try:
        finished = await asyncio.wait_for(
            loop.run_in_executor(None, bounded_wait), timeout=_REAP_WAIT_S + 3
        )
    except TimeoutError:
        finished = False
    if finished and popen.returncode is not None:
        state["reaped"] = True
    else:
        _note(f"[{name}] leader reap not confirmed within bound")
    # Idempotency without lying: only the observation of a REAL returncode
    # sets 'reaped'; a bounded-out attempt just prevents a second wait, and
    # every consumer reports the outcome honestly as NOT confirmed.
    state["reap_attempted"] = True


async def _close_lane_group(popen, name: str, state: dict) -> str:
    """Close the lane's own process group while the reap right is still OURS
    (state['reaped'] is False), then perform the single final reap.

    The entry check reads the supervisor's OWN lifecycle state — never
    popen.poll(), which would itself reap an exited (zombie) leader and
    release the identity exactly in the leader-first case. While unreaped,
    the pid stays allocated (alive or zombie): killpg(pgid) cannot reach a
    recycled identity because a new group with that numeric id would need
    pid == pgid, which is still ours. Group closure happens BEFORE the final
    wait; honest outcomes are closed/residual/unknown/refused.

    Without process-group APIs (Windows), the ONLY owned termination handle
    is this supervisor's own Popen: popen.terminate() delivers through the
    native process handle (TerminateProcess), never a numeric pid, so the
    direct child is terminated before the bounded reap — a live child is
    never merely waited on, and 'closed' is returned only when the reap is
    actually confirmed by a real returncode."""
    pgid = popen.pid
    if not hasattr(os, "killpg"):
        if not state["reaped"] and not state.get("reap_attempted"):
            if popen.returncode is None:
                try:
                    popen.terminate()
                except OSError as error:
                    _note(f"[{name}] own process not terminated: {error!r}")
        await _reap_leader(popen, name, state)
        return "closed" if state["reaped"] else "unknown"
    if state["reaped"]:
        _note(f"[{name}] leader already reaped (identity released); group cleanup NOT confirmed")
        return "refused"
    term = getattr(signal, "SIGTERM", None)
    kill_sig = getattr(signal, "SIGKILL", None)
    outcome = "unknown"
    for deliver in [s for s in (term, kill_sig) if s is not None]:
        try:
            os.killpg(pgid, deliver)
        except ProcessLookupError:
            pass  # group already fully gone; member observation confirms
        except (PermissionError, OSError) as error:
            _note(f"[{name}] own process group not signaled: {error!r}")
        members: list[int] | None = None
        deadline = time.monotonic() + _MEMBER_WAIT_S
        while time.monotonic() < deadline:
            members = _own_group_members(pgid)
            if members is None or not members:
                break
            await asyncio.sleep(0.05)
        if members is not None and not members:
            outcome = "closed"
            break
    final = _own_group_members(pgid)
    if final is None:
        outcome = "unknown"
    elif final:
        _note(f"[{name}] group members remain after bounded rounds; cleanup NOT confirmed: {final}")
        outcome = "residual"
    else:
        outcome = "closed"
    await _reap_leader(popen, name, state)
    return outcome


async def _settle_readers(readers, failures, name: str) -> bool:
    """Bounded, PROVEN reader/pipe settlement.

    POSIX: the readiness readers are tasks — unfinished ones are cancelled
    and awaited (their return IS the end proof), then the pipe is closed by
    its ONE owning wrapper (Popen's pipe object): wrapper.close() releases
    the fd exactly once and marks the wrapper closed, so no later
    finalizer can close a reused fd number. The reader coroutine itself
    never reads through the wrapper, so no lock can be held. Windows
    fallback: reader threads are joined inside a worker with its own
    timeout (that join worker always ends), and the buffered pipe is
    closed ONLY after its reader provably exited, so close can never wait
    on a lock held by a blocked read. Close/join failures are recorded,
    never counted settled."""
    settled = True
    loop = asyncio.get_running_loop()
    for entry in readers:
        if entry["kind"] == "task":
            task = entry["handle"]
            if not task.done():
                task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception:  # noqa: BLE001 — reader failures were recorded
                pass
            if not task.done() or task.cancelled():
                settled = False
            try:
                entry["pipe"].close()
            except OSError as error:
                _note(f"[{name}] pipe fd close failed: {error!r}")
                settled = False
        else:
            reader = entry["handle"]
            await loop.run_in_executor(None, reader.join, _DRAIN_BOUND_S)
            if reader.is_alive():
                _note(f"[{name}] pipe reader did not finish within bound")
                settled = False
                continue  # NEVER close a buffered pipe its reader still holds
            try:
                entry["pipe"].close()
            except OSError as error:
                _note(f"[{name}] pipe close failed: {error!r}")
                settled = False
    if failures:
        settled = False
    return settled


async def _supervise(popen, name: str, stdout=None, stderr=None) -> int:
    """Supervise the lane leader for its WHOLE lifecycle with exclusive
    creation/reap ownership.

    The leader is a plain Popen only this supervisor reaps; state['reaped']
    is the supervisor's own anchor flag — poll()/wait() never happen outside
    the two sanctioned points (the Windows terminal observation and the
    single final reap), so a leader-first exit keeps the identity pinned
    through group cleanup. A failing reader target — either pipe, at ANY
    time — settles the lane as failure with the group closed first.
    Cancellation protection covers the whole lifecycle. On clean supervision
    the child's REAL exit code is returned; supervision/settlement failures
    return 1."""
    state = {"reaped": False, "code_known": False, "reap_attempted": False}
    failures: list = []
    targets = (stdout or sys.stdout, stderr or sys.stderr)
    pipes = (popen.stdout, popen.stderr)
    use_ready_readers = os.name != "nt"
    readers: list[dict] = []
    for pipe, target in zip(pipes, targets, strict=True):
        if use_ready_readers:
            fd = pipe.fileno()
            os.set_blocking(fd, False)
            task = asyncio.ensure_future(_read_pipe_ready(fd, target, name, failures))
            # Keep the OWNING wrapper in the entry: the raw fd is only a
            # reader handle here, and settlement must close through the
            # wrapper so the fd is released exactly once.
            readers.append({"kind": "task", "handle": task, "pipe": pipe})
        else:
            thread = threading.Thread(
                target=_pipe_reader_thread,
                args=(pipe, target, name, failures),
                daemon=True,
            )
            thread.start()
            readers.append({"kind": "thread", "handle": thread, "pipe": pipe})
    drain_failure = None
    exited = False
    try:
        while drain_failure is None and not exited and _signal == 0:
            if failures:
                drain_failure = failures[0][1]
                break
            exited = _popen_exited_unreaped(popen, state)
            if not exited:
                await asyncio.sleep(_EXIT_POLL_S)
        # Tail: bounded reader settlement. A pipe held by a same-group
        # descendant keeps its reader pending past the bound.
        ready_tasks = [e["handle"] for e in readers if e["kind"] == "task"]
        done: set = set()
        if ready_tasks:
            done, _pending = await asyncio.wait(ready_tasks, timeout=_DRAIN_BOUND_S)
        reader_threads = [e["handle"] for e in readers if e["kind"] == "thread"]
        if exited and drain_failure is None and reader_threads:
            stop_join = threading.Event()

            def wait_threads() -> None:
                deadline = time.monotonic() + _DRAIN_BOUND_S
                for thread in reader_threads:
                    while thread.is_alive() and not stop_join.is_set() and not failures:
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            return
                        thread.join(min(0.05, remaining))

            try:
                await asyncio.get_running_loop().run_in_executor(None, wait_threads)
            finally:
                stop_join.set()
        if drain_failure is None and failures:
            drain_failure = failures[0][1]
        short = any(e["kind"] == "task" and e["handle"] not in done for e in readers)
        short = short or any(e["kind"] == "thread" and e["handle"].is_alive() for e in readers)
        short = short or bool(failures)
        if drain_failure is not None or short:
            # Cleanup FIRST — no poll/wait has run, so the identity window is
            # intact — then settle readers, then fail the lane.
            await _close_lane_group(popen, name, state)
            await _settle_readers(readers, failures, name)
            return 1
        settled = await _settle_readers(readers, failures, name)
        await _reap_leader(popen, name, state)
        if not settled or popen.returncode is None:
            return 1
        # Clean supervision: the child's real exit code, not a flattened 1.
        return popen.returncode
    except asyncio.CancelledError:
        try:
            await _close_lane_group(popen, name, state)
            await _settle_readers(readers, failures, name)
        except asyncio.CancelledError:
            _note(f"[{name}] cleanup interrupted by repeated cancellation; NOT confirmed")
        raise


async def spawn_lane(lane: Lane) -> int:
    # Production launches every lane through /bin/bash -e -c. The shell tuple
    # is a single test seam: the regression suite swaps it for a real
    # interpreter so the identical spawn → supervise → reap chain exercises
    # real child processes on platforms without bash; Linux production bytes
    # and behavior are unchanged. The leader is created with start_new_session
    # and EXCLUSIVE reap ownership (plain Popen, no asyncio watcher).
    try:
        popen = subprocess.Popen(
            [*_LANE_SHELL, lane.command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, **lane.env},
            start_new_session=True,
        )
    except OSError as error:
        print(f"[{lane.name}] spawn failed: {error}", file=sys.stderr)
        return 127
    return await _supervise(popen, lane.name)


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
