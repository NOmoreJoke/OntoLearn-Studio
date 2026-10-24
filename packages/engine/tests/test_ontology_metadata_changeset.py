"""Real temporary JobStore3 metadata/Diff/confirmation/Job/reopen/Undo chain.

Definitions only in this source contribution: no claimed execution result.
No mocked Store, contract, worker, issuer, confirmation or public permission.
"""

import base64
import json
from copy import deepcopy
from uuid import uuid4

import pytest
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.project.entity_metadata import MetadataError
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import canonical, digest

ENTITY = "urn:equipment:Equipment"
OTHER = "urn:equipment:Other"
TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
CLASS = "http://www.w3.org/2000/01/rdf-schema#Class"
LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
COMMENT = "http://www.w3.org/2000/01/rdf-schema#comment"
IMPL = {
    "engineVersion": "0.1.0",
    "executionSemanticsVersion": "changeset-v1",
    "dependencyLockHash": "a" * 64,
}
LIMITS = {
    "startupMs": 10000,
    "handshakeMs": 5000,
    "requestMs": 5000,
    "heartbeatMs": 10000,
    "cancelGraceMs": 5000,
    "totalMs": 120000,
    "maxFrameBytes": 262144,
    "maxQueuedJobs": 32,
    "maxConcurrentJobs": 2,
    "maxPageItems": 100,
    "maxPageBytes": 131072,
    "maxWorkerMemoryBytes": 536870912,
}


def uid():
    return str(uuid4())


def metadata(*, label="设备", identifier="Equipment", synonyms=None):
    return {
        "entityMetadataVersion": 1,
        "entities": {
            ENTITY: {
                "identifier": identifier,
                "labels": [[label, "zh"], ["Equipment", "en"]],
                "definitions": [["可维护的业务设备", "zh"], ["A business asset.", "en"]],
                "synonyms": ["资产"] if synonyms is None else synonyms,
                "examples": ["泵站 A"],
            }
        },
    }


def value(*, label="设备", include_metadata=True, identifier="Equipment", synonyms=None):
    result = {
        "triples": [
            {"subject": ENTITY, "predicate": TYPE, "object": f"<{CLASS}>"},
            {"subject": ENTITY, "predicate": LABEL, "object": f"{canonical(label)}@zh"},
            {"subject": ENTITY, "predicate": LABEL, "object": '"Equipment"@en'},
            {"subject": ENTITY, "predicate": COMMENT, "object": '"可维护的业务设备"@zh'},
            {"subject": ENTITY, "predicate": COMMENT, "object": '"A business asset."@en'},
        ],
        "references": [],
        "singleValuedPredicates": [],
    }
    if include_metadata:
        result["entityMetadata"] = metadata(label=label, identifier=identifier, synonyms=synonyms)
    return result


def definition(payload, identity="Equipment"):
    return {"layer": "ontology", "id": identity, "value": payload}


