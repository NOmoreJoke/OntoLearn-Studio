"""Single-snapshot IRI reuse must preserve the original validation boundary.

Successful values always use the installed Turtle parser. The transparent parser
counter observes work; it does not replace term(), Graph.parse(), or RDF results.
"""

import ontolearn_engine.storage as storage
import pytest
from ontolearn_engine import rdf_snapshot
from ontolearn_engine.storage import Store, canonical
from rdflib import Graph, URIRef
from rdflib.plugins.parsers.notation3 import TurtleParser
from rdflib.term import _toPythonMapping

IRI = "<urn:memo:object>"


@pytest.fixture
def real_parses(monkeypatch):
    calls = []
    original = TurtleParser.parse

    def counted(self, *args, **kwargs):
        calls.append(None)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(TurtleParser, "parse", counted)
    return calls


def fact(identity, obj=IRI):
    # Snapshot IDs remain stable across edits; this validator does not rederive them.
    return {
        "id": identity,
        "subject": "urn:memo:subject",
        "predicate": "urn:memo:predicate",
        "object": obj,
        "owner": None,
        "source_row": None,
        "managed_value": None,
    }


def definition_value(obj=IRI):
    return {
        "triples": [
            {
                "subject": "urn:memo:definition",
                "predicate": "urn:memo:predicate",
                "object": obj,
            }
        ],
        "references": [],
    }


def definition(identity, value=None):
    return {
        "layer": "ontology",
        "id": identity,
        "payload": canonical(definition_value() if value is None else value),
    }


def snapshot(*objects, definitions=()):
    return {
        "definitions": list(definitions),
        "facts": [fact(f"fact-{index}", obj) for index, obj in enumerate(objects)],
        "mappingState": {},
    }


def test_canonical_iri_reuse_is_shared_by_definition_and_fact_checks(real_parses):
    state = snapshot(IRI, IRI, definitions=[definition("D1"), definition("D2")])
    before = canonical(state)
    Store._snapshot_state(state)
    assert canonical(state) == before
    assert len(real_parses) == 1


def test_managed_value_and_tombstone_keep_their_original_ownership_checks(real_parses):
    state = snapshot(IRI, IRI)
    state["facts"][1].update(owner="M1", source_row="row-1", managed_value=IRI, object=None)
    Store._snapshot_state(state)
    assert len(real_parses) == 1
    state["facts"][1]["source_row"] = None
    with pytest.raises(ValueError, match="^Incomplete snapshot mapping ownership$"):
        Store._snapshot_state(state)


@pytest.mark.parametrize("location", ["definition", "fact"])
def test_lexical_alias_is_not_the_cached_canonical_string(location, real_parses):
    alias = " " + IRI
    if location == "definition":
        state = snapshot(definitions=[definition("D1"), definition("D2", definition_value(alias))])
        message = "Canonical RDF object required in definition"
    else:
        state = snapshot(IRI, alias)
        message = "Invalid snapshot RDF object"
    with pytest.raises(ValueError, match=f"^{message}$"):
        Store._snapshot_state(state)
    assert len(real_parses) == 2


def test_bare_iri_mode_is_not_a_term_memo_hit(real_parses):
    assert storage.iri("urn:memo:object") == URIRef("urn:memo:object")
    with pytest.raises(ValueError):
        Store._snapshot_state(snapshot(IRI, "urn:memo:object"))
    assert len(real_parses) == 2


@pytest.mark.parametrize(
    ("broken", "message"),
    [
        ("duplicate-id", "Incomplete snapshot fact record"),
        ("shape", "Incomplete snapshot fact record"),
        ("ownership", "Invalid snapshot manual ownership"),
        ("mapping-state", "Incomplete snapshot mapping state"),
    ],
)
def test_cached_iri_does_not_replace_record_validation(broken, message, real_parses):
    state = snapshot(IRI, IRI, IRI)
    if broken == "duplicate-id":
        state["facts"][2]["id"] = state["facts"][0]["id"]
    elif broken == "shape":
        del state["facts"][2]["owner"]
    elif broken == "ownership":
        state["facts"][2]["source_row"] = "not-manual"
    else:
        state["mappingState"] = {"M1": {}}
    with pytest.raises(ValueError, match=f"^{message}$"):
        Store._snapshot_state(state)
    assert len(real_parses) == 1


