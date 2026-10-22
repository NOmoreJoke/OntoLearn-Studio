"""Safely materialize immutable review inputs only; never execute source or tests."""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tarfile
import traceback
from datetime import datetime, timezone

P=Path(__file__).resolve().parent
W=P.parents[3]
REGISTER=Path('/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/additional-review-roots-20261022.json')
commands=[]
events=[]

def stamp(): return datetime.now(timezone.utc).isoformat()
def writejson(path,value):
    assert not path.exists(),str(path)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def command(argv):
    r=subprocess.run(argv,cwd=W,capture_output=True)
    commands.append({'argv':argv,'cwd':str(W),'exit':r.returncode,'stdoutBase64':base64.b64encode(r.stdout).decode(),'stderrBase64':base64.b64encode(r.stderr).decode()})
    assert r.returncode==0,(argv,r.returncode)
    return r.stdout
def checksum(path):
    h=hashlib.sha256();n=0
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
    return {'bytes':n,'sha256':h.hexdigest()}
def safe(name):
    assert isinstance(name,str) and name and '\\' not in name and '\x00' not in name
    parts=name.split('/')
    assert not name.startswith('/') and all(p not in ['', '.', '..'] for p in parts),name
    assert PurePosixPath(name).as_posix()==name,name
    return parts
def inside(root,name):
    parts=safe(name);dest=root.joinpath(*parts)
    cursor=root
    assert stat.S_ISDIR(cursor.lstat().st_mode) and not cursor.is_symlink()
    for part in parts[:-1]:
        cursor=cursor/part
        if not cursor.exists():cursor.mkdir(mode=0o700)
        assert stat.S_ISDIR(cursor.lstat().st_mode) and not cursor.is_symlink(),str(cursor)
    assert not dest.exists() and not dest.is_symlink(),str(dest)
    return dest
def exclusive_bytes(path,data):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as f:f.write(data)
    path.chmod(0o444)
def ordinary_copy(root,row):
    src=P/row['source'];assert src.is_file() and not src.is_symlink()
    assert checksum(src)=={'bytes':row['bytes'],'sha256':row['sha256']},str(src)
    dest=inside(root,row['destination'])
    fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with src.open('rb') as source,os.fdopen(fd,'wb') as target:
        for b in iter(lambda:source.read(1048576),b''):target.write(b)
    dest.chmod(0o444)
    assert checksum(dest)=={'bytes':row['bytes'],'sha256':row['sha256']}
    assert (src.stat().st_dev,src.stat().st_ino)!=(dest.stat().st_dev,dest.stat().st_ino)
    return {'path':row['destination'],'sourcePacketPath':row['source'],**checksum(dest),'device':dest.stat().st_dev,'inode':dest.stat().st_ino,'mode':'0444','ordinaryCopyIndependentFromSource':True}
def membercheck(member,row,previous):
    safe(member.name);assert member.name==row['member']
    assert not member.issym() and not member.isdir() and not member.isdev() and not member.isfifo()
    target=row.get('hardlinkTarget')
    if target:
        safe(target);assert member.islnk() and member.linkname==target and target in previous
        other=previous[target]
        assert (other['bytes'],other['sha256'],other['gitBlob'])==(row['bytes'],row['sha256'],row['gitBlob'])
        assert member.size==0
    else:assert member.isfile() and not member.islnk() and member.size==row['bytes']
def readonly_tree(root):
    for parent,dirs,files in os.walk(root,topdown=False,followlinks=False):
        for f in files:
            x=Path(parent)/f;assert stat.S_ISREG(x.lstat().st_mode) and not x.is_symlink();x.chmod(0o444)
        for d in dirs:
            x=Path(parent)/d;assert stat.S_ISDIR(x.lstat().st_mode) and not x.is_symlink();x.chmod(0o555)
    root.chmod(0o555)
def inventory(root):
    rows=[]
    for parent,dirs,files in os.walk(root,topdown=True,followlinks=False):
        for name in sorted(dirs+files):
            p=Path(parent)/name;s=p.lstat();assert not stat.S_ISLNK(s.st_mode),str(p)
            assert stat.S_ISDIR(s.st_mode) or stat.S_ISREG(s.st_mode),str(p)
            rows.append({'path':p.relative_to(root).as_posix(),'kind':'directory' if stat.S_ISDIR(s.st_mode) else 'file','bytes':s.st_size if stat.S_ISREG(s.st_mode) else None,'mode':format(stat.S_IMODE(s.st_mode),'04o'),'device':s.st_dev,'inode':s.st_ino,'links':s.st_nlink})
    return sorted(rows,key=lambda x:x['path'])

