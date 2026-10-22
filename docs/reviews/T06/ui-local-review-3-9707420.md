# T06 UI 9707420 全范围独立只读审查

结论：**通过“私有、未挂载 BehaviorWorkspace 组件完整范围”的本次本地独立审查。未发现新的 P1/P2；旧 571 的 3 项 P2 及 da37709 的 callback churn P2 均经本次独立验证关闭。** 保留第 5 节的 P3/装配边界与第 8 节全部未验范围；这不是双方新指定外审、FR-600–604 父模块、真实领域执行或发布通过。

审查者 `/root/ui_9707420_complete_independent_review`，来源为父 `/root` 的新全范围独立审查派发；未读取本轮其他指定模型意见。2026-10-22，Asia/Shanghai。

## 1. 固定身份与实际规则

- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 产品：`97074205d677a8cc272426b1bcabe7140b5be085`。
- 流程 HEAD：`8ed1fc562efd6416e9b571c4e62bc9e587db4b75`；本审查独占 detached worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-independent-review-9707420`。从该流程提交实际 `git worktree add --detach` 创建。
- 原开发树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior-ui` 及两个旧指定 review roots 保持冻结，本审查未写入。独立 `npm ci`、`uv sync --frozen` 实际 exit 0；本树独有 `node_modules`、`.venv`、`out`、`test-results`；Node `v24.15.0`、npm `11.12.1`、Python 依赖安装日志显示 CPython `3.12.12`。
- 已全文读取并复制最新 AGENTS，15147 B，SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，仅此规则副本受保护 dirty/未暂存。已全文读根 `iteration-control/2026-10-21-weekly-release/desktop-operation-policy-20261022.md`；旧静默限制已撤回，本次仍遵守父调度的 GUI/native/Electron/HMR 禁用范围，未抢其他 owner 的桌面资源。
- 没有产品、测试、依赖、锁、配置、公共契约、source-manifest 或其他树改动，没有 commit/push/PR/GUI/native/Electron/HMR。仅写本树独立报告、忽略的审查工具和验证证据。

## 2. 完整读取与来源核对

已全文读取全部 10 个新增文件：BehaviorWorkspace.tsx（804 行）、controller.ts（295）、model.ts（349）、presentation.ts（42）、behavior.css（301）、verify-headless.mjs（467）、tests/unit/t06-behavior-ui.test.ts（958），及 README.md（43）、status.md（62）、verification.json（295）。全新增 diff 的全部产品与流程内容已分别读完；并非只审 callback 修补差异。

独立由 Git 重新生成 base→流程 HEAD 完整 binary diff：**10 文件、173215 B，SHA-256 `8d71b91d6b80f56c3976621fb3d3e687738929dcc88166287039b19c509c0193`**；与开发线 full-delivery-diff.patch 逐字节相同。base→产品完整 10 文件 diff 为 156973 B/SHA `b5cf67b748b6c8a68e4deeeb817eb9990663cdc2bd288c89ce691299149fe3ae`；7 源及 README 的 source-diff 为 141603 B/SHA `892ee2bd3a70874463490258ae4cbcebed9d01dd55c3117b299a6a3122b630b7`。三份已保存 diff 均与对应 Git 命令的实际字节一致。产品→流程仅 status.md、verification.json，两者已全文审查；其余八路径零差异。

已按原文核对 PRD V0.6（93584 B，1255 行，SHA `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`）：FR-600–604、附录 C、D.1/D.2、E.1/E.2、G-behavior/重置契约、G.3 B-01…B-11、Q5、第 10.2/10.3/10.4。另读 ADR-0001、ADR-0002、M0 更新计划中 S1/S2/S3/C1/B1/U1（实际可用固定副本 `docs/reviews/I03/inputs/m0-review-and-update-plan-2026-10-19.md`），以及 M0 checklist。按 AGENTS 核本地优先、renderer 隔离、唯一 Store、历史不可改、失效规则、固定错误面和 Agent/确定性解耦，没有把历史状态快照误报为当前生产能力。

