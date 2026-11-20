"""``ontolearn-project-package-v1`` manifest construction, ZIP build and inspect.

The frozen v1 format replaces the ``t10-envelope-draft-1`` inspector's draft
envelope (which stays untouched for its own regression corpus). Deterministic
member order and timestamps make export bytes reproducible; the inspector
re-verifies every structural rule defensively: relative POSIX paths only, no
``..``/leading ``/``/symlinks/extra flags, member sizes and SHA-256 matching
the manifest exactly, role uniqueness, FR-1000 option isolation, and the
frozen version bounds with explicit import rejection reasons.
"""

import hashlib
import io
import re
import stat
import struct
import zipfile
import zlib
from dataclasses import dataclass

FORMAT_VERSION = "ontolearn-project-package-v1"
CORE_ROLES = frozenset({"definitions", "assertions", "ownership", "checkpoint"})
OPTION_ROLES = {
    "agentSessions": "agent-session",
    "rawSources": "raw-source",
    "derived": "derived",
    "history": "history",
}
ROLES = CORE_ROLES | frozenset(OPTION_ROLES.values())
FORBIDDEN_ROLES = frozenset({"vault", "credentials", "audit", "authorization"})
DEFAULT_OPTIONS = {"agentSessions": False, "rawSources": False, "derived": False, "history": False}
# Honest engine-side format facts for the manifest version columns.
DB_FORMAT_VERSION = 3
CHECKPOINT_SCHEMA_VERSION = 1
APPLICATION_STATE_VERSION = 1
MIN_READER_VERSION = 1
MIN_WRITER_VERSION = 1
READER_VERSION = 1
WRITER_VERSION = 1
# Manifest file paths stay inside the frozen schema pattern (lowercase, no
# reserved device names, data/ prefix, .json or .bin suffix).
PATH = re.compile(
    r"data/(?!(?:con|prn|aux|nul|com[1-9]|lpt[1-9])\.)[a-z0-9][a-z0-9_-]{0,79}\.(?:json|bin)\Z"
)
ROLE_PATHS = {
    "definitions": "data/definitions.json",
    "assertions": "data/assertions.json",
    "ownership": "data/ownership.json",
    "checkpoint": "data/checkpoint.json",
    "agent-session": "data/agent-session.json",
    "raw-source": "data/raw-source.json",
    "derived": "data/derived.json",
    "history": "data/history.json",
}
MAX_ARCHIVE = 40 * 1024 * 1024
MAX_MEMBER = 8 * 1024 * 1024
MAX_MANIFEST = 64 * 1024
MAX_ENTRIES = 64
MAX_TOTAL = 32 * 1024 * 1024
MAX_FILES = 8
SHA = re.compile(r"[0-9a-f]{64}\Z")


class PackageError(ValueError):
    """Fixed private code; import rejection reasons map onto the wire DTO."""


def _require(condition, code):
    if not condition:
        raise PackageError(code)


