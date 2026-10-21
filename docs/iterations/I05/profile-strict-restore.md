# I05 私有 strict 保存恢复实施记录

本阶段实现纯私有 `restore_profile_batches`：完整保存字节、同次独立捕获的 expected/原分池上下文，恢复全部原生字段并在新解释器重新发行 PV；所有核验完成后，逐 child 仅一次调用 16c `check_firing_batch`。返回仅声明 supplied-batch consistency，`formal_authority=False`、`aggregate_recomputed=False`。

基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3`；树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-profile-restore`；分支 `feature/I05-profile-restore`。68 份只读输入逐字采用提交 `ddcf5edfb9609874251882090693384b97073e9f`，收据为本线 `adoption-receipt.json`。实现与测试候选、检查原件、完整相对基线清单均保存在 `docs/reviews/I05/profile-strict-restore/`。最终核心候选 `3ef2f6952ed1a4f852da31c0bef7e8d8679752a5` 见 `candidate-3ef2f69.json`；旧 `candidate.json` 仍绑定 1316050。最终验收状态以末节为准。

## 文件责任与改动范围

仅新增两个核心模块和两个测试模块；不修改 68 份固定输入、旧 semantic/quality/Budget/API、资源、Store、worker、selected、配置或锁文件。保护的 AGENTS 为 15852B、SHA-256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，保持 dirty、未 stage。

| 内容                              | 实施责任                                                                      | 独立环境/审查                              |
| --------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------ |
| strict schema、原生重建、原子编排 | root，`semantic_profile_restore.py`                                           | schema 独立 agent 逐实际源码审查           |
| scanner、R 账本、完整键 trie      | budget 实施 agent 后按固定字节交给 root，`semantic_profile_restore_budget.py` | budget 独立 agent 审查循环、委托和同时持有 |
| 真实生产、跨 exec、污染与紧池测试 | test 实施 agent 后按固定字节交给 root，两个新测试文件                         | 独立树自身环境实际运行；root 集成复验      |

授权 raw、固定方案 raw、固定输入 raw、采用收据、各独立审查、首失败与修复处置均留档。没有整棵 cherry-pick、覆盖旧树或修改控制目录。

## 实现与资源合同

严格 bytes/UTF8/JSON 前门拒绝重复键、原生 number、非有限值、surrogate、过深结构、未知字段及错误位置 tag；按位置恢复 exact canonical 类与 tuple/list，不接受现成 native batch、pickle、alias 模块或任意对象协议。每个 PV occurrence 完整核 term/domain/value/language，缓存命中也不省略比较；完整 key 包括 SourceRecord 四字段、source 存在位、None/空串、原始语言和 datatype。每 child 独立强引用缓存与同原 L 的 R_parse 池。

原 matches 顺序及全部 false/true、comparison/head/basis/payload/source 均保留。disabled 保持原 None 载体，仅在 API 参数中明示映空 tuple；真实空 batch 仍核验。原 allocator 按 Unicode ID 排序与 ordinal 逐 divmod 对照全部 17 字段，disabled 仍占槽。input/source 前像缺失即拒绝，不重跑 matcher、不修保存值。聚合图结论、planDigest 等由 strict shape 与原独立摘要绑定，未重算图。

R 是分域逻辑费用与持有票据，分别报告 usage/peaks；不与 CPU/RSS 等同，不声称整体 R≤原 W/I。原 parse、16c 三池和新恢复域分开，所有上限沿固定方案。失败不退款；同 ledger 终态不得重试，新 ledger 仅表示另一纯操作。

首审后补明确前置票据：projection 每份 4J 普通 scalar 与 2J objects 持至消费者释放；canonical encoder 在委托前留 `8*bound+64`，覆盖 chunk/data/sink/final bytes 后转返回 buffer；graph/parse setup 固定对象提前预留；A16 工作、元数据及 receipt 在构造前预留，结果在账本 running 时构造，快照后仅清理和终态处理。调用者捕获上下文也显式记入固定池内持有。未扩大任何 cap。

## 实际验证与失败记录

root 树自身 `uv sync --frozen`、`npm ci` 均 exit 0，独立缓存；npm 安装使用 `ELECTRON_SKIP_BINARY_DOWNLOAD=1`。一次空 batch smoke 通过，仅为同解释器 smoke。

