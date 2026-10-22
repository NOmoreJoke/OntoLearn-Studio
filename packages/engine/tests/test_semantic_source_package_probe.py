"""Private source/package probe contract tests, written before runtime admission.

No test below is a native process, hard-timeout, physical-memory or Store proof.
Canonical integration requires the real adopted resources; there is no skip or
fake resource/graph/production fallback. This authoring window only AST-parses
this source. The future authorized pytest run must preserve failures separately.
"""

import ast
import base64
import copy
import hashlib
import io
import json
import signal
import sys
from functools import wraps
from pathlib import Path

import pytest

REPOSITORY = Path(__file__).resolve().parents[3]
PROBE_SOURCE = (
    REPOSITORY / "packages/engine/src/ontolearn_engine/semantic_source_package_probe.py"
)
FLAG = "--semantic-source-package-probe"
SELECTORS = ("full-v1", "b1-semantic-1x-v1", "b1-semantic-10x-v1")
RESOURCE_PINS = {
    "python/contract_v2.py": (
        34608,
        "17aa68bc2271b45ffb70a023b9db9e441bb1b4e79fc9a42bb6932f60631be7b7",
    ),
    "v2/schema.json": (
        207256,
        "e913138e6f3ac632268ae7f8c2461577022e8298d1c03e0668416a0d654eaabf",
    ),
    "v2/registry.json": (
        15962,
        "1f2e298209e238433c02864a05c70b24482e4c1fd00e7309f63eac84a1f3706b",
    ),
    "v2/errors.json": (
        16299,
        "ad242d93ced7a0c8a463b708b7a1f3105e65f03c3980e0a0c6c4309f8c26544c",
    ),
}
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
XSD = "http://www.w3.org/2001/XMLSchema#"
SH = "http://www.w3.org/ns/shacl#"
PREFIX = (
    "@prefix ex: <urn:probe-test:> .\n"
    f"@prefix xsd: <{XSD}> .\n"
    f"@prefix sh: <{SH}> .\n"
)


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _canonical(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def _asset_canonical(value):
    # The sealed input digest domain preserves escaped lone-surrogate negatives.
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


@pytest.fixture(scope="module")
def probe():
    # This import is for the future authorized pytest run, not author-time load.
    from ontolearn_engine import semantic_source_package_probe

    return semantic_source_package_probe


@pytest.mark.parametrize("selector", SELECTORS)
def test_three_exact_argv(probe, selector):
    assert probe.parse_argv([FLAG, selector]) == selector


@pytest.mark.parametrize(
    "argv",
    [
        [], [FLAG], ["full-v1"], [FLAG, "unknown"], [FLAG, "FULL-V1"],
        [FLAG + "=full-v1"], [FLAG, "full-v1", "extra"],
        [FLAG, "full-v1", FLAG, "full-v1"], [FLAG, "../full-v1"],
        [FLAG, "/tmp/input.json"], [FLAG, "https://example.invalid/input"],
        ["--semantic-profile-probe", "full-v1"], [FLAG, "full-v1\x00"],
        (FLAG, "full-v1"), FLAG + " full-v1", None, True,
    ],
)
def test_argv_rejects_nonliteral_shapes_before_loading(probe, argv):
    with pytest.raises(probe.ProbeFault):
        probe.parse_argv(argv)


def test_argv_rejects_subclass_carriers_even_when_values_compare_equal(probe):
    class ForeignText(str):
        pass

    class ForeignList(list):
        pass

    for value in (
        [ForeignText(FLAG), "full-v1"], [FLAG, ForeignText("full-v1")],
        ForeignList([FLAG, "full-v1"]),
    ):
        with pytest.raises(probe.ProbeFault):
            probe.parse_argv(value)


@pytest.mark.parametrize("selector", SELECTORS)
def test_main_strict_dispatch_harness_only(probe, monkeypatch, selector):
    calls = []

    def boundary(selected, **kwargs):
        calls.append((selected, kwargs))
        return 17

    monkeypatch.setattr(probe, "run_fixed_suite", boundary)
    assert probe.main([FLAG, selector]) == 17
    assert len(calls) == 1 and calls[0][0] == selector
    assert set(calls[0][1]) <= {"cancel_requested"}
    if "cancel_requested" in calls[0][1]:
        assert callable(calls[0][1]["cancel_requested"])


def test_main_invalid_argv_never_starts_suite(probe, monkeypatch, capsys):
    def forbidden(*args, **kwargs):
        raise AssertionError("invalid argv reached the suite")

    monkeypatch.setattr(probe, "run_fixed_suite", forbidden)
    assert probe.main([FLAG, "full-v1", "/tmp/other.json"]) == 2
    output = capsys.readouterr()
    assert not output.out
    assert "/tmp/other.json" not in output.err


def test_main_none_uses_actual_argv_and_no_environment_case_override(probe, monkeypatch):
    calls = []
    monkeypatch.setattr(sys, "argv", ["probe", FLAG, "b1-semantic-1x-v1"])
    monkeypatch.setenv("I05_CASE_SET", "full-v1")
    monkeypatch.setenv("I05_PROBE_INPUT", "/tmp/unsealed.json")
    monkeypatch.setattr(
        probe, "run_fixed_suite", lambda selected, **kwargs: calls.append(selected) or 0
    )
    assert probe.main() == 0
    assert calls == ["b1-semantic-1x-v1"]


def test_main_signal_request_is_only_a_flag_and_handlers_are_restored(probe, monkeypatch):
    previous = {number: signal.getsignal(number) for number in (signal.SIGINT, signal.SIGTERM)}

    def boundary(selected, *, cancel_requested):
        assert not cancel_requested()
        handler = signal.getsignal(signal.SIGINT)
        assert callable(handler)
        handler(signal.SIGINT, None)  # Direct handler call; no OS signal/process.
        assert cancel_requested()
        return 130

    monkeypatch.setattr(probe, "run_fixed_suite", boundary)
    assert probe.main([FLAG, "full-v1"]) == 130
    assert {number: signal.getsignal(number) for number in previous} == previous


def test_locators_are_module_relative_or_bundle_only(probe, monkeypatch, tmp_path):
    source = tmp_path / "checkout/src/ontolearn_engine/semantic_source_package_probe.py"
    monkeypatch.setattr(probe, "__file__", str(source))
    monkeypatch.delattr(sys, "frozen", raising=False)
    manifest, inputs = probe.asset_paths()
    assert manifest == source.parent / "probe_inputs/i05-source-package-parity-manifest.json"
    assert inputs == source.parent / "probe_inputs/i05-source-package-parity-inputs.json"
    bundle = tmp_path / "bundle"
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(bundle), raising=False)
    manifest, inputs = probe.asset_paths()
    expected = bundle / "provenance/i05/source-package-parity"
    assert manifest == expected / "i05-source-package-parity-manifest.json"
    assert inputs == expected / "i05-source-package-parity-inputs.json"


def test_missing_sealed_manifest_has_no_checkout_or_cwd_fallback(probe, monkeypatch, tmp_path):
    paths = []
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path / "absent-bundle"), raising=False)
    expected, _ = probe.asset_paths()

    def missing(path, cap):
        paths.append(Path(path))
        raise probe.ProbeFault("ASSET_UNAVAILABLE")

    monkeypatch.setattr(probe, "read_bounded", missing)
    with pytest.raises(probe.ProbeFault):
        probe.load_assets()
    assert paths == [expected]


def test_bounded_reader_requests_cap_plus_one_and_never_decodes(probe, monkeypatch, tmp_path):
    reads = []

    class Tracked(io.BytesIO):
        def read(self, size=-1):
            reads.append(size)
            assert size >= 0, "unbounded read"
            return super().read(size)

    def opened(path, mode="r", *args, **kwargs):
        assert mode == "rb"
        return Tracked(b"\xff" * 18)

    def decoded(*args):
        raise AssertionError("oversize bytes reached decoder")

    monkeypatch.setattr(Path, "open", opened)
    monkeypatch.setattr(probe, "strict_json", decoded)
    with pytest.raises(probe.ProbeFault):
        probe.read_bounded(tmp_path / "asset", 17)
    assert reads == [18]


def test_bounded_reader_accepts_exact_cap_without_text_normalization(probe, tmp_path):
    path = tmp_path / "asset"
    path.write_bytes(b"\xff\x00\r\n")
    assert probe.read_bounded(path, 4) == b"\xff\x00\r\n"


def test_bounded_reader_real_missing_path_is_safely_classified(probe, tmp_path):
    with pytest.raises(probe.ProbeFault) as error:
        probe.read_bounded(tmp_path / "private-unapproved-missing", 10)
    assert error.value.code == "ASSET_UNAVAILABLE"
    assert "private-unapproved" not in str(error.value)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"x":1,"x":2}', b'{"x":{"y":1,"y":2}}', b'{"x":NaN}',
        b'{"x":Infinity}', b'{"x":-Infinity}', b'{"x":1e999}', b'\xef\xbb\xbf{}',
        b'\xff', b'{} trailing',
    ],
)
def test_strict_json_rejects_ambiguous_or_non_unicode_input(probe, raw):
    with pytest.raises(probe.ProbeFault):
        probe.strict_json(raw)


