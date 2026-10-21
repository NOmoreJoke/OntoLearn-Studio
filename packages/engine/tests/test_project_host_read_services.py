"""Actual Store3 private reader proofs; no path capability, IPC or GUI claim."""

import sqlite3
from contextlib import contextmanager
from dataclasses import replace

import pytest
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project import format3
from ontolearn_engine.project.project_host import HostReadFault, ProjectHostReader, ReadLimits
from ontolearn_engine.storage import Store, canonical, digest
from test_job_store import CONTRACT, uid

PROJECTS = [f"00000000-0000-4000-8000-{i:012d}" for i in range(1, 5)]
WRITE_ACTIONS = {
    getattr(sqlite3, name)
    for name in (
        "SQLITE_INSERT",
        "SQLITE_UPDATE",
        "SQLITE_DELETE",
        "SQLITE_CREATE_INDEX",
        "SQLITE_CREATE_TABLE",
        "SQLITE_CREATE_TEMP_INDEX",
        "SQLITE_CREATE_TEMP_TABLE",
        "SQLITE_CREATE_TEMP_TRIGGER",
        "SQLITE_CREATE_TEMP_VIEW",
        "SQLITE_CREATE_TRIGGER",
        "SQLITE_CREATE_VIEW",
        "SQLITE_DROP_INDEX",
        "SQLITE_DROP_TABLE",
        "SQLITE_DROP_TEMP_INDEX",
        "SQLITE_DROP_TEMP_TABLE",
        "SQLITE_DROP_TEMP_TRIGGER",
        "SQLITE_DROP_TEMP_VIEW",
        "SQLITE_DROP_TRIGGER",
        "SQLITE_DROP_VIEW",
        "SQLITE_ALTER_TABLE",
        "SQLITE_REINDEX",
        "SQLITE_ANALYZE",
        "SQLITE_ATTACH",
        "SQLITE_DETACH",
        "SQLITE_CREATE_VTABLE",
        "SQLITE_DROP_VTABLE",
    )
}


@pytest.fixture
def store(tmp_path):
    s = JobStore(tmp_path / "host.sqlite", contract=CONTRACT, target_format=3)
    for project in PROJECTS[:3]:
        s.create_project(project)
    yield s
    s.close()


def apply(s, project, change):
    return s.apply_application(project, uid(), change, actor=uid(), permission="write")


def metadata(s, project, name, *, version=0, archived=False):
    return apply(
        s,
        project,
        {
            "type": "metadata",
            "expectedVersion": version,
            "patch": {"name": name, "archived": archived},
        },
    )


def save(s, project, content, *, editor="q", generation=0, bound=0):
    return apply(
        s,
        project,
        {
            "type": "draft.save",
            "editor": editor,
            "expectedGeneration": generation,
            "boundDomainRevision": bound,
            "content": content,
        },
    )


def logical_dump(s):
    return "\n".join(s._db.iterdump())


def read_authorizer(rejected):
    def authorizer(action, first, second, _database, _trigger):
        if action in WRITE_ACTIONS or (
            action == sqlite3.SQLITE_PRAGMA
            and (
                first not in {"integrity_check", "foreign_key_check", "table_info", "user_version"}
                or first == "user_version"
                and second is not None
            )
        ):
            rejected.append((action, first, second))
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    return authorizer


@contextmanager
def zero_write(s):
    before = logical_dump(s)
    rejected, trace = [], []
    s._db.set_authorizer(read_authorizer(rejected))
    s._db.set_trace_callback(trace.append)
    try:
        yield trace
    finally:
        s._db.set_trace_callback(None)
        s._db.set_authorizer(None)
        assert not rejected, rejected
        assert logical_dump(s) == before
        assert not s._db.in_transaction


def expect_fault(reason, fn):
    with pytest.raises(HostReadFault) as raised:
        fn()
    assert str(raised.value) == raised.value.reason == reason


@contextmanager
def corrupt_immutable(s, table):
    """Fixture-only offline damage; restore schema to isolate record validation."""
    triggers = s._db.execute(
        "SELECT name,sql FROM sqlite_master WHERE type='trigger' AND tbl_name=?", (table,)
    ).fetchall()
    for name, _ in triggers:
        s._db.execute('DROP TRIGGER "' + name.replace('"', '""') + '"')
    yield
    for _, sql in triggers:
        s._db.execute(sql)