共同历史全文读取：`/tmp/T06-UI-571b4d6-independent-review.md`、`/tmp/T06-UI-da37709-independent-review.md`、571 负例工具；主 T06 `docs/reviews/T06/ui-round-1/` 的旧 da37709 两指定报告（Z 24568 B/SHA `b7715b6dd4d8b4caadfdeebc59136923e610ff1280590b63f4a0e04010061cfd`；MM 45074 B/SHA `929a20820b916c60d4ade7f57195f8db7a59c63359bccd9ea13e76d13b2c2a26`），及 owner-completion-audit、remediation-plan。另全文读 ui-integration-handoff、ui-validation-da37709、ui-validation-9707420、ui-archive-index 和 ui-archive 文档。未读其他线当前 S1 审查或新同轮指定意见。旧指定报告的“条件通过”不是本次 P2 关闭依据；旧报告中被 owner 指出的 marker、截图、argv/tee 等矛盾保持原文，不照抄成已证事实。

来源核验的可追溯范围：

- `hash-audit.json`：144 条校验记录（含重复来源比较），失败 0。覆盖当前 7 源在工作树/产品 Git/流程 Git 三方、README、当前 verification 的 20 份产物引用与大小、571 和 da 固定 Git verification 对象、旧 11 与 r2 的 9 产物、旧独立报告/负例及其实际 headless 原件、当前浏览器 16 文件等。
- `archive-and-png-audit.json`：父回执 27 项实际源/产物逐件 bytes/SHA 一致；当前 source-manifest 与 verification 的 7 源字典一致；4 个历史恢复包按包 SHA、安全 regular 成员和内置 manifest 的每件 bytes/SHA 验证，未执行包内任何代码。历史 policy/handoff 摘要哈希作为固定旧 verification 的原文元数据保留，不能代替当前规则核验或声称本次重验了这些其他线交付。
- `npm run verify:sources` 本次实际 exit 0：**该固定基线的 docs/source-manifest.json 是 12 项**，全部逐件重算一致；manifest 自身 SHA `4e3a43ab0d67129d41ba42e2fea5d4e3e86d209d936ac04bb3d55857824a1ec8`。不沿用其他分支/旧记忆的 13 项计数。
- 最新 verification.json 本体 SHA `bd50fab94ed994bf7c04cb90b2a8abe8c8297866d83498748bbbc605d9554d32`；本线 source-manifest SHA `2ca4d598bcea58d23cd40ae053917897dec99d7743aeaa3b85163cf93c07757e`。不修改 pending review 记录来替换作者流程状态；本文是本次独立终态。

七项受审源/测试/脚本 SHA：

| 路径 | SHA-256 |
| --- | --- |
| `apps/desktop/src/renderer/src/behavior/BehaviorWorkspace.tsx` | `0e7012e1a5d2791fda1aafd5eea0a8248d78d7329e8513ea7ad2062ae39f671b` |
| `apps/desktop/src/renderer/src/behavior/controller.ts` | `c8869024557723b797fc0b3ba9ea29103ac8d965e540444ff2a269de1aac7628` |
| `apps/desktop/src/renderer/src/behavior/model.ts` | `68d6337e449b14d489978119eea2a95b593f22cd100a54f97af66c8a7161db39` |
| `apps/desktop/src/renderer/src/behavior/presentation.ts` | `5966010c9a052cc2bbd7524e759fe06d9806c698259e84039aae54fcb28fa1d2` |
| `apps/desktop/src/renderer/src/behavior/behavior.css` | `869ebea1be9dcbfb839814c5c610bd7bc698420edc5f4c05e315ad37347c1465` |
| `apps/desktop/src/renderer/src/behavior/verify-headless.mjs` | `b4e6288829114640fe0146d49a233ebee307e2a46591d6299360479c2c308149` |
| `tests/unit/t06-behavior-ui.test.ts` | `0fdf4eb8ac87cfc7390c3bd5b72f15ce6cd44bb862995e8e3d09f9d7bc182e67` |
| `apps/desktop/src/renderer/src/behavior/README.md` | `81eec885c9e251cfffd29fdd3d3797f5b3d87e14981dae529f7f70d853c7f6dd` |

## 3. P2 逐项关闭判定

