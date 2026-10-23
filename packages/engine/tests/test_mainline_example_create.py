"""Named FR003 source definitions; real Store tests, no worker/GUI or answer replay."""

import hashlib
import json
from copy import deepcopy
from dataclasses import replace

import pytest
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project import project_lifecycle as lifecycle
from ontolearn_engine.project.project_host import ReadLimits
from ontolearn_engine.storage import digest
from test_job_store import CONTRACT, uid

# Exact fixed T09 input, independent of a mutable checkout or packaging path.
RESOURCE = (
    "{\n"
    '  "schema": "t09.fr003.load-input/v1",\n'
    '  "contractKind": "T09_TO_T01_ADAPTER_INPUT_NOT_PUBLIC_IPC_OR_PROJECT_FORMAT",\n'
    '  "status": "PREPARED_ADAPTER_NOT_IMPLEMENTED",\n'
    '  "exampleId": "equipment-maintenance",\n'
    '  "exampleVersion": "prd-v0.6-learning-1.fr003-input-1",\n'
    '  "baseline": "G-base",\n'
    '  "sourceHead": "0cde6a11604214f4ff34d2a9fbcfb80b6f72bfd2",\n'
    '  "sourceBinding": {\n'
    '    "sourcePath": "tests/fixtures/product-baselines/G-base.json",\n'
    '    "bytes": 8219,\n'
    '    "sha256": "306d41b332d223b47929eb90f196c71e4965a0e9ff81100c9469ed32612e8845",\n'
    '    "proposedBundlePath": "resources/examples/equi'
    "pment-maintenance/source/tests/fixtures/product-ba"
    'selines/G-base.json",\n'
    '    "role": "baseline-input",\n'
    '    "consumer": "T01 approved example initialization adapter",\n'
    '    "sourceMutated": false\n'
    "  },\n"
    '  "versions": {\n'
    '    "fixtureVersion": "prd-v0.6-learning-1",\n'
    '    "inputVersion": "g0-1",\n'
    '    "ruleVersion": "rules-1",\n'
    '    "behaviorVersion": "behaviors-1",\n'
    '    "semanticsVersion": "PRD-V0.6-E"\n'
    "  },\n"
    '  "ontology": [\n'
    "    {\n"
    '      "subject": "urn:ontolearn:learning:Equipment",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<http://www.w3.org/2002/07/owl#Class>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:Alarm",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<http://www.w3.org/2002/07/owl#Class>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:WorkOrder",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<http://www.w3.org/2002/07/owl#Class>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:HighRiskEquipment",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<http://www.w3.org/2002/07/owl#Class>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:name",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<http://www.w3.org/2002/07/owl#DatatypeProperty>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:level",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<http://www.w3.org/2002/07/owl#DatatypeProperty>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:status",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<http://www.w3.org/2002/07/owl#DatatypeProperty>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:alarm",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<http://www.w3.org/2002/07/owl#ObjectProperty>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:workOrderStatus",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<http://www.w3.org/2002/07/owl#DatatypeProperty>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:eventOrder",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<http://www.w3.org/2002/07/owl#ObjectProperty>"\n'
    "    }\n"
    "  ],\n"
    '  "assertedFacts": [\n'
    "    {\n"
    '      "subject": "urn:ontolearn:learning:equipment/001",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<urn:ontolearn:learning:Equipment>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:equipment/001",\n'
    '      "predicate": "urn:ontolearn:learning:name",\n'
    '      "object": "\\"泵站A\\""\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:equipment/002",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<urn:ontolearn:learning:Equipment>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:equipment/002",\n'
    '      "predicate": "urn:ontolearn:learning:name",\n'
    '      "object": "\\"泵站B\\""\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:equipment/003",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<urn:ontolearn:learning:Equipment>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:equipment/003",\n'
    '      "predicate": "urn:ontolearn:learning:name",\n'
    '      "object": "\\"备用泵C\\""\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:alarm/A01",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<urn:ontolearn:learning:Alarm>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:alarm/A01",\n'
    '      "predicate": "urn:ontolearn:learning:level",\n'
    '      "object": "\\"High\\""\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:alarm/A01",\n'
    '      "predicate": "urn:ontolearn:learning:status",\n'
    '      "object": "\\"Open\\""\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:equipment/001",\n'
    '      "predicate": "urn:ontolearn:learning:alarm",\n'
    '      "object": "<urn:ontolearn:learning:alarm/A01>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:alarm/A02",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<urn:ontolearn:learning:Alarm>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:alarm/A02",\n'
    '      "predicate": "urn:ontolearn:learning:level",\n'
    '      "object": "\\"High\\""\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:alarm/A02",\n'
    '      "predicate": "urn:ontolearn:learning:status",\n'
    '      "object": "\\"Closed\\""\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:equipment/002",\n'
    '      "predicate": "urn:ontolearn:learning:alarm",\n'
    '      "object": "<urn:ontolearn:learning:alarm/A02>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:alarm/A03",\n'
    '      "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '      "object": "<urn:ontolearn:learning:Alarm>"\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:alarm/A03",\n'
    '      "predicate": "urn:ontolearn:learning:level",\n'
    '      "object": "\\"Low\\""\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:alarm/A03",\n'
    '      "predicate": "urn:ontolearn:learning:status",\n'
    '      "object": "\\"Open\\""\n'
    "    },\n"
    "    {\n"
    '      "subject": "urn:ontolearn:learning:equipment/003",\n'
    '      "predicate": "urn:ontolearn:learning:alarm",\n'
    '      "object": "<urn:ontolearn:learning:alarm/A03>"\n'
    "    }\n"
    "  ],\n"
    '  "singleValuedPredicates": ["urn:ontolearn:learning:workOrderStatus"],\n'
    '  "queries": [\n'
    "    {\n"
    '      "id": "unclosed-high",\n'
    '      "scope": "current-asserted",\n'
    '      "text": "PREFIX l: <urn:ontolearn:learning:>'
    "\\nSELECT ?alarm WHERE { ?equipment a l:Equipment ;"
    ' l:alarm ?alarm . ?alarm l:level \\"High\\" ; l:stat'
    'us \\"Open\\" . } ORDER BY ?alarm\\n",\n'
    '      "source": {\n'
    '        "sourcePath": "tests/fixtures/product-baselines/unclosed-high.rq",\n'
    '        "bytes": 162,\n'
    '        "sha256": "8efbacd589c42ac40abbb55475cdd088e407a88a23e0db61dc8375e04e4dd386",\n'
    '        "proposedBundlePath": "resources/examples/'
    "equipment-maintenance/source/tests/fixtures/produc"
    't-baselines/unclosed-high.rq",\n'
    '        "role": "readonly-query-source",\n'
    '        "consumer": "T04 current-asserted real query",\n'
    '        "sourceMutated": false\n'
    "      }\n"
    "    }\n"
    "  ],\n"
    '  "domainMaterials": {\n'
    '    "constraints": [\n'
    "      {\n"
    '        "id": "name-required",\n'
    '        "targetClass": "urn:ontolearn:learning:Equipment",\n'
    '        "path": "urn:ontolearn:learning:name",\n'
    '        "minCount": 1,\n'
    '        "scope": "current-asserted",\n'
    '        "includeInferred": false\n'
    "      }\n"
    "    ],\n"
    '    "rules": [\n'
    "      {\n"
    '        "id": "R-risk",\n'
    '        "version": 1,\n'
    '        "enabled": true,\n'
    '        "conditions": [\n'
    "          {\n"
    '            "subject": "?equipment",\n'
    '            "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '            "object": "<urn:ontolearn:learning:Equipment>"\n'
    "          },\n"
    "          {\n"
    '            "subject": "?equipment",\n'
    '            "predicate": "urn:ontolearn:learning:alarm",\n'
    '            "object": "?alarm"\n'
    "          },\n"
    "          {\n"
    '            "subject": "?alarm",\n'
    '            "predicate": "urn:ontolearn:learning:level",\n'
    '            "object": "\\"High\\""\n'
    "          },\n"
    "          {\n"
    '            "subject": "?alarm",\n'
    '            "predicate": "urn:ontolearn:learning:status",\n'
    '            "object": "\\"Open\\""\n'
    "          }\n"
    "        ],\n"
    '        "conclusions": [\n'
    "          {\n"
    '            "subject": "?equipment",\n'
    '            "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",\n'
    '            "object": "<urn:ontolearn:learning:HighRiskEquipment>"\n'
    "          }\n"
    "        ],\n"
    '        "inputScope": "asserted-plus-rdfs",\n'
    '        "outputReentry": false\n'
    "      }\n"
    "    ],\n"
    '    "behaviors": [\n'
    "      {\n"
    '        "id": "B-risk",\n'
    '        "version": 1,\n'
    '        "enabled": true,\n'
    '        "priority": 0,\n'
    '        "trigger": {\n'
    '          "eventType": "alarm-added"\n'
    "        },\n"
    '        "conditions": [\n'
    "          {\n"
    '            "eventAlarmLevel": "High"\n'
    "          },\n"
    "          {\n"
    '            "eventAlarmStatus": "Open"\n'
    "          },\n"
    "          {\n"
    '            "eventEquipmentType": "urn:ontolearn:learning:HighRiskEquipment"\n'
    "          }\n"
    "        ],\n"
    '        "actions": [\n'
    "          {\n"
    '            "kind": "create-individual",\n'
    '            "class": "urn:ontolearn:learning:WorkOrder",\n'
    '            "id": "W:{eventId}",\n'
    '            "properties": {\n'
    '              "workOrderStatus": "待处理"\n'
    "            }\n"
    "          },\n"
    "          {\n"
    '            "kind": "add-relation",\n'
    '            "subject": "{eventId}",\n'
    '            "predicate": "urn:ontolearn:learning:eventOrder",\n'
    '            "object": "W:{eventId}"\n'
    "          }\n"
    "        ]\n"
    "      }\n"
    "    ],\n"
    '    "mappings": [\n'
    "      {\n"
    '        "id": "equipment-csv",\n'
    '        "file": "equipment.csv",\n'
    '        "encoding": "utf-8",\n'
    '        "keyColumn": "equipment_id",\n'
    '        "keyType": "string",\n'
    '        "normalization": "none",\n'
    '        "subjectTemplate": "urn:ontolearn:learning:equipment/{equipment_id}",\n'
    '        "columns": {\n'
    '          "equipment_name": "urn:ontolearn:learning:name"\n'
    "        },\n"
    '        "type": "urn:ontolearn:learning:Equipment",\n'
    '        "sourceRowConvention": "physical-line-including-header"\n'
    "      }\n"
    "    ],\n"
    '    "initialState": {\n'
    '      "orders": [],\n'
    '      "pendingEvents": [],\n'
    '      "consumedEvents": [],\n'
    '      "triggeredInstances": []\n'
    "    },\n"
    '    "scenario": {\n'
    '      "maxRounds": 1,\n'
    '      "capacityMode": "direct",\n'
    '      "capacity": 0\n'
    "    }\n"
    "  },\n"
    '  "currentInferredFacts": [],\n'
    '  "currentResults": [],\n'
    '  "loadSemantics": {\n'
    '    "ontologyAndAssertedFacts": "T01 must map into'
    " approved typed definitions/facts and atomically c"
    "ommit to a newly created independent user project "
    "through its business API; these arrays are not Sto"
    're.commit kwargs",\n'
    '    "domainMaterials": "reference definitions only'
    " until individual real domain adapters and persist"
    'ence formats are approved; not execution proof",\n'
    '    "initialState": "empty source state only, not committed simulation history",\n'
    '    "mappingOwnership": "G-base preloaded facts ar'
    "e versioned example facts, not falsely claimed CSV"
    ' mapping execution or managed-source ownership",\n'
    '    "reset": "explicitly confirmed T01 snapshot re'
    "store or independently created new project; never "
    'silently clear/overwrite an existing project",\n'
    '    "onFailure": "no published half-created projec'
    "t; T01 retains actual transaction/failure contract"
    '",\n'
    '    "expectedAnswers": "excluded from load input; '
    "reference-expectations.json is acceptance referenc"
    'e only"\n'
    "  }\n"
    "}\n"
).encode()


