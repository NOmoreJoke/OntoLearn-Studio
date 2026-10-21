"""Real fixed components; fixture-only syntax binder, no saved Job authority.

Inputs are loaded independently of golden assertions. False call observations
are test-only diagnostics, never persistent ComparisonEvidence or a producer DTO.
"""

import hashlib
import json
import os
from contextlib import ExitStack
from dataclasses import fields, is_dataclass, replace
from pathlib import Path
from unittest.mock import patch

import pytest
from ontolearn_engine import semantic
from ontolearn_engine.quality import rule_firing
from ontolearn_engine.quality.rule_firing import Comparison, RuleSpec, Triple, Variable
from ontolearn_engine.quality.rule_numbers import Number
from ontolearn_engine.quality.rule_profile import PROFILE, Budget, SourceRecord, TermInput
from ontolearn_engine.quality.rule_terms import ProfileValue
from ontolearn_engine.resources import CONTRACT, ROOT
from ontolearn_engine.semantic_profile_input import CaptureLedger, prepare_profile_material
from ontolearn_engine.semantic_profile_production import execute_admitted_profile_job
from ontolearn_engine.semantic_profile_restore import (
    ReadonlyObject,
    ReadonlySequence,
    RestoreExpectation,
    restore_profile_result,
)
from ontolearn_engine.semantic_profile_restore_budget import RestoreLedger
from ontolearn_engine.semantic_turtle import decode_profile_term
from rdflib import RDF, SH

REPO = Path(__file__).resolve().parents[3]
PURE = REPO / "tests/fixtures/quality/profile-M1-graph-consumer-inputs.json"
READONLY = REPO / "docs/reviews/T05/profile-M1-math-explanation-input-contract"
GRAPH_INPUT = json.loads(PURE.read_bytes())
CONSUMER_INPUT = json.loads((READONLY / "consumer-C-inputs.json").read_bytes())
SCHEMA = json.loads((ROOT / "v2/schema.json").read_bytes())
GRAPH_IDS = ("M1-complete-heads", "M1-false-then-error")
POLICY_PENDING = ("C-inclusive-date-entry", "C-illtyped-entry")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def plain(value):
    """Lossless native observation only, never a production serializer/input."""
    if isinstance(value, ReadonlyObject):
        return {k: plain(v) for k, v in value.entries}
    if isinstance(value, ReadonlySequence):
        return {"collection": value.native_kind, "items": [plain(v) for v in value.items]}
    if value is None or type(value) in (str, bool):
        return value
    if type(value) is int:
        return {"integerDecimal": str(value)}
    if type(value) is bytes:
        return {"bytesHex": value.hex()}
    if type(value) in (tuple, list):
        return {"collection": type(value).__name__, "items": [plain(v) for v in value]}
    if type(value) is dict:
        return {k: plain(v) for k, v in value.items()}
    if is_dataclass(value):
        return {
            "recordType": type(value).__name__,
            **{f.name: plain(getattr(value, f.name)) for f in fields(value)},
        }
    raise TypeError(type(value).__name__)


def error_record(error):
    return {
        "exceptionType": type(error).__name__,
        "reason": getattr(error, "reason", getattr(error, "code", None)),
        "diagnostic": getattr(error, "diagnostic", None),
        "publicError": getattr(error, "error", None),
    }


def source(pointer):
    digest = sha(PURE.read_bytes())
    return SourceRecord(
        str(PURE.relative_to(REPO)) + "#" + pointer,
        digest,
        "sha256:" + digest,
        None,
    )


def term(token, pointer):
    if token.startswith("?"):
        return Variable(token)
    return replace(decode_profile_term(token), source=source(pointer))


def iri(token, pointer):
    return TermInput("iri", token, source=source(pointer))


