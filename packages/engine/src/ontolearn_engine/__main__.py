"""Serve one bounded request on stdin and exit; stdout is protocol-only."""

import json
import sys

from ontolearn_engine.protocol import MAX_REQUEST_BYTES, handle_request


def main() -> None:
    raw = sys.stdin.buffer.readline(MAX_REQUEST_BYTES + 1)
    response = handle_request(raw)
    sys.stdout.buffer.write((json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
