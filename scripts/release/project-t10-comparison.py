"""Read-only Wave 4 T10 package to ``t11-comparison-v3`` projection.

Strictly offline: reads a real ``ontolearn-project-package-v1`` ZIP
(``manifest.json`` plus ``data/*.json`` members), verifies every structural
rule the frozen format defines (member paths, sizes, SHA-256 hashes, option
isolation, core-role completeness) and emits a deterministic, honest
``t11-comparison-v3`` JSON document aligned with ``scripts/release/verify.mts``
(``comparisonSchema``):

* carried layers only - ``facts``/``definitions``/``ownership``/``mappingState``
  from the package members plus ``history``/``agentSessions`` when selected;
* layers the v1 format never carries (``queries``, ``results``, ``rounds``,
  ``rawSources``, ``undo``, ``derivedResults``) are projected as strictly empty
  arrays - never fabricated;
* ``capabilities``/``dependencies`` mirror the exporter's own portability
  claims (``transfer/service.py``): raw sources and scenario payloads are
  never packaged, so ``rerunOriginalMapping``/``replaySandbox`` stay ``false``
  with ``mappingSources: missing`` and ``replaySemantics: missing``;
* template packages (or any package without current facts/ownership) project
  ``restoreCurrent: false`` per selection-comparison-v3 and exit non-zero,
  because such a projection can never satisfy the strict schema.

Exit codes: ``0`` restorable full projection; ``1`` honest refusal (template,
missing current layers, unfulfillable ``g6-conflict``) with the projection
still written; ``2`` usage or invalid-package failures with a fixed
single-line stderr code that never echoes package bytes.
"""

import argparse
import hashlib
import io
import json
import os
import stat
import sys
import zipfile
import zlib
from pathlib import Path

FORMAT_VERSION = "ontolearn-project-package-v1"
COMPARISON_FORMAT = "t11-comparison-v3"
CASES = ("current-state", "g6-conflict")
MAX_ARCHIVE = 40 * 1024 * 1024
MAX_MEMBER = 8 * 1024 * 1024
MAX_MANIFEST = 64 * 1024
ROLE_PATHS = {
    "definitions": "data/definitions.json",
    "assertions": "data/assertions.json",
    "ownership": "data/ownership.json",
    "checkpoint": "data/checkpoint.json",
    "agent-session": "data/agent-session.json",
    "raw-source": "data/raw-source.json",
    "derived": "data/derived.json",
    "history": "data/history.json",
}
CORE_ROLES = frozenset({"definitions", "assertions", "ownership", "checkpoint"})
DEFINITION_LAYERS = frozenset(
    {"ontology", "mapping", "constraint", "rule", "behavior", "scenario", "query", "model"}
)
OPTION_ROLES = {
    "agentSessions": "agent-session",
    "rawSources": "raw-source",
    "derived": "derived",
    "history": "history",
}
MANIFEST_KEYS = frozenset(
    {
        "formatVersion",
        "kind",
        "dbFormatVersion",
        "checkpointSchemaVersion",
        "applicationStateVersion",
        "minReaderVersion",
        "minWriterVersion",
        "options",
        "files",
    }
)
G6_LAYERS = ("facts", "definitions", "ownership", "mappingState", "queries", "results")
LAYERS = (
    "facts",
    "definitions",
    "ownership",
    "mappingState",
    "queries",
    "results",
    "derivedResults",
    "history",
    "rounds",
    "rawSources",
    "agentSessions",
    "undo",
)
FACT_FIELDS = {"id", "subject", "predicate", "object", "owner", "sourceRow", "managedValue"}
DEFAULT_PROJECT_ID = "t10-package"


class ProjectionError(Exception):
    """Fixed private code plus the process exit status it maps onto."""

    def __init__(self, code, status):
        super().__init__(code)
        self.code = code
        self.status = status


def _require(condition, code, status=2):
    if not condition:
        raise ProjectionError(code, status)


def _json_value(payload, code):
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeError, ValueError, RecursionError):
        raise ProjectionError(code, 2) from None


def _json_object(payload, code):
    value = _json_value(payload, code)
    _require(isinstance(value, dict), code)
    return value


def _read_package_bytes(package_path):
    try:
        resolved = Path(package_path).resolve(strict=True)
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
        fd = os.open(resolved, flags)
    except OSError:
        raise ProjectionError("PACKAGE_UNREADABLE", 2) from None
    try:
        st = os.fstat(fd)
        _require(stat.S_ISREG(st.st_mode), "PACKAGE_SHAPE")
        _require(st.st_size <= MAX_ARCHIVE, "ARCHIVE_LIMIT")
        _require(st.st_size >= 22, "PACKAGE_SHAPE")
        chunks = []
        total = 0
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            total += len(chunk)
            _require(total <= MAX_ARCHIVE, "ARCHIVE_LIMIT")
            chunks.append(chunk)
        _require(total == st.st_size, "PACKAGE_UNREADABLE")
        return b"".join(chunks)
    except OSError:
        raise ProjectionError("PACKAGE_UNREADABLE", 2) from None
    finally:
        os.close(fd)


