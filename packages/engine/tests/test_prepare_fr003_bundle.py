"""Clean-checkout preparation uses the actual adopted ZIP, never a runtime double."""

import hashlib
import importlib.util
import io
import os
import stat
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "prepare_fr003_bundle", ROOT / "scripts/prepare-fr003-bundle.py"
)
PREPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARE)


def snapshot(root):
    return {
        path.relative_to(root).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in root.rglob("*")
        if path.is_file()
    }


def test_clean_stage_contains_the_complete_original_22_members_and_is_idempotent(tmp_path):
    destination = tmp_path / "bundle"
    PREPARE.prepare(destination=destination)
    with zipfile.ZipFile(PREPARE.ARCHIVE) as archive:
        original = {info.filename: archive.read(info) for info in archive.infolist()}
    assert len(original) == 22
    assert sum(map(len, original.values())) == 1_338_939
    assert {name: raw for name, (raw, _) in snapshot(destination).items()} == original
    if os.name == "posix":
        assert stat.S_IMODE(destination.stat().st_mode) == 0o555
        for path in destination.rglob("*"):
            assert stat.S_IMODE(path.stat().st_mode) == (0o555 if path.is_dir() else 0o444)
    provider = original[PREPARE.PREFIX + "loader/t01-provider.json"]
    payload = original[PREPARE.PREFIX + "loader/load-input.json"]
    assert len(provider) == 198 and provider.endswith(b"\n")
    assert (
        hashlib.sha256(provider).hexdigest()
        == "a2200250856474ebbae669151891d5495e7fcd042e8f8f0a77ccbb0553b521ee"
    )
    assert len(payload) == 10930
    assert (
        hashlib.sha256(payload).hexdigest()
        == "52952b637b02ba283d47a9e0c34a1691c1d850b94bb9b366a9863a55507c435e"
    )
    before = snapshot(destination)
    PREPARE.prepare(destination=destination)
    assert snapshot(destination) == before


@pytest.mark.parametrize("mutation", ["missing", "changed", "extra"])
def test_existing_stage_failure_is_not_repaired_or_overwritten(tmp_path, mutation):
    destination = tmp_path / "bundle"
    PREPARE.prepare(destination=destination)
    target = destination / PREPARE.PREFIX / "loader/load-input.json"
    # Only the owned negative fixture is made writable to inject corruption.
    target.parent.chmod(0o755)
    target.chmod(0o644)
    if mutation == "missing":
        target.unlink()
    elif mutation == "changed":
        target.write_bytes(target.read_bytes() + b" ")
    else:
        destination.chmod(0o755)
        (destination / "unexpected.txt").write_bytes(b"owned negative fixture")
        destination.chmod(0o555)
    if mutation != "missing":
        target.chmod(0o444)
    target.parent.chmod(0o555)
    before = snapshot(destination)
    with pytest.raises(ValueError):
        PREPARE.prepare(destination=destination)
    assert snapshot(destination) == before


def test_changed_archive_is_rejected_before_staging(tmp_path):
    archive = tmp_path / "changed.zip"
    raw = bytearray(PREPARE.ARCHIVE.read_bytes())
    raw[len(raw) // 2] ^= 1
    archive.write_bytes(raw)
    destination = tmp_path / "bundle"
    with pytest.raises(ValueError, match="ZIP identity mismatch"):
        PREPARE.prepare(archive, destination)
    assert not destination.exists()


@pytest.mark.parametrize("mutation", ["duplicate", "escape", "symlink", "unknown"])
def test_member_structure_is_rejected_even_after_a_test_only_outer_seal(
    tmp_path, monkeypatch, mutation
):
    # Deliberately re-seal only this test's archive to reach structural checks;
    # production always retains the original constant ZIP identity.
    changed = io.BytesIO()
    with zipfile.ZipFile(PREPARE.ARCHIVE) as original, zipfile.ZipFile(changed, "w") as output:
        entries = original.infolist()
        for index, member in enumerate(entries):
            name = member.filename
            if index == 0:
                if mutation == "duplicate":
                    name = entries[1].filename
                elif mutation == "escape":
                    name = PREPARE.PREFIX + "../escape.txt"
                elif mutation == "unknown":
                    name = PREPARE.PREFIX + "unadopted.txt"
            info = zipfile.ZipInfo(name)
            if index == 0 and mutation == "symlink":
                info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
            output.writestr(info, original.read(member))
    raw = changed.getvalue()
    archive = tmp_path / "sealed-test-only.zip"
    archive.write_bytes(raw)
    monkeypatch.setattr(PREPARE, "ZIP_BYTES", len(raw))
    monkeypatch.setattr(PREPARE, "ZIP_SHA256", hashlib.sha256(raw).hexdigest())
    destination = tmp_path / "bundle"
    with pytest.raises(ValueError):
        PREPARE.prepare(archive, destination)
    assert not destination.exists()
    assert not (tmp_path / "escape.txt").exists()


def test_an_existing_preparation_lock_is_never_removed(tmp_path):
    destination = tmp_path / "bundle"
    lock = tmp_path / ".bundle.prepare.lock"
    lock.write_bytes(b"another owner's lock")
    with pytest.raises(FileExistsError):
        PREPARE.prepare(destination=destination)
    assert lock.read_bytes() == b"another owner's lock"
    assert not destination.exists()


@pytest.mark.parametrize("location", ["archive", "parent", "member"])
def test_filesystem_links_are_rejected_without_writing_the_target(tmp_path, location):
    destination = tmp_path / "bundle"
    archive = PREPARE.ARCHIVE
    if location == "member":
        PREPARE.prepare(destination=destination)
        link = destination / PREPARE.PREFIX / "loader/t01-provider.json"
        link.parent.chmod(0o755)
        link.unlink()
        target = tmp_path / "outside.json"
        target.write_bytes(b"outside content")
    elif location == "parent":
        target = tmp_path / "outside"
        target.mkdir()
        link = tmp_path / "linked-parent"
        destination = link / "bundle"
    else:
        target = PREPARE.ARCHIVE
        link = tmp_path / "linked.zip"
        archive = link
    try:
        link.symlink_to(target, target_is_directory=location == "parent")
    except OSError as error:
        pytest.skip(f"Symlink creation unavailable on this host: {error}")
    before = target.read_bytes() if target.is_file() else snapshot(target)
    with pytest.raises(ValueError):
        PREPARE.prepare(archive, destination)
    after = target.read_bytes() if target.is_file() else snapshot(target)
    assert after == before


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission contract")
def test_existing_writable_member_is_rejected_without_chmod_repair(tmp_path):
    destination = tmp_path / "bundle"
    PREPARE.prepare(destination=destination)
    member = destination / PREPARE.PREFIX / "loader/t01-provider.json"
    member.chmod(0o644)
    before = snapshot(destination)
    with pytest.raises(ValueError, match="permissions"):
        PREPARE.prepare(destination=destination)
    assert snapshot(destination) == before
    assert stat.S_IMODE(member.stat().st_mode) == 0o644
