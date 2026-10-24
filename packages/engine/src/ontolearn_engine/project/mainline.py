"""Named services for the owned business3 stdio session and its selected project.

This is an application adapter, not a database resolver or domain dispatcher.
The process already owns the original JobStore lifetime lease. Wire callers
cannot supply a store, permission, scope, implementation, or read ticket.
"""

from contextlib import contextmanager
from dataclasses import dataclass, field
from uuid import uuid4

from ontolearn_engine.job_store import JobFault, fault
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
    }
)
# First-chain rejection bounds, within the original reader's limits. These are
# not Q5 capacity, RSS, SQLite I/O, or whole-H acceptance claims.
# Admit the three persisted copies of a legal 420002-byte historical literal.
# 1.5 MiB also fits both prepaid project.get Store reads inside the unchanged
# 128 MiB retained book; 2 MiB would exceed that book. No other cap is raised.
READ_LIMITS = ReadLimits(validation_rows=4096, validation_bytes=1572864, validation_work=67108864)
HELD_BYTES = 134217728
HELD_OBJECTS = 1048576
READ_WORK = 536870912
MAX_REPLIES = 16


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
        self.generation = 0
        self.host = self.session = None
        self.current = None
        self.replies = {}
        self.closed = False
        self.hold = False

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
        if self.current is not None and self.current.method == "project.open":
            return project  # Only named open may validate an unselected catalog ID.
        if project is not None and project != self.selected:
            fault("PERMISSION_DENIED")
        return project

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
        if (
            sum(r.scalar for r in others)
            + reply.scalar
            + scalar
            + self.reader_limits.retained_bytes
            > HELD_BYTES
            or sum(r.objects for r in others) + reply.objects + objects > HELD_OBJECTS
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
        self.current.generation = self.generation

    def dispatch(self, method, params):
        from ontolearn_engine.project.project_lifecycle import CreationFault

        self.require_owner(self.owner_id)
        if method not in METHODS or self.current is None or self.current.method != method:
            fault("PERMISSION_DENIED")
        budget = self._budget()
        try:
            if method == "project.catalog":
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
        self.closed = True
        self.reader.close()