def _read_member(archive, name, limit, code):
    try:
        with archive.open(name, "r") as stream:
            chunks = []
            total = 0
            while True:
                chunk = stream.read(65536)
                if not chunk:
                    break
                total += len(chunk)
                _require(total <= limit, "ARCHIVE_LIMIT")
                chunks.append(chunk)
            return b"".join(chunks)
    except KeyError:
        raise ProjectionError("UNLISTED_OR_MISSING_FILE", 2) from None
    except (zipfile.BadZipFile, zlib.error, OSError, ValueError, RuntimeError, EOFError):
        raise ProjectionError(code, 2) from None


def inspect_package(raw):
    """Bounded read-only structural inspection mirroring transfer/package.py."""
    _require(isinstance(raw, (bytes, bytearray)), "PACKAGE_SHAPE")
    _require(len(raw) <= MAX_ARCHIVE, "ARCHIVE_LIMIT")
    _require(len(raw) >= 22, "PACKAGE_SHAPE")
    try:
        archive = zipfile.ZipFile(io.BytesIO(bytes(raw)))
    except zipfile.BadZipFile:
        raise ProjectionError("PACKAGE_SHAPE", 2) from None
    with archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        names_set = set(names)
        _require(len(names) == len(names_set), "DUPLICATE_PATH")
        _require("manifest.json" in names_set, "MANIFEST_MISSING")
        for item in infos:
            _require(
                item.filename == "manifest.json" or item.filename in ROLE_PATHS.values(),
                "UNSAFE_PATH",
            )
            _require(not item.flag_bits & 1, "UNSAFE_ENTRY")
            _require(item.file_size <= MAX_MEMBER, "ARCHIVE_LIMIT")
        manifest_raw = _read_member(archive, "manifest.json", MAX_MANIFEST, "MANIFEST_SHAPE")
        _require(len(manifest_raw) <= MAX_MANIFEST, "ARCHIVE_LIMIT")
        manifest = _json_object(manifest_raw, "MANIFEST_SHAPE")
        _require(set(manifest) == MANIFEST_KEYS, "MANIFEST_SHAPE")
        _require(manifest["formatVersion"] == FORMAT_VERSION, "FORMAT_UNSUPPORTED")
        _require(manifest["kind"] in ("full", "template"), "KIND_INVALID")
        _require(
            all(
                type(manifest[key]) is int and manifest[key] >= 0
                for key in (
                    "dbFormatVersion",
                    "checkpointSchemaVersion",
                    "applicationStateVersion",
                    "minReaderVersion",
                    "minWriterVersion",
                )
            ),
            "MANIFEST_SHAPE",
        )
        options = manifest["options"]
        _require(
            isinstance(options, dict)
            and set(options) == set(OPTION_ROLES)
            and all(type(value) is bool for value in options.values()),
            "OPTIONS_INVALID",
        )
        files = manifest["files"]
        _require(isinstance(files, list) and 1 <= len(files) <= 8, "MANIFEST_SHAPE")
        roles, members = set(), {}
        for record in files:
            _require(
                isinstance(record, dict) and set(record) == {"path", "role", "size", "sha256"},
                "MANIFEST_SHAPE",
            )
            path, role = record["path"], record["role"]
            _require(isinstance(path, str) and ROLE_PATHS.get(role) == path, "ROLE_INVALID")
            _require(
                type(record["size"]) is int and record["size"] >= 0,
                "MANIFEST_SHAPE",
            )
            _require(record["size"] <= MAX_MEMBER, "ARCHIVE_LIMIT")
            _require(isinstance(record["sha256"], str), "MANIFEST_SHAPE")
            _require(role not in roles, "DUPLICATE_ROLE")
            for option, optional_role in OPTION_ROLES.items():
                _require(role != optional_role or options[option], "UNSELECTED_CONTENT")
            _require(path in names_set, "UNLISTED_OR_MISSING_FILE")
            payload = _read_member(archive, path, MAX_MEMBER, "ARCHIVE_INVALID")
            _require(len(payload) == record["size"], "SIZE_MISMATCH")
            _require(hashlib.sha256(payload).hexdigest() == record["sha256"], "HASH_MISMATCH")
            roles.add(role)
            members[path] = payload
        _require(names_set == {"manifest.json"} | set(members), "UNLISTED_OR_MISSING_FILE")
        _require(manifest["kind"] != "full" or CORE_ROLES <= roles, "FULL_CORE_MISSING")
        _require(manifest["kind"] != "template" or "definitions" in roles, "TEMPLATE_DEFINITIONS")
        # The projector only handles roles the v1 exporter actually produces.
        for role in ("raw-source", "derived"):
            _require(role not in roles, "ROLE_UNSUPPORTED")
        return manifest, members


