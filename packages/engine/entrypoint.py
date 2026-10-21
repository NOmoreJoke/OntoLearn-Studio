"""PyInstaller entrypoint; business modules remain in the engine package."""

import sys

if __name__ == "__main__":
    profile_flag = "--semantic-profile-probe"
    if any(arg == profile_flag or arg.startswith(profile_flag + "=") for arg in sys.argv[1:]):
        if sys.argv[1:] != [profile_flag]:
            sys.stderr.write("PROFILE_PROBE_ARGUMENTS_INVALID\n")
            raise SystemExit(2)
        from ontolearn_engine.semantic_profile_probe import main as profile_probe_main

        sys.argv.pop(1)
        raise SystemExit(profile_probe_main([]))
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
