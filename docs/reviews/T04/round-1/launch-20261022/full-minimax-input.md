# T04-S1 MiniMax M3.1-Flash 实际完整新任务正文（待 root 预检与短 lease）

这是本轮唯一指定审者的完整输入。不得把它当已创建任务、GUI lease、设置读回、指定 Pass 或父 Goal 恢复。操作者只能在 root 明确授予 T04 短创建/核验 lease 后通过 computer use 新建；当前 T01 先创建，T04 仅准备。你收到实际任务后独立审查整个固定 S1，不只 UI/reader 或某个 stage 摘要。

## 生效顺序与精确映射

原完整冻结 prompt 在下文按原字节附带，SHA `9873b3f6797d72937fd2da25c204b9aaf57f8c53ccdefc0e7b75b0097dd5ca9a`；原 manifest/旧输入均未改。其完整范围、历史事实及原需求保留；其中旧“禁止任何验证/只能写唯一报告/无 GUI/必须后台或独立桌面/用户时段/CLI 前置/原树报告目录”只是历史，操作条款由本正文的精确映射、执行补充和当前政策明确替代，不得继续用旧文字阻止必要普通验证。不得借此改产品、降验收或扩大到被拒绝研究。

- 你的唯一实际工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-554ec89`，detached HEAD `9a4dfc8f1e9106a4c05423f80a26e9e88eb0aaa1`，无开发分支；不得 checkout/reset 或切到原开发树执行。
- 固定 product `554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；review HEAD 的后来差异仅流程证据。完整 product diff 170428 字节，SHA `777ef6d58b8697530024ad4c47110443b613b9ba7de37d8420fae97e44b6c651`；全部 33 项源码/测试/fixture/文档的固定 Git blob 逐项在 `mapping-minimax.json`，必须全部审查。
- 保护 AGENTS 当前 SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，是阶段主聊天传播的未暂存 M，不是产品变化；审者不覆盖或格式化它。
- 你仅使用本方隔离 node_modules/.venv，安装已 exit0；setup-minimax.json 是备环境收据，不是测试或 build 通过。缓存/tmp/反例/raw 独占 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-554ec89/test-results/t04-review-runtime/minimax`，运行时设置 `npm_config_cache=/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-554ec89/test-results/t04-review-runtime/minimax/cache/npm`、`UV_CACHE_DIR=/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-554ec89/test-results/t04-review-runtime/minimax/cache/uv`、`TMPDIR=/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-554ec89/test-results/t04-review-runtime/minimax/tmp`；不共享对方环境或用户运行库，不打印其他环境变量。
- 唯一最终报告：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-554ec89/docs/reviews/T04/round-1/minimax-m31flash.md`。正常构建/cache/tmp、独占反例/raw/运行收据按执行补充允许写；source/tests/config/locks/Git/验收/历史输入/对方报告只读。可新增本方当前报告，但不以占位文档冒充模型结论。
- 指定设置：**M3.1-Flash / xhigh / bypassPermissions**；必须本轮新完整独立任务，实际 provider/model/最高可用等级/思考/权限/路径由操作者逐任务读回。actual task ID 和设置当前未产生，不得自填；实际读回记录须引用其真实来源。
- 不读取另一方本轮 prompt、反例、raw、报告或意见。原树仅为来源指针，不在原树运行或写报告；另一个 review 树不进入。本方独立作完整判断，不委派替代指定模型最终审查。

## 必须完整读取并独立核对

读取本方 `mapping-minimax.json`、`delivery-manifest-minimax.json`、本正文、setup-minimax.json，以及本方已有原33项manifest、`review-inputs.md`、`verification-and-history-index.md` 和其全部原件。内审1–8都读，完整复核R1-01/R1-02/R5-01..04/R6-01、同版本终态、同数量错义与原件归档R1的处置，不以旧closed或其他模型意见代判断。产品原 `status.md` 用固定554 Git blob读；当前物理status属于后续过程。父FR-400–404/FR-006/C/D/G Q-01/02/O-01及11–12和全部原门保留。

下面是原完整 S1 核对点，当前全部适用：

## 完整审查范围与具体核对点


- Python `query_service` 与 TS `draft.ts`：模板、对象/返回字段/条件编译、名称/说明/SPARQL/范围/关联问题/source 的完整意图；RDF IRI、语言/datatype/literal 安全序列化、数值/类型/边界/异常，编写不能激活执行、授权、第二 schema/writer/Store。Python/TS 与 golden case 一致；不能把同数量当完整答案正确。
- 批准 T09 固定输入：17 项与 PRD 来源 hash/provenance、独立还原 G-base、原查询和生成查询各完整 A01、Closed 空集、错误 A02 同行数反例；不用 expected 预填 Store，不消费 T09 helper 或未批执行器，不能当正式 Q-01/02 联验。
- `QueryPage.tsx`/CSS/结果工具：模板、可视条件/返回字段、可见 SPARQL 编辑/model 草稿载入、范围持续可见、历史选择与结果身份；源字符串按纯文本转义显示，表格/null“未记录”语义、空页与后续页区分及可操作检查方向；单页最多 200 行、CSV 公式/引号/分隔符边界；不以 URL 外观伪造 RDF 类型/图，不把编辑器后来文本冒充实际执行原文。
- 保存/复用 UI：同名不同定义、新建成功真实 ID 回执、更新 ID 不变、request/document generation/编辑 revision、新建/切项目/载入/卸载/迟到响应和保存期间新编辑。没有真实 adapter 时禁用执行/保存；不能声称已持久化/联通，不能 renderer 发 ID/直接写 Store。真正基线/CAS/preview/confirm/commit/对账仍属父接线缺口。
- `results.ts`/`reader.ts`：直接复用批准 validator/TaskView/TaskUpdate/getResult/getResultPage/getJob/cancelJob；项目/job/result/snapshot/scope/params/definition/derived 身份、generation/input 切换、迟到响应拒绝、实际发行 cursor 单页读取、页内及跨空页稳定排序/有界锚、缓存载荷回收仍保身份。不扩大 bridge 或公开新协议。
- 取消/任务：仅同项目 query.execute；single-flight 覆盖 ACK 后真实 job 重读；取消受理与实际终态分开；ACK 已知版本下限覆盖后续读/通知/取消前查；同版本矛盾和已观察终态重开拒绝，不拒绝合法跳跃观测；此前结果与当前任务区分，卸载/切输入清理。
- 错误：INVALID_REQUEST 的批准 identity/params/cursor params.field、原始 bridge 异常固定 internal、受限 explainError，不泄漏原异常；无假结果/假执行、第二可变源、共享文件抢写或未批依赖。
- 专属全部 Python/TS 测试、fixtures/SSR 探针、全部新增文档及每项历史意见处置，不只审查实现摘要。完整 diff/33 项来源要与 manifest 全等；之后过程仅文档证据，不以物理 status 与 product 原字节不同误判源码漂移，也不能隐瞒真正产品变化。


## 已有验证与父缺口


最终固定 554 全 `npm run check` 已真实 exit 0，TS 18 文件/666 项、Python 1083 项，新增 TS36/Python31，reader24 合成 transport、SSR14 有界静态继承，独立内审最终通过。原始失败和最终日志在 37 成员无损归档，开发线/总控已 Git blob 读回关闭 R1。你必须独立阅读原件确认适用范围，不能将旧 640/642 TS 汇总或旧 SSR8/11 当最终数据，也不能把这些结果升级为真实 IPC/浏览器/Store/平台通过。

完整 T04 仍未证明：真实 query.execute/项目内只读与外联拒绝、真实 Q-01/02/分页/游标/取消/历史、T01 原子保存/preview/confirm/commit/恢复/撤销/过期、T08 真实模型草稿/工具闭环、ASK 与真实 RDF/执行文本元数据及局部图、App/T10 跨设备、Windows/macOS/真人/父 P0/跨模块/发布。S1 范围已登记可独立审查，不以等待整个 M0 替代 S1 判断；同时必须报告这些真实父缺口，不能把 S1 通过写成完整产品验收。此轮尚无指定双审通过、push/PR/CI/merge/上线。


## 本方验证、报告与完整终态

你可在独立环境自主运行本补充允许的必要普通静态/单测/SSR/check/build和受控原有worker回归；先静态核精确入口。不机械重跑所有不变历史，也不得因旧输入过宽禁令而拒绝必要验证。反例只在本方独占ignored目录，不改原源码/测试/验收真值。保留首失败、完整argv/cwd/起止/真实exit或信号及完整raw/hash；不能用skip/xfail/删断言/失败后筛绿冒充整套通过。若范围涉及被拒绝的SQLite/heap/OS研究、新native/caller/producer或运行票缺失，按边界报告实际未验/阻断，不绕过也不假称通过。普通SSR/合成transport/受控worker不是真实业务IPC/Store/App联验；可用反例证明未接线缺口。

报告须包含实际task来源/ID、创建和正文接收时间、逐任务模型/思考/权限/路径真实读回；base/product/review head/实际cwd/提示及映射hash/33项与完整diff；完整范围和全部历史项逐项复核；每次实际命令完整结果及首失败/必要后继验证/未验边界；发现的严重度、实际文件行号、触发/影响/证据/建议；审前审后冻结源码/测试/锁/Git一致性；明确给出“通过/不通过/无法验证”之一，仅适用于同版完整S1，父功能未完成。

