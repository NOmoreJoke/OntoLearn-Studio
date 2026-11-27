"""Real owned rowsPage regression: fixed final material must fit before greedy rows."""

import json
import os
import traceback
from itertools import product
from pathlib import Path

import pytest
import rdflib
from ontolearn_engine.job_store import JobFault
from ontolearn_engine.project.mainline import HELD_BYTES, HELD_OBJECTS, READ_WORK
from ontolearn_engine.project.query_definitions import query_read
from ontolearn_engine.storage import canonical, digest
from test_mainline_dispatch import confirmed_job, drain_owned_changesets, exchange, frame, uid
from test_mainline_named_example_dispatch import named_owned as named_owned
from test_mainline_named_example_dispatch import request
from test_mainline_named_example_dispatch import staged_bundle as staged_bundle

TEXT = (
    "PREFIX l: <urn:ontolearn:learning:>\n"
    "SELECT ?a ?b ?c ?d ?e WHERE { ?a a l:Equipment . ?b a l:Equipment . "
    "?c a l:Equipment . ?d a l:Equipment . ?e a l:Equipment . } ORDER BY ?a ?b ?c ?d ?e"
)
DRAFT = {
    "name": "三个固定设备的五列有序组合",
    "description": "真实 UI 正式保存、受管执行及固定结果读取；不使用模型或推导。",
    "sparql": TEXT,
    "scope": "asserted",
    "capabilityQuestion": "固定断言输入的完整预期结果是否相同？",
    "source": "editor",
}


