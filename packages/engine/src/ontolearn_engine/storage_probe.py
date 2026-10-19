"""Real RDFLib S1 fixed workload; no user query or remote parser inputs.

JSON output is raw observation, not a business capacity pass/fail threshold.
One fresh process per scale/trial measures load, build and fixed query phases.
"""

import hashlib
import json
import platform
import resource
import sqlite3
import time
import tracemalloc
from importlib.metadata import version
from tempfile import TemporaryDirectory

from rdflib import Graph

from ontolearn_engine.rdf_snapshot import graph_from_snapshot
from ontolearn_engine.storage import Store, digest

SEED = 20261019
QUERY = """PREFIX : <urn:ontolearn:>
SELECT ?alarm WHERE { ?alarm :level "High"; :status "Open" } ORDER BY ?alarm"""


def fixture(scale: int) -> str:
    """Each copy uses independent IDs, same six objects/structure as G-base facts."""
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


def measure(scale: int = 1, trial: int = 0) -> dict:
    with TemporaryDirectory() as directory:
        store = Store(f"{directory}/probe.db")
        store.create_project("synthetic")
        ttl = fixture(scale)
        generated = Graph().parse(data=ttl, format="turtle")
        facts = [
            {
                "id": digest([str(s), str(p), o.n3()]),
                "subject": str(s),
                "predicate": str(p),
                "object": o.n3(),
            }
            for s, p, o in generated
        ]
        store.commit(
            "synthetic",
            0,
            "fixture",
            "fixture-job",
            manual=facts,
        )
        identity = store.snapshot("synthetic")
        store.close()
        store = Store(f"{directory}/probe.db")
        measurements = {}
        tracemalloc.start()

        def phase(name, action):
            tracemalloc.reset_peak()
            before = tracemalloc.get_traced_memory()[0]
            start = time.perf_counter_ns()
            result = action()
            elapsed = time.perf_counter_ns() - start
            current, peak = tracemalloc.get_traced_memory()
            measurements[name] = {
                "elapsedNs": elapsed,
                "pythonBytesBefore": before,
                "pythonBytesAfter": current,
                "pythonBytesPeak": peak,
                "processHighWaterRssBytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                * (1 if platform.system() == "Darwin" else 1024),
            }
            return result

        snapshot = phase("snapshotLoad", lambda: store.load_snapshot(identity))
        graph = phase("rdflibBuild", lambda: graph_from_snapshot(snapshot))
        results = phase("fixedSelect", lambda: [str(r.alarm) for r in graph.query(QUERY)])
        expected = sorted(f"urn:case:{i}:alarm/A01" for i in range(scale))
        assert results == expected
        assert len(graph) == 18 * scale
        phase("snapshotLoadWarm", lambda: store.load_snapshot(identity))
        warm_graph = phase("rdflibBuildWarm", lambda: graph_from_snapshot(snapshot))
        warm_results = phase(
            "fixedSelectWarm", lambda: [str(r.alarm) for r in warm_graph.query(QUERY)]
        )
        assert warm_results == expected
        store.close()
        tracemalloc.stop()
        return {
            "scale": scale,
            "trial": trial,
            "seed": SEED,
            "triples": len(graph),
            "inputSha256": hashlib.sha256(ttl.encode()).hexdigest(),
            "querySha256": hashlib.sha256(QUERY.encode()).hexdigest(),
            "result": results,
            "expected": expected,
            "snapshotId": identity,
            "measurement": measurements,
            "device": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
            "rdflib": version("rdflib"),
            "condition": "store reopened; OS cache uncontrolled; Warm phases repeat in process",
            "method": "perf_counter_ns; tracemalloc phase peaks; process lifetime ru_maxrss",
        }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", type=int, default=1)
    parser.add_argument("--trial", type=int, default=0)
    args = parser.parse_args()
    if not 1 <= args.scale <= 1000:
        parser.error("synthetic scale must be 1..1000")
    print(json.dumps(measure(args.scale, args.trial), ensure_ascii=False))


if __name__ == "__main__":
    main()
