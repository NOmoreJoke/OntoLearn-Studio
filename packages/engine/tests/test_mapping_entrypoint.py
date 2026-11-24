"""The product entrypoint exposes a bounded synthetic probe, never user paths."""

import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest
from ontolearn_engine.mapping import probe

ENTRY = Path(__file__).resolve().parents[1] / "entrypoint.py"
EXPECTED_FACTS = {
    ("urn:example:equipment/001", "urn:example:name", '"泵站A"'),
    ("urn:example:equipment/002", "urn:example:name", '"泵站B"'),
    (
        "urn:example:equipment/001",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
        "<urn:example:Equipment>",
    ),
    (
        "urn:example:equipment/002",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
        "<urn:example:Equipment>",
    ),
}
EXPECTED_CASES = {
    "csv-exact-set": "passed",
    "xlsx-exact-set": "passed",
    "sheet-selection": "passed",
    "cached-formula": "passed",
    "cached-empty-string": "passed",
    "sparse-cell": "passed",
    "missing-formula-cache": "FORMULA_CACHE_MISSING",
    "macro-refusal": "MACRO_UNSUPPORTED",
    "invalid-encoding": "INVALID_ENCODING",
    "source-limit": "SOURCE_LIMIT",
    "duplicate-key": "DUPLICATE_KEY",
}


@pytest.mark.parametrize("optimization", [[], ["-O"]])
def test_actual_entrypoint_runs_exact_fixed_real_parser_cases(optimization):
    result = subprocess.run(
        [sys.executable, *optimization, str(ENTRY), "--mapping-probe"],
        capture_output=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    assert result.stderr == b""
    output = json.loads(result.stdout)
    assert set(map(tuple, output["exactFacts"])) == EXPECTED_FACTS
    assert output["cases"] == EXPECTED_CASES
    assert output["versions"] == {"openpyxl": "3.1.5", "et-xmlfile": "2.0.0", "defusedxml": "0.7.1"}
    assert output["registeredBusinessCapability"] is False


@pytest.mark.parametrize("extra", ["/untrusted/input.xlsx", "--script", "https://example.invalid/"])
def test_probe_rejects_any_extra_argument_without_echoing_or_running_it(extra):
    result = subprocess.run(
        [sys.executable, str(ENTRY), "--mapping-probe", extra],
        capture_output=True,
        timeout=5,
        check=False,
    )
    assert result.returncode == 2
    assert result.stdout == b""
    assert result.stderr.replace(b"\r\n", b"\n") == b"MAPPING_PROBE_INVALID_ARGUMENTS\n"


def test_probe_runtime_error_is_fixed_and_does_not_leak_raw_exception(monkeypatch, capsys):
    def failure():
        raise ValueError("untrusted synthetic raw cell or local path")

    monkeypatch.setattr(probe, "main", failure)
    monkeypatch.setattr(sys, "argv", [str(ENTRY), "--mapping-probe"])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(ENTRY), run_name="__main__")
    assert error.value.code == 1
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == "MAPPING_PROBE_FAILED\n"
