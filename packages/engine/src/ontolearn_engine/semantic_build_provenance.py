"""Private build/loader evidence, deliberately separate from root approval.

No target module is imported by either runtime verifier. The owning probe must
install its audit observer before importing runtime modules and calling the
post-observer verifiers. This module has no command-line entrypoint.
"""

from __future__ import annotations

import ast
import email
import hashlib
import importlib.machinery
import importlib.metadata
import importlib.util
import json
import marshal
import math
import os
import re
import stat
import subprocess
import sys
import sysconfig
import types
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

CONTRACT_SHA256 = "9d97a6a233b47abc23064a9a8f8330080d62f39b3db981de14a148880e202a04"
CONTRACT_SOURCE = "docs/reviews/T03/i05-m08-provenance-20261023/private-contract-v1.json"
CONTRACT_BUNDLED = "provenance/i05-private-contract-v1.json"
PROVENANCE_BUNDLED = "provenance/i05-private-build-provenance-v1.json"
ANCHOR = "_i05_private_build_anchor"
ALGORITHM = "i05-code-object-marshal-filename-normalized/1"
MANIFEST_CAP = 4_194_304
CONTRACT_CAP = 262_144
BINDING_CAP = 8_388_608
CODE_CAP = 2_097_152
INPUT_CAP = 8_388_608
SMALL_CAP = 1_048_576
FILE_CAP = 134_217_728
TOTAL_CAP = 536_870_912
ENTRY_CAP = 16_384
FIXED_DISTRIBUTIONS = {
    "pyparsing": "3.3.3",
    "pyshacl": "0.30.1",
    "rdflib": "7.6.0",
    "owlrl": "7.6.2",
    "packaging": "26.3",
    "prettytable": "3.18.0",
    "wcwidth": "0.9.2",
    "html5rdf": "1.2.1",
}
SUPPLIER_MODULES = (
    "ontolearn_engine",
    "ontolearn_engine.quality",
    "ontolearn_engine.quality.rule_calendar",
    "ontolearn_engine.quality.rule_comparator",
    "ontolearn_engine.quality.rule_firing",
    "ontolearn_engine.quality.rule_numbers",
    "ontolearn_engine.quality.rule_profile",
    "ontolearn_engine.quality.rule_revalidation",
    "ontolearn_engine.quality.rule_terms",
    "ontolearn_engine.resources",
    "ontolearn_engine.semantic",
    "ontolearn_engine.semantic_error_adapter",
    "ontolearn_engine.semantic_execution",
    "ontolearn_engine.semantic_offline",
    "ontolearn_engine.semantic_profile_directsteps",
    "ontolearn_engine.semantic_profile_input",
    "ontolearn_engine.semantic_profile_production",
    "ontolearn_engine.semantic_profile_restore",
    "ontolearn_engine.semantic_profile_restore_budget",
    "ontolearn_engine.semantic_query",
    "ontolearn_engine.semantic_scopes",
    "ontolearn_engine.semantic_turtle",
)
PRIVATE_MODULES = (
    "ontolearn_engine.semantic_source_package_probe",
    "ontolearn_engine.semantic_build_provenance",
)
PUBLIC_PATHS = (
    "contracts/python/contract_v2.py",
    "contracts/v2/schema.json",
    "contracts/v2/registry.json",
    "contracts/v2/errors.json",
)
FIXED_INPUTS = (
    {
        "path": "ontolearn_engine/probe_inputs/i05-source-package-parity-manifest.json",
        "bytes": 21202,
        "sha256": "0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a",
    },
    {
        "path": "ontolearn_engine/probe_inputs/i05-source-package-parity-inputs.json",
        "bytes": 8205267,
        "sha256": "47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa",
    },
)
_ERROR_SUFFIXES = frozenset(
    (
        "MODE_INVALID",
        "JSON_INVALID",
        "SCHEMA_INVALID",
        "LIMIT_EXCEEDED",
        "PATH_INVALID",
        "PATH_ESCAPE",
        "IDENTITY_MISMATCH",
        "ANCHOR_UNAVAILABLE",
        "ANCHOR_MISMATCH",
        "CONTRACT_MISMATCH",
        "SOURCE_MISMATCH",
        "RESOURCE_MISMATCH",
        "LOCK_MISMATCH",
        "DISTRIBUTION_MISMATCH",
        "PYTHON_MISMATCH",
        "LOADER_UNAVAILABLE",
        "LOADER_MISMATCH",
        "MODULE_MISMATCH",
        "NATIVE_UNAVAILABLE",
        "NATIVE_MISMATCH",
        "BUILD_INPUT_DIRTY",
        "BUILD_OUTPUT_EXISTS",
        "BUILD_LAYOUT_INVALID",
        "ARCHIVE_MISMATCH",
        "ARTIFACT_MISMATCH",
        "EXTERNAL_BINDING_REQUIRED",
        "EXTERNAL_BINDING_MISMATCH",
        "ARTIFACT_CHANGED",
        "STAGING_INVALID",
    )
)
_SEAL = object()


class BuildProvenanceFault(ValueError):
    """Only a fixed code crosses the private consumer boundary."""

    def __init__(self, code: str):
        suffix = code.removeprefix("BUILD_PROVENANCE_") if type(code) is str else "SCHEMA_INVALID"
        self.code = "BUILD_PROVENANCE_" + (
            suffix if suffix in _ERROR_SUFFIXES else "SCHEMA_INVALID"
        )
        super().__init__(self.code)


