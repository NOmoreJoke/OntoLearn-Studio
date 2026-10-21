"""Complete cross-language material oracles; no parser/producer runtime claim."""

import copy
import hashlib
import json

import pytest
from test_job_store import CONTRACT

CORPUS = json.loads((CONTRACT.ROOT / "fixtures.json").read_text())["sourceTable"]
BASE = CORPUS["cases"][0]


def args(case):
    return (
        case["table"],
        case["options"],
        case["implementation"],
        case["expectedSourceHash"],
        case["maxEncodedBytes"],
    )


@pytest.mark.parametrize("case", CORPUS["cases"], ids=lambda c: c["name"])
def test_shared_complete_material(case):
    before = copy.deepcopy(case)
    if not case["valid"]:
        with pytest.raises(ValueError, match="^INVALID_REQUEST$"):
            CONTRACT.source_table_material(*args(case))
    else:
        material = CONTRACT.source_table_material(*args(case))
        assert material == case["material"].encode("utf-8")
        assert len(material) == case["encodedBytes"]
        assert hashlib.sha256(material).hexdigest() == case["sha256"]
        assert CONTRACT.source_table_digest(*args(case)) == {
            "sha256": case["sha256"],
            "encodedBytes": case["encodedBytes"],
        }
        plus = dict(case, maxEncodedBytes=case["encodedBytes"] + 1)
        assert CONTRACT.source_table_material(*args(plus)) == material
        with pytest.raises(ValueError, match="^INVALID_REQUEST$"):
            CONTRACT.source_table_material(
                *args(dict(case, maxEncodedBytes=case["encodedBytes"] - 1))
            )
    assert case == before


def test_all_encodings_identities_tail_and_empty_kind_are_bound():
    cases = CORPUS["cases"]
    encodings = [c for c in cases if c["name"].startswith("explicit encoding ")]
    assert len(encodings) == len({c["sha256"] for c in encodings}) == 5
    for name in (
        "all tail cells retained",
        "source identity changes",
        "execution semantics changes",
        "engine version changes",
        "whole lock changes",
        "physical row gaps retained",
        "field order exact",
    ):
        assert next(c["sha256"] for c in cases if c["name"] == name) != BASE["sha256"]
    assert (
        len({c["sha256"] for c in cases if c["name"].startswith("empty text distinct kind ")}) == 2
    )


def test_complete_material_larger_than_single_frame():
    case = copy.deepcopy(BASE)
    case["table"] = {
        "source_hash": "e" * 64,
        "sheet": "CSV",
        "fields": ["a", "b", "c"],
        "rows": [
            {"number": 2, "cells": [{"text": "汉" * 32768, "kind": "string"} for _ in range(3)]}
        ],
    }
    case["expectedSourceHash"] = "e" * 64
    case["maxEncodedBytes"] = CORPUS["large"]["encodedBytes"]
    material = CONTRACT.source_table_material(*args(case))
    assert len(material) == CORPUS["large"]["encodedBytes"] > 262144
    assert hashlib.sha256(material).hexdigest() == CORPUS["large"]["sha256"]


@pytest.mark.parametrize("kind", ["dict", "list", "str", "int", "key", "object"])
def test_host_subclasses_and_protocols_are_rejected_without_callbacks(kind):
    calls = []

    def called(*_):
        calls.append("called")
        raise AssertionError("host callback must not run")

    class HostDict(dict):
        __getitem__ = __iter__ = __len__ = called

    class HostList(list):
        __getitem__ = __iter__ = __len__ = called

    class HostString(str):
        __str__ = __eq__ = called
        __hash__ = str.__hash__

    class HostInt(int):
        __int__ = __eq__ = called

    class HostObject:
        __str__ = __eq__ = __iter__ = __getitem__ = called

    case = copy.deepcopy(BASE)
    if kind == "dict":
        case["table"] = HostDict(case["table"])
    elif kind == "list":
        case["table"]["rows"] = HostList(case["table"]["rows"])
    elif kind == "str":
        case["table"]["rows"][0]["cells"][0]["text"] = HostString("001")
    elif kind == "int":
        case["table"]["rows"][0]["number"] = HostInt(2)
    elif kind == "key":
        value = case["table"].pop("sheet")
        case["table"][HostString("sheet")] = value
    else:
        case["options"]["encoding"] = HostObject()
    calls.clear()
    with pytest.raises(ValueError, match="^INVALID_REQUEST$"):
        CONTRACT.source_table_material(*args(case))
    assert calls == []


def test_encoding_uses_the_captured_scalar_even_if_original_changes(monkeypatch):
    case = copy.deepcopy(BASE)
    original = CONTRACT.json.dumps
    changed = False

    def dumps(value, *a, **kw):
        nonlocal changed
        if value == "001" and not changed:
            changed = True
            case["table"]["rows"][0]["cells"][0]["text"] = "\ud800"
        return original(value, *a, **kw)

    monkeypatch.setattr(CONTRACT.json, "dumps", dumps)
    material = CONTRACT.source_table_material(*args(case))
    assert changed and hashlib.sha256(material).hexdigest() == BASE["sha256"]
    case["options"]["encoding"] = "big5"
    case["implementation"]["engineVersion"] = "caller-changed"
    assert material == BASE["material"].encode()


