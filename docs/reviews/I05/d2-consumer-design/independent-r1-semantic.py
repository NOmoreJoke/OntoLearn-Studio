"""Read-only, separately authored finite design semantic checks.

Only pathlib/json/hashlib/copy from stdlib; no candidate import or execution.
Prints detached synthetic counterexamples and exact document relationships.
Not a complete receipt/schema validator, RDF comparator, or actual certificate.
"""
import copy
import hashlib
import json
import pathlib

ROOT = pathlib.Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design')
R = ROOT/'docs/reviews/I05/d2-consumer-design'
D = ROOT/'docs/iterations/I05/d2-consumer-design'
OUT = []


def read(p):
    return json.loads(p.read_text())


def record(name, actual, expected):
    OUT.append({'name':name,'actual':actual,'expected':expected,'pass':type(actual) is type(expected) and actual==expected})


def canon(v):
    return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def sample_decision(v):
    # Independent finite predicate for the AUTHOR'S DETACHED SAMPLE domain.
    # Flags are illustrative assertions, never proofs of actual loader/raw data.
    if type(v['count']) is not int or v['count']<0:
        return False
    if v['signal'] is not None and v['exit'] is not None:
        return False
    if v['hasActualFalse'] and not v['observedFalseIncluded']:
        return False
    if v['state']=='not-started':
        return (not any(v[k] for k in ('dispatched','stdoutPresent','stderrPresent','complete','full'))
                and v['exit'] is None and v['signal'] is None and v['count']==0
                and v['header']==v['terminal']=='absent' and v['failure'])
    if not all(v[k] for k in ('dispatched','stdoutPresent','stderrPresent')):
        return False
    if v['state']=='pre-header-rejected':
        return (type(v['exit']) is int and v['exit']==2 and v['signal'] is None
                and v['header']==v['terminal']=='absent' and v['failure']
                and not v['complete'] and not v['full'])
    if v['state']=='incomplete':
        return (v['failure'] and not v['complete'] and not v['full']
                and v['header'] in ('absent','malformed','parsed')
                and v['terminal'] in ('absent','malformed','parsed'))
    if v['state']!='collected':
        return False
    gates=('idsUniqueOrdered','codeDomainMatches','moduleSetComplete','functionsComplete',
           'checkerSame','argvExact','headerDigestMatches','complete')
    if not all(v[k] for k in gates) or v['failure'] or v['selfPinEmbedded']:
        return False
    if not (type(v['exit']) is int and v['exit']==0 and v['signal'] is None and v['header']==v['terminal']=='parsed'):
        return False
    if v['sourceMode']:
        if (v['declaredSources'],v['actualSources'])!=(22,23):return False
    elif v['declaredSources']!=23 or not v['frozenSourceNull']:
        return False
    return ((v['selector']=='full-v1' and v['count']==417 and v['full']) or
            (v['selector'] in ('b1-semantic-1x-v1','b1-semantic-10x-v1') and v['count']==1 and not v['full']))


