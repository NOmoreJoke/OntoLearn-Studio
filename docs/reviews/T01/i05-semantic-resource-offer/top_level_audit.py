"""Lexical top-level calls including branches; never executes reviewed modules."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REF = "6891a5842302859a531cf82767c5a482417bc274"


class Calls(ast.NodeVisitor):
    def __init__(self):
        self.calls = []

    def visit_Call(self, node):
        self.calls.append({"line": node.lineno, "expression": ast.unparse(node)})
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        for expression in node.decorator_list + node.args.defaults + [
            v for v in node.args.kw_defaults if v is not None
        ]:
            self.visit(expression)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node):
        for expression in node.args.defaults + [v for v in node.args.kw_defaults if v is not None]:
            self.visit(expression)


result = json.loads((HERE / "static-audit.json").read_bytes())
records = []
sources = result["closure"]["identities"] + [
    result["sharedResourceIdentities"][0]["supplier"]
]
for item in sources:
    raw = subprocess.check_output(["git", "show", REF + ":" + item["path"]], cwd=HERE)
    assert hashlib.sha256(raw).hexdigest() == item["sha256"]
    visitor = Calls()
    visitor.visit(ast.parse(raw))
    records.append({"source": item, "lexicalTopLevelCalls": visitor.calls})
output = HERE / "top-level-static.json"
output.write_text(json.dumps({
    "method": "AST top-level, class bodies/decorators/defaults and lexical conditional branches; skip function/lambda bodies. Does not resolve imported stdlib/third-party side effects, dynamic calls, annotations or execution branches. Not runtime/heap evidence.",
    "sources": records,
    "manualRelevantSideEffects": [
        "resources top level dynamically executes original checker, rereads registry bytes, hashes lock",
        "checker top level reads three JSON resources and defines constants/functions",
        "semantic_offline top level registers sys.addaudithook and rdflib.term log filter; not installed/executed by this review",
        "main/resource_manifest lexical definition is not a top-level invocation or permission to call"
    ]
}, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(output), "bytes": output.stat().st_size,
                  "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "sources": len(records)}))