def test_definition_reference_failure_still_precedes_fact_parsing(real_parses):
    value = definition_value()
    value["references"] = [{"layer": "ontology", "id": "absent"}]
    state = snapshot('"unterminated', definitions=[definition("D1", value), definition("D2")])
    with pytest.raises(ValueError, match="^Incomplete snapshot definition reference$"):
        Store._snapshot_state(state)
    assert len(real_parses) == 1


def test_dict_subclass_access_is_not_replayed_by_eligibility(real_parses):
    accesses = []

    class SeenState(dict):
        def __getitem__(self, key):
            accesses.append(key)
            return super().__getitem__(key)

    Store._snapshot_state(SeenState(snapshot(IRI, IRI)))
    assert accesses == ["definitions", "facts", "mappingState"]
    assert len(real_parses) == 2


def test_record_subclass_side_effect_uses_the_current_term(monkeypatch, real_parses):
    accesses = []
    failure = RuntimeError("original subclass callback term failure")

    def refused(_value):
        raise failure

    class MutatingRecord(dict):
        def __getitem__(self, key):
            if key == "object":
                accesses.append(key)
                monkeypatch.setattr(storage, "term", refused)
            return super().__getitem__(key)

    state = snapshot(IRI, IRI)
    state["facts"][1] = MutatingRecord(state["facts"][1])
    with pytest.raises(RuntimeError) as caught:
        Store._snapshot_state(state)
    assert caught.value is failure
    assert accesses == ["object"]
    assert len(real_parses) == 1


def test_earlier_shape_error_does_not_invoke_subclass_object_callback(real_parses):
    accesses = []

    class BadRecord(dict):
        def __getitem__(self, key):
            if key == "object":
                accesses.append(key)
                raise AssertionError("object must not be read after the earlier shape failure")
            return super().__getitem__(key)

    bad = fact("bad")
    del bad["owner"]
    state = snapshot(IRI)
    state["facts"].append(BadRecord(bad))
    with pytest.raises(ValueError, match="^Incomplete snapshot fact record$"):
        Store._snapshot_state(state)
    assert accesses == []
    assert len(real_parses) == 1


def test_str_subclass_original_parser_callbacks_run_once_per_occurrence(real_parses):
    callbacks = []

    class SeenString(str):
        def startswith(self, *args, **kwargs):
            callbacks.append("startswith")
            return super().startswith(*args, **kwargs)

    Store._snapshot_state(snapshot(SeenString(IRI), SeenString(IRI)))
    assert callbacks == ["startswith", "startswith"]
    assert len(real_parses) == 2


@pytest.mark.parametrize("changed", ["term", "graph-parse"])
def test_real_literal_converter_cannot_leave_an_earlier_iri_hit(changed, monkeypatch, real_parses):
    datatype = URIRef("urn:memo:converter")
    converted = []
    failure = RuntimeError("original converter changed implementation")

    def refused(*_args, **_kwargs):
        raise failure

    def convert(value):
        converted.append(value)
        if changed == "term":
            monkeypatch.setattr(storage, "term", refused)
        else:
            monkeypatch.setattr(Graph, "parse", refused)
        return None

    monkeypatch.setitem(_toPythonMapping, datatype, convert)
    value = '"lexical"^^<urn:memo:converter>'
    expected = RuntimeError if changed == "term" else ValueError
    with pytest.raises(expected) as caught:
        Store._snapshot_state(snapshot(IRI, value, IRI))
    assert converted
    if changed == "term":
        assert caught.value is failure
    else:
        assert type(caught.value) is ValueError
        assert caught.value.__cause__ is failure
    assert len(real_parses) == 2


def test_non_iri_branch_permanently_disables_reuse_for_the_invocation(real_parses):
    Store._snapshot_state(snapshot(IRI, '"literal"', IRI, IRI))
    assert len(real_parses) == 4