def _fail(code):
    raise BuildProvenanceFault(code)


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _canonical(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _path(value):
    if (
        type(value) is not str
        or not value
        or len(value) > 512
        or "\\" in value
        or "\x00" in value
        or unicodedata.normalize("NFC", value) != value
        or any(0xD800 <= ord(c) <= 0xDFFF for c in value)
    ):
        _fail("PATH_INVALID")
    parts = value.split("/")
    if value.startswith("/") or any(p in ("", ".", "..") for p in parts):
        _fail("PATH_INVALID")
    if any(":" in p for p in parts):
        _fail("PATH_INVALID")
    return value


def _inside(root, relative):
    _path(relative)
    try:
        root = Path(root).resolve(strict=True)
    except (OSError, TypeError, ValueError):
        _fail("IDENTITY_MISMATCH")
    result = root.joinpath(*PurePosixPath(relative).parts)
    try:
        if not result.resolve(strict=True).is_relative_to(root):
            _fail("PATH_ESCAPE")
    except (OSError, RuntimeError):
        _fail("IDENTITY_MISMATCH")
    return result


def _read(path, cap):
    try:
        with Path(path).open("rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                _fail("PATH_INVALID")
            if before.st_size > cap:
                _fail("LIMIT_EXCEEDED")
            raw = stream.read(cap + 1)
            after = os.fstat(stream.fileno())
        if len(raw) > cap:
            _fail("LIMIT_EXCEEDED")
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ):
            _fail("ARTIFACT_CHANGED")
        if len(raw) != before.st_size:
            _fail("ARTIFACT_CHANGED")
        return raw
    except OSError:
        _fail("IDENTITY_MISMATCH")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _fail("JSON_INVALID")
        result[key] = value
    return result


def _json(raw, cap):
    if type(raw) is not bytes or len(raw) > cap:
        _fail("LIMIT_EXCEEDED")
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_pairs,
            parse_constant=lambda _x: _fail("JSON_INVALID"),
        )
    except (UnicodeError, ValueError, RecursionError) as error:
        if type(error) is BuildProvenanceFault:
            raise
        _fail("JSON_INVALID")
    count = 0

    def walk(item, depth):
        nonlocal count
        count += 1
        if depth > 16 or count > 200_000:
            _fail("LIMIT_EXCEEDED")
        if type(item) is str:
            if "\x00" in item or any(0xD800 <= ord(c) <= 0xDFFF for c in item):
                _fail("JSON_INVALID")
        elif type(item) is dict:
            for key, child in item.items():
                walk(key, depth + 1)
                walk(child, depth + 1)
        elif type(item) is list:
            for child in item:
                walk(child, depth + 1)
        elif type(item) is float and not math.isfinite(item):
            _fail("JSON_INVALID")
        elif type(item) not in (int, float, bool, type(None)):
            _fail("JSON_INVALID")

    walk(value, 0)
    return value


def _schema(value, schema):
    if "const" in schema:
        if type(value) is not type(schema["const"]) or value != schema["const"]:
            _fail("SCHEMA_INVALID")
    if "enum" in schema and not any(type(value) is type(x) and value == x for x in schema["enum"]):
        _fail("SCHEMA_INVALID")
    kinds = schema.get("type")
    if kinds:
        kinds = [kinds] if type(kinds) is str else kinds
        mapping = {
            "object": dict,
            "array": list,
            "string": str,
            "integer": int,
            "null": type(None),
            "boolean": bool,
        }
        if type(value) not in tuple(mapping[k] for k in kinds):
            _fail("SCHEMA_INVALID")
    if value is None:
        return
    if type(value) is dict:
        props = schema.get("properties", {})
        if set(value) != set(schema.get("required", [])) or set(value) - set(props):
            _fail("SCHEMA_INVALID")
        for key, item in value.items():
            _schema(item, props[key])
    elif type(value) is list:
        if not schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", ENTRY_CAP):
            _fail("SCHEMA_INVALID")
        for item in value:
            _schema(item, schema["items"])
    elif type(value) is str:
        if not schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", 512):
            _fail("SCHEMA_INVALID")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            _fail("SCHEMA_INVALID")
        if "pathPolicy" in schema:
            _path(value)
    elif type(value) is int:
        if not schema.get("minimum", 0) <= value <= schema.get("maximum", FILE_CAP):
            _fail("SCHEMA_INVALID")


def _load_contract(path):
    raw = _read(path, CONTRACT_CAP)
    if _sha(raw) != CONTRACT_SHA256:
        _fail("CONTRACT_MISMATCH")
    value = _json(raw, CONTRACT_CAP)
    if type(value) is not dict or value.get("format") != "i05-private-contract/1":
        _fail("CONTRACT_MISMATCH")
    return value, raw


def _unique(rows, key="path"):
    values = [r[key] for r in rows]
    if len(values) != len(set(values)) or len(values) != len({v.casefold() for v in values}):
        _fail("SCHEMA_INVALID")


def _module_path(module, path):
    if not re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*", module) or path not in (
        module.replace(".", "/") + ".py",
        module.replace(".", "/") + "/__init__.py",
    ):
        _fail("SCHEMA_INVALID")


def _validate_expectations(value, contract):
    _schema(value, contract["schemas"]["expectations"])
    if tuple(r["module"] for r in value["suppliers"]) != SUPPLIER_MODULES:
        _fail("SCHEMA_INVALID")
    _unique(value["suppliers"])
    for row in value["suppliers"]:
        _module_path(row["module"], row["path"])
    if tuple(r["path"] for r in value["publicResources"]) != PUBLIC_PATHS:
        _fail("SCHEMA_INVALID")
    if value["inputs"] != list(FIXED_INPUTS) or value["distributions"] != FIXED_DISTRIBUTIONS:
        _fail("SCHEMA_INVALID")


