"""Real CSV bytes and real OOXML workbook fixtures; optional parser probe is explicit."""

import io
import zipfile
from xml.sax.saxutils import escape

import pytest
from ontolearn_engine.mapping.source import (
    SourceError,
    parse_csv,
    parse_xlsx,
    xlsx_sheets,
)


def test_csv_multiline_bom_leading_zero_and_observed_samples():
    table = parse_csv('\ufeffid,name\n001,"第一行\n第二行"\n002,泵站B\n'.encode())
    assert table.fields == ("id", "name")
    assert [(r.number, tuple(c.text for c in r.cells)) for r in table.rows] == [
        (2, ("001", "第一行\n第二行")),
        (4, ("002", "泵站B")),
    ]
    assert table.describe() == (
        {"field": "id", "types": ["string"], "samples": ["001", "002"]},
        {"field": "name", "types": ["string"], "samples": ["第一行\n第二行", "泵站B"]},
    )


def test_csv_explicit_encoding_only():
    data = "id,name\n001,泵站A\n".encode("gb18030")
    with pytest.raises(SourceError) as error:
        parse_csv(data)
    assert (error.value.issue.code, error.value.issue.row, error.value.issue.column) == (
        "INVALID_ENCODING",
        2,
        2,
    )
    assert parse_csv(data, encoding="gb18030").rows[0].cells[1].text == "泵站A"


@pytest.mark.parametrize(
    ("data", "code", "row", "column"),
    [
        (b"", "EMPTY_SOURCE", 0, 0),
        (b"id,id\n1,2\n", "INVALID_HEADER", 1, 1),
        (b"id,name\n1\n", "ROW_WIDTH", 2, 2),
        (b'id,name\n1,"unclosed', "INVALID_CSV", 2, 0),
        (b"id,name\n1,a\x00b\n", "INVALID_CELL", 2, 2),
    ],
)
def test_csv_errors_are_located_and_do_not_echo_values(data, code, row, column):
    with pytest.raises(SourceError) as error:
        parse_csv(data)
    assert (error.value.issue.code, error.value.issue.row, error.value.issue.column) == (
        code,
        row,
        column,
    )
    assert str(error.value) == code


def workbook(sheet_xml, *, extra=None):
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rels = "http://schemas.openxmlformats.org/package/2006/relationships"
    docrel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    items = {
        "[Content_Types].xml": '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" '
        'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        "</Types>",
        "_rels/.rels": f'<Relationships xmlns="{rels}"><Relationship Id="rId1" '
        f'Type="{docrel}/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": f'<workbook xmlns="{ns}" xmlns:r="{docrel}">'
        '<sheets><sheet name="设备" sheetId="1" r:id="rId1"/></sheets></workbook>',
        "xl/_rels/workbook.xml.rels": f'<Relationships xmlns="{rels}">'
        f'<Relationship Id="rId1" Type="{docrel}/worksheet" '
        'Target="worksheets/sheet1.xml"/></Relationships>',
        "xl/worksheets/sheet1.xml": f'<worksheet xmlns="{ns}"><sheetData>{sheet_xml}'
        "</sheetData></worksheet>",
    }
    items.update(extra or {})
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        for name, value in items.items():
            archive.writestr(name, value)
    return out.getvalue()


def string_cell(coordinate, text):
    return f'<c r="{coordinate}" t="inlineStr"><is><t>{escape(text)}</t></is></c>'


def header():
    return '<row r="1">' + string_cell("A1", "id") + string_cell("B1", "name") + "</row>"


def test_xlsx_real_cached_formula_and_text_key():
    pytest.importorskip("openpyxl", reason="isolated candidate probe; dependency not approved")
    data = workbook(
        header()
        + '<row r="2">'
        + string_cell("A2", "001")
        + '<c r="B2" t="str"><f>CONCAT("泵站","A")</f><v>泵站A</v></c></row>'
    )
    assert xlsx_sheets(data) == ("设备",)
    table = parse_xlsx(data, sheet="设备")
    assert [(r.number, tuple(c.text for c in r.cells)) for r in table.rows] == [
        (2, ("001", "泵站A"))
    ]
    assert table.sheet == "设备"
    with pytest.raises(SourceError, match="SHEET_NOT_FOUND"):
        parse_xlsx(data, sheet="missing")


def test_xlsx_missing_cache_is_located_not_evaluated():
    pytest.importorskip("openpyxl", reason="isolated candidate probe; dependency not approved")
    data = workbook(
        header() + '<row r="2">' + string_cell("A2", "001") + '<c r="B2"><f>1+1</f><v/></c></row>'
    )
    with pytest.raises(SourceError) as error:
        parse_xlsx(data, sheet="设备")
    assert (
        error.value.issue.code,
        error.value.issue.sheet,
        error.value.issue.row,
        error.value.issue.column,
    ) == ("FORMULA_CACHE_MISSING", "设备", 2, 2)


@pytest.mark.parametrize(
    ("extra", "code"),
    [
        ({"xl/vbaProject.bin": "macro"}, "MACRO_UNSUPPORTED"),
        ({"xl/evil.xml": '<!DOCTYPE x [<!ENTITY x "boom">]><x>&x;</x>'}, "UNSAFE_XML"),
    ],
)
def test_xlsx_rejects_macros_and_dtd_before_optional_import(extra, code):
    with pytest.raises(SourceError, match=code):
        parse_xlsx(workbook(header(), extra=extra), sheet="设备")


def test_xls_or_encrypted_ole_is_not_silently_imported():
    with pytest.raises(SourceError, match="INVALID_XLSX"):
        parse_xlsx(bytes.fromhex("d0cf11e0a1b11ae1"), sheet="设备")


def test_xlsx_sparse_empty_cells_reach_empty_policy_and_keep_row_numbers():
    pytest.importorskip("openpyxl", reason="isolated candidate probe; dependency not approved")
    data = workbook(
        header()
        + '<row r="2">'
        + string_cell("A2", "001")
        + "</row>"
        + '<row r="4">'
        + string_cell("A4", "002")
        + string_cell("B4", "B")
        + "</row>"
    )
    table = parse_xlsx(data, sheet="设备")
    assert [(row.number, tuple(c.text for c in row.cells)) for row in table.rows] == [
        (2, ("001", "")),
        (3, ("", "")),
        (4, ("002", "B")),
    ]


def test_xlsx_formula_cached_empty_string_is_valid_but_not_computed():
    pytest.importorskip("openpyxl", reason="isolated candidate probe; dependency not approved")
    data = workbook(
        header()
        + '<row r="2">'
        + string_cell("A2", "001")
        + '<c r="B2" t="str"><f>IF(1=1,"","x")</f><v></v></c></row>'
    )
    assert parse_xlsx(data, sheet="设备").rows[0].cells[1].text == ""


@pytest.mark.parametrize(
    ("data", "row", "column"),
    [
        (b'id,name,note\n1,"a,b",\xff\n', 2, 3),
        (b'id,name,note\n1,"a\n,b",\xff\n', 2, 3),
        (b'id,name,note\r\n1,"a""b,c",\xff\r\n', 2, 3),
        (b'id,name,note\n1,"a\n,b\xff', 2, 2),
    ],
)
def test_encoding_location_respects_csv_records_and_quoted_commas(data, row, column):
    with pytest.raises(SourceError) as error:
        parse_csv(data)
    assert (error.value.issue.row, error.value.issue.column) == (row, column)
