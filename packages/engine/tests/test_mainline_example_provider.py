"""Trusted named-resource reads from an explicit controlled staged bundle."""

import hashlib
import json
import os
import subprocess
import sys

import pytest
from ontolearn_engine.project.mainline import ExampleResourceFault, make_example_provider
from ontolearn_engine.project.project_lifecycle import EXAMPLE_ID, EXAMPLE_INPUT_SHA256
from test_mainline_example_create import RESOURCE


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / "equipment-maintenance"
    root.mkdir()
    (root / "load-input.json").write_bytes(RESOURCE)
    manifest = {
        "exampleProviderManifestVersion": 1,
        "exampleId": EXAMPLE_ID,
        "input": {
            "path": "load-input.json",
            "bytes": len(RESOURCE),
            "sha256": EXAMPLE_INPUT_SHA256,
        },
    }
    raw = (
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    (root / "t01-provider.json").write_bytes(raw)
    return root, hashlib.sha256(raw).hexdigest()


def load(provider, **overrides):
    return provider.load(
        **({"example_id": EXAMPLE_ID, "input_digest": EXAMPLE_INPUT_SHA256} | overrides)
    )


def test_exact_controlled_bundle_returns_only_pinned_input_and_never_changes_source(bundle):
    root, pin = bundle
    before = {path.name: path.read_bytes() for path in root.iterdir()}
    provider = make_example_provider(root=root, manifest_sha256=pin)
    assert load(provider) == RESOURCE
    assert {path.name: path.read_bytes() for path in root.iterdir()} == before


@pytest.mark.parametrize(
    "failure",
    [
        "missing-manifest",
        "changed-manifest",
        "oversized-manifest",
        "missing-input",
        "changed-input",
        "oversized-input",
        "symlink-input",
        "symlink-manifest",
        "symlink-root",
    ],
)
def test_bad_resource_is_fixed_failure_without_fallback_or_path_disclosure(bundle, failure):
    root, pin = bundle
    if failure == "symlink-root":
        link = root.parent / "alias"
        link.symlink_to(root, target_is_directory=True)
        root = link
    else:
        member = root / ("t01-provider.json" if "manifest" in failure else "load-input.json")
        if failure.startswith("missing"):
            member.unlink()
        elif failure.startswith("changed"):
            member.write_bytes(member.read_bytes() + b" ")
        elif failure.startswith("oversized"):
            member.write_bytes(b" " * (8193 if "manifest" in failure else len(RESOURCE) + 1))
        else:
            original = root.parent / "outside"
            original.write_bytes(member.read_bytes())
            member.unlink()
            member.symlink_to(original)
    provider = make_example_provider(root=root, manifest_sha256=pin)
    with pytest.raises(ExampleResourceFault) as error:
        load(provider)
    assert str(error.value) == "EXAMPLE_RESOURCE_UNAVAILABLE"


@pytest.mark.parametrize("overrides", [{"example_id": "other"}, {"input_digest": "0" * 64}])
def test_wire_identity_cannot_select_other_resource(bundle, overrides):
    root, pin = bundle
    with pytest.raises(ExampleResourceFault, match="^EXAMPLE_RESOURCE_UNAVAILABLE$"):
        load(make_example_provider(root=root, manifest_sha256=pin), **overrides)


def test_untrusted_or_relative_factory_input_is_not_a_resource_authority(bundle):
    root, pin = bundle
    with pytest.raises(ExampleResourceFault):
        make_example_provider(root=str(root), manifest_sha256=pin)
    with pytest.raises(ExampleResourceFault):
        make_example_provider(root=root.relative_to(root.anchor), manifest_sha256=pin)
    with pytest.raises(ExampleResourceFault):
        make_example_provider(root=root, manifest_sha256="invalid")


@pytest.mark.parametrize("member", ["t01-provider.json", "load-input.json"])
def test_fifo_is_rejected_without_waiting_for_a_writer(bundle, member):
    root, pin = bundle
    (root / member).unlink()
    os.mkfifo(root / member)
    # A bounded actual child keeps a broken open from hanging the test owner.
    script = """
import sys
from pathlib import Path
from ontolearn_engine.project.mainline import ExampleResourceFault, make_example_provider
try:
    make_example_provider(root=Path(sys.argv[1]),manifest_sha256=sys.argv[2]).load(
        example_id='equipment-maintenance',input_digest=sys.argv[3])
except ExampleResourceFault as error:
    assert str(error)=='EXAMPLE_RESOURCE_UNAVAILABLE'
else:
    raise AssertionError('FIFO accepted')
"""
    process = subprocess.run(
        [sys.executable, "-I", "-B", "-c", script, str(root), pin, EXAMPLE_INPUT_SHA256],
        capture_output=True,
        timeout=5,
        check=False,
    )
    assert process.returncode == 0, process.stderr.decode()
    assert process.stdout == process.stderr == b""
