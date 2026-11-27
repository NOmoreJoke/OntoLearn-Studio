"""One fixed-input P1 computation probe, shared by source and packaged entrypoints.

Pure input projections exercise graph mathematics; lifecycle checks stay unexecuted.
No Store, Job, public capability, expected output or given-binding evaluator.
"""

import hashlib
import importlib
import importlib.metadata
import json
import sys
import time
from pathlib import Path

INPUT_SHA256 = "6c6ffc3a1a57d1817583c0a71d24e2847cc5d2d673848878c6e6e72dfe6c39de"
INPUT_BYTES = 1839011
INPUT_CAP = 2_097_152
REPORT_CAP = 67_108_864
CASE_COUNT = 83
DEADLINE_SECONDS = 120
MODULES = (
    "ontolearn_engine.quality",
    *(
        "ontolearn_engine.quality." + name
        for name in (
            "rule_profile",
            "rule_terms",
            "rule_numbers",
            "rule_calendar",
            "rule_comparator",
            "rule_firing",
        )
    ),
)


def _asset():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "provenance/i05/profile-probe-inputs.json"
    return Path(__file__).resolve().parents[4] / "docs/iterations/I05/profile-probe-inputs.json"


def _load_inputs():
    # One exact locator; no package -> checkout or user-directory fallback.
    with _asset().open("rb") as stream:
        raw = stream.read(INPUT_CAP + 1)
    if len(raw) != INPUT_BYTES or hashlib.sha256(raw).hexdigest() != INPUT_SHA256:
        raise ValueError("PROFILE_PROBE_INPUT_INVALID")
    value = json.loads(raw)
    if (
        value["format"] != "i05-profile-input-projection/1"
        or len(value["mathInputs"]) != CASE_COUNT
        or value["expectedIncluded"] is not False
        or value["counts"]
        != {
            "productCases": 50,
            "learningChecks": 54,
            "extensions": 22,
            "originalSetupAndSteps": 106,
            "mathInputRecords": CASE_COUNT,
        }
    ):
        raise ValueError("PROFILE_PROBE_INPUT_INVALID")
    return value


def _construct_case(case):
    """Project only fixture input fields into actual RDF text and RuleSpec.

    input_when is a concrete input graph, not a matcher result. Comparisons and
    heads come only from definition. No expected or input_binding is consulted.
    """
    from rdflib import RDF, RDFS, Literal, URIRef

    from ontolearn_engine.quality.rule_firing import Comparison, RuleSpec, Triple, Variable
    from ontolearn_engine.quality.rule_profile import XSD, SourceRecord, TermInput

    def source(value):
        return None if value is None else SourceRecord(**value)

    def term(value):
        if type(value) is str:
            return Variable(value) if value.startswith("?") else TermInput("iri", value)
        if "kind" in value:
            return TermInput(
                value["kind"],
                value["lexical_form"],
                value["datatype_iri"],
                value["language_raw"],
                source(value["source"]),
            )
        datatype = value["type"]
        return TermInput("literal", value["lexical"], XSD + datatype)

    def n3(value):
        item = term(value)
        if type(item) is not TermInput:
            raise ValueError("PROFILE_PROBE_INPUT_INVALID")
        if item.kind == "iri":
            return URIRef(item.lexical_form).n3()
        return Literal(
            item.lexical_form, datatype=item.datatype_iri, lang=item.language_raw, normalize=False
        ).n3()

    lines = []
    for key, declaration in (
        ("classes", str(RDFS.Class)),
        ("object_properties", "http://www.w3.org/2002/07/owl#ObjectProperty"),
        ("data_properties", "http://www.w3.org/2002/07/owl#DatatypeProperty"),
    ):
        for value in case["catalog"][key]:
            lines.append(f"<{value}> <{RDF.type}> <{declaration}> .")
    for triple in case["input_when"]:
        lines.append(" ".join(n3(triple[key]) for key in ("subject", "predicate", "object")) + " .")
    definition = case["definition"]
    spec = RuleSpec(
        definition["rule_id"],
        tuple(Triple(*(term(item) for item in row)) for row in definition["when"]),
        tuple(
            Comparison(term(left), op, term(right)) for left, op, right in definition["comparisons"]
        ),
        tuple(Triple(*(term(item) for item in row)) for row in definition["heads"]),
        source(definition["source"]),
        definition["revision"],
        definition["definition_digest"],
        definition["policy"],
    )
    return "\n".join(lines) + "\n", (spec,)