def test_complete_catalog_same_names_archive_stable_order_and_zero_writes(store, monkeypatch):
    s = store
    metadata(s, PROJECTS[0], "同名项目")
    metadata(s, PROJECTS[1], "同名项目", archived=True)
    reader = ProjectHostReader(s)

    def forbidden(*_args, **_kwargs):
        pytest.fail("reader called a known writing helper")

    for method in ("snapshot", "_snapshot", "project_get", "public_project"):
        monkeypatch.setattr(s, method, forbidden)
    with zero_write(s) as trace:
        first = reader.catalog_start(page_size=1)
        second = reader.catalog_next(first["nextCursor"])
        third = reader.catalog_next(second["nextCursor"])
    assert [r["items"][0]["projectId"] for r in (first, second, third)] == PROJECTS[:3]
    assert [r["offset"] for r in (first, second, third)] == [0, 1, 2]
    assert all(
        r["total"] == 3 and r["snapshotId"] == first["snapshotId"] for r in (first, second, third)
    )
    assert (
        first["items"][0]["metadata"]["name"]
        == second["items"][0]["metadata"]["name"]
        == "同名项目"
    )
    assert second["items"][0]["metadata"]["archived"] is True
    assert third["nextCursor"] is None and not reader._catalogs
    assert trace.count("BEGIN") == trace.count("ROLLBACK") == 1
    assert not any(sql.startswith("BEGIN IMMEDIATE") for sql in trace)


def test_freeze_does_not_mix_metadata_or_new_projects_and_returns_detached_values(store):
    reader = ProjectHostReader(store)
    first = reader.catalog_start(page_size=1)
    first["items"][0]["metadata"]["name"] = "caller mutation"
    metadata(store, PROJECTS[1], "after freeze", archived=True)
    store.create_project(PROJECTS[3])
    with zero_write(store):
        second = reader.catalog_next(first["nextCursor"])
        last = reader.catalog_next(second["nextCursor"])
        fresh = reader.catalog_start(page_size=4)
    assert second["items"][0]["metadata"]["name"] is None
    assert not second["items"][0]["metadata"]["archived"]
    assert second["items"][0]["metadataVersion"] == 0 and last["total"] == 3
    assert [item["projectId"] for item in fresh["items"]] == PROJECTS
    assert fresh["items"][1]["metadata"]["name"] == "after freeze"
    assert fresh["items"][0]["metadata"]["name"] is None


def test_workspace_one_read_transaction_existing_refs_and_project_identity(store, monkeypatch):
    s, project = store, PROJECTS[1]
    s.commit(
        project,
        0,
        uid(),
        "domain-seed",
        definitions=[
            {
                "layer": "rule",
                "id": "r",
                "value": {"enabled": True},
            }
        ],
    )
    receipt = metadata(s, project, "target")
    save(s, project, {"text": "真实大草稿" * 8000}, bound=0)
    checkpoint = s.project_checkpoint(project)
    reader = ProjectHostReader(s)
    for method in ("snapshot", "_snapshot", "project_get", "public_project"):
        monkeypatch.setattr(s, method, lambda *_a, **_k: pytest.fail("write helper"))
    with zero_write(s) as trace:
        result = reader.workspace(project, editor="q")
    assert trace[0] == "BEGIN" and trace[-1] == "ROLLBACK"
    assert trace.count("BEGIN") == trace.count("ROLLBACK") == 1
    assert set(result) == {
        "workspaceVersion",
        "projectId",
        "domainRevision",
        "metadataVersion",
        "metadata",
        "operationSequence",
        "checkpointRef",
        "inputSnapshotId",
        "draft",
    }
    assert result["projectId"] == project and result["domainRevision"] == 1
    assert result["metadataVersion"] == 1 and result["operationSequence"] == 3
    assert result["metadata"] == checkpoint["application"]["metadata"]
    assert result["inputSnapshotId"] == checkpoint["domainSnapshotRef"]
    assert result["checkpointRef"] != receipt["afterCheckpointRef"]
    draft = result["draft"]
    assert draft == {
        "editor": "q",
        "state": "present",
        "generation": 1,
        "present": True,
        "boundDomainRevision": 0,
        "contentHash": digest({"text": "真实大草稿" * 8000}),
        "content": {"text": "真实大草稿" * 8000},
    }
    assert s.load_snapshot(result["inputSnapshotId"])["project"] == project
    result["metadata"]["name"] = "mutate"
    result["draft"]["content"]["text"] = "mutate"
    assert reader.workspace(project, editor="q")["draft"] == draft | {
        "content": {"text": "真实大草稿" * 8000},
    }
    assert reader.workspace(PROJECTS[0], editor="q")["draft"] == {"editor": "q", "state": "missing"}


