"""Bounded facts from an owner's existing JobStore3, never dispatch authority.

There is no path, Store constructor, permission/binding factory, public service,
replay, or persistent intention cache here. All original validators see the same
read snapshot through a fixed, metered SQL gate.
"""

import json
import math
import re
import sqlite3
from types import SimpleNamespace

from ontolearn_engine import job_store, storage
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.project import domain_changesets, format3, project_lifecycle
from ontolearn_engine.project.applications import uuid_ref
from ontolearn_engine.project.project_host import HostReadFault, ProjectHostReader, ReadLimits
from ontolearn_engine.project.transactions import ProjectTransactions
from ontolearn_engine.storage import Store, canonical, digest

MAX_PROBE_WORK = 536870912
MAX_QUERY_COUNT = 65536
MAX_READ_WORK = 536870912
MAX_SAFE = 9007199254740991
_SHORT = {8, 9, 10, 12, 13}


class EvidenceFault(Exception):
    """Safe private control, deliberately outside the old ValueError wrappers."""

    def __init__(self, reason, *, cleanup_failed=False):
        if reason not in {
            "invalid-input",
            "state",
            "identity-conflict",
            "resource-limit",
            "unsupported-profile",
            "storage-busy",
            "storage-failure",
        }:
            raise ValueError("Invalid evidence reason")
        super().__init__(reason)
        self.reason = reason
        self.cleanup_failed = cleanup_failed


def _require(condition):
    if not condition:
        raise ValueError("Incomplete operation evidence")


def _limit(condition):
    if not condition:
        raise EvidenceFault("resource-limit")


def _positive(value, ceiling):
    if type(value) is not int or not 1 <= value <= ceiling:
        raise EvidenceFault("invalid-input")
    return value


def _string_cost(value):
    size = 2
    for c in value:
        n = ord(c)
        if n == 0 or 0xD800 <= n <= 0xDFFF:
            raise ValueError("Invalid Unicode scalar")
        size += (
            (2 if n in _SHORT or n in (34, 92) else 6)
            if n < 32 or n in (34, 92)
            else (1 if n < 128 else 2 if n < 2048 else 3 if n < 65536 else 4)
        )
    return size


def _measure(value, maximum, *, safe_int=True, max_depth=32, allow_float=False):
    """Count before encoding any scalar; iterencode's large chunks are unsafe."""
    stack, total, nodes = [(value, 0)], 0, 0
    while stack:
        item, depth = stack.pop()
        nodes += 1
        _limit(nodes <= maximum and depth <= max_depth)
        if type(item) is dict:
            _limit(len(item) <= maximum)
            total += 2 + max(0, len(item) - 1) + len(item)
            for key, child in item.items():
                if type(key) is not str:
                    raise ValueError("Invalid JSON key")
                stack.extend(((key, depth + 1), (child, depth + 1)))
        elif type(item) is list:
            _limit(len(item) <= maximum)
            total += 2 + max(0, len(item) - 1)
            stack.extend((v, depth + 1) for v in item)
        elif type(item) is str:
            _limit(len(item) <= maximum - total)
            # Stop on the first excess, before building an escaped string.
            total += 2
            for c in item:
                n = ord(c)
                if n == 0 or 0xD800 <= n <= 0xDFFF:
                    raise ValueError("Invalid Unicode scalar")
                total += (
                    (2 if n in _SHORT or n in (34, 92) else 6)
                    if n < 32 or n in (34, 92)
                    else (1 if n < 128 else 2 if n < 2048 else 3 if n < 65536 else 4)
                )
                _limit(total <= maximum)
        elif item is None:
            total += 4
        elif type(item) is bool:
            total += 4 if item else 5
        elif type(item) is int:
            if (
                not -(MAX_SAFE if safe_int else 2**63)
                <= item
                <= (MAX_SAFE if safe_int else 2**63 - 1)
            ):
                raise ValueError("Invalid integer")
            total += len(str(item))
        elif allow_float and type(item) is float:
            if not math.isfinite(item) or abs(item) > MAX_SAFE:
                raise ValueError("Invalid JSON number")
            # A binary64 scalar has a constant-size JSON representation. This
            # path is only for row-contract-validated result cells, never SQL
            # typed rows or selectors.
            total += len(canonical(item))
        else:
            raise ValueError("Invalid JSON scalar")
        _limit(total <= maximum)
    return total


def _sqlite_error(exc):
    code = getattr(exc, "sqlite_errorcode", None)
    return EvidenceFault(
        "storage-busy"
        if type(code) is int and code & 255 in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED)
        else "storage-failure"
    )


class _Cursor:
    def close(self):
        try:
            self._cursor.close()
        except sqlite3.Error as exc:
            raise _sqlite_error(exc) from None

    def __init__(self, cursor):
        self._cursor = cursor

    def fetchone(self):
        try:
            return self._cursor.fetchone()
        except sqlite3.Error as exc:
            raise _sqlite_error(exc) from None

    def fetchall(self):
        try:
            return self._cursor.fetchall()
        except sqlite3.Error as exc:
            raise _sqlite_error(exc) from None

    def fetchmany(self, size=1):
        try:
            return self._cursor.fetchmany(size)
        except sqlite3.Error as exc:
            raise _sqlite_error(exc) from None

    def __iter__(self):
        return self

    def __next__(self):
        row = self.fetchone()
        if row is None:
            raise StopIteration
        return row


def _normal(sql):
    return " ".join(sql.split())


def _quote(value):
    return '"' + value.replace('"', '""') + '"'


_TABLES = (
    {
        re.search(r"CREATE TABLE(?: IF NOT EXISTS)? (\w+)", sql)[1]
        for sql in storage.SCHEMA + job_store.JOB3_SCHEMA + job_store.JOB3_CATALOG
        if sql.startswith("CREATE TABLE")
    }
    | {name for name, _ in format3.TABLES}
    | {
        "mapping_state",
        "commit_evidence",
        "migration_log",
        "sqlite_master",
    }
)


class _CacheCursor:
    def __init__(self, rows):
        self.rows, self.offset = rows, 0

    def fetchone(self):
        if self.offset == len(self.rows):
            return None
        row = self.rows[self.offset]
        self.offset += 1
        return row

    def fetchall(self):
        rows = list(self.rows[self.offset :])
        self.offset = len(self.rows)
        return rows

    def fetchmany(self, size=1):
        rows = list(self.rows[self.offset : self.offset + size])
        self.offset += len(rows)
        return rows

    def __iter__(self):
        return self

    def __next__(self):
        row = self.fetchone()
        if row is None:
            raise StopIteration
        return row


