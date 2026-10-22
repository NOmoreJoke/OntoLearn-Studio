"""Fixed synthetic real-parser probe for the product's unsigned package.

No caller-supplied path, script, workbook, URL or business input is accepted.
A successful probe is not a registered mapping capability or platform acceptance.
"""

import io
import json
import socket
import zipfile
from contextlib import contextmanager
from importlib import import_module
from importlib.metadata import version
from xml.etree.ElementTree import SubElement, tostring

from ontolearn_engine.mapping.plan import Binding, Mapping, preview
from ontolearn_engine.mapping.source import (
    MAX_BYTES,
    MAX_CELL,
    MAX_COLUMNS,
    MAX_EXPANDED,
    MAX_ROWS,
    SourceError,
    parse_csv,
    parse_xlsx,
    xlsx_sheets,
)


def _require(condition: bool, code: str) -> None:
    # Keep probes effective under python -O / optimized bundle builds too.
    if not condition:
        raise RuntimeError(code)


def _variant(
    data: bytes, *, cache: str | None = None, missing=False, sparse=False, macro=False
) -> bytes:
    from defusedxml.ElementTree import fromstring

    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as original, zipfile.ZipFile(output, "w") as out:
        for item in original.infolist():
            value = original.read(item)
            if item.filename == "xl/worksheets/sheet1.xml":
                root = fromstring(value)
                row = root.find(f"{ns}sheetData/{ns}row[@r='2']")
                cell = row.find(f"{ns}c[@r='B2']")
                if sparse:
                    row.remove(cell)
                else:
                    cell.clear()
                    cell.set("r", "B2")
                    if not missing:
                        cell.set("t", "str")
                    SubElement(cell, ns + "f").text = 'CONCAT("泵站","A")'
                    if not missing:
                        SubElement(cell, ns + "v").text = cache
                value = tostring(root, encoding="utf-8")
            out.writestr(item, value)
        if macro:
            out.writestr("xl/vbaProject.bin", b"synthetic rejected marker; no executable macro")
    return output.getvalue()


