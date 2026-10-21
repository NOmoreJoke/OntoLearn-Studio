"""PyInstaller entrypoint; business modules remain in the engine package."""

import sys

if __name__ == "__main__":
    if sys.argv[1:2] == ["--mapping-probe"]:
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