def intent(name="设备运维", operation=None):
    return {
        "exampleCreateCoreVersion": 1,
        "request": {
            "exampleCreateRequestVersion": 1,
            "operationId": operation or uid(),
            "name": name,
            "exampleId": "equipment-maintenance",
            "inputDigest": lifecycle.EXAMPLE_INPUT_SHA256,
        },
        "origin": {"hostClientId": uid(), "engineSessionId": uid(), "permission": "library.create"},
        "readerLimits": ReadLimits(),
        "resource": RESOURCE,
    }


def run(store, value, **kwargs):
    return store.commit(
        None, None, value["request"]["operationId"], None, example_creation=value, **kwargs
    )


def dump(store):
    return "\n".join(store._db.iterdump())


@pytest.fixture
def store(tmp_path):
    value = JobStore(tmp_path / "example.sqlite", contract=CONTRACT, target_format=3)
    try:
        yield value
    finally:
        value.close()


def test_pinned_named_supported_mapping_preserves_every_original_value():
    value = intent()
    assert len(RESOURCE) == 10930
    assert hashlib.sha256(RESOURCE).hexdigest() == lifecycle.EXAMPLE_INPUT_SHA256
    source = json.loads(RESOURCE)
    prepared = lifecycle.example_plan(RESOURCE, value["request"])
    plan = prepared.domain_plan()
    ontology = [item for item in plan["definitions"] if item["layer"] == "ontology"]
    assert len(ontology) == 10
    assert [item["value"]["triples"][0] for item in ontology] == source["ontology"]
    assert len(plan["manual"]) == 18
    assert [
        {key: item[key] for key in ("subject", "predicate", "object")} for item in plan["manual"]
    ] == source["assertedFacts"]
    assert all(
        item["id"] == digest([item["subject"], item["predicate"], item["object"]])
        for item in plan["manual"]
    )
    assert any(item["subject"].endswith("equipment/001") for item in plan["manual"])
    assert not any(key in plan for key in ("mapping", "results", "inferred"))
    query = next(item for item in plan["definitions"] if item["layer"] == "query")
    assert [item["id"] for item in ontology] == [
        f"equipment-maintenance-{index:02d}" for index in range(10)
    ]
    assert query["value"]["text"] + "\n" == source["queries"][0]["text"]
    assert len(query["value"]["text"].encode("utf-8")) == 161
    assert set(query["value"]) == {"text", "references", "descriptor"}
    from ontolearn_engine.project.query_definitions import draft

    descriptor = query["value"]["descriptor"]
    visible = {key: value for key, value in descriptor.items() if key != "version"}
    visible["sparql"] = query["value"]["text"]
    assert draft(visible, stored=True) == visible
    assert (
        json.loads(prepared.reference_materials_json)["domainMaterials"]
        == source["domainMaterials"]
    )
    plan["manual"].clear()
    assert len(prepared.domain_plan()["manual"]) == 18


