"""Portable policy tests and separately marked real Windows handle checks."""

import ctypes
import os
import subprocess

import pytest
from ontolearn_engine.project import _windows_resource as resource
from ontolearn_engine.project.mainline import ExampleResourceFault, make_example_provider
from test_mainline_example_provider import bundle as bundle
from test_mainline_example_provider import load


@pytest.mark.parametrize(
    "path",
    [
        r"relative\bundle",
        r"C:bundle",
        r"\\server\share\bundle",
        r"\\?\C:\bundle",
        r"C:\a\..\bundle",
        r"C:\a\stream:ads",
        "C:\\a\\trailing ",
        "C:\\a\\trailing.",
        r"C:\a\NUL.txt",
        r"C:\a\COM¹",
        r"C:\a\LPT9.txt",
        r"C:\a\x?y",
        "C:\\a\\x\0y",
    ],
)
def test_unsupported_names_are_rejected_before_any_api(path, monkeypatch):
    def forbidden():
        raise AssertionError("API reached for unsupported path")

    monkeypatch.setattr(resource, "_Api", forbidden)
    with pytest.raises(resource.ResourceUnavailable, match="^EXAMPLE_RESOURCE_UNAVAILABLE$"):
        with resource.windows_resource(path, 3):
            raise AssertionError("unsupported path accepted")


def test_abi_uses_fixed_status_width_and_pointer_aligned_iosb():
    assert ctypes.sizeof(resource.LONG) == 4
    assert ctypes.sizeof(resource.HANDLE) == ctypes.sizeof(ctypes.c_void_p)
    assert ctypes.sizeof(resource._Status) == 2 * ctypes.sizeof(ctypes.c_void_p)
    assert resource._Status.Information.offset == ctypes.sizeof(ctypes.c_void_p)
    assert ctypes.sizeof(resource._Standard) == 24
    assert resource._Standard.Directory.offset == 21
    assert ctypes.sizeof(resource._Id) == 24
    assert ctypes.sizeof(resource._Basic) == 40


class _FakeApi:
    def __init__(self):
        self.opened, self.closed, self.reads = [], [], []
        self.fail = None
        self.changed = False
        self.root_count = 0

    def local_volume(self, drive):
        assert drive == "C:\\"
        return "\\\\?\\Volume{00000000-0000-0000-0000-000000000000}\\"

    def verify_volume(self, handle, guid):
        assert handle == 1

    def open_existing(self, parent, name, *, directory):
        if name == self.fail:
            raise OSError("secret OS path")
        handle = len(self.opened) + 1
        self.opened.append((handle, parent, name, directory))
        return handle

    def snapshot(self, handle, *, directory):
        return (
            7,
            bytes([handle]) * 16,
            0 if directory else 3,
            4096,
            1,
            10,
            20,
            31 if self.changed else 30,
            0x10 if directory else 0,
            0,
            0x10 if directory else 0,
        )

    def read_bytes(self, handle, maximum):
        self.reads.append((handle, maximum))
        return b"abc"

    def close(self, handle):
        assert handle not in self.closed
        self.closed.append(handle)
        return True


def test_fixed_members_are_relative_and_all_success_handles_close(monkeypatch):
    api = _FakeApi()
    monkeypatch.setattr(resource, "_Api", lambda: api)
    with resource.windows_resource(r"C:\bundle\example", 3) as read:
        assert read("t01-provider.json", 8192) == b"abc"
        assert read("load-input.json", 3) == b"abc"
        assert api.closed == [4, 5]
        assert api.opened[1:3] == [(2, 1, "bundle", True), (3, 2, "example", True)]
        assert api.opened[3:] == [
            (4, 3, "t01-provider.json", False),
            (5, 3, "load-input.json", False),
        ]
    assert api.closed == [4, 5, 3, 2, 1]


@pytest.mark.parametrize("failure", ["directory-open", "member-open", "read", "changed", "info"])
def test_api_failures_reject_without_fallback_and_close_owned_handles(monkeypatch, failure):
    api = _FakeApi()
    monkeypatch.setattr(resource, "_Api", lambda: api)
    if failure == "directory-open":
        api.fail = "example"
    elif failure == "member-open":
        api.fail = "load-input.json"
    elif failure == "read":

        def bad_read(*args):
            raise OSError("secret path and operating system error")

        api.read_bytes = bad_read
    elif failure == "changed":

        def changed_read(*args):
            api.changed = True
            return b"abc"

        api.read_bytes = changed_read
    else:
        api.snapshot = lambda *args, **kwargs: (_ for _ in ()).throw(OSError("info class failed"))
    with pytest.raises(resource.ResourceUnavailable, match="^EXAMPLE_RESOURCE_UNAVAILABLE$"):
        with resource.windows_resource(r"C:\bundle\example", 3) as read:
            read("load-input.json", 3)
    assert sorted(api.closed) == [entry[0] for entry in api.opened]


def test_unknown_member_or_wrong_bound_never_opens_a_file(monkeypatch):
    api = _FakeApi()
    monkeypatch.setattr(resource, "_Api", lambda: api)
    with resource.windows_resource(r"C:\bundle\example", 3) as read:
        for name, maximum in [("../other", 8192), ("load-input.json", 8192), ("other", 3)]:
            with pytest.raises(resource.ResourceUnavailable):
                read(name, maximum)
    assert len(api.opened) == 3