def _legacy_cases() -> dict:
    from openpyxl import Workbook

    versions = {name: version(name) for name in ("openpyxl", "et-xmlfile", "defusedxml")}
    _require(
        versions == {"openpyxl": "3.1.5", "et-xmlfile": "2.0.0", "defusedxml": "0.7.1"},
        "DEPENDENCY_VERSION_MISMATCH",
    )
    data = "equipment_id,equipment_name\n001,泵站A\n002,泵站B\n".encode()
    csv_table = parse_csv(data)
    book = Workbook()
    sheet = book.active
    sheet.title = "设备"
    sheet.append(["equipment_id", "equipment_name"])
    sheet.append(["001", "泵站A"])
    sheet.append(["002", "泵站B"])
    other = book.create_sheet("不能默认读取")
    other.append(["other"])
    output = io.BytesIO()
    book.save(output)
    book.close()
    xlsx_data = output.getvalue()
    _require(xlsx_sheets(xlsx_data) == ("设备", "不能默认读取"), "SHEET_SET_MISMATCH")
    xlsx_table = parse_xlsx(xlsx_data, sheet="设备")
    mapping = Mapping(
        "probe-map",
        1,
        "urn:example:equipment/",
        "urn:example:Equipment",
        ("equipment_id",),
        (Binding("equipment_name", "urn:example:name"),),
    )
    snapshot = {
        "project": "synthetic-probe",
        "projectRevision": 0,
        "state": {"definitions": [], "facts": []},
    }
    expected = {
        ("urn:example:equipment/001", "urn:example:name", '"泵站A"'),
        ("urn:example:equipment/002", "urn:example:name", '"泵站B"'),
        (
            "urn:example:equipment/001",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
            "<urn:example:Equipment>",
        ),
        (
            "urn:example:equipment/002",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
            "<urn:example:Equipment>",
        ),
    }
    for table in (csv_table, xlsx_table):
        result = preview(mapping, table, snapshot)
        _require(result.ready and set(result.added) == expected, "FACT_SET_MISMATCH")
        _require([row.cells[0].text for row in table.rows] == ["001", "002"], "KEY_MISMATCH")
        _require([row.number for row in table.rows] == [2, 3], "SOURCE_ROW_MISMATCH")
        _require(
            [row["row"] for row in result.rows()]
            == [
                json.dumps(
                    {"sheet": table.sheet, "row": n}, ensure_ascii=False, separators=(",", ":")
                )
                for n in (2, 3)
            ],
            "PROVENANCE_MISMATCH",
        )
    cached = parse_xlsx(_variant(xlsx_data, cache="泵站A"), sheet="设备")
    _require(cached.rows[0].cells[1].text == "泵站A", "FORMULA_CACHE_MISMATCH")
    empty = parse_xlsx(_variant(xlsx_data, cache=""), sheet="设备")
    _require(empty.rows[0].cells[1].text == "", "EMPTY_CACHE_MISMATCH")
    sparse = parse_xlsx(_variant(xlsx_data, sparse=True), sheet="设备")
    _require(tuple(c.text for c in sparse.rows[0].cells) == ("001", ""), "SPARSE_MISMATCH")
    cases = {
        "csv-exact-set": "passed",
        "xlsx-exact-set": "passed",
        "sheet-selection": "passed",
        "cached-formula": "passed",
        "cached-empty-string": "passed",
        "sparse-cell": "passed",
    }
    failures = (
        (
            "missing-formula-cache",
            lambda: parse_xlsx(_variant(xlsx_data, missing=True), sheet="设备"),
            "FORMULA_CACHE_MISSING",
        ),
        (
            "macro-refusal",
            lambda: parse_xlsx(_variant(xlsx_data, macro=True), sheet="设备"),
            "MACRO_UNSUPPORTED",
        ),
        ("invalid-encoding", lambda: parse_csv(b"id,name\n001,\xff\n"), "INVALID_ENCODING"),
        ("source-limit", lambda: parse_csv(b"x" * (MAX_BYTES + 1)), "SOURCE_LIMIT"),
    )
    for name, action, expected_code in failures:
        try:
            action()
        except SourceError as error:
            _require(error.issue.code == expected_code, "ERROR_CODE_MISMATCH")
            cases[name] = expected_code
        else:
            raise RuntimeError("EXPECTED_REFUSAL_MISSING")
    duplicate = preview(
        mapping, parse_csv(b"equipment_id,equipment_name\n001,A\n001,B\n"), snapshot
    )
    _require(
        not duplicate.ready
        and {(i.code, i.row, i.column) for i in duplicate.issues}
        == {("DUPLICATE_KEY", 2, 1), ("DUPLICATE_KEY", 3, 1)},
        "DUPLICATE_KEY_MISMATCH",
    )
    cases["duplicate-key"] = "DUPLICATE_KEY"
    return {
        "probe": "T03-real-csv-xlsx",
        "scope": "fixed-synthetic-parser-only",
        "csv": "passed",
        "xlsx": "passed",
        "exactFacts": sorted(expected),
        "versions": versions,
        "cases": cases,
        "registeredBusinessCapability": False,
    }


@contextmanager
def _socket_guard():
    """Count and refuse attempts during fixed parsing; never call the network."""
    names = ("socket", "create_connection", "getaddrinfo")
    originals = {name: getattr(socket, name) for name in names}
    calls = dict.fromkeys(names, 0)

    def forbidden(name):
        def reject(*_args, **_kwargs):
            calls[name] += 1
            raise RuntimeError("MAPPING_PROBE_NETWORK_ATTEMPT")

        return reject

    try:
        for name in names:
            setattr(socket, name, forbidden(name))
        yield calls
    finally:
        for name, original in originals.items():
            setattr(socket, name, original)


