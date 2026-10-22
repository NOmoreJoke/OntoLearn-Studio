# T11 全新完整同版指定审查报告（MiniMax M3.1-Flash）

> 本报告是候选 `036d7172ddba8502fe81e6e7ce375ce09ef7fa1c` 的**全新完整独立只读审查终态**。由指定模型 M3.1-Flash 在本方独立 worktree 中实际执行产生。未预设通过、未继承上一轮任何 Pass、未修改任何受审实现/测试/配置/依赖，未 stage/commit/push/PR/切分支。结论不构成发布授权，不关闭任何父 T11 发布门。

---

## 0. 终态结论（先行）

| 维度 | 结论 |
| --- | --- |
| **完整工程范围**（受审 56 个 requiredFiles 全文 + 原 25 产品路径按 036 现状 + 4 脚本 + 2 测试 + 2 fixture + 全部评审/证据/历史归档） | **不通过**（发现 1 项中严重度缺陷，见 F-1） |
| 原 18 项原意见 | **17 项可判定关闭、1 项无法验证**（逐项依据见 §7）；原 M NotPass 保留，owner 未自行关闭任何一项，关闭/重开由本审者独立判定 |
| 父 T11 发布门（57 P0 同候选真实联验、双平台安装/签名/公证/渠道、真实模型 API、五真人、Q5 容量、指定双审、push/PR/CI/合并/远端、下载实装） | **无法验证 / 未关闭**，本轮不关闭任何一项 |
| 核验器发布授权 | 恒 `releaseAuthorized:false`（类型层固化 + 实测） |

**不通过的硬因（F-1，中）**：`scripts/release/verify-release.mjs` 的 CLI 在受审树中运行时，**stderr 不是固定错误面**——Node 的 `MODULE_TYPELESS_PACKAGE_JSON` 警告会先于固定错误码输出到 stderr，包含**绝对本地路径**（含本机用户名/工作区路径的 URL 编码形式）。owner 的修复方式是**把测试断言从「整段 stderr 严格相等」放宽为「取最后一行」**（`tests/unit/t11-release.test.ts:1190`），而不是消除警告本身。这与 `docs/release/README.md:15`「无法读取或格式错退出 2」及共同要求「错误只传固定错误码和受限参数，不回传路径」存在口径冲突，且把一次真实首败（`final-expanded-unit.log`、`final-full-check.log`）转成了断言降级而非缺陷修复。

**方向为 fail-closed**（退出码仍为 2、stdout 仍为空、最终错误码仍固定），不产生虚假发布授权；但它是受审实现与自身验收口径的真实不一致，须由唯一 owner 出**新候选**修复并按原门禁重新独立审查。

---

## 1. 任务来源、模型、effort、权限与任务 provenance（实际读回）

| 项 | 实际值 | 读回来源 |
| --- | --- | --- |
| 任务来源 | 用户直接提交本条附件提示（full-prompt.md，26525 bytes，SHA-256 `4ea10d2b76947927ee79d9d4d2faf30d7cd899caed04e8b9b2ca44a1b8cfd0fa`） | 附件本体 + 本方 `.t11-review-runtime/input/full-prompt.md` 逐字节核同 |
| 附件核同 | 附件与本方 input 副本 **sha256 完全相同**（`4ea10d2b…d0fa`），`diff` 无差异，`wc -c` 均为 26525 | `shasum -a 256` + `diff` |
| 会话 ID | `mvs_c2a07cc404db489b9e1e5b32c4686c0a` | `mavis session get --session me` |
| 工作区（实际应用工作根） | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T11-minimax-review-036d7172` | session 元数据 + `pwd` |
| 模型 | `minimax/MiniMax-M3.1-Flash`，variant `thinking` | `mavis session get`（`effective_model` / `model.model_id` / `variant`） |
| 思考等级 | `thinking.effort = xhigh` | 同上（`model.thinking.effort`） |
| 权限模式 | **始终授权 / `bypassPermissions`** | 本方 `metadata/operator-ui-settings-before-send-20261023.json`（UI 收据，`permissionUI=始终授权`、`permissionMenuObserved` 选中指示）；**未读全局配置、agent list 或日志** |
| turn / stream ID | 本运行时 `session get` 不暴露 turn/stream 标识，**未获得即不记录**，不编造 | — |
| 准备阶段实际收据 | `operator-ui-settings…json` 记录 `taskCreated:false`、`sessionId:null`、`actualBackendScalarUntilOwnNativeReadback:"UNKNOWN"`；**本次为该记录之后新创建的独立任务**，实际模型/effort/权限由上表实际读回给出，非默认配置推定 | 同上 + `session get` |

模型、effort 与指定值一致；权限以本方 UI 收据为准，且已在本任务实际读回模型/effort。

---

## 2. 受审输入身份与漂移核验（全部实测）

| 项 | 值 | 核验结果 |
| --- | --- | --- |
| review HEAD | `036d7172ddba8502fe81e6e7ce375ce09ef7fa1c` | detached，`git rev-parse HEAD` 一致；**未切分支** |
| 工作树改动 | 仅 ` M AGENTS.md` ＋ 未跟踪 `.t11-review-runtime/` | 与提示一致；`git diff 036d7172 --name-only` **仅 AGENTS.md** |
| AGENTS.md | 实体 15147 bytes / sha256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` | 与 `operator-ui-settings` 的 `guideSha256`、`source-setup.json` 的 `currentGuideSha256` **三方一致**；HEAD 内 blob 为 `f3876f66…`（1056 bytes），差异为已声明的政策差异，保持未暂存 |
| 受控 892 文件 | `metadata/source-setup.json` 列 892 条 = `git ls-tree -r 036d7172` 的 892 条，**无多无缺** | 实测：逐条 `gitBlob` 与 `git ls-tree` 一致；逐条物理 SHA-256 与记录 `physicalSha256` 一致；**独立复核**（不依赖该 metadata，直接 `git cat-file blob` 对比工作树实体）亦仅 AGENTS.md 1 处差异 |
| 56 个 requiredFiles | `handoff-manifest.json` 声明 56 条，实际 entries 56 条 | **逐条实测字节数与 SHA-256 全部相等，0 mismatch / 0 missing** |
| 批准 873 Git 对象 | `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` | 对象存在；`git show` 取 manifest 实测 sha256 = `aaaef2c0…ac39e`，17 文件，version `prd-v0.6-learning-1`，PRD sha `7586b2c4…f60fbb` — **与 `APPROVED_BASELINE` 常量逐字一致** |
| 873 的 17 文件 | 逐文件 `git show` 实算 sha256 与 manifest 记录比对 | **17/17 全部匹配** |
| PRD 本树实体 | `docs/prd/PRD-本体学习与落地Agent工作台.md` sha256 = `7586b2c4…f60fbb` | 与批准 PRD SHA 一致 |
| 依赖环境 | 本树自带 `node_modules`（非符号链接）与 `.venv`（非符号链接）；node v24.15.0 / npm 11.12.1 / uv 0.11.12 | 未采用原开发树或 peer 可变环境 |
| TMPDIR/TMP/TEMP | 全部指向 `.t11-review-runtime/tmp` | 本轮全部测试/解包/探针均在其下 |
| 本轮 Git 终态 | HEAD 仍 `036d7172…`，`git diff --cached --stat` 为空 | **无 stage / commit / push / PR / 切分支；未修改任何受审文件** |

