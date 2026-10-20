"""Private owner bootstrap, real early-death checks and simulated Windows APIs.

The Win32 doubles check identity/failure policy and declared ctypes signatures;
only Windows CI can establish actual native behavior through venv/frozen launchers.
"""

import ctypes
import json
import subprocess
import sys
from types import SimpleNamespace

import pytest
from ontolearn_engine import worker
from ontolearn_engine.process_environment import worker_environment


class NativeCall:
    def __init__(self, implementation):
        self.implementation = implementation
        self.calls = []

    def __call__(self, *arguments):
        self.calls.append(arguments)
        return self.implementation(*arguments)


class Kernel:
    def __init__(self):
        self.pid = 4567
        self.handle = 0x100000005
        self.created = 0x123456789ABCDEF
        self.wait = 0x102
        self.opened = True
        self.times_ok = True
        self.close_ok = True
        self.GetCurrentProcess = NativeCall(lambda: -1)
        self.GetProcessId = NativeCall(lambda _handle: self.pid)
        self.OpenProcess = NativeCall(lambda *_: self.handle if self.opened else None)
        self.GetProcessTimes = NativeCall(self._times)
        self.WaitForSingleObject = NativeCall(lambda *_: self.wait)
        self.CloseHandle = NativeCall(lambda _: self.close_ok)

    def _times(self, _handle, created, *_):
        created._obj.dwLowDateTime = self.created & 0xFFFFFFFF
        created._obj.dwHighDateTime = self.created >> 32
        return self.times_ok


@pytest.fixture
def kernel(monkeypatch):
    native = Kernel()
    monkeypatch.setattr(worker.ctypes, "WinDLL", lambda *_a, **_k: native, raising=False)
    return native


def test_win32_signatures_and_pointer_sized_handle_are_explicit(kernel):
    from ctypes import wintypes

    native = worker._windows_kernel()
    assert native.OpenProcess.argtypes == [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    assert native.OpenProcess.restype is wintypes.HANDLE
    assert native.GetCurrentProcess.argtypes == []
    assert native.GetCurrentProcess.restype is wintypes.HANDLE
    assert native.GetProcessId.argtypes == [wintypes.HANDLE]
    assert native.GetProcessId.restype is wintypes.DWORD
    assert (
        native.GetProcessTimes.argtypes
        == [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    )
    assert native.GetProcessTimes.restype is wintypes.BOOL
    assert native.WaitForSingleObject.argtypes == [wintypes.HANDLE, wintypes.DWORD]
    assert native.WaitForSingleObject.restype is wintypes.DWORD
    assert native.CloseHandle.argtypes == [wintypes.HANDLE]
    assert native.CloseHandle.restype is wintypes.BOOL
    owner = worker._WindowsOwner(kernel.pid, kernel.created)
    assert owner.handle == kernel.handle  # A 64-bit value, never a c_int result.
    assert native.OpenProcess.calls == [(0x100000 | 0x1000, False, kernel.pid)]
    assert owner.alive()
    owner.close()
    owner.close()
    assert kernel.CloseHandle.calls == [(kernel.handle,)]


def test_windows_owner_uses_passed_identity_not_an_intermediate_parent(kernel, monkeypatch):
    monkeypatch.setattr(worker, "os", SimpleNamespace(getppid=lambda: 9999))
    owner = worker._WindowsOwner(kernel.pid, kernel.created)
    try:
        assert owner.alive()
        kernel.wait = 0
        assert not owner.alive()
        # A later PID reuse cannot change the already retained process handle.
        kernel.created += 1
        assert not owner.alive()
    finally:
        owner.close()


@pytest.mark.parametrize("failure", ["open", "pid", "birth", "times", "already-dead", "wait"])
def test_windows_startup_rejects_missing_reused_dead_or_unobservable_owner(kernel, failure):
    expected_pid, expected_birth = kernel.pid, kernel.created
    if failure == "open":
        kernel.opened = False
    elif failure == "pid":
        kernel.pid += 1
    elif failure == "birth":
        kernel.created += 1
    elif failure == "times":
        kernel.times_ok = False
    elif failure == "already-dead":
        kernel.wait = 0
    else:
        kernel.wait = 0xFFFFFFFF
    with pytest.raises(worker.OwnerUnavailable):
        worker._WindowsOwner(expected_pid, expected_birth)
    assert kernel.CloseHandle.calls == ([] if failure == "open" else [(kernel.handle,)])


def test_windows_handle_close_failure_is_not_silent(kernel):
    owner = worker._WindowsOwner(kernel.pid, kernel.created)
    kernel.close_ok = False
    with pytest.raises(worker.OwnerUnavailable):
        owner.close()


def test_private_arguments_capture_actual_current_process_and_birth(kernel, monkeypatch):
    monkeypatch.setattr(worker, "sys", SimpleNamespace(platform="win32"))
    monkeypatch.setattr(worker, "os", SimpleNamespace(getpid=lambda: kernel.pid))
    arguments = worker.worker_owner_arguments()
    assert arguments == ["--coordinator-owner", str(kernel.pid), str(kernel.created)]
    assert worker._owner_arguments(arguments) == (kernel.pid, kernel.created)
    assert worker._owner_arguments(["--worker", *arguments]) == (kernel.pid, kernel.created)
    assert kernel.CloseHandle.calls == []  # Current-process pseudo-handle is not closed.


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["--coordinator-owner", "1", "1"],
        ["--coordinator-owner", "-1", "1"],
        ["--coordinator-owner", "１２", "1"],
        ["--coordinator-owner", "4294967296", "1"],
        ["--coordinator-owner", "42", "18446744073709551616"],
        ["--coordinator-owner", "42", "0"],
        ["--coordinator-owner", "42", "1", "extra"],
        ["--unknown", "42", "1"],
    ],
)
def test_private_windows_arguments_fail_closed(monkeypatch, arguments):
    monkeypatch.setattr(worker, "sys", SimpleNamespace(platform="win32"))
    with pytest.raises(worker.OwnerUnavailable):
        worker._owner_arguments(arguments)


