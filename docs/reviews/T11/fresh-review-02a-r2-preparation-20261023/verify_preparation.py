"""Static packet verification only. Never runs setup, tests, or native tools.

Uses committed source objects and archive members directly; never extracts files.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import shlex
import subprocess
import tarfile
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CANDIDATE = "02a4738a220b2c6e881f7161ee658c61bf4328dc"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(name: str) -> dict:
    return json.loads((HERE / name).read_bytes())


def identity(data: bytes, record: dict) -> None:
    assert len(data) == record["bytes"] and sha(data) == record["sha256"], record


def git(path: str, commit: str = CANDIDATE) -> bytes:
    return subprocess.check_output(["git", "show", commit + ":" + path], cwd=REPO)


def archive(data: bytes) -> dict[str, bytes]:
    result = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        for member in tf.getmembers():
            name = PurePosixPath(member.name)
            assert member.isfile() and not name.is_absolute() and ".." not in name.parts
            assert member.name not in result, member.name
            result[member.name] = tf.extractfile(member).read()
    return result


def check_pages(data: bytes, pages: list[dict], materials: dict[str, bytes], key: str = "pageId") -> None:
    offset, line = 0, 1
    for page in pages:
        chunk = materials[page[key]]
        identity(chunk, page)
        chunk.decode("utf-8")
        lines = len(chunk.splitlines(keepends=True))
        assert 0 < len(chunk) <= 6144 and 0 < lines <= 64
        assert page["byteStart"] == offset and page["byteEndExclusive"] == offset + len(chunk)
        assert page["physicalLines"] == [line, line + lines - 1]
        assert page["endsWithLF"] == chunk.endswith(b"\n")
        assert chunk == data[offset:offset + len(chunk)]
        assert page.get("actualComplete", False) is False
        assert page.get("actualCallId") is None
        assert page.get("actualVisibleBytes") is None
        assert page.get("actualVisibleSha256") is None
        offset += len(chunk)
        line += lines
    assert offset == len(data)


def main() -> None:
    old = json.loads(git("docs/reviews/T11/fresh-review-02a-write-addendum-20261023/zcode-handoff-manifest.json", "f94ebafb409940b3973f7df1dd99b80325f380d0"))
    plan = load("scope-107-read-plan.json")
    expected = old["requiredFiles"]
    assert len(expected) == 107
    assert expected == [{k: r[k] for k in ("path", "bytes", "sha256")} for r in plan["files"]]
    index = load("common-input-materials-index.json")
    packed = (HERE / index["archive"]).read_bytes()
    identity(packed, index)
    materials = archive(packed)
    assert len(materials) == index["memberCount"] == 404
    assert set(materials) == {e["path"] for e in index["entries"]}
    for entry in index["entries"]:
        identity(materials[entry["path"]], entry)
        # Selected loose authored files must also match the archived exact bytes.
        if (HERE / entry["path"]).exists():
            assert materials[entry["path"]] == (HERE / entry["path"]).read_bytes()
    assert not any(n.startswith("roles/") or n == "environment-setup-plan.json" for n in materials)
    source, member_count, text_pages, member_pages = {}, 0, 0, 0
    for row in plan["files"]:
        data = git(row["path"])
        source[row["path"]] = data
        identity(data, row)
        assert row["candidate"] == CANDIDATE and row["actualComplete"] is False
        assert row["actualMethod"] is None
        if row["plannedMethod"] == "ARCHIVE_EACH_MEMBER":
            members = archive(data)
            assert set(members) == {m["name"] for m in row["archiveMembers"]}
            for member in row["archiveMembers"]:
                content = members[member["name"]]
                identity(content, member)
                check_pages(content, member["pages"], materials)
                member_count += 1
                member_pages += len(member["pages"])
        else:
            check_pages(data, row["pages"], materials)
            text_pages += len(row["pages"])
    assert (text_pages, member_count, member_pages) == (274, 75, 91)
    supplemental = load("supplemental-history-index.json")
    for entry in supplemental["entries"]:
        data = git(entry["sourcePath"], entry["sourceCommit"])
        identity(data, entry)
        assert data == materials[entry["path"]] and entry["actualRead"] is False
        if entry.get("pages"):
            check_pages(data, entry["pages"], materials)
    findings = load("source-treatment-19.json")
    levels = {**{f"M-F-{c}": "低" for c in "DEFGHIJK"}, "M-F-A": "高", "M-F-B": "中", "M-F-C": "中", "M-F-L": "中", **{f"Z-F{i}": "P4" for i in range(1, 7)}, "M036-F1": "中"}
    assert len(findings["findings"]) == 19 and findings["ownerClosedCount"] == 0
    assert {f["id"]: f["originalSeverity"] for f in findings["findings"]} == levels
    excerpts = 0
    for finding in findings["findings"]:
        assert finding["ownerStatus"] == "OPEN" and finding["ownerClosed"] is False
        assert finding["sourceTreatment"] and finding["existingVerificationLevels"] and finding["stillDependentOn"]
        for evidence in finding["sourceEvidence"]:
            data = source.get(evidence["path"])
            if data is None:
                data = git(evidence["path"])
            assert sha(data) == evidence["sourceSha256"] and evidence["candidate"] == CANDIDATE
            start, end = evidence["physicalLines"]
            excerpt = b"".join(data.splitlines(keepends=True)[start - 1:end])
            assert excerpt == evidence["excerpt"].encode() and sha(excerpt) == evidence["excerptSha256"]
            excerpts += 1
    historical = load("historical-derivations.json")
    historical_bytes = {r["logicalIndex"]: source[r["path"]] for r in historical["files"]}
    numbered = []
    for index in [39, 40]:
        matches = [re.match(rb" *([0-9]+)\xe2\x86\x92(.*)", line, re.DOTALL) for line in historical_bytes[index].splitlines(keepends=True)]
        numbered.append(b"".join(m.group(2) for m in matches if m))
    assert b"".join(numbered) == historical_bytes[41]
    for data, record in zip(numbered, historical["minimaxReadRelationship"]["decodedParts"]):
        identity(data, record)
    metadata = historical["minimaxReadRelationship"]["uniqueMetadata"]
    identity(metadata["text"].encode(), metadata)
    assert historical_bytes[39].endswith(metadata["text"].encode()) and metadata["bytes"] == 146
    rendered = historical_bytes[54].splitlines()
    decoded = b"\n".join(re.sub(rb"^[0-9]+\t", b"", line) for line in rendered)
    assert decoded == historical_bytes[51] and len(rendered) == 157
    zlines, mlines = historical_bytes[51].splitlines(keepends=True), historical_bytes[41].splitlines(keepends=True)
    assert [i + 1 for i, (a, b) in enumerate(zip(zlines, mlines)) if a != b] == [1, 3, 4, 6]
    assert b"".join(zlines[8:]) == b"".join(mlines[8:])
    assert sha(b"".join(zlines[8:])) == historical["roleAttachmentsRelationship"]["exactEqualSuffixSha256"]
    combined = load("environment-setup-plan.json")
    assert not Path(combined["newNamespace"]).exists()
    assert combined["setupExecuted"] is False and combined["productCommandsExecuted"] == []
    guide, common = (REPO / "AGENTS.md").read_bytes(), (HERE / "common-full-scope.md").read_bytes()
    role_receipts = {}
    for role, peer in [("zcode", "minimax"), ("minimax", "zcode")]:
        manifest = load(f"roles/{role}/handoff-manifest.json")
        assert manifest["requiredFiles"] == expected
        assert manifest["historicalFindingIds"] == [f["id"] for f in findings["findings"]]
        for value in manifest.values():
            if isinstance(value, dict) and "preparedPath" in value:
                identity((HERE / value["preparedPath"]).read_bytes(), value)
        identity(guide, manifest["guide"])
        identity(common, manifest["commonInstructionBody"])
        identity(packed, manifest["commonMaterialsArchive"])
        prompt = (HERE / manifest["fullInput"]["preparedPath"]).read_bytes()
        cb = manifest["commonInstructionBody"]
        assert prompt[cb["byteStartInOwnFullInput"]:cb["byteEndExclusiveInOwnFullInput"]] == common
        assert prompt.count(guide) == 1 and prompt.count(common) == 1
        env = load(f"roles/{role}/environment-plan.json")
        assert env == combined["roles"][role]
        assert f"fresh_r2/{peer}/" not in prompt.decode() and f"fresh_r2/{peer}/" not in json.dumps(manifest)
        assert env["actualTaskCreated"] is False and env["actualSetupExecuted"] is False
        assert env["offlineSeed"]["sourceIdentity"] is None
        assert env["ordinaryEnvironment"]["TMPDIR"] == env["ordinaryEnvironment"]["TMP"] == env["ordinaryEnvironment"]["TEMP"] == env["plannedTmp"]
        assert shlex.split(env["ordinaryEnvironment"]["PYTEST_ADDOPTS"]) == ["-o", "cache_dir=" + env["plannedRuntime"] + "/cache/pytest"]
        assert Path(env["plannedRuntime"]).parent == Path(env["plannedCwd"]).parent
        assert not Path(env["plannedCwd"]).exists() and not Path(env["plannedRuntime"]).exists()
        assert env["futureOrdinaryCommandPlan"][0]["argv"] == ["npm", "run", "check"]
        assert env["futureOrdinaryCommandPlan"][0]["additionalEnv"] == {"T11_FIXED_BASELINE_PROBE": "1"}
        assert not any(c["executed"] for c in env["futureOrdinaryCommandPlan"])
        assert env["supplementalFixtures"]["root"].startswith(env["plannedTmp"] + "/")
        for field in ["readyForDispatch", "setupExecuted", "newRootsCreated", "taskCreated", "actualSettingsReadBack", "ordinaryWritesAuthorized", "GUI_START", "designatedDualPass", "releaseAuthorized"]:
            assert manifest[field] is False
        page_manifest = load(f"roles/{role}/full-input-pages-manifest.json")
        page_archive = archive((HERE / f"roles/{role}/full-input-pages.tar.gz").read_bytes())
        assert set(page_archive) == {p["pathWithinOwnInput"] for p in page_manifest["pages"]}
        identity(prompt, page_manifest["preparedFullInput"])
        check_pages(prompt, page_manifest["pages"], page_archive, "pathWithinOwnInput")
        assert len(page_manifest["pages"]) == 16
        role_receipts[role] = {"bytes": len(prompt), "sha256": sha(prompt), "pages": 16}
    actual = load("actual-read-receipt-template.json")
    assert actual["logicalScopeCovered"] is False and actual["literalPathsRead"] == 0 and actual["gapPaths"] == 107
    assert len(actual["files"]) == 107 and all(not f["actualComplete"] for f in actual["files"])
    print(json.dumps({"kind": "STATIC_PREPARATION_VERIFICATION_ONLY", "candidate": CANDIDATE, "logicalFiles": 107, "textPages": text_pages, "archiveMembers": member_count, "archivePages": member_pages, "commonArchiveMembers": len(materials), "sourceBoundFindings": 19, "sourceExcerptsVerified": excerpts, "roleInputs": role_receipts, "actualReadProven": False, "setupExecuted": False, "productCommandsExecuted": [], "newNamespaceExists": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
