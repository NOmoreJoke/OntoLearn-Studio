"""Private checks of finite, explicitly supplied metadata material.

This module does not discover or authenticate a home, read a project, certify
project-wide coverage, activate a profile, or issue a proof. Profile numbers and
home identifiers below are supplied claims, not capabilities. The dataclasses
are an in-process leaf representation, not another canonical or wire schema.
"""

from dataclasses import dataclass

METADATA_FIELDS = ("identifier", "labels", "definitions", "synonyms", "examples")
ENTITY_KINDS = ("class", "objectProperty", "dataProperty", "individual")
_HARD_BOUNDS = (256, 128, 65_536, 2_097_152)


@dataclass(frozen=True, slots=True)
class MetadataText:
    """A supplied lexical value. No RDF parser or language normalization is used."""

    text: str
    language: str | None = None
    datatype: str | None = None


@dataclass(frozen=True, slots=True)
class MetadataFields:
    """None means not supplied; an empty tuple is an explicitly empty field."""

    identifier: str | None
    labels: tuple[MetadataText, ...] | None
    definitions: tuple[MetadataText, ...] | None
    synonyms: tuple[MetadataText, ...] | None
    examples: tuple[MetadataText, ...] | None


@dataclass(frozen=True, slots=True)
class MetadataHome:
    project: str
    entity_iri: str
    entity_kind: str
    home_id: str


@dataclass(frozen=True, slots=True)
class MetadataScope:
    """Only these declared homes are checked, never an asserted complete project."""

    project: str
    homes: tuple[MetadataHome, ...]


@dataclass(frozen=True, slots=True)
class MetadataMaterial:
    home: MetadataHome
    profile: int
    fields: MetadataFields | None
    opaque: bytes | None = None


@dataclass(frozen=True, slots=True)
class MetadataBounds:
    """Local input guards, not a CostSession or an approved project/wire budget."""

    max_homes: int = _HARD_BOUNDS[0]
    max_values_per_field: int = _HARD_BOUNDS[1]
    max_scalar_bytes: int = _HARD_BOUNDS[2]
    max_total_bytes: int = _HARD_BOUNDS[3]


DEFAULT_BOUNDS = MetadataBounds()


@dataclass(frozen=True, slots=True)
class MetadataGap:
    material_index: int
    reason: str
    fields: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MetadataCheck:
    """A local check report preserving the input, with no authority/coverage flag."""

    scope: MetadataScope
    materials: tuple[MetadataMaterial, ...]
    gaps: tuple[MetadataGap, ...]
    supplied_utf8_bytes: int


class MetadataFault(ValueError):
    """A finite private reason and structural location; never includes input values."""

    def __init__(self, reason: str, location: tuple[str | int, ...]):
        self.reason = reason
        self.location = location
        super().__init__(reason, location)


def _field(value: object, name: str, location: tuple[str | int, ...]):
    try:
        return object.__getattribute__(value, name)
    except AttributeError:
        raise MetadataFault("invalid-material", (*location, name)) from None


def _exact(value: object, expected: type, location: tuple[str | int, ...]) -> None:
    if type(value) is not expected:
        raise MetadataFault("invalid-material", location)


class _InputCounter:
    def __init__(self, bounds: MetadataBounds):
        _exact(bounds, MetadataBounds, ("bounds",))
        names = ("max_homes", "max_values_per_field", "max_scalar_bytes", "max_total_bytes")
        for name, ceiling in zip(names, _HARD_BOUNDS, strict=True):
            value = _field(bounds, name, ("bounds",))
            if type(value) is not int or not 0 <= value <= ceiling:
                raise MetadataFault("invalid-bounds", ("bounds", name))
        self.bounds = bounds
        self.total = 0

    def text(self, value: object, location: tuple[str | int, ...], *, nonempty=False) -> str:
        _exact(value, str, location)
        if nonempty and not value:
            raise MetadataFault("invalid-material", location)
        # Every Unicode scalar needs at least one UTF-8 byte. Reject this lower
        # bound before scanning; never allocate a complete encoded copy.
        if len(value) > self.bounds.max_scalar_bytes:
            raise MetadataFault("resource-limit", location)
        size = 0
        for character in value:
            code = ord(character)
            if 0xD800 <= code <= 0xDFFF:
                raise MetadataFault("invalid-unicode", location)
            size += 1 if code < 0x80 else 2 if code < 0x800 else 3 if code < 0x10000 else 4
            if (
                size > self.bounds.max_scalar_bytes
                or self.total + size > self.bounds.max_total_bytes
            ):
                raise MetadataFault("resource-limit", location)
        self.total += size
        return value

    def opaque(self, value: object, location: tuple[str | int, ...]) -> None:
        _exact(value, bytes, location)
        if self.total + len(value) > self.bounds.max_total_bytes:
            raise MetadataFault("resource-limit", location)
        self.total += len(value)


