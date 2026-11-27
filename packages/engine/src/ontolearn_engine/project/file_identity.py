"""Main-selected existing database identity; never accepted through an RPC."""

import errno
import gc
import os
import re
import sqlite3
import stat
import sys
import threading
from contextlib import contextmanager
from pathlib import Path

from ontolearn_engine.project.format3 import Format3Fault

_OPEN_LOCK = threading.Lock()
_MAX_DESCRIPTORS = 4096


def identity_value(value):
    if (
        type(value) is not str
        or re.fullmatch(r"(?:0|[1-9][0-9]{0,39}):(?:0|[1-9][0-9]{0,39})", value) is None
    ):
        raise ValueError("Invalid library file identity")
    return tuple(int(item) for item in value.split(":"))


def verify(path, identity, *, require_existing=False):
    expected = identity_value(identity)
    path = Path(path)
    try:
        # The main picker hands over a canonical real path. Reject symlinks in
        # any component and absent files; never create a substitute on restart.
        if not path.is_absolute() or path.resolve(strict=True) != path:
            raise Format3Fault("structure")
        observed = path.lstat()
        if (
            not stat.S_ISREG(observed.st_mode)
            or observed.st_nlink != 1
            or (observed.st_dev, observed.st_ino) != expected
        ):
            raise Format3Fault("structure")
        if require_existing:
            with path.open("rb") as handle:
                if handle.read(16) != b"SQLite format 3\x00":
                    raise Format3Fault("structure")
    except OSError:
        raise Format3Fault("structure") from None


def _regular_descriptors():
    """Snapshot actual handles, not the names SQLite reports via database_list.

    A SQLite connection opens its own regular descriptor on supported POSIX
    builds. The bootstrap rejects missing/ambiguous ownership rather than
    guessing which descriptor belongs to the connection. This is before any
    SQL, migration, worker startup, or application admission.
    """
    directory = "/proc/self/fd" if sys.platform == "linux" else "/dev/fd"
    observed = {}
    with os.scandir(directory) as entries:
        for count, entry in enumerate(entries, 1):
            if count > _MAX_DESCRIPTORS or not entry.name.isdecimal():
                raise Format3Fault("structure")
            fd = int(entry.name)
            try:
                info = os.fstat(fd)
            except OSError as error:
                # An entry can disappear during OS enumeration. Existing
                # regular descriptors are still required to survive unchanged.
                if error.errno == errno.EBADF:
                    continue
                raise
            if stat.S_ISREG(info.st_mode):
                observed[fd] = (info.st_dev, info.st_ino, info.st_mode)
    return observed


def _check_handle(fd, expected, *, require_existing):
    info = os.fstat(fd)
    if (
        not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
        or (info.st_dev, info.st_ino) != expected
    ):
        raise Format3Fault("structure")
    if require_existing:
        # Do not move SQLite's seek position. The Windows guard is our own
        # separately owned descriptor, so seeking it cannot affect SQLite.
        if os.name == "nt":
            os.lseek(fd, 0, os.SEEK_SET)
            header = os.read(fd, 16)
        else:
            header = os.pread(fd, 16, 0)
        if header != b"SQLite format 3\x00":
            raise Format3Fault("structure")


