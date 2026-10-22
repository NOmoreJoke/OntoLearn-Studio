"""Only fixed pure JSON inputs -> proposal fee artifacts. Never emits business results."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import traceback
import reference as r

HERE=Path(__file__).resolve().parent
REVIEW=HERE.parents[3]/'reviews'/'I05'/'independent-fee-spec'
FIXED={
 'inputs.json':(8205267,'47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa'),
 'oracle.json':(5651115,'d8a91a9a1dc99def3187b3f77d9f88e5d2a95def08287fc672c8e5aa0fd5a9ab'),
 'gaps.json':(327726,'4a0e72d103a156117e461810d1e0f27a4e96c8f69a56d405111cab34b99300e6')}

def load():
    result={}
    for name,(size,digest) in FIXED.items():
        raw=(REVIEW/'author-v2-inputs'/name).read_bytes()
        if (len(raw),r.sha(raw))!=(size,digest):raise ValueError('fixed input bytes/SHA mismatch: '+name)
        result[name]=json.loads(raw)
    return result

def write(path,value):path.write_bytes(r.canonical(value)+b'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--attempt',required=True)
    parser.add_argument('--baseline-only',action='store_true');parser.add_argument('--events',default=None)
    args=parser.parse_args()
    evidence=REVIEW/('r4-reference-'+args.attempt+'.json')
    if evidence.exists():raise ValueError('attempt evidence must never be overwritten')
    code=r.sha((HERE/'reference.py').read_bytes());log={'attempt':args.attempt,'argv':sys.argv,
          'sourceSha256':code,'driverSha256':r.sha(Path(__file__).read_bytes()),'fixedInputs':FIXED,'cases':[]}
    try:
        data=load();inputs=data['inputs.json'];oracle=data['oracle.json'];gaps=data['gaps.json']
        ii={v['id']:v for v in inputs['observations']};oi={v['id']:v for v in oracle['observations']}
        ids=[g['id'] for g in gaps['items']+gaps['additionalProductionRestoreCases']]
        if len(ids)!=114 or len(set(ids))!=114:raise ValueError('82+32 identity scope')
        if args.baseline_only:ids=ids[:1]
        if args.events:
            if args.events not in ids:raise ValueError('outside fixed 114 ID scope')
            ids=[args.events]
        items=[]
        for id in ids:
            observation=ii[id];exp=oi[id]['expected'];business=exp.get('conditionalBusinessExpected',exp.get('businessMath'))
            result,material=r.make_program(observation,inputs['datasets'][observation['datasetId']],business,code)
            if result['firstError'] and result['firstError']['reason']!='RESOURCE_LIMIT':raise ValueError('unexpected semantic rejection in fixed114: '+id+' '+str(result['firstError']))
            if not all(result['independentMathematicalChecks'].values()):raise ValueError('independent mathematical witness disagreement: '+id+' '+str(result['independentMathematicalChecks']))
            if id==ids[0] and (args.baseline_only or args.events):
                write(HERE/'baseline-prefix-r4.json' if args.baseline_only else HERE/'requested-prefix-r4.json',result)
                if args.baseline_only:
                    (HERE/'baseline-fee-material-r4.json').write_text(json.dumps(r.project(material),ensure_ascii=False,separators=(',',':'))+'\n')
                    (HERE/'baseline-fee-material-r4.bytes.hex').write_text(r.encode(material).hex()+'\n')
            events=result.pop('events');result.pop('executionEvents')
            result['programRecipe']={'interpreter':'reference.py','driver':'run_reference.py','commandEventArgument':id,
                'fixedInputs':FIXED,'observationPointer':'/observations/'+str(inputs['observations'].index(observation)),
                'independentExpectedPointer':'/observations/'+str(oracle['observations'].index(oi[id]))+'/expected',
                'parameters':observation['parameters'],'eventSequenceSha256':result['programSha256'],
                'programHasNoCallerSuppliedFeeVariables':True}
            result['requiredScheduleGroups']=['E00-whole-rule-metadata','E01-E09','G01-G09','M01-M04','C02-C04','H01']+(['R01-R17'] if result['operation']!='profile' else [])+(['D01-D08'] if 'Dc' in result['amount'] else [])+(['Q01-Q03'] if 'ROOTS' in result['amount'] else [])
            items.append(result)
            log['cases'].append({'id':id,'eventCount':len(events),'programSha256':result['programSha256'],
                'mathematicalChecks':result['independentMathematicalChecks'],'firstLimit':result['firstLimit'],'exit':0})
            print(id,len(events),'fits' if result['firstLimit'] is None else 'prefix-refusal',flush=True)
        if not args.baseline_only and not args.events:
            write(HERE/'all114-fee-programs-r4.json',{'format':'i05-proposal-only-fee-programs/4','sourceSha256':code,
                'scope':{'profile82':82,'chains32':32},'currentExactInvoiceClaim':False,'items':items})
        log['exit']=0
    except BaseException:
        log['exit']=1;log['firstFailure']=traceback.format_exc()
    write(evidence,log)
    if log['exit']:print(log['firstFailure'],file=sys.stderr)
    return log['exit']

if __name__=='__main__':sys.exit(main())