### 2.1 PRD 事实独立复算（不依赖被审代码）

| 事实 | 本审者独立解析结果 | 与工具口径 |
| --- | --- | --- |
| P0 条款数 | **57**，且 57 个 ID 全部唯一 | 与 `verify.ts` 正则口径一致 |
| G.1 表项 | **37** 个 `X-NN` ID | 一致 |
| G.4 列表项 | **13** 条 | 一致 |
| G 合计 | **50** | 一致 |
| T09 `coverage.json` | 50 条目；ID 集合与 PRD 派生集合**完全相等**；每条 `source` 原文与 PRD 对应行/条**逐字相等（0 mismatch）**；每条 source 均字面出现在 PRD 中 | 与 `COVERAGE_SOURCE`/`COVERAGE_PRD` 逻辑一致 |
| T09 `cases.json` | 50 条，ID 集合 = coverage ID 集合；指针 case 恰为 `G-list-01`/`G-list-02`/`G-list-06`（exact×2 + replay×1） | 与 `CASE_POINTER` 逻辑一致 |

---

## 3. 全部 56 个 requiredFiles 覆盖表（逐项已读；实体与字节全部核验）

字节/SHA-256 全部与 `handoff-manifest.json` 相等（0 mismatch）。审读深度：除两个二进制归档外全部**全文阅读**。

