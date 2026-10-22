"""Limited locator-correction delta; Git/docs/hash only, no product runs."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT=Path.cwd()
PACKET=Path('docs/reviews/T03/mapping-p2-dual-review-preparation-20261023')
OLD='70f4323fd574d7955fcbf7e581b2d06dd1f10e1c'
NEW='ff0b99f0992f5410b96528231035ff7c8c8e1ae4'

def git(*args,cwd=ROOT):
    return subprocess.check_output(['git',*args],cwd=cwd)

def read(path,ref=NEW):
    return git('show',ref+':'+str(path))

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

index_raw=read(PACKET/'dispatch-v2/dispatch-index.json')
index=json.loads(index_raw)
full_raw=read(PACKET/'dispatch-v2/full-candidate-tree.json')
result={'fixedProcess':NEW,'reviewHead':index['actualReviewHead'],'oldDispatchFilesExact':{},'scopeIndexUnchanged':full_raw==read(PACKET/'dispatch/full-candidate-tree.json',OLD),'scopeIndexIdentity':{'bytes':len(full_raw),'sha256':sha(full_raw)},'roots':[]}
for name in ['dispatch-index.json','full-candidate-tree.json','preparation-readback.json','mapping-P2-zcode-full-prompt.md','mapping-P2-minimax-full-prompt.md']:
    path=PACKET/'dispatch'/name
    result['oldDispatchFilesExact'][name]=read(path)==read(path,OLD)
changed=git('diff','--name-only',OLD,NEW).decode().splitlines()
result['changedPaths']=changed
result['onlyDocsChanged']=all(p.startswith('docs/') for p in changed)
for role in index['roots']:
    tree=Path(role['tree']);metadata=tree/'build/review-session/metadata'
    prompt=read(role['prompt'])
    task=json.loads((metadata/'task-actual.json').read_bytes())
    own_index=metadata/'full-candidate-tree-c1e44f81.json'
    tools=metadata/'preparation-tools-v2'
    manifest=json.loads((tools/'manifest.json').read_bytes())
    tools_exact=True
    for item in manifest['files']:
        raw=(tools/item['path']).read_bytes()
        tools_exact &= len(raw)==item['bytes'] and sha(raw)==item['sha256'] and raw==read(PACKET/'owner'/item['path'].removesuffix('.raw'))
    policies=[]
    for item in role['appendedPolicyOriginals']:
        block=prompt[item['offset']:item['offset']+item['bytes']]
        policies.append(sha(block)==item['sha256'] and block==read(PACKET/'control-snapshots'/item['name']))
    old=read(PACKET/'dispatch'/f"mapping-P2-{role['role']}-full-prompt.md",OLD)
    old_template=read(PACKET/'owner/full-review-template.md',OLD)
    new_template=read(PACKET/'owner/full-review-template.md')
    marker=b'**\xe5\xae\x8c\xe6\x95\xb41028'
    start=new_template.index(marker)
    end=new_template.index('## 完整审查范围'.encode(),start)
    result['roots'].append({'role':role['role'],'actualHead':git('rev-parse','HEAD',cwd=tree).decode().strip(),'status':git('status','--short',cwd=tree).decode(),'AGENTS':{'bytes':len((tree/'AGENTS.md').read_bytes()),'sha256':sha((tree/'AGENTS.md').read_bytes())},'prompt':{'bytes':len(prompt),'sha256':sha(prompt)},'ownPromptExact':(metadata/'dispatch-prompt.md').read_bytes()==prompt,'ownIndexExact':own_index.read_bytes()==full_raw,'headerNamesOwnAbsoluteIndex':str(own_index).encode() in prompt and sha(full_raw).encode() in prompt,'preparedIndexExact':(metadata/'dispatch-index-v2.prepared.json').read_bytes()==index_raw,'toolCopiesExact':bool(tools_exact),'toolCopiesCount':len(manifest['files']),'templateOnlyLocatorInserted':new_template[:start]+new_template[end:]==old_template,'policiesExact':all(policies),'legacySuffixExact':prompt[role['legacyOffset']:]==old[json.loads(read(PACKET/'dispatch/dispatch-index.json',OLD))['roots'][0 if role['role']=='zcode' else 1]['legacyOffset']:],'actualNull':all(task[k] is None for k in ['actualTask','actualSettings','sessionId','turnId','lease','terminalOutcome']),'taskPromptShaMatches':task['promptSha256']==sha(prompt),'actualSettingsRemainRequestedOnly':role['actualSettings'] is None})
result['runtimeExecuted']=False
print(json.dumps(result,ensure_ascii=False,indent=2))