def test_oversized_sheet_stops_before_escape_or_encode(monkeypatch):
    case = copy.deepcopy(BASE)
    sheet = "汉" * 1_000_000
    case["table"]["sheet"] = sheet
    case["options"] = {"format": "xlsx", "encoding": None, "sheet": sheet}
    case["maxEncodedBytes"] = 400
    original = CONTRACT.json.dumps
    escaped = []

    def dumps(value, *a, **kw):
        if value is sheet:
            escaped.append(True)
        return original(value, *a, **kw)

    monkeypatch.setattr(CONTRACT.json, "dumps", dumps)
    with pytest.raises(ValueError, match="^INVALID_REQUEST$"):
        CONTRACT.source_table_material(*args(case))
    assert escaped == []


@pytest.mark.parametrize("number", [10**1000, float("nan"), float("inf"), -float("inf"), True])
def test_numbers_reject_before_overflow_or_host_conversion(number):
    case = copy.deepcopy(BASE)
    case["table"]["rows"][0]["number"] = number
    with pytest.raises(ValueError, match="^INVALID_REQUEST$"):
        CONTRACT.source_table_material(*args(case))


def test_integral_float_json_value_has_the_same_canonical_integer():
    case = copy.deepcopy(BASE)
    case["table"]["rows"][0]["number"] = 2.0
    assert CONTRACT.source_table_material(*args(case)) == BASE["material"].encode()


@pytest.mark.parametrize(
    "kind",
    ["field-count", "row-count", "text-length", "field-length", "high-surrogate", "low-surrogate"],
)
def test_limits_and_unicode_reject_without_partial_output(kind):
    case = copy.deepcopy(BASE)
    case["maxEncodedBytes"] = 2_000_000
    table = case["table"]
    if kind == "field-count":
        table["fields"] = [f"f{i}" for i in range(257)]
    elif kind == "row-count":
        table["rows"] = [table["rows"][0]] * 50001
    elif kind == "text-length":
        table["rows"][0]["cells"][0]["text"] = "x" * 32769
    elif kind == "field-length":
        table["fields"][0] = "x" * 32769
    else:
        table["rows"][0]["cells"][0]["text"] = "\ud800" if kind == "high-surrogate" else "\udfff"
    with pytest.raises(ValueError, match="^INVALID_REQUEST$"):
        CONTRACT.source_table_material(*args(case))


@pytest.mark.parametrize("name", ["fields-256", "rows-50000", "nonbmp-32768"])
def test_complete_upper_boundaries_with_fixed_independent_oracles(name):
    case = copy.deepcopy(BASE)
    table = {"source_hash": "e" * 64, "sheet": "CSV", "fields": ["v"], "rows": []}
    if name == "fields-256":
        table["fields"] = [f"f{i}" for i in range(256)]
    elif name == "rows-50000":
        table["rows"] = [
            {"number": i + 2, "cells": [{"text": str(i), "kind": "string"}]} for i in range(50000)
        ]
    else:
        table["rows"] = [{"number": 2, "cells": [{"text": "𐀀" * 32768, "kind": "string"}]}]
    case["table"] = table
    case["expectedSourceHash"] = table["source_hash"]
    oracle = CORPUS["generated"][name]
    case["maxEncodedBytes"] = oracle["encodedBytes"]
    material = CONTRACT.source_table_material(*args(case))
    assert len(material) == oracle["encodedBytes"]
    assert hashlib.sha256(material).hexdigest() == oracle["sha256"]
    with pytest.raises(ValueError, match="^INVALID_REQUEST$"):
        CONTRACT.source_table_material(*args(dict(case, maxEncodedBytes=len(material) - 1)))


@pytest.mark.parametrize("cp", CORPUS["blankFieldCodePoints"])
def test_exact_python_whitespace_field(cp):
    case = copy.deepcopy(BASE)
    case["table"]["fields"][0] = chr(cp)
    with pytest.raises(ValueError, match="^INVALID_REQUEST$"):
        CONTRACT.source_table_material(*args(case))


@pytest.mark.parametrize("case", CORPUS["budgetJsonTokens"], ids=lambda c: c["token"])
def test_shared_json_budget_value_semantics(case):
    candidate = dict(copy.deepcopy(BASE), maxEncodedBytes=json.loads(case["token"]))
    if case["valid"]:
        assert (
            hashlib.sha256(CONTRACT.source_table_material(*args(candidate))).hexdigest()
            == BASE["sha256"]
        )
    else:
        with pytest.raises(ValueError, match="^INVALID_REQUEST$"):
            CONTRACT.source_table_material(*args(candidate))


@pytest.mark.parametrize("base_type", [int, float])
def test_budget_host_subclass_cannot_execute_conversion(base_type):
    calls = []

    class Budget(base_type):
        def __int__(self):
            calls.append("convert")
            return 10000

    candidate = dict(copy.deepcopy(BASE), maxEncodedBytes=Budget(10000))
    with pytest.raises(ValueError, match="^INVALID_REQUEST$"):
        CONTRACT.source_table_material(*args(candidate))
    assert calls == []
