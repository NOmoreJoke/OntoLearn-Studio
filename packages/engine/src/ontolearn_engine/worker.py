"""Isolated test workload. No database, project path, network or business capability."""

import ctypes
import hashlib
import json
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
from ontolearn_engine.protocol import MAX_REQUEST_BYTES, decode_frame, decode_payload


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
    if request["capability"] in {"query.execute", "reasoning.execute", "validation.execute"}:
        try:
            _semantic(request)
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


def _semantic(request):
    # The parent monitor and memory guard are established before reading the
    # snapshot or importing RDFLib/pySHACL. The worker has no database authority.
    from ontolearn_engine.resources import CONTRACT, safe_error
    from ontolearn_engine.semantic_error_adapter import (
        ErrorContext,
        Origin,
        Producer,
        SemanticErrorAdapter,
        Stage,
    )
    from ontolearn_engine.semantic_execution import SemanticExecutionFault, _rows, execute_request
    from ontolearn_engine.semantic_offline import SemanticError

    count = request.get("semanticParts")
    if type(count) is not int or not 1 <= count <= 1024:
        raise ValueError("SEMANTIC_INPUT_INVALID")
    parts, size = [], 0
    for index in range(count):
        part = decode_frame(sys.stdin.buffer.readline(MAX_REQUEST_BYTES + 1).rstrip(b"\n"))
        if (
            not isinstance(part, dict)
            or set(part) != {"index", "text"}
            or type(part["index"]) is not int
            or part["index"] != index
            or not isinstance(part["text"], str)
            or len(part["text"]) > 32000
        ):
            raise ValueError("SEMANTIC_INPUT_INVALID")
        size += len(part["text"].encode())
        if size > 8388608:
            raise ValueError("SEMANTIC_INPUT_LIMIT")
        parts.append(part["text"])
    text = "".join(parts)
    if hashlib.sha256(text.encode()).hexdigest() != request["semanticHash"]:
        raise ValueError("SEMANTIC_INPUT_INVALID")
    bundle = decode_payload(text.encode(), max_bytes=8388608)
    if not isinstance(bundle, dict) or set(bundle) != {"request", "validationBinding"}:
        raise ValueError("SEMANTIC_INPUT_INVALID")
    try:
        output = execute_request(
            bundle["request"], error_catalog=CONTRACT.ERROR_CATALOG, error_schema=CONTRACT.DOCUMENT
        )
        if bundle["validationBinding"] is not None:
            binding = bundle["validationBinding"]
            if not CONTRACT.validation_projection_matches_resources(
                binding["projection"], binding["resources"]
            ):
                raise ValueError("SEMANTIC_BINDING_INVALID")
            output["payload"]["validationBinding"] = binding
            output["rows"] = _rows(output["payload"])
        text = json.dumps(
            output, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        if len(text.encode()) > 8388608:
            emit(
                {
                    "type": "semantic.error",
                    "error": safe_error("RESOURCE_LIMIT", {"resource": "semanticResult"}),
                }
            )
            return
        parts = [text[i : i + 32000] for i in range(0, len(text), 32000)]
        for index, part in enumerate(parts):
            emit({"type": "semantic.chunk", "index": index, "text": part})
        emit(
            {
                "type": "semantic.done",
                "parts": len(parts),
                "sha256": hashlib.sha256(text.encode()).hexdigest(),
            }
        )
        emit({"type": "complete"})
    except SemanticExecutionFault as error:
        emit({"type": "semantic.error", "error": error.error})
    except SemanticError as error:
        # Binding metadata is added after the pure executor. Its final lossless
        # projection has the same semantic result budget and safe classification.
        adapter = SemanticErrorAdapter(
            error_catalog=CONTRACT.ERROR_CATALOG, error_schema=CONTRACT.DOCUMENT
        )
        emit(
            {
                "type": "semantic.error",
                "error": adapter.adapt(
                    producer=Producer.PROJECTION,
                    reason=error.code,
                    context=ErrorContext(Stage.PROJECTION, Origin.TRUSTED_INTERNAL),
                ),
            }
        )
    except MemoryError:
        raise  # The actual worker memory guard/exit code owns this classification.
    except Exception:
        emit({"type": "semantic.error", "error": safe_error("INTERNAL_ERROR")})


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
