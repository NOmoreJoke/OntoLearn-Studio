"""Real RDFLib S1 fixed workload; no user query or remote parser inputs.

JSON output is raw observation, not a business capacity pass/fail threshold.
One fresh process per scale/trial measures load, build and fixed query phases.
"""

import hashlib
import json
import platform
import sqlite3
import time
import tracemalloc
from importlib.metadata import version
from tempfile import TemporaryDirectory

from rdflib import Graph

from ontolearn_engine.rdf_snapshot import graph_from_snapshot
from ontolearn_engine.storage import Store, digest

try:
    import resource
except ImportError:  # Windows: retain tracemalloc measurements and state RSS is unavailable.
    resource = None


def high_water_rss() -> int | None:
    if resource is None:
        return None
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (
        1 if platform.system() == "Darwin" else 1024
    )


SEED = 20261019
QUERY = """PREFIX : <urn:ontolearn:>
SELECT ?alarm WHERE { ?alarm :level "High"; :status "Open" } ORDER BY ?alarm"""


def fixture(scale: int) -> str:
    """Each copy uses independent IDs, same six objects/structure as G-base facts."""
    blocks = ["@prefix : <urn:ontolearn:> ."]
    for i in range(scale):
        for equipment, name in (("001", "泵站A"), ("002", "泵站B"), ("003", "备用泵C")):
            blocks.append(f'<urn:case:{i}:equipment/{equipment}> a :Equipment; :name "{name}" .')
        for alarm, equipment, level, status in (
            ("A01", "001", "High", "Open"),
            ("A02", "002", "High", "Closed"),
            ("A03", "003", "Low", "Open"),
        ):
            blocks.append(
                f'<urn:case:{i}:alarm/{alarm}> a :Alarm; :level "{level}"; :status "{status}" .'
            )
            blocks.append(
                f"<urn:case:{i}:equipment/{equipment}> :alarm <urn:case:{i}:alarm/{alarm}> ."
            )
    return "\n".join(blocks)


def measure(scale: int = 1, trial: int = 0) -> dict:
    with TemporaryDirectory() as directory:
        store = Store(f"{directory}/probe.db")
        store.create_project("synthetic")
        ttl = fixture(scale)
        generated = Graph().parse(data=ttl, format="turtle")
        facts = [
            {
                "id": digest([str(s), str(p), o.n3()]),
                "subject": str(s),
                "predicate": str(p),
                "object": o.n3(),
            }
            for s, p, o in generated
        ]
        store.commit(
            "synthetic",
            0,
            "fixture",
            "fixture-job",
            manual=facts,
        )
        identity = store.snapshot("synthetic")
        store.close()
        store = Store(f"{directory}/probe.db")
        measurements = {}
        tracemalloc.start()

        def phase(name, action):
            tracemalloc.reset_peak()
            before = tracemalloc.get_traced_memory()[0]
            start = time.perf_counter_ns()
            result = action()
            elapsed = time.perf_counter_ns() - start
            current, peak = tracemalloc.get_traced_memory()
            measurements[name] = {
                "elapsedNs": elapsed,
                "pythonBytesBefore": before,
                "pythonBytesAfter": current,
                "pythonBytesPeak": peak,
                "processHighWaterRssBytes": high_water_rss(),
            }
            return result

        snapshot = phase("snapshotLoad", lambda: store.load_snapshot(identity))
        graph = phase("rdflibBuild", lambda: graph_from_snapshot(snapshot))
        results = phase("fixedSelect", lambda: [str(r.alarm) for r in graph.query(QUERY)])
        expected = sorted(f"urn:case:{i}:alarm/A01" for i in range(scale))
        assert results == expected
        assert len(graph) == 18 * scale
        phase("snapshotLoadWarm", lambda: store.load_snapshot(identity))
        warm_graph = phase("rdflibBuildWarm", lambda: graph_from_snapshot(snapshot))
        warm_results = phase(
            "fixedSelectWarm", lambda: [str(r.alarm) for r in warm_graph.query(QUERY)]
        )
        assert warm_results == expected
        store.close()
        tracemalloc.stop()
        return {
            "scale": scale,
            "trial": trial,
            "seed": SEED,
            "triples": len(graph),
            "inputSha256": hashlib.sha256(ttl.encode()).hexdigest(),
            "querySha256": hashlib.sha256(QUERY.encode()).hexdigest(),
            "result": results,
            "expected": expected,
            "snapshotId": identity,
            "measurement": measurements,
            "device": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
            "rdflib": version("rdflib"),
            "condition": "store reopened; OS cache uncontrolled; Warm phases repeat in process",
            "method": "perf_counter_ns; tracemalloc phase peaks; "
            + (
                "process lifetime ru_maxrss"
                if resource is not None
                else "RSS unavailable on platform"
            ),
            "rssAvailable": resource is not None,
        }