def _validate_manifest(value, contract):
    _schema(value, contract["schemas"]["provenance"])
    expected = {k: value[k] for k in ("publicResources", "inputs", "lock")}
    expected["suppliers"] = [
        {k: r[k] for k in ("module", "path", "bytes", "sha256")} for r in value["suppliers"]
    ]
    expected["distributions"] = {r["name"]: r["version"] for r in value["distributions"]}
    _validate_expectations(expected, contract)
    if tuple(r["name"] for r in value["distributions"]) != tuple(FIXED_DISTRIBUTIONS):
        _fail("SCHEMA_INVALID")
    if tuple(r["module"] for r in value["privateModules"]) != PRIVATE_MODULES:
        _fail("SCHEMA_INVALID")
    for row in value["privateModules"]:
        _module_path(row["module"], row["path"])
    if value["entrypoint"]["path"] != "packages/engine/entrypoint.py":
        _fail("SCHEMA_INVALID")
    if value["contract"]["path"] != CONTRACT_SOURCE:
        _fail("SCHEMA_INVALID")
    if value["contract"]["sha256"] != CONTRACT_SHA256:
        _fail("CONTRACT_MISMATCH")
    for row in value["publicResources"]:
        if row["bytes"] > SMALL_CAP:
            _fail("LIMIT_EXCEEDED")
    for dist in value["distributions"]:
        if dist["metadata"]["bytes"] > SMALL_CAP:
            _fail("LIMIT_EXCEEDED")
        _unique(dist["licenses"])
        _unique(dist["files"])
        info = PurePosixPath(dist["metadata"]["path"])
        if info.name != "METADATA" or info.parent.name != (
            dist["name"] + "-" + dist["version"] + ".dist-info"
        ):
            _fail("SCHEMA_INVALID")
        for row in dist["licenses"]:
            if (
                row["bytes"] > SMALL_CAP
                or PurePosixPath(row["path"]).parent != info.parent
                and not (PurePosixPath(row["path"]).is_relative_to(info.parent / "licenses"))
            ):
                _fail("SCHEMA_INVALID")
        for row in dist["files"]:
            if PurePosixPath(row["path"]).parts[0] != dist["name"]:
                _fail("SCHEMA_INVALID")
            if row["kind"] == "python":
                if row["bytes"] > CODE_CAP or row["module"] is None or row["codeSha256"] is None:
                    _fail("SCHEMA_INVALID")
                _module_path(row["module"], row["path"])
            elif row["kind"] == "data":
                if row["module"] is not None or row["codeSha256"] is not None:
                    _fail("SCHEMA_INVALID")
            else:
                suffix = next(
                    (s for s in importlib.machinery.EXTENSION_SUFFIXES if row["path"].endswith(s)),
                    None,
                )
                if (
                    suffix is None
                    or row["module"] != row["path"][: -len(suffix)].replace("/", ".")
                    or row["codeSha256"] is not None
                ):
                    _fail("SCHEMA_INVALID")
    return expected


def _normalized(code):
    if type(code) is not types.CodeType:
        _fail("LOADER_UNAVAILABLE")
    return code.replace(
        co_filename="<i05-canonical-code>",
        co_consts=tuple(_normalized(x) if type(x) is types.CodeType else x for x in code.co_consts),
    )


def _code_sha(code):
    try:
        return _sha(marshal.dumps(_normalized(code), 4))
    except BuildProvenanceFault:
        raise
    except (ValueError, TypeError, RecursionError):
        _fail("LOADER_MISMATCH")


def _compiled(raw):
    try:
        return compile(raw, "<i05-source>", "exec", flags=0, dont_inherit=True, optimize=0)
    except (SyntaxError, ValueError, TypeError):
        _fail("SOURCE_MISMATCH")


def _python_identity():
    if (
        sys.implementation.name != "cpython"
        or sys.version_info[:2] != (3, 12)
        or sys.flags.optimize != 0
    ):
        _fail("PYTHON_MISMATCH")
    return {
        "implementation": sys.implementation.name,
        "version": sys.version,
        "cacheTag": sys.implementation.cache_tag,
        "soabi": sysconfig.get_config_var("SOABI"),
        "bytecodeMagicHex": importlib.util.MAGIC_NUMBER.hex(),
        "marshalVersion": 4,
        "compileFlags": 0,
        "dontInherit": True,
        "optimize": 0,
    }


def _check_python(manifest):
    current = _python_identity()
    if any(manifest[key] != value for key, value in current.items()):
        _fail("PYTHON_MISMATCH")
    if manifest["buildSharedLibrary"]["name"] != sysconfig.get_config_var("LDLIBRARY"):
        _fail("PYTHON_MISMATCH")
    return current


def _identity(root, relative, cap=FILE_CAP):
    raw = _read(_inside(root, relative), cap)
    return {"path": relative, "bytes": len(raw), "sha256": _sha(raw)}


def _check_identity(root, row, cap, code="IDENTITY_MISMATCH", relative=None):
    actual = _identity(root, row["path"] if relative is None else relative, cap)
    if actual["bytes"] != row["bytes"] or actual["sha256"] != row["sha256"]:
        _fail(code)
    return actual


def _anchor_source(manifest_sha):
    return (
        f'PROVENANCE_SHA256 = "{manifest_sha}"\nCONTRACT_SHA256 = "{CONTRACT_SHA256}"\n'
    ).encode()


def _check_anchor(manifest_sha, root):
    try:
        spec = importlib.util.find_spec(ANCHOR)
        loader = spec.loader if spec else None
        get_code = getattr(loader, "get_code", None)
        if spec is None or spec.name != ANCHOR or not callable(get_code):
            _fail("ANCHOR_UNAVAILABLE")
        if not Path(spec.origin).resolve().is_relative_to(root):
            _fail("ANCHOR_MISMATCH")
        actual = get_code(ANCHOR)
        if _code_sha(actual) != _code_sha(_compiled(_anchor_source(manifest_sha))):
            _fail("ANCHOR_MISMATCH")
    except BuildProvenanceFault:
        raise
    except Exception:
        _fail("ANCHOR_UNAVAILABLE")


@dataclass(frozen=True, init=False)
class FrozenBuildEvidence:
    """Immutable private state, not an approval token against hostile Python."""

    _manifest: bytes
    _expectations: bytes
    _root: Path
    _python: bytes
    _seal: object

    def __new__(cls, *_args, **_kwargs):
        _fail("MODE_INVALID")


def _new_evidence(manifest_raw, expectations, root):
    result = object.__new__(FrozenBuildEvidence)
    for name, value in (
        ("_manifest", manifest_raw),
        ("_expectations", _canonical(expectations)),
        ("_root", root),
        ("_python", _canonical(_python_identity())),
        ("_seal", _SEAL),
    ):
        object.__setattr__(result, name, value)
    return result


