"""Keep native pytest by default; account for a complete two-process CI run."""

from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

PLUGIN = "scripts.engine-test-reporting"
# Scheduling scores seeded by CI40 Windows first-result to last-result spans.
# They are NOT per-test durations or promised speedups. Unmeasured files use
# their collected case count (at least one), including resident/storage tests.
HISTORICAL_SCORES = {
    "test_project_format3.py": 215.559,
    "test_mainline_dispatch.py": 126.630,
    "test_mainline_manual_input_rejection.py": 104.328,
    "test_mainline_postwrite_admission.py": 100.866,
    "test_project_job_format3.py": 86.041,
    "test_job_store.py": 83.311,
    "test_project_changeset_service.py": 45.996,
    "test_project_applications.py": 37.862,
}
_signal = 0
_console = threading.Lock()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def receive_signal(number, frame):
    global _signal
    if not _signal:
        _signal = number  # Never raise between Popen and registering its owned PID.


@dataclass
class Child:
    process: subprocess.Popen
    folder: Path
    owner: str
    readers: list = field(default_factory=list)
    errors: list = field(default_factory=list)


def copy_stream(pipe, path, target, errors):
    try:
        with path.open("wb") as raw:
            for line in iter(pipe.readline, b""):
                raw.write(line)
                raw.flush()
                with _console:
                    try:
                        target.buffer.write(line)
                        target.buffer.flush()
                    except (BrokenPipeError, OSError):
                        pass  # Raw evidence still survives a closed CI console.
    except Exception as error:
        errors.append(f"{path.name}: {type(error).__name__}: {error}")
    finally:
        pipe.close()


