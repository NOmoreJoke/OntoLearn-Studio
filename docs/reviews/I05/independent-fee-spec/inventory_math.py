"""Count frozen JSON fields; predict allocation only; do not interpret business triples."""
from pathlib import Path
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[4]
I = ROOT/'docs/iterations/I05/independent-fee-spec'
R = ROOT/'docs/reviews/I05/independent-fee-spec'
S = R/'author-v2-inputs'
# This local import is the independent mathematical file only, never engine code.
spec = importlib.util.spec_from_file_location('independent_fee_math', I/'invoice_model.py')
import sys
math = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = math
spec.loader.exec_module(math)
x = json.loads((S/'inputs.json').read_text())
g = json.loads((S/'gaps.json').read_text())
observations = {o['id']: o for o in x['observations']}
external_oracle = json.loads((S/'oracle.json').read_text())
external_rows = {o['id']:(i,o) for i,o in enumerate(external_oracle['observations'])}
assert len(observations)==417 and len(x['datasets'])==320

def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()

def census(value):
    out = {'valueNodes':0,'keyNodes':0,'stringUtf8BytesIncludingRepeatedFields':0}
    def walk(v):
        out['valueNodes'] += 1
        if type(v) is str:
            out['stringUtf8BytesIncludingRepeatedFields'] += len(v.encode())
        elif type(v) is list:
            for item in v: walk(item)
        elif type(v) is dict:
            for k, item in v.items():
                out['keyNodes'] += 1
                out['stringUtf8BytesIncludingRepeatedFields'] += len(k.encode())
                walk(item)
    walk(value)
    return out

