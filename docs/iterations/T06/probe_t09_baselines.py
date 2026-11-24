"""Explicit cross-worktree fixed-data probe, never full product acceptance.

Consumes verified JSON only. Manual derived facts remain labelled test inputs.
No T09 Python executor, real reasoner, Store, resource stage, Agent or GUI.
"""

import argparse
import copy
import json
from pathlib import Path

from ontolearn_engine.behavior import BehaviorError, plan_behaviors, prepare_events
from ontolearn_engine.behavior.baseline_adapter import (
    RDF_TYPE,
    adapt_case,
    decode_fact,
    load_bundle,
    project_candidate,
)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def check_equal(actual, expected, field, case):
    if actual != expected:
        raise AssertionError(f"{case}: complete {field} mismatch")


def run_probe(root, manifest_sha):
    bundle = load_bundle(root, manifest_sha)
    data = bundle.document
    results = []
    for case_id in ("B-01", "B-02", "B-03", "B-04", "B-05", "B-06", "B-09", "B-10", "B-11"):
        case = next(item for item in data["cases.json"]["cases"] if item["id"] == case_id)
        adapted = adapt_case(
            bundle,
            case_id,
            {"project_id": "T06-readonly-data-probe", "scenario_id": case_id, "mode": "sample"},
            "probe-1",
        )
        req = adapted["request"]
        original = copy.deepcopy(req)
        prepared = prepare_events(req)
        namespace = adapted["namespace"]
        model = data[case["baseline"] + ".json"]
        # Gold data supplied to the planner, explicitly not a reasoner result.
        manual_facts = case["expected"].get(
            "behaviorBeforeInference",
            [
                {
                    "subject": namespace + "equipment/001",
                    "predicate": RDF_TYPE,
                    "object": "<" + namespace + "HighRiskEquipment>",
                }
            ],
        )
        derived = prepared.reasoning_input
        derived.pop("state")
        derived.update(
            version="manual-derived-test-input",
            status="current",
            facts=[decode_fact(f, req["schema"]) for f in manual_facts],
        )
        failure = None
        try:
            plan = plan_behaviors(prepared, derived)
            if not case["expected"]["committed"]:
                raise AssertionError(f"{case_id}: expected competing-write rejection")
        except BehaviorError as error:
            if error.reason != "competing_write" or case["expected"]["committed"]:
                raise
            failure = {"reason": error.reason, "evidence": error.evidence}
            plan = {
                "candidate": req["state"],
                "action_trace": [],
                "consumption": req["consumption"],
            }
            pairs = error.evidence["conflict"]
            expected = case["expected"]["conflict"]
            check_equal(
                [[p["event_id"], p["behavior_id"]] for p in pairs],
                expected["instances"],
                "conflict instances",
                case_id,
            )
            check_equal(
                [p["action"]["value"] for p in pairs],
                expected["values"],
                "conflict values",
                case_id,
            )
            check_equal(
                error.evidence["conflict_slot"],
                {
                    "subject": namespace + expected["target"],
                    "property": namespace + expected["property"],
                },
                "conflict slot",
                case_id,
            )
        projected = project_candidate(plan, model, namespace)
        for field in (
            "orders",
            "notifications",
            "actionTrace",
            "consumedEvents",
            "triggeredInstances",
        ):
            check_equal(projected[field], case["expected"][field], field, case_id)
        check_equal(
            projected["facts"],
            sorted(case["expected"]["facts"], key=canonical),
            "asserted fact set",
            case_id,
        )
        check_equal(req, original, "immutable request", case_id)
        check_equal(projected["committed"], False, "uncommitted status", case_id)
        if case_id == "B-02":
            decisions = [d for d in plan["decisions"] if d["behavior_id"] == "B-risk"]
            check_equal(
                [(d["reason"], d["conditions"][0]["satisfied"]) for d in decisions],
                [("condition_not_satisfied", False)],
                "actual non-trigger reason",
                case_id,
            )
        if case_id == "B-06":
            frozen = [
                f["value"]
                for f in plan["frozen"]["facts"]
                if f["subject"] == namespace + "T1" and f["property"] == namespace + "P"
            ]
            check_equal(frozen, [False], "frozen P", case_id)
        if case_id == "B-04":
            previous = copy.deepcopy(req)
            previous["events"] = []
            old_prepared = prepare_events(previous)
            old = old_prepared.reasoning_input
            old.pop("state")
            old.update(
                version="manual-old-test-input",
                status="current",
                facts=[
                    {
                        "subject": namespace + "equipment/001",
                        "property": RDF_TYPE,
                        "value": namespace + "HighRiskEquipment",
                    }
                ],
            )
            try:
                plan_behaviors(prepared, old)
            except BehaviorError as error:
                check_equal(error.reason, "stale_reasoning", "stale binding rejection", case_id)
            else:
                raise AssertionError("B-04: stale binding accepted")
        repeat = None
        if adapted["repeat_events"]:
            repeated = copy.deepcopy(req)
            repeated.update(
                state=plan["candidate"],
                consumption=plan["consumption"],
                events=adapted["repeat_events"],
            )
            repeated_prepared = prepare_events(repeated)
            repeated_derived = repeated_prepared.reasoning_input
            repeated_derived.pop("state")
            repeated_derived.update(
                version="manual-repeat-test-input", status="current", facts=derived["facts"]
            )
            repeated_plan = plan_behaviors(repeated_prepared, repeated_derived)
            repeat = project_candidate(
                repeated_plan,
                model,
                namespace,
                prior_order_ids=[o["id"] for o in projected["orders"]],
            )
            for field in (
                "facts",
                "orders",
                "notifications",
                "consumedEvents",
                "triggeredInstances",
            ):
                check_equal(repeat[field], projected[field], "repeat " + field, case_id)
            check_equal(repeat["actionTrace"], [], "repeat actions", case_id)
            check_equal(repeated_plan["diff"], {"added": [], "removed": []}, "repeat diff", case_id)
        results.append(
            {
                "case_id": case_id,
                "source": adapted["source"],
                "status": "private-plan-comparison-passed",
                "projected_candidate": projected,
                "manual_reasoning_input": derived,
                "failure": failure,
                "repeat": repeat,
            }
        )
    return {
        "manifest_sha256": bundle.manifest_sha256,
        "case_count": len(results),
        "product_runtime": "not-executed",
        "formal_acceptance": False,
        "reasoning_source": "manual gold test input; no reasoner executed",
        "not_tested": ["atomic Store round", "resource stage B-07", "Agent B-08", "UI"],
        "cases": results,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--manifest-sha", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = run_probe(args.source_root, args.manifest_sha)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
