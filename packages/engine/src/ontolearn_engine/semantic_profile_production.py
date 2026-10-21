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


class _ProductionCapture:
    """Exact private observer. No arbitrary callback or supplied allocation."""

    def __init__(self, material, ledger):
        _require(type(material) is ProfileMaterial and type(ledger) is CaptureLedger)
        self.material, self.ledger = material, ledger
        self.actual_definitions = self.actual_catalog = self.raw_rules = None
        self.disabled = None
        self.slots = []
        self.native = self.encoded = self.rows_encoded = None
        self.source_encoded = self.definitions_encoded = None
        self.wire = None
        ledger.reserve("objects", 4)

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

    def before_projection(self):
        self.ledger.enter(6, 3 * MAX_BYTES)
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
        self.ledger.debit("hash", 4 * MAX_BYTES)
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
        self.material = self.actual_definitions = self.actual_catalog = self.raw_rules = None
        self.disabled = self.native = self.encoded = self.rows_encoded = None
        self.source_encoded = self.definitions_encoded = self.wire = None
        self.slots = None


def _same_bytes(actual, expected, ledger):
    _require(type(actual) is bytes and type(expected) is bytes)
    ledger.debit("scan_copy", len(actual) + len(expected) + 1)
    if actual != expected:
        raise MaterialFailure("MATERIAL_MISMATCH", stage=ledger.stage)


def execute_admitted_profile_job(material, *, error_catalog, error_schema, ledger=None):
    """Actual component execution; its name grants no Store or Job authority."""
    from . import semantic_execution

    ledger = CaptureLedger() if ledger is None else ledger
    _require(type(ledger) is CaptureLedger)
    capture = checked = catalog_json = allocation = receipt = outcome = error = None
    encoded_source = value = actual = supplied = reference = revision = None
    try:
        _require(type(material) is ProfileMaterial)
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
        capture = _ProductionCapture(checked, ledger)
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
        catalog_json = _profile_json_bytes(_ProfileProjection().value(capture.actual_catalog))
        _hash(catalog_json, ledger)
        receipt = ledger.receipt()
        outcome = ProfileComputation(
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
        )
        ledger.transferred()
    except MaterialFailure as exc:
        error = MaterialFailure(exc.reason, domain=exc.domain, stage=exc.stage)
    except semantic_execution.ProfileExecutionFault as exc:
        error = semantic_execution.ProfileExecutionFault(exc.error, exc.diagnostic)
    except Exception:
        error = MaterialFailure("MATERIAL_INTERNAL")
    finally:
        if capture is not None:
            capture.drop()
        capture = checked = catalog_json = allocation = receipt = None
        encoded_source = value = actual = supplied = reference = revision = None
        if error is not None:
            outcome = None
            ledger.failed()
    if error is not None:
        raise error
    return outcome