写完本方报告后正常完成指定任务，让操作者读回真实terminal和全文报告；文件存在不是终态。认证/额度/模型/路径/源码漂移要保留官方错误和句柄，不能换模型/创建重复任务/直接改实现。发现需修由唯一owner修后必要验证和双方新同版完整审。任何一方不通过不能自己改成通过；push/PR attach/实际CI/正常合并/远端与两OS/真人/原57P0全部门不变。当前准备无taskID、无actual settings、无T04GUI lease、无实际指定结论。

## 原完整冻结 prompt（原字节，仅作完整范围与历史输入；操作以本轮更新为准）

<!-- BEGIN ORIGINAL FROZEN PROMPT -->
````text
# MiniMax M3.1-Flash 完整独立审查输入

你是本轮指定的独立完整范围审查者。对 T04-S1 给出有证据的通过/不通过/无法验证结论；不要实施修复。当前文件是冻结输入准备，不是实际审查任务或批准运行。只有总控实际授予 T04 独占后台 lease、操作者按官方入口核验你的任务后，才允许投递本正文。

## 身份、设置与运行边界

- 审查对象：T04-S1 完整独立查询编写与批准读取客户端。原工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-query`，分支 `feature/weekly-t04-query`。
- 固定 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，product `554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6`，准备前 process `e761d2962aa18c83885dde4cc0dcd15fd9aba322`。本包提交/实际 workspace 如另有独立映射收据，按已核映射读取；不能猜目录、重置 checkout、换分支或消费未批准实现。
- 平台和设置：MiniMax Code 的真实 M3.1-Flash，reasoning=xhigh，permissionMode=bypassPermissions（始终授权/Full access）。操作者必须逐实际任务读回 provider/model、思考等级/可用等级和执行权限；用户级默认、任务标题、CLI 包名、目录或旧会话不算证据。必须是本轮新独立完整任务，不复用旧 task，不降模型或思考等级。实际设置无法达到要求则不得按替代模型开始，说明具体错误/恢复条件。
- 你只审查本任务，不创建另一模型任务、不委派替代指定模型的最终审查、不读取对方本轮 prompt/报告/日志/意见，不以其他 agent 的通过替代自己的判断。历史 Codex 内审 1–8 可作为需要独立复核的共同输入。
- 无本机 GUI/Electron/e2e/native/HMR/端口服务/浏览器或产物启动；不切应用、不抢焦点、不调用 CUA。不读取/输出密钥，不改认证/订阅/额度，不新增 API/付费，不猜内部 HTTP 或写任务库。仅已授权官方后台审查通道执行本任务。
- 实现/测试/配置/依赖/验收/AGENTS/历史输入全部只读。只可写自己的报告 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-query/docs/reviews/T04/round-1/minimax-m31flash.md`；独立 workspace 如改报告路径，须已有单独 hash 映射收据，不得在原树以外自行落报告。不能修改任何代码、测试、锁、说明、其他报告，不能 git add/commit/push/PR/merge、切分支、重置、安装依赖或启动运行服务。
- 不重跑无变化完整 check/构建/打包/SSR/测试，不用扩大验证当作完成工作。按固定源码、原始日志和证据完整审查。若发现具体新风险需要运行验证，在报告给出触发、最小命令和未验边界，交开发线按实际授权运行；未执行就写未执行，不能伪造命令结果。只读 git show/diff/status/hash/读取归档原字节可用于身份/来源核验，不算产品复测。

## 必须完整读取的输入

1. 本目录 `frozen-input-manifest.json` 与 `review-inputs.md`，核验固定 33 项产品 Git blob、全部 base→product diff、支持证据和自身提示 hash。所有新文件都要审查，不只 UI、reader 或某个增量 stage。
2. 本目录 `verification-and-history-index.md` 及所指原始完整日志、三份汇总和 internal-review-1..8 全文。历史失败/暂不通过要逐项检查关闭；不能只看最终 pass 摘要。
3. `operating-policy-snapshot.md`、`protected-guide-snapshot.md` 全文及下方完整政策。历史共同指令中的旧归属以尾部实际生效更新为准；不因此采用未批准代码。当前实现仅批准 5f 接口。
4. 批准 base 中 PRD 的 FR-400–404、FR-006、附录 C/D/G Q-01/02/O-01、第 11–12 节与本线 acceptance/integration-handoff/reader-integration/service-stage。保持完整父需求，不将 S1 可审查改写成完整 T04/产品已完成。
5. 实际设置/输入接收和 lease 证据由操作者提供真实 task ID 与读回，当前包没有这些凭据；没有真实证据应标“无法验证任务设置”，不得自填假 ID、通过或终态。

## 完整审查范围与具体核对点

- Python `query_service` 与 TS `draft.ts`：模板、对象/返回字段/条件编译、名称/说明/SPARQL/范围/关联问题/source 的完整意图；RDF IRI、语言/datatype/literal 安全序列化、数值/类型/边界/异常，编写不能激活执行、授权、第二 schema/writer/Store。Python/TS 与 golden case 一致；不能把同数量当完整答案正确。
- 批准 T09 固定输入：17 项与 PRD 来源 hash/provenance、独立还原 G-base、原查询和生成查询各完整 A01、Closed 空集、错误 A02 同行数反例；不用 expected 预填 Store，不消费 T09 helper 或未批执行器，不能当正式 Q-01/02 联验。
- `QueryPage.tsx`/CSS/结果工具：模板、可视条件/返回字段、可见 SPARQL 编辑/model 草稿载入、范围持续可见、历史选择与结果身份；源字符串按纯文本转义显示，表格/null“未记录”语义、空页与后续页区分及可操作检查方向；单页最多 200 行、CSV 公式/引号/分隔符边界；不以 URL 外观伪造 RDF 类型/图，不把编辑器后来文本冒充实际执行原文。
- 保存/复用 UI：同名不同定义、新建成功真实 ID 回执、更新 ID 不变、request/document generation/编辑 revision、新建/切项目/载入/卸载/迟到响应和保存期间新编辑。没有真实 adapter 时禁用执行/保存；不能声称已持久化/联通，不能 renderer 发 ID/直接写 Store。真正基线/CAS/preview/confirm/commit/对账仍属父接线缺口。
- `results.ts`/`reader.ts`：直接复用批准 validator/TaskView/TaskUpdate/getResult/getResultPage/getJob/cancelJob；项目/job/result/snapshot/scope/params/definition/derived 身份、generation/input 切换、迟到响应拒绝、实际发行 cursor 单页读取、页内及跨空页稳定排序/有界锚、缓存载荷回收仍保身份。不扩大 bridge 或公开新协议。
- 取消/任务：仅同项目 query.execute；single-flight 覆盖 ACK 后真实 job 重读；取消受理与实际终态分开；ACK 已知版本下限覆盖后续读/通知/取消前查；同版本矛盾和已观察终态重开拒绝，不拒绝合法跳跃观测；此前结果与当前任务区分，卸载/切输入清理。
- 错误：INVALID_REQUEST 的批准 identity/params/cursor params.field、原始 bridge 异常固定 internal、受限 explainError，不泄漏原异常；无假结果/假执行、第二可变源、共享文件抢写或未批依赖。
- 专属全部 Python/TS 测试、fixtures/SSR 探针、全部新增文档及每项历史意见处置，不只审查实现摘要。完整 diff/33 项来源要与 manifest 全等；之后过程仅文档证据，不以物理 status 与 product 原字节不同误判源码漂移，也不能隐瞒真正产品变化。

## 已有验证与父缺口

最终固定 554 全 `npm run check` 已真实 exit 0，TS 18 文件/666 项、Python 1083 项，新增 TS36/Python31，reader24 合成 transport、SSR14 有界静态继承，独立内审最终通过。原始失败和最终日志在 37 成员无损归档，开发线/总控已 Git blob 读回关闭 R1。你必须独立阅读原件确认适用范围，不能将旧 640/642 TS 汇总或旧 SSR8/11 当最终数据，也不能把这些结果升级为真实 IPC/浏览器/Store/平台通过。

完整 T04 仍未证明：真实 query.execute/项目内只读与外联拒绝、真实 Q-01/02/分页/游标/取消/历史、T01 原子保存/preview/confirm/commit/恢复/撤销/过期、T08 真实模型草稿/工具闭环、ASK 与真实 RDF/执行文本元数据及局部图、App/T10 跨设备、Windows/macOS/真人/父 P0/跨模块/发布。S1 范围已登记可独立审查，不以等待整个 M0 替代 S1 判断；同时必须报告这些真实父缺口，不能把 S1 通过写成完整产品验收。此轮尚无指定双审通过、push/PR/CI/merge/上线。

## 报告和完整终态

