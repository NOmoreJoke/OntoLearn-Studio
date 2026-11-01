"""Authenticated query-only presentation; no SPARQL executor or evidence-leaf replay."""

import hashlib
import json

from ontolearn_engine.job_store import fault
from ontolearn_engine.project.query_definitions import scalar
from ontolearn_engine.storage import digest

POLICY = "query-presentation-scalars-v1"


def _valid(store, schema, value):
    if not store.contract.validate(schema, value):
        fault("INVALID_STATE")


def _material(store, project, result, ticket):
    ticket.check(store)
    metadata, payload = store.semantic_result(project, result)
    context = store.job_context(metadata["jobId"])
    record = next(
        (
            r
            for r in context["snapshot"]["state"]["definitions"]
            if r["layer"] == "query" and r["id"] == metadata["definitionId"]
        ),
        None,
    )
    if record is None:
        fault("INVALID_STATE")
    ticket.pay(
        "presentation identity",
        bytes_=4096 + 32 * len(record["payload"]),
        objects=256 + 8 * len(record["payload"]),
        work=1024 + 8 * len(record["payload"]),
    )
    text, query = payload["queryText"], payload["query"]
    ticket.pay(
        "presentation shape", bytes_=8192 + 16 * len(text), objects=512, work=1024 + 8 * len(text)
    )
    if not scalar(text):
        fault("INVALID_STATE")
    if len(text) > 65536:
        fault("UNSUPPORTED_CAPABILITY")
    if type(query) is not dict:
        fault("INVALID_STATE")
    if query.get("type") == "ASK":
        if set(query) != {"type", "value"} or type(query["value"]) is not bool:
            fault("INVALID_STATE")
        header = {"kind": "ASK", "value": query["value"]}
    elif query.get("type") == "SELECT":
        if (
            set(query) != {"type", "variables", "rows"}
            or type(query["variables"]) is not list
            or type(query["rows"]) is not list
        ):
            fault("INVALID_STATE")
        names, rows = query["variables"], query["rows"]
        ticket.pay(
            "columns and widths",
            bytes_=4096 + 1024 * len(names),
            objects=128 + 16 * len(names),
            work=128 + 4 * len(names) + 4 * len(rows),
        )
        columns, seen = [], set()
        for i, name in enumerate(names):
            if not scalar(name):
                fault("INVALID_STATE")
            if len(name) > 128:
                fault("UNSUPPORTED_CAPABILITY")
            if name in seen:
                fault("INVALID_STATE")
            seen.add(name)
            columns.append({"index": i, "name": name})
        for row in rows:
            if (
                type(row) is not list
                or len(row) != len(names)
                or any(cell is not None and not scalar(cell) for cell in row)
            ):
                fault("INVALID_STATE")
        header = {"kind": "SELECT", "columns": columns, "rowCount": len(rows)}
    else:
        fault("INVALID_STATE")
    identity = {
        "projectId": project,
        "resultId": result,
        "jobId": metadata["jobId"],
        "inputSnapshotId": metadata["inputSnapshotId"],
        "inputProjectRevision": payload["inputProjectRevision"],
        "scope": metadata["scope"],
        "definitionId": metadata["definitionId"],
        "parametersHash": metadata["parametersHash"],
        "implementation": metadata["implementation"],
        "payloadSha256": digest(payload),
        "definitionSha256": digest(json.loads(record["payload"])),
        "inputSelection": payload["inputSelection"],
        "projectionVersion": 1,
        "lengthPolicyId": POLICY,
    }
    _valid(store, "query.consumer.identity", identity)
    encoded = text.encode("utf-8")
    executed = {
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "utf8Bytes": len(encoded),
        "unicodeScalars": len(text),
        "utf16Units": sum(2 if ord(c) > 0xFFFF else 1 for c in text),
    }
    return (
        {"identity": identity, "metadata": metadata, "executedText": executed, "query": header},
        query,
        text,
        encoded,
    )


def _room(store, value, limits, ticket):
    # Worst JSON escaping is <=6 bytes per scalar; the scope already holds inputs.
    ticket.pay(
        "page encode",
        bytes_=4 * limits["maxPageBytes"] + 4096,
        objects=256,
        work=8 * limits["maxPageBytes"] + 4096,
    )
    size = store.contract.encoded_size(value)
    if size > min(131072, limits["maxPageBytes"]):
        fault("RESOURCE_LIMIT", resource="page")
    if size + 1024 > min(262144, limits["maxFrameBytes"]):
        fault("RESOURCE_LIMIT", resource="frame")


