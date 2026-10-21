"""One real profile computation with independent occurrence-point capture.

The immutable result is data, not a Job, signed origin, worker admission or
permission. Only the future real T01 owner may bind it to its successful Job.
"""

from dataclasses import dataclass

from .quality.rule_firing import Catalog
from .quality.rule_profile import ProfileLimits, SourceRecord
from .semantic_profile_input import (
    MATERIAL_VERSION,
    MAX_BYTES,
    CaptureLedger,
    CaptureReceipt,
    MaterialFailure,
    ProfileMaterial,
    _encode,
    _hash,
    _prepare_profile_material,
    _require,
)
from .semantic_profile_restore import ChildAllocation, OriginalAllocation


@dataclass(frozen=True, slots=True)
class CapturedSlot:
    rule_id: str | None
    definition_ordinal: int | None
    limits: ProfileLimits


@dataclass(frozen=True, slots=True)
class ProfileComputation:
    material: ProfileMaterial
    native_result: dict
    original_allocation: OriginalAllocation
    actual_definitions: tuple
    actual_catalog: Catalog
    payload_json: bytes
    rows_json: bytes
    source_encoded: bytes
    definitions_encoded: bytes
    catalog_json: bytes
    wire: dict
    capture_receipt: CaptureReceipt
    version: str = "i05-profile-computation/1"
    retention_owner: str = "receiving caller; native, wire and bytes remain live"


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileExplanationComputation(ProfileComputation):
    direct_receipt: object
    version: str = "i05-profile-explanation-computation/1"


