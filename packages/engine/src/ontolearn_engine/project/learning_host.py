"""Session-owned learning host: named bridge over the T01 learning ledger.

Like CheckpointHost this object owns no wire authority of its own: the
MainlineHost authorizes the selected project, prepays the Store read budget
and only then dispatches into learning_ledger. The persisted ontology-model
evidence adapter is holder-scoped and cleared after each check so no stale
evidence can leak between attempts.
"""

import json

from ontolearn_engine.project import learning_ledger

A01_STATUS = ("urn:ontolearn:learning:alarm/A01", "urn:ontolearn:learning:status")


class _PersistedOntologyTools:
    """Owner-supplied persisted-evidence adapter for the wired learning checks.

    ``evidence`` keeps serving the single-check ``ontology-model`` task while
    ``evidence_by_check`` carries one entry per check for multi-check tasks
    such as ``query`` (Q-01/Q-02). ``execute_check`` resolves per-check first
    and falls back to the single-evidence slot only for None.
    """

    def __init__(self):
        self.evidence = None
        self.evidence_by_check: dict = {}

    def execute_check(self, check_id, context):
        evidence = self.evidence_by_check.get(check_id)
        if evidence is None:
            evidence = self.evidence
        if evidence is None or evidence.check_id != check_id or evidence.context != context:
            raise ValueError("Persisted ontology-model evidence required")
        return evidence

    def clear(self):
        self.evidence = None
        self.evidence_by_check = {}


