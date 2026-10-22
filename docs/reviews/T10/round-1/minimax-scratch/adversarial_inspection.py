"""Reviewer-local independent counterexamples against the frozen candidate inspector.

Corrected EOCD offsets (from end of file):
  len-22 signature | len-20 disk | len-18 cd_start_disk | len-16 entries_this_disk
  len-14 (unused)  | len-12 entries_total | len-10 cd_size(4) | len-6 cd_offset(4) | len-2 comment
"""

import hashlib
import io
import json
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path("/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-c3c7e90")
sys.path.insert(0, str(ROOT / "packages/engine/src"))

from ontolearn_engine.transfer import TransferError, inspect_candidate  # noqa: E402
from ontolearn_engine.transfer.inspection import DRAFT_VERSION, OPTION_ROLES  # noqa: E402

RESULTS = []


def manifest_for(names_roles, kind="template", options=None):
    files = []
    for name, role in names_roles:
        files.append({"path": name, "role": role, "size": 0, "sha256": None})
    return {
        "draftVersion": DRAFT_VERSION,
        "kind": kind,
        "options": options or dict.fromkeys(OPTION_ROLES, False),
        "files": files,
    }


def build(entries, kind="template", options=None, roles=None, extra=()):
    """entries: list of (name, bytes) that the manifest may declare."""
    data = {name: payload for name, payload in entries}
    files = []
    for name, _ in entries:
        role = (roles or {}).get(name)
        if role:
            files.append(
                {
                    "path": name,
                    "role": role,
                    "size": len(data[name]),
                    "sha256": hashlib.sha256(data[name]).hexdigest(),
                }
            )
    manifest = {
        "draftVersion": DRAFT_VERSION,
        "kind": kind,
        "options": options or dict.fromkeys(OPTION_ROLES, False),
        "files": files,
    }
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        for name, payload in entries:
            archive.writestr(name, payload)
        for name, payload in extra:
            archive.writestr(name, payload)
    return stream.getvalue()


def probe(name, raw, expect_reject=True):
    try:
        result = inspect_candidate(raw)
        outcome = f"ACCEPTED kind={result.declared_kind} roles={result.roles}"
        rejected = False
    except TransferError as error:
        result = None
        outcome = f"REJECTED {error}"
        rejected = True
    except Exception as error:  # noqa: BLE001
        result = None
        outcome = f"UNEXPECTED {type(error).__name__}: {error}"
        rejected = None
    if expect_reject:
        status = "OK-REJECTED" if rejected is True else ("!!-ACCEPTED" if rejected is False else "!!-CRASH")
    else:
        status = "OK-ACCEPTED" if rejected is False else ("!!-REJECTED" if rejected is True else "!!-CRASH")
    RESULTS.append((status, name, outcome))
    print(f"[{status:>12}] {name}: {outcome}")
    return result


DEF = {"data/definitions.json": "definitions"}
base = build([("data/definitions.json", b"{}")], roles=DEF)

print("=" * 78)
print("A. EOCD / central-directory count consistency")
print("=" * 78)

for label, count in [("A1 entries_total understated", 1), ("A2 entries_total overstated", 3)]:
    raw = bytearray(base)
    struct.pack_into("<H", raw, len(raw) - 12, count)
    struct.pack_into("<H", raw, len(raw) - 14, count)
    probe(label, bytes(raw))

raw = bytearray(base)
struct.pack_into("<H", raw, len(raw) - 12, 0xFFFF)
struct.pack_into("<H", raw, len(raw) - 14, 0xFFFF)
probe("A3 zip64 entries marker 0xFFFF", bytes(raw))

raw = bytearray(base)
struct.pack_into("<H", raw, len(raw) - 12, 0)
struct.pack_into("<H", raw, len(raw) - 14, 0)
probe("A4 entries_total zero", bytes(raw))

print()
print("=" * 78)
print("B. Filename normalisation (length preserving)")
print("=" * 78)

# B1: NUL padding after a still-valid name (length preserving on the real member name).
raw = bytearray(base)
raw = bytes(raw).replace(b"data/definitions.json", b"data/definitions.jsonXXXXX")
raw = raw.replace(b"data/definitions.jsonXXXXX", b"data/definitions.json\x00\x00\x00\x00\x00")
probe("B1 embedded NUL after a fully valid name", raw)

# B2: backslash separator, same length as the original member name.
raw = bytearray(base)
raw = bytes(raw).replace(b"data/definitions.json", b"data\\definitions.json")
probe("B2 backslash separator", raw)

# B3: absolute path (same length).
raw = bytearray(base)
raw = bytes(raw).replace(b"data/definitions.json", b"/ata/definitions.json")
probe("B3 absolute path", raw)

# B4: uppercase reserved device name, length preserving via a distinct member.
raw = build([("data/CON.json", b"{}")], roles={"data/CON.json": "definitions"})
probe("B4 uppercase CON.json (Windows device names are case-insensitive)", raw)