class Harness:
    def __init__(self, path, *, legacy_payload=None):
        self.path = path
        self.internal = "metadata-project"
        if legacy_payload is not None:
            # Explicit old-format logical fixture, not a new writer permission.
            # These rows satisfy the old opaque payload schema; no hashes,
            # receipt or snapshot are edited after migration/acceptance.
            old = JobStore(path, contract=CONTRACT, target_format=2)
            try:
                old.create_project(self.internal)
                with old._transaction():
                    old._db.execute(
                        "INSERT INTO definitions VALUES(?,?,?,?)",
                        (self.internal, "ontology", "Equipment", canonical(legacy_payload)),
                    )
            finally:
                old.close()
            self.store = JobStore(
                path,
                contract=CONTRACT,
                target_format=3,
                backup_path=path.with_suffix(".backup.sqlite"),
            )
        else:
            self.store = JobStore(path, contract=CONTRACT, target_format=3)
            self.store.create_project(self.internal)
        self.project = self.store.public_project(self.internal)
        self.host, self.session = uid(), uid()

    def reopen(self):
        self.store.close()
        self.store = JobStore(self.path, contract=CONTRACT, target_format=3)

    def context(self):
        return {"host_client_id": self.host, "engine_session_id": self.session}

    def seed(self, payload, identity="Equipment"):
        # A real existing formal domain commit; nonempty job retains the original
        # Store branch, never an unclaimed application-marker job=None shortcut.
        return self.store.commit(
            self.internal,
            self.store.revision(self.internal),
            uid(),
            uid(),
            definitions=[definition(payload, identity)],
        )

    def payload(self, identity="Equipment"):
        return next(
            json.loads(record["payload"])
            for record in self.store.state(self.internal)["definitions"]
            if record["id"] == identity and record["layer"] == "ontology"
        )

    def preview(self, plan=None, *, target=None, base=None, hook=lambda _: None):
        base = self.store.revision(self.internal) if base is None else base
        request = {
            "projectId": self.project,
            "baseRevision": base,
            "intent": "change",
            "plan": {} if plan is None else plan,
        }
        if target is not None:
            request = {
                "projectId": self.project,
                "baseRevision": base,
                "intent": "undo",
                "targetOperationId": target,
            }
        return self.store.preview_changeset(
            self.project, base, request, **self.context(), limits=LIMITS, hook=hook
        )

    def pages(self, ready):
        cursor, segments = None, []
        while True:
            page = self.store.changeset_diff_page(
                self.project,
                ready["previewHash"],
                "diff",
                1,
                cursor,
                **self.context(),
                limits=LIMITS,
            )
            segments.extend(page["segments"])
            cursor = page["nextCursor"]
            if page["complete"]:
                break
        raw = b"".join(base64.b64decode(item["dataBase64"]) for item in segments)
        assert len(raw) == ready["manifest"]["totalBytes"]
        document = json.loads(raw)
        assert digest(document) == ready["manifest"]["documentHash"]
        return cursor, document

    def accept(self, ready):
        cursor, document = self.pages(ready)
        confirmed = self.store.confirm_changeset(
            self.project, ready["previewHash"], cursor, **self.context()
        )
        input_ = {
            "inputSnapshotId": confirmed["inputSnapshotId"],
            "scope": "asserted",
            "definitionId": "changeset",
            "parametersHash": confirmed["parametersHash"],
            "derivedResultIds": [],
            "preparedPlanRef": confirmed["preparedPlanRef"],
        }
        accepted = self.store.create_changeset_job(
            self.project,
            uid(),
            input_,
            confirmed["confirmationRef"],
            IMPL,
            LIMITS,
            **self.context(),
        )
        assert accepted["state"] == "queued"
        return accepted, confirmed, document

    def apply(self, plan=None, *, target=None):
        ready = self.preview(plan, target=target)
        assert ready["status"] == "ready", ready
        accepted, confirmed, document = self.accept(ready)
        self.store.start_job(accepted["jobId"])
        terminal = self.store.commit_job(accepted["jobId"])
        assert terminal["state"] == "succeeded", terminal
        return terminal, ready, confirmed, document

    def dump(self):
        return tuple(self.store._db.iterdump())


@pytest.fixture
def owned(tmp_path):
    instance = Harness(tmp_path / "metadata.sqlite")
    try:
        yield instance
    finally:
        instance.store.close()


def test_full_chinese_identifier_synonyms_diff_job_reopen_and_undo(owned):
    before = value()
    before["legacyOpaque"] = {"note": "不丢原文", "order": [3, 1, 2], "flag": True}
    owned.seed(before)
    baseline = owned.store.state(owned.internal)
    changed = value(
        label="运维设备", identifier="MaintainableEquipment", synonyms=["资产", "维护对象"]
    )
    expected = deepcopy(changed) | {"legacyOpaque": deepcopy(before["legacyOpaque"])}
    ready = owned.preview({"definitions": [definition(changed)]})
    assert owned.store.state(owned.internal) == baseline
    accepted, confirmed, document = owned.accept(ready)
    assert document == [
        {
            "resource": ["definition", "ontology", "Equipment"],
            "before": {"layer": "ontology", "id": "Equipment", "payload": canonical(before)},
            "after": {"layer": "ontology", "id": "Equipment", "payload": canonical(expected)},
        }
    ]
    plan = owned.store._db.execute(
        "SELECT payload FROM job_plans WHERE ref=?", (ready["preparedPlanRef"],)
    ).fetchone()[0]
    assert json.loads(plan)["preview"]["plan"]["definitions"][0]["value"] == expected
    owned.store.start_job(accepted["jobId"])
    terminal = owned.store.commit_job(accepted["jobId"])
    assert terminal["state"] == "succeeded" and terminal["resultRef"] is not None
    assert owned.store.revision(owned.internal) == 2
    assert owned.store.vector(owned.internal)["ontology:Equipment"] == 2
    marker = owned.store.operation_get(owned.project, terminal["operationId"])
    assert marker["jobId"] == terminal["jobId"]
    owned.reopen()
    assert owned.payload() == expected
    # Actual accepted Job replay returns its original immutable terminal record.
    assert (
        owned.store.create_changeset_job(
            owned.project,
            terminal["operationId"],
            terminal["input"],
            confirmed["confirmationRef"],
            IMPL,
            LIMITS,
            **owned.context(),
        )
        == terminal
    )
    undone, _, _, undo_document = owned.apply(target=terminal["operationId"])
    assert undone["state"] == "succeeded"
    assert undo_document[0]["before"]["payload"] == canonical(expected)
    assert undo_document[0]["after"]["payload"] == canonical(before)
    owned.reopen()
    assert owned.payload() == before
    assert owned.store.revision(owned.internal) == 3
    assert owned.store.vector(owned.internal)["ontology:Equipment"] == 3
    assert owned.store.operation_get(owned.project, terminal["operationId"]) == marker


