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
import sys
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Lane:
    name: str
    phase: int
    command: str
    deps: tuple[str, ...] = ()
    env: dict[str, str] = field(default_factory=dict)


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
            log(f"[{lane.name}] cancelled; own child processes reaped by the lane")
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


async def _reap_lane_group(process, name: str) -> None:
    # Terminate exactly this lane's own process group (created with
    # start_new_session); never signal other lanes, the runner, or unrelated
    # user processes. Bounded by short waits, no extra job budget.
    if process.returncode is not None:
        return
    killers = [signal.SIGTERM]
    if hasattr(signal, "SIGKILL"):
        killers.append(signal.SIGKILL)
    for deliver in killers:
        try:
            if hasattr(os, "killpg"):
                os.killpg(process.pid, deliver)
            else:
                process.kill()
        except (ProcessLookupError, PermissionError, OSError):
            return
        try:
            await asyncio.wait_for(process.wait(), timeout=5)
            return
        except TimeoutError:
            continue
    print(f"[{name}] own process group exit not confirmed", file=sys.stderr)


async def spawn_lane(lane: Lane) -> int:
    try:
        process = await asyncio.create_subprocess_exec(
            "/bin/bash",
            "-e",
            "-c",
            lane.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, **lane.env},
            start_new_session=True,
        )
    except OSError as error:
        print(f"[{lane.name}] spawn failed: {error}", file=sys.stderr)
        return 127
    outputs = [
        asyncio.create_task(_drain(process.stdout, sys.stdout, lane.name)),
        asyncio.create_task(_drain(process.stderr, sys.stderr, lane.name)),
    ]
    try:
        code = await process.wait()
    except asyncio.CancelledError:
        await _reap_lane_group(process, lane.name)
        await asyncio.gather(*outputs, return_exceptions=True)
        raise
    drained = await asyncio.gather(*outputs, return_exceptions=True)
    failures = [item for item in drained if isinstance(item, BaseException)]
    if failures:
        for item in failures:
            print(f"[{lane.name}] output drain failure: {item!r}", file=sys.stderr)
        return 1
    return 0 if code == 0 else (code if code is not None else 1)


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
        print("quality pipeline cancelled; lanes settled and own process groups reaped")
        return 130
    for name, value in result["states"].items():
        print(f"quality lane {name}: {value}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
