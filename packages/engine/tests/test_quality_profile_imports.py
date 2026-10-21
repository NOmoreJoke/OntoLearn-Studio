"""Fresh-process compatibility and absence of parser/global-policy side effects."""

import hashlib
import json
import subprocess
import sys

from test_quality_profile_terms import FIXTURES


def test_partial_pure_import_and_unavailable_lazy_api():
    script = """
import logging, sys, decimal, importlib.util
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
assert importlib.util.find_spec("ontolearn_engine.quality.definitions") is None
assert importlib.util.find_spec("ontolearn_engine.quality.planning") is None
for name in quality.__all__:
    try: getattr(quality, name)
    except ImportError: pass
    else: raise AssertionError("unapproved lazy API unexpectedly callable")
    assert name not in vars(quality)
try: quality.unknown
except AttributeError: pass
else: raise AssertionError("unknown export")
print("partial pure import and unavailable lazy API passed")
"""
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=15
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "partial pure import and unavailable lazy API passed"


def test_independent_fixture_manifest():
    manifest = json.loads((FIXTURES / "manifest.json").read_text())
    assert manifest["profile"] == "OntoLearn-rule-comparison-profile/1"
    assert len(manifest["files"]) == 5
    for entry in manifest["files"]:
        data = (FIXTURES / entry["path"]).read_bytes()
        assert len(data) == entry["bytes"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