def test_first_metadata_on_legacy_and_undo_restores_absent_namespace(owned):
    legacy = value(include_metadata=False)
    legacy["opaque"] = {"retained": [False, 0, "0"]}
    original_marker = owned.seed(legacy)
    terminal, _, _, _ = owned.apply({"definitions": [definition(value())]})
    owned.reopen()
    assert owned.payload()["entityMetadata"] == metadata()
    owned.apply(target=terminal["operationId"])
    owned.reopen()
    assert owned.payload() == legacy and "entityMetadata" not in owned.payload()
    assert owned.store.load_snapshot(original_marker["after_snapshot"])["state"]["definitions"][0][
        "payload"
    ] == canonical(legacy)


def test_metadata_only_real_revision_and_omitted_metadata_preserved(owned):
    initial = value()
    owned.seed(initial)
    changed = deepcopy(initial)
    changed["entityMetadata"]["entities"][ENTITY]["examples"].append("备用泵 B")
    terminal, _, _, document = owned.apply({"definitions": [definition(changed)]})
    assert document[0]["before"]["payload"] != document[0]["after"]["payload"]
    assert owned.payload()["triples"] == initial["triples"]
    assert owned.store.revision(owned.internal) == 2
    assert owned.store.vector(owned.internal)["ontology:Equipment"] == 2
    omitted = value(include_metadata=False)
    owned.apply({"definitions": [definition(omitted)]})
    assert owned.payload()["entityMetadata"] == changed["entityMetadata"]
    assert owned.store.get_job(owned.project, terminal["jobId"])["state"] == "succeeded"


@pytest.mark.parametrize(
    "field,replacement",
    [
        ("identifier", "Equipment.invalid"),
        ("identifier", ""),
        ("labels", [["设备", "zh"], ["设备", "zh"]]),
        ("labels", [["设备", "zh-CN"]]),
        ("labels", [["\u3000", "zh"]]),
        ("synonyms", ["资产", "资产"]),
        ("examples", ["a" * 16001]),
        ("examples", ["\ud800"]),
    ],
)
def test_invalid_metadata_preview_has_zero_database_effect(owned, field, replacement):
    owned.seed(value())
    changed = value()
    changed["entityMetadata"]["entities"][ENTITY][field] = replacement
    before = owned.dump()
    with pytest.raises(ValueError):
        owned.preview({"definitions": [definition(changed)]})
    assert owned.dump() == before


@pytest.mark.parametrize("replacement", [True, 2])
def test_version_exact_and_namespace_unknown_keys_rejected(owned, replacement):
    changed = value()
    changed["entityMetadata"]["entityMetadataVersion"] = replacement
    before = owned.dump()
    with pytest.raises(ValueError):
        owned.preview({"definitions": [definition(changed)]})
    assert owned.dump() == before


def test_rdf_mismatch_duplicate_home_and_extra_support_rejected(owned):
    owned.seed(value())
    mismatch = value()
    mismatch["entityMetadata"]["entities"][ENTITY]["labels"][0][0] = "另一名字"
    for plan in (
        {"definitions": [definition(mismatch)]},
        {"definitions": [definition(value(), "OtherHome")]},
        {
            "manual": [
                {
                    "id": digest([ENTITY, LABEL, '"额外支持"@zh']),
                    "subject": ENTITY,
                    "predicate": LABEL,
                    "object": '"额外支持"@zh',
                }
            ]
        },
    ):
        before = owned.dump()
        with pytest.raises(ValueError):
            owned.preview(plan)
        assert owned.dump() == before


