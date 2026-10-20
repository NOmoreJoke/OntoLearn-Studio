"""I05 CLI-only probe, deliberately absent from product health capabilities."""

import argparse
import hashlib
import json
import platform
import sys
import time
import tracemalloc
from importlib.metadata import version

# Install before importing the semantic guard, so denied audit events are counted.
_observing = False
_attempts = []


def _observe(event, args):
    if _observing and (event.startswith("socket.") or event == "urllib.Request"):
        _attempts.append(event)  # Never record URL, path, payload, or request headers.


sys.addaudithook(_observe)

from rdflib import RDF, RDFS, Graph, URIRef  # noqa: E402

from ontolearn_engine.semantic import check_shapes, parse_turtle, query, reason  # noqa: E402
from ontolearn_engine.semantic_offline import SemanticError, offline  # noqa: E402
from ontolearn_engine.semantic_samples import (  # noqa: E402
    EX,
    QUERY,
    RISK,
    SEED,
    SHAPES,
    execute_case,
    fixture,
    rejection_cases,
    suite,
)
from ontolearn_engine.storage_probe import high_water_rss, measure  # noqa: E402


def rejection_matrix(endpoint):
    global _observing
    observations = []
    for name, expected, request in rejection_cases(endpoint):
        _attempts.clear()
        _observing = True
        try:
            execute_case(request)
        except SemanticError as error:
            actual = error.code
        else:
            actual = "UNEXPECTED_ACCEPT"
        finally:
            _observing = False
        assert actual == expected, (name, actual, expected)
        assert not _attempts, (name, _attempts)
        observations.append(
            {
                "name": name,
                "expected": expected,
                "actual": actual,
                "networkAuditEvents": list(_attempts),
            }
        )
    # Deliberately bypass product format gate to exercise a real library's implicit
    # JSON-LD fetch under the same execution guard. This is test-only input.
    _attempts.clear()
    _observing = True
    try:
        with offline():
            Graph().parse(data=json.dumps({"@context": endpoint}), format="json-ld")
    except SemanticError as error:
        assert error.code == "EXTERNAL_ACCESS_DENIED"
    else:
        raise AssertionError("real JSON-LD implicit I/O backstop was not reached")
    finally:
        _observing = False
    assert _attempts == ["urllib.Request"]
    observations.append(
        {
            "name": "library-jsonld-backstop",
            "actual": "EXTERNAL_ACCESS_DENIED",
            "networkAuditEvents": list(_attempts),
        }
    )
    return observations


