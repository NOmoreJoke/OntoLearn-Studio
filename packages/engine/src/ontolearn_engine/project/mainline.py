"""Named services for the owned business3 stdio session and its selected project.

This is an application adapter, not a database resolver or domain dispatcher.
The process already owns the original JobStore lifetime lease. Wire callers
cannot supply a store, permission, scope, implementation, or read ticket.
"""

from contextlib import contextmanager
from dataclasses import dataclass, field
from uuid import uuid4

from ontolearn_engine.job_store import JobFault, fault
from ontolearn_engine.project.management import METHODS as MANAGEMENT_METHODS
from ontolearn_engine.project.ordinary_library import OrdinaryReadAuthority
from ontolearn_engine.project.project_host import HostReadFault, ProjectHostReader, ReadLimits
from ontolearn_engine.project.query_definitions import (
    METHODS as QUERY_METHODS,
)
from ontolearn_engine.project.query_definitions import (
    ProjectGetReadTicket,
    QueryDispatchAuthority,
    QueryRead,
    QueryReadBudget,
)
from ontolearn_engine.storage import Conflict, canonical

METHODS = frozenset(
    {
        "project.catalog",
        "project.create",
        "project.example.create",
        "project.draft.save",
        "project.open",
        "project.read",
        "project.ownership.detail",
    }
)
# First-chain rejection bounds, within the original reader's limits. These are
# not Q5 capacity, RSS, SQLite I/O, or whole-H acceptance claims.
# Admit the three persisted copies of a legal 420002-byte historical literal.
# 1.5 MiB also fits both prepaid project.get Store reads inside the unchanged
# 128 MiB retained book; 2 MiB would exceed that book. No other cap is raised.
METHODS = METHODS | MANAGEMENT_METHODS

READ_LIMITS = ReadLimits(validation_rows=4096, validation_bytes=1572864, validation_work=67108864)
HELD_BYTES = 134217728
HELD_OBJECTS = 1048576
READ_WORK = 536870912
MAX_REPLIES = 16


@dataclass(eq=False)
class _WriteHolding:
    # Actual writer aggregation holding, never a reply/read/permission ticket.
    scalar: int
    objects: int
    work: int


@dataclass(eq=False)
class _WriteScope:
    controlled: bool
    reply: object = None
    charged: object = None
    holding: object = None
    checked: bool = False


