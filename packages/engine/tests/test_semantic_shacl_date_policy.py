"""Finite UTC date policy: actual parser/Validator, complete reports and paid gates."""

import hashlib
import json
import os
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from ontolearn_engine import semantic
from ontolearn_engine.semantic_offline import SemanticError
from ontolearn_engine.semantic_turtle import parse_graph
from rdflib import RDF, SH, XSD, Literal

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "docs/reviews/T05/profile-M1-math-explanation-input-contract"
CASES = json.loads((FIXTURES / "consumer-C-inputs.json").read_bytes())["cases"]
GOLDENS = json.loads((FIXTURES / "consumer-C-goldens.json").read_bytes())["cases"]
UTC = "utc-date-range-v1"
WIDE = "integer-illtyped-report-v1"
PREFIX = """@prefix ex: <urn:m1:> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
"""


def literal(spelling="2000-01-01Z", datatype="date"):
    return json.dumps(spelling, ensure_ascii=False) + "^^xsd:" + datatype


def data(value=None):
    return PREFIX + "ex:s a ex:Focus" + ("; ex:p " + value if value else "") + " ."


def shape(parameter=None):
    if parameter is None:
        parameter = "sh:minInclusive " + literal()
    return PREFIX + (
        "ex:node a sh:NodeShape; sh:targetClass ex:Focus; sh:property ex:shape .\n"
        "ex:shape a sh:PropertyShape; sh:path ex:p" + ("; " + parameter if parameter else "") + " ."
    )


def row(value, constraint="MinInclusiveConstraintComponent", focus="s", source="shape"):
    return {
        "focus": "<urn:m1:" + focus + ">",
        "path": "<urn:m1:p>",
        "constraint": "<http://www.w3.org/ns/shacl#" + constraint + ">",
        "sourceShape": "<urn:m1:" + source + ">",
        "value": value,
        "severity": "<http://www.w3.org/ns/shacl#Violation>",
    }


def date_term(spelling):
    return '"' + spelling + '"^^<http://www.w3.org/2001/XMLSchema#date>'


def case(identity):
    return next(item for item in CASES if item["id"] == identity)


@pytest.fixture
def observe(request):
    records = []

    def invoke(suffix, text, constraints, *, data_policy="strict", range_policy=UTC):
        original_run = semantic.Validator.run
        original_init = semantic._UtcDateWork.__init__
        original_charge = semantic._UtcDateWork.charge
        original_parse = semantic._parse_turtle
        record = {
            "id": request.node.nodeid + "/" + suffix,
            "dataTurtle": text,
            "shapesTurtle": constraints,
            "dataPolicy": data_policy,
            "rangePolicy": range_policy,
            "stage": "policy",
            "work": [],
            "validatorCalls": [],
            "result": None,
            "error": None,
        }
        records.append(record)
        meters = {}

        def parse(*args, **kwargs):
            record["stage"] = "parse-shapes" if kwargs.get("shapes") else "parse-data"
            graph = original_parse(*args, **kwargs)
            triples = sorted(semantic._key(t) for t in graph)
            record.setdefault("parsedGraphs", []).append(
                {
                    "stage": record["stage"],
                    "triples": len(graph),
                    "sha256": hashlib.sha256(json.dumps(triples).encode()).hexdigest(),
                }
            )
            return graph

        def init(self):
            original_init(self)
            item = {
                "version": self.version,
                "initial": self.remaining,
                "used": 0,
                "remaining": self.remaining,
                "chargesRLE": [],
                "failure": None,
            }
            meters[id(self)] = item
            record["work"].append(item)

        def charge(self, amount=1):
            item = meters[id(self)]
            record["stage"] = self.stage
            try:
                original_charge(self, amount)
            except SemanticError:
                item["failure"] = {
                    "stage": self.stage,
                    "requested": amount,
                    "remaining": self.remaining,
                    "used": self.used,
                }
                raise
            else:
                runs = item["chargesRLE"]
                if runs and runs[-1][:2] == [self.stage, amount]:
                    runs[-1][2] += 1
                else:
                    runs.append([self.stage, amount, 1])
            finally:
                item["used"], item["remaining"] = self.used, self.remaining

        def run(self, *args, **kwargs):
            record["stage"] = "validator"
            call = {"dataTriples": sorted(semantic._key(t) for t in self.data_graph)}
            record["validatorCalls"].append(call)
            actual = original_run(self, *args, **kwargs)
            call["conforms"] = bool(actual[0])
            call["rawReportNTriples"] = actual[1].serialize(format="nt")
            call["reportTriples"] = sorted(semantic._key(t) for t in actual[1])
            return actual

        try:
            with (
                patch.object(semantic.Validator, "run", run),
                patch.object(semantic._UtcDateWork, "__init__", init),
                patch.object(semantic._UtcDateWork, "charge", charge),
                patch.object(semantic, "_parse_turtle", parse),
            ):
                result = semantic.validate_shacl_text(
                    text, constraints, data_policy=data_policy, range_policy=range_policy
                )
            record["result"] = result
            record["stage"] = "complete"
            return result, record
        except Exception as error:
            record["error"] = {
                "type": type(error).__name__,
                "code": error.code if isinstance(error, SemanticError) else None,
            }
            if record["error"]["code"] == "FACT_SCOPE_CONTAINS_AXIOMS":
                record["stage"] = "fact-scope"
            raise
        finally:
            directory = os.environ.get("I05_SHACL_DATE_EVIDENCE_DIR")
            if directory:
                dest = Path(directory)
                dest.mkdir(parents=True, exist_ok=True)
                target = dest / (hashlib.sha256(record["id"].encode()).hexdigest() + ".json")
                assert not target.exists(), "do not overwrite first failure or evidence identity"
                target.write_text(json.dumps(record, ensure_ascii=True, indent=2) + "\n")

    invoke.records = records
    return invoke


