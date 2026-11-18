"""Session-owned quality host: named bridge over the quality projections.

Like LearningHost this object owns no wire authority of its own: the
MainlineHost authorizes the selected project, prepays the Store read budget
and only then dispatches into quality_definitions. Reads never mint snapshots
or write scopes; prepare only interns the frozen job-input parameters.
"""

from ontolearn_engine.project import quality_definitions


class QualityHost:
    def __init__(self, owner):
        self.owner = owner

    def dispatch(self, method, params, budget):
        from ontolearn_engine.job_store import fault
        from ontolearn_engine.project.query_definitions import query_read
        from ontolearn_engine.storage import Conflict

        if method not in quality_definitions.METHODS:
            fault("PERMISSION_DENIED")
        store = self.owner.store
        # The single full Store prepayment happens inside query_read's
        # before_store (reserve_store + preflight + recheck); prepaying again
        # here would double-charge the held-byte budget for one request.
        try:
            with query_read(
                self.owner.actor, method, params, methods=quality_definitions.METHODS
            ) as ticket:
                if method == "project.quality.read":
                    return quality_definitions.read(store, params, ticket)
                return quality_definitions.prepare(store, params, ticket)
        except Conflict as error:
            code = {
                "identity": "IDENTITY_CONFLICT",
                "input": "INVALID_REQUEST",
                "revision": "REVISION_CONFLICT",
            }.get(error.category, "INVALID_STATE")
            if code == "INVALID_REQUEST":
                fault(code, field="params")
            fault(code)