@pytest.mark.parametrize("resource", [b"{}", RESOURCE + b" ", RESOURCE[:-1] + b" "])
def test_unpinned_or_changed_resource_is_not_generic_import(store, resource):
    value = intent()
    value["resource"] = resource
    before = dump(store)
    with pytest.raises(lifecycle.CreationFault):
        run(store, value)
    assert dump(store) == before


def test_blank_request_stays_four_fields_blank_only():
    request = {
        "requestVersion": 1,
        "operationId": uid(),
        "name": "空白",
        "initialization": {"kind": "blank"},
    }
    assert lifecycle.request_value(request) == request
    request["initialization"]["plan"] = {}
    with pytest.raises(lifecycle.CreationFault):
        lifecycle.request_value(request)
    request["initialization"] = {"kind": "equipment-maintenance"}
    with pytest.raises(lifecycle.CreationFault):
        lifecycle.request_value(request)


def test_actual_atomic_named_creation_snapshot_receipt_and_reopen(store):
    value = intent()
    trace = []
    store._db.set_trace_callback(trace.append)
    result = run(store, value)
    store._db.set_trace_callback(None)
    project, operation = result["projectId"], value["request"]["operationId"]
    assert trace.count("BEGIN IMMEDIATE") == trace.count("COMMIT") == 1
    assert store.revision(project) == 1
    # Public vector/name validation is part of creation integration, independent
    # of the RDF graph accepting the same triples.
    assert store.contract.validate_business3("result_project.get", store.project_get(project))
    state = store.state(project)
    assert len(state["facts"]) == 18
    assert len([item for item in state["definitions"] if item["layer"] == "ontology"]) == 10
    assert len([item for item in state["definitions"] if item["layer"] == "query"]) == 1
    assert all(item["owner"] is None and item["source_row"] is None for item in state["facts"])
    assert store.project_receipt(project, operation) == result["receipt"]
    snapshot = store._project_snapshot(result["receipt"]["inputSnapshotId"], project)
    assert snapshot["state"] == state
    assert snapshot["projectRevision"] == 1
    from ontolearn_engine.rdf_snapshot import graph_from_snapshot

    query = next(item for item in state["definitions"] if item["layer"] == "query")
    text = json.loads(query["payload"])["text"]
    assert [(str(row[0]),) for row in graph_from_snapshot(snapshot).query(text)] == [
        ("urn:ontolearn:learning:alarm/A01",)
    ]
    assert store.project_checkpoint(project)["domainRevision"] == 1
    assert store._db.execute("SELECT count(*) FROM results").fetchone()[0] == 0
    assert store._db.execute("SELECT count(*) FROM runs").fetchone()[0] == 0
    before = dump(store)
    assert run(store, value) == result
    assert dump(store) == before
    store.close()
    reopened = JobStore(store.path, contract=CONTRACT, target_format=3)
    try:
        assert run(reopened, value) == result
        assert reopened.state(project) == state
        assert reopened.project_receipt(project, operation) == result["receipt"]
    finally:
        reopened.close()


