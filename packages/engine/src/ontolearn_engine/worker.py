"""Owned isolated computation. No database, project path or external I/O authority."""

import ctypes
import hashlib
import json
import math
import os
import sys
import threading
import time

from ontolearn_engine.memory_guard import (
    MEMORY_GUARD_EXIT,
    MEMORY_LIMIT_EXIT,
    MemoryGuardUnavailable,
    install_memory_guard,
)
from ontolearn_engine.protocol import MAX_DEPTH, MAX_REQUEST_BYTES, ProtocolFault, decode_frame


def emit(value: dict) -> None:
    raw = json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()
    if len(raw) > MAX_REQUEST_BYTES:
        raise ValueError("WORKER_FRAME_LIMIT")
    sys.stdout.buffer.write(raw + b"\n")
    sys.stdout.buffer.flush()


OWNER_EXIT = 73
_OWNER_FLAG = "--coordinator-owner"
_WAIT_TIMEOUT = 0x102


class OwnerUnavailable(RuntimeError):
    """The trusted coordinator identity cannot be monitored; contains no details."""


def _windows_kernel():
    from ctypes import wintypes

    try:
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "GetCurrentProcess": ([], wintypes.HANDLE),
            "GetProcessId": ([wintypes.HANDLE], wintypes.DWORD),
            "OpenProcess": ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
            "GetProcessTimes": (
                [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4,
                wintypes.BOOL,
            ),
            "WaitForSingleObject": ([wintypes.HANDLE, wintypes.DWORD], wintypes.DWORD),
            "CloseHandle": ([wintypes.HANDLE], wintypes.BOOL),
        }
        for name, (arguments, result) in signatures.items():
            function = getattr(kernel, name)
            function.argtypes = arguments
            function.restype = result
        return kernel
    except (OSError, AttributeError) as error:
        raise OwnerUnavailable() from error


def _created_at(kernel, handle) -> int:
    from ctypes import wintypes

    created, exited, kernel_time, user_time = (wintypes.FILETIME() for _ in range(4))
    try:
        success = kernel.GetProcessTimes(
            handle,
            ctypes.byref(created),
            ctypes.byref(exited),
            ctypes.byref(kernel_time),
            ctypes.byref(user_time),
        )
    except OSError as error:
        raise OwnerUnavailable() from error
    if not success:
        raise OwnerUnavailable()
    value = (created.dwHighDateTime << 32) | created.dwLowDateTime
    if not value:
        raise OwnerUnavailable()
    return value


def worker_owner_arguments() -> list[str]:
    # os.getpid identifies the Python coordinator, unlike a Popen/redirector PID
    # or the worker's immediate parent. Arguments cross both source/frozen boots.
    pid = os.getpid()
    created = 0
    if sys.platform == "win32":
        kernel = _windows_kernel()
        try:
            current = kernel.GetCurrentProcess()  # Pseudo-handle; must not be closed.
            if not current or kernel.GetProcessId(current) != pid:
                raise OwnerUnavailable()
        except OSError as error:
            raise OwnerUnavailable() from error
        created = _created_at(kernel, current)
    return [_OWNER_FLAG, str(pid), str(created)]


def _owner_arguments(arguments: list[str]) -> tuple[int, int]:
    # The frozen entrypoint leaves its private --worker dispatch token in argv.
    if arguments[:1] == ["--worker"]:
        arguments = arguments[1:]
    if len(arguments) != 3 or arguments[0] != _OWNER_FLAG:
        raise OwnerUnavailable()
    values = arguments[1:]
    if any(not value.isascii() or not value.isdecimal() or len(value) > 20 for value in values):
        raise OwnerUnavailable()
    pid, created = (int(value) for value in values)
    if not 1 < pid <= 0xFFFFFFFF or not 0 <= created <= 0xFFFFFFFFFFFFFFFF:
        raise OwnerUnavailable()
    if (sys.platform == "win32" and created == 0) or (sys.platform != "win32" and created != 0):
        raise OwnerUnavailable()
    return pid, created