@contextmanager
def _windows_path_guard(path, expected, *, require_existing):
    """Keep every path component non-renamable while SQLite opens the file.

    Use the public CreateFileW sharing contract, without FILE_SHARE_DELETE.
    Guard ancestors root-first and reject reparse points. This avoids relying
    on CPython's private sqlite connection layout or enumerating NT handles.
    """
    import ctypes
    import msvcrt
    from ctypes import wintypes

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    create.restype = wintypes.HANDLE
    close = kernel.CloseHandle
    close.argtypes = [wintypes.HANDLE]
    close.restype = wintypes.BOOL

    class AttributeInfo(ctypes.Structure):
        _fields_ = [("attributes", wintypes.DWORD), ("reparseTag", wintypes.DWORD)]

    attributes = kernel.GetFileInformationByHandleEx
    attributes.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
    attributes.restype = wintypes.BOOL
    invalid = ctypes.c_void_p(-1).value
    handles = []
    fd = None
    try:
        # GENERIC_READ, SHARE_READ|SHARE_WRITE, OPEN_EXISTING,
        # BACKUP_SEMANTICS|OPEN_REPARSE_POINT. A directory handle protects the
        # directory name, not its unrelated children or their normal writes.
        if len(path.parents) > 256:
            raise Format3Fault("structure")
        for component in [*reversed(path.parents), path]:
            handle = create(str(component), 0x80000000, 3, None, 3, 0x02200000, None)
            if handle == invalid:
                raise OSError(ctypes.get_last_error(), "Cannot guard selected library")
            handles.append(handle)
            info = AttributeInfo()
            if not attributes(handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
                raise OSError(ctypes.get_last_error(), "Cannot inspect selected library")
            if info.attributes & 0x400:  # FILE_ATTRIBUTE_REPARSE_POINT
                raise Format3Fault("structure")
            if bool(info.attributes & 0x10) != (component != path):
                raise Format3Fault("structure")
        # The CRT now owns only the file handle; all ancestors stay owned here.
        fd = msvcrt.open_osfhandle(handles[-1], os.O_RDONLY | os.O_BINARY)
        handles.pop()
        _check_handle(fd, expected, require_existing=require_existing)
        yield fd
    finally:
        failures = []
        if fd is not None:
            try:
                os.close(fd)
            except OSError as error:
                failures.append(error)
        for handle in reversed(handles):
            if not close(handle):
                failures.append(OSError(ctypes.get_last_error(), "Cannot close library guard"))
        if failures and sys.exc_info()[0] is None:
            raise failures[0]


class _SelectedConnection(sqlite3.Connection):
    """Public SQLite factory extension; never inspects CPython object memory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._selected_binding = None
        self._selected_guard = None
        self._selected_failed = False

    def verify_identity(self):
        if self._selected_failed or self._selected_binding is None:
            raise Format3Fault("structure")
        path, identity, fd, require_existing = self._selected_binding
        try:
            _check_handle(fd, identity_value(identity), require_existing=require_existing)
            verify(path, identity, require_existing=require_existing)
        except (OSError, Format3Fault):
            self._selected_failed = True
            raise Format3Fault("structure") from None

    def close(self):
        self._selected_failed = True
        try:
            super().close()
        finally:
            guard, self._selected_guard = self._selected_guard, None
            if guard is not None:
                guard.__exit__(None, None, None)


def verify_connection(connection):
    """Recheck the originally bound handle at a new read/write admission.

    A failed observation permanently fences this connection; restoring a path
    is not authorization to silently rebind it. Only SQLite closes its own fd.
    """
    if not isinstance(connection, _SelectedConnection):
        raise Format3Fault("structure")
    connection.verify_identity()


def connect_verified(path, identity, *, require_existing=False):
    """Open exactly the main-selected physical file, before executing any SQL.

    Path stat before/after connect alone admits ABA: another inode can occupy
    the name only during sqlite3_open and be moved away before the second stat.
    POSIX verifies the newly opened actual descriptor. This is a serialized
    bootstrap before the production reader thread starts. Any concurrent
    regular-descriptor activity makes ownership ambiguous and is refused;
    this is not a general-purpose multithreaded SQLite connector. Windows
    prevents rename using public kernel sharing rules for the complete path.
    """
    expected = identity_value(identity)
    path = Path(path)
    connection = None
    guard = None
    try:
        with _OPEN_LOCK:
            verify(path, identity, require_existing=require_existing)
            if os.name == "nt":
                guard = _windows_path_guard(path, expected, require_existing=require_existing)
                fd = guard.__enter__()
                verify(path, identity, require_existing=require_existing)
                connection = sqlite3.connect(
                    path.as_uri() + "?mode=rw",
                    uri=True,
                    isolation_level=None,
                    timeout=5,
                    factory=_SelectedConnection,
                )
                connection._selected_guard, guard = guard, None
                verify(path, identity, require_existing=require_existing)
            elif sys.platform in {"linux", "darwin"}:
                # Allocation of a Connection can trigger cyclic GC, which can
                # close unrelated unreachable SQLite connections mid-snapshot.
                # Defer automatic collection for this serial bootstrap only;
                # never collect explicitly or weaken the identity comparison.
                gc_enabled = gc.isenabled()
                if gc_enabled:
                    gc.disable()
                try:
                    before = _regular_descriptors()
                    connection = sqlite3.connect(
                        path.as_uri() + "?mode=rw",
                        uri=True,
                        isolation_level=None,
                        timeout=5,
                        factory=_SelectedConnection,
                    )
                    after = _regular_descriptors()
                finally:
                    if gc_enabled:
                        gc.enable()
                added = {fd for fd in after if fd not in before}
                if (
                    len(added) != 1
                    or any(after.get(fd) != value for fd, value in before.items())
                    or after[next(iter(added))][:2] != expected
                ):
                    raise Format3Fault("structure")
                fd = next(iter(added))
                _check_handle(fd, expected, require_existing=require_existing)
                verify(path, identity, require_existing=require_existing)
            else:
                raise Format3Fault("structure")
            connection._selected_binding = (path, identity, fd, require_existing)
        return connection
    except BaseException as error:
        failures = []
        try:
            if connection is not None:
                connection.close()
        except BaseException as cleanup_error:
            failures.append(type(cleanup_error).__name__)
        if guard is not None:
            try:
                guard.__exit__(type(error), error, error.__traceback__)
            except BaseException as cleanup_error:
                failures.append(type(cleanup_error).__name__)
        if failures:
            error.add_note("Library guard cleanup failed: " + ", ".join(failures))
        if isinstance(error, OSError):
            raise Format3Fault("structure") from None
        raise
