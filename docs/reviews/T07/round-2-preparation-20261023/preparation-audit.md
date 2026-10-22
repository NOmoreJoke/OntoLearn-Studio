# T07 R2 独立准备静态审查

结论：**本次 R2 准备静态范围通过，未发现需阻断准备交 root 预检的 P1/P2 实质错误。** 任务仍为 0，GUI RELEASED，实际模型设置、fresh SID、原 turn、官方附件及正式终态仍为空；本报告不创建任务、不授予 GUI 租约，不代表指定双审、148 项可见 EOF、产品或发布通过。前轮 PROCESS_FAIL 保留，不沿用前轮作者的“限 S1 通过”。

审查者 `/root/t07_dispatch_preflight_audit`，2026-10-23。收到 owner READY 后，仅核本次准备、两个明确新根及其独占 runtime 中给定输入/模板/来源/安装日志；允许共同阅读的内容仅为本树封存前轮终态历史。未访问旧 review roots、原应用 session、其他任务/controller 实时状态、全局元数据或凭据。使用当前已读 AGENTS 与 Audit and Verify 技能；只读 Git/文件与 Python 标准库身份检查，唯一新增报告为本文件。未改 Goal、产品、测试、配置、锁、旧输入/manifest，未 stage/commit/push。

## 1. 本次固定输入与来源

固定 B=`5f910b52c69d86a1076b2032e5d3c63e715947f3`，P=`f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3`，R=`fdfd908e36a85140078aa1509f091de369157973`。两新根实际均为 detached R，B→P→R 祖先关系成立；P→R 的 127 项差异全部在 `docs/reviews/T07/`。本次验证新复制件的来源，不重测旧 14 项产品、不重复原 native 取证。

- ZCode 根：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-zcode-review-r2-f9a1157`；runtime 为该绝对根后加 `.runtime`。
- MiniMax 根：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-minimax-review-r2-f9a1157`；runtime 同理。
- 两方精确 scratch 均为本角色 runtime 下 `scratch/probe-copy`。
- 当前 AGENTS 为唯一获批 protected M，SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。两树 tracked diff 唯一为该文件，index 无变更；角色 `current-AGENTS.md` 为准备副本，不赋予修改规则权限。

ZCode 完整输入为 **242491 B / 1700 个换行**，SHA256 `513da17b6f17e8004244cbc72c8f98dbc55a837862bd9c4d6d5c5ae80814c87d`；MiniMax 为 **242581 B / 1700 个换行**，SHA256 `525ac36e5e505c103760501ada799c4399b3780559891a3a1b6b28f8e2ed8ede`。owner 文件与各角色 `docs/reviews/T07/round-2-input/full-input.txt` 均逐字节一致，符合 dispatch/input manifest。

独立按 `current-prefix-template.md` 的本角色替换值、六份历史全文的边界标题及原始字节、旧完整输入重建整个输入，结果两份均精确相同，无未替换占位符。六份内嵌历史的长度/hash 符合各记录，包括两作者完整报告、时点证据独审、原生接收补审、PROCESS_FAIL 裁决、七意见 JSON；不是用其摘要替代全文。旧 143012/143054 B 完整输入分别为精确 suffix，原 hash 仍为 `bfd74c930cddbc9274ef05e30f7c3eaf482a56ff3caa5a10718fdc30128c7287` / `153dc55dbae5e3b27b8ae65e0a74f14e1da01c36398cffa477691269f7e325dd`。新规则优先，旧 workspace/报告/SID/turn/权限和历史状态只能作为历史，不复活为本轮操作许可。

每方 full-git-files 的 935 路径集合与 `git ls-tree -rz R` 一致。逐项重算新 root、scratch 与 source-snapshot.tar 的字节/blob：**934 项精确等 R，唯一差异为两副本相同的 protected AGENTS**。来源 tar hash、935 个 regular-file 成员及 Git 对象均一致。owner 与 role 的 full-git-files、required-reading、input-manifest 副本逐字节一致，角色 manifest 与 dispatch 对应记录相符。没有将状态过程文件的 R 字节冒称为 P 原件。

