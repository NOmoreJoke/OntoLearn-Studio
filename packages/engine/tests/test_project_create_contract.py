"""Real internal Store create mechanics, never host permission or resolution."""

import json
import sqlite3
import subprocess
import sys
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from uuid import UUID

import pytest
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.project import format3, project_lifecycle
from ontolearn_engine.project.project_host import ProjectHostReader, ReadLimits
from ontolearn_engine.project.project_lifecycle import CreationFault
from ontolearn_engine.storage import Store, canonical, digest
from test_job_store import CONTRACT, create, uid
from test_project_host_read_services import corrupt_immutable, logical_dump, zero_write

ROOT = Path(__file__).resolve().parents[3]
PHASES = [
    "before",
    "create_preflight",
    "create_project",
    "create_app_project",
    "create_domain_snapshot",
    "create_genesis_checkpoint",
    "create_genesis_head",
    "create_origin",
    "create_genesis_verified",
    "create_public",
    "create_claim",
    "create_metadata",
    "create_after_checkpoint",
    "create_operation",
    "create_receipt",
    "create_head",
    "create_validated",
    "before_commit",
    "after_commit",
]


@pytest.fixture
def store(tmp_path):
    s = JobStore(tmp_path / "create.sqlite", contract=CONTRACT, target_format=3)
    yield s
    s.close()


def intent(name="新项目", *, operation=None, origin=None, limits=None):
    return {
        "projectCreateCoreVersion": 1,
        "request": {
            "requestVersion": 1,
            "operationId": operation or uid(),
            "initialization": {"kind": "blank"},
            "name": name,
        },
        "origin": origin
        or {"hostClientId": uid(), "engineSessionId": uid(), "permission": "library.create"},
        "readerLimits": limits if limits is not None else ReadLimits(),
    }


def run(s, value, **kwargs):
    return s.commit(None, None, value["request"]["operationId"], None, creation=value, **kwargs)


def fault(reason, call):
    with pytest.raises(CreationFault) as raised:
        call()
    assert raised.value.reason == str(raised.value) == reason


def test_actual_atomic_genesis_uuid_context_receipt_and_reader(store):
    request = intent('  原名\\"\n保留  ')
    before_counts, before_bytes = project_lifecycle._totals(store._db)
    trace, phases = [], []
    store._db.set_trace_callback(trace.append)
    result = run(store, request, hook=phases.append)
    store._db.set_trace_callback(None)
    assert phases == PHASES
    assert trace.count("BEGIN IMMEDIATE") == trace.count("COMMIT") == 1
    assert not any("INSERT OR IGNORE" in sql for sql in trace)
    assert not store._db.in_transaction
    project, operation = result["projectId"], request["request"]["operationId"]
    assert str(UUID(project)) == project and UUID(project).version == 4
    assert set(result) == {
        "createResultVersion",
        "operationId",
        "projectId",
        "requestHash",
        "receipt",
    }
    assert result["operationId"] == operation and result["requestHash"] == digest(
        request["request"]
    )
    context = project_lifecycle.creation_context(store, project, operation)
    assert context["result"] == result
    assert project_lifecycle._actual_rows(store, context) == context["rows"]
    counts, total = project_lifecycle._totals(store._db)
    assert sum(counts.values()) - sum(before_counts.values()) == 10
    assert total - before_bytes == sum(
        project_lifecycle._row_size(store._db, r) for rows in context["rows"].values() for r in rows
    )
    for table in ("jobs", "commits", "app_drafts", "app_learning", "app_assistance"):
        assert store._db.execute(f"SELECT count(*) FROM {table}").fetchone()[0] == 0
    assert store._db.execute("SELECT public,internal FROM public_projects").fetchone()[:] == (
        project,
        project,
    )
    claim = store._db.execute("SELECT * FROM operation_claims").fetchone()
    assert claim["kind"] == "application" and claim["job"] is None
    assert claim["fingerprint"] == digest(json.loads(claim["context"]))
    assert (
        store.project_checkpoint(project, result["receipt"]["beforeCheckpointRef"])["application"][
            "metadata"
        ]["name"]
        is None
    )
    with zero_write(store):
        reader = ProjectHostReader(store)
        catalog = reader.catalog_start()
        workspace = reader.workspace(project, editor="\x01" * 512)
    assert catalog["total"] == 1 and catalog["items"][0]["projectId"] == project
    assert workspace["metadata"]["name"] == request["request"]["name"]
    assert (
        workspace["domainRevision"] == 0
        and workspace["metadataVersion"] == workspace["operationSequence"] == 1
    )
    assert workspace["draft"] == {"state": "missing", "editor": "\x01" * 512}
    assert workspace["inputSnapshotId"] == result["receipt"]["inputSnapshotId"]
    assert workspace["checkpointRef"] == result["receipt"]["afterCheckpointRef"]


