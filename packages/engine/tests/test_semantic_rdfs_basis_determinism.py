"""One stable valid RDFS witness, not all paths or a shortest-proof promise.

The oracle follows the declared (output, ordered direct inputs) full-key tie
break. Six fresh processes execute every scenario and input-order variation
once per module; no engine implementation is patched or copied into the test.
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from ontolearn_engine import semantic

TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
SUBCLASS = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
DOMAIN = "http://www.w3.org/2000/01/rdf-schema#domain"
RANGE = "http://www.w3.org/2000/01/rdf-schema#range"
U_TYPE_C = ("urn:u", TYPE, "urn:C")
U_TYPE_A = ("urn:u", TYPE, "urn:A")
U_P_A = ("urn:u", "urn:p", "urn:a")
U_P_B = ("urn:u", "urn:p", "urn:b")
P_DOMAIN_C = ("urn:p", DOMAIN, "urn:C")
P_DOMAIN_A = ("urn:p", DOMAIN, "urn:A")
P_RANGE_C = ("urn:p", RANGE, "urn:C")
A_P_U = ("urn:a", "urn:p", "urn:u")
B_P_U = ("urn:b", "urn:p", "urn:u")
A_SUB_B = ("urn:A", SUBCLASS, "urn:B")
A_SUB_C = ("urn:A", SUBCLASS, "urn:C")
A_SUB_D = ("urn:A", SUBCLASS, "urn:D")
B_SUB_C = ("urn:B", SUBCLASS, "urn:C")
D_SUB_C = ("urn:D", SUBCLASS, "urn:C")
U_TYPE_B = ("urn:u", TYPE, "urn:B")
U_TYPE_D = ("urn:u", TYPE, "urn:D")
OBSERVED = ("urn:u", "urn:observed", "urn:seen")


def n3(triple):
    return [f"<{term}>" for term in triple]


def basis(*triples):
    return sorted(n3(t) for t in set(triples))


def evidence(rule, result, inputs, proof):
    return {"rule": rule, "result": n3(result), "inputs": [n3(t) for t in inputs], "basis": proof}


def oracle(proofs, records):
    return {
        "rdfs": sorted(n3(t) for t in proofs),
        "rules": sorted({tuple(record["result"]) for record in records}),
        "warnings": [],
        "rdfsEvidence": [
            {"result": n3(result), "basis": proofs[result]} for result in sorted(proofs, key=n3)
        ],
        "evidence": records,
    }


def rule(identity="observe", when=None, then=None):
    return {
        "id": identity,
        "when": when or [("?u", TYPE, "urn:C")],
        "then": then or ("?u", "urn:observed", "urn:seen"),
    }


def observed(proof):
    return [evidence("observe", OBSERVED, [U_TYPE_C], proof)]


DOMAIN_PROOF = basis(P_DOMAIN_C, U_P_A)
RANGE_PROOF = basis(P_RANGE_C, A_P_U)
DIAMOND_C_PROOF = basis(A_SUB_B, B_SUB_C, U_TYPE_A)
MULTIHOP_C_PROOF = basis(A_SUB_B, B_SUB_C, P_DOMAIN_A, U_P_A)

SCENARIOS = {
    "domain-alternative-facts": {
        "triples": [U_P_A, U_P_B, P_DOMAIN_C],
        "rules": [rule()],
        "expected": oracle({U_TYPE_C: DOMAIN_PROOF}, observed(DOMAIN_PROOF)),
    },
    "range-alternative-facts": {
        "triples": [A_P_U, B_P_U, P_RANGE_C],
        "rules": [rule()],
        "expected": oracle({U_TYPE_C: RANGE_PROOF}, observed(RANGE_PROOF)),
    },
    "domain-range-same-output": {
        "triples": [U_P_A, P_DOMAIN_C, ("urn:b", "urn:q", "urn:u"), ("urn:q", RANGE, "urn:C")],
        "rules": [rule()],
        "expected": oracle({U_TYPE_C: DOMAIN_PROOF}, observed(DOMAIN_PROOF)),
    },
    "subclass-domain-direct-input-tie": {
        "triples": [U_TYPE_A, A_SUB_C, U_P_A, P_DOMAIN_C],
        "rules": [rule()],
        # Domain's ordered direct inputs begin with urn:p, before the
        # subclass route's urn:u. Sorting normalized basis instead would pick
        # urn:A's axiom and incorrectly change this declared witness policy.
        "expected": oracle({U_TYPE_C: DOMAIN_PROOF}, observed(DOMAIN_PROOF)),
    },
    "diamond-multiple-valid-paths": {
        "triples": [U_TYPE_A, A_SUB_B, A_SUB_D, B_SUB_C, D_SUB_C],
        "rules": [rule()],
        "expected": oracle(
            {
                A_SUB_C: basis(A_SUB_B, B_SUB_C),
                U_TYPE_B: basis(A_SUB_B, U_TYPE_A),
                U_TYPE_C: DIAMOND_C_PROOF,
                U_TYPE_D: basis(A_SUB_D, U_TYPE_A),
            },
            observed(DIAMOND_C_PROOF),
        ),
    },
    "domain-then-multihop-subclass": {
        "triples": [U_P_A, U_P_B, P_DOMAIN_A, A_SUB_B, B_SUB_C],
        "rules": [rule()],
        "expected": oracle(
            {
                A_SUB_C: basis(A_SUB_B, B_SUB_C),
                U_TYPE_A: basis(P_DOMAIN_A, U_P_A),
                U_TYPE_B: basis(A_SUB_B, P_DOMAIN_A, U_P_A),
                U_TYPE_C: MULTIHOP_C_PROOF,
            },
            observed(MULTIHOP_C_PROOF),
        ),
    },
    "rule-distinct-matches-retain-both-evidence-records": {
        "triples": [U_P_A, U_P_B, P_DOMAIN_C],
        "rules": [rule(when=[("?u", TYPE, "urn:C"), ("?u", "urn:p", "?value")])],
        "expected": oracle(
            {U_TYPE_C: DOMAIN_PROOF},
            [
                evidence("observe", OBSERVED, [U_TYPE_C, U_P_A], DOMAIN_PROOF),
                evidence("observe", OBSERVED, [U_TYPE_C, U_P_B], basis(P_DOMAIN_C, U_P_A, U_P_B)),
            ],
        ),
    },
    "asserted-result-keeps-asserted-proof": {
        "triples": [U_P_A, U_P_B, P_DOMAIN_C, U_TYPE_C],
        "rules": [rule()],
        "expected": oracle({}, observed(basis(U_TYPE_C))),
    },
    "rules-use-frozen-closure-and-do-not-reenter-rdfs": {
        "triples": [U_P_A, U_P_B, P_DOMAIN_C, ("urn:D", SUBCLASS, "urn:E")],
        "rules": [
            rule("01-produce", then=("?u", TYPE, "urn:D")),
            rule("02-consume", when=[("?u", TYPE, "urn:D")]),
        ],
        "expected": {
            **oracle(
                {U_TYPE_C: DOMAIN_PROOF},
                [evidence("01-produce", U_TYPE_D, [U_TYPE_C], DOMAIN_PROOF)],
            ),
            "warnings": ["RULE_CHAIN_UNSUPPORTED:02-consume"],
        },
    },
}
# JSON is also the actual subprocess wire format: expected tuples become lists.
SCENARIOS = json.loads(json.dumps(SCENARIOS, sort_keys=True))
SEEDS = (1, 2, 3, 5, 7, 11)

CHILD = r"""
import hashlib,json,os,sys
from pathlib import Path
from ontolearn_engine import semantic
from rdflib import Graph,URIRef,Variable
raw=sys.stdin.buffer.read()
scenarios=json.loads(raw)
outputs={}
for name,scenario in scenarios.items():
    outputs[name]={}
    for noise in (False,True):
        triples=scenario['triples']+([['urn:z','urn:unrelated-predicate','urn:w']] if noise else [])
        orders={'forward':triples,'reverse':list(reversed(triples)),
                'rotated':triples[1:]+triples[:1]}
        for order,items in orders.items():
            graph=Graph()
            for triple in items:
                graph.add(tuple(URIRef(t) for t in triple))
            original=set(graph)
            def term(text):
                return Variable(text[1:]) if text.startswith('?') else URIRef(text)
            rules=tuple(semantic.Rule(r['id'],tuple(tuple(term(t) for t in p)
                for p in r['when']),tuple(term(t) for t in r['then']))
                for r in scenario['rules'])
            outputs[name][str(noise)+':'+order]=semantic.reason(graph,rules)
            assert set(graph)==original