def test_strict_json_preserves_exact_lexical_strings_and_false(probe):
    assert probe.strict_json(b'{"v":"01","u":"\\u4e2d","f":false}') == {
        "v": "01", "u": "中", "f": False
    }
    assert probe.strict_json(b'{"x":"\\ud800"}') == {"x": "\ud800"}


def test_descriptor_identity_is_checked_before_json_decoding(probe, monkeypatch):
    manifest_path, _ = probe.asset_paths()
    original = probe.read_bounded
    decoder_calls = []

    def wrong_digest(path, cap):
        raw = original(path, cap)
        return bytes([raw[0] ^ 1]) + raw[1:] if Path(path) == manifest_path else raw

    def must_not_decode(raw):
        decoder_calls.append(raw)
        raise AssertionError("unsealed descriptor reached JSON decoder")

    monkeypatch.setattr(probe, "read_bounded", wrong_digest)
    monkeypatch.setattr(probe, "strict_json", must_not_decode)
    with pytest.raises(probe.ProbeFault):
        probe.load_assets()
    assert not decoder_calls


def test_input_identity_is_checked_before_its_json_decode(probe, monkeypatch):
    _, input_path = probe.asset_paths()
    original_read, original_decode = probe.read_bounded, probe.strict_json
    decoder_calls = []

    def wrong_digest(path, cap):
        raw = original_read(path, cap)
        return bytes([raw[0] ^ 1]) + raw[1:] if Path(path) == input_path else raw

    def observed_decode(raw):
        decoder_calls.append(raw)
        return original_decode(raw)

    monkeypatch.setattr(probe, "read_bounded", wrong_digest)
    monkeypatch.setattr(probe, "strict_json", observed_decode)
    with pytest.raises(probe.ProbeFault):
        probe.load_assets()
    assert len(decoder_calls) == 1, "only the sealed descriptor may be decoded"


@pytest.fixture(scope="module")
def sealed_assets(probe):
    inputs, manifest = probe.load_assets()
    assert probe.validate_assets(manifest, inputs) is None
    return inputs, manifest


@pytest.mark.parametrize("area", ["input", "manifest", "observation", "inputAsset"])
def test_asset_exact_schemas_reject_extra_keys(probe, sealed_assets, area):
    inputs, manifest = copy.deepcopy(sealed_assets)
    targets = {
        "input": inputs, "manifest": manifest, "observation": inputs["observations"][0],
        "inputAsset": manifest["inputAsset"],
    }
    targets[area]["unapproved"] = 1
    with pytest.raises(probe.ProbeFault):
        probe.validate_assets(manifest, inputs)


@pytest.mark.parametrize("kind", ["duplicate-id", "missing-dataset", "wrong-projection"])
def test_asset_identity_links_reject_invalid_values(probe, sealed_assets, kind):
    inputs, manifest = copy.deepcopy(sealed_assets)
    if kind == "duplicate-id":
        inputs["observations"][1]["id"] = inputs["observations"][0]["id"]
    elif kind == "missing-dataset":
        inputs["observations"][0]["datasetId"] = "not-a-sealed-dataset"
    else:
        inputs["observations"][0]["projectionSha256"] = "0" * 64
    with pytest.raises(probe.ProbeFault):
        probe.validate_assets(manifest, inputs)


@pytest.mark.parametrize(
    "kind", ["extra-selector", "duplicate-member", "unknown-member", "missing-member"]
)
def test_asset_case_sets_are_complete_unique_closed_ordered_inventory(probe, sealed_assets, kind):
    inputs, manifest = copy.deepcopy(sealed_assets)
    sets = manifest["caseSets"]
    if kind == "extra-selector":
        sets["arbitrary"] = []
    elif kind == "duplicate-member":
        sets["full-v1"].append(sets["full-v1"][0])
    elif kind == "unknown-member":
        sets["full-v1"][0] = "not-a-case"
    else:
        sets["full-v1"].pop()
    with pytest.raises(probe.ProbeFault):
        probe.validate_assets(manifest, inputs)


@pytest.mark.parametrize("kind", ["count", "full-order", "context-authority", "case-cap"])
def test_asset_tally_order_and_nonclaims_cannot_be_silently_rewritten(probe, sealed_assets, kind):
    inputs, manifest = copy.deepcopy(sealed_assets)
    if kind == "count":
        manifest["counts"]["observations"] += 1
    elif kind == "full-order":
        manifest["caseSets"]["full-v1"].reverse()
    elif kind == "context-authority":
        inputs["contexts"]["mathInputContexts"][0]["sourceAuthorityAuthenticated"] = True
    else:
        first = inputs["observations"][0]
        inputs["observations"] = [dict(first, id=f"oversize/{index}") for index in range(513)]
    with pytest.raises(probe.ProbeFault):
        probe.validate_assets(manifest, inputs)


def test_input_asset_manifest_pins_actual_bytes(probe, sealed_assets):
    inputs, manifest = sealed_assets
    _, path = probe.asset_paths()
    raw = path.read_bytes()
    assert manifest["inputAsset"] == {"bytes": len(raw), "sha256": _sha(raw)}
    assert set(inputs) == {"format", "datasets", "observations", "contexts"}
    assert set(manifest) == {"format", "inputAsset", "counts", "caseSets", "sources", "versions"}
    assert set(manifest["caseSets"]) == set(SELECTORS)
    assert len(inputs["observations"]) <= 512
    for item in inputs["observations"]:
        assert item["projectionSha256"] == _sha(
            _asset_canonical(inputs["datasets"][item["datasetId"]])
        )


def test_descriptor_pin_is_frozen_in_module_and_not_derived_from_runtime_asset(probe):
    path, _ = probe.asset_paths()
    raw = path.read_bytes()
    assert probe.MANIFEST_BYTES == len(raw)
    assert probe.MANIFEST_SHA256 == _sha(raw)
    assert len(probe.SUPPLIER_PINS) == 22
    assert len({row[0] for row in probe.SUPPLIER_PINS}) == 22
    assert len({row[1] for row in probe.SUPPLIER_PINS}) == 22
    tree = ast.parse(PROBE_SOURCE.read_text(encoding="utf-8"))
    assignments = {
        target.id: node.value for node in tree.body if isinstance(node, ast.Assign)
        for target in node.targets if isinstance(target, ast.Name)
    }
    assert ast.literal_eval(assignments["MANIFEST_BYTES"]) == len(raw)
    assert ast.literal_eval(assignments["MANIFEST_SHA256"]) == _sha(raw)
    assert ast.literal_eval(assignments["SUPPLIER_PINS"]) == probe.SUPPLIER_PINS


def test_runtime_preconditions_require_actual_adopted_pins(probe, real_resources):
    identity = probe.check_runtime_preconditions()
    assert identity["frozen"] is False
    assert len(identity["sourceModules"]) == 22
    assert len({row["module"] for row in identity["sourceModules"]}) == 22
    assert identity["packageCodeBoundToSource"] == "source-bytes-verified"
    assert identity["externalBuildProvenance"] == "unknown"
    assert len(identity["resources"]) == 4
    for relative, expected in RESOURCE_PINS.items():
        row = next(row for row in identity["resources"]
                   if Path(row["path"]) == real_resources / relative)
        assert (row["bytes"], row["sha256"]) == expected
    assert identity["distributions"] == {
        "rdflib": "7.6.0", "pyshacl": "0.30.1", "pyparsing": "3.3.3", "owlrl": "7.6.2",
        "prettytable": "3.18.0", "wcwidth": "0.9.2", "html5rdf": "1.2.1", "packaging": "26.3",
    }


@pytest.mark.parametrize("failure", ["missing", "wrong-bytes"])
def test_runtime_preconditions_reject_missing_or_wrong_supplier(probe, monkeypatch, failure):
    original = probe.read_bounded

    def rejected(path, cap):
        if Path(path).name == "contract_v2.py":
            if failure == "missing":
                raise probe.ProbeFault("ASSET_UNAVAILABLE")
            return b"# wrong resource\n"
        return original(path, cap)

    monkeypatch.setattr(probe, "read_bounded", rejected)
    with pytest.raises(probe.ProbeFault):
        probe.check_runtime_preconditions()


def _jsonl(raw):
    """External test reader rejects half-lines; it never repairs captured bytes."""
    assert not raw or raw.endswith(b"\n"), "incomplete captured JSONL line"
    return [json.loads(line) for line in raw.splitlines()]


def test_jsonl_complete_unicode_and_tail_fields(probe):
    stream = io.BytesIO()
    writer = probe.JSONLWriter(stream, total_cap=10000, item_cap=9000, reserve=500)
    value = {"type": "observation", "id": "unicode-tail", "rows": [["中文"]] * 30,
             "tail": {"source": "last", "raw": "\\\"\n"}}
    writer.emit(value)
    writer.emit({"type": "terminal", "collectionComplete": True}, terminal=True)
    assert _jsonl(stream.getvalue()) == [value, {"type": "terminal", "collectionComplete": True}]


def test_jsonl_rejects_item_before_any_partial_write(probe):
    stream = io.BytesIO()
    writer = probe.JSONLWriter(stream, total_cap=1000, item_cap=40, reserve=100)
    with pytest.raises(probe.ProbeFault):
        writer.emit({"type": "observation", "source": "中" * 40, "tail": "last"})
    assert stream.getvalue() == b""