| # | 路径 | 字节 | SHA256(前16) | 审读 | 结论 |
| --- | --- | --- | --- | --- | --- |
| 1 | `docs/iterations/T11/acceptance.md` | 4320 | `c83f90adb026c9cb` | 全文 | 探针/默认4 skip 边界、v3 修复说明、双审要求成文且与实现一致；验收条件**未被削弱**（见 §5 对比 7d28 diff） |
| 2 | `docs/iterations/T11/selection-comparison-v2.md` | 2625 | `03dd36b5cc3493cf` | 全文 | 历史 v2 规范保留；现行核验器**拒绝** v2（`format` literal） |
| 3 | `docs/iterations/T11/selection-comparison-v3.md` | 2569 | `3da1af492bf268ac` | 全文 | v3 口径与 `snapshotSchema`/`superRefine` 逐条对应；明写「不作 F01 新模板范围决定」 |
| 4 | `docs/iterations/T11/shared-file-handoff.md` | 9781 | `d160bb0db14d867a` | 全文 | 共享文件提案，未旁路唯一配置；T03/T01 责任路由 |
| 5 | `docs/release/README.md` | 9619 | `890680a0d220103c` | 全文 | freeze 字段、exit 语义、v3/Q9/profile 口径与实现一致；**F-1 相关**（§45「无法读取或格式错退出 2」未说明 stderr 前置警告） |
| 6 | `docs/release/migration-recovery.md` | 6029 | `d5ac30d8a4426d9b` | 全文 | v3 必含字段、22 项迁移 check、两项回退 check 均具名成文 |
| 7 | `docs/release/target-device-runbook.md` | 4648 | `29fda85e9e91d736` | 全文 | 11 步真机规范；明示 collector 不替代原生操作 |
| 8 | `docs/release/user-observation-template.csv` | 647 | `c2229f58febf8c76` | 全文 | 28 列、5 空行、未预填 |
| 9 | `docs/release/user-study.md` | 5463 | `fb279ddd6d06451e` | 全文 | 八步/迁移/辅助分记口径与实现一致；**F16 明确保留待决**（未代答） |
| 10 | `docs/reviews/T11/approved-fixed-baseline-probe.json` | 3833 | `614236667b67a576` | 全文 | 873 固定输入许可、17 文件 SHA、默认 skip 边界登记完整；其 `fixedInputTestsSkippedWithoutFlag:3` 属**旧 7d28 候选**历史计数（现候选为 4，见 status.md:7 已注明） |
| 11 | `docs/reviews/T11/blocked-audit.json` | 3726 | `e7ad460e2dfc8e7d` | 全文 | Goal blocked、releaseLimitations 五项如实；不含越权声明 |
| 12 | `docs/reviews/T11/completion-audit.md` | 8059 | `d8e16dbe757254bc` | 全文 | 逐门未完成清单；旧基线为历史标注 |
| 13 | `docs/reviews/T11/external-review-permissions-receipt.json` | 1722 | `bd354b1349ddbbed` | 全文 | 权限政策接收，只读边界保留 |
| 14 | `docs/reviews/T11/first-failure.json` | 603 | `2d6b63f58d2cbdb9` | 全文 | 首跑 38 仅摘录+transcript，**明确不冒充完整 raw** |
| 15 | `docs/reviews/T11/format-public-ownership-receipt.json` | 3070 | `83b90c71558f7223` | 全文 | 责任路由文档，无实现变更 |
| 16 | `docs/reviews/T11/format-python-ownership-receipt.json` | 2533 | `ce7d76cff33e50de` | 全文 | 同上 |
| 17 | `docs/reviews/T11/internal-review.md` | 2781 | `ab5f4815eaf6f7e3` | 全文 | 历史内审 5 项处置，不替代指定双审 |
| 18 | `docs/reviews/T11/minimax-received-20261023/index.json` | 2167 | `884be1fb2ab7aadc` | 全文 | 上一轮 M 收件索引，原字节保留 |
| 19 | `docs/reviews/T11/minimax-received-20261023/minimax-report-original.md` | 50693 | `272914fff1189ac7` | 全文（321 行，4 段读完） | 上一轮 M NotPass 原报告：F-A～F-L 十二项，**本轮据此逐项复判**（§7） |
| 20 | `docs/reviews/T11/minimax-received-20261023/owner-reception.md` | 2263 | `861a1961cc6454ce` | 全文 | 收件链如实；不成立双 Pass |
| 21 | `docs/reviews/T11/operating-policy-receipt.json` | 4177 | `b94083ae09b6488a` | 全文 | 政策哈希匹配；多代快照各自保留 |
| 22 | `docs/reviews/T11/owned-fixes-20261023/disposition.json` | 7647 | `f0084b9120d59ac5` | 全文 | **18 项全部 `status:"open"`、`closedByOwner:0`**、M NotPass 保留、owner 不自行降级——处置权正确留给本审者 |
| 23 | `docs/reviews/T11/owned-fixes-20261023/handoff.md` | 3160 | `bb1a4513361f7f92` | 全文 | 交接说明；明确未运行真实目标、未认证测试日志 |
| 24 | `docs/reviews/T11/owned-fixes-20261023/history-archive-verification.json` | 569 | `5213765318937bed` | 全文 | 48 成员只读核验声明；本审者**独立重做**，结论一致 |
| 25 | `docs/reviews/T11/owned-fixes-20261023/independent-implementation-review.md` | 12461 | `e65b131367df07f3` | 全文 | 内审 R1 与 338 delta 复核；非指定双审 |
| 26 | `docs/reviews/T11/owned-fixes-20261023/index.json` | 1555 | `f7183190efa9f10c` | 全文 | 本包 7 文件哈希登记，与实体一致 |
| 27 | `docs/reviews/T11/owned-fixes-20261023/raw-logs-index.json` | 2583 | `f8eac7fab92ef094` | 全文 | 14 条目索引 |
| 28 | `docs/reviews/T11/owned-fixes-20261023/raw-logs.tar.gz` | 2825 | `2e714950bfcba075` | **二进制：全部成员逐条核字节+hash** | 14 成员全部匹配，**0 mismatch**；已读失败日志（见 §5.3） |
| 29 | `docs/reviews/T11/owned-fixes-20261023/verification.json` | 6428 | `31cfc3a7c9c3356c` | 全文 | 命令/计数/失败保留登记；`failuresPreserved` 如实含 2 失败与 1 格式失败 |
| 30 | `docs/reviews/T11/q9-decision-source-20261023.json` | 919 | `60f919f93e7ad549` | 全文 | Q9 批准来源 SHA `def9817d…d84a7` 与 `APPROVED_MODEL.decisionSha256` **一致**；Base URL 与具体 route 分列 |
| 31 | `docs/reviews/T11/recovery.json` | 2685 | `7834b2fea3d148a4` | 全文 | 旧 7d28 恢复入口（历史） |
| 32 | `docs/reviews/T11/round-1/history-disposition.md` | 4001 | `ec168ba3b50adab9` | 全文 | 12 项历史处置；首 38 无完整 raw 已声明 |
| 33 | `docs/reviews/T11/round-1/raw-logs-index.json` | 8660 | `5b959f4c8b644f63` | 全文 | 48 条目索引 |
| 34 | `docs/reviews/T11/round-1/raw-logs.tar.gz` | 7208 | `c1f34bd3d6085f9e` | **二进制：全部成员逐条核字节+hash** | 48 成员全部匹配，**0 mismatch**，合计 73704 bytes 与索引一致 |
| 35 | `docs/reviews/T11/selection-v2-review.md` | 2402 | `dea7c2d6064a21ff` | 全文 | v2 内审，不替代指定双审 |
| 36 | `docs/reviews/T11/status.md` | 14344 | `374aed38f359937e` | 全文 | 新 dated 入口取代历史 active/current；首 38 raw 缺口已分列；18 项 open |
| 37 | `docs/reviews/T11/t09-readonly-alignment.json` | 617 | `038b9e851ff65294` | 全文 | 17/50/3 指针登记 |
| 38 | `docs/reviews/T11/triage-20261023/collector-and-io-independent-analysis.md` | 1545 | `82970b1f5a16ab04` | 全文 | Z 六项 + M collector 边界静态结论 |
| 39 | `docs/reviews/T11/triage-20261023/evidence-index.json` | 8331 | `23b571a8127a4c7b` | 全文 | 证据索引 |
| 40 | `docs/reviews/T11/triage-20261023/independent-plan-review.md` | 1260 | `5ec05f655328af37` | 全文 | 计划一致性复核 |
| 41 | `docs/reviews/T11/triage-20261023/index.json` | 1099 | `ac078b642cc9350b` | 全文 | 18 triaged / 0 closed |
| 42 | `docs/reviews/T11/triage-20261023/matrix.json` | 18299 | `ce990f9fde01cd54` | 全文 | **18 项原意见全表**（M 12 + Z 6），原严重度与 NotPass 全保留 |
| 43 | `docs/reviews/T11/triage-20261023/repair-plan.md` | 14848 | `60324616ab88010f` | 全文 | W1–W6 最小计划 |
| 44 | `docs/reviews/T11/verification.json` | 8857 | `0cb03592bcde2f0f` | 全文 | **旧 7d28** 65/695/1052 与 48 日志登记（历史） |
| 45 | `docs/reviews/T11/zcode-received-20261023/index.json` | 1914 | `00afdd85647d2efd` | 全文 | 上一轮 Z 收件索引 |
| 46 | `docs/reviews/T11/zcode-received-20261023/owner-reception.md` | 2376 | `816a9ff155165fe0` | 全文 | Z 工程 Pass 未被采纳为双审 |
| 47 | `docs/reviews/T11/zcode-received-20261023/zcode-report-original.md` | 29056 | `6e82553c693678e2` | 全文（183 行） | 上一轮 Z 报告：工程范围 Pass + P4×6，**本轮据此复判 Z 六项**（§7） |
| 48 | `scripts/release/collect-macos.sh` | 3484 | `195d8561098b3a28` | 全文 71 行 | **Z-F4 已关闭**：全部外部命令绝对路径（含 `/usr/bin/uname`、`/usr/bin/sw_vers` 最前门、`/usr/bin/xcrun`）；pending/step/failed/有限 exit/首 raw 保留/新目录防覆盖/末尾 complete 齐备 |
| 49 | `scripts/release/collect-windows.ps1` | 4740 | `cc572372e657fc34` | 全文 93 行 | 步骤/失败状态/first raw 分离保留；调用 `pe-machine.ps1`；**仅静态，无 pwsh** |
| 50 | `scripts/release/pe-machine.ps1` | 1270 | `62b8f743a95311bb` | 全文 28 行 | **Z-F5 已关闭**：DOS≥64 字节、`e_lfanew` ∈ [64, length-6]、MZ/PE 签名/machine 字段、`finally` 关闭 reader+stream、固定 `PE_INVALID` |
| 51 | `scripts/release/verify-release.mjs` | 916 | `6d1e4b81aa622d15` | 全文 23 行 | **F-1 所在**：见 §6 |
| 52 | `scripts/release/verify.ts` | 38220 | `c3e670e66594af4a` | 全文 1075 行 | 主实现；逐条审，见 §4 |
| 53 | `tests/fixtures/release/comparison.json` | 2578 | `f4ace4230de54844` | 全文 | v3 样例（`format=t11-comparison-v3`、`comparisonCase=g6-conflict`） |
| 54 | `tests/fixtures/release/synthetic-profile.json` | 348 | `654965c87ff3f26e` | 全文 | 合成身份声明清晰 |
| 55 | `tests/unit/t11-release-io.test.ts` | 5407 | `d1aa4c918f892116` | 全文 126 行 | 同 fd/限额/增长/短读/异常关闭/非 regular/外部 symlink/叶替换/PE/koly 覆盖齐备 |
| 56 | `tests/unit/t11-release.test.ts` | 45714 | `561b8eedaab8a22f` | 全文 1209 行 | 109 用例（含 4 项固定输入探针），断言到具体错误码 |

**未抽样**：56 条全部逐一读取并核 hash；两个二进制归档核全部成员字节与 hash 并阅读失败日志；未只审 `verify.ts`；未删除 Windows collector；未改 acceptance 条件取 Pass。

---

## 4. 独立技术审查：实现级判定

### 4.1 已实测成立的关键能力

