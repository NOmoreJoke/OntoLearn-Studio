#!/usr/bin/env python3
"""Deterministic input-only preparation. Never imports or executes engine/test code."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPPLIER = "6891a5842302859a531cf82767c5a482417bc274"
DOCS = "ee2b30a2dad35b2d395f9c735aff80371ab41110"
C4 = "523c478d5f39671c4ac7c1ea6997e51d3047d58e"
REVIEW = ROOT / "docs/reviews/I05/source-package-probe-source"
CORPUS = REVIEW / "inputs/corpus"
ASSETS = ROOT / "packages/engine/src/ontolearn_engine/probe_inputs"
INPUT_NAME = "i05-source-package-parity-inputs.json"
MANIFEST_NAME = "i05-source-package-parity-manifest.json"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
XSD = "http://www.w3.org/2001/XMLSchema#"
OWL = "http://www.w3.org/2002/07/owl#"
TYPE, SUB, DOMAIN, RANGE = RDF + "type", RDFS + "subClassOf", RDFS + "domain", RDFS + "range"
WIDE, UTC = "integer-illtyped-report-v1", "utc-date-range-v1"
SOURCES: dict[tuple[str, str], dict] = {}
DATASETS: dict[str, dict] = {}
OBS: list[dict] = []
DEDUPE: dict[bytes, str] = {}
CHECK = sys.argv[1:] == ["--check"]


def canonical(value):
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("ascii")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def raw_source(path, ref=SUPPLIER):
    key = (ref, path)
    if key not in SOURCES:
        raw = subprocess.run(
            ["git", "show", ref + ":" + path], cwd=ROOT, check=True, capture_output=True
        ).stdout
        name = ref[:12] + "__" + path.replace("/", "__") + ".raw"
        target = CORPUS / name
        if CHECK:
            assert target.read_bytes() == raw, path
        else:
            CORPUS.mkdir(parents=True, exist_ok=True)
            if target.exists():
                assert target.read_bytes() == raw, "Do not overwrite a different fixed original"
            else:
                target.write_bytes(raw)
        SOURCES[key] = {
            "ref": ref,
            "path": path,
            "bytes": len(raw),
            "sha256": sha(raw),
            "corpusPath": str(target.relative_to(ROOT)),
        }
    item = SOURCES[key]
    return (ROOT / item["corpusPath"]).read_bytes()


def source(path, pointer="", ref=SUPPLIER):
    raw_source(path, ref)
    item = SOURCES[(ref, path)]
    return {k: item[k] for k in ("ref", "path", "bytes", "sha256")} | {"pointer": pointer}


def source_original(row):
    ref = row.get("ref", row.get("copyRef", SUPPLIER))
    raw = raw_source(row["path"], ref)
    assert sha(raw) == row["sha256"], row["path"]
    return source(row["path"], row.get("pointer", ""), ref)


def json_source(path, ref=SUPPLIER):
    return json.loads(raw_source(path, ref))


def literal(node, assignments=None):
    """Restricted literal/concatenation extraction, not evaluation of Python source."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, (ast.Tuple, ast.List)):
        return [literal(item, assignments) for item in node.elts]
    if isinstance(node, ast.Dict):
        return {
            literal(k, assignments): literal(v, assignments)
            for k, v in zip(node.keys, node.values, strict=True)
        }
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = literal(node.left, assignments), literal(node.right, assignments)
        assert type(left) is type(right) is str
        return left + right
    if isinstance(node, ast.Name) and assignments is not None and node.id in assignments:
        return literal(assignments[node.id], assignments)
    raise ValueError("Nonliteral source expression is not an input extraction")


def module_literals(path):
    tree = ast.parse(raw_source(path).decode("utf-8"))
    assignments = {
        n.targets[0].id: n.value
        for n in tree.body
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
    }
    return tree, assignments


def assignment(path, name):
    _, items = module_literals(path)
    return literal(items[name], items)


def picked(row, fields):
    return {name: copy.deepcopy(row[name]) for name in fields if name in row}


def add(
    label, family, operation, dataset, parameters, refs, *, source_case=None, status="complete"
):
    encoded = canonical(dataset)
    dataset_id = DEDUPE.get(encoded)
    if dataset_id is None:
        dataset_id = label
        DATASETS[dataset_id] = dataset
        DEDUPE[encoded] = dataset_id
    assert label not in {row["id"] for row in OBS}
    OBS.append(
        {
            "id": label,
            "sourceCaseId": source_case or label,
            "family": family,
            "operation": operation,
            "datasetId": dataset_id,
            "parameters": parameters,
            "sourceRefs": refs,
            "contextStatus": status,
            "projectionSha256": sha(encoded),
        }
    )
    return dataset_id


def term(value, datatype=None, language=None, *, iri=False, source_record=None):
    return {
        "kind": "iri" if iri else "literal",
        "lexical_form": value,
        "datatype_iri": datatype,
        "language_raw": language,
        "source": source_record,
    }


def iri_term(value):
    return term(value, iri=True)


def V(value):
    return {"variable": value}


def records(rows):
    return [[iri_term(v) if type(v) is str else v for v in row] for row in rows]


def rule(identity, when, heads, comparisons=()):
    return {
        "rule_id": identity,
        "when": when,
        "comparisons": list(comparisons),
        "heads": heads,
        "source": None,
        "revision": None,
        "definition_digest": None,
        "policy": "OntoLearn-rule-comparison-profile/1",
    }


def risk_rule():
    ns = "urn:ontolearn:"
    e, a = V("?equipment"), V("?alarm")
    return rule(
        "R-risk",
        [
            [e, iri_term(TYPE), iri_term(ns + "Equipment")],
            [e, iri_term(ns + "alarm"), a],
            [a, iri_term(ns + "level"), term("High")],
            [a, iri_term(ns + "status"), term("Open")],
        ],
        [[e, iri_term(TYPE), iri_term(ns + "HighRiskEquipment")]],
    )


def ttl_dataset(text, format="turtle", shapes=False):
    return {"kind": "turtle", "text": text, "format": format, "shapes": shapes}


def shape_dataset(data, shapes):
    return {"kind": "shape", "dataText": data, "shapesText": shapes}


def profile_dataset(data):
    record_fields = ("triple", "source")
    definition_fields = (
        "rule_id",
        "enabled",
        "when",
        "comparisons",
        "heads",
        "revision",
        "definitionJsonValueSha256",
        "source",
        "rawTurtle",
        "rawTurtleSpan",
    )
    return {
        "kind": "profile",
        "input": {
            "asserted": [picked(r, record_fields) for r in data["asserted"]],
            "ontology": [picked(r, record_fields) for r in data["ontology"]],
            "definitions": [picked(r, definition_fields) for r in data["definitions"]],
            "disabled_rule_ids": copy.deepcopy(data["disabled_rule_ids"]),
        },
    }


def n3_literal(value, datatype="date"):
    return json.dumps(value, ensure_ascii=True) + "^^xsd:" + datatype


def fixture(scale):
    # Exact input expansion of fixed storage_probe.py:35-57. No Store helper import.
    blocks = ["@prefix : <urn:ontolearn:> ."]
    for i in range(scale):
        for equipment, name in (("001", "泵站A"), ("002", "泵站B"), ("003", "备用泵C")):
            blocks.append(f'<urn:case:{i}:equipment/{equipment}> a :Equipment; :name "{name}" .')
        for alarm, equipment, level, status in (
            ("A01", "001", "High", "Open"),
            ("A02", "002", "High", "Closed"),
            ("A03", "003", "Low", "Open"),
        ):
            blocks.append(
                f'<urn:case:{i}:alarm/{alarm}> a :Alarm; :level "{level}"; :status "{status}" .'
            )
            blocks.append(
                f"<urn:case:{i}:equipment/{equipment}> :alarm <urn:case:{i}:alarm/{alarm}> ."
            )
    return "\n".join(blocks)


