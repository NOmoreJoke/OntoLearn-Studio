"""Bind an editor's RDF view to an approved Store-2 immutable input.

This only proves RDF coverage and retains original record identities. It does not
construct a project, authorize metadata, translate mutations or confirm writes.
Callers must obtain the source through the owning trusted project service. A
content hash is an integrity check, never a capability or human confirmation.
"""

import json
from dataclasses import dataclass

from ontolearn_engine.invalidation import family
from ontolearn_engine.storage import Store, digest

from .model import OntologyError, Snapshot, Triple
from .service import Preview, rdf_triples


@dataclass(frozen=True)
class FactSource:
    record_id: str
    subject: str
    predicate: str
    current_object: str | None
    owner: str | None
    source_row: str | None
    managed_value: str | None


@dataclass(frozen=True)
class DefinitionSource:
    layer: str
    record_id: str
    payload_digest: str  # owner retains the complete opaque payload in the snapshot


@dataclass(frozen=True, order=True)
class DefinitionReference:
    source_layer: str
    source_id: str
    target_layer: str
    target_id: str


@dataclass(frozen=True)
class StatementSource:
    triple: Triple
    kind: str  # fact or ontology-definition
    record_id: str
    index: int | None  # exact position in the owner's immutable triples list


@dataclass(frozen=True)
class BoundRdfProjection:
    source_ref: str
    editor: Snapshot
    facts: tuple[FactSource, ...]  # includes mapped deletion tombstones
    definitions: tuple[DefinitionSource, ...]
    definition_references: tuple[DefinitionReference, ...]
    statement_sources: tuple[StatementSource, ...]  # retains overlapping supports

    def require_source(self, source_ref: str, source: dict) -> None:
        _validated_source(source_ref, source)
        if source_ref != self.source_ref:
            raise OntologyError("stale_source_projection")

    def removed_sources(self, preview: Preview) -> tuple[StatementSource, ...]:
        # A preview for another project/revision/editor cannot select source records.
        preview.require_current(self.editor)
        removed = set(preview.removed)
        known = {item.triple for item in self.statement_sources}
        if not removed <= known:
            raise OntologyError("projection_origin_missing")
        return tuple(item for item in self.statement_sources if item.triple in removed)


def _validated_source(source_ref: str, source: dict) -> None:
    try:
        if not isinstance(source_ref, str) or digest(source) != source_ref:
            raise OntologyError("source_integrity_mismatch")
        if not isinstance(source, dict) or set(source) != {
            "project",
            "projectRevision",
            "dependencyVector",
            "state",
        }:
            raise OntologyError("invalid_source_snapshot")
        if not isinstance(source["project"], str) or not source["project"]:
            raise OntologyError("invalid_source_snapshot")
        if type(source["projectRevision"]) is not int or source["projectRevision"] < 0:
            raise OntologyError("invalid_source_snapshot")
        if not isinstance(source["dependencyVector"], dict):
            raise OntologyError("invalid_source_snapshot")
        for key, version in source["dependencyVector"].items():
            family(key)
            if type(version) is not int or version < 0:
                raise OntologyError("invalid_source_snapshot")
        state = source["state"]
        if (
            not isinstance(state, dict)
            or set(state) != {"definitions", "facts", "mappingState"}
            or not isinstance(state["definitions"], list)
            or not isinstance(state["facts"], list)
            or not isinstance(state["mappingState"], dict)
        ):
            raise OntologyError("invalid_source_snapshot")
        # Reuse the approved owning implementation; no parallel record validator,
        # migration, SQL writer, Store instance, file path or database is introduced.
        Store._snapshot_state(state)
    except OntologyError:
        raise
    except (ValueError, KeyError, TypeError, AttributeError, IndexError, OverflowError):
        raise OntologyError("invalid_source_snapshot") from None


def bind_rdf_projection(source_ref: str, source: dict, editor: Snapshot) -> BoundRdfProjection:
    """Require exact RDF equality before retaining a source-to-editor binding.

    The caller supplies the editor projection and metadata; this function never
    guesses identifiers, entity annotations, public schemas or ownership. Opaque
    payloads, non-RDF metadata and definition-to-entity reference semantics still
    belong to T01/T00. Their content remains bound by the full source digest.
    """
    _validated_source(source_ref, source)
    if (editor.project, editor.revision) != (source["project"], source["projectRevision"]):
        raise OntologyError("projection_identity_mismatch")
    expected = set(rdf_triples(editor))
    facts = []
    definitions = []
    edges = set()
    statements = []
    try:
        for record in sorted(source["state"]["facts"], key=lambda value: value["id"]):
            facts.append(
                FactSource(
                    record["id"],
                    record["subject"],
                    record["predicate"],
                    record["object"],
                    record["owner"],
                    record["source_row"],
                    record["managed_value"],
                )
            )
            if record["object"] is not None:
                statements.append(
                    StatementSource(
                        Triple(record["subject"], record["predicate"], record["object"]),
                        "fact",
                        record["id"],
                        None,
                    )
                )
        for record in sorted(
            source["state"]["definitions"], key=lambda value: (value["layer"], value["id"])
        ):
            value = json.loads(record["payload"])
            definitions.append(DefinitionSource(record["layer"], record["id"], digest(value)))
            if not isinstance(value, dict):
                continue
            for reference in value.get("references", []):
                edges.add(
                    DefinitionReference(
                        record["layer"], record["id"], reference["layer"], reference["id"]
                    )
                )
            if record["layer"] == "ontology":
                for index, triple in enumerate(value.get("triples", [])):
                    statements.append(
                        StatementSource(
                            Triple(**triple), "ontology-definition", record["id"], index
                        )
                    )
    except OntologyError:
        raise
    except (ValueError, KeyError, TypeError, AttributeError, IndexError, OverflowError):
        raise OntologyError("invalid_source_snapshot") from None
    if expected != {item.triple for item in statements}:
        # Neither omission nor fabricated replacement is accepted, even if counts match.
        raise OntologyError("projection_rdf_mismatch")
    return BoundRdfProjection(
        source_ref,
        editor,
        tuple(facts),
        tuple(definitions),
        tuple(sorted(edges)),
        tuple(statements),
    )