def measurement(scale, trial):
    # Original S1 load/build/query metric, identity, input and query hashes retained.
    s1 = measure(scale, trial)
    phases = {}
    tracemalloc.start()

    def phase(name, action):
        tracemalloc.reset_peak()
        before = tracemalloc.get_traced_memory()[0]
        start = time.perf_counter_ns()
        result = action()
        current, peak = tracemalloc.get_traced_memory()
        phases[name] = {
            "elapsedNs": time.perf_counter_ns() - start,
            "pythonBytesBefore": before,
            "pythonBytesAfter": current,
            "pythonBytesPeak": peak,
            "processHighWaterRssBytes": high_water_rss(),
        }
        return result

    text = fixture(scale)
    ontology = Graph()
    for triple in (
        (EX.CriticalPump, RDFS.subClassOf, EX.Pump),
        (EX.Pump, RDFS.subClassOf, EX.Equipment),
        (EX.alarm, RDFS.domain, EX.MonitoredEquipment),
        (EX.alarm, RDFS.range, EX.Event),
    ):
        ontology.add(triple)

    def semantic_graph():
        data = parse_turtle(text)
        for i in range(scale):
            data.set((URIRef(f"urn:case:{i}:equipment/001"), RDF.type, EX.CriticalPump))
        for triple in ontology:
            data.add(triple)
        return data

    shapes = parse_turtle(SHAPES, shapes=True)
    expected = [[f"<urn:case:{i}:alarm/A01>"] for i in range(scale)]
    expected.sort()
    observed = {}
    for suffix in ("FirstAfterS1", "Warm"):
        graph = phase("turtleParseAndOntologyBuild" + suffix, semantic_graph)
        selected = phase("select" + suffix, lambda graph=graph: query(graph, QUERY))
        inferred = phase("rdfsRules" + suffix, lambda graph=graph: reason(graph, (RISK,)))
        asserted_scope = parse_turtle(text)
        validated = phase(
            "shacl" + suffix,
            lambda asserted_scope=asserted_scope: check_shapes(asserted_scope, shapes),
        )
        assert selected["rows"] == expected
        assert inferred["rules"] == sorted(
            (
                f"<urn:case:{i}:equipment/001>",
                "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>",
                "<urn:ontolearn:HighRiskEquipment>",
            )
            for i in range(scale)
        )
        expected_rdfs = [(EX.CriticalPump.n3(), RDFS.subClassOf.n3(), EX.Equipment.n3())]
        for i in range(scale):
            for identifier, cls in (
                ("equipment/001", EX.Pump),
                ("equipment/001", EX.Equipment),
                *((f"equipment/{j}", EX.MonitoredEquipment) for j in ("001", "002", "003")),
                *((f"alarm/{j}", EX.Event) for j in ("A01", "A02", "A03")),
            ):
                expected_rdfs.append((f"<urn:case:{i}:{identifier}>", RDF.type.n3(), cls.n3()))
        assert inferred["rdfs"] == sorted(expected_rdfs)
        assert validated == {"conforms": True, "violations": []}
        observed[suffix] = {"select": selected, "reason": inferred, "shacl": validated}
    tracemalloc.stop()
    assert observed["FirstAfterS1"] == observed["Warm"]
    return {
        "s1": s1,
        "semanticPhases": phases,
        "seed": SEED,
        "assertedTriples": 18 * scale,
        "shapeTriples": len(shapes),
        "ontologyTriples": len(ontology),
        "semanticInputTriples": 18 * scale + len(ontology),
        "semanticInputSha256": hashlib.sha256(
            "\n".join(sorted(" ".join(t.n3() for t in row) for row in semantic_graph())).encode()
        ).hexdigest(),
        "result": observed["FirstAfterS1"],
        "shapesSha256": hashlib.sha256(SHAPES.encode()).hexdigest(),
        "python": platform.python_version(),
        "machine": platform.machine(),
        "versions": {
            name: version(name)
            for name in (
                "rdflib",
                "pyshacl",
                "owlrl",
                "html5rdf",
                "pyparsing",
                "packaging",
                "prettytable",
                "wcwidth",
            )
        },
        "method": "S1 same seed/namespace/input/query; perf_counter_ns/tracemalloc; "
        "lifetime RSS, not phase RSS; FirstAfterS1=first candidate call after original S1 "
        "load/build/query warm-up, not a library-cold call; "
        "whole child wall time includes imports; "
        "OS cache uncontrolled; no capacity threshold",
    }