@pytest.mark.parametrize(
    "phase",
    [
        "example_preflight",
        "example_project",
        "create_app_project",
        "create_domain_snapshot",
        "create_genesis_checkpoint",
        "create_genesis_head",
        "create_origin",
        "example_genesis_verified",
        "example_claim",
        "example_definitions",
        "example_facts",
        "example_versions",
        "example_domain_marker",
        "example_checkpoint",
        "example_receipt",
        "example_validated",
        "before_commit",
    ],
)
def test_every_precommit_boundary_rolls_back_whole_project_and_receipt(store, phase):
    value = intent()
    before = dump(store)

    def stop(current):
        if current == phase:
            raise RuntimeError("injected example boundary")

    with pytest.raises(RuntimeError, match="injected example boundary"):
        run(store, value, hook=stop)
    assert dump(store) == before
    assert not store._db.in_transaction


def test_reset_is_new_copy_and_original_retry_survives_user_edit(store):
    value = intent()
    original = run(store, value)
    project = original["projectId"]
    fact = next(
        item
        for item in store.state(project)["facts"]
        if item["subject"].endswith("equipment/001") and item["predicate"].endswith(":name")
    )
    # A real accepted test.atomic Job owns the later user edit; no fabricated job ID.
    from test_job_store import create

    job = create(
        store, capability="test.atomic", project=project, plan={"edits": {fact["id"]: '"用户编辑"'}}
    )
    store.start_job(job["jobId"])
    store.commit_job(job["jobId"])
    edited = store.state(project)
    assert (
        next(item for item in edited["facts"] if item["id"] == fact["id"])["object"] == '"用户编辑"'
    )
    assert run(store, value) == original
    reset = run(store, intent())
    assert reset["projectId"] != project
    assert store.state(project) == edited
    assert (
        next(item for item in store.state(reset["projectId"])["facts"] if item["id"] == fact["id"])[
            "object"
        ]
        == '"泵站A"'
    )