def reject(observe, code, text, constraints, **options):
    with pytest.raises(SemanticError, match="^" + code + "$"):
        observe(code, text, constraints, **options)
    record = observe.records[-1]
    assert record["validatorCalls"] == [] and record["result"] is None
    return record


def assert_report(result, record, violations=(), *, policy="strict", range_policy=UTC):
    assert result == {
        "entryVersion": "i05-shacl-text-2" if range_policy == UTC else "i05-shacl-text-1",
        "dataPolicy": policy,
        "rangePolicy": range_policy,
        "report": {"conforms": not violations, "violations": list(violations)},
    }
    assert len(record["validatorCalls"]) == 1
    call = record["validatorCalls"][0]
    assert call["conforms"] is (not violations)
    # Independently read the actual RDF report, rather than trust extraction alone.
    raw = parse_graph(call["rawReportNTriples"], base_uri="urn:i05:report:")
    actual_rows = []
    for result_node in raw.subjects(RDF.type, SH.ValidationResult):
        value = raw.value(result_node, SH.value)
        actual_rows.append(
            {
                "focus": raw.value(result_node, SH.focusNode).n3(),
                "path": raw.value(result_node, SH.resultPath).n3(),
                "constraint": raw.value(result_node, SH.sourceConstraintComponent).n3(),
                "sourceShape": raw.value(result_node, SH.sourceShape).n3(),
                "value": value.n3() if value is not None else None,
                "severity": raw.value(result_node, SH.resultSeverity).n3(),
            }
        )
    assert sorted(actual_rows, key=str) == sorted(violations, key=str)
    assert [v.toPython() for v in raw.objects(None, SH.conforms)] == [not violations]


@pytest.mark.parametrize("policy", ["strict", WIDE])
def test_original_C_date_uses_adopted_extension_without_changing_old_golden(observe, policy):
    original = case("C-inclusive-date-entry")
    actual, record = observe(
        "utc", original["dataTurtle"], original["shapesTurtle"], data_policy=policy
    )
    expected = next(g["expected"] for g in GOLDENS if g["id"] == original["id"])
    extension = expected["ifI05ExplicitlySupportsXsdDateOperatorExtension"]
    assert extension == {
        "conforms": True,
        "requiredResultRows": [],
        "derivation": "Same valid date, same explicit offset and lexical denotes equal value; "
        "inclusive <= true under the explicitly chosen date relation extension",
    }
    assert_report(actual, record, policy=policy)
    reject(
        observe,
        "INVALID_SHAPE",
        original["dataTurtle"],
        original["shapesTurtle"],
        data_policy=policy,
        range_policy="legacy",
    )


@pytest.mark.parametrize("constraint", ["minInclusive", "maxInclusive"])
@pytest.mark.parametrize("spelling", ["1999-12-31Z", "2000-01-01Z", "2000-01-02Z"])
def test_inclusive_before_equal_after_complete_real_report(observe, constraint, spelling):
    actual, record = observe(
        "boundary", data(literal(spelling)), shape("sh:" + constraint + " " + literal())
    )
    violated = (
        spelling < "2000-01-01Z" if constraint == "minInclusive" else spelling > "2000-01-01Z"
    )
    component = (
        "MinInclusiveConstraintComponent"
        if constraint == "minInclusive"
        else "MaxInclusiveConstraintComponent"
    )
    assert_report(actual, record, [row(date_term(spelling), component)] if violated else [])
    assert ("<urn:m1:s>", "<urn:m1:p>", date_term(spelling)) in record["validatorCalls"][0][
        "dataTriples"
    ]


