"""Given-binding mechanism only: no graph matcher, producer auth or publication."""

import re
from dataclasses import dataclass, field
from functools import cmp_to_key
from weakref import ref

from .rule_comparator import compare_values
from .rule_profile import (
    OPS,
    PROFILE,
    RDF,
    Budget,
    InputLocation,
    ProfileFailure,
    SourceRecord,
    TermInput,
    account_input,
    encode_input,
    encode_output,
    fail,
    fingerprint,
    internal,
    text_compare,
    tuple_compare,
    utf8_size,
)
from .rule_terms import ProfileValue, iri_minimum, parse_value, term_key

VAR = re.compile(r"\?[A-Za-z][A-Za-z0-9_]{0,63}", re.ASCII)
_SEAL = object()
_ISSUED_PLANS = {}
SCHEMA_NAMESPACES = (
    RDF,
    "http://www.w3.org/2000/01/rdf-schema#",
    "http://www.w3.org/2002/07/owl#",
    "http://www.w3.org/ns/shacl#",
)


@dataclass(frozen=True, slots=True)
class Variable:
    name: str


@dataclass(frozen=True, slots=True)
class Triple:
    subject: TermInput | Variable
    predicate: TermInput
    object: TermInput | Variable


@dataclass(frozen=True, slots=True)
class Comparison:
    left: TermInput | Variable
    operator: str
    right: TermInput | Variable


@dataclass(frozen=True, slots=True)
class RuleSpec:
    rule_id: str
    when: tuple[Triple, ...]
    comparisons: tuple[Comparison, ...]
    heads: tuple[Triple, ...]
    source: SourceRecord | None = None
    revision: str | None = None
    definition_digest: str | None = None
    policy: str = PROFILE


@dataclass(frozen=True, slots=True)
class Catalog:
    classes: tuple[str, ...] = ()
    object_properties: tuple[str, ...] = ()
    data_properties: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class BindingMatch:
    rule_id: str
    bindings: tuple[tuple[str, TermInput], ...]
    when: tuple[Triple, ...]
    proof_leaves: tuple[tuple[str, ...], ...]


@dataclass(frozen=True, slots=True)
class _CompiledRule:
    spec: RuleSpec
    constants: tuple[tuple[TermInput, ProfileValue], ...]
    variables: tuple[str, ...]
    prepared_digest: str


@dataclass(frozen=True, slots=True, init=False, weakref_slot=True)
class CompiledPlan:
    rules: tuple[_CompiledRule, ...]
    catalog: Catalog
    digest: str
    _budget: Budget = field(repr=False, compare=False)
    _seal: object = field(repr=False, compare=False)

    def __init__(self, rules, catalog, digest, budget, seal=None):
        if seal is not _SEAL:
            internal()
        for name, value in (
            ("rules", rules),
            ("catalog", catalog),
            ("digest", digest),
            ("_budget", budget),
            ("_seal", seal),
        ):
            object.__setattr__(self, name, value)


@dataclass(frozen=True, slots=True)
class ComparisonEvidence:
    index: int
    left: ProfileValue
    operator: str
    right: ProfileValue
    result: bool


@dataclass(frozen=True, slots=True)
class HeadEvidence:
    index: int
    triple: Triple


@dataclass(frozen=True, slots=True)
class PreparedFiring:
    rule_id: str
    bindings: tuple[tuple[str, TermInput], ...]
    when: tuple[Triple, ...]
    proof_leaves: tuple[tuple[str, ...], ...]
    comparisons: tuple[ComparisonEvidence, ...]
    heads: tuple[HeadEvidence, ...]
    basis: tuple[str, ...]
    source: SourceRecord | None
    revision: str | None
    definition_digest: str | None
    policy: str = PROFILE


@dataclass(frozen=True, slots=True)
class PreparedFiringBatch:
    firings: tuple[PreparedFiring, ...]
    facts: tuple[Triple, ...]
    payload: bytes
    digest: str
    profile: str = PROFILE


def _sequence(value, limit, budget, location=None, nonempty=False):
    if type(value) is not tuple:
        fail(location=location)
    budget.bound(len(value), limit, location)
    if nonempty and not value:
        fail(location=location)


def _contains(text, values, budget):
    return any(text_compare(text, v, budget) == 0 for v in values)


def _sort_unique(values, budget):
    ordered = sorted(values, key=cmp_to_key(lambda a, b: text_compare(a, b, budget)))
    result = []
    for s in ordered:
        if not result or text_compare(result[-1], s, budget):
            result.append(s)
    return tuple(result)


