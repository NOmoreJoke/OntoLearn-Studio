"""Prepare R2 documentation only. No product imports or execution."""
from pathlib import Path
import hashlib
import json

P = Path(__file__).resolve().parent
BASE = "1106f15629c41833be9c9604eb7bf02134fa0541"
HOME = Path("/Users/kyle/Documents/工作/知爻/本体/.worktrees")

def write(name, data):
    target = P / name
    assert not target.exists(), str(target)
    target.write_text(data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2) + "\n")

def digest(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

reviewers = [
    {"key": "zcode-glm53", "root": str(HOME / "I05-retained-review-zcode"), "model": "GLM-5.3", "thinking": "highest/最高", "permission": "permission.mode=yolo"},
    {"key": "minimax-m31flash", "root": str(HOME / "I05-retained-review-minimax"), "model": "M3.1-Flash", "thinking": "xhigh", "permission": "permissionMode=bypassPermissions"},
]
mapping = (P / "original-material-map-r2.md").read_text()
old = (P / "zcode-glm53-input.md").read_text()
isolation = """
## 本轮物理隔离和自动状态读面

仅访问本提示给定的本人 workspace。不可读取或发现任何兄弟目录、其他本轮任务的 prompt、过程、报告、任务状态、应用自动状态；不得用搜索、Git worktree inventory、工具全局任务发现、全局应用状态目录或跨目录扫描间接取得。若需核产品 Git，仅允许明确固定 ref/path/blob 的读取，不扫描其他 checkout。独立历史 C1 两份报告及终态属于共同冻结必读输入，不受本轮 peer 禁读误遮。

只读 immutable/、data/、instructions/ 及根 AGENTS.md。只写本人的 reports/、scratch/、review-status/，其中 review-status/application-metadata/ 当前为空；应用未来生成元数据时，只能在 root 实际确认属于当前任务且批准的本人路径内读写。应用若要求全局状态目录，不自行扫描或扩大范围，交 root 获取当前任务的精确读回。当前空 baseline 不代表应用 metadata growth 已实测。禁止 symlink escape、跨根 hardlink、共享可变 .git、scratch 或报告。data 内部只读 hardlink 指向本人数据，禁止编辑或 chmod。

若意外看到其他本轮任务内容或范围外 metadata，立即停止本轮审查，不继续搜索或读取，不删除已有真实事件；仅保存已经实际观察到的最小事件及时间、来源、路径类别，在本人报告告知 root，由 root 判定独立性及是否重开任务。不得借意外发现继续读 peer 或自行宣称无污染。

实际创建来源、任务原生 ID、本人模型/thinking/逐任务权限、实际 workspace 路径、根内输入 SHA、本人 prompt SHA 均由 root 真实读回后记录。wrapper 是独立普通目录，无 .git，branch=N/A；不要创建 .git 或把备包分支误认成本人的实际 branch。未有任务时 ID=null、settingsReadback=pending，禁止把本提示要求当已经达到的设置。
"""
for r in reviewers:
    root = r["root"]
    identity = f"""## 精确任务身份

本人唯一 workspace：{root}
这是独立普通物理 wrapper，无 .git，实际 branch=N/A。固定 packet candidate SHA 由 root 在派发前以 dispatch receipt 精确绑定；本人核 instructions/own-input-manifest.json 和输入收据，禁止从目录名猜 SHA。
唯一可写 reports/、scratch/、review-status/；本人完整报告 reports/{r['key']}-r2.md，任务设置/终态读回 review-status/{r['key']}-r2.json。根 AGENTS.md、instructions/、immutable/、data/ 全部只读。
产品批准 base 5f910b52c69d86a1076b2032e5d3c63e715947f3；完整 source-only 候选 2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64；最终过程 61f53dbe76262f5003065900a4e97d9a6130014b，仅六 docs delta。原产品和供方树 STOP，不修改、不混合执行。
先读 instructions/receiver-guide-r2.md、immutable/current-policy-addendum.md、immutable/r2-guidance/ 四份现行规则、immutable/coverage-matrix.md/json、immutable/input-manifest.json、immutable/author-validation.json、immutable/candidate.patch.json 及 immutable/reference-diffs/。固定 archive 为 immutable/frozen-inputs.tar.gz；安全只读展开位于 data/snapshots/，保持各版本 namespace 分离。所有原件映射的 archiveMember 均加 data/ 前缀即可定位本人的完整普通路径。先核真实输入 SHA/manifest/receipt，再按完整 base→2cf 范围审查。

"""
    a = old.index("## 精确任务身份")
    b = old.index("## 全部原需求和固定范围")
    prompt = old[:a] + identity + old[b:]
    prompt = prompt.replace("docs/architecture/m0-review-and-update-plan-2026-10-19.md", "docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md")
    prompt = prompt.replace("reference-C4/docs/reviews/I05/inputs-c1/、round-4/full-review-input.md", "reference-C4/docs/reviews/I05/inputs-c1/七件、round-1/full-review-input.md、round-2/full-review-input.md、round-3/full-review-input.md")
    prompt = prompt.replace("见guidance/", "见immutable/guidance/")
    prompt = prompt[:prompt.index("## 本任务专属设置与输出")]
    prompt += isolation
    prompt += f"\n## 本任务专属设置与输出\n\n指定 {r['model']}，thinking={r['thinking']}，逐任务权限={r['permission']}。这是待真实读回的要求，不是已派发记录。仅写本人 reports/{r['key']}-r2.md 与本人必要结构收据。原生 ID 不可见时写 unknown 并列可定位标题，association 标签另列；默认配置不证明逐任务设置。实际任务当前 0、设置读回 pending、应用自动 metadata growth 未实测，不沿用其他任务身份。完整原验收、所有原 Fail 与运行缺证仍须在最终结论逐项交代。\n"
    prompt += "\n" + mapping + "\nshape a15 相对43d 的143项过程原件在 immutable/shape-process-map-r2.json 显式映射到四现存 integer/date namespace，逐路径/blob/bytes/SHA 相同；不是新缺包，也不代表其结论可以替代本次独审。\n"
    assert "round-4/full-review-input.md" not in prompt
    assert "I05-retained-source-review-package\n" not in prompt
    other = next(x for x in reviewers if x is not r)
    assert other["root"] not in prompt
    write(f"{r['key']}-input-r2.md", prompt)
    contract = {"format": "i05-own-wrapper-contract/2", **r, "branch": None, "branchReason": "standalone ordinary directory without .git", "prompt": f"instructions/{r['key']}-input-r2.md", "report": f"reports/{r['key']}-r2.md", "status": f"review-status/{r['key']}-r2.json", "readOnly": ["AGENTS.md", "instructions", "immutable", "data"], "mutable": ["reports", "scratch", "review-status"], "applicationMetadata": "review-status/application-metadata", "applicationMetadataGrowth": "pending actual application task creation; empty setup baseline only", "nativeTaskId": None, "settingsReadback": "pending", "noGlobalOrPeerDiscovery": True, "accidentalCrossRead": "STOP immediately; preserve observed minimal event without further reading/deleting; report to root for independence decision"}
    write(f"{r['key']}-own-contract-r2.json", contract)

write("receiver-guide-r2.md", """# R2 活跃审查入口

本 workspace 只保留一个本人 prompt，位于 instructions/；本人 contract 和 own-input-manifest 同目录。以本人 prompt 为完整任务入口。immutable/ 是共同冻结原件，data/snapshots/ 是经 manifest 安全展开且不可执行的分版本只读源码。禁止执行任何源码或测试。

必读 immutable/original-material-map-r2.md/json 的19项固定原件；活跃 M0 为 main-source-only/docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md，I03 同名 inputs 副本字节相同。历史 I05 全输入只有实际 round1/2/3 与 inputs-c1 七件。immutable/shape-process-map-r2.json 提供 a15 过程143件在四现存 namespace 的显式同 blob 映射。不存在的旧 M0/round4 指路已撤为历史，不延用。

immutable/independent-review-r1.md 是备包 R1 的独立 Fail 原件，属于共同固定备包历史；不是本轮另一指定模型的意见。历史 C1 两报告与终态在 data/snapshots/reference-C4/docs/reviews/I05/round-1/，必须阅读。本轮其他任务的 prompt、意见、过程和自动状态禁止发现或读取。

copy-ready 仅代表本地输入复制与结构预检，不代表任务创建、应用 metadata growth、设置读回、产品运行或指定 Pass。仅 reports/、scratch/、review-status/ 可写。实际设置或输入异常立即停，报告 root。
""")

common = ["frozen-inputs.tar.gz", "input-manifest.json", "candidate.patch.json", "coverage-matrix.json", "coverage-matrix.md", "retained-branch-queue.json", "author-validation.json", "author-finish-first-failure.json", "author-first-readback-interruption.json", "bootstrap-incidents.json", "text-correction-whitespace.json", "staged-whitespace-result.json", "final-input-audit.json", "candidate-git-manifest.json", "candidate-complete-manifest.json", "packet-file-manifest.json", "guidance-manifest.json", "current-policy-addendum.md", "independent-review-r1.md", "independent-proof-r1.json", "root-review-r1-receipt.json", "original-material-map-r2.json", "original-material-map-r2.md", "shape-process-map-r2.json", "guidance-manifest-r2.json", "prior-originals-preservation-r2.json"]
common += sorted(x.relative_to(P).as_posix() for directory in ["reference-diffs", "guidance", "r2-guidance"] for x in (P / directory).rglob("*") if x.is_file())
spec = {"format": "i05-physical-copy-spec/2", "revisionBase": BASE, "sourceBase": "5f910b52c69d86a1076b2032e5d3c63e715947f3", "sourceCandidate": "2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64", "sourceProcess": "61f53dbe76262f5003065900a4e97d9a6130014b", "common": [{"source": n, "destination": "immutable/" + n, **digest(P/n)} for n in common], "reviewers": [], "materialization": {"destination": "data", "memberManifest": "immutable/input-manifest.json", "expectedMembers": 22492, "types": ["regular", "backward internal hardlink"], "validation": "all paths are relative POSIX without dot/dotdot, no symlink/special type, exact manifest member order/type/size/target; hardlink target previously verified in same wrapper; full SHA256 and Git blob checked; strip execute bits", "fileMode": "0444", "directoryMode": "0555", "noCrossWrapperLink": True}, "mutableDirectories": ["reports", "scratch", "review-status", "review-status/application-metadata"], "ordinaryPhysicalCopies": True, "noSharedGit": True, "safeSetupOnlyNoExecution": True}
for r in reviewers:
    files = [{"source": f"{r['key']}-input-r2.md", "destination": f"instructions/{r['key']}-input-r2.md"}, {"source": f"{r['key']}-own-contract-r2.json", "destination": "instructions/own-contract-r2.json"}, {"source": "receiver-guide-r2.md", "destination": "instructions/receiver-guide-r2.md"}, {"source": "r2-guidance/AGENTS-current-r2.md", "destination": "AGENTS.md"}]
    for f in files:
        f.update(digest(P/f["source"]))
    spec["reviewers"].append({**r, "files": files, "nativeTaskId": None, "settingsReadback": "pending", "actualApplicationGrowth": "not-tested"})
write("physical-copy-spec-r2.json", spec)
write("isolation-plan-r2.md", """# R2 隔离计划与真实状态

两普通 wrapper 已由总控实际创建并将唯一 setup 写权交给本备包作者：

- /Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-review-zcode
- /Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-review-minimax

登记原件为 iteration-control/2026-10-21-weekly-release/additional-review-roots-20261022.json；仅核本两根，创建不代表输入就绪。physical-copy-spec-r2.json 是精确复制白名单。先冻结 R2 candidate，再复制最终字节，setup receipt 绑定实际 candidate 与逐件 SHA/inode。当前实际任务数0；不启动应用/模型/GUI。是否 copy-ready 仅以实际 setup receipt 为准。

每根只收到本人一个当前 prompt、本人 contract、共同不可变数据；不复制主 readme/dispatch/isolation 中的 peer 路径，也不复制旧 R1 两个 prompt。共同历史 C1 双报告是必需固定输入。每根独立 reports/scratch/review-status/application-metadata，空目录基线据真实检查登记；应用生成 metadata 的增长尚未发生，只允许以后按当前任务精确确认路径，禁全局发现。

常规物理复制不使用跨根硬链接；归档以流式安全 materialize 校验所有相对路径、类型、manifest、后向根内 hardlink、完整 SHA/Git blob，移除执行位且各 namespace 分离；不盲 tar 解包，不执行产品。核完整根内 pathset/所有 inode：输入0444与目录0555、输出0700，输入/输出无共享 inode，两根无共享 inode，根外无符号链接。异常立即停，保真实首失败；不删除证据。

意外串读立即停止审查和继续读取，最小真实事件留本人报告，root 判独立性。本人 prompt 不泄露 peer 根路径，不允许 Git worktree inventory、兄弟目录或全局任务扫描。full access 只为逐任务设置，不能扩大 scope。静态源码完整审查可先做，原运行门、HOLD/native/审批限制继续保留。
""")
write("dispatch-r2.json", {"format": "i05-dispatch/2", "state": "candidate-preparation-not-dispatched", "revisionBase": BASE, "packetCandidate": None, "packetCandidateBinding": "root records exact frozen candidate; setup receipt must bind copies to that commit", "actualTaskCount": 0, "actualTasks": [], "sourceCandidate": spec["sourceCandidate"], "sourceProcess": spec["sourceProcess"], "reviewers": spec["reviewers"], "requiredReadback": ["actual standalone workspace root; branch N/A", "actual fresh native task ID or unknown plus real title and separate association label", "exact task model/thinking/permission", "actual own prompt SHA and packet candidate plus input-copy receipt", "own initial metadata baseline and any actually created task-local paths; no global/peer discovery", "actual completed terminal and full own report hash"], "applicationGrowthVerified": False, "inputCopiesReady": "see actual setup receipt; creation alone insufficient", "independentPackageDeltaReview": "pending root-appointed independent reviewer", "noProductExecution": True, "noModelDispatchByAuthor": True, "pushPrMergeAuthorized": False})
write("disposition-r2.md", """# R1 两 P2 的 R2 处置

PKT-R1-P2-01：旧 prompts/README/manifest 不改。新增两份完整 R2 prompt，活跃 M0 改为真实 I01 inputs，I03 副本相同；真实 C4 round1/2/3 与七 inputs-c1、历史 C1 双报告/终态在19项 Git/blob/bytes/SHA 映射中。旧不存在路径明确废止。shape a15 的143过程文件在已有四 integer/date carrier 逐路径/blob 等同，新增显式映射，既不造缺包也不重压归档。

PKT-R1-P2-02：新增 physical-copy-spec/isolation/own contract，两个真实独立普通 wrapper 分别只复制本人 prompt，输出和应用 metadata 命名空间独立。复制/只读 materialize/完整 pathset/hash/inode/空 baseline 由 setup receipt 记录真实结果；应用任务与 metadata growth 未发生，不冒已测。本次提供准备和结构证据，最终是否关闭由 root 的独立 delta 审查决定，作者不自认指定 Pass。

不更改原57门、全部原工程范围、历史 Fail、未签 native/HOLD/审批限制与运行缺证。旧134件原件逐 SHA 不变；原首失败及 immutable 作者器 whitespace exit2 保留。实际指定模型任务0。
""")
write("readme-r2.md", """# I05 保留完整源码审查包 R2 活跃入口

R1 备包独审 Fail 已封存于1106f15629c41833be9c9604eb7bf02134fa0541。此版只修复真实原件指路与本轮物理任务隔离，完整范围不缩减；旧 R1 prompts/README/manifest/report/proof/归档等134件保留原字节，旧 README 仅为历史，不作为新派发入口。

活跃提示为 zcode-glm53-input-r2.md、minimax-m31flash-input-r2.md；精确原件19项与shape过程143项分别见 original-material-map-r2 和 shape-process-map-r2。主2cf整个工程和16版本 namespace、22492 member、17 diff、148×8覆盖矩阵、211 blob 原证据不变；22=6891只覆盖22模块，不能声称完整旧工程/47测试都已采用。

physical-copy-spec-r2.json 固定最终复制字节；isolation-plan-r2.md 与 dispatch-r2.json 给实际两根及唯一 setup/待派发身份。每根只给本人一个 prompt，禁止复制本主 README/dispatch/isolation 的 peer 地址。setup receipt 将实际复制与 packet candidate 绑定，copy-ready 不能代 task/settings/application-growth ready。

原归档84876346B SHA4bbbd798e6c7a67153db51e185c8795d9ac3509cc4442a81e2071bf319dfaa12 不改不重压。固定 source base5f910b52c69d86a1076b2032e5d3c63e715947f3、candidate2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64、process61f53dbe76262f5003065900a4e97d9a6130014b。当前指定任务0，无模型/GUI/产品/测试/安装/native/DB/network 执行。本次所有纯结构作者结果仍待独立 delta 复审。
""")
print(json.dumps({"prompts": [{"path": f"{r['key']}-input-r2.md", **digest(P/f"{r['key']}-input-r2.md")} for r in reviewers], "commonFiles": len(common)}, ensure_ascii=False))