@pytest.mark.parametrize("spelling", ["0001-01-01Z", "9999-12-31Z", "2000-02-29Z"])
def test_full_accepted_calendar_domain_on_both_operands(observe, spelling):
    actual, record = observe(
        "calendar",
        data(literal(spelling)),
        shape("sh:minInclusive " + literal(spelling) + "; sh:maxInclusive " + literal(spelling)),
    )
    assert_report(actual, record)


@pytest.mark.parametrize("side", ["bound", "value"])
@pytest.mark.parametrize(
    "spelling,early",
    [
        ("1900-02-29Z", True),
        ("2000-13-01Z", True),
        ("2000-00-01Z", True),
        ("2000-01-32Z", True),
        ("0000-01-01Z", True),
        ("-0001-01-01Z", True),
        ("10000-01-01Z", True),
        ("2000-1-01Z", True),
        ("２０００-01-01Z", True),
        (" 2000-01-01Z", True),
        ("20000101Z", True),
        ("2000-01-01", False),
        ("2000-01-01+00:00", False),
        ("2000-01-01+01:00", False),
        ("2000-01-01-05:00", False),
        ("2000-01-01z", False),
        ("2000-01-01T12:00:00Z", False),
    ],
)
def test_exact_lexical_domain_rejects_both_sides_before_validator(observe, side, spelling, early):
    text = data(literal(spelling if side == "value" else "2000-01-01Z"))
    constraints = shape(
        "sh:minInclusive " + literal(spelling if side == "bound" else "2000-01-01Z")
    )
    code = (
        "INVALID_LITERAL_LEXICAL"
        if early
        else "INVALID_SHAPE"
        if side == "bound"
        else "RDF_TERM_INVALID"
    )
    record = reject(observe, code, text, constraints)
    assert record["stage"] == (
        ("parse-shapes" if side == "bound" else "parse-data") if early else "date-" + side
    )


@pytest.mark.parametrize(
    "other",
    [literal("2000-01-01T00:00:00Z", "dateTime"), '"1"^^xsd:integer', '"a"', '"a"@en', "ex:iri"],
)
@pytest.mark.parametrize("side", ["bound", "value"])
def test_date_incompatible_pairs_both_directions(observe, other, side):
    bound = other if side == "bound" else literal()
    value = literal() if side == "bound" else other
    code = (
        "INVALID_SHAPE"
        if side == "bound" and other in ['"a"', '"a"@en', "ex:iri"]
        else "RDF_TERM_INVALID"
    )
    reject(observe, code, data(value), shape("sh:minInclusive " + bound))


def test_mixed_bounds_rejected_even_without_target(observe):
    reject(
        observe,
        "INVALID_SHAPE",
        PREFIX,
        shape("sh:minInclusive " + literal() + '; sh:maxInclusive "1"^^xsd:integer'),
    )


def test_reversed_bounds_are_real_independent_constraints(observe):
    actual, record = observe(
        "reverse",
        data(literal()),
        shape(
            "sh:minInclusive "
            + literal("2000-01-02Z")
            + "; sh:maxInclusive "
            + literal("1999-12-31Z")
        ),
    )
    assert_report(
        actual,
        record,
        [
            row(date_term("2000-01-01Z"), "MaxInclusiveConstraintComponent"),
            row(date_term("2000-01-01Z")),
        ],
    )
    actual, record = observe(
        "reverse-no-focus",
        PREFIX,
        shape(
            "sh:minInclusive "
            + literal("2000-01-02Z")
            + "; sh:maxInclusive "
            + literal("1999-12-31Z")
        ),
    )
    assert_report(actual, record)


@pytest.mark.parametrize("mode", ["no-target", "no-value", "minCount", "unrelated"])
def test_target_and_missing_values_do_not_invent_date_failures(observe, mode):
    text = data(literal("2000-01-01+00:00")) if mode == "no-target" else data()
    if mode == "no-target":
        text = text.replace("ex:Focus", "ex:Other")
    if mode == "unrelated":
        text += "\nex:other ex:p " + literal("2000-01-01+00:00") + " ."
    constraints = shape(
        "sh:minInclusive " + literal() + ("; sh:minCount 1" if mode == "minCount" else "")
    )
    actual, record = observe(mode, text, constraints)
    assert_report(
        actual, record, [row(None, "MinCountConstraintComponent")] if mode == "minCount" else []
    )