def build():
    profile_path = "docs/iterations/I05/profile-probe-inputs.json"
    original = json_source(profile_path)
    assert (
        len(raw_source(profile_path)) == 1839011
        and sha(raw_source(profile_path))
        == "6c6ffc3a1a57d1817583c0a71d24e2847cc5d2d673848878c6e6e72dfe6c39de"
    )
    for item in original["mathInputs"]:
        for ref in item["sourceRefs"]:
            source_original(ref)
    for row in original["unresolvedInputContexts"]:
        source_original(row["source"])
    context_rows = []
    for index, item in enumerate(original["mathInputs"]):
        data = item["input"]
        context_rows.append(
            {
                "index": index,
                **picked(
                    item,
                    (
                        "id",
                        "sourceRefs",
                        "inputProjectionJsonSha256",
                        "eligibleStandaloneMathInput",
                        "scopeNotes",
                    ),
                ),
                **picked(
                    data,
                    (
                        "fullOriginalInputContext",
                        "lifecycleExecuted",
                        "originalRequestedOperationPassed",
                        "sourceAuthorityAuthenticated",
                    ),
                ),
            }
        )
        add(
            "profile-83/" + item["id"],
            "profile-83",
            "profile",
            profile_dataset(data),
            {},
            [source(profile_path, f"/mathInputs/{index}")],
            source_case=item["id"],
            status="not-executed"
            if not item["eligibleStandaloneMathInput"]
            else "fragment"
            if not data["fullOriginalInputContext"]
            else "complete",
        )
    contexts = {
        "mathInputContexts": context_rows,
        "originalOperations": original["originalOperations"],
        "productCases": original["productCases"],
        "learningChecks": original["learningChecks"],
        "unresolved": original["unresolvedInputContexts"],
        "nonClaims": original["nonClaims"],
    }
    c_path = "docs/reviews/T05/profile-M1-math-explanation-input-contract/consumer-C-inputs.json"
    consumers = json_source(c_path)["cases"]
    for index, item in enumerate(consumers):
        refs = [source(c_path, f"/cases/{index}")]
        if "query" in item:
            add(
                item["id"],
                "consumer-C-query",
                "query",
                {"kind": "query", "dataText": item["dataTurtle"], "queryText": item["query"]},
                {},
                refs,
            )
        else:
            ds = shape_dataset(item["dataTurtle"], item["shapesTurtle"])
            if index == 11:
                for policy in ("strict", WIDE):
                    for range_policy in ("legacy", UTC):
                        add(
                            item["id"] + "/" + policy + "/" + range_policy,
                            "consumer-C-date",
                            "shacl-text",
                            ds,
                            {"dataPolicy": policy, "rangePolicy": range_policy},
                            refs,
                            source_case=item["id"],
                        )
            elif index == 12:
                for policy in ("strict", WIDE):
                    add(
                        item["id"] + "/" + policy,
                        "consumer-C-integer",
                        "shacl-text",
                        ds,
                        {"dataPolicy": policy, "rangePolicy": "legacy"},
                        refs,
                        source_case=item["id"],
                    )
            else:
                add(item["id"], "consumer-C-shape", "shape", ds, {}, refs)
    date_original = consumers[11]
    for identity, replacement in (("before", "1999-12-31Z"), ("offset", "2000-01-01+00:00")):
        assert date_original["dataTurtle"].count("2000-01-01Z") == 1
        ds = shape_dataset(
            date_original["dataTurtle"].replace("2000-01-01Z", replacement),
            date_original["shapesTurtle"],
        )
        add(
            "utc-date/C-" + identity,
            "utc-date",
            "shacl-text",
            ds,
            {"dataPolicy": "strict", "rangePolicy": UTC},
            [source(c_path, "/cases/11")],
            source_case="C-inclusive-date-entry",
        )
    samples_path = "packages/engine/src/ontolearn_engine/semantic_samples.py"
    sample_ref = [source(samples_path, "ast:constants/input-only")]
    prefix = assignment(samples_path, "PREFIX")
    shapes = assignment(samples_path, "SHAPES")
    ontology10 = assignment(samples_path, "ONTOLOGY")
    fixture_ref = [source("packages/engine/src/ontolearn_engine/storage_probe.py", "L35-L57")]
    query = assignment("packages/engine/src/ontolearn_engine/storage_probe.py", "QUERY")
    assert sha(query.encode()) == "7879b25f2833b8e485b53d3f6664220836ada716ec29ae7de82f907eae014ab5"
    assert (
        sha(fixture(1).encode())
        == "b0bcc466774f37d4f6a520900b8e7caa5f4fb7f827bbcf8c5ad0e9d12946ea0c"
    )
    assert (
        sha(fixture(10).encode())
        == "25393c99db270c57a75cd75c675876d148659fef7e7624e4197e90754b257ed2"
    )
    add("turtle/G-base-fixture", "turtle", "parse", ttl_dataset(fixture(1)), {}, fixture_ref)
    add(
        "rdfs/ten-ontology-suite",
        "rdfs",
        "legacy-reason",
        {"kind": "legacy", "dataText": fixture(1) + "\n" + ontology10, "rules": [risk_rule()]},
        {},
        sample_ref + fixture_ref,
    )
    for scale in (1, 10):
        old_path = "packages/engine/src/ontolearn_engine/semantic_probe.py"
        old_tree = ast.parse(raw_source(old_path, C4).decode())
        candidates = [
            n.value
            for n in ast.walk(old_tree)
            if isinstance(n, ast.Constant)
            and type(n.value) is str
            and ":alarm rdfs:domain :MonitoredEquipment" in n.value
            and ":CriticalPump rdfs:subClassOf :Pump" in n.value
        ]
        assert len(candidates) == 1
        ds = {
            "kind": "b1",
            "assertedText": fixture(scale),
            "ontologyText": candidates[0],
            "shapesText": shapes,
            "queryText": query,
            "rules": [risk_rule()],
            "replaceEquipmentTypes": [
                {"subject": f"urn:case:{i}:equipment/001", "type": "urn:ontolearn:CriticalPump"}
                for i in range(scale)
            ],
            "seed": 20261019,
            "scale": scale,
        }
        add(
            f"b1-semantic/{scale}x",
            "b1-measurement",
            "b1-measurement",
            ds,
            {},
            fixture_ref + [source(old_path, "L229-L259", C4)],
        )
    add_queries(prefix, fixture(1), sample_ref)
    add_turtle(prefix, sample_ref)
    add_rdfs(prefix, sample_ref)
    add_scope(prefix, shapes, samples_path)
    add_original_qv(original, profile_path)
    add_records()
    add_shapes(consumers)
    add_integer()
    add_date()
    add_offline(shapes, fixture(1), sample_ref)
    return contexts


def add_queries(prefix, text, refs):
    queries = {
        "ask": "ASK { <urn:case:0:alarm/A01> ?p ?o }",
        "words-in-string": 'SELECT ?x WHERE { BIND("SERVICE FROM" AS ?x) }',
        ("optional-unbound"): (
            "SELECT ?s ?missing WHERE {?s a <urn"
            ":ontolearn:Equipment> OPTIONAL {?s "
            "<urn:absent> ?missing}} ORDER BY ?s"
        ),
        "count": "SELECT (COUNT(?s) AS ?n) WHERE {?s a <urn:ontolearn:Equipment>}",
        ("order-tie"): (
            "SELECT ?s ?v WHERE {VALUES (?s ?v) "
            "{(<urn:b> 1) (<urn:a> 1) (<urn:c> 2"
            ")}} ORDER BY ?v ?s"
        ),
        "filter": 'SELECT ?s WHERE {?s <urn:ontolearn:level> ?v FILTER(?v = "High")} ORDER BY ?s',
        "string-distinct": 'SELECT DISTINCT ?v WHERE {VALUES ?v {"x" "x"^^<http://www.w3.org/2001/XMLSchema#string>}}',
        "string-count": 'SELECT (COUNT(DISTINCT ?v) AS ?n) WHERE {VALUES ?v {"x" "x"^^<http://www.w3.org/2001/XMLSchema#string>}}',
        "insert-update": "INSERT DATA {<urn:s> <urn:p> <urn:o>}",
        "delete-update": "DELETE WHERE {?s ?p ?o}",
        "construct": "CONSTRUCT {?s ?p ?o} WHERE {?s ?p ?o}",
        "describe": "DESCRIBE <urn:s>",
        "invalid": "SELECT WHERE {",
        "load-update": "LOAD <https://example.invalid/deny>",
        "rand": "SELECT (RAND() AS ?r) WHERE {}",
        "now": "SELECT (NOW() AS ?r) WHERE {}",
        "uuid": "SELECT (UUID() AS ?r) WHERE {}",
        "struuid": "SELECT (STRUUID() AS ?r) WHERE {}",
        "bnode": "SELECT (BNODE() AS ?r) WHERE {}",
    }
    for name, query_text in queries.items():
        add(
            "query/" + name,
            "readonly-query",
            "query",
            {"kind": "query", "dataText": text, "queryText": query_text},
            {},
            refs,
        )
    ns = "urn:ontolearn:"
    expressions = [
        'STRDT("x", <' + XSD + "string>)",
        'STR("x"^^<' + XSD + "string>)",
        'CONCAT("", "x"^^<' + XSD + "string>)",
        'SUBSTR(STRDT("xy", <' + XSD + "string>), 1, 1)",
        'REPLACE(STRDT("a", <' + XSD + 'string>), "a", "x")',
        'LCASE(STRDT("X", <' + XSD + "string>))",
    ]
    string_text = prefix + (
        ':bothString :value "x", "x"^^xsd:st'
        'ring . :plainString :value "x" . :t'
        'ypedString :value "x"^^xsd:string .'
    )
    for index, expression in enumerate(expressions):
        q = (
            "SELECT ?s WHERE { BIND("
            + expression
            + " AS ?v) ?s <"
            + ns
            + 'value> ?v FILTER(sameTerm(?v, "x")) } ORDER BY ?s'
        )
        add(
            f"query/string-expression-{index}",
            "readonly-query",
            "query",
            {"kind": "query", "dataText": string_text, "queryText": q},
            {},
            refs,
        )