def describe(store, params, limits, ticket):
    ticket.check(store)
    store._valid("params_query.result.describe", params)
    with store._read():
        result, _, _, _ = _material(store, params["projectId"], params["resultId"], ticket)
        _room(store, result, limits, ticket)
        _valid(store, "result_query.result.describe", result)
        return ticket.deliver(result)


def cursor_position(store, token, kind, binding, size, maximum):
    key = "nextIndex" if kind == "query-rows-v1" else "nextUtf8Byte"
    if token is None:
        return 0
    position = store._cursor(token, kind, binding, size)
    if (
        type(position) is not dict
        or set(position) != {key}
        or type(position[key]) is not int
        or not 0 <= position[key] <= maximum
    ):
        fault("INVALID_STATE")
    return position[key]


def _bound(store, params, ticket):
    binding = params["binding"]
    descriptor, query, text, encoded = _material(
        store, binding["projectId"], binding["resultId"], ticket
    )
    if descriptor["identity"] != binding:
        fault("IDENTITY_CONFLICT")
    return descriptor, query, text, encoded


def text_page(store, params, limits, ticket):
    ticket.check(store)
    store._valid("params_query.result.textPage", params)
    with store._transaction():
        descriptor, _, _, encoded = _bound(store, params, ticket)
        binding, size = params["binding"], params["maxUtf8Bytes"]
        start = cursor_position(
            store, params["cursor"], "query-text-v1", binding, size, len(encoded)
        )
        if start < len(encoded) and encoded[start] & 0xC0 == 0x80:
            fault("INVALID_STATE")
        # Candidate encoders may exhaust the original book. Reserve the same
        # final encoder once before that search, then consume only this local
        # prepayment; no fee is refunded or borrowed from another reply.
        final_fees = (
            4 * limits["maxPageBytes"] + 4096,
            256,
            8 * limits["maxPageBytes"] + 4096,
        )
        ticket.pay(
            "text final prepaid", bytes_=final_fees[0], objects=final_fees[1], work=final_fees[2]
        )
        ticket.check(store)
        final = _RowsPrepaid(store, ticket, final_fees)
        maximum = min(len(encoded), start + size)
        ticket.pay(
            "text bounded search",
            bytes_=16 * (maximum - start) + 8192,
            objects=512,
            work=32 * (maximum - start) + 8192,
        )
        low, high, chosen = start, maximum, None
        # <=16 candidates for <=32768 bytes, no cursor allocation during search.
        for _ in range(16):
            if low > high:
                break
            stop = (low + high) // 2
            while stop > start and stop < len(encoded) and encoded[stop] & 0xC0 == 0x80:
                stop -= 1
            candidate = {
                "identity": binding,
                "kind": "text",
                "order": "utf8-byte:asc",
                "startUtf8Byte": start,
                "utf8Length": stop - start,
                "text": encoded[start:stop].decode("utf-8"),
                "nextCursor": "00000000-0000-4000-8000-000000000001"
                if stop < len(encoded)
                else None,
            }
            try:
                _room(store, candidate, limits, ticket)
            except Exception as error:
                from ontolearn_engine.job_store import JobFault

                if not isinstance(error, JobFault) or error.code != "RESOURCE_LIMIT":
                    raise
                high = stop - 1
            else:
                chosen = candidate
                if stop == maximum:
                    break
                low = max(low + 1, (low + high) // 2 + 1)
        if chosen is None or (chosen["utf8Length"] == 0 and start < len(encoded)):
            fault("RESOURCE_LIMIT", resource="page")
        result = chosen
        stop = start + result["utf8Length"]
        if stop < len(encoded):
            result["nextCursor"] = store._new_cursor(
                "query-text-v1", binding, size, {"nextUtf8Byte": stop}
            )
        # Preserve the original budget's current-reply/unknown/generation check
        # immediately before encoding, without charging this encoder twice.
        ticket.pay("text final binding recheck")
        _room(store, result, limits, final)
        final.complete()
        _valid(store, "result_query.result.textPage", result)
        return ticket.deliver(result)


def typed_cell(raw, ticket):
    if raw is None:
        return None
    if not scalar(raw):
        fault("INVALID_STATE")
    # Reject an impossible empty-page cell before building an RDF graph.
    ticket.pay(
        "N3 projection",
        bytes_=4096 + 128 * len(raw),
        objects=1024 + 32 * len(raw),
        work=1024 + 64 * len(raw),
    )
    from rdflib import Graph, Literal, URIRef
    from rdflib.plugins.parsers.notation3 import SinkParser

    from ontolearn_engine.semantic_turtle import LexicalSink

    graph = Graph()
    first = None
    try:
        SinkParser(
            LexicalSink(graph, canonical_strings=False), baseURI="urn:ontolearn:term:", turtle=True
        ).loadBuf("<urn:ontolearn:subject> <urn:ontolearn:predicate> " + raw + " .")
        if len(graph) != 1:
            fault("INVALID_STATE")
        s, p, value = next(iter(graph))
        if (
            s != URIRef("urn:ontolearn:subject")
            or p != URIRef("urn:ontolearn:predicate")
            or not isinstance(value, URIRef | Literal)
            or value.n3() != raw
        ):
            fault("INVALID_STATE")
        if isinstance(value, URIRef):
            return {"kind": "iri", "iri": str(value), "n3": raw}
        literal_type = (
            {"kind": "language", "tag": value.language}
            if value.language
            else {"kind": "datatype", "iri": str(value.datatype)}
            if value.datatype
            else {"kind": "plain"}
        )
        return {"kind": "literal", "lexical": str(value), "literalType": literal_type, "n3": raw}
    except BaseException as error:
        first = error
        from ontolearn_engine.job_store import JobFault

        if isinstance(error, JobFault) or not isinstance(error, Exception):
            raise
        fault("INVALID_STATE")
    finally:
        try:
            graph.close()
        except BaseException:
            if first is None:
                raise
            # The actual issuer retains failed aliases; preserve the original cause.
            pass


class _RowsPrepaid:
    """Local consumption of one successful original pay; never an authority/credit issuer.

    Instances are created only immediately after that original pay and its
    binding check. Exceptions leave all successful original fees held by its book.
    """

    __slots__ = ("_store", "_ticket", "_remaining")

    def __init__(self, store, ticket, fees):
        self._store, self._ticket = store, ticket
        self._remaining = list(fees)

    def check(self, store):
        if store is not self._store:
            fault("PERMISSION_DENIED")
        self._ticket.check(store)

    def pay(self, stage, *, bytes_=0, objects=0, work=0):
        self.check(self._store)
        amounts = (bytes_, objects, work)
        if (
            type(stage) is not str
            or len(stage) > 128
            or any(type(n) is not int or n < 0 for n in amounts)
            or any(n > left for n, left in zip(amounts, self._remaining, strict=True))
        ):
            fault("INVALID_STATE")
        for i, amount in enumerate(amounts):
            self._remaining[i] -= amount
        self.check(self._store)

    def complete(self):
        self.check(self._store)
        if any(self._remaining):
            fault("INVALID_STATE")


def _rows_final_overhead(limits):
    # Complete final schema traversal, fixed cursor/binding temporaries and alias
    # delivery, in addition to the unchanged _room encoder fee. The validator
    # traverses the already prepaid typed values, rather than cloning their cells;
    # allow fixed cursor/iterator temporaries plus eight references per page item.
    # Original reserve_store covers native Store reads. This is held logical credit,
    # not measured physical memory and not a new limit or a refund.
    maximum = limits["maxPageBytes"]
    return 16 * maximum + 65536, 4096 + 8 * limits["maxPageItems"], 64 * maximum + 65536


def _rows_candidate_cost(raw, lower, nonnull, limits, *, bound_only=False):
    # Only len()/bounded scans of _material's authenticated exact lists/strings
    # precede admission. No Graph, typed cell or per-cell fee table is allocated.
    if bound_only:
        return 0, 0, 128 + len(raw)
    return (
        8192 + 64 * lower + 4096 * nonnull + 128 * lower + 4 * limits["maxPageBytes"] + 4096,
        256 + 32 * len(raw) + 1024 * nonnull + 32 * lower + 256,
        128
        + len(raw)
        + 1024
        + 16 * lower
        + 1024 * nonnull
        + 64 * lower
        + 8 * limits["maxPageBytes"]
        + 4096,
    )


def rows_page(store, params, limits, ticket):
    from ontolearn_engine.job_store import JobFault

    ticket.check(store)
    store._valid("params_query.result.rowsPage", params)
    if params["pageSize"] > min(200, limits["maxPageItems"]):
        fault("INVALID_REQUEST", field="params")
    with store._transaction():
        descriptor, query, _, _ = _bound(store, params, ticket)
        if descriptor["query"]["kind"] != "SELECT":
            fault("INVALID_STATE")
        binding, size, rows = params["binding"], params["pageSize"], query["rows"]
        overhead = _rows_final_overhead(limits)
        final_fees = (
            overhead[0] + 4 * limits["maxPageBytes"] + 4096,
            overhead[1] + 256,
            overhead[2] + 8 * limits["maxPageBytes"] + 4096,
        )
        ticket.pay(
            "rows final prepaid", bytes_=final_fees[0], objects=final_fees[1], work=final_fees[2]
        )
        ticket.check(store)
        final = _RowsPrepaid(store, ticket, final_fees)
        final.pay(
            "rows cursor validation delivery",
            bytes_=overhead[0],
            objects=overhead[1],
            work=overhead[2],
        )
        start = cursor_position(store, params["cursor"], "query-rows-v1", binding, size, len(rows))
        final.check(store)
        result = {
            "identity": binding,
            "kind": "rows",
            "order": "query-index:asc",
            "rows": [],
            "nextCursor": None,
        }
        stop = start
        for index in range(start, min(start + size, len(rows))):
            ticket.check(store)
            raw = rows[index]
            if any(cell is not None and type(cell) is not str for cell in raw):
                fault("INVALID_STATE")
            lower = sum(0 if cell is None else len(cell) for cell in raw)
            nonnull = sum(cell is not None for cell in raw)
            bound_only = lower > min(131072, limits["maxPageBytes"])
            fees = _rows_candidate_cost(raw, lower, nonnull, limits, bound_only=bound_only)
            # Catch only original atomic capacity admission, before candidate/Graph
            # allocation. Failed pay has no mutation; successful fees never refund.
            try:
                ticket.pay(
                    "rows candidate admission", bytes_=fees[0], objects=fees[1], work=fees[2]
                )
            except JobFault as error:
                if error.code != "RESOURCE_LIMIT" or error.params != {"resource": "memory"}:
                    raise
                ticket.check(store)  # QueryRead.pay's post-check did not run.
                if not result["rows"]:
                    raise
                break
            ticket.check(store)
            prepaid = _RowsPrepaid(store, ticket, fees)
            prepaid.pay("row bound", work=128 + len(raw))
            if bound_only:
                prepaid.complete()
                if not result["rows"]:
                    fault("RESOURCE_LIMIT", resource="page")
                break
            prepaid.pay(
                "typed row",
                bytes_=8192 + 64 * lower,
                objects=256 + 32 * len(raw),
                work=1024 + 16 * lower,
            )
            cells = []
            for cell in raw:
                prepaid.check(store)
                value = typed_cell(cell, prepaid)
                prepaid.check(store)  # Includes the actual Graph.close callback.
                cells.append(value)
            projected = {
                "index": index,
                "rowKey": digest([binding["resultId"], binding["payloadSha256"], index]),
                "cells": cells,
            }
            prepaid.check(store)
            result["rows"].append(projected)
            try:
                _room(
                    store,
                    result | {"nextCursor": "00000000-0000-4000-8000-000000000001"},
                    limits,
                    prepaid,
                )
                prepaid.complete()
            except JobFault as error:
                if error.code != "RESOURCE_LIMIT" or error.params not in (
                    {"resource": "page"},
                    {"resource": "frame"},
                ):
                    raise
                prepaid.complete()
                result["rows"].pop()
                if not result["rows"]:
                    raise
                break
            stop = index + 1
        final.check(store)
        if stop < len(rows):
            result["nextCursor"] = store._new_cursor(
                "query-rows-v1", binding, size, {"nextIndex": stop}
            )
            final.check(store)
        _room(store, result, limits, final)
        final.complete()
        _valid(store, "result_query.result.rowsPage", result)
        ticket.check(store)
        value = ticket.deliver(result)
        ticket.check(store)
        return value
