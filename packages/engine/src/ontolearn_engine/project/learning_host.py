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
            meta1, pay1 = store.semantic_result(project, j1["dto"]["resultRef"]["resultId"])
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
            result2 = j2["dto"]["resultRef"]["resultId"]
            if j2["dto"]["state"] != "succeeded":
                evidences["Q-02"] = persisted("Q-02", j2["jobId"], j2["dto"]["state"], None)
            elif (
                j2["input_selection"] != "current" or j2["dto"]["input"].get("scope") != "asserted"
            ):
                evidences["Q-02"] = persisted("Q-02", j2["jobId"], "historical", None)
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

    # ---- B3 quality / transfer evidences (V-01, R-01, R-05, LX-01, transfers) ----
    #
    # All evidence below derives from real persisted reasoning.execute /
    # validation.execute jobs and the current Store state, exactly like the
    # Q-01/Q-02 adapters above: never from UI claims, never re-executed here.

    def _semantic_job_candidates(self, store, project, internal, min_claim_rowid):
        """Reasoning/validation jobs claimed inside this attempt window."""
        from ontolearn_engine.job_store import payload_from_rows

        candidates = []
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
            if dto.get("capability") not in ("reasoning.execute", "validation.execute"):
                continue
            if dto.get("projectId") != project:
                continue
            snap = store._project_snapshot(dto["inputSnapshotId"], internal)
            item = {
                "claim_rowid": claim["rowid"],
                "jobId": claim["job"],
                "dto": dto,
                "snap_triples": learning_ledger._state_triples(snap["state"]),
            }
            if dto["state"] == "succeeded" and dto.get("resultRef"):
                rows = store.result(dto["resultRef"]["resultId"])["payload"]
                item["payload"] = payload_from_rows(rows)
            candidates.append(item)
        return candidates

    def _b3_payload_evidence(self, evidences, check_id, item, payload, assistance):
        from ontolearn_engine.learning.service import ToolEvidence

        evidences[check_id] = ToolEvidence(
            item["dto"]["resultRef"]["resultId"],
            item["context"],
            check_id,
            "succeeded",
            payload,
            assistance,
            "persisted-domain-tool",
        )

    def b3_evidences(
        self,
        store,
        project,
        internal,
        context,
        snapshot_ref,
        min_claim_rowid,
        assistance,
        selected_origins,
    ):
        from ontolearn_engine.learning.service import ToolEvidence

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

        candidates = []
        for item in self._semantic_job_candidates(store, project, internal, min_claim_rowid):
            item["context"] = context
            candidates.append(item)
        reasoning = [c for c in candidates if c["dto"]["capability"] == "reasoning.execute"]
        validation = [c for c in candidates if c["dto"]["capability"] == "validation.execute"]

        g_base = self.baseline_triples()
        evidences = {}

        def plain_key(triple):
            # Reasoning payloads carry full N3 keys; the checks contract spells
            # subjects/predicates as plain IRIs and keeps objects as N3 terms.
            def plain(term):
                return term[1:-1] if isinstance(term, str) and term[:1] == "<" else term

            return (plain(triple[0]), plain(triple[1]), triple[2])

        def dict3(triple):
            subject, predicate, obj = plain_key(triple)
            return {"subject": subject, "predicate": predicate, "object": obj}

        def persisted_or_stale(check_id, item, payload):
            """Succeed only on the current snapshot; stale runs never pass."""
            result_id = item["dto"]["resultRef"]["resultId"]
            if item["dto"]["inputSnapshotId"] != snapshot_ref or (
                store.result_get(project, result_id).get("state") != "current"
            ):
                evidences[check_id] = ToolEvidence(
                    result_id,
                    context,
                    check_id,
                    "stale",
                    None,
                    assistance,
                    "persisted-domain-tool",
                )
            else:
                evidences[check_id] = ToolEvidence(
                    result_id,
                    context,
                    check_id,
                    "succeeded",
                    payload,
                    assistance,
                    "persisted-domain-tool",
                )

        def reasoning_views(item):
            body = item["payload"]["reasoning"]
            inferred = sorted([*body.get("rules", []), *body.get("rdfs", [])])
            traces = [
                {
                    "output": dict3(entry["result"]),
                    "rule": entry["rule"],
                    "inputs": [dict3(triple) for triple in entry["inputs"]],
                }
                for entry in body.get("evidence", [])
            ]
            return inferred, traces, body

        # R-01: plain G-base reasoning with exact i05-finite-6 output. The
        # dependency vector carries the ontology/mapping/rule families, so the
        # rule-side discriminator is presence of R-risk and absence of R-next.
        base_reasoning = [
            c for c in reasoning if c["dto"]["state"] == "succeeded" and c["snap_triples"] == g_base
        ]
        r01 = next(
            (
                c
                for c in reversed(base_reasoning)
                if "rule:R-risk" in c["dto"]["dependencyVector"]
                and "rule:R-next" not in c["dto"]["dependencyVector"]
            ),
            None,
        )
        if r01 is None:
            evidences["R-01"] = unavailable("R-01")
        else:
            inferred, traces, _body = reasoning_views(r01)
            self._b3_payload_evidence(
                evidences,
                "R-01",
                r01,
                {
                    "inferred": [dict3(t) for t in inferred],
                    "traces": traces,
                    "assertedFacts": [dict3(t) for t in r01["payload"]["assertedFacts"]],
                },
                assistance,
            )

        # R-05: same closure plus the unsupported-rule-chain warning for R-next.
        # The R-05 state adds the NeedsInspection class, so the exact G-base
        # snapshot equality no longer holds; require the G-base superset. The
        # LX-01 repair state (002 assignedTo L02) is a later, different step and
        # must never serve as the R-05 run.
        lx_repair = (
            "urn:ontolearn:learning:equipment/002",
            "urn:ontolearn:learning:assignedTo",
            "<urn:ontolearn:learning:person/L02>",
        )
        r05 = next(
            (
                c
                for c in reversed(reasoning)
                if c["dto"]["state"] == "succeeded"
                and "rule:R-next" in c["dto"]["dependencyVector"]
                and g_base <= c["snap_triples"]
                and lx_repair not in c["snap_triples"]
            ),
            None,
        )
        if r05 is None:
            evidences["R-05"] = unavailable("R-05")
        else:
            inferred, traces, body = reasoning_views(r05)
            warnings = [
                {"ruleId": text.split(":", 1)[1], "reason": "unsupported-rule-chain"}
                for text in body.get("warnings", [])
                if isinstance(text, str) and text.startswith("RULE_CHAIN_UNSUPPORTED:")
            ]
            # The one-stage engine never re-feeds rule outputs, so the blocked
            # chain derivations never enter the closure. The frozen expectation
            # lists exactly what the chain would have produced: each consumer
            # rule's heads instantiated over the matching producer outputs.
            forbidden = self._blocked_chain_outputs(
                store, internal, r05["dto"]["inputSnapshotId"], inferred
            )
            forbidden = sorted(
                {tuple(t) for t in forbidden if t[2] == "<urn:ontolearn:learning:NeedsInspection>"}
            )
            self._b3_payload_evidence(
                evidences,
                "R-05",
                r05,
                {
                    "forEachOrder": {
                        "inferred": [dict3(t) for t in inferred],
                        "traces": traces,
                        "warnings": warnings,
                    },
                    "forbidden": [dict3(t) for t in forbidden],
                },
                assistance,
            )

        # V-01: name-required validation before and after the 003-name repair.
        def name_required(item):
            return item["dto"]["input"].get("definitionId") == "name-required"

        v01_jobs = [c for c in validation if name_required(c) and "payload" in c]
        if not v01_jobs:
            evidences["V-01"] = unavailable("V-01")
        else:

            def violations(item):
                report = item["payload"].get("report", {})
                out = []
                for row in report.get("violations", []):
                    out.append(
                        {
                            "focusNode": self._plain(row["focus"]),
                            "path": self._plain(row["path"]),
                            "constraint": "name-required",
                            "component": self._component(row["constraint"]),
                            "value": row["value"],
                        }
                    )
                return out

            last = v01_jobs[-1]
            # Like Q-01, the evidence binds to the actual persisted runs and
            # their own immutable snapshots; later domain edits mark those
            # results stale and the ledger's attempt staleness already projects
            # that, so the payload itself never claims a fresh current re-run.
            self._b3_payload_evidence(
                evidences,
                "V-01",
                last,
                {
                    "beforeRepair": violations(v01_jobs[0]),
                    "afterRepair": violations(v01_jobs[-1]),
                    "includeInferred": last["dto"]["input"].get("scope") == "asserted+derived",
                },
                assistance,
            )

        # LX-01: origins over the repaired assignedTo state (extension case).
        repair = (
            "urn:ontolearn:learning:equipment/002",
            "urn:ontolearn:learning:assignedTo",
            "<urn:ontolearn:learning:person/L02>",
        )
        lx = next(
            (
                c
                for c in reversed(reasoning)
                if c["dto"]["state"] == "succeeded" and repair in c["snap_triples"]
            ),
            None,
        )
        if lx is None:
            evidences["LX-01"] = unavailable("LX-01")
        else:
            # Payload keys are N3 triples; normalize to the plain subject/
            # predicate form the person-type expectations are written in.
            asserted = {plain_key(t) for t in lx["payload"]["assertedFacts"]}
            derived = {plain_key(t) for t in lx["payload"]["reasoning"].get("rdfs", [])}
            persons = (
                "urn:ontolearn:learning:person/L01",
                "urn:ontolearn:learning:person/L02",
            )
            person_type = {
                person: (
                    person,
                    "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                    "<urn:ontolearn:learning:Person>",
                )
                for person in persons
            }
            actual = {}
            for person, key in person_type.items():
                if key in asserted:
                    actual[person] = "asserted"
                elif key in derived:
                    actual[person] = "derived"
                else:
                    actual[person] = "missing"
            extra = sorted(
                person
                for person in persons
                if person.endswith("/L02") and person_type[person] in asserted
            )
            persisted_or_stale(
                "LX-01",
                lx,
                {
                    "selectedOrigins": dict(selected_origins or {}),
                    "actualOrigins": actual,
                    "extraAssertedPersons": extra,
                },
            )

        # transfer-repair: repaired transfer dataset state and validation runs.
        repair_fact = (
            "urn:ontolearn:learning:equipment/101",
            "urn:ontolearn:learning:name",
            '"循环泵"',
        )
        transfer_jobs = [
            c for c in validation if repair_fact in c["snap_triples"] and "payload" in c
        ]
        if not transfer_jobs:
            evidences["transfer-repair"] = unavailable("transfer-repair")
        else:

            def transfer_violations(item):
                report = item["payload"].get("report", {})
                return [
                    {
                        "focusNode": self._plain(row["focus"]),
                        "path": self._plain(row["path"]),
                        "constraint": "name-required",
                        "component": self._component(row["constraint"]),
                        "value": row["value"],
                    }
                    for row in report.get("violations", [])
                ]

            # Only asserted facts (N3 objects); ontology definitions are not
            # part of the frozen transfer-repair fact set.
            from ontolearn_engine.rdf_snapshot import term

            current = sorted(
                (fact["subject"], fact["predicate"], term(fact["object"]).n3())
                for fact in store.state(internal)["facts"]
                if fact["object"] is not None
            )
            last_transfer = transfer_jobs[-1]
            transfer_result_id = last_transfer["dto"]["resultRef"]["resultId"]
            if last_transfer["dto"]["inputSnapshotId"] != snapshot_ref or (
                store.result_get(project, transfer_result_id).get("state") != "current"
            ):
                evidences["transfer-repair"] = ToolEvidence(
                    transfer_result_id,
                    context,
                    "transfer-repair",
                    "stale",
                    None,
                    assistance,
                    "persisted-domain-tool",
                )
            else:
                evidences["transfer-repair"] = ToolEvidence(
                    transfer_result_id,
                    context,
                    "transfer-repair",
                    "succeeded",
                    {
                        "beforeRepair": transfer_violations(transfer_jobs[0]),
                        "afterRepair": transfer_violations(transfer_jobs[-1]),
                        "facts": [dict3(t) for t in sorted(current)],
                        "scope": "current-asserted",
                    },
                    assistance,
                    "persisted-domain-tool",
                )

        # transfer-classify: asserted vs derived question facts with the trace.
        classify_fact = (
            "urn:ontolearn:learning:equipment/201",
            "urn:ontolearn:learning:name",
            '"检测泵"',
        )
        cls = next(
            (
                c
                for c in reversed(reasoning)
                if c["dto"]["state"] == "succeeded" and classify_fact in c["snap_triples"]
            ),
            None,
        )
        if cls is None:
            evidences["transfer-classify"] = unavailable("transfer-classify")
        else:
            asserted_fact = dict3(classify_fact)
            derived_triple = (
                "urn:ontolearn:learning:equipment/201",
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                "<urn:ontolearn:learning:HighRiskEquipment>",
            )
            derivation = {"rule": None, "inputs": []}
            for entry in cls["payload"]["reasoning"].get("evidence", []):
                if plain_key(entry["result"]) == derived_triple:
                    derivation = {
                        "rule": entry["rule"],
                        "inputs": [dict3(t) for t in entry["inputs"]],
                    }
                    break
            persisted_or_stale(
                "transfer-classify",
                cls,
                {
                    "assertedFact": asserted_fact,
                    "derivedFact": dict3(derived_triple),
                    "selectedOrigins": list(selected_origins or []),
                    "derivation": derivation,
                },
            )
        return evidences

    @staticmethod
    def _blocked_chain_outputs(store, internal, snapshot_id, inferred):
        """Heads a chained rule would produce from other rules' outputs.

        The engine's one-stage semantics never re-feeds rule outputs, so these
        derivations stay blocked. Legacy {"when","then"} and formal FR-505
        rules are both projected to N3 key rows, the same representation the
        persisted payload uses, before pattern matching.
        """
        rdf_type = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
        try:
            snap = store._project_snapshot(snapshot_id, internal)
        except Exception:
            return []
        consumers = []
        for definition in snap["state"]["definitions"]:
            if definition["layer"] != "rule":
                continue
            try:
                value = json.loads(definition["payload"])
            except ValueError:
                continue
            if not isinstance(value, dict) or not value.get("enabled"):
                continue

            def n3(pattern):
                if pattern["kind"] == "type":
                    return (
                        pattern["subject"],
                        rdf_type,
                        f"<{pattern['class']}>",
                    )
                return (pattern["subject"], f"<{pattern['path']}>", pattern["object"])

            if value.get("kind") == "rule":
                when = [
                    n3(item)
                    for item in value.get("conditions", [])
                    if isinstance(item, dict) and item.get("kind") in ("type", "property")
                ]
                heads = [
                    n3(item)
                    for item in value.get("conclusions", [])
                    if isinstance(item, dict) and item.get("kind") in ("type", "property")
                ]
            else:
                when = [tuple(row) for row in value.get("when", []) if len(row) == 3]
                heads = [tuple(value["then"])] if len(value.get("then", ())) == 3 else []
            if when and heads:
                consumers.append((when, heads))
        outputs = []
        for when, heads in consumers:
            binding = {}
            for pattern in when:
                hit = next(
                    (
                        row
                        for row in inferred
                        if LearningHost._chain_bind(pattern, row, dict(binding))
                    ),
                    None,
                )
                if hit is None:
                    binding = None
                    break
                LearningHost._chain_bind(pattern, hit, binding)
            if binding is None:
                continue
            for head in heads:
                outputs.append(
                    tuple(
                        binding.get(term, term)
                        if isinstance(term, str) and term.startswith("?")
                        else term
                        for term in head
                    )
                )
        return outputs

    @staticmethod
    def _chain_bind(pattern, row, binding):
        """Try one pattern against one N3 row, extending the binding copy."""
        for expected, actual in zip(pattern, row, strict=True):
            if isinstance(expected, str) and expected.startswith("?"):
                bound = binding.get(expected)
                if bound is None:
                    binding[expected] = actual
                elif bound != actual:
                    return False
            elif expected != actual:
                return False
        return True

    @staticmethod
    def _plain(term):
        return (
            term[1:-1] if isinstance(term, str) and term[:1] == "<" and term[-1:] == ">" else term
        )

    @staticmethod
    def _component(constraint):
        return {
            "<http://www.w3.org/ns/shacl#MinCountConstraintComponent>": "minCount",
            "<http://www.w3.org/ns/shacl#MaxCountConstraintComponent>": "maxCount",
            "<http://www.w3.org/ns/shacl#DatatypeConstraintComponent>": "datatype",
            "<http://www.w3.org/ns/shacl#InConstraintComponent>": "allowedValues",
            "<http://www.w3.org/ns/shacl#MinInclusiveConstraintComponent>": "minInclusive",
            "<http://www.w3.org/ns/shacl#MaxInclusiveConstraintComponent>": "maxInclusive",
        }.get(constraint, LearningHost._plain(constraint))

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