def launch(folder, arguments, assignment=None):
    folder.mkdir()
    temporary = folder / "os-temp"
    temporary.mkdir()
    environment = os.environ.copy()
    for name in ("TMPDIR", "TMP", "TEMP"):
        environment[name] = str(temporary)
    owner = uuid4().hex
    command = [
        sys.executable,
        "-m",
        "pytest",
        *arguments,
        "-p",
        PLUGIN,
        # Pytest finds root/config before loading -p plugin options. Keep private
        # values in their option token so existing report paths aren't test roots.
        f"--engine-ci-report={folder}",
        f"--engine-ci-owner={owner}",
        f"--basetemp={folder / 'pytest-temp'}",
        "-o",
        f"cache_dir={folder / 'pytest-cache'}",
    ]
    if assignment is not None:
        write(folder / "files.json", assignment)
        command += [f"--engine-ci-files={folder / 'files.json'}"]
    write(folder / "command.json", {"argv": command, "cwd": os.getcwd(), "temp": str(temporary)})
    options = (
        {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        if os.name == "nt"
        else {"start_new_session": True}
    )
    process = subprocess.Popen(
        command, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **options
    )
    child = Child(process, folder, owner)
    try:
        write(folder / "pid.json", {"launcherPid": process.pid, "owner": owner})
        for pipe, name, target in (
            (process.stdout, "stdout.log", sys.stdout),
            (process.stderr, "stderr.log", sys.stderr),
        ):
            reader = threading.Thread(
                target=copy_stream,
                args=(pipe, folder / name, target, child.errors),
                daemon=True,
            )
            child.readers.append(reader)
            reader.start()
    except BaseException:
        stop([child])
        raise
    return child


def group_alive(child):
    if os.name == "nt":
        return child.process.poll() is None  # Not a claim about all descendants.
    try:
        os.killpg(child.process.pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def stop(children):
    evidence = {
        child.process.pid: {"launcherPid": child.process.pid, "signals": []} for child in children
    }
    for child in children:
        try:
            if os.name == "nt":
                # Group delivery may still work after its redirector leader exits.
                os.kill(child.process.pid, signal.CTRL_BREAK_EVENT)
            elif group_alive(child):
                os.killpg(child.process.pid, signal.SIGINT)
            evidence[child.process.pid]["signals"].append("native interrupt")
        except OSError as error:
            evidence[child.process.pid]["interruptError"] = str(error)
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline and any(group_alive(c) for c in children):
        time.sleep(0.05)
    for child in children:
        try:
            if os.name == "nt":
                if child.process.poll() is None:
                    result = subprocess.run(
                        ["taskkill", "/PID", str(child.process.pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=5,
                        check=False,
                    )
                    evidence[child.process.pid]["taskkillExit"] = result.returncode
                evidence[child.process.pid]["descendants"] = (
                    "UNKNOWN after launcher exit; no job handle"
                )
            elif group_alive(child):
                # The owned new session/group survives a dead pytest leader.
                os.killpg(child.process.pid, signal.SIGTERM)
                evidence[child.process.pid]["signals"].append("SIGTERM own group")
        except (OSError, subprocess.TimeoutExpired) as error:
            evidence[child.process.pid]["terminateError"] = str(error)
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline and any(group_alive(c) for c in children):
        time.sleep(0.05)
    for child in children:
        try:
            if os.name != "nt" and group_alive(child):
                os.killpg(child.process.pid, signal.SIGKILL)
                evidence[child.process.pid]["signals"].append("SIGKILL own group")
            elif os.name == "nt" and child.process.poll() is None:
                child.process.kill()
            child.process.wait(timeout=1)
        except (OSError, subprocess.TimeoutExpired) as error:
            child.errors.append(f"owned cleanup/exit unknown: {error}")
        observed = evidence[child.process.pid]
        observed["primaryExit"] = child.process.poll()
        if os.name != "nt":
            observed["groupStillPresent"] = group_alive(child)
            if observed["groupStillPresent"]:
                child.errors.append("owned process group exit not confirmed")
        with (child.folder / "cleanup.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(observed, ensure_ascii=False) + "\n")


def wait(children):
    while any(child.process.poll() is None for child in children):
        if _signal:
            stop(children)
            break
        time.sleep(0.05)
    if os.name != "nt" and any(group_alive(child) for child in children):
        for child in children:
            if group_alive(child):
                child.errors.append("owned descendant group outlived native pytest")
        stop(children)
    for child in children:
        for reader in child.readers:
            reader.join(timeout=2)
            if reader.is_alive():
                child.errors.append("output stream did not close")
        write(
            child.folder / "exit.json",
            {"exit": child.process.poll(), "parentSignal": _signal, "outputErrors": child.errors},
        )


def load_collection(folder):
    manifest = json.loads((folder / "collection.json").read_text(encoding="utf-8"))
    nodes = [item["nodeid"] for item in manifest["items"]]
    if not nodes or len(nodes) != len(set(nodes)):
        raise ValueError("empty or duplicate native collection")
    return manifest


def partition(items):
    counts = Counter(item["file"] for item in items)
    weights = {
        name: HISTORICAL_SCORES.get(Path(name).name, float(count)) for name, count in counts.items()
    }
    groups, loads = [[], []], [0.0, 0.0]
    for name in sorted(counts, key=lambda name: (-weights[name], name)):
        index = min(range(2), key=lambda index: (loads[index], index))
        groups[index].append(name)
        loads[index] += weights[name]
    return [sorted(group) for group in groups if group], weights


def session_owned(child, event):
    native, parent = event.get("pid"), event.get("parentPid")
    owned = (
        event.get("event") == "session_start"
        and event.get("owner") == child.owner
        and type(native) is int
        and type(parent) is int
        and native > 1
        and parent > 0
        and ((native == child.process.pid and parent == os.getpid()) or parent == child.process.pid)
    )
    write(
        child.folder / "session-identity.json",
        {
            "launcherPid": child.process.pid,
            "nativePid": native,
            "nativeParentPid": parent,
            "owner": child.owner,
            "owned": owned,
        },
    )
    return owned


def account(child, expected, identity):
    errors, outcomes = [], {}
    phases, starts, finishes = defaultdict(dict), Counter(), Counter()
    try:
        collection = load_collection(child.folder)
        if collection["items"] != expected or collection["identity"] != identity:
            errors.append("shard collection/identity differs from full native manifest")
        lines = (child.folder / "events.jsonl").read_text(encoding="utf-8").splitlines()
        events = [json.loads(line) for line in lines]
        if (
            not events
            or not session_owned(child, events[0])
            or events[-1].get("event") != "session_finish"
            or sum(e.get("event") == "session_start" for e in events) != 1
            or sum(e.get("event") == "session_finish" for e in events) != 1
            or events[-1].get("exitstatus") != 0
        ):
            errors.append("missing, interrupted or unsuccessful session boundary")
        expected_ids = {item["nodeid"] for item in expected}
        invalid = set()
        for event in events[1:-1]:
            node = event.get("nodeid")
            if node not in expected_ids:
                errors.append(f"unexpected node/event: {node!r}")
                continue
            kind = event.get("event")
            if kind == "start":
                if phases[node] or finishes[node]:
                    invalid.add(node)
                starts[node] += 1
            elif kind == "finish":
                if starts[node] != 1 or "teardown" not in phases[node]:
                    invalid.add(node)
                finishes[node] += 1
            elif kind == "report":
                phase = event.get("phase")
                seen = phases[node]
                if starts[node] != 1 or finishes[node]:
                    invalid.add(node)
                if phase == "setup" and seen:
                    invalid.add(node)
                if phase == "call" and seen.get("setup", {}).get("outcome") != "passed":
                    invalid.add(node)
                if phase == "teardown" and (
                    "setup" not in seen
                    or (seen["setup"]["outcome"] == "passed") != ("call" in seen)
                ):
                    invalid.add(node)
                if phase not in {"setup", "call", "teardown"} or phase in phases[node]:
                    invalid.add(node)
                else:
                    phases[node][phase] = event
            else:
                invalid.add(node)
        for node in expected_ids:
            reports = phases[node]
            setup, call, teardown = (reports.get(name) for name in ("setup", "call", "teardown"))
            valid = (
                node not in invalid
                and starts[node] == finishes[node] == 1
                and setup is not None
                and teardown is not None
                and all(
                    v.get("outcome") in {"passed", "failed", "skipped"} for v in reports.values()
                )
                and (
                    (setup["outcome"] == "passed" and call is not None)
                    or (setup["outcome"] != "passed" and call is None)
                )
            )
            if not valid:
                status = "unsettled"
            elif setup["outcome"] == "failed" or teardown["outcome"] == "failed":
                status = "error"
            elif teardown["outcome"] == "skipped":
                status = "teardown-skipped"
            elif setup["outcome"] == "skipped":
                status = "xfailed" if setup.get("wasxfail") else "skipped"
            elif call["outcome"] == "failed":
                status = "failed"
            elif call["outcome"] == "skipped":
                status = "xfailed" if call.get("wasxfail") else "skipped"
            else:
                status = "xpassed" if call.get("wasxfail") else "passed"
            outcomes[node] = {"status": status, "phases": reports}
        if any(
            value["status"] in {"unsettled", "failed", "error", "teardown-skipped"}
            for value in outcomes.values()
        ):
            errors.append("failed/error/unsettled case results")
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append(f"report loss/invalid report: {error}")
    if child.process.returncode != 0 or child.errors:
        errors.append(
            f"native child exit/output failure: {child.process.returncode}, {child.errors}"
        )
    return outcomes, errors


def parallel(arguments):
    root = Path(os.environ.get("CI_ENGINE_TEST_OUTPUT", "build/engine-tests")).resolve()
    root.mkdir(parents=True, exist_ok=True)
    run = root / ("run-" + uuid4().hex)
    run.mkdir()
    children, outcomes, errors = [], {}, []
    summary = {"passed": False, "pytestArgs": arguments, "requestedWorkers": 2, "run": str(run)}
    summary["controlHashes"] = {
        name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
        for name in ("run-engine-tests.py", "engine-test-reporting.py")
    }
    summary["checkout"] = {}
    for name, revision in (("head", "HEAD"), ("tree", "HEAD^{tree}")):
        result = subprocess.run(["git", "rev-parse", revision], capture_output=True, check=False)
        summary["checkout"][name] = (
            result.stdout.decode("ascii").strip() if result.returncode == 0 else None
        )
    for name in (signal.SIGINT, signal.SIGTERM):
        signal.signal(name, receive_signal)
    try:
        collector = launch(run / "collection", [*arguments, "--collect-only"])
        children.append(collector)
        wait([collector])
        if collector.process.returncode != 0 or collector.errors or _signal:
            raise ValueError("native full collection failed/interrupted")
        full = load_collection(collector.folder)
        collection_events = [
            json.loads(line)
            for line in (collector.folder / "events.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        if (
            len(collection_events) != 2
            or not session_owned(collector, collection_events[0])
            or collection_events[1].get("event") != "session_finish"
            or collection_events[1].get("exitstatus") != 0
        ):
            raise ValueError("native full collection report missing or invalid")
        groups, weights = partition(full["items"])
        write(run / "assignment.json", {"groups": groups, "heuristicScores": weights})
        summary.update(
            fullManifest=str(collector.folder / "collection.json"),
            fullCount=len(full["items"]),
            workers=len(groups),
        )
        workers = []
        for index, files in enumerate(groups):
            if _signal:
                break
            expected = [item for item in full["items"] if item["file"] in files]
            child = launch(
                run / f"worker-{index + 1}",
                arguments,
                {"files": files, "items": expected, "identity": full["identity"]},
            )
            children.append(child)
            workers.append(child)
        wait(workers)
        for child, files in zip(workers, groups, strict=False):
            expected = [item for item in full["items"] if item["file"] in files]
            settled, issues = account(child, expected, full["identity"])
            if outcomes.keys() & settled.keys():
                errors.append("duplicate node across shards")
            outcomes.update(settled)
            errors.extend(issues)
        universe = {item["nodeid"] for item in full["items"]}
        if set(outcomes) != universe or len(workers) != len(groups):
            errors.append("coverage mismatch against full native collection")
        summary["reportCoverage"] = {
            "expected": len(universe),
            "reported": len(outcomes),
            "missing": sorted(universe - outcomes.keys()),
            "unexpected": sorted(outcomes.keys() - universe),
        }
        for node in universe - outcomes.keys():
            outcomes[node] = {"status": "unsettled", "phases": {}}
        summary["counts"] = dict(Counter(value["status"] for value in outcomes.values()))
        summary["passed"] = not errors and not _signal
    except Exception as error:
        errors.append(f"{type(error).__name__}: {error}")
    finally:
        if any(child.process.poll() is None for child in children):
            stop(children)
            for child in children:
                for reader in child.readers:
                    if reader.ident is not None:
                        reader.join(timeout=2)
        summary.update(parentSignal=_signal, errors=errors, outcomes=outcomes)
        write(run / "summary.json", summary)
        print(f"Engine CI accounting: {str(run / 'summary.json')!a}; passed={summary['passed']}")
    return 128 + _signal if _signal else (0 if summary["passed"] else 1)


def single_report_exec(arguments):
    """Opt-in mode1 report: one exclusive run dir plus launch manifest, then os.execv
    the same PID into native pytest appending only the existing report options.
    Directory/identity/manifest failures return nonzero before any exec."""
    root = Path(os.environ.get("CI_ENGINE_TEST_OUTPUT", "build/engine-tests")).resolve()
    try:
        root.mkdir(parents=True, exist_ok=True)
        run = root / ("run-" + uuid4().hex)
        run.mkdir()
        owner = uuid4().hex
        control_hashes = {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ("run-engine-tests.py", "engine-test-reporting.py")
        }
        checkout = {}
        for name, revision in (("head", "HEAD"), ("tree", "HEAD^{tree}")):
            result = subprocess.run(
                ["git", "rev-parse", revision], capture_output=True, check=False
            )
            if result.returncode != 0:
                raise ValueError(f"git identity unavailable: {revision}")
            checkout[name] = result.stdout.decode("ascii").strip()
        argv = [sys.executable, "-m", "pytest", *arguments]
        exec_argv = [
            *argv,
            "-p",
            PLUGIN,
            f"--engine-ci-report={run}",
            f"--engine-ci-owner={owner}",
        ]
        write(
            run / "launch-manifest.json",
            {
                "mode": "single-report",
                "optIn": {
                    "CI_ENGINE_TEST_SHARDS": "1",
                    "CI_ENGINE_TEST_REPORT_SINGLE": "1",
                },
                "owner": owner,
                "pid": os.getpid(),
                "parentPid": os.getppid(),
                "argv": argv,
                "execArgv": exec_argv,
                "cwd": os.getcwd(),
                "checkout": checkout,
                "controlHashes": control_hashes,
                "reportDir": str(run),
            },
        )
    except (OSError, ValueError) as error:
        print(f"single report initialization failure: {error}", file=sys.stderr)
        return 1
    # os.execv replaces this process image: the manifest PID is the PID that runs pytest.
    os.execv(sys.executable, exec_argv)


def main():
    mode = os.environ.get("CI_ENGINE_TEST_SHARDS", "1")
    if mode == "1":
        if os.environ.get("CI_ENGINE_TEST_REPORT_SINGLE") == "1":
            return single_report_exec(sys.argv[1:])
        os.execv(sys.executable, [sys.executable, "-m", "pytest", *sys.argv[1:]])
    if mode != "2":
        print("CI_ENGINE_TEST_SHARDS must be 1 or 2", file=sys.stderr)
        return 2
    return parallel(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