def _external_workbook(reference: str) -> bytes:
    """The two fixed synthetic OOXML inputs; no paths or values from callers."""
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rels = "http://schemas.openxmlformats.org/package/2006/relationships"
    docrel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    first = '<c r="A2" t="inlineStr"><is><t>001</t></is></c>'
    if reference == "external-cached-formula":
        second = (
            '<c r="B2" t="str"><f>WEBSERVICE("https://example.invalid/ref")</f>'
            "<v>只读已保存值</v></c>"
        )
        links = ""
    elif reference == "external-hyperlink":
        second = '<c r="B2" t="inlineStr"><is><t>显示文本</t></is></c>'
        links = f'<hyperlinks><hyperlink xmlns:r="{docrel}" ref="B2" r:id="rId1"/></hyperlinks>'
    else:
        raise RuntimeError("MAPPING_PROBE_FIXED_CASE_INVALID")
    header = (
        '<row r="1"><c r="A1" t="inlineStr"><is><t>id</t></is></c>'
        '<c r="B1" t="inlineStr"><is><t>name</t></is></c></row>'
    )
    items = {
        "[Content_Types].xml": (
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" '
            'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>"
        ),
        "_rels/.rels": (
            f'<Relationships xmlns="{rels}"><Relationship Id="rId1" '
            f'Type="{docrel}/officeDocument" Target="xl/workbook.xml"/></Relationships>'
        ),
        "xl/workbook.xml": (
            f'<workbook xmlns="{ns}" xmlns:r="{docrel}">'
            '<sheets><sheet name="设备" sheetId="1" r:id="rId1"/></sheets></workbook>'
        ),
        "xl/_rels/workbook.xml.rels": (
            f'<Relationships xmlns="{rels}"><Relationship Id="rId1" '
            f'Type="{docrel}/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'
        ),
        "xl/worksheets/sheet1.xml": (
            f'<worksheet xmlns="{ns}"><sheetData>{header}'
            f'<row r="2">{first}{second}</row></sheetData>{links}</worksheet>'
        ),
    }
    if reference == "external-hyperlink":
        items["xl/worksheets/_rels/sheet1.xml.rels"] = (
            f'<Relationships xmlns="{rels}"><Relationship Id="rId1" '
            f'Type="{docrel}/hyperlink" Target="https://example.invalid/ref" '
            'TargetMode="External"/></Relationships>'
        )
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, value in items.items():
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            archive.writestr(info, value.encode())
    return output.getvalue()


def _boundary_cases(calls: dict) -> dict:
    evidence = {}
    for name, value in (
        ("external-cached-formula", "只读已保存值"),
        ("external-hyperlink", "显示文本"),
    ):
        table = parse_xlsx(_external_workbook(name), sheet="设备")
        cells = [cell.text for cell in table.rows[0].cells]
        _require(cells == ["001", value], "EXTERNAL_REFERENCE_VALUE_MISMATCH")
        _require(not any(calls.values()), "MAPPING_PROBE_NETWORK_ATTEMPT")
        evidence[name] = {
            "cells": cells,
            "code": "",
            "sheet": table.sheet,
            "row": table.rows[0].number,
            "column": 2,
            "socketCalls": dict(calls),
        }
    csv_cases = (
        ("csv-file-limit-located", b"x" * (MAX_BYTES + 1), "SOURCE_LIMIT", "", 0, 0),
        (
            "csv-column-limit-located",
            (",".join(f"c{i}" for i in range(MAX_COLUMNS + 1)) + "\n").encode(),
            "SOURCE_LIMIT",
            "CSV",
            1,
            0,
        ),
        (
            "csv-cell-limit-located",
            ("id\n" + "x" * (MAX_CELL + 1) + "\n").encode(),
            "INVALID_CELL",
            "CSV",
            2,
            1,
        ),
        (
            "csv-row-limit-located",
            ("id\n" + "x\n" * (MAX_ROWS + 1)).encode(),
            "SOURCE_LIMIT",
            "CSV",
            MAX_ROWS + 2,
            0,
        ),
    )
    for name, data, code, sheet, row, column in csv_cases:
        try:
            parse_csv(data)
        except SourceError as error:
            issue = error.issue
            _require(
                (issue.code, issue.sheet, issue.row, issue.column) == (code, sheet, row, column),
                "CSV_BOUNDARY_LOCATION_MISMATCH",
            )
            _require(not any(calls.values()), "MAPPING_PROBE_NETWORK_ATTEMPT")
            evidence[name] = {
                "cells": [],
                "code": issue.code,
                "sheet": issue.sheet,
                "row": issue.row,
                "column": issue.column,
                "socketCalls": dict(calls),
            }
        else:
            raise RuntimeError("CSV_BOUNDARY_REFUSAL_MISSING")
    return evidence


def run() -> dict:
    # Dependency import is not a network-attempt measurement. The guard covers
    # all fixed parsing and input construction, including the six new cases.
    import_module("openpyxl")
    with _socket_guard() as calls:
        result = _legacy_cases()
        _require(not any(calls.values()), "MAPPING_PROBE_NETWORK_ATTEMPT")
        evidence = _boundary_cases(calls)
        result["cases"].update({name: row["code"] or "passed" for name, row in evidence.items()})
        result["boundaryEvidence"] = evidence
        result["boundaryVersion"] = 1
        result["limits"] = {
            "maxBytes": MAX_BYTES,
            "maxExpanded": MAX_EXPANDED,
            "maxRows": MAX_ROWS,
            "maxColumns": MAX_COLUMNS,
            "maxCell": MAX_CELL,
        }
    return result


def main() -> None:
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
