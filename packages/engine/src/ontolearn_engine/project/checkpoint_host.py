"""Session-owned bounded checkpoint/restore refs; wire values mint no authority.

Durable evidence lives in job_details/job_plans/job_confirmations; this book only
accounts transient list cursors and preview announcements inside the mainline
ReadLimits/HELD_BYTES budgets, and is cleared on MainlineHost.close().
"""

from uuid import uuid4

from ontolearn_engine.job_store import fault
from ontolearn_engine.project import checkpoints, format3
from ontolearn_engine.storage import Conflict, canonical


class CheckpointHost:
    MAX_ENTRIES = 16
    MAX_ENCODED = 262144
    TTL_MS = 60000

    def __init__(self, owner):
        self.owner = owner
        self.entries = {}

    def _purge(self):
        now = self.owner.store.now_ms()
        for key, record in list(self.entries.items()):
            if now >= record["expires"]:
                del self.entries[key]

    @property
    def encoded(self):
        return sum(
            len(canonical(value).encode("utf-8")) + len(key) for key, value in self.entries.items()
        )

    @property
    def scalar(self):
        return 32 * self.encoded

    @property
    def objects(self):
        return 2 * self.encoded + 128 * len(self.entries)

    def close(self):
        self.entries.clear()

    def _hold(self, kind, value, budget):
        self._purge()
        size = len(canonical(value).encode("utf-8")) + 36
        if len(self.entries) >= self.MAX_ENTRIES or self.encoded + size > self.MAX_ENCODED:
            fault("RESOURCE_LIMIT", resource="memory")
        budget.reserve(
            "checkpoint retained reference",
            bytes_=32 * size,
            objects=2 * size + 128,
            work=64 * size,
        )
        token = str(uuid4())
        if token in self.entries:
            fault("INVALID_STATE")
        self.entries[token] = {
            "kind": kind,
            "owner": self.owner.owner_id,
            "expires": self.owner.store.now_ms() + self.TTL_MS,
            **value,
        }
        return token

    def _take(self, token, kind):
        self._purge()
        value = self.entries.get(token)
        if value is None or value["kind"] != kind or value["owner"] != self.owner.owner_id:
            fault("INVALID_STATE")
        return value

    def hold_cursor(self, public, value):
        budget = self.owner._budget()
        return self._hold(
            "list-cursor",
            {"projectId": public, "generation": self.owner.generation, **value},
            budget,
        )

    def take_cursor(self, token, public):
        record = self._take(token, "list-cursor")
        if (
            record["projectId"] != public
            or record["generation"] != self.owner.generation
            or public != self.owner.selected
        ):
            fault("PERMISSION_DENIED")
        del self.entries[token]
        return record

    def hold_preview(self, preview_ref, public):
        budget = self.owner._budget()
        self._hold(
            "restore-preview",
            {"projectId": public, "generation": self.owner.generation, "previewRef": preview_ref},
            budget,
        )

    def dispatch(self, method, params, budget):
        store = self.owner.store
        budget.reserve_store("checkpoint material and history", params)
        origin = {
            "hostClientId": self.owner.host,
            "engineSessionId": self.owner.session,
        }
        try:
            # Selected-project fencing for the mutating/reading routes; exact
            # evidence lookups bypass volatile selection like management.apply.
            if method not in {"project.restore.operation.get", "project.restore.apply"}:
                self.owner.authorize(params)
            return checkpoints.dispatch(store, method, params, self, origin)
        except format3.Format3Fault:
            # A checkpoint ref outside the verified ledger (cross-project,
            # future or forged) is simply absent, never a structure fault.
            fault("NOT_FOUND", resource="checkpoint")
        except Conflict as error:
            code = {
                "identity": "IDENTITY_CONFLICT",
                "input": "INVALID_REQUEST",
                "revision": "REVISION_CONFLICT",
            }.get(error.category, "INVALID_STATE")
            if code == "REVISION_CONFLICT":
                params = error.params or {}
                # REVISION_CONFLICT params are integers; only forward axes that
                # already satisfy the shared error contract.
                if all(type(params.get(key)) is int for key in ("expected", "actual")):
                    fault(code, expected=params["expected"], actual=params["actual"])
                fault("INVALID_STATE")
            fault(code, **({"field": "params"} if code == "INVALID_REQUEST" else {}))
