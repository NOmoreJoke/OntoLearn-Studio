"""Host<->Engine staging protocol (frozen for W4-A1 & W4-B; verbatim parity).

The desktop main process stages user file selections under
``<stagingRoot>/<selectionId>/`` next to the engine library; the renderer only
ever holds opaque selection tokens. This module is the engine-side reader and
writer for those directories and enforces, in order:

- ``selectionId`` must match ``^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}`` (rejecting
  traversal, separators and ``..``);
- no symlinks anywhere on the walked chain (staging root, selection directory,
  ``meta.json``, payload or output files) using ``O_NOFOLLOW`` opens plus
  before/after fstat identity checks;
- strict ``meta.json`` shape (``version == 1``, exact key set, purpose/format/
  extension/payloadFile allowlists, project + engine-session binding);
- inbound payload SHA-256 and byteLength re-verification against ``meta.json``.

No raw host path ever crosses the boundary in a DTO, error or log: faults use
fixed codes only.
"""

import hashlib
import json
import os
import stat
from uuid import uuid4

SELECTION_ID_MAX = 128
STAGING_DIRECTORY = ".ontolearn-host-selections"
META_FILE = "meta.json"
INBOUND_PURPOSES = frozenset({"mapping-source", "package-import"})
OUTBOUND_PURPOSES = frozenset({"package-export", "report-html"})
# purpose -> allowed (format, extension, payloadFile) tuples
INBOUND_ALLOWLIST = {
    "mapping-source": (
        ("csv", ".csv", "payload.csv"),
        ("xlsx", ".xlsx", "payload.xlsx"),
    ),
    "package-import": (("zip", ".ontolearn.zip", "payload.ontolearn.zip"),),
}
# purpose -> (extension, outputFile)
OUTBOUND_ALLOWLIST = {
    "package-export": (".ontolearn.zip", "output.ontolearn.zip"),
    "report-html": (".html", "output.html"),
}
_HEX = frozenset("0123456789abcdef")


class StagingFault(Exception):
    """Fixed private staging failure kind; mapped by callers to a wire fault."""

    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _fault(code):
    raise StagingFault(code)


def valid_selection_id(selection_id):
    import re

    return (
        isinstance(selection_id, str)
        and 1 <= len(selection_id) <= SELECTION_ID_MAX
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", selection_id) is not None
    )


def staging_root(store):
    """The shared root derives from the owned library file, never a wire input."""
    return store.path.parent / STAGING_DIRECTORY


def _open_selection(store, selection_id):
    """dir_fd for the selection directory; every component opened O_NOFOLLOW."""
    if not valid_selection_id(selection_id):
        _fault("SELECTION_INVALID")
    root = staging_root(store)
    try:
        root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError:
        _fault("STAGING_UNAVAILABLE")
    try:
        if not stat.S_ISDIR(os.fstat(root_fd).st_mode):
            _fault("STAGING_UNAVAILABLE")
        # O_NOFOLLOW on a symlinked directory fails with ELOOP, and a plain
        # file open would lack directory flags entirely.
        sel_fd = os.open(selection_id, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
    except OSError:
        os.close(root_fd)
        _fault("SELECTION_NOT_FOUND")
    os.close(root_fd)
    return sel_fd


def _read_regular(sel_fd, name, maximum):
    """Bounded regular-file read with no-symlink and identity re-checks."""
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=sel_fd)
    except OSError:
        _fault("FILE_UNAVAILABLE")
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            _fault("FILE_UNAVAILABLE")
        with os.fdopen(fd, "rb", closefd=False) as handle:
            raw = handle.read(maximum + 1)
        after = os.fstat(fd)
        if (
            len(raw) != before.st_size
            or len(raw) > maximum
            or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        ):
            _fault("FILE_UNAVAILABLE")
        return raw
    finally:
        os.close(fd)


def _strict_meta(raw):
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError, RecursionError):
        _fault("META_INVALID")
    if not isinstance(value, dict):
        _fault("META_INVALID")
    return value


def _check_common(meta, *, project, engine_session_id, purpose, selection_id):
    if meta.get("version") != 1 or meta.get("selectionId") != selection_id:
        _fault("META_INVALID")
    if meta.get("projectId") != project or meta.get("purpose") != purpose:
        _fault("BINDING_MISMATCH")
    if engine_session_id is not None and meta.get("engineSessionId") != engine_session_id:
        _fault("BINDING_MISMATCH")


def _sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def sha256_hex(raw):
    """Public engine-side SHA-256 helper for staged/published byte identity."""
    return _sha256(raw)


def read_inbound(store, project, engine_session_id, selection_id, purpose, maximum):
    """Return ``(meta, payload_bytes)`` after full protocol verification."""
    if purpose not in INBOUND_PURPOSES:
        _fault("PURPOSE_INVALID")
    sel_fd = _open_selection(store, selection_id)
    try:
        meta = _strict_meta(_read_regular(sel_fd, META_FILE, 65536))
        if set(meta) != {
            "version",
            "selectionId",
            "projectId",
            "engineSessionId",
            "purpose",
            "format",
            "extension",
            "payloadFile",
            "sha256",
            "byteLength",
            "createdAt",
        }:
            _fault("META_INVALID")
        _check_common(
            meta,
            project=project,
            engine_session_id=engine_session_id,
            purpose=purpose,
            selection_id=selection_id,
        )
        allowed = INBOUND_ALLOWLIST[purpose]
        if (meta.get("format"), meta.get("extension"), meta.get("payloadFile")) not in allowed:
            _fault("META_INVALID")
        if not isinstance(meta.get("byteLength"), int) or not 0 <= meta["byteLength"] <= maximum:
            _fault("META_INVALID")
        digest_hex = meta.get("sha256")
        if not isinstance(digest_hex, str) or len(digest_hex) != 64 or not set(digest_hex) <= _HEX:
            _fault("META_INVALID")
        payload = _read_regular(sel_fd, meta["payloadFile"], maximum)
        if len(payload) != meta["byteLength"] or _sha256(payload) != digest_hex:
            _fault("PAYLOAD_MISMATCH")
        return meta, payload
    finally:
        os.close(sel_fd)