def _evidence(value):
    if type(value) is not FrozenBuildEvidence or getattr(value, "_seal", None) is not _SEAL:
        _fail("MODE_INVALID")
    if getattr(sys, "frozen", None) is not True:
        _fail("MODE_INVALID")
    try:
        root = Path(sys._MEIPASS).resolve(strict=True)
    except (AttributeError, OSError, TypeError):
        _fail("MODE_INVALID")
    if root != value._root or _canonical(_python_identity()) != value._python:
        _fail("PYTHON_MISMATCH")
    return _json(value._manifest, MANIFEST_CAP), root


def _check_metadata(root, dist):
    _check_identity(root, dist["metadata"], SMALL_CAP, "DISTRIBUTION_MISMATCH")
    metadata = email.message_from_bytes(_read(_inside(root, dist["metadata"]["path"]), SMALL_CAP))
    if metadata.get_all("Name") != [dist["name"]] or metadata.get_all("Version") != [
        dist["version"]
    ]:
        _fail("DISTRIBUTION_MISMATCH")
    for row in dist["licenses"]:
        _check_identity(root, row, SMALL_CAP, "DISTRIBUTION_MISMATCH")
    declared = metadata.get_all("License-File", [])
    parent = PurePosixPath(dist["metadata"]["path"]).parent
    actual_paths = {x["path"] for x in dist["licenses"]}
    for value in declared:
        _path(value)
        if (
            str(parent / value) not in actual_paths
            and str(parent / "licenses" / value) not in actual_paths
        ):
            _fail("DISTRIBUTION_MISMATCH")
    for row in dist["files"]:
        if row["kind"] == "data":
            _check_identity(root, row, INPUT_CAP, "DISTRIBUTION_MISMATCH")


def load_frozen_provenance(*, expectations: dict) -> FrozenBuildEvidence:
    """Bounded preflight only: no semantic, target Python or native execution."""
    if getattr(sys, "frozen", None) is not True:
        _fail("MODE_INVALID")
    try:
        root = Path(sys._MEIPASS).resolve(strict=True)
    except (AttributeError, OSError, TypeError):
        _fail("MODE_INVALID")
    contract, contract_raw = _load_contract(_inside(root, CONTRACT_BUNDLED))
    if type(expectations) is not dict:
        _fail("SCHEMA_INVALID")
    _validate_expectations(expectations, contract)
    # Round-trip rejects non-JSON carriers before any caller value is trusted.
    try:
        supplied = _json(_canonical(expectations), MANIFEST_CAP)
    except (ValueError, TypeError, UnicodeError):
        _fail("SCHEMA_INVALID")
    if supplied != expectations:
        _fail("SCHEMA_INVALID")
    _validate_expectations(supplied, contract)
    raw = _read(_inside(root, PROVENANCE_BUNDLED), MANIFEST_CAP)
    manifest = _json(raw, MANIFEST_CAP)
    expected = _validate_manifest(manifest, contract)
    if supplied != expected or manifest["contract"]["bytes"] != len(contract_raw):
        _fail("IDENTITY_MISMATCH")
    _check_anchor(_sha(raw), root)
    _check_python(manifest["python"])
    library_name = manifest["python"]["buildSharedLibrary"]["name"]
    if "/" in library_name:
        _fail("PYTHON_MISMATCH")
    _identity(root, library_name)
    for row in manifest["publicResources"]:
        _check_identity(root, row, SMALL_CAP, "RESOURCE_MISMATCH")
    for row in manifest["inputs"]:
        _check_identity(root, row, INPUT_CAP, "RESOURCE_MISMATCH")
    _check_identity(root, manifest["lock"], SMALL_CAP, "LOCK_MISMATCH", "provenance/uv.lock")
    for dist in manifest["distributions"]:
        _check_metadata(root, dist)
    return _new_evidence(raw, supplied, root)


def _verify_module(module, row, root):
    name = row["module"]
    if (
        type(module) is not types.ModuleType
        or sys.modules.get(name) is not module
        or module.__name__ != name
    ):
        _fail("MODULE_MISMATCH")
    spec = getattr(module, "__spec__", None)
    if spec is None or spec.name != name:
        _fail("MODULE_MISMATCH")
    try:
        expected = root / row["path"]
        if (
            Path(module.__file__).resolve() != expected.resolve()
            or Path(spec.origin).resolve() != expected.resolve()
            or not expected.resolve().is_relative_to(root)
        ):
            _fail("MODULE_MISMATCH")
        if getattr(module, "__loader__", None) is not spec.loader:
            _fail("LOADER_MISMATCH")
        get_code = getattr(spec.loader, "get_code", None)
        if not callable(get_code):
            _fail("LOADER_UNAVAILABLE")
        code = get_code(name)
        if _code_sha(code) != row["codeSha256"]:
            _fail("LOADER_MISMATCH")
    except BuildProvenanceFault:
        raise
    except Exception:
        _fail("LOADER_UNAVAILABLE")
    return {"module": name, "path": row["path"], "actualCodeSha256": _code_sha(code)}