class _WindowsOwner:
    def __init__(self, pid: int, created: int):
        self.kernel = _windows_kernel()
        try:
            self.handle = self.kernel.OpenProcess(0x100000 | 0x1000, False, pid)
        except OSError as error:
            raise OwnerUnavailable() from error
        if not self.handle:
            raise OwnerUnavailable()
        try:
            # A PID can be reused before bootstrap. Creation time authenticates
            # that lookup; the retained handle then stays tied to that process.
            if (
                self.kernel.GetProcessId(self.handle) != pid
                or _created_at(self.kernel, self.handle) != created
            ):
                raise OwnerUnavailable()
            if not self.alive():
                raise OwnerUnavailable()
        except Exception as error:
            self.close()
            raise OwnerUnavailable() from error

    def alive(self) -> bool:
        try:
            result = self.kernel.WaitForSingleObject(self.handle, 0)
        except OSError as error:
            raise OwnerUnavailable() from error
        if result == 0:
            return False
        if result != _WAIT_TIMEOUT:
            raise OwnerUnavailable()
        return True

    def close(self) -> None:
        handle, self.handle = self.handle, None
        try:
            if handle and not self.kernel.CloseHandle(handle):
                raise OwnerUnavailable()
        except OSError as error:
            raise OwnerUnavailable() from error


class _DirectOwner:
    def __init__(self, pid: int):
        self.pid = pid
        if not self.alive():
            raise OwnerUnavailable()

    def alive(self) -> bool:
        # POSIX direct parentage cannot be fooled by reuse of the old owner's
        # PID: after reparenting getppid refers to the adopter, not that new PID.
        return os.getppid() == self.pid

    def close(self) -> None:
        pass


class _OwnerMonitor:
    def __init__(self, pid: int, created: int):
        self.owner = _WindowsOwner(pid, created) if sys.platform == "win32" else _DirectOwner(pid)
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._watch, daemon=True)
        try:
            self.thread.start()
        except Exception as error:
            self.owner.close()
            raise OwnerUnavailable() from error

    def _watch(self) -> None:
        try:
            while not self.stop.wait(0.1):
                if not self.owner.alive():
                    raise OwnerUnavailable()
        except BaseException:
            os._exit(OWNER_EXIT)

    def close(self) -> None:
        self.stop.set()
        self.thread.join(timeout=0.5)
        if self.thread.is_alive():
            raise OwnerUnavailable()
        # No native wait can still be using the handle when it is closed.
        self.owner.close()


def run() -> None:
    monitor = _OwnerMonitor(*_owner_arguments(sys.argv[1:]))
    try:
        _execute()
    finally:
        monitor.close()


def _execute() -> None:
    request = decode_frame(sys.stdin.buffer.readline(MAX_REQUEST_BYTES + 1).rstrip(b"\n"))
    guard = install_memory_guard(request["memoryBytes"])
    if request["capability"] in ("query.execute", "reasoning.execute", "validation.execute"):
        try:
            _query(request)
        finally:
            guard.close()
        return
    parameters = request["parameters"]
    delay = parameters.get("workMs", 0) / 1000
    rounds = parameters.get("maxRounds", 1) if request["capability"] == "test.rounds" else 1
    events = list(parameters.get("events", []))
    consumed = []
    for index in range(1, rounds + 1):
        until = time.monotonic() + delay
        while time.monotonic() < until:
            pass  # Intentionally real busy computation in an isolated process.
        if parameters.get("crashRound") == index:
            os._exit(71)
        if parameters.get("failRound") == index:
            emit({"type": "failure"})
            return
        if parameters.get("allocateBytes"):
            guard.check_allocation(parameters["allocateBytes"])
            allocation = bytearray(parameters["allocateBytes"])
            if not allocation:
                raise RuntimeError("ALLOCATION_FAILED")
        if request["capability"] == "test.rounds":
            take = min(len(events), parameters.get("consumePerRound", len(events)))
            consumed.extend(events[:take])
            events = events[take:]
            generated = [
                f"generated-{index}-{i}" for i in range(parameters.get("generatePerRound", 0))
            ]
            events.extend(generated)
            emit(
                {
                    "type": "round",
                    "round": index,
                    "state": {
                        "pendingEvents": events,
                        "consumedEvents": consumed,
                        "inputEvents": parameters.get("events", []),
                    },
                }
            )
        else:
            emit({"type": "ready", "rows": parameters.get("rows", [])})
    emit({"type": "complete"})
    guard.close()