@pytest.mark.parametrize("field", ["name", "hostClientId", "engineSessionId"])
def test_original_operation_never_rebinds_name_or_origin(store, field):
    value = intent()
    run(store, value)
    before = dump(store)
    other = deepcopy(value)
    if field == "name":
        other["request"][field] = "别名"
    else:
        other["origin"][field] = uid()
    with pytest.raises(lifecycle.CreationFault):
        run(store, other)
    assert dump(store) == before


def test_external_transaction_and_insufficient_preflight_do_not_write(store):
    value = intent()
    before = dump(store)
    store._db.execute("BEGIN")
    try:
        with pytest.raises(lifecycle.CreationFault):
            run(store, value)
    finally:
        store._db.execute("ROLLBACK")
    assert dump(store) == before
    value["readerLimits"] = replace(ReadLimits(), validation_bytes=1)
    with pytest.raises(lifecycle.CreationFault):
        run(store, value)
    assert dump(store) == before


def test_postcommit_delivery_failure_retains_original_receipt(store):
    value = intent()

    def fail_after(phase):
        if phase == "after_commit":
            raise RuntimeError("delivery failed after durable commit")

    with pytest.raises(RuntimeError, match="delivery failed after durable commit"):
        run(store, value, hook=fail_after)
    assert not store._db.in_transaction
    result = run(store, value)
    assert (
        store.project_receipt(result["projectId"], value["request"]["operationId"])
        == result["receipt"]
    )
    assert store._db.execute("SELECT count(*) FROM projects").fetchone()[0] == 1