| 能力 | 判定依据（本审者亲跑/亲构造） |
| --- | --- |
| **严格 schema + 未知字段拒绝** | `manifestSchema`/`expectedSchema` 全部 `.strict()`；`verifyManifest({...m, publish:true})` → `MANIFEST_SCHEMA`（单测覆盖）；**14 组自建反例全部按预期错误码拒绝**（§4.2） |
| **同 fd 限额读取** | `withFile()`：open 后 `fstat` → 普通/非空/限额判定 → **先限额后 Buffer 分配与 parse** → 同一 fd 有界读取+hash+PE/koly → 追加字节与元数据漂移复查 → `finally` 关闭。普通 16MiB、大文件 8GiB，`readJsonFile` 先限额后 `JSON.parse` |
| **增长/短读/非 regular/读错误** | 8 项 IO 单测 + 本审者缺 873 对象实测（4 项 fail，非 skip） |
| **路径/叶 symlink 与祖先前提** | `boundPath` 拒绝对路径/`\`/`..`/`.`；`realpath` 后 `relative` 必须落在根内；`O_NOFOLLOW|O_NONBLOCK`；祖先目录可信稳定前提**已在 README:43 明示且未宣称消除全部 TOCTOU** |
| **双平台资产/版本/架构/构建输入/两锁/组件/渠道** | WIN/MAC 各自 artifact+download 同 hash；`${label}_ARCH/VERSION/FORMAT/BUILD_SHA/BUILD_INPUT/LICENSE_COVERAGE/CHANNEL_*` 全覆盖；Mac 额外 `MAC_NOTARIZATION`（hardenedRuntime+notarized+stapled） |
| **结构标记 ≠ 签名链** | PE/koly 仅结构；签名 `valid` 为声明级并绑定签名报告；README:35/45 明示不证明签名可信 |
| **57 P0 + G50 + E.5 指针** | 独立复算 57/50，coverage↔PRD 逐字对应，3 指针真实展开；`PRODUCT_EXPECTATION_BASELINE` 把产品 expected 绑回 T09 唯一 manifest |
| **RDF 仅完整 SPO 无序、保重复数；其余保序** | `compareProductComplete` 仅对 `facts/assertedFacts/inferred/addedTriples/inputs` 且元素为完整三元组时排序；重复数保留；events/trace/rounds 严格保序（单测断言） |
| **v3 只读投影/唯一 id/完整 payload** | `rows` 唯一 id + payload 非空且非 count 摘要；`superRefine` 校验 selection/dependencies/三能力独立、未选内容必须空、模板边界 |
| **PRD1252 模板拒恢复** | `TEMPLATE_NOT_RESTORABLE`（facts 或 ownership 空即拒）——与 PRD G.6 第 1252 行「不含当前断言事实或来源所有权元数据的包只能标记为模板包，不得承诺恢复当前项目状态」一致；**不代答 F01**（v3 文档自述） |
| **两正式方向固定 g6-conflict、六层非空、22 迁移 check** | `migrationComparisonCases` 两向 `literal('g6-conflict')`；`expectedSchema` 强制；降级 → `EXPECTED_IDENTITY` + `MIGRATION_BEFORE_CASE` |
| **旧 v2 拒绝不转换** | `format: literal('t11-comparison-v3')`；v1/v2 → `RECOVERY_RESTORED_SCHEMA` |
| **零提交可重放 / 未选不泄漏** | `canReplay` 不以 rounds 为前提；`UNSELECTED_CONTENT` 覆盖 5 类未选内容（history/rounds/derived/rawSources/agentSessions/undo） |
| **双平台上一版独立 pin + 两项回退 check** | `previousAssets` 外部 pin；旧资产版本/sourceSha/hash 三重绑定、禁止复用当前包；`rollback-retain-new-version-copy`、`rollback-refuse-incompatible-format` 在 recovery **与每个**旧资产报告中**均具名强制** |
| **双 collector 完整** | Mac 绝对路径齐备（含最前 OS/arch 门）；Windows PE 边界与 finally 关闭；缺/pending/failed/malformed marker 全拒；`collector-complete` 与 `installed-components-match-package` 绑定独立预期/实际包 hash |
| **Q9 路由 pin** | `APPROVED_MODEL` 常量 + `expected` 双向 pin + 批准来源 SHA `def9817d…d84a7`；**任意 URL/模型即使两边同 tuple 仍拒**（实测 `MODEL_PROFILE_DRIFT`）；Base URL 误填 route 亦拒 |
| **五真人/80%/八步/辅助分记** | users ≥5 唯一 id；`human && !developer && ontologyNovice`；`core&&transfer` 矛盾拒；`product-hints` 计入完成但 `transferIndependent` 须独立；Agent 代做不得标独立；`agentFullCounterexample` 必须为真 |
| **CLI 永不放行** | `releaseAuthorized:false` 为返回类型字面量，代码层不可能输出 true；synthetic 一致 → exit 1；非法 → exit 2；stdout 空 |
| **检查清单未被削弱** | 对比 7d28→036：`DEVICE_CHECKS` 24→26（**+2，REMOVED=[]**）、`RECOVERY_CHECKS` 6→8（**+2，REMOVED=[]**）、`ENGINEERING_CHECKS` 15→15、`MODEL_CHECKS` 13→13、`MIGRATION_CHECKS` 22→22 **全部原 check 无一删除** |
| **T11 未另造 Store/项目包/恢复器** | `git diff 692077da..036d7172 -- packages/ apps/` **为空**；engine/desktop 零改动 |

### 4.2 本审者自建 14 组独立对抗探针（不复用仓内 fixture 断言）

自建独立 fixture（重新构造合成 manifest/evidence），逐条注入并核对**具体错误码**：

| # | 注入 | 期望错误码 | 实测 |
| --- | --- | --- | --- |
| 1 | 基线（无注入） | — | consistent=true, issues=[] ✔ |
| 2 | G.6 迁移快照清空 definitions | `MIGRATION_BEFORE_SCHEMA` | ✔ |
| 3 | current-state 恢复 facts 置空（模板） | `RECOVERY_BACKUP_SCHEMA` | ✔ |
| 4 | 迁移 case 降级为 current-state | `MIGRATION_BEFORE_CASE` | ✔ |
| 5 | 未选历史夹带 | `MIGRATION_AFTER_SCHEMA` | ✔ |
| 6 | collector marker 为 pending | `WIN_COLLECTOR_INCOMPLETE` | ✔ |
| 7 | 回退资产复用当前包 | `ROLLBACK_IDENTITY_PIN` | ✔ |
| 8 | restoreCurrent=true 但 ownership 空 | `RECOVERY_BACKUP_SCHEMA` | ✔ |
| 9 | 任意模型 endpoint（两边同填） | `MODEL_PROFILE_DRIFT` | ✔ |
| 10 | 回退报告缺 retain-new-version-copy | `ROLLBACK_windows11-x64_COVERAGE` | ✔ |
| 11 | evidence 模式 + 合成基线 | `BASELINE_APPROVED_PROFILE` | ✔ |
| 12 | 同包声明 packageSha256 漂移 | `WIN_PACKAGE_SOURCE` | ✔ |
| 13 | 无源却宣称可重跑映射 | `MIGRATION_AFTER_SCHEMA` | ✔ |
| 14 | 无输入却宣称可重放 | `MIGRATION_AFTER_SCHEMA` | ✔ |

**14/14 全部按预期拒绝，无一组产生虚假放行。**

### 4.3 本审者独立发现的能力边界（不构成缺陷，但须登记）

- **构建锁/配置身份未结构化 pin**：`build.nodeLock/pythonLock/config` 仅按 `ref` 读并验 hash（`verify.ts:730`），**未约束其路径必须是 `package-lock.json`/`uv.lock`/唯一 builder 配置**。本审者实测：把这三项指向任意自造文件后 `verifyManifest` 仍 `consistent=true`。此为 7d28 起的既有边界（非本轮引入），且 `build.sourceSha` 已与候选绑定、锁内容由外部 freeze 的 `expectedResults` 逐项 pin，属**声明级而非结构级**约束。登记为低优先级边界，不阻断本轮，但建议后续把锁路径纳入结构校验。
- **工程限额不作 Q5**：README:43 已明示 16MiB/8GiB 是工具工程边界，**未**充当业务容量门。

---

## 5. 本轮实际执行的检查（原始结果保全）

cwd 均为本 worktree 根；TMPDIR/TMP/TEMP 指向 `.t11-review-runtime/tmp`；未运行产品；未读 peer 本轮任何文件。

| # | 命令 | exit | 实际结果 | 日志（sha256前16 / bytes） |
| --- | --- | --- | --- | --- |
| C1 | `npm run check` | **0** | lint/format/typecheck/build/ruff 全过；**vitest 17 files / 735 passed \| 4 skipped (739)**；**pytest 1052 passed** | `rev-01-npm-check.log` `1f061dc6612eec42` / 5092 |
| C2 | `T11_FIXED_BASELINE_PROBE=1 npx vitest run tests/unit/t11-release.test.ts tests/unit/t11-release-io.test.ts` | **0** | **109 passed / 0 skipped**（4 项固定输入探针全部实跑） | `rev-02-fixed-probe.log` `f089b9d93dffd74a` / 220；复跑 verbose `rev-07-fixed-probe-verbose.log` / 17188，同为 109/109 |
| C3 | 默认模式（无 flag） | 0 | **105 passed \| 4 skipped (109)**；verbose 逐条确认 4 项 skip 全部是固定输入探针 | 同 C2 目录 |
| C4 | `T11_FIXED_BASELINE_PROBE=1 npm run check` | **0** | **vitest 739 passed（0 skipped）**；pytest 1052 passed；构建、ruff 全过 | `rev-05-check-with-probe.log` `69b8473adfd5fd3e` / 5080 |
| C5 | `npx eslint --no-ignore scripts/release/verify.ts scripts/release/verify-release.mjs` | 0 | 无问题 | `rev-03-release-scoped.log` `cc9255d7e1508f93` / 659 |
| C6 | `npx prettier --ignore-path /dev/null --check <release 全集>` | 0 | All matched files use Prettier code style | 同上 |
| C7 | `bash -n scripts/release/collect-macos.sh` | 0 | 语法通过（**未执行采集**） | 同上 |
| C8 | `npm run verify:sources` | 0 | 已核对 12 个归档源文件 | 同上 |
| C9 | 显式探针但 873 对象不可取（`GIT_DIR`→空仓库） | **1** | **4 failed / 96 passed**，失败原因明示 `git show 873:...` 不可得；**无 live HEAD 替代** | `rev-04-missing-873.log` `1fcce228519ccca1` / 4861 |
| C10 | 自建 14 组对抗探针（§4.2） | — | 14/14 按预期错误码拒绝 | `rev-06-adversarial.json` |
| C11 | 归档核验（round-1 48 + owned-fixes 14） | — | **48/48 与 14/14 逐成员字节+SHA-256 全匹配，0 mismatch**；round-1 合计 73704 bytes 与索引一致 | 本审者 python 核验实录 |
| C12 | 独立复算 PRD 57/50、coverage↔PRD 逐字对应、873 的 17 文件 hash | — | 全部吻合（§2.1） | 本审者 python 核验实录 |
| C13 | Mac collector 目标门实测（macOS 27.0.1，非 15） | **1** | `TARGET_REQUIRED: macOS 15 arm64`，**未创建任何输出目录**（平台门先于 mkdir，正确） | 本审者 shell 实录 |

**owner 计数与本审者亲跑的区分**：owner 在 `verification.json` 声称的 109 专项、739 TS、1052 Python、显式 lint/format、bash-n — 本审者**独立复跑得到相同结果**（C1–C8），故这些数字**可由本轮验证支持**。owner 的 105/735 是中间 640cf 结果（status.md:7 已限定），owner 的首败/后继记录本审者**从归档独立核对**而非采信自述（§5.3）。

### 5.3 历史失败原件（归档内）——本审者独立核对

| 原件 | 实测内容 | 与文档一致 |
| --- | --- | --- |
| `round-1/unit-third-run.log` | **40 failed (40)** 原件 | ✔ 历史失败保留 |
| `round-1/check-first-run.log` | TS2305「no exported member 'DEVICE_CHECKS'/'digest'/…」声明缺失失败原件 | ✔ |
| `round-1/check-second-run.log` | **8 failed / 662 passed**，`.venv/bin/python` ENOENT | ✔ |
| `round-1/unit-second-run.log` | **38 passed (38)**（修复后），**非首跑失败** | ✔ 与「首38只有摘录/transcript」不冲突 |
| 首跑 38 失败完整 raw | **归档 48 成员内 grep「38 failed」零命中** | ✔ 缺口确认 |
| `owned-fixes/final-expanded-unit.log` | **2 failed / 107 passed**，Node 警告抢先导致 stderr 断言失败 | ✔ **F-1 的直接证据** |
| `owned-fixes/final-full-check.log` | **2 failed / 737 passed**（同因），未从该失败 run 声称 build/Python 成功 | ✔ |
| `owned-fixes/cli-assertion-repaired-{unit,full-check}.log` | 109/109 零 skip；739 passed / 1052 passed | ✔ |
| `owned-fixes/independent-report-first-format.log` | 报告首次 format exit 1 | ✔ |

**首 38 缺口**：本审者独立 grep 确认归档内无「38 failed」完整 raw；`first-failure.json` 自述「full output retained in tool transcript, not represented here as full raw log」，status.md:11 已分列。**未以重跑补造首失败，未宣称永久不可得。**

### 5.4 未运行 / 无法验证边界（逐项如实保留）

| 项 | 状态 | 阻断影响 |
| --- | --- | --- |
| Windows collector 运行 | **未运行**（本机无 pwsh；仅静态审阅） | 无法验证 PowerShell 运行时行为、`Get-AuthenticodeSignature` 真实读取、PE helper 真实执行 |
| Mac collector 成功路径 | **未运行**（本机 macOS 27.0.1 非目标 15 arm64；目标门实测 exit 1 且未建目录） | 无法验证 codesign/spctl/stapler 真实输出与失败保留行为 |
| 目标设备安装/native/凭据/恢复/双向迁移 | **未运行** | DEVICE_CHECKS 26 项无任何真实设备证据 |
| 真实签名/公证/ticket/最终渠道与下载实装 | **未执行** | 签名链真实性不可证；渠道同 hash 仅合成样例 |
| 真实模型 API 评估 | **未调用** | 模型档位/零伪造仅结构校验 |
| 五真人 80% 研究 | **未执行** | 真人资格与记录真实度不可证 |
| T03 真实唯一包内成员/安装解包来源 | **未验** | `installed-components-match-package` 仅核声明与引用字节；真实同包关系须原件对照 |
| 完整 57 P0 与 C–G/10–12 同候选真实联验 | **未执行** | 领域行为未由本工具证明 |
| 1000 轮/每轮 1000 动作、已提交轮次不可变、未完成轮回滚、取消与响应丢失 | **未由本工具验证** | 属 PRD 领域语义，非本次离线核验器职责；不得以合成 fixture 说领域已验 |
| Q5 批准容量与测量 | **未做** | 工程限额不作 Q5 |
| 指定双审（GLM-5.3/最高） | **本报告仅为 M3.1-Flash 一方终态** | 双审门未关闭 |
| push/PR/实际 CI/正常合并/远端/下载实装 | **未执行** | 发布链路门未关闭 |
| e2e / install-electron / package:dir | **未授权未执行** | 非打包验收 |
| 真实 freeze 独立性 | **无法由工具证明** | freeze 不由清单作者自填属流程控制项，README:35 已声明 |

**工具能力边界**：报告签发者身份、签名人/证书链真实性、真人资格与真实操作、原始报告真实性、组件清单是否由实际包与固定依赖图得出 — 均不可由本工具证明，README:35/45 已如实声明。

---

## 6. 发现清单（级别 / 路径行号 / 反例触发 / 影响 / 依据 / 建议）

### F-1【中】CLI 的 stderr 不是固定错误面：Node 模块类型警告抢先输出并泄露绝对本地路径；修复方式为放宽断言而非消除成因

- **位置**：`scripts/release/verify-release.mjs:16`（CLI 入口 `import { expectedSchema, readJsonFile, verifyManifest } from './verify.ts'`）；`scripts/release/verify.ts:1-5`（被导入的 `.ts` 使用 ESM 语法）；根 `package.json`（**无 `"type"` 字段**，实测 `grep -c '"type"' package.json` = 0）；受影响断言 `tests/unit/t11-release.test.ts:1190`。
- **反例触发（本审者亲跑，可复现）**：
  ```
  node scripts/release/verify-release.mjs /nonexistent-manifest.json /tmp /nonexistent-freeze.json
  ```
  实际 stderr（625 bytes，5 行）：
  ```
  (node:94353) [MODULE_TYPELESS_PACKAGE_JSON] Warning: Module type of file:///Users/kyle/Documents/%E5%B7%A5%E4%BD%9C/%E7%9F%A5%E7%88%BB/%E6%9C%AC%E4%BD%93/.worktrees/T11-minimax-review-036d7172/scripts/release/verify.ts is not specified and it doesn't parse as CommonJS.
  Reparsing as ES module because module syntax was detected. This incurs a performance overhead.
  To eliminate this warning, add "type": "module" to /Users/kyle/.../package.json.
  (Use `node --trace-warnings ...` to show where the warning was created)
  MANIFEST_OR_FREEZE_UNREADABLE_OR_INVALID
  ```
  exit=2、stdout 为空（0 bytes）——**方向 fail-closed**，但 stderr 额外含工作区绝对路径（URL 编码形式）与运行环境细节。
- **影响**：
  ① 违反「跨边界只传固定错误码和受限参数，不回传原始异常、堆栈、路径」的固定错误面要求——stderr 泄露本地绝对路径与本机目录结构；
  ② `docs/release/README.md:15` 与 `acceptance.md` 描述的「无法读取或格式错退出 2」未披露 stderr 会附带运行时警告，读者按文档核对 stderr 会误判；
  ③ **owner 的修复是断言降级**：首败日志 `owned-fixes/final-expanded-unit.log` 显示新断言原为 `expect(run.stderr.trim()).toBe('MANIFEST_OR_FREEZE_UNREADABLE_OR_INVALID')`（整段严格相等），修复后改为 `expect(run.stderr.trim().split('\n').at(-1)).toBe(...)`（**只取最后一行**）。这使断言无法再发现「固定错误之前混入其他内容」这一类回归；
  ④ 上一轮 M 报告 §5.2 曾记录「错误输出固定文案，不回显敏感内容（测试断言 stderr 不含原文）」；本轮该性质已弱化为「最后一行是固定文案」。
- **依据**：本审者亲跑 CLI（stdout 0 bytes / stderr 625 bytes / exit 2）；owner 归档首败与后继日志 `final-expanded-unit.log`、`final-full-check.log`、`cli-assertion-repaired-*.log`；`owned-fixes/verification.json` 的 `failuresPreserved` 自述「New CLI assertion expected all stderr equal error code; existing Node MODULE_TYPELESS_PACKAGE_JSON warning precedes fixed final error. Exit2 was correct」——**owner 已准确登记事实，但把处置定为改断言**；根 `package.json` 无 `"type"` 字段为客观成因。
- **建议（由唯一 owner 出新候选处理，本轮不自行修复）**：任一即可，须同步测试与文档——
  ① 在 CLI 入口消除警告来源（例如由唯一配置维护者确认后于根 `package.json` 增加 `"type": "module"`，或让 CLI 以不触发重解析的方式加载 `.ts`），恢复 `expect(run.stderr.trim()).toBe('MANIFEST_OR_FREEZE_UNREADABLE_OR_INVALID')` 的整段严格断言；或
  ② 若必须在当前 Node/配置下保留警告，则在 `verify-release.mjs` 内自行抑制该特定警告并**显式声明**「stderr 可能含 Node 运行时警告」，同时把断言改为「stderr 不含敏感/输入内容」而非仅看最后一行，并在 README:15 同步披露。
  修复后须重跑显式专项 109 与全仓 check，并按原门禁重新独立审查。

> **本轮无其他级别缺陷**：未发现任何可导致虚假发布授权的路径；14 组自建反例全部拒绝；`releaseAuthorized:false` 在返回类型层固化。

---

## 7. 全部 18 项原意见逐条处置（保留原严重度；关闭/重开/无法验证由本审者独立判定）

原矩阵 `triage-20261023/matrix.json`（18 项）与 owner `disposition.json`（全部 `open`、`closedByOwner:0`、M NotPass 保留）均已全文读取。owner 未自行关闭或降低任何严重度，处置权按门禁留给本审者。

### 7.1 M 原 12 项

| 原项 | 原严重度 | 本轮判定 | 依据（036 现状 + 本审者亲验） |
| --- | --- | --- | --- |
| **M-F-A** 比较投影六层非空口径冲突 | 高 | **关闭** | 已改为 v3 显式 `comparisonCase`：`superRefine` 仅在 `g6-conflict` 时强制六层（`verify.ts:964-970`），通用 current-state 允许合法空 definitions/mappingState/queries/results；模板边界由 `TEMPLATE_NOT_RESTORABLE`（facts/ownership 必非空）保留；两正式方向由 `expectedSchema.migrationComparisonCases` 固定 `literal('g6-conflict')`。文档 `selection-comparison-v3.md`、`README.md:25`、`migration-recovery.md:21` 与实现一致，**冲突表述已消除**。自建探针 #2/#3/#4/#8 全部按预期拒绝。原冲突文档 `README.md:25` 旧句已被替换，无残留双口径 |
| **M-F-B** 端点/模型无批准依据 | 中 | **关闭** | 已固定具体 route `https://api.deepseek.com/chat/completions`（非 Base URL）、`requestedModel=deepseek-v4-pro`、批准来源 SHA `def9817dc35c11514335fce5ecf859878e00cdfccc259659edb7925fee9d84a7`，来源见 `q9-decision-source-20261023.json`（含 path/sha/section/lines，且与 `APPROVED_MODEL.decisionSha256` 字面一致）。`expected` 双向 pin + 常量校验；自建探针 #9（两边同填任意 URL）→ `MODEL_PROFILE_DRIFT`；Base URL 误填 route 亦拒（单测覆盖）。**原「无依据」缺陷已消除**；批准来源原件在仓外总控目录，本审者按边界未越界读取，仅核本树固定记录 |
| **M-F-C** T09 基线 17 文件集未在核验器内约束 | 中 | **关闭** | `evidence` 模式强制 `APPROVED_BASELINE` 的 manifest SHA `aaaef2c0…ac39e`、version `prd-v0.6-learning-1`、PRD SHA 与**精确 17 路径集合**（`verify.ts:566-576`）。本审者独立提取 `APPROVED_BASELINE.paths` 与 873 manifest 实际文件集比对：**集合完全相等**（missing=[] extra=[]）；缺项/额外/版本不符三个反例均有拒绝断言。**未复制第二份内容 hash**，每文件 hash 仍来自唯一 T09 manifest |
| **M-F-D** 80% 分子口径 | 低 | **关闭** | `user-study.md:25` 现已明写「80%分子保留 coreCompleted && transferCompleted 且 assistance 为 independent/product-hints」，与实现 `verify.ts:895-901` **逐字一致**；`transferIndependent` 另记（`user-study.md:25` 末句），未设额外百分比门；core=true/transfer=false → `USER_CORE_TRANSFER_CONTRADICTION`。4/5 通过、3/5 拒绝、product-hints 与独立性分记均有断言。**F16 明确保留待决**（`user-study.md:27`，本审者未代答） |
| **M-F-E** 最终检查措辞可误读 | 低 | **关闭** | `acceptance.md:22` 已由「3 项 skip」更新为「**4 项** skip」并加「本轮完整检查必须显式启用探针」「历史65/695等仅对应7d28旧候选」。本审者实测默认模式 **4 skipped**、显式模式 **0 skipped**，与文档一致 |
| **M-F-F** 回退两项无具名 check | 低 | **关闭** | `RECOVERY_CHECKS` 由 6→8，含 `rollback-retain-new-version-copy`、`rollback-refuse-incompatible-format`（`verify.ts:308-317`）；且 `ROLLBACK_<target>` 报告**各自**要求同两项（`verify.ts:1041-1053`）。自建探针 #10 确认缺任一即 `ROLLBACK_..._COVERAGE`；单测同时断言 recovery 与旧资产两处缺失 |
| **M-F-G** 同意/逐段记录工具不解析 | 低 | **关闭** | `user-study.md:29` 明确「工具只 hash `record`，不解析或验证同意、逐段观察、尝试先后、完整示范次数或录屏真实性」，并由主持人/独立验收人核原件、缺原件记待核、**不添加自证布尔**。README:31/35 同步。**未新增冒充真实性的布尔字段**（participant schema 未新增 consent 类自证位） |
| **M-F-H** 两 collector 混合缺口（三子项） | 低 | **部分关闭，余下项无法验证** | ①半成品/失败状态：Mac `write_status` pending/step/failed + 有限 exit + 首 raw 保留 + 新目录防覆盖 + 末尾 complete（`collect-macos.sh:19-71`）；Windows 步骤/失败/first raw 分离（`collect-windows.ps1:41-93`）——**已关闭**。②PE 越界：`pe-machine.ps1` 先核 DOS≥64 与 `e_lfanew`∈[64,length-6]，固定 `PE_INVALID`，finally 关闭——**已关闭**。③包与 app/engine 来源：新增 `installed-components-match-package` 强制 `{packageSha256,inventory,app,engine,method,provenance}` 且 `packageSha256` 必须等于候选包 hash（`verify.ts:783-803`），自建探针 #12 确认漂移即拒——**工具侧已关闭**；但**真实 T03 唯一包内成员与安装/解包来源仍须原件对照**，本轮无目标环境，**无法验证**（README:31 已如实声明） |
| **M-F-I** 结构/声明级边界 | 低 | **关闭** | README:35/45 明示 PE 仅核 DOS/PE 标记+偏移界限+机器字段、DMG 仅核尾部 koly，**不证明 NSIS/DMG 实质有效或签名可信**；`verify.ts` 注释亦声明「This binds the declared bytes, not the truth of the installation/extraction transcript」。metadata `valid` 不等于签名可信，已成文 |
| **M-F-J** 墙钟信任边界 | 低 | **关闭** | CLI 以 `new Date().toISOString()` 覆写 freeze.now（`verify-release.mjs:14`），**不可回填**（单测「CLI replaces forged freeze.now with the current local clock」以未来 24h 真人时间触发 `USER_STALE`）；README:45 明写操作者须核对本机日期/时区/同步来源与可知偏差、工具**不认证时钟也不伪称网络校时**。**未引入任意 `--now` 绕过开关** |
| **M-F-K** 状态文档版本双值 | 低 | **关闭** | `status.md:1-11` 新 dated 入口置顶（2026-10-23 owned 修复窗，适用候选/工作树/base 明确），并声明下方 2026-10-21 起的「当前/active/仅计划」均为历史；同 updatedAt 的不同来源 hash **保留各自快照不归并**（status.md:5 明写）；旧回执/原报告原字节未追改。独立内审 R1 已在 338 delta 复核关闭 |
| **M-F-L** 「失败原件保留」表述超出归档 | 中 | **关闭** | `status.md:11` 已分列：「首跑38失败目前只有 first-failure.json 摘录和原会话 transcript 线索，归档中**没有**独立完整首跑 raw，不能声称所有失败完整原件齐全，**也不声称永久不可获得**」；其后 48 现存日志在 `round-1/raw-logs.tar.gz` 并已只读逐成员核字节/hash。本审者独立 grep 确认归档内「38 failed」零命中、`unit-second-run.log` 记录的是修复后 38 passed。**表述与归档事实一致** |

