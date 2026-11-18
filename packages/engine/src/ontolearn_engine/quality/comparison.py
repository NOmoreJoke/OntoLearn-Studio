"""Compare supplied observations; never synthesize reasoning or validation results."""

import hashlib
import json

from .definitions import fail, items, shape, text
from .planning import validate_statement


def compare_statements(expected: object, actual: object) -> dict:
    """Complete set comparison for editor tests, not evidence that a runner executed."""

    def statements(value: object, name: str) -> set[tuple]:
        return {
            validate_statement(item, (name, index))
            for index, item in enumerate(items(value, (name,), empty=True))
        }

    wanted, observed = statements(expected, "expected"), statements(actual, "actual")
    return {
        "missing": sorted(wanted - observed),
        "unexpected": sorted(observed - wanted),
        "matched": sorted(wanted & observed),
    }


def validate_trace(nodes: object) -> dict[str, dict]:
    """Check a finite explicit proof DAG, without claiming authenticity of supplied nodes.

    The approved adapter must bind every leaf to the actual immutable input and
    rule/axiom versions. This structural check alone is not a true proof verifier.
    """
    result = {}
    for index, node in enumerate(items(nodes, ("trace",), empty=True)):
        path = ("trace", index)
        shape(node, {"id", "kind", "statement", "inputs", "ruleId"}, path)
        identity = text(node["id"], (*path, "id"))
        if identity in result:
            fail("DUPLICATE_TRACE_NODE", path)
        kind = node["kind"]
        if kind not in ("asserted", "axiom", "rdfs", "rule"):
            fail("INVALID_TRACE_KIND", (*path, "kind"))
        validate_statement(node["statement"], (*path, "statement"))
        refs = items(node["inputs"], (*path, "inputs"), empty=True)
        for ref in refs:
            text(ref, (*path, "inputs"))
        if len(set(refs)) != len(refs):
            fail("DUPLICATE_TRACE_INPUT", (*path, "inputs"))
        if kind in ("asserted", "axiom") and refs:
            fail("INVALID_TRACE_LEAF", path)
        if kind in ("rdfs", "rule") and not refs:
            fail("MISSING_TRACE_INPUT", path)
        if kind == "rule":
            text(node["ruleId"], (*path, "ruleId"))
        elif node["ruleId"] is not None:
            fail("INVALID_RULE_REFERENCE", (*path, "ruleId"))
        result[identity] = node
    visiting, visited = set(), set()

    def visit(identity: str) -> None:
        if identity not in result:
            fail("MISSING_TRACE_NODE", ("trace",))
        if identity in visiting:
            fail("CYCLIC_TRACE", ("trace",))
        if identity in visited:
            return
        visiting.add(identity)
        for parent in result[identity]["inputs"]:
            visit(parent)
        visiting.remove(identity)
        visited.add(identity)

    for identity in result:
        visit(identity)
    # Copy after checking to prevent mutation of the caller's data through this result.
    import copy

    return copy.deepcopy(result)


def compare_derivations(previous: object, current: object) -> dict:
    """Show additions, withdrawals and changed supports, including multiple supports."""
    before, after = validate_trace(previous), validate_trace(current)

    def outputs(nodes: dict) -> dict[tuple, set[str]]:
        result: dict[tuple, set[str]] = {}
        memo: dict[str, str] = {}
        for node in nodes.values():
            if node["kind"] not in ("rule", "rdfs"):
                continue
            statement = tuple(node["statement"])

            # Trace IDs can change between runs. Compare actual ancestor contents.
            def ancestry(identity: str) -> str:
                if identity in memo:
                    return memo[identity]
                item = nodes[identity]
                content = (
                    item["kind"],
                    tuple(item["statement"]),
                    item["ruleId"] or "",
                    tuple(sorted(ancestry(parent) for parent in item["inputs"])),
                )
                memo[identity] = hashlib.sha256(json.dumps(content).encode()).hexdigest()
                return memo[identity]

            result.setdefault(statement, set()).add(ancestry(node["id"]))
        return result

    old, new = outputs(before), outputs(after)
    return {
        "added": sorted(new.keys() - old.keys()),
        "withdrawn": sorted(old.keys() - new.keys()),
        "changed": sorted(s for s in old.keys() & new.keys() if old[s] != new[s]),
        "unchanged": sorted(s for s in old.keys() & new.keys() if old[s] == new[s]),
    }
