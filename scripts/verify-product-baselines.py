#!/usr/bin/env python3
"""Verify fixed input; --reset exports an independent versioned model to stdout."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages/engine/src"))

from ontolearn_engine.learning.baselines import BASELINES, reset_input, verify  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", choices=BASELINES)
    args = parser.parse_args()
    try:
        value = reset_input(ROOT, args.reset) if args.reset else verify(ROOT)
    except (ValueError, KeyError, OSError, TypeError) as error:
        print("Baseline verification failed: " + str(error), file=sys.stderr)
        return 1
    print(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
