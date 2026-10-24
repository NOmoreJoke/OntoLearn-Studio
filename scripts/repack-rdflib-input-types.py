"""Deterministically rebuild one verified RDFLib wheel with one pinned source patch.

Uses only the standard library and never imports or executes the wheel's code.
ZIP_STORED, fixed member ordering/timestamps/modes avoid compressor variability.
"""

import argparse
import base64
import csv
import hashlib
import io
import json
import re
import stat
import zipfile
from pathlib import Path

VERSION = "7.6.0+ontolearn.fr201.1"
UPSTREAM_SHA = "30c0a3ebf4c0e09215f066be7246794b6492e054e782d7ac2a34c9f70a15e0dd"
SOURCE_SHA = "a3e361632567b5326a06318e93e081f31f93c7497d1b52cbb91f2ef460a9d3ca"
PATCH_SHA = "03e12f742d8f52a105f9513f1788df928def25b06663efc616fa3eaaa3077b65"
AFTER_SHA = "a1f8eef3d99793d533e4b60da3299abc627fb2d164c1fa92b894c414333cb3b1"
MODULE = "rdflib/plugins/parsers/notation3.py"
OLD_INFO = "rdflib-7.6.0.dist-info/"
NEW_INFO = f"rdflib-{VERSION}.dist-info/"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def apply_exact_patch(source, patch):
    lines = source.decode("utf-8").splitlines(keepends=True)
    edits = patch.decode("utf-8").splitlines(keepends=True)
    require(edits[:2] == [f"--- a/{MODULE}\n", f"+++ b/{MODULE}\n"], "Unexpected patch target")
    cursor = 0
    result = []
    index = 2
    while index < len(edits):
        header = re.fullmatch(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@\n", edits[index])
        require(header is not None, "Malformed hunk")
        old_start, old_count, new_start, new_count = (
            int(header[1]) - 1,
            int(header[2] or 1),
            int(header[3]) - 1,
            int(header[4] or 1),
        )
        require(old_start >= cursor, "Overlapping hunk")
        result.extend(lines[cursor:old_start])
        require(len(result) == new_start, "New hunk offset mismatch")
        cursor = old_start
        consumed = produced = 0
        index += 1
        while index < len(edits) and not edits[index].startswith("@@ "):
            item = edits[index]
            require(item[:1] in (" ", "-", "+"), "Unsupported hunk line")
            if item[0] in " -":
                require(cursor < len(lines) and lines[cursor] == item[1:], "Patch context mismatch")
                cursor += 1
                consumed += 1
            if item[0] in " +":
                result.append(item[1:])
                produced += 1
            index += 1
        require((consumed, produced) == (old_count, new_count), "Hunk count mismatch")
    result.extend(lines[cursor:])
    return "".join(result).encode("utf-8")


def record_bytes(files):
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    for name in sorted(files):
        data = files[name]
        digest = (
            base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode("ascii")
        )
        writer.writerow((name, f"sha256={digest}", str(len(data))))
    writer.writerow((NEW_INFO + "RECORD", "", ""))
    return buffer.getvalue().encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--patch", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    original = args.upstream.read_bytes()
    patch = args.patch.read_bytes()
    require(sha(original) == UPSTREAM_SHA, "Official input wheel SHA mismatch")
    require(sha(patch) == PATCH_SHA, "Reviewed patch SHA mismatch")
    with zipfile.ZipFile(io.BytesIO(original)) as archive:
        require(len(archive.namelist()) == len(set(archive.namelist())), "Duplicate ZIP members")
        files = {name: archive.read(name) for name in archive.namelist() if not name.endswith("/")}
    require(sha(files[MODULE]) == SOURCE_SHA, "Upstream source SHA mismatch")
    # Validate every upstream RECORD row before transforming anything.
    records = list(csv.reader(io.StringIO(files[OLD_INFO + "RECORD"].decode("utf-8"))))
    require({row[0] for row in records} == set(files), "Upstream RECORD keyset mismatch")
    for name, digest, size in records:
        if name == OLD_INFO + "RECORD":
            require(not digest and not size, "Unexpected RECORD self hash")
        else:
            expected = (
                "sha256="
                + base64.urlsafe_b64encode(hashlib.sha256(files[name]).digest())
                .rstrip(b"=")
                .decode()
            )
            require(
                digest == expected and int(size) == len(files[name]),
                f"Upstream RECORD mismatch: {name}",
            )
    source = apply_exact_patch(files[MODULE], patch)
    require(sha(source) == AFTER_SHA, "Patched source SHA mismatch")
    old_files = files.copy()
    files[MODULE] = source
    metadata = files[OLD_INFO + "METADATA"]
    require(metadata.count(b"\nVersion: 7.6.0\n") == 1, "Unexpected upstream version header")
    files[OLD_INFO + "METADATA"] = metadata.replace(
        b"\nVersion: 7.6.0\n", f"\nVersion: {VERSION}\n".encode(), 1
    )
    del files[OLD_INFO + "RECORD"]
    files = {
        (NEW_INFO + name[len(OLD_INFO) :] if name.startswith(OLD_INFO) else name): data
        for name, data in files.items()
    }
    files[NEW_INFO + "RECORD"] = record_bytes(files)
    # License and every non-target member retain original bytes; names only change for dist-info.
    for name, data in old_files.items():
        if name not in (MODULE, OLD_INFO + "METADATA", OLD_INFO + "RECORD"):
            target = NEW_INFO + name[len(OLD_INFO) :] if name.startswith(OLD_INFO) else name
            require(files[target] == data, f"Unexpected member change: {name}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    wheel = args.output_dir / f"rdflib-{VERSION}-py3-none-any.whl"
    require(not wheel.exists(), "Output wheel already exists; preserve previous artifacts")
    with zipfile.ZipFile(wheel, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(files):
            member = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            member.create_system = 3
            member.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(member, files[name])
    print(
        json.dumps(
            {
                "wheel": str(wheel),
                "bytes": wheel.stat().st_size,
                "sha256": sha(wheel.read_bytes()),
                "version": VERSION,
                "upstreamSHA256": UPSTREAM_SHA,
                "patchSHA256": PATCH_SHA,
                "sourceSHA256": AFTER_SHA,
                "memberCount": len(files),
                "compression": "ZIP_STORED",
                "timestamp": "1980-01-01T00:00:00",
                "changedContentMembers": [MODULE, NEW_INFO + "METADATA", NEW_INFO + "RECORD"],
                "licenseUnchanged": files[NEW_INFO + "LICENSE"] == old_files[OLD_INFO + "LICENSE"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
