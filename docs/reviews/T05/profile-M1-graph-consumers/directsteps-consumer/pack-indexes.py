"""Preserve generated full index bytes losslessly; keep a small ZIP locator."""

import gzip
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCAL = Path.cwd() / "build/directsteps-index-originals"
LOCAL.mkdir(parents=True, exist_ok=True)


def identity(path):
    digest, size = hashlib.sha256(), 0
    with path.open("rb") as stream:
        while chunk := stream.read(1_048_576):
            digest.update(chunk)
            size += len(chunk)
    return {"bytes": size, "sha256": digest.hexdigest()}


records = []
for tag in ("direct-first", "direct-normal"):
    source = HERE / (tag + "-actual-index.json")
    raw_identity = identity(source)
    compressed = HERE / (tag + "-actual-index.full.json.gz")
    local = LOCAL / source.name
    assert not compressed.exists() and not local.exists()
    with source.open("rb") as reader, compressed.open("xb") as output:
        with gzip.GzipFile(filename="", mode="wb", fileobj=output, mtime=0) as writer:
            shutil.copyfileobj(reader, writer, 1_048_576)
    digest, size = hashlib.sha256(), 0
    with gzip.open(compressed, "rb") as reader:
        while chunk := reader.read(1_048_576):
            digest.update(chunk)
            size += len(chunk)
    assert {"bytes": size, "sha256": digest.hexdigest()} == raw_identity
    source.rename(local)
    members = json.loads((HERE / (tag + "-original-members.json")).read_bytes())
    cases = []
    with zipfile.ZipFile(HERE / members["summary"]["archive"]) as bundle:
        for row in members["members"]:
            if not row["member"].endswith("/observation.json"):
                continue
            value = json.loads(bundle.read(row["member"]))
            cases.append(
                {
                    "id": value["id"],
                    "kind": value["kind"],
                    "assertion": value["assertion"],
                    "completeObservation": row,
                    "actualStatus": value["actual"]["status"],
                }
            )
    record = {
        "tag": tag,
        "fullIndexOriginalBytes": raw_identity,
        "fullIndexLosslessGzip": {"path": compressed.name, **identity(compressed)},
        "uncompressedLocalOriginal": str(local),
        "decodedBytesSha256Verified": True,
        "noOriginalZipOrObservationOrCommandChange": True,
    }
    (HERE / (tag + "-actual-index.locator.json")).write_text(
        json.dumps(
            {"storage": record, "summary": members["summary"], "cases": cases},
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    records.append(record)
(HERE / "index-storage.json").write_text(
    json.dumps({"indexes": records}, ensure_ascii=False, indent=2) + "\n"
)
print(json.dumps({"losslessIndexes": records}, ensure_ascii=False))
