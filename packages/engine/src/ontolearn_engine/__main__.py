"""Run one supervised session; stdout contains only bounded flushed JSONL."""

import asyncio
import json
import sys
from pathlib import Path


def startup_arguments(arguments):
    profile = "legacy2"
    backup = None
    seen = set()
    for argument in arguments:
        if argument == "--t01-internal-profile=business3" and "profile" not in seen:
            seen.add("profile")
            profile = "business3"
        elif argument.startswith("--t01-internal-backup=") and "backup" not in seen:
            seen.add("backup")
            backup = argument.split("=", 1)[1]
            if not backup or not Path(backup).is_absolute():
                raise ValueError("INVALID_BACKUP")
        else:
            raise ValueError("INVALID_STARTUP_ARGUMENT")
    if backup is not None and profile != "business3":
        raise ValueError("INVALID_BACKUP")
    return profile, backup


def emit_startup_failure(contract, registry_hash, code):
    # Parameters are fixed by the approved startup contract, never exception data.
    params = (
        {"supportedFormats": [3]}
        if code == "PROJECT_FORMAT_UNSUPPORTED"
        else {"retryAfterMs": 250}
        if code == "STORAGE_BUSY"
        else {}
    )
    value = {
        "kind": "startupFailure",
        "diagnosticVersion": 1,
        "engineSessionId": None,
        "registryHash": registry_hash,
        "error": contract.startup_error(code, params),
    }
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode(
        "utf-8"
    )
    if not contract.validate_startup_failure(value, len(raw), registry_hash):
        raise ValueError("INVALID_STARTUP_DIAGNOSIS")
    if sys.stdout.buffer.write(raw + b"\n") != len(raw) + 1:
        raise BrokenPipeError("INCOMPLETE_STARTUP_WRITE")
    sys.stdout.buffer.flush()


def main() -> None:
    profile = "legacy2"
    resources = None
    entered_serve = False
    startup_failure = None
    code_for = None
    try:
        profile, backup = startup_arguments(sys.argv[1:])
        from ontolearn_engine import resources
        from ontolearn_engine.coordinator import StartupInitializationFailure, serve, startup_code

        startup_failure, code_for = StartupInitializationFailure, startup_code
        entered_serve = True
        asyncio.run(serve(profile=profile, backup_path=backup))
    except BaseException as error:
        wrote = False
        if profile == "business3" and resources is not None and isinstance(error, Exception):
            code = None
            if startup_failure is not None and isinstance(error, startup_failure):
                try:
                    code = code_for(error.cause)
                except Exception:
                    code = "INTERNAL_ERROR"
            elif not entered_serve:
                code = "INTERNAL_ERROR"  # Resources loaded, later initialization import failed.
            if code is not None:
                try:
                    emit_startup_failure(resources.CONTRACT, resources.REGISTRY_HASH, code)
                    wrote = True
                except BaseException:
                    pass  # A partial/broken write never becomes a successful diagnosis.
        if not wrote:
            try:
                sys.stderr.write("ENGINE_SESSION_FAILED\n")
                sys.stderr.flush()
            except BaseException:
                pass
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
