"""Strict bounded raw JSONL transport. No v1 fallback and no raw diagnostics."""

import json
import math

MAX_REQUEST_BYTES = 262144
MAX_DEPTH = 32


class ProtocolFault(Exception):
    """Session-fatal protocol violation, never carries input text."""

    def __init__(self):
        super().__init__("PROTOCOL_FAULT")
        self.frames = []  # Previously completed frames precede the fatal boundary.


def _pairs(pairs: list) -> dict:
    value = {}
    for key, item in pairs:
        if key in value:
            raise ProtocolFault()
        value[key] = item
    return value


def decode_frame(frame: bytes) -> object:
    return decode_payload(frame, max_bytes=MAX_REQUEST_BYTES)


def decode_payload(frame: bytes, *, max_bytes: int) -> object:
    """Private chunk reassembly uses the same strict JSON checks, with its own bound."""
    if not 1 <= max_bytes <= 8388608:
        raise ProtocolFault()
    if not frame or len(frame) > max_bytes or frame.startswith(b"\xef\xbb\xbf"):
        raise ProtocolFault()
    # Scan string/escape aware before JSON allocation/recursive parsing.
    quoted = escaped = False
    depth = 0
    for byte in frame:
        if quoted:
            if escaped:
                escaped = False
            elif byte == 92:
                escaped = True
            elif byte == 34:
                quoted = False
        elif byte == 34:
            quoted = True
        elif byte in (91, 123):
            depth += 1
            if depth > MAX_DEPTH:
                raise ProtocolFault()
        elif byte in (93, 125):
            depth -= 1
    try:
        value = json.loads(
            frame.decode("utf-8", errors="strict"),
            object_pairs_hook=_pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(ProtocolFault()),
        )
        stack = [value]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                stack.extend(item.keys())
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
            elif isinstance(item, str) and any(0xD800 <= ord(c) <= 0xDFFF for c in item):
                raise ProtocolFault()
            elif type(item) in {int, float} and (
                abs(item) > 9007199254740991 or not math.isfinite(item)
            ):
                raise ProtocolFault()
        return value
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ProtocolFault() from error


class JsonlReader:
    def __init__(self, max_bytes: int = MAX_REQUEST_BYTES):
        if not 1 <= max_bytes <= MAX_REQUEST_BYTES:
            raise ValueError("INVALID_FRAME_LIMIT")
        self.max_bytes = max_bytes
        self.buffer = bytearray()
        self.terminal = False

    def stop(self) -> None:
        self.terminal = True
        self.buffer.clear()

    def feed(self, chunk: bytes) -> list:
        if self.terminal:
            return []
        frames = []
        offset = 0
        try:
            while offset < len(chunk):
                end = chunk.find(b"\n", offset)
                stop = len(chunk) if end < 0 else end
                length = stop - offset
                # Check BEFORE copying any new bytes; even no-LF and repeated chunks bounded.
                if len(self.buffer) + length > self.max_bytes:
                    raise ProtocolFault()
                self.buffer.extend(memoryview(chunk)[offset:stop])
                if end < 0:
                    break
                raw = bytes(self.buffer)
                self.buffer.clear()
                if raw.endswith(b"\r"):
                    raw = raw[:-1]
                frames.append(decode_frame(raw))
                offset = end + 1
            return frames
        except ProtocolFault as error:
            error.frames = frames
            self.stop()
            raise

    def finish(self) -> None:
        incomplete = bool(self.buffer)
        self.stop()
        if incomplete:
            raise ProtocolFault()
