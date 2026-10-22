#!/usr/bin/env python3
"""Build an external semantic oracle from sealed data and independent expectations.

No product imports, subprocesses, RDF libraries, observation readers, or JSONL adapter.
The small Turtle decoder is only a finite fixture decoder, not a product parser.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from collections import Counter
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/reviews/T05/source-package-oracle'
INPUTS = EVIDENCE / 'inputs'
OUTPUT = ROOT / 'tests/fixtures/quality/i05-source-package-oracle'
ASSET = 'i05-source-package-parity-inputs.json'
DESCRIPTOR = 'i05-source-package-parity-manifest.json'
PINS = {
    'product-cases.json': (188023, 'a774a8d9615fd6fcacf81b567dff96c5cb202b6c35ef2d74a2943fe12b3e9baa'),
    ASSET: (8205267, '47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa'),
    DESCRIPTOR: (21202, '0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a'),
    'real-executor-acceptance-inputs.json': (767826, '87220503f9983146c974fe3e35025d520cad70e54fdd994aebfa86fb1ff7259f'),
    'explanation-goldens.json': (11584, '68bc6848ad05b7cca01f37368a15b9e961a78a6a877b841f08cafa2a2fba36d9'),
    'consumer-C-goldens.json': (8163, 'c25e7afcc593a7be09fc8b2ca29af9cff28a7a1e030a13b98aa5e7d88d596440'),
}
DOC_PINS = {
    'contract.md': (60953, 'd2cdc2e6017ad0257f30611d2928a60a116f4dc389cacdfc977c17efe13e2a23'),
    'semantic-boundaries.md': (23814, 'a1e279f8d55a82af12cf27dbf11e71b78a11005b310748c3a5b3496062fae61d'),
    'date-policy.md': (22938, '1457aea0ba8b15ed0d137492dd648bc846e9757e067cf2cf506b70949aa996cc'),
    'q6-profile.md': (16428, '9259f4ac6622857182570509378afb6c96ab5c4dc19d2e887db559c27a282427'),
    'q6-mechanism.md': (26782, '8008e906c7b20dbd9c9ba2d0a1bce0661ec32336f78d477831103cbc9bc27424'),
    'directsteps-contract.md': (34958, 'c947430801e6b3cca113c15a856704c3d5bed418efa9083d67819830a6961fba'),
    'native-child-declaration-reference.json': (2087, '71f64ab22f60fe6407e72f97a1296f4863fdcf8dc22e583425366d220a3dba74'),
    'pre-registered-date-assertions.py.raw': (1309, '6e67da970aac72b3d7e56e695d41a3f34ea6e57f7621235c42c589815d194795'),
}
SOURCE_PATHS = {
    ASSET: 'packages/engine/src/ontolearn_engine/probe_inputs/' + ASSET,
    DESCRIPTOR: 'packages/engine/src/ontolearn_engine/probe_inputs/' + DESCRIPTOR,
    'product-cases.json': 'tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/cases.json',
    'real-executor-acceptance-inputs.json': 'tests/fixtures/quality/real-executor-acceptance-inputs.json',
    'explanation-goldens.json': 'docs/reviews/T05/profile-M1-math-explanation-input-contract/explanation-goldens.json',
    'consumer-C-goldens.json': 'docs/reviews/T05/profile-M1-math-explanation-input-contract/consumer-C-goldens.json',
}

RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
RDFS = 'http://www.w3.org/2000/01/rdf-schema#'
XSD = 'http://www.w3.org/2001/XMLSchema#'
SH = 'http://www.w3.org/ns/shacl#'
OWL = 'http://www.w3.org/2002/07/owl#'


def canonical(value):
    # ASCII preserves intentional isolated-surrogate rejection inputs losslessly.
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def read_pinned(name):
    raw = (INPUTS / name).read_bytes()
    size, sha = PINS[name]
    if len(raw) != size or digest(raw) != sha:
        raise ValueError('fixed input identity mismatch: ' + name)
    return strict_json(raw)


def iri(value):
    return {'kind': 'iri', 'value': value}


def literal(value, datatype=None, language=None):
    return {'kind': 'literal', 'lexical': value,
            'datatype': RDF + 'langString' if language else datatype or XSD + 'string',
            'language': language.lower() if language else None}


def term_key(term):
    return canonical(term)


def ordered_set(values):
    return [json.loads(k) for k in sorted({canonical(v) for v in values})]


def n3_term(token):
    if token.startswith('<') and token.endswith('>'):
        return iri(token[1:-1])
    match = re.fullmatch(r'("(?:\\.|[^"\\])*")(?:(@[^ ]+)|\^\^<([^>]+)>)?', token, re.S)
    if match:
        return literal(json.loads(match[1]), match[3], match[2][1:] if match[2] else None)
    raise ValueError('unsupported independent N3 token: ' + token)


class FixtureTurtle:
    """Decode only the explicit finite Turtle grammar used by valid sealed fixtures."""
    token = re.compile(r'\s+|\#[^\n]*|<[^>]*>|[+-]?(?:\d+\.\d+|\.\d+|\d+)[eE][+-]?\d+|[+-]?(?:\d+\.\d+|\.\d+)|"(?:\\.|[^"\\])*"|\^\^|@[\w-]+|[.;,()\[\]]|[^\s.;,()\[\]<>"^]+', re.S)

    def __init__(self, text):
        self.tokens = []
        position = 0
        for match in self.token.finditer(text):
            if match.start() != position:
                raise ValueError('fixture token gap')
            position = match.end()
            token = match[0]
            if not token.isspace() and not token.startswith('#'):
                self.tokens.append(token)
        if position != len(text):
            raise ValueError('fixture trailing token gap')
        self.i = 0
        self.prefix = {'rdf': RDF, 'rdfs': RDFS, 'xsd': XSD, 'sh': SH, 'owl': OWL}
        self.graph = []
        self.blank = 0

    def pop(self, expected=None):
        if self.i == len(self.tokens):
            raise ValueError('fixture unexpectedly ended')
        token = self.tokens[self.i]
        self.i += 1
        if expected is not None and token != expected:
            raise ValueError('fixture expected ' + expected + ' got ' + token)
        return token

    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def term(self):
        token = self.pop()
        if token == '(':
            items = []
            while self.peek() != ')':
                items.append(self.term())
            self.pop(')')
            tail = iri(RDF + 'nil')
            for item in reversed(items):
                self.blank += 1
                node = {'kind': 'blank', 'label': 'list-' + str(self.blank)}
                self.graph += [[node, iri(RDF + 'first'), item], [node, iri(RDF + 'rest'), tail]]
                tail = node
            return tail
        if token.startswith('<'):
            return iri(token[1:-1])
        if token.startswith('"'):
            text = json.loads(token)
            datatype, language = None, None
            if self.peek() == '^^':
                self.pop()
                datatype = self.term()['value']
            elif self.peek() and self.peek().startswith('@'):
                language = self.pop()[1:]
            return literal(text, datatype, language)
        if token == 'a':
            return iri(RDF + 'type')
        if token in ('true', 'false'):
            return literal(token, XSD + 'boolean')
        if re.fullmatch(r'[+-]?\d+', token):
            return literal(token, XSD + 'integer')
        if re.fullmatch(r'[+-]?(?:\d+\.\d+|\.\d+|\d+)[eE][+-]?\d+', token):
            return literal(token, XSD + 'double')
        if re.fullmatch(r'[+-]?(?:\d+\.\d+|\.\d+)', token):
            return literal(token, XSD + 'decimal')
        if ':' in token:
            prefix, value = token.split(':', 1)
            if prefix in self.prefix:
                return iri(self.prefix[prefix] + value)
        raise ValueError('unsupported finite Turtle term: ' + token)

    def parse(self):
        while self.peek() is not None:
            if self.peek().lower() in ('@prefix', 'prefix'):
                directive = self.pop().lower()
                prefix = self.pop()
                self.prefix[prefix[:-1]] = self.pop()[1:-1]
                if directive == '@prefix':
                    self.pop('.')
                continue
            subject = self.term()
            while True:
                predicate = self.term()
                while True:
                    self.graph.append([subject, predicate, self.term()])
                    if self.peek() != ',':
                        break
                    self.pop(',')
                if self.peek() != ';':
                    break
                self.pop(';')
                if self.peek() == '.':
                    break
            self.pop('.')
        return ordered_set(self.graph)


def turtle(text):
    return FixtureTurtle(text).parse()


def values(graph, subject, predicate):
    return [o for s, p, o in graph if s == subject and p == iri(predicate)]


def scalar(term):
    if term['kind'] != 'literal':
        return None
    datatype, lexical = term['datatype'], term['lexical']
    if datatype in [XSD + n for n in ('integer', 'int', 'nonNegativeInteger', 'decimal', 'float', 'double')]:
        return Decimal(lexical)
    if datatype == XSD + 'date':
        return date.fromisoformat(lexical[:-1])
    if datatype == XSD + 'dateTime':
        return datetime.fromisoformat(lexical.replace('Z', '+00:00'))
    return None


def shacl_report(data, shapes):
    """Independent declarative evaluation of the six explicitly admitted templates."""
    rows = []
    def violation(focus, path, shape, component, value=None):
        rows.append({'focus': focus, 'path': path, 'value': value, 'sourceShape': shape,
                     'constraint': iri(SH + component + 'ConstraintComponent'), 'severity': iri(SH + 'Violation')})
    nodes = [s for s, p, o in shapes if p == iri(RDF + 'type') and o == iri(SH + 'NodeShape')]
    for node in nodes:
        target, = values(shapes, node, SH + 'targetClass')
        focuses = [s for s, p, o in data if p == iri(RDF + 'type') and o == target]
        for prop in values(shapes, node, SH + 'property'):
            path, = values(shapes, prop, SH + 'path')
            for focus in focuses:
                objects = values(data, focus, path['value'])
                for count_name, valid in [('minCount', lambda n, b: n >= b), ('maxCount', lambda n, b: n <= b)]:
                    for bound in values(shapes, prop, SH + count_name):
                        if not valid(len(objects), int(bound['lexical'])):
                            violation(focus, path, prop, count_name[0].upper() + count_name[1:])
                for value in objects:
                    for bound in values(shapes, prop, SH + 'datatype'):
                        good = value['kind'] == 'literal' and value['datatype'] == bound['value']
                        if good and value['datatype'] == XSD + 'integer':
                            good = re.fullmatch(r'[+-]?\d+', value['lexical']) is not None
                        if not good:
                            violation(focus, path, prop, 'Datatype', value)
                    for first in values(shapes, prop, SH + 'in'):
                        allowed, current = [], first
                        while current != iri(RDF + 'nil'):
                            item, = values(shapes, current, RDF + 'first')
                            allowed.append(item)
                            current, = values(shapes, current, RDF + 'rest')
                        if value not in allowed:
                            violation(focus, path, prop, 'In', value)
                    for name, valid in [('minInclusive', lambda a, b: a >= b), ('maxInclusive', lambda a, b: a <= b)]:
                        for bound in values(shapes, prop, SH + name):
                            try:
                                a, b = scalar(value), scalar(bound)
                                accepted = a is not None and b is not None and valid(a, b)
                            except (TypeError, ValueError, InvalidOperation):
                                accepted = False
                            if not accepted:
                                violation(focus, path, prop, name[0].upper() + name[1:], value)
    return {'conforms': not rows, 'violations': sorted(rows, key=canonical)}


def graph_from_records(records):
    return ordered_set([[iri(r['triple']['subject']), iri(r['triple']['predicate']), n3_term(r['triple']['object'])] for r in records])



def profile_value(token):
    term = n3_term(token)
    if term['kind'] == 'iri':
        return {'domain': 'I', 'value': term['value'], 'rdfTerm': term}
    if term['datatype'] in (XSD + 'integer', XSD + 'int', XSD + 'nonNegativeInteger'):
        return {'domain': 'N', 'value': {'numerator': int(term['lexical']), 'denominator': 1, 'negativeZero': False}, 'rdfTerm': term}
    if term['datatype'] == XSD + 'boolean':
        return {'domain': 'B', 'value': term['lexical'] in ('true', '1'), 'rdfTerm': term}
    if term['datatype'] in (XSD + 'string', RDF + 'langString'):
        return {'domain': 'L' if term['language'] else 'S', 'value': term['lexical'], 'rdfTerm': term}
    raise ValueError('No independently declared profile scalar for this corpus term: ' + token)

def profile_expected(dataset, golden, observation):
    data = dataset['input']
    triples = golden['triples']
    asserted, ontology = graph_from_records(data['asserted']), graph_from_records(data['ontology'])
    def expand(ids):
        return ordered_set([[n3_term(t) for t in triples[i]['n3']] for i in ids])
    definitions = [d['definitionJsonValueSha256'] for d in data['definitions']]
    candidates = []
    for name, graph in golden['graphs'].items():
        graph_defs = [digest(json.dumps(golden['ruleDefinitions'][r]['definition'], ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()) for r in graph['ruleDefinitionRefs']]
        if expand(graph['assertedTripleIds']) == asserted and expand(graph['ontologyTripleIds']) == ontology and graph_defs == definitions:
            candidates.append(name)
    fragment = ':event-fragment:round:' in observation['id']
    if fragment:
        round_number = int(observation['id'].rsplit(':', 1)[1])
        candidates = ['e5-c3-r' + str(round_number) + '-event']
    if not candidates:
        raise ValueError('no independently hand-selected graph: ' + observation['id'])
    graph = golden['graphs'][sorted(candidates)[0]]
    matches = []
    for ref in graph['matchRefs']:
        match = copy.deepcopy(golden['matches'][ref])
        for key in ('whenTripleIdsInDefinitionOrder', 'leafBasisTripleIds'):
            match[key.removesuffix('IdsInDefinitionOrder').removesuffix('Ids')] = [
                [n3_term(v) for v in triples[t]['n3']] for t in match[key]
            ]
        match['heads'] = [{'headIndex': h['headIndex'], 'triple': [n3_term(v) for v in triples[h['tripleId']]['n3']]} for h in match['heads']]
        match['typedBindings'] = [[variable, profile_value(token)] for variable, token in sorted(match['bindings'].items())]
        match['typedWhen'] = [[profile_value(v) for v in triples[t]['n3']] for t in match['whenTripleIdsInDefinitionOrder']]
        match['typedComparisons'] = [{
            'comparisonIndex': c['comparisonIndex'], 'conditionIndex': c['conditionIndex'],
            'operator': c['operator'], 'left': profile_value(c['left']), 'right': profile_value(c['right']),
            'result': c['independentResult'],
        } for c in match['comparisons']]
        match['typedHeads'] = [{'headIndex': h['headIndex'], 'triple': [profile_value(v) for v in triples[h['tripleId']]['n3']]} for h in golden['matches'][ref]['heads']]
        match['typedBasis'] = ordered_set([[profile_value(v) for v in triples[t]['n3']] for t in match['leafBasisTripleIds']])
        matches.append({'independentMatchRef': ref, **match})
    return {
        'asserted': asserted, 'ontology': ontology, 'rdfsAdded': expand(graph['rdfsAddedTripleIds']),
        'customOutput': expand(graph['customOutputTripleIds']), 'derivedUnion': expand(graph['derivedUnionTripleIds']),
        'warnings': graph['expectedSemanticWarnings'], 'matches': matches,
        'definitions': [golden['ruleDefinitions'][r] for r in graph['ruleDefinitionRefs']],
        'rdfsWitnesses': [golden['rdfsWitnesses'][r] for r in graph['rdfsWitnessRefs']],
        'independentGraphPointers': ['/graphs/' + n for n in sorted(candidates)],
        'fragmentOnly': fragment,
        'disabledRuleIds': data['disabled_rule_ids'],
        'definitionInputOrder': [{'definitionOrdinal': i, 'definitionJsonValueSha256': d['definitionJsonValueSha256']} for i, d in enumerate(data['definitions'])],
    }


def rejection(reason, phase, validator=0, exception='SemanticError'):
    return {'semanticState': 'known-rejection', 'exception': exception, 'reason': reason,
            'phase': phase, 'validatorCalls': validator, 'report': None, 'partialView': None}


def fixed_query(case_id):
    learning = 'urn:ontolearn:learning:'
    ont = 'urn:ontolearn:'
    names = {
        'C-query-numeric-promotion': (['s'], [[iri('urn:m1:s')]]),
        'C-query-type-error': (['s'], []),
        'query/words-in-string': (['x'], [[literal('SERVICE FROM')]]),
        'query/optional-unbound': (['s', 'missing'], [[iri('urn:case:0:equipment/' + i), None] for i in ('001', '002', '003')]),
        'query/count': (['n'], [[literal('3', XSD + 'integer')]]),
        'query/order-tie': (['s', 'v'], [[iri('urn:' + s), literal(v, XSD + 'integer')] for s, v in [('a', '1'), ('b', '1'), ('c', '2')]]),
        'query/filter': (['s'], [[iri('urn:case:0:alarm/' + s)] for s in ('A01', 'A02')]),
        'query/string-distinct': (['v'], [[literal('x')]]),
        'query/string-count': (['n'], [[literal('1', XSD + 'integer')]]),
        'original-Q01': (['alarm'], [[iri(learning + 'alarm/A01')]]),
        'original-Q02': (['alarm'], []),
    }
    if case_id == 'query/ask':
        return {'type': 'ASK', 'value': True}
    if case_id.startswith('query/string-expression-'):
        return {'type': 'SELECT', 'variables': ['s'], 'rows': [[iri(ont + s)] for s in ('bothString', 'plainString', 'typedString')]}
    if case_id in names:
        variables, rows = names[case_id]
        return {'type': 'SELECT', 'variables': variables, 'rows': rows}
    return None


def declared_rejection(o):
    key, family = o['id'], o['family']
    def result(reason, phase='entry', exception='SemanticError', pending=None):
        r = rejection(reason, phase, exception=exception)
        return r, pending or []
    if key.startswith('shacl-policy/'):
        if 'missing-' in key:
            return result(None, 'argument-binding', 'TypeError')
        return result('SCOPE_SELECTION_TYPE_INVALID', 'policy-selection')
    direct = {
        'utc-date/blank': ('UNSUPPORTED_BLANK_NODE', 'parse-data'),
        'utc-date/unknown-datatype': ('UNSUPPORTED_LITERAL_DATATYPE', 'parse-data'),
        'utc-date/nonfinite': ('UNSUPPORTED_NONFINITE_LITERAL', 'parse-data'),
        'utc-date/imports': ('EXTERNAL_ACCESS_DENIED', 'parse-data'),
        'utc-date/relative': ('ABSOLUTE_IRI_REQUIRED', 'parse-data'),
        'utc-date/bad-iri': ('ABSOLUTE_IRI_REQUIRED', 'parse-data'),
        'utc-date/path-arity': ('INVALID_SHAPE', 'check-shapes'),
        'utc-date/fact-axioms': ('FACT_SCOPE_CONTAINS_AXIOMS', 'fact-scope'),
        'utc-date/graph-limit-before-preflight': ('GRAPH_INPUT_LIMIT', 'parse-data'),
        'utc-date/mixed-bounds-no-target': ('INVALID_SHAPE', 'date-bound'),
        'utc-date/multiple-values': ('RDF_TERM_INVALID', 'date-value'),
        'utc-date/C-offset': ('RDF_TERM_INVALID', 'date-value'),
        'utc-date/minExclusive': ('UNSUPPORTED_SHACL', 'check-shapes'),
        'utc-date/maxExclusive': ('UNSUPPORTED_SHACL', 'check-shapes'),
        'utc-date/legacy-text-isolation': ('INVALID_SHAPE', 'check-shapes'),
        'utc-date/bound-before-facts': ('INVALID_SHAPE', 'date-bound'),
        'utc-date/facts-before-value': ('FACT_SCOPE_CONTAINS_AXIOMS', 'fact-scope'),
        'shape/date-legacy-entry': ('INVALID_SHAPE', 'check-shapes'),
        'scope/nonexact-include': ('SCOPE_SELECTION_TYPE_INVALID', 'scope-selection'),
        'scope/unselected-rules': ('UNSELECTED_RULES_PRESENT', 'scope-selection'),
        'scope/facts-axioms': ('FACT_SCOPE_CONTAINS_AXIOMS', 'fact-scope'),
        'legacy/unbound-head': ('UNBOUND_RULE_VARIABLE', 'rule-definition'),
    }
    if key in direct:
        return result(*direct[key])
    if key.startswith('utc-date/integer/strict/') or key == 'C-illtyped-entry/strict':
        return result('INVALID_LITERAL_LEXICAL', 'parse-data')
    if key.startswith('C-inclusive-date-entry/') and o['parameters']['rangePolicy'] == 'legacy':
        return result('INVALID_SHAPE', 'check-shapes')
    for fragment, reason in [('none', 'TEXT_TYPE_INVALID'), ('invalid-turtle', 'INVALID_TURTLE'),
                             ('surrogate', 'INVALID_UNICODE'), ('text-limit', 'TEXT_INPUT_LIMIT')]:
        if key in ('utc-date/' + fragment + '-data', 'utc-date/' + fragment + '-shapes'):
            return result(reason, 'parse-' + key.rsplit('-', 1)[1])
    if key.startswith('utc-date/lexical-'):
        index, side = key.split('/')[-2:]
        index = int(index.split('-')[-1])
        if index <= 6:
            return result('INVALID_LITERAL_LEXICAL', 'parse-shapes' if side == 'bound' else 'parse-data')
        if index in (11, 12, 13, 14):
            return result('INVALID_SHAPE' if side == 'bound' else 'RDF_TERM_INVALID', 'date-' + side)
        # Exact front-door regression expectation is pre-registered at old6891
        # test lines275-313, expressly approved for reuse; not a new standards proof.
        authority = {'sourceType': 'pre-registered legacy regression assertion',
                     'ref': '6891a5842302859a531cf82767c5a482417bc274',
                     'path': 'packages/engine/tests/test_semantic_shacl_date_policy.py',
                     'lines': [275, 313], 'independentLibraryClassificationProven': False}
        expected, pending = result('INVALID_LITERAL_LEXICAL' if index <= 10 else
                                   'INVALID_SHAPE' if side == 'bound' else 'RDF_TERM_INVALID',
                                   ('parse-shapes' if side == 'bound' else 'parse-data') if index <= 10 else 'date-' + side)
        expected['declaredRegressionAuthority'] = authority
        return expected, pending
    if key.startswith('utc-date/incompatible-'):
        index, side = key.split('/')[-2:]
        index = int(index.split('-')[-1])
        return result('INVALID_SHAPE', 'check-shapes') if side == 'bound' and index >= 2 else result('RDF_TERM_INVALID', 'date-value')
    if family == 'turtle-rejection':
        index = int(key.rsplit('-', 1)[1])
        if index == 5:
            return result(None, 'pending-parser-vs-iri-priority', pending=[{'field': 'reason+phase', 'gap': 'Independent fixed front-door ordering for whitespace IRI is absent.', 'required': 'Reject without graph', 'allowedCodesBeforePriorityResolved': ['INVALID_TURTLE', 'ABSOLUTE_IRI_REQUIRED']}])
        codes = ['INVALID_TURTLE'] * 4 + ['ABSOLUTE_IRI_REQUIRED', None, 'UNSUPPORTED_BLANK_NODE', 'UNSUPPORTED_LITERAL_DATATYPE', 'UNSUPPORTED_NONFINITE_LITERAL']
        return result(codes[index], 'parse-data' if index >= 4 else 'parse-shapes')
    if key.startswith('query/'):
        suffix = key.split('/')[1]
        if suffix in ('insert-update', 'delete-update', 'load-update', 'construct', 'describe'):
            return result('READ_ONLY_QUERY_REQUIRED', 'query')
        if suffix == 'invalid':
            return result('INVALID_QUERY', 'query')
        if suffix in ('rand', 'now', 'uuid', 'struuid', 'bnode'):
            return result('UNSUPPORTED_QUERY_FUNCTION', 'query')
    if family == 'offline':
        suffix = key.split('/')[1]
        if suffix == 'implicit-jsonld':
            return result(None, 'implicit-loader-guard', pending=[{'field': 'exception+reason+phase', 'gap': 'No approved actual-loader observation projection yet.', 'required': 'No I/O; reject; do not grant network permission.'}])
        if suffix in ('jsonld-context', 'jsonld-import', 'xml-entity', 'n3-formula'):
            return result('UNSUPPORTED_FORMAT', 'format')
        if suffix.startswith('shacl-'):
            return result('UNSUPPORTED_SHACL', 'check-shapes')
        return result('EXTERNAL_ACCESS_DENIED', 'query' if suffix in ('service', 'service-silent', 'service-variable', 'service-nested', 'from', 'from-named', 'base-from', 'file-from') else 'parse')
    if key.startswith('integer/bad-iri-'):
        return result('ABSOLUTE_IRI_REQUIRED', 'parse-shapes' if 'shape-path' in key else 'parse-data')
    if key.startswith('integer/lexical-') and key.endswith('/strict') and not key.startswith('integer/lexical-5/'):
        return result('INVALID_LITERAL_LEXICAL', 'parse-data')
    if key.startswith('integer/other-datatype-'):
        index = int(key.rsplit('-', 1)[1])
        if index == 1:
            return result(None, 'pending-terms-vs-shape-priority', pending=[{'field': 'reason+phase', 'gap': 'Exact nni=-1 terms gate priority needs independently fixed datatype parser contract.', 'required': 'Reject zero Validator with no result.'}])
        return result({0: 'INVALID_LITERAL_LEXICAL', 2: 'INVALID_LITERAL_LEXICAL', 3: 'UNSUPPORTED_LITERAL_DATATYPE', 4: 'UNSUPPORTED_NONFINITE_LITERAL', 5: 'UNSUPPORTED_NONFINITE_LITERAL', 6: 'UNSUPPORTED_NONFINITE_LITERAL', 7: 'UNSUPPORTED_BLANK_NODE', 8: 'ABSOLUTE_IRI_REQUIRED'}[index], 'parse-data')
    if key.startswith('integer/bound-front-'):
        index = int(key.rsplit('-', 1)[1])
        code = ['INVALID_LITERAL_LEXICAL'] * 3 + ['INVALID_SHAPE', 'SHAPE_DATATYPE_INVALID', 'UNSUPPORTED_DATATYPE', 'UNSUPPORTED_NONFINITE_LITERAL']
        return result(code[index], 'parse-shapes' if index in (0, 1, 2, 6) else 'check-shapes')
    if key.startswith('shape/front-'):
        index = int(key.rsplit('-', 1)[1])
        if index == 0:
            return None
        if index == 2:
            return result(None, 'pending-terms-vs-shape-priority', pending=[{'field': 'reason+phase', 'gap': 'Exact negative nni front priority requires independent datatype parser contract.', 'required': 'Reject; no Validator/report.'}])
        return result({1: 'INVALID_LITERAL_LEXICAL', 3: 'INVALID_LITERAL_LEXICAL', 4: 'INVALID_SHAPE', 5: 'INVALID_SHAPE', 6: 'UNSUPPORTED_DATATYPE', 7: 'SHAPE_DATATYPE_INVALID', 8: 'INVALID_SHAPE', 9: 'INVALID_SHAPE'}[index], 'parse-shapes' if index in (1, 3) else 'check-shapes')
    if key in ('shape/duplicate-target', 'shape/duplicate-path', 'shape/arbitrary-constraint'):
        return result('INVALID_SHAPE', 'check-shapes')
    if key in ('scope/missing-source', 'scope/wrong-source', 'scope/missing-result', 'scope/unselected-result'):
        return result(None, 'scope-provenance-gate', pending=[{'field': 'reason+phase', 'gap': 'Scope provenance exact internal rejection code/order absent in independent approved interface document.', 'required': 'Reject before downstream query/SHACL, no new reasoning on invalid projection.'}])
    return None


def date_budget_expected(o):
    key = o['id']
    if o['family'] == 'utc-date-public-budget':
        count = int(key.rsplit('-', 1)[1])
        # Independent algebra from adopted §5.1; no implementation access.
        total = 23 * count + 420
        if total == 1000000:
            return {'semanticState': 'normal', 'validatorCalls': 1, 'report': {'conforms': True, 'violations': []},
                    'work': {'policy': 'i05-utc-date-preflight/1', 'cap': 1000000, 'consumed': total, 'remaining': 0,
                             'derivation': 'C(n)=3+3n+n*ceil(log2(max(2,n))); 54+1+C(m)+12+4m+150+200=23m+420'}}
        return {**rejection('GRAPH_INPUT_LIMIT', 'date-value'),
                'work': {'policy': 'i05-utc-date-preflight/1', 'cap': 1000000, 'consumed': 1000000, 'remaining': 0,
                         'uncappedRequired': total, 'debitBeforeOperation': True}}
    if o['family'] == 'utc-date-D1':
        early = '/D1-p0/' in key
        return {**rejection('RDF_TERM_INVALID' if early else 'GRAPH_INPUT_LIMIT', 'date-value'),
                'work': {'policy': 'i05-utc-date-preflight/1', 'cap': 1000000,
                         'consumed': 366042 if early else 1000000, 'remaining': 633958 if early else 0,
                         'equivalenceGroup': key.rsplit('/', 1)[0],
                         'derivation': 'bound plan6006; focus cache360004; p0 rejects at366042; p99 reaches cap before value. All three serializations share complete ledger, first error and graph identity.'}}
    return None


def finite_rdfs(graph):
    """Independent least fixed point of the four declared entailment relations."""
    initial = ordered_set(graph)
    closure = initial[:]
    while True:
        proposals = []
        for s, p, o in closure:
            if p == iri(RDFS + 'subClassOf'):
                for x, q, y in closure:
                    if q == iri(RDFS + 'subClassOf') and o == x:
                        proposals.append([s, p, y])
                    if q == iri(RDF + 'type') and y == s:
                        proposals.append([x, q, o])
            if p in (iri(RDFS + 'domain'), iri(RDFS + 'range')):
                for x, q, y in closure:
                    if q == s:
                        subject = x if p == iri(RDFS + 'domain') else y
                        if subject['kind'] == 'iri':
                            proposals.append([subject, iri(RDF + 'type'), o])
        revised = ordered_set(closure + proposals)
        if revised == closure:
            return [t for t in closure if t not in initial]
        closure = revised


def declared_rules(rules, graph):
    """Relational conjunctive-query interpretation; no product rule objects."""
    all_matches, heads = [], []
    for ordinal, rule in enumerate(rules):
        bindings = [({}, [])]
        for pattern in rule['when']:
            joined = []
            for binding, when in bindings:
                for triple in graph:
                    trial = dict(binding)
                    for pattern_term, value in zip(pattern, triple):
                        if 'variable' in pattern_term:
                            variable = pattern_term['variable']
                            if variable in trial and trial[variable] != value:
                                break
                            trial[variable] = value
                        elif record_term(pattern_term) != value:
                            break
                    else:
                        joined.append((trial, when + [triple]))
            bindings = joined
        for binding, when in sorted(bindings, key=canonical):
            if rule.get('comparisons'):
                raise ValueError('legacy comparison needs separately authored finite expected')
            produced = []
            for index, pattern in enumerate(rule['heads']):
                triple = [binding[t['variable']] if 'variable' in t else record_term(t) for t in pattern]
                heads.append(triple)
                produced.append({'headIndex': index, 'triple': triple})
            all_matches.append({'ruleId': rule['rule_id'], 'definitionOrdinal': ordinal,
                                'bindings': dict(sorted(binding.items())), 'when': when,
                                'comparisons': [], 'accepted': True, 'heads': produced})
    return {'customOutput': ordered_set(heads), 'matches': all_matches}


def record_term(term):
    if term['kind'] == 'iri':
        return iri(term['lexical_form'])
    return literal(term['lexical_form'], term['datatype_iri'], term['language_raw'])


def key_n3(term):
    if term['kind'] == 'iri':
        return '<' + term['value'] + '>'
    text = json.dumps(term['lexical'], ensure_ascii=False)
    if term['language']:
        return text + '@' + term['language']
    return text if term['datatype'] == XSD + 'string' else text + '^^<' + term['datatype'] + '>'


def finite_witnesses(graph):
    """Four normative relation instances, sorted by the approved §2 pair key.

    This selects stable first insertion, never the shortest proof or all proofs.
    Logical leaf references deliberately do not invent producer leaf IDs.
    """
    closure = ordered_set(graph)
    refs = {canonical(t): {'kind': 'input-triple', 'triple': t} for t in closure}
    depths = {canonical(t): 0 for t in closure}
    leaves = {canonical(t): [t] for t in closure}
    steps = []
    while True:
        candidates = []
        for a in closure:
            s, p, o = a
            for b in closure:
                x, q, y = b
                if p == iri(RDFS + 'subClassOf'):
                    if q == iri(RDFS + 'subClassOf') and o == x:
                        candidates.append(([s, p, y], [a, b], 'rdfs11'))
                    if q == iri(RDF + 'type') and y == s:
                        candidates.append(([x, q, o], [b, a], 'rdfs9'))
                if p == iri(RDFS + 'domain') and q == s:
                    candidates.append(([x, iri(RDF + 'type'), o], [a, b], 'rdfs2'))
                if p == iri(RDFS + 'range') and q == s and y['kind'] == 'iri':
                    candidates.append(([y, iri(RDF + 'type'), o], [a, b], 'rdfs3'))
        def sort_key(item):
            result, premises, _rule = item
            return tuple(map(key_n3, result)), tuple(tuple(map(key_n3, t)) for t in premises)
        added = []
        for result, premises, rule in sorted(candidates, key=sort_key):
            key = canonical(result)
            if key in refs:
                continue
            leaf_union = ordered_set([leaf for t in premises for leaf in leaves[canonical(t)]])
            depth = 1 + max(depths[canonical(t)] for t in premises)
            steps.append({'ordinal': len(steps), 'rule': rule, 'result': result,
                          'premises': [refs[canonical(t)] for t in premises], 'depth': depth,
                          'orderedDirectInputTriples': premises, 'leafUnion': leaf_union})
            refs[key] = {'kind': 'step', 'ordinal': len(steps) - 1}
            leaves[key], depths[key] = leaf_union, depth
            added.append(result)
        if not added:
            return steps
        closure = ordered_set(closure + added)


def legacy_expected(dataset):
    data = turtle(dataset['dataText'])
    rdfs = finite_rdfs(data)
    steps = finite_witnesses(data)
    computed = with_leaf_basis(declared_rules(dataset['rules'], ordered_set(data + rdfs)), data, steps)
    return {'inputGraph': data, 'rdfsAdded': rdfs, 'selectedWitnesses': finite_witnesses(data), 'warnings': [],
            **computed}


def with_leaf_basis(computed, graph, steps):
    proof = {canonical(t): [t] for t in graph}
    proof.update({canonical(step['result']): step['leafUnion'] for step in steps})
    for match in computed['matches']:
        match['leafBasis'] = ordered_set([leaf for triple in match['when'] for leaf in proof[canonical(triple)]])
        match['whenBasis'] = [proof[canonical(triple)] for triple in match['when']]
        match['sourcePolicy'] = 'all original leaf/source occurrences bound to actual input preimage; raw token spans unavailable where not supplied, never fabricated'
    return computed


def scope_expected(o, dataset):
    asserted, ontology = turtle(dataset['assertedText']), turtle(dataset['ontologyText'])
    mode = o['parameters']['mode']
    rdfs = finite_rdfs(ordered_set(asserted + ontology)) if mode != 'asserted' else []
    inferred_facts = [t for t in rdfs if t[1] not in (iri(RDFS + 'subClassOf'), iri(RDFS + 'domain'), iri(RDFS + 'range'))]
    axioms = [t for t in rdfs if t not in inferred_facts]
    steps = finite_witnesses(ordered_set(asserted + ontology)) if mode != 'asserted' else []
    computed = with_leaf_basis(declared_rules(dataset['rules'], ordered_set(asserted + inferred_facts)), asserted + ontology, steps) if mode != 'asserted' else {'customOutput': [], 'matches': []}
    facts = ordered_set(asserted + inferred_facts + computed['customOutput'])
    query_rows = sorted([[s, value] for s, p, value in facts if p == iri(RDF + 'type')], key=lambda r: (r[0]['value'], r[1]['value']))
    return {
        'facts': facts, 'ontology': ordered_set(ontology + axioms), 'derivedAxioms': axioms,
        'selectedRuleIds': [] if mode == 'asserted' else ['R-risk'], 'warnings': [],
        'rdfsAdded': rdfs, **computed,
        'query': {'type': 'SELECT', 'variables': ['s', 'c'], 'rows': query_rows},
        'shacl': shacl_report(facts, turtle(dataset['shapesText'])),
        'reasonCallsByStage': {'prepare': 0 if mode == 'asserted' else 1, 'project': 0},
        'reasoningReceipt': None if mode == 'asserted' else {'relation': 'project uses the exact freshly returned reasoning_result and provenance.reasoningSource, not another run/value-equal copy'},
        'factSources': [{'triple': t, 'role': 'asserted' if t in asserted else 'rule' if t in computed['customOutput'] else 'rdfs',
                        'basis': [t] if t in asserted else next(m['leafBasis'] for m in computed['matches'] if any(h['triple'] == t for h in m['heads'])) if t in computed['customOutput'] else next(s['leafUnion'] for s in steps if s['result'] == t),
                        'rawTokenSpan': 'unavailable unless actually supplied by source owner'} for t in facts],
    }


def b1_expected(dataset):
    asserted, ontology = turtle(dataset['assertedText']), turtle(dataset['ontologyText'])
    replacements = {r['subject']: r['type'] for r in dataset['replaceEquipmentTypes']}
    modified = [[s, p, iri(replacements[s['value']])] if p == iri(RDF + 'type') and s['kind'] == 'iri' and s['value'] in replacements and o == iri('urn:ontolearn:Equipment') else [s, p, o] for s, p, o in asserted]
    merged = ordered_set(modified + ontology)
    rdfs = finite_rdfs(merged)
    computed = with_leaf_basis(declared_rules(dataset['rules'], ordered_set(merged + rdfs)), merged, finite_witnesses(merged))
    scale = dataset['scale']
    return {
        'scale': scale, 'seed': 20261019, 'instrumentation': False,
        'assertedOriginal': asserted, 'modifiedFacts': ordered_set(modified), 'ontology': ontology,
        'mergedInput': merged, 'rdfsAdded': rdfs, **computed,
        'query': {'type': 'SELECT', 'variables': ['alarm'], 'rows': [[iri('urn:case:' + str(i) + ':alarm/A01')] for i in range(scale)]},
        'shaclOnOriginalAsserted': shacl_report(asserted, turtle(dataset['shapesText'])),
        'firstWarmRelation': 'all complete business graphs, matches, query and SHACL equal for First and Warm; no result tail omitted',
        'snapshotLoad': {'state': 'not-executed', 'reason': 'S1 Store/SQLite HOLD; absence cannot be numeric zero'},
        'measurement': {'fixedValuesForbidden': True, 'relation': 'fresh process/actual monotonic timers/identity and complete ordered phases require separately authorized collector; timing not semantic expected'},
    }


def record_math(dataset):
    if dataset.get('kind') == 'turtle':
        graph = turtle(dataset['text'])
        rules = []
        raw_records = None
    else:
        graph = ordered_set([[record_term(t) for t in row] for row in dataset['records']])
        rules = dataset['rules']
        raw_records = dataset['records']
    rdfs = finite_rdfs(graph)
    computed = with_leaf_basis(declared_rules(rules, ordered_set(graph + rdfs)), graph, finite_witnesses(graph))
    witnesses = []
    closure = ordered_set(graph + rdfs)
    for result in rdfs:
        subject, predicate, obj = result
        candidates = []
        for axiom in closure:
            a, p, b = axiom
            if predicate == iri(RDF + 'type'):
                if p == iri(RDFS + 'domain') and b == obj:
                    candidates += [{'rule': 'rdfs2', 'premises': [axiom, fact]} for fact in closure if fact[0] == subject and fact[1] == a]
                if p == iri(RDFS + 'range') and b == obj and subject['kind'] == 'iri':
                    candidates += [{'rule': 'rdfs3', 'premises': [axiom, fact]} for fact in closure if fact[2] == subject and fact[1] == a]
                if p == iri(RDFS + 'subClassOf') and b == obj:
                    candidates += [{'rule': 'rdfs9', 'premises': [[subject, iri(RDF + 'type'), a], axiom]}] if [subject, iri(RDF + 'type'), a] in closure else []
            if predicate == iri(RDFS + 'subClassOf') and p == predicate and a == subject:
                right = [b, predicate, obj]
                if right in closure:
                    candidates.append({'rule': 'rdfs11', 'premises': [axiom, right]})
        witnesses.append({'result': result, 'finiteValidOrderedPremiseChoices': ordered_set(candidates),
                          'depthRule': '1+max(depth(premises)); original leaf depth0; no forward/self reference',
                          'leafRule': 'exact deduplicated union of all original leaf premises; every input source occurrence retained separately'})
    return {'inputGraph': graph, 'rdfsAdded': rdfs, **computed, 'witnessConstraints': witnesses, 'selectedDirectSteps': finite_witnesses(graph),
            'rawTermSourceOccurrences': raw_records,
            'rawAliases': 'RDF1.1 string and case-insensitive language identities coalesce only as RDF identity; raw lexical/datatype/language/source occurrences including None/empty preserved exactly',
            'rootOccurrences': [{'triple': head['triple'], 'ref': {'kind': 'ruleHead', 'firingIndex': i, 'headIndex': head['headIndex']}} for i, firing in enumerate(computed['matches']) for head in firing['heads']]}


DYNAMIC_RULES = {
    'allFields': 'Complete records: exact keys, exact scalar types (int excludes bool), full sequence tails, multiplicity and order; reject omitted/extra/duplicate fields rather than normalize away.',
    'wire': {
        'payload': 'canonical sorted compact UTF8 of complete payload; SHA/byte length recomputed from received bytes',
        'rows': 'sequence of str segments, each <=8192 characters, <=10000 rows; concat encoded UTF8 equals complete payload_json; rows_json canonical of every row; payload+rows <=8388608B',
        'sidecars': 'source_encoded/definitions_encoded/catalog_json and all respective SHA/lengths cover full preimages, including final child/source/definition/limits; no source-code SHA stands in for package code',
        'integers': 'native exact int nonbool; wire unique integerHex (zero canonical, no +/uppercase/negative-zero/leading zeros); all tuples become arrays without losing items',
    },
    'sameIssue': {
        'material': 'input text UTF8 or complete raw records, full rules/definitions/disabled/source and provenance are bound to the pinned input only',
        'expectation': 'actual caller-held expectation captured from this precise production; all payload/rows/input/source/definition/catalog/implementation fields equal complete original values; JSON self-assertion does not prove origin',
        'allocation': 'same actual OriginalAllocation object and every issued child(rule_id,definitionOrdinal,limits), original rule_ids/disabled match input and batches; no fresh/rebound allocation for modified bytes',
        'restore': 'complete immutable projection equals same produced native result and every child/row/source/definition/catalog field; no reason call and no partial view on rejection',
    },
    'directSteps': {
        'containerKeys': ['format', 'steps'], 'stepKeys': ['ordinal', 'rule', 'result', 'premises', 'depth'],
        'leafRefKeys': ['kind', 'reference'], 'stepRefKeys': ['kind', 'ordinal'],
        'ruleHeadKeys': ['kind', 'firingIndex', 'headIndex'],
        'relation': 'every result exactly in rdfsAdded, each introduced once; two ordered premises are declared rule instances; leaf refs resolve to complete input dictionary; step ordinal earlier; depth and leaf union exact; no cyclic/forward refs',
        'roots': 'for each actual requested target, return every matching leaf/direct-step/ruleHead occurrence in prescribed order; repeated head occurrences retained; no off-target roots or fabricated calls for unrequested targets',
    },
    'versions': {'fullview': {'payloadFormat': 'i05-reasoning-result/2', 'executionSemanticsVersion': 'i05-finite-7', 'schemaGeneration': 1}, 'explanation': {'payloadFormat': 'i05-reasoning-result/3', 'executionSemanticsVersion': 'i05-finite-8', 'restoreSchema': 'i05-profile-restore-schema/2', 'schemaGeneration': 2}, 'policy': 'Q6 remains OntoLearn-rule-comparison-profile/1; directsteps format i05-direct-rdfs-steps/1; dispatch by explicit versions, never keys'},
    'runtimeIdentity': 'run ID, times, real source/frozen origins and actual compiled-code domains require separate genuine provenance receipts. Source and package issue separate own objects; never compare memory addresses or prefill bundle code from source SHA.',
    'unknown': 'unknown/incomplete/not-started/unexpected-failure has no oracle-match permission; collection exit0 never implies semantic/original-operation success',
}


def business_expected(o, dataset, golden):
    key, op = o['id'], o['operation']
    declared = declared_rejection(o)
    if declared:
        return declared
    budget = date_budget_expected(o)
    if budget:
        if budget['semanticState'] == 'normal':
            budget['entryVersion'] = 'i05-shacl-text-2'
            budget['dataPolicy'], budget['rangePolicy'] = o['parameters']['dataPolicy'], o['parameters']['rangePolicy']
        return budget, []
    if op == 'profile':
        math = profile_expected(dataset, golden, o)
        if key == 'profile-83/transfer:repair':
            return {'semanticState': 'not-executed', 'reason': 'No independent rule execution authority in repair context; do not inherit R-risk', 'mathematicalContextOnly': math}, []
        return {'semanticState': 'normal', 'conditionalBusinessExpected': math,
                'admission': 'Compare full business math only after independently established logical budget admissibility; resource rejection needs exact authorized ledger, not historical result counts.'}, [
                    {'field': 'budgetAdmissibility+typedSerializedUsage', 'gap': 'Independent full per-occurrence producer/copy/projection charging and real caller-issued child allocation are not yet specified; static input below maxima cannot prove cumulative run admissibility.', 'required': 'Keep actual resource rejection distinct from a matched normal mathematical result; never reuse historical78/4/1 as expected.'}]
    if op == 'parse':
        return {'semanticState': 'normal', 'graph': turtle(dataset['text'])}, []
    if op == 'query':
        expected = fixed_query(key)
        if expected is None:
            raise ValueError('query independent expected missing: ' + key)
        return {'semanticState': 'normal', 'query': expected}, []
    if op in ('shape', 'shacl-text'):
        report = shacl_report(turtle(dataset['dataText']), turtle(dataset['shapesText']))
        expected = {'semanticState': 'normal', 'report': report, 'validatorCalls': 1}
        if op == 'shacl-text':
            p = o['parameters']
            expected.update(entryVersion='i05-shacl-text-2' if p['rangePolicy'] == 'utc-date-range-v1' else 'i05-shacl-text-1', dataPolicy=p['dataPolicy'], rangePolicy=p['rangePolicy'])
        return expected, []
    if op == 'legacy-reason':
        math = legacy_expected(dataset)
        pending = [{'field': 'legacyDTO+evidenceProjection', 'gap': 'Fixed independent contract specifies full mathematical graph/matches, but not all five DTO keys/version/evidence encoding.', 'required': 'Preserve every graph, binding, when/head and witness; future projection needs explicit schema, not output-derived golden.'}]
        if key == 'legacy/no-rule-feedback':
            math['warnings'] = {'requiredCode': 'RULE_CHAIN_UNSUPPORTED', 'ruleId': 'R-next', 'exactStringOrdering': 'pending'}
        return {'semanticState': 'normal', 'math': math}, pending
    if op == 'scope':
        return {'semanticState': 'normal', **scope_expected(o, dataset)}, [
            {'field': 'scopeProvenanceDigestEncoding', 'gap': 'Actual same-issue reasoningSource must be captured, exact full provenance DTO/receipt not frozen in independent schema.', 'required': 'Complete selectedFacts/ruleIds/warnings/axioms/two views and input-consistent fact provenance; no authentication claims.'}]
    if op == 'b1-measurement':
        return {'semanticState': 'normal', **b1_expected(dataset)}, []
    if op in ('fullview', 'dag', 'restore-negative'):
        pending = [{'field': 'graphBudget+budgetUsage+typedValues', 'gap': 'Exact top-level 7/15/11 field names are fixed by root literal-only reference; full independent typed cost/usage value and complete nested projection predicates still require approved interface/ledger data, not product/probe output.', 'knownPayloadKeys': ['format', 'inputDigest', 'inputDigestDomain', 'sourceDigest', 'definitionsDigest', 'implementation', 'reasoning'], 'knownNativeKeys': ['profile', 'semanticsVersion', 'formatVersion', 'rdfs', 'rules', 'warnings', 'proofLeaves', 'firingGroups', 'evidence', 'definitions', 'catalog', 'mechanismBatches', 'rdfsEvidence', 'termSources', 'graphBudget'], 'knownChildKeys': ['ruleId', 'definitionOrdinal', 'disabled', 'definitions', 'catalog', 'originalMatches', 'batch', 'limits', 'budgetLimits', 'planDigest', 'budgetUsage']},
                   {'field': 'genuineCapture+budgetAdmissibility', 'gap': 'Fresh expectation/allocation and full producer/restore budget ledgers cannot be independently supplied by JSON values; actual provenance gate remains separately required.'}]
        if op == 'dag' and dataset['kind'] == 'turtle':
            return {'semanticState': 'known-rejection', 'stage': 'structured-material-required', 'validatorCalls': 0, 'partialView': None}, [{'field': 'exactStructuredOnlyError', 'gap': 'Canonical direct entry rejection code not enumerated in independent schema.'}]
        if dataset['kind'] == 'profile':
            math = profile_expected(dataset, golden, o)
        else:
            math = record_math(dataset)
        expected = {'semanticState': 'normal', 'businessMath': math, 'dynamicRules': ['wire', 'sameIssue', 'directSteps', 'versions', 'runtimeIdentity', 'allFields'], 'requestedRoots': o['parameters'].get('rootsTargets', [])}
        if op == 'restore-negative':
            expected.update(semanticState='known-rejection', failureStage='A1', mutation=o['parameters']['mutation'],
                            receivedBytes='exact enum mutation of actual same-issue received bytes; original expectation/allocation unchanged',
                            originalSuccessViewUnchanged=True, partialView=None, restoreReasonCalls=0,
                            noDeepRevalidationClaim=True)
            pending.append({'field': 'A1ExactErrorProjection', 'gap': 'Need independent exact A1 safe error/diagnostic schema; do not use rebinding/deep-DAG golden errors for digest mismatch.'})
        return expected, pending
    raise ValueError('unhandled operation: ' + op)


FIELD_POLICIES = {
    'RDFTerm': {'oneOfExactKeys': [['kind', 'value'], ['kind', 'lexical', 'datatype', 'language'], ['kind', 'label']],
                'iri': 'exact absolute IRI, no namespace rewriting',
                'literal': 'exact lexical/datatype; simple string maps to xsd:string per RDF1.1; language comparison casefold only with full original occurrences separately pinned',
                'blank': 'only legal shape-list graph structure isomorphism; bijection must preserve every triple/multiplicity; no data blank nodes admitted'},
    'graphs': 'complete unordered RDF-identity sets, no numeric/date lexical normalization; actual input text bytes separate',
    'query': 'exact ASK boolean or SELECT ordered variables and every typed cell/None/row including tail and tie-order; no row-count shortcut',
    'SHACL': {'exactKeys': ['conforms', 'violations'], 'violationExactKeys': ['focus', 'path', 'value', 'sourceShape', 'constraint', 'severity'],
              'comparison': 'complete multiset of all six-field rows; conforms exact bool; absent value represented None, never synthesized'},
    'profile': 'asserted/ontology/rdfs/custom exact full sets; every binding/when/comparison/index/operator/operand/result/accepted/head occurrence/leaf/source/definition preserved; false computation is not persistent false ComparisonEvidence',
    'source': 'all raw None versus empty string values retained; spans unavailable remain unavailable; input content hashes are not producer authority',
    'DAG': 'every direct step and every result/root occurrence, ordered two premises, chosen-witness depth and exact leaf union, complete alias occurrence mappings; see dynamicRules and explicit pending interface fields',
    'state': 'normal, known-rejection, not-executed are distinct; pending means no oracle match may be claimed; incomplete/unknown/collectionComplete alone cannot satisfy oracle',
}


# These are semantic-object relations, not paths in an unapproved JSONL envelope.
RELATIONS = [
    {'id': 'received-payload-sha', 'op': 'sha256-equals',
     'bytes': ['wire', 'payload_json'], 'digest': ['held', 'payload_sha256']},
    {'id': 'received-rows-sha', 'op': 'sha256-equals',
     'bytes': ['wire', 'rows_json'], 'digest': ['held', 'rows_sha256']},
    {'id': 'received-source-sha', 'op': 'sha256-equals',
     'bytes': ['wire', 'source_encoded'], 'digest': ['held', 'source_sha256']},
    {'id': 'received-definitions-sha', 'op': 'sha256-equals',
     'bytes': ['wire', 'definitions_encoded'], 'digest': ['held', 'definitions_sha256']},
    {'id': 'received-catalog-sha', 'op': 'sha256-equals',
     'bytes': ['wire', 'catalog_json'], 'digest': ['held', 'catalog_sha256']},
    {'id': 'rows-no-truncated-tail', 'op': 'concat-utf8-equals',
     'rows': ['wire', 'rows'], 'bytes': ['wire', 'payload_json'], 'maxItems': 10000},
    {'id': 'payload-rows-byte-cap', 'op': 'byte-sum-at-most',
     'parts': [['wire', 'payload_json'], ['wire', 'rows_json']], 'cap': 8388608},
    {'id': 'restore-complete-native', 'op': 'exact-model',
     'left': ['produced', 'native'], 'right': ['restored', 'native']},
    {'id': 'restore-every-child', 'op': 'exact-model',
     'left': ['produced', 'children'], 'right': ['restored', 'children']},
    {'id': 'expectation-same-issuance', 'op': 'same-issued-object',
     'left': ['issued', 'expectation'], 'right': ['used', 'expectation']},
    {'id': 'allocation-same-issuance', 'op': 'same-issued-object',
     'left': ['issued', 'allocation'], 'right': ['used', 'allocation']},
]


def evaluate_relation(rule, model):
    """Finite predicate self-tests on owned semantic models, never observed runs.

    A genuine caller-capture receipt is a separate required trust gate. Supplying
    equal JSON values cannot satisfy same-issued-object or prove its provenance.
    """
    def at(path):
        current = model
        for key in path:
            current = current[key]
        return current
    op = rule['op']
    if op == 'sha256-equals':
        raw, sha = at(rule['bytes']), at(rule['digest'])
        if type(raw) is not bytes or type(sha) is not str or digest(raw) != sha:
            raise ValueError('received byte digest differs')
    elif op == 'concat-utf8-equals':
        rows, raw = at(rule['rows']), at(rule['bytes'])
        if type(rows) not in (list, tuple) or len(rows) > rule['maxItems']:
            raise ValueError('rows type or full count')
        if not all(type(row) is str for row in rows) or ''.join(rows).encode() != raw:
            raise ValueError('row tail/encoding differs')
    elif op == 'byte-sum-at-most':
        parts = [at(path) for path in rule['parts']]
        if not all(type(part) is bytes for part in parts) or sum(map(len, parts)) > rule['cap']:
            raise ValueError('complete wire byte cap')
    elif op == 'exact-model':
        assert_exact_model(at(rule['left']), at(rule['right']))
    elif op == 'same-issued-object':
        left, right = at(rule['left']), at(rule['right'])
        if type(left) in (type(None), bool, int, float, str, bytes, dict, list, tuple, set, frozenset):
            raise ValueError('missing/JSON value is not an issued typed object')
        if left is not right:
            raise ValueError('not the same issued caller object')
    else:
        raise ValueError('unknown predicate operator')
    return True


def expected_sources(observation, expected):
    """Expected authority is distinct from observation input-origin sourceRefs."""
    op, key = observation['operation'], observation['id']
    refs = [{'local': 'guidance/contract.md', 'pointer': 'sections3,4.2,6,7',
             'type': 'approved observation and comparison contract'}]
    if op == 'profile' or (op == 'fullview' and key.startswith('fullview/profile-')):
        math = expected.get('conditionalBusinessExpected', expected.get('businessMath', expected.get('mathematicalContextOnly', {})))
        refs.append({'local': 'inputs/real-executor-acceptance-inputs.json',
                     'pointers': math.get('independentGraphPointers', []) + ['/triples', '/matches', '/ruleDefinitions', '/rdfsWitnesses'],
                     'type': 'previous independently hand-selected complete expected',
                     'fields': ['graphs', 'all bindings', 'when', 'comparisons', 'heads', 'basis', 'definitions', 'sources']})
        refs += [{'local': 'guidance/q6-profile.md', 'pointer': 'sections2-4', 'type': 'adopted value/comparison policy'},
                 {'local': 'guidance/q6-mechanism.md', 'pointer': 'section4', 'type': 'budget bounds only; exact cumulative admissibility remains pending'}]
    elif op in ('parse', 'query', 'shape', 'shacl-text', 'offline'):
        refs.append({'local': 'guidance/semantic-boundaries.md', 'pointer': 'existing parser/query/template scope and fixed safe reasons',
                     'type': 'approved finite interface contract'})
        if key.startswith('C-'):
            base = key.split('/')[0]
            goldens = read_pinned('consumer-C-goldens.json')['cases']
            index = next(i for i, row in enumerate(goldens) if row['id'] == base)
            refs.append({'local': 'inputs/consumer-C-goldens.json', 'pointer': '/cases/' + str(index) + '/expected',
                         'type': 'independent pre-existing C expected; extension date branch only where explicitly selected'})
        else:
            refs.append({'local': 'inputs/' + ASSET, 'pointer': '/datasets/' + observation['datasetId'].replace('~', '~0').replace('/', '~1'),
                         'type': 'pinned finite input interpreted independently under the approved grammar/template/query relation; not an expected hidden in input'})
        if observation['family'].startswith('utc-date') or 'utc-date-range-v1' in observation['parameters'].values():
            refs.append({'local': 'guidance/date-policy.md', 'pointer': 'sections2,3,5.1',
                         'type': 'adopted date domain, priority, and independent closed-form work derivation'})
        if 'declaredRegressionAuthority' in expected:
            refs.append({'local': 'guidance/pre-registered-date-assertions.py.raw', 'pointer': 'original lines275-313',
                         'type': 'pre-registered legacy regression assertion; not independent fixed-library classification proof'})
    else:
        refs += [{'local': 'inputs/real-executor-acceptance-inputs.json', 'pointers': ['/finiteRdfsRules', '/excludedRdfs'],
                  'type': 'independent finite entailment relations; no generic OWL/RDFS or rule feedback'},
                 {'local': 'guidance/directsteps-contract.md', 'pointer': 'sections2-4',
                  'type': 'ordered first-insertion witnesses, typed refs, occurrence roots and dynamic wire relations'}]
    if op in ('fullview', 'dag', 'restore-negative'):
        refs.append({'local': 'guidance/native-child-declaration-reference.json', 'pointer': '/declarationsOnlyNoImplementationAlgorithmOrRuntimeOutput',
                     'type': 'explicitly authorized literal-only 7/15/11 interface declarations; not value/algorithm evidence'})
    return refs


def construct():
    for name, (size, sha) in DOC_PINS.items():
        raw = (EVIDENCE / 'guidance' / name).read_bytes()
        if len(raw) != size or digest(raw) != sha:
            raise ValueError('normative source identity mismatch: ' + name)
    asset, manifest = read_pinned(ASSET), read_pinned(DESCRIPTOR)
    golden = read_pinned('real-executor-acceptance-inputs.json')
    read_pinned('explanation-goldens.json')
    read_pinned('consumer-C-goldens.json')
    if asset['format'] != 'i05-source-package-parity-inputs/1' or manifest['format'] != 'i05-source-package-parity-manifest/1':
        raise ValueError('wrong fixed format')
    observations, datasets = asset['observations'], asset['datasets']
    if len(observations) != 417 or len(datasets) != 320 or len({o['id'] for o in observations}) != 417:
        raise ValueError('inventory identity mismatch')
    if manifest['inputAsset'] != {'bytes': PINS[ASSET][0], 'sha256': PINS[ASSET][1]}:
        raise ValueError('descriptor to input binding mismatch')
    ids = [o['id'] for o in observations]
    if set().union(*[set(v) for v in manifest['caseSets'].values()]) != set(ids):
        raise ValueError('case set coverage gap')
    entries = []
    for ordinal, observation in enumerate(observations):
        dataset = datasets[observation['datasetId']]
        if digest(canonical(dataset)) != observation['projectionSha256']:
            raise ValueError('projection mismatch: ' + observation['id'])
        expected, pending = business_expected(observation, dataset, golden)
        entries.append({
            'id': observation['id'], 'inventoryOrdinal': ordinal,
            'family': observation['family'], 'operation': observation['operation'],
            'datasetId': observation['datasetId'], 'projectionSha256': observation['projectionSha256'],
            'sourceRefs': observation['sourceRefs'], 'contextStatus': observation['contextStatus'],
            'parameters': observation['parameters'],
            'caseSets': {name: selected.index(observation['id']) for name, selected in manifest['caseSets'].items() if observation['id'] in selected},
            'expected': expected, 'pendingFields': pending, 'oracleStatus': 'pending' if pending else 'specified',
            'businessComparison': 'exact full canonical business model with fieldPolicies; this is not the future JSONL projection',
            'dynamicRules': ['allFields', 'unknown', 'runtimeIdentity'] + (['wire', 'sameIssue', 'directSteps', 'versions'] if observation['operation'] in ('fullview', 'dag', 'restore-negative') else []),
            'expectedSourceRefs': expected_sources(observation, expected),
        })
    counts = Counter(e['oracleStatus'] for e in entries)
    states = Counter(e['expected']['semanticState'] for e in entries)
    original = asset['contexts']
    original_cases = read_pinned('product-cases.json')
    def pointer(value, path):
        for token in path.lstrip('/').split('/') if path else []:
            token = token.replace('~1', '/').replace('~0', '~')
            value = value[int(token)] if isinstance(value, list) else value[token]
        return value
    context_ledger = {
        'original': original,
        'originalOperations': [{'id': r['id'], 'state': 'not-executed', 'source': r, 'originalOperationText': pointer(original_cases, r['source']['pointer'])} for r in original['originalOperations']],
        'learningChecks': [{'id': r['id'], 'state': 'not-executed', 'source': r} for r in original['learningChecks']],
        'productCases': [{'id': r['caseId'], 'state': 'not-executed', 'source': r, 'originalSetupSteps': pointer(original_cases, r['source']['pointer'])} for r in original['productCases']],
        'originalRequestedOperationPassed': False, 'lifecycleExecuted': False, 'sourceAuthorityAuthenticated': False,
        'mathOnlyCounts': {'all': 83, 'eligible': 82, 'fullContext': 79, 'intersection': 78,
                           'repairProfileNotExecuted': 1, 'E5FragmentsNotWholeOperations': 4},
        'restriction': '106 operations/54 checks/50 cases retain all metadata and original immutable source pointers; mathematical graphs do not execute reset/save/repair/history/behavior or certify original scenarios',
    }
    interface_raw = (EVIDENCE / 'guidance/native-child-declaration-reference.json').read_bytes()
    if len(interface_raw) != 2087 or digest(interface_raw) != '71f64ab22f60fe6407e72f97a1296f4863fdcf8dc22e583425366d220a3dba74':
        raise ValueError('literal interface identity mismatch')
    interface = strict_json(interface_raw)['declarationsOnlyNoImplementationAlgorithmOrRuntimeOutput']
    build_sha = digest(Path(__file__).read_bytes())
    oracle = {
        'format': 'T05-independent-semantic-oracle/1', 'builderSha256': build_sha,
        'inputRef': '0e42a0fe349054a92817cb4d463bccdc15f6c042',
        'inputIdentity': {'bytes': PINS[ASSET][0], 'sha256': PINS[ASSET][1]},
        'caseSets': manifest['caseSets'], 'fieldPolicies': FIELD_POLICIES, 'dynamicRules': DYNAMIC_RULES,
        'finiteRelations': RELATIONS,
        'observations': entries, 'contextLedger': context_ledger,
        'wholeOracleComplete': not counts['pending'],
        'notClaims': ['product executed', 'source/package equivalence', 'formal Job/selected', 'whole-H', 'SQLite/S1 readiness', 'parent T05 acceptance', 'JSONL adapter/build provenance approval'],
    }
    coverage = {'format': 'T05-oracle-coverage/1', 'observationCount': len(entries), 'datasetCount': len(datasets),
                'byFamily': dict(sorted(Counter(e['family'] for e in entries).items())),
                'byStatus': dict(sorted(counts.items())), 'semanticStates': dict(sorted(states.items())),
                'caseSets': {k: {'orderedIds': v, 'count': len(v), 'orderedIdsSha256': digest(canonical(v))} for k, v in manifest['caseSets'].items()},
                'pending': [{'id': e['id'], 'fields': e['pendingFields']} for e in entries if e['pendingFields']],
                'wholeOracleComplete': oracle['wholeOracleComplete']}
    budget_items = []
    for e in entries:
        if e['operation'] != 'profile' or e['expected']['semanticState'] == 'not-executed':
            continue
        raw = datasets[e['datasetId']]['input']
        math = e['expected']['conditionalBusinessExpected']
        budget_items.append({
            'id': e['id'], 'datasetPointer': '/datasets/' + e['datasetId'].replace('~', '~0').replace('/', '~1') + '/input',
            'entry': 'execute_profile_records', 'inputProjectionSha256': e['projectionSha256'],
            'knownFiniteSizesNotAdmissionProof': {
                'assertedRecords': len(raw['asserted']), 'ontologyRecords': len(raw['ontology']),
                'rawTermOccurrences': 3 * (len(raw['asserted']) + len(raw['ontology'])),
                'definitionCount': len(raw['definitions']), 'handSelectedBindings': len(math['matches']),
                'acceptedHeadOccurrences': sum(len(m['heads']) for m in math['matches'] if m['accepted']),
                'disabledRuleIds': raw['disabled_rule_ids'],
            },
            'missingInvoiceOperations': [
                {'operation': 'input record/TermInput/source decode and copy', 'knownRule': 'Q6 mechanism section4: byte scans and every item charge before construction', 'missingFormula': 'Exact repeated occurrences and complete raw source/lexical copies across material input/source preimages; canonical asset bytes are not native preimage bytes.'},
                {'operation': 'definition compile and original ordered plan', 'knownRule': 'Q6 mechanism section4: constants compile once; each binding/comparison/head and bigint limb operation charged', 'missingFormula': 'Exact compile/capture planDigest preimage encoding, all source copies and definitionOrdinal/ruleId ordering transitions, before any cache reuse.'},
                {'operation': 'finite graph preparation and real match enumeration', 'knownRule': 'ee2b contract3: full graph/when/basis and all matches; no given bindings as product input', 'missingFormula': 'An independent exact action invoice for canonical graph copying/indexing/sorting/closure candidate visits and match enumeration; expected match count alone is not work.'},
                {'operation': 'batch all-comparisons/all-heads atomic output', 'knownRule': 'Q6 mechanism sections2-4: false must not skip later comparisons; no partial return', 'missingFormula': 'Actual typed field/limb/string visits and complete batch byte serialization including each repeated source/basis/head occurrence; no blanket unit-per-row assumption.'},
                {'operation': 'production payload/rows/source/definition/catalog projection-copy-hash', 'knownRule': 'T05 directsteps section4: full J each copy; new B is not whole-J proxy', 'missingFormula': 'Exact canonical typed encoding/row segmentation, all simultaneous copies and hash scans; graphBudget and budgetUsage full values remain unknown, not zero.'},
            ],
            'allocationRequired': {'source': 'the actual same production issuer', 'ruleIdsAndDisabled': 'must equal full original rule set/disabled list', 'children': 'one exact original child per definition/rule with its actual limits, planDigest, budgetUsage; do not synthesize caps or rebind allocation', 'value': None},
            'firstErrorEntry': {'knownOrder': 'input counts/bytes/structure -> original definition positions/constants/heads -> binding -> all comparisons -> all-true heads -> complete output preflight', 'missingDecision': 'Exact first debit/exhaustion stage cannot be fixed without full independent invoice and actual child cap; a prior resource fault can precede a later lexical/domain error.'},
            'normativeRefs': ['guidance/q6-mechanism.md sections2-4', 'guidance/directsteps-contract.md sections2,4', 'guidance/contract.md sections3,4.2,4.3,6'],
            'status': 'pending; no historical or probe failure pattern used as expected',
        })
    budget_gaps = {'format': 'T05-operation-budget-gaps/1', 'scope': '82 eligible profile calls; repair excluded only from execution, not inventory', 'items': budget_items,
                   'additionalProductionRestoreCases': [{'id': e['id'], 'operation': e['operation'], 'entryChain': ['prepare_profile_material', 'execute_profile_explanation' if e['operation'] == 'dag' or e['parameters'].get('explanation') is True else 'execute_admitted_profile_job', 'original-receiver-bytes enum mutation' if e['operation'] == 'restore-negative' else 'unchanged same-issue wire', 'restore_profile_explanation_result' if e['operation'] == 'dag' or e['parameters'].get('explanation') is True else 'restore_profile_result', 'explanation_roots only for actual requestedTargets and successful restored view' if e['operation'] == 'dag' else 'no roots call on failed restore'], 'mutation': e['parameters'].get('mutation'), 'requestedTargets': e['parameters'].get('rootsTargets', []), 'knownFirstBoundary': 'production admissibility precedes any restore-negative A1; malformed receiver bytes must use original held expectation, never rebind', 'missingInvoice': 'complete all-occurrence C0/R0 projection-copy-hash plus separate C_D/R_D/roots charges where explanation selected, and actual original allocation/caps', 'actualAllocation': None, 'normativeRef': 'guidance/directsteps-contract.md section4'} for e in entries if e['operation'] in ('fullview', 'dag', 'restore-negative') and 'businessMath' in e['expected']],
                   'directPools': {'knownAnalyticPolicy': 'T05 directsteps section4 C_D/R_D/S/T/H; per candidate8work, per step32work, per indexed byte16work+2scan_copy; all whole-J copies and repeated receives separately charged', 'notProven': 'complete combined actual invoice/caller allocation and first exhausted pool; analytic sub-bound is not extra wallet or physical CPU/H proof'}}
    source_rows = [{'local': 'docs/reviews/T05/source-package-oracle/inputs/' + n, 'sourcePath': SOURCE_PATHS[n], 'bytes': size, 'sha256': sha,
                    'role': 'sealed pure input, not expected' if n in (ASSET, DESCRIPTOR) else 'previous independently authored external expected, never engine input',
                    'ref': '0e42a0fe349054a92817cb4d463bccdc15f6c042' if n in (ASSET, DESCRIPTOR) else '525c91717c07dc4b386fcec00f897e1e6a75caf1'} for n, (size, sha) in PINS.items()]
    source_rows += strict_json((EVIDENCE / 'guidance/source-identities.json').read_bytes())
    source_rows += [{'local': 'docs/reviews/T05/source-package-oracle/guidance/' + n, 'bytes': size, 'sha256': sha, 'sourceType': 'approved contract/interface or explicitly reused legacy pre-registration; never a new probe output'} for n, (size, sha) in DOC_PINS.items()]
    sources = {'format': 'T05-oracle-sources/1', 'sources': source_rows,
               'forbiddenAsOracle': ['new I05 probe/tests/generator', 'I05 source/package observations', 'source output as golden'],
               'semantics': 'Source file names do not grant authority: triples/graphs/matches/rdfsWitnesses are external expected even when named inputs.json.'}
    schema = {'format': 'T05-oracle-schema/1', 'scope': 'semantic model only; no frozen JSONL adapter',
              'entryKeys': sorted(entries[0]), 'statusValues': ['specified', 'pending'],
              'stateValues': ['normal', 'known-rejection', 'not-executed'],
              'normalization': FIELD_POLICIES, 'dynamicFieldPolicies': DYNAMIC_RULES, 'exactIssuedRecordKeys': {k: v['keys'] for k, v in interface.items()},
              'explanationDispatch': 'explicit /3 version only; reasoning is native15 plus directSteps, child11 unchanged',
              'unknownNotMatched': True, 'missingOrExtraOrDuplicateKeysRejected': True}
    return {'oracle.json': oracle, 'coverage.json': coverage, 'sources.json': sources, 'schema.json': schema,
            'budget-gaps.json': budget_gaps}


def validate_oracle(oracle, asset, descriptor):
    entries = oracle['observations']
    if [e['id'] for e in entries] != [e['id'] for e in asset['observations']]:
        raise ValueError('missing/reordered/extra observation')
    if oracle['caseSets'] != descriptor['caseSets']:
        raise ValueError('case sets changed')
    for expected, actual in zip(asset['observations'], entries):
        if actual['projectionSha256'] != expected['projectionSha256'] or actual['parameters'] != expected['parameters']:
            raise ValueError('input binding changed')
        if actual['oracleStatus'] != ('pending' if actual['pendingFields'] else 'specified'):
            raise ValueError('pending hidden')
        result = actual['expected']
        if result['semanticState'] not in ('normal', 'known-rejection', 'not-executed'):
            raise ValueError('unknown promoted to matched')
        if result['semanticState'] == 'known-rejection' and result.get('report') is not None:
            raise ValueError('rejection has partial report')
        if 'report' in result and result['report'] is not None:
            report = result['report']
            if set(report) != {'conforms', 'violations'} or type(report['conforms']) is not bool:
                raise ValueError('report schema')
            for row in report['violations']:
                if set(row) != set(FIELD_POLICIES['SHACL']['violationExactKeys']):
                    raise ValueError('incomplete SHACL six fields')
            if report['conforms'] != (not report['violations']):
                raise ValueError('report conforms inconsistent')
    if oracle['wholeOracleComplete'] != all(e['oracleStatus'] == 'specified' for e in entries):
        raise ValueError('false whole oracle completion')
    return True


def assert_exact_model(expected, actual):
    """Own-model mutation tests only; never consumes product JSONL or launches it."""
    if type(expected) is not type(actual):
        raise ValueError('exact model type differs')
    if isinstance(expected, dict):
        if expected.keys() != actual.keys():
            raise ValueError('exact model fields differ')
        for key in expected:
            assert_exact_model(expected[key], actual[key])
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            raise ValueError('model tail/multiplicity differs')
        for a, b in zip(expected, actual):
            assert_exact_model(a, b)
    elif expected != actual:
        raise ValueError('model scalar differs')
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='rebuild in memory and require exact committed data bytes')
    args = parser.parse_args(argv)
    artifacts = construct()
    validate_oracle(artifacts['oracle.json'], read_pinned(ASSET), read_pinned(DESCRIPTOR))
    if not args.check:
        OUTPUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, value in artifacts.items():
        raw = json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False).encode() + b'\n'
        target = OUTPUT / name
        if args.check:
            if not target.exists() or target.read_bytes() != raw:
                raise ValueError('non-reproducible oracle artifact: ' + name)
        else:
            target.write_bytes(raw)
        rows.append({'path': str(target.relative_to(ROOT)), 'bytes': len(raw), 'sha256': digest(raw)})
    coverage = artifacts['coverage.json']
    print(json.dumps({'mode': 'check' if args.check else 'build', 'observations': 417,
                      'datasets': 320, 'statuses': coverage['byStatus'],
                      'wholeOracleComplete': coverage['wholeOracleComplete'], 'artifacts': rows}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