def build_manifest(kind, options, entries):
    """entries: mapping role -> bytes (already canonical JSON payloads)."""
    _require(kind in ("full", "template"), "KIND_INVALID")
    _require(set(options) == set(DEFAULT_OPTIONS), "OPTIONS_INVALID")
    _require(all(type(value) is bool for value in options.values()), "OPTIONS_INVALID")
    files = []
    for role in sorted(entries):
        _require(role in ROLES and role not in FORBIDDEN_ROLES, "ROLE_INVALID")
        path = ROLE_PATHS[role]
        data = entries[role]
        _require(isinstance(data, (bytes, bytearray)) and len(data) <= MAX_MEMBER, "MEMBER_LIMIT")
        files.append(
            {
                "path": path,
                "role": role,
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    _require(len(files) <= MAX_FILES, "FILE_LIMIT")
    roles = {item["role"] for item in files}
    if kind == "full":
        _require(CORE_ROLES <= roles, "FULL_CORE_MISSING")
    else:
        _require("definitions" in roles, "TEMPLATE_DEFINITIONS_MISSING")
    for option, optional_role in OPTION_ROLES.items():
        _require(optional_role not in roles or options[option], "UNSELECTED_CONTENT")
    return {
        "formatVersion": FORMAT_VERSION,
        "kind": kind,
        "dbFormatVersion": DB_FORMAT_VERSION,
        "checkpointSchemaVersion": CHECKPOINT_SCHEMA_VERSION,
        "applicationStateVersion": APPLICATION_STATE_VERSION,
        "minReaderVersion": MIN_READER_VERSION,
        "minWriterVersion": MIN_WRITER_VERSION,
        "options": dict(options),
        "files": files,
    }


def build_archive(manifest, entries):
    """Deterministic safe ZIP: manifest.json first, then sorted data members."""
    from ontolearn_engine.storage import canonical

    stream = io.BytesIO()
    fixed_date = (1980, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        manifest_bytes = canonical(manifest).encode("utf-8")
        info = zipfile.ZipInfo("manifest.json", date_time=fixed_date)
        info.external_attr = (stat.S_IFREG | 0o600) << 16
        archive.writestr(info, manifest_bytes)
        for record in manifest["files"]:
            _require(PATH.fullmatch(record["path"]) is not None, "UNSAFE_PATH")
            info = zipfile.ZipInfo(record["path"], date_time=fixed_date)
            info.external_attr = (stat.S_IFREG | 0o600) << 16
            archive.writestr(info, entries[record["role"]])
    raw = stream.getvalue()
    _require(len(raw) <= MAX_ARCHIVE, "ARCHIVE_LIMIT")
    return raw


def _preflight(raw):
    _require(isinstance(raw, (bytes, bytearray)) and len(raw) <= MAX_ARCHIVE, "ARCHIVE_LIMIT")
    raw = bytes(raw)
    _require(len(raw) >= 22 and raw[-22:-18] == b"PK\x05\x06", "ARCHIVE_SHAPE")
    disk, start, count_disk, count, size, offset, comment = struct.unpack("<4H2IH", raw[-18:])
    _require(disk == start == comment == 0 and count_disk == count, "ARCHIVE_SHAPE")
    _require(1 <= count <= MAX_ENTRIES, "ARCHIVE_LIMIT")
    _require(size <= 256 * MAX_ENTRIES, "ARCHIVE_LIMIT")
    _require(offset + size == len(raw) - 22, "ARCHIVE_SHAPE")
    return raw, offset, count


def _read_member(raw, item, limit):
    _require(item.file_size <= limit, "ARCHIVE_LIMIT")
    start = item.header_offset + 30 + len(item.filename.encode("ascii"))
    compressed = raw[start : start + item.compress_size]
    if item.compress_type == zipfile.ZIP_STORED:
        payload = compressed
    else:
        decoder = zlib.decompressobj(-15)
        payload = decoder.decompress(compressed, limit + 1)
        _require(
            decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,
            "ARCHIVE_INVALID",
        )
    _require(len(payload) == item.file_size, "ARCHIVE_INVALID")
    _require(zlib.crc32(payload) == item.CRC, "ARCHIVE_INVALID")
    return payload


def _local_layout(raw, entries, central_offset):
    """Reject unindexed local bytes and local headers conflicting with the
    central directory (W4-11).

    Members must start at offset 0 and stay contiguous - no prefix padding, no
    holes, no overlaps - through to the central directory start, and every
    fixed-length local header must agree with its central record on magic,
    general-purpose flags, compression method, CRC and both lengths. The same
    defense is already proven on the frozen draft envelope inspector.
    """
    position = 0
    for item in sorted(entries, key=lambda entry: entry.header_offset):
        _require(item.header_offset == position, "ARCHIVE_LAYOUT")
        _require(position + 30 <= central_offset, "ARCHIVE_LAYOUT")
        header = struct.unpack("<4s5H3I2H", raw[position : position + 30])
        signature, _, flags, compression, _, _, crc, packed, unpacked, name_len, extra_len = header
        _require(signature == b"PK\x03\x04", "ARCHIVE_INVALID")
        _require(flags == item.flag_bits and flags & ~0x800 == 0, "UNSAFE_ENTRY")
        _require(
            (compression, crc, packed, unpacked)
            == (item.compress_type, item.CRC, item.compress_size, item.file_size),
            "ARCHIVE_INVALID",
        )
        _require(extra_len == 0, "UNSAFE_ENTRY")
        start = position + 30
        _require(raw[start : start + name_len] == item.filename.encode("ascii"), "ARCHIVE_INVALID")
        position = start + name_len + packed
        _require(position <= central_offset, "ARCHIVE_LAYOUT")
    _require(position == central_offset, "ARCHIVE_LAYOUT")


# Per-role member payload shapes validated during inspection (W4-07): every
# member's internal JSON structure is checked up front so a malformed package
# is rejected structurally instead of surfacing later as an internal error.
_MEMBER_LIST_SHAPES = {
    "definitions": ("definitions", frozenset({"layer", "id", "payload"})),
    "assertions": (
        "facts",
        frozenset({"id", "subject", "predicate", "object", "owner", "sourceRow", "managedValue"}),
    ),
    "agent-session": (
        "learning",
        frozenset({"attempt", "recordVersion", "course", "task", "payload"}),
    ),
    "history": ("operations", frozenset({"sequence", "operationId", "operationKind"})),
}


def _validate_member_payload(role, payload):
    import json as _json

    try:
        value = _json.loads(payload.decode("utf-8"))
    except (UnicodeError, ValueError, RecursionError):
        raise PackageError("MEMBER_SHAPE") from None
    _require(isinstance(value, dict), "MEMBER_SHAPE")
    if role == "checkpoint":
        _require(
            set(value) == {"domainRevision", "operationSequence", "metadata", "metadataVersion"},
            "MEMBER_SHAPE",
        )
        _require(
            type(value["domainRevision"]) is int and value["domainRevision"] >= 0,
            "MEMBER_SHAPE",
        )
        _require(
            type(value["operationSequence"]) is int and value["operationSequence"] >= 0,
            "MEMBER_SHAPE",
        )
        _require(
            type(value["metadataVersion"]) is int and value["metadataVersion"] >= 0,
            "MEMBER_SHAPE",
        )
        _require(isinstance(value["metadata"], dict), "MEMBER_SHAPE")
        return
    if role == "ownership":
        _require(set(value) == {"mappingState"}, "MEMBER_SHAPE")
        state = value["mappingState"]
        _require(isinstance(state, dict), "MEMBER_SHAPE")
        for owner, status in state.items():
            _require(isinstance(owner, str) and bool(owner), "MEMBER_SHAPE")
            _require(
                isinstance(status, dict) and set(status) == {"generatedVersion", "stale"},
                "MEMBER_SHAPE",
            )
            _require(type(status["generatedVersion"]) is int, "MEMBER_SHAPE")
            _require(isinstance(status["stale"], list), "MEMBER_SHAPE")
        return
    key, fields = _MEMBER_LIST_SHAPES[role]
    _require(set(value) == {key}, "MEMBER_SHAPE")
    records = value[key]
    _require(type(records) is list, "MEMBER_SHAPE")
    for record in records:
        _require(isinstance(record, dict) and set(record) == fields, "MEMBER_SHAPE")
        if role == "definitions":
            _require(
                isinstance(record["layer"], str)
                and isinstance(record["id"], str)
                and isinstance(record["payload"], str),
                "MEMBER_SHAPE",
            )
            try:
                _json.loads(record["payload"])
            except (UnicodeError, ValueError, RecursionError):
                raise PackageError("MEMBER_SHAPE") from None
        elif role == "agent-session":
            _require(
                isinstance(record["attempt"], str)
                and type(record["recordVersion"]) is int
                and isinstance(record["course"], str)
                and isinstance(record["task"], str)
                and isinstance(record["payload"], str),
                "MEMBER_SHAPE",
            )
        elif role == "history":
            _require(
                type(record["sequence"]) is int
                and isinstance(record["operationId"], str)
                and isinstance(record["operationKind"], str),
                "MEMBER_SHAPE",
            )


@dataclass(frozen=True)
class InspectedPackage:
    manifest: dict
    entries: dict  # path -> bytes


def rejection_reason(error):
    """The frozen wire reason carried by this private PackageError code."""
    reasons = {
        "format-unsupported",
        "reader-too-old",
        "writer-too-old",
        "database-unsupported",
        "checkpoint-unsupported",
        "application-unsupported",
        "kind-mismatch",
    }
    code = error.args[0] if error.args else ""
    return code if code in reasons else "unsafe-package"


def _version_reasons(manifest, expected_kind):
    if manifest.get("formatVersion") != FORMAT_VERSION:
        return "format-unsupported"
    for key, bound, reason in (
        ("minReaderVersion", READER_VERSION, "reader-too-old"),
        ("minWriterVersion", WRITER_VERSION, "writer-too-old"),
    ):
        value = manifest.get(key)
        if type(value) is not int or not 1 <= value <= 65535 or value > bound:
            return reason
    if (
        manifest.get("dbFormatVersion") != DB_FORMAT_VERSION
        or type(manifest.get("dbFormatVersion")) is not int
    ):
        return "database-unsupported"
    # Strict integer bounds (bool is an int subclass and must be excluded by
    # the exact-type test); 0/True/"bad" all carry the same frozen reason and
    # never reach a wire handler as INTERNAL_ERROR.
    for key, bound, reason in (
        ("checkpointSchemaVersion", CHECKPOINT_SCHEMA_VERSION, "checkpoint-unsupported"),
        ("applicationStateVersion", APPLICATION_STATE_VERSION, "application-unsupported"),
    ):
        value = manifest.get(key)
        if type(value) is not int or not 1 <= value <= 65535 or value > bound:
            return reason
    if manifest.get("kind") != expected_kind:
        return "kind-mismatch"
    return None


def inspect_v1(raw, expected_kind):
    """Full defensive inspection. Raises :class:`PackageError` on any defect.

    ``rejection_reason`` distinguishes the frozen version/kind reasons from
    the blanket ``unsafe-package``; structural violations are never importable.
    """
    import json as _json

    from ontolearn_engine.storage import canonical

    raw, central_offset, declared_count = _preflight(raw)
    try:
        with zipfile.ZipFile(io.BytesIO(raw), "r") as archive:
            entries_info = archive.infolist()
            _require(len(entries_info) == declared_count, "ARCHIVE_SHAPE")
            seen, total = set(), 0
            for item in entries_info:
                path = item.filename
                _require(item.orig_filename == path, "UNSAFE_PATH")
                _require(path == "manifest.json" or PATH.fullmatch(path) is not None, "UNSAFE_PATH")
                _require(path not in seen, "DUPLICATE_PATH")
                seen.add(path)
                mode = item.external_attr >> 16
                _require(stat.S_IFMT(mode) in {0, stat.S_IFREG}, "UNSAFE_ENTRY")
                _require(not item.flag_bits & 1, "UNSAFE_ENTRY")
                _require(item.compress_type in {0, zipfile.ZIP_DEFLATED}, "UNSAFE_ENTRY")
                _require(not item.extra and not item.comment, "UNSAFE_ENTRY")
                _require(item.file_size <= MAX_MEMBER, "ARCHIVE_LIMIT")
                total += item.file_size
            _require(total <= MAX_TOTAL, "ARCHIVE_LIMIT")
            _local_layout(raw, entries_info, central_offset)
            _require("manifest.json" in seen, "MANIFEST_MISSING")
            manifest_raw = _read(raw, archive.getinfo("manifest.json"), MAX_MANIFEST)
            try:
                manifest = _json.loads(manifest_raw.decode("utf-8"))
            except (UnicodeError, ValueError, RecursionError):
                raise PackageError("MANIFEST_SHAPE") from None
            _require(isinstance(manifest, dict), "MANIFEST_SHAPE")
            _require(
                set(manifest)
                == {
                    "formatVersion",
                    "kind",
                    "dbFormatVersion",
                    "checkpointSchemaVersion",
                    "applicationStateVersion",
                    "minReaderVersion",
                    "minWriterVersion",
                    "options",
                    "files",
                },
                "MANIFEST_SHAPE",
            )
            _require(canonical(manifest).encode("utf-8") == manifest_raw, "MANIFEST_SHAPE")
            reason = _version_reasons(manifest, expected_kind)
            if reason is not None:
                raise PackageError(reason)
            options = manifest["options"]
            _require(set(options) == set(DEFAULT_OPTIONS), "MANIFEST_SHAPE")
            _require(all(type(value) is bool for value in options.values()), "MANIFEST_SHAPE")
            files = manifest["files"]
            _require(type(files) is list and 1 <= len(files) <= MAX_FILES, "MANIFEST_SHAPE")
            listed, roles = set(), set()
            for record in files:
                _require(
                    isinstance(record, dict) and set(record) == {"path", "role", "size", "sha256"},
                    "MANIFEST_SHAPE",
                )
                path, role, size, digest_hex = (
                    record["path"],
                    record["role"],
                    record["size"],
                    record["sha256"],
                )
                _require(type(path) is str and PATH.fullmatch(path) is not None, "UNSAFE_PATH")
                _require(type(role) is str and role in ROLES, "ROLE_INVALID")
                # Every role maps onto exactly one frozen member path.
                _require(ROLE_PATHS.get(role) == path, "MANIFEST_SHAPE")
                _require(role not in roles, "DUPLICATE_ROLE")
                _require(path not in listed, "DUPLICATE_PATH")
                _require(type(size) is int and 0 <= size <= MAX_MEMBER, "MANIFEST_SHAPE")
                _require(
                    type(digest_hex) is str and SHA.fullmatch(digest_hex) is not None,
                    "MANIFEST_SHAPE",
                )
                for option, optional_role in OPTION_ROLES.items():
                    _require(role != optional_role or options[option], "UNSELECTED_CONTENT")
                listed.add(path)
                roles.add(role)
            _require(seen == listed | {"manifest.json"}, "UNLISTED_OR_MISSING_FILE")
            _require(manifest["kind"] != "full" or CORE_ROLES <= roles, "FULL_CORE_MISSING")
            _require(
                manifest["kind"] != "template" or "definitions" in roles,
                "TEMPLATE_DEFINITIONS_MISSING",
            )
            payload_entries = {}
            for record in files:
                payload = _read(raw, archive.getinfo(record["path"]), MAX_MEMBER)
                _require(len(payload) == record["size"], "SIZE_MISMATCH")
                _require(hashlib.sha256(payload).hexdigest() == record["sha256"], "HASH_MISMATCH")
                _validate_member_payload(record["role"], payload)
                payload_entries[record["path"]] = payload
            return InspectedPackage(manifest, payload_entries)
    except PackageError:
        raise
    except (OSError, ValueError, RuntimeError, EOFError, zipfile.BadZipFile, zlib.error, KeyError):
        raise PackageError("ARCHIVE_INVALID") from None


def _read(raw, item, limit):
    return _read_member(raw, item, limit)
