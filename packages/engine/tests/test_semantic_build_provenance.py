"""Private verifier unit boundaries; no real semantic/native/package execution."""

from __future__ import annotations

import copy
import importlib.machinery
import importlib.util
import json
import marshal
import os
import runpy
import shutil
import struct
import subprocess
import sys
import types
import uuid
import zlib
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from ontolearn_engine import semantic_build_provenance as p

REPOSITORY = Path(__file__).resolve().parents[3]
CONTRACT_RAW = (REPOSITORY / p.CONTRACT_SOURCE).read_bytes()
CONTRACT = json.loads(CONTRACT_RAW)


class CodeLoader:
    def __init__(self, code):
        self.code = code
        self.calls = []

    def get_code(self, name):
        self.calls.append(name)
        return self.code


def write(root, relative, raw):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return {"path": relative, "bytes": len(raw), "sha256": p._sha(raw)}


def fake_module(monkeypatch, root, name, path, code):
    module = types.ModuleType(name)
    loader = CodeLoader(code)
    module.__file__ = str(root / path)
    module.__spec__ = importlib.machinery.ModuleSpec(name, loader, origin=module.__file__)
    module.__loader__ = loader
    monkeypatch.setitem(sys.modules, name, module)
    return module


def make_case(monkeypatch, engine):
    for name in tuple(sys.modules):
        if any(name == prefix or name.startswith(prefix + ".") for prefix in p.FIXED_DISTRIBUTIONS):
            monkeypatch.delitem(sys.modules, name)
    root = engine / "_internal"
    root.mkdir(parents=True)
    launcher = engine / "ontolearn-engine"
    launcher.write_bytes(b"unit-test launcher, never executed")
    launcher.chmod(0o755)
    modules, code_objects, suppliers = {}, {}, []
    for name in p.SUPPLIER_MODULES + p.PRIVATE_MODULES:
        path = name.replace(".", "/") + (
            "/__init__.py" if name in ("ontolearn_engine", "ontolearn_engine.quality") else ".py"
        )
        raw = b"def observed():\n    return ('unchanged', 3)\n"
        row = {
            **write(root, path, raw),
            "module": name,
            "codeSha256": p._code_sha(p._compiled(raw)),
        }
        code_objects[name] = p._compiled(raw)
        module = fake_module(monkeypatch, root, name, path, code_objects[name])
        if name in p.SUPPLIER_MODULES:
            suppliers.append(row)
            modules[name] = module
    private = [
        {
            **p._identity(root, name.replace(".", "/") + ".py"),
            "module": name,
            "codeSha256": p._code_sha(code_objects[name]),
        }
        for name in p.PRIVATE_MODULES
    ]
    resources = [write(root, path, (path + " unit-resource").encode()) for path in p.PUBLIC_PATHS]
    for row in p.FIXED_INPUTS:
        source = REPOSITORY / "packages/engine/src" / row["path"]
        target = root / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    lock = {**write(root, "provenance/uv.lock", b"unit locked inputs"), "path": "uv.lock"}
    write(root, p.CONTRACT_BUNDLED, CONTRACT_RAW)
    distributions = []
    for name, version in p.FIXED_DISTRIBUTIONS.items():
        info = f"{name}-{version}.dist-info"
        metadata = write(
            root,
            info + "/METADATA",
            (
                f"Name: {name}\nVersion: {version}\nLicense-File: LICENSE\n"
                + ("License-File: AUTHORS.rst\n" if name == "html5rdf" else "")
            ).encode(),
        )
        licenses = [write(root, info + "/LICENSE", b"unit license")]
        if name == "html5rdf":
            licenses.append(write(root, info + "/AUTHORS.rst", b"unit attribution"))
        raw = b"VERSION = 'unit-only'\n"
        file_path = name + "/__init__.py"
        code = p._compiled(raw)
        python = {
            **write(root, file_path, raw),
            "kind": "python",
            "module": name,
            "codeSha256": p._code_sha(code),
        }
        fake_module(monkeypatch, root, name, file_path, code)
        code_objects[name] = code
        data = {
            **write(root, name + "/data.txt", b"unit data"),
            "kind": "data",
            "module": None,
            "codeSha256": None,
        }
        files = [python, data]
        if name == "wcwidth":
            files.append(
                {
                    **write(root, name + "/_wcwidth_c.abi3.so", b"unit-not-native-code"),
                    "kind": "native",
                    "module": "wcwidth._wcwidth_c",
                    "codeSha256": None,
                }
            )
        distributions.append(
            {
                "name": name,
                "version": version,
                "metadata": metadata,
                "licenses": licenses,
                "files": files,
            }
        )
    library = write(root, "libpython3.12.dylib", b"unit-not-a-runtime-library")
    python = {
        **p._python_identity(),
        "buildExecutable": {"bytes": 1, "sha256": p._sha(b"x")},
        "buildSharedLibrary": {
            "name": library["path"],
            "bytes": library["bytes"],
            "sha256": library["sha256"],
        },
    }
    manifest = {
        "format": "i05-private-build-provenance/1",
        "source": {"commit": "a" * 40, "tree": "b" * 40},
        "contract": {
            "path": p.CONTRACT_SOURCE,
            "bytes": len(CONTRACT_RAW),
            "sha256": p.CONTRACT_SHA256,
        },
        "python": python,
        "codeAlgorithm": p.ALGORITHM,
        "suppliers": suppliers,
        "privateModules": private,
        "entrypoint": {"path": "packages/engine/entrypoint.py", "bytes": 1, "sha256": p._sha(b"e")},
        "publicResources": resources,
        "inputs": copy.deepcopy(list(p.FIXED_INPUTS)),
        "lock": lock,
        "distributions": distributions,
    }
    expected = {key: copy.deepcopy(manifest[key]) for key in ("publicResources", "inputs", "lock")}
    expected["suppliers"] = [
        {key: row[key] for key in ("module", "path", "bytes", "sha256")} for row in suppliers
    ]
    expected["distributions"] = dict(p.FIXED_DISTRIBUTIONS)
    case = types.SimpleNamespace(
        root=root,
        engine=engine,
        manifest=manifest,
        expectations=expected,
        modules=modules,
        codes=code_objects,
    )

    def refresh():
        raw = p._canonical(manifest)
        write(root, p.PROVENANCE_BUNDLED, raw)
        code_objects[p.ANCHOR] = p._compiled(p._anchor_source(p._sha(raw)))
        return raw

    case.refresh = refresh
    refresh()
    anchor_loader = CodeLoader(None)

    def get_anchor(name):
        if name != p.ANCHOR:
            raise AssertionError("unit preflight attempted unrelated module discovery")
        anchor_loader.code = code_objects[p.ANCHOR]
        return importlib.machinery.ModuleSpec(
            name, anchor_loader, origin=str(root / (p.ANCHOR + ".py"))
        )

    monkeypatch.setattr(p.importlib.util, "find_spec", get_anchor)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(root), raising=False)
    case.load = lambda: p.load_frozen_provenance(expectations=expected)
    case.anchor_loader = anchor_loader
    return case


@pytest.fixture
def case(monkeypatch, tmp_path):
    return make_case(monkeypatch, tmp_path / "engine")


def fault(suffix):
    return pytest.raises(p.BuildProvenanceFault, match="^BUILD_PROVENANCE_" + suffix + "$")


def distribution_module_snapshot():
    return {
        name: module
        for name, module in sys.modules.items()
        if name.split(".", 1)[0] in p.FIXED_DISTRIBUTIONS
    }


def seed_inherited_distributions(monkeypatch):
    near_names = {}
    for prefix in p.FIXED_DISTRIBUTIONS:
        for name in (prefix, prefix + ".child", prefix + ".child.deep"):
            monkeypatch.setitem(sys.modules, name, types.ModuleType(name))
        monkeypatch.setitem(sys.modules, prefix + ".unavailable", None)
        for name in (prefix + "_neighbor", "outside_" + prefix):
            near_names[name] = types.ModuleType(name)
            monkeypatch.setitem(sys.modules, name, near_names[name])
    name = "wcwidth._wcwidth_c"
    monkeypatch.setitem(sys.modules, name, types.ModuleType(name))
    return distribution_module_snapshot(), near_names


def assert_synthetic_distribution_baseline(value, near_names):
    current = distribution_module_snapshot()
    assert set(current) == set(p.FIXED_DISTRIBUTIONS)
    assert all(type(module) is types.ModuleType for module in current.values())
    assert all(sys.modules[name] is module for name, module in near_names.items())
    result = p.verify_loaded_modules(value.load(), value.modules)
    assert {row["module"] for row in result["loadedDistributionModules"]} == set(
        p.FIXED_DISTRIBUTIONS
    )
    assert len(result["supplierAndPrivateModules"]) == 24
    with fault("NATIVE_UNAVAILABLE"):
        p.verify_native_extension(value.load())


@pytest.mark.parametrize("setup_fails", [False, True])
def test_make_case_isolates_all_distribution_names_and_restores_exact_objects(
    monkeypatch, tmp_path, setup_fails
):
    before, near_names = seed_inherited_distributions(monkeypatch)

    def fail_fake_module(*_args):
        assert distribution_module_snapshot() == {}
        assert all(sys.modules[name] is module for name, module in near_names.items())
        raise RuntimeError("synthetic setup failure")

    if setup_fails:
        with pytest.raises(RuntimeError, match="^synthetic setup failure$"):
            with pytest.MonkeyPatch.context() as isolated:
                isolated.setattr(sys.modules[__name__], "fake_module", fail_fake_module)
                make_case(isolated, tmp_path / "engine")
    else:
        with pytest.MonkeyPatch.context() as isolated:
            value = make_case(isolated, tmp_path / "engine")
            assert_synthetic_distribution_baseline(value, near_names)

    after = distribution_module_snapshot()
    assert set(after) == set(before)
    assert all(after[name] is module for name, module in before.items())
    assert all(sys.modules[name] is module for name, module in near_names.items())


def test_case_fixture_isolates_inherited_distribution_names(monkeypatch, request):
    _before, near_names = seed_inherited_distributions(monkeypatch)
    # Request only after seeding: pytest must construct the real fixture in this environment.
    value = request.getfixturevalue("case")
    assert_synthetic_distribution_baseline(value, near_names)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"a":1,"a":2}',
        b'{"a":{"b":1,"b":2}}',
        b'{"x":NaN}',
        b'{"x":Infinity}',
        b'{"x":1e999}',
        b'"\\ud800"',
        b'"\\u0000"',
        b"\xef\xbb\xbf{}",
        b"\xff",
    ],
)
def test_strict_json_rejects_ambiguous_or_nonfinite_values(raw):
    with fault("JSON_INVALID"):
        p._json(raw, 1000)


def test_parser_read_depth_and_schema_roles_are_bounded():
    with fault("LIMIT_EXCEEDED"):
        p._json(b"[]", 1)
    with fault("LIMIT_EXCEEDED"):
        p._json(b"[" * 18 + b"0" + b"]" * 18, 1000)
    for value in (True, 1.0, -1):
        with fault("SCHEMA_INVALID"):
            p._schema(value, {"type": "integer", "minimum": 0, "maximum": 5})


@pytest.mark.parametrize(
    "value", ["../a", "/a", "a//b", "a/./b", "a\\b", "C:/a", "a\x00b", "e\u0301"]
)
def test_paths_reject_noncanonical_or_escaping_spellings(value):
    with fault("PATH_INVALID"):
        p._path(value)


def test_path_resolution_rejects_outside_symlink(tmp_path):
    inside = tmp_path / "inside"
    inside.mkdir()
    outside = tmp_path / "secret"
    outside.write_bytes(b"outside")
    (inside / "link").symlink_to(outside)
    with fault("PATH_ESCAPE"):
        p._inside(inside, "link")


def test_preflight_verifies_identity_without_executing_target_or_anchor(case, monkeypatch):
    monkeypatch.setattr(
        p.importlib, "import_module", lambda *_a, **_k: pytest.fail("target import")
    )
    evidence = case.load()
    assert type(evidence) is p.FrozenBuildEvidence
    assert type(evidence._manifest) is bytes
    assert case.anchor_loader.calls == [p.ANCHOR]
    assert p._sha(evidence._manifest) == p._sha((case.root / p.PROVENANCE_BUNDLED).read_bytes())
    with pytest.raises(FrozenInstanceError):
        evidence._root = Path("/other")
    with fault("MODE_INVALID"):
        p.FrozenBuildEvidence()


@pytest.mark.parametrize(
    "field", ["missing", "extra", "duplicateSupplier", "wrongOrder", "wrongInput", "wrongVersion"]
)
def test_expectations_are_exact_and_complete(case, field):
    if field == "missing":
        del case.expectations["lock"]
    elif field == "extra":
        case.expectations["approval"] = True
    elif field == "duplicateSupplier":
        case.expectations["suppliers"][-1] = case.expectations["suppliers"][0]
    elif field == "wrongOrder":
        case.expectations["publicResources"].reverse()
    elif field == "wrongInput":
        case.expectations["inputs"][0]["sha256"] = "0" * 64
    else:
        case.expectations["distributions"]["wcwidth"] = "0.9.3"
    with fault("SCHEMA_INVALID"):
        case.load()


def test_expected_source_pin_change_does_not_rewrite_manifest(case):
    case.expectations["suppliers"][0]["sha256"] = "0" * 64
    with fault("IDENTITY_MISMATCH"):
        case.load()


@pytest.mark.parametrize(
    "kind", ["resource", "input", "lock", "metadata", "license", "data", "contract"]
)
def test_tampered_actual_resources_are_rejected(case, kind):
    paths = {
        "resource": p.PUBLIC_PATHS[0],
        "input": p.FIXED_INPUTS[0]["path"],
        "lock": "provenance/uv.lock",
        "metadata": case.manifest["distributions"][0]["metadata"]["path"],
        "license": case.manifest["distributions"][0]["licenses"][0]["path"],
        "data": "pyparsing/data.txt",
        "contract": p.CONTRACT_BUNDLED,
    }
    (case.root / paths[kind]).write_bytes(b"tampered")
    expected = {
        "resource": "RESOURCE_MISMATCH",
        "input": "RESOURCE_MISMATCH",
        "lock": "LOCK_MISMATCH",
        "metadata": "DISTRIBUTION_MISMATCH",
        "license": "DISTRIBUTION_MISMATCH",
        "data": "DISTRIBUTION_MISMATCH",
        "contract": "CONTRACT_MISMATCH",
    }[kind]
    with fault(expected):
        case.load()


def test_missing_declared_license_is_not_covered_by_other_license(case):
    dist = case.manifest["distributions"][-1]
    dist["licenses"] = dist["licenses"][:1]
    case.refresh()
    with fault("DISTRIBUTION_MISMATCH"):
        case.load()


@pytest.mark.parametrize("field", ["version", "cacheTag", "soabi", "bytecodeMagicHex", "optimize"])
def test_exact_python_identity_required(case, field):
    case.manifest["python"][field] = 1 if field == "optimize" else "different"
    case.refresh()
    with fault(
        "SCHEMA_INVALID" if field in ("optimize", "bytecodeMagicHex") else "PYTHON_MISMATCH"
    ):
        case.load()


def test_anchor_code_and_unknown_loader_are_rejected_without_execution(case):
    case.codes[p.ANCHOR] = p._compiled(b"raise RuntimeError('must never execute')")
    with fault("ANCHOR_MISMATCH"):
        case.load()
    case.codes[p.ANCHOR] = None
    with fault("LOADER_UNAVAILABLE"):
        case.load()


def test_code_normalization_changes_only_filenames_and_nested_filenames():
    raw = b"def f():\n    return lambda: 17\n"
    first = compile(raw, "/first/source.py", "exec", flags=0, dont_inherit=True, optimize=0)
    second = compile(raw, "/other/source.py", "exec", flags=0, dont_inherit=True, optimize=0)
    assert p._code_sha(first) == p._code_sha(second)
    assert p._code_sha(first) != p._code_sha(first.replace(co_firstlineno=5))
    assert p._code_sha(first) != p._code_sha(first.replace(co_flags=first.co_flags | 0x1000000))
    assert p._code_sha(first) != p._code_sha(p._compiled(raw.replace(b"17", b"18")))


