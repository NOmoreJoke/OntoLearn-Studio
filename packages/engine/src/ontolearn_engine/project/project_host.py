"""Private bounded reads on a trusted host's existing Store3 connection.

No path, connection factory, permission grant, RPC or persistent cursor. Catalog
pages are copies of one finite snapshot; workspace reads never mint evidence.
The owner serializes calls on the Store's owning thread and closes this reader
before relinquishing the Store/location capability.
"""

import json
import math
import re
import secrets
import sqlite3
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, fields
from uuid import uuid4

from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project import format3
from ontolearn_engine.project.applications import uuid_ref
from ontolearn_engine.storage import canonical


class HostReadFault(ValueError):
    """Finite private reasons only; no underlying exception or content escapes."""

    def __init__(self, reason: str):
        if reason not in {"input", "state", "structure", "limit", "cursor", "expired", "missing"}:
            raise ValueError("Invalid host read reason")
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class ReadLimits:
    # Engineering refusal bounds, not a capacity/performance acceptance claim.
    projects: int = 256
    schema_bytes: int = 131072
    validation_rows: int = 16384
    validation_bytes: int = 33554432
    validation_work: int = 536870912
    metadata_bytes: int = 4096
    identity_bytes: int = 512
    draft_bytes: int = 262144
    workspace_bytes: int = 278528
    catalog_row_bytes: int = 8192
    snapshot_bytes: int = 1048576
    page_items: int = 64
    page_bytes: int = 131072
    snapshots: int = 4
    retained_bytes: int = 8388608
    ttl_seconds: int = 60

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if type(value) is not int or not 1 <= value <= field.default:
                raise HostReadFault("input")


@dataclass(frozen=True)
class _Catalog:
    identity: str
    items: tuple[bytes, ...]
    page_size: int
    offset: int
    expires: float
    charge: int


