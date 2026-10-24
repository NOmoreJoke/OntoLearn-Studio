"""Same raw-byte corpus consumed by the TS reader."""

import json
import runpy
from pathlib import Path

import pytest
from ontolearn_engine import contract_probe
from ontolearn_engine.protocol import JsonlReader, ProtocolFault
from ontolearn_engine.resources import CONTRACT

CORPUS = json.loads((CONTRACT.ROOT / "frame-fixtures.json").read_text(encoding="utf-8"))["cases"]


@pytest.fixture
def cp1252_contract_default(monkeypatch):
    fixtures = {
        CONTRACT.ROOT / name
        for name in ("fixtures.json", "binding-regressions.json", "frame-fixtures.json")
    }
    original_read_text = Path.read_text

    def read_fixture(path, encoding=None, errors=None):
        # Emulate only this resource's platform default, leaving source loading,
        # pytest output and the real byte parser untouched. Inject before
        # read_text resolves None via io.text_encoding (including UTF-8 mode).
        if path in fixtures and encoding in {None, "locale"}:
            encoding = "cp1252"
        return original_read_text(path, encoding=encoding, errors=errors)

    monkeypatch.setattr(Path, "read_text", read_fixture)


def test_corpus_uses_utf8_when_default_file_encoding_is_cp1252(cp1252_contract_default):
    fixture = CONTRACT.ROOT / "frame-fixtures.json"
    default_cases = json.loads(fixture.read_text())["cases"]
    loaded_cases = runpy.run_path(__file__)["CORPUS"]
    boundaries = [case for case in loaded_cases if case["name"].startswith("UTF8 chunk boundary")]
    assert boundaries
    assert all(case["expectedFrames"] == [{"text": "中文😀"}, {"ok": True}] for case in boundaries)
    assert loaded_cases == CORPUS
    assert default_cases != loaded_cases
    assert default_cases[0]["expectedFrames"][0]["text"] == "中文😀".encode().decode("cp1252")


@pytest.mark.parametrize(
    "module_name,variable,fixture_name,section",
    [
        ("test_binding_regressions.py", "CASES", "binding-regressions.json", "cases"),
        ("test_project_business3_contract.py", "PROFILE", "fixtures.json", "business3"),
        (
            "test_project_business3_contract.py",
            "REGRESSIONS",
            "binding-regressions.json",
            "business3",
        ),
        ("test_project_source_table_material.py", "CORPUS", "fixtures.json", "sourceTable"),
        ("test_query_definition_service.py", "FIXTURES", "fixtures.json", None),
        ("test_query_definition_service.py", "BINDINGS", "binding-regressions.json", None),
        ("test_query_presentation.py", "DATA", "fixtures.json", "queryConsumer"),
    ],
)
def test_shared_corpus_modules_keep_utf8_under_cp1252(
    cp1252_contract_default, module_name, variable, fixture_name, section
):
    # Exercise eager test collection with a Windows-style default, without
    # changing process-wide encoding or replacing any contract validation.
    loaded = runpy.run_path(str(Path(__file__).with_name(module_name)))
    expected = json.loads((CONTRACT.ROOT / fixture_name).read_text(encoding="utf-8"))
    if section is not None:
        expected = expected[section]
    assert loaded[variable] == expected


def test_common_examples_use_utf8_when_default_file_encoding_is_cp1252(
    cp1252_contract_default, capsys
):
    contract_probe.main()
    captured = capsys.readouterr()
    assert captured.err == ""
    # The adopted ordinary/Query R3 composite has 372 shape cases and 34 common
    # response bindings. Retain full-set counts and the encoding/probe assertion.
    expected_counts = {
        "cases": 372,
        "routing": 11,
        "responses": 34,
        "cursors": 9,
        "jobListCursors": 7,
        "trustedBindings": 41,
        "rawFrames": 51,
    }
    fixtures = json.loads((CONTRACT.ROOT / "fixtures.json").read_text(encoding="utf-8"))
    bindings = json.loads((CONTRACT.ROOT / "binding-regressions.json").read_text(encoding="utf-8"))
    assert {
        key: len(fixtures[key])
        for key in ("cases", "routing", "responses", "cursors", "jobListCursors")
    } == {
        key: expected_counts[key]
        for key in ("cases", "routing", "responses", "cursors", "jobListCursors")
    }
    assert len(bindings["cases"]) == expected_counts["trustedBindings"]
    assert len(CORPUS) == expected_counts["rawFrames"]
    assert json.loads(captured.out) == {
        "status": "passed",
        "counts": expected_counts,
    }


@pytest.mark.parametrize("case", CORPUS, ids=lambda c: c["name"])
def test_raw_frames(case):
    reader = JsonlReader(case.get("maxBytes", 262144))
    frames, errors = [], []
    for chunk in case["chunks"]:
        try:
            frames.extend(reader.feed(bytes.fromhex(chunk)))
        except ProtocolFault as error:
            frames.extend(error.frames)
            errors.append("frame" if case["name"] == "append before byte limit" else "json")
    if case["end"]:
        try:
            reader.finish()
        except ProtocolFault as error:
            frames.extend(error.frames)
            errors.append("json")
    assert frames == case["expectedFrames"]
    assert errors == case["expectedErrors"]
    assert reader.terminal is case["terminal"]
    assert not reader.buffer
