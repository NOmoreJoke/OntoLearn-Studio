"""Read-only M08 package inventory; never execute the semantic probe or app."""

import email
import hashlib
import importlib.metadata
import json
import struct
import sys
from pathlib import Path

from PyInstaller.archive.readers import CArchiveReader

ROOT = Path(__file__).resolve().parents[4]
ENGINE = ROOT / "release/mac-arm64/OntoLearn Studio.app/Contents/Resources/engine"
INTERNAL = ENGINE / "_internal"
EXPECTED = {
    "pyparsing": "3.3.3",
    "pyshacl": "0.30.1",
    "rdflib": "7.6.0",
    "owlrl": "7.6.2",
    "packaging": "26.3",
    "prettytable": "3.18.0",
    "wcwidth": "0.9.2",
    "html5rdf": "1.2.1",
}


def identity(path):
    raw = path.read_bytes()
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def identical(source, packaged):
    assert source.read_bytes() == packaged.read_bytes(), (source, packaged)
    return {"source": identity(source), "packaged": identity(packaged), "exact": True}


archive = CArchiveReader(str(ENGINE / "ontolearn-engine"))
pyz = archive.open_embedded_archive("PYZ.pyz")
rows = []
for name, version in EXPECTED.items():
    installed = importlib.metadata.distribution(name)
    assert installed.version == version
    metadata_file = next(p for p in installed.files if str(p).endswith(".dist-info/METADATA"))
    installed_info = Path(installed.locate_file(metadata_file)).parent
    bundled_info = INTERNAL / installed_info.name
    metadata = email.message_from_bytes((bundled_info / "METADATA").read_bytes())
    assert metadata["Name"].lower() == name and metadata["Version"] == version
    metadata_row = identical(installed_info / "METADATA", bundled_info / "METADATA")
    license_files = set(
        p
        for p in installed_info.rglob("*")
        if p.is_file() and (p.name.upper().startswith(("LICENSE", "COPYING")))
    )
    for declared in metadata.get_all("License-File", []):
        choices = (installed_info / declared, installed_info / "licenses" / declared)
        declared_file = next((p for p in choices if p.is_file()), None)
        assert declared_file is not None, (name, declared)
        assert declared_file.resolve().is_relative_to(installed_info.resolve())
        license_files.add(declared_file)
    assert license_files, name
    licenses = [
        identical(p, bundled_info / p.relative_to(installed_info)) for p in sorted(license_files)
    ]
    code_names = sorted(k for k in pyz.toc if k == name or k.startswith(name + "."))
    assert code_names, name
    rows.append(
        {
            "name": name,
            "version": version,
            "metadata": metadata_row,
            "declaredLicenseFiles": metadata.get_all("License-File", []),
            "actualLicenseFiles": licenses,
            "pyzModules": code_names,
        }
    )
resources = []
for name in ("i05-source-package-parity-manifest.json", "i05-source-package-parity-inputs.json"):
    relative = Path("ontolearn_engine/probe_inputs") / name
    resources.append(identical(ROOT / "packages/engine/src" / relative, INTERNAL / relative))
contracts = []
for source in sorted((ROOT / "packages/contracts/v2").rglob("*")):
    if source.is_file():
        contracts.append(
            identical(
                source,
                INTERNAL / "contracts/v2" / source.relative_to(ROOT / "packages/contracts/v2"),
            )
        )
contracts.append(
    identical(
        ROOT / "packages/contracts/python/contract_v2.py",
        INTERNAL / "contracts/python/contract_v2.py",
    )
)
lock = identical(ROOT / "uv.lock", INTERNAL / "provenance/uv.lock")
native = sorted(
    p for p in (INTERNAL / "wcwidth").rglob("*") if p.is_file() and p.suffix in (".so", ".dylib")
)
assert native, "wcwidth native extension absent"
python_libs = sorted(
    p
    for p in INTERNAL.rglob("*")
    if p.is_file() and p.name.startswith("libpython3.12") and p.suffix == ".dylib"
)
assert python_libs, "bundled Python shared library absent"
with (ENGINE / "ontolearn-engine").open("rb") as source:
    source.seek(archive._end_offset - archive._COOKIE_LENGTH)
    cookie = struct.unpack(archive._COOKIE_FORMAT, source.read(archive._COOKIE_LENGTH))
assert cookie[-2] == 312
report = {
    "kind": "M08-actual-package-static-inventory/1",
    "distributions": rows,
    "resources": resources,
    "contracts": contracts,
    "lock": lock,
    "launcher": identity(ENGINE / "ontolearn-engine"),
    "pythonBuild": {
        "pyinstallerCookiePython": cookie[-2],
        "pythonLibraryName": cookie[-1].rstrip(bytes([0])).decode(),
        "builderInterpreter": sys.version,
        "builderExecutable": sys.executable,
        "bundledLibraries": [identity(p) for p in python_libs],
    },
    "wcwidthNativeFiles": [identity(p) for p in native],
    "runtimeImportExecuted": False,
    "semanticParityExecutedByThisScript": False,
    "limits": [
        "PYZ code inventory and native file presence do not prove frozen import/loader identity",
        "Python cookie/shared library and build log are static build identity, "
        "not runtime Python execution",
        "No frozen provenance reader or semantic entrypoint exists in this three-path change",
    ],
}
print(json.dumps(report, ensure_ascii=False, indent=2))
