"""Platform source selection, exact byte checks and fail-closed copying."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "native_inventory", ROOT / "scripts/i05-build-inventory.py"
)
INVENTORY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INVENTORY)


def digest(data):
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def linux_fixture(tmp_path):
    """Synthetic small files test selection mechanics, not upstream provenance."""
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "BUILD").write_text("20261013")
    source = tmp_path / "packages/engine/licenses" / INVENTORY.LINUX_SOURCE
    source.mkdir(parents=True)
    (source / "licenses").mkdir()
    (source / "licenses/LICENSE.test.txt").write_bytes(b"test license\n")
    (source / "upstream-PYTHON.json.raw").write_bytes(b'{"synthetic":true}')
    (source / "source-evidence").mkdir()
    (source / "source-evidence/observation.txt").write_bytes(b"synthetic test observation")
    binaries = []
    for index in range(10):
        name = "lib/test" + str(index) + ".so"
        path = runtime / name
        path.parent.mkdir(exist_ok=True)
        data = b"\x7fELFsynthetic test " + str(index).encode()
        path.write_bytes(data)
        binaries.append({"path": name, "sha256": digest(data)})
    native = {
        "runtime": {
            "system": "Linux",
            "machine": "aarch64",
            "pythonVersion": "3.12.15",
            "build": "20261013",
        },
        "metadataSha256": digest((source / "upstream-PYTHON.json.raw").read_bytes()),
        "licenseFiles": [
            {"path": "licenses/LICENSE.test.txt", "sha256": digest(b"test license\n")}
        ],
        "sourceEvidence": [
            {
                "path": "source-evidence/observation.txt",
                "sha256": digest(b"synthetic test observation"),
            }
        ],
        "binaryFiles": binaries,
    }
    (source / "provenance.json").write_text(json.dumps(native))
    return tmp_path, runtime, source


def collect(data, **overrides):
    root, runtime, _ = data
    values = {"system": "Linux", "machine": "aarch64", "version": "3.12.15", "base_prefix": runtime}
    values.update(overrides)
    target = root / "inventory"
    target.mkdir(exist_ok=True)
    return INVENTORY.collect_native(root, target, **values)


def test_exact_linux_chooses_its_own_source_and_preserves_bytes(linux_fixture):
    result = collect(linux_fixture)
    root, _, source = linux_fixture
    assert result["nativeLicenseProvenanceMatched"] is True
    assert result["nativeLicenseSource"] == INVENTORY.LINUX_SOURCE
    assert result["nativeLicenseScope"] == (
        "matched exact Linux aarch64 CPython 3.12.15 BUILD 20261013 runtime"
    )
    for path in source.rglob("*"):
        if path.is_file():
            assert (root / "inventory/native-runtime" / path.relative_to(source)).read_bytes() == (
                path.read_bytes()
            )


@pytest.mark.parametrize(
    "overrides",
    [
        {"system": "Windows"},
        {"machine": "x86_64"},
        {"version": "3.12.14"},
    ],
)
def test_unmatched_runtime_is_pending_and_copies_no_foreign_source(linux_fixture, overrides):
    result = collect(linux_fixture, **overrides)
    assert result["nativeLicenseProvenanceMatched"] is False
    assert result["nativeLicenseSource"] is None
    assert "pending" in result["nativeLicenseScope"]
    assert not (linux_fixture[0] / "inventory/native-runtime").exists()


@pytest.mark.parametrize("build", [None, "20261009"])
def test_other_linux_build_is_not_misidentified(linux_fixture, build):
    path = linux_fixture[1] / "BUILD"
    if build is None:
        path.unlink()
    else:
        path.write_text(build)
    result = collect(linux_fixture)
    assert result["nativeLicenseProvenanceMatched"] is False
    assert result["nativeRuntimeIdentity"]["build"] == build
    assert not (linux_fixture[0] / "inventory/native-runtime").exists()


@pytest.mark.parametrize(
    "path",
    [
        "licenses/LICENSE.test.txt",
        "upstream-PYTHON.json.raw",
        "source-evidence/observation.txt",
    ],
)
def test_source_corruption_aborts_before_copy(linux_fixture, path):
    (linux_fixture[2] / path).write_bytes(b"changed source")
    with pytest.raises(RuntimeError, match="integrity failure"):
        collect(linux_fixture)
    assert not (linux_fixture[0] / "inventory/native-runtime").exists()


@pytest.mark.parametrize("change", ["changed", "missing", "extra"])
def test_actual_elf_mutation_cannot_be_marked_matching(linux_fixture, change):
    runtime = linux_fixture[1]
    if change == "missing":
        (runtime / "lib/test0.so").unlink()
    elif change == "changed":
        (runtime / "lib/test0.so").write_bytes(b"\x7fELFchanged")
    else:
        (runtime / "lib/unknown.so").write_bytes(b"\x7fELFextra")
    with pytest.raises(RuntimeError, match="Linux native runtime binary"):
        collect(linux_fixture)


def test_failed_copy_propagates(linux_fixture, monkeypatch):
    def failed(*args, **kwargs):
        raise OSError("synthetic copy failure")

    monkeypatch.setattr(INVENTORY.shutil, "copytree", failed)
    with pytest.raises(OSError, match="synthetic copy failure"):
        collect(linux_fixture)


def test_post_copy_tampering_is_detected(linux_fixture, monkeypatch):
    real_copy = INVENTORY.shutil.copytree

    def tampered(source, destination, *args, **kwargs):
        result = real_copy(source, destination, *args, **kwargs)
        license_file = Path(destination) / "licenses/LICENSE.test.txt"
        if license_file.is_file():
            license_file.write_bytes(b"corrupted copy")
        return result

    monkeypatch.setattr(INVENTORY.shutil, "copytree", tampered)
    with pytest.raises(RuntimeError, match="integrity failure"):
        collect(linux_fixture)


def test_path_escape_is_rejected(linux_fixture):
    native_path = linux_fixture[2] / "provenance.json"
    native = json.loads(native_path.read_text())
    native["licenseFiles"][0]["path"] = "../outside.txt"
    native_path.write_text(json.dumps(native))
    with pytest.raises(RuntimeError, match="Invalid native provenance resource path"):
        collect(linux_fixture)


def test_real_source_metadata_licenses_and_210_section_binding_are_intact():
    source = ROOT / "packages/engine/licenses" / INVENTORY.LINUX_SOURCE
    native = json.loads((source / "provenance.json").read_text())
    INVENTORY._verify_native_resources(source, native)
    assert len(native["licenseFiles"]) == 19
    assert len(native["binaryFiles"]) == 10
    assert sum(len(row["allocatedSections"]) for row in native["binaryFiles"]) == 210
    comparison = json.loads((source / "source-evidence/native-comparison.json.raw").read_text())
    assert all(
        row["installedEqualsStripped"]
        and row["installedAllocatedSectionsEqualFull"]
        and row["fullVsStrippedAllocatedSectionsEqual"]
        for row in comparison["comparisons"].values()
    )
    metadata = json.loads((source / "upstream-PYTHON.json.raw").read_text())
    assert metadata["python_version"] == "3.12.15"
    assert metadata["target_triple"] == "aarch64-unknown-linux-gnu"
    assert metadata["build_options"] == "pgo+lto"
    assert not (source / "licenses/LICENSE.zlib-ng.txt").exists()
    exception = native["upstreamMetadataExceptions"][0]
    assert exception["actualZlib"] == "ordinary zlib 1.3.2 statically linked from build/lib/libz.a"
    assert exception["missingReferencedFile"] == "licenses/LICENSE.zlib-ng.txt"


def test_original_mac_provenance_is_still_intact():
    source = ROOT / "packages/engine/licenses" / INVENTORY.MAC_SOURCE
    native = json.loads((source / "provenance.json").read_text())
    INVENTORY._verify_native_resources(source, native)
    assert len(native["licenseFiles"]) == 19
    assert len(native["sectionSha256"]) == 15


def test_unknown_platform_keeps_actual_cpython_and_wheel_licenses(tmp_path, monkeypatch):
    monkeypatch.setattr(INVENTORY.platform, "system", lambda: "UnknownTestOS")
    target = tmp_path / "inventory"
    INVENTORY.build_inventory(ROOT, target)
    manifest = json.loads((target / "manifest.json").read_text())
    assert manifest["nativeLicenseProvenanceMatched"] is False
    assert "pending" in manifest["nativeLicenseScope"]
    assert not (target / "native-runtime").exists()
    assert INVENTORY.sha(target / "CPython-LICENSE.txt") == manifest["pythonLicenseSha256"]
    assert manifest["uvLockSha256"] == INVENTORY.sha(ROOT / "uv.lock")
    licenses = [item for package in manifest["packages"] for item in package["licenseFiles"]]
    assert licenses
    for item in licenses:
        assert INVENTORY.sha(target / item["path"]) == item["sha256"]