# Private prepared workload. Fixed pairs are authority; expected is never a result.
_PREPARED_PAIRS = {
    1: (
        (6266, "cf28104cd1e08bed57fb01782e3cb6fde2a10b535c5218e53e8450982d85f93c"),
        (663, "347630e2fb39b3c57f00ad5774356fb7d06178a55dfd327eeed84387b3b12140"),
    ),
    10: (
        (41799, "94fbd119a71ee0e68b49e0d0befc9d39664e0869f832ec1cadf8dc8e7dcda0e2"),
        (1445, "9a4a76639aab6de5e3afa714ab3f2cc5dd47638fb1a5cc6d13587489f5ea7763"),
    ),
    100: (
        (397210, "28ff312af35e79b17c390aa96c477347208f66879a0407e8eb0f7ddf508ee5b8"),
        (9193, "2b459247f05b09220ff795db22ff3aeeba084d0b964be89f90558114c2c014f3"),
    ),
}
_PREPARED_SEMANTIC_PINS = {
    "semantic_execution.py": (
        37294,
        "1354a3c24b8d323e1645f7b5485fc835bb03de662bf1ebf57a43efcfac6b2aad",
    ),
    "semantic.py": (66258, "d6c5f5c38aec310de726f73568e1086bf4de95117cbdf664ae1384fcd6808392"),
    "semantic_scopes.py": (
        13051,
        "aa8f1231df09332e9f02d96e3c8e4ef4cb64d4b3fa28067babcd3431de820ebf",
    ),
}
_PREPARED_QUERY_ID = "unclosed-high"
_PREPARED_RESOURCE_SHA = "8efbacd589c42ac40abbb55475cdd088e407a88a23e0db61dc8375e04e4dd386"
_PREPARED_MANAGED_SHA = "fece9d36a05da535d46ab2e8488bb5781b9fac338ebed43f95dc32b4a22e1cda"


class _PreparedFault(Exception):
    def __init__(self, reason, detail=None):
        self.reason, self.detail = reason, detail
        super().__init__(reason)


def _prepared_require(condition, reason, detail=None):
    if not condition:
        raise _PreparedFault(reason, detail)


