"""Same raw-byte corpus consumed by the TS reader."""

import json

import pytest
from ontolearn_engine.protocol import JsonlReader, ProtocolFault
from ontolearn_engine.resources import CONTRACT

CORPUS = json.loads((CONTRACT.ROOT / "frame-fixtures.json").read_text())["cases"]


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