def _checkpoint(members):
    if "data/checkpoint.json" not in members:
        return {}
    checkpoint = _json_object(members["data/checkpoint.json"], "MEMBER_SHAPE")
    _require(
        set(checkpoint) == {"domainRevision", "operationSequence", "metadata", "metadataVersion"}
        and type(checkpoint["domainRevision"]) is int
        and checkpoint["domainRevision"] >= 0,
        "MEMBER_SHAPE",
    )
    return checkpoint


def _facts_rows(members):
    facts = (
        _json_object(members["data/assertions.json"], "MEMBER_SHAPE").get("facts")
        if "data/assertions.json" in members
        else []
    )
    _require(isinstance(facts, list), "MEMBER_SHAPE")
    rows = []
    for fact in facts:
        _require(
            isinstance(fact, dict) and set(fact) == FACT_FIELDS and isinstance(fact["id"], str),
            "MEMBER_SHAPE",
        )
        rows.append(
            {
                "id": fact["id"],
                "payload": {
                    "subject": fact["subject"],
                    "predicate": fact["predicate"],
                    "object": fact["object"],
                },
            }
        )
    return rows


def _ownership_rows(fact_rows, members):
    """Per-fact ownership projection; only full packages carry assertions."""
    if "data/assertions.json" not in members:
        return []
    facts = _json_object(members["data/assertions.json"], "MEMBER_SHAPE").get("facts")
    _require(isinstance(facts, list), "MEMBER_SHAPE")
    return [
        {
            "id": fact["id"],
            "payload": {
                "fact": fact["id"],
                "owner": fact["owner"],
                "row": fact["sourceRow"],
                "managedValue": fact["managedValue"],
            },
        }
        for fact in facts
    ]


def _definitions_rows(members):
    definitions = (
        _json_object(members["data/definitions.json"], "MEMBER_SHAPE").get("definitions")
        if "data/definitions.json" in members
        else []
    )
    _require(isinstance(definitions, list), "MEMBER_SHAPE")
    rows = []
    for record in definitions:
        _require(
            isinstance(record, dict)
            and set(record) == {"layer", "id", "payload"}
            and isinstance(record["layer"], str)
            and record["layer"] in DEFINITION_LAYERS
            and isinstance(record["id"], str)
            and bool(record["id"])
            and isinstance(record["payload"], str),
            "MEMBER_SHAPE",
        )
        rows.append(
            {
                "id": f"{record['layer']}:{record['id']}",
                "payload": {
                    "layer": record["layer"],
                    "definition": _json_value(record["payload"].encode("utf-8"), "MEMBER_SHAPE"),
                },
            }
        )
    return rows


def _mapping_state_rows(members):
    mapping_state = (
        _json_object(members["data/ownership.json"], "MEMBER_SHAPE").get("mappingState")
        if "data/ownership.json" in members
        else {}
    )
    _require(isinstance(mapping_state, dict), "MEMBER_SHAPE")
    rows = []
    for owner in sorted(mapping_state):
        status = mapping_state[owner]
        _require(
            isinstance(owner, str)
            and owner
            and isinstance(status, dict)
            and set(status) == {"generatedVersion", "stale"},
            "MEMBER_SHAPE",
        )
        rows.append(
            {
                "id": owner,
                "payload": {
                    "mapping": owner,
                    "generatedVersion": status["generatedVersion"],
                    "stale": status["stale"],
                },
            }
        )
    return rows


def _history_rows(members):
    operations = (
        _json_object(members["data/history.json"], "MEMBER_SHAPE").get("operations")
        if "data/history.json" in members
        else []
    )
    _require(isinstance(operations, list), "MEMBER_SHAPE")
    rows = []
    for record in operations:
        _require(
            isinstance(record, dict)
            and set(record) == {"sequence", "operationId", "operationKind"}
            and type(record["sequence"]) is int
            and record["sequence"] >= 0
            and isinstance(record["operationId"], str)
            and isinstance(record["operationKind"], str),
            "MEMBER_SHAPE",
        )
        rows.append(
            {
                "id": f"history-{record['sequence']}",
                "payload": {
                    "sequence": record["sequence"],
                    "operationId": record["operationId"],
                    "operationKind": record["operationKind"],
                },
            }
        )
    return rows