def verify_loaded_modules(
    evidence: FrozenBuildEvidence, modules: dict[str, types.ModuleType]
) -> dict:
    """Call after the observer and target imports; this function never imports them."""
    manifest, root = _evidence(evidence)
    if type(modules) is not dict or set(modules) != set(SUPPLIER_MODULES):
        _fail("MODULE_MISMATCH")
    rows = [_verify_module(modules[row["module"]], row, root) for row in manifest["suppliers"]]
    rows.extend(
        _verify_module(sys.modules.get(row["module"]), row, root)
        for row in manifest["privateModules"]
    )
    dist_rows = []
    for dist in manifest["distributions"]:
        lookup = {row["module"]: row for row in dist["files"] if row["kind"] == "python"}
        loaded = [
            (name, module)
            for name, module in list(sys.modules.items())
            if name == dist["name"] or name.startswith(dist["name"] + ".")
        ]
        for name, module in loaded:
            if name == "wcwidth._wcwidth_c":
                continue
            if name not in lookup:
                _fail("MODULE_MISMATCH")
            dist_rows.append(_verify_module(module, lookup[name], root))
    return {
        "rootApproval": "unknown",
        "provenanceSha256": _sha(evidence._manifest),
        "packageCodeBoundToSource": "verified-python-code-and-identified-resources-only",
        "nativeSourceByteEquivalence": "unknown",
        "semanticParity": "unknown",
        "supplierAndPrivateModules": rows,
        "loadedDistributionModules": dist_rows,
        "actualPythonSharedLibrary": _identity(
            root, manifest["python"]["buildSharedLibrary"]["name"]
        ),
        "pythonSharedLibrarySourceByteEquivalence": "unknown",
        "entrypointDomain": "external-launcher-PYZ-binding-only",
    }


def verify_native_extension(evidence: FrozenBuildEvidence) -> dict:
    """Observe the already-loaded extension; never activate a pure-Python fallback."""
    manifest, root = _evidence(evidence)
    name = "wcwidth._wcwidth_c"
    module = sys.modules.get(name)
    if type(module) is not types.ModuleType:
        _fail("NATIVE_UNAVAILABLE")
    spec = getattr(module, "__spec__", None)
    if (
        module.__name__ != name
        or spec is None
        or spec.name != name
        or type(spec.loader) is not importlib.machinery.ExtensionFileLoader
        or getattr(module, "__loader__", None) is not spec.loader
    ):
        _fail("NATIVE_MISMATCH")
    dist = next(x for x in manifest["distributions"] if x["name"] == "wcwidth")
    native = [r for r in dist["files"] if r["kind"] == "native" and r["module"] == name]
    if len(native) != 1:
        _fail("NATIVE_MISMATCH")
    row = native[0]
    try:
        expected = _inside(root, row["path"]).resolve()
        if Path(spec.origin).resolve() != expected or Path(module.__file__).resolve() != expected:
            _fail("NATIVE_MISMATCH")
        actual = _identity(root, row["path"])
    except (OSError, AttributeError, TypeError):
        _fail("NATIVE_MISMATCH")
    return {
        "module": name,
        "loader": "ExtensionFileLoader",
        "path": row["path"],
        "actualArtifactFile": actual,
        "installedSourceFile": {k: row[k] for k in ("path", "bytes", "sha256")},
        "sourceByteMatch": actual["sha256"] == row["sha256"],
        "nativeSourceByteEquivalence": "unknown",
        "rootApproval": "unknown",
    }


def _git(root, *args):
    try:
        result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=False)
        if result.returncode != 0 or len(result.stdout) > INPUT_CAP:
            _fail("BUILD_INPUT_DIRTY")
        return result.stdout
    except OSError:
        _fail("BUILD_INPUT_DIRTY")


def _code_row(root, module, path):
    raw = _read(_inside(root, path), CODE_CAP)
    return {
        "module": module,
        "path": path,
        "bytes": len(raw),
        "sha256": _sha(raw),
        "codeSha256": _code_sha(_compiled(raw)),
    }


def _literal_pins(source):
    try:
        tree = ast.parse(source)
        result = {}
        for item in tree.body:
            if type(item) is ast.Assign and len(item.targets) == 1:
                target = item.targets[0]
                if type(target) is ast.Name and target.id in (
                    "SUPPLIER_PINS",
                    "PUBLIC_RESOURCE_PINS",
                ):
                    if target.id in result:
                        _fail("SOURCE_MISMATCH")
                    result[target.id] = ast.literal_eval(item.value)
        if set(result) != {"SUPPLIER_PINS", "PUBLIC_RESOURCE_PINS"}:
            _fail("SOURCE_MISMATCH")
        return result
    except (SyntaxError, ValueError, TypeError, RecursionError):
        _fail("SOURCE_MISMATCH")


def _dist_inventory(name, version):
    try:
        dist = importlib.metadata.distribution(name)
    except importlib.metadata.PackageNotFoundError:
        _fail("DISTRIBUTION_MISMATCH")
    if dist.version != version or not dist.files:
        _fail("DISTRIBUTION_MISMATCH")
    site = Path(sysconfig.get_path("purelib")).resolve()
    plat = Path(sysconfig.get_path("platlib")).resolve()
    metadata_paths = [str(x) for x in dist.files if str(x).endswith(".dist-info/METADATA")]
    if len(metadata_paths) != 1:
        _fail("DISTRIBUTION_MISMATCH")
    metadata_path = metadata_paths[0]
    site_root = Path(dist.locate_file("")).resolve()
    if site_root not in (site, plat) or not site_root.is_relative_to(Path(sys.prefix).resolve()):
        _fail("DISTRIBUTION_MISMATCH")
    metadata_row = _identity(site_root, metadata_path, SMALL_CAP)
    metadata = email.message_from_bytes(_read(_inside(site_root, metadata_path), SMALL_CAP))
    if metadata.get_all("Name") != [name] or metadata.get_all("Version") != [version]:
        _fail("DISTRIBUTION_MISMATCH")
    info = PurePosixPath(metadata_path).parent
    licenses = set()
    for path in dist.files:
        relative = str(path)
        if PurePosixPath(relative).is_relative_to(info) and PurePosixPath(
            relative
        ).name.upper().startswith(("LICENSE", "COPYING")):
            licenses.add(relative)
    for declared in metadata.get_all("License-File", []):
        _path(declared)
        options = (str(info / declared), str(info / "licenses" / declared))
        matched = next((x for x in options if (site_root / x).is_file()), None)
        if matched is None:
            _fail("DISTRIBUTION_MISMATCH")
        licenses.add(matched)
    if not licenses:
        _fail("DISTRIBUTION_MISMATCH")
    files = []
    for path in dist.files:
        relative = str(path)
        parts = PurePosixPath(relative).parts
        if not parts or parts[0] != name or "__pycache__" in parts or relative.endswith(".pyc"):
            continue
        _path(relative)
        row = _identity(site_root, relative)
        module, fingerprint, kind = None, None, "data"
        if relative.endswith(".py"):
            module = relative[:-3].replace("/", ".").removesuffix(".__init__")
            fingerprint = _code_sha(_compiled(_read(_inside(site_root, relative), CODE_CAP)))
            kind = "python"
        else:
            suffix = next(
                (s for s in importlib.machinery.EXTENSION_SUFFIXES if relative.endswith(s)), None
            )
            if suffix:
                module, kind = relative[: -len(suffix)].replace("/", "."), "native"
        files.append({**row, "kind": kind, "module": module, "codeSha256": fingerprint})
    return {
        "name": name,
        "version": version,
        "metadata": metadata_row,
        "licenses": [_identity(site_root, p, SMALL_CAP) for p in sorted(licenses)],
        "files": sorted(files, key=lambda row: row["path"]),
    }