class _WriteAdmission:
    def __init__(self, store):
        from ontolearn_engine.job_store import JobStore

        if not isinstance(store, JobStore) or store.actual_format != 3:
            raise ValueError("Original business3 Store required")
        if store.contract.ERROR_CATALOG["maxEncodedBytes"] != 2048:
            raise ValueError("Terminal growth proof requires the pinned error contract")
        self.store, self.connection, self.lease = store, store._db, store._format3_lease
        self.owner = None
        self.active = None
        self.retained = []
        self.charged_reply = False
        self.transaction = None

    def holdings(self):
        return self.retained + ([self.active] if self.active is not None else [])

    def check_store(self):
        if (
            self.store._db is not self.connection
            or self.store._format3_lease is not self.lease
            or self.lease is None
            or self.store._read_admission is not self
        ):
            fault("PERMISSION_DENIED")

    def bind(self, owner):
        from ontolearn_engine.coordinator import Coordinator

        self.check_store()
        if (
            type(owner) is not MainlineHost
            or not isinstance(owner.actor, Coordinator)
            or owner.store is not self.store
            or owner.actor.store is not self.store
            or owner.actor.profile != "business3"
            or owner.actor.test_mode
            or owner.actor.mainline is not None
            or owner.actor.query_dispatch is not None
        ):
            fault("PERMISSION_DENIED")
        # Bootstrap can already own an uncertain writer before any host binds.
        # Neither a first owner nor a successor may adopt that as a clean book.
        if (
            self.active is not None
            or self.retained
            or self.transaction is not None
            or self.charged_reply
            or self.connection.in_transaction
        ):
            fault("PERMISSION_DENIED")
        previous = self.owner
        if previous is not None and not self._clean_predecessor(previous):
            fault("PERMISSION_DENIED")
        self.owner = owner

    def _clean_predecessor(self, owner):
        from ontolearn_engine.coordinator import Coordinator

        # Explicit close must have returned successfully. Merely fencing a
        # failed delivery also sets closed, but cannot release its authority.
        return (
            type(owner) is MainlineHost
            and isinstance(owner.actor, Coordinator)
            and owner._clean_close
            and owner.closed
            and not owner.hold
            and type(owner.reader) is _MainlineReader
            and owner.reader._owner is owner
            and owner.reader._store is self.store
            and owner.reader._closed
            and not owner.reader._catalogs
            and not owner.management.entries
            and owner.store is self.store
            and owner.actor.store is self.store
            and owner.actor.mainline is owner
            and owner.actor.ordinary is owner
            and owner.actor.query_dispatch is owner
            and owner.actor.profile == "business3"
            and not owner.actor.test_mode
            and owner.actor.session == owner.session
            and owner.actor.host_client_id == owner.host
            and owner.current is None
            and not owner.replies
            and not owner.actor._query_replies
            and owner.actor._query_project_get is None
            and not owner.actor.active
            and not owner.actor.tasks
            and not owner.actor.queued
        )

    def begin_transaction(self):
        self.check_store()
        if self.transaction is not None:
            # In particular, after_commit callbacks cannot open another outer
            # scope and settle/refund this still-unfinished writer's holding.
            fault("INVALID_STATE")
        owner = self.owner
        reply = owner.current if owner is not None else None
        if reply is not None and owner.replies.get(reply.request_id) is not reply:
            fault("PERMISSION_DENIED")
        # A direct privileged Store fixture is not a caller/write grant. Real
        # named requests and original application/job producers mark this scope.
        token = _WriteScope(owner is None or reply is not None, reply)
        if reply is not None and reply.method in {"query.result.rowsPage", "query.result.textPage"}:
            owner.check_reply(reply)
            # This producer greedily fills a legal prefix up to its budget.
            # Keep room for its mandatory outer final check. Other purposes
            # retain their original charge timing, including scopes which roll
            # back before material validation and then persist a diagnostic.
            scalar, objects, work = self._final_material_cost()
            owner.reserve(reply, scalar, objects, work)
            token.charged = reply
            self.charged_reply = True
        self.transaction = token
        return token

    @staticmethod
    def _final_material_cost():
        return 8 * READ_LIMITS.schema_bytes + 64 * 32 * 32, 8192, 2 * READ_LIMITS.validation_work

    def mark_controlled(self):
        self.check_store()
        if self.transaction is None:
            fault("INVALID_STATE")
        self.transaction.controlled = True

    def check_final_material(self, token):
        from ontolearn_engine.project.project_host import material_profile

        self.check_store()
        if self.transaction is not token:
            fault("PERMISSION_DENIED")
        if not token.controlled:
            return
        if self.active is not None or token.checked:
            fault("INVALID_STATE")
        token.checked = True
        # Only schema/table metadata and scalar aggregates are materialized.
        # 8*schema covers retained names/current PRAGMA/escaped SQL copies;
        # 64*32*32 covers bounded per-column/per-table scaffolding. This is the
        # original logical accounting unit, not an RSS/SQLite-native-I/O claim.
        owner = self.owner
        if token.reply is not None:
            owner.check_reply(token.reply)
            if token.reply.method in {"query.result.rowsPage", "query.result.textPage"}:
                if token.charged is not token.reply or not self.charged_reply:
                    fault("INVALID_STATE")
            elif token.charged is not None or self.charged_reply:
                fault("INVALID_STATE")
            else:
                scalar, objects, work = self._final_material_cost()
                owner.reserve(token.reply, scalar, objects, work)
                token.charged = token.reply
                self.charged_reply = True
        else:
            if self.charged_reply:
                fault("INVALID_STATE")
            scalar, objects, work = self._final_material_cost()
            others = (list(owner.replies.values()) if owner is not None else []) + self.holdings()
            if (
                len(self.retained) >= MAX_REPLIES
                or sum(item.scalar for item in others)
                + scalar
                + READ_LIMITS.retained_bytes
                + (owner.management.scalar if owner is not None else 0)
                > HELD_BYTES
                or sum(item.objects for item in others)
                + objects
                + (owner.management.objects if owner is not None else 0)
                > HELD_OBJECTS
                or work > READ_WORK
            ):
                fault("RESOURCE_LIMIT", resource="memory")
            self.active = _WriteHolding(scalar, objects, work)
            token.holding = self.active
        try:
            profile = material_profile(self.connection, READ_LIMITS, _mainline_core_material=True)
            # All accepted, nonterminal jobs in this original DB count, not just
            # the selected project's job. Invalid JSON is never called terminal.
            pending, runs = self.connection.execute(
                "SELECT count(*),coalesce(sum(run IS NOT NULL),0) FROM jobs WHERE "
                "CASE WHEN json_valid(dto) THEN coalesce(json_extract(dto,'$.state'),'') "
                "ELSE '' END NOT IN ('succeeded','failed','cancelled')"
            ).fetchone()
            profile.admit_terminal_growth(READ_LIMITS, pending, runs)
        except HostReadFault as error:
            if error.reason != "limit":
                raise
            fault("RESOURCE_LIMIT", resource="page")

    def retain_unknown(self, token):
        if token.holding is not None and not any(x is token.holding for x in self.retained):
            self.retained.append(token.holding)
        for reply in (token.reply, token.charged):
            if reply is not None:
                reply.unknown = True
                if self.owner is not None and self.owner.replies.get(reply.request_id) is not reply:
                    if not any(x is reply for x in self.retained):
                        self.retained.append(reply)
        if self.owner is not None:
            self.owner.hold = True

    def settlement_failed(self, token):
        # Scope keeps the original references even if a faulty cleanup callback
        # already cleared the shared fields. Never retry/refund this scope.
        self.retain_unknown(token)
        self.transaction = token
        self.active = None
        self.charged_reply = False

    def completed(self, token, error):
        import asyncio

        from ontolearn_engine.coordinator import ServiceFault

        if self.transaction is not token:
            fault("PERMISSION_DENIED")
        known = error is None or isinstance(
            error, (JobFault, Conflict, ServiceFault, asyncio.CancelledError)
        )
        if not known:
            self.retain_unknown(token)
        self.active = None
        self.charged_reply = False
        self.transaction = None


def prepare_mainline_store(store):
    """Trusted bootstrap/adapter only; adds a restriction, never write authority."""
    admission = store._read_admission
    if admission is None:
        admission = _WriteAdmission(store)
        store._read_admission = admission
    if type(admission) is not _WriteAdmission:
        fault("PERMISSION_DENIED")
    admission.check_store()
    return admission