def verify_outbound(store, project, engine_session_id, selection_id, purpose):
    """Verify an outbound selection directory and return its meta."""
    if purpose not in OUTBOUND_PURPOSES:
        _fault("PURPOSE_INVALID")
    sel_fd = _open_selection(store, selection_id)
    try:
        meta = _strict_meta(_read_regular(sel_fd, META_FILE, 65536))
        if set(meta) != {
            "version",
            "selectionId",
            "projectId",
            "engineSessionId",
            "purpose",
            "extension",
            "outputFile",
            "createdAt",
        }:
            _fault("META_INVALID")
        _check_common(
            meta,
            project=project,
            engine_session_id=engine_session_id,
            purpose=purpose,
            selection_id=selection_id,
        )
        expected = OUTBOUND_ALLOWLIST[purpose]
        if (meta.get("extension"), meta.get("outputFile")) != expected:
            _fault("META_INVALID")
        return meta
    finally:
        os.close(sel_fd)


def read_report_publication(store, project, engine_session_id, selection_id):
    """Optional receipt from the trusted Main publisher, within the same selection."""
    try:
        sel_fd = _open_selection(store, selection_id)
    except StagingFault as error:
        if error.code in ("SELECTION_NOT_FOUND", "STAGING_UNAVAILABLE"):
            return None  # Normal exact replay after Main cleaned the selection.
        raise
    try:
        name = "report-published.json"
        try:
            os.stat(name, dir_fd=sel_fd, follow_symlinks=False)
        except FileNotFoundError:
            return None
        receipt = _strict_meta(_read_regular(sel_fd, name, 4096))
    finally:
        os.close(sel_fd)
    verify_outbound(store, project, engine_session_id, selection_id, "report-html")
    return receipt


def write_outbound(store, selection_id, output_file, data):
    """Atomically publish staged bytes: 0o600 temp + fsync + verify + replace."""
    sel_fd = _open_selection(store, selection_id)
    temp_name = f".stage-{uuid4().hex}"
    try:
        fd = os.open(
            temp_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=sel_fd,
        )
        try:
            with os.fdopen(fd, "wb", closefd=False) as handle:
                handle.write(data)
                handle.flush()
                os.fsync(fd)
        finally:
            os.close(fd)
        # Verify the staged temp with an explicitly owned, always-closed FD;
        # both the regular-check and every fault path below release it.
        verify_fd = os.open(temp_name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=sel_fd)
        try:
            if not stat.S_ISREG(os.fstat(verify_fd).st_mode):
                _fault("WRITE_FAILED")
        finally:
            os.close(verify_fd)
        try:
            existing = os.open(output_file, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=sel_fd)
        except FileNotFoundError:
            pass
        except OSError:
            _fault("TARGET_INVALID")
        else:
            mode = os.fstat(existing).st_mode
            os.close(existing)
            if not stat.S_ISREG(mode):
                _fault("TARGET_INVALID")
        os.replace(temp_name, output_file, src_dir_fd=sel_fd, dst_dir_fd=sel_fd)
        os.fsync(sel_fd)
        return {"sha256": _sha256(data), "byteLength": len(data)}
    except StagingFault:
        try:
            os.unlink(temp_name, dir_fd=sel_fd)
        except OSError:
            pass
        raise
    except OSError:
        try:
            os.unlink(temp_name, dir_fd=sel_fd)
        except OSError:
            pass
        _fault("WRITE_FAILED")
    finally:
        os.close(sel_fd)


def fault_for(code):
    """Map the fixed private staging codes onto bounded public wire faults.

    No staging detail (paths, names, sizes) is ever echoed; callers only see
    the frozen business3 vocabulary.
    """
    return {
        "SELECTION_INVALID": ("INVALID_REQUEST", {"field": "params"}),
        "SELECTION_NOT_FOUND": ("NOT_FOUND", {"resource": "selection"}),
        "STAGING_UNAVAILABLE": ("PERMISSION_DENIED", {}),
        "FILE_UNAVAILABLE": ("PERMISSION_DENIED", {}),
        "META_INVALID": ("IDENTITY_CONFLICT", {}),
        "BINDING_MISMATCH": ("IDENTITY_CONFLICT", {}),
        "PAYLOAD_MISMATCH": ("IDENTITY_CONFLICT", {}),
        "PURPOSE_INVALID": ("PERMISSION_DENIED", {}),
        "TARGET_INVALID": ("INVALID_STATE", {}),
        "WRITE_FAILED": ("STORAGE_FAILURE", {}),
    }.get(code, ("PERMISSION_DENIED", {}))