def bind_fixture(case, index):
    """This bounded binder accepts the actual fixture syntax, not product JSON."""
    prefix = f"/cases/{index}"
    records, specs, trace = [], [], []
    for section in ("asserted", "ontology"):
        for i, row in enumerate(case[section]):
            records.append(
                tuple(term(token, f"{prefix}/{section}/{i}/{j}") for j, token in enumerate(row))
            )
    for ordinal, raw in enumerate(case["rules"]):
        assert raw["schemaVersion"] == 1 and raw["kind"] == "rule" and raw["enabled"] is True
        pointer = f"{prefix}/rules/{ordinal}"
        when, comparisons, heads = [], [], []
        mapping = {"rulePointer": pointer, "when": [], "comparisons": [], "heads": []}
        for position, condition in enumerate(raw["conditions"]):
            base = f"{pointer}/conditions/{position}"
            kind = condition["kind"]
            if kind == "property":
                when.append(
                    Triple(
                        term(condition["subject"], base + "/subject"),
                        iri(condition["path"], base + "/path"),
                        term(condition["object"], base + "/object"),
                    )
                )
                mapping["when"].append(position)
            elif kind == "type":
                when.append(
                    Triple(
                        term(condition["subject"], base + "/subject"),
                        iri(str(RDF.type), base),
                        iri(condition["class"], base + "/class"),
                    )
                )
                mapping["when"].append(position)
            elif kind == "compare":
                comparisons.append(
                    Comparison(
                        term(condition["left"], base + "/left"),
                        condition["operator"],
                        term(condition["right"], base + "/right"),
                    )
                )
                mapping["comparisons"].append(position)
            else:
                raise ValueError("Unsupported fixture condition")
        for position, conclusion in enumerate(raw["conclusions"]):
            base = f"{pointer}/conclusions/{position}"
            if conclusion["kind"] == "type":
                head = Triple(
                    term(conclusion["subject"], base + "/subject"),
                    iri(str(RDF.type), base),
                    iri(conclusion["class"], base + "/class"),
                )
            else:
                assert conclusion["kind"] == "property"
                head = Triple(
                    term(conclusion["subject"], base + "/subject"),
                    iri(conclusion["path"], base + "/path"),
                    term(conclusion["object"], base + "/object"),
                )
            heads.append(head)
            mapping["heads"].append(position)
        specs.append(
            RuleSpec(
                raw["id"],
                tuple(when),
                tuple(comparisons),
                tuple(heads),
                source(pointer),
                str(raw["revision"]),
                sha(canonical(raw)),
                PROFILE,
            )
        )
        trace.append(mapping)
    return tuple(records), tuple(specs), trace


def triple_key(value):
    return [semantic._profile_term(t).n3() for t in (value.subject, value.predicate, value.object)]


def _fee_observer(cls, name, events, phase):
    original = getattr(cls, name)

    def observe(instance, *args, **kwargs):
        event = {
            "phase": phase[0],
            "ledger": cls.__name__,
            "method": name,
            "args": plain(args),
            "kwargs": plain(kwargs),
        }
        events.append(event)
        try:
            result = original(instance, *args, **kwargs)
            event["returned"] = True
            return result
        except Exception as error:
            event["error"] = error_record(error)
            raise

    return observe


