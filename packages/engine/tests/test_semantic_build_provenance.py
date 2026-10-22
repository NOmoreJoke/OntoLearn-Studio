"""Private verifier unit boundaries; no real semantic/native/package execution."""

from __future__ import annotations

import copy
import importlib.machinery
import json
import os
import runpy
import shutil
import subprocess
import sys
import types
import uuid
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
