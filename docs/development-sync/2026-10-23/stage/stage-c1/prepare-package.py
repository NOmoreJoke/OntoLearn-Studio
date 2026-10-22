from pathlib import Path
import hashlib,json,shutil,subprocess,datetime
from zoneinfo import ZoneInfo
ROOT=Path('/Users/kyle/Documents/工作/知爻/本体');OUT=Path(__file__).resolve().parent;SRC=ROOT/'outputs/20261022_stage_acceptance';PAY=OUT/'payload';PAY.mkdir(exist_ok=True)
def h(b):return hashlib.sha256(b).hexdigest()
def copy(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for name in ['README.md','stage-delivery.json','打开阶段验收.command']:copy(SRC/name,PAY/'artifacts'/name)
for src in sorted((SRC/'browser').rglob('*')):
 if src.is_file():copy(src,PAY/'artifacts/browser'/src.relative_to(SRC/'browser'))
for src in sorted((SRC/'desktop').iterdir()):
 if src.is_file() and not src.name.endswith('.zip'):copy(src,PAY/'artifacts/desktop'/src.name)
for src in sorted((SRC/'desktop/build-stage').rglob('*')):
 if src.is_file() and src.suffix in ['.yaml','.yml','.json']:copy(src,PAY/'artifacts/desktop/build-stage'/src.relative_to(SRC/'desktop/build-stage'))
for name in ['stage-independent-review.md','stage-review-proof.json']:
 copy(SRC/'review-coordination'/name,PAY/'independent-review'/name)
rawroot=ROOT/'.playwright-cli'
for name in ['OntoLearn-stage-feedback.json','OntoLearn-synthetic-samples.json','page-2026-10-22T07-51-49-383Z.yml','page-2026-10-22T07-53-45-217Z.yml','page-2026-10-22T07-54-37-071Z.yml','page-2026-10-22T07-54-40-921Z.yml','page-2026-10-22T07-55-02-351Z.yml','page-2026-10-22T07-56-11-755Z.png','page-2026-10-22T07-58-10-900Z.yml']:
 p=rawroot/name
 if p.exists():copy(p,PAY/'independent-review/raw'/name)
copy(ROOT/'OntoLearn-Studio/AGENTS.md',PAY/'guidance/AGENTS.current-de15.md')
assert h((PAY/'guidance/AGENTS.current-de15.md').read_bytes())=='de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4'
for name in ['external-review-permissions.md','desktop-operation-policy-20261022.md']:
 copy(ROOT/'iteration-control/2026-10-21-weekly-release'/name,PAY/'guidance'/name)
repo=ROOT/'OntoLearn-Studio';base='5f910b52c69d86a1076b2032e5d3c63e715947f3'
paths=['apps/desktop/src','apps/desktop/package.json','apps/desktop/electron-builder.yml','apps/desktop/electron.vite.config.ts','apps/desktop/tsconfig.json','packages/contracts','packages/engine/src','scripts/build-engine.mjs','package.json','package-lock.json','pyproject.toml','uv.lock']
files=subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','--name-only',base,'--',*paths],text=True).splitlines();frozen=[]
for name in files:
 b=subprocess.check_output(['git','-C',str(repo),'show',base+':'+name]);p=PAY/'baseline-source'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);frozen.append({'path':name,'bytes':len(b),'sha256':h(b),'gitBlob':subprocess.check_output(['git','-C',str(repo),'rev-parse',base+':'+name],text=True).strip()})
(PAY/'baseline-identity.json').write_text(json.dumps({'commit':base,'purpose':'Prior integrated source reference for stage package combination; does not transfer approval to new metadata/shell.','files':frozen},ensure_ascii=False,indent=2)+'\n')
(PAY/'baseline-git-tree.txt').write_bytes(subprocess.check_output(['git','-C',str(repo),'ls-tree','-r',base]))
manifest=json.loads((SRC/'desktop/manifest.json').read_text());zipfile=SRC/'desktop'/manifest['package']['zip'];zh=h(zipfile.read_bytes());assert zh==manifest['artifacts'][0]['sha256']
app=SRC/'desktop'/manifest['package']['app']
external={'originalStageRoot':str(SRC),'browserOriginalPath':str(SRC/'browser/index.html'),'browserIndexSHA256':h((SRC/'browser/index.html').read_bytes()),'native':{'baseline':base,'appPath':str(app),'fileManifestPath':str(SRC/'desktop/app-files.json'),'fileManifestSHA256':h((SRC/'desktop/app-files.json').read_bytes()),'appContentsNotCopied':True,'zipPath':str(zipfile),'zipBytes':zipfile.stat().st_size,'zipSHA256':zh,'appFileEntries':manifest['package']['fileEntries'],'appSymlinkEntries':manifest['package']['symlinkEntries'],'originalAppAndZipReadOnly':True},'independentRawCoverage':'All currently extant task-specific author headless files plus independent root snapshots/downloads copied as existing bytes; missing original raw tool transcripts are not reconstructed.'}
(PAY/'external-artifacts.json').write_text(json.dumps(external,ensure_ascii=False,indent=2)+'\n')
print('exported baseline',len(files),'browser sources',len(json.loads((SRC/'browser/manifest.json').read_text())['sources']))
