"""D1 third-party evidence only; no OntoLearn or I05 implementation imports."""

import base64
import csv
import hashlib
import importlib
import importlib.metadata
import io
import json
import sys
import tomllib
import urllib.request
import zipfile
from pathlib import Path

from packaging.requirements import Requirement
from packaging.tags import parse_tag
from packaging.utils import parse_wheel_filename
from packaging.version import Version

EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[3]
EXPECTED = {
    "pyshacl": "0.30.1",
    "pyparsing": "3.3.3",
    "rdflib": "7.6.0",
    "owlrl": "7.6.2",
    "prettytable": "3.18.0",
    "wcwidth": "0.9.2",
    "html5rdf": "1.2.1",
    "packaging": "26.3",
}
LOCK = {item["name"]: item for item in tomllib.loads((ROOT / "uv.lock").read_text())["package"]}
assert Path(sys.prefix).resolve() == ROOT / ".venv"
ARTIFACTS = ROOT / "build/d1-distributions"
ARTIFACTS.mkdir(parents=True, exist_ok=True)
records = []
for name, version in EXPECTED.items():
    distribution = importlib.metadata.distribution(name)
    assert distribution.version == version == LOCK[name]["version"]
    module = importlib.import_module(name)
    module_path = Path(module.__file__).resolve()
    assert module_path.is_relative_to(ROOT / ".venv"), module_path
    wheel_metadata = distribution.read_text("WHEEL")
    tags = set()
    for line in wheel_metadata.splitlines():
        if line.startswith("Tag: "):
            tags.update(parse_tag(line[5:]))
    compatible = [
        wheel
        for wheel in LOCK[name]["wheels"]
        if parse_wheel_filename(wheel["url"].rsplit("/", 1)[-1])[3] == tags
    ]
    assert len(compatible) == 1, (name, tags, compatible)
    artifact = compatible[0]
    filename = artifact["url"].rsplit("/", 1)[-1]
    target = ARTIFACTS / filename
    if target.exists():
        content = target.read_bytes()
        acquisition = "reuse immutable artifact fetched during this D1 attempt"
    else:
        with urllib.request.urlopen(artifact["url"], timeout=30) as response:
            content = response.read()
        acquisition = "download from exact lock URL"
    digest = hashlib.sha256(content).hexdigest()
    assert artifact["hash"] == "sha256:" + digest
    assert len(content) == artifact["size"]
    if not target.exists():
        target.write_bytes(content)
    license_files = []
    wheel_files_matched = 0
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        for entry in archive.namelist():
            if entry.endswith("/") or entry.endswith(".dist-info/RECORD"):
                continue
            installed = Path(distribution.locate_file(entry))
            assert installed.is_file(), (name, entry)
            data = archive.read(entry)
            assert installed.read_bytes() == data, (name, entry)
            wheel_files_matched += 1
            leaf = Path(entry).name.lower()
            if "license" in leaf or "licence" in leaf or "copying" in leaf or "notice" in leaf:
                license_files.append(
                    {
                        "path": entry,
                        "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "firstLines": data.decode("utf-8", errors="replace").splitlines()[:5],
                    }
                )
    assert license_files, name
    record_hashes_checked = 0
    for location, recorded_hash, size in csv.reader(io.StringIO(distribution.read_text("RECORD"))):
        if not recorded_hash:
            continue
        algorithm, encoded = recorded_hash.split("=", 1)
        assert algorithm == "sha256"
        data = Path(distribution.locate_file(location)).read_bytes()
        actual = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
        assert encoded == actual, (name, location)
        assert not size or len(data) == int(size), (name, location)
        record_hashes_checked += 1
    active_dependencies = []
    for requirement in distribution.requires or []:
        parsed = Requirement(requirement)
        extra = "html" if name == "rdflib" else ""
        if parsed.marker is not None and not parsed.marker.evaluate({"extra": extra}):
            continue
        installed_version = importlib.metadata.version(parsed.name)
        assert Version(installed_version) in parsed.specifier, requirement
        active_dependencies.append(
            {"requirement": requirement, "installedVersion": installed_version, "extra": extra}
        )
    metadata = distribution.read_text("METADATA").encode()
    records.append(
        {
            "name": name,
            "version": version,
            "module": module.__name__,
            "modulePath": str(module_path),
            "metadataSha256": hashlib.sha256(metadata).hexdigest(),
            "licenseExpression": distribution.metadata.get("License-Expression"),
            "licenseField": distribution.metadata.get("License"),
            "licenseClassifiers": [
                value
                for value in distribution.metadata.get_all("Classifier", [])
                if value.startswith("License ::")
            ],
            "licenseFiles": license_files,
            "activeDependencies": active_dependencies,
            "installedWheelTags": sorted(str(tag) for tag in tags),
            "downloadedArtifact": artifact,
            "downloadedSha256": digest,
            "artifactAcquisition": acquisition,
            "allWheelMembersMatchInstalled": wheel_files_matched,
            "installedRecordHashesChecked": record_hashes_checked,
        }
    )

