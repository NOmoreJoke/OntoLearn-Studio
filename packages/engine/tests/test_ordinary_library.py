"""Definitions only until a separate runtime ticket.

TestPureOrdinary: explicit in-memory issuer/Store doubles, no SQLite or process.
TestSQLiteOrdinary: own temporary real JobStore, no stdio/child/native; separately gated.
No test double is a production physical/read-work authority.
"""

from contextlib import contextmanager, nullcontext
from copy import deepcopy
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import Coordinator, ServiceFault
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.project.ordinary_library import (
    OrdinaryReadAuthority,
    consume_choices_ticket,
)
from ontolearn_engine.resources import CONTRACT


def uid():
    return str(uuid4())


def project(identity, revision=0):
    return {
        "projectId": identity,
        "projectRevision": revision,
        "inputSnapshotId": "a" * 64,
        "dependencyVector": {"facts:asserted": revision},
        "formatVersion": 2,
    }


class DoubleAuthority(OrdinaryReadAuthority):
    """Test-only injection, with no claim about actual SQLite physical work."""

    def __init__(self, owner=None, *, ticket=True):
        self._owner = owner or uid()
        self.ticket = ticket
        self.scopes = []

    @property
    def owner_id(self):
        return self._owner

    def allows_owner(self, store, session):
        return True

    def read_scope(self, store, session, purpose, identity):
        self.scopes.append((store, session, purpose, identity))
        return nullcontext() if self.ticket else None


class TrackingAuthority(DoubleAuthority):
    """Only observes the fake scope lifetime. It never attests physical release."""

    def __init__(self):
        super().__init__()
        self.active = False
        self.failed_holding = []

    @contextmanager
    def read_scope(self, store, session, purpose, identity):
        self.active = True
        try:
            yield
        except BaseException as error:
            # Keep first failure reachable; no fake claim of zero failed holding.
            self.failed_holding.append(error)
            raise
        finally:
            self.active = False


class DoubleStore:
    actual_format = 2

    def __init__(self):
        self.project = uid()
        self.calls = []
        self.actor = None
        self.rows = [{"projectId": self.project}]
        self.result = project(self.project)
        self.error = None
        self.during_get = None

    def ordinary_project_choices(self, *, limit, _read_ticket=None):
        consume_choices_ticket(_read_ticket, self)
        self.calls.append(("choices", limit))
        return deepcopy(self.rows)

    def project_get(self, identity):
        self.calls.append(("get", identity))
        # The actual get is in the acquire stack, but does not grant normal requests.
        if self.during_get:
            self.during_get()
        if self.error:
            raise self.error
        return deepcopy(self.result)


def actor(store=None, authority=None, *, base=None, test_mode=False):
    store = store or DoubleStore()
    value = Coordinator(
        store,
        ordinary_authority=authority,
        allowed_projects=base,
        test_mode=test_mode,
        emit=lambda value: None,
    )
    store.actor = value
    value.session = uid()
    return value


def params(value, op, **fields):
    return {"op": op, "ownerId": value.ordinary.owner_id, **fields}


def choices(value, seq=1):
    return value.ordinary.dispatch(params(value, "choices", menuSeq=seq))["choices"]


def acquire(value, choice, seq=1, identity=None):
    return value.ordinary.dispatch(
        params(
            value,
            "acquire",
            actionId=identity or uid(),
            actionSeq=seq,
            choiceRef=choice["choiceRef"],
        )
    )


def commit(value, result):
    return value.ordinary.dispatch(
        {k: v for k, v in (result | {"op": "commit"}).items() if k != "project"}
    )


def release(value, result):
    return value.ordinary.dispatch(
        params(value, "release", actionId=result["actionId"], actionSeq=result["actionSeq"])
    )


def expect_fault(code, call):
    with pytest.raises((JobFault, ServiceFault)) as caught:
        call()
    assert caught.value.code == code
    return caught.value


