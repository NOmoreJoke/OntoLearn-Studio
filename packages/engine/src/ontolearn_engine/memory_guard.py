"""Worker memory guards with explicit platform guarantees and fixed exit reasons.

Linux uses a kernel virtual-address-space cap; Windows a kernel committed-process
memory cap. Darwin has no usable per-process RLIMIT_AS here: it uses libproc RSS
sampling plus pre-allocation checks for the controlled infrastructure workload.
Darwin sampling is not a hard allocation cap and can overshoot between samples.
No business/native-library workload is approved by this infrastructure guard.
"""

import ctypes
import errno
import os
import sys
import threading
from functools import lru_cache

MEMORY_LIMIT_EXIT = 74
MEMORY_GUARD_EXIT = 75
MAX_MEMORY_BYTES = 2147483648


class MemoryBudgetExceeded(MemoryError):
    """A known resource budget was exceeded; never includes raw values or paths."""


class MemoryGuardUnavailable(RuntimeError):
    """The required platform guard could not be established or observed."""


class _TaskInfo(ctypes.Structure):
    # SDK sys/proc_info.h proc_taskinfo (6 uint64_t and 12 int32_t fields).
    _fields_ = [
        (name, ctypes.c_uint64)
        for name in (
            "virtual_size",
            "resident_size",
            "total_user",
            "total_system",
            "threads_user",
            "threads_system",
        )
    ] + [
        (name, ctypes.c_int32)
        for name in (
            "policy",
            "faults",
            "pageins",
            "cow_faults",
            "messages_sent",
            "messages_received",
            "syscalls_mach",
            "syscalls_unix",
            "csw",
            "threadnum",
            "numrunning",
            "priority",
        )
    ]


@lru_cache(maxsize=1)
def _darwin_library():
    try:
        library = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
        library.proc_pidinfo.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint64,
            ctypes.c_void_p,
            ctypes.c_int,
        ]
        library.proc_pidinfo.restype = ctypes.c_int
        return library
    except (OSError, AttributeError) as error:
        raise MemoryGuardUnavailable() from error


def resident_bytes(pid: int) -> int:
    """Read actual Darwin RSS; also usable by the parent outside the worker GIL."""
    if sys.platform != "darwin" or type(pid) is not int or pid <= 0:
        raise MemoryGuardUnavailable()
    info = _TaskInfo()
    size = ctypes.sizeof(info)
    library = _darwin_library()
    ctypes.set_errno(0)
    read = library.proc_pidinfo(pid, 4, 0, ctypes.byref(info), size)
    if read != size:
        if read <= 0 and ctypes.get_errno() == errno.ESRCH:
            raise ProcessLookupError(errno.ESRCH, "worker no longer exists")
        raise MemoryGuardUnavailable()
    return info.resident_size


def _windows_job(limit: int):
    from ctypes import wintypes

    class Basic(ctypes.Structure):
        _fields_ = [
            ("ProcessTime", ctypes.c_int64),
            ("JobTime", ctypes.c_int64),
            ("LimitFlags", wintypes.DWORD),
            ("MinWorkingSet", ctypes.c_size_t),
            ("MaxWorkingSet", ctypes.c_size_t),
            ("ActiveProcesses", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("Priority", wintypes.DWORD),
            ("Scheduling", wintypes.DWORD),
        ]

    class Counters(ctypes.Structure):
        _fields_ = [
            (name, ctypes.c_uint64)
            for name in ("ReadOps", "WriteOps", "OtherOps", "ReadBytes", "WriteBytes", "OtherBytes")
        ]

    class Extended(ctypes.Structure):
        _fields_ = [
            ("Basic", Basic),
            ("IO", Counters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    kernel.SetInformationJobObject.restype = wintypes.BOOL
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel.GetCurrentProcess.argtypes = []
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.CreateJobObjectW(None, None)
    settings = Extended()
    settings.Basic.LimitFlags = 0x100  # JOB_OBJECT_LIMIT_PROCESS_MEMORY
    settings.ProcessMemoryLimit = limit
    if not handle:
        raise MemoryGuardUnavailable()
    if not kernel.SetInformationJobObject(
        handle, 9, ctypes.byref(settings), ctypes.sizeof(settings)
    ) or not kernel.AssignProcessToJobObject(handle, kernel.GetCurrentProcess()):
        kernel.CloseHandle(handle)
        raise MemoryGuardUnavailable()
    return kernel, handle


class MemoryGuard:
    def __init__(self, limit: int):
        if type(limit) is not int or not 1 <= limit <= MAX_MEMORY_BYTES:
            raise MemoryGuardUnavailable()
        self.limit = limit
        self._stop = threading.Event()
        self._thread = None
        self._windows = None
        if sys.platform == "darwin":
            self.mode = "darwin-rss-monitor"
            self.native_hard_limit = False
            self.check_allocation(0)
            self._thread = threading.Thread(target=self._monitor, daemon=True)
            self._thread.start()
        elif sys.platform == "win32":
            self.mode = "windows-job"
            self.native_hard_limit = True
            try:
                self._windows = _windows_job(limit)
            except (OSError, AttributeError) as error:
                raise MemoryGuardUnavailable() from error
        elif sys.platform.startswith("linux"):
            self.mode = "linux-rlimit-as"
            self.native_hard_limit = True
            import resource

            try:
                _, hard = resource.getrlimit(resource.RLIMIT_AS)
                cap = limit if hard == resource.RLIM_INFINITY else min(limit, hard)
                resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
                self.limit = cap
            except (OSError, ValueError) as error:
                raise MemoryGuardUnavailable() from error
        else:
            raise MemoryGuardUnavailable()

    def check_allocation(self, size: int) -> None:
        """Reserve conservatively before the controlled test's known allocation.

        This checks live RSS plus the whole proposed allocation on Darwin. It is
        not a general allocator hook or a claim about future native libraries.
        """
        if type(size) is not int or size < 0:
            raise MemoryGuardUnavailable()
        current = resident_bytes(os.getpid()) if self.mode == "darwin-rss-monitor" else 0
        if current + size > self.limit:
            raise MemoryBudgetExceeded()

    def _monitor(self) -> None:
        while not self._stop.wait(0.01):
            try:
                self.check_allocation(0)
            except MemoryError:
                os._exit(MEMORY_LIMIT_EXIT)
            except (MemoryGuardUnavailable, OSError):
                os._exit(MEMORY_GUARD_EXIT)

    def close(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=0.1)
        if self._windows is not None:
            kernel, handle = self._windows
            kernel.CloseHandle(handle)
            self._windows = None


def install_memory_guard(limit: int) -> MemoryGuard:
    return MemoryGuard(limit)