def observe_rule(case, index, directory):
    phase, events, calls = ["binder"], [], []
    actual = {
        "status": "error",
        "stage": "binder",
        "producedResultReturned": False,
        "restoredResultReturned": False,
        "comparatorCalls": calls,
    }
    material = produced = restored = None
    preparation, production, restoration = CaptureLedger(), CaptureLedger(), RestoreLedger()
    original_compare = rule_firing.compare_values

    def compare(*args, **kwargs):
        call = {"phase": phase[0], "operator": args[1], "location": plain(args[4])}
        calls.append(call)
        try:
            outcome = original_compare(*args, **kwargs)
            call["returnedBoolean"] = outcome
            return outcome
        except Exception as error:
            call["error"] = error_record(error)
            raise

    try:
        with ExitStack() as stack:
            for cls, methods in (
                (CaptureLedger, ("begin", "enter", "debit", "reserve", "release", "finish")),
                (RestoreLedger, ("begin", "charge", "reserve", "release", "finish")),
                (Budget, ("debit",)),
                (semantic._GraphBudget, ("debit",)),
            ):
                for method in methods:
                    stack.enter_context(
                        patch.object(cls, method, _fee_observer(cls, method, events, phase))
                    )
            stack.enter_context(patch.object(rule_firing, "compare_values", compare))
            records, rules, mapping = bind_fixture(case, index)
            actual["binderMapping"] = mapping
            actual["records"] = plain(records)
            actual["rules"] = plain(rules)
            phase[0] = actual["stage"] = "material"
            material = prepare_profile_material(records=records, rules=rules, ledger=preparation)
            phase[0] = actual["stage"] = "production"
            produced = execute_admitted_profile_job(
                material,
                error_catalog=CONTRACT.ERROR_CATALOG,
                error_schema=SCHEMA,
                ledger=production,
            )
            actual["producedResultReturned"] = True
            payload = produced.wire["payload"]
            expectation = RestoreExpectation(
                sha(produced.payload_json),
                sha(produced.rows_json),
                payload["inputDigest"],
                payload["inputDigestDomain"],
                payload["sourceDigest"],
                payload["definitionsDigest"],
                sha(produced.catalog_json),
                tuple(sorted(payload["implementation"].items())),
                material.input_preimage,
                material.source_preimage,
            )
            phase[0] = actual["stage"] = "restore"
            restored = restore_profile_result(
                produced.payload_json,
                produced.rows_json,
                expected=expectation,
                allocation=produced.original_allocation,
                ledger=restoration,
            )
            actual["restoredResultReturned"] = True
            actual.update(status="success", stage="restored")
            actual["nativeResult"] = plain(produced.native_result)
            actual["restoredResult"] = plain(restored)
            actual["originalAllocation"] = plain(produced.original_allocation)
            actual["preparationReceipt"] = plain(material.capture_receipt)
            actual["productionReceipt"] = plain(produced.capture_receipt)
            actual["retentionMeaning"] = (
                "Held returned references; logical live zero is not physical release or H lease"
            )
            actual["fullPayloadEqual"] = plain(restored.projection.payload) == plain(
                {**payload, "reasoning": produced.native_result}
            )
            actual["fullChildrenEqual"] = all(
                plain(child.batch) == plain(native["batch"])
                and plain(child.original_matches) == plain(native["originalMatches"])
                for child, native in zip(
                    restored.batches.children,
                    produced.native_result["mechanismBatches"],
                    strict=True,
                )
            )
    except Exception as error:
        actual.update(error_record(error))
    finally:
        if material is not None:
            for name in (
                "input_preimage",
                "source_preimage",
                "definitions_preimage",
                "definition_material",
            ):
                (directory / (name + ".bin")).write_bytes(getattr(material, name))
        if produced is not None:
            for name in (
                "payload_json",
                "rows_json",
                "catalog_json",
                "source_encoded",
                "definitions_encoded",
            ):
                (directory / (name + ".bin")).write_bytes(getattr(produced, name))
        actual["ledgerStates"] = {
            "preparation": preparation.state,
            "production": production.state,
            "restore": restoration.state,
        }
        if restoration.state != "new":
            actual["restoreUsage"] = plain(restoration.usage)
            actual["restorePeaks"] = plain(restoration.peaks)
            actual["restoreLive"] = plain(restoration.live)
        (directory / "fee-events.json").write_bytes(canonical(events))
    return actual, produced, restored