def test_jsonl_exact_encoded_byte_cap_includes_newline(probe):
    value = {"type": "observation", "id": "exact", "v": "中"}
    encoded = _asset_canonical(value) + b"\n"
    stream = io.BytesIO()
    writer = probe.JSONLWriter(
        stream, total_cap=len(encoded) + 100, item_cap=len(encoded), reserve=100
    )
    writer.emit(value)
    assert stream.getvalue() == encoded
    too_small = io.BytesIO()
    writer = probe.JSONLWriter(
        too_small, total_cap=1000, item_cap=len(encoded) - 1, reserve=100
    )
    with pytest.raises(probe.ProbeFault) as error:
        writer.emit(value)
    assert error.value.code == "OUTPUT_ITEM_LIMIT"
    assert too_small.getvalue() == b""


def test_jsonl_total_cap_preserves_terminal_reservation_and_complete_prior_items(probe):
    stream = io.BytesIO()
    writer = probe.JSONLWriter(stream, total_cap=400, item_cap=300, reserve=180)
    first = {"type": "observation", "id": "first", "v": "x" * 110}
    writer.emit(first)
    before = stream.getvalue()
    with pytest.raises(probe.ProbeFault):
        writer.emit({"type": "observation", "id": "second", "v": "x" * 110})
    assert stream.getvalue() == before
    terminal = {"type": "terminal", "collectionComplete": False, "completedIds": ["first"],
                "unstartedIds": ["second"], "state": "failed"}
    writer.emit(terminal, terminal=True)
    assert len(stream.getvalue()) <= 400
    assert _jsonl(stream.getvalue()) == [first, terminal]


def test_jsonl_only_one_terminal_and_no_post_terminal_output(probe):
    stream = io.BytesIO()
    writer = probe.JSONLWriter(stream, total_cap=1000, item_cap=900, reserve=100)
    writer.emit({"type": "terminal", "collectionComplete": False}, terminal=True)
    saved = stream.getvalue()
    for terminal in (False, True):
        with pytest.raises(probe.ProbeFault) as error:
            writer.emit({"type": "terminal"}, terminal=terminal)
        assert error.value.code == "OUTPUT_STATE_INVALID"
        assert stream.getvalue() == saved


def test_jsonl_nonfinite_or_unserializable_output_never_partially_emits(probe):
    for value in ({"result": float("nan")}, {"result": object()}):
        stream = io.BytesIO()
        writer = probe.JSONLWriter(stream, total_cap=1000, item_cap=900, reserve=100)
        with pytest.raises(probe.ProbeFault):
            writer.emit(value)
        assert stream.getvalue() == b""


def test_jsonl_transport_failure_keeps_actual_half_line_as_incomplete(probe):
    class BrokenTransport(io.BytesIO):
        def write(self, raw):
            super().write(raw[: len(raw) // 2])
            raise BrokenPipeError("sensitive transport detail")

    stream = BrokenTransport()
    writer = probe.JSONLWriter(stream, total_cap=1000, item_cap=900, reserve=100)
    with pytest.raises((probe.ProbeFault, BrokenPipeError)):
        writer.emit({"type": "observation", "id": "unfinished", "result": [1, 2, 3]})
    raw = stream.getvalue()
    assert raw and not raw.endswith(b"\n")
    with pytest.raises(AssertionError, match="incomplete"):
        _jsonl(raw)
    assert b'"type":"terminal"' not in raw


def test_jsonl_partial_integer_writes_are_completed_without_duplicate_bytes(probe):
    class SlowTransport(io.BytesIO):
        def write(self, raw):
            return super().write(raw[:7])

    stream = SlowTransport()
    item = {"type": "observation", "id": "short-writes", "result": list(range(30))}
    probe.JSONLWriter(stream, total_cap=1000, item_cap=900, reserve=100).emit(item)
    assert _jsonl(stream.getvalue()) == [item]


@pytest.mark.parametrize("return_value", [None, 0, -1])
def test_jsonl_no_progress_is_a_harness_failure_not_success(probe, return_value):
    class NoProgress(io.BytesIO):
        def write(self, raw):
            return return_value

    stream = NoProgress()
    writer = probe.JSONLWriter(stream, total_cap=1000, item_cap=900, reserve=100)
    with pytest.raises(probe.ProbeFault) as error:
        writer.emit({"type": "observation", "id": "no-progress"})
    assert error.value.code == "OUTPUT_WRITE_FAILED"
    assert stream.getvalue() == b""


def _walk_json(value, path=()):
    if type(value) is dict:
        yield path, value
        for key, child in value.items():
            yield from _walk_json(child, path + (key,))
    elif type(value) is list:
        for index, child in enumerate(value):
            yield from _walk_json(child, path + (index,))


def test_inputs_retain_definition_heads_but_contain_no_computed_oracle(probe, sealed_assets):
    inputs, manifest = sealed_assets
    before = _asset_canonical(inputs)
    definitions_with_heads = []
    forbidden = {
        "expected", "expectedReport", "expectedRows", "given_binding", "input_binding",
        "matches", "originalMatches", "closure", "native_result", "native_reason",
        "firingGroups", "mechanismBatches", "proofLeaves", "directSteps", "rdfsEvidence",
        "payload_json", "rows_json", "allocation", "expectation",
    }
    for path, record in _walk_json(inputs["datasets"]):
        assert not (set(record) & forbidden), path
        if "heads" in record:
            assert "when" in record, path
            assert type(record["heads"]) is list, path
            definitions_with_heads.append(path)
    assert definitions_with_heads, "the original rule heads must remain actual inputs"
    probe.validate_assets(manifest, inputs)
    assert _asset_canonical(inputs) == before, "validation mutated the rule definitions"


@pytest.mark.parametrize(
    "forbidden", ["computedHeads", "native_reason", "expectation", "allocation"]
)
def test_computed_material_cannot_be_injected_as_input(probe, sealed_assets, forbidden):
    inputs, manifest = copy.deepcopy(sealed_assets)
    first = next(iter(inputs["datasets"].values()))
    first[forbidden] = []
    with pytest.raises(probe.ProbeFault):
        probe.validate_assets(manifest, inputs)


def test_original_context_denominators_do_not_become_operation_passes(sealed_assets):
    inputs, _ = sealed_assets
    contexts = inputs["contexts"]
    assert set(contexts) == {
        "mathInputContexts", "originalOperations", "productCases", "learningChecks",
        "unresolved", "nonClaims",
    }
    math = contexts["mathInputContexts"]
    assert len(math) == 83
    assert len({item["id"] for item in math}) == 83
    assert [item["index"] for item in math] == list(range(83))
    assert sum(item["eligibleStandaloneMathInput"] for item in math) == 82
    assert sum(item["fullOriginalInputContext"] for item in math) == 79
    assert sum(item["eligibleStandaloneMathInput"] and item["fullOriginalInputContext"]
               for item in math) == 78
    assert math[77]["eligibleStandaloneMathInput"] is False
    assert math[77]["fullOriginalInputContext"] is True
    fragments = [item for item in math if not item["fullOriginalInputContext"]]
    assert len(fragments) == 4
    assert [(item["index"], item["id"]) for item in fragments] == [
        (79, "E.5:event-fragment:round:1"), (80, "E.5:event-fragment:round:2"),
        (81, "E.5:event-fragment:round:3"), (82, "E.5:event-fragment:round:4"),
    ]
    assert all(item["eligibleStandaloneMathInput"] for item in fragments)
    for item in math:
        assert item["sourceRefs"]
        assert len(item["inputProjectionJsonSha256"]) == 64
        assert item["lifecycleExecuted"] is False
        assert item["originalRequestedOperationPassed"] is False
        assert item["sourceAuthorityAuthenticated"] is False
    assert len(contexts["originalOperations"]) == 106
    assert len(contexts["learningChecks"]) == 54
    assert len(contexts["productCases"]) == 50
    assert len({item["id"] for item in contexts["originalOperations"]}) == 106
    assert all(item["originalOperationExecuted"] is False and item["lifecycleExecuted"] is False
               for item in contexts["originalOperations"])
    assert all(item["checkExecuted"] is False for item in contexts["learningChecks"])
    assert all(item["originalLifecycleAndNonGraphAcceptance"] == "not-executed"
               for item in contexts["productCases"])
    for group in ("originalOperations", "learningChecks", "productCases"):
        assert all(item["source"]["pointer"] for item in contexts[group])
    assert contexts["unresolved"] and contexts["nonClaims"]


def test_consumer_c_preserves_two_queries_eleven_shapes_and_policy_variants(sealed_assets):
    inputs, _ = sealed_assets
    ids = {
        "C-query-numeric-promotion", "C-query-type-error", "C-datatype-exact", "C-langString",
        "C-count-term-identity", "C-in-term-identity", "C-inclusive-numeric", "C-inclusive-nni",
        "C-inclusive-dateTime-equal", "C-inclusive-dateTime-before", "C-inclusive-type-error",
        "C-inclusive-date-entry", "C-illtyped-entry",
    }
    observations = [item for item in inputs["observations"] if item["sourceCaseId"] in ids]
    assert {item["sourceCaseId"] for item in observations} == ids
    query_ids = {item["sourceCaseId"] for item in observations if item["operation"] == "query"}
    assert query_ids == {"C-query-numeric-promotion", "C-query-type-error"}
    assert len(ids - query_ids) == 11
    date_parameters = [item["parameters"] for item in observations
                       if item["sourceCaseId"] == "C-inclusive-date-entry"]
    for data_policy in ("strict", "integer-illtyped-report-v1"):
        assert {"dataPolicy": data_policy, "rangePolicy": "utc-date-range-v1"} in date_parameters
    integer_parameters = [item["parameters"] for item in observations
                          if item["sourceCaseId"] == "C-illtyped-entry"]
    assert {"dataPolicy": "strict", "rangePolicy": "legacy"} in integer_parameters
    assert {
        "dataPolicy": "integer-illtyped-report-v1", "rangePolicy": "legacy"
    } in integer_parameters


def test_case_sets_select_only_their_own_b1_pure_inputs(sealed_assets):
    inputs, manifest = sealed_assets
    by_id = {item["id"]: item for item in inputs["observations"]}
    one = manifest["caseSets"]["b1-semantic-1x-v1"]
    ten = manifest["caseSets"]["b1-semantic-10x-v1"]
    assert one and ten and set(one).isdisjoint(ten)
    for members in (one, ten):
        for case_id in members:
            item = by_id[case_id]
            assert item["operation"] == "b1-measurement"
            assert item["parameters"] == {}
            dataset = inputs["datasets"][item["datasetId"]]
            assert not any(key in {"snapshot", "snapshotLoad", "Store", "sqlite"}
                           for _, record in _walk_json(dataset) for key in record)
            assert dataset["seed"] == 20261019
            assert _sha(dataset["queryText"].encode()) == (
                "7879b25f2833b8e485b53d3f6664220836ada716ec29ae7de82f907eae014ab5"
            )
            expected_input_digest = {
                1: "b0bcc466774f37d4f6a520900b8e7caa5f4fb7f827bbcf8c5ad0e9d12946ea0c",
                10: "25393c99db270c57a75cd75c675876d148659fef7e7624e4197e90754b257ed2",
            }[dataset["scale"]]
            assert _sha(dataset["assertedText"].encode()) == expected_input_digest


def test_call_counter_counts_real_code_identity_and_restores_hook(probe, canonical):
    semantic = canonical["semantic"]
    graph = semantic.parse_turtle("<urn:counter:x> a <urn:counter:A> .")
    previous = sys.getprofile()
    assert previous is None, "the probe refuses a pre-existing profiler"

    def reason(*args, **kwargs):
        # A same-name harness function is deliberately not the canonical code.
        return None

    with probe.CallCounter(semantic, semantic.Validator) as counter:
        reason()
        assert counter.counts == {"validator": 0, "reason": 0}
        alias = semantic.reason
        alias(graph)
        assert counter.counts == {"validator": 0, "reason": 1}
        semantic.validate_shacl_text(
            _data("2000-01-01Z"),
            _shape('sh:minInclusive "2000-01-01Z"^^xsd:date'),
            data_policy="strict", range_policy="utc-date-range-v1",
        )
        assert counter.counts == {"validator": 1, "reason": 1}
    assert sys.getprofile() is previous


def test_call_counter_existing_hook_fails_without_overwriting_it(probe, canonical):
    def existing(frame, event, arg):
        return None

    previous = sys.getprofile()
    sys.setprofile(existing)
    try:
        with pytest.raises(probe.ProbeFault):
            with probe.CallCounter(canonical["semantic"], canonical["semantic"].Validator):
                raise AssertionError("existing hook must fail on entry")
        assert sys.getprofile() is existing
    finally:
        sys.setprofile(previous)


def test_suite_existing_hook_stops_before_any_business_observation(probe, canonical):
    def existing(frame, event, arg):
        return None

    previous = sys.getprofile()
    stdout, stderr = io.BytesIO(), io.BytesIO()
    sys.setprofile(existing)
    try:
        status = probe.run_fixed_suite("full-v1", stdout=stdout, stderr=stderr)
        assert status != 0
        assert not any(item["type"] == "observation" for item in _jsonl(stdout.getvalue()))
        assert sys.getprofile() is existing
    finally:
        sys.setprofile(previous)


def test_call_counter_restores_hook_on_real_policy_rejection(probe, canonical):
    from ontolearn_engine.semantic_offline import SemanticError

    previous = sys.getprofile()
    with pytest.raises(SemanticError):
        with probe.CallCounter(canonical["semantic"], canonical["semantic"].Validator) as counter:
            canonical["semantic"].validate_shacl_text(
                _data("2000-01-01Z"), _shape("sh:minCount 1"),
                data_policy="not-a-policy", range_policy="legacy",
            )
    assert counter.counts == {"validator": 0, "reason": 0}
    assert sys.getprofile() is previous


def test_scope_counts_real_prepare_and_project_as_separate_stages(probe, canonical):
    semantic, scopes = canonical["semantic"], canonical["scopes"]
    facts = semantic.parse_turtle("<urn:counter:x> a <urn:counter:A> .")
    axioms = semantic.parse_turtle(f"<urn:counter:A> <{RDFS}subClassOf> <urn:counter:B> .")
    with probe.CallCounter(semantic, semantic.Validator) as prepared_count:
        prepared = scopes.prepare_validation_scope(facts, axioms, include_derived=True)
    assert prepared_count.counts == {"validator": 0, "reason": 1}
    with probe.CallCounter(semantic, semantic.Validator) as project_count:
        projected = scopes.project_validation_scope(
            facts, axioms, include_derived=True, reasoning_result=prepared.reasoning_result,
            reasoning_source=prepared.provenance["reasoningSource"],
        )
    assert project_count.counts == {"validator": 0, "reason": 0}
    assert projected.reasoning_result is prepared.reasoning_result


def test_source_main_guard_precedes_types_and_calls_canonical_main_only():
    tree = ast.parse(PROBE_SOURCE.read_text(encoding="utf-8"))
    guards = [node for node in tree.body if isinstance(node, ast.If)
              and any(isinstance(n, ast.Constant) and n.value == "__main__"
                      for n in ast.walk(node.test))]
    assert len(guards) == 1
    guard = guards[0]
    definitions = [node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef))]
    assert definitions and guard.lineno < min(node.lineno for node in definitions)
    imports = [node for node in ast.walk(guard) if isinstance(node, ast.ImportFrom)]
    assert any(node.module == "ontolearn_engine.semantic_source_package_probe"
               and any(alias.name == "main" for alias in node.names) for node in imports)
    assert any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
               and node.func.id == "SystemExit" for node in ast.walk(guard))
    assert not any(isinstance(node, (ast.ClassDef, ast.FunctionDef)) for node in ast.walk(guard))