class _RememberCursor:
    def __init__(self, cursor, cache, key, maximum):
        self.cursor, self.cache, self.key = cursor, cache, key
        self.maximum, self.rows = maximum, []

    def _save(self, rows, ended=False):
        self.rows.extend(rows)
        _limit(len(self.rows) <= self.maximum)
        if ended or len(self.rows) == self.maximum:
            self.cache[self.key] = tuple(self.rows)

    def fetchone(self):
        row = self.cursor.fetchone()
        self._save([] if row is None else [row], row is None)
        return row

    def fetchall(self):
        rows = self.cursor.fetchall()
        self._save(rows, True)
        return rows

    def fetchmany(self, size=1):
        rows = self.cursor.fetchmany(size)
        self._save(rows, len(rows) < size)
        return rows

    def __iter__(self):
        return self

    def __next__(self):
        row = self.fetchone()
        if row is None:
            raise StopIteration
        return row


# These are conservative control-work tickets, not RSS/timing measurements.
# SQLite3.50.4 OP_Column bounds a physical record header at98307 and local
# payload at65536. Grouped native metadata visits the highest column first,
# so a corrupt long physical header is fetched at most once per row.
_SQLITE_SOURCE = (
    "2025-07-30 19:33:53 4d8adfb30e03f9cf27f800a2c1ba3c48fb4ca1b08b0f5ed59a4d5ecbf45e20a3"
)
_HEADER_WORK = 98307
_LOCAL_WORK = 65536
_STATEMENT_WORK = 4096


