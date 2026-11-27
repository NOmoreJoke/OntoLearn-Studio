"""Pure mapping preview. Trusted T01 owns all confirmation and Store.commit calls."""

import json
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import quote

from rdflib import RDF, XSD, Literal

from ontolearn_engine.mapping.source import Issue, Table
from ontolearn_engine.rdf_snapshot import iri, term
from ontolearn_engine.storage import digest


@dataclass(frozen=True)
class Conversion:
    kind: str = "string"
    trim: bool = False
    empty: str = "omit"  # omit, error or literal (string only)
    true_values: tuple[str, ...] = ("true", "1")
    false_values: tuple[str, ...] = ("false", "0")


@dataclass(frozen=True)
class Binding:
    column: str
    predicate: str
    conversion: Conversion = Conversion()
    reference_namespace: str | None = None
    reference_columns: tuple[str, ...] = ()


@dataclass(frozen=True)
class Mapping:
    identity: str
    version: int
    namespace: str
    class_iri: str
    keys: tuple[str, ...]
    bindings: tuple[Binding, ...]


@dataclass(frozen=True)
class Conflict:
    code: str
    subject: str
    predicate: str
    current: str | None
    source: str | None
    managed: str | None
    owner: str | None
    source_row: str | None


@dataclass(frozen=True)
class Preview:
    project: str
    base_revision: int
    snapshot_hash: str
    source_hash: str
    definition_hash: str
    mapping: Mapping
    rows_json: str
    issues: tuple[Issue, ...]
    conflicts: tuple[Conflict, ...]
    added: tuple[tuple[str, str, str], ...]
    removed: tuple[tuple[str, str, str], ...]
    unchanged: tuple[tuple[str, str, str], ...]
    modified: tuple[dict, ...]
    identities_added: tuple[str, ...]
    identities_removed: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return not self.issues and not self.conflicts

    def rows(self) -> list[dict]:
        return json.loads(self.rows_json)


class PreviewRejected(ValueError):
    pass


def entity(namespace: str, keys: tuple[str, ...]) -> str:
    iri(namespace)
    if not namespace.endswith("/") or not keys or any(not key.strip() for key in keys):
        raise ValueError("Namespace ending in / and nonempty string keys required")
    for key in keys:
        key.encode("utf-8", errors="strict")
    # '@' is escaped for a single key, so composite identities cannot collide with it.
    segment = (
        quote(keys[0], safe="")
        if len(keys) == 1
        else "@" + quote(json.dumps(keys, ensure_ascii=False, separators=(",", ":")), safe="")
    )
    return str(iri(namespace + segment))


def _validate(mapping: Mapping, table: Table) -> None:
    if (
        not re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", mapping.identity)
        or type(mapping.version) is not int
        or mapping.version < 1
    ):
        raise ValueError("Versioned mapping identity required")
    entity(mapping.namespace, ("probe",))
    iri(mapping.class_iri)
    if not mapping.keys or len(set(mapping.keys)) != len(mapping.keys):
        raise ValueError("Unique business keys required")
    required = set(mapping.keys)
    targets = set()
    for binding in mapping.bindings:
        iri(binding.predicate)
        required.add(binding.column)
        if binding.predicate in targets or binding.predicate == str(RDF.type):
            raise ValueError("Each property can be mapped once; class mapping supplies rdf:type")
        targets.add(binding.predicate)
        conversion = binding.conversion
        if conversion.kind not in {"string", "integer", "decimal", "boolean", "date", "datetime"}:
            raise ValueError("Unsupported conversion")
        if conversion.empty not in {"omit", "error", "literal"} or (
            conversion.empty == "literal" and conversion.kind != "string"
        ):
            raise ValueError("Invalid empty-value policy")
        if set(conversion.true_values) & set(conversion.false_values):
            raise ValueError("Boolean vocabularies must be disjoint")
        if binding.reference_namespace is not None:
            entity(binding.reference_namespace, ("probe",))
            if not binding.reference_columns or len(set(binding.reference_columns)) != len(
                binding.reference_columns
            ):
                raise ValueError("Reference uses the target's exact business keys")
            required.update(binding.reference_columns)
        elif binding.reference_columns:
            raise ValueError("Reference namespace required")
    if not required <= set(table.fields):
        raise ValueError("Selected column not found")


