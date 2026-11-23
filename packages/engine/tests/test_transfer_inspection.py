"""Synthetic draft envelopes only. Not Store migration or cross-device acceptance."""

import dataclasses
import hashlib
import io
import json
import stat
import struct
import warnings
import zipfile
import zlib
from pathlib import Path

import pytest
from ontolearn_engine.transfer import TransferError, inspect_candidate
from ontolearn_engine.transfer.inspection import (
    CORE_ROLES,
    DRAFT_VERSION,
    MAX_ARCHIVE,
    MAX_ENTRIES,
    MAX_MANIFEST,
    MAX_MEMBER,
    MAX_TOTAL,
    OPTION_ROLES,
)

FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "transfer"


def manifest(roles=("definitions",), kind="template", options=None):
    data = {f"data/{role}.json": b"{}" for role in roles}
    return {
        "draftVersion": DRAFT_VERSION,
        "kind": kind,
        "options": options or dict.fromkeys(OPTION_ROLES, False),
        "files": [
            {
                "path": path,
                "role": role,
                "size": len(data[path]),
                "sha256": hashlib.sha256(data[path]).hexdigest(),
            }
            for role, path in zip(roles, data, strict=True)
        ],
    }, data


def pack(m=None, data=None, raw_manifest=None, entries=(), compression=zipfile.ZIP_DEFLATED):
    if m is None:
        m, data = manifest()
    stream = io.BytesIO()
    with warnings.catch_warnings(), zipfile.ZipFile(stream, "w", compression) as z:
        warnings.simplefilter("ignore", UserWarning)
        z.writestr("manifest.json", raw_manifest or json.dumps(m))
        for path, value in (data or {}).items():
            z.writestr(path, value)
        for path, value in entries:
            if isinstance(path, str) and "\\" in path:
                info = zipfile.ZipInfo(path)
                info.filename = path
                z.writestr(info, value)
            else:
                z.writestr(path, value)
    return stream.getvalue()


def rejected(raw, code):
    with pytest.raises(TransferError, match=f"^{code}$"):
        inspect_candidate(raw)