def test_all_values_and_shared_property_targets_are_checked(observe):
    constraints = (
        shape() + "\nex:node2 a sh:NodeShape; sh:targetClass ex:Other; sh:property ex:shape ."
    )
    text = data(literal()) + "\nex:t a ex:Other; ex:p " + literal("1999-12-31Z") + " ."
    actual, record = observe("shared", text, constraints)
    assert_report(actual, record, [row(date_term("1999-12-31Z"), focus="t")])
    bad = data(literal() + ", " + literal("2000-01-01+00:00"))
    reject(observe, "RDF_TERM_INVALID", bad, shape())
    # Same path on a non-target subject is not accidentally pulled into either target.
    text = data(literal()) + "\nex:t a ex:Neither; ex:p " + literal("2000-01-01+00:00") + " ."
    actual, record = observe("shared-unrelated", text, constraints)
    assert_report(actual, record)


@pytest.mark.parametrize("policy", ["strict", WIDE])
@pytest.mark.parametrize("range_policy", ["legacy", UTC])
def test_integer_policy_and_identity_four_combinations(observe, policy, range_policy):
    original = case("C-illtyped-entry")
    if policy == "strict":
        reject(
            observe,
            "INVALID_LITERAL_LEXICAL",
            original["dataTurtle"],
            original["shapesTurtle"],
            data_policy=policy,
            range_policy=range_policy,
        )
    else:
        actual, record = observe(
            "wide",
            original["dataTurtle"],
            original["shapesTurtle"],
            data_policy=policy,
            range_policy=range_policy,
        )
        assert_report(
            actual,
            record,
            [
                row(
                    '"not-an-int"^^<http://www.w3.org/2001/XMLSchema#integer>',
                    "DatatypeConstraintComponent",
                )
            ],
            policy=policy,
            range_policy=range_policy,
        )
        actual, record = observe(
            "wide-no-target",
            original["dataTurtle"].replace("ex:Focus", "ex:Other"),
            original["shapesTurtle"],
            data_policy=policy,
            range_policy=range_policy,
        )
        assert_report(actual, record, policy=policy, range_policy=range_policy)


@pytest.mark.parametrize(
    "identity",
    [
        "C-langString",
        "C-datatype-exact",
        "C-inclusive-numeric",
        "C-inclusive-nni",
        "C-inclusive-dateTime-equal",
        "C-inclusive-dateTime-before",
        "C-inclusive-type-error",
        "C-count-term-identity",
        "C-in-term-identity",
    ],
)
def test_non_date_original_normative_cells_keep_full_reports(observe, identity):
    original = case(identity)
    actual, record = observe(identity, original["dataTurtle"], original["shapesTurtle"])
    golden = next(g["expected"] for g in GOLDENS if g["id"] == identity)
    names = {
        "focusNode": "focus",
        "resultPath": "path",
        "sourceShape": "sourceShape",
        "sourceConstraintComponent": "constraint",
        "resultSeverity": "severity",
        "value": "value",
    }
    rows = [
        {names[k]: v for k, v in r.items() if k in names}
        for r in golden.get("requiredResultRows", [])
    ]
    # Exact field sets/values, independent of dictionary insertion order.
    assert actual["report"] == {"conforms": golden["conforms"], "violations": rows}
    assert_report(actual, record, rows)


def test_new_legal_policy_reaches_text_gate_and_v2_remains_unknown(observe):
    reject(observe, "TEXT_TYPE_INVALID", None, None)
    reject(observe, "SCOPE_SELECTION_TYPE_INVALID", None, None, range_policy="utc-date-range-v2")


@pytest.mark.parametrize("options", [{}, {"data_policy": "strict"}, {"range_policy": UTC}])
def test_required_keywords_have_no_extension_default(options):
    with pytest.raises(TypeError):
        semantic.validate_shacl_text(data(literal()), shape(), **options)


@pytest.mark.parametrize("policy", [None, [], True, "strict ", 1])
def test_invalid_data_policy_precedes_parsing(observe, policy):
    reject(observe, "SCOPE_SELECTION_TYPE_INVALID", None, None, data_policy=policy)