def add_turtle(prefix, refs):
    pairs = [
        ("01", "1", "integer"),
        ("+01", "+1", "integer"),
        ("-01", "-1", "integer"),
        ("-00", "0", "integer"),
        ("01.00", "1.0", "decimal"),
        ("+01.00", "+1.0", "decimal"),
        ("-01.00", "-1.0", "decimal"),
        ("01e+00", "1e+00", "double"),
        ("+01e+00", "+1e+00", "double"),
        ("-01e+00", "-1e+00", "double"),
    ]
    for index, (token, other, dtype) in enumerate(pairs):
        # The strings are original lexical inputs, not normalized numeric values.
        text = prefix + ":unit :value " + token + ", " + n3_literal(other, dtype) + " ."
        add(
            f"turtle/numeric-lexical-{index}",
            "turtle-lexical",
            "parse",
            ttl_dataset(text),
            {},
            refs,
        )
    for index, value in enumerate(("", "x", 'quote" slash\\', "line\nnext", "你好")):
        literal_text = json.dumps(value, ensure_ascii=True)
        add(
            f"turtle/string-identity-{index}",
            "turtle-lexical",
            "parse",
            ttl_dataset(
                prefix + ":unit :value " + literal_text + ", " + literal_text + "^^xsd:string ."
            ),
            {},
            refs,
        )
    for name, text in (
        ("lang-case", ':s :p "Word"@EN-us, "Word"@en-US .'),
        ("integer-distinct", ':s :p "01"^^xsd:integer, "1"^^xsd:integer .'),
    ):
        add("turtle/" + name, "turtle-lexical", "parse", ttl_dataset(prefix + text), {}, refs)
    for index, text in enumerate(
        (
            "<urn:s> <urn:p> 1.2.3 .",
            "<urn:orphan> .",
            "([<urn:p> <urn:o>]) .",
            "<urn:s> <urn:p> 01 . true .",
            "<relative> <urn:p> <urn:o> .",
            "<urn:bad iri> <urn:p> <urn:o> .",
            "[] <urn:p> <urn:o> .",
            '<urn:s> <urn:p> "bad"^^<urn:unknown> .',
            '<urn:s> <urn:p> "NaN"^^<' + XSD + "double> .",
        )
    ):
        add(
            f"turtle/front-{index}",
            "turtle-rejection",
            "parse",
            ttl_dataset(text, shapes=index < 4),
            {},
            refs,
        )


def add_rdfs(prefix, refs):
    ns = "urn:ontolearn:"
    head = [[V("?s"), iri_term(TYPE), iri_term(ns + "Observed")]]
    cases = {
        "type": [(ns + "x", TYPE, ns + "A"), (ns + "A", SUB, ns + "B")],
        "domain-depth2": [
            (ns + "p", DOMAIN, ns + "A"),
            (ns + "x", ns + "p", ns + "y"),
            (ns + "A", SUB, ns + "B"),
        ],
        "range": [(ns + "p", RANGE, ns + "C"), (ns + "x", ns + "p", ns + "y")],
        "subclass": [(ns + "A", SUB, ns + "B"), (ns + "B", SUB, ns + "C")],
        "cycle": [
            (ns + "A", SUB, ns + "B"),
            (ns + "B", SUB, ns + "C"),
            (ns + "C", SUB, ns + "A"),
            (ns + "x", TYPE, ns + "A"),
        ],
        "domain-first-witness": [
            (ns + "u", ns + "p", ns + "b"),
            (ns + "u", ns + "p", ns + "a"),
            (ns + "p", DOMAIN, ns + "C"),
        ],
        "range-first-witness": [
            (ns + "b", ns + "p", ns + "u"),
            (ns + "a", ns + "p", ns + "u"),
            (ns + "p", RANGE, ns + "C"),
        ],
    }
    for name, rows in cases.items():
        text = "\n".join(" ".join("<" + t + ">" for t in row) + " ." for row in rows)
        rules = (
            [rule("observe", [[V("?s"), iri_term(TYPE), iri_term(ns + "C")]], head)]
            if "witness" in name
            else []
        )
        add(
            "rdfs/" + name,
            "rdfs-finite",
            "legacy-reason",
            {"kind": "legacy", "dataText": text, "rules": rules},
            {},
            refs,
        )
    next_rule = rule(
        "R-next",
        [[V("?equipment"), iri_term(TYPE), iri_term(ns + "HighRiskEquipment")]],
        [[V("?equipment"), iri_term(TYPE), iri_term(ns + "NeedsInspection")]],
    )
    for name, extra, rules in (
        (
            "no-rule-feedback",
            ":HighRiskEquipment <" + SUB + "> :NeedsInspection .",
            [risk_rule(), next_rule],
        ),
        (
            "multiple-matches",
            (
                "<urn:case:0:equipment/001> :alarm <"
                "urn:case:0:alarm/A04> . <urn:case:0"
                ':alarm/A04> :level "High"; :status '
                '"Open" .'
            ),
            [risk_rule()],
        ),
    ):
        add(
            "legacy/" + name,
            "legacy-rule",
            "legacy-reason",
            {"kind": "legacy", "dataText": fixture(1) + "\n" + prefix + extra, "rules": rules},
            {},
            refs,
        )
    for name, heads in (
        ("repeated-variable", [[V("?s"), iri_term(TYPE), iri_term("urn:Self")]]),
        ("unbound-head", [[V("?o"), iri_term(TYPE), iri_term("urn:Self")]]),
    ):
        add(
            "legacy/" + name,
            "legacy-rule",
            "legacy-reason",
            {
                "kind": "legacy",
                "dataText": "<urn:a> <urn:p> <urn:b> . <urn:c> <urn:p> <urn:c> .",
                "rules": [rule("same", [[V("?s"), iri_term("urn:p"), V("?s")]], heads)],
            },
            {},
            refs,
        )


def add_scope(prefix, shapes, path):
    tree, constants = module_literals(path)
    function = next(
        n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "scope_suite"
    )
    inputs = {}
    for node in function.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in ("ontology", "asserted", "shapes")
        ):
            inputs[node.targets[0].id] = literal(node.value.args[0], constants)
    assert set(inputs) == {"ontology", "asserted", "shapes"}
    ds = {
        "kind": "scope",
        "assertedText": inputs["asserted"],
        "ontologyText": inputs["ontology"],
        "rules": [risk_rule()],
        "shapesText": inputs["shapes"],
        "queryText": "SELECT ?s ?c WHERE {?s a ?c} ORDER BY ?s ?c",
    }
    for mode in (
        "asserted",
        "fresh",
        "project",
        "missing-source",
        "wrong-source",
        "missing-result",
        "nonexact-include",
        "unselected-rules",
        "unselected-result",
        "facts-axioms",
    ):
        add(
            "scope/" + mode,
            "scope",
            "scope",
            ds,
            {"mode": mode},
            [source(path, "ast:scope_suite input assignments")],
        )


def original_text(triples):
    # A raw JSON triple already contains the original object N3 spelling.
    return "\n".join(
        "<" + row["subject"] + "> <" + row["predicate"] + "> " + row["object"] + " ."
        for row in triples
    )


def add_original_qv(original, profile_path):
    refs = [source(profile_path, "/mathInputs/0/input")]
    data = original["mathInputs"][0]["input"]
    raw = data["asserted"]
    text = original_text([row["triple"] for row in raw])
    path = "tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/cases.json"
    json_source(path)
    # Preserve full operations in corpus; only explicit data transforms are runtime inputs.
    refs += [source(path, "/cases/41"), source(path, "/cases/42"), source(path, "/cases/49")]
    query_path = (
        "tests/fixtures/quality/approved-T09"
        "-873c8c0/tests/fixtures/product-bas"
        "elines/unclosed-high.rq"
    )
    query_text = raw_source(query_path).decode()
    add(
        "original-Q01",
        "original-query",
        "query",
        {"kind": "query", "dataText": text, "queryText": query_text},
        {},
        refs,
        source_case="Q-01",
    )
    before = '"Open"'
    subject = "urn:ontolearn:learning:alarm/A01"
    changed = []
    replacements = 0
    for row in raw:
        triple = dict(row["triple"])
        if triple["subject"] == subject and triple["predicate"] == "urn:ontolearn:learning:status":
            assert triple["object"] == before
            triple["object"] = '"Closed"'
            replacements += 1
        changed.append(original_text([triple]))
    assert replacements == 1
    add(
        "original-Q02",
        "original-query",
        "query",
        {"kind": "query", "dataText": "\n".join(changed), "queryText": query_text},
        {},
        refs,
        source_case="Q-02",
    )
    shape = (
        "@prefix sh: <http://www.w3.org/ns/s"
        "hacl#> .\n<urn:original:EquipmentNam"
        "e> a sh:NodeShape; sh:targetClass <"
        "urn:ontolearn:learning:Equipment>; "
        "sh:property <urn:original:Name> .\n<"
        "urn:original:Name> a sh:PropertySha"
        "pe; sh:path <urn:ontolearn:learning"
        ":name>; sh:minCount 1 ."
    )
    missing = [
        row
        for row in raw
        if (row["triple"]["subject"], row["triple"]["predicate"])
        != ("urn:ontolearn:learning:equipment/003", "urn:ontolearn:learning:name")
    ]
    assert len(missing) == len(raw) - 1
    missing_text = original_text([row["triple"] for row in missing])
    for identity, content in (
        ("original-V01-before", text),
        ("original-V01-missing", missing_text),
        ("original-V01-repaired", text),
    ):
        add(
            identity,
            "original-shape-repair",
            "shape",
            shape_dataset(content, shape),
            {},
            refs,
            source_case="V-01",
        )
    transfer = original["mathInputs"][77]["input"]
    transfer_text = original_text([row["triple"] for row in transfer["asserted"]])
    transfer_shape = shape
    # The input catalogue's raw text is the only authority for this repair value.
    transfer_path = (
        "tests/fixtures/quality/approved-T09-873c8c0/content/learning/transfer-inputs.json"
    )
    transfer_raw = json_source(transfer_path)
    repair_name = next(
        row["name"]
        for row in transfer_raw["repair"]["referenceCatalogue"]
        if row["equipmentId"] == "102"
    )
    # Do not invent a full project/rule context for this original repair fragment.
    for identity, content in (
        ("transfer-repair-before", transfer_text),
        (
            "transfer-repair-after",
            transfer_text
            + "\n<urn:ontolearn:learning:equipment/102> <urn:ontolearn:learning:name> "
            + json.dumps(repair_name, ensure_ascii=True)
            + " .",
        ),
    ):
        add(
            identity,
            "transfer-shape-repair",
            "shape",
            shape_dataset(content, transfer_shape),
            {},
            [source(transfer_path, "/repair")],
            source_case="transfer:repair",
            status="fragment",
        )