def test_loaded_module_positive_is_limited_and_has_no_root_approval(case):
    evidence = case.load()
    result = p.verify_loaded_modules(evidence, case.modules)
    assert result["rootApproval"] == "unknown"
    assert result["semanticParity"] == "unknown"
    assert result["nativeSourceByteEquivalence"] == "unknown"
    assert len(result["supplierAndPrivateModules"]) == 24
    assert {r["module"] for r in result["loadedDistributionModules"]} == set(p.FIXED_DISTRIBUTIONS)
    assert result["entrypointDomain"] == "external-launcher-PYZ-binding-only"


@pytest.mark.parametrize(
    "kind", ["name", "specName", "file", "origin", "sysModules", "loader", "code"]
)
def test_actual_loader_and_module_identity_mismatch_rejected(case, monkeypatch, kind):
    evidence = case.load()
    name = p.SUPPLIER_MODULES[0]
    module = case.modules[name]
    if kind == "name":
        module.__name__ = "foreign"
    elif kind == "specName":
        module.__spec__.name = "foreign"
    elif kind == "file":
        module.__file__ = "/outside/module.py"
    elif kind == "origin":
        module.__spec__.origin = "/outside/module.py"
    elif kind == "sysModules":
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))
    elif kind == "loader":
        module.__spec__.loader = object()
        module.__loader__ = module.__spec__.loader
    else:
        module.__spec__.loader.code = p._compiled(b"changed = True")
    with fault(
        "LOADER_UNAVAILABLE"
        if kind == "loader"
        else "LOADER_MISMATCH"
        if kind == "code"
        else "MODULE_MISMATCH"
    ):
        p.verify_loaded_modules(evidence, case.modules)


def test_evidence_is_context_bound_and_not_a_dict_approval(case, monkeypatch, tmp_path):
    evidence = case.load()
    with fault("MODE_INVALID"):
        p.verify_loaded_modules({"rootApproved": True}, case.modules)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path))
    with fault("PYTHON_MISMATCH"):
        p.verify_loaded_modules(evidence, case.modules)


def test_loaded_distribution_module_not_in_frozen_inventory_rejected(case, monkeypatch):
    evidence = case.load()
    p.verify_loaded_modules(evidence, case.modules)
    monkeypatch.setitem(sys.modules, "pyshacl.unrecorded", types.ModuleType("pyshacl.unrecorded"))
    with fault("MODULE_MISMATCH"):
        p.verify_loaded_modules(evidence, case.modules)


def test_native_observation_never_imports_or_claims_source_equivalence(case, monkeypatch):
    evidence = case.load()
    with fault("NATIVE_UNAVAILABLE"):
        p.verify_native_extension(evidence)
    name = "wcwidth._wcwidth_c"
    path = case.root / "wcwidth/_wcwidth_c.abi3.so"
    module = types.ModuleType(name)
    module.__file__ = str(path)
    loader = importlib.machinery.ExtensionFileLoader(name, str(path))
    module.__loader__ = loader
    module.__spec__ = importlib.machinery.ModuleSpec(name, loader, origin=str(path))
    monkeypatch.setitem(sys.modules, name, module)
    # This is a constructed ModuleType/loader unit fixture, not a native import proof.
    result = p.verify_native_extension(evidence)
    assert result["nativeSourceByteEquivalence"] == "unknown"
    assert result["rootApproval"] == "unknown"
    path.write_bytes(b"signed artifact fixture differs")
    result = p.verify_native_extension(evidence)
    assert result["sourceByteMatch"] is False
    module.__spec__.origin = "/outside/native.so"
    with fault("NATIVE_MISMATCH"):
        p.verify_native_extension(evidence)


def test_fake_native_loader_does_not_fall_back_to_python(case, monkeypatch):
    evidence = case.load()
    fake_module(
        monkeypatch,
        case.root,
        "wcwidth._wcwidth_c",
        "wcwidth/_wcwidth_c.abi3.so",
        p._compiled(b"pass"),
    )
    with fault("NATIVE_MISMATCH"):
        p.verify_native_extension(evidence)


def make_binding(case, target):
    raw = (case.root / p.PROVENANCE_BUNDLED).read_bytes()
    binding = {
        "format": "i05-private-artifact-binding/1",
        "provenanceSha256": p._sha(raw),
        "sourceCommit": case.manifest["source"]["commit"],
        "artifactDomain": "complete-engine-directory",
        "launcher": "ontolearn-engine",
        "entries": p._inventory_artifact(case.engine),
        "rootApproved": False,
    }
    target.write_bytes(p._canonical(binding))
    return binding, p._sha(target.read_bytes())


def test_external_binding_requires_expected_digest_and_complete_directory(case, tmp_path):
    target = tmp_path / "root-frozen-binding.json"
    _binding, digest = make_binding(case, target)
    with fault("EXTERNAL_BINDING_REQUIRED"):
        p.verify_external_binding(target, case.engine, expected_sha256="")
    with fault("EXTERNAL_BINDING_MISMATCH"):
        p.verify_external_binding(target, case.engine, expected_sha256="0" * 64)
    result = p.verify_external_binding(target, case.engine, expected_sha256=digest)
    assert result["inventoryVerified"] is True
    assert "no run executed" in result["rootApproval"]
    (case.root / "new-unlisted-file").write_bytes(b"extra")
    with fault("ARTIFACT_MISMATCH"):
        p.verify_external_binding(target, case.engine, expected_sha256=digest)


def test_self_replaced_anchor_and_manifest_do_not_bypass_original_external_digest(case, tmp_path):
    target = tmp_path / "root-binding.json"
    _binding, digest = make_binding(case, target)
    case.manifest["source"]["commit"] = "c" * 40
    case.refresh()
    with fault("ARTIFACT_MISMATCH"):
        p.verify_external_binding(target, case.engine, expected_sha256=digest)


@pytest.mark.parametrize("kind", ["missingHash", "wrongNull", "extra", "duplicate", "launcherMode"])
def test_binding_schema_and_role_rules_are_fail_closed(case, tmp_path, kind):
    target = tmp_path / "binding.json"
    binding, _digest = make_binding(case, target)
    row = next(r for r in binding["entries"] if r["path"] == "ontolearn-engine")
    if kind == "missingHash":
        row["sha256"] = None
    elif kind == "wrongNull":
        row["target"] = "foreign"
    elif kind == "extra":
        binding["approved"] = True
    elif kind == "duplicate":
        binding["entries"].append(copy.deepcopy(row))
    else:
        row["mode"] = 0
    target.write_bytes(p._canonical(binding))
    with fault("ARTIFACT_MISMATCH" if kind == "launcherMode" else "SCHEMA_INVALID"):
        p.verify_external_binding(target, case.engine, expected_sha256=p._sha(target.read_bytes()))


def test_artifact_symlink_policies_and_special_files(case, tmp_path):
    (case.root / "safe-link").symlink_to("pyparsing/data.txt")
    rows = p._inventory_artifact(case.engine)
    assert any(r["path"] == "_internal/safe-link" and r["kind"] == "symlink" for r in rows)
    (case.root / "safe-link").unlink()
    outside = tmp_path / "outside"
    outside.write_bytes(b"outside")
    (case.root / "escape").symlink_to(outside)
    with fault("PATH_ESCAPE"):
        p._inventory_artifact(case.engine)
    (case.root / "escape").unlink()
    os.mkfifo(case.root / "not-a-file")
    with fault("PATH_INVALID"):
        p._inventory_artifact(case.engine)


def test_artifact_collision_and_caps(case, monkeypatch):
    (case.root / "A").write_bytes(b"one")
    (case.root / "a").write_bytes(b"two")
    # This host may use case-insensitive storage; schema collisions are still rejected.
    with fault("SCHEMA_INVALID"):
        p._unique([{"path": "A"}, {"path": "a"}])
    monkeypatch.setattr(p, "ENTRY_CAP", 2)
    with fault("LIMIT_EXCEEDED"):
        p._inventory_artifact(case.engine)


def test_prepare_writes_fresh_inputs_without_running_pyinstaller(case, monkeypatch, tmp_path):
    repository = tmp_path / "repo"
    write(repository, p.CONTRACT_SOURCE, CONTRACT_RAW)
    output = repository / "build/i05-provenance" / str(uuid.uuid4())
    monkeypatch.setattr(p, "_git", lambda *_a: b"")
    monkeypatch.setattr(p, "_collect_build_manifest", lambda *_a: case.manifest)
    result = p.prepare_build(repository, output)
    assert set(result) == {"provenancePath", "contractPath", "generatedDir", "anchorPath"}
    assert Path(result["contractPath"]).read_bytes() == CONTRACT_RAW
    assert Path(result["anchorPath"]).read_bytes() == p._anchor_source(
        p._sha(Path(result["provenancePath"]).read_bytes())
    )
    with fault("BUILD_OUTPUT_EXISTS"):
        p.prepare_build(repository, output)


def test_prepare_rejects_dirty_sources_before_output_creation(monkeypatch, tmp_path):
    repository = tmp_path / "repo"
    write(repository, p.CONTRACT_SOURCE, CONTRACT_RAW)
    output = repository / "build/i05-provenance" / str(uuid.uuid4())
    monkeypatch.setattr(p, "_git", lambda *_a: b"packages/engine/src/dirty.py\n")
    with fault("BUILD_INPUT_DIRTY"):
        p.prepare_build(repository, output)
    assert not output.exists()
    with fault("BUILD_LAYOUT_INVALID"):
        p.prepare_build(repository, tmp_path / "outside")


def test_literal_pin_parser_never_imports_source():
    source = (
        b"raise RuntimeError('no execution')\n"
        b"SUPPLIER_PINS = (('m','x.py',1,'s'),)\nPUBLIC_RESOURCE_PINS = ()\n"
    )
    result = p._literal_pins(source)
    assert result["SUPPLIER_PINS"] == (("m", "x.py", 1, "s"),)
    with fault("SOURCE_MISMATCH"):
        p._literal_pins(b"SUPPLIER_PINS = dynamic()")


def test_finalize_audits_code_and_creates_immutable_unapproved_proposal(monkeypatch, tmp_path):
    repository = tmp_path / "repo"
    output = repository / "build/i05-provenance" / str(uuid.uuid4())
    case = make_case(monkeypatch, output / "dist/ontolearn-engine")
    provenance = output / "provenance"
    provenance.mkdir()
    shutil.copyfile(case.root / p.PROVENANCE_BUNDLED, provenance / Path(p.PROVENANCE_BUNDLED).name)
    shutil.copyfile(case.root / p.CONTRACT_BUNDLED, provenance / Path(p.CONTRACT_BUNDLED).name)

    class Archive:
        def extract(self, name):
            return case.codes[name]

    monkeypatch.setattr(p, "_archive_code", lambda _engine: Archive())
    result = p.finalize_build(repository, output, case.engine)
    assert set(result) == {"bindingPath", "bindingSha256", "engineDirectory", "provenanceSha256"}
    binding_path = Path(result["bindingPath"])
    assert not binding_path.is_relative_to(case.engine)
    assert json.loads(binding_path.read_bytes())["rootApproved"] is False
    assert p.verify_external_binding(
        binding_path, case.engine, expected_sha256=result["bindingSha256"]
    )["inventoryVerified"]
    with fault("BUILD_OUTPUT_EXISTS"):
        p.finalize_build(repository, output, case.engine)
    binding_path.unlink()
    library = case.root / case.manifest["python"]["buildSharedLibrary"]["name"]
    library_bytes = library.read_bytes()
    library.unlink()
    with fault("IDENTITY_MISMATCH"):
        p.finalize_build(repository, output, case.engine)
    library.write_bytes(library_bytes)
    case.codes[p.SUPPLIER_MODULES[0]] = p._compiled(b"changed = 1")
    with fault("ARCHIVE_MISMATCH"):
        p.finalize_build(repository, output, case.engine)


def test_error_is_always_fixed_and_never_leaks_path():
    assert str(p.BuildProvenanceFault("/secret/private/file")) == "BUILD_PROVENANCE_SCHEMA_INVALID"


@pytest.mark.parametrize("kind", ["extra", "missing", "boolByte", "metadataOwner", "nativeName"])
def test_manifest_rejects_incomplete_roles_and_cross_owner_paths(case, kind):
    if kind == "extra":
        case.manifest["approved"] = True
    elif kind == "missing":
        del case.manifest["privateModules"]
    elif kind == "boolByte":
        case.manifest["suppliers"][0]["bytes"] = True
    elif kind == "metadataOwner":
        case.manifest["distributions"][0]["metadata"]["path"] = "other.dist-info/METADATA"
    else:
        case.manifest["distributions"][6]["files"][-1]["module"] = "wcwidth.foreign"
    case.refresh()
    with fault("SCHEMA_INVALID"):
        case.load()


def test_contract_schema_and_fixed_error_list_match_the_executed_reader():
    assert p._sha(CONTRACT_RAW) == p.CONTRACT_SHA256
    assert set(CONTRACT["errorCodes"]) == {"BUILD_PROVENANCE_" + x for x in p._ERROR_SUFFIXES}
    assert p.FIXED_DISTRIBUTIONS == CONTRACT["fixedDistributions"]
    assert list(p.FIXED_INPUTS) == CONTRACT["fixedInputs"]


def test_false_frozen_carrier_is_rejected(case, monkeypatch):
    monkeypatch.setattr(sys, "frozen", 1)
    with fault("MODE_INVALID"):
        case.load()


def test_unconstructed_evidence_cannot_be_used_as_success(case):
    raw = object.__new__(p.FrozenBuildEvidence)
    with fault("MODE_INVALID"):
        p.verify_loaded_modules(raw, case.modules)


def test_loaded_code_is_rechecked_on_every_post_observer_call(case):
    evidence = case.load()
    p.verify_loaded_modules(evidence, case.modules)
    case.modules[p.SUPPLIER_MODULES[0]].__loader__.code = p._compiled(b"changed = 2")
    with fault("LOADER_MISMATCH"):
        p.verify_loaded_modules(evidence, case.modules)


def test_self_consistent_wrong_metadata_header_is_rejected(case):
    row = case.manifest["distributions"][0]
    row["metadata"] = write(case.root, row["metadata"]["path"], b"Name: foreign\nVersion: 3.3.3\n")
    case.refresh()
    with fault("DISTRIBUTION_MISMATCH"):
        case.load()


def test_metadata_and_license_caps_are_not_widened_to_general_file_cap(case):
    case.manifest["distributions"][0]["licenses"][0]["bytes"] = p.SMALL_CAP + 1
    case.refresh()
    with fault("SCHEMA_INVALID"):
        case.load()


def test_file_read_detects_changed_stat_not_just_expected_digest(tmp_path, monkeypatch):
    path = tmp_path / "input"
    path.write_bytes(b"stable")
    original = p.os.fstat
    count = 0

    def changed(fd):
        nonlocal count
        count += 1
        result = original(fd)
        if count == 2:
            return types.SimpleNamespace(
                st_dev=result.st_dev,
                st_ino=result.st_ino,
                st_size=result.st_size,
                st_mtime_ns=result.st_mtime_ns + 1,
            )
        return result

    monkeypatch.setattr(p.os, "fstat", changed)
    with fault("ARTIFACT_CHANGED"):
        p._read(path, 100)


def test_dist_inventory_reads_actual_record_files_and_declared_notice(tmp_path, monkeypatch):
    site = tmp_path / "env/lib/python3.12/site-packages"
    info = "html5rdf-1.2.1.dist-info"
    write(site, info + "/METADATA", b"Name: html5rdf\nVersion: 1.2.1\nLicense-File: AUTHORS.rst\n")
    write(site, info + "/LICENSE", b"license")
    write(site, info + "/AUTHORS.rst", b"notice")
    write(site, "html5rdf/__init__.py", b"VALUE = 1\n")
    write(site, "html5rdf/data.txt", b"data")

    class Distribution:
        version = "1.2.1"
        files = [
            info + "/METADATA",
            info + "/LICENSE",
            info + "/AUTHORS.rst",
            "html5rdf/__init__.py",
            "html5rdf/data.txt",
        ]

        def locate_file(self, path):
            return site / path

    monkeypatch.setattr(p.importlib.metadata, "distribution", lambda _name: Distribution())
    monkeypatch.setattr(p.sysconfig, "get_path", lambda _kind: str(site))
    monkeypatch.setattr(sys, "prefix", str(tmp_path / "env"))
    result = p._dist_inventory("html5rdf", "1.2.1")
    assert {r["path"] for r in result["licenses"]} == {info + "/LICENSE", info + "/AUTHORS.rst"}
    assert [(r["kind"], r["module"]) for r in result["files"]] == [
        ("python", "html5rdf"),
        ("data", None),
    ]
    (site / info / "AUTHORS.rst").unlink()
    with fault("DISTRIBUTION_MISMATCH"):
        p._dist_inventory("html5rdf", "1.2.1")