def test_actual_all_source_duplicate_support_kept_not_erased(owned):
    original = value()
    # Existing independent support for an already declared RDF value.
    fact = {"subject": ENTITY, "predicate": LABEL, "object": '"设备"@zh'}
    fact["id"] = digest([fact["subject"], fact["predicate"], fact["object"]])
    owned.seed(original)
    owned.store.commit(owned.internal, 1, uid(), uid(), manual=[fact])
    support = owned.store.state(owned.internal)["facts"]
    changed = value(identifier="Equipment2", synonyms=["资产", "对象"])
    owned.apply({"definitions": [definition(changed)]})
    owned.reopen()
    assert owned.store.state(owned.internal)["facts"] == support
    # Editing only the definition label cannot erase independent support.
    before = owned.dump()
    with pytest.raises(ValueError):
        owned.preview({"definitions": [definition(value(label="新名字"))]})
    assert owned.dump() == before


@pytest.mark.parametrize(
    "opaque",
    [
        "legacy-note",
        {"entityMetadataVersion": True, "entities": {}},
        metadata(label="与历史 RDF 不一致的旧名字"),
    ],
)
def test_legacy_namespace_collision_reopens_and_refuses_overwrite(tmp_path, opaque):
    original = value(include_metadata=False)
    original["entityMetadata"] = opaque
    owned = Harness(tmp_path / "legacy.sqlite", legacy_payload=original)
    try:
        snapshot = owned.store.snapshot(owned.internal)
        old_snapshot = owned.store.load_snapshot(snapshot)
        owned.reopen()
        assert owned.payload() == original
        assert owned.store.load_snapshot(snapshot) == old_snapshot
        before = owned.dump()
        with pytest.raises(ValueError):
            owned.preview({"definitions": [definition(value())]})
        assert owned.dump() == before
        # An unrelated supported edit preserves the original opaque collision.
        known = value(include_metadata=False)
        known["references"] = []
        known["triples"].append(
            {"subject": "urn:unrelated", "predicate": "urn:legacy", "object": '"kept"'}
        )
        edited, _, _, _ = owned.apply({"definitions": [definition(known)]})
        assert owned.payload()["entityMetadata"] == opaque
        owned.apply(target=edited["operationId"])
        owned.reopen()
        assert owned.payload() == original
        assert owned.store.load_snapshot(snapshot) == old_snapshot
    finally:
        owned.store.close()


def test_arbitrary_opaque_public_injection_rejected_and_inheritance_exact(owned):
    original = value()
    original["opaque"] = {"x": True, "order": [3, 1, 2]}
    owned.seed(original)
    changed = value(identifier="Equipment2")
    changed["opaque"] = {"x": 1, "order": [3, 1, 2]}
    before = owned.dump()
    with pytest.raises(ValueError):
        owned.preview({"definitions": [definition(changed)]})
    assert owned.dump() == before
    changed.pop("opaque")
    owned.apply({"definitions": [definition(changed)]})
    assert owned.payload()["opaque"] == original["opaque"]
    assert type(owned.payload()["opaque"]["x"]) is bool


def test_store_ordinary_writer_cannot_drop_metadata_or_leave_references(owned):
    owned.seed(value())
    for plan in (
        {"definitions": [definition(value(include_metadata=False))]},
        {
            "remove_definitions": [{"layer": "ontology", "id": "Equipment"}],
            "manual": [
                {
                    "id": digest(["urn:other", "urn:ref", f"<{ENTITY}>"]),
                    "subject": "urn:other",
                    "predicate": "urn:ref",
                    "object": f"<{ENTITY}>",
                }
            ],
        },
    ):
        before = owned.dump()
        with pytest.raises(MetadataError):
            owned.store.commit(owned.internal, 1, uid(), uid(), **plan)
        assert owned.dump() == before