source=Path(semantic.__file__).resolve()
print(json.dumps({'seed':os.environ['PYTHONHASHSEED'],
    'source':str(source),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'inputSha256':hashlib.sha256(raw).hexdigest(),'semanticsVersion':semantic.SEMANTICS_VERSION,
    'ignoreEnvironment':sys.flags.ignore_environment,'outputs':outputs},sort_keys=True))
"""


@pytest.fixture(scope="module")
def seeded_outputs():
    inputs = json.dumps(
        {
            name: {k: v for k, v in case.items() if k != "expected"}
            for name, case in SCENARIOS.items()
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    source = Path(semantic.__file__).resolve()
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    runs = []
    for seed in SEEDS:
        environment = os.environ | {"PYTHONHASHSEED": str(seed), "PYTHONDONTWRITEBYTECODE": "1"}
        # -I/-E would ignore PYTHONHASHSEED and invalidate this regression.
        process = subprocess.run(
            [sys.executable, "-B", "-c", CHILD],
            input=inputs,
            env=environment,
            capture_output=True,
            timeout=30,
        )
        assert process.returncode == 0, process.stderr.decode(errors="replace")
        assert process.stderr == b""
        record = json.loads(process.stdout)
        assert record["seed"] == str(seed) and record["ignoreEnvironment"] == 0
        assert record["source"] == str(source) and record["sourceSha256"] == source_hash
        assert record["inputSha256"] == hashlib.sha256(inputs).hexdigest()
        assert record["semanticsVersion"] == semantic.SEMANTICS_VERSION
        runs.append(record)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    return runs


@pytest.mark.parametrize("name", SCENARIOS)
def test_complete_rdfs_and_rule_output_uses_one_deterministic_direct_input_witness(
    name, seeded_outputs
):
    expected = SCENARIOS[name]["expected"]
    for run in seeded_outputs:
        for order, actual in run["outputs"][name].items():
            assert actual == expected, (name, run["seed"], order)


def test_complete_outputs_are_equal_across_seeds_noise_and_insertion_order(seeded_outputs):
    for name in SCENARIOS:
        actual = [output for run in seeded_outputs for output in run["outputs"][name].values()]
        assert all(output == actual[0] for output in actual), name
