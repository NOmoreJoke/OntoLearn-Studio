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
    original_open = Path.open

    def open_fixture(path, mode="r", buffering=-1, encoding=None, errors=None, newline=None):
        # Emulate only this resource's platform default, leaving source loading,
        # pytest output and the real byte parser untouched.
        if path in fixtures and encoding in {None, "locale"}:
            encoding = "cp1252"
        return original_open(path, mode, buffering, encoding, errors, newline)

    monkeypatch.setattr(Path, "open", open_fixture)


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


def test_common_examples_use_utf8_when_default_file_encoding_is_cp1252(
    cp1252_contract_default, capsys
):
    contract_probe.main()
    captured = capsys.readouterr()
    assert captured.err == ""
    assert json.loads(captured.out) == {
        "status": "passed",
        "counts": {
            "cases": 321,
            "routing": 11,
            "responses": 30,
            "cursors": 9,
            "jobListCursors": 7,
            "trustedBindings": 41,
            "rawFrames": 51,
        },
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
