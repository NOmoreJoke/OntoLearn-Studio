"""Fresh-process compatibility and absence of parser/global-policy side effects."""

import hashlib
import json
import subprocess
import sys

from test_quality_profile_terms import FIXTURES


def test_pure_import_and_lazy_api_identity():
    script = """
import logging, sys, decimal
before_filters=tuple(logging.getLogger("rdflib.term").filters)
before_limit=sys.get_int_max_str_digits()
before_context=decimal.getcontext().copy()
import ontolearn_engine.quality as quality
from ontolearn_engine.quality import rule_firing
assert "rdflib" not in sys.modules
assert "ontolearn_engine.quality.rdf_terms" not in sys.modules
assert tuple(logging.getLogger("rdflib.term").filters)==before_filters
assert sys.get_int_max_str_digits()==before_limit
assert str(decimal.getcontext())==str(before_context)
assert quality.__all__==[
    "DefinitionError", "ValidatedDefinition", "build_plan", "validate_definition"
]
from ontolearn_engine.quality import definitions, planning
assert quality.DefinitionError is definitions.DefinitionError
assert quality.ValidatedDefinition is definitions.ValidatedDefinition
assert quality.validate_definition is definitions.validate_definition
assert quality.build_plan is planning.build_plan
assert quality.build_plan is quality.build_plan
try: quality.unknown
except AttributeError: pass
else: raise AssertionError("unknown export")
print("pure import and lazy identities passed")
"""
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=15
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "pure import and lazy identities passed"


def test_independent_fixture_manifest():
    manifest = json.loads((FIXTURES / "manifest.json").read_text())
    assert manifest["profile"] == "OntoLearn-rule-comparison-profile/1"
    assert len(manifest["files"]) == 5
    for entry in manifest["files"]:
        data = (FIXTURES / entry["path"]).read_bytes()
        assert len(data) == entry["bytes"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
