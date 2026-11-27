"""Private ordinary-open leases. No production authority or physical read ticket is issued here.

The finite book is an engineering rejection boundary, not an SQLite work/RSS proof.
Accepted Jobs remain owned by Coordinator's original queued/active records and immutable
Store claims. This module never turns that responsibility into external request authority.
"""

import json
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from uuid import uuid4

from ontolearn_engine.job_store import fault
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import canonical

MAX_ACTIONS = 2
MAX_CHOICES = 64
BOOK_BYTES = 262144
BOOK_OBJECTS = 4096
MAX_SEQUENCE = 9007199254740991


class OrdinaryReadAuthority(ABC):
    """Trusted injection seam only. There is deliberately no concrete production issuer.

    allows_owner must be finite and perform no Store/SQL reads. read_scope must be
    an already approved same-store physical/read-work ticket, entered before any
    choices scan or actual project.get. A DTO, UUID, environment value, or subclass
    name alone supplies neither operation: callers must inject the actual issuer.

    The scope owns read material and staging through validation and handoff. On
    failure its issuer retains any material reachable through the original error/
    traceback; lexical __exit__ alone must not refund that holding. The library
    never reports a failed physical holding as released. Test scopes are doubles,
    not production physical/read-work issuers.
    """

    @property
    @abstractmethod
    def owner_id(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def allows_owner(self, store, session: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def read_scope(self, store, session: str, purpose: str, project: str | None):
        raise NotImplementedError


@dataclass(eq=False, slots=True)
class _ReadTicket:
    book: object
    store: object
    purpose: str
    project: str | None
    used: bool = False


@dataclass(slots=True)
class _Action:
    action_id: str
    seq: int
    project_id: str
    lease_ref: str
    choice_ref: str
    state: str = "ACTION"
    project: dict | None = None
    retained_bytes: int = 1024
    retained_objects: int = 16


def _sequence(value):
    return type(value) is int and 1 <= value <= MAX_SEQUENCE


def _measure(project):
    # The transport owns its finite decode. Reserve our additional retained copy
    # before cloning/freezing it; no claim about the original Store allocation.
    raw = canonical(project).encode("utf-8")
    vector = project["dependencyVector"]
    return 4 * len(raw) + 128 * len(vector) + 1024, 16 + 3 * len(vector)


def consume_choices_ticket(ticket, store):
    if not isinstance(ticket, _ReadTicket):
        fault("PERMISSION_DENIED")
    ticket.book.consume(ticket, store, "choices", None)


class OrdinaryLibrary:
    def __init__(self, actor, authority=None):
        self.actor = actor
        self.authority = authority if isinstance(authority, OrdinaryReadAuthority) else None
        self.owner_id = None
        if self.authority is not None:
            owner = self.authority.owner_id
            if not CONTRACT.validate("id", owner):
                fault("PERMISSION_DENIED")
            self.owner_id = owner
        self._choices = {}
        self._menu_seq = 0
        self._menu_reply = None
        self._actions = {}
        self._selected = None
        self._latest = 0
        self._closed_through = 0
        self._reading = None
        # Constant owner book/issuer state remains charged for this actor lifetime.
        self._choice_bytes = 4096
        self._choice_objects = 32

    def enabled(self):
        return (
            self.authority is not None
            and self.actor.profile == "legacy2"
            and not self.actor.test_mode
            and self.actor.session is not None
            and self.authority.allows_owner(self.actor.store, self.actor.session) is True
        )

    def require_owner(self, owner):
        if not self.enabled() or owner != self.owner_id:
            fault("PERMISSION_DENIED")

    def projects(self):
        # ACTION/JOB/UNKNOWN never enter ordinary _authorize.
        if not self.enabled() or self._selected is None:
            return frozenset()
        return frozenset([self._selected.project_id])

    def _room(self, *, extra_bytes=0, extra_objects=0, replacing=None):
        records = list(self._actions.values())
        if self._selected is not None:
            records.append(self._selected)
        used_bytes = self._choice_bytes + sum(
            r.retained_bytes for r in records if r is not replacing
        )
        used_objects = self._choice_objects + sum(
            r.retained_objects for r in records if r is not replacing
        )
        if used_bytes + extra_bytes > BOOK_BYTES or used_objects + extra_objects > BOOK_OBJECTS:
            fault("INVALID_STATE")

    @contextmanager
    def _read(self, purpose, project):
        self.require_owner(self.owner_id)
        if self._reading is not None:
            fault("INVALID_STATE")
        # No Store call has occurred. Missing tickets/default authority deny here.
        scope = self.authority.read_scope(self.actor.store, self.actor.session, purpose, project)
        if scope is None:
            fault("PERMISSION_DENIED")
        with scope:
            ticket = _ReadTicket(self, self.actor.store, purpose, project)
            self._reading = ticket
            try:
                yield ticket
            finally:
                self._reading = None

    def consume(self, ticket, store, purpose, project):
        if (
            ticket is not self._reading
            or ticket.store is not store
            or ticket.purpose != purpose
            or ticket.project != project
            or ticket.used
        ):
            fault("PERMISSION_DENIED")
        self.require_owner(self.owner_id)
        ticket.used = True

    def _live(self, action_id, seq):
        record = self._actions.get(seq)
        if self._selected is not None and self._selected.seq == seq:
            record = self._selected
        if record is not None and record.action_id != action_id:
            fault("INVALID_STATE")
        return record

    def _fit(self, reply):
        envelope = {
            "kind": "response",
            "protocolVersion": 2,
            "id": "00000000-0000-4000-8000-000000000000",
            "engineSessionId": self.actor.session,
            "method": "ordinary.library",
            "ok": True,
            "result": reply,
        }
        if CONTRACT.encoded_size(reply) > self.actor.limits["maxPageBytes"]:
            fault("RESOURCE_LIMIT", resource="page")
        if CONTRACT.encoded_size(envelope) > self.actor.limits["maxFrameBytes"]:
            fault("RESOURCE_LIMIT", resource="frame")
        return reply

    def _reply(self, op, owner, record):
        return self._fit(
            {
                "op": op,
                "ownerId": owner,
                "actionId": record.action_id,
                "actionSeq": record.seq,
                "leaseRef": record.lease_ref,
                "project": json.loads(canonical(record.project)),
            }
        )

    def dispatch(self, params):
        if not CONTRACT.validate("params_ordinary.library", params):
            fault("INVALID_REQUEST", field="params")
        self.require_owner(params["ownerId"])
        op = params["op"]
        if op == "choices":
            return self.choices(params["menuSeq"])
        action_id, seq = params["actionId"], params["actionSeq"]
        record = self._live(action_id, seq)
        if op == "release":
            reply = self._fit(
                {"op": op, "ownerId": self.owner_id, "actionId": action_id, "actionSeq": seq}
            )
            if record is not None:
                if record is self._selected:
                    self._selected = None
                else:
                    del self._actions[seq]
            # Only absent, closed historical identity is forgotten. Never infer it.
            self._closed_through = max(self._closed_through, seq)
            self._latest = max(self._latest, seq)
            return reply
        if record is None and seq <= self._closed_through:
            fault("PERMISSION_DENIED")
        if op == "commit":
            if record is None or seq != self._latest or record.lease_ref != params["leaseRef"]:
                fault("PERMISSION_DENIED")
            if record.state == "SELECTED":
                return self._reply(op, self.owner_id, record)
            if record.state != "VERIFIED" or (
                self._selected is not None and self._selected is not record
            ):
                fault("INVALID_STATE")
            reply = self._reply(op, self.owner_id, record)
            record.state = "SELECTED"
            self._actions.pop(seq)
            self._selected = record
            return reply
        if seq < self._latest:
            fault("PERMISSION_DENIED")
        if record is not None:
            if record.choice_ref != params["choiceRef"]:
                fault("INVALID_STATE")
            if record.state not in {"VERIFIED", "SELECTED"}:
                fault("INVALID_STATE")
            return self._reply(op, self.owner_id, record)
        if len(self._actions) >= MAX_ACTIONS:
            fault("INVALID_STATE")
        project = self._choices.get(params["choiceRef"])
        if project is None:
            fault("PERMISSION_DENIED")
        self._room(extra_bytes=1024, extra_objects=16)
        self._latest = seq
        record = _Action(action_id, seq, project, str(uuid4()), params["choiceRef"])
        self._actions[seq] = record
        try:
            with self._read("project.get", project) as ticket:
                result = None
                try:
                    result = self.actor.ordinary_project_get(self, ticket, project)
                    if (
                        not CONTRACT.validate("result_project.get", result)
                        or result["projectId"] != project
                        or seq != self._latest
                    ):
                        fault("INVALID_STATE")
                    size, objects = _measure(result)
                    self._room(extra_bytes=size, extra_objects=objects, replacing=record)
                    # Reserve the retained project/reply holding before either clone.
                    # The original result and transient encoder material remain scope-owned.
                    record.retained_bytes, record.retained_objects = size, objects
                    record.project = json.loads(canonical(result))
                    record.state = "VERIFIED"
                    reply = self._reply(op, self.owner_id, record)
                    result = None
                    return reply
                finally:
                    # On failure the original exception/traceback is delivered to
                    # read_scope.__exit__; its issuer retains reachable failed holding.
                    result = None
        except BaseException:
            # Only this acquire's admission reference is withdrawn; preserve first error.
            if self._actions.get(seq) is record:
                del self._actions[seq]
            self._closed_through = max(self._closed_through, seq)
            raise

    def choices(self, menu_seq):
        if not _sequence(menu_seq):
            fault("INVALID_REQUEST", field="params")
        if menu_seq < self._menu_seq:
            fault("PERMISSION_DENIED")
        if menu_seq == self._menu_seq and self._menu_reply is not None:
            return json.loads(canonical(self._menu_reply))
        with self._read("choices", None) as ticket:
            projects = choices = reply = result = mapping = None
            old_bytes, old_objects = self._choice_bytes, self._choice_objects
            try:
                projects = self.actor.store.ordinary_project_choices(
                    limit=MAX_CHOICES, _read_ticket=ticket
                )
                if not isinstance(projects, list) or len(projects) > MAX_CHOICES:
                    fault("RESOURCE_LIMIT", resource="page")
                if any(
                    not isinstance(p, dict)
                    or set(p) != {"projectId"}
                    or not CONTRACT.validate("id", p["projectId"])
                    for p in projects
                ) or len({p["projectId"] for p in projects}) != len(projects):
                    fault("INVALID_STATE")
                # All row IDs and newly issued refs are exact 36-byte ASCII UUIDs.
                # Compute the new retained menu bound before allocating its rows,
                # map, cached reply and returned reply. The old menu remains held.
                empty = {
                    "op": "choices",
                    "ownerId": self.owner_id,
                    "menuSeq": menu_seq,
                    "choices": [],
                }
                row_bytes = len('{"choiceRef":"","projectId":""}') + 72
                reply_bytes = (
                    len(canonical(empty).encode("utf-8"))
                    + len(projects) * row_bytes
                    + max(0, len(projects) - 1)
                )
                new_bytes, new_objects = 4096 + 4 * reply_bytes, 32 + 8 * len(projects)
                self._room(extra_bytes=new_bytes, extra_objects=new_objects)
                self._choice_bytes = old_bytes + new_bytes
                self._choice_objects = old_objects + new_objects
                choices = [
                    {"choiceRef": str(uuid4()), "projectId": p["projectId"]} for p in projects
                ]
                reply = {
                    "op": "choices",
                    "ownerId": self.owner_id,
                    "menuSeq": menu_seq,
                    "choices": choices,
                }
                self._fit(reply)
                result = json.loads(canonical(reply))
                mapping = {c["choiceRef"]: c["projectId"] for c in choices}
                # Synchronous transfer: both old and new are reserved through
                # replacing all strong old-menu fields; only then retire old book.
                self._choices = mapping
                self._menu_reply = reply
                self._menu_seq = menu_seq
                self._choice_bytes, self._choice_objects = new_bytes, new_objects
                projects = choices = reply = mapping = None
                return result
            except BaseException:
                self._choice_bytes, self._choice_objects = old_bytes, old_objects
                # The rejecting scope receives the original failure/traceback.
                # Its physical holding is not declared refunded by these book counters.
                raise
            finally:
                projects = choices = reply = result = mapping = None