def add_records():
    path = "packages/engine/tests/test_semantic_profile_directsteps.py"
    refs = [source(path, "input vectors / independent mathematical fixtures")]

    def iri(value):
        return "urn:" + value

    vectors = {
        "type": [(iri("x"), TYPE, iri("A")), (iri("A"), SUB, iri("B"))],
        "domain-depth2": [
            (iri("p"), DOMAIN, iri("A")),
            (iri("x"), iri("p"), iri("y")),
            (iri("A"), SUB, iri("B")),
        ],
        "range": [(iri("p"), RANGE, iri("C")), (iri("x"), iri("p"), iri("y"))],
        "subclass": [(iri("A"), SUB, iri("B")), (iri("B"), SUB, iri("C"))],
        "first-witness": [
            (iri("x"), TYPE, iri("B")),
            (iri("B"), SUB, iri("Z")),
            (iri("x"), TYPE, iri("A")),
            (iri("A"), SUB, iri("Z")),
        ],
        "cross-rule-witness": [
            (iri("x"), TYPE, iri("B")),
            (iri("B"), SUB, iri("A")),
            (iri("a"), DOMAIN, iri("A")),
            (iri("x"), iri("a"), iri("y")),
        ],
        "range-literal": [(iri("p"), RANGE, iri("C")), (iri("x"), iri("p"), term("text"))],
    }
    for name, rows in vectors.items():
        ds = {"kind": "records", "records": records(rows), "rules": []}
        target = [["<urn:x>", "<" + TYPE + ">", "<urn:B>"]] if name == "domain-depth2" else []
        add(
            "dag/" + name,
            "dag-fullview",
            "dag",
            ds,
            {"materialMode": "records", "rootsTargets": target},
            refs,
        )
    sourced = {"reference": "", "digest": None, "revision": "", "text": "raw a"}
    sourced_b = {"reference": None, "digest": "", "revision": None, "text": "raw b"}
    aliases = records(
        [(iri("p"), TYPE, OWL + "DatatypeProperty"), (iri("q"), TYPE, OWL + "DatatypeProperty")]
    )
    for value, dtype, language, src in (
        ("same", None, None, sourced),
        ("same", XSD + "string", None, sourced_b),
        ("Word", None, "EN-us", sourced),
        ("Word", None, "en-US", sourced_b),
        ("01", XSD + "integer", None, sourced),
        ("1", XSD + "integer", None, sourced_b),
    ):
        aliases.append(
            [
                iri_term(iri("x")),
                iri_term(iri("q") if dtype == XSD + "integer" else iri("p")),
                term(value, dtype, language, source_record=src),
            ]
        )
    ds_aliases = {"kind": "records", "records": aliases, "rules": []}
    add(
        "fullview/raw-aliases",
        "dag-fullview",
        "fullview",
        ds_aliases,
        {"materialMode": "records"},
        refs,
    )
    add(
        "dag/raw-aliases",
        "dag-fullview",
        "dag",
        ds_aliases,
        {"materialMode": "records", "rootsTargets": []},
        refs,
    )
    heads = [[V("?s"), iri_term(iri("out")), V("?o")], [V("?s"), iri_term(iri("out")), V("?o")]]
    ds = {
        "kind": "records",
        "records": records(
            [
                (iri("p"), TYPE, OWL + "ObjectProperty"),
                (iri("out"), TYPE, OWL + "ObjectProperty"),
                (iri("x"), iri("p"), iri("y")),
                (iri("z"), iri("p"), iri("w")),
            ]
        ),
        "rules": [rule("fixture:r", [[V("?s"), iri_term(iri("p")), V("?o")]], heads)],
    }
    roots = [["<urn:x>", "<urn:out>", "<urn:y>"]]
    add(
        "fullview/two-head-occurrences",
        "dag-fullview",
        "fullview",
        ds,
        {"materialMode": "records"},
        refs,
    )
    add(
        "dag/two-head-occurrences",
        "dag-fullview",
        "dag",
        ds,
        {"materialMode": "records", "rootsTargets": roots},
        refs,
    )
    for explanation in (False, True):
        for mutation in (
            "payload-unknown-key",
            "tail-source-tamper",
            "tail-definition-tamper",
            "tail-limits-tamper",
            "tail-child-tamper",
        ):
            add(
                "restore/" + ("explanation/" if explanation else "fullview/") + mutation,
                "restore-negative",
                "restore-negative",
                ds,
                {"explanation": explanation, "mutation": mutation, "rootsTargets": roots},
                refs,
            )
    chain = {"kind": "records", "records": records(vectors["domain-depth2"]), "rules": []}
    for mutation in ("dag-depth-plus-one", "dag-last-premise-forward", "leaf-rename-all"):
        add(
            "restore/explanation/" + mutation,
            "restore-negative",
            "restore-negative",
            chain,
            {
                "explanation": True,
                "mutation": mutation,
                "rootsTargets": [["<urn:x>", "<" + TYPE + ">", "<urn:B>"]],
            },
            refs,
        )
    add(
        "restore/explanation/head-occurrence-1023-15",
        "restore-negative",
        "restore-negative",
        ds,
        {"explanation": True, "mutation": "head-occurrence-1023-15", "rootsTargets": roots},
        refs,
    )
    text = "<urn:x> <" + TYPE + "> <urn:A> . <urn:A> <" + SUB + "> <urn:B> ."
    for operation in ("fullview", "dag"):
        parameters = {"materialMode": "text"}
        if operation == "dag":
            parameters["rootsTargets"] = []
        add(
            operation + "/turtle-entry",
            "dag-fullview",
            operation,
            ttl_dataset(text),
            parameters,
            refs,
        )
    profile_path = "docs/iterations/I05/profile-probe-inputs.json"
    original = json_source(profile_path)
    for index in (0, 55, 73, 74, 75, 76):
        item = original["mathInputs"][index]
        add(
            "fullview/profile-" + str(index),
            "dag-fullview",
            "fullview",
            profile_dataset(item["input"]),
            {"materialMode": "records"},
            [source(profile_path, f"/mathInputs/{index}")],
            source_case=item["id"],
        )


def m1_prefix():
    return assignment("packages/engine/tests/test_semantic_shacl_date_policy.py", "PREFIX")


def m1_data(value=None):
    return m1_prefix() + "ex:s a ex:Focus" + ("; ex:p " + value if value is not None else "") + " ."


def m1_shape(parameter=None):
    if parameter is None:
        parameter = "sh:minInclusive " + n3_literal("2000-01-01Z")
    return (
        m1_prefix()
        + (
            "ex:node a sh:NodeShape; sh:targetCl"
            "ass ex:Focus; sh:property ex:shape "
            ".\nex:shape a sh:PropertyShape; sh:p"
            "ath ex:p"
        )
        + ("; " + parameter if parameter else "")
        + " ."
    )


def add_shapes(consumers):
    path = "packages/engine/tests/test_semantic_profile_shape_entry.py"
    refs = [source(path, "input shape clauses / template front doors")]
    prefix = (
        (
            "@prefix ex: <urn:shape-entry:> .\n@p"
            "refix sh: <http://www.w3.org/ns/sha"
            "cl#> .\n@prefix xsd: <"
        )
        + XSD
        + "> .\n"
    )

    def shp(parameter):
        return (
            prefix
            + (
                "ex:node a sh:NodeShape; sh:targetCl"
                "ass ex:Focus; sh:property ex:shape "
                ". ex:shape a sh:PropertyShape; sh:p"
                "ath ex:p; "
            )
            + parameter
            + " ."
        )

    data = prefix + 'ex:s a ex:Focus; ex:p "0"^^xsd:nonNegativeInteger .'
    parameters = [
        'sh:minInclusive "0"^^xsd:nonNegativeInteger; sh:maxInclusive "0"^^xsd:nonNegativeInteger',
        'sh:minInclusive "bad"^^xsd:integer',
        'sh:minInclusive "-1"^^xsd:nonNegativeInteger',
        'sh:minInclusive "bad"^^xsd:dateTime',
        'sh:minInclusive "a"',
        "sh:minInclusive <urn:x>",
        "sh:datatype <urn:unknown>",
        'sh:datatype "literal"',
        "sh:minCount -1",
        "sh:maxCount true",
    ]
    for index, parameter in enumerate(parameters):
        add(
            f"shape/front-{index}",
            "shape-template",
            "shape",
            shape_dataset(data, shp(parameter)),
            {},
            refs,
        )
    # Four fixes are represented as legal nonNegativeInteger/inclusive, invalid bound,
    # exact datatype, and isolated target/path arity inputs, not serialized results.
    for name, constraints in (
        (
            "duplicate-target",
            shp("sh:minCount 1").replace(
                "sh:targetClass ex:Focus", "sh:targetClass ex:Focus, ex:Other"
            ),
        ),
        ("duplicate-path", shp("sh:minCount 1").replace("sh:path ex:p", "sh:path ex:p, ex:q")),
        ("arbitrary-constraint", shp("sh:minCount 1") + "\nex:other sh:minCount 1 ."),
    ):
        add("shape/" + name, "shape-template", "shape", shape_dataset(data, constraints), {}, refs)
    samples = "packages/engine/src/ontolearn_engine/semantic_samples.py"
    prefix = assignment(samples, "PREFIX")
    for name, constraint, values in (
        ("datatype", "sh:datatype xsd:integer", '"wrong"'),
        ("maximum", "sh:maxCount 1", '"a", "b"'),
        ("allowed", 'sh:in ("good" "ok")', '"bad"'),
        ("minimum", "sh:minInclusive 2", "1"),
        ("upper", "sh:maxInclusive 2", "3"),
    ):
        data = prefix + f":x a :Equipment; :name {values} ."
        constraints = prefix + (
            ":S a sh:NodeShape; sh:targetClass :"
            "Equipment; sh:property :P . :P a sh"
            ":PropertyShape; sh:path :name; "
            f"{constraint}"
            " ."
        )
        add(
            "shape/template-" + name,
            "shape-template",
            "shape",
            shape_dataset(data, constraints),
            {},
            [source(samples, "ast:template_suite input literals")],
        )