def convert(raw: str, rule: Conversion) -> str | None:
    value = raw.strip() if rule.trim else raw
    if value == "":
        if rule.empty == "omit":
            return None
        if rule.empty == "error":
            raise ValueError("Empty value")
    kind = rule.kind
    if kind == "string":
        obj = Literal(value)
    elif kind == "integer":
        if not re.fullmatch(r"[+-]?[0-9]+", value):
            raise ValueError("Invalid integer")
        obj = Literal(int(value), datatype=XSD.integer)
    elif kind == "decimal":
        if not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)", value):
            raise ValueError("Invalid decimal")
        try:
            number = Decimal(value)
        except InvalidOperation as error:
            raise ValueError("Invalid decimal") from error
        obj = Literal(number, datatype=XSD.decimal)
    elif kind == "boolean":
        if value not in rule.true_values + rule.false_values:
            raise ValueError("Invalid boolean")
        obj = Literal(value in rule.true_values, datatype=XSD.boolean)
    elif kind == "date":
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            raise ValueError("ISO date required")
        obj = Literal(date.fromisoformat(value), datatype=XSD.date)
    elif kind == "datetime":
        if "T" not in value:
            raise ValueError("ISO datetime required")
        obj = Literal(datetime.fromisoformat(value), datatype=XSD.dateTime)
    else:
        raise ValueError("Unsupported conversion")
    return term(obj.n3()).n3()


def suggest(table: Table, candidates: dict[str, str]) -> tuple[dict, ...]:
    """Offline exact-name hints with actual sample evidence. Never applies a change."""
    return tuple(
        {
            "column": field,
            "predicate": candidates[field],
            "basis": "exact-field-name",
            "samples": [row.cells[i].text for row in table.rows[:3]],
        }
        for i, field in enumerate(table.fields)
        if field in candidates
    )


