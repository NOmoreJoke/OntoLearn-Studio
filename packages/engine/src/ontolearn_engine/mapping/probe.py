"""Synthetic, real-parser candidate probe for dependency/packaging owners.

`python -m ontolearn_engine.mapping.probe` fails if candidate XLSX dependencies
are absent. This is not a registered business capability or production input.
"""

import io
import json

from ontolearn_engine.mapping.plan import Binding, Mapping, preview
from ontolearn_engine.mapping.source import parse_csv, parse_xlsx, xlsx_sheets


def run() -> dict:
    from openpyxl import Workbook

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
    out = io.BytesIO()
    book.save(out)
    book.close()
    xlsx_data = out.getvalue()
    assert xlsx_sheets(xlsx_data) == ("设备", "不能默认读取")
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
        assert result.ready and set(result.added) == expected
        assert [row.cells[0].text for row in table.rows] == ["001", "002"]
        assert [row.number for row in table.rows] == [2, 3]
    return {
        "probe": "T03-real-csv-xlsx",
        "scope": "synthetic-parser-only",
        "csv": "passed",
        "xlsx": "passed",
        "exactFacts": sorted(expected),
        "packagedProduct": False,
    }


def main() -> None:
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