def test_literal_pin_shapes_fail_before_unpacking_untrusted_rows():
    for pins in (
        {"SUPPLIER_PINS": (), "PUBLIC_RESOURCE_PINS": ()},
        {"SUPPLIER_PINS": (("module",),) * 22, "PUBLIC_RESOURCE_PINS": ()},
    ):
        with fault("SOURCE_MISMATCH"):
            p._validate_literal_rows(pins)


def test_missing_external_binding_is_fixed_rejection_without_path_disclosure(case, tmp_path):
    with fault("EXTERNAL_BINDING_REQUIRED"):
        p.verify_external_binding(
            tmp_path / "missing-private-file", case.engine, expected_sha256="0" * 64
        )


def test_missing_build_roots_are_fixed_rejections(tmp_path):
    with fault("BUILD_LAYOUT_INVALID"):
        p.prepare_build(tmp_path / "missing", tmp_path / "outside")
    with fault("BUILD_LAYOUT_INVALID"):
        p.finalize_build(tmp_path / "missing", tmp_path / "outside", tmp_path / "engine")


def test_inventory_rejects_file_mode_change_before_hash(case, monkeypatch):
    original = p._hash_file

    def changed(path, expected_mode=None):
        path.chmod(0o600)
        return original(path, expected_mode)

    monkeypatch.setattr(p, "_hash_file", changed)
    with fault("ARTIFACT_CHANGED"):
        p._inventory_artifact(case.engine)


def test_build_archive_reader_is_imported_only_by_explicit_build_helper(monkeypatch, tmp_path):
    calls = []
    result = object()

    class Archive:
        def __init__(self, path):
            calls.append(("open", path))

        def open_embedded_archive(self, name):
            calls.append(("embedded", name))
            return result

    def build_only_import(name):
        calls.append(("import", name))
        assert name == "PyInstaller.archive.readers"
        return types.SimpleNamespace(CArchiveReader=Archive)

    monkeypatch.setattr(p.importlib, "import_module", build_only_import)
    assert p._archive_code(tmp_path) is result
    assert calls == [
        ("import", "PyInstaller.archive.readers"),
        ("open", str(tmp_path / "ontolearn-engine")),
        ("embedded", "PYZ.pyz"),
    ]


# Stub subprocesses plus actual temporary filesystem; no prepare/PyInstaller execution.
BUILDER_UNIT = r"""import test from 'node:test'
import { spawnSync } from 'node:child_process'
import assert from 'node:assert/strict'
import * as fs from 'node:fs'
import { resolve, join } from 'node:path'
const { buildEngine, publishEngineCopy } = await import(process.env.BUILDER_MODULE_URL)
const token = '11111111-2222-3333-4444-555555555555'
const parent = new URL('./tmp/', import.meta.url)
fs.mkdirSync(parent, { recursive: true })
function fixture(t, behavior = {}) {
  const root = fs.mkdtempSync(new URL('builder-', parent))
  t.after(() => fs.rmSync(root, { recursive: true, force: true }))
  const runRoot = resolve(root, 'build/i05-provenance', token)
  const engine = resolve(runRoot, 'dist/ontolearn-engine')
  const calls = []
  const run = (command, args, options) => {
    calls.push({ command, args, options })
    if (calls.length === 1) {
      if (behavior.prepare) return behavior.prepare
      fs.mkdirSync(resolve(runRoot, 'generated'), { recursive: true })
      fs.mkdirSync(resolve(runRoot, 'provenance'))
      return {
        status: 0,
        stdout: JSON.stringify({
          provenancePath: resolve(
            runRoot,
            'provenance/i05-private-build-provenance-v1.json',
          ),
          contractPath: resolve(runRoot, 'provenance/i05-private-contract-v1.json'),
          generatedDir: resolve(runRoot, 'generated'),
          anchorPath: resolve(runRoot, 'generated/_i05_private_build_anchor.py'),
        }),
      }
    }
    if (calls.length === 2) {
      if (behavior.packager) return behavior.packager
      fs.mkdirSync(engine, { recursive: true })
      fs.writeFileSync(resolve(engine, 'ontolearn-engine'), 'synthetic-new-engine')
      return { status: 0 }
    }
    if (calls.length === 3) {
      if (behavior.finalize) return behavior.finalize
      fs.writeFileSync(resolve(runRoot, 'artifact-binding-v1.json'), 'synthetic-binding')
      return {
        status: 0,
        stdout: JSON.stringify({
          bindingPath: resolve(runRoot, 'artifact-binding-v1.json'),
          bindingSha256: 'a'.repeat(64),
          engineDirectory: engine,
          provenanceSha256: 'b'.repeat(64),
        }),
      }
    }
    throw new Error('unexpected subprocess')
  }
  return { root, runRoot, engine, calls, run }
}
function oldStage(f) {
  const path = resolve(f.root, 'build/engine/ontolearn-engine')
  fs.mkdirSync(path, { recursive: true })
  fs.writeFileSync(resolve(path, 'old'), 'synthetic-old-stage')
  return path
}

test('builder fixes8 collections, compile0, unique outputs and preserves old stage', (t) => {
  const f = fixture(t)
  const old = oldStage(f)
  const result = buildEngine({ repositoryRoot: f.root, run: f.run, uuid: () => token })
  assert.equal(f.calls.length, 3)
  const argv = f.calls[1].args
  for (const name of [
    'rdflib',
    'pyparsing',
    'pyshacl',
    'owlrl',
    'packaging',
    'prettytable',
    'wcwidth',
    'html5rdf',
  ]) {
    assert(argv.some((x, i) => x === '--collect-all' && argv[i + 1] === name))
    assert(argv.some((x, i) => x === '--copy-metadata' && argv[i + 1] === name))
  }
  assert.equal(argv[argv.indexOf('--optimize') + 1], '0')
  assert(
    argv.some(
      (x, i) =>
        x === '--hidden-import' &&
        argv[i + 1] === 'ontolearn_engine.semantic_build_provenance',
    ),
  )
  for (const flag of ['--distpath', '--workpath', '--specpath'])
    assert(argv[argv.indexOf(flag) + 1].startsWith(f.runRoot + '/'))
  assert.equal(f.calls[1].options.env.PYINSTALLER_CONFIG_DIR, resolve(f.runRoot, 'cache'))
  assert.equal(result.rootApproved, false)
  assert.equal(
    fs.readFileSync(resolve(old, 'ontolearn-engine'), 'utf8'),
    'synthetic-new-engine',
  )
  assert.equal(
    fs.readFileSync(resolve(f.runRoot, 'staging-archive/ontolearn-engine/old'), 'utf8'),
    'synthetic-old-stage',
  )
  assert.equal(
    fs.readFileSync(resolve(f.engine, 'ontolearn-engine'), 'utf8'),
    'synthetic-new-engine',
  )
  assert.equal(fs.readFileSync(result.bindingPath, 'utf8'), 'synthetic-binding')
})

test('prepare nonzero prevents packager and keeps first diagnostic', (t) => {
  const f = fixture(t, {
    prepare: { status: 2, stdout: '', stderr: 'EXPECTED_UNIT_PREPARE_FAILURE\n' },
  })
  assert.throws(
    () => buildEngine({ repositoryRoot: f.root, run: f.run, uuid: () => token }),
    /HELPER_FAILED/,
  )
  assert.equal(f.calls.length, 1)
})

test('packager failure never finalizes or replaces staging', (t) => {
  const f = fixture(t, { packager: { status: 7 } })
  const old = oldStage(f)
  assert.throws(
    () => buildEngine({ repositoryRoot: f.root, run: f.run, uuid: () => token }),
    /PYINSTALLER_FAILED/,
  )
  assert.equal(f.calls.length, 2)
  assert.equal(fs.readFileSync(resolve(old, 'old'), 'utf8'), 'synthetic-old-stage')
})

test('unexpected helper output cannot select other paths', (t) => {
  const f = fixture(t, {
    prepare: {
      status: 0,
      stdout: JSON.stringify({
        provenancePath: '/outside',
        contractPath: '/outside',
        generatedDir: '/outside',
        anchorPath: '/outside',
      }),
    },
  })
  assert.throws(
    () => buildEngine({ repositoryRoot: f.root, run: f.run, uuid: () => token }),
    /HELPER_PATH_INVALID/,
  )
  assert.equal(f.calls.length, 1)
})

test('invalid final binding prevents staging publication', (t) => {
  const f = fixture(t, {
    finalize: {
      status: 0,
      stdout: JSON.stringify({
        bindingPath: '/outside',
        bindingSha256: 'a'.repeat(64),
        engineDirectory: '/outside',
        provenanceSha256: 'b'.repeat(64),
      }),
    },
  })
  const old = oldStage(f)
  assert.throws(
    () => buildEngine({ repositoryRoot: f.root, run: f.run, uuid: () => token }),
    /BINDING_INVALID/,
  )
  assert.equal(fs.readFileSync(resolve(old, 'old'), 'utf8'), 'synthetic-old-stage')
})

test('duplicate UUID does not overwrite previous artifact or binding', (t) => {
  const f = fixture(t)
  const result = buildEngine({ repositoryRoot: f.root, run: f.run, uuid: () => token })
  const original = fs.readFileSync(result.bindingPath)
  assert.throws(
    () => buildEngine({ repositoryRoot: f.root, run: f.run, uuid: () => token }),
    /OUTPUT_EXISTS/,
  )
  assert.deepEqual(fs.readFileSync(result.bindingPath), original)
  assert.equal(f.calls.length, 3)
})

test('dangling build ancestor symlink is rejected without writing its target', (t) => {
  const f = fixture(t)
  fs.mkdirSync(resolve(f.root, 'build'))
  const outside = resolve(f.root, 'outside-not-created')
  fs.symlinkSync(outside, resolve(f.root, 'build/i05-provenance'))
  assert.throws(
    () => buildEngine({ repositoryRoot: f.root, run: f.run, uuid: () => token }),
    /DIRECTORY_INVALID/,
  )
  assert.equal(fs.existsSync(outside), false)
  assert.equal(f.calls.length, 0)
})

test('failed publication restores preceding stage without deleting immutable object', (t) => {
  const f = fixture(t)
  const old = oldStage(f)
  let injected = false
  const io = {
    ...fs,
    renameSync: (source, target) => {
      if (source.includes('.ontolearn-engine-') && target === old && !injected) {
        injected = true
        throw new Error('EXPECTED_RENAME_FAILURE')
      }
      return fs.renameSync(source, target)
    },
  }
  assert.throws(
    () => buildEngine({ repositoryRoot: f.root, run: f.run, uuid: () => token, io }),
    /EXPECTED_RENAME_FAILURE/,
  )
  assert.equal(fs.readFileSync(resolve(old, 'old'), 'utf8'), 'synthetic-old-stage')
  assert.equal(
    fs.readFileSync(resolve(f.engine, 'ontolearn-engine'), 'utf8'),
    'synthetic-new-engine',
  )
  assert.equal(
    fs.readFileSync(resolve(f.runRoot, 'artifact-binding-v1.json'), 'utf8'),
    'synthetic-binding',
  )
})

test('publish rejects source ancestor symlink and unsafe token', (t) => {
  const f = fixture(t)
  fs.mkdirSync(f.runRoot, { recursive: true })
  const outside = resolve(f.root, 'outside')
  fs.mkdirSync(resolve(outside, 'ontolearn-engine'), { recursive: true })
  fs.symlinkSync(outside, resolve(f.runRoot, 'dist'))
  assert.throws(
    () =>
      publishEngineCopy({
        root: f.root,
        runRoot: f.runRoot,
        engineDirectory: f.engine,
        token,
      }),
    /ARTIFACT_PATH_INVALID/,
  )
  assert.throws(
    () =>
      publishEngineCopy({
        root: f.root,
        runRoot: f.runRoot,
        engineDirectory: f.engine,
        token: '../outside',
      }),
    /ARTIFACT_PATH_INVALID/,
  )
})

test('noncanonical absolute root rejects promptly in a bounded unit child', (t) => {
  const f = fixture(t)
  fs.mkdirSync(f.engine, { recursive: true })
  const script = `import {publishEngineCopy} from ${JSON.stringify(process.env.BUILDER_MODULE_URL)};
  import {resolve} from 'node:path';
  const root=process.argv[1];const token=${JSON.stringify(token)};
  const runRoot=resolve(root,'build/i05-provenance',token);
  try {publishEngineCopy({root,runRoot,engineDirectory:resolve(runRoot,'dist/ontolearn-engine'),
  token});
  process.exit(3)}
  catch(error){
  process.stdout.write(error.message);
  process.exit(error.message==='BUILD_ENGINE_ARTIFACT_PATH_INVALID'?0:4)}`
  const result = spawnSync(
    process.execPath,
    ['--input-type=module', '-e', script, f.root + '/.'],
    { encoding: 'utf8', timeout: 2000 },
  )
  assert.equal(result.error, undefined)
  assert.equal(result.status, 0)
  assert.equal(result.stdout, 'BUILD_ENGINE_ARTIFACT_PATH_INVALID')
})
"""


