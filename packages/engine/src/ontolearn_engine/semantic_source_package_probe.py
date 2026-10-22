"""Sealed, private semantic observations; no Store, Job or acceptance authority.

Source -m and a future direct frozen target bootstrap the canonical module
before defining any observer class. Assets contain syntax, never oracle output.
"""

from __future__ import annotations

if __name__ == "__main__":
    from ontolearn_engine.semantic_source_package_probe import main

    raise SystemExit(main())

import _thread
import base64
import hashlib
import importlib
import importlib.metadata
import json
import marshal
import math
import signal
import sys
import time
import types
from contextlib import nullcontext
from contextvars import ContextVar
from dataclasses import fields, is_dataclass
from pathlib import Path

FLAG = "--semantic-source-package-probe"
SELECTORS = ("full-v1", "b1-semantic-1x-v1", "b1-semantic-10x-v1")
# Input provenance stays fixed when the runtime supplier is repaired.
ASSET_SUPPLIER_REF = "6891a5842302859a531cf82767c5a482417bc274"
SOURCE_REF = "23352bacb500088367f849e53980e97c937724b3"
PROCESS_REF = "513db0056f312342a6791e2d4c7842f3726581f2"
DESCRIPTOR_CAP = 1_048_576
INPUT_CAP = 8_388_608
ITEM_CAP = 33_554_432
REPORT_CAP = 67_108_864
TERMINAL_RESERVE = 65_536
CASE_CAP = 512
DEADLINE_SECONDS = 120
INPUT_NAME = "i05-source-package-parity-inputs.json"
MANIFEST_NAME = "i05-source-package-parity-manifest.json"
# These two pins are filled from the deterministic asset freeze, not at runtime.
MANIFEST_BYTES = 21202
MANIFEST_SHA256 = "0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a"
SUPPLIER_PINS = (
    (
        "ontolearn_engine",
        "__init__.py",
        101,
        "4b8460a6ccc649f44188171c3d4c0c9e58e1204c711462d9ecf0aff12135684f",
    ),
    (
        "ontolearn_engine.quality",
        "quality/__init__.py",
        548,
        "9a5130c2fdbe376e5e4c15e68085f01724847ff13e9b2c195cf270e476806d9c",
    ),
    (
        "ontolearn_engine.quality.rule_calendar",
        "quality/rule_calendar.py",
        4047,
        "6a2e43b029f7069e398f696ff19948d9e806f06fecd9a1e239b889a55e528aec",
    ),
    (
        "ontolearn_engine.quality.rule_comparator",
        "quality/rule_comparator.py",
        1750,
        "9a495876a182d1cad4cac86bb4651c1627e4afc37e1bf9bb3d62be6bb0e95ff2",
    ),
    (
        "ontolearn_engine.quality.rule_firing",
        "quality/rule_firing.py",
        19149,
        "5116aa3e96ae10e7f37eb7afddceef50879869d38af116f9c794437edf49243c",
    ),
    (
        "ontolearn_engine.quality.rule_numbers",
        "quality/rule_numbers.py",
        7372,
        "6b080a55bd8f4af1a1120b55448e02a1a442c231a32ab575ce6e82de054164f9",
    ),
    (
        "ontolearn_engine.quality.rule_profile",
        "quality/rule_profile.py",
        11987,
        "b40b73f65f474cda32ac42caeeb837ad6470a7daeeba9013d8f69e7f0c5a261c",
    ),
    (
        "ontolearn_engine.quality.rule_revalidation",
        "quality/rule_revalidation.py",
        6288,
        "9e9258cfefdef56f369dad6bb7838afd22478ea6714e4322b2d872d12616200e",
    ),
    (
        "ontolearn_engine.quality.rule_terms",
        "quality/rule_terms.py",
        6176,
        "218c4790e9b35236e393407b5b4e0207890d46fe3ea48a9a69e26aa08ddba1d1",
    ),
    (
        "ontolearn_engine.resources",
        "resources.py",
        3065,
        "177f57db2c3e768b9fc17d0c9e0665677e6aab55c16003ac7f304254c10d2238",
    ),
    (
        "ontolearn_engine.semantic",
        "semantic.py",
        66258,
        "d6c5f5c38aec310de726f73568e1086bf4de95117cbdf664ae1384fcd6808392",
    ),
    (
        "ontolearn_engine.semantic_error_adapter",
        "semantic_error_adapter.py",
        15426,
        "0572b4730ba1ac28192e84633633d7da222e6603ff7da811c84e1f368eb55014",
    ),
    (
        "ontolearn_engine.semantic_execution",
        "semantic_execution.py",
        35220,
        "3ac496383349e3ddefea1672c27c88bacaf99f4436c22e96e1592393bac102f3",
    ),
    (
        "ontolearn_engine.semantic_offline",
        "semantic_offline.py",
        1351,
        "4897d9c6a07756d5f8ed4908b4b7a28ca96c67b2670753b74f73e41bf4b67488",
    ),
    (
        "ontolearn_engine.semantic_profile_directsteps",
        "semantic_profile_directsteps.py",
        46459,
        "7927769077e363b23741f6dc78b7c0ec2ad00b7d3285f8403a190c0e00169b22",
    ),
    (
        "ontolearn_engine.semantic_profile_input",
        "semantic_profile_input.py",
        40378,
        "f4d76b68e6bd5f27d4e1c0ee7b26435117b1dd762a4b2a16503d41afd1841f74",
    ),
    (
        "ontolearn_engine.semantic_profile_production",
        "semantic_profile_production.py",
        19993,
        "5c857470890bd810370ad877db930848ba08e80096c640037d39bea83c14a320",
    ),
    (
        "ontolearn_engine.semantic_profile_restore",
        "semantic_profile_restore.py",
        70203,
        "1607d2968d2ba76ad0711be446fea7965641fb845226d0e683ac35e5d0f57243",
    ),
    (
        "ontolearn_engine.semantic_profile_restore_budget",
        "semantic_profile_restore_budget.py",
        37889,
        "ffde8fd243696ab4e8812e8994e6a8fc2b5832f411e5fdf1e4c7753fe19c93d0",
    ),
    (
        "ontolearn_engine.semantic_query",
        "semantic_query.py",
        6448,
        "fe8e600de7c0b300038ba0c952497cb8fbbf30f741f1e0d5e1bba78afef8670f",
    ),
    (
        "ontolearn_engine.semantic_scopes",
        "semantic_scopes.py",
        13051,
        "aa8f1231df09332e9f02d96e3c8e4ef4cb64d4b3fa28067babcd3431de820ebf",
    ),
    (
        "ontolearn_engine.semantic_turtle",
        "semantic_turtle.py",
        33916,
        "4180feb9d0c775669b65338e1cfb37a8d5bb7f3ce155b4804dd53a43efad5214",
    ),
)
PUBLIC_RESOURCE_PINS = (
    (
        "python/contract_v2.py",
        34608,
        "17aa68bc2271b45ffb70a023b9db9e441bb1b4e79fc9a42bb6932f60631be7b7",
    ),
    ("v2/schema.json", 207256, "e913138e6f3ac632268ae7f8c2461577022e8298d1c03e0668416a0d654eaabf"),
    ("v2/registry.json", 15962, "1f2e298209e238433c02864a05c70b24482e4c1fd00e7309f63eac84a1f3706b"),
    ("v2/errors.json", 16299, "ad242d93ced7a0c8a463b708b7a1f3105e65f03c3980e0a0c6c4309f8c26544c"),
)
LOCK_BYTES = 28440
LOCK_SHA256 = "86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73"
DISTRIBUTIONS = {
    "rdflib": "7.6.0",
    "pyshacl": "0.30.1",
    "pyparsing": "3.3.3",
    "owlrl": "7.6.2",
    "prettytable": "3.18.0",
    "wcwidth": "0.9.2",
    "html5rdf": "1.2.1",
    "packaging": "26.3",
}
OPERATIONS = {
    "parse",
    "query",
    "legacy-reason",
    "scope",
    "profile",
    "fullview",
    "dag",
    "restore-negative",
    "shape",
    "shacl-text",
    "offline",
    "b1-measurement",
}
OBS_KEYS = {
    "id",
    "sourceCaseId",
    "family",
    "operation",
    "datasetId",
    "parameters",
    "sourceRefs",
    "contextStatus",
    "projectionSha256",
}
CONTEXT_KEYS = {
    "mathInputContexts",
    "originalOperations",
    "productCases",
    "learningChecks",
    "unresolved",
    "nonClaims",
}
SCOPE_MODES = {
    "asserted",
    "fresh",
    "project",
    "missing-source",
    "wrong-source",
    "missing-result",
    "nonexact-include",
    "unselected-rules",
    "unselected-result",
    "facts-axioms",
}
MUTATIONS = {
    "payload-unknown-key",
    "tail-source-tamper",
    "tail-definition-tamper",
    "tail-limits-tamper",
    "tail-child-tamper",
    "dag-depth-plus-one",
    "dag-last-premise-forward",
    "leaf-rename-all",
    "head-occurrence-1023-15",
}


class ProbeFault(ValueError):
    """Stable harness code only; never stringify an incoming exception."""

    def __init__(self, code):
        self.code = code if type(code) is str and code.isascii() else "HARNESS_FAILED"
        super().__init__(self.code)


class BoundaryStop(ProbeFault):
    def __init__(self, code, exit_code, state):
        super().__init__(code)
        self.exit_code, self.state = exit_code, state


_COLLECTION_CONTEXT = ContextVar("i05_probe_collection_boundary", default=None)


class CollectionBoundary:
    """Caller observation only; never replaces a canonical business callable."""

    def __init__(self, monotonic, started, cancel_requested):
        self.monotonic, self.started = monotonic, started
        self.cancel_requested = cancel_requested
        self.stage, self.api = "dispatch/input", None
        self.completed = []
        self.attempts = []

    def check(self):
        if self.cancel_requested():
            raise BoundaryStop("COLLECTION_STOP_REQUESTED", 130, "stopping")
        if self.monotonic() - self.started >= DEADLINE_SECONDS:
            raise BoundaryStop("COLLECTION_DEADLINE", 1, "deadline-boundary")

    def call(self, stage, api, function, args, kwargs, capture=True):
        self.stage, self.api = stage, api
        self.check()
        attempt = {"stage": stage, "api": api, "start": self.monotonic(), "returned": False}
        self.attempts.append(attempt)
        tick = time.perf_counter_ns()
        try:
            value = function(*args, **kwargs)
        finally:
            attempt["end"] = self.monotonic()
            attempt["elapsedNs"] = time.perf_counter_ns() - tick
        attempt["returned"] = True
        if capture:
            # Retain actual references until this observation is written.
            # No fake success, cross-case cache or native reconstruction.
            self.completed.append({**attempt, "value": value})
        self.check()  # An opaque call may finish late; never start the next one.
        return value


def _checked_call(stage, api, function, *args, **kwargs):
    boundary = _COLLECTION_CONTEXT.get()
    if boundary is None:
        return function(*args, **kwargs)
    return boundary.call(stage, api, function, args, kwargs)


def _checked_lexical_decode(function, text):
    boundary = _COLLECTION_CONTEXT.get()
    if boundary is None:
        return function(text)
    # Each term is original input syntax. Do not retain thousands of duplicate
    # lexical adapter values; the actual prepared material is captured separately.
    return boundary.call(
        "input/decodeTerm",
        "semantic_turtle.decode_profile_term",
        function,
        (text,),
        {},
        capture=False,
    )


def parse_argv(argv):
    if (
        type(argv) is not list
        or len(argv) != 2
        or any(type(value) is not str for value in argv)
        or argv[0] != FLAG
        or argv[1] not in SELECTORS
    ):
        raise ProbeFault("PROBE_ARGUMENTS_INVALID")
    return argv[1]


def asset_paths():
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS) / "ontolearn_engine/probe_inputs"
    else:
        base = Path(__file__).resolve().parent / "probe_inputs"
    return base / MANIFEST_NAME, base / INPUT_NAME