def test_named_and_blank_operation_namespaces_do_not_alias(store):
    value = intent()
    run(store, value)
    before = dump(store)
    blank = {
        "projectCreateCoreVersion": 1,
        "request": {
            "requestVersion": 1,
            "operationId": value["request"]["operationId"],
            "initialization": {"kind": "blank"},
            "name": value["request"]["name"],
        },
        "origin": value["origin"],
        "readerLimits": ReadLimits(),
    }
    with pytest.raises(lifecycle.CreationFault):
        store.commit(None, None, value["request"]["operationId"], None, creation=blank)
    assert dump(store) == before


def test_named_example_query_load_and_prepare_use_actual_mainline_authority(store):
    from ontolearn_engine.coordinator import _JOB_READY, Coordinator
    from test_mainline_dispatch import exchange

    result = run(store, intent())
    project = result["projectId"]
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    try:
        hello = exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})
        assert hello["ok"], hello
        opened = exchange(actor, "project.open", {"projectId": project})
        assert opened["ok"], opened
        loaded = exchange(
            actor,
            "query.definition.load",
            {
                "projectId": project,
                "definitionId": "unclosed-high",
                "selection": {"kind": "current"},
            },
        )
        assert loaded["ok"], loaded
        record = loaded["result"]
        assert record["kind"] == "managed"
        assert record["draft"]["source"] == "template"
        binding = {
            key: record[key]
            for key in (
                "definitionId",
                "definitionVersion",
                "definitionSha256",
                "descriptorVersion",
                "descriptorSha256",
            )
        }
        prepared = exchange(
            actor,
            "query.execution.prepare",
            {
                "projectId": project,
                "operationId": uid(),
                "definitionBinding": binding,
                "visibleDraft": record["draft"],
                "selection": {"kind": "current"},
            },
        )
        assert prepared["ok"], prepared
        assert (
            prepared["result"]["input"]["inputSnapshotId"] == result["receipt"]["inputSnapshotId"]
        )
        assert prepared["result"]["input"]["scope"] == "asserted"
        assert store._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0
    finally:
        actor.mainline.close()
