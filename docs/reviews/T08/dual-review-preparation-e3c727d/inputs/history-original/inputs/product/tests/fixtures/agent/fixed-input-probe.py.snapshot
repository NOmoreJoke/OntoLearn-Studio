"""Offline, test-only RDFLib/CSV observation over approved fixed inputs.

No Store, T09 helper, product capability, model transport or expected-result preload.
Only the finite case identifiers below can be executed; this is not a query endpoint.
"""

import csv
import hashlib
import io
import json
import sys
from pathlib import Path

import rdflib
from pyparsing.exceptions import ParseBaseException
from rdflib import Graph, Literal, URIRef
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.util import from_n3

ROOT = Path(__file__).parent / "t09-873c8c0"
MANIFEST_HASH = "aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e"
SOURCE_COMMIT = "873c8c051b9870aa12fc7e1dbbd3e0c358e7c380"


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def packed(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def observe(case_id: str) -> dict:
    raw_manifest = (ROOT / "origin-manifest.json").read_bytes()
    if sha(raw_manifest) != MANIFEST_HASH:
        raise ValueError("baseline-integrity")
    manifest = json.loads(raw_manifest)
    inputs = {}
    for name in ("G-base.json", "unclosed-high.rq", "equipment.csv"):
        raw = (ROOT / name).read_bytes()
        if sha(raw) != manifest["files"][f"tests/fixtures/product-baselines/{name}"]:
            raise ValueError("baseline-integrity")
        inputs[name] = raw
    source = {
        "probeVersion": "t08-fixed-rdflib-csv-1",
        "sourceCommit": SOURCE_COMMIT,
        "manifestSha256": MANIFEST_HASH,
        "fixtureSha256": sha(inputs["G-base.json"]),
        "rdflibVersion": rdflib.__version__,
        "caseId": case_id,
    }
    if case_id == "CSV-original":
        reader = csv.DictReader(io.StringIO(inputs["equipment.csv"].decode("utf-8")))
        return {
            **source,
            "kind": "csv",
            "sourceSha256": sha(inputs["equipment.csv"]),
            "columns": reader.fieldnames,
            "rows": [{"sourceLine": index, **row} for index, row in enumerate(reader, 2)],
        }
    if case_id not in {"Q-01", "Q-02", "Q-01-semantic-wrong", "Q-01-syntax-wrong"}:
        raise ValueError("case-not-allowed")
    graph = Graph()
    for fact in json.loads(inputs["G-base.json"])["facts"]:
        graph.add((URIRef(fact["subject"]), URIRef(fact["predicate"]), from_n3(fact["object"])))
    if case_id == "Q-02":
        alarm = URIRef("urn:ontolearn:learning:alarm/A01")
        predicate = URIRef("urn:ontolearn:learning:status")
        graph.remove((alarm, predicate, Literal("Open")))
        graph.add((alarm, predicate, Literal("Closed")))
    actual_input = sorted(
        [[subject.n3(), predicate.n3(), obj.n3()] for subject, predicate, obj in graph]
    )
    query = inputs["unclosed-high.rq"].decode("utf-8")
    if case_id == "Q-01-semantic-wrong":
        query = query.replace('"Open"', '"Closed"')
    elif case_id == "Q-01-syntax-wrong":
        query = "SELECT ?alarm WHERE {"
    identity = {
        **source,
        "kind": "query",
        "inputSha256": sha(packed(actual_input)),
        "querySha256": sha(query.encode()),
        "query": query,
        "scope": "current-asserted",
    }
    try:
        parseQuery(query)
    except ParseBaseException:
        return {**identity, "ok": False, "code": "QUERY_SYNTAX"}
    try:
        result = graph.query(query)
        variables = [str(variable) for variable in result.vars]
        rows = [{name: row[index].n3() for index, name in enumerate(variables)} for row in result]
    except Exception:
        return {**identity, "ok": False, "code": "QUERY_EXECUTION_FAILED"}
    return {**identity, "ok": True, "variables": variables, "rows": rows}


if __name__ == "__main__":
    try:
        print(json.dumps(observe(sys.argv[1]), ensure_ascii=False))
    except (IndexError, ValueError):
        print(json.dumps({"ok": False, "code": "BASELINE_OR_CASE_INVALID"}))
        sys.exit(1)