def test_private_node_builder_boundaries(tmp_path):
    script = tmp_path / "builder-private-unit.mjs"
    script.write_text(BUILDER_UNIT)
    result = subprocess.run(
        ["node", "--test", "--test-reporter=tap", str(script)],
        cwd=REPOSITORY,
        env={
            **os.environ,
            "BUILDER_MODULE_URL": (REPOSITORY / "scripts/build-engine.mjs").as_uri(),
        },
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "# pass 10" in result.stdout
    assert "# fail 0" in result.stdout


@pytest.mark.parametrize("status", [0, 1, 2, 130])
def test_entrypoint_semantic_preserves_argv_and_exit(monkeypatch, status):
    name = "ontolearn_engine.semantic_source_package_probe"
    module = types.ModuleType(name)
    observed = []

    def main():
        observed.append(list(sys.argv))
        return status

    module.main = main
    monkeypatch.setitem(sys.modules, name, module)
    argv = [
        str(REPOSITORY / "packages/engine/entrypoint.py"),
        "--semantic-source-package-probe",
        "full-v1",
    ]
    monkeypatch.setattr(sys, "argv", argv.copy())
    with pytest.raises(SystemExit) as caught:
        runpy.run_path(str(REPOSITORY / "packages/engine/entrypoint.py"), run_name="__main__")
    assert caught.value.code == status
    assert observed == [argv]


@pytest.mark.parametrize(
    ("flag", "target", "expected_argv"),
    [
        ("--storage-probe", "storage_probe", ["entrypoint.py", "synthetic"]),
        ("--worker", "worker", ["entrypoint.py", "--worker", "synthetic"]),
        ("--contract-probe", "contract_probe", ["entrypoint.py", "--contract-probe", "synthetic"]),
        (
            "--protocol-resources",
            "resources",
            ["entrypoint.py", "--protocol-resources", "synthetic"],
        ),
        ("--other", "__main__", ["entrypoint.py", "--other", "synthetic"]),
    ],
)
def test_entrypoint_existing_dispatch(monkeypatch, flag, target, expected_argv):
    observed = []
    for candidate in [
        "semantic_source_package_probe",
        "storage_probe",
        "worker",
        "contract_probe",
        "resources",
        "__main__",
    ]:
        name = f"ontolearn_engine.{candidate}"
        module = types.ModuleType(name)

        def main(candidate=candidate):
            observed.append((candidate, list(sys.argv)))

        module.main = main
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setattr(sys, "argv", ["entrypoint.py", flag, "synthetic"])
    runpy.run_path(str(REPOSITORY / "packages/engine/entrypoint.py"), run_name="__main__")
    assert observed == [
        (target, [str(REPOSITORY / "packages/engine/entrypoint.py"), *expected_argv[1:]])
    ]


@pytest.mark.parametrize("oversized", [False, True])
def test_distribution_python_identity_uses_one_bounded_snapshot(tmp_path, monkeypatch, oversized):
    site = tmp_path / "env/site-packages"
    info = "html5rdf-1.2.1.dist-info"
    write(site, info + "/METADATA", b"Name: html5rdf\nVersion: 1.2.1\n")
    write(site, info + "/LICENSE", b"license")
    relative = "html5rdf/__init__.py"
    original_raw = b"VALUE = 1\n" if not oversized else b"#" * (p.CODE_CAP + 1)
    source = site / relative
    write(site, relative, original_raw)

    class Distribution:
        version = "1.2.1"
        files = [info + "/METADATA", info + "/LICENSE", relative]

        def locate_file(self, path):
            return site / path

    monkeypatch.setattr(p.importlib.metadata, "distribution", lambda _name: Distribution())
    monkeypatch.setattr(p.sysconfig, "get_path", lambda _kind: str(site))
    monkeypatch.setattr(sys, "prefix", str(tmp_path / "env"))
    original_read = p._read
    source_caps = []

    def observed_read(path, cap):
        if path == source:
            source_caps.append(cap)
            raw = original_read(path, cap)
            source.write_bytes(b"VALUE = 999\n")
            return raw
        return original_read(path, cap)

    monkeypatch.setattr(p, "_read", observed_read)
    if oversized:
        with fault("LIMIT_EXCEEDED"):
            p._dist_inventory("html5rdf", "1.2.1")
    else:
        row = p._dist_inventory("html5rdf", "1.2.1")["files"][0]
        assert row["bytes"] == len(original_raw)
        assert row["sha256"] == p._sha(original_raw)
        assert row["codeSha256"] == p._code_sha(p._compiled(original_raw))
    assert source_caps == [p.CODE_CAP]


# Standalone profile fixtures contain synthetic code objects; none are executed.
STANDALONE_CONTRACT_RAW = (REPOSITORY / p.STANDALONE_CONTRACT_SOURCE).read_bytes()
STANDALONE_CONTRACT = json.loads(STANDALONE_CONTRACT_RAW)


def make_standalone_case(monkeypatch, engine):
    allowed = set(p.SUPPLIER_MODULES + p.PRIVATE_MODULES)
    for name in tuple(sys.modules):
        if (
            name == "ontolearn_engine" or name.startswith("ontolearn_engine.")
        ) and name not in allowed:
            monkeypatch.delitem(sys.modules, name)
    value = make_case(monkeypatch, engine)
    (engine / "ontolearn-engine").rename(engine / "ontolearn-semantic-parity")
    manifest = value.manifest
    manifest["format"] = "i05-semantic-parity-build-provenance/1"
    manifest["profile"] = p.STANDALONE_PROFILE
    manifest["contract"] = {
        "path": p.STANDALONE_CONTRACT_SOURCE,
        "bytes": len(STANDALONE_CONTRACT_RAW),
        "sha256": p.STANDALONE_CONTRACT_SHA256,
    }
    for source, target in zip(p.FIXED_INPUTS, p.STANDALONE_INPUTS, strict=True):
        destination = value.root / target["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        (value.root / source["path"]).rename(destination)
    manifest["inputs"] = copy.deepcopy(list(p.STANDALONE_INPUTS))
    value.expectations["inputs"] = copy.deepcopy(manifest["inputs"])
    probe = next(row for row in manifest["privateModules"] if row["module"] == p.PRIVATE_MODULES[0])
    manifest["entrypoint"] = {
        "path": p.STANDALONE_TARGET,
        "bytes": probe["bytes"],
        "sha256": probe["sha256"],
        "codeSha256": probe["codeSha256"],
    }
    manifest["buildInputs"] = [
        {"path": name, "bytes": len(name.encode()), "sha256": p._sha(name.encode())}
        for name in p.BUILD_INPUTS[:3]
    ] + [copy.deepcopy(manifest["lock"]), copy.deepcopy(manifest["contract"])]
    mirrors = []
    for dist in manifest["distributions"]:
        for row in dist["licenses"]:
            relative = "licenses/" + dist["name"] + "/" + row["path"]
            identity = write(value.root, relative, (value.root / row["path"]).read_bytes())
            mirrors.append({**identity, "distribution": dist["name"], "sourcePath": row["path"]})
    manifest["licenseMirrors"] = mirrors
    (value.root / p.CONTRACT_BUNDLED).unlink()
    (value.root / p.PROVENANCE_BUNDLED).unlink()
    write(value.root, p.STANDALONE_CONTRACT_BUNDLED, STANDALONE_CONTRACT_RAW)
    value.codes.pop(p.ANCHOR)

    def refresh():
        raw = p._canonical(manifest)
        write(value.root, p.STANDALONE_PROVENANCE, raw)
        value.codes[p.STANDALONE_ANCHOR] = p._compiled(
            p._anchor_source(p._sha(raw), profile=p.STANDALONE_PROFILE)
        )
        return raw

    def get_anchor(name):
        assert name == p.STANDALONE_ANCHOR, "unrelated module discovery"
        value.anchor_loader.code = value.codes[name]
        return importlib.machinery.ModuleSpec(
            name, value.anchor_loader, origin=str(value.root / (name + ".py"))
        )

    value.refresh = refresh
    value.load = lambda: p.load_frozen_provenance(
        expectations=value.expectations, profile=p.STANDALONE_PROFILE
    )
    monkeypatch.setattr(p.importlib.util, "find_spec", get_anchor)
    refresh()
    return value


@pytest.fixture
def standalone_case(monkeypatch, tmp_path):
    return make_standalone_case(monkeypatch, tmp_path / "standalone")


def test_standalone_contract_uses_real_hash_and_exact_roles():
    assert p._sha(STANDALONE_CONTRACT_RAW) == p.STANDALONE_CONTRACT_SHA256
    assert STANDALONE_CONTRACT["format"] == "i05-semantic-parity-private-contract/1"
    assert STANDALONE_CONTRACT["profile"] == p.STANDALONE_PROFILE
    assert STANDALONE_CONTRACT["analysisImports"] == [
        *p.SUPPLIER_MODULES,
        *p.PRIVATE_MODULES,
        p.STANDALONE_ANCHOR,
    ]
    assert STANDALONE_CONTRACT["fixedInputs"] == list(p.STANDALONE_INPUTS)
    assert STANDALONE_CONTRACT["buildInputs"] == list(p.BUILD_INPUTS)
    pins = p._literal_pins((REPOSITORY / p.STANDALONE_TARGET).read_bytes())
    guards = p._standalone_source_guards(pins)
    assert tuple(STANDALONE_CONTRACT["sourceGuards"]) == guards
    assert len(guards) == len(set(guards)) == 35
    assert guards.count(p.STANDALONE_TARGET) == 1
    assert "packages/engine/entrypoint.py" not in guards
    for source, frozen in zip(p.FIXED_INPUTS, p.STANDALONE_INPUTS, strict=True):
        assert frozen == {
            **source,
            "path": "provenance/i05/source-package-parity/" + Path(source["path"]).name,
        }


@pytest.mark.parametrize(
    "profile", [None, False, 1, {}, "", "parent", "i05-source-package-parity/../x"]
)
def test_unknown_profile_rejects_before_any_file_read(monkeypatch, tmp_path, profile):
    monkeypatch.setattr(p, "_read", lambda *_a: pytest.fail("unexpected file read"))
    with fault("MODE_INVALID"):
        p.prepare_build(tmp_path, tmp_path, profile=profile)
    with fault("MODE_INVALID"):
        p.finalize_build(tmp_path, tmp_path, tmp_path, profile=profile)
    with fault("MODE_INVALID"):
        p.load_frozen_provenance(expectations={}, profile=profile)
    with fault("MODE_INVALID"):
        p.verify_external_binding(tmp_path, tmp_path, expected_sha256="0" * 64, profile=profile)


def test_standalone_preflight_has_no_imports_and_preserves_runtime_domain(
    standalone_case, monkeypatch
):
    value = standalone_case
    monkeypatch.setattr(
        p.importlib, "import_module", lambda *_a, **_k: pytest.fail("target import")
    )
    evidence = value.load()
    assert evidence._profile == p.STANDALONE_PROFILE
    assert value.anchor_loader.calls == [p.STANDALONE_ANCHOR]
    with pytest.raises(FrozenInstanceError):
        evidence._profile = p.PARENT_PROFILE
    result = p.verify_loaded_modules(evidence, value.modules)
    assert result["entrypointDomain"] == (
        "runtime-canonical-PYZ-only; target-CArchive-external-binding-required"
    )
    assert result["rootApproval"] == result["semanticParity"] == "unknown"
    assert {row["module"] for row in result["supplierAndPrivateModules"]} == set(
        p.SUPPLIER_MODULES + p.PRIVATE_MODULES
    )
    with fault("NATIVE_UNAVAILABLE"):
        p.verify_native_extension(evidence)


def test_standalone_unknown_internal_and_distribution_children_are_rejected(
    standalone_case, monkeypatch
):
    value = standalone_case
    evidence = value.load()
    for name in ("ontolearn_engine.unrecorded", "pyshacl.unrecorded"):
        with monkeypatch.context() as scoped:
            scoped.setitem(sys.modules, name, types.ModuleType(name))
            with fault("MODULE_MISMATCH"):
                p.verify_loaded_modules(evidence, value.modules)


@pytest.mark.parametrize("changed", ["root", "python", "contract", "anchor", "profile"])
def test_standalone_evidence_context_is_rechecked(standalone_case, monkeypatch, tmp_path, changed):
    value = standalone_case
    evidence = value.load()
    if changed == "root":
        monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path))
    elif changed == "python":
        original = p._python_identity
        monkeypatch.setattr(p, "_python_identity", lambda: {**original(), "cacheTag": "changed"})
    elif changed == "contract":
        (value.root / p.STANDALONE_CONTRACT_BUNDLED).write_bytes(CONTRACT_RAW)
    elif changed == "anchor":
        value.codes[p.STANDALONE_ANCHOR] = p._compiled(b"raise RuntimeError('never executed')")
    else:
        # Check accidental cross-profile carrier reuse, not protection from hostile Python.
        object.__setattr__(evidence, "_profile", p.PARENT_PROFILE)
    with pytest.raises(p.BuildProvenanceFault):
        p.verify_loaded_modules(evidence, value.modules)


@pytest.mark.parametrize(
    "field", ["mirrorFile", "missingMirror", "wrongMirror", "oldInput", "buildInput"]
)
def test_standalone_paths_and_license_roles_are_exact(standalone_case, field):
    value = standalone_case
    if field == "mirrorFile":
        (value.root / value.manifest["licenseMirrors"][0]["path"]).write_bytes(b"tampered")
    elif field == "missingMirror":
        value.manifest["licenseMirrors"].pop()
    elif field == "wrongMirror":
        value.manifest["licenseMirrors"][0]["sourcePath"] = "foreign.dist-info/LICENSE"
    elif field == "oldInput":
        value.manifest["inputs"] = copy.deepcopy(list(p.FIXED_INPUTS))
        value.expectations["inputs"] = copy.deepcopy(list(p.FIXED_INPUTS))
    else:
        value.manifest["buildInputs"][0]["path"] = "packages/engine/entrypoint.py"
    value.refresh()
    with pytest.raises(p.BuildProvenanceFault):
        value.load()


def test_standalone_missing_authors_cannot_be_covered_by_license(standalone_case):
    value = standalone_case
    dist = value.manifest["distributions"][-1]
    dist["licenses"] = dist["licenses"][:1]
    value.manifest["licenseMirrors"] = [
        row
        for row in value.manifest["licenseMirrors"]
        if not row["sourcePath"].endswith("AUTHORS.rst")
    ]
    value.refresh()
    with fault("DISTRIBUTION_MISMATCH"):
        value.load()


def test_standalone_mirror_caps_not_widened(standalone_case):
    value = standalone_case
    value.manifest["licenseMirrors"][0]["bytes"] = p.SMALL_CAP + 1
    value.refresh()
    with fault("SCHEMA_INVALID"):
        value.load()


def test_standalone_notice_inventory_covers_undeclared_record_notices(tmp_path, monkeypatch):
    site = tmp_path / "env/site-packages"
    info = "html5rdf-1.2.1.dist-info"
    listed = [info + "/METADATA", info + "/LICENSE", info + "/NOTICE", info + "/AUTHORS.rst"]
    write(site, listed[0], b"Name: html5rdf\nVersion: 1.2.1\n")
    for relative in listed[1:]:
        write(site, relative, relative.encode())
    write(site, "html5rdf/__init__.py", b"VALUE = 1\n")

    class Distribution:
        version = "1.2.1"
        files = [*listed, "html5rdf/__init__.py"]

        def locate_file(self, relative):
            return site / relative

    monkeypatch.setattr(p.importlib.metadata, "distribution", lambda _name: Distribution())
    monkeypatch.setattr(p.sysconfig, "get_path", lambda _kind: str(site))
    monkeypatch.setattr(sys, "prefix", str(tmp_path / "env"))
    parent = p._dist_inventory("html5rdf", "1.2.1")
    standalone = p._dist_inventory("html5rdf", "1.2.1", include_notices=True)
    assert [row["path"] for row in parent["licenses"]] == [info + "/LICENSE"]
    assert {row["path"] for row in standalone["licenses"]} == set(listed[1:])


def test_standalone_prepare_returns_nested_paths_and_preserves_first_output(
    standalone_case, monkeypatch, tmp_path
):
    value = standalone_case
    repository = tmp_path / "repository"
    write(repository, p.STANDALONE_CONTRACT_SOURCE, STANDALONE_CONTRACT_RAW)
    output = repository / "build/i05-semantic-parity" / str(uuid.uuid4())
    monkeypatch.setattr(p, "_collect_standalone_manifest", lambda *_a: value.manifest)
    monkeypatch.setattr(p.sysconfig, "get_path", lambda _kind: str(value.root))
    result = p.prepare_build(repository, output, profile=p.STANDALONE_PROFILE)
    assert result == {
        "provenancePath": str(output / p.STANDALONE_PROVENANCE),
        "contractPath": str(output / p.STANDALONE_CONTRACT_BUNDLED),
        "generatedDir": str(output / "generated"),
        "anchorPath": str(output / "generated" / (p.STANDALONE_ANCHOR + ".py")),
    }
    assert Path(result["contractPath"]).read_bytes() == STANDALONE_CONTRACT_RAW
    assert Path(result["anchorPath"]).read_bytes() == p._anchor_source(
        p._sha(Path(result["provenancePath"]).read_bytes()), profile=p.STANDALONE_PROFILE
    )
    for row in value.manifest["licenseMirrors"]:
        assert (output / row["path"]).read_bytes() == (value.root / row["sourcePath"]).read_bytes()
    first = Path(result["provenancePath"]).read_bytes()
    with fault("BUILD_OUTPUT_EXISTS"):
        p.prepare_build(repository, output, profile=p.STANDALONE_PROFILE)
    assert Path(result["provenancePath"]).read_bytes() == first


@pytest.mark.parametrize("invalid", ["extra", "wrongRequest", "symlink"])
def test_standalone_prepare_only_accepts_exact_builder_reservation(monkeypatch, tmp_path, invalid):
    repository = tmp_path / "repository"
    repository.mkdir()
    output = repository / "build/i05-semantic-parity" / str(uuid.uuid4())
    evidence = output / "evidence"
    evidence.mkdir(parents=True)
    (evidence / "cache").mkdir()
    (evidence / "tmp").mkdir()
    request = {"profile": p.STANDALONE_PROFILE, "token": output.name}
    if invalid == "wrongRequest":
        request["token"] = str(uuid.uuid4())
    write(evidence, "build-request-v1.json", p._canonical(request))
    write(evidence, "prepare.stdout.log", b"")
    write(evidence, "prepare.stderr.log", b"")
    if invalid == "extra":
        write(output, "unexpected", b"first output")
    elif invalid == "symlink":
        (evidence / "prepare.stdout.log").unlink()
        outside = tmp_path / "outside"
        outside.write_bytes(b"never write")
        (evidence / "prepare.stdout.log").symlink_to(outside)
    monkeypatch.setattr(
        p, "_collect_standalone_manifest", lambda *_a: pytest.fail("must reject first")
    )
    with pytest.raises(p.BuildProvenanceFault):
        p.prepare_build(repository, output, profile=p.STANDALONE_PROFILE)