def test_explicit_delete_and_copy_keep_complete_metadata_and_undo(owned):
    original = value()
    owned.seed(original)
    copied = deepcopy(original)
    copied["triples"] = [dict(triple, subject=OTHER) for triple in copied["triples"]]
    copied["entityMetadata"]["entities"] = {
        OTHER: deepcopy(original["entityMetadata"]["entities"][ENTITY])
    }
    # Same identifier for another IRI is explicitly supported by actual T02 M.
    copied_job, _, _, _ = owned.apply({"definitions": [definition(copied, "Other")]})
    assert (
        owned.payload("Other")["entityMetadata"]["entities"][OTHER]
        == original["entityMetadata"]["entities"][ENTITY]
    )
    owned.apply(target=copied_job["operationId"])
    deleted, _, _, _ = owned.apply(
        {"remove_definitions": [{"layer": "ontology", "id": "Equipment"}]}
    )
    assert owned.store.state(owned.internal)["definitions"] == []
    owned.apply(target=deleted["operationId"])
    owned.reopen()
    assert owned.payload() == original


def test_fault_after_actual_write_rolls_back_full_database_and_reopen(owned):
    owned.seed(value())
    ready = owned.preview({"definitions": [definition(value(identifier="Equipment2"))]})
    accepted, _, _ = owned.accept(ready)
    owned.store.start_job(accepted["jobId"])
    before = owned.dump()

    def fault(stage):
        if stage == "mid_marker":
            raise RuntimeError("owned-injected-fault")

    with pytest.raises(RuntimeError, match="owned-injected-fault"):
        owned.store.commit_job(accepted["jobId"], hook=fault)
    assert owned.dump() == before
    owned.reopen()
    assert owned.payload() == value()
    assert owned.store.get_job(owned.project, accepted["jobId"])["state"] == "running"
    assert owned.store.operation_get(owned.project, accepted["operationId"]) is None


def test_stale_confirmation_and_later_edit_undo_conflict(owned):
    owned.seed(value())
    ready = owned.preview({"definitions": [definition(value(identifier="Equipment2"))]})
    cursor, _ = owned.pages(ready)
    changed = deepcopy(value())
    changed["entityMetadata"]["entities"][ENTITY]["examples"].append("第二示例")
    owned.apply({"definitions": [definition(changed)]})
    before = owned.dump()
    with pytest.raises(JobFault, match="REVISION_CONFLICT"):
        owned.store.confirm_changeset(
            owned.project, ready["previewHash"], cursor, **owned.context()
        )
    assert owned.dump() == before
    first, _, _, _ = owned.apply({"definitions": [definition(value(identifier="Equipment2"))]})
    owned.apply({"definitions": [definition(value(identifier="Equipment3"))]})
    conflict = owned.preview(target=first["operationId"])
    assert conflict["status"] == "conflict"
    assert owned.payload()["entityMetadata"]["entities"][ENTITY]["identifier"] == "Equipment3"


def test_first_metadata_undo_of_undo_preserves_old_receipts_and_snapshot_hashes(owned):
    legacy = value(include_metadata=False)
    legacy["oldOpaque"] = {"order": [2, 1], "bool": False}
    seeded = owned.seed(legacy)
    frozen_snapshots = dict(owned.store._db.execute("SELECT id,payload FROM snapshots"))
    frozen_receipts = {
        tuple(row[:2]): row[2]
        for row in owned.store._db.execute("SELECT project,operation,payload FROM app_receipts")
    }
    original_snapshot = owned.store.load_snapshot(seeded["after_snapshot"])
    added, _, _, _ = owned.apply({"definitions": [definition(value())]})
    expected = owned.payload()
    undone, _, _, _ = owned.apply(target=added["operationId"])
    owned.reopen()
    assert owned.payload() == legacy
    redone, _, _, _ = owned.apply(target=undone["operationId"])
    owned.reopen()
    assert redone["state"] == "succeeded" and owned.payload() == expected
    assert owned.store.revision(owned.internal) == 4
    assert owned.store.vector(owned.internal)["ontology:Equipment"] == 4
    assert owned.store.load_snapshot(seeded["after_snapshot"]) == original_snapshot
    assert digest(original_snapshot) == seeded["after_snapshot"]
    for identity, payload in frozen_snapshots.items():
        assert (
            owned.store._db.execute(
                "SELECT payload FROM snapshots WHERE id=?", (identity,)
            ).fetchone()[0]
            == payload
        )
    for identity, payload in frozen_receipts.items():
        assert (
            owned.store._db.execute(
                "SELECT payload FROM app_receipts WHERE project=? AND operation=?", identity
            ).fetchone()[0]
            == payload
        )


