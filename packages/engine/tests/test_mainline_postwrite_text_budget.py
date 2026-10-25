"""Original writer cold history, real query worker and bounded text-page fees."""

import hashlib
import json
from contextlib import contextmanager

import pytest
import rdflib
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.project.query_definitions import QueryRead, query_read
from ontolearn_engine.resources import CONTRACT, LIMITS
from ontolearn_engine.storage import canonical
from test_mainline_dispatch import drain_owned_changesets, exchange, frame, uid
from test_mainline_postwrite_rows_budget import ledger, observe


@contextmanager
def cold_query(tmp_path, *, multibyte=False, escaped=True):
    body = ("\\" if escaped else "x") * 56300
    text = "ASK { }\n#" + (body[:-2] + "界😀" if multibyte else body)
    assert len(text) == 56309 and rdflib.__version__ == "7.6.0+ontolearn.fr201.3"
    draft = {
        "name": "scope",
        "description": "owned text prefix scope",
        "sparql": text,
        "scope": "asserted",
        "capabilityQuestion": "ASK?",
        "source": "editor",
    }
    definition = {
        "text": text,
        "references": [],
        "descriptor": {
            "version": 1,
            **{k: v for k, v in draft.items() if k != "sparql"},
        },
    }
    assert len(canonical(definition)) == ((112782 if multibyte else 112784) if escaped else 56484)
    store = JobStore(tmp_path / "cold.sqlite", contract=CONTRACT, target_format=3)
    actor = None
    try:
        # Valid existing history is supplied by the original trusted Store writer
        # before its first owner. No SQL seed, old DB, fake issuer or quota exists.
        internal = "cold-valid-text-scope"
        store.create_project(internal)
        project = store.public_project(internal)
        store.commit(
            internal,
            0,
            uid(),
            uid(),
            definitions=[
                {
                    "layer": "query",
                    "id": "scope-query",
                    "value": definition,
                }
            ],
        )
        actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
        assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
        assert exchange(actor, "project.open", {"projectId": project})["ok"]
        record = checked(
            actor,
            "query.definition.load",
            {
                "projectId": project,
                "definitionId": "scope-query",
                "selection": {"kind": "current"},
            },
        )
        ready = checked(
            actor,
            "query.execution.prepare",
            {
                "projectId": project,
                "operationId": uid(),
                "definitionBinding": {
                    k: record[k]
                    for k in (
                        "definitionId",
                        "definitionVersion",
                        "definitionSha256",
                        "descriptorVersion",
                        "descriptorSha256",
                    )
                },
                "visibleDraft": draft,
                "selection": {"kind": "current"},
            },
        )
        accepted = checked(
            actor,
            "job.create",
            {
                "projectId": project,
                "operationId": ready["operationId"],
                "capability": "query.execute",
                "input": ready["input"],
                "confirmationRef": None,
            },
        )
        drain_owned_changesets(actor)
        terminal = checked(actor, "job.get", {"projectId": project, "jobId": accepted["jobId"]})
        assert terminal["state"] == "succeeded", terminal
        header = checked(
            actor,
            "query.result.describe",
            {
                "projectId": project,
                "resultId": terminal["resultRef"]["resultId"],
            },
        )
        assert header["query"] == {"kind": "ASK", "value": True}
        assert header["executedText"]["sha256"] == hashlib.sha256(text.encode()).hexdigest()
        assert header["executedText"]["utf8Bytes"] == len(text.encode())
        yield actor, store, header["identity"], text
    finally:
        if actor is not None:
            actor.mainline.close()
        store.close()


def checked(actor, method, params):
    response = exchange(actor, method, params)
    assert response["ok"], response
    return response["result"]


