"""Opaque old-artifact integrity and explicit R3 manifest; no old code execution."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[5]
BASE='8d703858a9e7777e0086057032aea280316e49c1'
PREFIXES=('docs/iterations/I05/independent-fee-spec/','docs/reviews/I05/independent-fee-spec/')
REVIEW=ROOT/PREFIXES[1]
EXCLUDED=(PREFIXES[1]+'artifact-manifest-r3.json',PREFIXES[1]+'r3-author-process-receipt.json')
def sha(b):return hashlib.sha256(b).hexdigest()
def run(*args):
    p=subprocess.run(args,cwd=ROOT,capture_output=True)
    if p.returncode:raise AssertionError((args,p.returncode,p.stderr.decode()))
    return p.stdout
def main():
    report=REVIEW/'r3-final-integrity.json';manifest=ROOT/EXCLUDED[0]
    if report.exists() or manifest.exists():raise ValueError('immutable freeze already exists')
    assert run('git','rev-parse','HEAD').decode().strip()==BASE
    assert not run('git','diff','--cached','--name-only')
    protected=(ROOT/'AGENTS.md').read_bytes()
    assert (len(protected),sha(protected))==(15147,'de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4')
    before=[]
    # Deliberately opaque: including exposure quarantine, no content decoding.
    for item in run('git','ls-tree','-rz',BASE,'--',*PREFIXES).split(b'\0'):
        if not item:continue
        head,path=item.split(b'\t',1);mode,kind,oid=head.split();name=path.decode()
        assert kind==b'blob'
        original=run('git','cat-file','blob',oid.decode());current=(ROOT/name).read_bytes()
        assert current==original,name
        before.append({'path':name,'bytes':len(current),'sha256':sha(current),'baseBlob':oid.decode(),'currentEqualsBaseGit':True,'opaque':True})
    changed=run('git','diff','--name-only',BASE).decode().splitlines()
    assert changed==['AGENTS.md'],changed
    untracked=run('git','ls-files','--others','--exclude-standard','-z').split(b'\0')
    new=[p.decode() for p in untracked if p]
    assert all(p.startswith(PREFIXES) for p in new),new
    static=[]
    here=Path(__file__).resolve().parent
    for path in sorted(here.glob('*.py')):
        tree=ast.parse(path.read_text(),filename=str(path));imports=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):imports.extend(a.name for a in node.names)
            if isinstance(node,ast.ImportFrom):imports.append(node.module)
        allowed={'__future__','collections','pathlib','hashlib','json','re','unittest','argparse','sys','traceback','os','subprocess','ast','reference','run_reference','test_complete_failures_r3'}
        assert all(x in allowed for x in imports),(path,imports)
        static.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes()),'astParsed':True,'imports':imports})
    diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
    assert diff.returncode==0,diff.stderr
    record={'revisionBase':BASE,'exit':0,'oldMembers':before,'oldMemberCount':len(before),'allOldCurrentEqualBaseGit':True,'newUntrackedWriteSurface':new,'protectedAGENTS':{'bytes':len(protected),'sha256':sha(protected),'notStaged':True},'pureSourceStaticChecks':static,'gitDiffCheck':{'exit':diff.returncode,'stdout':diff.stdout,'stderr':diff.stderr},'indexInitiallyEmpty':True,'selfExclusion':'integrity does not hash itself; final manifest includes integrity','noOldArtifactDecodedOrExecuted':True}
    report.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    members=[]
    for prefix in PREFIXES:
        for path in sorted((ROOT/prefix).rglob('*')):
            if path.is_file():
                name=str(path.relative_to(ROOT))
                if name in EXCLUDED:continue
                raw=path.read_bytes();members.append({'path':name,'bytes':len(raw),'sha256':sha(raw)})
    value={'format':'i05-independent-fee-artifact-manifest/3','revisionBase':BASE,'scope':list(PREFIXES),'selfExclusion':list(EXCLUDED),'memberCount':len(members),'members':members,'oldEvidencePolicy':'all original files opaque current=revisionBase Git bytes; first Fail/unknown untouched','AGENTSProtectedUnstaged':record['protectedAGENTS']}
    manifest.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print('old unchanged',len(before),'manifest members',len(members),'manifest',len(manifest.read_bytes()),sha(manifest.read_bytes()))

if __name__=='__main__':main()
