"""Run one supervised resident v2 session. Stdout is exclusively flushed JSONL."""

import asyncio
import sys


def main() -> None:
    try:
        from ontolearn_engine.coordinator import serve

        asyncio.run(serve())
    except Exception:
        # Only a fixed bounded diagnostic crosses stderr, including initialization.
        sys.stderr.write("ENGINE_SESSION_FAILED\n")
        sys.stderr.flush()
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
