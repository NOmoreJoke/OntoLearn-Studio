"""PyInstaller entrypoint; business modules remain in the engine package."""

import sys

EXAMPLE_ROOT_ARGUMENT = "--t11-internal-example-root"
EXAMPLE_PROVIDER_MANIFEST_SHA256 = (
    "a2200250856474ebbae669151891d5495e7fcd042e8f8f0a77ccbb0553b521ee"
)


def _requests_example_bootstrap(arguments):
    return any(
        value == EXAMPLE_ROOT_ARGUMENT or value.startswith(EXAMPLE_ROOT_ARGUMENT + "=")
        for value in arguments
    )


def _example_arguments(arguments):
    from pathlib import Path

    ordinary = []
    root = None
    for value in arguments:
        if value == EXAMPLE_ROOT_ARGUMENT:
            raise ValueError("INVALID_EXAMPLE_BOOTSTRAP")
        if value.startswith(EXAMPLE_ROOT_ARGUMENT + "="):
            text = value[len(EXAMPLE_ROOT_ARGUMENT) + 1 :]
            if root is not None or not text or "\x00" in text:
                raise ValueError("INVALID_EXAMPLE_BOOTSTRAP")
            root = Path(text)
            if not root.is_absolute():
                raise ValueError("INVALID_EXAMPLE_BOOTSTRAP")
        else:
            ordinary.append(value)
    if root is None:
        raise ValueError("INVALID_EXAMPLE_BOOTSTRAP")
    return ordinary, root


def _example_bootstrap(arguments):
    """Host argv supplies trust; the existing provider authenticates resource bytes."""
    import asyncio

    profile = "legacy2"
    resources = None
    entered_serve = False
    startup_failure = None
    code_for = None
    try:
        from ontolearn_engine.__main__ import emit_startup_failure, startup_arguments

        ordinary, root = _example_arguments(arguments)
        profile, backup = startup_arguments(ordinary)
        if profile != "business3":
            raise ValueError("INVALID_EXAMPLE_BOOTSTRAP")
        from ontolearn_engine import resources
        from ontolearn_engine.coordinator import StartupInitializationFailure, serve, startup_code
        from ontolearn_engine.project.mainline import make_example_provider

        startup_failure, code_for = StartupInitializationFailure, startup_code
        provider = make_example_provider(
            root=root, manifest_sha256=EXAMPLE_PROVIDER_MANIFEST_SHA256
        )
        entered_serve = True
        asyncio.run(serve(profile=profile, backup_path=backup, example_provider=provider))
    except BaseException as error:
        # Preserve the existing startup contract; never emit paths or exception text.
        wrote = False
        if profile == "business3" and resources is not None and isinstance(error, Exception):
            code = None
            if startup_failure is not None and isinstance(error, startup_failure):
                try:
                    code = code_for(error.cause)
                except Exception:
                    code = "INTERNAL_ERROR"
            elif not entered_serve:
                code = "INTERNAL_ERROR"
            if code is not None:
                try:
                    emit_startup_failure(resources.CONTRACT, resources.REGISTRY_HASH, code)
                    wrote = True
                except BaseException:
                    pass
        if not wrote:
            try:
                sys.stderr.write("ENGINE_SESSION_FAILED\n")
                sys.stderr.flush()
            except BaseException:
                pass
        raise SystemExit(1) from None


if __name__ == "__main__":
    if _requests_example_bootstrap(sys.argv[1:]):
        _example_bootstrap(sys.argv[1:])
    elif sys.argv[1:2] == ["--mapping-probe"]:
        if sys.argv[1:] != ["--mapping-probe"]:
            sys.stderr.write("MAPPING_PROBE_INVALID_ARGUMENTS\n")
            raise SystemExit(2)
        try:
            from ontolearn_engine.mapping.probe import main as mapping_probe_main

            mapping_probe_main()
        except Exception:
            sys.stderr.write("MAPPING_PROBE_FAILED\n")
            raise SystemExit(1) from None
    elif sys.argv[1:2] == ["--storage-probe"]:
        from ontolearn_engine.storage_probe import main as probe_main

        sys.argv.pop(1)
        probe_main()
    elif sys.argv[1:2] == ["--worker"]:
        from ontolearn_engine.worker import main as worker_main

        worker_main()
    elif sys.argv[1:2] == ["--contract-probe"]:
        from ontolearn_engine.contract_probe import main as contract_probe_main

        contract_probe_main()
    elif sys.argv[1:2] == ["--protocol-resources"]:
        from ontolearn_engine.resources import main as resource_main

        resource_main()
    else:
        from ontolearn_engine.__main__ import main

        main()
