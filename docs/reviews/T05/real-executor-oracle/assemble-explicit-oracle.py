"""Serialize manually enumerated tables. No RDF parser, matcher, closure or value evaluator.

Every graph, accepted binding, comparison Boolean, head and RDFS witness below is an
explicit author decision. Helpers only encode triples/refs and copy approved INPUT
subtrees. Source expected/actual fields are never read to populate oracle values.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'tests/fixtures/quality/approved-T09-873c8c0'
OUT = ROOT / 'tests/fixtures/quality/real-executor-acceptance-inputs.json'
L = 'urn:ontolearn:learning:'
C = 'urn:ontolearn:quality:comparison-test:'
RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
RDFS = 'http://www.w3.org/2000/01/rdf-schema#'
OWL = 'http://www.w3.org/2002/07/owl#'
XSD = 'http://www.w3.org/2001/XMLSchema#'
PD = 'tests/fixtures/product-baselines/'

def load(rel):
    return json.loads((BASE / rel).read_text())

base = load(PD + 'G-base.json')
behavior = load(PD + 'G-behavior.json')
empty = load(PD + 'G-map-empty.json')
e5 = load(PD + 'E.5.json')
cases = load(PD + 'cases.json')['cases']
transfer = load('content/learning/transfer-inputs.json')
ext_path = ROOT / 'tests/fixtures/quality/fr505-extension-cases.json'
exts = json.loads(ext_path.read_text())
source_manifest = json.loads((ROOT / 'docs/reviews/T05/real-executor-oracle/inputs.json').read_text())
source_by_id = {s['id']: s for s in source_manifest['sources']}
triples = {}
lookup = {}
rules = {}
match = {}
graphs = {}
case_rows = []
witnesses = {}

def ref(file, pointer):
    key = file if file in source_by_id else 'T09/' + file
    return {'sourceId': key, 'sha256': source_by_id[key]['sha256'], 'pointer': pointer}

def iri(s):
    return '<' + s + '>'

def lit(s):
    return json.dumps(s, ensure_ascii=False)

def T(s, p, o, source=None, authored=None):
    """Encode an explicitly supplied ground triple; does not infer a statement."""
    key = (s, p, o)
    if key not in lookup:
        tid = 't' + str(len(triples) + 1).zfill(4)
        lookup[key] = tid
        triples[tid] = {'n3': [iri(s), iri(p), o], 'encodedFixtureTerms': [s, p, o],
                        'inputOccurrences': [], 'authoredDerivation': authored,
                        'rawImportToken': None, 'rawImportSource': 'unavailable',
                        'rawImportByteSpan': None}
    tid = lookup[key]
    if authored and triples[tid]['authoredDerivation'] is None:
        triples[tid]['authoredDerivation'] = authored
    if source and source not in triples[tid]['inputOccurrences']:
        triples[tid]['inputOccurrences'].append(source)
    return tid

def source_triples(rows, file, pointer):
    # INPUT copying and lossless RDF-term presentation only, never expected/actual.
    result = []
    for i, t in enumerate(rows):
        v = (t['subject'], t['predicate'], t['object']) if isinstance(t, dict) else t
        result.append(T(*v, source=ref(file, pointer + '/' + str(i))))
    return result

def unique(ids):
    # Set serialization. No inference/selection from graph contents.
    return sorted(set(ids))

O = source_triples(base['ontology'], PD + 'G-base.json', '/ontology')
B = source_triples(base['facts'], PD + 'G-base.json', '/facts')
BO = source_triples(behavior['ontology'], PD + 'G-behavior.json', '/ontology')
BF = source_triples(behavior['facts'], PD + 'G-behavior.json', '/facts')
EI = source_triples(e5['initialFacts'], PD + 'E.5.json', '/initialFacts')
EO = source_triples(e5['ontology'], PD + 'E.5.json', '/ontology')
RO = source_triples(transfer['repair']['ontology'], 'content/learning/transfer-inputs.json', '/repair/ontology')
RF = source_triples(transfer['repair']['facts'], 'content/learning/transfer-inputs.json', '/repair/facts')
CO = source_triples(transfer['classification']['ontology'], 'content/learning/transfer-inputs.json', '/classification/ontology')
CF = source_triples(transfer['classification']['facts'], 'content/learning/transfer-inputs.json', '/classification/facts')
XO = source_triples(exts['ontologyTriples'], 'tests/fixtures/quality/fr505-extension-cases.json', '/ontologyTriples')

rules['R-risk/base'] = {'definition': base['rules'][0], 'inputRef': ref(PD + 'G-base.json', '/rules/0')}
rules['R-risk/behavior'] = {'definition': behavior['rules'][0], 'inputRef': ref(PD + 'G-behavior.json', '/rules/0')}
rules['R-risk/E5'] = {'definition': e5['rules'][0], 'inputRef': ref(PD + 'E.5.json', '/rules/0')}
rules['R-risk/transfer'] = {'definition': transfer['classification']['rules'][0], 'inputRef': ref('content/learning/transfer-inputs.json', '/classification/rules/0')}

# Fixed author enumerations of source alarm partitions; never discover bindings by graph search.
# One row is one explicitly proved tuple and one head, not a generic rule interpreter.
positive_alarm_rows = [
    ('a01', '001', 'A01'), ('a04', '001', 'A04'), ('a06', '001', 'A06'),
    ('pump', 'P001', 'A-P001'), ('transfer', '201', 'T-A1'),
    ('e001', '001', 'AE001'), ('e002', '001', 'AE002'),
    ('e003', '001', 'AE003'), ('e004', '001', 'AE004'),
    ('e005', '001', 'AE005'), ('e006', '001', 'AE006'),
    ('e007', '001', 'AE007'), ('e008', '001', 'AE008'),
    ('e009', '001', 'AE009'), ('e010', '001', 'AE010'),
    ('e011', '001', 'AE011'), ('e012', '001', 'AE012'),
    ('e013', '001', 'AE013'), ('e014', '001', 'AE014'),
    ('e015', '001', 'AE015'), ('e016', '001', 'AE016'),
]
risk001 = T(L + 'equipment/001', RDF + 'type', iri(L + 'HighRiskEquipment'), authored='R-risk independent application, appendix G.2 R01/E.1')
riskpump = T(L + 'equipment/P001', RDF + 'type', iri(L + 'HighRiskEquipment'), authored='R04: subclass membership then independent R-risk')
risk201 = T(L + 'equipment/201', RDF + 'type', iri(L + 'HighRiskEquipment'), authored='transfer: Equipment201 and T-A1 High/Open')
for mid, eq, alarm in positive_alarm_rows:
    when = [T(L + 'equipment/' + eq, RDF + 'type', iri(L + 'Equipment')),
            T(L + 'equipment/' + eq, L + 'alarm', iri(L + 'alarm/' + alarm)),
            T(L + 'alarm/' + alarm, L + 'level', lit('High')),
            T(L + 'alarm/' + alarm, L + 'status', lit('Open'))]
    out = {'001': risk001, 'P001': riskpump, '201': risk201}[eq]
    match[mid] = {'ruleId': 'R-risk', 'bindings': {'?equipment': iri(L + 'equipment/' + eq), '?alarm': iri(L + 'alarm/' + alarm)},
                  'whenTripleIdsInDefinitionOrder': when, 'comparisons': [], 'accepted': True,
                  'heads': [{'headIndex': 0, 'tripleId': out}], 'leafBasisTripleIds': unique(when),
                  'reason': 'The explicitly listed same alarm has both High and Open and belongs to the listed Equipment.'}

# R04 is the sole nonempty finite RDFS addition in these fixed inputs.
critical_class = T(L + 'CriticalPump', RDF + 'type', iri(OWL + 'Class'))
critical_axiom = T(L + 'CriticalPump', RDFS + 'subClassOf', iri(L + 'Equipment'))
critical_fact = T(L + 'equipment/P001', RDF + 'type', iri(L + 'CriticalPump'))
pump_equipment = T(L + 'equipment/P001', RDF + 'type', iri(L + 'Equipment'), authored='R04 / finite rdfs9, level1')
witnesses['R04-equipment'] = {'resultTripleId': pump_equipment, 'axiomTripleIds': [critical_axiom],
    'orderedDirectPremiseTripleIds': [critical_fact, critical_axiom], 'leafBasisTripleIds': unique([critical_fact, critical_axiom]),
    'finiteRule': 'type-via-subClassOf (RDFS entailment rdfs9, selected finite subset)',
    'normativeBasis': 'Fixed PRD V0.6 FR501, appendix C finite RDFS, G.2 R04; type propagation along the explicitly supplied subclass axiom',
    'derivationLevel': 1, 'inputRefs': [],
    'witnessPolicy': 'one stable witness, only applicable pair here; not all possible formal proofs'}
# Replace the R04 assumption Equipment with its actual axiom and direct asserted leaf in rule basis.
match['pump']['leafBasisTripleIds'] = unique([critical_fact, critical_axiom, *match['pump']['whenTripleIdsInDefinitionOrder'][1:]])
match['pump']['rdfsWitnessRefs'] = ['R04-equipment']

# Explicit equality-free graph set assembly: no conditions, joins, fixed point or arithmetic evaluator.
def G(name, asserted, ontology=O, matches=('a01',), custom=(risk001,), rdfs=(), rule_refs=('R-risk/base',), why='base-partition', role='project-asserted'):
    graphs[name] = {'assertedTripleIds': unique(asserted), 'ontologyTripleIds': unique(ontology),
                    'rdfsAddedTripleIds': unique(rdfs), 'customOutputTripleIds': unique(custom),
                    'derivedUnionTripleIds': unique([*rdfs, *custom]), 'matchRefs': list(matches),
                    'rdfsWitnessRefs': ['R04-equipment'] if name == 'R04-complete' else [],
                    'ruleDefinitionRefs': list(rule_refs), 'completenessArgument': why, 'assertedRole': role,
                    'interpretation': 'independent mathematical expectation if this graph is reasoned; not a claim any job ran or a current result exists'}
    return name

G('base', B)
G('behavior-base', BF, BO, rule_refs=('R-risk/behavior',), why='behavior-literal-range')
G('map-empty', [], matches=(), custom=(), why='no-facts')
G('e5-initial', EI, EO, matches=(), custom=(), rule_refs=('R-risk/E5',), why='no-alarm', role='scenario-copy')
# Explicit indices in approved G-base (0..5 equipment, 6..9 A01, 10..13 A02, 14..17 A03).
G('base-no-A01', B[:6] + B[10:], matches=(), custom=(), why='only-closed-or-low')
G('base-no-A03', B[:14], why='only-A01-remains-positive')
G('behavior-no-A01', BF[:6] + BF[10:], BO, matches=(), custom=(), rule_refs=('R-risk/behavior',), why='behavior-literal-range-no-A01')
closed_a01 = T(L + 'alarm/A01', L + 'status', lit('Closed'), authored='Q02 explicit replacement')
G('A01-closed', B[:8] + [closed_a01] + B[9:], matches=(), custom=(), why='only-closed-or-low')
G('003-no-name', B[:5] + B[6:], why='name-not-in-rule')
for key, value in [('user', '用户名称')]:
    tid = T(L + 'equipment/001', L + 'name', lit(value), authored='Explicit input edit, not an inferred statement')
    G('base-name-' + key, B[:1] + [tid] + B[2:], why='name-not-in-rule')

# R03 addition and R04 input copying: read INPUT step subtrees, never old expected.
case_index = {c['id']: i for i, c in enumerate(cases)}
cmap = {c['id']: c for c in cases}
a04 = source_triples(cmap['R-03']['steps'][1]['facts'], PD + 'cases.json', '/cases/' + str(case_index['R-03']) + '/steps/1/facts')
G('base-plus-A04', B + a04, matches=('a01', 'a04'), why='two-same-output-matches')
G('base-A04-only', B[:6] + B[10:] + a04, matches=('a04',), why='only-A04-remains-positive')
pump_o = source_triples(cmap['R-04']['steps'][0]['triples'], PD + 'cases.json', '/cases/' + str(case_index['R-04']) + '/steps/0/triples')
pump_f = source_triples(cmap['R-04']['steps'][1]['facts'], PD + 'cases.json', '/cases/' + str(case_index['R-04']) + '/steps/1/facts')
# Bind witness to real case index rather than a guessed ordinal.
witnesses['R04-equipment']['inputRefs'] = [ref(PD + 'cases.json', '/cases/' + str(case_index['R-04']) + '/steps/0/triples/1'), ref(PD + 'cases.json', '/cases/' + str(case_index['R-04']) + '/steps/1/facts/0')]
G('R04-ontology-only', B, O + pump_o, why='subclass-present-no-instance')
G('R04-complete', B + pump_f, O + pump_o, matches=('a01', 'pump'), custom=(risk001, riskpump), rdfs=(pump_equipment,), why='R04-only-rdfs-pair')
needs_o = source_triples(cmap['R-05']['steps'][0]['triples'], PD + 'cases.json', '/cases/' + str(case_index['R-05']) + '/steps/0/triples')
rules['R-next'] = {'definition': cmap['R-05']['steps'][1]['rule'], 'inputRef': ref(PD + 'cases.json', '/cases/' + str(case_index['R-05']) + '/steps/1/rule')}
G('next-class-only', B, O + needs_o, why='base-partition')
G('chain-forward', B, O + needs_o, rule_refs=('R-risk/base', 'R-next'), why='no-feedback-R-next-zero-matches')
G('chain-reversed', B, O + needs_o, rule_refs=('R-next', 'R-risk/base'), why='no-feedback-R-next-zero-matches')

# CSV map graph sets are a manually enumerated four-statement mapping result.
MAP = [B[0], B[1], B[2], B[3]]
manual_name = T(L + 'equipment/001', L + 'name', lit('手工名称'))
note001 = T(L + 'equipment/001', L + 'note', lit('手工备注'))
note002 = T(L + 'equipment/002', L + 'note', lit('手工备注'))
G('map-two', MAP, matches=(), custom=(), why='no-alarm')
G('map-manual', [B[0], manual_name, B[2], B[3]], matches=(), custom=(), why='no-alarm')
G('map-two-note002', MAP + [note002], matches=(), custom=(), why='no-alarm')
G('map-001-note002', [B[0], B[1], note002], matches=(), custom=(), why='no-alarm')
G('imported', [B[0], manual_name, B[2], B[3], note001], matches=(), custom=(), why='no-alarm')
G('imported-user-edit', [B[0], T(L + 'equipment/001', L + 'name', lit('用户名称')), B[2], B[3], note001], matches=(), custom=(), why='no-alarm')

# Behavior source event payloads are INPUT triples; created action facts below are explicit expected action consequences.
for cid, base_ids, alarmmatch in [('B-01', B, ('a01','a04')), ('B-02', B, ('a01',)), ('B-03', B[:6]+B[10:], ('a06',)), ('B-07', B, ('a01','a04'))]:
    c = cmap[cid]; payload = c['steps'][0]['events'][0]['payload']['addFacts']
    extra = source_triples(payload, PD + 'cases.json', '/cases/' + str(case_index[cid]) + '/steps/0/events/0/payload/addFacts')
    G(cid + '-event', base_ids + extra, matches=alarmmatch, why='explicit-event-alarm-partition', role='scenario-copy')
    if cid == 'B-02':
        G(cid + '-commit', base_ids + extra, matches=alarmmatch, why='explicit-event-alarm-partition', role='scenario-copy')
    else:
        ev, order, status = {'B-01': ('E-B01','W:E-B01','待处理'), 'B-03': ('E-B03','W:E-B03','待处理'), 'B-07': ('E-B07','W1','待处理')}[cid]
        action_ids = [T(L+order,RDF+'type',iri(L+'WorkOrder'),authored=cid+' create-individual'), T(L+order,L+'workOrderStatus',lit(status),authored=cid+' action property'),T(L+ev,L+'eventOrder',iri(L+order),authored=cid+' add-relation')]
        G(cid+'-behavior',base_ids+extra+action_ids,matches=alarmmatch,why='workorder-does-not-affect-R-risk',role='scenario-copy')
        final_ids = action_ids if cid != 'B-07' else [action_ids[0],T(L+order,L+'workOrderStatus',lit('已完成'),authored='B07 capacity1 resource transition'),action_ids[2]]
        G(cid+'-commit',base_ids+extra+final_ids,matches=alarmmatch,why='workorder-does-not-affect-R-risk',role='scenario-copy')

# B06/10/11 action consequences manually fixed; P range does not infer a type on literal true/false.
bool_true = T(L+'T1',L+'P','"true"^^<'+XSD+'boolean>',authored='B06 X explicit update')
notif_y = [T(L+'N:E-B06:Y',RDF+'type',iri(L+'Notification'),authored='B06 Y frozen false condition'),T(L+'N:E-B06:Y',L+'notificationEvent',iri(L+'E-B06'),authored='B06 Y notification')]
G('B06-commit',BF[:19]+[bool_true]+BF[20:]+notif_y,BO,rule_refs=('R-risk/behavior',),why='behavior-literal-range',role='scenario-copy')
for key, wt, wo, ns in [('B10','S3','S4',['E-M4','E-M3']),('B11','S1','待处理',['E-M5','E-M6'])]:
    actions=[T(L+'W-test',L+'workOrderStatus',lit(wt),authored=key+' explicit action'),T(L+'W-other',L+'workOrderStatus',lit(wo),authored=key+' resulting status')]
    for ev in ns:
        nid='N:'+ev+':B-multi'
        actions += [T(L+nid,RDF+'type',iri(L+'Notification'),authored=key+' each instance notification'),T(L+nid,L+'notificationEvent',iri(L+ev),authored=key+' each instance notification')]
    G(key+'-commit',BF[:21]+[BF[22]]+actions,BO,rule_refs=('R-risk/behavior',),why='behavior-literal-range',role='scenario-copy')

# Transfer and course additions are separate resets; repair has no rule definition supplied.
G('transfer-repair-before', RF, RO, matches=(), custom=(), rule_refs=(), why='no-rules-or-rdfs-axioms')
repair_name=T(L+'equipment/102',L+'name',lit('供水泵'),authored='referenceCatalogue102 and explicit repair')
G('transfer-repair-after',RF+[repair_name],RO,matches=(),custom=(),rule_refs=(),why='no-rules-or-rdfs-axioms')
G('transfer-classification',CF,CO,matches=('transfer',),custom=(risk201,),rule_refs=('R-risk/transfer',),why='transfer-only-T-A1')
person_o=[T(L+'Person',RDF+'type',iri(OWL+'Class'),authored='course business-ontology task instruction'),T(L+'assignedTo',RDF+'type',iri(OWL+'ObjectProperty'),authored='course instruction')]
person_f=[T(L+'person/L01',RDF+'type',iri(L+'Person'),authored='course instruction'),T(L+'equipment/001',L+'assignedTo',iri(L+'person/L01'),authored='course instruction')]
G('ontology-model-delta-only', person_f, person_o, matches=(), custom=(), rule_refs=(), why='declarations-not-domain-or-range')
graphs['ontology-model-delta-only']['interpretation']='Only the four explicitly supplied additions, not an invented complete preexisting project graph; original course does not freeze that prior graph.'

# E5 explicit round/event/match and completed-order declarations, not a capacity simulator.
round_rows = [
    (1, ['e001','e002','e003','e004'], ['E001','E002','E003','E004']),
    (2, ['e001','e002','e003','e004','e005','e006','e007','e008'], ['E001','E002','E003','E004','E005','E006','E007','E008']),
    (3, ['e001','e002','e003','e004','e005','e006','e007','e008','e009','e010','e011','e012'], ['E001','E002','E003','E004','E005','E006','E007','E008','E009','E010','E011','E012']),
    (4, ['e001','e002','e003','e004','e005','e006','e007','e008','e009','e010','e011','e012','e013','e014','e015','e016'], ['E001','E002','E003','E004','E005','E006','E007','E008','E009','E010','E011','E012','E013','E014','E015','E016']),
]
# Explicitly selected completed IDs after each round per PRD E.5 queue analysis.
completed_table={
 '3':[['W001','W002','W003'],['W001','W002','W003','W004','W005','W006'],['W001','W002','W003','W004','W005','W006','W007','W008','W009'],['W001','W002','W003','W004','W005','W006','W007','W008','W009','W010','W011','W012']],
 '4':[['W001','W002','W003','W004'],['W001','W002','W003','W004','W005','W006','W007','W008'],['W001','W002','W003','W004','W005','W006','W007','W008','W009','W010','W011','W012'],['W001','W002','W003','W004','W005','W006','W007','W008','W009','W010','W011','W012','W013','W014','W015','W016']]}
event_input_ids={ev['id']:source_triples(ev['payload']['addFacts'],PD+'E.5.json','/events/'+str(i)+'/payload/addFacts') for i,ev in enumerate(e5['events'])}
# Rendering explicit expected WorkOrder records has no trigger/matching/queue logic.
order_atoms={}
for event_id,order_id in [('E001','W001'),('E002','W002'),('E003','W003'),('E004','W004'),('E005','W005'),('E006','W006'),('E007','W007'),('E008','W008'),('E009','W009'),('E010','W010'),('E011','W011'),('E012','W012'),('E013','W013'),('E014','W014'),('E015','W015'),('E016','W016')]:
    order_atoms[order_id]={'common':[T(L+order_id,RDF+'type',iri(L+'WorkOrder'),authored='E5 B-risk action1'),T(L+event_id,L+'eventOrder',iri(L+order_id),authored='E5 B-risk action2')],
    'pending':T(L+order_id,L+'workOrderStatus',lit('待处理'),authored='E5 action1'), 'completed':T(L+order_id,L+'workOrderStatus',lit('已完成'),authored='E5 resource phase')}
e5_records={}
for cap in ['3','4']:
    records=[]; prior_orders=[]; prior_completed=[]
    for round_n,mids,event_ids in round_rows:
        events_f=[t for e in event_ids for t in event_input_ids[e]]
        all_orders=['W'+e[1:] for e in event_ids]
        # Pure materialization of explicit completed_table into the two given status terms.
        def order_set(order_ids,done_ids):
            return [t for oid in order_ids for t in [*order_atoms[oid]['common'],order_atoms[oid]['completed' if oid in done_ids else 'pending']]]
        before=EI+events_f+order_set(prior_orders,prior_completed)
        behavior_f=EI+events_f+order_set(all_orders,prior_completed)
        final=EI+events_f+order_set(all_orders,completed_table[cap][round_n-1])
        label='e5-c'+cap+'-r'+str(round_n)
        G(label+'-event',before,EO,matches=mids,rule_refs=('R-risk/E5',),why='E5-all-arrived-alarms-High-Open',role='scenario-copy')
        G(label+'-behavior',behavior_f,EO,matches=mids,rule_refs=('R-risk/E5',),why='E5-all-arrived-alarms-High-Open',role='scenario-copy')
        G(label+'-commit',final,EO,matches=mids,rule_refs=('R-risk/E5',),why='E5-all-arrived-alarms-High-Open',role='scenario-copy')
        records.append({'round':round_n,'eventGraphRef':label+'-event','preBehaviorReasoningGraphRef':label+'-event','frozenConditionsGraphRef':label+'-event','behaviorGraphRef':label+'-behavior','resourceGraphRef':label+'-commit','roundEndReasoningGraphRef':label+'-commit','committedGraphRef':label+'-commit','arrivedEventIds':event_ids,'orderIds':all_orders,'completedOrderIds':completed_table[cap][round_n-1],'backlogOrderIds':[x for x in all_orders if x not in completed_table[cap][round_n-1]],'matchesBeforeAndAfterRefs':mids,'inputRef':ref(PD+'E.5.json','/events'),'semanticExecutionActuallyRun':False})
        prior_orders=all_orders;prior_completed=completed_table[cap][round_n-1]
    e5_records[cap]=records

# Extension inputs and independently written 18 integer comparison truth rows.
integer_decisions={
 'CMP-EQ-TRUE':('2','eq',True),'CMP-EQ-FALSE':('1','eq',False),
 'CMP-NE-TRUE':('1','ne',True),'CMP-NE-FALSE':('2','ne',False),
 'CMP-LT-TRUE':('1','lt',True),'CMP-LT-FALSE':('2','lt',False),
 'CMP-LE-TRUE':('2','le',True),'CMP-LE-FALSE':('3','le',False),
 'CMP-GT-TRUE':('3','gt',True),'CMP-GT-FALSE':('2','gt',False),
 'CMP-GE-TRUE':('2','ge',True),'CMP-GE-FALSE':('1','ge',False),
 'CMP-EQ-ABOVE-FALSE':('3','eq',False),'CMP-NE-ABOVE-TRUE':('3','ne',True),
 'CMP-LT-ABOVE-FALSE':('3','lt',False),'CMP-LE-BELOW-TRUE':('1','le',True),
 'CMP-GT-BELOW-FALSE':('1','gt',False),'CMP-GE-ABOVE-TRUE':('3','ge',True)}
matched=T(L+'equipment/001',RDF+'type',iri(C+'Matched'),authored='fixed comparison rule head, applied only to explicitly true rows')
multi_label=T(L+'equipment/001',C+'derivedLabel',lit('needs-review'),authored='multi-output head1')
for i,c in enumerate(exts['cases']):
    cid=c['id'];file='tests/fixtures/quality/fr505-extension-cases.json';pointer='/cases/'+str(i)
    xf=source_triples(c['inputTriples'],file,pointer+'/inputTriples')
    rr='extension/'+cid;rules[rr]={'definition':c['rules'][0],'inputRef':ref(file,pointer+'/rules/0')}
    if cid in integer_decisions:
        lexical,operator,truth=integer_decisions[cid]
        score='"'+lexical+'"^^<'+XSD+'integer>'
        when=[T(L+'equipment/001',RDF+'type',iri(L+'Equipment')),T(L+'equipment/001',C+'score',score)]
        match['cmp/'+cid]={'ruleId':cid,'bindings':{'?e':iri(L+'equipment/001'),'?score':score},'whenTripleIdsInDefinitionOrder':when,'comparisons':[{'comparisonIndex':0,'conditionIndex':2,'operator':operator,'left':score,'right':'"2"^^<'+XSD+'integer>','independentResult':truth,'derivation':'exact integers '+lexical+' and 2; manually enumerated 18-cell truth table'}],'accepted':truth,'heads':[{'headIndex':0,'tripleId':matched}] if truth else [],'leafBasisTripleIds':unique(when),'reason':'Only equipment001 has score; Equipment002/003 have no score. Threshold is a constant, never proof basis.'}
        G('extension/'+cid,xf,XO,matches=('cmp/'+cid,),custom=(matched,) if truth else (),rule_refs=(rr,),why='one-score-single-pattern-match')
    elif cid=='MULTI-OUTPUT-ONE-FIRING':
        match['multi']={**match['a01'],'ruleId':'R-risk-multi','heads':[{'headIndex':0,'tripleId':risk001},{'headIndex':1,'tripleId':multi_label}]}
        G('extension/'+cid,xf,XO,matches=('multi',),custom=(risk001,multi_label),rule_refs=(rr,),why='base-A01-one-match-two-heads')
    elif cid=='JOIN-NO-CROSS-ALARM':
        G('extension/'+cid,xf,XO,matches=(),custom=(),rule_refs=(rr,),why='A02-A04-closed-A03-A05-low-no-single-HighOpen')
    elif cid=='DISABLED-RULE-NO-OUTPUT':
        G('extension/'+cid,xf,XO,matches=(),custom=(),rule_refs=(rr,),why='disabled-rule-not-evaluated')
    elif cid=='MISSING-PROPERTY-IS-NOT-A-NEGATION':
        G('extension/'+cid,xf,XO,matches=(),custom=(),rule_refs=(rr,),why='no-score-no-match-not-negation')
    else:
        raise AssertionError('Unwritten extension decision '+cid)

# Each sequence below is explicit; no generic case-op interpreter.
# case, phase name, graph, reasoning intent. Repeated graph references do not merge resets.
sequences={}
def S(cid, rows, reset=None, obligations=None):
    sequences[cid]={'reset':reset or {'kind':'independent-original-baseline','baseline':cmap[cid]['baseline'],'scopeId':cid},'phases':[{'phaseId':n,'graphRef':g,'reasoningIntent':intent} for n,g,intent in rows],'originalNonGraphAcceptanceStillRequired':True,'obligations':obligations or []}
N='not-invoked-by-original-case; graph-only oracle, no published-result claim'
Y='reasoning-required-by-original-case; expected only, not run'
H='historical-or-stale-display; do not publish counterfactual recomputation'
for cid in ['A-03','A-04','A-05','A-06','A-07','A-08','A-09','A-10','B-08']:
    S(cid,[('reset','base',N),('after-each-nonmutating-operation','base',N)],obligations=['All original authorization/render/export/Agent or failed-tool acceptance remains; no RDF mutation is instructed.'])
S('A-01',[('reset','base',N),('preview-only','base',N),('manual-commit','base-name-user',N),('stale-C1-rejected','base-name-user',N)])
S('A-02',[('reset','base',N),('failed-mid-batch-no-commit','base',N),('reopen-committed','base',N)])
S('B-01',[('reset','base',Y),('event-applied-pre-behavior','B-01-event',Y),('behavior-complete','B-01-behavior',N),('resource-and-round-end','B-01-commit',Y),('repeat-no-change','B-01-commit',N)])
S('B-02',[('reset','base',Y),('low-event-pre-behavior','B-02-event',Y),('no-behavior-round-end','B-02-commit',Y)])
S('B-03',[('reset','base',N),('setup-remove-A01','base-no-A01',Y),('event-pre-behavior','B-03-event',Y),('behavior-complete','B-03-behavior',N),('round-end','B-03-commit',Y)])
S('B-04',[('reset','behavior-base',N),('prime-current','behavior-base',Y),('delete-before-probe','behavior-no-A01',Y),('no-stale-probe-notification','behavior-no-A01',Y)])
for cid in ['B-05','B-09']:
    S(cid,[('reset','behavior-base',Y),('event-pre-behavior','behavior-base',Y),('conflict-rollback-previous-commit','behavior-base',H)])
S('B-06',[('reset','behavior-base',Y),('frozen-false-condition','behavior-base',Y),('X-and-Y-both-executed','B06-commit',N),('round-end','B06-commit',Y)])
S('B-07',[('reset-and-replace-behavior','base',Y),('event-pre-behavior','B-07-event',Y),('behavior-W1-pending','B-07-behavior',N),('resource-W1-completed','B-07-commit',N),('round-end','B-07-commit',Y)])
S('B-10',[('reset','behavior-base',Y),('frozen-condition','behavior-base',Y),('both-distinct-target-actions','B10-commit',N),('round-end','B10-commit',Y)])
S('B-11',[('reset','behavior-base',Y),('frozen-condition','behavior-base',Y),('same-value-keep-both-notifications','B11-commit',N),('round-end','B11-commit',Y)])
for cid in ['G-list-01','G-list-02','G-list-06']:
    S(cid,[('independent-initial','e5-initial',Y)],obligations=['Use exact E5 branch/reset/replay expansion in e5RunPlans; no replay means executed.'])
S('G-list-03',[('independent-reset','behavior-base',Y),('alias-B09-conflict-rollback','behavior-base',H)],obligations=['Must run original B09 behavior conflict, not only this graph projection.'])
# G-list04 order records are explicit test state, no originating event is supplied or invented.
w1pending=[T(L+'W1',RDF+'type',iri(L+'WorkOrder'),authored='explicit committed WorkOrder record G-list04'),T(L+'W1',L+'workOrderStatus',lit('待处理'),authored='G-list04 committed record')]
w1working=[T(L+'W1',RDF+'type',iri(L+'WorkOrder')),T(L+'W1',L+'workOrderStatus',lit('已完成')),T(L+'W2',RDF+'type',iri(L+'WorkOrder'),authored='G-list04 uncommitted record'),T(L+'W2',L+'workOrderStatus',lit('待处理'),authored='G-list04 uncommitted record')]
G('cancel-committed',B+w1pending,why='workorder-does-not-affect-R-risk',role='scenario-copy')
G('cancel-uncommitted',B+w1working,why='workorder-does-not-affect-R-risk',role='uncommitted-scenario-workspace')
S('G-list-04',[('max-rounds-independent-initial','base',Y),('max-rounds-seed-no-data','base',Y),('cancel-independent-committed-round1','cancel-committed',H),('cancel-working-round2','cancel-uncommitted',N),('cancel-rollback-round2','cancel-committed',H)],reset={'kind':'independent-variants','branches':['max-rounds','cancel-round'],'noCrossBranchState':True},obligations=['Seed E-next remains pending; W2/uncommitted completed W1 never become committed; event origins for explicit order records unavailable.'])
S('G-list-05',[('V1-start','e5-initial',Y),('V2-config-save','e5-initial',N)],obligations=['V1 late payload not specified by fixture; do not invent a completion round/capacity. late run-v1 stays V1 historical; no V2 current result.'])
S('G-list-07',[('each-boundary-before','base',N),('after-crash-reopen-last-commit','base',N)],reset={'kind':'independent-variants','branches':['mapping-before-commit','changeset-mid-batch','scenario-before-round-commit'],'noCrossBranchState':True})
S('G-list-08',[('before-storage-failure','base',N),('failed-write-and-reopen','base',N)])
S('G-list-09',[('reset','map-empty',N),('map-first','map-two',N),('manual-001-name','map-manual',N),('updated-source-conflict','map-manual',N),('add-note','imported',N),('export-A-import-B','imported',N),('relink-and-conflict-rerun','imported',N)])
S('G-list-10',[('each-export-variant-source','base',N)],reset={'kind':'independent-variants','branches':['omit-asserted','omit-ownership','omit-both'],'noCrossBranchState':True},obligations=['Template packages do not restore a current graph; no restored full graph may be inferred from source graph.'])
S('G-list-11',[('reset','map-empty',N),('map','map-two',N),('export-import-no-source','map-two',N),('rerun-blocked-before-relink','map-two',N),('relink-rerun','map-two',N)])
S('G-list-12',[('complete-or-incomplete-manifest-input','e5-initial',N)],reset={'kind':'independent-variants','branches':['complete','omit-scenarioInput','omit-scenarioConfig','omit-behaviorVersion','omit-ruleVersion','omit-semanticsVersion'],'noCrossBranchState':True},obligations=['Missing manifest field means not replayable, never run or infer replacement output.'])
S('G-list-13',[('reset-then-G09','imported',N),('source-for-each-independent-imported-subcase','imported',N),('query-restored-imported','imported',N),('undo-only-deviceB-edit','imported',N)],obligations=['Imported branch subcases are explicitly expanded in importedSubcases; they reset to imported, not unrelated G-base.'])
S('M-01',[('reset','map-empty',N),('map','map-two',N)])
S('M-02',[('reset','map-empty',N),('map-first','map-two',N),('map-again-no-change','map-two',N)])
S('M-03',[('reset','map-empty',N),('map','map-two',N),('add-manual-note002','map-two-note002',N),('source-delete002','map-001-note002',N)])
for cid in ['M-04','M-06']:
    S(cid,[('reset','map-empty',N),('map','map-two',N),('manual-name','map-manual',N),('conflict-or-stale-preview-reject','map-manual',N)])
S('M-05',[('each-invalid-source-reset','map-empty',N),('failed-whole-batch','map-empty',N)],reset={'kind':'independent-variants','branches':['missing-key','duplicate-key'],'noCrossBranchState':True})
S('O-01',[('reset','base',N),('setup-remove-A03','base-no-A03',N),('inspect-003-unrecorded','base-no-A03',N)])
S('Q-01',[('reset','base',N),('query-current-asserted','base',N)])
S('Q-02',[('reset','base',N),('setup-close-A01','A01-closed',N),('query-empty','A01-closed',N)])
S('R-01',[('reset','base',N),('infer','base',Y)])
S('R-02',[('reset','base',N),('infer-V1','base',Y),('delete-A01-save','base-no-A01',H),('observe-stale-old-base-result','base-no-A01',H),('infer-V2-retract-risk','base-no-A01',Y)],obligations=['Before rerun old risk+a01 evidence retained only as stale/history for graph base, never as current evidence of graph base-no-A01.'])
S('R-03',[('reset','base',N),('infer-V1','base',Y),('add-A04-save','base-plus-A04',H),('remove-A01-save','base-A04-only',H),('infer-V2-A04-basis','base-A04-only',Y)],obligations=['Intermediate both-alarm mathematical graph has two matches but original case does not instruct an intermediate infer; old result is stale until final rerun.'])
S('R-04',[('reset','base',N),('add-subclass','R04-ontology-only',N),('add-P001-alarm','R04-complete',N),('infer-RDFS-then-rules','R04-complete',Y)])
S('R-05',[('reset','base',N),('add-class','next-class-only',N),('save-both-enabled','chain-forward',N),('infer-forward','chain-forward',Y)])
S('R-06',[('independent-source-reset','base',N),('reconstruct-R05-add-class','next-class-only',N),('independent-reconstruct-R05-enabled-both','chain-forward',N),('infer-original-order','chain-forward',Y),('save-reversed-both-enabled','chain-reversed',N),('infer-reversed','chain-reversed',Y)],reset={'kind':'independent-reconstruct-R05-precondition','scopeId':'R-06','bothEnabled':True,'noConsumptionOfPriorActualRun':True})
S('V-01',[('reset','base',N),('remove-003-name','003-no-name',N),('validate-violation','003-no-name',N),('repair-name','base',N),('validate-repaired','base',N)])

for i,c in enumerate(cases):
    assert c['id'] in sequences,c['id']
    case_rows.append({'id':c['id'],'inputRef':ref(PD+'cases.json','/cases/'+str(i)),
                      'inputVersion':c['inputVersion'],'inputSemanticsLabel':c['semanticsVersion'],
                      'sourceSetup':c['setup'],'sourceSteps':c['steps'],**sequences[c['id']]})

extensions=[]
for i,c in enumerate(exts['cases']):
    extensions.append({'id':c['id'],'inputRef':ref('tests/fixtures/quality/fr505-extension-cases.json','/cases/'+str(i)),
                       'reset':{'kind':'independent-exact-extension-input','scopeId':c['id'],'inheritBaseRules':False,'inheritPreviousResults':False},
                       'phases':[{'phaseId':'reset-and-input','graphRef':'extension/'+c['id'],'reasoningIntent':N},{'phaseId':'evaluate','graphRef':'extension/'+c['id'],'reasoningIntent':Y}]})

imported_subcases={
 'A-01':[('reset','imported'),('preview-no-write','imported'),('manual-edit','imported-user-edit'),('stale-reject','imported-user-edit')],
 'M-04':[('reset','imported'),('incoming-source-conflict','imported')],
 'M-06':[('reset','imported'),('preview','imported'),('manual-same-name','imported'),('old-preview-stale-reject','imported')],
 'A-02':[('reset','imported'),('mid-batch-failure-rollback','imported')]}
# Imported M06 uses the case's actual manual-name value, already present: even a same-value
# write must still satisfy the original G13/M06 stale-preview acceptance. The Store
# owner must implement the precise revision/conflict behavior; no no-op pass alternative
# is added here. Keep the exact original manual-name value.
imported_subcases['M-06']=[('reset','imported'),('preview','imported'),('manual-same-name','imported'),('old-preview-stale-reject','imported')]

run_plans={
 'G-list-01':[{'resetId':'G1-cap3-replay1','capacity':'3','initialGraphRef':'e5-initial','roundsRef':'3'}, {'resetId':'G1-cap3-replay2','capacity':'3','initialGraphRef':'e5-initial','roundsRef':'3'}, {'resetId':'G1-cap4-replay1','capacity':'4','initialGraphRef':'e5-initial','roundsRef':'4'}, {'resetId':'G1-cap4-replay2','capacity':'4','initialGraphRef':'e5-initial','roundsRef':'4'}],
 'G-list-02':[{'resetId':'G2-cap3','capacity':'3','initialGraphRef':'e5-initial','roundsRef':'3'}],
 'G-list-06':[{'resetId':'G6-cap3-replay1','capacity':'3','initialGraphRef':'e5-initial','roundsRef':'3'}, {'resetId':'G6-cap3-replay2','capacity':'3','initialGraphRef':'e5-initial','roundsRef':'3'}, {'resetId':'G6-explicit-round2-resume','capacity':'3','initialGraphRef':'e5-c3-r2-commit','resumeAfterRound':2,'roundNumbers':[3,4],'roundsRef':'3','preserveConsumedIds':['E001','E002','E003','E004','E005','E006','E007','E008']}]
}

supplemental=[
 {'id':'ontology-model','inputRef':ref('content/learning/course.json','/tasks/0'),'phases':[{'phaseId':'four-required-additions-only','graphRef':'ontology-model-delta-only','reasoningIntent':N}], 'graphScope':'Original course/check fixes addedTriples only; no full prior project graph specified. Delta graph is a projection, not a full current-project oracle.', 'reset':{'kind':'course-business-ontology-prior-project-unspecified','noDomainRangeInvented':True}},
 {'id':'transfer-repair','inputRef':ref('content/learning/transfer-inputs.json','/repair'),'phases':[{'phaseId':'fresh-independent-before','graphRef':'transfer-repair-before','reasoningIntent':N},{'phaseId':'repair-and-revalidate','graphRef':'transfer-repair-after','reasoningIntent':N}], 'reset':{'kind':'fresh-transfer-attempt','assistanceProvenanceMustPersist':True}},
 {'id':'transfer-classify','inputRef':ref('content/learning/transfer-inputs.json','/classification'),'phases':[{'phaseId':'asserted-input-derived-empty','graphRef':'transfer-classification','reasoningIntent':N},{'phaseId':'infer-and-classify-real-origins','graphRef':'transfer-classification','reasoningIntent':Y}], 'reset':{'kind':'another-fresh-transfer-case','initialPublishedDerived':[]}},
 {'id':'learning-report','inputRef':ref('content/learning/checks.json','/checks/learning-report'),'phases':[], 'graphScope':'No fixed RDF graph is supplied by this metadata/export check. Do not invent one or replace all T10 export requirements with empty graph success.', 'reset':{'kind':'report-current-version-grouped-input-selected-by-owner'}},
 {'id':'agent-full-assistance-negative','inputRef':ref('content/learning/transfer-inputs.json','/agentFullAssistanceNegative'),'phases':[{'phaseId':'before-assistance','graphRef':'transfer-repair-before','reasoningIntent':N},{'phaseId':'after-accepted-agent-repair','graphRef':'transfer-repair-after','reasoningIntent':N}], 'reset':{'kind':'fresh-transfer-attempt','mustNotLaunderAssistanceByReset':True},'independentTransferSuccess':False}
]

arguments={
 'base-partition':'No subclass/domain/range axioms. Equipment001-A01 is High/Open; Equipment002-A02 is High/Closed; Equipment003-A03 is Low/Open. R-risk has exactly one binding. Declarations alone add no finite RDFS facts.',
 'behavior-literal-range':'Only added inference axiom is P range xsd:boolean. Its objects are literals false/true, so finite URI-only range has no conclusion. Other extra facts have no R-risk alarm patterns; base A01 is the only positive binding.',
 'no-facts':'Ontology contains only declarations; asserted empty, so no subclass/domain/range candidate and no custom binding.',
 'no-alarm':'No alarm link and High/Open facts exist; no rule match. Ontology declarations introduce no axioms.',
 'only-closed-or-low':'A01 absent/Closed, A02 Closed, A03 Low: every available alarm fails at least one conjunct. No finite RDFS inference axiom.',
 'only-A01-remains-positive':'A03 removed, Equipment003 preserved; A01 High/Open only, A02 Closed; no negated absence or new class assertion.',
 'behavior-literal-range-no-A01':'P objects remain literals; range yields nothing. A01 removed; A02 Closed and A03 Low, so zero R-risk bindings.',
 'name-not-in-rule':'Only a name fact changes; name is not in R-risk and no domain/range/subclass axiom was added. Base partition remains complete.',
 'two-same-output-matches':'A01 and A04 both belong to001 and each independently High/Open. Exactly two bindings/heads, one deduplicated risk001 term. A02/A03 fail. No finite RDFS additions.',
 'only-A04-remains-positive':'A01 removed, A04 High/Open on001 remains; A02/A03 fail. Single A04 firing and no stale A01 premise.',
 'subclass-present-no-instance':'CriticalPump subClassOf Equipment is the only subclass edge; no CriticalPump instance yet and no outgoing Equipment subclass edge. No transitive addition or type propagation yet.',
 'R04-only-rdfs-pair':'CriticalPump→Equipment is the only subclass edge. P001 CriticalPump is the only instance of its subject class; type P001 Equipment is the only RDFS addition. Equipment has no successor edge, no domain/range. Base001/A01 and P001/A-P001 are exactly the two R-risk bindings; no custom feedback.',
 'no-feedback-R-next-zero-matches':'R-next is saved+enabled. Its required HighRiskEquipment type exists only in custom output, not the frozen asserted+RDFS input. Exactly zero R-next bindings; keep chain warning. R-risk still has only A01. No final RDFS pass.',
 'explicit-event-alarm-partition':'Explicit event input adds only its listed alarm. B01/B07: A01 and A04 positive; B02: A01 positive and A05 Low; B03: A01 deleted, A06 sole positive. A02 Closed/A03 Low. No finite RDFS axioms.',
 'workorder-does-not-affect-R-risk':'Only explicit WorkOrder type/status/eventOrder facts added or updated after event injection. These predicates do not add RDFS axioms or alter alarm patterns. The explicitly enumerated earlier alarm match set remains complete.',
 'no-rules-or-rdfs-axioms':'Repair fixture supplies declarations and name constraint, no rule definitions or finite RDFS inference axioms. No custom or RDFS output is implied by its ruleVersion label.',
 'transfer-only-T-A1':'201 Equipment linked only to T-A1 High/Open: exactly one rule binding, output risk201. No subclass/domain/range axiom.',
 'declarations-not-domain-or-range':'The supplied course delta contains Person/assignedTo declarations and two asserted instance/relation facts, no rules/domain/range axioms. Its finite graph projection has no outputs. Prior project graph is unspecified; do not infer it from glossary or G-base.',
 'E5-all-arrived-alarms-High-Open':'Exactly the enumerated arrived AE001..AE00n alarm links each carry High and Open on001; every one yields a distinct binding to the same risk001. Completing orders never changes alarm status. Future event facts are absent, no other Equipment facts/alarms/finite RDFS axioms.',
 'one-score-single-pattern-match':'Only001 has exactly one score triple and Equipment type. 002/003 have no score; exactly one positive triple-pattern binding before comparison. Manual truth table determines accepted Boolean; no base R-risk is inherited. No finite RDFS axiom.',
 'base-A01-one-match-two-heads':'Only A01 High/Open on001; one binding with head indices0/1 retained. Exactly risk001 and derivedLabel needs-review, both dedup-set and occurrence lists explicit; no base rule inheritance or feedback.',
 'A02-A04-closed-A03-A05-low-no-single-HighOpen':'001 A04 is High/Closed and A05 Low/Open; 002 A02 High/Closed; 003 A03 Low/Open. Shared alarm variable cannot combine A04 High with A05 Open: zero matches, zero heads. No finite RDFS axiom.',
 'disabled-rule-not-evaluated':'The only rule is disabled revision2. Its two heads and legal definitions remain in input; no enabled graph matches or outputs. R-risk is not inherited.',
 'no-score-no-match-not-negation':'No subject has score in the exact input graph, so zero complete when bindings. Constant comparison definition still valid; no false/negative fact inferred from missing property.'
}

# R1: the combined edit-and-undo endpoint is fixed; intermediate subject is not.
for c in case_rows:
    if c['id']=='G-list-13':
        c['unspecifiedIntermediate']={'operationRef':ref(PD+'cases.json','/cases/'+str(case_index['G-list-13'])+'/steps/3'),'selectedSubject':None,'intermediateGraph':None,'reason':'edit-and-undo gives name only; complete intermediate buffer not specified. End-of-operation undo restores imported exactly, never an empty graph.'}

# R2: same values do not establish actual baseline/source identity.
source_triples(empty['ontology'],PD+'G-map-empty.json','/ontology')
rules['R-risk/map']={'definition':empty['rules'][0],'inputRef':ref(PD+'G-map-empty.json','/rules/0')}
for gid,g in graphs.items():
    if gid.startswith(('map-','imported')):
        g['ruleDefinitionRefs']=['R-risk/map']
        g['effectiveBaselineRef']=ref(PD+'G-map-empty.json','')
        g['effectiveOntologyRef']=ref(PD+'G-map-empty.json','/ontology')
for c in case_rows:
    c['effectiveBaselineRef']=ref(PD+cmap[c['id']]['baseline']+'.json','')
source_triples(cmap['R-06']['steps'][0]['triples'],PD+'cases.json','/cases/'+str(case_index['R-06'])+'/steps/0/triples')
input_aliases={
 'map-ontology-same-values':{'left':ref(PD+'G-base.json','/ontology'),'right':ref(PD+'G-map-empty.json','/ontology'),'scope':'ontology values equal, actual case baseline remains G-map-empty'},
 'map-rule-same-values':{'left':ref(PD+'G-base.json','/rules/0'),'right':ref(PD+'G-map-empty.json','/rules/0'),'scope':'definition values equal, map graphs use actual map source'},
 'R06-class-same-values':{'left':ref(PD+'cases.json','/cases/'+str(case_index['R-05'])+'/steps/0/triples'),'right':ref(PD+'cases.json','/cases/'+str(case_index['R-06'])+'/steps/0/triples'),'scope':'shared representation, R06 actual class input'},
 'R06-rule-same-values':{'left':ref(PD+'cases.json','/cases/'+str(case_index['R-05'])+'/steps/1/rule'),'right':ref(PD+'cases.json','/cases/'+str(case_index['R-06'])+'/steps/1/rule'),'scope':'shared representation, R06 actual rule input'}
}
alias_values={'map-ontology-same-values':base['ontology'],'map-rule-same-values':base['rules'][0],'R06-class-same-values':cmap['R-05']['steps'][0]['triples'],'R06-rule-same-values':cmap['R-05']['steps'][1]['rule']}
for key,value in alias_values.items():
    input_aliases[key]['canonicalValueSha256']=hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    input_aliases[key]['equalityEncoding']='structural and sorted compact UTF8 JSON; not original formatted source bytes or producer authentication'
for c in case_rows:
    if c['id']=='R-06':
        c['effectiveAdditionalInputRefs']=[input_aliases['R06-class-same-values']['right'],input_aliases['R06-rule-same-values']['right']]
        c['inputValueAliasRefs']=['R06-class-same-values','R06-rule-same-values']
    elif cmap[c['id']]['baseline']=='G-map-empty':
        c['inputValueAliasRefs']=['map-ontology-same-values','map-rule-same-values']

# R3: existing exact ground JSON operation encodings get exact input pointers.
for cid,section,index in [('Q-02','setup',0),('A-01','steps',1),('M-04','steps',1),('M-06','steps',2)]:
    row=cmap[cid][section][index]
    T(row['subject'],row['predicate'],row['object'],source=ref(PD+'cases.json','/cases/'+str(case_index[cid])+'/'+section+'/'+str(index)))
source_triples(cmap['M-03']['steps'][1]['facts'],PD+'cases.json','/cases/'+str(case_index['M-03'])+'/steps/1/facts')
source_triples(cmap['G-list-09']['steps'][1]['facts'],PD+'cases.json','/cases/'+str(case_index['G-list-09'])+'/steps/1/facts')
# Explicit authored CSV consequences: never substitute identical G-base occurrences.
mapping_derivations={
 'csv-001-type':{'tripleId':B[0],'csvRef':ref(PD+'equipment.csv',''),'physicalLine':2,'key':'001','column':'equipment_id','rawCell':'001','mappingRef':ref(PD+'G-map-empty.json','/mappings/0'),'derivation':'subjectTemplate(key), declared Equipment type'},
 'csv-001-name':{'tripleId':B[1],'csvRef':ref(PD+'equipment.csv',''),'physicalLine':2,'key':'001','column':'equipment_name','rawCell':'泵站A','mappingRef':ref(PD+'G-map-empty.json','/mappings/0'),'derivation':'subjectTemplate(key), mapped name string'},
 'csv-002-type':{'tripleId':B[2],'csvRef':ref(PD+'equipment.csv',''),'physicalLine':3,'key':'002','column':'equipment_id','rawCell':'002','mappingRef':ref(PD+'G-map-empty.json','/mappings/0'),'derivation':'subjectTemplate(key), declared Equipment type'},
 'csv-002-name':{'tripleId':B[3],'csvRef':ref(PD+'equipment.csv',''),'physicalLine':3,'key':'002','column':'equipment_name','rawCell':'泵站B','mappingRef':ref(PD+'G-map-empty.json','/mappings/0'),'derivation':'subjectTemplate(key), mapped name string'}
}
for gid,g in graphs.items():
    if gid.startswith(('map-','imported')):
        g['mappingDerivationRefs']=[key for key,row in mapping_derivations.items() if row['tripleId'] in g['assertedTripleIds']]
        g['provenanceMeaning']='Explicit CSV mapping consequences plus manual-operation refs; canonical value dedup does not make G-base the CSV source.'

for graph_id,g in graphs.items():
    if graph_id in ['chain-forward','chain-reversed']:
        g['expectedSemanticWarnings']=[{'ruleId':'R-next','reason':'unsupported-rule-chain'}]
    else:
        g['expectedSemanticWarnings']=[]
    g['snapshotEncoding']='sorted canonical JSON of asserted/ontology/rule input refs only; local oracle binding, not producer authentication'
    payload={'asserted':[triples[t]['n3'] for t in g['assertedTripleIds']],'ontology':[triples[t]['n3'] for t in g['ontologyTripleIds']],'rules':[rules[r]['definition'] for r in g['ruleDefinitionRefs']]}
    g['oracleInputSha256']=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
# Exact original top-level operation coverage. Values are hand-selected after-operation
# graph references; branch-only instructions explicitly point to branch plans instead.
operation_graphs={
 'A-01':['base','base-name-user','base-name-user'], 'A-02':['base'],
 'A-03':['base','base','base'],'A-04':['base','base'],'A-05':['base','base','base','base','base'],
 'A-06':['base'],'A-07':['base'],'A-08':['base'],'A-09':['base'],'A-10':['base'],
 'B-01':['B-01-commit','B-01-commit'],'B-02':['B-02-commit'],'B-03':['B-03-commit'],
 'B-04':['behavior-base','behavior-no-A01'],'B-05':['behavior-base'],'B-06':['B06-commit'],
 'B-07':['B-07-commit'],'B-08':['base'],'B-09':['behavior-base'],'B-10':['B10-commit'],'B-11':['B11-commit'],
 'G-list-01':[None],'G-list-02':['e5-c3-r4-commit'],'G-list-03':['behavior-base'],
 'G-list-04':[None],'G-list-05':['e5-initial','e5-initial',None],
 'G-list-06':['e5-c3-r4-commit','e5-c3-r4-commit'],'G-list-07':['base','base'],
 'G-list-08':['base','base'],'G-list-09':['map-manual','imported','imported','imported','imported','imported'],
 'G-list-10':['base'],'G-list-11':['map-two','map-two','map-two','map-two','map-two','map-two'],
 'G-list-12':['e5-initial'],'G-list-13':['imported','imported','imported','imported'],
 'M-01':['map-two'],'M-02':['map-two','map-two'],
 'M-03':['map-two','map-two-note002','map-001-note002'],
 'M-04':['map-two','map-manual','map-manual'],'M-05':['map-empty'],
 'M-06':['map-two','map-two','map-manual','map-manual'],
 'O-01':['base-no-A03'],'Q-01':['base'],'Q-02':['A01-closed'],
 'R-01':['base'],'R-02':['base','base-no-A01','base-no-A01','base-no-A01'],
 'R-03':['base','base-plus-A04','base-A04-only','base-A04-only'],
 'R-04':['R04-ontology-only','R04-complete','R04-complete'],
 'R-05':['next-class-only','chain-forward','chain-forward'],
 'R-06':['next-class-only','chain-forward',None],
 'V-01':['003-no-name','003-no-name','base','base']}
setup_graphs={'B-03':['base-no-A01'],'B-07':['base'],'O-01':['base-no-A03'],'Q-02':['A01-closed']}
for c in case_rows:
    cid=c['id'];i=case_index[cid]
    assert len(operation_graphs[cid])==len(c['sourceSteps']),(cid,'step mapping count')
    assert len(setup_graphs.get(cid,[]))==len(c['sourceSetup']),(cid,'setup mapping count')
    c['operationGraphBindings']=[]
    for section,names in [('setup',setup_graphs.get(cid,[])),('steps',operation_graphs[cid])]:
        for j,gid in enumerate(names):
            row={'inputRef':ref(PD+'cases.json','/cases/'+str(i)+'/'+section+'/'+str(j)),
                 'afterGraphRef':gid,'oracleInputSha256':graphs[gid]['oracleInputSha256'] if gid else None}
            if gid is None:
                row['branchOrUnknownReason']={
                   'G-list-01':'e5RunPlans.G-list-01 contains four independent cap/replay branches',
                   'G-list-04':'max-rounds graph base; cancel-round graph cancel-committed; branches are independent',
                   'G-list-05':'late V1 completion round/payload unspecified; historical-selection obligation only, never invented V2 current output',
                   'R-06':'two independent save-order observations: chain-forward and chain-reversed; both rules enabled before each run'}[cid]
            c['operationGraphBindings'].append(row)
for cap,records in e5_records.items():
    for j,row in enumerate(records):
        row['beforeEventGraphRef']='e5-initial' if j==0 else records[j-1]['committedGraphRef']

for c in [*case_rows,*extensions,*supplemental]:
    for phase in c['phases']:
        phase['oracleInputSha256']=graphs[phase['graphRef']]['oracleInputSha256']
        phase['inputRef']=c['inputRef']

oracle={'version':'T05-real-executor-independent-oracle/1','status':'independent-expected-only-not-executed',
 'author':'T05 sole oracle author; independent reviewer read-only',
 'method':'Explicit hand-selected finite sets/bindings/witnesses; this script only serializes those decisions and approved input subtrees. No engine, RDF library, arbitrary matcher, closure solver, comparator, wrapper or actual-output import.',
 'inputsManifest':'docs/reviews/T05/real-executor-oracle/inputs.json',
 'termsConvention':{'triples':'dictionary IDs resolve to complete three N3 terms; subject/predicate IRI presentation has angle wrappers; no RDF/value normalization','setEquality':'exact resolved term sets for asserted/ontology/RDFS/custom, plus exact all match/head occurrences; counts insufficient','raw':'source pointers/hash refer to supplied fixture encodings, never original preimport Turtle token or producer authentication. raw unavailable and byteSpan null where not supplied. Generated action/head terms are authored expected only.','sourceLabel':'PRD-V0.6-E is an input label, not a new implementation executionSemanticsVersion'},
 'finiteRdfsRules':['subclass-transitivity (rdfs11 finite subset)','type-via-subclass (rdfs9 finite subset)','domain-type (rdfs2 finite subset)','range-type-for-IRI-object (rdfs3 finite subset)'],
 'excludedRdfs':'No generic axiomatic triples/reflexive class/subProperty/OWL inference; no matching label/comment; no custom feedback or final RDFS pass.',
 'inputValueAliases':input_aliases,'mappingDerivations':mapping_derivations,'triples':triples,'ruleDefinitions':rules,'matches':match,'rdfsWitnesses':witnesses,'graphs':graphs,
 'completenessArguments':arguments,'productCases':case_rows,'extensions':extensions,
 'supplementalLearningCases':supplemental,'e5Rounds':e5_records,'e5RunPlans':run_plans,'importedSubcases':imported_subcases,
 'publishedResultRules':{'unexecuted':'No published result/current proof can be inferred from mathematical oracle.','stale':'R02/03 old result keeps its original graph/input identity, explicit stale/history only until successful recompute.','historical':'G-list05 late V1 remains V1 historical, never relabelled V2.','cancel':'Rollback current uncommitted round, preserve previously committed historical rounds; explicit resume only.','undo':'G-list13 undo only last confirmed edit; not whole-project snapshot restore.'},
 'scopeBoundary':'50 fixed product cases and22 extensions plus supplemental graph inputs; original non-graph acceptance, whole57 P0, adopted nine-domain/six-numeric graph boundary matrix, actual E1/Store/lifecycle/UI/designated reviews/CI/merge remain pending.18 extension comparison cells are integer-only.'}
OUT.write_text(json.dumps(oracle,ensure_ascii=False,indent=2)+'\n')
print('Serialized explicit oracle',len(triples),'triples',len(graphs),'graphs',len(match),'match records',len(case_rows),'product cases',len(extensions),'extensions')