def observe_consumer(case, directory):
    actual = {
        "status": "error",
        "stage": "parse-data",
        "validatorRuns": 0,
        "costs": "Original query/SHACL API has no C/R receipt; none fabricated",
    }
    original_run = semantic.Validator.run

    def run(instance, *args, **kwargs):
        actual["validatorRuns"] += 1
        result = original_run(instance, *args, **kwargs)
        conforms, report, text = result
        (directory / "report.nt").write_bytes(report.serialize(format="nt", encoding="utf-8"))
        (directory / "report-text.txt").write_text(text)
        rows = []
        names = (
            "focusNode",
            "resultPath",
            "value",
            "sourceShape",
            "sourceConstraintComponent",
            "resultSeverity",
        )
        for node in report.subjects(RDF.type, SH.ValidationResult):
            row = {"actualResultNode": node.n3()}
            for name in names:
                values = list(report.objects(node, SH[name]))
                row[name] = [v.n3() for v in values]
            rows.append(row)
        actual["realValidatorReport"] = {"conforms": bool(conforms), "rows": rows}
        return result

    try:
        graph = semantic.parse_turtle(case["dataTurtle"])
        actual["dataTripleCount"] = len(graph)
        (directory / "data.nt").write_bytes(graph.serialize(format="nt", encoding="utf-8"))
        if "query" in case:
            actual["stage"] = "query"
            actual["result"] = semantic.query(graph, case["query"])
        else:
            actual["stage"] = "parse-shapes"
            shapes = semantic.parse_turtle(case["shapesTurtle"], shapes=True)
            actual["shapeTripleCount"] = len(shapes)
            (directory / "shapes.nt").write_bytes(shapes.serialize(format="nt", encoding="utf-8"))
            actual["stage"] = "check-shapes"
            with patch.object(semantic.Validator, "run", run):
                actual["result"] = semantic.check_shapes(graph, shapes)
        actual.update(status="success", stage="returned")
    except Exception as error:
        actual.update(error_record(error))
    return actual


@pytest.fixture(scope="session")
def goldens():
    return {
        "explanation": json.loads((READONLY / "explanation-goldens.json").read_bytes()),
        "consumers": {
            r["id"]: r["expected"]
            for r in json.loads((READONLY / "consumer-C-goldens.json").read_bytes())["cases"]
        },
    }


def artifact_directory(tmp_path, case_id):
    root = Path(os.environ.get("M1_GRAPH_OBSERVATION_DIR", str(tmp_path)))
    path = root / sha(case_id.encode())
    path.mkdir(parents=True, exist_ok=False)
    return path


def assert_source(actual, pointer):
    assert type(actual) is SourceRecord
    assert actual.reference == str(PURE.relative_to(REPO)) + "#" + pointer
    assert actual.digest == sha(PURE.read_bytes())
    assert actual.revision == "sha256:" + sha(PURE.read_bytes())
    assert actual.text is None