class ExampleResourceFault(ValueError):
    """Fixed internal resource failure; paths and OS errors never cross RPC."""


@contextmanager
def _example_resource_reader(root, input_bytes):
    import os
    import stat

    if os.name == "nt":
        from ontolearn_engine.project._windows_resource import windows_resource

        with windows_resource(root, input_bytes) as read_member:
            yield read_member
        return

    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:

        def read_member(name, maximum):
            # Nonblocking open lets fstat reject FIFO without waiting for a writer.
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=root_fd)
            try:
                before = os.fstat(fd)
                if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
                    raise ExampleResourceFault("EXAMPLE_RESOURCE_UNAVAILABLE")
                with os.fdopen(fd, "rb", closefd=False) as handle:
                    raw = handle.read(maximum + 1)
                after = os.fstat(fd)
                if (
                    len(raw) != before.st_size
                    or len(raw) > maximum
                    or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
                    != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
                ):
                    raise ExampleResourceFault("EXAMPLE_RESOURCE_UNAVAILABLE")
                return raw
            finally:
                os.close(fd)

        yield read_member
    finally:
        os.close(root_fd)


class BuiltinExampleProvider:
    """A fixed named resource in an explicitly installed, trusted bundle root.

    The process bootstrap owns root and manifest_sha256. There is deliberately
    no automatic cwd/environment/development-path discovery or wire factory.
    Factory construction alone grants no project/session/write authority.
    """

    def __init__(self, *, root, manifest_sha256):
        import re
        from pathlib import Path

        if (type(root) is not Path and not isinstance(root, Path)) or (
            type(manifest_sha256) is not str
            or re.fullmatch(r"[0-9a-f]{64}", manifest_sha256) is None
        ):
            raise ExampleResourceFault("EXAMPLE_RESOURCE_UNAVAILABLE")
        if not root.is_absolute():
            raise ExampleResourceFault("EXAMPLE_RESOURCE_UNAVAILABLE")
        self._root, self._manifest_sha256 = root, manifest_sha256

    def load(self, *, example_id, input_digest):
        import hashlib
        import json

        from ontolearn_engine.project.project_lifecycle import (
            EXAMPLE_ID,
            EXAMPLE_INPUT_BYTES,
            EXAMPLE_INPUT_SHA256,
        )

        if example_id != EXAMPLE_ID or input_digest != EXAMPLE_INPUT_SHA256:
            raise ExampleResourceFault("EXAMPLE_RESOURCE_UNAVAILABLE")
        try:
            with _example_resource_reader(self._root, EXAMPLE_INPUT_BYTES) as read_member:
                manifest_raw = read_member("t01-provider.json", 8192)
                if hashlib.sha256(manifest_raw).hexdigest() != self._manifest_sha256:
                    raise ExampleResourceFault("EXAMPLE_RESOURCE_UNAVAILABLE")
                manifest = json.loads(manifest_raw.decode("utf-8"))
                expected = {
                    "exampleProviderManifestVersion": 1,
                    "exampleId": EXAMPLE_ID,
                    "input": {
                        "path": "load-input.json",
                        "bytes": EXAMPLE_INPUT_BYTES,
                        "sha256": EXAMPLE_INPUT_SHA256,
                    },
                }
                # Canonical representation distinguishes booleans from integer 1.
                if canonical(manifest) != canonical(expected):
                    raise ExampleResourceFault("EXAMPLE_RESOURCE_UNAVAILABLE")
                raw = read_member("load-input.json", EXAMPLE_INPUT_BYTES)
                if (
                    len(raw) != EXAMPLE_INPUT_BYTES
                    or hashlib.sha256(raw).hexdigest() != EXAMPLE_INPUT_SHA256
                ):
                    raise ExampleResourceFault("EXAMPLE_RESOURCE_UNAVAILABLE")
                return raw
        except (OSError, ValueError, UnicodeError, RecursionError):
            raise ExampleResourceFault("EXAMPLE_RESOURCE_UNAVAILABLE") from None


def make_example_provider(*, root, manifest_sha256):
    """Bootstrap-only factory; T11 supplies both actual root and fixed manifest pin."""
    return BuiltinExampleProvider(root=root, manifest_sha256=manifest_sha256)


@dataclass(eq=False)
class _Reply:
    request_id: str
    method: str
    project: str | None
    generation: int
    scalar: int
    objects: int = 128
    work: int = 0
    values: list = field(default_factory=list)
    unknown: bool = False
    ticket: object = None
    lifecycle_checked: tuple | None = None


class _Budget(QueryReadBudget):
    def __init__(self, owner, reply):
        self.owner, self.reply = owner, reply

    def reserve(self, stage, *, bytes_, objects, work):
        self.owner.check_reply(self.reply)
        if (
            type(stage) is not str
            or len(stage) > 128
            or any(type(n) is not int or n < 0 for n in (bytes_, objects, work))
        ):
            fault("INVALID_STATE")
        self.owner.reserve(self.reply, bytes_, objects, work)

    def reserve_store(self, stage, request):
        # Prepay native material AND validation work before any aggregate, decode,
        # hash, or Store traversal. Then the original preflight checks the admitted
        # dataset before a projection can materialize it. No write scope is issued.
        limits = self.owner.reader_limits
        self.reserve(
            stage,
            bytes_=32 * limits.validation_bytes + 2048 * limits.validation_rows + 32768,
            objects=32 * limits.validation_rows + 4096,
            work=3 * limits.validation_work,
        )
        self.owner.preflight()

    def handoff(self, value):
        self.owner.check_reply(self.reply)
        if len(self.reply.values) >= 4:
            fault("INVALID_STATE")
        # The producer prepaid the material; retain its actual aliases until the
        # real stdout emission and sender drop. Scope exit alone releases nothing.
        self.reply.values.append(value)


