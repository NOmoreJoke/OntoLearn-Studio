"""PyInstaller entrypoint; business modules remain in the engine package."""

import sys

from ontolearn_engine.__main__ import main

if __name__ == "__main__":
    if sys.argv[1:2] == ["--semantic-probe"]:
        from ontolearn_engine.semantic_probe import main as semantic_probe_main

        sys.argv.pop(1)
        semantic_probe_main()
    elif sys.argv[1:2] == ["--storage-probe"]:
        from ontolearn_engine.storage_probe import main as probe_main

        sys.argv.pop(1)
        probe_main()
    else:
        main()
