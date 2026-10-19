"""PyInstaller entrypoint; business modules remain in the engine package."""

from ontolearn_engine.__main__ import main

if __name__ == "__main__":
    main()