# Finite dependency-only samples; these are not an I05 reason/probe or product oracle.
import html5rdf  # noqa: E402
import owlrl  # noqa: E402
import pyparsing  # noqa: E402
import pyshacl  # noqa: E402
from prettytable import PrettyTable  # noqa: E402
from rdflib import RDF, RDFS, SH, Graph, Literal, Namespace  # noqa: E402
from wcwidth import wcswidth  # noqa: E402

expression = (
    pyparsing.Word(pyparsing.alphas) + pyparsing.Suppress("=") + pyparsing.pyparsing_common.integer
)
parsed = expression.parse_string("count=7", parse_all=True).as_list()
assert parsed == ["count", 7]
html_tree = html5rdf.HTMLParser().parse("<html><body><p>D1</p></body></html>")
assert any(node.text == "D1" for node in html_tree.iter())
ex = Namespace("urn:d1:")
graph = Graph()
graph.add((ex.Child, RDFS.subClassOf, ex.Parent))
graph.add((ex.item, RDF.type, ex.Child))
owlrl.DeductiveClosure(owlrl.RDFS_Semantics).expand(graph)
assert (ex.item, RDF.type, ex.Parent) in graph
shape = Graph().parse(
    data="""@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <urn:d1:> .
ex:Shape a sh:NodeShape; sh:targetNode ex:item;
sh:property [ sh:path ex:label; sh:minCount 1 ] .
""",
    format="turtle",
)
data = Graph()
data.add((ex.item, ex.label, Literal("D1")))
positive, positive_report, _ = pyshacl.validate(data, shacl_graph=shape)
negative, negative_report, _ = pyshacl.validate(Graph(), shacl_graph=shape)
assert positive is True and negative is False
assert len(list(positive_report.subjects(RDF.type, SH.ValidationResult))) == 0
assert len(list(negative_report.subjects(RDF.type, SH.ValidationResult))) == 1
table = PrettyTable(["case", "value"])
table.add_row(["d1", 7])
rendered_table = table.get_string()
assert "d1" in rendered_table and "7" in rendered_table
assert wcswidth("\u4e2dA") == 3
assert Version("7.6.0") > Version("7.5.0")
assert not any(name.startswith("ontolearn_engine") for name in sys.modules)
result = {
    "scope": "D1 actual third-party dependency evidence only; no I05 product or package execution",
    "executable": sys.executable,
    "prefix": sys.prefix,
    "basePrefix": sys.base_prefix,
    "python": sys.version,
    "lockSha256": hashlib.sha256((ROOT / "uv.lock").read_bytes()).hexdigest(),
    "distributions": records,
    "smoke": {
        "pyparsingInput": "count=7",
        "pyparsingOutput": parsed,
        "html5rdfText": "D1",
        "owlrlParentTypePresent": True,
        "pyshaclPositiveConforms": positive,
        "pyshaclNegativeConforms": negative,
        "pyshaclNegativeViolationCount": 1,
        "prettytableOutput": rendered_table,
        "wcwidthInput": "\u4e2dA",
        "wcwidthColumns": 3,
        "packagingVersionComparison": True,
    },
    "ontolearnImported": False,
    "archiveOrNativeOrI05ProbeRun": False,
}
output = EVIDENCE / "dependency-evidence.json"
assert not output.exists(), "preserve earlier result"
output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