def _prepared_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _prepared_pin(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def _prepared_inputs(scale, input_path, expected_path):
    """Reject wrong size/hash/pair before parsing or creating any database."""
    from pathlib import Path

    _prepared_require(type(scale) is int and scale in _PREPARED_PAIRS, "fixed-scale-required")
    material, pins = [], []
    for path, (size, sha) in zip((input_path, expected_path), _PREPARED_PAIRS[scale], strict=True):
        with Path(path).open("rb") as stream:
            raw = stream.read(size + 1)
        _prepared_require(
            len(raw) == size and hashlib.sha256(raw).hexdigest() == sha,
            "fixed-pair-mismatch",
            {"path": str(path), "observed": _prepared_pin(raw)},
        )
        material.append(json.loads(raw))
        pins.append({"path": str(Path(path).resolve()), **_prepared_pin(raw)})
    data, expected = material
    text = data["queryText"]
    _prepared_require(
        data["scale"] == expected["scale"] == scale
        and len(data["assertedFacts"]) == 18 * scale
        and len(data["ontology"]) == 10,
        "fixed-data-shape",
    )
    _prepared_require(
        len(text.encode()) == 162
        and hashlib.sha256(text.encode()).hexdigest() == _PREPARED_RESOURCE_SHA
        and len(text.removesuffix("\n").encode()) == 161
        and hashlib.sha256(text.removesuffix("\n").encode()).hexdigest() == _PREPARED_MANAGED_SHA,
        "query-resource-managed-binding",
    )
    query_expected = {
        "type": "SELECT",
        "variables": expected["query"]["variables"],
        "rows": [
            [row[v] for v in expected["query"]["variables"]] for row in expected["query"]["rows"]
        ],
    }
    return data, query_expected, pins


class _PreparedSession:
    """Actual production serve child. No Coordinator sentinel or test authority.

    POSIX pipes are nonblocking; each write/read and final EOF is bounded. A
    failure preserves the first diagnosis plus full retained raw up to 16 MiB.
    No child PID guessed from a table is ever signalled.
    """

    def __init__(self, database):
        import os
        import selectors
        import subprocess
        import sys

        from ontolearn_engine.protocol import JsonlReader
        from ontolearn_engine.resources import CONTRACT, LIMITS, REGISTRY_HASH

        _prepared_require(os.name == "posix", "prepared-stdio-platform-not-supplied")
        self.contract, self.limits, self.registry = CONTRACT, LIMITS, REGISTRY_HASH
        self.reader = JsonlReader(LIMITS["maxFrameBytes"])
        self.raw = {"stdout": bytearray(), "stderr": bytearray()}
        self.eof = {"stdout": False, "stderr": False}
        self.frames, self.requests, self.signals = [], [], []
        self.dropped_bytes, self.read_failure = 0, None
        self.session, self.first_failure, self.process = None, None, None
        self.started = time.perf_counter_ns()
        self.end = time.monotonic() + LIMITS["totalMs"] / 1000
        self.selector = selectors.DefaultSelector()
        # Only OS essentials; no inherited product authority/test/Python injection.
        allowed = (
            "PATH",
            "HOME",
            "TMPDIR",
            "TEMP",
            "TMP",
            "LANG",
            "LC_ALL",
            "LC_CTYPE",
            "SYSTEMROOT",
            "WINDIR",
            "PATHEXT",
        )
        env = {key: os.environ[key] for key in allowed if key in os.environ}
        env["ONTOLEARN_DB_PATH"] = str(database)
        self.argv = (
            [sys.executable]
            if getattr(sys, "frozen", False)
            else [sys.executable, "-I", "-m", "ontolearn_engine"]
        )
        self.argv += ["--t01-internal-profile=business3"]
        self.environment = env
        try:
            self.process = subprocess.Popen(
                self.argv,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                bufsize=0,
            )
            for name in ("stdin", "stdout", "stderr"):
                os.set_blocking(getattr(self.process, name).fileno(), False)
            for name in ("stdout", "stderr"):
                self.selector.register(getattr(self.process, name), selectors.EVENT_READ, name)
        except BaseException:
            self.abort()
            raise

    def _pump(self, deadline, *, cleanup=False):
        import os

        remaining = (deadline if cleanup else min(deadline, self.end)) - time.monotonic()
        _prepared_require(remaining > 0, "production-session-deadline")
        for key, _ in self.selector.select(min(remaining, 0.1)):
            name = key.data
            if name == "stdin":
                continue
            chunk = os.read(key.fileobj.fileno(), 65536)
            if not chunk:
                self.eof[name] = True
                self.selector.unregister(key.fileobj)
                key.fileobj.close()
                if name == "stdout":
                    self.reader.finish()
                continue
            room = 16 * 1024 * 1024 - sum(map(len, self.raw.values()))
            self.raw[name].extend(chunk[:room])
            if len(chunk) > room:
                self.dropped_bytes += len(chunk) - room
                raise _PreparedFault("production-wire-capture-cap")
            if name == "stdout":
                self.frames.extend(self.reader.feed(chunk))
        if self.process.poll() not in (None, 0) and self.first_failure is None:
            self.first_failure = {
                "reason": "production-child-nonzero",
                "exitCode": self.process.returncode,
            }
        # Preserve bounded raw drain before reporting a nonzero exit.
        if self.first_failure is not None and all(self.eof.values()):
            raise _PreparedFault(self.first_failure["reason"], self.first_failure)

    def request(self, method, params):
        import os
        import selectors
        from uuid import uuid4

        _prepared_require(not self.frames and not self.eof["stdout"], "unexpected-before-request")
        envelope = {
            "kind": "request",
            "id": str(uuid4()),
            "protocolVersion": 2 if method == "hello" else 3,
            "engineSessionId": None if method == "hello" else self.session,
            "method": method,
            "params": params,
        }
        raw = _prepared_bytes(envelope)
        _prepared_require(
            len(raw) <= self.limits["maxFrameBytes"]
            and self.contract.validate_business3("request", envelope),
            "illegal-request-envelope",
            {"method": method, **_prepared_pin(raw)},
        )
        deadline = min(
            self.end,
            time.monotonic()
            + self.limits["handshakeMs" if method == "hello" else "requestMs"] / 1000,
        )
        self.selector.register(self.process.stdin, selectors.EVENT_WRITE, "stdin")
        packet, offset = raw + b"\n", 0
        start = time.perf_counter_ns()
        try:
            while offset < len(packet):
                self._pump(deadline)
                try:
                    offset += os.write(self.process.stdin.fileno(), memoryview(packet)[offset:])
                except BlockingIOError:
                    pass
        finally:
            self.selector.unregister(self.process.stdin)
        while not self.frames:
            _prepared_require(not self.eof["stdout"], "response-missing-at-eof")
            self._pump(deadline)
        _prepared_require(len(self.frames) == 1, "unexpected-extra-production-frame")
        response = self.frames.pop()
        self.requests.append(
            {
                "request": envelope,
                "requestBytes": len(raw),
                "response": response,
                "elapsedNs": time.perf_counter_ns() - start,
            }
        )
        _prepared_require(
            self.contract.matches_business3_response(envelope, response, self.registry),
            "strict-response-binding",
            response,
        )
        if not response["ok"]:
            raise _PreparedFault("original-business-refusal", response)
        if method == "hello":
            self.session = response["engineSessionId"]
        return response["result"]

    def finish(self):
        self.process.stdin.close()
        while not all(self.eof.values()) or self.process.poll() is None:
            self._pump(self.end)
        _prepared_require(
            self.process.wait(timeout=max(0.001, self.end - time.monotonic())) == 0
            and not self.frames
            and not self.signals,
            "unclean-production-finish",
        )
        self.selector.close()

    def abort(self):
        # This is failed-run cleanup, never a natural-exit success.
        process = self.process
        if process is not None:
            for action in ("terminate", "kill"):
                if process.poll() is not None:
                    break
                try:
                    getattr(process, action)()
                    self.signals.append(action)
                    process.wait(timeout=5)
                except Exception:
                    continue
            drain_end = time.monotonic() + 5
            while not all(self.eof.values()) and time.monotonic() < drain_end:
                try:
                    self._pump(drain_end, cleanup=True)
                except Exception as error:
                    self.read_failure = {"type": type(error).__name__, "reason": str(error)}
                    if all(self.eof.values()) or self.dropped_bytes:
                        break
            for name in ("stdin", "stdout", "stderr"):
                stream = getattr(process, name)
                if stream is not None:
                    stream.close()
        self.selector.close()

    def evidence(self):
        import base64
        import os

        return {
            "argv": self.argv,
            "environment": self.environment,
            "cwd": os.getcwd(),
            "coordinatorPid": self.process.pid if self.process else None,
            "naturalExitCode": self.process.returncode
            if self.process and not self.signals
            else None,
            "observedExitCode": self.process.returncode if self.process else None,
            "fullEof": dict(self.eof),
            "signals": self.signals,
            "droppedBytes": self.dropped_bytes,
            "readFailure": self.read_failure,
            "firstChildFailure": self.first_failure,
            "elapsedNs": time.perf_counter_ns() - self.started,
            "workerPid": None,
            "workerPidReason": "not supplied by existing public Job wire",
            "workerPhaseMemory": None,
            "requests": self.requests,
            "streams": {
                name: {**_prepared_pin(raw), "dataBase64": base64.b64encode(raw).decode()}
                for name, raw in self.raw.items()
            },
        }


def _prepared_job(client, project, accepted):
    deadline = min(client.end, time.monotonic() + client.limits["totalMs"] / 1000)
    while True:
        job = client.request("job.get", {"projectId": project, "jobId": accepted["jobId"]})
        _prepared_require(job["operationId"] == accepted["operationId"], "accepted-job-binding")
        if job["state"] in ("succeeded", "failed", "cancelled"):
            _prepared_require(job["state"] == "succeeded", "original-job-terminal", job)
            return job
        _prepared_require(time.monotonic() < deadline, "job-terminal-deadline")
        time.sleep(0.01)


def _prepared_preview_fits(params, max_frame):
    """Keep the original wire/count gate AND the domain params+1024 gate."""
    envelope = {
        "kind": "request",
        "id": "f" * 36,
        "protocolVersion": 3,
        "engineSessionId": "f" * 36,
        "method": "changeset.preview",
        "params": params,
    }
    return (
        len(params["plan"].get("manual", [])) <= 4096
        and len(_prepared_bytes(envelope)) <= max_frame
        and len(_prepared_bytes(params)) + 1024 <= min(262144, max_frame)
    )


def _prepared_fact_batches(project, facts, max_frame):
    """Yield unchanged ordered facts only after both worst-header checks."""
    batch = []
    for fact in facts:
        candidate = [*batch, fact]
        params = {
            "projectId": project,
            "baseRevision": 9007199254740991,
            "intent": "change",
            "plan": {"manual": candidate},
        }
        if not _prepared_preview_fits(params, max_frame):
            _prepared_require(bool(batch), "single-fact-frame-limit")
            single = [fact]
            single_params = {**params, "plan": {"manual": single}}
            # Reject an impossible next fact before yielding/committing even the
            # previous batch. A new singleton never bypasses either predicate.
            _prepared_require(
                _prepared_preview_fits(single_params, max_frame), "single-fact-frame-limit"
            )
            yield batch
            batch = single
        else:
            batch = candidate
    if batch:
        yield batch


def _prepared_commit(client, project, plan):
    import base64
    from uuid import uuid4

    opened = client.request("project.open", {"projectId": project})
    params = {
        "projectId": project,
        "baseRevision": opened["projectRevision"],
        "intent": "change",
        "plan": plan,
    }
    # Recheck the actual params after open supplies the real base revision,
    # before the preview request can be emitted. Session.request still performs
    # its original actual-envelope encoding and contract checks independently.
    _prepared_require(
        _prepared_preview_fits(params, client.limits["maxFrameBytes"]),
        "preview-input-frame-limit",
        {
            "paramsBytes": len(_prepared_bytes(params)),
            "maxFrameBytes": client.limits["maxFrameBytes"],
        },
    )
    ready = client.request("changeset.preview", params)
    _prepared_require(ready["status"] == "ready", "preview-not-ready", ready)
    manifest, cursor, pieces, seen = ready["manifest"], None, [], set()
    while True:
        page = client.request(
            "changeset.diff.page",
            {
                "projectId": project,
                "previewHash": ready["previewHash"],
                "documentKind": "diff",
                "pageSize": 1,
                "cursor": cursor,
            },
        )
        _prepared_require(
            page["documentHash"] == manifest["documentHash"]
            and page["documentKind"] == "diff"
            and page["previewHash"] == ready["previewHash"]
            and page["projectId"] == project,
            "diff-manifest-changed",
        )
        for segment in page["segments"]:
            ordinal = len(pieces)
            _prepared_require(ordinal < len(manifest["segments"]), "diff-extra-segment")
            descriptor = manifest["segments"][ordinal]
            _prepared_require(
                {k: segment[k] for k in descriptor} == descriptor
                and descriptor["ordinal"] == ordinal
                and descriptor["byteOffset"] == sum(map(len, pieces)),
                "diff-segment-binding",
            )
            raw = base64.b64decode(segment["dataBase64"], validate=True)
            _prepared_require(
                base64.b64encode(raw).decode() == segment["dataBase64"]
                and _prepared_pin(raw)
                == {"bytes": descriptor["rawByteLength"], "sha256": descriptor["sha256"]},
                "diff-segment-integrity",
            )
            pieces.append(raw)
        cursor = page["nextCursor"]
        _prepared_require(
            type(cursor) is str and cursor and cursor not in seen, "diff-cursor-progress"
        )
        seen.add(cursor)
        if page["complete"]:
            break
    raw = b"".join(pieces)
    _prepared_require(
        len(pieces) == manifest["segmentCount"]
        and _prepared_pin(raw)
        == {"bytes": manifest["totalBytes"], "sha256": manifest["documentHash"]}
        and type(json.loads(raw)) is list,
        "full-diff-integrity",
    )
    confirmation = client.request(
        "changeset.confirm",
        {"projectId": project, "previewHash": ready["previewHash"], "completionCursor": cursor},
    )
    operation = str(uuid4())
    accepted = client.request(
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
    job = _prepared_job(client, project, accepted)
    marker = client.request("operation.get", {"projectId": project, "operationId": operation})
    _prepared_require(
        job["commitProgress"]["mode"] == "atomic"
        and job["commitProgress"]["marker"]
        == {
            k: marker[k]
            for k in ("projectRevision", "beforeSnapshotId", "afterSnapshotId", "planHash")
        }
        and marker["jobId"] == job["jobId"]
        and marker["operationId"] == operation,
        "commit-marker-binding",
    )
    receipt = client.request(
        "result.get", {"projectId": project, "resultId": job["resultRef"]["resultId"]}
    )
    return {
        "job": job,
        "marker": marker,
        "receipt": receipt,
        "manifest": manifest,
        "diff": json.loads(raw),
        "confirmation": confirmation,
    }


def _prepared_setup(client, data):
    from uuid import uuid4

    client.request("hello", {"supportedVersions": [3], "clientId": str(uuid4())})
    created = client.request(
        "project.create",
        {
            "requestVersion": 1,
            "operationId": str(uuid4()),
            "name": "D2 fixed prepared G-base",
            "initialization": {"kind": "blank"},
        },
    )
    project = created["projectId"]
    opened = client.request("project.open", {"projectId": project})
    _prepared_require(
        opened["formatVersion"] == 3 and opened["projectRevision"] == 0, "format3-blank-required"
    )
    definitions = [
        {"layer": "ontology", "id": t["subject"].rsplit(":", 1)[1], "value": {"triples": [t]}}
        for t in data["ontology"]
    ]
    definitions.append(
        {
            "layer": "query",
            "id": _PREPARED_QUERY_ID,
            "value": {
                "text": data["queryText"].removesuffix("\n"),
                "references": [],
                "descriptor": {
                    "version": 1,
                    "name": "未关闭的高等级告警",
                    "description": "设备运维示例查询",
                    "scope": "asserted",
                    "capabilityQuestion": "哪些高等级告警尚未关闭？",
                    "source": "template",
                },
            },
        }
    )
    commits = [_prepared_commit(client, project, {"definitions": definitions})]
    facts = [
        {"id": digest([t["subject"], t["predicate"], t["object"]]), **t}
        for t in data["assertedFacts"]
    ]
    # Each worst-header batch satisfies both original input gates. No facts,
    # IDs or ordering change; all later real preview params are checked again.
    for batch in _prepared_fact_batches(project, facts, client.limits["maxFrameBytes"]):
        commits.append(_prepared_commit(client, project, {"manual": batch}))
    current = client.request("project.open", {"projectId": project})
    record = client.request(
        "query.definition.load",
        {
            "projectId": project,
            "definitionId": _PREPARED_QUERY_ID,
            "selection": {"kind": "current"},
        },
    )
    _prepared_require(record["kind"] == "managed", "managed-query-required")
    operation = str(uuid4())
    binding = {
        k: record[k]
        for k in (
            "definitionId",
            "definitionVersion",
            "definitionSha256",
            "descriptorVersion",
            "descriptorSha256",
        )
    }
    prepared = client.request(
        "query.execution.prepare",
        {
            "projectId": project,
            "operationId": operation,
            "definitionBinding": binding,
            "visibleDraft": record["draft"],
            "selection": {"kind": "current"},
        },
    )
    query_start = time.perf_counter_ns()
    accepted = client.request(
        "job.create",
        {
            "projectId": project,
            "operationId": operation,
            "capability": "query.execute",
            "input": prepared["input"],
            "confirmationRef": None,
        },
    )
    job = _prepared_job(client, project, accepted)
    worker_outer = {
        "elapsedNs": time.perf_counter_ns() - query_start,
        "boundary": (
            "actual query job.create request to terminal job.get; "
            "includes dispatch/poll/persistence"
        ),
        "workerPid": None,
        "phaseMemory": None,
        "reason": (
            "existing public Job wire supplies no worker PID or child-internal phase observations"
        ),
    }
    return {
        "created": created,
        "openedBlank": opened,
        "project": project,
        "commits": commits,
        "current": current,
        "record": record,
        "prepared": prepared,
        "queryJob": job,
        "actualQueryJobOuter": worker_outer,
    }


def _prepared_timed(action):
    tracemalloc.reset_peak()
    before, start = tracemalloc.get_traced_memory()[0], time.perf_counter_ns()
    value = action()
    elapsed = time.perf_counter_ns() - start
    current, peak = tracemalloc.get_traced_memory()
    return value, {
        "elapsedNs": elapsed,
        "pythonBytesBefore": before,
        "pythonBytesAfter": current,
        "pythonBytesPeak": peak,
        "processLifetimeHighWaterRssBytes": high_water_rss(),
    }


def _prepared_execute(request, expected):
    import inspect
    import sys
    import types
    from pathlib import Path

    from ontolearn_engine import semantic, semantic_execution, semantic_scopes
    from ontolearn_engine.resources import CONTRACT

    _prepared_require(sys.getprofile() is None, "existing-profiler")
    functions = (semantic_execution.execute_request, semantic_execution._graph, semantic.query)
    sources = []
    for module in (semantic_execution, semantic, semantic_scopes):
        raw = Path(module.__file__).read_bytes()
        pin = _PREPARED_SEMANTIC_PINS[Path(module.__file__).name]
        _prepared_require((len(raw), hashlib.sha256(raw).hexdigest()) == pin, "semantic-source-pin")
        sources.append({"path": str(Path(module.__file__).resolve()), **_prepared_pin(raw)})
    for function in functions:
        _prepared_require(
            type(function) is types.FunctionType
            and not function.__code__.co_flags
            & (inspect.CO_GENERATOR | inspect.CO_COROUTINE | inspect.CO_ASYNC_GENERATOR)
            and Path(function.__code__.co_filename).resolve()
            == Path(sys.modules[function.__module__].__file__).resolve(),
            "unsupported-profile-target",
        )
    root_code, graph_code, query_code = (function.__code__ for function in functions)
    phases, active, root, failures, counts = [], None, None, [], [0, 0, 0]
    target_graphs = [
        request["snapshot"]["state"]["facts"],
        [
            t
            for d in request["snapshot"]["state"]["definitions"]
            if d["layer"] == "ontology"
            for t in json.loads(d["payload"])["triples"]
        ],
    ]
    graph_keys = [
        sorted([t["subject"], t["predicate"], t["object"]] for t in values)
        for values in target_graphs
    ]

    def observer(frame, event, returned):
        nonlocal active, root
        # Never turn an observer bug into an exception in the producer's body.
        try:
            if frame.f_code is root_code:
                if event == "call":
                    counts[0] += 1
                    if root is not None:
                        raise _PreparedFault("nested-execute-target")
                    root = frame
                elif event == "return":
                    if root is not frame or returned is None or active is not None:
                        raise _PreparedFault("execute-abnormal-return")
                    root = None
                return
            if frame.f_code not in (graph_code, query_code) or root is None:
                return
            if frame.f_back is not root:
                raise _PreparedFault("unexpected-target-parent")
            if event == "call":
                if active is not None:
                    raise _PreparedFault("overlapping-target-frame")
                ordinal = len(phases)
                required = graph_code if ordinal < 2 else query_code
                if ordinal > 2 or frame.f_code is not required:
                    raise _PreparedFault("target-call-order")
                tracemalloc.reset_peak()
                active = (
                    frame,
                    ordinal,
                    tracemalloc.get_traced_memory()[0],
                    time.perf_counter_ns(),
                )
            elif event == "return":
                end = time.perf_counter_ns()
                current, peak = tracemalloc.get_traced_memory()
                if active is None or active[0] is not frame or returned is None:
                    raise _PreparedFault("target-abnormal-return")
                _, ordinal, before, start = active
                active = None
                phase = {
                    "phase": ("factsBuild", "ontologyBuild", "completeQuery")[ordinal],
                    "elapsedNs": end - start,
                    "pythonBytesBefore": before,
                    "pythonBytesAfter": current,
                    "pythonBytesPeak": peak,
                    "processLifetimeHighWaterRssBytes": high_water_rss(),
                    "normalReturn": True,
                    "sameFrame": True,
                }
                if ordinal < 2:
                    actual = sorted([str(s), str(p), o.n3()] for s, p, o in returned)
                    if actual != graph_keys[ordinal] or len(returned) != len(graph_keys[ordinal]):
                        raise _PreparedFault("graph-identity-count")
                    phase.update(triples=len(returned), graphRecordsSha256=digest(actual))
                    counts[1] += 1
                else:
                    if returned != expected:
                        raise _PreparedFault("complete-query-result-mismatch")
                    phase.update(
                        variables=returned["variables"],
                        rows=returned["rows"],
                        resultSha256=digest(returned),
                    )
                    counts[2] += 1
                phases.append(phase)
        except BaseException as error:
            if not failures:
                failures.append({"type": type(error).__name__, "reason": str(error)})

    previous = sys.getprofile()
    start = time.perf_counter_ns()
    try:
        sys.setprofile(observer)
        result = semantic_execution.execute_request(
            request, error_catalog=CONTRACT.ERROR_CATALOG, error_schema=CONTRACT.DOCUMENT
        )
    finally:
        sys.setprofile(previous)
    elapsed = time.perf_counter_ns() - start
    _prepared_require(
        not failures
        and root is None
        and active is None
        and counts == [1, 2, 1]
        and len(phases) == 3,
        "measurement-observer-incomplete",
        {
            "failures": failures,
            "counts": counts,
            "phases": phases,
            "openRoot": root is not None,
            "openPhase": active is not None,
        },
    )
    _prepared_require(result["payload"]["query"] == expected, "producer-complete-query-mismatch")
    return result, {
        "executeElapsedNs": elapsed,
        "executePeakBytes": None,
        "executePeakReason": "sibling phase reset_peak prevents a whole-execute peak",
        "phases": phases,
        "counts": counts,
        "source": sources,
        "profileRestored": sys.getprofile() is previous,
    }


def measure_prepared(scale, trial, input_path, expected_path):
    """Private real format3 workflow + instrumented same-process original core.

    This is an observation, not D2/capacity/physical-host qualification. Expected
    material is consumed only for validation, never used to construct results.
    """
    import os
    import sys
    from pathlib import Path

    from ontolearn_engine.job_store import JobStore
    from ontolearn_engine.resources import CONTRACT, LOCK_FILE, REGISTRY_HASH, semantic_identity

    _prepared_require(sys.getprofile() is None, "existing-profiler")
    _prepared_require(not tracemalloc.is_tracing(), "existing-tracemalloc")
    data, expected, input_pins = _prepared_inputs(scale, input_path, expected_path)
    report = {
        "schema": "t01.private.prepared-gbase-probe/1",
        "scale": scale,
        "trial": trial,
        "status": "measurement-failed",
        "inputPins": input_pins,
        "resourceQuery": {"bytes": 162, "sha256": _PREPARED_RESOURCE_SHA},
        "managedQuery": {"bytes": 161, "sha256": _PREPARED_MANAGED_SHA},
        "expectedQuery": expected,
        "actualMeasurementCommand": None,
        "probePid": os.getpid(),
        "runtime": {
            "python": sys.version,
            "executable": sys.executable,
            "sqlite": sqlite3.sqlite_version,
            "dependencies": {name: version(name) for name in ("rdflib", "pyshacl", "owlrl")},
            "implementation": semantic_identity(),
            "registryHash": REGISTRY_HASH,
            "lock": {"path": str(LOCK_FILE), **_prepared_pin(LOCK_FILE.read_bytes())},
        },
        "device": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "cpu": platform.processor() or None,
            "cpuCount": os.cpu_count(),
            "cpuReason": None if platform.processor() else "platform.processor supplied no value",
        },
        "limitations": [
            "instrumented same-process producer-core; profile/tracemalloc overhead included",
            "phase peak is absolute Python tracked allocation, not increment or RSS",
            "RSS is RUSAGE_SELF lifetime highwater; no phase/worker/App memory claim",
            "first core call in probe vs same-process repeat; OS cache uncontrolled",
            "prior retained results remain alive during warm call",
            "objects allocated before tracemalloc.start are outside tracked absolute peaks",
            "worker PID/internal memory not supplied; "
            "package and 8GB reference-host evidence absent",
        ],
    }
    code_root = Path(__file__).resolve().parent
    source_members = (
        "storage_probe.py",
        "semantic_execution.py",
        "semantic.py",
        "semantic_scopes.py",
        "coordinator.py",
        "job_store.py",
        "storage.py",
        "protocol.py",
        "resources.py",
        "__main__.py",
        "worker.py",
        "project/mainline.py",
        "project/project_lifecycle.py",
        "project/domain_changesets.py",
        "project/query_definitions.py",
    )
    report["runtime"]["source"] = [
        {
            "relativePath": name,
            "path": str(code_root / name),
            **_prepared_pin((code_root / name).read_bytes()),
        }
        for name in source_members
    ]
    report["runtime"]["executablePin"] = _prepared_pin(Path(sys.executable).resolve().read_bytes())
    report["runtime"]["executableResolved"] = str(Path(sys.executable).resolve())
    try:
        report["device"]["ramBytes"] = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
        report["device"]["ramReason"] = None
    except (ValueError, OSError, AttributeError):
        report["device"].update(
            ramBytes=None, ramReason="sysconf physical page information unavailable"
        )
    store, client = None, None
    with TemporaryDirectory(prefix="t01-d2-prepared-") as directory:
        try:
            database = Path(directory) / "prepared.sqlite"
            setup_start = time.perf_counter_ns()
            client = _PreparedSession(database)
            workflow = _prepared_setup(client, data)
            client.finish()
            report["workflow"], report["wire"] = workflow, client.evidence()
            report["setupElapsedNs"] = time.perf_counter_ns() - setup_start
            reopen_start = time.perf_counter_ns()
            store = JobStore(database, contract=CONTRACT, target_format=3)
            project, job = workflow["project"], workflow["queryJob"]
            for committed in workflow["commits"]:
                _prepared_require(
                    store.get_job(project, committed["job"]["jobId"]) == committed["job"]
                    and store.operation_get(project, committed["job"]["operationId"])
                    == committed["marker"],
                    "reopened-commit-binding",
                )
                store.result_get(project, committed["receipt"]["resultId"])
            _prepared_require(store.get_job(project, job["jobId"]) == job, "reopened-query-job")
            context = store.job_context(job["jobId"])
            metadata, persisted_payload = store.semantic_result(
                project, job["resultRef"]["resultId"]
            )
            persisted_rows = store.result(metadata["resultId"])["payload"]
            report["reopenAuthenticationElapsedNs"] = time.perf_counter_ns() - reopen_start
            tracemalloc.start()
            snapshot, snapshot_measure = _prepared_timed(
                lambda: store.load_snapshot(job["inputSnapshotId"])
            )
            _prepared_require(
                snapshot == context["snapshot"] and digest(snapshot) == job["inputSnapshotId"],
                "snapshot-accepted-context-binding",
            )
            actual_facts = sorted(
                [t["subject"], t["predicate"], t["object"]] for t in snapshot["state"]["facts"]
            )
            wanted_facts = sorted(
                [t["subject"], t["predicate"], t["object"]] for t in data["assertedFacts"]
            )
            definitions = snapshot["state"]["definitions"]
            ontologies = [json.loads(d["payload"]) for d in definitions if d["layer"] == "ontology"]
            ontology = [t for value in ontologies for t in value["triples"]]
            query_defs = [json.loads(d["payload"]) for d in definitions if d["layer"] == "query"]
            _prepared_require(
                actual_facts == wanted_facts
                and len(actual_facts) == 18 * scale
                and len(definitions) == 11
                and len(ontologies) == 10
                and sorted(ontology, key=_prepared_bytes)
                == sorted(data["ontology"], key=_prepared_bytes)
                and len(query_defs) == 1
                and query_defs[0]["text"] == data["queryText"].removesuffix("\n"),
                "full-reopened-input-mismatch",
            )
            request, request_measure = _prepared_timed(
                lambda: store.prepare_query_request(
                    project,
                    job["input"],
                    context["parameters"],
                    snapshot,
                    job["implementation"],
                    None,
                )
            )
            _prepared_require(request == context["queryRequest"], "accepted-query-request-mismatch")
            first, first_measure = _prepared_execute(request, expected)
            warm, warm_measure = _prepared_execute(request, expected)

            # Row UUIDs are fresh projection identities; all ordinals/cells must match.
            def cells(rows):
                return [{"ordinal": row["ordinal"], "cells": row["cells"]} for row in rows]

            _prepared_require(
                first["payload"] == warm["payload"] == persisted_payload
                and persisted_payload["query"] == expected
                and cells(first["rows"]) == cells(warm["rows"]) == cells(persisted_rows),
                "complete-payload-and-projection-binding",
            )
            report.update(
                status="observed",
                snapshotId=job["inputSnapshotId"],
                snapshotSha256=digest(snapshot),
                finalCounts={
                    "facts": len(actual_facts),
                    "ontology": len(ontology),
                    "definitions": len(definitions),
                },
                measurement={
                    "snapshotLoad": snapshot_measure,
                    "requestConstruction": request_measure,
                    "firstCoreCall": first_measure,
                    "sameProcessRepeat": warm_measure,
                },
                actualQuery=first["payload"]["query"],
                producerFirst=first,
                producerWarm=warm,
                persisted={
                    "metadata": metadata,
                    "payload": persisted_payload,
                    "rows": persisted_rows,
                },
                condition=(
                    "SQLite reopened after real Coordinator natural exit; OS cache uncontrolled"
                ),
            )
        except Exception as error:
            report["failure"] = {
                "type": type(error).__name__,
                "reason": error.reason if isinstance(error, _PreparedFault) else str(error),
                "detail": error.detail
                if isinstance(error, _PreparedFault)
                else getattr(error, "error", None),
            }
            if client is not None:
                try:
                    client.abort()
                except Exception as cleanup_error:
                    report["cleanupFailure"] = {
                        "type": type(cleanup_error).__name__,
                        "reason": str(cleanup_error),
                    }
                report["wire"] = client.evidence()
        finally:
            try:
                if store is not None:
                    store.close()
            finally:
                if tracemalloc.is_tracing():
                    tracemalloc.stop()
    return report


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", type=int, default=1)
    parser.add_argument("--trial", type=int, default=0)
    parser.add_argument("--prepared-gbase", action="store_true")
    parser.add_argument("--prepared-input")
    parser.add_argument("--prepared-expected")
    args = parser.parse_args()
    if args.prepared_gbase:
        if (
            args.scale not in _PREPARED_PAIRS
            or not args.prepared_input
            or not args.prepared_expected
        ):
            parser.error("prepared G-base requires fixed 1/10/100 input+expected pair")
        try:
            result = measure_prepared(
                args.scale, args.trial, args.prepared_input, args.prepared_expected
            )
        except _PreparedFault as error:
            result = {
                "status": "measurement-failed",
                "failure": {"reason": error.reason, "detail": error.detail},
            }
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        if result["status"] != "observed":
            raise SystemExit(1)
        return
    if args.prepared_input is not None or args.prepared_expected is not None:
        parser.error("prepared paths require explicit --prepared-gbase")
    if not 1 <= args.scale <= 1000:
        parser.error("synthetic scale must be 1..1000")
    print(json.dumps(measure(args.scale, args.trial), ensure_ascii=False))


if __name__ == "__main__":
    main()
