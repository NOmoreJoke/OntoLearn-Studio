"""Pure versioned Entity metadata on the existing ontology definition payload.

Inputs are the caller's already loaded, bounded Store states. No Store, SQL,
second model, migration, authority, or RDF synonyms vocabulary lives here.
Historical opaque namespaces remain data, never an inferred issuer/provenance.
"""

import json
import re
from copy import deepcopy

from rdflib import OWL, RDF, RDFS, XSD, Literal, URIRef

from ontolearn_engine.rdf_snapshot import iri, term

KEY = "entityMetadata"
KNOWN = frozenset({"triples", "singleValuedPredicates", "references", KEY})
FIELDS = frozenset({"identifier", "labels", "definitions", "synonyms", "examples"})
DATATYPES = frozenset(
    str(XSD[name])
    for name in ("string", "boolean", "integer", "decimal", "double", "date", "dateTime")
)


class MetadataError(ValueError):
    """Fixed private reason only; do not expose RDF, values or exception text."""


def _same(left, right):
    # Python equality alone would consider bool and int equal in opaque JSON.
    return json.dumps(left, ensure_ascii=False, sort_keys=True, allow_nan=False) == json.dumps(
        right, ensure_ascii=False, sort_keys=True, allow_nan=False
    )


def _scalar(value):
    return type(value) is str and not any(0xD800 <= ord(char) <= 0xDFFF for char in value)


def _text(value):
    return _scalar(value) and bool(value.strip()) and len(value) <= 16000


def validate_namespace(value):
    """Exact JSON equivalent of the five actual T02 Entity metadata fields."""
    if (
        type(value) is not dict
        or set(value) != {"entityMetadataVersion", "entities"}
        or type(value["entityMetadataVersion"]) is not int
        or value["entityMetadataVersion"] != 1
        or type(value["entities"]) is not dict
    ):
        raise MetadataError("invalid_metadata_namespace")
    for identity, item in value["entities"].items():
        if not _scalar(identity):
            raise MetadataError("invalid_metadata_iri")
        iri(identity)
        if type(item) is not dict or set(item) != FIELDS:
            raise MetadataError("invalid_metadata_fields")
        if not _scalar(item["identifier"]) or not re.fullmatch(
            r"[A-Za-z0-9_][A-Za-z0-9_-]*", item["identifier"]
        ):
            raise MetadataError("invalid_metadata_identifier")
        for field in ("labels", "definitions"):
            values = item[field]
            if type(values) is not list:
                raise MetadataError("invalid_metadata_localized")
            seen = set()
            for pair in values:
                if (
                    type(pair) is not list
                    or len(pair) != 2
                    or not _text(pair[0])
                    or not _scalar(pair[1])
                    or pair[1]
                    and not re.fullmatch(r"[a-z]+(?:-[a-z0-9]+)*", pair[1])
                ):
                    raise MetadataError("invalid_metadata_localized")
                if tuple(pair) in seen:
                    raise MetadataError("duplicate_metadata_value")
                seen.add(tuple(pair))
        for field in ("synonyms", "examples"):
            values = item[field]
            if type(values) is not list or any(not _text(value) for value in values):
                raise MetadataError("invalid_metadata_text")
            if len(set(values)) != len(values):
                raise MetadataError("duplicate_metadata_value")
    return value


def _namespace(value):
    if type(value) is not dict or KEY not in value:
        return None
    try:
        return validate_namespace(value[KEY])
    except (ValueError, TypeError):
        return None  # A pre-existing opaque collision remains historical data.


def _values(state):
    return {
        record["id"]: json.loads(record["payload"])
        for record in state["definitions"]
        if record["layer"] == "ontology"
    }


def merge_plan(state, plan):
    """Same-base public known edits -> complete immutable effective plan.

    The caller must already hold its original application transaction and have
    compared the actual base. No caller-supplied before value is authoritative.
    """
    result = deepcopy(plan)
    current = _values(state)
    for definition in result.get("definitions", []):
        if definition["layer"] != "ontology":
            continue
        value = definition["value"]
        if type(value) is not dict or set(value) - KNOWN:
            raise MetadataError("unsupported_public_ontology_field")
        old = current.get(definition["id"])
        if definition["id"] in current and type(old) is not dict:
            raise MetadataError("opaque_payload_conflict")
        if KEY in value:
            validate_namespace(value[KEY])
        if type(old) is dict:
            if KEY in old and _namespace(old) is None and KEY in value:
                raise MetadataError("metadata_namespace_conflict")
            # Unknown values and omitted M are inherited, never writable via API.
            for key, item in old.items():
                if key not in KNOWN or key == KEY and KEY not in value:
                    value[key] = deepcopy(item)
    return result


def validate_payload_update(old, new):
    """Store's ordinary replacement cannot create/overwrite an opaque collision."""
    if type(new) is not dict or KEY not in new:
        return
    unchanged = type(old) is dict and KEY in old and _same(old[KEY], new[KEY])
    if unchanged:
        return
    if type(old) is dict and KEY in old and _namespace(old) is None:
        raise MetadataError("metadata_namespace_conflict")
    validate_namespace(new[KEY])


def _rdf(state, values):
    """Preserve all supports in state; indexes only consolidate RDF values."""
    slots = {}
    occurrences = set()

    def add(subject, predicate, obj):
        slots.setdefault((subject, predicate), set()).add(obj)
        occurrences.update((subject, predicate))
        if obj.startswith("<") and obj.endswith(">"):
            occurrences.add(obj[1:-1])

    for payload in values.values():
        if type(payload) is dict:
            for triple in payload.get("triples", []):
                add(triple["subject"], triple["predicate"], triple["object"])
    for fact in state["facts"]:
        if fact["object"] is not None:
            add(fact["subject"], fact["predicate"], fact["object"])
    return slots, occurrences