def assert_complete_heads(produced, restored, expected):
    assert produced is not None and restored is not None
    native = produced.native_result
    assert len(produced.wire["payload"]) == 7 and len(native) == 15
    (child,) = native["mechanismBatches"]
    assert len(child) == 11
    assert child["ruleId"] == expected["ruleId"]
    assert child["definitionOrdinal"] == expected["definitionOrdinal"]
    assert child["disabled"] is False
    matches = child["originalMatches"]
    assert len(matches) == len(expected["originalMatches"]) == 2
    for match, golden in zip(matches, expected["originalMatches"], strict=True):
        assert {k: semantic._profile_term(v).n3() for k, v in match.bindings} == golden["bindings"]
        assert [triple_key(t) for t in match.when] == golden["when"]
        assert len(match.proof_leaves) == len(match.when)
        for term_index, term_value in enumerate(
            (match.when[0].subject, match.when[0].predicate, match.when[0].object)
        ):
            record_index = 0 if match is matches[0] or term_index == 1 else 1
            assert_source(term_value.source, f"/cases/0/asserted/{record_index}/{term_index}")
    (firing,) = child["batch"].firings
    assert firing.rule_id == expected["ruleId"]
    assert firing.when == matches[0].when and firing.bindings == matches[0].bindings
    assert_source(firing.source, "/cases/0/rules/0")
    assert firing.revision == "1" and firing.policy == PROFILE
    true = expected["originalMatches"][0]
    (comparison,) = firing.comparisons
    assert comparison.result is true["comparison"]["result"]
    assert comparison.operator == true["comparison"]["operator"]
    for actual, side in ((comparison.left, "left"), (comparison.right, "right")):
        assert type(actual) is ProfileValue and type(actual.value) is Number
        assert type(actual.term) is TermInput
        assert actual.domain == "N" and actual.language == ""
        number = true["comparison"][side + "Number"]
        assert (
            type(actual.value.numerator) is int
            and str(actual.value.numerator) == number["numerator"]
        )
        assert (
            type(actual.value.denominator) is int
            and str(actual.value.denominator) == number["denominator"]
        )
        assert type(actual.value.negative_zero) is bool
        assert actual.value.negative_zero is number["negative_zero"]
        assert actual.term.language_raw is None
        assert actual.term.datatype_iri == "http://www.w3.org/2001/XMLSchema#integer"
        assert actual.term.lexical_form == ("01" if side == "left" else "1")
        assert_source(actual.term.source, true["comparison"][side + "Source"]["pointer"])
    assert [h.index for h in firing.heads] == [h["headIndex"] for h in true["heads"]]
    assert [triple_key(h.triple) for h in firing.heads] == [h["triple"] for h in true["heads"]]
    assert len(firing.heads) == expected["headOccurrences"] == 3
    assert [list(row) for row in native["rules"]] == expected["uniqueDerivedRdfTriples"]
    assert {tuple(k) for k in native["rules"]} == {tuple(h["triple"]) for h in true["heads"]}
    leaves = {r["reference"]: r["triple"] for r in native["proofLeaves"]}
    assert {tuple(leaves[r]) for r in firing.basis} == {tuple(k) for k in true["leafBasis"]}
    assert len(native["evidence"]) == 3
    for evidence, head in zip(native["evidence"], firing.heads, strict=True):
        assert evidence["rule"] == firing.rule_id
        assert evidence["firingIndex"] == 0 and evidence["headIndex"] == head.index
        assert list(evidence["result"]) == triple_key(head.triple)
        assert [list(k) for k in evidence["inputs"]] == true["when"]
        assert evidence["basis"] == firing.basis
    assert restored.batches.formal_authority is False


@pytest.mark.parametrize("case_id", GRAPH_IDS)
def test_real_rule_graph(case_id, tmp_path, goldens):
    index, case = next((i, c) for i, c in enumerate(GRAPH_INPUT["cases"]) if c["id"] == case_id)
    directory = artifact_directory(tmp_path, case_id)
    actual, produced, restored = observe_rule(case, index, directory)
    expected = goldens["explanation"]["completeHeads" if index == 0 else "falseThenError"]
    observation = {
        "id": case_id,
        "kind": "rule-graph",
        "input": case,
        "inputSha256": sha(PURE.read_bytes()),
        "actual": actual,
        "expected": expected,
        "assertion": "fail",
        "testOnlyCompareCallsAreNotPersistentTrace": True,
    }
    try:
        if index == 0:
            assert actual["status"] == "success", actual
            assert actual["fullPayloadEqual"] and actual["fullChildrenEqual"]
            assert_complete_heads(produced, restored, expected)
            catalog = goldens["explanation"]["expectedCatalogObservations"][case_id]
            for key, value in catalog.items():
                assert list(getattr(produced.actual_catalog, key)) == value
            assert [
                c.get("returnedBoolean")
                for c in actual["comparatorCalls"]
                if c["phase"] == "production"
            ][:2] == [True, False]
        else:
            assert actual["status"] == "error" and actual["stage"] == "production"
            assert actual["exceptionType"] == "ProfileExecutionFault"
            diag = actual["diagnostic"]
            assert diag["reason"] == "RULE_COMPARISON_TYPE_MISMATCH"
            assert diag["classification"] == "input" and diag["ruleId"] == expected["ruleId"]
            assert diag["location"]["section"] == expected["expectedPrivateLocation"]["section"]
            assert diag["location"]["index"] == expected["expectedPrivateLocation"]["index"]
            assert actual["publicError"] == {
                "code": "SEMANTIC_INPUT_INVALID",
                "messageKey": "semantics.inputInvalid",
                "params": {"field": "rule"},
                "retryable": False,
            }
            calls = actual["comparatorCalls"]
            assert len(calls) == 2 and calls[0]["returnedBoolean"] is False
            assert calls[1]["error"]["reason"] == "RULE_COMPARISON_TYPE_MISMATCH"
            assert all(c["phase"] == "production" for c in calls)
            assert not actual["producedResultReturned"] and not actual["restoredResultReturned"]
        observation["assertion"] = "pass"
    finally:
        (directory / "observation.json").write_bytes(canonical(observation))