### 7.2 Z 原 P4 六项

| 原项 | 原严重度 | 本轮判定 | 依据 |
| --- | --- | --- | --- |
| **Z-F1** 重复 schema parse | P4 | **关闭** | 现仅在 `verify.ts:509` 做一次 `expectedSchema.safeParse`，其后 `Date.parse(expected.now)` 有限性检查保留（`:516-517`）；重复 parse 已删 |
| **Z-F2** fd/限额竞态 | P4 | **关闭** | 统一 `withFile()`：open→fstat→普通/非空/限额判定→**先限额后分配与 parse**→同 fd 有界读取/hash/PE/koly→追加字节与元数据漂移复查→finally 关闭；大文件 8GiB 流式 hash；CLI 复用同一限额路径。8 项 IO 单测覆盖超限前置拒绝/增长/短读/异常关闭/非 regular/外部 symlink/叶替换/PE+koly。README:43 明示**未消除全部祖先目录 TOCTOU**、工程限额不作 Q5——**未过度宣称** |
| **Z-F3** 绑定分支 guard 缺口 | P4 | **关闭** | `verify.ts:1067-1071` 现显式 `fail('MIGRATION_DESTINATION')` 并 `continue`，不再静默跳过资产 pin；单测「reports a missing migration destination explicitly after duplicate-target rejection」同时断言 `TARGET_MATRIX` 与 `MIGRATION_DESTINATION` |
| **Z-F4** Mac 目标判断 PATH 依赖 | P4 | **关闭** | `collect-macos.sh` 全部外部命令绝对路径：最前门 `/usr/bin/uname` `/usr/bin/sw_vers`（:8），采集 `/usr/bin/sw_vers` `/usr/bin/uname` `/usr/sbin/sysctl` `/usr/bin/shasum` `/usr/bin/plutil` `/usr/bin/file` `/usr/bin/codesign` `/usr/sbin/spctl` `/usr/bin/xcrun`，`/bin/mkdir` `/bin/mv`；本审者逐行确认**无相对命令残留**。`bash -n` 通过 |
| **Z-F5** PE 越界 | P4 | **关闭** | 新增 `scripts/release/pe-machine.ps1`（独立文件）：DOS 长度<64 → `PE_DOS_BOUNDS`；MZ 签名 → `PE_MZ_REQUIRED`；`e_lfanew` 越界 → `PE_HEADER_BOUNDS`；PE 签名 → `PE_SIGNATURE_REQUIRED`；长度变化 → `PE_SIZE_CHANGED`；统一固定 `PE_INVALID`，**finally 关闭 reader 与 stream**，不外泄原异常/路径。**本机无 pwsh，PowerShell 真实运行未验证**（静态成立） |
| **Z-F6** 半成品被当证据 | P4 | **关闭** | Mac：输出目录须不存在、新目录 mkdir、pending/步骤状态、失败保留 failed + 有限 exit + 全部 raw 与半成品、成功末尾才 complete（`collect-macos.sh:19-71`）；Windows：`OUTPUT_MUST_BE_NEW`、步骤状态、失败写 failed、状态文件经 tmp+原子替换（`collect-windows.ps1:16-93`）。消费端 `collectorStatus` schema 强制 `{schemaVersion:1,status:'complete',step:'complete',exitCode:0}`（`verify.ts:46-53`），**缺/pending/failed/malformed 全拒**（单测 + 自建探针 #6），且 `collector-complete` check 与 collectorStatus 文件 hash 绑定（`WIN_COLLECTOR_BINDING`）。**marker 不等于 native/签名/同包**，README:31 明示 |