class TestPureOrdinary:
    def test_missing_production_issuer_and_dict_do_zero_store_calls(self):
        for authority in (None, {"owner_id": uid(), "allows_owner": True}):
            value = actor(authority=authority)
            expect_fault(
                "PERMISSION_DENIED",
                lambda value=value: value.ordinary.dispatch(
                    {"op": "choices", "ownerId": uid(), "menuSeq": 1}
                ),
            )
            assert value.store.calls == []
            assert value.ordinary.projects() == frozenset()

    def test_missing_read_ticket_and_fixture_mode_do_zero_store_calls(self):
        for authority, test_mode in (
            (DoubleAuthority(ticket=False), False),
            (DoubleAuthority(), True),
        ):
            value = actor(authority=authority, test_mode=test_mode)
            expect_fault("PERMISSION_DENIED", lambda value=value: choices(value))
            assert value.store.calls == []

    def test_actual_get_once_action_is_not_external_gate(self):
        value = actor(authority=DoubleAuthority())
        row = choices(value)[0]
        value.store.during_get = lambda: expect_fault(
            "PERMISSION_DENIED", lambda: value._authorize({"projectId": row["projectId"]})
        )
        result = acquire(value, row)
        assert value.store.calls == [("choices", 64), ("get", row["projectId"])]
        assert value.ordinary.projects() == frozenset()
        assert CONTRACT.validate("result_ordinary.library", result)
        selected = commit(value, result)
        assert selected["project"] == result["project"]
        assert value._authorize({"projectId": row["projectId"]}) == row["projectId"]
        assert commit(value, result) == selected
        assert len(value.store.calls) == 2
        release(value, result)
        expect_fault("PERMISSION_DENIED", lambda: value._authorize({"projectId": row["projectId"]}))

    def test_read_ticket_is_same_store_one_use_not_caller_dict(self):
        value = actor(authority=DoubleAuthority())
        expect_fault("PERMISSION_DENIED", lambda: consume_choices_ticket({}, value.store))
        with value.ordinary._read("choices", None) as ticket:
            expect_fault("PERMISSION_DENIED", lambda: consume_choices_ticket(ticket, DoubleStore()))
            consume_choices_ticket(ticket, value.store)
            expect_fault("PERMISSION_DENIED", lambda: consume_choices_ticket(ticket, value.store))
        expect_fault("PERMISSION_DENIED", lambda: consume_choices_ticket(ticket, value.store))
        assert value.store.calls == []

    def test_failure_withdraws_only_new_reference_and_preserves_original_error(self):
        base = uid()
        value = actor(authority=DoubleAuthority(), base={base})
        first = acquire(value, choices(value)[0])
        commit(value, first)
        queued = {"id": "accepted-immutable"}
        active = {"job": queued}
        value.queued.append(queued)
        value.active["job"] = active
        failure = RuntimeError("first")
        value.store.error = failure
        with pytest.raises(RuntimeError) as caught:
            acquire(value, choices(value, 2)[0], seq=2)
        assert caught.value is failure
        assert value._authorize({"projectId": base}) == base
        assert value.ordinary.projects() == frozenset({first["project"]["projectId"]})
        assert list(value.queued) == [queued] and value.active["job"] is active
        release(value, first)
        assert value._authorize({"projectId": base}) == base
        assert list(value.queued) == [queued] and value.active["job"] is active
        expect_fault(
            "PERMISSION_DENIED",
            lambda: value._authorize({"projectId": first["project"]["projectId"]}),
        )

    def test_latest_two_actions_and_wrong_live_identity(self):
        value = actor(authority=DoubleAuthority())
        row = choices(value)[0]
        first, second = acquire(value, row), acquire(value, row, seq=2)
        expect_fault("INVALID_STATE", lambda: acquire(value, row, seq=3))
        expect_fault("PERMISSION_DENIED", lambda: commit(value, first))
        expect_fault(
            "INVALID_STATE",
            lambda: value.ordinary.dispatch(params(value, "release", actionId=uid(), actionSeq=2)),
        )
        commit(value, second)
        release(value, first)
        assert value.ordinary.projects() == frozenset({row["projectId"]})
        release(value, second)
        assert value.ordinary.projects() == frozenset()

    def test_closed_watermark_does_not_reconstruct_history_or_touch_new_selection(self):
        value = actor(authority=DoubleAuthority())
        row = choices(value)[0]
        first = acquire(value, row)
        release(value, first)
        second = acquire(value, row, seq=2)
        commit(value, second)
        echo = value.ordinary.dispatch(params(value, "release", actionId=uid(), actionSeq=1))
        assert set(echo) == {"op", "ownerId", "actionId", "actionSeq"}
        expect_fault("PERMISSION_DENIED", lambda: acquire(value, row, seq=1))
        assert value.ordinary.projects() == frozenset({row["projectId"]})

    def test_strict_get_mismatch_and_retained_book_reject_without_repair(self):
        value = actor(authority=DoubleAuthority())
        row = choices(value)[0]
        value.store.result["extra"] = True
        expect_fault("INVALID_STATE", lambda: acquire(value, row))
        assert value.ordinary._actions == {}
        value.store.result = project(value.store.project)
        value.store.result["dependencyVector"] = {f"query:k{i}": i for i in range(1400)}
        expect_fault("INVALID_STATE", lambda: acquire(value, row, seq=2))
        assert value.ordinary._actions == {}
        assert value.ordinary.projects() == frozenset()

    def test_choices_64_boundary_and_65_no_truncation(self):
        value = actor(authority=DoubleAuthority())
        value.store.rows = [{"projectId": uid()} for _ in range(64)]
        assert len(choices(value)) == 64
        old = deepcopy(value.ordinary._choices)
        value.store.rows.append({"projectId": uid()})
        error = expect_fault("RESOURCE_LIMIT", lambda: choices(value, 2))
        assert error.params == {"resource": "page"}
        assert value.ordinary._choices == old

    def test_engine_book_exact_and_one_unit_each_side(self):
        from ontolearn_engine.project.ordinary_library import BOOK_BYTES, BOOK_OBJECTS

        value = actor(authority=DoubleAuthority())
        value.ordinary._choice_bytes = BOOK_BYTES - 1
        value.ordinary._choice_objects = BOOK_OBJECTS - 1
        value.ordinary._room(extra_bytes=1, extra_objects=1)
        expect_fault("INVALID_STATE", lambda: value.ordinary._room(extra_bytes=2))
        expect_fault("INVALID_STATE", lambda: value.ordinary._room(extra_objects=2))
        assert value.store.calls == []

    def test_reply_frame_rejection_precedes_selection_and_preserves_base(self):
        base = uid()
        value = actor(authority=DoubleAuthority(), base={base})
        row = choices(value)[0]
        result = acquire(value, row)
        value.limits["maxFrameBytes"] = 1
        error = expect_fault("RESOURCE_LIMIT", lambda: commit(value, result))
        assert error.params == {"resource": "frame"}
        assert value.ordinary.projects() == frozenset()
        assert value.ordinary._actions[result["actionSeq"]].state == "VERIFIED"
        assert value._authorize({"projectId": base}) == base

    def test_scope_covers_strict_get_reserve_clone_and_reply(self, monkeypatch):
        from ontolearn_engine.project import ordinary_library as library

        authority = TrackingAuthority()
        value = actor(authority=authority)
        row = choices(value)[0]
        original_validate, original_canonical = CONTRACT.validate, library.canonical
        phases = []
        project_encodes = 0

        def validate(name, data):
            if name == "result_project.get":
                assert authority.active
                phases.append("strict")
            return original_validate(name, data)

        def canonical(data):
            nonlocal project_encodes
            if isinstance(data, dict) and data.get("projectId") == row["projectId"]:
                assert authority.active
                project_encodes += 1
                if project_encodes > 1:
                    record = next(iter(value.ordinary._actions.values()))
                    assert record.retained_bytes > 1024
                    phases.append("reserved-clone")
            return original_canonical(data)

        monkeypatch.setattr(CONTRACT, "validate", validate)
        monkeypatch.setattr(library, "canonical", canonical)
        result = acquire(value, row)
        assert phases[0] == "strict"
        assert phases.count("reserved-clone") >= 2
        assert result["project"] == value.store.result
        assert not authority.active
        assert authority.failed_holding == []

    def test_menu_old_new_overlap_is_reserved_while_scope_is_active(self, monkeypatch):
        from ontolearn_engine.project import ordinary_library as library

        authority = TrackingAuthority()
        value = actor(authority=authority)
        choices(value)
        old_reply = value.ordinary._menu_reply
        old_bytes, old_objects = value.ordinary._choice_bytes, value.ordinary._choice_objects
        original_uuid = library.uuid4
        allocations = []

        def issued_uuid():
            assert authority.active
            assert value.ordinary._menu_reply is old_reply
            assert value.ordinary._choice_bytes > old_bytes
            assert value.ordinary._choice_objects > old_objects
            allocations.append(True)
            return original_uuid()

        monkeypatch.setattr(library, "uuid4", issued_uuid)
        choices(value, 2)
        assert allocations == [True]
        assert value.ordinary._menu_reply is not old_reply
        assert not authority.active
        assert value.ordinary._choice_bytes == old_bytes

    def test_menu_private_book_rejection_keeps_old_page_and_first_failed_scope(self):
        from ontolearn_engine.project.ordinary_library import BOOK_BYTES

        authority = TrackingAuthority()
        value = actor(authority=authority)
        choices(value)
        old_reply, old_choices = value.ordinary._menu_reply, value.ordinary._choices
        value.ordinary._choice_bytes = BOOK_BYTES - 1
        error = expect_fault("INVALID_STATE", lambda: choices(value, 2))
        assert error.params == {}
        assert value.ordinary._menu_reply is old_reply
        assert value.ordinary._choices is old_choices
        assert value.ordinary._choice_bytes == BOOK_BYTES - 1
        assert authority.failed_holding == [error]
        assert not authority.active

    def test_page_bytes_and_frame_bytes_are_separate_actual_output_limits(self):
        value = actor(authority=DoubleAuthority())
        value.limits["maxPageBytes"] = 1
        error = expect_fault("RESOURCE_LIMIT", lambda: choices(value))
        assert error.params == {"resource": "page"}
        value.limits["maxPageBytes"] = 131072
        value.limits["maxFrameBytes"] = 1
        error = expect_fault("RESOURCE_LIMIT", lambda: choices(value))
        assert error.params == {"resource": "frame"}

    def test_canonical_exact_branches_and_nested_binding(self):
        import json
        from pathlib import Path

        examples = json.loads(
            (
                Path(__file__).resolve().parents[3]
                / "packages/contracts/v2/binding-regressions.json"
            ).read_text()
        )["ordinary"]
        for example in examples:
            assert (
                CONTRACT.matches_ordinary_response(
                    example["request"], example["response"], example["binding"]
                )
                is example["valid"]
            )
            bad = deepcopy(example["request"])
            bad["params"]["extra"] = True
            assert not CONTRACT.validate("request", bad)


