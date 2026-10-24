"""Stage the adopted T09 bundle, without network or a second content producer."""

import hashlib
import io
import json
import os
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "resources/examples/equipment-maintenance-resource-source-v2.zip"
DESTINATION = ROOT / "build/release-resources/fr003-bundle-v2"
ZIP_BYTES = 1_344_035
ZIP_SHA256 = "b8717a53501e0825c5209faaf7e056e28d2f8c5f8c74b4b7e1f7bdf8b618164a"
MANIFEST_BYTES = 7566
MANIFEST_SHA256 = "23de1c472afd808761073ee2b46e6fa920508b1f869321062143950efd1ed8fb"
PREFIX = "examples/equipment-maintenance/"


def is_link(path):
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def regular_bytes(path, maximum):
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    flags |= getattr(os, "O_BINARY", 0)
    if is_link(path):
        raise ValueError("Bundle symlink refused")
    with os.fdopen(os.open(path, flags), "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise ValueError("Bundle member is not a bounded regular file")
        data = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
        if len(data) != before.st_size or (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        ) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise ValueError("Bundle member changed while reading")
        return data


def load_bundle(archive=ARCHIVE):
    data = regular_bytes(archive, ZIP_BYTES)
    if len(data) != ZIP_BYTES or hashlib.sha256(data).hexdigest() != ZIP_SHA256:
        raise ValueError("Adopted bundle ZIP identity mismatch")
    with zipfile.ZipFile(io.BytesIO(data)) as bundle:
        infos = bundle.infolist()
        names = [item.filename for item in infos]
        if len(names) != 22 or len(set(names)) != 22:
            raise ValueError("Adopted bundle must contain exactly 22 unique members")
        for item in infos:
            path = PurePosixPath(item.filename)
            mode = item.external_attr >> 16
            if (
                not item.filename.startswith(PREFIX)
                or path.is_absolute()
                or any(part in {"", ".", ".."} for part in item.filename.split("/"))
                or "\\" in item.filename
                or item.is_dir()
                or stat.S_ISLNK(mode)
                or stat.S_IFMT(mode) not in {0, stat.S_IFREG}
            ):
                raise ValueError("Unsafe bundle member")
        if PREFIX + "manifest.json" not in names:
            raise ValueError("Adopted bundle manifest missing")
        raw = bundle.read(PREFIX + "manifest.json")  # Also validates the ZIP member CRC.
        if len(raw) != MANIFEST_BYTES or hashlib.sha256(raw).hexdigest() != MANIFEST_SHA256:
            raise ValueError("Adopted bundle manifest mismatch")
        manifest = json.loads(raw.decode("utf-8"))
        pins = {PREFIX + "manifest.json": (MANIFEST_BYTES, MANIFEST_SHA256)}
        for member in manifest["members"]:
            name = PREFIX + member["path"]
            if name in pins:
                raise ValueError("Duplicate bundle manifest member")
            pins[name] = (member["bytes"], member["sha256"])
        if set(names) != set(pins):
            raise ValueError("Bundle members differ from the complete adopted manifest")
        payload = {}
        for name, (size, digest) in pins.items():
            if bundle.getinfo(name).file_size != size:
                raise ValueError("Bundle member size mismatch")
            value = bundle.read(name)  # CRC is checked before any staging write.
            if len(value) != size or hashlib.sha256(value).hexdigest() != digest:
                raise ValueError("Bundle member identity mismatch")
            payload[name] = value
        if sum(map(len, payload.values())) != 1_338_939:
            raise ValueError("Bundle aggregate size mismatch")
        return payload


def safe_directories(path):
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if is_link(current):
            raise ValueError("Staging directory symlink refused")
        current.mkdir(exist_ok=True)
        if not current.is_dir():
            raise ValueError("Staging parent must be a directory")


def verify_tree(destination, payload):
    if is_link(destination) or not destination.is_dir():
        raise ValueError("Staged bundle root must be a directory")
    if os.name == "posix" and stat.S_IMODE(destination.stat().st_mode) != 0o555:
        raise ValueError("Staged bundle root permissions differ from the read-only contract")
    files, directories = set(), set()
    for parent, dirs, leaves in os.walk(destination, followlinks=False):
        for name in dirs + leaves:
            path = Path(parent) / name
            if is_link(path):
                raise ValueError("Staged bundle symlink refused")
            relative = path.relative_to(destination).as_posix()
            if name in dirs:
                directories.add(relative)
            else:
                files.add(relative)
            if os.name == "posix" and stat.S_IMODE(path.stat().st_mode) != (
                0o555 if name in dirs else 0o444
            ):
                raise ValueError("Staged bundle permissions differ from the read-only contract")
    expected_dirs = {
        str(p) for name in payload for p in PurePosixPath(name).parents if str(p) != "."
    }
    if files != set(payload) or directories != expected_dirs:
        raise ValueError("Existing staged bundle has missing or unknown members")
    for name, expected in payload.items():
        if regular_bytes(destination / name, len(expected)) != expected:
            raise ValueError("Existing staged bundle changed; it will not be overwritten")


def prepare(archive=ARCHIVE, destination=DESTINATION):
    payload = load_bundle(archive)
    destination = destination.absolute()
    safe_directories(destination.parent)
    lock = destination.parent / ("." + destination.name + ".prepare.lock")
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    owned_lock = os.fstat(descriptor)
    scratch = None
    try:
        if destination.exists() or is_link(destination):
            verify_tree(destination, payload)
            return
        scratch = Path(tempfile.mkdtemp(prefix=".fr003-stage-", dir=destination.parent))
        for name, value in payload.items():
            path = scratch / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(value)
            if os.name == "posix":
                path.chmod(0o444)
        if os.name == "posix":
            for parent, _, _ in os.walk(scratch, topdown=False):
                Path(parent).chmod(0o555)
        verify_tree(scratch, payload)
        # Cooperating preparers use the lock. Refuse a destination observed here;
        # this is not a no-replace guarantee against unrelated concurrent writers.
        if destination.exists() or is_link(destination):
            raise ValueError("Staging destination appeared during preparation")
        scratch.rename(destination)
        scratch = None
    finally:
        if scratch is not None:
            for parent, _, leaves in os.walk(scratch):
                Path(parent).chmod(0o700)
                for leaf in leaves:
                    (Path(parent) / leaf).chmod(0o600)
            shutil.rmtree(scratch)
        os.close(descriptor)
        current_lock = lock.lstat()
        if (current_lock.st_dev, current_lock.st_ino) == (owned_lock.st_dev, owned_lock.st_ino):
            lock.unlink()


if __name__ == "__main__":
    prepare()
    print("Verified and staged all 22 adopted FR-003 bundle members.")
