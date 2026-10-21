"""Bounded local file parsing. No paths, network, formula evaluation or Store writes."""

import csv
import io
import math
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from hashlib import sha256

MAX_BYTES = 8 * 1024 * 1024
MAX_EXPANDED = 64 * 1024 * 1024
MAX_ROWS = 50_000
MAX_COLUMNS = 256
MAX_CELL = 32_768
ENCODINGS = {"utf-8", "utf-8-sig", "gb18030", "big5", "utf-16"}


@dataclass(frozen=True)
class Issue:
    code: str
    sheet: str
    row: int
    column: int
    field: str = ""


class SourceError(ValueError):
    """Internal safe error; adapters must use an approved public error mapping."""

    def __init__(self, issue: Issue):
        self.issue = issue
        super().__init__(issue.code)


@dataclass(frozen=True)
class Cell:
    text: str
    kind: str = "string"


@dataclass(frozen=True)
class Row:
    number: int
    cells: tuple[Cell, ...]


@dataclass(frozen=True)
class Table:
    source_hash: str
    sheet: str
    fields: tuple[str, ...]
    rows: tuple[Row, ...]

    def describe(self) -> tuple[dict, ...]:
        """Observed types and real samples; no confidence score or coercion."""
        return tuple(
            {
                "field": field,
                "types": sorted({row.cells[i].kind for row in self.rows}),
                "samples": [row.cells[i].text for row in self.rows[:5]],
            }
            for i, field in enumerate(self.fields)
        )


def fail(code: str, sheet: str = "", row: int = 0, column: int = 0, field: str = ""):
    raise SourceError(Issue(code, sheet, row, column, field))


def _bytes(data: bytes) -> None:
    if not isinstance(data, bytes):
        fail("INVALID_SOURCE")
    if len(data) > MAX_BYTES:
        fail("SOURCE_LIMIT")


def _table(data: bytes, sheet: str, records) -> Table:
    fields = None
    rows = []
    for number, cells in records:
        if number > MAX_ROWS + 1 or len(cells) > MAX_COLUMNS:
            fail("SOURCE_LIMIT", sheet, number)
        for i, cell in enumerate(cells, 1):
            if len(cell.text) > MAX_CELL or "\x00" in cell.text:
                fail("INVALID_CELL", sheet, number, i)
        if fields is None:
            if not cells:
                fail("EMPTY_HEADER", sheet, number)
            names = [cell.text for cell in cells]
            for i, name in enumerate(names, 1):
                if not name.strip() or names.count(name) > 1:
                    fail("INVALID_HEADER", sheet, number, i, name)
            fields = tuple(names)
            continue
        if len(cells) != len(fields):
            fail("ROW_WIDTH", sheet, number, min(len(cells), len(fields)) + 1)
        # Blank records are preserved; selecting their empty key must block the batch.
        rows.append(Row(number, tuple(cells)))
    if fields is None:
        fail("EMPTY_SOURCE", sheet)
    return Table(sha256(data).hexdigest(), sheet, fields, tuple(rows))


def _encoding_position(prefix: str) -> tuple[int, int]:
    # Mirror csv.reader defaults, including quoted commas, escaped quotes and
    # multiline fields. Locations use the record's starting physical line.
    line = start = column = 1
    quoted = False
    field_start = True
    i = 0
    while i < len(prefix):
        char = prefix[i]
        if char == '"':
            if quoted and i + 1 < len(prefix) and prefix[i + 1] == '"':
                i += 2
                continue
            if quoted:
                quoted = False
            elif field_start:
                quoted = True
            field_start = False
        elif char in "\r\n":
            if char == "\r" and i + 1 < len(prefix) and prefix[i + 1] == "\n":
                i += 1
            line += 1
            if not quoted:
                start, column, field_start = line, 1, True
        elif char == "," and not quoted:
            column += 1
            field_start = True
        else:
            field_start = False
        i += 1
    return start, column


def parse_csv(data: bytes, *, encoding: str = "utf-8-sig") -> Table:
    _bytes(data)
    if encoding not in ENCODINGS:
        fail("ENCODING_UNSUPPORTED", "CSV")
    try:
        decoded = data.decode(encoding, errors="strict")
    except UnicodeDecodeError as error:
        prefix = data[: error.start].decode(encoding, errors="ignore")
        row, column = _encoding_position(prefix)
        fail("INVALID_ENCODING", "CSV", row, column)
    reader = csv.reader(io.StringIO(decoded, newline=""), strict=True)

    def records():
        while True:
            start = reader.line_num + 1
            try:
                values = next(reader)
            except StopIteration:
                return
            except csv.Error:
                fail("INVALID_CSV", "CSV", start)
            yield start, tuple(Cell(value) for value in values)

    return _table(data, "CSV", records())


