"""Partial package adopts canonical submodules, never legacy lazy services."""

import hashlib
import importlib
import json
from pathlib import Path

from ontolearn_engine.quality.rule_firing import RuleSpec
from ontolearn_engine.resources import IMPLEMENTATION, LOCK_FILE, semantic_identity
from ontolearn_engine.semantic import SEMANTICS_VERSION
from ontolearn_engine.semantic_turtle import parse_profile_graph

ROOT = Path(__file__).resolve().parents[3]


def test_fixed_readonly_sources_fixtures_and_old_tests_remain_exact_bytes():
    source = ROOT / "docs/reviews/I05/profile-integration/I05-profile-P1-fixed-inputs.json.raw"
    inputs = json.loads(source.read_bytes())["inputs"]
    seven = json.loads(
        (source.parent / "T05-profile-iri-approved-seven-inputs.json.raw").read_bytes()
    )
    replacements = {item["path"]: item for item in seven["modules"]}
    checked = []
    for item in inputs:
        if item["kind"] in {
            "T05_mechanism_readonly_consumer",
            "T05_fixed_profile_fixture_readonly_consumer",
            "I05_legacy_tests_immutable_adoption",
        }:
            item = replacements.get(item["path"], item)
            raw = (ROOT / item["path"]).read_bytes()
            assert len(raw) == item["bytes"]
            assert hashlib.sha256(raw).hexdigest() == item["sha256"]
            checked.append(item["path"])
    assert len(checked) == 23


def test_actual_identity_modes_keep_default_and_use_real_lock():
    lock = hashlib.sha256(LOCK_FILE.read_bytes()).hexdigest()
    assert IMPLEMENTATION["executionSemanticsVersion"] == "i04-infrastructure-v1"
    assert SEMANTICS_VERSION == "i05-finite-6"
    assert semantic_identity()["executionSemanticsVersion"] == "i05-finite-6"
    assert semantic_identity(profile=True)["executionSemanticsVersion"] == "i05-finite-7"
    assert all(
        value["dependencyLockHash"] == lock
        for value in (IMPLEMENTATION, semantic_identity(), semantic_identity(profile=True))
    )
    copy = semantic_identity(profile=True)
    copy["dependencyLockHash"] = "forged"
    assert IMPLEMENTATION["dependencyLockHash"] == lock


def test_one_canonical_class_and_no_legacy_service_side_effect():
    module = importlib.import_module("ontolearn_engine.quality.rule_firing")
    assert module.RuleSpec is RuleSpec
    assert RuleSpec.__module__ == "ontolearn_engine.quality.rule_firing"
    # W3a union port: definitions/planning are now first-class FR-504/505
    # modules with their own tests, so earlier tests may import them in this
    # process. Keep the original no-side-effect guarantee order-independent:
    # the fired-rule engine source must never import the editor-language
    # modules (checked statically, independent of test execution order).
    import ast
    import inspect

    imported = set()
    for node in ast.walk(ast.parse(inspect.getsource(module))):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert not imported & {
        "ontolearn_engine.quality.definitions",
        "ontolearn_engine.quality.planning",
        ".definitions",
        ".planning",
    }


def test_profile_does_not_change_process_literal_normalization():
    import rdflib

    before = rdflib.NORMALIZE_LITERALS
    parse_profile_graph(
        '<urn:s> <urn:p> "001"^^<http://www.w3.org/2001/XMLSchema#integer> .', base_uri="urn:test:"
    )
    assert rdflib.NORMALIZE_LITERALS is before