def _collect_build_manifest(root, contract, contract_raw):
    source_root = root / "packages/engine/src"
    probe = source_root / "ontolearn_engine/semantic_source_package_probe.py"
    pins = _literal_pins(_read(probe, CODE_CAP))
    _validate_literal_rows(pins)
    suppliers = []
    for module, relative, _count, _digest in pins["SUPPLIER_PINS"]:
        suppliers.append(_code_row(source_root, module, "ontolearn_engine/" + relative))
    resources = [
        _identity(root / "packages", "contracts/" + path, SMALL_CAP)
        for path, _count, _digest in pins["PUBLIC_RESOURCE_PINS"]
    ]
    inputs = [_identity(source_root, row["path"], INPUT_CAP) for row in FIXED_INPUTS]
    if inputs != list(FIXED_INPUTS):
        _fail("RESOURCE_MISMATCH")
    python = _python_identity()
    executable = Path(sys.executable).resolve()
    libname = sysconfig.get_config_var("LDLIBRARY")
    libdir = sysconfig.get_config_var("LIBDIR")
    if not libname or not libdir:
        _fail("PYTHON_MISMATCH")
    library = Path(libdir) / libname
    python["buildExecutable"] = {
        "bytes": len(_read(executable, FILE_CAP)),
        "sha256": _sha(_read(executable, FILE_CAP)),
    }
    python["buildSharedLibrary"] = {
        "name": libname,
        "bytes": len(_read(library, FILE_CAP)),
        "sha256": _sha(_read(library, FILE_CAP)),
    }
    value = {
        "format": "i05-private-build-provenance/1",
        "source": {
            "commit": _git(root, "rev-parse", "HEAD").decode().strip(),
            "tree": _git(root, "rev-parse", "HEAD^{tree}").decode().strip(),
        },
        "contract": {
            "path": CONTRACT_SOURCE,
            "bytes": len(contract_raw),
            "sha256": _sha(contract_raw),
        },
        "python": python,
        "codeAlgorithm": ALGORITHM,
        "suppliers": suppliers,
        "privateModules": [
            _code_row(source_root, name, name.replace(".", "/") + ".py") for name in PRIVATE_MODULES
        ],
        "entrypoint": _identity(root, "packages/engine/entrypoint.py", CODE_CAP),
        "publicResources": resources,
        "inputs": inputs,
        "lock": _identity(root, "uv.lock", SMALL_CAP),
        "distributions": [
            _dist_inventory(name, version) for name, version in FIXED_DISTRIBUTIONS.items()
        ],
    }
    _validate_manifest(value, contract)
    selected = [
        CONTRACT_SOURCE,
        "packages/engine/entrypoint.py",
        "uv.lock",
        "scripts/build-engine.mjs",
        "pyproject.toml",
        "packages/engine/pyproject.toml",
    ]
    selected += [
        "packages/engine/src/" + row["path"] for row in suppliers + value["privateModules"] + inputs
    ]
    selected += ["packages/" + row["path"] for row in resources]
    for relative in selected:
        cap = INPUT_CAP if relative.endswith("parity-inputs.json") else CODE_CAP
        if _read(_inside(root, relative), cap) != _git(root, "show", "HEAD:" + relative):
            _fail("BUILD_INPUT_DIRTY")
    return value


def _validate_literal_rows(pins):
    for key, count, width in (("SUPPLIER_PINS", 22, 4), ("PUBLIC_RESOURCE_PINS", 4, 3)):
        rows = pins[key]
        if type(rows) is not tuple or len(rows) != count:
            _fail("SOURCE_MISMATCH")
        for row in rows:
            if type(row) is not tuple or len(row) != width:
                _fail("SOURCE_MISMATCH")
            if (
                any(type(value) is not str for value in row[:-2])
                or type(row[-2]) is not int
                or not 0 <= row[-2] <= CODE_CAP
                or type(row[-1]) is not str
                or re.fullmatch(r"[0-9a-f]{64}", row[-1]) is None
            ):
                _fail("SOURCE_MISMATCH")


