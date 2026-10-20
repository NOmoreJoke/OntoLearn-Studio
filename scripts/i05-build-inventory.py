"""Capture exact Python lock, plugin entries and licenses into the engine bundle."""

import hashlib
import json
import platform
import shutil
import sys
import sysconfig
import tomllib
from importlib.metadata import distribution
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

MAC_SOURCE = "cpython-3.12.12-20260203-macos-arm64"
LINUX_SOURCE = "cpython-3.12.15-20261013-linux-aarch64"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resource(source, relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise RuntimeError("Invalid native provenance resource path")
    return source / path


def _verify_native_resources(source, native):
    if sha(source / "upstream-PYTHON.json.raw") != native["metadataSha256"]:
        raise RuntimeError("Native upstream metadata integrity failure")
    for item in [*native["licenseFiles"], *native.get("sourceEvidence", [])]:
        if sha(_resource(source, item["path"])) != item["sha256"]:
            raise RuntimeError("Native source/license integrity failure")


def _match_macos(base_prefix, native):
    from macholib.mach_o import LC_SEGMENT_64
    from macholib.MachO import MachO

    library = base_prefix / "lib/libpython3.12.dylib"
    data = library.read_bytes()
    sections = {}
    for command, _segment, section_list in MachO(str(library)).headers[0].commands:
        if command.cmd == LC_SEGMENT_64:
            for section in section_list:
                if section.offset:
                    key = (
                        section.segname.rstrip(b"\0").decode()
                        + ":"
                        + section.sectname.rstrip(b"\0").decode()
                    )
                    sections[key] = hashlib.sha256(
                        data[section.offset : section.offset + section.size]
                    ).hexdigest()
    if sections != native["sectionSha256"]:
        raise RuntimeError("Native runtime changed; refresh actual source/license provenance")


def _match_linux(base_prefix, native):
    expected = {item["path"]: item["sha256"] for item in native["binaryFiles"]}
    if len(expected) != 10 or len(native["binaryFiles"]) != 10:
        raise RuntimeError("Incomplete Linux native binary provenance")
    observed = set()
    for path in base_prefix.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        # Dependencies installed into base site-packages have separate wheel
        # provenance; this branch authenticates the CPython distribution itself.
        if "site-packages" in path.relative_to(base_prefix).parts:
            continue
        with path.open("rb") as handle:
            if handle.read(4) == b"\x7fELF":
                observed.add(str(path.relative_to(base_prefix)))
    if observed != set(expected):
        raise RuntimeError("Linux native runtime binary set changed")
    for relative, digest in expected.items():
        if sha(_resource(base_prefix, relative)) != digest:
            raise RuntimeError("Linux native runtime binary integrity failure")


def collect_native(root, target, *, system=None, machine=None, version=None, base_prefix=None):
    """Select only proven runtime sources; unknown runtimes stay explicitly pending."""
    system = platform.system() if system is None else system
    machine = platform.machine() if machine is None else machine
    version = platform.python_version() if version is None else version
    base_prefix = Path(sys.base_prefix) if base_prefix is None else Path(base_prefix)
    identity = {"system": system, "machine": machine, "pythonVersion": version, "build": None}
    source_name = None
    if (system, machine, version) == ("Darwin", "arm64", "3.12.12"):
        source_name = MAC_SOURCE
    elif (system, machine, version) == ("Linux", "aarch64", "3.12.15"):
        build_file = base_prefix / "BUILD"
        identity["build"] = build_file.read_text().strip() if build_file.is_file() else None
        if identity["build"] == "20261013":
            source_name = LINUX_SOURCE
    result = {
        "nativeLicenseProvenanceMatched": False,
        "nativeLicenseScope": "different runtime/platform: native source matching pending",
        "nativeLicenseSource": None,
        "nativeRuntimeIdentity": identity,
    }
    if source_name is None:
        return result
    source = root / "packages/engine/licenses" / source_name
    native = json.loads((source / "provenance.json").read_text())
    _verify_native_resources(source, native)
    if source_name == MAC_SOURCE:
        _match_macos(base_prefix, native)
        scope = "matched exact macOS arm64 runtime"
    else:
        expected_identity = native["runtime"]
        if expected_identity != identity:
            raise RuntimeError("Linux native runtime identity mismatch")
        _match_linux(base_prefix, native)
        scope = "matched exact Linux aarch64 CPython 3.12.15 BUILD 20261013 runtime"
    destination = target / "native-runtime"
    shutil.copytree(source, destination)
    _verify_native_resources(destination, native)
    if sha(destination / "provenance.json") != sha(source / "provenance.json"):
        raise RuntimeError("Native provenance copy integrity failure")
    result.update(
        nativeLicenseProvenanceMatched=True,
        nativeLicenseScope=scope,
        nativeLicenseSource=source_name,
    )
    return result


def build_inventory(root, target):
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    runtime = set()

    def visit(name):
        name = canonicalize_name(name)
        if name in runtime:
            return
        runtime.add(name)
        for text in distribution(name).requires or []:
            requirement = Requirement(text)
            # rdflib[html] is enabled by pySHACL; its extra must be carried through.
            if requirement.marker is None or any(
                requirement.marker.evaluate({"extra": extra}) for extra in ("", "html")
            ):
                visit(requirement.name)

    visit("ontolearn-engine")
    locked = tomllib.loads((root / "uv.lock").read_text())["package"]
    entries = []
    for item in locked:
        name = item["name"]
        if name == "ontolearn-workspace":
            continue
        try:
            dist = distribution(name)
        except Exception:
            entries.append(
                {
                    "name": name,
                    "version": item["version"],
                    "role": "lock-only-other-platform",
                    "licenseFiles": [],
                }
            )
            continue
        assert dist.version == item["version"], name
        license_files = []
        for path in dist.files or []:
            if any(word in path.name.upper() for word in ("LICENSE", "COPYING", "NOTICE")):
                source = Path(dist.locate_file(path))
                if not source.is_file():
                    raise RuntimeError("Dependency license source missing: " + name)
                destination = target / "licenses" / name / str(path)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
                if sha(source) != sha(destination):
                    raise RuntimeError("Dependency license copy integrity failure")
                license_files.append(
                    {"path": str(destination.relative_to(target)), "sha256": sha(destination)}
                )
        if name != "ontolearn-engine" and not license_files:
            raise RuntimeError("Dependency has no bundled license: " + name)
        entries.append(
            {
                "name": name,
                "version": dist.version,
                "role": "runtime" if canonicalize_name(name) in runtime else "build-test-tool",
                "license": dist.metadata.get("License-Expression") or dist.metadata.get("License"),
                "classifiers": [
                    c for c in dist.metadata.get_all("Classifier", []) if "License" in c
                ],
                "licenseFiles": license_files,
                "entryPoints": [
                    {"group": p.group, "name": p.name, "value": p.value} for p in dist.entry_points
                ],
            }
        )
    python_license = Path(sysconfig.get_path("stdlib")) / "LICENSE.txt"
    if not python_license.is_file():
        # CPython Windows installations normally keep LICENSE.txt at base prefix.
        python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if not python_license.is_file():
        raise RuntimeError("CPython license missing from build runtime")
    shutil.copyfile(python_license, target / "CPython-LICENSE.txt")
    if sha(python_license) != sha(target / "CPython-LICENSE.txt"):
        raise RuntimeError("CPython license copy integrity failure")

    manifest = {
        "python": platform.python_version(),
        "pythonLicenseSha256": sha(python_license),
        "uvLockSha256": sha(root / "uv.lock"),
        "packages": entries,
        "controlledRules": "in-tree ontolearn_engine.semantic; no additional rule library",
        **collect_native(root, target),
        "scope": "complete uv.lock Python inventory; bundled runtime and build tools separated; "
        "not a legal compliance determination or Electron dependency inventory",
    }
    (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "packages": len(entries),
                "runtime": sorted(runtime),
                "licenseFiles": sum(len(e["licenseFiles"]) for e in entries),
            }
        )
    )


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    build_inventory(root, root / "build/i05-inventory")
