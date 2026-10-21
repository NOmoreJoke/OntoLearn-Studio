"""Actual approved original input projection -> producer API census; no oracle."""

import hashlib
import json
from collections import Counter
from dataclasses import asdict

from ontolearn_engine import semantic_profile_probe as original
from ontolearn_engine.resources import CONTRACT, ROOT
from ontolearn_engine.semantic_execution import ProfileExecutionFault
from ontolearn_engine.semantic_profile_input import MaterialFailure, prepare_profile_material
from ontolearn_engine.semantic_profile_production import execute_admitted_profile_job

inputs = original._load_inputs()
schema = json.loads((ROOT / "v2/schema.json").read_bytes())
items = []
for index, case in enumerate(inputs["mathInputs"]):
    item = {
        "id": case["id"],
        "originalInputProjectionSha256": case["inputProjectionJsonSha256"],
        "sourceRefs": case["sourceRefs"],
    }
    if not case["eligibleStandaloneMathInput"]:
        item.update(status="not-executed", reason="ORIGINAL_INPUT_CONTEXT_INCOMPLETE")
    else:
        records, specs, disabled = original._construct_records(case, index)
        phase = "raw-material"
        try:
            material = prepare_profile_material(
                records=records, rules=specs, disabled_rule_ids=disabled
            )
            phase = "actual-computation"
            result = execute_admitted_profile_job(
                material, error_catalog=CONTRACT.ERROR_CATALOG, error_schema=schema
            )
            item.update(
                status="success",
                payloadSha256=hashlib.sha256(result.payload_json).hexdigest(),
                rowsSha256=hashlib.sha256(result.rows_json).hexdigest(),
                sourceSha256=hashlib.sha256(result.source_encoded).hexdigest(),
                definitionsSha256=hashlib.sha256(result.definitions_encoded).hexdigest(),
                catalogSha256=hashlib.sha256(result.catalog_json).hexdigest(),
                originalAllocation=asdict(result.original_allocation),
                cReceipt=asdict(result.capture_receipt),
            )
            result = material = None
        except ProfileExecutionFault as exc:
            item.update(status="failure", phase=phase, error=exc.error, diagnostic=exc.diagnostic)
        except MaterialFailure as exc:
            item.update(
                status="material-failure",
                phase=phase,
                reason=exc.reason,
                domain=exc.domain,
                stage=exc.stage,
            )
    items.append(item)
print(
    json.dumps(
        {
            "format": "producer83-evidence/1",
            "sourceInputSha256": original.INPUT_SHA256,
            "counts": dict(Counter(item["status"] for item in items)),
            "cases": items,
            "sourceAuthorityAuthenticated": False,
            "lifecycleExecuted": False,
            "acceptanceOracleCompared": False,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
)
