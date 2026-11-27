"""R03 caller errors: real original-ID edits, owned host and independent stdio.

Each parameter owns a fresh fixture. A RED fixture stops after its first refused
request/readback; no HOLD reset, host replacement or input normalization occurs.
"""

import asyncio
import base64
import hashlib
import json
import os
import sys
from copy import deepcopy

import pytest
from ontolearn_engine.rdf_snapshot import term
from ontolearn_engine.storage import canonical, digest
from test_mainline_dispatch import owned as owned
from test_mainline_dispatch import uid
from test_mainline_manual_input_rejection import (
    PLAIN,
    assert_rejected,
    change,
    fact,
    input_change,
)
from test_mainline_manual_input_rejection import (
    test_known_caller_objects_reject_then_same_host_reads_and_commits as owned_rejection,
)

R03_REFUSALS = [
    pytest.param(family, value, id=f"{name}-{family}")
    for name, value in (
        ("language-first-digit", '"设备"@1'),
        ("language-first-subtag-digit", '"设备"@zh1'),
        ("integer-over-default-digit-bound", "9" * 4301),
    )
    for family in ("manual", "edit")
]
CANONICAL_TAGS = ('"设备"@en-001', '"设备"@de-ch-1901')


@pytest.mark.parametrize(("family", "value"), R03_REFUSALS)
def test_r03_same_owned_host_rejects_then_commits(owned, tmp_path, family, value):
    # Reuse every existing assertion, including the actual internal HOLD flag,
    # connection/lease/selection/owner identity and true committed original ID.
    owned_rejection(owned, tmp_path, family, value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [('"设备"@en-001', '"设备"@en-001'), ('"设备"@de-CH-1901', '"设备"@de-ch-1901')],
)
def test_digit_subtags_are_grammatical_separate_from_canonical_case_policy(value, expected):
    assert term(value).n3() == expected


