"""Named example RPC over a real explicitly staged bundle; SOURCE tests, unrun."""

import hashlib
import json

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.project.mainline import make_example_provider
from ontolearn_engine.project.project_lifecycle import EXAMPLE_ID, EXAMPLE_INPUT_SHA256
from ontolearn_engine.protocol import ProtocolFault
from ontolearn_engine.resources import CONTRACT
from test_mainline_dispatch import create, exchange, frame, uid
from test_mainline_example_create import RESOURCE

INDEX_SHA256 = "a2200250856474ebbae669151891d5495e7fcd042e8f8f0a77ccbb0553b521ee"


@pytest.fixture
def staged_bundle(tmp_path):
    root = tmp_path / "equipment-maintenance"
    root.mkdir(mode=0o700)
    manifest = {
        "exampleProviderManifestVersion": 1,
        "exampleId": EXAMPLE_ID,
        "input": {
            "path": "load-input.json",
            "bytes": 10930,
            "sha256": EXAMPLE_INPUT_SHA256,
        },
    }
    raw = (
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    assert len(raw) == 198 and hashlib.sha256(raw).hexdigest() == INDEX_SHA256
    assert len(RESOURCE) == 10930 and hashlib.sha256(RESOURCE).hexdigest() == EXAMPLE_INPUT_SHA256
    (root / "t01-provider.json").write_bytes(raw)
    (root / "load-input.json").write_bytes(RESOURCE)
    return root


@pytest.fixture
def named_owned(tmp_path, staged_bundle):
    store = JobStore(tmp_path / "named.sqlite", contract=CONTRACT, target_format=3)
    provider = make_example_provider(root=staged_bundle, manifest_sha256=INDEX_SHA256)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY, example_provider=provider)
    hello = exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})
    assert hello["ok"] and "project.example.create" in hello["result"]["capabilities"], hello
    assert actor.mainline.example_provider is provider
    try:
        yield actor, store, staged_bundle
    finally:
        actor.mainline.close()
        store.close()


def request(name="设备运维", operation=None):
    return {
        "exampleCreateRequestVersion": 1,
        "operationId": operation or uid(),
        "name": name,
        "exampleId": EXAMPLE_ID,
        "inputDigest": EXAMPLE_INPUT_SHA256,
    }


def dump(store):
    return "\n".join(store._db.iterdump())


def test_named_load_open_query_prepare_retry_and_original_bundle(named_owned):
    actor, store, root = named_owned
    before_bundle = {path.name: path.read_bytes() for path in root.iterdir()}
    params = request()
    created = exchange(actor, "project.example.create", params)
    assert created["ok"], created
    result = created["result"]
    assert CONTRACT.validate_business3("result_project.example.create", result)
    project = result["projectId"]
    assert result["receipt"]["exampleCreateReceiptVersion"] == 1
    assert result["receipt"]["domainRevision"] == 1
    assert actor.mainline.selected == project
    context = json.loads(
        store._db.execute(
            "SELECT context FROM operation_claims WHERE operation=?", (params["operationId"],)
        ).fetchone()[0]
    )
    assert context["origin"] == {
        "hostClientId": actor.host_client_id,
        "engineSessionId": actor.session,
        "permission": "library.create",
    }
    before_retry = dump(store)
    retried = exchange(actor, "project.example.create", params)
    assert retried["ok"] and retried["result"] == result, retried
    assert dump(store) == before_retry

    opened = exchange(actor, "project.open", {"projectId": project})
    assert opened["ok"] and opened["result"]["projectRevision"] == 1, opened
    loaded = exchange(
        actor,
        "query.definition.load",
        {
            "projectId": project,
            "definitionId": "unclosed-high",
            "selection": {"kind": "current"},
        },
    )
    assert loaded["ok"] and loaded["result"]["kind"] == "managed", loaded
    record = loaded["result"]
    assert record["draft"]["source"] == "template"
    assert not record["draft"]["sparql"].endswith("\n")
    prepared = exchange(
        actor,
        "query.execution.prepare",
        {
            "projectId": project,
            "operationId": uid(),
            "definitionBinding": {
                key: record[key]
                for key in (
                    "definitionId",
                    "definitionVersion",
                    "definitionSha256",
                    "descriptorVersion",
                    "descriptorSha256",
                )
            },
            "visibleDraft": record["draft"],
            "selection": {"kind": "current"},
        },
    )
    assert prepared["ok"], prepared
    assert prepared["result"]["input"]["inputSnapshotId"] == result["receipt"]["inputSnapshotId"]
    assert prepared["result"]["input"]["scope"] == "asserted"
    assert store._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0
    assert {path.name: path.read_bytes() for path in root.iterdir()} == before_bundle


def test_named_reset_makes_new_project_and_blank_shape_stays_original(named_owned):
    actor, store, _ = named_owned
    blank, _ = create(actor)
    assert blank["receipt"]["projectCreateReceiptVersion"] == 1
    assert blank["receipt"]["domainRevision"] == 0
    assert "exampleId" not in blank["receipt"]
    first = exchange(actor, "project.example.create", request())
    second = exchange(actor, "project.example.create", request())
    assert first["ok"] and second["ok"], (first, second)
    identities = {first["result"]["projectId"], second["result"]["projectId"], blank["projectId"]}
    assert len(identities) == 3
    assert store.state(store._project(blank["projectId"]))["definitions"] == []
    assert exchange(actor, "project.open", {"projectId": blank["projectId"]})["ok"]


