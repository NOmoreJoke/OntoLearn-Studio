"""Selected-file bootstrap must authenticate the opened file, before any SQL."""

import gc
import os
import sqlite3
from pathlib import Path

import pytest
from ontolearn_engine.project import file_identity
from ontolearn_engine.project.format3 import Format3Fault


def identity(path):
    info = path.stat()
    return f"{info.st_dev}:{info.st_ino}"


def database(path, label):
    db = sqlite3.connect(path)
    try:
        with db:
            db.execute("CREATE TABLE proof(label TEXT)")
            db.execute("INSERT INTO proof VALUES(?)", (label,))
    finally:
        db.close()
    return path.read_bytes()


def test_opens_selected_handle_without_database_changes(tmp_path):
    path = (tmp_path / "selected.sqlite").resolve()
    before = database(path, "selected")
    db = file_identity.connect_verified(path, identity(path), require_existing=True)
    try:
        file_identity.verify_connection(db)
        file_identity.verify_connection(db)
        assert db.execute("SELECT label FROM proof").fetchall() == [("selected",)]
    finally:
        db.close()
    assert path.read_bytes() == before


def test_new_library_is_the_existing_empty_file_not_an_implicit_creation(tmp_path):
    path = (tmp_path / "new.sqlite").resolve()
    path.touch(exist_ok=False)
    expected = identity(path)
    db = file_identity.connect_verified(path, expected)
    try:
        assert path.read_bytes() == b""
        assert identity(path) == expected
        db.execute("CREATE TABLE proof(value)")
    finally:
        db.close()
    path.unlink()
    with pytest.raises(Format3Fault):
        file_identity.connect_verified(path, expected)
    assert not path.exists()


def test_open_existing_never_initializes_empty_file(tmp_path):
    path = (tmp_path / "empty.sqlite").resolve()
    path.touch()
    with pytest.raises(Format3Fault):
        file_identity.connect_verified(path, identity(path), require_existing=True)
    assert path.read_bytes() == b""


def test_actual_file_aba_cannot_connect_to_the_foreign_library(tmp_path, monkeypatch):
    selected = (tmp_path / "selected.sqlite").resolve()
    other = (tmp_path / "other.sqlite").resolve()
    saved = (tmp_path / "saved.sqlite").resolve()
    selected_bytes = database(selected, "selected")
    other_bytes = database(other, "foreign")
    expected = identity(selected)
    original = sqlite3.connect
    opened = []
    blocked = []
    statements = []

    def substituted(*args, **kwargs):
        try:
            os.replace(selected, saved)
        except PermissionError:
            # Windows guards must prevent the physical rename. This is an
            # asserted native outcome, not a skipped ABA acceptance case.
            blocked.append(True)
            assert os.name == "nt"
            handle = original(*args, **kwargs)
            opened.append(handle)
            return handle
        os.replace(other, selected)
        try:
            handle = original(*args, **kwargs)
            handle.set_trace_callback(statements.append)
            opened.append(handle)
        finally:
            os.replace(selected, other)
            os.replace(saved, selected)
        return handle

    monkeypatch.setattr(sqlite3, "connect", substituted)
    if os.name == "nt":
        db = file_identity.connect_verified(selected, expected, require_existing=True)
        try:
            assert blocked == [True]
            assert db.execute("SELECT label FROM proof").fetchall() == [("selected",)]
        finally:
            db.close()
    else:
        with pytest.raises(Format3Fault) as error:
            file_identity.connect_verified(selected, expected, require_existing=True)
        assert error.value.category == "structure"
        assert len(opened) == 1
        with pytest.raises(sqlite3.ProgrammingError):
            opened[0].execute("SELECT 1")
        assert statements == []  # No query, schema validation, or migration.
    assert identity(selected) == expected
    assert selected.read_bytes() == selected_bytes
    assert other.read_bytes() == other_bytes


@pytest.mark.skipif(os.name == "nt", reason="POSIX handle-ownership ambiguity")
def test_ambiguous_open_descriptors_fail_closed_and_close_only_own_connection(
    tmp_path, monkeypatch
):
    selected = (tmp_path / "selected.sqlite").resolve()
    database(selected, "selected")
    unrelated = tmp_path / "unrelated.txt"
    unrelated.write_text("unrelated")
    original = sqlite3.connect
    opened = []
    external = []

    def concurrent_open(*args, **kwargs):
        handle = original(*args, **kwargs)
        opened.append(handle)
        external.append(unrelated.open("rb"))
        return handle

    monkeypatch.setattr(sqlite3, "connect", concurrent_open)
    try:
        with pytest.raises(Format3Fault):
            file_identity.connect_verified(selected, identity(selected), require_existing=True)
        with pytest.raises(sqlite3.ProgrammingError):
            opened[0].execute("SELECT 1")
        assert external[0].read() == b"unrelated"  # Never close a guessed descriptor.
    finally:
        for handle in external:
            handle.close()