def add_integer():
    path = "packages/engine/tests/test_semantic_shacl_entry.py"
    refs = [source(path, "input data/shape clauses and policy parameters")]
    constraints = m1_shape("sh:datatype xsd:integer")
    for index, value in enumerate(("not-an-int", "1.2", "1e2", "", "--1", "+01")):
        for policy in ("strict", WIDE):
            add(
                f"integer/lexical-{index}/{policy}",
                "integer-policy",
                "shacl-text",
                shape_dataset(m1_data(n3_literal(value, "integer")), constraints),
                {"dataPolicy": policy, "rangePolicy": "legacy"},
                refs,
            )
    for name, text, shape in (
        (
            "no-target",
            m1_data(n3_literal("not-an-int", "integer")).replace("ex:Focus", "ex:Other"),
            constraints,
        ),
        ("no-constraint", m1_data(n3_literal("not-an-int", "integer")), m1_shape("")),
        (
            "max-count",
            m1_data(n3_literal("not-an-int", "integer") + ', "1"^^xsd:integer'),
            m1_shape("sh:maxCount 1"),
        ),
    ):
        add(
            "integer/" + name,
            "integer-policy",
            "shacl-text",
            shape_dataset(text, shape),
            {"dataPolicy": WIDE, "rangePolicy": "legacy"},
            refs,
        )
    for index, value in enumerate(
        (
            '"bad"^^xsd:int',
            '"-1"^^xsd:nonNegativeInteger',
            '"bad"^^xsd:decimal',
            '"1"^^<urn:unknown>',
            '"NaN"^^xsd:double',
            '"INF"^^xsd:float',
            '"-INF"^^xsd:double',
            "[]",
            "<urn:bad iri>",
        )
    ):
        add(
            f"integer/other-datatype-{index}",
            "integer-policy",
            "shacl-text",
            shape_dataset(m1_data(value), constraints),
            {"dataPolicy": WIDE, "rangePolicy": "legacy"},
            refs,
        )
    for index, parameter in enumerate(
        (
            'sh:minInclusive "bad"^^xsd:integer',
            'sh:minCount "bad"^^xsd:integer',
            'sh:in ("bad"^^xsd:integer)',
            "sh:minCount -1",
            'sh:datatype "integer"',
            "sh:datatype <urn:unknown>",
            'sh:minInclusive "NaN"^^xsd:double',
        )
    ):
        add(
            f"integer/bound-front-{index}",
            "integer-policy",
            "shacl-text",
            shape_dataset(m1_data('"1"^^xsd:integer'), m1_shape(parameter)),
            {"dataPolicy": WIDE, "rangePolicy": "legacy"},
            refs,
        )
    for position in ("subject", "predicate", "datatype", "shape-path"):
        for policy in ("strict", WIDE):
            text, shape = m1_data('"1"^^xsd:integer'), constraints
            if position == "subject":
                text = text.replace("ex:s a", "<urn:bad iri> a")
            elif position == "predicate":
                text = text.replace("ex:p ", "<urn:bad iri> ")
            elif position == "datatype":
                text = text.replace("^^xsd:integer", "^^<urn:bad iri>")
            else:
                shape = shape.replace("sh:path ex:p", "sh:path <urn:bad iri>")
            add(
                "integer/bad-iri-" + position + "/" + policy,
                "integer-policy",
                "shacl-text",
                shape_dataset(text, shape),
                {"dataPolicy": policy, "rangePolicy": "legacy"},
                refs,
            )
    # Policy is explicit even in invalid cases; missing-key calls are separate below.
    for index, policy in enumerate((None, [], {}, True, "strict ", 1)):
        add(
            f"shacl-policy/data-{index}",
            "shacl-front",
            "shacl-text",
            shape_dataset(None, None),
            {"dataPolicy": policy, "rangePolicy": UTC},
            refs,
        )
    for index, policy in enumerate((None, [], True, "utc-date-range-v2", "core-no-date")):
        add(
            f"shacl-policy/range-{index}",
            "shacl-front",
            "shacl-text",
            shape_dataset(None, None),
            {"dataPolicy": "strict", "rangePolicy": policy},
            refs,
        )
    valid_ds = shape_dataset(m1_data(n3_literal("2000-01-01Z")), m1_shape())
    for name, parameters in (
        ("both", {}),
        ("range", {"dataPolicy": "strict"}),
        ("data", {"rangePolicy": UTC}),
    ):
        add("shacl-policy/missing-" + name, "shacl-front", "shacl-text", valid_ds, parameters, refs)


def budget_text(n, extra=False):
    # Explicit literal/range expansion of fixed test's public input factory.
    text = "@prefix : <urn:m1:> .\n@prefix xsd: <" + XSD + "> .\n"
    lines = [f":f{i} a :Focus ." for i in range(n)]
    if extra:
        for focus, count in (("f0", 6), ("f1", 8)):
            values = ", ".join(f'"2000-01-{day:02d}Z"^^xsd:date' for day in range(2, count + 2))
            lines.append(":" + focus + " :p " + values + " .")
    return text + "\n".join(lines)


def reorder_turtle(text, mode):
    lines = text.splitlines()
    prefixes = [line for line in lines if line.startswith("@prefix")]
    triples = [line for line in lines if line and not line.startswith("@prefix")]
    reordered = list(reversed(triples)) if mode == "reverse" else triples[17:] + triples[:17]
    return "\n".join(prefixes + reordered)