# Literal independent integer truth witnesses, transcribed from pure inputs.
MATH = {
 'CMP-EQ-TRUE':(2,'eq',2,True), 'CMP-EQ-FALSE':(1,'eq',2,False),
 'CMP-NE-TRUE':(1,'ne',2,True), 'CMP-NE-FALSE':(2,'ne',2,False),
 'CMP-LT-TRUE':(1,'lt',2,True), 'CMP-LT-FALSE':(2,'lt',2,False),
 'CMP-LE-TRUE':(2,'le',2,True), 'CMP-LE-FALSE':(3,'le',2,False),
 'CMP-GT-TRUE':(3,'gt',2,True), 'CMP-GT-FALSE':(2,'gt',2,False),
 'CMP-GE-TRUE':(2,'ge',2,True), 'CMP-GE-FALSE':(1,'ge',2,False),
 'CMP-EQ-ABOVE-FALSE':(3,'eq',2,False), 'CMP-NE-ABOVE-TRUE':(3,'ne',2,True),
 'CMP-LT-ABOVE-FALSE':(3,'lt',2,False), 'CMP-LE-BELOW-TRUE':(1,'le',2,True),
 'CMP-GT-BELOW-FALSE':(1,'gt',2,False), 'CMP-GE-ABOVE-TRUE':(3,'ge',2,True),
}
rows=[]
for category, source in [('profile82',g['items']),('chain32',g['additionalProductionRestoreCases'])]:
    for j, gap in enumerate(source):
        o=observations[gap['id']]
        ds=x['datasets'][o['datasetId']]
        body=ds.get('input',ds)
        defs=body.get('definitions',body.get('rules'))
        disabled=body.get('disabled_rule_ids',[])
        if defs is not None:
            pred=math.allocation(tuple((d['rule_id'],d['rule_id'] in disabled) for d in defs))
            allocation_status='exact-value-prediction-not-capture'
            n=len(pred)
        else:
            pred=None; allocation_status='pending-omitted-rule-list-is-not-empty-proof'; n=None
        math_id=gap['id'].split('extension:')[-1]
        facts=[]
        if math_id in MATH:
            a,op,b,truth=MATH[math_id]
            facts.append({'status':'exact-independent-integer-truth','left':a,'operator':op,'right':b,
                          'result':truth,'proof':f'{a} {op} {b}; both have numerator itself, denominator1, limb1',
                          'doesNotProve':'graph matching completeness, producer admissibility or issuance'})
        op=o['operation']
        explanation=op=='dag' or o['parameters'].get('explanation') is True
        has_targets=bool(o['parameters'].get('rootsTargets'))
        if op=='restore-negative':
            relation='if producer succeeds and receiver bytes change, original held digests must reject before a view; no roots; resource earlier requires exact independently exhausted stage/domain'
            deps=['E01-E09','G01-G09','M01-M04','C01-C04','T01-T02','R01-R10']
            if explanation: deps += ['D01-D04']
        elif op=='profile':
            relation='complete mathematical execution conditional on all budgets/issuance; resource failure not automatically accepted'
            deps=['E01-E09','G01-G09','M01-M04','C02-C04']
        else:
            relation='complete same-issue fullview must preserve all fields; actual producer/restore success still pending'
            deps=['E01-E09','G01-G09','M01-M04','C01-C04','T01-T02','R01-R10']
            if explanation: deps += ['D01-D04']
            if has_targets: deps += ['S01']
        asset_bytes=dump(ds)
        predicted_n_defs=len(defs) if defs is not None else None
        row={
          'id':gap['id'],'category':category,'indexWithinCategory':j,'operation':op,
          'datasetId':o['datasetId'],'datasetPointer':gap.get('datasetPointer','/datasets/'+o['datasetId'].replace('~','~0').replace('/','~1')),
          'declaredInputProjectionSha256':o['projectionSha256'],
          'sourceRef':'0e42a0fe349054a92817cb4d463bccdc15f6c042',
          'independentAssetJsonMeasure':dict(bytes=len(asset_bytes),sha256=hashlib.sha256(asset_bytes).hexdigest(),
                 status='exact-own-canonical-JSON-domain-not-native-preimage-not-original-projection-domain',**census(ds)),
          'inputStructure':{'status':'exact-pure-JSON-counts','definitionCount':predicted_n_defs,
                 'assertedRecords':len(body['asserted']) if 'asserted' in body else None,
                 'ontologyRecords':len(body['ontology']) if 'ontology' in body else None,
                 'structuredRecords':len(body['records']) if 'records' in body else None,
                 'requestedTargetOccurrences':len(o['parameters'].get('rootsTargets',[])),
                 'disabledRuleIds':disabled},
          'predictedAllocation':{'status':allocation_status,'children':pred,
                 'revalidationCaps':math.revalidation_caps(pred) if pred is not None else None,
                 'basis':'I:76 and R:103; predictions cannot create OriginalAllocation, planDigest or issuer'},
          'conditionalCanonicalApiDefaultAllocation':None if pred is not None else {
                 'condition':'only if canonical execute_profile is actually called with omitted rules/disabled; fullview material/producer call binding is not supplied',
                 'values':math.allocation(()), 'source':'author-v2-inputs/api-defaults-reference.json',
                 'status':'exact-default-values-under-explicit-condition-not-current-call-proof-not-capture'},
          'mathFacts':facts,
          'existingIndependentBusinessExpected':{'status':'fixed-external-unreviewed-candidate-not-new-approved-requirement',
                 'ref':'3d8f4ee912f41bd03388322d29a9bfc0e7defe85',
                 'path':'tests/fixtures/quality/i05-source-package-oracle/oracle.json',
                 'fileSha256':'d8a91a9a1dc99def3187b3f77d9f88e5d2a95def08287fc672c8e5aa0fd5a9ab',
                 'pointer':'/observations/'+str(external_rows[gap['id']][0])+'/expected',
                 'expectedValueSha256':hashlib.sha256(dump(external_rows[gap['id']][1]['expected'])).hexdigest(),
                 'independentValueBoundary':'full business math remains separately consumable conditional on admission; pending fees do not erase this expected',
                 'feeAuthority':False},
          'providedHandSelection':{'status':'external-unreviewed-mathematical-context-not-current-actual',
                 'value':gap.get('knownFiniteSizesNotAdmissionProof'),
                 'notIndependentlyEnumeratedHere':True},
          'currentInvoice':{'status':'pending-exact','exact':None,
                 'conditionalMechanismWorkLowerBound':predicted_n_defs,
                 'lowerBoundPremise':'all supplied definitions reach compilation; only >=1 per definition is used; no unknown costs assigned zero',
                 'provenCompleteUpperBound':None,'firstExhaustedStage':None,'firstExhaustedDomain':None},
          'proposalInvoice':{'status':'event-formulas-exact-but-per-ID-event-program-not-yet-supplied',
                 'costVersion':'i05-fee-events/1-proposal','requiredScheduleGroups':deps,'amount':None},
          'authority':{'actualSameIssue17L':None,'actualPlanDigest':None,'actualBudgetUsage':None,
                 'producerIssuer':None,'sameIssueExpectedBinding':None,
                 'status':'pending-independent-from-predictable-values',
                 'missingReasons':['real original allocation capture','same production issuer/actual firing points',
                                   'original complete wire and expected preimages','real budgetUsage witness']},
          'decision':{'admission':'pending','resourceRejection':'not-automatically-allowed',
                 'exactFirstError':None,'finiteRelation':relation,
                 'mutation':gap.get('mutation'),'rootsCondition':'only after successful full restore and actual nonempty targets' if has_targets else 'not invoked by this observation',
                 'pendingDoesNotErase': 'input counts, full predicted17L where supplied, and exact integer facts remain usable'},
        }
        rows.append(row)