def read_bounded(path, cap):
    if type(cap) is not int or cap < 0:
        raise ProbeFault("ASSET_CAP_INVALID")
    try:
        with path.open("rb") as stream:
            raw = stream.read(cap + 1)
    except (OSError, ValueError, TypeError):
        raise ProbeFault("ASSET_UNAVAILABLE") from None
    if type(raw) is not bytes or len(raw) > cap:
        raise ProbeFault("ASSET_INPUT_LIMIT")
    return raw


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ProbeFault("ASSET_JSON_DUPLICATE_KEY")
            result[key] = value
        return result

    def constant(_value):
        raise ProbeFault("ASSET_JSON_NONFINITE")

    def floating(value):
        result = float(value)
        if not math.isfinite(result):
            raise ProbeFault("ASSET_JSON_NONFINITE")
        return result

    try:
        if type(raw) is not bytes or raw.startswith(b"\xef\xbb\xbf"):
            raise ProbeFault("ASSET_JSON_INVALID")
        return json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=pairs,
            parse_constant=constant,
            parse_float=floating,
        )
    except ProbeFault:
        raise
    except (ValueError, UnicodeError, RecursionError, OverflowError):
        raise ProbeFault("ASSET_JSON_INVALID") from None


def canonical_bytes(value):
    """Pure asset digest domain; escaped Unicode preserves even invalid text input."""
    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    except (TypeError, ValueError, RecursionError, OverflowError):
        raise ProbeFault("ASSET_JSON_INVALID") from None