native = pytest.mark.skipif(os.name != "nt", reason="real Windows HANDLE / NTFS contract")


@native
def test_native_held_bundle_rejects_rename_delete_and_preexisting_writer(bundle):
    root, pin = bundle
    root = root.rename(root.with_name("中文😀资源"))
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    delete_open = kernel.CreateFileW
    delete_open.argtypes = [
        ctypes.c_wchar_p,
        resource.ULONG,
        resource.ULONG,
        ctypes.c_void_p,
        resource.ULONG,
        resource.ULONG,
        resource.HANDLE,
    ]
    delete_open.restype = resource.HANDLE
    close = kernel.CloseHandle
    close.argtypes, close.restype = [resource.HANDLE], resource.LONG

    def open_for_delete():
        return delete_open(str(root), 0x10000, 7, None, 3, 0x02000000, None)

    with resource.WindowsResourceRoot(root, len((root / "load-input.json").read_bytes())):
        with pytest.raises(OSError):
            root.rename(root.with_name("renamed"))
        held = open_for_delete()
        if held != ctypes.c_void_p(-1).value:
            assert close(held)
            raise AssertionError("DELETE access accepted while directory is held")
        assert ctypes.get_last_error() == 32  # ERROR_SHARING_VIOLATION
    released = open_for_delete()
    assert released not in {None, ctypes.c_void_p(-1).value}
    assert close(released)
    renamed = root.with_name("renamed")
    root.rename(renamed)
    renamed.rename(root)
    # FILE_ADD_FILE is the directory data-write right, unlike WRITE_ATTRIBUTES.
    directory_writer = delete_open(str(root), 0x2, 7, None, 3, 0x02000000, None)
    assert directory_writer not in {None, ctypes.c_void_p(-1).value}
    try:
        with pytest.raises(ExampleResourceFault, match="^EXAMPLE_RESOURCE_UNAVAILABLE$"):
            load(make_example_provider(root=root, manifest_sha256=pin))
    finally:
        assert close(directory_writer)
    member = root / "load-input.json"
    with member.open("r+b"):
        with pytest.raises(ExampleResourceFault, match="^EXAMPLE_RESOURCE_UNAVAILABLE$"):
            load(make_example_provider(root=root, manifest_sha256=pin))
    assert load(make_example_provider(root=root, manifest_sha256=pin)) == member.read_bytes()


@native
@pytest.mark.parametrize("location", ["intermediate", "root"])
def test_native_junction_is_rejected_at_each_directory_component(bundle, location):
    root, pin = bundle
    junction = root.parent / "junction"
    destination = root.parent if location == "intermediate" else root
    # Junction creation needs no symlink privilege. Failure to construct fixture
    # is a failing test, never evidence that the resource reader rejected it.
    result = subprocess.run(
        ["cmd", "/d", "/c", "mklink", "/J", str(junction), str(destination)],
        capture_output=True,
        timeout=5,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    try:
        alias = junction / root.name if location == "intermediate" else junction
        with pytest.raises(ExampleResourceFault, match="^EXAMPLE_RESOURCE_UNAVAILABLE$"):
            load(make_example_provider(root=alias, manifest_sha256=pin))
    finally:
        os.rmdir(junction)


@native
@pytest.mark.parametrize("failure", ["info", "read", "open"])
def test_native_api_failure_closes_every_owned_handle(bundle, monkeypatch, failure):
    root, pin = bundle
    api = resource._Api()
    closed, opened, close_results = [], [], []
    original_open, original_close = api.open_existing, api.close

    def tracked_open(*args, **kwargs):
        if failure == "open" and not kwargs["directory"]:
            raise OSError("native open failure")
        handle = original_open(*args, **kwargs)
        opened.append(handle)
        return handle

    def tracked_close(handle):
        closed.append(handle)
        result = original_close(handle)
        close_results.append(bool(result))
        return result

    api.open_existing, api.close = tracked_open, tracked_close
    if failure == "info":
        api.info = lambda *args: 0
    elif failure == "read":
        api.read = lambda *args: 0
    monkeypatch.setattr(resource, "_Api", lambda: api)
    with pytest.raises(ExampleResourceFault, match="^EXAMPLE_RESOURCE_UNAVAILABLE$"):
        load(make_example_provider(root=root, manifest_sha256=pin))
    assert sorted(opened) == sorted(closed)
    assert len(closed) == len(set(closed))
    assert close_results and all(close_results)


@pytest.mark.parametrize(
    "result,iosb_status,information,returned",
    [(0x103, 0, 1, 7), (-1, 0, 1, 7), (0, -1, 1, 7), (0, 0, 2, 7), (0, 0, 1, None)],
)
def test_unexpected_native_open_completion_is_rejected_and_handle_closed(
    result, iosb_status, information, returned
):
    api = object.__new__(resource._Api)
    closed = []

    def opened(handle, access, attributes, iosb, *unused):
        ctypes.cast(handle, ctypes.POINTER(resource.HANDLE))[0] = returned
        status = ctypes.cast(iosb, ctypes.POINTER(resource._Status)).contents
        status.Result.Status, status.Information = iosb_status, information
        return result

    api.open, api.close = opened, lambda handle: closed.append(handle.value) or 1
    with pytest.raises(resource.ResourceUnavailable):
        api.open_existing(3, "load-input.json", directory=False)
    assert closed == ([] if returned is None else [returned])