def test_complete_expected_read_only_template(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    before = set(tmp_path.iterdir())
    result = inspect_candidate(pack())
    expected = json.loads((FIXTURES / "inspection-expected.json").read_text(encoding="utf-8"))
    assert dataclasses.asdict(result) == {
        **expected,
        "roles": tuple(expected["roles"]),
        "selected_options": (),
        "included_options": (),
    }
    assert set(tmp_path.iterdir()) == before  # No extraction or project write.
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.import_allowed = True


def test_claimed_full_is_not_a_proof_of_semantics():
    m, data = manifest(tuple(sorted(CORE_ROLES)), "full")
    result = inspect_candidate(pack(m, data))
    assert result.declared_kind == "full"
    assert result.roles == tuple(sorted(CORE_ROLES))
    assert not any(
        [result.restore_current, result.rerun_mapping, result.replay_runs, result.import_allowed]
    )
    assert result.reason == "UNAPPROVED_FORMAT_AND_UNVERIFIED_PAYLOADS"


def test_full_without_optional_source_history_sessions_or_derived_is_not_template():
    m, data = manifest(tuple(sorted(CORE_ROLES)), "full")
    result = inspect_candidate(pack(m, data))
    assert result.declared_kind == "full"
    assert result.included_options == result.selected_options == ()
    assert not result.rerun_mapping
    assert not result.replay_runs


@pytest.mark.parametrize("missing", sorted(CORE_ROLES))
def test_full_missing_any_core_role(missing):
    m, data = manifest(tuple(sorted(CORE_ROLES - {missing})), "full")
    rejected(pack(m, data), "MISLABELED_FULL_PACKAGE")


@pytest.mark.parametrize("option,role", OPTION_ROLES.items())
def test_selected_and_unselected_content(option, role):
    options = dict.fromkeys(OPTION_ROLES, False)
    m, data = manifest((role,), options=options)
    rejected(pack(m, data), "UNSELECTED_CONTENT")
    m["options"][option] = True
    result = inspect_candidate(pack(m, data))
    assert result.selected_options == (option,)
    assert result.included_options == (option,)
    assert not result.import_allowed


def test_selected_missing_file_is_distinct_from_actual_scope():
    m, data = manifest()
    m["options"]["rawSources"] = True
    result = inspect_candidate(pack(m, data))
    assert result.selected_options == ("rawSources",)
    assert result.included_options == ()
    assert not result.rerun_mapping


@pytest.mark.parametrize(
    "path",
    [
        "../outside",
        "/etc/passwd",
        "C:/private",
        "data/../vault.json",
        "data\\vault.json",
        "data/%2e%2e.json",
        "data/UPPER.json",
        "data/a:b.json",
        "data/设备.json",
        "data/.env",
        "data/foo.json/",
        "data/con.json ",
        "data/con.json",
        "data/lpt1.bin",
    ],
)
def test_unsafe_paths(path):
    rejected(pack(entries=[(path, b"secret")]), "UNSAFE_PATH")


def test_duplicates_unlisted_missing_and_role_alias():
    rejected(pack(entries=[("manifest.json", b"{}")]), "DUPLICATE_PATH")
    rejected(pack(entries=[("data/unlisted.json", b"{}")]), "UNLISTED_OR_MISSING_FILE")
    m, data = manifest()
    rejected(pack(m, {}), "UNLISTED_OR_MISSING_FILE")
    m["files"].append({**m["files"][0], "path": "data/alias.json"})
    rejected(pack(m, {**data, "data/alias.json": b"{}"}), "DUPLICATE_ROLE")


def test_real_embedded_nul_path_rejected():
    # ZipFile.writestr truncates NUL in source names, so mutate the actual wire bytes.
    raw = pack(entries=[("data/null.json", b"{}")])
    raw = raw.replace(b"data/null.json", b"data/nu\x00l.json")
    rejected(raw, "UNSAFE_PATH")


@pytest.mark.parametrize("role", ["vault", "credentials", "audit", "authorization", "unknown"])
def test_private_and_unknown_roles_rejected(role):
    m, data = manifest()
    m["files"][0]["role"] = role
    rejected(pack(m, data), "ROLE_UNSUPPORTED")


@pytest.mark.parametrize("version", [2, 3, "3", "t10-envelope-draft-2", None, {}])
def test_versions_not_implicitly_migrated(version):
    m, data = manifest()
    m["draftVersion"] = version
    rejected(pack(m, data), "FORMAT_UNSUPPORTED")


@pytest.mark.parametrize("mutation", ["unknown", "option-int", "file-extra", "size-bool", "hash"])
def test_strict_shapes(mutation):
    m, data = manifest()
    if mutation == "unknown":
        m["apiKey"] = "synthetic-secret-never-returned"
    elif mutation == "option-int":
        m["options"]["agentSessions"] = 1
    elif mutation == "file-extra":
        m["files"][0]["password"] = "synthetic-secret-never-returned"
    elif mutation == "size-bool":
        m["files"][0]["size"] = True
    else:
        m["files"][0]["sha256"] = "A" * 64
    rejected(pack(m, data), "MANIFEST_SHAPE")


@pytest.mark.parametrize("raw", ['{"kind":1,"kind":2}', "[1]", "NaN", "{", '"secret"'])
def test_manifest_invalid_json_or_duplicate(raw):
    code = "MANIFEST_DUPLICATE_KEY" if raw.startswith('{"kind"') else "MANIFEST_SHAPE"
    rejected(pack(raw_manifest=raw), code)


def test_hash_size_and_crc_failures_are_safe():
    m, data = manifest()
    m["files"][0]["sha256"] = "0" * 64
    rejected(pack(m, data), "HASH_MISMATCH")
    m, data = manifest()
    m["files"][0]["size"] = 3
    rejected(pack(m, data), "SIZE_MISMATCH")
    raw = bytearray(pack())
    offset = raw.find(b"PK\x01\x02")
    raw[offset + 16] ^= 1
    rejected(bytes(raw), "ARCHIVE_INVALID")


def test_symlink_and_directory_not_extracted():
    for mode in [stat.S_IFLNK | 0o777, stat.S_IFDIR | 0o755]:
        info = zipfile.ZipInfo("data/link.json")
        info.create_system = 3
        info.external_attr = mode << 16
        rejected(pack(entries=[(info, b"../../private")]), "UNSAFE_ENTRY")


def test_limits_on_archive_members_directory_and_manifest():
    rejected(b"x" * (MAX_ARCHIVE + 1), "ARCHIVE_LIMIT")
    rejected(pack(entries=[("data/large.bin", b"0" * (MAX_MEMBER + 1))]), "ARCHIVE_LIMIT")
    rejected(pack(raw_manifest=" " * (MAX_MANIFEST + 1)), "ARCHIVE_LIMIT")
    raw = bytearray(pack())
    struct.pack_into("<H", raw, len(raw) - 12, MAX_ENTRIES + 1)
    struct.pack_into("<H", raw, len(raw) - 14, MAX_ENTRIES + 1)
    rejected(bytes(raw), "ARCHIVE_LIMIT")
    entries = [(f"data/large{i}.bin", b"0" * MAX_MEMBER) for i in range(MAX_TOTAL // MAX_MEMBER)]
    rejected(pack(entries=entries), "ARCHIVE_LIMIT")


@pytest.mark.parametrize("raw", [b"", b"not a zip", b"PK\x05\x06" + b"\x00" * 18])
def test_malformed_archive(raw):
    rejected(raw, "ARCHIVE_SHAPE" if len(raw) < 22 else "ARCHIVE_LIMIT")


def test_trailing_bytes_and_comment_rejected():
    rejected(pack() + b"secret", "ARCHIVE_SHAPE")
    raw = bytearray(pack())
    raw[-2:] = b"\x01\x00"
    rejected(bytes(raw), "ARCHIVE_SHAPE")


@pytest.mark.parametrize("declared_count", [1, 3])
def test_eocd_count_must_match_actual_central_directory_members(declared_count):
    raw = bytearray(pack())  # Exactly manifest.json and data/definitions.json.
    struct.pack_into("<HH", raw, len(raw) - 14, declared_count, declared_count)
    rejected(bytes(raw), "ARCHIVE_SHAPE")


@pytest.mark.parametrize("disk_count,total_count", [(1, 2), (2, 1)])
def test_eocd_disk_count_must_match_total_count(disk_count, total_count):
    raw = bytearray(pack())
    struct.pack_into("<HH", raw, len(raw) - 14, disk_count, total_count)
    rejected(bytes(raw), "ARCHIVE_SHAPE")


@pytest.mark.parametrize("compression", [zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED])
def test_matching_eocd_counts_preserve_full_without_optional_content(compression):
    m, data = manifest(tuple(sorted(CORE_ROLES)), "full")
    result = inspect_candidate(pack(m, data, compression=compression))
    assert result.declared_kind == "full"
    assert result.roles == tuple(sorted(CORE_ROLES))
    assert result.selected_options == result.included_options == ()
    assert not any(
        [result.restore_current, result.rerun_mapping, result.replay_runs, result.import_allowed]
    )


def prepend_unindexed(raw, prefix):
    # Make an otherwise valid central directory point past arbitrary unindexed bytes.
    changed = bytearray(prefix + raw)
    central = struct.unpack_from("<I", raw, len(raw) - 6)[0]
    position = len(prefix) + central
    while changed[position : position + 4] == b"PK\x01\x02":
        old = struct.unpack_from("<I", changed, position + 42)[0]
        struct.pack_into("<I", changed, position + 42, old + len(prefix))
        name, extra, comment = struct.unpack_from("<3H", changed, position + 28)
        position += 46 + name + extra + comment
    struct.pack_into("<I", changed, len(changed) - 6, central + len(prefix))
    return bytes(changed)


def test_unindexed_private_bytes_and_members_are_rejected():
    rejected(prepend_unindexed(pack(), b"synthetic-unselected-private-data"), "ARCHIVE_LAYOUT")
    unselected = io.BytesIO()
    with zipfile.ZipFile(unselected, "w") as archive:
        archive.writestr("data/agent-session.json", b"synthetic-unselected-session")
    raw = unselected.getvalue()
    local_only = raw[: struct.unpack_from("<I", raw, len(raw) - 6)[0]]
    rejected(prepend_unindexed(pack(), local_only), "ARCHIVE_LAYOUT")


def test_conflicting_local_headers_encryption_and_streaming_are_rejected():
    for flag in [1, 8]:
        raw = bytearray(pack())
        central = raw.find(b"PK\x01\x02")
        struct.pack_into("<H", raw, 6, flag)
        struct.pack_into("<H", raw, central + 8, flag)
        rejected(bytes(raw), "UNSAFE_ENTRY")
    raw = bytearray(pack())
    raw[30] = ord("x")
    rejected(bytes(raw), "ARCHIVE_INVALID")


def test_hidden_deflate_trailer_rejected():
    m, _ = manifest(())
    raw = bytearray(pack(m, {}))
    central = struct.unpack_from("<I", raw, len(raw) - 6)[0]
    hidden = b"synthetic-unselected-session"
    changed = raw[:central] + hidden + raw[central:]
    packed = struct.unpack_from("<I", raw, 18)[0] + len(hidden)
    struct.pack_into("<I", changed, 18, packed)
    struct.pack_into("<I", changed, central + len(hidden) + 20, packed)
    struct.pack_into("<I", changed, len(changed) - 6, central + len(hidden))
    rejected(bytes(changed), "ARCHIVE_INVALID")


def test_actual_decompression_cannot_be_truncated_to_declared_prefix():
    m, data = manifest()
    data["data/definitions.json"] = b"{}synthetic-unselected-private-data"
    raw = bytearray(pack(m, data))
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entry = archive.getinfo("data/definitions.json")
    central = struct.unpack_from("<I", raw, len(raw) - 6)[0]
    while raw[central : central + 4] == b"PK\x01\x02":
        name, extra, comment = struct.unpack_from("<3H", raw, central + 28)
        if raw[central + 46 : central + 46 + name] == b"data/definitions.json":
            struct.pack_into("<I", raw, central + 16, zlib.crc32(b"{}"))
            struct.pack_into("<I", raw, central + 24, 2)
            break
        central += 46 + name + extra + comment
    struct.pack_into("<I", raw, entry.header_offset + 14, zlib.crc32(b"{}"))
    struct.pack_into("<I", raw, entry.header_offset + 22, 2)
    rejected(bytes(raw), "ARCHIVE_INVALID")
