"""Packaged B1a runner with owned process cleanup; no process-name-wide killing.

Linux uses a subreaper and pidfds (including setsid/double-fork descendants).
Windows assigns a gated launcher to a non-breakaway Job Object before allowing
any test process to spawn. macOS uses exact BSD start times for observed owners
plus the two B1a specs' launch manifest; it does not claim kernel containment.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import select
import shutil
import signal
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Process:
    pid: int
    ppid: int
    pgid: int
    birth: str
    zombie: bool


class BSDInfo(ctypes.Structure):
    _fields_ = (
        [
            (name, ctypes.c_uint32)
            for name in (
                "flags",
                "status",
                "xstatus",
                "pid",
                "ppid",
                "uid",
                "gid",
                "ruid",
                "rgid",
                "svuid",
                "svgid",
                "reserved",
            )
        ]
        + [("comm", ctypes.c_char * 16), ("name", ctypes.c_char * 32)]
        + [(name, ctypes.c_uint32) for name in ("nfiles", "pgid", "jobc", "tdev", "tpgid")]
        + [
            ("nice", ctypes.c_int32),
            ("start_sec", ctypes.c_uint64),
            ("start_usec", ctypes.c_uint64),
        ]
    )


def process_info(pid: int) -> Process | None:
    if sys.platform == "linux":
        try:
            raw = Path(f"/proc/{pid}/stat").read_text()
        except FileNotFoundError:
            return None
        values = raw.rpartition(")")[2].split()
        if len(values) < 20:
            raise RuntimeError("Incomplete /proc identity")
        return Process(pid, int(values[1]), int(values[2]), values[19], values[0] == "Z")
    if sys.platform == "darwin":
        lib = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
        lib.proc_pidinfo.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint64,
            ctypes.c_void_p,
            ctypes.c_int,
        ]
        value = BSDInfo()
        count = lib.proc_pidinfo(pid, 3, 0, ctypes.byref(value), ctypes.sizeof(value))
        if count == 0:
            return None
        if count != ctypes.sizeof(value) or value.pid != pid:
            raise RuntimeError("Incomplete BSD process identity")
        return Process(
            pid, value.ppid, value.pgid, f"{value.start_sec}:{value.start_usec}", value.status == 5
        )
    return None


def process_table() -> dict[int, Process]:
    if sys.platform == "linux":
        pids = [int(value.name) for value in Path("/proc").iterdir() if value.name.isdigit()]
    elif sys.platform == "darwin":
        lib = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
        lib.proc_listallpids.argtypes = [ctypes.c_void_p, ctypes.c_int]
        values = (ctypes.c_int * 65536)()
        count = lib.proc_listallpids(values, ctypes.sizeof(values))
        if count <= 0 or count >= len(values):
            raise RuntimeError("BSD process inventory unavailable or over bound")
        pids = list(values[:count])
    else:
        return {}
    result = {}
    for pid in pids:
        if pid <= 0:
            continue
        info = process_info(pid)
        if info is not None:
            result[pid] = info
    return result


def process_command(pid: int) -> str | None:
    if sys.platform == "linux":
        try:
            return (
                Path(f"/proc/{pid}/cmdline")
                .read_bytes()
                .replace(b"\0", b" ")
                .decode("utf-8", "replace")
            )
        except FileNotFoundError:
            return None
    if sys.platform == "darwin":
        result = subprocess.run(
            ["/bin/ps", "-ww", "-p", str(pid), "-o", "command="],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    return None


def process_executable(pid: int) -> str | None:
    if sys.platform == "darwin":
        lib = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
        lib.proc_pidpath.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
        buffer = ctypes.create_string_buffer(4096)
        count = lib.proc_pidpath(pid, buffer, len(buffer))
        return buffer.value.decode("utf-8", "strict") if count > 0 else None
    return None


def descends(pid: int, roots: set[int], table: dict[int, Process]) -> bool:
    seen: set[int] = set()
    while pid > 1 and pid not in seen:
        if pid in roots:
            return True
        seen.add(pid)
        value = table.get(pid)
        if value is None:
            return False
        pid = value.ppid
    return False


class WindowsJob:
    """Created before releasing the launcher's stdin gate; no assignment race."""

    def __init__(self):
        from ctypes import wintypes

        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        self.api.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.api.CreateJobObjectW.restype = wintypes.HANDLE
        self.api.SetInformationJobObject.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
        ]
        self.api.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.api.QueryInformationJobObject.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.c_void_p,
        ]
        self.api.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self.api.CloseHandle.argtypes = [wintypes.HANDLE]

        class Basic(ctypes.Structure):
            _fields_ = [
                ("process_time", ctypes.c_int64),
                ("job_time", ctypes.c_int64),
                ("flags", wintypes.DWORD),
                ("min_ws", ctypes.c_size_t),
                ("max_ws", ctypes.c_size_t),
                ("active_limit", wintypes.DWORD),
                ("affinity", ctypes.c_size_t),
                ("priority", wintypes.DWORD),
                ("scheduling", wintypes.DWORD),
            ]

        class IO(ctypes.Structure):
            _fields_ = [
                (name, ctypes.c_uint64)
                for name in (
                    "read_ops",
                    "write_ops",
                    "other_ops",
                    "read_bytes",
                    "write_bytes",
                    "other_bytes",
                )
            ]

        class Extended(ctypes.Structure):
            _fields_ = [
                ("basic", Basic),
                ("io", IO),
                ("process_memory", ctypes.c_size_t),
                ("job_memory", ctypes.c_size_t),
                ("peak_process", ctypes.c_size_t),
                ("peak_job", ctypes.c_size_t),
            ]

        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = Extended()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE; no breakaway.
        if not self.api.SetInformationJobObject(
            self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)
        ):
            self.close()
            raise ctypes.WinError(ctypes.get_last_error())

    def assign(self, child: subprocess.Popen) -> None:
        if not self.api.AssignProcessToJobObject(self.handle, int(child._handle)):
            raise ctypes.WinError(ctypes.get_last_error())

    def active(self) -> int:
        class Accounting(ctypes.Structure):
            _fields_ = [
                (name, ctypes.c_int64)
                for name in ("user", "kernel", "period_user", "period_kernel")
            ] + [(name, ctypes.c_uint32) for name in ("faults", "total", "active", "terminated")]

        value = Accounting()
        if not self.api.QueryInformationJobObject(
            self.handle, 1, ctypes.byref(value), ctypes.sizeof(value), None
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        return value.active

    def terminate(self) -> None:
        if not self.api.TerminateJobObject(self.handle, 1):
            raise ctypes.WinError(ctypes.get_last_error())

    def close(self) -> None:
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


def pidfd_open(pid: int) -> int:
    if hasattr(os, "pidfd_open"):
        return os.pidfd_open(pid)
    libc = ctypes.CDLL(None, use_errno=True)
    call = getattr(libc, "pidfd_open", None)
    if call is None:
        raise RuntimeError("Linux libc lacks pidfd_open")
    call.argtypes, call.restype = [ctypes.c_int, ctypes.c_uint], ctypes.c_int
    result = call(pid, 0)
    if result < 0:
        raise OSError(ctypes.get_errno(), "pidfd_open failed")
    return result


def pidfd_send(handle: int, sig: int) -> None:
    if hasattr(signal, "pidfd_send_signal"):
        signal.pidfd_send_signal(handle, sig)
        return
    libc = ctypes.CDLL(None, use_errno=True)
    call = getattr(libc, "pidfd_send_signal", None)
    if call is None:
        raise RuntimeError("Linux libc lacks pidfd_send_signal")
    call.argtypes, call.restype = (
        [ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint],
        ctypes.c_int,
    )
    if call(handle, sig, None, 0) < 0:
        raise OSError(ctypes.get_errno(), "pidfd_send_signal failed")


class Owners:
    def __init__(self, manifest: Path, run_id: str, executable: Path):
        self.manifest, self.run_id, self.executable = manifest, run_id, executable
        self.known: dict[int, Process] = {}
        self.pidfds: dict[int, int] = {}
        self.errors: list[str] = []
        self.profiles: set[str] = set()
        self.manifest_records = 0
        self.manifest_partial = False
        self.previous_subreaper: int | None = None
        self.owned_pgid: int | None = None
        initial = process_table()
        self.baseline = {
            pid: info
            for pid, info in initial.items()
            if pid != os.getpid() and descends(pid, {os.getpid()}, initial)
        }
        if sys.platform == "linux":
            # uv's standalone CPython can omit these Python wrappers even when
            # the real kernel/libc support pidfds. Exercise the actual handle API.
            probe = pidfd_open(os.getpid())
            try:
                pidfd_send(probe, 0)
            finally:
                os.close(probe)
            libc = ctypes.CDLL(None, use_errno=True)
            previous = ctypes.c_int()
            if (
                libc.prctl(37, ctypes.byref(previous), 0, 0, 0) != 0
                or libc.prctl(36, 1, 0, 0, 0) != 0
            ):
                raise OSError(ctypes.get_errno(), "subreaper unavailable")
            self.previous_subreaper = previous.value

    def register(
        self, info: Process, table: dict[int, Process], *, manifest_proof: bool = False
    ) -> None:
        if info.pid <= 1 or info.pid == os.getpid():
            return
        excluded = {
            pid
            for pid, prior in self.baseline.items()
            if table.get(pid) and table[pid].birth == prior.birth
        }
        if descends(info.pid, excluded, table):
            return
        existing = self.known.get(info.pid)
        if existing and existing.birth == info.birth:
            return
        if info.zombie:
            return
        if sys.platform == "linux":
            try:
                handle = pidfd_open(info.pid)
            except ProcessLookupError:
                return
            current = process_info(info.pid)
            # Prove current ancestry AFTER obtaining the stable signaling handle.
            if (
                current is None
                or current.birth != info.birth
                or (not manifest_proof and not descends(info.pid, {os.getpid()}, table))
            ):
                os.close(handle)
                return
            previous = self.pidfds.pop(info.pid, None)
            if previous is not None:
                os.close(previous)
            self.pidfds[info.pid] = handle
        self.known[info.pid] = info

    def read_manifest(self, table: dict[int, Process]) -> None:
        try:
            with self.manifest.open("rb") as stream:
                raw = stream.read(1048577)
        except FileNotFoundError:
            return
        if len(raw) > 1048576:
            raise RuntimeError("Ownership manifest over bound")
        self.manifest_partial = bool(raw and not raw.endswith(b"\n"))
        lines = raw.splitlines(keepends=True)
        if len(lines) > 512:
            raise RuntimeError("Ownership manifest record cap")
        for line in lines:
            if not line.endswith(b"\n"):
                continue  # An atomic single-record append can still be in progress.
            record = json.loads(line)
            if record.get("runId") != self.run_id:
                raise RuntimeError("Foreign ownership manifest")
            profile = record.get("profile")
            if not isinstance(profile, str) or not os.path.isabs(profile):
                raise RuntimeError("Invalid owned profile")
            self.profiles.add(profile)
            identities = record.get("identities", [])
            if not isinstance(identities, list) or len(identities) > 32:
                raise RuntimeError("Invalid ownership identities")
            for raw_identity in identities:
                info = Process(**raw_identity)
                current = table.get(info.pid)
                if current and current.birth == info.birth:
                    # The manifest is emitted by the runner-owned test process,
                    # using this script's actual OS birth-time reader. PID alone
                    # and caller-provided new argv never authorize signaling.
                    self.register(current, table, manifest_proof=True)
        self.manifest_records = len(lines)

    def scan(self, *, read_manifest: bool = True) -> dict[int, Process]:
        table = process_table()
        if sys.platform == "linux":
            # A relaunched app can exit while the test leader still waits for
            # its /proc entry to disappear. Reap only our adopted zombies;
            # the direct launcher must stay allocated to pin its process group.
            for pid, info in list(table.items()):
                prior = self.baseline.get(pid)
                if (
                    pid != self.owned_pgid
                    and info.ppid == os.getpid()
                    and info.zombie
                    and (prior is None or prior.birth != info.birth)
                ):
                    try:
                        reaped, _status = os.waitpid(pid, os.WNOHANG)
                    except ChildProcessError:
                        continue
                    if reaped == pid:
                        table.pop(pid, None)
        if read_manifest:
            self.read_manifest(table)
        for info in table.values():
            if info.pid != os.getpid() and descends(info.pid, {os.getpid()}, table):
                self.register(info, table)
            elif self.owned_pgid is not None and info.pgid == self.owned_pgid:
                self.register(info, table, manifest_proof=True)
        if sys.platform == "darwin" and self.profiles:
            # Relaunch can reparent to launchd. Only the exact unique test profile
            # and verified packaged executable can add that new main process.
            for info in table.values():
                if info.pid == os.getpid() or info.pid in self.known or info.zombie:
                    continue
                if process_executable(info.pid) != str(self.executable.resolve()):
                    continue
                command = process_command(info.pid)
                if (
                    command
                    and command.startswith(str(self.executable) + " ")
                    and any(
                        f"--user-data-dir={profile}" in command.split() for profile in self.profiles
                    )
                ):
                    self.register(info, table, manifest_proof=True)
            roots = {
                pid
                for pid, old in self.known.items()
                if table.get(pid) and table[pid].birth == old.birth
            }
            for info in table.values():
                if info.pid != os.getpid() and descends(info.pid, roots, table):
                    self.register(info, table, manifest_proof=True)
        return {
            pid: value
            for pid, value in table.items()
            if pid in self.known and value.birth == self.known[pid].birth and not value.zombie
        }

    def send(self, info: Process, sig: int) -> None:
        if sys.platform == "linux":
            try:
                pidfd_send(self.pidfds[info.pid], sig)
            except ProcessLookupError:
                pass
        else:
            # macOS has no pidfd API: require the same microsecond BSD birth
            # immediately before signaling, and report this weaker boundary.
            current = process_info(info.pid)
            if current and current.birth == info.birth and not current.zombie:
                try:
                    os.kill(info.pid, sig)
                except ProcessLookupError:
                    pass

    def close(self) -> None:
        for handle in self.pidfds.values():
            os.close(handle)
        if self.previous_subreaper is not None:
            ctypes.CDLL(None).prctl(36, self.previous_subreaper, 0, 0, 0)


GATED_LAUNCHER = """import json,subprocess,sys
if sys.stdin.buffer.readline()!=b'GO\\n': sys.exit(97)
p=subprocess.Popen(json.loads(sys.argv[1]))
sys.exit(p.wait())
"""


def run_owned(
    command: list[str], env: dict[str, str], output: Path, executable: Path, timeout: float = 180
) -> dict:
    """Own creation/reap rights; retain primary failure separately from cleanup."""
    output.mkdir(parents=True, exist_ok=True)
    run_id = uuid.uuid4().hex
    manifest = output / "process-ownership.jsonl"
    if manifest.exists():
        raise RuntimeError("Ownership output must be fresh")
    manifest.touch(mode=0o600, exist_ok=False)
    environment = {
        **env,
        "B1A_OWNERSHIP_MANIFEST": str(manifest.resolve()),
        "B1A_OWNER_RUN_ID": run_id,
        "B1A_OWNER_PYTHON": sys.executable,
        "B1A_OWNER_SCRIPT": str(Path(__file__).resolve()),
        "B1A_OWNER_PID": str(os.getpid()),
    }
    owners = Owners(manifest, run_id, executable)
    job = WindowsJob() if sys.platform == "win32" else None
    child: subprocess.Popen | None = None
    assigned = False
    exit_watch = None
    saved_handlers = {}

    def cancelled(signum, _frame):
        raise RuntimeError(f"Runner cancelled by signal {signum}")

    for signum in (signal.SIGTERM, signal.SIGINT):
        saved_handlers[signum] = signal.signal(signum, cancelled)
    primary: dict = {"kind": "not-started"}
    cleanup: dict = {
        "complete": False,
        "mode": "windows-job"
        if job
        else "linux-subreaper-pidfd"
        if sys.platform == "linux"
        else "macos-observed-bsd-incarnation",
        "errors": [],
    }

    def cleanup_scan():
        try:
            return owners.scan()
        except Exception as cause:
            cleanup["errors"].append({"phase": "cleanup-inventory", "message": str(cause)[:4096]})
            # Broken evidence must not prevent closing already-owned processes.
            return owners.scan(read_manifest=False)

    try:
        child = subprocess.Popen(
            [sys.executable, "-I", "-c", GATED_LAUNCHER, json.dumps(command)],
            stdin=subprocess.PIPE,
            env=environment,
            start_new_session=os.name != "nt",
        )
        owners.owned_pgid = child.pid if os.name != "nt" else None
        if sys.platform == "darwin":
            exit_watch = select.kqueue()
            exit_watch.control(
                [
                    select.kevent(
                        child.pid,
                        filter=select.KQ_FILTER_PROC,
                        flags=select.KQ_EV_ADD | select.KQ_EV_ENABLE,
                        fflags=select.KQ_NOTE_EXIT,
                    )
                ],
                0,
                0,
            )
        if job:
            job.assign(child)
            assigned = True
        else:
            owners.scan()
        assert child.stdin is not None
        child.stdin.write(b"GO\n")
        child.stdin.close()
        deadline = time.monotonic() + timeout
        while True:
            if job:
                exited = child.poll() is not None  # Windows owned handle remains valid.
            else:
                owners.scan()
                if exit_watch is not None:
                    exited = bool(exit_watch.control([], 1, 0))
                else:
                    state = process_info(child.pid)
                    if state is None:
                        raise RuntimeError("Owned leader disappeared before its exclusive reap")
                    exited = state.zombie
            if exited:
                # POSIX leader stays unreaped until its group and all detached
                # owners have been inspected/closed, preventing pgid reuse.
                if job:
                    code = child.returncode
                else:
                    code = None  # Reaped only after group/descendant cleanup.
                primary = {"kind": "exit", "exitCode": code}
                break
            if time.monotonic() >= deadline:
                primary = {"kind": "timeout", "timeoutSeconds": timeout}
                break
            time.sleep(0.05)
    except BaseException as cause:
        primary = {"kind": "exception", "type": type(cause).__name__, "message": str(cause)[:4096]}
    finally:
        # Repeated graceful cancellation cannot interrupt owned cleanup.
        for signum in saved_handlers:
            signal.signal(signum, signal.SIG_IGN)
        try:
            (output / "exit.json").write_text(json.dumps(primary) + "\n", encoding="utf-8")
        except OSError as cause:
            cleanup["errors"].append({"phase": "primary-evidence", "message": str(cause)[:4096]})
        try:
            if child:
                if job and not assigned:
                    child.terminate()
                    child.wait(timeout=5)
                    cleanup.update(complete=True, hadResidual=True, remaining=0, gateReleased=False)
                elif job:
                    residual = job.active()
                    cleanup["hadResidual"] = residual > 0
                    if residual:
                        job.terminate()
                    end = time.monotonic() + 5
                    while job.active() and time.monotonic() < end:
                        time.sleep(0.05)
                    cleanup["remaining"] = job.active()
                    cleanup["complete"] = cleanup["remaining"] == 0
                else:
                    live = cleanup_scan()
                    cleanup["hadResidual"] = bool(live)
                    for sig in (signal.SIGTERM, signal.SIGKILL):
                        # The unreaped direct leader pins this group ID.
                        if any(info.pgid == child.pid for info in live.values()):
                            try:
                                os.killpg(child.pid, sig)
                            except ProcessLookupError:
                                pass
                            except OSError as cause:
                                cleanup.setdefault("groupSignalErrors", []).append(str(cause))
                        end = time.monotonic() + 2.5
                        while True:
                            live = cleanup_scan()
                            for info in live.values():
                                owners.send(info, sig)
                            if not live or time.monotonic() >= end:
                                break
                            time.sleep(0.05)
                        if not live:
                            break
                    remaining = cleanup_scan()
                    cleanup["remaining"] = [asdict(info) for info in remaining.values()]
                    cleanup["observed"] = [asdict(info) for info in owners.known.values()]
                    cleanup["manifestRecords"] = owners.manifest_records
                    cleanup["manifestComplete"] = not owners.manifest_partial
                    cleanup["complete"] = not remaining and not owners.manifest_partial
                    if sys.platform == "darwin":
                        cleanup["boundary"] = (
                            "Observed ancestry, exact BSD birth and owned profile manifest; "
                            "no kernel detached-process containment "
                            "or atomic signal-by-handle claim."
                        )
                final_code = child.wait(timeout=5)
                if primary.get("kind") == "exit":
                    primary["exitCode"] = final_code
                # Reap only identities the Linux subreaper actually adopted.
                if sys.platform == "linux":
                    adopted = process_table()
                    reapable = set(owners.known) | {
                        pid
                        for pid, info in adopted.items()
                        if info.ppid == os.getpid() and info.zombie and pid not in owners.baseline
                    }
                    for pid in reapable:
                        if pid == child.pid:
                            continue
                        try:
                            os.waitpid(pid, os.WNOHANG)
                        except ChildProcessError:
                            pass
        except BaseException as cause:
            cleanup["errors"].append({"type": type(cause).__name__, "message": str(cause)[:4096]})
            cleanup["complete"] = False
        finally:
            if job:
                job.close()
            owners.close()
            if exit_watch is not None:
                exit_watch.close()
            for signum, handler in saved_handlers.items():
                signal.signal(signum, handler)
            if cleanup["errors"]:
                cleanup["complete"] = False
            (output / "exit.json").write_text(json.dumps(primary) + "\n", encoding="utf-8")
            (output / "cleanup.json").write_text(
                json.dumps(cleanup, indent=2) + "\n", encoding="utf-8"
            )
    return {"primary": primary, "cleanup": cleanup}


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "--describe-pids":
        pids = json.loads(sys.argv[2])
        if (
            not isinstance(pids, list)
            or len(pids) > 32
            or any(type(pid) is not int or pid <= 1 for pid in pids)
        ):
            raise RuntimeError("Invalid process evidence request")
        print(
            json.dumps([asdict(value) for pid in pids if (value := process_info(pid)) is not None])
        )
        return
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    release, output = args.release.resolve(strict=True), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    names = {
        "darwin": "OntoLearn Studio",
        "win32": "OntoLearn Studio.exe",
        "linux": "@ontolearndesktop",
    }
    candidates = []
    for asar in release.rglob("app.asar"):
        resources = asar.parent
        executable = (
            resources.parent / "MacOS" / names[sys.platform]
            if sys.platform == "darwin"
            else resources.parent / names[sys.platform]
        )
        if executable.is_file():
            candidates.append((executable, asar))
    if len(candidates) != 1:
        raise RuntimeError(f"Expected one packaged desktop; found {len(candidates)}")
    executable, asar = candidates[0]
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node runtime unavailable")
    env = os.environ.copy()
    for key in ("ELECTRON_RUN_AS_NODE", "ELECTRON_RENDERER_URL", "I04_TEST_FIXTURE"):
        env.pop(key, None)
    if sys.platform == "linux" and env.get("B1A_NATIVE_ISOLATED") != "1":
        raise RuntimeError("Linux B1a requires its dedicated native display lane")
    command = [
        node,
        str(Path("node_modules/@playwright/test/cli.js").resolve(strict=True)),
        "test",
        "tests/e2e/b1a-project-lifecycle.spec.ts",
        "tests/e2e/b1a-library-location.spec.ts",
        "--workers=1",
        "--reporter=list,github,json",
        f"--output={output / 'test-results'}",
    ]
    env.update(
        ONTOLEARN_PACKAGED_EXECUTABLE=str(executable),
        PLAYWRIGHT_JSON_OUTPUT_FILE=str(output / "report.json"),
    )
    record = {
        "executable": str(executable),
        "executableSha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
        "appAsar": str(asar),
        "appAsarSha256": hashlib.sha256(asar.read_bytes()).hexdigest(),
        "platform": sys.platform,
        "command": command,
        "nativePickerRequired": sys.platform == "linux",
    }
    (output / "launch.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    outcome = run_owned(command, env, output, executable)
    primary, cleanup = outcome["primary"], outcome["cleanup"]
    if primary.get("kind") != "exit" or primary.get("exitCode") != 0:
        raise SystemExit(primary.get("exitCode") or 1)
    if not cleanup["complete"] or cleanup.get("hadResidual"):
        raise RuntimeError("B1a tests left live processes or cleanup is unproven; see cleanup.json")
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    stats = report["stats"]
    if (
        stats["expected"] != (3 if sys.platform == "linux" else 2)
        or stats["unexpected"] != 0
        or stats["flaky"] != 0
        or stats["skipped"] != (0 if sys.platform == "linux" else 1)
    ):
        raise RuntimeError("Incomplete B1a packaged acceptance")


if __name__ == "__main__":
    main()