| 项目 | 本次源码审查与独立运行依据 | 判定 |
| --- | --- | --- |
| 571 P2-1：无额外条件无法忠实表达 | strict always 有明确 UI 选项且不伪造 object/property；空数组/缺条件/always 夹字段仍拒绝。53 单测包含 X/B-a/B-b author→callback；原完整 headless 实际完成 onDraftChange、空组拒绝、重选与 run callback 保真。独立补充检查 always 不改变其他条件检查责任。 | 关闭 |
| 571 P2-2：单轮候选/动作/通知证据矛盾 | 四种单轮状态的完整合法矩阵保留，原 60 合成组合实际重跑；四状态 controller 拒绝与刷新保留也重跑。新增探针逐状态构造“首项合法、第二项非法”的混合列表仍拒绝，及 error/stale/未知 evidence 反例。headless 实际验证 candidate+applied/recorded 被拒、新 run 不显示、refresh 保留旧有效结果。60 不是 60 次真实引擎运行。 | 关闭 |
| 571 P2-3：保留键静默丢值/身份折叠 | JSON.parse 后、record 归一化前核自有键；两份同 ID 不同 __proto__ 均拒绝且调用计数不增。新增 6 种 literal/escaped 三键混合载荷、带另一有效事件的批次，均不发生部分回调、原文精确保留。修正后普通字段完整送达。不描述为已利用的原型污染。 | 关闭 |
| da37709 MM P2：callback identity churn 清 pending 并重复提交 | configure 只更新未来服务函数，同 context 不改变 epoch/pending/cancelling；operations 以四维 context + 独立对象身份 token 记真实调用。显示 accepts 同时要求 token/context/epoch，finish 按 owns 回收真实在途，旧 finally 不影响 successor。原53测试与完整 headless 故意每次 host render 新建 callback，无 useMemo；真实 deferred 未放行前按钮持续禁用、计数不增，resolve/reject 才恢复；版本切换/切回、取消先赢、后继取消仍在途时旧 Promise 最后返回均实际通过。独立额外覆盖四维 hidden cancel 切回、三 context 逆序收尾、refresh 切回、同步 throw。没有靠宿主稳定引用或假取消释放来关闭。 | 关闭 |

UUID 边界：crypto.randomUUID 与 draft/event 请求构建处于 try 内，失败发生在 begin/pending/服务调用之前，固定文案安全返回，无不安全 ID 降级。53 项中的真实 mock 异常及恢复后新调用断言已本次运行；未把测试替身当真实浏览器缺 crypto 的平台验收。

取消归属：cancelAttempt 属原 operation，真正绑定 cancelled 终态才释放；ack、错误、五字段错配、schema 矩阵不符均保持原 run。取消错配专用提示、完成先赢/取消先赢、失效 epoch 的隐藏取消收尾、cancel 错误迟到不盖新 notice 已分别由53测试、headless与新增探针覆盖。

## 4. 完整范围其余结论

FR-600 的名称/业务说明/触发/条件/动作/效果/启用/优先级/版本齐备，单一 AND 组，已有行为编辑 ID 例外有校验。四种动作与上下移/删除具备；已知对象/类/属性/IRI、先创建再引用、单值关系追加拒绝与多值覆盖拒绝均保留。填空式 ID 输入符合已声明范围；没有将缺少 catalog 候选 UI 误列为新需求。

事件的唯一 ID、顺序、标量 JSON 和显式 add/remove/set 编辑保真；批内重复拒绝、跨 run 重投保留事件 ID，仅 requestId 新建。没有 UI 领域推理/竞争/幂等算法；本地检查明确不等于真实引擎通过。条件读取冻结断言+行为前推导、稳定排序文案与 E.1 一致，但算法真值仍须真实 adapter/服务证明。

触发/未触发理由、全部动作服务顺序/状态、Diff 增删、通知、request/run/断言/推导/执行语义版本展示完整；candidate、completed、failed、cancelled 与 current/stale/historical 分开。失败/取消非空 Diff 标为“未提交尝试”，不升级为提交。编辑后保留旧请求依据并提示，refresh 绑定同 runId，不重发事件、不盖草稿；切项目载入对应初始草稿，同项目输入变化保留本地编辑，宿主换编辑行为须按文档 key 重建。跨实例持久任务恢复没有被包装为本组件能力。

