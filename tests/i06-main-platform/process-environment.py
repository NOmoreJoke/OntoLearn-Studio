"""Read only this launched Electron main's real coordinator/worker descendants while work runs."""

import json
import sys
from pathlib import Path

parent = int(sys.argv[1])
processes = {}
for directory in Path("/proc").iterdir():
    if not directory.name.isdigit():
        continue
    try:
        status = (directory / "status").read_text()
        ppid = int(
            next(line.split()[1] for line in status.splitlines() if line.startswith("PPid:"))
        )
        processes[int(directory.name)] = (ppid, directory)
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        continue
descendants = {parent}
for _ in range(8):
    descendants.update(pid for pid, (ppid, _) in processes.items() if ppid in descendants)
found = []
for pid in sorted(descendants - {parent}):
    _, directory = processes[pid]
    try:
        command = (directory / "cmdline").read_bytes()
        if b"ontolearn_engine" not in command:
            continue
        environment = (directory / "environ").read_bytes()
        found.append(
            {
                "pid": pid,
                "role": "worker" if b"ontolearn_engine.worker" in command else "coordinator",
                "pythonIsOwnVenv": command.startswith(b"/workspace/.venv/bin/python\0"),
                "secretPrefixAbsent": b"I06_MAIN_SYNTHETIC_SECRET_" not in environment,
                "nodeExtraCAAbsent": b"NODE_EXTRA_CA_CERTS=" not in environment,
                "proxyVariablesAbsent": all(
                    token not in environment
                    for token in (b"HTTP_PROXY=", b"HTTPS_PROXY=", b"ALL_PROXY=")
                ),
            }
        )
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        continue
print(json.dumps(found))