def test_owner_monitor_stops_before_closing_the_native_handle():
    actions = []
    monitor = object.__new__(worker._OwnerMonitor)
    monitor.stop = SimpleNamespace(set=lambda: actions.append("stop"))
    monitor.thread = SimpleNamespace(
        join=lambda timeout: actions.append(("join", timeout)), is_alive=lambda: False
    )
    monitor.owner = SimpleNamespace(close=lambda: actions.append("close"))
    monitor.close()
    assert actions == ["stop", ("join", 0.5), "close"]


@pytest.mark.parametrize("failure", [False, worker.OwnerUnavailable(), OSError()])
def test_monitor_exits_with_fixed_code_on_owner_death_or_guard_failure(monkeypatch, failure):
    monitor = object.__new__(worker._OwnerMonitor)
    monitor.stop = SimpleNamespace(wait=lambda _: False)

    def alive():
        if isinstance(failure, BaseException):
            raise failure
        return failure

    monitor.owner = SimpleNamespace(alive=alive)
    exits = []

    class Exited(BaseException):
        pass

    def exit_(code):
        exits.append(code)
        raise Exited()

    monkeypatch.setattr(worker, "os", SimpleNamespace(_exit=exit_))
    with pytest.raises(Exited):
        monitor._watch()
    assert exits == [73]


@pytest.mark.parametrize("bootstrap", ["missing", "owner-already-dead"])
def test_actual_worker_refuses_work_before_a_valid_owner_is_established(bootstrap):
    arguments = []
    if bootstrap == "owner-already-dead":
        identity = subprocess.run(
            [
                sys.executable,
                "-I",
                "-c",
                "import json;from ontolearn_engine.worker import worker_owner_arguments;"
                "print(json.dumps(worker_owner_arguments()),flush=True)",
            ],
            capture_output=True,
            timeout=5,
            check=False,
        )
        assert identity.returncode == 0 and identity.stderr == b""
        arguments = json.loads(identity.stdout)
    request = {"memoryBytes": 536870912, "parameters": {}, "capability": "test.read"}
    process = subprocess.run(
        [sys.executable, "-I", "-m", "ontolearn_engine.worker", *arguments],
        input=json.dumps(request).encode() + b"\n",
        capture_output=True,
        env=worker_environment(),
        timeout=5,
        check=False,
    )
    assert process.returncode == 73
    assert process.stdout == b"" and process.stderr == b""


@pytest.mark.parametrize(
    "api", ["OpenProcess", "GetProcessId", "GetProcessTimes", "WaitForSingleObject"]
)
def test_native_owner_bootstrap_exceptions_fail_closed(kernel, api):
    def fail(*_):
        raise OSError("synthetic native failure")

    getattr(kernel, api).implementation = fail
    with pytest.raises(worker.OwnerUnavailable):
        worker._WindowsOwner(kernel.pid, kernel.created)
    assert kernel.CloseHandle.calls == ([] if api == "OpenProcess" else [(kernel.handle,)])