def prepare_build(repository_root: Path, output_dir: Path) -> dict:
    """Generate immutable inputs only; this does not run PyInstaller or semantics."""
    try:
        root = Path(repository_root).resolve(strict=True)
        output = Path(output_dir).absolute()
    except (OSError, TypeError, ValueError):
        _fail("BUILD_LAYOUT_INVALID")
    parent = root / "build/i05-provenance"
    if (
        output.parent.resolve() != parent.resolve()
        or not parent.resolve().is_relative_to(root)
        or re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", output.name) is None
    ):
        _fail("BUILD_LAYOUT_INVALID")
    if output.exists() or output.is_symlink():
        _fail("BUILD_OUTPUT_EXISTS")
    contract, contract_raw = _load_contract(_inside(root, CONTRACT_SOURCE))
    dirty = _git(
        root,
        "diff",
        "--name-only",
        "HEAD",
        "--",
        "packages/engine/src",
        "packages/contracts",
        "packages/engine/entrypoint.py",
        "uv.lock",
        "scripts/build-engine.mjs",
        "pyproject.toml",
        "packages/engine/pyproject.toml",
    )
    if dirty:
        _fail("BUILD_INPUT_DIRTY")
    manifest = _collect_build_manifest(root, contract, contract_raw)
    raw = _canonical(manifest)
    if len(raw) > MANIFEST_CAP:
        _fail("LIMIT_EXCEEDED")
    try:
        output.mkdir(parents=True, exist_ok=False)
        generated = output / "generated"
        provenance = output / "provenance"
        generated.mkdir()
        provenance.mkdir()
        manifest_path = provenance / Path(PROVENANCE_BUNDLED).name
        contract_path = provenance / Path(CONTRACT_BUNDLED).name
        anchor_path = generated / (ANCHOR + ".py")
        for path, data in (
            (manifest_path, raw),
            (contract_path, contract_raw),
            (anchor_path, _anchor_source(_sha(raw))),
        ):
            with path.open("xb") as stream:
                stream.write(data)
    except FileExistsError:
        _fail("BUILD_OUTPUT_EXISTS")
    except OSError:
        _fail("BUILD_LAYOUT_INVALID")
    return {
        "provenancePath": str(manifest_path),
        "contractPath": str(contract_path),
        "generatedDir": str(generated),
        "anchorPath": str(anchor_path),
    }


def _hash_file(path, expected_mode=None):
    total = 0
    digest = hashlib.sha256()
    try:
        before_path = path.lstat()
        if expected_mode is not None and before_path.st_mode != expected_mode:
            _fail("ARTIFACT_CHANGED")
        with path.open("rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > FILE_CAP:
                _fail("LIMIT_EXCEEDED")
            while data := stream.read(1_048_576):
                total += len(data)
                if total > FILE_CAP:
                    _fail("LIMIT_EXCEEDED")
                digest.update(data)
            after = os.fstat(stream.fileno())
        after_path = path.lstat()

        def fields(s):
            return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_mode)

        if (
            fields(before) != fields(after)
            or fields(before_path) != fields(after_path)
            or before_path.st_ino != before.st_ino
            or total != before.st_size
        ):
            _fail("ARTIFACT_CHANGED")
        return total, digest.hexdigest()
    except OSError:
        _fail("ARTIFACT_CHANGED")


def _inventory_artifact(artifact_dir):
    root = Path(artifact_dir).resolve(strict=True)
    result, total, seen = [], 0, set()

    def visit(directory):
        nonlocal total
        directory_before = directory.lstat()
        if not stat.S_ISDIR(directory_before.st_mode) or not directory.resolve(
            strict=True
        ).is_relative_to(root):
            _fail("PATH_ESCAPE")
        for path in sorted(directory.iterdir(), key=lambda p: p.name):
            relative = path.relative_to(root).as_posix()
            _path(relative)
            if relative.casefold() in seen:
                _fail("PATH_INVALID")
            seen.add(relative.casefold())
            if len(seen) > ENTRY_CAP:
                _fail("LIMIT_EXCEEDED")
            mode = path.lstat().st_mode
            row = {
                "path": relative,
                "kind": None,
                "bytes": None,
                "sha256": None,
                "mode": None,
                "target": None,
            }
            if stat.S_ISLNK(mode):
                target = os.readlink(path)
                if (
                    not target
                    or len(target) > 512
                    or "\\" in target
                    or "\x00" in target
                    or Path(target).is_absolute()
                    or unicodedata.normalize("NFC", target) != target
                ):
                    _fail("PATH_ESCAPE")
                try:
                    if not path.resolve(strict=True).is_relative_to(root):
                        _fail("PATH_ESCAPE")
                except (OSError, RuntimeError):
                    _fail("PATH_ESCAPE")
                row.update(kind="symlink", target=target)
            elif stat.S_ISDIR(mode):
                row.update(kind="directory", mode=stat.S_IMODE(mode))
            elif stat.S_ISREG(mode):
                if not path.resolve(strict=True).is_relative_to(root):
                    _fail("PATH_ESCAPE")
                size, digest = _hash_file(path, mode)
                total += size
                if total > TOTAL_CAP:
                    _fail("LIMIT_EXCEEDED")
                row.update(kind="file", bytes=size, sha256=digest, mode=stat.S_IMODE(mode))
            else:
                _fail("PATH_INVALID")
            result.append(row)
            if row["kind"] == "directory":
                visit(path)
        directory_after = directory.lstat()
        if (directory_before.st_dev, directory_before.st_ino, directory_before.st_mtime_ns) != (
            directory_after.st_dev,
            directory_after.st_ino,
            directory_after.st_mtime_ns,
        ):
            _fail("ARTIFACT_CHANGED")

    try:
        visit(root)
    except OSError:
        _fail("ARTIFACT_CHANGED")
    launcher = next((r for r in result if r["path"] == "ontolearn-engine"), None)
    if launcher is None or launcher["kind"] != "file" or not launcher["mode"] & 0o111:
        _fail("ARTIFACT_MISMATCH")
    return sorted(result, key=lambda r: r["path"])


def _validate_binding(binding, contract):
    _schema(binding, contract["schemas"]["artifactBinding"])
    _unique(binding["entries"])
    for row in binding["entries"]:
        rules = contract["bindingKindRules"][row["kind"]]
        if any(row[key] is None for key in rules["nonnull"]):
            _fail("SCHEMA_INVALID")
        if any(row[key] is not None for key in rules["null"]):
            _fail("SCHEMA_INVALID")
        if row["kind"] == "symlink":
            target = row["target"]
            if not target or "\\" in target or "\x00" in target or Path(target).is_absolute():
                _fail("PATH_INVALID")
            if unicodedata.normalize("NFC", target) != target:
                _fail("PATH_INVALID")


def _archive_code(engine_dir):
    # Build-only dependency; not imported by the runtime reader/preflight path.
    try:
        readers = importlib.import_module("PyInstaller.archive.readers")
        archive = readers.CArchiveReader(str(engine_dir / "ontolearn-engine"))
        pyz = archive.open_embedded_archive("PYZ.pyz")
        return pyz
    except Exception:
        _fail("ARCHIVE_MISMATCH")