renderer 产品代码未引入 Node/fs/shell/通用 IPC、网络/模型/存储/遥测、innerHTML 或公共能力。未装配 App，scope 字样不是权限证明。固定枚举错误映射本地文案，catch 不回显原异常；未知 evidence 被 strict schema 拒绝；React 将 HTML-like 通知显示为文本，headless 实际 img 数为 0。开发脚本的临时 loopback HTTP server 只服务受控夹具资源、finally 关闭，不是新增产品 HTTP 引擎端口。

真实 Tab 焦点推进与可访问角色断言通过。已实际查看本次 width-1440、viewport-390、width-390 图：双栏/窄屏单栏、中文表单、always 字段、取消回滚/丢弃与“未提交尝试”标签可见，无重叠或横向溢出。PNG IHDR：1440×2549、390×5292、390×1000；工具展示长图可能缩小，不以展示缩放尺寸替代原 PNG 尺寸。

## 5. P3 与未关闭边界（保留）

1. **P3：index key 焦点体验**。条件/动作/事件/变更列表仍以 index 作为 key；受控值本次正确，删除/重排的焦点稳定 UX 尚未独立做专项真人验收。旧观察保留，不称已修复，不在本轮擅改行身份模型。
2. **P3：本地检查 scroll 稳定超时根因未闭环**。开发线本轮首 headless 在 scrollIntoViewIfNeeded 等待 stable 超时，原日志/Failure.txt/ARIA 已核，failure.png 确实没有生成；不能补造失败图或认定唯一环境原因。最终 helper 记录 locator/box/fonts/style/scroll，仅该纯本地动作 TimeoutError 允许一次原生键盘 Space，并保留首败/实际模态；run/cancel 无 force/重试。本次独立完整运行首轮 exit0，三次 pointerSucceeded=true、interactionFallbacks=[]；证明本次鼠标路径通过，不能证明旧根因已解决。
3. **P3/装配 gate：结果自由文本的可信映射**。README 已明文要求 reason/detail/freshnessDetail/通知等逐项批准展示白名单；schema 仅结构/长度，不脱敏。独立探针主动让合成 path-like 文本进入合法 reason/detail，确实原样形成结果文本。因此文档边界已澄清，真正 adapter 映射未实现/未验；不能把本次 Pass 写成敏感文本已安全处理。禁止依靠猜测路径过滤代替真实映射。
4. **容量与引导边界**。catalog 仍主要用于校验，事件事实变更的已知性/基数与完整行为集合映射交给 adapter；结果有数组上界但无本次最大规模性能实测/分页联验。Q5/10.2 的容量/设备/响应目标仍未定，未量化性能改善，也不把 10k 条 schema 上界称为渲染性能保证。

混合保留键与取消专用提示的旧 P3 已以代码+真实交互闭环：整事件（含普通字段）不执行、原文保留且需显式修正，禁止自动 strip；取消错配明确“取消尚未得到有效收尾确认，原请求继续等待”，不误报已取消。这两个 P3 不因本段其他残余重开。

## 6. 本次真实命令、退出码与日志

