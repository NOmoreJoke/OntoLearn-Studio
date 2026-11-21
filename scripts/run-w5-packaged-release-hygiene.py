"""W5 packaged release hygiene and packaging-configuration gate.

Fail-closed checks over one already-packaged desktop product tree plus the
repository packaging configuration. Never signs, launches, installs or
notarizes anything; this script only reads bytes and writes two JSON
artifacts:

* verifies the exactly-one packaged product (macOS ``*.app/Contents/Resources``,
  ``*unpacked/resources`` or a ``@ontolearndesktop`` sibling ``resources/``);
* verifies the six ``extraResources`` entries exist with substantively
  non-empty bytes (engine executable, contracts v2 registry/schema, the
  FR003 equipment-maintenance example, NOTICE and both Electron license files);
* scans every file name under the release root for sensitive/debug residue
  (keys, keystores, env files, user databases, staging selections) while
  leaving ordinary runtime libraries (``.dat``/``.pak``/``.so``/``.dylib`` …)
  alone;
* re-checks the Stage 0 packaging invariants in ``apps/desktop/electron-builder.yml``
  and ``apps/desktop/package.json`` (mandatory signing/notarization, no
  hardcoded identities, unsigned ``package:dir`` isolated from the signed
  release builds).

``summary.json`` always records ``releaseAuthorized: false`` and
``installerAcceptanceClaimed: false``: a directory pre-verification package
never substitutes for signed-installer acceptance evidence. Exit status is
``0`` only when every check passes.
"""

import argparse
import hashlib
import json
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BUILDER = REPO_ROOT / "apps/desktop/electron-builder.yml"
DESKTOP_PACKAGE = REPO_ROOT / "apps/desktop/package.json"
ENGINE_NAMES = ("ontolearn-engine", "ontolearn-engine.exe")
FORBIDDEN_SUFFIXES = (".pem", ".key", ".p12", ".pfx", ".sqlite", ".sqlite3", ".db")
EXAMPLE_MIN_FILES = 3
FORBIDDEN_KEY = re.compile(
    r"^\s*[\w-]*(?:password|secret|certificate|api[-_]?key|identity|csc)[\w-]*\s*:", re.IGNORECASE
)


def detect_product(release: Path) -> tuple[Path, str]:
    """Exactly one packaged product resources directory, or fail closed."""
    candidates = []
    for asar in release.rglob("app.asar"):
        resources = asar.parent
        product_root = resources.parent
        if resources.name == "Resources" and product_root.name == "Contents":
            bundle = product_root.parent
            if bundle.suffix == ".app":
                candidates.append((resources, bundle))
        elif resources.name == "resources" and (
            product_root.name.endswith("unpacked") or (product_root / "@ontolearndesktop").exists()
        ):
            candidates.append((resources, product_root))
    unique = {resources: root for resources, root in candidates}
    if len(unique) != 1:
        raise RuntimeError(f"Expected exactly one packaged desktop product; found {len(unique)}")
    resources, product_root = next(iter(unique.items()))
    if resources.name == "Resources":
        platform = "macos"
    elif any(product_root.glob("*.exe")):
        platform = "windows"
    else:
        platform = "linux"
    return resources, platform


def file_sha256(path: Path) -> dict:
    data = path.read_bytes()
    return {"path": str(path), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def nonempty_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_size >= 1


def resource_checks(resources: Path) -> tuple[dict, Path]:
    engine = next((name for name in ENGINE_NAMES if (resources / "engine" / name).is_file()), None)
    engine_path = resources / "engine" / engine if engine else resources / "engine"
    examples = resources / "examples/equipment-maintenance"
    example_files = (
        [path for path in examples.rglob("*") if path.is_file()] if examples.is_dir() else []
    )
    checks = {
        "engineExecutable": engine is not None and nonempty_file(engine_path),
        "contractsRegistry": nonempty_file(resources / "contracts/v2/registry.json"),
        "contractsSchema": nonempty_file(resources / "contracts/v2/schema.json"),
        "examples": examples.is_dir()
        and len(example_files) >= EXAMPLE_MIN_FILES
        and (examples / "manifest.json").is_file(),
        "notice": nonempty_file(resources / "licenses/NOTICE"),
        "electronLicense": nonempty_file(resources / "licenses/electron/LICENSE"),
        "chromiumLicenses": nonempty_file(resources / "licenses/electron/LICENSES.chromium.html"),
    }
    return checks, engine_path


def scan_forbidden_files(release: Path) -> tuple[list[str], int]:
    """File-name scan for secrets/debug residue; runtime libraries stay allowed."""
    hits = []
    scanned = 0
    for base, directories, filenames in os.walk(release):
        for names in (directories, filenames):
            for name in names:
                scanned += 1
                lowered = name.lower()
                if (
                    lowered.endswith(FORBIDDEN_SUFFIXES)
                    or lowered == ".env"
                    or lowered.startswith(".env.")
                    or name.startswith(".ontolearn-host-selections")
                ):
                    hits.append(str(Path(base) / name))
    return sorted(hits), scanned


def yaml_sections(text: str) -> dict:
    sections: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        if re.match(r"^[A-Za-z][\w-]*:", line):
            current = line.split(":", 1)[0]
            sections.setdefault(current, [])
        if current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines) for name, lines in sections.items()}