### 7.3 汇总

- **M 原 12 项**：11 项关闭（M-F-A/B/C/D/E/F/G/I/J/K/L），1 项部分关闭且余下子项**无法验证**（M-F-H③：真实 T03 唯一包内成员与安装/解包来源）。
- **Z 原 P4 六项**：6 项关闭（Z-F1～Z-F6），其中 Z-F5 的 PowerShell **运行时**未验证（静态成立）。
- **原 18 项无一被 owner 自行关闭**；本审者的「关闭」判定基于 036 现状的**实现 + 文档 + 亲跑证据**，不因 owner 的 `ownerAction` 描述而自动降级或关闭。原严重度全部保留，**M 原 NotPass 保留**。
- **本轮新增 F-1（中）**：上一轮 18 项之外，由本审者独立审查新发现，须由 owner 出新候选处理。

---

## 8. 完整工程范围终态判定

| 范围 | 判定 |
| --- | --- |
| 受审 56 requiredFiles 的**实体一致性**（字节/SHA-256） | **通过**（56/56，0 mismatch） |
| 受审 892 受控文件与 036 的**漂移** | **通过**（仅 AGENTS.md 政策差异，已声明） |
| 4 个 release 脚本 + 2 个测试 + 2 个 fixture 的**实现正确性** | **不通过**（F-1：CLI 固定错误面缺陷 + 断言降级） |
| 原 18 项原意见的**当前状态判定** | 17 项可关闭、1 项（M-F-H③）无法验证；原严重度与 M NotPass 全保留 |
| 显式固定输入联验（4 探针零 skip） | **通过**（本审者亲跑 109/109） |
| 全仓 `npm run check`（含探针） | **通过**（739 TS / 1052 Python / build / ruff，exit 0） |
| 显式 release lint/format、sources、bash-n | **通过** |
| 缺 873 对象必须失败、无 live HEAD 替代 | **通过**（实测 4 fail） |
| 归档原件完整性（48+14 成员） | **通过**（0 mismatch） |
| 父 T11 发布门（真实双平台/签名/公证/模型/真人/容量/CI/合并/远端/渠道） | **无法验证 / 未关闭** |
| 指定双审（GLM-5.3/最高） | **未完成**（本报告仅 M3.1-Flash 一方终态） |