def saved_query(actor, store):
    created = exchange(actor, "project.example.create", request("T04 SELECT 243 行"))
    assert created["ok"], created
    project = created["result"]["projectId"]
    definition = {
        "text": TEXT,
        "references": [],
        "descriptor": {"version": 1, **{k: v for k, v in DRAFT.items() if k != "sparql"}},
    }
    assert len(canonical(definition)) == 392
    job = confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": 1,
            "intent": "change",
            "plan": {
                "definitions": [
                    {"layer": "query", "id": "e2e-equipment-cartesian", "value": definition}
                ]
            },
        },
    )
    drain_owned_changesets(actor)
    assert store.get_job(project, job["jobId"])["state"] == "succeeded"
    loaded = exchange(
        actor,
        "query.definition.load",
        {
            "projectId": project,
            "definitionId": "e2e-equipment-cartesian",
            "selection": {"kind": "current"},
        },
    )
    assert loaded["ok"], loaded
    record = loaded["result"]
    prepared = exchange(
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
            "visibleDraft": DRAFT,
            "selection": {"kind": "current"},
        },
    )
    assert prepared["ok"], prepared
    ready = prepared["result"]
    executed = exchange(
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
    assert executed["ok"], executed
    drain_owned_changesets(actor)
    terminal = exchange(
        actor, "job.get", {"projectId": project, "jobId": executed["result"]["jobId"]}
    )
    assert terminal["ok"] and terminal["result"]["state"] == "succeeded", terminal
    described = exchange(
        actor,
        "query.result.describe",
        {
            "projectId": project,
            "resultId": terminal["result"]["resultRef"]["resultId"],
        },
    )
    assert described["ok"], described
    assert described["result"]["query"] == {
        "kind": "SELECT",
        "columns": [{"index": i, "name": c} for i, c in enumerate("abcde")],
        "rowCount": 243,
    }
    return project, described["result"]["identity"]


def ledger(reply):
    return {"bytes": reply.scalar, "objects": reply.objects, "work": reply.work}


def observe(monkeypatch, host, store, events):
    reserve = host.reserve
    final = store._read_admission.check_final_material

    def allocation(reply, scalar, objects, work):
        item = {
            "stage": "reserve",
            "before": ledger(reply),
            "fee": {
                "bytes": scalar,
                "objects": objects,
                "work": work,
            },
            "stack": [f.name for f in traceback.extract_stack(limit=6)],
        }
        events.append(item)
        try:
            return reserve(reply, scalar, objects, work)
        except BaseException as error:
            item["error"] = {
                "type": type(error).__name__,
                "code": getattr(error, "code", None),
                "params": getattr(error, "params", None),
            }
            raise
        finally:
            item["after"] = ledger(reply)

    def boundary(token):
        item = {
            "stage": "before_commit_final_material",
            "before": ledger(token.reply),
            "controlled": token.controlled,
            "inTransaction": store._db.in_transaction,
            "deliveredRows": [
                len(v["rows"]) for v in token.reply.values if isinstance(v, dict) and "rows" in v
            ],
            "stack": [
                {"file": f.filename, "line": f.lineno, "name": f.name}
                for f in traceback.extract_stack(limit=6)
            ],
        }
        events.append(item)
        try:
            return final(token)
        except BaseException as error:
            item["error"] = {
                "type": type(error).__name__,
                "code": getattr(error, "code", None),
                "params": getattr(error, "params", None),
            }
            raise
        finally:
            item["after"] = ledger(token.reply)

    monkeypatch.setattr(host, "reserve", allocation)
    monkeypatch.setattr(store._read_admission, "check_final_material", boundary)


def test_real_owner_243_rows_five_columns_fit_final_material_and_continue(
    named_owned, monkeypatch, tmp_path
):
    actor, store, _ = named_owned
    assert rdflib.__version__ == "7.6.0+ontolearn.fr201.3"
    assert (HELD_BYTES, HELD_OBJECTS, READ_WORK) == (134217728, 1048576, 536870912)
    project, binding = saved_query(actor, store)
    host = actor.mainline
    identity = (host.owner_id, host.host, host.session, host.generation, host.selected)
    events, pages = [], []
    observe(monkeypatch, host, store, events)
    expected = list(
        product([f"urn:ontolearn:learning:equipment/{i:03}" for i in (1, 2, 3)], repeat=5)
    )
    all_rows, cursor = [], None
    try:
        for _ in range(243):
            request_ = frame(
                actor,
                "query.result.rowsPage",
                {"binding": binding, "pageSize": 200, "cursor": cursor},
            )
            response = actor.request(request_)
            pages.append({"request": request_, "response": response})
            actor.finish_query_reply(request_["id"], emitted=True)
            assert response["ok"], response
            page = response["result"]
            assert 0 < len(page["rows"]) <= 200 and page["identity"] == binding
            for row in page["rows"]:
                index = len(all_rows)
                assert row == {
                    "index": index,
                    "rowKey": digest([binding["resultId"], binding["payloadSha256"], index]),
                    "cells": [
                        {"kind": "iri", "iri": iri, "n3": f"<{iri}>"} for iri in expected[index]
                    ],
                }
                all_rows.append(row)
            cursor = page["nextCursor"]
            if cursor is None:
                break
        assert len(all_rows) == 243 and len(pages) > 1
        boundaries = [e for e in events if e["stage"] == "before_commit_final_material"]
        fees = [e for e in events if "begin_transaction" in e.get("stack", [])]
        assert len(boundaries) == len(fees) == len(pages)
        assert all(e["fee"] == {"bytes": 1114112, "objects": 8192, "work": 134217728} for e in fees)
        assert all(e["before"] == e["after"] and "error" not in e for e in boundaries)
        assert actor.mainline is host and identity == (
            host.owner_id,
            host.host,
            host.session,
            host.generation,
            host.selected,
        )
        assert not host.hold and host.replies == {} and store._read_admission.transaction is None
        assert exchange(
            actor, "project.read", {"projectId": project, "editor": "query-workspace-v1"}
        )["ok"]
    finally:
        result = {
            "logicalAccountingNotRSS": True,
            "rdflib": {"version": rdflib.__version__, "file": rdflib.__file__},
            "sourceMainline": str(
                Path(__import__("ontolearn_engine.project.mainline", fromlist=["x"]).__file__)
            ),
            "limits": {"bytes": HELD_BYTES, "objects": HELD_OBJECTS, "work": READ_WORK},
            "events": events,
            "pages": pages,
        }
        path = Path(os.environ.get("T01_ROWS_BUDGET_EVIDENCE", str(tmp_path / "rows-budget.json")))
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_final_fee_refusal_preserves_scope_and_same_host_continues(
    named_owned, monkeypatch, tmp_path
):
    actor, store, _ = named_owned
    project, binding = saved_query(actor, store)
    host, admission = actor.mainline, store._read_admission
    identity = (host.owner_id, host.host, host.session, host.generation, host.selected)
    # Private boundary diagnostic on the real installed issuer: perform two
    # complete authenticated Store preflights in one actual original reply.
    # Their original nonrefundable work leaves no room for the fixed final fee.
    # No counters, caps, owner classes or budgets are substituted.
    request_ = frame(
        actor, "query.result.rowsPage", {"binding": binding, "pageSize": 200, "cursor": None}
    )
    host.begin(request_)
    events = []
    observe(monkeypatch, host, store, events)
    try:
        with pytest.raises(JobFault) as caught:
            with query_read(actor, request_["method"], request_["params"]) as ticket:
                ticket.before_store(
                    store, "second real diagnostic preflight after issuer entry", request_["params"]
                )
                with store._transaction():
                    pytest.fail("No transaction body may run after failed prepayment")
        assert caught.value.code == "RESOURCE_LIMIT" and caught.value.params == {
            "resource": "memory"
        }
        host.observe_error(request_["id"], caught.value)
        failures = [e for e in events if "error" in e]
        assert len(failures) == 1 and "begin_transaction" in failures[0]["stack"]
        assert failures[0]["before"] == failures[0]["after"]  # Atomic refusal, no refund.
        assert (
            admission.transaction is None
            and admission.active is None
            and not admission.charged_reply
        )
        assert (
            set(host.replies) == {request_["id"]} and not host.hold and not store._db.in_transaction
        )
    finally:
        actor.finish_query_reply(request_["id"], emitted=True)
        (tmp_path / "prepay-refusal.json").write_text(
            json.dumps(events, indent=2) + "\n", encoding="utf-8"
        )
    continued = exchange(
        actor, "query.result.rowsPage", {"binding": binding, "pageSize": 200, "cursor": None}
    )
    assert continued["ok"] and len(continued["result"]["rows"]) > 0, continued
    assert actor.mainline is host and identity == (
        host.owner_id,
        host.host,
        host.session,
        host.generation,
        host.selected,
    )
    assert not host.hold and host.replies == {} and admission.transaction is None
    assert exchange(actor, "project.read", {"projectId": project, "editor": "query-workspace-v1"})[
        "ok"
    ]


@pytest.mark.parametrize("method", ["query.result.rowsPage", "query.result.textPage"])
@pytest.mark.parametrize("change", ["unknown", "replacement"])
def test_page_scope_cannot_lend_or_refund_prepaid_fee(named_owned, change, method):
    actor, store, _ = named_owned
    project, binding = saved_query(actor, store)
    host, admission = actor.mainline, store._read_admission
    params = {
        "binding": binding,
        "cursor": None,
        **({"pageSize": 200} if method.endswith("rowsPage") else {"maxUtf8Bytes": 32768}),
    }
    original, successor = frame(actor, method, params), frame(actor, method, params)
    host.begin(original)
    reply = host.current
    before = ledger(reply)

    def hook(phase):
        if phase == "before_commit":
            if change == "unknown":
                reply.unknown = True
            else:
                host.current = None
                host.begin(successor)

    with pytest.raises(JobFault) as denied:
        with store._transaction(hook):
            assert admission.transaction.reply is reply and admission.transaction.charged is reply
            prepaid = ledger(reply)
            assert prepaid == dict(
                zip(
                    ("bytes", "objects", "work"),
                    (
                        before["bytes"] + 1114112,
                        before["objects"] + 8192,
                        before["work"] + 134217728,
                    ),
                    strict=True,
                )
            )
    assert denied.value.code == "PERMISSION_DENIED"
    assert ledger(reply) == prepaid and admission.retained == [] and admission.active is None
    if change == "replacement":
        assert host.current.request_id == successor["id"] and ledger(host.current) == before
        actor.finish_query_reply(successor["id"], emitted=True)
    actor.finish_query_reply(original["id"], emitted=True)
    assert (original["id"] in host.replies) is (change == "unknown")


@pytest.mark.parametrize("method", ["query.result.rowsPage", "query.result.textPage"])
def test_page_prepaid_material_cannot_be_consumed_twice(named_owned, method):
    actor, store, _ = named_owned
    _, binding = saved_query(actor, store)
    host, admission = actor.mainline, store._read_admission
    params = {
        "binding": binding,
        "cursor": None,
        **({"pageSize": 200} if method.endswith("rowsPage") else {"maxUtf8Bytes": 32768}),
    }
    request_ = frame(actor, method, params)
    host.begin(request_)
    with pytest.raises(JobFault) as denied:
        with store._transaction():
            token = admission.transaction
            prepaid = ledger(host.current)
            admission.check_final_material(token)
            assert ledger(host.current) == prepaid
            # The original before_commit boundary must refuse a second use.
    assert denied.value.code == "INVALID_STATE" and ledger(host.current) == prepaid
    actor.finish_query_reply(request_["id"], emitted=True)
    assert not host.hold and host.replies == {} and admission.transaction is None