def add_date():
    path = "packages/engine/tests/test_semantic_shacl_date_policy.py"
    refs = [source(path, "explicit test input parameters (no expected/result/report projection)")]

    def emit(name, text, constraints, policy="strict", range_policy=UTC, family="utc-date"):
        add(
            "utc-date/" + name,
            family,
            "shacl-text",
            shape_dataset(text, constraints),
            {"dataPolicy": policy, "rangePolicy": range_policy},
            refs,
        )

    valid = n3_literal("2000-01-01Z")
    for constraint in ("minInclusive", "maxInclusive"):
        for spelling in ("1999-12-31Z", "2000-01-01Z", "2000-01-02Z"):
            emit(
                constraint + "/" + spelling,
                m1_data(n3_literal(spelling)),
                m1_shape("sh:" + constraint + " " + valid),
            )
    for spelling in ("0001-01-01Z", "9999-12-31Z", "2000-02-29Z"):
        emit(
            "calendar/" + spelling,
            m1_data(n3_literal(spelling)),
            m1_shape(
                "sh:minInclusive "
                + n3_literal(spelling)
                + "; sh:maxInclusive "
                + n3_literal(spelling)
            ),
        )
    spellings = (
        "1900-02-29Z",
        "2000-13-01Z",
        "2000-00-01Z",
        "2000-01-32Z",
        "0000-01-01Z",
        "-0001-01-01Z",
        "10000-01-01Z",
        "2000-1-01Z",
        "２０００-01-01Z",
        " 2000-01-01Z",
        "20000101Z",
        "2000-01-01",
        "2000-01-01+00:00",
        "2000-01-01+01:00",
        "2000-01-01-05:00",
        "2000-01-01z",
        "2000-01-01T12:00:00Z",
    )
    for index, spelling in enumerate(spellings):
        for side in ("bound", "value"):
            emit(
                f"lexical-{index}/{side}",
                m1_data(n3_literal(spelling) if side == "value" else valid),
                m1_shape("sh:minInclusive " + (n3_literal(spelling) if side == "bound" else valid)),
            )
    for index, other in enumerate(
        (
            n3_literal("2000-01-01T00:00:00Z", "dateTime"),
            '"1"^^xsd:integer',
            '"a"',
            '"a"@en',
            "ex:iri",
        )
    ):
        for side in ("bound", "value"):
            emit(
                f"incompatible-{index}/{side}",
                m1_data(valid if side == "bound" else other),
                m1_shape("sh:minInclusive " + (other if side == "bound" else valid)),
            )
    mixed = m1_shape("sh:minInclusive " + valid + '; sh:maxInclusive "1"^^xsd:integer')
    emit("mixed-bounds-no-target", m1_prefix(), mixed)
    reversed_bounds = m1_shape(
        "sh:minInclusive "
        + n3_literal("2000-01-02Z")
        + "; sh:maxInclusive "
        + n3_literal("1999-12-31Z")
    )
    emit("reversed", m1_data(valid), reversed_bounds)
    emit("reversed-no-focus", m1_prefix(), reversed_bounds)
    for mode in ("no-target", "no-value", "minCount", "unrelated"):
        text = m1_data(n3_literal("2000-01-01+00:00")) if mode == "no-target" else m1_data()
        if mode == "no-target":
            text = text.replace("ex:Focus", "ex:Other")
        if mode == "unrelated":
            text += "\nex:other ex:p " + n3_literal("2000-01-01+00:00") + " ."
        emit(
            mode,
            text,
            m1_shape(
                "sh:minInclusive " + valid + ("; sh:minCount 1" if mode == "minCount" else "")
            ),
        )
    shared = (
        m1_shape() + "\nex:node2 a sh:NodeShape; sh:targetClass ex:Other; sh:property ex:shape ."
    )
    emit(
        "shared",
        m1_data(valid) + "\nex:t a ex:Other; ex:p " + n3_literal("1999-12-31Z") + " .",
        shared,
    )
    emit("multiple-values", m1_data(valid + ", " + n3_literal("2000-01-01+00:00")), m1_shape())
    emit(
        "shared-unrelated",
        m1_data(valid) + "\nex:t a ex:Neither; ex:p " + n3_literal("2000-01-01+00:00") + " .",
        shared,
    )
    for policy in ("strict", WIDE):
        for range_policy in ("legacy", UTC):
            emit(
                "integer/" + policy + "/" + range_policy,
                m1_data('"not-an-int"^^xsd:integer'),
                m1_shape("sh:datatype xsd:integer"),
                policy,
                range_policy,
            )
            if policy == WIDE:
                emit(
                    "integer-no-target/" + range_policy,
                    m1_data('"not-an-int"^^xsd:integer').replace("ex:Focus", "ex:Other"),
                    m1_shape("sh:datatype xsd:integer"),
                    policy,
                    range_policy,
                )
    for predicate in ("minExclusive", "maxExclusive"):
        emit(predicate, m1_data(valid), m1_shape("sh:" + predicate + " " + valid))
    # The original graph entry deliberately retains legacy policy behavior.
    add(
        "shape/date-legacy-entry",
        "shape-template",
        "shape",
        shape_dataset(m1_data(valid), m1_shape()),
        {},
        refs,
    )
    emit("legacy-text-isolation", m1_data(valid), m1_shape(), range_policy="legacy")
    front_inputs = [
        ("none-data", None, m1_shape()),
        ("none-shapes", m1_data(valid), None),
        ("invalid-turtle-data", "not Turtle", m1_shape()),
        ("invalid-turtle-shapes", m1_data(valid), "not Turtle"),
        ("surrogate-data", "\ud800", m1_shape()),
        ("surrogate-shapes", m1_data(valid), "\ud800"),
        ("text-limit-data", "#" * (1_048_576 + 1), m1_shape()),
        ("text-limit-shapes", m1_data(valid), "#" * (1_048_576 + 1)),
        ("blank", m1_prefix() + "[] ex:p 1 .", m1_shape()),
        ("unknown-datatype", m1_data('"1"^^<urn:unknown>'), m1_shape()),
        ("nonfinite", m1_data('"NaN"^^xsd:double'), m1_shape()),
        ("imports", m1_prefix() + "ex:s owl:imports <https://example.invalid/o> .", m1_shape()),
        ("relative", m1_prefix() + "<relative> ex:p 1 .", m1_shape()),
        ("bad-iri", m1_prefix() + "<urn:bad iri> ex:p 1 .", m1_shape()),
        ("path-arity", m1_data(valid), m1_shape().replace("sh:path ex:p", "sh:path ex:p, ex:q")),
        ("fact-axioms", m1_data(valid) + "\nex:A rdfs:subClassOf ex:Focus .", m1_shape()),
    ]
    for name, text, constraints in front_inputs:
        emit(name, text, constraints, family="shacl-front")
    axioms = m1_data(n3_literal("2000-01-01+00:00")) + "\nex:A rdfs:subClassOf ex:Focus ."
    emit(
        "bound-before-facts", axioms, m1_shape("sh:minInclusive " + n3_literal("2000-01-01+00:00"))
    )
    emit("facts-before-value", axioms, m1_shape())
    for n in (43460, 43461):
        emit(
            "public-budget-" + str(n),
            budget_text(n, True),
            m1_shape("sh:minInclusive " + n3_literal("0001-01-01Z")),
            family="utc-date-public-budget",
        )
    for bad_path in (0, 99):
        data = budget_text(20000) + "\n:f0 :p" + str(bad_path) + ' "2000-01-01+00:00"^^xsd:date .'
        lines = [m1_prefix()]
        for index in range(100):
            lines += [
                (
                    "ex:n"
                    f"{index:03d}"
                    " a sh:NodeShape; sh:targetClass ex:"
                    "Focus; sh:property ex:b"
                    f"{index:03d}"
                    " ."
                ),
                f"ex:b{index:03d} a sh:PropertyShape; sh:path ex:p{index}; sh:minInclusive "
                + valid
                + " .",
            ]
        constraints = "\n".join(lines)
        for order in ("forward", "reverse", "rotate"):
            emit(
                f"D1-p{bad_path}/{order}",
                data if order == "forward" else reorder_turtle(data, order),
                constraints if order == "forward" else reorder_turtle(constraints, order),
                family="utc-date-D1",
            )
    graph_limit = m1_prefix() + "ex:s ex:p " + ",".join(str(i) for i in range(100001)) + " ."
    emit("graph-limit-before-preflight", graph_limit, m1_shape(), family="shacl-front")


def add_offline(shapes, text, refs):
    endpoint = "https://example.invalid/i05-offline"
    queries = {
        "service": f"SELECT * WHERE {{ SERVICE <{endpoint}> {{ ?s ?p ?o }} }}",
        "service-silent": f"ASK {{ SERVICE SILENT <{endpoint}> {{ ?s ?p ?o }} }}",
        ("service-variable"): (
            f"SELECT * WHERE {{ VALUES ?e {{ <{endpoint}> }} SERVICE ?e {{ ?s ?p ?o }} }}"
        ),
        ("service-nested"): (
            f"SELECT * WHERE {{ {{ SELECT * WHERE {{ SeRvIcE <{endpoint}> {{ ?s ?p ?o }} }} }} }}"
        ),
        "from": f"SELECT * FROM <{endpoint}> WHERE {{ ?s ?p ?o }}",
        "from-named": f"SELECT * FROM NAMED <{endpoint}> WHERE {{ GRAPH ?g {{ ?s ?p ?o }} }}",
        "base-from": f"BASE <{endpoint}> SELECT * FROM <relative> WHERE {{ ?s ?p ?o }}",
        "file-from": "SELECT * FROM <file:///must-not-read.ttl> WHERE {?s ?p ?o}",
    }
    for name, query_text in queries.items():
        add(
            "offline/" + name,
            "offline",
            "offline",
            {"kind": "query", "dataText": text, "queryText": query_text},
            {"action": "query"},
            refs,
        )
    for name, format, value in (
        ("jsonld-context", "json-ld", '{"@context":"' + endpoint + '"}'),
        ("jsonld-import", "json-ld", '{"@context":{"@import":"' + endpoint + '"}}'),
        ("xml-entity", "xml", '<!DOCTYPE x [<!ENTITY e SYSTEM "' + endpoint + '">]><x>&e;</x>'),
        ("n3-formula", "n3", "{ <urn:s> <urn:p> <urn:o> } <urn:p> <urn:o> ."),
    ):
        add(
            "offline/" + name,
            "offline",
            "offline",
            ttl_dataset(value, format),
            {"action": "parse"},
            refs,
        )
    for role in ("data", "ontology", "shapes"):
        for name, iri in (("https", endpoint), ("file", "file:///must-not-read.ttl")):
            add(
                "offline/imports-" + role + "-" + name,
                "offline",
                "offline",
                ttl_dataset(
                    "<urn:ontology> <" + OWL + "imports> <" + iri + "> .", shapes=role == "shapes"
                ),
                {"action": "parse"},
                refs,
            )
    for name, predicate, value in (
        ("sparql", "sparql", ":Remote"),
        ("js", "js", ":Remote"),
        ("js-library", "jsLibrary", "<" + endpoint + ">"),
        ("rule", "rule", ":Remote"),
        ("target", "target", ":Remote"),
        ("validator", "validator", ":Remote"),
        ("function", "select", '"SELECT * {}"'),
        ("logical", "or", "(:Remote)"),
        ("inverse", "inversePath", ":name"),
    ):
        add(
            "offline/shacl-" + name,
            "offline",
            "offline",
            shape_dataset(text, shapes + f"\n:Remote sh:{predicate} {value} ."),
            {"action": "shape"},
            refs,
        )
    # The dispatcher must invoke the real installed rdflib JSON-LD boundary under
    # offline(), in addition to the public parse format gate above.
    path = "packages/engine/src/ontolearn_engine/semantic_probe.py"
    add(
        "offline/implicit-jsonld",
        "offline",
        "offline",
        ttl_dataset('{"@context":"' + endpoint + '"}', "json-ld"),
        {"action": "implicit-jsonld"},
        [source(path, "L66-L85 real JSON-LD implicit-access guard", C4)],
    )


