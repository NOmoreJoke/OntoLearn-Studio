"""Immutable editor input; intentionally not a second project or wire schema."""

import re
from dataclasses import dataclass
from typing import Literal

from rdflib import RDF, RDFS, XSD, URIRef
from rdflib import Literal as RDFLiteral

from ontolearn_engine.rdf_snapshot import iri, term

Kind = Literal["class", "objectProperty", "dataProperty", "individual"]
KINDS = {"class", "objectProperty", "dataProperty", "individual"}
DATATYPES = frozenset(
    str(XSD[name])
    for name in ("string", "boolean", "integer", "decimal", "double", "date", "dateTime")
)


class OntologyError(ValueError):
    """Internal fixed reason and field location, never an underlying parser message."""

    def __init__(self, reason: str, location: str = ""):
        self.reason = reason
        self.location = location
        super().__init__(reason)


@dataclass(frozen=True, order=True)
class Triple:
    subject: str
    predicate: str
    object: str

    def __post_init__(self):
        try:
            iri(self.subject)
            iri(self.predicate)
            if term(self.object).n3() != self.object:
                raise ValueError("Noncanonical RDF object")
        except (ValueError, TypeError, AttributeError):
            raise OntologyError("invalid_rdf_term") from None


@dataclass(frozen=True)
class Entity:
    iri: str
    kind: Kind
    identifier: str
    labels: tuple[tuple[str, str], ...] = ()  # text, language (empty = no language)
    definitions: tuple[tuple[str, str], ...] = ()
    synonyms: tuple[str, ...] = ()  # project metadata, no invented RDF vocabulary
    examples: tuple[str, ...] = ()
    parents: tuple[str, ...] = ()
    domain: tuple[str, ...] = ()
    range: tuple[str, ...] = ()
    types: tuple[str, ...] = ()
    class_type: Literal["rdfs", "owl"] | None = None


@dataclass(frozen=True, order=True)
class Fact:
    """Assertion identity remains owning Store's concern; editor compares RDF values."""

    subject: str
    predicate: str
    object: str

    def triple(self) -> Triple:
        return Triple(self.subject, self.predicate, self.object)


@dataclass(frozen=True, order=True)
class ExternalReference:
    source: str  # stable owner-supplied definition ID, not a path or user value
    target: str


@dataclass(frozen=True)
class Snapshot:
    project: str
    revision: int
    entities: tuple[Entity, ...] = ()
    facts: tuple[Fact, ...] = ()
    external_references: tuple[ExternalReference, ...] = ()


def _unique_tuple(value: object, location: str) -> None:
    if not isinstance(value, tuple):
        raise OntologyError("immutable_tuple_required", location)
    try:
        if len(set(value)) != len(value):
            raise OntologyError("duplicate_value", location)
    except TypeError:
        raise OntologyError("invalid_value", location) from None


def validate(snapshot: Snapshot) -> None:
    if not isinstance(snapshot, Snapshot):
        raise OntologyError("invalid_snapshot")
    if not isinstance(snapshot.project, str) or not snapshot.project:
        raise OntologyError("project_required")
    if type(snapshot.revision) is not int or snapshot.revision < 0:
        raise OntologyError("invalid_revision")
    for field, element_type, reason in (
        ("entities", Entity, "invalid_entity"),
        ("facts", Fact, "invalid_fact"),
        ("external_references", ExternalReference, "invalid_external_reference"),
    ):
        values = getattr(snapshot, field)
        if not isinstance(values, tuple):
            raise OntologyError("immutable_tuple_required", field)
        # Check the typed collection before hashing or dereferencing its elements.
        if any(not isinstance(value, element_type) for value in values):
            raise OntologyError(reason, field)
        _unique_tuple(values, field)
    entities = {item.iri: item for item in snapshot.entities}
    if len(entities) != len(snapshot.entities):
        raise OntologyError("duplicate_iri")
    for item in snapshot.entities:
        try:
            iri(item.iri)
        except (ValueError, TypeError):
            raise OntologyError("invalid_iri") from None
        if item.kind not in KINDS:
            raise OntologyError("unsupported_kind")
        if item.class_type not in {None, "rdfs", "owl"} or (
            item.kind != "class" and item.class_type is not None
        ):
            raise OntologyError("invalid_class_type")
        if not isinstance(item.identifier, str) or not re.fullmatch(
            r"[A-Za-z0-9_][A-Za-z0-9_-]*", item.identifier
        ):
            raise OntologyError("invalid_identifier")
        for field in ("labels", "definitions"):
            values = getattr(item, field)
            _unique_tuple(values, field)
            for value in values:
                if not isinstance(value, tuple) or len(value) != 2:
                    raise OntologyError("invalid_text", field)
                text, language = value
                if not isinstance(text, str) or not text.strip() or len(text) > 16000:
                    raise OntologyError("invalid_text", field)
                if not isinstance(language, str) or (
                    language and not re.fullmatch(r"[a-z]+(?:-[a-z0-9]+)*", language)
                ):
                    raise OntologyError("invalid_language", field)
        for field in ("synonyms", "examples"):
            values = getattr(item, field)
            _unique_tuple(values, field)
            if any(not isinstance(v, str) or not v.strip() or len(v) > 16000 for v in values):
                raise OntologyError("invalid_text", field)
        for field in ("parents", "domain", "range", "types"):
            values = getattr(item, field)
            _unique_tuple(values, field)
            if values and (
                (field == "parents" and item.kind != "class")
                or (
                    field in {"domain", "range"}
                    and item.kind not in {"objectProperty", "dataProperty"}
                )
                or (field == "types" and item.kind != "individual")
            ):
                raise OntologyError("field_not_applicable", field)
            for target in values:
                if field == "range" and item.kind == "dataProperty":
                    if target not in DATATYPES:
                        raise OntologyError("unsupported_datatype", field)
                elif target not in entities or entities[target].kind != "class":
                    raise OntologyError("class_reference_required", field)
    for fact in snapshot.facts:
        fact.triple()
        if fact.subject not in entities or entities[fact.subject].kind != "individual":
            raise OntologyError("individual_reference_required", "subject")
        obj = term(fact.object)
        if isinstance(obj, RDFLiteral):
            if obj.datatype and str(obj.datatype) not in DATATYPES:
                raise OntologyError("unsupported_datatype", "object")
            if getattr(obj, "ill_typed", False):
                raise OntologyError("invalid_literal", "object")
        # One editable representation per RDF statement: type/name/comment belong
        # to the entity fields. The approved snapshot adapter must consolidate them
        # without changing Store ownership or dropping source evidence.
        if fact.predicate in {str(RDF.type), str(RDFS.label), str(RDFS.comment)}:
            raise OntologyError("entity_field_required", "predicate")
        prop = entities.get(fact.predicate)
        if prop is None or prop.kind not in {"objectProperty", "dataProperty"}:
            raise OntologyError("property_reference_required", "predicate")
        if prop.kind == "objectProperty":
            if (
                not isinstance(obj, URIRef)
                or str(obj) not in entities
                or (entities[str(obj)].kind != "individual")
            ):
                raise OntologyError("individual_reference_required", "object")
        elif not isinstance(obj, RDFLiteral):
            raise OntologyError("literal_required", "object")
    for reference in snapshot.external_references:
        if not isinstance(reference.source, str) or not reference.source:
            raise OntologyError("invalid_external_reference")
        if reference.target not in entities:
            raise OntologyError("dangling_external_reference")