def test_standalone_layout_rejects_source_ancestor_symlink_and_foreign_prefix(tmp_path):
    repository = tmp_path / "repo"
    (repository / "build").mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    (repository / "build/i05-semantic-parity").symlink_to(outside, target_is_directory=True)
    output = repository / "build/i05-semantic-parity" / str(uuid.uuid4())
    with fault("BUILD_LAYOUT_INVALID"):
        p.prepare_build(repository, output, profile=p.STANDALONE_PROFILE)
    assert list(outside.iterdir()) == []
    with fault("BUILD_LAYOUT_INVALID"):
        p.prepare_build(
            repository,
            repository / "build/i05-provenance" / str(uuid.uuid4()),
            profile=p.STANDALONE_PROFILE,
        )


def test_standalone_source_guard_dirty_check_is_exact_and_before_source_adoption(
    monkeypatch, tmp_path
):
    repository = tmp_path / "repo"
    write(repository, p.STANDALONE_TARGET, (REPOSITORY / p.STANDALONE_TARGET).read_bytes())
    calls = []

    def dirty(_root, *args):
        calls.append(args)
        assert args[:4] == ("diff", "--name-only", "HEAD", "--")
        return b"scripts/build-engine.mjs\n"

    monkeypatch.setattr(p, "_git", dirty)
    monkeypatch.setattr(p, "_dist_inventory", lambda *_a, **_k: pytest.fail("dirty source adopted"))
    with fault("BUILD_INPUT_DIRTY"):
        p._collect_standalone_manifest(repository, STANDALONE_CONTRACT, STANDALONE_CONTRACT_RAW)
    assert calls == [("diff", "--name-only", "HEAD", "--", *STANDALONE_CONTRACT["sourceGuards"])]


def synthetic_pyz(code_rows, *, change_rows=None, packed_overrides=None, toc_suffix=b""):
    """Build a real PYZ byte layout independently from the product parser."""
    payload = bytearray()
    toc = []
    for name, code, kind in code_rows:
        if kind == 3:
            toc.append((name, (kind, 0, 0)))
            continue
        packed = zlib.compress(marshal.dumps(code, 4))
        if packed_overrides and name in packed_overrides:
            packed = packed_overrides[name]
        toc.append((name, (kind, 12 + len(payload), len(packed))))
        payload.extend(packed)
    if change_rows:
        toc = change_rows(toc)
    header = b"PYZ\0" + importlib.util.MAGIC_NUMBER + struct.pack("!i", 12 + len(payload))
    return header + bytes(payload) + marshal.dumps(toc, 4) + toc_suffix


def synthetic_carchive(
    pyz, target, *, extra=(), change_rows=None, change_toc=None, cookie_overrides=None
):
    """Return inert launcher bytes with true CArchive records and cookie."""
    target_raw = marshal.dumps(target, 4) if type(target) is types.CodeType else target
    members = [
        ("PYZ.pyz", b"z", pyz, 0),
        ("semantic_source_package_probe", b"s", target_raw, 1),
        *extra,
    ]
    payload, rows = bytearray(), []
    for name, kind, raw, compressed in members:
        packed = zlib.compress(raw) if compressed else raw
        rows.append(
            {
                "name": name,
                "kind": kind,
                "start": 0 if kind == b"o" else len(payload),
                "packed": len(packed),
                "unpacked": len(raw),
                "compressed": compressed,
            }
        )
        payload.extend(packed)
    if change_rows:
        rows = change_rows(rows)
    records = []
    for row in rows:
        name = row["name"] if type(row["name"]) is bytes else row["name"].encode("utf-8")
        name += b"\0"
        records.append(
            struct.pack(
                "!IIIIBc",
                18 + len(name),
                row["start"],
                row["packed"],
                row["unpacked"],
                row["compressed"],
                row["kind"],
            )
            + name
        )
    toc = b"".join(records)
    if change_toc:
        toc = change_toc(toc)
    values = {
        "total": len(payload) + len(toc) + struct.calcsize("!8sIIII64s"),
        "tocOffset": len(payload),
        "tocSize": len(toc),
        "python": 312,
        "library": p.sysconfig.get_config_var("LDLIBRARY").encode().ljust(64, b"\0"),
    }
    values.update(cookie_overrides or {})
    cookie = struct.pack(
        "!8sIIII64s",
        b"MEI\014\013\012\013\016",
        values["total"],
        values["tocOffset"],
        values["tocSize"],
        values["python"],
        values["library"],
    )
    return b"inert unit prefix; never executable\0" + bytes(payload) + toc + cookie


def parser_fixture_code():
    return compile(
        b"raise RuntimeError('unit parser must never execute this code')",
        "unit",
        "exec",
        flags=0,
        dont_inherit=True,
        optimize=0,
    )


def test_bounded_pyz_reads_real_compressed_code_without_execution():
    code = parser_fixture_code()
    raw = synthetic_pyz([("safe", code, 0), ("namespace", None, 3)])
    archive = p._BoundedPYZ(raw)
    assert set(archive.toc) == {"safe", "namespace"}
    assert p._code_sha(archive.extract("safe")) == p._code_sha(code)
    with fault("ARCHIVE_MISMATCH"):
        archive.extract("namespace")
    with fault("ARCHIVE_MISMATCH"):
        archive.extract("missing")


@pytest.mark.parametrize(
    "invalid",
    ["duplicate", "casefold", "overlap", "kind", "offset", "bool", "unicode", "shape", "empty"],
)
def test_bounded_pyz_toc_rejects_ambiguous_or_unbounded_records(invalid):
    code = parser_fixture_code()

    def changed(rows):
        first, second = rows
        if invalid == "duplicate":
            return [first, first]
        if invalid == "casefold":
            return [first, (first[0].upper(), second[1])]
        if invalid == "overlap":
            return [first, (second[0], (0, first[1][1], second[1][2]))]
        if invalid == "kind":
            return [(first[0], (4, *first[1][1:])), second]
        if invalid == "offset":
            return [(first[0], (0, 0, first[1][2])), second]
        if invalid == "bool":
            return [(first[0], (False, *first[1][1:])), second]
        if invalid == "unicode":
            return [("e\u0301", first[1]), second]
        if invalid == "shape":
            return [("bad", (0, 12)), second]
        return [("", first[1]), second]

    raw = synthetic_pyz([("first", code, 0), ("second", code, 0)], change_rows=changed)
    with fault("ARCHIVE_MISMATCH"):
        p._BoundedPYZ(raw)


@pytest.mark.parametrize("invalid", ["magic", "python", "tocOffset", "trailing", "short"])
def test_bounded_pyz_header_and_marshal_eof_are_exact(invalid):
    raw = synthetic_pyz([("safe", parser_fixture_code(), 0)])
    if invalid == "magic":
        raw = b"bad!" + raw[4:]
    elif invalid == "python":
        raw = raw[:4] + b"\0" * 4 + raw[8:]
    elif invalid == "tocOffset":
        raw = raw[:8] + struct.pack("!i", -1) + raw[12:]
    elif invalid == "trailing":
        raw += b"trailing"
    else:
        raw = raw[:11]
    with fault("PYTHON_MISMATCH" if invalid == "python" else "ARCHIVE_MISMATCH"):
        p._BoundedPYZ(raw)


def test_bounded_pyz_limits_toc_records_bytes_and_decompression_before_code(monkeypatch):
    code = parser_fixture_code()
    raw = synthetic_pyz([("first", code, 0), ("second", code, 0)])
    with monkeypatch.context() as scoped:
        scoped.setattr(p, "ENTRY_CAP", 1)
        with fault("LIMIT_EXCEEDED"):
            p._BoundedPYZ(raw)
    with monkeypatch.context() as scoped:
        scoped.setattr(p, "MANIFEST_CAP", 8)
        with fault("ARCHIVE_MISMATCH"):
            p._BoundedPYZ(raw)
    bomb = synthetic_pyz([("safe", code, 0)], packed_overrides={"safe": zlib.compress(b"x" * 65)})
    archive = p._BoundedPYZ(bomb)
    with monkeypatch.context() as scoped:
        scoped.setattr(p, "CODE_CAP", 64)
        with fault("LIMIT_EXCEEDED"):
            archive.extract("safe")


@pytest.mark.parametrize(
    "invalid",
    ["garbage", "trailingCompressed", "truncated", "codeTrailing", "wrongObject", "declaredSize"],
)
def test_bounded_compressed_members_and_code_eof_are_exact(invalid):
    code_raw = marshal.dumps(parser_fixture_code(), 4)
    if invalid == "wrongObject":
        with fault("ARCHIVE_MISMATCH"):
            p._marshal_exact(marshal.dumps({"not": "code"}, 4), "code")
    elif invalid == "codeTrailing":
        with fault("ARCHIVE_MISMATCH"):
            p._marshal_exact(code_raw + b"x", "code")
    else:
        packed = zlib.compress(code_raw)
        declared = len(code_raw)
        if invalid == "garbage":
            packed = b"not zlib"
        elif invalid == "trailingCompressed":
            packed += b"x"
        elif invalid == "truncated":
            packed = packed[:-2]
        else:
            declared += 1
        with fault("ARCHIVE_MISMATCH"):
            p._inflate(packed, p.CODE_CAP, declared)


def test_bounded_carchive_compares_logical_cap_separately_from_physical_size(tmp_path):
    target = compile("VALUE = " + repr("x" * 32768), "unit", "exec", dont_inherit=True, optimize=0)
    pyz = synthetic_pyz([("safe", parser_fixture_code(), 0)])
    raw = synthetic_carchive(pyz, target)
    assert len(marshal.dumps(target, 4)) > len(raw), "fixture must exercise compression size domain"
    path = tmp_path / "inert-launcher"
    path.write_bytes(raw)
    archive, observed = p._bounded_archive(path)
    assert p._code_sha(observed) == p._code_sha(target)
    assert p._code_sha(archive.extract("safe")) == p._code_sha(parser_fixture_code())


@pytest.mark.parametrize(
    "invalid",
    [
        "missingTarget",
        "targetType",
        "duplicateTarget",
        "duplicatePyz",
        "overlap",
        "outside",
        "unpackedCap",
        "compressedFlag",
        "unicode",
        "invalidUTF8",
        "unknownType",
        "zeroRecord",
    ],
)
def test_bounded_carchive_toc_rejects_invalid_actual_members(tmp_path, invalid):
    def changed(rows):
        pyz_row, target = rows
        if invalid == "missingTarget":
            target["name"] = "different_probe"
        elif invalid == "targetType":
            target["kind"] = b"x"
        elif invalid == "duplicateTarget":
            return [*rows, copy.deepcopy(target)]
        elif invalid == "duplicatePyz":
            return [*rows, copy.deepcopy(pyz_row)]
        elif invalid == "overlap":
            target["start"] = pyz_row["start"]
        elif invalid == "outside":
            target["start"] = p.FILE_CAP
        elif invalid == "unpackedCap":
            target["unpacked"] = p.CODE_CAP + 1
        elif invalid == "compressedFlag":
            target["compressed"] = 2
        elif invalid == "unicode":
            target["name"] = "e\u0301"
        elif invalid == "invalidUTF8":
            target["name"] = b"\xff"
        elif invalid == "unknownType":
            target["kind"] = b"?"
        return rows

    toc_change = (lambda raw: struct.pack("!I", 0) + raw[4:]) if invalid == "zeroRecord" else None
    raw = synthetic_carchive(
        synthetic_pyz([("safe", parser_fixture_code(), 0)]),
        parser_fixture_code(),
        change_rows=changed,
        change_toc=toc_change,
    )
    path = tmp_path / "inert-launcher"
    path.write_bytes(raw)
    with fault("LIMIT_EXCEEDED" if invalid == "unpackedCap" else "ARCHIVE_MISMATCH"):
        p._bounded_archive(path)


def test_bounded_carchive_options_do_not_override_unique_members(tmp_path):
    raw = synthetic_carchive(
        synthetic_pyz([("safe", parser_fixture_code(), 0)]),
        parser_fixture_code(),
        extra=(
            ("pyi-contents-directory _internal", b"o", b"", 0),
            ("pyi-contents-directory _internal", b"o", b"", 0),
        ),
    )
    path = tmp_path / "inert-launcher"
    path.write_bytes(raw)
    archive, _target = p._bounded_archive(path)
    assert "safe" in archive.toc


@pytest.mark.parametrize(
    "invalid",
    [
        "fileCap",
        "tocCap",
        "tocRange",
        "python",
        "libraryPadding",
        "targetTrailing",
        "targetNonCode",
    ],
)
def test_bounded_carchive_header_caps_and_target_marshal_are_enforced(
    tmp_path, monkeypatch, invalid
):
    kwargs = {}
    target = parser_fixture_code()
    if invalid == "tocRange":
        kwargs["cookie_overrides"] = {"tocOffset": 0}
    elif invalid == "python":
        kwargs["cookie_overrides"] = {"python": 311}
    elif invalid == "libraryPadding":
        name = p.sysconfig.get_config_var("LDLIBRARY").encode()
        kwargs["cookie_overrides"] = {"library": (name + b"\0BAD").ljust(64, b"\0")}
    elif invalid == "targetTrailing":
        target = marshal.dumps(target, 4) + b"x"
    elif invalid == "targetNonCode":
        target = marshal.dumps([], 4)
    path = tmp_path / "inert-launcher"
    path.write_bytes(
        synthetic_carchive(synthetic_pyz([("safe", parser_fixture_code(), 0)]), target, **kwargs)
    )
    if invalid == "fileCap":
        monkeypatch.setattr(p, "FILE_CAP", 10)
    elif invalid == "tocCap":
        monkeypatch.setattr(p, "MANIFEST_CAP", 10)
    expected = (
        "LIMIT_EXCEEDED"
        if invalid == "fileCap"
        else ("PYTHON_MISMATCH" if invalid == "libraryPadding" else "ARCHIVE_MISMATCH")
    )
    with fault(expected):
        p._bounded_archive(path)


def complete_standalone_pyz(value, *, remove=None, changed=None, extra=None):
    codes = dict(value.codes)
    if remove:
        codes.pop(remove)
    if changed:
        codes[changed] = p._compiled(b"VALUE = 'tampered, never executed'\n")
    if extra:
        codes[extra] = p._compiled(b"VALUE = 'unexpected'\n")
    return synthetic_pyz([(name, code, 0) for name, code in codes.items()])


def test_standalone_archive_binds_exact24_anchor_and_independent_target(standalone_case):
    value = standalone_case
    archive = p._BoundedPYZ(complete_standalone_pyz(value))
    target = value.codes[p.PRIVATE_MODULES[0]]
    result = p._verify_standalone_archive(archive, target, value.manifest, value.root)
    assert result == {
        "archiveEntry": "semantic_source_package_probe",
        "typecode": "s",
        "sourcePath": p.STANDALONE_TARGET,
        "codeSha256": p._code_sha(target),
    }


@pytest.mark.parametrize(
    "invalid",
    [
        "supplier",
        "private",
        "anchor",
        "unknownInternal",
        "supplierCode",
        "privateCode",
        "anchorCode",
        "targetCode",
    ],
)
def test_standalone_archive_rejects_missing_or_changed_real_code(standalone_case, invalid):
    value = standalone_case
    options = {}
    if invalid == "supplier":
        options["remove"] = p.SUPPLIER_MODULES[0]
    elif invalid == "private":
        options["remove"] = p.PRIVATE_MODULES[1]
    elif invalid == "anchor":
        options["remove"] = p.STANDALONE_ANCHOR
    elif invalid == "unknownInternal":
        options["extra"] = "ontolearn_engine.unexpected"
    elif invalid == "supplierCode":
        options["changed"] = p.SUPPLIER_MODULES[1]
    elif invalid == "privateCode":
        options["changed"] = p.PRIVATE_MODULES[0]
    elif invalid == "anchorCode":
        options["changed"] = p.STANDALONE_ANCHOR
    archive = p._BoundedPYZ(complete_standalone_pyz(value, **options))
    target = value.codes[p.PRIVATE_MODULES[0]]
    if invalid == "targetCode":
        target = p._compiled(b"VALUE = 'changed target'\n")
    with fault("ANCHOR_MISMATCH" if invalid == "anchorCode" else "ARCHIVE_MISMATCH"):
        p._verify_standalone_archive(archive, target, value.manifest, value.root)


