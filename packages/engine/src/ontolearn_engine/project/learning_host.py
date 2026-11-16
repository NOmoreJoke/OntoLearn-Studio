"""Session-owned learning host: named bridge over the T01 learning ledger.

Like CheckpointHost this object owns no wire authority of its own: the
MainlineHost authorizes the selected project, prepays the Store read budget
and only then dispatches into learning_ledger. The persisted ontology-model
evidence adapter is holder-scoped and cleared after each check so no stale
evidence can leak between attempts.
"""

from ontolearn_engine.project import learning_ledger


class _PersistedOntologyTools:
    """Owner-supplied persisted-evidence adapter for the wired ontology-model check."""

    def __init__(self):
        self.evidence = None

    def execute_check(self, check_id, context):
        evidence = self.evidence
        if evidence is None or evidence.check_id != check_id or evidence.context != context:
            raise ValueError("Persisted ontology-model evidence required")
        return evidence


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

    def close(self):
        self._bare = None
        self._wired = None
        self._baseline = None
        self.tools.evidence = None

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