assert len(rows)==114 and len({r['id'] for r in rows})==114
assert sum(bool(r['mathFacts']) for r in rows)==18
out={'format':'i05-independent-fee-per-id/1','scope':{'profile':82,'productionRestoreChains':32,'observations':417,'datasets':320},
 'currentExactInvoices':0,'currentAdmissionStatus':'pending-incomplete-normative-action-schedules-and-authority',
 'unknownIsNotZero':True,'items':rows}
(I/'per-id.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
lines=['# 82 + 32 逐ID判定表','',
 '每行的 `17L` 指独立预测完整17字段及16c cap，详见同目录per-id.json，不是同次capture。所有114行完整现行invoice/首耗尽点/真实issuer/usage均pending；不得把该状态遮蔽可精确的结构、allocator或整数数学。`≥n`仅编译定义最小工作下界，非完整账。外部手选heads/matches只保给定数学上下文，不当本窗新枚举或旧actual。','',
 '| # | ID | operation / dataset | 17L预测 | 独立数学 / 给定结构 | 现行准入/首错 |',
 '| --- | --- | --- | --- | --- | --- |']
for q,r in enumerate(rows,1):
 pred=r['predictedAllocation']['children'];p=('exact '+','.join(str(c['rule_id'])+'@'+str(c['definition_ordinal']) for c in pred)) if pred else 'pending rules omitted'
 facts=r['mathFacts'];f=(str(facts[0]['left'])+' '+facts[0]['operator']+' '+str(facts[0]['right'])+' = '+str(facts[0]['result'])) if facts else '输入结构exact；图语义未在此枚举'
 if r['decision']['mutation']:f='原expectation不变；'+r['decision']['mutation']
 lines.append(f"| {q} | `{r['id']}` | {r['operation']} / `{r['datasetId']}` | {p} | {f} | pending；拒绝非自动Pass |")
(I/'per-id.md').write_text('\n'.join(lines)+'\n')
# Exact source line evidence and per-line hashes, no algorithm source reads.
manifest=json.loads((R/'input-manifest.json').read_text()); byname={r['name']:r for r in manifest}
claims=[]
for name,start,end,level in [
 ('q6',13,21,'behavior-exact'),('q6',50,50,'first-error-order'),('q6',58,67,'caps-and-lower-bound-not-full-exact'),
 ('integration',63,80,'allocator-exact-and-graph-cap'),('restore',23,23,'16c-contract'),
 ('restore',45,51,'wire-exact-and-physical-node-bound'),('restore',59,89,'schema-declarations-not-algorithms'),
 ('restore',93,99,'exact-key-and-cache-local-policy'),('restore',103,111,'allocator-lifecycle'),
 ('restore',117,136,'conservative-R-domain-bounds'),('restore',140,184,'R-proposed-fixed-schedule-and-local-proof'),
 ('restore',188,194,'conditional-parse-subset-and-16c-caps'),('producer',128,157,'proposed-C-T-S-H-bounds'),
 ('producer',161,180,'same-issue-selection-authority-and-retention'),
 ('direct',32,52,'direct-occurrence-order-and-issuance-contract'),('direct',117,155,'direct-fixed-charge-and-partial-upper-bounds')]:
 row=byname[name]; data=(ROOT/row['copy']).read_bytes().splitlines(keepends=True); block=b''.join(data[start-1:end])
 claims.append({'source':row,'startLine':start,'endLine':end,'level':level,
                'excerptBytes':len(block),'excerptSha256':hashlib.sha256(block).hexdigest(),
                'lines':[{'line':i+1,'utf8':data[i].decode().rstrip('\n'),'bytes':len(data[i]),
                          'sha256':hashlib.sha256(data[i]).hexdigest()} for i in range(start-1,end)]})
(R/'normative-claims.json').write_text(json.dumps(claims,ensure_ascii=False,indent=2)+'\n')
(I/'fee-contract.json').write_text(json.dumps({'version':'i05-fee-events/1-proposal','status':'not-adopted-not-current-product-proof',
    'currentMechanismVersion':'mechanism-budget/1','currentRevalidationVersion':'mechanism-revalidation-budget/2',
    'pools':math.POOLS,'structuralLimits':math.STRUCTURE,'fields17':list(math.POOLS)+list(math.STRUCTURE),
    'allocator':'T//N + int(sorted_index < T%N); N=max(1,definition_count); disabled included; original ordinal retained',
    'domainOrder':math.DOMAIN_ORDER,'proposalOnly':True,'missingIsNotZero':True},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'rows':len(rows),'profile':82,'chains':32,'mathIntegerFacts':18,
                 'predictedFullAllocations':sum(r['predictedAllocation']['children'] is not None for r in rows),
                 'exactCurrentCompleteInvoices':0,'productExecuted':False},ensure_ascii=False))
