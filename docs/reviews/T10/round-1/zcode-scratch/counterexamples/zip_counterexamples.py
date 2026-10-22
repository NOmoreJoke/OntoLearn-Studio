# Independent T10 review counterexamples — NOT part of the product test suite.
# Runs against the frozen inspection.py via the tree's own venv.
import hashlib
import io
import json
import struct
import sys
import zipfile
import zlib

sys.path.insert(0, "packages/engine/src")
from ontolearn_engine.transfer import TransferError, inspect_candidate  # noqa: E402
from ontolearn_engine.transfer.inspection import (  # noqa: E402
    CORE_ROLES,
    DRAFT_VERSION,
    OPTION_ROLES,
)

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


def pack(m=None, data=None, raw_manifest=None, entries=(), compression=zipfile.ZIP_DEFLATED):
    if m is None:
        m, data = base_manifest()
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression) as z:
        z.writestr("manifest.json", raw_manifest if raw_manifest is not None else json.dumps(m))
        for p, v in (data or {}).items():
            z.writestr(p, v)
        for p, v in entries:
            z.writestr(p, v)
    return stream.getvalue()


def expect(name, raw, code=None):
    try:
        result = inspect_candidate(raw)
        RESULTS.append((name, "ACCEPTED", result.declared_kind, result.roles))
        return result
    except TransferError as exc:
        RESULTS.append((name, "REJECTED", str(exc), None))
        if code is not None and str(exc) != code:
            RESULTS.append((name + "!!UNEXPECTED-CODE", str(exc), f"expected {code}", None))
        return None
    except Exception as exc:  # noqa: BLE001 — reviewer must see any leaked exception type
        RESULTS.append((name, "LEAKED-EXCEPTION", type(exc).__name__, str(exc)[:120]))
        return None


# --- Independent cases beyond the shipped suite -------------------------
# 1. eocd count field lies downward (2 declared, 1 actual entry present)
raw = bytearray(pack())
struct.pack_into("<H", raw, len(raw) - 10, 2)  # count on this disk
struct.pack_into("<H", raw, len(raw) - 8, 2)  # total count
expect("eocd-count-larger-than-actual", bytes(raw))

# 2. ZIP64 EOCD locator appended after EOCD
expect("zip64-locator-appended", pack() + b"PK\x06\x07" + b"\x00" * 16 + b"PK\x05\x06" + b"\x00" * 18)

# 3. 81-char member name
m, data = base_manifest()
long_name = "data/" + "a" * 81 + ".json"
m["files"][0]["path"] = long_name
data = {long_name: b"{}"}
expect("name-81-chars", pack(m, data))

# 4. uppercase extension
expect("uppercase-extension", pack(entries=[("data/x.JSON", b"{}")]))

# 5. template with zero roles (empty files list)
m, data = base_manifest(())
expect("template-empty-files", pack(m, {}))

# 6. BOM in manifest
expect("manifest-bom", pack(raw_manifest="﻿" + json.dumps(base_manifest()[0])))

# 7. deflate stream with concatenated second member inside declared size
payload = b"{}" * 10
first = zlib.compressobj(9, zlib.DEFLATED, -15)
blob = first.compress(payload) + first.flush()
second = zlib.compressobj(9, zlib.DEFLATED, -15)
blob += second.compress(b"hidden") + second.flush()
stream = io.BytesIO()
with zipfile.ZipFile(stream, "w", zipfile.ZIP_STORED) as z:
    z.writestr("manifest.json", json.dumps(base_manifest()[0]))
    info = zipfile.ZipInfo("data/definitions.json")
    info.compress_type = zipfile.ZIP_DEFLATED
    info.file_size = len(payload)
    info.CRC = zlib.crc32(payload)
    z.writestr(info, blob)
expect("deflate-concatenated-stream", stream.getvalue())

# 8. STORED with compress_size < file_size (declared mismatch)
stream = io.BytesIO()
with zipfile.ZipFile(stream, "w", zipfile.ZIP_STORED) as z:
    z.writestr("manifest.json", json.dumps(base_manifest()[0]))
expect("store-baseline", stream.getvalue())

# 9. role listed for path present twice in files with different roles/paths
m, data = base_manifest(("definitions", "assertions"))
m["files"][1]["path"] = m["files"][0]["path"]
expect("two-roles-one-path", pack(m, data))

# 10. valid large package at budget boundary (4 x 8MB stored)
big = b"0" * (8 * 1024 * 1024)
m = {
    "draftVersion": DRAFT_VERSION,
    "kind": "template",
    "options": dict.fromkeys(OPTION_ROLES, False),
    "files": [
        {
            "path": f"data/big{i}.json",
            "role": "definitions" if i == 0 else "raw-source",
            "size": len(big),
            "sha256": hashlib.sha256(big).hexdigest(),
        }
        for i in range(4)
    ],
}
m["options"]["rawSources"] = True
stream = io.BytesIO()
with zipfile.ZipFile(stream, "w", zipfile.ZIP_STORED) as z:
    z.writestr("manifest.json", json.dumps(m))
    for i in range(4):
        z.writestr(f"data/big{i}.json", big)
expect("budget-boundary-32mb-accepted", stream.getvalue())

# 11. one byte over total budget
small = [zlib.crc32(b"")]
m2 = json.loads(json.dumps(m))
extra = {
    "path": "data/big4.json",
    "role": "history",
    "size": 1,
    "sha256": hashlib.sha256(b"x").hexdigest(),
}
m2["files"].append(extra)
m2["options"]["history"] = True
stream = io.BytesIO()
with zipfile.ZipFile(stream, "w", zipfile.ZIP_STORED) as z:
    z.writestr("manifest.json", json.dumps(m2))
    for i in range(4):
        z.writestr(f"data/big{i}.json", big)
    z.writestr("data/big4.json", b"x")
expect("budget-over-32mb-rejected", stream.getvalue(), "ARCHIVE_LIMIT")

# 12. garbage inside declared central region
raw = bytearray(pack())
central = struct.unpack_from("<I", raw, len(raw) - 6)[0]
raw[central + 10] = 0xEE
expect("central-region-garbage", bytes(raw))

# 13. full package where a core role path exists but hash field wrong case
m, data = base_manifest(tuple(sorted(CORE_ROLES)), "full")
m["files"][0]["sha256"] = m["files"][0]["sha256"].upper()
expect("uppercase-hash-rejected", pack(m, data))

# 14. duplicate key inside a file record via raw JSON
m, data = base_manifest()
raw_manifest = json.dumps(m)[:-2] + ', "path":"data/definitions.json"}'
expect("record-duplicate-path-key", pack(raw_manifest=raw_manifest))

# 15. manifest.json listed as a data/ member with a role (data/manifest.json)
m, data = base_manifest(("definitions", "assertions"))
m["files"][1] = {
    "path": "data/manifest.json",
    "role": "assertions",
    "size": 2,
    "sha256": hashlib.sha256(b"{}").hexdigest(),
}
data["data/manifest.json"] = b"{}"
expect("data-manifest-role-member", pack(m, data))

print(f"{'CASE':38} {'OUTCOME':10} CODE/KIND")
for name, outcome, detail, _ in RESULTS:
    print(f"{name:38} {outcome:10} {detail}")
