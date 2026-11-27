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


@pytest.mark.parametrize("reference", ["cached-external-formula", "external-hyperlink"])
def test_xlsx_external_references_do_not_open_connections_or_evaluate_formulas(
    monkeypatch, reference
):
    import socket

    pytest.importorskip("openpyxl", reason="project XLSX dependency required")
    calls = []

    def forbidden(*_args, **_kwargs):
        calls.append("network-attempt")
        raise AssertionError("External reference must never initiate networking")

    for name in ("socket", "create_connection", "getaddrinfo"):
        monkeypatch.setattr(socket, name, forbidden)
    ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    formula = (
        '<c r="B2" t="str"><f>WEBSERVICE("https://example.invalid/ref")</f><v>只读已保存值</v></c>'
    )
    value = formula if reference == "cached-external-formula" else string_cell("B2", "显示文本")
    extra = {
        "xl/worksheets/_rels/sheet1.xml.rels": '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'<Relationship Id="rId1" Type="{ns}/hyperlink" '
        'Target="https://example.invalid/ref" TargetMode="External"/></Relationships>'
    }
    data = workbook(
        header() + '<row r="2">' + string_cell("A2", "001") + value + "</row>",
        extra=extra if reference == "external-hyperlink" else None,
    )
    if reference == "external-hyperlink":
        out = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(data)) as original, zipfile.ZipFile(out, "w") as archive:
            for item in original.infolist():
                content = original.read(item)
                if item.filename == "xl/worksheets/sheet1.xml":
                    links = (
                        f'<hyperlinks><hyperlink xmlns:r="{ns}" ref="B2" r:id="rId1"/>'
                        "</hyperlinks></worksheet>"
                    ).encode()
                    content = content.replace(b"</worksheet>", links)
                archive.writestr(item, content)
        data = out.getvalue()
    table = parse_xlsx(data, sheet="设备")
    expected = "只读已保存值" if reference == "cached-external-formula" else "显示文本"
    assert tuple(cell.text for cell in table.rows[0].cells) == ("001", expected)
    assert calls == []


def test_csv_file_column_cell_and_row_limits_are_enforced_with_locations():
    from ontolearn_engine.mapping.source import MAX_BYTES, MAX_CELL, MAX_COLUMNS, MAX_ROWS

    cases = (
        (b"x" * (MAX_BYTES + 1), "SOURCE_LIMIT", 0, 0),
        ((",".join(f"c{i}" for i in range(MAX_COLUMNS + 1)) + "\n").encode(), "SOURCE_LIMIT", 1, 0),
        (("id\n" + "x" * (MAX_CELL + 1) + "\n").encode(), "INVALID_CELL", 2, 1),
        (("id\n" + "x\n" * (MAX_ROWS + 1)).encode(), "SOURCE_LIMIT", MAX_ROWS + 2, 0),
    )
    for data, code, row, column in cases:
        with pytest.raises(SourceError) as error:
            parse_csv(data)
        assert (error.value.issue.code, error.value.issue.row, error.value.issue.column) == (
            code,
            row,
            column,
        )


# ---------------------------------------------------------------------------
# W4-06: real streaming decompression budgets (never trusting ZIP size headers)
# ---------------------------------------------------------------------------


def test_xlsx_over_wide_row_is_rejected_before_row_materialization():
    pytest.importorskip("openpyxl", reason="isolated candidate probe; dependency not approved")
    from ontolearn_engine.mapping.source import MAX_COLUMNS

    wide = (
        '<row r="1">'
        + "".join(string_cell(f"a{i}1", f"c{i}") for i in range(MAX_COLUMNS + 1))
        + "</row>"
    )
    with pytest.raises(SourceError, match="SOURCE_LIMIT"):
        parse_xlsx(workbook(wide), sheet="设备")


def test_xlsx_over_long_sheet_is_rejected_by_the_streaming_precheck():
    pytest.importorskip("openpyxl", reason="isolated candidate probe; dependency not approved")
    from ontolearn_engine.mapping.source import MAX_ROWS

    body = "".join(f'<row r="{number}"/>' for number in range(1, MAX_ROWS + 3))
    with pytest.raises(SourceError, match="SOURCE_LIMIT"):
        parse_xlsx(workbook(body), sheet="设备")


