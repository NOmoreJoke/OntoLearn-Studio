"""PyInstaller entrypoint; business modules remain in the engine package."""

import sys

if __name__ == "__main__":
    if sys.argv[1:2] == ["--semantic-source-package-probe"]:
        from ontolearn_engine.semantic_source_package_probe import main as probe_main

        raise SystemExit(probe_main())
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
