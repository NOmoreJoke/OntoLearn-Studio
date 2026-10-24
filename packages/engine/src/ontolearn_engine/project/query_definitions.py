"""Query definition reads and admission material; never a save/confirmation issuer.

The sole OrdinaryReadAuthority must supply a real prepaid QueryReadBudget from
its read_scope. Missing tickets deny before Store/measurement/clone. This module
only consumes that scope: it does not implement the pending physical provider.
"""

import json
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass

from ontolearn_engine.job_store import fault
from ontolearn_engine.storage import digest

METHODS = frozenset(
    {
        "query.definition.load",
        "query.execution.prepare",
        "query.result.describe",
        "query.result.textPage",
        "query.result.rowsPage",
    }
)
EDGE_SPACE = (
    "\t\n\x0b\x0c\r\x1c\x1d\x1e\x1f \x85\xa0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006"
    "\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff"
)


class QueryReadBudget(ABC):
    """Consumption contract on the original authority's actual scope, not a grant.

    reserve_store prepays the whole admitted physical read and retained native
    material *before* calling Store (including scans/JSON decode/authentication).
    reserve prepays additional local work/holding. Both must deny atomically when
    no real credit remains, and retain failed traceback aliases. handoff retains
    the exact returned value through the real owner/delivery cleanup; context exit
    alone must not refund it. Production implementation is deliberately absent.
    """

    @abstractmethod
    def reserve_store(self, stage, request):
        raise NotImplementedError

    @abstractmethod
    def reserve(self, stage, *, bytes_, objects, work):
        raise NotImplementedError

    @abstractmethod
    def handoff(self, value):
        raise NotImplementedError


@dataclass(eq=False)
class QueryRead:
    actor: object
    authority: object
    session: str
    store: object
    project: str
    budget: QueryReadBudget
    book: object
    owner_id: object
    active: bool = True

    def _originals(self, store):
        if (
            not self.active
            or store is not self.store
            or self.actor.store is not store
            or self.actor.session != self.session
            or self.actor.ordinary is not self.book
            or self.book.owner_id != self.owner_id
            or self.book.authority is not self.authority
        ):
            fault("PERMISSION_DENIED")

    def check(self, store):
        self._originals(store)
        self.book.require_owner(self.owner_id)
        self.actor._authorize({"projectId": self.project})
        # External negative checks may synchronously revoke or replace originals.
        self._originals(store)

    def before_store(self, store, stage, request):
        self.check(store)
        self.budget.reserve_store(stage, request)
        self.check(store)

    def pay(self, stage, *, bytes_=0, objects=0, work=0):
        self.check(self.store)
        self.budget.reserve(stage, bytes_=bytes_, objects=objects, work=work)
        self.check(self.store)

    def deliver(self, value):
        self.check(self.store)
        self.budget.handoff(value)
        self.check(self.store)
        return value


@contextmanager
def query_read(actor, method, params):
    if method not in METHODS:
        fault("PERMISSION_DENIED")
    project = params.get("projectId", params.get("binding", {}).get("projectId"))
    # Fix every original before any external authority/authorization callback.
    book = actor.ordinary
    owner_id = book.owner_id
    authority, session, store = book.authority, actor.session, actor.store

    def original():
        if (
            actor.ordinary is not book
            or book.owner_id != owner_id
            or book.authority is not authority
            or actor.session != session
            or actor.store is not store
        ):
            fault("PERMISSION_DENIED")

    actor._authorize({"projectId": project})
    original()
    book.require_owner(owner_id)
    original()
    # Enter even a returned scope whose callback revoked the originals: its own
    # context keeps cleanup/unknown holding. No Store call precedes the recheck.
    scope = authority.read_scope(store, session, method, project)
    if scope is None:
        fault("PERMISSION_DENIED")
    with scope as budget:
        if not isinstance(budget, QueryReadBudget):
            fault("PERMISSION_DENIED")
        ticket = QueryRead(actor, authority, session, store, project, budget, book, owner_id)
        try:
            ticket.check(store)
            ticket.before_store(store, method, params)
            yield ticket
        finally:
            ticket.active = False


def scalar(value):
    return type(value) is str and all(not 0xD800 <= ord(c) <= 0xDFFF for c in value)


def draft(value, *, stored=False):
    error = "INVALID_STATE" if stored else "INVALID_REQUEST"
    if (
        type(value) is not dict
        or len(value) != 6
        or set(value) != {"name", "description", "sparql", "scope", "capabilityQuestion", "source"}
    ):
        fault(error, **({} if stored else {"field": "params"}))
    for key, limit in {
        "name": 128,
        "description": 4096,
        "sparql": 65536,
        "capabilityQuestion": 4096,
    }.items():
        text = value[key]
        if not scalar(text) or sum(2 if ord(c) > 0xFFFF else 1 for c in text) > limit:
            fault(error, **({} if stored else {"field": "params"}))
    if value["scope"] not in {"asserted", "asserted+derived"} or value["source"] not in {
        "template",
        "visual",
        "editor",
        "model",
    }:
        fault(error, **({} if stored else {"field": "params"}))
    result = dict(value)
    for key in ("name", "sparql"):
        result[key] = result[key].strip(EDGE_SPACE)
        if not result[key]:
            fault(error, **({} if stored else {"field": "params"}))
    return result