def test_draft_missing_tombstone_and_json_null_remain_distinct(store):
    reader, project = ProjectHostReader(store), PROJECTS[0]
    with zero_write(store):
        assert reader.workspace(project, editor="q")["draft"] == {"editor": "q", "state": "missing"}
    save(store, project, None)
    with zero_write(store):
        null = reader.workspace(project, editor="q")["draft"]
    assert null == {
        "editor": "q",
        "state": "present",
        "generation": 1,
        "present": True,
        "boundDomainRevision": 0,
        "contentHash": digest(None),
        "content": None,
    }
    apply(store, project, {"type": "draft.delete", "editor": "q", "expectedGeneration": 1})
    with zero_write(store):
        tombstone = reader.workspace(project, editor="q")["draft"]
    assert tombstone == null | {
        "state": "tombstone",
        "generation": 2,
        "present": False,
        "contentHash": None,
    }


@pytest.mark.parametrize(
    "kind", ["mapping", "app", "head", "snapshot", "metadata", "draft-hash", "draft-payload"]
)
def test_missing_or_corrupt_evidence_fails_without_any_repair(store, kind):
    s, project = store, PROJECTS[0]
    if kind.startswith("draft-"):
        save(s, project, {"text": "draft"})
    if kind == "mapping":
        with corrupt_immutable(s, "public_projects"):
            s._db.execute("DELETE FROM public_projects WHERE internal=?", (project,))
    elif kind == "app":
        s._db.execute("DELETE FROM app_projects WHERE project=?", (project,))
    elif kind == "head":
        s._db.execute("UPDATE app_projects SET checkpoint=NULL WHERE project=?", (project,))
    elif kind == "snapshot":
        with corrupt_immutable(s, "snapshots"):
            s._db.execute(
                "UPDATE snapshots SET payload='{}' WHERE id=(SELECT domain_snapshot "
                "FROM app_checkpoints WHERE project=? LIMIT 1)",
                (project,),
            )
    elif kind == "metadata":
        s._db.execute(
            "UPDATE app_projects SET metadata=? WHERE project=?",
            (canonical({"name": "forged"}), project),
        )
    else:
        column, value = ("content_hash", "f" * 64) if kind == "draft-hash" else ("payload", "null")
        s._db.execute(f"UPDATE app_drafts SET {column}=? WHERE project=?", (value, project))
    s._db.commit()
    reader = ProjectHostReader(s)
    with zero_write(s):
        expect_fault("structure", reader.catalog_start)
        expect_fault("structure", lambda: reader.workspace(project, editor="q"))
    assert not reader._catalogs


def test_dangling_public_mapping_and_invalid_uuid_cannot_disappear_in_join(store):
    store._db.execute("PRAGMA foreign_keys=OFF")
    store._db.execute("INSERT INTO public_projects VALUES(?,?)", (uid(), "nonexistent"))
    store._db.commit()
    with zero_write(store):
        expect_fault("structure", ProjectHostReader(store).catalog_start)


def test_uuid_mapping_survives_close_and_real_reopen(tmp_path):
    path = tmp_path / "reopen.sqlite"
    s = JobStore(path, contract=CONTRACT, target_format=3)
    s.create_project("real-internal-id")
    reader = ProjectHostReader(s)
    before = reader.catalog_start()["items"]
    reader.close()
    s.close()
    reopened = JobStore(path, contract=CONTRACT, target_format=3)
    try:
        with zero_write(reopened):
            after = ProjectHostReader(reopened).catalog_start()["items"]
        assert before == after
        assert before[0]["projectId"] != "real-internal-id"
    finally:
        reopened.close()


def test_cursor_single_use_order_cross_reader_spoof_and_project_confusion(store):
    reader, other = ProjectHostReader(store), ProjectHostReader(store)
    with zero_write(store):
        first = reader.catalog_start(page_size=1)
        token = first["nextCursor"]
        for fake in [PROJECTS[0], "forged", "A" * 43, None, {"cursor": token}]:
            expect_fault("cursor", lambda fake=fake: reader.catalog_next(fake))
        expect_fault("cursor", lambda: other.catalog_next(token))
        expect_fault("input", lambda: reader.workspace(token, editor="q"))
        next_page = reader.catalog_next(token)
        expect_fault("cursor", lambda: reader.catalog_next(token))
        last = reader.catalog_next(next_page["nextCursor"])
        expect_fault("cursor", lambda: reader.catalog_next(next_page["nextCursor"]))
        assert last["nextCursor"] is None and not reader._catalogs