@pytest.mark.skipif(os.name == "nt", reason="POSIX descriptor enumeration")
def test_handle_enumeration_failure_never_falls_back_to_path_only(tmp_path, monkeypatch):
    selected = (tmp_path / "selected.sqlite").resolve()
    before = database(selected, "selected")
    expected = identity(selected)

    def denied(*args):
        raise PermissionError("descriptor enumeration denied")

    monkeypatch.setattr(file_identity.os, "scandir", denied)
    with pytest.raises(Format3Fault):
        file_identity.connect_verified(selected, expected, require_existing=True)
    assert selected.read_bytes() == before


@pytest.mark.skipif(os.name == "nt", reason="POSIX descriptor enumeration")
def test_descriptor_scan_has_a_hard_bound(tmp_path, monkeypatch):
    selected = (tmp_path / "selected.sqlite").resolve()
    before = database(selected, "selected")
    monkeypatch.setattr(file_identity, "_MAX_DESCRIPTORS", 1)
    with pytest.raises(Format3Fault):
        file_identity.connect_verified(selected, identity(selected), require_existing=True)
    assert selected.read_bytes() == before


@pytest.mark.skipif(os.name == "nt", reason="Windows prevents open-file replacement")
def test_runtime_path_drift_fences_original_connection_even_after_path_is_restored(tmp_path):
    selected = (tmp_path / "selected.sqlite").resolve()
    moved = selected.with_name("moved.sqlite")
    foreign = selected.with_name("foreign.sqlite")
    database(selected, "selected")
    database(foreign, "foreign")
    db = file_identity.connect_verified(selected, identity(selected), require_existing=True)
    try:
        os.replace(selected, moved)
        os.replace(foreign, selected)
        with pytest.raises(Format3Fault):
            file_identity.verify_connection(db)
        os.replace(selected, foreign)
        os.replace(moved, selected)
        with pytest.raises(Format3Fault):
            file_identity.verify_connection(db)
    finally:
        db.close()


@pytest.mark.skipif(os.name == "nt", reason="POSIX descriptor bootstrap critical section")
@pytest.mark.parametrize("initial_gc", [False, True])
def test_bootstrap_failure_preserves_collectors_prior_state(tmp_path, monkeypatch, initial_gc):
    selected = (tmp_path / "selected.sqlite").resolve()
    before = database(selected, "selected")
    previous = gc.isenabled()
    original = sqlite3.connect
    try:
        (gc.enable if initial_gc else gc.disable)()
        db = file_identity.connect_verified(selected, identity(selected), require_existing=True)
        db.close()
        assert gc.isenabled() == initial_gc

        def cannot_open(*args, **kwargs):
            raise sqlite3.OperationalError("test open failure")

        monkeypatch.setattr(sqlite3, "connect", cannot_open)
        with pytest.raises(sqlite3.OperationalError, match="test open failure"):
            file_identity.connect_verified(selected, identity(selected), require_existing=True)
        assert gc.isenabled() == initial_gc
        assert selected.read_bytes() == before
    finally:
        monkeypatch.setattr(sqlite3, "connect", original)
        (gc.enable if previous else gc.disable)()


@pytest.mark.skipif(os.name != "nt", reason="Windows complete-path sharing guard")
def test_windows_parent_directory_rename_is_blocked_during_open(tmp_path, monkeypatch):
    parent = (tmp_path / "selected-directory").resolve()
    parent.mkdir()
    selected = parent / "selected.sqlite"
    database(selected, "selected")
    original = sqlite3.connect
    blocked = []

    def move_parent(*args, **kwargs):
        with pytest.raises(PermissionError):
            os.replace(parent, parent.with_name("renamed"))
        blocked.append(True)
        return original(*args, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", move_parent)
    db = file_identity.connect_verified(selected, identity(selected), require_existing=True)
    db.close()
    assert blocked == [True]
    # No guard leaks after the connection bootstrap or after normal close.
    renamed = parent.with_name("renamed")
    os.replace(parent, renamed)
    assert Path(renamed / selected.name).exists()
