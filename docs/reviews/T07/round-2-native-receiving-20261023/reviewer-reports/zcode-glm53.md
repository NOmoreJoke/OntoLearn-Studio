# T07-S1 第二轮（R2）指定独立工程审查报告 — ZCode / GLM-5.3 方

日期：2026-10-23。审查者：ZCode（本应用）· GLM-5.3 · 思考最高 · 权限完全访问（yolo）。
会话：`session_0b35de3fed06d21bd17ec25a5848c29d`（operator 收据读回）；originalTurnId 与 officialTerminal 收据为 null，按 **UNKNOWN** 记录，不补造。
工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-zcode-review-r2-f9a1157`（HEAD detached = reviewHead `fdfd908e36a85140078aa1509f091de369157973`）；base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → product `f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3` → reviewHead 祖先链核验成立，base..product 差异恰为 25 路径。

## 0. 结论

**不通过（NotPass / 审查未完成）。** 本结论是程序性的，不是对候选实现质量的否决：

1. 三个必要运行验证目标在本轮**未执行**——本方唯一的验证 Bash 调用（pytest 两 T07 文件 + vitest t07 + `npm run check`，隔离环境、日志写入自有 `.runtime`）被 Mimosa PreToolUse 钩子**自动审批拒绝**。按派发规则，本方未以任何脚本、包装或等价路径绕过；完整命令与拒绝理由已逐字保全于 `.runtime/raw/validation/r2-zcode-001/00-rejection-record.md`，三个目标保持 **UNVERIFIED**，并请求根因（root）裁定。
2. 派发规则明示"必要验证不完整即 NotPass"，故即使静态阅读范围内未发现新的 P1/P2（见 §4.3），本轮判定仍为不通过。
3. 可选 scratch 探针本轮**未重跑**：拒绝保全优先，在裁定前不再发起同族验证命令；探针路径（`.runtime/scratch/probe-copy`，先 cd/pwd）在裁定后仍可用。

在上述限制内，本方完成了完整的独立阅读与源级工程审查：全部 14 项实现/测试/fixture、完整 25 路径 diff、全本 PRD V0.6、全部历史/首败/35 份日志与 PNG 原件、9 份原始终态、七项意见处置与 R1 五项流程失败证据（读覆盖与缺口见 §2、§6）。

## 1. 输入受理与身份核验（本方实际执行）

| 项目 | 实际值 | 依据 |
| --- | --- | --- |
| 官方附件 | 242491 B / 1700 换行 / SHA256 `513da17b…c87d` | 派发说明 + 本方 `shasum` |
| 工作区副本 | `round-2-input/full-input.txt` 与官方附件**逐字节一致**，全文读到 EOF（1701 行，末行无换行） | Read ×3 |
| 14 项实现/测试/fixture | 工作树、f9 blob、25+25 份候选副本、candidate.patch（340601 B / `3e697c94…`，8952 行全文）四处字节一致 | shasum × git show |
| 归档 frozen-inputs | tar 946863 B / `880d4cc9…`，75/75 成员哈希核验 | archive-manifest |
| PRD V0.6 | `.runtime/history/approved-prd-v0.6.md` 93584 B / `7586b2c4…` = base blob，**全文 1255 行**（本轮读全本，非节选——补救 R1 NR-02 对本方的覆盖缺口） | Read ×2 |
| operator 收据 | GLM-5.3 / 最高 / 完全访问；session 见文首；turnId、officialTerminal = UNKNOWN(null) | `.runtime/metadata/operator-identity-receipt.json`（只读） |
| 工作树状态 | 仅 `M AGENTS.md`（保护项 `de15f6ce…c8c4`，非本方改动）+ `?? docs/reviews/T07/round-2-input/` | git status |
| status.md | reviewHead 版（`8898e1a9…`，= @982e4535）与 f9 版（`9a0d5668…`）不同——纯过程差异，符合预期 | git show 对比 |

本方只写本报告与自有 runtime 面（`.runtime/raw/validation/`、`.runtime/reports/`、`.runtime/metadata/reviewer-read-ledger.json`）；未修改任何实现/测试/依赖/配置/受审路径，未 commit / push / 切分支。

## 2. 读覆盖（实际读到的范围）

完整清单见 `.runtime/metadata/reviewer-read-ledger.json`（逐文件 actualRange + 哈希）。要点：

- **全文本读**：full-input.txt（含 R2 规则 §1–§5、六份嵌入历史全文与旧冻结后缀）；candidate.patch 8952 行（25 个新文件全文）；14 项实现/测试/fixture（t09-e5.json 4963 行分 3 块）；PRD V0.6 全本；round-1 材料（README、historical-issues、internal-review-sources 含 9 终态 + 3 条加密中间消息仅元数据、preparation-audit、frozen-manifest、archive-manifest 75 成员、9 份原始终态 JSONL `51f5746a…`）。
- **launch-20261023**：六份历史文档（哈希 `8ee32ae5/050a018a/99323a1d/1ae1439a/4b2222ff/65946e21` 核验 + 嵌入副本全文）；zcode/tool-calls.jsonl（68 调用）与 zcode/tool-results.jsonl（290571 字符）**全文**；minimax/tool-calls.jsonl（85 调用）**全文**；minax 派生 5 件（终态候选、原位探针出处、官方终端标量、附件读取重建、报告写入绑定）**全文**。
- **35 份原件**：33 份文本日志全读到 EOF（含 check 系列 651→657 TS / 1086→1142 Py 的不同历史运行、`persistence-pytest-readonly-fix.log` 的 11 failed/32 passed NameError ×10 与 DisabledReadonly 负对照、ui-first 缺 Playwright 浏览器、ui-final `getByLabel('产能输入方式')` 超时、5 份空日志如实为空）；`page-wide.png`、`page-narrow.png` 以图像方式查看（场景页正常渲染、含 `<script>` 文本以纯文本转义显示、390px 窄视口单列无功能性破坏）。
- **指南/过程/参考**：frozen-inputs guidance 6 件全文（含封存 AGENTS `78df2825…`、旧政策版 developer-common-instructions）；blocking-audit、external-review-readiness.md/json、status.md；m0 更新计划（35812 B `c289a1cd…`，AGENTS 所指基线路径缺失、实际读 I03/inputs 同版副本——该缺口在 status.md 中已有记录）、ADR-0001、ADR-0002；积压清单 md/json/audit 全文；dispatch-20261022 guidance（现行 developer-common-instructions、desktop-operation-policy、AGENTS=现行 `de15f6ce…`）全文；现行 AGENTS.md 全文（会话工作区注入 + 哈希绑定）。

**缺口（如实登记）**：

| 编号 | 类型 | 内容 |
| --- | --- | --- |
| G-1 | 部分读取 | `minimax/tool-results.jsonl`（1315887 B）：85 行**结构目录全扫**（全部 callId/isError/长度，均 err=false）+ 16 行决策相关深读（NR-04 原位探针 bg `ca004736` exit 0 与 status.md 已知副本差异、合规 scratch 重跑探针 textEscaped/noPageOverflow、`npm run check` bg `8552d061` exit 0 / pytest 1142 items、报告复验 30205 B `050a018a…`、最终树状态干净）；其余 69 行正文未逐字读——主体为本方已在其源位置全文读过的文件之 Read 回显，决策相关内容已由全文读过的封存派生件绑定 |
| G-2 | 设计上不可读 | 3 条加密中间消息仅元数据（sources.json 已注明 encrypted/not exported） |
| G-3 | 执行被拒 | §0/§3 的三个验证目标 UNVERIFIED |
| G-4 | 决定不跑 | 可选 scratch 探针未重跑（§0 第 3 条） |

## 3. 必要验证的自动拒绝与保全（本轮核心过程事件）

本方按 AGENTS 第 4 节与派发要求准备单一 Bash 调用，在自有隔离环境（TMPDIR/UV_CACHE_DIR/UV_PROJECT_ENVIRONMENT/npm cache/RUFF_CACHE_DIR 均指向本方 `.runtime`，unset ROOT_SOURCE_PATH/PYTHONPATH/ONTOLEARN_TEST_ENGINE/ONTOLEARN_DB_PATH，pytest basetemp 唯一子目录；stdout/stderr 全量重定向到自有日志、直接取目标退出码、无管道尾部退出码替换）执行：

1. `uv run --frozen pytest` 两个 T07 测试文件；
2. `npx --no-install vitest run tests/unit/t07-scenario.test.ts`；
3. `npm run check`。

该调用被 Mimosa PreToolUse 钩子拒绝，理由为「Bash 直接写源码/安全配置会绕过 Write/Edit 安全扫描」并指称对三个测试文件直接写入——**误报**：三个路径是 pytest/vitest 的执行参数，命令不含任何仓库写入。处置（符合派发规则）：

- **未绕过**：不重试、不拆分脚本、不换等价路径、不经 wrapper；
- **保全**：完整命令、钩子理由、上下文逐字存于 `.runtime/raw/validation/r2-zcode-001/00-rejection-record.md`；
- **留空**：三个验证目标全部保持 UNVERIFIED，不以 R1/M 既有运行结果冒充本轮验证；
- **上交**：请求 root 对该钩子误报给出确切裁定；裁定恢复后可在同一冻结候选上补跑并出具新证据。

与 R1 的对照：封存的 zcode 链显示 R1 遭遇**同一文本**的 Mimosa 拒绝（`call_336cc6c0…` isError=true），随后以 Write 包装脚本 + Bash 执行绕过，构成 NR-03；本轮同一模式下本方选择保全不绕过——这正是 R2 要求"不得重蹈"的差异点，但代价即本轮验证空缺与 NotPass。

## 4. 工程审查结论（源级，限已读范围）

### 4.1 历史 IR-01..05 逐项复核：五项均确认关闭（源级）

| 项 | 内容 | 本方源级证据 |
| --- | --- | --- |
| IR-01 | 运行详情缺依据/身份 | `ScenarioPage.tsx` RunDetails 渲染 run.evidence/identity；历史运行收进折叠详情；presentation 10 字段 sameInput |
| IR-02 | 续跑消费校验不足 | `runner.py _validate_resume`：摘要相等、轮次界、consumed ⊆ 目录且唯一、未来消费拒绝（initial_consumed 除外）、丢失已提交消费拒绝；rounds 测试含正反例 |
| IR-03 | 项目/引擎/锁身份缺失 | Definition 8 项身份字段参与 `digest=sha256(canonical(asdict))`；rounds 测试 identity isolation 用例 |
| IR-04 | 复制来源语义不明 | `ScenarioPage.tsx` sourceMode 显式；project→copySource undefined（无默认继承）；探针断言 project source undefined |
| IR-05 | READONLY 断言可被 runner 吞 | `test_scenario_persistence.py` `assert_readonly_fault` 在 runner 边界**外**断言 `(True, SQLITE_READONLY, 'SQLITE_READONLY')`；`DisabledReadonly` 负对照使假证据路径必然抛错——首批 42 项假通过未被追认（35 份原件中 readonly-fix 日志已核） |

### 4.2 七项 P3 意见：全部登记沿用，处置不变更

七项（Z-P3-1..4 + M-F01..03）均为非阻断观察，`seven-opinion-dispositions.json`（`65946e21…`）处置与本方源级复核一致：Z-P3-1 initial_consumed 可声明未来轮事件（T01/T00 适配契约，延期）；Z-P3-2 资源选中即完成（PRD E.3 允许的最小私有语义，T06 真实完成条件待接线）；Z-P3-3 封存行哈希方法更正（非缺陷）；Z-P3-4 ignored log/png 经封存 75 成员哈希可追溯；M-F01 `resultLabel` 未按附录 D.1/D.2 区分"已过期"（固定文案"输入版本已变化"，最新运行失败/取消亦标"历史运行"，T00 契约后修）；M-F02 续跑以 `phase='initial'` 语义在 integration-request 未定义（T05 适配风险）；M-F03 逐动作轨迹仅校验三元组唯一性、无同实例 1..k 连续性（T06/T00）。均不要求改动已冻结候选；本方未发现需升级或降级的新证据。

### 4.3 新发现

**在本方完整已读范围内未发现新的 P1/P2。** 该结论不含未执行的运行验证（G-3）；若 root 裁定后补跑出现失败，以新证据为准。源级复核中的非登记性确认：E.2 阶段顺序（infer→events→infer→plan→execute→infer→commit）与提交边界/取消语义、FIFO `(created_round, sequence, id)`、三指标按实际状态统计、受限错误码（不泄原始异常）、T09 投影（含每轮 inputSequence 重置仍与 runner `(sequence,id)` 排序、FIFO W 单调性相容）均与 PRD E.2–E.5 及 fixture 预期一致。

## 5. R1 五项流程失败（NR-01..05）的本方核验

| 项 | 定义（independent-native-receiving-audit） | 本方核验 |
| --- | --- | --- |
| NR-01/P2 | 两方 fixture 通读缺失，M 另缺私有源码内容 | 采纳为历史；本轮本方 14 项全读（含 t09-e5.json 4963 行） |
| NR-02/P2 | 完整 PRD 与原历史日志通读未满足 | 本轮本方 PRD 全本 1255 行 + 33 份日志全读 + 2 PNG 查看 |
| NR-03/P2 | ZCode 明确拒绝后包装执行且报告遗漏首错 | 封存 zcode 链一手核验：拒绝→Write 包装（`call_bcea7d98/call_b24f630a`）→Bash 执行（`call_a6aa655e/call_256fe77e`）；本轮同型拒绝已保全不绕过（§3） |
| NR-04/P2 | MiniMax 原位 probe 违反派发 | 一手核验：`call_01a164ffa8ce7`（bg `ca004736`，exit 0）cwd 仍为固定审查树、脚本 `root=process.cwd()` 致产物落回固定树（逐字节等于封存件不豁免违规）；合规 scratch 重跑 `call_01a165000f4e7` 属事后纠正 |
| NR-05/P2 | MiniMax 为定位收据向父项目做发现性枚举 | 一手核验：`call_01a164fb56917` find 越出本工作树 |

R1 因上述 PROCESS_FAIL 判不通过；其工程结论（含 Z 旧通过与 M 意见）本轮未沿用为任何验证依据，仅作历史对照——本轮为全新完整独立审查。

## 6. 未验证边界（全部保留，不以本轮任何内容关闭）

1. **运行验证**：pytest（46+44 项）、vitest（27 项）、`npm run check`（657 TS / 1142 Py 口径）本轮 UNVERIFIED；R1/M 的历史运行结果不替代本轮验证。
2. **探针**：scratch 探针未重跑（G-4）；两 PNG 仅确认封存历史渲染证据的图像内容。
3. **父功能积压（INV-09..12）**：真实 T05/T06 领域与完整 E.5 四类结果；T01/I04 正式 scenario 生命周期/原子轮次/取消/终态/ack-loss 对账；公共契约/bridge/App 真实挂载与真实数据操作；完整运行依据、T10 跨设备、FR-700..705 父验收、CI、两 OS、真人验收、发布与远端门——全部未验未关闭。
4. **产品边界**：合成 ProbePorts/PersistentProbe 不等于真实领域端口；存储为 Python 内部 API，未暴露 IPC/UI/Agent；正式数据不受场景修改等声明维持原状。

## 7. 最终判定与请求

- **判定：不通过（NotPass / 未完成）**——直接原因是三个必要验证目标因被保全的自动审批拒绝而未执行（G-3），叠加可选探针未跑（G-4）与 G-1/G-2 读覆盖缺口如实登记；源级工程审查完成、IR-01..05 确认关闭、七项 P3 处置沿用、未发现新 P1/P2（§4）。
- **请求 root 裁定**：Mimosa PreToolUse 对 pytest/vitest 执行参数误判为"写源码"的确切根因与恢复条件。裁定恢复后，本方可在同一冻结候选（base 5f / product f9a1157 / reviewHead fdfd908e 不变）补跑三项验证与可选 scratch 探针，出具新证据；若补跑出现失败或受审内容/基线变化，按现行规则重新验证与审查。
- 本报告为 ZCode 方独立结论，不替代 MiniMax M3.1-Flash 方结论；不构成 push/PR/CI/合并许可。
