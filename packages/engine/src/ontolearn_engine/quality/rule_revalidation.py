"""Bounded supplied-batch consistency; no graph/producer/restore capability.

The caller must supply the original child's allocation and complete ordered
inputs. Numeric shape checks here cannot authenticate that provenance or bound
an outer allocator, restoration, retention, retries or cross-child lifetime.
"""

from dataclasses import fields
from typing import Literal

from .rule_firing import (
    BindingMatch,
    Catalog,
    ComparisonEvidence,
    PreparedFiring,
    PreparedFiringBatch,
    RuleSpec,
    compile_rules,
    evaluate_bound_batch,
)
from .rule_profile import (
    PROFILE,
    Budget,
    ProfileFailure,
    ProfileLimits,
    encode_output,
    fail,
    internal,
)
from .rule_terms import check_value

REVALIDATION_BUDGET_VERSION = "mechanism-revalidation-budget/2"
_LIMIT_FIELDS = tuple((f.name, f.default) for f in fields(ProfileLimits))
_COMPARISONS = 32
_DIGEST = 64
_PROFILE_LENGTH = len(PROFILE)


class _Control:
    """One entry unit, then a fixed child cap; no per-group reset or borrowing."""

    __slots__ = ("limit", "used")

    def __init__(self):
        self.limit, self.used = 1, 0

    def bind(self, limits):
        if self.limit != 1 or self.used != 1:
            internal()
        self.limit = (
            1
            + limits.firings
            + limits.firings * _COMPARISONS
            + 4 * limits.output_bytes
            + 2 * _DIGEST
            + 2 * _PROFILE_LENGTH
            + 4
        )

    def debit(self, amount=1):
        if type(amount) is not int or amount < 0:
            internal()
        total = self.used + amount
        if total > self.limit:
            fail("WORK_LIMIT", classification="resource")
        self.used = total

    def same(self, left, right):
        self.debit(len(left) + len(right) + 1)
        if left != right:
            internal()


class _Resources:
    """Private per-call pools, separated so success has three source bounds."""

    __slots__ = ("replay", "saved_encoding", "saved_issuance", "control")

    def __init__(self, limits, control):
        self.replay = Budget(limits)
        self.saved_encoding = Budget(limits)
        self.saved_issuance = Budget(limits)
        self.control = control


def _copy_limits(limits):
    if type(limits) is not ProfileLimits:
        internal()
    values = {}
    # Fixed class-owned field table, never input reflection or a caller mapping.
    for name, maximum in _LIMIT_FIELDS:
        value = getattr(limits, name)
        if type(value) is not int or not 0 <= value <= maximum:
            fail("RULE_INPUT_BUDGET", classification="resource")
        values[name] = value
    return ProfileLimits(**values)


def _tuple_bound(value, cap, reason="RULE_INPUT_BUDGET"):
    if type(value) is not tuple:
        internal()
    if len(value) > cap:
        fail(reason, classification="resource")


def check_firing_batch(
    definitions: tuple[RuleSpec, ...],
    catalog: Catalog,
    original_matches: tuple[BindingMatch, ...],
    saved: PreparedFiringBatch | None,
    *,
    limits: ProfileLimits,
    disabled: bool,
) -> Literal["batch-consistent", "definition-only"]:
    """Check one trusted child allocation; return a finite fact or safe failure.

    Replays all supplied false/true matches once. A consistent result does not
    prove these are the producer's original inputs, graph membership, complete
    matching, authorization or successful restoration from persistent bytes.
    """
    try:
        return _check_firing_batch(definitions, catalog, original_matches, saved, limits, disabled)
    except ProfileFailure as exc:
        if exc.classification == "resource":
            raise
        internal()
    except Exception:
        internal()


def _check_firing_batch(definitions, catalog, original_matches, saved, limits, disabled):
    control = _Control()
    control.debit()  # Prepay the fixed entry guards, finite limit copy and pool setup.
    copied = _copy_limits(limits)
    control.bind(copied)
    if type(disabled) is not bool or type(catalog) is not Catalog:
        internal()
    _tuple_bound(definitions, copied.rules)
    _tuple_bound(original_matches, copied.bindings)
    definition_only = saved is None
    if disabled:
        if original_matches or not definition_only:
            internal()
    elif definition_only and (definitions or original_matches):
        internal()
    if not definition_only:
        if type(saved) is not PreparedFiringBatch:
            internal()
        _tuple_bound(saved.firings, copied.firings, "RULE_EVIDENCE_RESULT_LIMIT")
        _tuple_bound(saved.facts, copied.head_occurrences, "RULE_EVIDENCE_RESULT_LIMIT")
        if (
            type(saved.payload) is not bytes
            or type(saved.digest) is not str
            or type(saved.profile) is not str
        ):
            internal()
        if len(saved.payload) > copied.output_bytes:
            fail("RULE_EVIDENCE_RESULT_LIMIT", classification="resource")
        if len(saved.digest) != _DIGEST or len(saved.profile) != _PROFILE_LENGTH:
            internal()
        control.same(saved.profile, PROFILE)
    pools = _Resources(copied, control)
    plan = compile_rules(definitions, catalog, pools.replay)
    if definition_only:
        return "definition-only"
    fresh = evaluate_bound_batch(plan, original_matches, pools.replay)
    canonical_saved = encode_output((PROFILE, saved.firings, saved.facts), pools.saved_encoding)
    control.same(fresh.payload, canonical_saved)
    control.same(canonical_saved, saved.payload)
    control.same(fresh.digest, saved.digest)
    # The sole explicit group/comparison shape traversal, after full equality.
    # Every operand occurrence is still checked, even when aliases are shared.
    for group in saved.firings:
        control.debit()
        if type(group) is not PreparedFiring:
            internal()
        _tuple_bound(group.comparisons, copied.comparisons, "RULE_EVIDENCE_RESULT_LIMIT")
        for comparison in group.comparisons:
            control.debit()
            if type(comparison) is not ComparisonEvidence:
                internal()
            check_value(comparison.left, pools.saved_issuance)
            check_value(comparison.right, pools.saved_issuance)
    return "batch-consistent"