# B5: '..' segment in the name.
raw = build([("data/../x.json", b"{}")], extra=[("data/../x.json", b"{}")])
probe("B5 traversal segment data/../x.json", raw)

# B6: name that is exactly the reserved stem plus a different extension.
raw = build([("data/nul.bin", b"x")], roles={"data/nul.bin": "definitions"})
probe("B6 data/nul.bin (reserved stem, .bin extension)", raw)

print()
print("=" * 78)
print("C. Structural / resource attacks")
print("=" * 78)

probe("C1 control: valid single-role template", base, expect_reject=False)

bomb = b"0" * (9 * 1024 * 1024)
raw = build([("data/definitions.json", bomb)], roles=DEF)
probe("C2 9MB deflate member vs MAX_MEMBER 8MB", raw)

# C3: central record whose local-header offset points at another member.
stream = io.BytesIO()
with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("manifest.json", json.dumps({"draftVersion": DRAFT_VERSION, "kind": "template",
                                                  "options": dict.fromkeys(OPTION_ROLES, False), "files": []}))
    archive.writestr("data/definitions.json", b"{}")
    archive.writestr("data/second.json", b"{}")
raw = bytearray(stream.getvalue())
central = struct.unpack_from("<I", raw, len(raw) - 6)[0]
pos = central
while raw[pos : pos + 4] == b"PK\x01\x02":
    name_len, extra_len, comment_len = struct.unpack_from("<3H", raw, pos + 28)
    name = bytes(raw[pos + 46 : pos + 46 + name_len])
    if name == b"data/second.json":
        struct.pack_into("<I", raw, pos + 42, struct.unpack_from("<I", raw, pos + 42)[0] - 0)
        break
    pos += 46 + name_len + extra_len + comment_len
probe("C3 second member shares the first member's local header", bytes(raw))

# C4: unindexed hidden local member spliced before the central directory.
hidden = io.BytesIO()
with zipfile.ZipFile(hidden, "w", zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("data/agent-session.json", b"hidden-session")
hidden_raw = hidden.getvalue()
hidden_local = hidden_raw[: struct.unpack_from("<I", hidden_raw, len(hidden_raw) - 6)[0]]
raw = bytearray(base)
central = struct.unpack_from("<I", raw, len(raw) - 6)[0]
raw = raw[:central] + hidden_local + raw[central:]
struct.pack_into("<I", raw, 18, struct.unpack_from("<I", raw, 18)[0] + len(hidden_local))
for pos in range(central, len(raw) - 22):
    if raw[pos : pos + 4] == b"PK\x01\x02":
        struct.pack_into("<I", raw, pos + 42, struct.unpack_from("<I", raw, pos + 42)[0] + len(hidden_local))
        break
struct.pack_into("<I", raw, len(raw) - 6, central + len(hidden_local))
probe("C4 unindexed hidden local member", bytes(raw))

# C5: a member declared in the manifest but stored with different bytes on disk.
manifest = {
    "draftVersion": DRAFT_VERSION,
    "kind": "template",
    "options": dict.fromkeys(OPTION_ROLES, False),
    "files": [{"path": "data/definitions.json", "role": "definitions", "size": 2,
               "sha256": hashlib.sha256(b"{}").hexdigest()}],
}
stream = io.BytesIO()
with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("manifest.json", json.dumps(manifest))
    archive.writestr("data/definitions.json", b"{}")
raw = bytearray(stream.getvalue())
probe("C5 control", bytes(raw), expect_reject=False)

print()
print("=" * 78)
print("D. Manifest semantics")
print("=" * 78)

raw = build([("data/definitions.json", b"{}")], kind="full", roles=DEF)
probe("D1 kind=full missing core roles", raw)

core = ("assertions", "checkpoint", "definitions", "ownership")
entries = [(f"data/{role}.json", b"{}") for role in core]
roles = {name: name[5:-5] for name, _ in entries}
raw = build(entries, kind="template", roles=roles)
probe("D2 kind=template while all four core roles are present", raw, expect_reject=False)

raw = build(entries, kind="full", roles=roles)
probe("D3 kind=full, all core roles, no optional content", raw, expect_reject=False)

raw = build(entries, kind="full", options=dict.fromkeys(OPTION_ROLES, True), roles=roles)
probe("D4 kind=full, options all true, no optional member present", raw, expect_reject=False)

# D5: manifest declares an optional role but the option flag is false.
raw = build([("data/agent-session.json", b"x")], roles={"data/agent-session.json": "agent-session"})
probe("D5 optional member present with its option flag false", raw)

print()
print("=" * 78)
print("SUMMARY")
print("=" * 78)
for status, name, outcome in RESULTS:
    print(f"{status:>12}  {name}: {outcome}")
print()
print("unexpected outcomes:", sum(1 for s, _, _ in RESULTS if s.startswith("!!")))