def _variable(value, budget, location):
    if type(value) is Variable:
        utf8_size(value.name, budget, budget.limits.term_bytes, location)
        budget.debit(len(value.name), location=location)
        if not VAR.fullmatch(value.name):
            fail(location=location)
        return value.name
    return None


def _check_triple(t, catalog, budget, location, allow_variables=True, output=False):
    if type(t) is not Triple:
        fail(location=location)
    if type(t.subject) is TermInput:
        subject = parse_value(t.subject, location, budget)
        if subject.domain != "I":
            fail(location=location)
        if output and _contains(
            subject.value,
            catalog.classes + catalog.object_properties + catalog.data_properties,
            budget,
        ):
            fail("UNSUPPORTED_RULE_OUTPUT", location)
    elif not allow_variables or not _variable(t.subject, budget, location):
        fail(location=location)
    predicate = parse_value(t.predicate, location, budget)
    if predicate.domain != "I":
        fail(location=location)
    path = predicate.value
    if output:
        budget.debit(len(path) + sum(map(len, SCHEMA_NAMESPACES)))
        if path != RDF + "type" and path.startswith(SCHEMA_NAMESPACES):
            fail("UNSUPPORTED_RULE_OUTPUT", location)
    if path == RDF + "type":
        obj = parse_value(t.object, location, budget)
        if obj.domain != "I" or not _contains(obj.value, catalog.classes, budget):
            fail(location=location)
        if output:
            budget.debit(len(obj.value) + sum(map(len, SCHEMA_NAMESPACES)))
            if obj.value.startswith(SCHEMA_NAMESPACES):
                fail("UNSUPPORTED_RULE_OUTPUT", location)
    else:
        is_object = _contains(path, catalog.object_properties, budget)
        is_data = _contains(path, catalog.data_properties, budget)
        if not is_object and not is_data:
            if output:
                fail("UNSUPPORTED_RULE_OUTPUT", location)
            fail(location=location)
        if type(t.object) is TermInput:
            obj = parse_value(t.object, location, budget)
            if (is_object and obj.domain != "I") or (is_data and obj.domain == "I"):
                fail(location=location)
        elif not allow_variables or not _variable(t.object, budget, location):
            fail(location=location)


def compile_rules(definitions, catalog, budget):
    if type(budget) is not Budget:
        internal()
    budget.start("compile")
    if type(definitions) not in (tuple, list) or type(catalog) is not Catalog:
        fail()
    budget.bound(len(definitions), "rules")
    account_input((tuple(definitions), catalog), budget)
    for group in (catalog.classes, catalog.object_properties, catalog.data_properties):
        if type(group) is not tuple:
            fail()
        budget.debit(len(group))
        for iri in group:
            iri_minimum(iri, budget)
        if len(_sort_unique(group, budget)) != len(group):
            fail()
    if any(_contains(p, catalog.data_properties, budget) for p in catalog.object_properties):
        fail()
    result, seen_ids = [], []
    for spec in definitions:
        budget.debit()
        if type(spec) is not RuleSpec:
            fail()
        if spec.source is not None:
            if type(spec.source) is not SourceRecord:
                fail()
            for text in (
                spec.source.reference,
                spec.source.digest,
                spec.source.revision,
                spec.source.text,
            ):
                if text is not None:
                    utf8_size(text, budget, budget.limits.source_bytes)
        for text in (spec.revision, spec.definition_digest):
            if text is not None:
                utf8_size(text, budget, budget.limits.term_bytes)
        utf8_size(spec.rule_id, budget, budget.limits.term_bytes)
        if not spec.rule_id or _contains(spec.rule_id, seen_ids, budget):
            fail()
        seen_ids.append(spec.rule_id)
        if spec.policy != PROFILE:
            fail("RULE_POLICY_UNSUPPORTED")
        _sequence(spec.when, "when", budget, nonempty=True)
        _sequence(spec.comparisons, "comparisons", budget)
        _sequence(spec.heads, "heads", budget, nonempty=True)
        constants, bound, used = [], [], []
        for section, items in (
            ("when", spec.when),
            ("comparison", spec.comparisons),
            ("head", spec.heads),
        ):
            for index, item in enumerate(items):
                loc = InputLocation(section, index)
                budget.debit()
                if section == "comparison":
                    if type(item) is not Comparison or item.operator not in OPS:
                        fail(location=loc)
                    operands = ((item.left, "left"), (item.right, "right"))
                else:
                    _check_triple(item, catalog, budget, loc, output=section == "head")
                    operands = ((item.subject, None), (item.predicate, None), (item.object, None))
                for operand, side in operands:
                    pos = InputLocation(section, index, side)
                    var = _variable(operand, budget, pos)
                    if var:
                        bound.append(var) if section == "when" else used.append((var, pos))
                    else:
                        constants.append((operand, parse_value(operand, pos, budget)))
        for index, comp in enumerate(spec.comparisons):
            if type(comp.left) is TermInput and type(comp.right) is TermInput:
                local = _CompiledRule(spec, tuple(constants), (), "")
                compare_values(
                    _resolve(comp.left, local, (), budget),
                    comp.operator,
                    _resolve(comp.right, local, (), budget),
                    budget,
                    InputLocation("comparison", index),
                )
        variables = _sort_unique(bound, budget)
        budget.bound(len(variables), "variables")
        for var, pos in used:
            if not _contains(var, variables, budget):
                fail("UNBOUND_RULE_VARIABLE", pos)
        result.append(
            _CompiledRule(
                spec, tuple(constants), variables, fingerprint(encode_input(spec, budget), budget)
            )
        )
    data = (tuple(result), catalog)
    digest = fingerprint(encode_input(data, budget), budget)
    plan = CompiledPlan(tuple(result), catalog, digest, budget, _SEAL)
    key = id(plan)

    def expire(reference):
        if _ISSUED_PLANS.get(key, (None,))[0] is reference:
            _ISSUED_PLANS.pop(key, None)

    _ISSUED_PLANS[key] = (ref(plan, expire), digest, budget)
    return plan