def query_transport_limits(limits):
    """Intersect current frame/memory limits with the supplier's serialized envelope.

    The same conservative envelope bounds the request too. This is not a new
    graph or workload capacity policy; the supplier still applies its own limits.
    """
    from ontolearn_engine.resources import LIMITS
    from ontolearn_engine.semantic_execution import MAX_OUTPUT_BYTES

    if any(
        type(limits[k]) is not int or limits[k] < 1
        for k in ("maxFrameBytes", "maxWorkerMemoryBytes")
    ):
        raise ProtocolFault()
    frame = min(limits["maxFrameBytes"], LIMITS["maxFrameBytes"], MAX_REQUEST_BYTES)
    size = min(MAX_OUTPUT_BYTES, limits["maxWorkerMemoryBytes"], LIMITS["maxWorkerMemoryBytes"])
    if frame <= 256 or size < 1:
        raise ProtocolFault()
    return frame, size


def query_encode(value, maximum):
    # Bound scalar and container visits before JSON encoding. No unbounded input
    # chunk is appended; UTF-8 allocation is at most four times this finite cap.
    stack = [(value, 0)]
    visits = 0
    while stack:
        item, depth = stack.pop()
        visits += 1
        if visits > maximum or depth > MAX_DEPTH:
            raise ProtocolFault()
        if type(item) is str:
            if len(item) > maximum or any(0xD800 <= ord(c) <= 0xDFFF for c in item):
                raise ProtocolFault()
        elif type(item) is dict:
            if len(item) > maximum - visits or any(type(k) is not str for k in item):
                raise ProtocolFault()
            stack.extend((v, depth + 1) for pair in item.items() for v in pair)
        elif type(item) is list:
            if len(item) > maximum - visits:
                raise ProtocolFault()
            stack.extend((v, depth + 1) for v in item)
        elif type(item) in {int, float}:
            if abs(item) > 9007199254740991 or not math.isfinite(item):
                raise ProtocolFault()
        elif item is not None and type(item) is not bool:
            raise ProtocolFault()
    output, size = [], 0
    encoder = json.JSONEncoder(
        ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    for text in encoder.iterencode(value):
        if len(text) > maximum - size:
            raise ProtocolFault()
        part = text.encode("utf-8", errors="strict")
        if len(part) > maximum - size:
            raise ProtocolFault()
        size += len(part)
        output.append(part)
    return b"".join(output)


def query_decode(raw, maximum):
    if not raw or len(raw) > maximum or raw.startswith(b"\xef\xbb\xbf"):
        raise ProtocolFault()
    quoted = escaped = False
    depth = 0
    for byte in raw:
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

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ProtocolFault()
            result[key] = value
        return result

    try:
        value = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(ProtocolFault()),
        )
        if query_encode(value, maximum) != raw:
            raise ProtocolFault()
        return value
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ProtocolFault() from error


def query_parts(raw, frame):
    # A Unicode scalar takes <=4 UTF-8 bytes, and JSON escaping <=6 bytes.
    # Twelve per scalar plus 256 fixed bytes conservatively covers the wrapper.
    width = (frame - 256) // 12
    if width < 1:
        raise ProtocolFault()
    text = raw.decode("utf-8", errors="strict")
    return [text[i : i + width] for i in range(0, len(text), width)]