def main():
    fields=read(D/'field-origin-map.json')
    a=read(D/'acceptance-map.json')
    rejects=read(D/'reject-cases.json')
    h=read(R/'fixed-inputs/06-runtime-header.schema.json')
    rv=read(R/'fixed-inputs/07-runtime-validation-receipt.schema.json')
    bp=read(R/'fixed-inputs/04-build-provenance.schema.json')
    br=read(R/'fixed-inputs/05-build-receipt.schema.json')
    run=rv['properties']['runs']['items']['properties']
    record('headerPayload-schema-complete-core',run['headerPayload']['anyOf'][0],{k:v for k,v in h.items() if k not in ('$schema','$id','title','$comment')})
    record('E0-dynamic-checker-no-runtimeLoaderCode','runtimeLoaderCode' in bp['properties']['dynamicChecker']['properties'],False)
    record('immutable-build-runtimeValidation',br['properties']['runtimeValidation']['const'],'not-executed')
    record('immutable-build-runtimeEvidenceManifest',br['properties']['runtimeEvidenceManifest'],{'const':None})
    mapping=[]
    direct={'mode','selector','externalReceiptStatus','declaredCompositionRef','moduleLoaders',
            'distributionModuleLoader','functionCodes','dynamicChecker','observedSource23',
            'packageCodeBoundToSource','sourceCodeBoundToSource'}
    for row in fields['fieldRows']:
        if row['schema']!='runtime-header.schema.json':continue
        expected=[]
        for loc in row['instanceLocations']:
            path=loc['pointerTemplate']
            expected.append('/runs/{run}/headerPayload'+path)
            top=path.split('/')[1]
            suffix=path
            if top in ('moduleLoaders','functionCodes'):
                suffix=suffix.replace('/{i0}', '/{member}',1)
            if top in direct:
                expected.append('/runs/{run}'+suffix)
            elif top=='observedPython':
                expected.append('/runs/{run}'+path.replace('/observedPython','/python',1))
            elif path=='/provenanceRead/sha256':
                expected.append('/runs/{run}/provenanceSha256')
        actual=[x['receiptPointerTemplate'] for x in row['crossLayerDisposition']['destinations']]
        mapping.append({'id':row['id'],'source':row['schemaPointer'],'expectedDestinations':expected,'actualDestinations':actual,'pass':expected==actual})
    record('all-150-header-raw-payload-run-destination-relations',all(x['pass'] for x in mapping),True)
    source_lines=(R/'fixed-inputs/24-contract.md').read_text().splitlines()
    for i,req in enumerate(a['completeLegacyFamilyRequirements']):
        fixed=req['fixedSource']
        record('full-legacy-family-row-'+str(i),source_lines[fixed['line']-1],fixed['text'])
    record('all-75-reject-design-rules-exist',all(x['rule'] in {r['id'] for r in a['rules']} for x in rejects['cases']),True)
    declared=[]
    for c in rejects['finiteSyntheticCases']:
        result=bool(sample_decision(c['value']))
        declared.append({'name':c['name'],'value':c['value'],'actual':result,'expected':c['expected'],'pass':result is c['expected']})
    record('all-34-detached-author-samples-independently-decided',all(x['pass'] for x in declared),True)
    # New contract-derived examples: intentionally small detached records.
    keys=set(h['properties'])
    good=dict.fromkeys(keys,None)
    wrong={**good,'runId':'legacy-run'}
    record('G02-legacy-runId-cannot-be-extra-strict-header-key',set(wrong)==keys,False)
    record('G02-strict-header-has-exact18-keys',len(keys),18)
    raw=b'{"sameConsumerObject":false}'
    parsed=json.loads(raw)
    tampered={'sameConsumerObject':None}
    tampered_mask=[]
    original_nonnull=[k for k,v in parsed.items() if v is not None]
    record('raw-false-cannot-be-erased-with-mask',parsed==tampered and original_nonnull==tampered_mask,False)
    record('raw-false-sha-bound-to-original',hashlib.sha256(raw).hexdigest()==hashlib.sha256(canon(tampered).encode()).hexdigest(),False)
    full=['case-'+str(i) for i in range(417)]
    reordered=full[:-2]+list(reversed(full[-2:]))
    record('same-count-unique417-reordered-is-not-full-inventory',reordered==full,False)
    record('same-count-unique417-substitution-is-not-full-inventory',full[:-1]+['other-case']==full,False)
    stage={'production':'failed','A1':'not-reached','heldBytesChanged':False}
    record('production-failure-cannot-become-A1-mismatch',stage['production']=='passed' and stage['heldBytesChanged'] and stage['A1']=='mismatch',False)
    identities=[None,None,None]
    results=[None,None,False]
    record('comparison-pending-rejects-false-as-null',all(x is None for x in identities+results),False)
    for truth in [(False,False,False),(True,False,True),(False,True,False)]:
        record('compared-independent-bools-'+str(truth),all(type(x) is bool for x in truth),True)
    record('frozen-canonical-and-distribution-source-null',all(x is None for x in [None,None,{'bytes':1}]),False)
    source=(R/'fixed-inputs/13-spec.md').read_text()
    projection=read(R/'fixed-inputs/16-cases.json')['cases']
    record('exact-shape-invocation-preserved-in-whole-case','invocation' in next(x for x in projection if x['id']=='shape/front-2'),True)
    record('exact-integer-invocation-preserved-in-whole-case','invocation' in next(x for x in projection if x['id']=='integer/other-datatype-1'),True)
    record('G03-full-old-source-metadata-explicitly-unclosed',any(x['id']=='G03' and 'metadata' in x['material'] for x in a['gaps']),True)
    print(json.dumps({'class':'finite-static-semantic-design-only','checks':OUT,'headerMappings':mapping,'authorDetachedSamplesIndependentlyChecked':declared,'issues':[x['name'] for x in OUT if not x['pass']],'wholeOracleComplete':False,'productExecuted':False,'schemaEngineValidation':False},ensure_ascii=False,indent=2))
    raise SystemExit(0 if all(x['pass'] for x in OUT) else 1)


if __name__=='__main__':
    main()