@pytest.mark.parametrize(
    "failure",
    [
        "missing-manifest",
        "changed-manifest",
        "missing-input",
        "changed-input",
    ],
)
def test_committed_exact_retry_uses_immutable_receipt_after_bundle_damage(named_owned, failure):
    actor, store, root = named_owned
    params = request()
    first = exchange(actor, "project.example.create", params)
    assert first["ok"], first
    member = root / ("t01-provider.json" if "manifest" in failure else "load-input.json")
    if failure.startswith("missing"):
        member.unlink()
    else:
        member.write_bytes(member.read_bytes() + b" ")
    before = dump(store)
    retried = exchange(actor, "project.example.create", params)
    assert retried["ok"] and retried["result"] == first["result"], retried
    assert dump(store) == before
    rebound = exchange(actor, "project.example.create", {**params, "name": "不同请求"})
    assert not rebound["ok"] and rebound["error"]["code"] == "IDENTITY_CONFLICT", rebound
    assert dump(store) == before
    fresh = exchange(actor, "project.example.create", request())
    assert not fresh["ok"] and fresh["error"]["code"] == "NOT_FOUND", fresh
    assert dump(store) == before
    assert actor.mainline.selected == first["result"]["projectId"]


def test_committed_retry_rejects_a_different_real_handshake_origin(named_owned):
    actor, store, root = named_owned
    params = request()
    first = exchange(actor, "project.example.create", params)
    assert first["ok"], first
    actor.mainline.close()
    (root / "load-input.json").unlink()
    other = Coordinator(store, profile="business3", _ready=_JOB_READY)
    try:
        hello = exchange(other, "hello", {"supportedVersions": [3], "clientId": uid()})
        assert hello["ok"] and other.session != actor.session, hello
        before = dump(store)
        refused = exchange(other, "project.example.create", params)
        assert not refused["ok"] and refused["error"]["code"] == "IDENTITY_CONFLICT", refused
        assert dump(store) == before and other.mainline.selected is None
    finally:
        other.mainline.close()


@pytest.mark.parametrize(
    "failure",
    [
        "missing-manifest",
        "changed-manifest",
        "missing-input",
        "changed-input",
        "symlink-input",
    ],
)
def test_missing_or_damaged_bundle_never_publishes_half_project(named_owned, failure):
    actor, store, root = named_owned
    blank, _ = create(actor)
    member = root / ("t01-provider.json" if "manifest" in failure else "load-input.json")
    if failure.startswith("missing"):
        member.unlink()
    elif failure.startswith("changed"):
        member.write_bytes(member.read_bytes() + b" ")
    else:
        outside = root.parent / "outside-input.json"
        outside.write_bytes(member.read_bytes())
        member.unlink()
        member.symlink_to(outside)
    before = dump(store)
    response = exchange(actor, "project.example.create", request())
    assert not response["ok"] and response["error"]["code"] == "NOT_FOUND", response
    assert response["error"]["params"] == {"resource": "snapshot"}
    assert str(root) not in json.dumps(response)
    assert dump(store) == before
    assert actor.mainline.selected == blank["projectId"]
    assert actor.mainline.projects() == frozenset([blank["projectId"]])


def test_no_bootstrap_provider_fails_closed_and_dto_cannot_replace_it(tmp_path):
    store = JobStore(tmp_path / "missing.sqlite", contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    try:
        assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
        before = dump(store)
        response = exchange(actor, "project.example.create", request())
        assert not response["ok"] and response["error"]["code"] == "NOT_FOUND", response
        assert response["error"]["params"] == {"resource": "snapshot"}
        assert dump(store) == before and actor.mainline.selected is None
        with pytest.raises(JobFault, match="INVALID_STATE"):
            Coordinator(
                store,
                profile="business3",
                _ready=_JOB_READY,
                example_provider={"root": "/untrusted", "manifest_sha256": INDEX_SHA256},
            )
        assert dump(store) == before
    finally:
        actor.mainline.close()
        store.close()


@pytest.mark.parametrize("extra", ["resource", "root", "path", "origin", "example_provider"])
def test_wire_cannot_supply_resource_location_bytes_or_authority(named_owned, extra):
    actor, store, _ = named_owned
    before = dump(store)
    params = {**request(), extra: "/wire-must-not-be-read"}
    refused = exchange(actor, "project.example.create", params)
    assert not refused["ok"] and refused["error"]["code"] == "INVALID_REQUEST", refused
    assert dump(store) == before and actor.mainline.selected is None


def test_old_session_is_fatal_before_provider_or_store_admission(named_owned):
    actor, store, root = named_owned
    # A removed actual member distinguishes a pre-dispatch session rejection
    # from accidental resource admission without mocking provider.load.
    (root / "load-input.json").unlink()
    message = frame(actor, "project.example.create", request())
    message["engineSessionId"] = uid()
    before = dump(store)
    trace = []
    store._db.set_trace_callback(trace.append)
    try:
        with pytest.raises(ProtocolFault):
            actor.request(message)
    finally:
        store._db.set_trace_callback(None)
    assert trace == [] and dump(store) == before
    assert actor.closed and actor.mainline.selected is None


def test_unknown_named_delivery_retains_actual_receipt_and_closes_authority(named_owned):
    actor, store, _ = named_owned
    message = frame(actor, "project.example.create", request())
    response = actor.request(message)
    assert response["ok"], response
    result = response["result"]
    original = actor.mainline.replies[message["id"]]
    scalar = original.scalar
    actor.finish_query_reply(message["id"], emitted=False, failure=BrokenPipeError())
    assert actor.mainline.replies[message["id"]] is original and original.unknown
    assert original.scalar == scalar and not actor.mainline.projects()
    assert not actor.mainline.enabled()
    assert (
        store.project_receipt(result["projectId"], message["params"]["operationId"])
        == result["receipt"]
    )
    assert store._db.execute("SELECT count(*) FROM projects").fetchone()[0] == 1