def fresh_measurements(scale, trial):
    """Yield the first complete real workload before executing the warm workload.

    This path never calls S1 measure(), suite(), or parses shapes beforehand.
    The parent records arrival of the first JSONL result independently of exit.
    """
    tracemalloc.start()
    try:
        reference = None
        for suffix in ("First", "Warm"):
            workload_start = time.perf_counter_ns()
            phases = {}

            def phase(name, action, measurements=phases):
                tracemalloc.reset_peak()
                before = tracemalloc.get_traced_memory()[0]
                start = time.perf_counter_ns()
                result = action()
                current, peak = tracemalloc.get_traced_memory()
                measurements[name] = {
                    "elapsedNs": time.perf_counter_ns() - start,
                    "pythonBytesBefore": before,
                    "pythonBytesAfter": current,
                    "pythonBytesPeak": peak,
                    "processHighWaterRssBytes": high_water_rss(),
                }
                return result

            text = fixture(scale)
            graph = phase("turtleParse", lambda text=text: parse_turtle(text))
            asserted_scope = Graph()
            for triple in graph:
                asserted_scope.add(triple)
            ontology = phase(
                "ontologyParse",
                lambda: parse_turtle("""
                @prefix : <urn:ontolearn:> .
                @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
                :CriticalPump rdfs:subClassOf :Pump . :Pump rdfs:subClassOf :Equipment .
                :alarm rdfs:domain :MonitoredEquipment; rdfs:range :Event .
            """),
            )

            def build(data=graph, schema=ontology):
                for i in range(scale):
                    data.set((URIRef(f"urn:case:{i}:equipment/001"), RDF.type, EX.CriticalPump))
                for triple in schema:
                    data.add(triple)
                return data

            graph = phase("graphBuild", build)
            selected = phase("select", lambda graph=graph: query(graph, QUERY))
            inferred = phase("rdfsRules", lambda graph=graph: reason(graph, (RISK,)))
            shapes = phase("shapesParse", lambda: parse_turtle(SHAPES, shapes=True))
            validated = phase(
                "shacl",
                lambda asserted_scope=asserted_scope, shapes=shapes: check_shapes(
                    asserted_scope, shapes
                ),
            )
            expected_select = sorted([[f"<urn:case:{i}:alarm/A01>"] for i in range(scale)])
            expected_rules = sorted(
                (f"<urn:case:{i}:equipment/001>", RDF.type.n3(), EX.HighRiskEquipment.n3())
                for i in range(scale)
            )
            expected_rdfs = [(EX.CriticalPump.n3(), RDFS.subClassOf.n3(), EX.Equipment.n3())]
            for i in range(scale):
                for identifier, cls in (
                    ("equipment/001", EX.Pump),
                    ("equipment/001", EX.Equipment),
                    *((f"equipment/{j}", EX.MonitoredEquipment) for j in ("001", "002", "003")),
                    *((f"alarm/{j}", EX.Event) for j in ("A01", "A02", "A03")),
                ):
                    expected_rdfs.append((f"<urn:case:{i}:{identifier}>", RDF.type.n3(), cls.n3()))
            assert selected == {"type": "SELECT", "variables": ["alarm"], "rows": expected_select}
            assert inferred["rules"] == expected_rules
            assert inferred["rdfs"] == sorted(expected_rdfs)
            assert validated == {"conforms": True, "violations": []}
            result = {"select": selected, "reason": inferred, "shacl": validated}
            if reference is None:
                reference = result
            else:
                assert reference == result
            observation = {
                "profile": "fresh-process-first-candidate-then-warm",
                "stage": suffix,
                "scale": scale,
                "trial": trial,
                "seed": SEED,
                "assertedTriples": 18 * scale,
                "ontologyTriples": len(ontology),
                "semanticInputTriples": len(graph),
                "shapeTriples": len(shapes),
                "inputSha256": hashlib.sha256(text.encode()).hexdigest(),
                "querySha256": hashlib.sha256(QUERY.encode()).hexdigest(),
                "shapesSha256": hashlib.sha256(SHAPES.encode()).hexdigest(),
                "semanticInputSha256": hashlib.sha256(
                    "\n".join(sorted(" ".join(t.n3() for t in row) for row in graph)).encode()
                ).hexdigest(),
                "phases": phases,
                "result": result,
                "python": platform.python_version(),
                "versions": {name: version(name) for name in ("rdflib", "pyshacl", "owlrl")},
                "device": platform.platform(),
                "machine": platform.machine(),
                "condition": "fresh CLI path before First has no S1 measure/suite/shapes parse; "
                "imports precede workload; Warm repeats in process; OS cache uncontrolled",
                "method": "perf_counter_ns phases and workload; tracemalloc; lifetime ru_maxrss; "
                "parent separately timestamps First JSONL arrival before waiting for exit",
            }
            observation["workloadElapsedNs"] = time.perf_counter_ns() - workload_start
            yield {
                "event": "firstComplete" if suffix == "First" else "warmComplete",
                "observation": observation,
            }
    finally:
        tracemalloc.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", choices=["suite", "reject", "measure", "startup", "fresh"], default="suite"
    )
    parser.add_argument("--endpoint", default="http://127.0.0.1:9/deny")
    parser.add_argument("--scale", type=int, choices=[1, 10], default=1)
    parser.add_argument("--trial", type=int, default=0)
    args = parser.parse_args()
    if args.mode == "fresh":
        for event in fresh_measurements(args.scale, args.trial):
            print(json.dumps(event, ensure_ascii=False, sort_keys=True), flush=True)
        return
    if args.mode == "startup":
        result = {
            "ready": True,
            "rssBytes": high_water_rss(),
            "scope": "CLI candidate modules imported; no semantic work executed",
        }
    elif args.mode == "suite":
        result = suite()
    elif args.mode == "reject":
        result = rejection_matrix(args.endpoint)
    else:
        result = measurement(args.scale, args.trial)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