全部 cwd 为本独占 worktree；验证日志完整保存在 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-independent-review-9707420/out/independent-review-9707420`。命令实际重定向 stdout/stderr，shell 捕获 `$?` 并以同值退出，工具返回真正上游退出码；未用 tee 的 host exit0 替代。下表 SHA 是完整日志 SHA，不是截取尾部。

| 命令/阶段 | 真正 exit | 结果 | 日志 / SHA-256 |
| --- | --- | --- | --- |
| `npm ci` | 0 | 独立440包；锁/配置未改 | `npm-ci.log`（748 B）/ `4496d9095268c72ef73b55a9a695cba372914bb846c19a2a61b5e1f0c084e4d9` |
| `uv sync --frozen` | 0 | 独立.venv；frozen | `uv-sync.log`（925 B）/ `ac88425497ee12658c9b25c8451e3755463d79ce86db53263e4f5cddd8330c74` |
| `npx vitest run tests/unit/t06-behavior-ui.test.ts` | 0 | 53/53 | `unit.log`（250 B）/ `5e2d3616ca264a7107f41e1f1d73b291e7a485a88bc7863fe6d6ee4a347b91ee` |
| `npm run verify:sources` | 0 | 12归档源一致 | `verify-sources.log`（111 B）/ `1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536` |
| `python3 .../audit.py` | 0 | 144条hash全部一致 | `hash-audit.log`（121 B）/ `b4ea5dccc69b8a1bb3df773c22d5e1e0207fba110cb84dab278b2fb2607c648a` |
| `PLAYWRIGHT_BROWSERS_PATH=本树browser-cache node .../verify-headless.mjs` | 0 | 完整原12链；首次成功；3真实pointer、0Space | `headless.log`（5688 B）/ `83fcd825bce5e07ce85a0aa96986e2011012ecf633e4a2a12137fc2f343de8f9` |
| `node .../extra-probes.mjs` | 0 | 8组全部通过 | `extra-probes.log`（988 B）/ `3ad7b0cfa0ea18cf0a86fd683ff3655c1f6ebcf0cb5733e80082a7d4206c03ca` |
| `archive-audit.py 首次（审查工具）` | 1 | 错误假定source-diff不含README，断言失败 | `archive-audit-first-failure.log`（324 B）/ `d8dcf04f990ceb2550466f61d939ba64878e5624370a9d5bc2c1e11fde307242` |
| `archive-audit.py 修正后` | 0 | 修正审查器路径集合为7源+README；4包/27项/3diff/PNG全部通过 | `archive-audit-final.log`（3285 B）/ `55d05bbd7b1bbc7776a8ca04e1ac3eaa0fff8b9fe3d1b96a1068bf9cc82004a6` |

headless 副本 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-independent-review-9707420/out/independent-review-9707420/verify-headless.mjs` 与冻结脚本 **恰好两行差异**：component 绝对路径与唯一 output 目录；runner-relocation.diff 已保存。所有 fixture 输入、断言、点击与取消行为、12链、截图和1440/390设置不变；没有浏览器版本伪装、降级安全、force 或 run/cancel 重试。实际 browser 从原开发树的官方回执安装只读复制至本树独占 cache，16 regular 文件 bytes/SHA/mode 全匹配，binary SHA `77d8278b1ac9d0687fad4e817ea83023ede09b1deef36e1864b49ba194ac9634`，`--version` 真正 exit0=`Google Chrome for Testing 156.0.8078.4`。官方 ZIP 103778487 B/SHA `94e4337b70cbc5638f0935fbc46b9f242bc7416f657e3fbe924baf348404b53d` 为已核回执来源；本次未重下载 ZIP，不冒称自己的官方网络获取。1248 只是本次来源，未加成永久产品额外 gate。

独立8组探针内容：四维 hidden cancel 切回与 callback churn；三 context 逆序 settle 和完成赢取消；refresh A→B→A 无复发/结果复活；同步 run/cancel throw 固定错误；混合条目矩阵/未知 evidence/stale/error；ack 与非法 cancel 不释放；6种 literal/escaped mixed reserved 原文/批次保护；自由文本残余边界主动复现。源码以内存 Vite build 加载，不写受审源码，不运行历史归档 preview。

**完整 npm run check 未在本审查机械重跑。** 按父授权复用开发线原配置原命令来源，已全文读并核 `test-results/t06-ui-r3-check-first.log`（5048 B，SHA `ecadd8e43f8aeb0298809578778a1fe248ed8aa9c6b4673ec1733d1dad839cff`）与当前源一致：lint、format、strict 类型、683 TS、本地桌面 build、ruff、1052 Python 全阶段完成，owner 记录真实 exit0。此为“owner 执行、独立来源/日志核验”，不写成我独立执行683/1052；其中 Python 属批准5f基线，不等于审过另一线未合入S1引擎。

开发线首 targeted lint exit1 的16unused mock诊断是明确标记的工具输出忠实转录，SHA已核，不能改称原 shell tee。开发线首 headless exit1、第二/最终exit0均保留；本次独立首次完整headless exit0，不删除/覆盖旧首败。原571两次工具装配失败、两指定旧check证据目录污染/网络失败/点击首败与argv局限仍在已核历史包中，未据后继成功倒推它们为成功。