def test_standalone_finalize_and_external_binding_use_real_synthetic_archive(monkeypatch, tmp_path):
    repository = tmp_path / "repository"
    output = repository / "build/i05-semantic-parity" / str(uuid.uuid4())
    value = make_standalone_case(monkeypatch, output / "dist/ontolearn-semantic-parity")
    write(output, p.STANDALONE_PROVENANCE, (value.root / p.STANDALONE_PROVENANCE).read_bytes())
    write(output, p.STANDALONE_CONTRACT_BUNDLED, STANDALONE_CONTRACT_RAW)
    launcher = value.engine / "ontolearn-semantic-parity"
    launcher.write_bytes(
        synthetic_carchive(complete_standalone_pyz(value), value.codes[p.PRIVATE_MODULES[0]])
    )
    launcher.chmod(0o755)
    result = p.finalize_build(repository, output, value.engine, profile=p.STANDALONE_PROFILE)
    assert set(result) == {"bindingPath", "bindingSha256", "engineDirectory", "provenanceSha256"}
    binding_path = Path(result["bindingPath"])
    binding = json.loads(binding_path.read_bytes())
    assert binding["profile"] == p.STANDALONE_PROFILE
    assert binding["rootApproved"] is False
    assert binding["launcher"] == "ontolearn-semantic-parity"
    assert binding["targetCode"]["codeSha256"] == value.manifest["entrypoint"]["codeSha256"]
    assert not binding_path.is_relative_to(value.engine)
    receipt = p.verify_external_binding(
        binding_path,
        value.engine,
        expected_sha256=result["bindingSha256"],
        profile=p.STANDALONE_PROFILE,
    )
    assert receipt["inventoryVerified"] is True
    assert "no run executed" in receipt["rootApproval"]
    with fault("BUILD_OUTPUT_EXISTS"):
        p.finalize_build(repository, output, value.engine, profile=p.STANDALONE_PROFILE)
    with fault("EXTERNAL_BINDING_MISMATCH"):
        p.verify_external_binding(
            binding_path, value.engine, expected_sha256="0" * 64, profile=p.STANDALONE_PROFILE
        )
    with pytest.raises(p.BuildProvenanceFault):
        p.verify_external_binding(
            binding_path, value.engine, expected_sha256=result["bindingSha256"]
        )
    write(value.engine, "unlisted", b"new output")
    with fault("ARTIFACT_MISMATCH"):
        p.verify_external_binding(
            binding_path,
            value.engine,
            expected_sha256=result["bindingSha256"],
            profile=p.STANDALONE_PROFILE,
        )


STANDALONE_BUILDER_UNIT = r"""import test from 'node:test'
import assert from 'node:assert/strict'
import * as fs from 'node:fs'
import { createHash } from 'node:crypto'
import { resolve } from 'node:path'
const { buildEngine, buildSemanticParity, selectBuild } =
  await import(process.env.BUILDER_MODULE_URL)
const token = '11111111-2222-3333-4444-555555555555'
const profile = 'i05-source-package-parity'
const contract = JSON.parse(fs.readFileSync(new URL(
  '../docs/iterations/T03/i05-semantic-parity-profile/private-profile-contract-v1.json',
  process.env.BUILDER_MODULE_URL), 'utf8'))
const expectedImports = [
  'ontolearn_engine', 'ontolearn_engine.quality',
  ...['rule_calendar', 'rule_comparator', 'rule_firing', 'rule_numbers', 'rule_profile',
      'rule_revalidation', 'rule_terms'].map(n => 'ontolearn_engine.quality.' + n),
  ...['resources', 'semantic', 'semantic_error_adapter', 'semantic_execution', 'semantic_offline',
      'semantic_profile_directsteps', 'semantic_profile_input', 'semantic_profile_production',
      'semantic_profile_restore', 'semantic_profile_restore_budget', 'semantic_query',
      'semantic_scopes', 'semantic_turtle', 'semantic_source_package_probe',
      'semantic_build_provenance'].map(n => 'ontolearn_engine.' + n),
  '_i05_semantic_parity_build_anchor',
]
const exclusions = ['quality.definitions', 'quality.planning', '__main__', 'worker',
  'coordinator', 'job_store', 'storage', 'storage_probe', 'protocol', 'semantic_samples']
  .map(n => 'ontolearn_engine.' + n)
const phases = ['prepare', 'pyinstaller', 'finalize']
const rootParent = new URL('./standalone-tmp/', import.meta.url)
fs.mkdirSync(rootParent, { recursive: true })
const sha = raw => createHash('sha256').update(raw).digest('hex')
function fixture(t, behavior = {}) {
  const root = fs.mkdtempSync(new URL('builder-', rootParent))
  t.after(() => fs.rmSync(root, { recursive: true, force: true }))
  const runRoot = resolve(root, 'build/i05-semantic-parity', token)
  const artifact = resolve(runRoot, 'dist/ontolearn-semantic-parity')
  const evidence = resolve(runRoot, 'evidence')
  const calls = []
  const run = (command, args, options) => {
    const phase = phases[calls.length]
    if (!phase) throw new Error('unexpected additional subprocess')
    calls.push({command, args, options, phase})
    assert.equal(command, 'uv')
    assert.equal(options.shell, false)
    assert.equal(options.stdio[0], 'ignore')
    assert.equal(typeof options.stdio[1], 'number')
    assert.equal(typeof options.stdio[2], 'number')
    assert.notEqual(options.stdio[1], options.stdio[2])
    assert.equal(options.cwd, root)
    const controls = phase === 'prepare' ? {
      provenancePath: resolve(runRoot, 'provenance/i05/source-package-parity-build.json'),
      contractPath: resolve(runRoot,
        'provenance/i05/source-package-parity-private-contract-v1.json'),
      generatedDir: resolve(runRoot, 'generated'),
      anchorPath: resolve(runRoot, 'generated/_i05_semantic_parity_build_anchor.py'),
    } : {
      bindingPath: resolve(runRoot, 'artifact-binding-v1.json'), bindingSha256: 'a'.repeat(64),
      engineDirectory: artifact, provenanceSha256: 'b'.repeat(64),
    }
    if (phase === 'prepare') {
      fs.mkdirSync(resolve(runRoot, 'generated'))
      fs.mkdirSync(resolve(runRoot, 'provenance/i05'), {recursive:true})
      fs.mkdirSync(resolve(runRoot, 'licenses'))
    } else if (phase === 'pyinstaller') {
      fs.mkdirSync(artifact, {recursive:true})
      fs.writeFileSync(resolve(artifact, 'ontolearn-semantic-parity'), 'inert unit artifact')
    } else {
      fs.writeFileSync(controls.bindingPath, 'unit binding; unapproved')
    }
    let stdout = phase === 'pyinstaller' ? 'complete package stdout\n' : JSON.stringify(controls)
    let stderr = `complete ${phase} stderr\n`
    if (behavior.stdout) stdout = behavior.stdout(phase, stdout, controls)
    if (behavior.stderr) stderr = behavior.stderr(phase, stderr)
    fs.writeSync(options.stdio[1], stdout)
    fs.writeSync(options.stdio[2], stderr)
    const result = {status:0, signal:null, pid:2000 + calls.length}
    return behavior.result ? behavior.result(phase, result) : result
  }
  return {root, runRoot, artifact, evidence, calls, run}
}
function invoke(f, extra = {}) {
  return buildSemanticParity({repositoryRoot:f.root, run:f.run, uuid:() => token, ...extra})
}
function receipt(f, phase) {
  return JSON.parse(fs.readFileSync(resolve(f.evidence, `${phase}.receipt.json`), 'utf8'))
}
function verifyStreams(f, phase, complete) {
  const observed = receipt(f, phase)
  const call = f.calls.find(c => c.phase === phase)
  assert.deepEqual(Object.keys(observed).sort(), ['format', 'profile', 'phase', 'argv', 'cwd',
    'environment', 'pid', 'startUtc', 'endUtc', 'status', 'signal', 'error', 'ioError', 'overflow',
    'complete', 'stdout', 'stderr', 'captureRange',
    'stdoutPath', 'stderrPath', 'receiptPath'].sort())
  for (const channel of ['stdout','stderr'])
    assert.equal(observed[channel + 'Path'], resolve(f.evidence,`${phase}.${channel}.log`))
  assert.equal(observed.receiptPath, resolve(f.evidence,`${phase}.receipt.json`))
  assert.equal(observed.format, 'i05-semantic-parity-child/1')
  assert.equal(observed.profile, profile)
  assert.equal(observed.phase, phase)
  assert.deepEqual(observed.argv, [call.command, ...call.args])
  assert.equal(observed.cwd, f.root)
  assert.deepEqual(observed.environment, call.options.env)
  const allowedEnv = new Set(['PATH','HOME','LANG','LC_ALL','LC_CTYPE','SYSTEMROOT','WINDIR',
    'VIRTUAL_ENV','UV_PROJECT_ENVIRONMENT','UV_NO_SYNC','UV_OFFLINE','UV_PYTHON_DOWNLOADS',
    'UV_CACHE_DIR','PYTHONDONTWRITEBYTECODE','PYTHONNOUSERSITE','PYTHONPATH','TMPDIR',
    'PYINSTALLER_CONFIG_DIR'])
  assert(Object.keys(observed.environment).every(key => allowedEnv.has(key)))
  assert.equal(observed.environment.UV_NO_SYNC, '1')
  assert.equal(observed.environment.UV_OFFLINE, '1')
  assert.equal(observed.environment.UV_PYTHON_DOWNLOADS, 'never')
  assert.equal(observed.environment.UV_CACHE_DIR, resolve(f.evidence,'cache/uv'))
  assert.equal(observed.environment.PYINSTALLER_CONFIG_DIR, resolve(f.evidence,'cache/pyinstaller'))
  assert.equal(observed.environment.TMPDIR, resolve(f.evidence,'tmp'))
  assert.equal(observed.pid, 2000 + f.calls.indexOf(call) + 1)
  assert.equal(observed.complete, complete)
  assert(Number.isFinite(Date.parse(observed.startUtc)))
  assert(Date.parse(observed.endUtc) >= Date.parse(observed.startUtc))
  for (const channel of ['stdout', 'stderr']) {
    const expectedPath = resolve(f.evidence, `${phase}.${channel}.log`)
    const raw = fs.readFileSync(expectedPath)
    assert.deepEqual(observed[channel], {path: expectedPath, bytes:raw.length, sha256:sha(raw)})
    assert.deepEqual(observed.captureRange[channel], [0, raw.length])
  }
  return observed
}

test('standalone dispatch is exact and never runs while choosing', () => {
  assert.equal(selectBuild([]), buildEngine)
  assert.equal(selectBuild(['--i05-source-package-parity']), buildSemanticParity)
  for (const argv of [['--unknown'], ['--i05-source-package-parity', 'extra'],
    ['--i05-source-package-parity=full-v1']]) assert.throws(() => selectBuild(argv))
})

test('standalone collects exact code and data, returns6, never publishes parent stage', (t) => {
  const f = fixture(t)
  const stage = resolve(f.root, 'build/engine/ontolearn-engine')
  fs.mkdirSync(stage, {recursive:true})
  fs.writeFileSync(resolve(stage, 'old'), 'original stage')
  const result = invoke(f)
  assert.deepEqual(Object.keys(result).sort(), ['profile','artifactDirectory','bindingPath',
    'bindingSha256','provenanceSha256','rootApproved'].sort())
  assert.equal(result.profile, profile)
  assert.equal(result.artifactDirectory, f.artifact)
  assert.equal(result.bindingPath, resolve(f.runRoot,'artifact-binding-v1.json'))
  assert.equal(result.bindingSha256, 'a'.repeat(64))
  assert.equal(result.provenanceSha256, 'b'.repeat(64))
  assert.equal(result.rootApproved, false)
  assert.equal(f.calls.length, 3)
  assert.equal(fs.readFileSync(resolve(stage, 'old'), 'utf8'), 'original stage')
  const args = f.calls[1].args
  const values = flag => args.flatMap((x, i) => x === flag ? [args[i+1]] : [])
  assert.deepEqual(values('--hidden-import'), expectedImports)
  assert.deepEqual(values('--exclude-module'), exclusions)
  assert.equal(new Set(values('--hidden-import')).size, 25)
  assert.equal(args.at(-1), 'packages/engine/src/ontolearn_engine/semantic_source_package_probe.py')
  assert.deepEqual(values('--name'), ['ontolearn-semantic-parity'])
  assert.deepEqual(values('--optimize'), ['0'])
  assert.equal(args.includes('--collect-data'), false)
  const data = values('--add-data')
  for (const file of ['schema.json','registry.json','errors.json']) {
    assert(data.includes(`${resolve(f.root,'packages/contracts/v2',file)}:contracts/v2`))
  }
  assert(data.includes(`${resolve(f.root,'packages/contracts/python/contract_v2.py')}:contracts/python`))
  assert(data.includes(`${resolve(f.runRoot,'provenance/i05/source-package-parity-build.json')}:provenance/i05`))
  assert(data.includes(`${resolve(f.runRoot,'provenance/i05/source-package-parity-private-contract-v1.json')}:provenance/i05`))
  for (const file of ['i05-source-package-parity-manifest.json',
    'i05-source-package-parity-inputs.json']) {
    assert(data.includes(`${resolve(f.root,'packages/engine/src/ontolearn_engine/probe_inputs',file)}:provenance/i05/source-package-parity`))
  }
  assert.equal(data.some(x => x.startsWith(resolve(f.root,'packages/contracts/v2') + ':')), false)
  for (const phase of phases) {
    const raw = verifyStreams(f, phase, true)
    assert.equal(raw.status, 0)
    assert.equal(raw.error, null)
    assert.equal(raw.ioError, null)
    assert.equal(raw.overflow, false)
    assert(fs.readFileSync(raw.stderr.path, 'utf8').includes(`${phase} stderr`))
  }
})

for (const failedPhase of phases) test(
  `standalone ${failedPhase} nonzero preserves raw first failure`, (t) => {
  const f = fixture(t, {result:(phase,result) => phase === failedPhase ?
    {...result,status:7} : result})
  assert.throws(() => invoke(f), /BUILD_PARITY_CHILD_FAILED/)
  assert.equal(f.calls.length, phases.indexOf(failedPhase) + 1)
  const raw = verifyStreams(f, failedPhase, true)
  assert.equal(raw.status, 7)
  assert.equal(raw.error, null)
  assert(fs.readFileSync(raw.stderr.path,'utf8').includes(`${failedPhase} stderr`))
})

for (const code of ['ENOBUFS','ERR_CHILD_PROCESS_STDIO_MAXBUFFER']) test(
  `standalone ${code} reports incomplete captured range`, (t) => {
  const f = fixture(t, {result:(_phase,result) => ({...result,status:null,
    error:Object.assign(new Error('synthetic overflow'), {code})})})
  assert.throws(() => invoke(f), /BUILD_PARITY_CHILD_FAILED/)
  assert.equal(f.calls.length,1)
  const raw = verifyStreams(f,'prepare',false)
  assert.equal(raw.overflow,true)
  assert.equal(raw.error.code,code)
  assert(raw.stdout.bytes > 0 && raw.stderr.bytes > 0)
})

test('standalone spawn error preserves both direct raw streams without rerun', (t) => {
  const f = fixture(t, {result:(_phase,result) => ({...result,status:null,
    error:Object.assign(new Error('synthetic spawn error'), {code:'ENOENT'})})})
  assert.throws(() => invoke(f), /BUILD_PARITY_CHILD_FAILED/)
  assert.equal(f.calls.length,1)
  const raw = verifyStreams(f,'prepare',false)
  assert.equal(raw.overflow,false)
  assert.equal(raw.error.code,'ENOENT')
})

for (const invalid of ['malformed','oversize','unknownKey','nonString','duplicate','BOM',
  'nonJSONWhitespace','invalidUTF8']) test(
  `standalone ${invalid} control preserves full raw`, (t) => {
  const f = fixture(t, {stdout:(phase,stdout,controls) => {
    if (phase !== 'prepare') return stdout
    if (invalid === 'malformed') return '{bad json'
    if (invalid === 'oversize') return 'x'.repeat(65537)
    if (invalid === 'unknownKey') return JSON.stringify({...controls, approved:true})
    if (invalid === 'duplicate') {
      const {anchorPath, ...rest} = controls
      return JSON.stringify(rest).slice(0,-1) + ',"anchorPath":"wrong","anchorPath":' +
        JSON.stringify(anchorPath) + '}'
    }
    if (invalid === 'BOM') return '\uFEFF' + stdout
    if (invalid === 'nonJSONWhitespace') return '\v' + stdout
    if (invalid === 'invalidUTF8') return Buffer.from([255])
    return JSON.stringify({...controls, anchorPath:7})
  }})
  assert.throws(() => invoke(f), /BUILD_PARITY_HELPER_OUTPUT_INVALID/)
  assert.equal(f.calls.length,1)
  const raw = verifyStreams(f,'prepare',true)
  assert.equal(raw.status,0)
  if (invalid === 'oversize') assert.equal(raw.stdout.bytes,65537)
  assert(fs.existsSync(resolve(f.evidence,'prepare.control.json')))
})

test('standalone exact 64KiB valid control keeps the complete accepted raw range', (t) => {
  const f = fixture(t, {stdout:(phase,stdout) => phase === 'prepare' ?
    stdout + ' '.repeat(65536 - Buffer.byteLength(stdout)) : stdout})
  invoke(f)
  assert.equal(f.calls.length,3)
  const raw = verifyStreams(f,'prepare',true)
  assert.equal(raw.stdout.bytes,65536)
  const control = JSON.parse(fs.readFileSync(resolve(f.evidence,'prepare.control.json'),'utf8'))
  assert.equal(control.accepted,true)
  assert.equal(control.stdout.sha256,raw.stdout.sha256)
})

test('standalone machine scratch map agrees with actual argv env paths and receipts', (t) => {
  const f = fixture(t)
  const result = invoke(f)
  const scratch = contract.buildScratch
  assert.equal(scratch.repositoryRelativeRunRoot,contract.fixedLayout.uniqueBuildRoot)
  assert.equal(resolve(f.root,scratch.repositoryRelativeRunRoot.replace('<fresh-uuid>',token)),
    f.runRoot)
  assert.equal(scratch.pathBase,'runRoot')
  for (const relative of Object.values(scratch.paths)) {
    assert.equal(typeof relative,'string')
    assert(!relative.startsWith('/') && !relative.split('/').includes('..'))
    assert(resolve(f.runRoot,relative).startsWith(f.runRoot + '/'))
  }
  const actualPath = key => resolve(f.runRoot,scratch.paths[key])
  const packageArgs = f.calls[1].args
  for (const [option,key] of Object.entries(scratch.argv)) {
    const index = packageArgs.indexOf(option)
    assert(index >= 0)
    assert.equal(packageArgs[index+1],actualPath(key))
  }
  assert.equal(result.artifactDirectory,actualPath('artifactDirectory'))
  assert.equal(result.bindingPath,actualPath('binding'))
  assert.equal(f.evidence,actualPath('evidence'))
  assert.deepEqual(JSON.parse(fs.readFileSync(actualPath('buildRequest'),'utf8')),
    {profile,token})
  assert.equal(f.calls[0].args.at(-1),f.runRoot)
  assert.deepEqual(f.calls[2].args.slice(-2),[f.runRoot,actualPath('artifactDirectory')])
  assert(packageArgs.includes(actualPath('licenses') + ':licenses'))
  for (const key of ['provenance','contract']) {
    assert(packageArgs.includes(actualPath(key) + ':provenance/i05'))
    assert.equal(scratch.paths[key],contract.fixedLayout[
      key === 'provenance' ? 'embeddedProvenance' : 'embeddedContract'])
  }
  assert.equal(scratch.paths.provenanceRoot,'provenance')
  assert(actualPath('provenance').startsWith(actualPath('provenanceRoot') + '/'))
  assert.equal(scratch.paths.generatedAnchor,contract.fixedLayout.generatedAnchor)
  for (const call of f.calls) {
    for (const [env,key] of Object.entries(scratch.environment))
      assert.equal(call.options.env[env],actualPath(key))
    for (const [kind,template] of Object.entries(scratch.phasePaths)) {
      const path = resolve(f.runRoot,template.replace('<phase>',call.phase))
      if (kind === 'control') {
        assert.equal(fs.existsSync(path),scratch.controlPhases.includes(call.phase))
      } else {
        assert(fs.existsSync(path))
        const raw = receipt(f,call.phase)
        assert.equal(raw[kind + 'Path'],path)
      }
    }
  }
  assert.deepEqual(scratch.phases,f.calls.map(call => call.phase))
  assert.deepEqual(packageArgs.flatMap((x,i) => x === '--hidden-import' ?
    [packageArgs[i+1]] : []),contract.analysisImports)
  for (const mapping of contract.inputMappings) {
    const source = resolve(f.root,'packages/engine/src',mapping.sourcePath)
    assert(packageArgs.includes(source + ':' + mapping.path.slice(0,mapping.path.lastIndexOf('/'))))
  }
})

test('standalone helper output paths cannot redirect the fixed target layout', (t) => {
  const f = fixture(t, {stdout:(phase,stdout,controls) => phase === 'prepare' ?
    JSON.stringify({...controls, provenancePath:resolve(f.root,'outside')}) : stdout})
  assert.throws(() => invoke(f), /HELPER_PATH_INVALID/)
  assert.equal(f.calls.length,1)
  verifyStreams(f,'prepare',true)
})

test('standalone invalid final binding never publishes or adds a child', (t) => {
  const f = fixture(t, {stdout:(phase,stdout,controls) => phase === 'finalize' ?
    JSON.stringify({...controls, engineDirectory:resolve(f.root,'foreign')}) : stdout})
  assert.throws(() => invoke(f), /BINDING_INVALID/)
  assert.equal(f.calls.length,3)
  verifyStreams(f,'finalize',true)
  assert.equal(fs.existsSync(resolve(f.root,'build/engine')),false)
})

for (const failedPhase of phases) test(
  `standalone ${failedPhase} hash IO failure keeps actual paths and first raw bytes`, (t) => {
  const f = fixture(t)
  const stdoutReadHandles = new Set()
  const io = {...fs, openSync:(path,...args) => {
    const fd = fs.openSync(path,...args)
    if (String(path).endsWith(`${failedPhase}.stdout.log`) && args[0] === 'r')
      stdoutReadHandles.add(fd)
    return fd
  }, readSync:(fd,...args) => {
    if (stdoutReadHandles.has(fd)) throw Object.assign(new Error('synthetic read IO'), {code:'EIO'})
    return fs.readSync(fd,...args)
  }, closeSync:fd => {stdoutReadHandles.delete(fd); return fs.closeSync(fd)}}
  assert.throws(() => invoke(f,{io}), /BUILD_PARITY_EVIDENCE_IO_FAILED/)
  assert.equal(f.calls.length,phases.indexOf(failedPhase) + 1)
  assert(fs.readFileSync(resolve(f.evidence,`${failedPhase}.stdout.log`)).length > 0)
  assert(fs.readFileSync(resolve(f.evidence,`${failedPhase}.stderr.log`)).length > 0)
  const raw = receipt(f,failedPhase)
  assert.equal(raw.complete,false)
  assert.equal(raw.ioError.code,'EIO')
  assert.equal(raw.stdout,null)
  assert.equal(raw.captureRange.stdout,null)
  assert.equal(raw.stdoutPath,resolve(f.evidence,`${failedPhase}.stdout.log`))
  assert.equal(raw.stderrPath,resolve(f.evidence,`${failedPhase}.stderr.log`))
  assert.equal(raw.receiptPath,resolve(f.evidence,`${failedPhase}.receipt.json`))
  assert(fs.existsSync(raw.stdoutPath) && fs.existsSync(raw.stderrPath))
  assert(fs.readFileSync(raw.stdoutPath).length > 0)
  assert.equal(raw.stderr.sha256,sha(fs.readFileSync(raw.stderrPath)))
  assert.deepEqual(raw.captureRange.stderr,[0,fs.readFileSync(raw.stderrPath).length])
})

test('standalone control read failure is separate from already complete raw capture', (t) => {
  const f = fixture(t)
  const io = {...fs, readFileSync:(path,...args) => {
    if (String(path).endsWith('prepare.stdout.log'))
      throw Object.assign(new Error('synthetic control read IO'), {code:'EIO'})
    return fs.readFileSync(path,...args)
  }}
  assert.throws(() => invoke(f,{io}), /BUILD_PARITY_EVIDENCE_IO_FAILED/)
  assert.equal(f.calls.length,1)
  const raw = verifyStreams(f,'prepare',true)
  assert.equal(raw.ioError,null)
  const control = JSON.parse(fs.readFileSync(resolve(f.evidence,'prepare.control.json'),'utf8'))
  assert.equal(control.accepted,false)
  assert.equal(control.code,'BUILD_PARITY_EVIDENCE_IO_FAILED')
  assert.equal(control.error.code,'EIO')
  assert.equal(control.stdout.sha256,raw.stdout.sha256)
})

test('standalone receipt write IO failure keeps channels and never returns success', (t) => {
  const f = fixture(t)
  const io = {...fs, writeFileSync:(path,...args) => {
    if (String(path).endsWith('prepare.receipt.json'))
      throw Object.assign(new Error('synthetic receipt IO'), {code:'EIO'})
    return fs.writeFileSync(path,...args)
  }}
  assert.throws(() => invoke(f,{io}), /BUILD_PARITY_EVIDENCE_IO_FAILED/)
  assert.equal(f.calls.length,1)
  assert(fs.readFileSync(resolve(f.evidence,'prepare.stdout.log')).length > 0)
  assert(fs.readFileSync(resolve(f.evidence,'prepare.stderr.log')).length > 0)
})

test('standalone opening stderr failure closes the first handle and never launches', (t) => {
  const f = fixture(t)
  const closed = [], retained = new Set()
  const io = {...fs, openSync:(path,...args) => {
    if (String(path).endsWith('prepare.stderr.log'))
      throw Object.assign(new Error('synthetic open IO'), {code:'EIO'})
    const fd = fs.openSync(path,...args)
    retained.add(fd)
    return fd
  }, closeSync:fd => {closed.push(fd); retained.delete(fd); return fs.closeSync(fd)}}
  assert.throws(() => invoke(f,{io}), /BUILD_PARITY_EVIDENCE_IO_FAILED/)
  assert.equal(f.calls.length,0)
  assert(closed.length >= 1)
  assert.equal(retained.size,0)
})

test('standalone large raw channels exceed the old pipe buffer without truncation', (t) => {
  const f = fixture(t, {stdout:(phase,stdout) => phase === 'pyinstaller' ?
    'O'.repeat(4 * 1024 * 1024 + 17) : stdout,
    stderr:(_phase,_stderr) => 'E'.repeat(4 * 1024 * 1024 + 31)})
  invoke(f)
  const raw = verifyStreams(f,'pyinstaller',true)
  assert.equal(raw.stdout.bytes,4 * 1024 * 1024 + 17)
  assert.equal(raw.stderr.bytes,4 * 1024 * 1024 + 31)
  assert.equal(fs.readFileSync(raw.stdout.path).at(-1),79)
  assert.equal(fs.readFileSync(raw.stderr.path).at(-1),69)
})

test('standalone thrown runner preserves partial channels and reports actual failure', (t) => {
  const f = fixture(t)
  const throwingRun = (...args) => {
    f.run(...args)
    throw Object.assign(new Error('synthetic throw after writes'), {code:'EIO'})
  }
  assert.throws(() => invoke(f,{run:throwingRun}), /BUILD_PARITY_CHILD_FAILED/)
  assert.equal(f.calls.length,1)
  const raw = receipt(f,'prepare')
  assert.equal(raw.error.code,'EIO')
  assert.equal(raw.complete,false)
  assert.equal(raw.status,null)
  for (const channel of ['stdout','stderr']) {
    const bytes = fs.readFileSync(resolve(f.evidence,`prepare.${channel}.log`))
    assert.equal(raw[channel].sha256,sha(bytes))
    assert(bytes.length > 0)
  }
})

test('standalone signal has no synthetic zero exit and does not finalize', (t) => {
  const f = fixture(t, {result:(_phase,result) => ({...result,status:null,signal:'SIGTERM'})})
  assert.throws(() => invoke(f), /BUILD_PARITY_CHILD_FAILED/)
  assert.equal(f.calls.length,1)
  const raw = receipt(f,'prepare')
  assert.equal(raw.status,null)
  assert.equal(raw.signal,'SIGTERM')
  assert.equal(raw.stdout.sha256,sha(fs.readFileSync(raw.stdout.path)))
  assert.equal(raw.stderr.sha256,sha(fs.readFileSync(raw.stderr.path)))
})

test('standalone repeated UUID preserves all original evidence and artifact', (t) => {
  const f = fixture(t)
  const result = invoke(f)
  const original = fs.readFileSync(result.bindingPath)
  const originalReceipt = fs.readFileSync(resolve(f.evidence,'prepare.receipt.json'))
  assert.throws(() => invoke(f), /OUTPUT_EXISTS/)
  assert.equal(f.calls.length,3)
  assert.deepEqual(fs.readFileSync(result.bindingPath),original)
  assert.deepEqual(fs.readFileSync(resolve(f.evidence,'prepare.receipt.json')),originalReceipt)
})

test('standalone rejects an ancestor symlink before any child or outside write', (t) => {
  const f = fixture(t)
  fs.mkdirSync(resolve(f.root,'build'))
  const outside = resolve(f.root,'outside-not-created')
  fs.symlinkSync(outside,resolve(f.root,'build/i05-semantic-parity'))
  assert.throws(() => invoke(f), /DIRECTORY_INVALID/)
  assert.equal(f.calls.length,0)
  assert.equal(fs.existsSync(outside),false)
})
"""


