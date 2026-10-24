"""Fixed bundle reader for local NTFS; no path fallback or resource discovery.

Only imported on Windows. Directory components are opened relative to retained
handles with OPEN_REPARSE_POINT, then checked on that same handle before descent.
"""

import ctypes as c
import re
from contextlib import contextmanager


class ResourceUnavailable(ValueError):
    pass


def _reject():
    raise ResourceUnavailable("EXAMPLE_RESOURCE_UNAVAILABLE")


def _components(root):
    text = str(root)
    if re.fullmatch(r"[A-Za-z]:\\.+", text) is None:
        _reject()
    parts = text[3:].split("\\")
    for part in parts:
        if (
            not part
            or part in {".", ".."}
            or part[-1] in " ."
            or any(ord(ch) < 32 or ch in '<>:"/\\|?*' for ch in part)
            or len(part.encode("utf-16-le")) > 510
            or re.fullmatch(
                r"CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|COM[1-9¹²³]|LPT[1-9¹²³]",
                part.split(".")[0],
                re.I,
            )
        ):
            _reject()
    return text[:3], parts


# Explicit Windows ABI widths: c_long is not 32 bits on every import host.
ULONG = c.c_uint32
LONG = c.c_int32
HANDLE = c.c_void_p


class _Unicode(c.Structure):
    _fields_ = [("Length", c.c_uint16), ("MaximumLength", c.c_uint16), ("Buffer", c.c_void_p)]


class _Attributes(c.Structure):
    _fields_ = [
        ("Length", ULONG),
        ("RootDirectory", HANDLE),
        ("ObjectName", c.POINTER(_Unicode)),
        ("Attributes", ULONG),
        ("SecurityDescriptor", c.c_void_p),
        ("SecurityQualityOfService", c.c_void_p),
    ]


class _StatusUnion(c.Union):
    _fields_ = [("Status", LONG), ("Pointer", c.c_void_p)]


class _Status(c.Structure):
    _fields_ = [("Result", _StatusUnion), ("Information", c.c_size_t)]


class _Tag(c.Structure):
    _fields_ = [("Attributes", ULONG), ("Tag", ULONG)]


class _Standard(c.Structure):
    _fields_ = [
        ("AllocationSize", c.c_int64),
        ("EndOfFile", c.c_int64),
        ("NumberOfLinks", ULONG),
        ("DeletePending", c.c_ubyte),
        ("Directory", c.c_ubyte),
    ]


class _Id(c.Structure):
    _fields_ = [("Volume", c.c_uint64), ("Id", c.c_ubyte * 16)]


class _Basic(c.Structure):
    _fields_ = [
        ("Creation", c.c_int64),
        ("Access", c.c_int64),
        ("Write", c.c_int64),
        ("Change", c.c_int64),
        ("Attributes", ULONG),
    ]


