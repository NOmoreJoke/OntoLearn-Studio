"""Fresh workload is real, first result precedes warm execution, legacy prewarm absent."""

import pytest
from ontolearn_engine import semantic_probe


@pytest.mark.parametrize("scale", [1, 10])
def test_fresh_first_result_then_identical_warm_without_s1_or_suite(scale, monkeypatch):
    def forbidden():
        raise AssertionError("S1 or suite must not run before the fresh workload")

    monkeypatch.setattr(semantic_probe, "measure", forbidden)
    monkeypatch.setattr(semantic_probe, "suite", forbidden)
    generator = semantic_probe.fresh_measurements(scale, 0)
    try:
        first = next(generator)
        assert first["event"] == "firstComplete"
        observation = first["observation"]
        assert observation["stage"] == "First"
        assert set(observation["phases"]) == {
            "turtleParse",
            "ontologyParse",
            "graphBuild",
            "select",
            "rdfsRules",
            "shapesParse",
            "shacl",
        }
        assert observation["result"]["select"]["rows"] == sorted(
            [[f"<urn:case:{i}:alarm/A01>"] for i in range(scale)]
        )
        assert observation["workloadElapsedNs"] >= sum(
            stage["elapsedNs"] for stage in observation["phases"].values()
        )
        warm = next(generator)
        assert warm["event"] == "warmComplete"
        assert warm["observation"]["stage"] == "Warm"
        for field in (
            "result",
            "inputSha256",
            "querySha256",
            "semanticInputSha256",
            "shapesSha256",
        ):
            assert warm["observation"][field] == observation[field]
        with pytest.raises(StopIteration):
            next(generator)
    finally:
        generator.close()