def test_expiry_is_absolute_no_sliding_release_cancel_and_close(store):
    now = [100.0]
    reader = ProjectHostReader(
        store, limits=replace(ReadLimits(), snapshots=1, ttl_seconds=3), clock=lambda: now[0]
    )
    first = reader.catalog_start(page_size=1)
    now[0] += 2
    second = reader.catalog_next(first["nextCursor"])
    now[0] += 1
    with zero_write(store):
        expect_fault("expired", lambda: reader.catalog_next(second["nextCursor"]))
        assert not reader._catalogs
        fresh = reader.catalog_start(page_size=1)
        reader.catalog_cancel(fresh["nextCursor"])
        expect_fault("cursor", lambda: reader.catalog_next(fresh["nextCursor"]))
        fresh = reader.catalog_start(page_size=1)
        reader.close()
        expect_fault("state", lambda: reader.catalog_next(fresh["nextCursor"]))
        expect_fault("state", lambda: reader.workspace(PROJECTS[0], editor="q"))
    assert not reader._catalogs
    assert store.revision(PROJECTS[0]) == 0  # owner connection remains open


def test_snapshot_slot_and_precharged_total_refuse_whole_operation(store, monkeypatch):
    reader = ProjectHostReader(store, limits=replace(ReadLimits(), snapshots=1))
    first = reader.catalog_start(page_size=1)
    with zero_write(store):
        expect_fault("limit", lambda: reader.catalog_start(page_size=1))
    assert list(reader._catalogs) == [first["nextCursor"]]
    reader.catalog_cancel(first["nextCursor"])

    def unexpected(_s):
        pytest.fail("capacity/preflight must reject before materializing validation")

    monkeypatch.setattr(format3, "validate", unexpected)
    with zero_write(store):
        for limits in [
            replace(ReadLimits(), retained_bytes=100),
            replace(ReadLimits(), projects=1),
            replace(ReadLimits(), validation_rows=1),
            replace(ReadLimits(), validation_bytes=100),
            replace(ReadLimits(), validation_work=100),
        ]:
            bounded = ProjectHostReader(store, limits=limits)
            expect_fault("limit", bounded.catalog_start)
            assert not bounded._catalogs


def test_full_encoding_snapshot_row_page_workspace_and_draft_budgets(store):
    metadata(store, PROJECTS[1], "有界名称" * 100)
    save(store, PROJECTS[0], {"text": "完整内容" * 100})
    with zero_write(store):
        for field in ("snapshot_bytes", "catalog_row_bytes", "metadata_bytes"):
            reader = ProjectHostReader(store, limits=replace(ReadLimits(), **{field: 100}))
            expect_fault("limit", reader.catalog_start)
            assert not reader._catalogs
        for field in ("workspace_bytes", "draft_bytes"):
            reader = ProjectHostReader(store, limits=replace(ReadLimits(), **{field: 100}))
            expect_fault("limit", lambda reader=reader: reader.workspace(PROJECTS[0], editor="q"))
        reader = ProjectHostReader(store, limits=replace(ReadLimits(), page_bytes=700))
        first = reader.catalog_start(page_size=1)
        expect_fault("limit", lambda: reader.catalog_next(first["nextCursor"]))
        assert not reader._catalogs  # later-page error releases whole snapshot
        expect_fault("cursor", lambda: reader.catalog_next(first["nextCursor"]))
        first_page_too_big = ProjectHostReader(store, limits=replace(ReadLimits(), page_bytes=100))
        expect_fault("limit", first_page_too_big.catalog_start)
        assert not first_page_too_big._catalogs