只写自己的 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-query/docs/reviews/T04/round-1/minimax-m31flash.md`。报告必须包含：

1. 实际任务来源与 task ID、创建/完整正文接收时间、实际 provider/model/思考和权限模式读回（无法读回就明确无法验证）、lease/实际 workspace 映射与来源 hash。
2. base/product/process、实际路径/分支/HEAD、完整 diff 与全部 33 项来源核验、支持证据和提示 hash、审查前后冻结源码一致性；不能仅凭目录名或 manifest 自述。
3. 完整审查的文件/范围和原 PRD/阶段边界，实际读取/命令及结果；本轮未执行产品复测必须明确，已有验证按其原候选/真实日期范围引用，不伪造运行。
4. 每个发现的严重度、实际文件及行号、具体触发、影响、可核对证据和修复建议；无发现也说清实际范围，不能用“测试绿”代替源码审查。未验项和不能判断之处单列。
5. 上述 R1-01/R1-02/R5-01..04/R6-01/同版本终态/同数量反例/总控归档 R1 逐项复核结论和依据；你可以独立发现回归，不能将开发者已写 closed 当自己的结论。
6. 对本固定完整 S1 给出明确“通过 / 不通过 / 无法验证”，并明确完整父功能未完成。自身结论不代判另一方，也不授权 push/PR/merge。

报告写完不等于任务终态。正常完成本指定任务，让操作者从官方状态读回 terminal、完整全文报告和实际设置。若认证、额度、模型、路径或源漂移阻断，保留官方错误/任务句柄/已运行内容和准确恢复条件，报告“无法验证”或“不通过”而非伪造成功；不重试创建第二任务、不换模型或接口。若产物/测试/依赖/配置/验收/base 发生变化，本轮不得继续沿用旧结论，交开发线新候选和必要验证/双方新完整审查。

## 完整原政策（冻结摘自共同指令，无新增外发/桌面授权）

## 原第九节及无桌面打扰约束全文

以下按原目标文件及最新AGENTS原文附带；该操作政策补充不重建Goal、不改冻结实现或已归档输入，也不单因此重开产品审查。

九、效率优先、额度恢复与持续执行（2026-10-20 用户更新）

本节与最新 AGENTS/scope 一起适用于总控、现有功能 Goal、后续开发会话及模块子任务；与旧提示词统一串行、额度不足一律停止后项的文字冲突时，以本节为准。用户表示 ZCode、Codex、MiniMax Code 均仍有额外重置次数；这属于用户提供的权益信息，实际余额、可用次数和恢复结果须在执行时核实，不假定无限额度。

1. **开发效率优先。** 不以节省 token 为目标压缩需求、实现、异常处理、必要上下文或验证；以正确交付和缩短关键路径为目标。充分利用实际可用的 agent 并发槽、独立 worktree 与 feature 分支，尽早开展不依赖尚未就绪接口的设计、真实探针和独立模块。不是为提高 token 消耗而重复探索、无变化重测、无效轮询或新增无关范围；普通任务不强设三轮。
2. **保留指定模型与门禁。** ZCode 的 GLM-5.3/最高思考、MiniMax Code 的 M3.1-Flash/xhigh 继续适用；Codex 保持任务既有设置，按复杂度和已授权工具能力分配 agent，不因节省额度擅自降级或更换模型。独立审查、冻结候选、原验收、双模型通过、CI 与远端核验要求均不变。
3. **额度受限先恢复。** 出现实际额度告警或明确 rate/usage-limit 错误时，先区分额度耗尽、短时限速、服务故障、账单异常和认证错误，保存 base/head、任务标识、报告与已运行证据。由总控指定每个平台/账号唯一额度负责人，查询当前额度、可用重置权益及恢复条件；不要让多个并行任务同时消费同一权益或重复充值。
4. **已有权益优先自动使用。** 用户已授权在平台及工具允许的范围内，额度受限时使用该账号已有的额外重置次数、已购余额或已配置的官方恢复能力，尽快继续原任务。仅调用实际可用、经核验的官方入口；无需逐次确认且无额外新增支付时可自动执行。若工具或平台要求该次确认，则按该要求办理；若只有会占用用户桌面的 UI 入口，先保存状态，等待隔离环境或用户明确给出的可用时段。不得绕过确认、支付验证或无桌面打扰约束。
5. **Codex 的具体限制。** 优先使用 `get_usage_limits` 查询；当前 `consume_usage_reset` 工具仅在五小时或周额度剩余不高于 10% 时尝试兑换已有重置，并硬性要求每次使用都取得用户对该次操作的明确确认。本节的未来批量授权不能替代该次确认。确认后每个逻辑尝试使用唯一 `idempotencyKey`，不确定结果重试必须复用原 key；`reset`/`alreadyRedeemed` 均表示该尝试已完成，不能再次消费；`noCredit`/`nothingToReset` 不得记为成功。使用后查询实际额度，区分兑换完成与额度刷新失败，不直接重复兑换。
6. **ZCode / MiniMax Code 的机制核实。** 两者的额外重置次数由用户说明，目前未在本任务中核验可调用的恢复接口或实际余额。遇限时由对应开发线核实官方状态与入口，满足第 4 条才自动使用；没有支持的方式时如实记录缺少条件。不得猜测私有接口、索取或打印凭据、自动点击未知付款按钮，亦不得声称已配置三平台无人值守充值。
7. **重置与新增付费充值分开。** 优先消费已有权益。本次用户未给出新增付款的单次金额、累计上限或套餐选项；“不考虑 token”不是无限额新增付款授权。确需新增支出时，先查明实际可选方案与费用，在交易前明确并确认单次金额及累计上限；已有明确金额授权可按其范围执行，平台/支付工具要求逐次确认时仍遵守。不得通过擅自切换付费 API、订阅升级或其他账号绕过额度门禁。
8. **恢复后续跑、受限时不停无关工作。** 以平台实际确认及额度读回验证恢复结果，再续接原任务与同一候选，不无故新建 Goal、丢弃报告或重跑不变的验证。等待确认、自然恢复或隔离环境时，继续其他已授权且不受限的开发线；保存准确恢复条件，不无限重试。持续到目标达成，但遵守实际工具/系统预算；不能用本节绕过硬限制、伪造自动续跑或将未完成标记完成。
9. **记录和透传。** 记录平台/账号的不敏感标识、实际额度来源、受限类型、已有权益、该次授权、幂等尝试标识、操作结果和复查结果；不记录凭据或付款敏感信息。总控统一更新状态，新任务提示词必须附本节与无桌面打扰约束；进行中任务在安全边界读取并执行，不改写已归档的冻结输入，不仅因调度/额度政策变化重开产品审查。文档更新不等于运行中 Goal 自动生效，必须向总控及各开发线实际传达并记录接收状态。

### 本地验证默认不打扰用户（2026-10-20 用户确认）

- 本机默认只运行不打开窗口的静态检查、单元测试、引擎测试及构建/打包命令；打包完成不自动启动产物。上表的桌面 e2e 要求保留，但当前 `npm run test:e2e` 会启动 Electron，必须遵守本节的运行位置限制，不能作为本机每轮默认命令执行。
- 浏览器测试优先 headless；Electron 的原生窗口、可见性、焦点、无响应与恢复验收优先放在远程 CI、虚拟显示或独立测试桌面。`headless` 配置不能保证 Electron 无窗口；不得用隐藏/最小化窗口、禁用 hang monitor 或 stub 原生提示来冒充完整原生验收。
- 不得自动在用户当前桌面启动、显示、聚焦或反复重建测试窗口；禁止通过 `app.focus({ steal: true })`、`window.focus()`、`Raise`、自动点击或切应用占用用户正在使用的桌面。此约束也适用于 ZCode/MiniMax 等审查应用操作。必须使用当前桌面的验证，先汇总不可替代的待验项，等待用户明确提供可用测试时段；不能因用户未回复而自动重试。
- 无法静默完成的验证保留为“待隔离环境/桌面验证”，继续其余工作；不得记为通过、降低原验收或因等待擅自暂停/完成整个 Goal。既有证据仅在候选、环境和原验收范围匹配时引用，缺失部分在隔离环境补齐。
- 启动任务及派发独立审查时须一并传递本节约束；进行中任务在下一个安全边界停止新增本机 GUI 操作，撤回已排队的本机 e2e/native/HMR 桌面命令。有正在循环重建窗口的自有测试进程时，由所属开发线核对 PID、命令和任务归属后有界清理，记录中断而非通过；禁止宽泛结束 Electron、浏览器、审查应用或用户进程。

### ZCode / MiniMax Code 默认执行权限（2026-10-21 用户确认）

- 用户明确要求“更新调用zcode和minimax code的权限，默认为完全访问和始终授权”。ZCode 默认完全访问（permission.mode=yolo），MiniMax Code 默认始终授权/Full access（permissionMode=bypassPermissions）。创建或进入审查任务时读回该任务实际模式；用户级配置不能证明已有会话即时切换。已获授权，不重复询问默认模式。
- 当前计算、Goal和冻结审查不重启；在应用支持的安全边界确认或调整权限。完全访问不改变审查只读职责：仅运行约定验证、写独立报告，不修改实现/测试/依赖/配置，不提交、推送或切分支。
- 指定模型与思考等级、同版双审、意见处理、CI、远端核验及无桌面打扰约束继续适用；不扩大为新增付费、读取密钥、绕过平台逐次确认或占用用户工作桌面。
- 详见仓库外 `../iteration-control/2026-10-21-weekly-release/external-review-permissions.md`（worktree中从本体根目录定位）；新任务附上本节，旧冻结输入保留，单纯操作政策更新不触发无变化实现重审。


2026-10-21单文件补充生效：在既有T01十二共享及storage责任之外，`packages/engine/src/ontolearn_engine/worker.py`未来维护唯一交T01；只从批准5f的9314B/2fa848aa…06f2f0施工，不复制消费I05未批准C3的13638B/3d934e79…4f99d语义worker。原I05 C3受审字节继续冻结；若审查需修先由root精确返还、T01停写保存SHA/差异，执行输入变重新验证/双新审。protocol/resources/语义模块/旧tests/build/CI等不随此转，其他owners不变；source wire/限额/格式3/ready并未获批。原offer/接收/独立复核与唯一责任/返还门见本目录I05-T01-worker-ownership-handoff.md及execution-state.json。此补充不改变前文完整第九节/无桌面规则。


## 四文件基础层未来维护交接生效（2026-10-21T11:40:05.102755+08:00）

I05原owner分别释放并由T01逐项明确接收 apps/desktop/src/main/jsonl.ts、apps/desktop/src/renderer/src/task-presentation.ts；I06原owner仅释放并由T01逐项明确接收 apps/desktop/src/main/task-service.ts、apps/desktop/src/main/index.ts。独立复核eeb221ea…0562、原接收01fa5ce5…2731/2124ef6c…3fae均由总控全文读回，四接收路径实际clean且逐字等批准develop5f；生效登记见 foundation-four-file-handoff-effective.json，原协议bad9716a…2965及全部原件保全。自此四路径唯一未来维护者T01，原I05/I06停止所有checkout未来逻辑编辑，固定C4/e2c/961只读审查/构建保留。T01仅沿自己批准5f，不复制未批gateway/语义实现；I06保留preload/index.ts、renderer/src/env.d.ts、App.tsx、style.css及私有模块。其余协议/resources/旧tests/依赖/build/CI/语义路径不转移。

此项仅维护责任生效；当前纯表材料阶段授权不变，startup/schema/新码/runtime3/ready仍须总控精确阶段授权。返还任一路径须root精确路径/原因/基线/窗口/验证、T01先停写并保全HEAD/文件SHA/WIP diff/测试状态，再明确唯一接手者和生效点；旧owner不得自动回收。受审执行输入变化仍新候选/必要验证/指定双方全新完整审查，不继承旧Pass。原第九节、无桌面干扰、安全应用入口/实际租约、指定双审及push/PR/CI/正常合并门全部保留；历史文字不覆盖本新生效责任。
````
<!-- END ORIGINAL FROZEN PROMPT -->

## 当前执行补充全文

原字节 6215B，SHA `a6cf1335042a6e25d4ab0f67b27978c346c13cd82e59f355d302e1ec80681d3e`。当前操作遵守本轮执行补充，旧冻结静默或只读运行限制不覆盖当前政策。

<!-- BEGIN current-execution-supplement.md -->
````text
# T04-S1 指定审查当前执行补充

2026-10-22。来源为总控聊天 `01a154de-843b-7a00-8a80-51ba1c0aebce` 本轮实际 setup 通知：原 T04 是两个独立 review 树的唯一 setup owner；本补充只改变审查运行与输出边界，不改变产品、测试、依赖、验收或 base。它不是 T04 GUI lease、任务创建、指定通过或 Goal 恢复。

## 优先关系

旧 `round-1` 两份原始完整 prompt、manifest、AGENTS/common/后台路线快照保留原字节，属于历史输入。新投递正文必须完整包含原 prompt 和完整 S1 范围，并附精确 workspace 映射与当前 AGENTS/common/桌面政策、本补充。实际执行以新正文的映射和本补充为准：替代旧 prompt 的“任何验证即使有新风险也只能申请”“只能写单一报告文件”“禁止当前桌面/必须后台或独立桌面”等过时操作限制。审查范围、模型、原需求与质量门不得缩小。

## 独立环境与允许验证

- 两审者各使用自己实际登记的独立 detached review 树、node_modules、.venv、构建/cache/tmp、反例、raw 和报告。只能读取本方完整输入和共同原件，不读取另一方本轮 prompt、反例、日志、报告或意见。不得共享可变运行目录、结果库或审查结论。
- 原 T04 setup owner 可按原锁独立 `npm ci --ignore-scripts --no-audit --no-fund` 与 `uv sync --frozen` 备环境；安装本身不算产品验证，不自动运行 build/test/Electron。两环境已备好，审者不得为安装/修环境改源、锁、依赖或全局认证；依赖缺失保留真实错误，交唯一 setup owner 处理。
- 两指定审者可自主进行与固定候选对应、为其独立判断所必要的普通静态检查、单元测试、SSR、check/build 及普通受控测试 worker 回归，不需因旧过宽限制再次请求这些普通验证。先静态读取准确 script/config/测试文件及其子入口，核清 cwd、输入、输出、资源和进程归属后运行。不机械重跑所有不变历史；若其独立判断需要正常完整 check，可运行并保留真实结果。
- 准确的候选入口包括 `npm run lint`、`npm run format:check`、`npm run typecheck`、`npm test -- tests/unit/t04-query-authoring.test.ts tests/unit/t04-query-results.test.ts tests/unit/t04-query-reader.test.ts`、`node docs/iterations/T04/ssr-probe.mjs`、`uv run --frozen pytest packages/engine/tests/test_query_service_authoring.py packages/engine/tests/test_query_service_approved_baseline.py -q`、`npm run check`、`npm run build`，以及静态核过的普通原有测试 worker 回归，例如 `uv run --frozen pytest packages/engine/tests/test_worker_parent.py -q`。这是普通验证运行面，不证明所有入口已由本次 setup 执行。
- `npm run check` 的准确链为 lint → format:check → typecheck → vitest → build → engine:check（ruff/format-check/pytest）；vitest 配置仅含 `tests/unit/**/*.test.ts`，desktop build 是 `electron-vite build`。这些名称本身不是安全证明，审者仍需检查其实际子入口。`npm run dev`、HMR、`test:e2e`、`package:dir`、自动启动 Electron/产物及新的 native/caller/producer 不在本次普通 S1 验证运行面，不能借通用桌面授权自行扩成新验收。
- 可在本方 ignored `test-results/t04-review-runtime/<role>/` 写独占反例、raw、运行收据、缓存、临时数据；也可由正常 check/build 写本方原有 ignored out/dist/build、.pytest_cache、.ruff_cache、__pycache__ 等常规产物。最终报告只写映射明确的本方 `docs/reviews/T04/round-1/<model>.md`。反例不能写进源或原测试目录，不能改变验收真值，也不能成为第二执行器/Store/公共 schema。
- 每次实际运行记录完整 argv、cwd、起止时间、真实 exit code/超时/信号、完整 stdout/stderr 原件与哈希，保留首失败及后续结果。禁止 skip/xfail、删除或削弱断言、改输入真值、失败后筛掉失败项冒充整套通过。精确路径定向验证可做，但必须说明它的范围，不能冒充完整 check。只清理本方已核 PID/进程树，不宽泛结束用户/其他任务进程。

## 仍禁止的研究与修改

源码、原测试、配置、锁、Git 状态/提交/分支、冻结旧输入、原验收和其他报告全部只读；AGENTS 仅由阶段主聊天传播为保护 M，审者不格式化、覆盖或提交。不得 `git add/commit/push/reset/checkout`、修改共享契约、写第二可变源或消费未批准实现。

已被拒绝的 SQLite 损坏/heap/OS 研究、SQLite 损坏 HOLD、未签运行票、new native/caller/producer、外部 API/新增付费和密钥读取/搬运继续禁止。普通受控 worker 测试不扩张为新破坏性研究；必要的临时测试库只在该测试自己的 tmp 路径，不能触及用户或其他任务数据。若精确入口实际包含被 HOLD/拒绝的工作，不擅自排除后宣称整套通过，报告该入口未运行/阻断及对应原授权边界。

当前 S1 无 App 正式接线，审者可用独占反例证明其实际缺口；标准库/合成 transport/SSR/普通 worker 不能冒充真实业务 IPC、Store 保存、query.execute、平台、真人或完整父功能验收。

## 桌面、模型与终态

人类已撤回静默桌面要求；已授权 computer use 不再需要用户桌面时段、独立桌面或 CLI 登录前置。原功能 owner 只在总控内部短 lease 中操作审查应用创建、设置和核验；后台推理不占整个桌面时段。本线当前尚未获得 GUI lease，不能启动 T04 任务或抢 T01/T06 资源；这不阻止当前静态输入和环境准备。

ZCode 固定 GLM-5.3/最高 max/yolo，MiniMax 固定 M3.1-Flash/xhigh/bypassPermissions。每方本轮新完整独立任务，同一 base/product，逐任务实际 provider/model/可用等级/思考/权限/工作区读回。无设置/任务 ID 时不能假填。完整终态、全文报告、所有意见处置、同版双方明确通过及原验收、push/PR attach/实际 CI/正常 merge/远端门保留。不得拿安装完成、目录存在、旧内审或另一方意见当本方指定通过。
````
<!-- END current-execution-supplement.md -->

## 当前 AGENTS 全文

原字节 15147B，SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。当前操作遵守本轮执行补充，旧冻结静默或只读运行限制不覆盖当前政策。

<!-- BEGIN current-agents.txt -->
````text
# OntoLearn Studio Agent 指南

默认中文，结论先行，简洁。先读需求依据再动手；不确定就问，不猜产品决定。

## 1. 先读什么

| 场景              | 必读                                                                                                                                                                                                                 |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 任何业务语义改动  | [PRD V0.6](docs/prd/PRD-本体学习与落地Agent工作台.md) 对应 FR 条款 + 附录 C/D/E/G                                                                                                                                    |
| 工程/架构改动     | [M0 更新计划](docs/architecture/m0-review-and-update-plan-2026-10-19.md)（S1/S2/S3/C1/B1/U1 验收全文）、[ADR-0001](docs/architecture/0001-desktop-framework.md)、[ADR-0002](docs/iterations/I01/ADR-0002-storage.md) |
| 当前状态与待办    | [M0 清单](docs/m0-checklist.md)；进行中迭代见 `docs/reviews/Ixx/status.md`                                                                                                                                           |
| 迭代 I01–I06 执行 | 仓库外总控 `../iteration-control/2026-10-19/scope.md` 与 `state.json`                                                                                                                                                |

状态快照（2026-10-20，以上述文件为准）：I01/S1 存储 spike 已合并 develop；I02/C1 CSP 与窗口恢复处于 CI 修复门禁；I03–I06 未开始。产品正式能力仍只有 health；存储是 Python 内部 API，未暴露给 IPC、UI 或 Agent。禁止把占位界面、测试替身或 spike 说成已实现的产品能力。

## 2. 仓库地图

```text
apps/desktop/src/main/      Electron 主进程：窗口安全、来源校验、引擎监督、恢复
apps/desktop/src/preload/   唯一桥接（按业务命名的方法）
apps/desktop/src/renderer/  React UI（无 Node 能力）
apps/desktop/src/csp.ts     CSP 唯一配置源（生产 meta / 开发 header 两个变体）
packages/contracts/         TS 边界类型与 zod 运行时校验
packages/engine/            Python stdio 引擎：protocol.py、storage.py、invalidation-v2.json
tests/unit, tests/e2e       vitest 单测；Playwright 驱动真实 Electron
docs/iterations/Ixx/        迭代设计、验收、证据；docs/reviews/Ixx/ 评审与流程记录
```

## 3. 架构不变量（违反即阻断）

- **本地优先**：不自动启用模型、遥测或云服务；不开 HTTP 端口；不引入云数据库或未经测量的图数据库。
- **渲染端隔离**：renderer 不得直接使用 Node、文件系统、shell 或通用 IPC；preload 只暴露按业务命名的方法，禁止 `invoke(method, params)` 式通道。IPC 处理器保持 sender/mainFrame/可信文档校验。
- **CSP**：只改 `csp.ts` 一处；生产脚本不得出现 `unsafe-inline`/`unsafe-eval`；不手写第三份策略。
- **确定性与 Agent 解耦**：确定性结果只能来自真实引擎；Agent 只产出草稿并调用白名单工具，不得自动确认自己的修改。
- **存储**：SQLite 是唯一可变源真相，正式写入只经 `Store.commit`（版本化、可预览、原子提交、旧基线拒绝）；RDFLib 图只从不可变快照重建，不能写回。
- **数据层次**：本体定义、断言事实、当前推导、场景副本、历史运行分层；历史与已提交轮次不可改写，缓存回收不得触及历史。
- **失效规则**：`staleReason` 只来自 `invalidation-v2.json`；仅改模型配置不使领域结果过期；历史/失败/取消不计为过期原因。
- **模型外发**（S3 前不得接入）：唯一网关在主进程，凭据只在主进程；Python 引擎不持有密钥，也不调用模型。
- **错误**：跨边界只传固定错误码和受限参数，不回传原始异常、堆栈、路径、单元格原值或凭据。

## 4. 改动类型 → 必跑验证

| 改动                                       | 命令                                                               |
| ------------------------------------------ | ------------------------------------------------------------------ |
| 任意代码或配置                             | `npm run check`（lint/格式/类型/vitest/构建/ruff/pytest）          |
| 涉及归档资料或 `docs/source-manifest.json` | `npm run verify:sources`                                           |
| 主进程、preload、bridge、CSP、窗口         | 另跑 `npm run test:e2e`（Linux 用 `xvfb-run -a`）                  |
| 引擎依赖、打包配置                         | 另跑 `npm run package:dir`，并在包内运行同一样例                   |
| 仅文档                                     | `npx prettier --check <文件>`；不批量格式化归档 PRD、审查和 `.pen` |

`I02_HMR=1` 的 HMR 探针会临时改写源文件，评审冻结期间禁止运行。结果须分开报告静态、运行、打包、生产四类证据，不以静态检查代替运行证据。

### 桌面工具与本地验证（2026-10-22 用户更新）

- 用户明确要求“直接使用 computer use 调用桌面端的工具，删除之前要求的静默桌面操作”。此前静默、不占用当前桌面、禁止聚焦或自动点击、须先取得桌面时段的偏好已撤回，不再作为现行限制。
- 已授权任务可按需直接使用 computer use 操作 ZCode、MiniMax Code 等桌面工具，也可运行本机浏览器、Electron、原生窗口与恢复验收；不为常规桌面操作重复询问或把后台、headless、隔离桌面作为前置。
- 多条开发线操作同一桌面应用或使用互斥测试资源时，由总控内部协调，避免互相改动任务或干扰测试；无需额外向用户预约桌面时段。清理进程仍须核对自有 PID 和任务归属，不得宽泛结束用户或其他任务的进程。
- 验证仍须覆盖原验收条件，区分静态、运行、打包与生产证据；不得用隐藏窗口、禁用 hang monitor 或 stub 原生提示冒充真实原生验收。操作政策更新不改变冻结候选、指定双审与发布门禁。

## 5. 分支、迭代与评审门禁

- **并行开发为默认执行要求（2026-10-20 用户确认）**：适用于当前 M0、后续里程碑、不同功能模块，以及单个模块内可独立开发的具体子任务。先识别真实接口、数据和集成依赖；可独立验收的工作须拆分并行推进，不得仅因迭代编号或模块顺序而全量串行。强依赖保留前置条件，不为增加并行数而重复实现或提前假定未冻结契约。
- **独立 worktree + feature 分支**：每条并行开发线使用自己的 Git worktree、feature 分支和负责 agent，禁止多个开发 agent 在同一 checkout 切分支或同时写文件。迭代使用 `feature/Ixx-<主题>`，模块子任务使用 `feature/<模块>-<子任务>`；其他改动使用 `feat/`、`fix/`、`docs/`、`chore/`。从核验过的 `develop` 提交切出并记录 base SHA，经 PR 合回；不强推共享分支。提交前缀使用 `feat:`、`fix:`、`docs:`、`test:`、`chore:`。
- **拆分与文件责任**：启动前记录各子任务的范围、前置依赖、接口约定、文件负责人、验收和集成顺序，再分配独立 agent。共享契约、存储迁移、能力注册表、依赖清单与锁文件指定唯一维护者；其他开发线提出接口需求，由维护者统一修改。依赖尚未就绪时，可先做独立设计、纯模块、真实库探针及对应测试，后置正式接线与联验；替身通过不得计作集成完成。
- **M0 的并行拆分**：I02 继续当前候选评审；I03 可基于已完成的 I01 并行设计；I05 可先做真实候选语义、外联拒绝、依赖与打包验证；I06 可先做网关 ADR、独立授权与凭据模块。I04 实施须等待 I03 同版本设计审查通过并合并；I05/I06 的正式接入及最终验收须等待各自实际依赖就绪，并补齐与存储、任务和窗口生命周期的联验。引入真实依赖时即做相应打包验证，不全部推迟到最终集成。
- **运行资源隔离**：各 worktree 独立依赖环境、构建输出、临时数据、日志及测试证据，开发端口和应用测试数据目录分别配置；不得共享可变运行库。桌面焦点、原生故障恢复、系统凭据存储及外部审查应用的 UI 操作由总控内部协调串行使用，避免运行互扰，不以向用户申请桌面时段为前置；已有固定端口或未隔离资源的测试须排队。
- **并行开发、按依赖串行集成**：每条开发线独立验证并履行现行评审门禁；合并前同步目标基线、处理冲突并验证实际集成结果。目标基线或受审内容变化时，按现行规则重新验证及独立审查，不沿用旧版本通过。保留双指定模型、CI 和远端核验要求；子任务完成不等于父模块或里程碑验收完成。
- **冻结与调度记录**：候选冻结后不得修改受审路径，任何实现、测试、配置、依赖或验收改动都要生成新候选，并按现行门禁重新独立审查。其他工作在独立 worktree 推进，不干扰冻结候选。总控记录并行任务、worktree/分支、base/head、文件责任、依赖和资源预约；仅按实际进展更新状态，不把获准并行登记为已启动或完成。
- **与旧计划的关系**：本节取代旧 `scope.md` 中“所有迭代必须前项合并后才启动后项”的统一串行调度要求；执行时总控须同步相关范围与调度记录，保留原需求、真实技术依赖、验收及评审门禁。后续功能模块和子任务同样执行本节，无需为常规并行拆分重复征求授权。
- **进行中开发与 Goal 的过渡**：按最新桌面操作政策执行；并行策略在安全边界用于新任务/新开发线，不强行迁移正在冻结审查的 checkout、不改写其候选、不重建已有 Goal、不丢弃报告或重跑无变化的验证。用户授权的 AGENTS/调度文档变化单独记录前后哈希与适用范围；若未改变受审实现、测试、依赖、CI、验收或集成基线，不将其误判为受审产品变更，不单因此重开整轮审查。若实际受审内容或基线确有变化，仍执行原重新审查规则。审查代码读取固定 SHA，实际执行遵守最新操作约束。新 worktree 须携带并核对最新指南，不能只读取旧基线中的 AGENTS；总控负责同步规则，开发会话各自维护状态，避免共同改写 `state.json`。
- 不混入其他会话的未提交改动；禁止 `git add -A` 或整体 stage。只 stage 本任务文件。
- 复杂或高风险交付使用独立 agent 审查，避免并发修改共享契约文件；不得替换指定审查模型或降低门禁。

### 效率与额度恢复（2026-10-20 用户确认）

- 以正确交付和开发效率为优先，不因 token 消耗缩减实现、异常处理、上下文或必要验证。充分使用实际可用的并行 agent/worktree；避免重复探索、无变化重测和无效轮询，不擅自更换指定模型或降低审查门禁。
- 用户说明 ZCode、Codex、MiniMax Code 均有额外重置次数；遇实际额度限制时由账号唯一负责人核实状态，优先通过经核验的官方方式使用已有权益恢复，成功后续接原任务。其他开发线保存现场并继续无关工作，不重复消费同一权益；短时限速、服务/认证/账单故障不能当作额度耗尽盲目充值。
- 自动恢复受实际工具/平台约束：Codex `consume_usage_reset` 每次必须取得用户对该次操作的明确确认，未来批量授权不能替代；只在工具的额度条件满足时使用，同次不确定重试复用幂等 key，完成后核验额度，不因刷新失败重复消费。ZCode/MiniMax Code 的可用恢复机制尚待核实，不虚称已实现无人值守充值；禁止通过 UI 绕过工具确认。
- 已有重置/余额与新增付费分开：本次未提供新增付款的单次金额及累计上限，实际购买前须明确这些条件及授权；不将“不考虑 token”扩大为无限付款、自动订阅升级或切换付费 API。完整执行与透传规则见仓库外 `../iteration-control/2026-10-19/goal-objective.md` 第九节；运行中 Goal 须实际同步，旧冻结输入保留。

## 6. 文档与证据规范

- **唯一状态来源**：完成度只在 `docs/m0-checklist.md` 和对应 `status.md` 中维护；其他文档链接过去，不重复“不代表 M0 完成”之类的声明。
- ADR 采用后放到 `docs/architecture/000N-<主题>.md`；迭代目录只保留设计、验收和证据。
- 证据只提交摘要、关键 JSON 和哈希；大段原始日志、截图、runtime dump 优先放 CI artifact。确需入库时写明理由。
- 文档写决定、理由、未决项，每份 ADR 控制在 1–2 屏；不编造性能数字、容量通过线、日期或人员承诺。
- 不提交凭据、业务数据、`.sqlite`/`.db` 运行库、`.env`、`.mimosa/`。

## 7. 编码约定

- TypeScript `strict`；边界数据一律经 zod `.strict()` 解析。Python 3.12 + ruff（line-length 100，E/F/I/UP/B）。
- JS 直接依赖写精确版本；npm 与 uv 两份锁文件随改动一起提交，CI 使用 `npm ci` 和 `uv sync --frozen`。
- 测试断言真实需求和错误边界（完整预期集合/顺序），不只断言数量或按钮可点击。
- 不设 PRD Q2/Q3/Q5/Q6/Q7/Q8/Q9 的默认答案；遇到这些决定时停下来询问。

### ZCode / MiniMax Code 默认执行权限（2026-10-21 用户确认）

- 用户明确要求“更新调用zcode和minimax code的权限，默认为完全访问和始终授权”。ZCode 默认完全访问（permission.mode=yolo），MiniMax Code 默认始终授权/Full access（permissionMode=bypassPermissions）。创建或进入审查任务时读回该任务实际模式；用户级配置不能证明已有会话即时切换。已获授权，不重复询问默认模式。
- 当前计算、Goal和冻结审查不重启；在应用支持的安全边界确认或调整权限。完全访问不改变审查只读职责：仅运行约定验证、写独立报告，不修改实现/测试/依赖/配置，不提交、推送或切分支。
- 指定模型与思考等级、同版双审、意见处理、CI 和远端核验继续适用；桌面操作按本指南最新政策执行，不扩大为新增付费、读取密钥或绕过平台逐次确认。
- 详见仓库外 `../iteration-control/2026-10-21-weekly-release/external-review-permissions.md`（worktree中从本体根目录定位）；新任务附上本节，旧冻结输入保留，单纯操作政策更新不触发无变化实现重审。
````
<!-- END current-agents.txt -->

## 当前共同指南全文

原字节 16867B，SHA `567b6e7064bf123dac46742aefa57e06f6ed2fe87ceec5225c395049be888fc1`。当前操作遵守本轮执行补充，旧冻结静默或只读运行限制不覆盖当前政策。

<!-- BEGIN current-common.txt -->
````text
# 完整首版功能开发共同指令

用户已在规划聊天 `01a15bad-ceeb-7103-b611-fff95e1f31ee` 明确要求 OntoLearn-Studio 全部原定首版功能于北京时间2026-10-25前开发上线、质量不降，并授权“发送并落实到现有总控”。总控实际读取原始用户消息确认了授权。本指令用于新功能开发聊天；截止日是目标，不是保质按期保证。

先读取本目录 controller-handoff.md、plan.md、tasks.json 中自己的任务、requirements.csv、acceptance-baselines.csv、review.md，以及实际工作树最新版AGENTS和对应PRD原条款/附录。57项P0、附录C–G及第10–12节保留；P1/P2原延期安排不变。T编号不覆盖I01–I06历史；纯服务完成不等于父模块P0完成，integration_prerequisites不是全部验收条件。

本会话只负责指定的一项功能，建立自己的Goal（不存在时），不继承总控Goal。先核验并回执绝对worktree、分支、base、实际git状态、指南SHA、唯一文件责任、验收与下一交付。总控已创建独立worktree，切勿改主checkout或其他树；AGENTS是总控复制的受保护操作规则，SHA应为 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，保持未暂存，不混入产品提交。不得重建原I05/I06 Goal或继续写其树。

当前批准develop为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。I01–I04已合并；I05 C1在指定双审冻结，已发现词法语义阻断，I06在自己的14文件接线与隔离平台联验。不得采用未批准I05/I06实现、环境或测试结果为正式依赖。只读取已批准基线接口开展独立工作，具体接口缺口/共享改动向总控提供精确路径和依据。

初始共享责任（历史，已被下述逐项生效交接更新）：I06原独占 contracts/src/{index.ts,v2.ts}、contracts/v2/{schema,registry,errors,fixtures,binding-regressions}.json，desktop/main/{index.ts,task-service.ts,engine.ts}、preload/index.ts、renderer/src/{env.d.ts,App.tsx,style.css}；I05原保留其他Python Store/coordinator/worker/protocol、语义/resources、entrypoint/build/锁/CI/窗口安全恢复。这些逻辑文件在任何树中均不得抢写。新增私有路径可按本任务授权实施；现有共享文件、迁移和依赖锁一律先做具体交接。不得复制第二套公共契约、SQLite可变权威或Store写入通道来绕过交接。子任务独立worktree/feature和文件责任，复杂交付独立agent审查；核验真实并发槽，不将创建目录当作已启动agent。

后续责任变更补充：I05/T01双方实际接受、独立复核及总控登记后，只有 `packages/engine/src/ontolearn_engine/storage.py` 后续维护已交T01生效，详见 I05-T01-storage-ownership-handoff.md 和 execution-state.json。I05冻结树保持原字节，其余共享/14文件不变。不得将这个单文件交接扩张为其他文件授权；当前具体责任以总控实际生效记录为准。

2026-10-21新增已生效交接：T01除原storage.py外，已唯一接管Python四个 `packages/engine/src/ontolearn_engine/{job_store.py,coordinator.py,__main__.py}`、`packages/contracts/python/contract_v2.py`，及原I06 canonical七个 `packages/contracts/src/{index.ts,v2.ts}`、`packages/contracts/v2/{schema,registry,errors,fixtures,binding-regressions}.json` 和 `apps/desktop/src/main/engine.ts`，仅从批准5f独立实施格式基础。T03已唯一接管 `packages/engine/pyproject.toml`、`uv.lock`、`scripts/build-engine.mjs`、`packages/engine/entrypoint.py`，仅做XLSX最小依赖/收集/受限probe。原I05/I06树原字节保留，可读/构建但不得继续维护已交逻辑文件；必要修复先精确返还。I06仍维护其余六个main/index、task-service、preload/index、env.d.ts、App.tsx、style.css，I05仍维护其他未交路径；既有测试、CI、resources等不自动扩权。三份新handoff协议及独立报告/实际接受/生效通知见本目录 I05-T01-format3-ownership-handoff.md、I06-T01-format3-ownership-handoff.md、I05-T03-build-ownership-handoff.md 和execution-state.json；这不是未批准代码采用、公共格式启用或运行通过。

2026-10-22人类已撤回静默桌面、不占用/聚焦/点击限制及先预约用户时段的偏好。已授权任务可直接computer use操作桌面端及按原验收运行本机原生测试；互斥资源由总控内部协调，不把CLI认证/后台/headless/隔离桌面作为前置。具体阶段源码/写面/运行票/被拒工作边界不随政策扩大；指定双审、冻结、必要验证、CI/平台/真人/远端和付款逐次确认门保持。当前详细政策见 /Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/desktop-operation-policy-20261022.md。 桌面仅在创建/设置/读回阶段按execution-state当前短lease串行，原任务后台推理不独占整个应用；CUA对Codex app的工具拒绝仍不得绕过。

开发至完整可审查结果，必要异常路径/事务/撤销/历史隔离均保留。AGENTS所需 check/sources/e2e/package 按实际改动执行，隔离项真实待验，首跑失败原件保留。文档/纯模块/静态检查不能冒充正式接线或生产。没有变化不重复测试。依赖资源缺失只阻塞相关部分，先完成独立工作，不擅自结束或暂停整个Goal。

最终完整验收前刷新实际批准依赖及develop、集成冲突并验证；冻结真实base/head。由同一开发聊天通过CUA在ZCode选择本精确工作树、GLM-5.3/最高，MiniMax Code选择本精确工作树、M3.1-Flash/xhigh；每轮双方各新建独立只读完整范围任务，不互传本轮意见。报告按 docs/reviews/Txx/round-N/{zcode-glm53,minimax-m31flash}.md，逐项含任务来源/模型设置/路径分支/base/head/检查命令结果/未验边界/问题严重度位置触发影响证据建议/历史逐项关闭/明确通过或不通过或无法验证。两个任务必须实际终态，全文读回、全部意见处置；不能自己把指定模型不通过改成通过。所有实现/测试/配置/依赖/验收或基线变化后重新验证并双方全新完整审查。纯追加流程证据记录对应关系，不自动触发无变化重审。

同版双方明确通过、验收和必要验证通过、全部意见有处置、实际推送内容与受审实现一致后才push/PR；实际CI通过后正常合并develop、核验远端与保护源。必须attach创建PR；无强推、绕过分支保护或双审前push。集成/外审按总控预约，减少前方候选基线失效。纯服务可单独冻结合并，但原父任务P0跨模块验收与完整发布门不关闭。

额度：效率和完整交付优先，不因token删减；真实告警由账号唯一负责人核实。Codex重置每次需本人明确确认/阈值/幂等，不能UI绕过；不新增付费、订阅、API消费或扩张授权。只读服务/身份元数据不含读取或输出密钥。真人非开发用户验收不能agent替代，向外招募/消息仍需用户明确授权。

各线只维护自己的 docs/reviews/Txx/status.md 及证据，不写根 state.json、tasks.json 或其他总控文件。及时保留可恢复SHA/原件和准确下一步；实际独立实现与验收证据成熟后向总控给出可读交付，不用反复询问常规实施许可。不能将配置/脚本存在、目录/模型名称或数量相同当作验收。完成后父模块/远端/上线分别据实记录。

## 第九节与当前桌面操作政策

以下按原目标文件及最新AGENTS原文附带；该操作政策补充不重建Goal、不改冻结实现或已归档输入，也不单因此重开产品审查。

九、效率优先、额度恢复与持续执行（2026-10-20 用户更新）

本节与最新 AGENTS/scope 一起适用于总控、现有功能 Goal、后续开发会话及模块子任务；与旧提示词统一串行、额度不足一律停止后项的文字冲突时，以本节为准。用户表示 ZCode、Codex、MiniMax Code 均仍有额外重置次数；这属于用户提供的权益信息，实际余额、可用次数和恢复结果须在执行时核实，不假定无限额度。

1. **开发效率优先。** 不以节省 token 为目标压缩需求、实现、异常处理、必要上下文或验证；以正确交付和缩短关键路径为目标。充分利用实际可用的 agent 并发槽、独立 worktree 与 feature 分支，尽早开展不依赖尚未就绪接口的设计、真实探针和独立模块。不是为提高 token 消耗而重复探索、无变化重测、无效轮询或新增无关范围；普通任务不强设三轮。
2. **保留指定模型与门禁。** ZCode 的 GLM-5.3/最高思考、MiniMax Code 的 M3.1-Flash/xhigh 继续适用；Codex 保持任务既有设置，按复杂度和已授权工具能力分配 agent，不因节省额度擅自降级或更换模型。独立审查、冻结候选、原验收、双模型通过、CI 与远端核验要求均不变。
3. **额度受限先恢复。** 出现实际额度告警或明确 rate/usage-limit 错误时，先区分额度耗尽、短时限速、服务故障、账单异常和认证错误，保存 base/head、任务标识、报告与已运行证据。由总控指定每个平台/账号唯一额度负责人，查询当前额度、可用重置权益及恢复条件；不要让多个并行任务同时消费同一权益或重复充值。
4. **已有权益优先自动使用。** 用户已授权在平台及工具允许的范围内，额度受限时使用该账号已有的额外重置次数、已购余额或已配置的官方恢复能力，尽快继续原任务。仅调用实际可用、经核验的官方入口；无需逐次确认且无额外新增支付时可自动执行。若工具或平台要求该次确认，按该要求办理；如需UI由唯一资源owner依2026-10-22当前政策直接computer use，不等待额外用户桌面时段。不得绕过确认或支付验证。
5. **Codex 的具体限制。** 优先使用 `get_usage_limits` 查询；当前 `consume_usage_reset` 工具仅在五小时或周额度剩余不高于 10% 时尝试兑换已有重置，并硬性要求每次使用都取得用户对该次操作的明确确认。本节的未来批量授权不能替代该次确认。确认后每个逻辑尝试使用唯一 `idempotencyKey`，不确定结果重试必须复用原 key；`reset`/`alreadyRedeemed` 均表示该尝试已完成，不能再次消费；`noCredit`/`nothingToReset` 不得记为成功。使用后查询实际额度，区分兑换完成与额度刷新失败，不直接重复兑换。
6. **ZCode / MiniMax Code 的机制核实。** 两者的额外重置次数由用户说明，目前未在本任务中核验可调用的恢复接口或实际余额。遇限时由对应开发线核实官方状态与入口，满足第 4 条才自动使用；没有支持的方式时如实记录缺少条件。不得猜测私有接口、索取或打印凭据、自动点击未知付款按钮，亦不得声称已配置三平台无人值守充值。
7. **重置与新增付费充值分开。** 优先消费已有权益。本次用户未给出新增付款的单次金额、累计上限或套餐选项；“不考虑 token”不是无限额新增付款授权。确需新增支出时，先查明实际可选方案与费用，在交易前明确并确认单次金额及累计上限；已有明确金额授权可按其范围执行，平台/支付工具要求逐次确认时仍遵守。不得通过擅自切换付费 API、订阅升级或其他账号绕过额度门禁。
8. **恢复后续跑、受限时不停无关工作。** 以平台实际确认及额度读回验证恢复结果，再续接原任务与同一候选，不无故新建 Goal、丢弃报告或重跑不变的验证。等待确认、自然恢复或隔离环境时，继续其他已授权且不受限的开发线；保存准确恢复条件，不无限重试。持续到目标达成，但遵守实际工具/系统预算；不能用本节绕过硬限制、伪造自动续跑或将未完成标记完成。
9. **记录和透传。** 记录平台/账号的不敏感标识、实际额度来源、受限类型、已有权益、该次授权、幂等尝试标识、操作结果和复查结果；不记录凭据或付款敏感信息。总控统一更新状态，新任务提示词必须附本节与当前桌面政策；进行中任务在安全边界读取并执行，不改写已归档的冻结输入，不仅因调度/额度政策变化重开产品审查。文档更新不等于运行中 Goal 自动生效，必须向总控及各开发线实际传达并记录接收状态。

### 当前桌面操作政策（2026-10-22 用户撤回静默限制）

2026-10-22人类已撤回静默桌面、不占用/聚焦/点击限制及先预约用户时段的偏好。已授权任务可直接computer use操作桌面端及按原验收运行本机原生测试；互斥资源由总控内部协调，不把CLI认证/后台/headless/隔离桌面作为前置。具体阶段源码/写面/运行票/被拒工作边界不随政策扩大；指定双审、冻结、必要验证、CI/平台/真人/远端和付款逐次确认门保持。当前详细政策见 /Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/desktop-operation-policy-20261022.md。

### ZCode / MiniMax Code 默认执行权限（2026-10-21 用户确认）

- 用户明确要求“更新调用zcode和minimax code的权限，默认为完全访问和始终授权”。ZCode 默认完全访问（permission.mode=yolo），MiniMax Code 默认始终授权/Full access（permissionMode=bypassPermissions）。创建或进入审查任务时读回该任务实际模式；用户级配置不能证明已有会话即时切换。已获授权，不重复询问默认模式。
- 当前计算、Goal和冻结审查不重启；在应用支持的安全边界确认或调整权限。完全访问不改变审查只读职责：仅运行约定验证、写独立报告，不修改实现/测试/依赖/配置，不提交、推送或切分支。
- 指定模型与思考等级、同版双审、意见处理、CI和远端核验保持；桌面按2026-10-22当前政策执行，不扩大为新增付费、读取密钥或绕过平台逐次确认。
- 详见仓库外 `../iteration-control/2026-10-21-weekly-release/external-review-permissions.md`（worktree中从本体根目录定位）；新任务附上本节，旧冻结输入保留，单纯操作政策更新不触发无变化实现重审。

2026-10-21单文件补充生效：在既有T01十二共享及storage责任之外，`packages/engine/src/ontolearn_engine/worker.py`未来维护唯一交T01；只从批准5f的9314B/2fa848aa…06f2f0施工，不复制消费I05未批准C3的13638B/3d934e79…4f99d语义worker。原I05 C3受审字节继续冻结；若审查需修先由root精确返还、T01停写保存SHA/差异，执行输入变重新验证/双新审。protocol/resources/语义模块/旧tests/build/CI等不随此转，其他owners不变；source wire/限额/格式3/ready并未获批。原offer/接收/独立复核与唯一责任/返还门见本目录I05-T01-worker-ownership-handoff.md及execution-state.json。此补充不改变前文完整第九节/最新桌面规则。

## 四文件基础层未来维护交接生效（2026-10-21T11:40:05.102755+08:00）

I05原owner分别释放并由T01逐项明确接收 apps/desktop/src/main/jsonl.ts、apps/desktop/src/renderer/src/task-presentation.ts；I06原owner仅释放并由T01逐项明确接收 apps/desktop/src/main/task-service.ts、apps/desktop/src/main/index.ts。独立复核eeb221ea…0562、原接收01fa5ce5…2731/2124ef6c…3fae均由总控全文读回，四接收路径实际clean且逐字等批准develop5f；生效登记见 foundation-four-file-handoff-effective.json，原协议bad9716a…2965及全部原件保全。自此四路径唯一未来维护者T01，原I05/I06停止所有checkout未来逻辑编辑，固定C4/e2c/961只读审查/构建保留。T01仅沿自己批准5f，不复制未批gateway/语义实现；I06保留preload/index.ts、renderer/src/env.d.ts、App.tsx、style.css及私有模块。其余协议/resources/旧tests/依赖/build/CI/语义路径不转移。

此项仅维护责任生效；当前纯表材料阶段授权不变，startup/schema/新码/runtime3/ready仍须总控精确阶段授权。返还任一路径须root精确路径/原因/基线/窗口/验证、T01先停写并保全HEAD/文件SHA/WIP diff/测试状态，再明确唯一接手者和生效点；旧owner不得自动回收。受审执行输入变化仍新候选/必要验证/指定双方全新完整审查，不继承旧Pass。原第九节、最新桌面政策、安全应用入口/内部资源租约、指定双审及push/PR/CI/正常合并门全部保留；历史文字不覆盖本新生效责任。
````
<!-- END current-common.txt -->

## 当前桌面政策全文

原字节 3160B，SHA `2032bd9e1cdbf398a0d505e092e1a08b80ff15df26b1d06c7d7e1c2e0a5a8ec1`。当前操作遵守本轮执行补充，旧冻结静默或只读运行限制不覆盖当前政策。

<!-- BEGIN current-desktop-policy.txt -->
````text
# 当前桌面操作政策：撤回静默限制

总控已正式read_thread核验人类最新原文：“直接使用computer use调用桌面端的工具就行，删除我之前要求的静默桌面操作”。来源chat `01a1628e-1220-7fb1-9135-97cbea4a3ed5`，turn `01a162ce-e65a-7753-84ab-47db9975c1d3`，human message `01a162cf-5a30-7e13-95ee-24d468007ce5`。这条在“现在可以登录”答复之后，当前执行以其为准。

## 立即生效

- 撤回此前静默、不占当前桌面、禁止聚焦/点击、须先预约用户时段的偏好。已授权任务可直接computer use操作桌面端审查工具及按既有验收运行本机浏览器/Electron/native；不为常规桌面操作重复询问，不把CLI认证、后台、headless或隔离桌面作为前置。
- 同一桌面应用、原生故障测试与其他互斥资源由总控内部调度。本轮最先创建ZCode/MiniMax任务的负责人是原T06聊天 `01a15bba-0c8a-7dc2-b612-5b5c4ec4a4b9`；直接创建ZCode GLM-5.3/max/yolo完整新审，保留现有MiniMax真实session/turn/stream，不重复任务、不互泄本轮意见。其自有OAuth等待已实际收尾，不再给本人CLI登录前置。T06创建已完成并释放前台；后台任务保持，不独占整个应用推理时长。当前短时创建/核验lease以execution-state.json为准，
- 尚在排队的T02/T03/T04/T07/T09/T10/T11不自行抢同一桌面；总控按实际资源交接。内部协调不是向用户重新申请桌面时段。完整必要验证可以按任务授权执行，不以“静默不了”一律停工；原native/窗口验收条件保留，不用隐藏/stub/禁hang monitor代真实结果。
- 操作政策撤回不扩大具体阶段写面/运行权：纯文档、源码静态准备、未签native caller、尚未获运行票的构建/探针，以及已被自动审批拒绝的工作仍按各自原界限；不得把桌面可用当ABI/loader/drain、SQLite损坏HOLD/whole-H/owner或其他产品验收通过。
- 指定模型/思考/逐任务权限、同版双审、必要验证、完整终态/全文报告/全部意见、CI/两OS/真人/develop远端及全部57P0保持。无新增付费、密钥读取/搬运、重置逐次确认绕过或宽泛结束用户进程授权。

## 规则传播与历史

阶段主聊天唯一修改主repo AGENTS及注册worktree政策副本；总控唯一修改common、active scope/goal-objective、permissions、state/队列。当前主AGENTS15147B/SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，传播收据 `outputs/20261022_desktop_policy_update/propagation.json`；异版仅按原操作政策段更新，其余不覆盖。

历史冻结prompt、原始审查输入、历史报告与旧原件不改。新任务附当前政策，已有任务由原owner在安全边界透传；单纯guidance变化不是产品/测试/依赖/验收或base变化，不重建Goal、不因本政策重审现有MiniMax。旧“无GUI许可”“待桌面时段”“必须先CLI登录”只能按历史时点解读，不能继续成为当前阻断理由。实际派发/任务ID/设置与终态另记，不把policy落地当任务已完成。
````
<!-- END current-desktop-policy.txt -->

## 当前指定应用权限全文

原字节 4462B，SHA `feea1595894b347ff1151e5526bc21e2055911f2ba744670f08ba85765f8b53a`。当前操作遵守本轮执行补充，旧冻结静默或只读运行限制不覆盖当前政策。

<!-- BEGIN current-permissions.txt -->
````text
# ZCode / MiniMax Code 默认执行权限

2026-10-21 用户明确指令：“更新调用zcode和minimax code的权限，默认为完全访问和始终授权”。适用于本项目现有和后续对这两个应用的调用；应用权限模式不改变具体任务的职责与验收。

## 默认与实际持久化

| 应用         | 默认模式               | 本机实际配置                                                             | 本次结果                                 |
| ------------ | ---------------------- | ------------------------------------------------------------------------ | ---------------------------------------- |
| ZCode        | 完全访问               | `/Users/kyle/.zcode/cli/config.json` → `permission.mode = "yolo"`        | 原子写入并读回；其他配置与原权限子项保留 |
| MiniMax Code | 始终授权 / Full access | `/Users/kyle/.minimax/config.yaml` → `permissionMode: bypassPermissions` | 原配置已经满足，核对后保留               |

ZCode 的默认配置路径、合法模式及 yolo 跳过权限提示的语义，来自已安装应用 `/Applications/ZCode.app/Contents/Resources/glm/zcode.cjs` 的实际配置加载器、schema 和权限判定实现。修改前备份为 `/Users/kyle/.zcode/cli/config.json.before-permission-20261021-084806.bak`，仅在需要恢复时本机读取，不复制进仓库或输出其他配置内容。

MiniMax 的配置和界面映射由已安装 `@mavis/local-runtime` 实际代码独立核验：`bypassPermissions` 对应中文“始终授权”和英文“Full access”。`config.chatPermissions` 不是已证实的全局默认入口，未手造或修改。运行时官方配置更新入口会清缓存并广播变更；本轮没有启动/连接运行时、修改其桌面 store 或重启应用。

## 调用时的执行要求

1. 新任务默认使用上述模式；创建/进入实际任务时读回其显示或实际配置，不只依赖用户级文件。项目覆盖值、显式请求参数和既有会话状态可能优先于用户默认。
2. 当前计算、冻结候选和审查任务不重启、不丢弃；在安全边界确认权限，必要时通过应用支持的会话设置切换。不能仅凭配置文件改动声称所有在途会话已经即时切换。
3. 用户已授权上述默认应用权限，常规调用不因旧提示词中的默认模式重复询问。应用硬限制、系统权限和平台工具自己的确认机制仍以实际支持为准。
4. 对抗审查仍只读实现；只允许约定验证和独立报告写入，禁止修改受审实现或自行提交/推送。完全访问是执行能力，不把审查任务改为开发任务。
5. 指定模型、思考等级、同版双审、意见处理、CI与远端核验保持。2026-10-22静默桌面偏好已撤回，可由原功能owner直接computer use，互斥桌面资源由总控内部协调；不必再申请用户时段。
6. 新任务提示词和共同开发指南附上本要求；历史冻结输入保留原样，文档权限规则更新本身不触发无变化的实现重审。

## 证据与接收

- ZCode 写前 SHA-256：`c7f88256c49fbae707d57bfcd294dfa4becee03169ded1f14f9ab7b8aa47bb5f`。
- ZCode 写后 SHA-256：`67f26b9702a009fa8353b77f9f9b6d44658bd9fc41f55b31e924d872cb2124`。
- 已逐项比较非权限配置及权限中其他字段，结构相同；未修改任务数据库、应用安装包、模型或思考设置。
- MiniMax 的本轮独立只读核验确认默认已符合；没有把静态文件核验当作每个运行会话的权限回执。
- 由现有执行总控维护调用指南与派发状态，在安全边界透传进行中开发线；实际发送/回执另行记录，不假定写文件即自动生效。

## 2026-10-22 后台恢复补充

当前人类已撤回静默桌面偏好，原功能owner可直接computer use；已启动的官方CLI/app-server任务继续。原指定模型、思考等级、逐任务权限读回、同版独立审查和全文终态门不变。T06两项真实任务已启动，桌面创建动作已结束；其他线由总控内部安排资源，不自行抢建任务。

历史：昨日短时答复曾被误记未答、随后又被误作本轮新答复，原件及16:01停止记录保留。当前人类已经撤回整个静默桌面偏好，原T06直接CUA创建ZCode审查，不再以旧时段/CLI认证阻塞；现有MiniMax任务保持。详见desktop-operation-policy-20261022.md。
````
<!-- END current-permissions.txt -->

执行前再次确认本方实际cwd/设置/lease。所有产品输入仍只读；只按上述允许普通验证写本方运行产物和最终报告，不修改旧提示/manifest、不抢任务、不降低任何原验收门。
