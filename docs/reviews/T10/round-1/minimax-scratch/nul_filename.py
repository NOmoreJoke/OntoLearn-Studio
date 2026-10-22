"""Reviewer-local: correct, length-preserving NUL-in-filename construction.

Builds the archive with zipfile so every offset/size is already correct, then swaps
only the placeholder bytes for NULs (same length => no structural drift).
"""

import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path("/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-c3c7e90")
sys.path.insert(0, str(ROOT / "packages/engine/src"))

from ontolearn_engine.transfer import TransferError, inspect_candidate  # noqa: E402
from ontolearn_engine.transfer.inspection import DRAFT_VERSION, OPTION_ROLES  # noqa: E402

PLACEHOLDER = b"data/definitions.jsonXXXXX"   # 24 bytes
PAYLOAD = b"{}"

manifest = {
    "draftVersion": DRAFT_VERSION,
    "kind": "template",
    "options": dict.fromkeys(OPTION_ROLES, False),
    "files": [
        {
            "path": "data/definitions.json",
            "role": "definitions",
            "size": len(PAYLOAD),
            "sha256": hashlib.sha256(PAYLOAD).hexdigest(),
        }
    ],
}

stream = io.BytesIO()
with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("manifest.json", json.dumps(manifest))
    archive.writestr(PLACEHOLDER.decode("ascii"), PAYLOAD)
raw = stream.getvalue()

assert raw.count(PLACEHOLDER) == 2, raw.count(PLACEHOLDER)
patched = raw.replace(PLACEHOLDER, b"data/definitions.json\x00\x00\x00\x00\x00")
assert len(patched) == len(raw)

with zipfile.ZipFile(io.BytesIO(patched)) as archive:
    info = archive.infolist()[0]
    print("zipfile filename    :", repr(info.filename))
    print("zipfile orig_filename:", repr(info.orig_filename))

try:
    result = inspect_candidate(patched)
    print("RESULT: ACCEPTED", result)
except TransferError as error:
    print("RESULT: REJECTED", error)
except Exception as error:  # noqa: BLE001
    print("RESULT: UNEXPECTED", type(error).__name__, error)

# Control: same archive with a non-NUL tail must be accepted.
control = raw.replace(PLACEHOLDER, b"data/definitions.jsonYYYYY")
try:
    result = inspect_candidate(control)
    print("CONTROL: ACCEPTED", result.declared_kind, result.roles)
except TransferError as error:
    print("CONTROL: REJECTED", error)
