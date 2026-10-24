"""Raw frame boundaries, not merely decoded JSON schema tests."""

import json

import pytest
from ontolearn_engine.protocol import MAX_REQUEST_BYTES, JsonlReader, ProtocolFault, decode_frame


def test_chunk_split_coalesced_multibyte_and_crlf():
    wire = '{"text":"中文😀\\"{[]}\\\\"}\r\n{"two":2}\n'.encode()
    for split in range(len(wire) + 1):
        reader = JsonlReader()
        assert reader.feed(wire[:split]) + reader.feed(wire[split:]) == [
            {"text": '中文😀"{[]}\\'},
            {"two": 2},
        ]
        reader.finish()


@pytest.mark.parametrize(
    "raw",
    [
        b"",
        b"\xef\xbb\xbf{}",
        b"\xff",
        b"{",
        b"{}{}",
        b'{"x":{"a":1,"a":2}}',
        b'{"a":NaN}',
        b'{"a":Infinity}',
        b"[" * 33 + b"0" + b"]" * 33,
    ],
)
def test_invalid_raw_input_is_session_fatal(raw):
    reader = JsonlReader()
    with pytest.raises(ProtocolFault):
        reader.feed(raw + b"\n")
    assert reader.terminal and not reader.buffer
    assert reader.feed(b"x" * (MAX_REQUEST_BYTES * 3)) == []
    assert reader.feed(b"{}\n") == []


def test_limit_checked_before_append_and_coalesced_total_not_frame_limit():
    reader = JsonlReader(8)
    assert reader.feed(b"{}\n" * 100) == [{}] * 100
    reader.feed(b"12345678")
    assert len(reader.buffer) == 8
    with pytest.raises(ProtocolFault):
        reader.feed(b"x" * 1000000)
    assert len(reader.buffer) == 0
    assert reader.feed(b"x" * 1000000) == []


def test_eof_partial_frame_rejected_and_finished_reader_stops():
    reader = JsonlReader()
    reader.feed(b"{}")
    with pytest.raises(ProtocolFault):
        reader.finish()
    assert reader.feed(b"{}\n") == []


def test_exact_frame_limit():
    raw = json.dumps({"x": "a" * (MAX_REQUEST_BYTES - 8)}, separators=(",", ":")).encode()
    assert len(raw) == MAX_REQUEST_BYTES
    assert decode_frame(raw)["x"]
    with pytest.raises(ProtocolFault):
        decode_frame(raw + b" ")
