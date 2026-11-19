"""Bounded read-only ZIP inspection; this draft is NOT an approved project format.

No extraction, file paths, database, pickle, library/plugin loading or migration is exposed.
Hashes prove byte integrity only. Real checkpoint/ownership/replay validators are not ready.
"""

import hashlib
import io
import json
import re
import stat
import struct
import zipfile
import zlib
from dataclasses import dataclass

DRAFT_VERSION = "t10-envelope-draft-1"
# Defensive parser budgets, not measured product capacity or a Q5 acceptance threshold.
MAX_ARCHIVE = 40 * 1024 * 1024
MAX_TOTAL = 32 * 1024 * 1024
MAX_MEMBER = 8 * 1024 * 1024
MAX_MANIFEST = 64 * 1024
MAX_ENTRIES = 256
CORE_ROLES = frozenset({"definitions", "assertions", "ownership", "checkpoint"})
OPTION_ROLES = {
    "rawSources": "raw-source",
    "derived": "derived",
    "history": "history",
    "agentSessions": "agent-session",
}
ROLES = CORE_ROLES | frozenset(OPTION_ROLES.values())
PATH = re.compile(r"data/[a-z0-9][a-z0-9_-]{0,79}\.(?:json|bin)\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
RESERVED = {"con", "prn", "aux", "nul"} | {
    f"{prefix}{number}" for prefix in ("com", "lpt") for number in range(1, 10)
}


class TransferError(ValueError):
    """Fixed private error identifier; never includes input values, paths or exception text."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise TransferError(code)


def _strict(value: object, keys: set[str]) -> dict:
    _require(type(value) is dict and set(value) == keys, "MANIFEST_SHAPE")
    return value


def _pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        _require(key not in result, "MANIFEST_DUPLICATE_KEY")
        result[key] = value
    return result


def _json(raw: bytes) -> dict:
    try:
        return json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(TransferError("MANIFEST_SHAPE")),
        )
    except (UnicodeError, ValueError, RecursionError) as exc:
        if isinstance(exc, TransferError):
            raise
        raise TransferError("MANIFEST_SHAPE") from None


@dataclass(frozen=True)
class Inspection:
    draft_version: str
    declared_kind: str
    roles: tuple[str, ...]
    selected_options: tuple[str, ...]
    included_options: tuple[str, ...]
    # No true values until the approved owner validates semantic coverage and runtime support.
    restore_current: bool = False
    rerun_mapping: bool = False
    replay_runs: bool = False
    import_allowed: bool = False
    reason: str = "UNAPPROVED_FORMAT_AND_UNVERIFIED_PAYLOADS"


def _preflight(raw: bytes) -> tuple[int, int]:
    _require(type(raw) is bytes and len(raw) <= MAX_ARCHIVE, "ARCHIVE_LIMIT")
    # Inspect classic EOCD before ZipFile allocates a list for every central-directory entry.
    # Deliberately reject ZIP64, multi-disk, trailing bytes and archive comments in this draft.
    _require(len(raw) >= 22 and raw[-22:-18] == b"PK\x05\x06", "ARCHIVE_SHAPE")
    disk, start, count_disk, count, size, offset, comment = struct.unpack("<4H2IH", raw[-18:])
    _require(disk == start == comment == 0 and count_disk == count, "ARCHIVE_SHAPE")
    _require(1 <= count <= MAX_ENTRIES, "ARCHIVE_LIMIT")
    _require(size <= 256 * MAX_ENTRIES, "ARCHIVE_LIMIT")
    _require(offset + size == len(raw) - 22, "ARCHIVE_SHAPE")
    return offset, count


def _local_layout(raw: bytes, entries: list[zipfile.ZipInfo], central_offset: int) -> None:
    """Reject unindexed local files, prefixes, gaps, suffixes and conflicting local headers.

    Central-directory-only inspection can hide unselected/private bytes elsewhere in ZIP.
    This memory-only draft deliberately does not accept streaming data descriptors/ZIP64.
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


def _read(raw: bytes, item: zipfile.ZipInfo, limit: int) -> bytes:
    _require(item.file_size <= limit, "ARCHIVE_LIMIT")
    start = item.header_offset + 30 + len(item.filename.encode("ascii"))
    compressed = raw[start : start + item.compress_size]
    if item.compress_type == zipfile.ZIP_STORED:
        _require(len(compressed) <= limit, "ARCHIVE_LIMIT")
        payload = compressed
    else:
        decoder = zlib.decompressobj(-15)
        payload = decoder.decompress(compressed, limit + 1)
        _require(len(payload) <= limit, "ARCHIVE_LIMIT")
        _require(
            decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,
            "ARCHIVE_INVALID",
        )
    _require(len(payload) == item.file_size, "ARCHIVE_INVALID")
    _require(zlib.crc32(payload) == item.CRC, "ARCHIVE_INVALID")
    return payload


def _inspect(
    archive: zipfile.ZipFile, raw: bytes, central_offset: int, declared_count: int
) -> Inspection:
    entries = archive.infolist()
    _require(1 <= len(entries) <= MAX_ENTRIES, "ARCHIVE_LIMIT")
    _require(len(entries) == declared_count, "ARCHIVE_SHAPE")
    seen = set()
    total = 0
    for item in entries:
        path = item.filename
        _require(item.orig_filename == path, "UNSAFE_PATH")
        _require(path == "manifest.json" or PATH.fullmatch(path) is not None, "UNSAFE_PATH")
        _require(path.split("/")[-1].split(".")[0] not in RESERVED, "UNSAFE_PATH")
        _require(path not in seen, "DUPLICATE_PATH")
        seen.add(path)
        mode = item.external_attr >> 16
        _require(stat.S_IFMT(mode) in {0, stat.S_IFREG}, "UNSAFE_ENTRY")
        _require(not item.flag_bits & 1, "UNSAFE_ENTRY")
        _require(item.compress_type in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}, "UNSAFE_ENTRY")
        _require(not item.extra and not item.comment, "UNSAFE_ENTRY")
        _require(item.file_size <= MAX_MEMBER, "ARCHIVE_LIMIT")
        total += item.file_size
    _require(total <= MAX_TOTAL, "ARCHIVE_LIMIT")
    _local_layout(raw, entries, central_offset)
    _require("manifest.json" in seen, "MANIFEST_MISSING")
    manifest = _strict(
        _json(_read(raw, archive.getinfo("manifest.json"), MAX_MANIFEST)),
        {"draftVersion", "kind", "options", "files"},
    )
    _require(manifest["draftVersion"] == DRAFT_VERSION, "FORMAT_UNSUPPORTED")
    _require(manifest["kind"] in ("template", "full"), "MANIFEST_SHAPE")
    options = _strict(manifest["options"], set(OPTION_ROLES))
    _require(all(type(v) is bool for v in options.values()), "MANIFEST_SHAPE")
    files = manifest["files"]
    _require(type(files) is list and len(files) < MAX_ENTRIES, "MANIFEST_SHAPE")
    listed, roles = set(), set()
    for value in files:
        record = _strict(value, {"path", "role", "size", "sha256"})
        path, role, size, digest = (record[k] for k in ("path", "role", "size", "sha256"))
        _require(type(path) is str and PATH.fullmatch(path) is not None, "UNSAFE_PATH")
        _require(type(role) is str and role in ROLES, "ROLE_UNSUPPORTED")
        _require(role not in roles, "DUPLICATE_ROLE")
        _require(path not in listed, "DUPLICATE_PATH")
        _require(type(size) is int and 0 <= size <= MAX_MEMBER, "MANIFEST_SHAPE")
        _require(type(digest) is str and SHA.fullmatch(digest) is not None, "MANIFEST_SHAPE")
        for option, optional_role in OPTION_ROLES.items():
            _require(role != optional_role or options[option], "UNSELECTED_CONTENT")
        listed.add(path)
        roles.add(role)
    _require(seen == listed | {"manifest.json"}, "UNLISTED_OR_MISSING_FILE")
    _require(manifest["kind"] != "full" or CORE_ROLES <= roles, "MISLABELED_FULL_PACKAGE")
    for record in files:
        payload = _read(raw, archive.getinfo(record["path"]), MAX_MEMBER)
        _require(len(payload) == record["size"], "SIZE_MISMATCH")
        _require(hashlib.sha256(payload).hexdigest() == record["sha256"], "HASH_MISMATCH")
    return Inspection(
        DRAFT_VERSION,
        manifest["kind"],
        tuple(sorted(roles)),
        tuple(sorted(k for k, v in options.items() if v)),
        tuple(sorted(k for k, role in OPTION_ROLES.items() if role in roles)),
    )


def inspect_candidate(raw: bytes) -> Inspection:
    """Read memory-only draft ZIP bytes. Never import or claim recovery from role names."""
    central_offset, declared_count = _preflight(raw)
    try:
        with zipfile.ZipFile(io.BytesIO(raw), "r") as archive:
            return _inspect(archive, raw, central_offset, declared_count)
    except TransferError:
        raise
    except (OSError, ValueError, RuntimeError, EOFError, zipfile.BadZipFile, zlib.error):
        raise TransferError("ARCHIVE_INVALID") from None