def _query(header):
    # run() established the original owner monitor; _execute() installed the
    # memory guard from the bounded bootstrap before these imports/body reads.
    from ontolearn_engine.resources import CONTRACT, safe_error
    from ontolearn_engine.semantic_execution import SemanticExecutionFault, execute_request

    required = {"capability", "memoryBytes", "frameBytes", "byteLimit", "parts", "bytes", "sha256"}
    if set(header) != required:
        raise ProtocolFault()
    frame, maximum = query_transport_limits(
        {"maxFrameBytes": header["frameBytes"], "maxWorkerMemoryBytes": header["memoryBytes"]}
    )
    if (
        type(header["byteLimit"]) is not int
        or header["byteLimit"] != maximum
        or type(header["parts"]) is not int
        or not 1 <= header["parts"] <= maximum
        or type(header["bytes"]) is not int
        or not 1 <= header["bytes"] <= maximum
    ):
        raise ProtocolFault()
    parts, size = [], 0
    for index in range(header["parts"]):
        raw = sys.stdin.buffer.readline(frame + 2)
        if not raw.endswith(b"\n") or len(raw) > frame + 1:
            raise ProtocolFault()
        part = decode_frame(raw[:-1])
        if (
            type(part) is not dict
            or set(part) != {"index", "text"}
            or type(part["index"]) is not int
            or part["index"] != index
            or type(part["text"]) is not str
            or not part["text"]
            or len(part["text"]) > (frame - 256) // 12
        ):
            raise ProtocolFault()
        encoded = part["text"].encode("utf-8", errors="strict")
        if len(encoded) > header["bytes"] - size:
            raise ProtocolFault()
        size += len(encoded)
        parts.append(encoded)
    if size != header["bytes"] or sys.stdin.buffer.read(1):
        raise ProtocolFault()
    raw = b"".join(parts)
    if hashlib.sha256(raw).hexdigest() != header["sha256"]:
        raise ProtocolFault()
    bundle = query_decode(raw, maximum)
    if (
        type(bundle) is not dict
        or bundle.get("capability") != header["capability"]
        or bundle.get("capability")
        not in ("query.execute", "reasoning.execute", "validation.execute")
    ):
        raise ProtocolFault()
    scope = bundle.get("input", {}).get("scope")
    if scope not in ("asserted", "asserted+derived"):
        raise ProtocolFault()
    # Only validation (and derived-scope query) may carry a selected reasoning
    # result; plain asserted query/reasoning bundles never select one.
    if bundle.get("selected") is not None and scope != "asserted+derived":
        raise ProtocolFault()
    if scope == "asserted+derived" and bundle.get("selected") is None:
        raise ProtocolFault()
    try:
        output = execute_request(
            bundle, error_catalog=CONTRACT.ERROR_CATALOG, error_schema=CONTRACT.DOCUMENT
        )
        encoded = query_encode(output, maximum)
        pieces = query_parts(encoded, frame)
        for index, text in enumerate(pieces):
            emit({"type": "query.chunk", "index": index, "text": text})
        emit(
            {
                "type": "query.done",
                "parts": len(pieces),
                "bytes": len(encoded),
                "sha256": hashlib.sha256(encoded).hexdigest(),
            }
        )
    except SemanticExecutionFault as error:
        emit({"type": "query.error", "error": error.error})
    except ProtocolFault:
        emit({"type": "query.error", "error": safe_error("RESOURCE_LIMIT", {"resource": "memory"})})
    emit({"type": "complete"})


def main() -> None:
    try:
        run()
    except OwnerUnavailable:
        os._exit(OWNER_EXIT)
    except MemoryError:
        os._exit(MEMORY_LIMIT_EXIT)
    except MemoryGuardUnavailable:
        os._exit(MEMORY_GUARD_EXIT)
    except Exception:
        os._exit(76)  # Fixed internal failure, no raw library traceback or input.


if __name__ == "__main__":
    main()