def _class(identity, slots):
    kinds = slots.get((identity, str(RDF.type)), set())
    return kinds in ({f"<{RDFS.Class}>"}, {f"<{OWL.Class}>"})


def _entity(identity, item, slots):
    types = slots.get((identity, str(RDF.type)), set())
    special = {
        f"<{RDFS.Class}>": "class",
        f"<{OWL.Class}>": "class",
        f"<{OWL.ObjectProperty}>": "objectProperty",
        f"<{OWL.DatatypeProperty}>": "dataProperty",
    }
    present = types & special.keys()
    if present:
        if len(types) != 1:
            raise MetadataError("ambiguous_metadata_kind")
        kind = special[next(iter(present))]
    else:
        kind = "individual"
        for value in types:
            parsed = term(value)
            if not isinstance(parsed, URIRef) or not _class(str(parsed), slots):
                raise MetadataError("metadata_class_reference_required")
    for field, predicate in (("labels", RDFS.label), ("definitions", RDFS.comment)):
        observed = set()
        for value in slots.get((identity, str(predicate)), set()):
            parsed = term(value)
            if not isinstance(parsed, Literal) or parsed.datatype not in {None, XSD.string}:
                raise MetadataError("metadata_annotation_literal_required")
            observed.add((str(parsed), parsed.language or ""))
        if observed != {tuple(pair) for pair in item[field]}:
            raise MetadataError("metadata_rdf_mismatch")
    for predicate in (RDFS.subClassOf, RDFS.domain, RDFS.range):
        targets = slots.get((identity, str(predicate)), set())
        if targets and (
            predicate == RDFS.subClassOf
            and kind != "class"
            or predicate in {RDFS.domain, RDFS.range}
            and kind not in {"objectProperty", "dataProperty"}
        ):
            raise MetadataError("metadata_field_not_applicable")
        for value in targets:
            parsed = term(value)
            if not isinstance(parsed, URIRef):
                raise MetadataError("metadata_class_reference_required")
            if predicate == RDFS.range and kind == "dataProperty":
                if str(parsed) not in DATATYPES:
                    raise MetadataError("metadata_unsupported_datatype")
            elif not _class(str(parsed), slots):
                raise MetadataError("metadata_class_reference_required")


def _inspect(state, *, force_rdf=False):
    values = _values(state)
    namespaces = {home: _namespace(value) for home, value in values.items()}
    # Legacy projects with no recognized M do not allocate a new RDF read model.
    if not force_rdf and not any(namespace is not None for namespace in namespaces.values()):
        return values, namespaces, {}, {}, set()
    slots, occurrences = _rdf(state, values)
    homes = {}
    for home, namespace in namespaces.items():
        if namespace is not None:
            for identity in namespace["entities"]:
                homes.setdefault(identity, []).append(home)
    invalid = {}
    for home, namespace in namespaces.items():
        if namespace is None:
            continue
        try:
            for identity, item in namespace["entities"].items():
                if len(homes[identity]) != 1:
                    raise MetadataError("ambiguous_metadata_home")
                _entity(identity, item, slots)
        except MetadataError as error:
            invalid[home] = str(error)
    return values, namespaces, homes, invalid, occurrences


def validate_change(before, after):
    """Actual whole candidate state, before any versions/marker are published."""
    old, old_ns, _, old_invalid, _ = _inspect(before)
    new, _, homes, invalid, occurrences = _inspect(
        after, force_rdf=any(namespace is not None for namespace in old_ns.values())
    )
    for home, value in new.items():
        validate_payload_update(old.get(home), value)
        if home in invalid:
            # A shape-looking legacy conflict is preserved, not silently upgraded.
            preserved = (
                home in old_invalid
                and type(old.get(home)) is dict
                and _same(old[home].get(KEY), value.get(KEY))
            )
            if not preserved:
                raise MetadataError(invalid[home])
        if (
            type(old.get(home)) is dict
            and KEY in old[home]
            and home in old_invalid
            and type(value) is dict
            and KEY in value
            and not _same(old[home][KEY], value[KEY])
        ):
            raise MetadataError("metadata_namespace_conflict")
    for home, namespace in old_ns.items():
        if namespace is None or home in old_invalid:
            continue
        if home in new and (type(new[home]) is not dict or KEY not in new[home]):
            raise MetadataError("metadata_loss")
        for identity in namespace["entities"]:
            if identity not in homes and identity in occurrences:
                raise MetadataError("metadata_entity_still_referenced")


def validate_compensation(before, after):
    """Only after existing compensation.resolve authenticated the full target.

    Restoring an old absent/opaque namespace is allowed; this function is not a
    public mode flag. Existing unresolved historical collisions stay opaque. New
    RDF inconsistency in a namespace retained from a valid current state fails.
    """
    old, _, _, old_invalid, _ = _inspect(before)
    new, _, _, invalid, _ = _inspect(after)
    for home, reason in invalid.items():
        if not (home in old_invalid and _same(old[home][KEY], new[home][KEY])):
            raise MetadataError(reason)


def validate_supported_pair(before, after, *, compensation=False):
    """Public plan cannot mutate inherited opaque fields, even in forged plans."""
    old = json.loads(before["payload"]) if before is not None else None
    new = json.loads(after["payload"]) if after is not None else None
    if compensation or new is None:
        return
    if type(new) is not dict:
        raise MetadataError("unsupported_public_ontology_field")
    old_extra = (
        {key: value for key, value in old.items() if key not in KNOWN} if type(old) is dict else {}
    )
    new_extra = {key: value for key, value in new.items() if key not in KNOWN}
    if not _same(old_extra, new_extra):
        raise MetadataError("opaque_payload_conflict")
    validate_payload_update(old, new)