class TestSQLiteOrdinary:
    def test_existing_mapping_strict_get_and_reopen_are_read_only(self, tmp_path):
        path = tmp_path / "ordinary.sqlite"
        store = JobStore(path, contract=CONTRACT)
        try:
            store.create_project("existing-fixture")
            public = store.public_project("existing-fixture")
            before = "\n".join(store._db.iterdump())
            value = actor(store, DoubleAuthority())
            row = choices(value)[0]
            assert row["projectId"] == public
            result = acquire(value, row)
            assert result["project"] == store.project_get(public)
            commit(value, result)
            release(value, result)
            assert "\n".join(store._db.iterdump()) == before
        finally:
            store.close()
        reopened = JobStore(path, contract=CONTRACT)
        try:
            assert reopened.project_get(public) == result["project"]
            assert "\n".join(reopened._db.iterdump()) == before
        finally:
            reopened.close()

    def test_direct_catalog_without_real_ticket_does_no_sql(self, tmp_path):
        store = JobStore(tmp_path / "deny.sqlite", contract=CONTRACT)
        try:
            trace = []
            store._db.set_trace_callback(trace.append)
            expect_fault("PERMISSION_DENIED", lambda: store.ordinary_project_choices(limit=64))
            assert trace == []
        finally:
            store.close()