@pytest.mark.parametrize("reverse", [False, True])
def test_atomic_home_move_uses_complete_final_state_and_undo(owned, reverse):
    original = value()
    owned.seed(original)
    former = deepcopy(original)
    former["entityMetadata"]["entities"] = {}
    destination = {
        "triples": [],
        "references": [],
        "singleValuedPredicates": [],
        "entityMetadata": metadata(),
    }
    definitions = [definition(former), definition(destination, "MetadataHome")]
    if reverse:
        definitions.reverse()
    moved, _, _, document = owned.apply({"definitions": definitions})
    assert len(document) == 2
    owned.reopen()
    assert owned.payload()["triples"] == original["triples"]
    assert owned.payload()["entityMetadata"]["entities"] == {}
    assert owned.payload("MetadataHome")["entityMetadata"] == metadata()
    assert owned.store.vector(owned.internal)["ontology:Equipment"] == 2
    assert owned.store.vector(owned.internal)["ontology:MetadataHome"] == 1
    owned.apply(target=moved["operationId"])
    owned.reopen()
    assert owned.payload() == original
    assert [record["id"] for record in owned.store.state(owned.internal)["definitions"]] == [
        "Equipment"
    ]


def test_frozen_effective_plan_not_remerged_at_confirm_or_job(monkeypatch, owned):
    from ontolearn_engine.project import domain_changesets

    original = value()
    original["legacyOpaque"] = {"unchanged": [1, True, "一"]}
    owned.seed(original)
    ready = owned.preview({"definitions": [definition(value(identifier="Equipment2"))]})
    raw = owned.store._db.execute(
        "SELECT payload FROM job_plans WHERE ref=?", (ready["preparedPlanRef"],)
    ).fetchone()[0]

    def forbidden_merge(*_args, **_kwargs):
        raise AssertionError("merge is admission-only, never confirm/Job/reopen")

    # A narrow call-observer: the actual confirmation, Job and Store remain real.
    monkeypatch.setattr(domain_changesets, "merge_plan", forbidden_merge)
    accepted, _, _ = owned.accept(ready)
    owned.store.start_job(accepted["jobId"])
    terminal = owned.store.commit_job(accepted["jobId"])
    assert terminal["state"] == "succeeded"
    owned.reopen()
    assert (
        owned.store._db.execute(
            "SELECT payload FROM job_plans WHERE ref=?", (ready["preparedPlanRef"],)
        ).fetchone()[0]
        == raw
    )
    assert owned.payload()["legacyOpaque"] == original["legacyOpaque"]


def test_opaque_change_after_acceptance_fences_frozen_job_without_remerge(owned):
    original = value()
    original["opaque"] = {"value": 1}
    owned.seed(original)
    ready = owned.preview({"definitions": [definition(value(identifier="Equipment2"))]})
    accepted, _, _ = owned.accept(ready)
    frozen = owned.store._db.execute(
        "SELECT payload FROM job_plans WHERE ref=?", (ready["preparedPlanRef"],)
    ).fetchone()[0]
    later = deepcopy(original)
    later["opaque"]["value"] = 2
    owned.seed(later)
    owned.store.start_job(accepted["jobId"])
    before = owned.dump()
    with pytest.raises(ValueError):
        owned.store.commit_job(accepted["jobId"])
    assert owned.dump() == before
    assert owned.payload() == later
    assert (
        owned.store._db.execute(
            "SELECT payload FROM job_plans WHERE ref=?", (ready["preparedPlanRef"],)
        ).fetchone()[0]
        == frozen
    )
    assert owned.store.operation_get(owned.project, accepted["operationId"]) is None


def test_later_metadata_aba_rejects_undo_even_when_current_payload_equals_target(owned):
    owned.seed(value())
    changed = value(identifier="Equipment2")
    first, _, _, _ = owned.apply({"definitions": [definition(changed)]})
    owned.apply({"definitions": [definition(value(identifier="Equipment3"))]})
    owned.apply({"definitions": [definition(changed)]})
    state = owned.store.state(owned.internal)
    counts = {
        table: owned.store._db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        for table in ("commits", "jobs", "app_receipts")
    }
    rejected = owned.preview(target=first["operationId"])
    assert rejected["status"] == "conflict"
    assert owned.store.state(owned.internal) == state
    assert counts == {
        table: owned.store._db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        for table in counts
    }
