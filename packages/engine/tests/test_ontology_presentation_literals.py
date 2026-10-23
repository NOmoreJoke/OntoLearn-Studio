"""Actual RDFLib parity for the browser's metadata literal serializer, not an App run."""

import json
import subprocess
from pathlib import Path

from rdflib import Literal


def test_browser_metadata_literals_match_actual_rdflib():
    root = Path(__file__).resolve().parents[3]
    module = root / "apps/desktop/src/renderer/src/ontology/mainline-ontology.ts"
    values = [
        ("设备", "zh"),
        ("Equipment", "en"),
        ("", ""),
        ("a\tb", ""),
        ("a\rb", "zh"),
        ('a"b\\c', "en"),
        ("a\nb", "zh"),
        ('line\n"', ""),
        ('line\n"""', "en"),
        ('line\n\\"', "zh-cn"),
        ("😀\ue000\ufeff", ""),
        ("line\r\nnext\t", ""),
    ]
    script = (
        f"import {{ literalN3 }} from {json.dumps(module.as_uri())};"
        "let input='';for await(const part of process.stdin)input+=part;"
        "process.stdout.write(JSON.stringify(JSON.parse(input).map(([text,lang])=>literalN3(text,lang))));"
    )
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        input=json.dumps(values),
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
        cwd=root,
    )
    expected = [Literal(text, lang=lang or None).n3() for text, lang in values]
    assert json.loads(result.stdout) == expected