def _check_plan(plan, budget):
    if type(plan) is not CompiledPlan or type(budget) is not Budget:
        internal()
    issued = _ISSUED_PLANS.get(id(plan))
    if issued is None or issued[0]() is not plan or issued[2] is not budget:
        internal()
    if type(plan.digest) is not str or plan._seal is not _SEAL or plan._budget is not budget:
        internal()
    try:
        actual = fingerprint(encode_input((plan.rules, plan.catalog), budget), budget)
    except ProfileFailure as exc:
        if exc.classification == "resource":
            raise
        internal()
    if actual != issued[1] or plan.digest != issued[1]:
        internal()


def _resolve(operand, rule, bindings, budget):
    if type(operand) is Variable:
        for name, value in bindings:
            if not text_compare(name, operand.name, budget):
                return value
        internal()
    for term, value in rule.constants:
        budget.debit()
        if term is operand:
            return value
    internal()


def _triple_key(t, budget):
    return tuple(
        term_key(parse_value(v, None, budget), budget) for v in (t.subject, t.predicate, t.object)
    )


def _triple_equal(a, b, budget):
    return tuple_compare(_triple_key(a, budget), _triple_key(b, budget), budget) == 0


def _instantiate(t, rule, bindings, budget):
    return Triple(
        *(_resolve(v, rule, bindings, budget).term for v in (t.subject, t.predicate, t.object))
    )


def _one(rule, match, catalog, budget):
    spec = rule.spec
    if (
        type(match.bindings) is not tuple
        or type(match.when) is not tuple
        or type(match.proof_leaves) is not tuple
    ):
        internal()
    if (
        len(match.bindings) != len(rule.variables)
        or len(match.when) != len(spec.when)
        or len(match.proof_leaves) != len(spec.when)
    ):
        internal()
    pairs, names = [], []
    try:
        for pair in match.bindings:
            if type(pair) is not tuple or len(pair) != 2:
                internal()
            name, term = pair
            if (
                type(name) is not str
                or not _contains(name, rule.variables, budget)
                or _contains(name, names, budget)
            ):
                internal()
            names.append(name)
            pairs.append((name, parse_value(term, None, budget)))
        for index, t in enumerate(match.when):
            _check_triple(t, catalog, budget, InputLocation("when", index), False)
            if not _triple_equal(t, _instantiate(spec.when[index], rule, pairs, budget), budget):
                internal(InputLocation("when", index))
        for leaves in match.proof_leaves:
            if type(leaves) is not tuple:
                internal()
            for leaf in leaves:
                utf8_size(leaf, budget, budget.limits.term_bytes)
                if not leaf:
                    internal()
                budget.debit(1, "trace_items")
    except Exception as exc:
        if isinstance(exc, ProfileFailure) and exc.classification == "resource":
            raise
        internal()
    evidence = []
    for index, comp in enumerate(spec.comparisons):
        loc = InputLocation("comparison", index)
        left = _resolve(comp.left, rule, pairs, budget)
        right = _resolve(comp.right, rule, pairs, budget)
        outcome = compare_values(left, comp.operator, right, budget, loc)
        evidence.append(ComparisonEvidence(index, left, comp.operator, right, outcome))
    if not all(c.result for c in evidence):
        return None
    heads = []
    for index, head in enumerate(spec.heads):
        actual = _instantiate(head, rule, pairs, budget)
        _check_triple(actual, catalog, budget, InputLocation("head", index), False, True)
        budget.debit(1, "head_occurrences")
        heads.append(HeadEvidence(index, actual))
    basis = _sort_unique([leaf for leaves in match.proof_leaves for leaf in leaves], budget)
    budget.debit(1, "firings")
    budget.debit(
        1 + 2 * len(pairs) + 4 * len(match.when) + 3 * len(evidence) + 4 * len(heads) + len(basis),
        "trace_items",
    )
    ordered_pairs = sorted(pairs, key=cmp_to_key(lambda a, b: text_compare(a[0], b[0], budget)))
    return PreparedFiring(
        spec.rule_id,
        tuple((k, v.term) for k, v in ordered_pairs),
        match.when,
        match.proof_leaves,
        tuple(evidence),
        tuple(heads),
        basis,
        spec.source,
        spec.revision,
        spec.definition_digest or rule.prepared_digest,
    )