首轮专项实际 139 例：134 passed / 5 failed，完整输出及当时四文件保存在 `runs/04-*`。超限分类的实现问题已修；其余处置区分保持原 expected 摘要的污染拒绝与主动重绑摘要的机制核验、真实双 key 的 split 夹具、未完成整次 slot 的私有单元终态。原首失败未覆盖。

测试实施线固定 b301/94d 的独立运行 139 passed / exit 0；93 份原 stdin/stdout/stderr/supervisor 共 11328060B，逐字归档于 `test-implementation/05-child-execs.zip` 并附成员 hash。23 组真实 exec、25 API slots 覆盖九 domain、负零、SourceRecord 四字段各 40000、重复 source、false/true、disabled、真实空状态、大 Turtle 和空图 witness。N100 原生产已 resource failure，保留其原始负例，未声称恢复成功。

候选 1316050 修后专项实际 142 passed / exit 0，未超时；`runs/06-*` 含完整输出及命令前后 72 文件 hash。运行时 Git HEAD 尚在 bbd，四个实际源码/测试字节与随后 1316050 提交逐字一致，由 `candidate.json` 显式核同，未改写运行身份。

## 独立审查与当前验收状态

首 bbd schema 审查确认 S1 P2：内嵌 `rule_ids` 在 exact tuple 门前触发 len/iter。真实入口探针保存在 `runs/05-schema-callback-probe.json`。首预算审查未批准完整持有来源：BR-01 encoder 局部“两 buffer”来源不足，BR-02 projection scalar 转票和 BR-03 metadata 前票未落明；未证明整次恢复突破固定总 cap。

1316050 独立 delta 已关闭 S1 和三条预算来源意见，但确认新 S2 P2：receipt 构造异常时公共错误帧仍保留局部 children；`runs/07-receipt-failure-probe.json` 保存真实反例。最终 3ef2f69 先清五组局部引用，再清 decoder/账本；constructor、usage、peaks 三处真实 MemoryError 故障注入均通过，原成功与末 child 失败路径保留。schema 的 `delta3ef-report.md` 与 budget 的 `delta-3ef2f69-review.md` 均已有限通过，本范围无未关闭源码意见。旧失败报告不改写。

最终候选实际 `npm run check` exit 0、未超时：lint/Prettier/typecheck、15 文件 630 Vitest、vite build、ruff check/212 文件 format、2873 pytest 全通过，其中恢复测试 145 例。实际 `npm run verify:sources` exit 0、未超时，核对 12 个归档源文件。`runs/08-*`、`runs/09-*` 保存完整输出、真实进程、命令及所有 72 项候选加 AGENTS 的前后 SHA。仅报告该次观测耗时，不承诺最坏 CPU/RSS 容量。

最终运行另归档 93 原件/11327668B：`runs/08-final-child-execs.zip`（326113B、SHA-256 `354133c1237ed2ea33fc6aa2ef42b7155628f5dd4a937853b9d8e8ba6600c807`）。23 个不同子 PID、初始 issuer 空、25 个完整 API slots 全部成功；输入流及完整 native children/calls/facts/parse_usage 对独立 94 归档逐字/结构全同，外层 R/peaks 按补票后的实现变化。N100 仍保留原生产失败。可从本树运行 `python3 docs/reviews/I05/profile-strict-restore/runs/audit-final-artifacts.py.raw` 复核源绑定、输出摘要、93 成员及完整签名比对；实际结果在 `runs/10-final-artifact-audit.json`。

本地技术候选和证据已准备供根总控固定 ref 读回；相对基线的 72 项及全部过程 docs 精确清单见 `final-full-diff-manifest.json`。源码检查完成后仅收尾过程文档，文档格式另核，不重复无变化的产品测试。

正式 T01/Store/worker 终态、项目快照/source/Catalog 权限、窗口/撤回/GC、selected、长期字段/公开消费、T03 包接入、父功能/目标平台/指定双模型/CI 与合并门均保留。本阶段未运行 GUI/Electron/e2e/native/HMR/CUA/Keychain/模型/付费，未 push/PR/merge；未重建或变更原 Goal 状态。
