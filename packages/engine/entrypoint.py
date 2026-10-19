"""PyInstaller entrypoint; business modules remain in the engine package."""

import sys

from ontolearn_engine.__main__ import main
from ontolearn_engine.storage_probe import main as probe_main

if __name__ == "__main__":
    if sys.argv[1:2] == ["--storage-probe"]:
        sys.argv.pop(1)
        probe_main()
    else:
        main()
