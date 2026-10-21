"""Pure edit planning. Owning T01 revalidates and translates into one Store commit."""

import hashlib
import json
from dataclasses import asdict, dataclass, replace

from rdflib import OWL, RDF, RDFS, Literal

from .model import Entity, Fact, OntologyError, Snapshot, Triple, validate


@dataclass(frozen=True)
class Put:
    entity: Entity
    create: bool  # explicit add versus edit; an edit may not silently create


@dataclass(frozen=True)
class Delete:
    iri: str


@dataclass(frozen=True)
class Copy:
    source: str
    iri: str
    identifier: str


@dataclass(frozen=True, order=True)
class Reference:
    target: str
    source: str
    field: str
    statement: tuple[str, ...] = ()  # exact impact, not a collapsed subject/field count


def references(snapshot: Snapshot) -> tuple[Reference, ...]:
    result = set()
    entity_ids = {item.iri for item in snapshot.entities}
    for entity in snapshot.entities:
        for field in ("parents", "domain", "range", "types"):
            for target in getattr(entity, field):
                if target in entity_ids:
                    result.add(Reference(target, entity.iri, field))
    for fact in snapshot.facts:
        for field in ("subject", "predicate", "object"):
            target = getattr(fact, field)
            if field == "object":
                if not target.startswith("<"):
                    continue
                target = target[1:-1]
            result.add(
                Reference(
                    target,
                    fact.subject,
                    f"fact.{field}",
                    (fact.subject, fact.predicate, fact.object),
                )
            )
    for ref in snapshot.external_references:
        result.add(Reference(ref.target, ref.source, "external"))
    return tuple(sorted(result))


def deletion_impact(snapshot: Snapshot, target: str) -> tuple[Reference, ...]:
    validate(snapshot)
    if target not in {item.iri for item in snapshot.entities}:
        raise OntologyError("not_found")
    return tuple(ref for ref in references(snapshot) if ref.target == target)


def rdf_triples(snapshot: Snapshot) -> tuple[Triple, ...]:
    validate(snapshot)
    triples = {fact.triple() for fact in snapshot.facts}
    kinds = {
        "class": RDFS.Class,
        "objectProperty": OWL.ObjectProperty,
        "dataProperty": OWL.DatatypeProperty,
    }
    for item in snapshot.entities:
        if item.kind in kinds:
            rdf_type = (
                OWL.Class if item.kind == "class" and item.class_type == "owl" else kinds[item.kind]
            )
            triples.add(Triple(item.iri, str(RDF.type), f"<{rdf_type}>"))
        for field, predicate in (("labels", RDFS.label), ("definitions", RDFS.comment)):
            for text, language in getattr(item, field):
                triples.add(
                    Triple(item.iri, str(predicate), Literal(text, lang=language or None).n3())
                )
        for field, predicate in (
            ("parents", RDFS.subClassOf),
            ("domain", RDFS.domain),
            ("range", RDFS.range),
            ("types", RDF.type),
        ):
            for target in getattr(item, field):
                triples.add(Triple(item.iri, str(predicate), f"<{target}>"))
    return tuple(sorted(triples))


def snapshot_digest(snapshot: Snapshot) -> str:
    # Structural order is not an observable difference. Text/list order is metadata.
    payload = asdict(snapshot)
    for key in ("entities", "facts", "external_references"):
        payload[key] = sorted(payload[key], key=lambda x: json.dumps(x, sort_keys=True))
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@dataclass(frozen=True)
class EntityChange:
    iri: str
    before: Entity | None
    after: Entity | None


@dataclass(frozen=True)
class Preview:
    project: str
    revision: int
    base_digest: str
    candidate: Snapshot
    added: tuple[Triple, ...]
    removed: tuple[Triple, ...]
    changed_entities: tuple[str, ...]  # includes metadata-only edits
    deletion_references: tuple[Reference, ...]
    entity_changes: tuple[EntityChange, ...]

    def require_current(self, current: Snapshot) -> None:
        """A guard for T01, not a user confirmation token or a commit operation."""
        validate(current)
        if (current.project, current.revision, snapshot_digest(current)) != (
            self.project,
            self.revision,
            self.base_digest,
        ):
            raise OntologyError("stale_preview")


def change_preview(
    snapshot: Snapshot,
    commands: tuple[Put | Delete | Copy, ...] = (),
    *,
    add_facts: tuple[Fact, ...] = (),
    remove_facts: tuple[Fact, ...] = (),
) -> Preview:
    validate(snapshot)
    if not all(isinstance(value, tuple) for value in (commands, add_facts, remove_facts)):
        raise OntologyError("immutable_tuple_required")
    entities = {item.iri: item for item in snapshot.entities}
    original = entities.copy()
    touched: set[str] = set()
    impact: set[Reference] = set()
    for command in commands:
        if not isinstance(command, Put | Delete | Copy):
            raise OntologyError("unsupported_command")
        target = command.entity.iri if isinstance(command, Put) else command.iri
        if target in touched:
            raise OntologyError("duplicate_command")
        touched.add(target)
        if isinstance(command, Put):
            if command.create and target in entities:
                raise OntologyError("already_exists")
            if not command.create and target not in entities:
                raise OntologyError("not_found")
            if not command.create and entities[target].kind != command.entity.kind:
                raise OntologyError("kind_change_requires_new_entity")
            entities[target] = command.entity
        elif isinstance(command, Copy):
            if command.source not in original:
                raise OntologyError("not_found")
            if target in entities:
                raise OntologyError("already_exists")
            # Copy definition/metadata, never silently clone all instance assertions.
            entities[target] = replace(
                original[command.source], iri=target, identifier=command.identifier
            )
        elif isinstance(command, Delete):
            if target not in entities:
                raise OntologyError("not_found")
            impact.update(deletion_impact(snapshot, target))
            del entities[target]
        else:
            raise OntologyError("unsupported_command")
    if len(set(add_facts)) != len(add_facts) or len(set(remove_facts)) != len(remove_facts):
        raise OntologyError("duplicate_fact_command")
    if set(add_facts) & set(remove_facts):
        raise OntologyError("contradictory_fact_command")
    if not set(remove_facts) <= set(snapshot.facts):
        raise OntologyError("fact_not_found")
    candidate = replace(
        snapshot,
        entities=tuple(sorted(entities.values(), key=lambda item: item.iri)),
        facts=tuple(sorted((set(snapshot.facts) - set(remove_facts)) | set(add_facts))),
    )
    validate(candidate)  # validate complete final state, including external references
    before, after = set(rdf_triples(snapshot)), set(rdf_triples(candidate))
    changed = tuple(
        sorted(
            key for key in set(original) | set(entities) if original.get(key) != entities.get(key)
        )
    )
    return Preview(
        snapshot.project,
        snapshot.revision,
        snapshot_digest(snapshot),
        candidate,
        tuple(sorted(after - before)),
        tuple(sorted(before - after)),
        changed,
        tuple(sorted(impact)),
        tuple(EntityChange(key, original.get(key), entities.get(key)) for key in changed),
    )