class ProjectHostReader:
    def __init__(
        self,
        store: JobStore,
        *,
        limits: ReadLimits | None = None,
        clock: Callable[[], float] = time.monotonic,
    ):
        if not isinstance(store, JobStore) or store._target_format != 3:
            raise HostReadFault("state")
        if limits is not None and type(limits) is not ReadLimits or not callable(clock):
            raise HostReadFault("input")
        self._store = store
        self._limits = limits or ReadLimits()
        self._clock = clock
        self._last_now: float | None = None
        self._reader_id = uuid4().hex
        self._cursor_sequence = 0
        self._catalogs: dict[str, _Catalog] = {}
        self._closed = False

    def close(self) -> None:
        """Release only this reader's memory; never close the host's Store."""
        self._catalogs.clear()
        self._closed = True

    def _now(self) -> float:
        try:
            value = self._clock()
            if type(value) not in (float, int) or not math.isfinite(value):
                raise ValueError
            value = float(value)
            if self._last_now is not None and value < self._last_now:
                raise ValueError
        except Exception:
            self._catalogs.clear()
            raise HostReadFault("state") from None
        self._last_now = value
        return value

    def _ready(self) -> None:
        if self._closed:
            raise HostReadFault("state")

    def _purge(self, now: float) -> None:
        for token, catalog in list(self._catalogs.items()):
            if now >= catalog.expires:
                del self._catalogs[token]

    @staticmethod
    def _encoded(value, maximum: int) -> bytes:
        try:
            result = canonical(value).encode("utf-8")
        except (ValueError, TypeError, OverflowError, RecursionError):
            raise HostReadFault("structure") from None
        if len(result) > maximum:
            raise HostReadFault("limit")
        return result

    def _identity(self, value) -> None:
        if type(value) is not str or not value or len(value) > self._limits.identity_bytes:
            raise HostReadFault("input")
        try:
            if len(value.encode("utf-8")) > self._limits.identity_bytes:
                raise HostReadFault("input")
        except UnicodeError:
            raise HostReadFault("input") from None

    @contextmanager
    def _read(self):
        self._ready()
        try:
            # Store._read joins an existing transaction. Reject it so no caller's
            # uncommitted writes can become a catalog/workspace snapshot.
            if self._store._db.in_transaction:
                raise HostReadFault("state")
            with self._store._read():
                if self._store._db.execute("PRAGMA user_version").fetchone()[0] != 3:
                    raise HostReadFault("state")
                yield
        except HostReadFault:
            raise
        except (ValueError, KeyError, TypeError, OverflowError, RecursionError, sqlite3.Error):
            raise HostReadFault("structure") from None

    def _preflight(self, *, _mainline_core_material: bool = False) -> int:
        if type(_mainline_core_material) is not bool:
            raise HostReadFault("input")
        db, limits = self._store._db, self._limits
        schema = db.execute(
            "SELECT count(*),coalesce(sum(length(CAST(sql AS BLOB))),0) FROM sqlite_master"
        ).fetchone()
        if schema[0] > 256 or schema[1] > limits.schema_bytes:
            raise HostReadFault("limit")
        tables = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        if len(tables) > 64:
            raise HostReadFault("limit")
        total_rows = total_bytes = scan_bytes = 0
        counts = {}
        plan_sizes = None
        # Default readers retain the original all-table material bound. The
        # mainline core reader additionally distinguishes SQL scans from decoded
        # material; both passes remain prepaid. Identifiers come from SQLite.
        for table in tables:
            quoted = '"' + table.replace('"', '""') + '"'
            columns = db.execute(f"PRAGMA table_info({quoted})").fetchall()
            if len(columns) > 32:
                raise HostReadFault("limit")
            sizes = "+".join(
                'coalesce(length(CAST("' + row[1].replace('"', '""') + '" AS BLOB)),0)'
                for row in columns
            )
            count, size = db.execute(
                f"SELECT count(*),coalesce(sum({sizes}),0) FROM {quoted}"
            ).fetchone()
            counts[table] = count
            total_rows += count
            scan_bytes += size
            if not _mainline_core_material or table not in {"job_blobs", "job_plans"}:
                total_bytes += size
            if table == "job_plans":
                plan_sizes = sizes
            if total_rows > limits.validation_rows or total_bytes > limits.validation_bytes:
                raise HostReadFault("limit")
        count = counts.get("projects", 0)
        # Conservative repeated-decode work guard for immutable histories.
        # Not a timer or an assertion of exact CPU/RSS usage.
        work = scan_bytes * (1 + counts.get("app_operations", 0) + counts.get("snapshots", 0))
        if count > limits.projects or work > limits.validation_work:
            raise HostReadFault("limit")
        if _mainline_core_material:
            # All claim contexts and confirmations were bounded in pass one.
            # Only application-authorized plans can be materialized by _history;
            # unconsumed preview plans/blobs are not decoded by the core reader.
            if plan_sizes is None or "operation_claims" not in counts:
                raise HostReadFault("structure")
            plan_bytes = db.execute(
                f"SELECT coalesce(sum({plan_sizes}),0) FROM job_plans WHERE ref IN ("
                "SELECT CASE WHEN json_valid(context) THEN "
                "json_extract(context,'$.request.authorization.preparedPlanRef') END "
                "FROM operation_claims WHERE kind='application')"
            ).fetchone()[0]
            if total_bytes + plan_bytes > limits.validation_bytes:
                raise HostReadFault("limit")
        return count

    def _validate(self) -> None:
        # These are existing read-only validators, not snapshot()/project_get().
        format3.validate(self._store)
        db = self._store._db
        mappings = db.execute("SELECT public,internal FROM public_projects").fetchall()
        projects = {row[0] for row in db.execute("SELECT id FROM projects")}
        apps = {row[0] for row in db.execute("SELECT project FROM app_projects")}
        if (
            len(mappings) != len(projects)
            or {row[1] for row in mappings} != projects
            or projects != apps
            or len({row[0] for row in mappings}) != len(mappings)
            or any(not uuid_ref(row[0]) for row in mappings)
        ):
            raise HostReadFault("structure")
        for internal in projects:
            self._identity(internal)

    def _row(self, row) -> dict:
        metadata = json.loads(row["metadata"])
        self._encoded(metadata, self._limits.metadata_bytes)
        return {
            "projectId": row["public"],
            "domainRevision": row["revision"],
            "metadataVersion": row["metadata_version"],
            "metadata": metadata,
            "operationSequence": row["operation_sequence"],
            "checkpointRef": row["checkpoint"],
        }

    def catalog_start(self, *, page_size: int = 64) -> dict:
        self._ready()
        if type(page_size) is not int or not 1 <= page_size <= self._limits.page_items:
            raise HostReadFault("input")
        now = self._now()
        self._purge(now)
        if len(self._catalogs) >= self._limits.snapshots:
            raise HostReadFault("limit")
        with self._read():
            count = self._preflight()
            # Reserve a complete worst-case copy plus one token/state, before
            # decoding/validating/freezing; no partial snapshot is installed.
            charge = 768 + count * (self._limits.catalog_row_bytes + 64)
            if (
                charge + sum(c.charge for c in self._catalogs.values())
                > self._limits.retained_bytes
            ):
                raise HostReadFault("limit")
            self._validate()
            rows = self._store._db.execute(
                "SELECT u.public,p.revision,a.metadata_version,a.metadata,"
                "a.operation_sequence,a.checkpoint FROM public_projects u "
                "JOIN projects p ON p.id=u.internal JOIN app_projects a ON a.project=p.id "
                "ORDER BY u.public COLLATE BINARY"
            )
            items = tuple(
                self._encoded(self._row(row), self._limits.catalog_row_bytes) for row in rows
            )
            if (
                len(items) != count
                or sum(map(len, items)) + 2 + count > self._limits.snapshot_bytes
            ):
                raise HostReadFault("limit")
        catalog = _Catalog(
            str(uuid4()), items, page_size, 0, now + self._limits.ttl_seconds, charge
        )
        if self._now() >= catalog.expires:
            raise HostReadFault("expired")
        return self._page(catalog)

    def _page(self, catalog: _Catalog) -> dict:
        end = min(catalog.offset + catalog.page_size, len(catalog.items))
        next_token = None
        if end < len(catalog.items):
            if self._cursor_sequence >= format3.MAX_VERSION:
                raise HostReadFault("limit")
            # Sequence is never reused, even on a failed page/new catalog. Thus
            # repeated entropy cannot resurrect an earlier consumed token, and
            # no unbounded consumed-token set is needed.
            self._cursor_sequence += 1
            try:
                suffix = secrets.token_urlsafe(32)
                if (
                    type(suffix) is not str
                    or len(suffix) != 43
                    or re.fullmatch(r"[A-Za-z0-9_-]{43}", suffix) is None
                ):
                    raise ValueError
            except Exception:
                raise HostReadFault("state") from None
            next_token = f"{self._reader_id}.{self._cursor_sequence:016x}.{suffix}"
        page = {
            "catalogVersion": 1,
            "snapshotId": catalog.identity,
            "items": [json.loads(item) for item in catalog.items[catalog.offset : end]],
            "total": len(catalog.items),
            "offset": catalog.offset,
            "nextCursor": next_token,
        }
        self._encoded(page, self._limits.page_bytes)
        if next_token is not None:
            self._catalogs[next_token] = _Catalog(
                catalog.identity,
                catalog.items,
                catalog.page_size,
                end,
                catalog.expires,
                catalog.charge,
            )
        return page

    def _cursor(self, cursor: str) -> tuple[str, _Catalog]:
        self._ready()
        if (
            type(cursor) is not str
            or len(cursor) != 93
            or re.fullmatch(r"[0-9a-f]{32}\.[0-9a-f]{16}\.[A-Za-z0-9_-]{43}", cursor) is None
            or cursor[:32] != self._reader_id
        ):
            raise HostReadFault("cursor")
        catalog = self._catalogs.get(cursor)
        now = self._now()
        self._purge(now)
        if catalog is None:
            raise HostReadFault("cursor")
        if now >= catalog.expires:
            raise HostReadFault("expired")
        return cursor, catalog

    def catalog_next(self, cursor: str) -> dict:
        token, catalog = self._cursor(cursor)
        # Consume before page construction: failed later pages release the whole
        # snapshot, and replay/cross-reader/forged tokens cannot advance it.
        del self._catalogs[token]
        return self._page(catalog)

    def catalog_cancel(self, cursor: str) -> None:
        token, _ = self._cursor(cursor)
        del self._catalogs[token]

    def workspace(self, project_id: str, *, editor: str) -> dict:
        self._ready()
        if type(project_id) is not str or not uuid_ref(project_id):
            raise HostReadFault("input")
        self._identity(editor)
        with self._read():
            self._preflight()
            self._validate()
            row = self._store._db.execute(
                "SELECT u.public,u.internal,p.revision,a.metadata_version,a.metadata,"
                "a.operation_sequence,a.checkpoint FROM public_projects u "
                "JOIN projects p ON p.id=u.internal JOIN app_projects a ON a.project=p.id "
                "WHERE u.public=?",
                (project_id,),
            ).fetchone()
            if row is None:
                raise HostReadFault("missing")
            # Complete histories/current heads were validated in this same read
            # transaction. Read existing proof, never create a snapshot/checkpoint.
            checkpoint = self._store._db.execute(
                "SELECT payload FROM app_checkpoints WHERE project=? AND id=?",
                (row["internal"], row["checkpoint"]),
            ).fetchone()
            if checkpoint is None:
                raise HostReadFault("structure")
            proof = json.loads(checkpoint[0])
            draft_row = self._store._db.execute(
                "SELECT generation,present,bound_revision,payload,content_hash FROM app_drafts "
                "WHERE project=? AND editor=?",
                (row["internal"], editor),
            ).fetchone()
            draft = {"editor": editor, "state": "missing"}
            if draft_row is not None:
                payload = draft_row["payload"]
                if payload is not None and len(payload.encode("utf-8")) > self._limits.draft_bytes:
                    raise HostReadFault("limit")
                draft = {
                    "editor": editor,
                    "state": "present" if draft_row["present"] else "tombstone",
                    "generation": draft_row["generation"],
                    "present": bool(draft_row["present"]),
                    "boundDomainRevision": draft_row["bound_revision"],
                    "contentHash": draft_row["content_hash"],
                    "content": json.loads(payload) if draft_row["present"] else None,
                }
            result = {
                "workspaceVersion": 1,
                **self._row(row),
                "inputSnapshotId": proof["domainSnapshotRef"],
                "draft": draft,
            }
            self._encoded(result, self._limits.workspace_bytes)
            return result