def evaluate_bound_batch(plan, matches, budget):
    try:
        return _evaluate_bound_batch(plan, matches, budget)
    except ProfileFailure:
        raise
    except Exception:
        internal()


def _evaluate_bound_batch(plan, matches, budget):
    _check_plan(plan, budget)
    budget.start("evaluate")
    if type(matches) not in (tuple, list):
        internal()
    budget.bound(len(matches), "bindings")
    try:
        account_input(matches, budget)
    except ProfileFailure as exc:
        if exc.classification == "resource":
            raise
        internal()
    output, seen, facts = [], [], []
    for match in matches:
        budget.debit()
        if type(match) is not BindingMatch or type(match.rule_id) is not str:
            internal()
        rule = next(
            (r for r in plan.rules if not text_compare(r.spec.rule_id, match.rule_id, budget)), None
        )
        if rule is None:
            internal()
        firing = _one(rule, match, plan.catalog, budget)
        # Every supplied match must be unique, including false matches.
        key = (
            match.rule_id,
            tuple(
                sorted(
                    (
                        (k, term_key(v, budget))
                        for k, v in ((k, parse_value(t, None, budget)) for k, t in match.bindings)
                    ),
                    key=cmp_to_key(lambda a, b: tuple_compare(a, b, budget)),
                )
            ),
            tuple(_triple_key(t, budget) for t in match.when),
        )
        if any(tuple_compare(key, other, budget) == 0 for other in seen):
            internal()
        seen.append(key)
        if firing is not None:
            output.append((key, firing))
    output.sort(key=cmp_to_key(lambda a, b: tuple_compare(a[0], b[0], budget)))
    for _, firing in output:
        for head in firing.heads:
            facts.append((_triple_key(head.triple, budget), head.triple))
    facts.sort(key=cmp_to_key(lambda a, b: tuple_compare(a[0], b[0], budget)))
    unique = []
    for key, triple in facts:
        if not unique or tuple_compare(key, unique[-1][0], budget):
            unique.append((key, triple))
    firings, triples = tuple(f for _, f in output), tuple(t for _, t in unique)
    payload = encode_output((PROFILE, firings, triples), budget)
    return PreparedFiringBatch(firings, triples, payload, fingerprint(payload, budget))


def check_firing_group(plan, group, budget):
    try:
        return _check_firing_group(plan, group, budget)
    except ProfileFailure as exc:
        if exc.classification == "resource":
            raise
        internal()
    except Exception:
        internal()


def _check_firing_group(plan, group, budget):
    """Pure consistency only. Does not prove graph membership or completeness."""
    _check_plan(plan, budget)
    if type(group) is not PreparedFiring:
        internal()
    try:
        account_input(group, budget)
    except ProfileFailure as exc:
        if exc.classification == "resource":
            raise
        internal()
    if type(group.rule_id) is not str:
        internal()
    rule = next(
        (r for r in plan.rules if not text_compare(r.spec.rule_id, group.rule_id, budget)), None
    )
    if rule is None:
        internal()
    expected = _one(
        rule,
        BindingMatch(group.rule_id, group.bindings, group.when, group.proof_leaves),
        plan.catalog,
        budget,
    )
    if expected is None or encode_output(expected, budget) != encode_output(group, budget):
        internal()
    return True