def _direct_bound(value, ledger, depth=0):
    """Count a canonical upper bound, without constructing a projection tree.

    Only the original projector's exact approved classes are traversed. Each
    dispatch, UTF8 scan and frame is prepaid in D before touching descendants.
    The result counts all JSON escapes, record tags and integer/byte wrappers.
    """
    from .quality.rule_profile import InputLocation
    from .semantic_profile_directsteps import DirectStepsFailure
    from .semantic_profile_restore import _EQUAL_FIELDS

    ledger.debit("work", 64)
    ledger.reserve("objects", 32)
    try:
        if depth > 32:
            raise DirectStepsFailure("DIRECT_STEPS_LIMIT", stage=ledger.stage, domain="work")
        kind = type(value)
        if value is None or kind is bool:
            return 5
        if kind is str:
            ledger.debit("scan_copy", 4 * len(value) + 1)
            return 6 * len(value) + 2
        if kind is int:
            return max(24, value.bit_length() // 4 + 32)
        if kind is bytes:
            ledger.debit("scan_copy", len(value) + 1)
            return 2 * len(value) + 48
        if kind in (tuple, list):
            ledger.debit("work", len(value) + 1)
            return 2 * len(value) + 2 + sum(_direct_bound(v, ledger, depth + 1) for v in value)
        if kind is dict:
            ledger.debit("work", 4 * len(value) + 1)
            total = 4 * len(value) + 2
            for key, item in value.items():
                if type(key) is not str:
                    raise DirectStepsFailure("DIRECT_STEPS_INTERNAL", stage=ledger.stage)
                total += _direct_bound(key, ledger, depth + 1)
                total += _direct_bound(item, ledger, depth + 1)
            return total
        approved = _EQUAL_FIELDS + ((InputLocation, ("section", "index", "side", "span")),)
        for cls, names in approved:
            if kind is cls:
                total = 64 + 6 * len(cls.__name__)
                for name in names:
                    total += 6 * len(name) + 8
                    total += _direct_bound(getattr(value, name), ledger, depth + 1)
                return total
        raise DirectStepsFailure("DIRECT_STEPS_INTERNAL", stage=ledger.stage)
    finally:
        value = None
        ledger.discard(objects=32)


def _direct_stream(ledger, bound, *, passes):
    # Per pass: UTF8 decoding <=4J scalars, JSON escaped buffer <=J,
    # projected dict/list slots <=8J, plus serializer sort/row slices <=3J.
    # The entire block stays held through transfer, including temporary slack.
    ledger.debit("work", 32 * passes * bound)
    ledger.debit("scan_copy", 16 * passes * bound)
    ledger.reserve("objects", 8 * passes * bound + 128)
    ledger.reserve("scalar", 8 * passes * bound + 1024)


class _ProductionCapture:
    """Exact private observer. No arbitrary callback or supplied allocation."""

    def __init__(self, material, ledger, direct_ledger=None):
        _require(type(material) is ProfileMaterial and type(ledger) is CaptureLedger)
        self.material, self.ledger = material, ledger
        self.direct_ledger = direct_ledger
        self.direct_capture = None
        if direct_ledger is not None:
            from .semantic_profile_directsteps import _DirectStepsCapture

            self.direct_capture = _DirectStepsCapture(direct_ledger)
        self.actual_definitions = self.actual_catalog = self.raw_rules = None
        self.disabled = None
        ledger.reserve("objects", 4)
        self.slots = []
        self.native = self.encoded = self.rows_encoded = None
        self.source_encoded = self.definitions_encoded = None
        self.wire = None

    def definitions(self, ordered_specs, rules):
        _require(self.actual_definitions is None and type(ordered_specs) is tuple)
        self.ledger.debit("traversal", 4 * len(ordered_specs) + 1)
        self.ledger.reserve("objects", 2 * len(ordered_specs) + 2)
        self.actual_definitions = ordered_specs
        self.raw_rules = rules

    def context(self, disabled):
        _require(self.disabled is None and type(disabled) is tuple)
        self.ledger.debit("traversal", len(disabled) + 1)
        self.ledger.reserve("objects", len(disabled) + 1)
        self.disabled = disabled

    def catalog(self, value):
        _require(self.actual_catalog is None and type(value) is Catalog)
        self.ledger.debit("traversal", 4)
        self.ledger.reserve("objects", 1)
        self.actual_catalog = value

    def allocation(self, spec, ordinal, limits):
        _require(type(limits) is ProfileLimits and len(self.slots) < 100)
        self.ledger.debit("traversal", 40)
        self.ledger.reserve("objects", 24)
        self.ledger.reserve("scalar", 1024)
        self.slots.append(CapturedSlot(None if spec is None else spec.rule_id, ordinal, limits))

    def before_input(self, original_bytes, source, input_domain):
        _require(input_domain == self.material.input_domain)
        _same_bytes(original_bytes, self.material.input_preimage, self.ledger)
        # The source preimage was fixed before this parser/reason call. Source
        # is checked after the original same-projection source gate as well.
        _require(type(source) is type(self.material.source))

    def before_projection(self, native=None, source=None, rules=None):
        if self.direct_ledger is not None:
            self.direct_ledger.enter("encode")
            bound = _direct_bound(native, self.direct_ledger)
            bound += _direct_bound(source, self.direct_ledger)
            bound += _direct_bound(rules, self.direct_ledger) + 2048
            _direct_stream(self.direct_ledger, bound, passes=3)
        self.ledger.enter(6, 3 * MAX_BYTES)
        # Prepay all five original digests before the first (input/source/defs)
        # in the projection stage. Q<=2M, defs<=M, payload+rows<=M.
        self.ledger.debit("hash", 4 * MAX_BYTES)
        # Ordinary temporary projected trees and all concurrent encoder buffers
        # are prepaid before invoking the unchanged bounded serializer. Its own
        # depth/node/output gates still run in the same original order.
        self.ledger.debit("traversal", 16 * MAX_BYTES)
        self.ledger.debit("scan_copy", 32 * MAX_BYTES)
        self.ledger.reserve("scalar", 24 * MAX_BYTES)
        self.ledger.reserve("objects", 8 * MAX_BYTES)

    def before_rows(self):
        self.ledger.enter(7, 3 * MAX_BYTES)
        self.ledger.debit("traversal", 16 * MAX_BYTES)
        self.ledger.debit("scan_copy", 24 * MAX_BYTES)
        self.ledger.reserve("scalar", 8 * MAX_BYTES)
        self.ledger.reserve("objects", 2 * MAX_BYTES)

    def completed(self, native, encoded, rows_encoded, source_encoded, definitions_encoded, wire):
        _require(self.native is None and self.actual_definitions is not None)
        _require(self.actual_catalog is not None and self.disabled is not None)
        _require(len(self.slots) == max(1, len(self.raw_rules)))
        _same_bytes(source_encoded, self.material.source_preimage, self.ledger)
        _same_bytes(definitions_encoded, self.material.definitions_preimage, self.ledger)
        self.native, self.encoded, self.rows_encoded = native, encoded, rows_encoded
        self.source_encoded, self.definitions_encoded, self.wire = (
            source_encoded,
            definitions_encoded,
            wire,
        )

    def drop(self):
        if self.direct_capture is not None:
            self.direct_capture.drop()
        self.direct_capture = None
        self.material = self.actual_definitions = self.actual_catalog = self.raw_rules = None
        self.disabled = self.native = self.encoded = self.rows_encoded = None
        self.source_encoded = self.definitions_encoded = self.wire = None
        self.slots = None


def _same_bytes(actual, expected, ledger):
    _require(type(actual) is bytes and type(expected) is bytes)
    ledger.debit("scan_copy", len(actual) + len(expected) + 1)
    if actual != expected:
        raise MaterialFailure("MATERIAL_MISMATCH", stage=ledger.stage)


def _execute_admitted_profile_job(
    material, *, error_catalog, error_schema, ledger=None, direct_ledger=None
):
    """Actual component execution; its name grants no Store or Job authority."""
    from . import semantic_execution
    from .semantic_profile_directsteps import DirectStepsFailure, DirectStepsLedger

    if direct_ledger is not None:
        if type(direct_ledger) is not DirectStepsLedger:
            raise DirectStepsFailure()
        if direct_ledger.state != "new":
            raise DirectStepsFailure("DIRECT_STEPS_REUSED", stage=direct_ledger.stage)
    ledger = CaptureLedger() if ledger is None else ledger
    _require(type(ledger) is CaptureLedger)
    capture = checked = catalog_json = allocation = receipt = outcome = error = None
    encoded_source = value = actual = supplied = reference = revision = None
    direct_receipt = None
    try:
        if direct_ledger is not None:
            direct_ledger.begin(stage="capture")
        _require(type(material) is ProfileMaterial)
        if direct_ledger is not None:
            _require(type(material.records) is tuple)
            bound = _direct_bound(material.records, direct_ledger)
            bound += _direct_bound(material.source, direct_ledger)
            bound += _direct_bound(material.rules, direct_ledger)
            bound += len(material.input_preimage) + len(material.definition_material) + 2048
            _direct_stream(direct_ledger, bound, passes=2)
        _require(type(material.version) is str and material.version == MATERIAL_VERSION)
        for value in (
            material.input_preimage,
            material.source_preimage,
            material.definitions_preimage,
            material.definition_material,
        ):
            _require(type(value) is bytes and len(value) <= MAX_BYTES)
        _require(type(material.rules) is tuple and len(material.rules) <= 100)
        if material.records is None:
            _require(type(material.source) is SourceRecord)
            reference, revision = material.source.reference, material.source.revision
        else:
            reference = revision = None
        checked = _prepare_profile_material(
            material.text,
            material.rules,
            records=material.records,
            disabled_rule_ids=material.disabled_rule_ids,
            source_reference=reference,
            source_revision=revision,
            parser_identity=material.parser_identity,
            ledger=ledger,
            finish=False,
            budget_inputs=(
                len(material.input_preimage) + len(material.source_preimage),
                len(material.definition_material),
            ),
        )
        ledger.enter(4, 3 * MAX_BYTES)
        _require(
            type(material.input_domain) is str and material.input_domain == checked.input_domain
        )
        for actual, supplied in (
            (checked.input_preimage, material.input_preimage),
            (checked.source_preimage, material.source_preimage),
            (checked.definitions_preimage, material.definitions_preimage),
            (checked.definition_material, material.definition_material),
        ):
            _same_bytes(actual, supplied, ledger)
        # Reject an independently changed native source field before computing.
        encoded_source = _encode(material.source, ledger)
        _same_bytes(encoded_source, checked.source_preimage, ledger)
        ledger.release("scalar", len(encoded_source))
        encoded_source = None
        ledger.enter(5, 3 * MAX_BYTES)
        capture = _ProductionCapture(checked, ledger, direct_ledger)
        semantic_execution._execute_profile_production(
            checked,
            capture,
            error_catalog=error_catalog,
            error_schema=error_schema,
        )
        _require(capture.native is not None)
        ledger.enter(8, 3 * MAX_BYTES)
        ledger.debit("traversal", 8 * len(capture.slots) + 4 * len(capture.raw_rules) + 8)
        ledger.reserve("objects", 6 * len(capture.slots) + 6 * len(capture.raw_rules) + 16)
        allocation = OriginalAllocation(
            tuple(spec.rule_id for spec in capture.raw_rules),
            capture.disabled,
            tuple(
                ChildAllocation(slot.rule_id, slot.definition_ordinal, slot.limits)
                for slot in capture.slots
            ),
        )
        # Catalog is actual normalized output, not recovered from saved JSON.
        from .semantic_execution import _profile_json_bytes, _ProfileProjection

        ledger.debit("traversal", 8 * MAX_BYTES)
        ledger.debit("scan_copy", 16 * MAX_BYTES)
        ledger.reserve("scalar", 8 * MAX_BYTES)
        ledger.reserve("objects", 2 * MAX_BYTES)
        if direct_ledger is not None:
            _direct_stream(
                direct_ledger, _direct_bound(capture.actual_catalog, direct_ledger), passes=1
            )
        catalog_json = _profile_json_bytes(_ProfileProjection().value(capture.actual_catalog))
        _hash(catalog_json, ledger)
        receipt = ledger.receipt()
        if direct_ledger is not None:
            # Drop private capture/index before receipt; carrier has its own tickets.
            capture.direct_capture.drop()
            capture.direct_capture = None
            direct_receipt = direct_ledger.receipt()
        cls = ProfileComputation if direct_ledger is None else ProfileExplanationComputation
        outcome = cls(
            checked,
            capture.native,
            allocation,
            capture.actual_definitions,
            capture.actual_catalog,
            capture.encoded,
            capture.rows_encoded,
            capture.source_encoded,
            capture.definitions_encoded,
            catalog_json,
            capture.wire,
            receipt,
            **({} if direct_ledger is None else {"direct_receipt": direct_receipt}),
        )
        ledger.transferred()
        if direct_ledger is not None:
            direct_ledger.transferred()
    except DirectStepsFailure as exc:
        error = DirectStepsFailure(exc.reason, stage=exc.stage, domain=exc.domain)
    except MaterialFailure as exc:
        error = MaterialFailure(exc.reason, domain=exc.domain, stage=exc.stage)
    except semantic_execution.ProfileExecutionFault as exc:
        error = semantic_execution.ProfileExecutionFault(exc.error, exc.diagnostic)
    except Exception:
        error = (
            MaterialFailure("MATERIAL_INTERNAL")
            if direct_ledger is None
            else DirectStepsFailure("DIRECT_STEPS_INTERNAL", stage=direct_ledger.stage)
        )
    finally:
        if capture is not None:
            capture.drop()
        capture = checked = catalog_json = allocation = receipt = direct_receipt = None
        encoded_source = value = actual = supplied = reference = revision = None
        if error is not None:
            outcome = None
            ledger.failed()
            if direct_ledger is not None:
                direct_ledger.failed()
    if error is not None:
        raise error
    return outcome


def execute_admitted_profile_job(material, *, error_catalog, error_schema, ledger=None):
    return _execute_admitted_profile_job(
        material, error_catalog=error_catalog, error_schema=error_schema, ledger=ledger
    )


def execute_profile_explanation(material, *, error_catalog, error_schema, ledger, direct_ledger):
    """Explicit internal explanation computation; no Job or source authority."""
    from .semantic_profile_directsteps import DirectStepsFailure, DirectStepsLedger

    if type(direct_ledger) is not DirectStepsLedger:
        raise DirectStepsFailure()
    return _execute_admitted_profile_job(
        material,
        error_catalog=error_catalog,
        error_schema=error_schema,
        ledger=ledger,
        direct_ledger=direct_ledger,
    )
