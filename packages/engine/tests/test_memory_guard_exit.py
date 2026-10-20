"""Native adapter fault distinctions; actual child-exit coverage is Darwin-only."""

import ctypes
import errno
from types import SimpleNamespace

import pytest
from ontolearn_engine import memory_guard as guard


@pytest.mark.parametrize(
    ("returned", "native_errno", "expected"),
    [
        (0, errno.ESRCH, ProcessLookupError),
        (-1, errno.ESRCH, ProcessLookupError),
        (1, errno.ESRCH, guard.MemoryGuardUnavailable),
        (0, errno.EACCES, guard.MemoryGuardUnavailable),
        (0, None, guard.MemoryGuardUnavailable),
    ],
)
def test_native_rss_distinguishes_only_actual_missing_process(
    monkeypatch, returned, native_errno, expected
):
    def read(*_):
        assert ctypes.get_errno() == 0
        if native_errno is not None:
            ctypes.set_errno(native_errno)
        return returned

    monkeypatch.setattr(guard.sys, "platform", "darwin")
    monkeypatch.setattr(guard, "_darwin_library", lambda: SimpleNamespace(proc_pidinfo=read))
    # An earlier native call's ESRCH must not classify this different failure.
    ctypes.set_errno(errno.ESRCH)
    with pytest.raises(expected) as failure:
        guard.resident_bytes(123)
    if expected is ProcessLookupError:
        assert failure.value.errno == errno.ESRCH


@pytest.mark.parametrize(
    "failure", [guard.MemoryGuardUnavailable(), ProcessLookupError(), PermissionError()]
)
def test_worker_monitor_exits_when_its_own_sampling_cannot_continue(monkeypatch, failure):
    monitor = object.__new__(guard.MemoryGuard)
    monitor._stop = SimpleNamespace(wait=lambda _: False)

    def sample(_):
        raise failure

    class Exited(BaseException):
        pass

    exits = []

    def exit_(code):
        exits.append(code)
        raise Exited()

    monitor.check_allocation = sample
    monkeypatch.setattr(guard.os, "_exit", exit_)
    with pytest.raises(Exited):
        monitor._monitor()
    assert exits == [guard.MEMORY_GUARD_EXIT]