class _MainlineReader(ProjectHostReader):
    """Private purpose selection from the actual owned reply, never wire input."""

    def __init__(self, owner):
        self._owner = owner
        super().__init__(owner.store, limits=owner.reader_limits)

    def _preflight(self) -> int:
        owner = self._owner
        owner.check_reply(owner.current)
        return super()._preflight(
            _mainline_core_material=owner.current.method in METHODS | {"project.get"}
        )


@dataclass(frozen=True)
class _OwnershipProof:
    """Stack-owned issuer proof; no constructor or authority is exposed on wire."""

    owner: object
    reply: object
    store: object
    connection: object
    lease: object
    project: str
    generation: int
    method: str
    base: int | None
    request_hash: str

    def check(self, store, project):
        owner = self.owner
        owner.check_reply(self.reply)
        if (
            store is not self.store
            or owner.store is not store
            or store._db is not self.connection
            or store._format3_lease is not self.lease
            or project != self.project
            or owner.selected != project
            or owner.generation != self.generation
            or self.reply.method != self.method
            or self.reply.project != project
        ):
            fault("PERMISSION_DENIED")
        owner.authorize({"projectId": project})

    @property
    def origin(self):
        return {
            "ownerId": self.owner.owner_id,
            "hostClientId": self.owner.host,
            "engineSessionId": self.owner.session,
        }

    def reserve(self, stage, *, bytes_, objects, work):
        self.check(self.store, self.project)
        self.owner._budget().reserve(stage, bytes_=bytes_, objects=objects, work=work)

    def admissions(self):
        self.reserve(
            "ownership admission scans",
            bytes_=4 * READ_LIMITS.validation_bytes,
            objects=4096,
            work=2 * READ_LIMITS.validation_work,
        )
        reader = ProjectHostReader(self.store, limits=READ_LIMITS)
        values = []
        for core in (True, False):
            try:
                reader._preflight(_mainline_core_material=core)
            except HostReadFault as error:
                if error.reason != "limit":
                    self.owner._host_fault(error)
                values.append(False)
            else:
                values.append(True)
        return tuple(values)

    def material_profile(self):
        # Admission already authenticated schema; identifiers still come only
        # from SQLite. This measures exact prospective row/column byte deltas.
        self.reserve(
            "ownership projected material",
            bytes_=2 * READ_LIMITS.validation_bytes,
            objects=4096,
            work=READ_LIMITS.validation_work // 2,
        )
        db = self.store._db
        total = scan = decoded = 0
        counts, plan_sizes = {}, None
        tables = list(db.execute("SELECT name FROM sqlite_master WHERE type='table'"))
        for (table,) in tables:
            quoted = '"' + table.replace('"', '""') + '"'
            columns = db.execute(f"PRAGMA table_info({quoted})").fetchall()
            sizes = "+".join(
                'coalesce(length(CAST("' + row[1].replace('"', '""') + '" AS BLOB)),0)'
                for row in columns
            )
            count, size = db.execute(
                f"SELECT count(*),coalesce(sum({sizes}),0) FROM {quoted}"
            ).fetchone()
            counts[table] = count
            total += count
            scan += size
            if table not in {"job_blobs", "job_plans"}:
                decoded += size
            if table == "job_plans":
                plan_sizes = sizes
        plans = db.execute(
            f"SELECT coalesce(sum({plan_sizes}),0) FROM job_plans WHERE ref IN ("
            "SELECT CASE WHEN json_valid(context) THEN "
            "json_extract(context,'$.request.authorization.preparedPlanRef') END "
            "FROM operation_claims WHERE kind='application')"
        ).fetchone()[0]
        return (
            total,
            scan,
            decoded,
            plans,
            (counts.get("app_operations", 0) + counts.get("snapshots", 0))
            * (1 + counts.get("management_receipts", 0))
            + counts.get("management_receipts", 0),
        )

    def project_admissions(self, before, profile, rows, scan_delta, decoded_delta):
        count, scan, decoded, plans, repeats = profile
        core = (
            count + rows <= READ_LIMITS.validation_rows
            and decoded + decoded_delta + plans <= READ_LIMITS.validation_bytes
            and 2 * (scan + scan_delta) + (decoded + decoded_delta + plans) * repeats
            <= READ_LIMITS.validation_work
        )
        full = (
            count + rows <= READ_LIMITS.validation_rows
            and scan + scan_delta <= READ_LIMITS.validation_bytes
            and (scan + scan_delta) * (1 + repeats) <= READ_LIMITS.validation_work
        )
        if not core or (before[1] and not full):
            fault("RESOURCE_LIMIT", resource="page")