def check_structure(payload):
    assert set(payload) == {"format", "datasets", "observations", "contexts"}
    assert payload["format"] == "i05-source-package-parity-inputs/1"
    assert len(OBS) <= 512
    assert len({item["id"] for item in OBS}) == len(OBS)
    kinds = {
        "turtle": {"kind", "text", "format", "shapes"},
        "query": {"kind", "dataText", "queryText"},
        "legacy": {"kind", "dataText", "rules"},
        "scope": {"kind", "assertedText", "ontologyText", "rules", "shapesText", "queryText"},
        "profile": {"kind", "input"},
        "records": {"kind", "records", "rules"},
        "shape": {"kind", "dataText", "shapesText"},
        "b1": {
            "kind",
            "assertedText",
            "ontologyText",
            "shapesText",
            "queryText",
            "rules",
            "replaceEquipmentTypes",
            "seed",
            "scale",
        },
    }
    operations = {
        "parse": {"turtle"},
        "query": {"query"},
        "legacy-reason": {"legacy"},
        "scope": {"scope"},
        "profile": {"profile"},
        "fullview": {"records", "profile", "turtle"},
        "dag": {"records", "turtle"},
        "restore-negative": {"records"},
        "shape": {"shape"},
        "shacl-text": {"shape"},
        "offline": {"query", "turtle", "shape"},
        "b1-measurement": {"b1"},
    }
    observation_keys = {
        "id",
        "sourceCaseId",
        "family",
        "operation",
        "datasetId",
        "parameters",
        "sourceRefs",
        "contextStatus",
        "projectionSha256",
    }
    for ds in DATASETS.values():
        assert type(ds) is dict and ds["kind"] in kinds and set(ds) == kinds[ds["kind"]]
        if ds["kind"] == "profile":
            assert set(ds["input"]) == {"asserted", "ontology", "definitions", "disabled_rule_ids"}
            for record in ds["input"]["asserted"] + ds["input"]["ontology"]:
                assert set(record) == {"triple", "source"}
                assert set(record["triple"]) == {"subject", "predicate", "object"}
            for definition in ds["input"]["definitions"]:
                assert not (
                    set(definition)
                    - {
                        "rule_id",
                        "enabled",
                        "when",
                        "comparisons",
                        "heads",
                        "revision",
                        "definitionJsonValueSha256",
                        "source",
                        "rawTurtle",
                        "rawTurtleSpan",
                    }
                )
        # This is a path-aware input whitelist; original definition.heads is legal.
        assert not (
            {
                "expected",
                "actual",
                "matches",
                "closure",
                "rdfsEvidence",
                "reasoning_result",
                "restorePremises",
                "projection",
                "rows_json",
                "payload_json",
            }
            & set(ds)
        )
    for item in OBS:
        assert set(item) == observation_keys
        ds = DATASETS[item["datasetId"]]
        assert ds["kind"] in operations[item["operation"]]
        assert item["projectionSha256"] == sha(canonical(ds))
        assert item["contextStatus"] in ("complete", "fragment", "not-executed")
        assert item["sourceRefs"]
        for ref in item["sourceRefs"]:
            assert set(ref) == {"ref", "path", "bytes", "sha256", "pointer"}
            fixed = SOURCES[(ref["ref"], ref["path"])]
            assert (ref["bytes"], ref["sha256"]) == (fixed["bytes"], fixed["sha256"])
    contexts = payload["contexts"]
    assert set(contexts) == {
        "mathInputContexts",
        "originalOperations",
        "productCases",
        "learningChecks",
        "unresolved",
        "nonClaims",
    }
    for name, count in (
        ("mathInputContexts", 83),
        ("originalOperations", 106),
        ("productCases", 50),
        ("learningChecks", 54),
        ("unresolved", 5),
    ):
        assert len(contexts[name]) == count, name
    assert sum(row["eligibleStandaloneMathInput"] for row in contexts["mathInputContexts"]) == 82
    assert sum(row["fullOriginalInputContext"] for row in contexts["mathInputContexts"]) == 79
    assert all(not row["originalOperationExecuted"] for row in contexts["originalOperations"])
    assert all(not row["checkExecuted"] for row in contexts["learningChecks"])
    assert len([row for row in OBS if row["family"] == "profile-83"]) == 83
    c_path = "docs/reviews/T05/profile-M1-math-explanation-input-contract/consumer-C-inputs.json"
    assert {row["id"] for row in json_source(c_path)["cases"]} <= {
        row["sourceCaseId"] for row in OBS
    }
    assert all(
        source_key in SOURCES
        for source_key in ((DOCS, "docs/iterations/I05/source-package-parity/contract.md"),)
    )


def emit_artifact(target, raw):
    if CHECK:
        assert target.read_bytes() == raw, "reproduction mismatch: " + str(target.relative_to(ROOT))
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)