## 2. 完整范围与 EOF 门

每方 required-reading 均为 **148 个唯一且存在的本角色绝对路径**，长度/hash 与实际文件一致，没有指向另一角色或父项目的读取项。分组完整：14 项实现/测试/fixture、25 项 P 候选原件镜像、1 份完整 candidate.patch、1 份 B 的完整 PRD、31 项当前指南/前轮封存历史、1 份当前 AGENTS、75 个旧归档原件（73 文本、2 PNG）。所有 `actualReadCompleted=false`、`requiredVisibleEOF=true`；不是准备 owner 代签已读。

25 项新 `history/product-candidate/` 镜像分别与给定 P 的 Git 文件相同；`history/approved-prd-v0.6.md` 的 93584 B 与 B 的完整 PRD 逐字节相同。75 个本角色新提取原件逐项符合固定 archive-manifest 的大小/hash，均非 symlink；其中确为 **35 个 log/PNG**。不把 35 写成 32，不将空日志当 exit0。CSS、`__init__.py`、169895 B / 4963 换行的 t09-e5、13004 B / 530 换行的投影交接样例均明确列入完整可见全文要求。

前缀第 17–28 行要求官方附件与本地完整输入分别核实，按工具**实际返回**范围续读至 EOF，不能用请求 limit、隐藏 details、json.load、hash、keys、head/tail 或测试内部读取替代模型可见全文；ledger 记录 call/返回范围/截断/续读/EOF。必读缺项、身份不符或必要运行未验必须明确 NotPass/未完成。完整 25/14、PRD 全文/附录、原验收、9 原 final、IR-01～05、12 项父积压与全部前轮已封存 calls/results 均保留，不缩成七意见或 delta。

本审查验证的是材料齐备、字节来源与读取要求，**没有执行外审模型的 148 项全文阅读，也没有逐图重新审查旧 PNG 或重判前轮 native 链**。正文与清单为后续模型提供全文，不等于后续接收/可见 EOF 已完成。工具输出截断不影响本次程序性逐字节来源比较，但不被本报告包装成可见全文审查证明。

## 3. Fresh 身份、独立性与写面

两方精确 `metadata/operator-identity-receipt.json` 及其 role template 副本一致：state=`TEMPLATE_NOT_SUBMITTED`、tasksCreated=0、GUIReleased=true，actualSettingsUI / actualSessionId / originalTurnId / officialTerminal / officialAttachment 全为 null。所写 GLM-5.3/最高/完全访问与 M3.1-Flash/xhigh/始终授权只是要求。缺真实读回不得当完成，不沿用前轮旧 SID/turn。

前缀第 13–14 行把 operator 收据限定为给定唯一绝对路径；缺失/不一致报 UNKNOWN，不执行 agent/list、sessionget、全 session、globalconfig、`.mimosa` 正文或父目录 find，不读取其他 runtime/任务/controller 队列。R2 peer 的报告、状态、metadata、模型意见与发现性枚举均禁止；本方树内封存的前轮双方终态明确属于共同历史。此边界没有被旧完整输入中的历史绝对路径覆盖。

唯一最终报告分别为新根 `docs/reviews/T07/round-2/{zcode-glm53,minimax-m31flash}.md`，要求本任务真实 Write/Edit；取证仅本方 raw/validation、reports 与明确 reviewer metadata，operator 收据模型只读。实现/测试/fixture/验收/PRD/配置/锁/源码政策、旧报告与冻结原件只读，不新加 ignore、不删 metadata 求 clean，不 commit/push/切分支。

## 4. 执行、拒绝及 scratch 边界

前缀第 32–39 行保留必要普通 check/vitest/pytest/lint/typecheck/build/verify:sources 和固定受控 worker/SQLite/READONLY/os._exit，未泛禁原 suite，未扩为真实产品适配或物理资源研究。每项必须直接原入口、全新 stdout/stderr 分别留存，紧接目标取整数退出码并保存 argv/cwd/时段/非敏感路径；禁止 tail/head/grep 丢上游或用管道末尾退出码冒充目标，自动截断须取完原输出。不以历史计数自填本轮结果。