def _verify_archive(pyz, manifest, root):
    rows = manifest["suppliers"] + manifest["privateModules"]
    rows += [
        r for dist in manifest["distributions"] for r in dist["files"] if r["kind"] == "python"
    ]
    for row in rows:
        try:
            code = pyz.extract(row["module"])
        except Exception:
            _fail("ARCHIVE_MISMATCH")
        if _code_sha(code) != row["codeSha256"]:
            _fail("ARCHIVE_MISMATCH")
    raw = _read(_inside(root, PROVENANCE_BUNDLED), MANIFEST_CAP)
    try:
        anchor = pyz.extract(ANCHOR)
    except Exception:
        _fail("ARCHIVE_MISMATCH")
    if _code_sha(anchor) != _code_sha(_compiled(_anchor_source(_sha(raw)))):
        _fail("ANCHOR_MISMATCH")


def finalize_build(repository_root: Path, output_dir: Path, engine_dir: Path) -> dict:
    """Audit actual output bytes/code and emit an unapproved external proposal."""
    try:
        repository = Path(repository_root).resolve(strict=True)
        output = Path(output_dir).resolve(strict=True)
        engine = Path(engine_dir).resolve(strict=True)
    except (OSError, TypeError, ValueError):
        _fail("BUILD_LAYOUT_INVALID")
    if (
        output.parent != repository / "build/i05-provenance"
        or engine != output / "dist/ontolearn-engine"
    ):
        _fail("BUILD_LAYOUT_INVALID")
    contract, _contract_raw = _load_contract(output / "provenance" / Path(CONTRACT_BUNDLED).name)
    raw = _read(output / "provenance" / Path(PROVENANCE_BUNDLED).name, MANIFEST_CAP)
    manifest = _json(raw, MANIFEST_CAP)
    _validate_manifest(manifest, contract)
    _check_python(manifest["python"])
    root = engine / "_internal"
    _identity(root, manifest["python"]["buildSharedLibrary"]["name"])
    if _read(_inside(root, PROVENANCE_BUNDLED), MANIFEST_CAP) != raw:
        _fail("IDENTITY_MISMATCH")
    if _read(_inside(root, CONTRACT_BUNDLED), CONTRACT_CAP) != _contract_raw:
        _fail("CONTRACT_MISMATCH")
    for row in manifest["publicResources"]:
        _check_identity(root, row, SMALL_CAP, "RESOURCE_MISMATCH")
    for row in manifest["inputs"]:
        _check_identity(root, row, INPUT_CAP, "RESOURCE_MISMATCH")
    _check_identity(root, manifest["lock"], SMALL_CAP, "LOCK_MISMATCH", "provenance/uv.lock")
    for dist in manifest["distributions"]:
        _check_metadata(root, dist)
        for row in dist["files"]:
            if row["kind"] == "native":
                _identity(root, row["path"])
    _verify_archive(_archive_code(engine), manifest, root)
    binding = {
        "format": "i05-private-artifact-binding/1",
        "provenanceSha256": _sha(raw),
        "sourceCommit": manifest["source"]["commit"],
        "artifactDomain": "complete-engine-directory",
        "launcher": "ontolearn-engine",
        "entries": _inventory_artifact(engine),
        "rootApproved": False,
    }
    _validate_binding(binding, contract)
    binding_raw = _canonical(binding)
    if len(binding_raw) > BINDING_CAP:
        _fail("LIMIT_EXCEEDED")
    path = output / "artifact-binding-v1.json"
    try:
        with path.open("xb") as stream:
            stream.write(binding_raw)
    except FileExistsError:
        _fail("BUILD_OUTPUT_EXISTS")
    return {
        "bindingPath": str(path),
        "bindingSha256": _sha(binding_raw),
        "engineDirectory": str(engine),
        "provenanceSha256": _sha(raw),
    }


def verify_external_binding(
    binding_path: Path, artifact_dir: Path, *, expected_sha256: str
) -> dict:
    """External pre-spawn check against a digest obtained from root, not the package."""
    if type(expected_sha256) is not str or re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None:
        _fail("EXTERNAL_BINDING_REQUIRED")
    try:
        root = Path(artifact_dir).resolve(strict=True)
    except (OSError, TypeError, ValueError):
        _fail("ARTIFACT_MISMATCH")
    try:
        path = Path(binding_path).resolve(strict=True)
    except (OSError, TypeError, ValueError):
        _fail("EXTERNAL_BINDING_REQUIRED")
    if path.is_relative_to(root):
        _fail("EXTERNAL_BINDING_REQUIRED")
    raw = _read(path, BINDING_CAP)
    if _sha(raw) != expected_sha256:
        _fail("EXTERNAL_BINDING_MISMATCH")
    contract, _ = _load_contract(_inside(root / "_internal", CONTRACT_BUNDLED))
    binding = _json(raw, BINDING_CAP)
    _validate_binding(binding, contract)
    if binding["entries"] != _inventory_artifact(root):
        _fail("ARTIFACT_MISMATCH")
    provenance_raw = _read(_inside(root / "_internal", PROVENANCE_BUNDLED), MANIFEST_CAP)
    provenance = _json(provenance_raw, MANIFEST_CAP)
    _validate_manifest(provenance, contract)
    if (
        _sha(provenance_raw) != binding["provenanceSha256"]
        or provenance["source"]["commit"] != binding["sourceCommit"]
    ):
        _fail("ARTIFACT_MISMATCH")
    return {
        "expectedBindingSha256": expected_sha256,
        "actualBindingSha256": _sha(raw),
        "artifactDirectory": str(root),
        "inventoryVerified": True,
        "sourceCommit": binding["sourceCommit"],
        "provenanceSha256": binding["provenanceSha256"],
        "rootApproval": "unknown; supplied-external-digest-verified, no run executed",
    }