def test_external_transaction_is_rejected_without_rollback_or_observing_uncommitted(store):
    reader = ProjectHostReader(store)
    store._db.execute("BEGIN")
    store._db.execute("UPDATE app_projects SET metadata_version=99 WHERE project=?", (PROJECTS[0],))
    expect_fault("state", reader.catalog_start)
    expect_fault("state", lambda: reader.workspace(PROJECTS[0], editor="q"))
    assert store._db.in_transaction
    assert (
        store._db.execute(
            "SELECT metadata_version FROM app_projects WHERE project=?", (PROJECTS[0],)
        ).fetchone()[0]
        == 99
    )
    store._db.rollback()
    with zero_write(store):
        assert reader.workspace(PROJECTS[0], editor="q")["metadataVersion"] == 0


@pytest.mark.parametrize("page_size", [True, 0, -1, 65, 1.5, "1", None])
def test_page_input_is_strict(store, page_size):
    with zero_write(store):
        expect_fault("input", lambda: ProjectHostReader(store).catalog_start(page_size=page_size))


@pytest.mark.parametrize("editor", ["", None, 5, "x" * 513, "\ud800"])
def test_editor_input_is_strict(store, editor):
    with zero_write(store):
        expect_fault(
            "input", lambda: ProjectHostReader(store).workspace(PROJECTS[0], editor=editor)
        )


def test_limits_can_only_tighten_and_wrong_store_missing_project_safe_faults(store, tmp_path):
    for change in [
        {"ttl_seconds": 61},
        {"snapshots": 0},
        {"projects": True},
        {"validation_work": 0},
    ]:
        expect_fault("input", lambda change=change: replace(ReadLimits(), **change))
    old = Store(tmp_path / "v2.sqlite")
    try:
        expect_fault("state", lambda: ProjectHostReader(old))
    finally:
        old.close()
    expect_fault("input", lambda: ProjectHostReader(store, limits={}))
    with zero_write(store):
        expect_fault("missing", lambda: ProjectHostReader(store).workspace(uid(), editor="q"))


def test_authorizer_negative_control_detects_insert_or_ignore_even_when_no_change(store):
    attempts = []

    def deny(action, *_args):
        if action in WRITE_ACTIONS:
            attempts.append(action)
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    before = logical_dump(store)
    store._db.set_authorizer(deny)
    try:
        with pytest.raises(sqlite3.DatabaseError):
            store.snapshot(PROJECTS[0])
    finally:
        store._db.set_authorizer(None)
    assert sqlite3.SQLITE_INSERT in attempts and logical_dump(store) == before


def test_malformed_database_errors_never_include_sql_or_path(store):
    store._db.execute("ALTER TABLE public_projects RENAME TO lost_mapping")
    store._db.commit()
    with zero_write(store):
        expect_fault("structure", ProjectHostReader(store).catalog_start)


@pytest.mark.parametrize("actual", [0, 2, 4])
def test_actual_header_is_checked_each_database_read_not_configuration(store, actual):
    reader = ProjectHostReader(store)
    frozen = reader.catalog_start(page_size=1)
    store._db.execute(f"PRAGMA user_version={actual}")
    with zero_write(store):
        expect_fault("state", reader.catalog_start)
        expect_fault("state", lambda: reader.workspace(PROJECTS[0], editor="q"))
        expect_fault("state", ProjectHostReader(store).catalog_start)
        # Frozen pages deliberately have no connection I/O. Host must close the
        # reader on Store/location invalidation; no new authority is minted here.
        page = reader.catalog_next(frozen["nextCursor"])
        assert page["items"][0]["projectId"] == PROJECTS[1]
    reader.close()


def test_empty_real_catalog_is_complete_without_retention(tmp_path):
    s = JobStore(tmp_path / "empty.sqlite", contract=CONTRACT, target_format=3)
    try:
        reader = ProjectHostReader(s)
        with zero_write(s):
            result = reader.catalog_start()
        assert result["items"] == [] and result["total"] == result["offset"] == 0
        assert result["nextCursor"] is None and not reader._catalogs
    finally:
        s.close()


def test_invalid_public_uuid_is_not_normalized_or_replaced(store):
    with corrupt_immutable(store, "public_projects"):
        store._db.execute(
            "UPDATE public_projects SET public='not-a-uuid' WHERE internal=?", (PROJECTS[0],)
        )
    store._db.commit()
    with zero_write(store):
        expect_fault("structure", ProjectHostReader(store).catalog_start)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), 10**1000, True, "100"])
def test_bad_clock_value_releases_existing_memory_and_has_safe_reason(store, bad):
    now = [100.0]
    reader = ProjectHostReader(store, clock=lambda: now[0])
    first = reader.catalog_start(page_size=1)
    now[0] = bad
    with zero_write(store):
        expect_fault("state", lambda: reader.catalog_next(first["nextCursor"]))
    assert not reader._catalogs