@pytest.mark.parametrize("multibyte", [False, True], ids=["original56309", "utf8-scalars56309"])
def test_full_cold_text_prefixes_keep_identity_offsets_and_each_final_fee_once(
    tmp_path, monkeypatch, multibyte
):
    with cold_query(tmp_path, multibyte=multibyte) as (actor, store, binding, text):
        host = actor.mainline
        owner = (host.owner_id, host.host, host.session, host.generation, host.selected)
        events, stages, pages, assembled, cursors = [], [], [], bytearray(), set()
        observe(monkeypatch, host, store, events)
        original_pay = QueryRead.pay

        def pay(ticket, stage, **fees):
            stages.append({"request": ticket.budget.reply.request_id, "stage": stage, "fees": fees})
            return original_pay(ticket, stage, **fees)

        monkeypatch.setattr(QueryRead, "pay", pay)
        cursor = None
        try:
            for _ in range(64):
                request_ = frame(
                    actor,
                    "query.result.textPage",
                    {
                        "binding": binding,
                        "maxUtf8Bytes": 32768,
                        "cursor": cursor,
                    },
                )
                response = actor.request(request_)
                pages.append({"request": request_, "response": response})
                actor.finish_query_reply(request_["id"], emitted=True)
                assert response["ok"], response
                page = response["result"]
                raw = page["text"].encode("utf-8")
                assert page["identity"] == binding and page["kind"] == "text"
                assert page["order"] == "utf8-byte:asc" and page["startUtf8Byte"] == len(assembled)
                assert 0 < page["utf8Length"] == len(raw) <= 32768
                assert CONTRACT.encoded_size(page) <= LIMITS["maxPageBytes"]
                assert CONTRACT.encoded_size(page) + 1024 <= LIMITS["maxFrameBytes"]
                assembled.extend(raw)
                cursor = page["nextCursor"]
                if cursor is None:
                    break
                assert cursor not in cursors
                cursors.add(cursor)
            assert bytes(assembled) == text.encode("utf-8") and len(pages) > 1 and cursor is None
            fees = [e for e in events if "begin_transaction" in e.get("stack", [])]
            boundaries = [e for e in events if e["stage"] == "before_commit_final_material"]
            prepaid = [e for e in stages if e["stage"] == "text final prepaid"]
            assert len(fees) == len(boundaries) == len(prepaid) == len(pages)
            assert all(
                e["fee"] == {"bytes": 1114112, "objects": 8192, "work": 134217728} for e in fees
            )
            assert all(
                e["fees"] == {"bytes_": 528384, "objects": 256, "work": 1052672} for e in prepaid
            )
            assert all(e["before"] == e["after"] and "error" not in e for e in boundaries)
            assert host is actor.mainline and owner == (
                host.owner_id,
                host.host,
                host.session,
                host.generation,
                host.selected,
            )
            assert (
                not host.hold and host.replies == {} and store._read_admission.transaction is None
            )
            assert exchange(actor, "project.get", {"projectId": binding["projectId"]})["ok"]
        finally:
            (tmp_path / "text-budget.json").write_text(
                json.dumps(
                    {
                        "events": events,
                        "stages": stages,
                        "pages": pages,
                        "textCharacters": len(text),
                        "utf8Bytes": len(text.encode()),
                        "logicalAccountingNotRSS": True,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )


def test_text_fixed_fee_atomic_refusal_then_same_host_legal_continue(tmp_path, monkeypatch):
    with cold_query(tmp_path) as (actor, store, binding, _):
        host, admission = actor.mainline, store._read_admission
        owner = (host.owner_id, host.host, host.session, host.generation, host.selected)
        request_ = frame(
            actor,
            "query.result.textPage",
            {"binding": binding, "maxUtf8Bytes": 32768, "cursor": None},
        )
        host.begin(request_)
        events = []
        observe(monkeypatch, host, store, events)
        try:
            with pytest.raises(JobFault) as caught:
                with query_read(actor, request_["method"], request_["params"]) as ticket:
                    ticket.before_store(
                        store, "second actual diagnostic preflight", request_["params"]
                    )
                    with store._transaction():
                        pytest.fail("Failed prepayment must not enter the transaction body")
            assert caught.value.code == "RESOURCE_LIMIT" and caught.value.params == {
                "resource": "memory"
            }
            host.observe_error(request_["id"], caught.value)
            failures = [e for e in events if "error" in e]
            assert len(failures) == 1 and "begin_transaction" in failures[0]["stack"]
            assert failures[0]["before"] == failures[0]["after"]
            assert (
                admission.transaction is None
                and admission.active is None
                and not admission.charged_reply
            )
            assert not store._db.in_transaction and not host.hold
        finally:
            actor.finish_query_reply(request_["id"], emitted=True)
            (tmp_path / "text-refusal.json").write_text(
                json.dumps(events, indent=2) + "\n", encoding="utf-8"
            )
        page = checked(
            actor,
            "query.result.textPage",
            {"binding": binding, "maxUtf8Bytes": 32768, "cursor": None},
        )
        assert page["utf8Length"] > 0 and page["identity"] == binding
        assert actor.mainline is host and owner == (
            host.owner_id,
            host.host,
            host.session,
            host.generation,
            host.selected,
        )
        assert not host.hold and host.replies == {} and admission.transaction is None


@pytest.mark.parametrize("change", ["unknown", "replacement"])
def test_text_cursor_callback_revocation_denies_before_final_encoder(tmp_path, monkeypatch, change):
    from ontolearn_engine.project import query_presentation

    # Leave room for the replacement's real begin. The original near-full book
    # correctly rejects that new reply on capacity before replacement can occur.
    with cold_query(tmp_path, escaped=change != "replacement") as (actor, store, binding, _):
        host = actor.mainline
        params = {"binding": binding, "maxUtf8Bytes": 32768, "cursor": None}
        request_, successor = (
            frame(actor, "query.result.textPage", params),
            frame(actor, "query.result.textPage", params),
        )
        original_cursor, original_room = store._new_cursor, query_presentation._room
        observed, encoders_after_revocation = [], []
        cursors_before = store._db.execute("SELECT count(*) FROM job_cursors").fetchone()[0]

        def cursor(*args, **kwargs):
            value = original_cursor(*args, **kwargs)
            reply = host.current
            observed.append((reply, ledger(reply)))
            if change == "unknown":
                reply.unknown = True
            else:
                host.current = None
                host.begin(successor)
            return value

        def room(*args, **kwargs):
            if observed:
                encoders_after_revocation.append(True)
            return original_room(*args, **kwargs)

        monkeypatch.setattr(store, "_new_cursor", cursor)
        monkeypatch.setattr(query_presentation, "_room", room)
        response = actor.request(request_)
        assert (
            observed and not response["ok"] and response["error"]["code"] == "PERMISSION_DENIED"
        ), response
        reply, prepaid = observed[0]
        assert ledger(reply) == prepaid and encoders_after_revocation == []
        assert not store._db.in_transaction and store._read_admission.transaction is None
        assert store._db.execute("SELECT count(*) FROM job_cursors").fetchone()[0] == cursors_before
        if change == "replacement":
            assert host.current.request_id == successor["id"]
            assert ledger(host.current) == {"bytes": 1052672, "objects": 256, "work": 4096}
            actor.finish_query_reply(successor["id"], emitted=True)
        actor.finish_query_reply(request_["id"], emitted=True)
        assert (request_["id"] in host.replies) is (change == "unknown")