本审查自身首失败也保留：archive-audit-first.py 与 archive-audit-first-failure.log（exit1）完整保全。审查器原假定source-diff只含7源，真实该文件含7源+README，133841 B与141603 B区别明确；只改审查器，三份原diff未改，修正后exit0。另有三次只读工具准备/读取失败：首次从非Git父目录执行worktree add exit128（未创建），改在已知Git worktree执行成功；旧M0文档路径缺失exit2，改读固定inputs副本；manifest探索把list当dict导致AttributeError exit1，随后按真实结构读取。它们保留在工具记录并在evidence-index列明，不当作产品失败或测试成功。

`git diff --check base HEAD` 本次 exit0；收尾重新核固定HEAD、受审10文件hash/zero diff，只有保护AGENTS与本独立报告未跟踪路径可见，没有stage。

## 7. 独立产物与恢复定位

完整结构化命令/退出、大小与 SHA 清单：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-independent-review-9707420/out/independent-review-9707420/evidence-index.json`（13245 B，SHA `d41cb2a748076daeda28f9285ab8e4dfbe739b52cc1cee890c66a6b6d05e1201`）。该文件记录了验证脚本本身、完整日志、hash-audit、archive-audit、runner两行diff及实际新PNG；不含浏览器全部大二进制。开发线历史证据只读副本在out/history，不进入源码扫描目录。

当前本次新图：

| 图 | 原始尺寸 | bytes | SHA-256 |
| --- | --- | --- | --- |
| `viewport-390.png` | 390×1000 | 86643 | `b95d7e9254fa35c38e80d97ca68ebb42c7c452c4e2fa20c89e23d1ebc17d614e` |
| `width-390.png` | 390×5292 | 338533 | `4142f092cfa1dd70554719d5be4d5baa5f0a0c648ec84979f63b6d95c3d1a253` |
| `width-1440.png` | 1440×2549 | 356292 | `c356b2bb2f30f2a34957416c803819b31955a052891498e416513d5a5fd078a5` |

4 个历史包只读完整性复核（不表示重做所有历史验证）：

| 包 | 成员 / 逐件数据核验 | bytes | SHA-256 |
| --- | --- | --- | --- |
| `ui-original-artifacts-20261021.tar.gz` | 34 regular / 33 manifest entries | 2232198 | `a51bfec8089f9a7db1578ebbfcc3570e1591beda51b956f2d8bf165a0cfab433` |
| `ui-session-tool-records-20261021.tar.gz` | 8 regular / 6 manifest entries | 6698 | `06d2e8636bbef29c6bb131bb3605c4f15e679d784137a2bffec5e58d472f5a3b` |
| `ui-zcode-original-tool-evidence-20261022.tar.gz` | 1013 regular / 1012 manifest entries | 3566845 | `3fabc7472130653d15d50900f36a7015d2a6cac3e286a10c321d12f1a03c5b80` |
| `ui-minimax-original-tool-evidence-20261022.tar.gz` | 139 regular / 137 manifest entries | 1494644 | `84d476e30e855aa4c0cce03164314e2512302103c521682052d84dedc806bfc5` |

原33件恢复包manifest、6条工具原行长度/SHA、两个指定工具包1012/137数据条目均一致。没有从当前浏览器/新截图倒推历史没记录的binary/完整argv，没有把归档完整性检查说成独立语义复演全部历史工具。

## 8. 私有范围结论与全部未验门

本次私有未挂载UI完整范围通过；4项历史P2闭环不依赖useMemo，2项文案P3闭环，其他P3及适配器/容量边界保留。双方必须针对本产品9707420/流程8ed1fc的新同版完整指定审查；旧da报告不能转移为新版本双通过。

下列仍未验，不能凭组件夹具或静态检查关闭：正式App导航/宿主草稿与跨实例任务恢复；公共bridge/preload/CSP及真实授权/隔离来源；私有equals/exists/type、完整行为集合、事件sequence/version/changes、动作初始化/单多值/源动作计数的批准无损映射；真实推理/行为前冻结快照/写意图/排序/幂等/竞争；Store唯一原子提交、回滚、cancel终态持久化、崩溃对账；真实G.3 B-01…B-11与E.2整轮及资源/轮末推理、Agent真实工具结果；正式失效表current/staleReason来源与历史只读；自由文本白名单和受限结果/分页；Electron/macOS/Windows、包内执行/干净设备/签名安装/真人验收；CI、push、PR、merge、develop远端与发布。父FR、T06整体、M0和发布状态均不由本文更改。