def test_xlsx_worksheet_decompressed_byte_budget_is_enforced():
    pytest.importorskip("openpyxl", reason="isolated candidate probe; dependency not approved")
    from ontolearn_engine.mapping.source import MAX_COLUMNS, WORKSHEET_BUDGET

    # Legal width (<=256 cells per row) but the real decompressed worksheet
    # stream exceeds its explicit budget long before the row cap is reached.
    row = '<row r="1">' + "<c/>" * MAX_COLUMNS + "</row>"
    body = row * (WORKSHEET_BUDGET // len(row) + 2)
    with pytest.raises(SourceError, match="SOURCE_LIMIT"):
        parse_xlsx(workbook(body), sheet="设备")


def test_xlsx_oversized_shared_strings_is_rejected_by_its_explicit_budget():
    pytest.importorskip("openpyxl", reason="isolated candidate probe; dependency not approved")
    from ontolearn_engine.mapping.source import SHARED_STRINGS_BUDGET

    item = "<si><t>x</t></si>"
    huge = "<sst>" + item * (SHARED_STRINGS_BUDGET // len(item) + 2) + "</sst>"
    data = workbook(header(), extra={"xl/sharedStrings.xml": huge})
    with pytest.raises(SourceError, match="SOURCE_LIMIT"):
        parse_xlsx(data, sheet="设备")


def test_xlsx_forged_zip_size_headers_cannot_smuggle_inflation():
    import struct

    # A real ~70 MB member whose local and central uncompressed-size fields
    # are forged down to 1: the header sum looks tiny, but neither CPython's
    # CRC reconciliation nor the real streaming budget lets it through.
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("xl/evil.xml", b"0" * (70 * 1024 * 1024))
    raw = bytearray(out.getvalue())

    def forge(raw, signature, member, size_at, namelen_at, name_at):
        position = 0
        while True:
            position = raw.find(signature, position)
            if position < 0:
                return
            name_length = struct.unpack_from("<H", raw, position + namelen_at)[0]
            if bytes(raw[position + name_at : position + name_at + name_length]) == member:
                struct.pack_into("<I", raw, position + size_at, 1)
            position += 4

    forge(raw, b"PK\x03\x04", b"xl/evil.xml", 22, 26, 30)
    forge(raw, b"PK\x01\x02", b"xl/evil.xml", 24, 28, 46)
    with pytest.raises(SourceError) as error:
        parse_xlsx(bytes(raw), sheet="设备")
    assert error.value.issue.code in {"SOURCE_LIMIT", "INVALID_XLSX"}


def test_xlsx_bare_internal_entity_declaration_is_unsafe_xml():
    # `<!ENTITY xxe "boom">` with no DOCTYPE wrapper and no trailing ">" right
    # after the keyword: the exact real declaration form must still match the
    # forbidden-markup scan (a token with a trailing ">" would miss it).
    with pytest.raises(SourceError) as error:
        parse_xlsx(
            workbook(header(), extra={"xl/evil.xml": '<x><!ENTITY xxe "boom">&xxe;</x>'}),
            sheet="设备",
        )
    assert error.value.issue.code == "UNSAFE_XML"


def test_xlsx_entity_declaration_split_across_drain_chunks_is_unsafe_xml():
    # The UTF-32LE "<!ENTITY" keyword itself straddles the 64 KiB drain
    # boundary (7 of its 8 chars = 28 raw bytes close chunk one), so neither
    # chunk matches alone and only the widened 64-byte carry -- which still
    # holds the leading "<!" -- reassembles it. The old 16-byte carry kept
    # only the trailing 4 chars and would let the declaration through.
    from ontolearn_engine.mapping.source import FORBIDDEN_MARKUP

    token = '<!ENTITY xxe "boom">'.encode("utf-32-le")
    padding = 65536 - 28  # one STORED chunk ends inside the keyword
    member = b"\x00" * padding + token
    assert member.find(FORBIDDEN_MARKUP[1]) < 0  # raw bytes alone never match
    data = workbook(header(), extra={"xl/evil2.xml": member})
    with pytest.raises(SourceError) as error:
        parse_xlsx(data, sheet="设备")
    assert error.value.issue.code == "UNSAFE_XML"