def test_standalone_node_builder_uses_only_fd_run_stubs(tmp_path):
    script = tmp_path / "standalone-builder-unit.mjs"
    script.write_text(STANDALONE_BUILDER_UNIT)
    result = subprocess.run(
        ["node", "--test", "--test-reporter=tap", str(script)],
        cwd=REPOSITORY,
        env={
            **os.environ,
            "BUILDER_MODULE_URL": (REPOSITORY / "scripts/build-engine.mjs").as_uri(),
        },
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "# pass 31" in result.stdout
    assert "# fail 0" in result.stdout


def test_standalone_exact_builder_reservation_keeps_open_stream_evidence(
    standalone_case, monkeypatch, tmp_path
):
    value = standalone_case
    repository = tmp_path / "repository"
    write(repository, p.STANDALONE_CONTRACT_SOURCE, STANDALONE_CONTRACT_RAW)
    output = repository / "build/i05-semantic-parity" / str(uuid.uuid4())
    evidence = output / "evidence"
    (evidence / "cache").mkdir(parents=True)
    (evidence / "tmp").mkdir()
    request = p._canonical({"profile": p.STANDALONE_PROFILE, "token": output.name})
    write(evidence, "build-request-v1.json", request)
    stdout, stderr = b"first stdout", b"first stderr"
    write(evidence, "prepare.stdout.log", stdout)
    write(evidence, "prepare.stderr.log", stderr)
    monkeypatch.setattr(p, "_collect_standalone_manifest", lambda *_a: value.manifest)
    monkeypatch.setattr(p.sysconfig, "get_path", lambda _kind: str(value.root))
    result = p.prepare_build(repository, output, profile=p.STANDALONE_PROFILE)
    assert Path(result["provenancePath"]).parent == output / "provenance/i05"
    assert (evidence / "build-request-v1.json").read_bytes() == request
    assert (evidence / "prepare.stdout.log").read_bytes() == stdout
    assert (evidence / "prepare.stderr.log").read_bytes() == stderr


def test_standalone_carchive_unknown_runtimehook_is_not_silently_collected(tmp_path):
    raw = synthetic_carchive(
        synthetic_pyz([("safe", parser_fixture_code(), 0)]),
        parser_fixture_code(),
        extra=(("pyi_rth_unknown", b"s", marshal.dumps(parser_fixture_code(), 4), 1),),
    )
    target = tmp_path / "inert-launcher"
    target.write_bytes(raw)
    with fault("ARCHIVE_MISMATCH"):
        p._bounded_archive(target)


@pytest.mark.parametrize("field", ["bytes", "sha256", "codeSha256"])
def test_standalone_target_identity_must_equal_canonical_private_writer(standalone_case, field):
    value = standalone_case
    value.manifest["entrypoint"][field] = (
        value.manifest["entrypoint"][field] + 1 if field == "bytes" else "0" * 64
    )
    value.refresh()
    with fault("SOURCE_MISMATCH"):
        value.load()


def test_standalone_declared_contract_bytes_must_be_exact(standalone_case):
    value = standalone_case
    value.manifest["contract"]["bytes"] += 1
    value.manifest["buildInputs"][-1] = copy.deepcopy(value.manifest["contract"])
    value.refresh()
    with fault("CONTRACT_MISMATCH"):
        value.load()


def test_standalone_rejects_parent_contract_before_using_its_schema(standalone_case):
    value = standalone_case
    (value.root / p.STANDALONE_CONTRACT_BUNDLED).write_bytes(CONTRACT_RAW)
    with fault("CONTRACT_MISMATCH"):
        value.load()


def test_code_graph_depth_and_node_caps_are_checked_before_normalization(monkeypatch):
    code = parser_fixture_code()
    with monkeypatch.context() as scoped:
        scoped.setattr(p, "ENTRY_CAP", 1)
        with fault("LIMIT_EXCEEDED"):
            p._marshal_exact(marshal.dumps(code, 4), "code")
    for _ in range(70):
        code = code.replace(co_consts=(code,))
    with fault("LIMIT_EXCEEDED"):
        p._marshal_exact(marshal.dumps(code, 4), "code")


def test_standalone_carchive_known_option_cannot_select_another_layout(tmp_path):
    raw = synthetic_carchive(
        synthetic_pyz([("safe", parser_fixture_code(), 0)]),
        parser_fixture_code(),
        extra=(("pyi-contents-directory foreign", b"o", b"", 0),),
    )
    target = tmp_path / "inert-launcher"
    target.write_bytes(raw)
    with fault("ARCHIVE_MISMATCH"):
        p._bounded_archive(target)


@pytest.mark.parametrize(
    "raw",
    [
        b"[" + struct.pack("<i", 2**31 - 1),
        b"s" + struct.pack("<i", 2**31 - 1),
        b"(" + struct.pack("<i", -1),
        b"l" + struct.pack("<i", 2**31 - 1),
        b"r" + struct.pack("<i", -1),
        b"r" + struct.pack("<i", 2**31 - 1),
        bytes([ord("[") | 0x80]) + struct.pack("<i", 1) + b"r" + struct.pack("<i", 0),
        (b"[" + struct.pack("<i", 1)) * 70 + b"N",
        b"c" + b"\0" * 20,
        b"z\xffshort",
        marshal.dumps({"dictTOC": (0, 12, 1)}, 4),
    ],
)
def test_marshal_allocation_and_reference_preflight_happens_before_load(monkeypatch, raw):
    monkeypatch.setattr(
        p.marshal, "load", lambda *_a: pytest.fail("untrusted marshal.load reached")
    )
    with pytest.raises(p.BuildProvenanceFault):
        p._marshal_exact(raw, "toc")


@pytest.mark.parametrize(
    "raw",
    [
        b"c" + b"\0" * 20,
        # A tiny code declaration whose first field is not bytes.
        b"c" + b"\0" * 20 + b"N",
        # localsplusnames has one item while localspluskinds has no bytes.
        b"c"
        + b"\0" * 20
        + b"s"
        + struct.pack("<i", 0)
        + b")\0"
        + b")\0"
        + b")\x01z\x01x"
        + b"s"
        + struct.pack("<i", 0)
        + b"z\x01f" * 3
        + struct.pack("<i", 0)
        + (b"s" + struct.pack("<i", 0)) * 2,
    ],
)
def test_code_field_preflight_happens_before_marshal_load(monkeypatch, raw):
    monkeypatch.setattr(
        p.marshal, "load", lambda *_a: pytest.fail("malformed code reached marshal.load")
    )
    with pytest.raises(p.BuildProvenanceFault):
        p._marshal_exact(raw, "code")


@pytest.mark.parametrize("limit", ["depth", "expandedPayload", "expandedNodes"])
def test_loader_code_graph_is_bounded_before_normalization(monkeypatch, limit):
    code = parser_fixture_code()
    if limit == "depth":
        nested = None
        for _ in range(70):
            nested = (nested,)
        constants = (nested,)
    elif limit == "expandedPayload":
        # Repeated references must count each expansion, not only unique objects.
        chunk = b"x" * 1024
        constants = ((chunk,) * 2049,)
    else:
        chunk = (None,) * 1000
        constants = ((chunk,) * 201,)
    code = code.replace(co_consts=constants)
    monkeypatch.setattr(
        p, "_normalized", lambda *_a: pytest.fail("unbounded normalization reached")
    )
    with fault("LIMIT_EXCEEDED"):
        p._bounded_code_sha(code)


def test_loader_code_graph_preserves_the_existing_fingerprint():
    code = parser_fixture_code()
    assert p._bounded_code_sha(code) == p._code_sha(code)


def test_standalone_contract_source_and_frozen_domains_are_relational():
    contract = STANDALONE_CONTRACT
    layout = contract["fixedLayout"]
    domains = contract["pathDomains"]
    mappings = contract["inputMappings"]
    assert domains["inputs"]["mappingField"] == "inputMappings"
    assert domains["inputs"]["sourceRoot"] == "repository/packages/engine/src"
    assert domains["inputs"]["frozenRoot"] == "sys._MEIPASS"
    assert domains["inputs"]["sourcePaths"] == [row["path"] for row in p.FIXED_INPUTS]
    assert domains["inputs"]["rowPaths"] == [row["path"] for row in p.STANDALONE_INPUTS]
    assert len(mappings) == len(contract["fixedInputs"]) == 2
    for mapping, source, frozen in zip(mappings, p.FIXED_INPUTS, p.STANDALONE_INPUTS, strict=True):
        assert mapping == {"sourcePath": source["path"], **frozen}
        assert mapping["sourcePath"] != mapping["path"]
        assert mapping["bytes"] == source["bytes"]
        assert mapping["sha256"] == source["sha256"]
    assert domains["contract"]["rowPath"] == p.STANDALONE_CONTRACT_SOURCE
    assert domains["contract"]["frozenRoot"] == "sys._MEIPASS"
    assert domains["contract"]["frozenPath"] == layout["embeddedContract"]
    assert layout["embeddedContract"] == p.STANDALONE_CONTRACT_BUNDLED
    assert p.CONTRACT_SOURCE != domains["contract"]["rowPath"]
    assert p.CONTRACT_BUNDLED != domains["contract"]["frozenPath"]
    assert domains["provenance"]["rowPath"] == domains["provenance"]["frozenPath"]
    assert domains["provenance"]["frozenPath"] == layout["embeddedProvenance"]
    assert layout["embeddedProvenance"] == p.STANDALONE_PROVENANCE
    assert domains["anchor"]["module"] == layout["anchorModule"] == p.STANDALONE_ANCHOR
    assert domains["anchor"]["generatedPath"] == layout["generatedAnchor"]
    assert domains["anchor"]["constants"] == layout["anchorConstants"]
    assert layout["anchorConstants"] == ["PROVENANCE_SHA256", "CONTRACT_SHA256", "PROFILE"]
    assert domains["licenseMirrors"]["sourceRow"] == "distributions[].licenses[]"
    assert domains["licenseMirrors"]["rowPath"] == (
        "licenses/<distribution>/<original-dist-info-relative-path>"
    )
    assert domains["licenseMirrors"]["frozenRoot"] == "sys._MEIPASS"
    assert "sha256" not in contract  # The source identity cannot be self-embedded.


def test_standalone_contract_target_and_launcher_domains_match_archive_and_runtime(standalone_case):
    contract = STANDALONE_CONTRACT
    domains = contract["pathDomains"]
    target = domains["entrypoint"]
    layout = contract["fixedLayout"]
    schema = contract["schemas"]["artifactBinding"]
    target_schema = schema["properties"]["targetCode"]
    assert target["rowPath"] == layout["target"] == p.STANDALONE_TARGET
    assert target["canonicalModule"] == p.PRIVATE_MODULES[0]
    assert target["frozenPath"] is None
    assert target["runtimeDomain"] == "canonical-PYZ-loader-code-only"
    assert target["externalDomain"] == "target-CArchive-code-plus-complete-directory-binding"
    assert target["archiveEntry"] == contract["archivePolicy"]["businessScript"]
    assert target["archiveTypecode"] == "s"
    assert target["targetCodeKeys"] == target_schema["required"]
    assert set(target_schema["properties"]) == set(target["targetCodeKeys"])
    for key, value in {
        "archiveEntry": target["archiveEntry"],
        "typecode": target["archiveTypecode"],
        "sourcePath": target["rowPath"],
    }.items():
        assert target_schema["properties"][key]["const"] == value
    assert layout["launcher"] == schema["properties"]["launcher"]["const"]
    assert layout["launcher"] == "ontolearn-semantic-parity"
    assert contract["bindingKindRules"]["file"]["launcherRule"] == (
        layout["launcher"] + " must be a regular file and mode&0o111 nonzero"
    )
    assert contract["analysisImports"] == [
        *p.SUPPLIER_MODULES,
        *p.PRIVATE_MODULES,
        p.STANDALONE_ANCHOR,
    ]
    assert len(p.SUPPLIER_MODULES + p.PRIVATE_MODULES) == 24
    assert len(set(contract["analysisImports"])) == 25
    evidence = standalone_case.load()
    runtime = p.verify_loaded_modules(evidence, standalone_case.modules)
    assert runtime["entrypointDomain"] == (
        "runtime-canonical-PYZ-only; target-CArchive-external-binding-required"
    )
    assert runtime["rootApproval"] == "unknown"
    pyz = p._BoundedPYZ(complete_standalone_pyz(standalone_case))
    actual_target = standalone_case.codes[target["canonicalModule"]]
    external_target = p._verify_standalone_archive(
        pyz, actual_target, standalone_case.manifest, standalone_case.root
    )
    assert set(external_target) == set(target["targetCodeKeys"])
    assert external_target["archiveEntry"] == target["archiveEntry"]
    assert external_target["sourcePath"] == target["rowPath"]
    assert external_target["typecode"] == target["archiveTypecode"]
    assert external_target["codeSha256"] == p._code_sha(actual_target)


def test_standalone_contract_separates_actual_base_historical_components_and_root_approval():
    pins = STANDALONE_CONTRACT["identityRules"]["finalPins"]
    assert type(pins) is dict
    assert pins["implementationBase"] == "c706f8f581785053278f26e48d21d7bebadf09f6"
    assert pins["adoptedM08"] == "a633ef391344cce60807638ecd942d4e2183c7b4"
    assert pins["implementationBase"] != pins["adoptedM08"]
    assert pins["historicalComponentReferences"] == ["2cf", "6891", "401a"]
    assert pins["implementationBase"] not in pins["historicalComponentReferences"]
    assert pins["adoptedM08"] not in pins["historicalComponentReferences"]
    assert "not the current implementation base" in pins["historicalMeaning"]
    assert "never self-approved" in pins["candidateIdentity"]
    assert "Root externally freezes" in pins["finalApproval"]
    assert "packages/engine/entrypoint.py" not in STANDALONE_CONTRACT["sourceGuards"]
    assert STANDALONE_CONTRACT["schemas"]["artifactBinding"]["properties"]["rootApproved"] == {
        "const": False
    }


def test_standalone_contract_defines_conditional_unit_without_granting_build_execution():
    scope = STANDALONE_CONTRACT["identityRules"]["noRuntimeExecutionNow"]
    assert type(scope) is dict
    assert "exact four product paths" in scope["currentScope"]
    assert "zero new blocking P1/P2" in scope["conditionalUnit"]
    assert "separate exact START" in scope["conditionalUnit"]
    assert scope["apiDoesNotAuthorizeExecution"] is True
    assert scope["notGranted"] == [
        "standalone product imports or import smoke outside the separately started designated unit",
        "actual prepare_build or finalize_build",
        "actual PyInstaller or build/CLI/help/version",
        "source/frozen probe comparison or target/native/archive execution",
        "OS probes or physical capacity/runtime guarantees",
    ]
    assert (
        "neither permit digest nor unit/static success grants build execution"
        in scope["laterExecution"]
    )


def test_standalone_contract_requires_all_sixteen_negative_test_domains():
    rows = STANDALONE_CONTRACT["requiredNegativeTests"]
    categories = [row.split(":", 1)[0] for row in rows]
    assert categories == [
        "strict-json",
        "profile",
        "source-domains",
        "contract-relations",
        "resources",
        "license-mirrors",
        "loader",
        "python-native",
        "carchive",
        "pyz",
        "marshal-budget",
        "binding",
        "child-raw",
        "control-json",
        "scratch-contract",
        "parent-compatibility",
    ]
    assert len(rows) == len(set(categories)) == 16
    descriptions = dict(row.split(": ", 1) for row in rows)
    for category, required in {
        "marshal-budget": (
            "pre-load",
            "active/cyclic",
            "before allocation",
            "before normalization",
        ),
        "child-raw": ("all three", "without replay", "known paths"),
        "control-json": ("64KiB inclusive", "exact helper4", "public6"),
        "scratch-contract": ("exact8589934592", "BUILD_SCRATCH_GUARD_REQUIRED", "cannot bypass"),
    }.items():
        assert all(term in descriptions[category] for term in required)


def test_standalone_scratch_policy_is_single_external_accounting_domain_without_quota_claims():
    contract = STANDALONE_CONTRACT
    scratch = contract["buildScratch"]
    assert scratch["format"] == "i05-semantic-parity-build-scratch-map/1"
    assert scratch["repositoryRelativeRunRoot"] == contract["fixedLayout"]["uniqueBuildRoot"]
    assert scratch["repositoryRelativeRunRoot"] == "build/i05-semantic-parity/<fresh-uuid>"
    assert scratch["pathBase"] == "runRoot"
    assert scratch["paths"] == {
        "work": "pyinstaller",
        "spec": "spec",
        "dist": "dist",
        "artifactDirectory": "dist/ontolearn-semantic-parity",
        "uvCache": "evidence/cache/uv",
        "pyinstallerCache": "evidence/cache/pyinstaller",
        "tmp": "evidence/tmp",
        "generated": "generated",
        "generatedAnchor": "generated/_i05_semantic_parity_build_anchor.py",
        "licenses": "licenses",
        "provenance": p.STANDALONE_PROVENANCE,
        "contract": p.STANDALONE_CONTRACT_BUNDLED,
        "binding": "artifact-binding-v1.json",
        "evidence": "evidence",
        "buildRequest": "evidence/build-request-v1.json",
        "provenanceRoot": "provenance",
    }
    assert scratch["environment"] == {
        "UV_CACHE_DIR": "uvCache",
        "PYINSTALLER_CONFIG_DIR": "pyinstallerCache",
        "TMPDIR": "tmp",
    }
    assert scratch["argv"] == {
        "--workpath": "work",
        "--specpath": "spec",
        "--distpath": "dist",
        "--paths": "generated",
    }
    assert scratch["phases"] == ["prepare", "pyinstaller", "finalize"]
    assert scratch["controlPhases"] == ["prepare", "finalize"]
    assert scratch["phasePaths"] == {
        "stdout": "evidence/<phase>.stdout.log",
        "stderr": "evidence/<phase>.stderr.log",
        "receipt": "evidence/<phase>.receipt.json",
        "control": "evidence/<phase>.control.json",
    }
    sampling = scratch["sampling"]
    assert sampling["owner"] == "I05 external caller"
    assert sampling["root"] == "runRoot"
    assert sampling["rootTemplate"] == scratch["repositoryRelativeRunRoot"]
    assert type(sampling["thresholdBytes"]) is int
    assert sampling["thresholdBytes"] == 8 * 1024**3 == 8589934592
    assert sampling["recursive"] is True
    assert sampling["scope"] == "entire own runRoot and all descendants as one accounting domain"
    assert "do not sum child domains again" in sampling["accounting"]
    assert sampling["builderEnforced"] is False
    assert sampling["osHardLimitImplemented"] is False
    assert sampling["runtimeGuarantee"] is False
    assert "no sample" in sampling["evidenceMeaning"]
    assert "does not enforce" in sampling["thresholdMeaning"]
    guard = scratch["executionGuard"]
    assert guard["owner"] == "I05 external caller"
    assert guard["guardRequired"] is True
    assert guard["missingOutcome"] == "BUILD_SCRATCH_GUARD_REQUIRED"
    assert guard["permitDigestMayBypass"] is False
    assert "does not implement OS hard limits" in guard["implementation"]
