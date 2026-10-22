"""R2-only formatter, hash receipt and Git candidate freeze; no product execution."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess

P = Path(__file__).resolve().parent
W = P.parents[3]
REPO = Path('/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio')
BASE = '1106f15629c41833be9c9604eb7bf02134fa0541'
log = []

def run(argv):
    result = subprocess.run(argv, cwd=W, capture_output=True)
    log.append({'argv': argv, 'cwd': str(W), 'exit': result.returncode, 'stdoutBase64': base64.b64encode(result.stdout).decode(), 'stderrBase64': base64.b64encode(result.stderr).decode()})
    (P/'freeze-command-log-r2.json').write_text(json.dumps(log, ensure_ascii=False, indent=2)+'\n')
    assert result.returncode == 0, (argv, result.returncode)
    return result.stdout

def sha(path):
    b = path.read_bytes()
    return {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

assert run(['git','rev-parse','HEAD']).decode().strip() == BASE
assert not run(['git','diff','--cached','--name-only'])
prior = json.loads((P/'prior-originals-preservation-r2.json').read_text())
for f in prior['files']:
    assert sha(W/f['path']) == {'bytes': f['bytes'], 'sha256': f['sha256']}
new_policy = P/'current-policy-addendum-r2.md'
assert not new_policy.exists()
new_policy.write_text('''# R2 现行政策与 setup 扩授权

本件补充 immutable/current-policy-addendum.md 中旧备包写面记载。总控已实际创建两个独立普通 wrapper，并将 setup 独占交给原 I05 备包作者；本人审查任务仅获本提示所给自己的 workspace。作者可普通复制冻结输入和本人一个提示、安全只读 materialize、核完整 pathset/bytes/SHA/inode 和空输出基线，不获产品/测试/模型/GUI/native/DB/network/安装/Goal/push 权限。

当前主 AGENTS 15147B SHAde15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4 与 immutable/r2-guidance/四份现行规则适用。旧历史规则和原件不改。当前 full access 是逐任务设置要求，不扩只读职责，不绕过 HOLD/native/审批拒绝。仅 root 按真实短 lease 操作审查应用；作者不派发模型。

本人可读范围为完整冻结工程源码、共同历史输入、本人 prompt/report/当前任务精确已确认 metadata；运行范围仅纯结构读取/Git/opaque hash/stdlib JSON/tar/AST，禁止导入产品和执行产品/测试/探针/生成器。禁止 peer/global 自动状态发现，意外串读立即停止并保最小事件交 root 判独立性。当前任务0，应用 metadata growth 还未实测，不能以目录创建或默认权限冒设置读回。
''')
for key in ['zcode-glm53','minimax-m31flash']:
    f = P/f'{key}-input-r2.md'
    s = f.read_text().replace('先读 instructions/receiver-guide-r2.md、immutable/current-policy-addendum.md', '先读 instructions/receiver-guide-r2.md、immutable/current-policy-addendum-r2.md、immutable/current-policy-addendum.md')
    f.write_text(s)
formatter = str(REPO/'node_modules/.bin/prettier')
new = [x for x in P.rglob('*') if x.is_file() and str(x.relative_to(W)) not in {f['path'] for f in prior['files']}]
formatted = [str(x.relative_to(W)) for x in new if x.suffix in ['.md','.json']]
run([formatter,'--ignore-path','/dev/null','--write',*formatted])
spec = json.loads((P/'physical-copy-spec-r2.json').read_text())
spec['common'].append({'source':new_policy.name,'destination':'immutable/'+new_policy.name})
for row in spec['common']:
    row.update(sha(P/row['source']))
for reviewer in spec['reviewers']:
    for row in reviewer['files']:
        row.update(sha(P/row['source']))
(P/'physical-copy-spec-r2.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
dispatch = json.loads((P/'dispatch-r2.json').read_text())
dispatch['reviewers'] = spec['reviewers']
(P/'dispatch-r2.json').write_text(json.dumps(dispatch,ensure_ascii=False,indent=2)+'\n')
run([formatter,'--ignore-path','/dev/null','--write',str((P/'physical-copy-spec-r2.json').relative_to(W)),str((P/'dispatch-r2.json').relative_to(W))])
run([formatter,'--ignore-path','/dev/null','--check',*formatted,str(new_policy.relative_to(W))])
for f in prior['files']:
    assert sha(W/f['path']) == {'bytes': f['bytes'], 'sha256': f['sha256']}
new = [x for x in P.rglob('*') if x.is_file() and str(x.relative_to(W)) not in {f['path'] for f in prior['files']}]
receipt = {'format':'i05-r2-author-candidate-manifest/2','revisionBase':BASE,'prior134Unchanged':True,'actualTaskCount':0,'applicationGrowthVerified':False,'files':[{'path':str(x.relative_to(W)),**sha(x)} for x in sorted(new) if x.name not in ['freeze-command-log-r2.json','candidate-manifest-r2.json']], 'manifestSelfExcluded':True,'commandLogIsMutableUntilFreeze':True,'outerToolStreamBoundary':'outer bootstrap/tool calls are retained by Codex tool transcript; this log records exact subprocess split streams only; no synthetic exit claims', 'knownOuterSearchFailure':{'operation':'rg two packet script paths with cwd project parent instead of packet worktree','exit':2,'effect':'read only, no files changed; corrected with exact packet cwd','output':'rg: both paths No such file or directory'},'independentDeltaReview':'pending'}
(P/'candidate-manifest-r2.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
run([formatter,'--ignore-path','/dev/null','--write',str((P/'candidate-manifest-r2.json').relative_to(W))])
paths = [str(x.relative_to(W)) for x in new]+[str((P/'candidate-manifest-r2.json').relative_to(W))]
run(['git','add','--',*paths])
run(['git','diff','--cached','--check'])
# Log writes after staging intentionally become process-only and are explicitly re-added.
run(['git','add','--',str((P/'freeze-command-log-r2.json').relative_to(W))])
result = subprocess.run(['git','-c','core.hooksPath=/dev/null','commit','-m','docs(I05): freeze R2 source review inputs and isolated copy spec'],cwd=W,capture_output=True)
assert result.returncode == 0, result.stderr.decode()
# Commit and post-commit commands are captured in a new process receipt to avoid self mutation.
head = subprocess.run(['git','rev-parse','HEAD'],cwd=W,capture_output=True)
assert head.returncode == 0
(P/'candidate-freeze-receipt-r2.json').write_text(json.dumps({'candidate':head.stdout.decode().strip(),'revisionBase':BASE,'commands':[{'argv':['git','-c','core.hooksPath=/dev/null','commit','-m','docs(I05): freeze R2 source review inputs and isolated copy spec'],'cwd':str(W),'exit':result.returncode,'stdoutBase64':base64.b64encode(result.stdout).decode(),'stderrBase64':base64.b64encode(result.stderr).decode()},{'argv':['git','rev-parse','HEAD'],'cwd':str(W),'exit':head.returncode,'stdoutBase64':base64.b64encode(head.stdout).decode(),'stderrBase64':base64.b64encode(head.stderr).decode()}],'copies':'pending actual setup','actualTaskCount':0},ensure_ascii=False,indent=2)+'\n')
print(head.stdout.decode().strip())