def database_files(database):
    """Physical file bytes, not iterdump; no SQL/import into the child host."""
    result = {}
    for suffix in ("", "-wal", "-shm", "-journal"):
        path = database.with_name(database.name + suffix)
        if path.exists():
            raw = path.read_bytes()
            result[suffix or "main"] = {
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
    return result


async def stdio_case(tmp_path, family, value, *, reject):
    database = tmp_path / "stdio.sqlite"
    env = {**os.environ, "ONTOLEARN_DB_PATH": str(database)}
    env.pop("ONTOLEARN_TEST_MODE", None)
    env.pop("ONTOLEARN_ALLOWED_PROJECTS", None)
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "ontolearn_engine",
        "--t01-internal-profile=business3",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    session, wire, commits = None, [], []
    trace = {
        "transport": "independent stdio subprocess",
        "pid": process.pid,
        "family": family,
        "value": value,
        "expectControlledRefusal": reject,
    }

    async def call(method, params):
        request = {
            "kind": "request",
            "id": uid(),
            "method": method,
            "params": params,
            "protocolVersion": 2 if method == "hello" else 3,
            "engineSessionId": session,
        }
        wire.append({"sent": deepcopy(request)})
        process.stdin.write((json.dumps(request, ensure_ascii=False) + "\n").encode())
        await process.stdin.drain()
        while True:
            raw = await asyncio.wait_for(process.stdout.readline(), 10)
            assert raw, f"stdio EOF: {process.returncode}"
            response = json.loads(raw)
            wire.append({"received": response})
            if response.get("id") == request["id"]:
                if session is not None:
                    assert response["engineSessionId"] == session
                assert process.returncode is None
                return response

    async def ok(method, params):
        reply = await call(method, params)
        assert reply["ok"], canonical(reply)
        return reply["result"]

    async def commit(request):
        preview = await ok("changeset.preview", request)
        assert preview["status"] == "ready"
        cursor, pages, segments = None, [], []
        for _ in range(512):
            page = await ok(
                "changeset.diff.page",
                {
                    "projectId": project,
                    "previewHash": preview["previewHash"],
                    "documentKind": "diff",
                    "pageSize": 1,
                    "cursor": cursor,
                },
            )
            pages.append(page)
            segments.extend(page["segments"])
            cursor = page["nextCursor"]
            if page["complete"]:
                break
        assert pages[-1]["complete"]
        raw, offset = b"", 0
        for ordinal, part in enumerate(segments):
            chunk = base64.b64decode(part["dataBase64"], validate=True)
            assert part["ordinal"] == ordinal and part["byteOffset"] == offset
            assert len(chunk) == part["rawByteLength"]
            assert hashlib.sha256(chunk).hexdigest() == part["sha256"]
            raw += chunk
            offset += len(chunk)
        manifest = preview["manifest"]
        assert len(segments) == manifest["segmentCount"]
        assert len(raw) == manifest["totalBytes"]
        assert hashlib.sha256(raw).hexdigest() == manifest["documentHash"]
        document = json.loads(raw)
        expected = (
            next(iter(request["plan"]["edits"].values()))
            if "edits" in request["plan"]
            else request["plan"]["manual"][0]["object"]
        )
        assert len(document) == 1 and document[0]["after"]["object"] == expected
        assert digest(document) == manifest["documentHash"]
        confirmation = await ok(
            "changeset.confirm",
            {
                "projectId": project,
                "previewHash": preview["previewHash"],
                "completionCursor": cursor,
            },
        )
        operation = uid()
        job = await ok(
            "job.create",
            {
                "projectId": project,
                "operationId": operation,
                "capability": "changeset.commit",
                "confirmationRef": confirmation["confirmationRef"],
                "input": {
                    "inputSnapshotId": confirmation["inputSnapshotId"],
                    "scope": "asserted",
                    "definitionId": "changeset",
                    "parametersHash": confirmation["parametersHash"],
                    "derivedResultIds": [],
                    "preparedPlanRef": confirmation["preparedPlanRef"],
                },
            },
        )
        deadline = asyncio.get_running_loop().time() + 10
        while job["state"] in {"queued", "running", "cancelling"}:
            assert asyncio.get_running_loop().time() < deadline, job
            await asyncio.sleep(0.01)
            job = await ok("job.get", {"projectId": project, "jobId": job["jobId"]})
        assert job["state"] == "succeeded", job
        marker = await ok("operation.get", {"projectId": project, "operationId": operation})
        assert marker["jobId"] == job["jobId"] and marker["operationId"] == operation
        commits.append(
            {
                "preview": preview,
                "pages": pages,
                "document": document,
                "confirmation": confirmation,
                "job": job,
                "marker": marker,
            }
        )
        return marker

    try:
        hello = await ok("hello", {"supportedVersions": [3], "clientId": uid()})
        session = hello["engineSessionId"]
        trace["session"] = session
        project = (
            await ok(
                "project.create",
                {
                    "requestVersion": 1,
                    "operationId": uid(),
                    "name": "R03输入边界",
                    "initialization": {"kind": "blank"},
                },
            )
        )["projectId"]
        seed = await commit(change(project))
        params = {"projectId": project, "editor": "ontology"}
        before = await ok("project.read", params)
        identity = await ok("project.get", {"projectId": project})
        original = before["domain"]["state"]["facts"][0]
        assert before["domain"]["projectRevision"] == 1
        assert before["inputSnapshotId"] == seed["afterSnapshotId"]
        assert before["domain"]["state"]["facts"] == [
            {**fact(PLAIN), "owner": None, "source_row": None, "managed_value": None}
        ]
        request = input_change(project, family, value, 1)
        original_request = deepcopy(request)
        trace.update({"before": before, "identityBefore": identity, "request": original_request})
        if reject:
            physical_before = database_files(database)
            refused = await call("changeset.preview", request)
            current = await call("project.get", {"projectId": project})
            after_error = await call("project.read", params)
            physical_after = database_files(database)
            trace.update(
                {
                    "refused": refused,
                    "identityAfter": current,
                    "afterError": after_error,
                    "databaseBefore": physical_before,
                    "databaseAfter": physical_after,
                    "requestUnchanged": request == original_request,
                }
            )
            # A RED HOLD fixture stops at this assertion, without another write.
            assert_rejected(refused)
            assert current["ok"] and current["result"] == identity
            assert after_error["ok"] and after_error["result"] == before
            assert physical_before == physical_after
            assert request == original_request
            request = input_change(project, family, '"后继合法"@en-001', 1)
        marker = await commit(request)
        after = await ok("project.read", params)
        assert after["domain"]["projectRevision"] == 2
        assert marker["beforeSnapshotId"] == before["inputSnapshotId"]
        assert after["inputSnapshotId"] == marker["afterSnapshotId"]
        expected_value = '"后继合法"@en-001' if reject else value
        expected_facts = {original["id"]: original}
        if family == "edit":
            expected_facts[original["id"]] = {**original, "object": expected_value}
        else:
            added = {
                **fact(expected_value),
                "owner": None,
                "source_row": None,
                "managed_value": None,
            }
            expected_facts[added["id"]] = added
        assert {item["id"]: item for item in after["domain"]["state"]["facts"]} == expected_facts
        assert session == hello["engineSessionId"] and process.returncode is None
        trace.update(
            {
                "after": after,
                "stage": "complete",
                "samePID": process.pid,
                "sameSession": session,
                "marker": marker,
            }
        )
    finally:
        process.stdin.close()
        forced = False
        try:
            await asyncio.wait_for(process.wait(), 10)
        finally:
            if process.returncode is None:
                forced = True
                process.kill()
                await process.wait()
            trace.update(
                {"commits": commits, "returnCode": process.returncode, "forcedKill": forced}
            )
            (tmp_path / "r03-stdio-trace.json").write_text(
                json.dumps(trace, ensure_ascii=False), encoding="utf-8"
            )
            (tmp_path / "r03-stdio-wire.json").write_text(
                json.dumps(wire, ensure_ascii=False), encoding="utf-8"
            )
            (tmp_path / "r03-stdio.stderr.txt").write_bytes(await process.stderr.read())
        assert process.returncode == 0 and not forced


@pytest.mark.parametrize(("family", "value"), R03_REFUSALS)
def test_r03_independent_stdio_refusal_then_same_host_full_commit(tmp_path, family, value):
    asyncio.run(stdio_case(tmp_path, family, value, reject=True))


@pytest.mark.parametrize("family", ["manual", "edit"])
@pytest.mark.parametrize("value", CANONICAL_TAGS)
def test_canonical_digit_subtags_still_commit_over_stdio(tmp_path, family, value):
    asyncio.run(stdio_case(tmp_path, family, value, reject=False))


@pytest.mark.parametrize("family", ["manual", "edit"])
def test_grammatical_uppercase_subtag_keeps_existing_canonical_rejection(tmp_path, family):
    asyncio.run(stdio_case(tmp_path, family, '"设备"@de-CH-1901', reject=True))
