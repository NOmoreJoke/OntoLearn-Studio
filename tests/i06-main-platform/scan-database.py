"""Read actual closed SQLite fields, excluding gateway writes and allowing existing source rows."""

import json
import sqlite3
import sys
from pathlib import Path

connection = sqlite3.connect(Path(sys.argv[1]).as_uri() + "?mode=ro", uri=True)
require_source = sys.argv[2] == "require-source"
bodies = [Path(name).read_bytes() for name in sys.argv[3:]]
rows = 0
source_seen = False
try:
    tables = [
        row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
    ]
    for table in tables:
        quoted = '"' + table.replace('"', '""') + '"'
        for row in connection.execute("SELECT * FROM " + quoted):
            rows += 1
            for value in row:
                raw = value if isinstance(value, bytes) else str(value).encode()
                if b"PUBLIC_VALUE_" in raw:
                    source_seen = True
                if b"I06_MAIN_SYNTHETIC_SECRET_" in raw or b"I06_RESPONSE_PRIVATE_MARKER_" in raw:
                    raise RuntimeError("CREDENTIAL_OR_MODEL_RESPONSE_IN_PROJECT_DATABASE")
                if any(body and body in raw for body in bodies):
                    raise RuntimeError("COMPLETE_GATEWAY_PAYLOAD_IN_PROJECT_DATABASE")
    if require_source and not source_seen:
        raise RuntimeError("EXPECTED_REAL_SOURCE_ROWS_ABSENT")
    print(
        json.dumps(
            {
                "result": "passed",
                "tables": len(tables),
                "rows": rows,
                "expectedSourceRowsPresent": source_seen,
                "credentialModelResponseOrExactOutboundPayloadPresent": False,
            }
        )
    )
finally:
    connection.close()
