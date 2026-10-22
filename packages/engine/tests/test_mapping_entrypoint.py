"""The product entrypoint exposes a bounded synthetic probe, never user paths."""

import json
import runpy
import socket
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from ontolearn_engine.mapping import probe

ENTRY = Path(__file__).resolve().parents[1] / "entrypoint.py"
EXPECTED = json.loads(
    (
        ENTRY.parents[2]
        / "docs/reviews/T03/mapping-p2-boundaries-20261023/fixed-probe-v2-expected.json"
    ).read_text()
)
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
    "external-cached-formula": "passed",
    "external-hyperlink": "passed",
    "csv-file-limit-located": "SOURCE_LIMIT",
    "csv-column-limit-located": "SOURCE_LIMIT",
    "csv-cell-limit-located": "INVALID_CELL",
    "csv-row-limit-located": "SOURCE_LIMIT",
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
    assert output == EXPECTED
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
    assert result.stderr == b"MAPPING_PROBE_INVALID_ARGUMENTS\n"


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


def test_socket_guard_is_restored_after_successful_fixed_probe():
    originals = {
        name: getattr(socket, name) for name in ("socket", "create_connection", "getaddrinfo")
    }
    assert probe.run()["boundaryEvidence"] == EXPECTED["boundaryEvidence"]
    assert all(getattr(socket, name) is original for name, original in originals.items())


@pytest.mark.parametrize("api", ["socket", "create_connection", "getaddrinfo"])
def test_socket_attempt_is_refused_and_original_apis_are_restored(monkeypatch, api):
    originals = {
        name: getattr(socket, name) for name in ("socket", "create_connection", "getaddrinfo")
    }

    def attempt(*_args, **_kwargs):
        getattr(socket, api)("not-used; guarded before any network call")

    monkeypatch.setattr(probe, "parse_xlsx", attempt)
    with pytest.raises(RuntimeError, match="^MAPPING_PROBE_NETWORK_ATTEMPT$"):
        probe.run()
    assert all(getattr(socket, name) is original for name, original in originals.items())


def test_swallowed_socket_failure_cannot_be_reported_as_zero_calls(monkeypatch):
    originals = {
        name: getattr(socket, name) for name in ("socket", "create_connection", "getaddrinfo")
    }
    parse = probe.parse_xlsx

    def swallow_attempt(*args, **kwargs):
        try:
            socket.getaddrinfo("not-used; guarded", 0)
        except RuntimeError:
            pass
        return parse(*args, **kwargs)

    monkeypatch.setattr(probe, "parse_xlsx", swallow_attempt)
    with pytest.raises(RuntimeError, match="^MAPPING_PROBE_NETWORK_ATTEMPT$"):
        probe.run()
    assert all(getattr(socket, name) is original for name, original in originals.items())


def test_new_file_limit_case_requires_location_beyond_the_legacy_error_code(monkeypatch):
    parse = probe.parse_csv

    def wrong_location(data, **kwargs):
        try:
            return parse(data, **kwargs)
        except probe.SourceError as error:
            if len(data) > probe.MAX_BYTES:
                raise probe.SourceError(replace(error.issue, row=1)) from None
            raise

    monkeypatch.setattr(probe, "parse_csv", wrong_location)
    with pytest.raises(RuntimeError, match="^CSV_BOUNDARY_LOCATION_MISMATCH$"):
        probe.run()