**终态：完整工程范围 = 不通过。** 唯一硬因为 F-1（中）；其余全部工程与证据侧能力经本审者亲跑验证成立，方向 fail-closed，无虚假放行路径。F-1 须由唯一 owner 在**新候选**中修复（消除警告来源并恢复严格断言，或显式声明并同步文档），修复后按原门禁重新独立审查。

---

## 9. 交付物与保全位置

- 本报告：`.t11-review-runtime/report/review.md`
- 本方输入/元数据/原始日志/临时目录：`.t11-review-runtime/{input,metadata,raw,tmp}/`（原始日志 sha256 见 §5 表）
- 本轮 Git 终态：HEAD 仍 `036d7172ddba8502fe81e6e7ce375ce09ef7fa1c`；` M AGENTS.md`（政策差异，保持未暂存）＋未跟踪 `.t11-review-runtime/`；**无 stage/commit/push/PR/切分支，未修改任何受审文件**
- 本轮**未读取** peer 本轮 prompt/receipt/report/state/metadata，未扫描父 `.worktrees` 或总控队列，未读全局应用日志；仅读取本方 input/metadata/显式列出的上一轮历史两份完整报告/18 矩阵/triage/归档

---

## 10. 给总控的处置建议（非发布授权）

1. **F-1 须在新候选解决**：CLI stderr 非固定错误面且泄露绝对路径，owner 的处置为放宽断言。建议消除警告来源并恢复整段严格 stderr 断言；若受唯一配置约束必须保留警告，则显式声明并同步 README:15 与测试断言。修复后重跑显式专项与全仓 check，按原门禁重新独立审查。
2. **M-F-H③ 保持开口**：真实 T03 唯一包内成员与安装/解包来源须原件对照，不得以 marker、声明 hash 或同目录放行。
3. **Z-F5 保持开口**：PowerShell helper 真实运行待批准 Windows 环境，本轮仅静态。
4. **能力边界登记（低）**：`build.nodeLock/pythonLock/config` 未结构化 pin 到唯一锁与唯一配置路径，本审者实测可指向任意文件仍 consistent；建议后续纳入结构校验。
5. 本报告为 M3.1-Flash/xhigh 一方终态，**不替代 GLM-5.3/最高一方**，**不关闭任何父 T11 门**，**不授权 push/发布**；后续按原门禁由总控调度。