def main():
    if sys.argv[1:] not in ([], ["--check"]):
        raise SystemExit("usage: generate-i05-source-package-inputs.py [--check]")
    raw_source("docs/iterations/I05/source-package-parity/contract.md", DOCS)
    contexts = build()
    payload = {
        "format": "i05-source-package-parity-inputs/1",
        "datasets": DATASETS,
        "observations": OBS,
        "contexts": contexts,
    }
    check_structure(payload)
    input_raw = canonical(payload) + b"\n"
    assert len(input_raw) <= 8_388_608, f"input asset cap: {len(input_raw)}"
    families = {}
    for row in OBS:
        families[row["family"]] = families.get(row["family"], 0) + 1
    counts = {
        "observations": len(OBS),
        "datasets": len(DATASETS),
        **{
            name: len(contexts[name])
            for name in (
                "mathInputContexts",
                "originalOperations",
                "productCases",
                "learningChecks",
                "unresolved",
            )
        },
        "families": families,
    }
    case_sets = {
        "full-v1": [row["id"] for row in OBS],
        "b1-semantic-1x-v1": ["b1-semantic/1x"],
        "b1-semantic-10x-v1": ["b1-semantic/10x"],
    }
    sources = sorted(SOURCES.values(), key=lambda row: (row["ref"], row["path"]))
    versions = {
        "supplierRef": SUPPLIER,
        "contractRef": DOCS,
        "b1InputMethodRef": C4,
        "generator": "input-only-stdlib/1",
        "datasetCanonicalization": "json-ascii-sorted-compact/1",
    }
    manifest = {
        "format": "i05-source-package-parity-manifest/1",
        "inputAsset": {"bytes": len(input_raw), "sha256": sha(input_raw)},
        "counts": counts,
        "caseSets": case_sets,
        "sources": sources,
        "versions": versions,
    }
    manifest_raw = canonical(manifest) + b"\n"
    assert len(manifest_raw) <= 1_048_576
    emit_artifact(ASSETS / INPUT_NAME, input_raw)
    emit_artifact(ASSETS / MANIFEST_NAME, manifest_raw)
    generator_raw = Path(__file__).read_bytes()
    source_manifest = {
        "format": "i05-source-package-input-sources/1",
        "versions": versions,
        "generator": {
            "path": str(Path(__file__).relative_to(ROOT)),
            "bytes": len(generator_raw),
            "sha256": sha(generator_raw),
        },
        "artifacts": [
            {"path": str((ASSETS / name).relative_to(ROOT)), "bytes": len(raw), "sha256": sha(raw)}
            for name, raw in ((INPUT_NAME, input_raw), (MANIFEST_NAME, manifest_raw))
        ],
        "counts": counts,
        "caseSets": case_sets,
        "sources": sources,
        "projectionRules": [
            (
                "Original profile asserted/ontology "
                "select triple+source only; definiti"
                "ons select only declared input fiel"
                "ds including legal heads."
            ),
            (
                "Original contexts preserve metadata"
                " only; raw operations/check expecta"
                "tions remain in fixed audit corpus "
                "and never enter runtime datasets."
            ),
            (
                "Other datasets are explicit literal"
                " input transforms or restricted AST"
                " literal extraction. No product/tes"
                "t import, eval, exec, closure, matc"
                "her, expected, golden or business o"
                "utput computation."
            ),
            (
                "Dataset SHA is ASCII JSON, sorted k"
                "eys, compact separators, allow_nan="
                "False; source SHA hashes exact orig"
                "inal bytes."
            ),
            (
                "83 contexts retained; transfer repa"
                "ir math profile is not-executed; fo"
                "ur E5 event folds remain fragments."
            ),
            (
                "Public work-budget and D1 inputs ar"
                "e original deterministic text expan"
                "sions; private cap/native fault sea"
                "ms are not serialized as runtime in"
                "puts."
            ),
        ],
    }
    emit_artifact(REVIEW / "inputs-source-manifest.json", canonical(source_manifest) + b"\n")
    lines = [
        "# I05 source/package pure-input generation",
        "",
        "仅完成纯输入准备与结构验证；未运行产品、测试、CLI、打包程序、语义库或业务算法，不能将本报告视为业务运行通过。",
        "",
        (
            "固定供应 `"
            f"{SUPPLIER}"
            "`；合同 `"
            f"{DOCS}"
            "`；B1 原输入方法 `"
            f"{C4}"
            "`。生成器仅依赖 Python 标准库，从固定 Git 字节读取原件，"
            "或做显式 AST literal／JSON 白名单提取和命名输入变换。"
        ),
        "",
        (
            "输入资产 "
            f"{len(input_raw)}"
            " bytes / SHA-256 `"
            f"{sha(input_raw)}"
            "`；manifest "
            f"{len(manifest_raw)}"
            " bytes / SHA-256 `"
            f"{sha(manifest_raw)}"
            "`。共 "
            f"{len(OBS)}"
            " observations、"
            f"{len(DATASETS)}"
            " 去重 datasets、"
            f"{len(sources)}"
            " 固定原件。硬上限 512／8MiB／1MiB 均在写出前检查；未按 "
            "cap 删除用例。"
        ),
        "",
        (
            "原83、106 operations、54 learning chec"
            "ks、50 product cases、5 unresolved 均保"
            "留。82 个 eligible、79 个 full，交集 78；tra"
            "nsfer:repair 的 profile 调用保留 not-exe"
            "cuted，并另用真实 SHACL 纯输入表达修复前后。四 E5 输入"
            "保留 fragment，不能升级为完整原项目／原操作通过。原106/5"
            "4均维持未执行状态，原操作全文与独立 expected 只在审计原件中"
            "。"
        ),
        "",
        (
            "C 的13个原 caseId全部引用；C date/illtyped "
            "以显式 policy 组合扩展，不能误称17个原case。运行时 da"
            "tasets 不装入 golden、expected、实际结果、推理闭"
            "包、已算 matches、basis、native carrier 或"
            "恢复前提；原规则定义 heads 属于合法输入并保留。"
        ),
        "",
        (
            "dataset digest 与资产采用 `json.dumps(en"
            "sure_ascii=True,sort_keys=True,sepa"
            "rators=(',',':'),allow_nan=False).e"
            "ncode('ascii')`，资产另加一个 LF；不配对 surro"
            "gate 保留为 decoded 输入值而不回显。raw 原件 byt"
            "es/SHA 另外固定，不能将新 JSON digest 冒作原 SH"
            "A。"
        ),
        "",
        "## 入口与来源",
        "",
        (
            "parse→turtle；query→query；legacy-rea"
            "son→legacy；scope→scope；profile→prof"
            "ile；fullview→records/profile/turtle"
            "；dag→records/turtle；restore-negativ"
            "e→records；shape/shacl-text→shape；of"
            "fline→query/turtle/shape；b1-measure"
            "ment→b1。每 observation 绑定 exact data"
            "set digest、固定 sourceRefs 和上下文状态，详细参"
            "数和全部有序 selector 在两份 JSON 中。"
        ),
        "",
        (
            "规则 structured terms 使用 kind/lexical"
            "_form/datatype_iri/language_raw/sou"
            "rce 五字段；SourceRecord 为 reference/di"
            "gest/revision/text 或 null。原83 sourc"
            "e 为原 path/ref/sha256/pointer，未重新计算 "
            "definition 摘要、匹配或业务值。rootsTargets 为"
            "三项 N3 key，restore mutation 只描述如何在真实"
            " producer/restore 边界扰动，不携带任何 payloa"
            "d/rows 摘要或预设输出。"
        ),
        "",
        (
            "scope 含 asserted/fresh/project 与七个选"
            "择失败/分区模式，须由真实 prepare→project 再交 qu"
            "ery/SHACL 消费。fullview/DAG 含四 finite"
            " 分支、depth2、同轮首 witness、原始 alias、双 h"
            "ead occurrence 和 text 拒绝。restore 变体"
            "覆盖末项 source/definition/limits/child"
            "、unknown key、depth/forward premise、"
            "统一 leaf rename、1023/15 occurrence。纯"
            " JSON 不模拟 native foreign／私有故障对象。"
        ),
        "",
        (
            "SHACL 含 C 全量、原 V01 与 transfer repai"
            "r 前后、有限模板和 shape 前门；整数 B 的 strict/W"
            "IDE、UTC bound/value 双侧正负、混合两侧、缺 tar"
            "get/value、legacy 隔离、D1 三顺序×两路径、原 pu"
            "blic exact/overcap 和 graph/text 前门。"
            "私有少一票、native 库兼容故障与 hook 费用正确性不能由输入"
            "资产执行，须由已授权产品测试或独立审查另验。"
        ),
        "",
        (
            "B1 两 selector 各只含一个 b1-measurement "
            "输入，固定 seed=20261019、scale1/10、18×sc"
            "ale fresh asserted input 与原四 ontolo"
            "gy text，明确 equipment type 替换输入；不导入 "
            "Store fixture/helper。十 ontology sui"
            "te 是另一个语义用例。full-v1 中两个 B1 observat"
            "ion 允许 instrumented/nonfresh，不能冒作独立"
            " fresh 测量证据；只有专用 selector 供后续无 hook"
            " fresh 进程。"
        ),
        "",
        (
            "offline 覆盖八类 SERVICE/FROM、格式拒绝、impo"
            "rts 三角色×两 scheme、九类非支持 SHACL 与真实 im"
            "plicit JSON-LD 边界；example.invalid/f"
            "ile 字符串均为拒绝输入，生成过程无网络或文件业务读取。"
        ),
        "",
        "## 结构与可复现检查",
        "",
        (
            "允许命令（cwd 为当前精确 worktree）：`python3 s"
            "cripts/generate-i05-source-package-"
            "inputs.py`；`python3 scripts/generat"
            "e-i05-source-package-inputs.py --ch"
            "eck`。后者只从相同固定 Git/原件重建并逐字节比对，不覆盖；未知"
            "参数拒绝。生成器内验证 exact root/kind/observa"
            "tion 字段、operation-kind 对应、源 bytes/S"
            "HA、dataset digest、原context数量及未执行标志、"
            "C13集合和全部 cap。"
        ),
        "",
        (
            "首轮准备命令 exit1：原 query 路径误带 queries/，"
            "在读取固定 Git 原件前即失败，未写出 runtime assets"
            "；已改为固定原件真实 product-baselines/unclos"
            "ed-high.rq 后重建。另两次只读定位命令确认 supplier"
            " 不包含旧 semantic_probe；implicit JSON-"
            "LD 方法改引用固定 C4 原件，未运行旧 probe。原失败工具输出"
            "保留，不当作业务失败或通过。"
        ),
        "",
        (
            "实际准备记录：修正路径后 generate exit0；补充六个 qu"
            "ery 前门与八个 bad-IRI policy 组合后 genera"
            "te exit0、--check exit0；另以标准库 ast.pa"
            "rse 完整检查生成器语法 exit0。最后固化说明后再次 gener"
            "ate/--check 仅核可复现字节。所有步骤 cwd 均为 I05"
            "-source-package-probe，未设置业务 env、未导入"
            "业务模块。stdout 是有限 metadata JSON，stder"
            "r 成功时为空；首次失败的 traceback 已保留在本会话原输出。"
        ),
        "",
        (
            "准备结果与原件清单见 inputs-source-manifest.j"
            "son；本报告列出的 source-path/JSON pointer"
            " 属于输入出处，不能补齐 unresolved 原上下文。后续主线必须"
            "执行真实 canonical dispatcher、完整报告与双端对比"
            "，并保持 B1 fresh 条件与原失败边界。"
        ),
        "",
        "## R1-03 delta：报告 EOF",
        "",
        (
            "R1 正式 Fail 原件保留于 review-r1.md／cf154"
            "39；固定旧候选 0e42a0fe349054a92817cb4d46"
            "3bccdc15f6c042 的首 EOF 失败为 `input-ge"
            "neration-report.md:497: new blank l"
            "ine at EOF.`，base→candidate diff ch"
            "eck 原 exit2 不改写。"
        ),
        "",
        (
            "本 delta 只将 generator 报告输出尾部规范为恰一个 L"
            "F（移除 join 后遗留的空白行），并重建本报告及 inputs-s"
            "ource-manifest 的 generator bytes/SH"
            "A。所有输入、dataset、观测、selector、两件 runti"
            "me JSON 字节均保持原值；未删用例，未改产品或测试，未执行产品／"
            "库／测试，未 stage／commit。"
        ),
        "",
        (
            "本 delta 实际执行 generator generate 和 -"
            "-check，均 exit0；另外以纯标准库比较两件 runtime "
            "JSON 的 before/after bytes 与原冻结 SHA、"
            "核报告末尾恰一个 LF。R1-01/02 由对应 writer 处理，"
            "不能用此 EOF 修复声称整体审查通过。"
        ),
        "",
        "## family counts",
        "",
    ]
    lines += [f"- `{family}`: {count}" for family, count in sorted(families.items())]
    lines += ["", "## 完整 selector 表", ""]
    for selector, identities in case_sets.items():
        lines += (
            ["### " + selector, ""]
            + [f"{index}. `{identity}`" for index, identity in enumerate(identities, 1)]
            + [""]
        )
    emit_artifact(
        REVIEW / "input-generation-report.md", ("\n".join(lines).rstrip("\n") + "\n").encode()
    )
    print(
        json.dumps(
            {
                "mode": "check" if CHECK else "generate",
                "inputAsset": manifest["inputAsset"],
                "manifestAsset": {"bytes": len(manifest_raw), "sha256": sha(manifest_raw)},
                "counts": counts,
                "sources": len(sources),
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
