"""Isolated test workload. No database, project path, network or business capability."""

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
from ontolearn_engine.protocol import MAX_REQUEST_BYTES, decode_frame


def emit(value: dict) -> None:
    raw = json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()
    if len(raw) > MAX_REQUEST_BYTES:
        raise ValueError("WORKER_FRAME_LIMIT")
    sys.stdout.buffer.write(raw + b"\n")
    sys.stdout.buffer.flush()


def watch_parent() -> None:
    parent = os.getppid()
    if parent <= 1:
        os._exit(73)
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        handle = kernel.OpenProcess(0x100000, False, parent)  # SYNCHRONIZE only
        if not handle:
            os._exit(73)
        kernel.WaitForSingleObject(handle, 0xFFFFFFFF)
        os._exit(73)
    while os.getppid() == parent:
        time.sleep(0.1)
    os._exit(73)


def run() -> None:
    threading.Thread(target=watch_parent, daemon=True).start()
    request = decode_frame(sys.stdin.buffer.readline(MAX_REQUEST_BYTES + 1).rstrip(b"\n"))
    guard = install_memory_guard(request["memoryBytes"])
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


def main() -> None:
    try:
        run()
    except MemoryError:
        os._exit(MEMORY_LIMIT_EXIT)
    except MemoryGuardUnavailable:
        os._exit(MEMORY_GUARD_EXIT)
    except Exception:
        os._exit(76)  # Fixed internal failure, no raw library traceback or input.


if __name__ == "__main__":
    main()