class _MeteredGate:
    def __init__(self, connection, maximum, limits):
        self.connection, self.maximum, self.limits = connection, maximum, limits
        self.evidence = self.probe = self.read_work = self.queries = 0
        self.seen, self.columns, self.column_kinds = {}, {}, {}
        self.guard_phase, self.encoding = False, None
        self.native, self.table_rows, self.table_info = {}, {}, {}
        self.schema_rows, self.schema_size = None, 0
        self.locator_cache, self.result_cache, self.plans = {}, {}, set()
        self.profile_ready = False
        self.verified_rows = {}
        self.highest = {}
        self.probe_peak = 0
        self.page_size = None
        self.schema_names, self.schema_tables, self.table_sizes = {}, (), {}

    @property
    def in_transaction(self):
        return self.connection.in_transaction

    def _audit(self, event, **facts):
        """No retained diagnostics. Tests may observe this private no-op seam."""

    def _raw(
        self,
        sql,
        params=(),
        *,
        numeric_columns=1,
        rows=1,
        body_cost=None,
        control_work=0,
        cached=None,
    ):
        _limit(self.queries < MAX_QUERY_COUNT - 2)
        work = 128 + (128 * numeric_columns * rows if body_cost is None else body_cost)
        if cached is None:
            control_work += 65536 + 32 * len(sql) + 128 * len(params)
        work += control_work
        _limit(self.read_work + work <= MAX_READ_WORK)
        self.queries += 1
        self.read_work += work
        self._audit(
            "query",
            sql=sql,
            query=self.queries,
            readWork=self.read_work,
            reservedWork=work,
            numericColumns=numeric_columns,
            rows=rows,
            bodyCost=body_cost,
            controlWork=control_work,
            provider="sqlite" if cached is None else "snapshot-cache",
        )
        if cached is not None:
            return _CacheCursor(cached)
        try:
            return _Cursor(self.connection.execute(sql, params))
        except sqlite3.Error as exc:
            raise _sqlite_error(exc) from None

    def _profile(self):
        if self.profile_ready:
            return
        actual = self._raw(
            "SELECT sqlite_version(),sqlite_source_id()",
            numeric_columns=2,
            control_work=_STATEMENT_WORK,
        ).fetchone()
        if tuple(actual) != ("3.50.4", _SQLITE_SOURCE):
            raise EvidenceFault("unsupported-profile")
        page = self._raw("PRAGMA page_size", control_work=_STATEMENT_WORK).fetchone()[0]
        if type(page) is not int or page < 512 or page > 65536 or page & (page - 1):
            raise EvidenceFault("unsupported-profile")
        self.page_size = page
        self.profile_ready = True
        self._audit("sqlite-profile", version=actual[0], sourceId=actual[1])

    def _columns(self, table):
        if table not in _TABLES:
            raise EvidenceFault("unsupported-profile")
        if table == "sqlite_master" and table not in self.columns:
            self.columns[table] = ("type", "name", "tbl_name", "rootpage", "sql")
            self.column_kinds[table] = {
                c: ({"integer", "null"} if c == "rootpage" else {"text", "null"})
                for c in self.columns[table]
            }
        if table not in self.columns:
            self._schema()
            fee = self._schema_fee(table)
            info = self._raw(
                "SELECT * FROM pragma_table_xinfo(?) LIMIT 33",
                (table,),
                body_cost=fee + 128 * 6 * 33,
                control_work=_STATEMENT_WORK,
            ).fetchall()
            _limit(0 < len(info) <= 32)
            kinds = {}
            for row in info:
                _require(row[6] == 0 and row[1] != "_t01_rowkey")
                kind = {"TEXT": "text", "INTEGER": "integer", "INT": "integer"}.get(row[2].upper())
                if kind is None:
                    raise EvidenceFault("unsupported-profile")
                kinds[row[1]] = {kind} if row[3] else {kind, "null"}
            self.columns[table] = tuple(r[1] for r in info)
            self.column_kinds[table], self.table_info[table] = (
                kinds,
                tuple(tuple(r[:6]) for r in info),
            )
        return self.columns[table]

    def _schema_fee(self, table):
        self._schema()
        self._raw("schema fee lookup", body_cost=128 + self._parameter_work((table,)), cached=((),))
        rows = self.schema_names.get(table, ())
        _require(len(rows) == 1 and rows[0]["type"] == "table")
        return self.seen[("sqlite_master", rows[0]["rowid"])]

    def _rowids(self, table, maximum):
        self._profile()
        # No WHERE or keyset can skip malformed duplicate rowids. LIMIT counts
        # every emitted physical entry. Empty children/depth are rejected by
        # moveToRoot/moveToChild; First/Next each traverse at most40 pages.
        sql = f"SELECT rowid FROM {_quote(table)} NOT INDEXED LIMIT ?"
        cursor = self._raw(
            sql, (maximum + 1,), rows=1, control_work=_STATEMENT_WORK + 40 * self.page_size
        )
        result = []
        first = None
        try:
            while True:
                # CPython constructs this numeric row and steps to the next one
                # before returning it. The current row was paid by the prior step;
                # reserve this next step (including DONE/error) before fetchone.
                self._raw(
                    "rowid cursor advance reservation",
                    rows=1,
                    control_work=40 * self.page_size,
                    cached=((),),
                )
                row = cursor.fetchone()
                if row is None:
                    return tuple(result)
                rowid = row[0]
                _require(type(rowid) is int and (not result or result[-1] < rowid))
                result.append(rowid)
                _limit(len(result) <= maximum)
        except BaseException as exc:
            first = exc
            raise
        finally:
            try:
                cursor.close()
            except EvidenceFault:
                if first is None:
                    raise
                first.cleanup_failed = True

    def _native(self, table, rowid):
        columns = self._columns(table)
        key = (table, rowid)
        if key in self.native:
            self._raw("cached native row metadata", numeric_columns=2 * len(columns), cached=((),))
            return self.native[key]
        self._profile()
        ordered = tuple(reversed(columns))
        expressions = ",".join(f"typeof({_quote(c)}),octet_length({_quote(c)})" for c in ordered)
        sql = f"SELECT {expressions} FROM {_quote(table)} NOT INDEXED WHERE rowid=?"
        if sql not in self.plans:
            plan = self._raw(
                "EXPLAIN " + sql,
                (rowid,),
                rows=256,
                numeric_columns=8,
                control_work=_STATEMENT_WORK,
            ).fetchall()
            access = [r for r in plan if r[1] == "Column"]
            if (
                (access and access[0][3] != max(r[3] for r in access))
                or any(r[6] not in (128, 192) for r in access)
                or any(r[1] in {"IdxRowid", "SorterOpen", "OpenEphemeral"} for r in plan)
            ):
                raise EvidenceFault("unsupported-profile")
            self.highest[table] = access[0][3] if access else None
            self.plans.add(sql)
            self._audit(
                "native-plan",
                table=table,
                columnP5=[r[6] for r in access],
                firstColumn=access[0][3] if access else None,
            )
        row = self._raw(
            sql,
            (rowid,),
            numeric_columns=2 * len(columns),
            control_work=_STATEMENT_WORK + _HEADER_WORK + 22 * self.page_size,
        ).fetchone()
        _require(row is not None)
        info = {}
        for i, column in enumerate(ordered):
            kind, u = row[2 * i : 2 * i + 2]
            _require(kind in self.column_kinds[table][column])
            _require(u is None if kind == "null" else type(u) is int and u >= 0)
            if kind == "text" and self.encoding != "UTF-8":
                _require(u % 2 == 0)
            info[column] = (kind, u)
        self.native[key] = info
        self._audit(
            "native-metadata",
            table=table,
            rowid=rowid,
            fields={c: {"kind": v[0], "nativeBytes": v[1]} for c, v in info.items()},
        )
        return info

    def _schema(self):
        if self.schema_rows is not None:
            return
        rowids = self._rowids("sqlite_master", 256)
        self.table_rows["sqlite_master"] = rowids
        size = 0
        for rowid in rowids:
            meta = self._native("sqlite_master", rowid)
            size += meta["sql"][1] or 0
            _limit(size <= self.limits.schema_bytes)
        # All DDL bytes bounded before any schema body is read/parsed by gate.
        self.schema_size = size
        rows = []
        for rowid in rowids:
            self._cost("sqlite_master", rowid)
            source = self.verified_rows[("sqlite_master", rowid)]
            self._raw(
                "cached schema complete row",
                body_cost=self.seen[("sqlite_master", rowid)],
                cached=((),),
            )
            rows.append({"rowid": rowid, **dict(source)})
        self.schema_rows = tuple(rows)
        names, tables = {}, []
        for row in rows:
            self._raw(
                "schema index construction",
                body_cost=self.seen[("sqlite_master", row["rowid"])],
                cached=((),),
            )
            names.setdefault(row["name"], []).append(row)
            if row["type"] == "table":
                tables.append(row)
        self.schema_names = {name: tuple(items) for name, items in names.items()}
        self.schema_tables = tuple(tables)

    def _table_metadata(self, table):
        if table not in self.table_rows:
            rows = self._rowids(table, self.limits.validation_rows)
            size = 0
            for rowid in rows:
                meta = self._native(table, rowid)
                size += sum(u or 0 for _, u in meta.values())
            self.table_sizes[table] = size
            self.table_rows[table] = rows
        return self.table_rows[table]

    def _probe_bound(self, info):
        unit = 1 if self.encoding == "UTF-8" else 2
        return 128 + sum(
            256 + (160 * (u + 1) if unit == 1 else 16 * (u // 2 + 1) ** 2) if kind == "text" else 64
            for kind, u in info.values()
        )

    def _cost(self, table, rowid):
        key = (table, rowid)
        if key in self.seen:
            return self.seen[key]
        columns = self._columns(table)
        info = self._native(table, rowid)
        bound = self._probe_bound(info)
        _limit(self.probe + bound <= MAX_PROBE_WORK)
        # Conservative hold is charged BEFORE length/NUL/transcoding. On any
        # interruption it remains consumed; only a completed scan can settle.
        self.probe += bound
        self.probe_peak = max(self.probe_peak, self.probe)
        self._audit("probe-held", table=table, rowid=rowid, work=bound, total=self.probe)
        text = [c for c in columns if info[c][0] == "text"]
        lengths = {}
        if text:
            sql = "SELECT " + ",".join(
                f"length({_quote(c)}),instr({_quote(c)},char(0))" for c in text
            )
            sql += f" FROM {_quote(table)} WHERE rowid=?"
            native_bytes = sum(info[c][1] for c in text)
            values = self._raw(
                sql,
                (rowid,),
                numeric_columns=2 * len(text),
                body_cost=4 * native_bytes + 128 * 2 * len(text),
                control_work=_STATEMENT_WORK + len(text) * (_HEADER_WORK + 21 * self.page_size),
            ).fetchone()
            _require(values is not None)
            for i, c in enumerate(text):
                n, nul = values[2 * i : 2 * i + 2]
                _require(type(n) is int and n >= 0 and nul == 0)
                lengths[c] = n
        actual = 128 + sum(
            256 + (160 * (u + 1) if self.encoding == "UTF-8" else 16 * (lengths[c] + 1) ** 2)
            if kind == "text"
            else 64
            for c, (kind, u) in info.items()
        )
        _require(actual <= bound)
        self.probe -= bound - actual
        self._audit("probe-settled", table=table, rowid=rowid, released=bound - actual)
        self._audit(
            "probe-reserved",
            table=table,
            rowid=rowid,
            work=actual,
            total=self.probe,
            heldBound=bound,
        )
        size = 2 + max(0, len(columns) - 1) + len(columns) + sum(_string_cost(c) for c in columns)
        for column in columns:
            kind, u = info[column]
            if kind == "null":
                size += 4
            elif kind == "integer":
                size += u if self.encoding == "UTF-8" else u // 2
            else:
                col, target, n = _quote(column), _quote(table), lengths[column]
                if self.encoding == "UTF-8":
                    counts, params = [], [2 + u]
                    for code in (34, 92, *range(1, 32)):
                        multiplier = 1 if code in _SHORT or code in (34, 92) else 5
                        counts.append(f"{multiplier}*(?-length(replace({col},char({code}),'')))")
                        params.append(n)
                    sql = f"SELECT ?+{'+'.join(counts)} FROM {target} WHERE rowid=?"
                    params.append(rowid)
                else:
                    sql = (
                        f"WITH RECURSIVE target(v,n) AS (SELECT {col},length({col}) "
                        f"FROM {target} WHERE rowid=?),"
                        "chars(i,c) AS (SELECT 1,unicode(substr(v,1,1)) FROM target WHERE n>0 "
                        "UNION ALL SELECT i+1,unicode(substr(v,i+1,1)) "
                        "FROM chars,target WHERE i<n) "
                        "SELECT 2+coalesce(sum(CASE WHEN c IN (8,9,10,12,13,34,92) THEN 2 "
                        "WHEN c BETWEEN 1 AND 31 THEN 6 WHEN c<128 THEN 1 WHEN c<2048 THEN 2 "
                        "WHEN c<65536 THEN 3 ELSE 4 END),0) FROM chars"
                    )
                    params = (rowid,)
                amount = self._raw(
                    sql,
                    params,
                    body_cost=128 + 64 * u,
                    control_work=_STATEMENT_WORK + _HEADER_WORK + 21 * self.page_size,
                ).fetchone()[0]
                _require(type(amount) is int and amount >= 2)
                size += amount
        _limit(self.evidence + size <= self.maximum)
        self.evidence += size
        self.seen[key] = size
        self._audit("charged", table=table, rowid=rowid, bytes=size, total=self.evidence)
        row = self._raw(
            self._bounded_select(f"SELECT * FROM {table} WHERE rowid=?"),
            (rowid,),
            body_cost=size,
            control_work=_STATEMENT_WORK + _HEADER_WORK + 22 * self.page_size,
        ).fetchone()
        _require(
            row is not None
            and _measure(dict(row), self.maximum, safe_int=False, max_depth=2) == size
        )
        self.verified_rows[key] = row
        self._audit("verified-row", table=table, rowid=rowid, bytes=size)
        return size

    def _scan_work(self, table):
        rows = self._table_metadata(table)
        self._raw("table bound lookup", cached=((),))
        native = self.table_sizes[table]
        return (
            len(rows),
            native,
            _STATEMENT_WORK + len(rows) * (_HEADER_WORK + 22 * self.page_size),
        )

    def _bounded_select(self, sql):
        match = re.fullmatch(r"SELECT (.+?) FROM (\w+)(.*)", sql)
        if match is None:
            raise EvidenceFault("unsupported-profile")
        fields, table, tail = match.groups()
        ordered = tail.find(" ORDER BY ")
        predicate, order = (tail, "") if ordered < 0 else (tail[:ordered], tail[ordered:])
        predicate = predicate.strip()
        _require(not predicate or predicate.startswith("WHERE "))
        predicate = predicate[6:] if predicate else "1"
        last = self.highest.get(table)
        first = (
            "1"
            if last is None
            else f"typeof({_quote(self.columns[table][last])}) IN ('text','integer','null')"
        )
        return (
            f"SELECT {fields} FROM {_quote(table)} NOT INDEXED "
            f"WHERE CASE WHEN {first} THEN ({predicate}) ELSE 0 END{order}"
        )

    def _point_set(self, sql, params):
        match = re.fullmatch(r"SELECT (.+?) FROM (\w+)(.*)", sql)
        if match is None:
            raise EvidenceFault("unsupported-profile")
        fields, table, _ = match.groups()
        rowids = self._table_metadata(table)
        # Reserve the bounded numeric VALUES program before building its SQL.
        self._raw(
            "point-set program reservation",
            body_cost=4096 + 512 * max(1, len(rowids)),
            cached=((),),
        )
        bounded = self._bounded_select(sql)
        if fields == "*":
            bounded = bounded.replace("SELECT * FROM", f"SELECT {_quote(table)}.* FROM", 1)
        elif fields == "rowid":
            bounded = bounded.replace("SELECT rowid FROM", f"SELECT {_quote(table)}.rowid FROM", 1)
        values = ",".join("(?)" for _ in rowids) if rowids else "(NULL)"
        start = f"WITH _t01_wanted(_t01_rowkey) AS (VALUES {values}) "
        bounded = bounded.replace(
            f"FROM {_quote(table)} NOT INDEXED WHERE ",
            f"FROM _t01_wanted CROSS JOIN {_quote(table)} NOT INDEXED "
            f"WHERE {_quote(table)}.rowid=_t01_rowkey AND ",
            1,
        )
        return start + bounded, (*rowids, *params)

    @staticmethod
    def _parameter_work(params):
        # len(str) is O(1); reserve UTF8 worst case without encoding first.
        _require(all(type(p) in (str, int) or p is None for p in params))
        return sum(16 * len(p) + 128 if type(p) is str else 128 for p in params)

    def _locators(self, table, tail, params):
        tail = tail.strip()
        if table not in _TABLES:
            raise EvidenceFault("unsupported-profile")
        if table == "sqlite_master":
            self._schema()
            # Index was built only after exact schema body charges. Pay lookup
            # and numeric output before traversing/copying cached references.
            self._raw(
                "cached schema locator lookup",
                body_cost=1024 + self._parameter_work(params),
                cached=((),),
            )
            if tail == "WHERE type='table' AND name=?":
                selected = [r for r in self.schema_names.get(params[0], ()) if r["type"] == "table"]
            elif tail == "WHERE type='table'":
                selected = self.schema_tables
            elif tail == "WHERE name=?":
                selected = self.schema_names.get(params[0], ())
            elif tail.startswith("WHERE type='table' AND name='"):
                name = tail.split("name='", 1)[1].split("'", 1)[0]
                selected = [r for r in self.schema_names.get(name, ()) if r["type"] == "table"]
            else:
                raise EvidenceFault("unsupported-profile")
            self._raw("cached schema rowid output", rows=len(selected), cached=((),))
            return [(table, r["rowid"]) for r in selected]
        self._raw(
            "locator cache lookup", body_cost=128 + self._parameter_work(params), cached=((),)
        )
        key = (table, tail, tuple(params))
        if key not in self.locator_cache:
            count, native, control = self._scan_work(table)
            # Comparisons/order may read any original column. Reserve a complete
            # linear native-body pass before evaluating the first WHERE value.
            extra = 128 + 16 * native + 128 * count + max(1, count) * self._parameter_work(params)
            _limit(self.probe + extra <= MAX_PROBE_WORK)
            self.probe += extra
            self.probe_peak = max(self.probe_peak, self.probe)
            self._audit("scan-reserved", table=table, work=extra, total=self.probe)
            query, actual_params = self._point_set(
                f"SELECT rowid FROM {table} {tail}".strip(), params
            )
            rows = self._raw(
                query,
                actual_params,
                rows=count,
                body_cost=16 * native + 128 * count,
                control_work=control,
            ).fetchall()
            _limit(len(rows) <= self.limits.validation_rows)
            self.locator_cache[key] = tuple((table, row[0]) for row in rows)
        result = self.locator_cache[key]
        self._raw("cached row locators", rows=len(result), cached=((),))
        return list(result)

    def execute(self, sql, params=()):
        sql = _normal(sql)
        if self.guard_phase:
            return self._guard_query(sql, params)
        if sql not in _TEMPLATES:
            raise EvidenceFault("unsupported-profile")
        sources = self._sources(sql, params)
        cost = sum(self._cost(table, rowid) for table, rowid in sources)
        self._raw("result cache lookup", body_cost=128 + self._parameter_work(params), cached=((),))
        key = (sql, tuple(params))
        if sql.startswith("SELECT * FROM "):
            # Locator order/WHERE/LIMIT were already actually evaluated on paid
            # point seeks. Reuse the fully priced original sqlite.Row objects,
            # paying every returned full row again, without another SQLite read.
            rows = tuple(self.verified_rows[(table, rowid)] for table, rowid in sources)
            return self._raw(sql, params, body_cost=cost, cached=rows)
        if key in self.result_cache:
            return self._raw(sql, params, body_cost=cost, cached=self.result_cache[key])
        if "FROM sqlite_master" in sql:
            if not sources:
                return self._raw(sql, body_cost=0, cached=())
            _require(len(sources) == 1)
            actual_sql = sql.split(" FROM ")[0] + " FROM sqlite_master WHERE rowid=?"
            actual_params, control = (
                (sources[0][1],),
                _STATEMENT_WORK + _HEADER_WORK + 21 * self.page_size,
            )
        else:
            tables = set(re.findall(r"(?:FROM|JOIN) (\w+)", sql))
            if not tables:
                match = re.search(r"FROM (\w+)", sql)
                if match:
                    tables.add(match[1])
            control = sum(self._scan_work(t)[2] for t in tables)
            native = sum(self._scan_work(t)[1] for t in tables)
            extra = (
                128
                + 16 * native
                + max(1, sum(self._scan_work(t)[0] for t in tables)) * self._parameter_work(params)
            )
            _limit(self.probe + extra <= MAX_PROBE_WORK)
            self.probe += extra
            self.probe_peak = max(self.probe_peak, self.probe)
            self._audit(
                "scan-reserved", table=",".join(sorted(tables)), work=extra, total=self.probe
            )
            cost += 16 * native
            if " LEFT JOIN " in sql:
                left = [r for t, r in sources if t == "commits"]
                right = [r for t, r in sources if t == "commit_evidence"]
                _require(len(left) <= 1 and len(right) <= 1)
                actual_sql = sql.replace(
                    "commits c LEFT JOIN commit_evidence e ON ",
                    "commits c NOT INDEXED LEFT JOIN commit_evidence e NOT INDEXED "
                    "ON e.rowid=? AND ",
                ).replace("WHERE c.project=?", "WHERE c.rowid=? AND c.project=?")
                actual_params = (right[0] if right else None, left[0] if left else None, *params)
                control = _STATEMENT_WORK + sum(
                    len(self._columns(t)) * (_HEADER_WORK + 21 * self.page_size) for t in tables
                )
            elif " UNION " in sql:
                left, right = sql.split(" UNION ", 1)
                a, ap = self._point_set(left, params[:1])
                b, bp = self._point_set(right, params[1:])
                actual_sql, actual_params = (
                    f"SELECT * FROM ({a}) UNION SELECT * FROM ({b})",
                    (*ap, *bp),
                )
            else:
                actual_sql, actual_params = self._point_set(sql, params)

        cursor = self._raw(actual_sql, actual_params, body_cost=cost, control_work=control)
        expected = 1 if sql.startswith("SELECT count(*)") else max(1, len(sources))
        return _RememberCursor(cursor, self.result_cache, key, expected)

    def _sources(self, sql, params):
        if sql.startswith("SELECT c.*,e.before_snapshot,e.after_snapshot FROM commits c "):
            tail = "WHERE project=? AND operation=?"
            return self._locators("commits", tail, params) + self._locators(
                "commit_evidence", tail, params
            )
        if " UNION " in sql:
            left, right = sql.split(" UNION ", 1)
            return self._sources(left, params[:1]) + self._sources(right, params[1:])
        match = re.fullmatch(r"SELECT .+? FROM (\w+)(.*)", sql)
        if match is None:
            raise EvidenceFault("unsupported-profile")
        table, tail = match.groups()
        return self._locators(table, tail, params)

    def _guard_query(self, sql, params):
        if params:
            raise EvidenceFault("unsupported-profile")
        if sql == "SELECT count(*),coalesce(sum(length(CAST(sql AS BLOB))),0) FROM sqlite_master":
            self._schema()
            return self._raw(
                "cached schema aggregate",
                numeric_columns=2,
                cached=((len(self.schema_rows), self.schema_size),),
            )
        if sql == "SELECT name FROM sqlite_master WHERE type='table'":
            self._schema()
            _limit(len(self.schema_tables) <= 64)
            self._raw(
                "cached table names reservation",
                body_cost=sum(self.seen[("sqlite_master", r["rowid"])] for r in self.schema_tables),
                cached=((),),
            )
            names = tuple((r["name"],) for r in self.schema_tables)
            return self._raw(
                sql,
                body_cost=sum(self.seen[("sqlite_master", r["rowid"])] for r in self.schema_rows),
                cached=names,
            )
        info = re.fullmatch(r'PRAGMA table_info\("(\w+)"\)', sql)
        if info:
            self._columns(info[1])
            return self._raw(
                sql,
                body_cost=self._schema_fee(info[1]) + 128 * 6 * len(self.columns[info[1]]),
                cached=self.table_info[info[1]],
            )
        aggregate = re.fullmatch(r'SELECT count\(\*\),coalesce\(sum\(.+\),0\) FROM "(\w+)"', sql)
        if not aggregate or aggregate[1] not in _TABLES:
            raise EvidenceFault("unsupported-profile")
        table = aggregate[1]
        rows = self._table_metadata(table)
        self._raw("native aggregate cache lookup", cached=((),))
        size = self.table_sizes[table]
        return self._raw(
            "cached native aggregate " + table, numeric_columns=2, cached=((len(rows), size),)
        )


class _EvidenceView:
    """Bind original descriptors, without inheriting or constructing a Store."""

    _project = JobStore._project
    _valid = JobStore._valid
    blob = JobStore.blob
    _plan = staticmethod(JobStore._plan)
    _job_prepared_plan = JobStore._job_prepared_plan
    _accepted_job = JobStore._accepted_job
    get_job = JobStore.get_job
    revision = Store.revision
    vector = Store.vector
    _has_retirements = Store._has_retirements
    _read = Store._read
    state = Store.state
    _state = Store._state
    mapping_status = Store.mapping_status
    marker = Store.marker
    load_snapshot = Store.load_snapshot
    _project_snapshot = Store._project_snapshot
    _snapshot_state = staticmethod(Store._snapshot_state)
    _definition = staticmethod(Store._definition)
    _run = Store._run
    progress = Store.progress
    history = Store.history
    _history = Store._history
    _round_audit_cells = JobStore._round_audit_cells
    _check_summary = JobStore._check_summary
    _marker_dto = staticmethod(JobStore._marker_dto)

    def __init__(self, gate, contract):
        self._db = gate
        self.contract = contract
        self._target_format = 3


def _selector(owner, value, maximum):
    try:
        _measure(value, maximum)
        _require(type(value) is dict)
        kind = value.get("kind")
        common = {"resolutionVersion", "kind", "operationId", "expectedRequest", "originalOrigin"}
        extra = (
            {"projectId", "jobId", "issuedImplementation", "issuedLimits"}
            if kind == "job"
            else set()
        )
        _require(kind in {"job", "project.create"} and set(value) == common | extra)
        _require(type(value["resolutionVersion"]) is int and value["resolutionVersion"] == 1)
        _require(uuid_ref(value["operationId"]))
        origin = value["originalOrigin"]
        _require(type(origin) is dict and set(origin) == {"hostClientId", "engineSessionId"})
        project_lifecycle.origin_value({**origin, "permission": "library.create"})
        request = value["expectedRequest"]
        if kind == "project.create":
            project_lifecycle.request_value(request)
        else:
            _require(uuid_ref(value["projectId"]))
            _require(value["jobId"] is None or uuid_ref(value["jobId"]))
            _require(owner.contract.validate("params_job.create", request))
            _require(owner.contract.validate("implementation", value["issuedImplementation"]))
            _require(owner.contract.validate("limits", value["issuedLimits"]))
            _require(request["projectId"] == value["projectId"])
        _require(request["operationId"] == value["operationId"])
        return json.loads(canonical(value))
    except EvidenceFault:
        raise
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError):
        raise EvidenceFault("invalid-input") from None


def _catalog(view):
    """Schema-only reuse; no unmetered whole-library semantic validation."""
    db = view._db
    format3._domain_schema(view)
    expected = list(format3.TABLES + format3.TRIGGERS)
    expected.extend(
        (job_store._job_object_name(sql), sql)
        for sql in job_store.JOB3_SCHEMA + job_store.JOB3_CATALOG
    )
    for name, sql in expected:
        row = db.execute("SELECT sql FROM sqlite_master WHERE name=?", (name,)).fetchone()
        _require(row is not None and format3._schema(row[0]) == format3._schema(sql))
    apps = db.execute("SELECT * FROM app_format").fetchall()
    _require(len(apps) == 1)
    app = apps[0]
    _require(app["schema_version"] == 1 and app["schema_hash"] == format3.SCHEMA_HASH)
    _require(app["source_format"] in (0, 1, 2) and format3._text(app["migration_id"]))
    _require(
        app["backup_hash"] is None or re.fullmatch(r"[0-9a-f]{64}", app["backup_hash"]) is not None
    )
    jobs = db.execute("SELECT * FROM job_format").fetchall()
    _require(len(jobs) == 1 and jobs[0]["schema_version"] == 3)
    _require(
        jobs[0]["schema_hash"] == job_store.JOB3_HASH and jobs[0]["source_kind"] in {"new", "v2"}
    )


def _identity(condition):
    if not condition:
        raise EvidenceFault("identity-conflict")


def _same(actual, expected):
    # JSON distinguishes booleans from integers; Python equality does not.
    return canonical(actual) == canonical(expected)


def _create(view, selector, claim):
    _identity(claim["kind"] == "application")
    context = project_lifecycle.creation_context(view, claim["project"], selector["operationId"])
    _require(context is not None)
    _identity(context["context"]["request"] == selector["expectedRequest"])
    original = context["context"]["origin"]
    _identity(all(original[key] == value for key, value in selector["originalOrigin"].items()))
    receipt = format3.receipt_for(view, claim["project"], selector["operationId"])
    _require(receipt == context["receipt"])
    return {"finding": "create-record", "createResult": context["result"]}


def _job(view, selector, claim):
    _identity(claim["kind"] == "job" and claim["project"] == selector["projectId"])
    _identity(selector["jobId"] is None or selector["jobId"] == claim["job"])
    request = selector["expectedRequest"]
    job = view._accepted_job(
        claim,
        selector["projectId"],
        request["capability"],
        request["input"],
        request["confirmationRef"],
        selector["issuedImplementation"],
        selector["issuedLimits"],
    )
    row = view._db.execute("SELECT * FROM jobs WHERE id=?", (job["jobId"],)).fetchone()
    context = json.loads(row["context"])
    _require(claim["context"] is None)
    _require(type(context["manifests"]) is dict)
    _require(
        _same(
            context["snapshot"],
            view._project_snapshot(
                job["inputSnapshotId"],
                view._project(job["projectId"]),
            ),
        )
    )
    _require(_same(context["parameters"], view.blob(job["projectId"], job["parametersHash"])))
    if "runConfig" in context:
        config = context["runConfig"]
        _require(_same(config["parameters"], context["parameters"]))
        _require(_same(config["events"], view.blob(job["projectId"], config["eventsRef"])))
        _require(
            _same(
                view.blob(job["projectId"], config["eventConsumptionRef"]),
                {
                    "inputEvents": config["events"],
                    "consumedEvents": [],
                },
            )
        )
    _require(job["definitionSetDigests"] == {k: digest(v) for k, v in context["manifests"].items()})
    snapshot = context["snapshot"]
    _require(
        _same(
            job["dependencyVector"],
            {key: snapshot["dependencyVector"].get(key, 0) for key in job["dependencyVector"]},
        )
    )
    origin = "not-recorded"
    if job["capability"] == "changeset.commit":
        envelope = context[
            "plan"
        ]  # Original accepted_plan above verified all segments/confirmation.
        _identity(all(envelope[key] == value for key, value in selector["originalOrigin"].items()))
        origin = "recorded"
    format3._history(view, view._project(job["projectId"]))
    _terminal(view, job, row, context)
    return {"finding": "job-record", "job": job, "originEvidence": origin}


def _rounds(view, job, row, context):
    db, identity = view._db, job["jobId"]
    reverse = db.execute("SELECT * FROM rounds WHERE job=?", (identity,)).fetchall()
    progress = job["commitProgress"]
    if row["run"] is None:
        _require(not reverse)
        if progress["mode"] == "rounds":
            _require(progress["committedProgress"] is None and job["state"] != "succeeded")
        return
    _require(progress["mode"] == "rounds")
    _require(job["state"] != "queued")
    run = row["run"]
    _require(all(r["run"] == run for r in reverse))
    history = view.history(run)
    _require(history["project"] == view._project(job["projectId"]))
    _require(history["snapshot"] == job["inputSnapshotId"])
    config = json.loads(history["config"])
    _require(json.loads(history["implementation"]) == job["implementation"])
    _require(type(config) is dict and type(config.get("maxRounds")) is int)
    _require(1 <= config["maxRounds"] <= 1000)
    _require(_same(view.blob(job["projectId"], digest(config)), config))
    if job["capability"] == "test.rounds":
        _require(_same(config, context["runConfig"]))
    rounds = history["rounds"]
    _require(len(rounds) == len(reverse))
    _require([r["number"] for r in rounds] == list(range(1, len(rounds) + 1)))
    _require(len(rounds) <= config["maxRounds"])
    for committed in rounds:
        view._round_audit_cells(run, identity, committed)
        saved = view.load_snapshot(committed["snapshot"])
        _require(type(committed["number"]) is int)
        _require(set(saved) == {"project", "run", "round", "state"})
        _require(type(saved["round"]) is int and type(saved["state"]) is dict)
    actual = history["committedProgress"]
    _require(_same(progress["committedProgress"], actual))
    terminal = history["terminal"]
    if job["state"] not in {"failed", "cancelled", "succeeded"}:
        _require(terminal is None)
        return
    _require(terminal is not None and terminal["status"] == job["state"])
    evidence = json.loads(terminal["evidence"])
    if job["state"] != "succeeded":
        _require(_same(evidence, {"jobId": identity, "committedProgress": actual}))
        return
    _require(actual is not None and len(rounds) == config["maxRounds"])
    state = view.load_snapshot(actual["snapshotRef"])["state"]
    consumption = view.blob(job["projectId"], evidence["eventConsumptionRef"])
    _require(type(state.get("pendingEvents")) is list and type(state.get("consumedEvents")) is list)
    _require(
        _same(
            consumption,
            {
                "runId": run,
                "inputSnapshotId": job["inputSnapshotId"],
                "parametersHash": job["parametersHash"],
                "config": config,
                "eventConsumption": state["consumedEvents"],
            },
        )
    )
    _require(
        _same(
            evidence,
            {
                "jobId": identity,
                **actual,
                "reachedMaxRounds": True,
                "pendingEventCount": len(state["pendingEvents"]),
                "eventConsumptionRef": digest(consumption),
            },
        )
    )


def _terminal(view, job, row, context):
    _rounds(view, job, row, context)
    progress, marker = job["commitProgress"], None
    if progress["mode"] == "atomic":
        marker = view.marker(view._project(job["projectId"]), job["operationId"])
        _require(_same(progress["marker"], view._marker_dto(marker) if marker else None))
        if marker is not None:
            _require(marker["job"] == job["jobId"])
            expected_hash = (
                ProjectTransactions._fingerprint(
                    domain_changesets.unpack(context["plan"]["preview"])
                )
                if job["capability"] == "changeset.commit"
                else digest(context["plan"])
            )
            _require(marker["fingerprint"] == expected_hash)
            _require(marker["before_snapshot"] == job["inputSnapshotId"])
            _require(marker["revision"] == context["snapshot"]["projectRevision"] + 1)
            receipt = format3.receipt_for(view, view._project(job["projectId"]), job["operationId"])
            _require(receipt["domainMarkerRef"] == job["operationId"])
        if job["state"] == "succeeded":
            _require(marker is not None)
    published = view._db.execute(
        "SELECT * FROM job_results WHERE job=?", (job["jobId"],)
    ).fetchall()
    if job["state"] != "succeeded":
        _require(not published)
        _require(job["resultRef"] is None)
        return
    ref = job["resultRef"]
    _require(ref is not None and ref["inputSnapshotId"] == job["inputSnapshotId"])
    _require(len(published) == 1 and published[0]["id"] == ref["resultId"])
    result = view._db.execute("SELECT * FROM results WHERE id=?", (ref["resultId"],)).fetchone()
    joined = view._db.execute("SELECT * FROM job_results WHERE id=?", (ref["resultId"],)).fetchone()
    _require(result is not None and joined is not None and joined["job"] == job["jobId"])
    kind = {
        "test.read": "test",
        "test.atomic": "receipt",
        "test.rounds": "scenario",
        "query.execute": "query",
        "reasoning.execute": "reasoning",
        "validation.execute": "validation",
        "behavior.test": "behavior",
        "scenario.run": "scenario",
        "mapping.commit": "receipt",
        "changeset.commit": "receipt",
    }[job["capability"]]
    internal = view._project(job["projectId"])
    _require(result["project"] == internal and result["snapshot"] == job["inputSnapshotId"])
    _require(
        result["kind"] == kind and json.loads(result["implementation"]) == job["implementation"]
    )
    _require(_same(json.loads(result["dependencies"]), job["dependencyVector"]))
    _require(_same(json.loads(joined["manifests"]), context["manifests"]))
    _require(
        json.loads(joined["projection"])
        == {
            "definitionId": job["input"]["definitionId"],
            "scope": job["scope"],
            "parametersHash": job["parametersHash"],
        }
    )
    _require(
        result["cache_key"]
        == digest(
            {
                "project": internal,
                "kind": kind,
                "snapshot": job["inputSnapshotId"],
                "dependencies": job["dependencyVector"],
                "implementation": job["implementation"],
            }
        )
    )
    if result["payload"] is None:
        return
    payload = json.loads(result["payload"])
    _require(type(payload) is list and all(view.contract.validate("row", r) for r in payload))
    _require(len(payload) <= 10000)
    _measure(payload, 8388608, allow_float=True)
    _require(len({r["rowId"] for r in payload}) == len(payload))
    _require(len({r["ordinal"] for r in payload}) == len(payload))
    _require(payload == sorted(payload, key=lambda r: (r["ordinal"], r["rowId"])))
    if marker is not None:
        _require(len(payload) == 1 and payload[0]["ordinal"] == 0)
        _require(
            _same(
                payload[0]["cells"],
                [
                    "commit.receipt.v1",
                    job["operationId"],
                    marker["revision"],
                    marker["before_snapshot"],
                    marker["after_snapshot"],
                    marker["fingerprint"],
                ],
            )
        )
    if progress["mode"] == "rounds":
        actual = progress["committedProgress"]
        history = view.history(actual["runId"])
        evidence = json.loads(history["terminal"]["evidence"])
        pending = view.load_snapshot(actual["snapshotRef"])["state"]["pendingEvents"]
        _require(len(payload) == len(history["rounds"]) + 1)
        expected = [
            [
                "run.summary.v1",
                actual["runId"],
                actual["lastCommittedRound"],
                actual["snapshotRef"],
                True,
                bool(pending),
                len(pending),
                evidence["eventConsumptionRef"],
            ]
        ]
        expected.extend(
            view._round_audit_cells(actual["runId"], job["jobId"], r) for r in history["rounds"]
        )
        _require(_same([r["cells"] for r in payload], expected))
        view._check_summary(
            {
                "projectId": job["projectId"],
                "jobId": job["jobId"],
                "resultId": result["id"],
                "inputSnapshotId": job["inputSnapshotId"],
            },
            payload,
        )


def read_operation_evidence(
    owner,
    selector,
    *,
    maxEvidenceBytes,
    maxSelectorBytes,
    maxReturnBytes,
    readerLimits,
):
    """Read bounded local facts. The caller supplies its actual owner and limits."""
    maximum = _positive(maxEvidenceBytes, 67108864)
    selector_max = _positive(maxSelectorBytes, 262144)
    result_max = _positive(maxReturnBytes, 131072)
    if not isinstance(owner, JobStore) or owner._target_format != 3:
        raise EvidenceFault("state")
    if type(readerLimits) is not ReadLimits:
        raise EvidenceFault("invalid-input")
    selected = _selector(owner, selector, selector_max)
    db = owner._db
    try:
        if db.in_transaction:
            raise EvidenceFault("state")
    except sqlite3.Error as exc:
        raise _sqlite_error(exc) from None
    gate = _MeteredGate(db, maximum, readerLimits)
    view = _EvidenceView(gate, owner.contract)
    began, first, result = False, None, None
    try:
        db.execute("BEGIN")
        began = True
        gate._audit("begin", controlQueries=1)
        actual_format = gate._raw("PRAGMA user_version").fetchone()[0]
        if type(actual_format) is not int or actual_format != 3:
            raise EvidenceFault("state")
        gate.encoding = gate._raw("PRAGMA encoding").fetchone()[0].upper()
        if gate.encoding not in {"UTF-8", "UTF-16LE", "UTF-16BE"}:
            raise EvidenceFault("unsupported-profile")
        base = {
            "evidenceVersion": 1,
            "kind": selected["kind"],
            "operationId": selected["operationId"],
        }
        try:
            gate.guard_phase = True
            ProjectHostReader._preflight(SimpleNamespace(_store=view, _limits=readerLimits))
            gate.guard_phase = False
            _catalog(view)
            claim = gate.execute(
                "SELECT * FROM operation_claims WHERE operation=?", (selected["operationId"],)
            ).fetchone()
            finding = (
                {"finding": "no-evidence"}
                if claim is None
                else (
                    _create(view, selected, claim)
                    if selected["kind"] == "project.create"
                    else _job(view, selected, claim)
                )
            )
        except HostReadFault:
            raise
        except JobFault as exc:
            if exc.code == "IDENTITY_CONFLICT":
                raise EvidenceFault("identity-conflict") from None
            finding = {"finding": "incomplete-evidence"}
        except (
            ValueError,
            KeyError,
            TypeError,
            OverflowError,
            RecursionError,
            AttributeError,
            IndexError,
        ):
            finding = {"finding": "incomplete-evidence"}
        result = {**base, **finding}
        _measure(result, result_max)
        result = json.loads(canonical(result))
    except EvidenceFault as exc:
        first = exc
    except HostReadFault as exc:
        first = EvidenceFault("resource-limit" if exc.reason == "limit" else "state")
    except sqlite3.Error as exc:
        first = _sqlite_error(exc)
    except BaseException as exc:
        # Preserve cancellation/interrupt identity while allowing the owner to
        # observe a subsequent cleanup failure on this same exception object.
        first = exc
    finally:
        if began:
            try:
                db.execute("ROLLBACK")
                gate._audit(
                    "rollback",
                    controlQueries=2,
                    queries=gate.queries + 2,
                    evidence=gate.evidence,
                    probe=gate.probe,
                    probePeak=gate.probe_peak,
                    readWork=gate.read_work,
                )
            except sqlite3.Error as exc:
                if first is None:
                    first = _sqlite_error(exc)
                first.cleanup_failed = True
    if first is not None:
        raise first from None
    return result


_TEMPLATES = {
    "SELECT * FROM job_results WHERE job=?",
    "SELECT * FROM app_checkpoints WHERE id=? AND project=?",
    "SELECT * FROM app_format",
    "SELECT * FROM app_operations WHERE project=? AND operation=?",
    "SELECT * FROM app_operations WHERE project=? ORDER BY sequence",
    "SELECT * FROM app_origins WHERE project=?",
    "SELECT * FROM app_projects WHERE project=?",
    "SELECT * FROM app_receipts WHERE project=? AND operation=?",
    "SELECT * FROM job_confirmations WHERE id=? AND project=?",
    "SELECT * FROM job_confirmations WHERE project=? AND id=?",
    "SELECT * FROM job_details WHERE project=? AND id=?",
    "SELECT * FROM job_format",
    "SELECT * FROM job_plans WHERE project=? AND ref=?",
    "SELECT * FROM job_plans WHERE ref=? AND project=?",
    "SELECT * FROM job_results WHERE id=?",
    "SELECT * FROM jobs WHERE id=?",
    "SELECT * FROM migration_log",
    "SELECT * FROM operation_claims WHERE operation=?",
    "SELECT * FROM results WHERE id=?",
    "SELECT * FROM rounds WHERE job=?",
    "SELECT * FROM rounds WHERE run=? ORDER BY number",
    "SELECT * FROM run_terminal WHERE run=?",
    "SELECT * FROM runs WHERE id=?",
    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='definition_retirements'",
    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='operation_claims'",
    (
        "SELECT attempt,record_version,course,task,payload FROM app_learning WHERE "
        "project=? ORDER BY attempt"
    ),
    (
        "SELECT c.*,e.before_snapshot,e.after_snapshot FROM commits c LEFT JOIN "
        "commit_evidence e ON e.project=c.project AND e.operation=c.operation WHERE "
        "c.project=? AND c.operation=?"
    ),
    "SELECT count(*) FROM app_receipts WHERE project=?",
    (
        "SELECT domain_revision FROM app_operations WHERE project=? AND "
        "kind='legacy-domain' ORDER BY sequence"
    ),
    "SELECT domain_revision FROM app_origins WHERE project=?",
    (
        "SELECT editor,generation,present,bound_revision,payload,content_hash FROM "
        "app_drafts WHERE project=? ORDER BY editor"
    ),
    "SELECT generated_version FROM mapping_state WHERE project=? AND owner=?",
    "SELECT id FROM app_checkpoints WHERE project=?",
    (
        "SELECT id,subject,predicate,object,owner,source_row,managed_value FROM facts WHERE "
        "project=? ORDER BY id"
    ),
    "SELECT internal FROM public_projects WHERE public=?",
    "SELECT key,version FROM versions WHERE project=?",
    "SELECT layer,id FROM definition_retirements WHERE project=?",
    "SELECT layer,id FROM definitions WHERE project=?",
    "SELECT layer,id,payload FROM definitions WHERE project=? ORDER BY layer,id",
    "SELECT migration_id FROM app_format WHERE singleton=1",
    "SELECT number,snapshot FROM rounds WHERE run=? ORDER BY number DESC LIMIT 1",
    "SELECT operation FROM commits WHERE project=?",
    "SELECT owner FROM mapping_state WHERE project=? ORDER BY owner",
    (
        "SELECT owner FROM mapping_state WHERE project=? UNION SELECT owner FROM facts "
        "WHERE project=? AND owner IS NOT NULL"
    ),
    "SELECT payload FROM app_receipts WHERE project=? AND operation=?",
    "SELECT payload FROM job_blobs WHERE project=? AND ref=?",
    "SELECT payload FROM snapshots WHERE id=?",
    "SELECT revision FROM projects WHERE id=?",
    (
        "SELECT sequence,attempt,event_id,payload FROM app_assistance WHERE project=? ORDER "
        "BY sequence"
    ),
    "SELECT sql FROM sqlite_master WHERE name=?",
    "SELECT status,evidence FROM run_terminal WHERE run=?",
}
