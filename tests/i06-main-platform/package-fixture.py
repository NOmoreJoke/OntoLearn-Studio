"""Fresh native-only fixture, using the real approved worker plus a real atomic Store commit."""

import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location(
    "i06_main_fixture", Path(__file__).with_name("fixture.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
directory = Path(sys.argv[1])
module.prepare(directory, "fields")
fixture = json.loads((directory / "fixture.json").read_text())
evidence = json.loads((directory / "fixture-evidence.json").read_text())
fixture["startRequests"] = [evidence["atomic"]]
(directory / "fixture.json").write_text(json.dumps(fixture, indent=2) + "\n")

fixture.pop("modelFieldPolicy", None)
(directory / "fixture.json").write_text(json.dumps(fixture, indent=2) + "\n")