try:
    candidate=command(['git','rev-parse','HEAD']).decode().strip()
    assert candidate=='92652c2db7ad600e9c4ab304812fede7943a8f01'
    assert not command(['git','diff','--cached','--name-only'])
    spec=json.loads((P/'physical-copy-spec-r2.json').read_text())
    manifest=json.loads((P/'input-manifest.json').read_text());members=manifest['members']
    assert len(members)==22492
    assert checksum(P/'frozen-inputs.tar.gz')=={'bytes':84876346,'sha256':'4bbbd798e6c7a67153db51e185c8795d9ac3509cc4442a81e2071bf319dfaa12'}
    # Validate ALL archive paths/types/backward links before creating any data file.
    previous={};regular=0;links=0
    with tarfile.open(P/'frozen-inputs.tar.gz','r|gz') as archive:
        for i,m in enumerate(archive):
            assert i<len(members);row=members[i];membercheck(m,row,previous)
            assert m.name not in previous;previous[m.name]=row
            if row.get('hardlinkTarget'):links+=1
            else:regular+=1
    assert len(previous)==len(members)
    registered=json.loads(REGISTER.read_text())
    selected=[]
    for reviewer in spec['reviewers']:
        root=Path(reviewer['root'])
        registration=[r for r in registered['roots'] if r['path']==str(root)]
        assert len(registration)==1 and registration[0]['created'] and registration[0]['kind']=='empty isolated wrapper'
        assert root.is_dir() and not root.is_symlink() and not list(root.iterdir())
        selected.append({'path':str(root),'registration':registration[0],'actualInitialPathset':[],'observedAt':stamp(),'device':root.stat().st_dev,'inode':root.stat().st_ino})
    writejson(P/'wrapper-empty-baselines-r2.json',{'candidate':candidate,'registerPath':str(REGISTER),'register':checksum(REGISTER),'selectedI05RootsOnly':selected,'actualTaskCount':0,'applicationMetadataGrowthVerified':False})
    receipts=[];all_inode_sets=[]
    for reviewer in spec['reviewers']:
        root=Path(reviewer['root']);key=reviewer['key'];started=stamp()
        copied=[ordinary_copy(root,row) for row in spec['common']+reviewer['files']]
        data=root/'data';data.mkdir(mode=0o700)
        done={};fingerprints={}
        with tarfile.open(root/'immutable/frozen-inputs.tar.gz','r|gz') as archive:
            for i,m in enumerate(archive):
                row=members[i];membercheck(m,row,done)
                target=inside(data,m.name)
                if row.get('hardlinkTarget'):
                    local=data/row['hardlinkTarget'];assert local.is_file() and not local.is_symlink()
                    os.link(local,target,follow_symlinks=False)
                    fingerprint=fingerprints[row['hardlinkTarget']]
                else:
                    source=archive.extractfile(m);assert source is not None
                    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
                    h=hashlib.sha256();g=hashlib.sha1();g.update(('blob '+str(row['bytes'])+'\0').encode());n=0
                    with source,os.fdopen(fd,'wb') as f:
                        for b in iter(lambda:source.read(1048576),b''):f.write(b);h.update(b);g.update(b);n+=len(b)
                    fingerprint={'bytes':n,'sha256':h.hexdigest(),'gitBlob':g.hexdigest()}
                assert fingerprint=={k:row[k] for k in ['bytes','sha256','gitBlob']},m.name
                target.chmod(0o444);done[m.name]=row;fingerprints[m.name]=fingerprint
        assert len(done)==len(members)
        # Independently read back every distinct local inode; each path's expectations are checked.
        inode_cache={};materialized=[]
        for row in members:
            f=data/row['member'];s=f.lstat();assert stat.S_ISREG(s.st_mode) and stat.S_IMODE(s.st_mode)==0o444
            inode=(s.st_dev,s.st_ino)
            if inode not in inode_cache:
                info=checksum(f);b=f.read_bytes();info['gitBlob']=hashlib.sha1(('blob '+str(len(b))+'\0').encode()+b).hexdigest();inode_cache[inode]=info
            assert inode_cache[inode]=={k:row[k] for k in ['bytes','sha256','gitBlob']},str(f)
            materialized.append({'path':'data/'+row['member'],'sourceRef':row['sourceRef'],'sourcePath':row['sourcePath'],'gitBlob':row['gitBlob'],'bytes':s.st_size,'sha256':row['sha256'],'device':s.st_dev,'inode':s.st_ino,'mode':'0444','internalHardlinkTarget':('data/'+row['hardlinkTarget']) if row.get('hardlinkTarget') else None})
        for name in spec['mutableDirectories']:(root/name).mkdir(mode=0o700,parents=True,exist_ok=True)
        baseline={name:sorted(x.relative_to(root).as_posix() for x in (root/name).rglob('*')) for name in spec['mutableDirectories']}
        assert baseline=={'reports':[],'scratch':[],'review-status':['review-status/application-metadata'],'review-status/application-metadata':[]}
        own={'format':'i05-own-input-copy-manifest/2','root':str(root),'branch':None,'packetCandidate':candidate,'sourceBase':spec['sourceBase'],'sourceCandidate':spec['sourceCandidate'],'sourceProcess':spec['sourceProcess'],'bundle':manifest['bundle'],'copiedFiles':copied,'materialized':materialized,'regularPayloads':regular,'internalBackwardHardlinks':links,'actualTaskCount':0,'nativeTaskId':None,'settingsReadback':'pending','applicationMetadataGrowthVerified':False,'outputBaseline':baseline,'allowedMutable':['reports','scratch','review-status'],'noPeerOrGlobalDiscovery':True,'safeMaterialization':'all paths/types/link targets validated before any data write; readback every distinct inode, check every path expected SHA/Git blob; no source executed'}
        ownfile=inside(root,'instructions/own-input-manifest.json');exclusive_bytes(ownfile,(json.dumps(own,ensure_ascii=False,indent=2)+'\n').encode())
        for directory in ['instructions','immutable','data']:readonly_tree(root/directory)
        paths=inventory(root)
        expected_files={x['destination'] for x in spec['common']+reviewer['files']}|{'data/'+r['member'] for r in members}|{'instructions/own-input-manifest.json'}
        assert {x['path'] for x in paths if x['kind']=='file'}==expected_files
        expected_dirs=set(spec['mutableDirectories'])
        for file in expected_files:
            parent=PurePosixPath(file).parent
            while str(parent)!='.':expected_dirs.add(str(parent));parent=parent.parent
        assert {x['path'] for x in paths if x['kind']=='directory'}==expected_dirs
        for x in paths:
            mutable=any(x['path']==n or x['path'].startswith(n+'/') for n in ['reports','scratch','review-status'])
            assert x['mode']==('0700' if mutable else ('0555' if x['kind']=='directory' else '0444')),(key,x)
        input_inodes={(x['device'],x['inode']) for x in paths if not any(x['path']==n or x['path'].startswith(n+'/') for n in ['reports','scratch','review-status'])}
        mutable_inodes={(x['device'],x['inode']) for x in paths if any(x['path']==n or x['path'].startswith(n+'/') for n in ['reports','scratch','review-status'])}
        assert not input_inodes & mutable_inodes
        all_inode_sets.append(input_inodes|mutable_inodes|{(root.stat().st_dev,root.stat().st_ino)})
        receipt={'key':key,'root':str(root),'packetCandidate':candidate,'startedAt':started,'completedAt':stamp(),'copyReady':True,'commonFiles':len(spec['common']),'ownFrozenFiles':len(reviewer['files']),'materializedMembers':len(materialized),'materializedLogicalBytes':sum(x['bytes'] for x in materialized),'payloadInodes':len(inode_cache),'regularPayloads':regular,'internalHardlinks':links,'ownManifest':{'path':str(ownfile),**checksum(ownfile)},'ownPrompt':next(x for x in copied if x['path'].endswith('-input-r2.md')),'fullPathset':paths,'actualFiles':len(expected_files),'actualDirectories':len(expected_dirs),'copiedBytes':sum(x['bytes'] for x in copied),'allInputModesReadonly':True,'allOutputModes0700':True,'noSymlinksOrSpecialFiles':True,'noGitDirectory':not(root/'.git').exists(),'inputOutputInodesDisjoint':True,'actualTaskCount':0,'nativeTaskId':None,'settingsReadback':'pending','actualApplicationGrowthVerified':False,'outputBaseline':baseline}
        out=P/f'wrapper-{key}-preflight-r2.json';writejson(out,receipt);receipts.append({'key':key,'root':str(root),'preflight':out.name,**checksum(out),'ownPrompt':receipt['ownPrompt'],'copyReady':True,'members':len(materialized),'actualFiles':len(expected_files),'actualDirectories':len(expected_dirs),'copiedBytes':receipt['copiedBytes']})
        print(json.dumps({'key':key,'copyReady':True,'members':len(materialized),'files':len(expected_files),'ownManifestSHA':checksum(ownfile)['sha256']},ensure_ascii=False),flush=True)
    assert len(all_inode_sets)==2 and not all_inode_sets[0]&all_inode_sets[1]
    prior=json.loads((P/'prior-originals-preservation-r2.json').read_text())
    for row in prior['files']:assert checksum(W/row['path'])=={'bytes':row['bytes'],'sha256':row['sha256']}
    writejson(P/'setup-receipt-r2.json',{'format':'i05-isolated-review-setup/2','packetCandidate':candidate,'copySpec':{'path':'physical-copy-spec-r2.json',**checksum(P/'physical-copy-spec-r2.json')},'registerPath':str(REGISTER),'registerHash':checksum(REGISTER),'actualCopies':receipts,'archivePrevalidation':{'members':len(members),'regular':regular,'backwardHardlinks':links,'allSafeBeforeWriting':True},'crossRootSharedInodes':0,'inputOutputSharedInodes':0,'prior134Unchanged':True,'archiveUnchanged':checksum(P/'frozen-inputs.tar.gz'),'actualTaskCount':0,'actualTasks':[],'actualApplicationGrowthVerified':False,'settingsReadback':'pending','independentDeltaReview':'pending root-appointed independent review','commands':commands,'sourceProductsExecuted':False,'scope':'two specifically authorized wrapper roots and new packet docs only; no global or peer-task discovery'})
except BaseException:
    failure={'observedAt':stamp(),'commands':commands,'events':events,'traceback':traceback.format_exc(),'sourceProductsExecuted':False,'action':'STOP; preserve actual partial outputs and failure; no cleanup or false copyReady claim'}
    f=P/'setup-first-failure-r2.json'
    if not f.exists():writejson(f,failure)
    raise