def test_clock_failure_or_backward_step_releases_memory(store):
    now = [100.0]

    def clock():
        if isinstance(now[0], Exception):
            raise now[0]
        return now[0]

    for bad in (99.0, RuntimeError("private path must not escape")):
        now[0] = 100.0
        reader = ProjectHostReader(store, clock=clock)
        first = reader.catalog_start(page_size=1)
        now[0] = bad
        with zero_write(store):
            expect_fault(
                "state", lambda reader=reader, first=first: reader.catalog_next(first["nextCursor"])
            )
        assert not reader._catalogs


def test_random_token_collision_never_replaces_another_snapshot(store, monkeypatch):
    reader = ProjectHostReader(store)
    monkeypatch.setattr(
        "ontolearn_engine.project.project_host.secrets.token_urlsafe", lambda _: "A" * 43
    )
    first = reader.catalog_start(page_size=1)
    token = first["nextCursor"]
    with zero_write(store):
        second = reader.catalog_start(page_size=1)
        assert second["nextCursor"] != token
        assert set(reader._catalogs) == {token, second["nextCursor"]}
        next_page = reader.catalog_next(token)
        assert next_page["nextCursor"] not in {token, second["nextCursor"]}
        expect_fault("cursor", lambda: reader.catalog_next(token))
        last = reader.catalog_next(next_page["nextCursor"])
        assert last["offset"] == 2 and last["nextCursor"] is None
        reader.catalog_cancel(second["nextCursor"])
        fresh = reader.catalog_start(page_size=1)
        assert fresh["nextCursor"] not in {token, next_page["nextCursor"], second["nextCursor"]}
        expect_fault("cursor", lambda: reader.catalog_next(token))
        other = ProjectHostReader(store)
        other_first = other.catalog_start(page_size=1)
        assert other_first["nextCursor"] != fresh["nextCursor"]
        expect_fault("cursor", lambda: other.catalog_next(fresh["nextCursor"]))


def test_cursor_sequence_exhaustion_refuses_whole_page_and_releases_consumed_snapshot(store):
    reader = ProjectHostReader(store)
    first = reader.catalog_start(page_size=1)
    reader._cursor_sequence = format3.MAX_VERSION
    with zero_write(store):
        expect_fault("limit", lambda: reader.catalog_next(first["nextCursor"]))
        assert not reader._catalogs
        expect_fault("cursor", lambda: reader.catalog_next(first["nextCursor"]))
        expect_fault("limit", lambda: reader.catalog_start(page_size=1))
        assert not reader._catalogs
        assert reader.catalog_start(page_size=3)["nextCursor"] is None


@pytest.mark.parametrize("bad", ["wrong", None, "A" * 44])
def test_entropy_failure_is_safe_and_does_not_retain_partial_pages(store, monkeypatch, bad):
    reader = ProjectHostReader(store)
    first = reader.catalog_start(page_size=1)
    monkeypatch.setattr(
        "ontolearn_engine.project.project_host.secrets.token_urlsafe", lambda _: bad
    )
    with zero_write(store):
        expect_fault("state", lambda: reader.catalog_next(first["nextCursor"]))
        assert not reader._catalogs


def test_entropy_exception_is_safe_and_does_not_retain_partial_pages(store, monkeypatch):
    def fail(_size):
        raise OSError("private runtime detail")

    monkeypatch.setattr("ontolearn_engine.project.project_host.secrets.token_urlsafe", fail)
    reader = ProjectHostReader(store)
    with zero_write(store):
        expect_fault("state", lambda: reader.catalog_start(page_size=1))
        assert not reader._catalogs


@pytest.mark.parametrize("value", [3, 4])
def test_same_authorizer_rejects_same_value_and_changed_header_writes(store, value):
    before = logical_dump(store)
    rejected = []
    store._db.set_authorizer(read_authorizer(rejected))
    try:
        with pytest.raises(sqlite3.DatabaseError):
            store._db.execute(f"PRAGMA user_version={value}")
    finally:
        store._db.set_authorizer(None)
    assert rejected == [(sqlite3.SQLITE_PRAGMA, "user_version", str(value))]
    assert store._db.execute("PRAGMA user_version").fetchone()[0] == 3
    assert logical_dump(store) == before
