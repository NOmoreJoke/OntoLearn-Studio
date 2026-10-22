"""Preserve R3 current/mathematical fields; replace only the R4 proposal column."""
from pathlib import Path
import json
import reference as r
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
old=json.loads((PARENT/'per-id-r3.json').read_text())
programs=json.loads((HERE/'all114-fee-programs-r4.json').read_text())
by_id={x['id']:x for x in programs['items']}
items=[]
for original in old['items']:
    item=json.loads(json.dumps(original));p=by_id[item['id']]
    item['proposalInvoice']={
        'status':'complete-computable-proposal-program-no-current-exact-claim',
        'state':p['state'],'firstError':p['firstError'],'executionEventCount':p['executionEventCount'],'executionSha256':p['executionSha256'],'H01Paid':p['finalization']['H01Paid'],
        'costVersion':p['version'],'requiredScheduleGroups':p['requiredScheduleGroups'],
        'amount':p['amount'],'paidPrefix':p['paidPrefix'],'firstLimit':p['firstLimit'],
        'componentCapDecision':p['feeAdmission'],'peak':p['peak'],
        'wholeOwnerHRequiredPeak':p['wholeOwnerHRequiredPeak'],
        'eventCount':p['programEventCount'],'programSha256':p['programSha256'],
        'programSourceSha256':p['programSourceSha256'],
        'r4IndependentDeltaPointer':'charge-reference-v4/metadata-delta-r4.json#/items/'+str(len(items)),
        'completeProgramPointer':'charge-reference-v4/all114-fee-programs-r4.json#/items/'+str(len(items)),
        'programRecipe':p['programRecipe'],'H01Required':True}
    item['pureMathematicalProgram']={'counts':p['mathematicalCounts'],
          'independentFullSetAndWitnessChecks':p['independentMathematicalChecks'],
          'currentFeeAuthority':False}
    item['proposalBinder']={'feeMaterialSha256':p['feeMaterialSha256'],
          'entryMetadata':p['entryMetadata'],
          'fieldOriginsPointer':'charge-reference-v4/all114-fee-programs-r4.json#/items/'+str(len(items))+'/fieldOrigins',
          'sourceLocatorIsSourceRecord':False,'headsGrantCatalogPermission':False,
          'actualSameIssueAuthority':p['actualSameIssueAuthority']}
    items.append(item)
r2={**old,'format':'i05-independent-fee-per-id/4','supersedes':'per-id-r3.json (R1/R2/R3 preserved)',
    'currentAdmissionStatus':'pending-current-encoding-and-real-same-issue-authority','proposalCompleteProgramCount':len(items),'proposalSourceSha256':programs['sourceSha256'],'items':items}
(PARENT/'per-id-r4.json').write_bytes(r.canonical(r2)+b'\n')
lines=['# 82+32 逐 ID 的数学、提案费用及现行权威分栏','',
'此表的金额均为新提案收费程序；每行完整分池金额、原预测17L、数学值/全集核对、绑定来源和首拒 prefix 在 [per-id-r4.json](per-id-r4.json)；完整编程配方、fieldOrigins、receipt 字节及逐池 live 在 [114 程序](charge-reference-v4/all114-fee-programs-r4.json)。真实同次 limits/usage/issuer、现行 wire/codec 仍分别 pending。旧 R1 表保持原件，不能当本版表。','',
'每行 `H01` 都包含 receipt/累积 cleanup 静态预付和 terminal 清理。`fits` 仅新程序分池可容纳；owner H 仍须真实额度，不证明当前产品成功。`refusal` 是下列精确前缀，不授权任意 RESOURCE_LIMIT。','',
'| ID | 数学 records/matches/firings/heads/RDFS | 提案 work 各池 | 事件/提案首拒 | 现行真权威 |',
'| --- | --- | --- | --- | --- |']
for p in programs['items']:
    c=p['mathematicalCounts'];nums='/'.join(str(c[k]) for k in ('seedRawOccurrences','matches','acceptedFirings','headOccurrences','rdfsTriples'))
    fees='; '.join(w+'='+str(v['work']) for w,v in p['amount'].items())
    first=p['firstLimit'];decision='fits' if first is None else str(first['event'])+':'+first['wallet']+'/'+first['domain']
    lines.append('| '+p['id']+' | '+nums+' | '+fees+' | '+str(p['programEventCount'])+'/'+decision+'; H01 | pending |')
(PARENT/'per-id-r4.md').write_text('\n'.join(lines)+'\n')
print('bound',len(items),'amount-null',sum(x['proposalInvoice']['amount'] is None for x in items))