def test_same_name_distinct_projects_retry_after_metadata_and_domain_reopen(store):
    first = intent("同名")
    created = run(store, first)
    second = run(store, intent("同名"))
    assert created["projectId"] != second["projectId"]
    project = created["projectId"]
    store.apply_application(
        project,
        uid(),
        {"type": "metadata", "expectedVersion": 1, "patch": {"name": "later"}},
        actor=uid(),
        permission="write",
    )
    store.commit(
        project,
        0,
        uid(),
        "domain-job",
        definitions=[{"layer": "rule", "id": "r", "value": {"enabled": True}}],
    )
    before = logical_dump(store)
    assert run(store, first) == created and logical_dump(store) == before
    tightened = dict(first, readerLimits=replace(ReadLimits(), projects=1, metadata_bytes=1))
    assert run(store, tightened) == created and logical_dump(store) == before
    path = store.path
    store.close()
    reopened = JobStore(path, contract=CONTRACT, target_format=3)
    try:
        assert run(reopened, first) == created
        assert (
            reopened.project_receipt(project, first["request"]["operationId"]) == created["receipt"]
        )
    finally:
        reopened.close()


@pytest.mark.parametrize("phase", PHASES)
def test_exception_at_each_persistent_boundary_is_rollback_or_committed(store, phase):
    value = intent()
    before = logical_dump(store)

    def fail(point):
        if point == phase:
            raise RuntimeError("synthetic failure")

    with pytest.raises(RuntimeError, match="synthetic failure"):
        run(store, value, hook=fail)
    assert not store._db.in_transaction
    if phase == "after_commit":
        assert logical_dump(store) != before
        result = run(store, value)
        assert (
            ProjectHostReader(store).catalog_start()["items"][0]["projectId"] == result["projectId"]
        )
    else:
        assert logical_dump(store) == before
        assert store._db.execute("SELECT count(*) FROM projects").fetchone()[0] == 0


CHILD = r"""
import importlib.util,json,os,sys
from pathlib import Path
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project.project_host import ReadLimits
spec=importlib.util.spec_from_file_location('c',Path(sys.argv[1])/'packages/contracts/python/contract_v2.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
s=JobStore(sys.argv[2],contract=c,target_format=3)
value=json.loads(sys.argv[3]);value['readerLimits']=ReadLimits()
def hook(phase):
 if phase==sys.argv[4]:os._exit(77)
s.commit(None,None,value['request']['operationId'],None,creation=value,hook=hook)
raise SystemExit(90)
"""


