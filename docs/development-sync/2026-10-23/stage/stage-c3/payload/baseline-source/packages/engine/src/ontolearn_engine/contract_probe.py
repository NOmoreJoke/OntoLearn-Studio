"""Run bundled common positive/negative examples; no source-checkout lookup."""

import json

from ontolearn_engine.protocol import JsonlReader, ProtocolFault
from ontolearn_engine.resources import CONTRACT


def main() -> None:
    fixtures = json.loads((CONTRACT.ROOT / "fixtures.json").read_text(encoding="utf-8"))
    counts = {}
    for group, function, fields in [
        ("cases", CONTRACT.validate, ("schema", "value")),
        ("routing", CONTRACT.accepts_job_event, ("value", "binding")),
        ("responses", CONTRACT.matches_response, ("request", "response")),
        ("cursors", CONTRACT.cursor_matches, ("record", "request", "nowMs")),
        ("jobListCursors", CONTRACT.job_list_cursor_matches, ("record", "request", "nowMs")),
    ]:
        for case in fixtures[group]:
            if function(*(case[k] for k in fields)) is not case["valid"]:
                raise RuntimeError("BUNDLED_CONTRACT_MISMATCH")
        counts[group] = len(fixtures[group])
    bindings = json.loads((CONTRACT.ROOT / "binding-regressions.json").read_text(encoding="utf-8"))[
        "cases"
    ]
    for case in bindings:
        if CONTRACT.accepts_job_event(case["value"], case["binding"]) is not case["valid"]:
            raise RuntimeError("BUNDLED_BINDING_MISMATCH")
    counts["trustedBindings"] = len(bindings)
    frames = json.loads((CONTRACT.ROOT / "frame-fixtures.json").read_text(encoding="utf-8"))[
        "cases"
    ]
    for case in frames:
        reader = JsonlReader(case.get("maxBytes", 262144))
        values = []
        errors = []
        for chunk in case["chunks"]:
            try:
                values.extend(reader.feed(bytes.fromhex(chunk)))
            except ProtocolFault as error:
                values.extend(error.frames)
                errors.append("frame" if case["name"] == "append before byte limit" else "json")
        if case["end"]:
            try:
                reader.finish()
            except ProtocolFault as error:
                values.extend(error.frames)
                errors.append("json")
        if values != case["expectedFrames"] or errors != case["expectedErrors"]:
            raise RuntimeError("BUNDLED_FRAME_MISMATCH")
    counts["rawFrames"] = len(frames)
    print(json.dumps({"status": "passed", "counts": counts}, separators=(",", ":")), flush=True)