@pytest.mark.parametrize("failure_site", ["parser", "n3"])
def test_unknown_parser_or_n3_failure_is_not_converted_to_success(
    failure_site, monkeypatch, real_parses
):
    failure = RuntimeError("original unknown parser or n3 failure")
    original_n3 = URIRef.n3

    def parser_refused(*_args, **_kwargs):
        raise failure

    def n3_refused(self, *args, **kwargs):
        if str(self) == "urn:memo:object":
            raise failure
        return original_n3(self, *args, **kwargs)

    with monkeypatch.context() as patch:
        if failure_site == "parser":
            patch.setattr(Graph, "parse", parser_refused)
            with pytest.raises(ValueError) as caught:
                Store._snapshot_state(snapshot(IRI, IRI))
            assert type(caught.value) is ValueError
            assert caught.value.__cause__ is failure
        else:
            patch.setattr(URIRef, "n3", n3_refused)
            with pytest.raises(RuntimeError) as caught:
                Store._snapshot_state(snapshot(IRI, IRI))
            assert caught.value is failure
    real_parses.clear()
    Store._snapshot_state(snapshot(IRI, IRI))
    assert len(real_parses) == 1


def test_capacity_excess_is_reparsed_without_eviction_of_the_first_sixteen(real_parses):
    values = [f"<urn:memo:capacity:{index}>" for index in range(17)]
    Store._snapshot_state(snapshot(*values, *values[:16], values[16], values[16]))
    assert len(real_parses) == 19


def test_successful_aliases_do_not_cross_calls(real_parses):
    state = snapshot(IRI, IRI)
    Store._snapshot_state(state)
    Store._snapshot_state(state)
    assert len(real_parses) == 2


def test_exception_does_not_publish_aliases_into_the_next_call(real_parses):
    with pytest.raises(ValueError, match="^Invalid snapshot RDF object$"):
        Store._snapshot_state(snapshot(IRI, " " + IRI))
    real_parses.clear()
    Store._snapshot_state(snapshot(IRI, IRI))
    assert len(real_parses) == 1


def test_custom_definition_keeps_the_single_argument_hook_and_disables_whole_call(real_parses):
    calls = []

    class CustomStore(Store):
        @staticmethod
        def _definition(value):
            calls.append(value)
            Store._definition(value)

    value = definition_value()
    CustomStore._snapshot_state(snapshot(IRI, IRI, definitions=[definition("D1", value)]))
    assert calls == [value]
    assert len(real_parses) == 3


@pytest.mark.parametrize("opaque_kind", ["subclass", "cycle", "depth", "scan-cap"])
def test_bounded_eligibility_never_executes_unused_user_methods(opaque_kind, real_parses):
    callbacks = []

    class Untouched(dict):
        def __iter__(self):
            callbacks.append("iter")
            raise AssertionError("qualification must not iterate a dict subclass")

        def __getitem__(self, _key):
            callbacks.append("getitem")
            raise AssertionError("qualification must not read a dict subclass")

        def items(self):
            callbacks.append("items")
            raise AssertionError("qualification must not call subclass methods")

    if opaque_kind == "subclass":
        opaque = Untouched({"unread": "value"})
    elif opaque_kind == "cycle":
        opaque = []
        opaque.append(opaque)
    elif opaque_kind == "depth":
        opaque = None
        for _ in range(2048):
            opaque = [opaque]
    else:
        opaque = [None] * 10000
    state = snapshot(IRI, IRI)
    state["unused-original-field"] = opaque
    Store._snapshot_state(state)
    assert callbacks == []
    assert len(real_parses) == 2


def test_standalone_definition_has_no_shared_or_retained_memo(real_parses):
    value = definition_value()
    value["triples"].append(dict(value["triples"][0]))
    Store._definition(value)
    Store._definition(value)
    assert len(real_parses) == 4


def test_current_term_iri_helper_failure_is_not_hidden_by_a_repeated_object(
    monkeypatch, real_parses
):
    original = rdf_snapshot.iri
    calls = []
    failure = RuntimeError("original term IRI helper failure")

    def checked(value):
        if value == "urn:memo:object":
            calls.append(value)
            if len(calls) == 3:
                raise failure
        return original(value)

    monkeypatch.setattr(rdf_snapshot, "iri", checked)
    with pytest.raises(RuntimeError) as caught:
        Store._snapshot_state(snapshot(IRI, IRI))
    assert caught.value is failure
    assert calls == ["urn:memo:object"] * 3
    assert len(real_parses) == 1