def _home(home: object, counter: _InputCounter, location: tuple[str | int, ...]):
    _exact(home, MetadataHome, location)
    values = tuple(
        counter.text(_field(home, name, location), (*location, name), nonempty=True)
        for name in ("project", "entity_iri", "entity_kind", "home_id")
    )
    if values[2] not in ENTITY_KINDS:
        raise MetadataFault("unsupported-kind", (*location, "entity_kind"))
    return values


def _values(value: object, counter: _InputCounter, location: tuple[str | int, ...]) -> None:
    _exact(value, tuple, location)
    if len(value) > counter.bounds.max_values_per_field:
        raise MetadataFault("resource-limit", location)
    for index, item in enumerate(value):
        position = (*location, index)
        _exact(item, MetadataText, position)
        counter.text(_field(item, "text", position), (*position, "text"))
        language = _field(item, "language", position)
        datatype = _field(item, "datatype", position)
        if language is not None:
            counter.text(language, (*position, "language"), nonempty=True)
        if datatype is not None:
            counter.text(datatype, (*position, "datatype"), nonempty=True)
        if language is not None and datatype is not None:
            raise MetadataFault("invalid-material", position)


def check_metadata_materials(
    scope: MetadataScope,
    materials: tuple[MetadataMaterial, ...],
    *,
    bounds: MetadataBounds = DEFAULT_BOUNDS,
) -> MetadataCheck:
    """Check only the supplied finite scope and preserve every original value.

    A profile1 opaque payload is not decoded or recognized as profile2, even if
    it contains identically named fields. Gaps are L1/uninterpreted material,
    not an editable Entity. Conflicts/malformed input raise MetadataFault.
    Bounds count supplied string occurrences (including both home declarations
    and material homes) plus opaque bytes; this is not whole-chain metering.
    RDF term/IRI/datatype/BCP47 semantics, provenance, and full-project uniqueness
    require their own owners and are deliberately not certified here.
    """
    counter = _InputCounter(bounds)
    _exact(scope, MetadataScope, ("scope",))
    project = counter.text(
        _field(scope, "project", ("scope",)), ("scope", "project"), nonempty=True
    )
    homes = _field(scope, "homes", ("scope",))
    _exact(homes, tuple, ("scope", "homes"))
    _exact(materials, tuple, ("materials",))
    if len(homes) > bounds.max_homes or len(materials) > bounds.max_homes:
        raise MetadataFault("resource-limit", ("scope", "homes"))
    declared = {}
    for index, home in enumerate(homes):
        key = _home(home, counter, ("scope", "homes", index))
        if key[0] != project:
            raise MetadataFault("scope-mismatch", ("scope", "homes", index, "project"))
        if key[1] in declared:
            reason = "multiple-homes" if declared[key[1]][3] != key[3] else "duplicate-home"
            raise MetadataFault(reason, ("scope", "homes", index))
        declared[key[1]] = key
    if len(materials) != len(homes):
        raise MetadataFault("scope-mismatch", ("materials",))

    supplied = set()
    identifiers = {}
    gaps = []
    for index, material in enumerate(materials):
        position = ("materials", index)
        _exact(material, MetadataMaterial, position)
        key = _home(_field(material, "home", position), counter, (*position, "home"))
        if key[0] != project or declared.get(key[1]) != key:
            raise MetadataFault("scope-mismatch", (*position, "home"))
        if key[1] in supplied:
            raise MetadataFault("duplicate-home", (*position, "home"))
        supplied.add(key[1])
        profile = _field(material, "profile", position)
        if type(profile) is not int or profile not in (1, 2):
            raise MetadataFault("unsupported-profile", (*position, "profile"))
        fields = _field(material, "fields", position)
        opaque = _field(material, "opaque", position)
        if profile == 1:
            if fields is not None:
                raise MetadataFault("invalid-material", (*position, "fields"))
            if opaque is not None:
                counter.opaque(opaque, (*position, "opaque"))
            gaps.append(MetadataGap(index, "legacy-opaque", METADATA_FIELDS))
            continue
        if opaque is not None:
            raise MetadataFault("invalid-material", (*position, "opaque"))
        if fields is None:
            gaps.append(MetadataGap(index, "missing-metadata", METADATA_FIELDS))
            continue
        _exact(fields, MetadataFields, (*position, "fields"))
        missing = []
        identifier = _field(fields, "identifier", (*position, "fields"))
        if identifier is None:
            missing.append("identifier")
        else:
            identifier = counter.text(identifier, (*position, "fields", "identifier"))
            if not identifier:
                raise MetadataFault("empty-identifier", (*position, "fields", "identifier"))
            if identifier in identifiers:
                raise MetadataFault("identifier-conflict", (*position, "fields", "identifier"))
            identifiers[identifier] = index
        for name in METADATA_FIELDS[1:]:
            value = _field(fields, name, (*position, "fields"))
            if value is None:
                missing.append(name)
            else:
                _values(value, counter, (*position, "fields", name))
        if missing:
            gaps.append(MetadataGap(index, "missing-fields", tuple(missing)))
    return MetadataCheck(scope, materials, tuple(gaps), counter.total)