def preview(mapping: Mapping, table: Table, snapshot: dict) -> Preview:
    _validate(mapping, table)
    if (
        not isinstance(snapshot.get("project"), str)
        or not snapshot["project"]
        or type(snapshot.get("projectRevision")) is not int
        or snapshot["projectRevision"] < 0
    ):
        raise ValueError("Trusted project snapshot required")
    state = snapshot["state"]
    existing = state["facts"]
    single = set()
    for definition in state["definitions"]:
        if definition["layer"] == "ontology":
            value = json.loads(definition["payload"])
            if isinstance(value, dict):
                single.update(value.get("singleValuedPredicates", []))
    issues = []
    rows = []
    seen = {}
    for row in table.rows:
        values = dict(zip(table.fields, (cell.text for cell in row.cells), strict=True))
        keys = tuple(values[field] for field in mapping.keys)
        empty = [field for field in mapping.keys if not values[field].strip()]
        if empty:
            issues.extend(
                Issue("EMPTY_KEY", table.sheet, row.number, table.fields.index(field) + 1, field)
                for field in empty
            )
            continue
        if keys in seen:
            for number in (seen[keys], row.number):
                for field in mapping.keys:
                    issue = Issue(
                        "DUPLICATE_KEY", table.sheet, number, table.fields.index(field) + 1, field
                    )
                    if issue not in issues:
                        issues.append(issue)
            continue
        seen[keys] = row.number
        subject = entity(mapping.namespace, keys)
        triples = [(subject, str(RDF.type), f"<{mapping.class_iri}>")]
        for binding in mapping.bindings:
            try:
                if binding.reference_namespace is not None:
                    ref_keys = tuple(values[field] for field in binding.reference_columns)
                    if all(not value.strip() for value in ref_keys) and (
                        binding.conversion.empty == "omit"
                    ):
                        continue
                    bad_fields = [
                        field for field in binding.reference_columns if not values[field].strip()
                    ]
                    if bad_fields:
                        issues.extend(
                            Issue(
                                "EMPTY_REFERENCE_KEY",
                                table.sheet,
                                row.number,
                                table.fields.index(field) + 1,
                                field,
                            )
                            for field in bad_fields
                        )
                        continue
                    obj = f"<{entity(binding.reference_namespace, ref_keys)}>"
                else:
                    obj = convert(values[binding.column], binding.conversion)
                if obj is not None:
                    triples.append((subject, binding.predicate, obj))
            except (ValueError, UnicodeError):
                issues.append(
                    Issue(
                        "CONVERSION_FAILED",
                        table.sheet,
                        row.number,
                        table.fields.index(binding.column) + 1,
                        binding.column,
                    )
                )
        rows.append(
            {
                "row": json.dumps(
                    {"sheet": table.sheet, "row": row.number},
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                "facts": [
                    {"id": digest(list(t)), "subject": t[0], "predicate": t[1], "object": t[2]}
                    for t in triples
                ],
            }
        )
    conflicts = []
    owned = [fact for fact in existing if fact["owner"] == mapping.identity]
    proposed = [fact for row in rows for fact in row["facts"]]
    slots = {}
    for fact in proposed:
        slots.setdefault((fact["subject"], fact["predicate"]), []).append(fact)
    for fact in owned:
        if fact["object"] != fact["managed_value"]:
            source_values = slots.get((fact["subject"], fact["predicate"]), [])
            conflicts.append(
                Conflict(
                    "MANUAL_DRIFT",
                    fact["subject"],
                    fact["predicate"],
                    fact["object"],
                    source_values[0]["object"] if source_values else None,
                    fact["managed_value"],
                    fact["owner"],
                    fact["source_row"],
                )
            )
    for fact in existing:
        if fact["owner"] == mapping.identity:
            continue
        for candidate in slots.get((fact["subject"], fact["predicate"]), []):
            if candidate["id"] == fact["id"] or (
                fact["object"] is not None
                and (fact["object"] == candidate["object"] or fact["predicate"] in single)
            ):
                conflicts.append(
                    Conflict(
                        "OWNERSHIP_CONFLICT",
                        fact["subject"],
                        fact["predicate"],
                        fact["object"],
                        candidate["object"],
                        fact["managed_value"],
                        fact["owner"],
                        fact["source_row"],
                    )
                )
    before = {(f["subject"], f["predicate"], f["object"]) for f in owned if f["object"] is not None}
    after = {(f["subject"], f["predicate"], f["object"]) for f in proposed}
    removed, added = before - after, after - before
    modified = []
    for subject, predicate in sorted({t[:2] for t in removed} & {t[:2] for t in added}):
        modified.append(
            {
                "subject": subject,
                "predicate": predicate,
                "before": sorted(t[2] for t in removed if t[:2] == (subject, predicate)),
                "after": sorted(t[2] for t in added if t[:2] == (subject, predicate)),
            }
        )
    return Preview(
        snapshot["project"],
        snapshot["projectRevision"],
        digest(snapshot),
        table.source_hash,
        digest(asdict(mapping)),
        mapping,
        json.dumps(rows, ensure_ascii=False, sort_keys=True),
        tuple(issues),
        tuple(conflicts),
        tuple(sorted(added)),
        tuple(sorted(removed)),
        tuple(sorted(before & after)),
        tuple(modified),
        tuple(sorted({t[0] for t in after} - {t[0] for t in before})),
        tuple(sorted({t[0] for t in before} - {t[0] for t in after})),
    )


def checked_plan(old: Preview, mapping: Mapping, table: Table, snapshot: dict) -> dict:
    """Recompute against trusted current inputs; return T01's existing Store plan shape.

    Caller must still atomically check base revision inside Store.commit, perform
    explicit user confirmation, operation/job reconciliation and cancellation.
    Never accept renderer-owned Preview instances as trusted evidence.
    """
    fresh = preview(mapping, table, snapshot)
    if old != fresh:
        raise PreviewRejected("STALE_PREVIEW")
    if not fresh.ready:
        raise PreviewRejected("MAPPING_BLOCKED")
    return {
        "base": fresh.base_revision,
        "mapping": {"id": mapping.identity, "rows": fresh.rows()},
        "definitions": [
            {
                "layer": "mapping",
                "id": mapping.identity,
                "value": {
                    "version": mapping.version,
                    "definition": asdict(mapping),
                    "sourceHash": table.source_hash,
                    "sheet": table.sheet,
                },
            }
        ],
    }
