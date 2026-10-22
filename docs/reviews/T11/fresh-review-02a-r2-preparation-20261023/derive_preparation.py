"""Author preparation material only; never executes setup or product commands."""

from __future__ import annotations

import hashlib
import io
import json
import subprocess
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CANDIDATE = "02a4738a220b2c6e881f7161ee658c61bf4328dc"
LIMIT = 6144
LINE_LIMIT = 64


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def git_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", CANDIDATE + ":" + path], cwd=REPO)


def pages(data: bytes, directory: str) -> list[dict]:
    """Exact UTF-8 whole-line pages; no prefix, suffix, or LF is inserted."""
    data.decode("utf-8")
    result = []
    offset = 0
    first_line = 1
    chunk = b""
    count = 0

    def flush() -> None:
        nonlocal offset, first_line, chunk, count
        if not chunk:
            return
        rel = f"{directory}/part-{len(result) + 1:03d}.txt"
        path = HERE / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(chunk)
        result.append(
            {
                "pageId": rel,
                "byteStart": offset,
                "byteEndExclusive": offset + len(chunk),
                "physicalLines": [first_line, first_line + count - 1],
                "bytes": len(chunk),
                "sha256": sha(chunk),
                "endsWithLF": chunk.endswith(b"\n"),
                "derivation": "Exact contiguous source bytes; whole physical lines; no inserted bytes",
                "actualCallId": None,
                "actualVisibleBytes": None,
                "actualVisibleSha256": None,
                "actualComplete": False,
            }
        )
        offset += len(chunk)
        first_line += count
        chunk = b""
        count = 0

    for line in data.splitlines(keepends=True):
        if len(line) > LIMIT:
            raise ValueError(f"Long source line requires a separately approved split plan: {directory}")
        if chunk and (len(chunk) + len(line) > LIMIT or count >= LINE_LIMIT):
            flush()
        chunk += line
        count += 1
    flush()
    assert offset == len(data)
    reconstructed = b"".join((HERE / p["pageId"]).read_bytes() for p in result)
    assert reconstructed == data
    return result


def main() -> None:
    old = json.loads(
        (REPO / "docs/reviews/T11/fresh-review-02a-write-addendum-20261023/zcode-handoff-manifest.json").read_text()
    )
    required = old["requiredFiles"]
    assert len(required) == 107
    rows = []
    archives = []
    blobs = {}
    for index, entry in enumerate(required, 1):
        path = entry["path"]
        data = git_bytes(path)
        assert len(data) == entry["bytes"] and sha(data) == entry["sha256"], path
        blob = subprocess.check_output(
            ["git", "rev-parse", CANDIDATE + ":" + path], cwd=REPO, text=True
        ).strip()
        blobs.setdefault(blob, []).append(index)
        row = {
            "logicalIndex": index,
            **entry,
            "candidate": CANDIDATE,
            "gitBlob": blob,
            "plannedMethod": "LITERAL",
            "actualMethod": None,
            "actualComplete": False,
            "pages": [],
            "sameBlobLogicalIndices": [],
        }
        if path.endswith(".tar.gz"):
            row["plannedMethod"] = "ARCHIVE_EACH_MEMBER"
            index_path = str(Path(path).with_name("raw-logs-index.json"))
            member_index = json.loads(git_bytes(index_path))
            expected = {e["name"]: e for e in member_index["entries"]}
            members = []
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
                regular = [m for m in archive.getmembers() if m.isfile()]
                assert {m.name for m in regular} == set(expected), path
                for member_no, member in enumerate(regular, 1):
                    member_data = archive.extractfile(member).read()
                    e = expected[member.name]
                    assert len(member_data) == e["bytes"] and sha(member_data) == e["sha256"]
                    member_pages = pages(member_data, f"archive-pages/{index:03d}/{member_no:03d}")
                    members.append(
                        {
                            "name": member.name,
                            "bytes": len(member_data),
                            "sha256": sha(member_data),
                            "plannedMethod": "LITERAL_MEMBER_TEXT",
                            "pages": member_pages,
                            "actualComplete": False,
                        }
                    )
            row["archiveMembers"] = members
            archives.append({"logicalIndex": index, "path": path, "memberCount": len(members)})
        else:
            row["pages"] = pages(data, f"source-pages/{index:03d}")
        rows.append(row)
    for row in rows:
        row["sameBlobLogicalIndices"] = [i for i in blobs[row["gitBlob"]] if i != row["logicalIndex"]]
    dump(
        HERE / "scope-107-read-plan.json",
        {
            "schemaVersion": 1,
            "candidate": CANDIDATE,
            "logicalFileCount": 107,
            "sourceScopeUnchanged": required == [{k: r[k] for k in ("path", "bytes", "sha256")} for r in rows],
            "defaultDeduplication": "NONE: all104text paths literal;75archive members literal as separately indexed",
            "pageLimitBytes": LIMIT,
            "pageLimitPhysicalLines": LINE_LIMIT,
            "preparedPagesAreReadProof": False,
            "logicalScopeCoveredActual": False,
            "literalPathsReadActual": 0,
            "archives": archives,
            "files": rows,
        },
    )
    print(
        json.dumps(
            {
                "materialDerivationOnly": True,
                "logicalFiles": len(rows),
                "textPages": sum(len(r["pages"]) for r in rows),
                "archiveMembers": sum(a["memberCount"] for a in archives),
                "archivePages": sum(len(m["pages"]) for r in rows for m in r.get("archiveMembers", [])),
                "productCommandsExecuted": [],
            }
        )
    )


if __name__ == "__main__":
    main()