def _record(store, project, definition, selection, ticket, *, snapshot=None):
    ticket.check(store)
    if project != ticket.project:
        fault("PERMISSION_DENIED")
    internal = store._project(project)
    if snapshot is None:
        if selection["kind"] == "current":
            snapshot = store._snapshot_projection(internal)
            identity = digest(snapshot)
            if store._db.execute("SELECT 1 FROM snapshots WHERE id=?", (identity,)).fetchone():
                # An existing historical row must authenticate even when current
                # bytes derive its identity. Never repair or replace corrupt proof.
                if store._project_snapshot(identity, internal) != snapshot:
                    fault("INVALID_STATE")
        else:
            identity = selection["snapshotId"]
            snapshot = store._project_snapshot(identity, internal)
    else:
        identity = digest(snapshot)
    ticket.pay("definition traversal", work=1 + len(snapshot["state"]["definitions"]))
    record = next(
        (
            r
            for r in snapshot["state"]["definitions"]
            if r["layer"] == "query" and r["id"] == definition
        ),
        None,
    )
    if record is None:
        fault("INVALID_REQUEST", field="dependency")
    raw = record["payload"]
    ticket.pay(
        "definition decode",
        bytes_=32 * len(raw) + 4096,
        objects=8 * len(raw) + 128,
        work=8 * len(raw) + 128,
    )
    try:
        value = json.loads(raw)
        if type(value) is not dict or set(value) - {"text", "references", "descriptor"}:
            fault("INVALID_STATE")
        if not scalar(value.get("text")) or (
            "references" in value and type(value["references"]) is not list
        ):
            fault("INVALID_STATE")
        version = snapshot["dependencyVector"]["query:" + definition]
        if type(version) is not int or version < 0:
            fault("INVALID_STATE")
        common = {
            "projectId": project,
            "definitionId": definition,
            "baseProjectRevision": snapshot["projectRevision"],
            "inputSnapshotId": identity,
            "definitionVersion": version,
            "definitionSha256": digest(value),
        }
        if "descriptor" not in value:
            return {"kind": "legacy", **common, "text": value["text"]}, snapshot
        descriptor = value["descriptor"]
        if (
            type(descriptor) is not dict
            or len(descriptor) != 6
            or set(descriptor)
            != {"version", "name", "description", "scope", "capabilityQuestion", "source"}
            or type(descriptor["version"]) is not int
            or descriptor["version"] != 1
        ):
            fault("INVALID_STATE")
        visible = draft(
            {k: v for k, v in descriptor.items() if k != "version"} | {"sparql": value["text"]},
            stored=True,
        )
        if visible["sparql"] != value["text"] or visible["name"] != descriptor["name"]:
            fault("INVALID_STATE")
        return {
            "kind": "managed",
            **common,
            "descriptorVersion": 1,
            "descriptorSha256": digest(descriptor),
            "draft": visible,
        }, snapshot
    except (KeyError, TypeError, ValueError) as error:
        from ontolearn_engine.job_store import JobFault

        if isinstance(error, JobFault):
            raise
        fault("INVALID_STATE")


def load(store, params, ticket):
    ticket.check(store)
    store._valid("params_query.definition.load", params)
    with store._read():
        result, _ = _record(
            store, params["projectId"], params["definitionId"], params["selection"], ticket
        )
        if not store.contract.validate("result_query.definition.load", result):
            fault("INVALID_STATE")
        return ticket.deliver(result)