def test_imported_probe_classes_have_only_canonical_module_identity(probe):
    name = "ontolearn_engine.semantic_source_package_probe"
    assert probe.__name__ == name
    assert probe.__spec__.name == name
    assert sys.modules[name] is probe
    for value in (probe.ProbeFault, probe.JSONLWriter, probe.CallCounter):
        assert value.__module__ == name
    assert probe is not sys.modules.get("__main__")


def test_probe_does_not_import_old_runtime_store_or_observation_helpers():
    tree = ast.parse(PROBE_SOURCE.read_text(encoding="utf-8"))
    forbidden = {"semantic_samples", "semantic_probe", "semantic_profile_probe", "storage_probe",
                 "storage", "worker", "coordinator", "job_store", "__main__", "entrypoint"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(not (set(alias.name.split(".")) & forbidden) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert not (set((node.module or "").split(".")) & forbidden)
            assert all(alias.name not in forbidden for alias in node.names)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in {
                "resource_manifest", "build_request", "execute_request", "derive_dependencies",
                "permits_transition",
            }


@pytest.fixture(scope="module")
def full_run(probe, canonical):
    """One actual full canonical collection, shared instead of redoing the run."""
    stdout, stderr = io.BytesIO(), io.BytesIO()
    status = probe.run_fixed_suite("full-v1", stdout=stdout, stderr=stderr)
    return status, _jsonl(stdout.getvalue()), stdout.getvalue(), stderr.getvalue()


def test_full_jsonl_is_complete_inventory_not_self_signed_equivalence(full_run, sealed_assets):
    status, records, raw, stderr = full_run
    _, manifest = sealed_assets
    assert status == 0, (status, stderr)
    assert len(raw) <= 67108864
    assert records[0]["type"] == "header"
    assert records[0]["format"] == "i05-source-package-observations/1"
    assert records[-1]["type"] == "terminal"
    assert sum(item["type"] == "header" for item in records) == 1
    assert sum(item["type"] == "terminal" for item in records) == 1
    observations = records[1:-1]
    assert all(item["type"] == "observation" for item in observations)
    assert [item["id"] for item in observations] == manifest["caseSets"]["full-v1"]
    terminal = records[-1]
    assert terminal["completedIds"] == manifest["caseSets"]["full-v1"]
    assert terminal["unstartedIds"] == []
    assert terminal["selectedCaseSet"] == "full-v1"
    assert terminal["collectionComplete"] is True
    assert terminal["fullSuiteCollectionComplete"] is True
    assert terminal["externalOracleCompared"] is False
    assert terminal["originalOperationPassed"] is False


def test_full_header_records_actual_identity_and_retains_context_ledger(full_run, sealed_assets):
    _, records, _, _ = full_run
    inputs, manifest = sealed_assets
    header = records[0]
    assert type(header["runId"]) is str and header["runId"]
    assert header["mode"] == "source"
    assert header["supplierRef"] == "6891a5842302859a531cf82767c5a482417bc274"
    assert header["supplierProcessRef"] == "f79a29f596b2444cba542a906c91727869014886"
    assert header["counts"] == manifest["counts"]
    assert header["contexts"] == inputs["contexts"]
    assert header["fullInventory"] == manifest["caseSets"]["full-v1"]
    assert header["selectedInventory"] == manifest["caseSets"]["full-v1"]
    assert header["fullInventorySha256"] == _sha(
        _asset_canonical(manifest["caseSets"]["full-v1"])
    )
    assert header["selectedInventorySha256"] == header["fullInventorySha256"]
    assert header["instrumentation"] is True
    assert header["sourcePackageEquivalent"] is False
    assert header["externalOracleMatched"] is False
    identity = header["identity"]
    assert identity["probeModule"] == "ontolearn_engine.semantic_source_package_probe"
    assert identity["probeSpecName"] == "ontolearn_engine.semantic_source_package_probe"
    assert identity["externalBuildProvenance"] == "unknown"
    assert len(identity["modules"]) == 22
    for row in identity["modules"]:
        assert row["module"] == row["specName"]
        assert len(row["actualSourceSha256"]) == 64
        assert row["actualSourceSha256"] == row["declaredSupplierSourceSha256"]
        assert row["actualCode"]["domain"] == (
            "actual-loader-code; not source bytes or a build approval"
        )
        assert len(row["actualCode"]["sha256"]) == 64
    assert set(identity["functionCode"]) == {
        "semantic.reason", "semantic.query", "semantic.validate_shacl_text", "Validator.run"
    }


def test_full_observations_keep_parameters_sources_counts_and_statuses(full_run, sealed_assets):
    _, records, _, _ = full_run
    inputs, _ = sealed_assets
    declared = {item["id"]: item for item in inputs["observations"]}
    statuses = set()
    for observed in records[1:-1]:
        original = declared[observed["id"]]
        for field in (
            "sourceCaseId", "family", "operation", "datasetId", "parameters", "sourceRefs",
            "contextStatus", "projectionSha256",
        ):
            assert observed[field] == original[field], (observed["id"], field)
        assert observed["start"] <= observed["end"]
        statuses.add(observed["status"])
        assert observed["status"] in {
            "observed-return", "observed-rejection", "not-executed", "missing-context"
        }
        if observed["status"] == "observed-return":
            assert "result" in observed
            assert type(observed["callCounts"]) is dict
            assert set(observed["callCounts"]) == {"validator", "reason"}
            assert all(
                type(count) is int and count >= 0 for count in observed["callCounts"].values()
            )
        elif observed["status"] == "observed-rejection":
            assert "error" in observed and "diagnostic" in observed
            assert type(observed["callCounts"]) is dict
    assert "observed-return" in statuses
    assert "observed-rejection" in statuses
    assert statuses & {"not-executed", "missing-context"}
    repair = [item for item in records[1:-1]
              if item["sourceCaseId"] == inputs["contexts"]["mathInputContexts"][77]["id"]
              and item["operation"] == "profile"]
    assert repair and all(item["status"] in {"not-executed", "missing-context"} for item in repair)


def test_fragment_repair_shape_inputs_execute_without_upgrading_old_math77(full_run):
    _, records, _, _ = full_run
    by_id = {item["id"]: item for item in records[1:-1]}
    before, after = by_id["transfer-repair-before"], by_id["transfer-repair-after"]
    assert before["sourceCaseId"] == after["sourceCaseId"] == "transfer:repair"
    assert before["status"] == after["status"] == "observed-return"
    assert before["contextStatus"] == after["contextStatus"] == "fragment"
    assert before["callCounts"]["validator"] == after["callCounts"]["validator"] == 1
    assert before["result"]["conforms"] is False
    assert after["result"] == {"conforms": True, "violations": []}
    old_math = by_id["profile-83/transfer:repair"]
    assert old_math["status"] == "not-executed"
    assert old_math["callCounts"] == {"validator": 0, "reason": 0}


def test_missing_mandatory_policy_keywords_are_actual_call_contract_rejections(
    full_run, sealed_assets
):
    _, records, _, _ = full_run
    inputs, _ = sealed_assets
    omitted = [item for item in inputs["observations"] if item["operation"] == "shacl-text"
               and set(item["parameters"]) != {"dataPolicy", "rangePolicy"}]
    assert omitted
    by_id = {item["id"]: item for item in records[1:-1]}
    for declaration in omitted:
        observed = by_id[declaration["id"]]
        assert observed["status"] == "observed-rejection"
        assert observed["error"] == {"kind": "call-contract", "code": "CALL_ARGUMENTS_INVALID"}
        assert observed["callCounts"] == {"validator": 0, "reason": 0}


def test_full_production_bytes_are_complete_and_restore_uses_actual_capture(full_run):
    _, records, _, _ = full_run
    produced = [item for item in records[1:-1]
                if item["operation"] in {"fullview", "dag"}
                and item["status"] == "observed-return"]
    assert {item["operation"] for item in produced} == {"fullview", "dag"}
    for item in produced:
        result = item["result"]
        for field in (
            "payloadBytes", "rowsBytes", "sourceBytes", "definitionBytes", "catalogBytes"
        ):
            packet = result[field]
            assert packet["encoding"] == "base64"
            decoded = base64.b64decode(packet["data"], validate=True)
            assert packet["bytes"] == len(decoded)
            assert packet["sha256"] == _sha(decoded)
        payload = json.loads(base64.b64decode(result["payloadBytes"]["data"]))
        rows = json.loads(base64.b64decode(result["rowsBytes"]["data"]))
        assert payload == result["wire"]["payload"]
        assert rows == result["wire"]["rows"]
        assert "".join(row[0] for row in rows) == base64.b64decode(
            result["payloadBytes"]["data"]
        ).decode()
        assert result["expectedCapture"] and result["allocation"] and result["receipts"]
        assert result["restored"]
        if item["operation"] == "dag":
            assert payload["format"] == "i05-reasoning-result/3"
            assert "roots" in result


def test_full_run_b1_actual_scales_four_ontology_and_no_s1_claim(full_run):
    _, records, _, _ = full_run
    measurements = [item["result"] for item in records[1:-1]
                    if item["operation"] == "b1-measurement"
                    and item["status"] == "observed-return"]
    assert {item["scale"] for item in measurements} == {1, 10}
    for result in measurements:
        scale = result["scale"]
        assert result["seed"] == 20261019
        assert result["actualCounts"] == {
            "asserted": 18 * scale, "ontology": 4, "merged": 18 * scale + 4
        }
        for field, count in (
            ("assertedInput", 18 * scale), ("ontology", 4), ("semanticGraph", 18 * scale + 4)
        ):
            graph = result[field]
            assert len(graph["triples"]) == graph["tripleCount"] == count
            assert len({tuple(triple) for triple in graph["triples"]}) == count
        subjects = {triple[0] for triple in result["assertedInput"]["triples"]}
        for index in range(scale):
            assert f"<urn:case:{index}:equipment/001>" in subjects
            assert f"<urn:case:{index}:alarm/A01>" in subjects
        assert result["querySha256"] == (
            "7879b25f2833b8e485b53d3f6664220836ada716ec29ae7de82f907eae014ab5"
        )
        assert result["coldClaim"] is False, "full-suite execution is already warm"
        assert result["instrumentation"] is records[0]["instrumentation"]
        assert [item["name"] for item in result["passes"]] == ["First", "Warm"]
        for item in result["passes"]:
            assert "snapshotLoad" not in item["phases"]
            assert "outputs" in item and "report" in item["outputs"]
            assert "query" in item["outputs"] and "reason" in item["outputs"]


@pytest.fixture(scope="module")
def b1_selector_runs(probe, canonical):
    runs = {}
    for selector in SELECTORS[1:]:
        stdout, stderr = io.BytesIO(), io.BytesIO()
        code = probe.run_fixed_suite(selector, stdout=stdout, stderr=stderr)
        runs[selector] = code, _jsonl(stdout.getvalue()), stderr.getvalue()
    return runs


def test_b1_selectors_are_uninstrumented_subsets_without_claiming_fresh_process(
    b1_selector_runs, sealed_assets
):
    _, manifest = sealed_assets
    for selector, (code, records, stderr) in b1_selector_runs.items():
        assert code == 0, stderr
        assert [item["type"] for item in records] == ["header", "observation", "terminal"]
        header, observation, terminal = records
        inventory = manifest["caseSets"][selector]
        assert header["selectedCaseSet"] == selector
        assert header["selectedInventory"] == inventory
        assert header["fullInventory"] == manifest["caseSets"]["full-v1"]
        assert header["instrumentation"] is False
        assert observation["id"] == inventory[0]
        assert observation["operation"] == "b1-measurement"
        assert observation["status"] == "observed-return"
        assert observation["callCounts"] is None
        result = observation["result"]
        assert result["instrumentation"] is False
        assert result["freshProcessRequestedBySelector"] is True
        assert result["freshProcessExternallyVerified"] is False
        assert result["coldClaim"] is False
        assert result["snapshotLoad"] == "not-executed; Store HOLD"
        assert terminal["completedIds"] == inventory
        assert terminal["unstartedIds"] == []
        assert terminal["collectionComplete"] is True
        assert terminal["fullSuiteCollectionComplete"] is False
        assert terminal["externalOracleCompared"] is False
        # These direct library calls do not establish external fresh-process timing.


def test_restore_negative_copies_bytes_but_keeps_same_caller_capture(full_run):
    _, records, _, _ = full_run
    negatives = [item for item in records[1:-1]
                 if item["operation"] == "restore-negative"
                 and item["status"] == "observed-return"]
    assert negatives
    for observed in negatives:
        result = observed["result"]
        mutation = result["mutation"]
        assert mutation["status"] == "observed-rejection"
        assert mutation["expectedCapture"] == result["expectedCapture"]
        assert mutation["allocationReissued"] is False
        assert mutation.get("onlyOuterDigestsRebound", False) is False
        assert mutation["payloadBytes"] != result["payloadBytes"]
        assert result["restored"], "original immutable success remains complete"


def test_cancel_request_stops_new_cases_without_claiming_external_cancelled(
    probe, canonical, sealed_assets
):
    _, manifest = sealed_assets
    stdout, stderr = io.BytesIO(), io.BytesIO()
    status = probe.run_fixed_suite(
        "full-v1", stdout=stdout, stderr=stderr, cancel_requested=lambda: True
    )
    records = _jsonl(stdout.getvalue())
    terminal = records[-1]
    assert status == 130
    assert [item["type"] for item in records] == ["header", "terminal"]
    assert terminal["state"] == "stopping"
    assert terminal["collectionComplete"] is False
    assert terminal["completedIds"] == []
    assert terminal["unstartedIds"] == manifest["caseSets"]["full-v1"]
    assert terminal["state"] not in {"cancelled", "timed-out"}
    # No process, signal, reader join or actual OS stopped receipt is simulated.


def test_deadline_boundary_does_not_claim_hard_timeout_or_complete_collection(
    probe, canonical, sealed_assets
):
    _, manifest = sealed_assets
    ticks = 0

    def boundary_clock():
        nonlocal ticks
        now = ticks * 121.0
        ticks += 1
        return now

    stdout, stderr = io.BytesIO(), io.BytesIO()
    status = probe.run_fixed_suite(
        "full-v1", stdout=stdout, stderr=stderr, monotonic=boundary_clock
    )
    records = _jsonl(stdout.getvalue())
    terminal = records[-1]
    assert status == 1
    assert terminal["collectionComplete"] is False
    assert terminal["state"] not in {"cancelled", "timed-out"}
    completed, unstarted = terminal["completedIds"], terminal["unstartedIds"]
    assert completed + unstarted == manifest["caseSets"]["full-v1"]
    assert unstarted


@pytest.mark.parametrize("fault", [RuntimeError, TypeError])
def test_unknown_library_fault_is_incomplete_harness_failure_not_known_rejection(
    probe, canonical, monkeypatch, fault
):
    def unexpected(*args, **kwargs):
        raise fault("private-token/secret/path")

    # Fault injection only: no fake graph, inferred data or business return.
    monkeypatch.setattr(canonical["semantic"], "parse_turtle", unexpected)
    stdout, stderr = io.BytesIO(), io.BytesIO()
    status = probe.run_fixed_suite("b1-semantic-1x-v1", stdout=stdout, stderr=stderr)
    records = _jsonl(stdout.getvalue())
    observations = records[1:-1]
    assert status == 1
    assert observations and observations[0]["status"] == "unexpected-failure"
    assert observations[0]["status"] != "observed-rejection"
    assert records[-1]["collectionComplete"] is False
    assert b"private-token" not in stdout.getvalue() + stderr.getvalue()


def _partial_by_stage(observation):
    partial = observation["partialOutputs"]
    assert type(partial) is list
    assert len({item["stage"] for item in partial}) == len(partial)
    for item in partial:
        assert {"stage", "api", "start", "end", "value"} <= set(item)
        assert type(item["api"]) is str and item["api"]
        assert item["start"] <= item["end"]
        if "returned" in item:
            assert item["returned"] is True
        if "elapsedNs" in item:
            assert type(item["elapsedNs"]) is int and item["elapsedNs"] >= 0
    return {item["stage"]: item for item in partial}


def _failed_observation(records):
    observations = [item for item in records if item["type"] == "observation"]
    assert observations
    return observations[-1]


def test_r1_real_first_outputs_survive_warm_shacl_unknown_failure(probe, canonical, monkeypatch):
    semantic = canonical["semantic"]
    original = semantic.check_shapes
    calls = 0

    @wraps(original)
    def fail_warm(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("private-warm-shacl-detail")
        return original(*args, **kwargs)

    monkeypatch.setattr(semantic, "check_shapes", fail_warm)
    stdout, stderr = io.BytesIO(), io.BytesIO()
    code = probe.run_fixed_suite("b1-semantic-1x-v1", stdout=stdout, stderr=stderr)
    records = _jsonl(stdout.getvalue())
    failed = _failed_observation(records)
    assert code == 1 and calls == 2
    assert failed["status"] == "unexpected-failure"
    assert failed["error"]["code"] == "INTERNAL_ERROR"
    assert failed["diagnostic"]["stage"] == "Warm/shacl"
    assert failed["diagnostic"]["api"] == "semantic.check_shapes"
    assert "result" not in failed, "no complete B1 result was returned"
    partial = _partial_by_stage(failed)
    assert {"First/turtleParse", "First/ontologyParse", "First/graphBuild", "First/fixedSelect",
            "First/rdfsRules", "First/shapesParse", "First/shacl",
            "First/resultSerialization"} <= set(partial)
    assert {"Warm/turtleParse", "Warm/ontologyParse", "Warm/graphBuild", "Warm/fixedSelect",
            "Warm/rdfsRules", "Warm/shapesParse"} <= set(partial)
    assert "Warm/shacl" not in partial, "a throwing call has no returned value"
    attempts = [item for item in failed["stageAttempts"] if item["stage"] == "Warm/shacl"]
    assert len(attempts) == 1 and "value" not in attempts[0]
    assert attempts[0]["returned"] is False
    assert partial["First/fixedSelect"]["value"] == {
        "type": "SELECT", "variables": ["alarm"], "rows": [["<urn:case:0:alarm/A01>"]]
    }
    assert partial["First/shacl"]["value"] == {"conforms": True, "violations": []}
    encoded = partial["First/resultSerialization"]["value"]
    raw = base64.b64decode(encoded["data"], validate=True)
    assert encoded["bytes"] == len(raw) and encoded["sha256"] == _sha(raw)
    first_outputs = json.loads(raw)
    assert first_outputs["query"] == partial["First/fixedSelect"]["value"]
    assert first_outputs["report"] == {"conforms": True, "violations": []}
    assert first_outputs["reason"] == partial["First/rdfsRules"]["value"]
    assert first_outputs["assertedOriginal"]["tripleCount"] == 18
    assert first_outputs["ontology"]["tripleCount"] == 4
    assert first_outputs["graph"]["tripleCount"] == 22
    assert records[-1]["collectionComplete"] is False
    assert b"private-warm-shacl-detail" not in stdout.getvalue() + stderr.getvalue()


def _snapshot_has_exact_bytes(value, raw):
    return any(
        record.get("encoding") == "base64"
        and record.get("bytes") == len(raw)
        and record.get("sha256") == _sha(raw)
        and record.get("data") == base64.b64encode(raw).decode("ascii")
        for _, record in _walk_json(value)
    )


def test_r1_real_producer_capture_survives_restore_unknown_failure(probe, canonical, monkeypatch):
    production, restore = canonical["production"], canonical["restore"]
    original_compute = production.execute_profile_explanation
    original_restore = restore.restore_profile_explanation_result
    issued, received = [], []

    @wraps(original_compute)
    def real_compute(*args, **kwargs):
        produced = original_compute(*args, **kwargs)
        issued.append(produced)
        return produced

    @wraps(original_restore)
    def fail_restore(payload, rows, *, expected, allocation, **kwargs):
        received.append((payload, rows, expected, allocation))
        raise RuntimeError("private-restore-detail")

    monkeypatch.setattr(production, "execute_profile_explanation", real_compute)
    monkeypatch.setattr(restore, "restore_profile_explanation_result", fail_restore)
    stdout, stderr = io.BytesIO(), io.BytesIO()
    code = probe.run_fixed_suite("full-v1", stdout=stdout, stderr=stderr)
    records = _jsonl(stdout.getvalue())
    failed = _failed_observation(records)
    assert code == 1 and len(issued) == len(received) == 1
    produced = issued[0]
    payload, rows, expected, allocation = received[0]
    assert payload is produced.payload_json and rows is produced.rows_json
    assert allocation is produced.original_allocation
    assert expected.payload_digest == _sha(payload) and expected.rows_digest == _sha(rows)
    assert failed["status"] == "unexpected-failure"
    assert failed["error"]["code"] == "INTERNAL_ERROR"
    assert failed["diagnostic"]["stage"] == "restore/result"
    assert failed["diagnostic"]["api"] == (
        "semantic_profile_restore.restore_profile_explanation_result"
    )
    partial = _partial_by_stage(failed)
    assert {"material/prepare", "production/compute", "production/expectation"} <= set(partial)
    assert "restore/result" not in partial and "restore/roots" not in partial
    for raw in (produced.payload_json, produced.rows_json, produced.source_encoded,
                produced.definitions_encoded, produced.catalog_json):
        assert _snapshot_has_exact_bytes(partial["production/compute"]["value"], raw)
    assert any(record.get("payload_digest") == expected.payload_digest
               and record.get("rows_digest") == expected.rows_digest
               for _, record in _walk_json(partial["production/expectation"]["value"]))
    assert "result" not in failed, "a failed restore must not publish a partial restored view"
    assert records[-1]["collectionComplete"] is False
    assert b"private-restore-detail" not in stdout.getvalue() + stderr.getvalue()


@pytest.mark.parametrize("stop", ["deadline", "deadline-cumulative", "cancel"])
def test_r1_boundary_after_real_parse_prevents_next_canonical_stage(
    probe, canonical, monkeypatch, stop
):
    semantic = canonical["semantic"]
    original_parse = semantic.parse_turtle
    state = {"now": 0.0, "cancel": False, "calls": 0}

    @wraps(original_parse)
    def actual_parse_then_stop(*args, **kwargs):
        graph = original_parse(*args, **kwargs)
        state["calls"] += 1
        if stop == "deadline":
            state["now"] = 121.0
        elif stop == "deadline-cumulative":
            state["now"] = 70.0 if state["calls"] == 1 else 121.0
        else:
            state["cancel"] = True
        return graph

    monkeypatch.setattr(semantic, "parse_turtle", actual_parse_then_stop)
    stdout, stderr = io.BytesIO(), io.BytesIO()
    code = probe.run_fixed_suite(
        "b1-semantic-1x-v1", stdout=stdout, stderr=stderr,
        monotonic=lambda: state["now"], cancel_requested=lambda: state["cancel"],
    )
    records = _jsonl(stdout.getvalue())
    failed = _failed_observation(records)
    terminal = records[-1]
    expected_calls = 2 if stop == "deadline-cumulative" else 1
    assert state["calls"] == expected_calls, "no next canonical stage after the stop"
    assert code == (130 if stop == "cancel" else 1)
    assert failed["status"] != "observed-rejection"
    assert failed["diagnostic"]["classification"] != "harness-or-unknown"
    expected_stage = "First/ontologyParse" if stop == "deadline-cumulative" else "First/turtleParse"
    assert failed["diagnostic"]["stage"] == expected_stage
    assert failed["diagnostic"]["api"] == "semantic.parse_turtle"
    partial = _partial_by_stage(failed)
    expected_stages = {"First/turtleParse"}
    if stop == "deadline-cumulative":
        expected_stages.add("First/ontologyParse")
        assert partial["First/ontologyParse"]["value"]["tripleCount"] == 4
    assert set(partial) == expected_stages
    assert partial["First/turtleParse"]["value"]["tripleCount"] == 18
    assert len(partial["First/turtleParse"]["value"]["triples"]) == 18
    assert terminal["collectionComplete"] is False
    assert terminal["state"] == ("stopping" if stop == "cancel" else "deadline-boundary")
    assert terminal.get("externalProcessStopped", "unknown") == "unknown"
    assert terminal.get("readerJoin", "unknown") == "unknown"


def test_r1_preflight_elapsed_time_counts_before_first_business_call(
    probe, canonical, monkeypatch
):
    original_preflight = probe.check_runtime_preconditions
    original_parse = canonical["semantic"].parse_turtle
    state = {"now": 0.0, "parseCalls": 0}

    @wraps(original_preflight)
    def actual_preflight_then_elapsed():
        identity = original_preflight()
        state["now"] = 121.0
        return identity

    @wraps(original_parse)
    def actual_parse(*args, **kwargs):
        state["parseCalls"] += 1
        return original_parse(*args, **kwargs)

    monkeypatch.setattr(probe, "check_runtime_preconditions", actual_preflight_then_elapsed)
    monkeypatch.setattr(canonical["semantic"], "parse_turtle", actual_parse)
    stdout, stderr = io.BytesIO(), io.BytesIO()
    code = probe.run_fixed_suite(
        "b1-semantic-1x-v1", stdout=stdout, stderr=stderr, monotonic=lambda: state["now"]
    )
    records = _jsonl(stdout.getvalue())
    assert code == 1
    assert state["parseCalls"] == 0
    assert [item["type"] for item in records] == ["header", "terminal"]
    assert records[0]["limits"]["deadlineIncludesPreflight"] is True
    assert records[-1]["collectionComplete"] is False
    assert records[-1]["completedIds"] == []


@pytest.fixture(scope="module")
def real_resources():
    """An unmet adoption/pin is an actual failure, never a skipped integration."""
    root = REPOSITORY / "packages/contracts"
    for relative, (size, digest) in RESOURCE_PINS.items():
        raw = (root / relative).read_bytes()
        assert (len(raw), _sha(raw)) == (size, digest), relative
    return root


@pytest.fixture(scope="module")
def canonical(real_resources):
    from ontolearn_engine import semantic
    from ontolearn_engine import semantic_profile_directsteps as direct
    from ontolearn_engine import semantic_profile_production as production
    from ontolearn_engine import semantic_profile_restore as restore
    from ontolearn_engine import semantic_scopes as scopes
    from ontolearn_engine.quality.rule_profile import TermInput
    from ontolearn_engine.resources import CONTRACT
    from ontolearn_engine.semantic_profile_input import CaptureLedger, prepare_profile_material
    from ontolearn_engine.semantic_profile_restore_budget import RestoreFailure, RestoreLedger

    return {
        "semantic": semantic,
        "direct": direct,
        "production": production,
        "restore": restore,
        "scopes": scopes,
        "TermInput": TermInput,
        "catalog": CONTRACT.ERROR_CATALOG,
        "schema": json.loads((real_resources / "v2/schema.json").read_bytes()),
        "CaptureLedger": CaptureLedger,
        "prepare": prepare_profile_material,
        "RestoreFailure": RestoreFailure,
        "RestoreLedger": RestoreLedger,
    }


def _data(spelling, datatype="date"):
    return PREFIX + f'ex:s a ex:Focus; ex:p "{spelling}"^^xsd:{datatype} .'


def _shape(parameter):
    return PREFIX + (
        "ex:node a sh:NodeShape; sh:targetClass ex:Focus; sh:property ex:shape .\n"
        f"ex:shape a sh:PropertyShape; sh:path ex:p; {parameter} ."
    )


def _violation(value, constraint):
    # Independently specified six-field golden; no observed source result used.
    return {
        "focus": "<urn:probe-test:s>",
        "path": "<urn:probe-test:p>",
        "value": value,
        "sourceShape": "<urn:probe-test:shape>",
        "constraint": f"<{SH}{constraint}>",
        "severity": f"<{SH}Violation>",
    }


def test_real_parse_query_preserves_lexical_identity_and_numeric_promotion(canonical):
    semantic = canonical["semantic"]
    graph = semantic.parse_turtle(
        PREFIX + 'ex:a ex:p "01"^^xsd:integer .\n'
        'ex:b ex:p "1"^^xsd:integer .\n'
        'ex:c ex:p "1.0"^^xsd:decimal .'
    )
    result = semantic.query(
        graph, "SELECT ?s ?v WHERE { ?s <urn:probe-test:p> ?v . FILTER(?v = 1.0) } ORDER BY ?s"
    )
    assert result == {
        "type": "SELECT", "variables": ["s", "v"],
        "rows": [
            ["<urn:probe-test:a>", f'"01"^^<{XSD}integer>'],
            ["<urn:probe-test:b>", f'"1"^^<{XSD}integer>'],
            ["<urn:probe-test:c>", f'"1.0"^^<{XSD}decimal>'],
        ],
    }
    typed_error = semantic.parse_turtle(PREFIX + 'ex:a ex:p "text" .')
    assert semantic.query(
        typed_error, "SELECT ?s WHERE { ?s <urn:probe-test:p> ?v . FILTER(?v < 1) }"
    ) == {"type": "SELECT", "variables": ["s"], "rows": []}


@pytest.mark.parametrize(
    "query",
    [
        "SELECT ?s WHERE { SERVICE <https://example.invalid/sparql> { ?s ?p ?o } }",
        "SELECT ?s FROM <https://example.invalid/data> WHERE { ?s ?p ?o }",
    ],
)
def test_real_offline_query_rejection_is_a_code_not_a_network_success(canonical, query):
    from ontolearn_engine.semantic_offline import SemanticError

    graph = canonical["semantic"].parse_turtle("<urn:offline:s> <urn:offline:p> <urn:offline:o> .")
    with pytest.raises(SemanticError) as error:
        canonical["semantic"].query(graph, query)
    assert error.value.code == "EXTERNAL_ACCESS_DENIED"
    # This exercises the actual parser's refusal, not a network/sentinel proof.


def test_real_service_word_inside_literal_is_not_rejected(canonical):
    semantic = canonical["semantic"]
    graph = semantic.parse_turtle('<urn:offline:s> <urn:offline:p> "SERVICE" .')
    assert semantic.query(
        graph, 'SELECT ?s WHERE { ?s <urn:offline:p> "SERVICE" }'
    ) == {"type": "SELECT", "variables": ["s"], "rows": [["<urn:offline:s>"]]}


@pytest.mark.parametrize("spelling,conforms", [("1999-12-31Z", False), ("2000-01-01Z", True)])
def test_real_date_policy_full_six_fields(canonical, spelling, conforms):
    result = canonical["semantic"].validate_shacl_text(
        _data(spelling),
        _shape('sh:minInclusive "2000-01-01Z"^^xsd:date'),
        data_policy="strict",
        range_policy="utc-date-range-v1",
    )
    expected = [] if conforms else [
        _violation(f'"{spelling}"^^<{XSD}date>', "MinInclusiveConstraintComponent")
    ]
    assert result["report"] == {"conforms": conforms, "violations": expected}
    assert result["entryVersion"] == "i05-shacl-text-2"
    assert result["dataPolicy"] == "strict"
    assert result["rangePolicy"] == "utc-date-range-v1"


def test_real_integer_entry_keeps_bad_lexical_and_strict_front_door(canonical):
    from ontolearn_engine.semantic_offline import SemanticError

    text = _data("not-an-int", "integer")
    shape = _shape("sh:datatype xsd:integer")
    with pytest.raises(SemanticError) as failed:
        canonical["semantic"].validate_shacl_text(
            text, shape, data_policy="strict", range_policy="legacy"
        )
    assert failed.value.code == "INVALID_LITERAL_LEXICAL"
    result = canonical["semantic"].validate_shacl_text(
        text, shape, data_policy="integer-illtyped-report-v1", range_policy="legacy"
    )
    assert result["entryVersion"] == "i05-shacl-text-1"
    assert result["report"] == {
        "conforms": False,
        "violations": [
            _violation(f'"not-an-int"^^<{XSD}integer>', "DatatypeConstraintComponent")
        ],
    }
    with pytest.raises(SemanticError) as strict_again:
        canonical["semantic"].parse_turtle(text)
    assert strict_again.value.code == "INVALID_LITERAL_LEXICAL"


@pytest.mark.parametrize(
    "data,parameter,policy,code",
    [
        ("2000-01-01Z", 'sh:minInclusive "2000-01-01Z"^^xsd:date', "legacy", "INVALID_SHAPE"),
        (
            "2000-01-01+00:00",
            'sh:minInclusive "2000-01-01Z"^^xsd:date',
            "utc-date-range-v1",
            "RDF_TERM_INVALID",
        ),
        (
            "2000-01-01Z",
            'sh:minExclusive "2000-01-01Z"^^xsd:date',
            "utc-date-range-v1",
            "UNSUPPORTED_SHACL",
        ),
    ],
)
def test_real_policy_negatives_keep_original_codes(canonical, data, parameter, policy, code):
    from ontolearn_engine.semantic_offline import SemanticError

    with pytest.raises(SemanticError) as error:
        canonical["semantic"].validate_shacl_text(
            _data(data), _shape(parameter), data_policy="strict", range_policy=policy
        )
    assert error.value.code == code


def test_real_scope_consumes_the_same_fresh_prepare_result(canonical):
    semantic, scopes = canonical["semantic"], canonical["scopes"]
    asserted = semantic.parse_turtle("<urn:scope:x> a <urn:scope:A> .")
    ontology = semantic.parse_turtle(f"<urn:scope:A> <{RDFS}subClassOf> <urn:scope:B> .")
    prepared = scopes.prepare_validation_scope(asserted, ontology, include_derived=True)
    projected = scopes.project_validation_scope(
        asserted,
        ontology,
        include_derived=True,
        reasoning_result=prepared.reasoning_result,
        reasoning_source=prepared.provenance["reasoningSource"],
    )
    asserted_only = scopes.prepare_validation_scope(asserted, ontology, include_derived=False)
    query = "ASK { <urn:scope:x> a <urn:scope:B> }"
    assert semantic.query(asserted_only.facts, query) == {"type": "ASK", "value": False}
    assert semantic.query(projected.facts, query) == {"type": "ASK", "value": True}
    assert projected.reasoning_result is prepared.reasoning_result
    assert projected.provenance == prepared.provenance
    shapes = semantic.parse_turtle(
        PREFIX + "ex:n a sh:NodeShape; sh:targetClass <urn:scope:B>; sh:property ex:shape .\n"
        "ex:shape a sh:PropertyShape; sh:path <urn:scope:p>; sh:minCount 1 .",
        shapes=True,
    )
    assert semantic.check_shapes(asserted_only.facts, shapes) == {
        "conforms": True, "violations": []
    }
    assert semantic.check_shapes(projected.facts, shapes) == {
        "conforms": False,
        "violations": [{
            "focus": "<urn:scope:x>",
            "path": "<urn:scope:p>",
            "value": None,
            "sourceShape": "<urn:probe-test:shape>",
            "constraint": f"<{SH}MinCountConstraintComponent>",
            "severity": f"<{SH}Violation>",
        }],
    }


def _fresh_production(canonical, explanation):
    term = canonical["TermInput"]
    records = tuple(
        tuple(term("iri", value) for value in row)
        for row in (("urn:dag:x", RDF + "type", "urn:dag:A"),
                    ("urn:dag:A", RDFS + "subClassOf", "urn:dag:B"))
    )
    material = canonical["prepare"](records=records)
    keywords = {
        "error_catalog": canonical["catalog"],
        "error_schema": canonical["schema"],
        "ledger": canonical["CaptureLedger"](),
    }
    if explanation:
        keywords["direct_ledger"] = canonical["direct"].DirectStepsLedger()
        produced = canonical["production"].execute_profile_explanation(material, **keywords)
    else:
        produced = canonical["production"].execute_admitted_profile_job(material, **keywords)
    payload = produced.wire["payload"]
    expectation_class = (
        canonical["restore"].ExplanationRestoreExpectation
        if explanation else canonical["restore"].RestoreExpectation
    )
    expected = expectation_class(
        payload_digest=_sha(produced.payload_json),
        rows_digest=_sha(produced.rows_json),
        input_digest=payload["inputDigest"],
        input_domain=payload["inputDigestDomain"],
        source_digest=payload["sourceDigest"],
        definitions_digest=payload["definitionsDigest"],
        catalog_digest=_sha(produced.catalog_json),
        implementation=tuple(sorted(payload["implementation"].items())),
        input_preimage=material.input_preimage,
        source_preimage=material.source_preimage,
    )
    return produced, expected


@pytest.mark.parametrize("explanation", [False, True])
def test_real_capture_restore_retains_original_expectation_on_bad_bytes(canonical, explanation):
    produced, expected = _fresh_production(canonical, explanation)
    allocation = produced.original_allocation
    restore = canonical["restore"]
    receive = (
        restore.restore_profile_explanation_result
        if explanation else restore.restore_profile_result
    )

    def receive_bytes(payload, rows):
        keywords = {"expected": expected, "allocation": allocation,
                    "ledger": canonical["RestoreLedger"]()}
        if explanation:
            keywords["direct_ledger"] = canonical["direct"].DirectStepsLedger()
        return receive(payload, rows, **keywords)

    view = receive_bytes(produced.payload_json, produced.rows_json)
    assert produced.payload_json == _canonical(produced.wire["payload"])
    assert produced.rows_json == _canonical(produced.wire["rows"])
    assert produced.source_encoded == produced.material.source_preimage
    assert produced.definitions_encoded == produced.material.definitions_preimage
    assert view.rows_json == produced.rows_json
    assert len(produced.wire["payload"]) == 7
    assert len(produced.native_result) == (16 if explanation else 15)
    assert all(len(child) == 11 for child in produced.native_result["mechanismBatches"])
    saved = produced.payload_json, produced.rows_json, expected, allocation
    for payload, rows in (
        (produced.payload_json + b" ", produced.rows_json),
        (produced.payload_json, produced.rows_json + b" "),
    ):
        with pytest.raises(canonical["RestoreFailure"]):
            receive_bytes(payload, rows)
        assert saved == (produced.payload_json, produced.rows_json, expected, allocation)
    if explanation:
        target = ("<urn:dag:x>", f"<{RDF}type>", "<urn:dag:B>")
        roots = restore.explanation_roots(
            view, (target,), direct_ledger=canonical["direct"].DirectStepsLedger()
        )
        assert len(roots) == 1 and roots[0].kind == "step" and roots[0].ordinal == 0
        steps = produced.native_result["directSteps"]["steps"]
        assert len(steps) == 1
        assert steps[0]["rule"] == "rdfs9-type-via-subclass"
        assert steps[0]["depth"] == 1
        assert steps[0]["result"] == target
        seeds = (
            ("<urn:dag:x>", f"<{RDF}type>", "<urn:dag:A>"),
            ("<urn:dag:A>", f"<{RDFS}subClassOf>", "<urn:dag:B>"),
        )
        expected_premises = tuple(
            {"kind": "leaf", "reference": "i05-proof:" + _sha(
                ("i05-profile-proof-leaf/1\0" + "\0".join(triple)).encode()
            )}
            for triple in seeds
        )
        assert steps[0]["premises"] == expected_premises
        all_roots = restore.explanation_roots(
            view, (target, *seeds), direct_ledger=canonical["direct"].DirectStepsLedger()
        )
        assert [root.kind for root in all_roots] == ["step", "leaf", "leaf"]
        assert [root.reference for root in all_roots[1:]] == [
            row["reference"] for row in expected_premises
        ]