def _agent_session_rows(members):
    learning = (
        _json_object(members["data/agent-session.json"], "MEMBER_SHAPE").get("learning")
        if "data/agent-session.json" in members
        else []
    )
    _require(isinstance(learning, list), "MEMBER_SHAPE")
    rows = []
    for record in learning:
        _require(
            isinstance(record, dict)
            and set(record) == {"attempt", "recordVersion", "course", "task", "payload"}
            and isinstance(record["attempt"], str)
            and type(record["recordVersion"]) is int
            and isinstance(record["course"], str)
            and isinstance(record["task"], str)
            and isinstance(record["payload"], str),
            "MEMBER_SHAPE",
        )
        rows.append(
            {
                "id": record["attempt"],
                "payload": {
                    "attempt": record["attempt"],
                    "recordVersion": record["recordVersion"],
                    "course": record["course"],
                    "task": record["task"],
                    "record": _json_value(record["payload"].encode("utf-8"), "MEMBER_SHAPE"),
                },
            }
        )
    return rows


def _check_rows(rows):
    seen = set()
    for row in rows:
        _require(
            isinstance(row, dict)
            and isinstance(row["id"], str)
            and 1 <= len(row["id"]) <= 512
            and row["id"] not in seen,
            "ROW_INVALID",
        )
        _require(
            isinstance(row["payload"], dict) and row["payload"] and "count" not in row["payload"],
            "ROW_INVALID",
        )
        seen.add(row["id"])


def build_projection(manifest, members, package_sha, case, project_id):
    """Deterministic honest projection; identical package bytes give identical output."""
    options = manifest["options"]
    checkpoint = _checkpoint(members)
    fact_rows = _facts_rows(members)
    ownership_rows = _ownership_rows(fact_rows, members)
    projection = {
        "format": COMPARISON_FORMAT,
        "comparisonCase": case,
        "projectId": project_id,
        "sourceSnapshotId": package_sha,
        "projectRevision": checkpoint.get("domainRevision", 0),
        "selection": {
            "currentDerived": options["derived"],
            "historicalRuns": options["history"],
            "rawSources": options["rawSources"],
            "agentSessions": options["agentSessions"],
            "priorUndo": False,
        },
        # v1 never packages raw sources or scenario payloads, so rerun/replay
        # stay false exactly like the exporter's own portability claims.
        "capabilities": {
            "restoreCurrent": bool(manifest["kind"] == "full" and fact_rows and ownership_rows),
            "rerunOriginalMapping": False,
            "replaySandbox": False,
        },
        "dependencies": {
            "mappingSources": "missing",
            "replayInputs": False,
            "replayConfiguration": False,
            "replaySemantics": "missing",
        },
        "facts": fact_rows,
        "definitions": _definitions_rows(members),
        "ownership": ownership_rows,
        "mappingState": _mapping_state_rows(members),
        "queries": [],
        "results": [],
        "derivedResults": [],
        "history": _history_rows(members) if options["history"] else [],
        "rounds": [],
        "rawSources": [],
        "agentSessions": _agent_session_rows(members) if options["agentSessions"] else [],
        "undo": [],
        "executionVersions": {
            "semantics": f"application-state-v{manifest['applicationStateVersion']}",
            "engine": f"db-format-v{manifest['dbFormatVersion']}",
            "lock": f"checkpoint-schema-v{manifest['checkpointSchemaVersion']}",
        },
    }
    for layer in LAYERS:
        _check_rows(projection[layer])
    return projection


def _refusal(projection):
    """The single honest reason this projection cannot be a valid v3 snapshot."""
    if not projection["capabilities"]["restoreCurrent"]:
        return "TEMPLATE_NOT_RESTORABLE"
    if projection["comparisonCase"] == "g6-conflict":
        for layer in G6_LAYERS:
            if not projection[layer]:
                return "G6_REQUIRED_LAYER"
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Project a read-only T10 ontolearn zip onto t11-comparison-v3."
    )
    parser.add_argument("--package", required=True)
    parser.add_argument("--case", default="current-state", choices=list(CASES))
    parser.add_argument("--output", required=True)
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    args = parser.parse_args(argv)
    try:
        project_id = args.project_id.strip()
        _require(1 <= len(project_id) <= 512, "USAGE_PROJECT_ID")
        raw = _read_package_bytes(args.package)
        manifest, members = inspect_package(raw)
        projection = build_projection(
            manifest, members, hashlib.sha256(raw).hexdigest(), args.case, project_id
        )
        Path(args.output).write_text(
            json.dumps(projection, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
            + "\n",
            encoding="utf-8",
        )
        refusal = _refusal(projection)
        if refusal:
            print(refusal, file=sys.stderr)
            return 1
        return 0
    except ProjectionError as error:
        print(error.code, file=sys.stderr)
        return error.status
    except (OSError, ValueError, RecursionError):
        print("PACKAGE_UNREADABLE", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