def _identities():
    from ontolearn_engine.resources import resource_manifest

    modules = []
    for name in MODULES:
        module = importlib.import_module(name)
        if module.__name__ != name or module.__spec__.name != name:
            raise ValueError("PROFILE_PROBE_MODULE_INVALID")
        path = Path(module.__file__)
        # A frozen archive's pyc is not the approved source's .py byte domain.
        source_hash = (
            hashlib.sha256(path.read_bytes()).hexdigest()
            if not getattr(sys, "frozen", False) and path.suffix == ".py"
            else None
        )
        modules.append({"module": name, "sourceSha256": source_hash})
    return {
        "frozen": bool(getattr(sys, "frozen", False)),
        "modules": modules,
        "distributions": {
            name: importlib.metadata.version(name)
            for name in (
                "rdflib",
                "pyshacl",
                "pyparsing",
                "owlrl",
                "html5rdf",
                "prettytable",
                "wcwidth",
                "packaging",
            )
        },
        "resources": resource_manifest(),
    }


def _construct_records(case, index):
    """Decode only fixed original-input projection fields, never oracle outputs.

    Sources identify decoded scalar fields in this exact projection asset. Original
    source pointers/transforms remain separate; no unavailable raw Turtle/span or
    authenticated producer is fabricated from a JSON value or N3 spelling.
    """
    from ontolearn_engine.quality.rule_firing import Comparison, RuleSpec, Triple, Variable
    from ontolearn_engine.quality.rule_profile import SourceRecord, TermInput
    from ontolearn_engine.semantic_turtle import decode_profile_term

    data = case["input"]
    base = f"#/mathInputs/{index}/input"
    revision = None

    def source(pointer, text=None, *, version=revision):
        return SourceRecord(base + pointer, INPUT_SHA256, version, text)

    def term(value, pointer, *, iri=False):
        if value.startswith("?") and not iri:
            return Variable(value)
        original = TermInput("iri", value) if iri else decode_profile_term(value)
        return TermInput(
            original.kind,
            original.lexical_form,
            original.datatype_iri,
            original.language_raw,
            source(pointer, value),
        )

    records = []
    for section in ("asserted", "ontology"):
        for position, record in enumerate(data[section]):
            pointer = f"/{section}/{position}/triple"
            records.append(
                tuple(
                    term(record["triple"][key], pointer + "/" + key, iri=key != "object")
                    for key in ("subject", "predicate", "object")
                )
            )
    specs = []
    for position, definition in enumerate(data["definitions"]):
        pointer = f"/definitions/{position}"

        def rows(section, *, pointer=pointer, definition=definition):
            return tuple(
                Triple(
                    *(
                        term(
                            row[key],
                            f"{pointer}/{section}/{j}/{key}",
                            iri=key != "object" and not row[key].startswith("?"),
                        )
                        for key in ("subject", "predicate", "object")
                    )
                )
                for j, row in enumerate(definition[section])
            )

        specs.append(
            RuleSpec(
                definition["rule_id"],
                rows("when"),
                tuple(
                    Comparison(
                        term(row["left"], f"{pointer}/comparisons/{j}/left"),
                        row["operator"],
                        term(row["right"], f"{pointer}/comparisons/{j}/right"),
                    )
                    for j, row in enumerate(definition["comparisons"])
                ),
                rows("heads"),
                source(pointer, version=definition["revision"]),
                definition["revision"],
                definition["definitionJsonValueSha256"],
            )
        )
    return tuple(records), tuple(specs), tuple(data["disabled_rule_ids"])