class MainlineHost(OrdinaryReadAuthority, QueryDispatchAuthority):
    """One real actor/store/handshake owner; no authority derived from a DTO."""

    def __init__(self, actor, *, example_provider=None):
        if example_provider is not None and type(example_provider) is not BuiltinExampleProvider:
            fault("INVALID_STATE")
        self.actor, self.store = actor, actor.store
        # Trusted bootstrap object only; never constructed from request fields.
        self.example_provider = example_provider
        self._owner_id = str(uuid4())
        self.reader_limits = READ_LIMITS
        self.reader = _MainlineReader(self)
        self.authority = self  # Narrow book interface consumed by query_read.
        self.selected = None
        self.selected_lifecycle = None
        from ontolearn_engine.project.management_host import ManagementHost

        self.management = ManagementHost(self)
        self.generation = 0
        self.host = self.session = None
        self.current = None
        self.replies = {}
        self.closed = False
        self._clean_close = False
        self.hold = False
        prepare_mainline_store(self.store).bind(self)

    @property
    def owner_id(self):
        return self._owner_id

    def bind_handshake(self):
        if (
            self.session is not None
            or self.actor.profile != "business3"
            or self.actor.test_mode
            or self.actor.session is None
            or self.actor.host_client_id is None
            or self.actor.store is not self.store
        ):
            fault("PERMISSION_DENIED")
        self.host, self.session = self.actor.host_client_id, self.actor.session

    def allows_owner(self, store, session):
        return (
            not self.closed
            and not self.actor.closed
            and not self.hold
            and self.actor.profile == "business3"
            and not self.actor.test_mode
            and self.actor.store is self.store is store
            and self.actor.session == self.session == session
            and self.actor.host_client_id == self.host
            and self.host is not None
            and self.actor.ordinary is self
            and self.actor.mainline is self
        )

    def enabled(self):
        return self.allows_owner(self.store, self.session)

    def require_owner(self, owner):
        if self.hold:
            fault("STORAGE_FAILURE")
        if owner != self.owner_id or not self.enabled():
            fault("PERMISSION_DENIED")

    def projects(self):
        return frozenset([self.selected]) if self.enabled() and self.selected else frozenset()

    def authorize(self, params):
        self.require_owner(self.owner_id)
        project = params.get("projectId", params.get("binding", {}).get("projectId"))
        method = self.current.method if self.current is not None else None
        # These are library-management admission paths, not selected-project
        # grants. Their own handlers bind exact refs/hash and current lifecycle.
        if method in {"project.management.operation.get", "project.management.apply"}:
            return project
        if (
            method == "project.management.preview"
            and params.get("action", {}).get("kind") == "restore-trash"
        ):
            return project
        if method == "project.management.confirm":
            return project
        if method == "project.open":
            return project
        if project is not None:
            if project != self.selected:
                fault("PERMISSION_DENIED")
            from ontolearn_engine.project.management import lifecycle, public_internal

            binding = (project, self.generation, canonical(self.selected_lifecycle))
            if self.current.lifecycle_checked != binding:
                # This synchronous frame cannot execute a second mutation or
                # yield to another actor. Authenticate once per original reply;
                # per-cell capability checks reuse that exact funded read. A new
                # frame/generation always performs a fresh lifecycle lookup.
                self._budget().reserve(
                    "current lifecycle authorization", bytes_=8192, objects=128, work=16384
                )
                current = lifecycle(self.store, public_internal(self.store, project))
                if current["state"] != "active" or current != self.selected_lifecycle:
                    fault("PERMISSION_DENIED")
                self.current.lifecycle_checked = binding
        return project

    def ownership_proof(self, params, *, method):
        self.require_owner(self.owner_id)
        self.check_reply(self.current)
        if (
            method not in {"changeset.preview", "project.ownership.detail"}
            or self.current.method != method
        ):
            fault("PERMISSION_DENIED")
        self.authorize(params)
        from ontolearn_engine.storage import digest

        self._budget().reserve(
            "ownership request binding",
            bytes_=4 * self.actor.limits["maxFrameBytes"],
            objects=4096,
            work=8 * self.actor.limits["maxFrameBytes"],
        )
        return _OwnershipProof(
            self,
            self.current,
            self.store,
            self.store._db,
            self.store._format3_lease,
            params["projectId"],
            self.generation,
            method,
            params.get("baseRevision"),
            digest(params),
        )

    def begin(self, request):
        self.require_owner(self.owner_id)
        if self.current is not None or len(self.replies) >= MAX_REPLIES:
            fault("INVALID_STATE")
        request_id, method = request["id"], request["method"]
        if (
            method in {"project.create", "project.example.create", "project.open"}
            and self.generation >= 9007199254740991
        ):
            fault("INVALID_STATE")
        project = request["params"].get(
            "projectId", request["params"].get("binding", {}).get("projectId")
        )
        reply = _Reply(request_id, method, project, self.generation, 4096)
        self.reserve(reply, 4 * self.actor.limits["maxFrameBytes"], 128, 4096)
        self.replies[request_id] = reply
        self.current = reply
        if self.store._file_identity is not None:
            from ontolearn_engine.project.file_identity import verify_connection
            from ontolearn_engine.project.format3 import Format3Fault

            # The reply is prepaid before checking physical identity, and no
            # business authorization or catalog read has happened yet. Liveness
            # methods do not enter begin(), so a damaged library keeps pinging.
            try:
                verify_connection(self.store._db)
            except Format3Fault:
                fault("STORAGE_FAILURE")

    def check_reply(self, reply):
        self.require_owner(self.owner_id)
        if (
            reply is None
            or self.replies.get(reply.request_id) is not reply
            or self.current is not reply
            or reply.unknown
            or reply.generation != self.generation
        ):
            fault("PERMISSION_DENIED")

    def reserve(self, reply, scalar, objects, work):
        others = [r for r in self.replies.values() if r is not reply]
        others += self.store._read_admission.holdings()
        if (
            sum(r.scalar for r in others)
            + reply.scalar
            + scalar
            + self.reader_limits.retained_bytes
            + self.management.scalar
            > HELD_BYTES
            or sum(r.objects for r in others) + reply.objects + objects + self.management.objects
            > HELD_OBJECTS
            or reply.work + work > READ_WORK
        ):
            fault("RESOURCE_LIMIT", resource="memory")
        reply.scalar += scalar
        reply.objects += objects
        reply.work += work

    def preflight(self):
        self.require_owner(self.owner_id)
        try:
            with self.reader._read():
                self.reader._preflight()
                self.reader._validate()
        except HostReadFault as error:
            self._host_fault(error)

    def _host_fault(self, error):
        code, params = {
            "input": ("INVALID_REQUEST", {"field": "params"}),
            "missing": ("NOT_FOUND", {"resource": "project"}),
            "limit": ("RESOURCE_LIMIT", {"resource": "page"}),
            "cursor": ("CURSOR_MISMATCH", {}),
            "expired": ("CURSOR_EXPIRED", {}),
            "state": ("INVALID_STATE", {}),
            "structure": ("STORAGE_FAILURE", {}),
        }[error.reason]
        if error.reason == "structure":
            self.hold = True
        fault(code, **params)

    @contextmanager
    def read_scope(self, store, session, purpose, project):
        self.require_owner(self.owner_id)
        reply = self.current
        if (
            store is not self.store
            or session != self.session
            or reply is None
            or reply.method != purpose
            or project != reply.project
            or project != self.selected
            or purpose not in QUERY_METHODS
        ):
            fault("PERMISSION_DENIED")
        budget = _Budget(self, reply)
        try:
            yield budget
        except BaseException as error:
            # Fixed business rejections are reconciled after their error reply.
            # Unknown exceptions keep all admitted holdings in the original book.
            if not isinstance(error, JobFault):
                reply.unknown = True
            raise

    def _budget(self):
        reply = self.current
        if reply is None:
            fault("PERMISSION_DENIED")
        self.check_reply(reply)
        return _Budget(self, reply)

    def _room(self, value, budget, schema):
        maximum = self.actor.limits["maxFrameBytes"]
        budget.reserve("reply encoding", bytes_=64 * maximum, objects=4096, work=128 * maximum)
        if not self.actor.validate(schema, value):
            fault("INVALID_STATE")
        if self.store.contract.encoded_size(value) + 1024 > maximum:
            fault("RESOURCE_LIMIT", resource="frame")
        budget.handoff(value)
        return value

    def _project(self, project, budget):
        budget.reserve_store("project read", {"projectId": project})
        value = self.store.project_get(project)
        self.check_reply(budget.reply)
        maximum = self.actor.limits["maxFrameBytes"]
        budget.reserve("project shape", bytes_=8 * maximum, objects=4096, work=64 * maximum)
        if not self.actor.validate("result_project.get", value):
            fault("INVALID_STATE")
        return value

    def _select(self, project):
        # No Job/worker/subscription is cancelled when the view changes.
        self.generation += 1
        self.selected = project
        from ontolearn_engine.project.management import lifecycle, public_internal

        self.selected_lifecycle = lifecycle(self.store, public_internal(self.store, project))
        self.current.generation = self.generation

    def dispatch(self, method, params):
        from ontolearn_engine.project.project_lifecycle import CreationFault

        self.require_owner(self.owner_id)
        if method not in METHODS or self.current is None or self.current.method != method:
            fault("PERMISSION_DENIED")
        budget = self._budget()
        try:
            if method in MANAGEMENT_METHODS:
                result = self.management.dispatch(method, params, budget)
            elif method == "project.catalog":
                budget.reserve_store("project catalog", params)
                cursor = params["cursor"]
                if cursor is not None:
                    _, original = self.reader._cursor(cursor)
                    if original.page_size != params["pageSize"]:
                        fault("CURSOR_MISMATCH")
                result = (
                    self.reader.catalog_start(page_size=params["pageSize"])
                    if cursor is None
                    else self.reader.catalog_next(cursor)
                )
            elif method == "project.create":
                budget.reserve_store("project create admission", params)
                result = self.store.commit(
                    None,
                    None,
                    params["operationId"],
                    None,
                    creation={
                        "projectCreateCoreVersion": 1,
                        "request": params,
                        "origin": {
                            "hostClientId": self.host,
                            "engineSessionId": self.session,
                            "permission": "library.create",
                        },
                        "readerLimits": self.reader_limits,
                    },
                )
                # A committed create has its original receipt on response failure.
                # Selection is only installed after output shape/size admission.
                self._room(result, budget, "result_project.create")
                self._select(result["projectId"])
                return result
            elif method == "project.example.create":
                from ontolearn_engine.project.project_lifecycle import (
                    example_context,
                    example_request_value,
                )

                request = example_request_value(params)
                origin = {
                    "hostClientId": self.host,
                    "engineSessionId": self.session,
                    "permission": "library.create",
                }
                budget.reserve_store("project example create admission", request)
                budget.reserve("example resource", bytes_=1048576, objects=4096, work=2097152)
                # Accepted creation replays from its authenticated immutable
                # source/receipt closure, never a later mutable bundle read.
                with self.store._read():
                    claim = self.store._db.execute(
                        "SELECT project FROM operation_claims WHERE operation=?",
                        (request["operationId"],),
                    ).fetchone()
                    if claim is not None:
                        accepted = example_context(
                            self.store, claim["project"], request["operationId"]
                        )
                        if (
                            accepted is None
                            or accepted["context"]["request"] != request
                            or accepted["context"]["origin"] != origin
                        ):
                            fault("IDENTITY_CONFLICT")
                        if (
                            self.store.project_receipt(claim["project"], request["operationId"])
                            != accepted["receipt"]
                        ):
                            fault("INVALID_STATE")
                        resource = accepted["context"]["resourceUtf8"].encode("utf-8")
                if claim is None:
                    provider = self.example_provider
                    if provider is None:
                        fault("NOT_FOUND", resource="snapshot")
                    if type(provider) is not BuiltinExampleProvider:
                        fault("INVALID_STATE")
                    try:
                        resource = provider.load(
                            example_id=request["exampleId"], input_digest=request["inputDigest"]
                        )
                    except ExampleResourceFault:
                        fault("NOT_FOUND", resource="snapshot")
                    except Exception:
                        fault("INVALID_STATE")
                result = self.store.commit(
                    None,
                    None,
                    request["operationId"],
                    None,
                    example_creation={
                        "exampleCreateCoreVersion": 1,
                        "request": request,
                        "origin": origin,
                        "readerLimits": self.reader_limits,
                        "resource": resource,
                    },
                )
                self._room(result, budget, "result_project.example.create")
                self._select(result["projectId"])
                return result
            elif method == "project.draft.save":
                import json

                self.authorize(params)
                if type(params) is not dict or set(params) != {
                    "projectId",
                    "operationId",
                    "editor",
                    "expectedGeneration",
                    "boundDomainRevision",
                    "contentJson",
                }:
                    fault("INVALID_REQUEST", field="params")
                budget.reserve("draft input", bytes_=2097152, objects=524288, work=2097152)
                text = params["contentJson"]
                if type(text) is not str:
                    fault("INVALID_REQUEST", field="params")
                try:
                    if len(text.encode("utf-8")) > 65536:
                        fault("INVALID_REQUEST", field="params")
                    content = json.loads(text)
                    if canonical(content) != text:
                        fault("INVALID_REQUEST", field="params")
                except (ValueError, TypeError, UnicodeError, OverflowError, RecursionError):
                    fault("INVALID_REQUEST", field="params")
                project, operation = params["projectId"], params["operationId"]
                budget.reserve_store("project draft save admission", params)
                internal = self.store._project(project)
                generation_conflict = False
                try:
                    with self.store._transaction():
                        # Only new writes acquire a current domain CAS. An accepted
                        # operation is authenticated by apply_application against its
                        # original request/actor, even after later drafts/domain edits.
                        if not self.store.has_operation_claim(operation):
                            revision = self.store.revision(internal)
                            if params["boundDomainRevision"] != revision:
                                fault(
                                    "REVISION_CONFLICT",
                                    expected=params["boundDomainRevision"],
                                    actual=revision,
                                )
                            head = self.store._db.execute(
                                "SELECT generation FROM app_drafts WHERE project=? AND editor=?",
                                (internal, params["editor"]),
                            ).fetchone()
                            actual_generation = head[0] if head is not None else 0
                            generation_conflict = actual_generation != params["expectedGeneration"]
                        receipt = self.store.apply_application(
                            project,
                            operation,
                            {
                                "type": "draft.save",
                                "editor": params["editor"],
                                "expectedGeneration": params["expectedGeneration"],
                                "boundDomainRevision": params["boundDomainRevision"],
                                "content": content,
                            },
                            actor=self.host,
                            permission="write",
                        )
                        checkpoint = self.store.project_checkpoint(
                            internal, receipt["afterCheckpointRef"]
                        )
                        draft = next(
                            (
                                row
                                for row in checkpoint["application"]["drafts"]
                                if row["editor"] == params["editor"]
                            ),
                            None,
                        )
                        if draft is None or draft["present"] != 1 or draft["payload"] != text:
                            fault("INVALID_STATE")
                        result = {
                            "draftSaveVersion": 1,
                            "projectId": project,
                            "operationId": operation,
                            "operationSequence": receipt["operationSequence"],
                            "editor": params["editor"],
                            "generation": draft["generation"],
                            "boundDomainRevision": draft["bound_revision"],
                            "contentHash": draft["content_hash"],
                            "afterCheckpointRef": receipt["afterCheckpointRef"],
                        }
                except Conflict as error:
                    # The original Store transaction/savepoint has rolled back.
                    # Only the observed generation CAS mismatch is a normal
                    # rejection; unrelated state/storage failures stay UNKNOWN.
                    if generation_conflict and error.category == "state":
                        fault("INVALID_STATE")
                    raise
                return self._room(result, budget, "result_project.draft.save")
            elif method == "project.open":
                result = self._project(params["projectId"], budget)
                self._room(result, budget, "result_project.open")
                self._select(params["projectId"])
                return result
            elif method == "project.ownership.detail":
                self.authorize(params)
                budget.reserve_store("ownership detail read", params)
                proof = self.ownership_proof(params, method=method)
                result = self.store.ownership_detail_page(params, proof, self.actor.limits)
            else:
                project = params["projectId"]
                self.authorize(params)
                budget.reserve_store("project read material", params)
                # HostReader deliberately refuses ANY pre-existing transaction.
                # Read its coherent workspace first, then authenticate its exact
                # CP1 in the second pure read. The checkpoint includes application
                # sequence as well as domain input, so even metadata-only changes
                # cannot splice two views. No await or writer runs between them.
                workspace = self.reader.workspace(project, editor=params["editor"])
                with self.store._read():
                    internal = self.store._project(project)
                    head = self.store._db.execute(
                        "SELECT checkpoint FROM app_projects WHERE project=?", (internal,)
                    ).fetchone()
                    if head is None or head[0] != workspace["checkpointRef"]:
                        fault("IDENTITY_CONFLICT")
                    budget.reserve(
                        "domain identity",
                        bytes_=8 * self.reader_limits.validation_bytes,
                        objects=4096,
                        work=32 * self.reader_limits.validation_bytes,
                    )
                    snapshot = self.store._snapshot_projection(internal)
                    from ontolearn_engine.storage import digest

                    identity = digest(snapshot)
                    if identity != workspace["inputSnapshotId"]:
                        fault("IDENTITY_CONFLICT")
                    existing = self.store._db.execute(
                        "SELECT 1 FROM snapshots WHERE id=?", (identity,)
                    ).fetchone()
                    if existing and self.store._project_snapshot(identity, internal) != snapshot:
                        fault("INVALID_STATE")
                    draft = workspace["draft"]
                    if "content" in draft:
                        budget.reserve(
                            "draft encoding",
                            bytes_=16 * self.reader_limits.draft_bytes,
                            objects=128,
                            work=32 * self.reader_limits.draft_bytes,
                        )
                        draft["contentJson"] = (
                            canonical(draft.pop("content")) if draft["state"] == "present" else None
                        )
                        draft.pop("content", None)
                    result = {
                        "readVersion": 1,
                        "projectId": project,
                        "inputSnapshotId": identity,
                        "workspace": workspace,
                        "domain": {
                            key: snapshot[key]
                            for key in ("projectRevision", "dependencyVector", "state")
                        },
                    }
            return self._room(result, budget, "result_" + method)
        except HostReadFault as error:
            self._host_fault(error)
        except CreationFault as error:
            code, detail = {
                "input": ("INVALID_REQUEST", {"field": "params"}),
                "limit": ("RESOURCE_LIMIT", {"resource": "frame"}),
                "identity": ("IDENTITY_CONFLICT", {}),
                "state": ("INVALID_STATE", {}),
                "structure": ("STORAGE_FAILURE", {}),
            }[error.reason]
            if error.reason == "structure":
                self.hold = True
            fault(code, **detail)

    def take(self, actor, request):
        # Every production business3 selected project.get is pure. The original
        # authenticated frame id is the single-use purpose; no sixth RPC/flag.
        reply = self.current
        if (
            actor is not self.actor
            or reply is None
            or request["id"] != reply.request_id
            or request["method"] != "project.get"
            or reply.method != "project.get"
            or request["params"]["projectId"] != self.selected
        ):
            fault("PERMISSION_DENIED")
        self.check_reply(reply)
        budget = self._budget()
        project = self.selected
        value = self._project(project, budget)
        read = QueryRead(
            actor, self, self.session, self.store, project, budget, self, self.owner_id
        )
        ticket = ProjectGetReadTicket(
            self,
            read,
            request["id"],
            project,
            value["projectRevision"],
            value["inputSnapshotId"],
            self.owner_id,
            self.generation,
            self.generation,
        )
        reply.ticket = ticket
        return ticket

    def check(self, ticket, actor, store):
        self.check_reply(self.current)
        if (
            actor is not self.actor
            or store is not self.store
            or self.current.ticket is not ticket
            or ticket.issuer is not self
            or ticket.project != self.selected
            or ticket.generation != self.generation
            or ticket.owner_id != self.owner_id
        ):
            fault("PERMISSION_DENIED")

    def finish(self, ticket, *, emitted, failure=None):
        reply = self.replies.get(ticket.request_id)
        if reply is None or reply.ticket is not ticket:
            fault("PERMISSION_DENIED")
        ticket.read.active = False
        if not emitted or failure is not None:
            reply.unknown = True
            self.closed = True

    def finish_reply(self, request_id, *, emitted, failure=None):
        reply = self.replies.get(request_id)
        if reply is None:
            return
        if not emitted or failure is not None:
            reply.unknown = True
            self.closed = True
        if self.current is reply:
            self.current = None
        if not reply.unknown:
            reply.values.clear()
            del self.replies[request_id]
        # UNKNOWN records never evict/refill when a new selection/session arrives.

    def observe_error(self, request_id, error):
        from ontolearn_engine.coordinator import ServiceFault

        reply = self.replies.get(request_id)
        if reply is None:
            return
        # JobFault is the bounded original service rejection. Unclassified
        # failures retain their original owner reservation; no new generation
        # refunds it or turns damaged/unknown material into authority.
        if not isinstance(error, (JobFault, ServiceFault)):
            reply.unknown = True
            self.hold = True
        if isinstance(error, JobFault) and error.code == "STORAGE_FAILURE":
            self.hold = True

    def close(self):
        self._clean_close = False
        self.closed = True
        self.reader.close()
        self.management.close()
        self._clean_close = True