class _Api:
    def __init__(self):
        kernel = c.WinDLL("kernel32", use_last_error=True)
        native = c.WinDLL("ntdll", use_last_error=True)

        def bind(dll, name, result, *arguments):
            function = getattr(dll, name)
            function.restype, function.argtypes = result, list(arguments)
            return function

        self.open = bind(
            native,
            "NtCreateFile",
            LONG,
            c.POINTER(HANDLE),
            ULONG,
            c.POINTER(_Attributes),
            c.POINTER(_Status),
            c.c_void_p,
            ULONG,
            ULONG,
            ULONG,
            ULONG,
            c.c_void_p,
            ULONG,
        )
        self.close = bind(kernel, "CloseHandle", LONG, HANDLE)
        self.kind = bind(kernel, "GetFileType", ULONG, HANDLE)
        self.info = bind(
            kernel, "GetFileInformationByHandleEx", LONG, HANDLE, LONG, c.c_void_p, ULONG
        )
        self.read = bind(
            kernel, "ReadFile", LONG, HANDLE, c.c_void_p, ULONG, c.POINTER(ULONG), c.c_void_p
        )
        self.drive_type = bind(kernel, "GetDriveTypeW", ULONG, c.c_wchar_p)
        self.volume_name = bind(
            kernel, "GetVolumeNameForVolumeMountPointW", LONG, c.c_wchar_p, c.c_wchar_p, ULONG
        )
        self.dos_device = bind(kernel, "QueryDosDeviceW", ULONG, c.c_wchar_p, c.c_wchar_p, ULONG)
        self.final_path = bind(
            kernel, "GetFinalPathNameByHandleW", ULONG, HANDLE, c.c_wchar_p, ULONG, ULONG
        )
        self.volume_info = bind(
            kernel,
            "GetVolumeInformationByHandleW",
            LONG,
            HANDLE,
            c.c_wchar_p,
            ULONG,
            c.POINTER(ULONG),
            c.POINTER(ULONG),
            c.POINTER(ULONG),
            c.c_wchar_p,
            ULONG,
        )

    def open_existing(self, parent, name, *, directory):
        encoded = name.encode("utf-16-le")
        if not encoded or len(encoded) > 65532:
            _reject()
        buffer = c.create_unicode_buffer(name)
        unicode = _Unicode(len(encoded), len(encoded) + 2, c.cast(buffer, c.c_void_p))
        attributes = _Attributes(
            c.sizeof(_Attributes), parent, c.pointer(unicode), 0x40, None, None
        )
        status, handle = _Status(), HANDLE()
        # Directories need attributes/traverse, not FILE_READ_DATA. Type-neutral
        # open avoids the undocumented DIRECTORY_FILE/REPARSE_POINT combination.
        access = 0x100000 | 0x80 | (0x20 if directory else 0x1)
        result = self.open(
            c.byref(handle),
            access,
            c.byref(attributes),
            c.byref(status),
            None,
            0,
            0x1,  # Deny WRITE and DELETE sharing for directories and members.
            0x1,
            0x200000 | 0x20 | (0 if directory else 0x40),
            None,
            0,
        )
        # Own any returned handle even if the completion status is unexpected.
        if result != 0 or status.Result.Status != 0 or status.Information != 1 or not handle.value:
            if handle.value and handle.value != c.c_void_p(-1).value:
                self.close(handle)
            _reject()
        if handle.value == c.c_void_p(-1).value:
            _reject()
        return handle.value

    def snapshot(self, handle, *, directory):
        tag, standard, identity, basic = _Tag(), _Standard(), _Id(), _Basic()
        if self.kind(handle) != 1:
            _reject()
        for code, output in ((9, tag), (1, standard), (18, identity), (0, basic)):
            if not self.info(handle, code, c.byref(output), c.sizeof(output)):
                _reject()
        if (
            tag.Attributes & 0x400
            or tag.Tag
            or basic.Attributes & 0x400
            or bool(standard.Directory) != directory
            or bool(tag.Attributes & 0x10) != directory
            or bool(basic.Attributes & 0x10) != directory
            or standard.DeletePending
            or standard.EndOfFile < 0
        ):
            _reject()
        return (
            identity.Volume,
            bytes(identity.Id),
            standard.EndOfFile,
            standard.AllocationSize,
            standard.NumberOfLinks,
            basic.Creation,
            basic.Write,
            basic.Change,
            tag.Attributes,
            tag.Tag,
            basic.Attributes,
        )

    def local_volume(self, drive):
        device, guid = c.create_unicode_buffer(32768), c.create_unicode_buffer(64)
        if (
            self.drive_type(drive) != 3
            or not self.dos_device(drive[:2], device, len(device))
            or re.fullmatch(r"\\Device\\HarddiskVolume[0-9]+", device.value) is None
            or not self.volume_name(drive, guid, len(guid))
            or re.fullmatch(r"\\\\\?\\Volume\{[0-9a-fA-F-]{36}\}\\", guid.value) is None
            or self.drive_type(guid.value) != 3
        ):
            _reject()
        return guid.value

    def verify_volume(self, handle, guid):
        final, filesystem = c.create_unicode_buffer(32768), c.create_unicode_buffer(64)
        length = self.final_path(handle, final, len(final), 0x1)
        if (
            not 0 < length < len(final)
            or final.value.casefold() != guid.casefold()
            or not self.volume_info(handle, None, 0, None, None, None, filesystem, len(filesystem))
            or filesystem.value != "NTFS"
        ):
            _reject()

    def read_bytes(self, handle, maximum):
        chunks, remaining = [], maximum + 1
        while remaining:
            buffer = c.create_string_buffer(min(65536, remaining))
            count = ULONG()
            if not self.read(handle, buffer, len(buffer), c.byref(count), None):
                _reject()
            if count.value > len(buffer):
                _reject()
            if not count.value:
                break
            chunks.append(buffer.raw[: count.value])
            remaining -= count.value
        return b"".join(chunks)


class WindowsResourceRoot:
    """Two fixed files only; the caller must validate manifest before input."""

    def __init__(self, root, input_bytes):
        self.drive, self.parts = _components(root)
        self.limits = {"t01-provider.json": 8192, "load-input.json": input_bytes}
        self.handles = []
        self.identities = []
        self.api = None

    def __enter__(self):
        try:
            self.api = _Api()
            guid = self.api.local_volume(self.drive)
            root = self.api.open_existing(None, "\\??\\" + guid[4:], directory=True)
            self.handles.append(root)
            self.api.verify_volume(root, guid)
            state = self.api.snapshot(root, directory=True)
            self.identities.append(state[:2])
            for part in self.parts:
                handle = self.api.open_existing(self.handles[-1], part, directory=True)
                self.handles.append(handle)
                state = self.api.snapshot(handle, directory=True)
                if state[0] != self.identities[0][0]:
                    _reject()
                self.identities.append(state[:2])
            return self
        except BaseException as error:
            self.__exit__(type(error), error, error.__traceback__)
            raise

    def _check_chain(self):
        for handle, identity in zip(self.handles, self.identities, strict=True):
            if self.api.snapshot(handle, directory=True)[:2] != identity:
                _reject()

    def read_member(self, name, maximum):
        if self.limits.get(name) != maximum:
            _reject()
        self._check_chain()
        handle = self.api.open_existing(self.handles[-1], name, directory=False)
        try:
            before = self.api.snapshot(handle, directory=False)
            if before[0] != self.identities[0][0] or before[2] > maximum:
                _reject()
            raw = self.api.read_bytes(handle, maximum)
            after = self.api.snapshot(handle, directory=False)
            if before != after or len(raw) != before[2] or len(raw) > maximum:
                _reject()
            self._check_chain()
            return raw
        finally:
            if not self.api.close(handle):
                _reject()

    def __exit__(self, exc_type, exc, traceback):
        failed = False
        while self.handles:
            failed |= not bool(self.api.close(self.handles.pop()))
        if failed and exc_type is None:
            _reject()


@contextmanager
def windows_resource(root, input_bytes):
    # Keep OS details and unsupported API information inside the fixed boundary.
    try:
        with WindowsResourceRoot(root, input_bytes) as opened:
            yield opened.read_member
    except (OSError, ValueError, AttributeError, TypeError, OverflowError, c.ArgumentError):
        raise ResourceUnavailable("EXAMPLE_RESOURCE_UNAVAILABLE") from None
