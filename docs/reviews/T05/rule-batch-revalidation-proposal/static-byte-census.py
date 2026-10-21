"""Static byte-size arithmetic only; no product imports, parsing, matching or execution.

Fields follow fixed 1e3e0ee typed _walk. Each returned int is a byte count,
not an encoded product value. Exact for the ASCII-only witness below.
"""
import json
from pathlib import Path


def text(s):
    assert all(32 <= ord(c) < 127 and c not in '\\"' for c in s)
    return len(s) + 2


def seq(*sizes):
    return 2 + sum(n + 1 for n in sizes)


def record(tag, **sizes):
    return 2 + text(tag) + sum(text(k) + v for k, v in sizes.items())


NULL = 4
P = 'OntoLearn-rule-comparison-profile/1'
source = record('SourceRecord', reference=NULL, digest=NULL, revision=NULL, text=40002)
variable = record('Variable', name=text('?x'))
catalog = record('Catalog', classes=seq(), object_properties=seq(),
                 data_properties=seq(text('urn:p'), text('urn:q')))


def term(kind, lexical):
    return record('TermInput', kind=text(kind), lexical_form=text(lexical),
                  datatype_iri=NULL, language_raw=NULL, source=NULL)


def value(kind, lexical):
    return record('ProfileValue', term=term(kind, lexical),
                  domain=text('I' if kind == 'iri' else 'S'), value=text(lexical),
                  language=text(''))


def triple(s, p, o):
    return record('Triple', subject=s, predicate=p, object=o)


p, q, v, ok = term('iri', 'urn:p'), term('iri', 'urn:q'), term('literal', 'v'), term('literal', 'ok')
vp, vq, vv, vok = value('iri', 'urn:p'), value('iri', 'urn:q'), value('literal', 'v'), value('literal', 'ok')
when = triple(variable, p, v)
head = triple(variable, q, ok)
spec = record('RuleSpec', rule_id=text('r'), when=seq(when), comparisons=seq(),
              heads=seq(head), source=source, revision=NULL, definition_digest=NULL, policy=text(P))
compiled = record('_CompiledRule', spec=spec, constants=seq(seq(p, vp), seq(v, vv), seq(q, vq), seq(ok, vok)),
                  variables=seq(text('?x')), prepared_digest=66)
plan = seq(seq(compiled), catalog)
definitions_and_catalog = seq(seq(spec), catalog)
compile_parsing = 2 * sum((p + vp, q + vq, v + vv, ok + vok))
compile_input = definitions_and_catalog + compile_parsing + spec + plan
matches = []
groups = []
facts = []
eval_parsing = 0
term_key_checks = 0
for suffix in ('1', '2'):
    s = term('iri', 'urn:s' + suffix)
    vs = value('iri', 'urn:s' + suffix)
    w = triple(s, p, v)
    h = triple(s, q, ok)
    bindings = seq(seq(text('?x'), s))
    proof = seq(seq(text('f' + suffix)))
    matches.append(record('BindingMatch', rule_id=text('r'), bindings=bindings, when=seq(w), proof_leaves=proof))
    groups.append(record('PreparedFiring', rule_id=text('r'), bindings=bindings, when=seq(w),
                         proof_leaves=proof, comparisons=seq(),
                         heads=seq(record('HeadEvidence', index=5, triple=h)),
                         basis=seq(text('f' + suffix)), source=source, revision=NULL,
                         definition_digest=66, policy=text(P)))
    facts.append(h)
    # Direct census of the fixed source, no calls to parse_value/_one:
    eval_parsing += 8 * (s + vs) + 4 * (p + vp) + 4 * (v + vv) + 2 * (q + vq) + 2 * (ok + vok)
    term_key_checks += 5 * vs + 3 * vp + 3 * vv + vq + vok
match_input = seq(*matches)
evaluate_input = plan + match_input + eval_parsing + term_key_checks
payload = seq(text(P), seq(*groups), seq(*facts))
result = {
    'kind': 'static ASCII byte-count arithmetic; not a product execution',
    'fixedCommit': '1e3e0ee1d9d5b70f1f59233d0a3c64f6d85fd2cb',
    'sourceTextCharacters': 40000,
    'compileInputBytes': compile_input,
    'evaluateAdditionalInputBytes': evaluate_input,
    'combinedExecutionInputBytes': compile_input + evaluate_input,
    'executionOutputBytes': payload,
    'singleGroupLoopInputLowerBoundBytes': compile_input + 2 * plan + sum(groups),
    'singleGroupLoopOutputBytes': 2 * sum(groups),
    'sizes': {'planEncoding': plan, 'specEncoding': spec, 'matchesEncoding': match_input,
              'groupEncoding': groups, 'compileParseAndIssuance': compile_parsing,
              'evaluateParseAndIssuance': eval_parsing, 'evaluateTermKeyIssuance': term_key_checks},
    'limitations': 'Work/trace counts and actual success/resource failures are not run; proposed implementation tests must execute this exact witness. Input/output byte obstruction is statically proven.'
}
Path(__file__).with_name('static-byte-census.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