class LearningHost:
    def __init__(self, owner, root=None):
        self.owner = owner
        self._root = root
        self._bare = None
        self._wired = None
        self._baseline = None
        self.tools = _PersistedOntologyTools()

    def root(self):
        if self._root is None:
            from ontolearn_engine.learning import default_learning_root

            self._root = default_learning_root()
        return self._root

    def bare_service(self):
        if self._bare is None:
            from ontolearn_engine.learning.service import LearningService

            self._bare = LearningService(self.root())
        return self._bare

    def wired_service(self):
        if self._wired is None:
            from ontolearn_engine.learning.service import LearningService

            self._wired = LearningService(self.root(), self.tools)
        return self._wired

    def baseline_triples(self):
        if self._baseline is None:
            self._baseline = learning_ledger.baseline_triples(self.root())
        return self._baseline

    def q02_triples(self):
        """G-base with alarm/A01 status moved from Open to Closed.

        The literal strings stay the exact N3 forms used by
        learning_ledger._state_triples / baseline_triples.
        """
        return (self.baseline_triples() - {(*A01_STATUS, '"Open"')}) | {(*A01_STATUS, '"Closed"')}

    def ontology_evidence(self, context, snapshot_ref, present, baseline, assistance):
        from ontolearn_engine.learning.service import ToolEvidence

        added = sorted(present - baseline)
        removed = sorted(baseline - present)
        return ToolEvidence(
            evidence_id=snapshot_ref,
            context=context,
            check_id="ontology-model",
            status="succeeded",
            payload={
                "addedTriples": [{"subject": s, "predicate": p, "object": o} for s, p, o in added],
                "removedTriples": [
                    {"subject": s, "predicate": p, "object": o} for s, p, o in removed
                ],
            },
            assistance=assistance,
            provenance="persisted-domain-tool",
        )

    def _query_check_payload(self, pay):
        """Project one real query payload into the Q-01/Q-02 evidence shape."""
        if pay["query"].get("type") != "SELECT":
            return {"type": pay["query"].get("type")}
        variables = list(pay["query"]["variables"])
        rows = [dict(zip(variables, row, strict=False)) for row in pay["query"]["rows"]]
        return {"variables": variables, "rows": rows, "scope": "current-asserted"}

    def query_evidences(
        self, store, project, internal, context, snapshot_ref, min_claim_rowid, assistance
    ):
        """Derive Q-01/Q-02 evidence from real persisted query.execute jobs.

        jobs.project and operation_claims.project both store the public project
        UUID. Only jobs whose operation claim landed after the attempt's
        ``min_claim_rowid`` count, so a fresh attempt always demands freshly
        executed queries.
        """
        from ontolearn_engine.learning.service import ToolEvidence

        g_base = self.baseline_triples()
        g_q02 = self.q02_triples()
        candidates = []
        # Bound parameters only: the public project UUID and the minimum claim
        # rowid; no caller text is ever interpolated into a statement. Only job
        # claims (job NOT NULL) name executable jobs; application claims have
        # their job column NULL by construction.
        claims = store._db.execute(
            "SELECT rowid,job FROM operation_claims WHERE project=? AND rowid>? ORDER BY rowid",
            (project, min_claim_rowid),
        ).fetchall()
        for claim in claims:
            if claim["job"] is None:
                continue
            dto_row = store._db.execute(
                "SELECT dto FROM jobs WHERE id=?", (claim["job"],)
            ).fetchone()
            if dto_row is None:
                continue
            dto = json.loads(dto_row["dto"])
            if dto.get("capability") != "query.execute" or dto.get("projectId") != project:
                continue
            snap = store._project_snapshot(dto["inputSnapshotId"], internal)
            parameters = store.blob(project, dto["input"]["parametersHash"])
            candidates.append(
                {
                    "claim_rowid": claim["rowid"],
                    "jobId": claim["job"],
                    "dto": dto,
                    "snap_triples": learning_ledger._state_triples(snap["state"]),
                    "input_selection": parameters.get("inputSelection"),
                }
            )

        def unavailable(check_id):
            return ToolEvidence(
                f"missing:{context.attempt_id}:{check_id}",
                context,
                check_id,
                "unavailable",
                None,
                assistance,
                "persisted-domain-tool",
            )

        def persisted(check_id, evidence_id, status, payload):
            return ToolEvidence(
                evidence_id,
                context,
                check_id,
                status,
                payload,
                assistance,
                "persisted-domain-tool",
            )

        evidences = {}
        base_jobs = [item for item in candidates if item["snap_triples"] == g_base]
        j1 = base_jobs[-1] if base_jobs else None
        if j1 is None:
            evidences["Q-01"] = unavailable("Q-01")
        elif j1["dto"]["state"] != "succeeded":
            evidences["Q-01"] = persisted("Q-01", j1["jobId"], j1["dto"]["state"], None)
        elif j1["input_selection"] != "current" or j1["dto"]["input"].get("scope") != "asserted":
            evidences["Q-01"] = persisted("Q-01", j1["jobId"], "historical", None)
        else:
            result1 = (j1["dto"].get("resultRef") or {}).get("resultId")
            if not result1:
                evidences["Q-01"] = unavailable("Q-01")
            else:
                meta1, pay1 = store.semantic_result(project, result1)
                evidences["Q-01"] = persisted(
                    "Q-01", meta1["resultId"], "succeeded", self._query_check_payload(pay1)
                )

        # Q-02 must run after the Q-01 baseline, against the A01=Closed state.
        min_q2_rowid = j1["claim_rowid"] if j1 is not None else min_claim_rowid
        after_q2 = [item for item in candidates if item["claim_rowid"] > min_q2_rowid]
        q02_jobs = [item for item in after_q2 if item["snap_triples"] == g_q02]
        current_triples = learning_ledger._state_triples(store.state(internal))
        # The Q-02 mismatch window includes the Q-01 baseline query itself: a
        # succeeded current/asserted run against the still-open G-base state is
        # itself the "A01 was never closed" failure, not an unavailable tool.
        bad_jobs = [
            item
            for item in candidates
            if item["claim_rowid"] >= min_q2_rowid
            and item["dto"]["inputSnapshotId"] == snapshot_ref
            and item["dto"]["state"] == "succeeded"
            and bool((item["dto"].get("resultRef") or {}).get("resultId"))
            and item["input_selection"] == "current"
            and item["dto"]["input"].get("scope") == "asserted"
        ]
        if current_triples != g_q02:
            if q02_jobs:
                # The attempt once reached the A01=Closed state and queried it,
                # then further domain edits moved the state away again.
                evidences["Q-02"] = persisted("Q-02", q02_jobs[-1]["jobId"], "stale", None)
            elif bad_jobs:
                # A succeeded current/asserted query ran against a state that is
                # not the A01=Closed domain Q-02 demands (wrong fact edited, or
                # the state was never moved off G-base); the mismatched payload
                # reads needs-repair through the LearningService comparison.
                evidences["Q-02"] = persisted(
                    "Q-02",
                    bad_jobs[-1]["dto"]["resultRef"]["resultId"],
                    "succeeded",
                    {
                        "variables": [],
                        "rows": [],
                        "scope": "current-asserted",
                        "domainStateMismatch": True,
                    },
                )
            else:
                evidences["Q-02"] = unavailable("Q-02")
        elif not q02_jobs:
            evidences["Q-02"] = unavailable("Q-02")
        else:
            j2 = q02_jobs[-1]
            if j2["dto"]["state"] != "succeeded":
                evidences["Q-02"] = persisted("Q-02", j2["jobId"], j2["dto"]["state"], None)
            elif (
                j2["input_selection"] != "current" or j2["dto"]["input"].get("scope") != "asserted"
            ):
                evidences["Q-02"] = persisted("Q-02", j2["jobId"], "historical", None)
            else:
                result2 = (j2["dto"].get("resultRef") or {}).get("resultId")
                if not result2:
                    evidences["Q-02"] = unavailable("Q-02")
                elif j2["dto"]["inputSnapshotId"] != snapshot_ref or (
                    store.result_get(project, result2).get("state") != "current"
                ):
                    evidences["Q-02"] = persisted("Q-02", result2, "stale", None)
                else:
                    meta2, pay2 = store.semantic_result(project, result2)
                    evidences["Q-02"] = persisted(
                        "Q-02", meta2["resultId"], "succeeded", self._query_check_payload(pay2)
                    )
        return evidences

    def close(self):
        self._bare = None
        self._wired = None
        self._baseline = None
        self.tools.clear()

    def dispatch(self, method, params, budget):
        from ontolearn_engine.job_store import fault
        from ontolearn_engine.storage import Conflict

        store = self.owner.store
        budget.reserve_store("learning ledger material", params)
        origin = {
            "hostClientId": self.owner.host,
            "engineSessionId": self.owner.session,
        }
        try:
            self.owner.authorize(params)
            return learning_ledger.dispatch(store, method, params, self, origin)
        except Conflict as error:
            code = {
                "identity": "IDENTITY_CONFLICT",
                "input": "INVALID_REQUEST",
                "revision": "REVISION_CONFLICT",
            }.get(error.category, "INVALID_STATE")
            if code == "INVALID_REQUEST":
                fault(code, field="params")
            detail = error.params or {}
            if code == "REVISION_CONFLICT" and all(
                type(detail.get(key)) is int for key in ("expected", "actual")
            ):
                fault(code, expected=detail["expected"], actual=detail["actual"])
            fault(code)
