"""Versioned Appendix D contract. Presentation strings belong to clients."""

import json
from importlib.resources import files

RULES = json.loads(files("ontolearn_engine").joinpath("invalidation-v1.json").read_text())
CODES = {r["family"]: r["staleReason"] for r in RULES["rules"]}


def family(key: str) -> str:
    category, separator, name = key.partition(":")
    if not separator or not name or category not in CODES:
        raise ValueError(f"Unknown dependency key: {key}")
    return category


def reasons(before: dict[str, int], now: dict[str, int]) -> list[dict]:
    """Only actual dependencies; config is intentionally a no-invalidation rule."""
    result = []
    for key, version in sorted(before.items()):
        code = CODES[family(key)]
        if code and version != now.get(key, 0):
            result.append(
                {"code": code, "dependency": key, "before": version, "after": now.get(key, 0)}
            )
    return result
