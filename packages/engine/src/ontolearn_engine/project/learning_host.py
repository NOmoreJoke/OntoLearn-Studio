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
        self._transfer_inputs = None
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
                "snap": snap,
                "snap_triples": learning_ledger._state_triples(snap["state"]),
            }
            if dto["state"] == "succeeded" and dto.get("resultRef"):
                rows = store.result(dto["resultRef"]["resultId"])["payload"]
                item["payload"] = payload_from_rows(rows)
            candidates.append(item)
        return candidates

    def _transfer_fixture_facts(self):
        """Exact repair/classification fact sets from transfer-inputs.json."""
        if self._transfer_inputs is None:
            from ontolearn_engine.learning.baselines import read_json

            data = read_json(self.root() / "content/learning/transfer-inputs.json")
            self._transfer_inputs = {
                kind: {
                    (item["subject"], item["predicate"], item["object"])
                    for item in data[kind]["facts"]
                }
                for kind in ("repair", "classification")
            }
        return self._transfer_inputs

    @staticmethod
    def _is_constraint_target(snap, def_id, predicate_iri):
        """The definition is an enabled required shape on Equipment/predicate.

        FR-504 templates check the structured fields directly; legacy Turtle
        payloads are parsed into the real SHACL graph — no text-substring
        shortcuts. A comment mentioning the Equipment IRI, a different
        targetClass, an extra targetNode/targetSubjectsOf/targetObjectsOf, a
        deactivated shape, a blank-node path or a conflicting minCount all
        reject the definition outright.
        """
        for record in snap["state"]["definitions"]:
            if record["layer"] != "constraint" or record["id"] != def_id:
                continue
            try:
                payload = json.loads(record["payload"])
            except ValueError:
                return False
            if not isinstance(payload, dict) or payload.get("enabled") is not True:
                return False
            if payload.get("kind") == "constraint":
                return (
                    payload.get("targetClass") == "urn:ontolearn:learning:Equipment"
                    and payload.get("path") == predicate_iri
                    and payload.get("template") == "required"
                )
            turtle = payload.get("turtle")
            if not isinstance(turtle, str):
                return False
            from rdflib import Literal, URIRef
            from rdflib.namespace import SH

            from ontolearn_engine import semantic
            from ontolearn_engine.semantic_offline import SemanticError

            try:
                graph = semantic.parse_turtle(turtle, shapes=True)
            except SemanticError:
                return False
            equipment = URIRef("urn:ontolearn:learning:Equipment")
            if (
                any(graph.objects(None, SH.targetNode))
                or any(graph.objects(None, SH.targetSubjectsOf))
                or any(graph.objects(None, SH.targetObjectsOf))
                or any(True for _ in graph.triples((None, SH.deactivated, Literal(True))))
            ):
                return False
            if set(graph.objects(None, SH.targetClass)) != {equipment}:
                return False
            shapes = list(graph.subjects(SH.targetClass, equipment))
            if not shapes:
                return False
            min_counts = []
            for shape in shapes:
                props = list(graph.objects(shape, SH.property))
                if not props:
                    return False
                for prop in props:
                    if set(graph.objects(prop, SH.path)) != {URIRef(predicate_iri)}:
                        return False
                    min_counts.extend(literal for literal in graph.objects(prop, SH.minCount))
            if not any(
                isinstance(literal, Literal) and type(literal.value) is int and literal.value == 1
                for literal in min_counts
            ):
                return False
            return not any(
                isinstance(literal, Literal) and type(literal.value) is int and literal.value != 1
                for literal in min_counts
            )
        return False

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

        def violations(item):
            report = item["payload"].get("report", {})
            out = []
            for row in report.get("violations", []):
                out.append(
                    {
                        "focusNode": self._plain(row["focus"]),
                        "path": self._plain(row["path"]),
                        "constraint": item["dto"]["input"]["definitionId"],
                        "component": self._component(row["constraint"]),
                        "value": row["value"],
                    }
                )
            return out

        # V-01: name-required validation before and after the 003-name repair.
        # Both runs must be real name-required shapes on the Equipment name
        # path (not merely jobs labelled that id), must be current-selection
        # runs (never historical replays) and must come from two different
        # snapshots: one before the repair, one after it. When an asserted
        # before/after repair pair is established and later runs on the project
        # still keep 003 valid, subsequent asserted+derived checks (for R-05 /
        # LX-01) do not retroactively fail V-01.
        v01_jobs = [
            c
            for c in validation
            if c["dto"]["input"].get("definitionId") == "name-required"
            and self._is_constraint_target(
                c["snap"], "name-required", "urn:ontolearn:learning:name"
            )
            and "payload" in c
            and c["payload"].get("inputSelection", "current") == "current"
        ]
        v01_asserted = [c for c in v01_jobs if c["dto"]["input"].get("scope") == "asserted"]
        if len(v01_jobs) < 2:
            evidences["V-01"] = unavailable("V-01")
        else:
            chosen_before = None
            chosen_after = None
            if len(v01_asserted) >= 2:
                cand_after = v01_asserted[-1]
                earlier_diff = [
                    c
                    for c in v01_asserted[:-1]
                    if c["dto"]["inputSnapshotId"] != cand_after["dto"]["inputSnapshotId"]
                ]
                if earlier_diff and (v01_jobs[-1] is cand_after or not violations(v01_jobs[-1])):
                    chosen_before = next(
                        (c for c in reversed(earlier_diff) if violations(c)),
                        earlier_diff[0],
                    )
                    chosen_after = cand_after
            if chosen_before is None or chosen_after is None:
                if v01_jobs[0]["dto"]["inputSnapshotId"] == v01_jobs[-1]["dto"]["inputSnapshotId"]:
                    evidences["V-01"] = unavailable("V-01")
                else:
                    chosen_before, chosen_after = v01_jobs[0], v01_jobs[-1]
            if chosen_before is not None and chosen_after is not None:
                # Like Q-01, the evidence binds to the actual persisted runs and
                # their own immutable snapshots; later domain edits mark those
                # results stale and the ledger's attempt staleness already projects
                # that, so the payload itself never claims a fresh current re-run.
                self._b3_payload_evidence(
                    evidences,
                    "V-01",
                    chosen_after,
                    {
                        "beforeRepair": violations(chosen_before),
                        "afterRepair": violations(chosen_after),
                        "includeInferred": (
                            chosen_before["dto"]["input"].get("scope") != "asserted"
                            or chosen_after["dto"]["input"].get("scope") != "asserted"
                        ),
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
            lx_checks = self._lx01_step_checks(store, project, reasoning, validation, lx, plain_key)
            persisted_or_stale(
                "LX-01",
                lx,
                {
                    "selectedOrigins": dict(selected_origins or {}),
                    "actualOrigins": actual,
                    "extraAssertedPersons": extra,
                    **lx_checks,
                },
            )

        # transfer-repair: repaired transfer dataset state and validation runs.
        repair_fact = (
            "urn:ontolearn:learning:equipment/101",
            "urn:ontolearn:learning:name",
            '"循环泵"',
        )
        transfer_jobs = [
            c
            for c in validation
            if repair_fact in c["snap_triples"]
            and c["dto"]["input"].get("definitionId") == "name-required"
            and self._is_constraint_target(
                c["snap"], "name-required", "urn:ontolearn:learning:name"
            )
            and "payload" in c
        ]
        if len(transfer_jobs) < 2 or (
            transfer_jobs[0]["dto"]["inputSnapshotId"]
            == transfer_jobs[-1]["dto"]["inputSnapshotId"]
        ):
            # The fixed expectation needs a pre-repair and a post-repair run
            # across a real snapshot change.
            evidences["transfer-repair"] = unavailable("transfer-repair")
        else:

            def transfer_violations(item):
                report = item["payload"].get("report", {})
                return [
                    {
                        "focusNode": self._plain(row["focus"]),
                        "path": self._plain(row["path"]),
                        "constraint": item["dto"]["input"]["definitionId"],
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
                both_current = all(
                    item["payload"].get("inputSelection", "current") == "current"
                    for item in (transfer_jobs[0], transfer_jobs[-1])
                )
                if (
                    transfer_jobs[0]["dto"]["input"].get("scope") == "asserted"
                    and transfer_jobs[-1]["dto"]["input"].get("scope") == "asserted"
                    and both_current
                ):
                    transfer_scope = "current-asserted"
                elif any(
                    item["dto"]["input"].get("scope") != "asserted"
                    for item in (transfer_jobs[0], transfer_jobs[-1])
                ):
                    transfer_scope = "asserted+derived"
                else:
                    transfer_scope = "historical-asserted"
                evidences["transfer-repair"] = ToolEvidence(
                    transfer_result_id,
                    context,
                    "transfer-repair",
                    "succeeded",
                    {
                        "beforeRepair": transfer_violations(transfer_jobs[0]),
                        "afterRepair": transfer_violations(transfer_jobs[-1]),
                        "facts": [dict3(t) for t in sorted(current)],
                        "scope": transfer_scope,
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
                if c["dto"]["state"] == "succeeded"
                and c["dto"]["input"].get("scope") == "asserted"
                and c["payload"].get("inputSelection", "current") == "current"
                and classify_fact in c["snap_triples"]
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
            # The asserted set must be exactly the six fixture facts: a
            # hand-asserted derived triple (or any extra assertion) voids the
            # derived answer so LearningService.check must reject the pass.
            classification_facts = self._transfer_fixture_facts()["classification"]
            asserted_set = {plain_key(t) for t in cls["payload"]["assertedFacts"]}
            derived_preserved = (
                asserted_set == classification_facts and derived_triple not in asserted_set
            )
            persisted_or_stale(
                "transfer-classify",
                cls,
                {
                    "assertedFact": asserted_fact,
                    "derivedFact": dict3(derived_triple) if derived_preserved else None,
                    "selectedOrigins": list(selected_origins or []),
                    "derivation": derivation,
                },
            )
        return evidences

    def _lx01_step_checks(self, store, project, reasoning, validation, lx, plain_key):
        """The four real-run verifications behind LX-01 steps 1-4.

        1. repairAssertionsMatch: the repaired snapshot carries exactly the
           three expected assignedTo assertions — and, against the verified
           pre-repair baseline (step 1's run or the matched Step-2 SHACL
           before-run), exactly the two repair facts and nothing else.
        2. step1DerivedMatch: an earlier pre-repair current reasoning run (the
           L01 assignment present, no 002/003 assignment, domain/range axioms
           present) derived exactly equipment/001's HighRiskEquipment via
           R-risk with the alarm/A01 input and nothing else on the RDFS side.
        3. shaclStepsVerified: one enabled assignedTo required constraint on
           Equipment (verified against each run's own snapshot, so an
           OtherEquipment look-alike never stands in) measured exactly the two
           pre-repair violations and, on the repaired snapshot, conforms with
           zero violations.
        4. step4DerivedMatch: the repaired run's closure is exactly the R-risk
           conclusion plus person/L02's Person type, with the alarm/A01 input
           evidence and the range-axiom + repaired-assertion basis.
        """
        equipment_prefix = "urn:ontolearn:learning:equipment/"
        assigned_to = "urn:ontolearn:learning:assignedTo"
        rdf_type = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
        repair_002 = (
            equipment_prefix + "002",
            assigned_to,
            "<urn:ontolearn:learning:person/L02>",
        )
        repair_003 = (
            equipment_prefix + "003",
            assigned_to,
            "<urn:ontolearn:learning:person/L01>",
        )
        assigned_to_001 = (
            equipment_prefix + "001",
            assigned_to,
            "<urn:ontolearn:learning:person/L01>",
        )
        person_l01_type = (
            "urn:ontolearn:learning:person/L01",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
            "<urn:ontolearn:learning:Person>",
        )
        repair_assertions_match = {
            (equipment_prefix + "001", assigned_to, "<urn:ontolearn:learning:person/L01>"),
            repair_002,
            repair_003,
        } == {
            (subject, predicate, object_)
            for subject, predicate, object_ in lx["snap_triples"]
            if subject.startswith(equipment_prefix) and predicate == assigned_to
        }

        def ontology_records(item):
            records = []
            for record in item["snap"]["state"]["definitions"]:
                if record["layer"] != "ontology":
                    continue
                try:
                    payload = json.loads(record["payload"])
                except ValueError:
                    continue
                if isinstance(payload, dict):
                    records.extend(payload.get("triples") or [])
            return records

        high_risk = (
            f"<{equipment_prefix}001>",
            rdf_type,
            "<urn:ontolearn:learning:HighRiskEquipment>",
        )
        high_risk_plain = plain_key(high_risk)
        alarm_input = [
            f"<{equipment_prefix}001>",
            "<urn:ontolearn:learning:alarm>",
            "<urn:ontolearn:learning:alarm/A01>",
        ]
        person_l02 = (
            "<urn:ontolearn:learning:person/L02>",
            rdf_type,
            "<urn:ontolearn:learning:Person>",
        )
        repair_002_n3 = (
            f"<{equipment_prefix}002>",
            f"<{assigned_to}>",
            "<urn:ontolearn:learning:person/L02>",
        )
        range_basis = (
            f"<{assigned_to}>",
            "<http://www.w3.org/2000/01/rdf-schema#range>",
            "<urn:ontolearn:learning:Person>",
        )
        domain_axiom = {
            "subject": assigned_to,
            "predicate": "http://www.w3.org/2000/01/rdf-schema#domain",
            "object": "<urn:ontolearn:learning:Equipment>",
        }
        range_axiom = {
            "subject": assigned_to,
            "predicate": "http://www.w3.org/2000/01/rdf-schema#range",
            "object": "<urn:ontolearn:learning:Person>",
        }
        step1_item = next(
            (
                item
                for item in reasoning
                if item["claim_rowid"] < lx["claim_rowid"]
                and item["dto"]["state"] == "succeeded"
                and "payload" in item
                and item["payload"].get("inputSelection", "current") == "current"
                and assigned_to_001 in item["snap_triples"]
                and person_l01_type in item["snap_triples"]
                and not any(
                    triple[0] in (equipment_prefix + "002", equipment_prefix + "003")
                    and triple[1] == assigned_to
                    for triple in item["snap_triples"]
                )
                and domain_axiom in ontology_records(item)
                and range_axiom in ontology_records(item)
                and {plain_key(t) for t in item["payload"]["reasoning"].get("rules", [])}
                == {high_risk_plain}
                and {tuple(t) for t in item["payload"]["reasoning"].get("rdfs", [])} == set()
                and any(
                    entry.get("rule") == "R-risk"
                    and tuple(entry.get("result") or ()) == high_risk
                    and alarm_input in entry.get("inputs", [])
                    for entry in item["payload"]["reasoning"].get("evidence", [])
                )
            ),
            None,
        )
        step1_derived_match = step1_item is not None

        def violation_signature(item):
            report = item["payload"].get("report", {})
            return sorted(
                (
                    row["focus"],
                    row["path"],
                    self._component(row["constraint"]),
                    row["value"],
                )
                for row in report.get("violations", [])
            )

        expected_violations = sorted(
            (
                (f"<{equipment_prefix}002>", f"<{assigned_to}>", "minCount", None),
                (f"<{equipment_prefix}003>", f"<{assigned_to}>", "minCount", None),
            )
        )
        shacl_steps_verified = False
        matched_before = None
        for cid in sorted(
            {
                record["id"]
                for record in lx["snap"]["state"]["definitions"]
                if record["layer"] == "constraint"
            }
        ):
            if not self._is_constraint_target(lx["snap"], cid, assigned_to):
                continue
            before = next(
                (
                    item
                    for item in validation
                    if item["claim_rowid"] < lx["claim_rowid"]
                    and item["dto"]["state"] == "succeeded"
                    and "payload" in item
                    and item["dto"]["input"].get("definitionId") == cid
                    and item["dto"]["input"].get("scope") == "asserted"
                    and item["payload"].get("inputSelection", "current") == "current"
                    and self._is_constraint_target(item["snap"], cid, assigned_to)
                    and violation_signature(item) == expected_violations
                ),
                None,
            )
            if before is not None and step1_item is not None:
                # The pre-repair SHACL run must measure the very same snapshot
                # the Step-1 reasoning ran on — no older stand-in state.
                if before["snap_triples"] != step1_item["snap_triples"]:
                    before = None
            after = next(
                (
                    item
                    for item in validation
                    if item["dto"]["state"] == "succeeded"
                    and "payload" in item
                    and item["dto"]["input"].get("definitionId") == cid
                    and item["dto"]["input"].get("scope") == "asserted"
                    and item["payload"].get("inputSelection", "current") == "current"
                    and item["dto"]["inputSnapshotId"] == lx["dto"]["inputSnapshotId"]
                    and self._is_constraint_target(item["snap"], cid, assigned_to)
                    and item["payload"].get("report", {}).get("violations") == []
                    and item["payload"].get("report", {}).get("conforms") is True
                ),
                None,
            )
            if before is not None and after is not None:
                shacl_steps_verified = True
                matched_before = before
                break
        reference_pre = step1_item if step1_item is not None else matched_before
        if reference_pre is not None:
            # Zero extra facts / deletions tolerated beyond the two repairs.
            repair_assertions_match = repair_assertions_match and (
                lx["snap_triples"] == (reference_pre["snap_triples"] | {repair_002, repair_003})
            )
        body = lx["payload"]["reasoning"]
        step4_derived_match = (
            lx["payload"].get("inputSelection", "current") == "current"
            and domain_axiom in ontology_records(lx)
            and range_axiom in ontology_records(lx)
            and {tuple(t) for t in body.get("rules", [])} == {high_risk}
            and {tuple(t) for t in body.get("rdfs", [])} == {person_l02}
            and any(
                entry.get("rule") == "R-risk"
                and tuple(entry.get("result") or ()) == high_risk
                and alarm_input in entry.get("inputs", [])
                for entry in body.get("evidence", [])
            )
            and any(
                tuple(entry.get("result") or ()) == person_l02
                and {range_basis, tuple(repair_002_n3)}
                <= {tuple(triple) for triple in entry.get("basis", [])}
                for entry in body.get("rdfsEvidence", [])
            )
        )
        return {
            "repairAssertionsMatch": repair_assertions_match,
            "step1DerivedMatch": step1_derived_match,
            "shaclStepsVerified": shacl_steps_verified,
            "step4DerivedMatch": step4_derived_match,
        }

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