任一自动审批/安全扫描/平台拒绝，须保留原命令/call ID/理由/状态并把该项标未验，报 root 精确裁定；明确禁止换脚本、Write 后执行、重定向改写、不同工具/身份或等价包装继续同一被拒目的。完全访问、可能误报或 Write 成功均不解除。独立只读工作可继续，此规则没有把拒绝变为产品失败，也没有把先前拒绝涂成“无首错”。

前缀第 43–47 行精确禁止固定 review cwd 运行 probe，也禁止在 review cwd 仅换绝对 scratch 脚本。必要且未被拒绝的探针必须在记录中 `cd` 到本角色 `scratch/probe-copy`、核真实 pwd，再用相对 `node docs/reviews/T07/evidence/render-probe.mjs` 调原未改脚本；不改 sandbox，只用已有授权 Chromium。原脚本自身 `.t07-ui-*` 回收是精确例外，模型不 rm 重建 scratch。before/after 与完整双流/直接 exit 保留，合成 UI 不提升为正式 App。

两 scratch 的 ui-probe before 副本均与当前固定 JSON 一致，before-state 指向精确 scratch 与 R；page-wide/page-narrow PNG 当前确实不存在，记录为 false，未补造。本次没有跑 probe。前述普通检查许可不授权 dev/HMR、Electron/e2e、engine/package 构建/产物运行、新 native/caller/producer/物理实验、真实模型/API、付费/重置或 reviewer CUA。

## 5. 新物理环境与 setup 证据

两 root/runtime、各自 scratch、root venv/node_modules、scratch node_modules、uv/npm cache、tmp、pytest、raw/validation、reports、metadata 都为各自实目录，resolve 无跨根，inode 各异。四套 node_modules 各有 13196 个 regular 文件；四套任意两套 regular-file inode 交集均为 0，symlink 均解析回对应 root 或 scratch。不是只依赖顶层目录名判断物理副本。两 venv 的 editable `.pth` / direct_url 均绑定本角色新根的 packages/engine，未指向旧树或对方。

setup-environments 源码仅按锁调用 uv sync frozen/no-python-downloads 与 npm ci ignore-scripts/no-audit/fund=false，清跨树覆盖变量并使用各自 cache/TMPDIR；stdout/stderr 分别独占新建，保存 subprocess 直接 returncode 后才处理副本。四条 setup 记录均 exit0，八份原始 stdout/stderr 大小/hash 与记录相符，完整输出已核；空 uv stdout、Z uv retry warning、npm deprecated/版本 notice 均保留。未据此推断 Electron、产品 check 或运行通过，本审没有重跑安装。

preparation-first-error 保留系统 Python `tarfile.extractall(filter=...)` 不支持的 TypeError，以及其发生于创建新根/空 runtime 后、无产品执行的事实；后续记录为 regular-only 路径校验解包，现有两套新解包结果逐项 hash/regular-file 身份符合。该语言 API 兼容错误不是自动审批拒绝，不把兼容修正误当绕过安全拒绝；也不隐藏首错。

本审查初次读取试用了不存在的 owner `setup-results.json`，cat exit1；实际按已列 `{zcode,minimax}-setup.json` 和 dispatch 角色内记录完成校验。属于审计路径误试，无文件修改/产品执行，不将其记作成功或产品失败。另一次诊断输出的两方完整路径列表被工具截断，本审通过程序性全清单逐项存在/字节核对完成准备身份核验，没有声称该截断输出构成 148 项模型全文覆盖。

## 6. 前轮失败、七意见及后继门