@pytest.mark.parametrize("phase", PHASES)
def test_actual_child_exit_each_boundary_and_reopen(tmp_path, phase):
    path = tmp_path / "exit.sqlite"
    s = JobStore(path, contract=CONTRACT, target_format=3)
    before = logical_dump(s)
    s.close()
    value = intent()
    child_value = {k: v for k, v in value.items() if k != "readerLimits"}
    child = subprocess.run(
        [sys.executable, "-c", CHILD, str(ROOT), str(path), json.dumps(child_value), phase],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert child.returncode == 77, (child.returncode, child.stdout, child.stderr)
    reopened = JobStore(path, contract=CONTRACT, target_format=3)
    try:
        if phase == "after_commit":
            recovered = run(reopened, value)
            assert recovered["receipt"] == reopened.project_receipt(
                recovered["projectId"], value["request"]["operationId"]
            )
            assert ProjectHostReader(reopened).catalog_start()["total"] == 1
        else:
            assert logical_dump(reopened) == before
            assert reopened._db.execute("SELECT count(*) FROM projects").fetchone()[0] == 0
    finally:
        reopened.close()


@pytest.mark.parametrize(
    "table",
    [
        "projects",
        "snapshots",
        "app_projects",
        "app_checkpoints",
        "app_origins",
        "public_projects",
        "operation_claims",
        "app_operations",
        "app_receipts",
    ],
)
def test_sqlite_actual_write_denial_rolls_whole_transaction_back(store, table):
    before = logical_dump(store)
    attempts = []

    def deny(action, first, *_rest):
        if action == sqlite3.SQLITE_INSERT and first == table:
            attempts.append(first)
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    store._db.set_authorizer(deny)
    try:
        fault("structure", lambda: run(store, intent()))
    finally:
        store._db.set_authorizer(None)
    assert attempts and logical_dump(store) == before and not store._db.in_transaction


@pytest.mark.parametrize("field", ["name", "host", "session"])
def test_same_operation_different_business_or_origin_never_reuses(store, field):
    value = intent()
    run(store, value)
    before = logical_dump(store)
    other = deepcopy(value)
    if field == "name":
        other["request"]["name"] = "different"
    else:
        other["origin"]["hostClientId" if field == "host" else "engineSessionId"] = uid()
    fault("identity", lambda: run(store, other))
    assert logical_dump(store) == before


def test_global_cross_namespace_conflicts_both_directions(store):
    result = run(store, intent())
    project, op = result["projectId"], result["operationId"]
    before = logical_dump(store)
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        store.apply_application(
            project,
            op,
            {"type": "metadata", "expectedVersion": 1, "patch": {"name": "other"}},
            actor=uid(),
            permission="write",
        )
    assert logical_dump(store) == before
    old_op = uid()
    store.apply_application(
        project,
        old_op,
        {"type": "metadata", "expectedVersion": 1, "patch": {"name": "other"}},
        actor=uid(),
        permission="write",
    )
    before = logical_dump(store)
    fault("identity", lambda: run(store, intent(operation=old_op)))
    assert logical_dump(store) == before
    store.project = project
    job = create(store)
    before = logical_dump(store)
    fault("identity", lambda: run(store, intent(operation=job["operationId"])))
    assert logical_dump(store) == before


def test_uuid_collision_rejected_without_adopting_existing_project(store, monkeypatch):
    first = run(store, intent())
    before = logical_dump(store)
    monkeypatch.setattr(project_lifecycle, "uuid4", lambda: UUID(first["projectId"]))
    fault("identity", lambda: run(store, intent()))
    assert logical_dump(store) == before


def test_orphan_global_operation_evidence_not_adopted(store):
    store.create_project("legacy")
    op = uid()
    store.commit("legacy", 0, op, "legacy-job")
    before = logical_dump(store)
    fault("identity", lambda: run(store, intent(operation=op)))
    assert logical_dump(store) == before


def test_creation_claim_cannot_borrow_a_valid_domain_receipt(store):
    project, operation = uid(), uid()
    store.create_project(project)
    store.commit(project, 0, operation, "domain-job", definitions=[])
    value = intent(operation=operation)
    forged = project_lifecycle.model(
        project, value["request"], value["origin"], project_lifecycle.library_evidence(store)
    )
    store._db.execute(
        "INSERT INTO operation_claims VALUES (?,?,?,?,?,?)",
        forged["rows"]["operation_claims"][0],
    )
    store._db.commit()
    before = logical_dump(store)
    assert store.project_receipt(project, operation)["domainAfterRevision"] == 1
    assert (
        store._db.execute(
            "SELECT 1 FROM app_checkpoints WHERE id=?",
            (forged["receipt"]["afterCheckpointRef"],),
        ).fetchone()
        is None
    )
    with zero_write(store):
        fault("structure", lambda: project_lifecycle.creation_context(store, project, operation))
        with pytest.raises(format3.Format3Fault):
            store._validate_job3()
    assert logical_dump(store) == before
    path = store.path
    store.close()
    with pytest.raises(format3.Format3Fault):
        JobStore(path, contract=CONTRACT, target_format=3)
    db = sqlite3.connect(path)
    try:
        assert "\n".join(db.iterdump()) == before
    finally:
        db.close()


@pytest.mark.parametrize("kind", ["claim", "receipt", "checkpoint", "mixed-tag"])
def test_corrupt_existing_creation_is_not_repaired(store, kind):
    value = intent()
    result = run(store, value)
    table = {
        "claim": "operation_claims",
        "receipt": "app_receipts",
        "checkpoint": "app_checkpoints",
        "mixed-tag": "operation_claims",
    }[kind]
    with corrupt_immutable(store, table):
        if kind == "claim":
            store._db.execute("UPDATE operation_claims SET fingerprint=?", ("f" * 64,))
        elif kind == "receipt":
            store._db.execute("UPDATE app_receipts SET payload='{}'")
        elif kind == "checkpoint":
            store._db.execute(
                "UPDATE app_checkpoints SET payload='{}' WHERE id=?",
                (result["receipt"]["afterCheckpointRef"],),
            )
        else:
            row = store._db.execute("SELECT context FROM operation_claims").fetchone()[0]
            context = json.loads(row)
            context["applicationContextVersion"] = 1
            store._db.execute(
                "UPDATE operation_claims SET context=?,fingerprint=?",
                (canonical(context), digest(context)),
            )
    store._db.commit()
    before = logical_dump(store)
    fault("structure", lambda: run(store, value))
    assert logical_dump(store) == before


@pytest.mark.parametrize(
    "limits",
    [
        {"metadata_bytes": 80},
        {"catalog_row_bytes": 100},
        {"snapshot_bytes": 100},
        {"page_bytes": 100},
        {"workspace_bytes": 100},
        {"validation_rows": 1},
        {"validation_bytes": 100},
        {"validation_work": 100},
        {"retained_bytes": 100},
        {"identity_bytes": 35},
    ],
)
def test_all_new_persistent_budgets_refuse_before_first_insert(store, limits):
    before = logical_dump(store)
    inserts = []

    def observe(action, first, *_rest):
        if action == sqlite3.SQLITE_INSERT:
            inserts.append(first)
        return sqlite3.SQLITE_OK

    store._db.set_authorizer(observe)
    try:
        fault("limit", lambda: run(store, intent(limits=replace(ReadLimits(), **limits))))
    finally:
        store._db.set_authorizer(None)
    assert inserts == [] and logical_dump(store) == before


def test_complete_metadata_boundary_and_json_escape_expansion(store):
    assert len(canonical({**format3.metadata("created"), "name": "x" * 4096}).encode()) == 4178
    before = logical_dump(store)
    for name in ("x" * 4096, '"' * 4014):
        with zero_write(store):
            fault("limit", lambda name=name: run(store, intent(name)))
    assert logical_dump(store) == before
    result = run(store, intent("x" * 4014))
    assert (
        len(
            canonical(
                ProjectHostReader(store).workspace(result["projectId"], editor="q")["metadata"]
            ).encode()
        )
        == 4096
    )


def test_workspace_editor_worst_escape_budget_is_checked_not_only_ascii(store):
    with zero_write(store):
        fault(
            "limit", lambda: run(store, intent(limits=replace(ReadLimits(), workspace_bytes=1000)))
        )


@pytest.mark.parametrize(
    "field",
    [
        "metadata_bytes",
        "catalog_row_bytes",
        "snapshot_bytes",
        "page_bytes",
        "workspace_bytes",
        "validation_rows",
        "validation_bytes",
        "validation_work",
        "retained_bytes",
        "identity_bytes",
        "projects",
    ],
)
@pytest.mark.parametrize("offset", [-1, 0, 1])
def test_real_post_state_budget_boundary_plus_minus_one(tmp_path, monkeypatch, field, offset):
    old = "00000000-0000-4000-8000-000000000001"
    new = "00000000-0000-4000-8000-000000000004"
    monkeypatch.setattr(project_lifecycle, "uuid4", lambda: UUID(new))
    request = intent("fixture")
    reference = JobStore(tmp_path / "reference.sqlite", contract=CONTRACT, target_format=3)
    reference.create_project(old)
    created = run(reference, request)
    reader = ProjectHostReader(reference)
    items = reader.catalog_start()["items"]
    workspace = reader.workspace(new, editor="\x01" * 512)
    counts, total = {}, 0
    # Independent SQL measurement of the real committed database, not a
    # predicted candidate or the new preflight's result.
    for (table,) in reference._db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall():
        quoted = '"' + table.replace('"', '""') + '"'
        columns = reference._db.execute(f"PRAGMA table_info({quoted})").fetchall()
        expression = "+".join(
            'coalesce(length(CAST("' + c[1].replace('"', '""') + '" AS BLOB)),0)' for c in columns
        )
        count, size = reference._db.execute(
            f"SELECT count(*),coalesce(sum({expression}),0) FROM {quoted}"
        ).fetchone()
        counts[table] = count
        total += size
    page_bytes = 0
    for size in range(1, 65):
        page = reader.catalog_start(page_size=size)
        while True:
            page_bytes = max(page_bytes, len(canonical(page).encode()))
            if page["nextCursor"] is None:
                break
            page = reader.catalog_next(page["nextCursor"])
    boundaries = {
        "metadata_bytes": len(canonical(workspace["metadata"]).encode()),
        "catalog_row_bytes": max(len(canonical(item).encode()) for item in items),
        "snapshot_bytes": sum(len(canonical(item).encode()) for item in items) + 2 + len(items),
        "page_bytes": page_bytes,
        "workspace_bytes": len(canonical(workspace).encode()),
        "validation_rows": sum(counts.values()),
        "validation_bytes": total,
        "validation_work": total * (1 + counts["app_operations"] + counts["snapshots"]),
        "retained_bytes": 768 + len(items) * (ReadLimits().catalog_row_bytes + 64),
        "identity_bytes": 36,
        "projects": 2,
    }
    reference.close()
    target = JobStore(tmp_path / "target.sqlite", contract=CONTRACT, target_format=3)
    try:
        target.create_project(old)
        before = logical_dump(target)
        policy = replace(ReadLimits(), **{field: boundaries[field] + offset})
        value = dict(request, readerLimits=policy)
        if offset < 0:
            with zero_write(target):
                fault("limit", lambda: run(target, value))
            assert logical_dump(target) == before
        else:
            result = run(target, value)
            assert result["projectId"] == created["projectId"]
            assert (
                ProjectHostReader(target, limits=policy).workspace(new, editor="q")["metadata"][
                    "name"
                ]
                == "fixture"
            )
    finally:
        target.close()


@pytest.mark.parametrize("actual", [0, 2, 4])
def test_actual_header_must_be_three_before_insert(store, actual):
    store._db.execute(f"PRAGMA user_version={actual}")
    with zero_write(store):
        fault("state", lambda: run(store, intent()))


@pytest.mark.parametrize(
    "mutation",
    [
        "core-bool",
        "request-bool",
        "extra",
        "client-project",
        "init-extra",
        "reader-dict",
        "origin-extra",
    ],
)
def test_strict_core_request_shapes_not_authorization_inputs(store, mutation):
    value = intent()
    if mutation == "core-bool":
        value["projectCreateCoreVersion"] = True
    elif mutation == "request-bool":
        value["request"]["requestVersion"] = True
    elif mutation == "extra":
        value["request"]["extra"] = None
    elif mutation == "client-project":
        value["request"]["projectId"] = uid()
    elif mutation == "init-extra":
        value["request"]["initialization"]["plan"] = {}
    elif mutation == "reader-dict":
        value["readerLimits"] = {}
    else:
        value["origin"]["scope"] = True
    with zero_write(store):
        fault("input", lambda: run(store, value))


def test_uuid_scalar_size_is_rejected_before_parsing_or_copy(store, monkeypatch):
    value = intent()

    def parser(value):
        assert len(value) == 36, "oversized scalar reached UUID parser"
        return UUID(value).version == 4

    monkeypatch.setattr(project_lifecycle, "uuid_ref", parser)
    for field in ("operationId", "hostClientId", "engineSessionId"):
        bad = deepcopy(value)
        (bad["request"] if field == "operationId" else bad["origin"])[field] = "x" * 1000000
        with zero_write(store):
            fault("input", lambda bad=bad: run(store, bad))


def test_all_page_sizes_checked_even_when_largest_size_fits(store, monkeypatch):
    projects = [f"00000000-0000-4000-8000-{i:012d}" for i in range(1, 5)]
    for project in projects[:3]:
        store.create_project(project)
    monkeypatch.setattr(project_lifecycle, "uuid4", lambda: UUID(projects[3]))
    # Precisely derive the threshold from the actual existing row shape.
    candidate = project_lifecycle.model(
        projects[3],
        intent("x" * 900)["request"],
        intent()["origin"],
        project_lifecycle.library_evidence(store),
    )
    rows = ProjectHostReader(store).catalog_start()["items"] + [
        {
            "projectId": projects[3],
            "domainRevision": 0,
            "metadataVersion": 1,
            "metadata": candidate["after"]["application"]["metadata"],
            "operationSequence": 1,
            "checkpointRef": digest(candidate["after"]),
        }
    ]

    def size(offset, count):
        end = min(offset + count, 4)
        return len(
            canonical(
                {
                    "catalogVersion": 1,
                    "snapshotId": "0" * 36,
                    "items": rows[offset:end],
                    "total": 4,
                    "offset": offset,
                    "nextCursor": "0" * 93 if end < 4 else None,
                }
            ).encode()
        )

    maximum = max(size(0, 3), size(3, 3), *(size(i, 1) for i in range(4)))
    assert size(2, 2) > maximum
    with zero_write(store):
        fault(
            "limit",
            lambda: run(
                store,
                intent("x" * 900, limits=replace(ReadLimits(), page_items=3, page_bytes=maximum)),
            ),
        )


def test_unknown_outer_transaction_cannot_publish_uncommitted_creation(store):
    store._db.execute("BEGIN")
    fault("state", lambda: run(store, intent()))
    assert store._db.in_transaction
    store._db.rollback()


def test_pure_store3_and_missing_job3_structure_rejected_before_write(tmp_path, store):
    pure = Store(tmp_path / "pure.sqlite", target_format=3)
    try:
        before = logical_dump(pure)
        fault("state", lambda: run(pure, intent()))
        assert logical_dump(pure) == before
    finally:
        pure.close()
    store._db.execute("ALTER TABLE operation_claims RENAME TO missing_claims")
    store._db.commit()
    with zero_write(store):
        fault("structure", lambda: run(store, intent()))


def test_mutation_branches_are_exclusive_even_explicit_empty_lists(store):
    value = intent()
    before = logical_dump(store)
    for kwargs in ({"definitions": []}, {"manual": []}, {"application": {}}, {"compensate": {}}):
        with pytest.raises(ValueError):
            run(store, value, **kwargs)
    assert logical_dump(store) == before


@pytest.mark.parametrize("name", ["", " ", "\0", "\ud800", None, 1, True])
def test_invalid_names_are_strict_and_zero_write(store, name):
    with zero_write(store):
        fault("input", lambda: run(store, intent(name)))


def test_legacy_format2_behavior_and_old_format3_reader_reject_new_namespace(tmp_path, store):
    result = run(store, intent())
    old = tmp_path / "old"
    old.mkdir()
    # Frozen source modules only, no other-tree runtime/environment is reused.
    for relative in ["storage.py", "job_store.py", "project/format3.py"]:
        path = old / "ontolearn_engine" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(
            subprocess.check_output(
                [
                    "git",
                    "show",
                    "a816c2d018772ce8b172101d9debec787ffa434a:packages/engine/src/ontolearn_engine/"
                    + relative,
                ],
                cwd=ROOT,
            )
        )
    package = old / "ontolearn_engine"
    (package / "invalidation-v2.json").write_bytes(
        subprocess.check_output(
            [
                "git",
                "show",
                "a816c2d018772ce8b172101d9debec787ffa434a:"
                "packages/engine/src/ontolearn_engine/invalidation-v2.json",
            ],
            cwd=ROOT,
        )
    )
    (package / "__init__.py").write_text(
        "from pathlib import Path\n__path__.append("
        + repr(str(ROOT / "packages/engine/src/ontolearn_engine"))
        + ")\n"
    )
    (package / "project/__init__.py").write_text(
        "from pathlib import Path\n__path__.append("
        + repr(str(ROOT / "packages/engine/src/ontolearn_engine/project"))
        + ")\n"
    )
    code = (
        "import sys;sys.path.insert(0,sys.argv[1]);"
        "from ontolearn_engine.storage import Store;Store(sys.argv[2],target_format=3)"
    )
    store.close()
    child = subprocess.run(
        [sys.executable, "-c", code, str(old), str(store.path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert child.returncode != 0 and "Invalid project structure" in child.stderr
    reopened = JobStore(store.path, contract=CONTRACT, target_format=3)
    try:
        assert (
            ProjectHostReader(reopened).workspace(result["projectId"], editor="q")[
                "metadataVersion"
            ]
            == 1
        )
    finally:
        reopened.close()
    legacy = Store(tmp_path / "legacy.sqlite")
    legacy.create_project("p")
    try:
        marker = legacy.commit("p", 0, "operation", "job", definitions=[])
        expected = {
            "base": 0,
            "definitions": [],
            "manual": None,
            "edits": None,
            "remove": None,
            "mapping": None,
        }
        assert marker["fingerprint"] == digest(expected) and json.loads(marker["plan"]) == expected
        before = logical_dump(legacy)
        fault("state", lambda: run(legacy, intent()))
        assert logical_dump(legacy) == before
    finally:
        legacy.close()
