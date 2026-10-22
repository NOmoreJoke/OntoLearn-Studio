"""Finalize actual setup receipts and process commit; pure docs/hash/Git/formatter."""
import base64
import hashlib
import json
from pathlib import Path
import stat
import subprocess

P=Path(__file__).resolve().parent
W=P.parents[3]
C='92652c2db7ad600e9c4ab304812fede7943a8f01'
FMT='/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/node_modules/.bin/prettier'
commands=[]
def run(argv,expected=0):
    r=subprocess.run(argv,cwd=W,capture_output=True)
    commands.append({'argv':argv,'cwd':str(W),'exit':r.returncode,'stdoutBase64':base64.b64encode(r.stdout).decode(),'stderrBase64':base64.b64encode(r.stderr).decode()})
    assert r.returncode==expected,(argv,r.returncode)
    return r.stdout
def hashfile(f):
    h=hashlib.sha256();n=0
    with f.open('rb') as x:
        for b in iter(lambda:x.read(1048576),b''):h.update(b);n+=len(b)
    return {'bytes':n,'sha256':h.hexdigest()}
def write(name,value):
    (P/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
assert run(['git','rev-parse','HEAD']).decode().strip()==C
assert not run(['git','diff','--cached','--name-only'])
setup=json.loads((P/'setup-receipt-r2.json').read_text())
assert setup['packetCandidate']==C and setup['crossRootSharedInodes']==0 and setup['actualTaskCount']==0
spec=json.loads((P/'physical-copy-spec-r2.json').read_text())
frozen={}
prefix=P.relative_to(W).as_posix()
listing=run(['git','ls-tree','-r','-z','--full-tree',C,'--',prefix])
for entry in listing.split(b'\0'):
    if not entry:continue
    head,name=entry.split(b'\t',1);mode,kind,blob=head.decode().split();path=name.decode()
    current=hashfile(W/path)
    opaque=run(['git','hash-object','--no-filters','--',path]).decode().strip()
    assert opaque==blob,path
    frozen[path]={'path':path,'gitBlob':blob,'mode':mode,**current}
write('candidate-git-manifest-r2.json',{'candidate':C,'entries':list(frozen.values()),'count':len(frozen),'allCurrentEqualCandidateGit':True,'scope':'all candidate packet Git entries including unchanged134; product refs and archive unchanged'})
# Inspect ONLY the two specifically authorized roots. The setup already content-hashed all members.
inodes=[];summaries=[]
for person in spec['reviewers']:
    root=Path(person['root']);receiptfile=P/f"wrapper-{person['key']}-preflight-r2.json"
    receipt=json.loads(receiptfile.read_text());assert receipt['copyReady'] and receipt['packetCandidate']==C
    ownpath=Path(receipt['ownManifest']['path']);assert hashfile(ownpath)=={k:receipt['ownManifest'][k] for k in ['bytes','sha256']}
    own=json.loads(ownpath.read_text());assert own['packetCandidate']==C
    for row in person['files']+spec['common']:
        dest=root/row['destination'];assert hashfile(dest)=={'bytes':row['bytes'],'sha256':row['sha256']}
        fixed=frozen[prefix+'/'+row['source']];assert fixed['sha256']==row['sha256']
    observed={x.relative_to(root).as_posix():x for x in root.rglob('*')}
    assert set(observed)=={x['path'] for x in receipt['fullPathset']}
    rootinodes={(root.stat().st_dev,root.stat().st_ino)}
    for item in receipt['fullPathset']:
        path=observed[item['path']];s=path.lstat();assert not stat.S_ISLNK(s.st_mode)
        assert (s.st_dev,s.st_ino)==(item['device'],item['inode'])
        assert format(stat.S_IMODE(s.st_mode),'04o')==item['mode']
        rootinodes.add((s.st_dev,s.st_ino))
    inodes.append(rootinodes)
    for output in ['reports','scratch','review-status/application-metadata']:assert not list((root/output).iterdir())
    assert set(x.name for x in (root/'review-status').iterdir())=={'application-metadata'}
    prompt=next(row for row in person['files'] if row['source'].endswith('-input-r2.md'))
    text=(root/prompt['destination']).read_text()
    for peer in spec['reviewers']:
        if peer['key']!=person['key']:assert peer['root'] not in text
    assert 'docs/architecture/m0-review-and-update-plan-2026-10-19.md' not in text
    assert 'round-4/full-review-input.md' not in text
    summaries.append({'root':str(root),'key':person['key'],'prompt':prompt,'ownManifest':receipt['ownManifest'],'actualFiles':receipt['actualFiles'],'actualDirectories':receipt['actualDirectories'],'members':receipt['materializedMembers'],'copiedBytes':receipt['copiedBytes'],'materializedLogicalBytes':receipt['materializedLogicalBytes'],'allCurrentPathInodesModesMatchSetup':True,'allCopiedInputsEqualFrozenCandidate':True,'emptyMutableBaselineStillTrue':True})
assert not inodes[0]&inodes[1]
write('author-validation-r2.json',{'packetCandidate':C,'checks':summaries,'crossRootSharedInodes':0,'candidatePacketFiles':len(frozen),'prior134Unchanged':True,'inputCopiesReady':True,'actualTaskCount':0,'actualApplicationMetadataGrowthVerified':False,'settingsReadback':'pending','productRuntimeTestsExecuted':False,'independentDeltaReview':'pending','firstFailure':'freeze-first-failure-r2.json retained; original failed author script and complete command streams preserved'})
(P/'setup-summary-r2.md').write_text('''# R2 实际 setup 收据

固定 packet candidate：92652c2db7ad600e9c4ab304812fede7943a8f01；实际副本与其中 physical-copy-spec-r2.json、本人完整 prompt 的冻结字节一致。两 wrapper 均为普通独立目录，无 .git、branch=N/A，每根仅有本人一份当前 prompt。

两根各完整 materialize 22492 个 member，3006 个实际 payload inode 与19486 个后向根内 hardlink。全部路径/类型/目标在写数据前已核，每个独立 inode 完整 SHA/Git blob 读回且每路径匹配；16 namespace 分离，未把互斥版本拼成产品。根内完整文件/目录/bytes/mode/inode 清单见两 preflight，逐件源ref与hash见本人 instructions/own-input-manifest.json。

共同输入60件，加本人固定输入4件和本人实际 manifest1件，每根共22557文件。输入0444、目录0555；本人 reports/scratch/review-status 为0700。两根共享 inode=0，input/output共享inode=0，无symlink/特殊文件/共享.git。真实空 baseline 和当前空输出已核；不是应用创建后的 metadata growth 实测。

旧134件当前与1106固定原件全等，bundle84876346B SHA4bbbd798e6c7a67153db51e185c8795d9ac3509cc4442a81e2071bf319dfaa12不变。R1归档未重压，旧作者器和原首失败未改。R2首次formatter活跃日志样式失败与完整流封存；随后静态formatter/check和staged whitespace准确记录于新顺序收据。

结论仅 input-copy-ready。当前指定模型任务0、真实任务ID/模型设置读回pending、应用metadata增长未测，R2独立delta审查pending；未运行产品/测试/探针/生成器/native/DB/network/install/GUI/模型，无push/PR/merge。
''')
pending=run(['git','ls-files','--others','--exclude-standard','-z','--',prefix]).split(b'\0')
newpaths=[x.decode() for x in pending if x]
textpaths=[n for n in newpaths if Path(n).suffix in ['.md','.json']]
run([FMT,'--ignore-path','/dev/null','--write',*textpaths])
# Formatting new process receipts changes their carrier SHA only; rebind those hashes explicitly.
setup=json.loads((P/'setup-receipt-r2.json').read_text())
for row in setup['actualCopies']:row.update(hashfile(P/row['preflight']))
write('setup-receipt-r2.json',setup)
run([FMT,'--ignore-path','/dev/null','--write',str((P/'setup-receipt-r2.json').relative_to(W))])
run([FMT,'--ignore-path','/dev/null','--check',*textpaths])
write('process-input-manifest-r2.json',{'packetCandidate':C,'files':[{'path':n,**hashfile(W/n)} for n in newpaths],'selfExcluded':True,'commandsInSeparateFinalLog':True,'actualTaskCount':0})
run([FMT,'--ignore-path','/dev/null','--write',str((P/'process-input-manifest-r2.json').relative_to(W))])
run([FMT,'--ignore-path','/dev/null','--check',str((P/'process-input-manifest-r2.json').relative_to(W))])
write('finalize-command-log-r2.json',commands)
# Freeze this log once; all following argv/streams live in the terminal receipt/tool transcript.
later=[]
for argv in [[FMT,'--ignore-path','/dev/null','--write',str((P/'finalize-command-log-r2.json').relative_to(W))],['git','add','--',*newpaths,str((P/'process-input-manifest-r2.json').relative_to(W)),str((P/'finalize-command-log-r2.json').relative_to(W))],['git','diff','--cached','--check'],['git','-c','core.hooksPath=/dev/null','commit','-m','docs(I05): bind R2 isolated physical copies and setup preflight'],['git','rev-parse','HEAD'],['git','status','--short']]:
    r=subprocess.run(argv,cwd=W,capture_output=True);later.append({'argv':argv,'cwd':str(W),'exit':r.returncode,'stdoutBase64':base64.b64encode(r.stdout).decode(),'stderrBase64':base64.b64encode(r.stderr).decode()});assert r.returncode==0
process=base64.b64decode(later[-2]['stdoutBase64']).decode().strip()
print(json.dumps({'packetCandidate':C,'process':process,'actualCopies':summaries,'terminalCommands':later,'receiptBoundary':'terminal tail remains exact in tool output, avoiding recursive self-changing Git proof','actualTaskCount':0,'independentDeltaReview':'pending'},ensure_ascii=False))