def assert_consumer_report(actual, expected):
    assert actual["status"] == "success", actual
    result = actual["result"]
    assert type(result["conforms"]) is bool and result["conforms"] is expected["conforms"]
    assert actual["validatorRuns"] == 1
    report = actual["realValidatorReport"]
    assert report["conforms"] is result["conforms"]
    component_prefix = "<http://www.w3.org/ns/shacl#"
    assert sorted(
        v["constraint"].removeprefix(component_prefix).removesuffix(">")
        for v in result["violations"]
    ) == sorted(expected["components"])
    required = expected.get("requiredResultRows", [])
    assert len(result["violations"]) == len(required)
    unmatched = list(result["violations"])
    mapping = {
        "focusNode": "focus",
        "resultPath": "path",
        "value": "value",
        "sourceShape": "sourceShape",
        "sourceConstraintComponent": "constraint",
        "resultSeverity": "severity",
    }
    for row in required:
        candidate = next(
            v
            for v in unmatched
            if v["focus"] == row["focusNode"]
            and v["constraint"] == row["sourceConstraintComponent"]
        )
        for name, key in mapping.items():
            # Inputs use named shapes; original report bnode IDs are not fixtures.
            assert candidate[key] == row[name]
        unmatched.remove(candidate)
    assert not unmatched
    assert len(report["rows"]) == len(required)
    for row in report["rows"]:
        assert all(len(row[name]) == 1 for name in mapping if name != "value")
        assert len(row["value"]) <= 1


@pytest.mark.parametrize("case", CONSUMER_INPUT["cases"], ids=lambda c: c["id"])
def test_real_consumer_cell(case, tmp_path, goldens):
    directory = artifact_directory(tmp_path, case["id"])
    (directory / "input.json").write_bytes(canonical(case))
    actual = observe_consumer(case, directory)
    expected = goldens["consumers"][case["id"]]
    observation = {
        "id": case["id"],
        "kind": "consumer-cell",
        "input": case,
        "actual": actual,
        "expected": expected,
        "assertion": "fail",
    }
    try:
        if case["id"] in POLICY_PENDING:
            observation["normativeStatus"] = "pending-policy-or-frontdoor-versus-report"
            assert actual["status"] == "error" and actual["validatorRuns"] == 0
            assert actual["reason"] == (
                "INVALID_SHAPE" if case["id"] == POLICY_PENDING[0] else "INVALID_LITERAL_LEXICAL"
            )
            observation["assertion"] = "observed-pending-not-normative-pass"
            return
        if "query" in case:
            assert actual["status"] == "success", actual
            result = actual["result"]
            assert result["type"] == "SELECT"
            rows = [dict(zip(result["variables"], row, strict=True)) for row in result["rows"]]
            assert rows == expected["rows"]
        else:
            assert_consumer_report(actual, expected)
        observation["assertion"] = "pass"
        observation["normativeStatus"] = "matched"
    finally:
        (directory / "observation.json").write_bytes(canonical(observation))


def test_all_pure_inputs_preserved_and_coverage_is_not_all_five_graphs():
    assert PURE.read_bytes() == (READONLY / "supplemental-graph-inputs.json").read_bytes()
    assert len(GRAPH_INPUT["cases"]) == 5 and len(CONSUMER_INPUT["cases"]) == 13
    assert [c["id"] for c in GRAPH_INPUT["cases"][:2]] == list(GRAPH_IDS)
    assert len({c["id"] for c in CONSUMER_INPUT["cases"]}) == 13
    assert all("expected" not in c for c in GRAPH_INPUT["cases"] + CONSUMER_INPUT["cases"])
