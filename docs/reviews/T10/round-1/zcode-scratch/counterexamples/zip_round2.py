# Round 2: corrected counterexample constructions.
import hashlib
import io
import json
import struct
import sys
import zipfile
import zlib

sys.path.insert(0, "packages/engine/src")
from ontolearn_engine.transfer import TransferError, inspect_candidate  # noqa: E402
from ontolearn_engine.transfer.inspection import DRAFT_VERSION, OPTION_ROLES  # noqa: E402

RESULTS = []


def base_manifest(roles=("definitions",), kind="template", options=None):
    data = {f"data/{role}.json": b"{}" for role in roles}
    return {
        "draftVersion": DRAFT_VERSION,
        "kind": kind,
        "options": options or dict.fromkeys(OPTION_ROLES, False),
        "files": [
            {
                "path": p,
                "role": r,
                "size": len(data[p]),
                "sha256": hashlib.sha256(data[p]).hexdigest(),
            }
            for r, p in zip(roles, data, strict=True)
        ],
    }, data


def pack(m=None, data=None):
    if m is None:
        m, data = base_manifest()
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(m))
        for p, v in (data or {}).items():
            z.writestr(p, v)
    return stream.getvalue()


def expect(name, raw, code=None):
    try:
        result = inspect_candidate(raw)
        RESULTS.append((name, "ACCEPTED", result.declared_kind))
    except TransferError as exc:
        RESULTS.append((name, "REJECTED", str(exc)))
        if code is not None and str(exc) != code:
            RESULTS.append((name + "!!UNEXPECTED", "CODE-MISMATCH", f"got {exc} want {code}"))
    except Exception as exc:  # noqa: BLE001
        RESULTS.append((name, "LEAKED", f"{type(exc).__name__}: {exc}"))


# 1. EOCD count lied downward (0 declared... must be >=1; use 1 with 2 actual entries)
raw = bytearray(pack())
struct.pack_into("<H", raw, len(raw) - 14, 1)  # entries on this disk
struct.pack_into("<H", raw, len(raw) - 12, 1)  # total entries
expect("eocd-count-smaller-than-actual", bytes(raw))

# 2. Real deflate trailer: hand-built member, stream ends early, rest is payload bytes
payload = b"{}" * 32
comp = zlib.compressobj(9, zlib.DEFLATED, -15)
stream_bytes = comp.compress(payload) + comp.flush()
trailer = zlib.compressobj(9, zlib.DEFLATED, -15).compress(b"hidden-tail") + zlib.compressobj(
    9, zlib.DEFLATED, -15
).flush()
blob = stream_bytes + trailer
crc = zlib.crc32(payload)
mf, _ = base_manifest()
manual = io.BytesIO()
name = b"data/definitions.json"
lh = struct.pack(
    "<4s5H3I2H", b"PK\x03\x04", 20, 0, 8, 0, 0, crc, len(blob), len(payload), len(name), 0
)
manual.write(lh + name + blob)
central_off = manual.tell()
ch = struct.pack(
    "<4s6H3I5H2I", b"PK\x01\x02", 20, 20, 0, 8, 0, 0, crc, len(blob), len(payload),
    len(name), 0, 0, 0, 0, 0o100600, 0,
)
manual.write(ch + name)
central_size = manual.tell() - central_off
manual.write(struct.pack("<4s4H2IH", b"PK\x05\x06", 0, 0, 1, 1, central_size, central_off, 0))
expect("hand-built-deflate-trailer", manual.getvalue(), "ARCHIVE_INVALID")

# 3. Same hand-built archive without trailer must be ACCEPTED (control)
blob_ok = stream_bytes
manual = io.BytesIO()
lh = struct.pack(
    "<4s5H3I2H", b"PK\x03\x04", 20, 0, 8, 0, 0, crc, len(blob_ok), len(payload), len(name), 0
)
manual.write(lh + name + blob_ok)
central_off = manual.tell()
ch = struct.pack(
    "<4s6H3I5H2I", b"PK\x01\x02", 20, 20, 0, 8, 0, 0, crc, len(blob_ok), len(payload),
    len(name), 0, 0, 0, 0, 0o100600, 0,
)
manual.write(ch + name)
central_size = manual.tell() - central_off
manual.write(struct.pack("<4s4H2IH", b"PK\x05\x06", 0, 0, 1, 1, central_size, central_off, 0))
expect("hand-built-control-accepted", manual.getvalue())

# 4. data/manifest.json as a clean role member (fresh manifest, no leftovers)
mf2 = {
    "draftVersion": DRAFT_VERSION,
    "kind": "template",
    "options": dict.fromkeys(OPTION_ROLES, False),
    "files": [
        {
            "path": "data/definitions.json",
            "role": "definitions",
            "size": 2,
            "sha256": hashlib.sha256(b"{}").hexdigest(),
        }
    ],
}
data2 = {"data/definitions.json": b"{}"}
expect("clean-template", pack(mf2, data2))
mf2["files"].append(
    {
        "path": "data/manifest.json",
        "role": "assertions",
        "size": 2,
        "sha256": hashlib.sha256(b"{}").hexdigest(),
    }
)
data2["data/manifest.json"] = b"{}"
expect("data-manifest-json-role-member", pack(mf2, data2))

# 5. exact total budget: 3 x 8MB + definitions 2B + manifest — just under 32MB
big = b"0" * (8 * 1024 * 1024)
roles = ["definitions"] + ["raw-source"] * 3
mf3 = {
    "draftVersion": DRAFT_VERSION,
    "kind": "template",
    "options": {**dict.fromkeys(OPTION_ROLES, False), "rawSources": True},
    "files": [
        {
            "path": "data/definitions.json",
            "role": "definitions",
            "size": 2,
            "sha256": hashlib.sha256(b"{}").hexdigest(),
        }
    ]
    + [
        {
            "path": f"data/raw{i}.json",
            "role": "raw-source",
            "size": len(big),
            "sha256": hashlib.sha256(big).hexdigest(),
        }
        for i in range(3)
    ],
}
data3 = {"data/definitions.json": b"{}"}
for i in range(3):
    data3[f"data/raw{i}.json"] = big
expect("total-just-under-32mb", pack(mf3, data3))

print(f"{'CASE':40} {'OUTCOME':10} CODE/KIND")
for row in RESULTS:
    print(f"{row[0]:40} {row[1]:10} {row[2]}")