def prepare(store, params, implementation, limits, registry_hash, ticket):
    ticket.check(store)
    store._valid("params_query.execution.prepare", params)
    project, binding = params["projectId"], params["definitionBinding"]
    if project != ticket.project:
        fault("PERMISSION_DENIED")
    visible = draft(params["visibleDraft"])
    with store._transaction():
        claim = store._db.execute(
            "SELECT * FROM operation_claims WHERE operation=?", (params["operationId"],)
        ).fetchone()
        original = None
        if claim:
            original = store.get_job(project, claim["job"])
            if (
                original["capability"] != "query.execute"
                or original["operationId"] != params["operationId"]
            ):
                fault("IDENTITY_CONFLICT")
            original = store._accepted_job(
                claim,
                project,
                "query.execute",
                original["input"],
                None,
                original["implementation"],
                original["limits"],
            )
            context = store.job_context(original["jobId"])
            snapshot = context["snapshot"]
            selection = store.blob(project, original["input"]["parametersHash"])["inputSelection"]
            if params["selection"]["kind"] != selection:
                fault("IDENTITY_CONFLICT")
            if (
                selection == "historical"
                and params["selection"]["snapshotId"] != original["inputSnapshotId"]
            ):
                fault("IDENTITY_CONFLICT")
        else:
            snapshot = None
        record, snapshot = _record(
            store, project, binding["definitionId"], params["selection"], ticket, snapshot=snapshot
        )
        actual = {key: record.get(key) for key in binding}
        if actual != binding:
            fault("IDENTITY_CONFLICT")
        if record["kind"] != "managed" or record["draft"] != visible:
            fault("INVALID_STATE")
        if visible["scope"] != "asserted":
            fault("INVALID_REQUEST", field="identity")
        if original:
            input_ = original["input"]
            implementation, limits = original["implementation"], original["limits"]
            if input_["definitionId"] != binding["definitionId"]:
                fault("IDENTITY_CONFLICT")
        else:
            ticket.pay("parameters blob", bytes_=4096, objects=128, work=1024)
            parameters = {"inputSelection": params["selection"]["kind"]}
            input_ = {
                "inputSnapshotId": record["inputSnapshotId"],
                "scope": "asserted",
                "definitionId": binding["definitionId"],
                "derivedResultIds": [],
                "parametersHash": store.put_blob(project, parameters),
                "preparedPlanRef": None,
            }
            # Current material came from the same coherent pure projection above;
            # historical/accepted inputs keep their original strict evidence path.
            # Preparing parameters does not persist a snapshot. Actual create_job
            # must materialize this exact digest in its normal writer transaction.
            from ontolearn_engine.resources import semantic_identity

            if implementation != semantic_identity():
                fault("IDENTITY_CONFLICT")
            store.prepare_query_request(
                project, input_, parameters, snapshot, implementation, None, live=False
            )
        result = {
            "projectId": project,
            "operationId": params["operationId"],
            "definitionBinding": actual,
            "input": input_,
            "executionIdentity": {
                "implementation": implementation,
                "limits": limits,
                "registryHash": registry_hash,
            },
        }
        if not store.contract.validate("result_query.execution.prepare", result):
            fault("INVALID_STATE")
        return ticket.deliver(result)


class QueryDispatchAuthority(ABC):
    """Actual external issuer/dispatch bridge injection; no implementation here.

    take authenticates original main owner/incarnation, generation, selection,
    normalized original frame and prepaid read work. It returns None only for a
    genuinely ordinary dispatch, and must reject a missing/stale registered query
    dispatch. A local object/flag alone is not a cross-process grant.
    """

    @abstractmethod
    def take(self, actor, request):
        raise NotImplementedError

    @abstractmethod
    def check(self, ticket, actor, store):
        """Authenticate current originals/purpose/generation; reject stale/replay."""
        raise NotImplementedError

    @abstractmethod
    def finish(self, ticket, *, emitted, failure=None):
        raise NotImplementedError


@dataclass(eq=False)
class ProjectGetReadTicket:
    issuer: QueryDispatchAuthority
    read: QueryRead
    request_id: str
    project: str
    revision: int
    snapshot: str
    owner_id: str
    selection_seq: int
    generation: int
    used: bool = False
    consuming: bool = False
    finishing: bool = False
    finished: bool = False
    terminal_observed: bool = False
    emitted_observed: bool = False
    failure_observed: object = None

    def consume(self, actor, store, project):
        if (
            self.used
            or self.consuming
            or self.finished
            or actor.query_dispatch is not self.issuer
            or self.read.actor is not actor
            or self.read.store is not store
            or self.project != project
            or self.owner_id != actor.ordinary.owner_id
            or self.selection_seq < 1
            or self.generation < 0
        ):
            fault("PERMISSION_DENIED")
        self.consuming = True
        try:
            self.issuer.check(self, actor, store)
            self.read.check(store)
            self.read.before_store(store, "query_read.project.get", {"projectId": project})
            self.issuer.check(self, actor, store)
            self.read._originals(store)
            if self.used or self.finished or actor.query_dispatch is not self.issuer:
                fault("PERMISSION_DENIED")
            self.used = True
        finally:
            self.consuming = False

    def reply(self, store, value):
        self.issuer.check(self, self.read.actor, store)
        self.read.check(store)
        if value["projectRevision"] != self.revision or value["inputSnapshotId"] != self.snapshot:
            fault("IDENTITY_CONFLICT")
        return self.read.deliver(value)

    def finish(self, *, emitted, failure=None):
        if self.finished or self.finishing:
            return
        # Preserve the first actual terminal event across an unknown callback.
        # The real issuer must reconcile this same ticket idempotently, never
        # issue another credit or turn successful emission into a failed event.
        if not self.terminal_observed:
            self.terminal_observed = True
            self.emitted_observed = emitted
            self.failure_observed = failure
        self.finishing = True
        try:
            self.issuer.finish(self, emitted=self.emitted_observed, failure=self.failure_observed)
            self.finished = True
        finally:
            self.finishing = False