def _exact(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise ProbeFault("ASSET_SCHEMA_INVALID")


def _list(value):
    if type(value) is not list:
        raise ProbeFault("ASSET_SCHEMA_INVALID")


def _text(value):
    if type(value) is not str:
        raise ProbeFault("ASSET_SCHEMA_INVALID")


def _validate_parameters(observation, dataset):
    operation, parameters = observation["operation"], observation["parameters"]
    if type(parameters) is not dict:
        raise ProbeFault("ASSET_SCHEMA_INVALID")
    kinds = {
        "parse": {"turtle"},
        "query": {"query"},
        "legacy-reason": {"legacy"},
        "scope": {"scope"},
        "profile": {"profile"},
        "fullview": {"records", "profile", "turtle"},
        "dag": {"records", "turtle"},
        "restore-negative": {"records"},
        "shape": {"shape"},
        "shacl-text": {"shape"},
        "offline": {"query", "turtle", "shape"},
        "b1-measurement": {"b1"},
    }
    if dataset["kind"] not in kinds[operation]:
        raise ProbeFault("ASSET_SCHEMA_INVALID")
    if operation in {"parse", "query", "legacy-reason", "profile", "shape", "b1-measurement"}:
        _exact(parameters, ())
    elif operation == "scope":
        _exact(parameters, ("mode",))
        if type(parameters["mode"]) is not str or parameters["mode"] not in SCOPE_MODES:
            raise ProbeFault("ASSET_SCHEMA_INVALID")
    elif operation in {"fullview", "dag"}:
        _exact(
            parameters,
            ("materialMode",) if operation == "fullview" else ("materialMode", "rootsTargets"),
        )
        if type(parameters["materialMode"]) is not str or parameters["materialMode"] not in {
            "records",
            "text",
        }:
            raise ProbeFault("ASSET_SCHEMA_INVALID")
        if operation == "dag":
            _list(parameters["rootsTargets"])
    elif operation == "restore-negative":
        _exact(parameters, ("explanation", "mutation", "rootsTargets"))
        if type(parameters["explanation"]) is not bool:
            raise ProbeFault("ASSET_SCHEMA_INVALID")
        if type(parameters["mutation"]) is not str or parameters["mutation"] not in MUTATIONS:
            raise ProbeFault("ASSET_SCHEMA_INVALID")
        _list(parameters["rootsTargets"])
    elif operation == "shacl-text":
        # Missing mandatory Python keywords are real explicit call-contract cases.
        if set(parameters) - {"dataPolicy", "rangePolicy"}:
            raise ProbeFault("ASSET_SCHEMA_INVALID")
    elif operation == "offline":
        _exact(parameters, ("action",))
        if type(parameters["action"]) is not str or parameters["action"] not in {
            "query",
            "parse",
            "shape",
            "implicit-jsonld",
        }:
            raise ProbeFault("ASSET_SCHEMA_INVALID")


def validate_assets(manifest, inputs):
    _exact(manifest, ("format", "inputAsset", "counts", "caseSets", "sources", "versions"))
    _exact(inputs, ("format", "datasets", "observations", "contexts"))
    if (
        manifest["format"] != "i05-source-package-parity-manifest/1"
        or inputs["format"] != "i05-source-package-parity-inputs/1"
    ):
        raise ProbeFault("ASSET_VERSION_INVALID")
    _exact(manifest["inputAsset"], ("bytes", "sha256"))
    if (
        type(manifest["inputAsset"]["bytes"]) is not int
        or not 0 <= manifest["inputAsset"]["bytes"] <= INPUT_CAP
        or type(manifest["inputAsset"]["sha256"]) is not str
        or len(manifest["inputAsset"]["sha256"]) != 64
    ):
        raise ProbeFault("ASSET_SCHEMA_INVALID")
    if type(inputs["datasets"]) is not dict or not inputs["datasets"]:
        raise ProbeFault("ASSET_SCHEMA_INVALID")
    schemas = {
        "turtle": {"kind", "text", "format", "shapes"},
        "query": {"kind", "dataText", "queryText"},
        "legacy": {"kind", "dataText", "rules"},
        "scope": {"kind", "assertedText", "ontologyText", "rules", "shapesText", "queryText"},
        "profile": {"kind", "input"},
        "records": {"kind", "records", "rules"},
        "shape": {"kind", "dataText", "shapesText"},
        "b1": {
            "kind",
            "assertedText",
            "ontologyText",
            "shapesText",
            "queryText",
            "rules",
            "replaceEquipmentTypes",
            "seed",
            "scale",
        },
    }
    for name, dataset in inputs["datasets"].items():
        _text(name)
        if type(dataset) is not dict or type(dataset.get("kind")) is not str:
            raise ProbeFault("ASSET_SCHEMA_INVALID")
        if dataset["kind"] not in schemas:
            raise ProbeFault("ASSET_SCHEMA_INVALID")
        _exact(dataset, schemas[dataset["kind"]])
        if dataset["kind"] == "profile":
            _exact(dataset["input"], ("asserted", "ontology", "definitions", "disabled_rule_ids"))
        for key in ("text", "dataText", "queryText", "assertedText", "ontologyText", "shapesText"):
            if key in dataset:
                if not (dataset["kind"] == "shape" and dataset[key] is None):
                    _text(dataset[key])
        for key in ("rules", "records", "replaceEquipmentTypes"):
            if key in dataset:
                _list(dataset[key])
        if dataset["kind"] == "turtle":
            _text(dataset["format"])
            if type(dataset["shapes"]) is not bool:
                raise ProbeFault("ASSET_SCHEMA_INVALID")
    _list(inputs["observations"])
    if not 0 < len(inputs["observations"]) <= CASE_CAP:
        raise ProbeFault("ASSET_CASE_LIMIT")
    ids, lookup = [], {}
    for observation in inputs["observations"]:
        _exact(observation, OBS_KEYS)
        for key in ("id", "sourceCaseId", "family", "operation", "datasetId", "contextStatus"):
            _text(observation[key])
        if not observation["id"] or observation["id"] in lookup:
            raise ProbeFault("ASSET_CASE_ID_INVALID")
        if observation["operation"] not in OPERATIONS:
            raise ProbeFault("ASSET_SCHEMA_INVALID")
        if observation["datasetId"] not in inputs["datasets"]:
            raise ProbeFault("ASSET_SCHEMA_INVALID")
        _list(observation["sourceRefs"])
        dataset = inputs["datasets"][observation["datasetId"]]
        if hashlib.sha256(canonical_bytes(dataset)).hexdigest() != observation["projectionSha256"]:
            raise ProbeFault("ASSET_PROJECTION_HASH_INVALID")
        _validate_parameters(observation, dataset)
        ids.append(observation["id"])
        lookup[observation["id"]] = observation
    _exact(manifest["caseSets"], SELECTORS)
    for selector, chosen in manifest["caseSets"].items():
        _list(chosen)
        if not chosen or any(type(name) is not str or name not in lookup for name in chosen):
            raise ProbeFault("ASSET_CASE_SET_INVALID")
        if len(chosen) != len(set(chosen)):
            raise ProbeFault("ASSET_CASE_SET_INVALID")
        # The terminal includes a partition of these IDs; reserve it before any call.
        if len(canonical_bytes(chosen)) + 4096 > TERMINAL_RESERVE:
            raise ProbeFault("ASSET_TERMINAL_LIMIT")
        if selector != "full-v1" and (
            len(chosen) != 1
            or lookup[chosen[0]]["operation"] != "b1-measurement"
            or inputs["datasets"][lookup[chosen[0]]["datasetId"]]["scale"]
            != (1 if selector == "b1-semantic-1x-v1" else 10)
        ):
            raise ProbeFault("ASSET_CASE_SET_INVALID")
    if manifest["caseSets"]["full-v1"] != ids:
        raise ProbeFault("ASSET_CASE_SET_INVALID")
    _exact(inputs["contexts"], CONTEXT_KEYS)
    for key in (
        "mathInputContexts",
        "originalOperations",
        "productCases",
        "learningChecks",
        "unresolved",
    ):
        _list(inputs["contexts"][key])
    expected = {
        "mathInputContexts": 83,
        "originalOperations": 106,
        "productCases": 50,
        "learningChecks": 54,
    }
    for key, count in expected.items():
        if len(inputs["contexts"][key]) != count:
            raise ProbeFault("ASSET_CONTEXT_INCOMPLETE")
    for context in inputs["contexts"]["mathInputContexts"]:
        if type(context) is not dict or any(
            context.get(key) is not False
            for key in (
                "lifecycleExecuted",
                "originalRequestedOperationPassed",
                "sourceAuthorityAuthenticated",
            )
        ):
            raise ProbeFault("ASSET_CONTEXT_INVALID")
    if type(manifest["counts"]) is not dict:
        raise ProbeFault("ASSET_SCHEMA_INVALID")
    for key, actual in (("datasets", len(inputs["datasets"])), ("observations", len(ids))):
        if manifest["counts"].get(key) != actual or type(manifest["counts"].get(key)) is not int:
            raise ProbeFault("ASSET_COUNT_INVALID")
    _list(manifest["sources"])
    if type(manifest["versions"]) is not dict:
        raise ProbeFault("ASSET_SCHEMA_INVALID")
    _validate_nested_assets(manifest, inputs)


def load_assets():
    descriptor_path, input_path = asset_paths()
    descriptor_raw = read_bounded(descriptor_path, DESCRIPTOR_CAP)
    if (
        len(descriptor_raw) != MANIFEST_BYTES
        or hashlib.sha256(descriptor_raw).hexdigest() != MANIFEST_SHA256
    ):
        raise ProbeFault("ASSET_MANIFEST_IDENTITY_INVALID")
    manifest = strict_json(descriptor_raw)
    if type(manifest) is not dict or type(manifest.get("inputAsset")) is not dict:
        raise ProbeFault("ASSET_SCHEMA_INVALID")
    input_raw = read_bounded(input_path, INPUT_CAP)
    identity = manifest["inputAsset"]
    if len(input_raw) != identity.get("bytes") or hashlib.sha256(
        input_raw
    ).hexdigest() != identity.get("sha256"):
        raise ProbeFault("ASSET_INPUT_IDENTITY_INVALID")
    inputs = strict_json(input_raw)
    validate_assets(manifest, inputs)
    return inputs, manifest


class JSONLWriter:
    """Full encoded logical records; physical pipe writes are not called atomic."""

    def __init__(
        self, stream, *, total_cap=REPORT_CAP, item_cap=ITEM_CAP, reserve=TERMINAL_RESERVE
    ):
        if (
            not callable(getattr(stream, "write", None))
            or any(type(v) is not int or v < 0 for v in (total_cap, item_cap, reserve))
            or reserve > total_cap
        ):
            raise ProbeFault("OUTPUT_STREAM_INVALID")
        self.stream, self.total_cap = stream, total_cap
        self.item_cap, self.reserve = item_cap, reserve
        self.used = self.written = 0
        self.terminal_written = False
        self.broken = False

    def emit(self, value, *, terminal=False):
        if self.terminal_written or self.broken:
            raise ProbeFault("OUTPUT_STATE_INVALID")
        bound = self.reserve if terminal else self.item_cap
        raw = bytearray()
        try:
            encoder = json.JSONEncoder(
                ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")
            )
            for chunk in encoder.iterencode(value):
                part = chunk.encode("ascii")
                if len(raw) + len(part) + 1 > bound:
                    raise ProbeFault("OUTPUT_ITEM_LIMIT")
                raw.extend(part)
            raw.extend(b"\n")
        except ProbeFault:
            raise
        except (TypeError, ValueError, UnicodeError, RecursionError, OverflowError):
            raise ProbeFault("OUTPUT_SERIALIZATION_FAILED") from None
        ceiling = self.total_cap if terminal else self.total_cap - self.reserve
        if self.used + len(raw) > ceiling:
            raise ProbeFault("OUTPUT_REPORT_LIMIT")
        self.used += len(raw)  # Charge the full record before exposing its first byte.
        view, offset = memoryview(raw), 0
        try:
            while offset < len(view):
                count = self.stream.write(view[offset:])
                if type(count) is not int or count <= 0 or count > len(view) - offset:
                    raise ProbeFault("OUTPUT_WRITE_FAILED")
                offset += count
                self.written += count
            if callable(getattr(self.stream, "flush", None)):
                self.stream.flush()
        except Exception:
            self.broken = True
            raise ProbeFault("OUTPUT_WRITE_FAILED") from None
        if terminal:
            self.terminal_written = True


class CallCounter:
    """Count owner-thread entries using two real, synchronous code identities."""

    def __init__(self, semantic, validator):
        try:
            self.reason_code = semantic.reason.__code__
            self.validator_code = validator.run.__code__
            self._codes = (
                (self.reason_code,)
                if self.reason_code is self.validator_code
                else (self.reason_code, self.validator_code)
            )
            # CPython 3.12 CO_GENERATOR | CO_COROUTINE | CO_ASYNC_GENERATOR.
            if any(
                type(code) is not types.CodeType or code.co_flags & 0x2A0 for code in self._codes
            ):
                raise ProbeFault("INTERNAL_ERROR")
            self._monitor = sys.monitoring
            self._tool_id = self._monitor.PROFILER_ID
            self._start = self._monitor.events.PY_START
            self._get_ident = _thread.get_ident
        except Exception as error:
            raise ProbeFault("INTERNAL_ERROR") from error
        self.counts = {"reason": 0, "validator": 0}
        self.previous = None
        self.active = False
        self._counts_complete = False
        self._callback_failed = False
        self._acquired = False
        self._installed = False
        self._admitted = False
        self._prior_start = None
        self._attempted = []
        self._owner_thread = None
        self._name = "i05-call-counter-" + str(id(self))
        self._callback = self._on_start

    @property
    def counts_complete(self):
        return self._counts_complete

    def _on_start(self, code, _offset):
        try:
            if not self.active or self._get_ident() != self._owner_thread:
                return None
            if code is self.reason_code:
                self.counts["reason"] += 1
            if code is self.validator_code:
                self.counts["validator"] += 1
        except BaseException as error:
            self._callback_failed = True
            if isinstance(error, Exception):
                raise ProbeFault("INTERNAL_ERROR") from error
            raise
        return None

    def _cleanup(self, was_active):
        """Return the first integrity/cleanup error; never free uncertain state."""
        self.active = False
        failures = []
        safe_to_free = True
        monitor, tool = self._monitor, self._tool_id
        if not self._acquired:
            return None
        try:
            if monitor.get_tool(tool) != self._name:
                return ProbeFault("INTERNAL_ERROR")
        except BaseException as error:
            return error
        try:
            if self._get_ident() != self._owner_thread or sys.getprofile() is not self.previous:
                failures.append(ProbeFault("INTERNAL_ERROR"))
            if self._admitted and monitor.get_events(tool) != 0:
                failures.append(ProbeFault("INTERNAL_ERROR"))
                safe_to_free = False
        except BaseException as error:
            failures.append(error)
            safe_to_free = False
        for code in self._attempted:
            try:
                mask = monitor.get_local_events(tool, code)
                if mask == self._start:
                    monitor.set_local_events(tool, code, 0)
                    if monitor.get_local_events(tool, code) != 0:
                        raise ProbeFault("INTERNAL_ERROR")
                elif mask == 0:
                    if was_active:
                        failures.append(ProbeFault("INTERNAL_ERROR"))
                else:
                    failures.append(ProbeFault("INTERNAL_ERROR"))
                    safe_to_free = False
            except BaseException as error:
                failures.append(error)
                safe_to_free = False
        if self._installed:
            try:
                actual = monitor.register_callback(tool, self._start, self._prior_start)
                if actual is not self._callback:
                    # Preserve what was actually found, not the expected callback.
                    monitor.register_callback(tool, self._start, actual)
                    failures.append(ProbeFault("INTERNAL_ERROR"))
                    safe_to_free = False
                else:
                    self._installed = False
            except BaseException as error:
                failures.append(error)
                safe_to_free = False
        if safe_to_free:
            try:
                # Only our acquired reservation, after our exact changes were undone.
                if monitor.get_tool(tool) != self._name:
                    raise ProbeFault("INTERNAL_ERROR")
                if self._admitted and monitor.get_events(tool) != 0:
                    raise ProbeFault("INTERNAL_ERROR")
                if any(monitor.get_local_events(tool, code) != 0 for code in self._attempted):
                    raise ProbeFault("INTERNAL_ERROR")
                monitor.free_tool_id(tool)
                self._acquired = False
                self._attempted = []
            except BaseException as error:
                failures.append(error)
        if self._callback_failed:
            failures.append(ProbeFault("INTERNAL_ERROR"))
        return failures[0] if failures else None

    def __enter__(self):
        self._counts_complete = False
        if self.active or self._acquired:
            raise ProbeFault("PROFILE_HOOK_ALREADY_PRESENT")
        self._callback_failed = False
        self._admitted = False
        try:
            self.previous = sys.getprofile()
            if self.previous is not None:
                raise ProbeFault("PROFILE_HOOK_ALREADY_PRESENT")
            self._owner_thread = self._get_ident()
            monitor, tool = self._monitor, self._tool_id
            if monitor.get_tool(tool) is not None:
                raise ProbeFault("PROFILE_HOOK_ALREADY_PRESENT")
            monitor.use_tool_id(tool, self._name)
            self._acquired = True
            if monitor.get_events(tool) != 0 or any(
                monitor.get_local_events(tool, code) != 0 for code in self._codes
            ):
                raise ProbeFault("PROFILE_HOOK_ALREADY_PRESENT")
            self._admitted = True
            self._prior_start = monitor.register_callback(tool, self._start, self._callback)
            self._installed = True
            if self._prior_start is not None:
                raise ProbeFault("PROFILE_HOOK_ALREADY_PRESENT")
            for code in self._codes:
                # CPython may mutate the mask before instrumentation can fail.
                self._attempted.append(code)
                monitor.set_local_events(tool, code, self._start)
                if monitor.get_local_events(tool, code) != self._start:
                    raise ProbeFault("INTERNAL_ERROR")
            self.active = True
            return self
        except BaseException as error:
            cleanup_error = self._cleanup(False)
            if cleanup_error is not None:
                raise ProbeFault("INTERNAL_ERROR") from cleanup_error
            if isinstance(error, ProbeFault) or not isinstance(error, Exception):
                raise
            raise ProbeFault("INTERNAL_ERROR") from error

    def __exit__(self, *_exception):
        was_active = self.active
        self._counts_complete = False
        failure = self._cleanup(was_active)
        if failure is not None:
            raise ProbeFault("INTERNAL_ERROR") from failure
        self._counts_complete = was_active and not self._callback_failed
        return False


def _check_pin(path, count, digest, code):
    raw = read_bounded(path, count)
    if len(raw) != count or hashlib.sha256(raw).hexdigest() != digest:
        raise ProbeFault(code)
    return {"path": str(path), "bytes": len(raw), "sha256": digest}


def _frozen_expectations():
    """Convert the existing fixed pins to the private reader's exact layout."""
    return {
        "suppliers": [
            {
                "module": module,
                "path": "ontolearn_engine/" + relative,
                "bytes": count,
                "sha256": digest,
            }
            for module, relative, count, digest in SUPPLIER_PINS
        ],
        "publicResources": [
            {"path": "contracts/" + relative, "bytes": count, "sha256": digest}
            for relative, count, digest in PUBLIC_RESOURCE_PINS
        ],
        "inputs": [
            {
                "path": "ontolearn_engine/probe_inputs/" + MANIFEST_NAME,
                "bytes": MANIFEST_BYTES,
                "sha256": MANIFEST_SHA256,
            },
            {
                "path": "ontolearn_engine/probe_inputs/" + INPUT_NAME,
                "bytes": 8205267,
                "sha256": "47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa",
            },
        ],
        "lock": {"path": "uv.lock", "bytes": LOCK_BYTES, "sha256": LOCK_SHA256},
        "distributions": dict(DISTRIBUTIONS),
    }


def check_runtime_preconditions():
    """Read identity before importing resources or any semantic implementation."""
    frozen = bool(getattr(sys, "frozen", False))
    package = Path(__file__).resolve().parent
    contracts = Path(sys._MEIPASS) / "contracts" if frozen else package.parents[2] / "contracts"
    lock = Path(sys._MEIPASS) / "provenance/uv.lock" if frozen else package.parents[3] / "uv.lock"
    resource_rows = [
        _check_pin(contracts / name, count, digest, "RESOURCE_IDENTITY_INVALID")
        for name, count, digest in PUBLIC_RESOURCE_PINS
    ]
    lock_row = _check_pin(lock, LOCK_BYTES, LOCK_SHA256, "LOCK_IDENTITY_INVALID")
    source_rows = []
    if not frozen:
        for module, relative, count, digest in SUPPLIER_PINS:
            row = _check_pin(package / relative, count, digest, "SOURCE_IDENTITY_INVALID")
            source_rows.append({"module": module, **row})
    versions = {}
    try:
        for name, expected in DISTRIBUTIONS.items():
            versions[name] = importlib.metadata.version(name)
            if versions[name] != expected:
                raise ProbeFault("DISTRIBUTION_IDENTITY_INVALID")
    except importlib.metadata.PackageNotFoundError:
        raise ProbeFault("DISTRIBUTION_UNAVAILABLE") from None
    if sys.version_info[:2] != (3, 12):
        raise ProbeFault("PYTHON_IDENTITY_INVALID")
    return {
        "frozen": frozen,
        "resources": resource_rows,
        "lock": lock_row,
        "sourceModules": source_rows,
        "distributions": versions,
        "packageCodeBoundToSource": "unknown" if frozen else "source-bytes-verified",
        "externalBuildProvenance": "unknown",
    }


def _code_fingerprint(code):
    def normalized(item):
        if type(item) is not types.CodeType:
            return item
        return item.replace(
            co_filename="<i05-canonical-code>",
            co_consts=tuple(normalized(value) for value in item.co_consts),
        )

    return {
        "algorithm": "i05-code-object-marshal-filename-normalized/1",
        "sha256": hashlib.sha256(marshal.dumps(normalized(code), 4)).hexdigest(),
        "pythonCacheTag": sys.implementation.cache_tag,
        "domain": "actual-loader-code; not source bytes or a build approval",
    }


def _runtime_modules(identity):
    modules, rows = {}, []
    frozen = identity["frozen"]
    package = Path(__file__).resolve().parent
    for name, relative, _count, declared_sha in SUPPLIER_PINS:
        module = importlib.import_module(name)
        if (
            module.__name__ != name
            or module.__spec__ is None
            or module.__spec__.name != name
            or sys.modules.get(name) is not module
        ):
            raise ProbeFault("MODULE_IDENTITY_INVALID")
        if not frozen and Path(module.__file__).resolve() != (package / relative).resolve():
            raise ProbeFault("MODULE_ORIGIN_INVALID")
        loader = module.__spec__.loader
        get_code = getattr(loader, "get_code", None)
        code = get_code(name) if callable(get_code) else None
        if not frozen:
            source = read_bounded(package / relative, _count)
            compiled = compile(
                source,
                str(package / relative),
                "exec",
                dont_inherit=True,
                optimize=sys.flags.optimize,
            )
            if type(code) is not types.CodeType or _code_fingerprint(code) != _code_fingerprint(
                compiled
            ):
                raise ProbeFault("LOADER_SOURCE_CODE_MISMATCH")
        rows.append(
            {
                "module": name,
                "specName": module.__spec__.name,
                "origin": module.__spec__.origin,
                "declaredSupplierSourceSha256": declared_sha,
                "actualSourceSha256": None if frozen else declared_sha,
                "actualCode": _code_fingerprint(code)
                if type(code) is types.CodeType
                else "unknown",
            }
        )
        modules[name] = module
    semantic = modules["ontolearn_engine.semantic"]
    from pyshacl.validator import Validator

    identity.update(
        {
            "modules": rows,
            "python": sys.version,
            "probeModule": __name__,
            "probeSpecName": __spec__.name if __spec__ else None,
            "functionCode": {
                "semantic.reason": _code_fingerprint(semantic.reason.__code__),
                "semantic.query": _code_fingerprint(semantic.query.__code__),
                "semantic.validate_shacl_text": _code_fingerprint(
                    semantic.validate_shacl_text.__code__
                ),
                "Validator.run": _code_fingerprint(Validator.run.__code__),
            },
            "semanticVersions": {
                "legacy": semantic.SEMANTICS_VERSION,
                "profile": "i05-finite-7",
                "explanation": "i05-finite-8",
                "shaclText": semantic.SHACL_TEXT_ENTRY_VERSION,
                "utcDateText": semantic._SHACL_DATE_ENTRY_VERSION,
                "utcDatePolicy": semantic._UTC_DATE_RANGE_POLICY,
            },
            "policyVersions": {
                "comparisonProfile": modules["ontolearn_engine.quality.rule_profile"].PROFILE,
                "mechanismBudget": modules["ontolearn_engine.quality.rule_profile"].BUDGET_VERSION,
                "material": modules["ontolearn_engine.semantic_profile_input"].MATERIAL_VERSION,
                "captureBudget": (
                    modules["ontolearn_engine.semantic_profile_input"].CAPTURE_BUDGET_VERSION
                ),
                "restoreSchema": modules[
                    "ontolearn_engine.semantic_profile_restore"
                ].SCHEMA_VERSION,
                "restoreBudget": (
                    modules[
                        "ontolearn_engine.semantic_profile_restore_budget"
                    ].RESTORE_BUDGET_VERSION
                ),
                "restoreCache": (
                    modules[
                        "ontolearn_engine.semantic_profile_restore_budget"
                    ].RESTORE_CACHE_VERSION
                ),
                "directSteps": modules["ontolearn_engine.semantic_profile_directsteps"].VERSION,
                "directBudget": modules[
                    "ontolearn_engine.semantic_profile_directsteps"
                ].BUDGET_VERSION,
            },
            "probeWriter": {
                "sourceSha256": None
                if frozen
                else hashlib.sha256(read_bounded(Path(__file__), ITEM_CAP)).hexdigest(),
                "code": _code_fingerprint(sys.modules[__name__].__spec__.loader.get_code(__name__)),
            },
            "contractModule": {
                "name": modules["ontolearn_engine.resources"].CONTRACT.__name__,
                "specName": modules["ontolearn_engine.resources"].CONTRACT.__spec__.name,
                "origin": modules["ontolearn_engine.resources"].CONTRACT.__spec__.origin,
                "usesCanonicalResourcesObject": True,
            },
            "pyinstaller": "unknown; source candidate not built",
            "platform": sys.platform,
            "architecture": "unknown",
            "cpu": "unknown",
            "physicalMemory": "unknown",
        }
    )
    return modules, Validator


def _bytes_value(raw):
    return {
        "encoding": "base64",
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "data": base64.b64encode(raw).decode("ascii"),
    }


def _graph_value(graph):
    return {
        "triples": sorted(tuple(term.n3() for term in triple) for triple in graph),
        "tripleCount": len(graph),
    }


def _typed_value(value, approved, *, budget=None, depth=0):
    """Observe fixed canonical dataclass fields only; never reconstruct a result."""
    budget = [ITEM_CAP] if budget is None else budget
    budget[0] -= 1
    if budget[0] < 0 or depth > 96:
        raise ProbeFault("OUTPUT_ITEM_LIMIT")
    kind = type(value)
    if value is None or kind is bool:
        return value
    if kind is int:
        size = value.bit_length() // 4 + 4
        if size > budget[0]:
            raise ProbeFault("OUTPUT_ITEM_LIMIT")
        text = hex(value)
        budget[0] -= len(text)
        return {"integerHex": text}
    if kind is str:
        if 6 * len(value) + 2 > budget[0]:
            raise ProbeFault("OUTPUT_ITEM_LIMIT")
        budget[0] -= 6 * len(value) + 2
        return value
    if kind is bytes:
        size = 4 * ((len(value) + 2) // 3) + 256
        if size > budget[0]:
            raise ProbeFault("OUTPUT_ITEM_LIMIT")
        budget[0] -= size
        return _bytes_value(value)
    if kind in (tuple, list):
        if len(value) > budget[0]:
            raise ProbeFault("OUTPUT_ITEM_LIMIT")
        return [_typed_value(item, approved, budget=budget, depth=depth + 1) for item in value]
    if kind is dict:
        if len(value) > budget[0] or any(type(key) is not str for key in value):
            raise ProbeFault("OUTPUT_TYPE_INVALID")
        return {
            key: _typed_value(item, approved, budget=budget, depth=depth + 1)
            for key, item in value.items()
        }
    if kind not in approved or not is_dataclass(value):
        raise ProbeFault("OUTPUT_TYPE_INVALID")
    return {
        "recordType": kind.__module__ + "." + kind.__qualname__,
        "fields": {
            field.name: _typed_value(
                getattr(value, field.name),
                approved,
                budget=budget,
                depth=depth + 1,
            )
            for field in fields(kind)
        },
    }


def _approved_types(modules):
    from dataclasses import is_dataclass as declared_dataclass

    # Exact objects from the already-verified canonical modules. No saved tag imports a class.
    result = set()
    for module in modules.values():
        for value in vars(module).values():
            if type(value) is type and declared_dataclass(value) and value.__module__ in modules:
                result.add(value)
    return frozenset(result)


def _validate_nested_assets(manifest, inputs):
    """Structural input whitelist, including legitimate rule definition heads."""

    def sha(value):
        if (
            type(value) is not str
            or len(value) != 64
            or any(c not in "0123456789abcdef" for c in value)
        ):
            raise ProbeFault("ASSET_SCHEMA_INVALID")

    def reference(value):
        if type(value) is not dict or set(value) not in (
            {"ref", "path", "sha256", "pointer"},
            {"ref", "path", "sha256", "pointer", "physicalLine"},
        ):
            raise ProbeFault("ASSET_SCHEMA_INVALID")
        for key in ("ref", "path", "pointer"):
            _text(value[key])
        sha(value["sha256"])
        if "physicalLine" in value and (
            type(value["physicalLine"]) is not int or value["physicalLine"] < 1
        ):
            raise ProbeFault("ASSET_SCHEMA_INVALID")

    def source(value):
        if value is None:
            return
        _exact(value, ("reference", "digest", "revision", "text"))
        for item in value.values():
            if item is not None:
                _text(item)

    def term(value):
        if type(value) is dict and set(value) == {"variable"}:
            _text(value["variable"])
            return
        _exact(value, ("kind", "lexical_form", "datatype_iri", "language_raw", "source"))
        for key in ("kind", "lexical_form"):
            _text(value[key])
        for key in ("datatype_iri", "language_raw"):
            if value[key] is not None:
                _text(value[key])
        source(value["source"])

    def triple(value):
        _list(value)
        if len(value) != 3:
            raise ProbeFault("ASSET_SCHEMA_INVALID")
        for item in value:
            term(item)

    def structured_rule(value):
        _exact(
            value,
            (
                "rule_id",
                "when",
                "comparisons",
                "heads",
                "source",
                "revision",
                "definition_digest",
                "policy",
            ),
        )
        for key in ("rule_id", "policy"):
            _text(value[key])
        for key in ("revision", "definition_digest"):
            if value[key] is not None:
                _text(value[key])
        source(value["source"])
        for key in ("when", "heads"):
            _list(value[key])
            for item in value[key]:
                triple(item)
        _list(value["comparisons"])
        for item in value["comparisons"]:
            _exact(item, ("left", "operator", "right"))
            term(item["left"])
            term(item["right"])
            _text(item["operator"])

    def raw_triple(value):
        _exact(value, ("subject", "predicate", "object"))
        for item in value.values():
            _text(item)

    for dataset in inputs["datasets"].values():
        for rule in dataset.get("rules", ()):
            structured_rule(rule)
        for record in dataset.get("records", ()):
            triple(record)
        for replacement in dataset.get("replaceEquipmentTypes", ()):
            _exact(replacement, ("subject", "type"))
            for item in replacement.values():
                _text(item)
        if dataset["kind"] == "b1" and (
            type(dataset["scale"]) is not int
            or dataset["scale"] not in (1, 10)
            or type(dataset["seed"]) is not int
            or dataset["seed"] != 20261019
        ):
            raise ProbeFault("ASSET_SCHEMA_INVALID")
        if dataset["kind"] == "profile":
            raw = dataset["input"]
            for key in ("asserted", "ontology", "definitions", "disabled_rule_ids"):
                _list(raw[key])
            for key in ("asserted", "ontology"):
                for record in raw[key]:
                    if type(record) is not dict or set(record) not in (
                        {"triple", "source"},
                        {"triple", "source", "transformRefs"},
                    ):
                        raise ProbeFault("ASSET_SCHEMA_INVALID")
                    raw_triple(record["triple"])
                    reference(record["source"])
                    if "transformRefs" in record:
                        _list(record["transformRefs"])
                        for item in record["transformRefs"]:
                            reference(item)
            for definition in raw["definitions"]:
                _exact(
                    definition,
                    (
                        "rule_id",
                        "enabled",
                        "when",
                        "comparisons",
                        "heads",
                        "revision",
                        "definitionJsonValueSha256",
                        "source",
                        "rawTurtle",
                        "rawTurtleSpan",
                    ),
                )
                if type(definition["enabled"]) is not bool:
                    raise ProbeFault("ASSET_SCHEMA_INVALID")
                for key in ("rule_id", "revision"):
                    if definition[key] is not None:
                        _text(definition[key])
                sha(definition["definitionJsonValueSha256"])
                reference(definition["source"])
                if definition["rawTurtle"] is not None:
                    _text(definition["rawTurtle"])
                if definition["rawTurtleSpan"] is not None:
                    _list(definition["rawTurtleSpan"])
                    if len(definition["rawTurtleSpan"]) != 2 or any(
                        type(v) is not int or v < 0 for v in definition["rawTurtleSpan"]
                    ):
                        raise ProbeFault("ASSET_SCHEMA_INVALID")
                for key in ("when", "heads"):
                    _list(definition[key])
                    for item in definition[key]:
                        raw_triple(item)
                _list(definition["comparisons"])
                for item in definition["comparisons"]:
                    _exact(item, ("left", "operator", "right"))
                    for value in item.values():
                        _text(value)
            for item in raw["disabled_rule_ids"]:
                _text(item)
    family_counts = {}
    for observation in inputs["observations"]:
        if observation["contextStatus"] not in ("complete", "fragment", "not-executed"):
            raise ProbeFault("ASSET_CONTEXT_INVALID")
        family_counts[observation["family"]] = family_counts.get(observation["family"], 0) + 1
        for ref in observation["sourceRefs"]:
            _exact(ref, ("ref", "path", "bytes", "sha256", "pointer"))
            if type(ref["bytes"]) is not int or ref["bytes"] < 0:
                raise ProbeFault("ASSET_SCHEMA_INVALID")
            for key in ("ref", "path", "sha256", "pointer"):
                _text(ref[key])
            sha(ref["sha256"])
        sha(observation["projectionSha256"])
        for key in ("rootsTargets",):
            for target in observation["parameters"].get(key, ()):
                _list(target)
                if len(target) != 3 or any(type(item) is not str for item in target):
                    raise ProbeFault("ASSET_SCHEMA_INVALID")
    context = inputs["contexts"]
    _exact(
        manifest["counts"],
        (
            "observations",
            "datasets",
            "mathInputContexts",
            "originalOperations",
            "productCases",
            "learningChecks",
            "unresolved",
            "families",
        ),
    )
    for key in (
        "mathInputContexts",
        "originalOperations",
        "productCases",
        "learningChecks",
        "unresolved",
    ):
        if type(manifest["counts"][key]) is not int or manifest["counts"][key] != len(context[key]):
            raise ProbeFault("ASSET_COUNT_INVALID")
    if manifest["counts"]["families"] != family_counts:
        raise ProbeFault("ASSET_COUNT_INVALID")
    eligible = full = intersection = 0
    for index, item in enumerate(context["mathInputContexts"]):
        _exact(
            item,
            (
                "index",
                "id",
                "sourceRefs",
                "inputProjectionJsonSha256",
                "eligibleStandaloneMathInput",
                "fullOriginalInputContext",
                "scopeNotes",
                "lifecycleExecuted",
                "originalRequestedOperationPassed",
                "sourceAuthorityAuthenticated",
            ),
        )
        if type(item["index"]) is not int or item["index"] != index:
            raise ProbeFault("ASSET_CONTEXT_INVALID")
        _text(item["id"])
        sha(item["inputProjectionJsonSha256"])
        _list(item["sourceRefs"])
        for value in item["sourceRefs"]:
            reference(value)
        _list(item["scopeNotes"])
        for key in ("eligibleStandaloneMathInput", "fullOriginalInputContext"):
            if type(item[key]) is not bool:
                raise ProbeFault("ASSET_CONTEXT_INVALID")
        eligible += item["eligibleStandaloneMathInput"]
        full += item["fullOriginalInputContext"]
        intersection += item["eligibleStandaloneMathInput"] and item["fullOriginalInputContext"]
    repair = context["mathInputContexts"][77]
    if (eligible, full, intersection) != (82, 79, 78) or (
        repair["eligibleStandaloneMathInput"] is not False
        or repair["fullOriginalInputContext"] is not True
    ):
        raise ProbeFault("ASSET_CONTEXT_INVALID")
    for item in context["originalOperations"]:
        _exact(
            item,
            (
                "caseId",
                "decision",
                "group",
                "id",
                "lifecycleExecuted",
                "mathInputId",
                "notes",
                "op",
                "ordinal",
                "originalOperationExecuted",
                "source",
            ),
        )
        reference(item["source"])
        if (
            item.get("lifecycleExecuted") is not False
            or item.get("originalOperationExecuted") is not False
        ):
            raise ProbeFault("ASSET_CONTEXT_INVALID")
    for item in context["learningChecks"]:
        _exact(
            item,
            (
                "caseRef",
                "checkExecuted",
                "courseInputRefs",
                "extraInputStatus",
                "id",
                "linkedProductCase",
                "source",
                "toolOwner",
            ),
        )
        reference(item["source"])
        if item.get("checkExecuted") is not False:
            raise ProbeFault("ASSET_CONTEXT_INVALID")
    for item in context["productCases"]:
        _exact(
            item,
            (
                "caseId",
                "independentBaseline",
                "mathInputs",
                "operationRefs",
                "originalLifecycleAndNonGraphAcceptance",
                "source",
            ),
        )
        reference(item["source"])
        if item.get("originalLifecycleAndNonGraphAcceptance") != "not-executed":
            raise ProbeFault("ASSET_CONTEXT_INVALID")
    _list(context["nonClaims"])
    if len(context["nonClaims"]) != 3 or any(
        type(item) is not str for item in context["nonClaims"]
    ):
        raise ProbeFault("ASSET_CONTEXT_INVALID")
    for source_row in manifest["sources"]:
        _exact(source_row, ("ref", "path", "bytes", "sha256", "corpusPath"))
        for key in ("ref", "path", "corpusPath"):
            _text(source_row[key])
        sha(source_row["sha256"])
        if type(source_row["bytes"]) is not int or source_row["bytes"] < 0:
            raise ProbeFault("ASSET_SCHEMA_INVALID")
    for item in context["unresolved"]:
        _exact(item, ("gap", "id", "source"))
        reference(item["source"])
    if manifest["versions"] != {
        "supplierRef": ASSET_SUPPLIER_REF,
        "contractRef": "ee2b30a2dad35b2d395f9c735aff80371ab41110",
        "b1InputMethodRef": "523c478d5f39671c4ac7c1ea6997e51d3047d58e",
        "generator": "input-only-stdlib/1",
        "datasetCanonicalization": "json-ascii-sorted-compact/1",
    }:
        raise ProbeFault("ASSET_VERSION_INVALID")


def _source_record(raw, modules):
    if raw is None:
        return None
    return modules["ontolearn_engine.quality.rule_profile"].SourceRecord(**raw)


def _term_input(raw, modules):
    firing = modules["ontolearn_engine.quality.rule_firing"]
    profile = modules["ontolearn_engine.quality.rule_profile"]
    if set(raw) == {"variable"}:
        return firing.Variable(raw["variable"])
    return profile.TermInput(
        raw["kind"],
        raw["lexical_form"],
        raw["datatype_iri"],
        raw["language_raw"],
        _source_record(raw["source"], modules),
    )


def _structured_inputs(dataset, modules):
    firing = modules["ontolearn_engine.quality.rule_firing"]

    def triple(raw):
        return firing.Triple(*(_term_input(term, modules) for term in raw))

    rules = tuple(
        firing.RuleSpec(
            raw["rule_id"],
            tuple(triple(item) for item in raw["when"]),
            tuple(
                firing.Comparison(
                    _term_input(item["left"], modules),
                    item["operator"],
                    _term_input(item["right"], modules),
                )
                for item in raw["comparisons"]
            ),
            tuple(triple(item) for item in raw["heads"]),
            _source_record(raw["source"], modules),
            raw["revision"],
            raw["definition_digest"],
            raw["policy"],
        )
        for raw in dataset.get("rules", ())
    )
    # The producer accepts tuples of TermInput triples, not rule Triple objects.
    records = tuple(
        tuple(_term_input(item, modules) for item in raw) for raw in dataset.get("records", ())
    )
    return records, rules, ()


def _original_profile_inputs(dataset, dataset_id, input_sha, modules):
    """Construct original syntax only, using the single canonical lexical adapter."""
    firing = modules["ontolearn_engine.quality.rule_firing"]
    profile = modules["ontolearn_engine.quality.rule_profile"]
    decode = modules["ontolearn_engine.semantic_turtle"].decode_profile_term
    raw = dataset["input"]
    prefix = (
        INPUT_NAME + "#/datasets/" + dataset_id.replace("~", "~0").replace("/", "~1") + "/input"
    )

    def source(pointer, text=None, revision=None):
        return profile.SourceRecord(prefix + pointer, input_sha, revision, text)

    def term(value, pointer, iri=False):
        if value.startswith("?") and not iri:
            return firing.Variable(value)
        value_term = (
            profile.TermInput("iri", value) if iri else _checked_lexical_decode(decode, value)
        )
        return profile.TermInput(
            value_term.kind,
            value_term.lexical_form,
            value_term.datatype_iri,
            value_term.language_raw,
            source(pointer, value),
        )

    def triple(value, pointer, rule=False):
        terms = tuple(
            term(
                value[key],
                pointer + "/" + key,
                iri=(key in ("subject", "predicate") and not value[key].startswith("?")),
            )
            for key in ("subject", "predicate", "object")
        )
        return firing.Triple(*terms) if rule else terms

    records = tuple(
        triple(item["triple"], f"/{section}/{index}/triple")
        for section in ("asserted", "ontology")
        for index, item in enumerate(raw[section])
    )
    rules = []
    for index, definition in enumerate(raw["definitions"]):
        pointer = f"/definitions/{index}"
        rules.append(
            firing.RuleSpec(
                definition["rule_id"],
                tuple(
                    triple(item, f"{pointer}/when/{n}", True)
                    for n, item in enumerate(definition["when"])
                ),
                tuple(
                    firing.Comparison(
                        term(item["left"], f"{pointer}/comparisons/{n}/left"),
                        item["operator"],
                        term(item["right"], f"{pointer}/comparisons/{n}/right"),
                    )
                    for n, item in enumerate(definition["comparisons"])
                ),
                tuple(
                    triple(item, f"{pointer}/heads/{n}", True)
                    for n, item in enumerate(definition["heads"])
                ),
                source(pointer, revision=definition["revision"]),
                definition["revision"],
                definition["definitionJsonValueSha256"],
            )
        )
    return records, tuple(rules), tuple(raw["disabled_rule_ids"])


def _legacy_rules(dataset, modules):
    from rdflib import Literal, URIRef, Variable

    def term(raw):
        if set(raw) == {"variable"}:
            return Variable(raw["variable"].removeprefix("?"))
        if raw["kind"] == "iri":
            return URIRef(raw["lexical_form"])
        if raw["kind"] == "literal":
            return Literal(
                raw["lexical_form"],
                lang=raw["language_raw"],
                datatype=URIRef(raw["datatype_iri"]) if raw["datatype_iri"] else None,
                normalize=False,
            )
        raise ProbeFault("LEGACY_INPUT_NOT_SUPPORTED")

    result = []
    for rule in dataset["rules"]:
        if rule["comparisons"] or len(rule["heads"]) != 1:
            raise ProbeFault("LEGACY_INPUT_NOT_SUPPORTED")
        result.append(
            modules["ontolearn_engine.semantic"].Rule(
                rule["rule_id"],
                tuple(tuple(term(item) for item in triple) for triple in rule["when"]),
                tuple(term(item) for item in rule["heads"][0]),
            )
        )
    return tuple(result)


def _catalog(modules):
    resources = modules["ontolearn_engine.resources"]
    contract = resources.CONTRACT
    return {
        "error_catalog": contract.ERROR_CATALOG,
        "error_schema": strict_json(read_bounded(resources.ROOT / "v2/schema.json", 207256)),
    }


def _known_failure(error, modules):
    """Known business rejection never implies an oracle pass."""
    semantic = modules["ontolearn_engine.semantic_offline"]
    execution = modules["ontolearn_engine.semantic_execution"]
    material = modules["ontolearn_engine.semantic_profile_input"]
    restore = modules["ontolearn_engine.semantic_profile_restore_budget"]
    direct = modules["ontolearn_engine.semantic_profile_directsteps"]
    if isinstance(error, execution.ProfileExecutionFault):
        code = error.error.get("code") if type(error.error) is dict else None
        if (
            type(code) is not str
            or code == "INTERNAL_ERROR"
            or (
                type(error.diagnostic) is dict
                and error.diagnostic.get("classification") == "internal"
            )
        ):
            return None
        return error.error, error.diagnostic
    if isinstance(error, semantic.SemanticError):
        code = error.code
        if (
            type(code) is not str
            or getattr(error, "classification", None) == "internal"
            or code
            in {
                "INTERNAL_ERROR",
                "QUERY_FAILED",
                "VALIDATION_FAILED",
                "EXECUTION_FAILED",
            }
        ):
            return None
        diagnostic = {
            "classification": getattr(error, "classification", "observed-business-rejection")
        }
        for key in ("location", "rule_id", "context"):
            if hasattr(error, key):
                value = getattr(error, key)
                diagnostic[key] = _typed_value(value, _approved_types(modules))
        return {"kind": "semantic", "code": code}, diagnostic
    classes = (material.MaterialFailure, restore.RestoreFailure, direct.DirectStepsFailure)
    if type(error) in classes:
        code = error.reason
        if (
            type(code) is not str
            or "INTERNAL" in code
            or getattr(error, "classification", None) == "internal"
        ):
            return None
        return {"kind": type(error).__name__, "code": code}, {
            key: getattr(error, key, None) for key in ("classification", "stage", "slot", "domain")
        }
    return None


def _scope_observation(dataset, mode, modules, counter):
    if counter is None:
        raise ProbeFault("INTERNAL_ERROR")
    semantic = modules["ontolearn_engine.semantic"]
    scopes = modules["ontolearn_engine.semantic_scopes"]
    asserted = _checked_call(
        "scope/assertedParse",
        "semantic.parse_turtle",
        semantic.parse_turtle,
        dataset["assertedText"],
    )
    ontology = _checked_call(
        "scope/ontologyParse",
        "semantic.parse_turtle",
        semantic.parse_turtle,
        dataset["ontologyText"],
    )
    shapes = _checked_call(
        "scope/shapesParse",
        "semantic.parse_turtle",
        semantic.parse_turtle,
        dataset["shapesText"],
        shapes=True,
    )
    rules = _legacy_rules(dataset, modules)
    stages = []
    counter.scope_details = {
        "assertedInput": _graph_value(asserted),
        "ontologyInput": _graph_value(ontology),
        "shapesInput": _graph_value(shapes),
        "stages": stages,
    }

    def stage(name, call):
        before = dict(counter.counts)
        try:
            value = _checked_call(
                "scope/" + name,
                "semantic_scopes."
                + ("prepare_validation_scope" if name == "prepare" else "project_validation_scope"),
                call,
            )
        except Exception:
            boundary = _COLLECTION_CONTEXT.get()
            returned = bool(
                boundary is not None and boundary.attempts and boundary.attempts[-1]["returned"]
            )
            stages.append(
                {
                    "name": name,
                    "stageCompleted": False,
                    "apiReturned": returned,
                    "callCounts": {key: counter.counts[key] - before[key] for key in before},
                }
            )
            raise
        stages.append(
            {
                "name": name,
                "callCounts": {key: counter.counts[key] - before[key] for key in before},
                "facts": _graph_value(value.facts),
                "ontology": _graph_value(value.ontology),
                "provenance": value.provenance,
                "reasoningResult": value.reasoning_result,
            }
        )
        return value

    if mode in ("asserted", "fresh", "project"):
        prepared = stage(
            "prepare",
            lambda: scopes.prepare_validation_scope(
                asserted,
                ontology,
                include_derived=mode != "asserted",
                rules=() if mode == "asserted" else rules,
            ),
        )
        if mode == "project":
            prepared = stage(
                "project",
                lambda: scopes.project_validation_scope(
                    asserted,
                    ontology,
                    include_derived=True,
                    rules=rules,
                    reasoning_result=prepared.reasoning_result,
                    reasoning_source=prepared.provenance["reasoningSource"],
                ),
            )
    elif mode in ("missing-source", "wrong-source", "missing-result", "unselected-result"):
        fresh = stage(
            "prepare",
            lambda: scopes.prepare_validation_scope(
                asserted, ontology, include_derived=True, rules=rules
            ),
        )
        source = fresh.provenance["reasoningSource"]
        if mode == "wrong-source":
            source = {**source, "assertedInputSha256": "0" * 64}
        prepared = stage(
            "project",
            lambda: scopes.project_validation_scope(
                asserted,
                ontology,
                include_derived=mode != "unselected-result",
                rules=() if mode == "unselected-result" else rules,
                reasoning_result=None if mode == "missing-result" else fresh.reasoning_result,
                reasoning_source=None if mode == "missing-source" else source,
            ),
        )
    else:
        prepared = stage(
            "prepare",
            lambda: scopes.prepare_validation_scope(
                ontology if mode == "facts-axioms" else asserted,
                ontology,
                include_derived=1 if mode == "nonexact-include" else False,
                rules=rules if mode == "unselected-rules" else (),
            ),
        )
    query = _checked_call(
        "scope/query", "semantic.query", semantic.query, prepared.facts, dataset["queryText"]
    )
    report = _checked_call(
        "scope/shacl", "semantic.check_shapes", semantic.check_shapes, prepared.facts, shapes
    )
    return {**counter.scope_details, "query": query, "report": report}


def _capture_expectation(produced, explanation, modules):
    restore = modules["ontolearn_engine.semantic_profile_restore"]
    cls = restore.ExplanationRestoreExpectation if explanation else restore.RestoreExpectation
    payload = produced.wire["payload"]
    return cls(
        payload_digest=hashlib.sha256(produced.payload_json).hexdigest(),
        rows_digest=hashlib.sha256(produced.rows_json).hexdigest(),
        input_digest=payload["inputDigest"],
        input_domain=payload["inputDigestDomain"],
        source_digest=payload["sourceDigest"],
        definitions_digest=payload["definitionsDigest"],
        catalog_digest=hashlib.sha256(produced.catalog_json).hexdigest(),
        implementation=tuple(sorted(payload["implementation"].items())),
        input_preimage=produced.material.input_preimage,
        source_preimage=produced.material.source_preimage,
    )


def _restore(produced, expectation, explanation, modules, *, payload=None, rows=None):
    restore = modules["ontolearn_engine.semantic_profile_restore"]
    ledger = modules["ontolearn_engine.semantic_profile_restore_budget"].RestoreLedger()
    direct = modules["ontolearn_engine.semantic_profile_directsteps"].DirectStepsLedger()
    kwargs = {"expected": expectation, "allocation": produced.original_allocation, "ledger": ledger}
    if explanation:
        kwargs["direct_ledger"] = direct
    function = (
        restore.restore_profile_explanation_result
        if explanation
        else restore.restore_profile_result
    )
    restored = _checked_call(
        "restore/mutation" if payload is not None else "restore/result",
        "semantic_profile_restore." + function.__name__,
        function,
        produced.payload_json if payload is None else payload,
        produced.rows_json if rows is None else rows,
        **kwargs,
    )
    return restored


def _production_observation(dataset, observation, manifest, modules, approved):
    parameters = observation["parameters"]
    explanation = observation["operation"] == "dag" or parameters.get("explanation", False)
    material_api = modules["ontolearn_engine.semantic_profile_input"]
    production = modules["ontolearn_engine.semantic_profile_production"]
    direct_api = modules["ontolearn_engine.semantic_profile_directsteps"]
    restore_api = modules["ontolearn_engine.semantic_profile_restore"]
    ledger = material_api.CaptureLedger()
    if dataset["kind"] == "profile":
        records, rules, disabled = _original_profile_inputs(
            dataset, observation["datasetId"], manifest["inputAsset"]["sha256"], modules
        )
    else:
        records, rules, disabled = _structured_inputs(dataset, modules)
    kwargs = {"rules": rules, "disabled_rule_ids": disabled, "ledger": ledger}
    if parameters.get("materialMode", "records") == "text":
        kwargs.update(
            text=dataset["text"],
            source_reference=observation["datasetId"],
            source_revision=SOURCE_REF,
        )
    else:
        kwargs["records"] = records
    material = _checked_call(
        "material/prepare",
        "semantic_profile_input.prepare_profile_material",
        material_api.prepare_profile_material,
        **kwargs,
    )
    # Preparation transfers its receipt. Production independently rechecks using a new ledger.
    ledger = material_api.CaptureLedger()
    if explanation:
        produced = _checked_call(
            "production/compute",
            "semantic_profile_production.execute_profile_explanation",
            production.execute_profile_explanation,
            material,
            **_catalog(modules),
            ledger=ledger,
            direct_ledger=direct_api.DirectStepsLedger(),
        )
    else:
        produced = _checked_call(
            "production/compute",
            "semantic_profile_production.execute_admitted_profile_job",
            production.execute_admitted_profile_job,
            material,
            **_catalog(modules),
            ledger=ledger,
        )
    expected = _checked_call(
        "production/expectation",
        "probe._capture_expectation",
        _capture_expectation,
        produced,
        explanation,
        modules,
    )
    restored = _restore(produced, expected, explanation, modules)
    roots = ()
    if explanation:
        roots = _checked_call(
            "restore/roots",
            "semantic_profile_restore.explanation_roots",
            restore_api.explanation_roots,
            restored,
            tuple(tuple(item) for item in parameters.get("rootsTargets", ())),
            direct_ledger=direct_api.DirectStepsLedger(),
        )
    boundary = _COLLECTION_CONTEXT.get()
    if boundary is not None:
        boundary.stage, boundary.api = "production/serialize", None
    result = {
        "wire": produced.wire,
        "payloadBytes": _bytes_value(produced.payload_json),
        "rowsBytes": _bytes_value(produced.rows_json),
        "sourceBytes": _bytes_value(produced.source_encoded),
        "definitionBytes": _bytes_value(produced.definitions_encoded),
        "catalogBytes": _bytes_value(produced.catalog_json),
        "actualDefinitions": _typed_value(produced.actual_definitions, approved),
        "actualCatalog": _typed_value(produced.actual_catalog, approved),
        "allocation": _typed_value(produced.original_allocation, approved),
        "expectedCapture": _typed_value(expected, approved),
        "restored": _typed_value(restored, approved),
        "roots": _typed_value(roots, approved),
        "receipts": {
            "capture": _typed_value(produced.capture_receipt, approved),
            "direct": _typed_value(produced.direct_receipt, approved) if explanation else None,
        },
    }
    if observation["operation"] == "restore-negative":
        bad_payload, bad_rows, mutation_receipt = _mutate_current_payload(
            produced.payload_json, parameters["mutation"]
        )
        result["mutation"] = {
            "name": parameters["mutation"],
            "changes": mutation_receipt,
            "payloadBytes": _bytes_value(bad_payload),
            "rowsBytes": _bytes_value(bad_rows),
            "expectedCapture": _typed_value(expected, approved),
            "allocationReissued": False,
            "expectationReissued": False,
            "onlyOuterDigestsRebound": False,
            "deepValidationReached": "unknown; original digest gate preserved",
        }
        try:
            bad_restored = _restore(
                produced, expected, explanation, modules, payload=bad_payload, rows=bad_rows
            )
        except Exception as error:
            failure = _known_failure(error, modules)
            if failure is None:
                raise
            result["mutation"].update(
                status="observed-rejection", error=failure[0], diagnostic=failure[1]
            )
        else:
            result["mutation"].update(
                status="observed-return", restored=_typed_value(bad_restored, approved)
            )
    return result


def _mutate_current_payload(payload_json, mutation):
    """Only a receiver copy; never issue another expectation or allocation."""
    payload = strict_json(payload_json)
    reasoning = payload["reasoning"]
    changes = []

    def change(parent, key, value, pointer):
        before = parent[key]
        if before == value:
            raise ProbeFault("MUTATION_WOULD_BE_NOOP")
        changes.append({"pointer": pointer, "before": before, "after": value})
        parent[key] = value

    def last(value):
        if type(value) is not list or not value:
            raise ProbeFault("MUTATION_FIXTURE_PRECONDITION")
        return len(value) - 1

    if mutation == "payload-unknown-key":
        if "mutationUnknown" in payload:
            raise ProbeFault("MUTATION_FIXTURE_PRECONDITION")
        payload["mutationUnknown"] = True
        changes.append({"pointer": "/mutationUnknown", "absentBefore": True, "after": True})
    elif mutation == "tail-source-tamper":
        values = reasoning["termSources"]
        index = last(values)
        term = values[index]["value"]
        pointer = f"/reasoning/termSources/{index}/value/source"
        if term["source"] is None:
            change(
                term,
                "source",
                {
                    "recordType": "SourceRecord",
                    "reference": "urn:i05:tampered",
                    "digest": None,
                    "revision": None,
                    "text": None,
                },
                pointer,
            )
        else:
            change(
                term["source"],
                "reference",
                "urn:i05:tampered:" + str(index),
                pointer + "/reference",
            )
    elif mutation == "tail-definition-tamper":
        values = reasoning["definitions"]
        index = last(values)
        change(
            values[index],
            "revision",
            "urn:i05:tampered:revision",
            f"/reasoning/definitions/{index}/revision",
        )
    elif mutation in ("tail-limits-tamper", "tail-child-tamper"):
        values = reasoning["mechanismBatches"]
        index = last(values)
        child = values[index]
        if mutation == "tail-limits-tamper":
            limits = child["limits"]["work"]
            change(
                limits,
                "integerHex",
                "0x0" if limits["integerHex"] != "0x0" else "0x1",
                f"/reasoning/mechanismBatches/{index}/limits/work/integerHex",
            )
        else:
            change(
                child,
                "ruleId",
                "urn:i05:tampered:child",
                f"/reasoning/mechanismBatches/{index}/ruleId",
            )
    elif mutation in ("dag-depth-plus-one", "dag-last-premise-forward"):
        values = reasoning["directSteps"]["steps"]
        index = last(values)
        step = values[index]
        if mutation == "dag-depth-plus-one":
            change(
                step["depth"],
                "integerHex",
                hex(int(step["depth"]["integerHex"], 16) + 1),
                f"/reasoning/directSteps/steps/{index}/depth/integerHex",
            )
        else:
            if len(step["premises"]) != 2:
                raise ProbeFault("MUTATION_FIXTURE_PRECONDITION")
            change(
                step["premises"],
                0,
                {"kind": "step", "ordinal": dict(step["ordinal"])},
                f"/reasoning/directSteps/steps/{index}/premises/0",
            )
    elif mutation == "leaf-rename-all":
        leaves = reasoning["proofLeaves"]
        last(leaves)
        old = leaves[0]["reference"]
        replacement = "i05-proof:" + ("0" * 64 if old != "i05-proof:" + "0" * 64 else "1" * 64)
        remaining = [1_000_000]

        def rename(value, pointer="", depth=0):
            remaining[0] -= 1
            if remaining[0] < 0 or depth > 96:
                raise ProbeFault("MUTATION_OBSERVER_LIMIT")
            if type(value) is dict:
                for key, item in value.items():
                    if type(item) is str and item == old:
                        change(value, key, replacement, pointer + "/" + key)
                    else:
                        rename(item, pointer + "/" + key, depth + 1)
            elif type(value) is list:
                for index, item in enumerate(value):
                    if type(item) is str and item == old:
                        change(value, index, replacement, pointer + "/" + str(index))
                    else:
                        rename(item, pointer + "/" + str(index), depth + 1)

        rename(payload)
    elif mutation == "head-occurrence-1023-15":
        values = reasoning["evidence"]
        last(values)
        item = values[0]
        change(
            item["firingIndex"],
            "integerHex",
            "0x3ff",
            "/reasoning/evidence/0/firingIndex/integerHex",
        )
        change(item["headIndex"], "integerHex", "0xf", "/reasoning/evidence/0/headIndex/integerHex")
    else:
        raise ProbeFault("MUTATION_NOT_FIXED")
    if not changes:
        raise ProbeFault("MUTATION_WOULD_BE_NOOP")
    raw = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(",", ":")
    ).encode("utf-8")
    if raw == payload_json:
        raise ProbeFault("MUTATION_WOULD_BE_NOOP")
    text = raw.decode("utf-8")
    rows = json.dumps(
        [[text[index : index + 8192]] for index in range(0, len(text), 8192)],
        ensure_ascii=False,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return raw, rows, changes


_AUDIT_CONTEXT = ContextVar("i05_probe_readonly_audit_observation", default=None)
_AUDIT_INSTALLED = False
_AUDIT_ORDER_KNOWN = False


def _install_audit_observer():
    """Observe event names only, before the canonical denial hook when possible."""
    global _AUDIT_INSTALLED, _AUDIT_ORDER_KNOWN
    if not _AUDIT_INSTALLED:
        _AUDIT_ORDER_KNOWN = "ontolearn_engine.semantic_offline" not in sys.modules

        def observe(event, _args):
            state = _AUDIT_CONTEXT.get()
            if state is not None and (
                event.startswith("socket.")
                or event in {"urllib.Request", "subprocess.Popen", "os.system", "os.posix_spawn"}
            ):
                state["attemptCount"] += 1
                if len(state["events"]) < 32:
                    state["events"].append(event)
                else:
                    state["eventNamesComplete"] = False

        sys.addaudithook(observe)
        _AUDIT_INSTALLED = True


def _offline_observation(dataset, action, modules):
    semantic = modules["ontolearn_engine.semantic"]
    state = {
        "attemptCount": 0,
        "events": [],
        "eventNamesComplete": True,
        "observerBeforeDenialHook": _AUDIT_ORDER_KNOWN,
        "denialHookInstalled": True,
        "externalAccessSucceeded": "unknown",
    }
    token = _AUDIT_CONTEXT.set(state)
    try:
        try:
            if action == "query":
                graph = _checked_call(
                    "offline/parse",
                    "semantic.parse_turtle",
                    semantic.parse_turtle,
                    dataset["dataText"],
                )
                value = _checked_call(
                    "offline/query", "semantic.query", semantic.query, graph, dataset["queryText"]
                )
            elif action == "shape":
                data = _checked_call(
                    "offline/dataParse",
                    "semantic.parse_turtle",
                    semantic.parse_turtle,
                    dataset["dataText"],
                )
                shapes = _checked_call(
                    "offline/shapesParse",
                    "semantic.parse_turtle",
                    semantic.parse_turtle,
                    dataset["shapesText"],
                    shapes=True,
                )
                value = _checked_call(
                    "offline/shacl", "semantic.check_shapes", semantic.check_shapes, data, shapes
                )
            elif action == "implicit-jsonld":
                from rdflib import Graph

                with modules["ontolearn_engine.semantic_offline"].offline():
                    value = _graph_value(
                        _checked_call(
                            "offline/implicitJsonld",
                            "rdflib.Graph.parse",
                            Graph().parse,
                            data=dataset["text"],
                            format=dataset["format"],
                        )
                    )
            else:
                value = _graph_value(
                    _checked_call(
                        "offline/parse",
                        "semantic.parse_turtle",
                        semantic.parse_turtle,
                        dataset["text"],
                        format=dataset["format"],
                        shapes=dataset["shapes"],
                    )
                )
        except Exception as error:
            failure = _known_failure(error, modules)
            if failure is None:
                raise
            return {
                "status": "observed-rejection",
                "error": failure[0],
                "diagnostic": failure[1],
                "audit": state,
            }
        return {"status": "observed-return", "value": value, "audit": state}
    finally:
        _AUDIT_CONTEXT.reset(token)


def _b1_observation(dataset, modules, instrumentation):
    """Future measurements of fixed pure inputs; no Store or heap/OS sampler."""
    from rdflib import RDF, Graph, URIRef

    semantic = modules["ontolearn_engine.semantic"]
    passes = []
    first_graphs = None
    for name in ("First", "Warm"):
        phases = {}

        def timed(phase, api, call, *, name=name, phases=phases):
            start = time.perf_counter_ns()
            value = _checked_call(name + "/" + phase, api, call)
            phases[phase] = {
                "elapsedNs": time.perf_counter_ns() - start,
                "pythonAllocation": "unknown",
                "processHighWaterRss": "unknown",
            }
            return value

        asserted = timed(
            "turtleParse",
            "semantic.parse_turtle",
            lambda: semantic.parse_turtle(dataset["assertedText"]),
        )
        ontology = timed(
            "ontologyParse",
            "semantic.parse_turtle",
            lambda: semantic.parse_turtle(dataset["ontologyText"]),
        )

        def build(*, asserted=asserted, ontology=ontology):
            # Explicit input transformation, not derived facts or an alternate reasoner.
            facts = Graph()
            for triple in asserted:
                facts.add(triple)
            for replacement in dataset["replaceEquipmentTypes"]:
                subject = URIRef(replacement["subject"])
                facts.remove((subject, RDF.type, None))
                facts.add((subject, RDF.type, URIRef(replacement["type"])))
            combined = Graph()
            for triple in facts:
                combined.add(triple)
            for triple in ontology:
                combined.add(triple)
            return facts, combined

        transformed, combined = timed("graphBuild", "probe.explicitInputGraphBuild", build)
        query = timed(
            "fixedSelect",
            "semantic.query",
            lambda *, combined=combined: semantic.query(combined, dataset["queryText"]),
        )
        reason = timed(
            "rdfsRules",
            "semantic.reason",
            lambda *, combined=combined: semantic.reason(combined, _legacy_rules(dataset, modules)),
        )
        shapes = timed(
            "shapesParse",
            "semantic.parse_turtle",
            lambda: semantic.parse_turtle(dataset["shapesText"], shapes=True),
        )
        report = timed(
            "shacl",
            "semantic.check_shapes",
            lambda *, asserted=asserted, shapes=shapes: semantic.check_shapes(asserted, shapes),
        )
        outputs = {
            "assertedOriginal": _graph_value(asserted),
            "transformedFacts": _graph_value(transformed),
            "ontology": _graph_value(ontology),
            "graph": _graph_value(combined),
            "query": query,
            "reason": reason,
            "report": report,
        }
        # The timer observes encoding only; JSONL transport/parent wall is a distinct domain.
        encoded = timed(
            "resultSerialization",
            "probe.canonical_bytes",
            lambda *, outputs=outputs: canonical_bytes(outputs),
        )
        passes.append(
            {
                "name": name,
                "phases": phases,
                "outputs": outputs,
                "serializationBytes": len(encoded),
                "serializationSha256": hashlib.sha256(encoded).hexdigest(),
            }
        )
        if first_graphs is None:
            first_graphs = (asserted, ontology, combined)
    asserted, ontology, combined = first_graphs
    return {
        "scale": dataset["scale"],
        "seed": dataset["seed"],
        "assertedInput": _graph_value(asserted),
        "ontology": _graph_value(ontology),
        "semanticGraph": _graph_value(combined),
        "actualCounts": {
            "asserted": len(asserted),
            "ontology": len(ontology),
            "merged": len(combined),
        },
        "inputSha256": hashlib.sha256(dataset["assertedText"].encode("utf-8")).hexdigest(),
        "ontologyTextSha256": hashlib.sha256(dataset["ontologyText"].encode("utf-8")).hexdigest(),
        "querySha256": hashlib.sha256(dataset["queryText"].encode("utf-8")).hexdigest(),
        "transformedGraphSha256": hashlib.sha256(
            canonical_bytes(_graph_value(combined))
        ).hexdigest(),
        "instrumentation": instrumentation,
        "coldClaim": False,
        "freshProcessRequestedBySelector": not instrumentation,
        "freshProcessExternallyVerified": False,
        "timer": "perf_counter_ns",
        "timerResolutionSeconds": time.get_clock_info("perf_counter").resolution,
        "importStartupWall": "unknown",
        "physicalColdRead": "unknown",
        "snapshotLoad": "not-executed; Store HOLD",
        "capacityThreshold": "unknown",
        "memoryMeasurementStatus": "unknown; requires later resource/tool ticket",
        "passes": passes,
    }


def _dispatch(observation, dataset, manifest, modules, approved, counter, instrumentation):
    semantic = modules["ontolearn_engine.semantic"]
    operation, parameters = observation["operation"], observation["parameters"]
    if operation == "parse":
        return _graph_value(
            _checked_call(
                "parse/turtle",
                "semantic.parse_turtle",
                semantic.parse_turtle,
                dataset["text"],
                format=dataset["format"],
                shapes=dataset["shapes"],
            )
        )
    if operation == "query":
        graph = _checked_call(
            "query/parse", "semantic.parse_turtle", semantic.parse_turtle, dataset["dataText"]
        )
        return _checked_call(
            "query/select", "semantic.query", semantic.query, graph, dataset["queryText"]
        )
    if operation == "legacy-reason":
        graph = _checked_call(
            "legacy/parse", "semantic.parse_turtle", semantic.parse_turtle, dataset["dataText"]
        )
        reason = _checked_call(
            "legacy/reason",
            "semantic.reason",
            semantic.reason,
            graph,
            _legacy_rules(dataset, modules),
        )
        return {"graph": _graph_value(graph), "reason": reason}
    if operation == "scope":
        return _scope_observation(dataset, parameters["mode"], modules, counter)
    if operation == "profile":
        records, rules, disabled = _original_profile_inputs(
            dataset, observation["datasetId"], manifest["inputAsset"]["sha256"], modules
        )
        return _checked_call(
            "profile/execute",
            "semantic_execution.execute_profile_records",
            modules["ontolearn_engine.semantic_execution"].execute_profile_records,
            records,
            rules,
            disabled_rule_ids=disabled,
            **_catalog(modules),
        )
    if operation in ("fullview", "dag", "restore-negative"):
        return _production_observation(dataset, observation, manifest, modules, approved)
    if operation == "shape":
        data = _checked_call(
            "shape/dataParse", "semantic.parse_turtle", semantic.parse_turtle, dataset["dataText"]
        )
        shapes = _checked_call(
            "shape/shapesParse",
            "semantic.parse_turtle",
            semantic.parse_turtle,
            dataset["shapesText"],
            shapes=True,
        )
        return _checked_call(
            "shape/shacl", "semantic.check_shapes", semantic.check_shapes, data, shapes
        )
    if operation == "shacl-text":
        kwargs = {}
        for incoming, keyword in (("dataPolicy", "data_policy"), ("rangePolicy", "range_policy")):
            if incoming in parameters:
                kwargs[keyword] = parameters[incoming]
        # A missing mandatory keyword is deliberately passed to the actual callable.
        return _checked_call(
            "shacl-text/validate",
            "semantic.validate_shacl_text",
            semantic.validate_shacl_text,
            dataset["dataText"],
            dataset["shapesText"],
            **kwargs,
        )
    if operation == "offline":
        return _checked_call(
            "offline/action",
            "probe._offline_observation",
            _offline_observation,
            dataset,
            parameters["action"],
            modules,
        )
    if operation == "b1-measurement":
        return _b1_observation(dataset, modules, instrumentation)
    raise ProbeFault("OPERATION_NOT_FIXED")


def _partial_value(value, modules, approved, *, depth=0):
    """Read actual completed values only; never publish an unfinished restore view."""
    from rdflib import Graph

    if depth > 96:
        raise ProbeFault("OUTPUT_ITEM_LIMIT")
    if type(value) is Graph:
        return _graph_value(value)
    production = modules["ontolearn_engine.semantic_profile_production"]
    if type(value) in (production.ProfileComputation, production.ProfileExplanationComputation):
        explanation = type(value) is production.ProfileExplanationComputation
        return {
            "wire": value.wire,
            "payloadBytes": _bytes_value(value.payload_json),
            "rowsBytes": _bytes_value(value.rows_json),
            "sourceBytes": _bytes_value(value.source_encoded),
            "definitionBytes": _bytes_value(value.definitions_encoded),
            "catalogBytes": _bytes_value(value.catalog_json),
            "material": _typed_value(value.material, approved),
            "nativeResult": _typed_value(value.native_result, approved),
            "actualDefinitions": _typed_value(value.actual_definitions, approved),
            "actualCatalog": _typed_value(value.actual_catalog, approved),
            "allocation": _typed_value(value.original_allocation, approved),
            "receipts": {
                "capture": _typed_value(value.capture_receipt, approved),
                "direct": _typed_value(value.direct_receipt, approved) if explanation else None,
            },
        }
    if type(value) is modules["ontolearn_engine.semantic_scopes"].ValidationScope:
        return {
            "facts": _graph_value(value.facts),
            "ontology": _graph_value(value.ontology),
            "provenance": value.provenance,
            "reasoningResult": value.reasoning_result,
        }
    kind = type(value)
    if value is None or kind in (bool, str, int):
        return value
    if kind is float and math.isfinite(value):
        return value
    if kind is bytes:
        return _bytes_value(value)
    if kind in (tuple, list):
        return [_partial_value(item, modules, approved, depth=depth + 1) for item in value]
    if kind is dict:
        if any(type(key) is not str for key in value):
            raise ProbeFault("OUTPUT_TYPE_INVALID")
        return {
            key: _partial_value(item, modules, approved, depth=depth + 1)
            for key, item in value.items()
        }
    return _typed_value(value, approved)


def _partial_outputs(boundary, modules, approved):
    return [
        {
            key: (_partial_value(value, modules, approved) if key == "value" else value)
            for key, value in item.items()
        }
        for item in boundary.completed
    ]


def _safe_stderr(stream, code):
    raw = canonical_bytes({"error": code}) + b"\n"
    try:
        stream.write(raw)
        if callable(getattr(stream, "flush", None)):
            stream.flush()
    except Exception:
        pass  # A broken error channel cannot turn an incomplete report into success.


def run_fixed_suite(selector, *, stdout=None, stderr=None, monotonic=None, cancel_requested=None):
    """The only collector; exit zero describes protocol collection, never acceptance."""
    stdout = getattr(sys.stdout, "buffer", None) if stdout is None else stdout
    stderr = getattr(sys.stderr, "buffer", sys.stderr) if stderr is None else stderr
    monotonic = time.monotonic if monotonic is None else monotonic
    cancel_requested = (lambda: False) if cancel_requested is None else cancel_requested
    start = monotonic()  # Includes asset/identity/import preparation in the same deadline domain.
    provenance_reader = None
    frozen_evidence = None
    try:
        parse_argv([FLAG, selector])
        inputs, manifest = load_assets()
        identity = check_runtime_preconditions()
        if sys.getprofile() is not None:
            raise ProbeFault("PROFILE_HOOK_ALREADY_PRESENT")
        if identity["frozen"]:
            provenance_reader = importlib.import_module(
                "ontolearn_engine.semantic_build_provenance"
            )
            frozen_evidence = provenance_reader.load_frozen_provenance(
                expectations=_frozen_expectations()
            )
        _install_audit_observer()
        modules, validator = _runtime_modules(identity)
        if identity["frozen"]:
            importlib.import_module("wcwidth._wcwidth_c")
            provenance_reader.verify_loaded_modules(frozen_evidence, modules)
            provenance_reader.verify_native_extension(frozen_evidence)
        approved = _approved_types(modules)
    except Exception as error:
        known_fault = type(error) is ProbeFault or (
            provenance_reader is not None
            and type(error) is getattr(provenance_reader, "BuildProvenanceFault", None)
        )
        _safe_stderr(stderr, error.code if known_fault else "PREFLIGHT_FAILED")
        return 2
    instrumentation = selector == "full-v1"
    inventory = manifest["caseSets"][selector]
    lookup = {item["id"]: item for item in inputs["observations"]}
    context = {item["id"]: item for item in inputs["contexts"]["mathInputContexts"]}
    completed, first_failure = [], None
    current_observation_id = None
    code, state = 0, "collecting"
    try:
        writer = JSONLWriter(stdout)
    except ProbeFault as error:
        _safe_stderr(stderr, error.code)
        return 1
    try:
        writer.emit(
            {
                "type": "header",
                "format": "i05-source-package-observations/1",
                "runId": str(time.time_ns()),
                "mode": "frozen" if identity["frozen"] else "source",
                "supplierRef": SOURCE_REF,
                "supplierProcessRef": PROCESS_REF,
                "identity": identity,
                "selectedCaseSet": selector,
                "instrumentation": instrumentation,
                "fullInventory": manifest["caseSets"]["full-v1"],
                "selectedInventory": inventory,
                "manifestSha256": MANIFEST_SHA256,
                "inputAsset": manifest["inputAsset"],
                "counts": manifest["counts"],
                "contexts": inputs["contexts"],
                "fullInventorySha256": hashlib.sha256(
                    canonical_bytes(manifest["caseSets"]["full-v1"])
                ).hexdigest(),
                "selectedInventorySha256": hashlib.sha256(canonical_bytes(inventory)).hexdigest(),
                "limits": {
                    "reportBytes": REPORT_CAP,
                    "itemBytes": ITEM_CAP,
                    "terminalReserveBytes": TERMINAL_RESERVE,
                    "caseCount": CASE_CAP,
                    "cooperativeBoundaryDeadlineSeconds": DEADLINE_SECONDS,
                    "deadlineIncludesPreflight": True,
                },
                "externalOracleCompared": False,
                "sourcePackageEquivalent": False,
                "externalOracleMatched": False,
                "originalOperationPassed": False,
            }
        )
        for case_id in inventory:
            if cancel_requested():
                code, state = 130, "stopping"
                break
            if monotonic() - start >= DEADLINE_SECONDS:
                code, state = 1, "deadline-boundary"
                first_failure = first_failure or {"code": "COLLECTION_DEADLINE"}
                break
            original = lookup[case_id]
            current_observation_id = case_id
            observation = {"type": "observation", **original, "start": monotonic()}
            source_context = context.get(original["sourceCaseId"])
            if (
                original["operation"] == "profile"
                and source_context is not None
                and not source_context["eligibleStandaloneMathInput"]
            ):
                observation.update(
                    status="not-executed",
                    callCounts={"reason": 0, "validator": 0},
                    stage="input/not-executed",
                    api=None,
                    stageAttempts=[],
                    diagnostic={
                        "code": "ORIGINAL_INPUT_CONTEXT_NOT_STANDALONE",
                        "originalOperationPassed": False,
                    },
                )
            else:
                counter = (
                    CallCounter(modules["ontolearn_engine.semantic"], validator)
                    if instrumentation
                    else None
                )
                boundary = CollectionBoundary(monotonic, start, cancel_requested)
                token = _COLLECTION_CONTEXT.set(boundary)
                try:
                    with counter if counter is not None else nullcontext():
                        result = _dispatch(
                            original,
                            inputs["datasets"][original["datasetId"]],
                            manifest,
                            modules,
                            approved,
                            counter,
                            instrumentation,
                        )
                    observation.update(status="observed-return", result=result)
                    if (
                        original["operation"] == "offline"
                        and result["status"] == "observed-rejection"
                    ):
                        observation.update(
                            status="observed-rejection",
                            error=result["error"],
                            diagnostic=result["diagnostic"],
                        )
                except Exception as error:
                    failure = _known_failure(error, modules)
                    missing_keywords = (
                        original["operation"] == "shacl-text"
                        and type(error) is TypeError
                        and set(original["parameters"]) != {"dataPolicy", "rangePolicy"}
                    )
                    if type(error) is BoundaryStop:
                        observation.update(
                            status="unexpected-failure",
                            error={"code": error.code},
                            diagnostic={"classification": "cooperative-boundary-stop"},
                        )
                        code, state = error.exit_code, error.state
                        first_failure = first_failure or {
                            "id": case_id,
                            "code": error.code,
                            "stage": boundary.stage,
                            "api": boundary.api,
                        }
                    elif missing_keywords:
                        observation.update(
                            status="observed-rejection",
                            error={"kind": "call-contract", "code": "CALL_ARGUMENTS_INVALID"},
                            diagnostic={"classification": "mandatory-keyword-missing"},
                        )
                    elif failure is not None:
                        observation.update(
                            status="observed-rejection", error=failure[0], diagnostic=failure[1]
                        )
                    else:
                        safe_code = error.code if type(error) is ProbeFault else "INTERNAL_ERROR"
                        observation.update(
                            status="unexpected-failure",
                            error={"code": safe_code},
                            diagnostic={
                                "classification": "harness-or-unknown",
                                "exceptionClass": type(error).__name__,
                            },
                        )
                        code, state = 1, "failed"
                        first_failure = first_failure or {
                            "id": case_id,
                            "code": safe_code,
                            "stage": boundary.stage,
                            "api": boundary.api,
                        }
                    observation["diagnostic"].update(stage=boundary.stage, api=boundary.api)
                    observation["partialOutputs"] = _partial_outputs(boundary, modules, approved)
                finally:
                    _COLLECTION_CONTEXT.reset(token)
                    observation["stage"], observation["api"] = boundary.stage, boundary.api
                    observation["stageAttempts"] = boundary.attempts
                    observation["callCounts"] = (
                        dict(counter.counts)
                        if counter is not None
                        and getattr(counter, "counts_complete", False) is True
                        else None
                    )
                    if counter is not None and hasattr(counter, "scope_details"):
                        observation["scopeStages"] = counter.scope_details
            observation["end"] = monotonic()
            writer.emit(observation)
            completed.append(case_id)
            if code:
                break
        requested = cancel_requested()
        if code == 0 and (requested or monotonic() - start >= DEADLINE_SECONDS):
            if requested:
                code, state = 130, "stopping"
            else:
                code, state = 1, "deadline-boundary"
                first_failure = first_failure or {"code": "COLLECTION_DEADLINE"}
        complete = code == 0 and len(completed) == len(inventory)
        state = "collected" if complete else state
        writer.emit(
            {
                "type": "terminal",
                "state": state,
                "selectedCaseSet": selector,
                "collectionComplete": complete,
                "fullSuiteCollectionComplete": complete and selector == "full-v1",
                "completedIds": completed,
                "unstartedIds": inventory[len(completed) :],
                "fullInventory": manifest["caseSets"]["full-v1"],
                "selectedInventory": inventory,
                "firstFailure": first_failure,
                "elapsedSeconds": monotonic() - start,
                "externalOracleCompared": False,
                "sourcePackageEquivalent": False,
                "externalOracleMatched": False,
                "originalOperationPassed": False,
                "externalProcessStopped": "unknown",
                "readerJoin": "unknown",
            },
            terminal=True,
        )
        return code
    except Exception as error:
        safe_code = error.code if type(error) is ProbeFault else "COLLECTION_FAILED"
        _safe_stderr(stderr, safe_code)
        first_failure = first_failure or {
            "code": safe_code,
            "id": current_observation_id,
            "stage": "observation/JSONL-write",
            "api": "JSONLWriter.emit",
        }
        if not writer.broken and not writer.terminal_written:
            try:
                writer.emit(
                    {
                        "type": "terminal",
                        "state": "failed",
                        "selectedCaseSet": selector,
                        "collectionComplete": False,
                        "fullSuiteCollectionComplete": False,
                        "completedIds": completed,
                        "unstartedIds": inventory[len(completed) :],
                        "firstFailure": first_failure or {"code": safe_code},
                        "externalOracleCompared": False,
                        "originalOperationPassed": False,
                        "sourcePackageEquivalent": False,
                        "externalOracleMatched": False,
                    },
                    terminal=True,
                )
            except Exception:
                pass  # No terminal means incomplete; never append after a partial physical line.
        return 1


def main(argv=None):
    try:
        selector = parse_argv(sys.argv[1:] if argv is None else argv)
    except ProbeFault as error:
        _safe_stderr(getattr(sys.stderr, "buffer", sys.stderr), error.code)
        return 2
    requested = [False]

    def request_stop(_number, _frame):
        requested[0] = True

    previous = {}
    try:
        for number in (signal.SIGINT, signal.SIGTERM):
            previous[number] = signal.getsignal(number)
            signal.signal(number, request_stop)
        return run_fixed_suite(selector, cancel_requested=lambda: requested[0])
    finally:
        for number, handler in previous.items():
            signal.signal(number, handler)