@pytest.mark.parametrize("predicate", ["minExclusive", "maxExclusive"])
def test_exclusive_stays_unsupported(observe, predicate):
    reject(
        observe, "UNSUPPORTED_SHACL", data(literal()), shape("sh:" + predicate + " " + literal())
    )


@pytest.mark.parametrize(
    "text,constraints,code",
    [
        (None, shape(), "TEXT_TYPE_INVALID"),
        ("not Turtle", shape(), "INVALID_TURTLE"),
        ("\ud800", shape(), "INVALID_UNICODE"),
        ("#" * (1_048_576 + 1), shape(), "TEXT_INPUT_LIMIT"),
        (PREFIX + "[] ex:p 1 .", shape(), "UNSUPPORTED_BLANK_NODE"),
        (data('"1"^^<urn:unknown>'), shape(), "UNSUPPORTED_LITERAL_DATATYPE"),
        (data('"NaN"^^xsd:double'), shape(), "UNSUPPORTED_NONFINITE_LITERAL"),
        (
            PREFIX + "ex:s owl:imports <https://example.invalid/o> .",
            shape(),
            "EXTERNAL_ACCESS_DENIED",
        ),
        (PREFIX + "<relative> ex:p 1 .", shape(), "ABSOLUTE_IRI_REQUIRED"),
        (data(literal()), shape().replace("sh:path ex:p", "sh:path ex:p, ex:q"), "INVALID_SHAPE"),
        (
            data(literal()) + "\nex:A rdfs:subClassOf ex:Focus .",
            shape(),
            "FACT_SCOPE_CONTAINS_AXIOMS",
        ),
    ],
)
def test_existing_front_doors_are_preserved(observe, text, constraints, code):
    reject(observe, code, text, constraints)


def test_bound_domain_precedes_fact_scope_but_actual_value_does_not(observe):
    axioms = data(literal("2000-01-01+00:00")) + "\nex:A rdfs:subClassOf ex:Focus ."
    reject(
        observe, "INVALID_SHAPE", axioms, shape("sh:minInclusive " + literal("2000-01-01+00:00"))
    )
    reject(observe, "FACT_SCOPE_CONTAINS_AXIOMS", axioms, shape())


def test_utc_policy_does_not_change_legacy_or_global_entry_semantics(observe):
    actual, record = observe("utc", data(literal()), shape())
    assert_report(actual, record)
    reject(observe, "INVALID_SHAPE", data(literal()), shape(), range_policy="legacy")
    graph = semantic.parse_turtle(data(literal()))
    shapes = semantic.parse_turtle(shape(), shapes=True)
    with pytest.raises(SemanticError, match="^INVALID_SHAPE$"):
        semantic.check_shapes(graph, shapes)
    assert semantic.SEMANTICS_VERSION == "i05-finite-6"
    assert semantic.SHACL_TEXT_ENTRY_VERSION == "i05-shacl-text-1"
    assert semantic.query(graph, "SELECT ?s WHERE {?s <urn:m1:p> ?v}")["rows"] == [
        {"s": "<urn:m1:s>"}
    ]


def test_private_library_compatibility_guard_never_casts_or_shrinks_domain():
    # Per-object malformed native values simulate an incompatible library; no global patch.
    for wrong in (date(2001, 1, 1), datetime(2000, 1, 1), None):
        term = Literal("2000-01-01Z", datatype=XSD.date, normalize=False)
        term._value = wrong
        with pytest.raises(SemanticError, match="^VALIDATION_FAILED$"):
            semantic._utc_date_fields(term, semantic._UtcDateWork(), "RDF_TERM_INVALID")


def test_private_work_first_debit_and_exact_balance_are_separate_from_public_input():
    class Source:
        def __init__(self):
            self.created = self.pulled = 0

        def triples(self, pattern):
            self.created += 1
            owner = self

            class Iterator:
                def __next__(self):
                    owner.pulled += 1
                    raise StopIteration

            return Iterator()

    work = semantic._UtcDateWork()
    assert work.version == "i05-utc-date-preflight/1"
    work.charge(1_000_000)
    assert work.remaining == 0 and work.used == 1_000_000
    with pytest.raises(SemanticError, match="^GRAPH_INPUT_LIMIT$"):
        work.charge()
    assert work.used == 1_000_000
    for balance, created in [(0, 0), (1, 1)]:
        work = semantic._UtcDateWork()
        work.charge(1_000_000 - balance)
        source = Source()
        with pytest.raises(SemanticError, match="^GRAPH_INPUT_LIMIT$"):
            work.ordered(source, (None, None, None), 0)
        assert source.created == created and source.pulled == 0