旧作者报告 19230/30205 B 保留其原文，不改为本轮报告；旧证据独审的当时 UNKNOWN 与后续原生补审解除项并存，PROCESS_FAIL 原文明确保留实际阅读缺项、M review cwd 原位 probe、tail/退出证据缺口、Z 拒绝后包装与首错未披露、M 扩搜身份边界。新前缀逐项给出防复发约束，不拿同 SHA、后继 scratch 重跑或工程 P3 登记抵消流程失败。本审未重新取证或自行豁免前轮事实。

七意见 JSON 全文内嵌且保留：未来事件 initial_consumed、资源选中即完成、原行 hash 方法、ignored log/png 追溯、状态/失效标签、续跑 initial phase、动作序号连续性。既有依据、拟定责任和延期条件完整，`responsibilityAcknowledgedByOtherOwner=false`，未虚称其他 owner 已接收。没有为求绿临时引入新契约或改候选；若实际实施/测试/契约/验收/配置/依赖/base 变化，仍按新候选、必要验证、双方全新完整审查。

真实 T05/T06、T01/I04 生命周期/取消/原子进度/终态/响应丢失对账、公共契约/bridge/App、真实删除/恢复/快照续跑、完整 E5 四类领域结果、T10 跨设备、父 FR/附录、双 OS、真人、CI、远端与发布门全部保留。fresh 两任务仍需实际设置/受理/可见 EOF/运行证据/Write-Edit 绑定/完整终态、全部意见处置和同版审查结论，之后才能触发原 push/PR/CI/合并门；准备审查不关闭这些门。

## 7. 补充操作壳与 root 预检材料

补充核完 owner 的 root-preflight、两 short-launch、operator-create-checklist 与 preparation-error-log。两方 root-preflight role 副本均与 owner 原件逐字节相同；两 English short-launch 各自明确写出新 root、full-input 绝对路径/完整 hash/bytes/1700 newline、operator 收据、唯一新报告与精确 scratch cwd，不用“同根后加”代替关键地址。完整附件和前端中文规则继续为准，短操作壳没有替代 25/14/PRD/全历史、EOF、拒绝停报、直接 exit 或写面限制。

operator checklist 仍为 `PREPARATION_ONLY_ROOT_PREFLIGHT_PENDING` / newTasks=0 / GUIReleased=true，actual 设置/SID/turn/terminal 全 null；要求 fresh 空任务、官方菜单定向身份与真实附件受理，不授权审查模型扩搜。root-preflight 明确没有内部创建交接不得创建，文件存在不等于 root 已实际放行。

preparation-error-log 另保留旧统一 manifest 路径误试，以及 short-launch writer 在任何写入前的 Non-UTF-8 Python parse 失败、后用 ASCII source/显式 UTF-8 的修正。均为准备读取/语言解析错误，不是自动审批拒绝，不把它们当无首错或被拒验证的替代包装。补充文件生成后，两完整输入 hash 仍与上文一致。历史附件换行/EOF 空项按原件解释，本次 manifest 的 1700 明确为 newline 数，不擅自改称物理行或完整可见阅读次数。

补充核 `setup-originals-index.json` 的八份 stdout/stderr 固定副本，均与各给定 source 逐字节相同，大小/hash 符合；复制封存没有运行原命令或变化退出记录。operator-only precision-note 明确更正前轮两附件 896 LF/末 LF、Z 显示 897 为 EOF 空项；历史原报告不改。本次两 R2 输入实际均为 1700 LF 且末字节 LF，旁注未改变正文、清单或候选。本审不为此重取旧 native 链。

## 8. 最终限定结论

本次准备物无 P1/P2 阻断，无需因此改旧输入或候选。**只通过 R2 准备静态范围，交 root 预检；任务 0、GUI RELEASED、root 实际预检 PENDING 与 operator UNKNOWN 模板状态继续保持。** 本审未运行产品、测试、build、headless、Electron/native、外部模型或 CUA，未读实时任务状态，未伪造完整外审阅读或正式终态。未来真实派发与运行应按本前缀和 root 当时精确授权执行。

文档验证：仅对本报告执行本树现有 `npx --no-install prettier --ignore-path /dev/null --write` 与 `--check`；write 未改变格式，check exit0。未扩展为产品检查。