def _xlsx_container(data: bytes) -> None:
    _bytes(data)
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) > 2048 or sum(item.file_size for item in entries) > MAX_EXPANDED:
                fail("SOURCE_LIMIT")
            names = [item.filename for item in entries]
            if len(names) != len(set(names)):
                fail("INVALID_XLSX")
            if "[Content_Types].xml" not in names:
                fail("INVALID_XLSX")
            for item in entries:
                if item.flag_bits & 1:
                    fail("ENCRYPTED_UNSUPPORTED")
                if "vbaproject" in item.filename.lower():
                    fail("MACRO_UNSUPPORTED")
                if item.filename.endswith((".xml", ".rels")):
                    value = archive.read(item)
                    # Also reject UTF-16/32 DTD syntax. defusedxml is mandatory below.
                    text = value.replace(b"\x00", b"").upper()
                    if b"<!DOCTYPE" in text or b"<!ENTITY" in text:
                        fail("UNSAFE_XML")
                    if item.filename == "[Content_Types].xml" and b"MACROENABLED" in text:
                        fail("MACRO_UNSUPPORTED")
    except (zipfile.BadZipFile, RuntimeError, OSError):
        fail("INVALID_XLSX")


def _open_xlsx(data: bytes, *, values: bool):
    _xlsx_container(data)
    try:
        import defusedxml  # noqa: F401 -- required, not an optional security fallback
        from openpyxl import load_workbook
    except ImportError:
        fail("XLSX_PARSER_UNAVAILABLE")
    try:
        return load_workbook(io.BytesIO(data), read_only=True, data_only=values, keep_links=False)
    except Exception:
        fail("INVALID_XLSX")


def xlsx_sheets(data: bytes) -> tuple[str, ...]:
    book = _open_xlsx(data, values=True)
    try:
        return tuple(book.sheetnames)
    finally:
        book.close()


def _cell(value, kind: str, sheet: str, row: int, column: int) -> Cell:
    if kind == "e":
        fail("XLSX_CELL_ERROR", sheet, row, column)
    if value is None:
        return Cell("", "empty")
    if isinstance(value, bool):
        return Cell("true" if value else "false", "boolean")
    if isinstance(value, datetime):
        return Cell(value.isoformat(), "datetime")
    if isinstance(value, date):
        return Cell(value.isoformat(), "date")
    if isinstance(value, int | float):
        if isinstance(value, float) and not math.isfinite(value):
            fail("INVALID_CELL", sheet, row, column)
        return Cell(str(value), "number")
    return Cell(str(value))


def _empty_formula_caches(data: bytes, path: str) -> set[str]:
    # openpyxl returns None for a cached empty string and for an absent cache.
    # Inspect only the selected worksheet; never evaluate a formula. This uses
    # the pinned candidate's worksheet path, with no URL/file dereferencing.
    from defusedxml.ElementTree import iterparse

    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    result = set()
    with zipfile.ZipFile(io.BytesIO(data)) as archive, archive.open(path.lstrip("/")) as xml:
        for _, element in iterparse(xml, events=("end",)):
            if element.tag == ns + "c":
                value = element.find(ns + "v")
                if (
                    element.get("t") == "str"
                    and element.find(ns + "f") is not None
                    and value is not None
                    and value.text in (None, "")
                ):
                    result.add(element.get("r"))
                element.clear()
    return result


def parse_xlsx(data: bytes, *, sheet: str) -> Table:
    if not isinstance(sheet, str) or not sheet:
        fail("SHEET_REQUIRED")
    book = _open_xlsx(data, values=True)
    formulas = None
    try:
        formulas = _open_xlsx(data, values=False)
        if sheet not in book.sheetnames:
            fail("SHEET_NOT_FOUND", sheet)
        ws, fs = book[sheet], formulas[sheet]
        # Do not trust worksheet dimensions (often stale or malicious).
        ws.reset_dimensions()
        fs.reset_dimensions()
        empty_caches = _empty_formula_caches(data, fs._worksheet_path)

        def records():
            width = None
            for number, (values, originals) in enumerate(zip(ws.rows, fs.rows, strict=True), 1):
                if len(values) > MAX_COLUMNS or number > MAX_ROWS + 1:
                    fail("SOURCE_LIMIT", sheet, number)
                cells = []
                for i, (cell, original) in enumerate(zip(values, originals, strict=True), 1):
                    if original.data_type == "f" and cell.value is None:
                        if original.coordinate in empty_caches:
                            cells.append(Cell("", "string"))
                            continue
                        fail("FORMULA_CACHE_MISSING", sheet, number, i)
                    cells.append(_cell(cell.value, cell.data_type, sheet, number, i))
                if width is None:
                    width = len(cells)
                elif len(cells) < width:
                    cells.extend(Cell("", "empty") for _ in range(width - len(cells)))
                yield number, tuple(cells)

        return _table(data, sheet, records())
    except SourceError:
        raise
    except Exception:
        fail("INVALID_XLSX", sheet)
    finally:
        book.close()
        if formulas is not None:
            formulas.close()