def budget_input(n, extra_values=False):
    # Short prefixes keep the actual public input inside the original 1MiB text gate.
    text = "@prefix : <urn:m1:> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
    lines = [f":f{i} a :Focus ." for i in range(n)]
    if extra_values:
        for focus, count in [("f0", 6), ("f1", 8)]:
            values = ", ".join(f'"2000-01-{day:02d}Z"^^xsd:date' for day in range(2, count + 2))
            lines.append(":" + focus + " :p " + values + " .")
    return text + "\n".join(lines)


def test_public_one_million_unit_boundary_is_an_independent_invoice(observe):
    # C(n)=3+3n+n*ceil(log2(max(2,n))); the independent plan fixes this invoice.
    # One shape costs 54 in bound phase, then 16 fixed + (7+16)*n in value phase.
    # Six and eight values on different focuses add 6*(22+3)+8*(22+3)=350.
    # 70 + 23*43460 + 350 = 1,000,000. No measured usage feeds this expected value.
    text = budget_input(43460, extra_values=True)
    assert len(text.encode()) <= 1_048_576
    constraints = shape("sh:minInclusive " + literal("0001-01-01Z"))
    actual, record = observe("exact-million", text, constraints)
    assert_report(actual, record)
    assert record["work"][0]["used"] == 1_000_000
    assert record["work"][0]["remaining"] == 0
    # The same real public input with one fewer private ticket is a distinct seam test.
    with patch.object(semantic, "_UTC_DATE_WORK_CAP", 999_999):
        record = reject(observe, "GRAPH_INPUT_LIMIT", text, constraints)
    assert record["work"][0]["initial"] == 999_999
    assert record["work"][0]["failure"] == {
        "stage": "date-value",
        "requested": 1,
        "remaining": 0,
        "used": 999_999,
    }
    # A separate larger public input crosses the real fixed cap; no cap override.
    record = reject(
        observe, "GRAPH_INPUT_LIMIT", budget_input(43461, extra_values=True), constraints
    )
    assert record["work"][0]["initial"] == 1_000_000


def d1_input(bad_path):
    text = budget_input(20000) + "\n:f0 :p" + str(bad_path) + ' "2000-01-01+00:00"^^xsd:date .'
    lines = [PREFIX]
    for i in range(100):
        lines.append(
            f"ex:n{i:03d} a sh:NodeShape; sh:targetClass ex:Focus; sh:property ex:b{i:03d} ."
        )
        lines.append(
            f"ex:b{i:03d} a sh:PropertyShape; sh:path ex:p{i}; sh:minInclusive " + literal() + " ."
        )
    return text, "\n".join(lines)


@pytest.mark.parametrize("bad_path,code", [(0, "RDF_TERM_INVALID"), (99, "GRAPH_INPUT_LIMIT")])
def test_D1_order_invariance_of_cost_stage_and_first_error(observe, bad_path, code):
    text, constraints = d1_input(bad_path)
    records = []
    # Reverse complete triples/statements, preserving exactly the same RDF and prefixes.
    originals = text, constraints
    for suffix in ["forward", "reverse", "rotate"]:

        def reorder(source, mode=suffix):
            lines = source.splitlines()
            prefixes = [line for line in lines if line.startswith("@prefix")]
            triples = [line for line in lines if line and not line.startswith("@prefix")]
            reordered = (
                list(reversed(triples)) if mode == "reverse" else triples[17:] + triples[:17]
            )
            return "\n".join(prefixes + reordered)

        text, constraints = (
            originals if suffix == "forward" else tuple(reorder(v) for v in originals)
        )
        with pytest.raises(SemanticError, match="^" + code + "$"):
            observe(suffix, text, constraints)
        record = observe.records[-1]
        assert not record["validatorCalls"] and record["result"] is None
        records.append(record)
    assert all(r["stage"] == "date-value" for r in records)
    assert all(r["work"] == records[0]["work"] for r in records)
    assert all(r["parsedGraphs"] == records[0]["parsedGraphs"] for r in records)
    assert records[0]["work"][0]["initial"] == 1_000_000


def test_original_graph_limit_precedes_date_preflight(observe):
    text = PREFIX + "ex:s ex:p " + ",".join(str(i) for i in range(100001)) + " ."
    assert len(text.encode()) <= 1_048_576
    record = reject(observe, "GRAPH_INPUT_LIMIT", text, shape())
    assert record["work"] == [] and record["stage"] == "parse-data"