def _report_bytes(value):
    # Aggregate collection has its own finite bound. Each computation continues
    # to enforce its unchanged 8 MiB complete payload+rows limit.
    result = bytearray()
    for chunk in json.JSONEncoder(
        ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).iterencode(value):
        raw = chunk.encode("utf-8")
        if len(result) + len(raw) > REPORT_CAP:
            raise ValueError("PROFILE_PROBE_REPORT_LIMIT")
        result.extend(raw)
    return bytes(result)


def main(argv=None):
    """Source has no args; packaged dispatcher calls main([]) after its flag."""
    args = sys.argv[1:] if argv is None else argv
    if type(args) is not list or args:
        sys.stderr.write("PROFILE_PROBE_ARGUMENTS_INVALID\n")
        return 2
    started = time.monotonic()
    try:
        from ontolearn_engine.resources import CONTRACT, ROOT
        from ontolearn_engine.semantic_execution import (
            ProfileExecutionFault,
            execute_profile_records,
        )

        inputs = _load_inputs()
        schema = json.loads((ROOT / "v2/schema.json").read_bytes())
        output = []
        retained_bytes = 0
        failed = False
        for index, case in enumerate(inputs["mathInputs"]):
            item = {
                "caseId": case["id"],
                "sourceRefs": case["sourceRefs"],
                "inputProjectionJsonSha256": case["inputProjectionJsonSha256"],
                "fullOriginalInputContext": case["input"]["fullOriginalInputContext"],
                "scopeNotes": case["scopeNotes"],
                "purpose": case["purpose"],
            }
            if not case["eligibleStandaloneMathInput"]:
                failed = True
                item.update(status="not-executed", reason="ORIGINAL_INPUT_CONTEXT_INCOMPLETE")
            else:
                records, rules, disabled = _construct_records(case, index)
                try:
                    result = execute_profile_records(
                        records,
                        rules,
                        disabled_rule_ids=disabled,
                        error_catalog=CONTRACT.ERROR_CATALOG,
                        error_schema=schema,
                    )
                    item.update(status="success", result=result)
                except ProfileExecutionFault as error:
                    failed = True
                    item.update(status="failure", error=error.error, diagnostic=error.diagnostic)
            # Preflight this full item before retention; never clip a firing/head,
            # original false binding, source, tail row or failed-case diagnostic.
            retained_bytes += len(_report_bytes(item))
            if retained_bytes > REPORT_CAP - INPUT_CAP:
                raise ValueError("PROFILE_PROBE_REPORT_LIMIT")
            output.append(item)
            if time.monotonic() - started > DEADLINE_SECONDS:
                raise ValueError("PROFILE_PROBE_TIME_LIMIT")
        report = {
            "format": "i05-profile-probe/2",
            "scope": "mathematical-input-projections",
            "acceptanceOracleCompared": False,
            "lifecycleExecuted": False,
            "originalRequestedOperationPassed": False,
            "sourceAuthorityAuthenticated": False,
            "collectionComplete": len(output) == CASE_COUNT,
            "inputSha256": INPUT_SHA256,
            "inputBytes": INPUT_BYTES,
            "counts": inputs["counts"],
            "cases": output,
            "identity": _identities(),
            "productCases": inputs["productCases"],
            "learningChecks": inputs["learningChecks"],
            "originalOperations": inputs["originalOperations"],
            "unresolvedInputContexts": inputs["unresolvedInputContexts"],
            "nonClaims": inputs["nonClaims"],
            "limits": {
                "inputBytes": INPUT_CAP,
                "aggregateReportBytes": REPORT_CAP,
                "perComputationPayloadAndRowsBytes": 8_388_608,
                "cases": CASE_COUNT,
                "deadlineSeconds": DEADLINE_SECONDS,
                "deadlineEnforcement": "boundary-check; caller must enforce hard process timeout",
            },
        }
        encoded = _report_bytes(report)
        if time.monotonic() - started > DEADLINE_SECONDS:
            raise ValueError("PROFILE_PROBE_TIME_LIMIT")
        sys.stdout.write(encoded.decode("utf-8") + "\n")
        return 1 if failed else 0
    except Exception:
        sys.stderr.write("PROFILE_PROBE_FAILED\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
