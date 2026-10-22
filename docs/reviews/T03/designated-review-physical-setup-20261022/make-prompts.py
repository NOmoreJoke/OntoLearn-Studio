# coding: utf-8
"""Append exact frozen full prompts after a physical/execution supplement."""
import hashlib
import json
from pathlib import Path

ROOT = Path('/Users/kyle/Documents/工作/知爻/本体')
OWNER = ROOT / '.worktrees/T03-mapping'
OUT = OWNER / 'docs/reviews/T03/designated-review-physical-setup-20261022'
OLD = OWNER / 'docs/reviews/T03/designated-review-backlog-20261022/dispatch-v2'
CONTROL = ROOT / 'iteration-control/2026-10-21-weekly-release'
rows = json.loads((CONTROL / 'T03-T04-review-roots-20261022.json').read_text())['roots'][:6]
policies = ['developer-common-instructions.md', 'desktop-operation-policy-20261022.md', 'external-review-permissions.md']
index = []
for row in rows:
    group = row['module'].removeprefix('T03-')
    filename = group + '-' + row['role'] + '-prompt.md'
    old = (OLD / filename).read_bytes()
    physical = Path(row['tree'])
    session = physical / 'build/review-session'
    report = session / 'reports' / (group + '-' + row['role'] + '-full-report.md')
    task = session / 'metadata/task-actual.json'
    mapping = {k:str(session / k) for k in ['env-cache','tmp','scratch','raw','reports','metadata']}
    mapping.update({'workingTree':str(physical),'nodeModules':str(physical/'node_modules'),'pythonVenv':str(physical/'.venv'),
                    'environmentShell':str(session/'environment.sh'),'fullReport':str(report),'actualTaskMetadata':str(task),
                    'ordinaryBuildOutput':str(physical/'apps/desktop/out'),'engineBuildOutput':str(physical/'build/engine'),
                    'packageOutput':str(physical/'release'),'playwrightOutput':str(physical/'test-results'),
                    'c1Evidence':str(session/'raw/c1-evidence.json')})
    header = f'''# 本轮物理树与执行补充（优先于下附冻结历史提示中的路径、安装及一律不运行段）

任务仍为本组全部固定工程与全部原依据的独立完整审查。只允许选择本物理树：`{physical}`。它是detached HEAD，必须保持HEAD `{row['reviewHead']}`；产品候选 `{row['product']}`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。旧提示中的原owner工作树/分支仅为历史来源，不是当前执行目录，不切去原树，不切分支，不拼装其他分支。原固定完整工程/历史输入清单及manifest继续用原只读共享地址与ref逐件核身份；过程追加的纯文档不改变产品。当前AGENTS15147B/SHAde15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4已在本树传播，保持未暂存，不修产品/测试/锁/配置/验收。

## 唯一本任务路径

```json
{json.dumps(mapping,ensure_ascii=False,indent=2)}
```

开始运行前source本树environment.sh（不是执行bootstrap.py）；它设置本树独立npm/uv/Electron/builder/XDG缓存与TMP，UV_LINK_MODE=copy，清除ROOT_SOURCE_PATH、旧engine/package/fixture/HMR目标。I02_EVIDENCE明确覆盖任何继承值并固定为上述c1Evidence路径；每次真实重跑前owner另建本树新raw轮次路径保首失败，不覆盖旧证据。仅本树实体node_modules/.venv可用，不能借其他树、把.venv指向外部、用共享mutable inode或复制同伴运行库；系统Node/npm/uv/Python只读基础工具可以共用，`.venv/bin/python`基础解释器符号链接须如实披露。Hatchling正常editable安装只指本树源码，是setup，不是产品运行通过。

setup由原T03唯一owner完成，模型不得重装依赖、更新锁、运行本包bootstrap或make-prompts脚本；若依赖缺失，报告精确setup缺口给owner。setup收据记录`npm ci --ignore-scripts`、`uv sync --frozen --python /Users/kyle/.local/bin/python3.12 --no-managed-python --link-mode copy`及独立Electron install.js安装结果；跳过的可选lifecycle不等于跨平台工具均ready。不能用安装exit0冒充check/e2e/package通过。当前这份预备包制作阶段不运行产品；后续真实审查任务可按下列正常回归权限执行，不继承旧“一律不新运行”限制。

## 正常回归权限及资源

静态完整审读后，若必要验证对应受审内容，可在本树记录精确argv/原因/时间/exit/stdout/stderr后运行原未改入口：`npm run check`、`npm run verify:sources`、`npm run test:e2e`、`npm run package:dir`。无需因旧提示重复向用户申请权限。没有变化不强制重测；不因普通C1/I04测试含native路径就泛禁它们。check含真实Vitest/Python进程、coordinator/worker/SQLite和build，不是纯静态；sources读取原source-manifest所列资料；e2e显式安装Electron后启动真实可见应用；package构建unsigned mac目录，尚不等于包内样例验收。各命令具体调用、输出与平台条件见只读完整静态审计`{OUT / 'static-command-audit.md'}`，此审计是Codex setup依据，不是另一指定模型本轮意见。

GUI/C1真实恢复、焦点、现有固定5173端口和默认应用数据目录须由总控内部排互斥运行lease；当前包不证明任何lease，当前T01独占GUI以总控交接为准。仅worktree/TMP隔离不能证明初始Electron userData隔离，启动前明确实际应用数据使用范围与自有PID，不改冻结源码来绕过，不清理用户/其他任务进程。资源未交接时继续完整静态审读，准确记录待运行项，不向用户索要桌面时段。

C1 `csp-lifecycle.spec.ts`默认包含无平台/I02_NATIVE启用开关的runNativeRecovery，Mac也执行；保留其真实crash/hang与既有hook局限，不宣传为全部原生提示人工验收。I04 reload需本轮独立fixture；coordinator additionally Linux；I04 real-native需Linux且I04_NATIVE_ISOLATED=1及其原display/window前提。正常独立fixture准备`uv run --frozen python scripts/prepare-i04-fixture.py <本树scratch下新的唯一目录>`属于产品运行，只有正常运行阶段且对应资源条件满足才执行，输出fixture绝对路径赋I04_TEST_FIXTURE；不得拿Mac skip冒称Linux门通过。I02_HMR=1会改源，冻结期禁止；不改测试以跳过native或换stub/禁hang-monitor冒充验收。

普通package内回归使用本次本树包内engine：`uv run --frozen python scripts/verify-i04-package.py <本树release/mac-arm64/OntoLearn Studio.app/Contents/Resources/engine/ontolearn-engine> <本树scratch下新建输出目录>`，不得借旧包。mapping已有--mapping-probe、profile已有固定semantic-profile CLI及其外部oracle属于各自原验收，若确需重跑先列其冻结合同原argv和当阶段精确运行界限交owner核对；本补充不凭“正常回归”扩成任意参数、任意文件、SDK/原生身份读取或新资源研究。profile历史probe/oracle真实exit1、83=78成功/4资源拒绝/1缺规则未执行保持原样，不把计数相同当全通过。

## 严格保留的界限与完整交付

不运行未签T03-N0 native/producer/caller及其局部函数、runner/reader、ABI/loader/drain、witness/descriptor/index身份payload或被拒资源研究；不借票、不抬guard、不导入它们做fixture/dry-run。普通已有C1/I04回归与这些专票研究分清。只读完整工程源码/全部原设计、失败、验收/历史原件仍在范围内；历史资料按原固定ref读，SDK/受限身份载荷继续按原明确权限，不自行解码。Caller停止现场不读不写；必要身份以原已固定manifest说明未验边界。

只向上述本任务raw/scratch/reports/metadata及原命令自有忽略输出写入。完整意见报告写唯一fullReport，真实task/session/turn/实际模型思考权限与来源写actualTaskMetadata；尚未实际创建则留空，不能用目标模型名称伪填实际值。{('ZCode要求GLM-5.3/最高思考/yolo' if row['role']=='zcode' else 'MiniMax Code要求M3.1-Flash/xhigh/bypassPermissions')}，创建/读回由原owner按总控短lease执行，不自建第二任务。不创建Goal/新聊天，不提交/推送/PR，不stageAGENTS。

禁止发现、搜索、读取另一指定模型本轮任务、意见、进度、状态库、报告、raw或metadata；也不通过共享Git新日志、app runtime/configDB窥探同伴。可读原固定完整历史原件及本补充明确列出的setup收据。只审自己本轮独立任务，不削减原范围。所有首次失败完整保留；全部原门逐项判定，静态/运行/包/父业务/两OS/生产分别报告。终态完整全文读回及全部意见处置由owner后续封存，setup独审不算指定模型Pass。

下附当前三份共同规则全文和冻结dispatch-v2提示原字节。发生冲突时本补充仅覆盖本物理目录、独立写面、setup、正常回归执行与资源调度；原工程范围/历史/严格安全/模型/完整报告/发布门不缩减。共同指南中“建立Goal”等新开发入口不适用于本既有审查任务，不新建Goal。
'''
    supplement = header.encode()
    policy_ids = []
    for name in policies:
        raw = (CONTROL/name).read_bytes()
        policy_ids.append({'path':str(CONTROL/name),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        supplement += ('\n\n---\n\n# 当前共同原件：'+name+'\n\n').encode() + raw
    supplement += b'\n\n---\n\n# Frozen dispatch-v2 full original (exact bytes below)\n\n'
    new = supplement + old
    (OUT / filename).write_bytes(new)
    assert new[-len(old):] == old
    index.append(dict(row,prompt=filename,promptBytes=len(new),promptSha256=hashlib.sha256(new).hexdigest(),
                      frozenOriginalPath=str(OLD/filename),frozenOriginalBytes=len(old),frozenOriginalSha256=hashlib.sha256(old).hexdigest(),
                      frozenSuffixOffset=len(supplement),pathMap=mapping,policies=policy_ids,actualTask=None,actualSettings=None,lease=None))
(OUT/'prompt-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'fullPrompts':len(index),'allFrozenSuffixesExact':True},ensure_ascii=False))