def config_checks() -> dict:
    builder = yaml_sections(BUILDER.read_text(encoding="utf-8"))
    desktop = json.loads(DESKTOP_PACKAGE.read_text(encoding="utf-8"))
    whole_builder = "\n".join(builder.values())
    forbidden_keys = [line for line in whole_builder.split("\n") if FORBIDDEN_KEY.match(line)]
    extra = builder.get("extraResources", "")
    release_mac = desktop.get("scripts", {}).get("package:release:mac", "")
    release_win = desktop.get("scripts", {}).get("package:release:win", "")
    package_dir = desktop.get("scripts", {}).get("package:dir", "")
    return {
        "forceCodeSigning": builder.get("forceCodeSigning", "").strip() == "forceCodeSigning: true",
        "macHardenedRuntime": "hardenedRuntime: true" in builder.get("mac", ""),
        "macNotarize": "notarize: true" in builder.get("mac", ""),
        "macDmg": "- target: dmg" in builder.get("mac", ""),
        "macArm64": "- arm64" in builder.get("mac", ""),
        "macIdentityEnabled": "identity" not in builder.get("mac", ""),
        "winSignAndEdit": "signAndEditExecutable: true" in builder.get("win", ""),
        "winSignExecutable": "signExecutable: true" in builder.get("win", ""),
        "winNsis": "- target: nsis" in builder.get("win", ""),
        "winX64": "- x64" in builder.get("win", ""),
        "extraResourcesCount": extra.count("- from:") == 6,
        "extraResourcesFr003": "fr003-bundle-v2" in extra,
        "extraResourcesLicenses": "licenses/electron/LICENSE" in extra
        and "LICENSES.chromium.html" in extra,
        "zeroHardcodedSecrets": not forbidden_keys,
        "packageDirUnsignedOverrides": all(
            flag in package_dir
            for flag in (
                "-c.forceCodeSigning=false",
                "-c.mac.identity=null",
                "-c.mac.hardenedRuntime=false",
                "-c.mac.notarize=false",
                "-c.win.signExecutable=false",
            )
        ),
        "releaseBuildsSeparated": "dmg" in release_mac
        and "arm64" in release_mac
        and "nsis" in release_win
        and "x64" in release_win
        and "-c." not in release_mac
        and "-c." not in release_win,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fail-closed hygiene gate over a packaged desktop release directory."
    )
    parser.add_argument("release", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    release = args.release.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    resources, platform = detect_product(release)
    checks, engine_path = resource_checks(resources)
    secret_hits, scanned_files = scan_forbidden_files(release)
    config = config_checks()
    inventory_paths = {
        "package-lock.json": REPO_ROOT / "package-lock.json",
        "uv.lock": REPO_ROOT / "uv.lock",
        "electron-builder.yml": BUILDER,
        "app.asar": resources / "app.asar",
        "engine": engine_path,
        "NOTICE": resources / "licenses/NOTICE",
        "electron-LICENSE": resources / "licenses/electron/LICENSE",
    }
    inventory_files = {}
    for name, path in inventory_paths.items():
        inventory_files[name] = (
            file_sha256(path) if path.is_file() else {"path": str(path), "missing": True}
        )
    failures = [name for name, passed in checks.items() if not passed]
    failures += [f"secret:{hit}" for hit in secret_hits]
    failures += [name for name, value in inventory_files.items() if value.get("missing")]
    failures += [name for name, passed in config.items() if not passed]
    inventory = {
        "files": inventory_files,
        "resourceStats": {
            "scannedFiles": scanned_files,
            "engineFiles": sum(1 for _ in (resources / "engine").rglob("*") if _.is_file()),
            "contractsFiles": sum(1 for _ in (resources / "contracts").rglob("*") if _.is_file()),
            "examplesFiles": sum(1 for _ in (resources / "examples").rglob("*") if _.is_file()),
        },
    }
    (output / "inventory.json").write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    summary = {
        "allOk": not failures,
        "platform": platform,
        "resourceChecks": checks,
        "secretScanClean": not secret_hits,
        "configInvariantsOk": all(config.values()),
        # A directory pre-verification package is never release authorization
        # and never installer acceptance evidence.
        "releaseAuthorized": False,
        "installerAcceptanceClaimed": False,
        "failures": failures,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if failures:
        print(json.dumps({"status": "failed", "failures": failures}))
        raise SystemExit(1)
    print(json.dumps({"status": "passed", "platform": platform}))


if __name__ == "__main__":
    main()
