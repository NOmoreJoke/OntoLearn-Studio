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

root = Path(__file__).resolve().parents[1]
target = root / "build/i05-inventory"
if target.exists():
    shutil.rmtree(target)
target.mkdir(parents=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
            if source.is_file():
                destination = target / "licenses" / name / str(path)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
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
            "classifiers": [c for c in dist.metadata.get_all("Classifier", []) if "License" in c],
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
native_source = root / "packages/engine/licenses/cpython-3.12.12-20260203-macos-arm64"
shutil.copytree(native_source, target / "native-runtime")
native = json.loads((native_source / "provenance.json").read_text())
for item in native["licenseFiles"]:
    assert sha(native_source / item["path"]) == item["sha256"]
native_match = False
if (
    platform.system() == "Darwin"
    and platform.machine() == "arm64"
    and (platform.python_version() == "3.12.12")
):
    from macholib.mach_o import LC_SEGMENT_64
    from macholib.MachO import MachO

    library = Path(sys.base_prefix) / "lib/libpython3.12.dylib"
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
    native_match = sections == native["sectionSha256"]
    if not native_match:
        raise RuntimeError("Native runtime changed; refresh actual source/license provenance")
manifest = {
    "python": platform.python_version(),
    "pythonLicenseSha256": sha(python_license),
    "uvLockSha256": sha(root / "uv.lock"),
    "packages": entries,
    "controlledRules": "in-tree ontolearn_engine.semantic; no additional rule library",
    "nativeLicenseProvenanceMatched": native_match,
    "nativeLicenseScope": "matched exact macOS arm64 runtime"
    if native_match
    else "different runtime/platform: native source matching pending",
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