class TestColdOrdinaryReadOnly:
    @pytest.mark.parametrize("existing_snapshot", [False, True])
    def test_complete_open_get_acquire_and_reopen_emit_no_write_sql(
        self, tmp_path, monkeypatch, existing_snapshot
    ):
        import sqlite3

        path = tmp_path / "readonly.sqlite"
        store = JobStore(path, contract=CONTRACT)
        store.create_project("cold")
        public = store.public_project("cold")
        if existing_snapshot:
            store.snapshot("cold")  # Explicit setup of the existing-row variant only.
        assert store._db.execute("SELECT count(*) FROM snapshots").fetchone()[0] == int(
            existing_snapshot
        )
        before = "\n".join(store._db.iterdump())
        store.close()
        original_connect = sqlite3.connect
        trace = []
        denied = []

        def readonly_connection(*args, **kwargs):
            connection = original_connect(*args, **kwargs)
            connection.execute("PRAGMA query_only=ON")
            connection.set_trace_callback(trace.append)
            forbidden = {
                sqlite3.SQLITE_INSERT,
                sqlite3.SQLITE_UPDATE,
                sqlite3.SQLITE_DELETE,
                sqlite3.SQLITE_CREATE_TABLE,
                sqlite3.SQLITE_CREATE_INDEX,
                sqlite3.SQLITE_CREATE_TRIGGER,
                sqlite3.SQLITE_DROP_TABLE,
                sqlite3.SQLITE_DROP_INDEX,
                sqlite3.SQLITE_DROP_TRIGGER,
                sqlite3.SQLITE_ALTER_TABLE,
            }

            def authorize(action, first, second, database, source):
                if action in forbidden:
                    denied.append((action, first, second))
                    return sqlite3.SQLITE_DENY
                return sqlite3.SQLITE_OK

            connection.set_authorizer(authorize)
            return connection

        monkeypatch.setattr(sqlite3, "connect", readonly_connection)
        expected = None
        for _ in range(2):
            reopened = JobStore(path, contract=CONTRACT)
            try:
                value = actor(reopened, DoubleAuthority())
                selected = choices(value)[0]
                result = acquire(value, selected)
                assert result["project"] == reopened.project_get(public)
                if expected is not None:
                    assert result["project"] == expected
                expected = result["project"]
                commit(value, result)
                release(value, result)
                assert not reopened._db.in_transaction
                assert "\n".join(reopened._db.iterdump()) == before
                assert reopened._db.execute("SELECT count(*) FROM snapshots").fetchone()[0] == int(
                    existing_snapshot
                )
            finally:
                reopened.close()
        assert denied == []
        assert not any("BEGIN IMMEDIATE" in statement.upper() for statement in trace)
        assert not any(
            statement.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP"))
            for statement in trace
        )

    def test_read_scope_does_not_issue_snapshot_write_authority(self, tmp_path):
        from ontolearn_engine.storage import Conflict, digest

        store = JobStore(tmp_path / "no-write-token.sqlite", contract=CONTRACT)
        try:
            store.create_project("cold")
            store.public_project("cold")
            before = "\n".join(store._db.iterdump())
            value = actor(store, DoubleAuthority())
            result = acquire(value, choices(value)[0])
            assert result["project"]["inputSnapshotId"] == digest(
                store._snapshot_projection("cold")
            )
            trace = []
            with store._read():
                store._db.set_trace_callback(trace.append)
                with pytest.raises(Conflict, match="Snapshot write scope required"):
                    store._materialize_snapshot(
                        result["project"]["inputSnapshotId"], "cold", _write_scope=value.ordinary
                    )
                store._db.set_trace_callback(None)
            assert trace == []
            assert "\n".join(store._db.iterdump()) == before
        finally:
            store.close()
