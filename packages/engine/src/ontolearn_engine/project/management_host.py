"""Session-owned bounded management refs. No wire value can mint authority."""

from uuid import uuid4

from ontolearn_engine.job_store import fault
from ontolearn_engine.project import management
from ontolearn_engine.project.project_lifecycle import library_evidence
from ontolearn_engine.storage import Conflict, canonical, digest


class ManagementHost:
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

    def _hold(self, value, budget):
        self._purge()
        size = len(canonical(value).encode("utf-8")) + 36
        if len(self.entries) >= self.MAX_ENTRIES or self.encoded + size > self.MAX_ENCODED:
            fault("RESOURCE_LIMIT", resource="memory")
        budget.reserve(
            "management retained reference",
            bytes_=32 * size,
            objects=2 * size + 128,
            work=64 * size,
        )
        token = str(uuid4())
        if token in self.entries:
            fault("INVALID_STATE")
        self.entries[token] = value
        return token

    def _take(self, token, kind):
        self._purge()
        value = self.entries.get(token)
        if value is None or value["kind"] != kind or value["owner"] != self.owner.owner_id:
            fault("INVALID_STATE")
        return value

    def _bound(self, value, public):
        if value["projectId"] != public or value["generation"] != self.owner.generation:
            fault("PERMISSION_DENIED")
        if value["action"]["kind"] != "restore-trash":
            internal = management.public_internal(self.owner.store, public)
            current = management.lifecycle(self.owner.store, internal)
            if (
                public != self.owner.selected
                or current["state"] != "active"
                or current != self.owner.selected_lifecycle
            ):
                fault("PERMISSION_DENIED")
        else:
            internal = management.public_internal(self.owner.store, public)
            if management.lifecycle(self.owner.store, internal)["state"] != "trashed":
                fault("INVALID_STATE")

    def item(self, public):
        store = self.owner.store
        internal = management.public_internal(store, public)
        cp = store.project_checkpoint(internal)
        return {
            "projectId": public,
            "domainRevision": cp["domainRevision"],
            "metadataVersion": cp["application"]["metadataVersion"],
            "metadata": cp["application"]["metadata"],
            "operationSequence": cp["operationSequence"],
            "checkpointRef": digest(cp),
            "lifecycle": management.lifecycle(store, internal),
        }

    def _catalog(self, params, budget):
        cursor = params["cursor"]
        if cursor is None:
            items = []
            for row in self.owner.store._db.execute(
                "SELECT public FROM public_projects ORDER BY public"
            ):
                item = self.item(row[0])
                state = (
                    "trashed"
                    if item["lifecycle"]["state"] == "trashed"
                    else "archived"
                    if item["metadata"]["archived"]
                    else "active"
                )
                if state == params["state"]:
                    items.append(item)
            record = {
                "kind": "catalog",
                "owner": self.owner.owner_id,
                "expires": self.owner.store.now_ms() + self.TTL_MS,
                "state": params["state"],
                "pageSize": params["pageSize"],
                "snapshotId": str(uuid4()),
                "items": items,
                "offset": 0,
            }
        else:
            record = self._take(cursor, "catalog")
            if record["state"] != params["state"] or record["pageSize"] != params["pageSize"]:
                fault("CURSOR_MISMATCH")
            del self.entries[cursor]
        start = record["offset"]
        end = min(start + record["pageSize"], len(record["items"]))
        next_cursor = None
        if end < len(record["items"]):
            next_record = {**record, "offset": end}
            next_cursor = self._hold(next_record, budget)
        return {
            "catalogVersion": 1,
            "snapshotId": record["snapshotId"],
            "items": record["items"][start:end],
            "total": len(record["items"]),
            "offset": start,
            "nextCursor": next_cursor,
        }

    def dispatch(self, method, params, budget):
        store = self.owner.store
        budget.reserve_store("management material and history", params)
        try:
            if method == "project.library.status":
                return {
                    "libraryEvidenceRef": library_evidence(store),
                    "activeJobs": management.active_jobs(store),
                }
            if method == "project.management.catalog":
                return self._catalog(params, budget)
            public = params["projectId"]
            if method == "project.management.operation.get":
                return management.operation_get(
                    store, public, params["operationId"], params["requestHash"]
                )
            if method == "project.management.read":
                self.owner.authorize(params)
                return self.item(public)
            if method == "project.management.preview":
                action = management.action_value(params["action"])
                if action["kind"] != "restore-trash":
                    self.owner.authorize(params)
                document, seed = management.document(store, public, action)
                if (
                    document["checkpointRef"] != params["expectedCheckpointRef"]
                    or document["lifecycleVersion"] != params["expectedLifecycleVersion"]
                ):
                    fault("INVALID_STATE")
                expires = store.now_ms() + self.TTL_MS
                value = {
                    "kind": "preview",
                    "owner": self.owner.owner_id,
                    "expires": expires,
                    "projectId": public,
                    "generation": self.owner.generation,
                    "action": action,
                    "document": document,
                    "seed": seed,
                    "documentHash": digest({"action": action, "document": document}),
                }
                ref = self._hold(value, budget)
                return {
                    "managementPreviewVersion": 1,
                    "previewRef": ref,
                    "projectId": public,
                    "action": action,
                    "documentHash": value["documentHash"],
                    "document": document,
                    "expiresAtMs": expires,
                }
            if method == "project.management.confirm":
                preview = self._take(params["previewRef"], "preview")
                self._bound(preview, public)
                if params["documentHash"] != preview["documentHash"]:
                    fault("IDENTITY_CONFLICT")
                current, seed = management.document(store, public, preview["action"])
                if current != preview["document"] or seed != preview["seed"]:
                    fault("INVALID_STATE")
                value = {
                    "kind": "confirmation",
                    "owner": self.owner.owner_id,
                    "expires": preview["expires"],
                    "previewRef": params["previewRef"],
                    "projectId": public,
                    "generation": self.owner.generation,
                    "action": preview["action"],
                    "documentHash": preview["documentHash"],
                }
                ref = self._hold(value, budget)
                return {
                    "confirmationRef": ref,
                    "previewRef": params["previewRef"],
                    "documentHash": preview["documentHash"],
                    "projectId": public,
                    "kind": preview["action"]["kind"],
                }
            if method == "project.management.apply":
                # Exact evidence lookup precedes volatile refs: an acknowledged
                # commit is retryable even if selection/TTL subsequently changed.
                existing = management.operation_get(
                    store, public, params["operationId"], digest(params)
                )
                if existing["state"] == "applied":
                    return existing["result"]
                confirmation = self._take(params["confirmationRef"], "confirmation")
                self._bound(confirmation, public)
                preview = self._take(confirmation["previewRef"], "preview")
                self._bound(preview, public)
                if (
                    params["documentHash"] != preview["documentHash"]
                    or confirmation["documentHash"] != preview["documentHash"]
                ):
                    fault("IDENTITY_CONFLICT")
                result = store.commit(
                    None,
                    None,
                    params["operationId"],
                    None,
                    management={
                        "request": params,
                        "action": preview["action"],
                        "document": preview["document"],
                        "seed": preview["seed"],
                        "origin": {
                            "hostClientId": self.owner.host,
                            "engineSessionId": self.owner.session,
                            "permission": "library.create",
                        },
                        "readerLimits": self.owner.reader_limits,
                    },
                )
                # The durable receipt now owns exact retries; preview buffers
                # may be released without turning a lost ACK into replay.
                self.entries.pop(params["confirmationRef"], None)
                self.entries.pop(confirmation["previewRef"], None)
                # Do not publish or select a new project on receipt emission
                # failure. Selection is the separate named project.open action.
                return result
            fault("PERMISSION_DENIED")
        except Conflict as error:
            code = {"identity": "IDENTITY_CONFLICT", "input": "INVALID_REQUEST"}.get(
                error.category, "INVALID_STATE"
            )
            fault(code, **({"field": "params"} if code == "INVALID_REQUEST" else {}))
