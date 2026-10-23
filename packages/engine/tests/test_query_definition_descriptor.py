"""Source-only definitions for the exact managed query descriptor boundary.

No worker, graph, Store, database, Session or execution path is needed here.
These definitions have not been executed under the SOURCE-only ticket.
"""

import hashlib
import json
from copy import deepcopy

import pytest
from ontolearn_engine.semantic_execution import SemanticRequestFault, build_request

QUERY = 'SELECT ?item WHERE { ?item <urn:label> "泵站" . }'
DESCRIPTOR = {
    "version": 1,
    "name": "泵站查询",
    "description": "  原说明\n",
    "scope": "asserted",
    "capabilityQuestion": "  哪些泵站？\n",
    "source": "editor",
}


def request_material(definition, *, layer="query"):
    snapshot = {
        "state": {
            "facts": [],
            "definitions": [
                {"layer": layer, "id": "Q1", "payload": json.dumps(definition, ensure_ascii=True)}
            ],
        }
    }
    encoded = json.dumps(
        snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    input_ = {
        "inputSnapshotId": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
        "scope": "asserted",
        "derivedResultIds": [],
        "definitionId": "Q1",
    }
    return snapshot, input_


def build_definition(definition):
    snapshot, input_ = request_material(definition)
    return build_request(snapshot, "query.execute", input_, {})


def managed_definition():
    return {"text": QUERY, "references": [], "descriptor": deepcopy(DESCRIPTOR)}


@pytest.mark.parametrize("scope", ["asserted", "asserted+derived"])
@pytest.mark.parametrize("source", ["template", "visual", "editor", "model"])
def test_exact_descriptor_keeps_authenticated_snapshot_and_execution_text(scope, source):
    definition = managed_definition()
    definition["descriptor"].update(scope=scope, source=source)
    snapshot, input_ = request_material(definition)
    before = deepcopy(snapshot)
    result = build_request(snapshot, "query.execute", input_, {})
    assert result == {
        "snapshot": snapshot,
        "capability": "query.execute",
        "input": input_,
        "parameters": {},
        "selected": None,
    }
    assert json.loads(result["snapshot"]["state"]["definitions"][0]["payload"]) == definition
    assert definition["text"] == QUERY
    result["snapshot"]["state"]["definitions"].clear()
    assert snapshot == before


@pytest.mark.parametrize("text", ["", "  SELECT ?s WHERE { ?s ?p ?o }\n"])
@pytest.mark.parametrize("references", [None, [], [{"layer": "ontology", "id": "O1"}]])
def test_legacy_definition_without_descriptor_keeps_original_shape_and_text(text, references):
    definition = {"text": text}
    if references is not None:
        definition["references"] = references
    result = build_definition(definition)
    assert json.loads(result["snapshot"]["state"]["definitions"][0]["payload"]) == definition


@pytest.mark.parametrize("version", [None, False, True, 0, 2, 1.0, "1", [], {}])
def test_descriptor_rejects_wrong_version_or_version_type(version):
    definition = managed_definition()
    definition["descriptor"]["version"] = version
    with pytest.raises(SemanticRequestFault, match="^SEMANTIC_REQUEST_INVALID$"):
        build_definition(definition)


@pytest.mark.parametrize("descriptor", [None, [], "descriptor", 1, True])
def test_descriptor_rejects_non_object(descriptor):
    definition = managed_definition()
    definition["descriptor"] = descriptor
    with pytest.raises(SemanticRequestFault):
        build_definition(definition)


@pytest.mark.parametrize("field", list(DESCRIPTOR))
def test_descriptor_rejects_missing_field(field):
    definition = managed_definition()
    del definition["descriptor"][field]
    with pytest.raises(SemanticRequestFault):
        build_definition(definition)


@pytest.mark.parametrize("field", ["sparql", "text", "definitionId", "extra"])
def test_descriptor_rejects_extra_field_and_duplicated_text(field):
    definition = managed_definition()
    definition["descriptor"][field] = QUERY
    with pytest.raises(SemanticRequestFault):
        build_definition(definition)


@pytest.mark.parametrize("field", ["name", "description", "capabilityQuestion", "scope", "source"])
@pytest.mark.parametrize("value", [None, False, 1, [], {}])
def test_descriptor_rejects_non_string_fields(field, value):
    definition = managed_definition()
    definition["descriptor"][field] = value
    with pytest.raises(SemanticRequestFault):
        build_definition(definition)


@pytest.mark.parametrize(
    "field,value",
    [("scope", "derived"), ("scope", ""), ("source", "agent"), ("source", " editor ")],
)
def test_descriptor_rejects_unknown_scope_or_source(field, value):
    definition = managed_definition()
    definition["descriptor"][field] = value
    with pytest.raises(SemanticRequestFault):
        build_definition(definition)


@pytest.mark.parametrize(
    "field,maximum", [("name", 128), ("description", 4096), ("capabilityQuestion", 4096)]
)
@pytest.mark.parametrize("character", ["界", "😀"])
def test_descriptor_enforces_utf16_limit_at_and_above_boundary(field, maximum, character):
    definition = managed_definition()
    units = 2 if ord(character) > 0xFFFF else 1
    definition["descriptor"][field] = character * (maximum // units)
    build_definition(definition)
    definition["descriptor"][field] += "x"
    with pytest.raises(SemanticRequestFault):
        build_definition(definition)


@pytest.mark.parametrize("field", ["name", "description", "capabilityQuestion"])
@pytest.mark.parametrize("surrogate", ["\ud800", "\udfff"])
def test_descriptor_rejects_non_scalar_unicode(field, surrogate):
    definition = managed_definition()
    definition["descriptor"][field] = "x" + surrogate
    with pytest.raises(SemanticRequestFault):
        build_definition(definition)


@pytest.mark.parametrize("name", ["", " ", "\ufeffname", "name\x85", "\x1cname", "name\u3000"])
def test_descriptor_rejects_noncanonical_or_empty_name_without_rewriting(name):
    definition = managed_definition()
    definition["descriptor"]["name"] = name
    snapshot, input_ = request_material(definition)
    before = deepcopy(snapshot)
    with pytest.raises(SemanticRequestFault):
        build_request(snapshot, "query.execute", input_, {})
    assert snapshot == before


@pytest.mark.parametrize("field", ["description", "capabilityQuestion"])
@pytest.mark.parametrize("value", ["", "  \ufeff\n", "x\n y"])
def test_descriptor_preserves_optional_text_whitespace(field, value):
    definition = managed_definition()
    definition["descriptor"][field] = value
    result = build_definition(definition)
    actual = json.loads(result["snapshot"]["state"]["definitions"][0]["payload"])
    assert actual["descriptor"][field] == value


@pytest.mark.parametrize("text", ["", " ", " " + QUERY, QUERY + "\ufeff", "x" * 65537])
def test_managed_text_must_be_canonical_draft_sparql(text):
    definition = managed_definition()
    definition["text"] = text
    with pytest.raises(SemanticRequestFault):
        build_definition(definition)


def test_managed_text_utf16_boundary_preserves_exact_execution_text():
    definition = managed_definition()
    definition["text"] = "😀" * 32768
    result = build_definition(definition)
    actual = json.loads(result["snapshot"]["state"]["definitions"][0]["payload"])
    assert actual["text"] == definition["text"]
    definition["text"] += "x"
    with pytest.raises(SemanticRequestFault):
        build_definition(definition)


@pytest.mark.parametrize("references", [None, "reference", {}])
def test_managed_definition_does_not_relax_original_references_type(references):
    definition = managed_definition()
    definition["references"] = references
    with pytest.raises(SemanticRequestFault):
        build_definition(definition)


def test_managed_definition_does_not_relax_definition_extra_keys():
    definition = managed_definition()
    definition["extra"] = True
    with pytest.raises(SemanticRequestFault):
        build_definition(definition)


@pytest.mark.parametrize("references", [None, [{"layer": "ontology", "id": "O1"}]])
def test_managed_definition_preserves_optional_original_references(references):
    definition = managed_definition()
    if references is None:
        del definition["references"]
    else:
        definition["references"] = references
    result = build_definition(definition)
    assert json.loads(result["snapshot"]["state"]["definitions"][0]["payload"]) == definition


@pytest.mark.parametrize("text", [None, False, 1, [], {}, "x\ud800", "x\udfff"])
def test_managed_text_rejects_wrong_type_and_non_scalar_unicode(text):
    definition = managed_definition()
    definition["text"] = text
    with pytest.raises(SemanticRequestFault):
        build_definition(definition)


def test_descriptor_is_not_admitted_on_constraint_definition():
    definition = {"turtle": "", "enabled": True, "descriptor": deepcopy(DESCRIPTOR)}
    snapshot, input_ = request_material(definition, layer="constraint")
    with pytest.raises(SemanticRequestFault):
        build_request(snapshot, "validation.execute", input_, {})
